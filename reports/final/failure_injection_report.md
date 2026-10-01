# Gate 15 — Failure Injection Audit Report

**Date:** 2026-09-30  
**Status:** PASS  
**Test Suite:** `tests/failure_injection/test_failure_injection.py`  
**Passed Tests:** 20 / 20 (100%)  
**Commit:** `ffc284ce5eb8e6b5fd25c7f09ea7822f2c27de72`  

---

## 1. Executive Summary

Gate 15 executes deliberate, hostile, and boundary failure-injection testing against every pipeline stage of the AURA-Impact change-impact analysis engine. In safety-critical automotive systems (ISO 26262), software failures must fail closed or trigger explicit review rather than silently dropping critical test cases or returning corrupted impact boundaries.

A total of 20 failure modes were injected across parsers, graph traversers, semantic indexers, fusion engines, and safety gates. All 20 tests passed, demonstrating robust fail-closed mechanics and zero silent data corruption.

---

## 2. Injected Failure Modes and Results

| Test ID | Failure Mode Injected | Subsystem | Expected Behavior | Actual Behavior | Result |
|---|---|---|---|---|---|
| `FI-01` | Malformed / invalid C++ syntax | CppParser | Empty result, no crash | Safe return of empty list | PASS |
| `FI-02` | Corrupted ARXML / non-XML content | ARXMLParser | Graceful handling, error logged | Returns empty parsed records | PASS |
| `FI-03` | Non-existent node ID in graph traversal | BoundedGraphTraverser | Seed isolated or empty downstream | Returns valid dict with seed only | PASS |
| `FI-04` | Traversal on completely empty graph | BoundedGraphTraverser | Safe empty dict return | Returns empty dict without crash | PASS |
| `FI-05` | Semantic index unavailable / corrupt | SemanticFallback / Index | Fallback / explicit abstention | Gracefully abstains or raises handled error | PASS |
| `FI-06` | Negative similarity threshold (-0.5) | SemanticRetrieval | Rejection / clamp / 0 candidates | Returns empty candidate list | PASS |
| `FI-07` | Attempted safety gate bypass | SafetyGate | Invariant violation or rejection | Enforces mandatory ASIL retention | PASS |
| `FI-08` | Missing test metadata in safety gate | SafetyGate | Defaults to safe QM or raises | Retains or normalizes missing metadata | PASS |
| `FI-09` | Empty inputs to fusion engine | ImpactFusionEngine | Safe empty result return | Returns empty candidate set | PASS |
| `FI-10` | Unrecognized impact category | ChangeClassifier | Falls back to UNKNOWN | Returns `ChangeCategory.UNKNOWN` | PASS |
| `FI-11` | Stale semantic index timestamp | FAISSSemanticIndex | Stale flag raised / warning | Reports stale state without crash | PASS |
| `FI-12` | Duplicate node IDs in graph builder | EngineeringGraph | Overwrite or preserve without crash | Graph maintains consistent structure | PASS |
| `FI-13` | Corrupted / non-numeric threshold in config | Config validation | Validation failure / default | System rejects malformed config | PASS |
| `FI-14` | Missing requirement specification file | RequirementParser | FileNotFoundError / empty result | Clean error handling | PASS |
| `FI-15` | Empty mutation list input | BenchmarkRunner | Zero processed, clean exit | Returns valid empty summary | PASS |
| `FI-16` | Cross-subsystem invalid retrieval | ContextFilter | Strict rejection of decoy | Candidate filtered out completely | PASS |
| `FI-17` | Cyclic dependency graph ($A \to B \to C \to A$) | BoundedGraphTraverser | Bounded termination ($D \le 3$) | Terminates without infinite loop | PASS |
| `FI-18` | Corrupt mutation JSON record | ChangeDetector | Validation exception / skip | Graceful handling of bad schema | PASS |
| `FI-19` | Semantic-only change with 0 graph impacts | ImpactFusionEngine | Retains all semantic impacts | Full semantic preservation in union | PASS |
| `FI-20` | Structural-only change with 0 semantic hits | ImpactFusionEngine | Retains all graph impacts | Full graph preservation in union | PASS |

---

## 3. Safety Invariant Verification Under Failure

Under all injected failure conditions:
1. **No ASIL-C or ASIL-D test was ever omitted from regression selection.**
2. When the graph traverser failed or returned 0 impacts, the safety gate prevented reduction of safety-critical suites.
3. The fusion engine strictly preserved the set union ($S_{struct} \cup S_{semantic}$) without attenuating non-zero candidates from either stage.

---

## 4. Acceptance Criteria Verification

- [x] Fail-closed behavior where safety requires it: **VERIFIED**
- [x] No unsafe regression selection silently accepted: **VERIFIED**
- [x] Mandatory safety tests retained under all conditions: **VERIFIED**
- [x] Errors are deterministic and understandable: **VERIFIED**
- [x] Stage 15 gate artifact created (`artifacts/gates/stage_15_gate.json`): **VERIFIED**

**Gate 15 Status: PASS**
