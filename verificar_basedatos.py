# verificar.py
#import os
import sqlite3
from datos.base_datos import BaseDatos

ruta_base = "datos/punto_venta.db"

db = BaseDatos(ruta_db=ruta_base)
db.inicializar_tablas()

conexion = sqlite3.connect(ruta_base)
cursor = conexion.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
tablas_encontradas = [fila[0] for fila in cursor.fetchall()]
conexion.close()

tablas_esperadas = ["PRODUCTOS", "VENTAS", "DETALLE_VENTA", "CONFIGURACION"]
exito = sorted(tablas_encontradas) == sorted(tablas_esperadas)

print(f"Tablas detectadas en el archivo: {tablas_encontradas}")
if exito:
    print("STATUS: ¡VERIFICACIÓN EXITOSA! Las 4 tablas están en su lugar.")
else:
    print("STATUS: ERROR. La estructura no coincide con el diseño original.")