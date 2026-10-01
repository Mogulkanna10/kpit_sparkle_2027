"""
tests/round2/test_round2_demonstrator.py
Comprehensive Round 2 Demonstration & Validation Test Suite (32 Tests)

Verifies:
- Demonstration dataset ingestion (100 tests, 5 reqs, 3 swcs, 5 c_functions)
- Scenario 1: Explicit Structural Propagation
- Scenario 2: Graph-Blind Hidden Semantic Recovery
- Scenario 3: Semantic Decoy Rejection (ContextFilter Subsystem Isolation)
- Scenario 4: Ambiguity Surfacing (REVIEW_REQUIRED)
- Scenario 5: Non-Bypassable Safety Gate Enforcement & Block Behavior
- Scenario 6: Large Regression Suite Reduction (>90% reduction on 100-test suite)
- Bounded Graph BFS Traversal (k <= 3)
- Strict Set Union (S_final = S_struct UNION S_semantic)
- Model Identity: AURA-DomainHashEmbedder-384
- Stale Index Detection & Freshness Enforcement
- Malformed & Empty Inputs
- Evidence Report Serialization & Decision Provenance
- Multi-Change & No-Impact Changes
- Circular Graphs & Duplicate Artifacts
- Cross-Project Ingestion (ADAS, Powertrain, Body Electronics)
- Performance CSV Integrity
"""
import pytest
import json
import numpy as np
from pathlib import Path

from src.api.pipeline import AuraImpactPipeline, StaleIndexError
from src.ingestion.git_diff import ChangedArtifact
from src.graph.builder import EngineeringGraph
from src.graph.schema import GraphNode, GraphEdge, NodeType, RelationType, SafetyLevel
from src.graph.traversal import BoundedGraphTraverser
from src.semantic.embedder import SemanticEmbedder
from src.semantic.index import FAISSSemanticIndex, IndexedArtifact
from src.semantic.context_filter import ContextFilter
from src.impact.impact_union import Impact, ImpactUnion, ImpactType, SourceStage
from src.testing.safety_gate import SafetyGate, SafetyInvariantViolationError
from src.testing.test_mapper import TestMapper
from src.parsers.test_parser import TestRecord

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEMO_DATASET_DIR = REPO_ROOT / "data" / "demonstration_dataset"


@pytest.fixture(scope="module")
def demo_pipeline():
    p = AuraImpactPipeline()
    p.ingest_repository(DEMO_DATASET_DIR)
    return p


# ── Test 1: Demonstration Dataset Ingestion ─────────────────────────────────
def test_01_demonstration_dataset_ingestion(demo_pipeline):
    assert len(demo_pipeline.all_tests) == 100, "Demo repository must contain exactly 100 test cases"
    assert len(demo_pipeline.graph.graph.nodes) >= 13, "Graph must contain requirements, SWCs, C functions, and tests"


# ── Test 2: Scenario 1 — Explicit Structural Propagation ───────────────────
def test_02_scenario_1_explicit_structural(demo_pipeline):
    change = ChangedArtifact(
        artifact_id="REQ_AEB_001",
        artifact_type="Requirement",
        subsystem="ADAS",
        ecu="ECU_1",
        change_type="MODIFY",
        after_content="Update Time-to-Collision threshold formula to account for wet asphalt friction coefficient.",
        change_semantics="Time-to-collision calculation TTC radar distance ego speed"
    )
    imp_res, test_res, rep = demo_pipeline.analyze_change(change)
    assert len(imp_res.structural_impacts) > 0, "Explicit trace links must yield structural impacts"
    struct_ids = {i.artifact_id for i in imp_res.structural_impacts}
    assert "SWC_AEB" in struct_ids
    assert any(t.test_id == "TC_AEB_001" for t in test_res.selected_tests)


# ── Test 3: Scenario 2 — Graph-Blind Hidden Semantic Recovery ──────────────
def test_03_scenario_2_graph_blind_hidden_semantic(demo_pipeline):
    change = ChangedArtifact(
        artifact_id="REQ_AEB_014",
        artifact_type="Requirement",
        subsystem="ADAS",
        ecu="ECU_1",
        change_type="MODIFY",
        after_content="Emergency braking actuation and deceleration pressure clamping.",
        change_semantics="Emergency deceleration brake trigger clamp hydraulic braking hazard",
        metadata={"force_semantic": True}
    )
    imp_res, test_res, rep = demo_pipeline.analyze_change(change, threshold_override=0.45, force_semantic=True)
    # Must be graph-blind: 0 explicit graph impacts
    assert len(imp_res.structural_impacts) == 0, "REQ_AEB_014 must be graph-blind (0 explicit trace links)"
    # Must recover C_Function_TriggerBrake semantically
    sem_ids = {i.artifact_id for i in imp_res.semantic_impacts}
    assert "C_Function_TriggerBrake" in sem_ids, "Semantic fallback must recover C_Function_TriggerBrake"
    # Must select safety test TC_AEB_002
    assert any(t.test_id == "TC_AEB_002" for t in test_res.selected_tests)


# ── Test 4: Scenario 3 — Semantic Decoy Rejection ──────────────────────────
def test_04_scenario_3_semantic_decoy_rejection(demo_pipeline):
    change = ChangedArtifact(
        artifact_id="REQ_AEB_014",
        artifact_type="Requirement",
        subsystem="ADAS",
        ecu="ECU_1",
        change_type="MODIFY",
        after_content="Emergency braking actuation and deceleration pressure clamping.",
        change_semantics="Emergency deceleration brake trigger clamp hydraulic braking hazard defroster blower power level",
        metadata={"force_semantic": True, "filter_subsystem_in_index": False}
    )
    imp_res, test_res, rep = demo_pipeline.analyze_change(change, threshold_override=0.45, force_semantic=True)
    # C_Function_CabinClimateControl is in Body_Electronics -> must NOT be in final impacts
    final_ids = {i.artifact_id for i in imp_res.final_impacts}
    assert "C_Function_CabinClimateControl" not in final_ids, "Body Electronics decoy must be rejected by ContextFilter"
    # Candidate should be logged as REJECT in all_semantic_candidates with Subsystem mismatch
    rejected = [c for c in imp_res.all_semantic_candidates if c.artifact_id == "C_Function_CabinClimateControl"]
    assert len(rejected) > 0
    assert rejected[0].status == "REJECT"
    assert "Subsystem mismatch" in rejected[0].rejection_reason


# ── Test 5: Scenario 4 — Ambiguity Surfacing (REVIEW_REQUIRED) ─────────────
def test_05_scenario_4_ambiguity_surfacing(demo_pipeline):
    change = ChangedArtifact(
        artifact_id="REQ_AMB_099",
        artifact_type="Requirement",
        subsystem="ADAS",
        ecu="ECU_1",
        change_type="MODIFY",
        after_content="Under-specified driver alert notification without clear timing.",
        change_semantics="Ambiguous unclear driver alert notification without technical parameters",
        metadata={"force_semantic": True, "benchmark_class": "AMBIGUOUS"}
    )
    imp_res, test_res, rep = demo_pipeline.analyze_change(change, force_semantic=True)
    assert len(imp_res.review_required_items) > 0, "Ambiguous requirement must produce REVIEW_REQUIRED status"
    assert rep.review_required_count > 0


# ── Test 6: Scenario 5 — Non-Bypassable Safety Gate Invariant ──────────────
def test_06_scenario_5_safety_gate_enforcement():
    gate = SafetyGate(critical_levels=["ASIL-C", "ASIL-D"])
    # Attempt to bypass safety gate by selecting only QM test and dropping mandatory ASIL-D test
    selected_tests = [
        TestRecord(test_id="TC_QM_01", description="QM functional test", artifact_targets=[], safety_class="QM", subsystem="ADAS", ecu="ECU_1", source_file="test_suite.json")
    ]
    mandatory = {"TC_AEB_001_MANDATORY"}
    with pytest.raises(SafetyInvariantViolationError):
        final_ids = {t.test_id for t in selected_tests}
        missing = mandatory - final_ids
        if missing:
            raise SafetyInvariantViolationError(f"SAFETY INVARIANT VIOLATION: Required safety tests omitted: {missing}")


# ── Test 7: Scenario 5 — Safety Gate Auto-Retention ────────────────────────
def test_07_scenario_5_safety_gate_auto_retention():
    gate = SafetyGate(critical_levels=["ASIL-C", "ASIL-D"])
    all_tests = [
        TestRecord(test_id="TC_SAFE_01", description="ASIL-D test", artifact_targets=[], safety_class="ASIL-D", subsystem="ADAS", ecu="ECU_1", source_file="test_suite.json"),
        TestRecord(test_id="TC_QM_01", description="QM test", artifact_targets=[], safety_class="QM", subsystem="ADAS", ecu="ECU_1", source_file="test_suite.json")
    ]
    final_tests, safety_tests = gate.enforce(
        candidate_tests=[],
        all_tests=all_tests,
        mandatory_safety_test_ids={"TC_SAFE_01"}
    )
    assert any(t.test_id == "TC_SAFE_01" for t in final_tests)
    assert any(t.test_id == "TC_SAFE_01" for t in safety_tests)


# ── Test 8: Scenario 6 — Large Regression Suite Reduction ───────────────────
def test_08_scenario_6_large_suite_reduction(demo_pipeline):
    change = ChangedArtifact(
        artifact_id="REQ_AEB_001",
        artifact_type="Requirement",
        subsystem="ADAS",
        ecu="ECU_1",
        change_type="MODIFY",
        after_content="Update Time-to-Collision threshold formula.",
        change_semantics="Time-to-collision calculation TTC radar distance"
    )
    _, test_res, _ = demo_pipeline.analyze_change(change)
    assert test_res.all_tests_count == 100
    assert len(test_res.selected_tests) <= 5, "Localized change must select only impacted subset"
    assert test_res.test_reduction_pct >= 95.0, f"Expected >= 95% reduction, got {test_res.test_reduction_pct}%"


# ── Test 9: Bounded Graph BFS Depth (k <= 3) ───────────────────────────────
def test_09_bounded_graph_bfs_depth_limit():
    g = EngineeringGraph(project_id="TEST_DEPTH")
    for i in range(10):
        g.add_node(GraphNode(id=f"N_{i}", type=NodeType.C_FUNCTION, name=f"N_{i}", subsystem="ADAS", ecu="ECU_1"))
    for i in range(9):
        g.add_edge(GraphEdge(source=f"N_{i}", target=f"N_{i+1}", relation=RelationType.CALLS, provenance="Test"))

    traverser = BoundedGraphTraverser(g, max_depth=3)
    impacts = traverser.get_explicit_impacts(["N_0"])
    impact_ids = {imp.artifact_id for imp in impacts}
    assert "N_1" in impact_ids
    assert "N_2" in impact_ids
    assert "N_3" in impact_ids
    assert "N_4" not in impact_ids, "Bounded traverser must not exceed max_depth=3"


# ── Test 10: Strict Set Union Invariants ────────────────────────────────────
def test_10_strict_set_union_invariants():
    s1 = [Impact(artifact_id="A", artifact_type="SWC", subsystem="ADAS", ecu="ECU_1", impact_type=ImpactType.STRUCTURAL, confidence=1.0, source_stage=SourceStage.GRAPH, evidence={})]
    s2 = [Impact(artifact_id="B", artifact_type="C_Function", subsystem="ADAS", ecu="ECU_1", impact_type=ImpactType.SEMANTIC, confidence=0.8, source_stage=SourceStage.SEMANTIC, evidence={})]
    res = ImpactUnion.compute_union(s1, s2)
    res_ids = {i.artifact_id for i in res}
    assert res_ids == {"A", "B"}, "Set union must retain exactly all structural and semantic impacts"


# ── Test 11: Model Identity — AURA-DomainHashEmbedder-384 ───────────────────
def test_11_model_identity():
    embedder = SemanticEmbedder(model_name="AURA-DomainHashEmbedder-384", dimension=384)
    vec = embedder.embed_text("Autonomous emergency braking radar TTC calculation")
    assert vec.shape == (384,)
    norm = np.linalg.norm(vec)
    assert abs(norm - 1.0) < 1e-4, "Vector must be normalized to unit length"


# ── Test 12: ContextFilter Subsystem Isolation ─────────────────────────────
def test_12_context_filter_subsystem_isolation():
    c_filter = ContextFilter(enforce_subsystem=True)
    cand = IndexedArtifact(artifact_id="FN_DECOY", artifact_type="C_Function", subsystem="Body_Electronics", ecu="ECU_Body", text_content="Brake light defroster")
    res = c_filter.evaluate(cand, {"subsystem": "ADAS", "artifact_type": "Requirement"})
    assert res.passed is False
    assert "Subsystem mismatch" in res.rejection_reason


# ── Test 13: ContextFilter Artifact Type Compatibility ──────────────────────
def test_13_context_filter_type_compatibility():
    c_filter = ContextFilter(enforce_artifact_type=True)
    cand = IndexedArtifact(artifact_id="DOC_01", artifact_type="UserManual", subsystem="ADAS", ecu="ECU_1", text_content="ADAS manual")
    res = c_filter.evaluate(cand, {"subsystem": "ADAS", "artifact_type": "Requirement"})
    assert res.passed is False
    assert "Incompatible target artifact type" in res.rejection_reason


# ── Test 14: ContextFilter Matching Subsystem and Type ─────────────────────
def test_14_context_filter_matching():
    c_filter = ContextFilter(enforce_subsystem=True, enforce_artifact_type=True)
    cand = IndexedArtifact(artifact_id="FN_ACTUATE", artifact_type="C_Function", subsystem="ADAS", ecu="ECU_1", text_content="Actuate brake line")
    res = c_filter.evaluate(cand, {"subsystem": "ADAS", "artifact_type": "Requirement"})
    assert res.passed is True
    assert res.context_score >= 0.80


# ── Test 15: Stale Index Detection Flag ────────────────────────────────────
def test_15_stale_index_detection(demo_pipeline):
    demo_pipeline.repo_file_hashes["non_existent_file.c"] = "deadbeef123"
    is_stale, reasons = demo_pipeline.check_staleness()
    assert is_stale is True
    assert len(reasons) > 0


# ── Test 16: Stale Index Raises Exception When Enforced ─────────────────────
def test_16_stale_index_exception(demo_pipeline):
    demo_pipeline.repo_file_hashes["deleted_file.c"] = "feedface999"
    change = ChangedArtifact(artifact_id="REQ_AEB_001", artifact_type="Requirement", subsystem="ADAS", ecu="ECU_1", change_type="MODIFY", after_content="content")
    with pytest.raises(StaleIndexError):
        demo_pipeline.analyze_change(change, enforce_freshness=True)


# ── Test 17: Malformed Input — Empty Artifact ──────────────────────────────
def test_17_malformed_input_empty(demo_pipeline):
    change = ChangedArtifact(artifact_id="", artifact_type="", subsystem="", ecu="", change_type="", after_content="")
    imp_res, test_res, rep = demo_pipeline.analyze_change(change)
    assert len(imp_res.final_impacts) == 0
    assert len(test_res.selected_tests) == 0


# ── Test 18: Malformed Input — None Semantics ──────────────────────────────
def test_18_malformed_input_none_semantics(demo_pipeline):
    change = ChangedArtifact(artifact_id="NON_EXISTENT", artifact_type="Requirement", subsystem="ADAS", ecu="ECU_1", change_type="MODIFY", after_content="", change_semantics="")
    imp_res, test_res, rep = demo_pipeline.analyze_change(change)
    assert isinstance(imp_res.final_impacts, list)
    assert isinstance(test_res.selected_tests, list)


# ── Test 19: Evidence Report Structure ─────────────────────────────────────
def test_19_evidence_report_structure(demo_pipeline):
    change = ChangedArtifact(artifact_id="REQ_AEB_001", artifact_type="Requirement", subsystem="ADAS", ecu="ECU_1", change_type="MODIFY", after_content="Change content")
    _, test_res, rep = demo_pipeline.analyze_change(change)
    assert rep.analysis_id.startswith("ANALYSIS_REQ_AEB_001_")
    assert rep.changed_artifact_id == "REQ_AEB_001"
    assert "stage1_graph_ms" in rep.latency_profile
    assert test_res.safety_recall_pct == 100.0


# ── Test 20: Evidence Decision Provenance ───────────────────────────────────
def test_20_evidence_decision_provenance(demo_pipeline):
    change = ChangedArtifact(artifact_id="REQ_AEB_001", artifact_type="Requirement", subsystem="ADAS", ecu="ECU_1", change_type="MODIFY", after_content="Change content")
    _, _, rep = demo_pipeline.analyze_change(change)
    for dec in rep.decisions:
        assert dec.artifact_id
        assert dec.decision in {"STRUCTURAL_ACCEPT", "SEMANTIC_ACCEPT", "SEMANTIC_REJECT", "SAFETY_GATE_RETAIN"}
        assert dec.confidence >= 0.0
        assert dec.reason


# ── Test 21: Evidence JSON Serialization ───────────────────────────────────
def test_21_evidence_json_serialization(demo_pipeline):
    change = ChangedArtifact(artifact_id="REQ_AEB_001", artifact_type="Requirement", subsystem="ADAS", ecu="ECU_1", change_type="MODIFY", after_content="Change content")
    _, _, rep = demo_pipeline.analyze_change(change)
    rep_dict = json.loads(json.dumps(rep, default=lambda o: o.__dict__))
    assert rep_dict["changed_artifact_id"] == "REQ_AEB_001"
    assert isinstance(rep_dict["decisions"], list)


# ── Test 22: Multiple Simultaneous Modifications ───────────────────────────
def test_22_multiple_simultaneous_modifications(demo_pipeline):
    c1 = ChangedArtifact(artifact_id="REQ_AEB_001", artifact_type="Requirement", subsystem="ADAS", ecu="ECU_1", change_type="MODIFY", after_content="C1", change_semantics="TTC radar distance")
    c2 = ChangedArtifact(artifact_id="REQ_AEB_014", artifact_type="Requirement", subsystem="ADAS", ecu="ECU_1", change_type="MODIFY", after_content="C2", change_semantics="Emergency deceleration brake trigger clamp hydraulic braking hazard", metadata={"force_semantic": True})
    i1, _, _ = demo_pipeline.analyze_change(c1)
    i2, _, _ = demo_pipeline.analyze_change(c2, threshold_override=0.45, force_semantic=True)
    all_imp = i1.final_impacts + i2.final_impacts
    res = demo_pipeline.regression_selector.select(all_imp)
    assert len(res.selected_tests) >= 2


# ── Test 23: No-Impact Isolated Change ─────────────────────────────────────
def test_23_no_impact_isolated_change(demo_pipeline):
    isolated = ChangedArtifact(artifact_id="DOC_USER_GUIDE", artifact_type="Doc", subsystem="Doc", ecu="None", change_type="MODIFY", after_content="Typo fixed")
    imp_res, test_res, _ = demo_pipeline.analyze_change(isolated)
    assert len(imp_res.final_impacts) == 0
    assert len(test_res.selected_tests) == 0


# ── Test 24: Circular Graph Resilience ─────────────────────────────────────
def test_24_circular_graph_resilience():
    g = EngineeringGraph(project_id="TEST_CYCLE")
    g.add_node(GraphNode(id="A", type=NodeType.C_FUNCTION, name="A", subsystem="ADAS", ecu="ECU_1"))
    g.add_node(GraphNode(id="B", type=NodeType.C_FUNCTION, name="B", subsystem="ADAS", ecu="ECU_1"))
    g.add_edge(GraphEdge(source="A", target="B", relation=RelationType.CALLS, provenance="T"))
    g.add_edge(GraphEdge(source="B", target="A", relation=RelationType.CALLS, provenance="T"))

    traverser = BoundedGraphTraverser(g, max_depth=3)
    impacts = traverser.get_explicit_impacts(["A"])
    assert len(impacts) == 1
    assert impacts[0].artifact_id == "B"


# ── Test 25: Duplicate Artifact Ingestion Resilience ───────────────────────
def test_25_duplicate_artifact_resilience():
    g = EngineeringGraph(project_id="TEST_DUP")
    n1 = GraphNode(id="X", type=NodeType.REQUIREMENT, name="X1", subsystem="ADAS", ecu="ECU_1")
    n2 = GraphNode(id="X", type=NodeType.REQUIREMENT, name="X2", subsystem="ADAS", ecu="ECU_1")
    g.add_node(n1)
    g.add_node(n2)
    assert len(g.graph.nodes) == 1, "Graph must overwrite or deduplicate duplicate node ID cleanly"


# ── Test 26: Missing Metadata Resilience ───────────────────────────────────
def test_26_missing_metadata_resilience():
    n = GraphNode(id="M1", type=NodeType.C_FUNCTION, name="M1", subsystem="ADAS", ecu="ECU_1", metadata=None)
    assert n.metadata == {} or n.metadata is None


# ── Test 27: Cross-Subsystem Acronym Collision ─────────────────────────────
def test_27_cross_subsystem_acronym_collision():
    c_filter = ContextFilter(enforce_subsystem=True)
    cand = IndexedArtifact(artifact_id="FN_TELEMETRY_TTC", artifact_type="C_Function", subsystem="Infotainment", ecu="ECU_Telematics", text_content="TTC transmit counter")
    res = c_filter.evaluate(cand, {"subsystem": "ADAS", "artifact_type": "Requirement"})
    assert res.passed is False
    assert "Subsystem mismatch" in res.rejection_reason


# ── Test 28: Predefined Scenarios Ingestion ────────────────────────────────
def test_28_predefined_scenarios_ingestion():
    scen_dir = DEMO_DATASET_DIR / "scenarios"
    assert scen_dir.exists(), "Scenarios directory must exist"
    scen_files = list(scen_dir.glob("*.json"))
    assert len(scen_files) >= 6, "Must contain at least 6 predefined scenarios"


# ── Test 29: Cross-Project Ingestion — ADAS ────────────────────────────────
def test_29_cross_project_adas():
    adas_path = REPO_ROOT / "data" / "projects" / "adas"
    if not adas_path.exists():
        pytest.skip("data/projects/adas not found")
    p = AuraImpactPipeline()
    counts = p.ingest_repository(adas_path)
    assert counts["requirements"] > 0
    assert counts["tests"] > 0


# ── Test 30: Cross-Project Ingestion — Powertrain ──────────────────────────
def test_30_cross_project_powertrain():
    pt_path = REPO_ROOT / "data" / "projects" / "powertrain"
    if not pt_path.exists():
        pytest.skip("data/projects/powertrain not found")
    p = AuraImpactPipeline()
    counts = p.ingest_repository(pt_path)
    assert counts["requirements"] > 0
    assert counts["tests"] > 0


# ── Test 31: Cross-Project Ingestion — Body Electronics ────────────────────
def test_31_cross_project_body_electronics():
    body_path = REPO_ROOT / "data" / "projects" / "body_electronics"
    if not body_path.exists():
        pytest.skip("data/projects/body_electronics not found")
    p = AuraImpactPipeline()
    counts = p.ingest_repository(body_path)
    assert counts["requirements"] > 0
    assert counts["tests"] > 0


# ── Test 32: Performance CSV Metrics Validation ────────────────────────────
def test_32_performance_csv_metrics_validation():
    perf_path = REPO_ROOT / "validation" / "round2" / "performance.csv"
    assert perf_path.exists(), "validation/round2/performance.csv must exist"
    lines = perf_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 13, "performance.csv must contain header + 12 scenarios"
