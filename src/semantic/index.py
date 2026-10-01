"""
FAISS Semantic Vector Index
Builds and persists dense vector indexes for fast top-K similarity search with metadata.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from pathlib import Path
import json

try:
    import faiss
    FAISS_AVAILABLE = True
except Exception:
    FAISS_AVAILABLE = False


@dataclass
class IndexedArtifact:
    artifact_id: str
    artifact_type: str
    subsystem: str
    ecu: str
    text_content: str
    source_file: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class FAISSSemanticIndex:
    """Stores artifact vectors and metadata with FAISS / NumPy cosine acceleration."""

    def __init__(self, dimension: Any = 384, embedder: Any = None):
        if hasattr(dimension, "dimension"):
            self.embedder = dimension
            self.dimension = int(dimension.dimension)
        else:
            self.dimension = int(dimension) if isinstance(dimension, (int, float, str)) else 384
            self.embedder = embedder

        self.artifacts: List[IndexedArtifact] = []
        self.vectors: Optional[np.ndarray] = None
        self.index = None
        if FAISS_AVAILABLE:
            self.index = faiss.IndexFlatIP(int(self.dimension))

    def add_artifacts(self, artifacts: List[IndexedArtifact], embeddings: np.ndarray):
        if len(artifacts) != len(embeddings):
            raise ValueError(f"Artifacts count ({len(artifacts)}) != embeddings count ({len(embeddings)})")

        self.artifacts.extend(artifacts)
        if self.vectors is None:
            self.vectors = np.array(embeddings, dtype=np.float32)
        else:
            self.vectors = np.vstack([self.vectors, np.array(embeddings, dtype=np.float32)])

        if self.index is not None:
            self.index.add(np.array(embeddings, dtype=np.float32))

    def build_index(self, nodes: List[Any]):
        artifacts = []
        texts = []
        for n in nodes:
            t = f"{n.id} {n.name} {getattr(n, 'description', '')} {getattr(n, 'subsystem', '')}"
            c_type = n.type.value if hasattr(n.type, "value") else str(n.type)
            artifacts.append(IndexedArtifact(
                artifact_id=n.id,
                artifact_type=c_type,
                subsystem=getattr(n, "subsystem", "ADAS"),
                ecu=getattr(n, "ecu", "ECU_1"),
                text_content=t,
                source_file=getattr(n, "source_file", "")
            ))
            texts.append(t)

        if self.embedder and texts:
            if hasattr(self.embedder, "embed_batch"):
                vecs = self.embedder.embed_batch(texts)
            elif hasattr(self.embedder, "embed_artifacts"):
                vecs = self.embedder.embed_artifacts(artifacts)
            else:
                vecs = np.array([self.embedder.embed_text(t) for t in texts], dtype=np.float32)
            self.add_artifacts(artifacts, vecs)

    def search(self, query_vec: np.ndarray, top_k: int = 10, subsystem_filter: Optional[str] = None) -> List[Tuple[IndexedArtifact, float]]:
        if self.vectors is None or len(self.artifacts) == 0:
            return []

        query_vec = query_vec.reshape(1, -1).astype(np.float32)
        norm = np.linalg.norm(query_vec)
        if norm > 1e-6:
            query_vec = query_vec / norm

        candidates: List[Tuple[IndexedArtifact, float]] = []

        if subsystem_filter:
            sub_lower = subsystem_filter.lower().replace("_", "").replace(" ", "")
            # Filter candidates matching subsystem
            matching_indices = [
                i for i, a in enumerate(self.artifacts)
                if a.subsystem.lower().replace("_", "").replace(" ", "") == sub_lower
            ]
            if not matching_indices:
                # Fallback to all if zero in subsystem
                matching_indices = list(range(len(self.artifacts)))

            sub_vecs = self.vectors[matching_indices]
            scores = np.dot(sub_vecs, query_vec.T).flatten()
            ranked_order = np.argsort(scores)[::-1][:top_k]

            for rank_idx in ranked_order:
                orig_idx = matching_indices[rank_idx]
                candidates.append((self.artifacts[orig_idx], float(scores[rank_idx])))
        else:
            if FAISS_AVAILABLE and self.index is not None:
                scores, indices = self.index.search(query_vec, min(top_k, len(self.artifacts)))
                for s, i in zip(scores[0], indices[0]):
                    if i >= 0 and i < len(self.artifacts):
                        candidates.append((self.artifacts[i], float(s)))
            else:
                scores = np.dot(self.vectors, query_vec.T).flatten()
                ranked_order = np.argsort(scores)[::-1][:top_k]
                for idx in ranked_order:
                    candidates.append((self.artifacts[idx], float(scores[idx])))

        return candidates


# Backward-compatible alias
SemanticIndex = FAISSSemanticIndex
