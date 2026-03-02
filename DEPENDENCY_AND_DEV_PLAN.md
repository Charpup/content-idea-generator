# Content Idea Generator - Dependency Analysis & Development Plan

**Date:** 2026-03-02  
**TriadDev Version:** 3.0 (SDD+TDD Dual Workflow)  
**TDD-SDD Version:** 3.0 (RED-GREEN-REFACTOR Engine)

---

## 📦 核心模块依赖分析

### 1. 数据库模块 (Database)

**功能需求:**
- SQLite 数据持久化
- FTS5 全文搜索
- 多表关联 (ideas, tags, categories)

**依赖方案:**
| 依赖 | 用途 | 安装方式 | 必需 |
|------|------|----------|------|
| `sqlite3` | 数据库引擎 | Python 内置 | ✅ |
| `sqlite-fts5` | 全文搜索 | SQLite 内置 | ✅ |

**无外部依赖** - SQLite 是 Python 标准库

---

### 2. 分析引擎 (Analysis Engine)

**功能需求:**
- HAC 层次聚类
- TF-IDF 特征提取
- 内容建议生成
- 关键词提取

**依赖方案对比:**

| 方案 | 优点 | 缺点 | 推荐 |
|------|------|------|------|
| **scikit-learn** | 成熟, HAC内置, 文档丰富 | 较大依赖 (~20MB) | ⭐ 首选 |
| **scipy** | 科学计算基础, linkage可用 | 需配合其他库 | 备选 |
| **纯Python实现** | 零依赖, 可控 | 性能差, 维护成本高 | 不推荐 |

**选定方案: scikit-learn**
```bash
pip install scikit-learn
```

**具体使用:**
- `sklearn.cluster.AgglomerativeClustering` - HAC聚类
- `sklearn.feature_extraction.text.TfidfVectorizer` - TF-IDF
- `sklearn.metrics.pairwise.cosine_similarity` - 相似度计算

---

### 3. 报告生成 (Report Generation)

**功能需求:**
- Chat格式输出 (Discord/Telegram)
- Markdown导出 (Obsidian)
- 模板渲染
- 统计数据可视化

**依赖方案:**
| 依赖 | 用途 | 必需 |
|------|------|------|
| `jinja2` | 模板引擎 | ✅ 推荐 |
| `rich` | 终端美化 (可选) | ⭐ 可选 |

**选定方案: jinja2 (轻量)**
```bash
pip install jinja2
```

---

### 4. 内容采集 (Capture)

**功能需求:**
- 文本解析
- 语音转文字 (whisper.cpp)
- 截图OCR

**依赖方案:**

#### 4.1 语音 (whisper.cpp)
| 方案 | 说明 | 必需 |
|------|------|------|
| `whisper.cpp` | C++实现, CPU运行 | ⭐ 推荐 |
| `openai-whisper` | Python绑定, 需下载模型 | 备选 |

**选定: whisper.cpp (本地, 无API费用)**
- 安装: 编译 whisper.cpp 二进制
- Python调用: `subprocess` 直接调用

#### 4.2 OCR (截图)
| 方案 | 说明 | 必需 |
|------|------|------|
| `pytesseract` | Python wrapper | ✅ |
| `tesseract-ocr` | 系统包 | ✅ (apt/yum/brew) |
| `Pillow` | 图像处理 | ✅ |

**安装:**
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Python
pip install pytesseract Pillow
```

---

### 5. 其他依赖

| 依赖 | 用途 | 必需 |
|------|------|------|
| `pyyaml` | YAML配置解析 | ✅ |
| `click` | CLI命令行 | ⭐ 推荐 |
| `pytest` | 测试框架 | ✅ (开发) |
| `pytest-cov` | 覆盖率 | ✅ (开发) |

---

## 📋 完整依赖清单

### 运行时依赖 (requirements.txt)
```
# Core
pyyaml>=6.0
click>=8.0.0

# Analysis
scikit-learn>=1.3.0

# Report
jinja2>=3.1.0

# OCR
pytesseract>=0.3.10
Pillow>=10.0.0

# Optional (for better output)
rich>=13.0.0
```

### 开发依赖
```
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-asyncio>=0.21.0
black>=23.0.0
mypy>=1.0.0
```

### 系统依赖
```bash
# Ubuntu/Debian
sudo apt-get install -y sqlite3 tesseract-ocr

# macOS
brew install sqlite tesseract

# whisper.cpp (需编译)
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp
make
```

---

## 🚀 TriadDev 3.0 开发计划

### Phase 1: SDD (Spec-Driven) - 2小时
**目标:** 完善 SPEC.yaml, 定义所有接口

```bash
# 使用 TriadDev v3.0 SDD 模式
triaddev sdd "Content Idea Generator - Core Implementation"

# 生成:
# - specs/database-spec.yaml
# - specs/analysis-spec.yaml
# - specs/report-spec.yaml
```

**任务:**
- [ ] 定义 Database 接口 (CRUD, FTS5)
- [ ] 定义 AnalysisEngine 接口 (cluster, suggest)
- [ ] 定义 ReportGenerator 接口 (daily, export)
- [ ] 定义数据模型 (Idea, Tag, Category)

---

### Phase 2: TDD (Test-Driven) - 4小时
**目标:** RED-GREEN-REFACTOR 完成核心模块

```bash
# 使用 TDD-SDD v3.0
triaddev tdd specs/database-spec.yaml
# RED → GREEN → REFACTOR → Coverage 80%+

triaddev tdd specs/analysis-spec.yaml
triaddev tdd specs/report-spec.yaml
```

**任务:**
- [ ] Database 模块 + 测试 (100% coverage)
- [ ] AnalysisEngine + 测试 (HAC, TF-IDF)
- [ ] ReportGenerator + 测试 (模板渲染)
- [ ] Integration 测试 (端到端)

---

### Phase 3: Implementation - 3小时
**目标:** 集成所有模块, 完善 CLI 和 Chat 接口

```bash
triaddev implement task-001 --requirements "Complete database layer"
triaddev implement task-002 --requirements "Analysis engine with clustering"
triaddev implement task-003 --requirements "Report generation"
triaddev implement task-004 --requirements "CLI and Chat integration"
```

**任务:**
- [ ] 实现 database.py
- [ ] 实现 analysis/engine.py
- [ ] 实现 report/daily.py
- [ ] 更新 chat.py (错误处理)
- [ ] 更新 main.py (完整 CLI)

---

### Phase 4: Deployment - 1小时
**目标:** 打包, 文档, GitHub 发布

```bash
# 更新 requirements.txt
# 完善 SKILL.md
# 创建安装脚本
# GitHub Release
```

---

## 📊 时间估算

| 阶段 | 时间 | 产出 |
|------|------|------|
| SDD (Spec) | 2h | 3个 SPEC.yaml |
| TDD (Test) | 4h | 完整测试套件, 80%+ 覆盖率 |
| Implementation | 3h | 可运行的核心模块 |
| Deployment | 1h | 发布就绪的 skill |
| **总计** | **10h** | **完整可用的 skill** |

---

## 🎯 成功标准

- ✅ 所有 `/capture`, `/search`, `/report` 命令可用
- ✅ 数据库持久化 + FTS5 搜索
- ✅ HAC 聚类分析 + 内容建议
- ✅ 日报生成 + Obsidian 导出
- ✅ 测试覆盖率 80%+
- ✅ 零硬编码配置
- ✅ 完整错误处理

---

*Plan Created: 2026-03-02 | TriadDev 3.0 | TDD-SDD 3.0*
