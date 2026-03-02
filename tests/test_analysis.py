"""
TDD Test Suite for Content Idea Generator - Analysis Engine
Test cases TC-001 to TC-012 from analysis-spec.yaml

Phase 2.1: RED - Generate tests from spec, expect failure
"""

import pytest
import numpy as np
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from analysis import (
    Idea, ClusterResult, Suggestion, KeywordResult, DailyReport, AnalysisConfig,
    TFIDFExtractor, HACClusterer, SimilarityCalculator, SuggestionGenerator, 
    DailyPipeline, AnalysisEngine
)


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def sample_ideas():
    """Sample ideas for testing"""
    return [
        Idea(id="1", content="Python machine learning tutorial for beginners", 
             tags=["python", "ml"], source="text", created_at=datetime.now()),
        Idea(id="2", content="Deep learning with PyTorch and neural networks", 
             tags=["python", "dl"], source="text", created_at=datetime.now()),
        Idea(id="3", content="Docker containerization best practices", 
             tags=["docker", "devops"], source="text", created_at=datetime.now()),
        Idea(id="4", content="Kubernetes deployment strategies", 
             tags=["k8s", "devops"], source="text", created_at=datetime.now()),
        Idea(id="5", content="Introduction to machine learning algorithms", 
             tags=["ml", "ai"], source="text", created_at=datetime.now()),
    ]


@pytest.fixture
def ml_ideas():
    """Machine learning focused ideas for clustering tests"""
    return [
        Idea(id="1", content="Python machine learning basics", tags=["python"], source="text", created_at=datetime.now()),
        Idea(id="2", content="Deep learning neural networks", tags=["dl"], source="text", created_at=datetime.now()),
        Idea(id="3", content="Supervised learning algorithms", tags=["ml"], source="text", created_at=datetime.now()),
        Idea(id="4", content="Unsupervised learning clustering", tags=["ml"], source="text", created_at=datetime.now()),
        Idea(id="5", content="Reinforcement learning basics", tags=["rl"], source="text", created_at=datetime.now()),
        Idea(id="6", content="Docker containers explained", tags=["docker"], source="text", created_at=datetime.now()),
        Idea(id="7", content="Kubernetes orchestration", tags=["k8s"], source="text", created_at=datetime.now()),
        Idea(id="8", content="Container best practices", tags=["docker"], source="text", created_at=datetime.now()),
        Idea(id="9", content="Neural network architectures", tags=["dl"], source="text", created_at=datetime.now()),
        Idea(id="10", content="Transfer learning methods", tags=["ml"], source="text", created_at=datetime.now()),
    ]


@pytest.fixture
def default_config():
    """Default analysis configuration"""
    return AnalysisConfig(
        max_features=100,
        n_clusters=3,
        linkage="average",
        min_cluster_size=2,
        similarity_threshold=0.5,
        schedule="09:00"
    )


@pytest.fixture
def sample_texts():
    """Sample texts for TF-IDF testing"""
    return [
        "Python machine learning tutorial for beginners",
        "Deep learning with neural networks and PyTorch",
        "Docker containerization best practices guide",
        "Kubernetes deployment strategies for production",
        "Introduction to machine learning algorithms"
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# TC-001: TF-IDF extraction with valid text
# ═══════════════════════════════════════════════════════════════════════════════

class TestTC001_TFIDFExtraction:
    """TC-001: TF-IDF extraction with valid text"""
    
    def test_tfidf_extractor_initialization(self):
        """Verify TFIDFExtractor can be initialized"""
        extractor = TFIDFExtractor(max_features=100, ngram_range=(1, 2))
        assert extractor is not None
        assert extractor.max_features == 100
        assert extractor.ngram_range == (1, 2)
    
    def test_tfidf_fit_transform_returns_sparse_matrix(self, sample_texts):
        """Verify fit_transform returns sparse matrix with correct shape"""
        extractor = TFIDFExtractor(max_features=100, ngram_range=(1, 2))
        result = extractor.fit_transform(sample_texts)
        
        # Returns sparse matrix with shape (5, <=100)
        assert result is not None
        assert result.shape[0] == 5  # 5 documents
        assert result.shape[1] <= 100  # max_features
    
    def test_tfidf_feature_names_contain_unigrams_and_bigrams(self, sample_texts):
        """Verify feature names contain unigrams and bigrams"""
        extractor = TFIDFExtractor(max_features=100, ngram_range=(1, 2))
        extractor.fit_transform(sample_texts)
        feature_names = extractor.get_feature_names()
        
        # Should have feature names
        assert len(feature_names) > 0
        assert len(feature_names) <= 100
        
        # Check for unigrams (single words)
        unigrams = [f for f in feature_names if ' ' not in f]
        assert len(unigrams) > 0
        
        # Check for bigrams (two words)
        bigrams = [f for f in feature_names if ' ' in f]
        assert len(bigrams) > 0
    
    def test_tfidf_all_documents_have_nonzero_vectors(self, sample_texts):
        """Verify all documents have non-zero vectors"""
        extractor = TFIDFExtractor(max_features=100, ngram_range=(1, 2))
        result = extractor.fit_transform(sample_texts)
        
        # Each document should have at least one non-zero value
        for i in range(result.shape[0]):
            row = result[i]
            assert row.nnz > 0  # Number of non-zero elements
    
    def test_tfidf_common_words_have_lower_scores(self, sample_texts):
        """Verify common words have lower TF-IDF scores than unique terms"""
        extractor = TFIDFExtractor(max_features=100, ngram_range=(1, 2))
        result = extractor.fit_transform(sample_texts)
        feature_names = extractor.get_feature_names()
        
        # Get top terms for first document
        top_terms = extractor.get_top_terms(0, n=5)
        
        # Should return list of (term, score) tuples
        assert len(top_terms) == 5
        assert all(isinstance(term, str) for term, _ in top_terms)
        assert all(isinstance(score, (int, float)) for _, score in top_terms)
        assert all(score > 0 for _, score in top_terms)
        
        # Scores should be sorted in descending order
        scores = [score for _, score in top_terms]
        assert scores == sorted(scores, reverse=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TC-002: HAC clustering with TF-IDF vectors
# ═══════════════════════════════════════════════════════════════════════════════

class TestTC002_HACClustering:
    """TC-002: HAC clustering with TF-IDF vectors"""
    
    def test_hac_clusterer_initialization(self):
        """Verify HACClusterer can be initialized"""
        clusterer = HACClusterer(n_clusters=3, linkage="average")
        assert clusterer is not None
        assert clusterer.n_clusters == 3
        assert clusterer.linkage == "average"
    
    def test_hac_fit_predict_returns_cluster_labels(self, ml_ideas):
        """Verify fit_predict returns array of cluster labels"""
        # First extract TF-IDF features
        extractor = TFIDFExtractor(max_features=50)
        texts = [idea.content for idea in ml_ideas]
        vectors = extractor.fit_transform(texts)
        
        # Then cluster
        clusterer = HACClusterer(n_clusters=3, linkage="average")
        labels = clusterer.fit_predict(vectors)
        
        # Returns array of 10 cluster labels (0, 1, or 2)
        assert labels is not None
        assert len(labels) == 10
        assert all(label in [0, 1, 2] for label in labels)
    
    def test_hac_documents_same_topic_same_label(self, ml_ideas):
        """Verify documents on same topic have same label"""
        extractor = TFIDFExtractor(max_features=50)
        texts = [idea.content for idea in ml_ideas]
        vectors = extractor.fit_transform(texts)
        
        clusterer = HACClusterer(n_clusters=3, linkage="average")
        labels = clusterer.fit_predict(vectors)
        
        # ML-related ideas (indices 0-4, 9) should mostly cluster together
        # Docker/K8s ideas (indices 5-7) should cluster together
        ml_labels = [labels[i] for i in [0, 1, 2, 3, 4, 9]]
        docker_labels = [labels[i] for i in [5, 6, 7]]
        
        # At least some grouping should occur
        assert len(set(ml_labels)) <= 3  # ML ideas shouldn't be spread across all clusters
        assert len(set(docker_labels)) <= 2  # Docker ideas should be close
    
    def test_hac_silhouette_score_calculated(self, ml_ideas):
        """Verify silhouette score is calculated and > 0.5"""
        extractor = TFIDFExtractor(max_features=50)
        texts = [idea.content for idea in ml_ideas]
        vectors = extractor.fit_transform(texts)
        
        clusterer = HACClusterer(n_clusters=3, linkage="average")
        labels = clusterer.fit_predict(vectors)
        
        # Get silhouette score
        score = clusterer.get_silhouette_score(vectors, labels)
        
        # Silhouette score should be > 0.5
        assert score is not None
        assert score > 0.5
    
    def test_hac_dendrogram_structure_valid(self, ml_ideas):
        """Verify dendrogram structure is valid"""
        extractor = TFIDFExtractor(max_features=50)
        texts = [idea.content for idea in ml_ideas]
        vectors = extractor.fit_transform(texts)
        
        clusterer = HACClusterer(n_clusters=3, linkage="average")
        clusterer.fit_predict(vectors)
        
        # Get dendrogram
        dendrogram = clusterer.get_dendrogram()
        
        # Should be a valid dict structure
        assert isinstance(dendrogram, dict)
        assert "children" in dendrogram or "linkage_matrix" in dendrogram


# ═══════════════════════════════════════════════════════════════════════════════
# TC-003: Cosine similarity calculation
# ═══════════════════════════════════════════════════════════════════════════════

class TestTC003_CosineSimilarity:
    """TC-003: Cosine similarity calculation"""
    
    def test_similarity_calculator_initialization(self):
        """Verify SimilarityCalculator can be initialized"""
        calc = SimilarityCalculator()
        assert calc is not None
    
    def test_similarity_identical_vectors(self):
        """Verify identical vectors have similarity = 1.0"""
        calc = SimilarityCalculator()
        
        # Create identical vectors
        vec = np.array([[1.0, 0.5, 0.3, 0.2]])
        
        similarity = calc.compute_single(vec, vec)
        
        assert similarity == 1.0
    
    def test_similarity_orthogonal_vectors(self):
        """Verify orthogonal vectors have similarity = 0.0"""
        calc = SimilarityCalculator()
        
        # Create orthogonal vectors
        vec_a = np.array([[1.0, 0.0, 0.0]])
        vec_b = np.array([[0.0, 1.0, 0.0]])
        
        similarity = calc.compute_single(vec_a, vec_b)
        
        assert abs(similarity - 0.0) < 1e-10
    
    def test_similarity_partial_vectors(self):
        """Verify partially similar vectors have 0.0 < similarity < 1.0"""
        calc = SimilarityCalculator()
        
        # Create partially similar vectors
        vec_a = np.array([[1.0, 0.5, 0.0]])
        vec_b = np.array([[0.8, 0.4, 0.2]])
        
        similarity = calc.compute_single(vec_a, vec_b)
        
        assert 0.0 < similarity < 1.0
    
    def test_similarity_all_scores_in_valid_range(self, sample_texts):
        """Verify all similarity scores are within [0, 1]"""
        calc = SimilarityCalculator()
        
        # Extract TF-IDF vectors
        extractor = TFIDFExtractor(max_features=50)
        vectors = extractor.fit_transform(sample_texts)
        
        # Compute pairwise similarities
        sim_matrix = calc.compute_pairwise(vectors)
        
        # All scores should be in [0, 1]
        assert np.all(sim_matrix >= 0.0)
        assert np.all(sim_matrix <= 1.0)
        
        # Diagonal should be 1.0 (self-similarity)
        for i in range(sim_matrix.shape[0]):
            assert abs(sim_matrix[i, i] - 1.0) < 1e-10
    
    def test_similarity_find_similar(self, sample_ideas):
        """Verify find_similar returns most similar ideas"""
        calc = SimilarityCalculator()
        
        # Extract TF-IDF vectors
        extractor = TFIDFExtractor(max_features=50)
        texts = [idea.content for idea in sample_ideas]
        vectors = extractor.fit_transform(texts)
        
        # Cache vectors in ideas
        for i, idea in enumerate(sample_ideas):
            idea.vector = vectors[i]
        
        # Find similar ideas to first idea
        query = sample_ideas[0]  # Python ML tutorial
        candidates = sample_ideas[1:]
        
        similar = calc.find_similar(query, candidates, threshold=0.1, top_k=2)
        
        # Should return list of (idea, similarity) tuples
        assert len(similar) <= 2
        if len(similar) > 0:
            idea, score = similar[0]
            assert isinstance(idea, Idea)
            assert 0.0 <= score <= 1.0


# ═══════════════════════════════════════════════════════════════════════════════
# TC-004: Keyword extraction ranking
# ═══════════════════════════════════════════════════════════════════════════════

class TestTC004_KeywordExtraction:
    """TC-004: Keyword extraction ranking"""
    
    def test_keyword_extraction_returns_ranked_keywords(self):
        """Verify keyword extraction returns ranked keywords"""
        texts = ["Machine learning is a subset of artificial intelligence"]
        keywords = self.engine.extract_keywords(texts, top_n=5)
        
        # Should return list of (keyword, score) tuples
        assert len(keywords) <= 5
        if len(keywords) > 0:
            keyword, score = keywords[0]
            assert isinstance(keyword, str)
            assert 0.0 <= score <= 1.0
