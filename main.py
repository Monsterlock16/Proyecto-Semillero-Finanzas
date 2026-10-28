"""Punto de entrada. Capas: main -> servidor -> login -> finanzas -> modelo."""
import os

from controlador.auth_controlador import AuthControlador
from controlador.finanzas_controlador import FinanzasControlador
from modelo.usuarios import RepositorioUsuarios
from servidor.servidor import Servidor


def main():
    carpeta = os.path.dirname(os.path.abspath(__file__))
    datos = os.path.join(carpeta, "datos")

    auth = AuthControlador(RepositorioUsuarios(os.path.join(datos, "usuarios.json")))
    finanzas = FinanzasControlador(datos)
    Servidor(os.path.join(carpeta, "web"), auth, finanzas).iniciar()


if __name__ == "__main__":
    main()
