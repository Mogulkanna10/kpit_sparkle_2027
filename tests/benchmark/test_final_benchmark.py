"""
tests/benchmark/test_final_benchmark.py
Gate 11 — Final Benchmark Reconstruction Validation Suite

All tests run against the ALREADY-COMPUTED outputs in:
  - benchmark/final/outputs/
  - artifacts/final_benchmark_results.json

Tests are PASS/FAIL against pre-defined acceptance criteria.
If the benchmark has not yet been run, tests will fail with an informative skip.
"""
import json
import sys
import pytest
import pandas as pd
import numpy as np
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from benchmark.final.config import (
    MASTER_SEED, TOTAL_MUTATIONS, CALIBRATION_SIZE, VALIDATION_SIZE, TEST_SIZE,
    PROJECTS, METHODS, SAFETY_GATE_MANDATORY, OUTPUT_DIR, ARTIFACT_JSON, VERSION
)

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def artifact() -> dict:
    """Load the final benchmark artifact JSON."""
    p = Path(ARTIFACT_JSON)
    if not p.exists():
        pytest.skip(f"Benchmark artifact not found: {ARTIFACT_JSON}. Run benchmark/final/runner.py first.")
    return json.loads(p.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def impact_df() -> pd.DataFrame:
    p = Path(OUTPUT_DIR) / "impact_results.csv"
    if not p.exists():
        pytest.skip(f"Impact CSV not found: {p}")
    return pd.read_csv(p)


@pytest.fixture(scope="module")
def reg_df() -> pd.DataFrame:
    p = Path(OUTPUT_DIR) / "regression_results.csv"
    if not p.exists():
        pytest.skip(f"Regression CSV not found: {p}")
    return pd.read_csv(p)


@pytest.fixture(scope="module")
def sem_df() -> pd.DataFrame:
    p = Path(OUTPUT_DIR) / "semantic_results.csv"
    if not p.exists():
        pytest.skip(f"Semantic CSV not found: {p}")
    return pd.read_csv(p)


# ── Gate 11 Test 1: Dataset integrity ─────────────────────────────────────────

def test_dataset_size_and_fingerprint(artifact: dict):
    """
    ACCEPTANCE: Exactly 150 mutations were loaded, fingerprint is recorded.
    """
    assert artifact["n_mutations"] == TOTAL_MUTATIONS, \
        f"Expected {TOTAL_MUTATIONS} mutations, got {artifact['n_mutations']}"
    assert artifact["n_calibration"] == CALIBRATION_SIZE
    assert artifact["n_validation"]  == VALIDATION_SIZE
    assert artifact["n_test"]        == TEST_SIZE
    assert "dataset_fingerprint" in artifact
    fp = artifact["dataset_fingerprint"]
    assert isinstance(fp, str) and len(fp) == 16, \
        f"Fingerprint must be 16-char hex, got: {fp!r}"


# ── Gate 11 Test 2: PRNG seed recorded ────────────────────────────────────────

def test_prng_seed_recorded(artifact: dict):
    """
    ACCEPTANCE: Artifact records seed == 42.
    """
    assert artifact["seed"] == MASTER_SEED, \
        f"Expected seed {MASTER_SEED}, got {artifact['seed']}"


# ── Gate 11 Test 3: All methods present in impact dataframe ───────────────────

def test_all_methods_present_in_impact_df(impact_df: pd.DataFrame):
    """
    ACCEPTANCE: All 6 non-Full_Suite methods appear in impact_results.csv.
    """
    expected = [m for m in METHODS if m != "Full_Suite"]
    found = set(impact_df["method"].unique())
    for method in expected:
        assert method in found, f"Method '{method}' missing from impact_results.csv"


# ── Gate 11 Test 4: Safety invariant — 100% safety recall ─────────────────────

def test_safety_invariant_100_percent(artifact: dict, reg_df: pd.DataFrame):
    """
    ACCEPTANCE CRITERION: T_safe ⊆ T_selected for ALL 150 mutations.
    safety_recall == 1.0 for every AURA Hybrid Routed row.
    """
    safety_meta = artifact["safety"]
    assert safety_meta["invariant_verified"] is True, \
        f"Safety invariant failed: {safety_meta}"
    assert safety_meta["pass_pct"] == 100.0 or safety_meta["pass_count"] == safety_meta["total"], \
        f"Safety pass rate not 100%: {safety_meta}"

    # Also verify directly in the DataFrame
    aura_reg = reg_df[reg_df["method"] == "Hybrid_AURA_Routed"]
    violations = aura_reg[aura_reg["safety_recall"] < 1.0]
    assert len(violations) == 0, \
        f"Safety invariant violated for {len(violations)} mutations: {violations[['mutation_id','safety_recall']].head()}"


# ── Gate 11 Test 5: AURA hybrid beats graph-only recall ───────────────────────

def test_aura_hybrid_beats_graph_recall(artifact: dict):
    """
    ACCEPTANCE: AURA Hybrid Recall > Graph-Only Recall.
    """
    aura_rec  = artifact["metrics"]["aura_hybrid_routed"]["artifact_recall"]
    graph_rec = artifact["metrics"]["graph_only"]["artifact_recall"]
    assert aura_rec >= graph_rec, \
        f"AURA recall ({aura_rec:.4f}) not >= Graph recall ({graph_rec:.4f})"


# ── Gate 11 Test 6: AURA achieves ≥ 50% test suite reduction ──────────────────

def test_test_suite_reduction_target(artifact: dict):
    """
    ACCEPTANCE: AURA Hybrid Routed achieves ≥ 50% mean test-suite reduction.
    """
    reduction = artifact["metrics"]["aura_hybrid_routed"]["test_reduction_pct"]
    assert reduction >= 50.0, \
        f"Test suite reduction {reduction:.2f}% < 50% target"


# ── Gate 11 Test 7: Semantic recall@1 > 0 ─────────────────────────────────────

def test_semantic_recall_at_1_nonzero(artifact: dict):
    """
    ACCEPTANCE: Contextual semantic Recall@1 > 0%.
    """
    r1 = artifact["semantic"]["recall_at_1"]
    assert r1 > 0.0, f"Recall@1 must be > 0, got {r1}"


# ── Gate 11 Test 8: Recall@K is monotonically non-decreasing ──────────────────

def test_recall_at_k_monotone(artifact: dict):
    """
    ACCEPTANCE: Recall@1 ≤ Recall@3 ≤ Recall@5 ≤ Recall@10.
    """
    sem = artifact["semantic"]
    r1, r3, r5, r10 = sem["recall_at_1"], sem["recall_at_3"], sem["recall_at_5"], sem["recall_at_10"]
    assert r1 <= r3 <= r5 <= r10, \
        f"Recall@K not monotone: {r1} -> {r3} -> {r5} -> {r10}"


# ── Gate 11 Test 9: Calibrated threshold within grid ──────────────────────────

def test_calibrated_threshold_within_grid(artifact: dict):
    """
    ACCEPTANCE: Calibrated threshold is a value from THRESHOLD_GRID.
    """
    from benchmark.final.config import THRESHOLD_GRID
    th = artifact["calibrated_threshold"]
    assert th in THRESHOLD_GRID, \
        f"Calibrated threshold {th} not in THRESHOLD_GRID {THRESHOLD_GRID}"


# ── Gate 11 Test 10: Cross-project coverage ───────────────────────────────────

def test_cross_project_coverage(impact_df: pd.DataFrame):
    """
    ACCEPTANCE: All 3 projects appear in impact_results.csv.
    """
    found = set(impact_df["project"].unique())
    for pid in PROJECTS:
        assert pid in found, f"Project '{pid}' missing from impact_results.csv"


# ── Gate 11 Test 11: Full_Suite row present in regression ─────────────────────

def test_full_suite_method_in_regression(reg_df: pd.DataFrame):
    """
    ACCEPTANCE: Full_Suite baseline row must appear in regression_results.csv.
    """
    assert "Full_Suite" in reg_df["method"].unique(), \
        "Full_Suite method missing from regression_results.csv"


# ── Gate 11 Test 12: Impact rows count correct ────────────────────────────────

def test_impact_row_count(impact_df: pd.DataFrame):
    """
    ACCEPTANCE: impact_df has exactly 150 mutations × 6 methods = 900 rows.
    Expected methods (excluding Full_Suite): 6.
    """
    non_full = impact_df[impact_df["method"] != "Full_Suite"]
    n_methods = len(non_full["method"].unique())
    n_mutations = len(non_full["mutation_id"].unique())
    expected_rows = n_methods * n_mutations
    assert len(non_full) == expected_rows, \
        f"Expected {expected_rows} rows, got {len(non_full)}"
    assert n_mutations == TOTAL_MUTATIONS, \
        f"Expected {TOTAL_MUTATIONS} mutations, got {n_mutations}"


# ── Gate 11 Test 13: F1 scores in [0, 1] ─────────────────────────────────────

def test_f1_scores_bounded(impact_df: pd.DataFrame, reg_df: pd.DataFrame):
    """
    ACCEPTANCE: All F1 values are in [0.0, 1.0].
    """
    assert (impact_df["f1"] >= 0.0).all() and (impact_df["f1"] <= 1.0).all(), \
        "Impact F1 out of [0,1]"
    assert (reg_df["f1"] >= 0.0).all() and (reg_df["f1"] <= 1.0).all(), \
        "Regression F1 out of [0,1]"


# ── Gate 11 Test 14: Output files all exist ───────────────────────────────────

def test_output_files_exist():
    """
    ACCEPTANCE: All 7 output files exist.
    """
    files = [
        Path(OUTPUT_DIR) / "impact_results.csv",
        Path(OUTPUT_DIR) / "regression_results.csv",
        Path(OUTPUT_DIR) / "semantic_results.csv",
        Path(OUTPUT_DIR) / "ablation_results.csv",
        Path(OUTPUT_DIR) / "scale_results.csv",
        Path(OUTPUT_DIR) / "summary_table.csv",
        Path("reports/final/FINAL_BENCHMARK_REPORT.md"),
        Path(ARTIFACT_JSON),
    ]
    missing = [str(f) for f in files if not f.exists()]
    assert not missing, f"Missing output files: {missing}"


# ── Gate 11 Test 15: Version tag correct ─────────────────────────────────────

def test_artifact_version_tag(artifact: dict):
    """
    ACCEPTANCE: Artifact version matches frozen config VERSION.
    """
    assert artifact["version"] == VERSION, \
        f"Version mismatch: artifact={artifact['version']!r}, config={VERSION!r}"
