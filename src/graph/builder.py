"""
NetworkX Engineering Graph Builder
Assembles multi-layer AUTOSAR traceability graphs from parsed requirements, ARXML, C/C++, and tests.
"""
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
import networkx as nx

from src.graph.schema import GraphNode, GraphEdge, NodeType, RelationType, SafetyLevel


class EngineeringGraph:
    """Directed multi-layer engineering traceability graph."""

    def __init__(self, project_id: str = "DEFAULT", name: Optional[str] = None):
        self.project_id = name or project_id
        self.name = self.project_id
        self.graph = nx.DiGraph()
        self.node_store: Dict[str, GraphNode] = {}
        self.edge_store: List[GraphEdge] = []

    @property
    def nodes(self):
        return self.node_store

    @property
    def edges(self):
        return self.edge_store

    def add_node(self, node: GraphNode):
        self.node_store[node.id] = node
        self.graph.add_node(
            node.id,
            type=node.type.value if hasattr(node.type, "value") else str(node.type),
            name=node.name,
            subsystem=node.subsystem,
            ecu=node.ecu,
            source_file=node.source_file,
            source_location=node.source_location,
            safety_level=node.safety_level.value if hasattr(node.safety_level, "value") else str(node.safety_level),
            metadata=node.metadata
        )

    def add_edge(self, edge: GraphEdge):
        self.edge_store.append(edge)
        self.graph.add_edge(
            edge.source,
            edge.target,
            relation=edge.relation.value if hasattr(edge.relation, "value") else str(edge.relation),
            provenance=edge.provenance,
            confidence=edge.confidence,
            metadata=edge.metadata
        )

    def has_node(self, node_id: str) -> bool:
        return node_id in self.node_store

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        return self.node_store.get(node_id)

    def get_nodes_by_type(self, node_type: NodeType) -> List[GraphNode]:
        t_val = node_type.value if hasattr(node_type, "value") else str(node_type)
        return [n for n in self.node_store.values() if (n.type.value if hasattr(n.type, "value") else str(n.type)) == t_val]

    def get_neighbors(self, node_id: str, direction: str = "out") -> List[str]:
        if node_id not in self.graph:
            return []
        if direction == "out":
            return list(self.graph.successors(node_id))
        elif direction == "in":
            return list(self.graph.predecessors(node_id))
        else:
            return list(set(self.graph.successors(node_id)).union(set(self.graph.predecessors(node_id))))
