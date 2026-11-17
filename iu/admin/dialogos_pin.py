# iu/admin/dialogos_pin.py
"""
Diálogos de autenticación por PIN — Fase 4 (Admin).

Componentes:
- DialogoConfigurarPIN (A-001 / A-003): Primer acceso, crear PIN de 6 dígitos.
- DialogoPIN           (A-002 / A-003): Ingresar PIN existente, intentos ilimitados.

Restricciones de negocio:
- El PIN, una vez configurado, NO puede recuperarse ni modificarse.
- Si el administrador olvida el PIN, la única forma de recuperar acceso
  es reinstalando el software desde cero.

Referencia SRS:
- A-001: Primer uso → configurar PIN de 6 dígitos numéricos.
- A-002: Accesos subsecuentes → solicitar PIN existente.
- A-003: Solo dígitos, máx 6 caracteres, enmascaramiento con asteriscos.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QWidget,
    QLineEdit, QPushButton, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import (
    QFont, QColor, QIntValidator
)


# ══════════════════════════════════════════════════
#  Constantes
# ══════════════════════════════════════════════════

_PIN_LEN = 6


# ══════════════════════════════════════════════════
#  Etiqueta de error con animación de sacudida
# ══════════════════════════════════════════════════

class _LabelError(QLabel):
    """Etiqueta roja que aparece con una micro-animación de shake."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Segoe UI", 10))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(24)
        self.setStyleSheet("""
            QLabel {
                color: #DC2626;
                background: transparent;
            }
        """)
        self.hide()

    def mostrar_error(self, mensaje: str):
        self.setText(mensaje)
        self.show()
        self._animar_shake()

    def _animar_shake(self):
        geo = self.geometry()
        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setDuration(350)
        self._anim.setKeyValueAt(0.0, geo)
        self._anim.setKeyValueAt(0.15, QRect(geo.x() - 6, geo.y(), geo.width(), geo.height()))
        self._anim.setKeyValueAt(0.30, QRect(geo.x() + 6, geo.y(), geo.width(), geo.height()))
        self._anim.setKeyValueAt(0.50, QRect(geo.x() - 4, geo.y(), geo.width(), geo.height()))
        self._anim.setKeyValueAt(0.70, QRect(geo.x() + 4, geo.y(), geo.width(), geo.height()))
        self._anim.setKeyValueAt(1.0, geo)
        self._anim.setEasingCurve(QEasingCurve.Type.OutElastic)
        self._anim.start()

    def ocultar(self):
        self.hide()
        self.setText("")


# ══════════════════════════════════════════════════
#  Campo de PIN reutilizable
# ══════════════════════════════════════════════════

def _crear_campo_pin() -> QLineEdit:
    """QLineEdit: solo dígitos, máx 6, asteriscos, centrado."""
    campo = QLineEdit()
    campo.setEchoMode(QLineEdit.EchoMode.Password)
    campo.setMaxLength(_PIN_LEN)
    campo.setAlignment(Qt.AlignmentFlag.AlignCenter)
    campo.setFont(QFont("Segoe UI", 18))
    campo.setFixedHeight(44)
    campo.setFixedWidth(260)

    validador = QIntValidator(0, 999999, campo)
    campo.setValidator(validador)

    campo.setStyleSheet("""
        QLineEdit {
            background-color: #F1F1F1;
            border: none;
            border-bottom: 2px solid #999999;
            border-radius: 4px;
            padding: 4px 16px;
            color: #1E293B;
            letter-spacing: 10px;
            font-size: 20px;
            lineedit-password-character: 42;
        }
        QLineEdit:focus {
            border-bottom: 2px solid #2563EB;
            background-color: #E8E8E8;
        }
    """)
    return campo


# ══════════════════════════════════════════════════
#  DialogoConfigurarPIN  (A-001 / A-003)
# ══════════════════════════════════════════════════

class DialogoConfigurarPIN(QDialog):
    """Modal para configurar el PIN de 6 dígitos en el primer acceso.

    Diseño (fiel al wireframe):
    - Tarjeta centrada con borde fino.
    - Título: "Configuración de PIN del administrador"
    - Advertencia: "Una vez configurado, el pin no puede modificarse ni recuperarse"
    - Un campo de PIN con asteriscos.
    - Texto auxiliar: "Ingrese un PIN de 6 dígitos, únicamente numéricos"

    Restricción de negocio:
    - El PIN NO puede recuperarse ni modificarse una vez configurado.
    - Si se olvida, la única opción es reinstalar el software.

    Uso:
        dialogo = DialogoConfigurarPIN(parent)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            pin = dialogo.obtener_pin()
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(420, 320)
        self._pin_resultado = ""
        self._setup_ui()

    # ── Arrastre ──

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, "_drag_pos"):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    # ── UI ──

    def _setup_ui(self):
        layout_ext = QVBoxLayout(self)
        layout_ext.setContentsMargins(0, 0, 0, 0)

        # ── Tarjeta principal (borde fino, esquinas suaves) ──
        tarjeta = QFrame()
        tarjeta.setObjectName("TarjetaPIN")
        tarjeta.setStyleSheet("""
            QFrame#TarjetaPIN {
                background-color: #FFFFFF;
                border: 1.5px solid #BBBBBB;
                border-radius: 8px;
            }
        """)
        sombra = QGraphicsDropShadowEffect(tarjeta)
        sombra.setBlurRadius(30)
        sombra.setOffset(0, 6)
        sombra.setColor(QColor(0, 0, 0, 40))
        tarjeta.setGraphicsEffect(sombra)
        layout_ext.addWidget(tarjeta)

        layout = QVBoxLayout(tarjeta)
        layout.setContentsMargins(36, 32, 36, 28)
        layout.setSpacing(0)

        # ── Título ──
        lbl_titulo = QLabel("Configuración de PIN\ndel administrador")
        lbl_titulo.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet("color: #1A1A1A; background: transparent;")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setWordWrap(True)
        layout.addWidget(lbl_titulo)

        layout.addSpacing(10)

        # ── Advertencia (no recuperable) ──
        lbl_advertencia = QLabel(
            "Una vez configurado, el PIN no puede\n"
            "modificarse ni recuperarse"
        )
        lbl_advertencia.setFont(QFont("Segoe UI", 10))
        lbl_advertencia.setStyleSheet("color: #666666; background: transparent;")
        lbl_advertencia.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_advertencia.setWordWrap(True)
        layout.addWidget(lbl_advertencia)

        layout.addSpacing(20)

        # ── Campo de PIN (centrado) ──
        contenedor_campo = QHBoxLayout()
        contenedor_campo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.campo_pin = _crear_campo_pin()
        self.campo_pin.textChanged.connect(self._on_texto_cambiado)
        contenedor_campo.addWidget(self.campo_pin)
        layout.addLayout(contenedor_campo)

        layout.addSpacing(14)

        # ── Texto auxiliar ──
        lbl_ayuda = QLabel("Ingrese un PIN de 6 dígitos,\núnicamente numéricos")
        lbl_ayuda.setFont(QFont("Segoe UI", 9))
        lbl_ayuda.setStyleSheet("color: #3B82F6; background: transparent;")
        lbl_ayuda.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_ayuda.setWordWrap(True)
        layout.addWidget(lbl_ayuda)

        # ── Error ──
        self.lbl_error = _LabelError()
        layout.addWidget(self.lbl_error)

        layout.addSpacing(16)

        # ── Botones ──
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_guardar = QPushButton("Confirmar")
        self.btn_guardar.setFixedSize(120, 38)
        self.btn_guardar.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        self.btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guardar.setEnabled(False)
        self.btn_guardar.clicked.connect(self._on_guardar)
        self.btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
            QPushButton:pressed {
                background-color: #1E40AF;
            }
            QPushButton:disabled {
                background-color: #CBD5E1;
                color: #94A3B8;
            }
        """)

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setFixedSize(120, 38)
        self.btn_cancelar.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        self.btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancelar.clicked.connect(self.reject)
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
                color: #1E293B;
            }
            QPushButton:pressed {
                background-color: #CBD5E1;
            }
        """)

        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(self.btn_cancelar)
        layout.addLayout(btn_layout)

        # Foco inicial
        self.campo_pin.setFocus()

    # ── Lógica ──

    def _on_texto_cambiado(self):
        self.btn_guardar.setEnabled(len(self.campo_pin.text()) >= 1)
        if self.lbl_error.isVisible():
            self.lbl_error.ocultar()

    def _on_guardar(self):
        pin = self.campo_pin.text()
        if len(pin) < _PIN_LEN:
            self.lbl_error.mostrar_error("El PIN debe ser de 6 cifras")
            self.campo_pin.setFocus()
            return
        self._pin_resultado = pin
        self.accept()

    def obtener_pin(self) -> str:
        """Retorna el PIN configurado (solo válido tras Accepted)."""
        return self._pin_resultado

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.btn_guardar.isEnabled():
                self._on_guardar()
        else:
            super().keyPressEvent(event)


# ══════════════════════════════════════════════════
#  DialogoPIN  (A-002 / A-003)
#  Acceso subsecuente — diseño fiel al prototipo
# ══════════════════════════════════════════════════

class DialogoPIN(QDialog):
    """Modal para ingresar el PIN de administrador.

    Diseño (fiel al wireframe):
    - Tarjeta centrada con borde fino.
    - Título: "Ingrese su PIN"
    - Un campo de PIN con asteriscos.
    - Intentos ilimitados, error si < 6 dígitos o PIN incorrecto.

    Uso:
        dialogo = DialogoPIN(gestor_auth, parent)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            # Autenticación exitosa
    """

    def __init__(self, gestor_autenticacion=None, parent=None):
        super().__init__(parent)
        self.gestor_auth = gestor_autenticacion
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(380, 250)
        self._setup_ui()

    # ── Arrastre ──

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, "_drag_pos"):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    # ── UI ──

    def _setup_ui(self):
        layout_ext = QVBoxLayout(self)
        layout_ext.setContentsMargins(0, 0, 0, 0)

        # ── Tarjeta principal ──
        tarjeta = QFrame()
        tarjeta.setObjectName("TarjetaPIN")
        tarjeta.setStyleSheet("""
            QFrame#TarjetaPIN {
                background-color: #FFFFFF;
                border: 1.5px solid #BBBBBB;
                border-radius: 8px;
            }
        """)
        sombra = QGraphicsDropShadowEffect(tarjeta)
        sombra.setBlurRadius(30)
        sombra.setOffset(0, 6)
        sombra.setColor(QColor(0, 0, 0, 40))
        tarjeta.setGraphicsEffect(sombra)
        layout_ext.addWidget(tarjeta)

        layout = QVBoxLayout(tarjeta)
        layout.setContentsMargins(36, 28, 36, 24)
        layout.setSpacing(0)

        # ── Título ──
        lbl_titulo = QLabel("Ingrese su PIN")
        lbl_titulo.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet("color: #1A1A1A; background: transparent;")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_titulo)

        layout.addSpacing(20)

        # ── Campo de PIN (centrado) ──
        contenedor_campo = QHBoxLayout()
        contenedor_campo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.campo_pin = _crear_campo_pin()
        self.campo_pin.textChanged.connect(self._on_texto_cambiado)
        contenedor_campo.addWidget(self.campo_pin)
        layout.addLayout(contenedor_campo)

        # ── Error ──
        layout.addSpacing(8)
        self.lbl_error = _LabelError()
        layout.addWidget(self.lbl_error)

        layout.addSpacing(16)

        # ── Botones ──
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_ingresar = QPushButton("Ingresar")
        self.btn_ingresar.setFixedSize(120, 38)
        self.btn_ingresar.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        self.btn_ingresar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ingresar.setEnabled(False)
        self.btn_ingresar.clicked.connect(self._on_ingresar)
        self.btn_ingresar.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
            QPushButton:pressed {
                background-color: #1E40AF;
            }
            QPushButton:disabled {
                background-color: #CBD5E1;
                color: #94A3B8;
            }
        """)

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setFixedSize(120, 38)
        self.btn_cancelar.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        self.btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancelar.clicked.connect(self.reject)
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
                color: #1E293B;
            }
            QPushButton:pressed {
                background-color: #CBD5E1;
            }
        """)

        btn_layout.addWidget(self.btn_ingresar)
        btn_layout.addWidget(self.btn_cancelar)
        layout.addLayout(btn_layout)

        # Foco inicial
        self.campo_pin.setFocus()

    # ── Lógica ──

    def _on_texto_cambiado(self):
        self.btn_ingresar.setEnabled(len(self.campo_pin.text()) >= 1)
        if self.lbl_error.isVisible():
            self.lbl_error.ocultar()

    def _on_ingresar(self):
        pin = self.campo_pin.text()

        if len(pin) < _PIN_LEN:
            self.lbl_error.mostrar_error("El PIN debe ser de 6 cifras")
            self.campo_pin.setFocus()
            return

        # Verificar contra hash almacenado
        if self.gestor_auth and not self.gestor_auth.verificar_pin(pin):
            self.lbl_error.mostrar_error("PIN incorrecto, intente de nuevo")
            self.campo_pin.clear()
            self.campo_pin.setFocus()
            return

        self.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.btn_ingresar.isEnabled():
                self._on_ingresar()
        else:
            super().keyPressEvent(event)

# ══════════════════════════════════════════════════ #
#  CÓDIGO DE PRUEBA INTEGRADO (STANDALONE)           #
# ══════════════════════════════════════════════════ #
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    dialogo = DialogoPIN()
    dialogo.exec()

    sys.exit()