# main.py
import sys
import os

# Agregar la carpeta del proyecto al path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "SistemaDePuntoDeVenta"))

from PyQt6.QtWidgets import QApplication
from datos.base_datos import BaseDatos
from logica.gestor_autenticacion import GestorAutenticacion
from logica.gestor_productos import GestorProductos
from logica.gestor_carrito import GestorCarrito
from logica.gestor_ventas import GestorVentas
from logica.gestor_reportes import GestorReportes
from iu.ventana_principal import VentanaPrincipal

def main():
    home_dir = os.path.expanduser("~")
    
    carpeta_app = os.path.join(home_dir, ".sistema_punto_venta")
    
    if not os.path.exists(carpeta_app):
        os.makedirs(carpeta_app)
        
    RUTA_DB = os.path.join(carpeta_app, "prueba_punto_venta.db")
    db = BaseDatos(ruta_db=RUTA_DB)
    db.inicializar_tablas()
    
    auth = GestorAutenticacion(db)
    gp = GestorProductos(db)
    gc = GestorCarrito()
    gv = GestorVentas(db, gc)
    gr = GestorReportes(db)
    
    app = QApplication(sys.argv)
    
    
    ventana = VentanaPrincipal(
        gestor_productos=gp,
        gestor_carrito=gc,
        gestor_ventas=gv,
        gestor_autenticacion=auth,
        gestor_reportes=gr
    )
    ventana.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
