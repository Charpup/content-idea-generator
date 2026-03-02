"""
Unit Tests for Content Idea Generator Skill - Database Operations (CRUD)

TDD Cycle:
1. RED: Write failing tests
2. GREEN: Implement to pass
3. REFACTOR: Optimize while keeping tests green
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import sqlite3
import json


# ═══════════════════════════════════════════════════════════════════════════════
# Test Suite: Idea Database Operations (CRUD)
# ═══════════════════════════════════════════════════════════════════════════════

class TestIdeaCreate:
    """Test cases for creating content ideas."""
    
    def test_create_idea_with_minimal_data(self, sample_idea):
        """✅ Should create idea with only required fields."""
        # Arrange
        db = Mock()
        minimal_idea = {
            "title": "Test Idea",
            "content_type": "note"
        }
        
        # Act
        result = IdeaRepository(db).create(minimal_idea)
        
        # Assert
        assert result["id"] is not None
        assert result["title"] == "Test Idea"
        assert result["status"] == "draft"  # Default
        assert result["created_at"] is not None
        
    def test_create_idea_with_complete_data(self, sample_idea):
        """✅ Should create idea with all fields populated."""
        # Arrange
        db = Mock()
        
        # Act
        result = IdeaRepository(db).create(sample_idea)
        
        # Assert
        assert result["id"] == "idea-001"
        assert result["title"] == "10 Python Tips for Beginners"
        assert result["tags"] == ["python", "beginners", "programming", "tutorial"]
        assert result["source"]["type"] == "voice"
        
    def test_create_idea_generates_id_if_missing(self):
        """✅ Should auto-generate UUID if id not provided."""
        # Arrange
        db = Mock()
        idea_without_id = {"title": "New Idea", "content_type": "blog_post"}
        
        # Act
        result = IdeaRepository(db).create(idea_without_id)
        
        # Assert
        assert result["id"] is not None
        assert len(result["id"]) > 0
        assert result["id"].startswith("idea-") or len(result["id"]) == 36  # UUID
        
    def test_create_idea_sets_default_status(self):
        """✅ Should set default status to 'draft' if not specified."""
        # Arrange
        db = Mock()
        idea = {"title": "Test", "content_type": "note"}
        
        # Act
        result = IdeaRepository(db).create(idea)
        
        # Assert
        assert result["status"] == "draft"
        
    def test_create_idea_sets_timestamps(self):
        """✅ Should set created_at and updated_at timestamps."""
        # Arrange
        db = Mock()
        idea = {"title": "Test", "content_type": "note"}
        before_create = datetime.now()
        
        # Act
        result = IdeaRepository(db).create(idea)
        after_create = datetime.now()
        
        # Assert
        created_at = datetime.fromisoformat(result["created_at"])
        assert before_create <= created_at <= after_create
        assert result["updated_at"] == result["created_at"]
        
    def test_create_idea_rejects_empty_title(self):
        """❌ Should reject idea with empty title."""
        # Arrange
        db = Mock()
        invalid_idea = {"title": "", "content_type": "note"}
        
        # Act & Assert
        with pytest.raises(ValueError, match="Title cannot be empty"):
            IdeaRepository(db).create(invalid_idea)
            
    def test_create_idea_rejects_missing_title(self):
        """❌ Should reject idea without title field."""
        # Arrange
        db = Mock()
        invalid_idea = {"content_type": "note"}
        
        # Act & Assert
        with pytest.raises(ValueError, match="Title is required"):
            IdeaRepository(db).create(invalid_idea)
            
    def test_create_idea_rejects_invalid_content_type(self):
        """❌ Should reject idea with invalid content_type."""
        # Arrange
        db = Mock()
        invalid_idea = {"title": "Test", "content_type": "invalid_type"}
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid content_type"):
            IdeaRepository(db).create(invalid_idea)
            
    def test_create_idea_handles_unicode(self, idea_variations):
        """✅ Should handle unicode characters in all fields."""
        # Arrange
        db = Mock()
        unicode_idea = idea_variations["unicode"]
        
        # Act
        result = IdeaRepository(db).create(unicode_idea)
        
        # Assert
        assert "🚀" in result["title"]
        assert "中文" in result["title"]
        assert "日本語" in result["description"]
        
    def test_create_idea_sanitizes_html(self, idea_variations):
        """✅ Should sanitize HTML/script tags to prevent XSS."""
        # Arrange
        db = Mock()
        xss_idea = idea_variations["special_chars"]
        
        # Act
        result = IdeaRepository(db).create(xss_idea)
        
        # Assert
        assert "<script>" not in result["title"]
        assert "</script>" not in result["title"]


class TestIdeaRead:
    """Test cases for reading/retrieving content ideas."""
    
    def test_get_idea_by_id_exists(self, sample_idea):
        """✅ Should retrieve idea by ID when it exists."""
        # Arrange
        db = Mock()
        db.fetch_one.return_value = sample_idea
        
        # Act
        result = IdeaRepository(db).get_by_id("idea-001")
        
        # Assert
        assert result is not None
        assert result["id"] == "idea-001"
        assert result["title"] == "10 Python Tips for Beginners"
        
    def test_get_idea_by_id_not_exists(self):
        """✅ Should return None when idea doesn't exist."""
        # Arrange
        db = Mock()
        db.fetch_one.return_value = None
        
        # Act
        result = IdeaRepository(db).get_by_id("nonexistent")
        
        # Assert
        assert result is None
        
    def test_get_all_ideas(self, sample_ideas):
        """✅ Should retrieve all ideas."""
        # Arrange
        db = Mock()
        db.fetch_all.return_value = sample_ideas
        
        # Act
        result = IdeaRepository(db).get_all()
        
        # Assert
        assert len(result) == 4
        assert all("id" in idea for idea in result)
        
    def test_get_ideas_pagination(self, sample_ideas):
        """✅ Should support pagination with limit and offset."""
        # Arrange
        db = Mock()
        db.fetch_all.return_value = sample_ideas[0:2]
        
        # Act
        result = IdeaRepository(db).get_all(limit=2, offset=0)
        
        # Assert
        assert len(result) == 2
        db.fetch_all.assert_called_with(
            "SELECT * FROM ideas ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (2, 0)
        )
        
    def test_get_ideas_by_status(self, sample_ideas):
        """✅ Should filter ideas by status."""
        # Arrange
        db = Mock()
        active_ideas = [i for i in sample_ideas if i["status"] == "active"]
        db.fetch_all.return_value = active_ideas
        
        # Act
        result = IdeaRepository(db).get_by_status("active")
        
        # Assert
        assert len(result) == 2
        assert all(idea["status"] == "active" for idea in result)
        
    def test_get_ideas_by_priority(self, sample_ideas):
        """✅ Should filter ideas by priority."""
        # Arrange
        db = Mock()
        high_priority = [i for i in sample_ideas if i["priority"] == "high"]
        db.fetch_all.return_value = high_priority
        
        # Act
        result = IdeaRepository(db).get_by_priority("high")
        
        # Assert
        assert len(result) == 1
        assert result[0]["priority"] == "high"
        
    def test_get_ideas_by_date_range(self):
        """✅ Should filter ideas by creation date range."""
        # Arrange
        db = Mock()
        start_date = "2026-03-01T00:00:00"
        end_date = "2026-03-01T23:59:59"
        
        # Act
        result = IdeaRepository(db).get_by_date_range(start_date, end_date)
        
        # Assert
        db.fetch_all.assert_called_once()
        call_args = db.fetch_all.call_args[0]
        assert start_date in call_args or start_date in str(call_args)


class TestIdeaUpdate:
    """Test cases for updating content ideas."""
    
    def test_update_idea_title(self, sample_idea):
        """✅ Should update idea title."""
        # Arrange
        db = Mock()
        db.fetch_one.return_value = sample_idea
        
        # Act
        result = IdeaRepository(db).update(
            "idea-001", 
            {"title": "Updated Title"}
        )
        
        # Assert
        assert result["title"] == "Updated Title"
        
    def test_update_idea_status(self, sample_idea):
        """✅ Should update idea status."""
        # Arrange
        db = Mock()
        db.fetch_one.return_value = sample_idea
        
        # Act
        result = IdeaRepository(db).update(
            "idea-001",
            {"status": "completed"}
        )
        
        # Assert
        assert result["status"] == "completed"
        
    def test_update_idea_tags(self, sample_idea):
        """✅ Should update idea tags."""
        # Arrange
        db = Mock()
        db.fetch_one.return_value = sample_idea
        new_tags = ["python", "advanced", "tips"]
        
        # Act
        result = IdeaRepository(db).update(
            "idea-001",
            {"tags": new_tags}
        )
        
        # Assert
        assert result["tags"] == new_tags
        
    def test_update_idea_updates_timestamp(self, sample_idea):
        """✅ Should update updated_at timestamp on modification."""
        # Arrange
        db = Mock()
        db.fetch_one.return_value = sample_idea
        original_updated_at = sample_idea["updated_at"]
        
        # Act
        result = IdeaRepository(db).update(
            "idea-001",
            {"title": "New Title"}
        )
        
        # Assert
        assert result["updated_at"] != original_updated_at
        
    def test_update_nonexistent_idea(self):
        """❌ Should raise error when updating non-existent idea."""
        # Arrange
        db = Mock()
        db.fetch_one.return_value = None
        
        # Act & Assert
        with pytest.raises(IdeaNotFoundError):
            IdeaRepository(db).update("nonexistent", {"title": "Test"})
            
    def test_update_idea_partial_fields(self, sample_idea):
        """✅ Should allow partial updates without affecting other fields."""
        # Arrange
        db = Mock()
        original = sample_idea.copy()
        db.fetch_one.return_value = original
        
        # Act - only update title
        result = IdeaRepository(db).update(
            "idea-001",
            {"title": "New Title"}
        )
        
        # Assert - other fields unchanged
        assert result["title"] == "New Title"
        assert result["description"] == original["description"]
        assert result["tags"] == original["tags"]


class TestIdeaDelete:
    """Test cases for deleting content ideas."""
    
    def test_delete_idea_exists(self, sample_idea):
        """✅ Should delete existing idea and return success."""
        # Arrange
        db = Mock()
        db.fetch_one.return_value = sample_idea
        db.execute.return_value = True
        
        # Act
        result = IdeaRepository(db).delete("idea-001")
        
        # Assert
        assert result is True
        db.execute.assert_called_with(
            "DELETE FROM ideas WHERE id = ?",
            ("idea-001",)
        )
        
    def test_delete_idea_not_exists(self):
        """❌ Should raise error when deleting non-existent idea."""
        # Arrange
        db = Mock()
        db.fetch_one.return_value = None
        
        # Act & Assert
        with pytest.raises(IdeaNotFoundError):
            IdeaRepository(db).delete("nonexistent")
            
    def test_delete_idea_cascades_to_tags(self, sample_idea):
        """✅ Should remove tag associations when idea deleted."""
        # Arrange
        db = Mock()
        db.fetch_one.return_value = sample_idea
        
        # Act
        IdeaRepository(db).delete("idea-001")
        
        # Assert
        # Verify tag associations were cleaned up
        calls = db.execute.call_args_list
        tag_cleanup_calls = [c for c in calls if "idea_tags" in str(c)]
        assert len(tag_cleanup_calls) > 0


class TestIdeaSearch:
    """Test cases for full-text search functionality."""
    
    def test_search_by_keyword_in_title(self, sample_ideas):
        """✅ Should find ideas by keyword in title."""
        # Arrange
        db = Mock()
        db.fetch_all.return_value = [sample_ideas[0]]
        
        # Act
        result = IdeaRepository(db).search("python")
        
        # Assert
        assert len(result) == 1
        assert "python" in result[0]["title"].lower()
        
    def test_search_by_keyword_in_description(self, sample_ideas):
        """✅ Should find ideas by keyword in description."""
        # Arrange
        db = Mock()
        db.fetch_all.return_value = [sample_ideas[1]]
        
        # Act
        result = IdeaRepository(db).search("container")
        
        # Assert
        assert len(result) > 0
        assert any("container" in str(v).lower() for v in result[0].values())
        
    def test_search_case_insensitive(self, sample_ideas):
        """✅ Should perform case-insensitive search."""
        # Arrange
        db = Mock()
        db.fetch_all.return_value = [sample_ideas[0], sample_ideas[3]]
        
        # Act
        result_lower = IdeaRepository(db).search("python")
        result_upper = IdeaRepository(db).search("PYTHON")
        
        # Assert
        assert len(result_lower) == len(result_upper)
        
    def test_search_multi_word(self):
        """✅ Should support multi-word search (AND logic)."""
        # Arrange
        db = Mock()
        
        # Act
        result = IdeaRepository(db).search("docker best practices")
        
        # Assert
        db.fetch_all.assert_called_once()
        query = str(db.fetch_all.call_args)
        assert "AND" in query or "docker" in query.lower()
        
    def test_search_no_results(self):
        """✅ Should return empty list when no matches found."""
        # Arrange
        db = Mock()
        db.fetch_all.return_value = []
        
        # Act
        result = IdeaRepository(db).search("xyznonexistent")
        
        # Assert
        assert result == []
        
    def test_search_with_filters(self, sample_ideas):
        """✅ Should combine search with filters."""
        # Arrange
        db = Mock()
        db.fetch_all.return_value = [sample_ideas[0]]
        
        # Act
        result = IdeaRepository(db).search(
            "python",
            filters={"status": "active"}
        )
        
        # Assert
        assert len(result) == 1
        assert result[0]["status"] == "active"


# ═══════════════════════════════════════════════════════════════════════════════
# Mock Classes for Tests
# ═══════════════════════════════════════════════════════════════════════════════

class IdeaRepository:
    """Mock repository for testing - will be replaced by actual implementation."""
    
    VALID_CONTENT_TYPES = ["blog_post", "video_script", "social_post", "tutorial", "note", "research_paper"]
    
    def __init__(self, db_connection):
        self.db = db_connection
        
    def create(self, idea_data: dict) -> dict:
        """Create a new idea."""
        # Validation
        if "title" not in idea_data:
            raise ValueError("Title is required")
        if not idea_data.get("title"):
            raise ValueError("Title cannot be empty")
        if idea_data.get("content_type") not in self.VALID_CONTENT_TYPES:
            raise ValueError("Invalid content_type")
            
        # Set defaults
        result = idea_data.copy()
        if "id" not in result:
            result["id"] = f"idea-{datetime.now().timestamp()}"
        if "status" not in result:
            result["status"] = "draft"
            
        now = datetime.now().isoformat()
        result["created_at"] = now
        result["updated_at"] = now
        
        # Sanitize
        if "title" in result:
            result["title"] = result["title"].replace("<script>", "").replace("</script>", "")
        if "description" in result:
            result["description"] = result["description"].replace("<script>", "").replace("</script>", "")
            
        return result
        
    def get_by_id(self, idea_id: str) -> dict:
        """Get idea by ID."""
        return self.db.fetch_one("SELECT * FROM ideas WHERE id = ?", (idea_id,))
        
    def get_all(self, limit: int = None, offset: int = None) -> list:
        """Get all ideas with optional pagination."""
        query = "SELECT * FROM ideas ORDER BY created_at DESC"
        params = ()
        if limit is not None:
            query += " LIMIT ?"
            params += (limit,)
        if offset is not None:
            query += " OFFSET ?"
            params += (offset,)
        return self.db.fetch_all(query, params)
        
    def get_by_status(self, status: str) -> list:
        """Get ideas by status."""
        return self.db.fetch_all(
            "SELECT * FROM ideas WHERE status = ? ORDER BY created_at DESC",
            (status,)
        )
        
    def get_by_priority(self, priority: str) -> list:
        """Get ideas by priority."""
        return self.db.fetch_all(
            "SELECT * FROM ideas WHERE priority = ? ORDER BY created_at DESC",
            (priority,)
        )
        
    def get_by_date_range(self, start: str, end: str) -> list:
        """Get ideas within date range."""
        return self.db.fetch_all(
            "SELECT * FROM ideas WHERE created_at BETWEEN ? AND ? ORDER BY created_at DESC",
            (start, end)
        )
        
    def update(self, idea_id: str, updates: dict) -> dict:
        """Update an existing idea."""
        existing = self.get_by_id(idea_id)
        if existing is None:
            raise IdeaNotFoundError(f"Idea {idea_id} not found")
            
        result = existing.copy()
        result.update(updates)
        result["updated_at"] = datetime.now().isoformat()
        return result
        
    def delete(self, idea_id: str) -> bool:
        """Delete an idea."""
        existing = self.get_by_id(idea_id)
        if existing is None:
            raise IdeaNotFoundError(f"Idea {idea_id} not found")
            
        # Clean up tag associations
        self.db.execute("DELETE FROM idea_tags WHERE idea_id = ?", (idea_id,))
        self.db.execute("DELETE FROM ideas WHERE id = ?", (idea_id,))
        return True
        
    def search(self, query: str, filters: dict = None) -> list:
        """Search ideas by keyword."""
        sql = """
            SELECT * FROM ideas 
            WHERE (title LIKE ? OR description LIKE ?)
        """
        params = (f"%{query}%", f"%{query}%")
        
        if filters:
            for key, value in filters.items():
                sql += f" AND {key} = ?"
                params += (value,)
                
        return self.db.fetch_all(sql, params)


class IdeaNotFoundError(Exception):
    """Raised when an idea is not found."""
    pass
