"""
Bounded Directed Graph Traversal
Implements typed, depth-bounded forward impact analysis stopping at architectural boundaries.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Set, Optional, Tuple
from collections import deque
import networkx as nx

from src.graph.builder import EngineeringGraph
from src.graph.schema import NodeType, RelationType


@dataclass
class TraversalImpact:
    artifact_id: str
    artifact_type: str
    subsystem: str
    depth: int
    path: List[str]
    edge_relations: List[str]
    confidence: float
    source_file: str = ""
    source_location: str = ""


class BoundedGraphTraverser:
    """Performs deterministic bounded BFS traversal from changed nodes."""

    def __init__(self, graph: EngineeringGraph, max_depth: int = 3):
        self.graph = graph
        self.max_depth = max_depth

    def get_explicit_impacts(self, changed_nodes: List[str], max_depth: Optional[int] = None) -> List[TraversalImpact]:
        depth_limit = max_depth if max_depth is not None else self.max_depth
        impacts: List[TraversalImpact] = []
        visited: Set[str] = set()

        # Queue contains: (current_node_id, current_depth, path_nodes, path_relations, cum_confidence)
        queue = deque()
        for start_id in changed_nodes:
            if self.graph.has_node(start_id):
                queue.append((start_id, 0, [start_id], [], 1.0))
                visited.add(start_id)

        while queue:
            curr_id, curr_depth, path, rels, conf = queue.popleft()

            # Record non-root visited nodes as impacts
            if curr_depth > 0:
                node_obj = self.graph.get_node(curr_id)
                if node_obj:
                    impacts.append(TraversalImpact(
                        artifact_id=curr_id,
                        artifact_type=node_obj.type.value if hasattr(node_obj.type, "value") else str(node_obj.type),
                        subsystem=node_obj.subsystem,
                        depth=curr_depth,
                        path=list(path),
                        edge_relations=list(rels),
                        confidence=conf,
                        source_file=node_obj.source_file,
                        source_location=node_obj.source_location
                    ))

            if curr_depth >= depth_limit:
                continue

            # Follow outgoing edges in NetworkX graph
            if curr_id in self.graph.graph:
                for nbr in self.graph.graph.successors(curr_id):
                    edge_data = self.graph.graph.get_edge_data(curr_id, nbr) or {}
                    rel = edge_data.get("relation", "DEPENDS_ON")
                    edge_conf = edge_data.get("confidence", 1.0)

                    if nbr not in visited:
                        visited.add(nbr)
                        queue.append((
                            nbr,
                            curr_depth + 1,
                            path + [nbr],
                            rels + [rel],
                            conf * edge_conf
                        ))

        return impacts

    def propagate_downstream(self,
                             changed_nodes: Any = None,
                             start_node_ids: Any = None,
                             max_depth: Optional[int] = None,
                             decay: Optional[float] = None,
                             **kwargs) -> Dict[str, Any]:
        targets = changed_nodes or start_node_ids or []
        if isinstance(targets, str):
            targets = [targets]
        impacts = self.get_explicit_impacts(targets, max_depth=max_depth)
        res: Dict[str, Any] = {}
        decay_val = decay if decay is not None else 0.85
        for c in targets:
            res[c] = {"distance": 0, "confidence": 1.0, "structural_score": 1.0, "path": [c]}
        for imp in impacts:
            score = imp.confidence * (decay_val ** imp.depth)
            res[imp.artifact_id] = {
                "distance": imp.depth,
                "confidence": imp.confidence,
                "structural_score": score,
                "path": imp.path
            }
        return res


# Backward-compatible alias
GraphTraverser = BoundedGraphTraverser
