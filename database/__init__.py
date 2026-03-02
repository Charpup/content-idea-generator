"""
Content Idea Generator - Database Module

SQLite database with FTS5 full-text search support.
"""

from .database import (
    ContentIdeaDatabase,
    DatabaseError,
    init_database,
    get_db
)

__all__ = [
    'ContentIdeaDatabase',
    'DatabaseError',
    'init_database',
    'get_db'
]
