# Subir el proyecto a GitHub y activar las cotizaciones

Este paquete incluye la corrección de Prodem, los workflows de actualización automática
y manual, la publicación explícita en GitHub Pages y las pruebas individuales.

## 1. Descomprimir

Descomprime el ZIP. La carpeta `cotizacion` contiene el proyecto. No subas el archivo
ZIP a GitHub: sube los archivos descomprimidos. Comprueba que exista la carpeta oculta
`.github/workflows/` con cuatro archivos YAML. Usa Git o GitHub Desktop para incluirla.

## 2A. Si ya tienes un repositorio funcionando

1. Abre la copia local de tu repositorio (o clónalo con GitHub Desktop).
2. Copia del paquete `actualizar.py`, `bancos.py`, `requirements.txt`,
   `index.template.html`, `README.md`, `INSTRUCCIONES_GITHUB.md`, `.gitignore`,
   `.github/` y `pruebas/`, aceptando reemplazar los archivos del mismo nombre.
3. **Conserva la carpeta `docs/` del repositorio existente**: contiene tu historial real.
   No la reemplaces con los datos de ejemplo del paquete.
4. En GitHub Desktop, selecciona la rama `main`, escribe un mensaje como
   "Corregir captura Prodem y publicación Pages", pulsa **Commit to main** y **Push origin**.

Alternativa por terminal, dentro de tu copia local del repositorio:

```powershell
git switch main
git add actualizar.py bancos.py requirements.txt index.template.html README.md INSTRUCCIONES_GITHUB.md .gitignore .github pruebas
git commit -m "Corregir captura Prodem y publicación Pages"
git push origin main
```

## 2B. Si vas a crear un repositorio nuevo

1. En GitHub, crea un repositorio **público**, por ejemplo `tipo-cambio-bolivia`.
   Déjalo vacío: no selecciones README, licencia ni .gitignore al crearlo.
2. Instala Git o usa GitHub Desktop. Abre una terminal en la carpeta descomprimida
   `cotizacion`, donde están `actualizar.py` y `bancos.py`.
3. Ejecuta lo siguiente, sustituyendo `TU_USUARIO` y el nombre del repositorio:

```powershell
git init -b main
git add .
git commit -m "Publicar cotizaciones de bancos de Bolivia"
git remote add origin https://github.com/TU_USUARIO/tipo-cambio-bolivia.git
git push -u origin main
```

Autentícate con el navegador/Git Credential Manager cuando Git lo solicite.
Si pide identidad para el commit, configura tu nombre y correo de Git.
Los datos e historiales incluidos son una copia previa; la primera actualización
exitosa consultará las tasas actuales. No los interpretes como cotizaciones en vivo.

## 3. Configurar Actions y Pages (también para repositorios existentes)

1. En el repositorio, abre **Settings → Actions → General**. Permite GitHub Actions
   y las acciones oficiales de GitHub. En **Workflow permissions**, selecciona
   **Read and write permissions** y guarda.
2. Abre **Settings → Pages → Build and deployment** y selecciona
   **Source: GitHub Actions**. Cambia esta opción si antes usabas "Deploy from a branch".
3. Usa `main` como rama predeterminada. Si tu repositorio usa `master` u otra rama,
   adapta las referencias `main` en el workflow de publicación y en el formulario
   de `index.template.html`, o cambia la rama a `main`.
4. Si hay reglas que impiden a Actions escribir en `main`, configura una excepción
   adecuada para el bot; el flujo necesita guardar las consultas en esa rama.

El token automático `GITHUB_TOKEN` lo proporciona GitHub: no crees secretos para
la consulta periódica ni para publicar Pages. El workflow instala Python,
dependencias y Chromium para los bancos que usan JavaScript. Prodem usa HTTP.

## 4. Primera ejecución y comprobación

1. Abre **Actions → Actualizar tipo de cambio → Run workflow**, selecciona `main`
   y ejecútalo.
2. Espera a que terminen los jobs **actualizar** y **publicar**. En la salida de
   "Obtener tipos de cambio", busca `[OK] prodem` y el resumen de los 14 bancos.
3. Si el resumen muestra fallos, consulta cada línea `[FALLO]`: el job puede salir
   exitoso si al menos un banco funciona, conservando las tasas anteriores de los demás.
4. Abre **Settings → Pages → Visit site**, o entra a:

```text
https://TU_USUARIO.github.io/tipo-cambio-bolivia/
https://TU_USUARIO.github.io/tipo-cambio-bolivia/prodem.txt
https://TU_USUARIO.github.io/tipo-cambio-bolivia/todos.json
```

5. Confirma que Prodem tenga compra, venta, oficial y `origen=automatico`, con una
   fecha reciente. El historial estará en `historial/prodem.jsonl`.

Las próximas consultas están programadas cada 30 minutos. GitHub puede retrasarlas.
En repositorios públicos, los workflows programados pueden desactivarse tras 60 días
sin actividad: si ocurre, habilítalos de nuevo en Actions.

## 5. Probar todos los bancos sin cambiar las cotizaciones

Opcional, en tu equipo y dentro de la carpeta del proyecto:

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
python pruebas/verificar_bancos.py
python actualizar.py --probar prodem
python -m unittest discover -s pruebas -p "test_*.py" -v
```

La prueba individual exige los campos esperados de cada banco y comprueba que
`docs/` no cambie. Guarda el detalle en `pruebas/resultado_bancos.json`.
La verificación local previa pasó en los 14 bancos; el informe está en
`pruebas/INFORME.md`. La ejecución en tu repositorio se verifica con el paso 4.

## 6. Actualización manual desde la página (opcional)

Introduce usuario/organización y repositorio en el formulario. Para enviarlo,
usa un token fine-grained limitado a ese repositorio con **Actions: Read and write**.
El token se usa en memoria y el campo se limpia tras el envío; no lo guardes en
archivos del proyecto. El formulario ejecuta `actualizacion-manual.yml`, guarda el
registro y publica Pages. Los campos de tasas que dejes vacíos se omiten del nuevo
estado actual de ese banco.

## Problemas frecuentes

### Prodem: ConnectTimeout desde GitHub Actions

Un `ConnectTimeout` significa que el servidor de GitHub no pudo establecer la
conexión HTTPS con Prodem. No identifica un problema de extracción HTML ni confirma
por sí solo que el banco esté bloqueando GitHub. En las pruebas locales, tanto
`prodem.bo` como `www.prodem.bo` respondieron correctamente y resolvieron a la misma IP.

1. Sube también `.github/workflows/diagnostico-prodem.yml` y
   `pruebas/diagnostico_conexion_prodem.py` (o todos los archivos de código del paquete).
2. En Actions ejecuta **Diagnosticar conexión Prodem → Run workflow** en `main`.
   Prueba Linux, Windows y macOS por separado, sin escribir cotizaciones.
3. Si alguno termina en verde, abre **Settings → Secrets and variables → Actions →
   Variables → New repository variable**. Nombre: `COTIZACIONES_RUNNER`.
   Valor: el runner que funcionó, por ejemplo `windows-latest` o `macos-latest`.
4. Ejecuta **Actualizar tipo de cambio** y comprueba los 14 bancos en ese runner.
   El cambio de runner puede afectar la conectividad de otros bancos; el resultado
   definitivo se verifica con esa nueva ejecución. Ambos workflows de captura
   tienen Bash explícito para funcionar también en Windows y macOS.
5. Si los tres runners fallan, se necesita una máquina con acceso a Prodem para
   ejecutar la captura (por ejemplo un runner propio). Aumentar tiempos de espera
   no garantiza resolver una conexión inaccesible. Conserva el dato anterior
   mientras se configura esa alternativa o registra una actualización manual.

Sin la variable, la actualización sigue usando `ubuntu-latest`. El despliegue de
Pages continúa en Ubuntu de forma independiente de la captura.

- **No aparecen workflows:** falta `.github/workflows/` en la raíz del repositorio
  o los archivos se subieron dentro de una carpeta extra.
- **Error 403 al hacer git push:** revisa permisos de Actions y reglas de `main`.
- **Pages devuelve 404 o no actualiza:** configura Source: GitHub Actions y vuelve
  a ejecutar "Publicar página de cotizaciones" desde Actions.
- **Falla un banco:** revisa la salida `[FALLO]` y prueba su ID individualmente.
  Los sitios bancarios pueden cambiar su HTML o no estar disponibles.

Referencias oficiales:

- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule
