"""
pantalla_admin.py — Pantalla del Módulo Administrador
Requerimientos: A-004, A-009, A-011, A-013, A-014, A-015, A-016
Jueves 18 de Junio — Fase 4, Alta Prioridad
Encargados: Mauricio S. Castillo (A-004/A-009/A-011/A-016)
            Romo Perez Axel Leonel (formulario_producto — A-005/A-008, Jueves+Viernes)
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QFrame,
    QSizePolicy, QGraphicsDropShadowEffect, QDialog
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import (
    QFont, QColor, QLinearGradient, QPainter,
    QPaintEvent, QIcon, QPen, QPixmap
)


# ══════════════════════════════════════════════════ #
#  Colores del sistema                               #
# ══════════════════════════════════════════════════ #

class _Colors:
    HEADER_START      = "#1E3A8A"
    HEADER_END        = "#0F172A"
    BG                = "#F8F9FA"  # Fondo grisáceo general
    BG_WHITE          = "#FFFFFF"
    HEADER_BTN        = "rgba(255,255,255,0.08)"
    HEADER_BTN_HOVER  = "rgba(255,255,255,0.18)"
    HEADER_BTN_ACTIVE = "rgba(96,165,250,0.25)"
    HEADER_BTN_BORDER = "#60A5FA"
    TABLA_BORDER      = "#CBD5E1"  # Borde de la tabla tipo tarjeta
    TABLA_HOVER       = "#EFF6FF"
    ROJO_ALERTA       = "#DC2626"
    AZUL_BTN          = "#1E3A8A"
    VERDE_BTN         = "#15803D"
    VERDE_BTN_HV      = "#166534"


class _GradientHeader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(72)

    def paintEvent(self, e: QPaintEvent):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        g = QLinearGradient(0, 0, self.width(), 0)
        g.setColorAt(0.0, QColor(_Colors.HEADER_START))
        g.setColorAt(1.0, QColor(_Colors.HEADER_END))
        p.fillRect(self.rect(), g)
        p.end()


# ══════════════════════════════════════════════════ #
#  Diálogo confirmación Generar reporte              #
# ══════════════════════════════════════════════════ #

class _DialogoConfirmarReporte(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generar Reporte del Día")
        self.setFixedSize(400, 200) # Ajuste sutil de tamaño
        self.setModal(True)
        self.setStyleSheet("background-color: #FFFFFF;")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 24, 20, 20)
        layout.setSpacing(10)

        # 1. Título
        lbl_titulo = QLabel("¿Generar reporte de cierre?")
        lbl_titulo.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet("color: #333333;")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_titulo)

        # 2. Texto de aviso (sin caja amarilla, todo centrado)
        texto_aviso = (
            "Esta acción exportará el PDF y reiniciará\n"
            "a cero los contadores de ventas del día.\n"
            "Esta acción no se puede deshacer"
        )
        lbl_aviso = QLabel(texto_aviso)
        lbl_aviso.setFont(QFont("Segoe UI", 11))
        lbl_aviso.setStyleSheet("color: #333333;")
        lbl_aviso.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_aviso)

        layout.addSpacing(15)

        # 3. Fila de botones centrada
        fila = QHBoxLayout()
        fila.setSpacing(35) # Separación exacta entre los botones
        fila.addStretch()

        # Botón Confirmar (Celeste, Izquierda)
        self.btn_confirmar = QPushButton("Confirmar")
        self.btn_confirmar.setFixedSize(125, 40)
        self.btn_confirmar.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        self.btn_confirmar.setStyleSheet("""
            QPushButton { 
                background-color: #52C5D8; /* Celeste de tu diseño */
                color: white; 
                border: none; 
                border-radius: 20px; /* Forma de píldora */
            }
            QPushButton:hover { background-color: #42AFC1; }
            QPushButton:pressed { background-color: #339AA8; }
        """)
        self.btn_confirmar.clicked.connect(self.accept)

        # Botón Cancelar (Rojo, Derecha)
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setFixedSize(125, 40)
        self.btn_cancelar.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        self.btn_cancelar.setDefault(True) # Mantiene el foco por seguridad (A-016)
        self.btn_cancelar.setAutoDefault(True)
        self.btn_cancelar.setStyleSheet("""
            QPushButton { 
                background-color: #DE4A4A; /* Rojo de tu diseño */
                color: white; 
                border: none; 
                border-radius: 20px; /* Forma de píldora */
            }
            QPushButton:hover { background-color: #C63D3D; }
            QPushButton:pressed { background-color: #AF3030; }
        """)
        self.btn_cancelar.clicked.connect(self.reject)
        self.btn_cancelar.setFocus()

        # Agregamos en el orden correcto (Confirmar -> Cancelar)
        fila.addWidget(self.btn_confirmar)
        fila.addWidget(self.btn_cancelar)
        fila.addStretch()

        layout.addLayout(fila)


# ══════════════════════════════════════════════════ #
#  Fila de la tabla del catálogo                     #
# ══════════════════════════════════════════════════ #

class _FilaCatalogo(QWidget):
    senal_editar   = pyqtSignal(int)
    senal_eliminar = pyqtSignal(int)

    _F_NORMAL = QFont("Segoe UI", 11) # Fuente ligeramente más grande
    _F_BOLD   = QFont("Segoe UI", 11, QFont.Weight.DemiBold)

    def __init__(self, producto: dict, parent=None):
        super().__init__(parent)
        self._id = producto["id_producto"]
        self._build(producto)

    def _build(self, p: dict):
        self.setFixedHeight(56)
        self.setStyleSheet("background: transparent;")

        row = QHBoxLayout(self)
        row.setContentsMargins(24, 0, 24, 0) # Margen alineado al encabezado
        row.setSpacing(0)

        tipo   = p.get("tipo_venta", "pieza").lower()
        unidad = "/kg" if tipo == "granel" else ""
        stock  = p.get("stock_actual", 0)
        minimo = p.get("stock_minimo", 0)

        lbl_n = QLabel(p["nombre"])
        lbl_n.setFont(self._F_NORMAL)
        lbl_n.setStyleSheet("color: #1E293B;")
        lbl_n.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        row.addWidget(lbl_n, stretch=4)

        lbl_pv = QLabel(f"${p.get('precio_venta', 0):,.2f}{unidad}")
        lbl_pv.setFont(self._F_NORMAL)
        lbl_pv.setStyleSheet("color: #1E293B;")
        lbl_pv.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(lbl_pv, stretch=2)

        lbl_pc = QLabel(f"${p.get('precio_compra', 0):,.2f}{unidad}")
        lbl_pc.setFont(self._F_NORMAL)
        lbl_pc.setStyleSheet("color: #475569;")
        lbl_pc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(lbl_pc, stretch=2)

        if stock == 0:
            txt_stock = "AGOTADO"
            color_stock = _Colors.ROJO_ALERTA
            bold = True
        else:
            txt_stock   = f"{stock:.3f} Kg" if tipo == "granel" else str(int(stock))
            color_stock = _Colors.ROJO_ALERTA if stock <= minimo else "#1E293B"
            bold = stock <= minimo

        lbl_s = QLabel(txt_stock)
        lbl_s.setFont(self._F_BOLD if bold else self._F_NORMAL)
        lbl_s.setStyleSheet(f"color: {color_stock};")
        lbl_s.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(lbl_s, stretch=2)

        btn_edit = QPushButton("✏")
        btn_edit.setFixedSize(36, 36)
        btn_edit.setFont(QFont("Segoe UI", 13))
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.setStyleSheet("""
            QPushButton { background-color: #DBEAFE; color: #1E3A8A; border: none; border-radius: 8px; }
            QPushButton:hover { background-color: #BFDBFE; }
        """)
        btn_edit.clicked.connect(lambda: self.senal_editar.emit(self._id))
        row.addWidget(btn_edit)
        row.addSpacing(8)

        btn_del = QPushButton("🗑")
        btn_del.setFixedSize(36, 36)
        btn_del.setFont(QFont("Segoe UI", 13))
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setStyleSheet("""
            QPushButton { background-color: #FEE2E2; color: #991B1B; border: none; border-radius: 8px; }
            QPushButton:hover { background-color: #FECACA; }
        """)
        btn_del.clicked.connect(lambda: self.senal_eliminar.emit(self._id))
        row.addWidget(btn_del)

    def enterEvent(self, e):
        self.setStyleSheet(f"background-color: {_Colors.TABLA_HOVER}; border-radius: 8px;")

    def leaveEvent(self, e):
        self.setStyleSheet("background: transparent;")


# ══════════════════════════════════════════════════ #
#  Pantalla Admin Principal                          #
# ══════════════════════════════════════════════════ #

class PantallaAdmin(QWidget):
    senal_ir_cajero         = pyqtSignal()
    senal_nuevo_producto    = pyqtSignal()
    senal_editar_producto   = pyqtSignal(int)
    senal_eliminar_producto = pyqtSignal(int)
    senal_generar_reporte   = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._filas: dict[int, _FilaCatalogo] = {}
        self._setup_ui()

    def _setup_ui(self):
        # Fondo general de la ventana
        self.setStyleSheet(f"background-color: {_Colors.BG};")
        
        layout_raiz = QVBoxLayout(self)
        layout_raiz.setContentsMargins(0, 0, 0, 0)
        layout_raiz.setSpacing(0)

        # 1. Header pegado al borde superior
        layout_raiz.addWidget(self._crear_header())

        # 2. Contenedor central con márgenes para dar efecto de "marco" o encuadre
        cuerpo_widget = QWidget()
        layout_cuerpo = QVBoxLayout(cuerpo_widget)
        # Márgenes que simulan el marco gris de tu documento de diseño:
        layout_cuerpo.setContentsMargins(36, 30, 36, 30) 
        layout_cuerpo.setSpacing(20) # Espacio entre la tabla y los botones inferiores

        layout_cuerpo.addWidget(self._crear_tabla_catalogo())
        layout_cuerpo.addWidget(self._crear_footer())

        layout_raiz.addWidget(cuerpo_widget)

    def _crear_header(self) -> QWidget:
        header = _GradientHeader()
        lay = QHBoxLayout(header)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(12)
        lay.addStretch()

        self.btn_cajero = self._btn_header("  Cajero")
        self.btn_admin  = self._btn_header("  Admin.", activo=True)
        self.btn_cajero.clicked.connect(self.senal_ir_cajero.emit)

        lay.addWidget(self.btn_cajero)
        lay.addWidget(self.btn_admin)
        return header

    def _btn_header(self, texto: str, activo: bool = False) -> QPushButton:
        btn = QPushButton(texto)
        btn.setFixedHeight(38)
        btn.setMinimumWidth(110)
        btn.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if activo:
            btn.setStyleSheet(f"QPushButton {{ background-color: {_Colors.HEADER_BTN_ACTIVE}; color: white; border: 1.5px solid {_Colors.HEADER_BTN_BORDER}; border-radius: 10px; padding: 0 18px; }}")
        else:
            btn.setStyleSheet(f"QPushButton {{ background-color: {_Colors.HEADER_BTN}; color: white; border: 1.5px solid transparent; border-radius: 10px; padding: 0 18px; }} QPushButton:hover {{ background-color: {_Colors.HEADER_BTN_HOVER}; }}")
        return btn

    def _crear_tabla_catalogo(self) -> QWidget:
        # Convertimos la tabla en un QFrame con borde y fondo blanco
        contenedor = QFrame()
        contenedor.setObjectName("tabla_container")
        contenedor.setStyleSheet(f"""
            #tabla_container {{
                background-color: {_Colors.BG_WHITE};
                border: 1.5px solid {_Colors.TABLA_BORDER};
                border-radius: 12px;
            }}
        """)
        contenedor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        lay = QVBoxLayout(contenedor)
        lay.setContentsMargins(0, 0, 0, 0) # Sin márgenes para que la línea separadora toque los bordes
        lay.setSpacing(0)

        lay.addWidget(self._crear_encabezados_tabla())
        lay.addWidget(self._separador())

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet("background: transparent;")

        self._contenedor_filas = QWidget()
        self._contenedor_filas.setStyleSheet("background: transparent;")
        self._lay_filas = QVBoxLayout(self._contenedor_filas)
        self._lay_filas.setContentsMargins(0, 4, 0, 10)
        self._lay_filas.setSpacing(2)
        self._lay_filas.addStretch()

        self._scroll.setWidget(self._contenedor_filas)
        lay.addWidget(self._scroll)
        return contenedor

    def _crear_encabezados_tabla(self) -> QWidget:
        w = QWidget()
        w.setFixedHeight(48)
        w.setStyleSheet("background: transparent;")
        row = QHBoxLayout(w)
        row.setContentsMargins(24, 0, 24, 0) # Márgenes interiores del texto
        row.setSpacing(0)
        
        # Fuente más grande simulando el documento de diseño
        font = QFont("Segoe UI", 12, QFont.Weight.DemiBold)

        for texto, stretch, alinear in [
            ("Nombre",          4, Qt.AlignmentFlag.AlignLeft),
            ("Precio de venta", 2, Qt.AlignmentFlag.AlignCenter),
            ("Precio de compra",2, Qt.AlignmentFlag.AlignCenter),
            ("Stock actual",    2, Qt.AlignmentFlag.AlignCenter),
            ("",                0, Qt.AlignmentFlag.AlignCenter),
        ]:
            lbl = QLabel(texto)
            lbl.setFont(font)
            lbl.setStyleSheet("color: #475569;") # Gris oscuro
            if texto == "":
                lbl.setFixedWidth(84)
                row.addWidget(lbl)
            else:
                lbl.setAlignment(alinear | Qt.AlignmentFlag.AlignVCenter)
                row.addWidget(lbl, stretch=stretch)
        return w

    def _separador(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {_Colors.TABLA_BORDER}; border: none;")
        return sep

    def _crear_footer(self) -> QWidget:
        footer = QWidget()
        # Fondo transparente para que los botones floten sobre el fondo general gris
        footer.setStyleSheet("background: transparent;")

        lay = QHBoxLayout(footer)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        self.btn_reporte = QPushButton("  Generar reporte del día")
        self.btn_reporte.setFixedSize(220, 46)
        self.btn_reporte.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        self.btn_reporte.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reporte.setStyleSheet(f"""
            QPushButton {{ background-color: #0F4C81; color: white; border: none; border-radius: 14px; padding: 0 16px; }}
            QPushButton:hover {{ background-color: #0D3D6E; }}
        """)
        sombra_r = QGraphicsDropShadowEffect()
        sombra_r.setBlurRadius(16)
        sombra_r.setOffset(0, 3)
        sombra_r.setColor(QColor(15, 76, 129, 55))
        self.btn_reporte.setGraphicsEffect(sombra_r)
        self.btn_reporte.clicked.connect(self._solicitar_generar_reporte)

        self.btn_nuevo = QPushButton("  + Nuevo producto")
        self.btn_nuevo.setFixedSize(190, 46)
        self.btn_nuevo.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        self.btn_nuevo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_nuevo.setStyleSheet(f"""
            QPushButton {{ background-color: {_Colors.VERDE_BTN}; color: white; border: none; border-radius: 14px; padding: 0 16px; }}
            QPushButton:hover {{ background-color: {_Colors.VERDE_BTN_HV}; }}
        """)
        sombra_n = QGraphicsDropShadowEffect()
        sombra_n.setBlurRadius(16)
        sombra_n.setOffset(0, 3)
        sombra_n.setColor(QColor(21, 128, 61, 55))
        self.btn_nuevo.setGraphicsEffect(sombra_n)
        self.btn_nuevo.clicked.connect(self.senal_nuevo_producto.emit)

        lay.addWidget(self.btn_reporte, alignment=Qt.AlignmentFlag.AlignLeft)
        lay.addStretch()
        lay.addWidget(self.btn_nuevo, alignment=Qt.AlignmentFlag.AlignRight)
        return footer

    # ────────────────────────────────────────────────────────────────── #
    #  API y Lógica Interna (Sin Cambios)                                #
    # ────────────────────────────────────────────────────────────────── #

    def cargar_catalogo(self, productos: list[dict]):
        for fila in self._filas.values():
            self._lay_filas.removeWidget(fila)
            fila.deleteLater()
        self._filas.clear()
        for p in productos:
            self._insertar_fila(p)

    def actualizar_fila(self, producto: dict):
        id_p = producto["id_producto"]
        if id_p in self._filas:
            fila_vieja = self._filas.pop(id_p)
            idx = self._lay_filas.indexOf(fila_vieja)
            self._lay_filas.removeWidget(fila_vieja)
            fila_vieja.deleteLater()
            fila_nueva = self._crear_fila(producto)
            self._lay_filas.insertWidget(idx, fila_nueva)
            self._filas[id_p] = fila_nueva
        else:
            self._insertar_fila(producto)

    def eliminar_fila(self, id_producto: int):
        if id_producto not in self._filas:
            return
        fila = self._filas.pop(id_producto)
        self._lay_filas.removeWidget(fila)
        fila.deleteLater()

    def _solicitar_generar_reporte(self):
        dlg = _DialogoConfirmarReporte(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.senal_generar_reporte.emit()

    def _solicitar_eliminar(self, id_producto: int):
        self.senal_eliminar_producto.emit(id_producto)

    def _insertar_fila(self, producto: dict):
        fila = self._crear_fila(producto)
        idx = self._lay_filas.count() - 1 
        self._lay_filas.insertWidget(idx, fila)
        self._filas[producto["id_producto"]] = fila

    def _crear_fila(self, producto: dict) -> _FilaCatalogo:
        fila = _FilaCatalogo(producto)
        fila.senal_editar.connect(self.senal_editar_producto.emit)
        fila.senal_eliminar.connect(self._solicitar_eliminar)
        return fila
    
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtGui import QFont

    app = QApplication(sys.argv)

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    ventana = PantallaAdmin()
    ventana.setWindowTitle("Punto de Venta — Admin")
    ventana.resize(1200, 800)
    
    productos_prueba = [
        {"id_producto": 1, "nombre": "Coca Cola 600ml", "precio_venta": 18.00, "precio_compra": 12.00, "stock_actual": 45, "stock_minimo": 10, "tipo_venta": "pieza"},
        {"id_producto": 2, "nombre": "Frijol Peruano", "precio_venta": 42.50, "precio_compra": 28.00, "stock_actual": 8.5, "stock_minimo": 10, "tipo_venta": "granel"}, # Stock bajo (Saldrá en rojo)
        {"id_producto": 3, "nombre": "Galletas Emperador", "precio_venta": 22.00, "precio_compra": 16.50, "stock_actual": 0, "stock_minimo": 5, "tipo_venta": "pieza"}   # Agotado
    ]
    ventana.cargar_catalogo(productos_prueba)

    ventana.show()

    sys.exit(app.exec())