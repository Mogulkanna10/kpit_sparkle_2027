"""
Adversarial and Edge Case Tests for AURA-Impact
"""
import pytest
from pathlib import Path
from src.benchmark.runners import BenchmarkRunner
from src.impact.change_detector import ChangeContext


def test_dead_code_no_impact():
    runner = BenchmarkRunner(seed=42)
    p_ctx = runner.setup_project("ADAS", Path("data/projects/adas"))

    dead_code_change = ChangeContext(
        change_id="ADV_DEAD_01",
        project="ADAS",
        source_artifact="src/adas_controller.c",
        target_node_id="ADAS_Func_001",
        artifact_type="C_CODE",
        before_content="/* dead code */ int a = 1;",
        after_content="/* dead code */ int a = 2;",
        diff_text="- int a = 1;\n+ int a = 2;",
        change_semantics="Modifying unused local dead code",
        metadata={"change_type": "M24"}
    )

    res = p_ctx["hybrid_routed"].run(dead_code_change)
    assert res["change_category"] == "NO_IMPACT"
    assert len(res["impacted_artifacts"]) == 0
    assert len(res["selected_tests"]) == 0


def test_comments_only_no_impact():
    runner = BenchmarkRunner(seed=42)
    p_ctx = runner.setup_project("ADAS", Path("data/projects/adas"))

    comment_change = ChangeContext(
        change_id="ADV_DOC_01",
        project="ADAS",
        source_artifact="docs/architecture.md",
        target_node_id="R_ADAS_001",
        artifact_type="DOC",
        before_content="/* Documentation note: System operates under standard conditions. */",
        after_content="/* Documentation note: System operates under standard conditions (reviewed 2026). */",
        diff_text="- standard\n+ reviewed",
        change_semantics="Documentation only update without code modification",
        metadata={"change_type": "M25"}
    )

    res = p_ctx["hybrid_routed"].run(comment_change)
    assert res["change_category"] == "NO_IMPACT"
    assert len(res["impacted_artifacts"]) == 0
