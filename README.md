# Content Idea Generator

💡 A comprehensive skill for capturing, organizing, and analyzing content inspiration to generate actionable content ideas.

---

## 📋 Table of Contents

- [Part 1: To AI Agent](#part-1-to-ai-agent) - Technical documentation for AI agents
- [Part 2: To Human User](#part-2-to-human-user) - User guide in Chinese (中文)

---

## Part 1: To AI Agent

### 1. Installation

```bash
# Clone to OpenClaw skills directory
cd ~/.openclaw/skills
git clone https://github.com/Charpup/content-idea-generator.git

# Install dependencies
cd content-idea-generator
pip3 install -r requirements.txt

# Download NLTK data (optional, for enhanced NLP)
python3 -m nltk.downloader punkt stopwords
```

**Requirements:**
- Python 3.8+
- SQLite 3.35+ (with FTS5 support)
- 100MB disk space

### 2. Deployment

```bash
# Initialize database
python3 main.py init

# Verify installation
python3 -c "from database import ContentIdeaDatabase; print('✅ Database OK')"
python3 -c "from analysis import AnalysisEngine; print('✅ Analysis OK')"
```

### 3. Acceptance Testing

| Test | Command | Expected Result |
|------|---------|----------------|
| Database init | `python3 main.py init` | Database created |
| Capture content | `python3 main.py capture --type note --title "Test" --content "Hello"` | Content ID returned |
| Search | `python3 main.py search "test"` | Search results |
| Analysis | `python3 main.py analyze --daily` | Report generated |
| Export | `python3 main.py export --output /tmp/test` | Files exported |

### 4. Usage Guide for Agents

**When to trigger this skill:**
- User says Chinese trigger words like "记灵感", "记笔记", "收藏了"
- User wants to capture content ideas or reading notes
- User asks for content suggestions or analysis
- User mentions Obsidian export

**Key capabilities:**
```python
from content_idea_generator import ContentIdeaManager

manager = ContentIdeaManager()

# Capture content from user input
content_id = manager.capture(
    type="article",  # article, book, video, podcast, tweet, note, idea
    title="User provided title",
    content="User provided content",
    source="URL if available",
    tags=["tag1", "tag2"]
)

# Search existing content
results = manager.search("keywords")

# Generate suggestions
suggestions = manager.analyze_and_suggest()

# Export to Obsidian
manager.export_to_obsidian(content_id)
```

### 5. User Onboarding Guide

**How to guide human users:**

1. **Introduce the skill:**
   > "我可以帮你记录灵感、整理笔记、分析内容，还能导出到 Obsidian。"

2. **Show trigger words:**
   > "你可以直接说：记灵感、记笔记、收藏了、这句好、整理笔记、素材库、内容分析、Obsidian导出"

3. **Demonstrate with examples:**
   - "记灵感：这篇文章讲的是 AI 写作工具..."
   - "收藏了：这个选题不错，关于时间管理"
   - "整理笔记：帮我分析一下我收集的素材"

4. **Explain the workflow:**
   - 捕捉 → 整理 → 分析 → 导出
   - Capture → Organize → Analyze → Export

---

## Part 2: To Human User (中文)

### 💡 这是什么？

**Content Idea Generator** 是你的「灵感管家」。

看书看到好句子？刷到不错的选题？突然想到一个点子？

告诉它，它会帮你：**记下来 → 分好类 → 做分析 → 导出来**

### ✨ 能做什么？

| 功能 | 说明 | 例子 |
|------|------|------|
| 📝 **记灵感** | 记录任何想法、句子、文章 | "记灵感：这篇文章说..." |
| 🏷️ **整理笔记** | 自动分类、打标签 | "整理我的素材库" |
| 🔍 **搜索** | 全文搜索你记过的内容 | "搜一下关于时间管理的" |
| 📊 **分析** | AI 分析你的内容，推荐选题 | "分析我的选题库" |
| 🔄 **导出** | 一键导出到 Obsidian | "导出到 Obsidian" |

### 🚀 怎么用？

**直接说这些词，我就会帮你：**

#### 记录灵感
- "记灵感：这篇文章讲的是..."
- "记笔记：我觉得这个观点很好..."
- "收藏了：这个选题不错"
- "这句好：记录下来"
- "码住：这个素材有用"

#### 整理内容
- "整理笔记"
- "打开素材库"
- "看看我的选题库"
- "整理一下内容"

#### 分析内容
- "内容分析"
- "分析我的选题"
- "复盘整理"
- "给我内容建议"

#### 导出笔记
- "Obsidian导出"
- "导出笔记"
- "导到 Obsidian"

### 📱 完整使用流程

```
看到好内容 → 说"记灵感" → 我帮你记录 → 说"整理笔记" → 自动分类
    ↓
说"内容分析" ← 生成选题建议 ← AI 分析 ← 积累足够多
    ↓
说"Obsidian导出" → 一键导出 → 在你的笔记软件里查看
```

### 🎯 适合谁用？

- ✍️ **公众号写手** - 积累选题、整理素材
- 📱 **小红书/抖音博主** - 记录灵感、追踪热点
- 🎬 **B站 UP主** - 策划内容、整理脚本
- 📚 **知识付费创作者** - 构建知识体系
- 📝 **Newsletter 作者** - 收集金句、整理观点

### 💬 真实对话例子

**你：** 记灵感：刚才看到一篇文章说，每天写 500 字比一周写一次 3500 字更有效

**我：** ✅ 已记录！标题：写作频率对比，标签：写作、习惯

**你：** 收藏了：这个"渐进式总结"的方法不错

**我：** ✅ 已保存到素材库！需要我帮你整理相关的内容吗？

**你：** 整理笔记

**我：** 📊 你的素材库现状：
- 总笔记：23 条
- 分类：写作(8)、效率(5)、思考(10)
- 建议：可以建立一个"写作方法"专题

**你：** 内容分析

**我：** 💡 基于你的收藏，推荐 3 个选题：
1. 《为什么我放弃了周更，选择日更》
2. 《渐进式总结：我的知识管理方法》
3. 《从 0 到 1 建立写作习惯》

**你：** Obsidian导出

**我：** ✅ 已导出到 ~/Obsidian/Vault/Content-Ideas/
包含：23 条笔记 + 3 个选题建议

### 🔧 需要配置吗？

**基本不用！** 开箱即用。

如果你想导出到 Obsidian，告诉我你的 Vault 路径：
> "设置 Obsidian 路径为 ~/Obsidian/Vault"

### ❓ 常见问题

**Q: 我的数据存在哪里？**
A: 存在你的电脑上，~/.openclaw/content-ideas.db，完全私密

**Q: 支持哪些类型的内容？**
A: 文章、书籍、视频、播客、推文、笔记、想法，都可以

**Q: 可以搜索吗？**
A: 可以！支持全文搜索，就像 Google 一样

**Q: 和 Obsidian 什么关系？**
A: 你可以随时把记录的内容导出到 Obsidian，两边不冲突

### 🎬 快速开始

现在就试试：

> **"记灵感：看到一个观点，说写作的本质是思考"**

我会帮你记录下来，以后随时可以找到！

---

## Trigger Words Reference

### Chinese Triggers (中文触发词)

| Category | Triggers |
|----------|----------|
| Capture | 记灵感, 记笔记, 记下来, 灵感记录, 记录灵感, 笔记灵感, 收藏了, 码住, 这句好, 摘抄 |
| Organize | 整理笔记, 素材库, 选题库, 内容库, 素材整理, 笔记整理, 选题整理, 建立素材库 |
| Analyze | 内容分析, 选题分析, 复盘整理, 内容规划, 选题策划 |
| Export | Obsidian导出, 导出笔记, 笔记导出, 导出到Obsidian |
| Suggest | 内容建议, 选题建议, 灵感推荐, 内容创意, 爆款选题 |

### English Triggers

| Category | Triggers |
|----------|----------|
| Capture | content idea, capture inspiration, reading notes, content library |
| Organize | organize articles, content library |
| Export | Obsidian export |
| Suggest | content suggestion |

---

## Technical Details

### Project Structure
```
content-idea-generator/
├── SKILL.md              # Skill documentation
├── main.py               # CLI entry point
├── config.yaml           # Configuration
├── requirements.txt      # Dependencies
├── database/             # SQLite database module
├── models/               # Data models
├── capture/              # Content ingestion
├── analysis/             # NLP analysis engine
├── report/               # Report formatting
└── chat/                 # Chat interface
```

### Database Schema
- **categories** - Hierarchical content categories
- **tags** - Tags with colors
- **content_items** - Main content storage
- **text_snippets** - Extracted snippets
- **gold_sentences** - High-value sentences
- **ideas** - Extracted ideas
- **content_fts** - FTS5 full-text search index

### CLI Commands
```bash
python3 main.py init                    # Initialize database
python3 main.py capture [options]       # Capture content
python3 main.py search [query]          # Search content
python3 main.py list [options]          # List items
python3 main.py analyze [options]       # Run analysis
python3 main.py export [options]        # Export to Obsidian
python3 main.py stats                   # Show statistics
python3 main.py test                    # Run tests
```

## License

MIT License

## Changelog
- 2026-03-11: Skill audit upgrade — normalized SKILL.md frontmatter to `name` + `description`, revalidated trigger wording, and rechecked lightweight lint/smoke compatibility with OpenClaw.
