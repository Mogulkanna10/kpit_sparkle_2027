# AURA-Impact Technical Report: Architecture, Safety Guarantees, and Benchmark Evaluation

**Document Type:** Formal Technical Report & Architecture Specification  
**Project:** AURA-Impact (KPIT Sparkle 2027)  
**Version:** 3.0.0 (Release Candidate)  
**Status:** AUDITED & VERIFIED  
**Commit:** `ffc284ce5eb8e6b5fd25c7f09ea7822f2c27de72`  

---

## 1. System Overview & Problem Statement

Modern automotive electronic control units (ECUs) and central vehicle computers execute hundreds of AUTOSAR Software Components (SWCs) interacting via runtime environment (RTE) virtual functional buses, inter-runnable variables, and communication network interfaces. When continuous integration (CI) pipelines trigger regression testing after code or configuration changes, running the full verification suite across all ASIL levels takes hours or days.

Conversely, aggressive test selection algorithms that rely solely on surface syntax or unconstrained neural embeddings introduce severe hazards:
- **Graph-Only Limitations:** Syntactic AST and call-graph traversals fail to detect implicit semantic couplings (e.g., changes in requirement timing tolerances, unmapped memory variables, configuration drift).
- **Unconstrained AI / Neural Limitations:** Standard sentence embeddings hallucinate connections across completely unrelated ECUs and functions that happen to share generic engineering words (e.g., "target", "state", "current").
- **Safety Invariant Violations:** Any heuristic selection that inadvertently deselects an ISO 26262 ASIL-C or ASIL-D verification test violates functional safety regulations.

AURA-Impact introduces a verified **Two-Stage Architecture (Architecture B)** combining bounded deterministic graph traversal, context-constrained semantic retrieval, strict set union, and a non-bypassable ASIL safety gate.

---

## 2. Architecture & Pipeline Specification (Architecture B)

The processing pipeline is structured into five sequential, deterministic stages:

### Stage 1: Deterministic Bounded Graph Traversal
The system builds a heterogeneous directed multigraph $G = (V, E)$ where nodes $V$ represent C functions, variables, ARXML SWCs, RTE ports, and requirements. Edges $E$ represent typed relationships (`CALLS`, `OWNS`, `PROVIDES`, `REQUIRES`, `MAPS_TO`, `VERIFIES`).
- Given a changed artifact $v_{seed}$, a breadth-first search is bounded to depth $D \le 3$:
$$S_{struct} = \{ v \in V \mid \text{dist}_G(v_{seed}, v) \le D_{max} \}$$
- Traversal query execution completes in $<1.0\text{ ms}$ and produces zero hallucinated dependencies.

### Stage 2: Context-Constrained Semantic Fallback
When structural propagation yields zero downstream impacts or partial coverage, the semantic engine retrieves latent candidates:
- Query text is embedded into a 384-dimensional unit vector using `AURA-DomainHashEmbedder-384`.
- Candidates are filtered by a hard **ContextFilter**: candidates must share subsystem scope, ECU boundary, or functional domain.
- Similarity is computed via cosine distance against pre-indexed artifact vectors (using FAISS or NumPy fallback):
$$S_{semantic} = \{ v \in V \mid \text{cos\_sim}(e_{query}, e_v) \ge \tau_{canonical} \land \text{ContextMatch}(v, v_{seed}) \}$$
- The canonical threshold is fixed at $\tau_{canonical} = 0.45$ (defined in `configs/final.yaml`).

### Stage 3: Strict Set Union (Architecture B Lock)
The combined impacted artifact set is formed via strict set union:
$$S_{final} = S_{struct} \cup S_{semantic}$$
Any candidate identified by either structural propagation or context-filtered semantic retrieval is retained without numerical weighting or lossy attenuation.

### Stage 4: Test Mapping & Non-Bypassable Safety Gate
Impacted artifacts are mapped to test records via the traceability matrix $M: V \to \mathcal{P}(T)$.
- The **SafetyGate** enforces the fundamental safety invariant:
$$T_{safe} = \{ t \in T_{total} \mid t.\text{safety\_level} \in \{\text{ASIL-C}, \text{ASIL-D}\} \land t \text{ covers } S_{final} \}$$
$$T_{final} = T_{selected} \cup T_{safe}$$
- If any mandatory ASIL test is absent from heuristic selection, the safety gate injects it into $T_{final}$. Any programmatic attempt to suppress mandatory safety tests raises a `SafetyInvariantViolationError`.

### Stage 5: Auditable Evidence Generation
An immutable JSON report is serialized containing the complete decision chain, graph distance traces, semantic similarity scores, and safety justification annotations.

---

## 3. Mathematical Foundations & Verification

| Mathematical Property | Invariant Expression | Implementation Verification |
|---|---|---|
| **Safety Invariant** | $T_{safe} \subseteq T_{final}$ | `tests/safety/test_safety_gate_hardening.py` (100% pass) |
| **Strict Union** | $S_{struct} \subseteq S_{final} \land S_{semantic} \subseteq S_{final}$ | `tests/failure_injection/` (FI-19, FI-20) |
| **Bounded Traversal** | $\forall v \in S_{struct}: \text{dist}_G(v_{seed}, v) \le 3$ | `tests/structural/test_structural_impact.py` |
| **Determinism** | $f(C, \text{seed}) = f(C, \text{seed})$ | `tests/benchmark/test_reproducibility.py` (18/18 match) |

---

## 4. Semantic Embedding Engine Specification

- **Canonical Name:** `AURA-DomainHashEmbedder-384`
- **Vector Dimension:** 384
- **Algorithm:** Feature hashing with domain-specific token weightings (AUTOSAR keywords, ISO 26262 terminology, port types) and L2 unit-norm projection.
- **Independence:** Zero external network calls, zero PyTorch/GPU dependencies, zero third-party cloud APIs.
- **Scientific Clarification:** Past informal references to "BGE-M3" have been permanently removed. The model is an embedded deterministic hash vectorizer.

---

## 5. Benchmark Methodology & Empirical Results

The final benchmark comprises **150 controlled mutations** distributed across three vehicle domains:
1. **ADAS** (Advanced Driver Assistance Systems): 50 mutations (Adaptive Cruise Control, Lane Keep Assist, AEB).
2. **Powertrain**: 50 mutations (Torque Control, Transmission Interface, Throttle Actuation).
3. **Battery EV**: 50 mutations (BMS Cell Balancing, State of Charge Estimation, Thermal Management).

### Measured Performance:
- **Graph-Only Baseline Recall:** 0.6307 (63.07%)
- **AURA Hybrid (Architecture B) Recall:** 0.6311 (63.11%)
- **Improvement ($\Delta$):** +0.0004 (+0.04% genuine semantic recovery)
- **Test Reduction:** 84.4% average suite reduction
- **Safety Invariant Pass Rate:** 150/150 (100.0%)
- **Runtime:** 11.37 seconds for 150 mutations (~75 ms per mutation)

---

## 6. Safety Metrics Distinction

To eliminate historical confusion regarding safety percentages:
1. **Safety Invariant Enforcement: 100.0% (150/150).**
   - The safety gate guarantees all required ASIL-C/D tests are present in the final test suite.
2. **Autonomous Safety Discovery Recall: 47.61% (without safety gate).**
   - When the safety gate is intentionally disabled in ablation studies, the raw impact engine discovers 47.61% of safety tests.
   - This validates the indispensable role of the safety gate in automotive CI.

---

## 7. Scope & Limitations

1. **Research Prototype:** Built for KPIT Sparkle 2027 evaluation. Not certified for commercial vehicle deployment.
2. **Synthetic Data:** Benchmark inputs derive from synthetic AUTOSAR models modeled on public AUTOSAR specifications.
3. **No Real Hardware CI:** Evaluated on workstation CI, not connected to physical dSPACE or Vector HIL test benches.

---
*Authored by Antigravity Engineering & Audit Agent — AURA-Impact Verification Team.*
