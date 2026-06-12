import sqlite3
import os


class BaseDatos:
    """Gestiona la conexión y operaciones con la base de datos SQLite.

    Responsabilidades:
    - Conexión/desconexión con integridad ACID (modo WAL).
    - Creación e inicialización de las 4 tablas del sistema.
    - Métodos auxiliares para ejecutar consultas de forma segura.

    Referencia SRS:
    - G-006: Un cierre inesperado no debe provocar pérdida de
      transacciones ya confirmadas ni productos dados de alta.
    - G-010: Toda la información se almacena y procesa de forma local.
    """

    def __init__(self, ruta_db="punto_venta.db"):
        self.ruta_db = ruta_db
        self.conexion = None
        self.cursor = None

    # ──────────────────────────────────────────────
    #  Conexión y desconexión
    # ──────────────────────────────────────────────

    def conectar(self):
        """Establece la conexión con la base de datos SQLite.

        Configuraciones aplicadas:
        - journal_mode=WAL: Write-Ahead Logging para integridad ACID.
          Garantiza que las transacciones confirmadas sobrevivan a un
          cierre inesperado de la aplicación (G-006).
        - foreign_keys=ON: Habilita la verificación de claves foráneas
          para mantener la integridad referencial entre tablas.
        - row_factory=sqlite3.Row: Permite acceder a las columnas por
          nombre en lugar de por índice numérico.
        """
        try:
            self.conexion = sqlite3.connect(self.ruta_db)
            self.conexion.row_factory = sqlite3.Row
            self.cursor = self.conexion.cursor()

            # WAL (Write-Ahead Logging): las escrituras van primero a un
            # archivo temporal (-wal). Si la app se cierra abruptamente,
            # SQLite recupera los datos automáticamente al reconectar.
            self.cursor.execute("PRAGMA journal_mode=WAL")

            # Habilitar claves foráneas (desactivadas por defecto en SQLite)
            self.cursor.execute("PRAGMA foreign_keys=ON")

        except sqlite3.Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            raise

    def desconectar(self):
        """Cierra la conexión con la base de datos de forma segura.

        Realiza un commit de cualquier transacción pendiente antes
        de cerrar para evitar pérdida de datos.
        """
        if self.conexion:
            try:
                self.conexion.commit()
                self.conexion.close()
            except sqlite3.Error as e:
                print(f"Error al desconectar de la base de datos: {e}")
            finally:
                self.conexion = None
                self.cursor = None

    def _asegurar_conexion(self):
        """Verifica que exista una conexión activa; si no, la establece."""
        if not self.conexion:
            self.conectar()

    # ──────────────────────────────────────────────
    #  Inicialización de tablas
    # ──────────────────────────────────────────────

    def inicializar_tablas(self):
        """Crea las 4 tablas del sistema si no existen.

        Tablas:
        - PRODUCTOS: Catálogo de artículos de la tienda.
        - VENTAS: Encabezados de transacciones confirmadas.
        - DETALLE_VENTA: Desglose por ítem con datos congelados.
        - CONFIGURACION: Almacén clave-valor (PIN, sal, etc.).
        """
        self._asegurar_conexion()

        try:
            # ── Tabla PRODUCTOS ──
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

            # ── Tabla VENTAS ──
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

            # ── Tabla DETALLE_VENTA ──
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

            # ── Tabla CONFIGURACION ──
            # Almacén clave-valor para persistencia de configuración
            # del sistema (ej. admin_pin_hash, admin_pin_salt).
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS CONFIGURACION (
                    clave TEXT PRIMARY KEY,
                    valor TEXT NOT NULL
                )
            """)

            self.conexion.commit()
        except sqlite3.Error as e:
            print(f"Error al inicializar las tablas: {e}")
            raise

    # ──────────────────────────────────────────────
    #  Métodos auxiliares de ejecución
    # ──────────────────────────────────────────────

    def ejecutar(self, sql, parametros=None):
        """Ejecuta una sentencia SQL y hace commit automáticamente.

        Args:
            sql: Sentencia SQL a ejecutar.
            parametros: Tupla con los valores para los placeholders (?).

        Returns:
            El cursor después de la ejecución (útil para lastrowid).
        """
        self._asegurar_conexion()
        try:
            if parametros:
                self.cursor.execute(sql, parametros)
            else:
                self.cursor.execute(sql)
            self.conexion.commit()
            return self.cursor
        except sqlite3.Error as e:
            self.conexion.rollback()
            print(f"Error al ejecutar consulta: {e}")
            raise

    def consultar(self, sql, parametros=None):
        """Ejecuta una consulta SELECT y retorna todas las filas.

        Args:
            sql: Sentencia SELECT a ejecutar.
            parametros: Tupla con los valores para los placeholders (?).

        Returns:
            Lista de filas (sqlite3.Row) con los resultados.
        """
        self._asegurar_conexion()
        try:
            if parametros:
                self.cursor.execute(sql, parametros)
            else:
                self.cursor.execute(sql)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error al consultar: {e}")
            raise

    def consultar_uno(self, sql, parametros=None):
        """Ejecuta una consulta SELECT y retorna solo la primera fila.

        Args:
            sql: Sentencia SELECT a ejecutar.
            parametros: Tupla con los valores para los placeholders (?).

        Returns:
            Una fila (sqlite3.Row) o None si no hay resultados.
        """
        self._asegurar_conexion()
        try:
            if parametros:
                self.cursor.execute(sql, parametros)
            else:
                self.cursor.execute(sql)
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error al consultar: {e}")
            raise

    "Funciones para SHA-256"

    def obtener_configuracion(self, clave: str) -> str:
        """Busca una configuración en la tabla por su clave única."""
        self.conectar()
        cursor = self.conexion.cursor()
        cursor.execute("SELECT valor FROM CONFIGURACION WHERE clave = ?;", (clave,))
        resultado = cursor.fetchone()
        self.desconectar()
        
        return resultado["valor"] if resultado else None

    def guardar_configuracion(self, clave: str, valor: str):
        """Inserta o reemplaza una configuración clave-valor."""
        self.conectar()
        cursor = self.conexion.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO CONFIGURACION (clave, valor) 
            VALUES (?, ?);
        """, (clave, valor))
        self.conexion.commit()
        self.desconectar()
