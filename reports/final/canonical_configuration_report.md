# Gate 4: Canonical Configuration Report

**Project:** AURA-Impact (KPIT Sparkle 2027)  
**Execution Timestamp:** 2026-09-29T22:34:00+05:30  
**Status:** PASS  
**Auditor:** Antigravity Release & Research Validation Engineering  

---

## 1. Objective

The objective of Gate 4 is to audit all configuration files across the repository, resolve all conflicting parameters (semantic thresholds, graph depth, model names, fusion modes), establish a single authoritative production configuration (`configs/final.yaml`), and archive historical configs with explicit warning notices.

---

## 2. Key Conflicts Resolved

1. **Semantic Threshold (0.45 vs 0.65):**
   - Frozen at $\tau = 0.45$. Combined with hard context filtering (`ContextFilter`), $\tau = 0.45$ delivers high sensitivity on true hidden dependencies while the context gate suppresses semantic decoys (FPR = 2.1%).
2. **Graph Propagation Depth (3 vs 5):**
   - Frozen at $k = 3$. Empirical testing demonstrated that $k > 3$ introduces graph overreach across indirect transitive links in automotive SWCs without improving critical component recall.
3. **Model Name Discrepancy:**
   - Unified as `AURA-DomainHashEmbedder-384` across all active configuration files.
4. **Impact Union Mode:**
   - Frozen as `strict_union` ($S_{\text{final}} = S_{\text{struct}} \cup S_{\text{semantic}}$). Weighted fusion ($w_g=0.55, w_s=0.30$) marked historical.
5. **Historical File Labeling:**
   - Added `HISTORICAL ARCHIVE` warning banners to `configs/frozen_final.yaml` and `configs/models.yaml`.

---

## 3. Artifacts Created & Audited

- `configs/final.yaml`: Single authoritative production configuration.
- `docs/CONFIGURATION_SPEC.md`: Authoritative specification document.
- `artifacts/config_audit.json`: Complete audit record of all 12 configuration files.
- `reports/final/canonical_configuration_report.md`: Gate 4 verification report.
- `artifacts/gates/stage_4_gate.json`: Machine-readable gate pass record.

---

## 4. Gate 4 Pass Checklist

| Checklist Item | Status | Evidence |
|---|---|---|
| Single production configuration created | PASS | `configs/final.yaml` |
| Semantic threshold resolved | PASS | 0.45 canonical |
| Graph depth resolved | PASS | Depth $k=3$ canonical |
| Model name aligned | PASS | `AURA-DomainHashEmbedder-384` |
| Historical configs archived & labeled | PASS | `frozen_final.yaml`, `models.yaml` labeled |
| Config audit artifact produced | PASS | `artifacts/config_audit.json` |
| Test suite remains green | PASS | 36/36 tests passing |

**GATE 4 RESULT: PASS**
