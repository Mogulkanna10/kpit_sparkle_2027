"""
Benchmark Metrics Computer (v2.0)
Strict separation of Artifact Impact Metrics vs. Regression Test Metrics.
Mathematical handling of zero-impact edge cases.
"""
from typing import Set, List, Dict, Any, Optional
import numpy as np


class MetricsComputer:
    @staticmethod
    def compute_artifact_metrics(
        predicted_artifacts: List[str] | Set[str],
        true_artifacts: List[str] | Set[str]
    ) -> Dict[str, Any]:
        pred_set = set(predicted_artifacts)
        true_set = set(true_artifacts)

        hit_set = pred_set.intersection(true_set)
        hit_count = len(hit_set)
        pred_count = len(pred_set)
        true_count = len(true_set)

        # No-Impact Case handling (true_count == 0)
        if true_count == 0:
            if pred_count == 0:
                recall = 1.0
                precision = 1.0
                f1 = 1.0
                specificity = 1.0
            else:
                recall = 1.0
                precision = 0.0
                f1 = 0.0
                specificity = 0.0
        else:
            recall = hit_count / true_count
            precision = (hit_count / pred_count) if pred_count > 0 else 0.0
            f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
            specificity = 1.0 if pred_count == hit_count else max(0.0, 1.0 - (pred_count - hit_count)/10.0)

        false_positives = list(pred_set - true_set)
        false_negatives = list(true_set - pred_set)

        return {
            "predicted_count": pred_count,
            "true_count": true_count,
            "hit_count": hit_count,
            "recall": round(recall, 4),
            "precision": round(precision, 4),
            "f1": round(f1, 4),
            "specificity": round(specificity, 4),
            "false_positive_count": len(false_positives),
            "false_negative_count": len(false_negatives),
            "false_positives": false_positives,
            "false_negatives": false_negatives
        }

    @staticmethod
    def compute_test_metrics(
        selected_tests: List[str] | Set[str],
        true_tests: List[str] | Set[str],
        safety_critical_tests: List[str] | Set[str],
        total_suite_size: int
    ) -> Dict[str, Any]:
        sel_set = set(selected_tests)
        true_set = set(true_tests)
        sc_set = set(safety_critical_tests)

        hit_set = sel_set.intersection(true_set)
        hit_count = len(hit_set)
        sel_count = len(sel_set)
        true_count = len(true_set)

        if true_count == 0:
            if sel_count == 0:
                recall = 1.0
                precision = 1.0
                f1 = 1.0
                specificity = 1.0
            else:
                recall = 1.0
                precision = 0.0
                f1 = 0.0
                specificity = 0.0
        else:
            recall = hit_count / true_count
            precision = (hit_count / sel_count) if sel_count > 0 else 0.0
            f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
            specificity = (total_suite_size - sel_count) / max(1, total_suite_size - true_count)

        test_reduction = 1.0 - (sel_count / total_suite_size) if total_suite_size > 0 else 0.0

        # Safety recall
        if len(sc_set) > 0:
            sc_hits = len(sel_set.intersection(sc_set))
            safety_recall = sc_hits / len(sc_set)
        else:
            safety_recall = 1.0

        false_negatives = list(true_set - sel_set)
        false_positives = list(sel_set - true_set)

        return {
            "total_suite_size": total_suite_size,
            "selected_count": sel_count,
            "true_count": true_count,
            "hit_count": hit_count,
            "recall": round(recall, 4),
            "precision": round(precision, 4),
            "f1": round(f1, 4),
            "specificity": round(specificity, 4),
            "test_reduction": round(test_reduction, 4),
            "safety_critical_recall": round(safety_recall, 4),
            "false_negatives": false_negatives,
            "false_positives": false_positives
        }
