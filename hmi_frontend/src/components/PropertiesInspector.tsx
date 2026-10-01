import {
  Settings, Copy, ExternalLink, Link2, GitMerge, CheckCircle2, X
} from "lucide-react";

interface PropertiesInspectorProps {
  selectedNode: any;
  onClose: () => void;
  onOpenInGraph: (nodeId: string) => void;
}

function AsilBadge({ level }: { level: string }) {
  const colors: Record<string, string> = {
    'ASIL-D': 'bg-red-600 text-white border-red-700',
    'ASIL-C': 'bg-orange-500 text-white border-orange-600',
    'ASIL-B': 'bg-yellow-500 text-white border-yellow-600',
    'ASIL-A': 'bg-yellow-300 text-gray-800 border-yellow-400',
    'QM': 'bg-gray-100 text-gray-600 border-gray-300',
  };
  const cls = colors[level] || 'bg-gray-100 text-gray-600 border-gray-300';
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-bold border ${cls}`}>{level || 'QM'}</span>
  );
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="grid grid-cols-5 gap-2 py-1.5 border-b border-gray-100 last:border-0 items-start">
      <span className="col-span-2 text-xs text-gray-400 pt-0.5">{label}</span>
      <span className="col-span-3 text-xs text-gray-800">{children}</span>
    </div>
  );
}

function Section({ title }: { title: string }) {
  return (
    <div className="px-4 py-1.5 bg-gray-100 border-y border-gray-200">
      <span className="text-[10px] font-bold uppercase tracking-widest text-gray-500">{title}</span>
    </div>
  );
}

export default function PropertiesInspector({ selectedNode, onClose, onOpenInGraph }: PropertiesInspectorProps) {
  if (!selectedNode) return null;

  const { id, data } = selectedNode;
  const safetyLevel = data?.safety_level || 'ASIL-C';
  const artType = data?.type || 'Artifact';
  const subsystem = data?.subsystem || 'ADAS';
  const isSemantic = data?.isImpacted && !data?.isSeed;

  const handleCopyId = () => {
    navigator.clipboard.writeText(id).catch(() => {});
  };

  return (
    <div className="h-full flex flex-col bg-white text-sm overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-[#0f4a66] text-white shrink-0">
        <span className="text-sm font-semibold">Artifact Properties</span>
        <div className="flex items-center space-x-2">
          <button className="p-1 hover:bg-white/10 rounded transition"><Settings className="w-3.5 h-3.5 text-gray-300" /></button>
          <button onClick={onClose} className="p-1 hover:bg-white/10 rounded transition"><X className="w-3.5 h-3.5 text-gray-300" /></button>
        </div>
      </div>

      {/* Artifact icon + name */}
      <div className="flex items-start space-x-3 px-4 py-3 border-b border-gray-200 shrink-0">
        <div className="w-9 h-9 border border-gray-300 rounded flex items-center justify-center bg-gray-50 shrink-0 text-gray-500 font-mono text-xs font-bold">
          {'{  }'}
        </div>
        <div className="min-w-0">
          <div className="font-semibold text-gray-900 text-sm truncate" title={id}>{id}</div>
          <div className="text-xs text-gray-500 mt-0.5">{artType}</div>
        </div>
      </div>

      {/* Scrollable content */}
      <div className="flex-1 overflow-y-auto">
        <Section title="Identification" />
        <div className="px-4 py-1">
          <Row label="ID"><span className="font-mono text-blue-600 text-[11px] break-all">{id}</span></Row>
          <Row label="Type">{artType}</Row>
          <Row label="Title">{data?.name || id}</Row>
        </div>

        <Section title="Classification" />
        <div className="px-4 py-1">
          <Row label="ASIL"><AsilBadge level={safetyLevel} /></Row>
          <Row label="Subsystem">{subsystem}</Row>
        </div>

        <Section title="Impact" />
        <div className="px-4 py-1">
          <Row label="Detection Stage">
            <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold ${isSemantic ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'}`}>
              {isSemantic ? 'Semantic' : 'Structural'}
            </span>
          </Row>
          <Row label="Confidence / Similarity">{isSemantic ? '0.6128' : '1.0000'}</Row>
          <Row label="Decision">
            <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-green-100 text-green-700 border border-green-200">ACCEPTED</span>
          </Row>
          <Row label="Selection Source">{isSemantic ? 'Semantic Fallback' : 'Graph Traversal'}</Row>
        </div>

        <Section title="Traceability" />
        <div className="px-4 py-1">
          <Row label="Relates to">
            <span className="text-blue-600 flex items-center space-x-1 cursor-pointer hover:underline">
              <Link2 className="w-3 h-3 shrink-0" />
              <span>REQ_AEB_001</span>
            </span>
          </Row>
          <Row label="Implemented by">
            <span className="text-blue-600 flex items-center space-x-1 cursor-pointer hover:underline">
              <GitMerge className="w-3 h-3 shrink-0" />
              <span>SWC_AEB</span>
            </span>
          </Row>
          <Row label="Verified by">
            <span className="text-blue-600 flex items-center space-x-1 cursor-pointer hover:underline">
              <CheckCircle2 className="w-3 h-3 shrink-0" />
              <span>TC_AEB_014</span>
            </span>
          </Row>
        </div>

        <Section title="Safety" />
        <div className="px-4 py-1">
          <Row label="Safety Gate Status">
            <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-green-100 text-green-700 border border-green-200">RETAINED</span>
          </Row>
          <Row label="Mandatory Test">Yes</Row>
        </div>

        <Section title="Rationale" />
        <div className="px-4 py-2">
          <p className="text-xs text-gray-600 bg-gray-50 p-2 rounded border border-gray-200 leading-relaxed">
            {isSemantic
              ? 'Semantic similarity (0.61) above threshold with verified context. Selected due to semantic match and safety rule.'
              : 'Direct structural impact from changed artifact. All downstream nodes are marked for mandatory review.'}
          </p>
        </div>

        <Section title="Analysis" />
        <div className="px-4 py-1 pb-4">
          <Row label="Analysis ID"><span className="font-mono">7f3e2c9a</span></Row>
          <Row label="Timestamp">Oct 1, 2025 18:44</Row>
        </div>
      </div>

      {/* Action buttons */}
      <div className="px-4 py-3 border-t border-gray-200 space-y-2 shrink-0">
        <div className="flex space-x-2">
          <button
            onClick={() => onOpenInGraph(id)}
            className="flex-1 flex items-center justify-center space-x-1.5 bg-[#0f4a66] hover:bg-[#165a78] text-white py-1.5 rounded transition text-xs font-medium shadow-sm"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            <span>Open in graph</span>
          </button>
          <button onClick={handleCopyId} className="flex-1 flex items-center justify-center space-x-1.5 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 py-1.5 rounded transition text-xs font-medium">
            <Copy className="w-3.5 h-3.5" />
            <span>Copy ID</span>
          </button>
        </div>
        <button
          onClick={onClose}
          className="w-full text-center text-xs text-blue-600 hover:underline py-0.5"
        >
          Close
        </button>
      </div>
    </div>
  );
}
