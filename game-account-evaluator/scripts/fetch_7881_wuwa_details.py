import csv
import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen


DETAIL_API_URL = "https://gw.7881.com/goods-service-api/api/goods/detail?channel=17&goodsId={goods_id}"
USER_AGENT = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Safari/604.1"
)


def _now_tag() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_goods_items(path: Path) -> List[Dict[str, Any]]:
    obj = _read_json(path)
    return list(obj.get("items", []))


def _request_json(goods_id: str, timeout: int = 30) -> Dict[str, Any]:
    url = DETAIL_API_URL.format(goods_id=goods_id)
    req = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Referer": "https://h5.7881.com/",
            "Accept": "application/json, text/plain, */*",
        },
    )
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", "ignore"))


def _find_group_value(group_list: List[Dict[str, Any]], name: str) -> str:
    for item in group_list:
        if str(item.get("ename") or "").strip() == name:
            return str(item.get("ev") or "").strip()
    return ""


def _to_int(value: Any) -> int:
    m = re.search(r"\d+", str(value or ""))
    return int(m.group(0)) if m else 0


def _parse_roles(raw: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    roles: List[Dict[str, Any]] = []
    for item in raw or []:
        name = str(item.get("name") or "").strip()
        if not name:
            continue
        sub_val_text = str(item.get("subVal") or "").strip()
        resonance = 6 if sub_val_text == "满" else int(re.search(r"\d+", sub_val_text).group(0)) if re.search(r"\d+", sub_val_text) else 0
        roles.append(
            {
                "name": name,
                "resonance": resonance,
                "raw_sub_val": sub_val_text,
            }
        )
    return roles


def _parse_weapons(raw: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    weapons: List[Dict[str, Any]] = []
    for item in raw or []:
        name = str(item.get("name") or "").strip()
        if not name:
            continue
        sub_val_text = str(item.get("subVal") or "").strip()
        refine = int(re.search(r"\d+", sub_val_text).group(0)) if re.search(r"\d+", sub_val_text) else 0
        weapons.append(
            {
                "name": name,
                "refine": refine,
                "raw_sub_val": sub_val_text,
            }
        )
    return weapons


def _parse_roles_from_text(text: str) -> List[Dict[str, Any]]:
    roles: List[Dict[str, Any]] = []
    for part in [x.strip() for x in re.split(r"[，,]", text or "") if x.strip()]:
        m = re.match(r"(.+?)\((满|\d+)命.+\)$", part)
        if not m:
            continue
        raw_res = m.group(2)
        resonance = 6 if raw_res == "满" else _to_int(raw_res)
        roles.append(
            {
                "name": m.group(1).strip(),
                "resonance": resonance,
                "raw_sub_val": raw_res,
            }
        )
    return roles


def _parse_weapons_from_text(text: str) -> List[Dict[str, Any]]:
    weapons: List[Dict[str, Any]] = []
    for part in [x.strip() for x in re.split(r"[，,]", text or "") if x.strip()]:
        m = re.match(r"(.+?)\(精(\d+).+\)$", part)
        if not m:
            continue
        weapons.append(
            {
                "name": m.group(1).strip(),
                "refine": _to_int(m.group(2)),
                "raw_sub_val": m.group(2),
            }
        )
    return weapons


def _extract_summary(body: Dict[str, Any], item_meta: Dict[str, Any]) -> Dict[str, Any]:
    group_list = list(body.get("gameAccountGroupInfoList") or [])
    camp_info = body.get("accountCampInfoDTO") or {}
    report = camp_info.get("mingchaoReport") or {}
    roles = _parse_roles(report.get("fiveRoleList") or []) or _parse_roles_from_text(_find_group_value(group_list, "五星角色"))
    weapons = _parse_weapons(report.get("fiveWqList") or []) or _parse_weapons_from_text(_find_group_value(group_list, "五星武器"))

    return {
        "goods_id": str(body.get("goodsId") or item_meta.get("goods_id") or ""),
        "detail_url": item_meta.get("detail_url") or f"https://search.7881.com/{body.get('goodsId')}.html",
        "page_num": item_meta.get("page_num"),
        "rank_in_page": item_meta.get("rank_in_page"),
        "title": str(body.get("title") or "").strip(),
        "price": float(body.get("price") or 0),
        "seller_desc": str(body.get("sellerDesc") or "").strip(),
        "status_closed": str(body.get("closed") or ""),
        "support_report": bool(body.get("supportReport")),
        "level": str(report.get("level") or _find_group_value(group_list, "等级") or "").strip(),
        "yellow_count": _to_int(report.get("huangNum") or _find_group_value(group_list, "黄数")),
        "star_voice": _to_int(_find_group_value(group_list, "星声数量")),
        "float_gold_wave": _to_int(report.get("fjbwNum") or _find_group_value(group_list, "浮金波纹数量")),
        "weapon_wave": _to_int(report.get("zcbwNum") or _find_group_value(group_list, "铸潮波纹数量")),
        "standard_wave": _to_int(report.get("hswwNum") or _find_group_value(group_list, "唤声涡纹数量")),
        "five_role_num": int(report.get("fiveRoleNum") or len(roles)),
        "five_weapon_num": int(report.get("fiveWqNum") or len(weapons)),
        "four_role_num": int(report.get("fourRoleNum") or 0),
        "update_time": str(report.get("updateTime") or "").strip(),
        "roles": roles,
        "weapons": weapons,
    }


def _write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = [
        "goods_id",
        "page_num",
        "rank_in_page",
        "price",
        "yellow_count",
        "level",
        "star_voice",
        "float_gold_wave",
        "weapon_wave",
        "standard_wave",
        "five_role_num",
        "five_weapon_num",
        "update_time",
        "status_closed",
        "detail_url",
        "title",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in header})


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    raw_list_path = base_dir / "data" / "raw" / "7881_wuwa_top100_list_20260606.json"
    detail_json_dir = base_dir / "data" / "7881" / "detail_json"
    output_dir = base_dir / "outputs"

    detail_json_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    items = _load_goods_items(raw_list_path)
    summaries: List[Dict[str, Any]] = []
    failures: List[Dict[str, str]] = []

    for idx, item in enumerate(items, start=1):
        goods_id = str(item.get("goods_id") or "").strip()
        if not goods_id:
            continue
        try:
            payload = _request_json(goods_id=goods_id)
            (detail_json_dir / f"{goods_id}.json").write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            body = payload.get("body") or {}
            summaries.append(_extract_summary(body=body, item_meta=item))
            print(f"[{idx:03d}/{len(items):03d}] ok {goods_id}")
            time.sleep(0.2)
        except Exception as exc:  # pragma: no cover
            failures.append({"goods_id": goods_id, "error": str(exc)})
            print(f"[{idx:03d}/{len(items):03d}] fail {goods_id}: {exc}")
            time.sleep(0.5)

    tag = _now_tag()
    summary_json_path = output_dir / f"7881_wuwa_detail_extract_{tag}.json"
    summary_csv_path = output_dir / f"7881_wuwa_detail_extract_{tag}.csv"
    fetch_report_path = output_dir / f"7881_wuwa_fetch_report_{tag}.json"

    summary_json_path.write_text(
        json.dumps(
            {
                "meta": {
                    "source": "7881 goods detail api",
                    "count": len(summaries),
                    "failure_count": len(failures),
                    "generated_at": datetime.now().isoformat(timespec="seconds"),
                },
                "items": summaries,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    _write_csv(summary_csv_path, summaries)
    fetch_report_path.write_text(
        json.dumps(
            {
                "meta": {
                    "requested": len(items),
                    "success": len(summaries),
                    "failed": len(failures),
                    "generated_at": datetime.now().isoformat(timespec="seconds"),
                },
                "failures": failures,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"saved detail json dir: {detail_json_dir}")
    print(f"saved summary json: {summary_json_path}")
    print(f"saved summary csv: {summary_csv_path}")
    print(f"saved fetch report: {fetch_report_path}")


if __name__ == "__main__":
    main()
