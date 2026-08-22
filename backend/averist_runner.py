#Este módulo lanza AVERIST como subproceso, dentro del entorno conda (Sage/z3/ppl)
import json
import subprocess
from pathlib import Path
from uuid import uuid4

#rutas fijas
BACKEND_DIR = Path(__file__).resolve().parent
AVERIST_SRC = BACKEND_DIR / "averist_src"
SAGE_DRIVER = BACKEND_DIR / "sage_driver.py"
RUNS_DIR = BACKEND_DIR / "runs"
CONDA_ENV = "averist"
CONDA_SETUP = "~/miniforge3/etc/profile.d/conda.sh"

#Granularidad tiene valor fijo ya que no es un parametro que el usuario peuda elegir
DEFAULT_GRANULARITY = 2
DEFAULT_TIMEOUT_SECONDS = 600

#Excepción para cuando AVERIST falla al ejecutar, guardando el log completo
class AveristRunError(Exception):
    def __init__(self, message, log=""):
        super().__init__(message)
        self.log = log

#Ahora convertimos grafo a un diccionario normal, que posteriorimente se convierte en JSON
def _graph_to_dict(graph, variables):
    return {
        "variables": variables,
        "nodes": {
            node: {"inv": data["inv"], "dyn": data["dyn"]}
            for node, data in graph.nodes(data=True)
        },
        "edges": [
            {"source": u, "target": v, "guard": data["guard"]}
            for u, v, data in graph.edges(data=True)
        ],
    }

#Traduce el mensaje técnico de AVERIST a una explicación en lenguaje sencillo para usuarios sin experiencia
def _explain_message(message):
    if message.startswith("Stable"):
        return "El sistema es estable: pequeñas perturbaciones no lo alejan de su comportamiento esperado, y con el tiempo tiende a mantenerse controlado."

    if message.startswith("Unstable (blow-up)"):
        return "El sistema es inestable: se ha detectado que alguna variable puede crecer sin límite (no está acotada), lo que indica un comportamiento divergente."

    if message.startswith("Unstable (concrete counterexample)"):
        return "El sistema es inestable: se ha encontrado una ejecución real y concreta del autómata que demuestra que no se mantiene estable."

    if message.startswith("Unstable (hybridization)"):
        return "El sistema es inestable: la abstracción del autómata ha detectado un comportamiento que viola la estabilidad."

    if message.startswith("Unstable"):
        return "El sistema es inestable."

    return (
        "AVERIST no ha podido determinar si el sistema es estable o no dentro del "
        "número máximo de iteraciones del algoritmo CEGAR. Prueba a aumentar el "
        "valor de 'max_CEGAR_iteration' para permitir un análisis más preciso."
    )

#Funcion principal (IMPORTANTE)
def run_averist(graph, variables, ha_type, max_cegar_iteration, timeout=DEFAULT_TIMEOUT_SECONDS):
    RUNS_DIR.mkdir(exist_ok=True) 

    #Creamos carpeta para su ejecución
    run_id = uuid4().hex[:8]
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir()

    #Se escribe en model.json el grafo convertido a texto
    input_path = run_dir / "model.json"
    input_path.write_text(
        json.dumps(_graph_to_dict(graph, variables), ensure_ascii=False), encoding="utf-8"
    )

    #Montamos el comando que se va a lanzar para correr AVERIST con conda, sage y todo lo necesaario
    command = (
        f"source {CONDA_SETUP} && "
        f"conda activate {CONDA_ENV} && "
        f"sage {SAGE_DRIVER} "
        f"--namefile {input_path} "
        f"--ha-type {ha_type} "
        f"--max-cegar {int(max_cegar_iteration)} "
        f"--granularity {DEFAULT_GRANULARITY}"
    )

    #Ejecuta el comando anterior por terminal
    try:
        proc = subprocess.run(
            ["bash", "-lc", command],
            cwd=AVERIST_SRC,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        log = (exc.stdout or "") + "\n" + (exc.stderr or "")
        raise AveristRunError(f"AVERIST no terminó en {timeout}s (timeout)", log=log)

    log = proc.stdout + "\n" + proc.stderr 

    if proc.returncode != 0:
        raise AveristRunError("AVERIST terminó con un error", log=log)

    #Busca todos los stable.dat generados ordenados de antiguo a reciente
    output_root = run_dir / "model_averist"
    stable_files = sorted(
        output_root.glob("**/output/stable.dat"),
        key=lambda p: p.stat().st_mtime,
    )

    if not stable_files:
        raise AveristRunError(
            "AVERIST no generó ningún resultado (no se encontró stable.dat)", log=log
        )

    #Busca el veredicto FINAL que va a devolver al usuario que esta en la ultima carpeta de iteración
    final_stable = stable_files[-1]
    lines = final_stable.read_text(encoding="utf-8").splitlines()
    message = lines[0] if lines else ""
    counterexample = lines[1:]

    if message.startswith("Stable"):
        answer = True
    elif message.startswith("Unstable"):
        answer = False
    else:
        answer = None  #no concluyente dentro del límite de iteraciones CEGAR (hay que refinar)

    #Añadimos una explicación sencilla debajo del mensaje técnico, para usuarios sin experiencia
    message_with_explanation = message + "\n\n" + _explain_message(message)

    #Devuelve la información que app.py necesita para construir la respuesta del usuario
    return {
        "run_id": run_id,
        "message": message_with_explanation,
        "answer": answer,
        "counterexample": counterexample,
        "log": log,
    }
