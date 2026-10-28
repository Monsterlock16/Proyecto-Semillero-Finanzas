import secrets


class AuthControlador:
    """Capa de login: decide quien entra y mantiene las sesiones abiertas."""

    def __init__(self, repositorio):
        self.repositorio = repositorio
        self.sesiones = {}  # token -> usuario

    def registrar(self, usuario, clave):
        usuario = self.repositorio.registrar(usuario, clave)
        return self._abrir_sesion(usuario)

    def ingresar(self, usuario, clave):
        if not self.repositorio.verificar(usuario, clave):
            raise ValueError("Usuario o clave incorrectos.")
        return self._abrir_sesion(usuario.strip().lower())

    def usuario_de(self, token):
        return self.sesiones.get(token)

    def salir(self, token):
        self.sesiones.pop(token, None)

    def _abrir_sesion(self, usuario):
        token = secrets.token_hex(24)
        self.sesiones[token] = usuario
        return token
