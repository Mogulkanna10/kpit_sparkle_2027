"""
Graph-Based Impact Analyzer
"""
from typing import Dict, List, Any, Optional
from src.graph.traversal import GraphTraverser
from src.impact.change_detector import ChangeContext


class GraphImpactAnalyzer:
    def __init__(self, traverser: GraphTraverser):
        self.traverser = traverser

    def analyze_impact(
        self,
        change: ChangeContext,
        max_depth: Optional[int] = None,
        decay: Optional[float] = None
    ) -> Dict[str, Dict[str, Any]]:
        start_nodes = []
        if change.target_node_id:
            start_nodes.append(change.target_node_id)
        
        # If target_node_id not provided directly, check metadata
        if not start_nodes and "changed_node_ids" in change.metadata:
            start_nodes.extend(change.metadata["changed_node_ids"])

        if not start_nodes:
            return {}

        return self.traverser.propagate_downstream(
            start_node_ids=start_nodes,
            max_depth=max_depth,
            decay=decay
        )
