# Lesson 9 · 多步工作流：让 Agent 跑端到端闭环

> 一句话定位：把 L1–L8 所有积累串成**一句触发 → 全程自动跑**的端到端工作流。这是 PM 个人生产力跃迁的临界点。

---

## 1. 你将学会

- [ ] 我能把多个 Skill / 工具调用 / 人工确认点编排成一个完整工作流
- [ ] 我能在工作流里**精准设置中断点**：哪些步骤全自动、哪些必须人工
- [ ] 我能让工作流**出错时优雅停下**而不是把现场搞乱

---

## 2. 背景小知识

到 L8 你已经有了一堆"积木"：调研、落盘、HTML、Wiki、CLI、表格、MR review、单测……

**工作流就是把积木拼起来跑一次**。它和单个 Skill 的区别：

| 形态 | 长什么样 | 例子 |
|------|----------|------|
| Skill | 一段稳定的、原子的流程 | news-weekly：调研 → 落盘 → 出 dashboard |
| 工作流 | 多个 Skill / 工具串成的链路 | 周一早 9 点：跑 news-weekly → 发飞书 → 同步表格 → 给我一段口播稿 |

> 直觉口诀：**Skill 是关键词命中，工作流是流水线。**
> Skill 关注"做对一件事"，工作流关注"按节奏做对一串事"。

⚠️ 工作流的最大坑是**链路长 → 一处出错全盘乱**。本讲会专门给你"中断 + 续跑"的姿势。

---

## 3. 准备工作

- [ ] 已完成 L5 / L6 / L7（Skill 化 + lark-cli + 数据落点）
- [ ] 工作目录：`pm-agent-lab/workflows/`
- [ ] 一份你**真的会重复跑**的 PM 工作目标。本讲使用主线"周一早晨新闻周报全流程"

> 🎯 **三选一练手主线**
> 本讲示例默认演示「**行业 / 竞品周报**」场景。如果你的日常工作里几乎不做行业调研，可以从下面三个 PM 通用场景里挑一个最贴近你工作的，下面 Step 里的 prompt 都给出三种版本：
>
> | 场景 ID | 适合谁 | 主线产物路径 |
> |---|---|---|
> | 📋 `backlog` 需求池整理 | 几乎所有 PM（覆盖率最高） | `pm-agent-lab/backlog-lab/L9-demo/` |
> | 📝 `meeting` 会议纪要跟进 | 跨团队协作多的 PM | `pm-agent-lab/meeting-lab/L9-demo/` |
> | 📰 `news` 行业 / 竞品周报 | 战略 / 对外汇报型 PM | `pm-agent-lab/news-lab/L9-demo/` |
>
> 每讲只需选 1 个跑透即可。HTML 单课页会根据你在首页选定的场景，自动把对应版本作为默认演示。下面文本版讲义里，**默认展开 `news` 版本，另外两个折叠在每个 Step 末尾**。
>
> 在 L9 里，三个场景对应三条不同的工作流：
> - 📰 `news` → 工作流 `monday-news-brief`，dry_run 数据集 = 上周新闻原文 / RSS 抓取样本
> - 📋 `backlog` → 工作流 `weekly-backlog-review`，dry_run 数据集 = 上周新增需求线索 / 用户反馈摘录
> - 📝 `meeting` → 工作流 `meeting-followup-pipeline`，dry_run 数据集 = 本周会议纪要 .md 文件

---

## 4. 实战任务

我们要做的工作流叫 `monday-news-brief`，一句话触发后自动：

1. 跑 `news-weekly` Skill（本地产出）
2. 按 ROUTING 分发：飞书文档 / 多维表格 / 群消息（双确认）
3. 自动写一段口播稿（用于产品早会）
4. 把本周与上周差异写到 `llm-wiki/memory.md`
5. 给我一份"今日开工指南"（含日程摘要）

---

### Step 1 · 把工作流"画"出来

> 不要直接 prompt → 跑。先让 Agent 帮你**画 plan**，看着画再决定哪些自动、哪些手动。

**🎯 你要做什么**

**⌨️ 你输入什么**

```
我要做一个 monday-news-brief 工作流，目标 / 阶段我口述如下：

[目标] 周一早晨我打开电脑，一句话就能拿到：本周新闻周报飞书文档 + 一段产品早会口播稿 + 今日日程摘要 + 与上周差异。

[已有积木]
- Skill: news-weekly （L5）
- ROUTING.md（L7）
- lark-cli docs / im / sheets / calendar / base
- llm-wiki（L4）

[任务]
帮我画一份工作流 plan，写到 pm-agent-lab/workflows/monday-news-brief/PLAN.md：
- 步骤树：每步编号、做什么、读什么、写什么、调用什么工具
- 中断点：哪些步骤需要人工确认（用 🔴 标）；哪些是只读 / 私有写（用 🟢 标）；哪些产生外发 / 群消息（用 🟡 标）
- 失败兜底：每个 🔴/🟡 步骤都写"如果失败，状态保留在哪、怎么续跑"
- 时间预估：每步预计耗时

不要立刻执行，先给我看 PLAN.md。
```

<details><summary>📋 切换到「需求池整理」场景的 prompt</summary>

```
我要做一个 weekly-backlog-review 工作流，目标 / 阶段我口述如下：

[目标] 周末 / 周一早晨我打开电脑，一句话就能拿到：本周需求池摘要飞书文档 + 一段评审会口播稿 + 待评估高优需求 TOP3 + 与上周拒掉/新增差异。

[已有积木]
- Skill: backlog-weekly （L5/L6 派生）
- ROUTING.md（L7）
- lark-cli docs / im / sheets / calendar / base
- llm-wiki（L4）

[任务]
帮我画一份工作流 plan，写到 pm-agent-lab/workflows/weekly-backlog-review/PLAN.md：
- 步骤树：每步编号、做什么、读什么、写什么、调用什么工具
- 中断点：哪些步骤需要人工确认（用 🔴 标）；哪些是只读 / 私有写（用 🟢 标）；哪些产生外发 / 群消息（用 🟡 标）
- 失败兜底：每个 🔴/🟡 步骤都写"如果失败，状态保留在哪、怎么续跑"
- 时间预估：每步预计耗时

不要立刻执行，先给我看 PLAN.md。
```
</details>

<details><summary>📝 切换到「会议纪要跟进」场景的 prompt</summary>

```
我要做一个 meeting-followup-pipeline 工作流，目标 / 阶段我口述如下：

[目标] 每次例会结束后，一句话就能拿到：本次会议纪要飞书文档 + 拆好的待办（带归属人）+ 写入事项追踪表 + 按归属人 @ 出去的协作群消息 + 关键决策进 Wiki 决策档案。

[已有积木]
- Skill: meeting-followup （L5/L6 派生）
- ROUTING.md（L7）
- lark-cli docs / im / sheets / calendar / base / wiki / contact
- llm-wiki（L4）

[任务]
帮我画一份工作流 plan，写到 pm-agent-lab/workflows/meeting-followup-pipeline/PLAN.md：
- 步骤树：每步编号、做什么、读什么、写什么、调用什么工具
- 中断点：哪些步骤需要人工确认（用 🔴 标）；哪些是只读 / 私有写（用 🟢 标）；哪些产生外发 / 群消息（用 🟡 标）
- 失败兜底：每个 🔴/🟡 步骤都写"如果失败，状态保留在哪、怎么续跑"
- 时间预估：每步预计耗时

不要立刻执行，先给我看 PLAN.md。
```
</details>

**👀 预期看到什么**
- 一份带颜色标记的步骤树
- 你看着 PLAN.md 就能改：哪步不需要确认、哪步需要加确认

**📝 PM 决策时刻**
PM 的核心价值在这一步：**决定哪些环节让 Agent 自由跑，哪些必须人控。**
建议默认规则：
- 🟢 全自动：本地读写、本地 dashboard、wiki 写入
- 🟡 打印后执行：飞书文档创建、多维表格 append
- 🔴 三步双确认：群发、@ 人、跨部门发送

---

### Step 2 · 把工作流写成 WORKFLOW.md（可执行版本）

**🎯 你要做什么**
让 Agent 把 PLAN 升级成一份**可被它自己读着执行**的工作流文件。

**⌨️ 你输入什么**

```
基于 PLAN.md 写 pm-agent-lab/workflows/monday-news-brief/WORKFLOW.md，结构：

[触发]
关键词：monday-news-brief / 周一早安
入参（可选）：keywords（默认 "AI Agent"）, week_id（默认本周 ISO）, dry_run（默认 false）

[行为契约]
- 严格按步骤顺序，跑完一步再跑下一步
- 每步开始前打印：步骤号 + 名称 + 这一步会读/写什么
- 🔴 步骤前必须等我"OK"才执行
- 🟡 步骤先打印命令再执行
- 任何步骤失败：写一行到 STATE.md（步骤号 + 失败原因 + 当前已产出文件），然后停下不要往后跑
- dry_run=true 时所有 🟡/🔴 都只打印不执行

[步骤]
逐步写，每步一个段落（步骤号 / 颜色 / 描述 / 读 / 写 / 工具 / 失败兜底）。
完整覆盖 PLAN.md 的步骤树。

[产物]
- 本地：本周 news 数据 + dashboard
- 飞书：文档 + 表格行
- 群：双确认后的 TL;DR
- wiki/memory.md：新增 3 条本周差异
- 对话内：今日日程摘要 + 早会口播稿

[复用]
明确说明：以后只要我说"跑 monday-news-brief"或"周一早安"，先读本文件再开干。
```

<details><summary>📋 切换到「需求池整理」场景的 prompt</summary>

```
基于 PLAN.md 写 pm-agent-lab/workflows/weekly-backlog-review/WORKFLOW.md，结构：

[触发]
关键词：weekly-backlog-review / 评审周扫描
入参（可选）：since（默认上周一）, until（默认本周日）, dry_run（默认 false）

[行为契约]
- 严格按步骤顺序，跑完一步再跑下一步
- 每步开始前打印：步骤号 + 名称 + 这一步会读/写什么
- 🔴 步骤前必须等我"OK"才执行
- 🟡 步骤先打印命令再执行
- 任何步骤失败：写一行到 STATE.md（步骤号 + 失败原因 + 当前已产出文件），然后停下不要往后跑
- dry_run=true 时所有 🟡/🔴 都只打印不执行；输入数据集 = 上周新增需求线索 / 用户反馈摘录的样本

[步骤]
逐步写，每步一个段落（步骤号 / 颜色 / 描述 / 读 / 写 / 工具 / 失败兜底）。
完整覆盖 PLAN.md 的步骤树。

[产物]
- 本地：本周 backlog 数据 + RICE 排序结果
- 飞书：评审文档 + 需求池多维表格 append
- 群：双确认后的 TOP3 摘要发到产研群
- wiki/memory.md：新增 3 条本周拒绝/新增差异
- 对话内：评审会口播稿 + 高优 TOP3 摘要

[复用]
明确说明：以后只要我说"跑 weekly-backlog-review"或"评审周扫描"，先读本文件再开干。
```
</details>

<details><summary>📝 切换到「会议纪要跟进」场景的 prompt</summary>

```
基于 PLAN.md 写 pm-agent-lab/workflows/meeting-followup-pipeline/WORKFLOW.md，结构：

[触发]
关键词：meeting-followup-pipeline / 会后跟进
入参（可选）：notes_path（必填，会议纪要 .md 路径）, meeting_name（必填）, dry_run（默认 false）

[行为契约]
- 严格按步骤顺序，跑完一步再跑下一步
- 每步开始前打印：步骤号 + 名称 + 这一步会读/写什么
- 🔴 步骤前必须等我"OK"才执行（特别是按归属人 @ 这一步）
- 🟡 步骤先打印命令再执行
- 任何步骤失败：写一行到 STATE.md（步骤号 + 失败原因 + 当前已产出文件），然后停下不要往后跑
- dry_run=true 时所有 🟡/🔴 都只打印不执行；输入数据集 = 本周会议纪要 .md 文件样本

[步骤]
逐步写，每步一个段落（步骤号 / 颜色 / 描述 / 读 / 写 / 工具 / 失败兜底）。
完整覆盖 PLAN.md 的步骤树。

[产物]
- 本地：本次会议拆好的待办 JSON + 决策清单
- 飞书：会议纪要文档 + 事项追踪表 append + Wiki 决策档案新增节点
- 群：双确认后的协作群消息（按归属人 @）
- wiki/memory.md：新增 3 条本次会议关键决策 / 争议点
- 对话内：本次会议 TL;DR + 待与责任人确认的事项清单

[复用]
明确说明：以后只要我说"跑 meeting-followup-pipeline"或"会后跟进"，先读本文件再开干。
```
</details>

---

### Step 3 · 真跑一次（dry_run=true）

> **第一次跑，永远先 dry_run。**

**🎯 你要做什么**

**⌨️ 你输入什么**

```
[新会话]

请读 pm-agent-lab/workflows/monday-news-brief/WORKFLOW.md 并按其执行：
跑 monday-news-brief，keywords=AI Agent，dry_run=true
```

<details><summary>📋 切换到「需求池整理」场景的 prompt</summary>

```
[新会话]

请读 pm-agent-lab/workflows/weekly-backlog-review/WORKFLOW.md 并按其执行：
跑 weekly-backlog-review，dry_run=true
（输入数据集请用 pm-agent-lab/backlog-lab/L9-demo/sample-leads/ 下的样本需求线索）
```
</details>

<details><summary>📝 切换到「会议纪要跟进」场景的 prompt</summary>

```
[新会话]

请读 pm-agent-lab/workflows/meeting-followup-pipeline/WORKFLOW.md 并按其执行：
跑 meeting-followup-pipeline，notes_path=pm-agent-lab/meeting-lab/L9-demo/sample-notes/2026-06-22-sync.md，meeting_name="本周项目同步会"，dry_run=true
```
</details>

**👀 预期看到什么**
- Agent 老实地按步骤"演练"：每步打印它会读啥、写啥、调啥命令
- **完全不动飞书 / 不动数据库**
- 你能在演练中发现：哪些步骤的预期产出不符你期望

**⚠️ 如果出错怎么办**
- 偏差：Agent 跳过了 dry_run，真的写了文件 → 立刻让它回滚 + 写进 me.md：

  ```
  违反 dry_run 契约。请：1) 列出所有违规创建的产物；2) 把它们删除或恢复；3) 把"严格遵守 dry_run"补到 me.md 的工作约束里；下次违反请自报。
  ```

---

### Step 4 · 真跑一次（dry_run=false，第一次实跑）

**🎯 你要做什么**

**⌨️ 你输入什么**

```
跑 monday-news-brief，keywords=AI Agent
```

<details><summary>📋 切换到「需求池整理」场景的 prompt</summary>

```
跑 weekly-backlog-review
```
</details>

<details><summary>📝 切换到「会议纪要跟进」场景的 prompt</summary>

```
跑 meeting-followup-pipeline，notes_path=pm-agent-lab/meeting-lab/L9-demo/notes/2026-06-22-sync.md，meeting_name="本周项目同步会"
```
</details>

**👀 预期看到什么**
- 🟢 步骤一路跑过去
- 🟡 步骤打印命令等你确认
- 🔴 步骤双确认才发出去
- 全程 < 10 分钟，你只在关键点点几次"OK"

**📝 这一刻的体验**
你周一早 9:00 喝着咖啡，整套周报已经发出去、表格已经更新、wiki 已经更新、口播稿已经在你眼前——**这是 PM 在 Agent 时代的标准开工姿势**。

---

### Step 5 · 给工作流加一个"状态文件" STATE.md

> 长链路的工作流必须有"现场"，否则失败一次就乱套。

**🎯 你要做什么**
让 Agent 维护一份 `STATE.md`，每跑一次都更新。

**⌨️ 你输入什么**

```
更新 WORKFLOW.md 行为契约：

工作流每次开始时，先在 pm-agent-lab/workflows/monday-news-brief/STATE.md 写一段：
- run_id（带本次开始时间，分钟级，例如 202606191205）
- 每步状态（pending / running / done / failed / skipped）
- 关键产出路径
- 用户确认点的原话（"OK / 改 X / 跳过"）

完成后 STATE.md 末尾追加 RESULT 段：
- 本次产出文件清单
- 本次失败/跳过的步骤
- 下次需要改进的地方（≤ 3 条）

下一次跑时，新建一段，不要覆盖历史。STATE.md 是可追溯的运行日志。
```

<details><summary>📋 切换到「需求池整理」场景的 prompt</summary>

```
更新 WORKFLOW.md 行为契约：

工作流每次开始时，先在 pm-agent-lab/workflows/weekly-backlog-review/STATE.md 写一段：
- run_id（带本次开始时间，分钟级，例如 202606191205）
- 每步状态（pending / running / done / failed / skipped）
- 关键产出路径（含本次新增/拒绝/合并的需求条数）
- 用户确认点的原话（"OK / 改 X / 跳过"）

完成后 STATE.md 末尾追加 RESULT 段：
- 本次产出文件清单（评审文档 / 表格 append 行数 / 群消息 message_id）
- 本次失败/跳过的步骤
- 下次需要改进的地方（≤ 3 条）

下一次跑时，新建一段，不要覆盖历史。STATE.md 是可追溯的运行日志。
```
</details>

<details><summary>📝 切换到「会议纪要跟进」场景的 prompt</summary>

```
更新 WORKFLOW.md 行为契约：

工作流每次开始时，先在 pm-agent-lab/workflows/meeting-followup-pipeline/STATE.md 写一段：
- run_id（带本次开始时间，分钟级，例如 202606191205）
- meeting_name + notes_path（本次输入）
- 每步状态（pending / running / done / failed / skipped）
- 关键产出路径（含本次拆出待办条数 / @ 到的归属人列表 / Wiki 决策档案节点）
- 用户确认点的原话（"OK / 改 X / 跳过"）

完成后 STATE.md 末尾追加 RESULT 段：
- 本次产出文件清单（纪要文档 / 追踪表 append 行数 / 群消息 message_id / Wiki 节点链接）
- 本次失败/跳过的步骤（特别是哪些待办因归属人未识别被跳过）
- 下次需要改进的地方（≤ 3 条）

下一次跑时，新建一段，不要覆盖历史。STATE.md 是可追溯的运行日志。
```
</details>

> 这一份 `STATE.md` 在你出问题时是**救命稻草**：你能精确知道"上次跑到哪一步、为什么停"。

---

### Step 6 · 把工作流串到日历 / 提醒

**🎯 你要做什么**
让 Agent 帮你设个固定时间触发自己（轻量版自动化）。

**⌨️ 你输入什么**

```
我希望每周一早 9:00 我打开电脑就能想到跑这个工作流。请：

1) 用 lark-cli calendar +create 创建一个每周一 09:00 的循环日程：
   - 标题：[Agent] 周一早安 · 跑 monday-news-brief
   - 描述：贴一段我可以直接复制的触发 prompt
   - 提前 5 分钟提醒
2) 创建前先打印命令字符串等我确认（这是 🟡 操作）

我之后看到提醒就手动开会话跑——不要直接做"全自动定时跑"，因为里面有 🔴 步骤需要我在场。
```

<details><summary>📋 切换到「需求池整理」场景的 prompt</summary>

```
我希望每周一早 9:00（评审会前一天）我打开电脑就能想到跑这个工作流。请：

1) 用 lark-cli calendar +create 创建一个每周一 09:00 的循环日程：
   - 标题：[Agent] 评审周扫描 · 跑 weekly-backlog-review
   - 描述：贴一段我可以直接复制的触发 prompt
   - 提前 5 分钟提醒
2) 创建前先打印命令字符串等我确认（这是 🟡 操作）

我之后看到提醒就手动开会话跑——不要直接做"全自动定时跑"，因为里面有 🔴 步骤（发产研群）需要我在场。
```
</details>

<details><summary>📝 切换到「会议纪要跟进」场景的 prompt</summary>

```
我希望每次例会结束后能立刻被提醒跑这个工作流（与会议日程绑定）。请：

1) 用 lark-cli calendar +create 创建一个跟随会议的提醒日程（或为常态例会建一个会后 5 分钟的循环日程，例如每周二 10:30）：
   - 标题：[Agent] 会后跟进 · 跑 meeting-followup-pipeline
   - 描述：贴一段我可以直接复制的触发 prompt（含 notes_path 占位）
   - 提前 0 分钟提醒（会议刚结束就提示）
2) 创建前先打印命令字符串等我确认（这是 🟡 操作）

我之后看到提醒就手动开会话跑——不要直接做"全自动定时跑"，因为里面有 🔴 步骤（按归属人 @ 群发）需要我在场确认。
```
</details>

> 这是 PM 视角下的"伪自动化"：**节奏由日历提示，触发由人，执行由 Agent**——足够轻量、足够安全。

---

## 5. 自检清单

- [ ] 我有 `pm-agent-lab/workflows/monday-news-brief/PLAN.md` + `WORKFLOW.md`
- [ ] 我用 dry_run 跑通过一次，再用真实模式跑通过 ≥ 1 次
- [ ] 我的 `STATE.md` 里有 ≥ 1 次 RESULT 段
- [ ] 我能 30 秒讲清"🟢/🟡/🔴 三档"在我工作流里的分布
- [ ] 我已用 calendar 设了一个周一固定提醒

---

## 6. 思考题 & 下一讲引子

**思考题**
- 哪些步骤其实可以升档到"全自动"？哪些一定要保留🔴？这是你团队工作流共识的雏形。
- 如果某天你休假、由同事代跑这条工作流，他需要看 `WORKFLOW.md` 之外的什么文件？

**下一讲引子**
你已经把 Agent 用得很顺手了。但**用得越深，红线越要清晰**。L10 我们专讲"边界与安全"——什么数据不能喂、什么操作必须 diff、什么场景永远人工兜底。

---

## 7. 本讲交付物

按你选定的场景，下面三选一即可（`PLAN.md / WORKFLOW.md / STATE.md` 三件套结构通用，差别在工作流名与日历提醒节奏）：

```
# 📰 news 场景
pm-agent-lab/
└── workflows/
    └── monday-news-brief/
        ├── PLAN.md
        ├── WORKFLOW.md
        └── STATE.md
飞书：
└── 日历：每周一 09:00 [Agent] 周一早安 · 跑 monday-news-brief

# 📋 backlog 场景
pm-agent-lab/
└── workflows/
    └── weekly-backlog-review/
        ├── PLAN.md
        ├── WORKFLOW.md
        └── STATE.md
飞书：
└── 日历：每周一 09:00 [Agent] 评审周扫描 · 跑 weekly-backlog-review

# 📝 meeting 场景
pm-agent-lab/
└── workflows/
    └── meeting-followup-pipeline/
        ├── PLAN.md
        ├── WORKFLOW.md
        └── STATE.md
飞书：
└── 日历：例会后 0 分钟提醒 [Agent] 会后跟进 · 跑 meeting-followup-pipeline
```

---

## 8. 副线练习（可选）

本讲主线已可在三个场景切换，副线建议挑战更进阶的玩法：

- **friday-wrap-up**：周五下午自动跑"本周复盘 + 下周日程草稿 + OKR 进度同步"
- **monthly-review**：每月最后一个工作日跑"月度数据总结 + wiki 体检 + Skill BACKLOG 复盘"
- **ad-hoc-deepdive**：当老板甩来一个临时调研需求时一次性跑通"调研 → 整理 → 文档 → 同步"

每条都按"PLAN → WORKFLOW → dry_run → 真跑 → STATE 维护"五步走。

---

## 9. 给 PM 的小结：工作流的"三色 + 三状态"

**三色**（已贯穿本讲）
- 🟢 自动：本地、只读、私有写
- 🟡 半自动：打印命令再执行
- 🔴 全人工：群发 / 推送 / 跨部门

**三状态**（必须可追溯）
- 起始时刻（run_id）
- 中间快照（每步 pending/running/done/failed）
- 终态总结（RESULT）

把这套机制内化，**你就能让任何一个 PM 长链路工作变成"开工 5 分钟"**。
