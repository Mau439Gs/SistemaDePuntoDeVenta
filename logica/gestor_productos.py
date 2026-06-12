# logica/gestor_productos.py
import unicodedata
from datos.base_datos import BaseDatos


class GestorProductos:
    def __init__(self, db: BaseDatos):
        self.db = db

    # ──────────────────────────────────────────────
    #  Normalización de texto (G-002)
    # ──────────────────────────────────────────────

    def normalizar_texto(self, texto: str) -> str:
        """Normaliza texto a mayúsculas, sin tildes, sin caracteres
        especiales y sustituyendo 'ñ/Ñ' por 'N'.

        Referencia SRS G-002:
        'Todo texto ingresado en campos de nombre de producto o búsqueda
        debe normalizarse automáticamente a mayúsculas, eliminando tildes,
        caracteres especiales y sustituyendo la ñ por N.'
        """
        # Sustituir ñ/Ñ por N antes de eliminar tildes
        texto = texto.replace("ñ", "N").replace("Ñ", "N")
        # Descomponer caracteres acentuados (é → e + ´)
        texto = unicodedata.normalize("NFD", texto)
        # Eliminar las marcas de acento (categoría Unicode 'Mn')
        texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
        # Convertir a mayúsculas
        texto = texto.upper()
        return texto

    # ──────────────────────────────────────────────
    #  CRUD de productos
    # ──────────────────────────────────────────────

    def alta_producto(self, nombre, tipo_venta, pc, pv, s_min, s_act):
        nombre = self.normalizar_texto(nombre)
        id_nuevo = self.db.insertar_producto(nombre, tipo_venta, pc, pv, s_min, s_act)
        return id_nuevo > 0

    def editar_producto(self, id_producto, nombre, tipo_venta, pc, pv, s_min, s_act):
        nombre = self.normalizar_texto(nombre)
        return self.db.actualizar_producto(id_producto, nombre, tipo_venta, pc, pv, s_min, s_act)

    def eliminar_producto(self, id_producto):
        return self.db.eliminar_producto(id_producto)

    # ──────────────────────────────────────────────
    #  Consultas
    # ──────────────────────────────────────────────

    def obtener_catalogo(self) -> list:
        return self.db.obtener_catalogo()

    def buscar_producto(self, termino: str) -> list:
        termino_limpio = self.normalizar_texto(termino)
        return self.db.buscar_productos(termino_limpio)

    # ──────────────────────────────────────────────
    #  Cálculos de precio (A-010)
    # ──────────────────────────────────────────────

    def calcular_porcentaje_ganancia(self, precio_compra: float, precio_venta: float) -> float:
        """Calcula el porcentaje de ganancia a partir de los precios."""
        if precio_compra <= 0:
            return 0.0
        return ((precio_venta - precio_compra) / precio_compra) * 100

    def calcular_precio_venta(self, precio_compra: float, porcentaje: float) -> float:
        """Calcula el precio de venta a partir del precio de compra y el porcentaje."""
        return precio_compra * (1 + porcentaje / 100)
