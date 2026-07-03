# Lesson 8 · Agent + 代码协作：自助跑数据 / MR 评审 / 单测

> 一句话定位：PM 不需要会写代码，但**会让 Agent 写代码**——这是新形态 PM 最被低估的杠杆。

---

## 1. 你将学会

- [ ] 我能让 Agent 帮我**自助跑数据**（写 SQL / Python，看数据、出图）
- [ ] 我能让 Agent 帮我**读懂一个 MR**，并给非技术视角的 review
- [ ] 我能让 Agent 帮我跑一段**简单业务逻辑的单测**，提前验证设想

---

## 2. 背景小知识

老 PM 提需求时常常听到：
> "查这个数据要等数据团队排期"
> "这个 bug 行为我得先 review 代码看看"
> "你这个逻辑 corner case 我得回去想想"

新 PM 在 Agent 时代有一条新通路：

| 场景 | 老 PM 做法 | 新 PM 做法 |
|------|-----------|------------|
| 看一个数据指标 | 提需求等数据同学 | 让 Agent 写 SQL/Python 直接跑 |
| 看一个 bug 是怎么发生的 | 等研发解释 | 让 Agent 读代码给"翻译版" |
| 验证一个 corner case | 等开发完再测 | 让 Agent 写一个最小单测先验 |

> 直觉口诀：**你不需要写代码；你需要会判断 Agent 写的代码是不是在解决你的问题。**

⚠️ 三条红线：
1. **不要把生产代码权限给到 Agent 自动 push**——所有提交必须人工审。
2. **不要把含真实用户数据的查询直接跑到生产库**——先在测试库 / 脱敏数据集跑。
3. **PM 视角的 review 是"业务正确性"——别越界做技术深度评审**，把架构判断留给研发。

---

## 3. 准备工作

- [ ] 已完成 L7
- [ ] 工作目录：`pm-agent-lab/code-lab/`
- [ ] 准备一个**可以随便折腾的代码仓库**：你产品的 demo repo / 一个开源项目 / 或新 init 一个空仓库
- [ ] 准备一份**可以读取的脱敏数据**：CSV / SQLite 文件 / 任何不涉及隐私的样本

> 🎯 **三选一练手主线**
> 本讲示例默认演示「**行业 / 竞品周报**」场景。如果你的日常工作里几乎不做行业调研，可以从下面三个 PM 通用场景里挑一个最贴近你工作的，下面 Step 里的 prompt 都给出三种版本：
>
> | 场景 ID | 适合谁 | 主线产物路径 |
> |---|---|---|
> | 📋 `backlog` 需求池整理 | 几乎所有 PM（覆盖率最高） | `pm-agent-lab/backlog-lab/L8-demo/` |
> | 📝 `meeting` 会议纪要跟进 | 跨团队协作多的 PM | `pm-agent-lab/meeting-lab/L8-demo/` |
> | 📰 `news` 行业 / 竞品周报 | 战略 / 对外汇报型 PM | `pm-agent-lab/news-lab/L8-demo/` |
>
> 每讲只需选 1 个跑透即可。HTML 单课页会根据你在首页选定的场景，自动把对应版本作为默认演示。下面文本版讲义里，**默认展开 `news` 版本，另外两个折叠在每个 Step 末尾**。
>
> 在 L8 里，"功能上下文"按场景对应：
> - 📰 `news`：脚本是**行业新闻聚合脚本**（抓 RSS / 整理新闻 / 出 dashboard）
> - 📋 `backlog`：脚本是**需求池打分脚本**（读需求 CSV / 跑优先级算法 / 出排序）
> - 📝 `meeting`：脚本是**会议待办分发脚本**（读纪要 / 拆 Action 项 / 按归属人分发）

---

## 4. 实战任务

我们做 3 个 PM 真实场景。

---

### Step 1 · 自助跑数据：让 Agent 写 SQL / Python 帮你看数

**🎯 你要做什么**
准备一份脱敏 CSV（哪怕是飞书表格导出），让 Agent 跑出你想要的数据。

示例：你有一份 `users.csv`，列：`user_id, register_at, last_active_at, plan, region`。

**⌨️ 你输入什么**

```
[附 users.csv 路径或上传]

[角色] 你是数据分析师 + PM。

[上下文] 这是脱敏的用户数据，我想看几个最近留存相关的指标。

[任务] 用 Python（pandas）跑下面 4 个数据，每个指标都给：数值 + 一段不超过 30 字的口语化解读 + 1 张 matplotlib 图（保存到 pm-agent-lab/code-lab/charts/）。

指标：
1) D7 留存率（按周分组）
2) 各 plan 留存差异
3) 各 region 用户活跃度差异
4) 最近 7 天新注册的留存表现 vs 历史均值

[约束]
- 写一个独立 python 脚本：pm-agent-lab/code-lab/retention.py
- 每个指标单独函数，便于我之后改
- 跑完把脚本和图片路径告诉我
- 数据有任何异常（缺失/重复/格式问题）先停下来汇报，不要悄悄填默认值
- 不要安装非常用的库；只用 pandas / matplotlib

[产物]
- 脚本：pm-agent-lab/code-lab/retention.py
- 图：pm-agent-lab/code-lab/charts/*.png
- 一份 markdown 报告：pm-agent-lab/code-lab/retention-report.md（贴指标 + 解读 + 图链接）
```

<details><summary>📋 切换到「需求池整理」场景的 prompt</summary>

```
[附 backlog.csv 路径或上传，列：req_id, source, submitted_at, value_score, effort_score, status, owner]

[角色] 你是数据分析师 + PM。

[上下文] 这是脱敏的需求池数据，我想看几个最近优先级 / 流转相关的指标。

[任务] 用 Python（pandas）跑下面 4 个数据，每个指标都给：数值 + 一段不超过 30 字的口语化解读 + 1 张 matplotlib 图（保存到 pm-agent-lab/code-lab/charts/）。

指标：
1) 各 status 的需求分布（待评估 / 已立项 / 已交付 / 已拒绝）
2) value_score / effort_score 的二维散点（识别 RICE 高优区）
3) 各 source 进入需求池的速率（按周分组）
4) 最近 7 天新提的需求 vs 历史均值（看是否激增）

[约束]
- 写一个独立 python 脚本：pm-agent-lab/code-lab/backlog-score.py
- 每个指标单独函数，便于我之后改打分公式
- 跑完把脚本和图片路径告诉我
- 数据有任何异常（缺失/重复/格式问题）先停下来汇报，不要悄悄填默认值
- 不要安装非常用的库；只用 pandas / matplotlib

[产物]
- 脚本：pm-agent-lab/code-lab/backlog-score.py
- 图：pm-agent-lab/code-lab/charts/*.png
- 一份 markdown 报告：pm-agent-lab/code-lab/backlog-score-report.md
```
</details>

<details><summary>📝 切换到「会议纪要跟进」场景的 prompt</summary>

```
[附 followup.csv 路径或上传，列：item_id, meeting_name, owner, urgency, due_date, created_at, status, closed_at]

[角色] 你是数据分析师 + PM。

[上下文] 这是脱敏的会议待办数据，我想看几个最近闭环 / 拖延相关的指标。

[任务] 用 Python（pandas）跑下面 4 个数据，每个指标都给：数值 + 一段不超过 30 字的口语化解读 + 1 张 matplotlib 图（保存到 pm-agent-lab/code-lab/charts/）。

指标：
1) 整体闭环率（已 close / 总数）
2) 各 owner 的平均闭环时长 + 超期率
3) 各 urgency 档位的及时完成率
4) 最近 7 天新建待办 vs 同期已 close 待办（看是否在累积）

[约束]
- 写一个独立 python 脚本：pm-agent-lab/code-lab/followup-stats.py
- 每个指标单独函数，便于我之后调整口径
- 跑完把脚本和图片路径告诉我
- 数据有任何异常（缺失/重复/格式问题）先停下来汇报，不要悄悄填默认值
- 不要安装非常用的库；只用 pandas / matplotlib

[产物]
- 脚本：pm-agent-lab/code-lab/followup-stats.py
- 图：pm-agent-lab/code-lab/charts/*.png
- 一份 markdown 报告：pm-agent-lab/code-lab/followup-report.md
```
</details>

**👀 预期看到什么**
- 真的跑出 4 张图 + 一份报告
- 你打开报告就能贴到飞书发出去
- Agent 主动指出"你这份数据里有 X 行 last_active_at 缺失"——这是数据团队都未必会主动告诉你的

**⚠️ 如果出错怎么办**
- 偏差 A：Agent 写完不跑 → "请实际执行 retention.py 并把 stderr/stdout 给我看；不要只贴代码不跑。"
- 偏差 B：跑出空数据 → "先 head() 看 5 行，告诉我列名和 dtype，再跑指标。"

---

### Step 2 · MR 评审：让 Agent 给你"非技术视角翻译"

**🎯 你要做什么**
找一个真实 MR / PR，让 Agent 帮你 review。

**⌨️ 你输入什么**

```
我要 review 一个 MR：<MR 链接 / 本地分支 diff>

[角色] 你是 PM 协助人，不是研发 reviewer。请按 PM 视角看代码。

[任务]
1) 1 段 ≤ 100 字的"这个 MR 在做什么"白话翻译（给非研发同事也能看懂）
2) 列出本次改动**用户感知到**的变化（UI / 文案 / 行为 / 性能 / 错误提示）
3) 列出 3 个我应当追问研发的业务问题（不是架构问题）
4) 标出**疑似遗漏**的 corner case（ ≤ 3 个）
5) 不要评价代码风格 / 命名 / 架构——那是研发 reviewer 的事

输出到 pm-agent-lab/code-lab/mr-reviews/<MR 编号>.md。
```

<details><summary>📋 切换到「需求池整理」场景的 prompt</summary>

```
我要 review 一个 MR：<MR 链接 / 本地分支 diff>

[功能上下文] 这个 MR 改动的是"需求池打分脚本"（读 backlog.csv，跑 RICE / value*confidence/effort 等优先级算法，输出排序）。我关心的是打分逻辑变化是否符合 PM 心目中的优先级直觉。

[角色] 你是 PM 协助人，不是研发 reviewer。请按 PM 视角看代码。

[任务]
1) 1 段 ≤ 100 字的"这个 MR 在做什么"白话翻译（重点说明打分公式或字段权重的变化）
2) 列出本次改动会让"哪一类需求被排到更前 / 更后"
3) 列出 3 个我应当追问研发的业务问题（不是架构问题，例如"新公式对低 effort 高 value 的需求是否过度倾斜"）
4) 标出**疑似遗漏**的 corner case（ ≤ 3 个，例如缺失 effort 时如何兜底）
5) 不要评价代码风格 / 命名 / 架构——那是研发 reviewer 的事

输出到 pm-agent-lab/code-lab/mr-reviews/<MR 编号>.md。
```
</details>

<details><summary>📝 切换到「会议纪要跟进」场景的 prompt</summary>

```
我要 review 一个 MR：<MR 链接 / 本地分支 diff>

[功能上下文] 这个 MR 改动的是"会议待办分发脚本"（读会议纪要，拆出 Action 项，按归属人 @ 出去到协作群 / 写入事项追踪表）。我关心的是分发逻辑是否会漏发或错发。

[角色] 你是 PM 协助人，不是研发 reviewer。请按 PM 视角看代码。

[任务]
1) 1 段 ≤ 100 字的"这个 MR 在做什么"白话翻译（重点说明拆解规则或 @ 策略的变化）
2) 列出本次改动会让"哪一类待办被以何种方式分发出去"
3) 列出 3 个我应当追问研发的业务问题（不是架构问题，例如"无归属待办是否仍会进追踪表"）
4) 标出**疑似遗漏**的 corner case（ ≤ 3 个，例如归属人离职 / 同名重复 / 跨部门）
5) 不要评价代码风格 / 命名 / 架构——那是研发 reviewer 的事

输出到 pm-agent-lab/code-lab/mr-reviews/<MR 编号>.md。
```
</details>

**👀 预期看到什么**
- 一份**你可以直接发评论区**的 PM 视角 review
- "应追问研发"那 3 条问题 = 你这次 review 的真正价值

**📝 PM 视角的洞察**
研发评 MR 看"代码质量"；PM 评 MR 看"业务一致性"。两者互不替代。**让 Agent 帮你做 PM 视角，而不是越界做研发视角。**

---

### Step 3 · 用单测验证 corner case

> 你不需要会写测试代码——你只要会描述你担心的场景。

**🎯 你要做什么**
随便挑一个你产品里的"业务规则"，让 Agent 写最小单测验证。

示例：你的产品有规则"新用户注册 7 天内享受免费会员"。

**⌨️ 你输入什么**

```
我担心一个业务规则的 corner case，但不会写代码。请帮我做最小单测验证。

[规则] 新用户注册 7 天内享受免费会员；超过 7 天自动转为普通用户。

[我担心的场景]
1) 注册整 7 天那一刻是免费会员还是普通用户？
2) 注册时间是 23:59，第 8 天 0:01 算不算超时？
3) 用户跨时区时，"7 天"按服务器时区还是用户时区？
4) 用户注销后又注册同一邮箱算新用户吗？

[任务]
- 在 pm-agent-lab/code-lab/spec-tests/ 下用 pytest 写一组最小测试用例
- 每个 case 一个独立函数，函数名直接写中文场景描述
- mock 一个最简单的 is_free_member(user) 实现，带"你认为最合理"的业务边界
- 跑通后告诉我：哪些 case 通过、哪些 case 取决于"你假设的业务边界"
- 把"待与产品确认的边界假设"列成单独一份 markdown：boundary-questions.md
```

<details><summary>📋 切换到「需求池整理」场景的 prompt</summary>

```
我担心一个需求池打分规则的 corner case，但不会写代码。请帮我做最小单测验证。

[规则] 需求优先级 = (value * confidence) / effort；满足以下任一条件直接置为最低优先级：
   - effort 缺失
   - confidence 低于 0.3
   - 已存在重复需求（按标题相似度 > 0.85 判定）

[我担心的场景]
1) value=10、effort=0.0001 时分数会爆炸，是否需要加上限？
2) confidence 正好 0.3 是高优还是最低？
3) 同一需求来自 3 个不同来源，相似度判定怎么处理（取平均还是去重保留最高）？
4) 已交付的旧需求又被新人重新提，算重复吗？

[任务]
- 在 pm-agent-lab/code-lab/spec-tests/backlog-score/ 下用 pytest 写一组最小测试用例
- 每个 case 一个独立函数，函数名直接写中文场景描述
- mock 一个最简单的 score(req) 实现，带"你认为最合理"的业务边界
- 跑通后告诉我：哪些 case 通过、哪些 case 取决于"你假设的业务边界"
- 把"待与产品确认的边界假设"列成单独一份 markdown：boundary-questions.md
```
</details>

<details><summary>📝 切换到「会议纪要跟进」场景的 prompt</summary>

```
我担心一个会议待办分发规则的 corner case，但不会写代码。请帮我做最小单测验证。

[规则] 会议待办从纪要中拆出后：
   - 若纪要明确写了归属人姓名 → 按姓名查 open_id 后 @ 该人
   - 若姓名查不到 open_id → 标记为"待指派"，不发群、写入"无归属待办"列
   - 若纪要写"全员" / "团队" → 不 @ 个人，仅在群里发提醒
   - 紧急度高的待办自动同步到归属人个人 wiki/today.md

[我担心的场景]
1) 同名两个人（不同部门）→ 按谁的 open_id @？
2) 归属人姓名拼错（"张伟" vs "张玮"）→ 是按相似度兜底还是当作待指派？
3) 待办归属人就是我自己 → 还需不需要把我自己 @ 一遍？
4) 同一条待办在两次会议里被重复提到 → 分发两次还是合并？

[任务]
- 在 pm-agent-lab/code-lab/spec-tests/followup-dispatch/ 下用 pytest 写一组最小测试用例
- 每个 case 一个独立函数，函数名直接写中文场景描述
- mock 一个最简单的 dispatch(item) 实现，带"你认为最合理"的业务边界
- 跑通后告诉我：哪些 case 通过、哪些 case 取决于"你假设的业务边界"
- 把"待与产品确认的边界假设"列成单独一份 markdown：boundary-questions.md
```
</details>

**👀 预期看到什么**
- 一组真的能跑的单测
- 一份"我假设的业务边界" 清单——这就是你下次找研发对齐的**精确清单**

**📝 PM 决策时刻**
你刚刚做了一件传统 PM 几乎不会做的事：**把模糊的业务规则用单测的精确度逼出来**。这一份 `boundary-questions.md` 拿到评审会上，研发会觉得"这个 PM 想得真清楚"。

---

### Step 4 · 把这三个姿势写进 Skill 候选清单

**🎯 你要做什么**

```
在 pm-agent-lab/skills/_BACKLOG.md 增加三条候选 Skill：

1) self-data-query：自助跑数据
   触发：当我贴 CSV/SQL 并要求看数据时
   流程：read → describe → 跑指标 → 出图 → markdown 报告
   产物路径：pm-agent-lab/code-lab/<task>/

2) pm-mr-review：PM 视角 MR review
   触发：当我贴 MR 链接并要 review 时
   流程：白话翻译 → 用户感知变化 → 应追问问题 → 疑似遗漏 corner case
   产物路径：pm-agent-lab/code-lab/mr-reviews/<MR 编号>.md

3) spec-tests：业务规则单测
   触发：当我描述一个业务规则 + 担心场景时
   流程：写最小 pytest → 跑通 → 列出"假设边界"清单
   产物路径：pm-agent-lab/code-lab/spec-tests/<rule>/

每条加一句"何时不该用此 Skill"。
```

<details><summary>📋 切换到「需求池整理」场景的 prompt</summary>

```
在 pm-agent-lab/skills/_BACKLOG.md 增加三条候选 Skill（围绕"需求池打分脚本"上下文）：

1) backlog-score-query：自助跑需求池打分数据
   触发：当我贴 backlog.csv 并要求看分布 / RICE 排序时
   流程：read → describe → 跑 4 类指标（status / RICE / 来源速率 / 增量）→ 出图 → markdown 报告
   产物路径：pm-agent-lab/code-lab/<task>/

2) pm-mr-review-backlog：需求池打分脚本 PM 视角 review
   触发：当我贴打分脚本相关 MR 链接并要 review 时
   流程：白话翻译公式变化 → 哪类需求会被排前/排后 → 应追问问题 → 疑似遗漏 corner case
   产物路径：pm-agent-lab/code-lab/mr-reviews/<MR 编号>.md

3) spec-tests-backlog：需求评分规则单测
   触发：当我描述一个评分规则 + 担心场景时
   流程：写最小 pytest → 跑通 → 列出"假设边界"清单
   产物路径：pm-agent-lab/code-lab/spec-tests/<rule>/

每条加一句"何时不该用此 Skill"。
```
</details>

<details><summary>📝 切换到「会议纪要跟进」场景的 prompt</summary>

```
在 pm-agent-lab/skills/_BACKLOG.md 增加三条候选 Skill（围绕"会议待办分发脚本"上下文）：

1) followup-stats-query：自助跑会议待办数据
   触发：当我贴 followup.csv 并要求看闭环率 / 拖延情况时
   流程：read → describe → 跑 4 类指标（闭环率 / 各 owner 时长 / 紧急度完成率 / 累积速率）→ 出图 → markdown 报告
   产物路径：pm-agent-lab/code-lab/<task>/

2) pm-mr-review-followup：待办分发脚本 PM 视角 review
   触发：当我贴待办分发脚本相关 MR 链接并要 review 时
   流程：白话翻译拆解 / @ 策略 → 哪类待办被如何分发 → 应追问问题 → 疑似遗漏 corner case
   产物路径：pm-agent-lab/code-lab/mr-reviews/<MR 编号>.md

3) spec-tests-followup：待办分发规则单测
   触发：当我描述一个分发规则 + 担心场景时
   流程：写最小 pytest → 跑通 → 列出"假设边界"清单
   产物路径：pm-agent-lab/code-lab/spec-tests/<rule>/

每条加一句"何时不该用此 Skill"。
```
</details>

---

## 5. 自检清单

- [ ] 我能让 Agent 跑出一份完整的"留存数据 + 图 + 解读"报告
- [ ] 我能让 Agent 给一个 MR 出 PM 视角 review，且不越界
- [ ] 我能让 Agent 写最小单测把"模糊业务规则"逼出精确边界
- [ ] 我有 `_BACKLOG.md` 里 3 条新候选 Skill
- [ ] 我能用 30 秒讲清"PM 让 Agent 做代码"的三条红线

---

## 6. 思考题 & 下一讲引子

**思考题**
- 你过去一周，有几次"想看一个数据但等了好几天"？这就是你最该自助化的地方。
- 你 review 过的 MR 里，最常忽略的是哪一类问题？让 Agent 在这一类上**专门盯紧你**。

**下一讲引子**
L9 我们把 L1–L8 所有积累串起来，做一个**真正端到端的工作流**：从行业新闻到飞书周报到表格沉淀到群同步到下次复用——一句话触发，全程跑通。

---

## 7. 本讲交付物

按你选定的场景，下面三选一即可（`code-lab/` 通用骨架共用，差别在脚本名 / 报告 / 单测的"功能上下文"）：

```
# 📰 news 场景（默认演示：留存为示例数据；脚本上下文 = 行业新闻聚合脚本）
pm-agent-lab/
└── code-lab/
    ├── retention.py
    ├── retention-report.md
    ├── charts/*.png
    ├── mr-reviews/<MR 编号>.md          # 行业新闻聚合脚本 MR review
    └── spec-tests/<rule>/
        ├── test_*.py
        └── boundary-questions.md
pm-agent-lab/skills/
└── _BACKLOG.md   # 已增加 3 条候选（self-data-query / pm-mr-review / spec-tests）

# 📋 backlog 场景（脚本上下文 = 需求池打分脚本）
pm-agent-lab/
└── code-lab/
    ├── backlog-score.py
    ├── backlog-score-report.md
    ├── charts/*.png
    ├── mr-reviews/<MR 编号>.md          # 打分脚本 PM 视角 review
    └── spec-tests/backlog-score/
        ├── test_*.py
        └── boundary-questions.md
pm-agent-lab/skills/
└── _BACKLOG.md   # 已增加 3 条候选（backlog-score-query / pm-mr-review-backlog / spec-tests-backlog）

# 📝 meeting 场景（脚本上下文 = 会议待办分发脚本）
pm-agent-lab/
└── code-lab/
    ├── followup-stats.py
    ├── followup-report.md
    ├── charts/*.png
    ├── mr-reviews/<MR 编号>.md          # 分发脚本 PM 视角 review
    └── spec-tests/followup-dispatch/
        ├── test_*.py
        └── boundary-questions.md
pm-agent-lab/skills/
└── _BACKLOG.md   # 已增加 3 条候选（followup-stats-query / pm-mr-review-followup / spec-tests-followup）
```

---

## 8. 副线练习（可选）

本讲主线已可在三个场景切换，副线建议挑战更进阶的玩法：

- **运营数据日巡检**：让 Agent 每天读一份脱敏数据集，按你定义的 5 个核心指标跑 + 出图，写到 wiki/today-metrics.md
- **PRD 反向 lint**：让 Agent 读你最新一份 PRD，挑出"未定义边界 / 含糊副词 / 自相矛盾"的句子
- **客服反馈快速分类**：把客服每周导出的 CSV 喂给 Agent，自动按主题聚类 + 给三个最值得跟进的 case

---

## 9. 给 PM 的小结：代码协作的"PM 三件事"

| 你做的事 | 不是 | 是 |
|----------|------|----|
| 跑数据 | 学 SQL/Python | 描述要看的指标 + 让 Agent 写代码 + 看结果 |
| 评审 MR | 看代码质量 | 看业务一致性 + 列追问清单 |
| 验证规则 | 学单测语法 | 描述担心场景 + 让 Agent 跑单测 + 收"边界假设" |

记住：**PM 是在用代码做产品判断，不是在做工程**。这条边界守住，你和研发就永远是合作而不是越界。
