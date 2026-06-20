# logica/gestor_reportes.py
import os
from datetime import datetime
from fpdf import FPDF
from datos.base_datos import BaseDatos

class GestorReportes:
    """Gestiona la generación de reportes diarios, exportación a PDF y
    el reinicio de contadores de ventas.

    Referencia SRS:
    - A-011: Generar reporte diario (ingresos, costos, ganancias, detalle y alertas).
    - A-012: Reiniciar contadores sin afectar stock.
    """

    def __init__(self, db: BaseDatos):
        self.db = db

    def obtener_productos_alerta(self) -> list:
        """Obtiene productos cuyo stock actual es menor o igual al mínimo.
        Ordenados de menor a mayor stock (A-011)."""
        sql = """
            SELECT nombre, stock_actual, stock_minimo, tipo_venta
            FROM PRODUCTOS
            WHERE stock_actual <= stock_minimo
            ORDER BY stock_actual ASC
        """
        resultados = self.db.consultar(sql)
        return [dict(fila) for fila in resultados]

    def generar_datos_reporte(self) -> dict:
        """Recopila todos los datos necesarios para el reporte de cierre de día.
        
        Retorna:
            dict con:
            - fecha_hora
            - ingresos_brutos
            - costo_mercancia
            - ganancia_neta
            - transacciones
            - detalle_productos (agrupado por producto)
            - alertas_stock
        """
        # 1. Resumen global (desde VENTAS)
        resumen = self.db.consultar_uno("""
            SELECT 
                COUNT(*) as transacciones,
                COALESCE(SUM(total), 0.0) as ingresos_brutos,
                COALESCE(SUM(costo_total), 0.0) as costo_mercancia
            FROM VENTAS
        """)
        
        ingresos = resumen['ingresos_brutos']
        costos = resumen['costo_mercancia']
        ganancia = ingresos - costos
        transacciones = resumen['transacciones']

        # 2. Desglose por producto (desde DETALLE_VENTA)
        detalle = self.db.consultar("""
            SELECT 
                nombre_producto,
                tipo_venta,
                MAX(precio_unitario_compra) as costo_unitario,
                SUM(cantidad) as cantidad_vendida,
                SUM(subtotal) as total_ingreso,
                SUM(costo) as total_costo
            FROM DETALLE_VENTA
            GROUP BY id_producto, nombre_producto
            ORDER BY total_ingreso DESC
        """)
        detalle_productos = [dict(fila) for fila in detalle]
        for d in detalle_productos:
            d['ganancia'] = d['total_ingreso'] - d['total_costo']

        # 3. Alertas de inventario
        alertas = self.obtener_productos_alerta()

        return {
            'fecha_hora': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'ingresos_brutos': ingresos,
            'costo_mercancia': costos,
            'ganancia_neta': ganancia,
            'transacciones': transacciones,
            'detalle_productos': detalle_productos,
            'alertas_stock': alertas
        }

    def reiniciar_contadores(self):
        """Reinicia a cero los contadores de ventas del día.
        Borra registros de VENTAS y DETALLE_VENTA sin afectar PRODUCTOS (A-012)."""
        self.db._asegurar_conexion()
        try:
            # Primero borrar detalle por la clave foránea
            self.db.cursor.execute("DELETE FROM DETALLE_VENTA;")
            self.db.cursor.execute("DELETE FROM VENTAS;")
            
            # Reiniciar secuencias de autoincrement (opcional pero limpio)
            self.db.cursor.execute("DELETE FROM sqlite_sequence WHERE name='DETALLE_VENTA';")
            self.db.cursor.execute("DELETE FROM sqlite_sequence WHERE name='VENTAS';")
            
            self.db.conexion.commit()
        except Exception as e:
            self.db.conexion.rollback()
            raise RuntimeError(f"Error al reiniciar contadores: {e}")

    def exportar_pdf(self, datos: dict, ruta_guardado: str) -> bool:
        """Genera un archivo PDF con un diseño idéntico al prototipo provisto por el usuario."""
        try:
            pdf = FPDF(orientation="P", unit="mm", format="A4")
            pdf.add_page()
            
            # --- Configuración de márgenes ---
            pdf.set_margins(15, 15, 15)
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Colores base
            COLOR_TEXT = (51, 51, 51)       # Gris oscuro #333333
            COLOR_BLACK = (0, 0, 0)         # Negro
            COLOR_HEADER_BG = (217, 217, 217) # Gris claro del mockup #D9D9D9
            COLOR_BORDER = (160, 160, 160)   # Gris de bordes #A0A0A0
            
            # Helper para formatear montos en dólares (con sufijo $ si es entero grande en cabecera)
            def fmt_currency_suffix(val: float) -> str:
                if val.is_integer():
                    return f"{int(val)}$"
                return f"{val:.2f}$"
            
            def fmt_currency_prefix(val: float) -> str:
                return f"${val:.2f}"

            # --- Encabezado Superior ---
            # Fecha y hora de emisión (DD/MM/YYYY a las HH:MM hrs)
            try:
                # El formato de fecha en el mockup es '03/06/2026 a las 20:32 hrs'
                dt_obj = datetime.strptime(datos['fecha_hora'], "%Y-%m-%d %H:%M:%S")
                fecha_formateada = dt_obj.strftime("%d/%m/%Y a las %H:%M hrs")
            except Exception:
                fecha_formateada = datos['fecha_hora']
                
            pdf.set_text_color(*COLOR_TEXT)
            pdf.set_font("helvetica", "", 12)
            
            # Fila 1 Izquierda: Fecha de emisión
            pdf.set_xy(15, 15)
            pdf.cell(100, 6, f"Fecha y hora de emisión: {fecha_formateada}", border=0, align="L")
            
            # Fila 1 Derecha: Ganancia neta (Título)
            pdf.set_xy(135, 15)
            pdf.cell(60, 6, "Ganancia neta", border=0, align="R")
            
            # Fila 2 Izquierda: Ingresos brutos
            pdf.set_xy(15, 21)
            pdf.cell(100, 6, f"Total de ingresos brutos: {fmt_currency_suffix(datos['ingresos_brutos'])}", border=0, align="L")
            
            # Fila 2 Derecha: Ganancia neta (Valor destacado)
            pdf.set_xy(135, 22)
            pdf.set_font("helvetica", "B", 26)
            pdf.set_text_color(*COLOR_BLACK)
            pdf.cell(60, 10, fmt_currency_suffix(datos['ganancia_neta']), border=0, align="R")
            
            # Fila 3 Izquierda: Número total de transacciones
            pdf.set_font("helvetica", "", 12)
            pdf.set_text_color(*COLOR_TEXT)
            pdf.set_xy(15, 27)
            pdf.cell(100, 6, f"Número total de transacciones: {datos['transacciones']}", border=0, align="L")
            
            pdf.ln(18) # Separación de la cabecera al primer título
            
            # --- Tabla 1: Mercancía vendida ---
            pdf.set_x(15)
            pdf.set_font("helvetica", "B", 14)
            pdf.set_text_color(*COLOR_BLACK)
            pdf.cell(180, 8, "Mercancía vendida", border=0, ln=True, align="L")
            pdf.ln(3)
            
            # Configurar color de borde
            pdf.set_draw_color(*COLOR_BORDER)
            
            # Cabecera de Tabla
            pdf.set_fill_color(*COLOR_HEADER_BG)
            pdf.set_font("helvetica", "", 11)
            
            col_widths = [90, 30, 30, 30]
            
            x_start = 15
            y_start = pdf.get_y()
            alt_cabecera = 12
            
            # Columna 1
            pdf.set_xy(x_start, y_start)
            pdf.cell(col_widths[0], alt_cabecera, "Producto", border=1, fill=True, align="C")
            
            # Columna 2
            pdf.set_xy(x_start + col_widths[0], y_start)
            pdf.multi_cell(col_widths[1], alt_cabecera / 2, "Costo\nmercancía", border=1, fill=True, align="C")
            
            # Columna 3
            pdf.set_xy(x_start + col_widths[0] + col_widths[1], y_start)
            pdf.multi_cell(col_widths[2], alt_cabecera / 2, "Cantidad\nvendida", border=1, fill=True, align="C")
            
            # Columna 4
            pdf.set_xy(x_start + col_widths[0] + col_widths[1] + col_widths[2], y_start)
            pdf.cell(col_widths[3], alt_cabecera, "Total vendido", border=1, fill=True, align="C", ln=True)
            
            pdf.set_y(y_start + alt_cabecera)
            
            # Contenido de Tabla 1
            pdf.set_font("helvetica", "", 10)
            
            if not datos['detalle_productos']:
                pdf.set_x(15)
                pdf.cell(180, 10, "No hubo ventas registradas el día de hoy.", border=1, align="C")
                pdf.ln()
            else:
                for d in datos['detalle_productos']:
                    pdf.set_x(15)
                    
                    costo_unit = d.get('costo_unitario')
                    if costo_unit is None:
                        costo_unit = d['total_costo'] / d['cantidad_vendida'] if d['cantidad_vendida'] > 0 else 0.0
                        
                    es_gr = d.get('tipo_venta') == 'granel'
                    cant_vendida = d['cantidad_vendida']
                    cant_str = f"{cant_vendida:.2f}" if es_gr else f"{int(cant_vendida)}"
                    
                    pdf.cell(col_widths[0], 8, f"  {d['nombre_producto']}", border=1, align="L")
                    pdf.cell(col_widths[1], 8, fmt_currency_prefix(costo_unit), border=1, align="C")
                    pdf.cell(col_widths[2], 8, cant_str, border=1, align="C")
                    pdf.cell(col_widths[3], 8, fmt_currency_prefix(d['total_ingreso']), border=1, align="C", ln=True)
            
            pdf.ln(12) # Espaciado al siguiente título
            
            # --- Tabla 2: Productos con stock en alerta o agotados ---
            pdf.set_x(15)
            pdf.set_font("helvetica", "B", 14)
            pdf.set_text_color(*COLOR_BLACK)
            pdf.cell(180, 8, "Productos con stock en alerta o agotados", border=0, ln=True, align="L")
            pdf.ln(3)
            
            # Cabecera de Tabla 2
            pdf.set_fill_color(*COLOR_HEADER_BG)
            pdf.set_font("helvetica", "", 11)
            
            col_widths_alertas = [120, 60]
            
            pdf.set_x(15)
            pdf.cell(col_widths_alertas[0], 8, "Producto", border=1, fill=True, align="C")
            pdf.cell(col_widths_alertas[1], 8, "Stock", border=1, fill=True, align="C", ln=True)
            
            # Contenido de Tabla 2
            pdf.set_font("helvetica", "", 10)
            
            if not datos['alertas_stock']:
                pdf.set_x(15)
                pdf.cell(180, 8, "Todo el inventario se encuentra por encima del nivel mínimo.", border=1, align="C", ln=True)
            else:
                for a in datos['alertas_stock']:
                    pdf.set_x(15)
                    pdf.cell(col_widths_alertas[0], 8, f"  {a['nombre']}", border=1, align="L")
                    
                    stock_act = a['stock_actual']
                    if stock_act <= 0:
                        stock_txt = "Agotado"
                    else:
                        es_gr = a.get('tipo_venta') == 'granel'
                        if es_gr:
                            stock_txt = f"{stock_act:.2f}KG"
                        else:
                            stock_txt = str(int(stock_act))
                            
                    pdf.cell(col_widths_alertas[1], 8, stock_txt, border=1, align="C", ln=True)
                    
            pdf.output(ruta_guardado)
            return True
            
        except Exception as e:
            print(f"Error al exportar PDF: {e}")
            return False

