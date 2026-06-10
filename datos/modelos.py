from dataclasses import dataclass
from typing import Optional

@dataclass
class Producto:
    id: Optional[int]
    nombre: str
    tipo_venta: str  # 'pieza' o 'granel'
    precio_compra: float
    precio_venta: float
    stock_minimo: float
    stock_actual: float

@dataclass
class Venta:
    id: Optional[int]
    fecha_hora: str
    total: float
    monto_recibido: float
    cambio: float

@dataclass
class DetalleVenta:
    id: Optional[int]
    venta_id: int
    producto_id: int
    cantidad: float
    precio_unitario: float
    subtotal: float
