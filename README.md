# Herramienta Web para el programa AVERIST
Os presento el proyecto en el que llevo trabajando unos meses, un editor visual de autómatas híbridos con verificación de estabilidad mediante el programa AVERIST. 

He desarrollado esta herramienta web como parte de mi Trabajo de Fin de Grado con el objetivo de facilitar el uso de AVERIST a usuarios que no estén familiarizados con este tipo de herramientas. La aplicación permite diseñar autómatas híbridos de forma visual e interactiva y comprobar su estabilidad mediante AVERIST, sin tener que escribir manualmente los ficheros de entrada .averist ni trabajar directamente desde la línea de comandos.

En esta herramienta web el usuario construye el autómata como un grafo desde el navegador, donde los nodos son localizaciones, con su invariante y su dinámica y las aristas son transiciones, con su guarda. El backend valida el modelo, lo traduce a la representación interna que AVERIST necesita y ejecuta el análisis, devolviendo un mensaje explicativo a modo de veredicto de estabilidad. Antes del análisis aparece una ventana donde el usuario puede seleccionar el tipo de autómata y el número máximo de iteraciones de CEGAR. 

## Requisitos previos
Esta herramienta necesita de algunos programas que deben estar instalados en el ordenador donde se vaya a utilizar. 

- **Linux, macOS o WSL2 en Windows.** SageMath no tiene buen soporte nativo en Windows, y el backend ejecuta comandos de terminal (`bash`, `conda`) directamente, así que **todo el proyecto** (frontend, backend y AVERIST) debe instalarse y ejecutarse dentro de este entorno.
- [Node.js](https://nodejs.org/) 18+: para el frontend 
- Python 3.11+ : para el entorno del backend
- [Miniforge/conda](https://github.com/conda-forge/miniforge): para el entorno con SageMath
- `git`, para clonar el repositorio

**Importante:** Es recomendable clonar y trabajar el proyecto dentro de tu carpeta de usuario de Linux, no dentro de una carpeta del disco de Windows montado (`/mnt/c/...`), ya que la segunda opción es más lenta para operaciones con muchos archivos pequeños. 

## Instalación

### 1. Clonar el repositorio

```bash
cd ~
git clone
https://github.com/candelaperez11/Herramienta-Web-AVERIST.git
cd Herramienta-Web-AVERIST
```
Si aparece un error de "Command not found" ejecutamos  `sudo apt-get update && sudo apt-get install -y git`, ya que pueden no estar instalados en nuestro equipo.

### 2. Node.js (con nvm)

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc
nvm install 20
```

Comprueba con `which npm` que la ruta empieza por tu carpeta de usuario de Linux (algo como `/home/tu_usuario/.nvm/...`), no por `/mnt/c/...`.

### 3. Frontend

```bash
cd frontend
npm install
```

### 4. Backend (entorno Python)

```bash
cd ../backend
sudo apt-get install -y python3 python3-venv python3-pip
python3 -m venv .venv
source .venv/bin/activate
pip install flask flask-cors networkx
```

### 5. Entorno de AVERIST

```bash
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
```

Te hará una serie de preguntas que debes responder con: 
- Licencia --> `yes`
- Ruta de instalación --> ENTER
- Inicializar conda --> `yes`
Una vez hayamos acabado cerramos y volvemos a abrir la terminal.

```bash
conda install -n base -c conda-forge mamba -y
mamba create -n averist -c conda-forge sage=10.7 python=3.11 z3-solver
```
Este proceso puede tardar entre 20-40 minutos depende del ordenador.

## Ejecución

Se necesitan dos terminales abiertas a la vez.

**Terminal 1 — backend:**

```bash
cd backend
source .venv/bin/activate
python app.py
```

Levanta el servidor Flask en `http://127.0.0.1:5000`. Internamente, cada análisis lanza un subproceso con `sage` dentro del entorno conda `averist` — no hace falta activar ese entorno a mano.

**Terminal 2 — frontend:**

```bash
cd frontend
npm run dev
```
Abre la URL que indique Vite (por defecto `http://localhost:5173`).

## Solución de problemas

Los siguientes problemas son problemas reales que me he encontrado probando la herramienta. 

**"Cannot find module @rollup/rollup-linux-x64-gnu"** (u otro paquete similar) al ejecutar `npm run dev`: pasa si `node_modules` se instaló con un Node.js de otro sistema operativo. Podemos arreglarlo con:
```bash
rm -rf node_modules package-lock.json
npm install
```

**"AVERIST terminó con un error"** al analizar: revisa el campo `log` de la respuesta del backend (pestaña "Network" del navegador, en la petición `analyze`) para ver el detalle, puede deberse a un problema puntual del entorno conda, no del propio proyecto.

## Uso

1. Pulsa **+ Nodo** para crear una localización y dale un nombre.
2. Selecciona el nodo para editar su `flow` (dinámica) e `invariant` desde el panel lateral. Si se dejan vacíos, se asume `True` (sin restricciones).
3. Arrastra desde cualquier lado de un nodo hasta otro para crear una transición. Selecciónala para editar su `guard`.
4. Pulsa **Analizar**, elige el tipo de autómata (`polyhedral` o `linear`) y el número máximo de iteraciones del algoritmo CEGAR, y ejecuta el análisis.
5. El resultado (estable / inestable, mensaje explicativo y errores de validación si los hubiera) se muestra en pantalla.

También puedes usar **Exportar JSON** para descargar el modelo construido en formato JSON sin ejecutar el análisis.

## Créditos

Construido sobre [AVERIST](https://software.imdea.org/projects/averist/), desarrollado por Miriam García Soto y Pavithra Prabhakar.

> P. Prabhakar y M. García Soto, "AVERIST: An Algorithmic Verifier for Stability", Electronic Notes in Theoretical Computer Science, vol. 317, pp. 133–139, 2015.
