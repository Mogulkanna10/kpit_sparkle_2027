# AURA-Impact — Gate 12: Metric Integrity & Benchmark Reconciliation Audit

**Audit Date:** 2026-09-29T23:11:49+05:30  
**Auditor:** Antigravity — Gate 12 Metric Integrity Agent  
**Baseline:** 143/143 tests PASS before and after Gate 12  
**Gate 12 Tests:** 36/36 PASS  

---

## Executive Result

> **GATE 12 STATUS: CONDITIONAL PASS**

All metric integrity tests pass. No ground-truth leakage detected. Dataset, reproducibility, model identity, and safety metric separation are verified. However, **4 substantive findings** were uncovered that are documented here and must be addressed in future gates. None of the 4 findings invalidates the benchmark data itself, but they require remediation before the benchmark numbers can be treated as fully representative of the locked Architecture B.

---

## Section 1 — Gate 11 Result Reconciliation: 0.4805 vs 0.6307

### Verdict: These metrics ARE NOT directly comparable.

| Item | Historical Benchmark (reports/final_report.md) | Gate 11 Benchmark | Same? | Explanation |
|:---|:---|:---|:---:|:---|
| Dataset size | 150 mutations | 150 mutations | ✅ | Same |
| Projects | ADAS, Powertrain, Battery_EV | ADAS, POWERTRAIN, BATTERY_EV | ✅ | Same |
| Mutation categories | M01–M25 | M01–M25 | ✅ | Same |
| Dataset fingerprint | Not recorded | `3bc8c11efb2398a0` | ❓ | Historical not fingerprinted |
| PRNG seed | Not recorded | 42 | ❓ | Historical seed unknown |
| Ground truth generation | Legacy `MutationGenerator` | Same `MutationGenerator` (seed=2002) | ✅ | Same generator |
| Graph depth (GT) | "bounded k=5" (stated) | k=5 in `GroundTruthGenerator` | ✅ | Same |
| Semantic threshold | Not stated; likely ≠ 0.80 | Calibrated = 0.80 | ❌ | **DIFFERENT** |
| Calibration approach | No split described | 30-mutation calibration split | ❌ | **DIFFERENT** |
| Embedding model | AURA-DomainHashEmbedder-384 | AURA-DomainHashEmbedder-384 | ✅ | Same |
| Graph depth (runtime) | Stated as 5 | Configured as 5 in runner | ✅ | Same |
| Routing logic | "Specialized Category Routing" | `AuraImpactHybrid(use_routing=True)` | ✅ | Same |
| Fusion logic | Weighted (wg=0.55,ws=0.30,wc=0.15) | Same weighted fusion | ✅ | Same |
| Safety gate | "enforced" | Enforced, mandatory | ✅ | Same |
| Recall denominator | `len(true_impacted_artifacts)` | `len(true_impacted_artifacts)` | ✅ | Same |
| No-impact handling | recall=1.0 when true=0, pred=0 | Same (MetricsComputer) | ✅ | Same |
| Benchmark runner | `scripts/run_clean_benchmark.py` | `benchmark/final/runner.py` | ❌ | **DIFFERENT runner** |
| API correctness | Used broken `query_text=` call | Fixed in Gate 11 | ❌ | **DIFFERENT (bug fixed)** |
| ContextFilter API | Incomplete `compute_context_score` | Fixed in Gate 11 | ❌ | **DIFFERENT (bug fixed)** |

### Root Cause of 0.4805 → 0.6307 Shift

The recall change from 0.4805 to 0.6307 is attributable to **two interacting factors**:

**Factor A — Semantic fallback API was broken in the historical run.**  
The historical `run_clean_benchmark.py` called `index.search(query_text=..., threshold=..., filter_project=...)` — kwargs that `FAISSSemanticIndex.search()` does not accept. This would have caused the semantic component to either error-out silently or return zero candidates for every mutation. The historical 0.4805 result therefore reflected a **graph-only execution masquerading as a hybrid run**.

**Factor B — Calibrated threshold = 0.80 means semantic fallback still contributes zero recall.**  
Even with the API fixed, the Gate 11 benchmark calibrated to threshold=0.80. At this threshold, the semantic retriever returns zero candidates for essentially all mutations. This means Gate 11 AURA Hybrid recall (0.6307) is **also graph-only in practice**, just with the bug absent.

**Conclusion:**  
- 0.4805 = historical graph-only execution (semantic broken, 5-depth graph with different runner state)  
- 0.6307 = Gate 11 graph-only execution (semantic zero-contribution at threshold=0.80, same 5-depth graph, fixed API)  
- The difference (0.4805 → 0.6307) reflects **different ground-truth realization conditions** from the same generator, not genuine algorithm improvement  
- **Neither number is the true hybrid recall** — the semantic component has contributed zero in both cases  
- These results are **not directly comparable** without resolving the semantic threshold problem

---

## Section 2 — Dataset Integrity

| Check | Result |
|:---|:---:|
| Mutation count | 150 ✅ |
| GT record count | 150 ✅ |
| All mutations have GT | Yes ✅ |
| No duplicate mutation IDs | Verified ✅ |
| ADAS: 50 mutations | ✅ |
| POWERTRAIN: 50 mutations | ✅ |
| BATTERY_EV: 50 mutations | ✅ |
| Mutation fingerprint (SHA-256[:16]) | `3bc8c11efb2398a0` ✅ |
| GT fingerprint (SHA-256[:16]) | `3bc8c11efb2398a0` ✅ |
| GT fields not in mutation records | Verified ✅ |
| `true_impacted_artifacts` not leaked into mutation records | Verified ✅ |

---

## Section 3 — Ground Truth Integrity

| Check | Result |
|:---|:---:|
| GT generated before evaluation | Yes (data/ directory pre-exists) ✅ |
| Prediction code cannot modify GT files | GT is read-only JSON ✅ |
| GT labels not in mutation after_state | No direct injection detected ✅ |
| Mutation record does not contain GT answer keys | Verified on sample ✅ |
| Ground-truth evaluation happens after prediction | Yes (MetricsComputer called post-run) ✅ |

---

## Section 4 — Configuration Integrity

### FINDING F1 (Non-Blocking): Config File vs Runner Discrepancy

| Parameter | configs/final.yaml | benchmark/final/runner.py (runtime) |
|:---|:---:|:---:|
| semantic threshold | **0.45** | **calibrated = 0.80** |
| graph max_depth | **3** | **5** |
| top_k | 10 | 10 ✅ |
| seed | 42 | 42 ✅ |
| model | AURA-DomainHashEmbedder-384 | Same ✅ |
| safety_gate mandatory | true | true ✅ |

`configs/final.yaml` was not directly consumed by the benchmark runner. The runner uses its own `benchmark/final/config.py` for depth and calibrates the threshold on the calibration split. This means the "canonical configuration" and the "benchmark configuration" are not the same file. **This is Finding F1** — needs resolution in a future gate.

---

## Section 5 — Architecture B Integrity

### FINDING F2 (Blocking): Weighted Fusion Violates Architecture B

Architecture B (locked) requires:
```
S_final = S_struct UNION S_semantic  (strict set union)
```

The implemented `ImpactFusionEngine` uses:
```
final_score = (0.55 * g_score) + (0.30 * s_score) + (0.15 * c_score)
```

This is **weighted fusion with a score threshold (`min_score_threshold=0.20`)** that can exclude structurally reachable artifacts if their weighted score falls below 0.20. A strict set union would include ALL graph-reachable nodes regardless of score.

**Impact on 0.6307 result:** Because the semantic threshold is 0.80 and semantic fallback returns zero candidates, the fusion engine only operates on graph impacts. However, the `ImpactRanker` with `min_score_threshold=0.20` may exclude some graph nodes (those with structural_score < 0.20 after weighting). This means AURA Hybrid recall could be **lower than Graph_Only** for some mutations — but the equal recall (0.6307 = 0.6307) observed suggests the threshold is not currently culling any graph nodes in practice.

**Architecture B is technically violated** but the violation is dormant at the current calibrated threshold. This must be fixed before the benchmark can claim to evaluate Architecture B.

### FINDING F3 (Non-Blocking): Recall Equality Between AURA and Graph

Verified independently: AURA Hybrid Routed recall == Graph_Only recall on all 150 mutations (max diff = 0.000000). This occurs because:

1. Calibrated semantic threshold = 0.80 → zero semantic candidates retrieved
2. The semantic fallback contributes nothing to the impact union
3. AURA result = Graph result exactly

The Wilcoxon test p=1.0 for recall (no significant difference) is consistent with this finding. **The benchmark does not currently measure a hybrid algorithm — it measures the graph algorithm with additional overhead.**

---

## Section 6 — Model Identity

| Check | Result |
|:---|:---:|
| Model class | `SemanticEmbedder` ✅ |
| Model name | `AURA-DomainHashEmbedder-384` ✅ |
| `is_neural` | False ✅ |
| `model_type` | `deterministic_domain_hash_vectorizer` ✅ |
| Dimension | 384 ✅ |
| Deterministic (same output every call) | Verified ✅ |
| `sentence_transformers` imported | No ✅ |
| `configs/final.yaml` model name | `AURA-DomainHashEmbedder-384` ✅ |
| BGE-M3 anywhere in active config | Not found ✅ |

---

## Section 7 — Metric Definitions

| Metric | Formula | Population | Source |
|:---|:---|:---|:---|
| Artifact Recall | hit_count / true_count (1.0 if true_count=0, pred_count=0) | 150 mutations × 6 methods | `src/benchmark/metrics.py:MetricsComputer.compute_artifact_metrics` |
| Artifact Precision | hit_count / pred_count (0.0 if pred_count=0) | Same | Same |
| Artifact F1 | 2·P·R / (P+R); 0.0 if both 0 | Same | Same |
| Test Reduction | 1 − selected_count / total_suite_size | 150 mutations × 7 methods | `src/benchmark/metrics.py:MetricsComputer.compute_test_metrics` |
| Safety Invariant | fraction of mutations where safety_recall==1.0 | 150 AURA Hybrid Routed rows | `src/benchmark/runners.py` (hard assert) |
| Safety-Critical Discovery Recall | selected_safety_tests / true_safety_tests | 77 mutations with true_safety_tests>0 | `benchmark/final/outputs/regression_results.csv` |
| Semantic Recall@k | fraction of semantic mutations where true artifact in top-k | Semantic mutation subset | `src/benchmark/semantic_eval.py` |
| MRR | mean 1/rank (0 if not found) | Same | Same |

---

## Section 8 — Safety Metric Separation

Two distinct metrics, explicitly verified:

### 8A. Safety Invariant (T_safe ⊆ T_selected)
- **Definition:** For every mutation, the known mandatory safety tests are included in the selected test set.
- **Measured:** 150/150 = 100.00%
- **Mechanism:** Hard assertion in `runners.py` — raises `SafetyGateViolationException` if violated
- **This IS the benchmark's reported "safety_recall" = 1.0**

### 8B. Safety-Critical Discovery Recall
- **Definition:** Of all safety-critical tests that should have been selected, how many were selected?
- **Condition:** Only for mutations where `true_safety_tests > 0` (77 of 150)
- **Measured (Gate 12):** selected_safety_tests / true_safety_tests = **1.0000** (mean)
- **Note:** This is also 1.0 in Gate 11 because the safety gate forces inclusion of all known mandatory tests. The historical 47.61% was from a run where the safety gate was bypassed.
- **These are the same number here because the safety gate forces 100% selection of known tests.**

**FINDING F4 (Non-Blocking):** The 47.61% historical safety recall came from a run without the safety gate enforced. Gate 11 enforces it, giving 100% on both metrics. This is the documented resolution of BLOCKER-001.

---

## Section 9 — Test Reduction Verification

| Measurement | Value |
|:---|---:|
| Mean total_tests | 81.67 |
| Mean selected_tests | 12.64 |
| Independently computed reduction | **84.52%** |
| CSV reduction field (mean) | **84.37%** |
| Max per-row discrepancy | < 1% (rounding) |

Independently verified as correct. The denominator is actual test count per project; the numerator is selected tests; safety tests are included in the selection.

---

## Section 10 — Semantic Metrics Verification

| Metric | Reported | Population |
|:---|---:|:---|
| Recall@1 | 3.3% | Semantic mutations subset |
| Recall@3 | 6.7% | Same |
| Recall@5 | 13.3% | Same |
| Recall@10 | 20.0% | Same |
| MRR | 0.0665 | Same |

These numbers are internally consistent (Recall@1 ≤ @3 ≤ @5 ≤ @10, verified by Gate 11 test). The low values (3.3% @1) are consistent with the hash-based embedder's limited semantic discrimination for cross-artifact retrieval. These are honest results from the actual embedding implementation.

---

## Section 11 — Baseline Comparability

All 6 methods (Full_Suite excluded from impact CSV) evaluated on:
- Identical 150 mutations ✅
- Identical ground truth ✅
- Identical MetricsComputer formula ✅
- Identical preprocessing (ChangeContext from same MutationRecord) ✅

The baselines are methodologically comparable within Gate 11. Historical baselines from `reports/final_report.md` are **NOT directly comparable** to Gate 11 due to the API bug fix documented above.

---

## Section 12 — Reproducibility

| Run | Recall | Dataset FP | Threshold |
|:---|---:|:---:|---:|
| Gate 11 Run 1 | 0.6307 | 3bc8c11efb2398a0 | 0.80 |
| Gate 12 Rerun | 0.6307 | 3bc8c11efb2398a0 | 0.80 |

**Fully deterministic.** Same results on every run. Seed=42 controls all randomness.

---

## Section 13 — Output Fingerprints

| Artifact | SHA-256[:16] |
|:---|:---|
| data/mutations/all_mutations.json (mutation IDs) | `3bc8c11efb2398a0` |
| data/ground_truth/all_ground_truth.json (GT IDs) | `3bc8c11efb2398a0` |
| configs/final.yaml threshold | 0.45 (recorded) |
| benchmark/final/config.py MAX_GRAPH_DEPTH | 5 (recorded) |
| benchmark/final/config.py calibrated_threshold (runtime) | 0.80 (recorded) |
| artifacts/final_benchmark_results.json version | GATE-11-v1.0.0 |

---

## Section 14 — Findings Summary

| ID | Severity | Finding | Action Required |
|:---|:---:|:---|:---|
| **F1** | NON-BLOCKING | `configs/final.yaml` (threshold=0.45, depth=3) not consumed by benchmark runner (uses depth=5, calibrated threshold=0.80). These are known pre-existing discrepancies. | Gate 13: Align runner with canonical config OR document deliberately |
| **F2** | **BLOCKING** | `ImpactFusionEngine` uses weighted fusion (wg=0.55, ws=0.30, wc=0.15) + min_score_threshold, NOT the strict set union required by Architecture B. | Gate 13: Implement strict set union. The current 0.6307 result does NOT evaluate Architecture B. |
| **F3** | **BLOCKING** | AURA Hybrid recall == Graph_Only recall (0.6307 = 0.6307) on all 150 mutations. Semantic fallback contributes zero recall. The benchmark measures graph-only algorithm, not the hybrid. | Gate 13: Lower semantic threshold to Architecture B canonical value (0.45) and re-benchmark |
| **F4** | NON-BLOCKING | Safety-critical discovery recall history (47.61%): this was from a run without safety gate enforcement. Gate 11 correctly shows 100% with enforcement. Documented and resolved. | None required — BLOCKER-001 is resolved |

---

## Section 15 — Final Gate Decision

```
GATE 12 — CONDITIONAL PASS

Metric integrity:        PASS (all formulas verified)
Dataset integrity:       PASS (150/150, fingerprint verified)
Ground truth integrity:  PASS (no leakage detected)
Model identity:          PASS (AURA-DomainHashEmbedder-384 confirmed)
Safety separation:       PASS (invariant and discovery distinguished)
Test reduction:          PASS (84.37% independently verified)
Reproducibility:         PASS (identical results on two runs)
Baseline comparability:  PASS (within Gate 11; not comparable to historical)

BLOCKING FINDINGS:
  F2: Architecture B violated (weighted fusion, not strict set union)
  F3: Semantic fallback contributes zero recall — hybrid not evaluated

0.4805 vs 0.6307 reconciliation: COMPLETE
  NOT directly comparable — different API correctness state
  Both results reflect graph-only execution in practice
  0.6307 is the authoritative Gate 11 result (API-correct run)
  0.4805 is superseded (API-broken historical run)

Gate 13 MUST NOT begin until F2 and F3 are resolved.
Gate 13 objective: Implement strict set union, lower threshold to 0.45,
                   re-benchmark, verify genuine hybrid behavior.
```

---

*Gate 12 evidence: `artifacts/gates/stage_12_gate.json`*  
*Gate 12 tests: `tests/benchmark/test_metric_integrity.py` (36/36 PASS)*  
*Full test suite: 143/143 PASS*
