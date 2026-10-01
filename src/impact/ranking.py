"""
Impact Candidate Ranking and Explanation Engine
"""
from typing import List, Dict, Any, Optional
from src.graph.builder import EngineeringGraph
from src.graph.schema import SafetyLevel


class ImpactRanker:
    def __init__(self, eng_graph: Optional[EngineeringGraph] = None):
        self.eng_graph = eng_graph

    def rank(
        self,
        impact_candidates: Dict[str, Dict[str, Any]],
        min_score_threshold: float = 0.15,
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        ranked_list = []

        for node_id, data in impact_candidates.items():
            score = data.get("impact_score", 0.0)
            if score < min_score_threshold:
                continue

            safety = SafetyLevel.QM
            if self.eng_graph and self.eng_graph.has_node(node_id):
                node = self.eng_graph.get_node(node_id)
                safety = node.safety_level if node else SafetyLevel.QM

            ranked_list.append({
                "artifact_id": node_id,
                "node_type": data.get("node_type", "Unknown"),
                "impact_score": round(score, 4),
                "confidence": round(data.get("confidence", 1.0), 2),
                "safety_level": safety.value if hasattr(safety, 'value') else str(safety),
                "graph_distance": data.get("graph_distance", -1),
                "structural_score": round(data.get("structural_score", 0.0), 4),
                "semantic_score": round(data.get("semantic_score", 0.0), 4),
                "selection_reason": data.get("selection_reason", ""),
                "graph_evidence": data.get("graph_evidence", []),
                "semantic_evidence": data.get("semantic_evidence", {})
            })

        # Rank primarily by impact_score descending, secondarily by safety level priority
        def sort_key(item):
            safety_priority = 2 if "SAFETY" in item["safety_level"] or "ASIL" in item["safety_level"] else 1
            return (item["impact_score"], safety_priority)

        ranked_list.sort(key=sort_key, reverse=True)

        for rank_idx, item in enumerate(ranked_list, start=1):
            item["rank"] = rank_idx

        if top_k is not None:
            ranked_list = ranked_list[:top_k]

        return ranked_list
