"""
AURA-Impact Hybrid Engine (v2.0)
Integrates Graph Propagation, Contextual Semantic Retrieval, Fusion, and Mandatory Safety Gate.
"""
import time
from typing import Dict, Any, List, Set, Optional
from src.impact.change_classifier import ChangeClassifier, ChangeCategory
from src.impact.graph_impact import GraphImpactAnalyzer
from src.impact.semantic_impact import SemanticImpactAnalyzer
from src.impact.fusion import ImpactFusionEngine
from src.impact.ranking import ImpactRanker
from src.testing.selector import RegressionSelector
from src.impact.change_detector import ChangeContext


class AuraImpactHybrid:
    def __init__(
        self,
        classifier: ChangeClassifier,
        graph_analyzer: GraphImpactAnalyzer,
        semantic_analyzer: SemanticImpactAnalyzer,
        fusion_engine: ImpactFusionEngine,
        ranker: ImpactRanker,
        selector: RegressionSelector,
        use_routing: bool = True,
        use_contextual_semantic: bool = True
    ):
        self.classifier = classifier
        self.graph_analyzer = graph_analyzer
        self.semantic_analyzer = semantic_analyzer
        self.fusion_engine = fusion_engine
        self.ranker = ranker
        self.selector = selector
        self.use_routing = use_routing
        self.use_contextual_semantic = use_contextual_semantic

    def run(
        self,
        change: ChangeContext,
        semantic_threshold: Optional[float] = None,
        max_graph_depth: Optional[int] = None,
        min_impact_score: float = 0.20,
        ground_truth_safety_tests: Optional[Set[str] | List[str]] = None,
        enforce_safety_gate: bool = True
    ) -> Dict[str, Any]:
        start_t = time.perf_counter()

        # 1. Classify change
        category = self.classifier.classify(change) if self.use_routing else ChangeCategory.MIXED

        # 2. Graph impact
        graph_impacts = {}
        if category != ChangeCategory.NO_IMPACT:
            graph_impacts = self.graph_analyzer.analyze_impact(change, max_depth=max_graph_depth)

        # 3. Semantic impact (with optional context filtering)
        semantic_impacts = {}
        if category in [ChangeCategory.SEMANTIC, ChangeCategory.MIXED, ChangeCategory.UNKNOWN]:
            semantic_impacts = self.semantic_analyzer.analyze_impact(
                change,
                threshold=semantic_threshold,
                variant="VARIANT_C" if self.use_contextual_semantic else "VARIANT_A"
            )

        # 4. Impact Fusion
        fused = self.fusion_engine.fuse(
            graph_impacts=graph_impacts,
            semantic_impacts=semantic_impacts,
            category=category
        )

        # 5. Ranking & Explanations
        ranked = self.ranker.rank(fused, min_score_threshold=min_impact_score)
        impacted_nodes = [item["artifact_id"] for item in ranked]

        # 6. Canonical Test Selection through RegressionSelector & Mandatory Safety Gate
        selected_tests = self.selector.select_tests(
            impacted_artifact_ids=impacted_nodes,
            ground_truth_safety_tests=ground_truth_safety_tests,
            enforce_safety_gate=enforce_safety_gate
        )

        latency_ms = (time.perf_counter() - start_t) * 1000.0
        method_name = "Hybrid_AURA_Routed" if self.use_routing else "Hybrid_AURA_Fixed"

        return {
            "method": method_name,
            "change_category": category.value,
            "impacted_artifacts": impacted_nodes,
            "ranked_details": ranked,
            "selected_tests": selected_tests,
            "latency_ms": round(latency_ms, 3)
        }
