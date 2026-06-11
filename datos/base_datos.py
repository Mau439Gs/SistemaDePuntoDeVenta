import sqlite3


class BaseDatos:
    """Gestiona la conexión y operaciones con la base de datos SQLite."""

    def __init__(self, ruta_db="punto_venta.db"):
        self.ruta_db = ruta_db
        self.conexion = None
        self.cursor = None

    def conectar(self):
        """Establece la conexión con la base de datos y habilita el modo WAL."""
        try:
            self.conexion = sqlite3.connect(self.ruta_db)
            self.conexion.row_factory = sqlite3.Row
            self.cursor = self.conexion.cursor()
            # Modo WAL para mejor integridad ACID y rendimiento
            self.cursor.execute("PRAGMA journal_mode=WAL")
            # Habilitar claves foráneas
            self.cursor.execute("PRAGMA foreign_keys=ON")
        except sqlite3.Error as e:
            print(f"Error al conectar a la base de datos: {e}")

    def desconectar(self):
        """Cierra la conexión con la base de datos."""
        if self.conexion:
            self.conexion.close()
            self.conexion = None
            self.cursor = None

    def inicializar_tablas(self):
        """Crea las 4 tablas del sistema si no existen."""
        if not self.conexion:
            self.conectar()

        try:
            # Tabla PRODUCTOS
            # Catálogo de artículos de la tienda.
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS PRODUCTOS (
                    id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    tipo_venta TEXT NOT NULL,
                    precio_compra REAL NOT NULL,
                    precio_venta REAL NOT NULL,
                    stock_minimo REAL NOT NULL,
                    stock_actual REAL NOT NULL
                )
            """)

            # Tabla VENTAS
            # Encabezados de transacciones confirmadas.
            # Los registros se eliminan tras generar el reporte diario.
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS VENTAS (
                    id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha_hora TEXT NOT NULL,
                    total REAL NOT NULL,
                    costo_total REAL NOT NULL
                )
            """)

            # Tabla DETALLE_VENTA
            # Desglose por ítem de cada venta. Congela datos del producto
            # para preservar el historial ante modificaciones futuras.
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS DETALLE_VENTA (
                    id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_venta INTEGER NOT NULL,
                    id_producto INTEGER NOT NULL,
                    nombre_producto TEXT NOT NULL,
                    tipo_venta TEXT NOT NULL,
                    cantidad REAL NOT NULL,
                    precio_unitario_venta REAL NOT NULL,
                    precio_unitario_compra REAL NOT NULL,
                    subtotal REAL NOT NULL,
                    costo REAL NOT NULL,
                    FOREIGN KEY (id_venta) REFERENCES VENTAS (id_venta),
                    FOREIGN KEY (id_producto) REFERENCES PRODUCTOS (id_producto)
                )
            """)

            # Tabla CONFIGURACION
            # Almacén clave-valor para persistencia de configuración
            # del sistema (ej. hash del PIN de administrador, sal).
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS CONFIGURACION (
                    clave TEXT PRIMARY KEY,
                    valor TEXT NOT NULL
                )
            """)

            self.conexion.commit()
        except sqlite3.Error as e:
            print(f"Error al inicializar las tablas: {e}")
