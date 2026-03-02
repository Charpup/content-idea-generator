# Content Idea Generator Skill - Revised Task Plan

**Project:** Content-Idea-Generator-Skill  
**Date:** 2026-03-01  
**Version:** 2.0 (基于 Master 反馈修订)

---

## 📋 Master 反馈要点

| 原始想法 | 调整 | 影响 |
|----------|------|------|
| 社交媒体输入为主 | **用户主动输入为主** | 改变采集方式 |
| 语音输入 | **需要本地语音转文字** | 新增技术模块 |
| Notion/Obsidian | **可能偏重度** | 考虑更轻量存储 |
| 本地 LLM (Ollama) | **否决，走 API 或 Galatea 执行** | 简化架构 |
| 定期分析 | **每日报告 + 串联灵感生成文案** | 增强输出 |
| Karakeep | **质疑其必要性** | 重新评估存储 |

**关键问题**：为什么选 Karakeep？是否需付费？

---

## 🔍 Karakeep 重新评估

### Karakeep 优势
- ✅ 自托管，免费开源
- ✅ AI 自动标签 (OpenAI API)
- ✅ 全文搜索 (Meilisearch)
- ✅ 浏览器扩展 + 移动端
- ✅ REST API

### 但可能不适合的原因
- ❌ 主要是**链接收藏**，不是**灵感/金句收藏**
- ❌ 需要自托管 (Docker)
- ❌ 对用户来说可能过重

### 替代方案考虑
| 方案 | 优势 | 劣势 |
|------|------|------|
| **SQLite 本地文件** | 极简，零配置 | 无现成 UI |
| **Markdown 文件** | 通用，Obsidian 可打开 | 检索需额外工具 |
| **Notion API** | 已有配置，云端 | 需要网络 |
| **飞书文档** | 国内可用，协作好 | API 复杂度 |

---

## 🎯 修订后架构 (方案 C-2)

### 核心流程
```
用户输入 (打字/语音/截图)
    ↓
[语音转文字] (本地工具，如 whisper.cpp)
    ↓
[内容解析] (Galatea 执行)
    ↓
[灵感库] (SQLite/Markdown 本地存储)
    ↓
[每日分析] (Galatea + API)
    ↓
[报告输出] (聊天对话框)
```

### 存储方案选择
**推荐：SQLite + Markdown 混合**
- SQLite：结构化数据，标签、分类、检索
- Markdown：导出给 Obsidian，满足重度用户

---

## 📊 新任务计划

### Phase 3: 需求论证 (修订)
- [ ] Task 3.1: 语音转文字本地工具调研
- [ ] Task 3.2: 轻量级存储方案对比 (SQLite vs Markdown vs 其他)
- [ ] Task 3.3: 用户交互流程设计 (聊天对话框优先)

### Phase 4: 架构设计
- [ ] Task 4.1: 数据模型设计 (灵感条目、标签、分类)
- [ ] Task 4.2: 语音输入模块设计
- [ ] Task 4.3: 每日分析引擎设计
- [ ] Task 4.4: 报告生成模块设计

### Phase 5: SPEC 文档
- [ ] Task 5.1: 编写 SPEC.yaml
- [ ] Task 5.2: API 接口设计
- [ ] Task 5.3: 用户交互流程文档

---

## 🤔 待 Master 确认

1. **存储方案**：SQLite + Markdown 混合是否合适？
2. **语音转文字**：是否接受 whisper.cpp (本地，CPU 可运行)？
3. **LLM 方案**：走外部 API (OpenAI/Claude) 还是 Galatea 直接执行？
4. **输出格式**：每日报告在聊天框输出，是否需要其他格式 (如导出到 Notion)？

---

*Revised Plan: 2026-03-01*
