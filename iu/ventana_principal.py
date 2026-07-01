# iu/ventana_principal.py
from PyQt6.QtWidgets import QMainWindow, QStackedWidget

from iu.cajero.pantalla_cajero import PantallaCajero
from iu.admin.pantalla_admin import PantallaAdmin


class VentanaPrincipal(QMainWindow):
    """Ventana principal minimalista que gestiona la navegación entre la pantalla
    de cajero (principal) y la pantalla de administrador usando QStackedWidget."""
    
    def __init__(self, gestor_productos, gestor_carrito, gestor_ventas, gestor_autenticacion, gestor_reportes, parent=None):
        super().__init__(parent)
        self.gp = gestor_productos
        self.gc = gestor_carrito
        self.gv = gestor_ventas
        self.ga = gestor_autenticacion
        self.gr = gestor_reportes
        
        self.setWindowTitle("Sistema de Punto de Venta")
        self.resize(1280, 850)
        
        # Stacked Widget para intercambiar vistas
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Inicializar pantallas del sistema con sus gestores correspondientes
        self.pantalla_cajero = PantallaCajero(
            gestor_productos=self.gp,
            gestor_carrito=self.gc,
            gestor_ventas=self.gv,
            gestor_autenticacion=self.ga
        )
        
        self.pantalla_admin = PantallaAdmin(
            gestor_productos=self.gp,
            gestor_reportes=self.gr
        )
        
        # Agregar al stacked widget
        self.stacked_widget.addWidget(self.pantalla_cajero)
        self.stacked_widget.addWidget(self.pantalla_admin)
        
        # Vista inicial: Pantalla de Cajero (Requerimiento de inicio)
        self.stacked_widget.setCurrentWidget(self.pantalla_cajero)
        
        self._conectar_senales()
        
    def _conectar_senales(self):
        # Única responsabilidad: Enrutar navegación mediante señales
        self.pantalla_cajero.senal_ir_admin.connect(self._mostrar_admin)
        self.pantalla_admin.senal_ir_cajero.connect(self._mostrar_cajero)

    def _mostrar_admin(self):
        # Cargar catálogo de productos en la administración al cambiar de pantalla
        productos = self.gp.obtener_catalogo()
        self.pantalla_admin.cargar_catalogo(productos)
        self.stacked_widget.setCurrentWidget(self.pantalla_admin)

    def _mostrar_cajero(self):
        items_a_eliminar = []
        for item in self.gc.items:
            producto_db = self.gp.db.consultar_uno(
                "SELECT * FROM PRODUCTOS WHERE id_producto = ?;", 
                (item.producto['id_producto'],)
            )
            if producto_db:
                item.producto = dict(producto_db)
                if item.producto.get('tipo_venta') == 'pieza':
                    item.cantidad = float(int(item.cantidad))
                item.subtotal = item.calcular_subtotal()
            else:
                items_a_eliminar.append(item.producto['id_producto'])
                
        for id_prod in items_a_eliminar:
            self.gc.eliminar_item(id_prod)

        self.pantalla_cajero._actualizar_tabla()
        self.stacked_widget.setCurrentWidget(self.pantalla_cajero)
        self.pantalla_cajero.barra_busqueda.setFocus()
