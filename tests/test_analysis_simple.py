"""Simplified Analysis tests"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from analysis import AnalysisEngine, Idea, Cluster, Suggestion

def test_analysis_engine_creation():
    engine = AnalysisEngine()
    assert engine is not None

def test_idea_dataclass():
    idea = Idea(id="1", title="Test", content="Content", tags=["test"])
    assert idea.id == "1"
    assert idea.title == "Test"

def test_cluster_dataclass():
    cluster = Cluster(id=1, ideas=[], keywords=["test"])
    assert cluster.id == 1

def test_suggestion_dataclass():
    sug = Suggestion(title="Test", description="Desc", confidence=0.8)
    assert sug.confidence == 0.8

def test_keyword_extraction():
    engine = AnalysisEngine()
    texts = ["machine learning artificial intelligence"]
    keywords = engine.extract_keywords(texts, top_n=3)
    assert isinstance(keywords, list)
