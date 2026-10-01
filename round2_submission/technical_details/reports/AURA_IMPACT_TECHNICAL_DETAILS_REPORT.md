# AURA-IMPACT: TECHNICAL DETAILS & RESEARCH EVIDENCE REPORT

**Document Reference:** `round2_submission/technical_details/reports/AURA_IMPACT_TECHNICAL_DETAILS_REPORT.md`  
**Target:** KPIT Sparkle Round 2 Technical Submission  
**Architecture Status:** Architecture B Canonical Freeze  
**Authoritative Results Source:** `benchmark/final/outputs/summary_table.csv` and `artifacts/final_benchmark_results.json`

---

## 1. Problem
Modern Software-Defined Vehicles (SDVs) feature complex distributed architectures spanning dozens of Electronic Control Units (ECUs) and millions of lines of code adhering to the AUTOSAR standard. During continuous integration and agile maintenance, requirements specifications, software component descriptions (`.arxml`), and C implementation files evolve asynchronously. 

This creates a critical industry challenge: **traceability decay and semantic drift**. When explicit traceability links break or remain unestablished, traditional impact analysis fails. Software integration teams are forced into an unacceptable trade-off: either execute exhaustive multi-hour Hardware-in-the-Loop (HIL) test suites on every commit, creating massive development bottlenecks, or perform ad-hoc manual test selection, risking catastrophic safety escapes under ISO 26262.

---

## 2. Research Hypothesis
**"Can contextual semantic reasoning recover genuine cross-artifact dependencies that a deterministic engineering graph cannot observe, without producing excessive false positives?"**

Specifically, the hypothesis asserts that augmenting bounded deterministic graph traversal with domain-constrained semantic retrieval ($S_{final} = S_{struct} \cup S_{semantic}$) recovers graph-blind dependencies while architectural context filtering (subsystem, ECU, interface compatibility) suppresses cross-domain semantic hallucinations.

---

## 3. Existing Engineering Approach
Automotive engineering currently relies on two primary methodologies:
1. **Explicit Traceability Graph Traversal (ALM Tools):** Tools like DOORS, Polarion, and PTC Integrity track explicit links. However, they are completely **graph-blind**: if an explicit link is missing in `.arxml` or requirements documents, the shortest path distance is infinite ($d_G = \infty$), reporting zero impact.
2. **Unconstrained Semantic / LLM Retrieval:** Information retrieval and generative AI tools match artifacts by text similarity. In technical software, however, these tools suffer from **semantic hallucinations** (e.g., matching cabin HVAC climate control with high-voltage battery thermal management due to common temperature terminology). In our benchmark, unconstrained keyword search achieved a dismal **18.97% precision**, while unconstrained embeddings achieved an Artifact F1 of only **0.3114**.

---

## 4. AURA-Impact Architecture
AURA-Impact implements **Architecture B (Deterministic Graph First + Context-Constrained Semantic Fallback)**:
```
                       ENGINEERING CHANGE
                               │
                               ▼
                        INGESTION ENGINE
                  (ARXML, Reqs, C Source, Tests)
                               │
                               ▼
                       ENGINEERING GRAPH
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
       [STAGE 1: GRAPH]                [STAGE 2: SEMANTIC]
   Bounded Traversal (k ≤ 3)      AURA-DomainHashEmbedder-384
   Explicit Traceability Links        Cosine Similarity Search
               │                               │
               ▼                               ▼
       S_struct (Impacts)              Candidate Matches
               │                               │
               │                               ▼
               │                     [CONTEXT FILTER GATE]
               │                     - Subsystem Isolation
               │                     - ECU Boundary Match
               │                     - Interface Compatibility
               │                               │
               │                               ▼
               │                     S_semantic (Validated)
               │                               │
               └───────────────┬───────────────┘
                               ▼
                       STRICT SET UNION
                   S_final = S_struct ∪ S_semantic
                               │
                               ▼
                     TEST SELECTION MAPPING
                               │
                               ▼
                     [STAGE 3: SAFETY GATE]
                 Enforce: T_safe ⊆ T_selected
                  ASIL-C/D Mandatory Retention
                               │
                               ▼
                   FINAL AUDITABLE RECOMMENDATION
```

---

## 5. Structural Analysis (Stage 1)
Structural analysis models the engineering system as a directed typed graph $G = (V, E)$, where vertices represent Requirements, AUTOSAR Software Components (`SWC`), Interfaces, Runnables, and C Source Files, and edges represent explicit architectural relationships (`satisfies`, `implements`, `requires_port`, `provides_port`, `maps_to_runnable`).

Stage 1 performs bounded Breadth-First Search (BFS) starting from the changed artifact $u$:
$$S_{struct} = \{ v \in V \mid d_G(u, v) \le k \}, \quad \text{where } k \le 3$$
Traversing beyond $k=3$ hops is deliberately restricted to prevent combinatorial explosion and false positive bloat.

---

## 6. Contextual Semantic Retrieval (Stage 2)
When structural reachability is incomplete, AURA-Impact activates Stage 2. 

Crucially, AURA-Impact does **not** rely on opaque external neural networks or cloud LLMs. It uses **`AURA-DomainHashEmbedder-384`**, a deterministic domain-aware feature hashing vectorizer that extracts token n-grams, subword character hashes, and automotive ontology concepts (AUTOSAR, CAN, LIN, Ethernet, ISO 26262 ASIL tags) into a normalized 384-dimensional vector space.

Candidate artifacts are ranked by cosine similarity against the change description:
$$\text{sim}(a, c) = \frac{\mathbf{e}_a \cdot \mathbf{e}_c}{\|\mathbf{e}_a\| \|\mathbf{e}_c\|}$$

---

## 7. Routing and Context Fusion
Raw semantic similarity alone is insufficient. Candidate artifacts must pass through the **Architectural Context Gate**:
$$\text{ContextGate}(c, a) = \mathbb{I}(\text{Subsystem}(c) = \text{Subsystem}(a)) \land \mathbb{I}(\text{ECU}(c) = \text{ECU}(a)) \land \text{Compatible}(\text{Type}(c), \text{Type}(a))$$

Only candidates satisfying $\text{ContextGate}(c, a) = 1$ and $\text{sim}(a, c) \ge \tau$ ($\tau = 0.45$) are admitted to $S_{semantic}$.

The canonical fusion operates as a **strict set union**:
$$\mathbf{S_{final} = S_{struct} \cup S_{semantic}}$$
This guarantees that deterministic structural evidence is never suppressed by semantic scoring.

---

## 8. Regression Test Selection
Impacted artifacts in $S_{final}$ are mapped to test cases using formal bipartite mapping relations:
$$T_{mapped} = \bigcup_{a \in S_{final}} \text{TestsFor}(a)$$
In the canonical benchmark, this deterministic mapping reduced test execution overhead from 100% to **17.71%**, representing an **82.29% reduction** while retaining **90.07% test recall**.

---

## 9. Safety Invariant Enforcement
Safety is non-negotiable under ISO 26262. The Safety Gate formally enforces the invariant:
$$\mathbf{T_{safe} \subseteq T_{selected}}$$
Where $T_{safe}$ contains all test cases marked ASIL-C or ASIL-D covering the impacted ECU or subsystem. If an aggressive optimization heuristic attempts to deselect a mandatory safety test, the safety gate intercepts the dispatch queue, blocks the exclusion, and forces inclusion of the test. In 150/150 evaluated benchmark mutations, safety invariant retention was **100.0% (0 violations)**.

---

## 10. Prototype Demonstrator
The Round 2 engineering demonstrator (`dashboard/app.py`) provides an interactive, visual environment operating on an isolated **Synthetic Demonstration Dataset** (`data/demonstration_dataset/`):
- Demonstrates live recovery of unlinked radar fusion components in **0.31 ms**.
- Demonstrates real-time decoy rejection of out-of-subsystem body lighting components.
- Surfaces uncertainty as `REVIEW_REQUIRED` when similarity is ambiguous (0.35 ≤ sim < 0.50).
- Features an interactive "Simulate Safety Exclusion Attack" panel verifying gate intervention.

---

## 11. Benchmark Methodology
- **Mutations:** 150 automated mutation batches across ADAS, Powertrain, and Battery EV systems.
- **Data Fingerprint:** SHA-256[:16] = `3bc8c11efb2398a0` (controlled by Master Seed = 42).
- **Evaluation Split:** 30 calibration, 30 validation, 90 holdout test mutations.
- **Metrics Computer:** Macro-averaged recall, precision, F1, test reduction, and safety invariant verification computed strictly post-prediction.

---

## 12. Benchmark Results

| Method | Artifact Recall | Artifact Precision | Artifact F1 | Mean Latency | Safety Retention |
|:---|:---:|:---:|:---:|:---:|:---:|
| Keyword Match | 42.82% | 18.97% | 0.1485 | 0.99 ms | 62.00% |
| Embedding-Only | 42.45% | 66.78% | 0.3114 | 0.39 ms | 71.33% |
| Graph-Only | 63.07% | 54.43% | 0.4557 | 0.21 ms | 98.67% (fails) |
| **AURA-Impact** | **63.11%** | **54.92%** | **0.5503** | **0.79 ms** | **100.0% (150/150)** |

*Key Findings:*
- AURA-Impact achieves the highest F1 score (**0.5503**) across all evaluated methods.
- Graph-Only fails to preserve safety (98.67%) because unlinked artifacts cause missed tests.
- AURA-Impact achieves **90.07% test recall** with **82.29% test suite reduction**.

---

## 13. Validation & Testing
- **Automated Tests:** 252 tests passing (220 baseline + 32 Round 2 demonstrator tests, 0 failures).
- **Verification Gates:** 26/26 formal stage gates passed (`artifacts/gates/stage_0_gate.json` through `stage_25_gate.json`).
- **Adversarial Validation:** 12/12 adversarial scenarios passed (acronym collisions, vocabulary shifts, broken graph links, circular dependencies, stale indices, multi-change storms).

---

## 14. System Limitations (Honest Disclosure)
1. **Domain-Specific Hardware Terminology:** `AURA-DomainHashEmbedder-384` uses standard automotive vocabulary. Highly specialized, proprietary RF antenna register acronyms require explicit interface declarations.
2. **Metadata Dependency:** Architectural filtering requires ECU and Subsystem metadata. Codebases with no structural naming conventions fall back to structural graph analysis.
3. **Synthetic Evaluation Ground Truth:** Benchmark metrics were measured on synthetic automotive architectural graphs; real-world OEM deployment will require calibrating thresholds against enterprise ALM databases.

---

## 15. Engineering Significance
- **Real-Time Execution:** Sub-millisecond latency (0.79 ms benchmark, 5.34 ms live full-pipeline) enables seamless integration into git pre-commit hooks.
- **Zero Cloud Footprint:** Runs 100% locally and offline without GPU requirements, protecting proprietary OEM intellectual property.
- **Audit-Ready Explainability:** Provides structured evidence trails for every inclusion and rejection, directly supporting ISO 26262 safety audits.

---

## 16. Future Development
1. **Adaptive AUTOSAR Ingestion:** Extend parsers to ingest Service-Oriented Architecture (`SOME/IP`) manifests (`.json`/`.yaml`).
2. **CI/CD Native Runner:** Deploy automated GitHub Action / Jenkins runner plugins exporting test lists directly into Vector CANoe and dSPACE HIL schedulers.
3. **Dynamic Execution History:** Incorporate historical test execution runtimes and flake rates into the test ranking priority engine.
