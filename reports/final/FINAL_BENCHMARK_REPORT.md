# AURA-Impact — Gate 11: Final Benchmark Report
**Version:** GATE-14-v2.0.0  
**Timestamp:** 2026-09-30T04:47:36.756671+00:00  
**PRNG Seed:** 42  
**Dataset Fingerprint (SHA-256[:16]):** `3bc8c11efb2398a0`  
**Mutations:** 150 (Calibration=30, Validation=30, Test=90)  
**Projects:** ADAS, POWERTRAIN, BATTERY_EV  

---

## 1. Headline Results

| Metric | Graph-Only Baseline | Embedding+Context | **AURA Hybrid Routed** | Δ vs Graph |
|:---|---:|---:|---:|---:|
| Artifact Recall | 0.6307 | 0.4336 | **0.6311** | ++0.0004 |
| Artifact Precision | 0.5443 | 0.4117 | **0.5492** | ++0.0050 |
| Artifact F1-Score | 0.4557 | 0.2667 | **0.5503** | ++0.0946 |
| Test Suite Reduction | — | — | **82.29%** | — |
| Test Recall | — | — | **0.9007** | — |
| **Safety Test Recall** | **100.00%** | **100.00%** | **100.00%** | Invariant |

---

## 2. Safety Gate Invariant (T_safe ⊆ T_selected)

- **Status:** ✅ PASS
- Safety-critical mutations with 100% recall: **150 / 150**
- Safety pass rate: **100.00%**
- Any violation would have raised `SafetyInvariantViolationError` and aborted execution.

---

## 3. Semantic Retrieval Performance

| k | Recall@k |
|:---|---:|
| 1 | 3.33% |
| 3 | 6.67% |
| 5 | 13.33% |
| 10 | 20.00% |
| MRR | 0.0665 |

---

## 4. Context Ablation

| Variant | Mean F1 |
|:---|---:|
| Embedding_Only (Raw) | 0.0133 |
| Embedding + Soft Context | 0.0170 |
| Embedding + Hard Filter + Soft Rank | 0.0170 |

---

## 5. Statistical Significance (Paired Wilcoxon Signed-Rank, Bonferroni α=0.0125)

| Test | W-statistic | p-value | Significant? |
|:---|---:|---:|:---:|
| Recall (Hybrid vs Graph) | 5513.0 | 7.4800e-01 | ❌ No |
| Precision (Hybrid vs Graph) | 981.0 | 8.5248e-01 | ❌ No |

---

## 6. Scalability

| Nodes | Graph Build (ms) | Query (ms) | Peak Mem (MB) |
|---:|---:|---:|---:|
| 100 | 4.36 | 1.461 | 0.15 |
| 500 | 22.42 | 0.625 | 0.76 |
| 1,000 | 31.60 | 0.616 | 1.53 |
| 5,000 | 155.17 | 0.603 | 7.53 |
| 10,000 | 355.71 | 0.620 | 15.07 |
| 25,000 | 943.12 | 0.942 | 39.39 |

---

## 7. Method Summary Table

| Method | Recall μ | Recall σ | Precision μ | Precision σ | F1 μ | F1 σ | Latency (ms) |
|:---|---:|---:|---:|---:|---:|---:|---:|
| Embedding_Context | 0.4336 | 0.4541 | 0.4117 | 0.3864 | 0.2667 | 0.3352 | 1.504 |
| Embedding_Only | 0.4245 | 0.4589 | 0.6678 | 0.4277 | 0.3114 | 0.3847 | 0.392 |
| Graph_Only | 0.6307 | 0.3272 | 0.5443 | 0.3649 | 0.4557 | 0.3444 | 0.208 |
| Hybrid_AURA_Fixed | 0.6322 | 0.3256 | 0.3390 | 0.2954 | 0.3731 | 0.2947 | 1.863 |
| Hybrid_AURA_Routed | 0.6311 | 0.3265 | 0.5492 | 0.3600 | 0.5503 | 0.3467 | 0.790 |
| Keyword | 0.4282 | 0.4560 | 0.1897 | 0.1655 | 0.1485 | 0.1671 | 0.987 |

---

## 8. Reproducibility Checklist

- [x] PRNG seed frozen to `42` (dataset + splits + runner)
- [x] Dataset fingerprint recorded: `3bc8c11efb2398a0`
- [x] Calibration split strictly isolated (no leakage into test)
- [x] Safety gate enforced on all 150 mutations × 7 methods
- [x] All CSVs saved to `benchmark/final/outputs/`
- [x] Gate artifact: `artifacts/gates/stage_14_gate.json`

---

## 9. Gate 11 Verdict

```
BENCHMARK VALIDITY:        PASS
SAFETY INVARIANT:          PASS (150/150)
GROUND-TRUTH INTEGRITY:    PASS (Bounded k=5)
DATA LEAKAGE:              PASS (0 leaks, calibration isolated)
STATISTICAL SIGNIFICANCE:  Recall sig=False, Precision sig=False
ARCHITECTURE VERDICT:      B — Graph + Context-Constrained Semantic Fallback
GATE STATUS:               PASS ✅
```

*Run duration: 3.5 s*
