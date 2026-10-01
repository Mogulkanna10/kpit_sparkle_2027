"""
tests/unit/test_ranking_classifier.py
Unit tests for ImpactRanker and ChangeClassifier (completing Gate 21 test coverage).
"""
import pytest
from src.impact.ranking import ImpactRanker
from src.impact.change_classifier import ChangeClassifier, ChangeCategory
from src.impact.change_detector import ChangeContext
from src.graph.builder import EngineeringGraph
from src.graph.schema import GraphNode, NodeType, SafetyLevel


def _make_ctx(artifact_type: str, metadata: dict) -> ChangeContext:
    return ChangeContext(
        change_id="chg_01",
        project="ADAS",
        source_artifact="file.c",
        target_node_id="node_01",
        artifact_type=artifact_type,
        before_content="",
        after_content="",
        diff_text="",
        change_semantics="",
        metadata=metadata
    )


def test_impact_ranker_basic():
    ranker = ImpactRanker()
    candidates = {
        "node_a": {"impact_score": 0.85, "confidence": 0.9, "node_type": "C_FUNCTION", "structural_score": 0.85},
        "node_b": {"impact_score": 0.40, "confidence": 0.7, "node_type": "REQUIREMENT", "semantic_score": 0.40},
        "node_c": {"impact_score": 0.10, "confidence": 0.5, "node_type": "ARXML_PORT"},
    }
    ranked = ranker.rank(candidates, min_score_threshold=0.20)
    assert len(ranked) == 2
    assert ranked[0]["artifact_id"] == "node_a"
    assert ranked[0]["rank"] == 1
    assert ranked[1]["artifact_id"] == "node_b"
    assert ranked[1]["rank"] == 2


def test_impact_ranker_with_graph_and_top_k():
    g = EngineeringGraph()
    g.add_node(GraphNode(id="safe_node", type=NodeType.C_FUNCTION, safety_level=SafetyLevel.ASIL_D))
    g.add_node(GraphNode(id="qm_node", type=NodeType.C_FUNCTION, safety_level=SafetyLevel.QM))

    ranker = ImpactRanker(eng_graph=g)
    candidates = {
        "safe_node": {"impact_score": 0.75, "node_type": "C_FUNCTION"},
        "qm_node": {"impact_score": 0.75, "node_type": "C_FUNCTION"},
        "extra_node": {"impact_score": 0.90, "node_type": "C_FUNCTION"},
    }
    ranked = ranker.rank(candidates, min_score_threshold=0.1, top_k=2)
    assert len(ranked) == 2
    assert ranked[0]["artifact_id"] == "extra_node"


def test_change_classifier_benchmark_classes():
    classifier = ChangeClassifier()

    c1 = _make_ctx("C_CODE", {"benchmark_class": "EXPLICIT_STRUCTURAL"})
    assert classifier.classify(c1) == ChangeCategory.STRUCTURAL

    c2 = _make_ctx("DOC", {"benchmark_class": "HIDDEN_SEMANTIC"})
    assert classifier.classify(c2) == ChangeCategory.SEMANTIC

    c3 = _make_ctx("C_CODE", {"benchmark_class": "SEMANTIC_DECOY"})
    assert classifier.classify(c3) == ChangeCategory.NO_IMPACT

    c4 = _make_ctx("C_CODE", {"benchmark_class": "AMBIGUOUS"})
    assert classifier.classify(c4) == ChangeCategory.UNKNOWN


def test_change_classifier_mutation_codes():
    classifier = ChangeClassifier()

    c_no_impact = _make_ctx("C_CODE", {"change_type": "M15"})
    assert classifier.classify(c_no_impact) == ChangeCategory.NO_IMPACT

    c_semantic = _make_ctx("REQ", {"change_type": "M03"})
    assert classifier.classify(c_semantic) == ChangeCategory.SEMANTIC

    c_structural = _make_ctx("C_CODE", {"change_type": "M07"})
    assert classifier.classify(c_structural) == ChangeCategory.STRUCTURAL

    c_mixed = _make_ctx("C_CODE", {"change_type": "M01"})
    assert classifier.classify(c_mixed) == ChangeCategory.MIXED


def test_change_classifier_fallback_types():
    classifier = ChangeClassifier()

    c_c = _make_ctx("C_FUNCTION", {})
    assert classifier.classify(c_c) == ChangeCategory.STRUCTURAL

    c_req = _make_ctx("REQUIREMENT", {})
    assert classifier.classify(c_req) == ChangeCategory.SEMANTIC

    c_unk = _make_ctx("OTHER_UNRECOGNIZED", {})
    assert classifier.classify(c_unk) == ChangeCategory.UNKNOWN
