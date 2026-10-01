"""
Baseline 1: Keyword Search (v2.0)
"""
import time
from typing import List, Dict, Any, Set, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from src.graph.builder import EngineeringGraph
from src.testing.selector import RegressionSelector
from src.impact.change_detector import ChangeContext


class KeywordBaseline:
    def __init__(self, eng_graph: EngineeringGraph, selector: RegressionSelector, threshold: float = 0.15):
        self.eng_graph = eng_graph
        self.selector = selector
        self.threshold = threshold
        self.node_ids = list(eng_graph.node_store.keys())
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), token_pattern=r"(?u)\b\w+\b")
        
        corpus = []
        for nid in self.node_ids:
            node = eng_graph.get_node(nid)
            text = f"{node.name} {node.description} {' '.join(str(v) for v in node.properties.values())}"
            corpus.append(text)

        if corpus:
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        else:
            self.tfidf_matrix = None

    def run(
        self,
        change: ChangeContext,
        threshold: float = 0.15,
        ground_truth_safety_tests: Optional[Set[str] | List[str]] = None,
        enforce_safety_gate: bool = True
    ) -> Dict[str, Any]:
        start_t = time.perf_counter()
        th = threshold if threshold is not None else self.threshold

        query_text = f"{change.diff_text} {change.after_content} {change.change_semantics}"
        
        impacted_nodes = []
        if self.tfidf_matrix is not None and query_text.strip():
            query_vec = self.vectorizer.transform([query_text])
            scores = (self.tfidf_matrix * query_vec.T).toarray().flatten()

            for idx, score in enumerate(scores):
                if score >= th:
                    impacted_nodes.append(self.node_ids[idx])

        if change.target_node_id and change.target_node_id not in impacted_nodes:
            impacted_nodes.append(change.target_node_id)

        selected_tests = self.selector.select_tests(
            impacted_artifact_ids=impacted_nodes,
            ground_truth_safety_tests=ground_truth_safety_tests,
            enforce_safety_gate=enforce_safety_gate
        )
        latency_ms = (time.perf_counter() - start_t) * 1000.0

        return {
            "method": "Keyword",
            "impacted_artifacts": impacted_nodes,
            "selected_tests": selected_tests,
            "latency_ms": round(latency_ms, 3)
        }
