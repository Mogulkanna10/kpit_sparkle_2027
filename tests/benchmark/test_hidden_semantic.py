"""
Automated Pytest Suite for AURA-Impact v3 Hidden Semantic Benchmark
"""
import pytest
from pathlib import Path
from src.benchmark.hidden_semantic_generator import HiddenSemanticGenerator
from scripts.build_graph import build_project_graph


def test_hidden_semantic_generation_and_audits():
    projects = ["ADAS", "POWERTRAIN", "BATTERY_EV", "BODY_ELECTRONICS"]
    project_graphs = {}
    for pid in projects:
        p_dir = Path("data/projects") / pid.lower()
        project_graphs[pid] = build_project_graph(pid, p_dir)

    generator = HiddenSemanticGenerator(seed=3003)
    cases = generator.generate_all_cases(project_graphs)

    # 1. Total cases check
    assert len(cases) >= 350
    classes = {c.benchmark_class for c in cases}
    assert "EXPLICIT_STRUCTURAL" in classes
    assert "HIDDEN_SEMANTIC" in classes
    assert "SEMANTIC_DECOY" in classes
    assert "AMBIGUOUS" in classes

    # 2. No-leakage audit
    generator.run_no_leakage_audit(cases, project_graphs)

    # 3. Graph-blindness verification
    generator.run_graph_blindness_audit(cases, project_graphs)


def test_hidden_semantic_graph_blindness():
    # Verify that HIDDEN_SEMANTIC cases have graph_reachability == False
    generator = HiddenSemanticGenerator(seed=3003)
    projects = ["ADAS", "POWERTRAIN", "BATTERY_EV", "BODY_ELECTRONICS"]
    project_graphs = {pid: build_project_graph(pid, Path("data/projects") / pid.lower()) for pid in projects}
    cases = generator.generate_all_cases(project_graphs)

    hidden_cases = [c for c in cases if c.benchmark_class == "HIDDEN_SEMANTIC"]
    assert len(hidden_cases) >= 100
    for c in hidden_cases:
        assert c.graph_reachability is False
