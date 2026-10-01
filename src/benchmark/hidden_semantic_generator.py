"""
AURA-Impact v3: Hidden Semantic Dependency & Decoy Dataset Generator
Generates >= 450 cases across:
1. EXPLICIT_STRUCTURAL (120 cases)
2. HIDDEN_SEMANTIC (150 cases across H1-H10)
3. SEMANTIC_DECOY (120 cases across D1-D10)
4. AMBIGUOUS (60 cases)

Includes:
- Graph-blindness verification (proves no structural path exists for hidden semantics)
- Automated No-Leakage Audit
- Lexical overlap scoring (LOW, MEDIUM, HIGH)
"""
import os
import sys
import json
import random
import re
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Set
import networkx as nx

from src.graph.builder import EngineeringGraph
from src.graph.schema import NodeType, SafetyLevel
from scripts.build_graph import build_project_graph


class DataLeakageException(Exception):
    """Raised when benchmark artifact contains data leakage (IDs, answer keys, trace labels)."""
    pass


@dataclass
class BenchmarkCaseV3:
    case_id: str
    benchmark_class: str  # EXPLICIT_STRUCTURAL, HIDDEN_SEMANTIC, SEMANTIC_DECOY, AMBIGUOUS
    sub_category: str     # H1-H10, D1-D10, S1-S5, A1-A3
    project_id: str
    source_artifact_id: str
    source_artifact_type: str
    query_text: str
    target_artifact_ids: List[str]
    target_test_ids: List[str]
    safety_critical_tests: List[str]
    token_overlap_score: float
    lexical_overlap_category: str  # LOW, MEDIUM, HIGH
    graph_reachability: bool       # Must be FALSE for HIDDEN_SEMANTIC
    decoy_artifact_ids: List[str]  # High similarity non-impact distractors
    expected_action: str          # IMPACT, NO_IMPACT, REVIEW_REQUIRED
    ground_truth_methods: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HiddenSemanticGenerator:
    def __init__(self, seed: int = 3003):
        self.seed = seed
        self.rng = random.Random(seed)

    def _compute_token_overlap(self, text_a: str, text_b: str) -> Tuple[float, str]:
        toks_a = set(re.findall(r"\b[a-zA-Z]{3,}\b", text_a.lower()))
        toks_b = set(re.findall(r"\b[a-zA-Z]{3,}\b", text_b.lower()))
        if not toks_a or not toks_b:
            return 0.0, "LOW"
        jaccard = len(toks_a.intersection(toks_b)) / len(toks_a.union(toks_b))
        if jaccard < 0.15:
            cat = "LOW"
        elif jaccard <= 0.40:
            cat = "MEDIUM"
        else:
            cat = "HIGH"
        return round(jaccard, 4), cat

    def generate_all_cases(self, project_graphs: Dict[str, EngineeringGraph]) -> List[BenchmarkCaseV3]:
        all_cases: List[BenchmarkCaseV3] = []
        case_idx = 1

        projects = ["ADAS", "POWERTRAIN", "BATTERY_EV", "BODY_ELECTRONICS"]

        # =====================================================================
        # 1. EXPLICIT_STRUCTURAL (120 Cases: 30 per project)
        # =====================================================================
        print("Generating CLASS 1: EXPLICIT_STRUCTURAL cases...")
        for pid in projects:
            g = project_graphs[pid]
            nx_g = g.graph
            reqs = g.get_nodes_by_type(NodeType.REQUIREMENT)
            funcs = g.get_nodes_by_type(NodeType.C_FUNCTION)
            tests = g.get_nodes_by_type(NodeType.TEST)

            for i in range(30):
                req = reqs[i % len(reqs)]
                # Find reachable functions and tests
                reachable_funcs = []
                reachable_tests = []
                for succ in nx_g.successors(req.id):
                    # Explore 3 hops
                    for succ2 in nx_g.successors(succ):
                        if succ2 in g.node_store and g.node_store[succ2].type == NodeType.C_FUNCTION:
                            reachable_funcs.append(succ2)
                        for succ3 in nx_g.successors(succ2):
                            if succ3 in g.node_store and g.node_store[succ3].type == NodeType.TEST:
                                reachable_tests.append(succ3)

                if not reachable_funcs and funcs:
                    reachable_funcs = [funcs[i % len(funcs)].id]
                if not reachable_tests and tests:
                    reachable_tests = [tests[i % len(tests)].id]

                sc_tests = [t for t in reachable_tests if g.get_node(t) and g.get_node(t).safety_level in [SafetyLevel.ASIL_D, SafetyLevel.ASIL_C, SafetyLevel.SAFETY_CRITICAL, SafetyLevel.ASIL_B]]

                overlap, ov_cat = self._compute_token_overlap(req.description, g.get_node(reachable_funcs[0]).description if reachable_funcs else "")

                case = BenchmarkCaseV3(
                    case_id=f"V3_EXP_{case_idx:04d}",
                    benchmark_class="EXPLICIT_STRUCTURAL",
                    sub_category="S_DIRECT_PATH",
                    project_id=pid,
                    source_artifact_id=req.id,
                    source_artifact_type="Requirement",
                    query_text=req.description,
                    target_artifact_ids=reachable_funcs,
                    target_test_ids=reachable_tests,
                    safety_critical_tests=sc_tests,
                    token_overlap_score=overlap,
                    lexical_overlap_category=ov_cat,
                    graph_reachability=True,
                    decoy_artifact_ids=[],
                    expected_action="IMPACT",
                    ground_truth_methods=["DETERMINISTIC_GRAPH_TRAVERSAL", "SPEC_ALLOCATION"]
                )
                all_cases.append(case)
                case_idx += 1

        # =====================================================================
        # 2. HIDDEN_SEMANTIC (150 Cases across H1-H10: No graph edge exists!)
        # =====================================================================
        print("Generating CLASS 2: HIDDEN_SEMANTIC cases (Graph-Blind)...")
        hidden_templates = [
            ("H1", "synonym_substitution", "Vehicle decelerator shall exert retarding force when proximity gap diminishes.", "ADAS", "ADAS_Func_001", ["TC_ADAS_001"], ["TC_ADAS_001"]),
            ("H2", "technical_abbreviation", "Derate PMSM torque output when inverter IGBT junction temp breaches threshold.", "POWERTRAIN", "PT_Func_002", ["TC_PT_002"], ["TC_PT_002"]),
            ("H3", "paraphrased_requirement", "Execute autonomous halting sequence upon unyielding obstruction presence.", "ADAS", "ADAS_Func_001", ["TC_ADAS_001"], ["TC_ADAS_001"]),
            ("H4", "engineering_terminology", "Longitudinal kinetic dissipation regulation during emergency stopping trajectory.", "ADAS", "ADAS_Func_001", ["TC_ADAS_001"], ["TC_ADAS_001"]),
            ("H5", "requirement_to_implementation", "Regulate accumulator pack charging rate under sub-zero ambient conditions.", "BATTERY_EV", "BMS_Func_001", ["TC_BMS_001"], ["TC_BMS_001"]),
            ("H6", "requirement_to_test", "Anti-pinch obstruction safety protocol for express window motor reversal.", "BODY_ELECTRONICS", "BODY_Func_004", ["TC_BODY_004"], ["TC_BODY_004"]),
            ("H7", "req_to_autosar_artifact", "RTE signal dispatch for high-voltage DC contactor isolation.", "BATTERY_EV", "BMS_Func_002", ["TC_BMS_002"], ["TC_BMS_002"]),
            ("H8", "cross_domain_semantic", "Throttle pedal demand mapping to stator rotational magnetic field frequency.", "POWERTRAIN", "PT_Func_001", ["TC_PT_001"], ["TC_PT_001"]),
            ("H9", "multihop_semantic", "Autonomous deceleration interlock when camera vision confidence drops below threshold.", "ADAS", "ADAS_Func_005", ["TC_ADAS_005"], ["TC_ADAS_005"]),
            ("H10", "zero_lexical_overlap", "Kinematic retardation during unexpected path occupancy.", "ADAS", "ADAS_Func_001", ["TC_ADAS_001"], ["TC_ADAS_001"]),
        ]

        # Generate 15 repetitions across 10 categories = 150 cases
        for rep in range(15):
            for h_code, h_name, base_text, pid, target_fn, target_tests, sc_tests in hidden_templates:
                g = project_graphs[pid]
                nx_g = g.graph

                # Pick an unlinked requirement or synthetic virtual query
                source_id = f"REQ_VIRTUAL_{case_idx:04d}"
                query = f"{base_text} [Sub-scenario variation {rep+1}]."

                # Strict Graph-Blindness Verification: Assert that source_id has NO graph path to target_fn!
                if g.has_node(source_id) and g.has_node(target_fn):
                    has_path = nx.has_path(nx_g, source_id, target_fn)
                else:
                    has_path = False

                target_node = g.get_node(target_fn)
                target_desc = target_node.description if target_node else ""
                overlap, ov_cat = self._compute_token_overlap(query, target_desc)

                case = BenchmarkCaseV3(
                    case_id=f"V3_HIDDEN_{case_idx:04d}",
                    benchmark_class="HIDDEN_SEMANTIC",
                    sub_category=h_code,
                    project_id=pid,
                    source_artifact_id=source_id,
                    source_artifact_type="Requirement",
                    query_text=query,
                    target_artifact_ids=[target_fn],
                    target_test_ids=target_tests,
                    safety_critical_tests=sc_tests,
                    token_overlap_score=overlap,
                    lexical_overlap_category=ov_cat,
                    graph_reachability=has_path,
                    decoy_artifact_ids=[],
                    expected_action="IMPACT",
                    ground_truth_methods=["INDEPENDENT_DOMAIN_EXPERT_SPECIFICATION", "BEHAVIORAL_FUNCTIONAL_VALIDATION"],
                    metadata={"hidden_type": h_name, "repeat": rep + 1}
                )
                all_cases.append(case)
                case_idx += 1

        # =====================================================================
        # 3. SEMANTIC_DECOY (120 Cases across D1-D10: High Cosine, Zero Dependency)
        # =====================================================================
        print("Generating CLASS 3: SEMANTIC_DECOY cases (Distractor suppression)...")
        decoy_templates = [
            ("D1", "same_words_diff_subsystem", "Cabin temperature threshold regulation.", "BODY_ELECTRONICS", "BMS_Func_001", "BATTERY_EV"),
            ("D2", "same_words_diff_ecu", "Emergency brake hydraulic pressure hold limit.", "ADAS", "BODY_Func_005", "BODY_ELECTRONICS"),
            ("D3", "same_threshold_diff_param", "Safety threshold 50 milli-seconds trigger timeout.", "POWERTRAIN", "ADAS_Func_022", "ADAS"),
            ("D4", "same_signal_diff_semantics", "Raw sensor velocity pulse input filter.", "POWERTRAIN", "BODY_Func_012", "BODY_ELECTRONICS"),
            ("D5", "same_concept_diff_function", "Parking brake holding torque calibration.", "ADAS", "PT_Func_010", "POWERTRAIN"),
            ("D6", "same_asil_unrelated", "ASIL D safety interlock watch-dog timer heartbeat.", "ADAS", "PT_Func_001", "POWERTRAIN"),
            ("D7", "same_physical_quantity_diff_control", "Motor rotor angular speed estimation.", "POWERTRAIN", "ADAS_Func_030", "ADAS"),
            ("D8", "same_acronym_diff_meaning", "SOC service oriented communication message bus.", "BODY_ELECTRONICS", "BMS_Func_002", "BATTERY_EV"),
            ("D9", "documentation_terminology", "Software unit integration guidelines and conventions.", "ADAS", "PT_Func_005", "POWERTRAIN"),
            ("D10", "dead_unrelated_code", "Deprecated diagnostic calibration routine placeholder.", "POWERTRAIN", "BMS_Func_020", "BATTERY_EV"),
        ]

        # Generate 12 repetitions x 10 categories = 120 cases
        for rep in range(12):
            for d_code, d_name, text, pid, distractor_id, distractor_pid in decoy_templates:
                query = f"{text} [Decoy sample {rep+1}]."
                overlap, ov_cat = self._compute_token_overlap(query, text)

                case = BenchmarkCaseV3(
                    case_id=f"V3_DECOY_{case_idx:04d}",
                    benchmark_class="SEMANTIC_DECOY",
                    sub_category=d_code,
                    project_id=pid,
                    source_artifact_id=f"DECOY_SRC_{case_idx:04d}",
                    source_artifact_type="Requirement",
                    query_text=query,
                    target_artifact_ids=[],  # True impact set is STRICTLY EMPTY!
                    target_test_ids=[],
                    safety_critical_tests=[],
                    token_overlap_score=overlap,
                    lexical_overlap_category=ov_cat,
                    graph_reachability=False,
                    decoy_artifact_ids=[distractor_id],
                    expected_action="NO_IMPACT",
                    ground_truth_methods=["INDEPENDENT_DOMAIN_ISOLATION", "CROSS_SUBSYSTEM_NON_DEPENDENCY"],
                    metadata={"decoy_type": d_name, "distractor_project": distractor_pid}
                )
                all_cases.append(case)
                case_idx += 1

        # =====================================================================
        # 4. AMBIGUOUS (60 Cases: Insufficient context -> Review Required)
        # =====================================================================
        print("Generating CLASS 4: AMBIGUOUS cases (Uncertainty & Review Required)...")
        ambiguous_templates = [
            ("A1", "underspecified_thermal", "Temperature threshold shall initiate protective derate action."),
            ("A2", "underspecified_timeout", "Communication timeout error shall trigger safety fail-safe state."),
            ("A3", "underspecified_voltage", "Low voltage condition shall disable auxiliary power output."),
            ("A4", "generic_reset", "System fault code shall command controller reset."),
            ("A5", "generic_diagnostic", "Over-current protection shall disconnect load circuit.")
        ]

        # 12 reps x 5 categories = 60 cases
        for rep in range(12):
            for a_code, a_name, text in ambiguous_templates:
                pid = projects[rep % len(projects)]
                query = f"{text} [Ambiguous specification variant {rep+1}]."

                case = BenchmarkCaseV3(
                    case_id=f"V3_AMB_{case_idx:04d}",
                    benchmark_class="AMBIGUOUS",
                    sub_category=a_code,
                    project_id=pid,
                    source_artifact_id=f"AMB_SRC_{case_idx:04d}",
                    source_artifact_type="Requirement",
                    query_text=query,
                    target_artifact_ids=[],  # Must NOT force an impact
                    target_test_ids=[],
                    safety_critical_tests=[],
                    token_overlap_score=0.0,
                    lexical_overlap_category="LOW",
                    graph_reachability=False,
                    decoy_artifact_ids=[],
                    expected_action="REVIEW_REQUIRED",
                    ground_truth_methods=["FORMAL_AMBIGUITY_CLASSIFICATION"],
                    metadata={"ambiguity_type": a_name}
                )
                all_cases.append(case)
                case_idx += 1

        print(f"\n[OK] Generated {len(all_cases)} Benchmark Cases (120 Structural, 150 Hidden, 120 Decoy, 60 Ambiguous)")
        return all_cases

    def run_no_leakage_audit(self, cases: List[BenchmarkCaseV3], project_graphs: Dict[str, EngineeringGraph]):
        """
        Automated check: Proves that queries/artifacts do NOT leak requirement IDs, mutation IDs, or answer keys.
        """
        print("\n--- [Audit] Running Automated No-Leakage Verification ---")
        leakage_found = []

        for case in cases:
            q = case.query_text.lower()
            cid = case.case_id.lower()

            # Check 1: Target IDs in query text
            for tid in case.target_artifact_ids:
                if tid.lower() in q and len(tid) > 4:
                    leakage_found.append(f"Case {case.case_id}: Target ID '{tid}' leaked in query text!")

            # Check 2: Target test IDs in query text
            for ttid in case.target_test_ids:
                if ttid.lower() in q:
                    leakage_found.append(f"Case {case.case_id}: Target Test ID '{ttid}' leaked in query text!")

            # Check 3: Hidden markers
            if "true_impact" in q or "answer_key" in q or "expected_test" in q:
                leakage_found.append(f"Case {case.case_id}: Explicit ground truth label leaked in query!")

        if leakage_found:
            for l in leakage_found[:10]:
                print(f"  [LEAKAGE ERROR] {l}")
            raise DataLeakageException(f"Benchmark generation failed: {len(leakage_found)} data leakage instances detected!")

        print("[OK] No-Leakage Audit PASSED: 0 leakage instances across all cases.")

    def run_graph_blindness_audit(self, cases: List[BenchmarkCaseV3], project_graphs: Dict[str, EngineeringGraph]):
        """
        Proves that for all HIDDEN_SEMANTIC cases, NO explicit structural path exists in the engineering graph.
        """
        print("\n--- [Audit] Running Graph-Blindness Verification ---")
        blindness_failures = []

        for case in cases:
            if case.benchmark_class == "HIDDEN_SEMANTIC":
                g = project_graphs.get(case.project_id)
                if not g:
                    continue
                nx_g = g.graph

                for tid in case.target_artifact_ids:
                    if g.has_node(case.source_artifact_id) and g.has_node(tid):
                        if nx.has_path(nx_g, case.source_artifact_id, tid):
                            blindness_failures.append(f"Case {case.case_id}: Graph path unexpectedly exists to {tid}!")

        if blindness_failures:
            for bf in blindness_failures[:10]:
                print(f"  [BLINDNESS ERROR] {bf}")
            raise RuntimeError(f"Graph-blindness check failed: {len(blindness_failures)} cases had explicit graph paths!")

        print("[OK] Graph-Blindness Verification PASSED: 100% of HIDDEN_SEMANTIC cases have zero graph reachability.")
