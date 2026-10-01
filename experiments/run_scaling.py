"""
Experiment Suite: Scalability & Incremental Update Analysis (Experiments L & Incremental Update)
Evaluates runtime scaling from N=50 to N=25,000 nodes:
- Graph build time
- Hybrid query latency
- Semantic index latency
- Incremental update vs full rebuild latency
"""
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
import numpy as np
import networkx as nx

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.graph.schema import Node, Edge, NodeType, EdgeType, SafetyLevel
from src.graph.builder import EngineeringGraph
from src.graph.traversal import GraphTraverser
from src.semantic.embedder import ArtifactEmbedder
from src.semantic.index import SemanticIndex
from src.impact.fusion import ImpactFusionEngine


def run_scaling_benchmark(out_dir: Path, max_nodes_list: List[int] = None) -> pd.DataFrame:
    node_sizes = max_nodes_list or [50, 100, 250, 500, 1000, 5000, 10000, 25000]
    results = []

    embedder = ArtifactEmbedder()

    for n in node_sizes:
        print(f"Benchmarking scaling for N = {n} nodes...")
        
        # 1. Measure Graph Build Time
        t0 = time.perf_counter()
        g = EngineeringGraph(f"Scale_{n}")
        nodes = []
        for i in range(n):
            node = Node(
                id=f"Node_{i:06d}",
                type=NodeType.C_FUNCTION if i % 2 == 0 else NodeType.REQUIREMENT,
                name=f"Artifact_{i}",
                file_path=f"src/file_{i//10}.c",
                project="ScalingTest",
                description=f"Scaling automotive control artifact {i} with computation routine #{i % 20}"
            )
            g.add_node(node)
            nodes.append(node)

        # Add ~ 3n edges
        for i in range(n - 1):
            g.add_edge(Edge(
                source_id=f"Node_{i:06d}",
                target_id=f"Node_{min(n-1, i + (i%5) + 1):06d}",
                relation=EdgeType.CALLS,
                source_file="scale.c"
            ))
            if i % 3 == 0 and i + 10 < n:
                g.add_edge(Edge(
                    source_id=f"Node_{i:06d}",
                    target_id=f"Node_{i+10:06d}",
                    relation=EdgeType.DEPENDS_ON,
                    source_file="scale.c"
                ))

        graph_build_ms = (time.perf_counter() - t0) * 1000.0

        # 2. Measure Traversal Query Latency
        traverser = GraphTraverser(g, max_depth=5)
        t_q0 = time.perf_counter()
        traverser.propagate_downstream([f"Node_{0:06d}"])
        graph_query_ms = (time.perf_counter() - t_q0) * 1000.0

        # 3. Measure Semantic Search Latency (on sample for large N)
        index_nodes = nodes[:min(n, 1000)]
        sem_index = SemanticIndex(embedder)
        sem_index.build_index(index_nodes)
        
        t_sq0 = time.perf_counter()
        sem_index.search("emergency braking deceleration", threshold=0.65, top_k=10)
        sem_query_ms = (time.perf_counter() - t_sq0) * 1000.0

        # 4. Measure Full Rebuild vs Incremental Update
        # Full rebuild
        t_fb0 = time.perf_counter()
        # Modify 1 node
        g_rebuild = EngineeringGraph(f"Scale_Rebuild_{n}")
        for nd in nodes:
            g_rebuild.add_node(nd)
        full_rebuild_ms = (time.perf_counter() - t_fb0) * 1000.0

        # Incremental Update (update single node + its edges)
        t_inc0 = time.perf_counter()
        modified_node = Node(
            id=f"Node_000000",
            type=NodeType.C_FUNCTION,
            name="Artifact_0_Modified",
            file_path="src/file_0.c",
            project="ScalingTest",
            description="Updated description"
        )
        g.add_node(modified_node)  # Updates node_store & graph node in-place
        inc_update_ms = (time.perf_counter() - t_inc0) * 1000.0

        hybrid_query_ms = graph_query_ms + sem_query_ms

        results.append({
            "node_count": n,
            "edge_count": g.graph.number_of_edges(),
            "graph_build_ms": round(graph_build_ms, 2),
            "graph_query_ms": round(graph_query_ms, 3),
            "semantic_query_ms": round(sem_query_ms, 3),
            "hybrid_query_ms": round(hybrid_query_ms, 3),
            "full_rebuild_ms": round(full_rebuild_ms, 2),
            "incremental_update_ms": round(inc_update_ms, 4),
            "speedup_factor": round(full_rebuild_ms / max(0.0001, inc_update_ms), 1)
        })

    df = pd.DataFrame(results)
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "scaling_results.csv", index=False)
    print(f"[OK] Exp L: Scalability benchmark completed ({len(df)} scale tiers)")
    return df


if __name__ == "__main__":
    run_scaling_benchmark(Path("reports/raw_results"))
