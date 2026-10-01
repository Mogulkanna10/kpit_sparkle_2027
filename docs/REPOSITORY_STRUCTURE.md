# AURA-Impact Repository Structure & Classification Guide

**Project:** AURA-Impact (KPIT Sparkle 2027)  
**Status:** AUTHORITATIVE & FROZEN  
**Auditor:** Antigravity Release & Research Validation Engineering  

---

## 1. Top-Level Directory Taxonomy

This document provides a unambiguous classification of every directory and file in the repository, clearly distinguishing active **Canonical Production** components from **Historical / Experimental** artifacts.

```text
AURA-Impact/
├── src/                  [CANONICAL PRODUCTION SOURCE] Core engine, algorithms, parsers, safety gate
├── configs/              [CANONICAL & HISTORICAL CONFIGS] Production config (final.yaml) + archived configs
├── tests/                [CANONICAL AUTOMATED TESTS] Unit, integration, adversarial, semantic tests
├── data/                 [CANONICAL DATASET] Synthetic vehicle projects (ADAS, Powertrain, Battery_EV)
├── dashboard/            [CANONICAL UI] Streamlit interactive visualization dashboard
├── docs/                 [CANONICAL CONTINUITY DOCS] Architectural specs, status, and reconciliation records
├── artifacts/            [CANONICAL MACHINE-READABLE STATE] Gates, state JSON, and audit trails
├── reports/              [FINAL & HISTORICAL REPORTS] reports/final/ (Canonical) vs v4/v5/v6 (Historical)
├── scripts/              [OPERATIONAL SCRIPTS] Benchmark execution and verification runners
├── baselines/            [BENCHMARK COMPARISONS] Full Suite, Keyword, Embedding, Graph-Only baselines
└── experiments/          [HISTORICAL SWEEPS] Historical experiment runners (v4, v5, scaling)
```

---

## 2. Detailed Classification Matrix

| Directory / Subpath | Classification | Canonical Status | Role / Contents |
|---|---|---|---|
| **`src/api/`** | Production Runtime | **CANONICAL** | `pipeline.py` (Master Orchestrator), `cli.py` (Command-line interface) |
| **`src/graph/`** | Production Runtime | **CANONICAL** | `schema.py` (Graph types), `builder.py` (Graph construction), `traversal.py` (Bounded BFS $k \le 3$), `provenance.py` (Trace provenance) |
| **`src/parsers/`** | Production Runtime | **CANONICAL** | `cpp_parser.py` (C/C++ AST), `arxml_parser.py` (AUTOSAR XML), `requirement_parser.py` (Reqs), `test_parser.py` (Tests) |
| **`src/semantic/`** | Production Runtime | **CANONICAL** | `embedder.py` (`AURA-DomainHashEmbedder-384`), `index.py` (FAISS IP index), `context_filter.py` (Hard context gate), `retriever.py` |
| **`src/impact/`** | Production Runtime | **CANONICAL** | `impact_engine.py` (`TwoStageImpactEngine`), `impact_union.py` (Strict set union), `ranking.py` (Impact ranker), `semantic_fallback.py` |
| **`src/testing/`** | Production Runtime | **CANONICAL** | `safety_gate.py` (Non-bypassable ASIL-C/D gate), `test_mapper.py` (Artifact-test mapping), `regression_selector.py` |
| **`src/evidence/`** | Production Runtime | **CANONICAL** | `evidence_logger.py`, `report_generator.py`, `evidence_model.py` (Auditable traces) |
| **`src/ingestion/`** | Production Runtime | **CANONICAL** | `artifact_loader.py` (Repo scanner), `git_diff.py` (Diff & patch parser) |
| **`src/benchmark/`** | Benchmark Runtime | **CANONICAL** | Ground truth loaders, metrics computation, mutation generation, benchmark runners |
| **`configs/final.yaml`** | Configuration | **CANONICAL (AUTHORITATIVE)** | Single authoritative configuration governing production pipeline |
| **`configs/canonical_architecture.yaml`** | Configuration | **CANONICAL (LOCKED)** | Frozen architecture configuration |
| **`configs/architecture.yaml`** | Configuration | CANONICAL DEFAULT | Synchronized default architecture settings |
| **`configs/semantic.yaml`** | Configuration | CANONICAL DEFAULT | Synchronized default semantic settings |
| **`configs/graph.yaml`** | Configuration | CANONICAL DEFAULT | Synchronized default graph settings |
| **`configs/safety.yaml`** | Configuration | CANONICAL DEFAULT | Synchronized default safety gate settings |
| **`configs/test_selection.yaml`** | Configuration | CANONICAL DEFAULT | Synchronized default test selector settings |
| **`configs/frozen_final.yaml`** | Configuration | HISTORICAL ARCHIVE | Archived v6 experimental benchmark sweep config |
| **`configs/models.yaml`** | Configuration | HISTORICAL ARCHIVE | Archived exploratory model references |
| **`tests/unit/`** | Automated Verification | **CANONICAL** | Parser, graph, semantic, safety gate, regression selector unit tests |
| **`tests/integration/`** | Automated Verification | **CANONICAL** | Two-stage impact engine and pipeline integration tests |
| **`tests/adversarial/`** | Automated Verification | **CANONICAL** | Hostile context filter decoy and stress tests |
| **`tests/semantic/`** | Automated Verification | **CANONICAL** | Model identity, dimension, reproducibility, and index tests |
| **`dashboard/app.py`** | User Interface | **CANONICAL** | Streamlit web application providing interactive visualization |
| **`data/projects/`** | Data / Models | **CANONICAL** | ADAS, Powertrain, Battery_EV, Body_Electronics synthetic AUTOSAR projects |
| **`data/ground_truth/`** | Data / Models | **CANONICAL** | 150 ground truth impact mapping JSON files |
| **`data/mutations/`** | Data / Models | **CANONICAL** | 150 controlled mutation change specifications |
| **`reports/final/`** | Reports & Verification | **CANONICAL** | Gated release verification and audit reports (Stage 0 to Stage 25) |
| **`reports/final_report.md`** | Reports & Verification | HISTORICAL BENCHMARK | Baseline comparison report on 150 mutations |
| **`reports/v4/`, `v5/`, `v6/`** | Reports & Verification | HISTORICAL ARCHIVE | Historical development iteration reports |
| **`experiments/`** | Experimental Sweeps | HISTORICAL ARCHIVE | Ablation, scaling, and historical validation runners |
| **`baselines/`** | Benchmark Baselines | BENCHMARK COMPARATIVE | Full Suite, Keyword, Dense Embedding, Graph-Only implementations |

---

## 3. Developer Guidance: How to Navigate

1. **To run the canonical production pipeline:**
   Use `AuraImpactPipeline` from `src.api.pipeline` configured with `configs/final.yaml`.
2. **To execute automated tests:**
   Run `python -m pytest tests/ -q`.
3. **To launch the interactive dashboard:**
   Run `streamlit run dashboard/app.py`.
4. **To inspect project progress:**
   Read `docs/START_HERE.md` and `docs/PROJECT_STATUS.md`.
