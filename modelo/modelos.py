import calendar
from datetime import date


class Suscripcion:
    def __init__(self, nombre, valor, dia_cobro, activa=True):
        self.nombre = nombre
        self.valor = valor
        self.dia_cobro = dia_cobro
        self.activa = activa

    def cambiar_estado(self):
        self.activa = not self.activa

    def proximo_cobro(self, hoy=None):
        hoy = hoy or date.today()
        ultimo_dia = calendar.monthrange(hoy.year, hoy.month)[1]
        dia = min(self.dia_cobro, ultimo_dia)
        if dia >= hoy.day:
            return date(hoy.year, hoy.month, dia)
        # el cobro de este mes ya paso, toca el del mes siguiente
        mes = hoy.month + 1 if hoy.month < 12 else 1
        anio = hoy.year if hoy.month < 12 else hoy.year + 1
        ultimo_dia = calendar.monthrange(anio, mes)[1]
        return date(anio, mes, min(self.dia_cobro, ultimo_dia))

    def dias_para_cobro(self, hoy=None):
        hoy = hoy or date.today()
        return (self.proximo_cobro(hoy) - hoy).days

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "valor": self.valor,
            "dia_cobro": self.dia_cobro,
            "activa": self.activa,
        }

    @classmethod
    def from_dict(cls, datos):
        return cls(datos["nombre"], datos["valor"], datos["dia_cobro"], datos["activa"])


class Gasto:
    def __init__(self, categoria, descripcion, valor):
        self.categoria = categoria
        self.descripcion = descripcion
        self.valor = valor

    def to_dict(self):
        return {
            "categoria": self.categoria,
            "descripcion": self.descripcion,
            "valor": self.valor,
        }

    @classmethod
    def from_dict(cls, datos):
        return cls(datos["categoria"], datos["descripcion"], datos["valor"])
