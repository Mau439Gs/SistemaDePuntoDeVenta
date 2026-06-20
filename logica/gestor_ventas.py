# logica/gestor_ventas.py
from datetime import datetime
from datos.base_datos import BaseDatos
from logica.gestor_carrito import GestorCarrito


class GestorVentas:
    """Gestiona la lógica de confirmación de ventas, cálculo de cambio
    y verificación de alertas de stock.

    Referencia SRS:
    - C-006: Calcular cambio, no confirmar si monto < total.
    - C-007: Cancelar venta en cualquier momento.
    - C-008: Preguntar si requiere ticket tras confirmar cobro.
    - C-009: Cancelar venta sin afectar stock ni contadores.
    - C-010: Verificar alertas de stock al finalizar cada venta.
    - G-001: Descontar stock exacto, nunca debajo de cero.
    """

    def __init__(self, db: BaseDatos, carrito: GestorCarrito):
        self.db = db
        self.carrito = carrito

    # ──────────────────────────────────────────────
    #  Cálculo de cambio (C-006)
    # ──────────────────────────────────────────────

    def calcular_cambio(self, total: float, monto_recibido: float) -> float:
        """Calcula el cambio a devolver al cliente.

        Args:
            total: Monto total a pagar.
            monto_recibido: Cantidad de efectivo entregada por el cliente.

        Returns:
            El cambio a devolver (monto_recibido - total).

        Raises:
            ValueError: Si el monto recibido es menor al total a pagar.
        """
        if monto_recibido < total:
            raise ValueError("El monto recibido no puede ser menor al total a pagar.")
        return round(monto_recibido - total, 2)

    # ──────────────────────────────────────────────
    #  Validación de stock (G-001)
    # ──────────────────────────────────────────────

    def validar_stock(self) -> list:
        """Verifica que todos los productos del carrito tengan stock suficiente
        consultando la base de datos en tiempo real.

        Referencia SRS G-001:
        'El stock nunca debe descender por debajo de cero; si rebasa el
        stock disponible, el sistema debe rechazar la operación.'

        Returns:
            Lista de mensajes de error. Si está vacía, todo es válido.
        """
        errores = []
        self.db._asegurar_conexion()
        for item in self.carrito.obtener_items():
            producto = item.producto
            id_producto = producto['id_producto']
            res = self.db.consultar_uno(
                "SELECT stock_actual, nombre FROM PRODUCTOS WHERE id_producto = ?;",
                (id_producto,)
            )
            if res:
                stock_actual = res['stock_actual']
                if item.cantidad > stock_actual:
                    errores.append(
                        f"El stock en tienda actual de {res['nombre']} "
                        f"es: {stock_actual}"
                    )
        return errores

    # ──────────────────────────────────────────────
    #  Confirmar venta (Tarea 2.8)
    # ──────────────────────────────────────────────

    def confirmar_venta(self, monto_recibido: float) -> dict:
        """Confirma la venta en curso dentro de una transacción ACID.

        Ejecuta en una sola transacción atómica:
        1. INSERT en VENTAS (encabezado).
        2. INSERT en DETALLE_VENTA por cada ítem (datos congelados).
        3. UPDATE en PRODUCTOS para descontar el stock vendido.

        Si cualquier paso falla, se hace rollback completo y no se
        modifica nada en la base de datos.

        Args:
            monto_recibido: Efectivo entregado por el cliente.

        Returns:
            Diccionario con los datos de la venta confirmada:
            {
                'id_venta': int,
                'fecha_hora': str,
                'items': lista de detalles por producto,
                'total': float,
                'costo_total': float,
                'monto_recibido': float,
                'cambio': float,
                'alertas_stock': lista de alertas
            }

        Raises:
            ValueError: Si el carrito está vacío, el monto es insuficiente
                        o el stock es insuficiente.
        """
        # ── Validaciones previas ──
        items = self.carrito.obtener_items()
        if not items:
            raise ValueError("El carrito está vacío.")

        total = self.carrito.calcular_total()
        cambio = self.calcular_cambio(total, monto_recibido)

        errores_stock = self.validar_stock()
        if errores_stock:
            raise ValueError("\n".join(errores_stock))

        # ── Calcular costo total de la mercancía vendida ──
        costo_total = sum(
            item.cantidad * item.producto['precio_compra']
            for item in items
        )

        # ── Transacción ACID ──
        self.db.conectar()
        try:
            fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 1. INSERT encabezado de la venta
            self.db.cursor.execute("""
                INSERT INTO VENTAS (fecha_hora, total, costo_total)
                VALUES (?, ?, ?);
            """, (fecha_hora, total, costo_total))
            id_venta = self.db.cursor.lastrowid

            # 2. INSERT detalle por cada ítem (datos congelados)
            detalles = []
            for item in items:
                p = item.producto
                subtotal = round(item.cantidad * p['precio_venta'], 2)
                costo = round(item.cantidad * p['precio_compra'], 2)

                self.db.cursor.execute("""
                    INSERT INTO DETALLE_VENTA 
                    (id_venta, id_producto, nombre_producto, tipo_venta,
                     cantidad, precio_unitario_venta, precio_unitario_compra,
                     subtotal, costo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    id_venta, p['id_producto'], p['nombre'], p['tipo_venta'],
                    item.cantidad, p['precio_venta'], p['precio_compra'],
                    subtotal, costo
                ))

                detalles.append({
                    'nombre': p['nombre'],
                    'tipo_venta': p['tipo_venta'],
                    'cantidad': item.cantidad,
                    'precio_unitario': p['precio_venta'],
                    'subtotal': subtotal
                })

                # 3. UPDATE descontar stock del producto
                self.db.cursor.execute("""
                    UPDATE PRODUCTOS
                    SET stock_actual = stock_actual - ?
                    WHERE id_producto = ?;
                """, (item.cantidad, p['id_producto']))

            # Confirmar toda la transacción
            self.db.conexion.commit()

        except Exception as e:
            self.db.conexion.rollback()
            raise RuntimeError(f"Error al confirmar la venta: {e}")

        # ── Verificar alertas de stock después del commit (C-010) ──
        alertas = self.verificar_alertas_stock(items)

        # ── Vaciar carrito para la siguiente venta ──
        self.carrito.vaciar_carrito()

        return {
            'id_venta': id_venta,
            'fecha_hora': fecha_hora,
            'items': detalles,
            'total': total,
            'costo_total': costo_total,
            'monto_recibido': monto_recibido,
            'cambio': cambio,
            'alertas_stock': alertas
        }

    # ──────────────────────────────────────────────
    #  Verificar alertas de stock (C-010, C-011)
    # ──────────────────────────────────────────────

    def verificar_alertas_stock(self, items_vendidos: list) -> list:
        """Verifica si algún producto vendido alcanzó o cayó por debajo
        de su umbral mínimo de stock.

        Referencia SRS:
        - C-010: Verificar stock tras cada venta.
        - C-011: Si stock < mínimo, mostrar aviso con nombre y stock.
                  Si stock = 0, indicar 'Agotado' en rojo.

        Args:
            items_vendidos: Lista de ItemCarrito que se acaban de vender.

        Returns:
            Lista de diccionarios con las alertas:
            [{'nombre': str, 'stock_actual': float, 'agotado': bool}]
        """
        alertas = []
        for item in items_vendidos:
            id_producto = item.producto['id_producto']

            # Consultar stock actualizado directamente de la BD
            resultado = self.db.consultar_uno(
                "SELECT nombre, stock_actual, stock_minimo FROM PRODUCTOS WHERE id_producto = ?;",
                (id_producto,)
            )

            if resultado:
                stock_actual = resultado['stock_actual']
                stock_minimo = resultado['stock_minimo']

                if stock_actual <= 0:
                    alertas.append({
                        'nombre': resultado['nombre'],
                        'stock_actual': stock_actual,
                        'agotado': True
                    })
                elif stock_actual <= stock_minimo:
                    alertas.append({
                        'nombre': resultado['nombre'],
                        'stock_actual': stock_actual,
                        'agotado': False
                    })

        return alertas

    # ──────────────────────────────────────────────
    #  Cancelar venta (C-007, C-009)
    # ──────────────────────────────────────────────

    def cancelar_venta(self):
        """Cancela la venta en curso vaciando el carrito.

        Referencia SRS:
        - C-007: Permitir cancelar en cualquier momento.
        - C-009: No afectar stock ni contadores de ventas del día.
        """
        self.carrito.vaciar_carrito()
