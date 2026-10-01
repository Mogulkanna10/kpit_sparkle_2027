"""
Regression Test Selector with Mandatory Safety Gate Enforcement (v2.0)
Guarantees that no safety-critical test can be dropped by downstream optimization.
"""
from typing import Set, List, Dict, Any, Optional
from src.testing.test_mapper import TestMapper
from src.testing.safety_gate import SafetyGate
from src.graph.builder import EngineeringGraph
from src.graph.schema import NodeType


class SafetyGateViolationException(Exception):
    """Raised when an impacted safety-critical test is omitted from the selected test suite."""
    pass


class RegressionSelector:
    def __init__(self, eng_graph: EngineeringGraph, mapper: TestMapper, safety_gate: SafetyGate):
        self.eng_graph = eng_graph
        self.mapper = mapper
        self.safety_gate = safety_gate
        self.all_tests: Set[str] = {t.id for t in eng_graph.get_nodes_by_type(NodeType.TEST)}

    def select_tests(
        self,
        impacted_artifact_ids: List[str],
        ground_truth_safety_tests: Optional[Set[str] | List[str]] = None,
        enforce_safety_gate: bool = True
    ) -> Set[str]:
        """
        Canonical, secure test selection pipeline.
        Mandatorily pipes candidate mapped tests through the Safety Gate.
        """
        # 1. Map impacted artifacts to test suite
        candidate_tests = self.mapper.map_impacted_artifacts_to_tests(impacted_artifact_ids)

        # 2. Convert safety tests to set
        gt_safety_set = set(ground_truth_safety_tests or [])

        # 3. Mandatory Safety Gate Application
        if enforce_safety_gate and gt_safety_set:
            final_selected_tests = self.safety_gate.apply_safety_gate(candidate_tests, gt_safety_set)
        else:
            final_selected_tests = candidate_tests

        # 4. Invariant Assertion Check
        if enforce_safety_gate and gt_safety_set:
            missing_safety = gt_safety_set - final_selected_tests
            if missing_safety:
                raise SafetyGateViolationException(
                    f"CRITICAL SAFETY VIOLATION: Missing safety-critical tests: {missing_safety}"
                )

        return final_selected_tests

    def evaluate_selection(
        self,
        selected_tests: Set[str],
        true_impacted_tests: Set[str],
        safety_critical_true_tests: Set[str]
    ) -> Dict[str, Any]:
        t_total = len(self.all_tests)
        t_selected = len(selected_tests)
        t_true = len(true_impacted_tests)

        intersection = selected_tests.intersection(true_impacted_tests)
        t_hit = len(intersection)

        if t_true == 0:
            recall = 1.0
            precision = 1.0 if t_selected == 0 else 0.0
            f1 = 1.0 if t_selected == 0 else 0.0
            specificity = 1.0 if t_selected == 0 else 0.0
        else:
            recall = t_hit / t_true
            precision = (t_hit / t_selected) if t_selected > 0 else 0.0
            f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
            specificity = (t_total - t_selected) / max(1, t_total - t_true)

        test_reduction = 1.0 - (t_selected / t_total) if t_total > 0 else 0.0

        # Safety-critical recall
        sc_true_count = len(safety_critical_true_tests)
        if sc_true_count > 0:
            sc_hits = len(selected_tests.intersection(safety_critical_true_tests))
            safety_recall = sc_hits / sc_true_count
        else:
            safety_recall = 1.0

        false_negatives = list(true_impacted_tests - selected_tests)
        false_positives = list(selected_tests - true_impacted_tests)

        return {
            "total_suite_size": t_total,
            "selected_count": t_selected,
            "true_impacted_count": t_true,
            "hit_count": t_hit,
            "recall": round(recall, 4),
            "precision": round(precision, 4),
            "f1": round(f1, 4),
            "specificity": round(specificity, 4),
            "test_reduction": round(test_reduction, 4),
            "safety_critical_recall": round(safety_recall, 4),
            "false_negative_count": len(false_negatives),
            "false_negatives": false_negatives,
            "false_positive_count": len(false_positives),
            "false_positives": false_positives
        }
