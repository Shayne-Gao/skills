import json
import os
import re
import urllib.error
import urllib.request
from http.client import RemoteDisconnected
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from generate_unified_wuwa_review import _html_template, _write_csv


USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
TIMEOUT_SECONDS = 20
MAX_WORKERS = 10
PZDS_SOLD_RE = re.compile(r'<div class="sold"[^>]*>\s*已下架\s*</div>', re.I)


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _now_iso() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def _latest_file(raw_dir: Path, pattern: str) -> Optional[Path]:
    matches = sorted(raw_dir.glob(pattern), key=lambda p: p.stat().st_mtime)
    return matches[-1] if matches else None


def _resolve_skip_platforms() -> List[str]:
    raw = os.environ.get("STATUS_REFRESH_SKIP_PLATFORMS", "")
    return [part.strip() for part in raw.split(",") if part.strip()]


def _fetch_text(url: str) -> Tuple[int, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            body = response.read().decode("utf-8", "ignore")
            return int(response.getcode() or 200), body
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "ignore") if exc.fp else ""
        return exc.code, body
    except (urllib.error.URLError, TimeoutError, ConnectionError, RemoteDisconnected):
        return 0, ""
    except Exception:
        return 0, ""


def _classify_status(platform: str, status_code: int, text: str) -> Dict[str, Any]:
    text = text or ""
    if "aliyun_waf_aa" in text or "window._waf_is_mobile" in text:
        return {"market_status": "unknown", "is_sold": False, "status_reason": "waf_blocked"}
    if platform == "pzds":
        if status_code in {404, 410}:
            return {"market_status": "sold", "is_sold": True, "status_reason": f"http_{status_code}"}
        if PZDS_SOLD_RE.search(text):
            return {"market_status": "sold", "is_sold": True, "status_reason": "detail_overlay_已下架"}
        if any(token in text for token in ["立即购买", "下单", "联系客服"]):
            return {"market_status": "active", "is_sold": False, "status_reason": "buy_action_present"}
        return {"market_status": "unknown", "is_sold": False, "status_reason": "no_strong_signal"}

    if platform == "7881":
        if status_code in {404, 410}:
            return {"market_status": "sold", "is_sold": True, "status_reason": f"http_{status_code}"}
        if any(token in text for token in ["已出售", "已下架", "该商品已下架", "已被购买", "商品不存在", "已售"]):
            return {"market_status": "sold", "is_sold": True, "status_reason": "detail_keyword"}
        if "立即购买" in text:
            return {"market_status": "active", "is_sold": False, "status_reason": "buy_action_present"}
        return {"market_status": "unknown", "is_sold": False, "status_reason": "no_strong_signal"}

    if status_code in {404, 410}:
        return {"market_status": "sold", "is_sold": True, "status_reason": f"http_{status_code}"}
    if any(token in text for token in ["已出售", "已下架", "商品不存在", "已被购买", "已售"]):
        return {"market_status": "sold", "is_sold": True, "status_reason": "detail_keyword"}
    if any(token in text for token in ["购买", "联系客服"]):
        return {"market_status": "active", "is_sold": False, "status_reason": "buy_action_present"}
    return {"market_status": "unknown", "is_sold": False, "status_reason": "no_strong_signal"}


def _check_one(platform: str, product_id: str, detail_url: str) -> Tuple[str, Dict[str, Any]]:
    status_code, text = _fetch_text(detail_url)
    result = _classify_status(platform=platform, status_code=status_code, text=text)
    result.update(
        {
            "product_id": product_id,
            "detail_url": detail_url,
            "status_code": status_code,
            "status_checked_at": _now_iso(),
            "status_source": "live_detail_check",
        }
    )
    return product_id, result


def _refresh_items(platform: str, items: List[Dict[str, Any]], detail_url_builder) -> Dict[str, Dict[str, Any]]:
    status_map: Dict[str, Dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_map = {}
        for item in items:
            product_id = str(item.get("product_id") or "")
            if not product_id:
                continue
            detail_url = detail_url_builder(item)
            future = executor.submit(_check_one, platform, product_id, detail_url)
            future_map[future] = product_id

        for future in as_completed(future_map):
            product_id, result = future.result()
            status_map[product_id] = result
    return status_map


def _apply_status(items: Iterable[Dict[str, Any]], status_map: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in items:
        product_id = str(item.get("product_id") or "")
        status = status_map.get(product_id, {})
        enriched = dict(item)
        if status:
            # Once sold, always sold. Do not regress confirmed sold rows back to unknown/active.
            prev_sold = bool(enriched.get("is_sold")) or str(enriched.get("market_status") or "") == "sold"
            next_sold = bool(status["is_sold"]) or str(status.get("market_status") or "") == "sold"
            if prev_sold and not next_sold:
                status = dict(status)
                status["market_status"] = "sold"
                status["is_sold"] = True
                status["status_reason"] = f"sticky_prev_sold__{status.get('status_reason', '')}".strip("_")
            # Only treat unknown as active when the row is visible in the latest source snapshot.
            elif status.get("market_status") == "unknown" and bool(enriched.get("visible_in_latest_snapshot")):
                status = dict(status)
                status["market_status"] = "active"
                status["is_sold"] = False
                status["status_reason"] = f"visible_in_current_source__{status.get('status_reason', '')}".strip("_")
            enriched.update(
                {
                    "market_status": status["market_status"],
                    "is_sold": bool(status["is_sold"]),
                    "status_reason": status["status_reason"],
                    "status_code": status["status_code"],
                    "status_checked_at": status["status_checked_at"],
                    "status_source": status["status_source"],
                }
            )
        out.append(enriched)
    return out


def _build_price_map(base_dir: Path) -> Dict[str, Dict[str, Dict[str, Any]]]:
    raw_dir = base_dir / "data" / "raw"
    price_map: Dict[str, Dict[str, Dict[str, Any]]] = {
        "kejinshou": {},
        "pzds": {},
        "7881": {},
    }

    kjs_path = _latest_file(raw_dir, "kejinshou_incremental_page1_*.json")
    if kjs_path:
        obj = _load_json(kjs_path)
        for item in obj.get("items", []):
            product_id = str(item.get("id") or "")
            if product_id:
                price_map["kejinshou"][product_id] = {
                    "price": float(item.get("price") or 0),
                    "listing_time": str(item.get("upper_at") or ""),
                    "listing_time_desc": str(item.get("polish_time_desc") or ""),
                }

    pzds_path = _latest_file(raw_dir, "pzds_incremental_page1_*.json")
    if pzds_path:
        obj = _load_json(pzds_path)
        for item in obj.get("items", []):
            product_id = str(item.get("id") or "")
            if product_id:
                price_map["pzds"][product_id] = {
                    "price": float(item.get("price") or 0),
                    "listing_time_desc": str(item.get("publish_text") or ""),
                }

    t7881_path = _latest_file(raw_dir, "7881_incremental_page1_*.json")
    if t7881_path:
        obj = _load_json(t7881_path)
        for item in obj.get("items", []):
            product_id = str(item.get("goods_id") or item.get("id") or "")
            if product_id:
                price_map["7881"][product_id] = {
                    "price": float(item.get("price") or 0),
                    "listing_time_desc": str(item.get("publish_text") or ""),
                }

    return price_map


def _apply_price_updates(platform: str, items: Iterable[Dict[str, Any]], price_map: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in items:
        product_id = str(item.get("product_id") or "")
        enriched = dict(item)
        patch = price_map.get(product_id)
        if patch:
            enriched["visible_in_latest_snapshot"] = True
            if patch.get("price"):
                enriched["price"] = float(patch["price"])
            if patch.get("listing_time"):
                enriched["listing_time"] = patch["listing_time"]
            if patch.get("listing_time_desc"):
                enriched["listing_time_desc"] = patch["listing_time_desc"]
            enriched["price_checked_at"] = _now_iso()
            enriched["price_source"] = f"latest_{platform}_incremental_snapshot"
        else:
            enriched["visible_in_latest_snapshot"] = False
        out.append(enriched)
    return out


def _status_summary(items: List[Dict[str, Any]]) -> Dict[str, int]:
    counts = {"active": 0, "sold": 0, "unknown": 0}
    for item in items:
        state = str(item.get("market_status") or "unknown")
        counts[state] = counts.get(state, 0) + 1
    return counts


def _status_summary_by_platform(items: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {"kejinshou": [], "pzds": [], "7881": []}
    for item in items:
        platform = str(item.get("platform") or "")
        if platform in grouped:
            grouped[platform].append(item)
    return {platform: _status_summary(rows) for platform, rows in grouped.items()}


def _rebuild_unified_outputs_from_current_json(base_dir: Path, unified_obj: Dict[str, Any]) -> None:
    outputs_dir = base_dir / "outputs"
    out_csv = outputs_dir / "wuwa_unified_scored.csv"
    out_html = outputs_dir / "wuwa_unified_review.html"
    rows = list(unified_obj.get("items", []))
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
    for row in rows:
        resources = row.get("resources") or {}
        csv_rows.append(
            [
                row.get("unified_rank", ""),
                row.get("strength_rank", ""),
                row.get("platform", ""),
                row.get("product_id", ""),
                row.get("round_id", ""),
                row.get("price", ""),
                row.get("listing_time", ""),
                row.get("listing_time_desc", ""),
                row.get("level", ""),
                row.get("total_yellow", ""),
                row.get("team_count", 0),
                row.get("team_bonus", 0),
                resources.get("pulls_total", ""),
                row.get("role_score_total", ""),
                row.get("weapon_score_total", ""),
                row.get("strength_score", ""),
                row.get("value_score", ""),
                row.get("detail_url", ""),
            ]
        )
    _write_csv(out_csv, header, csv_rows)
    out_html.write_text(_html_template(rows, unified_obj.get("meta", {})), encoding="utf-8")


def _refresh_unified(
    base_dir: Path,
    latest_price_map: Dict[str, Dict[str, Dict[str, Any]]],
    checked_at: str,
    skip_platforms: List[str],
) -> Dict[str, Any]:
    unified_path = base_dir / "outputs" / "wuwa_unified_scored.json"
    unified_obj = _load_json(unified_path)
    unified_items = unified_obj.get("items", [])

    grouped: Dict[str, List[Dict[str, Any]]] = {"kejinshou": [], "pzds": [], "7881": []}
    skipped_sold = 0
    for item in unified_items:
        platform = str(item.get("platform") or "")
        if platform in skip_platforms:
            continue
        already_sold = bool(item.get("is_sold")) or str(item.get("market_status") or "") == "sold"
        if already_sold:
            skipped_sold += 1
            continue
        if platform in grouped and item.get("detail_url"):
            grouped[platform].append(item)

    kejin_status = _refresh_items(
        platform="kejinshou",
        items=grouped["kejinshou"],
        detail_url_builder=lambda item: item["detail_url"],
    )
    pzds_status = _refresh_items(
        platform="pzds",
        items=grouped["pzds"],
        detail_url_builder=lambda item: item["detail_url"],
    )
    t7881_status = _refresh_items(
        platform="7881",
        items=grouped["7881"],
        detail_url_builder=lambda item: item["detail_url"],
    )

    kejin_items = _apply_status(
        _apply_price_updates("kejinshou", grouped["kejinshou"], latest_price_map["kejinshou"]),
        kejin_status,
    )
    pzds_items = _apply_status(
        _apply_price_updates("pzds", grouped["pzds"], latest_price_map["pzds"]),
        pzds_status,
    )
    t7881_items = _apply_status(
        _apply_price_updates("7881", grouped["7881"], latest_price_map["7881"]),
        t7881_status,
    )

    refreshed_map = {
        ("kejinshou", str(item.get("product_id") or "")): item for item in kejin_items
    }
    refreshed_map.update({
        ("pzds", str(item.get("product_id") or "")): item for item in pzds_items
    })
    refreshed_map.update({
        ("7881", str(item.get("product_id") or "")): item for item in t7881_items
    })

    next_items: List[Dict[str, Any]] = []
    for item in unified_items:
        key = (str(item.get("platform") or ""), str(item.get("product_id") or ""))
        next_items.append(refreshed_map.get(key, item))

    unified_obj["items"] = next_items
    unified_obj.setdefault("meta", {})
    unified_obj["meta"]["statusCheckedAt"] = checked_at
    unified_obj["meta"]["statusSource"] = "live_detail_check"
    unified_obj["meta"]["statusRefreshScope"] = {
        "mode": "unified_non_sold_only",
        "skippedPlatforms": skip_platforms,
        "checked": {
            "kejinshou": len(grouped["kejinshou"]),
            "pzds": len(grouped["pzds"]),
            "7881": len(grouped["7881"]),
            "total": len(grouped["kejinshou"]) + len(grouped["pzds"]) + len(grouped["7881"]),
        },
        "skippedSold": skipped_sold,
    }
    _write_json(unified_path, unified_obj)
    return unified_obj


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    outputs_dir = base_dir / "outputs"
    summary_path = outputs_dir / "market_status_refresh_summary.json"
    latest_price_map = _build_price_map(base_dir)
    checked_at = _now_iso()
    skip_platforms = _resolve_skip_platforms()
    unified_obj = _refresh_unified(
        base_dir=base_dir,
        latest_price_map=latest_price_map,
        checked_at=checked_at,
        skip_platforms=skip_platforms,
    )

    summary = {
        "updatedAt": checked_at,
        "mode": "status_refresh_existing_records_only",
        "skippedPlatforms": skip_platforms,
        "priceUpdatedFromLatestSnapshot": {
            "kejinshou": len(latest_price_map["kejinshou"]),
            "pzds": len(latest_price_map["pzds"]),
            "7881": len(latest_price_map["7881"]),
        },
        "platforms": _status_summary_by_platform(unified_obj.get("items", [])),
        "unified": {
            "total": len(unified_obj.get("items", [])),
            "status": _status_summary(unified_obj.get("items", [])),
            "refreshScope": unified_obj.get("meta", {}).get("statusRefreshScope", {}),
        },
    }
    _write_json(summary_path, summary)
    _rebuild_unified_outputs_from_current_json(base_dir=base_dir, unified_obj=unified_obj)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
