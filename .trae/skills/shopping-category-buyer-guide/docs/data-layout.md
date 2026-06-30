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

### 3. Buying advice

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

## Update Rule

价格与参数分开维护：
- 价格记录更新 `latest_capture`
- 型号参数更新 `model_specs_registry`

不要在每次刷新价格时重写整份参数库，除非：
- 发现新型号
- 补到了原本缺失的关键参数
- 修正了旧口径错误

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
