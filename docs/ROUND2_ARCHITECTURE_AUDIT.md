# AURA-Impact — Round 2 Engineering Demonstrator Architecture Audit

**Document Type:** Pre-Implementation Architectural & System State Audit  
**Target:** KPIT Sparkle Round 2 — Judge-Ready Engineering Demonstrator  
**Date:** 2026-09-30  
**Status:** AUDITED & VERIFIED  
**Baseline Git Commit:** `54fee22e06f3ce863a302c8a0c931cb230c89594`  
**Test Suite State:** 220 passed (100% passing across 28 subsystems)  

---

## 1. Executive Summary & Audit Purpose

This audit inspects the exact state of the AURA-Impact repository prior to constructing the Round-2 judge-ready demonstration platform. In strict accordance with the Master Architectural Directives:
- **No benchmark metrics are modified or fabricated.**
- **The validated research findings are preserved without regression:**
  - AURA-Impact Headline Recall: **63.11%** (Graph-Only: 63.07%, $\Delta = +0.0004$)
  - Precision: **54.92%** | F1: **0.5503**
  - Test Suite Recall: **90.07%** | Test Suite Reduction: **82.29%**
  - Safety Invariant Enforcement: **100.0% (150/150 mutations)**
  - Autonomous Safety Discovery: **47.61%**
  - Mean Latency: **0.79 ms**
- **The frozen canonical architecture (Architecture B)** is respected as the single source of truth.

---

## 2. Current Architecture (Architecture B)

The system operates as a five-stage pipeline:

```
                            ChangedArtifact
                                   │
                                   ▼
                   [ Ingestion & Schema Parsing ]
                   (ARXML, C/C++, Reqs, Tests)
                                   │
                  ┌────────────────┴────────────────┐
                  ▼                                 ▼
         [ EngineeringGraph ]             [ SemanticEmbedder ]
          (Nodes, Edges k<=3)           (AURA-DomainHash-384)
                  │                                 │
                  ▼                                 ▼
      [ Stage 1: Graph BFS ]              [ FAISSSemanticIndex ]
                  │                                 │
                  ▼                                 │
         Traceability Complete?                     │
            ├── YES ───────────────────┐            │
            └── NO / Incomplete        │            │
                  │                    │            │
                  ▼                    │            │
        [ Stage 2: Semantic ]          │            │
        (Context-Constrained) ◀────────┼────────────┘
                  │                    │
                  ▼                    │
         [ ContextFilter Gate ]        │
         (Subsystem, Type, ECU)        │
                  │                    │
            ┌─────┴─────┐              │
            ▼           ▼              │
        [ REJECT ]  [ ACCEPT ]         │
        (Decoys)        │              │
                        ▼              ▼
                  [ Strict Set Union ]
               (S_final = S_str ∪ S_sem)
                        │
                        ▼
            [ Deterministic Test Mapper ]
            (Artifact -> Test Case IDs)
                        │
                        ▼
            [ Non-Bypassable Safety Gate ]
             (T_safe ⊆ T_selected: 100%)
                        │
                        ▼
            [ Ranked Regression Suite ]
            [ + Auditable JSON Evidence ]
```

### Core Invariants
1. **Graph-First Priority:** Deterministic graph propagation ($k \le 3$) has zero hallucinations.
2. **Context-Constrained Semantic Recovery:** Semantic retrieval is conditional on incomplete/missing structural traceability and is strictly gated by hard automotive metadata filters.
3. **Strict Set Union ($S_{final} = S_{struct} \cup S_{semantic}$):** No lossy score weighting or down-ranking of validated structural edges.
4. **Non-Bypassable Safety Gate ($T_{safe} \subseteq T_{selected}$):** 100% retention of all ASIL-C/D safety-critical test cases. If an optimization attempt drops a required safety test, a `SafetyInvariantViolationError` is raised.
5. **Model Identity:** `AURA-DomainHashEmbedder-384` (384-dimensional deterministic feature hashing with domain vocabulary weighting; zero cloud/GPU dependencies).

---

## 3. Executable Components & Entry Points

| Component | Entry File | Invocation Method | Primary Responsibility |
|---|---|---|---|
| **Pipeline API** | `src/api/pipeline.py` | `AuraImpactPipeline` | Master orchestrator connecting ingestion, graph, index, impact engine, safety gate, and evidence. |
| **CLI** | `src/api/cli.py` | `python -m src.api.cli` | Command-line execution for CI/CD integration and change analysis. |
| **Dashboard** | `dashboard/app.py` | `streamlit run dashboard/app.py` | Interactive Streamlit engineer workbench. |
| **Benchmark Runner** | `benchmark/final/runner.py` | `python benchmark/final/runner.py` | Canonical reproducible benchmark over 150 mutations across 3 domains. |
| **Adversarial Suite** | `validation/adversarial_suite.py` | `python -m validation.adversarial_suite` | 26 hostile attack scenarios (Scenarios A–Z). |
| **Reproducibility Audit** | `scripts/run_reproducibility_audit.py` | `python scripts/run_reproducibility_audit.py` | Verifies bit-for-bit determinism across repeated runs. |
| **Test Suite** | `tests/` | `python -m pytest tests/ -q` | 220 automated unit, integration, safety, failure injection, and benchmark tests. |

---

## 4. Ingestion & Data Flow

### 4.1 Ingestion
`ArtifactLoader` scans repository directories (`requirements/`, `arxml/`, `src/`, `tests/`):
- `RequirementParser` $\rightarrow$ parses JSON requirements into `RequirementRecord` ($ID$, $ASIL$, $subsystem$, $trace\_links$).
- `AutosarARXMLParser` $\rightarrow$ parses XML into `SWCRecord`, `PortRecord`, `RunnableRecord`.
- `CppTreeSitterParser` $\rightarrow$ parses C/C++ into `FunctionRecord`, `VariableRecord`, and extracts call graphs (`callees`, `rte_apis`).
- `TestParser` $\rightarrow$ parses test suites into `TestRecord` ($ID$, $targets$, $safety\_class$, $subsystem$).

### 4.2 Graph Construction
`EngineeringGraph` encapsulates a NetworkX `MultiDiGraph`:
- **Nodes:** `REQUIREMENT`, `SOFTWARE_COMPONENT`, `PORT`, `RUNNABLE`, `C_FUNCTION`, `VARIABLE`, `TEST`.
- **Edges:** `MAPS_TO`, `PROVIDES`, `REQUIRES`, `OWNS`, `CALLS`, `VERIFIES`.

### 4.3 Semantic Indexing
- Artifact text representation: `f"{id} {name} {description} {subsystem}"`.
- Embedded into 384-D unit vector via `AURA-DomainHashEmbedder-384`.
- Indexed in `FAISSSemanticIndex` (using `faiss.IndexFlatIP` with NumPy dot-product fallback).

### 4.4 Change Analysis Flow
1. Input `ChangedArtifact` received (from JSON or Git diff).
2. Freshness check: `check_staleness()` verifies MD5 file hashes against index build timestamp.
3. Stage 1: `BoundedGraphTraverser.get_explicit_impacts([seed], max_depth=3)`.
4. Stage 2: `SemanticFallback.recover(query_text, query_context, threshold=0.45)`:
   - Queries `FAISSSemanticIndex` for top-$K$ candidates.
   - Evaluates each candidate via `ContextFilter.evaluate()`:
     - Subsystem domain isolation check.
     - Artifact type compatibility check.
     - Ambiguity detection $\rightarrow$ `REVIEW_REQUIRED`.
     - Validated match $\rightarrow$ `ACCEPT` (if similarity $\ge 0.45$).
     - Out-of-domain or low similarity $\rightarrow$ `REJECT`.
5. Strict Set Union: `ImpactUnion.compute_union(structural, semantic)`.
6. Test Mapping: `TestMapper.map_impacts_to_tests(impacts)`.
7. Non-Bypassable Safety Gate: `SafetyGate.enforce(candidates, all_tests, mandatory_safety_tests)`:
   - Retains all ASIL-C/D tests.
   - Enforces $T_{safe} \subseteq T_{selected}$.
8. Evidence Generation: `EvidenceLogger` compiles `AnalysisEvidenceReport` with cryptographic timestamp and justification trail.

---

## 5. Input and Output Formats

### 5.1 Input Change Format (`ChangedArtifact`)
```json
{
  "artifact_id": "REQ_AEB_001",
  "artifact_type": "Requirement",
  "subsystem": "ADAS",
  "ecu": "ECU_1",
  "change_type": "MODIFY",
  "after_content": "Update Time-to-Collision threshold formula to account for wet asphalt friction coefficient.",
  "change_semantics": "Time-to-collision calculation TTC radar distance ego speed",
  "metadata": {}
}
```

### 5.2 Output Evidence Format (`AnalysisEvidenceReport`)
```json
{
  "analysis_id": "ANALYSIS_REQ_AEB_001_1775034500",
  "timestamp": "2026-09-30T14:45:00.123456",
  "changed_artifact_id": "REQ_AEB_001",
  "subsystem": "ADAS",
  "structural_impacts_count": 3,
  "semantic_recoveries_count": 1,
  "rejected_candidates_count": 4,
  "review_required_count": 0,
  "total_impacts_count": 4,
  "tests_selected_count": 2,
  "safety_tests_count": 2,
  "total_test_suite_size": 170,
  "test_reduction_pct": 98.82,
  "safety_recall_pct": 100.0,
  "decisions": [
    {
      "artifact_id": "SWC_AEB",
      "artifact_type": "SoftwareComponent",
      "decision": "STRUCTURAL_ACCEPT",
      "stage": "GRAPH",
      "confidence": 1.0,
      "reason": "Explicit graph path of depth 1 with confidence 1.00",
      "details": {"path": ["REQ_AEB_001", "SWC_AEB"], "depth": 1}
    },
    {
      "artifact_id": "C_Function_TriggerBrake",
      "artifact_type": "C_Function",
      "decision": "SEMANTIC_ACCEPT",
      "stage": "SEMANTIC",
      "confidence": 0.82,
      "reason": "Semantic similarity (0.82) above threshold with verified context.",
      "details": {"context_score": 1.0, "evidence": {"subsystem_match": true}}
    },
    {
      "artifact_id": "TC_AEB_001",
      "artifact_type": "Test",
      "decision": "SAFETY_GATE_RETAIN",
      "stage": "SAFETY_GATE",
      "confidence": 1.0,
      "reason": "Mandatory safety-critical test (ASIL_D)",
      "details": {"safety_class": "ASIL_D"}
    }
  ],
  "latency_profile": {
    "stage1_graph_ms": 0.25,
    "stage2_semantic_ms": 0.45,
    "total_latency_ms": 0.78
  }
}
```

---

## 6. Current Dashboard Capabilities

The existing dashboard in `dashboard/app.py` provides:
1. **Target Repository Selection:** Ingests `examples/demo_repo`, `data/projects/adas`, `data/projects/powertrain`, or `data/projects/battery_ev`.
2. **Page Navigation:** 5 distinct pages accessed via sidebar radio buttons:
   - *1. Change Analysis:* Metrics, change JSON, and table of impacted artifacts.
   - *2. Visual Impact Graph:* Matplotlib / NetworkX static layout of nodes colored by type.
   - *3. Semantic Candidates:* Table of retrieved candidates with similarity scores, context scores, and accept/reject statuses.
   - *4. Test Selection:* Test suite counts, reduction metric, and prioritized test table.
   - *5. Evidence Report:* Analysis ID, latency profile, decision trail, and downloadable JSON evidence.
3. **Change Input:** Supports 4 predefined demo scenarios or manual input fields.

---

## 7. Current Limitations & Missing Demo Capabilities for Round 2

| Area | Current Implementation Limitation | Required Round-2 Demonstrator Capability |
|---|---|---|
| **Demonstrator Layout** | The user must click across 5 separate pages in the sidebar to understand a single change. | Unified single-screen flow or tabbed judge-first walkthrough showing the full lifecycle: `Change` $\rightarrow$ `Graph` $\rightarrow$ `Semantic` $\rightarrow$ `Decoy Rejection` $\rightarrow$ `Safety Gate` $\rightarrow$ `Evidence`. |
| **Demo Scenarios** | Only 4 basic JSON files in `examples/demo_repo`; lacks dedicated one-click scenarios with pre-configured expected outcomes. | 6 dedicated, judge-ready scenarios: (1) Explicit Structural, (2) Hidden Semantic Dependency, (3) Semantic Decoy Rejection, (4) Ambiguous Change (`REVIEW_REQUIRED`), (5) Safety-Critical Regression ($T_{safe} \subseteq T_{selected}$), (6) Large Regression Reduction. |
| **Graph-Blind Demonstration** | Graph analysis and semantic fallback run sequentially, but the UI does not explicitly highlight the exact graph-blindness comparison (Graph finding 0 vs Semantic finding 1 with evidence). | Explicit comparison card: "GRAPH: No explicit path found (0 impacts) vs SEMANTIC: Discovered latent coupling with context accepted (1 impact)". |
| **Decoy Rejection Visibility** | In `src/semantic/retriever.py`, passing `subsystem_filter` to `index.search()` filters candidates before retrieval, so out-of-subsystem decoys are dropped at indexing rather than explicitly retrieved and rejected by `ContextFilter`. | Provide full transparency mode where both candidates are retrieved, showing: Raw Semantic: Both high score $\rightarrow$ Context Filter: Candidate B rejected with clear reason $\rightarrow$ Final: Candidate A retained. |
| **Ambiguity Surfacing** | Minimal guidance on what missing evidence triggered `REVIEW_REQUIRED`. | Detailed ambiguity breakdown showing missing interface, unclear timing, candidate artifacts, and recommended engineer action. |
| **Live Performance Profiling** | `report.latency_profile` only tracks Stage 1 and Stage 2 latency. | Measure and display parsing time, graph time, semantic retrieval time, context filtering time, test mapping time, safety gate time, and total time, writing to `validation/round2/performance.csv`. |
| **Safety Invariant Visualization** | Shows "100% Retained" metric, but lacks a visible interactive safety invariant panel with a simulated block test. | Dedicated Safety Invariant Panel with live enforcement badge, retained ASIL-C/D test list, and simulated violation test showing immediate `BLOCKED` status. |
| **Benchmark vs Live Separation** | Research benchmark metrics and live demo results are not clearly juxtaposed. | Explicitly separate and display canonical benchmark results (63.11%, 82.29%, 0.79 ms) from live demonstration results. |

---

## 8. Components That Must NOT Be Changed

1. **Benchmark Results:**
   - Recall: 63.11%, Precision: 54.92%, F1: 0.5503, Test Reduction: 82.29%, Safety Invariant: 100.0%, Mean Latency: 0.79 ms.
   - Graph-Only: 63.07%, Embedding-Only: 42.45%, Keyword: 42.82%.
2. **Canonical Architecture B Core Invariants:**
   - Strict set union: $S_{final} = S_{struct} \cup S_{semantic}$.
   - Non-bypassable safety gate: $T_{safe} \subseteq T_{selected}$.
   - Semantic model identity: `AURA-DomainHashEmbedder-384`.
3. **Data Integrity & Benchmark Splits:**
   - `data/ground_truth/`, `data/mutations/`, `artifacts/gates/`, `benchmark/final/outputs/`.
4. **All 220 Passing Tests:**
   - All tests in `tests/` must remain untouched and passing.

---

## 9. Next Steps for Round 2 Execution

1. Build a realistic, cohesive automotive demonstration dataset labeled clearly as `DEMONSTRATION DATASET` with all 5 required relationship types (explicit, hidden, decoy, safety-critical, ambiguous).
2. Enhance `dashboard/app.py` with unified judge-focused layout, dedicated scenario tabs, visual graph-blindness comparison, decoy rejection inspector, safety gate invariant panel, and live latency breakdown.
3. Implement `scripts/run_round2_validation.py` executing all 12 validation scenarios.
4. Implement adversarial testing and failure logging in `validation/round2/failures/`.
5. Run cross-project validation across ADAS, Powertrain, and Body Electronics.
6. Verify zero data leakage and write `validation/round2/leakage_audit.md`.
7. Generate comprehensive documentation:
   - `reports/round2/ROUND2_VALIDATION_REPORT.md`
   - `docs/ROUND2_DEMO_RUNBOOK.md`
   - `docs/ROUND2_30_SECOND_DEMO.md`
   - `docs/ROUND2_3_MINUTE_DEMO.md`
   - `docs/ROUND2_JUDGE_QA.md`
8. Add new test suite in `tests/round2/` (at least 30 new tests) while maintaining all 220 existing tests passing.
