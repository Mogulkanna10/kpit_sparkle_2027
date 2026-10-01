"""
Engineering Graph Provenance & Traceability Chains
Renders step-by-step structural paths with node types, edge relations, and source files.
"""
from typing import List, Dict, Any, Optional
from src.graph.traversal import TraversalImpact
from src.graph.builder import EngineeringGraph


class ProvenanceTracker:
    """Formats provenance chains for human explainability and automated evidence logging."""

    @staticmethod
    def format_trace_chain(impact: TraversalImpact, graph: Optional[EngineeringGraph] = None) -> str:
        if not impact.path:
            return impact.artifact_id

        steps = []
        for i, node_id in enumerate(impact.path):
            node_type = "Artifact"
            source_file = ""
            if graph and graph.has_node(node_id):
                n = graph.get_node(node_id)
                node_type = n.type.value if hasattr(n.type, "value") else str(n.type)
                source_file = f" ({n.source_file})" if n.source_file else ""

            step_str = f"[{node_type}] {node_id}{source_file}"
            steps.append(step_str)

            if i < len(impact.edge_relations):
                rel = impact.edge_relations[i]
                steps.append(f"  ──[{rel}]──►")

        return "\n".join(steps)

    @staticmethod
    def to_mermaid(impact: TraversalImpact) -> str:
        lines = ["graph LR"]
        for i in range(len(impact.path) - 1):
            src = impact.path[i]
            dst = impact.path[i + 1]
            rel = impact.edge_relations[i] if i < len(impact.edge_relations) else "DEPENDS_ON"
            lines.append(f"    {src} -->|{rel}| {dst}")
        return "\n".join(lines)
