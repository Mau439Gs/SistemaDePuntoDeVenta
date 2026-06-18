"""
pantalla_cobro.py — Pantalla de Cobro (Módulo Cajero)
Requerimientos: C-006, C-007, C-017
Miércoles 17 de Junio — Fase 3, Alta Prioridad
Encargado: Mauricio S. Castillo
"""

from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFrame,
    QMessageBox, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import (
    QDoubleValidator, QFont, QColor, QLinearGradient, 
    QPainter, QPaintEvent, QIcon, QPen, QPixmap
)


# ══════════════════════════════════════════════════
#  Colores y Estilos del Header
# ══════════════════════════════════════════════════
class Colors:
    HEADER_START = "#1E3A8A"
    HEADER_END = "#0F172A"
    SEARCH_BG = "rgba(255, 255, 255, 0.12)"
    SEARCH_BORDER = "rgba(255, 255, 255, 0.20)"
    SEARCH_TEXT = "#FFFFFF"
    SEARCH_FOCUS_BORDER = "rgba(255, 255, 255, 0.45)"
    HEADER_BTN = "rgba(255, 255, 255, 0.08)"
    HEADER_BTN_HOVER = "rgba(255, 255, 255, 0.18)"
    HEADER_BTN_ACTIVE = "rgba(96, 165, 250, 0.25)"
    HEADER_BTN_ACTIVE_BORDER = "#60A5FA"


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


def crear_icono_lupa(size: int = 22, color: QColor = QColor(255, 255, 255, 160)) -> QIcon:
    """Dibuja una lupa con QPainter."""
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor("transparent"))
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(color, 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    cx, cy, r = size * 0.40, size * 0.40, size * 0.28
    p.drawEllipse(int(cx - r), int(cy - r), int(r * 2), int(r * 2))
    from math import cos, sin, radians
    angle = radians(45)
    x1, y1 = cx + r * cos(angle), cy + r * sin(angle)
    p.drawLine(int(x1), int(y1), int(size * 0.85), int(size * 0.85))
    p.end()
    return QIcon(pixmap)


# ══════════════════════════════════════════════════
#  Clase Principal
# ══════════════════════════════════════════════════
class PantallaCobro(QWidget):
    """
    Pantalla de cobro del módulo cajero con barra superior.
    """
    cobro_confirmado = pyqtSignal(float, float)
    regresar_carrito = pyqtSignal()
    venta_cancelada = pyqtSignal()
    
    # Señales para la barra superior
    senal_ir_admin = pyqtSignal()
    senal_busqueda = pyqtSignal(str)

    def __init__(self, gestor_carrito, gestor_ventas, parent=None):
        super().__init__(parent)
        self._gestor_carrito = gestor_carrito
        self._gestor_ventas = gestor_ventas
        self._total = 0.0
        self.resize(1200, 800)
        self._configurar_ui()

    # ------------------------------------------------------------------ #
    #  Construcción de la UI                                             #
    # ------------------------------------------------------------------ #

    def _configurar_ui(self):
        # Layout raíz (sin márgenes para que el header toque las esquinas)
        layout_raiz = QVBoxLayout(self)
        layout_raiz.setContentsMargins(0, 0, 0, 0)
        layout_raiz.setSpacing(0)

        # 1. Agregamos el Header en la parte superior
        layout_raiz.addWidget(self._crear_header())

        # 2. Contenedor para el cuerpo de cobro (con los márgenes que teníamos antes)
        cuerpo_widget = QWidget()
        layout_cuerpo = QVBoxLayout(cuerpo_widget)
        layout_cuerpo.setContentsMargins(40, 40, 40, 40)

        # --- LA "TARJETA" CENTRAL ESTRICTA ---
        self.contenedor_central = QFrame()
        self.contenedor_central.setMaximumWidth(550) 
        self.contenedor_central.setMinimumWidth(450) 
        
        layout_central = QVBoxLayout(self.contenedor_central)
        layout_central.setContentsMargins(0, 0, 0, 0)
        layout_central.setSpacing(35) 
        
        layout_central.addLayout(self._crear_campos_cobro())
        layout_central.addLayout(self._crear_botones_centrales())

        layout_centrado_horizontal = QHBoxLayout()
        layout_centrado_horizontal.addStretch()
        layout_centrado_horizontal.addWidget(self.contenedor_central)
        layout_centrado_horizontal.addStretch()

        # Ensamblamos el cuerpo
        layout_cuerpo.addStretch()
        layout_cuerpo.addLayout(layout_centrado_horizontal)
        layout_cuerpo.addStretch()

        # Botón Cancelar (Anclado abajo a la izquierda dentro del cuerpo)
        layout_inferior = QHBoxLayout()
        layout_inferior.setContentsMargins(0, 0, 0, 0)
        layout_inferior.addWidget(self._crear_btn_cancelar())
        layout_inferior.addStretch()
        layout_cuerpo.addLayout(layout_inferior)

        # Agregamos el cuerpo al layout raíz, debajo del header
        layout_raiz.addWidget(cuerpo_widget)

    def _crear_header(self) -> QWidget:
        """Crea la barra de navegación idéntica a PantallaCajero."""
        header = GradientHeader()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(12)

        layout.addStretch(1)

        self.barra_busqueda = QLineEdit()
        self.barra_busqueda.setFixedHeight(42)
        self.barra_busqueda.setMinimumWidth(480)
        self.barra_busqueda.setMaximumWidth(650)
        self.barra_busqueda.setFont(QFont("Segoe UI", 13))
        self.barra_busqueda.textChanged.connect(self.senal_busqueda.emit)

        icono_lupa = crear_icono_lupa(22, QColor(255, 255, 255, 160))
        self.barra_busqueda.addAction(icono_lupa, QLineEdit.ActionPosition.TrailingPosition)

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

        sombra_busqueda = QGraphicsDropShadowEffect()
        sombra_busqueda.setBlurRadius(24)
        sombra_busqueda.setOffset(0, 2)
        sombra_busqueda.setColor(QColor(96, 165, 250, 50))
        self.barra_busqueda.setGraphicsEffect(sombra_busqueda)

        layout.addWidget(self.barra_busqueda)
        layout.addStretch(1)

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

    def _crear_campos_cobro(self) -> QGridLayout:
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(25)

        font_label = QFont()
        font_label.setPointSize(14)
        
        font_valor = QFont()
        font_valor.setPointSize(14)
        font_valor.setBold(True)

        lbl_total = QLabel("Total a pagar:")
        lbl_total.setFont(font_label)
        lbl_monto = QLabel("Monto recibido:")
        lbl_monto.setFont(font_label)
        lbl_cambio = QLabel("Cambio:")
        lbl_cambio.setFont(font_label)

        self._lbl_total_valor = QLabel("------ $")
        self._lbl_total_valor.setFont(font_valor)
        self._lbl_cambio_valor = QLabel("------ $")
        self._lbl_cambio_valor.setFont(font_valor)

        self._inp_monto = QLineEdit()
        self._inp_monto.setPlaceholderText("Efectivo")
        self._inp_monto.setValidator(QDoubleValidator(0.0, 999999.99, 2, self))
        self._inp_monto.setFont(font_valor)
        self._inp_monto.setFixedWidth(110)
        self._inp_monto.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._inp_monto.textChanged.connect(self._actualizar_cambio)

        lbl_simbolo = QLabel("$")
        lbl_simbolo.setFont(font_valor)

        layout_input = QHBoxLayout()
        layout_input.setContentsMargins(0, 0, 0, 0)
        layout_input.setSpacing(8)
        layout_input.addWidget(self._inp_monto)
        layout_input.addWidget(lbl_simbolo)

        grid.addWidget(lbl_total, 0, 0, Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(self._lbl_total_valor, 0, 2, Qt.AlignmentFlag.AlignRight)

        grid.addWidget(lbl_monto, 1, 0, Qt.AlignmentFlag.AlignLeft)
        grid.addLayout(layout_input, 1, 2, Qt.AlignmentFlag.AlignRight)

        grid.addWidget(lbl_cambio, 2, 0, Qt.AlignmentFlag.AlignLeft)
        grid.addWidget(self._lbl_cambio_valor, 2, 2, Qt.AlignmentFlag.AlignRight)

        grid.setColumnStretch(1, 1)

        return grid

    def _crear_botones_centrales(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setSpacing(20)
        layout.addStretch()

        self._btn_regresar = QPushButton("Regresar al carrito")
        self._btn_regresar.setFixedHeight(40)
        self._btn_regresar.setStyleSheet(
            "QPushButton { background-color: #f0a500; color: white; border-radius: 12px; padding: 0 20px; font-weight: bold; }"
            "QPushButton:hover { background-color: #d4920a; }"
        )
        self._btn_regresar.clicked.connect(self.regresar_carrito.emit)
        layout.addWidget(self._btn_regresar)

        self._btn_confirmar = QPushButton("Confirmar cobro")
        self._btn_confirmar.setFixedHeight(40)
        self._btn_confirmar.setEnabled(False)
        self._btn_confirmar.setStyleSheet(
            "QPushButton:enabled { background-color: #2196F3; color: white; border-radius: 12px; padding: 0 20px; font-weight: bold; }"
            "QPushButton:disabled { background-color: #b0bec5; color: #fff; border-radius: 12px; padding: 0 20px; }"
            "QPushButton:enabled:hover { background-color: #1565C0; }"
        )
        self._btn_confirmar.clicked.connect(self._confirmar_cobro)
        layout.addWidget(self._btn_confirmar)

        layout.addStretch()
        return layout

    def _crear_btn_cancelar(self) -> QPushButton:
        btn = QPushButton("Cancelar Venta")
        btn.setFixedHeight(40)
        btn.setStyleSheet(
            "QPushButton { background-color: #e53935; color: white; border-radius: 12px; padding: 0 22px; font-weight: bold; }"
            "QPushButton:hover { background-color: #b71c1c; }"
        )
        btn.clicked.connect(self._solicitar_cancelacion)
        return btn

    # ------------------------------------------------------------------ #
    #  Lógica                                                            #
    # ------------------------------------------------------------------ #

    def cargar_total(self, total: float):
        self._total = total
        self._lbl_total_valor.setText(f"{total:,.2f} $")
        self._inp_monto.clear()
        self._lbl_cambio_valor.setText("------ $")
        self._btn_confirmar.setEnabled(False)

    def _actualizar_cambio(self, texto: str):
        texto = texto.strip()
        if not texto:
            self._lbl_cambio_valor.setText("------ $")
            self._btn_confirmar.setEnabled(False)
            return

        try:
            monto = float(texto)
        except ValueError:
            self._lbl_cambio_valor.setText("------ $")
            self._btn_confirmar.setEnabled(False)
            return

        cambio = monto - self._total
        if cambio < 0:
            self._lbl_cambio_valor.setText("------ $")
            self._lbl_cambio_valor.setStyleSheet("color: red;")
            self._btn_confirmar.setEnabled(False)
        else:
            self._lbl_cambio_valor.setText(f"{cambio:,.2f} $")
            self._lbl_cambio_valor.setStyleSheet("")
            self._btn_confirmar.setEnabled(True)

    def _confirmar_cobro(self):
        try:
            monto = float(self._inp_monto.text())
        except ValueError:
            return

        cambio = monto - self._total

        try:
            self._gestor_ventas.confirmar_venta(self._gestor_carrito.obtener_items())
        except Exception as e:
            QMessageBox.critical(self, "Error al confirmar", f"No se pudo registrar la venta:\n{e}")
            return

        self.cobro_confirmado.emit(monto, cambio)

    def _solicitar_cancelacion(self):
        respuesta = QMessageBox.question(
            self,
            "Cancelar Venta",
            "¿Deseas cancelar la venta actual?\nSe perderán todos los productos del carrito.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if respuesta == QMessageBox.StandardButton.Yes:
            self._gestor_carrito.vaciar_carrito()
            self.venta_cancelada.emit()


if __name__ == "__main__":

    import sys
    from logica.gestor_carrito import GestorCarrito
    from logica.gestor_ventas import GestorVentas
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    ventana = PantallaCobro(GestorCarrito, GestorVentas)
    ventana.show()
    ventana.cargar_total(100)
    sys.exit(app.exec())