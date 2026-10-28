// ===================== MODELO =====================
// Ya no calcula nada: guarda el estado que entrega el servidor (Python).
class Modelo {
  constructor() { this.e = null; }
  async pedir(url, opciones = {}) {
    const respuesta = await fetch(url, { headers: { "Content-Type": "application/json" }, ...opciones });
    if (respuesta.status === 401) { window.location.href = "/login.html"; throw new Error("Sesión vencida."); }
    const datos = await respuesta.json();
    if (!respuesta.ok) throw new Error(datos.error || "Error del servidor.");
    return datos;
  }
  async cargar() { this.e = await this.pedir("/api/estado"); }
  async accion(datos) { this.e = await this.pedir("/api/accion", { method: "POST", body: JSON.stringify(datos) }); }
  async salir() { await this.pedir("/api/logout", { method: "POST", body: "{}" }); window.location.href = "/login.html"; }
  get usuario() { return this.e.usuario; }
  get categorias() { return this.e.categorias; }
  get suscripciones() { return this.e.suscripciones; }
  get gastos() { return this.e.gastos; }
  get diasAlerta() { return this.e.diasAlerta; }
  gastoMensual() { return this.e.mensual; }
  proyeccionAnual() { return this.e.anual; }
  porCategoria() { return this.e.porCategoria; }
  alertas() { return this.e.alertas; }
}

// ===================== VISTA =====================
const PALETA = ["#93c5fd", "#c4b5fd", "#86efac", "#fde68a", "#fca5a5", "#fdba74"];
const plata = n => "$ " + Number(n).toLocaleString("es-CO");
const esc = t => String(t).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fecha = d => d.toLocaleDateString("es-CO");

class Vista {
  constructor() {
    this.menu = document.getElementById("menu");
    this.cont = document.getElementById("contenido");
    this.secciones = [["inicio", "Inicio"], ["suscripciones", "Suscripciones"], ["resumen", "Resumen"],
                      ["alertas", "Alertas"], ["config", "Configuración"]];
  }
  alClick(manejador) {
    document.addEventListener("click", e => {
      const el = e.target.closest("[data-a]");
      if (el) manejador(el.dataset.a, el.dataset.i);
    });
  }
  valor(id) { return document.getElementById(id).value.trim(); }
  mensaje(texto) {
    const m = document.getElementById("msg");
    m.textContent = texto; m.style.display = "block";
    setTimeout(() => { m.style.display = "none"; }, 2800);
  }
  saludo(usuario) { document.getElementById("saludo").textContent = `Hola, ${usuario}`; }
  confirmar(texto) { return window.confirm(texto); }
  pintarMenu(actual, cantidad) {
    this.menu.innerHTML = this.secciones.map(([id, nombre]) =>
      `<button class="${id === actual ? "act" : ""}" data-a="ir" data-i="${id}">${nombre}</button>`).join("");
    document.getElementById("campana").textContent = `Alertas (${cantidad})`;
  }
  torta(cats) {
    let acum = 0;
    const tramos = cats.map((c, i) => {
      const ini = acum; acum += c.pct;
      return `${PALETA[i % PALETA.length]} ${ini}% ${acum}%`;
    }).join(",");
    const ley = cats.map((c, i) => `<div><i style="background:${PALETA[i % PALETA.length]}"></i>${esc(c.nombre)} ${c.pct.toFixed(0)}%</div>`).join("");
    return `<div class="torta"><div class="pie" style="background:conic-gradient(${tramos || "var(--borde) 0 100%"})"></div><div class="ley">${ley}</div></div>`;
  }
  interruptores(subs) {
    return subs.map((s, i) => `<div class="fila"><div><b>${esc(s.nombre)}</b><small>${plata(s.valor)} / mes</small></div>
      <button class="sw ${s.activa ? "on" : ""}" data-a="alternar" data-i="${i}" aria-label="Activar o desactivar ${esc(s.nombre)}"></button></div>`).join("")
      || "<p>Aún no tienes suscripciones.</p>";
  }
  inicio(m) {
    this.cont.innerHTML = `<h2>¡Bienvenido!</h2><p class="sub">Aquí puedes ver un resumen de tus gastos y suscripciones.</p>
      <div class="tarjetas">
        <div class="tarjeta"><b>Gasto mensual</b><div class="n">${plata(m.gastoMensual())}</div><small>Total estimado</small></div>
        <div class="tarjeta"><b>Proyección anual</b><div class="n">${plata(m.proyeccionAnual())}</div><small>Si mantienes tus suscripciones</small></div>
        <div class="tarjeta"><b>Alertas activas</b><div class="n">${m.alertas().length}</div><small>Antes de próximos cobros</small></div>
      </div>
      <div class="dos"><div class="panel"><h3>Tus gastos por categoría</h3>${this.torta(m.porCategoria())}</div>
      <div class="panel"><h3>Suscripciones activas</h3>${this.interruptores(m.suscripciones)}</div></div>
      <div class="aviso">Recuerda: cancelar a tiempo tus suscripciones te ayuda a ahorrar y usar mejor tu dinero.</div>`;
  }
  suscripciones(m) {
    const filas = m.suscripciones.map((s, i) => `<tr><td>${esc(s.nombre)}</td><td>${plata(s.valor)}</td><td>${s.dia}</td>
      <td>${s.proximo}</td>
      <td><button class="sw ${s.activa ? "on" : ""}" data-a="alternar" data-i="${i}" aria-label="Cambiar estado"></button></td>
      <td><button class="btn rojo chico" data-a="borrarSub" data-i="${i}">Eliminar</button></td></tr>`).join("");
    this.cont.innerHTML = `<h2>Suscripciones</h2><p class="sub">Administra tus cobros recurrentes.</p>
      <div class="panel"><div class="form"><input id="sNombre" placeholder="Nombre"><input id="sValor" type="number" placeholder="Valor mensual">
      <input id="sDia" type="number" placeholder="Día de cobro (1-31)"><button class="btn" data-a="addSub">Agregar</button></div>
      <table class="tabla"><tr><th>Nombre</th><th>Valor</th><th>Día</th><th>Próximo cobro</th><th>Activa</th><th></th></tr>${filas}</table></div>`;
  }
  resumen(m) {
    const filas = m.gastos.map((g, i) => `<tr><td>${esc(g.categoria)}</td><td>${esc(g.descripcion)}</td><td>${plata(g.valor)}</td>
      <td><button class="btn rojo chico" data-a="borrarGasto" data-i="${i}">Eliminar</button></td></tr>`).join("");
    const opciones = m.categorias.map(c => `<option>${c}</option>`).join("");
    this.cont.innerHTML = `<h2>Resumen</h2><p class="sub">Gasto mensual total: ${plata(m.gastoMensual())}</p>
      <div class="dos"><div class="panel"><h3>Por categoría</h3>${this.torta(m.porCategoria())}</div>
      <div class="panel"><h3>Gastos registrados</h3><div class="form"><select id="gCat">${opciones}</select>
      <input id="gDesc" placeholder="Descripción"><input id="gValor" type="number" placeholder="Valor"><button class="btn" data-a="addGasto">Registrar</button></div>
      <table class="tabla"><tr><th>Categoría</th><th>Descripción</th><th>Valor</th><th></th></tr>${filas}</table></div></div>`;
  }
  alertas(m) {
    const lista = m.alertas().map(s => {
      const d = s.dias;
      return `<div class="panel alerta" style="margin-bottom:10px"><b>${esc(s.nombre)} cobra ${plata(s.valor)} ${d === 0 ? "hoy" : "en " + d + " día(s)"}</b><br><small>Fecha: ${s.fecha}</small></div>`;
    }).join("");
    this.cont.innerHTML = `<h2>Alertas</h2><p class="sub">Cobros que llegan en los próximos ${m.diasAlerta} día(s).</p>${lista || "<p>No tienes cobros cercanos.</p>"}`;
  }
  config(m) {
    this.cont.innerHTML = `<h2>Configuración</h2><p class="sub">Ajusta el demo a tu gusto.</p>
      <div class="panel"><h3>Alertas</h3><div class="form"><label>Avisarme con (días) de anticipación:</label>
      <input id="cDias" type="number" min="1" max="15" value="${m.diasAlerta}"><button class="btn" data-a="guardarDias">Guardar</button></div></div>
      <div class="panel" style="margin-top:14px"><h3>Datos</h3><button class="btn rojo" data-a="reiniciar">Restablecer datos de ejemplo</button></div>`;
  }
}

// ===================== CONTROLADOR =====================
class Controlador {
  constructor(modelo, vista) {
    this.m = modelo; this.v = vista; this.pantalla = "inicio";
    this.v.alClick((accion, dato) => this.manejar(accion, dato));
    this.iniciar();
  }
  async iniciar() {
    try { await this.m.cargar(); this.ir("inicio"); } catch (error) { this.v.mensaje(error.message); }
  }
  ir(pantalla) {
    this.pantalla = pantalla;
    this.v[pantalla](this.m);
    this.v.pintarMenu(pantalla, this.m.alertas().length);
    this.v.saludo(this.m.usuario);
  }
  async manejar(accion, dato) {
    try {
      const i = Number(dato);
      if (accion === "ir") return this.ir(dato);
      if (accion === "salir") return this.m.salir();
      if (accion === "borrarSub" && !this.v.confirmar("¿Eliminar esta suscripción?")) return;
      if (accion === "reiniciar" && !this.v.confirmar("Se borrarán tus datos. ¿Continuar?")) return;
      const cargas = {
        alternar: () => ({ indice: i }),
        borrarSub: () => ({ indice: i }),
        borrarGasto: () => ({ indice: i }),
        addSub: () => ({ nombre: this.v.valor("sNombre"), valor: this.v.valor("sValor"), dia: this.v.valor("sDia") }),
        addGasto: () => ({ categoria: this.v.valor("gCat"), descripcion: this.v.valor("gDesc"), valor: this.v.valor("gValor") }),
        guardarDias: () => ({ dias: this.v.valor("cDias") }),
        reiniciar: () => ({})
      };
      await this.m.accion({ accion, ...cargas[accion]() });
      if (accion === "guardarDias") this.v.mensaje("Configuración guardada.");
      this.ir(this.pantalla);
    } catch (error) {
      this.v.mensaje(error.message);
    }
  }
}

new Controlador(new Modelo(), new Vista());
