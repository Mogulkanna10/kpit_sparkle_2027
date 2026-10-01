"""
Semantic Fallback Engine
Invokes context-constrained semantic retrieval when deterministic graph links are incomplete or missing.
"""
from typing import List, Dict, Any, Optional, Tuple
from src.semantic.retriever import ContextualRetriever, RetrievedCandidate
from src.impact.impact_union import Impact, ImpactType, SourceStage


class SemanticFallback:
    """Executes Stage 2 context-constrained semantic recovery."""

    def __init__(self, retriever: ContextualRetriever):
        self.retriever = retriever

    def recover(self,
                query_text: str,
                query_context: Dict[str, Any],
                threshold_override: Optional[float] = None) -> Tuple[List[Impact], List[RetrievedCandidate]]:
        candidates = self.retriever.retrieve(query_text, query_context, threshold_override=threshold_override)

        accepted_impacts: List[Impact] = []
        for c in candidates:
            if c.status == "ACCEPT":
                accepted_impacts.append(Impact(
                    artifact_id=c.artifact_id,
                    artifact_type=c.artifact_type,
                    subsystem=c.subsystem,
                    ecu=c.ecu,
                    impact_type=ImpactType.SEMANTIC,
                    confidence=c.similarity_score,
                    source_stage=SourceStage.SEMANTIC,
                    evidence={
                        "decision": "SEMANTIC_RECOVERY",
                        "semantic_similarity": c.similarity_score,
                        "context_score": c.context_score,
                        "applied_rules": c.evidence.get("context_rules", {}),
                        "reason": f"Semantic similarity ({c.similarity_score:.2f}) above threshold with verified context."
                    },
                    source_file=c.source_file
                ))

        return accepted_impacts, candidates
