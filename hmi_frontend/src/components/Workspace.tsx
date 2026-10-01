import { useState, useEffect, useRef } from "react";
import {
  Play, RotateCw, Square, Maximize2, ZoomIn, ZoomOut, RefreshCw,
  Download, FileJson, Printer, FileText, CheckCircle2, Shield, Search
} from "lucide-react";
import {
  ReactFlow, Background, Controls, MiniMap,
  useNodesState, useEdgesState, MarkerType,
  useReactFlow, ReactFlowProvider
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import ELK from 'elkjs/lib/elk.bundled.js';
import CustomNode from './CustomNode';

const elk = new ELK();
const nodeTypes = { custom: CustomNode };

/** Layout with ELK */
const getLayoutedElements = async (nodes: any[], edges: any[], nodeW = 240, nodeH = 95) => {
  if (!nodes.length) return { nodes, edges };
  const graph = {
    id: 'root',
    layoutOptions: {
      'elk.algorithm': 'layered',
      'elk.direction': 'RIGHT',
      'elk.layered.spacing.nodeNodeBetweenLayers': '120',
      'elk.spacing.nodeNode': '50',
      'elk.layered.layering.strategy': 'NETWORK_SIMPLEX',
      'elk.edgeRouting': 'SPLINES',
      'elk.padding': '[top=40,left=40,bottom=40,right=40]',
      'elk.layered.nodePlacement.strategy': 'BRANDES_KOEPF',
    },
    children: nodes.map((n) => ({ id: n.id, width: nodeW, height: nodeH })),
    edges: edges.map((e) => ({ id: e.id, sources: [e.source], targets: [e.target] })),
  };
  try {
    const layouted = await elk.layout(graph);
    return {
      nodes: nodes.map((node) => {
        const n = layouted.children?.find((c: any) => c.id === node.id);
        return { ...node, position: { x: n?.x ?? 0, y: n?.y ?? 0 } };
      }),
      edges,
    };
  } catch (e) {
    console.error('ELK error', e);
    return { nodes, edges };
  }
};

/** Normalize ASIL: "ASIL_D" → "ASIL-D" */
function normalizeAsil(level: string): string {
  if (!level) return 'QM';
  return level.replace('ASIL_', 'ASIL-');
}

/** Extract sets for graph highlighting */
function extractSets(analysisData: any, seedArtifactId: string) {
  const report = analysisData?.report || {};
  const seedId = report.changed_artifact_id || seedArtifactId;

  const impactedIds = new Set<string>();
  const testIds = new Set<string>();
  const decisionIds = new Set<string>();
  const acceptedIds = new Set<string>();

  (report.decisions || []).forEach((d: any) => {
    decisionIds.add(d.artifact_id);
    if (d.decision && !d.decision.includes('REJECT')) {
      acceptedIds.add(d.artifact_id);
      if (d.stage === 'GRAPH' || d.stage === 'SEMANTIC') {
        impactedIds.add(d.artifact_id);
      }
    }
  });

  (report.impact_items || report.impacted_artifacts || []).forEach((a: any) => {
    const id = a.artifact_id || a.id;
    if (id) { impactedIds.add(id); acceptedIds.add(id); }
  });

  (report.test_items || report.tests_requiring_execution || []).forEach((t: any) => {
    const id = typeof t === 'string' ? t : t.artifact_id || t.id;
    if (id) { testIds.add(id); acceptedIds.add(id); }
  });

  return { seedId, impactedIds, testIds, decisionIds, acceptedIds };
}

/** Build display subgraph using BFS */
function buildDisplaySubgraph(
  fullGraph: any,
  seedId: string,
  impactedIds: Set<string>,
  testIds: Set<string>,
  decisionIds: Set<string>,
) {
  const allLinks: any[] = fullGraph.links || [];
  const nodeMap = new Map<string, any>();
  for (const n of (fullGraph.nodes || [])) nodeMap.set(n.id, n);

  const adj = new Map<string, Set<string>>();
  for (const link of allLinks) {
    if (!adj.has(link.source)) adj.set(link.source, new Set());
    if (!adj.has(link.target)) adj.set(link.target, new Set());
    adj.get(link.source)!.add(link.target);
    adj.get(link.target)!.add(link.source);
  }

  const coreIds = new Set<string>();
  if (seedId && nodeMap.has(seedId)) coreIds.add(seedId);
  impactedIds.forEach(id => { if (nodeMap.has(id)) coreIds.add(id); });
  testIds.forEach(id => { if (nodeMap.has(id)) coreIds.add(id); });
  decisionIds.forEach(id => { if (nodeMap.has(id)) coreIds.add(id); });

  const visible = new Set<string>(coreIds);
  const queue = [...coreIds];
  const depth = new Map<string, number>();
  queue.forEach(id => depth.set(id, 0));

  let qi = 0;
  while (qi < queue.length && visible.size < 60) {
    const cur = queue[qi++];
    const curDepth = depth.get(cur) ?? 0;
    if (curDepth >= 2) continue;
    const neighbors = adj.get(cur) || new Set();
    for (const nxt of neighbors) {
      if (!visible.has(nxt) && visible.size < 60) {
        visible.add(nxt);
        depth.set(nxt, curDepth + 1);
        queue.push(nxt);
      }
    }
  }

  if (visible.size <= 1 && fullGraph.nodes?.length > 1) {
    const seedNode = nodeMap.get(seedId);
    const sub = seedNode?.subsystem || 'ADAS';
    for (const n of fullGraph.nodes) {
      if (visible.size >= 25) break;
      if (n.subsystem === sub || !seedNode) visible.add(n.id);
    }
  }

  const subNodes = (fullGraph.nodes || []).filter((n: any) => visible.has(n.id));
  const subEdges = allLinks.filter((l: any) => visible.has(l.source) && visible.has(l.target));

  return { nodes: subNodes, edges: subEdges };
}

// ---- ReactFlow Canvas ----
function FlowCanvas({ nodes, edges, onNodesChange, onEdgesChange, onNodeClick, fitViewRef, zoomInRef, zoomOutRef, resetRef, highlightNodeId }: any) {
  const { fitView, zoomIn, zoomOut, setCenter } = useReactFlow();

  useEffect(() => {
    if (fitViewRef) fitViewRef.current = () => fitView({ duration: 500, padding: 0.12 });
    if (zoomInRef) zoomInRef.current = () => zoomIn({ duration: 300 });
    if (zoomOutRef) zoomOutRef.current = () => zoomOut({ duration: 300 });
    if (resetRef) resetRef.current = () => fitView({ duration: 500, padding: 0.2 });
  }, [fitView, zoomIn, zoomOut, fitViewRef, zoomInRef, zoomOutRef, resetRef]);

  useEffect(() => {
    if (!highlightNodeId) return;
    const node = nodes.find((n: any) => n.id === highlightNodeId);
    if (node && node.position) {
      setCenter(node.position.x + 120, node.position.y + 47, { zoom: 1.5, duration: 600 });
    }
  }, [highlightNodeId, nodes, setCenter]);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onNodeClick={onNodeClick}
      nodeTypes={nodeTypes}
      fitView
      fitViewOptions={{ padding: 0.15 }}
      minZoom={0.05}
      maxZoom={2.5}
      className="bg-slate-50"
      defaultEdgeOptions={{ animated: false }}
    >
      <Background color="#cbd5e1" gap={24} size={1} />
      <Controls showInteractive={false} className="shadow border border-gray-200 rounded" />
      <MiniMap
        className="shadow border border-gray-200 rounded"
        nodeColor={(n: any) => {
          if (n.data?.isSeed) return '#1e293b';
          if (n.data?.isImpacted) return '#ef4444';
          if (n.data?.isTest) return '#0891b2';
          if (n.data?.isDecision) return '#a78bfa';
          return '#94a3b8';
        }}
        maskColor="rgba(241,245,249,0.6)"
      />
    </ReactFlow>
  );
}

// ---- Types ----
type WorkspaceProps = {
  activeMenu: string;
  analysisData: any;
  onSelectNode: (node: any) => void;
  onRunAnalysis: (id?: string) => void;
  isLoading: boolean;
  artifactId: string;
  setArtifactId: (id: string) => void;
  highlightNodeId: string | null;
  forceTab: string | null;
  onForceTabConsumed: () => void;
};

export default function Workspace(props: WorkspaceProps) {
  return (
    <ReactFlowProvider>
      <WorkspaceInner {...props} />
    </ReactFlowProvider>
  );
}

function WorkspaceInner({
  activeMenu, analysisData, onSelectNode, onRunAnalysis, isLoading, artifactId, setArtifactId,
  highlightNodeId, forceTab, onForceTabConsumed,
}: WorkspaceProps) {
  const [activeTab, setActiveTab] = useState('Impact Graph');
  const [nodes, setNodes, onNodesChange] = useNodesState<any>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<any>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [showFullGraph, setShowFullGraph] = useState(false);

  const fitViewRef = useRef<(() => void) | null>(null);
  const zoomInRef = useRef<(() => void) | null>(null);
  const zoomOutRef = useRef<(() => void) | null>(null);
  const resetRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    if (forceTab) {
      setActiveTab(forceTab);
      onForceTabConsumed();
    }
  }, [forceTab, onForceTabConsumed]);

  // Map sidebar menu selection directly to tab / view
  useEffect(() => {
    switch (activeMenu) {
      case 'Home': setActiveTab('Executive Summary'); break;
      case 'System Requirements':
      case 'Software Requirements':
      case 'Safety Requirements': setActiveTab('Requirements View'); break;
      case 'ECUs':
      case 'Software Components':
      case 'Ports':
      case 'Runnables': setActiveTab('Architecture View'); break;
      case 'C Functions':
      case 'C++ Functions':
      case 'RTE Interfaces': setActiveTab('Source Code View'); break;
      case 'Current Analysis':
      case 'Change Seeds':
      case 'Analysis History': setActiveTab('Change Analysis View'); break;
      case 'Impact Tree': setActiveTab('Impact Graph'); break;
      case 'Traceability Matrix': setActiveTab('Traceability Matrix'); break;
      case 'Test Cases':
      case 'Regression Selection':
      case 'Safety Tests': setActiveTab('Testing View'); break;
      case 'ASIL Analysis':
      case 'Safety Gate': setActiveTab('Safety View'); break;
      case 'Decision Trail':
      case 'Audit Evidence':
      case 'Raw JSON': setActiveTab('Evidence View'); break;
      default: setActiveTab('Impact Graph'); break;
    }
  }, [activeMenu]);

  // Build graph
  useEffect(() => {
    if (!analysisData?.full_graph) {
      setNodes([]);
      setEdges([]);
      return;
    }

    const buildGraph = async () => {
      const { seedId, impactedIds, testIds, decisionIds, acceptedIds } = extractSets(analysisData, artifactId);

      let graphNodes: any[];
      let graphLinks: any[];

      if (showFullGraph) {
        graphNodes = analysisData.full_graph.nodes;
        graphLinks = analysisData.full_graph.links;
      } else {
        const sub = buildDisplaySubgraph(analysisData.full_graph, seedId, impactedIds, testIds, decisionIds);
        graphNodes = sub.nodes;
        graphLinks = sub.edges;
      }

      const rawNodes = graphNodes.map((n: any) => ({
        id: n.id,
        type: 'custom',
        position: { x: 0, y: 0 },
        data: {
          ...n,
          safety_level: normalizeAsil(n.safety_level || ''),
          isImpacted: impactedIds.has(n.id),
          isTest: testIds.has(n.id),
          isSeed: n.id === seedId,
          isDecision: decisionIds.has(n.id) && !impactedIds.has(n.id) && !testIds.has(n.id) && n.id !== seedId,
          isAccepted: acceptedIds.has(n.id),
          isHighlighted: n.id === highlightNodeId,
        },
      }));

      const rawEdges = graphLinks.map((e: any, i: number) => {
        const isSemantic = e.edge_type === 'SEMANTIC' || e.relation === 'SEMANTIC_SIMILARITY';
        const srcImpacted = impactedIds.has(e.source) || e.source === seedId || acceptedIds.has(e.source);
        const tgtImpacted = impactedIds.has(e.target) || e.target === seedId || acceptedIds.has(e.target);
        const isImpactPath = srcImpacted && tgtImpacted;

        return {
          id: `e-${i}-${e.source}-${e.target}`,
          source: e.source,
          target: e.target,
          type: 'smoothstep',
          animated: isImpactPath,
          style: {
            stroke: isSemantic ? '#8b5cf6' : isImpactPath ? '#ef4444' : '#cbd5e1',
            strokeWidth: isImpactPath ? 2.5 : 1.2,
            strokeDasharray: isSemantic ? '4,4' : undefined,
          },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            width: 14,
            height: 14,
            color: isSemantic ? '#8b5cf6' : isImpactPath ? '#ef4444' : '#cbd5e1',
          },
          label: (isImpactPath && !isSemantic) ? (e.relation || '') : '',
          labelStyle: { fontSize: 10, fill: '#374151', fontWeight: 500 },
          labelBgStyle: { fill: '#fff', fillOpacity: 0.9 },
          labelBgPadding: [4, 2] as [number, number],
          labelBgBorderRadius: 3,
        };
      });

      const { nodes: ln, edges: le } = await getLayoutedElements(rawNodes, rawEdges, 240, 95);
      setNodes(ln);
      setEdges(le);
    };

    buildGraph();
  }, [analysisData, showFullGraph, artifactId, highlightNodeId, setNodes, setEdges]);

  const tabs = ['Executive Summary', 'Impact Graph', 'Requirements View', 'Architecture View', 'Source Code View', 'Testing View', 'Safety View', 'Evidence View', 'Traceability Matrix'];

  const report = analysisData?.report || {};
  const allDecisions = report.decisions || [];
  const impactedArtifacts = (report.impact_items || report.impacted_artifacts || []);
  const testArtifacts = (report.test_items || report.tests_requiring_execution || []);

  const handleExportJSON = () => {
    if (!analysisData) return;
    const blob = new Blob([JSON.stringify(analysisData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = `aura_impact_${artifactId}.json`; a.click();
    URL.revokeObjectURL(url);
  };

  const handleExportEvidence = () => {
    if (!analysisData) return;
    const lines = [
      'AURA-Impact Audit Evidence Report',
      `Generated: ${new Date().toISOString()}`,
      `Artifact: ${artifactId}`,
      `Analysis ID: ${report.analysis_id || '—'}`,
      '',
      '=== IMPACTED ARTIFACTS ===',
      ...impactedArtifacts.map((a: any) => `${a.artifact_id || a.id} [${a.artifact_type || a.type}]`),
      '',
      '=== TESTS REQUIRING EXECUTION ===',
      ...testArtifacts.map((t: any) => (typeof t === 'string' ? t : t.artifact_id || t.id || String(t))),
      '',
      '=== DECISIONS ===',
      ...allDecisions.map((d: any) => `${d.artifact_id} [${d.decision}] score=${d.confidence?.toFixed(3)} ${d.reason || ''}`),
    ];
    const blob = new Blob([lines.join('\n')], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = `aura_evidence_${artifactId}.txt`; a.click();
    URL.revokeObjectURL(url);
  };

  // Table rows: all decisions from the engine
  const tableRows = allDecisions.length > 0
    ? allDecisions.map((d: any) => ({
        artifact_id: d.artifact_id || d.id,
        type: d.artifact_type || 'Artifact',
        detection_stage: d.stage || 'SEMANTIC',
        similarity: d.confidence,
        justification: d.reason || d.decision,
        decision: d.decision,
      }))
    : [...impactedArtifacts, ...testArtifacts.map((t: any) => ({
        artifact_id: typeof t === 'string' ? t : t.artifact_id || t.id || String(t),
        type: 'Test Case',
        detection_stage: 'SAFETY_GATE',
        similarity: 1.0,
        justification: 'Safety gate mandatory test.',
        decision: 'ACCEPTED',
      }))];

  const filteredRows = tableRows.filter((a: any) =>
    !searchTerm || String(a.artifact_id).toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="h-full flex flex-col bg-gray-50 overflow-hidden">
      {/* Top Toolbar matching Image 1 */}
      <div className="h-10 flex items-center px-4 border-b border-gray-200 bg-white space-x-1 shrink-0">
        <button onClick={() => onRunAnalysis(artifactId)} disabled={isLoading} className="flex items-center space-x-1.5 text-xs font-medium text-gray-700 hover:bg-gray-100 px-2.5 py-1.5 rounded transition disabled:opacity-50 border border-transparent hover:border-gray-300">
          <Play className="w-3.5 h-3.5 text-green-600" /><span>Run Analysis</span>
        </button>
        <button onClick={() => onRunAnalysis(artifactId)} disabled={isLoading} className="flex items-center space-x-1.5 text-xs text-gray-600 hover:bg-gray-100 px-2 py-1.5 rounded transition border border-transparent hover:border-gray-300">
          <RotateCw className="w-3.5 h-3.5" /><span>Re-run</span>
        </button>
        <button className="flex items-center space-x-1.5 text-xs text-gray-400 px-2 py-1.5 rounded cursor-not-allowed">
          <Square className="w-3.5 h-3.5" /><span>Stop</span>
        </button>
        <div className="w-px h-5 bg-gray-200 mx-1" />
        
        {/* Exact Graph Controls from Image 1 */}
        <button onClick={() => fitViewRef.current?.()} className="flex items-center space-x-1.5 text-xs text-gray-700 hover:bg-gray-100 px-2.5 py-1.5 rounded transition border border-transparent hover:border-gray-300">
          <Maximize2 className="w-3.5 h-3.5 text-[#0f4a66]" /><span>Fit Graph</span>
        </button>
        <button onClick={() => zoomInRef.current?.()} className="flex items-center space-x-1.5 text-xs text-gray-700 hover:bg-gray-100 px-2.5 py-1.5 rounded transition border border-transparent hover:border-gray-300">
          <ZoomIn className="w-3.5 h-3.5 text-[#0f4a66]" /><span>Zoom In</span>
        </button>
        <button onClick={() => zoomOutRef.current?.()} className="flex items-center space-x-1.5 text-xs text-gray-700 hover:bg-gray-100 px-2.5 py-1.5 rounded transition border border-transparent hover:border-gray-300">
          <ZoomOut className="w-3.5 h-3.5 text-[#0f4a66]" /><span>Zoom Out</span>
        </button>
        <button onClick={() => resetRef.current?.()} className="flex items-center space-x-1.5 text-xs text-gray-700 hover:bg-gray-100 px-2.5 py-1.5 rounded transition border border-transparent hover:border-gray-300">
          <RefreshCw className="w-3.5 h-3.5 text-[#0f4a66]" /><span>Reset</span>
        </button>

        <div className="flex-1" />
        <button onClick={handleExportEvidence} className="flex items-center space-x-1.5 text-xs text-gray-600 hover:bg-gray-100 px-2 py-1.5 rounded transition border border-transparent hover:border-gray-300">
          <Download className="w-3.5 h-3.5" /><span>Export Evidence</span>
        </button>
        <button onClick={handleExportJSON} className="flex items-center space-x-1.5 text-xs text-gray-600 hover:bg-gray-100 px-2 py-1.5 rounded transition border border-transparent hover:border-gray-300">
          <FileJson className="w-3.5 h-3.5" /><span>Export JSON</span>
        </button>
        <button onClick={() => window.print()} className="flex items-center space-x-1.5 text-xs text-gray-600 hover:bg-gray-100 px-2 py-1.5 rounded transition border border-transparent hover:border-gray-300">
          <Printer className="w-3.5 h-3.5" /><span>Print</span>
        </button>
      </div>

      {/* Breadcrumb Header */}
      <div className="px-6 pt-3 pb-2.5 bg-white border-b border-gray-200 shrink-0">
        <div className="flex items-center text-xs text-teal-700 font-medium mb-1 space-x-1">
          <CheckCircle2 className="w-3 h-3" />
          <span>AURA-Impact</span><span className="text-gray-400">/</span>
          <span>Navigation</span><span className="text-gray-400">/</span>
          <span className="font-semibold text-teal-800">{activeMenu}</span>
        </div>
        <div className="flex items-center justify-between">
          <h1 className="text-lg font-bold text-gray-900">{activeMenu}</h1>
          <div className="text-xs text-gray-500 flex items-center space-x-2">
            <span>Seed: <strong className="text-gray-800 font-mono">{artifactId}</strong></span>
            <span className="text-gray-300">|</span>
            <span>Nodes: {analysisData?.full_graph?.nodes?.length || 0}</span>
          </div>
        </div>
      </div>

      {/* Workspace View Navigation Tabs */}
      <div className="flex border-b border-gray-200 bg-white px-4 shrink-0 overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-3 py-2 text-xs font-medium border-b-2 transition whitespace-nowrap ${
              activeTab === tab ? 'border-teal-600 text-teal-700 font-semibold' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {activeTab === 'Impact Graph' && (
          <ImpactGraphView
            analysisData={analysisData}
            artifactId={artifactId}
            setArtifactId={setArtifactId}
            isLoading={isLoading}
            onRunAnalysis={onRunAnalysis}
            onSelectNode={onSelectNode}
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            showFullGraph={showFullGraph}
            setShowFullGraph={setShowFullGraph}
            fitViewRef={fitViewRef}
            zoomInRef={zoomInRef}
            zoomOutRef={zoomOutRef}
            resetRef={resetRef}
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            filteredRows={filteredRows}
            handleExportEvidence={handleExportEvidence}
            highlightNodeId={highlightNodeId}
          />
        )}
        {activeTab === 'Executive Summary' && <ExecutiveSummaryView analysisData={analysisData} artifactId={artifactId} />}
        {activeTab === 'Requirements View' && <RequirementsView analysisData={analysisData} activeMenu={activeMenu} onSelectNode={onSelectNode} onRunAnalysis={onRunAnalysis} />}
        {activeTab === 'Architecture View' && <ArchitectureView analysisData={analysisData} activeMenu={activeMenu} onSelectNode={onSelectNode} />}
        {activeTab === 'Source Code View' && <SourceCodeView analysisData={analysisData} activeMenu={activeMenu} onSelectNode={onSelectNode} />}
        {activeTab === 'Change Analysis View' && <ChangeAnalysisView activeMenu={activeMenu} onRunAnalysis={onRunAnalysis} setArtifactId={setArtifactId} />}
        {activeTab === 'Testing View' && <TestingView analysisData={analysisData} activeMenu={activeMenu} onSelectNode={onSelectNode} />}
        {activeTab === 'Safety View' && <SafetyView analysisData={analysisData} activeMenu={activeMenu} />}
        {activeTab === 'Evidence View' && <EvidenceView analysisData={analysisData} artifactId={artifactId} activeMenu={activeMenu} />}
        {activeTab === 'Traceability Matrix' && <TraceabilityMatrixView analysisData={analysisData} />}
      </div>
    </div>
  );
}

// ---- Impact Graph View ----
function ImpactGraphView({
  analysisData, artifactId, setArtifactId, isLoading, onRunAnalysis, onSelectNode,
  nodes, edges, onNodesChange, onEdgesChange,
  showFullGraph, setShowFullGraph,
  fitViewRef, zoomInRef, zoomOutRef, resetRef,
  searchTerm, setSearchTerm, filteredRows, handleExportEvidence,
  highlightNodeId,
}: any) {
  return (
    <div className="flex-1 flex flex-col overflow-hidden min-h-0">
      {/* Control bar */}
      <div className="flex items-center space-x-2 px-4 py-2 bg-white border-b border-gray-200 shrink-0">
        <span className="text-xs text-gray-600 font-medium">Artifact ID:</span>
        <input
          type="text"
          value={artifactId}
          onChange={(e) => setArtifactId(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') onRunAnalysis(artifactId); }}
          className="border border-gray-300 rounded px-2 py-1 text-xs w-44 focus:outline-none focus:ring-2 focus:ring-teal-400 focus:border-transparent font-mono"
          placeholder="e.g. REQ_AEB_014"
        />
        <button
          onClick={() => onRunAnalysis(artifactId)}
          disabled={isLoading}
          className="bg-[#0f4a66] hover:bg-[#165a78] text-white text-xs px-3 py-1.5 rounded transition font-medium disabled:opacity-50 flex items-center space-x-1"
        >
          {isLoading ? <><RotateCw className="w-3 h-3 animate-spin" /><span>Running...</span></> : <span>Display Report</span>}
        </button>
        <div className="ml-auto flex items-center space-x-2">
          {analysisData && (
            <div className="flex items-center rounded border border-gray-200 overflow-hidden text-xs">
              <button
                onClick={() => setShowFullGraph(false)}
                className={`px-2.5 py-1 transition ${!showFullGraph ? 'bg-[#0f4a66] text-white font-medium' : 'bg-white text-gray-600 hover:bg-gray-50'}`}
              >Impact View</button>
              <button
                onClick={() => setShowFullGraph(true)}
                className={`px-2.5 py-1 transition ${showFullGraph ? 'bg-[#0f4a66] text-white font-medium' : 'bg-white text-gray-600 hover:bg-gray-50'}`}
              >{`Full Graph (${analysisData.full_graph?.nodes?.length || 0})`}</button>
            </div>
          )}
          {analysisData && (
            <span className="text-xs text-gray-400">{nodes.length} nodes</span>
          )}
          <div className="flex items-center border border-gray-200 rounded bg-gray-50 px-1">
            <button onClick={() => zoomInRef.current?.()} className="p-1 hover:bg-gray-200 rounded transition" title="Zoom In"><ZoomIn className="w-3.5 h-3.5 text-gray-600" /></button>
            <button onClick={() => zoomOutRef.current?.()} className="p-1 hover:bg-gray-200 rounded transition" title="Zoom Out"><ZoomOut className="w-3.5 h-3.5 text-gray-600" /></button>
            <button onClick={() => fitViewRef.current?.()} className="p-1 hover:bg-gray-200 rounded transition" title="Fit View"><Maximize2 className="w-3.5 h-3.5 text-gray-600" /></button>
            <button onClick={() => resetRef.current?.()} className="p-1 hover:bg-gray-200 rounded transition" title="Reset"><RefreshCw className="w-3.5 h-3.5 text-gray-600" /></button>
          </div>
        </div>
      </div>

      {/* Lane headers */}
      <div className="flex items-stretch px-6 py-2 bg-gray-50 border-b border-gray-200 gap-3 shrink-0">
        {[
          { label: 'Requirement', cls: 'bg-amber-50 text-amber-800 border-amber-200' },
          { label: 'Software Component', cls: 'bg-orange-50 text-orange-800 border-orange-200' },
          { label: 'Port / Runnable', cls: 'bg-green-50 text-green-800 border-green-200' },
          { label: 'C Function', cls: 'bg-blue-50 text-blue-800 border-blue-200' },
          { label: 'Test Case', cls: 'bg-cyan-50 text-cyan-800 border-cyan-200' },
        ].map((lane) => (
          <div key={lane.label} className={`flex-1 text-center text-xs font-semibold py-1.5 rounded border ${lane.cls}`}>
            {lane.label}
          </div>
        ))}
      </div>

      {/* Graph canvas */}
      <div className="flex-1 relative overflow-hidden" style={{ minHeight: 280 }}>
        {!analysisData ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-400 bg-white">
            <Shield className="w-12 h-12 mb-3 text-gray-200" />
            <p className="text-sm font-medium">No analysis data</p>
            <p className="text-xs mt-1">Enter an Artifact ID and click <strong>Display Report</strong></p>
          </div>
        ) : (
          <FlowCanvas
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={(_: any, node: any) => onSelectNode(node)}
            fitViewRef={fitViewRef}
            zoomInRef={zoomInRef}
            zoomOutRef={zoomOutRef}
            resetRef={resetRef}
            highlightNodeId={highlightNodeId}
          />
        )}
      </div>

      {/* Legend */}
      <div className="flex items-center justify-center flex-wrap gap-x-5 gap-y-1 px-4 py-2 bg-white border-t border-gray-200 text-xs text-gray-600 shrink-0">
        <span className="flex items-center space-x-1.5"><span className="inline-block w-7 h-0.5 bg-red-500"></span><span className="font-medium text-red-600">Impact Path</span></span>
        <span className="flex items-center space-x-1.5"><span className="inline-block w-7 h-0.5 bg-slate-400"></span><span>Structural</span></span>
        <span className="flex items-center space-x-1.5"><span className="inline-block w-7 border-t-2 border-dashed border-purple-400"></span><span className="text-purple-600">Semantic</span></span>
        {[
          { color: '#d97706', label: 'Requirement' }, { color: '#ea580c', label: 'SWC' },
          { color: '#16a34a', label: 'Runnable' }, { color: '#2563eb', label: 'C Function' },
          { color: '#0891b2', label: 'Test' }, { color: '#dc2626', label: 'Impacted' },
          { color: '#1e293b', label: 'Seed' }, { color: '#a78bfa', label: 'Evaluated' },
        ].map((item) => (
          <span key={item.label} className="flex items-center space-x-1">
            <span className="inline-block w-3 h-3 rounded" style={{ background: item.color }}></span>
            <span>{item.label}</span>
          </span>
        ))}
      </div>

      {/* Decisions table */}
      <div className="flex flex-col bg-white border-t border-gray-200" style={{ maxHeight: 240, minHeight: 150, overflowY: 'auto' }}>
        <div className="flex items-center justify-between px-4 py-2 border-b border-gray-200 bg-gray-50 shrink-0">
          <span className="text-sm font-semibold text-gray-700">
            Analysis Decisions
            {analysisData && <span className="ml-2 text-xs font-normal text-gray-400">({filteredRows.length} artifacts evaluated)</span>}
          </span>
          <div className="flex items-center space-x-3">
            <div className="flex items-center border border-gray-200 rounded px-2 py-1 bg-white">
              <Search className="w-3 h-3 text-gray-400 mr-1" />
              <input type="text" placeholder="Filter..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="text-xs outline-none w-28" />
            </div>
            <button onClick={handleExportEvidence} className="flex items-center space-x-1 text-xs text-gray-600 hover:bg-gray-100 px-2 py-1 rounded transition">
              <Download className="w-3.5 h-3.5" /><span>Export</span>
            </button>
          </div>
        </div>
        <div className="overflow-auto flex-1">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="sticky top-0 bg-gray-50 z-10">
              <tr className="border-b border-gray-200 text-gray-500">
                <th className="px-4 py-2 font-medium">Artifact ID</th>
                <th className="px-4 py-2 font-medium">Type</th>
                <th className="px-4 py-2 font-medium">Stage</th>
                <th className="px-4 py-2 font-medium">Score</th>
                <th className="px-4 py-2 font-medium">Decision</th>
                <th className="px-4 py-2 font-medium w-full">Reason</th>
              </tr>
            </thead>
            <tbody>
              {!analysisData ? (
                <tr><td colSpan={6} className="px-4 py-6 text-center text-gray-400">Run an analysis to see results</td></tr>
              ) : filteredRows.length === 0 ? (
                <tr><td colSpan={6} className="px-4 py-6 text-center text-gray-400">No decisions found</td></tr>
              ) : (
                filteredRows.map((row: any, i: number) => {
                  const isAccepted = row.decision && !row.decision.includes('REJECT');
                  return (
                    <tr
                      key={i}
                      className={`border-b border-gray-100 hover:bg-blue-50 cursor-pointer transition ${isAccepted ? '' : 'opacity-60'}`}
                      onClick={() => onSelectNode({ id: row.artifact_id, data: { id: row.artifact_id, type: row.type, safety_level: '' } })}
                    >
                      <td className="px-4 py-2 font-mono text-blue-600 flex items-center space-x-1.5">
                        <FileText className="w-3.5 h-3.5 text-gray-400 shrink-0" />
                        <span className="hover:underline">{row.artifact_id}</span>
                      </td>
                      <td className="px-4 py-2 text-gray-700">{row.type}</td>
                      <td className="px-4 py-2">
                        <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-gray-100 text-gray-600">{row.detection_stage}</span>
                      </td>
                      <td className="px-4 py-2 text-gray-700">
                        {typeof row.similarity === 'number' ? row.similarity.toFixed(4) : '—'}
                      </td>
                      <td className="px-4 py-2">
                        <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${isAccepted ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'}`}>
                          {row.decision}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-gray-500 text-[11px]">{row.justification}</td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ---- Sub-views ----
function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 bg-white text-gray-400">
      <Shield className="w-12 h-12 mb-3 text-gray-200" />
      <p className="text-sm font-medium text-gray-600">{message}</p>
    </div>
  );
}

function RequirementsView({ analysisData, activeMenu, onSelectNode, onRunAnalysis }: any) {
  if (!analysisData) return <EmptyState message="Run analysis to inspect requirements" />;
  const nodes = analysisData.full_graph?.nodes || [];
  const reqs = nodes.filter((n: any) => n.type === 'Requirement');

  return (
    <div className="flex-1 overflow-auto p-6 bg-white">
      <div className="flex items-center justify-between mb-4 border-b border-gray-200 pb-3">
        <div>
          <h2 className="text-base font-bold text-gray-800">{activeMenu} ({reqs.length})</h2>
          <p className="text-xs text-gray-500 mt-0.5">Ingested requirements from specification dataset</p>
        </div>
      </div>
      <div className="border border-gray-200 rounded overflow-hidden shadow-sm">
        <table className="w-full text-left text-xs border-collapse">
          <thead className="bg-gray-50 border-b border-gray-200 text-gray-600 font-semibold">
            <tr>
              <th className="px-4 py-2.5">Requirement ID</th>
              <th className="px-4 py-2.5">Title / Name</th>
              <th className="px-4 py-2.5">Subsystem</th>
              <th className="px-4 py-2.5">ECU</th>
              <th className="px-4 py-2.5">ASIL Level</th>
              <th className="px-4 py-2.5 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {reqs.map((r: any) => (
              <tr key={r.id} className="hover:bg-blue-50 transition cursor-pointer" onClick={() => onSelectNode({ id: r.id, data: r })}>
                <td className="px-4 py-2.5 font-mono text-blue-600 font-medium">{r.id}</td>
                <td className="px-4 py-2.5 text-gray-800">{r.name || r.id}</td>
                <td className="px-4 py-2.5 text-gray-600">{r.subsystem || 'ADAS'}</td>
                <td className="px-4 py-2.5 text-gray-600">{r.ecu || 'ECU_1'}</td>
                <td className="px-4 py-2.5">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    r.safety_level?.includes('D') ? 'bg-red-100 text-red-700' :
                    r.safety_level?.includes('C') ? 'bg-amber-100 text-amber-700' : 'bg-gray-100 text-gray-700'
                  }`}>{normalizeAsil(r.safety_level)}</span>
                </td>
                <td className="px-4 py-2.5 text-right">
                  <button onClick={(e) => { e.stopPropagation(); onRunAnalysis(r.id); }} className="bg-[#0f4a66] hover:bg-[#165a78] text-white px-2.5 py-1 rounded text-[11px] font-medium transition">
                    Analyze Impact
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ArchitectureView({ analysisData, activeMenu, onSelectNode }: any) {
  if (!analysisData) return <EmptyState message="Run analysis to inspect architecture" />;
  const nodes = analysisData.full_graph?.nodes || [];

  let filtered = nodes;
  if (activeMenu === 'Software Components') filtered = nodes.filter((n: any) => n.type === 'SoftwareComponent' || n.type === 'SWC');
  else if (activeMenu === 'Ports') filtered = nodes.filter((n: any) => n.type === 'Port');
  else if (activeMenu === 'Runnables') filtered = nodes.filter((n: any) => n.type === 'Runnable');
  else if (activeMenu === 'ECUs') filtered = Array.from(new Set(nodes.map((n: any) => n.ecu || 'ECU_1'))).map((ecu) => ({ id: String(ecu), type: 'ECU', ecu }));

  return (
    <div className="flex-1 overflow-auto p-6 bg-white">
      <h2 className="text-base font-bold text-gray-800 mb-4">{activeMenu} ({filtered.length})</h2>
      <div className="border border-gray-200 rounded overflow-hidden shadow-sm">
        <table className="w-full text-left text-xs border-collapse">
          <thead className="bg-gray-50 border-b border-gray-200 text-gray-600 font-semibold">
            <tr>
              <th className="px-4 py-2.5">Identifier</th>
              <th className="px-4 py-2.5">Type</th>
              <th className="px-4 py-2.5">Subsystem</th>
              <th className="px-4 py-2.5">ECU Host</th>
              <th className="px-4 py-2.5">Source File</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filtered.map((item: any, idx: number) => (
              <tr key={idx} className="hover:bg-blue-50 transition cursor-pointer" onClick={() => onSelectNode({ id: item.id, data: item })}>
                <td className="px-4 py-2.5 font-mono text-teal-700 font-semibold">{item.id}</td>
                <td className="px-4 py-2.5 text-gray-600">{item.type}</td>
                <td className="px-4 py-2.5 text-gray-600">{item.subsystem || 'ADAS'}</td>
                <td className="px-4 py-2.5 text-gray-600">{item.ecu || 'ECU_1'}</td>
                <td className="px-4 py-2.5 text-gray-500 font-mono text-[11px] truncate max-w-xs">{item.source_file || 'arxml/adas_components.arxml'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function SourceCodeView({ analysisData, activeMenu, onSelectNode }: any) {
  if (!analysisData) return <EmptyState message="Run analysis to inspect source code" />;
  const nodes = analysisData.full_graph?.nodes || [];
  const funcs = nodes.filter((n: any) => n.type === 'C_Function' || n.type === 'Function');

  return (
    <div className="flex-1 overflow-auto p-6 bg-white">
      <h2 className="text-base font-bold text-gray-800 mb-4">{activeMenu} ({funcs.length})</h2>
      <div className="border border-gray-200 rounded overflow-hidden shadow-sm">
        <table className="w-full text-left text-xs border-collapse">
          <thead className="bg-gray-50 border-b border-gray-200 text-gray-600 font-semibold">
            <tr>
              <th className="px-4 py-2.5">C Function Name</th>
              <th className="px-4 py-2.5">Subsystem</th>
              <th className="px-4 py-2.5">File Location</th>
              <th className="px-4 py-2.5">ASIL Level</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {funcs.map((f: any) => (
              <tr key={f.id} className="hover:bg-blue-50 transition cursor-pointer" onClick={() => onSelectNode({ id: f.id, data: f })}>
                <td className="px-4 py-2.5 font-mono text-blue-600 font-semibold">{f.id}</td>
                <td className="px-4 py-2.5 text-gray-600">{f.subsystem || 'ADAS'}</td>
                <td className="px-4 py-2.5 text-gray-500 font-mono text-[11px]">{f.source_file || 'src/aeb_controller.c'}</td>
                <td className="px-4 py-2.5">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-gray-100 text-gray-700">{normalizeAsil(f.safety_level)}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ChangeAnalysisView({ activeMenu, onRunAnalysis, setArtifactId }: any) {
  const seedScenarios = [
    { id: 'REQ_AEB_014', title: 'Hidden Semantic Dependency', type: 'Requirement', subsystem: 'ADAS', desc: 'Emergency deceleration brake trigger clamp hydraulic braking hazard' },
    { id: 'REQ_AEB_001', title: 'Explicit Structural Impact', type: 'Requirement', subsystem: 'ADAS', desc: 'Time-to-collision calculation TTC radar distance ego speed' },
    { id: 'REQ_BODY_005', title: 'Decoy Distractor Rejection', type: 'Requirement', subsystem: 'Body_Electronics', desc: 'Cabin temperature interior climate defroster blower power level' },
    { id: 'REQ_AMB_099', title: 'Ambiguous Abstention', type: 'Requirement', subsystem: 'ADAS', desc: 'Ambiguous unclear driver alert notification without technical parameters' },
  ];

  return (
    <div className="flex-1 overflow-auto p-6 bg-white">
      <h2 className="text-base font-bold text-gray-800 mb-2">{activeMenu}</h2>
      <p className="text-xs text-gray-500 mb-4">Run change impact analysis benchmarks across automotive engineering seed changes.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {seedScenarios.map((s) => (
          <div key={s.id} className="border border-gray-200 rounded-lg p-4 bg-gray-50 hover:bg-blue-50/50 transition">
            <div className="flex items-center justify-between mb-2">
              <span className="font-mono text-sm font-bold text-[#0f4a66]">{s.id}</span>
              <span className="text-[10px] bg-teal-100 text-teal-800 font-semibold px-2 py-0.5 rounded">{s.subsystem}</span>
            </div>
            <h3 className="text-xs font-semibold text-gray-800 mb-1">{s.title}</h3>
            <p className="text-[11px] text-gray-600 mb-3">{s.desc}</p>
            <button
              onClick={() => { setArtifactId(s.id); onRunAnalysis(s.id); }}
              className="bg-[#0f4a66] hover:bg-[#165a78] text-white text-xs px-3 py-1.5 rounded transition font-medium flex items-center space-x-1"
            >
              <Play className="w-3 h-3 text-green-400" />
              <span>Run Scenario Analysis</span>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

function TestingView({ analysisData, activeMenu, onSelectNode }: any) {
  if (!analysisData) return <EmptyState message="Run analysis to inspect test suites" />;
  const nodes = analysisData.full_graph?.nodes || [];
  const tests = nodes.filter((n: any) => n.type === 'Test' || n.type === 'TestCase');

  return (
    <div className="flex-1 overflow-auto p-6 bg-white">
      <h2 className="text-base font-bold text-gray-800 mb-4">{activeMenu} ({tests.length})</h2>
      <div className="border border-gray-200 rounded overflow-hidden shadow-sm">
        <table className="w-full text-left text-xs border-collapse">
          <thead className="bg-gray-50 border-b border-gray-200 text-gray-600 font-semibold">
            <tr>
              <th className="px-4 py-2.5">Test Case ID</th>
              <th className="px-4 py-2.5">Subsystem</th>
              <th className="px-4 py-2.5">ECU Target</th>
              <th className="px-4 py-2.5">ASIL Classification</th>
              <th className="px-4 py-2.5">Source Suite</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {tests.slice(0, 50).map((t: any) => (
              <tr key={t.id} className="hover:bg-blue-50 transition cursor-pointer" onClick={() => onSelectNode({ id: t.id, data: t })}>
                <td className="px-4 py-2.5 font-mono text-cyan-700 font-semibold">{t.id}</td>
                <td className="px-4 py-2.5 text-gray-600">{t.subsystem || 'ADAS'}</td>
                <td className="px-4 py-2.5 text-gray-600">{t.ecu || 'ECU_1'}</td>
                <td className="px-4 py-2.5">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    t.safety_level?.includes('D') ? 'bg-red-100 text-red-700' :
                    t.safety_level?.includes('C') ? 'bg-amber-100 text-amber-700' : 'bg-gray-100 text-gray-700'
                  }`}>{normalizeAsil(t.safety_level)}</span>
                </td>
                <td className="px-4 py-2.5 text-gray-500 font-mono text-[11px] truncate max-w-xs">{t.source_file || 'tests/adas_test_suite.json'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function SafetyView({ analysisData, activeMenu }: any) {
  if (!analysisData) return <EmptyState message="Run analysis to inspect safety compliance" />;
  const report = analysisData.report || {};

  return (
    <div className="flex-1 overflow-auto p-6 bg-white">
      <h2 className="text-base font-bold text-gray-800 mb-4">{activeMenu}</h2>
      <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
        <div className="flex items-center space-x-2 text-green-800 font-bold text-sm mb-1">
          <Shield className="w-5 h-5 text-green-600" />
          <span>ISO 26262 Non-Bypassable Safety Gate: ACTIVE</span>
        </div>
        <p className="text-xs text-green-700">
          All ASIL-C and ASIL-D safety-critical test cases are retained unconditionally in accordance with the mathematical invariant assertion <code>T_safe ⊆ T_final</code>.
        </p>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="border border-gray-200 rounded p-4 text-center bg-gray-50">
          <div className="text-2xl font-bold text-red-600">{report.safety_tests_count || 0}</div>
          <div className="text-xs text-gray-500 mt-1">ASIL-C/D Tests Retained</div>
        </div>
        <div className="border border-gray-200 rounded p-4 text-center bg-gray-50">
          <div className="text-2xl font-bold text-teal-700">{report.test_reduction_pct?.toFixed(1) || 0}%</div>
          <div className="text-xs text-gray-500 mt-1">Test Suite Reduction</div>
        </div>
        <div className="border border-gray-200 rounded p-4 text-center bg-gray-50">
          <div className="text-2xl font-bold text-gray-800">FAIL_CLOSED</div>
          <div className="text-xs text-gray-500 mt-1">Safety Gate Enforcement Policy</div>
        </div>
      </div>
    </div>
  );
}

function EvidenceView({ analysisData, artifactId, activeMenu }: any) {
  if (!analysisData) return <EmptyState message="Run analysis to inspect audit evidence" />;

  return (
    <div className="flex-1 overflow-auto p-6 bg-white">
      <h2 className="text-base font-bold text-gray-800 mb-4">{activeMenu} — {artifactId}</h2>
      <div className="bg-slate-900 text-slate-100 p-4 rounded-lg font-mono text-xs overflow-x-auto max-h-[500px]">
        <pre>{JSON.stringify(analysisData, null, 2)}</pre>
      </div>
    </div>
  );
}

function TraceabilityMatrixView({ analysisData }: { analysisData: any }) {
  if (!analysisData) return <EmptyState message="Run analysis to view traceability matrix" />;
  const nodes = analysisData.full_graph?.nodes || [];
  const links = analysisData.full_graph?.links || [];
  const nodeIds = nodes.map((n: any) => n.id);
  const linkSet = new Set(links.map((l: any) => `${l.source}::${l.target}`));
  return (
    <div className="flex-1 overflow-auto p-4 bg-white">
      <h2 className="text-sm font-semibold text-gray-700 mb-3">Traceability Matrix — {nodeIds.length} artifacts</h2>
      <div className="overflow-auto border border-gray-200 rounded">
        <table className="text-[10px] border-collapse">
          <thead>
            <tr>
              <th className="bg-gray-100 border border-gray-200 px-2 py-1 text-left font-semibold text-gray-600 sticky left-0 z-10">Artifact</th>
              {nodeIds.map((id: string) => (
                <th key={id} className="bg-gray-100 border border-gray-200 px-1 py-1 font-medium text-gray-600 max-w-[60px] truncate" style={{ writingMode: 'vertical-rl', transform: 'rotate(180deg)', height: 80 }}>{id}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {nodeIds.map((rowId: string) => (
              <tr key={rowId} className="hover:bg-blue-50">
                <td className="border border-gray-200 px-2 py-1 font-mono font-medium text-gray-700 sticky left-0 bg-white z-10 max-w-[120px] truncate">{rowId}</td>
                {nodeIds.map((colId: string) => (
                  <td key={colId} className="border border-gray-200 text-center px-1 py-1">
                    {rowId === colId ? <span className="text-gray-300">—</span>
                      : linkSet.has(`${rowId}::${colId}`) ? <span className="text-green-600 font-bold">✓</span> : ''}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ExecutiveSummaryView({ analysisData, artifactId }: any) {
  if (!analysisData) return <EmptyState message="Run analysis to view executive summary" />;
  const report = analysisData.report || {};
  const impacted = report.structural_impacts_count || (report.impact_items || []).length || 0;
  const tests = report.tests_selected_count || (report.test_items || []).length || 0;

  return (
    <div className="flex-1 overflow-auto p-6 bg-white space-y-6">
      <div className="border border-gray-200 rounded-lg p-5 bg-gradient-to-r from-slate-50 to-teal-50/30">
        <h2 className="text-lg font-bold text-gray-900 mb-1">AURA-Impact Analysis Report: {report.changed_artifact_id || artifactId}</h2>
        <p className="text-xs text-gray-600">Automotive Traceability & Safety-Gated Impact Assessment</p>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="border border-gray-200 rounded-lg p-4 bg-white text-center shadow-sm">
          <div className="text-2xl font-bold text-red-600">{impacted}</div>
          <div className="text-xs text-gray-500 mt-1">Structural Impacts</div>
        </div>
        <div className="border border-gray-200 rounded-lg p-4 bg-white text-center shadow-sm">
          <div className="text-2xl font-bold text-purple-600">{report.semantic_recoveries_count || 0}</div>
          <div className="text-xs text-gray-500 mt-1">Semantic Recoveries</div>
        </div>
        <div className="border border-gray-200 rounded-lg p-4 bg-white text-center shadow-sm">
          <div className="text-2xl font-bold text-blue-600">{tests}</div>
          <div className="text-xs text-gray-500 mt-1">Selected Tests</div>
        </div>
        <div className="border border-gray-200 rounded-lg p-4 bg-white text-center shadow-sm">
          <div className="text-2xl font-bold text-teal-700">{report.test_reduction_pct?.toFixed(1) || 0}%</div>
          <div className="text-xs text-gray-500 mt-1">Suite Reduction</div>
        </div>
      </div>
    </div>
  );
}
