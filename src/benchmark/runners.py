"""
Benchmark Runner and Experiment Orchestration Engine (v2.0)
Executes Baselines and Contextual AURA-Impact across calibration, validation, and test splits.
Strictly enforces Safety Gate invariant and clean metric separation.
"""
import os
import sys
import json
import time
import random
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.graph.builder import EngineeringGraph
from src.graph.traversal import GraphTraverser
from src.parsers.requirement_parser import RequirementParser
from src.parsers.arxml_parser import ARXMLParser
from src.parsers.cpp_parser import CppParser
from src.parsers.test_parser import TestParser

from src.semantic.embedder import ArtifactEmbedder
from src.semantic.index import SemanticIndex
from src.semantic.context_filter import EngineeringContextFilter
from src.semantic.retrieval import SemanticRetriever

from src.impact.change_detector import ChangeDetector, ChangeContext
from src.impact.change_classifier import ChangeClassifier, ChangeCategory
from src.impact.graph_impact import GraphImpactAnalyzer
from src.impact.semantic_impact import SemanticImpactAnalyzer
from src.impact.fusion import ImpactFusionEngine
from src.impact.ranking import ImpactRanker

from src.testing.test_mapper import TestMapper
from src.testing.safety_gate import SafetyGate
from src.testing.selector import RegressionSelector, SafetyGateViolationException

from src.benchmark.mutation_generator import MutationRecord
from src.benchmark.ground_truth import GroundTruthRecord
from src.benchmark.metrics import MetricsComputer

from baselines.full_suite_baseline import FullSuiteBaseline
from baselines.keyword_baseline import KeywordBaseline
from baselines.embedding_baseline import EmbeddingBaseline
from baselines.graph_baseline import GraphBaseline
from baselines.hybrid_baseline import AuraImpactHybrid


class BenchmarkRunner:
    def __init__(self, seed: int = 42, device: str = "cpu"):
        self.seed = seed
        self.rng = random.Random(seed)
        self.device = device
        self.embedder = ArtifactEmbedder(device=device)
        self.detector = ChangeDetector()
        self.classifier = ChangeClassifier()
        self.projects_cache: Dict[str, Dict[str, Any]] = {}

    def setup_project(self, project_name: str, project_dir: Path) -> Dict[str, Any]:
        """
        Initializes graph, vector index, context filter, and baselines for a project.
        """
        if project_name in self.projects_cache:
            return self.projects_cache[project_name]

        from scripts.build_graph import build_project_graph
        eng_graph = build_project_graph(project_name, project_dir)

        # Build Semantic Index & Context Filter
        sem_index = SemanticIndex(self.embedder)
        sem_index.build_index(list(eng_graph.node_store.values()))

        context_filter = EngineeringContextFilter(eng_graph=eng_graph)
        retriever = SemanticRetriever(sem_index, context_filter=context_filter)

        traverser = GraphTraverser(eng_graph, max_depth=5)
        mapper = TestMapper(eng_graph)
        safety_gate = SafetyGate(eng_graph)
        selector = RegressionSelector(eng_graph, mapper, safety_gate)

        # Analyzers & Baselines
        graph_analyzer = GraphImpactAnalyzer(traverser)
        semantic_analyzer = SemanticImpactAnalyzer(retriever)
        fusion_engine = ImpactFusionEngine()
        ranker = ImpactRanker(eng_graph)

        full_suite = FullSuiteBaseline(eng_graph)
        keyword_base = KeywordBaseline(eng_graph, selector)
        embedding_raw = EmbeddingBaseline(retriever, selector, variant="VARIANT_A")
        embedding_context = EmbeddingBaseline(retriever, selector, variant="VARIANT_C")
        graph_base = GraphBaseline(traverser, selector, max_depth=5)
        
        aura_hybrid_routed = AuraImpactHybrid(
            self.classifier, graph_analyzer, semantic_analyzer, fusion_engine, ranker, selector,
            use_routing=True, use_contextual_semantic=True
        )
        aura_hybrid_fixed = AuraImpactHybrid(
            self.classifier, graph_analyzer, semantic_analyzer, fusion_engine, ranker, selector,
            use_routing=False, use_contextual_semantic=True
        )

        cache_entry = {
            "graph": eng_graph,
            "traverser": traverser,
            "sem_index": sem_index,
            "context_filter": context_filter,
            "retriever": retriever,
            "mapper": mapper,
            "safety_gate": safety_gate,
            "selector": selector,
            "graph_analyzer": graph_analyzer,
            "semantic_analyzer": semantic_analyzer,
            "fusion_engine": fusion_engine,
            "ranker": ranker,
            "full_suite": full_suite,
            "keyword": keyword_base,
            "embedding_raw": embedding_raw,
            "embedding_context": embedding_context,
            "graph_only": graph_base,
            "hybrid_routed": aura_hybrid_routed,
            "hybrid_fixed": aura_hybrid_fixed
        }
        self.projects_cache[project_name] = cache_entry
        return cache_entry

    def calibrate_threshold(
        self,
        calibration_mutations: List[MutationRecord],
        calibration_ground_truth: Dict[str, GroundTruthRecord],
        grid: Optional[List[float]] = None
    ) -> float:
        """
        Calibrates the optimal semantic similarity threshold on the calibration split only.
        """
        grid_values = grid or [0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]
        best_th = 0.65
        best_f1 = -1.0

        for th in grid_values:
            f1_scores = []
            for mut in calibration_mutations:
                p_ctx = self.projects_cache.get(mut.project_id)
                if not p_ctx:
                    continue
                change_ctx = self.detector.parse_mutation_record(mut.to_dict())
                gt = calibration_ground_truth.get(mut.mutation_id)
                if not gt:
                    continue
                res = p_ctx["embedding_context"].run(
                    change_ctx,
                    threshold=th,
                    ground_truth_safety_tests=gt.safety_critical_tests,
                    enforce_safety_gate=True
                )
                metrics = MetricsComputer.compute_artifact_metrics(res["impacted_artifacts"], gt.true_impacted_artifacts)
                f1_scores.append(metrics["f1"])

            mean_f1 = np.mean(f1_scores) if f1_scores else 0.0
            if mean_f1 > best_f1:
                best_f1 = mean_f1
                best_th = th

        print(f"[Calibration] Optimal contextual semantic threshold: {best_th:.2f} (Mean F1: {best_f1:.4f})")
        return best_th

    def run_benchmark(
        self,
        all_mutations: List[MutationRecord],
        ground_truth_map: Dict[str, GroundTruthRecord],
        semantic_threshold: float = 0.65,
        enforce_safety_gate: bool = True
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        impact_rows = []
        reg_rows = []

        for mut in all_mutations:
            pid = mut.project_id
            p_ctx = self.projects_cache.get(pid)
            if not p_ctx:
                continue

            change_ctx = self.detector.parse_mutation_record(mut.to_dict())
            gt = ground_truth_map.get(mut.mutation_id)
            if not gt:
                continue

            true_arts = gt.true_impacted_artifacts
            true_tests = set(gt.true_impacted_tests)
            sc_tests = set(gt.safety_critical_tests)
            total_tests = len(p_ctx["graph"].get_nodes_by_type("Test"))

            # Methods to evaluate
            methods = [
                ("Full_Suite", lambda c: p_ctx["full_suite"].run(c)),
                ("Keyword", lambda c: p_ctx["keyword"].run(c, ground_truth_safety_tests=sc_tests, enforce_safety_gate=enforce_safety_gate)),
                ("Embedding_Only", lambda c: p_ctx["embedding_raw"].run(c, threshold=semantic_threshold, ground_truth_safety_tests=sc_tests, enforce_safety_gate=enforce_safety_gate)),
                ("Embedding_Context", lambda c: p_ctx["embedding_context"].run(c, threshold=semantic_threshold, ground_truth_safety_tests=sc_tests, enforce_safety_gate=enforce_safety_gate)),
                ("Graph_Only", lambda c: p_ctx["graph_only"].run(c, ground_truth_safety_tests=sc_tests, enforce_safety_gate=enforce_safety_gate)),
                ("Hybrid_AURA_Routed", lambda c: p_ctx["hybrid_routed"].run(c, semantic_threshold=semantic_threshold, ground_truth_safety_tests=sc_tests, enforce_safety_gate=enforce_safety_gate)),
                ("Hybrid_AURA_Fixed", lambda c: p_ctx["hybrid_fixed"].run(c, semantic_threshold=semantic_threshold, ground_truth_safety_tests=sc_tests, enforce_safety_gate=enforce_safety_gate)),
            ]

            for m_name, fn in methods:
                try:
                    res = fn(change_ctx)
                except Exception as e:
                    print(f"Error evaluating {m_name} on {mut.mutation_id}: {e}")
                    continue

                pred_arts = res.get("impacted_artifacts", [])
                sel_tests = set(res.get("selected_tests", []))
                latency = res.get("latency_ms", 0.0)

                # Hard Safety Invariant Assertion
                if enforce_safety_gate and sc_tests:
                    missing_safety = sc_tests - sel_tests
                    if missing_safety:
                        raise SafetyGateViolationException(
                            f"SAFETY GATE FAILED for {m_name} on {mut.mutation_id}: Missing {missing_safety}"
                        )

                # 1. Artifact Impact Metrics (skip for Full Suite)
                if m_name != "Full_Suite":
                    art_m = MetricsComputer.compute_artifact_metrics(pred_arts, true_arts)
                    impact_rows.append({
                        "project": pid,
                        "mutation_id": mut.mutation_id,
                        "change_type": mut.change_type,
                        "category_name": mut.category_name,
                        "artifact_type": mut.artifact_type,
                        "method": m_name,
                        "predicted_count": art_m["predicted_count"],
                        "true_count": art_m["true_count"],
                        "hit_count": art_m["hit_count"],
                        "recall": art_m["recall"],
                        "precision": art_m["precision"],
                        "f1": art_m["f1"],
                        "specificity": art_m["specificity"],
                        "false_positives": art_m["false_positive_count"],
                        "false_negatives": art_m["false_negative_count"],
                        "latency_ms": latency
                    })

                # 2. Regression Test Metrics
                test_m = MetricsComputer.compute_test_metrics(
                    selected_tests=sel_tests,
                    true_tests=true_tests,
                    safety_critical_tests=sc_tests,
                    total_suite_size=total_tests
                )
                reg_rows.append({
                    "project": pid,
                    "mutation_id": mut.mutation_id,
                    "change_type": mut.change_type,
                    "category_name": mut.category_name,
                    "method": m_name,
                    "total_tests": total_tests,
                    "selected_tests": test_m["selected_count"],
                    "true_impacted_tests": test_m["true_count"],
                    "selected_impacted_tests": test_m["hit_count"],
                    "true_safety_tests": len(sc_tests),
                    "selected_safety_tests": len(sel_tests.intersection(sc_tests)),
                    "hit_count": test_m["hit_count"],
                    "recall": test_m["recall"],
                    "precision": test_m["precision"],
                    "f1": test_m["f1"],
                    "specificity": test_m["specificity"],
                    "test_reduction": test_m["test_reduction"],
                    "safety_recall": test_m["safety_critical_recall"],
                    "false_negatives": len(test_m["false_negatives"]),
                    "latency_ms": latency
                })

        impact_df = pd.DataFrame(impact_rows)
        reg_df = pd.DataFrame(reg_rows)
        return impact_df, reg_df
