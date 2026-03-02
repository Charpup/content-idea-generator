"""
Content Idea Generator - Analysis Engine

Provides intelligent content analysis including:
- HAC Clustering for idea grouping
- TF-IDF feature extraction
- Cosine similarity calculation
- Topic suggestion generation
- Keyword extraction
"""

from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class Idea:
    """Represents a content idea"""
    id: str
    title: str
    content: str
    tags: List[str]
    created_at: Optional[str] = None


@dataclass
class Cluster:
    """Represents a cluster of related ideas"""
    id: int = 0
    ideas: List[Idea] = None
    centroid: np.ndarray = None
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.ideas is None:
            self.ideas = []
        if self.keywords is None:
            self.keywords = []
        if self.centroid is None:
            self.centroid = np.array([])


@dataclass
class Suggestion:
    """Content suggestion with confidence score"""
    title: str = ""
    description: str = ""
    confidence: float = 0.0
    related_ideas: List[str] = None
    suggested_tags: List[str] = None
    
    def __post_init__(self):
        if self.related_ideas is None:
            self.related_ideas = []
        if self.suggested_tags is None:
            self.suggested_tags = []


class AnalysisEngine:
    """
    Analysis Engine for content ideas.
    
    Provides clustering, similarity analysis, and content suggestions.
    """
    
    def __init__(self, 
                 max_features: int = 1000,
                 min_df: int = 1,
                 max_df: float = 1.0,
                 ngram_range: Tuple[int, int] = (1, 2)):
        """
        Initialize the analysis engine.
        
        Args:
            max_features: Maximum number of TF-IDF features
            min_df: Minimum document frequency
            max_df: Maximum document frequency
            ngram_range: Range of n-grams to extract
        """
        self.max_features = max_features
        self.min_df = min_df
        self.max_df = max_df
        self.ngram_range = ngram_range
        
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            min_df=min_df,
            max_df=max_df,
            ngram_range=ngram_range,
            stop_words='english'
        )
        self.clusters: List[Cluster] = []
        self.idea_vectors: Dict[str, np.ndarray] = {}
        
    def fit_transform(self, ideas: List[Idea]) -> np.ndarray:
        """
        Fit the vectorizer and transform ideas to TF-IDF vectors.
        
        Args:
            ideas: List of ideas to analyze
            
        Returns:
            TF-IDF matrix
        """
        texts = [f"{idea.title} {idea.content}" for idea in ideas]
        vectors = self.vectorizer.fit_transform(texts)
        
        # Store idea vectors for later use
        for i, idea in enumerate(ideas):
            self.idea_vectors[idea.id] = vectors[i]
            
        return vectors
    
    def cluster_ideas(self, 
                     ideas: List[Idea],
                     n_clusters: Optional[int] = None,
                     linkage: str = 'ward') -> List[Cluster]:
        """
        Cluster ideas using Hierarchical Agglomerative Clustering.
        
        Args:
            ideas: List of ideas to cluster
            n_clusters: Number of clusters (auto-detected if None)
            linkage: Linkage method ('ward', 'complete', 'average', 'single')
            
        Returns:
            List of clusters
        """
        if len(ideas) < 2:
            return []
            
        # Transform to TF-IDF vectors
        vectors = self.fit_transform(ideas)
        
        # Auto-determine number of clusters
        if n_clusters is None:
            n_clusters = max(2, min(len(ideas) // 3, 10))
        
        # Perform HAC clustering
        clustering = AgglomerativeClustering(
            n_clusters=n_clusters,
            linkage=linkage
        )
        labels = clustering.fit_predict(vectors.toarray())
        
        # Create clusters
        cluster_dict = defaultdict(list)
        for i, label in enumerate(labels):
            cluster_dict[label].append(ideas[i])
        
        # Build cluster objects with centroids and keywords
        self.clusters = []
        feature_names = self.vectorizer.get_feature_names_out()
        
        for label, cluster_ideas in cluster_dict.items():
            # Calculate centroid
            cluster_vectors = [self.idea_vectors[idea.id].toarray()[0] 
                             for idea in cluster_ideas]
            centroid = np.mean(cluster_vectors, axis=0)
            
            # Extract top keywords for cluster
            top_indices = centroid.argsort()[-5:][::-1]
            keywords = [feature_names[i] for i in top_indices]
            
            cluster = Cluster(
                id=label,
                ideas=cluster_ideas,
                centroid=centroid,
                keywords=keywords
            )
            self.clusters.append(cluster)
        
        return self.clusters
    
    def calculate_similarity(self, idea1: Idea, idea2: Idea) -> float:
        """
        Calculate cosine similarity between two ideas.
        
        Args:
            idea1: First idea
            idea2: Second idea
            
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        if idea1.id not in self.idea_vectors or idea2.id not in self.idea_vectors:
            # Transform on the fly if not cached
            texts = [f"{idea1.title} {idea1.content}", 
                    f"{idea2.title} {idea2.content}"]
            vectors = self.vectorizer.transform(texts)
            return cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        
        vec1 = self.idea_vectors[idea1.id].reshape(1, -1)
        vec2 = self.idea_vectors[idea2.id].reshape(1, -1)
        return cosine_similarity(vec1, vec2)[0][0]
    
    def find_similar_ideas(self, 
                          idea: Idea, 
                          ideas: List[Idea],
                          threshold: float = 0.3,
                          top_n: int = 5) -> List[Tuple[Idea, float]]:
        """
        Find ideas similar to the given idea.
        
        Args:
            idea: Reference idea
            ideas: List of ideas to search
            threshold: Minimum similarity threshold
            top_n: Maximum number of results
            
        Returns:
            List of (idea, similarity_score) tuples
        """
        similarities = []
        
        for other in ideas:
            if other.id != idea.id:
                sim = self.calculate_similarity(idea, other)
                if sim >= threshold:
                    similarities.append((other, sim))
        
        # Sort by similarity and return top N
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_n]
    
    def extract_keywords(self, 
                        texts: List[str], 
                        top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Extract keywords from texts using TF-IDF scores.
        
        Args:
            texts: List of text documents
            top_n: Number of top keywords to return
            
        Returns:
            List of (keyword, score) tuples
        """
        if not texts:
            return []
            
        # Fit TF-IDF on the texts
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        
        # Get feature names
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Calculate mean TF-IDF scores across all documents
        mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
        
        # Get top keywords
        top_indices = mean_scores.argsort()[-top_n:][::-1]
        keywords = [(feature_names[i], float(mean_scores[i])) 
                   for i in top_indices if mean_scores[i] > 0]
        
        return keywords
    
    def generate_suggestions(self, 
                           ideas: List[Idea],
                           min_confidence: float = 0.5) -> List[Suggestion]:
        """
        Generate content suggestions based on idea clusters.
        
        Args:
            ideas: List of ideas to analyze
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of content suggestions
        """
        if len(ideas) < 2:
            return []
            
        # Cluster ideas
        clusters = self.cluster_ideas(ideas)
        suggestions = []
        
        for cluster in clusters:
            if len(cluster.ideas) < 2:
                continue
                
            # Calculate confidence based on cluster cohesion
            confidence = min(1.0, len(cluster.ideas) / 5.0)
            
            if confidence >= min_confidence:
                # Generate suggestion title from keywords
                title = f"Create content about: {', '.join(cluster.keywords[:3])}"
                
                # Generate description
                description = f"Based on {len(cluster.ideas)} related ideas. "
                description += f"Key themes: {', '.join(cluster.keywords)}"
                
                # Collect related idea IDs and tags
                related_ids = [idea.id for idea in cluster.ideas]
                all_tags = []
                for idea in cluster.ideas:
                    all_tags.extend(idea.tags)
                suggested_tags = list(set(all_tags))[:5]
                
                suggestion = Suggestion(
                    title=title,
                    description=description,
                    confidence=confidence,
                    related_ideas=related_ids,
                    suggested_tags=suggested_tags
                )
                suggestions.append(suggestion)
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        return suggestions
    
    def run_daily_analysis(self, ideas: List[Idea]) -> Dict[str, Any]:
        """
        Run complete daily analysis pipeline.
        
        Args:
            ideas: List of ideas captured today
            
        Returns:
            Analysis results dictionary
        """
        if not ideas:
            return {
                "total_ideas": 0,
                "clusters": [],
                "suggestions": [],
                "keywords": []
            }
        
        # Cluster ideas
        clusters = self.cluster_ideas(ideas)
        
        # Generate suggestions
        suggestions = self.generate_suggestions(ideas)
        
        # Extract keywords from all ideas
        texts = [f"{idea.title} {idea.content}" for idea in ideas]
        keywords = self.extract_keywords(texts, top_n=10)
        
        return {
            "total_ideas": len(ideas),
            "clusters": clusters,
            "suggestions": suggestions,
            "keywords": keywords
        }
