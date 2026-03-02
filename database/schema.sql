-- ============================================
-- Content Idea Generator Database Schema
-- SQLite with FTS5 Support
-- ============================================

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- ============================================
-- 1. CATEGORIES (Hierarchical)
-- ============================================
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    parent_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- Index for hierarchical queries
CREATE INDEX IF NOT EXISTS idx_categories_parent ON categories(parent_id);
CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name);

-- ============================================
-- 2. TAGS
-- ============================================
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    color TEXT DEFAULT '#6366f1',
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);

-- ============================================
-- 3. CONTENT ITEMS (Main Entity)
-- ============================================
CREATE TABLE IF NOT EXISTS content_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK (type IN ('article', 'book', 'video', 'podcast', 'tweet', 'note', 'idea')),
    title TEXT NOT NULL,
    content TEXT,
    source TEXT,
    author TEXT,
    category_id INTEGER,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'archived', 'draft')),
    priority INTEGER DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_content_type ON content_items(type);
CREATE INDEX IF NOT EXISTS idx_content_category ON content_items(category_id);
CREATE INDEX IF NOT EXISTS idx_content_status ON content_items(status);
CREATE INDEX IF NOT EXISTS idx_content_priority ON content_items(priority);
CREATE INDEX IF NOT EXISTS idx_content_created ON content_items(created_at);
CREATE INDEX IF NOT EXISTS idx_content_updated ON content_items(updated_at);
CREATE INDEX IF NOT EXISTS idx_content_category_status ON content_items(category_id, status);

-- ============================================
-- 4. CONTENT-TAGS (Many-to-Many Junction)
-- ============================================
CREATE TABLE IF NOT EXISTS content_tags (
    content_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (content_id, tag_id),
    FOREIGN KEY (content_id) REFERENCES content_items(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_content_tags_tag ON content_tags(tag_id);

-- ============================================
-- 5. TEXT SNIPPETS
-- ============================================
CREATE TABLE IF NOT EXISTS text_snippets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER NOT NULL,
    snippet_text TEXT NOT NULL,
    context TEXT,
    source_ref TEXT,
    page_ref TEXT,
    position INTEGER,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (content_id) REFERENCES content_items(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_snippets_content ON text_snippets(content_id);
CREATE INDEX IF NOT EXISTS idx_snippets_position ON text_snippets(content_id, position);

-- ============================================
-- 6. SNIPPET-TAGS (Many-to-Many for Snippets)
-- ============================================
CREATE TABLE IF NOT EXISTS snippet_tags (
    snippet_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (snippet_id, tag_id),
    FOREIGN KEY (snippet_id) REFERENCES text_snippets(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_snippet_tags_tag ON snippet_tags(tag_id);

-- ============================================
-- 7. GOLD SENTENCES
-- ============================================
CREATE TABLE IF NOT EXISTS gold_sentences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER NOT NULL,
    sentence TEXT NOT NULL,
    context TEXT,
    rating INTEGER DEFAULT 3 CHECK (rating BETWEEN 1 AND 5),
    usage_count INTEGER DEFAULT 0,
    last_used_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (content_id) REFERENCES content_items(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_gold_content ON gold_sentences(content_id);
CREATE INDEX IF NOT EXISTS idx_gold_rating ON gold_sentences(rating);
CREATE INDEX IF NOT EXISTS idx_gold_usage ON gold_sentences(usage_count);

-- ============================================
-- 8. IDEAS
-- ============================================
CREATE TABLE IF NOT EXISTS ideas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER NOT NULL,
    concept TEXT NOT NULL,
    elaboration TEXT,
    use_cases TEXT,
    tags TEXT,
    priority INTEGER DEFAULT 3 CHECK (priority BETWEEN 1 AND 5),
    status TEXT DEFAULT 'new' CHECK (status IN ('new', 'developing', 'ready', 'used', 'archived')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (content_id) REFERENCES content_items(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_ideas_content ON ideas(content_id);
CREATE INDEX IF NOT EXISTS idx_ideas_status ON ideas(status);
CREATE INDEX IF NOT EXISTS idx_ideas_priority ON ideas(priority);
CREATE INDEX IF NOT EXISTS idx_ideas_created ON ideas(created_at);

-- ============================================
-- 9. IDEA RELATIONS (Ideas connected to Ideas)
-- ============================================
CREATE TABLE IF NOT EXISTS idea_relations (
    idea_id INTEGER NOT NULL,
    related_idea_id INTEGER NOT NULL,
    relation_type TEXT DEFAULT 'related' CHECK (relation_type IN ('related', 'inspired_by', 'builds_on', 'contradicts', 'similar')),
    strength INTEGER DEFAULT 3 CHECK (strength BETWEEN 1 AND 5),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (idea_id, related_idea_id),
    FOREIGN KEY (idea_id) REFERENCES ideas(id) ON DELETE CASCADE,
    FOREIGN KEY (related_idea_id) REFERENCES ideas(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_idea_relations_related ON idea_relations(related_idea_id);
CREATE INDEX IF NOT EXISTS idx_idea_relations_type ON idea_relations(relation_type);

-- ============================================
-- 10. FTS5 VIRTUAL TABLE (Full-Text Search)
-- ============================================
CREATE VIRTUAL TABLE IF NOT EXISTS content_fts USING fts5(
    title,
    content,
    content='content_items',
    content_rowid='id',
    tokenize='porter unicode61'
);

-- ============================================
-- TRIGGERS FOR FTS5 SYNCHRONIZATION
-- ============================================

-- Trigger: Insert into FTS when content_items is inserted
CREATE TRIGGER IF NOT EXISTS content_items_ai AFTER INSERT ON content_items BEGIN
    INSERT INTO content_fts(rowid, title, content)
    VALUES (new.id, new.title, new.content);
END;

-- Trigger: Update FTS when content_items is updated
CREATE TRIGGER IF NOT EXISTS content_items_au AFTER UPDATE ON content_items BEGIN
    INSERT INTO content_fts(content_fts, rowid, title, content)
    VALUES ('delete', old.id, old.title, old.content);
    INSERT INTO content_fts(rowid, title, content)
    VALUES (new.id, new.title, new.content);
END;

-- Trigger: Delete from FTS when content_items is deleted
CREATE TRIGGER IF NOT EXISTS content_items_ad AFTER DELETE ON content_items BEGIN
    INSERT INTO content_fts(content_fts, rowid, title, content)
    VALUES ('delete', old.id, old.title, old.content);
END;

-- ============================================
-- TRIGGERS FOR UPDATED_AT TIMESTAMP
-- ============================================

CREATE TRIGGER IF NOT EXISTS categories_updated_at AFTER UPDATE ON categories BEGIN
    UPDATE categories SET updated_at = CURRENT_TIMESTAMP WHERE id = new.id;
END;

CREATE TRIGGER IF NOT EXISTS content_items_updated_at AFTER UPDATE ON content_items BEGIN
    UPDATE content_items SET updated_at = CURRENT_TIMESTAMP WHERE id = new.id;
END;

CREATE TRIGGER IF NOT EXISTS ideas_updated_at AFTER UPDATE ON ideas BEGIN
    UPDATE ideas SET updated_at = CURRENT_TIMESTAMP WHERE id = new.id;
END;

-- ============================================
-- VIEWS FOR COMMON QUERIES
-- ============================================

-- View: Content with category and tag info
CREATE VIEW IF NOT EXISTS v_content_full AS
SELECT 
    ci.id,
    ci.type,
    ci.title,
    ci.content,
    ci.source,
    ci.author,
    ci.status,
    ci.priority,
    ci.created_at,
    ci.updated_at,
    c.name as category_name,
    c.parent_id as category_parent_id,
    GROUP_CONCAT(t.name, ', ') as tags
FROM content_items ci
LEFT JOIN categories c ON ci.category_id = c.id
LEFT JOIN content_tags ct ON ci.id = ct.content_id
LEFT JOIN tags t ON ct.tag_id = t.id
GROUP BY ci.id;

-- View: Hierarchical category tree
CREATE VIEW IF NOT EXISTS v_category_tree AS
WITH RECURSIVE category_tree AS (
    SELECT 
        id,
        name,
        parent_id,
        0 as level,
        name as path
    FROM categories
    WHERE parent_id IS NULL
    
    UNION ALL
    
    SELECT 
        c.id,
        c.name,
        c.parent_id,
        ct.level + 1,
        ct.path || ' > ' || c.name
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT * FROM category_tree;

-- View: Ideas ready for use with source info
CREATE VIEW IF NOT EXISTS v_ideas_ready AS
SELECT 
    i.id,
    i.concept,
    i.elaboration,
    i.use_cases,
    i.priority,
    i.status,
    i.created_at,
    ci.title as source_title,
    ci.type as source_type,
    c.name as category_name
FROM ideas i
JOIN content_items ci ON i.content_id = ci.id
LEFT JOIN categories c ON ci.category_id = c.id
WHERE i.status IN ('new', 'ready');

-- View: Top gold sentences
CREATE VIEW IF NOT EXISTS v_top_gold_sentences AS
SELECT 
    gs.id,
    gs.sentence,
    gs.context,
    gs.rating,
    gs.usage_count,
    ci.title as source_title,
    ci.author as source_author
FROM gold_sentences gs
JOIN content_items ci ON gs.content_id = ci.id
ORDER BY gs.rating DESC, gs.usage_count ASC;

-- ============================================
-- INITIAL DATA
-- ============================================

-- Default categories
INSERT OR IGNORE INTO categories (name, description) VALUES
    ('Uncategorized', 'Default category for unclassified content'),
    ('Books', 'Books and reading notes'),
    ('Articles', 'Online articles and blog posts'),
    ('Videos', 'Video content and transcripts'),
    ('Ideas', 'Original ideas and concepts'),
    ('Quotes', 'Notable quotes and sayings');

-- Default tags
INSERT OR IGNORE INTO tags (name, color, description) VALUES
    ('important', '#ef4444', 'High priority content'),
    ('idea', '#f59e0b', 'Contains actionable ideas'),
    ('quote', '#10b981', 'Notable quote or saying'),
    ('insight', '#3b82f6', 'Deep insight or realization'),
    ('todo', '#8b5cf6', 'Needs further action'),
    ('review', '#ec4899', 'Needs review');
