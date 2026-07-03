import csv
import html
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from urllib.request import Request, urlopen

from post_refresh_hooks import outputs_exist, run_scripts


BASE_DETAIL_URL = "https://www.pzds.com/goodsDetails/{product_id}/6?from=%E5%95%86%E5%93%81%E5%88%97%E8%A1%A8"


def _now_tag() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_lines(path: Path) -> List[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _clean_text(raw_html: str) -> str:
    s = re.sub(r"<script[\s\S]*?</script>", " ", raw_html, flags=re.I)
    s = re.sub(r"<style[\s\S]*?</style>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s)
    return s


def _pick(text: str, pattern: str, idx: int = 1, default: str = "") -> str:
    m = re.search(pattern, text)
    return m.group(idx) if m else default


def _to_int(value: Any) -> int:
    m = re.search(r"(\d+)", str(value))
    return int(m.group(1)) if m else 0


def _score_multiplier(level: int) -> float:
    mapping = {
        0: 1.0,
        1: 1.4,
        2: 1.7,
        3: 1.95,
        4: 2.15,
        5: 2.3,
        6: 2.4,
    }
    return mapping.get(max(0, min(level, 6)), 1.0)


def _mode_grade_score(grade: str, grade_score_map: Dict[str, float]) -> float:
    return grade_score_map.get(str(grade or "").strip(), 0.0)


def _display_tier_from_score(score: float, tier_score_map: Dict[str, float]) -> str:
    thresholds = [
        ("T0", (tier_score_map["T0"] + tier_score_map["T0.5"]) / 2.0),
        ("T0.5", (tier_score_map["T0.5"] + tier_score_map["T1"]) / 2.0),
        ("T1", (tier_score_map["T1"] + tier_score_map["T2"]) / 2.0),
        ("T2", max(tier_score_map["T2"] / 2.0, 1.0)),
    ]
    for tier, threshold in thresholds:
        if score >= threshold:
            return tier
    return "T3" if score > 0 else "T4"


def _build_role_profile(
    tier_item: Dict[str, Any],
    star: str,
    tier_score_map: Dict[str, float],
    mode_grade_score_map: Dict[str, float],
    overall_weight: float,
    tower_weight: float,
    requiem_weight: float,
    four_star_factor: float,
    manual_adjust: float,
    dependency_penalty: float,
) -> Dict[str, Any]:
    overall_tier = str(tier_item.get("梯度") or "").strip()
    tower_grade = str(tier_item.get("深塔评分") or "").strip()
    requiem_grade = str(tier_item.get("冥歌评分") or "").strip()
    overall_score = tier_score_map.get(overall_tier, 0.0)
    tower_score = _mode_grade_score(tower_grade, mode_grade_score_map)
    requiem_score = _mode_grade_score(requiem_grade, mode_grade_score_map)
    weighted_base_score = (
        overall_score * overall_weight
        + tower_score * tower_weight
        + requiem_score * requiem_weight
    )
    if star == "四星":
        weighted_base_score *= four_star_factor
    adjusted_base_score = max(weighted_base_score + manual_adjust + dependency_penalty, 0.0)
    display_tier = _display_tier_from_score(adjusted_base_score, tier_score_map)
    return {
        "overall_tier": overall_tier,
        "tower_grade": tower_grade,
        "requiem_grade": requiem_grade,
        "overall_score": round(overall_score, 2),
        "tower_score": round(tower_score, 2),
        "requiem_score": round(requiem_score, 2),
        "weighted_base_score": round(weighted_base_score, 2),
        "adjusted_base_score": round(adjusted_base_score, 2),
        "display_tier": display_tier,
    }


def _normalize_role_name(name: str) -> str:
    return name.replace("陆赫斯", "陆·赫斯").strip()


def _write_csv(path: Path, header: List[str], rows: List[List[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def _parse_role_chunks(line: str, star: str) -> List[Dict[str, Any]]:
    parts = [x.strip() for x in re.split(r"[，,]", line) if x.strip()]
    out = []
    for part in parts:
        m = re.match(r"(\d+)命(.+)", part)
        if not m:
            continue
        out.append(
            {
                "name": _normalize_role_name(m.group(2).strip()),
                "resonance": int(m.group(1)),
                "star": star,
            }
        )
    return out


def _parse_weapon_chunks(line: str) -> List[Dict[str, Any]]:
    parts = [x.strip() for x in re.split(r"[，,]", line) if x.strip()]
    out = []
    for part in parts:
        m = re.match(r"精(\d+)(.+)", part)
        if not m:
            continue
        out.append(
            {
                "name": m.group(2).strip(),
                "refine": int(m.group(1)),
                "star": "五星",
            }
        )
    return out


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    ids_path = base_dir / "configs" / "pzds_wuwa_top100_ids.txt"
    role_tier_path = base_dir / "configs" / "wuwa_role_tiers_corrected.json"
    role_adjust_path = base_dir / "configs" / "wuwa_role_adjustments_33.json"
    weapon_catalog_path = base_dir / "configs" / "wuwa_weapon_catalog.json"

    raw_dir = base_dir / "data" / "pzds" / "detail_html"
    raw_dir.mkdir(parents=True, exist_ok=True)
    output_dir = base_dir / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    role_tiers = {item["角色"]: item for item in _read_json(role_tier_path)["items"]}
    role_adjust = {item["角色"]: item for item in _read_json(role_adjust_path)["items"]}
    weapon_catalog = {item["weapon_name"]: item for item in _read_json(weapon_catalog_path)["items"]}
    product_ids = _read_lines(ids_path)

    tier_score_map = {"T0": 120.0, "T0.5": 90.0, "T1": 40.0, "T2": 10.0, "T3": 0.0, "T4": 0.0, "T5": 0.0}
    mode_grade_score_map = {"EX": 120.0, "SS": 90.0, "S": 40.0, "A": 10.0, "B": 0.0, "C": 0.0}
    weapon_score_map = {"T0": 60.0, "T0.5": 50.0, "T1": 30.0, "T2": 10.0}
    four_star_factor = 0.5
    standard_weapon_score = 20.0
    overall_weight = 0.4
    tower_weight = 0.3
    requiem_weight = 0.3
    weapon_pull_factor = 0.8

    items: List[Dict[str, Any]] = []

    for product_id in product_ids:
        url = BASE_DETAIL_URL.format(product_id=product_id)
        raw_html = urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read().decode("utf-8", "ignore")
        (raw_dir / f"{product_id}.html").write_text(raw_html, encoding="utf-8")
        text = _clean_text(raw_html)
        waf_blocked = "aliyun_waf" in raw_html.lower() or "_waf_" in raw_html.lower()

        desc = _pick(text, r"商品描述\s*(.*?)\s*交易流程") or text
        price = _to_int(_pick(text, r"¥\s*(\d+)"))
        level = _to_int(_pick(desc, r"【联觉等级】[:：]\s*(\d+)级") or _pick(text, r"联觉等级\s*(\d+)"))
        total_yellow = _to_int(_pick(desc, r"【黄数】[:：]\s*(\d+)") or _pick(text, r"黄数量\s*(\d+)"))
        star_voice = _to_int(_pick(desc, r"【星声】[:：]\s*(\d+)") or _pick(text, r"星声\s*(\d+)"))
        fj = _to_int(_pick(desc, r"【浮金波纹】[:：]\s*(\d+)") or _pick(text, r"浮金波纹\s*(\d+)"))
        hs = _to_int(_pick(desc, r"【唤声涡纹】[:：]\s*(\d+)") or _pick(text, r"唤声涡纹\s*(\d+)"))
        zc = _to_int(_pick(desc, r"【铸潮波纹】[:：]\s*(\d+)") or _pick(text, r"铸潮波纹\s*(\d+)"))
        title = _pick(text, rf"{product_id}\s*号\s*(.*?)\s*官服手机")
        security_summary = " ".join(
            x
            for x in [
                _pick(text, r"(未绑定Wegame|能解绑Wegame|不能解绑Wegame)"),
                _pick(text, r"(未绑定TAP|送TAP|不送TAP)"),
                _pick(text, r"(无换绑冷却|有换绑冷却)"),
            ]
            if x
        )

        roles = []
        roles.extend(_parse_role_chunks(_pick(desc, r"【五星角色】[:：]\s*([^【]+)"), "五星"))
        roles.extend(_parse_role_chunks(_pick(desc, r"【四星角色】[:：]\s*([^【]+)"), "四星"))
        weapons = _parse_weapon_chunks(_pick(desc, r"【金色武器】[:：]\s*([^【]+)"))

        normalized_roles = []
        for role in roles:
            tier_item = role_tiers.get(role["name"])
            adjust = role_adjust.get(role["name"], {})
            manual_adjust = float(adjust.get("manual_adjust", 0))
            dependency_penalty = float(adjust.get("dependency_penalty", 0))
            profile = (
                _build_role_profile(
                    tier_item=tier_item,
                    star=role["star"],
                    tier_score_map=tier_score_map,
                    mode_grade_score_map=mode_grade_score_map,
                    overall_weight=overall_weight,
                    tower_weight=tower_weight,
                    requiem_weight=requiem_weight,
                    four_star_factor=four_star_factor,
                    manual_adjust=manual_adjust,
                    dependency_penalty=dependency_penalty,
                )
                if tier_item
                else None
            )
            tier = profile["display_tier"] if profile else ""
            base_score = profile["adjusted_base_score"] if profile else 0.0
            score = base_score * _score_multiplier(role["resonance"]) if tier else 0.0
            normalized_roles.append(
                {
                    "name": role["name"],
                    "star": role["star"],
                    "resonance": role["resonance"],
                    "tier": tier,
                    "overall_tier": profile["overall_tier"] if profile else "",
                    "tower_grade": profile["tower_grade"] if profile else "",
                    "requiem_grade": profile["requiem_grade"] if profile else "",
                    "overall_score": profile["overall_score"] if profile else 0.0,
                    "tower_score": profile["tower_score"] if profile else 0.0,
                    "requiem_score": profile["requiem_score"] if profile else 0.0,
                    "raw_base_score": profile["weighted_base_score"] if profile else 0.0,
                    "base_score": round(base_score, 2),
                    "manual_adjust": round(manual_adjust, 2),
                    "dependency_penalty": round(dependency_penalty, 2),
                    "score": round(score, 2),
                }
            )

        normalized_weapons = []
        for weapon in weapons:
            weapon_info = weapon_catalog.get(weapon["name"], {})
            owner = weapon_info.get("owner_character", "")
            owner_profile = None
            if owner and owner in role_tiers:
                owner_adjust = role_adjust.get(owner, {})
                owner_profile = _build_role_profile(
                    tier_item=role_tiers[owner],
                    star="五星",
                    tier_score_map=tier_score_map,
                    mode_grade_score_map=mode_grade_score_map,
                    overall_weight=overall_weight,
                    tower_weight=tower_weight,
                    requiem_weight=requiem_weight,
                    four_star_factor=four_star_factor,
                    manual_adjust=float(owner_adjust.get("manual_adjust", 0)),
                    dependency_penalty=float(owner_adjust.get("dependency_penalty", 0)),
                )
            owner_tier = owner_profile["display_tier"] if owner_profile else ""
            if weapon_info.get("weapon_class") == "signature":
                base_score = weapon_score_map.get(owner_tier, 0.0)
            else:
                base_score = standard_weapon_score
            effective_refine = max(weapon["refine"] - 1, 0)
            score = base_score * _score_multiplier(effective_refine)
            normalized_weapons.append(
                {
                    "name": weapon["name"],
                    "refine": weapon["refine"],
                    "effective_refine": effective_refine,
                    "weapon_class": weapon_info.get("weapon_class", "unknown"),
                    "owner_character": owner,
                    "owner_tier": owner_tier,
                    "score": round(score, 2),
                }
            )

        pulls_total = star_voice / 160.0 + fj + zc * weapon_pull_factor
        role_score_total = round(sum(item["score"] for item in normalized_roles), 2)
        weapon_score_total = round(sum(item["score"] for item in normalized_weapons), 2)
        strength_score = round(pulls_total + role_score_total + weapon_score_total, 2)
        value_score = round(strength_score / max(price, 1), 3)
        can_rank = True
        data_quality = "ok"
        quality_label = "正常"
        parse_failed_reason = ""
        detail_fetch_status = "fetched"
        detail_fetch_label = "已抓到详情"
        if waf_blocked or (price == 0 and level == 0 and total_yellow == 0 and not normalized_roles and not normalized_weapons and not (title or "")):
            can_rank = False
            data_quality = "parse_failed_empty"
            quality_label = "没抓到详情"
            parse_failed_reason = "pzds_detail_waf_or_parse_failed"
            detail_fetch_status = "missing"
            detail_fetch_label = "没抓到详情"

        items.append(
            {
                "platform": "pzds",
                "product_id": product_id,
                "detail_url": url,
                "price": price,
                "level": level,
                "total_yellow": total_yellow,
                "summary": title or "",
                "security_summary": security_summary,
                "resources": {
                    "star_voice": star_voice,
                    "fj_waves": fj,
                    "hs_waves": hs,
                    "zc_waves": zc,
                    "character_pulls": fj,
                    "weapon_pulls": round(zc * weapon_pull_factor, 2),
                    "standard_pulls_ignored": hs,
                    "pulls_total": round(pulls_total, 2),
                },
                "roles": normalized_roles,
                "weapons": normalized_weapons,
                "role_score_total": role_score_total,
                "weapon_score_total": weapon_score_total,
                "strength_score": strength_score,
                "value_score": value_score,
                "can_rank": can_rank,
                "data_quality": data_quality,
                "quality_label": quality_label,
                "parse_failed_reason": parse_failed_reason,
                "detail_fetch_status": detail_fetch_status,
                "detail_fetch_label": detail_fetch_label,
            }
        )

    value_ranked = sorted(items, key=lambda x: (x["value_score"], x["strength_score"]), reverse=True)
    strength_ranked = sorted(items, key=lambda x: (x["strength_score"], x["value_score"]), reverse=True)
    strength_rank_map = {item["product_id"]: idx for idx, item in enumerate(strength_ranked, start=1)}
    for idx, item in enumerate(value_ranked, start=1):
        item["value_rank"] = idx
        item["strength_rank"] = strength_rank_map[item["product_id"]]

    json_path = output_dir / "pzds_wuwa_top100_scored.json"
    csv_path = output_dir / "pzds_wuwa_top100_scored.csv"
    json_path.write_text(
        json.dumps(
            {
                "meta": {
                    "generatedAt": _now_tag(),
                    "count": len(value_ranked),
                    "platform": "pzds",
                    "idsFile": str(ids_path),
                    "rawDir": str(raw_dir),
                    "pullScoring": {
                        "starVoiceFactor": 160,
                        "characterWaveFactor": 1.0,
                        "weaponWaveFactor": weapon_pull_factor,
                        "ignoreStandardWave": True,
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
        "value_rank",
        "strength_rank",
        "product_id",
        "price",
        "level",
        "total_yellow",
        "pulls_total",
        "role_score_total",
        "weapon_score_total",
        "strength_score",
        "value_score",
        "detail_url",
    ]
    rows = []
    for item in value_ranked:
        rows.append(
            [
                item["value_rank"],
                item["strength_rank"],
                item["product_id"],
                item["price"],
                item["level"],
                item["total_yellow"],
                item["resources"]["pulls_total"],
                item["role_score_total"],
                item["weapon_score_total"],
                item["strength_score"],
                item["value_score"],
                item["detail_url"],
            ]
        )
    _write_csv(csv_path, header, rows)

    print(f"count: {len(value_ranked)}")
    print(f"json: {json_path}")
    print(f"csv: {csv_path}")
    for item in value_ranked[:10]:
        print(
            f"{item['value_rank']:>2}  {item['product_id']}  price={item['price']}  "
            f"strength={item['strength_score']}  value={item['value_score']}"
        )

    if outputs_exist(
        base_dir=base_dir,
        relative_paths=[
            "outputs/wuwa_top200_normalized_assets.json",
            "outputs/7881_wuwa_top100_scored.json",
        ],
    ):
        run_scripts(
            base_dir=base_dir,
            script_names=["generate_unified_wuwa_review.py"],
            reason="pzds scored fetch",
        )


if __name__ == "__main__":
    main()
