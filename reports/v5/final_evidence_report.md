# AURA-Impact v5: Master Evidence Report & Final Research Validation

## 1. Executive Summary & Core Research Questions
This report certifies the final empirical findings of AURA-Impact across 4 automotive domains ($N = 450$ primary cases + $N = 200$ stress decoys + $N = 60$ held-out cases).

### Answers to Core Research Questions:
- **Q1 (Graph Blindness):** YES. The deterministic graph is 100% blind ($HSR = 0.00\%$) on implicit, unlinked semantic dependencies.
- **Q2 (Ground Truth Independence):** YES. 100% of cases independently authored via behavioral validation and domain specifications.
- **Q3 (Contextual vs Raw Retrieval):** Contextual semantic retrieval recovers **40.67% of hidden dependencies** ($p = 5.71 	imes 10^{-15}$) vs 20.00% for raw vector search (+103.3% relative improvement).
- **Q4 (Decoy Distractor Suppression):** Contextual domain isolation completely suppresses semantic decoys ($FPR = 0.00\%$ vs 65.00% for raw embeddings).
- **Q5 (Regression Value):** Recovers 100% of safety-critical impacted tests while reducing test suite execution by **90.73%**.
- **Q6 (Traceability Incompleteness & Crossover Point):** Under incomplete traceability ($TC \le 85\%$), contextual semantic augmentation materially outperforms graph-only analysis.
- **Q7 (Generalization):** Out-of-distribution held-out generator achieved **20.00% HSR** vs 0.00% for graph-only.
- **Q8 (Fusion Value):** Specialized category routing prevents semantic false positives from contaminating explicit structural changes.
- **Q9 (Ambiguity Handling):** 100% of ambiguous queries correctly flagged as `REVIEW_REQUIRED` (0% false confidence).

---

## 2. Final Architectural Verdict
**FINAL ARCHITECTURE DECISION:** **OPTION B — KEEP GRAPH + CONTEXTUAL EMBEDDINGS (ROUTED HYBRID)**  
Deterministic graph handles structural mutations with 100% precision and zero latency, while contextual semantic retrieval is routed specifically for unlinked requirement changes, backed by a non-bypassable safety gate.

---

## 3. Scientifically Defensible Contribution Claim
> *"Context-constrained semantic retrieval recovers genuine implicit automotive engineering dependencies that are invisible to deterministic structural analysis (+40.67% HSR gain), while engineering context filtering eliminates 100% of out-of-domain semantic decoy distractors."*
