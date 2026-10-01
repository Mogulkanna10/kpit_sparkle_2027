"""
Semantic Embedder
Implements AURA-DomainHashEmbedder-384: A deterministic automotive domain-concept
hash vectorizer with ontology projection and L2 unit hypersphere normalization.
Provides microsecond latency and zero external neural model weight dependencies.
"""
from typing import List, Dict, Any, Optional
import numpy as np
import re
import hashlib


class SemanticEmbedder:
    """Computes dense normalized embeddings for engineering artifact texts using deterministic domain hashing."""

    def __init__(self, model_name: str = "AURA-DomainHashEmbedder-384", dimension: int = 384, device: str = "cpu", **kwargs):
        self.model_name = model_name
        self.dimension = dimension
        self.device = device
        self.is_neural = False
        self.model_type = "deterministic_domain_hash_vectorizer"

        # Automotive domain concept ontology for high-fidelity semantic alignment
        self.domain_concepts = {
            "aeb": ["automatic", "emergency", "braking", "collision", "ttc", "deceleration", "hazard"],
            "acc": ["adaptive", "cruise", "control", "distance", "radar", "target", "velocity"],
            "bms": ["battery", "management", "contactor", "overtemperature", "current", "soc", "thermal", "derating"],
            "powertrain": ["propulsion", "motor", "inverter", "torque", "inhibit", "traction", "derating"],
            "body": ["lighting", "door", "wiper", "climate", "window", "pinch", "cabin"],
            "safety": ["shutdown", "inhibit", "asil", "clamp", "protective", "hazard", "cutoff"]
        }

    def embed_text(self, text: str) -> np.ndarray:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        vectors = []
        for text in texts:
            vec = np.zeros(self.dimension, dtype=np.float32)
            if not text or not text.strip():
                vec[0] = 1.0
                vectors.append(vec)
                continue

            cleaned = text.lower()
            tokens = re.findall(r"\b[a-z0-9_]+\b", cleaned)

            for token in tokens:
                # Primary token hash
                h1 = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16) % self.dimension
                vec[h1] += 1.0

                # 3-gram subword features
                for i in range(len(token) - 2):
                    sub = token[i:i+3]
                    h_sub = int(hashlib.sha256(sub.encode("utf-8")).hexdigest(), 16) % self.dimension
                    vec[h_sub] += 0.35

                # Domain ontology concept expansion
                for concept, keywords in self.domain_concepts.items():
                    if token in keywords or any(k in token for k in keywords):
                        h_c = int(hashlib.md5(concept.encode("utf-8")).hexdigest(), 16) % self.dimension
                        vec[h_c] += 1.5

            norm = np.linalg.norm(vec)
            if norm > 1e-6:
                vec = vec / norm
            else:
                vec[0] = 1.0
            vectors.append(vec)

        return np.array(vectors, dtype=np.float32)


# Backward-compatible alias
ArtifactEmbedder = SemanticEmbedder
