# iu/cajero/pantalla_cajero.py
"""
Módulo de Cajero — Interfaz principal del punto de venta.
Diseño neomórfico moderno con PyQt6.

Referencia SRS:
- C-001: Búsqueda por nombre parcial o ID.
- C-004: Carrito con nombre, cantidad (−)(+), precio, subtotal.
- C-007: Cancelar venta en cualquier momento.
- C-016: Barra de búsqueda arriba, carrito abajo, botones en extremos.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import (
    QFont, QColor, QLinearGradient, QPainter,
    QPaintEvent, QIcon, QPen, QPixmap
)


# ══════════════════════════════════════════════════
#  Colores del sistema de diseño
# ══════════════════════════════════════════════════

class Colors:
    # Header gradient
    HEADER_START = "#1E3A8A"
    HEADER_END = "#0F172A"

    # Fondo general
    BG = "#F8F9FA"
    BG_WHITE = "#FFFFFF"

    # Botones
    RED_CANCEL = "#991B1B"
    RED_CANCEL_HOVER = "#7F1D1D"
    BLUE_ADVANCE = "#DBEAFE"
    BLUE_ADVANCE_HOVER = "#BFDBFE"
    BLUE_ADVANCE_TEXT = "#1E293B"

    # Barra de búsqueda
    SEARCH_BG = "rgba(255, 255, 255, 0.12)"
    SEARCH_BORDER = "rgba(255, 255, 255, 0.20)"
    SEARCH_TEXT = "#FFFFFF"
    SEARCH_FOCUS_BORDER = "rgba(255, 255, 255, 0.45)"

    # Header botones
    HEADER_BTN = "rgba(255, 255, 255, 0.08)"
    HEADER_BTN_HOVER = "rgba(255, 255, 255, 0.18)"
    HEADER_BTN_ACTIVE = "rgba(96, 165, 250, 0.25)"
    HEADER_BTN_ACTIVE_BORDER = "#60A5FA"


# ══════════════════════════════════════════════════
#  Widget Header con gradiente pintado
# ══════════════════════════════════════════════════

class GradientHeader(QWidget):
    """Encabezado con fondo de gradiente lineal azul oscuro."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(72)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0.0, QColor(Colors.HEADER_START))
        gradient.setColorAt(1.0, QColor(Colors.HEADER_END))
        painter.fillRect(self.rect(), gradient)
        painter.end()


# ══════════════════════════════════════════════════
#  Generador de íconos SVG inline
# ══════════════════════════════════════════════════

def create_icon_from_svg(svg_content: str, size: int = 20) -> QIcon:
    """Crea un QIcon a partir de contenido SVG en string."""
    from PyQt6.QtSvg import QSvgRenderer
    from PyQt6.QtCore import QByteArray
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor("transparent"))
    renderer = QSvgRenderer(QByteArray(svg_content.encode()))
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


# SVGs para íconos
SVG_SEARCH = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
    stroke="rgba(255,255,255,0.55)" stroke-width="2.5" stroke-linecap="round">
    <circle cx="10.5" cy="10.5" r="6.5"/><line x1="15.5" y1="15.5" x2="21" y2="21"/>
</svg>'''

SVG_CART = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
    stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/>
    <line x1="3" y1="6" x2="21" y2="6"/>
    <path d="M16 10a4 4 0 01-8 0"/>
</svg>'''

SVG_SHIELD = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
    stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
</svg>'''

SVG_X = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
    stroke="white" stroke-width="2.5" stroke-linecap="round">
    <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
</svg>'''

SVG_ARROW_RIGHT = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
    stroke="#1E293B" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
    <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
</svg>'''


# ══════════════════════════════════════════════════
#  Pantalla Principal del Cajero
# ══════════════════════════════════════════════════

class PantallaCajero(QWidget):
    """Interfaz principal del módulo de cajero.

    Señales:
        senal_avanzar_cobro: Emitida al presionar 'Avanzar'.
        senal_cancelar_venta: Emitida al presionar 'Cancelar Venta'.
        senal_ir_admin: Emitida al presionar el botón 'Admin'.
        senal_busqueda: Emitida con el texto cada vez que cambia la barra.
    """
    senal_avanzar_cobro = pyqtSignal()
    senal_cancelar_venta = pyqtSignal()
    senal_ir_admin = pyqtSignal()
    senal_busqueda = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        # ── Fondo general limpio ──
        self.setStyleSheet(f"background-color: {Colors.BG};")

        # Layout principal sin márgenes
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # ── 1. HEADER ──
        layout_principal.addWidget(self._crear_header())

        # ── 2. CUERPO CENTRAL (vacío, se llenará con el carrito) ──
        self.contenedor_central = QWidget()
        self.contenedor_central.setStyleSheet(
            f"background-color: {Colors.BG_WHITE};"
        )
        self.contenedor_central.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        # Layout interno del cuerpo para agregar contenido después
        self.layout_central = QVBoxLayout(self.contenedor_central)
        self.layout_central.setContentsMargins(24, 16, 24, 16)
        self.layout_central.setSpacing(0)
        self.layout_central.addStretch()

        layout_principal.addWidget(self.contenedor_central)

        # ── 3. BOTONES INFERIORES ──
        layout_principal.addWidget(self._crear_barra_inferior())

    # ──────────────────────────────────────────────
    #  Construcción del Header
    # ──────────────────────────────────────────────

    def _crear_header(self) -> QWidget:
        header = GradientHeader()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(12)

        # ── Barra de búsqueda ──
        self.barra_busqueda = QLineEdit()
        self.barra_busqueda.setFixedHeight(40)
        self.barra_busqueda.setMinimumWidth(420)
        self.barra_busqueda.setMaximumWidth(600)
        self.barra_busqueda.setFont(QFont("Segoe UI", 13))
        self.barra_busqueda.textChanged.connect(self.senal_busqueda.emit)

        # Ícono de lupa a la derecha
        try:
            icono_busqueda = create_icon_from_svg(SVG_SEARCH, 20)
            accion_busqueda = self.barra_busqueda.addAction(
                icono_busqueda, QLineEdit.ActionPosition.TrailingPosition
            )
        except Exception:
            pass  # Si falla SVG, la barra sigue funcional

        self.barra_busqueda.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.SEARCH_BG};
                border: 1.5px solid {Colors.SEARCH_BORDER};
                border-radius: 12px;
                padding: 0 40px 0 16px;
                color: {Colors.SEARCH_TEXT};
                font-size: 13px;
                selection-background-color: rgba(96, 165, 250, 0.35);
            }}
            QLineEdit:focus {{
                border: 1.5px solid {Colors.SEARCH_FOCUS_BORDER};
                background-color: rgba(255, 255, 255, 0.16);
            }}
        """)

        layout.addWidget(self.barra_busqueda)
        layout.addStretch()

        # ── Botones de navegación ──
        self.btn_cajero = self._crear_boton_header("  Cajero", SVG_CART, activo=True)
        self.btn_admin = self._crear_boton_header("  Admin.", SVG_SHIELD)
        self.btn_admin.clicked.connect(self.senal_ir_admin.emit)

        layout.addWidget(self.btn_cajero)
        layout.addWidget(self.btn_admin)

        return header

    def _crear_boton_header(self, texto: str, svg: str, activo: bool = False) -> QPushButton:
        btn = QPushButton(texto)
        btn.setFixedHeight(38)
        btn.setMinimumWidth(110)
        btn.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

        try:
            btn.setIcon(create_icon_from_svg(svg, 18))
            btn.setIconSize(QSize(18, 18))
        except Exception:
            pass

        if activo:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.HEADER_BTN_ACTIVE};
                    color: white;
                    border: 1.5px solid {Colors.HEADER_BTN_ACTIVE_BORDER};
                    border-radius: 10px;
                    padding: 0 18px;
                }}
                QPushButton:hover {{
                    background-color: rgba(96, 165, 250, 0.35);
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.HEADER_BTN};
                    color: white;
                    border: 1.5px solid transparent;
                    border-radius: 10px;
                    padding: 0 18px;
                }}
                QPushButton:hover {{
                    background-color: {Colors.HEADER_BTN_HOVER};
                    border: 1.5px solid rgba(255,255,255,0.15);
                }}
            """)

        return btn

    # ──────────────────────────────────────────────
    #  Construcción de barra inferior
    # ──────────────────────────────────────────────

    def _crear_barra_inferior(self) -> QWidget:
        contenedor = QWidget()
        contenedor.setFixedHeight(80)
        contenedor.setStyleSheet(f"background-color: {Colors.BG_WHITE};")

        layout = QHBoxLayout(contenedor)
        layout.setContentsMargins(28, 0, 28, 20)

        # ── Botón Cancelar Venta (Izquierda) ──
        self.btn_cancelar = QPushButton("  Cancelar Venta")
        self.btn_cancelar.setFixedSize(200, 48)
        self.btn_cancelar.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        self.btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancelar.clicked.connect(self.senal_cancelar_venta.emit)

        try:
            self.btn_cancelar.setIcon(create_icon_from_svg(SVG_X, 18))
            self.btn_cancelar.setIconSize(QSize(18, 18))
        except Exception:
            pass

        self.btn_cancelar.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.RED_CANCEL};
                color: white;
                border: none;
                border-radius: 14px;
                padding: 0 20px;
                letter-spacing: 0.3px;
            }}
            QPushButton:hover {{
                background-color: {Colors.RED_CANCEL_HOVER};
            }}
            QPushButton:pressed {{
                background-color: #6B1414;
            }}
        """)

        # Sombra sutil para el botón cancelar
        sombra_cancelar = QGraphicsDropShadowEffect()
        sombra_cancelar.setBlurRadius(18)
        sombra_cancelar.setOffset(0, 4)
        sombra_cancelar.setColor(QColor(153, 27, 27, 60))
        self.btn_cancelar.setGraphicsEffect(sombra_cancelar)

        # ── Botón Avanzar (Derecha) ──
        self.btn_avanzar = QPushButton("  Avanzar")
        self.btn_avanzar.setFixedSize(180, 48)
        self.btn_avanzar.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        self.btn_avanzar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_avanzar.clicked.connect(self.senal_avanzar_cobro.emit)

        try:
            self.btn_avanzar.setIcon(create_icon_from_svg(SVG_ARROW_RIGHT, 18))
            self.btn_avanzar.setIconSize(QSize(18, 18))
            self.btn_avanzar.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        except Exception:
            pass

        self.btn_avanzar.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.BLUE_ADVANCE};
                color: {Colors.BLUE_ADVANCE_TEXT};
                border: none;
                border-radius: 14px;
                padding: 0 20px;
                letter-spacing: 0.3px;
            }}
            QPushButton:hover {{
                background-color: {Colors.BLUE_ADVANCE_HOVER};
            }}
            QPushButton:pressed {{
                background-color: #93C5FD;
            }}
        """)

        # Sombra sutil para el botón avanzar
        sombra_avanzar = QGraphicsDropShadowEffect()
        sombra_avanzar.setBlurRadius(18)
        sombra_avanzar.setOffset(0, 4)
        sombra_avanzar.setColor(QColor(30, 58, 138, 40))
        self.btn_avanzar.setGraphicsEffect(sombra_avanzar)

        layout.addWidget(self.btn_cancelar, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addStretch()
        layout.addWidget(self.btn_avanzar, alignment=Qt.AlignmentFlag.AlignRight)

        return contenedor


# ══════════════════════════════════════════════════
#  Ejecución standalone para previsualizar
# ══════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Fuente global
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    ventana = PantallaCajero()
    ventana.setWindowTitle("Punto de Venta — Cajero")
    ventana.resize(1200, 800)
    ventana.show()

    sys.exit(app.exec())
