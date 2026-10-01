# AURA-Impact: Round 2 Submission Visual Evidence & Technical Details Package

**Directory:** `round2_submission/technical_details/`  
**Target:** KPIT Sparkle Round 2 Submission Presentation (PPT)  
**System Identity:** AURA-Impact (Context-Aware Change Impact and Regression Intelligence for AUTOSAR Software Integration)  
**Architecture Freeze:** Architecture B Canonical Release

---

## 1. Directory Structure & Asset Index

```
round2_submission/technical_details/
├── source_data/
│   └── source_manifest.json          # Complete data provenance and audit trail
├── charts/
│   ├── artifact_f1_comparison.png/.svg       # Bar chart comparing Artifact F1 across all 4 methods
│   ├── recall_precision_comparison.png/.svg  # Grouped bar chart: Recall vs Precision
│   ├── regression_reduction.png/.svg         # Regression suite reduction (100% -> 17.71%, 82.29% avoided)
│   ├── safety_invariant.png/.svg             # Euler diagram & metrics: T_safe ⊆ T_selected (150/150)
│   └── latency_comparison.png/.svg           # Mean execution latency (0.79 ms canonical benchmark)
├── architecture/
│   └── architecture_detailed.png/.svg        # Complete 5-layer canonical Architecture B diagram
├── research/
│   ├── research_pipeline.png/.svg            # 10-step research methodology flowchart
│   ├── structure_vs_semantics.png/.svg       # "Why AURA Needs Both Structure and Semantics"
│   ├── context_filtering.png/.svg            # Architectural Context Filter Gate candidate evaluation
│   └── research_validation_timeline.png/.svg # 11-step Research -> Validation -> Prototype timeline
├── prototype/
│   └── end_to_end_workflow.png/.svg          # Working demonstrator workflow with live audit panel
├── tables/
│   ├── benchmark_summary.csv/.png            # Formatted benchmark comparison table
│   └── system_outcomes.csv                   # Comprehensive system verification outcomes
├── reports/
│   ├── AURA_IMPACT_TECHNICAL_DETAILS_REPORT.md # 16-section comprehensive technical details report
│   └── AURA_IMPACT_EVIDENCE_SUMMARY.md       # Executive evidence summary answering the 6 key questions
├── technical_details_master.png              # 16:9 Master composite slide visual (1920x1080)
├── technical_details_master.svg              # Scalable vector master composite visual
└── README.md                                 # This document
```

---

## 2. PPT Slide Mapping & Recommended Chart Usage

| Asset File | Intended PPT Slide | Recommended Visual Role |
|:---|:---|:---|
| **`technical_details_master.png`** | **Slide: Technical Details & Reports (Master Slide)** | Drop-in ready 16:9 composite visual containing the full story: architecture, F1 comparison, safety invariant, and validated results summary. |
| **`architecture/architecture_detailed.svg`** | **Slide: Proposed System Architecture** | Primary visual showing the 5 architectural layers, two analysis paths, context gate, and safety gate. |
| **`charts/artifact_f1_comparison.svg`** | **Slide: Research Results & Benchmarks** | Clear bar chart proving AURA-Impact achieves the highest F1 score (0.5503) against Graph, Embedding, and Keyword baselines. |
| **`charts/regression_reduction.svg`** | **Slide: Engineering Value & Impact** | Demonstrates the 82.29% reduction in regression suite execution time with 100% safety test retention. |
| **`charts/safety_invariant.svg`** | **Slide: ISO 26262 Safety Compliance** | Formal Euler set visual showing that safety tests are a strict, non-bypassable subset of selected tests ($T_{safe} \subseteq T_{selected}$). |
| **`research/structure_vs_semantics.svg`** | **Slide: Core Innovation / Problem Statement** | Side-by-side contrast explaining graph blindness on missing edges and how contextual semantic recovery bridges the gap. |
| **`research/context_filtering.svg`** | **Slide: Semantic Intelligence & AI Control** | Visual evidence of how architectural context constraints (subsystem, ECU, interface) eliminate semantic hallucinations and decoys. |
| **`prototype/end_to_end_workflow.svg`** | **Slide: Working Demonstrator / Live Demo** | Shows the practical engineering user journey from Git change to automated test queue with live audit evidence. |
| **`research/research_validation_timeline.svg`**| **Slide: Research Rigor & Methodology** | Proves the exhaustive experimental progression across 11 audit stages from hypothesis to release. |

---

## 3. Canonical Benchmark Metrics (Authoritative Source of Truth)

Every visual asset in this package is strictly grounded in the authoritative release results (`benchmark/final/outputs/summary_table.csv` and `artifacts/final_benchmark_results.json`):

* **AURA-Impact:**
  - Artifact Recall: **63.11%**
  - Artifact Precision: **54.92%**
  - Artifact F1: **0.5503**
  - Test Suite Recall: **90.07%**
  - Test Suite Reduction: **82.29%**
  - Safety Invariant: **100.0% (150/150)**
  - Mean Latency: **0.79 ms**
* **Graph-Only Baseline:**
  - Artifact Recall: **63.07%**
  - Artifact Precision: **54.43%**
  - Artifact F1: **0.4557**
  - Safety Invariant: **98.67% (Fails safety compliance)**
* **Embedding-Only Baseline:**
  - Artifact Recall: **42.45%**
  - Artifact Precision: **66.78%**
  - Artifact F1: **0.3114**
* **Keyword Match Baseline:**
  - Artifact Recall: **42.82%**
  - Artifact Precision: **18.97%**
  - Artifact F1: **0.1485**
* **Validation Rigor:**
  - **220** baseline automated tests passed (now **252** with Round 2 demonstrator tests).
  - **26 / 26** formal validation gates passed (`stage_0_gate.json` through `stage_25_gate.json`).

---

## 4. Benchmark vs. Prototype Distinction (Scientific Honesty)

To ensure total transparency before the judges:
1. **Canonical Research Benchmark Results:**
   - Generated over 150 automated mutation batches across ADAS, Powertrain, and Battery EV topologies.
   - Measures vectorized, in-memory execution latency (**0.79 ms**).
   - Validates statistical macro-metrics (Recall: 63.11%, Precision: 54.92%, F1: 0.5503).
2. **Live Engineering Demonstrator Results:**
   - Executes live end-to-end processing of `.arxml` files, C sources, and a 100-test verification suite.
   - Measured live latency averages **5.34 ms** (including cold disk I/O and text parsing).
   - Evaluates concrete single-change scenarios (e.g., Scenario 2 recovering unlinked radar fusion in 0.31 ms).

*Note: These datasets and contexts are physically separated in the repository and explicitly labeled.*

---

## 5. Visual Hierarchy & Design Guidelines

All visual assets follow strict automotive research presentation standards:
- **Clean Background:** 100% white / neutral slate backgrounds for seamless PPT slide integration.
- **Color Discipline:** 
  - Dark Navy (`#0F172A`) for authoritative headings and structural containers.
  - AURA Teal (`#0D9488`) for primary system highlights and AURA-Impact results.
  - Royal Blue (`#2563EB`) for structural graph elements.
  - Purple (`#7C3AED`) for semantic embeddings.
  - Forest Green (`#16A34A`) for ISO 26262 safety guarantees and verified outcomes.
  - Alert Red (`#DC2626`) for graph-blind failure modes and rejected semantic decoys.
- **High Resolution:** PNGs are rendered at high DPI; vector SVGs scale infinitely with zero pixelation.
- **16:9 Layout:** Optimized for widescreen projection and standard PPT slide ratios.
