import csv
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_csv(path: Path, header: List[str], rows: List[List[Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def _latest_file(raw_dir: Path, pattern: str) -> Optional[Path]:
    matches = sorted(raw_dir.glob(pattern), key=lambda p: p.stat().st_mtime)
    return matches[-1] if matches else None


def _latest_incremental_files(raw_dir: Path, platform: str) -> List[Path]:
    latest_by_page: Dict[int, Path] = {}
    for path in raw_dir.glob(f"{platform}_incremental_page*_*.json"):
        match = re.search(r"_page(\d+)_", path.name)
        if not match:
            continue
        page = int(match.group(1))
        current = latest_by_page.get(page)
        if current is None or path.stat().st_mtime > current.stat().st_mtime:
            latest_by_page[page] = path
    return [latest_by_page[page] for page in sorted(latest_by_page)]


def _extract_7881_product_id(detail_url: str) -> str:
    match = re.search(r"search\.7881\.com/(\d+)\.html", str(detail_url or ""))
    return match.group(1) if match else ""


def _normalize_round_id(value: Any) -> str:
    digits = re.sub(r"\D", "", str(value or ""))
    if len(digits) >= 12:
        return digits[:12]
    if len(digits) == 8:
        return digits + "0000"
    return ""


def _infer_round_id(row: Dict[str, Any]) -> str:
    for key in ["round_id", "first_seen_at", "status_checked_at", "listing_time", "last_seen_at"]:
        round_id = _normalize_round_id(row.get(key))
        if round_id:
            return round_id
    return ""


def _resolve_current_round_id() -> str:
    explicit = (
        os.environ.get("WUWA_REFRESH_ROUND_ID")
        or os.environ.get("WUWA_ROUND_ID")
        or os.environ.get("REFRESH_ROUND_ID")
    )
    normalized = _normalize_round_id(explicit)
    if normalized:
        return normalized
    return datetime.now().strftime("%Y%m%d%H%M")


def _normalize_role_name(name: str) -> str:
    alias_map = {
        "卡提那娅": "卡提希娅",
        "坎特雷拉": "坎特蕾拉",
        "莫宁": "莫宁",
        "风主": "风主",
    }
    return alias_map.get(str(name).strip(), str(name).strip())


def _load_team_configs(path: Path) -> Dict[str, Any]:
    obj = _load_json(path)
    for item in obj.get("items", []):
        item["positions"] = [
            [_normalize_role_name(role) for role in position]
            for position in item.get("positions", [])
        ]
    return obj


def _match_teams(rows: List[Dict[str, Any]], team_config: Dict[str, Any]) -> None:
    bonus_per_team = int(team_config.get("meta", {}).get("bonus_per_team", 100))
    for row in rows:
        role_set: Set[str] = {_normalize_role_name(role.get("name", "")) for role in row.get("roles", [])}
        matched_teams = []
        for team in team_config.get("items", []):
            matched_roles = []
            ok = True
            for position in team.get("positions", []):
                hit = next((candidate for candidate in position if candidate in role_set), "")
                if not hit:
                    ok = False
                    break
                matched_roles.append(hit)
            if ok:
                matched_teams.append(
                    {
                        "system": team.get("体系", ""),
                        "team_name": team.get("队伍", ""),
                        "matched_roles": matched_roles,
                    }
                )
        row["team_count"] = len(matched_teams)
        row["team_bonus"] = len(matched_teams) * bonus_per_team
        row["matched_teams"] = matched_teams
        row["strength_score"] = round(float(row.get("strength_score", 0)) + row["team_bonus"], 2)
        price = max(float(row.get("price", 0) or 0), 1.0)
        row["value_score"] = round(row["strength_score"] / price, 3)


def _build_kejin_rows(base_dir: Path) -> List[Dict[str, Any]]:
    normalized = _load_json(base_dir / "outputs" / "wuwa_top200_normalized_assets.json")
    rows = []
    for item in normalized["items"]:
        rows.append(
            {
                "platform": "kejinshou",
                "product_id": str(item["product_id"]),
                "detail_url": f"https://m.kejinshou.com/goods/details/{item['product_id']}",
                "price": float(item["price"]),
                "listing_time": item.get("upper_at", ""),
                "listing_time_desc": item.get("polish_time_desc", ""),
                "level": int(item["level"]),
                "total_yellow": int(item["total_yellow"]),
                "summary": item.get("sub_title", ""),
                "security_summary": item.get("sub_title", ""),
                "resources": item["resources"],
                "roles": item["roles"],
                "weapons": item["weapons"],
                "role_score_total": float(item["role_score_total"]) if "role_score_total" in item else round(sum(x["score"] for x in item["roles"]), 2),
                "weapon_score_total": float(item["weapon_score_total"]) if "weapon_score_total" in item else round(sum(x["score"] for x in item["weapons"]), 2),
                "strength_score": float(item["strength_score"]),
                "value_score": float(item["value_score"]),
                "market_status": item.get("market_status", "unknown"),
                "is_sold": bool(item.get("is_sold", False)),
                "status_reason": item.get("status_reason", ""),
                "status_checked_at": item.get("status_checked_at", ""),
            }
        )
    return rows


def _build_pzds_rows(base_dir: Path) -> List[Dict[str, Any]]:
    src = _load_json(base_dir / "outputs" / "pzds_wuwa_top100_scored.json")
    rows = []
    for item in src["items"]:
        item.setdefault("listing_time", item.get("onStandTime", ""))
        item.setdefault("listing_time_desc", item.get("onStandTimeDesc", ""))
        item.setdefault("market_status", item.get("market_status", "unknown"))
        item.setdefault("is_sold", bool(item.get("is_sold", False)))
        item.setdefault("status_reason", item.get("status_reason", ""))
        item.setdefault("status_checked_at", item.get("status_checked_at", ""))
        rows.append(item)
    return rows


def _build_7881_rows(base_dir: Path) -> List[Dict[str, Any]]:
    src = _load_json(base_dir / "outputs" / "7881_wuwa_top100_scored.json")
    rows = []
    for item in src["items"]:
        item.setdefault("listing_time", item.get("publish_abs", item.get("createTime", item.get("updateTime", ""))))
        item.setdefault("listing_time_desc", item.get("publish_text", ""))
        item.setdefault("market_status", item.get("market_status", "unknown"))
        item.setdefault("is_sold", bool(item.get("is_sold", False)))
        item.setdefault("status_reason", item.get("status_reason", ""))
        item.setdefault("status_checked_at", item.get("status_checked_at", ""))
        rows.append(item)
    return rows


def _default_row(platform: str, product_id: str, detail_url: str, price: float, listing_time: str, listing_time_desc: str) -> Dict[str, Any]:
    return {
        "platform": platform,
        "product_id": product_id,
        "detail_url": detail_url,
        "price": float(price or 0),
        "listing_time": listing_time or "",
        "listing_time_desc": listing_time_desc or "",
        "level": 0,
        "total_yellow": 0,
        "summary": "",
        "security_summary": "",
        "resources": {
            "star_voice": 0,
            "fj_waves": 0,
            "zc_waves": 0,
            "hs_waves": 0,
            "character_pulls": 0,
            "weapon_pulls": 0,
            "standard_pulls_ignored": 0,
            "pulls_total": 0,
        },
        "roles": [],
        "weapons": [],
        "role_score_total": 0.0,
        "weapon_score_total": 0.0,
        "team_count": 0,
        "team_bonus": 0,
        "matched_teams": [],
        "strength_score": 0.0,
        "value_score": 0.0,
        "market_status": "active",
        "is_sold": False,
        "status_reason": "current_incremental_page_visible",
        "status_checked_at": "",
        "source_type": "incremental_snapshot",
        "is_incremental_only": True,
    }


def _repair_row_identity(row: Dict[str, Any]) -> Dict[str, Any]:
    item = dict(row)
    product_id = str(item.get("product_id") or "").strip()
    if item.get("platform") == "7881" and (not product_id or product_id in {"0", "0000"}):
        recovered = _extract_7881_product_id(str(item.get("detail_url") or ""))
        if recovered:
            item["product_id"] = recovered
    return item


def _build_incremental_snapshot_rows(base_dir: Path) -> List[Dict[str, Any]]:
    raw_dir = base_dir / "data" / "raw"
    rows: List[Dict[str, Any]] = []

    for kjs_path in _latest_incremental_files(raw_dir, "kejinshou"):
        obj = _load_json(kjs_path)
        for item in obj.get("items", []):
            row = _default_row(
                platform="kejinshou",
                product_id=str(item.get("id") or ""),
                detail_url=f"https://m.kejinshou.com/goods/details/{item.get('id')}",
                price=float(item.get("price") or 0),
                listing_time=str(item.get("upper_at") or ""),
                listing_time_desc=str(item.get("polish_time_desc") or ""),
            )
            row["status_checked_at"] = obj.get("capturedAt", "")
            row["new_by_snapshot"] = bool(item.get("new_by_id", False))
            row["snapshot_page"] = obj.get("strategy", {}).get("page", "")
            rows.append(row)

    for pzds_path in _latest_incremental_files(raw_dir, "pzds"):
        obj = _load_json(pzds_path)
        for item in obj.get("items", []):
            row = _default_row(
                platform="pzds",
                product_id=str(item.get("id") or ""),
                detail_url=f"https://www.pzds.com/goodsDetails/{item.get('id')}/6?from=%E5%95%86%E5%93%81%E5%88%97%E8%A1%A8",
                price=float(item.get("price") or 0),
                listing_time="",
                listing_time_desc=str(item.get("publish_text") or ""),
            )
            row["status_checked_at"] = obj.get("capturedAt", "")
            row["new_by_snapshot"] = bool(item.get("new_by_id", False))
            row["snapshot_page"] = obj.get("strategy", {}).get("page", "")
            rows.append(row)

    for t7881_path in _latest_incremental_files(raw_dir, "7881"):
        obj = _load_json(t7881_path)
        for item in obj.get("items", []):
            product_id = str(item.get("goods_id") or item.get("id") or "")
            row = _default_row(
                platform="7881",
                product_id=product_id,
                detail_url=f"https://search.7881.com/{product_id}.html",
                price=float(item.get("price") or 0),
                listing_time="",
                listing_time_desc=str(item.get("publish_text") or ""),
            )
            row["status_checked_at"] = obj.get("capturedAt", "")
            row["new_by_snapshot"] = bool(item.get("new_by_id", False))
            row["snapshot_page"] = obj.get("strategy", {}).get("page", "")
            rows.append(row)

    return [row for row in rows if row["product_id"]]


def _merge_incremental_patch(previous: Dict[str, Any], patch: Dict[str, Any]) -> Dict[str, Any]:
    combined = dict(previous)
    # Incremental page snapshots only patch market/listing metadata.
    for key in [
        "detail_url",
        "price",
        "listing_time",
        "listing_time_desc",
        "market_status",
        "is_sold",
        "status_reason",
        "status_checked_at",
        "new_by_snapshot",
    ]:
        if key in patch:
            if key == "new_by_snapshot":
                combined[key] = bool(previous.get(key)) or bool(patch[key])
            else:
                combined[key] = patch[key]
    return combined


def _merge_rows(existing_rows: List[Dict[str, Any]], fresh_rows: List[Dict[str, Any]], current_round_id: str) -> List[Dict[str, Any]]:
    now_tag = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    merged: Dict[str, Dict[str, Any]] = {}

    for row in existing_rows:
        item = _repair_row_identity(row)
        # Reset round-scoped snapshot markers and let the latest raw snapshots repopulate them.
        item["new_by_snapshot"] = False
        item["snapshot_page"] = ""
        item.setdefault("first_seen_at", item.get("status_checked_at") or item.get("listing_time") or now_tag)
        item.setdefault("last_seen_at", item.get("status_checked_at") or now_tag)
        item.setdefault("source_type", "scored")
        item.setdefault("is_incremental_only", False)
        inferred_round_id = _infer_round_id(item)
        if not inferred_round_id and bool(item.get("is_new_this_round")):
            inferred_round_id = current_round_id
        item["round_id"] = inferred_round_id or current_round_id
        merged[f"{item['platform']}::{item['product_id']}"] = item

    for row in fresh_rows:
        item = _repair_row_identity(row)
        item.setdefault("source_type", "scored")
        item.setdefault("is_incremental_only", False)
        key = f"{item['platform']}::{item['product_id']}"
        previous = merged.get(key, {})
        first_seen_at = previous.get("first_seen_at", item.get("status_checked_at") or item.get("listing_time") or now_tag)
        last_seen_at = item.get("status_checked_at") or now_tag
        if previous and item.get("source_type") == "incremental_snapshot":
            combined = _merge_incremental_patch(previous, item)
        else:
            combined = dict(previous)
            combined.update(item)
        combined["first_seen_at"] = first_seen_at
        combined["last_seen_at"] = last_seen_at
        combined["round_id"] = previous.get("round_id") or _infer_round_id(item) or current_round_id
        if previous and previous.get("source_type") == "scored" and item.get("source_type") == "incremental_snapshot":
            combined["source_type"] = "scored"
            combined["is_incremental_only"] = False
        merged[key] = combined

    return list(merged.values())


def _annotate_row_quality(row: Dict[str, Any]) -> Dict[str, Any]:
    item = dict(row)
    platform = str(item.get("platform") or "")
    is_incremental_only = bool(item.get("is_incremental_only"))
    source_type = str(item.get("source_type") or "")
    price = float(item.get("price", 0) or 0)
    level = int(item.get("level", 0) or 0)
    total_yellow = int(item.get("total_yellow", 0) or 0)
    roles = item.get("roles") or []
    weapons = item.get("weapons") or []
    strength_score = float(item.get("strength_score", 0) or 0)
    summary = str(item.get("summary") or "").strip()

    data_quality = "ok"
    quality_label = "正常"
    parse_failed_reason = ""
    can_rank = True
    detail_fetch_status = "fetched"
    detail_fetch_label = "已抓到详情"

    if is_incremental_only or source_type == "incremental_snapshot":
        data_quality = "incremental_snapshot_pending"
        quality_label = "待抓详情"
        parse_failed_reason = "incremental_snapshot_only"
        can_rank = False
        detail_fetch_status = "pending"
        detail_fetch_label = "待抓详情"
    elif platform == "pzds" and price == 0 and level == 0 and total_yellow == 0 and not roles and not weapons and not summary:
        data_quality = "parse_failed_empty"
        quality_label = "没抓到详情"
        parse_failed_reason = "pzds_detail_waf_or_parse_failed"
        can_rank = False
        detail_fetch_status = "missing"
        detail_fetch_label = "没抓到详情"
    elif strength_score == 0 and not roles and not weapons:
        data_quality = "parse_failed_partial"
        quality_label = "没抓到详情"
        parse_failed_reason = "detail_incomplete_or_parse_failed"
        can_rank = False
        detail_fetch_status = "missing"
        detail_fetch_label = "没抓到详情"

    item["data_quality"] = data_quality
    item["quality_label"] = quality_label
    item["parse_failed_reason"] = parse_failed_reason
    item["can_rank"] = can_rank
    item["detail_fetch_status"] = detail_fetch_status
    item["detail_fetch_label"] = detail_fetch_label
    return item


def _html_template(rows: List[Dict[str, Any]], meta: Dict[str, Any]) -> str:
    data_json = json.dumps(rows, ensure_ascii=False)
    meta_json = json.dumps(meta, ensure_ascii=False)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>鸣潮账号跨平台统一评估</title>
  <style>
    :root {{
      --bg:#09111f; --panel:#111b2f; --panel2:#17233f; --line:#2b3d67; --text:#eef3ff; --muted:#9fb0d6; --good:#58d39d;
    }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:linear-gradient(180deg,#09111f,#0e1730); color:var(--text); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
    a {{ color:#9cc2ff; text-decoration:none; }} a:hover {{ text-decoration:underline; }}
    .wrap {{ max-width:1660px; margin:0 auto; padding:24px; }}
    .hero,.table-wrap {{ background:rgba(17,27,47,.95); border:1px solid var(--line); border-radius:16px; }}
    .hero {{ padding:20px 22px; margin-bottom:18px; }}
    .hero h1 {{ margin:0 0 8px; font-size:28px; }}
    .hero p {{ margin:6px 0; color:var(--muted); }}
    .stats,.controls,.detail-grid {{ display:grid; gap:12px; }}
    .stats {{ grid-template-columns:repeat(8,minmax(0,1fr)); margin-top:16px; }}
    .controls {{ grid-template-columns:2fr 1fr 1fr 1fr; margin:18px 0 10px; }}
    .stat,.card {{ background:var(--panel2); border:1px solid var(--line); border-radius:12px; padding:14px; }}
    .stat .k {{ font-size:12px; color:var(--muted); }} .stat .v {{ margin-top:8px; font-size:22px; font-weight:700; }}
    .controls input,.controls select {{ width:100%; padding:12px 14px; border-radius:10px; border:1px solid var(--line); background:var(--panel2); color:var(--text); }}
    .filter-drawer {{ margin:0 0 18px; }}
    .filter-toggle {{ width:100%; display:flex; justify-content:space-between; align-items:center; gap:16px; padding:14px 16px; border-radius:14px; border:1px solid rgba(94,122,189,.6); background:linear-gradient(180deg, rgba(24,37,67,.95), rgba(14,23,42,.95)); color:var(--text); cursor:pointer; text-align:left; }}
    .filter-toggle-main {{ display:flex; flex-direction:column; gap:6px; min-width:0; }}
    .filter-toggle-title {{ font-size:15px; font-weight:700; color:#eef3ff; }}
    .filter-toggle-hint {{ font-size:12px; color:#a9b8dc; line-height:1.5; }}
    .filter-toggle-meta {{ display:flex; align-items:center; gap:12px; flex-shrink:0; }}
    .filter-chip {{ background:#243761; }}
    .filter-toggle-arrow {{ font-size:18px; color:#bfd0ff; transition:transform .2s ease; }}
    .filter-toggle.open .filter-toggle-arrow {{ transform:rotate(180deg); }}
    .filter-panel {{ display:none; margin-top:12px; padding:16px; border-radius:14px; border:1px solid var(--line); background:rgba(12,20,37,.96); }}
    .filter-panel.open {{ display:block; }}
    .filter-panel-head {{ display:flex; justify-content:space-between; align-items:flex-start; gap:12px; margin-bottom:14px; }}
    .filter-panel-title {{ margin:0 0 4px; font-size:14px; font-weight:700; color:#eef3ff; }}
    .filter-panel-hint {{ font-size:12px; color:#9fb0d6; line-height:1.5; }}
    .filter-panel-head button,.role-filter-actions button {{ background:#22315b; color:var(--text); border:1px solid var(--line); border-radius:10px; padding:8px 12px; cursor:pointer; }}
    .quick-filter-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; margin-bottom:16px; }}
    .quick-filter-btn {{ display:flex; flex-direction:column; align-items:flex-start; gap:6px; min-height:88px; padding:12px 14px; background:#17233f; color:#dfe6ff; border:1px solid rgba(67,87,137,.9); border-radius:12px; font-size:12px; cursor:pointer; text-align:left; transition:border-color .2s ease, transform .2s ease, background .2s ease; }}
    .quick-filter-btn:hover {{ transform:translateY(-1px); border-color:#7390df; }}
    .quick-filter-btn.active {{ background:linear-gradient(180deg, rgba(124,92,255,.24), rgba(41,54,100,.92)); border-color:#9d86ff; color:#fff; }}
    .quick-filter-system {{ font-size:11px; color:#9fb0d6; text-transform:uppercase; letter-spacing:.04em; }}
    .quick-filter-name {{ font-size:14px; font-weight:700; color:inherit; }}
    .quick-filter-roles {{ color:#d7e0ff; line-height:1.4; }}
    .quick-filter-count {{ color:#9fb0d6; }}
    .selected-role-list {{ display:flex; flex-wrap:wrap; gap:8px; min-height:40px; padding:10px 0 14px; }}
    .selected-role-empty {{ color:var(--muted); font-size:12px; padding:4px 0; }}
    .selected-role-chip {{ display:inline-flex; align-items:center; gap:8px; padding:7px 10px; border-radius:999px; border:1px solid rgba(95,119,180,.9); background:#1e2d53; color:#eef3ff; font-size:12px; }}
    .selected-role-chip button {{ appearance:none; border:none; background:transparent; color:#bfd0ff; cursor:pointer; font-size:14px; line-height:1; padding:0; }}
    .role-filter-actions {{ display:flex; justify-content:space-between; align-items:center; gap:10px; margin-bottom:12px; color:var(--muted); font-size:12px; }}
    .role-options {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; }}
    .role-group {{ border:1px solid rgba(43,61,103,.7); border-radius:12px; padding:12px; background:rgba(9,17,31,.45); }}
    .role-group-title {{ display:flex; justify-content:space-between; align-items:center; margin:0 0 10px; font-size:13px; font-weight:700; color:#e6ecff; }}
    .role-group-badge {{ display:inline-flex; align-items:center; justify-content:center; min-width:52px; padding:4px 8px; border-radius:999px; background:#243761; color:#d9e4ff; font-size:11px; text-transform:uppercase; letter-spacing:.04em; }}
    .role-group-count {{ color:var(--muted); font-weight:500; font-size:12px; }}
    .role-group-options {{ display:flex; flex-wrap:wrap; gap:8px; }}
    .role-option {{ position:relative; }}
    .role-option input {{ position:absolute; opacity:0; pointer-events:none; }}
    .role-option span {{ display:inline-flex; align-items:center; gap:6px; min-height:34px; padding:7px 10px; border-radius:999px; border:1px solid rgba(67,87,137,.8); background:rgba(21,33,61,.9); color:#dfe6ff; font-size:13px; cursor:pointer; transition:border-color .2s ease, background .2s ease, transform .2s ease; }}
    .role-option span:hover {{ border-color:#7f9fff; transform:translateY(-1px); }}
    .role-option input:checked + span {{ background:linear-gradient(180deg, rgba(124,92,255,.28), rgba(34,49,91,.95)); border-color:#9d86ff; color:#fff; }}
    .role-option-tier {{ color:#9fb0d6; font-size:11px; }}
    .toolbar {{ display:flex; justify-content:space-between; align-items:center; color:var(--muted); font-size:13px; margin-bottom:10px; }}
    .table-wrap {{ overflow:hidden; }} table {{ width:100%; border-collapse:collapse; }}
    thead th {{ position:sticky; top:0; background:#16213b; color:#d9e3ff; padding:12px 10px; font-size:13px; text-align:left; border-bottom:1px solid var(--line); cursor:pointer; }}
    tbody td {{ padding:12px 10px; border-bottom:1px solid rgba(43,61,103,.65); vertical-align:top; font-size:14px; }}
    tbody tr.main-row:hover {{ background:rgba(156,194,255,.08); }}
    tbody tr.detail-row {{ display:none; background:rgba(255,255,255,.02); }} tbody tr.detail-row.open {{ display:table-row; }}
    .rank {{ display:inline-flex; min-width:28px; justify-content:center; border-radius:999px; padding:2px 8px; background:#243761; font-weight:700; }}
    .score {{ color:var(--good); font-weight:700; }}
    .muted {{ color:var(--muted); font-size:12px; }}
    .mono {{ font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }}
    .chip {{ display:inline-block; margin:0 6px 6px 0; padding:2px 8px; border-radius:999px; background:#243761; font-size:12px; }}
    .chip.platform-k {{ background:#4b2e83; }} .chip.platform-p {{ background:#1f5d5b; }} .chip.platform-7 {{ background:#7a3c18; }}
    .chip.t0 {{ background:#6e2b2b; }} .chip.t05 {{ background:#7a4f26; }} .chip.t1 {{ background:#29507a; }} .chip.t2 {{ background:#2b5446; }} .chip.t3 {{ background:#444b63; }} .chip.t4 {{ background:#3f3f3f; }}
    .chip.team {{ background:#345b2f; }}
    .chip.new-round {{ background:#7c5cff; }}
    .chip.status-active {{ background:#245f45; }} .chip.status-sold {{ background:#6f2d32; }} .chip.status-unknown {{ background:#4e587a; }}
    .chip.quality-ok {{ background:#2c4f86; }} .chip.quality-pending {{ background:#7a5a20; }} .chip.quality-failed {{ background:#6f2d32; }}
    .core-tags {{ display:flex; flex-wrap:wrap; gap:6px; min-width:180px; }}
    .compact-role-chip {{ display:inline-flex; align-items:center; gap:4px; margin:0; padding:3px 8px; font-weight:600; line-height:1.1; }}
    .weapon-mark {{ font-size:11px; opacity:0.95; }}
    .detail-grid {{ grid-template-columns:1.15fr 1fr 1fr; padding:12px 6px 18px; }}
    .card h3 {{ margin:0 0 10px; font-size:14px; }} .card p {{ margin:6px 0; color:var(--muted); line-height:1.5; }}
    .list {{ display:flex; flex-wrap:wrap; }} .tier-section {{ margin-bottom:12px; }} .tier-title {{ margin:0 0 8px; font-size:12px; color:#bfcdff; text-transform:uppercase; }}
    @media (max-width: 1200px) {{
      .stats,.controls,.detail-grid,.role-options,.quick-filter-grid {{ grid-template-columns:1fr; }}
      .wrap {{ padding:14px; }} .table-wrap {{ overflow-x:auto; }} table {{ min-width:1400px; }}
      .filter-panel-head,.role-filter-actions {{ flex-direction:column; align-items:flex-start; }}
      .filter-toggle {{ align-items:flex-start; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>鸣潮账号跨平台统一评估</h1>
      <p>合并 `Kejinshou + PZDS + 7881` 三个平台的账号结果，使用同一套角色/武器/资源评分规则统一排序。</p>
      <p>角色分采用三榜合成：综合榜 + 逆境深塔 + 冥歌海墟，并提高 T0 / T0.5 的保值权重；每命中 1 套完整配队额外 +100。</p>
      <p class="mono" style="font-size:12px;color:#9fb0d6;">{meta_json}</p>
      <p style="font-size:12px;color:#9fb0d6;">生成时间：{generated_at}</p>
      <div class="stats" id="stats"></div>
    </section>
    <section class="controls">
      <input id="searchInput" placeholder="搜索：平台 / ID / 角色名 / 武器名 / 描述" />
      <select id="platformFilter">
        <option value="all">全部平台</option>
        <option value="kejinshou">只看 Kejinshou</option>
        <option value="pzds">只看 PZDS</option>
        <option value="7881">只看 7881</option>
      </select>
      <select id="statusFilter">
        <option value="exclude_sold">默认：隐藏已售</option>
        <option value="all">全部状态</option>
        <option value="active">只看在售</option>
        <option value="sold">只看已卖出</option>
        <option value="unknown">只看待确认</option>
      </select>
      <select id="roundFilter">
        <option value="all">全部轮次</option>
      </select>
    </section>
    <section class="filter-drawer">
      <button type="button" class="filter-toggle" id="roleFilterToggle">
        <span class="filter-toggle-main">
          <span class="filter-toggle-title">角色筛选 / 配队快捷筛选</span>
          <span class="filter-toggle-hint">点击后展开一整行筛选区。可先按配队快速带出角色，再继续手动多选、删减、补充。</span>
        </span>
        <span class="filter-toggle-meta">
          <span class="chip filter-chip" id="roleFilterCountChip">未选择</span>
          <span class="filter-toggle-arrow">▾</span>
        </span>
      </button>
      <div class="filter-panel" id="roleFilterPanel">
        <div class="filter-panel-head">
          <div>
            <div class="filter-panel-title">配队快捷筛选</div>
            <div class="filter-panel-hint">快捷筛选会直接联动下面的角色筛选。点一个配队会把对应角色加入当前选择，你还可以继续编辑。</div>
          </div>
          <button type="button" id="clearRoleFilter">清空全部</button>
        </div>
        <div class="quick-filter-grid" id="teamQuickFilters"></div>
        <div class="filter-panel-title">已选角色</div>
        <div class="selected-role-list" id="selectedRoleChips"></div>
        <div class="role-filter-actions">
          <span>勾选后只显示同时拥有所选角色的账号</span>
          <span id="roleFilterSelectionMeta">当前未选择角色</span>
        </div>
        <div class="role-options" id="roleOptions"></div>
      </div>
    </section>
    <div class="toolbar">
      <div id="resultCount"></div>
      <div>点击任意行展开平台、角色、武器与评分拆解</div>
    </div>
    <section class="table-wrap">
      <table>
        <thead>
          <tr>
            <th data-sort="unified_rank">排名</th>
            <th>平台 / ID</th>
            <th data-sort="price">价格</th>
            <th>上架时间</th>
            <th data-sort="level">等级</th>
            <th data-sort="total_yellow">总黄</th>
            <th data-sort="team_count">配队数</th>
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
    const META = {meta_json};
    const state = {{ search:"", platform:"all", sortField:"value_score", sortOrder:"desc", statusFilter:"exclude_sold", roundFilter:"all", selectedRoles:[], roleFilterOpen:false }};
    const el = {{
      searchInput: document.getElementById("searchInput"),
      platformFilter: document.getElementById("platformFilter"),
      statusFilter: document.getElementById("statusFilter"),
      roundFilter: document.getElementById("roundFilter"),
      roleFilterToggle: document.getElementById("roleFilterToggle"),
      roleFilterPanel: document.getElementById("roleFilterPanel"),
      roleFilterCountChip: document.getElementById("roleFilterCountChip"),
      teamQuickFilters: document.getElementById("teamQuickFilters"),
      selectedRoleChips: document.getElementById("selectedRoleChips"),
      roleFilterSelectionMeta: document.getElementById("roleFilterSelectionMeta"),
      roleOptions: document.getElementById("roleOptions"),
      clearRoleFilter: document.getElementById("clearRoleFilter"),
      tableBody: document.getElementById("tableBody"),
      resultCount: document.getElementById("resultCount"),
      stats: document.getElementById("stats"),
    }};
    const ROLE_TIER_ORDER = {{ "T0": 0, "T0.5": 1, "T1": 2, "T2": 3, "T3": 4, "T4": 5, "": 6 }};
    function tierSortValue(tier) {{
      return Object.prototype.hasOwnProperty.call(ROLE_TIER_ORDER, tier) ? ROLE_TIER_ORDER[tier] : 99;
    }}
    const ROLE_META_MAP = DATA.reduce((acc, row) => {{
      (row.roles || []).forEach(role => {{
        const name = String(role.name || "").trim();
        if (!name) return;
        const tier = String(role.tier || "");
        const score = Number(role.score || 0);
        const prev = acc[name];
        if (!prev || tierSortValue(tier) < tierSortValue(prev.tier) || (tierSortValue(tier) === tierSortValue(prev.tier) && score > prev.score)) {{
          acc[name] = {{ tier, score }};
        }}
      }});
      return acc;
    }}, {{}});
    const ROLE_OPTIONS = Array.from(new Set(DATA.flatMap(row => row.roles.map(role => role.name))))
      .sort((a,b) => {{
        const aMeta = ROLE_META_MAP[a] || {{ tier:"", score:0 }};
        const bMeta = ROLE_META_MAP[b] || {{ tier:"", score:0 }};
        const tierDiff = tierSortValue(aMeta.tier) - tierSortValue(bMeta.tier);
        if (tierDiff) return tierDiff;
        if (bMeta.score !== aMeta.score) return bMeta.score - aMeta.score;
        return String(a).localeCompare(String(b), "zh-CN");
      }});
    const ROLE_FILTER_GROUPS = [
      {{ key:"T0", badge:"T0", title:"核心角色" }},
      {{ key:"T0.5", badge:"T0.5", title:"强势角色" }},
      {{ key:"T1", badge:"T1", title:"主力角色" }},
      {{ key:"T2", badge:"T2", title:"补位角色" }},
      {{ key:"OTHER", badge:"其他", title:"其他角色" }},
    ];
    const TEAM_PRESETS = Array.from(DATA.reduce((acc, row) => {{
      (row.matched_teams || []).forEach(team => {{
        const roles = Array.from(new Set((team.matched_roles || []).map(role => String(role || "").trim()).filter(Boolean)))
          .sort((a,b) => ROLE_OPTIONS.indexOf(a) - ROLE_OPTIONS.indexOf(b) || String(a).localeCompare(String(b), "zh-CN"));
        if (!roles.length) return;
        const system = String(team.system || "配队");
        const name = String(team.team_name || roles.join(" + "));
        const key = `${{system}}::${{name}}::${{roles.join("|")}}`;
        const prev = acc.get(key) || {{ key, system, name, roles, count:0 }};
        prev.count += 1;
        acc.set(key, prev);
      }});
      return acc;
    }}, new Map()).values()).sort((a,b) => {{
      if (b.count !== a.count) return b.count - a.count;
      if (b.roles.length !== a.roles.length) return b.roles.length - a.roles.length;
      return String(a.name).localeCompare(String(b.name), "zh-CN");
    }});
    const ROUND_OPTIONS = Array.from(new Set(DATA.map(row => String(row.round_id || "").trim()).filter(Boolean)))
      .sort((a,b) => String(b).localeCompare(String(a), "zh-CN"));
    function sortSelectedRoles(list) {{
      return Array.from(new Set(list))
        .filter(role => ROLE_OPTIONS.includes(role))
        .sort((a,b) => ROLE_OPTIONS.indexOf(a) - ROLE_OPTIONS.indexOf(b) || String(a).localeCompare(String(b), "zh-CN"));
    }}
    function teamPresetActive(preset) {{
      return preset.roles.every(role => state.selectedRoles.includes(role));
    }}
    function rolesInGroup(groupKey) {{
      return ROLE_OPTIONS.filter(role => {{
        const tier = String((ROLE_META_MAP[role] || {{ tier:"" }}).tier || "");
        if (groupKey === "OTHER") return !["T0", "T0.5", "T1", "T2"].includes(tier);
        return tier === groupKey;
      }});
    }}
    function fmt(n,d=2) {{ return Number(n).toFixed(d); }}
    function platformChip(platform) {{
      const cls = platform === "kejinshou" ? "platform-k" : platform === "pzds" ? "platform-p" : "platform-7";
      return `<span class="chip ${{cls}}">${{platform}}</span>`;
    }}
    function marketStatusLabel(row) {{
      return row.market_status === "sold" ? "已卖出" : row.market_status === "active" ? "在售" : "待确认";
    }}
    function marketStatusChip(row) {{
      const cls = row.market_status === "sold" ? "status-sold" : row.market_status === "active" ? "status-active" : "status-unknown";
      return `<span class="chip ${{cls}}">${{marketStatusLabel(row)}}</span>`;
    }}
    function qualityChip(row) {{
      if (row.data_quality === "ok") return "";
      const cls = row.data_quality === "incremental_snapshot_pending" ? "quality-pending" : "quality-failed";
      return `<span class="chip ${{cls}}" title="${{row.parse_failed_reason || ''}}">${{row.detail_fetch_label || row.quality_label || "待处理"}}</span>`;
    }}
    function roundChip(row) {{
      return row.round_id ? `<span class="chip new-round">轮次 ${{row.round_id}}</span>` : "";
    }}
    function scoreText(row, field, digits=2) {{
      return row.can_rank === false ? '<span class="muted">-</span>' : `<span class="score">${{fmt(row[field], digits)}}</span>`;
    }}
    function plainScoreText(row, field, digits=2) {{
      return row.can_rank === false ? '<span class="muted">-</span>' : fmt(row[field], digits);
    }}
    function detailStrengthText(row) {{
      if (row.can_rank === false) return "待补/失败，暂不计分";
      return `${{fmt(row.strength_score,2)}} = 抽数分 ${{fmt(row.resources.pulls_total,2)}} + 角色分 ${{fmt(row.role_score_total,2)}} + 武器分 ${{fmt(row.weapon_score_total,2)}} + 配队加分 ${{fmt(row.team_bonus || 0,2)}}`;
    }}
    function detailValueText(row) {{
      if (row.can_rank === false) return "待补/失败，暂不展示";
      return `${{fmt(row.value_score,3)}} = 强度分 / 价格`;
    }}
    function roleTierClass(tier) {{
      return tier === "T0" ? "t0" : tier === "T0.5" ? "t05" : tier === "T1" ? "t1" : tier === "T2" ? "t2" : tier === "T3" ? "t3" : "t4";
    }}
    function roleChip(role) {{
      const cls = roleTierClass(role.tier || "");
      const tierLabel = role.tier ? role.tier : role.star;
      return `<span class="chip ${{cls}}">${{role.name}} ${{tierLabel}} ${{role.resonance}}鸣 = ${{fmt(role.score,0)}} | 综${{role.overall_tier || "-"}} / 塔${{role.tower_grade || "-"}} / 冥${{role.requiem_grade || "-"}}</span>`;
    }}
    function signatureOwnerSet(weapons) {{
      return new Set((weapons || []).map(weapon => String(weapon.owner_character || "").trim()).filter(Boolean));
    }}
    function compactRoleSummary(row) {{
      const ownerSet = signatureOwnerSet(row.weapons);
      const roles = row.roles
        .filter(role => ["T0", "T0.5", "T1"].includes(role.tier || ""))
        .sort((a,b) => {{
          const tierDiff = tierSortValue(a.tier || "") - tierSortValue(b.tier || "");
          if (tierDiff) return tierDiff;
          if ((b.score || 0) !== (a.score || 0)) return (b.score || 0) - (a.score || 0);
          return String(a.name).localeCompare(String(b.name), "zh-CN");
        }});
      if (!roles.length) return '<span class="muted">-</span>';
      return `<div class="core-tags">${{roles.map(role => {{
        const hasSignature = ownerSet.has(role.name);
        const mark = hasSignature ? '<span class="weapon-mark" title="有专武">🔪</span>' : "";
        const cls = roleTierClass(role.tier || "");
        const title = `${{role.name}} / ${{role.tier || role.star || "-"}} / ${{role.resonance}}共鸣${{hasSignature ? " / 有专武" : ""}}`;
        return `<span class="chip compact-role-chip ${{cls}}" title="${{title}}">${{role.name}}${{role.resonance}} ${{mark}}</span>`;
      }}).join("")}}</div>`;
    }}
    function renderRoleSections(roles) {{
      const groups = [["T0","T0 角色"],["T0.5","T0.5 角色"],["T1","T1 角色"],["T2","T2 角色"],["T3","T3 角色"],["T4","T4 角色"],["","未命中梯度"]];
      return groups.map(([tier,title]) => {{
        const list = roles.filter(r => (r.tier || "") === tier).sort((a,b) => (b.score||0)-(a.score||0) || String(a.name).localeCompare(String(b.name), "zh-CN"));
        if (!list.length) return "";
        return `<div class="tier-section"><div class="tier-title">${{title}}</div><div class="list">${{list.map(roleChip).join("")}}</div></div>`;
      }}).join("");
    }}
    function weaponChip(w) {{
      const owner = w.owner_character ? `${{w.owner_character}}/${{w.owner_tier || "未分档"}}` : "常驻";
      const refine = (w.effective_refine !== undefined) ? `显示${{w.refine || w.resonance}}精/计分${{w.effective_refine}}层` : `显示${{w.resonance}}鸣`;
      return `<span class="chip">${{w.name}} [${{w.weapon_class || "unknown"}}] -> ${{owner}} ${{refine}} = ${{fmt(w.score,0)}}</span>`;
    }}
    function teamChip(team) {{
      return `<span class="chip team">${{team.system}} / ${{team.team_name}} / ${{team.matched_roles.join(" + ")}}</span>`;
    }}
    function searchable(row) {{
      return [row.platform,row.product_id,row.round_id || "",row.detail_url || "",row.summary || "",row.security_summary || "",row.listing_time || "",row.listing_time_desc || "",row.market_status || "",row.roles.map(r=>r.name).join(" "),row.weapons.map(w=>w.name).join(" "), (row.matched_teams || []).map(t => t.team_name).join(" ")].join(" ").toLowerCase();
    }}
    function renderRoundFilter() {{
      const current = state.roundFilter;
      el.roundFilter.innerHTML = ['<option value="all">全部轮次</option>']
        .concat(ROUND_OPTIONS.map(roundId => `<option value="${{roundId}}">${{roundId}}</option>`))
        .join("");
      el.roundFilter.value = ROUND_OPTIONS.includes(current) || current === "all" ? current : "all";
    }}
    function renderTeamQuickFilters() {{
      if (!TEAM_PRESETS.length) {{
        el.teamQuickFilters.innerHTML = '<div class="selected-role-empty">当前没有可用的配队快捷筛选</div>';
        return;
      }}
      el.teamQuickFilters.innerHTML = TEAM_PRESETS.map(preset => {{
        const active = teamPresetActive(preset) ? "active" : "";
        return `<button type="button" class="quick-filter-btn ${{active}}" data-team-key="${{preset.key}}">
          <span class="quick-filter-system">${{preset.system}}</span>
          <span class="quick-filter-name">${{preset.name}}</span>
          <span class="quick-filter-roles">${{preset.roles.join(" + ")}}</span>
          <span class="quick-filter-count">命中 ${{preset.count}} 条</span>
        </button>`;
      }}).join("");
      el.teamQuickFilters.querySelectorAll("[data-team-key]").forEach(button => {{
        button.addEventListener("click", () => {{
          const preset = TEAM_PRESETS.find(item => item.key === button.dataset.teamKey);
          if (!preset) return;
          const selected = new Set(state.selectedRoles);
          const active = preset.roles.every(role => selected.has(role));
          if (active) preset.roles.forEach(role => selected.delete(role));
          else preset.roles.forEach(role => selected.add(role));
          state.selectedRoles = sortSelectedRoles(Array.from(selected));
          state.roleFilterOpen = true;
          render();
        }});
      }});
    }}
    function renderSelectedRoleChips() {{
      if (!state.selectedRoles.length) {{
        el.selectedRoleChips.innerHTML = '<span class="selected-role-empty">还没有选择角色，可直接勾选，也可先点上面的配队快捷筛选。</span>';
        return;
      }}
      el.selectedRoleChips.innerHTML = state.selectedRoles.map(role => {{
        const meta = ROLE_META_MAP[role] || {{ tier:"" }};
        const tierText = meta.tier ? `<span class="role-option-tier">${{meta.tier}}</span>` : "";
        return `<span class="selected-role-chip">${{role}} ${{tierText}} <button type="button" data-role-remove="${{role}}" aria-label="移除 ${{role}}">×</button></span>`;
      }}).join("");
      el.selectedRoleChips.querySelectorAll("[data-role-remove]").forEach(button => {{
        button.addEventListener("click", () => {{
          state.selectedRoles = state.selectedRoles.filter(role => role !== button.dataset.roleRemove);
          render();
        }});
      }});
    }}
    function renderRoleFilter() {{
      el.roleFilterToggle.classList.toggle("open", state.roleFilterOpen);
      el.roleFilterPanel.classList.toggle("open", state.roleFilterOpen);
      el.roleFilterCountChip.textContent = state.selectedRoles.length ? `已选 ${{state.selectedRoles.length}} 个角色` : "未选择";
      el.roleFilterSelectionMeta.textContent = state.selectedRoles.length ? `当前选择 ${{state.selectedRoles.length}} 个角色` : "当前未选择角色";
      renderTeamQuickFilters();
      renderSelectedRoleChips();
      el.roleOptions.innerHTML = ROLE_FILTER_GROUPS.map(group => {{
        const roles = rolesInGroup(group.key);
        if (!roles.length) return "";
        return `<section class="role-group">
          <div class="role-group-title">
            <span><span class="role-group-badge">${{group.badge}}</span> ${{group.title}}</span>
            <span class="role-group-count">${{roles.length}} 个</span>
          </div>
          <div class="role-group-options">
            ${{
              roles.map(role => {{
                const checked = state.selectedRoles.includes(role) ? "checked" : "";
                const meta = ROLE_META_MAP[role] || {{ tier:"", score:0 }};
                const tierText = meta.tier ? `<em class="role-option-tier">${{meta.tier}}</em>` : "";
                return `<label class="role-option"><input type="checkbox" value="${{role}}" ${{checked}} /> <span>${{role}} ${{tierText}}</span></label>`;
              }}).join("")
            }}
          </div>
        </section>`;
      }}).join("");
      el.roleOptions.querySelectorAll('input[type="checkbox"]').forEach(input => {{
        input.addEventListener("change", e => {{
          const value = e.target.value;
          if (e.target.checked) {{
            state.selectedRoles = sortSelectedRoles([...state.selectedRoles, value]);
          }} else {{
            state.selectedRoles = state.selectedRoles.filter(role => role !== value);
          }}
          state.roleFilterOpen = true;
          render();
        }});
      }});
    }}
    function filteredRows() {{
      let rows = DATA.slice();
      if (state.platform !== "all") rows = rows.filter(r => r.platform === state.platform);
      const kw = state.search.trim().toLowerCase();
      if (kw) rows = rows.filter(r => searchable(r).includes(kw));
      if (state.selectedRoles.length) {{
        rows = rows.filter(row => {{
          const roleSet = new Set(row.roles.map(role => role.name));
          return state.selectedRoles.every(role => roleSet.has(role));
        }});
      }}
      if (state.statusFilter === "exclude_sold") {{
        rows = rows.filter(row => (row.market_status || "unknown") !== "sold");
      }} else if (state.statusFilter !== "all") {{
        rows = rows.filter(row => (row.market_status || "unknown") === state.statusFilter);
      }}
      if (state.roundFilter !== "all") {{
        rows = rows.filter(row => String(row.round_id || "") === state.roundFilter);
      }}
      rows.sort((a,b) => {{
        const aRankable = a.can_rank !== false;
        const bRankable = b.can_rank !== false;
        if (aRankable !== bRankable) return bRankable ? 1 : -1;
        const av = Number(a[state.sortField] || 0), bv = Number(b[state.sortField] || 0);
        const aRank = Number(a.unified_rank || 999999), bRank = Number(b.unified_rank || 999999);
        if (av === bv) return aRank - bRank;
        return state.sortOrder === "desc" ? (bv - av) : (av - bv);
      }});
      return rows;
    }}
    function buildStats(rows) {{
      const rankableRows = rows.filter(row => row.can_rank !== false);
      const avgValue = rankableRows.reduce((s,x)=>s+x.value_score,0)/(rankableRows.length||1);
      const avgStrength = rankableRows.reduce((s,x)=>s+x.strength_score,0)/(rankableRows.length||1);
      const avgTeamCount = rankableRows.reduce((s,x)=>s+(x.team_count || 0),0)/(rankableRows.length||1);
      const kejin = rows.filter(x=>x.platform==='kejinshou').length;
      const pzds = rows.filter(x=>x.platform==='pzds').length;
      const p7881 = rows.filter(x=>x.platform==='7881').length;
      const currentRound = META.rounds && META.rounds.current ? META.rounds.current : (ROUND_OPTIONS[0] || "-");
      const filteredRound = state.roundFilter === "all" ? "全部轮次" : state.roundFilter;
      const best = rankableRows[0];
      const cards = [
        {{k:"账号数",v:rows.length}},
        {{k:"当前轮次",v:currentRound}},
        {{k:"轮次数",v:ROUND_OPTIONS.length}},
        {{k:"筛选轮次",v:filteredRound}},
        {{k:"Kejinshou 数量",v:kejin}},
        {{k:"PZDS 数量",v:pzds}},
        {{k:"7881 数量",v:p7881}},
        {{k:"平均配队数",v:fmt(avgTeamCount,2)}},
        {{k:"平均性价比分",v:fmt(avgValue,3)}},
        {{k:"已卖出",v:rows.filter(row => row.market_status === "sold").length}},
        {{k:"待补/失败",v:rows.filter(row => row.can_rank === false).length}},
        {{k:"当前第一名",v:best ? `${{best.platform}}/${{best.product_id}}` : "-"}}
      ];
      el.stats.innerHTML = cards.map(card => `<div class="stat"><div class="k">${{card.k}}</div><div class="v">${{card.v}}</div></div>`).join("");
    }}
    function render() {{
      renderRoleFilter();
      const rows = filteredRows();
      buildStats(rows);
      const roundSummary = state.roundFilter === "all"
        ? `全部轮次 / 共 ${{ROUND_OPTIONS.length}} 个轮次`
        : `轮次 ${{state.roundFilter}}`;
      el.resultCount.textContent = `当前展示 ${{rows.length}} 条 / ${{roundSummary}}`;
      el.tableBody.innerHTML = rows.map((row, idx) => {{
        const rid = `detail-${{row.platform}}-${{row.product_id}}-${{idx}}`;
        return `
          <tr class="main-row" data-target="${{rid}}">
            <td><span class="rank">${{row.unified_rank || "-"}}</span></td>
            <td>${{platformChip(row.platform)}}<div class="mono">${{row.product_id}}</div><div><a href="${{row.detail_url}}" target="_blank" rel="noreferrer">打开详情页</a></div></td>
            <td>${{fmt(row.price,0)}}</td>
            <td>${{row.listing_time || "-"}}<div class="muted">${{row.listing_time_desc || "-"}}</div></td>
            <td>${{row.level}}</td>
            <td>${{row.total_yellow}}</td>
            <td>${{row.team_count || 0}}</td>
            <td>${{fmt(row.resources.pulls_total,2)}}</td>
            <td>${{plainScoreText(row, "role_score_total", 2)}}</td>
            <td>${{plainScoreText(row, "weapon_score_total", 2)}}</td>
            <td>${{scoreText(row, "strength_score", 2)}}</td>
            <td>${{scoreText(row, "value_score", 3)}}</td>
            <td>${{marketStatusChip(row)}}${{roundChip(row)}}${{qualityChip(row)}}</td>
            <td>${{compactRoleSummary(row)}}</td>
          </tr>
          <tr class="detail-row" id="${{rid}}">
            <td colspan="14">
              <div class="detail-grid">
                <div class="card">
                  <h3>评分拆解</h3>
                  <p><strong>平台：</strong>${{row.platform}}</p>
                  <p><strong>轮次：</strong>${{row.round_id || "-"}}</p>
                  <p><strong>详情状态：</strong>${{row.detail_fetch_label || row.quality_label || "正常"}} <span class="muted">${{row.parse_failed_reason || ""}}</span></p>
                  <p><strong>上架时间：</strong>${{row.listing_time || "-"}} <span class="muted">${{row.listing_time_desc || ""}}</span></p>
                  <p><strong>在售状态：</strong>${{marketStatusLabel(row)}} <span class="muted">${{row.status_reason || ""}} / ${{row.status_checked_at || "-"}}</span></p>
                  <p><strong>强度分：</strong>${{detailStrengthText(row)}}</p>
                  <p><strong>性价比分：</strong>${{detailValueText(row)}}</p>
                  <p><strong>资源：</strong>星声 ${{row.resources.star_voice || 0}} / 浮金 ${{row.resources.fj_waves || 0}} / 唤声 ${{row.resources.hs_waves || 0}} / 铸潮 ${{row.resources.zc_waves || 0}}</p>
                  <p><strong>摘要：</strong>${{row.summary || "-"}}</p>
                  <p><strong>附加描述：</strong>${{row.security_summary || "-"}}</p>
                  <p><strong>命中配队：</strong>${{row.team_count || 0}} 套</p>
                  <div class="list">${{(row.matched_teams || []).map(teamChip).join("") || '<span>无</span>'}}</div>
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
    el.platformFilter.addEventListener("change", e => {{ state.platform = e.target.value; render(); }});
    el.statusFilter.addEventListener("change", e => {{ state.statusFilter = e.target.value; render(); }});
    el.roundFilter.addEventListener("change", e => {{ state.roundFilter = e.target.value; render(); }});
    el.roleFilterToggle.addEventListener("click", () => {{
      state.roleFilterOpen = !state.roleFilterOpen;
      render();
    }});
    el.clearRoleFilter.addEventListener("click", () => {{
      state.selectedRoles = [];
      state.roleFilterOpen = true;
      render();
    }});
    document.querySelectorAll("th[data-sort]").forEach(th => {{
      th.addEventListener("click", () => {{
        const f = th.dataset.sort;
        if (state.sortField === f) state.sortOrder = state.sortOrder === "desc" ? "asc" : "desc";
        else state.sortField = f;
        render();
      }});
    }});
    renderRoundFilter();
    render();
  </script>
</body>
</html>
"""


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    team_config = _load_team_configs(base_dir / "configs" / "wuwa_team_synergy_33.json")
    out_json = base_dir / "outputs" / "wuwa_unified_scored.json"
    out_csv = base_dir / "outputs" / "wuwa_unified_scored.csv"
    out_html = base_dir / "outputs" / "wuwa_unified_review.html"
    current_round_id = _resolve_current_round_id()

    kejin_rows = _build_kejin_rows(base_dir)
    pzds_rows = _build_pzds_rows(base_dir)
    rows_7881 = _build_7881_rows(base_dir)
    incremental_rows = _build_incremental_snapshot_rows(base_dir)
    fresh_rows = kejin_rows + pzds_rows + rows_7881 + incremental_rows
    _match_teams(fresh_rows, team_config)

    existing_rows: List[Dict[str, Any]] = []
    if out_json.exists():
        existing_rows = _load_json(out_json).get("items", [])

    previous_keys = {
        f"{_repair_row_identity(row)['platform']}::{_repair_row_identity(row)['product_id']}"
        for row in existing_rows
    }
    merged_rows = _merge_rows(existing_rows, fresh_rows, current_round_id=current_round_id)
    rows = []
    for row in merged_rows:
        item = dict(row)
        row_key = f"{item['platform']}::{item['product_id']}"
        item["is_new_this_round"] = (
            bool(item.get("is_new_this_round"))
            or bool(item.get("new_by_snapshot"))
            or row_key not in previous_keys
        )
        if item["is_new_this_round"]:
            item["round_id"] = current_round_id
        else:
            item["round_id"] = _infer_round_id(item) or current_round_id
        item["is_new_this_round"] = item["round_id"] == current_round_id
        rows.append(_annotate_row_quality(item))

    excluded_incomplete_rows = [
        row
        for row in rows
        if row.get("source_type") == "incremental_snapshot"
        and str(row.get("detail_fetch_status") or "") in {"pending", "missing"}
        and float(row.get("strength_score") or 0) == 0
        and float(row.get("value_score") or 0) == 0
    ]
    rows = [row for row in rows if row not in excluded_incomplete_rows]

    (out_json.parent / "wuwa_unified_excluded_incomplete_rows.json").write_text(
        json.dumps(
            {
                "meta": {
                    "count": len(excluded_incomplete_rows),
                    "generated_at": datetime.now().isoformat(timespec="seconds"),
                    "reason": "excluded_incremental_placeholder_without_full_score",
                },
                "items": excluded_incomplete_rows,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    rankable_rows = [row for row in rows if row.get("can_rank", True)]
    non_rankable_rows = [row for row in rows if not row.get("can_rank", True)]
    value_ranked_scored = sorted(rankable_rows, key=lambda x: (x["value_score"], x["strength_score"]), reverse=True)
    strength_ranked = sorted(rankable_rows, key=lambda x: (x["strength_score"], x["value_score"]), reverse=True)
    strength_rank_map = {f"{x['platform']}::{x['product_id']}": i for i, x in enumerate(strength_ranked, start=1)}
    for i, row in enumerate(value_ranked_scored, start=1):
        row["unified_rank"] = i
        row["strength_rank"] = strength_rank_map[f"{row['platform']}::{row['product_id']}"]
    for row in non_rankable_rows:
        row["unified_rank"] = ""
        row["strength_rank"] = ""
    value_ranked = value_ranked_scored + sorted(
        non_rankable_rows,
        key=lambda x: (
            x.get("data_quality", ""),
            x.get("last_seen_at", ""),
            x.get("status_checked_at", ""),
            x.get("platform", ""),
            x.get("product_id", ""),
        ),
        reverse=True,
    )
    round_counts: Dict[str, Dict[str, Any]] = {}
    for row in value_ranked:
        round_id = str(row.get("round_id") or "")
        if not round_id:
            continue
        bucket = round_counts.setdefault(
            round_id,
            {"total": 0, "platforms": {"kejinshou": 0, "pzds": 0, "7881": 0}},
        )
        bucket["total"] += 1
        if row["platform"] in bucket["platforms"]:
            bucket["platforms"][row["platform"]] += 1
    available_rounds = sorted(round_counts.keys(), reverse=True)

    out_json.write_text(
        json.dumps(
            {
                "meta": {
                    "generatedAt": datetime.now().strftime("%Y%m%d_%H%M%S"),
                    "currentRoundId": current_round_id,
                    "platforms": {"kejinshou": len(kejin_rows), "pzds": len(pzds_rows), "7881": len(rows_7881)},
                    "historyPlatforms": {
                        "kejinshou": sum(1 for row in value_ranked if row["platform"] == "kejinshou"),
                        "pzds": sum(1 for row in value_ranked if row["platform"] == "pzds"),
                        "7881": sum(1 for row in value_ranked if row["platform"] == "7881"),
                    },
                    "rankableRows": len(value_ranked_scored),
                    "nonRankableRows": len(non_rankable_rows),
                    "dataQuality": {
                        "ok": sum(1 for row in value_ranked if row.get("data_quality") == "ok"),
                        "incremental_snapshot_pending": sum(1 for row in value_ranked if row.get("data_quality") == "incremental_snapshot_pending"),
                        "parse_failed": sum(1 for row in value_ranked if str(row.get("data_quality", "")).startswith("parse_failed")),
                    },
                    "excludedIncompleteRows": len(excluded_incomplete_rows),
                    "rounds": {
                        "current": current_round_id,
                        "available": available_rounds,
                        "counts": round_counts,
                    },
                    "incrementalSnapshotRows": len(incremental_rows),
                    "teamSynergy": {
                        "configFile": str(base_dir / "configs" / "wuwa_team_synergy_33.json"),
                        "bonusPerTeam": team_config.get("meta", {}).get("bonus_per_team", 100),
                    },
                },
                "items": value_ranked,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    header = [
        "unified_rank",
        "strength_rank",
        "platform",
        "product_id",
        "round_id",
        "price",
        "listing_time",
        "listing_time_desc",
        "level",
        "total_yellow",
        "team_count",
        "team_bonus",
        "pulls_total",
        "role_score_total",
        "weapon_score_total",
        "strength_score",
        "value_score",
        "detail_url",
    ]
    csv_rows = []
    for row in value_ranked:
        csv_rows.append(
            [
                row["unified_rank"],
                row["strength_rank"],
                row["platform"],
                row["product_id"],
                row.get("round_id", ""),
                row["price"],
                row.get("listing_time", ""),
                row.get("listing_time_desc", ""),
                row["level"],
                row["total_yellow"],
                row.get("team_count", 0),
                row.get("team_bonus", 0),
                row["resources"]["pulls_total"],
                row["role_score_total"],
                row["weapon_score_total"],
                row["strength_score"],
                row["value_score"],
                row["detail_url"],
            ]
        )
    _write_csv(out_csv, header, csv_rows)

    out_html.write_text(
        _html_template(
            value_ranked,
            {
                "currentRoundId": current_round_id,
                "platforms": {"kejinshou": len(kejin_rows), "pzds": len(pzds_rows), "7881": len(rows_7881)},
                "historyPlatforms": {
                    "kejinshou": sum(1 for row in value_ranked if row["platform"] == "kejinshou"),
                    "pzds": sum(1 for row in value_ranked if row["platform"] == "pzds"),
                    "7881": sum(1 for row in value_ranked if row["platform"] == "7881"),
                },
                "rankableRows": len(value_ranked_scored),
                "nonRankableRows": len(non_rankable_rows),
                "dataQuality": {
                    "ok": sum(1 for row in value_ranked if row.get("data_quality") == "ok"),
                    "incremental_snapshot_pending": sum(1 for row in value_ranked if row.get("data_quality") == "incremental_snapshot_pending"),
                    "parse_failed": sum(1 for row in value_ranked if str(row.get("data_quality", "")).startswith("parse_failed")),
                },
                "excludedIncompleteRows": len(excluded_incomplete_rows),
                "rounds": {
                    "current": current_round_id,
                    "available": available_rounds,
                    "counts": round_counts,
                },
                "incrementalSnapshotRows": len(incremental_rows),
                "teamSynergy": {"bonusPerTeam": team_config.get("meta", {}).get("bonus_per_team", 100)},
            },
        ),
        encoding="utf-8",
    )

    print(out_json)
    print(out_csv)
    print(out_html)


if __name__ == "__main__":
    main()
