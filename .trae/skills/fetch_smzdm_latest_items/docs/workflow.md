# Workflow

## Goal

在 `workspace_projects/spider_smzdm/` 内执行一轮“默认 `3+5` 最新内容抓取 + 全量落盘 + 历史比价 + Top20 推荐”。

## Inputs

默认输入：
- `jingxuan_pages = 3`
- `faxian_pages = 5`

可选输入：
- 用户指定更多页数
- 用户指定只看某一池
- 用户指定只做落盘、不做推荐

## Steps

1. 确认抓取窗口
2. 逐页抓取最新商品字段
3. 先落盘当前页结果，再继续下一页
4. 写入本轮 capture 目录
5. 汇总本轮页数和条数
6. 读取历史 capture 做同款/近似款对比
7. 生成推荐结果与 Top20

## Capture Schema

### NDJSON page object

```json
{
  "capture_id": "20260629-104527",
  "captured_at": "2026-06-29 10:45:27",
  "source": "jingxuan",
  "page": 1,
  "items": [
    {
      "title": "示例商品",
      "price": "69元",
      "mall": "天猫精选",
      "link": "https://www.smzdm.com/p/123456789/",
      "captured_at": "2026-06-29 10:45:27"
    }
  ]
}
```

### Flat TSV columns

```text
source	page	captured_at	mall	price	link	title
```

## Historical Comparison

优先级：
1. 同 `link`
2. 标准化标题近似匹配

输出建议对比字段：
- 本次价格
- 最近一次历史价格
- 历史最低价
- 首次出现时间
- 最近出现时间
- 出现次数

## Delivery Format

每次都先输出：
- 看了多少页
- 抓了多少行

然后输出：
- Top20 推荐表

## Failure Handling

- 如某页抓取失败，保留已抓到页面并继续写 summary
- 如遇风控页或安全验证，停止扩大抓取范围
- 如历史样本不足，明确标注而不是强行判断低价
