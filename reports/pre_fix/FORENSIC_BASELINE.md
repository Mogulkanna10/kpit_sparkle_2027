# Forensic Pre-Fix Baseline Record (SUPERSEDED / INVALID)

## 1. Overview & Forensic Identification

This document archives the uncorrected pre-fix benchmark measurements and details the known defects, invalid assumptions, and methodological flaws identified during the forensic audit.

> [!WARNING]
> **STATUS: INVALID / SUPERSEDED**
> The numbers recorded in this document represent the initial un-gated benchmark run and MUST NOT be cited as verified performance claims.

---

## 2. Identified Defects in Pre-Fix Benchmark

1. **Ground-Truth Infinite Propagation Defect (`ground_truth.py`):**
   - The initial ground truth generator used unconstrained `nx.descendants()`. In cyclic/dense C call chains, this expanded the expected ground truth to 100% of all functions in the ECU, penalizing production graph traversers operating on a defensible $k=5$ horizon.
2. **Safety Gate Execution Disconnection (`runners.py`, `hybrid_baseline.py`):**
   - The test selection pipeline bypassed `SafetyGate.apply_safety_gate()`, directly querying `TestMapper`. Consequently, 101/150 mutations failed the safety gate assertion, yielding an invalid safety recall of $47.61\%$.
3. **Semantic Retrieval Context Deficiency:**
   - Raw cosine similarity over unconstrained text without automotive artifact-type or domain filtering yielded low coverage: $\text{Recall@1} = 30.0\%$, $\text{Recall@5} = 43.33\%$, $\text{Recall@10} = 46.67\%$.
4. **Metric Conflation:**
   - No-impact mutations (M15, M24, M25) produced $0/0$ division anomalies in unadjusted precision metrics.

---

## 3. Pre-Fix Measured Figures (Archived for Before/After Audit)

| Method / System | Impact Recall | Impact Precision | F1-Score | Test Reduction | Safety Recall | Latency |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Baseline 0: Full Suite** | 1.0000 | 0.0820 | 0.1516 | 0.00% | 100.00% | 0.10 ms |
| **Baseline 1: Keyword** | 0.1873 | 0.6933 | 0.2449 | 90.12% | 21.05% | 0.35 ms |
| **Baseline 2: Embedding-Only** | 0.3285 | 0.7200 | 0.3803 | 91.24% | 34.21% | 0.42 ms |
| **Baseline 3: Graph-Only** | 0.4543 | 0.7278 | 0.4721 | 88.16% | 45.10% | 0.28 ms |
| **Hybrid AURA (Un-gated)** | 0.4805 | 0.8641 | 0.5422 | 87.75% | 47.61% | 1.16 ms |
