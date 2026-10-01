"""
Integration Test for AURA-Impact Prototype End-to-End Pipeline
"""
import pytest
from pathlib import Path
from src.api.pipeline import AuraImpactPipeline
from src.ingestion.git_diff import GitDiffParser


def test_end_to_end_pipeline():
    pipeline = AuraImpactPipeline()
    
    # 1. Ingest repository
    counts = pipeline.ingest_repository(Path("examples/demo_repo"))
    assert counts["requirements"] >= 4
    assert counts["swcs"] >= 1
    assert counts["c_functions"] >= 4
    assert counts["tests"] >= 4

    # 2. Ingest structural change
    struct_changes = GitDiffParser.parse_change_file(Path("examples/demo_repo/change_structural.json"))
    assert len(struct_changes) == 1
    imp_s, test_s, rep_s = pipeline.analyze_change(struct_changes[0])
    
    assert len(imp_s.structural_impacts) > 0
    assert len(test_s.selected_tests) > 0
    assert rep_s.safety_tests_count >= 1

    # 3. Ingest hidden semantic change
    hidden_changes = GitDiffParser.parse_change_file(Path("examples/demo_repo/change_hidden_semantic.json"))
    imp_h, test_h, rep_h = pipeline.analyze_change(hidden_changes[0])
    assert len(imp_h.semantic_impacts) > 0
    assert "C_Function_TriggerBrake" in [imp.artifact_id for imp in imp_h.semantic_impacts]

    # 4. Generate Reports
    paths = pipeline.report_generator.export_all(rep_h)
    assert paths["json"].exists()
    assert paths["markdown"].exists()
    assert paths["html"].exists()
