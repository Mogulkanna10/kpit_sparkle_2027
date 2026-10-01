"""
Baseline 3: Deterministic Graph Baseline (v2.0)
"""
import time
from typing import Dict, Any, List, Set, Optional
from src.graph.traversal import GraphTraverser
from src.testing.selector import RegressionSelector
from src.impact.change_detector import ChangeContext


class GraphBaseline:
    def __init__(self, traverser: GraphTraverser, selector: RegressionSelector, max_depth: int = 5):
        self.traverser = traverser
        self.selector = selector
        self.max_depth = max_depth

    def run(
        self,
        change: ChangeContext,
        max_depth: Optional[int] = None,
        ground_truth_safety_tests: Optional[Set[str] | List[str]] = None,
        enforce_safety_gate: bool = True
    ) -> Dict[str, Any]:
        start_t = time.perf_counter()
        depth = max_depth if max_depth is not None else self.max_depth

        start_nodes = []
        if change.target_node_id:
            start_nodes.append(change.target_node_id)
        if not start_nodes and "changed_node_ids" in change.metadata:
            start_nodes.extend(change.metadata["changed_node_ids"])

        graph_impacts = self.traverser.propagate_downstream(
            start_node_ids=start_nodes,
            max_depth=depth
        )

        impacted_nodes = list(graph_impacts.keys())
        selected_tests = self.selector.select_tests(
            impacted_artifact_ids=impacted_nodes,
            ground_truth_safety_tests=ground_truth_safety_tests,
            enforce_safety_gate=enforce_safety_gate
        )

        latency_ms = (time.perf_counter() - start_t) * 1000.0

        return {
            "method": "Graph_Only",
            "impacted_artifacts": impacted_nodes,
            "selected_tests": selected_tests,
            "graph_impact_details": graph_impacts,
            "latency_ms": round(latency_ms, 3)
        }
