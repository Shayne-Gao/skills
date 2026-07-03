# Data Layout

## Project Root

- `workspace_projects/spider_smzdm/`

## Runtime Data Root

- `workspace_projects/spider_smzdm/data/`

## Capture Root

- `workspace_projects/spider_smzdm/data/captures/`

每轮抓取必须新建一个以开始时间命名的 capture 目录：

```text
data/captures/<capture_id>/
```

推荐格式：

```text
YYYYMMDD-HHMMSS
```

例如：

```text
20260629-104527
```

## Required Files Per Capture

### 1. `capture_summary.json`

用途：
- 记录本轮抓取摘要
- 作为本轮交付总索引

最低字段：
- `capture_id`
- `captured_at`
- `strategy`
- `counts`
- `pools`
- `files`
- `notes`

### 2. `all_items_pages.ndjson`

用途：
- 保留逐页全量原始商品字段
- 作为后续历史补录和问题回放的主数据源

每行一个 page object。

page object 最低字段：

```json
{
  "capture_id": "20260629-104527",
  "captured_at": "2026-06-29 10:45:27",
  "source": "jingxuan",
  "page": 1,
  "count": 20,
  "items": []
}
```

item 最低字段：

```json
{
  "title": "示例商品",
  "price": "69元",
  "mall": "天猫精选",
  "link": "https://www.smzdm.com/p/123456789/",
  "captured_at": "2026-06-29 10:45:27"
}
```

建议扩展字段：
- `price_value`
- `normalized_title`
- `availability_label`
- `tag_labels`

### 3. `all_items_flat.tsv`

用途：
- 便于快速检索、diff、筛选和脚本消费

列顺序固定：

```text
source	page	captured_at	mall	price	link	title
```

不要擅自调整列顺序。

### 4. `top20.md`

用途：
- 提供面向人工决策的推荐结果

必须包含：
- 看了多少页
- 抓了多少行
- Top20 推荐表

### 5. `history_price_index.json`

用途：
- 保存当前轮对历史 capture 的价格对比结果
- 作为“是否真便宜”的结构化依据

若本轮完成了历史对比，必须生成该文件。

## Optional Files

### `additional_page_link_inventory.json`

适用于扩展抓取窗口的情况，保留页级链接库存，便于回溯。

### `comparison_notes.md`

适用于需要补充人工判断说明时，记录：
- 为什么判定为真低价
- 为什么只给观察而不推荐
- 哪些条目因为历史样本不足而未强判

## Source Windows

默认窗口：
- `jingxuan 1-3`
- `faxian 1-5`

扩展窗口只在用户明确要求时启用。

## Data Roles

三类数据职责分离：

1. 页面全量抓取
- `all_items_pages.ndjson`

2. 便于对比的平铺表
- `all_items_flat.tsv`

3. 历史价格分析结果
- `history_price_index.json`

不要把这三类职责混在一个文件里。
