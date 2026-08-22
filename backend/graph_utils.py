#En este modulo convertimos el JSON exportado por el frontend en un networkx.DiGraph
import networkx as nx

#Usamos true como valor por defecto para no obligar al usuario a escribir invariantes/guards, lo traducimos como todo el espacio
DEFAULT_INVARIANT = "True"
DEFAULT_GUARD = "True"

#Definimo errores específicos para nuestro proyecto
class GraphValidationError(Exception):
    def __init__(self, errors):
        super().__init__("; ".join(errors))
        self.errors = errors #lista completa errores 

#Funcion principal que pasa de JSON a digrpah usada en app.py
def json_to_digraph(data):
    errors = []
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    #Validaciones sencillas
    if not nodes:
        raise GraphValidationError(["El grafo no tiene ningún nodo"])

    id_to_name = {}
    names_seen = set()

    for n in nodes:
        node_id = n.get("id")
        name = (n.get("name") or "").strip()

        if not name:
            errors.append(f"El nodo '{node_id}' no tiene nombre")
            continue
        if name in names_seen:
            errors.append(f"Hay dos nodos con el mismo nombre: '{name}'")
            continue

        names_seen.add(name)
        id_to_name[node_id] = name

    graph = nx.DiGraph()  #comenzamos a construir grafo primero recorremos nodos y luego aristas hasta obtener toda la info necesaria

    for n in nodes:
        name = id_to_name.get(n.get("id"))
        if name is None:
            continue

        invariant = (n.get("invariant") or "").strip() or DEFAULT_INVARIANT
        flow = (n.get("flow") or "").strip()

        if not flow:
            errors.append(f"El nodo '{name}' no tiene dinámica (flow)")

        graph.add_node(name, inv=invariant, dyn=flow) 

    for e in edges:
        source = id_to_name.get(e.get("source"))
        target = id_to_name.get(e.get("target"))
        guard = (e.get("guard") or "").strip() or DEFAULT_GUARD

        if source is None or target is None:
            errors.append(f"La arista '{e.get('id')}' apunta a un nodo que no existe")
            continue

        graph.add_edge(source, target, guard=guard)

    if errors:
        raise GraphValidationError(errors)

    return graph 
