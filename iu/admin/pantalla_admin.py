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
    QSizePolicy, QGraphicsDropShadowEffect, QDialog,
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import (
    QFont, QColor, QLinearGradient, QPainter,
    QPaintEvent, QIcon, QPen, QPixmap
)
import os
from datetime import datetime
from iu.admin.formulario_producto import FormularioProducto


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
        self.btn_confirmar = QPushButton("Continuar")
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
#  Diálogo confirmación Eliminar producto            #
# ══════════════════════════════════════════════════ #

class DialogoConfirmacionEliminar(QDialog):
    """Diálogo modal para confirmación de eliminación de producto.
    Cumple con el requerimiento de tener el foco inicial por defecto en Cancelar."""
    def __init__(self, nombre_producto: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirmar Eliminación")
        self.setFixedSize(400, 200)
        self.setModal(True)
        self.setStyleSheet("background-color: #FFFFFF;")
        self._build(nombre_producto)
        
    def _build(self, nombre):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 24, 20, 20)
        layout.setSpacing(10)
        
        lbl_titulo = QLabel("¿Eliminar producto?")
        lbl_titulo.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet("color: #333333;")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_titulo)
        
        lbl_aviso = QLabel(f"¿Está seguro que desea eliminar el producto\n\"{nombre}\"\nde su tienda?")
        lbl_aviso.setFont(QFont("Segoe UI", 11))
        lbl_aviso.setStyleSheet("color: #333333;")
        lbl_aviso.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_aviso.setWordWrap(True)
        layout.addWidget(lbl_aviso)
        
        layout.addSpacing(15)
        
        fila = QHBoxLayout()
        fila.setSpacing(35)
        fila.addStretch()
        
        self.btn_confirmar = QPushButton("Confirmar")
        self.btn_confirmar.setFixedSize(125, 40)
        self.btn_confirmar.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        self.btn_confirmar.setStyleSheet("""
            QPushButton { 
                background-color: #52C5D8;
                color: white; 
                border: none; 
                border-radius: 20px;
            }
            QPushButton:hover { background-color: #42AFC1; }
            QPushButton:pressed { background-color: #339AA8; }
        """)
        self.btn_confirmar.clicked.connect(self.accept)
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setFixedSize(125, 40)
        self.btn_cancelar.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        self.btn_cancelar.setDefault(True)
        self.btn_cancelar.setAutoDefault(True)
        self.btn_cancelar.setStyleSheet("""
            QPushButton { 
                background-color: #DE4A4A;
                color: white; 
                border: none; 
                border-radius: 20px;
            }
            QPushButton:hover { background-color: #C63D3D; }
            QPushButton:pressed { background-color: #AF3030; }
        """)
        self.btn_cancelar.clicked.connect(self.reject)
        
        fila.addWidget(self.btn_confirmar)
        fila.addWidget(self.btn_cancelar)
        fila.addStretch()
        
        layout.addLayout(fila)
        self.btn_cancelar.setFocus()


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

    def __init__(self, gestor_productos, gestor_reportes, parent=None):
        super().__init__(parent)
        self.gp = gestor_productos
        self.gr = gestor_reportes
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

        from iu.cajero.pantalla_cajero import crear_icono_bag, crear_icono_gear
        icono_cajero = crear_icono_bag(22, QColor(148, 163, 184))
        icono_admin = crear_icono_gear(22, QColor(255, 255, 255))

        self.btn_cajero = self._btn_header("  Cajero", icono_cajero, activo=False)
        self.btn_admin  = self._btn_header("  Admin.", icono_admin, activo=True)
        self.btn_cajero.clicked.connect(self.senal_ir_cajero.emit)

        lay.addWidget(self.btn_cajero)
        lay.addWidget(self.btn_admin)
        return header

    def _btn_header(self, texto: str, icono: QIcon, activo: bool = False) -> QPushButton:
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
                    background-color: {_Colors.HEADER_BTN_ACTIVE};
                    color: #FFFFFF;
                    border: 1.5px solid {_Colors.HEADER_BTN_BORDER};
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
        self.btn_reporte.clicked.connect(self._generar_reporte)

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
        self.btn_nuevo.clicked.connect(self._nuevo_producto)

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

    def _insertar_fila(self, producto: dict):
        fila = self._crear_fila(producto)
        idx = self._lay_filas.count() - 1 
        self._lay_filas.insertWidget(idx, fila)
        self._filas[producto["id_producto"]] = fila

    def _crear_fila(self, producto: dict) -> _FilaCatalogo:
        fila = _FilaCatalogo(producto)
        fila.senal_editar.connect(self._editar_producto)
        fila.senal_eliminar.connect(self._eliminar_producto)
        return fila

    def _nuevo_producto(self):
        dialogo = FormularioProducto(parent=self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            datos = dialogo.datos_producto()
            exito = self.gp.alta_producto(
                datos["nombre"],
                datos["tipo_venta"],
                datos["precio_compra"],
                datos["precio_venta"],
                datos["stock_minimo"],
                datos["stock_actual"]
            )
            if exito:
                self.cargar_catalogo(self.gp.obtener_catalogo())
            else:
                QMessageBox.critical(self, "Error de Guardado", "No se pudo registrar el nuevo producto en la base de datos.")

    def _editar_producto(self, id_producto):
        producto = self.gp.db.consultar_uno(
            "SELECT id_producto, nombre, tipo_venta, precio_compra, precio_venta, stock_minimo, stock_actual FROM PRODUCTOS WHERE id_producto = ?;",
            (id_producto,)
        )
        if not producto:
            QMessageBox.warning(self, "Error de Selección", "No se encontró el producto a editar.")
            return
            
        dialogo = FormularioProducto(producto=dict(producto), parent=self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            datos = dialogo.datos_producto()
            exito = self.gp.editar_producto(
                id_producto,
                datos["nombre"],
                datos["tipo_venta"],
                datos["precio_compra"],
                datos["precio_venta"],
                datos["stock_minimo"],
                datos["stock_actual"]
            )
            if exito:
                self.cargar_catalogo(self.gp.obtener_catalogo())
            else:
                QMessageBox.critical(self, "Error de Guardado", "No se pudo actualizar el producto en la base de datos.")

    def _eliminar_producto(self, id_producto):
        producto = self.gp.db.consultar_uno("SELECT nombre FROM PRODUCTOS WHERE id_producto = ?;", (id_producto,))
        if not producto:
            return
        nombre = producto["nombre"]
        
        dialogo = DialogoConfirmacionEliminar(nombre, parent=self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            exito = self.gp.eliminar_producto(id_producto)
            if exito:
                self.cargar_catalogo(self.gp.obtener_catalogo())
            else:
                QMessageBox.critical(self, "Error al Eliminar", "No se pudo eliminar el producto de la base de datos.")

    def _generar_reporte(self):
        # 1. Confirmar con diálogo visual
        dlg = _DialogoConfirmarReporte(parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
            
        # 2. Recopilar datos
        datos = self.gr.generar_datos_reporte()
        
        # 3. Elegir ruta de guardado mediante QFileDialog
        ruta_archivo, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Reporte Diario",
            os.path.join(os.path.expanduser("~"), f"Reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"),
            "Documentos PDF (*.pdf)"
        )
        if not ruta_archivo:
            return
            
        # 4. Exportar a PDF
        if self.gr.exportar_pdf(datos, ruta_archivo):
            # 5. Reiniciar contadores (vaciar tablas ventas y detalle_ventas)
            try:
                self.gr.reiniciar_contadores()
                QMessageBox.information(
                    self,
                    "Reporte Generado",
                    f"Reporte diario exportado con éxito en:\n{ruta_archivo}\n\nLos contadores de ventas del día se han reiniciado a cero."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error de Reinicio",
                    f"Se exportó el PDF, pero ocurrió un error al reiniciar los contadores diarios:\n{e}"
                )
            self.cargar_catalogo(self.gp.obtener_catalogo())
        else:
            QMessageBox.critical(self, "Error de Exportación", "No se pudo generar el archivo PDF del reporte diario.")
    
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