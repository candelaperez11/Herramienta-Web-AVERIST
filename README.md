# ha-v1 — Editor visual de autómatas híbridos para AVERIST

Herramienta web para diseñar autómatas híbridos de forma visual e interactiva y verificar su estabilidad global asintótica (GAS) sin necesidad de escribir a mano el fichero de entrada `.averist` ni usar la línea de comandos.

El usuario construye el autómata como un grafo (nodos = localizaciones, con su invariante y su dinámica; aristas = transiciones, con su guarda) desde el navegador. El backend valida el modelo, lo traduce a la representación interna que AVERIST necesita y ejecuta el análisis, devolviendo el veredicto de estabilidad en pantalla.

## Arquitectura

```
Navegador (React + React Flow, :5173)
        │  POST /analyze (JSON)
        ▼
Backend Flask (:5000)
        │  valida y traduce el grafo
        ▼
AVERIST (entorno conda: SageMath + PPL + z3, algoritmo CEGAR)
        │  veredicto de estabilidad
        ▼
Navegador (pantalla de resultado)
```

El proyecto incluye su propia copia de AVERIST en `backend/averist_src/`, con correcciones aplicadas sobre la versión original. **No es necesario instalar AVERIST por separado.**

## Requisitos previos

- [Node.js](https://nodejs.org/) (para el frontend)
- Python 3.11+ (para el entorno del backend)
- [Miniforge/conda](https://github.com/conda-forge/miniforge) (para el entorno con SageMath)
- **Linux, macOS o WSL2 en Windows.** SageMath no tiene buen soporte nativo en Windows, así que en Windows es necesario usar WSL2.

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd ha-v1
```

### 2. Frontend

```bash
cd frontend
npm install
```

### 3. Backend (entorno Python normal)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install flask flask-cors networkx
```

### 4. Entorno de AVERIST (conda)

```bash
conda create -n averist -c conda-forge sage=10.7 python=3.11 z3-solver
```

Este paso es el más pesado (descarga varios GB y puede tardar bastante), ya que instala SageMath completo. PPL (Parma Polyhedra Library) viene incluido con esta instalación de Sage, no requiere un paso aparte.

## Ejecución

Se necesitan dos terminales abiertas a la vez.

**Terminal 1 — backend:**

```bash
cd backend
source .venv/bin/activate
python app.py
```

Levanta el servidor Flask en `http://127.0.0.1:5000`. Internamente, cada análisis lanza un subproceso con `sage` dentro del entorno conda `averist` — no hace falta activar ese entorno a mano, el backend lo hace por ti al invocar AVERIST.

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

También puedes usar **Exportar JSON** para descargar el modelo construido sin ejecutar el análisis.

## Estructura del repositorio

```
frontend/           Editor visual (React + React Flow)
backend/
  app.py            Endpoints /analyze y /health
  graph_utils.py     JSON → grafo interno, validación estructural
  averist_input_builder.py   Detección de variables, validación de dinámicas
  read_input.py      Grafo → representación interna de AVERIST (sin pasar por su parser de texto)
  sage_driver.py      Punto de entrada que se ejecuta con el intérprete `sage`
  averist_runner.py   Orquesta la ejecución de AVERIST y recoge el veredicto
  averist_src/         Copia vendorizada de AVERIST, con correcciones aplicadas
```

## Créditos

Construido sobre [AVERIST](https://software.imdea.org/projects/averist/), desarrollado por Miriam García Soto y Pavithra Prabhakar.

> P. Prabhakar y M. García Soto, "AVERIST: An Algorithmic Verifier for Stability", Electronic Notes in Theoretical Computer Science, vol. 317, pp. 133–139, 2015.
