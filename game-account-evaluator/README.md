# 游戏账号评估器（可复用框架）

目标：把账号资源（5 星角色 / 5 星武器 / 剩余抽数）统一换算为一个固定数值，再用该数值与售价的比例做性价比排序。

## 鸣潮（Kejinshou 平台）— 用法

1. 先用你已有的 curl 拉接口，把响应 JSON 喂给脚本（建议落盘缓存）：

```bash
curl 'https://api.kejinshou.com/...' -H '...' \
  | python3 game-account-evaluator/scripts/evaluate_wuthering_waves_kejinshou.py --save-raw
```

2. 或者对已缓存的 JSON 文件直接评估：

```bash
python3 game-account-evaluator/scripts/evaluate_wuthering_waves_kejinshou.py \
  --input game-account-evaluator/data/raw/kejinshou_*.json
```

3. 自定义权重（单位：等价抽数）：

```bash
python3 game-account-evaluator/scripts/evaluate_wuthering_waves_kejinshou.py \
  --input game-account-evaluator/data/raw/kejinshou_*.json \
  --weights '{"char5":90,"weapon5":70,"pull":1}'
```

4. 固定输出文件名（推荐用于“原始文件 + 评分文件”两份落盘）：

```bash
curl 'https://api.kejinshou.com/...' -H '...' \
  | python3 game-account-evaluator/scripts/evaluate_wuthering_waves_kejinshou.py \
    --raw-out game-account-evaluator/data/raw/kejinshou_wuwa_p1.json \
    --csv-out game-account-evaluator/outputs/kejinshou_wuwa_p1_scored.csv
```

脚本会输出：
- 标准输出：按性价比排序的明细表
- 本地文件：`game-account-evaluator/outputs/ranking_*.csv`
