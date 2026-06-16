# logica/gestor_productos.py
import unicodedata
from datos.base_datos import BaseDatos

class GestorProductos:
    def __init__(self, db: BaseDatos):
        self.db = db

    def alta_producto(self, nombre, tipo_venta, pc, pv, s_min, s_act):

        id_nuevo = self.db.insertar_producto(nombre, tipo_venta, pc, pv, s_min, s_act)
        return id_nuevo > 0

    def editar_producto(self, id_producto, nombre, tipo_venta, pc, pv, s_min, s_act):

        return self.db.actualizar_producto(id_producto, nombre, tipo_venta, pc, pv, s_min, s_act)

    def eliminar_producto(self, id_producto):

        return self.db.eliminar_producto(id_producto)

    def obtener_catalogo(self) -> list:
        
        return self.db.obtener_catalogo()

    def buscar_producto(self, termino: str) -> list:
        return self.db.buscar_productos(termino)
