// Vista del login: solo envia los datos al servidor (capa de login en Python).
const campoUsuario = document.getElementById("usuario");
const campoClave = document.getElementById("clave");
const textoError = document.getElementById("error");

async function enviar(ruta) {
  textoError.textContent = "";
  try {
    const respuesta = await fetch(ruta, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ usuario: campoUsuario.value, clave: campoClave.value })
    });
    const datos = await respuesta.json();
    if (!respuesta.ok) throw new Error(datos.error || "No se pudo completar.");
    window.location.href = "/index.html";
  } catch (error) {
    textoError.textContent = error.message;
  }
}

document.getElementById("entrar").addEventListener("click", () => enviar("/api/login"));
document.getElementById("crear").addEventListener("click", () => enviar("/api/registro"));
campoClave.addEventListener("keydown", e => { if (e.key === "Enter") enviar("/api/login"); });
