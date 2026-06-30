---
name: "shopping-category-buyer-guide"
description: "Builds a category buying guide from recent SMZDM deals, model specs, reviews, and price context. Invoke when user asks how to choose or compare a product category such as TVs or mite removers."
---

# Shopping Category Buyer Guide

This skill turns a shopping category request into a reusable buying workflow:
- search recent SMZDM deals for the category
- normalize and group models
- research key specs from external sources
- summarize public praise and complaints
- recommend what to buy, fair prices, and whether to order now
- persist model specs and current-round price records for future refreshes

Use this skill when the user wants to:
- 研究一个品类最近有哪些好价
- 输入一个品类后做选购建议，例如“除螨仪”“电视”“电饭煲”
- 比较多个型号的关键参数、口碑和性价比
- 判断什么价位算好价、现在值不值得买
- 沉淀某个品类的本地价格库、型号参数库、推荐结论

## Scope

本 skill 负责以下闭环：
- 从什么值得买搜索页抓取该品类近期好价
- 去重、过滤噪音、按型号归一化
- 补充每个主力型号的关键参数与来源
- 汇总“大家常夸什么、常吐槽什么”
- 按多个维度给选购建议
- 将价格记录、型号参数、结论文件落盘到本地目录

## Non-Goals

本 skill 不负责：
- 代替真实下单决策中的最终付款链路
- 伪造未核实的参数、口碑或历史低价
- 只看当前页面价格就直接给“闭眼买”结论

如果用户只是要抓全站最新什么值得买内容，不带特定品类分析，优先使用 `fetch_smzdm_latest_items`。

## Input Contract

最低输入：
- 一个品类关键词，例如 `除螨仪`

推荐补充输入：
- 预算区间
- 使用场景
- 核心诉求，例如“清洁能力”“噪音”“是否适合长辈”“是否要低维护”
- 是否需要 HTML 宽表 / 在线页

如果用户没补充，先按通用家庭场景做第一轮研究，再明确说明默认假设。

## Required Outputs

每次执行至少应交付：
- 本轮看了哪些什么值得买结果页
- 抓到多少条候选
- 归一后有哪些主力型号
- 每个主力型号的关键参数和口碑摘要
- 不同预算/场景下的推荐结论
- 明确回答：
  - `最推荐买哪个型号`
  - `什么价格算合适`
  - `当前有哪些型号性价比不错`
  - `现在是否建议下单，还是继续等`

## Persistence Rule

每个品类都应在 `shopping-research/<category_slug>/` 下持续沉淀，至少保留：
- `*_latest_capture.json`
- `*_model_specs_registry.json`
- `*_buying_advice.md` 或 `*.html`

如已存在历史文件：
- 优先增量更新，不要无理由覆盖整库
- 型号参数优先 patch 更新
- 新一轮价格记录单独更新 capture 文件

具体目录与字段见：
- `docs/data-layout.md`
- `docs/workflow.md`
- `docs/spec-research-playbook.md`
- `docs/recommendation-framework.md`

## Core Operating Rules

1. 先抓近期好价，再做参数和推荐，不要脱离实际在售价格空谈。
2. 先按型号归一再研究参数，避免同款不同标题重复分析。
3. 参数只写可验证硬参数；不能稳定核实就写 `null` 或在 warning 说明。
4. 必须区分：
   - 原生参数
   - 营销口径
5. 评价部分优先提炼稳定共识，而不是只摘一条极端评论。
6. 推荐结论必须同时看：
   - 当前价格
   - 型号能力
   - 常见口碑
   - 适用人群
   - 是否属于值得现在买的价位
7. 如果历史价格样本不足，要明确写 `历史样本不足`。
8. 如果关键参数不完整，要降低推荐确定性，而不是装作结论很稳。

## Standard Flow

### 1. Clarify category and scenario

确认：
- 品类关键词
- 是否有预算/用途/特殊人群

### 2. Capture recent SMZDM deals

围绕品类关键词抓最近什么值得买搜索结果，记录：
- 标题
- 价格
- 平台
- 链接
- 标签
- 时间
- 值率/评论等热度信息

### 3. Normalize models

对候选条目做：
- 去重
- 噪音过滤
- 型号抽取
- 系列归组

### 4. Research model specs

对核心型号从品牌官网、官方电商参数页、主流参数站、评测等交叉核实：
- 关键硬参数
- 参数冲突
- 明确来源

### 5. Summarize public feedback

提炼每个型号的：
- 常见优点
- 常见问题
- 适合谁
- 不适合谁

### 6. Produce buying advice

至少给出：
- 最推荐型号
- 好价带
- 当前最值得关注的替代项
- 是否建议现在下单
- 观望条件是什么

### 7. Persist artifacts

把本轮结果落盘，方便后续只刷新价格或补充新型号。

## Example Triggers

- “帮我做个除螨仪选购建议”
- “从什么值得买看看最近电饭煲好价”
- “这个品类有哪些型号最值得买”
- “什么价格算好价，现在能买吗”
- “把这个品类做成长期跟踪的选购库”
