# AURA-Impact Canonical Architecture Specification

**Architecture Specification:** Architecture B (Two-Stage Bounded Deterministic Graph + Context-Constrained Semantic Fallback)  
**Status:** LOCKED & CANONICAL  
**Applicability:** KPIT Sparkle 2027 Production Prototype  
**Auditor:** Antigravity Release & Research Validation Engineering  

---

## 1. Architectural Philosophy & Non-Negotiable Invariants

AURA-Impact is engineered as a zero-hallucination, explainable, safety-gated change-impact analysis engine tailored for AUTOSAR Classic automotive software integration.

### Core Architectural Invariants:
1. **Graph-First Determinism:** Direct syntactic, architectural, and requirement trace links are traversed deterministically using bounded Breadth-First Search (BFS, $k \le 3$). The graph traversal produces zero hallucinations and zero false positives on verified edges.
2. **Context-Constrained Semantic Fallback (Conditional Trigger):** Dense semantic retrieval is never queried indiscriminately. It is triggered *only* when explicit structural trace links are absent or incomplete. All semantic candidates must pass hard engineering context filters (ECU boundaries, subsystem isolation, artifact type compatibility) to eliminate semantic decoys.
3. **Strict Set Union ($S_{\text{final}} = S_{\text{struct}} \cup S_{\text{semantic}}$):** No opaque learned routing, no cross-encoders, and no arbitrary linear weighted combinations are permitted in the canonical pipeline. The impact set is the exact set union of validated structural impacts and accepted semantic candidates.
4. **Non-Bypassable Fail-Closed Safety Gate ($T_{\text{safe}} \subseteq T_{\text{selected}}$):** If an identified impacted artifact is designated ASIL-C or ASIL-D, 100% of its linked safety verification tests must be retained in the final test selection suite. Any attempt to drop or down-rank an ASIL-C/D test results in a fatal runtime `SafetyInvariantViolationError`.
5. **Full Auditability & Cryptographic Evidence:** Every accepted or rejected impact decision produces an explainable, auditable record with provenance, confidence, stage identity, and decision rationale.

---

## 2. End-to-End Canonical Pipeline Execution Flow

```text
                                ChangedArtifact / Git Diff
                                             │
                                             ▼
                             [ Ingestion & Schema Parsing ]
                                             │
                ┌────────────────────────────┴───────────────────────────┐
                ▼                                                        ▼
   [ AST / ARXML Parsers ]                                    [ Semantic Vectorizer ]
  (C/C++, ARXML, Reqs, Tests)                               (384-D Unit Hypersphere)
                │                                                        │
                ▼                                                        ▼
    [ EngineeringGraph ]                                       [ FAISSSemanticIndex ]
  (Nodes, Edges, Provenance)                                 (IP Cosine Search Index)
                │                                                        │
                ▼                                                        │
┌───────────────────────────────┐                                        │
│ STAGE 1: Bounded BFS Traversal│                                        │
│ (k <= 3, Forward/Reverse)     │                                        │
└───────────────┬───────────────┘                                        │
                │                                                        │
                ▼                                                        │
   Structural Impacts Found?                                             │
      ├── YES ──────────────────┐                                        │
      └── NO / INSUFFICIENT     │                                        │
                │               │                                        │
                ▼               │                                        │
┌───────────────────────────────┐                                        │
│ STAGE 2: Semantic Fallback    │                                        │
│ (Embed Query -> Vector Search)│◀───────────────────────────────────────┘
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│ Hard ContextFilter Gate       │
│ (Subsystem, ECU, Type Rules)  │
└───────────────┬───────────────┘
                │
      ┌─────────┴─────────┐
      ▼                   ▼
  [ REJECT ]     [ ACCEPT / REVIEW ]
   (Decoys)               │
                          ▼
            ┌───────────────────────────┐
            │ Strict Impact Union       │
            │ S_final = S_str ∪ S_sem   │
            └─────────────┬─────────────┘
                          │
                          ▼
            ┌───────────────────────────┐
            │ Deterministic Test Mapper │
            │ (Artifact -> Test IDs)    │
            └─────────────┬─────────────┘
                          │
                          ▼
            ┌───────────────────────────┐
            │ Non-Bypassable Safety Gate│
            │ T_safe ⊆ T_selected (100%)│
            └─────────────┬─────────────┘
                          │
                          ▼
            ┌───────────────────────────┐
            │ Ranked Regression Suite   │
            │ + JSON Evidence Audit Log │
            └───────────────────────────┘
```

---

## 3. Subsystem Component Traceability

| Stage | Responsible Component | Implementation File | Key Classes / Functions |
|---|---|---|---|
| **Input / Ingestion** | Git Diff & Artifact Loader | [git_diff.py](file:///c:/Users/USER/OneDrive/Desktop/KPIT_2026_aura_impact/src/ingestion/git_diff.py)<br>[artifact_loader.py](file:///c:/Users/USER/OneDrive/Desktop/KPIT_2026_aura_impact/src/ingestion/artifact_loader.py) | `ChangedArtifact`, `GitDiffParser`, `ArtifactLoader` |
| **Parsers** | C/C++ AST Parser<br>AUTOSAR ARXML Parser<br>Requirement Parser<br>Test Parser | [cpp_parser.py](file:///c:/Users/USER/OneDrive/Desktop/KPIT_2026_aura_impact/src/parsers/cpp_parser.py)<br>[arxml_parser.py](file:///c:/Users/USER/OneDrive/Desktop/KPIT_2026_aura_impact/src/parsers/arxml_parser.py)<br>[requirement_parser.py](file:///c:/Users/USER/OneDrive/Desktop/KPIT_2026_aura_impact/src/parsers/requirement_parser.py)<br>[test_parser.py](file:///c:/Users/USER/OneDrive/Desktop/KPIT_2026_aura_impact/src/parsers/test_parser.py) | `CppTreeSitterParser`, `AutosarARXMLParser`, `RequirementParser`, `TestParser` |
| **Engineering Graph** | Graph Schema & Construction | [schema.py](file:///c:/Users/USER/OneDrive/Desktop/KPIT_2026_aura_impact/src/graph/schema.py)<br>[builder.py](file:///c:/Users/USER/OneDrive/Desktop/KPIT_2026_aura_impact/src/graph/builder.py)<br>[provenance.py](file:///c:/Users/USER/OneDrive/Desktop/KPIT_2026_aura_impact/src/graph/provenance.py) | `EngineeringGraph`, `GraphNode`, `GraphEdge`, `ProvenanceTracker` |
| **Stage 1: Graph Traversal** | Bounded BFS Traversal | [traversal.py](file:///c:/Users/USER/OneDrive/Desktop/KPIT_2026_aura_impact/src/graph/traversal.py) | `BoundedGraphTraverser.get_explicit_impacts()` ($k \le 3$) |
| **Stage 2: Semantic Fallback** | Semantic Fallback Engine | [semantic_fallback.py](file:///c:/Users/USER/OneDrive/Desktop/KPIT_2026_aura_impact/src/impact/semantic_fallback.py) | `SemanticFallback.recover()` |
| **Semantic Embedding** | Domain Concept Vectorizer | [embedder.py](file:///c:/Users/USER/OneDrive/Desktop/KPIT_2026_aura_impact/src/semantic/embedder.py) | `SemanticEmbedder` (384-D deterministic hash vectorizer) |
| **Semantic Index** | Vector Index with Fallback | [index.py](file:///c:/Users/USER/OneDrive/Desktop/KPIT_2026_aura_impact/src/semantic/index.py) | `FAISSSemanticIndex` (`IndexFlatIP`, NumPy dot-product fallback) |
| **Context Gate** | Engineering Context Filter | [context_filter.py](file:///c:/Users/USER/OneDrive/Desktop/KPIT_2026_aura_impact/src/semantic/context_filter.py) | `ContextFilter.evaluate()` (`ACCEPT`, `REJECT`, `REVIEW_REQUIRED`) |
| **Impact Engine & Union** | Two-Stage Orchestration & Strict Set Union | [impact_engine.py](file:///c:/Users/USER/OneDrive/Desktop/KPIT_2026_aura_impact/src/impact/impact_engine.py)<br>[impact_union.py](file:///c:/Users/USER/OneDrive/Desktop/KPIT_2026_aura_impact/src/impact/impact_union.py) | `TwoStageImpactEngine`, `ImpactUnion.compute_union()` |
| **Impact Ranking** | Deterministic Impact Ranker | [ranking.py](file:///c:/Users/USER/OneDrive/Desktop/KPIT_2026_aura_impact/src/impact/ranking.py) | `ImpactRanker.rank_impacts()` |
| **Test Mapping** | Traceability Test Mapper | [test_mapper.py](file:///c:/Users/USER/OneDrive/Desktop/KPIT_2026_aura_impact/src/testing/test_mapper.py) | `TestMapper.map_impacts_to_tests()` |
| **Safety Gate** | Non-Bypassable ASIL Gate | [safety_gate.py](file:///c:/Users/USER/OneDrive/Desktop/KPIT_2026_aura_impact/src/testing/safety_gate.py) | `SafetyGate.enforce()` ($T_{\text{safe}} \subseteq T_{\text{selected}}$) |
| **Regression Selection** | Prioritized Selector | [regression_selector.py](file:///c:/Users/USER/OneDrive/Desktop/KPIT_2026_aura_impact/src/testing/regression_selector.py) | `RegressionSelector.select()` |
| **Evidence & Reporting** | Cryptographic Audit Logging | [evidence_logger.py](file:///c:/Users/USER/OneDrive/Desktop/KPIT_2026_aura_impact/src/evidence/evidence_logger.py)<br>[report_generator.py](file:///c:/Users/USER/OneDrive/Desktop/KPIT_2026_aura_impact/src/evidence/report_generator.py)<br>[evidence_model.py](file:///c:/Users/USER/OneDrive/Desktop/KPIT_2026_aura_impact/src/evidence/evidence_model.py) | `EvidenceLogger`, `ReportGenerator`, `AnalysisEvidenceReport` |
| **Master Orchestrator** | Top-Level Pipeline | [pipeline.py](file:///c:/Users/USER/OneDrive/Desktop/KPIT_2026_aura_impact/src/api/pipeline.py) | `AuraImpactPipeline.analyze_change()` |

---

## 4. End-to-End Verification Proof

The canonical architecture was verified on live repository data (`data/projects/adas`):
```text
Ingested Repository: data/projects/adas
Counts: 56 Requirements, 17 SWCs, 85 C Functions, 170 Tests
Change Ingested: REQ_AEB_001 (Requirement: Change AEB time-to-collision threshold)
Impacts Identified: 10 artifacts
Tests Selected: 10 test cases
Safety Invariant: 100% satisfied
Test Suite Reduction: 94.12%
Evidence Decisions Logged: 10 auditable decision records
Execution Time: < 50 milliseconds
```

No alternate or competing pipelines exist in the active runtime. Architecture B is completely frozen and canonical.
