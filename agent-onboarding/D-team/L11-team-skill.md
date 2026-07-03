# Lesson 11 · 团队化：Skill 共享、版本与 Review

> 一句话定位：把"我自己用得很爽"升级为"全团队都能跑"——这是 PM 在 Agent 时代真正放大杠杆的那一档。

---

## 1. 你将学会

- [ ] 我能把一个个人 Skill **重构成团队可用版**（命名 / 文档 / 版本 / owner）
- [ ] 我能在团队里推行一份**最小 Skill 评审清单**，避免"什么都进 / 什么都乱"
- [ ] 我能让团队 Skill **平稳演进**，新同事开箱即用

---

## 2. 背景小知识

L5 你封装了个人 Skill。它的核心特征是"**只在你的 wiki / 你的电脑里跑**"。

团队 Skill 必须解决三件新问题：

| 问题 | 个人 Skill | 团队 Skill |
|------|-----------|------------|
| 谁来读？ | 只有你 | 多个 PM、可能还有研发 / 运营 |
| 上下文怎么办？ | 引用你的 wiki | **不能依赖你的私人 wiki**——必须自包含或引用团队 wiki |
| 谁负责维护？ | 你（默认） | **必须有 owner + 版本 + changelog** |

> 直觉口诀：**个人 Skill 像便利贴，团队 Skill 像产品。** 产品就要有定位、有文档、有 owner、有迭代。

⚠️ 反模式三连：
1. 把个人路径硬编码到 SKILL.md（只在自己电脑能跑）
2. SKILL.md 里随手引用了私人 wiki / 私人偏好
3. 没有 owner，三个月后没人改

---

## 3. 准备工作

- [ ] 已完成 L5（你有至少 1 个个人 Skill）
- [ ] 有一个团队共享代码仓库或飞书空间作为 Skill 注册地
- [ ] 工作目录：`pm-agent-lab/team-skills/`（个人 fork 区，等成熟再迁出去）

> 🎯 **三选一练手主线**
> 本讲示例默认演示「**行业 / 竞品周报**」场景（把 `news-weekly` 重构为 `team-news-weekly`）。如果你的日常工作里几乎不做行业调研，可以从下面三个 PM 通用场景里挑一个最贴近你工作的，下面 Step 里的 prompt 都给出三种版本：
>
> | 场景 ID | 适合谁 | 主线产物路径 |
> |---|---|---|
> | 📋 `backlog` 需求池整理 | 几乎所有 PM（覆盖率最高） | `pm-agent-lab/backlog-lab/L11-demo/` |
> | 📝 `meeting` 会议纪要跟进 | 跨团队协作多的 PM | `pm-agent-lab/meeting-lab/L11-demo/` |
> | 📰 `news` 行业 / 竞品周报 | 战略 / 对外汇报型 PM | `pm-agent-lab/news-lab/L11-demo/` |
>
> 每讲只需选 1 个跑透即可。HTML 单课页会根据你在首页选定的场景，自动把对应版本作为默认演示。下面文本版讲义里，**默认展开 `news` 版本，另外两个折叠在每个 Step 末尾**。

---

## 4. 实战任务

我们把 L5 的 `news-weekly` 升级为团队版 `team-news-weekly`。

---

### Step 1 · 让 Agent 帮你"体检"个人 Skill 能不能上团队

> 不是所有 Skill 都该团队化。先体检。

**🎯 你要做什么**

**⌨️ 你输入什么**

```
对 pm-agent-lab/skills/news-weekly/ 做一次"团队化体检"，写到 pm-agent-lab/team-skills/audit/news-weekly.md：

体检维度：
1) 复用度：有没有 ≥ 2 位同事真的会用？或者你预测会用？
2) 上下文耦合：SKILL.md 里有没有依赖"只有你电脑/你 wiki/你飞书账号"的部分？列出每条
3) 路径依赖：有没有写死的绝对路径 / 私人路径
4) 命名清晰度：触发词、Skill 名字是否够通用，会不会和别人冲突
5) 缺失项：要团队化还差什么（owner / 版本 / changelog / 例子 / 边界）

不要修改原 Skill，只输出体检报告。给一份"上 / 不上 / 改后再上"建议。
```

<details><summary>📋 切换到「需求池整理」场景的 prompt</summary>

```
对 pm-agent-lab/skills/backlog-weekly/ 做一次"团队化体检"，写到 pm-agent-lab/team-skills/audit/backlog-weekly.md：

体检维度：
1) 复用度：有没有 ≥ 2 位同事真的会用？或者你预测会用？
2) 上下文耦合：SKILL.md 里有没有依赖"只有你电脑/你 wiki/你飞书账号/你那张需求池多维表"的部分？列出每条
3) 路径依赖：有没有写死的绝对路径 / 私人路径 / 私人 base_id
4) 命名清晰度：触发词、Skill 名字是否够通用，会不会和别人冲突
5) 缺失项：要团队化还差什么（owner / 版本 / changelog / 例子 / 边界）

不要修改原 Skill，只输出体检报告。给一份"上 / 不上 / 改后再上"建议。
```
</details>

<details><summary>📝 切换到「会议纪要跟进」场景的 prompt</summary>

```
对 pm-agent-lab/skills/meeting-followup/ 做一次"团队化体检"，写到 pm-agent-lab/team-skills/audit/meeting-followup.md：

体检维度：
1) 复用度：有没有 ≥ 2 位同事真的会用？或者你预测会用？
2) 上下文耦合：SKILL.md 里有没有依赖"只有你电脑/你 wiki/你飞书账号/你的妙记账号"的部分？列出每条
3) 路径依赖：有没有写死的绝对路径 / 私人路径 / 私人会议归档目录
4) 命名清晰度：触发词、Skill 名字是否够通用，会不会和别人冲突
5) 缺失项：要团队化还差什么（owner / 版本 / changelog / 例子 / 边界）

不要修改原 Skill，只输出体检报告。给一份"上 / 不上 / 改后再上"建议。
```
</details>

**👀 预期看到什么**
- 一份很具体的体检报告，多半结论是"改后再上"
- 你能立刻看到自己 Skill 里"私人化"的程度

---

### Step 2 · 重构成 `team-news-weekly`

**🎯 你要做什么**

**⌨️ 你输入什么**

```
基于体检报告，把 news-weekly 重构为团队版，落到 pm-agent-lab/team-skills/team-news-weekly/。

要求：

[1] 目录结构
team-news-weekly/
├── SKILL.md           # 主流程，不可硬编码个人路径
├── README.md          # 给同事看的"为什么 / 怎么用 / 不要怎么用"
├── EXAMPLES.md        # 至少 3 个真实使用示例
├── CHANGELOG.md       # v0.1 起步
├── OWNERS.md          # owner / co-owner / 备份 owner
└── inputs/
    └── news.schema.example.md  # 字段契约示例（可被使用方 fork 改）

[2] 重构原则
- 路径全部用相对路径或参数化（如 ${TEAM_ROOT}）
- 不引用私人 wiki；如需上下文，让使用方自己接他们的 wiki
- 触发词改成更通用的："team-news-weekly" 或 "团队新闻周报"
- 加一段"前置约束"：使用方必须有 ROUTING.md 否则 Skill 拒绝跑

[3] OWNERS.md 内容
- 主 owner：<你的名字 + 工号>
- 备份 owner：1 个真实同事
- 决策权：变更需要 owner 审；分支可以由任何人提

[4] CHANGELOG.md
- v0.1（今天）：从 news-weekly 迁移而来；变更点列清

完成后给我一段 30 字以内的"团队公告"草稿，我用来发群。
```

<details><summary>📋 切换到「需求池整理」场景的 prompt</summary>

```
基于体检报告，把 backlog-weekly 重构为团队版，落到 pm-agent-lab/team-skills/team-backlog-weekly/。

要求：

[1] 目录结构
team-backlog-weekly/
├── SKILL.md           # 主流程，不可硬编码个人路径
├── README.md          # 给同事看的"为什么 / 怎么用 / 不要怎么用"
├── EXAMPLES.md        # 至少 3 个真实使用示例
├── CHANGELOG.md       # v0.1 起步
├── OWNERS.md          # owner / co-owner / 备份 owner
└── inputs/
    └── backlog.schema.example.md  # 字段契约示例（可被使用方 fork 改）

[2] 重构原则
- 路径全部用相对路径或参数化（如 ${TEAM_ROOT}、${BACKLOG_BASE_ID}）
- 不引用私人 wiki / 私人需求池 base；如需上下文，让使用方自己接他们的 wiki + base
- 触发词改成更通用的："team-backlog-weekly" 或 "团队需求池整理"
- 加一段"前置约束"：使用方必须有 ROUTING.md + 团队 backlog base 否则 Skill 拒绝跑

[3] OWNERS.md 内容
- 主 owner：<你的名字 + 工号>
- 备份 owner：1 个真实同事
- 决策权：变更需要 owner 审；分支可以由任何人提

[4] CHANGELOG.md
- v0.1（今天）：从 backlog-weekly 迁移而来；变更点列清

完成后给我一段 30 字以内的"团队公告"草稿，我用来发群。
```
</details>

<details><summary>📝 切换到「会议纪要跟进」场景的 prompt</summary>

```
基于体检报告，把 meeting-followup 重构为团队版，落到 pm-agent-lab/team-skills/team-meeting-followup/。

要求：

[1] 目录结构
team-meeting-followup/
├── SKILL.md           # 主流程，不可硬编码个人路径
├── README.md          # 给同事看的"为什么 / 怎么用 / 不要怎么用"
├── EXAMPLES.md        # 至少 3 个真实使用示例
├── CHANGELOG.md       # v0.1 起步
├── OWNERS.md          # owner / co-owner / 备份 owner
└── inputs/
    └── followup.schema.example.md  # 字段契约示例（可被使用方 fork 改）

[2] 重构原则
- 路径全部用相对路径或参数化（如 ${TEAM_ROOT}、${MEETING_NOTES_DIR}）
- 不引用私人 wiki / 私人妙记账号；如需上下文，让使用方自己接他们的 wiki + 会议归档
- 触发词改成更通用的："team-meeting-followup" 或 "团队会议待办分发"
- 加一段"前置约束"：使用方必须有 ROUTING.md + 团队会议归档目录否则 Skill 拒绝跑

[3] OWNERS.md 内容
- 主 owner：<你的名字 + 工号>
- 备份 owner：1 个真实同事
- 决策权：变更需要 owner 审；分支可以由任何人提

[4] CHANGELOG.md
- v0.1（今天）：从 meeting-followup 迁移而来；变更点列清

完成后给我一段 30 字以内的"团队公告"草稿，我用来发群。
```
</details>

**👀 预期看到什么**
- 一个**可以直接放团队仓库**的标准化目录
- 一段你能直接用的发群文案

---

### Step 3 · 起一份"团队 Skill 评审清单"

> Skill 越多越乱——必须有"准入门槛"。

**🎯 你要做什么**

**⌨️ 你输入什么**

```
帮我写 pm-agent-lab/team-skills/REVIEW_CHECKLIST.md：

一份"任何想进团队 Skill 库的提案"必须先过的清单。条目尽量可勾选、可验证：

[1] 价值
- [ ] 至少 2 位同事预期使用
- [ ] 月触发频次预估 ≥ 4
- [ ] 节省的时间 ≥ 1 人 30 分钟/月

[2] 健康度
- [ ] SKILL.md 不依赖私人路径 / 私人 wiki
- [ ] 有 README + EXAMPLES + CHANGELOG + OWNERS
- [ ] 触发词唯一（在团队 Skill 库里 grep 不到冲突）
- [ ] 有 dry_run 模式（如适用）

[3] 安全
- [ ] 引用了团队 AGENTS.md 等价规范
- [ ] 涉及外发 / 群发 / 删除 / 多人数据时，明确标 🟡/🔴
- [ ] 数据红线 / 反幻觉句式已嵌入

[4] 演进
- [ ] 有 owner + 备份 owner
- [ ] 有"何时不该用本 Skill"段落
- [ ] 提供了 1 条用户反馈通道（评论 / 飞书表 / 群）

末尾写："任意一项不达标 → 退回修改；不退回的 owner 是评审组组长。"
```

<details><summary>📋 切换到「需求池整理」场景的 prompt</summary>

```
帮我写 pm-agent-lab/team-skills/REVIEW_CHECKLIST.md：

一份"任何想进团队 Skill 库的提案"必须先过的清单（这次以 team-backlog-weekly 这种"需求池整理类 Skill"为参考视角）。条目尽量可勾选、可验证：

[1] 价值
- [ ] 至少 2 位同事预期使用
- [ ] 月触发频次预估 ≥ 4
- [ ] 节省的时间 ≥ 1 人 30 分钟/月

[2] 健康度
- [ ] SKILL.md 不依赖私人路径 / 私人 base / 私人 wiki
- [ ] 有 README + EXAMPLES + CHANGELOG + OWNERS
- [ ] 触发词唯一（在团队 Skill 库里 grep 不到冲突）
- [ ] 有 dry_run 模式（如适用，特别是写入需求池主表前）

[3] 安全
- [ ] 引用了团队 AGENTS.md 等价规范
- [ ] 涉及外发 / 群发 / 删除 / 多人数据（如 @ 提需求人）时，明确标 🟡/🔴
- [ ] 数据红线 / 反幻觉句式已嵌入

[4] 演进
- [ ] 有 owner + 备份 owner
- [ ] 有"何时不该用本 Skill"段落
- [ ] 提供了 1 条用户反馈通道（评论 / 飞书表 / 群）

末尾写："任意一项不达标 → 退回修改；不退回的 owner 是评审组组长。"
```
</details>

<details><summary>📝 切换到「会议纪要跟进」场景的 prompt</summary>

```
帮我写 pm-agent-lab/team-skills/REVIEW_CHECKLIST.md：

一份"任何想进团队 Skill 库的提案"必须先过的清单（这次以 team-meeting-followup 这种"会议待办分发类 Skill"为参考视角）。条目尽量可勾选、可验证：

[1] 价值
- [ ] 至少 2 位同事预期使用
- [ ] 月触发频次预估 ≥ 4
- [ ] 节省的时间 ≥ 1 人 30 分钟/月

[2] 健康度
- [ ] SKILL.md 不依赖私人路径 / 私人妙记账号 / 私人 wiki
- [ ] 有 README + EXAMPLES + CHANGELOG + OWNERS
- [ ] 触发词唯一（在团队 Skill 库里 grep 不到冲突）
- [ ] 有 dry_run 模式（如适用，特别是派任务给具体人前）

[3] 安全
- [ ] 引用了团队 AGENTS.md 等价规范
- [ ] 涉及外发 / 群发 / 删除 / 多人数据（如 @ 群、改飞书任务）时，明确标 🟡/🔴
- [ ] 数据红线 / 反幻觉句式已嵌入

[4] 演进
- [ ] 有 owner + 备份 owner
- [ ] 有"何时不该用本 Skill"段落
- [ ] 提供了 1 条用户反馈通道（评论 / 飞书表 / 群）

末尾写："任意一项不达标 → 退回修改；不退回的 owner 是评审组组长。"
```
</details>

---

### Step 4 · 真跑一次"评审会"

**🎯 你要做什么**
让 Agent 当评审组，把 `team-news-weekly` 按 REVIEW_CHECKLIST 过一遍。

**⌨️ 你输入什么**

```
你扮演"团队 Skill 评审组"，对 pm-agent-lab/team-skills/team-news-weekly/ 按 REVIEW_CHECKLIST.md 逐项打勾或不打勾，未达标的写一句改进建议。

评审风格：
- 客观、抓硬伤、不在风格鸡蛋里挑骨头
- 每条不达标都给"最小修复"建议（不要让 owner 大改）
- 末尾给整体结论：通过 / 退回（附最长 5 条退回原因）

把评审报告写到 pm-agent-lab/team-skills/audit/team-news-weekly-review.md。
```

<details><summary>📋 切换到「需求池整理」场景的 prompt</summary>

```
你扮演"团队 Skill 评审组"，对 pm-agent-lab/team-skills/team-backlog-weekly/ 按 REVIEW_CHECKLIST.md 逐项打勾或不打勾，未达标的写一句改进建议。

评审风格：
- 客观、抓硬伤、不在风格鸡蛋里挑骨头
- 每条不达标都给"最小修复"建议（不要让 owner 大改）
- 末尾给整体结论：通过 / 退回（附最长 5 条退回原因）

把评审报告写到 pm-agent-lab/team-skills/audit/team-backlog-weekly-review.md。
```
</details>

<details><summary>📝 切换到「会议纪要跟进」场景的 prompt</summary>

```
你扮演"团队 Skill 评审组"，对 pm-agent-lab/team-skills/team-meeting-followup/ 按 REVIEW_CHECKLIST.md 逐项打勾或不打勾，未达标的写一句改进建议。

评审风格：
- 客观、抓硬伤、不在风格鸡蛋里挑骨头
- 每条不达标都给"最小修复"建议（不要让 owner 大改）
- 末尾给整体结论：通过 / 退回（附最长 5 条退回原因）

把评审报告写到 pm-agent-lab/team-skills/audit/team-meeting-followup-review.md。
```
</details>

**📝 PM 决策时刻**
看完评审，**亲手按建议改一遍 SKILL/README/CHANGELOG**——不要再让 Agent 替你改。这一手改的过程会让你真正理解"团队产品"和"个人产品"的差别。

---

### Step 5 · 给 Skill 设计一条"增长曲线"

> Skill 上线不是终点。让它**自我成长**。

**🎯 你要做什么**

**⌨️ 你输入什么**

```
给 team-news-weekly 写一份 GROWTH.md，回答：

1) 本 Skill 的"成功指标"是什么？（如：周触发次数、月触发同事数、平均节省时长）
2) 怎么收数据？（建议用最低成本方案：使用者每次跑完手动写一行到 USAGE_LOG.md）
3) 评估节奏：建议每月 owner 看一次，每季度团队复盘一次
4) 演进规则：
   - 同一问题被反馈 ≥ 3 次 → 必须迭代
   - 半年没人用 → 进入"待退役"状态，再过 1 季度真退役
   - 出现新强场景 → 不要硬塞进现 Skill；fork 一个新 Skill

末尾给 owner 一段"接下来 30 天"的具体动作清单，3–5 条，可执行。
```

<details><summary>📋 切换到「需求池整理」场景的 prompt</summary>

```
给 team-backlog-weekly 写一份 GROWTH.md，回答：

1) 本 Skill 的"成功指标"是什么？（如：周触发次数、月触发同事数、平均节省时长、新增进入需求池主表的有效条目数）
2) 怎么收数据？（建议用最低成本方案：使用者每次跑完手动写一行到 USAGE_LOG.md）
3) 评估节奏：建议每月 owner 看一次，每季度团队复盘一次
4) 演进规则：
   - 同一问题被反馈 ≥ 3 次 → 必须迭代
   - 半年没人用 → 进入"待退役"状态，再过 1 季度真退役
   - 出现新强场景（比如多个团队都要 backlog 跨域聚合）→ 不要硬塞进现 Skill；fork 一个新 Skill

末尾给 owner 一段"接下来 30 天"的具体动作清单，3–5 条，可执行。
```
</details>

<details><summary>📝 切换到「会议纪要跟进」场景的 prompt</summary>

```
给 team-meeting-followup 写一份 GROWTH.md，回答：

1) 本 Skill 的"成功指标"是什么？（如：周触发次数、月触发同事数、平均节省时长、提取出的待办按时关闭率）
2) 怎么收数据？（建议用最低成本方案：使用者每次跑完手动写一行到 USAGE_LOG.md）
3) 评估节奏：建议每月 owner 看一次，每季度团队复盘一次
4) 演进规则：
   - 同一问题被反馈 ≥ 3 次 → 必须迭代
   - 半年没人用 → 进入"待退役"状态，再过 1 季度真退役
   - 出现新强场景（比如跨部门联会的待办分发）→ 不要硬塞进现 Skill；fork 一个新 Skill

末尾给 owner 一段"接下来 30 天"的具体动作清单，3–5 条，可执行。
```
</details>

---

## 5. 自检清单

- [ ] 我有 `team-news-weekly/` 完整目录，文件齐全
- [ ] 我有 `REVIEW_CHECKLIST.md`，并真的用它评审过 ≥ 1 个 Skill
- [ ] 我能 30 秒讲清"个人 Skill 和团队 Skill 的本质差别"
- [ ] 我有 `GROWTH.md`，知道这个 Skill 怎么长大、怎么退役
- [ ] 我有一段可发群的"团队公告"草稿

---

## 6. 思考题 & 下一讲引子

**思考题**
- 你团队现在没有任何 Skill 评审机制，加上之后会不会让大家"不愿意贡献"？怎么平衡？
- 如果 Skill 库膨胀到 50 个，你会用什么"目录"或"标签"让它继续可用？

**下一讲引子**
最后一讲 L12 我们做收尾——让你把这本手册学到的所有能力**变成你工作里持续被使用的"机会清单"**，并制定下一步行动。

---

## 7. 本讲交付物

按你选定的场景，下面三选一即可（评审清单 REVIEW_CHECKLIST.md 是三场景共用的）：

```
pm-agent-lab/
└── team-skills/
    ├── REVIEW_CHECKLIST.md            # 三场景共用
    │
    ├── audit/                         # 📰 news 场景产物
    │   ├── news-weekly.md
    │   └── team-news-weekly-review.md
    └── team-news-weekly/
        ├── SKILL.md
        ├── README.md
        ├── EXAMPLES.md
        ├── CHANGELOG.md
        ├── OWNERS.md
        ├── GROWTH.md
        └── inputs/news.schema.example.md

# 或 📋 backlog 场景：
pm-agent-lab/team-skills/
├── audit/
│   ├── backlog-weekly.md
│   └── team-backlog-weekly-review.md
└── team-backlog-weekly/
    ├── SKILL.md
    ├── README.md
    ├── EXAMPLES.md
    ├── CHANGELOG.md
    ├── OWNERS.md
    ├── GROWTH.md
    └── inputs/backlog.schema.example.md

# 或 📝 meeting 场景：
pm-agent-lab/team-skills/
├── audit/
│   ├── meeting-followup.md
│   └── team-meeting-followup-review.md
└── team-meeting-followup/
    ├── SKILL.md
    ├── README.md
    ├── EXAMPLES.md
    ├── CHANGELOG.md
    ├── OWNERS.md
    ├── GROWTH.md
    └── inputs/followup.schema.example.md
```

---

## 8. 副线练习（可选）

> 本讲主线已可在三个场景切换，副线建议挑战更进阶的玩法。

- 把 L8 三条候选 Skill（self-data-query / pm-mr-review / spec-tests）也按本讲流程团队化一个
- 在你部门起一个**Skill 飞书群**，固定每月最后一周开"30 分钟 Skill 评审会"
- 起一份**部门 Skill 索引**：用多维表格沉淀（按 L7 的落点决策）

---

## 9. 给 PM 的小结：团队化的"三段式"

| 段位 | 长什么样 | 标志 |
|------|----------|------|
| **个人** | 在你电脑里跑 | 有 SKILL.md |
| **团队** | 同事能跑 | 有 REVIEW + OWNERS + CHANGELOG |
| **平台** | 跨团队用、有运维 | 有监控 + SLA + 多版本兼容（通常交研发） |

绝大多数 PM Skill **停在团队段位就够了**。再往上是工程问题，不是 PM 问题。
