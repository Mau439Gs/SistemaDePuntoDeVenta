# iu/cajero/pantalla_cobro.py
"""
Módulo de Cobro — Interfaz para ingresar el pago en efectivo y calcular el cambio.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QFrame, QWidget
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QDoubleValidator


class PantallaCobro(QDialog):
    """Diálogo modal de Cobro.
    
    Campos en disposición vertical: Total a Pagar, Monto Recibido, Cambio.
    """
    
    def __init__(self, total_pagar: float, parent=None):
        super().__init__(parent)
        self.total_pagar = total_pagar
        self.monto_recibido = 0.0
        self.cambio = 0.0
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(500, 440)
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
        self.contenedor.setObjectName("ContenedorCobro")
        self.contenedor.setStyleSheet("""
            QFrame#ContenedorCobro {
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
        cabecera.setFixedHeight(60)
        cabecera.setStyleSheet("""
            QFrame#Cabecera {
                background-color: #2563EB;
                border-top-left-radius: 14px;
                border-top-right-radius: 14px;
            }
        """)
        layout_cabecera = QHBoxLayout(cabecera)
        layout_cabecera.setContentsMargins(0, 0, 0, 0)
        
        lbl_titulo = QLabel("Cobro de Venta", cabecera)
        lbl_titulo.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet("color: white; border: none;")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_cabecera.addWidget(lbl_titulo)
        layout_body.addWidget(cabecera)
        
        # Cuerpo del diálogo (Campos verticales)
        cuerpo = QWidget()
        layout_cuerpo_interno = QVBoxLayout(cuerpo)
        layout_cuerpo_interno.setContentsMargins(32, 24, 32, 24)
        layout_cuerpo_interno.setSpacing(14)
        
        # 1. Total a pagar (Solo lectura)
        lbl_total_titulo = QLabel("TOTAL A PAGAR:", cuerpo)
        lbl_total_titulo.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        lbl_total_titulo.setStyleSheet("color: #64748B; border: none;")
        
        self.lbl_total_valor = QLabel(f"$ {self.total_pagar:.2f}", cuerpo)
        self.lbl_total_valor.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self.lbl_total_valor.setStyleSheet("color: #0F172A; background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 6px;")
        self.lbl_total_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout_cuerpo_interno.addWidget(lbl_total_titulo)
        layout_cuerpo_interno.addWidget(self.lbl_total_valor)
        
        # 2. Monto recibido (Editable)
        lbl_recibido_titulo = QLabel("MONTO RECIBIDO:", cuerpo)
        lbl_recibido_titulo.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        lbl_recibido_titulo.setStyleSheet("color: #64748B; border: none;")
        
        self.txt_recibido = QLineEdit(cuerpo)
        self.txt_recibido.setPlaceholderText("Efectivo")
        self.txt_recibido.setFont(QFont("Segoe UI", 16))
        self.txt_recibido.setFixedSize(436, 44)
        self.txt_recibido.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.txt_recibido.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1.5px solid #CBD5E1;
                border-radius: 8px;
                color: #0F172A;
            }
            QLineEdit:focus {
                border: 2px solid #2563EB;
            }
        """)
        validador = QDoubleValidator(0.0, 99999.99, 2, self)
        validador.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.txt_recibido.setValidator(validador)
        self.txt_recibido.textChanged.connect(self._on_recibido_changed)
        
        layout_cuerpo_interno.addWidget(lbl_recibido_titulo)
        layout_cuerpo_interno.addWidget(self.txt_recibido)
        
        # 3. Cambio (Solo lectura)
        lbl_cambio_titulo = QLabel("CAMBIO A DEVOLVER:", cuerpo)
        lbl_cambio_titulo.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        lbl_cambio_titulo.setStyleSheet("color: #64748B; border: none;")
        
        self.lbl_cambio_valor = QLabel("$ 0.00", cuerpo)
        self.lbl_cambio_valor.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self.lbl_cambio_valor.setStyleSheet("color: #16A34A; background-color: #F0FDF4; border: 1px solid #DCFCE7; border-radius: 8px; padding: 6px;")
        self.lbl_cambio_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout_cuerpo_interno.addWidget(lbl_cambio_titulo)
        layout_cuerpo_interno.addWidget(self.lbl_cambio_valor)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        btn_layout.setContentsMargins(0, 10, 0, 0)
        
        self.btn_cancelar = QPushButton("Regresar", cuerpo)
        self.btn_cancelar.setObjectName("btn_cancelar")
        self.btn_cancelar.setFixedSize(140, 42)
        self.btn_cancelar.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancelar.clicked.connect(self.reject)
        self.btn_cancelar.setStyleSheet("""
            QPushButton#btn_cancelar {
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: 21px;
            }
            QPushButton#btn_cancelar:hover {
                background-color: #DC2626;
            }
        """)
        
        self.btn_confirmar = QPushButton("Cobrar", cuerpo)
        self.btn_confirmar.setObjectName("btn_confirmar")
        self.btn_confirmar.setFixedSize(140, 42)
        self.btn_confirmar.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.btn_confirmar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_confirmar.clicked.connect(self.accept)
        self.btn_confirmar.setEnabled(False)
        self.btn_confirmar.setStyleSheet("""
            QPushButton#btn_confirmar {
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 21px;
            }
            QPushButton#btn_confirmar:hover {
                background-color: #1D4ED8;
            }
            QPushButton#btn_confirmar:disabled {
                background-color: #E2E8F0;
                color: #94A3B8;
            }
        """)
        
        btn_layout.addWidget(self.btn_cancelar)
        btn_layout.addWidget(self.btn_confirmar)
        layout_cuerpo_interno.addLayout(btn_layout)
        
        layout_body.addWidget(cuerpo)
        
        # Enfoque inicial en Monto Recibido
        self.txt_recibido.setFocus()
        
        # Instalar event filter para navegación por teclado
        self.txt_recibido.installEventFilter(self)
        self.btn_cancelar.installEventFilter(self)
        self.btn_confirmar.installEventFilter(self)
 
    def _on_recibido_changed(self, texto):
        try:
            texto = texto.replace(",", ".")
            monto = float(texto) if texto else 0.0
        except ValueError:
            monto = 0.0
            
        self.monto_recibido = monto
        
        if monto >= self.total_pagar:
            self.cambio = round(monto - self.total_pagar, 2)
            self.lbl_cambio_valor.setText(f"$ {self.cambio:.2f}")
            self.btn_confirmar.setEnabled(True)
        else:
            self.cambio = 0.0
            self.lbl_cambio_valor.setText("$ 0.00")
            self.btn_confirmar.setEnabled(False)
 
    def eventFilter(self, watched, event):
        from PyQt6.QtCore import QEvent
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            if watched == self.txt_recibido:
                if key == Qt.Key.Key_Down:
                    self.btn_cancelar.setFocus()
                    return True
                elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    if self.btn_confirmar.isEnabled():
                        self.accept()
                        return True
            elif watched == self.btn_cancelar:
                if key == Qt.Key.Key_Up:
                    self.txt_recibido.setFocus()
                    return True
                elif key == Qt.Key.Key_Right:
                    self.btn_confirmar.setFocus()
                    return True
                elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    self.reject()
                    return True
            elif watched == self.btn_confirmar:
                if key == Qt.Key.Key_Up:
                    self.txt_recibido.setFocus()
                    return True
                elif key == Qt.Key.Key_Left:
                    self.btn_cancelar.setFocus()
                    return True
                elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    if self.btn_confirmar.isEnabled():
                        self.accept()
                        return True
                        
        return super().eventFilter(watched, event)
