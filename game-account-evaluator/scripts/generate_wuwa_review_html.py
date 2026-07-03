import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


DETAIL_BASE_URL = "https://m.kejinshou.com/goods/details/"


def _read_scored_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _load_normalized(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _build_rows(scored_rows: List[Dict[str, str]], normalized_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized_map = {str(item["product_id"]): item for item in normalized_items}
    rows: List[Dict[str, Any]] = []
    for row in scored_rows:
        product_id = str(row["product_id"])
        asset = normalized_map.get(product_id, {})
        detail_url = f"{DETAIL_BASE_URL}{product_id}"
        rows.append(
            {
                "rank": int(row["rank"]),
                "product_id": product_id,
                "detail_url": detail_url,
                "price": float(row["price"]),
                "upper_at": asset.get("upper_at", ""),
                "polish_time_desc": asset.get("polish_time_desc", ""),
                "level": int(row["level"]),
                "total_yellow": int(row["total_yellow"]),
                "pulls_total": float(row["pulls_total"]),
                "role_score_total": float(row["role_score_total"]),
                "weapon_score_total": float(row["weapon_score_total"]),
                "strength_score": float(row["strength_score"]),
                "value_score": float(row["value_score"]),
                "matched_tier_roles": int(row["matched_tier_roles"]),
                "unmatched_roles_count": int(row["unmatched_roles_count"]),
                "tier_breakdown": row["tier_breakdown"],
                "weapon_breakdown": row.get("weapon_breakdown", ""),
                "sub_title": asset.get("sub_title", ""),
                "resources": asset.get("resources", {}),
                "roles": asset.get("roles", []),
                "weapons": asset.get("weapons", []),
                "weapon_score_total_exact": asset.get("weapon_score_total", 0),
                "market_status": asset.get("market_status", "unknown"),
                "is_sold": bool(asset.get("is_sold", False)),
                "status_reason": asset.get("status_reason", ""),
                "status_checked_at": asset.get("status_checked_at", ""),
            }
        )
    return rows


def _html_template(rows: List[Dict[str, Any]], meta: Dict[str, Any]) -> str:
    data_json = json.dumps(rows, ensure_ascii=False)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    meta_json = json.dumps(meta, ensure_ascii=False)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>鸣潮账号评估 Review</title>
  <style>
    :root {{
      --bg: #0b1020;
      --panel: #121933;
      --panel-2: #182140;
      --line: #2b3560;
      --text: #e9edff;
      --muted: #9aa6d1;
      --accent: #7aa2ff;
      --good: #44d19f;
      --warn: #ffca5c;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: linear-gradient(180deg, #0b1020 0%, #0f1630 100%);
      color: var(--text);
    }}
    a {{ color: #9ec1ff; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .wrap {{ max-width: 1600px; margin: 0 auto; padding: 24px; }}
    .hero {{
      background: rgba(18, 25, 51, 0.92);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 20px 22px;
      margin-bottom: 20px;
    }}
    .hero h1 {{ margin: 0 0 8px; font-size: 28px; }}
    .hero p {{ margin: 6px 0; color: var(--muted); line-height: 1.5; }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 12px;
      margin: 18px 0 8px;
    }}
    .stat {{
      background: var(--panel-2);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 14px;
    }}
    .stat .k {{ color: var(--muted); font-size: 12px; }}
    .stat .v {{ margin-top: 8px; font-size: 22px; font-weight: 700; }}
    .controls {{
      display: grid;
      grid-template-columns: 2fr 1fr 1fr 1fr 1fr 2fr;
      gap: 12px;
      margin: 20px 0;
    }}
    .controls input, .controls select {{
      width: 100%;
      background: var(--panel);
      color: var(--text);
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 12px 14px;
      font-size: 14px;
    }}
    .role-filter {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 10px 12px;
      min-height: 46px;
    }}
    .role-filter summary {{
      cursor: pointer;
      color: var(--text);
      list-style: none;
      outline: none;
    }}
    .role-filter summary::-webkit-details-marker {{ display: none; }}
    .role-filter-panel {{
      margin-top: 10px;
      max-height: 260px;
      overflow: auto;
      border-top: 1px solid var(--line);
      padding-top: 10px;
    }}
    .role-filter-actions {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
      color: var(--muted);
      font-size: 12px;
    }}
    .role-filter-actions button {{
      background: #22315b;
      color: var(--text);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 4px 8px;
      cursor: pointer;
    }}
    .role-options {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 6px 10px;
    }}
    .role-option {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      color: #dfe6ff;
    }}
    .table-wrap {{
      background: rgba(18, 25, 51, 0.92);
      border: 1px solid var(--line);
      border-radius: 16px;
      overflow: hidden;
    }}
    table {{ width: 100%; border-collapse: collapse; }}
    thead th {{
      position: sticky;
      top: 0;
      background: #162041;
      color: #cbd6ff;
      font-size: 13px;
      text-align: left;
      padding: 12px 10px;
      border-bottom: 1px solid var(--line);
      cursor: pointer;
      white-space: nowrap;
    }}
    tbody td {{
      padding: 12px 10px;
      border-bottom: 1px solid rgba(43, 53, 96, 0.65);
      font-size: 14px;
      vertical-align: top;
    }}
    tbody tr.main-row:hover {{ background: rgba(122, 162, 255, 0.08); }}
    tbody tr.detail-row {{ display: none; background: rgba(255, 255, 255, 0.02); }}
    tbody tr.detail-row.open {{ display: table-row; }}
    .rank {{
      display: inline-flex;
      min-width: 28px;
      justify-content: center;
      border-radius: 999px;
      padding: 2px 8px;
      background: #24315d;
      color: #dfe7ff;
      font-weight: 700;
    }}
    .score {{ color: var(--good); font-weight: 700; }}
    .muted {{ color: var(--muted); }}
    .chip {{
      display: inline-block;
      padding: 2px 8px;
      margin: 0 6px 6px 0;
      border-radius: 999px;
      background: #22315b;
      color: #e5ebff;
      font-size: 12px;
    }}
    .chip.t0 {{ background: #6b2d2d; }}
    .chip.t05 {{ background: #77502b; }}
    .chip.t1 {{ background: #274c79; }}
    .chip.t2 {{ background: #2c4c44; }}
    .chip.t3 {{ background: #444b63; }}
    .chip.t4 {{ background: #3f3f3f; }}
    .chip.status-active {{ background: #245f45; }}
    .chip.status-sold {{ background: #6f2d32; }}
    .chip.status-unknown {{ background: #4e587a; }}
    .core-tags {{ display: flex; flex-wrap: wrap; gap: 6px; min-width: 180px; }}
    .compact-role-chip {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      margin: 0;
      padding: 3px 8px;
      font-weight: 600;
      line-height: 1.1;
    }}
    .weapon-mark {{ font-size: 11px; opacity: 0.95; }}
    .detail-panel {{
      display: grid;
      grid-template-columns: 1.3fr 1fr 1fr;
      gap: 16px;
      padding: 12px 6px 18px;
    }}
    .card {{
      background: var(--panel-2);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 14px;
    }}
    .card h3 {{
      margin: 0 0 10px;
      font-size: 14px;
      color: #dfe6ff;
    }}
    .card p {{
      margin: 6px 0;
      color: var(--muted);
      line-height: 1.5;
    }}
    .list {{ display: flex; flex-wrap: wrap; }}
    .tier-section {{ margin-bottom: 12px; }}
    .tier-title {{
      margin: 0 0 8px;
      font-size: 12px;
      color: #b9c7ff;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}
    .toolbar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin: 10px 0 14px;
      color: var(--muted);
      font-size: 13px;
    }}
    .small {{ font-size: 12px; color: var(--muted); }}
    .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
    @media (max-width: 1100px) {{
      .controls, .stats, .detail-panel {{
        grid-template-columns: 1fr;
      }}
      .wrap {{ padding: 14px; }}
      .table-wrap {{ overflow-x: auto; }}
      table {{ min-width: 1300px; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>鸣潮账号评估 Review</h1>
      <p>用于整体 review 当前 200 个账号的强度分、性价比分、角色命中、武器映射，以及详情页直达链接。</p>
      <p>角色分采用三榜合成：综合榜 + 逆境深塔 + 冥歌海墟，并强调 T0 / T0.5 的保值率。</p>
      <p class="small">生成时间：{generated_at}</p>
      <p class="small mono">评分参数：{meta_json}</p>
      <div class="stats" id="stats"></div>
    </section>

    <section class="controls">
      <input id="searchInput" placeholder="搜索：ID / 角色名 / 武器名 / 文案" />
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
      <select id="statusFilter">
        <option value="all">全部状态</option>
        <option value="active">只看在售</option>
        <option value="sold">只看已卖出</option>
        <option value="unknown">只看待确认</option>
      </select>
      <select id="topN">
        <option value="200">显示全部</option>
        <option value="20">只看 Top 20</option>
        <option value="50">只看 Top 50</option>
        <option value="100">只看 Top 100</option>
      </select>
      <details class="role-filter" id="roleFilterBox">
        <summary id="roleFilterSummary">按角色筛选：未选择</summary>
        <div class="role-filter-panel">
          <div class="role-filter-actions">
            <span>勾选后只显示同时拥有所选角色的账号</span>
            <button type="button" id="clearRoleFilter">清空</button>
          </div>
          <div class="role-options" id="roleOptions"></div>
        </div>
      </details>
    </section>

    <div class="toolbar">
      <div id="resultCount"></div>
      <div>点击任意行展开详细资产与评分拆解</div>
    </div>

    <section class="table-wrap">
      <table>
        <thead>
          <tr>
            <th data-sort="rank">排名</th>
            <th>ID / 链接</th>
            <th data-sort="price">价格</th>
            <th>上架时间</th>
            <th data-sort="level">等级</th>
            <th data-sort="total_yellow">总黄</th>
            <th data-sort="pulls_total">抽数分</th>
            <th data-sort="role_score_total">角色分</th>
            <th data-sort="weapon_score_total">武器分</th>
            <th data-sort="strength_score">强度分</th>
            <th data-sort="value_score">性价比分</th>
            <th>状态</th>
            <th>核心角色</th>
            <th>梯度命中</th>
          </tr>
        </thead>
        <tbody id="tableBody"></tbody>
      </table>
    </section>
  </div>

  <script>
    const DATA = {data_json};
    const META = {meta_json};

    const state = {{
      search: "",
      sortField: "value_score",
      sortOrder: "desc",
      topN: 200,
      statusFilter: "all",
      selectedRoles: []
    }};

    const el = {{
      stats: document.getElementById("stats"),
      searchInput: document.getElementById("searchInput"),
      sortField: document.getElementById("sortField"),
      sortOrder: document.getElementById("sortOrder"),
      topN: document.getElementById("topN"),
      statusFilter: document.getElementById("statusFilter"),
      roleFilterSummary: document.getElementById("roleFilterSummary"),
      roleOptions: document.getElementById("roleOptions"),
      clearRoleFilter: document.getElementById("clearRoleFilter"),
      tableBody: document.getElementById("tableBody"),
      resultCount: document.getElementById("resultCount"),
    }};
    const ROLE_OPTIONS = Array.from(new Set(DATA.flatMap(row => row.roles.map(role => role.name)))).sort((a, b) => a.localeCompare(b, "zh-CN"));

    function fmt(num, digits = 2) {{
      return Number(num).toFixed(digits);
    }}

    function marketStatusLabel(row) {{
      return row.market_status === "sold" ? "已卖出" : row.market_status === "active" ? "在售" : "待确认";
    }}

    function marketStatusChip(row) {{
      const cls = row.market_status === "sold" ? "status-sold" : row.market_status === "active" ? "status-active" : "status-unknown";
      return `<span class="chip ${{cls}}">${{marketStatusLabel(row)}}</span>`;
    }}

    function roleChip(role) {{
      const tier = role.tier || "NA";
      const cls = roleTierClass(tier);
      const label = role.tier
        ? `${{role.name}} ${{role.tier}} ${{role.resonance}}鸣 = ${{fmt(role.score, 0)}} | 综${{role.overall_tier || "-"}} / 塔${{role.tower_grade || "-"}} / 冥${{role.requiem_grade || "-"}}`
        : `${{role.name}} ${{role.star}} ${{role.resonance}}鸣`;
      return `<span class="chip ${{cls}}">${{label}}</span>`;
    }}

    function roleTierClass(tier) {{
      return tier === "T0"
        ? "t0"
        : tier === "T0.5"
        ? "t05"
        : tier === "T1"
        ? "t1"
        : tier === "T2"
        ? "t2"
        : tier === "T3"
        ? "t3"
        : "t4";
    }}

    function signatureOwnerSet(weapons) {{
      return new Set((weapons || []).map(weapon => String(weapon.owner_character || "").trim()).filter(Boolean));
    }}

    function compactRoleSummary(row) {{
      const ownerSet = signatureOwnerSet(row.weapons);
      const tierOrder = {{ "T0": 0, "T0.5": 1, "T1": 2 }};
      const roles = row.roles
        .filter(role => ["T0", "T0.5", "T1"].includes(role.tier || ""))
        .sort((a, b) => {{
          const tierDiff = (tierOrder[a.tier] ?? 99) - (tierOrder[b.tier] ?? 99);
          if (tierDiff) return tierDiff;
          if ((b.score || 0) !== (a.score || 0)) return (b.score || 0) - (a.score || 0);
          return String(a.name).localeCompare(String(b.name), "zh-CN");
        }});
      if (!roles.length) return '<span class="muted">-</span>';
      return `<div class="core-tags">${{roles.map(role => {{
        const hasSignature = ownerSet.has(role.name);
        const cls = roleTierClass(role.tier || "");
        const mark = hasSignature ? '<span class="weapon-mark" title="有专武">🔪</span>' : "";
        const title = `${{role.name}} / ${{role.tier || role.star || "-"}} / ${{role.resonance}}共鸣${{hasSignature ? " / 有专武" : ""}}`;
        return `<span class="chip compact-role-chip ${{cls}}" title="${{title}}">${{role.name}}${{role.resonance}} ${{mark}}</span>`;
      }}).join("")}}</div>`;
    }}

    function renderRoleSections(roles) {{
      const groups = [
        ["T0", "T0 角色"],
        ["T0.5", "T0.5 角色"],
        ["T1", "T1 角色"],
        ["T2", "T2 角色"],
        ["T3", "T3 角色"],
        ["T4", "T4 角色"],
        ["", "未命中梯度"]
      ];
      return groups.map(([tier, title]) => {{
        const list = roles
          .filter(role => (role.tier || "") === tier)
          .sort((a, b) => {{
            if ((b.score || 0) !== (a.score || 0)) return (b.score || 0) - (a.score || 0);
            return String(a.name).localeCompare(String(b.name), "zh-CN");
          }});
        if (!list.length) return "";
        return `
          <div class="tier-section">
            <div class="tier-title">${{title}}</div>
            <div class="list">${{list.map(roleChip).join("")}}</div>
          </div>
        `;
      }}).join("");
    }}

    function weaponChip(weapon) {{
      const owner = weapon.owner_character ? `${{weapon.owner_character}}/${{weapon.owner_tier || "未分档"}}` : "常驻";
      const refine = `显示${{weapon.resonance}}鸣/计分${{weapon.effective_refine}}层`;
      const label = `${{weapon.name}} [${{weapon.weapon_class}}] -> ${{owner}} ${{refine}} = ${{fmt(weapon.score, 0)}}`;
      return `<span class="chip">${{label}}</span>`;
    }}

    function buildStats(rows) {{
      const best = rows[0] || null;
      const avgValue = rows.length ? rows.reduce((s, x) => s + x.value_score, 0) / rows.length : 0;
      const avgScore = rows.length ? rows.reduce((s, x) => s + x.strength_score, 0) / rows.length : 0;
      const cards = [
        {{ k: "账号数", v: rows.length }},
        {{ k: "平均性价比分", v: fmt(avgValue, 3) }},
        {{ k: "平均强度分", v: fmt(avgScore, 2) }},
        {{ k: "当前第一名", v: best ? `${{best.product_id}} / ${{fmt(best.value_score, 3)}}` : "-" }},
        {{ k: "已卖出", v: rows.filter(row => row.market_status === "sold").length }},
      ];
      el.stats.innerHTML = cards.map(card => `
        <div class="stat">
          <div class="k">${{card.k}}</div>
          <div class="v">${{card.v}}</div>
        </div>
      `).join("");
    }}

    function searchableText(row) {{
      const roleText = row.roles.map(x => x.name).join(" ");
      const weaponText = row.weapons.map(x => x.name).join(" ");
      return [
        row.product_id,
        row.sub_title,
        row.upper_at || "",
        row.polish_time_desc || "",
        row.market_status || "",
        row.tier_breakdown,
        roleText,
        weaponText
      ].join(" ").toLowerCase();
    }}

    function renderRoleFilter() {{
      el.roleOptions.innerHTML = ROLE_OPTIONS.map(role => {{
        const checked = state.selectedRoles.includes(role) ? "checked" : "";
        return `<label class="role-option"><input type="checkbox" value="${{role}}" ${{checked}} /> <span>${{role}}</span></label>`;
      }}).join("");
      const label = state.selectedRoles.length
        ? `按角色筛选：已选 ${{state.selectedRoles.length}} 个`
        : "按角色筛选：未选择";
      el.roleFilterSummary.textContent = label;
      el.roleOptions.querySelectorAll('input[type="checkbox"]').forEach(input => {{
        input.addEventListener("change", e => {{
          const value = e.target.value;
          if (e.target.checked) {{
            state.selectedRoles = [...state.selectedRoles, value].sort((a, b) => a.localeCompare(b, "zh-CN"));
          }} else {{
            state.selectedRoles = state.selectedRoles.filter(role => role !== value);
          }}
          render();
        }});
      }});
    }}

    function filteredRows() {{
      const kw = state.search.trim().toLowerCase();
      let rows = DATA.slice();
      if (kw) {{
        rows = rows.filter(row => searchableText(row).includes(kw));
      }}
      if (state.selectedRoles.length) {{
        rows = rows.filter(row => {{
          const roleSet = new Set(row.roles.map(role => role.name));
          return state.selectedRoles.every(role => roleSet.has(role));
        }});
      }}
      if (state.statusFilter !== "all") {{
        rows = rows.filter(row => (row.market_status || "unknown") === state.statusFilter);
      }}
      rows.sort((a, b) => {{
        const av = a[state.sortField];
        const bv = b[state.sortField];
        if (av === bv) return a.rank - b.rank;
        return state.sortOrder === "desc" ? (bv - av) : (av - bv);
      }});
      return rows.slice(0, state.topN);
    }}

    function render() {{
      const rows = filteredRows();
      buildStats(rows);
      el.resultCount.textContent = `当前展示 ${{rows.length}} 条`;

      el.tableBody.innerHTML = rows.map((row, idx) => {{
        const rid = `detail-${{row.product_id}}-${{idx}}`;
        const fiveStarWeapons = row.weapons.filter(x => x.star === "五星");
        return `
          <tr class="main-row" data-target="${{rid}}">
            <td><span class="rank">${{idx + 1}}</span></td>
            <td>
              <div class="mono">${{row.product_id}}</div>
              <div><a href="${{row.detail_url}}" target="_blank" rel="noreferrer">打开详情页</a></div>
            </td>
            <td>${{fmt(row.price, 0)}}</td>
            <td>${{row.upper_at || "-"}}<div class="muted">${{row.polish_time_desc || "-"}}</div></td>
            <td>${{row.level}}</td>
            <td>${{row.total_yellow}}</td>
            <td>${{fmt(row.pulls_total, 2)}}</td>
            <td>${{fmt(row.role_score_total, 2)}}</td>
            <td>${{fmt(row.weapon_score_total, 2)}}</td>
            <td class="score">${{fmt(row.strength_score, 2)}}</td>
            <td class="score">${{fmt(row.value_score, 3)}}</td>
            <td>${{marketStatusChip(row)}}</td>
            <td>${{compactRoleSummary(row)}}</td>
            <td>${{row.matched_tier_roles}} 命中 / ${{row.unmatched_roles_count}} 未命中</td>
          </tr>
          <tr class="detail-row" id="${{rid}}">
            <td colspan="14">
              <div class="detail-panel">
                <div class="card">
                  <h3>评分拆解</h3>
                  <p><strong>强度分：</strong>${{fmt(row.strength_score, 2)}} = 抽数分 ${{fmt(row.pulls_total, 2)}} + 角色分 ${{fmt(row.role_score_total, 2)}} + 武器分 ${{fmt(row.weapon_score_total, 2)}}</p>
                  <p><strong>性价比分：</strong>${{fmt(row.value_score, 3)}} = 强度分 / 价格</p>
                  <p><strong>资源：</strong>星声 ${{row.resources.star_voice || 0}} / 浮金 ${{row.resources.fj_waves || 0}} / 铸潮 ${{row.resources.zc_waves || 0}} / 唤声 ${{row.resources.hs_waves || 0}}</p>
                  <p><strong>详情页：</strong><a href="${{row.detail_url}}" target="_blank" rel="noreferrer">${{row.detail_url}}</a></p>
                  <p><strong>上架时间：</strong>${{row.upper_at || "-"}} <span class="muted">${{row.polish_time_desc || ""}}</span></p>
                  <p><strong>在售状态：</strong>${{marketStatusLabel(row)}} <span class="muted">${{row.status_reason || ""}} / ${{row.status_checked_at || "-"}}</span></p>
                  <p><strong>卖家摘要：</strong><span class="muted">${{row.sub_title || "-"}}</span></p>
                  <p><strong>角色基准：</strong><span class="muted">综合榜 0.4 + 深塔 0.3 + 冥歌 0.3；T0=120，T0.5=90，T1=40，T2=10</span></p>
                  <p><strong>武器拆解：</strong><span class="muted">${{row.weapon_breakdown || "-"}}</span></p>
                </div>
                <div class="card">
                  <h3>角色明细</h3>
                  ${{renderRoleSections(row.roles) || '<span class="muted">无角色数据</span>'}}
                </div>
                <div class="card">
                  <h3>武器明细</h3>
                  <p><strong>五星武器数：</strong>${{fiveStarWeapons.length}}，专武按角色梯度计分，常驻统一 20 分</p>
                  <div class="list">${{row.weapons.map(weaponChip).join("") || '<span class="muted">无武器数据</span>'}}</div>
                </div>
              </div>
            </td>
          </tr>
        `;
      }}).join("");

      document.querySelectorAll(".main-row").forEach(row => {{
        row.addEventListener("click", () => {{
          const target = document.getElementById(row.dataset.target);
          target.classList.toggle("open");
        }});
      }});
    }}

    el.searchInput.addEventListener("input", e => {{
      state.search = e.target.value;
      render();
    }});
    el.sortField.addEventListener("change", e => {{
      state.sortField = e.target.value;
      render();
    }});
    el.sortOrder.addEventListener("change", e => {{
      state.sortOrder = e.target.value;
      render();
    }});
    el.statusFilter.addEventListener("change", e => {{
      state.statusFilter = e.target.value;
      render();
    }});
    el.topN.addEventListener("change", e => {{
      state.topN = Number(e.target.value);
      render();
    }});
    el.clearRoleFilter.addEventListener("click", () => {{
      state.selectedRoles = [];
      render();
    }});

    document.querySelectorAll("th[data-sort]").forEach(th => {{
      th.addEventListener("click", () => {{
        const field = th.dataset.sort;
        if (state.sortField === field) {{
          state.sortOrder = state.sortOrder === "desc" ? "asc" : "desc";
          el.sortOrder.value = state.sortOrder;
        }} else {{
          state.sortField = field;
          el.sortField.value = field;
        }}
        render();
      }});
    }});

    renderRoleFilter();
    render();
  </script>
</body>
</html>
"""


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    scored_csv = base_dir / "outputs" / "wuwa_top200_role_tier_scored.csv"
    normalized_json = base_dir / "outputs" / "wuwa_top200_normalized_assets.json"
    out_path = base_dir / "outputs" / "wuwa_top200_review.html"

    scored_rows = _read_scored_csv(scored_csv)
    normalized = _load_normalized(normalized_json)
    rows = _build_rows(scored_rows, normalized["items"])
    meta = normalized.get("meta", {}).get("scoring", {})
    out_path.write_text(_html_template(rows, meta), encoding="utf-8")
    print(out_path)


if __name__ == "__main__":
    main()
