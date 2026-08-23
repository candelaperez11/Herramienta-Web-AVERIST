import { useCallback, useMemo, useRef, useState } from "react";
import ReactFlow, {
  addEdge,
  reconnectEdge,
  Background,
  Controls,
  MiniMap,
  useEdgesState,
  useNodesState,
  Handle,
  Position,
  MarkerType,
} from "reactflow"; //lienzo interactivo
import "reactflow/dist/style.css";

//Se necesita un id único para nodos y aristas
function uid(prefix = "id") {
  return prefix + "_" + Math.random().toString(16).slice(2, 10);
}

//Para dibujar nodos (valor por defecto en invariant y name como dijo Miriam)
function AutomatonNode({ data }) {
  return (
    <div
      style={{
        padding: 10,
        border: "1px solid #333",
        borderRadius: 8,
        background: "white",
        minWidth: 180,
        fontSize: 12,
        lineHeight: 1.2,
      }}
    >
      <Handle type="source" position={Position.Top} id="top" />

      <div style={{ fontWeight: 700, marginBottom: 6 }}>
        {data?.name || "State"}
      </div>

      <div style={{ marginBottom: 6 }}>
        <b>flow:</b>
        <div style={{ whiteSpace: "pre-wrap", color: "#444" }}>
          {data?.flow || "—"}
        </div>
      </div>

      <div>
        <b>inv:</b>
        <div style={{ whiteSpace: "pre-wrap", color: "#444" }}>
          {data?.invariant || "True"}
        </div>
      </div>

      <Handle type="source" position={Position.Bottom} id="bottom" />
    </div>
  );
}

//Aquí se guarda todo lo importante del editor: nodos, aristas, selección y ventanas emergentes
export default function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selected, setSelected] = useState(null); //Donde se clica para mostrar en panel de la derecha

  const [showAnalyzeModal, setShowAnalyzeModal] = useState(false);
  const [haType, setHaType] = useState("polyhedral"); //Polyhedral por defecto
  const [maxCegarIteration, setMaxCegarIteration] = useState(10);

  const [analysisResult, setAnalysisResult] = useState(null);
  const [showResultScreen, setShowResultScreen] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  //useMemo evita crear el objeto de nuevo en cada render, se calcula solo una vez
  const nodeTypes = useMemo(
    () => ({
      automaton: AutomatonNode,
    }),
    [],
  );

  //Funcion que se ejecuta al pulsa + nodo
  const addNode = () => {
    const name = prompt("Nombre del nodo/estado:", "q");
    if (!name) return;

    const id = uid("N");
    //Añade nuevo nodo a la lista de nodos
    setNodes((ns) =>
      ns.concat({
        id,
        position: { x: 120 + ns.length * 40, y: 140 + ns.length * 30 },
        data: { name, flow: "", invariant: "" },
        type: "automaton",
      }),
    );
  };

  //Funcion que se ejecuta al conectar dos nodos
  const onConnect = useCallback(
    (params) => {
      const edge = {
        ...params,
        id: uid("E"),
        data: { guard: "" },
        label: "True",
        markerEnd: { type: MarkerType.ArrowClosed }, //para punta de flecha
      };
      setEdges((eds) => addEdge(edge, eds));
    },
    [setEdges],
  );

  //SOLO PARA RECONEXIONES
  //Guarda si la reconexión de una arista tuvo éxito
  const edgeUpdateSuccessful = useRef(true);

  //Se empieza a arrastrar con el ratón
  const onReconnectStart = useCallback(() => {
    edgeUpdateSuccessful.current = false;
  }, []);

  //Se conecta si suletas encima de un nodo válido
  const onReconnect = useCallback(
    (oldEdge, newConnection) => {
      edgeUpdateSuccessful.current = true;
      setEdges((eds) => reconnectEdge(oldEdge, newConnection, eds));
    },
    [setEdges],
  );

  //Soltar ratón al terminar, se ejecuta siempre haya conexion o no
  const onReconnectEnd = useCallback(
    (_event, edge) => {
      if (!edgeUpdateSuccessful.current) {
        //si no se conecto se borra la arista
        setEdges((eds) => eds.filter((e) => e.id !== edge.id));
      }
      edgeUpdateSuccessful.current = true;
    },
    [setEdges],
  );

  //Guarda qué está seleccionado (nodo o arista) para mostrarlo en el panel lateral, con su id y tipo
  const onSelectionChange = useCallback(({ nodes: selN, edges: selE }) => {
    if (selN?.length) setSelected({ type: "node", id: selN[0].id });
    else if (selE?.length) setSelected({ type: "edge", id: selE[0].id });
    else setSelected(null);
  }, []);

  //Nodo completo (con su flow/invariant) a partir del id en selected
  const selectedNode = useMemo(() => {
    if (selected?.type !== "node") return null;
    return nodes.find((n) => n.id === selected.id) ?? null;
  }, [selected, nodes]);

  //Arista completa (con su guard) a parir del id en selected
  const selectedEdge = useMemo(() => {
    if (selected?.type !== "edge") return null;
    return edges.find((e) => e.id === selected.id) ?? null;
  }, [selected, edges]);

  //Para actualizar un campo del nodo seleccionado
  const updateNodeField = (field, value) => {
    if (!selectedNode) return;
    setNodes((ns) =>
      ns.map((n) =>
        n.id === selectedNode.id
          ? { ...n, data: { ...n.data, [field]: value } }
          : n,
      ),
    );
  };

  //Para actualizar el guard de la arista seleccionada
  const updateEdgeGuard = (value) => {
    if (!selectedEdge) return;
    setEdges((es) =>
      es.map((e) =>
        e.id === selectedEdge.id
          ? {
              ...e,
              data: { ...(e.data || {}), guard: value },
              label: value || "True",
            }
          : e,
      ),
    );
  };

  //Para convertir nodos y aristas a formato JSON simple, listo para enviar backend
  const buildAutomatonJson = () => ({
    nodes: nodes.map((n) => ({
      id: n.id,
      position: n.position,
      name: n.data?.name ?? "",
      flow: n.data?.flow ?? "",
      invariant: n.data?.invariant ?? "",
    })),
    edges: edges.map((e) => ({
      id: e.id,
      source: e.source,
      target: e.target,
      guard: e.data?.guard ?? "",
    })),
  });

  //Convierte el objeto devuelto por buildAutomatonJson en texto y lo descarga como archivo en el equipo
  const exportAutomaton = () => {
    const automaton = buildAutomatonJson();
    const text = JSON.stringify(automaton, null, 2);

    const blob = new Blob([text], { type: "application/json" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "automaton.json";
    a.click();

    URL.revokeObjectURL(url);
    alert("Archivo JSON descargado correctamente ✅");
  };

  //Para crear el objeto final que el backend va a recibir para el analisis AVERIST
  //Después envía el autómata y los parámetros al backend, y muestra el veredicto final o error si lo hubiera
  const analyzeAutomaton = async () => {
    const automaton = buildAutomatonJson();

    const payload = {
      ...automaton,
      HA_type: haType,
      max_CEGAR_iteration: Number(maxCegarIteration),
    };

    try {
      setIsAnalyzing(true);

      const res = await fetch("http://127.0.0.1:5000/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const result = await res.json();

      setAnalysisResult(result);
      setShowAnalyzeModal(false);
      setShowResultScreen(true);
    } catch (err) {
      //Si hay error, se muestra en la misma pantalla que el veredicto final
      console.error(err);
      setAnalysisResult({
        ok: false,
        message: "No puedo conectar con Flask",
      });
      setShowAnalyzeModal(false);
      setShowResultScreen(true);
    } finally {
      setIsAnalyzing(false);
    }
  };

  //A partir de aquí es diseño de la pantalla, barra superior, ventanas, etc..
  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        <div
          style={{
            padding: "10px 12px",
            borderBottom: "1px solid #ddd",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 12,
            flexWrap: "wrap",
          }}
        >
          <div style={{ minWidth: 260 }}>
            <div style={{ fontWeight: 700, fontSize: 16 }}>
              Editor de Autómatas / Grafos
            </div>
            <div style={{ fontSize: 12, color: "#555" }}>
              Diseña autómatas, guárdalos en JSON y envíalos al backend.
            </div>
          </div>

          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <button onClick={addNode}>+ Nodo</button>
            <button onClick={exportAutomaton}>Exportar JSON</button>
            <button onClick={() => setShowAnalyzeModal(true)}>Analizar</button>
            <span style={{ marginLeft: 8, color: "#666", fontSize: 12 }}>
              Tip: arrastra desde arriba o abajo de un nodo a otro para crear
              una arista, o arrastra el extremo de una arista existente para
              reconectarla.
            </span>
          </div>
        </div>

        <div style={{ flex: 1 }}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onReconnect={onReconnect}
            onReconnectStart={onReconnectStart}
            onReconnectEnd={onReconnectEnd}
            onSelectionChange={onSelectionChange}
            connectionMode="loose" //Para poder conectar cualquier nodo con otro en cualquier dirección
            fitView
          >
            <Background />
            <MiniMap />
            <Controls />
          </ReactFlow>
        </div>
      </div>

      <aside
        style={{
          width: 260,
          borderLeft: "1px solid #ddd",
          padding: 10,
          overflow: "auto",
          background: "#fafafa",
        }}
      >
        <h3 style={{ margin: "4px 0 8px", fontSize: 14 }}>Editor</h3>

        {/*al utilizar && solo dibuja lo de la derecha si la condición de la izquierda es verdadera */}
        {!selected && (
          <p style={{ color: "#666", fontSize: 13 }}>
            Selecciona un nodo o una arista para editar sus campos.
          </p>
        )}

        {/*al utilizar <>...</> agrupa varios elementos sin añadir un div extra al diseño*/}
        {selectedNode && (
          <>
            <p style={{ margin: "8px 0", fontSize: 13 }}>
              <b>Nodo:</b> {selectedNode.data?.name ?? selectedNode.id}
            </p>

            <label style={{ fontSize: 12, color: "#444" }}>name</label>
            <input
              style={{ width: "100%", marginBottom: 10 }}
              value={selectedNode.data?.name ?? ""}
              onChange={(e) => updateNodeField("name", e.target.value)}
            />

            <label style={{ fontSize: 12, color: "#444" }}>flow</label>
            <textarea
              style={{ width: "100%", marginBottom: 10 }}
              rows={3}
              value={selectedNode.data?.flow ?? ""}
              onChange={(e) => updateNodeField("flow", e.target.value)}
            />

            <label style={{ fontSize: 12, color: "#444" }}>invariant</label>
            <textarea
              style={{ width: "100%" }}
              rows={3}
              placeholder="True"
              value={selectedNode.data?.invariant ?? ""}
              onChange={(e) => updateNodeField("invariant", e.target.value)}
            />
            <p style={{ color: "#666", fontSize: 12, marginTop: 6 }}>
              Si se deja vacío, se usa "True" (sin restricciones).
            </p>
          </>
        )}

        {selectedEdge && (
          <>
            <p style={{ margin: "8px 0", fontSize: 13 }}>
              <b>Arista:</b> {selectedEdge.source} → {selectedEdge.target}
            </p>

            <label style={{ fontSize: 12, color: "#444" }}>guard</label>
            <textarea
              style={{ width: "100%" }}
              rows={3}
              placeholder="True"
              value={selectedEdge.data?.guard ?? ""}
              onChange={(e) => updateEdgeGuard(e.target.value)}
            />

            <p style={{ color: "#666", fontSize: 12, marginTop: 6 }}>
              El guard se muestra como etiqueta en la arista. Si se deja vacío,
              se usa "True" (la transición no tiene condición).
            </p>
          </>
        )}
      </aside>

      {showAnalyzeModal && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.35)",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            zIndex: 2000,
          }}
        >
          <div
            style={{
              background: "#fff",
              padding: 24,
              borderRadius: 12,
              minWidth: 380,
              boxShadow: "0 8px 30px rgba(0,0,0,0.2)",
            }}
          >
            <h2 style={{ marginTop: 0 }}>Parámetros de análisis</h2>

            <label style={{ display: "block", marginBottom: 12 }}>
              HA_type
              <select
                value={haType}
                onChange={(e) => setHaType(e.target.value)}
                style={{ display: "block", width: "100%", marginTop: 6 }}
              >
                <option value="polyhedral">polyhedral</option>
                <option value="linear">linear</option>
              </select>
            </label>

            <label style={{ display: "block", marginBottom: 18 }}>
              max_CEGAR_iteration
              <input
                type="number"
                min="1"
                value={maxCegarIteration}
                onChange={(e) => setMaxCegarIteration(Number(e.target.value))}
                style={{ display: "block", width: "100%", marginTop: 6 }}
              />
            </label>

            <div
              style={{ display: "flex", justifyContent: "flex-end", gap: 8 }}
            >
              <button
                onClick={() => setShowAnalyzeModal(false)}
                disabled={isAnalyzing}
              >
                Cancelar
              </button>
              <button onClick={analyzeAutomaton} disabled={isAnalyzing}>
                {isAnalyzing ? "Analizando..." : "Ejecutar análisis"}
              </button>
            </div>
          </div>
        </div>
      )}

      {showResultScreen && analysisResult && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "#ffffff",
            zIndex: 3000,
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            padding: 40,
            textAlign: "center",
            overflow: "auto",
          }}
        >
          <h1 style={{ fontSize: 40, marginBottom: 20 }}>
            Resultado del análisis
          </h1>

          <div style={{ fontSize: 22, marginBottom: 12 }}>
            {analysisResult.ok ? "Análisis completado" : "Error en el análisis"}
          </div>

          {analysisResult.answer !== undefined && (
            <div style={{ fontSize: 28, fontWeight: 700, marginBottom: 16 }}>
              Respuesta: {String(analysisResult.answer)}
            </div>
          )}

          {analysisResult.message && (
            <div
              style={{
                maxWidth: 900,
                fontSize: 18,
                color: "#444",
                marginBottom: 10,
              }}
            >
              {analysisResult.message}
            </div>
          )}

          {analysisResult.stable_message && (
            <pre
              style={{
                marginTop: 16,
                maxWidth: 1000,
                whiteSpace: "pre-wrap",
                textAlign: "left",
                background: "#f5f5f5",
                padding: 20,
                borderRadius: 10,
                border: "1px solid #ddd",
              }}
            >
              {analysisResult.stable_message}
            </pre>
          )}

          {analysisResult.errors && (
            <div style={{ marginTop: 16, textAlign: "left", maxWidth: 900 }}>
              <h3>Errores</h3>
              <ul>
                {analysisResult.errors.map((err, i) => (
                  <li key={i}>{err}</li>
                ))}
              </ul>
            </div>
          )}

          <button
            onClick={() => setShowResultScreen(false)}
            style={{ marginTop: 28, padding: "12px 20px", fontSize: 18 }}
          >
            Volver al editor
          </button>
        </div>
      )}
    </div>
  );
}
