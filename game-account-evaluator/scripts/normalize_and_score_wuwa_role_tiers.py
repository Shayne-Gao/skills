import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from post_refresh_hooks import outputs_exist, run_scripts


def _now_tag() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _to_int(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(round(value))
    text = str(value).strip()
    digits = []
    for ch in text:
        if ch.isdigit():
            digits.append(ch)
    return int("".join(digits)) if digits else 0


def _csv_escape(s: str) -> str:
    t = str(s or "")
    if any(x in t for x in [",", "\"", "\n", "\r"]):
        return "\"" + t.replace("\"", "\"\"") + "\""
    return t


def _write_csv(path: Path, header: List[str], rows: List[List[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [",".join(_csv_escape(x) for x in header)]
    for row in rows:
        lines.append(",".join(_csv_escape(x) for x in row))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _format_table(rows: List[List[str]]) -> str:
    if not rows:
        return ""
    widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    out = []
    for row in rows:
        out.append("  ".join(row[i].ljust(widths[i]) for i in range(len(row))).rstrip())
    return "\n".join(out)


def _build_relation_maps(fp: Dict[str, Any]) -> Tuple[Dict[int, str], Dict[Tuple[int, int], str]]:
    sp_map: Dict[int, str] = {}
    pv_map: Dict[Tuple[int, int], str] = {}
    for sp in fp.get("sps", []):
        sp_id = _to_int(sp.get("id"))
        sp_title = str(sp.get("title") or "").strip()
        if sp_id:
            sp_map[sp_id] = sp_title
        for pv in sp.get("pvs", []):
            pv_id = _to_int(pv.get("id"))
            pv_title = str(pv.get("title") or "").strip()
            if sp_id and pv_id:
                pv_map[(sp_id, pv_id)] = pv_title
    return sp_map, pv_map


def _extract_assets(fp: Dict[str, Any], asset_kind: str) -> List[Dict[str, Any]]:
    sp_map, pv_map = _build_relation_maps(fp)
    assets: List[Dict[str, Any]] = []
    for item in fp.get("ups", []):
        name = str(item.get("title") or "").strip()
        if not name:
            continue
        star = ""
        resonance = 0
        for rel in item.get("relations", []):
            sp_id = _to_int(rel.get("spId"))
            pv_id = _to_int(rel.get("pvId"))
            sp_title = sp_map.get(sp_id, "")
            pv_title = pv_map.get((sp_id, pv_id), "")
            if sp_title == "星级":
                star = pv_title
            elif asset_kind == "role" and sp_title == "角色共鸣":
                resonance = _to_int(pv_title)
            elif asset_kind == "weapon" and sp_title == "武器共鸣":
                resonance = _to_int(pv_title)
        assets.append(
            {
                "name": name,
                "star": star,
                "resonance": resonance,
            }
        )
    return assets


def _load_tier_map(tier_path: Path) -> Dict[str, Dict[str, Any]]:
    obj = json.loads(tier_path.read_text(encoding="utf-8"))
    return {item["角色"]: item for item in obj["items"]}


def _load_weapon_map(catalog_path: Path) -> Dict[str, Dict[str, Any]]:
    obj = json.loads(catalog_path.read_text(encoding="utf-8"))
    return {item["weapon_name"]: item for item in obj["items"]}


def _load_role_adjustments(path: Path) -> Dict[str, Dict[str, Any]]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    return {item["角色"]: item for item in obj.get("items", [])}


def _diminishing_multiplier(level: int) -> float:
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


def _weapon_base_score(
    weapon_info: Dict[str, Any],
    owner_tier: str,
    signature_score_map: Dict[str, float],
    standard_score: float,
) -> float:
    if weapon_info.get("weapon_class") == "signature":
        return signature_score_map.get(owner_tier, 0.0)
    return standard_score


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--detail-dir",
        type=str,
        default="game-account-evaluator/data/detail/kejinshou_top200",
    )
    parser.add_argument(
        "--tier-file",
        type=str,
        default="game-account-evaluator/configs/wuwa_role_tiers_corrected.json",
    )
    parser.add_argument(
        "--weapon-catalog",
        type=str,
        default="game-account-evaluator/configs/wuwa_weapon_catalog.json",
    )
    parser.add_argument(
        "--role-adjustments",
        type=str,
        default="game-account-evaluator/configs/wuwa_role_adjustments_33.json",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="game-account-evaluator/outputs",
    )
    parser.add_argument("--pull-score", type=float, default=1.0)
    parser.add_argument("--weapon-pull-factor", type=float, default=0.8)
    parser.add_argument("--t0-score", type=float, default=120.0)
    parser.add_argument("--t05-score", type=float, default=90.0)
    parser.add_argument("--t1-score", type=float, default=40.0)
    parser.add_argument("--t2-score", type=float, default=10.0)
    parser.add_argument("--t3-score", type=float, default=0.0)
    parser.add_argument("--t4-score", type=float, default=0.0)
    parser.add_argument("--overall-weight", type=float, default=0.4)
    parser.add_argument("--tower-weight", type=float, default=0.3)
    parser.add_argument("--requiem-weight", type=float, default=0.3)
    parser.add_argument("--four-star-factor", type=float, default=0.5)
    parser.add_argument("--weapon-t0-score", type=float, default=60.0)
    parser.add_argument("--weapon-t05-score", type=float, default=50.0)
    parser.add_argument("--weapon-t1-score", type=float, default=30.0)
    parser.add_argument("--weapon-t2-score", type=float, default=10.0)
    parser.add_argument("--weapon-standard-score", type=float, default=20.0)
    args = parser.parse_args()

    detail_dir = Path(args.detail_dir).expanduser()
    tier_file = Path(args.tier_file).expanduser()
    weapon_catalog = Path(args.weapon_catalog).expanduser()
    role_adjustments_path = Path(args.role_adjustments).expanduser()
    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    tier_map = _load_tier_map(tier_file)
    weapon_map = _load_weapon_map(weapon_catalog)
    role_adjustments = _load_role_adjustments(role_adjustments_path)
    tier_score_map = {
        "T0": args.t0_score,
        "T0.5": args.t05_score,
        "T1": args.t1_score,
        "T2": args.t2_score,
        "T3": args.t3_score,
        "T4": args.t4_score,
        "T5": args.t4_score,
    }
    mode_grade_score_map = {
        "EX": args.t0_score,
        "SS": args.t05_score,
        "S": args.t1_score,
        "A": args.t2_score,
        "B": args.t3_score,
        "C": args.t4_score,
    }
    weapon_signature_score_map = {
        "T0": args.weapon_t0_score,
        "T0.5": args.weapon_t05_score,
        "T1": args.weapon_t1_score,
        "T2": args.weapon_t2_score,
    }
    normalized_items: List[Dict[str, Any]] = []
    scored_items: List[Dict[str, Any]] = []

    for path in sorted(detail_dir.glob("*.json")):
        obj = json.loads(path.read_text(encoding="utf-8"))
        data = obj["data"]["data"]
        prop = data.get("propertyDetail", {})
        base_infos = prop.get("baseInfos", {})
        properties_info = prop.get("propertiesInfo", {})

        role_fp = {}
        weapon_fp = {}
        for fp in properties_info.get("fps", []):
            if fp.get("title") == "共鸣者":
                role_fp = fp
            elif fp.get("title") == "武器":
                weapon_fp = fp

        roles = _extract_assets(role_fp, asset_kind="role")
        weapons = _extract_assets(weapon_fp, asset_kind="weapon")

        price = _to_int(data.get("price") or data.get("payPrice"))
        star_voice = _to_int(base_infos.get("星声数量"))
        fj = _to_int(base_infos.get("浮金波纹数量"))
        zc = _to_int(base_infos.get("铸潮波纹数量"))
        hs = _to_int(base_infos.get("唤声涡纹数量"))
        wave_pulls = fj + zc * args.weapon_pull_factor
        pulls_total = star_voice / 160.0 + wave_pulls

        normalized_roles = []
        total_role_score = 0.0
        matched_roles = 0
        unmatched_roles = []
        for role in roles:
            name = role["name"]
            tier_item = tier_map.get(name)
            adjust = role_adjustments.get(name, {})
            manual_adjust = float(adjust.get("manual_adjust", 0))
            dependency_penalty = float(adjust.get("dependency_penalty", 0))
            profile = (
                _build_role_profile(
                    tier_item=tier_item,
                    star=role["star"],
                    tier_score_map=tier_score_map,
                    mode_grade_score_map=mode_grade_score_map,
                    overall_weight=args.overall_weight,
                    tower_weight=args.tower_weight,
                    requiem_weight=args.requiem_weight,
                    four_star_factor=args.four_star_factor,
                    manual_adjust=manual_adjust,
                    dependency_penalty=dependency_penalty,
                )
                if tier_item
                else None
            )
            tier = profile["display_tier"] if profile else ""
            base_score = profile["adjusted_base_score"] if profile else 0.0
            multiplier = _diminishing_multiplier(role["resonance"])
            score = base_score * multiplier if tier else 0.0
            if tier:
                matched_roles += 1
            else:
                unmatched_roles.append(name)
            total_role_score += score
            normalized_roles.append(
                {
                    "name": name,
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
                    "tier_base_score": base_score,
                    "manual_adjust": round(manual_adjust, 2),
                    "dependency_penalty": round(dependency_penalty, 2),
                    "multiplier": round(multiplier if tier else 1.0, 2),
                    "score": round(score, 2),
                }
            )

        normalized_weapons = []
        weapon_score_total = 0.0
        for weapon in weapons:
            weapon_info = weapon_map.get(weapon["name"], {})
            owner_character = str(weapon_info.get("owner_character") or "")
            owner_profile = None
            if owner_character and owner_character in tier_map:
                owner_adjust = role_adjustments.get(owner_character, {})
                owner_profile = _build_role_profile(
                    tier_item=tier_map[owner_character],
                    star="五星",
                    tier_score_map=tier_score_map,
                    mode_grade_score_map=mode_grade_score_map,
                    overall_weight=args.overall_weight,
                    tower_weight=args.tower_weight,
                    requiem_weight=args.requiem_weight,
                    four_star_factor=args.four_star_factor,
                    manual_adjust=float(owner_adjust.get("manual_adjust", 0)),
                    dependency_penalty=float(owner_adjust.get("dependency_penalty", 0)),
                )
            owner_tier = owner_profile["display_tier"] if owner_profile else ""
            displayed_resonance = weapon["resonance"]
            effective_refine = max(displayed_resonance - 1, 0)
            base_score = _weapon_base_score(
                weapon_info=weapon_info,
                owner_tier=owner_tier,
                signature_score_map=weapon_signature_score_map,
                standard_score=args.weapon_standard_score,
            )
            multiplier = _diminishing_multiplier(effective_refine)
            score = base_score * multiplier if weapon["star"] == "五星" else 0.0
            weapon_score_total += score
            normalized_weapons.append(
                {
                    "name": weapon["name"],
                    "english_name": weapon_info.get("english_name", ""),
                    "star": weapon["star"],
                    "resonance": displayed_resonance,
                    "effective_refine": effective_refine,
                    "weapon_class": weapon_info.get("weapon_class", "unknown"),
                    "owner_character": owner_character,
                    "owner_tier": owner_tier,
                    "confidence": weapon_info.get("confidence", "unknown"),
                    "source": weapon_info.get("source", ""),
                    "base_score": round(base_score, 2),
                    "multiplier": round(multiplier, 2),
                    "score": round(score, 2),
                }
            )

        strength_score = pulls_total * args.pull_score + total_role_score + weapon_score_total
        value_score = strength_score / max(price, 1)
        normalized = {
            "product_id": str(data.get("id") or ""),
            "price": price,
            "area_name": data.get("areaName") or "",
            "sub_title": data.get("subTitle") or "",
            "upper_at": data.get("upperAt") or "",
            "polish_time_desc": data.get("polishTimeDesc") or "",
            "level": _to_int(base_infos.get("联觉等级")),
            "total_yellow": _to_int(base_infos.get("总黄数")),
            "resources": {
                "star_voice": star_voice,
                "fj_waves": fj,
                "zc_waves": zc,
                "hs_waves": hs,
                "wave_pulls": wave_pulls,
                "character_pulls": fj,
                "weapon_pulls": round(zc * args.weapon_pull_factor, 2),
                "standard_pulls_ignored": hs,
                "pulls_total": round(pulls_total, 2),
            },
            "roles": normalized_roles,
            "weapons": normalized_weapons,
            "role_score_total": round(total_role_score, 2),
            "weapon_score_total": round(weapon_score_total, 2),
            "strength_score": round(strength_score, 2),
            "value_score": round(value_score, 3),
            "matched_tier_roles": matched_roles,
            "unmatched_roles": unmatched_roles,
        }
        normalized_items.append(normalized)

        tier_breakdown = " | ".join(
            f"{r['name']}:{r['tier']}@{r['resonance']}鸣={r['score']}"
            for r in normalized_roles
            if r["tier"]
        )
        weapon_breakdown = " | ".join(
            f"{w['name']}:{w['weapon_class']}->{w['owner_character'] or '常驻'}@{w['resonance']}鸣={w['score']}"
            for w in normalized_weapons
            if w["score"] > 0
        )
        scored_items.append(
            {
                "product_id": str(data.get("id") or ""),
                "price": price,
                "upper_at": data.get("upperAt") or "",
                "polish_time_desc": data.get("polishTimeDesc") or "",
                "level": _to_int(base_infos.get("联觉等级")),
                "total_yellow": _to_int(base_infos.get("总黄数")),
                "pulls_total": round(pulls_total, 2),
                "role_score_total": round(total_role_score, 2),
                "weapon_score_total": round(weapon_score_total, 2),
                "strength_score": round(strength_score, 2),
                "value_score": round(value_score, 3),
                "matched_tier_roles": matched_roles,
                "unmatched_roles_count": len(unmatched_roles),
                "tier_breakdown": tier_breakdown,
                "weapon_breakdown": weapon_breakdown,
                "sub_title": data.get("subTitle") or "",
            }
        )

    scored_items.sort(key=lambda x: (x["value_score"], x["strength_score"]), reverse=True)

    normalized_path = output_dir / "wuwa_top200_normalized_assets.json"
    normalized_path.write_text(
        json.dumps(
            {
                "meta": {
                    "generatedAt": _now_tag(),
                    "detailDir": str(detail_dir),
                    "tierFile": str(tier_file),
                    "weaponCatalog": str(weapon_catalog),
                    "roleAdjustments": str(role_adjustments_path),
                    "scoring": {
                        "pull": args.pull_score,
                        "weaponPullFactor": args.weapon_pull_factor,
                        "T0": args.t0_score,
                        "T0.5": args.t05_score,
                        "T1": args.t1_score,
                        "T2": args.t2_score,
                        "T3": args.t3_score,
                        "T4": args.t4_score,
                        "fourStarFactor": args.four_star_factor,
                        "overallWeight": args.overall_weight,
                        "towerWeight": args.tower_weight,
                        "requiemWeight": args.requiem_weight,
                        "modeGradeMap": mode_grade_score_map,
                        "weaponT0": args.weapon_t0_score,
                        "weaponT0.5": args.weapon_t05_score,
                        "weaponT1": args.weapon_t1_score,
                        "weaponT2": args.weapon_t2_score,
                        "weaponStandard": args.weapon_standard_score,
                        "roleMultiplier": {
                            "0": 1.0,
                            "1": 1.4,
                            "2": 1.7,
                            "3": 1.95,
                            "4": 2.15,
                            "5": 2.3,
                            "6": 2.4
                        },
                        "weaponRefineRule": "武器数据中的1鸣视为基础值，计分时按 max(显示鸣数-1, 0) 套用同一倍率表"
                    }
                },
                "items": normalized_items,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    csv_header = [
        "rank",
        "product_id",
        "price",
        "upper_at",
        "polish_time_desc",
        "level",
        "total_yellow",
        "pulls_total",
        "role_score_total",
        "weapon_score_total",
        "strength_score",
        "value_score",
        "matched_tier_roles",
        "unmatched_roles_count",
        "tier_breakdown",
        "weapon_breakdown",
    ]
    csv_rows = []
    table_rows = [csv_header[:9]]
    for idx, item in enumerate(scored_items, start=1):
        row = [
            str(idx),
            item["product_id"],
            str(item["price"]),
            item["upper_at"],
            item["polish_time_desc"],
            str(item["level"]),
            str(item["total_yellow"]),
            f"{item['pulls_total']:.2f}",
            f"{item['role_score_total']:.2f}",
            f"{item['weapon_score_total']:.2f}",
            f"{item['strength_score']:.2f}",
            f"{item['value_score']:.3f}",
            str(item["matched_tier_roles"]),
            str(item["unmatched_roles_count"]),
            item["tier_breakdown"],
            item["weapon_breakdown"],
        ]
        csv_rows.append(row)
        table_rows.append(row[:9])

    csv_path = output_dir / "wuwa_top200_role_tier_scored.csv"
    json_path = output_dir / "wuwa_top200_role_tier_scored.json"
    _write_csv(csv_path, header=csv_header, rows=csv_rows)
    json_path.write_text(
        json.dumps(
            {
                "meta": {
                    "generatedAt": _now_tag(),
                    "normalizedAssetsPath": str(normalized_path),
                    "tierFile": str(tier_file),
                    "roleAdjustments": str(role_adjustments_path),
                },
                "items": [
                    dict(zip(csv_header, row))
                    for row in csv_rows
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"normalized_assets: {normalized_path}")
    print(f"csv: {csv_path}")
    print(f"json: {json_path}")
    print()
    print(_format_table(table_rows[:21]))

    if outputs_exist(
        base_dir=base_dir,
        relative_paths=[
            "outputs/pzds_wuwa_top100_scored.json",
            "outputs/7881_wuwa_top100_scored.json",
        ],
    ):
        run_scripts(
            base_dir=base_dir,
            script_names=["generate_unified_wuwa_review.py"],
            reason="kejinshou current-model re-score",
        )


if __name__ == "__main__":
    main()
