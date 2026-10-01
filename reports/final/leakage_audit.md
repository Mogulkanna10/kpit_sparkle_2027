# AURA-Impact — Gate 13: Benchmark Leakage Audit Report

**Audit Date:** 2026-09-29T23:28:30+05:30  
**Auditor:** Antigravity — Gate 13 Benchmark Leakage Auditor  
**Baseline Tests:** 143 passed  
**Total Tests After Gate 13:** 153/153 PASSED (10 new gate-specific leakage tests)  
**Status:** **PASS** (Zero leakage detected across all 11 vectors)

---

## 1. Executive Summary

A forensic audit of the benchmark data flow and inference pipeline was conducted to ensure complete isolation between ground truth answer labels and the prediction engines (`GraphImpactAnalyzer`, `SemanticImpactAnalyzer`, `AuraImpactHybrid`, `FullSuiteBaseline`, `KeywordBaseline`, `EmbeddingBaseline`).

All 11 potential leakage vectors specified in the controlling Master Prompt were rigorously examined and tested:
1. **Target IDs:** Analyzers evaluate starting from mutated node, but receive zero downstream answers.
2. **Mutation IDs:** Mutation IDs are not used for any answer table lookup; spoofed IDs produce identical results.
3. **Ground-Truth Labels:** Neither `true_impacted_artifacts` nor `true_impacted_tests` are present in `ChangeContext`.
4. **File Names:** Paths point only to source engineering assets; no answers are encoded in filenames.
5. **Directory Names:** Standard project directories only; no leakage.
6. **Answer Keys:** Zero forbidden answer keys found in all 150 mutation records.
7. **Metadata:** Mutation metadata contains exclusively benign categorization fields (`change_type`, `repeat`).
8. **Generated Identifiers:** IDs encode project and category only, not answers.
9. **Semantic Text:** Natural requirement texts contain only domain descriptions; no answer lists injected.
10. **Configuration:** No hardcoded answer mappings exist in YAML/Python configs.
11. **Safety Oracles / Test Names:** Ground-truth safety tests are supplied solely to the downstream ISO 26262 safety filter, completely isolated from artifact impact prediction.

---

## 2. Forensic Inspection of Leakage Vectors

| Vector ID | Vector Description | Status | Evidence & Verification |
|-----------|--------------------|--------|--------------------------|
| **V1** | Target IDs | **CLEAN** | The target node ID indicates the modified root artifact (as in real git diffs). Downstream impact nodes are computed via BFS and semantic retrieval without answer foreknowledge. |
| **V2** | Mutation IDs | **CLEAN** | Verified in `test_mutation_id_independence`: Replacing `mutation_id` with an unknown spoofed string (`SPOOFED_UNKNOWN_ID_9999`) produces identical predicted impacts. |
| **V3** | Ground-Truth Labels | **CLEAN** | Verified in `test_change_context_has_no_answer_fields` and `test_analyzers_execute_without_ground_truth_map`. `ChangeContext` dataclass has no ground-truth fields. |
| **V4** | File Names | **CLEAN** | Verified in `test_file_and_directory_names_contain_no_answers`. Paths point to valid repository files. |
| **V5** | Directory Names | **CLEAN** | Standard project structure (`data/projects/{adas,powertrain,battery_ev}`). |
| **V6** | Answer Keys | **CLEAN** | Verified in `test_no_forbidden_answer_keys_in_mutations`. 0/150 records contain forbidden keys (`true_impacted_artifacts`, `true_impacted_tests`, `ground_truth`, etc.). |
| **V7** | Metadata | **CLEAN** | Verified in `test_no_forbidden_keys_in_mutation_metadata`. All 150 records contain only `{'change_type', 'repeat'}`. |
| **V8** | Generated Identifiers | **CLEAN** | Mutation IDs follow standard format (`{PROJECT}_M{CAT}_{NUM}`). Source code AST scan confirms no answer dictionaries keyed by mutation ID. |
| **V9** | Semantic Text | **CLEAN** | Verified in `test_semantic_index_contains_only_project_nodes`. Natural requirement descriptions contain domain component names without injected answer keys. |
| **V10** | Configuration | **CLEAN** | Frozen configs specify thresholds and depths; zero artifact or test mappings hardcoded. |
| **V11** | Test Names & Safety Oracles | **CLEAN** | Verified in `test_safety_tests_do_not_leak_into_artifact_prediction`. Providing or withholding safety tests has 0.000% effect on predicted artifact impacts. |

---

## 3. Data Flow & Evaluation Isolation

The execution flow in `src/benchmark/runners.py` enforces temporal and scope isolation:

```
[Mutation Record] -> ChangeDetector -> ChangeContext (clean, no GT)
                                           |
                                           v
[Prediction Phase] ----------------> res = fn(ChangeContext)
                                           |
                                           v
                               {pred_arts, sel_tests, latency}
                                           |
[Post-Prediction Evaluation] <-------------+
         |
         +--> MetricsComputer.compute_artifact_metrics(pred_arts, gt.true_impacted_artifacts)
         |
         +--> MetricsComputer.compute_test_metrics(sel_tests, gt.true_impacted_tests, ...)
```

The ground truth records are read solely during the post-prediction evaluation phase to compute benchmark metrics, guaranteeing that no predictor can observe the answers.

---

## 4. Test Suite Verification

Dedicated leakage audit test suite: `tests/benchmark/test_leakage.py`
- Total tests: 10
- Passed: 10
- Failed: 0
- Execution duration: 2.32s

Full regression test suite:
- Total tests: 153
- Passed: 153
- Failed: 0
- Execution duration: 3.21s

---

## 5. Gate Decision

**GATE 13 VERDICT: PASS**

Zero benchmark leakage detected. The evaluation pipeline is completely isolated from answer keys, ground truth labels, and oracles.
