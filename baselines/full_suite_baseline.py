"""
Baseline 0: Full Test Suite Baseline (Upper Reference for Recall, Lower for Reduction)
"""
from typing import Set, Dict, Any, List
from src.graph.builder import EngineeringGraph
from src.graph.schema import NodeType
from src.impact.change_detector import ChangeContext


class FullSuiteBaseline:
    def __init__(self, eng_graph: EngineeringGraph):
        self.eng_graph = eng_graph
        self.all_nodes = list(eng_graph.node_store.keys())
        self.all_tests = {t.id for t in eng_graph.get_nodes_by_type(NodeType.TEST)}

    def run(self, change: ChangeContext) -> Dict[str, Any]:
        return {
            "method": "Full_Suite",
            "impacted_artifacts": self.all_nodes,
            "selected_tests": self.all_tests,
            "latency_ms": 0.1
        }
