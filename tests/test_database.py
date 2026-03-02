"""
Content Idea Generator - Database Module Tests
TDD Test Suite for Database Module (TC-001 to TC-010)
"""

import pytest
import sqlite3
import tempfile
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def temp_db_path():
    """Create a temporary database file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, "test.db")


@pytest.fixture
def empty_db():
    """Create an in-memory database with schema."""
    from src.database import DatabaseManager
    db = DatabaseManager(":memory:", init_schema=True)
    yield db
    db.close()


@pytest.fixture
def sample_tags(empty_db):
    """Create sample tags."""
    repo = empty_db.tag_repository
    tags = []
    for name in ["python", "javascript", "tutorial", "advanced", "beginner"]:
        tag = repo.create(name)
        tags.append(tag)
    return tags


@pytest.fixture
def sample_categories(empty_db):
    """Create category hierarchy: Tech → Programming → Python/JavaScript."""
    repo = empty_db.category_repository
    tech = repo.create("Technology", description="Tech content")
    programming = repo.create("Programming", parent_id=tech.id, description="Programming content")
    python = repo.create("Python", parent_id=programming.id, description="Python programming")
    javascript = repo.create("JavaScript", parent_id=programming.id, description="JS programming")
    return {
        "tech": tech,
        "programming": programming,
        "python": python,
        "javascript": javascript
    }


@pytest.fixture
def sample_ideas(empty_db, sample_tags, sample_categories):
    """Create sample ideas with tags and categories."""
    idea_repo = empty_db.idea_repository
    tag_repo = empty_db.tag_repository
    
    ideas = []
    
    # Idea 1: Python decorators tutorial
    idea1 = idea_repo.create(
        title="Python Decorators Tutorial",
        content="A comprehensive guide to Python decorators",
        source="text",
        category_id=sample_categories["python"].id,
        tags=["python", "tutorial"]
    )
    ideas.append(idea1)
    
    # Idea 2: JavaScript async guide
    idea2 = idea_repo.create(
        title="JavaScript Async Guide",
        content="Understanding async/await in JavaScript",
        source="text",
        category_id=sample_categories["javascript"].id,
        tags=["javascript", "tutorial"]
    )
    ideas.append(idea2)
    
    # Idea 3: Python machine learning
    idea3 = idea_repo.create(
        title="Python Machine Learning",
        content="Introduction to machine learning with Python",
        source="text",
        category_id=sample_categories["python"].id,
        tags=["python", "advanced"]
    )
    ideas.append(idea3)
    
    # Idea 4: Beginner Python tips
    idea4 = idea_repo.create(
        title="Beginner Python Tips",
        content="Tips for Python beginners",
        source="text",
        category_id=sample_categories["python"].id,
        tags=["python", "beginner"]
    )
    ideas.append(idea4)
    
    return ideas


# ============================================================================
# TC-001: Database Initialization
# ============================================================================

class TestTC001DatabaseInitialization:
    """TC-001: Database initialization creates all tables and indexes."""
    
    def test_database_file_created(self, temp_db_path):
        """Test that database file is created on initialization."""
        from src.database import DatabaseManager
        
        assert not os.path.exists(temp_db_path)
        db = DatabaseManager(temp_db_path, init_schema=True)
        
        assert os.path.exists(temp_db_path)
        db.close()
    
    def test_all_tables_created(self, empty_db):
        """Test that all required tables are created."""
        cursor = empty_db.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        
        required_tables = {
            "ideas", "tags", "categories", "idea_tags", 
            "content_items", "content_fts", "schema_version"
        }
        
        assert required_tables.issubset(tables), f"Missing tables: {required_tables - tables}"
    
    def test_all_indexes_created(self, empty_db):
        """Test that all required indexes are created."""
        cursor = empty_db.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = {row[0] for row in cursor.fetchall()}
        
        required_indexes = {
            "idx_ideas_category", "idx_ideas_status", "idx_ideas_created",
            "idx_categories_parent", "idx_categories_path",
            "idx_content_idea", "idx_ideatag_tag"
        }
        
        assert required_indexes.issubset(indexes), f"Missing indexes: {required_indexes - indexes}"
    
    def test_fts5_virtual_table_created(self, empty_db):
        """Test that FTS5 virtual table is created."""
        cursor = empty_db.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='content_fts'")
        result = cursor.fetchone()
        
        assert result is not None, "FTS5 virtual table not found"
    
    def test_fts_triggers_created(self, empty_db):
        """Test that FTS auto-sync triggers are created."""
        cursor = empty_db.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger'")
        triggers = {row[0] for row in cursor.fetchall()}
        
        required_triggers = {
            "content_items_ai", "content_items_ad", "content_items_au"
        }
        
        assert required_triggers.issubset(triggers), f"Missing triggers: {required_triggers - triggers}"
    
    def test_existing_database_connection(self, temp_db_path):
        """Test that existing database can be connected without data loss."""
        from src.database import DatabaseManager
        
        # Create initial database
        db1 = DatabaseManager(temp_db_path, init_schema=True)
        cursor = db1.connection.cursor()
        cursor.execute("INSERT INTO tags (name, display_name) VALUES ('test', 'Test')")
        db1.connection.commit()
        db1.close()
        
        # Reconnect
        db2 = DatabaseManager(temp_db_path, init_schema=False)
        cursor = db2.connection.cursor()
        cursor.execute("SELECT name FROM tags WHERE name='test'")
        result = cursor.fetchone()
        
        assert result is not None, "Data lost after reconnection"
        assert result[0] == "test"
        db2.close()


# ============================================================================
# TC-002: Idea CRUD Operations
# ============================================================================

class TestTC002IdeaCRUD:
    """TC-002: Idea CRUD operations with tag associations."""
    
    def test_create_idea_with_tags(self, empty_db, sample_tags):
        """Test creating an idea with tags."""
        idea = empty_db.idea_repository.create(
            title="Python Decorators",
            content="A guide to Python decorators",
            source="text",
            tags=["python", "tutorial"]
        )
        
        assert idea.id is not None
        assert idea.title == "Python Decorators"
        assert idea.content == "A guide to Python decorators"
        assert idea.source == "text"
        assert idea.status == "active"
        assert idea.created_at is not None
        assert idea.updated_at is not None
    
    def test_retrieve_idea_by_id(self, empty_db, sample_tags):
        """Test retrieving an idea by ID."""
        repo = empty_db.idea_repository
        created = repo.create(
            title="Test Idea",
            content="Test content",
            tags=["python"]
        )
        
        retrieved = repo.get_by_id(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.title == "Test Idea"
        assert retrieved.content == "Test content"
    
    def test_update_idea_preserves_relations(self, empty_db, sample_tags, sample_categories):
        """Test that updating an idea preserves tag and category associations."""
        repo = empty_db.idea_repository
        
        # Create idea with tags and category
        idea = repo.create(
            title="Original Title",
            content="Original content",
            category_id=sample_categories["python"].id,
            tags=["python", "tutorial"]
        )
        original_updated_at = idea.updated_at
        
        # Update content
        updated = repo.update(idea.id, content="Updated content")
        
        assert updated.content == "Updated content"
        assert updated.title == "Original Title"  # Unchanged
        assert updated.category_id == sample_categories["python"].id  # Preserved
        assert updated.updated_at >= original_updated_at  # Timestamp updated
    
    def test_soft_delete_idea(self, empty_db, sample_tags):
        """Test soft deleting an idea."""
        repo = empty_db.idea_repository
        idea = repo.create(title="To Delete", content="Content", tags=["python"])
        
        result = repo.delete(idea.id, soft=True)
        
        assert result is True
        
        # Verify idea still exists but is archived
        cursor = empty_db.connection.cursor()
        cursor.execute("SELECT status FROM ideas WHERE id=?", (idea.id,))
        status = cursor.fetchone()[0]
        assert status == "archived"
    
    def test_hard_delete_idea(self, empty_db, sample_tags):
        """Test hard deleting an idea."""
        repo = empty_db.idea_repository
        idea = repo.create(title="To Delete", content="Content", tags=["python"])
        idea_id = idea.id
        
        result = repo.delete(idea_id, soft=False)
        
        assert result is True
        
        # Verify idea is completely removed
        retrieved = repo.get_by_id(idea_id)
        assert retrieved is None
        
        # Verify tag associations are cleaned up
        cursor = empty_db.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM idea_tags WHERE idea_id=?", (idea_id,))
        count = cursor.fetchone()[0]
        assert count == 0


# ============================================================================
# TC-003: Tag Management
# ============================================================================

class TestTC003TagManagement:
    """TC-003: Tag management with duplicate prevention."""
    
    def test_create_tag_normalized(self, empty_db):
        """Test that tag names are normalized to lowercase."""
        repo = empty_db.tag_repository
        tag = repo.create("Python")
        
        assert tag.name == "python"
        assert tag.display_name == "Python"
    
    def test_prevent_duplicate_tags(self, empty_db):
        """Test that duplicate tags are prevented."""
        repo = empty_db.tag_repository
        
        # Create first tag
        tag1 = repo.create("Python")
        
        # Try to create duplicate (different case)
        tag2 = repo.create("python")
        
        # Should return existing tag
        assert tag2.id == tag1.id
    
    def test_delete_tag_with_references_blocked(self, empty_db, sample_tags):
        """Test that tags with references cannot be deleted."""
        repo = empty_db.tag_repository
        
        # Create idea using the tag
        empty_db.idea_repository.create(
            title="Test",
            content="Content",
            tags=["python"]
        )
        
        # Try to delete the tag
        python_tag = repo.get_by_name("python")
        
        with pytest.raises(Exception) as exc_info:
            repo.delete(python_tag.id)
        
        assert "references" in str(exc_info.value).lower() or "exists" in str(exc_info.value).lower()
    
    def test_delete_unused_tag_succeeds(self, empty_db):
        """Test that unused tags can be deleted."""
        repo = empty_db.tag_repository
        tag = repo.create("unused")
        
        result = repo.delete(tag.id)
        
        assert result is True
        
        # Verify tag is deleted
        retrieved = repo.get_by_id(tag.id)
        assert retrieved is None
    
    def test_get_or_create_tags_batch(self, empty_db):
        """Test batch get or create tags."""
        repo = empty_db.tag_repository
        
        # Create initial tag
        repo.create("python")
        
        # Get or create batch (mix of existing and new)
        tags = repo.get_or_create(["python", "javascript", "Python"])
        
        # Should return 2 unique tags
        assert len(tags) == 2
        names = {t.name for t in tags}
        assert names == {"python", "javascript"}


# ============================================================================
# TC-004: Category Hierarchy
# ============================================================================

class TestTC004CategoryHierarchy:
    """TC-004: Category hierarchy with cycle prevention."""
    
    def test_create_nested_category(self, empty_db):
        """Test creating nested categories."""
        repo = empty_db.category_repository
        
        tech = repo.create("Technology")
        programming = repo.create("Programming", parent_id=tech.id)
        
        assert programming.parent_id == tech.id
        assert programming.level == 1
    
    def test_get_category_descendants(self, empty_db):
        """Test getting all descendants of a category."""
        repo = empty_db.category_repository
        
        # Create hierarchy: Tech → Programming → Python
        tech = repo.create("Technology")
        programming = repo.create("Programming", parent_id=tech.id)
        python = repo.create("Python", parent_id=programming.id)
        javascript = repo.create("JavaScript", parent_id=programming.id)
        
        descendants = repo.get_descendants(tech.id)
        
        descendant_names = {d.name for d in descendants}
        assert descendant_names == {"Programming", "Python", "JavaScript"}
    
    def test_get_category_path(self, empty_db):
        """Test getting path from root to category."""
        repo = empty_db.category_repository
        
        # Create hierarchy
        tech = repo.create("Technology")
        programming = repo.create("Programming", parent_id=tech.id)
        python = repo.create("Python", parent_id=programming.id)
        
        path = repo.get_path(python.id)
        
        path_names = [p.name for p in path]
        assert path_names == ["Technology", "Programming", "Python"]
    
    def test_prevent_circular_reference(self, empty_db):
        """Test that circular references are prevented."""
        repo = empty_db.category_repository
        
        # Create hierarchy: A → B → C
        cat_a = repo.create("Category A")
        cat_b = repo.create("Category B", parent_id=cat_a.id)
        cat_c = repo.create("Category C", parent_id=cat_b.id)
        
        # Try to set C's parent to A (would create cycle)
        with pytest.raises(Exception) as exc_info:
            repo.update(cat_a.id, parent_id=cat_c.id)
        
        assert "circular" in str(exc_info.value).lower() or "cycle" in str(exc_info.value).lower()


# ============================================================================
# TC-005: Content Items
# ============================================================================

class TestTC005ContentItems:
    """TC-005: Content items for multi-input capture."""
    
    def test_create_text_content_item(self, empty_db, sample_tags):
        """Test creating a text content item."""
        idea_repo = empty_db.idea_repository
        content_repo = empty_db.content_repository
        
        idea = idea_repo.create(title="Test Idea", content="Main content", tags=["python"])
        
        item = content_repo.create(
            idea_id=idea.id,
            content_type="text",
            content_text="Additional text content",
            source_path=None
        )
        
        assert item.id is not None
        assert item.idea_id == idea.id
        assert item.content_type == "text"
        assert item.content_text == "Additional text content"
    
    def test_create_voice_content_item(self, empty_db, sample_tags):
        """Test creating a voice content item with transcription."""
        idea_repo = empty_db.idea_repository
        content_repo = empty_db.content_repository
        
        idea = idea_repo.create(title="Voice Idea", content="Voice note", tags=["python"])
        
        item = content_repo.create(
            idea_id=idea.id,
            content_type="voice",
            content_text="Transcribed voice text",
            source_path="/path/to/audio.mp3",
            metadata={"duration": 120}
        )
        
        assert item.content_type == "voice"
        assert item.source_path == "/path/to/audio.mp3"
        assert item.metadata == {"duration": 120}
    
    def test_create_screenshot_content_item(self, empty_db, sample_tags):
        """Test creating a screenshot content item with OCR text."""
        idea_repo = empty_db.idea_repository
        content_repo = empty_db.content_repository
        
        idea = idea_repo.create(title="Screenshot Idea", content="Screenshot note", tags=["python"])
        
        item = content_repo.create(
            idea_id=idea.id,
            content_type="screenshot",
            content_text="OCR extracted text from image",
            source_path="/path/to/screenshot.png",
            metadata={"width": 1920, "height": 1080}
        )
        
        assert item.content_type == "screenshot"
        assert "OCR" in item.content_text
    
    def test_get_idea_with_content(self, empty_db, sample_tags):
        """Test retrieving an idea with its content items."""
        idea_repo = empty_db.idea_repository
        content_repo = empty_db.content_repository
        
        idea = idea_repo.create(title="Multi-content Idea", content="Main", tags=["python"])
        
        # Create multiple content items
        content_repo.create(idea_id=idea.id, content_type="text", content_text="Text 1")
        content_repo.create(idea_id=idea.id, content_type="voice", content_text="Voice 1")
        content_repo.create(idea_id=idea.id, content_type="screenshot", content_text="OCR 1")
        
        # Retrieve idea with content
        retrieved = idea_repo.get_by_id(idea.id, include_content=True)
        
        assert retrieved is not None
        assert hasattr(retrieved, 'content_items')
        assert len(retrieved.content_items) == 3
    
    def test_create_batch_content_items(self, empty_db, sample_tags):
        """Test batch creation of content items."""
        idea_repo = empty_db.idea_repository
        content_repo = empty_db.content_repository
        
        idea = idea_repo.create(title="Batch Idea", content="Main", tags=["python"])
        
        items_data = [
            {"idea_id": idea.id, "content_type": "text", "content_text": f"Text {i}"}
            for i in range(5)
        ]
        
        items = content_repo.create_batch(items_data)
        
        assert len(items) == 5
        assert all(item.id is not None for item in items)


# ============================================================================
# TC-006: FTS5 Full-Text Search
# ============================================================================

class TestTC006FullTextSearch:
    """TC-006: FTS5 full-text search with filters."""
    
    def test_basic_fulltext_search(self, empty_db, sample_ideas):
        """Test basic full-text search."""
        repo = empty_db.idea_repository
        
        results = repo.search("python")
        
        # Should find ideas with "python" in title or content
        assert len(results) >= 3  # We created 4 python-related ideas
        
        # Results should be ranked by relevance
        titles = [r.title for r in results]
        assert any("Python" in t for t in titles)
    
    def test_phrase_search(self, empty_db, sample_tags, sample_categories):
        """Test phrase search with quotes."""
        repo = empty_db.idea_repository
        content_repo = empty_db.content_repository
        
        # Create ideas with specific phrases
        idea1 = repo.create(
            title="Machine Learning",
            content="Introduction to machine learning concepts",
            tags=["python"]
        )
        idea2 = repo.create(
            title="Learning Machines",
            content="Machines that learn",
            tags=["python"]
        )
        
        # Add content items for FTS
        content_repo.create(idea_id=idea1.id, content_type="text", content_text="machine learning is great")
        content_repo.create(idea_id=idea2.id, content_type="text", content_text="learning machines are different")
        
        # Search for exact phrase
        results = repo.search('"machine learning"')
        
        # Should only find the first idea
        assert len(results) == 1
        assert results[0].title == "Machine Learning"
    
    def test_prefix_search(self, empty_db, sample_tags, sample_categories):
        """Test prefix search with wildcard."""
        repo = empty_db.idea_repository
        content_repo = empty_db.content_repository
        
        # Create ideas with words starting with "doc"
        idea1 = repo.create(title="Documentation", content="Docs content", tags=["python"])
        idea2 = repo.create(title="Document", content="A document", tags=["python"])
        idea3 = repo.create(title="Other", content="Something else", tags=["python"])
        
        content_repo.create(idea_id=idea1.id, content_type="text", content_text="documentation guide")
        content_repo.create(idea_id=idea2.id, content_type="text", content_text="document file")
        content_repo.create(idea_id=idea3.id, content_type="text", content_text="other content")
        
        results = repo.search("doc*")
        
        # Should find ideas with words starting with "doc"
        titles = {r.title for r in results}
        assert "Documentation" in titles or "Document" in titles
    
    def test_filtered_search_by_tag(self, empty_db, sample_ideas):
        """Test search filtered by tags."""
        repo = empty_db.idea_repository
        
        # Search for "tutorial" filtered by python tag
        results = repo.search("tutorial", tags=["python"])
        
        # Should only return python tutorials
        for result in results:
            # Verify it's a python-tagged idea
            assert any(tag.name == "python" for tag in result.tags)


# ============================================================================
# TC-007: Tag-based Filtering
# ============================================================================

class TestTC007TagFiltering:
    """TC-007: Tag-based filtering and statistics."""
    
    def test_filter_by_single_tag(self, empty_db, sample_ideas):
        """Test filtering ideas by single tag."""
        repo = empty_db.idea_repository
        
        results = repo.get_by_tags(["python"])
        
        # Should return all python-tagged ideas
        assert len(results) == 3  # We created 3 python ideas
        for idea in results:
            assert any(tag.name == "python" for tag in idea.tags)
    
    def test_filter_by_multiple_tags_and(self, empty_db, sample_ideas):
        """Test filtering by multiple tags with AND logic."""
        repo = empty_db.idea_repository
        
        results = repo.get_by_tags(["python", "tutorial"], match_all=True)
        
        # Should only return ideas with BOTH tags
        for idea in results:
            tag_names = {t.name for t in idea.tags}
            assert "python" in tag_names
            assert "tutorial" in tag_names
    
    def test_filter_by_multiple_tags_or(self, empty_db, sample_ideas):
        """Test filtering by multiple tags with OR logic."""
        repo = empty_db.idea_repository
        
        results = repo.get_by_tags(["python", "javascript"], match_all=False)
        
        # Should return ideas with EITHER tag
        assert len(results) == 4  # 3 python + 1 javascript
        for idea in results:
            tag_names = {t.name for t in idea.tags}
            assert "python" in tag_names or "javascript" in tag_names
    
    def test_get_tag_statistics(self, empty_db, sample_ideas):
        """Test getting tag usage statistics."""
        repo = empty_db.tag_repository
        
        stats = repo.get_stats()
        
        # Should return stats for all tags
        stats_dict = {s.name: s.count for s in stats}
        
        assert stats_dict.get("python") == 3  # 3 python ideas
        assert stats_dict.get("javascript") == 1  # 1 javascript idea
        assert stats_dict.get("tutorial") == 2  # 2 tutorial ideas


# ============================================================================
# TC-008: Transaction Support
# ============================================================================

class TestTC008Transactions:
    """TC-008: Transaction rollback on error."""
    
    def test_transaction_rollback_on_error(self, empty_db, sample_tags):
        """Test that transactions roll back on error."""
        repo = empty_db.idea_repository
        
        # Count ideas before
        cursor = empty_db.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM ideas")
        count_before = cursor.fetchone()[0]
        
        # Try to create idea with invalid category_id (should fail FK constraint)
        try:
            repo.create(
                title="Test",
                content="Content",
                category_id=99999,  # Non-existent
                tags=["python"]
            )
        except Exception:
            pass  # Expected to fail
        
        # Count ideas after
        cursor.execute("SELECT COUNT(*) FROM ideas")
        count_after = cursor.fetchone()[0]
        
        # Should be same count (transaction rolled back)
        assert count_after == count_before
    
    def test_foreign_key_constraint(self, empty_db):
        """Test that foreign key constraints are enforced."""
        cursor = empty_db.connection.cursor()
        
        # Try to insert idea with non-existent category
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute(
                "INSERT INTO ideas (title, category_id) VALUES (?, ?)",
                ("Test", 99999)
            )
            empty_db.connection.commit()


# ============================================================================
# TC-009: Performance Benchmarks
# ============================================================================

class TestTC009Performance:
    """TC-009: Query performance benchmarks."""
    
    def test_query_by_id_performance(self, empty_db, sample_tags):
        """Test that ID queries are fast (< 10ms)."""
        import time
        
        repo = empty_db.idea_repository
        
        # Create test idea
        idea = repo.create(title="Perf Test", content="Content", tags=["python"])
        
        # Benchmark 100 queries
        start = time.time()
        for _ in range(100):
            repo.get_by_id(idea.id)
        elapsed = (time.time() - start) * 1000 / 100  # ms per query
        
        assert elapsed < 10, f"ID query too slow: {elapsed:.2f}ms"
    
    def test_paginated_list_performance(self, empty_db, sample_tags):
        """Test that paginated queries are fast (< 50ms)."""
        import time
        
        repo = empty_db.idea_repository
        
        # Create multiple ideas
        for i in range(50):
            repo.create(title=f"Idea {i}", content=f"Content {i}", tags=["python"])
        
        # Benchmark pagination
        start = time.time()
        for _ in range(100):
            repo.list(limit=10, offset=0)
        elapsed = (time.time() - start) * 1000 / 100  # ms per query
        
        assert elapsed < 50, f"Paginated query too slow: {elapsed:.2f}ms"


# ============================================================================
# TC-010: In-Memory Database
# ============================================================================

class TestTC010InMemoryDatabase:
    """TC-010: In-memory database for testing."""
    
    def test_in_memory_database_works(self):
        """Test that in-memory database works identically to file-based."""
        from src.database import DatabaseManager
        
        db = DatabaseManager(":memory:", init_schema=True)
        
        # Create and retrieve data
        idea = db.idea_repository.create(title="Test", content="Content", tags=["python"])
        retrieved = db.idea_repository.get_by_id(idea.id)
        
        assert retrieved is not None
        assert retrieved.title == "Test"
        
        db.close()
    
    def test_in_memory_isolation(self):
        """Test that in-memory databases are isolated."""
        from src.database import DatabaseManager
        
        # Create first database with data
        db1 = DatabaseManager(":memory:", init_schema=True)
        db1.idea_repository.create(title="DB1 Idea", content="Content", tags=["python"])
        
        # Create second database
        db2 = DatabaseManager(":memory:", init_schema=True)
        
        # Second database should be empty
        cursor = db2.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM ideas")
        count = cursor.fetchone()[0]
        
        assert count == 0
        
        db1.close()
        db2.close()
    
    def test_no_file_system_artifacts(self):
        """Test that in-memory database creates no files."""
        from src.database import DatabaseManager
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            initial_files = set(os.listdir(tmpdir))
            
            db = DatabaseManager(":memory:", init_schema=True)
            db.idea_repository.create(title="Test", content="Content", tags=["python"])
            db.close()
            
            final_files = set(os.listdir(tmpdir))
            
            assert initial_files == final_files, "In-memory database created files"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# ============================================================================
# Additional Tests for Coverage
# ============================================================================

class TestAdditionalCoverage:
    """Additional tests to reach 80%+ coverage."""
    
    def test_tag_update(self, empty_db):
        """Test updating a tag name."""
        repo = empty_db.tag_repository
        tag = repo.create("oldname")
        
        updated = repo.update(tag.id, "newname")
        
        assert updated.name == "newname"
        assert updated.display_name == "newname"
    
    def test_tag_get_by_id_not_found(self, empty_db):
        """Test getting non-existent tag by ID."""
        result = empty_db.tag_repository.get_by_id(99999)
        assert result is None
    
    def test_tag_get_by_name_not_found(self, empty_db):
        """Test getting non-existent tag by name."""
        result = empty_db.tag_repository.get_by_name("nonexistent")
        assert result is None
    
    def test_category_get_by_id_not_found(self, empty_db):
        """Test getting non-existent category by ID."""
        result = empty_db.category_repository.get_by_id(99999)
        assert result is None
    
    def test_category_update_name_only(self, empty_db):
        """Test updating only category name."""
        repo = empty_db.category_repository
        cat = repo.create("OldName")
        
        updated = repo.update(cat.id, name="NewName")
        
        assert updated.name == "NewName"
    
    def test_category_update_description_only(self, empty_db):
        """Test updating only category description."""
        repo = empty_db.category_repository
        cat = repo.create("Name", description="Old desc")
        
        updated = repo.update(cat.id, description="New desc")
        
        assert updated.description == "New desc"
    
    def test_category_delete_with_reassign(self, empty_db, sample_categories):
        """Test deleting category with reassignment."""
        repo = empty_db.category_repository
        
        # Create idea in programming category
        idea = empty_db.idea_repository.create(
            title="Test",
            content="Content",
            category_id=sample_categories["programming"].id,
            tags=["python"]
        )
        
        # Delete programming category and reassign to tech
        result = repo.delete(
            sample_categories["programming"].id,
            reassign_to=sample_categories["tech"].id
        )
        
        assert result is True
        
        # Verify idea was reassigned
        updated_idea = empty_db.idea_repository.get_by_id(idea.id)
        assert updated_idea.category_id == sample_categories["tech"].id
    
    def test_category_get_descendants_empty(self, empty_db):
        """Test getting descendants of non-existent category."""
        result = empty_db.category_repository.get_descendants(99999)
        assert result == []
    
    def test_category_get_path_empty(self, empty_db):
        """Test getting path of non-existent category."""
        result = empty_db.category_repository.get_path(99999)
        assert result == []
    
    def test_content_item_update(self, empty_db, sample_tags):
        """Test updating content item."""
        idea_repo = empty_db.idea_repository
        content_repo = empty_db.content_repository
        
        idea = idea_repo.create(title="Test", content="Content", tags=["python"])
        item = content_repo.create(idea_id=idea.id, content_type="text", content_text="Original")
        
        updated = content_repo.update(item.id, {"content_text": "Updated"})
        
        assert updated.content_text == "Updated"
    
    def test_content_item_update_metadata(self, empty_db, sample_tags):
        """Test updating content item metadata."""
        idea_repo = empty_db.idea_repository
        content_repo = empty_db.content_repository
        
        idea = idea_repo.create(title="Test", content="Content", tags=["python"])
        item = content_repo.create(idea_id=idea.id, content_type="voice", content_text="Text")
        
        updated = content_repo.update(item.id, {"metadata": {"duration": 300}})
        
        assert updated.metadata == {"duration": 300}
    
    def test_content_item_delete(self, empty_db, sample_tags):
        """Test deleting content item."""
        idea_repo = empty_db.idea_repository
        content_repo = empty_db.content_repository
        
        idea = idea_repo.create(title="Test", content="Content", tags=["python"])
        item = content_repo.create(idea_id=idea.id, content_type="text", content_text="Text")
        
        result = content_repo.delete(item.id)
        
        assert result is True
        
        # Verify deletion
        items = content_repo.get_by_idea(idea.id)
        assert len(items) == 0
    
    def test_content_item_delete_not_found(self, empty_db):
        """Test deleting non-existent content item."""
        result = empty_db.content_repository.delete(99999)
        assert result is False
    
    def test_idea_update_title(self, empty_db, sample_tags):
        """Test updating only idea title."""
        repo = empty_db.idea_repository
        idea = repo.create(title="Old Title", content="Content", tags=["python"])
        
        updated = repo.update(idea.id, title="New Title")
        
        assert updated.title == "New Title"
        assert updated.content == "Content"  # Unchanged
    
    def test_idea_update_category(self, empty_db, sample_tags, sample_categories):
        """Test updating idea category."""
        repo = empty_db.idea_repository
        idea = repo.create(title="Test", content="Content", tags=["python"])
        
        updated = repo.update(idea.id, category_id=sample_categories["tech"].id)
        
        assert updated.category_id == sample_categories["tech"].id
    
    def test_idea_update_priority(self, empty_db, sample_tags):
        """Test updating idea priority."""
        repo = empty_db.idea_repository
        idea = repo.create(title="Test", content="Content", tags=["python"])
        
        updated = repo.update(idea.id, priority=5)
        
        assert updated.priority == 5
    
    def test_idea_update_clear_tags(self, empty_db, sample_tags):
        """Test updating idea with empty tags list."""
        repo = empty_db.idea_repository
        idea = repo.create(title="Test", content="Content", tags=["python", "tutorial"])
        
        updated = repo.update(idea.id, tags=[])
        
        assert len(updated.tags) == 0
    
    def test_idea_list_with_status_filter(self, empty_db, sample_tags):
        """Test listing ideas with status filter."""
        repo = empty_db.idea_repository
        idea = repo.create(title="Test", content="Content", tags=["python"])
        
        # Soft delete the idea
        repo.delete(idea.id, soft=True)
        
        # List only active ideas
        active = repo.list(status="active")
        archived = repo.list(status="archived")
        
        assert len(active) == 0
        assert len(archived) == 1
    
    def test_idea_delete_not_found(self, empty_db):
        """Test deleting non-existent idea."""
        result = empty_db.idea_repository.delete(99999)
        assert result is False
    
    def test_idea_get_by_id_not_found(self, empty_db):
        """Test getting non-existent idea."""
        result = empty_db.idea_repository.get_by_id(99999)
        assert result is None
    
    def test_database_manager_migration(self, empty_db):
        """Test database migration functionality."""
        result = empty_db.execute_migration(1)
        assert result is True
    
    def test_database_manager_migration_already_current(self, empty_db):
        """Test migration when already at target version."""
        empty_db.execute_migration(1)
        result = empty_db.execute_migration(1)
        assert result is True
