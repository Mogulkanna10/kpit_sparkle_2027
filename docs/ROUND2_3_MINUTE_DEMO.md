# AURA-IMPACT: 3-MINUTE JUDGE PRESENTATION & LIVE DEMO SCRIPT

**Document Reference:** `docs/ROUND2_3_MINUTE_DEMO.md`  
**Target Event:** KPIT Sparkle Round 2 Technical Evaluation  
**Presentation Time:** 3 Minutes (180 Seconds)  
**Presenter Role:** Lead Engineering Architect

---

### Timing Breakdown at a Glance

| Time Slot | Segment | Visual Display | Key Talking Point |
|:---|:---|:---|:---|
| **0:00 – 0:20** | The Problem | Title slide / System diagram | CI bottleneck & traceability breakdown in AUTOSAR integration |
| **0:20 – 0:45** | Existing Approaches | Architecture comparison | Graph-only misses broken links; LLM/embeddings hallucinate |
| **0:45 – 1:15** | AURA Architecture | Interactive Dashboard Tab 1 | Two-stage hybrid: Bounded Graph + Context Gate + Safety Gate |
| **1:15 – 2:00** | Live Hidden Dependency Demo | Dashboard Tab 2 | Concrete recovery of unlinked radar-fusion runnable in 0.31 ms |
| **2:00 – 2:25** | Decoy Rejection + Evidence | Dashboard Tab 2 & Tab 4 | Context gate blocks body controller decoy; auditable evidence |
| **2:25 – 2:45** | Regression Suite Reduction | Dashboard Tab 1 | 96% test reduction on 100-test suite; huge CI acceleration |
| **2:45 – 3:00** | Safety Invariant + Benchmark | Dashboard Tab 5 & Tab 1 | 100% ASIL-D retention; 63.11% recall benchmark validation |

---

### Minute-by-Minute Script

#### [0:00 – 0:20] The Problem: The AUTOSAR Integration Crisis
> *"Respected KPIT judges, modern software-defined vehicles contain over 100 ECUs and tens of millions of lines of code. When an automotive engineer modifies a single requirement or AUTOSAR software component, predicting the ripple effect is almost impossible.*
> 
> *In daily CI/CD integration, explicit traceability links frequently break or lag behind development. Teams face an impossible dilemma: either run full 12-hour Hardware-in-the-Loop test suites on every commit, creating massive integration bottlenecks, or cherry-pick tests manually and risk catastrophic safety escapes."*

---

#### [0:20 – 0:45] Existing Approaches: Why Both Graphs and AI Fail
> *"Today's industry approaches fail on two opposite extremes:*
> 1. *Deterministic Traceability Graphs (like Polarion or DOORS) are completely blind when explicit XML links are missing. If an edge isn't drawn, impact analysis reports zero dependencies.*
> 2. *Modern Generative AI and vector search suffer from semantic hallucinations. When searching code by text similarity, an LLM retrieves brake lights in the Body domain just because they mention 'deceleration,' flooding engineers with false positives.*
> 
> *Automotive engineering cannot afford either graph blindness or semantic hallucination."*

---

#### [0:45 – 1:15] AURA-Impact Architecture: Deterministic Hybrid Intelligence
*(Switch to Dashboard UI: `http://localhost:8501`)*
> *"Our solution is AURA-Impact, built on a frozen three-stage deterministic architecture:*
> 
> *First, we execute Bounded Deterministic Graph Traversal up to depth 3 to capture all explicit links.*
> 
> *Second, when traceability is incomplete, we trigger our domain-aware embedder (`AURA-DomainHashEmbedder-384`). But we do NOT trust raw embeddings alone. Every candidate must pass our rigorous **Architectural Context Gate**, matching Subsystem, ECU, and Interface compatibility.*
> 
> *Third, our Non-Bypassable Safety Gate mathematically guarantees that ISO 26262 ASIL-C and ASIL-D test cases are never excluded by optimization."*

---

#### [1:15 – 2:00] Live Demonstration: Graph-Blind Hidden Dependency
*(Select `SCENARIO_02: Hidden Semantic Dependency` in the sidebar and click **Run Impact Analysis**; switch to **Tab 2: Core Differentiators**)*
> *"Let's watch this live in our demonstration environment.*
> 
> *Here, an engineer modifies `REQ_AEB_SENSOR_001`—an ADAS radar-camera sensor fusion requirement. Notice that the explicit `.arxml` link to the implementation component is missing.*
> 
> *Look at Stage 1 on the left: Graph traversal finds **ZERO** impacted artifacts. A conventional tool stops here, missing the bug.*
> 
> *Now look at Stage 2 in the middle: AURA-Impact’s semantic retriever recovers `SWC_AEB_FusedTargetHandler` with 0.88 similarity. Because the candidate shares the `ADAS` subsystem and `ECU_ADAS_Front`, the context filter approves it. In 0.31 milliseconds, we caught the hidden dependency that graph tools missed!"*

---

#### [2:00 – 2:25] Live Demonstration: Semantic Decoy Rejection
*(Scroll down in Tab 2 to the **Semantic Decoy Rejection Inspector**)*
> *"Now look at how we defeat semantic hallucination.*
> 
> *Here is an adversarial decoy: `SWC_BodyLightController` in the Body domain. Because it contains words like 'deceleration brake light warning,' raw embedding similarity gives it a high score of 0.78.*
> 
> *An LLM would flag this as an impact. But AURA-Impact's Context Filter inspects the subsystem metadata, sees a mismatch between `ADAS` and `Body_Electronics`, and immediately **REJECTS** it.*
> 
> *Every single decision is logged with an explainable evidence trail available for ISO 26262 audits in Tab 6."*

---

#### [2:25 – 2:45] Regression Suite Optimization: Slashing CI Cycles
*(Click **Tab 1: Executive Summary**)*
> *"What does this mean for testing?*
> 
> *In this realistic 100-test verification suite, instead of executing all 100 tests, AURA-Impact selects precisely the 4 tests mapped to the impacted interface and component.*
> 
> *That is a **96.0% reduction** in test execution overhead. In an overnight HIL environment, this turns an 8-hour test run into a 20-minute targeted smoke run."*

---

#### [2:45 – 3:00] Safety Invariant & Validated Benchmark
*(Click **Tab 5: Safety Gate Invariant**)*
> *"Most importantly: **Safety is non-negotiable**.*
> 
> *Our Safety Gate formally enforces the invariant: $T_{safe} \subseteq T_{selected}$. Even if an optimizer tries to deselect safety tests, the gate blocks it. 100% of mandatory ASIL-D tests are retained.*
> 
> *In our 150-scenario validated research benchmark, AURA-Impact achieved **63.11% artifact recall**, **82.29% test reduction**, and **100% safety invariant retention** at **0.79 milliseconds**.*
> 
> *AURA-Impact is fast, offline, explainable, and ready to transform automotive software integration. Thank you, judges!"*
