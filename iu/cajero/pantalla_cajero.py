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
#  Generador de íconos pintados con QPainter
# ══════════════════════════════════════════════════

def crear_icono_lupa(size: int = 22, color: QColor = QColor(255, 255, 255, 160)) -> QIcon:
    """Dibuja una lupa con QPainter — siempre visible."""
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor("transparent"))
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(color, 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    # Círculo de la lupa
    cx, cy, r = size * 0.40, size * 0.40, size * 0.28
    p.drawEllipse(int(cx - r), int(cy - r), int(r * 2), int(r * 2))
    # Mango de la lupa
    from math import cos, sin, radians
    angle = radians(45)
    x1 = cx + r * cos(angle)
    y1 = cy + r * sin(angle)
    x2 = size * 0.85
    y2 = size * 0.85
    p.drawLine(int(x1), int(y1), int(x2), int(y2))
    p.end()
    return QIcon(pixmap)


def crear_icono_x(size: int = 20, color: QColor = QColor(255, 255, 255)) -> QIcon:
    """Dibuja una X con QPainter."""
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor("transparent"))
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(QPen(color, 2.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
    m = int(size * 0.22)  # margen
    p.drawLine(m, m, size - m, size - m)
    p.drawLine(size - m, m, m, size - m)
    p.end()
    return QIcon(pixmap)


def crear_icono_flecha(size: int = 20, color: QColor = QColor(30, 41, 59)) -> QIcon:
    """Dibuja una flecha → con QPainter."""
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor("transparent"))
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(QPen(color, 2.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    mid = size // 2
    m = int(size * 0.18)
    # Línea horizontal
    p.drawLine(m, mid, size - m, mid)
    # Cabeza de flecha
    head = int(size * 0.28)
    p.drawLine(size - m, mid, size - m - head, mid - head)
    p.drawLine(size - m, mid, size - m - head, mid + head)
    p.end()
    return QIcon(pixmap)


# ══════════════════════════════════════════════════
#  Fondo premium para el cuerpo central
# ══════════════════════════════════════════════════

class FondoPremium(QWidget):
    """Fondo blanco con gradiente radial sutil y patrón de puntos decorativos."""

    def paintEvent(self, event: QPaintEvent):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # Fondo base blanco
        p.fillRect(self.rect(), QColor(Colors.BG_WHITE))

        # Gradiente radial sutil desde el centro (muy tenue)
        from PyQt6.QtGui import QRadialGradient
        gradient = QRadialGradient(w / 2, h / 2, max(w, h) * 0.7)
        gradient.setColorAt(0.0, QColor(237, 242, 255, 35))   # Azul hielo ultra tenue
        gradient.setColorAt(0.5, QColor(245, 247, 250, 20))
        gradient.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.fillRect(self.rect(), gradient)

        # Patrón de puntos decorativos sutiles
        p.setPen(Qt.PenStyle.NoPen)
        dot_color = QColor(200, 210, 225, 22)  # Gris azulado ultra tenue
        p.setBrush(dot_color)
        spacing = 32
        dot_r = 1.5
        for x in range(spacing, w, spacing):
            for y in range(spacing, h, spacing):
                p.drawEllipse(int(x - dot_r), int(y - dot_r), int(dot_r * 2), int(dot_r * 2))

        # Línea decorativa superior fina
        p.setPen(QPen(QColor(30, 58, 138, 18), 1))
        p.drawLine(0, 0, w, 0)

        p.end()


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

        # ── 2. CUERPO CENTRAL (fondo premium) ──
        self.contenedor_central = FondoPremium()
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

        # ── Espaciador izquierdo para centrar la barra ──
        layout.addStretch(1)

        # ── Barra de búsqueda (centrada) ──
        self.barra_busqueda = QLineEdit()
        self.barra_busqueda.setFixedHeight(42)
        self.barra_busqueda.setMinimumWidth(480)
        self.barra_busqueda.setMaximumWidth(650)
        self.barra_busqueda.setFont(QFont("Segoe UI", 13))
        self.barra_busqueda.textChanged.connect(self.senal_busqueda.emit)

        # Ícono de lupa a la derecha (pintado directo, siempre visible)
        icono_lupa = crear_icono_lupa(22, QColor(255, 255, 255, 160))
        self.barra_busqueda.addAction(
            icono_lupa, QLineEdit.ActionPosition.TrailingPosition
        )

        self.barra_busqueda.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.SEARCH_BG};
                border: 1.5px solid {Colors.SEARCH_BORDER};
                border-radius: 14px;
                padding: 0 42px 0 18px;
                color: {Colors.SEARCH_TEXT};
                font-size: 13px;
                selection-background-color: rgba(96, 165, 250, 0.35);
            }}
            QLineEdit:focus {{
                border: 1.5px solid {Colors.SEARCH_FOCUS_BORDER};
                background-color: rgba(255, 255, 255, 0.18);
            }}
        """)

        # Glow sutil alrededor de la barra
        sombra_busqueda = QGraphicsDropShadowEffect()
        sombra_busqueda.setBlurRadius(24)
        sombra_busqueda.setOffset(0, 2)
        sombra_busqueda.setColor(QColor(96, 165, 250, 50))
        self.barra_busqueda.setGraphicsEffect(sombra_busqueda)

        layout.addWidget(self.barra_busqueda)

        # ── Espaciador derecho (más corto para dejar espacio a botones) ──
        layout.addStretch(1)

        # ── Botones de navegación ──
        self.btn_cajero = self._crear_boton_header("  Cajero", activo=True)
        self.btn_admin = self._crear_boton_header("  Admin.")
        self.btn_admin.clicked.connect(self.senal_ir_admin.emit)

        layout.addWidget(self.btn_cajero)
        layout.addWidget(self.btn_admin)

        return header

    def _crear_boton_header(self, texto: str, activo: bool = False) -> QPushButton:
        btn = QPushButton(texto)
        btn.setFixedHeight(38)
        btn.setMinimumWidth(110)
        btn.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

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

        self.btn_cancelar.setIcon(crear_icono_x(18, QColor(255, 255, 255)))
        self.btn_cancelar.setIconSize(QSize(18, 18))

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

        self.btn_avanzar.setIcon(crear_icono_flecha(18, QColor(30, 41, 59)))
        self.btn_avanzar.setIconSize(QSize(18, 18))
        self.btn_avanzar.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

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
