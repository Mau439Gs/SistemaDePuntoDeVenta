class ItemCarrito:

    def __init__(self, producto_dict: dict, cantidad: float):
        self.producto = producto_dict
        self.cantidad = cantidad
        self.subtotal = self.calcular_subtotal()

    def calcular_subtotal(self) -> float:
        return self.cantidad * self.producto['precio_venta']

    def actualizar_cantidad(self, nueva_cantidad: float):
        self.cantidad = nueva_cantidad
        self.subtotal = self.calcular_subtotal()


class GestorCarrito:
    def __init__(self):

        self.items = [] 

    def agregar_producto(self, producto_dict: dict, cantidad: float = 1.0) -> bool:
        """Agrega un producto o incrementa su cantidad si ya existe en la lista."""

        for item in self.items:
            if item.producto['id_producto'] == producto_dict['id_producto']:
                item.actualizar_cantidad(item.cantidad + cantidad)
                return True
        
        nuevo_item = ItemCarrito(producto_dict, cantidad)
        self.items.append(nuevo_item)
        return True

    def calcular_total(self) -> float:
        """Suma dinámicamente los subtotales vigentes de la RAM."""
        return sum(item.subtotal for item in self.items)

    def vaciar_carrito(self):
        """Limpia por completo la lista temporal para la siguiente transacción."""
        self.items.clear()

    def obtener_items(self) -> list:
        """Devuelve la lista actual para que PyQt6 pueda pintar las celdas."""
        return self.items