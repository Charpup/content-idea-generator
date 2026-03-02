---
name: content-idea-generator
description: Content Idea Generator Skill - Capture, organize, and analyze content inspiration to generate actionable content ideas. Use when users want to capture content ideas, organize reading notes, extract insights from articles/videos, manage content library, generate content suggestions, or export notes to Obsidian. Triggers on "content idea", "capture inspiration", "reading notes", "content library", "organize articles", "Obsidian export", "content suggestion", "记灵感", "记笔记", "记下来", "灵感记录", "记录灵感", "笔记灵感", "收藏了", "码住", "这句好", "摘抄", "整理笔记", "素材库", "选题库", "内容库", "素材整理", "笔记整理", "选题整理", "建立素材库", "内容分析", "选题分析", "复盘整理", "内容规划", "选题策划", "Obsidian导出", "导出笔记", "笔记导出", "导出到Obsidian", "内容建议", "选题建议", "灵感推荐", "内容创意", "爆款选题".
triggers:
  # 捕捉类
  - 记灵感
  - 记笔记
  - 记下来
  - 灵感记录
  - 记录灵感
  - 笔记灵感
  - 收藏了
  - 码住
  - 这句好
  - 摘抄
  # 整理类
  - 整理笔记
  - 素材库
  - 选题库
  - 内容库
  - 素材整理
  - 笔记整理
  - 选题整理
  - 建立素材库
  # 分析类
  - 内容分析
  - 选题分析
  - 复盘整理
  - 内容规划
  - 选题策划
  # 导出类
  - Obsidian导出
  - 导出笔记
  - 笔记导出
  - 导出到Obsidian
  # 建议类
  - 内容建议
  - 选题建议
  - 灵感推荐
  - 内容创意
  - 爆款选题
metadata:
  openclaw:
    emoji: "💡"
    version: "1.0.0"
    requires:
      bins: ["python3", "pip3"]
      env: []
      python_packages: ["sqlite3", "nltk", "scikit-learn", "numpy"]
    os: ["linux", "macos", "windows"]
    install:
      - pip3 install -r requirements.txt
      - python3 -m nltk.downloader punkt stopwords
---

# Content Idea Generator

A comprehensive skill for capturing, organizing, and analyzing content inspiration to generate actionable content ideas.

## Overview

The Content Idea Generator helps you:
- **Capture** content from various sources (articles, videos, books, tweets)
- **Organize** with categories, tags, and hierarchical structures
- **Extract** key snippets, gold sentences, and ideas
- **Analyze** patterns and connections between ideas
- **Generate** content suggestions and drafts
- **Export** to Obsidian for seamless knowledge management

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONTENT IDEA GENERATOR                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ CAPTURE  │  │ DATABASE │  │ ANALYSIS │  │  REPORT  │        │
│  │          │  │          │  │          │  │          │        │
│  │ • Input  │  │ • SQLite │  │ • NLP    │  │ • Chat   │        │
│  │ • Parse  │  │ • FTS5   │  │ • ML     │  │ • Export │        │
│  │ • Store  │  │ • Schema │  │ • Graph  │  │ • Format │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│       │              │              │              │            │
│       └──────────────┴──────────────┴──────────────┘            │
│                         │                                       │
│                    ┌──────────┐                                 │
│                    │   CHAT   │                                 │
│                    │  INTERFACE │                               │
│                    └──────────┘                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Requirements

- Python 3.8+
- SQLite 3.35+ (with FTS5 support)
- 100MB disk space for database
- Optional: NLTK data for NLP features

## Installation

### Quick Install

```bash
# Clone or copy skill to OpenClaw skills directory
cp -r content-idea-generator ~/.openclaw/skills/

# Install dependencies
cd ~/.openclaw/skills/content-idea-generator
pip3 install -r requirements.txt

# Download NLTK data (optional, for enhanced NLP)
python3 -m nltk.downloader punkt stopwords
```

### Verify Installation

```bash
python3 -c "from database import ContentIdeaDatabase; print('✅ Database module OK')"
python3 -c "from analysis import AnalysisEngine; print('✅ Analysis module OK')"
```

## Configuration

Create `config.yaml` in the skill directory:

```yaml
# Content Idea Generator Configuration

database:
  path: "~/.openclaw/content-ideas.db"
  backup_interval_days: 7

capture:
  default_category: "Uncategorized"
  auto_extract_snippets: true
  max_snippet_length: 1000

analysis:
  enabled: true
  schedule: "0 9 * * *"  # Daily at 9 AM
  min_cluster_size: 2
  similarity_threshold: 0.4
  max_suggestions: 5

nlp:
  language: "english"
  extract_keywords: true
  sentiment_analysis: true
  entity_recognition: false  # Requires additional setup

export:
  obsidian_vault_path: "~/Obsidian/Vault"
  export_format: "markdown"
  include_metadata: true

chat:
  max_suggestions_display: 3
  enable_draft_previews: true
  emoji_indicators: true
```

## Usage

### Command Line Interface

```bash
# Initialize database
python3 main.py init

# Capture content
python3 main.py capture --type article --title "Title" --content "..."
python3 main.py capture --file article.txt --type book

# Search content
python3 main.py search "machine learning"
python3 main.py search "AI AND ethics"

# List items
python3 main.py list --type article --status active
python3 main.py list-ideas --status ready

# Generate analysis
python3 main.py analyze --daily
python3 main.py analyze --cluster

# Export to Obsidian
python3 main.py export --output ~/Obsidian/Vault
python3 main.py export --content-id 123

# Get statistics
python3 main.py stats

# Run tests
python3 main.py test
```

### Python API

```python
from content_idea_generator import ContentIdeaManager

# Initialize manager
manager = ContentIdeaManager()

# Capture content
content_id = manager.capture(
    type="article",
    title="The Future of AI",
    content="Full article text...",
    source="https://example.com",
    author="Jane Doe",
    tags=["AI", "future", "technology"]
)

# Extract snippets
manager.add_snippet(content_id, "Key quote here...", context="Introduction")

# Create idea
idea_id = manager.create_idea(
    content_id=content_id,
    concept="AI Accessibility",
    elaboration="Making AI accessible to everyone...",
    use_cases=["Education", "Healthcare"]
)

# Search
results = manager.search("AI accessibility")

# Analyze and generate suggestions
suggestions = manager.analyze_and_suggest()

# Export to Obsidian
manager.export_to_obsidian(content_id)
```

## Module Reference

### Database Module (`database/`)

SQLite database with FTS5 full-text search support.

**Key Classes:**
- `ContentIdeaDatabase` - Main database interface

**Features:**
- Hierarchical categories
- Tags with colors
- Content items (article, book, video, podcast, tweet, note, idea)
- Text snippets with context
- Gold sentences tracking
- Ideas with relations
- Full-text search (FTS5)
- Obsidian export

### Models Module (`models/`)

Data models and schemas.

**Key Classes:**
- `ContentItem` - Content item model
- `Idea` - Idea model
- `Category` - Category model
- `Tag` - Tag model
- `Snippet` - Text snippet model

### Capture Module (`capture/`)

Content ingestion and parsing.

**Key Classes:**
- `ContentCapture` - Capture content from various sources
- `TextParser` - Parse and clean text content
- `URLFetcher` - Fetch content from URLs (optional)

### Analysis Module (`analysis/`)

Content analysis and idea generation.

**Key Classes:**
- `AnalysisEngine` - Main analysis engine
- `TopicClusterer` - Cluster related content
- `ContentGenerator` - Generate content suggestions
- `ConnectionFinder` - Find connections between ideas

**Analysis Pipeline:**
1. **Ingest** - Load new content items
2. **Analyze** - Extract keywords, sentiment, entities
3. **Cluster** - Group similar content
4. **Connect** - Find relationships between ideas
5. **Generate** - Create content suggestions
6. **Format** - Prepare chat-friendly reports

### Report Module (`report/`)

Report generation and formatting.

**Key Classes:**
- `ReportFormatter` - Format analysis results
- `ChatFormatter` - Format for chat display
- `MarkdownExporter` - Export to Markdown

### Chat Module (`chat/`)

Chat interface for interactive use.

**Key Classes:**
- `ChatInterface` - Main chat interface
- `CommandParser` - Parse chat commands
- `ResponseBuilder` - Build chat responses

## Examples

### Example 1: Capture Article with Snippets

```python
from content_idea_generator import ContentIdeaManager

manager = ContentIdeaManager()

# Capture article
article_id = manager.capture(
    type="article",
    title="10 Tips for Better Writing",
    content="Full article text here...",
    source="https://writingtips.com/article",
    author="John Writer",
    category="Writing",
    tags=["writing", "tips", "productivity"]
)

# Extract key snippets
manager.add_snippet(
    content_id=article_id,
    snippet_text="Write every day, even if it's just 100 words.",
    context="Tip #1",
    notes="Great advice for building habits"
)

manager.add_snippet(
    content_id=article_id,
    snippet_text="Read widely to expand your vocabulary.",
    context="Tip #3"
)

# Mark as gold sentence
manager.add_gold_sentence(
    content_id=article_id,
    sentence="Consistency beats intensity in writing.",
    rating=5
)

# Create idea from content
idea_id = manager.create_idea(
    content_id=article_id,
    concept="Daily Writing Habit",
    elaboration="Build a sustainable daily writing practice...",
    use_cases=["Blogging", "Book writing", "Journaling"],
    priority=5,
    status="ready"
)

print(f"✅ Captured article with ID: {article_id}")
print(f"✅ Created idea with ID: {idea_id}")
```

### Example 2: Search and Export

```python
from content_idea_generator import ContentIdeaManager

manager = ContentIdeaManager()

# Search for writing-related content
results = manager.search("writing AND habit")
print(f"Found {len(results)} results:")
for r in results:
    print(f"  - {r['title']} (rank: {r['rank']})")

# Export to Obsidian
export_path = "~/Obsidian/Vault/Content Ideas"
counts = manager.export_all_to_obsidian(export_path)
print(f"Exported {counts['content']} content items and {counts['ideas']} ideas")
```

### Example 3: Daily Analysis

```python
from content_idea_generator import ContentIdeaManager

manager = ContentIdeaManager()

# Run daily analysis
report = manager.run_daily_analysis()

# Display top suggestions
print("💡 Top Content Suggestions:")
for i, suggestion in enumerate(report['suggestions'][:3], 1):
    print(f"\n{i}. {suggestion['title']}")
    print(f"   Confidence: {suggestion['confidence']:.0%}")
    print(f"   Based on {suggestion['item_count']} items")
    if 'draft_preview' in suggestion:
        print(f"   Preview: {suggestion['draft_preview'][:100]}...")

# Get statistics
stats = manager.get_statistics()
print(f"\n📊 Library Statistics:")
print(f"   Content Items: {stats['content_items']}")
print(f"   Ideas: {stats['ideas']}")
print(f"   Categories: {stats['categories']}")
```

### Example 4: Command Line Usage

```bash
# Capture a book note
python3 main.py capture \
  --type book \
  --title "Atomic Habits" \
  --author "James Clear" \
  --content "$(cat atomic_habits_notes.txt)" \
  --category "Self-Improvement" \
  --tags "habits,productivity,psychology"

# Search for habit-related content
python3 main.py search "habit AND (build OR create)"

# List all ready ideas
python3 main.py list-ideas --status ready

# Export everything to Obsidian
python3 main.py export --output ~/Obsidian/Vault/Reading

# Run analysis and see suggestions
python3 main.py analyze --daily
```

## Database Schema

### Tables

| Table | Description |
|-------|-------------|
| `categories` | Hierarchical content categories |
| `tags` | Tags with colors |
| `content_items` | Main content storage |
| `content_tags` | Content-tag relationships |
| `text_snippets` | Extracted text snippets |
| `snippet_tags` | Snippet-tag relationships |
| `gold_sentences` | High-value sentences |
| `ideas` | Extracted ideas/concepts |
| `idea_relations` | Relationships between ideas |
| `content_fts` | FTS5 virtual table for search |

### Views

| View | Description |
|------|-------------|
| `v_content_full` | Content with category and tags |
| `v_category_tree` | Hierarchical category tree |
| `v_ideas_ready` | Ideas ready for use |
| `v_top_gold_sentences` | Top-rated gold sentences |

## Troubleshooting

### Database Locked

If you encounter "database is locked" errors:
```bash
# Check for other processes
lsof ~/.openclaw/content-ideas.db

# Backup and recreate if needed
cp ~/.openclaw/content-ideas.db ~/.openclaw/content-ideas.db.backup
```

### FTS5 Not Available

If FTS5 is not available:
```bash
# Check SQLite version
sqlite3 --version

# FTS5 requires SQLite 3.35+
# Upgrade SQLite or use basic search
```

### NLTK Data Missing

If NLP features fail:
```bash
python3 -m nltk.downloader punkt stopwords averaged_perceptron_tagger
```

## Tips

1. **Use Tags Consistently** - Create a tag taxonomy early
2. **Extract Snippets** - Capture key quotes while reading
3. **Rate Gold Sentences** - Mark high-value sentences for reuse
4. **Link Ideas** - Create relations between related ideas
5. **Export Regularly** - Backup to Obsidian periodically
6. **Run Analysis Daily** - Get fresh content suggestions

## License

MIT License - See LICENSE file for details.
