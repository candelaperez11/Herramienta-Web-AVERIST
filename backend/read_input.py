#En este módulo transofrmamos los datos en la estructura de entrada de AVERIST, 4 elementos
import networkx as nx
import ppl_functions as pplf

#Quitamos espacios, saltos de linea y tabulaciones del texto (igual que lo hace AVERIST en su input_parse)
def _no_whitespace(text):
    return "".join((text or "").split())

#Traducimos para que PPL puedea entender los nombres de las variables
def _build_var_dicts(variables):
    var_dict = {name: i for i, name in enumerate(variables)}
    inv_var_dict = {i: name for name, i in var_dict.items()}
    inv_var_dict_dyn = {i: "d" + name for i, name in inv_var_dict.items()}
    return var_dict, inv_var_dict, inv_var_dict_dyn

#Funcion principal donde recibimos data y el tipo y arrancamos un grafo vacío
def read_input(graph_data, ha_type):
    variables = graph_data["variables"]
    var_dict, inv_var_dict, inv_var_dict_dyn = _build_var_dicts(variables)

    G = nx.DiGraph() 
    G.add_nodes_from(graph_data["nodes"].keys())

    P = [] #lista de predicados 

    #Limpiamos espacios y convertimos invariante a un polítopo
    for node, attrs in graph_data["nodes"].items():
        inv_str = _no_whitespace(attrs["inv"])
        dyn_str = _no_whitespace(attrs["dyn"])

        inv_poly = pplf.ppl_functions.get_polyhedron(inv_str, inv_var_dict)
        G.add_node(node, inv=inv_poly)
        P.extend(inv_str.split("AND"))

        #En el polyhedral dyn también se convierte a un polítopo
        if ha_type == "polyhedral":
            dyn_poly = pplf.ppl_functions.get_polyhedron(dyn_str, inv_var_dict_dyn)
            G.add_node(node, dyn=dyn_poly)
        else:
            G.add_node(node, dyn=dyn_str)

    for edge in graph_data["edges"]:
        guard_str = _no_whitespace(edge["guard"])
        guard_poly = pplf.ppl_functions.get_polyhedron(guard_str, inv_var_dict)
        G.add_edge(edge["source"], edge["target"], guard=guard_poly)
        P.extend(guard_str.split("AND"))

    P = list(set(P)) #quitamos duplicados

    return var_dict, inv_var_dict, P, G #devuelve lo que devolveria el parser original de AVERIST (justo lo que necesitamos)
