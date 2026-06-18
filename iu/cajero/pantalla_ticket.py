# iu/cajero/pantalla_ticket.py
"""
Módulo de Ticket — Pantalla para mostrar el desglose de venta (ticket) y diálogo de confirmación.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtGui import QFont, QColor
from iu.cajero.pantalla_cajero import Colors, GradientHeader, FondoPremium, crear_icono_bag, crear_icono_gear


class DialogoRequiereTicket(QDialog):
    """Diálogo modal para preguntar al cajero si requiere ticket."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Requiere ticket")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(450, 220)
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
        
        lbl_titulo = QLabel("Requiere ticket", cabecera)
        lbl_titulo.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet("color: white; border: none;")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_cabecera.addWidget(lbl_titulo)
        layout_body.addWidget(cabecera)
        
        # Cuerpo
        cuerpo = QWidget()
        layout_cuerpo_interno = QVBoxLayout(cuerpo)
        layout_cuerpo_interno.setContentsMargins(24, 24, 24, 24)
        layout_cuerpo_interno.setSpacing(20)
        
        lbl_msg = QLabel("¿El cliente requiere ticket de compra?", cuerpo)
        lbl_msg.setWordWrap(True)
        lbl_msg.setFont(QFont("Segoe UI", 13))
        lbl_msg.setStyleSheet("color: #334155; border: none;")
        lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_cuerpo_interno.addWidget(lbl_msg)
        
        # Botones Sí/No
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(24)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.btn_si = QPushButton("Sí", cuerpo)
        self.btn_si.setObjectName("btn_si")
        self.btn_si.setFixedSize(120, 42)
        self.btn_si.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.btn_si.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_si.clicked.connect(self.accept)
        self.btn_si.setStyleSheet("""
            QPushButton#btn_si {
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 21px;
            }
            QPushButton#btn_si:hover {
                background-color: #1D4ED8;
            }
        """)
        
        self.btn_no = QPushButton("No", cuerpo)
        self.btn_no.setObjectName("btn_no")
        self.btn_no.setFixedSize(120, 42)
        self.btn_no.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.btn_no.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_no.clicked.connect(self.reject)
        self.btn_no.setStyleSheet("""
            QPushButton#btn_no {
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: 21px;
            }
            QPushButton#btn_no:hover {
                background-color: #DC2626;
            }
        """)
        
        btn_layout.addWidget(self.btn_si)
        btn_layout.addWidget(self.btn_no)
        layout_cuerpo_interno.addLayout(btn_layout)
        layout_body.addWidget(cuerpo)
        
        # Foco predeterminado en Sí
        self.btn_si.setDefault(True)
        self.btn_si.setFocus()
        
        # Instalar event filter para navegación por teclado
        self.btn_si.installEventFilter(self)
        self.btn_no.installEventFilter(self)

    def eventFilter(self, watched, event):
        from PyQt6.QtCore import QEvent
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            if watched == self.btn_si:
                if key == Qt.Key.Key_Right:
                    self.btn_no.setFocus()
                    return True
                elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    self.accept()
                    return True
            elif watched == self.btn_no:
                if key == Qt.Key.Key_Left:
                    self.btn_si.setFocus()
                    return True
                elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    self.reject()
                    return True
        return super().eventFilter(watched, event)


class PantallaTicket(QDialog):
    """Pantalla/Modal de Ticket de compra.
    
    Despliega la lista completa de artículos en formato ticket y botón Continuar.
    """
    
    def __init__(self, datos_venta: dict, parent=None):
        super().__init__(parent)
        self.datos_venta = datos_venta
        self.setWindowTitle("Ticket de Venta")
        
        # Frameless para overlay limpio
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # Copiar dimensiones del padre si está disponible para overlay exacto
        if parent:
            self.setFixedSize(parent.size())
        else:
            self.setFixedSize(1280, 850)
            
        self._setup_ui()

    def _setup_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)
        
        # 1. Cabecera (GradientHeader similar al cajero)
        header = GradientHeader()
        layout_header = QHBoxLayout(header)
        layout_header.setContentsMargins(24, 0, 24, 0)
        layout_header.setSpacing(16)
        
        layout_header.addStretch(1)
        
        # Botones de navegación inactivos
        icono_cajero = crear_icono_bag(22, QColor(255, 255, 255))
        icono_admin = crear_icono_gear(22, QColor(148, 163, 184))
        
        btn_cajero = QPushButton("  Cajero", header)
        btn_cajero.setIcon(icono_cajero)
        btn_cajero.setIconSize(QSize(22, 22))
        btn_cajero.setFixedHeight(46)
        btn_cajero.setMinimumWidth(150)
        btn_cajero.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
        btn_cajero.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.HEADER_BTN_ACTIVE};
                color: #FFFFFF;
                border: 1.5px solid {Colors.HEADER_BTN_ACTIVE_BORDER};
                border-radius: 12px;
                padding: 0 16px;
            }}
        """)
        
        btn_admin = QPushButton("  Admin.", header)
        btn_admin.setIcon(icono_admin)
        btn_admin.setIconSize(QSize(22, 22))
        btn_admin.setFixedHeight(46)
        btn_admin.setMinimumWidth(150)
        btn_admin.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
        btn_admin.setStyleSheet("""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.04);
                color: #94A3B8;
                border: 1.5px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                padding: 0 16px;
            }}
        """)
        
        layout_header.addWidget(btn_cajero)
        layout_header.addWidget(btn_admin)
        layout_principal.addWidget(header)
        
        # 2. Cuerpo Central (FondoPremium con tarjeta blanca en el centro)
        self.cuerpo = FondoPremium(self)
        layout_cuerpo = QVBoxLayout(self.cuerpo)
        layout_cuerpo.setContentsMargins(24, 20, 24, 20)
        
        # Layout para centrar el ticket
        layout_centro = QHBoxLayout()
        layout_centro.addStretch(1)
        
        # Tarjeta del Ticket (Color blanco con sombra)
        self.ticket_card = QFrame(self.cuerpo)
        self.ticket_card.setObjectName("TicketCard")
        self.ticket_card.setFixedSize(500, 560)
        self.ticket_card.setStyleSheet("""
            QFrame#TicketCard {
                background-color: white;
                border: 1.5px solid #CBD5E1;
                border-radius: 16px;
            }
        """)
        
        # Sombra sutil
        sombra = QGraphicsDropShadowEffect(self)
        sombra.setBlurRadius(24)
        sombra.setOffset(0, 6)
        sombra.setColor(QColor(0, 0, 0, 30))
        self.ticket_card.setGraphicsEffect(sombra)
        
        layout_ticket = QVBoxLayout(self.ticket_card)
        layout_ticket.setContentsMargins(24, 24, 24, 24)
        layout_ticket.setSpacing(16)
        
        # Título del Ticket
        lbl_ticket_titulo = QLabel("Ticket", self.ticket_card)
        lbl_ticket_titulo.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        lbl_ticket_titulo.setStyleSheet("color: #0F172A; border: none;")
        lbl_ticket_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_ticket.addWidget(lbl_ticket_titulo)
        
        # Tabla de Desglose
        self.tabla = QTableWidget(self.ticket_card)
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Nombre", "Precio", "Cantidad", "Subtotal"])
        
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setShowGrid(False)
        self.tabla.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.tabla.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        self.tabla.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                border: none;
                gridline-color: transparent;
                font-family: "Segoe UI";
                font-size: 13px;
                color: #1E293B;
            }
            QTableWidget::item {
                padding: 8px 4px;
                border-bottom: 1px dashed #E2E8F0;
            }
            QHeaderView::section {
                background-color: transparent;
                border: none;
                border-bottom: 1.5px solid #0F172A;
                font-family: "Segoe UI";
                font-size: 11pt;
                font-weight: bold;
                color: #0F172A;
                padding: 6px 4px;
            }
        """)
        
        # Llenar tabla con los datos reales de la venta
        self.tabla.setRowCount(0)
        for idx, item in enumerate(self.datos_venta['items']):
            self.tabla.insertRow(idx)
            es_gr = item['tipo_venta'] == 'granel'
            
            # Formatos de precio y cantidad basados en el prototipo
            sufijo_precio = "/Kg" if es_gr else ""
            sufijo_cantidad = "Kg" if es_gr else "pz"
            
            precio_unit_txt = f"${item['precio_unitario']:.2f}{sufijo_precio}"
            cantidad_txt = f"{item['cantidad']:.2f}{sufijo_cantidad}" if es_gr else f"{int(item['cantidad'])}{sufijo_cantidad}"
            
            # Col 0: Nombre
            item_nom = QTableWidgetItem(item['nombre'])
            item_nom.setFont(QFont("Segoe UI", 10))
            item_nom.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.tabla.setItem(idx, 0, item_nom)
            
            # Col 1: Precio
            item_prec = QTableWidgetItem(precio_unit_txt)
            item_prec.setFont(QFont("Segoe UI", 10))
            item_prec.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_prec.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.tabla.setItem(idx, 1, item_prec)
            
            # Col 2: Cantidad
            item_cant = QTableWidgetItem(cantidad_txt)
            item_cant.setFont(QFont("Segoe UI", 10))
            item_cant.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_cant.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.tabla.setItem(idx, 2, item_cant)
            
            # Col 3: Subtotal
            item_sub = QTableWidgetItem(f"${item['subtotal']:.2f}")
            item_sub.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            item_sub.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            item_sub.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.tabla.setItem(idx, 3, item_sub)
            
        layout_ticket.addWidget(self.tabla)
        
        # Línea de Total
        lbl_total = QLabel(f"Total: {self.datos_venta['total']:.2f}$", self.ticket_card)
        lbl_total.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        lbl_total.setStyleSheet("color: #0F172A; border: none;")
        lbl_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_ticket.addWidget(lbl_total)
        
        layout_centro.addWidget(self.ticket_card)
        layout_centro.addStretch(1)
        layout_cuerpo.addLayout(layout_centro)
        
        # 3. Fila del Botón Continuar (Esquina inferior derecha)
        layout_bottom = QHBoxLayout()
        layout_bottom.addStretch(1)
        
        self.btn_continuar = QPushButton("Continuar", self.cuerpo)
        self.btn_continuar.setObjectName("btn_continuar")
        self.btn_continuar.setFixedSize(180, 48)
        self.btn_continuar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_continuar.clicked.connect(self.accept)
        
        # Estilo del botón conforme al prototipo
        self.btn_continuar.setStyleSheet("""
            QPushButton#btn_continuar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #A5F3FC, stop:1 #38BDF8);
                border: 2px solid #0F172A;
                border-radius: 24px;
                color: #0F172A;
                font-family: "Segoe UI";
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton#btn_continuar:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #CFFAFE, stop:1 #0EA5E9);
            }
            QPushButton#btn_continuar:pressed {
                background: #0284C7;
            }
        """)
        
        # Sombra sutil para el botón
        sombra_btn = QGraphicsDropShadowEffect(self)
        sombra_btn.setBlurRadius(15)
        sombra_btn.setOffset(0, 4)
        sombra_btn.setColor(QColor(0, 0, 0, 40))
        self.btn_continuar.setGraphicsEffect(sombra_btn)
        
        layout_bottom.addWidget(self.btn_continuar)
        layout_cuerpo.addLayout(layout_bottom)
        layout_principal.addWidget(self.cuerpo)
        
        # Enfoque inicial en Continuar y habilitar Enter
        self.btn_continuar.setDefault(True)
        self.btn_continuar.setFocus()
        
        # Instalar event filter para interceptar escape o cerrar
        self.btn_continuar.installEventFilter(self)

    def eventFilter(self, watched, event):
        from PyQt6.QtCore import QEvent
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Escape, Qt.Key.Key_Space):
                self.accept()
                return True
        return super().eventFilter(watched, event)
