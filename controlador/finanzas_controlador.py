import os

from modelo.almacenamiento import AlmacenJSON
from modelo.gestor import CATEGORIAS, GestorFinanzas


class FinanzasControlador:
    """Capa de finanzas: solo se llega aqui despues de pasar por el login."""

    def __init__(self, carpeta_datos):
        self.carpeta = carpeta_datos
        self.usuarios = {}  # usuario -> (gestor, almacen)

    def _cargar(self, usuario):
        if usuario not in self.usuarios:
            almacen = AlmacenJSON(os.path.join(self.carpeta, f"{usuario}.json"))
            gestor = GestorFinanzas()
            if almacen.existe():
                gestor.suscripciones, gestor.gastos, gestor.dias_alerta = almacen.cargar()
            else:
                gestor.datos_ejemplo()
                almacen.guardar(gestor.suscripciones, gestor.gastos, gestor.dias_alerta)
            self.usuarios[usuario] = (gestor, almacen)
        return self.usuarios[usuario]

    def estado(self, usuario):
        g, _ = self._cargar(usuario)
        return {
            "usuario": usuario,
            "categorias": CATEGORIAS,
            "diasAlerta": g.dias_alerta,
            "mensual": g.gasto_mensual(),
            "anual": g.proyeccion_anual(),
            "porCategoria": [{"nombre": n, "valor": v, "pct": p}
                             for n, (v, p) in g.gastos_por_categoria().items()],
            "suscripciones": [{
                "nombre": s.nombre, "valor": s.valor, "dia": s.dia_cobro, "activa": s.activa,
                "proximo": s.proximo_cobro().strftime("%d/%m/%Y"),
            } for s in g.suscripciones],
            "gastos": [g2.to_dict() for g2 in g.gastos],
            "alertas": [{
                "nombre": s.nombre, "valor": s.valor, "dias": s.dias_para_cobro(),
                "fecha": s.proximo_cobro().strftime("%d/%m/%Y"),
            } for s in g.alertas()],
        }

    def accion(self, usuario, datos):
        g, almacen = self._cargar(usuario)
        tipo = datos.get("accion")
        if tipo == "addSub":
            nombre = str(datos.get("nombre", "")).strip()
            if not nombre:
                raise ValueError("El nombre no puede estar vacio.")
            g.agregar_suscripcion(nombre, self._numero(datos.get("valor")), self._numero(datos.get("dia")))
        elif tipo == "alternar":
            g.cambiar_estado(self._indice(datos, g.suscripciones))
        elif tipo == "borrarSub":
            g.eliminar_suscripcion(self._indice(datos, g.suscripciones))
        elif tipo == "addGasto":
            descripcion = str(datos.get("descripcion", "")).strip()
            if not descripcion:
                raise ValueError("La descripcion no puede estar vacia.")
            g.agregar_gasto(str(datos.get("categoria", "Otros")), descripcion, self._numero(datos.get("valor")))
        elif tipo == "borrarGasto":
            g.eliminar_gasto(self._indice(datos, g.gastos))
        elif tipo == "guardarDias":
            g.dias_alerta = max(1, min(15, self._numero(datos.get("dias"))))
        elif tipo == "reiniciar":
            g.suscripciones.clear()
            g.gastos.clear()
            g.dias_alerta = 3
            g.datos_ejemplo()
        else:
            raise ValueError("Accion desconocida.")
        almacen.guardar(g.suscripciones, g.gastos, g.dias_alerta)
        return self.estado(usuario)

    @staticmethod
    def _numero(valor):
        try:
            return int(str(valor).replace(".", "").replace(",", "").strip())
        except ValueError:
            raise ValueError("Escribe solo numeros en los campos numericos.")

    @staticmethod
    def _indice(datos, lista):
        indice = datos.get("indice")
        if not isinstance(indice, int) or not 0 <= indice < len(lista):
            raise ValueError("Elemento no encontrado.")
        return indice
