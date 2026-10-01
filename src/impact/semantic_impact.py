"""
Semantic-Based Impact Analyzer (v2.0)
Leverages context-aware semantic retrieval with artifact-type and graph proximity context.
"""
from typing import Dict, List, Any, Optional
from src.semantic.retrieval import SemanticRetriever
from src.impact.change_detector import ChangeContext


class SemanticImpactAnalyzer:
    def __init__(self, retriever: SemanticRetriever):
        self.retriever = retriever

    def analyze_impact(
        self,
        change: ChangeContext,
        threshold: Optional[float] = None,
        top_k: Optional[int] = None,
        variant: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        query_text = change.after_content if change.after_content else change.change_semantics
        if not query_text:
            query_text = change.diff_text

        candidates = self.retriever.retrieve_candidates_for_change(
            change_text=query_text,
            source_artifact_id=change.target_node_id,
            source_artifact_type=change.artifact_type,
            source_subsystem=change.project,
            threshold=threshold,
            top_k=top_k,
            variant=variant,
            project=change.project,
            exclude_node_ids=[change.target_node_id] if change.target_node_id else None
        )

        impacted: Dict[str, Dict[str, Any]] = {}
        for c in candidates:
            impacted[c["id"]] = {
                "semantic_score": c["semantic_score"],
                "context_score": c.get("context_score", 0.0),
                "final_score": c.get("final_score", c["semantic_score"]),
                "node_type": c["node_type"],
                "name": c["name"],
                "graph_distance": c.get("graph_distance", -1),
                "reason": c["reason"],
                "evidence": c["evidence"]
            }

        return impacted
