# Agent Onboarding · 给产品经理的 Agent 实战手册

> 一份**自学闯关型**文档：你不需要老师，跟着每一讲做完任务，就能完成从"听说过 Agent" → "把 Agent 当同事用" → "把 Agent 沉淀成团队资产"的完整跃迁。

---

## 0. 写在前面：PM 这个岗位，已经被 Agent 重新定义了

过去的 PM ≈ **PRD 的生产者**。
今天的 PM ≈ **产品交付的总指挥**：

| 维度 | 旧 PM | 新 PM（Agent 时代） |
|------|-------|---------------------|
| 主要产出 | PRD、需求评审纪要 | PRD + 原型 + 数据洞察 + 可运行 demo + 工具型小产品 |
| 工作方式 | 写文档 → 等研发实现 | 写意图 → Agent 直出可验证产物 → 再交给研发深做 |
| 核心能力 | 表达需求 | **拆解任务 + 指挥 Agent + 沉淀流程** |
| 衡量标准 | 文档质量 | 想法到验证的速度（time-to-evidence） |

**这本手册的核心立场**：
PM 必须能独立用 Agent 交付产物。PRD 不再是终点，而是中间态；很多时候你应当**先用 Agent 跑出一个可点击的 demo / 一份带数据的洞察 / 一个可运行的小工具**，再把它附在需求里推动落地。

---

## 1. 你将得到什么

读完并做完所有任务后，你会拥有：

1. **一条端到端工作流**：基于你选定的练手主线（**需求池整理 / 会议纪要跟进 / 行业 / 竞品周报 三选一**）跑通：素材汇总 → 结构化落盘 → 可视化 dashboard → 飞书分发，每周一键复用。
2. **一套个人 Agent 工作环境**：`llm-wiki/`（个人知识库）+ 若干 Skill + 一份 `AGENTS.md` 使用规范。
3. **一份"我的 Agent 机会清单 v1"**：从你日常工作里识别出 ≥10 个可被 Agent 接管的任务，并按 ROI 排序好的下一步行动表。
4. **一组可迁移的方法论**：Prompt 4 要素、上下文管理、Skill 三要素、人在环路、数据落点设计。

---

## 2. 课程地图（4 篇章 · 12 讲）

> **三选一练手主线（贯穿 L0–L9）**：每讲均提供三种 PM 通用场景版本的 prompt，任选其一为主线练手，方法论 100% 通用。
>
> | 主线 | 适合谁 | 主线产物路径 |
> |---|---|---|
> | 📋 **需求池整理** | 几乎所有 PM（覆盖率最高，推荐默认） | `pm-agent-lab/backlog-lab/` |
> | 📝 **会议纪要 → 待办分发 → 跟进** | 跨团队协作多的 PM（刚需） | `pm-agent-lab/meeting-lab/` |
> | 📰 **行业 / 竞品周报** | 战略 / 对外汇报型 PM | `pm-agent-lab/news-lab/` |
>
> 副线任务：每讲都附"再用另一个场景跑一遍"的迁移练习，以及更进阶的玩法。

### 篇章 A · 认知与上手：理解 Agent 是什么

| 讲次 | 标题 | 你会学会 |
|------|------|----------|
| **L0** | [Chat vs Agent：差别到底在哪](./A-cognition/L0-chat-vs-agent.md) | 用同一个问题对比，亲手感受工具调用 / 自主循环 |
| **L1** | [让 Agent 第一次"动手"：操作本地文件](./A-cognition/L1-first-hands-on.md) | 行业新闻调研 → 结构化落盘到 `news/` |
| **L2** | [Vibe Coding 初体验：不会写代码也能做工具](./A-cognition/L2-vibe-coding.md) | 给本地数据生成可交互 HTML dashboard |
| **L2.5** | [让 Agent 操作浏览器：突破 API 与公开数据的边界](./A-cognition/L2.5-browser-use.md) | 用 Agent 跑登录态 / 后台 / 公开网页的"重复体力活" |

### 篇章 B · 把 Agent 变成生产力

| 讲次 | 标题 | 你会学会 |
|------|------|----------|
| **L3** | [Prompt 工程的最小够用版](./B-productivity/L3-prompt-minimal.md) | 角色 / 上下文 / 约束 / 产物 4 要素模板 |
| **L4** | [上下文管理：搭建你的 LLM Wiki](./B-productivity/L4-llm-wiki.md) | 让 Agent "记得住"你和你的产品 |
| **L4.5** | [多模态：截图 / 设计稿 / 报错图](./B-productivity/L4.5-multimodal.md) | 把 PM 每天看到的图直接交给 Agent 解析 |
| **L5** | [Skill 化：把"做一次"沉淀为"团队资产"](./B-productivity/L5-skill-ization.md) | Skill 三要素：触发、流程、产物 |

### 篇章 C · 企业场景接入：从个人玩具到工作伙伴

| 讲次 | 标题 | 你会学会 |
|------|------|----------|
| **L6** | [Agent + 企业 CLI（飞书 lark-cli 等）](./C-enterprise/L6-lark-cli.md) | CLI 是 Agent 的"手脚延伸" |
| **L7** | [Agent + 数据：文档 / 表格 / 知识库的落点设计](./C-enterprise/L7-data-landing.md) | 什么进文档、什么进多维表格、什么进 wiki |
| **L8** | [Agent + 代码协作：MR 评审、单测、原型代码](./C-enterprise/L8-code-collab.md) | PM 也能 review MR、跑通原型 |
| **L9** | [多步工作流：让 Agent 跑端到端闭环](./C-enterprise/L9-end-to-end-workflow.md) | 周报全链路：调研→HTML→摘要→飞书发送 |

### 篇章 D · 安全、协作与持续进化

| 讲次 | 标题 | 你会学会 |
|------|------|----------|
| **L10** | [边界与安全：哪些事不能让 Agent 独自做](./D-team/L10-boundary.md) | 数据红线 / 默认人工确认 / diff 预览 |
| **L11** | [团队化：Skill 共享、版本与 Review](./D-team/L11-team-skill.md) | 写出第一个能给同事用的 Skill |
| **L12** | [自我进化：找出你工作中的 10 个 Agent 机会](./D-team/L12-self-evolution.md) | 输出"我的 Agent 机会清单 v1" |

---

## 3. 学习路径建议

### 路径 A · 最小可行（约 1 周，先尝鲜）
`L0 → L1 → L2 → L5`
做完你已经能体会到 "Chat 只能聊 → Agent 能动手 → Agent 能帮你做产品 → Agent 能沉淀流程"。

### 路径 B · 完整版（约 4 周，强烈推荐 PM 走这条）
`A 篇章 → B 篇章 → C 篇章 → D 篇章`，每周一个篇章，主线产物会一路被复用。

### 路径 C · 已有基础（直奔企业接入）
`L3 → L4 → L6 → L7 → L9 → L11`，跳过认知预热，重点解决"和飞书 / 表格 / 团队 Skill 怎么打通"。

### 路径 D · "我就是要爽"（半天体验装）
`L0 → L2 → L2.5 → L4.5`：跳过结构化讲法，专挑最有冲击力的"动手感"实践。适合你想先说服一个还在观望的同事。

---

## 4. 学习方式（很重要，请先读一遍）

每一讲都按统一模板：

1. **你将学会**：1–3 条目标。
2. **背景小知识**：≤300 字白话讲清概念。
3. **准备工作**：环境、目录、所需账号。
4. **实战任务**：Step 1…N，每步包含
   - 你输入什么（精确到 prompt 文本）
   - 预期看到什么（产物形态 / 关键截图）
   - 如果出错怎么办（最常见 2–3 种偏差及纠偏 prompt）
5. **自检清单**：能不能解释、能不能在新会话里独立复现。
6. **思考题 & 引子**：自然过渡到下一讲。
7. **交付物**：本地/系统里应当留下哪些文件或资产。

> **重要原则**：你不是在"看教程"，而是在"边做边长出资产"。每一讲结束后，你的本地目录都应该比上一讲多一些真实可用的东西。

---

## 5. 准备工作（先完成这一步再进 L0）

- [ ] 选定一款 Agent 客户端（Codex / Claude Code / Trae / 任一你公司允许的均可）。
- [ ] 已配置好飞书 lark-cli（C 篇章会大量用到，A/B 篇章不强制）。详见 [00-prep/env-setup.md](./00-prep/env-setup.md)。
- [ ] 通读一次最小词表 [00-prep/glossary.md](./00-prep/glossary.md)，对 Agent / Tool / Skill / Context / RAG 这 5 个词建立直觉即可。
- [ ] 在你的工作目录下建一个空文件夹 `pm-agent-lab/`，作为本课程所有产物的根目录。

---

## 6. 文档结构

```
agent-onboarding/
├── README.md                  # 本文件
├── 00-prep/
│   ├── env-setup.md
│   └── glossary.md
├── A-cognition/               # 认知与上手
│   ├── L0-chat-vs-agent.md
│   ├── L1-first-hands-on.md
│   ├── L2-vibe-coding.md
│   └── L2.5-browser-use.md
├── B-productivity/            # 生产力
│   ├── L3-prompt-minimal.md
│   ├── L4-llm-wiki.md
│   ├── L4.5-multimodal.md
│   └── L5-skill-ization.md
├── C-enterprise/              # 企业接入
│   ├── L6-lark-cli.md
│   ├── L7-data-landing.md
│   ├── L8-code-collab.md
│   └── L9-end-to-end-workflow.md
├── D-team/                    # 安全与团队
│   ├── L10-boundary.md
│   ├── L11-team-skill.md
│   └── L12-self-evolution.md
└── templates/
    ├── lesson-template.md     # 每讲的标准模板
    ├── AGENTS.md.example      # 个人使用规范模板
    └── skill-template/        # 一个最小 Skill 骨架
```

---

## 7. 给读者的话

如果你只能记住这本手册的一句话：

> **不要再问"Agent 能做什么"，去问"我每周重复在做什么 → 哪些可以让 Agent 替我做"。**

读完 L12，你应该能在 30 分钟内，把工作里任何一个高频任务变成一个可跑的 Agent Skill。这才是 PM 在 Agent 时代真正的杠杆。

祝你玩得愉快。Now go ship things.
