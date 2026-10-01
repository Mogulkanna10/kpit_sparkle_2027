"""
AURA-Impact: Generation script for Round 2 technical details & research evidence visual assets.
Generates publication-quality SVGs and high-DPI PNGs for KPIT Sparkle Round 2 submission PPT.
Adheres strictly to canonical benchmark results and visual design requirements.
"""

import os
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle
import numpy as np

# Output directories
BASE_DIR = os.path.join("round2_submission", "technical_details")
CHARTS_DIR = os.path.join(BASE_DIR, "charts")
ARCH_DIR = os.path.join(BASE_DIR, "architecture")
RESEARCH_DIR = os.path.join(BASE_DIR, "research")
PROTOTYPE_DIR = os.path.join(BASE_DIR, "prototype")
TABLES_DIR = os.path.join(BASE_DIR, "tables")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

for d in [CHARTS_DIR, ARCH_DIR, RESEARCH_DIR, PROTOTYPE_DIR, TABLES_DIR, REPORTS_DIR]:
    os.makedirs(d, exist_ok=True)

# Aesthetic color palette (Clean, modern engineering palette: Dark Navy, Vibrant Teal, Crimson, Slate)
COLOR_NAVY = "#0F172A"       # Slate 900
COLOR_SLATE = "#475569"      # Slate 600
COLOR_LIGHT_BG = "#F8FAFC"   # Slate 50
COLOR_BORDER = "#CBD5E1"     # Slate 300
COLOR_PRIMARY = "#0284C7"    # Sky 600
COLOR_AURA = "#0D9488"       # Teal 600 (AURA brand)
COLOR_GRAPH = "#2563EB"      # Blue 600
COLOR_EMBED = "#7C3AED"      # Purple 600
COLOR_KEYWORD = "#64748B"    # Slate 500
COLOR_SUCCESS = "#16A34A"    # Green 600
COLOR_ALERT = "#DC2626"      # Red 600
COLOR_AMBER = "#D97706"      # Amber 600
COLOR_CARD = "#FFFFFF"

# Global font styling
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['text.color'] = COLOR_NAVY
plt.rcParams['axes.labelcolor'] = COLOR_NAVY
plt.rcParams['xtick.color'] = COLOR_NAVY
plt.rcParams['ytick.color'] = COLOR_NAVY


# ==============================================================================
# 1. CHART: Artifact F1 Comparison
# ==============================================================================
def generate_f1_chart():
    fig, ax = plt.subplots(figsize=(8, 5.2), dpi=300)
    fig.patch.set_facecolor(COLOR_CARD)
    ax.set_facecolor(COLOR_CARD)

    methods = ["Keyword Match", "Embedding-Only", "Graph-Only", "AURA-Impact"]
    f1_scores = [0.1485, 0.3114, 0.4557, 0.5503]
    colors = [COLOR_KEYWORD, COLOR_EMBED, COLOR_GRAPH, COLOR_AURA]

    bars = ax.bar(methods, f1_scores, color=colors, width=0.55, edgecolor=COLOR_NAVY, linewidth=1.2, zorder=3)

    for bar, val in zip(bars, f1_scores):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.015, f"{val:.4f}",
                ha='center', va='bottom', fontsize=12, fontweight='bold', color=COLOR_NAVY)

    ax.set_ylim(0, 0.68)
    ax.set_ylabel("Artifact F1 Score", fontsize=12, fontweight='bold', labelpad=10)
    ax.set_title("Artifact Impact Prediction — F1 Comparison", fontsize=15, fontweight='bold', pad=18)
    ax.text(0.5, 1.02, "Canonical AURA-Impact benchmark (150 evaluation mutations)",
            transform=ax.transAxes, ha='center', fontsize=10, color=COLOR_SLATE)

    # Note
    ax.text(0.5, -0.15, "Note: Evaluated across 150 automated mutation batches on formal benchmark.",
            transform=ax.transAxes, ha='center', fontsize=9, color=COLOR_SLATE, style='italic')

    ax.grid(axis='y', linestyle='--', alpha=0.4, color=COLOR_BORDER, zorder=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(COLOR_BORDER)
    ax.spines['bottom'].set_color(COLOR_NAVY)

    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "artifact_f1_comparison.png"), dpi=300)
    plt.savefig(os.path.join(CHARTS_DIR, "artifact_f1_comparison.svg"))
    plt.close()
    print("Generated: artifact_f1_comparison")


# ==============================================================================
# 2. CHART: Recall vs Precision Comparison
# ==============================================================================
def generate_recall_precision_chart():
    fig, ax = plt.subplots(figsize=(9, 5.4), dpi=300)
    fig.patch.set_facecolor(COLOR_CARD)
    ax.set_facecolor(COLOR_CARD)

    methods = ["Keyword Match", "Embedding-Only", "Graph-Only", "AURA-Impact"]
    recalls = [42.82, 42.45, 63.07, 63.11]
    precisions = [18.97, 66.78, 54.43, 54.92]

    x = np.arange(len(methods))
    width = 0.35

    rects1 = ax.bar(x - width/2, recalls, width, label='Recall (%)',
                    color=COLOR_AURA, edgecolor=COLOR_NAVY, linewidth=1.1, zorder=3)
    rects2 = ax.bar(x + width/2, precisions, width, label='Precision (%)',
                    color=COLOR_PRIMARY, edgecolor=COLOR_NAVY, linewidth=1.1, zorder=3)

    for r in rects1:
        h = r.get_height()
        ax.text(r.get_x() + r.get_width()/2., h + 1.2, f"{h:.1f}%", ha='center', va='bottom', fontsize=10, fontweight='bold')
    for r in rects2:
        h = r.get_height()
        ax.text(r.get_x() + r.get_width()/2., h + 1.2, f"{h:.1f}%", ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax.set_ylabel("Metric Value (%)", fontsize=12, fontweight='bold', labelpad=10)
    ax.set_title("Impact Prediction: Recall vs Precision", fontsize=15, fontweight='bold', pad=18)
    ax.text(0.5, 1.02, "Evaluating retrieval trade-offs across canonical methods",
            transform=ax.transAxes, ha='center', fontsize=10, color=COLOR_SLATE)

    ax.set_xticks(x)
    ax.set_xticklabels(methods, fontsize=11, fontweight='medium')
    ax.set_ylim(0, 80)
    ax.legend(frameon=True, facecolor=COLOR_CARD, edgecolor=COLOR_BORDER, loc='upper left', fontsize=10)

    ax.grid(axis='y', linestyle='--', alpha=0.4, color=COLOR_BORDER, zorder=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(COLOR_BORDER)
    ax.spines['bottom'].set_color(COLOR_NAVY)

    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "recall_precision_comparison.png"), dpi=300)
    plt.savefig(os.path.join(CHARTS_DIR, "recall_precision_comparison.svg"))
    plt.close()
    print("Generated: recall_precision_comparison")


# ==============================================================================
# 3. CHART: Regression Test Reduction
# ==============================================================================
def generate_regression_reduction_chart():
    fig, ax = plt.subplots(figsize=(8, 5.2), dpi=300)
    fig.patch.set_facecolor(COLOR_CARD)
    ax.set_facecolor(COLOR_CARD)

    categories = ["Full Baseline Suite", "AURA Selected Suite"]
    values = [100.0, 17.71]
    colors = [COLOR_SLATE, COLOR_AURA]

    bars = ax.bar(categories, values, color=colors, width=0.45, edgecolor=COLOR_NAVY, linewidth=1.2, zorder=3)

    ax.text(bars[0].get_x() + bars[0].get_width()/2., 102, "100.0%\n(Baseline)", ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax.text(bars[1].get_x() + bars[1].get_width()/2., 19.5, "17.71%\n(Selected)", ha='center', va='bottom', fontsize=11, fontweight='bold')

    # Reduction callout arrow
    ax.annotate('82.29% reduction in the evaluated\nbenchmark regression suite',
                xy=(1, 20), xytext=(0.55, 60),
                arrowprops=dict(facecolor=COLOR_ALERT, shrink=0.08, width=2, headwidth=8),
                fontsize=11, fontweight='bold', color=COLOR_ALERT,
                bbox=dict(boxstyle="round,pad=0.5", fc="#FEF2F2", ec=COLOR_ALERT, lw=1.2))

    # Safety callout badge
    ax.text(0.5, 0.15, "SAFE: 100% safety-test retention (150/150 mandatory tests preserved)\nTest Impact Recall: 90.07%",
            transform=ax.transAxes, ha='center', fontsize=10.5, fontweight='bold', color=COLOR_SUCCESS,
            bbox=dict(boxstyle="round,pad=0.5", fc="#F0FDF4", ec=COLOR_SUCCESS, lw=1.2))

    ax.set_ylim(0, 120)
    ax.set_ylabel("Test Suite Size (%)", fontsize=12, fontweight='bold', labelpad=10)
    ax.set_title("Regression Test Suite Optimization", fontsize=15, fontweight='bold', pad=18)

    ax.grid(axis='y', linestyle='--', alpha=0.4, color=COLOR_BORDER, zorder=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(COLOR_BORDER)
    ax.spines['bottom'].set_color(COLOR_NAVY)

    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "regression_reduction.png"), dpi=300)
    plt.savefig(os.path.join(CHARTS_DIR, "regression_reduction.svg"))
    plt.close()
    print("Generated: regression_reduction")


# ==============================================================================
# 4. CHART: Safety Invariant (Euler/Venn & Metric)
# ==============================================================================
def generate_safety_invariant_chart():
    fig, ax = plt.subplots(figsize=(8.5, 5.2), dpi=300)
    fig.patch.set_facecolor(COLOR_CARD)
    ax.set_facecolor(COLOR_CARD)

    # Draw Euler diagram boxes
    outer_box = FancyBboxPatch((0.08, 0.12), 0.50, 0.76, boxstyle="round,pad=0.03",
                               fc="#F1F5F9", ec=COLOR_NAVY, lw=1.8, zorder=2)
    ax.add_patch(outer_box)
    ax.text(0.12, 0.81, "T_selected (All Selected Tests)", fontsize=11, fontweight='bold', color=COLOR_NAVY)

    inner_box = FancyBboxPatch((0.14, 0.22), 0.38, 0.50, boxstyle="round,pad=0.03",
                               fc="#DCFCE7", ec=COLOR_SUCCESS, lw=2.0, zorder=3)
    ax.add_patch(inner_box)
    ax.text(0.33, 0.52, "T_safe\n(Mandatory ASIL-C/D)\n150 / 150 Retained",
            ha='center', va='center', fontsize=11, fontweight='bold', color="#14532D")

    # Invariant statement
    ax.text(0.33, 0.26, "T_safe ⊆ T_selected", ha='center', fontsize=12, fontweight='bold', color=COLOR_NAVY)

    # Metrics card on the right
    card_right = FancyBboxPatch((0.64, 0.12), 0.32, 0.76, boxstyle="round,pad=0.03",
                                fc=COLOR_LIGHT_BG, ec=COLOR_BORDER, lw=1.5, zorder=2)
    ax.add_patch(card_right)

    metrics_text = (
        "SAFETY METRICS\n"
        "────────────────────\n\n"
        "Safety-Critical Tests:\n"
        "  • 150 mutations\n\n"
        "Safety Tests Retained:\n"
        "  • 150 / 150 (100.0%)\n\n"
        "Safety Recall:\n"
        "  • 100.0%\n\n"
        "Safety Violations:\n"
        "  • 0 (Zero Exclusions)\n\n"
        "Status: PASS (Enforced)"
    )
    ax.text(0.67, 0.48, metrics_text, va='center', fontsize=10.5, fontfamily='monospace', color=COLOR_NAVY)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title("Safety Invariant Enforcement: T_safe ⊆ T_selected", fontsize=15, fontweight='bold', pad=12)

    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "safety_invariant.png"), dpi=300)
    plt.savefig(os.path.join(CHARTS_DIR, "safety_invariant.svg"))
    plt.close()
    print("Generated: safety_invariant")


# ==============================================================================
# 5. CHART: Latency Comparison
# ==============================================================================
def generate_latency_chart():
    fig, ax = plt.subplots(figsize=(8, 5.2), dpi=300)
    fig.patch.set_facecolor(COLOR_CARD)
    ax.set_facecolor(COLOR_CARD)

    methods = ["Graph-Only", "Embedding-Only", "AURA-Impact", "Keyword"]
    latencies = [0.21, 0.39, 0.79, 0.99]
    colors = [COLOR_GRAPH, COLOR_EMBED, COLOR_AURA, COLOR_KEYWORD]

    bars = ax.bar(methods, latencies, color=colors, width=0.52, edgecolor=COLOR_NAVY, linewidth=1.2, zorder=3)

    for bar, val in zip(bars, latencies):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 0.03, f"{val:.2f} ms",
                ha='center', va='bottom', fontsize=11, fontweight='bold', color=COLOR_NAVY)

    ax.set_ylim(0, 1.25)
    ax.set_ylabel("Mean Latency (ms)", fontsize=12, fontweight='bold', labelpad=10)
    ax.set_title("Mean Execution Latency Comparison", fontsize=15, fontweight='bold', pad=18)
    ax.text(0.5, 1.02, "AURA-Impact remains sub-millisecond in the canonical benchmark.",
            transform=ax.transAxes, ha='center', fontsize=10, color=COLOR_SLATE)

    ax.text(0.5, -0.15, "Note: Evaluated in canonical in-memory benchmark; does not generalize to all environments.",
            transform=ax.transAxes, ha='center', fontsize=9, color=COLOR_SLATE, style='italic')

    ax.grid(axis='y', linestyle='--', alpha=0.4, color=COLOR_BORDER, zorder=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(COLOR_BORDER)
    ax.spines['bottom'].set_color(COLOR_NAVY)

    plt.tight_layout()
    plt.savefig(os.path.join(CHARTS_DIR, "latency_comparison.png"), dpi=300)
    plt.savefig(os.path.join(CHARTS_DIR, "latency_comparison.svg"))
    plt.close()
    print("Generated: latency_comparison")


# ==============================================================================
# 6. VISUAL: Research Pipeline Diagram
# ==============================================================================
def generate_research_pipeline_diagram():
    fig, ax = plt.subplots(figsize=(10, 6.2), dpi=300)
    fig.patch.set_facecolor(COLOR_CARD)
    ax.set_facecolor(COLOR_CARD)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 11)
    ax.axis('off')

    steps = [
        ("PROBLEM", "Incomplete automotive software traceability & unlinked artifacts", COLOR_ALERT),
        ("STRUCTURAL ANALYSIS", "Deterministic engineering dependency graph traversal (k ≤ 3)", COLOR_GRAPH),
        ("TRACEABILITY GAP", "Explicit links missing / unlinked semantic drift", COLOR_AMBER),
        ("CONTEXTUAL SEMANTIC RETRIEVAL", "Domain-aware hash vectorizer (AURA-DomainHashEmbedder-384)", COLOR_EMBED),
        ("ENGINEERING CONTEXT FILTER", "Hard constraints: ECU + Subsystem + Artifact Type + Interface", COLOR_AURA),
        ("ROUTING / FUSION", "Strict set union: S_final = S_struct ∪ S_semantic", COLOR_PRIMARY),
        ("IMPACT ANALYSIS", "Ranked impacted components, runnables & interfaces", COLOR_SLATE),
        ("REGRESSION TEST SELECTION", "Automated test mapping: 82.29% benchmark suite reduction", COLOR_AURA),
        ("SAFETY GATE", "Non-bypassable invariant enforcement: T_safe ⊆ T_selected", COLOR_SUCCESS),
        ("EVIDENCE RECOMMENDATION", "Auditable evidence trail for ISO 26262 compliance", COLOR_NAVY)
    ]

    y_start = 10.2
    box_height = 0.65
    box_width = 8.6
    spacing = 0.98

    for i, (title, desc, color) in enumerate(steps):
        y = y_start - (i * spacing)
        # Background box
        box = FancyBboxPatch((0.7, y - box_height), box_width, box_height, boxstyle="round,pad=0.08",
                             fc=COLOR_LIGHT_BG, ec=color, lw=1.6, zorder=2)
        ax.add_patch(box)

        # Title badge
        ax.text(1.0, y - 0.28, title, fontsize=10.5, fontweight='bold', color=color, va='center')
        ax.text(4.2, y - 0.28, desc, fontsize=9.5, fontweight='normal', color=COLOR_NAVY, va='center')

        # Down arrow
        if i < len(steps) - 1:
            ax.annotate('', xy=(5.0, y - box_height - 0.25), xytext=(5.0, y - box_height - 0.02),
                        arrowprops=dict(arrowstyle="->", color=COLOR_SLATE, lw=1.5), zorder=3)

    ax.text(5.0, 10.7, "AURA-Impact Research Methodology Pipeline", ha='center', fontsize=15, fontweight='bold', color=COLOR_NAVY)

    plt.tight_layout()
    plt.savefig(os.path.join(RESEARCH_DIR, "research_pipeline.png"), dpi=300)
    plt.savefig(os.path.join(RESEARCH_DIR, "research_pipeline.svg"))
    plt.close()
    print("Generated: research_pipeline")


# ==============================================================================
# 7. VISUAL: Canonical Architecture Diagram
# ==============================================================================
def generate_canonical_architecture():
    fig, ax = plt.subplots(figsize=(11, 7.0), dpi=300)
    fig.patch.set_facecolor(COLOR_CARD)
    ax.set_facecolor(COLOR_CARD)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 11)
    ax.axis('off')

    # Layer 1: Inputs
    l1 = FancyBboxPatch((0.6, 9.2), 9.8, 1.2, boxstyle="round,pad=0.05", fc="#F8FAFC", ec=COLOR_BORDER, lw=1.5)
    ax.add_patch(l1)
    ax.text(0.9, 10.05, "LAYER 1 — ENGINEERING INPUTS", fontsize=11, fontweight='bold', color=COLOR_NAVY)
    ax.text(0.9, 9.55, "Requirements (reqs.json)  |  AUTOSAR Manifests (*.arxml)  |  Source Code (*.c, *.h)  |  Tests  |  Configurations",
            fontsize=9.5, color=COLOR_SLATE)

    # Layer 2: Graph
    l2 = FancyBboxPatch((0.6, 7.6), 9.8, 1.1, boxstyle="round,pad=0.05", fc="#EFF6FF", ec=COLOR_GRAPH, lw=1.6)
    ax.add_patch(l2)
    ax.text(0.9, 8.35, "LAYER 2 — ENGINEERING REPRESENTATION", fontsize=11, fontweight='bold', color=COLOR_GRAPH)
    ax.text(0.9, 7.85, "Typed Multi-Layer Engineering Dependency Graph (Components, Ports, Runnables, Signals, Tests)",
            fontsize=9.5, color=COLOR_NAVY)

    # Layer 3: Two Analysis Paths
    l3_left = FancyBboxPatch((0.6, 5.0), 4.7, 2.1, boxstyle="round,pad=0.05", fc="#F0F9FF", ec=COLOR_GRAPH, lw=1.6)
    ax.add_patch(l3_left)
    ax.text(0.9, 6.75, "LAYER 3A: STRUCTURAL ANALYSIS", fontsize=10.5, fontweight='bold', color=COLOR_GRAPH)
    ax.text(0.9, 6.30, "• Deterministic Graph Traversal\n• Bounded BFS (k ≤ 3 hops)\n• Explicit Traceability Links",
            fontsize=9, color=COLOR_NAVY)
    ax.text(0.9, 5.35, "Output: S_struct (Structural Impacts)", fontsize=9.5, fontweight='bold', color=COLOR_GRAPH)

    l3_right = FancyBboxPatch((5.7, 5.0), 4.7, 2.1, boxstyle="round,pad=0.05", fc="#FAF5FF", ec=COLOR_EMBED, lw=1.6)
    ax.add_patch(l3_right)
    ax.text(6.0, 6.75, "LAYER 3B: CONTEXTUAL SEMANTIC", fontsize=10.5, fontweight='bold', color=COLOR_EMBED)
    ax.text(6.0, 6.30, "• AURA-DomainHashEmbedder-384\n• Cosine Similarity Matrix Search\n• Incomplete Traceability Fallback",
            fontsize=9, color=COLOR_NAVY)
    ax.text(6.0, 5.35, "Output: Candidate Semantic Matches", fontsize=9.5, fontweight='bold', color=COLOR_EMBED)

    # Layer 4: Context Filtering & Routing
    l4 = FancyBboxPatch((0.6, 3.2), 9.8, 1.3, boxstyle="round,pad=0.05", fc="#F0FDFA", ec=COLOR_AURA, lw=1.6)
    ax.add_patch(l4)
    ax.text(0.9, 4.15, "LAYER 4 — ARCHITECTURAL CONTEXT GATE & ROUTING", fontsize=11, fontweight='bold', color=COLOR_AURA)
    ax.text(0.9, 3.70, "Filters: Subsystem Isolation  |  ECU Boundary Match  |  Artifact Compatibility  |  Interface Binding",
            fontsize=9.2, color=COLOR_NAVY)
    ax.text(0.9, 3.35, "Canonical Fusion: S_final = S_struct ∪ S_semantic (Strict Set Union)", fontsize=10, fontweight='bold', color=COLOR_NAVY)

    # Layer 5: Decision & Output
    l5 = FancyBboxPatch((0.6, 1.2), 9.8, 1.5, boxstyle="round,pad=0.05", fc="#F0FDF4", ec=COLOR_SUCCESS, lw=1.8)
    ax.add_patch(l5)
    ax.text(0.9, 2.35, "LAYER 5 — REGRESSION INTELLIGENCE & NON-BYPASSABLE SAFETY GATE", fontsize=11, fontweight='bold', color=COLOR_SUCCESS)
    ax.text(0.9, 1.90, "Regression Selector: Deterministic Test Mapping (82.29% reduction in benchmark)", fontsize=9.2, color=COLOR_NAVY)
    ax.text(0.9, 1.50, "Safety Gate: Enforces T_safe ⊆ T_selected (100% ASIL-C/D Mandatory Retention)", fontsize=10, fontweight='bold', color="#14532D")

    # Output banner
    out = FancyBboxPatch((0.6, 0.1), 9.8, 0.7, boxstyle="round,pad=0.04", fc=COLOR_NAVY, ec=COLOR_NAVY, lw=1.2)
    ax.add_patch(out)
    ax.text(5.5, 0.45, "DECISION OUTPUT: Selected Tests (T_selected)  |  Auditable Evidence Trail  |  Review Required Cases",
            ha='center', va='center', fontsize=10, fontweight='bold', color="#FFFFFF")

    # Connectors
    ax.annotate('', xy=(5.5, 8.7), xytext=(5.5, 9.2), arrowprops=dict(arrowstyle="->", color=COLOR_SLATE, lw=1.4))
    ax.annotate('', xy=(2.95, 7.1), xytext=(2.95, 7.6), arrowprops=dict(arrowstyle="->", color=COLOR_SLATE, lw=1.4))
    ax.annotate('', xy=(8.05, 7.1), xytext=(8.05, 7.6), arrowprops=dict(arrowstyle="->", color=COLOR_SLATE, lw=1.4))
    ax.annotate('', xy=(2.95, 4.5), xytext=(2.95, 5.0), arrowprops=dict(arrowstyle="->", color=COLOR_SLATE, lw=1.4))
    ax.annotate('', xy=(8.05, 4.5), xytext=(8.05, 5.0), arrowprops=dict(arrowstyle="->", color=COLOR_SLATE, lw=1.4))
    ax.annotate('', xy=(5.5, 2.7), xytext=(5.5, 3.2), arrowprops=dict(arrowstyle="->", color=COLOR_SLATE, lw=1.4))
    ax.annotate('', xy=(5.5, 0.8), xytext=(5.5, 1.2), arrowprops=dict(arrowstyle="->", color=COLOR_SLATE, lw=1.4))

    ax.set_title("AURA-Impact Canonical Architecture (Architecture B)", fontsize=15, fontweight='bold', pad=14)

    plt.tight_layout()
    plt.savefig(os.path.join(ARCH_DIR, "architecture_detailed.png"), dpi=300)
    plt.savefig(os.path.join(ARCH_DIR, "architecture_detailed.svg"))
    plt.close()
    print("Generated: architecture_detailed")


# ==============================================================================
# 8. VISUAL: Core Research Insight (Structure vs Semantics)
# ==============================================================================
def generate_structure_vs_semantics():
    fig, ax = plt.subplots(figsize=(10, 5.8), dpi=300)
    fig.patch.set_facecolor(COLOR_CARD)
    ax.set_facecolor(COLOR_CARD)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Left Column: Graph-Only
    left_card = FancyBboxPatch((0.5, 1.5), 4.2, 7.2, boxstyle="round,pad=0.08", fc="#FEF2F2", ec=COLOR_ALERT, lw=1.8)
    ax.add_patch(left_card)
    ax.text(2.6, 8.2, "GRAPH-ONLY ANALYSIS", ha='center', fontsize=12, fontweight='bold', color=COLOR_ALERT)

    left_steps = [
        "Explicit Dependency Present",
        "↓ (Works when traceability exists)",
        "Deterministic Graph Traversal",
        "↓",
        "Missing / Unlinked Edge\n(Traceability Breakdown)",
        "↓",
        "Graph Traversal Fails\n(Infinite distance d_G = ∞)",
        "↓",
        "[ALERT] Hidden Dependency Missed\n(Dangerous False Negative!)"
    ]
    y_pos = 7.5
    for s in left_steps:
        ax.text(2.6, y_pos, s, ha='center', va='center', fontsize=9.2, color=COLOR_NAVY, fontweight='medium' if "ALERT" not in s else 'bold')
        y_pos -= 0.70

    # Right Column: AURA-Impact
    right_card = FancyBboxPatch((5.3, 1.5), 4.2, 7.2, boxstyle="round,pad=0.08", fc="#F0FDFA", ec=COLOR_AURA, lw=1.8)
    ax.add_patch(right_card)
    ax.text(7.4, 8.2, "AURA-IMPACT HYBRID", ha='center', fontsize=12, fontweight='bold', color=COLOR_AURA)

    right_steps = [
        "Missing / Unlinked Structural Edge",
        "↓",
        "Contextual Semantic Retrieval\n(Domain-Aware Hash Vectorizer)",
        "↓",
        "Engineering Context Filtering\n(ECU + Subsystem + Interface)",
        "↓",
        "Semantic Candidate Recovered\n(Decoys strictly rejected)",
        "↓",
        "[VERIFIED] Safe Set Union Impact\n(S_final = S_struct ∪ S_semantic)"
    ]
    y_pos = 7.5
    for s in right_steps:
        ax.text(7.4, y_pos, s, ha='center', va='center', fontsize=9.2, color=COLOR_NAVY, fontweight='medium' if "VERIFIED" not in s else 'bold')
        y_pos -= 0.70

    # Bottom Banner
    banner = FancyBboxPatch((0.5, 0.4), 9.0, 0.8, boxstyle="round,pad=0.05", fc=COLOR_NAVY, ec=COLOR_NAVY, lw=1.2)
    ax.add_patch(banner)
    ax.text(5.0, 0.8, '"AI augments incomplete traceability; it does not replace deterministic engineering evidence."',
            ha='center', va='center', fontsize=10.5, fontweight='bold', color="#FFFFFF", style='italic')

    ax.set_title("Why AURA-Impact Needs Both Structure and Semantics", fontsize=15, fontweight='bold', pad=14)

    plt.tight_layout()
    plt.savefig(os.path.join(RESEARCH_DIR, "structure_vs_semantics.png"), dpi=300)
    plt.savefig(os.path.join(RESEARCH_DIR, "structure_vs_semantics.svg"))
    plt.close()
    print("Generated: structure_vs_semantics")


# ==============================================================================
# 9. VISUAL: Context Filtering Diagram
# ==============================================================================
def generate_context_filtering_diagram():
    fig, ax = plt.subplots(figsize=(10, 5.8), dpi=300)
    fig.patch.set_facecolor(COLOR_CARD)
    ax.set_facecolor(COLOR_CARD)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Top: Semantic search candidates
    top_box = FancyBboxPatch((0.6, 7.2), 8.8, 1.8, boxstyle="round,pad=0.06", fc="#FAF5FF", ec=COLOR_EMBED, lw=1.6)
    ax.add_patch(top_box)
    ax.text(5.0, 8.6, "STAGE 1: SEMANTIC SEARCH (Unconstrained Embedding Similarity)",
            ha='center', fontsize=11, fontweight='bold', color=COLOR_EMBED)

    cands = [
        "Candidate 1: High Similarity (ADAS Fusion)",
        "Candidate 2: High Similarity (Body Decoy)",
        "Candidate 3: High Similarity (Wrong ECU)",
        "Candidate 4: Moderate Similarity (Ambiguous)"
    ]
    for i, c in enumerate(cands):
        ax.text(1.0 + (i % 2) * 4.4, 8.0 - (i // 2) * 0.45, f"• {c}", fontsize=9, color=COLOR_NAVY)

    # Middle: Context Filters Gate
    mid_box = FancyBboxPatch((0.6, 4.4), 8.8, 2.0, boxstyle="round,pad=0.06", fc="#F0FDFA", ec=COLOR_AURA, lw=1.8)
    ax.add_patch(mid_box)
    ax.text(5.0, 5.95, "STAGE 2: ARCHITECTURAL CONTEXT FILTER GATE", ha='center', fontsize=11.5, fontweight='bold', color=COLOR_AURA)

    filters = [
        ("Subsystem Isolation", "Rejects cross-domain matches (e.g., ADAS vs Body)"),
        ("ECU Boundary", "Validates electronic hardware boundary"),
        ("Artifact Compatibility", "Enforces valid Req → Component → Code → Test"),
        ("Interface Match", "Checks sender-receiver / client-server compatibility")
    ]
    for i, (fname, fdesc) in enumerate(filters):
        ax.text(1.0 + (i % 2) * 4.4, 5.35 - (i // 2) * 0.50, f"✓ {fname}: {fdesc}", fontsize=8.8, color=COLOR_NAVY)

    # Bottom: Filtered Decisions
    decisions = [
        ("Candidate 1", "ACCEPT", COLOR_SUCCESS, "Subsystem & ECU match; interface compatible"),
        ("Candidate 2", "REJECT", COLOR_ALERT, "Subsystem mismatch: Body vs ADAS (Decoy blocked)"),
        ("Candidate 3", "REJECT", COLOR_ALERT, "ECU boundary mismatch: Gateway absent"),
        ("Candidate 4", "REVIEW", COLOR_AMBER, "Borderline confidence (REVIEW_REQUIRED surfaced)")
    ]

    for i, (cname, dec, col, reason) in enumerate(decisions):
        x = 0.6 + i * 2.25
        card = FancyBboxPatch((x, 1.2), 2.05, 2.4, boxstyle="round,pad=0.05", fc=COLOR_LIGHT_BG, ec=col, lw=1.5)
        ax.add_patch(card)
        ax.text(x + 1.02, 3.2, cname, ha='center', fontsize=9.5, fontweight='bold', color=COLOR_NAVY)
        badge = FancyBboxPatch((x + 0.35, 2.6), 1.35, 0.4, boxstyle="round,pad=0.03", fc=col, ec=col)
        ax.add_patch(badge)
        ax.text(x + 1.02, 2.8, dec, ha='center', va='center', fontsize=9.5, fontweight='bold', color="#FFFFFF")
        ax.text(x + 1.02, 1.9, reason, ha='center', va='center', fontsize=8, color=COLOR_SLATE, wrap=True)

    # Connecting arrows
    ax.annotate('', xy=(5.0, 6.4), xytext=(5.0, 7.2), arrowprops=dict(arrowstyle="->", color=COLOR_SLATE, lw=1.5))
    ax.annotate('', xy=(5.0, 3.6), xytext=(5.0, 4.4), arrowprops=dict(arrowstyle="->", color=COLOR_SLATE, lw=1.5))

    ax.set_title("Semantic Similarity Is Constrained by Engineering Context", fontsize=15, fontweight='bold', pad=14)

    plt.tight_layout()
    plt.savefig(os.path.join(RESEARCH_DIR, "context_filtering.png"), dpi=300)
    plt.savefig(os.path.join(RESEARCH_DIR, "context_filtering.svg"))
    plt.close()
    print("Generated: context_filtering")


# ==============================================================================
# 10. VISUAL: End-to-End Prototype Workflow
# ==============================================================================
def generate_end_to_end_prototype():
    fig, ax = plt.subplots(figsize=(11, 6.2), dpi=300)
    fig.patch.set_facecolor(COLOR_CARD)
    ax.set_facecolor(COLOR_CARD)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Left: Main flow (col width 7.0)
    flow_steps = [
        ("ENGINEER & CHANGE REQUEST", "Git commit / requirement change input", COLOR_NAVY),
        ("AURA-IMPACT ENGINE", "Parses .arxml, C source & test mappings", COLOR_PRIMARY),
        ("STAGE 1: IMPACT GRAPH", "Deterministic BFS graph traversal along explicit links", COLOR_GRAPH),
        ("STAGE 2: SEMANTIC RECOVERY", "AURA-DomainHashEmbedder-384 fallback retrieval", COLOR_EMBED),
        ("STAGE 3: CONTEXT FILTER", "Hard ECU & Subsystem domain constraints", COLOR_AURA),
        ("FUSION IMPACT SET", "S_final = S_struct ∪ S_semantic", COLOR_NAVY),
        ("REGRESSION SELECTION & SAFETY GATE", "Selects minimal suite while enforcing T_safe ⊆ T_selected", COLOR_SUCCESS),
        ("ENGINEER AUDIT & REVIEW", "Auditable report with evidence reasoning", COLOR_NAVY)
    ]

    y_start = 9.2
    box_h = 0.62
    spacing = 0.95

    for i, (t, d, col) in enumerate(flow_steps):
        y = y_start - i * spacing
        b = FancyBboxPatch((0.5, y - box_h), 6.5, box_h, boxstyle="round,pad=0.06", fc=COLOR_LIGHT_BG, ec=col, lw=1.5)
        ax.add_patch(b)
        ax.text(0.8, y - 0.26, t, fontsize=9.5, fontweight='bold', color=col, va='center')
        ax.text(3.5, y - 0.26, d, fontsize=8.5, color=COLOR_SLATE, va='center')

        if i < len(flow_steps) - 1:
            ax.annotate('', xy=(3.75, y - box_h - 0.22), xytext=(3.75, y - box_h - 0.02),
                        arrowprops=dict(arrowstyle="->", color=COLOR_SLATE, lw=1.4))

    # Right: Side Panel (Audit & Evidence Dashboard)
    panel = FancyBboxPatch((7.4, 1.2), 3.2, 7.8, boxstyle="round,pad=0.08", fc="#F8FAFC", ec=COLOR_NAVY, lw=1.8)
    ax.add_patch(panel)
    ax.text(9.0, 8.6, "AUDIT & EVIDENCE PANEL", ha='center', fontsize=11, fontweight='bold', color=COLOR_NAVY)

    evidence_info = (
        "LIVE SYSTEM STATE\n"
        "────────────────────────\n\n"
        "• Changed Artifact:\n"
        "  REQ_AEB_SENSOR_001\n\n"
        "• Impacted Artifacts: 4\n"
        "  - SWC_AEB_Controller (struct)\n"
        "  - SWC_FusedTarget (semantic)\n\n"
        "• Decoys Rejected: 2\n"
        "  - SWC_BodyLight (blocked)\n\n"
        "• Selected Tests: 4 / 100\n"
        "  - 96.0% Suite Reduction\n\n"
        "• Safety Invariant: PASS\n"
        "  - 100% ASIL-D Retained\n\n"
        "• Execution Latency:\n"
        "  - 0.31 ms end-to-end"
    )
    ax.text(7.6, 5.0, evidence_info, va='center', fontsize=8.8, fontfamily='monospace', color=COLOR_NAVY)

    ax.set_title("AURA-Impact End-to-End Working Demonstrator Workflow", fontsize=15, fontweight='bold', pad=14)

    plt.tight_layout()
    plt.savefig(os.path.join(PROTOTYPE_DIR, "end_to_end_workflow.png"), dpi=300)
    plt.savefig(os.path.join(PROTOTYPE_DIR, "end_to_end_workflow.svg"))
    plt.close()
    print("Generated: end_to_end_workflow")


# ==============================================================================
# 11. VISUAL: Research Evidence Timeline
# ==============================================================================
def generate_research_timeline():
    fig, ax = plt.subplots(figsize=(11, 4.5), dpi=300)
    fig.patch.set_facecolor(COLOR_CARD)
    ax.set_facecolor(COLOR_CARD)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5)
    ax.axis('off')

    timeline_nodes = [
        "Research\nHypothesis",
        "Benchmark\nDesign",
        "Graph Blindness\nAudit",
        "Ground Truth\nAudit",
        "Context\nAblation",
        "Decoy\nTesting",
        "General-\nization",
        "Safety\nValidation",
        "Hostile\nAudit",
        "Prototype\nValidation",
        "Canonical\nRelease"
    ]

    # Horizontal line
    ax.plot([0.8, 10.2], [2.5, 2.5], color=COLOR_SLATE, lw=2.5, zorder=1)

    for i, name in enumerate(timeline_nodes):
        x = 0.8 + i * 0.94
        circ = Circle((x, 2.5), 0.22, fc=COLOR_AURA if i < 10 else COLOR_PRIMARY, ec=COLOR_NAVY, lw=1.4, zorder=2)
        ax.add_patch(circ)
        ax.text(x, 2.5, str(i + 1), ha='center', va='center', fontsize=9, fontweight='bold', color="#FFFFFF", zorder=3)

        y_text = 3.3 if i % 2 == 0 else 1.3
        ax.text(x, y_text, name, ha='center', va='center', fontsize=8.2, fontweight='bold', color=COLOR_NAVY)

    ax.set_title("AURA-Impact Research → Validation → Prototype Timeline", fontsize=15, fontweight='bold', pad=16)

    plt.tight_layout()
    plt.savefig(os.path.join(RESEARCH_DIR, "research_validation_timeline.png"), dpi=300)
    plt.savefig(os.path.join(RESEARCH_DIR, "research_validation_timeline.svg"))
    plt.close()
    print("Generated: research_validation_timeline")


# ==============================================================================
# 12. TABLES: Benchmark Summary & System Outcomes
# ==============================================================================
def generate_tables():
    # 1. benchmark_summary.csv
    bench_rows = [
        ["Method", "Recall", "Precision", "F1", "Latency"],
        ["Keyword", "42.82%", "18.97%", "0.1485", "0.99 ms"],
        ["Embedding-Only", "42.45%", "66.78%", "0.3114", "0.39 ms"],
        ["Graph-Only", "63.07%", "54.43%", "0.4557", "0.21 ms"],
        ["AURA-Impact", "63.11%", "54.92%", "0.5503", "0.79 ms"]
    ]
    with open(os.path.join(TABLES_DIR, "benchmark_summary.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(bench_rows)

    # 2. system_outcomes.csv
    outcome_rows = [
        ["Metric", "Result", "Interpretation"],
        ["Test Recall", "90.07%", "Coverage of truly impacted regression tests"],
        ["Test Reduction", "82.29%", "Reduction in benchmark regression test suite execution overhead"],
        ["Safety Recall", "100.0%", "Retention of mandatory ISO 26262 ASIL-C/D safety regression tests"],
        ["Safety Tests", "150 / 150", "Zero safety invariant violations across 150 automated mutation batches"],
        ["Mean Latency", "0.79 ms", "Sub-millisecond execution in canonical benchmark"],
        ["Automated Tests", "252 passed", "220 baseline + 32 Round 2 demonstrator tests (100% pass)"],
        ["Validation Gates", "26 / 26 passed", "Full formal stage gate verification (Gate 0 through Gate 25)"]
    ]
    with open(os.path.join(TABLES_DIR, "system_outcomes.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(outcome_rows)

    # Render benchmark_summary.png
    fig, ax = plt.subplots(figsize=(8.5, 3.6), dpi=300)
    fig.patch.set_facecolor(COLOR_CARD)
    ax.axis('off')

    col_labels = bench_rows[0]
    cell_data = bench_rows[1:]

    table = ax.table(cellText=cell_data, colLabels=col_labels, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 1.6)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor(COLOR_BORDER)
        if row == 0:
            cell.set_facecolor(COLOR_NAVY)
            cell.set_text_props(color="#FFFFFF", fontweight='bold')
        elif row == 4:  # AURA-Impact row
            cell.set_facecolor("#CCFBF1")
            cell.set_text_props(fontweight='bold', color=COLOR_NAVY)
        else:
            cell.set_facecolor("#F8FAFC" if row % 2 == 1 else "#FFFFFF")

    ax.set_title("Canonical Benchmark Retrieval Summary", fontsize=14, fontweight='bold', pad=12)
    plt.tight_layout()
    plt.savefig(os.path.join(TABLES_DIR, "benchmark_summary.png"), dpi=300)
    plt.close()
    print("Generated: benchmark tables")


# ==============================================================================
# 13. MASTER VISUAL: 16:9 PPT-Ready Technical Details Slide Composite
# ==============================================================================
def generate_master_visual():
    # 16:9 ratio at 1920x1080: 19.2 x 10.8 inches at 100 dpi
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
    fig.patch.set_facecolor("#FFFFFF")

    # Header Title
    fig.text(0.05, 0.93, "AURA-Impact — Research & Technical Evidence",
             fontsize=24, fontweight='bold', color=COLOR_NAVY)
    fig.text(0.05, 0.90, "Context-Aware Change Impact and Regression Intelligence for AUTOSAR Software Integration",
             fontsize=14, color=COLOR_SLATE)

    # Sub-panels Layout:
    # LEFT: Research Pipeline / Architecture (x: 0.05 -> 0.35, y: 0.22 -> 0.86)
    # CENTER: Artifact F1 Comparison (x: 0.38 -> 0.68, y: 0.48 -> 0.86)
    # RIGHT: Regression & Safety Invariant (x: 0.70 -> 0.95, y: 0.48 -> 0.86)
    # CENTER-RIGHT LOWER: Validation & Outcomes (x: 0.38 -> 0.95, y: 0.22 -> 0.44)
    # BOTTOM: Validated Results Cards (x: 0.05 -> 0.95, y: 0.06 -> 0.18)
    # FOOTER: (y: 0.02)

    # --- LEFT PANEL: Research Pipeline & Architecture ---
    ax_left = fig.add_axes([0.05, 0.22, 0.30, 0.65])
    ax_left.set_facecolor(COLOR_LIGHT_BG)
    ax_left.axis('off')
    box_left = FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.02", fc=COLOR_LIGHT_BG, ec=COLOR_BORDER, lw=1.5)
    ax_left.add_patch(box_left)

    ax_left.text(0.5, 0.95, "CANONICAL HYBRID ARCHITECTURE", ha='center', fontsize=12, fontweight='bold', color=COLOR_NAVY)

    arch_layers = [
        ("INPUTS", "Requirements, ARXML, C Code, Tests", COLOR_SLATE),
        ("REPRESENTATION", "Typed Engineering Dependency Graph", COLOR_GRAPH),
        ("STAGE 1: GRAPH", "Bounded BFS Traversal (k ≤ 3 hops)", COLOR_GRAPH),
        ("STAGE 2: SEMANTIC", "AURA-DomainHashEmbedder-384", COLOR_EMBED),
        ("CONTEXT GATE", "ECU, Subsystem & Interface Constraints", COLOR_AURA),
        ("STRICT FUSION", "S_final = S_struct ∪ S_semantic", COLOR_PRIMARY),
        ("REGRESSION", "Test Selection Mapping (82.29% reduction)", COLOR_AURA),
        ("SAFETY GATE", "Invariant Enforced: T_safe ⊆ T_selected", COLOR_SUCCESS)
    ]
    for idx, (ltitle, ldesc, lcol) in enumerate(arch_layers):
        y_l = 0.85 - idx * 0.105
        b_sub = FancyBboxPatch((0.05, y_l - 0.04), 0.90, 0.08, boxstyle="round,pad=0.01", fc="#FFFFFF", ec=lcol, lw=1.2)
        ax_left.add_patch(b_sub)
        ax_left.text(0.08, y_l, ltitle, fontsize=9, fontweight='bold', color=lcol, va='center')
        ax_left.text(0.40, y_l, ldesc, fontsize=8, color=COLOR_NAVY, va='center')

    # --- CENTER PANEL: Artifact F1 Comparison ---
    ax_center = fig.add_axes([0.38, 0.49, 0.30, 0.38])
    ax_center.set_facecolor("#FFFFFF")
    methods = ["Keyword", "Embedding", "Graph-Only", "AURA-Impact"]
    f1_vals = [0.1485, 0.3114, 0.4557, 0.5503]
    f1_colors = [COLOR_KEYWORD, COLOR_EMBED, COLOR_GRAPH, COLOR_AURA]
    bars = ax_center.bar(methods, f1_vals, color=f1_colors, width=0.55, edgecolor=COLOR_NAVY, linewidth=1.1, zorder=3)
    for b, v in zip(bars, f1_vals):
        ax_center.text(b.get_x() + b.get_width()/2., v + 0.015, f"{v:.4f}", ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax_center.set_ylim(0, 0.68)
    ax_center.set_ylabel("Artifact F1", fontsize=10, fontweight='bold')
    ax_center.set_title("Artifact Impact Prediction (F1 Comparison)", fontsize=12, fontweight='bold', pad=10)
    ax_center.grid(axis='y', linestyle='--', alpha=0.3, color=COLOR_BORDER, zorder=0)
    ax_center.spines['top'].set_visible(False)
    ax_center.spines['right'].set_visible(False)
    ax_center.spines['left'].set_color(COLOR_BORDER)
    ax_center.spines['bottom'].set_color(COLOR_NAVY)

    # --- RIGHT PANEL: Safety Invariant & Regression Reduction ---
    ax_right = fig.add_axes([0.70, 0.49, 0.25, 0.38])
    ax_right.set_facecolor(COLOR_LIGHT_BG)
    ax_right.axis('off')
    box_r = FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.02", fc=COLOR_LIGHT_BG, ec=COLOR_BORDER, lw=1.5)
    ax_right.add_patch(box_r)

    ax_right.text(0.5, 0.92, "SAFETY & TEST SELECTION", ha='center', fontsize=12, fontweight='bold', color=COLOR_NAVY)

    # Mini Euler box
    e_out = FancyBboxPatch((0.10, 0.48), 0.80, 0.38, boxstyle="round,pad=0.02", fc="#EFF6FF", ec=COLOR_GRAPH, lw=1.4)
    ax_right.add_patch(e_out)
    ax_right.text(0.15, 0.77, "T_selected (All Selected Tests)", fontsize=8.5, fontweight='bold', color=COLOR_GRAPH)

    e_in = FancyBboxPatch((0.18, 0.52), 0.64, 0.22, boxstyle="round,pad=0.02", fc="#DCFCE7", ec=COLOR_SUCCESS, lw=1.6)
    ax_right.add_patch(e_in)
    ax_right.text(0.50, 0.63, "T_safe ⊆ T_selected\n150/150 Retained (100%)", ha='center', va='center',
                  fontsize=8.5, fontweight='bold', color="#14532D")

    # Safety Text Callouts
    safe_callout = (
        "• Safety Invariant: 100% (150/150)\n"
        "• Safety Violations: 0 (Zero Exclusions)\n"
        "• Test Suite Reduction: 82.29%\n"
        "• Test Impact Recall: 90.07%"
    )
    ax_right.text(0.10, 0.26, safe_callout, fontsize=9.2, fontfamily='monospace', color=COLOR_NAVY)

    # --- LOWER CENTER/RIGHT: Validation & Engineering Table ---
    ax_table = fig.add_axes([0.38, 0.22, 0.57, 0.22])
    ax_table.axis('off')
    out_table_data = [
        ["System Metric", "Benchmark / Live Result", "Engineering Significance"],
        ["Artifact Recall / Prec", "63.11% Recall / 54.92% Precision", "Recovers unlinked impacts; balances precision vs recall"],
        ["Regression Reduction", "82.29% Suite Reduction", "Slashes continuous integration test cycle duration"],
        ["Safety Gate", "100.0% Retention (150/150)", "Guarantees zero omissions of ISO 26262 ASIL-C/D tests"],
        ["Execution Latency", "0.79 ms benchmark / 5.34 ms live", "Sub-millisecond processing enables pre-commit git hooks"]
    ]
    t_obj = ax_table.table(cellText=out_table_data[1:], colLabels=out_table_data[0], loc='center', cellLoc='left')
    t_obj.auto_set_font_size(False)
    t_obj.set_fontsize(9)
    t_obj.scale(1.0, 1.4)
    for (r_i, c_i), c_cell in t_obj.get_celld().items():
        c_cell.set_edgecolor(COLOR_BORDER)
        if r_i == 0:
            c_cell.set_facecolor(COLOR_NAVY)
            c_cell.set_text_props(color="#FFFFFF", fontweight='bold')
        else:
            c_cell.set_facecolor("#F8FAFC" if r_i % 2 == 1 else "#FFFFFF")

    # --- BOTTOM CARDS: Key Validated Results ---
    cards = [
        ("63.11%", "Artifact Recall", "Benchmark"),
        ("0.5503", "Artifact F1", "Benchmark"),
        ("90.07%", "Test Suite Recall", "Benchmark"),
        ("82.29%", "Test Suite Reduction", "Benchmark"),
        ("100.0%", "Safety Invariant", "150/150 Retained"),
        ("0.79 ms", "Mean Latency", "In-Memory Benchmark")
    ]
    card_w = 0.138
    gap = 0.014
    for idx, (cval, clbl, csub) in enumerate(cards):
        cx = 0.05 + idx * (card_w + gap)
        ax_c = fig.add_axes([cx, 0.06, card_w, 0.12])
        ax_c.axis('off')
        c_box = FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.03", fc="#F0FDFA", ec=COLOR_AURA, lw=1.5)
        ax_c.add_patch(c_box)
        ax_c.text(0.5, 0.68, cval, ha='center', va='center', fontsize=15, fontweight='bold', color=COLOR_AURA)
        ax_c.text(0.5, 0.38, clbl, ha='center', va='center', fontsize=9.2, fontweight='bold', color=COLOR_NAVY)
        ax_c.text(0.5, 0.16, csub, ha='center', va='center', fontsize=7.8, color=COLOR_SLATE)

    # Footer
    fig.text(0.5, 0.02, "Canonical benchmark • Prototype evidence shown separately • KPIT Sparkle Round 2 Submission",
             ha='center', fontsize=10, color=COLOR_SLATE, style='italic')

    # Save
    master_png = os.path.join(BASE_DIR, "technical_details_master.png")
    master_svg = os.path.join(BASE_DIR, "technical_details_master.svg")
    plt.savefig(master_png, dpi=100)
    plt.savefig(master_svg)
    plt.close()
    print("Generated: technical_details_master (16:9 composite)")


def main():
    print("Generating all Round 2 Technical Details visual assets...")
    generate_f1_chart()
    generate_recall_precision_chart()
    generate_regression_reduction_chart()
    generate_safety_invariant_chart()
    generate_latency_chart()
    generate_research_pipeline_diagram()
    generate_canonical_architecture()
    generate_structure_vs_semantics()
    generate_context_filtering_diagram()
    generate_end_to_end_prototype()
    generate_research_timeline()
    generate_tables()
    generate_master_visual()
    print("All visual assets successfully generated!")

if __name__ == "__main__":
    main()
