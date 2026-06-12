import hashlib
import os
from datos.base_datos import BaseDatos

class GestorAutenticacion:
    def __init__(self, db: BaseDatos):
        self.db = db

    "generar_sal hashear_pin pin_configurado conforman la tarea 'SHA-256 con sal'"

    def _generar_sal(self) -> bytes:
        return os.urandom(16)

    def _hashear_pin(self, pin: str, sal: bytes) -> str:
        hash_objeto = hashlib.sha256()
        hash_objeto.update(sal + pin.encode('utf-8'))
        return hash_objeto.hexdigest()

    def pin_configurado(self) -> bool:

        hash_existente = self.db.obtener_configuracion("admin_pin_hash")
        return hash_existente is not None and hash_existente != ""

    def configurar_pin(self, pin: str) -> bool:
        if self.pin_configurado() or len(pin) != 6 or not pin.isdigit():
            return False
        
        sal_bytes = self._generar_sal()
        sal_hex = sal_bytes.hex()
        hash_hex = self._hashear_pin(pin, sal_bytes)
        
        self.db.guardar_configuracion("admin_pin_hash", hash_hex)
        self.db.guardar_configuracion("admin_pin_salt", sal_hex)
        return True

    def verificar_pin(self, pin: str) -> bool:
        if not self.pin_configurado():
            return False
            
        hash_guardado = self.db.obtener_configuracion("admin_pin_hash")
        sal_guardada_hex = self.db.obtener_configuracion("admin_pin_salt")
        
        sal_bytes = bytes.fromhex(sal_guardada_hex)
        hash_calculado = self._hashear_pin(pin, sal_bytes)
        
        return hash_calculado == hash_guardado