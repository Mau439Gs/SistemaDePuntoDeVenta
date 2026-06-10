import sqlite3

class BaseDatos:
    def __init__(self, ruta_db="punto_venta.db"):
        self.ruta_db = ruta_db
        self.conexion = None
        self.cursor = None

    def conectar(self):
        try:
            self.conexion = sqlite3.connect(self.ruta_db)
            self.conexion.row_factory = sqlite3.Row
            self.cursor = self.conexion.cursor()
            # Habilitar el modo WAL para mejor concurrencia e integridad ACID
            self.cursor.execute("PRAGMA journal_mode=WAL")
        except sqlite3.Error as e:
            print(f"Error al conectar a la base de datos: {e}")

    def desconectar(self):
        if self.conexion:
            self.conexion.close()

    def inicializar_tablas(self):
        if not self.conexion:
            self.conectar()
            
        try:
            # Tabla PRODUCTOS
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS PRODUCTOS (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    tipo_venta TEXT NOT NULL,
                    precio_compra REAL NOT NULL,
                    precio_venta REAL NOT NULL,
                    stock_minimo REAL NOT NULL,
                    stock_actual REAL NOT NULL
                )
            """)

            # Tabla VENTAS
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS VENTAS (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha_hora TEXT NOT NULL,
                    total REAL NOT NULL,
                    monto_recibido REAL NOT NULL,
                    cambio REAL NOT NULL
                )
            """)

            # Tabla DETALLE_VENTA
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS DETALLE_VENTA (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venta_id INTEGER NOT NULL,
                    producto_id INTEGER NOT NULL,
                    cantidad REAL NOT NULL,
                    precio_unitario REAL NOT NULL,
                    subtotal REAL NOT NULL,
                    FOREIGN KEY (venta_id) REFERENCES VENTAS (id),
                    FOREIGN KEY (producto_id) REFERENCES PRODUCTOS (id)
                )
            """)

            # Tabla CONFIGURACION (ej. para el PIN del admin)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS CONFIGURACION (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    clave TEXT NOT NULL UNIQUE,
                    valor TEXT NOT NULL
                )
            """)

            self.conexion.commit()
        except sqlite3.Error as e:
            print(f"Error al inicializar las tablas: {e}")
