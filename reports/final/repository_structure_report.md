# Gate 5: Repository Structure and Code Path Cleanup Report

**Project:** AURA-Impact (KPIT Sparkle 2027)  
**Execution Timestamp:** 2026-09-29T22:36:00+05:30  
**Status:** PASS  
**Auditor:** Antigravity Release & Research Validation Engineering  

---

## 1. Objective

The objective of Gate 5 is to perform reference and import analysis across all repository code paths, eliminate ambiguity between multiple generations of experimental code and the active canonical runtime, and establish an authoritative navigation guide (`docs/REPOSITORY_STRUCTURE.md`).

---

## 2. Dependency & Reference Analysis Results

1. **`src/` Independence:**
   - Grep analysis confirmed that `src/` has **zero** dependencies on `experiments/`.
   - `src/benchmark/runners.py` references `baselines/` exclusively for comparative baseline benchmarking (Full Suite, Keyword, Embedding, Graph-Only).
2. **`tests/` Independence:**
   - Grep analysis confirmed that the test suite has **zero** imports from `experiments/`.
3. **`scripts/` References:**
   - `scripts/run_benchmark.py` invokes `experiments.run_all.main` for historical benchmark re-execution.
   - Preserved `experiments/` in place with explicit historical labeling in `docs/REPOSITORY_STRUCTURE.md` to prevent breaking existing CLI scripts while completely isolating the canonical pipeline.

---

## 3. Directory Classification Summary

- **Canonical Production Code:** `src/api/`, `src/graph/`, `src/parsers/`, `src/semantic/`, `src/impact/`, `src/testing/`, `src/evidence/`, `src/ingestion/`
- **Canonical Configuration:** `configs/final.yaml`, `configs/canonical_architecture.yaml`
- **Canonical Tests:** `tests/unit/`, `tests/integration/`, `tests/adversarial/`, `tests/semantic/`
- **Canonical Data:** `data/projects/`, `data/ground_truth/`, `data/mutations/`
- **Canonical UI:** `dashboard/app.py`
- **Canonical Reports:** `reports/final/`
- **Historical Archives:** `experiments/`, `reports/v4/`, `reports/v5/`, `reports/v6/`, `reports/hidden_semantic/`, `configs/frozen_final.yaml`, `configs/models.yaml`

---

## 4. Gate 5 Pass Checklist

| Checklist Item | Status | Evidence |
|---|---|---|
| Import/reference analysis executed | PASS | Zero unapproved dependencies on historical scripts |
| Canonical vs Historical taxonomy established | PASS | Detailed classification matrix in `docs/REPOSITORY_STRUCTURE.md` |
| No historical evidence deleted | PASS | All historical benchmarks and sweep reports preserved |
| No canonical runtime files broken | PASS | 36/36 tests continue to pass |
| New engineer navigation clarity achieved | PASS | Guide covers every directory and file path |

**GATE 5 RESULT: PASS**
