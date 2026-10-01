"""
Unit Tests for Semantic Retrieval and Context Filtering
"""
import pytest
import numpy as np
from src.semantic.embedder import SemanticEmbedder
from src.semantic.index import FAISSSemanticIndex, IndexedArtifact
from src.semantic.context_filter import ContextFilter
from src.semantic.retriever import ContextualRetriever


def test_semantic_embedding_and_indexing():
    embedder = SemanticEmbedder(dimension=384)
    v1 = embedder.embed_text("Emergency brake deceleration actuation")
    assert v1.shape == (384,)
    assert abs(np.linalg.norm(v1) - 1.0) < 1e-4

    index = FAISSSemanticIndex(dimension=384)
    art1 = IndexedArtifact("FN_BRAKE", "C_Function", "ADAS", "ECU_1", "Emergency braking deceleration")
    art2 = IndexedArtifact("FN_CABIN", "C_Function", "Body_Electronics", "ECU_Body", "Cabin climate blower fan")
    
    vecs = embedder.embed_batch([art1.text_content, art2.text_content])
    index.add_artifacts([art1, art2], vecs)

    results = index.search(v1, top_k=2)
    assert len(results) == 2
    assert results[0][0].artifact_id == "FN_BRAKE"


def test_context_filter_subsystem_isolation():
    c_filter = ContextFilter(enforce_subsystem=True, enforce_artifact_type=True)
    
    # Candidate in Body Electronics queried from ADAS
    art_decoy = IndexedArtifact("FN_DECOY", "C_Function", "Body_Electronics", "ECU_Body", "Brake pedal light indicator")
    query_ctx = {"subsystem": "ADAS", "artifact_type": "Requirement"}
    
    res = c_filter.evaluate(art_decoy, query_ctx)
    assert res.passed is False
    assert "Subsystem mismatch" in res.rejection_reason


def test_contextual_retriever_abstention():
    embedder = SemanticEmbedder(dimension=384)
    index = FAISSSemanticIndex(dimension=384)
    art = IndexedArtifact("FN_ALERT", "C_Function", "ADAS", "ECU_1", "Alert driver warning")
    index.add_artifacts([art], embedder.embed_batch([art.text_content]))

    c_filter = ContextFilter()
    retriever = ContextualRetriever(embedder, index, c_filter, similarity_threshold=0.45)

    candidates = retriever.retrieve(
        query_text="Ambiguous unclear alert condition without parameters",
        query_context={"subsystem": "ADAS", "artifact_type": "Requirement"}
    )
    assert len(candidates) > 0
    assert candidates[0].status == "REVIEW_REQUIRED"
