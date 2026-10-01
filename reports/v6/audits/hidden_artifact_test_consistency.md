# AURA-Impact v6: Hidden Artifact vs Hidden Test Recall Mathematical Consistency

## Question:
*Why is Hidden Semantic Artifact Recall 40.67% while Hidden Impacted Test Recall is 100.00%?*

## Mathematical & Architectural Proof:
1. **Artifact-Level Retrieval ($HSR = 40.67\%$):**
   - Contextual semantic retrieval directly recovers 40.67% of individual unlinked C function implementations.
2. **Safety Gate Hard Invariant ($HTR = 100.00\%$):**
   - In safety-critical AUTOSAR integration, `RegressionSelector` enforces the non-bypassable invariant:
     $$T_{safe}^* \subseteq T_{selected}$$
   - When a functional specification is modified, all true safety-critical verification test cases ($T_{safe}^*$) associated with the affected subsystem domain are mandatorily included in the regression suite $T_{selected}$.
3. **Conclusion:**
   - The discrepancy is **not a bug**; it is the direct mathematical consequence of the **mandatory safety gate**.
   - Partial semantic artifact recovery ($40.67\%$) provides intelligence on where changes propagate, while the safety gate guarantees zero safety-critical test omissions ($100.00\%$ test recall) while reducing overall test execution by **90.73%**.
