# Lesson 6 · Agent + 企业 CLI（飞书 lark-cli）

> 一句话定位：CLI 是 Agent 的"手脚延伸"——让你的 Agent 真正接入飞书全家桶（文档 / 表格 / 群聊 / 日历 / 知识库 / 多维表格）。

---

## 1. 你将学会

- [ ] 我能让 Agent 通过 lark-cli **写文档、发消息、查日程、读多维表格**
- [ ] 我能区分"什么走 CLI"、"什么走浏览器"、"什么留在本地"
- [ ] 我能让 Agent 在**敏感操作前自动停下**等我确认

---

## 2. 背景小知识

到 L5 你的产物全部在本地。但 PM 真实工作 80% 都发生在飞书：文档要发出去、群里要同步、日程要查、表格要更新。

**lark-cli = 飞书的官方命令行工具**，把飞书 API 包成命令。Agent 调它就跟调 `ls`/`cat` 一样自然。

> 直觉口诀（来自 L2.5 三问）：
> **有 API（CLI）就走 CLI；没 CLI 走浏览器；都没有才本地手动。**

CLI 比浏览器好在：
- 速度快得多
- 可以全自动跑（不用人在环路登录）
- 错误返回清晰、易调试
- 不会"误点按钮"

⚠️ 但威力也更大：CLI 一行命令能发 100 条群消息。L10 会专讲安全清单。

---

## 3. 准备工作

- [ ] 已完成 [00-prep/env-setup.md](../00-prep/env-setup.md) 中的 lark-cli 配置（`lark-cli config init` + `lark-cli auth login`）
- [ ] 验证 lark-cli 可用：随便跑一个只读命令（如查今日日程）能成功
- [ ] 工作目录：`pm-agent-lab/lark-lab/`

> 🎯 **三选一练手主线**
> 本讲示例默认演示「**行业 / 竞品周报**」场景。如果你的日常工作里几乎不做行业调研，可以从下面三个 PM 通用场景里挑一个最贴近你工作的，下面 Step 里的 prompt 都给出三种版本：
>
> | 场景 ID | 适合谁 | 主线产物路径 |
> |---|---|---|
> | 📋 `backlog` 需求池整理 | 几乎所有 PM（覆盖率最高） | `pm-agent-lab/backlog-lab/L6-demo/` |
> | 📝 `meeting` 会议纪要跟进 | 跨团队协作多的 PM | `pm-agent-lab/meeting-lab/L6-demo/` |
> | 📰 `news` 行业 / 竞品周报 | 战略 / 对外汇报型 PM | `pm-agent-lab/news-lab/L6-demo/` |
>
> 每讲只需选 1 个跑透即可。HTML 单课页会根据你在首页选定的场景，自动把对应版本作为默认演示。下面文本版讲义里，**默认展开 `news` 版本，另外两个折叠在每个 Step 末尾**。

---

## 4. 实战任务

我们把 L5 跑出来的"周新闻周报"产物，**真的送到飞书**——经过 4 个递进的 CLI 场景。

---

### Step 1 · 让 Agent 先"看清"它有哪些 lark-cli 能力

> 不要一上来就喊它发消息。先让它**告诉你**它能做什么。

**🎯 你要做什么**

**⌨️ 你输入什么**

```
我会大量使用 lark-cli。请：
1) 列出 lark-cli 当前可用的主要子命令组（im / docs / sheets / calendar / base / wiki / contact / mail 等）
2) 每组用 1 句话说明能做什么
3) 列出 3 个本周我最可能用到的命令模板（仅命令字符串，不要执行）
4) 列出 3 个我**不应该让你独立执行**的命令（涉及群发 / 删除 / 推送的）

写到 pm-agent-lab/lark-lab/CLI_INVENTORY.md。
```

<details><summary>📋 切换到「需求池整理」场景的 prompt</summary>

```
我会大量使用 lark-cli 来做需求池整理。请：
1) 列出 lark-cli 当前可用的主要子命令组（im / docs / sheets / calendar / base / wiki / contact / mail 等）
2) 每组用 1 句话说明在"需求池整理"场景下能做什么（例如 base 用于多维表格做需求看板）
3) 列出 3 个本周我最可能用到的命令模板（仅命令字符串，不要执行）
4) 列出 3 个我**不应该让你独立执行**的命令（涉及群发到产研群 / 删除需求行 / 推送的）

写到 pm-agent-lab/lark-lab/CLI_INVENTORY.md。
```
</details>

<details><summary>📝 切换到「会议纪要跟进」场景的 prompt</summary>

```
我会大量使用 lark-cli 来做会议纪要跟进。请：
1) 列出 lark-cli 当前可用的主要子命令组（im / docs / sheets / calendar / base / wiki / contact / mail 等）
2) 每组用 1 句话说明在"会议纪要跟进"场景下能做什么（例如 contact 用于查归属人 open_id 以便 @ 出去）
3) 列出 3 个本周我最可能用到的命令模板（仅命令字符串，不要执行）
4) 列出 3 个我**不应该让你独立执行**的命令（涉及 @ 责任人 / 跨部门转发 / 删除待办的）

写到 pm-agent-lab/lark-lab/CLI_INVENTORY.md。
```
</details>

**👀 预期看到什么**
- 一份能看懂的"飞书 CLI 全家桶速查"
- Agent 主动标出"这些命令我执行前要找你确认"

---

### Step 2 · 自动生成本周新闻飞书文档

**🎯 你要做什么**
让 Agent 把 L5 的本周 `news.md` 发布成飞书云文档。

**⌨️ 你输入什么**

```
基于 pm-agent-lab/news-lab/data/<本周 week_id>/news.md，在飞书"我的空间"下创建一篇云文档：

要求：
- 标题：[新闻周报] AI Agent · 2026-W25
- 内容：news.md 全部，外加顶部一段 ≤ 100 字的 TL;DR 总结
- 创建后告诉我文档链接
- 不要发到任何群里——我自己来决定怎么转发
- 在执行 docs +create 之前，先把命令字符串完整打印出来让我确认一次

完成后把链接 append 到 pm-agent-lab/news-lab/data/<本周 week_id>/HOWTO.md。
```

<details><summary>📋 切换到「需求池整理」场景的 prompt</summary>

```
基于 pm-agent-lab/backlog-lab/L6-demo/backlog.md，在飞书"我的空间"下创建一篇云文档：

要求：
- 标题：[需求池] 本周候选需求摘要 · 2026-W25
- 内容：backlog.md 全部，外加顶部一段 ≤ 100 字的 TL;DR（覆盖几条高优需求）
- 创建后告诉我文档链接
- 不要发到任何群里——我自己来决定怎么转发到产研群
- 在执行 docs +create 之前，先把命令字符串完整打印出来让我确认一次

完成后把链接 append 到 pm-agent-lab/backlog-lab/L6-demo/HOWTO.md。
```
</details>

<details><summary>📝 切换到「会议纪要跟进」场景的 prompt</summary>

```
基于 pm-agent-lab/meeting-lab/L6-demo/follow-up.md，在飞书"我的空间"下创建一篇云文档：

要求：
- 标题：[会议待办] 本周跨团队待办与决策 · 2026-W25
- 内容：follow-up.md 全部，外加顶部一段 ≤ 100 字的 TL;DR（覆盖最紧急的几条事项）
- 创建后告诉我文档链接
- 不要发到任何群里、不要 @ 任何人——我自己来决定怎么分发给归属人
- 在执行 docs +create 之前，先把命令字符串完整打印出来让我确认一次

完成后把链接 append 到 pm-agent-lab/meeting-lab/L6-demo/HOWTO.md。
```
</details>

**👀 预期看到什么**
- Agent 先打印 `lark-cli docs +create ...` 完整命令等你确认
- 你说"OK"后它执行
- 拿到飞书文档链接，能直接打开

**⚠️ 如果出错怎么办**
- 偏差 A：Agent 直接执行没等你确认 → 立刻让它道歉并写进 `me.md`：

  ```
  我已经在 SKILL.md/me.md 里说过"破坏性或外发命令前必须人工确认"。请把这条规则补到你的 lark-lab 行为准则里。下次违反请自报。
  ```

- 偏差 B：`Permission denied` → scope 不全：

  ```
  按 lark-shared 的提示重新跑 auth login，并加上 docs:write scope。完成后再试。
  ```

---

### Step 3 · 把摘要发到群里（带"双确认"护栏）

> 这是第一次让 Agent 真正"对外发声"，必须特别谨慎。

**🎯 你要做什么**

**⌨️ 你输入什么**

```
我想把本周新闻周报的 TL;DR 和文档链接发到群"产品同步"。

请按下面三步走，每步都停下等我确认：

第一步：用 lark-cli 搜出"产品同步"群的 chat_id，先列出来，让我确认是哪个群（重名可能有多个）

第二步：把准备发送的消息内容**完整打印**给我看：
- 第一行：标题
- 中间：TL;DR ≤ 80 字
- 末尾：文档链接

第三步：我说"发"，你才执行 im +send-message；执行后给我 message_id。

约束：
- 不要 @ 任何人
- 不要在第二步之前去 send
- 如果第一步搜出多个同名群，给我列表让我选 chat_id，不要自己挑
```

<details><summary>📋 切换到「需求池整理」场景的 prompt</summary>

```
我想把本周需求池摘要的 TL;DR 和文档链接发到群"产研同步"。

请按下面三步走，每步都停下等我确认：

第一步：用 lark-cli 搜出"产研同步"群的 chat_id，先列出来，让我确认是哪个群（重名可能有多个）

第二步：把准备发送的消息内容**完整打印**给我看：
- 第一行：标题（本周候选需求摘要）
- 中间：TL;DR ≤ 80 字（覆盖 3 条高优需求 + 是否需要研发评估）
- 末尾：文档链接

第三步：我说"发"，你才执行 im +send-message；执行后给我 message_id。

约束：
- 不要 @ 任何人
- 不要在第二步之前去 send
- 如果第一步搜出多个同名群，给我列表让我选 chat_id，不要自己挑
```
</details>

<details><summary>📝 切换到「会议纪要跟进」场景的 prompt</summary>

```
我想把本周会议待办按归属人 @ 出去（同一条群消息内分别 @ 各责任人），目标群"项目协作"。

请按下面三步走，每步都停下等我确认：

第一步：用 lark-cli 搜出"项目协作"群的 chat_id；同时用 contact 查询本周待办里出现的归属人姓名对应的 open_id，列成"姓名→open_id"映射表给我确认

第二步：把准备发送的消息内容**完整打印**给我看：
- 第一行：标题（本周跨团队待办分发）
- 中间：每条待办一行，行首 @ 归属人 + 紧急度 + 一句话事项 + 截止建议
- 末尾：完整文档链接

第三步：我说"发"，你才执行 im +send-message；执行后给我 message_id。

约束：
- 不要在第二步之前去 send
- 如果某归属人 open_id 查不到，单独列出来让我决定（不要直接省略 @）
- 如果第一步搜出多个同名群，给我列表让我选 chat_id，不要自己挑
```
</details>

**👀 预期看到什么**
- 三个明显的暂停点
- 你像通过三道门才把消息送出去——这就是**敏感操作的标准姿势**

**📝 PM 决策时刻**
你会发现这种"步骤化 + 双确认"比你直接打字到群里**反而更不容易出错**——因为内容在打印阶段就被你审过一遍。

---

### Step 4 · 把数据落进飞书多维表格（结构化沉淀）

> markdown 文档适合给人读；多维表格适合做"长期资产 + 后续筛选"。

**🎯 你要做什么**
把本周新闻 8–12 条**逐行写入**一个多维表格。

**⌨️ 你输入什么**

```
我有一个飞书多维表格用来沉淀新闻周报，URL：<贴你的 base url>

要求：
1) 先用 base +list-fields 把当前字段列出来给我看（确保和 schema 对得上）
2) 字段对不上时，列出"建议新增 / 重命名"，但**不要自动改字段**——告诉我让我手动改
3) 字段对得上后，把本周 news.json 每条作为一行 append 到表里
4) 不要更新已有行（仅 append），避免覆盖历史
5) 写入完成后告诉我：写入 N 条 / 表里目前共 M 条 / 表的链接

涉及到任何字段结构变动前都先告诉我。
```

<details><summary>📋 切换到「需求池整理」场景的 prompt</summary>

```
我有一个飞书多维表格用作"需求池优先级看板"，URL：<贴你的 base url>

要求：
1) 先用 base +list-fields 把当前字段列出来给我看（确保和需求看板 schema 对得上：需求描述/来源/价值判断/优先级/状态/提出日期）
2) 字段对不上时，列出"建议新增 / 重命名"，但**不要自动改字段**——告诉我让我手动改
3) 字段对得上后，把本周 backlog.json 每条作为一行 append 到表里（默认状态=待评估）
4) 不要更新已有行（仅 append），避免覆盖历史需求
5) 写入完成后告诉我：写入 N 条 / 表里目前共 M 条 / 表的链接

涉及到任何字段结构变动前都先告诉我。
```
</details>

<details><summary>📝 切换到「会议纪要跟进」场景的 prompt</summary>

```
我有一个飞书多维表格用作"会议待办事项追踪"，URL：<贴你的 base url>

要求：
1) 先用 base +list-fields 把当前字段列出来给我看（确保和事项追踪 schema 对得上：事项/归属人/紧急度/截止日期/来源会议/状态）
2) 字段对不上时，列出"建议新增 / 重命名"，但**不要自动改字段**——告诉我让我手动改
3) 字段对得上后，把本周 follow-up.json 每条作为一行 append 到表里（默认状态=进行中）
4) 不要更新已有行（仅 append），避免覆盖历史事项
5) 写入完成后告诉我：写入 N 条 / 表里目前共 M 条 / 表的链接

涉及到任何字段结构变动前都先告诉我。
```
</details>

**👀 预期看到什么**
- 字段对齐报告
- 真实写入 N 行数据
- 表里历史数据安然无恙

**📝 这一步价值很大**：从此你的"新闻周报"不再是孤立的一周一份，而是**一张持续生长的资产表**——下季度想做"行业 OKR 复盘"，直接在表上筛就行。

---

### Step 5 · 把这套姿势写进 `news-weekly` Skill

**🎯 你要做什么**
让 L5 那个 Skill 自动**多走一步**——产出 + 飞书发布。

**⌨️ 你输入什么**

```
更新 pm-agent-lab/skills/news-weekly/SKILL.md：

在原流程末尾增加可选发布步骤：
- 如果调用方传 publish=lark，自动：
  1. 创建飞书云文档（仿 Step 2 流程，先打印命令再执行）
  2. 发送群通知（仿 Step 3 流程，三步双确认）
  3. 写入多维表格（仿 Step 4 流程，仅 append）

如果调用方没传 publish，所有产物只落本地，不动飞书。

更新完后给我一个新的触发示例：
- 仅本地版：跑一下 news-weekly，keywords=AI Agent
- 全流程版：跑一下 news-weekly，keywords=AI Agent，publish=lark
```

<details><summary>📋 切换到「需求池整理」场景的 prompt</summary>

```
更新 pm-agent-lab/skills/backlog-weekly/SKILL.md：

在原流程末尾增加可选发布步骤：
- 如果调用方传 publish=lark，自动：
  1. 创建飞书云文档（仿 Step 2 流程，先打印命令再执行）
  2. 发送产研群通知（仿 Step 3 流程，三步双确认）
  3. 写入需求池多维表格（仿 Step 4 流程，仅 append）

如果调用方没传 publish，所有产物只落本地，不动飞书。

更新完后给我一个新的触发示例：
- 仅本地版：跑一下 backlog-weekly
- 全流程版：跑一下 backlog-weekly，publish=lark
```
</details>

<details><summary>📝 切换到「会议纪要跟进」场景的 prompt</summary>

```
更新 pm-agent-lab/skills/meeting-followup/SKILL.md：

在原流程末尾增加可选发布步骤：
- 如果调用方传 publish=lark，自动：
  1. 创建飞书云文档（仿 Step 2 流程，先打印命令再执行）
  2. 发送项目协作群通知并按归属人 @（仿 Step 3 流程，三步双确认）
  3. 写入事项追踪多维表格（仿 Step 4 流程，仅 append）

如果调用方没传 publish，所有产物只落本地，不动飞书。

更新完后给我一个新的触发示例：
- 仅本地版：跑一下 meeting-followup
- 全流程版：跑一下 meeting-followup，publish=lark
```
</details>

**📝 至此**你的 Skill 已经从"个人本地工具"升级为"个人闭环工作流"——这就是 L9 端到端工作流的雏形。

---

## 5. 自检清单

- [ ] 我能让 Agent 在执行任何 `+create / +send / +write` 类命令前先打印命令等我确认
- [ ] 我能让 Agent 把本周新闻同时落到本地 + 飞书文档 + 多维表格
- [ ] 我有 `CLI_INVENTORY.md`，对 lark-cli 主要能力心里有数
- [ ] 我能用 30 秒解释"CLI vs 浏览器 vs 本地"分别什么时候用
- [ ] 我已经在 wiki/me.md 里强化了"敏感操作必须人工确认"规则

---

## 6. 思考题 & 下一讲引子

**思考题**
- 同样的内容，发飞书文档 / 多维表格 / 群聊，**哪种最适合长期复用**？为什么？这就是下一讲。
- 你公司还有哪些 CLI / 内部 API 可以让 Agent 接入？做一份候选清单。

**下一讲引子**
L7 我们专门讲"数据落点设计"——同一份数据，到底该进文档、表格、wiki，还是几者并存？这是 PM 在企业接入阶段最容易踩坑的环节。

---

## 7. 本讲交付物

按你选定的场景，下面三选一即可：

```
pm-agent-lab/
└── lark-lab/
    └── CLI_INVENTORY.md       # 飞书 CLI 能力速查 + 风险清单（三场景共用）

# 📰 news 场景
pm-agent-lab/skills/news-weekly/
└── SKILL.md                   # 已更新：增加 publish=lark 全流程
飞书空间（news）：
├── 云文档：[新闻周报] AI Agent · <week_id>
├── 群消息：产品同步群里一条 TL;DR + 链接
└── 多维表格：本周 N 条新闻已 append

# 📋 backlog 场景
pm-agent-lab/skills/backlog-weekly/
└── SKILL.md                   # 已更新：增加 publish=lark 全流程
飞书空间（backlog）：
├── 云文档：[需求池] 本周候选需求摘要 · <week_id>
├── 群消息：产研同步群里一条 TL;DR + 链接
└── 多维表格：需求池优先级看板已 append N 行

# 📝 meeting 场景
pm-agent-lab/skills/meeting-followup/
└── SKILL.md                   # 已更新：增加 publish=lark 全流程
飞书空间（meeting）：
├── 云文档：[会议待办] 本周跨团队待办与决策 · <week_id>
├── 群消息：项目协作群里一条 TL;DR + 链接（按归属人 @）
└── 多维表格：事项追踪表已 append N 行
```

---

## 8. 副线练习（可选）

本讲主线已可在三个场景切换，副线建议挑战更进阶的玩法：

- **会议纪要自动化**：会后让 Agent 读纪要 → 创建飞书文档 → 拆出 Action 项 → 写入"待办多维表格"并 @ 责任人
- **OKR 双周回顾**：让 Agent 每两周自动从你的 OKR 表抓数据 → 出一份回顾文档 → 发给 leader
- **日程巡检**：每天早 9 点让 Agent 用 calendar +agenda 整理今日日程 → 写到 wiki/today.md

---

## 9. 给 PM 的小结：CLI 使用的"三档信任"

| 档位 | 行为 | 何时启用 |
|------|------|----------|
| 🟢 **完全放手** | 只读命令（list / search / get） | 任何时候 |
| 🟡 **打印后执行** | 创建 / 写入 / 修改私有文档 | 默认 |
| 🔴 **三步双确认** | 群发 / 推送 / 删除 / 涉及他人的操作 | **永远** |

把这三档写进你的 wiki，**Agent 就永远不会越界**。
