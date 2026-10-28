import json
import mimetypes
import os
import threading
import webbrowser
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse


class Manejador(BaseHTTPRequestHandler):
    """Recibe cada peticion del navegador y la manda a la capa que corresponde."""

    carpeta_web = None
    auth = None
    finanzas = None

    def log_message(self, formato, *args):
        pass  # sin ruido en la terminal

    # ---------- utilidades ----------
    def _token(self):
        galleta = SimpleCookie(self.headers.get("Cookie", ""))
        return galleta["sid"].value if "sid" in galleta else None

    def _usuario(self):
        return self.auth.usuario_de(self._token())

    def _cuerpo(self):
        largo = int(self.headers.get("Content-Length") or 0)
        if largo == 0:
            return {}
        try:
            return json.loads(self.rfile.read(largo))
        except json.JSONDecodeError:
            raise ValueError("Datos invalidos.")

    def _responder(self, codigo, datos, cabeceras=()):
        cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        for nombre, valor in cabeceras:
            self.send_header(nombre, valor)
        self.end_headers()
        self.wfile.write(cuerpo)

    def _redirigir(self, destino):
        self.send_response(302)
        self.send_header("Location", destino)
        self.end_headers()

    # ---------- GET: paginas y estado ----------
    def do_GET(self):
        ruta = urlparse(self.path).path
        if ruta == "/api/estado":
            usuario = self._usuario()
            if not usuario:
                return self._responder(401, {"error": "Sesion no iniciada."})
            return self._responder(200, self.finanzas.estado(usuario))
        self._servir_archivo(ruta)

    def _servir_archivo(self, ruta):
        con_sesion = self._usuario() is not None
        if ruta == "/":
            return self._redirigir("/index.html" if con_sesion else "/login.html")
        if ruta == "/index.html" and not con_sesion:
            return self._redirigir("/login.html")  # la app no se abre sin login
        destino = os.path.realpath(os.path.join(self.carpeta_web, ruta.lstrip("/")))
        if not destino.startswith(os.path.realpath(self.carpeta_web)) or not os.path.isfile(destino):
            self.send_error(404, "No encontrado")
            return
        tipo = mimetypes.guess_type(destino)[0] or "application/octet-stream"
        with open(destino, "rb") as archivo:
            contenido = archivo.read()
        self.send_response(200)
        self.send_header("Content-Type", tipo + ("; charset=utf-8" if tipo.startswith("text") or "javascript" in tipo else ""))
        self.send_header("Content-Length", str(len(contenido)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(contenido)

    # ---------- POST: login y acciones ----------
    def do_POST(self):
        ruta = urlparse(self.path).path
        try:
            datos = self._cuerpo()
            if ruta in ("/api/login", "/api/registro"):
                metodo = self.auth.ingresar if ruta == "/api/login" else self.auth.registrar
                token = metodo(str(datos.get("usuario", "")), str(datos.get("clave", "")))
                galleta = f"sid={token}; HttpOnly; Path=/; SameSite=Lax"
                return self._responder(200, {"ok": True}, [("Set-Cookie", galleta)])
            if ruta == "/api/logout":
                self.auth.salir(self._token())
                return self._responder(200, {"ok": True}, [("Set-Cookie", "sid=; Max-Age=0; Path=/")])
            if ruta == "/api/accion":
                usuario = self._usuario()
                if not usuario:
                    return self._responder(401, {"error": "Sesion no iniciada."})
                return self._responder(200, self.finanzas.accion(usuario, datos))
            self._responder(404, {"error": "Ruta no encontrada."})
        except ValueError as error:
            self._responder(400, {"error": str(error)})


class Servidor:
    def __init__(self, carpeta_web, auth, finanzas, puerto=8000):
        Manejador.carpeta_web = carpeta_web
        Manejador.auth = auth
        Manejador.finanzas = finanzas
        self.puerto = puerto
        self.http = self._abrir_puerto()

    def _abrir_puerto(self):
        for puerto in range(self.puerto, self.puerto + 10):
            try:
                self.puerto = puerto
                return HTTPServer(("127.0.0.1", puerto), Manejador)
            except OSError:
                continue
        raise OSError("No hay puertos libres entre 8000 y 8009.")

    def iniciar(self):
        url = f"http://127.0.0.1:{self.puerto}/"
        print(f"Tu Finanzas esta corriendo en {url}")
        print("Para cerrar el programa presiona Ctrl+C en esta ventana.")
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
        try:
            self.http.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor cerrado.")
        finally:
            self.http.server_close()
