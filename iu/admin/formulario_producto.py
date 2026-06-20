"""
formulario_producto.py — Formulario de Alta / Edición de Producto
Requerimientos: A-005, A-006, A-007, A-008, A-010
Jueves 18 de Junio — Fase 4, Alta Prioridad
Encargado: Romo Perez Axel Leonel

Diálogo modal para crear un producto nuevo o editar uno existente.
- Diseño visual alineado al prototipo con Header azul unificado.
- Precio de venta y % ganancia vinculados bidireccionalmente (A-006/A-010).
- Botón Guardar deshabilitado mientras haya campos obligatorios vacíos (A-007).
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QButtonGroup,
    QFrame, QWidget, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSignalBlocker, QSize
from PyQt6.QtGui import QFont, QDoubleValidator, QLinearGradient, QPainter, QPaintEvent, QColor, QIcon


# ── Paleta de colores y estilos unificados ────────────────────────── #
_C_HEADER_START = "#1E3A8A"
_C_HEADER_END   = "#0F172A"
_C_HEADER_BTN   = "rgba(255, 255, 255, 0.08)"
_C_HEADER_BTN_HV = "rgba(255, 255, 255, 0.18)"
_C_HEADER_BTN_ACT = "rgba(96, 165, 250, 0.25)"
_C_HEADER_BORDER = "#60A5FA"

_C_BG       = "#FFFFFF"
_C_TITULO   = "#1E293B"
_C_LABEL    = "#64748B"
_C_INPUT_BG = "#F1F5F9" # Un gris ligeramente azulado
_C_BORDER   = "#CBD5E1"
_C_FOCUS    = "#60A5FA"
_C_ERROR    = "#DC2626"
_C_BTN_OFF  = "#CBD5E1" # Gris para botón deshabilitado
_C_BTN_CANC = "#EF4444" # Rojo para cancelar

_FONT_LBL = QFont("Segoe UI", 11, QFont.Weight.DemiBold)
_FONT_INP = QFont("Segoe UI", 11)
_FONT_BTN = QFont("Segoe UI", 14, QFont.Weight.DemiBold)


class _GradientHeader(QWidget):
    """Componente para pintar el fondo azul marino con gradiente."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(72)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0.0, QColor(_C_HEADER_START))
        gradient.setColorAt(1.0, QColor(_C_HEADER_END))
        painter.fillRect(self.rect(), gradient)
        painter.end()


def _estilo_input(error: bool = False) -> str:
    border = _C_ERROR if error else _C_BORDER
    focus  = _C_ERROR if error else _C_FOCUS
    return f"""
        QLineEdit {{
            background-color: {_C_INPUT_BG};
            border: 1.5px solid {border};
            border-radius: 8px;
            padding: 0 14px;
            color: {_C_TITULO};
        }}
        QLineEdit:focus {{ border: 1.5px solid {focus}; background-color: #FFFFFF; }}
    """


# ── Clase Principal del Formulario ────────────────────────────────── #
class FormularioProducto(QDialog):
    def __init__(self, producto: dict | None = None, parent=None):
        super().__init__(parent)
        self._modo_edicion = producto is not None
        self._id_producto  = producto.get("id_producto") if producto else None
        
        self.setWindowFlag(Qt.WindowType.Window)
        if parent:
            self.setGeometry(parent.geometry())
        else:
            self.resize(1200, 800) 
        
        self.setModal(True)
        self.setStyleSheet(f"background-color: {_C_BG};")
        
        self._build_ui()
        
        if producto:
            self._cargar_datos(producto)
        self._validar()

    def _build_ui(self):
        # Layout raíz sin márgenes para que el header toque perfectamente los bordes exteriores
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 1. Agregamos el Header Superior Azul
        root.addWidget(self._crear_header())

        # 2. Contenedor del Cuerpo (Campos y botones de acción inferiores)
        cuerpo_widget = QWidget()
        cuerpo_lay = QVBoxLayout(cuerpo_widget)
        cuerpo_lay.setContentsMargins(50, 30, 50, 30)
        cuerpo_lay.setSpacing(20)

        # Sub-layout para organizar los campos de texto de forma vertical y limpia
        form_lay = QVBoxLayout()
        form_lay.setSpacing(18)

        # --- Campo: Nombre del producto ---
        self._inp_nombre = QLineEdit()
        self._inp_nombre.setFixedSize(450, 42)
        self._inp_nombre.setFont(_FONT_INP)
        self._inp_nombre.setStyleSheet(_estilo_input())
        form_lay.addLayout(self._bloque_campo("Nombre del producto", self._inp_nombre))

        # --- Campo: Tipo de venta (Botones segmentados) ---
        cont_tipo = QWidget()
        h_tipo = QHBoxLayout(cont_tipo)
        h_tipo.setContentsMargins(0, 0, 0, 0)
        h_tipo.setSpacing(0)

        self._rb_piezas = QPushButton("Piezas/Unidades")
        self._rb_piezas.setCheckable(True)
        self._rb_piezas.setChecked(True)
        self._rb_piezas.setFixedSize(150, 38)

        self._rb_granel = QPushButton("Granel")
        self._rb_granel.setCheckable(True)
        self._rb_granel.setFixedSize(150, 38)

        estilo_base_btn = f"""
            QPushButton {{
                background-color: {_C_INPUT_BG}; color: {_C_LABEL};
                border: 1.5px solid {_C_BORDER}; font-weight: bold; font-size: 13px;
            }}
            QPushButton:checked {{
                background-color: #E0F2FE; color: #0284C7; border: 1.5px solid #38BDF8;
            }}
        """
        self._rb_piezas.setStyleSheet(estilo_base_btn + "QPushButton { border-top-left-radius: 8px; border-bottom-left-radius: 8px; border-right: none; }")
        self._rb_granel.setStyleSheet(estilo_base_btn + "QPushButton { border-top-right-radius: 8px; border-bottom-right-radius: 8px; }")

        self._grupo_tipo = QButtonGroup(self)
        self._grupo_tipo.addButton(self._rb_piezas)
        self._grupo_tipo.addButton(self._rb_granel)

        h_tipo.addWidget(self._rb_piezas)
        h_tipo.addWidget(self._rb_granel)
        form_lay.addLayout(self._bloque_campo("Tipo de venta", cont_tipo))

        # --- Campo: Precio de compra ---
        w_pc, self._inp_precio_compra = self._crear_input_simbolo("$", 180)
        form_lay.addLayout(self._bloque_campo("Precio de compra", w_pc))

        # --- Campos: Precio de venta y Ganancia ---
        h_precios = QHBoxLayout()
        w_pv, self._inp_precio_venta = self._crear_input_simbolo("$", 160)
        w_gan, self._inp_ganancia = self._crear_input_simbolo("%", 160)

        h_precios.addStretch()
        h_precios.addLayout(self._bloque_campo("Precio de venta", w_pv))
        
        lbl_flecha = QLabel("⇆")
        lbl_flecha.setFont(QFont("Segoe UI", 16))
        lbl_flecha.setStyleSheet(f"color: {_C_LABEL}; margin-top: 25px;")
        h_precios.addWidget(lbl_flecha, alignment=Qt.AlignmentFlag.AlignTop)
        
        h_precios.addLayout(self._bloque_campo("Ganancia", w_gan))
        h_precios.addStretch()
        form_lay.addLayout(h_precios)

        # --- Campos: Stock Mínimo y Stock Actual ---
        h_stocks = QHBoxLayout()
        self._inp_stock_min = QLineEdit()
        self._inp_stock_min.setFixedSize(160, 42)
        self._inp_stock_min.setFont(_FONT_INP)
        self._inp_stock_min.setStyleSheet(_estilo_input())
        self._inp_stock_min.setValidator(QDoubleValidator(0.0, 999999.99, 3, self))

        self._inp_stock_actual = QLineEdit()
        self._inp_stock_actual.setFixedSize(160, 42)
        self._inp_stock_actual.setFont(_FONT_INP)
        self._inp_stock_actual.setStyleSheet(_estilo_input())
        self._inp_stock_actual.setValidator(QDoubleValidator(0.0, 999999.99, 3, self))

        h_stocks.addStretch()
        h_stocks.addLayout(self._bloque_campo("Stock mínimo", self._inp_stock_min))
        h_stocks.addSpacing(40)
        h_stocks.addLayout(self._bloque_campo("Stock actual", self._inp_stock_actual))
        h_stocks.addStretch()
        form_lay.addLayout(h_stocks)

        cuerpo_lay.addLayout(form_lay)
        cuerpo_lay.addStretch()

        # --- Botones Inferiores de Acción (Píldoras en los Extremos) ---
        fila_btns = QHBoxLayout()
        
        self._btn_cancelar = QPushButton("Cancelar")
        self._btn_cancelar.setFixedSize(240, 56)
        self._btn_cancelar.setFont(_FONT_BTN)
        self._btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_cancelar.setStyleSheet(f"""
            QPushButton {{
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: 16px;
            }}
            QPushButton:hover {{
                background-color: #DC2626;
            }}
        """)
        self._btn_cancelar.clicked.connect(self.reject)

        self._btn_guardar = QPushButton("Guardar")
        self._btn_guardar.setFixedSize(200, 56)
        self._btn_guardar.setFont(_FONT_BTN)
        self._btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        self._aplicar_estilo_guardar(False)
        self._btn_guardar.clicked.connect(self.accept)

        fila_btns.addWidget(self._btn_cancelar, alignment=Qt.AlignmentFlag.AlignLeft)
        fila_btns.addStretch()
        fila_btns.addWidget(self._btn_guardar, alignment=Qt.AlignmentFlag.AlignRight)
        
        cuerpo_lay.addLayout(fila_btns)
        root.addWidget(cuerpo_widget)

        # --- Conexiones de Eventos ---
        for w in (self._inp_nombre, self._inp_precio_compra,
                  self._inp_precio_venta, self._inp_ganancia,
                  self._inp_stock_min, self._inp_stock_actual):
            w.textChanged.connect(self._validar)

        self._inp_precio_venta.textChanged.connect(self._precio_venta_cambiado)
        self._inp_ganancia.textChanged.connect(self._ganancia_cambiada)

    # ────────────────────────────────────────────────────────────────── #
    #  Componentes Visuales Auxiliares                                   #
    # ────────────────────────────────────────────────────────────────── #

    def _crear_header(self) -> QWidget:
        """Construye e inicializa la barra azul de navegación superior."""
        header = _GradientHeader()
        lay = QHBoxLayout(header)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(12)
        
        lay.addStretch() # Empuja los botones a la derecha

        from iu.cajero.pantalla_cajero import crear_icono_bag, crear_icono_gear
        icono_cajero = crear_icono_bag(22, QColor(148, 163, 184))
        icono_admin = crear_icono_gear(22, QColor(255, 255, 255))

        self.btn_cajero = self._crear_boton_nav("  Cajero", icono_cajero, activo=False)
        self.btn_admin  = self._crear_boton_nav("  Admin.", icono_admin, activo=True)

        lay.addWidget(self.btn_cajero)
        lay.addWidget(self.btn_admin)
        return header

    def _crear_boton_nav(self, texto: str, icono: QIcon, activo: bool = False) -> QPushButton:
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
                    background-color: rgba(96, 165, 250, 0.25);
                    color: #FFFFFF;
                    border: 1.5px solid #60A5FA;
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

    def _bloque_campo(self, texto_label: str, widget_input: QWidget) -> QVBoxLayout:
        lay = QVBoxLayout()
        lay.setSpacing(6)
        lbl = QLabel(texto_label)
        lbl.setFont(_FONT_LBL)
        lbl.setStyleSheet(f"color: {_C_LABEL};")
        lay.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignHCenter)
        lay.addWidget(widget_input, alignment=Qt.AlignmentFlag.AlignHCenter)
        return lay

    def _crear_input_simbolo(self, simbolo: str, ancho: int) -> tuple[QFrame, QLineEdit]:
        contenedor = QFrame()
        contenedor.setFixedSize(ancho, 42)
        contenedor.setStyleSheet(f"QFrame {{ background-color: {_C_INPUT_BG}; border: 1.5px solid {_C_BORDER}; border-radius: 8px; }}")
        lay = QHBoxLayout(contenedor)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        inp = QLineEdit()
        inp.setFont(_FONT_INP)
        inp.setValidator(QDoubleValidator(-100.0, 999999.99, 2, self))
        inp.setStyleSheet(f"QLineEdit {{ border: none; background: transparent; padding: 0 12px; color: {_C_TITULO}; }}")

        lbl_simbolo = QLabel(simbolo)
        lbl_simbolo.setFont(_FONT_INP)
        lbl_simbolo.setStyleSheet(f"color: {_C_TITULO}; border-left: 1.5px solid {_C_BORDER}; padding: 0 14px; background: transparent;")

        lay.addWidget(inp)
        lay.addWidget(lbl_simbolo)
        return contenedor, inp

    # ────────────────────────────────────────────────────────────────── #
    #  Lógica del Formulario                                              #
    # ────────────────────────────────────────────────────────────────── #

    def _cargar_datos(self, p: dict):
        self._inp_nombre.setText(p.get("nombre", ""))
        tipo = p.get("tipo_venta", "pieza").lower()
        self._rb_granel.setChecked(tipo == "granel")
        self._rb_piezas.setChecked(tipo != "granel")
        self._inp_precio_compra.setText(str(p.get("precio_compra", "")))
        self._inp_precio_venta.setText(str(p.get("precio_venta", "")))
        self._inp_stock_min.setText(str(p.get("stock_minimo", "")))
        self._inp_stock_actual.setText(str(p.get("stock_actual", "")))

    def _precio_venta_cambiado(self, texto: str):
        compra = self._float(self._inp_precio_compra.text())
        venta  = self._float(texto)
        if compra and compra > 0 and venta is not None:
            pct = ((venta - compra) / compra) * 100.0
            with QSignalBlocker(self._inp_ganancia):
                self._inp_ganancia.setText(f"{pct:.2f}")

    def _ganancia_cambiada(self, texto: str):
        compra = self._float(self._inp_precio_compra.text())
        pct    = self._float(texto)
        if compra and compra > 0 and pct is not None:
            precio = compra * (1 + pct / 100.0)
            with QSignalBlocker(self._inp_precio_venta):
                self._inp_precio_venta.setText(f"{precio:.2f}")

    def _validar(self):
        ok = all([
            self._inp_nombre.text().strip() != "",
            self._float(self._inp_precio_compra.text()) is not None,
            self._float(self._inp_precio_venta.text()) is not None,
            self._float(self._inp_stock_min.text())    is not None,
            self._float(self._inp_stock_actual.text()) is not None,
        ])
        self._btn_guardar.setEnabled(ok)
        self._aplicar_estilo_guardar(ok)

    def datos_producto(self) -> dict:
        tipo = "granel" if self._rb_granel.isChecked() else "pieza"
        datos = {
            "nombre":        self._inp_nombre.text().strip(),
            "tipo_venta":    tipo,
            "precio_compra": self._float(self._inp_precio_compra.text()) or 0.0,
            "precio_venta":  self._float(self._inp_precio_venta.text())  or 0.0,
            "stock_minimo":  self._float(self._inp_stock_min.text())     or 0.0,
            "stock_actual":  self._float(self._inp_stock_actual.text())  or 0.0,
        }
        if self._modo_edicion:
            datos["id_producto"] = self._id_producto
        return datos

    @staticmethod
    def _float(texto: str) -> float | None:
        try:
            return float(texto.replace(",", "."))
        except (ValueError, AttributeError):
            return None

    def _aplicar_estilo_guardar(self, habilitado: bool):
        if habilitado:
            self._btn_guardar.setStyleSheet("""
                QPushButton {
                    background-color: #10B981;
                    color: white;
                    border: none;
                    border-radius: 16px;
                }
                QPushButton:hover {
                    background-color: #059669;
                }
            """)
        else:
            self._btn_guardar.setStyleSheet(f"""
                QPushButton {{
                    background-color: {_C_BTN_OFF};
                    color: white;
                    border: none;
                    border-radius: 16px;
                }}
            """)


# ══════════════════════════════════════════════════ #
#  CÓDIGO DE PRUEBA INTEGRADO (STANDALONE)           #
# ══════════════════════════════════════════════════ #
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    formulario_alta = FormularioProducto()
    formulario_alta.exec()

    sys.exit()