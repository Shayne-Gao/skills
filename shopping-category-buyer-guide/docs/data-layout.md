# Data Layout

## Root

每个品类建议独立放在：

```text
shopping-research/<category_slug>/
```

示例：

```text
shopping-research/mite-remover/
shopping-research/tv_618_2026/
shopping-research/rice-cooker/
```

## Recommended Files

### 1. Latest capture

```text
<category_slug>_latest_capture.json
```

用途：
- 保存本轮从什么值得买抓到的原始候选
- 保存型号归一结果
- 保存价格、热度、讨论度等即时信号

建议结构：

```json
{
  "meta": {},
  "raw_items": [],
  "normalized_groups": [],
  "quick_takeaways": []
}
```

### 2. Model specs registry

```text
<category_slug>_model_specs_registry.json
```

用途：
- 长期保存型号参数
- 后续抓到新价格时直接 join

建议字段：
- `brand`
- `model`
- `series`
- `normalized_model`
- `aliases`
- `lookup_tokens`
- `key_specs`
- `warnings`
- `confidence`
- `sources`

如果是扁平字段，也可以直接展开为：
- `peak_power_w`
- `suction_kpa`
- `dust_capacity_ml`
- `battery_mah`

字段名按品类定制，但必须稳定。

### 3. Price history cache

```text
<category_slug>_price_history_cache.json
```

用途：
- 聚合本地所有已抓价格记录
- 让每天的新价格都能放进“全历史上下文”里判断
- 支撑四档输出中的价格证据，但不把历史低价当成唯一结论依据

建议字段：
- `normalized_model`
- `aliases`
- `current_focus_link`
- `deal_links`
- `all_time_low_price`
- `all_time_low_date`
- `recent_low_price`
- `latest_seen_price`
- `latest_seen_date`
- `price_samples`
- `status_band`
- `status_reason`
- `value_for_money_summary`
- `fit_summary`
- `info_completeness`
- `decision_confidence`
- `decision_factors`
- `source_files`

### 4. Buying advice

```text
<category_slug>_buying_advice.md
```

或：

```text
<category_slug>_buying_advice.html
```

用途：
- 人读结论页
- 记录推荐顺位、好价带、购买建议、替代项

### 5. Compare table

```text
<category_slug>_compare_table.md
```

或：

```text
<category_slug>_compare_table.html
```

用途：
- 每次抓新数据后输出主力型号横向比较
- 让后续对话直接复用，不必重新临时整理表格
- 把价格、参数、口碑、推荐结论放到同一张表里

建议列：
- `model_group`
- `deal_link`
- `current_price`
- `all_time_low_price`
- `recent_low_price`
- `price_position`
- `decision_band`
- `key_specs`
- `config_details`
- `public_feedback_summary`
- `value_for_money`
- `fit_for`
- `info_completeness`
- `recommendation_level`
- `buy_now_decision`

## Update Rule

价格与参数分开维护：
- 价格记录更新 `latest_capture`
- 型号参数更新 `model_specs_registry`
- 历史价格汇总更新 `price_history_cache`
- 本轮横向比较更新 `compare_table`

不要在每次刷新价格时重写整份参数库，除非：
- 发现新型号
- 补到了原本缺失的关键参数
- 修正了旧口径错误

但只要本轮抓了新数据：
- `compare_table` 必须更新
- `buying_advice` 也应至少做最小更新

## Naming Rule

`category_slug` 建议：
- 英文小写
- 用 `-` 连接
- 尽量稳定，不因一次问法不同而反复改名

例如：
- `mite-remover`
- `rice-cooker`
- `air-fryer`
- `vacuum-cleaner`

## Source Rule

每条参数记录都应带来源数组：

```json
[
  {
    "type": "官网参数页",
    "site": "品牌官网",
    "url": "https://example.com/spec"
  }
]
```

至少保留：
- `type`
- `site`
- `url`
