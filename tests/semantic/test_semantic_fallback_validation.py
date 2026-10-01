"""
Gate 7: Semantic Fallback and Context Filtering Validation Suite
Validates all required semantic fallback and context gate conditions:
1. Hidden semantic dependency recovery
2. Same words / different subsystem decoy rejection
3. Same acronym / different meaning (TTC ADAS vs TTC Telemetry)
4. Same physical quantity / different function (Hydraulic vs Parking brake)
5. Documentation terminology / synonym recovery
6. Dead unrelated code rejection
7. Cross-artifact decoy rejection (type incompatibility)
8. Ambiguous case handling (REVIEW_REQUIRED abstention)
9. Missing context handling
10. Missing index handling (empty index)
11. Stale index detection (StaleIndexError)
12. Low similarity rejection
13. Top-K boundary enforcement
14. Threshold boundary enforcement
"""
import pytest
import numpy as np
from pathlib import Path

from src.semantic.embedder import SemanticEmbedder
from src.semantic.index import FAISSSemanticIndex, IndexedArtifact
from src.semantic.context_filter import ContextFilter
from src.semantic.retriever import ContextualRetriever, RetrievedCandidate
from src.api.pipeline import AuraImpactPipeline, StaleIndexError
from src.ingestion.git_diff import ChangedArtifact


@pytest.fixture
def semantic_setup():
    """Sets up an embedder, populated index, and retriever."""
    embedder = SemanticEmbedder(dimension=384)
    index = FAISSSemanticIndex(dimension=384)
    
    artifacts = [
        # ADAS Genuine target
        IndexedArtifact("FN_AEB_ACTUATE", "C_Function", "ADAS", "ECU_1", "Emergency braking hydraulic deceleration control actuation"),
        IndexedArtifact("FN_CALC_TTC", "C_Function", "ADAS", "ECU_1", "Calculate time to collision radar distance velocity"),
        # Body Electronics Decoy
        IndexedArtifact("FN_BRAKE_LIGHT", "C_Function", "Body_Electronics", "ECU_Body", "Emergency braking stop light illumination activation"),
        # Telemetry Decoy (Same TTC acronym)
        IndexedArtifact("FN_TELEMETRY_TTC", "C_Function", "Infotainment", "ECU_Telematics", "TTC transmit telemetry counter buffer packet transmission"),
        # Chassis Parking Brake Decoy (Same physical quantity: braking)
        IndexedArtifact("FN_PARK_BRAKE", "C_Function", "Chassis", "ECU_Chassis", "Electric parking brake hold motor clamping actuator"),
        # Dead code
        IndexedArtifact("FN_DEPRECATED_STUB", "C_Function", "ADAS", "ECU_1", "Deprecated legacy obsolete calibration stub non_functional"),
        # Incompatible artifact type decoy
        IndexedArtifact("DOC_BRAKE_GUIDE", "UserManual", "ADAS", "ECU_1", "Driver assistance emergency braking manual guide")
    ]
    
    vecs = embedder.embed_batch([a.text_content for a in artifacts])
    index.add_artifacts(artifacts, vecs)
    
    c_filter = ContextFilter(enforce_subsystem=True, enforce_artifact_type=True, min_context_score=0.50)
    retriever = ContextualRetriever(embedder, index, c_filter, similarity_threshold=0.45, top_k=5)
    
    return embedder, index, c_filter, retriever


def test_hidden_semantic_dependency(semantic_setup):
    """Scenario 1: Hidden semantic dependency without syntactic link is recovered."""
    _, _, _, retriever = semantic_setup
    results = retriever.retrieve(
        query_text="Braking deceleration control threshold trigger",
        query_context={"subsystem": "ADAS", "artifact_type": "Requirement"}
    )
    accepted = [r for r in results if r.status == "ACCEPT"]
    assert len(accepted) > 0
    assert any(r.artifact_id == "FN_AEB_ACTUATE" for r in accepted)


def test_same_words_different_subsystem(semantic_setup):
    """Scenario 2: Same words in different subsystem (Body Electronics) suppressed from accepted results and rejected by ContextFilter."""
    _, _, c_filter, retriever = semantic_setup
    
    # 1. Pipeline/Retriever suppression: Body_Electronics decoy is NEVER in accepted results
    results = retriever.retrieve(
        query_text="Emergency braking activation",
        query_context={"subsystem": "ADAS", "artifact_type": "Requirement"}
    )
    accepted_ids = {r.artifact_id for r in results if r.status == "ACCEPT"}
    assert "FN_BRAKE_LIGHT" not in accepted_ids
    
    # 2. ContextFilter direct evaluation: explicitly rejects Body_Electronics decoy with Subsystem mismatch
    decoy_art = IndexedArtifact("FN_BRAKE_LIGHT", "C_Function", "Body_Electronics", "ECU_Body", "Emergency braking stop light illumination activation")
    filter_res = c_filter.evaluate(decoy_art, {"subsystem": "ADAS", "artifact_type": "Requirement"})
    assert filter_res.passed is False
    assert "Subsystem mismatch" in filter_res.rejection_reason


def test_same_acronym_different_meaning(semantic_setup):
    """Scenario 3: Same acronym (TTC) in Telemetry suppressed and rejected when querying ADAS."""
    _, _, c_filter, retriever = semantic_setup
    
    # Retriever suppresses telemetry from ADAS acceptance
    results = retriever.retrieve(
        query_text="TTC threshold calculation",
        query_context={"subsystem": "ADAS", "artifact_type": "Requirement"}
    )
    accepted_ids = {r.artifact_id for r in results if r.status == "ACCEPT"}
    assert "FN_TELEMETRY_TTC" not in accepted_ids
    
    # ContextFilter explicitly rejects Telemetry candidate
    telemetry_art = IndexedArtifact("FN_TELEMETRY_TTC", "C_Function", "Infotainment", "ECU_Telematics", "TTC transmit telemetry counter buffer packet transmission")
    filter_res = c_filter.evaluate(telemetry_art, {"subsystem": "ADAS", "artifact_type": "Requirement"})
    assert filter_res.passed is False
    assert "Subsystem mismatch" in filter_res.rejection_reason


def test_same_physical_quantity_different_function(semantic_setup):
    """Scenario 4: Hydraulic braking vs Parking brake hold rejected by subsystem isolation."""
    _, _, c_filter, retriever = semantic_setup
    
    results = retriever.retrieve(
        query_text="Braking actuator deceleration",
        query_context={"subsystem": "ADAS", "artifact_type": "Requirement"}
    )
    accepted_ids = {r.artifact_id for r in results if r.status == "ACCEPT"}
    assert "FN_PARK_BRAKE" not in accepted_ids
    
    chassis_art = IndexedArtifact("FN_PARK_BRAKE", "C_Function", "Chassis", "ECU_Chassis", "Electric parking brake hold motor clamping actuator")
    filter_res = c_filter.evaluate(chassis_art, {"subsystem": "ADAS", "artifact_type": "Requirement"})
    assert filter_res.passed is False
    assert "Subsystem mismatch" in filter_res.rejection_reason


def test_documentation_terminology_recovery(semantic_setup):
    """Scenario 5: Paraphrased requirement recovers target function."""
    _, _, _, retriever = semantic_setup
    results = retriever.retrieve(
        query_text="Urgent hazard deceleration intervention",
        query_context={"subsystem": "ADAS", "artifact_type": "Requirement"}
    )
    accepted = [r for r in results if r.status == "ACCEPT"]
    assert any(r.artifact_id == "FN_AEB_ACTUATE" for r in accepted)


def test_dead_unrelated_code_low_similarity(semantic_setup):
    """Scenario 6: Dead unrelated code does not match active functional query."""
    _, _, _, retriever = semantic_setup
    results = retriever.retrieve(
        query_text="Radar speed target velocity calculation",
        query_context={"subsystem": "ADAS", "artifact_type": "Requirement"}
    )
    dead_code = [r for r in results if r.artifact_id == "FN_DEPRECATED_STUB"]
    assert len(dead_code) == 0 or dead_code[0].status == "REJECT"


def test_cross_artifact_decoy_rejection(semantic_setup):
    """Scenario 7: Incompatible artifact type (UserManual) rejected by context filter."""
    _, _, _, retriever = semantic_setup
    results = retriever.retrieve(
        query_text="Emergency braking manual guide",
        query_context={"subsystem": "ADAS", "artifact_type": "Requirement"}
    )
    doc_decoy = [r for r in results if r.artifact_id == "DOC_BRAKE_GUIDE"]
    assert len(doc_decoy) == 1
    assert doc_decoy[0].status == "REJECT"
    assert "Incompatible target artifact type" in doc_decoy[0].rejection_reason


def test_ambiguous_case_abstention(semantic_setup):
    """Scenario 8: Ambiguous or under-specified requirement flagged as REVIEW_REQUIRED."""
    _, _, _, retriever = semantic_setup
    results = retriever.retrieve(
        query_text="Ambiguous unclear parameter modification for review",
        query_context={"subsystem": "ADAS", "artifact_type": "Requirement"}
    )
    assert len(results) > 0
    assert any(r.status == "REVIEW_REQUIRED" for r in results)


def test_missing_context_handling(semantic_setup):
    """Scenario 9: Missing subsystem context does not crash and defaults safely."""
    _, _, _, retriever = semantic_setup
    results = retriever.retrieve(
        query_text="Emergency deceleration actuation",
        query_context={}  # Empty context
    )
    assert isinstance(results, list)


def test_missing_index_handling():
    """Scenario 10: Empty index returns 0 results gracefully."""
    embedder = SemanticEmbedder(dimension=384)
    empty_index = FAISSSemanticIndex(dimension=384)
    c_filter = ContextFilter()
    retriever = ContextualRetriever(embedder, empty_index, c_filter)
    
    results = retriever.retrieve("Any query text", {"subsystem": "ADAS"})
    assert len(results) == 0


def test_stale_index_detection(tmp_path):
    """Scenario 11: Modifying repository file raises StaleIndexError when freshness enforced."""
    # Create mock repo
    repo = tmp_path / "repo"
    repo.mkdir()
    req_dir = repo / "requirements"
    req_dir.mkdir()
    req_file = req_dir / "req.json"
    req_file.write_text('[{"req_id": "REQ_01", "subsystem": "ADAS", "ecu": "ECU_1", "description": "v1"}]', encoding="utf-8")
    
    pipeline = AuraImpactPipeline()
    pipeline.ingest_repository(repo)
    
    # Check staleness before modification -> should not be stale
    is_stale, _ = pipeline.check_staleness(repo)
    assert is_stale is False
    
    # Modify file on disk
    req_file.write_text('[{"req_id": "REQ_01", "subsystem": "ADAS", "ecu": "ECU_1", "description": "v2_MODIFIED"}]', encoding="utf-8")
    
    # Check staleness after modification -> must be stale
    is_stale, stale_files = pipeline.check_staleness(repo)
    assert is_stale is True
    assert any("MODIFIED" in s for s in stale_files)
    
    # Enforcing freshness in analyze_change must raise StaleIndexError
    ch = ChangedArtifact("REQ_01", "Requirement", "ADAS", "ECU_1", "MODIFY")
    with pytest.raises(StaleIndexError):
        pipeline.analyze_change(ch, repo_dir=repo, enforce_freshness=True)


def test_low_similarity_rejection(semantic_setup):
    """Scenario 12: Candidate with similarity below threshold rejected with explicit reason."""
    _, _, _, retriever = semantic_setup
    results = retriever.retrieve(
        query_text="Completely unrelated topic about celestial navigation and planets",
        query_context={"subsystem": "ADAS", "artifact_type": "Requirement"},
        threshold_override=0.70
    )
    for r in results:
        assert r.status == "REJECT"
        assert any(k in r.rejection_reason for k in ["below threshold", "mismatch", "Incompatible"])


def test_top_k_boundary(semantic_setup):
    """Scenario 13: Results strictly bounded by top_k."""
    _, _, _, retriever = semantic_setup
    retriever.top_k = 3
    results = retriever.retrieve(
        query_text="Emergency braking",
        query_context={"subsystem": "ADAS", "artifact_type": "Requirement"}
    )
    assert len(results) <= 3


def test_threshold_boundary(semantic_setup):
    """Scenario 14: Overriding threshold dynamically strictly controls ACCEPT vs REJECT."""
    _, _, _, retriever = semantic_setup
    query = "Emergency braking hydraulic deceleration"
    ctx = {"subsystem": "ADAS", "artifact_type": "Requirement"}
    
    # Low threshold accepts
    low_res = retriever.retrieve(query, ctx, threshold_override=0.20)
    low_accepted = [r for r in low_res if r.status == "ACCEPT"]
    
    # Very high threshold rejects
    high_res = retriever.retrieve(query, ctx, threshold_override=0.99)
    high_accepted = [r for r in high_res if r.status == "ACCEPT"]
    
    assert len(low_accepted) >= len(high_accepted)
    assert len(high_accepted) == 0
