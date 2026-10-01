"""
Benchmark Reporting and Figure Generation Engine
"""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


class BenchmarkReporter:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.figures_dir = self.output_dir / "figures"
        self.tables_dir = self.output_dir / "tables"
        self.raw_dir = self.output_dir / "raw_results"
        self._ensure_dirs()

    def _ensure_dirs(self):
        self.figures_dir.mkdir(parents=True, exist_ok=True)
        self.tables_dir.mkdir(parents=True, exist_ok=True)
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    def generate_figures(
        self,
        impact_df: pd.DataFrame,
        regression_df: pd.DataFrame,
        scaling_df: Optional[pd.DataFrame] = None
    ) -> List[str]:
        generated_figs = []

        # Set clean aesthetic styling
        plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
        
        # 1. Precision vs Recall by Method
        fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
        method_stats = impact_df.groupby("method").agg({"recall": "mean", "precision": "mean", "latency_ms": "mean"}).reset_index()
        
        colors = {"Keyword": "#e74c3c", "Embedding_Only": "#e67e22", "Graph_Only": "#2980b9", "Hybrid_AURA_Routed": "#27ae60", "Full_Suite": "#7f8c8d"}
        
        for _, row in method_stats.iterrows():
            m = row["method"]
            color = colors.get(m, "#34495e")
            ax.scatter(row["recall"], row["precision"], s=220, color=color, label=m, alpha=0.9, edgecolors="black", linewidths=1.5)
            ax.annotate(m, (row["recall"] + 0.01, row["precision"] + 0.01), fontsize=10, weight="bold")

        ax.set_xlabel("Artifact Impact Recall", fontsize=12, weight="bold")
        ax.set_ylabel("Artifact Impact Precision", fontsize=12, weight="bold")
        ax.set_title("Impact Analysis: Precision vs Recall across Methods", fontsize=14, weight="bold")
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.05, 1.05)
        ax.legend(loc="lower left", frameon=True)
        
        f1_path = self.figures_dir / "fig1_precision_vs_recall.png"
        fig.tight_layout()
        fig.savefig(f1_path)
        plt.close(fig)
        generated_figs.append(str(f1_path))

        # 2. Recall by Change Category
        if "category_name" in impact_df.columns:
            fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
            cat_pivot = impact_df.pivot_table(index="category_name", columns="method", values="recall", aggfunc="mean")
            cat_pivot.plot(kind="bar", ax=ax, width=0.8, colormap="viridis")
            ax.set_title("Impact Recall Breakdown by Mutation Category", fontsize=14, weight="bold")
            ax.set_ylabel("Mean Recall", fontsize=12, weight="bold")
            ax.set_xlabel("Change Category", fontsize=12, weight="bold")
            plt.xticks(rotation=45, ha="right", fontsize=9)
            ax.legend(title="Method", loc="upper right")
            
            f2_path = self.figures_dir / "fig2_recall_by_change_type.png"
            fig.tight_layout()
            fig.savefig(f2_path)
            plt.close(fig)
            generated_figs.append(str(f2_path))

        # 3. Test Reduction vs Impact Recall (Regression)
        fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
        reg_summary = regression_df.groupby("method").agg({"test_reduction": "mean", "recall": "mean", "safety_recall": "mean"}).reset_index()
        
        for _, row in reg_summary.iterrows():
            m = row["method"]
            color = colors.get(m, "#34495e")
            ax.scatter(row["test_reduction"], row["recall"], s=220, color=color, label=m, alpha=0.9, edgecolors="black", linewidths=1.5)
            ax.annotate(f"{m}\n(Safety Rec: {row['safety_recall']*100:.1f}%)", (row["test_reduction"] + 0.01, row["recall"] - 0.03), fontsize=9)

        ax.set_xlabel("Test Suite Execution Reduction (1 - |Ts|/|T|)", fontsize=12, weight="bold")
        ax.set_ylabel("Impacted Test Recall", fontsize=12, weight="bold")
        ax.set_title("Regression Test Selection: Reduction vs Recall", fontsize=14, weight="bold")
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.05, 1.05)
        ax.legend(loc="lower left", frameon=True)
        
        f3_path = self.figures_dir / "fig3_test_reduction_vs_recall.png"
        fig.tight_layout()
        fig.savefig(f3_path)
        plt.close(fig)
        generated_figs.append(str(f3_path))

        # 4. Latency by Method
        fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
        impact_df.boxplot(column="latency_ms", by="method", ax=ax, patch_artist=True)
        ax.set_title("Impact Analysis Latency by Method (ms)", fontsize=13, weight="bold")
        ax.set_ylabel("Execution Time (ms)", fontsize=11)
        plt.suptitle("")
        
        f4_path = self.figures_dir / "fig4_latency_by_method.png"
        fig.tight_layout()
        fig.savefig(f4_path)
        plt.close(fig)
        generated_figs.append(str(f4_path))

        # 5. Scaling Curves if available
        if scaling_df is not None and not scaling_df.empty:
            fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
            ax.plot(scaling_df["node_count"], scaling_df["graph_build_ms"], marker="o", label="Graph Build (ms)", linewidth=2)
            ax.plot(scaling_df["node_count"], scaling_df["hybrid_query_ms"], marker="s", label="Hybrid Query Latency (ms)", linewidth=2)
            ax.plot(scaling_df["node_count"], scaling_df["incremental_update_ms"], marker="^", label="Incremental Update (ms)", linewidth=2)
            ax.set_xscale("log")
            ax.set_yscale("log")
            ax.set_xlabel("Total Graph Nodes (N)", fontsize=12, weight="bold")
            ax.set_ylabel("Time (ms) [Log Scale]", fontsize=12, weight="bold")
            ax.set_title("Scalability: Graph Build vs Query vs Incremental Update", fontsize=14, weight="bold")
            ax.legend(loc="upper left")
            
            f5_path = self.figures_dir / "fig5_scaling_curves.png"
            fig.tight_layout()
            fig.savefig(f5_path)
            plt.close(fig)
            generated_figs.append(str(f5_path))

        return generated_figs
