import hashlib
import hmac
import json
import os
import re


class RepositorioUsuarios:
    """Guarda los usuarios con la clave cifrada (nunca en texto plano)."""

    def __init__(self, ruta):
        self.ruta = ruta
        self.usuarios = self._leer()

    def _leer(self):
        if not os.path.exists(self.ruta):
            return {}
        with open(self.ruta, "r", encoding="utf-8") as archivo:
            return json.load(archivo)

    def _guardar(self):
        os.makedirs(os.path.dirname(self.ruta), exist_ok=True)
        with open(self.ruta, "w", encoding="utf-8") as archivo:
            json.dump(self.usuarios, archivo, indent=4)

    @staticmethod
    def _cifrar(clave, sal):
        return hashlib.pbkdf2_hmac("sha256", clave.encode("utf-8"), sal, 100_000).hex()

    def registrar(self, usuario, clave):
        usuario = usuario.strip().lower()
        if not re.fullmatch(r"[a-z0-9_]{3,20}", usuario):
            raise ValueError("El usuario debe tener de 3 a 20 letras, numeros o guion bajo.")
        if len(clave) < 4:
            raise ValueError("La clave debe tener minimo 4 caracteres.")
        if usuario in self.usuarios:
            raise ValueError("Ese usuario ya existe.")
        sal = os.urandom(16)
        self.usuarios[usuario] = {"sal": sal.hex(), "hash": self._cifrar(clave, sal)}
        self._guardar()
        return usuario

    def verificar(self, usuario, clave):
        datos = self.usuarios.get(usuario.strip().lower())
        if not datos:
            return False
        calculado = self._cifrar(clave, bytes.fromhex(datos["sal"]))
        return hmac.compare_digest(calculado, datos["hash"])
