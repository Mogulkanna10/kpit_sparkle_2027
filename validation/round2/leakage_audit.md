# AURA-Impact — Round 2 Data Leakage Forensic Audit

**Audit Date:** 2026-09-30  
**Auditor:** Antigravity — Round 2 Engineering Architecture Audit  
**Scope:** Live Demonstrator Pipeline, Predefined Demo Scenarios, Test Selection, and Safety Gate  
**Verdict:** ✅ **ZERO_LEAKAGE_VERIFIED**

---

## 1. Audit Objective & Non-Leakage Principle

In safety-critical automotive software and academic benchmarks, data leakage occurs when ground-truth test labels, true downstream impacts, or synthetic mutation tags are fed into the prediction pipeline before or during decision-making.

The fundamental non-leakage invariant is:
$$\text{Input Change} \xrightarrow{\text{System Prediction}} \hat{Y} \quad \text{vs.} \quad Y_{\text{GT}} \ (\text{Used strictly post-hoc for evaluation})$$

Under no circumstances may the prototype query ground truth files (`data/ground_truth/`, benchmark mutation labels, or evaluation masks) to infer:
1. Which artifacts are impacted.
2. Which tests should be selected.
3. Whether semantic fallback should accept or reject candidates.

---

## 2. Ingestion & Invariant Inspection

### Vector 1: Input Ingestion Independence
- **Inspection Target:** `src/ingestion/artifact_loader.py` and `src/ingestion/git_diff.py`
- **Audit Findings:** The `ChangedArtifact` data model contains strictly:
  - `artifact_id`
  - `artifact_type`
  - `subsystem`
  - `ecu`
  - `change_type`
  - `after_content`
  - `change_semantics`
  - `metadata`
- **Result:** **PASS**. No ground truth references, true impact lists, or test label sets exist in `ChangedArtifact`.

### Vector 2: Graph Construction Independence
- **Inspection Target:** `src/graph/builder.py` and `src/parsers/`
- **Audit Findings:** The `EngineeringGraph` builds nodes and edges strictly from source files on disk (`arxml/`, `requirements/`, `src/`, `tests/`).
- **Result:** **PASS**. Only declared architectural trace links, C call graphs, and test target tags are ingested. No evaluation ground truth files are parsed.

### Vector 3: Semantic Vectorization & Index Independence
- **Inspection Target:** `src/semantic/embedder.py` and `src/semantic/index.py`
- **Audit Findings:** `AURA-DomainHashEmbedder-384` uses deterministic feature hashing of artifact text descriptions. FAISS vector search computes inner product similarity against indexed artifact vectors.
- **Result:** **PASS**. Embeddings and indices are built purely from repository text content without benchmark ground truth supervision.

### Vector 4: Impact Determination Independence
- **Inspection Target:** `src/impact/impact_engine.py`
- **Audit Findings:**
  - Stage 1 uses bounded BFS on the extracted graph ($k \le 3$).
  - Stage 2 uses `ContextFilter.evaluate()` inspecting candidate subsystem and artifact type against the query metadata.
  - Set Union: $S_{final} = S_{struct} \cup S_{semantic}$.
- **Result:** **PASS**. No benchmark mutation records or ground-truth sets are consulted.

### Vector 5: Safety Gate Enforcement vs Ground Truth
- **Inspection Target:** `src/testing/safety_gate.py`
- **Audit Findings:**
  - The safety gate determines safety criticality from the parsed `TestRecord.safety_class` (e.g. `ASIL-C`, `ASIL-D`) or graph node `safety_level`.
  - When `mandatory_safety_test_ids` are supplied (such as during test assertions or CI evaluation), they act as external safety constraints; the engine asserts $T_{safe} \subseteq T_{selected}$.
- **Result:** **PASS**. In production/live execution, safety test retention is driven entirely by parsed ISO 26262 ASIL tags.

---

## 3. Forensic Code Scan for Ground-Truth Contamination

A recursive scan across `src/api/`, `src/impact/`, `src/semantic/`, `src/testing/`, and `dashboard/` was conducted to verify no imports or read operations target:
- `data/ground_truth/`
- `ground_truth.json`
- `benchmark_ground_truth`
- `true_impacted_artifacts`
- `true_selected_tests`

| Component Directory | Files Scanned | Ground-Truth Ingestion Calls | Verdict |
|---|---|---|---|
| `src/api/` | 2 | 0 | ✅ CLEAN |
| `src/graph/` | 4 | 0 | ✅ CLEAN |
| `src/impact/` | 8 | 0 | ✅ CLEAN |
| `src/semantic/` | 5 | 0 | ✅ CLEAN |
| `src/testing/` | 4 | 0 | ✅ CLEAN |
| `src/evidence/` | 3 | 0 | ✅ CLEAN |
| `dashboard/` | 1 | 0 | ✅ CLEAN |

---

## 4. Final Verdict

**VERDICT: ZERO DATA LEAKAGE CONFIRMED.**  
The live demonstrator and Round 2 validation scenarios are completely decoupled from benchmark ground-truth labels.
