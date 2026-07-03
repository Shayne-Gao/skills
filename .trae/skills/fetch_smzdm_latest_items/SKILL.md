---
name: "fetch_smzdm_latest_items"
description: "Fetches latest SMZDM deals, persists full captures, compares against local history, and recommends Top20. Invoke when user asks for latest deals, price comparison, or SMZDM refresh."
---

# Fetch SMZDM Latest Items

This skill runs the `spider_smzdm` latest-items workflow in the `life_skills` workspace.

Use this skill when the user wants to:
- 抓取什么值得买最新内容
- 默认执行一轮 `jingxuan 3 页 + faxian 5 页`
- 在用户未明确要求更多页数时，按 `3+5` 执行，不要擅自扩大
- 将本轮抓到的所有商品和价格全量落盘
- 基于本地历史 capture 做价格对比、判断这次是否真便宜
- 输出一版更适合人工决策的 Top20 推荐表

## Scope

本 skill 负责以下闭环：
- 采集 `jingxuan` 最新 `3` 页
- 采集 `faxian` 最新 `5` 页
- 记录本轮所有抓到的标题、价格、平台、链接、抓取时间
- 将本轮数据落盘到 capture 目录
- 与本地历史 capture 对比，识别同款 / 类似款的历史价格
- 输出“看了多少页、抓了多少行”以及 Top20 推荐结果

## Workspace Layout

主项目目录：
- `workspace_projects/spider_smzdm/`

核心目录：
- `workspace_projects/spider_smzdm/data/`
- `workspace_projects/spider_smzdm/data/captures/`

关键文件：
- `workspace_projects/spider_smzdm/data/captures/README.md`
- `workspace_projects/spider_smzdm/spider_v2.py`
- `workspace_projects/spider_smzdm/README.md`

Skill docs：
- `docs/workflow.md`
- `docs/data-layout.md`
- `docs/history-index.md`
- `docs/refresh-playbook.md`

## Default Operating Rule

默认抓取范围：
- `jingxuan 1-3`
- `faxian 1-5`

只有在以下情况才扩大范围：
- 用户明确说“多抓一些”“抓更多页”“继续追加”
- 用户给出新的明确页数要求

如果用户没有明确要求更多页数，必须坚持默认 `3+5`。

## Data Persistence Rule

每一轮都必须新建一个 capture 目录：
- `workspace_projects/spider_smzdm/data/captures/<capture_id>/`

至少保留以下文件：
- `capture_summary.json`
- `all_items_pages.ndjson`
- `all_items_flat.tsv`
- `history_price_index.json`
- `top20.md`

如本轮有扩展页链接库存，也可保留：
- `additional_page_link_inventory.json`

### Required fields

`all_items_pages.ndjson`：
- 顶层至少包含：
  - `capture_id`
  - `captured_at`
  - `source`
  - `page`
- 每条 item 至少包含：
  - `title`
  - `price`
  - `mall`
  - `link`
  - `captured_at`

`all_items_flat.tsv` 列顺序固定为：
- `source`
- `page`
- `captured_at`
- `mall`
- `price`
- `link`
- `title`

更完整的数据结构约束见：
- `docs/data-layout.md`

## Analysis Rule

抓完默认 `3+5` 后，必须做历史对比，而不是只看当前页面：

1. 先读取当前 capture 的全量商品数据
2. 再读取本地历史 capture 数据
3. 优先按 `link` 对同款
4. 如果缺少稳定同款链路，再按标准化标题做近似比对
5. 对比历史中最近一次价格、历史低价、以及是否重复出现
6. 结合商品本身信息理解给出推荐等级和推荐理由，而不只是看历史命中

推荐时还要同时判断：
- 促销强度是否足够强
- 门槛是否复杂，是否需要买多件、叠券、会员或淘金币
- 规格、容量、件数是否真的划算
- 这是不是常驻价，还是有限时强促 / 错过可惜的价格
- 商品本身是否属于高频刚需、容易决策的品类

如果历史库中没有可比样本，要明确写：
- `历史样本不足`

不能把“没有历史记录”的商品伪装成“历史低价”。
但也不能因为没有历史样本，就完全放弃基于商品信息本身做推荐。

历史索引字段、价格信号标签和判断规则见：
- `docs/history-index.md`

## Output Rule

每次输出都必须先给：
- 看了多少页
- 抓了多少行

然后再给 Top20 表格。

Top20 至少应包含：
- 商品
- 平台
- 价格
- 推荐等级
- 门槛
- 推荐理由

如果商品标题带链接，优先让商品标题可点击。

## Anti-bot Rule

什么值得买链路存在风控 / WAF 风险，优先采用更稳的浏览器态或小批量页面解析方式。

执行时遵守以下规则：
- 默认用较小页数的稳定抓法，不一次性大批量拉取
- 遇到安全验证、验证码、Safety check 或异常空页，先停止自动扩大抓取
- 已成功抓到的数据先落盘，再继续下一页，避免中途丢数据

## Standard Flow

### 1. Decide page window

默认使用：
- `jingxuan 3`
- `faxian 5`

若用户明确要求更多页数，再按用户要求调整。

### 2. Capture current pages

逐页抓取当前窗口内的所有商品字段：
- 标题
- 价格
- 平台
- 链接
- 抓取时间
- 来源页

### 3. Persist full capture

将当前窗口内所有成功抓到的商品全量写入：
- `all_items_pages.ndjson`
- `all_items_flat.tsv`

同时写入：
- `capture_summary.json`

### 4. Compare with history

读取旧 capture，做：
- 同链接历史价对比
- 近似标题历史价对比
- 历史出现频次判断
- 是否新出现、是否价格刷新、是否可能为短促低价

### 5. Produce recommendation

输出：
- 看了多少页
- 抓了多少行
- 更合适的 Top20

本轮若完成历史对比，还必须落盘：
- `history_price_index.json`

推荐要优先偏向：
- 价格有明显优势
- 有限时或稀缺感
- 历史可对比后显得更便宜

同时也要避开：
- 门槛很重但文案看起来便宜的伪低价
- 规格小、单价未必划算的低客单价噪音
- 没有历史优势、也没有商品理解优势的普通常驻价

## Safety Notes

- 不要只落摘要，必须落本轮所有成功抓到的商品和价格。
- 不要覆盖旧 capture；每轮必须新增目录。
- 不要在没有历史依据时声称“历史最低”。
- 如遇明显风控导致页面不可读，先保住当前已抓到的数据，再决定是否继续。

## Engineering References

执行时优先按以下文档分工理解：
- `docs/refresh-playbook.md`：刷新执行顺序与失败处理
- `docs/data-layout.md`：落盘目录和文件格式
- `docs/history-index.md`：历史价格索引和对比规则
- `docs/workflow.md`：整体闭环和交付顺序

## Example Triggers

示例触发语句：
- “抓一下什么值得买最新好价”
- “按默认 3+5 抓一轮并推荐”
- “重新抓一下最新 deals，并和历史价格对比”
- “看看最近有什么真便宜的好价”
- “把最新一轮也落盘，然后给我 Top20”
