import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


PLATFORM_PATTERNS: Dict[str, str] = {
    "kejinshou": "kejinshou_incremental_page1_*.json",
    "7881": "7881_incremental_page1_*.json",
    "pzds": "pzds_incremental_page1_*.json",
}


def _latest_file(raw_dir: Path, pattern: str) -> Path:
    matches = sorted(raw_dir.glob(pattern), key=lambda p: p.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(f"未找到增量快照: {pattern}")
    return matches[-1]


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_row(platform: str, row: Dict[str, Any]) -> Dict[str, Any]:
    if platform == "kejinshou":
        product_id = str(row.get("id") or "")
        detail_url = f"https://m.kejinshou.com/goods/details/{product_id}" if product_id else ""
        listing_time = str(row.get("upper_at") or "")
        listing_desc = str(row.get("polish_time_desc") or "")
    elif platform == "7881":
        product_id = str(row.get("goods_id") or row.get("id") or "")
        detail_url = ""
        listing_time = ""
        listing_desc = str(row.get("publish_text") or "")
    else:
        product_id = str(row.get("id") or "")
        detail_url = f"https://www.pzds.com/goodsDetails/{product_id}/6?from=%E5%95%86%E5%93%81%E5%88%97%E8%A1%A8" if product_id else ""
        listing_time = str(row.get("onStandTime") or "")
        listing_desc = str(row.get("publish_text") or "")

    return {
        "platform": platform,
        "rank": int(row.get("rank") or 0),
        "product_id": product_id,
        "price": row.get("price") or "",
        "listing_time": listing_time,
        "listing_desc": listing_desc,
        "seen_before": bool(row.get("seen_before")),
        "new_by_id": bool(row.get("new_by_id")),
        "detail_url": detail_url,
    }


def _platform_title(platform: str) -> str:
    return {
        "kejinshou": "Kejinshou",
        "7881": "7881",
        "pzds": "PZDS",
    }[platform]


def _load_sources(base_dir: Path) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    raw_dir = base_dir / "data" / "raw"
    sources: List[Dict[str, Any]] = []
    rows: List[Dict[str, Any]] = []

    for platform, pattern in PLATFORM_PATTERNS.items():
        path = _latest_file(raw_dir, pattern)
        obj = _load_json(path)
        items = obj.get("items") or []
        summary = obj.get("summary") or {}
        normalized_rows = [_normalize_row(platform, row) for row in items]
        rows.extend(normalized_rows)
        sources.append(
            {
                "platform": platform,
                "platform_title": _platform_title(platform),
                "file_path": str(path),
                "captured_at": obj.get("capturedAt") or "",
                "batch_count": int(summary.get("batchCount") or len(normalized_rows)),
                "new_count": int(summary.get("newCount") or 0),
                "existing_count": int(summary.get("existingCount") or 0),
                "new_ids": summary.get("newIds") or [],
            }
        )

    return sources, rows


def _render_html(sources: List[Dict[str, Any]], rows: List[Dict[str, Any]]) -> str:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_new = sum(item["new_count"] for item in sources)
    total_batch = sum(item["batch_count"] for item in sources)
    data_json = json.dumps(rows, ensure_ascii=False)
    source_json = json.dumps(sources, ensure_ascii=False)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>鸣潮增量刷新汇总</title>
  <style>
    :root {{
      --bg: #0a1020;
      --panel: #111a31;
      --panel-2: #162341;
      --line: #29416f;
      --text: #edf2ff;
      --muted: #9cb0d9;
      --good: #5fd39c;
      --chip: #21355f;
      --warn: #ffcf70;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: linear-gradient(180deg, #08101d, #101a34); color: var(--text); }}
    a {{ color: #9cc2ff; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .wrap {{ max-width: 1560px; margin: 0 auto; padding: 24px; }}
    .hero, .panel {{ background: rgba(17, 26, 49, 0.96); border: 1px solid var(--line); border-radius: 18px; }}
    .hero {{ padding: 22px 24px; margin-bottom: 18px; }}
    .hero h1 {{ margin: 0 0 8px; font-size: 30px; }}
    .hero p {{ margin: 6px 0; color: var(--muted); }}
    .stats {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-top: 18px; }}
    .stat {{ background: var(--panel-2); border: 1px solid var(--line); border-radius: 14px; padding: 14px; }}
    .stat .k {{ color: var(--muted); font-size: 12px; }}
    .stat .v {{ margin-top: 8px; font-size: 24px; font-weight: 700; }}
    .source-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin-bottom: 18px; }}
    .source-card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 16px; padding: 16px; }}
    .source-card h2 {{ margin: 0 0 10px; font-size: 18px; }}
    .source-card p {{ margin: 6px 0; color: var(--muted); }}
    .good {{ color: var(--good); font-weight: 700; }}
    .controls {{ display: grid; grid-template-columns: 1.8fr 1fr 1fr 1fr; gap: 12px; margin-bottom: 14px; }}
    .controls input, .controls select {{
      width: 100%;
      padding: 12px 14px;
      border-radius: 10px;
      border: 1px solid var(--line);
      background: var(--panel-2);
      color: var(--text);
    }}
    .panel {{ overflow: hidden; }}
    .toolbar {{ display: flex; justify-content: space-between; align-items: center; color: var(--muted); font-size: 13px; margin-bottom: 10px; }}
    .toolbar-wrap {{ margin-bottom: 8px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    thead th {{
      position: sticky;
      top: 0;
      background: #172540;
      padding: 12px 10px;
      text-align: left;
      font-size: 13px;
      border-bottom: 1px solid var(--line);
    }}
    tbody td {{
      padding: 12px 10px;
      border-bottom: 1px solid rgba(41, 65, 111, 0.65);
      font-size: 14px;
      vertical-align: top;
    }}
    tbody tr:hover {{ background: rgba(156, 194, 255, 0.06); }}
    .chip {{
      display: inline-block;
      padding: 3px 8px;
      border-radius: 999px;
      background: var(--chip);
      font-size: 12px;
    }}
    .chip.new {{ background: #234f3c; color: #dffff1; }}
    .chip.old {{ background: #4e3d1f; color: #ffe7b5; }}
    .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
    @media (max-width: 1100px) {{
      .stats, .source-grid, .controls {{ grid-template-columns: 1fr; }}
      .wrap {{ padding: 14px; }}
      .panel {{ overflow-x: auto; }}
      table {{ min-width: 1100px; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>鸣潮增量刷新汇总</h1>
      <p>这是每次抓取后的最终 HTML 产物，直接汇总三平台当前增量页、已见基线去重结果，以及新增条数。</p>
      <p style="font-size:12px;">生成时间：{generated_at}</p>
      <div class="stats">
        <div class="stat"><div class="k">本次新增总数</div><div class="v good">{total_new}</div></div>
        <div class="stat"><div class="k">本次抓取总量</div><div class="v">{total_batch}</div></div>
        <div class="stat"><div class="k">平台数</div><div class="v">{len(sources)}</div></div>
        <div class="stat"><div class="k">最终交付</div><div class="v">HTML</div></div>
      </div>
    </section>

    <section class="source-grid">
      {"".join(
          f'''
      <div class="source-card">
        <h2>{item["platform_title"]}</h2>
        <p>抓取时间：<span class="mono">{item["captured_at"] or "-"}</span></p>
        <p>本页抓取：<strong>{item["batch_count"]}</strong> 条</p>
        <p>新增：<span class="good">{item["new_count"]}</span> 条，已存在：{item["existing_count"]}</p>
        <p>来源文件：<span class="mono">{Path(item["file_path"]).name}</span></p>
      </div>'''
          for item in sources
      )}
    </section>

    <section class="controls">
      <input id="searchInput" placeholder="搜索：平台 / 商品 ID / 时间文案" />
      <select id="platformFilter">
        <option value="all">全部平台</option>
        <option value="kejinshou">Kejinshou</option>
        <option value="7881">7881</option>
        <option value="pzds">PZDS</option>
      </select>
      <select id="newFilter">
        <option value="all">全部记录</option>
        <option value="new">仅看新增</option>
        <option value="existing">仅看已存在</option>
      </select>
      <select id="sortField">
        <option value="platform_rank">按平台内排名</option>
        <option value="price_desc">按价格降序</option>
        <option value="price_asc">按价格升序</option>
      </select>
    </section>

    <div class="toolbar-wrap">
      <div class="toolbar">
        <div id="resultCount"></div>
        <div>新增记录已高亮标记</div>
      </div>
    </div>

    <section class="panel">
      <table>
        <thead>
          <tr>
            <th>平台</th>
            <th>平台内排名</th>
            <th>商品 ID</th>
            <th>状态</th>
            <th>价格</th>
            <th>绝对时间</th>
            <th>时间文案</th>
            <th>详情</th>
          </tr>
        </thead>
        <tbody id="tableBody"></tbody>
      </table>
    </section>
  </div>

  <script>
    const DATA = {data_json};
    const SOURCES = {source_json};
    const state = {{
      keyword: "",
      platform: "all",
      newFilter: "all",
      sortField: "platform_rank",
    }};

    const el = {{
      searchInput: document.getElementById("searchInput"),
      platformFilter: document.getElementById("platformFilter"),
      newFilter: document.getElementById("newFilter"),
      sortField: document.getElementById("sortField"),
      resultCount: document.getElementById("resultCount"),
      tableBody: document.getElementById("tableBody"),
    }};

    function platformName(platform) {{
      if (platform === "kejinshou") return "Kejinshou";
      if (platform === "7881") return "7881";
      return "PZDS";
    }}

    function searchable(row) {{
      return [
        row.platform,
        platformName(row.platform),
        row.product_id,
        row.listing_time || "",
        row.listing_desc || "",
      ].join(" ").toLowerCase();
    }}

    function numericPrice(value) {{
      const num = Number(String(value).replace(/[^\d.]/g, ""));
      return Number.isFinite(num) ? num : 0;
    }}

    function filteredRows() {{
      let rows = DATA.slice();
      const keyword = state.keyword.trim().toLowerCase();
      if (keyword) rows = rows.filter(row => searchable(row).includes(keyword));
      if (state.platform !== "all") rows = rows.filter(row => row.platform === state.platform);
      if (state.newFilter === "new") rows = rows.filter(row => row.new_by_id);
      if (state.newFilter === "existing") rows = rows.filter(row => !row.new_by_id);

      rows.sort((a, b) => {{
        if (state.sortField === "price_desc") return numericPrice(b.price) - numericPrice(a.price) || a.rank - b.rank;
        if (state.sortField === "price_asc") return numericPrice(a.price) - numericPrice(b.price) || a.rank - b.rank;
        const platformOrder = {{ kejinshou: 0, "7881": 1, pzds: 2 }};
        return (platformOrder[a.platform] - platformOrder[b.platform]) || (a.rank - b.rank);
      }});
      return rows;
    }}

    function render() {{
      const rows = filteredRows();
      el.resultCount.textContent = `当前展示 ${{rows.length}} 条`;
      el.tableBody.innerHTML = rows.map(row => {{
        const badge = row.new_by_id
          ? '<span class="chip new">新增</span>'
          : '<span class="chip old">已存在</span>';
        const link = row.detail_url
          ? `<a href="${{row.detail_url}}" target="_blank" rel="noreferrer">打开</a>`
          : '<span style="color:#9cb0d9;">-</span>';
        return `
          <tr>
            <td>${{platformName(row.platform)}}</td>
            <td>${{row.rank}}</td>
            <td class="mono">${{row.product_id || "-"}}</td>
            <td>${{badge}}</td>
            <td>${{row.price || "-"}}</td>
            <td>${{row.listing_time || "-"}}</td>
            <td>${{row.listing_desc || "-"}}</td>
            <td>${{link}}</td>
          </tr>
        `;
      }}).join("");
    }}

    el.searchInput.addEventListener("input", event => {{
      state.keyword = event.target.value;
      render();
    }});
    el.platformFilter.addEventListener("change", event => {{
      state.platform = event.target.value;
      render();
    }});
    el.newFilter.addEventListener("change", event => {{
      state.newFilter = event.target.value;
      render();
    }});
    el.sortField.addEventListener("change", event => {{
      state.sortField = event.target.value;
      render();
    }});

    render();
  </script>
</body>
</html>
"""


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    output_path = base_dir / "outputs" / "wuwa_incremental_refresh_latest.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sources, rows = _load_sources(base_dir)
    output_path.write_text(_render_html(sources=sources, rows=rows), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
