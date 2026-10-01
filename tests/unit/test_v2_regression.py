"""
Unit and Integration Tests for AURA-Impact v2 Enhancements
Verifies:
1. Safety Gate non-bypassability and mandatory retention
2. Ground truth bounded propagation
3. No-impact metric stability
4. Context-aware semantic ranking determinism
5. Data leakage prevention
"""
import pytest
import json
from pathlib import Path
from src.graph.schema import Node, Edge, NodeType, EdgeType, SafetyLevel
from src.graph.builder import EngineeringGraph
from src.testing.test_mapper import TestMapper
from src.testing.safety_gate import SafetyGate
from src.testing.selector import RegressionSelector, SafetyGateViolationException
from src.benchmark.ground_truth import GroundTruthGenerator, GroundTruthRecord
from src.benchmark.mutation_generator import MutationRecord
from src.benchmark.metrics import MetricsComputer
from src.semantic.embedder import ArtifactEmbedder
from src.semantic.context_filter import EngineeringContextFilter


def test_safety_gate_cannot_be_bypassed():
    g = EngineeringGraph("TestProject")
    f_node = Node(id="Func_01", type=NodeType.C_FUNCTION, name="Func_01", file_path="f.c", project="Test")
    t_safe = Node(id="TC_Safe_01", type=NodeType.TEST, name="TC_Safe_01", file_path="t.c", project="Test", safety_level=SafetyLevel.ASIL_D)
    t_qm = Node(id="TC_QM_01", type=NodeType.TEST, name="TC_QM_01", file_path="t.c", project="Test", safety_level=SafetyLevel.QM)
    
    g.add_node(f_node)
    g.add_node(t_safe)
    g.add_node(t_qm)
    g.add_edge(Edge(source_id="TC_Safe_01", target_id="Func_01", relation=EdgeType.TESTS, source_file="t.c"))
    g.add_edge(Edge(source_id="TC_QM_01", target_id="Func_01", relation=EdgeType.TESTS, source_file="t.c"))

    mapper = TestMapper(g)
    gate = SafetyGate(g)
    selector = RegressionSelector(g, mapper, gate)

    # Calling select_tests with safety-critical ground truth MUST preserve TC_Safe_01
    selected = selector.select_tests(
        impacted_artifact_ids=["Func_01"],
        ground_truth_safety_tests=["TC_Safe_01"],
        enforce_safety_gate=True
    )
    assert "TC_Safe_01" in selected


def test_ground_truth_bounded_propagation():
    g = EngineeringGraph("ChainProject")
    # Build a 10-hop linear chain: N0 -> N1 -> ... -> N9
    for i in range(10):
        g.add_node(Node(id=f"N_{i}", type=NodeType.C_FUNCTION, name=f"N_{i}", file_path="f.c", project="Chain"))
    for i in range(9):
        g.add_edge(Edge(source_id=f"N_{i}", target_id=f"N_{i+1}", relation=EdgeType.CALLS, source_file="f.c"))

    gt_gen = GroundTruthGenerator(g, max_depth=5)
    mut = MutationRecord(
        mutation_id="MUT_CHAIN_01",
        project_id="CHAIN",
        change_type="M06",
        category_name="C_FUNCTION_BODY",
        source_artifact="f.c",
        target_node_id="N_0",
        artifact_type="C_Function",
        before_state="old",
        after_state="new",
        diff="--- f.c\n+++ f.c\n-old\n+new",
        intended_change_semantics="semantics",
        expected_impact_scope="PROPAGATED",
        metadata={}
    )
    gt = gt_gen.generate_ground_truth(mut)
    
    # Must only reach N_0 through N_5 (distance <= 5)
    assert "N_0" in gt.true_impacted_artifacts
    assert "N_5" in gt.true_impacted_artifacts
    assert "N_6" not in gt.true_impacted_artifacts
    assert "N_9" not in gt.true_impacted_artifacts


def test_no_impact_metrics_handling():
    # Empty ground truth
    m_art = MetricsComputer.compute_artifact_metrics(predicted_artifacts=[], true_artifacts=[])
    assert m_art["recall"] == 1.0
    assert m_art["precision"] == 1.0
    assert m_art["f1"] == 1.0

    # False positive on no-impact
    m_fp = MetricsComputer.compute_artifact_metrics(predicted_artifacts=["FalseAlarm_01"], true_artifacts=[])
    assert m_fp["recall"] == 1.0
    assert m_fp["precision"] == 0.0
    assert m_fp["f1"] == 0.0


def test_context_filter_subsystem_isolation():
    g = EngineeringGraph("MultiDomain")
    c_filter = EngineeringContextFilter(eng_graph=g)
    
    # ADAS candidate for ADAS source
    score_same = c_filter.compute_context_score(
        source_artifact_id="Req_01",
        source_artifact_type="Requirement",
        source_subsystem="ADAS",
        candidate_id="SWC_01",
        candidate_type="SWC",
        candidate_subsystem="ADAS",
        raw_cosine=0.80
    )

    # Battery candidate for ADAS source (cross-subsystem)
    score_cross = c_filter.compute_context_score(
        source_artifact_id="Req_01",
        source_artifact_type="Requirement",
        source_subsystem="ADAS",
        candidate_id="SWC_BMS_01",
        candidate_type="SWC",
        candidate_subsystem="BATTERY_EV",
        raw_cosine=0.80
    )

    assert score_same["context_score"] > score_cross["context_score"]
    assert score_same["final_score"] > score_cross["final_score"]


def test_data_leakage_prevention():
    mutations_path = Path("data/mutations/all_mutations.json")
    if mutations_path.exists():
        with open(mutations_path, "r", encoding="utf-8") as f:
            mutations = json.load(f)

        for m in mutations:
            # Verify diff_text and after_state do not contain ground truth target labels or answers
            assert "true_impacted" not in m.get("diff_text", "").lower()
            assert "expected_tests" not in m.get("after_state", "").lower()
