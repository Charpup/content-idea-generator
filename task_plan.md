# Content Idea Generator Skill - Task Plan

**Project:** Content-Idea-Generator-Skill  
**Created:** 2026-03-01  
**Source:** Master (Charpup) 的聊天记录截图  
**Mode:** TriadDev + Subagent-First

---

## 📋 原始需求提取

来自截图中的核心需求：

> 内容灵感收集器：
> - 平时刷推/即刻/小红书/即刻/即刻（重复）时，看到好玩的内容/帖子/图片
> - 可以一键收藏到「灵感库」
> - 灵感库可以打标签、分类
> - 定期（比如每周）自动分析灵感库
> - 生成选题建议/内容方向
> - 输出选题报告

**核心功能**:
1. 多平台内容一键收藏
2. 标签/分类管理
3. 定期自动分析
4. 选题建议生成
5. 报告输出

---

## 🎯 任务计划 (Subagent-First)

### Phase 1: 需求分析与拆分 (当前)
- [x] 提取原始需求
- [ ] 拆分功能模块
- [ ] 分析 DAG 依赖
- [ ] 定义 MVP vs 完整版

### Phase 2: 市场调研 (Subagents)
- [ ] Task 2.1: 搜索 GitHub 现有内容收藏/灵感管理工具
- [ ] Task 2.2: 搜索 ClawHub 相关 skills
- [ ] Task 2.3: 调研现有笔记工具集成 (Notion, Obsidian, etc.)
- [ ] Task 2.4: 调研内容分析/选题生成相关工具

### Phase 3: 需求论证
- [ ] 汇总调研结果
- [ ] 评估自建 vs 复用现有方案
- [ ] 确定技术路线

### Phase 4: 架构设计
- [ ] 设计文档 (SPEC.yaml)
- [ ] 数据模型设计
- [ ] API 接口设计

### Phase 5: 实现
- [ ] 开发
- [ ] 测试
- [ ] 部署

---

## 🔍 功能模块拆分

### Module A: 内容采集层
- A1: 浏览器插件/书签脚本
- A2: 移动端分享扩展
- A3: 内容解析 (提取正文/图片/元数据)

### Module B: 存储管理层
- B1: 灵感库数据模型
- B2: 标签系统
- B3: 分类管理
- B4: 搜索/过滤

### Module C: 分析引擎
- C1: 内容特征提取
- C2: 聚类分析
- C3: 趋势识别
- C4: 选题生成算法

### Module D: 输出层
- D1: 报告生成
- D2: 定时任务 (cron)
- D3: 通知推送

---

## 📊 DAG 依赖分析

```
A (采集) → B (存储) → C (分析) → D (输出)
                ↓
           [定时触发]
```

**关键路径**: A → B → C → D
**可并行**: A1/A2/A3, C1/C2/C3

---

## 🤖 Subagent 分配

| Subagent | 任务 | 依赖 |
|----------|------|------|
| research-github | 搜索 GitHub 相关内容工具 | 无 |
| research-clawhub | 搜索 ClawHub 相关 skills | 无 |
| research-notion | 调研 Notion 等笔记工具集成 | 无 |
| research-ai-tools | 调研 AI 内容分析工具 | 无 |

---

## 🚀 下一步

启动 Phase 2 市场调研 subagents。

---

*Plan Created: 2026-03-01*
