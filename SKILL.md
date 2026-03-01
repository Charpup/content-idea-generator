---
name: content-idea-generator
description: "Capture, organize, and analyze content ideas. Get daily inspiration reports and content suggestions."
version: 1.0.0
author: Galatea
homepage: https://github.com/openclaw/skills
tags: ["content", "ideas", "creativity", "writing", "productivity"]
---

# Content Idea Generator

**Your personal content inspiration library.**

Capture ideas from anywhere — text, voice, or screenshots. Get daily analysis and content suggestions delivered to your chat.

## ✨ Features

- **Multi-input capture**: Text, voice (whisper.cpp), screenshots (OCR)
- **Smart organization**: Tags, categories, full-text search
- **Daily analysis**: Automated reports with insights
- **Content suggestions**: AI-powered topic recommendations
- **Obsidian export**: Sync to your knowledge base

## 🚀 Quick Start

### Installation

```bash
# Clone to skills directory
git clone https://github.com/openclaw/skills/content-idea-generator \
  ~/.openclaw/skills/content-idea-generator

# Install dependencies
pip install -r requirements.txt

# Optional: Install whisper.cpp for voice
# See: https://github.com/ggerganov/whisper.cpp
```

### Configuration

Create `config.yaml`:

```yaml
database:
  path: "~/.openclaw/content-idea-generator/library.db"
  
whisper:
  enabled: true
  model: "base"  # tiny/base/small/medium/large
  path: "whisper-cli"
  
report:
  schedule: "daily"  # daily/weekly
  time: "09:00"
  
obsidian:
  export_path: "~/Obsidian/Content Ideas"
```

## 💬 Usage

### Capture Ideas

```
/capture Python decorators tutorial #python #advanced
✅ Idea saved!
> Python decorators tutorial
Type: tutorial | Tags: #python #advanced
ID: idea-001
```

### Voice Input

```
/voice
🎙️ Send me a voice message and I'll transcribe it!
```

### Search Ideas

```
/search python
🔍 Found 3 ideas:
1. Python decorators tutorial...
2. Python tips for beginners...
3. Advanced Python patterns...
```

### Daily Report

```
/report
📊 Daily Inspiration Report

📈 Stats:
• 5 new ideas today
• 3 from voice, 2 from text
• Top tag: #python

💡 Suggestions:
🟢 Create a "Python Advanced" series (confidence: 85%)
Related: idea-001, idea-004

📝 Quick Drafts:
[Twitter] 5 Python decorators you should know 🧵👇
[LinkedIn] Advanced Python: Decorators Explained
```

## 📝 Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/capture <text>` | Save text idea | `/capture Blog post about AI` |
| `/voice` | Capture voice message | Send voice message |
| `/screenshot` | Capture from image | Send screenshot |
| `/search <query>` | Search ideas | `/search python` |
| `/report` | Generate daily report | `/report` |
| `/help` | Show help | `/help` |

## 🏗️ Architecture

```
User Input → Capture → Storage → Analysis → Report
    ↓           ↓          ↓          ↓         ↓
  Text      Parse     SQLite    Cluster   Chat
  Voice     Extract   + FTS5    Connect   Format
  Image     Save      Index     Generate  Deliver
```

### Modules

- **capture**: Text, voice, screenshot input
- **models**: Idea, Tag, Category data models
- **database**: SQLite + FTS5 storage
- **analysis**: HAC clustering, suggestion generation
- **report**: Daily/weekly reports, chat formatting
- **chat**: Command parsing, interaction handling

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test category
pytest tests/unit/
pytest tests/integration/
```

## 📦 Dependencies

```
python >= 3.9
sqlite3 (built-in)
pytesseract (optional, for OCR)
Pillow (optional, for image processing)
whisper.cpp (optional, for voice)
```

## 🔒 Privacy

- All data stored locally in SQLite
- No cloud services required
- Optional: Use local LLM for analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests (TDD)
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file

## 🙏 Credits

- OpenClaw framework
- whisper.cpp by Georgi Gerganov
- SQLite FTS5

---

**Made with ❤️ by Galatea for Charpup**
