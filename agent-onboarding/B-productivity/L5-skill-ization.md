# Lesson 5 · Skill 化：把"做一次"沉淀为"团队资产"

> 一句话定位：把 L1–L4.5 一路积累的重复流程**封装成一段可复用的 Skill**——下次只要一句话触发，全流程自动跑。

---

## 1. 你将学会

- [ ] 我能用 **Skill 三要素**（触发 / 流程 / 产物）写出一个 Agent 能稳定复现的 Skill
- [ ] 我能在新会话里仅用一句触发词，跑完整套"行业新闻周报"流程
- [ ] 我能识别哪些任务**值得**Skill 化、哪些不值得

---

## 2. 背景小知识

到 L4.5，你做过的每个流程其实都"长成了一份 SOP"——L1 的 HOWTO、L2 的 README、L4.5 的 VISION_PROMPTS……

**Skill 就是把它们升级一档**：从"我自己看的笔记"升级为"Agent 能直接执行的工作流"。

Skill 三要素：

```
[触发]   什么时候启动这个 Skill（关键词、文件、时间）
[流程]   分几步、每步干什么、产物路径
[产物]   完成后本地/系统里应该多出什么、形态如何
```

> 直觉口诀：**Skill = 给 Agent 的 SOP，让它"自己看说明书做事"。**

⚠️ Skill 化的判断红线：**做过 ≥ 3 次、流程稳定、产物形态明确**——满足这三条再 Skill 化。一次性事情不要 Skill 化，否则维护成本反而高。

---

## 3. 准备工作

- [ ] 已完成 L1（有 `news.json` + schema）、L2（dashboard）、L3（4 要素）、L4（wiki）
- [ ] 工作目录：`pm-agent-lab/skills/news-weekly/`
- [ ] 心理建设：第一版 Skill 写**够用就行**，能跑通是核心，优雅是 V2 的事

> 🎯 **三选一练手主线**
> 本讲示例默认演示「**行业 / 竞品周报**」场景，封装成 Skill `news-weekly`。如果你的日常工作里几乎不做行业调研，可以从下面三个 PM 通用场景里挑一个最贴近你工作的，下面 Step 里的 prompt 都给出三种版本：
>
> | 场景 ID | 适合谁 | Skill 名 | 主线产物路径 |
> |---|---|---|---|
> | 📋 `backlog` 需求池整理 | 几乎所有 PM（覆盖率最高） | `backlog-weekly` | `pm-agent-lab/skills/backlog-weekly/` |
> | 📝 `meeting` 会议纪要跟进 | 跨团队协作多的 PM | `meeting-followup` | `pm-agent-lab/skills/meeting-followup/` |
> | 📰 `news` 行业 / 竞品周报 | 战略 / 对外汇报型 PM | `news-weekly` | `pm-agent-lab/skills/news-weekly/` |
>
> 每讲只需选 1 个跑透即可。HTML 单课页会根据你在首页选定的场景，自动把对应版本作为默认演示。下面文本版讲义里，**默认展开 `news` 版本，另外两个折叠在每个 Step 末尾**。

---

## 4. 实战任务

我们把"行业新闻周报"主线封装成 Skill `news-weekly`，目标：

> 在新会话里说一句"跑一下 news-weekly，关键词=AI Agent"，Agent 自动完成：调研 → 落盘 → 自检 → dashboard 更新 → 给我汇报。

---

### Step 1 · 先盘点你已有的"原料"

**🎯 你要做什么**
让 Agent 把 L1–L4.5 你产出的相关文件**全部找出来**，作为 Skill 的素材。

**⌨️ 你输入什么**

```
扫描 pm-agent-lab/news-lab/ 下所有文件，告诉我：
1) 每个文件的角色（schema / 数据 / 模板 / HOWTO / dashboard / 其它）
2) 哪些是"每周都会变的"，哪些是"长期不变的"
3) 如果我要把这套流程封装成一个 Skill，你建议哪些文件作为"模板"复用、哪些作为"产物"每周新生

不要动文件，只做盘点报告。
```

<details><summary>📋 切换到「需求池整理」场景的 prompt</summary>

```
扫描 pm-agent-lab/backlog-lab/ 下所有文件，告诉我：
1) 每个文件的角色（schema / 来源汇总 / 模板 / HOWTO / 摘要 / 其它）
2) 哪些是"每周都会变的"（新增需求线索、本周摘要），哪些是"长期不变的"（优先级口径、字段定义）
3) 如果我要把这套流程封装成一个 Skill `backlog-weekly`，你建议哪些文件作为"模板"复用、哪些作为"产物"每周新生

不要动文件，只做盘点报告。
```
</details>

<details><summary>📝 切换到「会议纪要跟进」场景的 prompt</summary>

```
扫描 pm-agent-lab/meeting-lab/ 下所有文件，告诉我：
1) 每个文件的角色（schema / 纪要原文 / 模板 / HOWTO / 跟进清单 / 其它）
2) 哪些是"每周都会变的"（本周纪要、待办清单），哪些是"长期不变的"（决策/待办/风险三栏模板、字段定义）
3) 如果我要把这套流程封装成一个 Skill `meeting-followup`，你建议哪些文件作为"模板"复用、哪些作为"产物"每周新生

不要动文件，只做盘点报告。
```
</details>

**👀 预期看到什么**
- 一份分类清单：
  - 长期不变：`schema/news.schema.md`、`dashboard.html` 模板
  - 每周新生：`data/2026-W25/news.json`、`HOWTO.md`
- 你立刻能看清"Skill 应该装什么、应该指向什么"

---

### Step 2 · 写 Skill 的"主文件" SKILL.md

**🎯 你要做什么**
让 Agent 按 Skill 三要素结构写 `SKILL.md`。

**⌨️ 你输入什么**

```
帮我写 pm-agent-lab/skills/news-weekly/SKILL.md，按三段结构：

[触发]
- 关键词：news-weekly / 新闻周报 / 跑一下周报
- 输入参数：
  - keywords（必填，行业关键词，如"AI Agent"）
  - days（可选，默认 7，调研时间窗口）
  - week_id（可选，默认本周 ISO 周编号，如 2026-W25）

[流程]
按下面步骤顺序执行，每步完成后简短汇报：
1. 读 pm-agent-lab/llm-wiki/me.md 和 product.md 取背景
2. 读 pm-agent-lab/news-lab/schema/news.schema.md 作为字段契约
3. 联网调研 keywords 在过去 days 天内的新闻 8–12 条
4. 严格按 schema 写入 pm-agent-lab/news-lab/data/<week_id>/news.json
5. 同步生成 news.md（同内容 markdown 表格视图）
6. 跑一遍数据自检（标签统一性 / 重复 / 时间范围 / 必填字段缺失）
7. 复用模板更新 dashboard.html（不要新写 HTML，沿用现有模板）
8. 给我一份本周汇报：抓 N 条 / 丢弃 X 条 / 与上周差异 TOP 3 / 我建议你看的 3 条

[产物]
- pm-agent-lab/news-lab/data/<week_id>/news.json
- pm-agent-lab/news-lab/data/<week_id>/news.md
- pm-agent-lab/news-lab/data/<week_id>/dashboard.html
- 对话里的本周汇报

[约束]
- 不编造链接；找不到链接的条目直接丢弃，并在汇报里说丢了几条
- 调研前先打印你打算搜的关键词清单，让我来确认是否合理
- 数据自检发现问题不要自己改，先汇报让我决定

写完后告诉我我下次怎么触发它。
```

<details><summary>📋 切换到「需求池整理」场景的 prompt</summary>

```
帮我写 pm-agent-lab/skills/backlog-weekly/SKILL.md，按三段结构：

[触发]
- 关键词：backlog-weekly / 需求池周报 / 跑一下需求池
- 输入参数：
  - sources（可选，默认扫描 pm-agent-lab/backlog-lab/inbox/，包括 IM/邮件/访谈）
  - days（可选，默认 7，回看时间窗口）
  - week_id（可选，默认本周 ISO 周编号，如 2026-W25）

[流程]
按下面步骤顺序执行，每步完成后简短汇报：
1. 读 pm-agent-lab/llm-wiki/me.md、product.md、backlog-priorities.md 取背景与口径
2. 读 pm-agent-lab/backlog-lab/schema/backlog.schema.md 作为字段契约
3. 扫描 sources 下过去 days 天的新增需求线索 8–15 条
4. 严格按 schema 写入 pm-agent-lab/backlog-lab/data/<week_id>/backlog.json
5. 同步生成 backlog.md（按优先级分组的 markdown 视图）
6. 跑一遍数据自检（去重 / 提需人缺失 / 优先级口径冲突 / 描述模糊）
7. 复用模板更新 backlog-dashboard.html（不要新写 HTML）
8. 给我一份本周汇报：新增 N 条 / 合并 X 条 / 高优 TOP 3 / 我建议你立即决策的 3 条

[产物]
- pm-agent-lab/backlog-lab/data/<week_id>/backlog.json
- pm-agent-lab/backlog-lab/data/<week_id>/backlog.md
- pm-agent-lab/backlog-lab/data/<week_id>/backlog-dashboard.html
- 对话里的本周汇报

[约束]
- 不编造提需人；提需人不明的条目标记 "unknown" 并单列汇报
- 扫描前先打印你打算读的来源目录清单，让我来确认是否合理
- 数据自检发现优先级冲突时不要自己拍板，先汇报让我决定

写完后告诉我我下次怎么触发它。
```
</details>

<details><summary>📝 切换到「会议纪要跟进」场景的 prompt</summary>

```
帮我写 pm-agent-lab/skills/meeting-followup/SKILL.md，按三段结构：

[触发]
- 关键词：meeting-followup / 会议跟进 / 跑一下会议待办
- 输入参数：
  - meeting_dir（可选，默认 pm-agent-lab/meeting-lab/notes/，扫描所有会议纪要）
  - days（可选，默认 7，回看时间窗口）
  - week_id（可选，默认本周 ISO 周编号，如 2026-W25）

[流程]
按下面步骤顺序执行，每步完成后简短汇报：
1. 读 pm-agent-lab/llm-wiki/me.md、product.md、meeting-decisions.md 取背景与历史决策
2. 读 pm-agent-lab/meeting-lab/schema/followup.schema.md 作为字段契约
3. 扫描 meeting_dir 下过去 days 天的会议纪要，提取 8–15 条决策/待办/风险
4. 严格按 schema 写入 pm-agent-lab/meeting-lab/data/<week_id>/followup.json
5. 同步生成 followup.md（按"决策 / 待办 / 风险"三栏的 markdown 视图）
6. 跑一遍数据自检（归属人缺失 / 截止日缺失 / 与上周已闭环项重复）
7. 复用模板更新 followup-dashboard.html（不要新写 HTML）
8. 给我一份本周汇报：新增 N 条 / 闭环 X 条 / 逾期 Y 条 / 我建议你今天就跟进的 3 条

[产物]
- pm-agent-lab/meeting-lab/data/<week_id>/followup.json
- pm-agent-lab/meeting-lab/data/<week_id>/followup.md
- pm-agent-lab/meeting-lab/data/<week_id>/followup-dashboard.html
- 对话里的本周汇报

[约束]
- 不编造归属人；纪要里没写就标 "待指派" 并在汇报里单列
- 扫描前先打印你打算读的纪要文件清单，让我来确认是否合理
- 数据自检发现"和已闭环项冲突"时不要自己合并，先汇报让我决定

写完后告诉我我下次怎么触发它。
```
</details>

**👀 预期看到什么**
- 一份结构清晰的 `SKILL.md`
- Agent 末尾会告诉你触发方式："以后说'跑一下 news-weekly，关键词=X'即可"

---

### Step 3 · 给 Skill 配一个"使用说明" README

**🎯 你要做什么**
让团队其他人也能看懂这个 Skill。

**⌨️ 你输入什么**

```
帮我写 pm-agent-lab/skills/news-weekly/README.md：
1) 这个 Skill 是干嘛的（2 句话）
2) 触发方式（带 1 个最简示例 + 1 个完整参数示例）
3) 产物长什么样（贴一张产物目录树）
4) 失败时怎么办（最常见 3 种偏差及自检 prompt）
5) 何时不该用这个 Skill（避免被滥用：如一次性调研、跨季度对比等场景）

不要写"未来可能扩展"——只写当前能用的。
```

<details><summary>📋 切换到「需求池整理」场景的 prompt</summary>

```
帮我写 pm-agent-lab/skills/backlog-weekly/README.md：
1) 这个 Skill 是干嘛的（2 句话）
2) 触发方式（带 1 个最简示例 + 1 个完整参数示例：含 sources 与 days）
3) 产物长什么样（贴一张产物目录树）
4) 失败时怎么办（最常见 3 种偏差及自检 prompt——例如来源漏扫、提需人识别错、优先级口径不一致）
5) 何时不该用这个 Skill（避免被滥用：如单条紧急需求评估、跨季度优先级重排等场景）

不要写"未来可能扩展"——只写当前能用的。
```
</details>

<details><summary>📝 切换到「会议纪要跟进」场景的 prompt</summary>

```
帮我写 pm-agent-lab/skills/meeting-followup/README.md：
1) 这个 Skill 是干嘛的（2 句话）
2) 触发方式（带 1 个最简示例 + 1 个完整参数示例：含 meeting_dir 与 days）
3) 产物长什么样（贴一张产物目录树）
4) 失败时怎么办（最常见 3 种偏差及自检 prompt——例如归属人识别错、截止日漏抓、决策/待办分类混乱）
5) 何时不该用这个 Skill（避免被滥用：如单次会议的实时纪要、季度复盘等场景）

不要写"未来可能扩展"——只写当前能用的。
```
</details>

---

### Step 4 · 在新会话里"只用一句话"验证 Skill 可复现

> 这一步是 Skill 化是否成功的硬指标——**新会话能不能一句话跑通**。

**🎯 你要做什么**

打开一个**全新会话**（没有任何 L1–L4.5 上下文）。

**⌨️ 你输入什么**

```
请先读 pm-agent-lab/skills/news-weekly/SKILL.md 并按其执行：
跑一下 news-weekly，keywords=AI Agent
```

<details><summary>📋 切换到「需求池整理」场景的 prompt</summary>

```
请先读 pm-agent-lab/skills/backlog-weekly/SKILL.md 并按其执行：
跑一下 backlog-weekly
```
</details>

<details><summary>📝 切换到「会议纪要跟进」场景的 prompt</summary>

```
请先读 pm-agent-lab/skills/meeting-followup/SKILL.md 并按其执行：
跑一下 meeting-followup
```
</details>

**👀 预期看到什么**
- Agent 主动读 `SKILL.md` → 读 `wiki` → 读 `schema` → 打印关键词清单等你确认 → 调研 → 落盘 → 自检 → 更新 dashboard → 汇报
- **整个过程你只输入了上面那一段话**

**⚠️ 如果失败**
- 偏差 A：Agent 没读 SKILL.md，直接开始抓 → 你的 SKILL.md 在写法上不够"指令式"。修正：在 SKILL.md 开头加一句"任何人（包括你自己将来的会话）调用本 Skill 时，第一件事是逐字读完本文件再开始动手"。
- 偏差 B：Agent 跑到一半跑偏 → 看 `SKILL.md` 流程描述里哪一步留了歧义，把它改写得更精确。

> 这就是 Skill 化的本质：**反复用、反复改 SKILL.md**，直到任何会话都能稳定复现。

---

### Step 5 · 把 Skill 接入 wiki，让 Agent 自动知道它的存在

**🎯 你要做什么**

```
在 pm-agent-lab/llm-wiki/README.md 末尾追加一段"已注册 Skill"清单，第一条就是：

- news-weekly：每周行业新闻调研 + dashboard 更新。位置：pm-agent-lab/skills/news-weekly/SKILL.md。触发：当我说"跑一下 news-weekly"或"出本周新闻周报"时调用。

并在使用契约里加一条：当我提到的任务命中"已注册 Skill"清单的任一描述时，主动建议我用对应 Skill，而不是从零开始。
```

<details><summary>📋 切换到「需求池整理」场景的 prompt</summary>

```
在 pm-agent-lab/llm-wiki/README.md 末尾追加一段"已注册 Skill"清单，第一条就是：

- backlog-weekly：每周需求池盘点 + 摘要。位置：pm-agent-lab/skills/backlog-weekly/SKILL.md。触发：当我说"跑一下 backlog-weekly"或"出本周需求池摘要"时调用。

并在使用契约里加一条：当我提到的任务命中"已注册 Skill"清单的任一描述时，主动建议我用对应 Skill，而不是从零开始。
```
</details>

<details><summary>📝 切换到「会议纪要跟进」场景的 prompt</summary>

```
在 pm-agent-lab/llm-wiki/README.md 末尾追加一段"已注册 Skill"清单，第一条就是：

- meeting-followup：每周会议纪要扫描 + 决策/待办/风险整理。位置：pm-agent-lab/skills/meeting-followup/SKILL.md。触发：当我说"跑一下 meeting-followup"或"汇总本周会议待办"时调用。

并在使用契约里加一条：当我提到的任务命中"已注册 Skill"清单的任一描述时，主动建议我用对应 Skill，而不是从零开始。
```
</details>

> 这一步把 wiki 和 Skill 串起来。从此 Agent 会**主动提醒你**："你这件事其实有 Skill 可以用。"

---

### Step 6 · 起一个"Skill 候选清单"

**🎯 你要做什么**
盘点你工作里**还有哪些可以 Skill 化**。

**⌨️ 你输入什么**

```
帮我建 pm-agent-lab/skills/_BACKLOG.md，按下面表头列我应该考虑 Skill 化的候选任务：

| 候选 Skill | 高频度（每周？月？季？） | 流程是否稳定 | 产物是否明确 | 优先级 |

先空着让我自己填。给我一个填表示例，再附 5 条 PM 常见候选作为参考。
```

<details><summary>📋 切换到「需求池整理」场景的 prompt</summary>

```
帮我建 pm-agent-lab/skills/_BACKLOG.md，按下面表头列我应该考虑 Skill 化的候选任务（已经有 backlog-weekly 在跑，列其它候选）：

| 候选 Skill | 高频度（每周？月？季？） | 流程是否稳定 | 产物是否明确 | 优先级 |

先空着让我自己填。给我一个填表示例，再附 5 条围绕"需求池治理"主题的常见候选作为参考（如：单条需求评估、季度优先级重排、需求闭环回检、跨产品线需求合并、需求溯源校对等）。
```
</details>

<details><summary>📝 切换到「会议纪要跟进」场景的 prompt</summary>

```
帮我建 pm-agent-lab/skills/_BACKLOG.md，按下面表头列我应该考虑 Skill 化的候选任务（已经有 meeting-followup 在跑，列其它候选）：

| 候选 Skill | 高频度（每周？月？季？） | 流程是否稳定 | 产物是否明确 | 优先级 |

先空着让我自己填。给我一个填表示例，再附 5 条围绕"会议跟进"主题的常见候选作为参考（如：会前材料预读、会中实时纪要、跨部门同步邮件起草、季度复盘会议总览、决策逾期告警等）。
```
</details>

> Skill 化的关键不是会写一个，而是有意识地**排队**——下次再做类似事情，先翻 BACKLOG，决定要不要立刻封装。

---

## 5. 自检清单

- [ ] 我有 `pm-agent-lab/skills/news-weekly/SKILL.md` + `README.md`
- [ ] 我在新会话里只用一句话就跑通了一次完整流程
- [ ] 我的 wiki README 已注册了这个 Skill
- [ ] 我有一份 `_BACKLOG.md`，候选 Skill 至少 ≥ 3 条
- [ ] 我能用 30 秒讲清楚"什么任务该 Skill 化、什么不该"

---

## 6. 思考题 & 下一讲引子

**思考题**
- 你的 SKILL.md 写到第几版才稳定？哪一句改完最关键？这个经验值得写进 BACKLOG 顶部。
- 如果同事 A 和你用一份 SKILL.md，是否能跑出**一致**的产物？不一致的话差在哪？

**下一讲引子**
本讲所有产物都还在你本地。下一讲我们打开**飞书 lark-cli**，让 Agent 把 Skill 的产物直接发到云文档 / 多维表格 / 群聊——开始把 Agent 接入企业系统。

---

## 7. 本讲交付物

按你选定的场景，下面三选一即可（`_BACKLOG.md` 三场景共享，每个场景产出 1 个 Skill 目录）：

```
pm-agent-lab/
└── skills/
    ├── _BACKLOG.md                # 三场景共享：Skill 候选清单
    ├── news-weekly/               # 📰 news 场景
    │   ├── SKILL.md
    │   └── README.md
    ├── backlog-weekly/             # 📋 backlog 场景
    │   ├── SKILL.md
    │   └── README.md
    └── meeting-followup/           # 📝 meeting 场景
        ├── SKILL.md
        └── README.md
```

> 选定的那个场景，对应一个 Skill 目录就够；另外两个目录是其它学员的演示。等你跑透一档之后，再回来补另一个场景的 Skill 是非常自然的事。

---

## 8. 副线练习（可选）

本讲主线已可在三个场景切换，副线建议挑战更进阶的玩法。把你副线做过的某个流程也封装成 Skill：

- `competitor-watch`：竞品动态监控（基于 L1 副线）
- `feedback-cluster`：用户反馈聚类（多渠道抓 → 聚类 → 出洞察）
- `design-diff`：设计稿对比（基于 L4.5 Step 2）
- `vision-doc-audit`：每月对一组截图做巡检报告

每个新 Skill 都按"SKILL.md + README.md + 注册到 wiki"三件套来做。

---

## 9. 给 PM 的小结：Skill 化的"三档止步线"

| 档位 | 长什么样 | 何时停 |
|------|----------|--------|
| 个人 Skill | 你一个人用、你电脑里跑 | 本讲 = 一档 |
| 团队 Skill | 同事也能用、有 README | L11 |
| 平台级 Skill | 接入公司平台、有 owner / 版本 / 监控 | 通常交研发 |

**一档够用别上二档；二档够用别上三档。** Skill 化的最大坑是过度工程。
