# History Index

## Goal

对本轮 `3+5` 抓到的商品做历史价格对比，回答两个问题：

1. 这是不是历史上见过的同款 / 近似款？
2. 这次价格相比历史是更低、相近，还是更高？

注意：
- 历史价格对比只是推荐依据之一，不是全部。
- 最终推荐还必须结合 `SMZDM 平台信号`、值率、门槛和去噪结果，而不能只靠历史样本命中。
- `SMZDM` 页面给出的 `xx天新低 / 比上次发布低xx% / 价格低于618 / 低于常卖价` 可以作为历史型辅助证据，但不能替代本地历史索引。
- 本地历史默认更适合做“排除项”判断，而不是做强正向推荐。

## Matching Priority

历史比价必须按以下优先级执行：

### 1. Exact match by `link`

优先使用商品详情链接做同款匹配。

适合：
- 同一篇 SMZDM 商品页重复出现
- 明显同一条 deal 的重复刷新

### 2. Fallback match by normalized title

若 `link` 无法命中，再按标准化标题近似匹配。

标题标准化建议：
- 去掉多余空格
- 去掉常见营销前缀，如“今日必买”“手慢无”“绝对值”“值友专享”“百亿补贴”
- 保留核心商品名、规格、容量、件数

### 3. No match

若上述两步都无法命中，明确标为：

```text
历史样本不足
```

不能误报为“历史低价”。

## Output File

建议每轮生成：

- `history_price_index.json`

## Suggested Record Schema

每条记录对应本轮一个商品：

```json
{
  "capture_id": "20260629-104527",
  "source": "jingxuan",
  "page": 1,
  "title": "示例商品",
  "link": "https://www.smzdm.com/p/123456789/",
  "captured_at": "2026-06-29 10:45:27",
  "current_price_text": "69元",
  "match_type": "link",
  "history_found": true,
  "history_count": 3,
  "first_seen_at": "2026-06-20 10:15:00",
  "last_seen_at": "2026-06-27 08:41:12",
  "latest_history_price_text": "79元",
  "lowest_history_price_text": "65元",
  "price_signal": "near_low",
  "recommendation_hint": "可重点关注",
  "smzdm_history_tags": [
    "30天新低",
    "比上次发布低12%"
  ],
  "history_evidence_summary": "本地历史接近低位，且页面给出30天新低"
}
```

## Required Fields

最低字段：
- `capture_id`
- `source`
- `page`
- `title`
- `link`
- `captured_at`
- `current_price_text`
- `match_type`
- `history_found`
- `history_count`
- `first_seen_at`
- `last_seen_at`
- `latest_history_price_text`
- `lowest_history_price_text`
- `price_signal`

推荐补充字段：
- `smzdm_history_tags`
- `history_evidence_summary`

## Price Signal Labels

建议统一标签：

- `new_item`
- `history_missing`
- `lower_than_latest`
- `equal_to_latest`
- `higher_than_latest`
- `at_history_low`
- `near_low`
- `far_from_low`
- `smzdm_history_only`
- `history_conflict_with_smzdm`

## Recommendation Hints

建议输出一个轻量提示字段，便于 Top20 组装：

- `可重点关注`
- `可观察`
- `历史样本不足`
- `价格一般`

## Judgment Rules

### Strong positive

可以更积极推荐的情况：
- 当前价低于最近一次历史价
- 当前价接近或达到历史低价
- 商品为限时强促而非常驻普通会员价
- 商品本身属于高频刚需或价格敏感品类，且当前规格/容量明显划算

补充说明：
- 如果只是“低于本地历史”，最多说明没有明显负面证据，不能单独作为高优先级理由
- 强正向仍应优先依赖 `SMZDM` 平台标签和页面历史型标签

### Neutral

只适合观察的情况：
- 历史价格与当前接近
- 商品重复出现频繁但没有价格优势
- `SMZDM` 给出一般型标签，如 `热度Top / 商品好评率`，但缺少更强的历史证据
- 没有明确历史优势，但商品信息本身存在一定可买性

### Weak / avoid

不建议进 Top20 的情况：
- 当前价明显高于近期历史价
- 历史上多次出现更低价
- `SMZDM` 没有给出强平台信号，只剩商品自身活动标签
- 没有强促信号，只是常规价
- 门槛过重、规格偏小、单价优势不清晰

## Important Constraints

- 没有历史命中的商品，不能直接判为低价。
- 只有标题近似命中时，结论必须更保守。
- 历史对比是推荐依据之一，不是唯一依据；仍需结合 `SMZDM 平台标签`、品类常识、规格容量、门槛复杂度和限时属性。
- 没有历史样本时，仍然可以基于商品信息本身给出“可关注”或“可观察”，但不能伪装成历史低价判断。
- 若 `SMZDM` 页面历史型标签与本地历史相冲突，应优先写明“页面提示偏强，但本地历史未支持”，不要强推。
- 若当前价高于本地历史，应明确写出“本地历史已有更低价”，这是一条强负向证据。
