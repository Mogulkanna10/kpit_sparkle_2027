import { useState, useCallback } from "react";
import CommandBar from "./components/CommandBar";
import ProjectExplorer from "./components/ProjectExplorer";
import Workspace from "./components/Workspace";
import PropertiesInspector from "./components/PropertiesInspector";
import StatusBar from "./components/StatusBar";
import { runAnalysis } from "./api";
import { Shield, CheckCircle2, XCircle } from "lucide-react";

function App() {
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [activeMenu, setActiveMenu] = useState("Impact Tree");
  const [artifactId, setArtifactId] = useState("REQ_AEB_014");
  const [highlightNodeId, setHighlightNodeId] = useState<string | null>(null);
  const [forceTab, setForceTab] = useState<string | null>(null);

  const handleRunAnalysis = async (aid?: string) => {
    const id = aid || artifactId;
    setIsLoading(true);
    try {
      const result = await runAnalysis({
        artifact_id: id,
        artifact_type: "requirement",
        subsystem: "ADAS",
        ecu: "VCU",
        change_type: "MODIFICATION",
        after_content: "void override_safety_limits() { max_temp = 90; }",
        change_semantics: "Increased maximum temperature limit to 90 degrees.",
        force_semantic: false,
        filter_subsystem: true,
      });
      setAnalysisData(result);
      setSelectedNode(null);
      setForceTab("Impact Graph");
    } catch (error) {
      console.error("Analysis failed:", error);
      alert("Analysis failed. Make sure the backend is running on port 8000.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectNode = (node: any) => {
    setSelectedNode(node);
  };

  const handleOpenInGraph = useCallback((nodeId: string) => {
    setHighlightNodeId(nodeId);
    setForceTab("Impact Graph");
    setSelectedNode(null);
    setTimeout(() => setHighlightNodeId(null), 3000);
  }, []);

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-gray-100 font-sans">
      <CommandBar analysisData={analysisData} isLoading={isLoading} />

      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <div className="w-52 shrink-0 flex flex-col bg-[#0f4a66] overflow-hidden">
          <ProjectExplorer activeMenu={activeMenu} onMenuSelect={setActiveMenu} />
        </div>

        {/* Main workspace */}
        <div className="flex-1 flex overflow-hidden min-w-0">
          <Workspace
            activeMenu={activeMenu}
            analysisData={analysisData}
            onSelectNode={handleSelectNode}
            onRunAnalysis={handleRunAnalysis}
            isLoading={isLoading}
            artifactId={artifactId}
            setArtifactId={setArtifactId}
            highlightNodeId={highlightNodeId}
            forceTab={forceTab}
            onForceTabConsumed={() => setForceTab(null)}
          />
        </div>

        {/* Right panel — ALWAYS visible */}
        <div className="w-72 shrink-0 flex flex-col bg-white border-l border-gray-200 overflow-hidden">
          {selectedNode ? (
            <PropertiesInspector
              selectedNode={selectedNode}
              onClose={() => setSelectedNode(null)}
              onOpenInGraph={handleOpenInGraph}
            />
          ) : (
            <SummaryPanel analysisData={analysisData} isLoading={isLoading} onRunAnalysis={handleRunAnalysis} artifactId={artifactId} />
          )}
        </div>
      </div>

      <StatusBar analysisData={analysisData} />
    </div>
  );
}

/** Always-visible right panel — shows summary when nothing is selected */
function SummaryPanel({ analysisData, isLoading, onRunAnalysis, artifactId }: { analysisData: any; isLoading: boolean; onRunAnalysis: (id?: string) => void; artifactId: string }) {
  const report = analysisData?.report || {};
  const decisions = report.decisions || [];
  const accepted = decisions.filter((d: any) => d.decision && !d.decision.includes('REJECT'));

  if (!analysisData) {
    return (
      <div className="flex flex-col h-full">
        <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
          <p className="text-xs font-semibold text-gray-600 uppercase tracking-wider">Analysis Summary</p>
        </div>
        <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
          <Shield className="w-10 h-10 text-gray-200 mb-3" />
          <p className="text-sm font-medium text-gray-500 mb-1">No Analysis Run</p>
          <p className="text-xs text-gray-400 mb-4">Enter an artifact ID and run analysis to see results here</p>
          <button
            onClick={() => onRunAnalysis(artifactId)}
            disabled={isLoading}
            className="bg-[#0f4a66] text-white text-xs px-4 py-2 rounded hover:bg-[#165a78] transition disabled:opacity-50"
          >
            {isLoading ? 'Running...' : 'Run Analysis'}
          </button>
        </div>
        <div className="px-4 pb-4 text-xs text-gray-300 text-center">
          Click a node in the graph to inspect its properties
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full overflow-y-auto">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200 bg-gray-50 shrink-0">
        <p className="text-xs font-semibold text-gray-600 uppercase tracking-wider">Analysis Summary</p>
        <p className="text-xs text-gray-400 mt-0.5 font-mono truncate">{report.changed_artifact_id || artifactId}</p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-2 p-3 border-b border-gray-100">
        {[
          { label: 'Structural', value: report.structural_impacts_count ?? 0, color: 'text-red-600', bg: 'bg-red-50' },
          { label: 'Semantic', value: report.semantic_recoveries_count ?? 0, color: 'text-purple-600', bg: 'bg-purple-50' },
          { label: 'Tests', value: report.tests_selected_count ?? 0, color: 'text-blue-600', bg: 'bg-blue-50' },
          { label: 'Rejected', value: report.rejected_candidates_count ?? 0, color: 'text-gray-500', bg: 'bg-gray-50' },
        ].map((s) => (
          <div key={s.label} className={`${s.bg} rounded-lg px-3 py-2 text-center`}>
            <div className={`text-xl font-bold ${s.color}`}>{s.value}</div>
            <div className="text-[10px] text-gray-500 mt-0.5">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Safety Gate */}
      <div className="px-3 py-2 border-b border-gray-100">
        <div className="flex items-center space-x-2 p-2 bg-green-50 border border-green-200 rounded">
          <Shield className="w-3.5 h-3.5 text-green-600 shrink-0" />
          <div>
            <div className="text-xs font-semibold text-green-700">Safety Gate: RETAINED</div>
            <div className="text-[10px] text-green-600">{report.safety_tests_count ?? 0} safety tests • ISO 26262</div>
          </div>
        </div>
      </div>

      {/* Graph stats */}
      <div className="px-3 py-2 border-b border-gray-100">
        <div className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider mb-1.5">Graph</div>
        <div className="space-y-1 text-xs text-gray-600">
          <div className="flex justify-between"><span className="text-gray-400">Nodes</span><span className="font-medium">{analysisData.full_graph?.nodes?.length ?? 0}</span></div>
          <div className="flex justify-between"><span className="text-gray-400">Edges</span><span className="font-medium">{analysisData.full_graph?.links?.length ?? 0}</span></div>
          <div className="flex justify-between"><span className="text-gray-400">Test reduction</span><span className="font-medium">{report.test_reduction_pct?.toFixed(1) ?? 0}%</span></div>
          <div className="flex justify-between"><span className="text-gray-400">Analysis ID</span><span className="font-mono text-[10px] truncate max-w-[120px]">{report.analysis_id?.slice(0,12) ?? '—'}</span></div>
        </div>
      </div>

      {/* Decisions list */}
      <div className="px-3 py-2 flex-1 overflow-y-auto">
        <div className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider mb-2 flex items-center justify-between">
          <span>Decisions ({decisions.length})</span>
          <span className="normal-case font-normal text-gray-400">{accepted.length} accepted</span>
        </div>
        <div className="space-y-1">
          {decisions.slice(0, 20).map((d: any, i: number) => {
            const isAccepted = d.decision && !d.decision.includes('REJECT');
            return (
              <div key={i} className={`flex items-start space-x-2 rounded px-2 py-1.5 ${isAccepted ? 'bg-green-50' : 'bg-gray-50'}`}>
                {isAccepted
                  ? <CheckCircle2 className="w-3 h-3 text-green-500 shrink-0 mt-0.5" />
                  : <XCircle className="w-3 h-3 text-gray-300 shrink-0 mt-0.5" />
                }
                <div className="min-w-0">
                  <div className="text-[10px] font-mono truncate text-gray-700">{d.artifact_id}</div>
                  <div className="text-[10px] text-gray-400">{d.confidence?.toFixed(3)} • {d.stage}</div>
                </div>
              </div>
            );
          })}
          {decisions.length > 20 && (
            <div className="text-[10px] text-center text-gray-400 py-1">+{decisions.length - 20} more in Analysis Decisions table</div>
          )}
        </div>
      </div>

      {/* Footer hint */}
      <div className="px-3 py-2 border-t border-gray-100 shrink-0">
        <p className="text-[10px] text-gray-400 text-center">Click any graph node to inspect properties</p>
      </div>
    </div>
  );
}

export default App;
