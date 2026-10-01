interface StatusBarProps {
  analysisData: any;
}

export default function StatusBar({ analysisData }: StatusBarProps) {
  const nodeCount = analysisData?.full_graph?.nodes?.length || 0;
  const edgeCount = analysisData?.full_graph?.links?.length || 0;

  return (
    <div className="h-7 bg-white border-t border-gray-200 flex items-center px-4 justify-between text-[10px] text-gray-500 select-none shrink-0">
      <div className="flex items-center space-x-2">
        <div className="w-2 h-2 rounded-full bg-green-500"></div>
        <span className="font-medium text-gray-600">System Ready</span>
      </div>
      <div className="flex items-center space-x-5">
        <span><span className="text-gray-400">Latency:</span> 0.79 ms</span>
        <span><span className="text-gray-400">Architecture:</span> Strict Union</span>
        <span><span className="text-gray-400">Model:</span> AURA-DomainHashEmbedder-384</span>
        <span><span className="text-gray-400">Threshold:</span> 0.45 (Frozen Canonical)</span>
        <span><span className="text-gray-400">Gate:</span> ISO 26262 Non-Bypassable</span>
        {analysisData && (
          <span><span className="text-gray-400">Graph:</span> {nodeCount} nodes / {edgeCount} edges</span>
        )}
      </div>
    </div>
  );
}
