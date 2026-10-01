"""
Semantic Model Identity Verification Test
Proves actual model identity, dimension, deterministic hashing implementation,
FAISS/NumPy index behavior, similarity metric, configuration alignment, and fallback.
"""
import pytest
import numpy as np
from pathlib import Path
import yaml

from src.semantic.embedder import SemanticEmbedder
from src.semantic.index import FAISSSemanticIndex, IndexedArtifact
from src.semantic.retriever import ContextualRetriever
from src.semantic.context_filter import ContextFilter


def test_actual_model_identity():
    """Prove the model identity is AURA-DomainHashEmbedder-384 and NOT an unverified neural model."""
    embedder = SemanticEmbedder()
    assert embedder.model_name == "AURA-DomainHashEmbedder-384"
    assert embedder.dimension == 384
    assert embedder.is_neural is False
    assert embedder.model_type == "deterministic_domain_hash_vectorizer"


def test_actual_dimension_and_normalization():
    """Prove output embedding is strictly 384-D, float32, and L2 normalized."""
    embedder = SemanticEmbedder(dimension=384)
    text = "Autonomous emergency braking radar sensor actuation"
    vec = embedder.embed_text(text)
    
    assert isinstance(vec, np.ndarray)
    assert vec.shape == (384,)
    assert vec.dtype == np.float32
    norm = np.linalg.norm(vec)
    assert abs(norm - 1.0) < 1e-4, f"Vector must be L2 unit norm, got {norm}"


def test_deterministic_reproducibility():
    """Prove that multiple runs produce bit-for-bit identical vectors (deterministic hash-based)."""
    embedder1 = SemanticEmbedder(dimension=384)
    embedder2 = SemanticEmbedder(dimension=384)
    
    text = "Battery management system contactor thermal runaway cutoff"
    v1 = embedder1.embed_text(text)
    v2 = embedder2.embed_text(text)
    
    np.testing.assert_array_equal(v1, v2)


def test_actual_index_and_similarity():
    """Prove FAISS (or fallback NumPy index) computes accurate cosine similarity using Inner Product on normalized vectors."""
    embedder = SemanticEmbedder(dimension=384)
    index = FAISSSemanticIndex(dimension=384)
    
    art1 = IndexedArtifact("REQ_AEB_01", "Requirement", "ADAS", "ECU_1", "Emergency braking deceleration threshold")
    art2 = IndexedArtifact("REQ_BMS_01", "Requirement", "Battery_EV", "ECU_BMS", "Battery cell overtemperature threshold")
    
    vecs = embedder.embed_batch([art1.text_content, art2.text_content])
    index.add_artifacts([art1, art2], vecs)
    
    # Query AEB
    q_vec = embedder.embed_text("AEB emergency braking decelerate")
    results = index.search(q_vec, top_k=2)
    
    assert len(results) == 2
    top_art, top_sim = results[0]
    second_art, second_sim = results[1]
    
    assert top_art.artifact_id == "REQ_AEB_01"
    assert top_sim > second_sim
    assert -1.0 <= top_sim <= 1.0001


def test_configuration_identity_alignment():
    """Prove configuration explicitly defines AURA-DomainHashEmbedder-384 and 384-D."""
    config_path = Path("configs/canonical_architecture.yaml")
    assert config_path.exists(), "configs/canonical_architecture.yaml must exist"
    
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
        
    sem_cfg = cfg.get("semantic", {})
    assert sem_cfg.get("model") == "AURA-DomainHashEmbedder-384"
    assert sem_cfg.get("embedding_dimension") == 384


def test_fallback_behavior_on_empty_text():
    """Prove embedder gracefully handles empty, whitespace, and malformed inputs with unit fallback vector."""
    embedder = SemanticEmbedder(dimension=384)
    v_empty = embedder.embed_text("")
    v_spaces = embedder.embed_text("   \n\t  ")
    
    assert v_empty.shape == (384,)
    assert v_spaces.shape == (384,)
    assert abs(np.linalg.norm(v_empty) - 1.0) < 1e-4
    assert abs(np.linalg.norm(v_spaces) - 1.0) < 1e-4
    assert v_empty[0] == 1.0
