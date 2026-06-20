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
from iu.cajero.pantalla_cajero import Colors, GradientHeader, FondoPremium, crear_icono_bag, crear_icono_gear, DialogoBaseCabecera


class DialogoRequiereTicket(DialogoBaseCabecera):
    """Diálogo modal para preguntar al cajero si requiere ticket."""
    def __init__(self, parent=None):
        super().__init__("Requiere ticket", "sí", "NO", parent)


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
