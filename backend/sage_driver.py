#Ejecuta AVERIST de forma no interactiva con los parámetros que el usuario elije en forntend, recibe un JSON y se ejecuta con sage
import argparse
import json
import os
import sys
from pathlib import Path

#Buscamos los archivos necesarios dentro de averist_src 
AVERIST_SRC = Path(__file__).resolve().parent / "averist_src"
sys.path.insert(0, str(AVERIST_SRC))

#Estos imports van aquí y no al principio porque necesitan que sys.path ya esté modificado; por eso el noqa(ignorar el aviso)
import main_functions as mf  # noqa: E402(import no al principio)
import files as f  # noqa: E402
import read_input as ri  # noqa: E402

#Corremos averist con los parametros introducidos por el usuario de tipo e iteraciones ya añadimos los declarados por defecto en AVERIST
def run(namefile, ha_type, max_cegar_iteration, granularity):
    given_linear_exp = "nle"
    unif_linear_exp = granularity
    extract_linear_exp = "exle"
    cegar_ref = "unif"
    unif_linear_exp_cegar = granularity
    opt_solver = 1

    namefolder = os.path.splitext(namefile)[0] + "_averist"
    f.file_creation.folders(namefolder) #creamos esa carpeta donde guardaremos los datos

    print("namefile =", namefile)
    print("namefolder =", namefolder)
    print("HA_type =", ha_type)

    with open(namefile, "r", encoding="utf-8") as fh:
        graph_data = json.load(fh)

    var_dict, inv_var_dict, P, G = ri.read_input(graph_data, ha_type)

    print("var_dict =", var_dict)
    print("Nodes of G =", G.nodes())
    print("Edges of G =", G.edges())

    f.file_creation.store_graph(G, namefolder, ha_type)

    #Calculamos los hiperplanos iniciales
    LE = mf.main_functions_maximal.initial_LE(
        P, given_linear_exp, extract_linear_exp, unif_linear_exp, inv_var_dict, namefolder
    )
    print("LE =", LE)

    namefolder_le = f.file_creation.itfolders(LE, namefolder)
    f.file_creation.store_le(LE, namefolder_le + "/output")

    if ha_type == "polyhedral":
        result = mf.cegar_loop_functions.polyhedral_cegar_loop(
            G, LE, var_dict, inv_var_dict, namefolder, max_cegar_iteration,
            cegar_ref, unif_linear_exp_cegar, opt_solver,
        )
    #Linear
    else:
        result = mf.cegar_loop_functions.linear_cegar_loop(
            G, LE, var_dict, inv_var_dict, namefolder, max_cegar_iteration,
            cegar_ref, unif_linear_exp_cegar, opt_solver,
        )

    answer = result[0]
    if not answer:
        print("WE DID NOT GET ANY ANSWER")

#Definimos los 4 argumentos que necesitamos y llamamos a run
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--namefile", required=True)
    parser.add_argument("--ha-type", required=True, choices=["linear", "polyhedral"])
    parser.add_argument("--max-cegar", required=True, type=int)
    parser.add_argument("--granularity", required=True, type=int)
    args = parser.parse_args()

    run(args.namefile, args.ha_type, args.max_cegar, args.granularity) 


if __name__ == "__main__":
    main()
