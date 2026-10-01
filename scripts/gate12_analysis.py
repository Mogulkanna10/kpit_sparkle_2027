"""
Gate 12 — Data Analysis Script
Independently computes fingerprints, metric values, and structural diagnostics.
"""
import pandas as pd
import json
import hashlib
import numpy as np
from pathlib import Path

ROOT = Path(".")

# ── 1. Dataset fingerprint (independent of runner) ──────────────────────────
with open("data/mutations/all_mutations.json", "r") as f:
    muts = json.load(f)
with open("data/ground_truth/all_ground_truth.json", "r") as f:
    gts = json.load(f)

ids_mut = sorted(m["mutation_id"] for m in muts)
ids_gt  = sorted(g["mutation_id"] for g in gts)
fp_mut = hashlib.sha256("|".join(ids_mut).encode()).hexdigest()[:16]
fp_gt  = hashlib.sha256("|".join(ids_gt).encode()).hexdigest()[:16]

print("=== SECTION 1: DATASET INTEGRITY ===")
print(f"  Mutation count: {len(muts)}")
print(f"  Ground-truth count: {len(gts)}")
print(f"  Mutation fingerprint (SHA-256[:16]): {fp_mut}")
print(f"  GT fingerprint (SHA-256[:16]): {fp_gt}")
projects = sorted(set(m["project_id"] for m in muts))
print(f"  Projects: {projects}")
print(f"  Mutations per project: {dict((p, sum(1 for m in muts if m['project_id']==p)) for p in projects)}")

# Check all mutation IDs present in GT
mut_ids = set(ids_mut)
gt_ids  = set(ids_gt)
print(f"  Mutation IDs in GT: {len(mut_ids & gt_ids)} (expected {len(muts)})")
print(f"  Mutations missing from GT: {mut_ids - gt_ids}")
print(f"  Extra GT records: {gt_ids - mut_ids}")
print()

# ── 2. Impact CSV analysis ───────────────────────────────────────────────────
impact = pd.read_csv("benchmark/final/outputs/impact_results.csv")
reg    = pd.read_csv("benchmark/final/outputs/regression_results.csv")

print("=== SECTION 2: IMPACT CSV STRUCTURE ===")
print(f"  Impact rows: {len(impact)}")
print(f"  Methods in impact CSV: {sorted(impact.method.unique())}")
print(f"  Mutations in impact CSV: {impact.mutation_id.nunique()}")
print()

print("  Mean metrics per method:")
g = impact.groupby("method").agg(
    recall_mean=("recall","mean"),
    precision_mean=("precision","mean"),
    f1_mean=("f1","mean"),
    n=("recall","count")
).round(4)
print(g.to_string())
print()

# ── 3. CRITICAL: Are AURA and Graph_Only producing identical recall? ─────────
print("=== SECTION 3: AURA vs GRAPH_ONLY RECALL ANALYSIS ===")
aura  = impact[impact.method=="Hybrid_AURA_Routed"][["mutation_id","recall","precision","f1"]].rename(
    columns={"recall":"aura_rec","precision":"aura_prec","f1":"aura_f1"})
graph = impact[impact.method=="Graph_Only"][["mutation_id","recall","precision","f1"]].rename(
    columns={"recall":"graph_rec","precision":"graph_prec","f1":"graph_f1"})
m = pd.merge(aura, graph, on="mutation_id")
m["rec_diff"]  = (m.aura_rec  - m.graph_rec).abs()
m["prec_diff"] = (m.aura_prec - m.graph_prec).abs()
m["f1_diff"]   = (m.aura_f1   - m.graph_f1).abs()
print(f"  AURA recall mean:  {m.aura_rec.mean():.6f}")
print(f"  Graph recall mean: {m.graph_rec.mean():.6f}")
print(f"  Max |aura_rec - graph_rec|: {m.rec_diff.max():.6f}")
print(f"  Rows where aura_rec > graph_rec: {(m.aura_rec > m.graph_rec).sum()}")
print(f"  Rows where aura_rec < graph_rec: {(m.aura_rec < m.graph_rec).sum()}")
print(f"  Rows where aura_rec == graph_rec: {(m.aura_rec == m.graph_rec).sum()}")
print()
print(f"  AURA precision mean:  {m.aura_prec.mean():.6f}")
print(f"  Graph precision mean: {m.graph_prec.mean():.6f}")
print(f"  Rows where aura_prec > graph_prec: {(m.aura_prec > m.graph_prec).sum()}")
print(f"  Rows where aura_prec < graph_prec: {(m.aura_prec < m.graph_prec).sum()}")
print()

# ── 4. Manual recall formula check (spot check on 5 mutations) ──────────────
print("=== SECTION 4: MANUAL RECALL FORMULA VERIFICATION ===")
gt_map = {g["mutation_id"]: g for g in gts}
sample_rows = impact[impact.method=="Hybrid_AURA_Routed"].head(5)
for _, row in sample_rows.iterrows():
    mid = row.mutation_id
    gt = gt_map.get(mid, {})
    true_arts = set(gt.get("true_impacted_artifacts", []))
    true_count = len(true_arts)
    csv_recall = row.recall
    print(f"  {mid}: true_count={true_count}, csv_recall={csv_recall:.4f}")

print()

# ── 5. Test reduction independent verification ──────────────────────────────
print("=== SECTION 5: TEST REDUCTION VERIFICATION ===")
aura_reg = reg[reg.method=="Hybrid_AURA_Routed"]
mean_total = aura_reg.total_tests.mean()
mean_selected = aura_reg.selected_tests.mean()
mean_reduction_formula = 1.0 - mean_selected / mean_total
mean_reduction_csv = aura_reg.test_reduction.mean()
print(f"  Mean total_tests: {mean_total:.2f}")
print(f"  Mean selected_tests: {mean_selected:.2f}")
print(f"  Computed reduction: {mean_reduction_formula*100:.2f}%")
print(f"  CSV reduction mean: {mean_reduction_csv*100:.2f}%")
print()

# ── 6. Safety metric separation ─────────────────────────────────────────────
print("=== SECTION 6: SAFETY METRICS SEPARATION ===")
# Invariant: rows where safety_recall==1.0
inv_pass = (aura_reg.safety_recall == 1.0).sum()
inv_total = len(aura_reg)
print(f"  Safety INVARIANT (T_safe SUBSET T_selected): {inv_pass}/{inv_total} = {inv_pass/inv_total*100:.2f}%")

# Safety-critical discovery recall: selected_safety / true_safety
aura_reg2 = aura_reg.copy()
aura_reg2["sc_disc_recall"] = aura_reg2.selected_safety_tests / aura_reg2.true_safety_tests.replace(0, np.nan)
sc_disc_mean = aura_reg2.sc_disc_recall.mean()
sc_disc_nonzero = (aura_reg2.true_safety_tests > 0).sum()
print(f"  Rows with true_safety_tests > 0: {sc_disc_nonzero}")
print(f"  Safety-critical DISCOVERY recall (selected_sc/true_sc): {sc_disc_mean:.4f}")
print()

# ── 7. Historical 0.4805 source ─────────────────────────────────────────────
print("=== SECTION 7: HISTORICAL 0.4805 RECALL SOURCE ===")
hist_report = Path("reports/final_report.md")
if hist_report.exists():
    txt = hist_report.read_text(encoding="utf-8", errors="replace")
    for line in txt.splitlines():
        if "0.4805" in line or "48.05" in line or "AURA" in line.upper():
            print(f"  {line.strip()}")
else:
    print("  reports/final_report.md not found")

print()

# ── 8. Configuration values in runner vs final.yaml ─────────────────────────
print("=== SECTION 8: CONFIG CROSSCHECK ===")
import yaml
with open("configs/final.yaml","r") as f:
    cfg = yaml.safe_load(f)
print(f"  configs/final.yaml semantic threshold: {cfg['semantic']['threshold']}")
print(f"  configs/final.yaml graph max_depth: {cfg['graph']['max_depth']}")
print(f"  configs/final.yaml model: {cfg['semantic']['model']}")
print(f"  configs/final.yaml top_k: {cfg['semantic']['top_k']}")
print(f"  configs/final.yaml seed: {cfg['master_seed']}")

from benchmark.final.config import (
    MASTER_SEED, MAX_GRAPH_DEPTH, TOP_K_SEMANTIC, THRESHOLD_GRID
)
print(f"  benchmark/final/config.py MASTER_SEED: {MASTER_SEED}")
print(f"  benchmark/final/config.py MAX_GRAPH_DEPTH: {MAX_GRAPH_DEPTH}")
print(f"  benchmark/final/config.py TOP_K_SEMANTIC: {TOP_K_SEMANTIC}")
print(f"  benchmark/final/config.py calibrated_threshold (from runner): see artifact")
print()

print("=== DONE ===")
