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
            SELECT nombre, stock_actual, stock_minimo
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
        """Genera un archivo PDF con un layout complejo usando FPDF2."""
        try:
            pdf = FPDF(orientation="P", unit="mm", format="A4")
            pdf.add_page()
            
            # --- Configuración de colores corporativos ---
            # Azul oscuro para cabeceras, Verde para ganancias, Gris para textos secundarios
            COLOR_PRIMARY = (41, 128, 185)    # #2980b9
            COLOR_DARK = (44, 62, 80)         # #2c3e50
            COLOR_GRAY = (127, 140, 141)      # #7f8c8d
            COLOR_GREEN = (39, 174, 96)       # #27ae60
            COLOR_RED = (192, 57, 43)         # #c0392b
            COLOR_LIGHT_GRAY = (236, 240, 241)# #ecf0f1
            
            # --- Encabezado ---
            pdf.set_font("helvetica", "B", 24)
            pdf.set_text_color(*COLOR_DARK)
            pdf.cell(0, 15, "Reporte de Cierre de Día", ln=True, align="C")
            
            pdf.set_font("helvetica", "", 11)
            pdf.set_text_color(*COLOR_GRAY)
            pdf.cell(0, 8, f"Fecha y hora de emisión: {datos['fecha_hora']}", ln=True, align="C")
            pdf.ln(10)

            # --- Resumen Financiero (Tarjetas Simples) ---
            pdf.set_font("helvetica", "B", 14)
            pdf.set_text_color(*COLOR_DARK)
            pdf.cell(0, 10, "1. Resumen Financiero", ln=True)
            
            pdf.set_font("helvetica", "", 12)
            
            # Bloque de resumen
            resumen_data = [
                ("Transacciones Totales:", str(datos['transacciones']), COLOR_DARK),
                ("Ingresos Brutos:", f"${datos['ingresos_brutos']:,.2f}", COLOR_DARK),
                ("Costo de Mercancía:", f"${datos['costo_mercancia']:,.2f}", COLOR_RED),
                ("Ganancia Neta:", f"${datos['ganancia_neta']:,.2f}", COLOR_GREEN)
            ]
            
            for etiqueta, valor, color in resumen_data:
                pdf.set_text_color(*COLOR_DARK)
                pdf.cell(60, 8, etiqueta, border=0)
                pdf.set_font("helvetica", "B", 12)
                pdf.set_text_color(*color)
                pdf.cell(40, 8, valor, border=0, ln=True)
                pdf.set_font("helvetica", "", 12)
            
            pdf.ln(10)

            # --- Desglose de Ventas por Producto ---
            pdf.set_font("helvetica", "B", 14)
            pdf.set_text_color(*COLOR_DARK)
            pdf.cell(0, 10, "2. Desglose de Ventas por Producto", ln=True)
            
            # Cabecera de Tabla
            pdf.set_fill_color(*COLOR_PRIMARY)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("helvetica", "B", 10)
            
            col_widths = [65, 20, 35, 35, 35]
            cabeceras = ["Producto", "Cant.", "Ingreso", "Costo", "Ganancia"]
            
            for width, header in zip(col_widths, cabeceras):
                pdf.cell(width, 8, header, border=1, fill=True, align="C")
            pdf.ln()
            
            # Contenido de Tabla
            pdf.set_font("helvetica", "", 10)
            pdf.set_text_color(*COLOR_DARK)
            
            fill = False
            pdf.set_fill_color(*COLOR_LIGHT_GRAY)
            
            if not datos['detalle_productos']:
                pdf.cell(sum(col_widths), 10, "No hubo ventas registradas el día de hoy.", border=1, align="C")
                pdf.ln()
            else:
                for d in datos['detalle_productos']:
                    pdf.cell(col_widths[0], 8, d['nombre_producto'], border=1, fill=fill)
                    pdf.cell(col_widths[1], 8, str(d['cantidad_vendida']), border=1, align="R", fill=fill)
                    pdf.cell(col_widths[2], 8, f"${d['total_ingreso']:,.2f}", border=1, align="R", fill=fill)
                    pdf.cell(col_widths[3], 8, f"${d['total_costo']:,.2f}", border=1, align="R", fill=fill)
                    
                    # Ganancia en color verde
                    pdf.set_text_color(*COLOR_GREEN)
                    pdf.cell(col_widths[4], 8, f"${d['ganancia']:,.2f}", border=1, align="R", fill=fill)
                    pdf.set_text_color(*COLOR_DARK) # Restaurar color
                    
                    pdf.ln()
                    fill = not fill
            
            pdf.ln(10)

            # --- Alertas de Inventario ---
            pdf.set_font("helvetica", "B", 14)
            pdf.set_text_color(*COLOR_DARK)
            pdf.cell(0, 10, "3. Alertas de Inventario", ln=True)
            
            if not datos['alertas_stock']:
                pdf.set_font("helvetica", "", 11)
                pdf.set_text_color(*COLOR_GRAY)
                pdf.cell(0, 8, "Todo el inventario se encuentra por encima del nivel mínimo.", ln=True)
            else:
                pdf.set_fill_color(*COLOR_DARK)
                pdf.set_text_color(255, 255, 255)
                pdf.set_font("helvetica", "B", 10)
                
                col_widths_alertas = [100, 45, 45]
                cabeceras_alertas = ["Producto", "Stock Actual", "Mínimo Requerido"]
                
                for width, header in zip(col_widths_alertas, cabeceras_alertas):
                    pdf.cell(width, 8, header, border=1, fill=True, align="C")
                pdf.ln()
                
                pdf.set_font("helvetica", "", 10)
                pdf.set_text_color(*COLOR_DARK)
                
                fill = False
                pdf.set_fill_color(*COLOR_LIGHT_GRAY)
                
                for a in datos['alertas_stock']:
                    pdf.cell(col_widths_alertas[0], 8, a['nombre'], border=1, fill=fill)
                    
                    # Resaltar en rojo si está agotado
                    if a['stock_actual'] <= 0:
                        pdf.set_text_color(*COLOR_RED)
                        stock_txt = "AGOTADO (0)"
                    else:
                        pdf.set_text_color(*COLOR_DARK)
                        stock_txt = str(a['stock_actual'])
                        
                    pdf.cell(col_widths_alertas[1], 8, stock_txt, border=1, align="C", fill=fill)
                    pdf.set_text_color(*COLOR_DARK)
                    
                    pdf.cell(col_widths_alertas[2], 8, str(a['stock_minimo']), border=1, align="C", fill=fill)
                    pdf.ln()
                    fill = not fill

            # Pie de página simple
            pdf.set_y(-15)
            pdf.set_font("helvetica", "I", 8)
            pdf.set_text_color(*COLOR_GRAY)
            pdf.cell(0, 10, "Reporte generado automáticamente por el Sistema de Punto de Venta", align="C")

            pdf.output(ruta_guardado)
            return True
            
        except Exception as e:
            print(f"Error al exportar PDF: {e}")
            return False
