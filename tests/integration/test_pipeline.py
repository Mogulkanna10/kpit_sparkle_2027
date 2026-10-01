"""
Integration tests for end-to-end impact analysis and regression selection
"""
import pytest
from pathlib import Path
from src.benchmark.runners import BenchmarkRunner
from src.impact.change_detector import ChangeContext


def test_end_to_end_pipeline():
    runner = BenchmarkRunner(seed=42)
    p_ctx = runner.setup_project("ADAS", Path("data/projects/adas"))

    change = ChangeContext(
        change_id="TEST_001",
        project="ADAS",
        source_artifact="src/adas_controller.c",
        target_node_id="ADAS_Func_001",
        artifact_type="C_CODE",
        before_content="ADAS_Func_001 implementation v1",
        after_content="ADAS_Func_001 implementation v2",
        diff_text="- v1\n+ v2",
        change_semantics="Modified primary ADAS control function",
        metadata={"change_type": "M10"}
    )

    res_hybrid = p_ctx["hybrid_routed"].run(change)
    assert res_hybrid["change_category"] == "STRUCTURAL"
    assert "ADAS_Func_001" in res_hybrid["impacted_artifacts"]
    assert len(res_hybrid["selected_tests"]) > 0
