from dataclasses import dataclass
from typing import Optional


@dataclass
class Producto:
    """Representa un artículo del catálogo de la tienda."""
    id_producto: Optional[int]
    nombre: str
    tipo_venta: str  # 'pieza' o 'granel'
    precio_compra: float
    precio_venta: float
    stock_minimo: float
    stock_actual: float


@dataclass
class Venta:
    """Encabezado de una transacción confirmada en el módulo de cajero.
    Los registros se eliminan tras generar el reporte diario de cierre."""
    id_venta: Optional[int]
    fecha_hora: str
    total: float
    costo_total: float


@dataclass
class DetalleVenta:
    """Desglose de cada ítem incluido en una venta.
    Congela los datos del producto al momento de la venta para
    garantizar que modificaciones futuras no alteren el historial."""
    id_detalle: Optional[int]
    id_venta: int
    id_producto: int
    nombre_producto: str
    tipo_venta: str  # 'pieza' o 'granel'
    cantidad: float
    precio_unitario_venta: float
    precio_unitario_compra: float
    subtotal: float  # cantidad * precio_unitario_venta
    costo: float     # cantidad * precio_unitario_compra


@dataclass
class ItemCarrito:
    """Elemento temporal del carrito de compra durante una venta en curso."""
    producto: Producto
    cantidad: float

    @property
    def subtotal(self) -> float:
        return self.cantidad * self.producto.precio_venta

    @property
    def costo(self) -> float:
        return self.cantidad * self.producto.precio_compra
