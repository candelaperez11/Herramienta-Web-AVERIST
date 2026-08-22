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
https://github.com/c-AVERIST.git
cd Herramienta-Web-AVERIST
```

(Si `git clone` da " primero con `sudoapt-get update && sudo apt-get install -y git`.)

### 2. Frontend

```bash
cd frontend
npm install
```

### 3. Backend (ento

```bash
cd ../backend
sudo apt-get installon3-pip
python3 -m venv .venv
source .venv/bin/act
pip install flask flask-cors networkx
```

### 4. Entorno de AV

```bash
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$
bash Miniforge3-$(uname)-$(uname -m).sh                                ```
                                                                       Responde a sus pregude instalación →Enter, inicializar conda → `yes`). Cierra y vuelve a abrir la terminal al terminar.
                                                                       ```bash
conda install -n base -c conda-forge mamba -y                          mamba create -n averpython=3.11 z3-solver
```                                                                   
Usa `mamba` en vez de `conda create` directamente para este paso — con `conda` a secas, rese puede quedarsecolgado mucho tiempo sin dar ningún error; `mamba` es más rápido y fiable. Este paso dempleto) y puedetardar bastante incluso con `mamba`.

## Ejecución

Se necesitan dos terminales abiertas a la vez.

**Terminal 1 — backend:**

```bash
cd backend
source .venv/bin/activate
python app.py
```

Levanta el servidor Flask en `http://127.0.0.1:5000`. Internamente,
cada análisis lanza ro del entorno conda`averist` — no hace falta activar ese entorno a mano.

**Terminal 2 — frontend:**

```bash                                                                cd frontend
npm run dev                                                            ```
                                                                       Abre la URL que indi/localhost:5173`).
                                                                       > **Nota:** todos loida la ejecucióncompleta de un análisis con AVERIST, han sido verificados de principio a fin. Si al ejecutaT terminó con unerror", revisa el campo `log` de la respuesta del backend (pestaña Network del navegadoema puntual delentorno conda recién creado, no del propio proyecto.
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
