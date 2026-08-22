# Herramienta Web AVERIST
Os presento un editor visual de autómatas híbridos con verificación de estabilidad mediante el programa AVERIST. 

He creado esta herramienta web como parte de mi Trabajo de Fin de Grado con el objetivo de diseñar autómatas híbridos de forma visual e interactiva y verificar su estabilidad con el programa AVERIST, sin necesidad de escribir a mano el fichero de entrada `.averist` ni usar la línea de comandos.

En esta herramiento web el usuario construye el autómata como un grafo desde el navegador, donde los nodos son localizaciones, con su invariante y su dinámica y las aristas son transiciones, con su guarda. El backend valida el modelo, lo traduce a la representación interna que AVERIST necesita y ejecuta el análisis, devolviendo un mensaje explicativo a modo de veredicto de estabilidad. 

## Requisitos previos
El usuario necesita tener instaladas las siguientes herramientas para poder correr la herramienta web:

- [Node.js](https://nodejs.org/): para ejecutar el frontend
- Python 3.11+: Para el entorno del backend
- [Miniforge/conda](https://github.com/conda-forge/miniforge): para el entorno con SageMath, PPL y z3, que es lo que ejecuta AVERIST por debajo.
- Linux, macOS o WSL2 en Windows: SageMath no funciona bien en Windows nativo.

## Instalación
### 0. Instalar WSL2 

Abre **PowerShell como administrador** y ejecuta:

```powershell
wsl --install
```

Reinicia el ordenador cuando te lo pida. Esto instala Ubuntu por defecto. Abre **"Ubuntu"** desde el menú de inicio y haz **todos los pasos siguientes dentro de esa terminal**, no en PowerShell/CMD.

### 1. Instalar Node.js

Dentro de la terminal de Ubuntu/WSL2 (o de tu Linux/Mac):

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

(El `nodejs` que trae Ubuntu por defecto vía `apt` suele ser una versión demasiado antigua para este proyecto — mejor usar el comando de arriba.) Comprueba la instalación con `node -v`.

### 2. Instalar Miniforge (conda)

```bash
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
```

Acepta la licencia y deja la ruta de instalación por defecto. Cierra y vuelve a abrir la terminal al terminar.
### 4. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd ha-v1
```

### 5. Frontend

```bash
cd frontend
npm install
```

### 6. Backend (entorno Python normal)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install flask flask-cors networkx
```

### 7. Entorno de AVERIST (conda)

```bash
conda create -n averist -c conda-forge sage=10.7 python=3.11 z3-solver
```

Este paso puede tardar bastante ya que descarga varios GB porque instala SageMath completo. PPL (Parma Polyhedra Library) viene incluido con esta instalación de Sage, no requiere un paso aparte.

## Ejecución

Se necesitan dos terminales abiertas a la vez.

**Terminal 1 — backend:**

```bash
cd backend
source .venv/bin/activate
python app.py
```

Esto levanta el servidor Flask en `http://127.0.0.1:5000`, el backend se encarga de activar el entorno conda, por lo que no necesitas activar nada a mano.

**Terminal 2 — frontend:**

```bash
cd frontend
npm run dev
```

Abre la URL que indique Vite (por defecto `http://localhost:5173`).

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
