# AURA-Impact — Gate 14: Reproducibility Audit Report
**Gate:** GATE-14  
**Status:** PASS  
**Timestamp:** 2026-09-30T09:02:29+05:30  
**Python version:** 3.14.0  
**Git commit:** ffc284ce5eb8e6b5fd25c7f09ea7822f2c27de72  
**Seed:** 42  

---

## 1. Objective

Verify that the canonical benchmark produces **bit-for-bit deterministic outputs**
under two independent, sequential executions with identical configuration.

---

## 2. Configuration Lock

| Parameter | Value |
|:---|:---|
| Canonical threshold | 0.45 (from configs/final.yaml) |
| Union mode | strict_union |
| Model | AURA-DomainHashEmbedder-384 |
| Embedding dimension | 384 |
| Seed | 42 |
| N mutations | 150 |
| Dataset fingerprint | 3bc8c11efb2398a0 |

---

## 3. Determinism Verification Results

| Check | Run 1 | Run 2 | Match |
|:---|:---|:---|:---:|
| Dataset fingerprint | 3bc8c11efb2398a0 | 3bc8c11efb2398a0 | MATCH |
| Canonical threshold | 0.45 | 0.45 | MATCH |
| impact_results.csv hash | 384fd78b...a2b98 | 384fd78b...a2b98 | MATCH |
| regression_results.csv hash | (identical) | (identical) | MATCH |
| AURA Hybrid recall | 0.6311 | 0.6311 | MATCH |
| Graph-Only recall | 0.6307 | 0.6307 | MATCH |
| Safety pass_count | 150/150 | 150/150 | MATCH |

> **Note:** CSV hashes are computed excluding wall-clock timing columns
> (latency_ms, latency_ms_mean) which vary by definition. All data
> columns (recall, precision, F1, predicted/true/hit counts, etc.) are
> deterministically identical.

---

## 4. Headline Metrics (Both Runs)

| Metric | Value |
|:---|---:|
| AURA Hybrid Recall | **0.6311** |
| Graph-Only Recall | 0.6307 |
| Delta (AURA - Graph) | **+0.0004** |
| AURA > Graph | YES |
| Test Suite Reduction | ~82.3% |
| Safety Invariant | 150/150 = 100.00% PASS |

---

## 5. Architecture B Confirmed

- **Fusion mode:** strict_union (S_final = S_struct UNION S_semantic)
- **Threshold:** 0.45 (canonical, from configs/final.yaml)
- **Result:** AURA Hybrid (0.6311) > Graph-Only (0.6307), confirming semantic
  fallback adds genuine recall improvement under Architecture B.

---

## 6. Test Suite

Gate 14 test file: 	ests/benchmark/test_reproducibility.py (18 tests)  
Full regression suite: **171/171 passed**

| Test | Description | Status |
|:---|:---|:---:|
| TEST 1 | Run metadata consistency | PASS |
| TEST 2 | Dataset fingerprint equality | PASS |
| TEST 3 | Ground-truth fingerprint equality | PASS |
| TEST 4 | Configuration fingerprint equality | PASS |
| TEST 5 | Runner version equality (GATE-14-v2.0.0) | PASS |
| TEST 6 | Model identity equality | PASS |
| TEST 7 | Seed equality | PASS |
| TEST 8 | Impact result equality | PASS |
| TEST 9 | Regression result equality | PASS |
| TEST 10 | Safety invariant equality | PASS |
| TEST 11 | Safety recall equality (1.0) | PASS |
| TEST 12 | Semantic metric equality | PASS |
| TEST 13 | Evidence (Wilcoxon W/p) equality | PASS |
| TEST 14 | Output hash equality | PASS |
| TEST 15 | No uncontrolled randomness | PASS |
| TEST 16 | Deterministic ordering (ADAS_M01_01 first) | PASS |
| TEST 17 | FAISS/NumPy backend consistency | PASS |
| TEST 18 | Full benchmark reproducibility | PASS |

---

## 7. Gate Verdict

`
REPRODUCIBILITY:         PASS (7/7 determinism checks)
AURA vs GRAPH:           AURA 0.6311 > Graph 0.6307 (+0.0004)
SAFETY INVARIANT:        PASS (150/150, 100.00%)
ARCHITECTURE:            B (strict_union, threshold=0.45)
TEST SUITE:              171/171 PASSING
GATE STATUS:             PASS
`

*Report generated: 2026-09-30T09:02:29+05:30*
