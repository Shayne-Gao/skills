import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from normalize_and_score_wuwa_role_tiers import (
    _build_role_profile,
    _diminishing_multiplier,
    _load_role_adjustments,
    _load_tier_map,
    _load_weapon_map,
    _weapon_base_score,
)
from post_refresh_hooks import outputs_exist, run_scripts


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_csv(path: Path, header: List[str], rows: List[List[Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def _normalize_role_name(name: str) -> str:
    alias_map = {
        "卡提那娅": "卡提希娅",
        "坎特雷拉": "坎特蕾拉",
        "陆赫斯": "陆·赫斯",
    }
    return alias_map.get(str(name).strip(), str(name).strip())


def _latest_extract_file(output_dir: Path) -> Path:
    matches = sorted(output_dir.glob("7881_wuwa_detail_extract_*.json"))
    if not matches:
        raise FileNotFoundError("未找到 7881 结构化详情文件，请先运行 fetch_7881_wuwa_details.py")
    return matches[-1]


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    output_dir = base_dir / "outputs"
    input_path = _latest_extract_file(output_dir)
    tier_file = base_dir / "configs" / "wuwa_role_tiers_corrected.json"
    weapon_catalog = base_dir / "configs" / "wuwa_weapon_catalog.json"
    role_adjustments_path = base_dir / "configs" / "wuwa_role_adjustments_33.json"

    src = _load_json(input_path)
    tier_map = _load_tier_map(tier_file)
    weapon_map = _load_weapon_map(weapon_catalog)
    role_adjustments = _load_role_adjustments(role_adjustments_path)

    tier_score_map = {"T0": 120.0, "T0.5": 90.0, "T1": 40.0, "T2": 10.0, "T3": 0.0, "T4": 0.0, "T5": 0.0}
    mode_grade_score_map = {"EX": 120.0, "SS": 90.0, "S": 40.0, "A": 10.0, "B": 0.0, "C": 0.0}
    weapon_signature_score_map = {"T0": 60.0, "T0.5": 50.0, "T1": 30.0, "T2": 10.0}
    weapon_standard_score = 20.0
    overall_weight = 0.4
    tower_weight = 0.3
    requiem_weight = 0.3
    four_star_factor = 0.5
    weapon_pull_factor = 0.8

    scored_items: List[Dict[str, Any]] = []
    csv_rows: List[List[Any]] = []

    for item in src.get("items", []):
        roles = []
        total_role_score = 0.0
        matched_roles = 0
        unmatched_roles: List[str] = []
        for role in item.get("roles", []):
            name = _normalize_role_name(role.get("name", ""))
            tier_item = tier_map.get(name)
            adjust = role_adjustments.get(name, {})
            manual_adjust = float(adjust.get("manual_adjust", 0))
            dependency_penalty = float(adjust.get("dependency_penalty", 0))
            profile = (
                _build_role_profile(
                    tier_item=tier_item,
                    star="五星",
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
            multiplier = _diminishing_multiplier(int(role.get("resonance", 0)))
            score = round(base_score * multiplier if tier else 0.0, 2)
            if tier:
                matched_roles += 1
            else:
                unmatched_roles.append(name)
            total_role_score += score
            roles.append(
                {
                    "name": name,
                    "star": "五星",
                    "resonance": int(role.get("resonance", 0)),
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
                    "multiplier": round(multiplier if tier else 1.0, 2),
                    "score": score,
                }
            )

        weapons = []
        weapon_score_total = 0.0
        for weapon in item.get("weapons", []):
            weapon_name = str(weapon.get("name", "")).strip()
            weapon_info = weapon_map.get(weapon_name, {})
            owner_character = _normalize_role_name(weapon_info.get("owner_character", ""))
            owner_profile = None
            if owner_character and owner_character in tier_map:
                owner_adjust = role_adjustments.get(owner_character, {})
                owner_profile = _build_role_profile(
                    tier_item=tier_map[owner_character],
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
            displayed_refine = int(weapon.get("refine", 0))
            effective_refine = max(displayed_refine - 1, 0)
            base_score = _weapon_base_score(
                weapon_info=weapon_info,
                owner_tier=owner_tier,
                signature_score_map=weapon_signature_score_map,
                standard_score=weapon_standard_score,
            )
            multiplier = _diminishing_multiplier(effective_refine)
            score = round(base_score * multiplier, 2)
            weapon_score_total += score
            weapons.append(
                {
                    "name": weapon_name,
                    "english_name": weapon_info.get("english_name", ""),
                    "star": "五星",
                    "refine": displayed_refine,
                    "resonance": displayed_refine,
                    "effective_refine": effective_refine,
                    "weapon_class": weapon_info.get("weapon_class", "unknown"),
                    "owner_character": owner_character,
                    "owner_tier": owner_tier,
                    "confidence": weapon_info.get("confidence", "unknown"),
                    "source": weapon_info.get("source", ""),
                    "base_score": round(base_score, 2),
                    "multiplier": round(multiplier, 2),
                    "score": score,
                }
            )

        star_voice = int(item.get("star_voice", 0) or 0)
        fj = int(item.get("float_gold_wave", 0) or 0)
        zc = int(item.get("weapon_wave", 0) or 0)
        hs = int(item.get("standard_wave", 0) or 0)
        pulls_total = round(star_voice / 160.0 + fj + zc * weapon_pull_factor, 2)
        strength_score = round(pulls_total + total_role_score + weapon_score_total, 2)
        price = float(item.get("price", 0) or 0)
        value_score = round(strength_score / max(price, 1.0), 3)
        can_rank = True
        data_quality = "ok"
        quality_label = "正常"
        parse_failed_reason = ""
        detail_fetch_status = "fetched"
        detail_fetch_label = "已抓到详情"
        if strength_score == 0 and not roles and not weapons:
            can_rank = False
            data_quality = "parse_failed_partial"
            quality_label = "没抓到详情"
            parse_failed_reason = "detail_incomplete_or_parse_failed"
            detail_fetch_status = "missing"
            detail_fetch_label = "没抓到详情"

        scored = {
            "platform": "7881",
            "product_id": str(item.get("goods_id", "")),
            "detail_url": item.get("detail_url", ""),
            "price": price,
            "level": int(item.get("level", 0) or 0),
            "total_yellow": int(item.get("yellow_count", 0) or 0),
            "summary": item.get("title", ""),
            "security_summary": item.get("seller_desc", ""),
            "resources": {
                "star_voice": star_voice,
                "fj_waves": fj,
                "zc_waves": zc,
                "hs_waves": hs,
                "character_pulls": fj,
                "weapon_pulls": round(zc * weapon_pull_factor, 2),
                "standard_pulls_ignored": hs,
                "pulls_total": pulls_total,
            },
            "roles": roles,
            "weapons": weapons,
            "role_score_total": round(total_role_score, 2),
            "weapon_score_total": round(weapon_score_total, 2),
            "strength_score": strength_score,
            "value_score": value_score,
            "can_rank": can_rank,
            "data_quality": data_quality,
            "quality_label": quality_label,
            "parse_failed_reason": parse_failed_reason,
            "detail_fetch_status": detail_fetch_status,
            "detail_fetch_label": detail_fetch_label,
            "matched_tier_roles": matched_roles,
            "unmatched_roles": unmatched_roles,
            "source_meta": {
                "page_num": item.get("page_num"),
                "rank_in_page": item.get("rank_in_page"),
                "support_report": bool(item.get("support_report")),
                "status_closed": item.get("status_closed", ""),
                "update_time": item.get("update_time", ""),
            },
        }
        scored_items.append(scored)
        csv_rows.append(
            [
                scored["platform"],
                scored["product_id"],
                scored["price"],
                scored["level"],
                scored["total_yellow"],
                pulls_total,
                scored["role_score_total"],
                scored["weapon_score_total"],
                scored["strength_score"],
                scored["value_score"],
                scored["detail_url"],
            ]
        )

    out_json = output_dir / "7881_wuwa_top100_scored.json"
    out_csv = output_dir / "7881_wuwa_top100_scored.csv"
    out_json.write_text(
        json.dumps(
            {
                "meta": {
                    "generatedAt": datetime.now().strftime("%Y%m%d_%H%M%S"),
                    "platform": "7881",
                    "sourceFile": str(input_path),
                    "count": len(scored_items),
                },
                "items": scored_items,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _write_csv(
        out_csv,
        [
            "platform",
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
        ],
        csv_rows,
    )
    print(out_json)
    print(out_csv)

    if outputs_exist(
        base_dir=base_dir,
        relative_paths=[
            "outputs/wuwa_top200_normalized_assets.json",
            "outputs/pzds_wuwa_top100_scored.json",
        ],
    ):
        run_scripts(
            base_dir=base_dir,
            script_names=["generate_unified_wuwa_review.py"],
            reason="7881 scored fetch",
        )


if __name__ == "__main__":
    main()
