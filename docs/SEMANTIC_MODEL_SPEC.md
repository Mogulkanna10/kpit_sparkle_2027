# AURA-Impact Semantic Model Specification

**Model Name:** AURA-DomainHashEmbedder-384  
**Architecture:** Deterministic Automotive Domain-Concept Hash Vectorizer  
**Status:** FROZEN & CANONICAL  
**Auditor:** Antigravity Release & Research Validation Engineering  

---

## 1. Specification Overview

AURA-Impact uses a dedicated, lightweight, fully deterministic domain-concept hash vectorizer designated as **`AURA-DomainHashEmbedder-384`**.

This replaces earlier informal references to "BGE-M3" or "all-MiniLM-L6-v2". No unverified neural model weights are downloaded or executed in the canonical pipeline.

### Why Deterministic Domain Hashing over Black-Box Neural Models?
1. **Safety & Determinism:** In safety-critical automotive environments (ISO 26262), impact analysis must be 100% reproducible across different compiler versions, CPU architectures, and CI operating systems. Neural floating-point matrix multiplications (BLAS/CUDA) can exhibit non-deterministic bit drift.
2. **Zero External Dependencies / True Air-Gapped Operation:** Eliminates the requirement to download 1.5 GB HuggingFace weights or depend on PyTorch/CUDA runtimes in restricted OEM CI environments.
3. **Microsecond Latency:** Query embedding completes in under 0.05 ms per artifact, compared to 15–50 ms for neural transformers on CPU.
4. **Targeted Domain Ontology Projection:** Infuses explicit automotive domain semantics (e.g., mapping `AEB` to collision avoidance, deceleration, and braking concepts).

---

## 2. Technical Formulation

Given input artifact text $T$:
1. **Text Normalization:** Lowercased and tokenized into alphanumeric words $w \in W$.
2. **Primary Token Hashing:** Each token is hashed using MD5 into dimension space:
   $$h_1(w) = \text{int}(\text{MD5}(w)) \pmod{384}$$
   $$\vec{v}[h_1(w)] \mathrel{+}= 1.0$$
3. **Subword N-Gram Hashing:** For subword robustness against compounding and abbreviations, character 3-grams are hashed using SHA-256:
   $$h_{\text{sub}}(s) = \text{int}(\text{SHA256}(s)) \pmod{384}$$
   $$\vec{v}[h_{\text{sub}}(s)] \mathrel{+}= 0.35$$
4. **Domain Ontology Projection:** If token matches calibrated automotive concept clusters (AEB, ACC, BMS, Powertrain, Body, Safety), concept anchors are reinforced:
   $$h_c = \text{int}(\text{MD5}(\text{concept})) \pmod{384}$$
   $$\vec{v}[h_c] \mathrel{+}= 1.50$$
5. **L2 Unit Hypersphere Normalization:**
   $$\vec{v}_{\text{norm}} = \frac{\vec{v}}{\|\vec{v}\|_2}$$
   If $\|\vec{v}\|_2 < 10^{-6}$, fallback vector is $\vec{e}_1 = [1.0, 0.0, \dots, 0.0]^T$.

---

## 3. Dimensionality & Indexing

- **Output Dimension:** $d = 384$
- **Data Type:** 32-bit floating point (`numpy.float32`)
- **Index Engine:** `FAISSSemanticIndex` using `faiss.IndexFlatIP` (Inner Product on L2-normalized vectors is exact Cosine Similarity).
- **Fallback Index:** Deterministic NumPy dot-product matrix multiplication when native FAISS-CPU library is absent.
- **Default Similarity Threshold:** $\tau = 0.45$

---

## 4. Verification & Testing

The model identity is formally verified by `tests/semantic/test_model_identity.py`:
- `test_actual_model_identity`: Confirms `embedder.model_name == "AURA-DomainHashEmbedder-384"`, `embedder.is_neural is False`.
- `test_actual_dimension_and_normalization`: Verifies $384$-D shape and strict $\|\vec{v}\| = 1.0 \pm 10^{-4}$.
- `test_deterministic_reproducibility`: Proves exact bit-for-bit identity across instances.
- `test_actual_index_and_similarity`: Proves cosine similarity ordering and boundary $[-1.0, +1.0]$.
- `test_configuration_identity_alignment`: Proves `configs/canonical_architecture.yaml` references `AURA-DomainHashEmbedder-384`.
- `test_fallback_behavior_on_empty_text`: Confirms graceful unit fallback on empty strings.
