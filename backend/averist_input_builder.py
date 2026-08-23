#Aquí traducimos el grafo (networkx.DiGraph) al formato que entiende AVERIST
import re

_RESERVED_WORDS = {"AND", "OR", "NOT", "TRUE", "FALSE"} 
_TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

#Para diferenciar en las palabras introducidas las variables de operadores lógicos u otras sintaxis
def _identifiers(text):
    return [t for t in _TOKEN_RE.findall(text or "") if t.upper() not in _RESERVED_WORDS]

#Obtienemos la lista de variables del autómata (los invariantes y dyn de los nodos, y guards de las aristas)
def extract_variables(graph):
    variables = []
    seen = set() #evitar duplicados

    def _add(token):
        if token not in seen:
            seen.add(token)
            variables.append(token)
    #Sacamos los identificadores de cada nodo y arista EN ORDEN 
    for _, data in graph.nodes(data=True):
        for token in _identifiers(data.get("inv", "")):
            _add(token)

    for _, _, data in graph.edges(data=True):
        for token in _identifiers(data.get("guard", "")):
            _add(token)

    for _, data in graph.nodes(data=True):
        for token in _identifiers(data.get("dyn", "")):
            if token.startswith("d") and len(token) > 1:
                _add(token[1:])
            else:
                _add(token)

    return variables

#Comprobamos que dyn de cada nodo solo use derivadas de variables declaradas
def validate_dynamics(graph, variables, ha_type):
    derivatives = {"d" + v for v in variables}
    expected = derivatives | set(variables) if ha_type == "linear" else derivatives #en modo linear también la propia variable
    errors = []

    for node, data in graph.nodes(data=True):
        for token in _identifiers(data.get("dyn", "")):
            if token not in expected:
                errors.append(
                    f"El nodo '{node}': la dinámica usa '{token}', pero se esperaba "
                    f"una derivada de una variable declarada ({', '.join(sorted(expected))})"
                )

    return errors
