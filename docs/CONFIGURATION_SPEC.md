# AURA-Impact Authoritative Configuration Specification

**Authoritative File:** `configs/final.yaml`  
**Architecture:** Locked Architecture B  
**Status:** FROZEN & AUTHORITATIVE  
**Auditor:** Antigravity Release & Research Validation Engineering  

---

## 1. Specification Purpose

This document defines the single authoritative production configuration controlling the AURA-Impact change impact analysis engine. It supersedes all historical, exploratory, and ad-hoc configuration files.

---

## 2. Canonical Parameter Registry

| Parameter Key | Canonical Value | Type | Purpose | Historical Alternatives Resolved |
|---|---|---|---|---|
| `version` | `1.0.0-PROD` | String | Release version | `2.0.0-HISTORICAL` |
| `master_seed` | `42` | Integer | Deterministic PRNG seed | N/A |
| `graph.enabled` | `true` | Boolean | Activates Stage 1 graph analysis | N/A |
| `graph.max_depth` | `3` | Integer | Maximum BFS traversal depth | $k=5$ (rejected: caused overreach) |
| `graph.direction` | `forward` | String | Dependency propagation direction | N/A |
| `graph.deterministic_confidence` | `1.0` | Float | Confidence on explicit edges | N/A |
| `semantic.enabled` | `true` | Boolean | Activates Stage 2 semantic fallback | N/A |
| `semantic.model` | `AURA-DomainHashEmbedder-384` | String | Vectorizer model name | `BGE-M3`, `all-MiniLM-L6-v2` (eliminated) |
| `semantic.embedding_dimension` | `384` | Integer | Hypersphere embedding dimensions | N/A |
| `semantic.similarity_metric` | `cosine` | String | Inner Product on normalized vectors | N/A |
| `semantic.threshold` | `0.45` | Float | Fallback candidate acceptance cutoff | $0.65, 0.80$ (reconciled with ContextFilter) |
| `semantic.top_k` | `10` | Integer | Max candidate retrievals per query | N/A |
| `semantic.fallback_on_incomplete_structural` | `true` | Boolean | Triggers Stage 2 only when Stage 1 is empty | N/A |
| `semantic.context_constraints.enforce_subsystem_isolation` | `true` | Boolean | Drops candidates across subsystem boundaries | N/A |
| `semantic.context_constraints.min_context_score` | `0.50` | Float | Minimum metadata match score | N/A |
| `impact_union.mode` | `strict_union` | String | $S_{\text{final}} = S_{\text{struct}} \cup S_{\text{semantic}}$ | `weighted_fusion` ($w_g=0.55, w_s=0.30$) (eliminated) |
| `safety_gate.mandatory` | `true` | Boolean | Enforces $T_{\text{safe}} \subseteq T_{\text{selected}}$ | N/A |
| `safety_gate.fail_mode` | `FAIL_CLOSED` | String | Raises exception on invariant violation | N/A |
| `safety_gate.critical_levels` | `[ASIL_C, ASIL_D]` | List[String] | Safety classifications requiring retention | N/A |

---

## 3. Configuration Hierarchy & Precedence

1. **Production Runtime:**
   `configs/final.yaml` governs execution.
2. **Subsystem Defaults:**
   `configs/architecture.yaml`, `configs/graph.yaml`, `configs/semantic.yaml`, `configs/safety.yaml` are synchronized to match `configs/final.yaml`.
3. **Historical / Archived Configurations:**
   `configs/frozen_final.yaml`, `configs/models.yaml`, `configs/benchmark.yaml` are strictly labeled `HISTORICAL ARCHIVE` and are never loaded by the production pipeline.
