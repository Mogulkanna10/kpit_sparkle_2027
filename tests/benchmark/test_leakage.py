"""
tests/benchmark/test_leakage.py
Gate 13 — Benchmark Leakage Audit Test Suite

Verifies absolute data isolation between ground-truth labels and prediction pipelines.
Ensures zero data leakage across all 11 specified vectors:
  1. Target IDs
  2. Mutation IDs
  3. Ground-truth labels
  4. File names
  5. Directory names
  6. Answer keys
  7. Metadata
  8. Generated identifiers
  9. Semantic text
  10. Configuration
  11. Test names / safety oracles
"""
import ast
import json
import re
from pathlib import Path
from typing import Dict, Any, Set, List

import pytest

from src.benchmark.mutation_generator import MutationRecord
from src.benchmark.ground_truth import GroundTruthRecord
from src.impact.change_detector import ChangeContext, ChangeDetector
from src.benchmark.runners import BenchmarkRunner
from src.benchmark.metrics import MetricsComputer


@pytest.fixture(scope="module")
def dataset():
    mut_path = Path("data/mutations/all_mutations.json")
    gt_path = Path("data/ground_truth/all_ground_truth.json")
    with mut_path.open("r", encoding="utf-8") as f:
        mutations = json.load(f)
    with gt_path.open("r", encoding="utf-8") as f:
        ground_truth = json.load(f)
    return mutations, ground_truth


@pytest.fixture(scope="module")
def runner_and_ctx():
    runner = BenchmarkRunner(seed=42)
    runner.setup_project("ADAS", Path("data/projects/adas"))
    return runner


# ═══════════════════════════════════════════════════════════════════════════════
# VECTOR 1 & 6: ANSWER KEYS & FORBIDDEN GROUND TRUTH FIELDS IN MUTATION RECORDS
# ═══════════════════════════════════════════════════════════════════════════════

def test_no_forbidden_answer_keys_in_mutations(dataset):
    """
    VECTOR 6: Ensure no mutation record contains answer keys or ground truth labels.
    """
    mutations, _ = dataset
    forbidden_keys = {
        "true_impacted_artifacts",
        "true_impacted_tests",
        "ground_truth",
        "answer_key",
        "expected_artifacts",
        "expected_tests",
        "true_safety_tests",
    }
    leaks = []
    for m in mutations:
        found = set(m.keys()).intersection(forbidden_keys)
        if found:
            leaks.append((m.get("mutation_id"), list(found)))
    assert not leaks, f"Direct answer keys leaked in mutation records: {leaks}"


def test_no_forbidden_keys_in_mutation_metadata(dataset):
    """
    VECTOR 7: Ensure mutation metadata contains only benign execution attributes.
    """
    mutations, _ = dataset
    allowed_meta_keys = {"change_type", "repeat", "subsystem"}
    disallowed_found = []
    for m in mutations:
        meta = m.get("metadata", {})
        extra = set(meta.keys()) - allowed_meta_keys
        if extra:
            disallowed_found.append((m.get("mutation_id"), list(extra)))
    assert not disallowed_found, f"Unexpected metadata keys found: {disallowed_found}"


# ═══════════════════════════════════════════════════════════════════════════════
# VECTOR 2: MUTATION ID IS NOT USED AS A LOOKUP KEY FOR ANSWERS
# ═══════════════════════════════════════════════════════════════════════════════

def test_mutation_id_independence(runner_and_ctx, dataset):
    """
    VECTOR 2: Verifies that changing the mutation_id to an arbitrary unknown ID
    does not alter the prediction outputs of the impact analyzers.
    """
    runner = runner_and_ctx
    mutations, _ = dataset
    p_ctx = runner.projects_cache["ADAS"]
    sample_mut = next(m for m in mutations if m["project_id"] == "ADAS")

    detector = ChangeDetector()
    real_ctx = detector.parse_mutation_record(sample_mut)

    # Clone with obfuscated/spoofed change_id
    spoofed_dict = dict(sample_mut)
    spoofed_dict["mutation_id"] = "SPOOFED_UNKNOWN_ID_9999"
    spoofed_ctx = detector.parse_mutation_record(spoofed_dict)

    res_real = p_ctx["graph_only"].run(real_ctx)
    res_spoofed = p_ctx["graph_only"].run(spoofed_ctx)

    assert res_real["impacted_artifacts"] == res_spoofed["impacted_artifacts"], \
        "Graph analyzer changed behavior when mutation_id changed! Possible ID-based answer lookup."

    res_hybrid_real = p_ctx["hybrid_routed"].run(real_ctx)
    res_hybrid_spoofed = p_ctx["hybrid_routed"].run(spoofed_ctx)

    assert res_hybrid_real["impacted_artifacts"] == res_hybrid_spoofed["impacted_artifacts"], \
        "Hybrid analyzer changed behavior when mutation_id changed! Possible ID-based answer lookup."


# ═══════════════════════════════════════════════════════════════════════════════
# VECTOR 3: GROUND TRUTH LABELS NEVER REACH INFERENCE PIPELINES
# ═══════════════════════════════════════════════════════════════════════════════

def test_change_context_has_no_answer_fields():
    """
    VECTOR 3: Ensure ChangeContext dataclass has no fields that could carry ground truth.
    """
    ctx_fields = set(ChangeContext.__dataclass_fields__.keys())
    forbidden = {"ground_truth", "true_impacts", "expected_impacts", "true_tests", "true_artifacts"}
    assert not ctx_fields.intersection(forbidden), \
        f"ChangeContext dataclass has forbidden answer fields: {ctx_fields.intersection(forbidden)}"


def test_analyzers_execute_without_ground_truth_map(runner_and_ctx, dataset):
    """
    VECTOR 3: Verify analyzers execute completely blind without ground truth map.
    """
    runner = runner_and_ctx
    mutations, _ = dataset
    p_ctx = runner.projects_cache["ADAS"]
    sample_mut = next(m for m in mutations if m["project_id"] == "ADAS")

    detector = ChangeDetector()
    c_ctx = detector.parse_mutation_record(sample_mut)

    # Calling analyzers with NO ground truth anywhere in scope
    graph_res = p_ctx["graph_only"].run(c_ctx, ground_truth_safety_tests=None, enforce_safety_gate=False)
    assert "impacted_artifacts" in graph_res
    assert isinstance(graph_res["impacted_artifacts"], list)

    hybrid_res = p_ctx["hybrid_routed"].run(c_ctx, ground_truth_safety_tests=None, enforce_safety_gate=False)
    assert "impacted_artifacts" in hybrid_res
    assert isinstance(hybrid_res["impacted_artifacts"], list)


# ═══════════════════════════════════════════════════════════════════════════════
# VECTOR 11: SAFETY ORACLE DOES NOT LEAK INTO ARTIFACT IMPACT PREDICTION
# ═══════════════════════════════════════════════════════════════════════════════

def test_safety_tests_do_not_leak_into_artifact_prediction(runner_and_ctx, dataset):
    """
    VECTOR 11: Providing ground_truth_safety_tests to AuraImpactHybrid must NOT
    alter or leak into the predicted impacted_artifacts list.
    """
    runner = runner_and_ctx
    mutations, ground_truth = dataset
    gt_map = {g["mutation_id"]: g for g in ground_truth}
    p_ctx = runner.projects_cache["ADAS"]

    sc_mut = next(
        m for m in mutations
        if m["project_id"] == "ADAS" and len(gt_map[m["mutation_id"]]["safety_critical_tests"]) > 0
    )
    c_ctx = ChangeDetector().parse_mutation_record(sc_mut)
    sc_tests = gt_map[sc_mut["mutation_id"]]["safety_critical_tests"]

    # Run with safety tests provided
    res_with_safety = p_ctx["hybrid_routed"].run(
        c_ctx,
        ground_truth_safety_tests=sc_tests,
        enforce_safety_gate=True
    )

    # Run without safety tests provided
    res_without_safety = p_ctx["hybrid_routed"].run(
        c_ctx,
        ground_truth_safety_tests=None,
        enforce_safety_gate=False
    )

    # Artifact impacts MUST be completely identical regardless of safety test input
    assert res_with_safety["impacted_artifacts"] == res_without_safety["impacted_artifacts"], \
        "Impacted artifacts changed when ground_truth_safety_tests was provided! Leakage detected."


# ═══════════════════════════════════════════════════════════════════════════════
# VECTOR 9: SEMANTIC INDEX CONTAINS NO GROUND TRUTH OR LEAKED ANSWERS
# ═══════════════════════════════════════════════════════════════════════════════

def test_semantic_index_contains_only_project_nodes(runner_and_ctx):
    """
    VECTOR 9: Verify that the semantic index contains ONLY node descriptions
    from the target engineering graph, and NO injected benchmark labels or answer keys.
    """
    runner = runner_and_ctx
    p_ctx = runner.projects_cache["ADAS"]
    graph = p_ctx["graph"]
    sem_index = p_ctx["sem_index"]

    graph_node_ids = set(graph.nodes.keys())

    # Check indexed metadata IDs
    if hasattr(sem_index, "metadata") and sem_index.metadata:
        for item in sem_index.metadata:
            node_id = item.get("id") or item.get("node_id")
            assert node_id in graph_node_ids, \
                f"Semantic index contains non-graph node ID '{node_id}' — potential leak!"


# ═══════════════════════════════════════════════════════════════════════════════
# VECTOR 8 & 10: NO HARDCODED ANSWER MAPPINGS IN SOURCE CODE
# ═══════════════════════════════════════════════════════════════════════════════

def test_no_hardcoded_answer_dictionaries_in_src():
    """
    VECTOR 8 & 10: Scan AST of all python files in src/ to verify no hardcoded
    mutation ID -> ground truth dictionaries exist.
    """
    src_dir = Path("src")
    py_files = list(src_dir.rglob("*.py"))
    
    # Pattern matching mutation IDs like ADAS_M01_01, POWERTRAIN_M03_02
    mut_pattern = re.compile(r"(ADAS|POWERTRAIN|BATTERY_EV)_M\d{2}_\d{2}")

    suspicious_files = []
    for fpath in py_files:
        # Exclude generator and evaluation modules which legitimately reference mutation types
        if any(skip in fpath.name for skip in ["mutation_generator.py", "ground_truth.py", "runners.py"]):
            continue
        content = fpath.read_text(encoding="utf-8")
        matches = mut_pattern.findall(content)
        if matches:
            suspicious_files.append((str(fpath), matches))

    assert not suspicious_files, \
        f"Source code files contain hardcoded mutation IDs: {suspicious_files}"


# ═══════════════════════════════════════════════════════════════════════════════
# DATA IMMUTABILITY: BENCHMARK CANNOT ALTER GROUND TRUTH
# ═══════════════════════════════════════════════════════════════════════════════

def test_ground_truth_immutability(runner_and_ctx, dataset):
    """
    Verify that ground-truth objects cannot be mutated or altered during benchmark runs.
    """
    runner = runner_and_ctx
    mutations, ground_truth = dataset
    gt_map = {g["mutation_id"]: GroundTruthRecord(**g) for g in ground_truth}

    sample_id = "ADAS_M01_01"
    gt_record = gt_map[sample_id]
    original_arts = list(gt_record.true_impacted_artifacts)
    original_tests = list(gt_record.true_impacted_tests)

    # Run benchmark evaluation on this record
    p_ctx = runner.projects_cache["ADAS"]
    sample_mut = next(m for m in mutations if m["mutation_id"] == sample_id)
    c_ctx = ChangeDetector().parse_mutation_record(sample_mut)

    res = p_ctx["hybrid_routed"].run(c_ctx)
    MetricsComputer.compute_artifact_metrics(res["impacted_artifacts"], gt_record.true_impacted_artifacts)

    # Verify ground truth record is identical
    assert gt_record.true_impacted_artifacts == original_arts
    assert gt_record.true_impacted_tests == original_tests


# ═══════════════════════════════════════════════════════════════════════════════
# VECTOR 4 & 5: FILE/DIRECTORY NAME ISOLATION
# ═══════════════════════════════════════════════════════════════════════════════

def test_file_and_directory_names_contain_no_answers(dataset):
    """
    VECTOR 4 & 5: Ensure file and directory paths in mutations do not leak
    answer lists or test names.
    """
    mutations, _ = dataset
    for m in mutations:
        src_path = m.get("source_artifact", "")
        # Path should point to requirements or arxml or c files, not benchmark answers
        assert not any(bad in src_path.lower() for bad in ["answer", "ground_truth", "true_impact"]), \
            f"Source artifact path '{src_path}' contains suspicious answer strings"
