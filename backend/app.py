from pathlib import Path
from uuid import uuid4
import json

from flask import Flask, request, jsonify
from flask_cors import CORS

from graph_utils import json_to_digraph, GraphValidationError
from averist_input_builder import extract_variables, validate_dynamics
from averist_runner import run_averist, AveristRunError


app = Flask(__name__)
CORS(app)

#Carpeta donde se van a guardar los JSON recibidos desde frontend
EXPORTS_DIR = Path(__file__).resolve().parent / "exports"
EXPORTS_DIR.mkdir(exist_ok=True)

#Solo para comprobar que fucniona y está encendido
@app.get("/health")
def health():
    return jsonify({
        "ok": True,
        "message": "Backend funcionando correctamente"
    })

#Para comprobar que el JSON tiene la forma esperada
def basic_json_shape_validate(data):
    errors = []

    if not isinstance(data, dict):
        return ["El JSON recibido debe ser un objeto"] 

    #necesitamos nodos y aristas como listas
    if "nodes" not in data:
        errors.append("Falta el campo 'nodes'")
    elif not isinstance(data["nodes"], list):
        errors.append("'nodes' debe ser una lista")

    if "edges" not in data:
        errors.append("Falta el campo 'edges'")
    elif not isinstance(data["edges"], list):
        errors.append("'edges' debe ser una lista")

    return errors

#Endpoint principal de nuestro backend (LO IMPORTANTE)
@app.post("/analyze")
def analyze():
    data = request.get_json(silent=True) 

    if data is None:
        return jsonify({
            "ok": False,
            "message": "No se recibió ningún JSON"
        }), 400

    shape_errors = basic_json_shape_validate(data) #validamos forma basic
    if shape_errors:
        return jsonify({
            "ok": False,
            "message": "El JSON no tiene la estructura mínima esperada",
            "errors": shape_errors
        }), 400

    #Párametros solicitados en la ventana de ejecutar analisis
    ha_type = data.get("HA_type", "linear") 
    max_cegar_iteration = data.get("max_CEGAR_iteration", 10)

    #Convertimos JSON del frontend a networkx.DiGraph
    try:
        graph = json_to_digraph(data) 
    except GraphValidationError as e:
        return jsonify({
            "ok": False,
            "message": "El grafo tiene errores",
            "errors": e.errors
        }), 400

    #Ahora extraemos las variables del autómata, invariantes, guards, flow
    variables = extract_variables(graph)
    if not variables:
        return jsonify({
            "ok": False,
            "message": "No se han detectado variables en los invariantes, guards o dinámicas (flow)",
            "errors": ["Revisa que al menos un invariante, guard o flow use una variable, p.ej. x>=0 o dx==1"]
        }), 400

    #Validamos las dinámicas usen las variables detectadas
    dyn_errors = validate_dynamics(graph, variables, ha_type)
    if dyn_errors:
        return jsonify({
            "ok": False,
            "message": "Las dinámicas (flow) usan variables no declaradas",
            "errors": dyn_errors
        }), 400

    run_id = uuid4().hex[:8]
    (EXPORTS_DIR / f"model_{run_id}.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8" #guardar copia en exports
    )

    #Ejecutar AVERIST directamente sobre el grafo (run_averist se declara en averist_runner.py)
    try:
        result = run_averist(graph, variables, ha_type, max_cegar_iteration)
    except AveristRunError as e:
        return jsonify({
            "ok": False,
            "message": str(e),
            "errors": [str(e)],
            "log": e.log[-4000:]
        }), 500

    counterexample_text = (
        "\n\nContraejemplo abstracto:\n" + "\n".join(result["counterexample"])
        if result["counterexample"] else ""
    )

    return jsonify({ #responde peticion de fetch
        "ok": True,
        "message": "Análisis completado",
        "answer": result["answer"],
        "stable_message": result["message"] + counterexample_text,
        "summary": {
            "nodes": graph.number_of_nodes(),
            "edges": graph.number_of_edges(),
            "variables": variables,
            "HA_type": ha_type,
            "max_CEGAR_iteration": max_cegar_iteration
        },
        "run_id": result["run_id"]
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
