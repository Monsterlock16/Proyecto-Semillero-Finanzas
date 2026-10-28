import json
import os

from modelo.modelos import Gasto, Suscripcion


class AlmacenJSON:
    """Guarda y lee los datos de un usuario en un archivo JSON."""

    def __init__(self, ruta):
        self.ruta = ruta

    def existe(self):
        return os.path.exists(self.ruta)

    def cargar(self):
        with open(self.ruta, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        suscripciones = [Suscripcion.from_dict(s) for s in datos.get("suscripciones", [])]
        gastos = [Gasto.from_dict(g) for g in datos.get("gastos", [])]
        return suscripciones, gastos, datos.get("dias_alerta", 3)

    def guardar(self, suscripciones, gastos, dias_alerta):
        os.makedirs(os.path.dirname(self.ruta), exist_ok=True)
        datos = {
            "suscripciones": [s.to_dict() for s in suscripciones],
            "gastos": [g.to_dict() for g in gastos],
            "dias_alerta": dias_alerta,
        }
        with open(self.ruta, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)
