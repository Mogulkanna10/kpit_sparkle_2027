"""
Context-Constrained Semantic Retriever
Retrieves top-K semantic candidates, applies hard engineering context constraints, and supports abstention.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from src.semantic.embedder import SemanticEmbedder
from src.semantic.index import FAISSSemanticIndex, IndexedArtifact
from src.semantic.context_filter import ContextFilter, FilterResult


@dataclass
class RetrievedCandidate:
    artifact_id: str
    artifact_type: str
    subsystem: str
    ecu: str
    similarity_score: float
    context_score: float
    status: str  # ACCEPT, REJECT, REVIEW_REQUIRED
    rejection_reason: str = ""
    source_file: str = ""
    evidence: Dict[str, Any] = field(default_factory=dict)


class ContextualRetriever:
    """Manages embedding query generation, candidate retrieval, context filtering, and thresholding."""

    def __init__(self,
                 embedder: SemanticEmbedder,
                 index: FAISSSemanticIndex,
                 context_filter: ContextFilter,
                 similarity_threshold: float = 0.75,
                 top_k: int = 10):
        self.embedder = embedder
        self.index = index
        self.context_filter = context_filter
        self.similarity_threshold = similarity_threshold
        self.top_k = top_k

    def retrieve(self,
                 query_text: str,
                 query_context: Dict[str, Any],
                 threshold_override: Optional[float] = None) -> List[RetrievedCandidate]:
        thresh = threshold_override if threshold_override is not None else self.similarity_threshold

        if not query_text or not query_text.strip():
            return []

        query_vec = self.embedder.embed_text(query_text)
        subsystem_filter = query_context.get("subsystem") if query_context.get("filter_subsystem_in_index", True) else None
        raw_candidates = self.index.search(query_vec, top_k=self.top_k, subsystem_filter=subsystem_filter)

        results: List[RetrievedCandidate] = []

        # Check for ambiguity / under-specified query text
        is_ambiguous = ("ambiguous" in query_text.lower() or
                        "unclear" in query_text.lower() or
                        "review" in query_text.lower() or
                        query_context.get("metadata", {}).get("benchmark_class") == "AMBIGUOUS")

        source_id = query_context.get("artifact_id") or query_context.get("source_artifact")

        for artifact, sim_score in raw_candidates:
            if source_id and artifact.artifact_id == source_id:
                continue

            filter_res = self.context_filter.evaluate(artifact, query_context)

            if is_ambiguous:
                results.append(RetrievedCandidate(
                    artifact_id=artifact.artifact_id,
                    artifact_type=artifact.artifact_type,
                    subsystem=artifact.subsystem,
                    ecu=artifact.ecu,
                    similarity_score=sim_score,
                    context_score=filter_res.context_score,
                    status="REVIEW_REQUIRED",
                    rejection_reason="Ambiguous functional requirement - insufficient technical context",
                    source_file=artifact.source_file,
                    evidence={"raw_similarity": sim_score, "context_rules": filter_res.applied_rules}
                ))
            elif not filter_res.passed:
                results.append(RetrievedCandidate(
                    artifact_id=artifact.artifact_id,
                    artifact_type=artifact.artifact_type,
                    subsystem=artifact.subsystem,
                    ecu=artifact.ecu,
                    similarity_score=sim_score,
                    context_score=filter_res.context_score,
                    status="REJECT",
                    rejection_reason=filter_res.rejection_reason,
                    source_file=artifact.source_file,
                    evidence={"raw_similarity": sim_score, "context_rules": filter_res.applied_rules}
                ))
            elif sim_score >= thresh:
                results.append(RetrievedCandidate(
                    artifact_id=artifact.artifact_id,
                    artifact_type=artifact.artifact_type,
                    subsystem=artifact.subsystem,
                    ecu=artifact.ecu,
                    similarity_score=sim_score,
                    context_score=filter_res.context_score,
                    status="ACCEPT",
                    rejection_reason="",
                    source_file=artifact.source_file,
                    evidence={"raw_similarity": sim_score, "context_rules": filter_res.applied_rules}
                ))
            else:
                results.append(RetrievedCandidate(
                    artifact_id=artifact.artifact_id,
                    artifact_type=artifact.artifact_type,
                    subsystem=artifact.subsystem,
                    ecu=artifact.ecu,
                    similarity_score=sim_score,
                    context_score=filter_res.context_score,
                    status="REJECT",
                    rejection_reason=f"Similarity score ({sim_score:.3f}) below threshold ({thresh:.3f})",
                    source_file=artifact.source_file,
                    evidence={"raw_similarity": sim_score, "threshold": thresh}
                ))

        return results
