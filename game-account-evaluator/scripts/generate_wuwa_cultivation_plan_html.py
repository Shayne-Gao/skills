#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
UNIFIED_JSON = OUTPUTS_DIR / "wuwa_unified_scored.json"
DEFAULT_OUTPUT = OUTPUTS_DIR / "wuwa_cultivation_plan.html"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a reusable HTML cultivation summary for a Wuwa account."
    )
    parser.add_argument(
        "--product-id",
        default="35112357",
        help="Target product_id in unified JSON. Defaults to the owned account 35112357.",
    )
    parser.add_argument(
        "--platform",
        default="kejinshou",
        help="Platform of the target account. Defaults to kejinshou.",
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


def find_row(product_id: str, platform: str) -> Dict[str, Any]:
    for row in load_unified_rows():
        if str(row.get("product_id")) == str(product_id) and str(row.get("platform")) == str(platform):
            return row
    raise SystemExit(f"Missing account in unified JSON: platform={platform}, product_id={product_id}")


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
    return f"¥{fmt_num(value)}"


def escape(value: Any) -> str:
    return html.escape(str(value))


def slugify(value: str) -> str:
    safe = "".join(ch.lower() if ch.isalnum() else "-" for ch in value)
    while "--" in safe:
        safe = safe.replace("--", "-")
    return safe.strip("-") or "item"


def chip(text: str, cls: str = "") -> str:
    extra = f" {cls}" if cls else ""
    return f'<span class="chip{extra}">{escape(text)}</span>'


def render_ranked_tags(items: Iterable[str], cls: str) -> str:
    parts: List[str] = []
    for index, item in enumerate(items, start=1):
        parts.append(
            f'<span class="rank-chip {cls}"><em>{index}</em><span>{escape(item)}</span></span>'
        )
    return "".join(parts)


def collect_five_star_roles(row: Dict[str, Any]) -> List[str]:
    names: List[str] = []
    for role in row.get("roles", []) or []:
        if role.get("star") == "五星":
            name = str(role.get("name") or "").strip()
            if name:
                names.append(name)
    return names


def collect_signature_weapons(row: Dict[str, Any]) -> List[Dict[str, str]]:
    result: List[Dict[str, str]] = []
    for weapon in row.get("weapons", []) or []:
        if weapon.get("weapon_class") != "signature":
            continue
        name = str(weapon.get("name") or "").strip()
        owner = str(weapon.get("owner_character") or "").strip()
        if not name:
            continue
        result.append({"name": name, "owner": owner})
    return result


def matched_team_lines(row: Dict[str, Any]) -> List[str]:
    lines: List[str] = []
    for team in row.get("matched_teams", []) or []:
        name = str(team.get("team_name") or "").strip()
        roles = [str(role).strip() for role in team.get("matched_roles", []) or [] if str(role).strip()]
        if name and roles:
            lines.append(f"{name}：{' / '.join(roles)}")
    return lines


def signatures_for_character(row: Dict[str, Any], character_name: str) -> List[str]:
    result: List[str] = []
    for weapon in collect_signature_weapons(row):
        if weapon["owner"] == character_name:
            result.append(weapon["name"])
    return result


def build_sources() -> List[Dict[str, str]]:
    return [
        {
            "id": "version-baseline",
            "name": "3.4 官方上线公告",
            "label": "官方公告：3.4 上线时间",
            "url": "https://www.xiao-haijing.com/ja/article/detail/12247.html",
            "kind": "版本基线",
            "summary": "确认 3.4 于 2026-06-08 上线，因此本页按 2026-06-07 在线版本 3.3 产出，不提前套用明日环境。",
        },
        {
            "id": "hiyuki-g8",
            "name": "Game8 - Hiyuki",
            "label": "Game8 绯雪攻略",
            "url": "https://game8.co/games/Wuthering-Waves/archives/586421?page=191",
            "kind": "当前版本队伍",
            "summary": "3.3 下绯雪的最佳队伍指向琳奈 + 千咲，且明确绯雪围绕共鸣解放与冰蚀体系吃满收益。",
        },
        {
            "id": "best-teams-g8",
            "name": "Game8 - Best Team Comps",
            "label": "Game8 最强配队总览",
            "url": "https://game8.co/games/Wuthering-Waves/archives/454728",
            "kind": "当前版本队伍",
            "summary": "当前版本通用配队页继续把赞妮 + 菲比 + 守岸人作为赞妮侧的最佳组合之一。",
        },
        {
            "id": "zani-g8",
            "name": "Game8 - Zani",
            "label": "Game8 赞妮攻略",
            "url": "https://game8.co/games/Wuthering-Waves/archives/486248?page=177",
            "kind": "角色构筑",
            "summary": "赞妮当前仍以衍射光噪体系队为核心，和菲比联动价值最高，且需要一定充能与完整循环。",
        },
        {
            "id": "phoebe-g8",
            "name": "Game8 - Phoebe",
            "label": "Game8 菲比攻略",
            "url": "https://game8.co/games/Wuthering-Waves/archives/486244?page=154",
            "kind": "角色构筑",
            "summary": "菲比可在两种形态间切换，在赞妮队里最优先作为挂层副 C 使用。",
        },
        {
            "id": "chisa-g8",
            "name": "Game8 - Chisa",
            "label": "Game8 千咲攻略",
            "url": "https://game8.co/games/Wuthering-Waves/archives/524880?page=136",
            "kind": "角色构筑",
            "summary": "千咲是负面状态体系支撑位，能提高负面层数上限并提供防御削减，是绯雪队的重要拼图。",
        },
        {
            "id": "shorekeeper-g8",
            "name": "Game8 - Shorekeeper",
            "label": "Game8 守岸人攻略",
            "url": "https://game8.co/games/Wuthering-Waves/archives/463667",
            "kind": "角色构筑",
            "summary": "守岸人当前仍是强势辅助位，核心点在大招覆盖与充能阈值管理。",
        },
        {
            "id": "shorekeeper-builds",
            "name": "WutheringWaves-Builds - Shorekeeper",
            "label": "WutheringWaves-Builds 守岸人构筑",
            "url": "https://wutheringwaves-builds.com/character/shorekeeper/",
            "kind": "技能与阈值",
            "summary": "守岸人的共鸣解放优先级最高，且建议约 250% 充能以吃满领域暴击/暴伤增益。",
        },
        {
            "id": "zani-builds",
            "name": "WutheringWaves-Builds - Zani",
            "label": "WutheringWaves-Builds 赞妮构筑",
            "url": "https://wutheringwaves-builds.com/character/zani/",
            "kind": "技能优先级",
            "summary": "赞妮技能优先级的共识是先回路和解放，再补普攻链，技能和变奏靠后。",
        },
        {
            "id": "phoebe-builds",
            "name": "WutheringWaves-Builds - Phoebe",
            "label": "WutheringWaves-Builds 菲比构筑",
            "url": "https://wutheringwaves-builds.com/character/phoebe/",
            "kind": "技能优先级",
            "summary": "菲比的核心在回路，其次是解放与战技；若作为副 C，先保证挂层与循环效率。",
        },
        {
            "id": "hiyuki-lootbar",
            "name": "LootBar / Hiyuki Build",
            "label": "LootBar 绯雪构筑",
            "url": "https://www.lootbar.com/blog/en/wuthering-waves-hiyuki-build-guide.html",
            "kind": "技能优先级",
            "summary": "绯雪主打共鸣解放伤害，技能升级顺序明确把解放、普攻、回路放在最高优先级。",
        },
        {
            "id": "lynae-ldshop",
            "name": "LDShop / Lynae Build",
            "label": "LDShop 琳奈构筑",
            "url": "https://www.ldshop.gg/blog/wuthering-waves/lynae-build.html",
            "kind": "技能优先级",
            "summary": "琳奈的常见优先级为回路 > 解放 > 普攻 > 战技 > 变奏，定位仍是副 C + 全队增益轴。",
        },
        {
            "id": "chisa-lootbar",
            "name": "LootBar / Chisa Build",
            "label": "LootBar 千咲构筑",
            "url": "https://lootbar.gg/blog/en/wuthering-waves-chisa-build-guide.html",
            "kind": "技能优先级",
            "summary": "千咲优先固有节点 / 回路 / 解放，战技和变奏靠后，更强调体系价值而非个人站场伤害。",
        },
        {
            "id": "shorekeeper-gamekee",
            "name": "Gamekee / Shorekeeper Guide",
            "label": "Gamekee 守岸人养成攻略",
            "url": "https://www.gamekee.com/mc/636808.html",
            "kind": "中文养成攻略",
            "summary": "中文攻略明确给出守岸人技能与武器顺序：星序协响优先，且约 250% 共鸣效率可保证大招不断。",
        },
        {
            "id": "zani-gamekee-banner",
            "name": "Gamekee / Zani Banner",
            "label": "Gamekee 赞妮卡池公告",
            "url": "https://www.gamekee.com/mc/658770.html",
            "kind": "中文名称校对",
            "summary": "用于校对赞妮专武中文名“焰光裁定”，保证页面展示采用国服中文名称。",
        },
    ]


def build_plan(row: Dict[str, Any]) -> Dict[str, Any]:
    team_lines = matched_team_lines(row)
    signature_map = {item["owner"]: item["name"] for item in collect_signature_weapons(row) if item["owner"]}
    five_star_roles = collect_five_star_roles(row)
    online_version = "3.3"
    return {
        "hero": {
            "title": "鸣潮账号培养结论页",
            "subtitle": "把账号现状、当前版本判断、优先队伍、角色技能顺序和下一步动作压缩成高密度结论面板，后续都在这个模板上迭代。",
            "account_id": str(row.get("product_id") or "-"),
            "online_version": online_version,
            "input_tier": "Tier 1：角色 + 武器",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "confidence_label": "账号事实高置信；练度判断中置信",
            "confidence_note": "本页只确定账号拥有的角色、武器、配队和版本共识；由于缺少角色等级、技能等级、声骸与武器等级截图，所以“毕业度”按阵容完整度粗估，不冒充精确练度。",
        },
        "summary": {
            "main_goal": "先把一队练穿，再补完整二队，不分散资源。",
            "main_strength": "两套现成强队框架已齐，不是缺角色，而是该把前两队做扎实。",
            "main_weakness": "当前最可能的短板不是角色池，而是守岸人充能、菲比挂层效率，以及两队的技能/声骸细节未完全成型。",
            "now_team": "霜渐队优先：绯雪 / 琳奈 / 千咲",
            "next_team": "光噪队第二：赞妮 / 菲比 / 守岸人",
            "biggest_blocker": "守岸人充能线 + 菲比挂层稳定度",
            "do_not_do": "现在不要开第三队，也不要先深刷极限声骸。",
        },
        "facts": [
            {"label": "当前主练", "value": "霜渐队", "tone": "focus"},
            {"label": "第二路线", "value": "光噪队", "tone": "secondary"},
            {"label": "完整强队", "value": f"{fmt_num(row.get('team_count'))} 套", "tone": "info"},
            {"label": "核心培养角色", "value": "6 名", "tone": "info"},
            {"label": "五星角色", "value": str(len(five_star_roles)), "tone": "neutral"},
            {"label": "专武匹配", "value": str(len(collect_signature_weapons(row))), "tone": "success"},
            {"label": "最大瓶颈", "value": "守岸人充能", "tone": "warn"},
            {"label": "待补输入", "value": "5 项", "tone": "danger"},
        ],
        "top_bullets": [
            "先完成一队，再补第二队，不把资源平均摊给所有五星。",
            "先养霜渐队，是因为当前版本共识强、你号上武器与队友匹配度也最好。",
            "第二队不是缺核心，而是更依赖守岸人的充能线和菲比的挂层稳定度。",
            "在没有精确练度输入前，先给“技能顺序 + 成长顺序 + 声骸方向”，不假装知道具体数值。",
        ],
        "team_priority": [
            {
                "priority": "P1",
                "name": "霜渐队",
                "members": ["绯雪", "琳奈", "千咲"],
                "status": "当前版本主练一队",
                "why": "Game8 当前 3.3 的绯雪最佳队仍指向琳奈 + 千咲；你的账号上这三人齐、且绯雪与千咲专武也在，属于最容易立刻兑现的主力队。",
                "actions": [
                    "先把绯雪的主 C 骨架补满，保证等级、武器、回路/解放都先到线。",
                    "同步补琳奈的循环与增益轴，别只把她当挂名副 C。",
                    "千咲优先保证回路、解放与充能/功能装，先让体系完整跑起来。",
                ],
                "evidence": ["Game8 - Hiyuki", "Game8 - Chisa", "LDShop / Lynae Build"],
            },
            {
                "priority": "P2",
                "name": "光噪队",
                "members": ["赞妮", "菲比", "守岸人"],
                "status": "主线二队",
                "why": "赞妮与菲比仍是当前版本衍射光噪体系的主组合，守岸人是最佳支撑位；你的账号这三人都在，因此第二阶段直接补成完整二队比重新开第三队更赚。",
                "actions": [
                    "守岸人先到约 250% 充能门槛，确保领域增益稳定覆盖。",
                    "菲比优先按副 C / 挂层位培养，先提高挂层与循环，再追个人输出。",
                    "赞妮在队友稳定后再补输出细节，避免先堆面板、后发现循环断档。",
                ],
                "evidence": ["Game8 - Best Team Comps", "Game8 - Zani", "Game8 - Phoebe", "WutheringWaves-Builds - Shorekeeper"],
            },
            {
                "priority": "P3",
                "name": "其余五星与旧体系",
                "members": ["维里奈", "鉴心", "安可", "凌阳", "坎特蕾拉"],
                "status": "暂缓投入",
                "why": "当前账号增长点不在第三队，而在前两队最后 20% 的完成度。老角色和旁支体系暂时不应该抢走核心资源。",
                "actions": [
                    "维里奈只保留替补治疗与过渡价值，不抢主资源。",
                    "旧 C 与非当前优先体系角色先不追技能与声骸深挖。",
                    "只有在前两队循环成型后，才考虑补第三队覆盖。",
                ],
                "evidence": ["综合判断", "Planning Playbook"],
            },
        ],
        "growth_rules": [
            {
                "title": "成长顺序总则",
                "items": [
                    "如果角色等级 / 武器等级明显没到位，先补基础骨架，再谈声骸精修。",
                    "主 C 先看输出主轴技能；副 C / 支撑位先看循环、挂层、解放和功能技能。",
                    "声骸排在基础等级、关键技能和武器之后，除非你已经接近成型。",
                ],
            },
            {
                "title": "这号的共用止损线",
                "items": [
                    "不要把声骸副词条当成第一优先级。",
                    "不要把第三队当成当前资源出口。",
                    "不要在守岸人没到充能线前，就先追赞妮与菲比的极限伤害词条。",
                ],
            },
        ],
        "timeline": [
            {
                "window": "先做的 3 件事",
                "items": [
                    "绯雪：角色等级 / 突破、武器等级、回路与解放优先补满。",
                    "千咲：先保证功能与解放循环，至少做到稳定挂负面和团队续航。",
                    "守岸人：优先冲到约 250% 充能门槛，这是第二队最重要的稳定器。",
                ],
            },
            {
                "window": "接着做的 3 件事",
                "items": [
                    "琳奈：补回路、解放与普攻链，让霜队完整兑现站场收益。",
                    "菲比：按挂层副 C 思路补回路、解放和战技，不急着当主 C 练。",
                    "赞妮：在队友稳定后，继续补输出主轴技能与声骸。",
                ],
            },
            {
                "window": "当前先别做",
                "items": [
                    "别平均铺资源给全部五星。",
                    "别在没有等级/技能截图前就深刷单角色完美声骸。",
                    "别优先开第三队。",
                ],
            },
        ],
        "characters": [
            {
                "priority": 1,
                "name": "绯雪",
                "team": "霜渐队",
                "role": "主 C / 当前版本一队核心",
                "completion": "约 85%-90%",
                "summary": "角色、队友和专武都齐，是这个账号上最适合先吃满资源的主 C。",
                "owned_weapon": signature_map.get("绯雪", "未识别到专武"),
                "next_action": "先把绯雪拉成账号第一主 C，优先投入技能、等级和专武。",
                "decision_sources": ["Game8 - Hiyuki", "LootBar / Hiyuki Build"],
                "dimension_order": ["技能", "角色等级", "武器等级", "声骸"],
                "skill_priority": ["共鸣回路", "共鸣解放", "普攻", "共鸣技能", "变奏技能"],
                "skill_note": "不同站点对“回路”和“解放”先后略有差异，但都明确属于第一梯队；实际执行可按“回路≈解放 > 普攻”的思路推进。",
                "growth_priority": ["角色等级 / 突破", "武器等级", "回路与解放", "普攻链", "声骸"],
                "steps": [
                    "第一步：如果等级和武器没满，先补到主 C 骨架线，再点技能。",
                    "第二步：优先把回路和解放抬起来，随后补普攻链。",
                    "第三步：最后再做双暴、冷凝伤、必要充能的声骸整理。",
                ],
                "skill_details": [
                    "先拉共鸣回路：这是主输出窗和资源回收的核心。",
                    "再拉共鸣解放：绯雪当前版本最关键的爆发来源之一。",
                    "第三补普攻：用于补足站场期的稳定伤害。",
                    "共鸣技能、变奏最后补，不是第一波资源位。",
                ],
                "level_details": [
                    "主 C 默认优先拉到 90 级和满突破。",
                    "如果经验或素材吃紧，先保证等级线，再回头刷完美声骸。",
                ],
                "weapon_options": [
                    f"当前识别武器：{signature_map.get('绯雪', '未识别到专武')}",
                    "最佳：灼霜（绯雪专武）。",
                    "替代：优先 5 星双暴剑，其次高面板输出剑；没有时再用过渡输出剑。",
                ],
                "echo_set": "冷凝输出 5 件套",
                "echo_main_echo": "冷凝主回响",
                "echo_main_stats": ["4C：暴击率 / 暴击伤害", "3C：冷凝伤 + 冷凝伤", "1C：攻击% + 攻击%"],
                "echo_substats": ["双暴", "攻击%", "共鸣解放伤害", "适量充能"],
                "echo_direction": "优先冷凝输出套，主词条围绕双暴 / 冷凝伤 / 攻击，先保证核心输出窗而不是极限词条。",
                "skill_sources": ["Game8 - Hiyuki", "LootBar / Hiyuki Build"],
                "weapon_sources": ["Game8 - Hiyuki", "LootBar / Hiyuki Build"],
                "echo_sources": ["Game8 - Hiyuki"],
                "evidence": ["Game8 - Hiyuki", "LootBar / Hiyuki Build"],
            },
            {
                "priority": 2,
                "name": "琳奈",
                "team": "霜渐队",
                "role": "副 C / 全队增益轴",
                "completion": "约 75%-85%",
                "summary": "她不是挂名副位，而是把绯雪上限兑现出来的关键增益位。",
                "owned_weapon": signature_map.get("琳奈", "未识别到专武"),
                "next_action": "在绯雪之后补琳奈，让霜队的循环、增益和副伤同时成型。",
                "decision_sources": ["Game8 - Hiyuki", "LDShop / Lynae Build"],
                "dimension_order": ["技能", "武器等级", "角色等级", "声骸"],
                "skill_priority": ["共鸣回路", "共鸣解放", "普攻", "共鸣技能", "变奏技能"],
                "skill_note": "多份攻略对琳奈的共识较稳定：回路、解放、普攻是前 3 位，后两项明显靠后。",
                "growth_priority": ["武器等级", "共鸣回路", "共鸣解放", "普攻链", "声骸 / 充能"],
                "steps": [
                    "第一步：先保证她的进场循环、武器和基础等级，不让增益轴断档。",
                    "第二步：回路和解放优先，随后补普攻链。",
                    "第三步：再按副 C 方向整理声骸和副词条，优先循环稳定。",
                ],
                "skill_details": [
                    "先拉共鸣回路：这是她自身输出和节奏的核心。",
                    "再拉共鸣解放：保证团队增益和轮转价值。",
                    "第三补普攻：补足站场段伤害和手感。",
                    "共鸣技能、变奏放后面补，收益低于前 3 项。",
                ],
                "level_details": [
                    "副 C 不必硬卡第一时间 90，但至少要跟上一队练度线。",
                    "如果资源吃紧，先武器和技能到线，再补角色等级。",
                ],
                "weapon_options": [
                    f"当前识别武器：{signature_map.get('琳奈', '未识别到专武')}",
                    "最佳：琳奈专武。",
                    "替代：优先高面板双暴手枪；没有时再用副 C 通用输出枪。",
                ],
                "echo_set": "琳奈主流衍射副 C 套",
                "echo_main_echo": "对应衍射副 C 主回响",
                "echo_main_stats": ["4C：暴击率 / 暴击伤害", "3C：衍射伤 / 攻击% / 视循环补充能", "1C：攻击%"],
                "echo_substats": ["双暴", "攻击%", "充能", "普攻 / 全伤相关词条"],
                "echo_direction": "按副 C / 增益位处理，先保证循环和进场节奏，再追双暴与输出副词条。",
                "skill_sources": ["LDShop / Lynae Build", "Game8 - Hiyuki"],
                "weapon_sources": ["LDShop / Lynae Build"],
                "echo_sources": ["LDShop / Lynae Build"],
                "evidence": ["LDShop / Lynae Build", "Game8 - Hiyuki"],
            },
            {
                "priority": 3,
                "name": "千咲",
                "team": "霜渐队",
                "role": "支撑位 / 治疗 / 负面体系件",
                "completion": "约 80%-85%",
                "summary": "她在这队里不是单纯奶位，而是能抬层数、补负面和保循环的体系核心。",
                "owned_weapon": signature_map.get("千咲", "未识别到专武"),
                "next_action": "让千咲先把体系功能点满，优先保证解放、回路和关键节点。",
                "decision_sources": ["Game8 - Chisa", "LootBar / Chisa Build"],
                "dimension_order": ["技能", "武器等级", "声骸", "角色等级"],
                "skill_priority": ["固有技能节点", "共鸣回路", "共鸣解放", "普攻", "共鸣技能", "变奏技能"],
                "skill_note": "若资源不够，至少先把回路、解放和关键节点拉上来；战技和变奏明显靠后。",
                "growth_priority": ["关键节点", "共鸣回路", "共鸣解放", "武器等级", "充能 / 奶套"],
                "steps": [
                    "第一步：先点关键固有节点、回路和解放，保证体系功能生效。",
                    "第二步：补武器等级与基础生存 / 治疗能力。",
                    "第三步：再补奶套或功能向声骸，优先让霜队整体更稳定。",
                ],
                "skill_details": [
                    "第一优先是关键固有节点，不点出来功能不完整。",
                    "第二拉共鸣回路，第三拉共鸣解放。",
                    "普攻只补到够用，战技和变奏靠后。",
                ],
                "level_details": [
                    "支撑位等级不用抢在主 C 前，但要保证不脆、治疗够用。",
                    "若队伍已稳定，可把等级优先级放到武器与声骸后。",
                ],
                "weapon_options": [
                    f"当前识别武器：{signature_map.get('千咲', '未识别到专武')}",
                    "最佳：千咲专武。",
                    "替代：优先暴击 / 充能向长刃，再考虑功能型过渡武器。",
                ],
                "echo_set": "千咲负面体系功能套",
                "echo_main_echo": "对应负面体系主回响",
                "echo_main_stats": ["4C：暴击率 / 暴击伤害", "3C：湮灭伤 / 攻击% / 视循环补充能", "1C：攻击%"],
                "echo_substats": ["充能", "双暴", "攻击%", "共鸣解放伤害"],
                "echo_direction": "先功能与充能，再考虑输出向微调；没有精确练度时不建议优先走纯输出千咲。",
                "skill_sources": ["Game8 - Chisa", "LootBar / Chisa Build"],
                "weapon_sources": ["Game8 - Chisa", "LootBar / Chisa Build"],
                "echo_sources": ["Game8 - Chisa"],
                "evidence": ["Game8 - Chisa", "LootBar / Chisa Build"],
            },
            {
                "priority": 4,
                "name": "赞妮",
                "team": "光噪队",
                "role": "主 C / 二队输出核心",
                "completion": "约 80%-85%",
                "summary": "本体强，但非常依赖菲比挂层与全队循环完整度；不能脱离衍射光噪体系单独评估。",
                "owned_weapon": signature_map.get("赞妮", "未识别到专武"),
                "next_action": "霜队稳定后，马上补赞妮，把第二队主 C 骨架拉起来。",
                "decision_sources": ["Game8 - Best Team Comps", "Game8 - Zani"],
                "dimension_order": ["技能", "角色等级", "武器等级", "声骸"],
                "skill_priority": ["共鸣回路", "共鸣解放", "普攻 / 重击链", "共鸣技能", "变奏技能"],
                "skill_note": "对下位顺序不同站点有小分歧，但“回路 + 解放”在最前面是一致结论。",
                "growth_priority": ["角色等级 / 武器等级", "共鸣回路", "共鸣解放", "普攻 / 重击链", "声骸"],
                "steps": [
                    "第一步：先补主 C 骨架，不在低等级状态下直接深刷声骸。",
                    "第二步：回路和解放优先，随后补普攻 / 重击链。",
                    "第三步：在守岸人和菲比稳定后，再精修声骸和词条。",
                ],
                "skill_details": [
                    "先拉共鸣回路：赞妮的衍射光噪核心输出轴。",
                    "再拉共鸣解放：补爆发与完整轮转。",
                    "第三补普攻 / 重击链：她很吃重击段收益。",
                    "共鸣技能、变奏最后补。",
                ],
                "level_details": [
                    "二队主 C 也建议最终 90 级，但放在一队主 C 之后。",
                    "若只能选一个先拉，优先等级和技能，不先赌声骸。",
                ],
                "weapon_options": [
                    f"当前识别武器：{signature_map.get('赞妮', '未识别到专武')}",
                    "最佳：焰光裁定（赞妮专武，按国服中文名展示）。",
                    "替代：优先高面板双暴拳套，其次重击/普攻收益高的五星拳套。",
                ],
                "echo_set": "此间永驻之光 5 件套",
                "echo_main_echo": "赞妮主流衍射输出主回响",
                "echo_main_stats": ["4C：暴击率 / 暴击伤害", "3C：衍射伤 + 衍射伤", "1C：攻击% + 攻击%"],
                "echo_substats": ["双暴", "攻击%", "重击收益", "少量充能"],
                "echo_direction": "优先衍射光噪主轴的输出套，围绕双暴、衍射伤、重击收益来做。",
                "skill_sources": ["Game8 - Zani", "WutheringWaves-Builds - Zani"],
                "weapon_sources": ["Game8 - Zani", "Gamekee / Zani Banner"],
                "echo_sources": ["Game8 - Zani"],
                "evidence": ["Game8 - Zani", "WutheringWaves-Builds - Zani"],
            },
            {
                "priority": 5,
                "name": "菲比",
                "team": "光噪队",
                "role": "副 C / 挂层位 / 衍射光噪体系发动机",
                "completion": "约 70%-75%",
                "summary": "她现在在你号上的第一价值不是单独站主 C，而是让赞妮队真正成型。",
                "owned_weapon": signature_map.get("菲比", "未识别到专武"),
                "next_action": "按挂层副 C 的思路练菲比，让赞妮队先能稳定跑起来。",
                "decision_sources": ["Game8 - Phoebe", "Game8 - Zani"],
                "dimension_order": ["技能", "武器等级", "声骸", "角色等级"],
                "skill_priority": ["共鸣回路", "共鸣解放", "共鸣技能", "普攻", "变奏技能"],
                "skill_note": "作为赞妮队副 C 时，优先做回路、解放和战技，确保核心挂层与循环。",
                "growth_priority": ["共鸣回路", "共鸣解放", "共鸣技能", "武器等级", "声骸 / 充能"],
                "steps": [
                    "第一步：按挂层副 C 路线点回路和解放，不急着追满主 C 面板。",
                    "第二步：补战技与武器等级，让挂层节奏更顺。",
                    "第三步：最后才根据实际体验决定偏 Moonlit 功能流还是偏输出流。",
                ],
                "skill_details": [
                    "先拉共鸣回路：决定挂层和形态价值。",
                    "再拉共鸣解放：补足轮转期伤害与功能。",
                    "第三补共鸣技能：服务核心挂层和节奏。",
                    "普攻和变奏优先级低于前 3 项。",
                ],
                "level_details": [
                    "副 C 等级可后置，但不要低到影响生存和基础伤害。",
                    "在第二队没成型前，等级不是第一投入位。",
                ],
                "weapon_options": [
                    f"当前识别武器：{signature_map.get('菲比', '未识别到专武')}",
                    "最佳：菲比专武。",
                    "替代：如果走副 C，可先用高面板双暴音感仪；没有时用功能向过渡音感仪。",
                ],
                "echo_set": "此间永驻之光 5 件套；副 C 过渡可轻云出月 5 件套",
                "echo_main_echo": "优先衍射主回响；过渡可走轻云出月主回响",
                "echo_main_stats": ["4C：暴击率 / 暴击伤害", "3C：衍射伤 / 视副C需求补充能", "1C：攻击%"],
                "echo_substats": ["双暴", "攻击%", "充能", "共鸣技能 / 解放收益"],
                "echo_direction": "在赞妮队里优先副 C / 挂层思路，可先功能向，后续再根据练度切到更输出的配置。",
                "skill_sources": ["Game8 - Phoebe", "WutheringWaves-Builds - Phoebe"],
                "weapon_sources": ["Game8 - Phoebe"],
                "echo_sources": ["Game8 - Phoebe"],
                "evidence": ["Game8 - Phoebe", "WutheringWaves-Builds - Phoebe"],
            },
            {
                "priority": 6,
                "name": "守岸人",
                "team": "光噪队",
                "role": "支撑位 / 二队稳定器",
                "completion": "约 70%-80%",
                "summary": "她的最大价值不是治疗量数字，而是领域增益与整队循环稳定度。",
                "owned_weapon": signatures_for_character(row, "守岸人")[0] if signatures_for_character(row, "守岸人") else "未识别到专武",
                "next_action": "优先补守岸人的充能阈值和解放，让第二队从“能上场”变成“能稳定打”。",
                "decision_sources": ["Game8 - Best Team Comps", "Gamekee / Shorekeeper Guide"],
                "dimension_order": ["声骸", "技能", "武器等级", "角色等级"],
                "skill_priority": ["共鸣解放", "变奏技能", "共鸣技能", "共鸣回路", "普攻"],
                "skill_note": "守岸人的技能顺序站点共识很高，关键就是先把解放和进场价值点出来。",
                "growth_priority": ["充能到约 250%", "共鸣解放", "变奏技能", "共鸣技能", "奶套 / 生命"],
                "steps": [
                    "第一步：优先把充能做到约 250%，这是必须先满足的阈值。",
                    "第二步：技能优先点解放，再点变奏和战技。",
                    "第三步：最后再补生命、奶套和更舒服的生存副词条。",
                ],
                "skill_details": [
                    "第一优先共鸣解放，所有核心 buff 都围绕它。",
                    "第二拉变奏技能，保证进场价值和团队衔接。",
                    "第三补共鸣技能，回路和普攻靠后。",
                ],
                "level_details": [
                    "等级优先级低于充能线、技能和功能声骸。",
                    "只要生存够、奶量够，就不急着和主 C 抢等级资源。",
                ],
                "weapon_options": [
                    f"当前识别武器：{signatures_for_character(row, '守岸人')[0] if signatures_for_character(row, '守岸人') else '未识别到专武'}",
                    "最佳：星序协响（守岸人专武，按国服中文名展示）。",
                    "4 星高性价比替代：奇幻变奏。",
                ],
                "echo_set": "隐世回光 5 件套",
                "echo_main_echo": "无归的谬误",
                "echo_main_stats": ["4C：治疗加成 / 生命%", "3C：充能 + 充能 / 生命%", "1C：生命%"],
                "echo_substats": ["充能", "生命%", "共鸣效率相关词条", "生存词条"],
                "echo_direction": "优先 Rejuvenating Glow / Fallacy of No Return 这类功能组合，先满足充能，再谈奶量和杂项。",
                "skill_sources": ["Gamekee / Shorekeeper Guide", "WutheringWaves-Builds - Shorekeeper"],
                "weapon_sources": ["Gamekee / Shorekeeper Guide"],
                "echo_sources": ["Gamekee / Shorekeeper Guide", "WutheringWaves-Builds - Shorekeeper"],
                "evidence": ["Game8 - Shorekeeper", "WutheringWaves-Builds - Shorekeeper"],
            },
        ],
        "delayed_targets": [
            {"name": "维里奈", "reason": "保留替补治疗与兼容位价值，但不应抢走当前两队核心资源。"},
            {"name": "鉴心 / 安可 / 凌阳", "reason": "老体系或旁支角色，不是当前账号最有效的增长点。"},
            {"name": "第三队开发", "reason": "当前账号更需要把两套现成强队补到完整状态。"},
            {"name": "极限声骸词条", "reason": "在等级、武器和关键技能没到位前，深刷声骸性价比偏低。"},
        ],
        "missing_inputs": [
            "角色等级 / 突破",
            "武器等级",
            "技能等级",
            "声骸套装与词条",
            "当前周本 / 日常材料瓶颈",
        ],
        "sources": build_sources(),
        "fact_box": {
            "matched_teams": team_lines,
            "five_star_roles": five_star_roles,
            "signature_weapons": collect_signature_weapons(row),
            "resources": row.get("resources") or {},
        },
    }


def render_source_list(sources: Iterable[Dict[str, str]]) -> str:
    cards = []
    for source in sources:
        cards.append(
            f"""
            <article class="source-card" id="source-{escape(source['id'])}">
              <div class="source-kind">{escape(source["kind"])}</div>
              <h4><a href="{escape(source["url"])}" target="_blank" rel="noreferrer">{escape(source.get("label") or source["name"])}</a></h4>
              <p>{escape(source["summary"])}</p>
            </article>
            """
        )
    return "".join(cards)


def render_source_links(source_names: Iterable[str], source_index: Dict[str, Dict[str, str]]) -> str:
    links: List[str] = []
    seen = set()
    for name in source_names:
        if name in seen:
            continue
        seen.add(name)
        source = source_index.get(name)
        if not source:
            links.append(chip(name, "soft"))
            continue
        links.append(
            f'<a class="chip soft link-chip" href="{escape(source["url"])}" target="_blank" rel="noreferrer">{escape(source.get("label") or source["name"])}</a>'
        )
    return "".join(links)


def render_team_cards(teams: Iterable[Dict[str, Any]]) -> str:
    cards = []
    for team in teams:
        actions = "".join(f"<li>{escape(item)}</li>" for item in team["actions"])
        evidence = "".join(chip(item, "soft") for item in team["evidence"])
        members = "".join(chip(member, "member") for member in team["members"])
        team_cls = "team-p1" if team["priority"] == "P1" else "team-p2" if team["priority"] == "P2" else "team-p3"
        cards.append(
            f"""
            <article class="team-card {team_cls}">
              <div class="team-head">
                <div>
                  <div class="pill priority">{escape(team["priority"])}</div>
                  <h3>{escape(team["name"])}</h3>
                  <p class="team-status">{escape(team["status"])}</p>
                </div>
                <div class="member-list">{members}</div>
              </div>
              <p>{escape(team["why"])}</p>
              <ul>{actions}</ul>
              <div class="evidence-row">{evidence}</div>
            </article>
            """
        )
    return "".join(cards)


def render_priority_board(characters: Iterable[Dict[str, Any]], source_index: Dict[str, Dict[str, str]]) -> str:
    cards = []
    for item in sorted(characters, key=lambda x: int(x.get("priority", 999))):
        role_cls = "tag-main" if "主 C" in item["role"] else "tag-sub" if "副 C" in item["role"] else "tag-support"
        order = render_ranked_tags(item["dimension_order"], "dimension")
        decision_sources = render_source_links(item.get("decision_sources", []), source_index)
        cards.append(
            f"""
            <a class="priority-card" href="#{slugify(item["name"])}">
              <div class="priority-top">
                <span class="priority-index">P{int(item["priority"])}</span>
                <div>
                  <strong>{escape(item["name"])}</strong>
                  <div class="badge-row compact">
                    {chip(item["team"], "member")}
                    {chip(item["role"], role_cls)}
                  </div>
                </div>
              </div>
              <p>{escape(item["next_action"])}</p>
              <div class="priority-order">{order}</div>
              <div class="source-row"><span>来源</span><div class="chip-row">{decision_sources}</div></div>
            </a>
            """
        )
    return "".join(cards)


def render_character_cards(characters: Iterable[Dict[str, Any]], source_index: Dict[str, Dict[str, str]]) -> str:
    cards = []
    for item in sorted(characters, key=lambda x: int(x.get("priority", 999))):
        skill_priority = render_ranked_tags(item["skill_priority"], "skill")
        dimension_priority = render_ranked_tags(item["dimension_order"], "dimension")
        steps = "".join(f"<li>{escape(step)}</li>" for step in item["steps"])
        skill_details = "".join(f"<li>{escape(step)}</li>" for step in item["skill_details"])
        level_details = "".join(f"<li>{escape(step)}</li>" for step in item["level_details"])
        weapon_details = "".join(f"<li>{escape(step)}</li>" for step in item["weapon_options"])
        echo_stats = "".join(chip(text, "soft") for text in item["echo_main_stats"])
        echo_substats = "".join(chip(text, "soft") for text in item["echo_substats"])
        evidence = "".join(chip(text, "soft") for text in item["evidence"])
        card_id = slugify(item["name"])
        team_cls = "char-frost" if item["team"] == "霜渐队" else "char-light" if item["team"] == "光噪队" else "char-other"
        role_cls = "tag-main" if "主 C" in item["role"] else "tag-sub" if "副 C" in item["role"] else "tag-support"
        decision_sources = render_source_links(item.get("decision_sources", []), source_index)
        skill_sources = render_source_links(item.get("skill_sources", []), source_index)
        weapon_sources = render_source_links(item.get("weapon_sources", []), source_index)
        echo_sources = render_source_links(item.get("echo_sources", []), source_index)
        cards.append(
            f"""
            <article class="character-card {team_cls}" id="{card_id}" data-team="{escape(item["team"])}" data-name="{escape(item["name"])}">
              <div class="character-head">
                <div>
                  <div class="title-line">
                    <span class="priority-index">P{int(item["priority"])}</span>
                    <h3>{escape(item["name"])}</h3>
                  </div>
                  <div class="badge-row compact">
                    {chip(item["team"], "member")}
                    {chip(item["role"], role_cls)}
                  </div>
                </div>
                <div class="completion">{escape(item["completion"])}</div>
              </div>
              <p>{escape(item["summary"])}</p>
              <div class="kv-grid">
                <div class="kv"><span>你接下来该做什么</span><strong>{escape(item["next_action"])}</strong></div>
                <div class="kv"><span>当前武器</span><strong>{escape(item["owned_weapon"])}</strong></div>
              </div>
              <section class="sub-section">
                <h4>培养项目顺序</h4>
                <div class="chip-row">{dimension_priority}</div>
                <div class="source-row"><span>决策来源</span><div class="chip-row">{decision_sources}</div></div>
              </section>
              <section class="sub-section">
                <h4>第一层执行步骤</h4>
                <ul>{steps}</ul>
              </section>
              <section class="sub-section">
                <div class="tab-group" data-tab-group="{card_id}">
                  <div class="tab-nav">
                    <button class="tab-btn active" type="button" data-tab="{card_id}-skill">技能</button>
                    <button class="tab-btn" type="button" data-tab="{card_id}-level">等级</button>
                    <button class="tab-btn" type="button" data-tab="{card_id}-weapon">武器</button>
                    <button class="tab-btn" type="button" data-tab="{card_id}-echo">声骸</button>
                  </div>
                  <div class="tab-pane active" data-pane="{card_id}-skill">
                    <div class="chip-row">{skill_priority}</div>
                    <p class="note">{escape(item["skill_note"])}</p>
                    <ul>{skill_details}</ul>
                    <div class="source-row"><span>来源</span><div class="chip-row">{skill_sources}</div></div>
                  </div>
                  <div class="tab-pane" data-pane="{card_id}-level">
                    <ul>{level_details}</ul>
                    <div class="source-row"><span>来源</span><div class="chip-row">{decision_sources}</div></div>
                  </div>
                  <div class="tab-pane" data-pane="{card_id}-weapon">
                    <ul>{weapon_details}</ul>
                    <div class="source-row"><span>来源</span><div class="chip-row">{weapon_sources}</div></div>
                  </div>
                  <div class="tab-pane" data-pane="{card_id}-echo">
                    <div class="echo-grid">
                      <div class="kv"><span>推荐套装</span><strong>{escape(item["echo_set"])}</strong></div>
                      <div class="kv"><span>推荐主回响</span><strong>{escape(item["echo_main_echo"])}</strong></div>
                    </div>
                    <p class="note">{escape(item["echo_direction"])}</p>
                    <div class="fact-row">
                      <strong>主词条</strong>
                      <div class="chip-row">{echo_stats}</div>
                    </div>
                    <div class="fact-row">
                      <strong>副词条</strong>
                      <div class="chip-row">{echo_substats}</div>
                    </div>
                    <div class="source-row"><span>来源</span><div class="chip-row">{echo_sources}</div></div>
                  </div>
                </div>
              </section>
              <div class="evidence-row">{evidence}</div>
            </article>
            """
        )
    return "".join(cards)


def build_html(plan: Dict[str, Any]) -> str:
    data_json = json.dumps(plan, ensure_ascii=False)
    source_index = {source["name"]: source for source in plan["sources"]}
    priority_board = render_priority_board(plan["characters"], source_index)
    facts = plan["facts"]
    fact_cards = "".join(
        f'<div class="stat {escape(item.get("tone", ""))}"><span>{escape(item["label"])}</span><strong>{escape(item["value"])}</strong></div>'
        for item in facts
    )
    top_bullets = "".join(f"<li>{escape(item)}</li>" for item in plan["top_bullets"])
    quick_cards = "".join(
        (
            f'<article class="quick-card focus"><span>当前主线</span><strong>{escape(plan["summary"]["now_team"])}</strong></article>'
            f'<article class="quick-card secondary"><span>第二目标</span><strong>{escape(plan["summary"]["next_team"])}</strong></article>'
            f'<article class="quick-card warn"><span>最大瓶颈</span><strong>{escape(plan["summary"]["biggest_blocker"])}</strong></article>'
            f'<article class="quick-card danger"><span>当前别做</span><strong>{escape(plan["summary"]["do_not_do"])}</strong></article>'
        )
    )
    growth_sections = []
    for group in plan["growth_rules"]:
        items = "".join(f"<li>{escape(item)}</li>" for item in group["items"])
        growth_sections.append(
            f"""
            <article class="rule-card">
              <h3>{escape(group["title"])}</h3>
              <ul>{items}</ul>
            </article>
            """
        )
    timeline_sections = []
    for group in plan["timeline"]:
        items = "".join(f"<li>{escape(item)}</li>" for item in group["items"])
        timeline_sections.append(
            f"""
            <article class="timeline-card">
              <h3>{escape(group["window"])}</h3>
              <ul>{items}</ul>
            </article>
            """
        )
    delayed = "".join(
        f"<li><strong>{escape(item['name'])}</strong>：{escape(item['reason'])}</li>"
        for item in plan["delayed_targets"]
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>鸣潮账号培养结论页</title>
  <style>
    :root {{
      --bg:#08111f;
      --bg2:#0d1730;
      --panel:rgba(15,24,45,.92);
      --panel2:rgba(19,30,58,.95);
      --line:#26375f;
      --text:#edf3ff;
      --muted:#9aabd4;
      --accent:#84a8ff;
      --accent2:#76dfb8;
      --warn:#f4c76a;
      --danger:#f08d9f;
      --shadow:0 22px 60px rgba(0,0,0,.28);
    }}
    * {{ box-sizing:border-box; }}
    html,body {{ margin:0; padding:0; }}
    body {{
      font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
      color:var(--text);
      background:
        radial-gradient(circle at top left, rgba(132,168,255,.16), transparent 28%),
        radial-gradient(circle at top right, rgba(118,223,184,.10), transparent 24%),
        linear-gradient(180deg,var(--bg),var(--bg2));
    }}
    a {{ color:#aecaFF; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    .wrap {{ max-width:1560px; margin:0 auto; padding:24px; }}
    .hero, .panel {{
      background:var(--panel);
      border:1px solid var(--line);
      border-radius:20px;
      box-shadow:var(--shadow);
    }}
    .hero {{ padding:26px; }}
    .hero-top {{
      display:flex;
      justify-content:space-between;
      gap:18px;
      align-items:flex-start;
    }}
    .hero h1 {{ margin:0 0 10px; font-size:34px; line-height:1.12; }}
    .hero p {{ margin:8px 0; color:var(--muted); line-height:1.65; }}
    .meta-row, .nav-row, .badge-row, .chip-row, .evidence-row {{
      display:flex;
      flex-wrap:wrap;
      gap:8px;
    }}
    .badge-row.compact {{ margin-top:8px; }}
    .nav-row {{ margin-top:16px; }}
    .badge, .chip, .pill {{
      display:inline-flex;
      align-items:center;
      gap:6px;
      padding:6px 12px;
      border-radius:999px;
      border:1px solid var(--line);
      background:rgba(35,51,90,.88);
      font-size:13px;
      color:#e8eeff;
    }}
    .badge.accent {{ border-color:rgba(132,168,255,.55); background:rgba(52,78,145,.34); }}
    .badge.soft {{ background:rgba(28,40,73,.76); }}
    .chip.soft {{ background:rgba(28,40,73,.76); color:#d8e3ff; }}
    .chip.member {{ background:rgba(39,79,61,.34); border-color:rgba(118,223,184,.22); }}
    .chip.skill {{ background:rgba(69,58,121,.38); border-color:rgba(160,146,255,.25); }}
    .chip.growth {{ background:rgba(91,71,30,.34); border-color:rgba(244,199,106,.24); }}
    .chip.tag-main {{ background:rgba(73,104,196,.36); border-color:rgba(132,168,255,.42); }}
    .chip.tag-sub {{ background:rgba(38,104,126,.34); border-color:rgba(105,215,255,.30); }}
    .chip.tag-support {{ background:rgba(63,114,74,.34); border-color:rgba(118,223,184,.28); }}
    .pill.priority {{ background:rgba(84,109,191,.34); border-color:rgba(132,168,255,.45); }}
    .panel {{ padding:20px; margin-top:18px; }}
    .section-title {{
      display:flex;
      justify-content:space-between;
      gap:12px;
      align-items:flex-end;
      margin-bottom:14px;
    }}
    .section-title h2 {{ margin:0; font-size:22px; }}
    .section-title p {{ margin:0; color:var(--muted); }}
    .stats {{
      display:grid;
      grid-template-columns:repeat(4,minmax(0,1fr));
      gap:12px;
      margin-top:18px;
    }}
    .stat {{
      background:var(--panel2);
      border:1px solid var(--line);
      border-radius:16px;
      padding:14px 16px;
      position:relative;
      overflow:hidden;
    }}
    .stat::before {{
      content:"";
      position:absolute;
      inset:0 auto 0 0;
      width:4px;
      background:rgba(132,168,255,.4);
    }}
    .stat.focus::before {{ background:#76dfb8; }}
    .stat.secondary::before {{ background:#84a8ff; }}
    .stat.info::before {{ background:#7dc8ff; }}
    .stat.success::before {{ background:#66e2a3; }}
    .stat.warn::before {{ background:#f4c76a; }}
    .stat.danger::before {{ background:#f08d9f; }}
    .stat.neutral::before {{ background:#6d7da4; }}
    .hero-quick {{
      display:grid;
      grid-template-columns:repeat(4,minmax(0,1fr));
      gap:12px;
      margin-top:18px;
    }}
    .quick-card {{
      padding:14px 16px;
      border-radius:16px;
      border:1px solid var(--line);
      background:var(--panel2);
    }}
    .quick-card span {{
      display:block;
      font-size:12px;
      color:var(--muted);
      text-transform:uppercase;
      letter-spacing:.04em;
    }}
    .quick-card strong {{
      display:block;
      margin-top:8px;
      line-height:1.45;
      font-size:16px;
    }}
    .quick-card.focus {{ background:linear-gradient(180deg, rgba(35,86,70,.55), rgba(19,30,58,.95)); }}
    .quick-card.secondary {{ background:linear-gradient(180deg, rgba(37,70,132,.52), rgba(19,30,58,.95)); }}
    .quick-card.warn {{ background:linear-gradient(180deg, rgba(110,79,29,.48), rgba(19,30,58,.95)); }}
    .quick-card.danger {{ background:linear-gradient(180deg, rgba(118,49,66,.42), rgba(19,30,58,.95)); }}
    .summary-band {{
      display:grid;
      grid-template-columns:1.2fr .8fr;
      gap:14px;
    }}
    .stat span {{
      display:block;
      color:var(--muted);
      font-size:12px;
      text-transform:uppercase;
      letter-spacing:.04em;
    }}
    .stat strong {{
      display:block;
      margin-top:8px;
      font-size:24px;
    }}
    .main {{
      display:grid;
      gap:18px;
      margin-top:18px;
    }}
    .summary-grid, .team-grid, .rule-grid, .timeline-grid, .source-grid {{
      display:grid;
      gap:14px;
    }}
    .priority-board {{
      display:grid;
      grid-template-columns:repeat(3,minmax(0,1fr));
      gap:14px;
    }}
    .priority-card {{
      display:block;
      color:var(--text);
      background:var(--panel2);
      border:1px solid var(--line);
      border-radius:18px;
      padding:16px;
      box-shadow:inset 0 0 0 1px rgba(132,168,255,.05);
      transition:transform .15s ease, border-color .15s ease;
    }}
    .priority-card:hover {{
      transform:translateY(-2px);
      border-color:rgba(132,168,255,.4);
      text-decoration:none;
    }}
    .priority-top {{
      display:flex;
      align-items:flex-start;
      gap:12px;
      margin-bottom:10px;
    }}
    .priority-index {{
      display:inline-flex;
      align-items:center;
      justify-content:center;
      min-width:36px;
      height:36px;
      padding:0 10px;
      border-radius:999px;
      background:linear-gradient(180deg, rgba(118,223,184,.35), rgba(54,95,83,.45));
      border:1px solid rgba(118,223,184,.25);
      font-size:13px;
      font-weight:800;
      letter-spacing:.04em;
    }}
    .priority-card strong {{ font-size:18px; }}
    .priority-card p {{
      margin:0 0 12px;
      color:var(--muted);
      line-height:1.55;
    }}
    .priority-order {{
      display:flex;
      flex-wrap:wrap;
      gap:8px;
    }}
    .summary-grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }}
    .team-grid {{ grid-template-columns:repeat(3,minmax(0,1fr)); }}
    .rule-grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }}
    .timeline-grid {{ grid-template-columns:repeat(3,minmax(0,1fr)); }}
    .source-grid {{ grid-template-columns:repeat(3,minmax(0,1fr)); }}
    .summary-card, .team-card, .rule-card, .timeline-card, .source-card, .character-card {{
      background:var(--panel2);
      border:1px solid var(--line);
      border-radius:18px;
      padding:18px;
    }}
    .team-card.team-p1 {{ border-color:rgba(118,223,184,.35); box-shadow:inset 0 0 0 1px rgba(118,223,184,.08); }}
    .team-card.team-p2 {{ border-color:rgba(132,168,255,.35); box-shadow:inset 0 0 0 1px rgba(132,168,255,.08); }}
    .team-card.team-p3 {{ border-color:rgba(240,141,159,.24); box-shadow:inset 0 0 0 1px rgba(240,141,159,.06); }}
    .summary-card h3, .team-card h3, .rule-card h3, .timeline-card h3, .source-card h4, .character-card h3 {{
      margin:0 0 10px;
      font-size:20px;
    }}
    .title-line {{
      display:flex;
      align-items:center;
      gap:10px;
    }}
    .title-line h3 {{ margin:0; }}
    .summary-card p, .team-card p, .rule-card li, .timeline-card li, .source-card p, .character-card p, .character-card li {{
      color:var(--muted);
      line-height:1.65;
    }}
    .summary-card ul, .team-card ul, .rule-card ul, .timeline-card ul, .character-card ul {{
      margin:0;
      padding-left:18px;
    }}
    .fact-panel {{
      display:grid;
      gap:12px;
    }}
    .fact-row strong {{
      display:block;
      margin-bottom:8px;
      font-size:14px;
    }}
    .team-head, .character-head {{
      display:flex;
      justify-content:space-between;
      gap:12px;
      align-items:flex-start;
    }}
    .team-status, .muted {{
      color:var(--muted);
      font-size:13px;
    }}
    .completion {{
      min-width:116px;
      text-align:right;
      padding:10px 12px;
      border-radius:14px;
      border:1px solid var(--line);
      background:rgba(40,58,103,.74);
      font-weight:700;
    }}
    .character-card.char-frost {{ border-color:rgba(132,168,255,.34); }}
    .character-card.char-light {{ border-color:rgba(244,199,106,.30); }}
    .character-card.char-other {{ border-color:rgba(109,125,164,.28); }}
    .member-list {{
      display:flex;
      flex-wrap:wrap;
      justify-content:flex-end;
      gap:8px;
      max-width:45%;
    }}
    .filter-bar {{
      display:flex;
      gap:10px;
      margin-bottom:14px;
      flex-wrap:wrap;
      align-items:center;
    }}
    .filter-bar input, .filter-bar select {{
      padding:10px 12px;
      border-radius:12px;
      border:1px solid var(--line);
      background:rgba(8,14,27,.72);
      color:var(--text);
      font-size:14px;
    }}
    .filter-bar input {{ min-width:220px; }}
    .character-grid {{
      display:grid;
      grid-template-columns:1fr;
      gap:14px;
    }}
    .kv-grid {{
      display:grid;
      grid-template-columns:repeat(2,minmax(0,1fr));
      gap:10px;
      margin:12px 0;
    }}
    .kv {{
      background:rgba(14,22,42,.68);
      border:1px solid var(--line);
      border-radius:14px;
      padding:12px;
    }}
    .kv span {{
      display:block;
      color:var(--muted);
      font-size:12px;
      margin-bottom:6px;
    }}
    .kv strong {{ font-size:15px; }}
    .rank-chip {{
      display:inline-flex;
      align-items:center;
      gap:8px;
      padding:7px 11px 7px 8px;
      border-radius:999px;
      border:1px solid var(--line);
      background:rgba(20,31,59,.88);
      font-size:13px;
      color:#eaf0ff;
    }}
    .rank-chip em {{
      display:inline-flex;
      align-items:center;
      justify-content:center;
      width:20px;
      height:20px;
      border-radius:999px;
      font-style:normal;
      font-size:11px;
      font-weight:700;
      background:rgba(255,255,255,.08);
    }}
    .rank-chip.dimension {{ background:rgba(35,66,111,.66); }}
    .rank-chip.skill:nth-child(1) em, .rank-chip.growth:nth-child(1) em, .rank-chip.dimension:nth-child(1) em {{ background:#2f9d72; }}
    .rank-chip.skill:nth-child(2) em, .rank-chip.growth:nth-child(2) em, .rank-chip.dimension:nth-child(2) em {{ background:#4f84d7; }}
    .rank-chip.skill:nth-child(3) em, .rank-chip.growth:nth-child(3) em, .rank-chip.dimension:nth-child(3) em {{ background:#8a69d6; }}
    .rank-chip.skill:nth-child(4) em, .rank-chip.growth:nth-child(4) em, .rank-chip.dimension:nth-child(4) em {{ background:#b78349; }}
    .rank-chip.skill:nth-child(5) em, .rank-chip.growth:nth-child(5) em,
    .rank-chip.skill:nth-child(6) em, .rank-chip.growth:nth-child(6) em,
    .rank-chip.dimension:nth-child(5) em, .rank-chip.dimension:nth-child(6) em {{ background:#905a66; }}
    .detail-block {{
      margin-top:12px;
      border:1px solid rgba(38,55,95,.72);
      border-radius:16px;
      background:rgba(12,20,39,.55);
      overflow:hidden;
    }}
    .detail-block summary {{
      cursor:pointer;
      list-style:none;
      padding:14px 16px;
      font-weight:700;
      background:rgba(18,29,56,.72);
    }}
    .detail-block summary::-webkit-details-marker {{ display:none; }}
    .detail-body {{ padding:14px 16px 16px; }}
    .echo-grid {{
      display:grid;
      grid-template-columns:repeat(2,minmax(0,1fr));
      gap:10px;
      margin-bottom:12px;
    }}
    .sub-section {{
      margin-top:14px;
      padding-top:14px;
      border-top:1px solid rgba(38,55,95,.72);
    }}
    .sub-section h4 {{ margin:0 0 10px; font-size:15px; }}
    .note {{ font-size:13px; }}
    .source-row {{
      display:flex;
      align-items:flex-start;
      gap:10px;
      margin-top:12px;
      padding-top:12px;
      border-top:1px dashed rgba(38,55,95,.72);
    }}
    .source-row span {{
      flex:0 0 auto;
      font-size:12px;
      color:var(--muted);
      padding-top:7px;
    }}
    .link-chip:hover {{ text-decoration:none; border-color:rgba(132,168,255,.4); }}
    .tab-nav {{
      display:flex;
      flex-wrap:wrap;
      gap:8px;
      margin-bottom:12px;
    }}
    .tab-btn {{
      appearance:none;
      border:1px solid var(--line);
      background:rgba(20,31,59,.82);
      color:var(--text);
      border-radius:12px;
      padding:10px 14px;
      font-size:13px;
      cursor:pointer;
    }}
    .tab-btn.active {{
      background:rgba(55,84,150,.52);
      border-color:rgba(132,168,255,.45);
    }}
    .tab-pane {{
      display:none;
      padding:14px;
      border:1px solid rgba(38,55,95,.72);
      border-radius:16px;
      background:rgba(12,20,39,.55);
    }}
    .tab-pane.active {{ display:block; }}
    .source-kind {{
      display:inline-flex;
      margin-bottom:8px;
      padding:4px 9px;
      border-radius:999px;
      background:rgba(36,53,97,.82);
      border:1px solid var(--line);
      color:#dfe8ff;
      font-size:12px;
    }}
    .empty {{
      padding:30px 20px;
      border:1px dashed var(--line);
      border-radius:16px;
      text-align:center;
      color:var(--muted);
      background:rgba(14,22,42,.55);
    }}
    @media (max-width: 1200px) {{
      .stats, .hero-quick, .summary-grid, .summary-band, .priority-board, .team-grid, .rule-grid, .timeline-grid, .source-grid, .character-grid, .echo-grid {{ grid-template-columns:1fr; }}
      .member-list {{ max-width:none; justify-content:flex-start; }}
    }}
    @media (max-width: 760px) {{
      .wrap {{ padding:14px; }}
      .hero-top, .team-head, .character-head {{ flex-direction:column; }}
      .kv-grid {{ grid-template-columns:1fr; }}
      .completion {{ text-align:left; }}
      .stats {{ grid-template-columns:1fr 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <div class="hero-top">
        <div>
          <h1>{escape(plan["hero"]["title"])}</h1>
          <p>{escape(plan["hero"]["subtitle"])}</p>
          <div class="meta-row">
            <span class="badge soft">账号快照 {escape(plan["hero"]["account_id"])}</span>
            <span class="badge">当前在线版本 {escape(plan["hero"]["online_version"])}</span>
            <span class="badge">输入层级 {escape(plan["hero"]["input_tier"])}</span>
            <span class="badge">生成时间 {escape(plan["hero"]["generated_at"])}</span>
          </div>
        </div>
        <div class="badge-row">
          <span class="badge accent">{escape(plan["hero"]["confidence_label"])}</span>
        </div>
      </div>
      <p>{escape(plan["hero"]["confidence_note"])}</p>
      <div class="nav-row">
        <a class="badge" href="#overview">总览</a>
        <a class="badge" href="#teams">队伍优先级</a>
        <a class="badge" href="#characters">角色详情</a>
        <a class="badge" href="#sources">依据来源</a>
      </div>
      <div class="hero-quick">{quick_cards}</div>
      <div class="stats">{fact_cards}</div>
    </section>

      <main class="main">
        <section class="panel" id="overview">
          <div class="section-title">
            <h2>角色优先级总览</h2>
            <p>第一层只回答一件事：下面先练谁</p>
          </div>
          <div class="priority-board">{priority_board}</div>
          <div class="summary-grid">
            <article class="summary-card">
              <h3>当前核心目标</h3>
              <p><strong>主目标：</strong>{escape(plan["summary"]["main_goal"])}</p>
              <p><strong>当前最强一队：</strong>{escape(plan["summary"]["now_team"])}</p>
              <p><strong>第二队方向：</strong>{escape(plan["summary"]["next_team"])}</p>
            </article>
            <article class="summary-card">
              <h3>当前最需要注意</h3>
              <p><strong>最大瓶颈：</strong>{escape(plan["summary"]["biggest_blocker"])}</p>
              <p><strong>当前别做：</strong>{escape(plan["summary"]["do_not_do"])}</p>
            </article>
          </div>
        </section>

        <section class="panel" id="characters">
          <div class="section-title">
            <h2>逐角色执行卡</h2>
            <p>第二层是培养项目顺序，第三层展开技能、武器和声骸细节</p>
          </div>
          <div class="filter-bar">
            <input id="searchInput" placeholder="搜索角色名" />
            <select id="teamSelect">
              <option value="">全部队伍</option>
              <option value="霜渐队">霜渐队</option>
              <option value="光噪队">光噪队</option>
            </select>
            <span class="muted" id="resultCount">当前展示 0 个角色</span>
          </div>
          <div class="character-grid" id="characterGrid">
            {render_character_cards(plan["characters"], source_index)}
          </div>
        </section>

        <section class="panel" id="teams">
          <div class="section-title">
            <h2>补充说明</h2>
            <p>这些内容放后面，供你理解为什么这样排</p>
          </div>
          <div class="team-grid">
            {render_team_cards(plan["team_priority"])}
          </div>
          <div class="rule-grid" style="margin-top:14px;">
            {''.join(growth_sections)}
          </div>
          <div class="timeline-grid" style="margin-top:14px;">
            {''.join(timeline_sections)}
          </div>
          <article class="summary-card" style="margin-top:14px;">
            <h3>暂缓项</h3>
            <ul>{delayed}</ul>
          </article>
          <article class="summary-card" style="margin-top:14px;">
            <h3>执行原则</h3>
            <ul>{top_bullets}</ul>
          </article>
        </section>

        <section class="panel" id="sources">
          <div class="section-title">
            <h2>依据来源</h2>
            <p>把版本基线、队伍共识和技能顺序来源留在页内，后续方便复核和迭代</p>
          </div>
          <div class="source-grid">
            {render_source_list(plan["sources"])}
          </div>
        </section>
      </main>
  </div>

  <script>
    const PAYLOAD = {data_json};
    const searchInput = document.getElementById("searchInput");
    const teamSelect = document.getElementById("teamSelect");
    const resultCount = document.getElementById("resultCount");
    const cards = Array.from(document.querySelectorAll(".character-card"));

    function applyFilters() {{
      const keyword = (searchInput.value || "").trim().toLowerCase();
      const team = teamSelect.value;
      let visible = 0;
      for (const card of cards) {{
        const name = (card.dataset.name || "").toLowerCase();
        const teamName = card.dataset.team || "";
        const matched = (!keyword || name.includes(keyword)) && (!team || teamName === team);
        card.style.display = matched ? "" : "none";
        if (matched) visible += 1;
      }}
      resultCount.textContent = `当前展示 ${{visible}} 个角色`;
      document.getElementById("characterGrid").dataset.count = String(visible);
    }}

    searchInput.addEventListener("input", applyFilters);
    teamSelect.addEventListener("change", applyFilters);
    document.addEventListener("click", (event) => {{
      const btn = event.target.closest(".tab-btn");
      if (!btn) return;
      const group = btn.closest(".tab-group");
      if (!group) return;
      const target = btn.dataset.tab;
      for (const item of group.querySelectorAll(".tab-btn")) {{
        item.classList.toggle("active", item === btn);
      }}
      for (const pane of group.querySelectorAll(".tab-pane")) {{
        pane.classList.toggle("active", pane.dataset.pane === target);
      }}
    }});
    applyFilters();
  </script>
</body>
</html>
"""


def main() -> None:
    args = parse_args()
    row = find_row(args.product_id, args.platform)
    plan = build_plan(row)
    output_path = Path(args.output).resolve()
    output_path.write_text(build_html(plan), encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
