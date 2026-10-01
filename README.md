# AURA-Impact: Context-Aware Change Impact & Regression Intelligence for AUTOSAR Software Integration

[![KPIT Sparkle 2027](https://img.shields.io/badge/KPIT_Sparkle-2027_Submission-0052CC.svg?style=for-the-badge&logo=codeforces&logoColor=white)](#)
[![Status: Research Prototype](https://img.shields.io/badge/Status-Research%20Prototype-orange.svg?style=for-the-badge)](#project-status--maturity-level)
[![Architecture: Locked B](https://img.shields.io/badge/Architecture-Bounded%20Graph%20%2B%20Strict%20Union%20Fallback-008080.svg?style=for-the-badge)](#locked-architecture-architecture-b)
[![Safety Invariant](https://img.shields.io/badge/ISO%2026262-100%25%20Mandatory%20Safety%20Retention-success.svg?style=for-the-badge)](#safety-guarantee--invariant-distinction)
[![Tests Passing](https://img.shields.io/badge/Tests-220%20Passed%20%7C%2026%20Gates%20Verified-brightgreen.svg?style=for-the-badge)](#testing--verification)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

---

## 📌 Project Status & Maturity Level

> [!IMPORTANT]
> **RESEARCH & COMPETITION PROTOTYPE:** AURA-Impact is an academic and research engineering prototype developed for KPIT Sparkle 2027.
> - **Evaluation Dataset:** All benchmarks are evaluated on **synthetic AUTOSAR models and controlled mutations** (150 mutations across ADAS, Powertrain, and Battery EV domains).
> - **Production Scope:** This system is **not** currently certified by any automotive OEM or Tier-1 supplier, nor is it connected to live vehicle hardware-in-the-loop (HIL) test rigs.
> - **Zero Hallucination Policy:** All metrics, models, and test results in this repository are verified by executable tests and reproducible scripts.

---

## 📖 Executive Summary

Modern Software-Defined Vehicles (SDVs) integrate millions of lines of C/C++ code, thousands of AUTOSAR XML (`ARXML`) software components (SWCs), complex runtime environment (`RTE`) port mappings, and strict functional safety constraints ([ISO 26262](https://www.iso.org/standard/68383.html)). In multi-tier automotive development (OEM ↔ Tier-1 ↔ Tier-2), minor modifications—such as an interface signature change in a low-level device driver or a subtle timing semantic alteration—trigger multi-day continuous integration cycles, broad unfocused regression suites, and high risk of escaped integration defects.

**AURA-Impact** investigates a hybrid, explainable change-impact analysis engine designed specifically for AUTOSAR architectures:
1. **Deterministic Graph Traversal:** Extracts high-fidelity structural relationships from ARXML, C/C++ headers/sources, and requirement specifications, performing bounded breadth-first propagation ($D \le 3$).
2. **Context-Constrained Semantic Fallback:** Employs domain-specific embedding representations filtered by strict automotive attributes (ECU boundaries, function clusters, ASIL levels) to recover *hidden semantic dependencies* that pure AST/graph parsers miss.
3. **Strict Set Union ($S_{final} = S_{struct} \cup S_{semantic}$):** Under Architecture B, semantic candidates are retained alongside structural impacts without numerical attenuation.
4. **Non-Bypassable ASIL Safety Gate:** Ensures mandatory retention of all ASIL-C/D safety-critical test cases regardless of ranking heuristics or threshold cutoffs.
5. **Actionable Engineering Evidence:** Generates cryptographically auditable JSON traces explaining exactly *why* every artifact and test case was selected.

---

## 🏛️ Locked Architecture (Architecture B)

```
                         GIT / FILE CHANGE
                                │
                                ▼
                       PARSER + INGESTION
                       /               \
                      /                 \
         +-----------------------+   +-------------------------------+
         |  Heterogeneous AST    |   | Domain Hash Embedder          |
         |  & ARXML Graph Builder|   | (AURA-DomainHashEmbedder-384) |
         +-----------+-----------+   +---------------+---------------+
                     │                               │
                     ▼                               ▼
         +-----------------------+   +-------------------------------+
         | Stage 1: Deterministic|   | Stage 2: Context-Constrained  |
         | Bounded Traversal     |   | Semantic Retrieval            |
         | (Depth <= 3, BFS)     |   | (Hard Subsystem Filter, >0.45)|
         +-----------+-----------+   +---------------+---------------+
                     │                               │
                     └───────────────┬───────────────┘
                                     │
                                     ▼
                       +---------------------------+
                       |    Strict Set Union       |
                       | S_final = S_struct ∪ S_sem|
                       +-------------+-------------+
                                     │
                                     ▼
                       +---------------------------+
                       | Deterministic Test Mapper |
                       | (Artifact -> Test Suite)  |
                       +-------------+-------------+
                                     │
                                     ▼
                       +---------------------------+
                       | Non-Bypassable Safety Gate|
                       | (Mandatory ASIL-C/D Added)|
                       +-------------+-------------+
                                     │
                                     ▼
                       +---------------------------+
                       | Ranked Regression Suite   |
                       | + JSON Evidence Audit Log |
                       +---------------------------+
```

### Core Architecture Invariants
* **Graph Priority:** Structural propagation is deterministic, fast (<1 ms query), and zero-hallucination.
* **Context Constraints:** Semantic retrieval rejects cross-subsystem decoys and incompatible artifact pairs, preventing false positive explosions.
* **Strict Set Union:** The impact union preserves both structural and semantic detections ($S_{final} = S_{struct} \cup S_{semantic}$) without lossy weighting.
* **Safety Invariant ($T_{safe} \subseteq T_{selected}$):** All known safety-critical tests are guaranteed to be in the final execution suite.

---

## 🔬 Semantic Model Specification

The canonical semantic model employed across all benchmarks and pipelines is:
- **Identifier:** `AURA-DomainHashEmbedder-384`
- **Embedding Dimension:** 384
- **Algorithm:** Deterministic domain-specific feature hashing with automotive ontology expansion, subword tokenization, and L2 unit normalization.
- **Indexing Backend:** FAISS (or NumPy cosine similarity fallback when FAISS C-extensions are unavailable).
- **Execution:** Zero external API calls, zero neural GPU requirements, 100% deterministic vector generation.

*(Note: Prior draft documentation informally referred to this component as "BGE-M3". That label was inaccurate and has been formally deprecated. The actual executable implementation is the deterministic domain-hash vectorizer.)*

---

## 📊 Canonical Benchmark Results (150 Mutations)

The canonical benchmark was reconstructed, validated, and verified across two independent clean runs (`benchmark/final/runner.py` with `configs/final.yaml`, canonical threshold `0.45`, random seed `42`):

| Evaluation Dimension | Graph-Only Baseline | AURA Hybrid (Architecture B) | Delta / Improvement |
| :--- | :---: | :---: | :---: |
| **Headline Artifact Recall** | 0.6307 (63.07%) | **0.6311 (63.11%)** | **+0.0004 (+0.04%)** |
| **Average Test Suite Reduction** | 82.29% | **82.29%** | Optimal test suite size |
| **Safety Invariant Enforcement** | 100.0% (150/150) | **100.0% (150/150)** | Zero safety violations |
| **Reproducibility Hash Match** | N/A | **100% Bit-for-Bit Identical** | Fully deterministic |
| **Benchmark Execution Time** | ~11.0 s | **11.37 s** | ~75 ms per mutation |

---

## 🛡️ Safety Guarantee & Invariant Distinction

To maintain strict scientific integrity, AURA-Impact distinguishes between two safety metrics:

1. **Safety Invariant Enforcement ($T_{safe} \subseteq T_{selected}$): 100.0% (150/150).**
   - Implemented in `src/testing/safety_gate.py`.
   - Guaranteed by post-selection invariant checking: any mandatory ASIL-C/D test omitted by algorithmic heuristics is forced back into the selected suite.
2. **Autonomous Safety Discovery Recall: 47.61% (without safety gate).**
   - Measures what percentage of safety-critical items the structural and semantic impact engines identify purely through graph walking and embedding retrieval without forced inclusion.
   - The safety gate exists precisely to bridge this gap, ensuring that safe automotive CI never relies solely on statistical or heuristic discovery.

---

## 📂 Repository Structure

```
KPIT_2026_aura_impact/
├── src/                               # Core Pipeline Implementation
│   ├── api/                           # CLI and high-level pipeline entrypoints
│   ├── benchmark/                     # Benchmark generators, metrics, statistics
│   ├── evidence/                      # Audit logging and multi-format report generator
│   ├── graph/                         # Engineering graph builder, schema, traversal
│   ├── impact/                        # Impact fusion, classification, fallback, ranking
│   ├── ingestion/                     # Git diff analyzer and artifact loader
│   ├── parsers/                       # C/C++, ARXML, Requirement, Test spec parsers
│   ├── semantic/                      # Domain hash embedder, FAISS index, context filter
│   └── testing/                       # Test mapper, regression selector, safety gate
├── configs/                           # Canonical Configuration YAMLs
│   └── final.yaml                     # Authoritative benchmark configuration (thresh=0.45)
├── data/synthetic/                    # Synthetic Automotive Benchmarks (ADAS, Powertrain, EV)
├── dashboard/                         # Streamlit Interactive Explorer (dashboard/app.py)
├── benchmark/final/                   # Canonical Final Benchmark Runner & Config
├── reports/final/                     # Comprehensive Forensic Audit & Gate Reports
├── artifacts/gates/                   # Formal Gate Decision JSONs (stage_0 through stage_25)
├── tests/                             # Comprehensive 220-Test Regression Suite
│   ├── benchmark/                     # Final benchmark, metric integrity, leakage, repro
│   ├── cli/                           # Subprocess CLI integration tests
│   ├── dashboard/                     # Dashboard programmatic validation tests
│   ├── evidence/                      # Audit logging completeness tests
│   ├── failure_injection/             # 20 Hostile failure injection tests
│   ├── integration/                   # End-to-end pipeline tests
│   ├── safety/                        # Safety gate invariant and hardening tests
│   ├── semantic/                      # Model identity and fallback validation tests
│   ├── structural/                    # Graph propagation and boundary tests
│   ├── testing/                       # Regression selection tests
│   └── unit/                          # Unit tests across parsers, graph, ranking, classifier
├── .github/workflows/                 # Continuous Integration Pipeline (aura-impact.yml)
├── pyproject.toml                     # Modern Python packaging configuration
└── requirements.txt                   # Dependency specifications
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10, 3.11, 3.12, or 3.14
- Git

### 2. Clone & Install
```bash
git clone https://github.com/yuvanchandar-arch/KPIT_2026_aura_impact.git
cd KPIT_2026_aura_impact
pip install -r requirements.txt
```

### 3. Run Automated Tests
```bash
python -m pytest tests/ -v
```
*Executes the complete 220-test regression and validation suite.*

### 4. Run Canonical Benchmark
```bash
python benchmark/final/runner.py
```
*Executes the 150-mutation evaluation using canonical configuration `configs/final.yaml`.*

### 5. Launch the Interactive Exploration Dashboard
```bash
streamlit run dashboard/app.py
```
*Opens the web-based visualizer for inspecting graph structures, change propagation paths, and safety justifications.*

---

## 🏆 KPIT Sparkle 2027 Submission Details

- **Project Title:** AURA-Impact (Automotive Unified Regression & Architecture Impact Intelligence)
- **Domain:** Software-Defined Vehicles (SDV), AUTOSAR Integration, ISO 26262 Functional Safety, Regression Test Selection.
- **Innovation:** Bounded Heterogeneous Graph Traversal combined with Context-Constrained Semantic Fallback and Mandatory Safety Invariant Enforcement.
