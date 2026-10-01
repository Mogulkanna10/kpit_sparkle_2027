"""
Baseline 2: Embedding-Only Baseline (v2.0)
Supports Variant 2A (Raw Embedding), 2B (+ Type), 2C (+ Graph Proximity), 2D (+ Full Context).
"""
import time
from typing import Dict, Any, List, Set, Optional
from src.semantic.retrieval import SemanticRetriever
from src.testing.selector import RegressionSelector
from src.impact.change_detector import ChangeContext


class EmbeddingBaseline:
    def __init__(
        self,
        retriever: SemanticRetriever,
        selector: RegressionSelector,
        threshold: float = 0.65,
        variant: str = "VARIANT_A"
    ):
        self.retriever = retriever
        self.selector = selector
        self.threshold = threshold
        self.variant = variant

    def run(
        self,
        change: ChangeContext,
        threshold: Optional[float] = None,
        variant: Optional[str] = None,
        ground_truth_safety_tests: Optional[Set[str] | List[str]] = None,
        enforce_safety_gate: bool = True
    ) -> Dict[str, Any]:
        start_t = time.perf_counter()
        th = threshold if threshold is not None else self.threshold
        var = variant if variant is not None else self.variant

        candidates = self.retriever.retrieve_candidates_for_change(
            change_text=change.after_content if change.after_content else change.change_semantics,
            source_artifact_id=change.target_node_id,
            source_artifact_type=change.artifact_type,
            source_subsystem=change.project,
            threshold=th,
            variant=var,
            project=change.project
        )

        impacted_nodes = [c["id"] for c in candidates]
        if change.target_node_id and change.target_node_id not in impacted_nodes:
            impacted_nodes.append(change.target_node_id)

        selected_tests = self.selector.select_tests(
            impacted_artifact_ids=impacted_nodes,
            ground_truth_safety_tests=ground_truth_safety_tests,
            enforce_safety_gate=enforce_safety_gate
        )

        latency_ms = (time.perf_counter() - start_t) * 1000.0

        return {
            "method": f"Embedding_{var}",
            "impacted_artifacts": impacted_nodes,
            "selected_tests": selected_tests,
            "candidates_details": candidates,
            "threshold_used": th,
            "latency_ms": round(latency_ms, 3)
        }
