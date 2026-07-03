# Refresh Playbook

## When To Use

适用于以下场景：
- 用户说“抓一下最新好价”
- 用户说“默认来一轮 `3+5`”
- 用户说“重新抓最新并和历史比一下”
- 用户说“把这轮也落盘并给我推荐”

## Default Mode

默认执行：
- `jingxuan 1-3`
- `faxian 1-5`

除非用户明确要求更多页数，否则不要扩大抓取窗口。

## Execution Checklist

### 1. Prepare capture

生成新的 `capture_id`，新建目录：

```text
data/captures/<capture_id>/
```

### 2. Capture latest pages

逐页抓取默认窗口内商品。

每页成功后立即写入临时结果或直接写入 capture 文件，避免中途超时造成整轮丢失。

### 3. Persist full items

本轮成功抓到的所有商品必须写入：
- `all_items_pages.ndjson`
- `all_items_flat.tsv`

不要只保留推荐结果。

### 4. Write summary

写入：
- `capture_summary.json`

至少记录：
- 看了多少页
- 抓了多少行
- 每个 source 的分页条数
- 输出文件名

### 5. Compare against history

读取旧 capture 做历史匹配：
- 先按 `link`
- 再按标准化标题

输出：
- `history_price_index.json`

### 6. Build recommendation

基于：
- 当前价格
- 历史价格对比
- 是否强促 / 限时
- 商品可买性

生成：
- `top20.md`

## Required Delivery

对用户的最终输出必须包含：

1. 看了多少页
2. 抓了多少行
3. 更合适的 Top20

## Failure Handling

### WAF / Safety

如遇风控：
- 先停止扩大范围
- 先保住已抓到的页
- 明确说明哪些页成功、哪些页失败

### Partial success

若只抓到部分页：
- 仍然落盘已抓到的数据
- summary 中写清实际成功页数
- 不要伪装成完整成功

### Weak historical data

若历史库不足：
- 允许继续做推荐
- 但必须降低结论强度，标记“历史样本不足”

## Output Tone

推荐输出应偏向人工决策场景：
- 先给抓取规模
- 再给表格
- 推荐理由要简洁、可执行
- 不要用空泛评价替代价格对比
