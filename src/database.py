"""
Content Idea Generator - Database Module
SQLite-based storage with FTS5 full-text search
"""

import sqlite3
import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from contextlib import contextmanager


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class Idea:
    """Core entity representing a content idea."""
    id: Optional[int] = None
    title: str = ""
    content: Optional[str] = None
    source: Optional[str] = None
    category_id: Optional[int] = None
    status: str = "active"
    priority: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    tags: List['Tag'] = field(default_factory=list)
    content_items: List['ContentItem'] = field(default_factory=list)


@dataclass
class Tag:
    """Label for categorizing ideas."""
    id: Optional[int] = None
    name: str = ""  # Normalized (lowercase)
    display_name: str = ""  # Original display name
    color: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class Category:
    """Hierarchical category for organizing ideas."""
    id: Optional[int] = None
    name: str = ""
    description: Optional[str] = None
    parent_id: Optional[int] = None
    path: Optional[str] = None
    level: int = 0
    created_at: Optional[str] = None


@dataclass
class ContentItem:
    """Raw input data (text, voice transcription, OCR)."""
    id: Optional[int] = None
    idea_id: int = 0
    content_type: str = ""  # text/voice/screenshot
    content_text: Optional[str] = None
    source_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None


@dataclass
class TagStats:
    """Tag usage statistics."""
    id: int
    name: str
    count: int


# ============================================================================
# Exceptions
# ============================================================================

class CircularReferenceError(Exception):
    """Raised when attempting to create a circular category reference."""
    pass


class ReferenceExistsError(Exception):
    """Raised when attempting to delete an entity that has references."""
    pass


# ============================================================================
# Schema SQL
# ============================================================================

SCHEMA_SQL = """
-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Categories (create first due to self-reference)
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    parent_id INTEGER,
    path VARCHAR(500),
    level INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- Ideas
CREATE TABLE IF NOT EXISTS ideas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    source VARCHAR(50),
    category_id INTEGER,
    status VARCHAR(20) DEFAULT 'active',
    priority INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- Tags
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    display_name VARCHAR(50) NOT NULL,
    color VARCHAR(7),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Idea-Tag junction
CREATE TABLE IF NOT EXISTS idea_tags (
    idea_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (idea_id, tag_id),
    FOREIGN KEY (idea_id) REFERENCES ideas(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Content Items
CREATE TABLE IF NOT EXISTS content_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idea_id INTEGER NOT NULL,
    content_type VARCHAR(20) NOT NULL,
    content_text TEXT,
    source_path VARCHAR(500),
    metadata JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idea_id) REFERENCES ideas(id) ON DELETE CASCADE
);

-- FTS5 Virtual Table
CREATE VIRTUAL TABLE IF NOT EXISTS content_fts USING fts5(
    content_text,
    content='content_items',
    content_rowid='id'
);

-- FTS5 Triggers for auto-sync
CREATE TRIGGER IF NOT EXISTS content_items_ai AFTER INSERT ON content_items BEGIN
    INSERT INTO content_fts(rowid, content_text) VALUES (new.id, new.content_text);
END;

CREATE TRIGGER IF NOT EXISTS content_items_ad AFTER DELETE ON content_items BEGIN
    INSERT INTO content_fts(content_fts, rowid, content_text) VALUES ('delete', old.id, old.content_text);
END;

CREATE TRIGGER IF NOT EXISTS content_items_au AFTER UPDATE ON content_items BEGIN
    INSERT INTO content_fts(content_fts, rowid, content_text) VALUES ('delete', old.id, old.content_text);
    INSERT INTO content_fts(rowid, content_text) VALUES (new.id, new.content_text);
END;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_ideas_category ON ideas(category_id);
CREATE INDEX IF NOT EXISTS idx_ideas_status ON ideas(status);
CREATE INDEX IF NOT EXISTS idx_ideas_created ON ideas(created_at);
CREATE INDEX IF NOT EXISTS idx_categories_parent ON categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_categories_path ON categories(path);
CREATE INDEX IF NOT EXISTS idx_content_idea ON content_items(idea_id);
CREATE INDEX IF NOT EXISTS idx_ideatag_tag ON idea_tags(tag_id);
"""


# ============================================================================
# Repository Classes
# ============================================================================

class TagRepository:
    """Repository for Tag entity operations."""
    
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
    
    def create(self, name: str, color: Optional[str] = None) -> Tag:
        """Create new tag with normalized name."""
        normalized_name = name.lower().strip()
        display_name = name.strip()
        
        cursor = self.connection.cursor()
        
        # Check for existing tag
        cursor.execute("SELECT id, name, display_name, color, created_at FROM tags WHERE name=?", (normalized_name,))
        row = cursor.fetchone()
        
        if row:
            return Tag(id=row[0], name=row[1], display_name=row[2], color=row[3], created_at=row[4])
        
        # Create new tag
        cursor.execute(
            "INSERT INTO tags (name, display_name, color) VALUES (?, ?, ?)",
            (normalized_name, display_name, color)
        )
        self.connection.commit()
        
        return Tag(
            id=cursor.lastrowid,
            name=normalized_name,
            display_name=display_name,
            color=color,
            created_at=datetime.now().isoformat()
        )
    
    def get_by_id(self, tag_id: int) -> Optional[Tag]:
        """Retrieve tag by ID."""
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT id, name, display_name, color, created_at FROM tags WHERE id=?",
            (tag_id,)
        )
        row = cursor.fetchone()
        
        if row:
            return Tag(id=row[0], name=row[1], display_name=row[2], color=row[3], created_at=row[4])
        return None
    
    def get_by_name(self, name: str) -> Optional[Tag]:
        """Retrieve tag by name (case-insensitive)."""
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT id, name, display_name, color, created_at FROM tags WHERE name=?",
            (name.lower().strip(),)
        )
        row = cursor.fetchone()
        
        if row:
            return Tag(id=row[0], name=row[1], display_name=row[2], color=row[3], created_at=row[4])
        return None
    
    def get_or_create(self, names: List[str]) -> List[Tag]:
        """Get existing tags or create new ones."""
        tags = []
        seen = set()
        
        for name in names:
            normalized = name.lower().strip()
            if normalized in seen:
                continue
            seen.add(normalized)
            
            tag = self.create(name)
            tags.append(tag)
        
        return tags
    
    def update(self, tag_id: int, new_name: str) -> Tag:
        """Rename tag, updating all associations."""
        cursor = self.connection.cursor()
        
        normalized_name = new_name.lower().strip()
        display_name = new_name.strip()
        
        cursor.execute(
            "UPDATE tags SET name=?, display_name=? WHERE id=?",
            (normalized_name, display_name, tag_id)
        )
        self.connection.commit()
        
        return self.get_by_id(tag_id)
    
    def delete(self, tag_id: int, force: bool = False) -> bool:
        """Delete tag if no references exist."""
        cursor = self.connection.cursor()
        
        # Check for references
        cursor.execute("SELECT COUNT(*) FROM idea_tags WHERE tag_id=?", (tag_id,))
        count = cursor.fetchone()[0]
        
        if count > 0 and not force:
            raise ReferenceExistsError(f"Tag has {count} references and cannot be deleted")
        
        cursor.execute("DELETE FROM tags WHERE id=?", (tag_id,))
        self.connection.commit()
        
        return cursor.rowcount > 0
    
    def get_stats(self) -> List[TagStats]:
        """Get usage statistics for all tags."""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT t.id, t.name, COUNT(it.idea_id) as count
            FROM tags t
            LEFT JOIN idea_tags it ON t.id = it.tag_id
            GROUP BY t.id, t.name
            ORDER BY count DESC
        """)
        
        return [TagStats(id=row[0], name=row[1], count=row[2]) for row in cursor.fetchall()]


class CategoryRepository:
    """Repository for Category entity operations with hierarchy support."""
    
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
    
    def _update_path_and_level(self, category_id: int, parent_id: Optional[int]) -> None:
        """Update path and level for a category based on parent."""
        cursor = self.connection.cursor()
        
        if parent_id is None:
            path = f"/{category_id}/"
            level = 0
        else:
            cursor.execute("SELECT path, level FROM categories WHERE id=?", (parent_id,))
            row = cursor.fetchone()
            if row:
                path = f"{row[0]}{category_id}/"
                level = row[1] + 1
            else:
                path = f"/{category_id}/"
                level = 0
        
        cursor.execute(
            "UPDATE categories SET path=?, level=? WHERE id=?",
            (path, level, category_id)
        )
        self.connection.commit()
    
    def _is_descendant(self, potential_descendant: int, potential_ancestor: int) -> bool:
        """Check if potential_descendant is a descendant of potential_ancestor."""
        cursor = self.connection.cursor()
        
        current = potential_descendant
        visited = set()
        
        while current is not None:
            if current == potential_ancestor:
                return True
            if current in visited:
                break  # Cycle detected
            visited.add(current)
            
            cursor.execute("SELECT parent_id FROM categories WHERE id=?", (current,))
            row = cursor.fetchone()
            current = row[0] if row else None
        
        return False
    
    def create(self, name: str, parent_id: Optional[int] = None, description: Optional[str] = None) -> Category:
        """Create category with optional parent."""
        cursor = self.connection.cursor()
        
        cursor.execute(
            "INSERT INTO categories (name, description, parent_id) VALUES (?, ?, ?)",
            (name, description, parent_id)
        )
        category_id = cursor.lastrowid
        self.connection.commit()
        
        # Update path and level
        self._update_path_and_level(category_id, parent_id)
        
        return self.get_by_id(category_id)
    
    def get_by_id(self, category_id: int) -> Optional[Category]:
        """Retrieve category by ID."""
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT id, name, description, parent_id, path, level, created_at FROM categories WHERE id=?",
            (category_id,)
        )
        row = cursor.fetchone()
        
        if row:
            return Category(
                id=row[0], name=row[1], description=row[2], parent_id=row[3],
                path=row[4], level=row[5], created_at=row[6]
            )
        return None
    
    def get_descendants(self, category_id: int, include_self: bool = False) -> List[Category]:
        """Get all descendants of a category."""
        cursor = self.connection.cursor()
        
        cursor.execute(
            "SELECT path FROM categories WHERE id=?",
            (category_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            return []
        
        path = row[0]
        
        if include_self:
            cursor.execute(
                """SELECT id, name, description, parent_id, path, level, created_at 
                   FROM categories WHERE path LIKE ? ORDER BY path""",
                (f"{path}%",)
            )
        else:
            cursor.execute(
                """SELECT id, name, description, parent_id, path, level, created_at 
                   FROM categories WHERE path LIKE ? AND id != ? ORDER BY path""",
                (f"{path}%", category_id)
            )
        
        return [
            Category(id=r[0], name=r[1], description=r[2], parent_id=r[3],
                    path=r[4], level=r[5], created_at=r[6])
            for r in cursor.fetchall()
        ]
    
    def get_path(self, category_id: int) -> List[Category]:
        """Get path from root to category."""
        cursor = self.connection.cursor()
        
        # Get the category's path
        cursor.execute("SELECT path FROM categories WHERE id=?", (category_id,))
        row = cursor.fetchone()
        
        if not row or not row[0]:
            return []
        
        # Parse path to get category IDs
        path_str = row[0]
        ids = [int(x) for x in path_str.strip("/").split("/") if x]
        
        if not ids:
            return []
        
        # Fetch categories in path order
        categories = []
        for cid in ids:
            cat = self.get_by_id(cid)
            if cat:
                categories.append(cat)
        
        return categories
    
    def update(self, category_id: int, parent_id: Optional[int] = None, name: Optional[str] = None, description: Optional[str] = None) -> Category:
        """Update category, validating no cycles."""
        cursor = self.connection.cursor()
        
        # Check for circular reference
        if parent_id is not None and self._is_descendant(parent_id, category_id):
            raise CircularReferenceError("Cannot set parent to a descendant (would create cycle)")
        
        updates = []
        params = []
        
        if name is not None:
            updates.append("name=?")
            params.append(name)
        
        if description is not None:
            updates.append("description=?")
            params.append(description)
        
        if parent_id is not None:
            updates.append("parent_id=?")
            params.append(parent_id)
        
        if updates:
            params.append(category_id)
            cursor.execute(
                f"UPDATE categories SET {', '.join(updates)} WHERE id=?",
                params
            )
            self.connection.commit()
        
        # Update path and level if parent changed
        if parent_id is not None:
            self._update_path_and_level(category_id, parent_id)
            
            # Update all descendants' paths
            descendants = self.get_descendants(category_id)
            for desc in descendants:
                self._update_path_and_level(desc.id, desc.parent_id)
        
        return self.get_by_id(category_id)
    
    def delete(self, category_id: int, reassign_to: Optional[int] = None) -> bool:
        """Delete category, optionally reassigning ideas."""
        cursor = self.connection.cursor()
        
        if reassign_to is not None:
            cursor.execute(
                "UPDATE ideas SET category_id=? WHERE category_id=?",
                (reassign_to, category_id)
            )
        
        cursor.execute("DELETE FROM categories WHERE id=?", (category_id,))
        self.connection.commit()
        
        return cursor.rowcount > 0


class ContentItemRepository:
    """Repository for ContentItem entity operations."""
    
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
    
    def create(self, idea_id: int, content_type: str, content_text: Optional[str] = None,
               source_path: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> ContentItem:
        """Create content item linked to idea."""
        cursor = self.connection.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute(
            """INSERT INTO content_items (idea_id, content_type, content_text, source_path, metadata)
               VALUES (?, ?, ?, ?, ?)""",
            (idea_id, content_type, content_text, source_path, metadata_json)
        )
        self.connection.commit()
        
        return ContentItem(
            id=cursor.lastrowid,
            idea_id=idea_id,
            content_type=content_type,
            content_text=content_text,
            source_path=source_path,
            metadata=metadata,
            created_at=datetime.now().isoformat()
        )
    
    def create_batch(self, items: List[Dict[str, Any]]) -> List[ContentItem]:
        """Batch create content items in transaction."""
        cursor = self.connection.cursor()
        created = []
        
        try:
            for item_data in items:
                metadata_json = json.dumps(item_data.get('metadata')) if item_data.get('metadata') else None
                
                cursor.execute(
                    """INSERT INTO content_items (idea_id, content_type, content_text, source_path, metadata)
                       VALUES (?, ?, ?, ?, ?)""",
                    (item_data['idea_id'], item_data['content_type'],
                     item_data.get('content_text'), item_data.get('source_path'), metadata_json)
                )
                
                created.append(ContentItem(
                    id=cursor.lastrowid,
                    idea_id=item_data['idea_id'],
                    content_type=item_data['content_type'],
                    content_text=item_data.get('content_text'),
                    source_path=item_data.get('source_path'),
                    metadata=item_data.get('metadata'),
                    created_at=datetime.now().isoformat()
                ))
            
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
        
        return created
    
    def get_by_idea(self, idea_id: int) -> List[ContentItem]:
        """Get all content items for an idea."""
        cursor = self.connection.cursor()
        cursor.execute(
            """SELECT id, idea_id, content_type, content_text, source_path, metadata, created_at
               FROM content_items WHERE idea_id=?""",
            (idea_id,)
        )
        
        items = []
        for row in cursor.fetchall():
            metadata = json.loads(row[5]) if row[5] else None
            items.append(ContentItem(
                id=row[0], idea_id=row[1], content_type=row[2], content_text=row[3],
                source_path=row[4], metadata=metadata, created_at=row[6]
            ))
        
        return items
    
    def update(self, item_id: int, data: Dict[str, Any]) -> ContentItem:
        """Update content item."""
        cursor = self.connection.cursor()
        
        updates = []
        params = []
        
        if 'content_text' in data:
            updates.append("content_text=?")
            params.append(data['content_text'])
        
        if 'source_path' in data:
            updates.append("source_path=?")
            params.append(data['source_path'])
        
        if 'metadata' in data:
            updates.append("metadata=?")
            params.append(json.dumps(data['metadata']))
        
        if updates:
            params.append(item_id)
            cursor.execute(
                f"UPDATE content_items SET {', '.join(updates)} WHERE id=?",
                params
            )
            self.connection.commit()
        
        # Return updated item
        cursor.execute(
            """SELECT id, idea_id, content_type, content_text, source_path, metadata, created_at
               FROM content_items WHERE id=?""",
            (item_id,)
        )
        row = cursor.fetchone()
        
        if row:
            metadata = json.loads(row[5]) if row[5] else None
            return ContentItem(
                id=row[0], idea_id=row[1], content_type=row[2], content_text=row[3],
                source_path=row[4], metadata=metadata, created_at=row[6]
            )
        return None
    
    def delete(self, item_id: int) -> bool:
        """Delete content item."""
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM content_items WHERE id=?", (item_id,))
        self.connection.commit()
        return cursor.rowcount > 0


class IdeaRepository:
    """Repository for Idea entity operations."""
    
    def __init__(self, connection: sqlite3.Connection, tag_repo: TagRepository, content_repo: ContentItemRepository):
        self.connection = connection
        self.tag_repo = tag_repo
        self.content_repo = content_repo
    
    def _load_tags_for_idea(self, idea_id: int) -> List[Tag]:
        """Load tags associated with an idea."""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT t.id, t.name, t.display_name, t.color, t.created_at
            FROM tags t
            JOIN idea_tags it ON t.id = it.tag_id
            WHERE it.idea_id = ?
        """, (idea_id,))
        
        return [Tag(id=r[0], name=r[1], display_name=r[2], color=r[3], created_at=r[4]) for r in cursor.fetchall()]
    
    def _row_to_idea(self, row: tuple, include_tags: bool = True, include_content: bool = False) -> Idea:
        """Convert database row to Idea object."""
        idea = Idea(
            id=row[0], title=row[1], content=row[2], source=row[3],
            category_id=row[4], status=row[5], priority=row[6],
            created_at=row[7], updated_at=row[8]
        )
        
        if include_tags:
            idea.tags = self._load_tags_for_idea(idea.id)
        
        if include_content:
            idea.content_items = self.content_repo.get_by_idea(idea.id)
        
        return idea
    
    def create(self, title: str, content: Optional[str] = None, source: Optional[str] = None,
               category_id: Optional[int] = None, tags: Optional[List[str]] = None,
               priority: int = 0) -> Idea:
        """Create new idea with optional tags and category."""
        cursor = self.connection.cursor()
        
        try:
            # Insert idea
            cursor.execute(
                """INSERT INTO ideas (title, content, source, category_id, priority)
                   VALUES (?, ?, ?, ?, ?)""",
                (title, content, source, category_id, priority)
            )
            idea_id = cursor.lastrowid
            
            # Handle tags
            if tags:
                tag_objects = self.tag_repo.get_or_create(tags)
                for tag in tag_objects:
                    cursor.execute(
                        "INSERT INTO idea_tags (idea_id, tag_id) VALUES (?, ?)",
                        (idea_id, tag.id)
                    )
            
            self.connection.commit()
            
            return self.get_by_id(idea_id)
        except Exception:
            self.connection.rollback()
            raise
    
    def get_by_id(self, idea_id: int, include_content: bool = False) -> Optional[Idea]:
        """Retrieve idea by ID, optionally with content items."""
        cursor = self.connection.cursor()
        cursor.execute(
            """SELECT id, title, content, source, category_id, status, priority, created_at, updated_at
               FROM ideas WHERE id=?""",
            (idea_id,)
        )
        row = cursor.fetchone()
        
        if row:
            return self._row_to_idea(row, include_tags=True, include_content=include_content)
        return None
    
    def update(self, idea_id: int, title: Optional[str] = None, content: Optional[str] = None,
               category_id: Optional[int] = None, tags: Optional[List[str]] = None,
               priority: Optional[int] = None) -> Idea:
        """Update idea fields, preserving immutable data."""
        cursor = self.connection.cursor()
        
        updates = []
        params = []
        
        if title is not None:
            updates.append("title=?")
            params.append(title)
        
        if content is not None:
            updates.append("content=?")
            params.append(content)
        
        if category_id is not None:
            updates.append("category_id=?")
            params.append(category_id)
        
        if priority is not None:
            updates.append("priority=?")
            params.append(priority)
        
        # Always update updated_at
        updates.append("updated_at=CURRENT_TIMESTAMP")
        
        if updates:
            params.append(idea_id)
            cursor.execute(
                f"UPDATE ideas SET {', '.join(updates)} WHERE id=?",
                params
            )
        
        # Update tags if provided
        if tags is not None:
            # Remove existing tags
            cursor.execute("DELETE FROM idea_tags WHERE idea_id=?", (idea_id,))
            
            # Add new tags
            tag_objects = self.tag_repo.get_or_create(tags)
            for tag in tag_objects:
                cursor.execute(
                    "INSERT INTO idea_tags (idea_id, tag_id) VALUES (?, ?)",
                    (idea_id, tag.id)
                )
        
        self.connection.commit()
        
        return self.get_by_id(idea_id)
    
    def delete(self, idea_id: int, soft: bool = True) -> bool:
        """Delete idea (soft or hard delete)."""
        cursor = self.connection.cursor()
        
        if soft:
            cursor.execute(
                "UPDATE ideas SET status='archived', updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (idea_id,)
            )
        else:
            cursor.execute("DELETE FROM ideas WHERE id=?", (idea_id,))
        
        self.connection.commit()
        
        return cursor.rowcount > 0
    
    def list(self, limit: int = 10, offset: int = 0, status: Optional[str] = None) -> List[Idea]:
        """List ideas with pagination."""
        cursor = self.connection.cursor()
        
        if status:
            cursor.execute(
                """SELECT id, title, content, source, category_id, status, priority, created_at, updated_at
                   FROM ideas WHERE status=? ORDER BY created_at DESC LIMIT ? OFFSET ?""",
                (status, limit, offset)
            )
        else:
            cursor.execute(
                """SELECT id, title, content, source, category_id, status, priority, created_at, updated_at
                   FROM ideas ORDER BY created_at DESC LIMIT ? OFFSET ?""",
                (limit, offset)
            )
        
        return [self._row_to_idea(row) for row in cursor.fetchall()]
    
    def search(self, query: str, tags: Optional[List[str]] = None) -> List[Idea]:
        """Full-text search across ideas and content."""
        cursor = self.connection.cursor()
        
        # First, try FTS5 search on content_items via content_fts
        fts_idea_ids = set()
        try:
            # Use FTS5 MATCH in a separate query to get matching content item IDs
            cursor.execute("SELECT rowid FROM content_fts WHERE content_text MATCH ?", (query,))
            content_ids = [row[0] for row in cursor.fetchall()]
            
            if content_ids:
                placeholders = ','.join('?' * len(content_ids))
                cursor.execute(f"SELECT idea_id FROM content_items WHERE id IN ({placeholders})", content_ids)
                fts_idea_ids = {row[0] for row in cursor.fetchall()}
        except sqlite3.OperationalError:
            # FTS5 MATCH failed, will fall back to LIKE search
            pass
        
        # Search in ideas table using LIKE for title and content
        cursor.execute("""
            SELECT id, title, content, source, category_id, status, priority, created_at, updated_at
            FROM ideas
            WHERE (
                title LIKE ? OR 
                content LIKE ?
            )
            AND status = 'active'
        """, (f"%{query}%", f"%{query}%"))
        
        like_idea_ids = {row[0] for row in cursor.fetchall()}
        
        # Combine results
        all_idea_ids = fts_idea_ids | like_idea_ids
        
        if not all_idea_ids:
            return []
        
        # Fetch full idea data
        placeholders = ','.join('?' * len(all_idea_ids))
        cursor.execute(f"""
            SELECT id, title, content, source, category_id, status, priority, created_at, updated_at
            FROM ideas
            WHERE id IN ({placeholders}) AND status = 'active'
        """, tuple(all_idea_ids))
        
        ideas = [self._row_to_idea(row) for row in cursor.fetchall()]
        
        # Filter by tags if specified
        if tags:
            normalized_tags = {t.lower() for t in tags}
            ideas = [
                idea for idea in ideas
                if normalized_tags.intersection({t.name for t in idea.tags})
            ]
        
        return ideas
    
    def get_by_tags(self, tags: List[str], match_all: bool = False) -> List[Idea]:
        """Get ideas by tags (AND or OR logic)."""
        cursor = self.connection.cursor()
        
        normalized_tags = [t.lower() for t in tags]
        
        if match_all:
            # AND logic - ideas must have ALL specified tags
            placeholders = ','.join('?' * len(normalized_tags))
            cursor.execute(f"""
                SELECT i.id, i.title, i.content, i.source, i.category_id, i.status, i.priority, i.created_at, i.updated_at
                FROM ideas i
                JOIN idea_tags it ON i.id = it.idea_id
                JOIN tags t ON it.tag_id = t.id
                WHERE t.name IN ({placeholders}) AND i.status = 'active'
                GROUP BY i.id
                HAVING COUNT(DISTINCT t.name) = ?
            """, (*normalized_tags, len(normalized_tags)))
        else:
            # OR logic - ideas with ANY of the specified tags
            placeholders = ','.join('?' * len(normalized_tags))
            cursor.execute(f"""
                SELECT DISTINCT i.id, i.title, i.content, i.source, i.category_id, i.status, i.priority, i.created_at, i.updated_at
                FROM ideas i
                JOIN idea_tags it ON i.id = it.idea_id
                JOIN tags t ON it.tag_id = t.id
                WHERE t.name IN ({placeholders}) AND i.status = 'active'
            """, normalized_tags)
        
        return [self._row_to_idea(row) for row in cursor.fetchall()]


# ============================================================================
# Database Manager
# ============================================================================

class DatabaseManager:
    """Main entry point for all database operations."""
    
    def __init__(self, db_path: str, init_schema: bool = True):
        """Initialize database connection and optionally create schema."""
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        
        # Enable foreign keys
        self.connection.execute("PRAGMA foreign_keys = ON")
        
        # Initialize repositories
        self.tag_repository = TagRepository(self.connection)
        self.category_repository = CategoryRepository(self.connection)
        self.content_repository = ContentItemRepository(self.connection)
        self.idea_repository = IdeaRepository(
            self.connection, self.tag_repository, self.content_repository
        )
        
        if init_schema:
            self._init_schema()
    
    def _init_schema(self) -> None:
        """Initialize database schema."""
        self.connection.executescript(SCHEMA_SQL)
        self.connection.commit()
    
    def close(self) -> None:
        """Close database connection and cleanup resources."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_migration(self, target_version: int) -> bool:
        """Apply migration scripts to reach target schema version."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT MAX(version) FROM schema_version")
        row = cursor.fetchone()
        current_version = row[0] if row and row[0] else 0
        
        if current_version >= target_version:
            return True
        
        # Apply migrations (placeholder for future migrations)
        for version in range(current_version + 1, target_version + 1):
            cursor.execute(
                "INSERT INTO schema_version (version) VALUES (?)",
                (version,)
            )
        
        self.connection.commit()
        return True


if __name__ == "__main__":
    # Simple test
    db = DatabaseManager(":memory:")
    print("Database initialized successfully!")
    db.close()
