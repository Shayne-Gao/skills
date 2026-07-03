import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _html_template(rows: List[Dict[str, Any]], meta: Dict[str, Any]) -> str:
    data_json = json.dumps(rows, ensure_ascii=False)
    meta_json = json.dumps(meta, ensure_ascii=False)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>PZDS 鸣潮账号评估 Review</title>
  <style>
    :root {{
      --bg: #09111f;
      --panel: #111b2f;
      --panel2: #17233f;
      --line: #2b3d67;
      --text: #eef3ff;
      --muted: #9fb0d6;
      --good: #58d39d;
      --warn: #ffcf6f;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: linear-gradient(180deg,#09111f,#0e1730); color: var(--text); font-family: -apple-system,BlinkMacSystemFont,\"Segoe UI\",sans-serif; }}
    a {{ color: #9cc2ff; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .wrap {{ max-width: 1600px; margin: 0 auto; padding: 24px; }}
    .hero,.table-wrap {{ background: rgba(17,27,47,.95); border: 1px solid var(--line); border-radius: 16px; }}
    .hero {{ padding: 20px 22px; margin-bottom: 18px; }}
    .hero h1 {{ margin: 0 0 8px; font-size: 28px; }}
    .hero p {{ margin: 6px 0; color: var(--muted); }}
    .controls {{ display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr; gap: 12px; margin: 18px 0; }}
    .controls input,.controls select {{ width: 100%; padding: 12px 14px; border-radius: 10px; border: 1px solid var(--line); background: var(--panel2); color: var(--text); }}
    .stats {{ display: grid; grid-template-columns: repeat(5, minmax(0,1fr)); gap: 12px; margin-top: 16px; }}
    .stat {{ background: var(--panel2); border: 1px solid var(--line); border-radius: 12px; padding: 14px; }}
    .stat .k {{ font-size: 12px; color: var(--muted); }}
    .stat .v {{ margin-top: 8px; font-size: 22px; font-weight: 700; }}
    .toolbar {{ display:flex; justify-content:space-between; align-items:center; color: var(--muted); font-size: 13px; margin-bottom: 10px; }}
    .table-wrap {{ overflow: hidden; }}
    table {{ width: 100%; border-collapse: collapse; }}
    thead th {{ position: sticky; top: 0; background: #16213b; color: #d9e3ff; padding: 12px 10px; font-size: 13px; text-align: left; border-bottom: 1px solid var(--line); cursor: pointer; }}
    tbody td {{ padding: 12px 10px; border-bottom: 1px solid rgba(43,61,103,.65); vertical-align: top; font-size: 14px; }}
    tbody tr.main-row:hover {{ background: rgba(156,194,255,.08); }}
    tbody tr.detail-row {{ display:none; background: rgba(255,255,255,.02); }}
    tbody tr.detail-row.open {{ display: table-row; }}
    .rank {{ display:inline-flex; min-width:28px; justify-content:center; border-radius:999px; padding:2px 8px; background:#243761; font-weight:700; }}
    .score {{ color: var(--good); font-weight: 700; }}
    .detail-grid {{ display:grid; grid-template-columns: 1.2fr 1fr 1fr; gap: 16px; padding: 12px 6px 18px; }}
    .card {{ background: var(--panel2); border: 1px solid var(--line); border-radius: 12px; padding: 14px; }}
    .card h3 {{ margin: 0 0 10px; font-size: 14px; }}
    .card p {{ margin: 6px 0; color: var(--muted); line-height: 1.5; }}
    .list {{ display: flex; flex-wrap: wrap; }}
    .chip {{ display:inline-block; margin:0 6px 6px 0; padding:2px 8px; border-radius:999px; background:#243761; font-size:12px; }}
    .chip.t0 {{ background:#6e2b2b; }}
    .chip.t05 {{ background:#7a4f26; }}
    .chip.t1 {{ background:#29507a; }}
    .chip.t2 {{ background:#2b5446; }}
    .chip.status-active {{ background:#245f45; }}
    .chip.status-sold {{ background:#6f2d32; }}
    .chip.status-unknown {{ background:#4e587a; }}
    .core-tags {{ display:flex; flex-wrap:wrap; gap:6px; min-width:180px; }}
    .compact-role-chip {{ display:inline-flex; align-items:center; gap:4px; margin:0; padding:3px 8px; font-weight:600; line-height:1.1; }}
    .weapon-mark {{ font-size:11px; opacity:0.95; }}
    .tier-section {{ margin-bottom: 12px; }}
    .tier-title {{ margin:0 0 8px; font-size:12px; color:#bfcdff; text-transform:uppercase; }}
    .mono {{ font-family: ui-monospace,SFMono-Regular,Menlo,monospace; }}
    @media (max-width: 1100px) {{
      .controls,.stats,.detail-grid {{ grid-template-columns: 1fr; }}
      .wrap {{ padding: 14px; }}
      .table-wrap {{ overflow-x: auto; }}
      table {{ min-width: 1300px; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>PZDS 鸣潮账号评估 Review</h1>
      <p>基于页面滚动采集到的前 100 个账号详情页 HTML，按统一规则计算强度分与性价比分。</p>
      <p class="mono" style="font-size:12px;color:#9fb0d6;">{meta_json}</p>
      <p style="font-size:12px;color:#9fb0d6;">生成时间：{generated_at}</p>
      <div class="stats" id="stats"></div>
    </section>
    <section class="controls">
      <input id="searchInput" placeholder="搜索：ID / 角色名 / 武器名 / 安全描述" />
      <select id="sortField">
        <option value="value_score">按性价比分</option>
        <option value="strength_score">按强度分</option>
        <option value="price">按价格</option>
        <option value="role_score_total">按角色分</option>
        <option value="weapon_score_total">按武器分</option>
        <option value="pulls_total">按抽数分</option>
      </select>
      <select id="sortOrder">
        <option value="desc">降序</option>
        <option value="asc">升序</option>
      </select>
      <select id="topN">
        <option value="100">显示全部</option>
        <option value="20">只看 Top 20</option>
        <option value="50">只看 Top 50</option>
      </select>
      <select id="statusFilter">
        <option value="all">全部状态</option>
        <option value="active">只看在售</option>
        <option value="sold">只看已卖出</option>
        <option value="unknown">只看待确认</option>
      </select>
    </section>
    <div class="toolbar">
      <div id="resultCount"></div>
      <div>点击行展开详情</div>
    </div>
    <section class="table-wrap">
      <table>
        <thead>
          <tr>
            <th data-sort="value_rank">排名</th>
            <th>ID / 链接</th>
            <th data-sort="price">价格</th>
            <th data-sort="level">等级</th>
            <th data-sort="total_yellow">总黄</th>
            <th data-sort="pulls_total">抽数分</th>
            <th data-sort="role_score_total">角色分</th>
            <th data-sort="weapon_score_total">武器分</th>
            <th data-sort="strength_score">强度分</th>
            <th data-sort="value_score">性价比分</th>
            <th>状态</th>
            <th>核心角色</th>
          </tr>
        </thead>
        <tbody id="tableBody"></tbody>
      </table>
    </section>
  </div>
  <script>
    const DATA = {data_json};
    const state = {{ search: "", sortField: "value_score", sortOrder: "desc", topN: 100, statusFilter: "all" }};
    const el = {{
      searchInput: document.getElementById("searchInput"),
      sortField: document.getElementById("sortField"),
      sortOrder: document.getElementById("sortOrder"),
      topN: document.getElementById("topN"),
      statusFilter: document.getElementById("statusFilter"),
      tableBody: document.getElementById("tableBody"),
      resultCount: document.getElementById("resultCount"),
      stats: document.getElementById("stats"),
    }};
    function fmt(n,d=2) {{ return Number(n).toFixed(d); }}
    function marketStatusLabel(row) {{
      return row.market_status === "sold" ? "已卖出" : row.market_status === "active" ? "在售" : "待确认";
    }}
    function marketStatusChip(row) {{
      const cls = row.market_status === "sold" ? "status-sold" : row.market_status === "active" ? "status-active" : "status-unknown";
      return `<span class="chip ${{cls}}">${{marketStatusLabel(row)}}</span>`;
    }}
    function roleTierClass(tier) {{
      return tier === "T0" ? "t0" : tier === "T0.5" ? "t05" : tier === "T1" ? "t1" : tier === "T2" ? "t2" : "";
    }}
    function roleChip(role) {{
      const cls = roleTierClass(role.tier || "");
      const tierLabel = role.tier ? `${{role.tier}}` : role.star;
      return `<span class="chip ${{cls}}">${{role.name}} ${{tierLabel}} ${{role.resonance}}鸣 = ${{fmt(role.score,0)}}</span>`;
    }}
    function signatureOwnerSet(weapons) {{
      return new Set((weapons || []).map(weapon => String(weapon.owner_character || "").trim()).filter(Boolean));
    }}
    function compactRoleSummary(row) {{
      const ownerSet = signatureOwnerSet(row.weapons);
      const tierOrder = {{ "T0": 0, "T0.5": 1, "T1": 2 }};
      const roles = row.roles
        .filter(role => ["T0", "T0.5", "T1"].includes(role.tier || ""))
        .sort((a,b) => {{
          const tierDiff = (tierOrder[a.tier] ?? 99) - (tierOrder[b.tier] ?? 99);
          if (tierDiff) return tierDiff;
          if ((b.score || 0) !== (a.score || 0)) return (b.score || 0) - (a.score || 0);
          return String(a.name).localeCompare(String(b.name), "zh-CN");
        }});
      if (!roles.length) return '<span>-</span>';
      return `<div class="core-tags">${{roles.map(role => {{
        const hasSignature = ownerSet.has(role.name);
        const mark = hasSignature ? '<span class="weapon-mark" title="有专武">🔪</span>' : "";
        const cls = roleTierClass(role.tier || "");
        const title = `${{role.name}} / ${{role.tier || role.star || "-"}} / ${{role.resonance}}共鸣${{hasSignature ? " / 有专武" : ""}}`;
        return `<span class="chip compact-role-chip ${{cls}}" title="${{title}}">${{role.name}}${{role.resonance}} ${{mark}}</span>`;
      }}).join("")}}</div>`;
    }}
    function renderRoleSections(roles) {{
      const groups = [["T0","T0 角色"],["T0.5","T0.5 角色"],["T1","T1 角色"],["T2","T2 角色"],["","未命中梯度"]];
      return groups.map(([tier,title]) => {{
        const list = roles.filter(r => (r.tier || "") === tier).sort((a,b) => (b.score||0)-(a.score||0) || String(a.name).localeCompare(String(b.name), "zh-CN"));
        if (!list.length) return "";
        return `<div class="tier-section"><div class="tier-title">${{title}}</div><div class="list">${{list.map(roleChip).join("")}}</div></div>`;
      }}).join("");
    }}
    function weaponChip(w) {{
      const owner = w.owner_character ? `${{w.owner_character}}/${{w.owner_tier||"未分档"}}` : "常驻";
      return `<span class="chip">${{w.name}} [${{w.weapon_class}}] -> ${{owner}} 显示${{w.refine}}精/计分${{w.effective_refine}}层 = ${{fmt(w.score,0)}}</span>`;
    }}
    function searchable(row) {{
      return [row.product_id, row.summary || "", row.security_summary || "", row.market_status || "", row.roles.map(r => r.name).join(" "), row.weapons.map(w => w.name).join(" ")].join(" ").toLowerCase();
    }}
    function filteredRows() {{
      let rows = DATA.slice();
      const kw = state.search.trim().toLowerCase();
      if (kw) rows = rows.filter(row => searchable(row).includes(kw));
      if (state.statusFilter !== "all") rows = rows.filter(row => (row.market_status || "unknown") === state.statusFilter);
      rows.sort((a,b) => {{
        const av = a[state.sortField], bv = b[state.sortField];
        if (av === bv) return a.value_rank - b.value_rank;
        return state.sortOrder === "desc" ? (bv - av) : (av - bv);
      }});
      return rows.slice(0, state.topN);
    }}
    function buildStats(rows) {{
      const avgValue = rows.reduce((s,x)=>s+x.value_score,0)/(rows.length||1);
      const avgStrength = rows.reduce((s,x)=>s+x.strength_score,0)/(rows.length||1);
      const best = rows[0];
      const cards = [
        {{k:"账号数",v:rows.length}},
        {{k:"平均性价比分",v:fmt(avgValue,3)}},
        {{k:"平均强度分",v:fmt(avgStrength,2)}},
        {{k:"当前第一名",v:best ? `${{best.product_id}} / ${{fmt(best.value_score,3)}}` : "-"}},
        {{k:"已卖出",v:rows.filter(row => row.market_status === "sold").length}}
      ];
      el.stats.innerHTML = cards.map(card => `<div class="stat"><div class="k">${{card.k}}</div><div class="v">${{card.v}}</div></div>`).join("");
    }}
    function render() {{
      const rows = filteredRows();
      buildStats(rows);
      el.resultCount.textContent = `当前展示 ${{rows.length}} 条`;
      el.tableBody.innerHTML = rows.map((row, idx) => {{
        const rid = `detail-${{row.product_id}}-${{idx}}`;
        return `
          <tr class="main-row" data-target="${{rid}}">
            <td><span class="rank">${{idx+1}}</span></td>
            <td><div class="mono">${{row.product_id}}</div><div><a href="${{row.detail_url}}" target="_blank" rel="noreferrer">打开详情页</a></div></td>
            <td>${{fmt(row.price,0)}}</td>
            <td>${{row.level}}</td>
            <td>${{row.total_yellow}}</td>
            <td>${{fmt(row.resources.pulls_total,2)}}</td>
            <td>${{fmt(row.role_score_total,2)}}</td>
            <td>${{fmt(row.weapon_score_total,2)}}</td>
            <td class="score">${{fmt(row.strength_score,2)}}</td>
            <td class="score">${{fmt(row.value_score,3)}}</td>
            <td>${{marketStatusChip(row)}}</td>
            <td>${{compactRoleSummary(row)}}</td>
          </tr>
          <tr class="detail-row" id="${{rid}}">
            <td colspan="12">
              <div class="detail-grid">
                <div class="card">
                  <h3>评分拆解</h3>
                  <p><strong>强度分：</strong>${{fmt(row.strength_score,2)}} = 抽数分 ${{fmt(row.resources.pulls_total,2)}} + 角色分 ${{fmt(row.role_score_total,2)}} + 武器分 ${{fmt(row.weapon_score_total,2)}}</p>
                  <p><strong>性价比分：</strong>${{fmt(row.value_score,3)}}</p>
                  <p><strong>资源：</strong>星声 ${{row.resources.star_voice}} / 浮金 ${{row.resources.fj_waves}} / 唤声 ${{row.resources.hs_waves}} / 铸潮 ${{row.resources.zc_waves}}</p>
                  <p><strong>摘要：</strong>${{row.summary || "-"}}</p>
                  <p><strong>安全信息：</strong>${{row.security_summary || "-"}}</p>
                  <p><strong>在售状态：</strong>${{marketStatusLabel(row)}} <span class="muted">${{row.status_reason || ""}} / ${{row.status_checked_at || "-"}}</span></p>
                </div>
                <div class="card">
                  <h3>角色明细</h3>
                  ${{renderRoleSections(row.roles) || '<span>无角色数据</span>'}}
                </div>
                <div class="card">
                  <h3>武器明细</h3>
                  <div class="list">${{row.weapons.map(weaponChip).join("") || '<span>无武器数据</span>'}}</div>
                </div>
              </div>
            </td>
          </tr>
        `;
      }}).join("");
      document.querySelectorAll(".main-row").forEach(row => {{
        row.addEventListener("click", () => document.getElementById(row.dataset.target).classList.toggle("open"));
      }});
    }}
    el.searchInput.addEventListener("input", e => {{ state.search = e.target.value; render(); }});
    el.sortField.addEventListener("change", e => {{ state.sortField = e.target.value; render(); }});
    el.sortOrder.addEventListener("change", e => {{ state.sortOrder = e.target.value; render(); }});
    el.topN.addEventListener("change", e => {{ state.topN = Number(e.target.value); render(); }});
    el.statusFilter.addEventListener("change", e => {{ state.statusFilter = e.target.value; render(); }});
    document.querySelectorAll("th[data-sort]").forEach(th => {{
      th.addEventListener("click", () => {{
        const f = th.dataset.sort;
        if (state.sortField === f) state.sortOrder = state.sortOrder === "desc" ? "asc" : "desc";
        else state.sortField = f;
        el.sortField.value = state.sortField;
        el.sortOrder.value = state.sortOrder;
        render();
      }});
    }});
    render();
  </script>
</body>
</html>
"""


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    src = base_dir / "outputs" / "pzds_wuwa_top100_scored.json"
    out = base_dir / "outputs" / "pzds_wuwa_top100_review.html"
    obj = _load_json(src)
    out.write_text(_html_template(obj["items"], obj["meta"]), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
