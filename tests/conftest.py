"""
Test fixtures and mock data for Content Idea Generator Skill.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Any


# ═══════════════════════════════════════════════════════════════════════════════
# Sample Content Ideas
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def sample_idea() -> Dict[str, Any]:
    """Single complete content idea."""
    return {
        "id": "idea-001",
        "title": "10 Python Tips for Beginners",
        "description": "A comprehensive guide covering essential Python tips",
        "content_type": "blog_post",
        "source": {
            "type": "voice",
            "raw_transcription": "I should write about Python tips for beginners",
            "confidence": 0.95,
            "timestamp": datetime(2026, 3, 1, 10, 30, 0).isoformat()
        },
        "tags": ["python", "beginners", "programming", "tutorial"],
        "categories": ["education", "technology"],
        "status": "active",
        "priority": "high",
        "created_at": datetime(2026, 3, 1, 10, 30, 0).isoformat(),
        "updated_at": datetime(2026, 3, 1, 10, 30, 0).isoformat(),
        "metadata": {
            "word_count_estimate": 1500,
            "target_audience": "beginners",
            "seo_keywords": ["python tips", "learn python"]
        }
    }


@pytest.fixture
def sample_ideas() -> List[Dict[str, Any]]:
    """Multiple content ideas for batch testing."""
    return [
        {
            "id": "idea-001",
            "title": "Python Tips for Beginners",
            "description": "Essential Python tips",
            "content_type": "blog_post",
            "source": {"type": "voice", "confidence": 0.95},
            "tags": ["python", "beginners"],
            "categories": ["education", "technology"],
            "status": "active",
            "priority": "high",
            "created_at": datetime(2026, 3, 1, 9, 0, 0).isoformat()
        },
        {
            "id": "idea-002",
            "title": "Docker Best Practices",
            "description": "Container optimization guide",
            "content_type": "video_script",
            "source": {"type": "screenshot", "ocr_confidence": 0.88},
            "tags": ["docker", "devops", "containers"],
            "categories": ["technology", "infrastructure"],
            "status": "active",
            "priority": "medium",
            "created_at": datetime(2026, 3, 1, 11, 0, 0).isoformat()
        },
        {
            "id": "idea-003",
            "title": "AI in Content Creation",
            "description": "How AI is transforming content",
            "content_type": "social_post",
            "source": {"type": "manual"},
            "tags": ["ai", "content", "future"],
            "categories": ["technology", "ai"],
            "status": "draft",
            "priority": "low",
            "created_at": datetime(2026, 3, 1, 14, 0, 0).isoformat()
        },
        {
            "id": "idea-004",
            "title": "React Hooks Deep Dive",
            "description": "Advanced React patterns",
            "content_type": "tutorial",
            "source": {"type": "voice", "confidence": 0.92},
            "tags": ["react", "javascript", "frontend"],
            "categories": ["technology", "web_dev"],
            "status": "archived",
            "priority": "medium",
            "created_at": datetime(2026, 2, 28, 16, 0, 0).isoformat()
        }
    ]


@pytest.fixture
def idea_variations() -> Dict[str, Dict[str, Any]]:
    """Content ideas with different characteristics for edge case testing."""
    return {
        "minimal": {
            "id": "idea-min",
            "title": "X",
            "description": "Y",
            "content_type": "note",
            "source": {"type": "manual"},
            "tags": [],
            "categories": [],
            "status": "draft",
            "priority": "low",
            "created_at": datetime.now().isoformat()
        },
        "maximal": {
            "id": "idea-max",
            "title": "A" * 200,
            "description": "B" * 5000,
            "content_type": "research_paper",
            "source": {
                "type": "voice",
                "raw_transcription": "C" * 10000,
                "confidence": 0.99,
                "timestamp": datetime.now().isoformat(),
                "audio_duration": 3600
            },
            "tags": [f"tag_{i}" for i in range(50)],
            "categories": [f"cat_{i}" for i in range(20)],
            "status": "active",
            "priority": "urgent",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": {
                "word_count_estimate": 50000,
                "target_audience": "experts",
                "seo_keywords": [f"keyword_{i}" for i in range(100)]
            }
        },
        "unicode": {
            "id": "idea-unicode",
            "title": "🚀 中文标题 with émojis 🎉",
            "description": "日本語テキスト العربية Русский",
            "content_type": "blog_post",
            "source": {"type": "manual"},
            "tags": ["中文", "日本語", "emoji_🎨"],
            "categories": ["国际化", "multilingual"],
            "status": "active",
            "priority": "high",
            "created_at": datetime.now().isoformat()
        },
        "special_chars": {
            "id": "idea-special",
            "title": "Test <script>alert('xss')</script> & \"quotes\"",
            "description": "Special chars: < > & \" ' ` ~ ! @ # $ % ^ & * ( )",
            "content_type": "blog_post",
            "source": {"type": "manual"},
            "tags": ["<tag>", "test&test", "quote\"test"],
            "categories": ["security", "testing"],
            "status": "active",
            "priority": "medium",
            "created_at": datetime.now().isoformat()
        }
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Tag & Category Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def sample_tags() -> List[Dict[str, Any]]:
    """Sample tags with metadata."""
    return [
        {"id": "tag-001", "name": "python", "color": "#3776AB", "usage_count": 15},
        {"id": "tag-002", "name": "javascript", "color": "#F7DF1E", "usage_count": 12},
        {"id": "tag-003", "name": "docker", "color": "#2496ED", "usage_count": 8},
        {"id": "tag-004", "name": "ai", "color": "#FF6B6B", "usage_count": 20},
        {"id": "tag-005", "name": "beginners", "color": "#4ECDC4", "usage_count": 5},
        {"id": "tag-006", "name": "advanced", "color": "#95E1D3", "usage_count": 3}
    ]


@pytest.fixture
def sample_categories() -> List[Dict[str, Any]]:
    """Sample categories with hierarchy."""
    return [
        {
            "id": "cat-001",
            "name": "technology",
            "parent_id": None,
            "description": "Tech-related content",
            "idea_count": 25
        },
        {
            "id": "cat-002",
            "name": "programming",
            "parent_id": "cat-001",
            "description": "Programming topics",
            "idea_count": 18
        },
        {
            "id": "cat-003",
            "name": "web_dev",
            "parent_id": "cat-002",
            "description": "Web development",
            "idea_count": 10
        },
        {
            "id": "cat-004",
            "name": "education",
            "parent_id": None,
            "description": "Educational content",
            "idea_count": 12
        }
    ]


@pytest.fixture
def tag_relationships() -> Dict[str, List[str]]:
    """Tag co-occurrence relationships for suggestion testing."""
    return {
        "python": ["programming", "beginners", "django", "data_science"],
        "javascript": ["frontend", "react", "nodejs", "web_dev"],
        "docker": ["devops", "kubernetes", "containers", "infrastructure"],
        "ai": ["machine_learning", "nlp", "gpt", "automation"]
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Voice & OCR Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def voice_transcriptions() -> List[Dict[str, Any]]:
    """Sample voice transcription results."""
    return [
        {
            "audio_file": "voice_001.wav",
            "transcription": "I have an idea for a blog post about Python decorators",
            "confidence": 0.95,
            "language": "en",
            "duration_seconds": 4.5,
            "word_count": 11,
            "extracted_idea": {
                "title": "Python Decorators Guide",
                "tags": ["python", "decorators", "advanced"]
            }
        },
        {
            "audio_file": "voice_002.wav",
            "transcription": "Note to self create a video about Docker best practices",
            "confidence": 0.88,
            "language": "en",
            "duration_seconds": 3.8,
            "word_count": 10,
            "extracted_idea": {
                "title": "Docker Best Practices Video",
                "tags": ["docker", "devops", "video"]
            }
        },
        {
            "audio_file": "voice_003.wav",
            "transcription": "",  # Empty/unclear audio
            "confidence": 0.15,
            "language": "unknown",
            "duration_seconds": 2.0,
            "word_count": 0,
            "extracted_idea": None
        },
        {
            "audio_file": "voice_004.wav",
            "transcription": "Um uh so like I was thinking maybe we could do something about AI",
            "confidence": 0.72,
            "language": "en",
            "duration_seconds": 6.2,
            "word_count": 15,
            "extracted_idea": {
                "title": "AI Content Ideas",
                "tags": ["ai", "ideas"]
            }
        }
    ]


@pytest.fixture
def ocr_results() -> List[Dict[str, Any]]:
    """Sample OCR results from screenshots."""
    return [
        {
            "image_file": "screenshot_001.png",
            "text": "Meeting Notes:\n- Blog post: Kubernetes vs Docker Swarm\n- Target: DevOps audience\n- Due: Next week",
            "confidence": 0.92,
            "language": "en",
            "extracted_idea": {
                "title": "Kubernetes vs Docker Swarm",
                "description": "Comparison article for DevOps audience",
                "tags": ["kubernetes", "docker", "devops", "comparison"]
            }
        },
        {
            "image_file": "screenshot_002.png",
            "text": "TODO:\n1. Write React tutorial\n2. Create video script\n3. Schedule social posts",
            "confidence": 0.85,
            "language": "en",
            "extracted_ideas": [
                {
                    "title": "React Tutorial",
                    "tags": ["react", "tutorial"]
                },
                {
                    "title": "Video Script",
                    "tags": ["video", "script"]
                }
            ]
        },
        {
            "image_file": "screenshot_003.png",
            "text": "",  # Empty/unreadable image
            "confidence": 0.05,
            "language": "unknown",
            "extracted_idea": None
        },
        {
            "image_file": "screenshot_004.jpg",
            "text": " blurry distorted text ",
            "confidence": 0.35,
            "language": "en",
            "extracted_idea": None
        }
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# Report Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def daily_report_data() -> Dict[str, Any]:
    """Expected structure for daily analysis report."""
    today = datetime(2026, 3, 1)
    yesterday = today - timedelta(days=1)
    
    return {
        "report_date": today.isoformat(),
        "period": {
            "start": yesterday.isoformat(),
            "end": today.isoformat()
        },
        "summary": {
            "total_ideas": 5,
            "new_ideas": 3,
            "by_source": {
                "voice": 2,
                "screenshot": 1,
                "manual": 2
            },
            "by_status": {
                "active": 3,
                "draft": 1,
                "archived": 1
            }
        },
        "top_tags": [
            {"tag": "python", "count": 2},
            {"tag": "docker", "count": 1},
            {"tag": "ai", "count": 1}
        ],
        "top_categories": [
            {"category": "technology", "count": 4},
            {"category": "education", "count": 1}
        ],
        "suggestions": [
            {
                "type": "cluster",
                "message": "You have 2 Python-related ideas. Consider creating a series.",
                "related_ideas": ["idea-001", "idea-004"]
            },
            {
                "type": "priority",
                "message": "1 high-priority idea needs attention",
                "related_ideas": ["idea-001"]
            }
        ],
        "trends": {
            "ideas_per_day": [3, 2, 4, 5, 3],
            "avg_confidence": 0.89
        }
    }


@pytest.fixture
def weekly_report_data() -> Dict[str, Any]:
    """Expected structure for weekly analysis report."""
    return {
        "report_date": datetime(2026, 3, 1).isoformat(),
        "period": {
            "start": (datetime(2026, 3, 1) - timedelta(days=7)).isoformat(),
            "end": datetime(2026, 3, 1).isoformat()
        },
        "summary": {
            "total_ideas": 28,
            "new_ideas": 15,
            "completed_ideas": 8,
            "conversion_rate": 0.53
        },
        "category_distribution": {
            "technology": 18,
            "education": 6,
            "lifestyle": 4
        },
        "content_type_distribution": {
            "blog_post": 12,
            "video_script": 8,
            "social_post": 5,
            "tutorial": 3
        },
        "insights": [
            "Most productive day: Wednesday (6 ideas)",
            "Top performing category: Technology",
            "Suggested focus: Video content (growing trend)"
        ]
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Search Test Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def search_test_cases() -> List[Dict[str, Any]]:
    """Test cases for full-text search functionality."""
    return [
        {
            "query": "python",
            "expected_results": ["idea-001", "idea-004"],
            "description": "Basic keyword search"
        },
        {
            "query": "docker container",
            "expected_results": ["idea-002"],
            "description": "Multi-word search"
        },
        {
            "query": "PYTHON",  # Case insensitive
            "expected_results": ["idea-001", "idea-004"],
            "description": "Case insensitive search"
        },
        {
            "query": "beginners tutorial",
            "expected_results": ["idea-001"],
            "description": "Tag + type search"
        },
        {
            "query": "nonexistent",
            "expected_results": [],
            "description": "No results search"
        },
        {
            "query": "",
            "expected_results": ["idea-001", "idea-002", "idea-003", "idea-004"],
            "description": "Empty query returns all"
        }
    ]


@pytest.fixture
def filter_test_cases() -> List[Dict[str, Any]]:
    """Test cases for idea filtering."""
    return [
        {
            "filters": {"status": "active"},
            "expected_count": 2,
            "description": "Filter by status"
        },
        {
            "filters": {"priority": "high"},
            "expected_count": 1,
            "description": "Filter by priority"
        },
        {
            "filters": {"content_type": "blog_post"},
            "expected_count": 1,
            "description": "Filter by content type"
        },
        {
            "filters": {"tags": ["python"]},
            "expected_count": 2,
            "description": "Filter by single tag"
        },
        {
            "filters": {"tags": ["python", "docker"]},
            "expected_count": 3,
            "description": "Filter by multiple tags (OR)"
        },
        {
            "filters": {"status": "active", "priority": "high"},
            "expected_count": 1,
            "description": "Multiple filters (AND)"
        },
        {
            "filters": {"created_after": "2026-03-01T00:00:00"},
            "expected_count": 3,
            "description": "Date range filter"
        }
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# Mock Service Responses
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def mock_stt_response() -> Dict[str, Any]:
    """Mock STT service response."""
    return {
        "success": True,
        "text": "I have an idea for a blog post about Python decorators",
        "confidence": 0.95,
        "language": "en",
        "duration": 4.5,
        "words": [
            {"word": "I", "start": 0.0, "end": 0.1, "confidence": 0.99},
            {"word": "have", "start": 0.1, "end": 0.3, "confidence": 0.98},
            {"word": "an", "start": 0.3, "end": 0.4, "confidence": 0.97},
            {"word": "idea", "start": 0.4, "end": 0.7, "confidence": 0.96}
        ]
    }


@pytest.fixture
def mock_ocr_response() -> Dict[str, Any]:
    """Mock OCR service response."""
    return {
        "success": True,
        "text": "Meeting Notes:\n- Blog post: Kubernetes vs Docker Swarm",
        "confidence": 0.92,
        "language": "en",
        "regions": [
            {
                "bbox": [10, 10, 400, 50],
                "text": "Meeting Notes:",
                "confidence": 0.95
            },
            {
                "bbox": [10, 60, 500, 100],
                "text": "- Blog post: Kubernetes vs Docker Swarm",
                "confidence": 0.89
            }
        ]
    }


@pytest.fixture
def mock_llm_analysis_response() -> Dict[str, Any]:
    """Mock LLM content analysis response."""
    return {
        "success": True,
        "analysis": {
            "title": "Python Decorators Guide",
            "description": "Comprehensive guide to Python decorators",
            "suggested_tags": ["python", "decorators", "advanced", "programming"],
            "suggested_categories": ["technology", "programming"],
            "content_type": "tutorial",
            "priority": "high",
            "estimated_read_time": 15,
            "target_audience": "intermediate developers",
            "seo_score": 0.85
        }
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Error Fixtures
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def database_errors() -> List[Dict[str, Any]]:
    """Common database error scenarios."""
    return [
        {
            "error_type": "connection_error",
            "message": "Failed to connect to database",
            "recoverable": True
        },
        {
            "error_type": "unique_violation",
            "message": "Duplicate key value violates unique constraint",
            "recoverable": False
        },
        {
            "error_type": "foreign_key_violation",
            "message": "Insert or update violates foreign key constraint",
            "recoverable": False
        },
        {
            "error_type": "timeout",
            "message": "Query timeout after 30s",
            "recoverable": True
        }
    ]


@pytest.fixture
def service_errors() -> List[Dict[str, Any]]:
    """External service error scenarios."""
    return [
        {
            "service": "stt",
            "error_type": "rate_limit",
            "status_code": 429,
            "message": "Rate limit exceeded",
            "retry_after": 60
        },
        {
            "service": "ocr",
            "error_type": "invalid_image",
            "status_code": 400,
            "message": "Image format not supported"
        },
        {
            "service": "llm",
            "error_type": "timeout",
            "status_code": 504,
            "message": "Gateway timeout"
        }
    ]
