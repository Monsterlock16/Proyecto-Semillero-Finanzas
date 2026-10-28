from datetime import date, timedelta

from modelo.modelos import Gasto, Suscripcion

CATEGORIAS = ["Alimentación", "Transporte", "Otros"]


class GestorFinanzas:
    """Logica del negocio: calculos, alertas y manejo de las listas."""

    def __init__(self, suscripciones=None, gastos=None):
        self.suscripciones = suscripciones or []
        self.gastos = gastos or []
        self.dias_alerta = 3

    # ---- altas y bajas ----
    def agregar_suscripcion(self, nombre, valor, dia_cobro):
        if valor <= 0:
            raise ValueError("El valor debe ser mayor a cero.")
        if not 1 <= dia_cobro <= 31:
            raise ValueError("El dia de cobro debe estar entre 1 y 31.")
        self.suscripciones.append(Suscripcion(nombre, valor, dia_cobro))

    def eliminar_suscripcion(self, indice):
        return self.suscripciones.pop(indice)

    def cambiar_estado(self, indice):
        self.suscripciones[indice].cambiar_estado()
        return self.suscripciones[indice]

    def agregar_gasto(self, categoria, descripcion, valor):
        if valor <= 0:
            raise ValueError("El valor debe ser mayor a cero.")
        self.gastos.append(Gasto(categoria, descripcion, valor))

    def eliminar_gasto(self, indice):
        return self.gastos.pop(indice)

    # ---- calculos ----
    def total_suscripciones(self):
        return sum(s.valor for s in self.suscripciones if s.activa)

    def total_otros_gastos(self):
        return sum(g.valor for g in self.gastos)

    def gasto_mensual(self):
        return self.total_suscripciones() + self.total_otros_gastos()

    def proyeccion_anual(self):
        return self.gasto_mensual() * 12

    def ahorro_si_cancela(self):
        """Lo que se ahorraria al ano si se cancelaran las suscripciones apagadas."""
        return sum(s.valor for s in self.suscripciones if not s.activa) * 12

    def gastos_por_categoria(self):
        total = self.gasto_mensual()
        resultado = {"Suscripciones": self.total_suscripciones()}
        for g in self.gastos:
            resultado[g.categoria] = resultado.get(g.categoria, 0) + g.valor
        # se devuelve (valor, porcentaje) por categoria
        return {
            nombre: (valor, (valor / total * 100) if total else 0)
            for nombre, valor in resultado.items()
        }

    def alertas(self, dias=None):
        dias = dias or self.dias_alerta
        proximas = [
            s for s in self.suscripciones
            if s.activa and s.dias_para_cobro() <= dias
        ]
        return sorted(proximas, key=lambda s: s.dias_para_cobro())

    def datos_ejemplo(self):
        # el cobro de Spotify queda a dos dias para que se vea una alerta de ejemplo
        self.agregar_suscripcion("Spotify", 19900, (date.today() + timedelta(days=2)).day)
        self.agregar_suscripcion("Netflix", 24900, 15)
        self.agregar_suscripcion("Dropbox", 11900, 20)
        self.suscripciones[2].activa = False
        self.agregar_gasto("Alimentación", "Mercado del mes", 64000)
        self.agregar_gasto("Transporte", "Transmilenio", 48000)
        self.agregar_gasto("Otros", "Salidas", 64000)
