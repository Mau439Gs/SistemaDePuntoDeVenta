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
    QPushButton, QLabel, QSizePolicy, QGraphicsDropShadowEffect,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QDialog, QListWidget, QListWidgetItem, QFrame
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPoint, QTimer
from PyQt6.QtGui import (
    QFont, QColor, QLinearGradient, QPainter,
    QPaintEvent, QIcon, QPen, QPixmap, QIntValidator, QDoubleValidator
)

from iu.admin.dialogos_pin import DialogoConfigurarPIN, DialogoPIN


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
    BLUE_ADVANCE = "#2563EB"
    BLUE_ADVANCE_HOVER = "#1D4ED8"
    BLUE_ADVANCE_TEXT = "#FFFFFF"

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
        self.setFixedHeight(88)

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


def crear_icono_bag(size: int = 20, color: QColor = QColor(255, 255, 255)) -> QIcon:
    """Dibuja una bolsa de compras minimalista con QPainter."""
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor("transparent"))
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(QPen(color, 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    # Cuerpo de la bolsa
    x, y, w, h = int(size * 0.26), int(size * 0.40), int(size * 0.48), int(size * 0.46)
    p.drawRect(x, y, w, h)
    # Asa de la bolsa
    hx, hy, hw, hh = int(size * 0.35), int(size * 0.18), int(size * 0.30), int(size * 0.44)
    p.drawArc(hx, hy, hw, hh, 0, 180 * 16)
    p.end()
    return QIcon(pixmap)


def crear_icono_gear(size: int = 20, color: QColor = QColor(255, 255, 255)) -> QIcon:
    """Dibuja un engranaje técnico minimalista con QPainter."""
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor("transparent"))
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(QPen(color, 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    cx, cy = size / 2.0, size / 2.0
    r = size * 0.20
    # Agujero central
    p.drawEllipse(int(cx - r), int(cy - r), int(r * 2), int(r * 2))
    # Dientes exteriores (8 dientes)
    from math import cos, sin, radians
    for i in range(8):
        angle = radians(i * 45)
        x1 = cx + r * cos(angle)
        y1 = cy + r * sin(angle)
        x2 = cx + r * 1.8 * cos(angle)
        y2 = cy + r * 1.8 * sin(angle)
        p.drawLine(int(x1), int(y1), int(x2), int(y2))
    p.end()
    return QIcon(pixmap)



# ══════════════════════════════════════════════════
#  Panel de Resultados Flotante (Búsqueda)
# ══════════════════════════════════════════════════

class PanelResultados(QListWidget):
    """Panel flotante con sombra para mostrar los resultados de búsqueda."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1.5px solid #CBD5E1;
                border-radius: 12px;
                padding: 8px;
                font-family: "Segoe UI";
                font-size: 17px;
                color: #1E293B;
            }
            QListWidget::item {
                padding: 14px 18px;
                border-radius: 8px;
                margin: 2px 0;
            }
            QListWidget::item:hover {
                background-color: #F1F5F9;
                color: #0F172A;
            }
            QListWidget::item:selected {
                background-color: #DBEAFE;
                color: #1E40AF;
                font-weight: bold;
            }
        """)
        
        # Sombra sutil
        sombra = QGraphicsDropShadowEffect(self)
        sombra.setBlurRadius(20)
        sombra.setOffset(0, 6)
        sombra.setColor(QColor(0, 0, 0, 45))
        self.setGraphicsEffect(sombra)

    def posicionar_bajo_busqueda(self, barra):
        pos_global = barra.mapToGlobal(QPoint(0, barra.height() + 6))
        self.move(pos_global)
        self.setFixedWidth(barra.width())
        # Altura dinámica escalada por ítem para evitar recortes
        cant = self.count()
        item_height = 56  # Altura ampliada por ítem
        self.setFixedHeight(min(6, cant) * item_height + 16 if cant > 0 else 60)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.itemClicked.emit(self.currentItem())
        elif event.key() == Qt.Key.Key_Escape:
            self.hide()
        else:
            QListWidget.keyPressEvent(self, event)


# ══════════════════════════════════════════════════
#  Selector de Cantidades en la Tabla (- / input / +)
# ══════════════════════════════════════════════════

class SelectorCantidadTabla(QWidget):
    """Control compacto de cantidad para colocar dentro de la celda de la tabla."""
    senal_cantidad_cambiada = pyqtSignal(float)

    def __init__(self, cantidad_inicial: float, es_granel: bool = False, parent=None):
        super().__init__(parent)
        self.es_granel = es_granel
        self.cantidad = cantidad_inicial
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 4, 0, 4)
        main_layout.setSpacing(6)

        layout = QHBoxLayout()
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(8)

        # Botón Menos (Más grande)
        self.btn_menos = QPushButton("−")
        self.btn_menos.setFixedSize(46, 46)
        self.btn_menos.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.btn_menos.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_menos.clicked.connect(self._on_menos_clicked)
        
        # Campo de Entrada (Más grande)
        self.txt_cantidad = QLineEdit(self._formatear_cantidad(self.cantidad))
        self.txt_cantidad.setFixedSize(96, 46)
        self.txt_cantidad.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.txt_cantidad.setFont(QFont("Segoe UI", 15))
        
        if self.es_granel:
            validador = QDoubleValidator(0.0, 9999.99, 2, self)
            validador.setNotation(QDoubleValidator.Notation.StandardNotation)
            self.txt_cantidad.setValidator(validador)
        else:
            validador = QIntValidator(0, 9999, self)
            self.txt_cantidad.setValidator(validador)
            
        self.txt_cantidad.editingFinished.connect(self._on_editing_finished)

        # Botón Mas (Más grande)
        self.btn_mas = QPushButton("+")
        self.btn_mas.setFixedSize(46, 46)
        self.btn_mas.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.btn_mas.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mas.clicked.connect(self._on_mas_clicked)

        # Estilo visual moderno y limpio
        self.setStyleSheet("""
            SelectorCantidadTabla {
                background: transparent;
            }
            QPushButton {
                background-color: #F1F5F9;
                border: 1px solid #CBD5E1;
                border-radius: 10px;
                color: #475569;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
                color: #0F172A;
            }
            QPushButton:disabled {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                color: #CBD5E1;
            }
            QLineEdit {
                background-color: white;
                border: 1px solid #CBD5E1;
                border-radius: 10px;
                color: #1E293B;
            }
            QLineEdit:focus {
                border: 1.5px solid #60A5FA;
            }
            QLineEdit::placeholder {
                color: #94A3B8;
            }
        """)

        layout.addWidget(self.btn_menos)
        layout.addWidget(self.txt_cantidad)
        layout.addWidget(self.btn_mas)

        main_layout.addLayout(layout)

        self.lbl_tipo = QLabel("Granel" if self.es_granel else "Unidad")
        self.lbl_tipo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_tipo.setStyleSheet("color: #94A3B8; font-size: 13px;")
        main_layout.addWidget(self.lbl_tipo)

        self._actualizar_estados_botones()

    def _formatear_cantidad(self, valor: float) -> str:
        if self.es_granel:
            return str(round(valor, 2))
        return str(int(valor))

    def _on_menos_clicked(self):
        paso = 0.1 if self.es_granel else 1.0
        nueva = round(self.cantidad - paso, 2)
        min_lim = 0.1 if self.es_granel else 1.0
        
        if nueva >= min_lim:
            self.cantidad = nueva
            self.txt_cantidad.setText(self._formatear_cantidad(self.cantidad))
            self._actualizar_estados_botones()
            self.senal_cantidad_cambiada.emit(self.cantidad)

    def _on_mas_clicked(self):
        paso = 0.1 if self.es_granel else 1.0
        self.cantidad = round(self.cantidad + paso, 2)
        self.txt_cantidad.setText(self._formatear_cantidad(self.cantidad))
        self._actualizar_estados_botones()
        self.senal_cantidad_cambiada.emit(self.cantidad)

    def _on_editing_finished(self):
        texto = self.txt_cantidad.text().strip().replace(",", ".")
        if not texto:
            valor = self.cantidad
        else:
            try:
                valor = float(texto) if self.es_granel else int(texto)
            except ValueError:
                valor = self.cantidad
            
        if valor < 0:
            valor = 0
            
        if valor != self.cantidad:
            self.cantidad = valor
            self.txt_cantidad.setText(self._formatear_cantidad(self.cantidad))
            self._actualizar_estados_botones()
            self.senal_cantidad_cambiada.emit(self.cantidad)

    def _actualizar_estados_botones(self):
        limite = 0.1 if self.es_granel else 1.0
        self.btn_menos.setEnabled(self.cantidad > limite)


# ══════════════════════════════════════════════════
#  Botón de Eliminación Roja (Bote de Basura)
# ══════════════════════════════════════════════════

class BotonEliminarTabla(QPushButton):
    """Botón cuadrado rojo con icono de bote de basura pintado con QPainter."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(52, 52)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                border: none;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
            QPushButton:pressed {
                background-color: #B91C1C;
            }
        """)
        
    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QPen(QColor("white"), 2.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.setBrush(Qt.BrushStyle.NoBrush)
        
        w, h = self.width(), self.height()
        
        # Tapa del bote de basura
        p.drawLine(int(w * 0.22), int(h * 0.28), int(w * 0.78), int(h * 0.28))
        # Asa de la tapa
        p.drawArc(int(w * 0.40), int(h * 0.16), int(w * 0.20), int(h * 0.20), 0, 180 * 16)
        # Contenedor del bote
        p.drawLine(int(w * 0.28), int(h * 0.28), int(w * 0.32), int(h * 0.82))
        p.drawLine(int(w * 0.72), int(h * 0.28), int(w * 0.68), int(h * 0.82))
        p.drawLine(int(w * 0.32), int(h * 0.82), int(w * 0.68), int(h * 0.82))
        
        # Líneas verticales internas
        p.drawLine(int(w * 0.43), int(h * 0.36), int(w * 0.43), int(h * 0.74))
        p.drawLine(int(w * 0.57), int(h * 0.36), int(w * 0.57), int(h * 0.74))
        p.end()


# ══════════════════════════════════════════════════
#  Diálogo de Confirmación de Eliminación
# ══════════════════════════════════════════════════

class DialogoBaseCabecera(QDialog):
    """Clase base para diálogos con cabecera azul y botones cápsula."""
    def __init__(self, titulo: str, texto_confirmar: str, texto_cancelar: str, parent=None):
        super().__init__(parent)
        self.titulo = titulo
        self.texto_confirmar = texto_confirmar
        self.texto_cancelar = texto_cancelar
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(380, 160)
        self._setup_ui()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def _setup_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        
        self.contenedor = QFrame(self)
        self.contenedor.setObjectName("ContenedorDialogo")
        self.contenedor.setStyleSheet("""
            QFrame#ContenedorDialogo {
                background-color: white;
                border: 1.5px solid #CBD5E1;
                border-radius: 16px;
            }
        """)
        layout_principal.addWidget(self.contenedor)
        
        layout_body = QVBoxLayout(self.contenedor)
        layout_body.setContentsMargins(0, 0, 0, 0)
        layout_body.setSpacing(0)
        
        # Cabecera Azul
        cabecera = QFrame()
        cabecera.setObjectName("Cabecera")
        cabecera.setFixedHeight(50)
        cabecera.setStyleSheet("""
            QFrame#Cabecera {
                background-color: #2563EB;
                border-top-left-radius: 14px;
                border-top-right-radius: 14px;
                border-bottom: none;
            }
        """)
        layout_cabecera = QHBoxLayout(cabecera)
        layout_cabecera.setContentsMargins(0, 0, 0, 0)
        
        lbl_titulo = QLabel(self.titulo, cabecera)
        lbl_titulo.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet("color: white; border: none;")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_cabecera.addWidget(lbl_titulo)
        layout_body.addWidget(cabecera)
        
        # Cuerpo
        cuerpo = QWidget()
        layout_cuerpo_interno = QVBoxLayout(cuerpo)
        layout_cuerpo_interno.setContentsMargins(16, 24, 16, 24)
        layout_cuerpo_interno.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Botones Cápsula
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(24)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.btn_confirmar = QPushButton(self.texto_confirmar, cuerpo)
        self.btn_confirmar.setObjectName("btn_confirmar")
        self.btn_confirmar.setFixedSize(120, 42)
        self.btn_confirmar.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.btn_confirmar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_confirmar.clicked.connect(self.accept)
        self.btn_confirmar.setStyleSheet("""
            QPushButton#btn_confirmar {
                background-color: #52C5D8; /* Celeste original */
                color: white;
                border: none;
                border-radius: 21px;
            }
            QPushButton#btn_confirmar:hover {
                background-color: #42AFC1;
            }
            QPushButton#btn_confirmar:pressed {
                background-color: #339AA8;
            }
        """)
        
        self.btn_cancelar = QPushButton(self.texto_cancelar, cuerpo)
        self.btn_cancelar.setObjectName("btn_cancelar")
        self.btn_cancelar.setFixedSize(120, 42)
        self.btn_cancelar.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancelar.clicked.connect(self.reject)
        self.btn_cancelar.setStyleSheet("""
            QPushButton#btn_cancelar {
                background-color: #DE4A4A; /* Rojo original */
                color: white;
                border: none;
                border-radius: 21px;
            }
            QPushButton#btn_cancelar:hover {
                background-color: #C63D3D;
            }
            QPushButton#btn_cancelar:pressed {
                background-color: #AF3030;
            }
        """)
        
        btn_layout.addWidget(self.btn_confirmar)
        btn_layout.addWidget(self.btn_cancelar)
        layout_cuerpo_interno.addLayout(btn_layout)
        layout_body.addWidget(cuerpo)
        
        # Foco predeterminado en el botón derecho (Cancelar/No) por seguridad
        self.btn_cancelar.setDefault(True)
        self.btn_cancelar.setFocus()

        # Instalar event filter para navegación por teclado
        self.btn_confirmar.installEventFilter(self)
        self.btn_cancelar.installEventFilter(self)

    def eventFilter(self, watched, event):
        from PyQt6.QtCore import QEvent
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            if watched == self.btn_confirmar:
                if key == Qt.Key.Key_Right:
                    self.btn_cancelar.setFocus()
                    return True
                elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    self.accept()
                    return True
            elif watched == self.btn_cancelar:
                if key == Qt.Key.Key_Left:
                    self.btn_confirmar.setFocus()
                    return True
                elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    self.reject()
                    return True
        return super().eventFilter(watched, event)


class DialogoConfirmacion(DialogoBaseCabecera):
    """Diálogo modal para confirmar eliminación con cabecera azul y botones estilo cápsula."""
    def __init__(self, nombre_producto: str = "", parent=None):
        super().__init__("Confirmar eliminación", "Confirmar", "Cancelar", parent)


class DialogoEliminarCarrito(DialogoBaseCabecera):
    """Diálogo modal para confirmar vaciado de carrito con cabecera azul."""
    def __init__(self, parent=None):
        super().__init__("Eliminar carrito", "sí", "NO", parent)


# ══════════════════════════════════════════════════
#  Fondo premium para el cuerpo central
# ══════════════════════════════════════════════════

class FondoPremium(QWidget):
    """Fondo premium con efecto de gradiente Aurora suave y cuadrícula de precisión sutil."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("background: transparent;")

    def paintEvent(self, event: QPaintEvent):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # 1. Fondo base ultra-limpio (Soft Slate Gray)
        p.fillRect(self.rect(), QColor("#F8FAFC"))

        # 2. Mezcla de gradientes radiales orgánicos (Efecto Aurora sutil pero visible)
        from PyQt6.QtGui import QRadialGradient

        # Aurora 1: Azul Cielo Brillante (Superior Izquierda)
        g1 = QRadialGradient(w * 0.15, h * 0.15, max(w, h) * 0.65)
        g1.setColorAt(0.0, QColor(147, 197, 253, 110))  # Azul celeste (#93C5FD)
        g1.setColorAt(0.5, QColor(191, 219, 254, 50))
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

    def __init__(self, gestor_productos=None, gestor_carrito=None, gestor_ventas=None, gestor_autenticacion=None, parent=None):
        super().__init__(parent)
        self.gestor_productos = gestor_productos
        self.gestor_carrito = gestor_carrito
        self.gestor_ventas = gestor_ventas
        self.gestor_autenticacion = gestor_autenticacion
        self.setMinimumSize(1280, 800)
        self._setup_ui()

    def _setup_ui(self):
        # ── Fondo general limpio (con selector ID para no heredar a hijos) ──
        self.setObjectName("PantallaCajero")
        self.setStyleSheet(f"QWidget#PantallaCajero {{ background-color: {Colors.BG}; }}")

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

        # Layout interno del cuerpo
        self.layout_central = QVBoxLayout(self.contenedor_central)
        self.layout_central.setContentsMargins(24, 20, 24, 16)
        self.layout_central.setSpacing(0)

        # Marco de la tabla estilo tarjeta redondeada (idéntico al prototipo)
        self.marco_tabla = QFrame()
        self.marco_tabla.setObjectName("MarcoTabla")
        self.marco_tabla.setStyleSheet("""
            QFrame#MarcoTabla {
                background-color: white;
                border: 1.5px solid #E2E8F0;
                border-radius: 16px;
            }
        """)
        
        layout_marco = QVBoxLayout(self.marco_tabla)
        layout_marco.setContentsMargins(4, 4, 4, 4)
        
        # Tabla QTableWidget
        self.tabla_carrito = QTableWidget()
        self.tabla_carrito.setColumnCount(5)
        self.tabla_carrito.setHorizontalHeaderLabels(["Producto", "Cantidad", "Precio", "Subtotal", ""])
        self.tabla_carrito.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabla_carrito.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.tabla_carrito.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.tabla_carrito.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.tabla_carrito.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.tabla_carrito.setColumnWidth(1, 240)
        self.tabla_carrito.setColumnWidth(2, 180)
        self.tabla_carrito.setColumnWidth(3, 180)
        self.tabla_carrito.setColumnWidth(4, 110)
        
        self.tabla_carrito.verticalHeader().setVisible(False)
        self.tabla_carrito.verticalHeader().setDefaultSectionSize(95)
        self.tabla_carrito.setShowGrid(False)
        self.tabla_carrito.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_carrito.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tabla_carrito.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.tabla_carrito.itemSelectionChanged.connect(self._actualizar_alertas_stock)
        
        self.tabla_carrito.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                border: none;
                gridline-color: transparent;
                font-family: "Segoe UI";
                font-size: 15px;
                color: #1E293B;
            }
            QTableWidget::item {
                border-bottom: 1.5px solid #F1F5F9;
                padding: 12px;
            }
            QTableWidget::item:selected {
                background-color: #DBEAFE;
                color: #1E40AF;
            }
            QHeaderView::section {
                background-color: #F8FAFC;
                border: none;
                border-bottom: 2px solid #CBD5E1;
                font-family: "Segoe UI";
                font-size: 13pt;
                font-weight: bold;
                color: #475569;
                padding: 12px;
            }
        """)
        
        layout_marco.addWidget(self.tabla_carrito)
        self.layout_central.addWidget(self.marco_tabla)

        # Panel de Total (centrado)
        self.panel_total = QWidget()
        layout_total = QVBoxLayout(self.panel_total)
        layout_total.setContentsMargins(0, 20, 0, 12)
        layout_total.setSpacing(8)
        
        self.lbl_total = QLabel("Total $-----")
        self.lbl_total.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self.lbl_total.setStyleSheet("color: #0F172A;")
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_total.addWidget(self.lbl_total)

        self.lbl_alerta_stock = QLabel("")
        self.lbl_alerta_stock.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.lbl_alerta_stock.setStyleSheet("color: #EF4444; background: transparent; border: none;")
        self.lbl_alerta_stock.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_alerta_stock.setVisible(False)
        layout_total.addWidget(self.lbl_alerta_stock)
        
        self.layout_central.addWidget(self.panel_total)
        layout_principal.addWidget(self.contenedor_central)

        # ── 3. BOTONES INFERIORES ──
        layout_principal.addWidget(self._crear_barra_inferior())

        # ── Panel flotante de búsqueda ──
        self.panel_resultados = PanelResultados(self)
        self.panel_resultados.itemClicked.connect(self._on_item_resultado_clicked)
        self.barra_busqueda.keyPressEvent = self._on_barra_key_press

        # Instalar event filters para navegación por teclado
        self.barra_busqueda.installEventFilter(self)
        self.panel_resultados.installEventFilter(self)
        self.tabla_carrito.installEventFilter(self)
        self.btn_cancelar.installEventFilter(self)
        self.btn_avanzar.installEventFilter(self)
        self.btn_cajero.installEventFilter(self)
        self.btn_admin.installEventFilter(self)

        # Configurar orden de pestañas (Tab order)
        self.setTabOrder(self.barra_busqueda, self.btn_admin)
        self.setTabOrder(self.btn_admin, self.tabla_carrito)
        self.setTabOrder(self.tabla_carrito, self.btn_cancelar)
        self.setTabOrder(self.btn_cancelar, self.btn_avanzar)

        self.senal_avanzar_cobro.connect(self._on_avanzar_clicked)

        self._actualizar_tabla()

    def _crear_header(self) -> QWidget:
        header = GradientHeader()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(16)

        layout.addStretch(1)

        self.barra_busqueda = QLineEdit()
        self.barra_busqueda.setFixedHeight(48)
        self.barra_busqueda.setMinimumWidth(520)
        self.barra_busqueda.setMaximumWidth(750)
        self.barra_busqueda.setFont(QFont("Segoe UI", 14))
        self.barra_busqueda.textChanged.connect(self.senal_busqueda.emit)
        self.barra_busqueda.textChanged.connect(self._on_busqueda_changed)

        icono_lupa = crear_icono_lupa(24, QColor(255, 255, 255, 160))
        self.barra_busqueda.addAction(
            icono_lupa, QLineEdit.ActionPosition.TrailingPosition
        )

        self.barra_busqueda.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.SEARCH_BG};
                border: 1.5px solid {Colors.SEARCH_BORDER};
                border-radius: 14px;
                padding: 0 48px 0 20px;
                color: {Colors.SEARCH_TEXT};
                font-size: 15px;
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

        icono_cajero = crear_icono_bag(22, QColor(255, 255, 255))
        icono_admin = crear_icono_gear(22, QColor(148, 163, 184))

        self.btn_cajero = self._crear_boton_header("  Cajero", icono_cajero, activo=True)
        self.btn_admin = self._crear_boton_header("  Admin.", icono_admin, activo=False)
        self.btn_admin.clicked.connect(self._on_admin_clicked)

        layout.addWidget(self.btn_cajero)
        layout.addWidget(self.btn_admin)

        return header

    def _crear_boton_header(self, texto: str, icono: QIcon, activo: bool = False) -> QPushButton:
        btn = QPushButton(texto)
        btn.setIcon(icono)
        btn.setIconSize(QSize(22, 22))
        btn.setFixedHeight(46)
        btn.setMinimumWidth(150)
        btn.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

        if activo:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.HEADER_BTN_ACTIVE};
                    color: #FFFFFF;
                    border: 1.5px solid {Colors.HEADER_BTN_ACTIVE_BORDER};
                    border-radius: 12px;
                    padding: 0 16px;
                }}
                QPushButton:hover {{
                    background-color: rgba(96, 165, 250, 0.35);
                    border: 1.5px solid #93C5FD;
                }}
            """)
            glow = QGraphicsDropShadowEffect(btn)
            glow.setBlurRadius(15)
            glow.setOffset(0, 0)
            glow.setColor(QColor(96, 165, 250, 100))
            btn.setGraphicsEffect(glow)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(255, 255, 255, 0.04);
                    color: #94A3B8;
                    border: 1.5px solid rgba(255, 255, 255, 0.08);
                    border-radius: 12px;
                    padding: 0 16px;
                }}
                QPushButton:hover {{
                    background-color: rgba(255, 255, 255, 0.12);
                    color: #FFFFFF;
                    border: 1.5px solid rgba(255, 255, 255, 0.20);
                }}
                QPushButton:pressed {{
                    background-color: rgba(255, 255, 255, 0.08);
                }}
            """)
        return btn

    def _crear_barra_inferior(self) -> QWidget:
        contenedor = QWidget()
        contenedor.setFixedHeight(96)
        contenedor.setStyleSheet(f"background-color: {Colors.BG_WHITE};")

        layout = QHBoxLayout(contenedor)
        layout.setContentsMargins(28, 0, 28, 24)

        self.btn_cancelar = QPushButton("  Cancelar Venta")
        self.btn_cancelar.setFixedSize(240, 56)
        self.btn_cancelar.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        self.btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancelar.clicked.connect(self._on_cancelar_venta)

        self.btn_cancelar.setIcon(crear_icono_x(22, QColor(255, 255, 255)))
        self.btn_cancelar.setIconSize(QSize(22, 22))

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

        sombra_cancelar = QGraphicsDropShadowEffect()
        sombra_cancelar.setBlurRadius(18)
        sombra_cancelar.setOffset(0, 4)
        sombra_cancelar.setColor(QColor(153, 27, 27, 60))
        self.btn_cancelar.setGraphicsEffect(sombra_cancelar)

        self.btn_avanzar = QPushButton("  Avanzar")
        self.btn_avanzar.setFixedSize(200, 56)
        self.btn_avanzar.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        self.btn_avanzar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_avanzar.clicked.connect(self.senal_avanzar_cobro.emit)

        self.btn_avanzar.setIcon(crear_icono_flecha(22, QColor(255, 255, 255)))
        self.btn_avanzar.setIconSize(QSize(22, 22))
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
                background-color: #1E40AF;
            }}
            QPushButton:disabled {{
                background-color: #F1F5F9;
                color: #94A3B8;
                border: 1px solid #E2E8F0;
            }}
        """)

        sombra_avanzar = QGraphicsDropShadowEffect()
        sombra_avanzar.setBlurRadius(18)
        sombra_avanzar.setOffset(0, 4)
        sombra_avanzar.setColor(QColor(30, 58, 138, 40))
        self.btn_avanzar.setGraphicsEffect(sombra_avanzar)

        layout.addWidget(self.btn_cancelar, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addStretch()
        layout.addWidget(self.btn_avanzar, alignment=Qt.AlignmentFlag.AlignRight)

        return contenedor

    # ──────────────────────────────────────────────
    #  Autenticación PIN para acceso a Admin
    # ──────────────────────────────────────────────

    def _on_admin_clicked(self):
        """Flujo de autenticación al presionar el botón Admin.

        - Si no hay PIN configurado → DialogoConfigurarPIN (A-001).
        - Si hay PIN configurado   → DialogoPIN (A-002).
        - Solo emite senal_ir_admin si la autenticación es exitosa.
        """
        if not self.gestor_autenticacion:
            # Sin gestor, acceso directo (modo desarrollo)
            self.senal_ir_admin.emit()
            return

        if not self.gestor_autenticacion.pin_configurado():
            # ── Primer acceso: configurar PIN ──
            dialogo = DialogoConfigurarPIN(self)
            if dialogo.exec() == QDialog.DialogCode.Accepted:
                pin = dialogo.obtener_pin()
                exito = self.gestor_autenticacion.configurar_pin(pin)
                if exito:
                    # PIN configurado → acceso concedido
                    self.senal_ir_admin.emit()
        else:
            # ── Acceso subsecuente: ingresar PIN ──
            dialogo = DialogoPIN(self.gestor_autenticacion, self)
            if dialogo.exec() == QDialog.DialogCode.Accepted:
                self.senal_ir_admin.emit()

    # ──────────────────────────────────────────────
    #  Lógica de Búsqueda y Resultados Flotantes
    # ──────────────────────────────────────────────

    def _on_busqueda_changed(self, texto):
        if not self.gestor_productos:
            return
            
        texto_limpio = texto.strip()
        if not texto_limpio:
            self.panel_resultados.hide()
            return
            
        productos = self.gestor_productos.buscar_producto(texto_limpio)
        self.panel_resultados.clear()
        
        if not productos:
            item = QListWidgetItem("No se encontraron productos")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.panel_resultados.addItem(item)
        else:
            for prod in productos:
                es_gr = prod['tipo_venta'] == 'granel'
                sufijo_p = "/Kg" if es_gr else ""
                sufijo_cant = "Kg" if es_gr else "pz"
                
                cant_str = f"({prod['stock_actual']:.1f} {sufijo_cant})" if es_gr else f"({int(prod['stock_actual'])} {sufijo_cant})"
                if prod['stock_actual'] <= 0:
                    cant_str = "(AGOTADO)"
                
                texto_item = f"{prod['nombre']}   ·   ${prod['precio_venta']:.2f}{sufijo_p}   {cant_str}"
                
                item = QListWidgetItem(texto_item)
                item.setData(Qt.ItemDataRole.UserRole, prod)
                
                if prod['stock_actual'] <= 0:
                    item.setForeground(QColor("#EF4444"))
                
                self.panel_resultados.addItem(item)
                
        self.panel_resultados.posicionar_bajo_busqueda(self.barra_busqueda)
        self.panel_resultados.setCurrentRow(-1)
        self.panel_resultados.show()

    def _on_barra_key_press(self, event):
        if self.panel_resultados.isVisible() and event.key() == Qt.Key.Key_Down:
            self.panel_resultados.setFocus()
            self.panel_resultados.setCurrentRow(0)
        else:
            QLineEdit.keyPressEvent(self.barra_busqueda, event)

    def _on_item_resultado_clicked(self, item):
        prod = item.data(Qt.ItemDataRole.UserRole)
        if not prod:
            return
            
        self.gestor_carrito.agregar_producto(prod, 1.0)
        self.panel_resultados.hide()
        self.barra_busqueda.clear()
        self._actualizar_tabla()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'panel_resultados') and self.panel_resultados.isVisible():
            self.panel_resultados.posicionar_bajo_busqueda(self.barra_busqueda)

    # ──────────────────────────────────────────────
    #  Lógica de Carrito de Compras (QTableWidget)
    # ──────────────────────────────────────────────

    def _actualizar_tabla(self):
        if not self.gestor_carrito:
            self.btn_avanzar.setEnabled(False)
            self.marco_tabla.hide()
            self.panel_total.hide()
            return
            
        fila_sel = self.tabla_carrito.currentRow()
        self.tabla_carrito.setRowCount(0)
        items = self.gestor_carrito.obtener_items()
        
        # Ocultar o mostrar tabla y total según si hay productos en el carrito
        vacio = self.gestor_carrito.esta_vacio()
        self.marco_tabla.setVisible(not vacio)
        self.panel_total.setVisible(not vacio)
        
        for idx, item in enumerate(items):
            self.tabla_carrito.insertRow(idx)
            prod = item.producto
            es_gr = prod['tipo_venta'] == 'granel'
            sufijo_p = "/Kg" if es_gr else ""
            
            # Column 0: Nombre
            nombre_item = QTableWidgetItem(prod['nombre'])
            nombre_item.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
            nombre_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.tabla_carrito.setItem(idx, 0, nombre_item)
            
            # Column 1: Cantidad (SelectorCantidadTabla)
            selector = SelectorCantidadTabla(item.cantidad, es_gr)
            selector.senal_cantidad_cambiada.connect(
                lambda cant, p_id=prod['id_producto']: self._on_cantidad_cambiada(p_id, cant)
            )
            self.tabla_carrito.setCellWidget(idx, 1, selector)
            
            # Column 2: Precio de venta
            precio_item = QTableWidgetItem(f"${prod['precio_venta']:.2f}{sufijo_p}")
            precio_item.setFont(QFont("Segoe UI", 12))
            precio_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            precio_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.tabla_carrito.setItem(idx, 2, precio_item)
            
            # Column 3: Subtotal
            subtotal_item = QTableWidgetItem(f"${item.subtotal:.2f}")
            subtotal_item.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
            subtotal_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            subtotal_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.tabla_carrito.setItem(idx, 3, subtotal_item)
            
            # Column 4: Acción (BotonEliminarTabla)
            btn_eliminar = BotonEliminarTabla()
            btn_eliminar.clicked.connect(
                lambda checked, p_id=prod['id_producto']: self._on_eliminar_clicked(p_id)
            )
            
            # Centrar botón en celda
            contenedor = QWidget()
            contenedor.setStyleSheet("background: transparent;")
            layout_btn = QHBoxLayout(contenedor)
            layout_btn.setContentsMargins(0, 0, 0, 0)
            layout_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout_btn.addWidget(btn_eliminar)
            self.tabla_carrito.setCellWidget(idx, 4, contenedor)
            
        if not vacio:
            if fila_sel < 0 or fila_sel >= self.tabla_carrito.rowCount():
                fila_sel = self.tabla_carrito.rowCount() - 1
            self.tabla_carrito.setCurrentCell(fila_sel, 0)
            
        total = self.gestor_carrito.calcular_total()
        if vacio:
            self.lbl_total.setText("Total $-----")
        else:
            self.lbl_total.setText(f"Total ${total:.2f}")
        
        self.btn_avanzar.setEnabled(not vacio)
        self._actualizar_alertas_stock()

    def _actualizar_alertas_stock(self):
        row = self.tabla_carrito.currentRow()
        if row < 0:
            if self.gestor_carrito and not self.gestor_carrito.esta_vacio():
                row = len(self.gestor_carrito.obtener_items()) - 1
            else:
                self.lbl_alerta_stock.setVisible(False)
                return
                
        if not self.gestor_carrito:
            self.lbl_alerta_stock.setVisible(False)
            return
            
        items = self.gestor_carrito.obtener_items()
        if row >= len(items):
            self.lbl_alerta_stock.setVisible(False)
            return
            
        item = items[row]
        prod = item.producto
        es_gr = prod['tipo_venta'] == 'granel'
        
        stock_inicial = prod.get('stock_actual', 0.0)
        cantidad_carrito = item.cantidad
        stock_restante = round(stock_inicial - cantidad_carrito, 2)
        stock_minimo = prod.get('stock_minimo', 0.0)
        
        if stock_restante <= 0:
            self.lbl_alerta_stock.setText(f"{prod['nombre']}\nAgotado")
            self.lbl_alerta_stock.setVisible(True)
        elif stock_restante < stock_minimo:
            stock_str = f"{stock_restante:.2f}" if es_gr else f"{int(stock_restante)}"
            self.lbl_alerta_stock.setText(
                f"El stock en tienda actual de\n{prod['nombre']}\nes: {stock_str}"
            )
            self.lbl_alerta_stock.setVisible(True)
        else:
            self.lbl_alerta_stock.setVisible(False)

    def _on_cantidad_cambiada(self, id_producto, nueva_cantidad):
        if nueva_cantidad <= 0:
            QTimer.singleShot(0, lambda: self._confirmar_y_eliminar(id_producto))
            return

        self.gestor_carrito.modificar_cantidad(id_producto, nueva_cantidad)
        for r in range(self.tabla_carrito.rowCount()):
            item = self.gestor_carrito.obtener_items()[r]
            if item.producto['id_producto'] == id_producto:
                self.tabla_carrito.item(r, 3).setText(f"${item.subtotal:.2f}")
                selector = self.tabla_carrito.cellWidget(r, 1)
                if isinstance(selector, SelectorCantidadTabla):
                    selector.cantidad = nueva_cantidad
                    selector.txt_cantidad.setText(selector._formatear_cantidad(nueva_cantidad))
                    selector._actualizar_estados_botones()
                break
            
        total = self.gestor_carrito.calcular_total()
        vacio = self.gestor_carrito.esta_vacio()
        self.marco_tabla.setVisible(not vacio)
        self.panel_total.setVisible(not vacio)
        if vacio:
            self.lbl_total.setText("Total $-----")
        else:
            self.lbl_total.setText(f"Total ${total:.2f}")
        self._actualizar_alertas_stock()

    def _on_eliminar_clicked(self, id_producto):
        self._confirmar_y_eliminar(id_producto)

    def _confirmar_y_eliminar(self, id_producto):
        items = self.gestor_carrito.obtener_items()
        item = next((it for it in items if it.producto['id_producto'] == id_producto), None)
        nombre = item.producto['nombre'] if item else "el producto"
        diag = DialogoConfirmacion(nombre, self)
        if diag.exec() == QDialog.DialogCode.Accepted:
            self.gestor_carrito.eliminar_item(id_producto)
        self._actualizar_tabla()
        
        # Devolver foco al carrito o a la barra de búsqueda si quedó vacío
        if self.gestor_carrito.esta_vacio():
            self.barra_busqueda.setFocus()
            self.barra_busqueda.selectAll()
        else:
            self.tabla_carrito.setFocus()

    def _obtener_id_producto_fila(self, row: int):
        if not self.gestor_carrito:
            return None
        items = self.gestor_carrito.obtener_items()
        if 0 <= row < len(items):
            return items[row].producto['id_producto']
        return None

    def _modificar_cantidad_por_teclado(self, id_producto, aumentar: bool):
        if not self.gestor_carrito:
            return
        items = self.gestor_carrito.obtener_items()
        item = next((it for it in items if it.producto['id_producto'] == id_producto), None)
        if not item:
            return
        es_gr = item.producto['tipo_venta'] == 'granel'
        paso = 0.1 if es_gr else 1.0
        min_lim = 0.1 if es_gr else 1.0
        
        if aumentar:
            nueva = round(item.cantidad + paso, 2)
        else:
            nueva = round(item.cantidad - paso, 2)
            
        if nueva < min_lim:
            QTimer.singleShot(0, lambda: self._confirmar_y_eliminar(id_producto))
        else:
            self._on_cantidad_cambiada(id_producto, nueva)

    def eventFilter(self, watched, event):
        from PyQt6.QtCore import QEvent
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            
            # --- BARRA DE BÚSQUEDA ---
            if watched == self.barra_busqueda:
                if key == Qt.Key.Key_Down:
                    if self.panel_resultados.isVisible() and self.panel_resultados.count() > 0:
                        current = self.panel_resultados.currentRow()
                        next_row = current + 1
                        if next_row < self.panel_resultados.count():
                            self.panel_resultados.setCurrentRow(next_row)
                        return True
                    elif not self.gestor_carrito.esta_vacio():
                        self.tabla_carrito.setFocus()
                        self.tabla_carrito.selectRow(0)
                        return True
                elif key == Qt.Key.Key_Up:
                    if self.panel_resultados.isVisible() and self.panel_resultados.count() > 0:
                        current = self.panel_resultados.currentRow()
                        if current > 0:
                            self.panel_resultados.setCurrentRow(current - 1)
                        return True
                elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    if self.panel_resultados.isVisible() and self.panel_resultados.count() > 0:
                        row = self.panel_resultados.currentRow()
                        if row < 0:
                            row = 0
                        item = self.panel_resultados.item(row)
                        if item:
                            self._on_item_resultado_clicked(item)
                            return True
            
            # --- PANEL DE RESULTADOS FLOTANTE ---
            elif watched == self.panel_resultados:
                if key == Qt.Key.Key_Up:
                    if self.panel_resultados.currentRow() == 0:
                        self.barra_busqueda.setFocus()
                        return True
                elif key == Qt.Key.Key_Escape:
                    self.panel_resultados.hide()
                    self.barra_busqueda.setFocus()
                    return True
            
            # --- TABLA DEL CARRITO ---
            elif watched == self.tabla_carrito:
                if key == Qt.Key.Key_Up:
                    if self.tabla_carrito.currentRow() == 0:
                        self.barra_busqueda.setFocus()
                        self.barra_busqueda.selectAll()
                        return True
                elif key == Qt.Key.Key_Down:
                    if self.tabla_carrito.currentRow() == self.tabla_carrito.rowCount() - 1:
                        self.btn_cancelar.setFocus()
                        return True
                elif key in (Qt.Key.Key_Right, Qt.Key.Key_Plus, Qt.Key.Key_Equal):
                    row = self.tabla_carrito.currentRow()
                    if row >= 0:
                        id_prod = self._obtener_id_producto_fila(row)
                        if id_prod:
                            self._modificar_cantidad_por_teclado(id_prod, aumentar=True)
                            return True
                elif key in (Qt.Key.Key_Left, Qt.Key.Key_Minus):
                    row = self.tabla_carrito.currentRow()
                    if row >= 0:
                        id_prod = self._obtener_id_producto_fila(row)
                        if id_prod:
                            self._modificar_cantidad_por_teclado(id_prod, aumentar=False)
                            return True
                elif key in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
                    row = self.tabla_carrito.currentRow()
                    if row >= 0:
                        id_prod = self._obtener_id_producto_fila(row)
                        if id_prod:
                            self._on_eliminar_clicked(id_prod)
                            return True
                elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    # Si el foco está en un control de edición dentro de la tabla, no avanzar al cobro
                    from PyQt6.QtWidgets import QApplication
                    foco = QApplication.focusWidget()
                    if foco and (self.tabla_carrito.isAncestorOf(foco) or isinstance(foco, QLineEdit)):
                        return True  # Consumir el evento para que la tabla no avance al cobro
                    
                    if self.btn_avanzar.isEnabled():
                        self.senal_avanzar_cobro.emit()
                        return True
            
            # --- BOTONES DE LA BARRA INFERIOR ---
            elif watched == self.btn_cancelar:
                if key == Qt.Key.Key_Up:
                    if not self.gestor_carrito.esta_vacio():
                        self.tabla_carrito.setFocus()
                        self.tabla_carrito.selectRow(self.tabla_carrito.rowCount() - 1)
                        return True
                    else:
                        self.barra_busqueda.setFocus()
                        return True
                elif key == Qt.Key.Key_Right:
                    self.btn_avanzar.setFocus()
                    return True
                elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    self._on_cancelar_venta()
                    return True
                    
            elif watched == self.btn_avanzar:
                if key == Qt.Key.Key_Up:
                    if not self.gestor_carrito.esta_vacio():
                        self.tabla_carrito.setFocus()
                        self.tabla_carrito.selectRow(self.tabla_carrito.rowCount() - 1)
                        return True
                    else:
                        self.barra_busqueda.setFocus()
                        return True
                elif key == Qt.Key.Key_Left:
                    self.btn_cancelar.setFocus()
                    return True
                elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    if self.btn_avanzar.isEnabled():
                        self.senal_avanzar_cobro.emit()
                        return True
                        
        return super().eventFilter(watched, event)

    def _on_avanzar_clicked(self):
        if not self.gestor_carrito or self.gestor_carrito.esta_vacio():
            return
            
        # 1. Obtener total
        total = self.gestor_carrito.calcular_total()
        
        # 2. Mostrar Pantalla de Cobro (monto recibido y cambio)
        from iu.cajero.pantalla_cobro import PantallaCobro
        dlg_cobro = PantallaCobro(self.gestor_carrito, self.gestor_ventas, self)
        dlg_cobro.cargar_total(total)
        
        # Conectar señales al flujo del diálogo modal
        dlg_cobro.cobro_confirmado.connect(lambda m, c: dlg_cobro.accept())
        dlg_cobro.regresar_carrito.connect(dlg_cobro.reject)
        dlg_cobro.venta_cancelada.connect(dlg_cobro.reject)
        
        if dlg_cobro.exec() != QDialog.DialogCode.Accepted:
            # Si se rechazó (ej. al cancelar la venta) pero el carrito está vacío,
            # actualizamos la interfaz del cajero para reflejarlo
            if self.gestor_carrito.esta_vacio():
                self._actualizar_tabla()
            return
            
        # 3. Obtener el resultado de la venta ya procesada y confirmada
        resultado = getattr(dlg_cobro, 'resultado_venta', None)
        if not resultado:
            # Fallback de seguridad por si no se guardó el resultado en el diálogo
            monto_recibido = float(dlg_cobro._inp_monto.text())
            try:
                resultado = self.gestor_ventas.confirmar_venta(monto_recibido)
            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Error de Venta", f"No se pudo completar la venta: {e}")
                return
            
        # 4. Preguntar si requiere ticket
        from iu.cajero.pantalla_ticket import DialogoRequiereTicket, PantallaTicket
        dlg_pregunta = DialogoRequiereTicket(self)
        if dlg_pregunta.exec() == QDialog.DialogCode.Accepted:
            # Mostrar ticket completo con desglose
            dlg_ticket = PantallaTicket(resultado, self)
            dlg_ticket.exec()
            
        # 5. Si hay alertas de stock, mostrarlas en un modal informativo
        if resultado.get('alertas_stock'):
            from PyQt6.QtWidgets import QMessageBox
            alertas_txt = ""
            for alerta in resultado['alertas_stock']:
                if alerta.get('agotado'):
                    alertas_txt += f"• {alerta['nombre']}: Agotado\n"
                else:
                    alertas_txt += f"• {alerta['nombre']}: Stock bajo ({alerta['stock_actual']:.1f})\n"
            
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Alertas de Stock")
            msg.setText("Se han generado alertas de inventario:")
            msg.setInformativeText(alertas_txt)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                    font-family: "Segoe UI";
                }
                QLabel {
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #F1F5F9;
                    color: #475569;
                    border: 1px solid #CBD5E1;
                    border-radius: 8px;
                    padding: 6px 14px;
                    font-weight: bold;
                }
            """)
            msg.exec()
            
        # 6. Actualizar la tabla del carrito (estará vacío)
        self._actualizar_tabla()

    def _on_cancelar_venta(self):
        if not self.gestor_carrito or self.gestor_carrito.esta_vacio():
            self.senal_cancelar_venta.emit()
            return
            
        diag = DialogoEliminarCarrito(self)
        if diag.exec() == QDialog.DialogCode.Accepted:
            self.gestor_carrito.vaciar_carrito()
            self._actualizar_tabla()
            self.senal_cancelar_venta.emit()


# ══════════════════════════════════════════════════
#  Ejecución standalone con Base de Datos real
# ══════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    import os
    from PyQt6.QtWidgets import QApplication
    from datos.base_datos import BaseDatos
    from logica.gestor_productos import GestorProductos
    from logica.gestor_carrito import GestorCarrito
    from logica.gestor_ventas import GestorVentas

    app = QApplication(sys.argv)

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Conectar a la base de datos local
    ruta_db = "prueba_punto_venta.db"
    db = BaseDatos(ruta_db)
    db.inicializar_tablas()

    # Si está vacía, poblamos con algunos productos de prueba
    if not db.obtener_catalogo():
        db.insertar_producto("LECHE ENTERA ALPURA 1L", "pieza", 18.0, 22.0, 5.0, 15.0)
        db.insertar_producto("DONAS ESPOLVOREADAS BIMBO", "pieza", 15.0, 19.5, 2.0, 3.0)
        db.insertar_producto("CROQUETAS PARA PERRO GANADOR A GRANEL", "granel", 45.0, 60.0, 10.0, 20.0)
        db.insertar_producto("QUESO PANELA A GRANEL", "granel", 80.0, 110.0, 3.0, 0.0)
        db.insertar_producto("COCA COLA 3L", "pieza", 30.0, 38.0, 4.0, 8.0)

    gestor_productos = GestorProductos(db)
    gestor_carrito = GestorCarrito()
    gestor_ventas = GestorVentas(db, gestor_carrito)

    ventana = PantallaCajero(
        gestor_productos=gestor_productos,
        gestor_carrito=gestor_carrito,
        gestor_ventas=gestor_ventas
    )
    ventana.setWindowTitle("Punto de Venta — Cajero")
    ventana.resize(1280, 850)
    ventana.show()

    sys.exit(app.exec())
