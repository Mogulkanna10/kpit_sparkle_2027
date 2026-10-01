"""
Two-Stage Impact Engine (Locked Architecture B)
Coordinates Stage 1 deterministic graph analysis and Stage 2 context-constrained semantic recovery.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set, Tuple
import time

from src.graph.builder import EngineeringGraph
from src.graph.traversal import BoundedGraphTraverser, TraversalImpact
from src.semantic.retriever import RetrievedCandidate
from src.impact.semantic_fallback import SemanticFallback
from src.impact.impact_union import Impact, ImpactUnion, ImpactType, SourceStage
from src.ingestion.git_diff import ChangedArtifact


@dataclass
class ImpactEngineResult:
    changed_artifact_id: str
    structural_impacts: List[Impact]
    semantic_impacts: List[Impact]
    all_semantic_candidates: List[RetrievedCandidate]
    final_impacts: List[Impact]
    review_required_items: List[RetrievedCandidate]
    structural_coverage_complete: bool
    stage1_latency_ms: float
    stage2_latency_ms: float
    total_latency_ms: float


class TwoStageImpactEngine:
    """Executes Stage 1 Bounded Graph Traversal + Stage 2 Contextual Semantic Fallback."""

    def __init__(self,
                 graph: EngineeringGraph,
                 semantic_fallback: Optional[SemanticFallback] = None,
                 max_graph_depth: int = 3,
                 default_threshold: float = 0.75):
        self.graph = graph
        self.traverser = BoundedGraphTraverser(graph, max_depth=max_graph_depth)
        self.semantic_fallback = semantic_fallback
        self.default_threshold = default_threshold

    def analyze_change(self,
                       change: ChangedArtifact,
                       threshold_override: Optional[float] = None,
                       force_semantic: bool = False) -> ImpactEngineResult:
        start_time = time.perf_counter()

        # =====================================================================
        # STAGE 1: Bounded Deterministic Graph Traversal
        # =====================================================================
        s1_start = time.perf_counter()
        raw_traversal = self.traverser.get_explicit_impacts([change.artifact_id])
        s1_latency = (time.perf_counter() - s1_start) * 1000.0

        structural_impacts: List[Impact] = []
        for t in raw_traversal:
            structural_impacts.append(Impact(
                artifact_id=t.artifact_id,
                artifact_type=t.artifact_type,
                subsystem=t.subsystem,
                ecu="ECU_1",
                impact_type=ImpactType.STRUCTURAL,
                confidence=t.confidence,
                source_stage=SourceStage.GRAPH,
                evidence={
                    "decision": "DETERMINISTIC_GRAPH_TRAVERSAL",
                    "depth": t.depth,
                    "path": t.path,
                    "relations": t.edge_relations,
                    "confidence": t.confidence,
                    "reason": f"Explicit graph path of depth {t.depth} with confidence {t.confidence:.2f}"
                },
                source_file=t.source_file,
                source_location=t.source_location
            ))

        # Check structural completeness: if change artifact exists in graph and has outgoing trace links
        structural_complete = len(structural_impacts) > 0 and self.graph.has_node(change.artifact_id)

        # =====================================================================
        # STAGE 2: Context-Constrained Semantic Recovery (Fallback / Supplement)
        # =====================================================================
        semantic_impacts: List[Impact] = []
        all_candidates: List[RetrievedCandidate] = []
        review_required: List[RetrievedCandidate] = []
        s2_latency = 0.0

        # Invoke Stage 2 if zero structural impacts OR incomplete coverage OR force_semantic requested
        should_run_semantic = (
            force_semantic
            or change.metadata.get("force_semantic", False)
            or not structural_complete
            or len(structural_impacts) == 0
        )

        if self.semantic_fallback is not None and should_run_semantic:
            s2_start = time.perf_counter()
            query_ctx = {
                "artifact_id": change.artifact_id,
                "subsystem": change.subsystem,
                "artifact_type": change.artifact_type,
                "ecu": change.ecu,
                "metadata": change.metadata,
                "filter_subsystem_in_index": change.metadata.get("filter_subsystem_in_index", True)
            }
            query_text = change.change_semantics or change.after_content or change.artifact_id

            recovered, candidates = self.semantic_fallback.recover(
                query_text=query_text,
                query_context=query_ctx,
                threshold_override=threshold_override or self.default_threshold
            )
            semantic_impacts = recovered
            all_candidates = candidates
            review_required = [c for c in candidates if c.status == "REVIEW_REQUIRED"]
            s2_latency = (time.perf_counter() - s2_start) * 1000.0

        # =====================================================================
        # IMPACT SET UNION (S_final = S_struct UNION S_semantic)
        # =====================================================================
        final_impacts = ImpactUnion.compute_union(structural_impacts, semantic_impacts)
        total_latency = (time.perf_counter() - start_time) * 1000.0

        return ImpactEngineResult(
            changed_artifact_id=change.artifact_id,
            structural_impacts=structural_impacts,
            semantic_impacts=semantic_impacts,
            all_semantic_candidates=all_candidates,
            final_impacts=final_impacts,
            review_required_items=review_required,
            structural_coverage_complete=structural_complete,
            stage1_latency_ms=s1_latency,
            stage2_latency_ms=s2_latency,
            total_latency_ms=total_latency
        )
