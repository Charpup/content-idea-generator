"""
Content Idea Generator - Database Module
SQLite database with FTS5 full-text search support
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager


class DatabaseError(Exception):
    """Base exception for database operations"""
    pass


class ContentIdeaDatabase:
    """
    SQLite database manager for Content Idea Generator
    Supports FTS5 full-text search and Obsidian export
    """
    
    def __init__(self, db_path: str = "content_ideas.db"):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._ensure_directory()
        self._init_database()
    
    def _ensure_directory(self):
        """Ensure database directory exists"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _init_database(self):
        """Initialize database with schema"""
        schema_path = Path(__file__).parent / "schema.sql"
        if schema_path.exists():
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = f.read()
            with self._get_connection() as conn:
                conn.executescript(schema)
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise DatabaseError(f"Database operation failed: {e}") from e
        finally:
            conn.close()
    
    # ==================== CATEGORIES CRUD ====================
    
    def create_category(self, name: str, description: Optional[str] = None, 
                       parent_id: Optional[int] = None) -> int:
        """
        Create a new category
        
        Args:
            name: Category name (unique)
            description: Optional description
            parent_id: Parent category ID for hierarchical structure
            
        Returns:
            ID of created category
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO categories (name, description, parent_id) 
                   VALUES (?, ?, ?)""",
                (name, description, parent_id)
            )
            return cursor.lastrowid
    
    def get_category(self, category_id: int) -> Optional[Dict[str, Any]]:
        """Get category by ID"""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM categories WHERE id = ?",
                (category_id,)
            ).fetchone()
            return dict(row) if row else None
    
    def get_category_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get category by name"""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM categories WHERE name = ?",
                (name,)
            ).fetchone()
            return dict(row) if row else None
    
    def update_category(self, category_id: int, **kwargs) -> bool:
        """
        Update category fields
        
        Args:
            category_id: Category ID to update
            **kwargs: Fields to update (name, description, parent_id)
        """
        allowed_fields = {'name', 'description', 'parent_id'}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [category_id]
        
        with self._get_connection() as conn:
            cursor = conn.execute(
                f"UPDATE categories SET {set_clause} WHERE id = ?",
                values
            )
            return cursor.rowcount > 0
    
    def delete_category(self, category_id: int) -> bool:
        """Delete category by ID"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM categories WHERE id = ?",
                (category_id,)
            )
            return cursor.rowcount > 0
    
    def list_categories(self, parent_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """List all categories, optionally filtered by parent"""
        with self._get_connection() as conn:
            if parent_id is not None:
                rows = conn.execute(
                    "SELECT * FROM categories WHERE parent_id = ? ORDER BY name",
                    (parent_id,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM categories ORDER BY name"
                ).fetchall()
            return [dict(row) for row in rows]
    
    def get_category_tree(self) -> List[Dict[str, Any]]:
        """Get hierarchical category tree"""
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM v_category_tree").fetchall()
            return [dict(row) for row in rows]
    
    # ==================== TAGS CRUD ====================
    
    def create_tag(self, name: str, color: str = '#6366f1',
                   description: Optional[str] = None) -> int:
        """
        Create a new tag
        
        Args:
            name: Tag name (unique)
            color: Hex color code (default: indigo)
            description: Optional description
            
        Returns:
            ID of created tag
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO tags (name, color, description) 
                   VALUES (?, ?, ?)""",
                (name, color, description)
            )
            return cursor.lastrowid
    
    def get_tag(self, tag_id: int) -> Optional[Dict[str, Any]]:
        """Get tag by ID"""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM tags WHERE id = ?",
                (tag_id,)
            ).fetchone()
            return dict(row) if row else None
    
    def get_tag_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get tag by name"""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM tags WHERE name = ?",
                (name,)
            ).fetchone()
            return dict(row) if row else None
    
    def update_tag(self, tag_id: int, **kwargs) -> bool:
        """Update tag fields"""
        allowed_fields = {'name', 'color', 'description'}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [tag_id]
        
        with self._get_connection() as conn:
            cursor = conn.execute(
                f"UPDATE tags SET {set_clause} WHERE id = ?",
                values
            )
            return cursor.rowcount > 0
    
    def delete_tag(self, tag_id: int) -> bool:
        """Delete tag by ID"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM tags WHERE id = ?",
                (tag_id,)
            )
            return cursor.rowcount > 0
    
    def list_tags(self) -> List[Dict[str, Any]]:
        """List all tags"""
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM tags ORDER BY name").fetchall()
            return [dict(row) for row in rows]
    
    # ==================== CONTENT ITEMS CRUD ====================
    
    def create_content_item(self, type: str, title: str, content: Optional[str] = None,
                           source: Optional[str] = None, author: Optional[str] = None,
                           category_id: Optional[int] = None, status: str = 'active',
                           priority: int = 3, tag_ids: Optional[List[int]] = None) -> int:
        """
        Create a new content item
        
        Args:
            type: Content type ('article', 'book', 'video', 'podcast', 'tweet', 'note', 'idea')
            title: Content title
            content: Full content text
            source: Original source (URL, book title, etc.)
            author: Content author
            category_id: Category ID
            status: 'active', 'archived', or 'draft'
            priority: 1-5 rating
            tag_ids: List of tag IDs to associate
            
        Returns:
            ID of created content item
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO content_items 
                   (type, title, content, source, author, category_id, status, priority)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (type, title, content, source, author, category_id, status, priority)
            )
            content_id = cursor.lastrowid
            
            # Associate tags
            if tag_ids:
                for tag_id in tag_ids:
                    conn.execute(
                        "INSERT OR IGNORE INTO content_tags (content_id, tag_id) VALUES (?, ?)",
                        (content_id, tag_id)
                    )
            
            return content_id
    
    def get_content_item(self, content_id: int) -> Optional[Dict[str, Any]]:
        """Get content item by ID with full details"""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM v_content_full WHERE id = ?",
                (content_id,)
            ).fetchone()
            return dict(row) if row else None
    
    def update_content_item(self, content_id: int, **kwargs) -> bool:
        """Update content item fields"""
        allowed_fields = {'type', 'title', 'content', 'source', 'author',
                         'category_id', 'status', 'priority'}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [content_id]
        
        with self._get_connection() as conn:
            cursor = conn.execute(
                f"UPDATE content_items SET {set_clause} WHERE id = ?",
                values
            )
            return cursor.rowcount > 0
    
    def delete_content_item(self, content_id: int) -> bool:
        """Delete content item by ID (cascades to related records)"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM content_items WHERE id = ?",
                (content_id,)
            )
            return cursor.rowcount > 0
    
    def list_content_items(self, type: Optional[str] = None,
                          category_id: Optional[int] = None,
                          status: Optional[str] = None,
                          limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List content items with optional filters"""
        with self._get_connection() as conn:
            query = "SELECT * FROM v_content_full WHERE 1=1"
            params = []
            
            if type:
                query += " AND type = ?"
                params.append(type)
            if category_id:
                query += " AND category_id = ?"
                params.append(category_id)
            if status:
                query += " AND status = ?"
                params.append(status)
            
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]
    
    def add_tags_to_content(self, content_id: int, tag_ids: List[int]):
        """Add tags to content item"""
        with self._get_connection() as conn:
            for tag_id in tag_ids:
                conn.execute(
                    "INSERT OR IGNORE INTO content_tags (content_id, tag_id) VALUES (?, ?)",
                    (content_id, tag_id)
                )
    
    def remove_tags_from_content(self, content_id: int, tag_ids: List[int]):
        """Remove tags from content item"""
        with self._get_connection() as conn:
            for tag_id in tag_ids:
                conn.execute(
                    "DELETE FROM content_tags WHERE content_id = ? AND tag_id = ?",
                    (content_id, tag_id)
                )
    
    # ==================== FULL-TEXT SEARCH ====================
    
    def search_content(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search content using FTS5 full-text search
        
        Args:
            query: Search query (supports FTS5 syntax: AND, OR, NOT, *)
            limit: Maximum results to return
            
        Returns:
            List of matching content items with rank
        """
        with self._get_connection() as conn:
            rows = conn.execute(
                """SELECT 
                    ci.*,
                    rank,
                    snippet(content_fts, 0, '<mark>', '</mark>', '...', 32) as title_snippet,
                    snippet(content_fts, 1, '<mark>', '</mark>', '...', 32) as content_snippet
                   FROM content_fts
                   JOIN content_items ci ON content_fts.rowid = ci.id
                   WHERE content_fts MATCH ?
                   ORDER BY rank
                   LIMIT ?""",
                (query, limit)
            ).fetchall()
            return [dict(row) for row in rows]
    
    def search_with_snippet(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search with highlighted snippets
        
        Returns content with highlighted matching terms
        """
        with self._get_connection() as conn:
            rows = conn.execute(
                """SELECT 
                    ci.id,
                    ci.type,
                    ci.title,
                    ci.source,
                    ci.author,
                    ci.status,
                    ci.priority,
                    rank,
                    snippet(content_fts, 0, '<mark>', '</mark>', '...', 32) as title_highlight,
                    snippet(content_fts, 1, '<mark>', '</mark>', '...', 64) as content_preview
                   FROM content_fts
                   JOIN content_items ci ON content_fts.rowid = ci.id
                   WHERE content_fts MATCH ?
                   ORDER BY rank
                   LIMIT ?""",
                (query, limit)
            ).fetchall()
            return [dict(row) for row in rows]
    
    # ==================== TEXT SNIPPETS CRUD ====================
    
    def create_text_snippet(self, content_id: int, snippet_text: str,
                           context: Optional[str] = None,
                           source_ref: Optional[str] = None,
                           page_ref: Optional[str] = None,
                           position: Optional[int] = None,
                           notes: Optional[str] = None,
                           tag_ids: Optional[List[int]] = None) -> int:
        """Create a text snippet"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO text_snippets 
                   (content_id, snippet_text, context, source_ref, page_ref, position, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (content_id, snippet_text, context, source_ref, page_ref, position, notes)
            )
            snippet_id = cursor.lastrowid
            
            if tag_ids:
                for tag_id in tag_ids:
                    conn.execute(
                        "INSERT OR IGNORE INTO snippet_tags (snippet_id, tag_id) VALUES (?, ?)",
                        (snippet_id, tag_id)
                    )
            
            return snippet_id
    
    def get_text_snippet(self, snippet_id: int) -> Optional[Dict[str, Any]]:
        """Get text snippet by ID"""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM text_snippets WHERE id = ?",
                (snippet_id,)
            ).fetchone()
            return dict(row) if row else None
    
    def list_text_snippets(self, content_id: int) -> List[Dict[str, Any]]:
        """List all snippets for a content item"""
        with self._get_connection() as conn:
            rows = conn.execute(
                """SELECT * FROM text_snippets 
                   WHERE content_id = ? 
                   ORDER BY position, created_at""",
                (content_id,)
            ).fetchall()
            return [dict(row) for row in rows]
    
    def update_text_snippet(self, snippet_id: int, **kwargs) -> bool:
        """Update text snippet fields"""
        allowed_fields = {'snippet_text', 'context', 'source_ref', 
                         'page_ref', 'position', 'notes'}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [snippet_id]
        
        with self._get_connection() as conn:
            cursor = conn.execute(
                f"UPDATE text_snippets SET {set_clause} WHERE id = ?",
                values
            )
            return cursor.rowcount > 0
    
    def delete_text_snippet(self, snippet_id: int) -> bool:
        """Delete text snippet"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM text_snippets WHERE id = ?",
                (snippet_id,)
            )
            return cursor.rowcount > 0
    
    # ==================== GOLD SENTENCES CRUD ====================
    
    def create_gold_sentence(self, content_id: int, sentence: str,
                            context: Optional[str] = None,
                            rating: int = 3) -> int:
        """Create a gold sentence"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO gold_sentences (content_id, sentence, context, rating)
                   VALUES (?, ?, ?, ?)""",
                (content_id, sentence, context, rating)
            )
            return cursor.lastrowid
    
    def get_gold_sentence(self, sentence_id: int) -> Optional[Dict[str, Any]]:
        """Get gold sentence by ID"""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM gold_sentences WHERE id = ?",
                (sentence_id,)
            ).fetchone()
            return dict(row) if row else None
    
    def list_gold_sentences(self, content_id: Optional[int] = None,
                           min_rating: Optional[int] = None) -> List[Dict[str, Any]]:
        """List gold sentences with optional filters"""
        with self._get_connection() as conn:
            query = "SELECT * FROM gold_sentences WHERE 1=1"
            params = []
            
            if content_id:
                query += " AND content_id = ?"
                params.append(content_id)
            if min_rating:
                query += " AND rating >= ?"
                params.append(min_rating)
            
            query += " ORDER BY rating DESC, usage_count ASC"
            
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]
    
    def update_gold_sentence(self, sentence_id: int, **kwargs) -> bool:
        """Update gold sentence fields"""
        allowed_fields = {'sentence', 'context', 'rating', 'usage_count'}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [sentence_id]
        
        with self._get_connection() as conn:
            cursor = conn.execute(
                f"UPDATE gold_sentences SET {set_clause} WHERE id = ?",
                values
            )
            return cursor.rowcount > 0
    
    def increment_gold_sentence_usage(self, sentence_id: int) -> bool:
        """Increment usage count for a gold sentence"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """UPDATE gold_sentences 
                   SET usage_count = usage_count + 1, last_used_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (sentence_id,)
            )
            return cursor.rowcount > 0
    
    def delete_gold_sentence(self, sentence_id: int) -> bool:
        """Delete gold sentence"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM gold_sentences WHERE id = ?",
                (sentence_id,)
            )
            return cursor.rowcount > 0
    
    # ==================== IDEAS CRUD ====================
    
    def create_idea(self, content_id: int, concept: str,
                   elaboration: Optional[str] = None,
                   use_cases: Optional[List[str]] = None,
                   tags: Optional[List[str]] = None,
                   priority: int = 3, status: str = 'new') -> int:
        """
        Create a new idea
        
        Args:
            content_id: Source content item ID
            concept: Core idea/concept
            elaboration: Detailed explanation
            use_cases: List of use case strings
            tags: List of internal tag strings
            priority: 1-5 priority rating
            status: 'new', 'developing', 'ready', 'used', 'archived'
        """
        use_cases_json = json.dumps(use_cases) if use_cases else None
        tags_json = json.dumps(tags) if tags else None
        
        with self._get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO ideas 
                   (content_id, concept, elaboration, use_cases, tags, priority, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (content_id, concept, elaboration, use_cases_json, tags_json, priority, status)
            )
            return cursor.lastrowid
    
    def get_idea(self, idea_id: int) -> Optional[Dict[str, Any]]:
        """Get idea by ID"""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM ideas WHERE id = ?",
                (idea_id,)
            ).fetchone()
            if row:
                result = dict(row)
                result['use_cases'] = json.loads(result['use_cases']) if result['use_cases'] else []
                result['tags'] = json.loads(result['tags']) if result['tags'] else []
                return result
            return None
    
    def list_ideas(self, content_id: Optional[int] = None,
                  status: Optional[str] = None,
                  min_priority: Optional[int] = None) -> List[Dict[str, Any]]:
        """List ideas with optional filters"""
        with self._get_connection() as conn:
            query = "SELECT * FROM ideas WHERE 1=1"
            params = []
            
            if content_id:
                query += " AND content_id = ?"
                params.append(content_id)
            if status:
                query += " AND status = ?"
                params.append(status)
            if min_priority:
                query += " AND priority >= ?"
                params.append(min_priority)
            
            query += " ORDER BY priority DESC, created_at DESC"
            
            rows = conn.execute(query, params).fetchall()
            results = []
            for row in rows:
                result = dict(row)
                result['use_cases'] = json.loads(result['use_cases']) if result['use_cases'] else []
                result['tags'] = json.loads(result['tags']) if result['tags'] else []
                results.append(result)
            return results
    
    def update_idea(self, idea_id: int, **kwargs) -> bool:
        """Update idea fields"""
        allowed_fields = {'concept', 'elaboration', 'priority', 'status'}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if 'use_cases' in kwargs:
            updates['use_cases'] = json.dumps(kwargs['use_cases'])
        if 'tags' in kwargs:
            updates['tags'] = json.dumps(kwargs['tags'])
        
        if not updates:
            return False
        
        set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [idea_id]
        
        with self._get_connection() as conn:
            cursor = conn.execute(
                f"UPDATE ideas SET {set_clause} WHERE id = ?",
                values
            )
            return cursor.rowcount > 0
    
    def delete_idea(self, idea_id: int) -> bool:
        """Delete idea"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM ideas WHERE id = ?",
                (idea_id,)
            )
            return cursor.rowcount > 0
    
    # ==================== IDEA RELATIONS ====================
    
    def create_idea_relation(self, idea_id: int, related_idea_id: int,
                            relation_type: str = 'related',
                            strength: int = 3) -> bool:
        """
        Create a relation between two ideas
        
        Args:
            relation_type: 'related', 'inspired_by', 'builds_on', 'contradicts', 'similar'
            strength: 1-5 connection strength
        """
        with self._get_connection() as conn:
            try:
                conn.execute(
                    """INSERT INTO idea_relations (idea_id, related_idea_id, relation_type, strength)
                       VALUES (?, ?, ?, ?)""",
                    (idea_id, related_idea_id, relation_type, strength)
                )
                return True
            except sqlite3.IntegrityError:
                return False
    
    def get_related_ideas(self, idea_id: int) -> List[Dict[str, Any]]:
        """Get all ideas related to the given idea"""
        with self._get_connection() as conn:
            rows = conn.execute(
                """SELECT 
                    i.*,
                    ir.relation_type,
                    ir.strength,
                    ir.related_idea_id
                   FROM idea_relations ir
                   JOIN ideas i ON ir.related_idea_id = i.id
                   WHERE ir.idea_id = ?""",
                (idea_id,)
            ).fetchall()
            
            results = []
            for row in rows:
                result = dict(row)
                result['use_cases'] = json.loads(result['use_cases']) if result['use_cases'] else []
                result['tags'] = json.loads(result['tags']) if result['tags'] else []
                results.append(result)
            return results
    
    def delete_idea_relation(self, idea_id: int, related_idea_id: int) -> bool:
        """Delete relation between ideas"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """DELETE FROM idea_relations 
                   WHERE idea_id = ? AND related_idea_id = ?""",
                (idea_id, related_idea_id)
            )
            return cursor.rowcount > 0
    
    # ==================== OBSIDIAN EXPORT ====================
    
    def export_content_to_markdown(self, content_id: int) -> Optional[str]:
        """
        Export a content item to Markdown format for Obsidian
        
        Returns:
            Markdown string or None if content not found
        """
        with self._get_connection() as conn:
            row = conn.execute(
                """SELECT 
                    ci.*,
                    c.name as category_name,
                    GROUP_CONCAT(DISTINCT t.name) as tag_names
                   FROM content_items ci
                   LEFT JOIN categories c ON ci.category_id = c.id
                   LEFT JOIN content_tags ct ON ci.id = ct.content_id
                   LEFT JOIN tags t ON ct.tag_id = t.id
                   WHERE ci.id = ?
                   GROUP BY ci.id""",
                (content_id,)
            ).fetchone()
            
            if not row:
                return None
            
            # Build markdown
            md_lines = [
                f"# {row['title']}",
                "",
                f"**Type:** {row['type']}",
                f"**Source:** {row['source'] or 'N/A'}",
                f"**Author:** {row['author'] or 'N/A'}",
                f"**Category:** {row['category_name'] or 'Uncategorized'}",
            ]
            
            if row['tag_names']:
                tags = ' '.join(f"#{tag}" for tag in row['tag_names'].split(','))
                md_lines.append(f"**Tags:** {tags}")
            
            md_lines.extend([
                f"**Priority:** {row['priority']}/5",
                f"**Status:** {row['status']}",
                f"**Created:** {row['created_at']}",
                "",
                "---",
                "",
                row['content'] or ''
            ])
            
            # Add snippets
            snippets = conn.execute(
                "SELECT * FROM text_snippets WHERE content_id = ? ORDER BY position",
                (content_id,)
            ).fetchall()
            
            if snippets:
                md_lines.extend(["", "## Snippets", ""])
                for i, snip in enumerate(snippets, 1):
                    md_lines.extend([
                        f"### Snippet {i}",
                        f"> {snip['snippet_text']}",
                        ""
                    ])
                    if snip['context']:
                        md_lines.append(f"*Context: {snip['context']}*")
                    if snip['notes']:
                        md_lines.append(f"*Notes: {snip['notes']}*")
                    md_lines.append("")
            
            # Add gold sentences
            gold = conn.execute(
                "SELECT * FROM gold_sentences WHERE content_id = ? ORDER BY rating DESC",
                (content_id,)
            ).fetchall()
            
            if gold:
                md_lines.extend(["", "## Gold Sentences", ""])
                for g in gold:
                    md_lines.extend([
                        f"> {g['sentence']}",
                        f"*Rating: {g['rating']}/5 | Used: {g['usage_count']} times*",
                        ""
                    ])
            
            # Add ideas
            ideas = conn.execute(
                "SELECT * FROM ideas WHERE content_id = ? ORDER BY priority DESC",
                (content_id,)
            ).fetchall()
            
            if ideas:
                md_lines.extend(["", "## Ideas", ""])
                for idea in ideas:
                    md_lines.extend([
                        f"### {idea['concept']}",
                        f"**Status:** {idea['status']} | **Priority:** {idea['priority']}/5",
                        ""
                    ])
                    if idea['elaboration']:
                        md_lines.append(idea['elaboration'])
                        md_lines.append("")
            
            return '\n'.join(md_lines)
    
    def export_idea_to_markdown(self, idea_id: int) -> Optional[str]:
        """Export an idea as an atomic note for Obsidian"""
        idea = self.get_idea(idea_id)
        if not idea:
            return None
        
        content = self.get_content_item(idea['content_id'])
        
        md_lines = [
            f"# Idea: {idea['concept']}",
            "",
            f"**Status:** {idea['status']}",
            f"**Priority:** {idea['priority']}/5",
        ]
        
        if content:
            md_lines.append(f"**Source:** [[{content['title']}]]")
        
        md_lines.append("")
        
        if idea['tags']:
            tags = ' '.join(f"#{tag}" for tag in idea['tags'])
            md_lines.append(f"**Tags:** {tags}")
            md_lines.append("")
        
        if idea['elaboration']:
            md_lines.extend(["## Elaboration", "", idea['elaboration'], ""])
        
        if idea['use_cases']:
            md_lines.extend(["## Use Cases", ""])
            for use_case in idea['use_cases']:
                md_lines.append(f"- {use_case}")
            md_lines.append("")
        
        # Get related ideas
        related = self.get_related_ideas(idea_id)
        if related:
            md_lines.extend(["## Related Ideas", ""])
            for rel in related:
                md_lines.append(f"- [[{rel['concept']}]] ({rel['relation_type']}, strength: {rel['strength']})")
            md_lines.append("")
        
        md_lines.extend([
            "---",
            f"*Created: {idea['created_at']}*"
        ])
        
        return '\n'.join(md_lines)
    
    def export_all_content(self, output_dir: str) -> Dict[str, int]:
        """
        Export all content to Markdown files in the specified directory
        
        Returns:
            Dict with counts of exported items
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        counts = {'content': 0, 'ideas': 0}
        
        # Export content items
        content_items = self.list_content_items(limit=10000)
        for item in content_items:
            md = self.export_content_to_markdown(item['id'])
            if md:
                filename = f"{self._sanitize_filename(item['title'])}.md"
                (output_path / filename).write_text(md, encoding='utf-8')
                counts['content'] += 1
        
        # Export ideas as atomic notes
        ideas = self.list_ideas()
        ideas_dir = output_path / 'ideas'
        ideas_dir.mkdir(exist_ok=True)
        
        for idea in ideas:
            md = self.export_idea_to_markdown(idea['id'])
            if md:
                filename = f"{self._sanitize_filename(idea['concept'])}.md"
                (ideas_dir / filename).write_text(md, encoding='utf-8')
                counts['ideas'] += 1
        
        return counts
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize string for use as filename"""
        import re
        # Remove invalid characters
        name = re.sub(r'[\\/*?:"<>|]', '', name)
        # Limit length
        name = name[:100].strip()
        # Replace spaces with underscores
        name = name.replace(' ', '_')
        return name or 'untitled'
    
    # ==================== STATISTICS ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self._get_connection() as conn:
            stats = {}
            
            tables = ['categories', 'tags', 'content_items', 'text_snippets',
                     'gold_sentences', 'ideas', 'idea_relations']
            
            for table in tables:
                row = conn.execute(
                    f"SELECT COUNT(*) as count FROM {table}"
                ).fetchone()
                stats[table] = row['count']
            
            # Content by type
            rows = conn.execute(
                "SELECT type, COUNT(*) as count FROM content_items GROUP BY type"
            ).fetchall()
            stats['content_by_type'] = {row['type']: row['count'] for row in rows}
            
            # Ideas by status
            rows = conn.execute(
                "SELECT status, COUNT(*) as count FROM ideas GROUP BY status"
            ).fetchall()
            stats['ideas_by_status'] = {row['status']: row['count'] for row in rows}
            
            return stats


# ==================== UTILITY FUNCTIONS ====================

def init_database(db_path: str = "content_ideas.db") -> ContentIdeaDatabase:
    """
    Initialize a new database instance
    
    Args:
        db_path: Path to database file
        
    Returns:
        ContentIdeaDatabase instance
    """
    return ContentIdeaDatabase(db_path)


def get_db(db_path: str = "content_ideas.db") -> ContentIdeaDatabase:
    """Get or create database instance (singleton pattern)"""
    if not hasattr(get_db, '_instance'):
        get_db._instance = ContentIdeaDatabase(db_path)
    return get_db._instance
