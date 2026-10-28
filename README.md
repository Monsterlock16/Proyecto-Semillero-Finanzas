# Tu Finanzas (demo web)

Ejecutar: python main.py  (se abre el navegador solo, no hay que instalar nada)

Capas (cada una llama a la siguiente):
main.py -> servidor/servidor.py -> controlador/auth_controlador.py (login)
        -> controlador/finanzas_controlador.py -> modelo/ (gestor, almacenamiento, usuarios)

La vista es la carpeta web/ (login.html, index.html, css/estilos.css, js/login.js, js/app.js).
Los datos de cada usuario quedan en datos/ (se crea sola al correr).
