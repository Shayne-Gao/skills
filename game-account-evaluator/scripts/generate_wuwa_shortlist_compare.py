#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
UNIFIED_JSON = OUTPUTS_DIR / "wuwa_unified_scored.json"
DEFAULT_OUTPUT = OUTPUTS_DIR / "wuwa_shortlist_compare.html"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a standalone HTML comparison page for selected Wuwa accounts."
    )
    parser.add_argument(
        "--ids",
        nargs="+",
        required=True,
        help="Product IDs to compare, in display order.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Output HTML path.",
    )
    return parser.parse_args()


def load_unified_rows() -> List[Dict[str, Any]]:
    obj = json.loads(UNIFIED_JSON.read_text(encoding="utf-8"))
    return obj.get("items", [])


def find_rows(product_ids: Sequence[str]) -> List[Dict[str, Any]]:
    by_id = {str(row.get("product_id")): row for row in load_unified_rows()}
    rows: List[Dict[str, Any]] = []
    missing: List[str] = []
    for product_id in product_ids:
        row = by_id.get(str(product_id))
        if row:
            rows.append(row)
        else:
            missing.append(str(product_id))
    if missing:
        raise SystemExit(f"Missing product_id in unified JSON: {', '.join(missing)}")
    return rows


def fmt_num(value: Any, digits: int = 2) -> str:
    if value in (None, ""):
        return "-"
    try:
        num = float(value)
    except (TypeError, ValueError):
        return str(value)
    if abs(num - int(num)) < 1e-9:
        return str(int(num))
    return f"{num:.{digits}f}"


def fmt_price(value: Any) -> str:
    if value in (None, ""):
        return "-"
    return f"{fmt_num(value)}"


def fmt_rank(value: Any) -> str:
    if value in (None, ""):
        return "-"
    try:
        return f"#{int(value)}"
    except (TypeError, ValueError):
        return str(value)


def chip(text: str, cls: str = "") -> str:
    safe = html.escape(text)
    extra = f" {cls}" if cls else ""
    return f'<span class="chip{extra}">{safe}</span>'


def platform_chip(platform: str) -> str:
    cls_map = {
        "kejinshou": "platform-k",
        "pzds": "platform-p",
        "7881": "platform-7",
    }
    return chip(platform, cls_map.get(platform, ""))


def status_chip(row: Dict[str, Any]) -> str:
    status = str(row.get("market_status") or "unknown")
    label_map = {
        "active": "在售",
        "sold": "已售",
        "unknown": "待确认",
    }
    return chip(label_map.get(status, status), f"status-{status}")


def collect_roles(row: Dict[str, Any], tiers: Sequence[str] | None = None) -> List[str]:
    result = []
    for role in row.get("roles", []) or []:
        if role.get("star") != "五星":
            continue
        tier = str(role.get("tier") or "")
        if tiers and tier not in tiers:
            continue
        name = str(role.get("name") or "").strip()
        if name:
            result.append(name)
    return result


def collect_weapons(row: Dict[str, Any], signature_only: bool = False) -> List[str]:
    result = []
    for weapon in row.get("weapons", []) or []:
        weapon_name = str(weapon.get("name") or "").strip()
        if not weapon_name:
            continue
        if signature_only and weapon.get("weapon_class") != "signature":
            continue
        result.append(weapon_name)
    return result


def collect_teams(row: Dict[str, Any]) -> List[str]:
    result = []
    for team in row.get("matched_teams", []) or []:
        name = str(team.get("team_name") or "").strip()
        roles = " + ".join(team.get("matched_roles", []) or [])
        if name and roles:
            result.append(f"{name}: {roles}")
        elif name:
            result.append(name)
    return result


def safety_summary(row: Dict[str, Any]) -> str:
    parts: List[str] = []
    for key, label in (
        ("wegame_binding", "WeGame"),
        ("taptap_binding", "TAP"),
        ("qq_binding", "QQ"),
        ("wechat_binding", "微信"),
        ("apple_binding", "Apple"),
    ):
        value = row.get(key)
        if value in (None, "", "unknown"):
            continue
        parts.append(f"{label}:{value}")
    security = str(row.get("security_summary") or "").strip()
    if security and any(
        keyword in security for keyword in ("未绑定", "绑定", "换绑", "实名", "包赔", "冷却")
    ):
        parts.append(security)
    return " / ".join(parts) or "未见明确绑定摘要"


def auto_comment(row: Dict[str, Any]) -> str:
    good: List[str] = []
    risk: List[str] = []

    price = float(row.get("price") or 0)
    value_score = float(row.get("value_score") or 0)
    strength_score = float(row.get("strength_score") or 0)
    team_count = int(row.get("team_count") or 0)
    pulls = float(row.get("pulls_total") or 0)
    t0_roles = collect_roles(row, tiers=("T0", "T0.5"))
    signature_weapons = collect_weapons(row, signature_only=True)
    safety = safety_summary(row)

    if value_score >= 10:
        good.append("性价比分很高")
    if strength_score >= 120:
        good.append("绝对强度不低")
    if team_count >= 2:
        good.append("至少有两套可用配队")
    if len(t0_roles) >= 4:
        good.append("高保值角色覆盖较好")
    if len(signature_weapons) >= 4:
        good.append("专武完成度高")
    if pulls >= 10:
        good.append("资源储备不算空")

    if "绑定" in safety and "未绑定" not in safety:
        risk.append("绑定风险需要单独核验")
    if price >= 180:
        risk.append("价格进入高段，容错更低")
    if team_count <= 1:
        risk.append("成体系配队偏少")
    if len(signature_weapons) <= 2:
        risk.append("专武覆盖一般")

    good_text = "；".join(good[:3]) or "整体结构均衡"
    risk_text = "；".join(risk[:2]) or "买前重点确认账号绑定与交付方式"
    return f"优点：{good_text}。注意：{risk_text}。"


def metric_row(label: str, values: Sequence[str]) -> str:
    cells = "".join(f"<td>{value}</td>" for value in values)
    return f"<tr><th>{html.escape(label)}</th>{cells}</tr>"


def render_table(rows: Sequence[Dict[str, Any]]) -> str:
    headers = "".join(
        "<th>"
        f"{platform_chip(str(row.get('platform') or ''))}"
        f"<div class=\"id\">{html.escape(str(row.get('product_id') or '-'))}</div>"
        "</th>"
        for row in rows
    )
    body_rows = [
        metric_row("价格", [f"¥{fmt_price(row.get('price'))}" for row in rows]),
        metric_row("统一榜排名", [fmt_rank(row.get("unified_rank")) for row in rows]),
        metric_row("性价比分", [fmt_num(row.get("value_score")) for row in rows]),
        metric_row("强度分", [fmt_num(row.get("strength_score")) for row in rows]),
        metric_row("角色分", [fmt_num(row.get("role_score_total")) for row in rows]),
        metric_row("武器分", [fmt_num(row.get("weapon_score_total")) for row in rows]),
        metric_row("状态", [status_chip(row) for row in rows]),
        metric_row("等级 / 总黄", [f"{fmt_num(row.get('level'))} / {fmt_num(row.get('total_yellow'))}" for row in rows]),
        metric_row("配队数 / 加分", [f"{fmt_num(row.get('team_count'))} / {fmt_num(row.get('team_bonus'))}" for row in rows]),
        metric_row("抽数分", [fmt_num(row.get("pulls_total")) for row in rows]),
        metric_row(
            "T0/T0.5 角色",
            [
                "".join(chip(name, "t0") for name in collect_roles(row, tiers=("T0", "T0.5"))) or "-"
                for row in rows
            ],
        ),
        metric_row(
            "专武",
            ["".join(chip(name, "team") for name in collect_weapons(row, signature_only=True)) or "-" for row in rows],
        ),
        metric_row(
            "命中配队",
            ["".join(chip(name, "team") for name in collect_teams(row)) or "-" for row in rows],
        ),
        metric_row("安全摘要", [html.escape(safety_summary(row)) for row in rows]),
        metric_row("我的判断", [html.escape(auto_comment(row)) for row in rows]),
    ]
    return (
        "<table>"
        f"<thead><tr><th>对比项</th>{headers}</tr></thead>"
        f"<tbody>{''.join(body_rows)}</tbody>"
        "</table>"
    )


def render_cards(rows: Sequence[Dict[str, Any]]) -> str:
    cards = []
    for row in rows:
        roles = "".join(chip(name, "t0") for name in collect_roles(row, tiers=("T0", "T0.5")))
        teams = "".join(chip(name, "team") for name in collect_teams(row))
        weapons = "".join(chip(name) for name in collect_weapons(row, signature_only=True)[:8])
        cards.append(
            f"""
            <article class="card">
              <div class="card-head">
                <div>
                  <div class="title-line">{platform_chip(str(row.get("platform") or ""))}<span class="mono">{html.escape(str(row.get("product_id") or "-"))}</span></div>
                  <h2>¥{fmt_price(row.get("price"))}</h2>
                </div>
                <div class="score-box">
                  <div><span>性价比</span><strong>{fmt_num(row.get("value_score"))}</strong></div>
                  <div><span>强度</span><strong>{fmt_num(row.get("strength_score"))}</strong></div>
                </div>
              </div>
              <p class="muted">统一榜排名 {fmt_rank(row.get("unified_rank"))} / 状态 {status_chip(row)}</p>
              <p><strong>简评：</strong>{html.escape(auto_comment(row))}</p>
              <p><strong>核心角色：</strong>{roles or '-'}</p>
              <p><strong>专武：</strong>{weapons or '-'}</p>
              <p><strong>配队：</strong>{teams or '-'}</p>
              <p><strong>安全：</strong>{html.escape(safety_summary(row))}</p>
              <p><strong>详情：</strong><a href="{html.escape(str(row.get("detail_url") or "#"))}">{html.escape(str(row.get("detail_url") or "-"))}</a></p>
            </article>
            """
        )
    return "".join(cards)


def best_summary(rows: Sequence[Dict[str, Any]]) -> str:
    best_value = max(rows, key=lambda row: float(row.get("value_score") or 0))
    best_strength = max(rows, key=lambda row: float(row.get("strength_score") or 0))
    safest = min(
        rows,
        key=lambda row: (
            0 if "未绑定" in safety_summary(row) else 1,
            float(row.get("price") or 0),
        ),
    )
    return (
        f"<p>性价比最强：<strong>{html.escape(str(best_value.get('product_id')))}</strong>，"
        f"价格 ¥{fmt_price(best_value.get('price'))}，性价比分 {fmt_num(best_value.get('value_score'))}。</p>"
        f"<p>绝对强度最高：<strong>{html.escape(str(best_strength.get('product_id')))}</strong>，"
        f"强度分 {fmt_num(best_strength.get('strength_score'))}。</p>"
        f"<p>安全侧更稳：<strong>{html.escape(str(safest.get('product_id')))}</strong>，"
        f"{html.escape(safety_summary(safest))}。</p>"
    )


def build_html(rows: Sequence[Dict[str, Any]], product_ids: Sequence[str]) -> str:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>鸣潮账号候选对比</title>
  <style>
    :root {{
      --bg:#09111f; --panel:#111b2f; --panel2:#17233f; --line:#2b3d67; --text:#eef3ff; --muted:#9fb0d6; --good:#58d39d;
    }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:linear-gradient(180deg,#09111f,#0e1730); color:var(--text); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
    a {{ color:#9cc2ff; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    .wrap {{ max-width:1680px; margin:0 auto; padding:24px; }}
    .hero,.panel {{ background:rgba(17,27,47,.95); border:1px solid var(--line); border-radius:16px; }}
    .hero {{ padding:20px 22px; margin-bottom:18px; }}
    .hero h1 {{ margin:0 0 8px; font-size:30px; }}
    .hero p {{ margin:6px 0; color:var(--muted); line-height:1.6; }}
    .mono {{ font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:14px; margin-bottom:18px; }}
    .card,.summary-card {{ background:var(--panel2); border:1px solid var(--line); border-radius:14px; padding:16px; }}
    .card-head {{ display:flex; justify-content:space-between; gap:16px; align-items:flex-start; }}
    .card h2 {{ margin:6px 0 8px; font-size:28px; }}
    .card p {{ margin:10px 0; line-height:1.6; }}
    .title-line {{ display:flex; gap:10px; align-items:center; }}
    .score-box {{ display:grid; gap:8px; min-width:120px; }}
    .score-box div {{ background:#1a284a; border:1px solid var(--line); border-radius:12px; padding:10px 12px; text-align:right; }}
    .score-box span {{ display:block; font-size:12px; color:var(--muted); }}
    .score-box strong {{ font-size:22px; color:var(--good); }}
    .chip {{ display:inline-block; margin:0 6px 6px 0; padding:3px 8px; border-radius:999px; background:#243761; font-size:12px; }}
    .platform-k {{ background:#4b2e83; }}
    .platform-p {{ background:#1f5d5b; }}
    .platform-7 {{ background:#7a3c18; }}
    .status-active {{ background:#245f45; }}
    .status-sold {{ background:#6f2d32; }}
    .status-unknown {{ background:#4e587a; }}
    .t0 {{ background:#6e2b2b; }}
    .team {{ background:#345b2f; }}
    .muted {{ color:var(--muted); font-size:13px; }}
    .panel {{ padding:18px; margin-bottom:18px; overflow:hidden; }}
    .panel h3 {{ margin:0 0 12px; font-size:18px; }}
    table {{ width:100%; border-collapse:collapse; }}
    thead th {{ background:#16213b; color:#d9e3ff; padding:12px 10px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
    tbody th, tbody td {{ padding:12px 10px; border-bottom:1px solid rgba(43,61,103,.65); vertical-align:top; font-size:14px; line-height:1.6; }}
    tbody th {{ width:180px; color:#d9e3ff; background:rgba(255,255,255,.02); }}
    .id {{ margin-top:8px; font-size:12px; color:var(--muted); }}
    @media (max-width: 1100px) {{
      .wrap {{ padding:14px; }}
      .panel {{ overflow-x:auto; }}
      table {{ min-width:980px; }}
      .card-head {{ flex-direction:column; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>鸣潮账号候选对比页</h1>
      <p>本页从 unified 主库抽取指定账号，专门用于横向比较价格、强度、性价比、配队、专武和绑定风险。</p>
      <p class="mono">候选 product_id：{html.escape(', '.join(product_ids))}</p>
      <p class="muted">生成时间：{generated_at}</p>
    </section>
    <section class="panel">
      <h3>快速结论</h3>
      {best_summary(rows)}
    </section>
    <section class="grid">
      {render_cards(rows)}
    </section>
    <section class="panel">
      <h3>横向明细</h3>
      {render_table(rows)}
    </section>
  </div>
</body>
</html>
"""


def main() -> None:
    args = parse_args()
    rows = find_rows(args.ids)
    output_path = Path(args.output).resolve()
    output_path.write_text(build_html(rows, args.ids), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
