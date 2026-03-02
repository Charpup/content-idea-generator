"""
Content Idea Generator - Models Module

Data models for content items, ideas, categories, and tags.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class ContentType(Enum):
    """Content type enumeration"""
    ARTICLE = "article"
    BOOK = "book"
    VIDEO = "video"
    PODCAST = "podcast"
    TWEET = "tweet"
    NOTE = "note"
    IDEA = "idea"


class ContentStatus(Enum):
    """Content status enumeration"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DRAFT = "draft"


class IdeaStatus(Enum):
    """Idea status enumeration"""
    NEW = "new"
    DEVELOPING = "developing"
    READY = "ready"
    USED = "used"
    ARCHIVED = "archived"


class RelationType(Enum):
    """Idea relation type enumeration"""
    RELATED = "related"
    INSPIRED_BY = "inspired_by"
    BUILDS_ON = "builds_on"
    CONTRADICTS = "contradicts"
    SIMILAR = "similar"


@dataclass
class Category:
    """Category model"""
    id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    parent_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


@dataclass
class Tag:
    """Tag model"""
    id: Optional[int] = None
    name: str = ""
    color: str = "#6366f1"
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class ContentItem:
    """Content item model"""
    id: Optional[int] = None
    type: ContentType = ContentType.ARTICLE
    title: str = ""
    content: Optional[str] = None
    source: Optional[str] = None
    author: Optional[str] = None
    category_id: Optional[int] = None
    status: ContentStatus = ContentStatus.ACTIVE
    priority: int = 3
    tags: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if isinstance(self.type, str):
            self.type = ContentType(self.type)
        if isinstance(self.status, str):
            self.status = ContentStatus(self.status)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'type': self.type.value,
            'title': self.title,
            'content': self.content,
            'source': self.source,
            'author': self.author,
            'category_id': self.category_id,
            'status': self.status.value,
            'priority': self.priority,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


@dataclass
class TextSnippet:
    """Text snippet model"""
    id: Optional[int] = None
    content_id: int = 0
    snippet_text: str = ""
    context: Optional[str] = None
    source_ref: Optional[str] = None
    page_ref: Optional[str] = None
    position: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'content_id': self.content_id,
            'snippet_text': self.snippet_text,
            'context': self.context,
            'source_ref': self.source_ref,
            'page_ref': self.page_ref,
            'position': self.position,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class GoldSentence:
    """Gold sentence model"""
    id: Optional[int] = None
    content_id: int = 0
    sentence: str = ""
    context: Optional[str] = None
    rating: int = 3
    usage_count: int = 0
    last_used_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'content_id': self.content_id,
            'sentence': self.sentence,
            'context': self.context,
            'rating': self.rating,
            'usage_count': self.usage_count,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class Idea:
    """Idea model"""
    id: Optional[int] = None
    content_id: int = 0
    concept: str = ""
    elaboration: Optional[str] = None
    use_cases: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    priority: int = 3
    status: IdeaStatus = IdeaStatus.NEW
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if isinstance(self.status, str):
            self.status = IdeaStatus(self.status)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'content_id': self.content_id,
            'concept': self.concept,
            'elaboration': self.elaboration,
            'use_cases': self.use_cases,
            'tags': self.tags,
            'priority': self.priority,
            'status': self.status.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


@dataclass
class IdeaRelation:
    """Idea relation model"""
    idea_id: int = 0
    related_idea_id: int = 0
    relation_type: RelationType = RelationType.RELATED
    strength: int = 3
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if isinstance(self.relation_type, str):
            self.relation_type = RelationType(self.relation_type)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'idea_id': self.idea_id,
            'related_idea_id': self.related_idea_id,
            'relation_type': self.relation_type.value,
            'strength': self.strength,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


__all__ = [
    'ContentType',
    'ContentStatus',
    'IdeaStatus',
    'RelationType',
    'Category',
    'Tag',
    'ContentItem',
    'TextSnippet',
    'GoldSentence',
    'Idea',
    'IdeaRelation'
]
