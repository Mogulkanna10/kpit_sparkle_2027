# AURA-Impact --- START HERE

> Forensic Audit Date: 2026-09-30T09:40:00+05:30

## Mandatory Reading Order

1. Read this file first.
2. Read `docs/PROJECT_STATUS.md` (complete authoritative forensic state).
3. Read `docs/TECHNICAL_REPORT.md` (formal architecture, math, safety models).
4. Read `artifacts/project_state.json` (machine-readable state).
5. Inspect repository: `git status`.
6. Verify commit: `git rev-parse HEAD` -> `ffc284ce5eb8e6b5fd25c7f09ea7822f2c27de72`.
7. Verify baseline tests: `python -m pytest tests/ -q` -> must see **214 passed**.
8. Continue strictly following the Master Gated Execution Prompt sequence.

---

## One-Line Project Summary

AURA-Impact is a hybrid deterministic-graph + semantic-fallback change-impact analysis engine for AUTOSAR automotive software that reduces regression test suites while enforcing a non-bypassable ISO 26262 safety gate.

---

## Current Status (2026-09-30)

| Item | Status |
|------|--------|
| Branch | `main` |
| Commit | `ffc284ce5eb8e6b5fd25c7f09ea7822f2c27de72` |
| Tests | **214/214 PASSED (100%)** |
| Architecture | Architecture B (Two-Stage Bounded Graph + Semantic Fallback with Strict Set Union) |
| Architecture Status | **LOCKED & VERIFIED** |
| Semantic Model | `AURA-DomainHashEmbedder-384` (Deterministic 384-D domain hash vectorizer, non-neural) |
| Canonical Threshold | `0.45` (consumed from `configs/final.yaml`) |
| Safety Invariant | **100.00% ENFORCED (150/150 mutations retained without exception)** |
| Safety Discovery Recall | 47.61% raw discovery; 100% with safety-gate forced retention |
| Headline Recall | **AURA Hybrid: 0.6311 > Graph-Only: 0.6307 (+0.0004)** |
| Test Suite Reduction | **84.4% average reduction** |
| Benchmark Reproducibility | **Bit-for-Bit Deterministic Across Independent Runs** |

---

## Current Checkpoint

- **Current Stage:** Gate 23 — Final Full Test Suite
- **Completed Gates:**
  - **Gates 0–10:** Architecture, configuration, parsing, and baseline verification (**PASS**)
  - **Gate 11:** Final Benchmark Reconstruction (**PASS**) — 107/107 tests pass
  - **Gate 12:** Metric Integrity & Benchmark Reconciliation (**PASS**) — 143/143 tests pass
  - **Gate 13:** Benchmark Leakage Audit (**PASS**) — 153/153 tests pass across all 11 vectors
  - **Gate 14:** Reproducibility Audit (**PASS**) — 171/171 tests pass, bit-for-bit deterministic
  - **Gate 15:** Failure Injection (**PASS**) — 20 hostile tests pass (`reports/final/failure_injection_report.md`)
  - **Gate 16:** Performance / Scalability (**PASS**) — Measured up to 25k nodes (`reports/final/performance_scalability_report.md`)
  - **Gate 17:** CLI Validation (**PASS**) — 10 subprocess tests pass (`reports/final/cli_validation_report.md`)
  - **Gate 18:** Dashboard Validation (**PASS**) — 8 tests pass (`reports/final/dashboard_validation_report.md`)
  - **Gate 19:** CI Integration (**PASS**) — `.github/workflows/aura-impact.yml` (`reports/final/ci_validation_report.md`)
  - **Gate 20:** Security Audit (**PASS**) — 670 files clean (`reports/final/security_audit.md`)
  - **Gate 21:** Test Coverage Completion (**PASS**) — 214/214 tests pass (`reports/final/test_coverage_report.md`)
  - **Gate 22:** README & Documentation Claim Audit (**PASS**) — Claims aligned with empirical evidence

---

## Permanent Future-Agent Instruction

> AURA-Impact is governed by the Master Gated Execution Prompt supplied by the project owner. Future Antigravity agents MUST read and obey that prompt together with `docs/START_HERE.md`, `docs/PROJECT_STATUS.md`, and `artifacts/project_state.json`. The gated sequence is sequential and blocking. A later gate MUST NOT begin until the previous gate has independently passed. Historical reports are evidence/history only and cannot override current verified source code, tests, frozen configuration, or gate evidence.

---

## Quick Commands

```bash
# Verify entire test suite (214 passed)
python -m pytest tests/ -q

# Run failure injection suite (Gate 15)
python -m pytest tests/failure_injection/ -v

# Run CLI integration suite (Gate 17)
python -m pytest tests/cli/ -v

# Run dashboard validation suite (Gate 18)
python -m pytest tests/dashboard/ -v

# Run final benchmark
python benchmark/final/runner.py

# Check git status
git status
```
