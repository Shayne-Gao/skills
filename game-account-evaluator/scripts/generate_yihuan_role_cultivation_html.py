import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def _load_data(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _html_template(payload: Dict[str, Any]) -> str:
    data_json = json.dumps(payload, ensure_ascii=False)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>异环 角色培养指南</title>
  <style>
    :root {{
      --bg: #09111f;
      --bg-2: #0d1630;
      --panel: rgba(15, 24, 46, 0.92);
      --panel-2: rgba(20, 31, 58, 0.92);
      --line: #24335a;
      --text: #edf2ff;
      --muted: #98a6cf;
      --accent: #83a7ff;
      --accent-2: #71e0be;
      --warn: #f5c56a;
      --shadow: 0 18px 60px rgba(0, 0, 0, 0.28);
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(131, 167, 255, 0.16), transparent 28%),
        radial-gradient(circle at top right, rgba(113, 224, 190, 0.12), transparent 24%),
        linear-gradient(180deg, var(--bg) 0%, var(--bg-2) 100%);
    }}
    a {{ color: #aac4ff; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .wrap {{ max-width: 1440px; margin: 0 auto; padding: 24px; }}
    .hero {{
      background: linear-gradient(180deg, rgba(17, 28, 53, 0.94), rgba(12, 20, 40, 0.92));
      border: 1px solid var(--line);
      border-radius: 20px;
      padding: 26px;
      box-shadow: var(--shadow);
    }}
    .hero-top {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 16px;
      margin-bottom: 16px;
    }}
    .hero h1 {{
      margin: 0 0 8px;
      font-size: 34px;
      line-height: 1.15;
    }}
    .hero p {{
      margin: 8px 0;
      color: var(--muted);
      line-height: 1.6;
    }}
    .hero-badges {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 14px;
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: rgba(34, 49, 91, 0.88);
      color: #e7edff;
      font-size: 13px;
    }}
    .badge.accent {{
      background: rgba(43, 84, 170, 0.26);
      border-color: rgba(131, 167, 255, 0.5);
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-top: 18px;
    }}
    .stat {{
      background: var(--panel-2);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 14px 16px;
    }}
    .stat .k {{
      font-size: 12px;
      color: var(--muted);
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}
    .stat .v {{
      margin-top: 8px;
      font-size: 24px;
      font-weight: 700;
    }}
    .layout {{
      display: grid;
      grid-template-columns: 300px minmax(0, 1fr);
      gap: 18px;
      margin-top: 18px;
      align-items: start;
    }}
    .sidebar {{
      position: sticky;
      top: 18px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
      box-shadow: var(--shadow);
    }}
    .sidebar h2 {{
      margin: 0 0 12px;
      font-size: 16px;
    }}
    .field {{
      margin-bottom: 14px;
    }}
    .field label {{
      display: block;
      margin-bottom: 6px;
      color: var(--muted);
      font-size: 13px;
    }}
    .field input, .field select {{
      width: 100%;
      padding: 11px 12px;
      border-radius: 10px;
      border: 1px solid var(--line);
      background: rgba(8, 14, 28, 0.7);
      color: var(--text);
      font-size: 14px;
    }}
    .checks {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .check-chip {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 8px 10px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: rgba(16, 25, 48, 0.82);
      font-size: 13px;
      color: #dfe7ff;
    }}
    .check-chip input {{ margin: 0; }}
    .sidebar-actions {{
      display: flex;
      gap: 10px;
      margin-top: 8px;
    }}
    .btn {{
      flex: 1;
      padding: 10px 12px;
      border-radius: 10px;
      border: 1px solid var(--line);
      background: rgba(34, 49, 91, 0.92);
      color: var(--text);
      cursor: pointer;
      font-size: 14px;
    }}
    .btn:hover {{ background: rgba(45, 66, 120, 0.96); }}
    .result-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin-bottom: 14px;
      color: var(--muted);
      font-size: 13px;
    }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
      box-shadow: var(--shadow);
    }}
    .card-head {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: flex-start;
      margin-bottom: 14px;
    }}
    .card h3 {{
      margin: 0;
      font-size: 24px;
      line-height: 1.2;
    }}
    .card-sub {{
      margin-top: 8px;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .tier {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 64px;
      padding: 8px 12px;
      border-radius: 12px;
      font-weight: 700;
      font-size: 18px;
      background: rgba(42, 58, 104, 0.82);
      border: 1px solid var(--line);
    }}
    .tier.t0 {{ background: rgba(145, 41, 69, 0.28); border-color: rgba(255, 128, 160, 0.38); }}
    .tier.t05 {{ background: rgba(154, 104, 28, 0.26); border-color: rgba(245, 197, 106, 0.36); }}
    .tier.t1 {{ background: rgba(39, 76, 121, 0.28); border-color: rgba(131, 167, 255, 0.4); }}
    .tier.t2 {{ background: rgba(34, 90, 74, 0.28); border-color: rgba(113, 224, 190, 0.34); }}
    .section {{
      margin-top: 14px;
      padding-top: 14px;
      border-top: 1px solid rgba(36, 51, 90, 0.8);
    }}
    .section:first-of-type {{
      margin-top: 0;
      padding-top: 0;
      border-top: 0;
    }}
    .section h4 {{
      margin: 0 0 10px;
      font-size: 14px;
      color: #dbe5ff;
    }}
    .priority-groups {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .priority-group {{
      display: inline-flex;
      flex-wrap: wrap;
      gap: 6px;
      align-items: center;
      padding: 8px 10px;
      border-radius: 12px;
      border: 1px solid rgba(50, 68, 114, 0.92);
      background: rgba(18, 28, 52, 0.9);
    }}
    .chip {{
      display: inline-flex;
      align-items: center;
      padding: 4px 10px;
      border-radius: 999px;
      background: rgba(39, 55, 98, 0.92);
      border: 1px solid rgba(67, 88, 143, 0.82);
      font-size: 12px;
      color: #e8eeff;
    }}
    .arrow {{
      color: var(--muted);
      font-size: 12px;
    }}
    .raw {{
      color: var(--muted);
      line-height: 1.65;
      font-size: 13px;
    }}
    .empty {{
      padding: 28px 20px;
      text-align: center;
      color: var(--muted);
      background: var(--panel);
      border: 1px dashed var(--line);
      border-radius: 18px;
    }}
    .appendix {{
      margin-top: 18px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
      box-shadow: var(--shadow);
    }}
    .appendix-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 14px;
      margin-top: 12px;
    }}
    .appendix-card {{
      background: var(--panel-2);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 14px;
    }}
    .appendix-card h3 {{
      margin: 0 0 10px;
      font-size: 15px;
    }}
    .appendix-list {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .footnote {{
      margin-top: 16px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.7;
    }}
    .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
    @media (max-width: 1100px) {{
      .layout {{
        grid-template-columns: 1fr;
      }}
      .sidebar {{
        position: static;
      }}
      .cards {{
        grid-template-columns: 1fr;
      }}
      .appendix-grid, .stats {{
        grid-template-columns: 1fr;
      }}
    }}
    @media (max-width: 720px) {{
      .wrap {{ padding: 14px; }}
      .hero h1 {{ font-size: 28px; }}
      .hero-top {{
        flex-direction: column;
      }}
      .card-head {{
        flex-direction: column;
      }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <div class="hero-top">
        <div>
          <h1>异环 角色培养指南</h1>
          <p>把角色培养建议做成可搜索、可筛选、可排序的静态页面，方便游玩时快速查看该角色该怎么养。</p>
          <p>当前页面聚焦文字可结构化内容：定位、梯度、加点顺序、技能优先级、弧盘、空幕、主词条、副词条。</p>
        </div>
        <div class="hero-badges">
          <span class="badge accent">单文件 HTML</span>
          <span class="badge">适合本地/线上托管</span>
          <span class="badge">生成时间 {generated_at}</span>
        </div>
      </div>
      <div class="hero-badges">
        <span class="badge">来源标题：<span class="mono" id="metaTitle"></span></span>
        <span class="badge">抓取日期：<span class="mono" id="metaDate"></span></span>
        <a class="badge" id="sourceLink" target="_blank" rel="noreferrer">打开源文档</a>
      </div>
      <div class="stats" id="stats"></div>
    </section>

    <div class="layout">
      <aside class="sidebar">
        <h2>筛选与排序</h2>
        <div class="field">
          <label for="searchInput">关键词</label>
          <input id="searchInput" placeholder="角色 / 弧盘 / 空幕 / 词条 / 技能" />
        </div>
        <div class="field">
          <label for="roleSelect">定位</label>
          <select id="roleSelect">
            <option value="">全部定位</option>
          </select>
        </div>
        <div class="field">
          <label for="tierSelect">梯度</label>
          <select id="tierSelect">
            <option value="">全部梯度</option>
          </select>
        </div>
        <div class="field">
          <label for="sortField">排序</label>
          <select id="sortField">
            <option value="default">默认顺序</option>
            <option value="tier">按梯度</option>
            <option value="name">按角色名</option>
            <option value="role">按定位</option>
          </select>
        </div>
        <div class="field">
          <label>快捷筛选</label>
          <div class="checks">
            <label class="check-chip"><input type="checkbox" value="main" /> 只看主力输出</label>
            <label class="check-chip"><input type="checkbox" value="support" /> 只看辅助</label>
            <label class="check-chip"><input type="checkbox" value="burst" /> 只看爆发输出</label>
          </div>
        </div>
        <div class="sidebar-actions">
          <button class="btn" id="resetBtn" type="button">重置筛选</button>
          <button class="btn" id="toggleAppendixBtn" type="button">附录显隐</button>
        </div>
      </aside>

      <main>
        <div class="result-bar">
          <div id="resultCount">当前展示 0 个角色</div>
          <div>支持按关键词、定位、梯度快速过滤</div>
        </div>
        <section class="cards" id="cards"></section>
      </main>
    </div>

    <section class="appendix" id="appendix">
      <h2>附录</h2>
      <div class="appendix-grid">
        <div class="appendix-card">
          <h3>每日事项</h3>
          <div class="appendix-list" id="dailyList"></div>
        </div>
        <div class="appendix-card">
          <h3>每周事项</h3>
          <div class="appendix-list" id="weeklyList"></div>
        </div>
        <div class="appendix-card">
          <h3>兑换码与图片章节</h3>
          <div class="appendix-list" id="miscList"></div>
        </div>
      </div>
      <div class="footnote" id="footnote"></div>
    </section>
  </div>

  <script>
    const PAYLOAD = {data_json};
    const DATA = PAYLOAD.characters || [];
    const META = PAYLOAD.meta || {{}};
    const APPENDIX = PAYLOAD.appendix || {{}};

    const state = {{
      search: "",
      role: "",
      tier: "",
      sortField: "default",
      quickFilters: [],
      appendixVisible: true,
    }};

    const tierOrder = {{
      "T0": 0,
      "T0.5": 1,
      "T1": 2,
      "T2": 3,
      "T3": 4,
      "T4": 5,
      "": 9,
    }};

    const el = {{
      metaTitle: document.getElementById("metaTitle"),
      metaDate: document.getElementById("metaDate"),
      sourceLink: document.getElementById("sourceLink"),
      stats: document.getElementById("stats"),
      searchInput: document.getElementById("searchInput"),
      roleSelect: document.getElementById("roleSelect"),
      tierSelect: document.getElementById("tierSelect"),
      sortField: document.getElementById("sortField"),
      resetBtn: document.getElementById("resetBtn"),
      toggleAppendixBtn: document.getElementById("toggleAppendixBtn"),
      cards: document.getElementById("cards"),
      resultCount: document.getElementById("resultCount"),
      appendix: document.getElementById("appendix"),
      dailyList: document.getElementById("dailyList"),
      weeklyList: document.getElementById("weeklyList"),
      miscList: document.getElementById("miscList"),
      footnote: document.getElementById("footnote"),
    }};

    function uniq(values) {{
      return Array.from(new Set(values)).filter(Boolean).sort((a, b) => a.localeCompare(b, "zh-CN"));
    }}

    function flattenGroups(field) {{
      if (!field) return [];
      if (Array.isArray(field.推荐项)) return field.推荐项;
      if (!Array.isArray(field.优先级组)) return [];
      return field.优先级组.flat();
    }}

    function searchableText(item) {{
      return [
        item.角色名称,
        item.定位,
        item.梯度展示,
        item.梯度备注,
        item.加点顺序?.原始,
        item.技能加点?.原始,
        item.弧盘推荐?.原始,
        item.空幕推荐?.原始,
        item.主词条?.原始,
        item.副词条?.原始,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
    }}

    function tierClass(tier) {{
      if (tier === "T0") return "t0";
      if (tier === "T0.5") return "t05";
      if (tier === "T1") return "t1";
      return "t2";
    }}

    function renderStats(rows) {{
      const roleCount = uniq(rows.map(item => item.定位)).length;
      const tierCount = uniq(rows.map(item => item.梯度)).length;
      const topTier = rows.filter(item => item.梯度 === "T0" || item.梯度 === "T0.5").length;
      const cards = [
        {{ k: "角色总数", v: String(rows.length) }},
        {{ k: "定位种类", v: String(roleCount) }},
        {{ k: "梯度覆盖", v: String(tierCount) }},
        {{ k: "高优先角色", v: String(topTier) }},
      ];
      el.stats.innerHTML = cards.map(card => `
        <div class="stat">
          <div class="k">${{card.k}}</div>
          <div class="v">${{card.v}}</div>
        </div>
      `).join("");
    }}

    function buildGroupHtml(groups) {{
      if (!Array.isArray(groups) || !groups.length) {{
        return '<div class="raw">暂无</div>';
      }}
      return `
        <div class="priority-groups">
          ${{groups.map((group, index) => `
            <div class="priority-group">
              ${{group.map(item => `<span class="chip">${{item}}</span>`).join("")}}
              ${{index < groups.length - 1 ? '<span class="arrow">→</span>' : ""}}
            </div>
          `).join("")}}
        </div>
      `;
    }}

    function buildFlatChips(items) {{
      if (!items.length) return '<div class="raw">暂无</div>';
      return `<div class="priority-groups">${{items.map(item => `<span class="chip">${{item}}</span>`).join("")}}</div>`;
    }}

    function cardHtml(item) {{
      const tierLabel = item.梯度展示 || item.梯度 || "-";
      const note = item.梯度备注 ? `<span class="badge">备注：${{item.梯度备注}}</span>` : "";
      return `
        <article class="card">
          <div class="card-head">
            <div>
              <h3>${{item.角色名称}}</h3>
              <div class="card-sub">
                <span class="badge accent">${{item.定位}}</span>
                <span class="badge">序号：${{item.序号}}</span>
                ${{note}}
              </div>
            </div>
            <div class="tier ${{tierClass(item.梯度)}}">${{tierLabel}}</div>
          </div>

          <div class="section">
            <h4>加点顺序</h4>
            ${{buildGroupHtml(item.加点顺序?.优先级组 || [])}}
            <div class="raw">原始：${{item.加点顺序?.原始 || "-"}}</div>
          </div>

          <div class="section">
            <h4>技能加点</h4>
            ${{buildGroupHtml(item.技能加点?.优先级组 || [])}}
          </div>

          <div class="section">
            <h4>弧盘推荐</h4>
            ${{buildGroupHtml(item.弧盘推荐?.优先级组 || [])}}
          </div>

          <div class="section">
            <h4>空幕推荐</h4>
            ${{buildFlatChips(flattenGroups(item.空幕推荐))}}
          </div>

          <div class="section">
            <h4>主词条</h4>
            ${{buildFlatChips(flattenGroups(item.主词条))}}
          </div>

          <div class="section">
            <h4>副词条</h4>
            ${{buildGroupHtml(item.副词条?.优先级组 || [])}}
          </div>
        </article>
      `;
    }}

    function applyQuickFilter(item) {{
      if (!state.quickFilters.length) return true;
      const label = item.定位 || "";
      return state.quickFilters.every(filter => {{
        if (filter === "main") return label.includes("主力输出");
        if (filter === "support") return label.includes("辅助");
        if (filter === "burst") return label.includes("爆发输出");
        return true;
      }});
    }}

    function filteredRows() {{
      const keyword = state.search.trim().toLowerCase();
      let rows = DATA.slice();

      if (keyword) {{
        rows = rows.filter(item => searchableText(item).includes(keyword));
      }}
      if (state.role) {{
        rows = rows.filter(item => item.定位 === state.role);
      }}
      if (state.tier) {{
        rows = rows.filter(item => item.梯度 === state.tier);
      }}
      rows = rows.filter(applyQuickFilter);

      rows.sort((a, b) => {{
        if (state.sortField === "name") {{
          return String(a.角色名称).localeCompare(String(b.角色名称), "zh-CN");
        }}
        if (state.sortField === "role") {{
          const roleCompare = String(a.定位).localeCompare(String(b.定位), "zh-CN");
          if (roleCompare !== 0) return roleCompare;
        }}
        if (state.sortField === "tier") {{
          const tierCompare = (tierOrder[a.梯度] ?? 9) - (tierOrder[b.梯度] ?? 9);
          if (tierCompare !== 0) return tierCompare;
        }}
        return (a.序号 || 0) - (b.序号 || 0);
      }});

      return rows;
    }}

    function renderCards() {{
      const rows = filteredRows();
      el.resultCount.textContent = `当前展示 ${{rows.length}} 个角色`;
      if (!rows.length) {{
        el.cards.innerHTML = '<div class="empty">没有匹配到角色，试试放宽关键词或清空筛选。</div>';
        return;
      }}
      el.cards.innerHTML = rows.map(cardHtml).join("");
    }}

    function fillSelect(selectEl, values, placeholder) {{
      selectEl.innerHTML = [`<option value="">${{placeholder}}</option>`]
        .concat(values.map(value => `<option value="${{value}}">${{value}}</option>`))
        .join("");
    }}

    function renderAppendix() {{
      const daily = APPENDIX["每日事项"] || [];
      const weekly = APPENDIX["每周事项"] || [];
      const codes = APPENDIX["兑换码"] || [];
      const images = APPENDIX["图片章节"] || [];

      el.dailyList.innerHTML = daily.map(item => `<span class="chip">${{item}}</span>`).join("");
      el.weeklyList.innerHTML = weekly.map(item => `<span class="chip">${{item}}</span>`).join("");
      el.miscList.innerHTML = codes
        .map(item => `<span class="chip mono">${{item}}</span>`)
        .concat(images.map(item => `<span class="chip">${{item}}（图片待结构化）</span>`))
        .join("");

      const notes = Array.isArray(META["说明"]) ? META["说明"] : [];
      el.footnote.innerHTML = notes.map(note => `<div>${{note}}</div>`).join("");
    }}

    function renderMeta() {{
      const source = META["来源"] || {{}};
      el.metaTitle.textContent = META["标题"] || "-";
      el.metaDate.textContent = source["抓取日期"] || "-";
      el.sourceLink.textContent = "打开飞书源文档";
      el.sourceLink.href = source["链接"] || "#";
    }}

    function render() {{
      renderStats(DATA);
      renderCards();
      el.appendix.style.display = state.appendixVisible ? "block" : "none";
      el.toggleAppendixBtn.textContent = state.appendixVisible ? "隐藏附录" : "显示附录";
    }}

    el.searchInput.addEventListener("input", event => {{
      state.search = event.target.value;
      render();
    }});
    el.roleSelect.addEventListener("change", event => {{
      state.role = event.target.value;
      render();
    }});
    el.tierSelect.addEventListener("change", event => {{
      state.tier = event.target.value;
      render();
    }});
    el.sortField.addEventListener("change", event => {{
      state.sortField = event.target.value;
      render();
    }});
    document.querySelectorAll('.check-chip input').forEach(input => {{
      input.addEventListener("change", event => {{
        const value = event.target.value;
        if (event.target.checked) {{
          state.quickFilters = Array.from(new Set(state.quickFilters.concat(value)));
        }} else {{
          state.quickFilters = state.quickFilters.filter(item => item !== value);
        }}
        render();
      }});
    }});
    el.resetBtn.addEventListener("click", () => {{
      state.search = "";
      state.role = "";
      state.tier = "";
      state.sortField = "default";
      state.quickFilters = [];
      el.searchInput.value = "";
      el.roleSelect.value = "";
      el.tierSelect.value = "";
      el.sortField.value = "default";
      document.querySelectorAll('.check-chip input').forEach(input => {{
        input.checked = false;
      }});
      render();
    }});
    el.toggleAppendixBtn.addEventListener("click", () => {{
      state.appendixVisible = !state.appendixVisible;
      render();
    }});

    fillSelect(el.roleSelect, uniq(DATA.map(item => item.定位)), "全部定位");
    fillSelect(
      el.tierSelect,
      uniq(DATA.map(item => item.梯度)).sort((a, b) => (tierOrder[a] ?? 9) - (tierOrder[b] ?? 9)),
      "全部梯度"
    );
    renderMeta();
    renderAppendix();
    render();
  </script>
</body>
</html>
"""


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    data_path = base_dir / "data" / "localized" / "role_cultivation" / "wuwa_role_cultivation.json"
    out_path = base_dir / "outputs" / "yihuan_role_cultivation_guide.html"

    payload = _load_data(data_path)
    out_path.write_text(_html_template(payload), encoding="utf-8")
    print(out_path)


if __name__ == "__main__":
    main()
