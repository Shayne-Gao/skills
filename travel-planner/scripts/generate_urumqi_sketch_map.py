import json
import math
from pathlib import Path


URUMQI = {"lat": 43.8256, "lon": 87.6168}


def amap_link(query: str) -> str:
    return f"https://ditu.amap.com/search?query={query.replace(' ', '+')}"


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
    r = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return int(round(2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))))


def project(lon: float, lat: float, bounds: dict[str, float]) -> tuple[float, float]:
    width, height = 1000.0, 760.0
    pad_x, pad_y = 120.0, 90.0
    x = pad_x + (lon - bounds["min_lon"]) / (bounds["max_lon"] - bounds["min_lon"]) * (width - pad_x * 2)
    y = height - (
        pad_y + (lat - bounds["min_lat"]) / (bounds["max_lat"] - bounds["min_lat"]) * (height - pad_y * 2)
    )
    return round(x, 2), round(y, 2)


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    outputs_dir = base_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    output_path = outputs_dir / "Trip_Sketch_Map_Urumqi_Xinjiang.html"

    groups = [
        {"id": "city", "name": "乌市 1-2 天", "color": "#355c7d"},
        {"id": "nearby", "name": "天池/南山/达坂城", "color": "#6c8b5d"},
        {"id": "turpan", "name": "吐鲁番方向", "color": "#c46f2d"},
        {"id": "yili", "name": "伊犁环线", "color": "#2f7e79"},
        {"id": "north", "name": "北疆深度", "color": "#695a98"},
        {"id": "s101", "name": "S101 / 公路地貌", "color": "#9a4d62"},
    ]

    spots = [
        {
            "id": "urumqi",
            "name": "乌鲁木齐（枢纽）",
            "shortLabel": "乌鲁木齐",
            "group": "city",
            "kind": "城市枢纽",
            "query": "乌鲁木齐",
            "lat": 43.8256,
            "lon": 87.6168,
            "driveHoursHint": "0h",
            "objective": "本次 7 天游的出发与回程枢纽，适合安排到达缓冲、补给与返程前收尾。",
            "subjective": "你说得对，乌市本身不该放太多点。建议只留 1-2 天，重点放在周边大方向。",
            "importance": "core",
        },
        {
            "id": "museum",
            "name": "新疆维吾尔自治区博物馆",
            "shortLabel": "博物馆",
            "group": "city",
            "kind": "室内人文",
            "query": "新疆维吾尔自治区博物馆 乌鲁木齐",
            "lat": 43.8427,
            "lon": 87.5934,
            "driveHoursHint": "市内",
            "objective": "最适合乌市 1 天游中的室内主点，适合老人小孩慢节奏参观。",
            "subjective": "若只保留一个乌市文化点，优先它。",
            "importance": "core",
        },
        {
            "id": "bazaar",
            "name": "新疆国际大巴扎",
            "shortLabel": "大巴扎",
            "group": "city",
            "kind": "夜间逛吃",
            "query": "新疆国际大巴扎 乌鲁木齐",
            "lat": 43.7789,
            "lon": 87.6086,
            "driveHoursHint": "市内",
            "objective": "更适合作为傍晚/夜间轻松收尾，体验氛围、吃饭、买伴手礼。",
            "subjective": "不建议白天长时间暴晒逛，晚上去更合适。",
            "importance": "core",
        },
        {
            "id": "tianchi",
            "name": "天山天池",
            "shortLabel": "天山天池",
            "group": "nearby",
            "kind": "高山湖泊",
            "query": "天山天池 阜康 新疆",
            "lat": 43.886028,
            "lon": 88.132389,
            "driveHoursHint": "约 1.5-2h",
            "objective": "乌鲁木齐周边最稳的自然代表点，适合多代同行做 1 天游。",
            "subjective": "如果只选一个近郊自然点，优先天池。",
            "importance": "core",
        },
        {
            "id": "nanshan",
            "name": "南山风景区",
            "shortLabel": "南山",
            "group": "nearby",
            "kind": "避暑草原",
            "query": "乌鲁木齐 南山 风景区",
            "lat": 43.487,
            "lon": 87.208,
            "driveHoursHint": "约 1.5h",
            "objective": "更偏放松、避暑、短走，适合安排在老人孩子需要缓冲的那天。",
            "subjective": "它不是“必须打卡”，但作为节奏调剂非常好用。",
            "importance": "core",
        },
        {
            "id": "grand-canyon",
            "name": "天山大峡谷",
            "shortLabel": "天山大峡谷",
            "group": "nearby",
            "kind": "峡谷地貌",
            "query": "乌鲁木齐 天山大峡谷",
            "lat": 43.431128,
            "lon": 87.3737683,
            "driveHoursHint": "约 2h",
            "objective": "峡谷景观比南山更强烈，但步行和台阶压力更大。",
            "subjective": "适合全员状态不错时替代南山，不适合作为高温天轻松点。",
            "importance": "optional",
        },
        {
            "id": "salt-lake",
            "name": "新疆盐湖景区",
            "shortLabel": "盐湖",
            "group": "nearby",
            "kind": "拍照短停",
            "query": "新疆盐湖景区 达坂城",
            "lat": 43.39111,
            "lon": 88.10750,
            "driveHoursHint": "约 1.5h",
            "objective": "适合做轻量出片点，短停观景即可。",
            "subjective": "更像“加点”，不建议撑成全天。",
            "importance": "optional",
        },
        {
            "id": "jiaohe",
            "name": "交河故城",
            "shortLabel": "交河",
            "group": "turpan",
            "kind": "遗址人文",
            "query": "交河故城 吐鲁番",
            "lat": 42.95460079,
            "lon": 89.06543255,
            "driveHoursHint": "约 2.5-3h",
            "objective": "吐鲁番方向最有代表性的古城遗址之一。",
            "subjective": "8 月很热，建议清晨或傍晚去，不要正午硬逛。",
            "importance": "core",
        },
        {
            "id": "karez",
            "name": "坎儿井",
            "shortLabel": "坎儿井",
            "group": "turpan",
            "kind": "室内/半室内",
            "query": "吐鲁番 坎儿井",
            "lat": 42.944,
            "lon": 89.189,
            "driveHoursHint": "约 2.5-3h",
            "objective": "更适合作为吐鲁番一日中的降温缓冲点。",
            "subjective": "对老人小孩友好，和交河搭配比火焰山更实用。",
            "importance": "core",
        },
        {
            "id": "grape-valley",
            "name": "葡萄沟",
            "shortLabel": "葡萄沟",
            "group": "turpan",
            "kind": "休闲绿荫",
            "query": "葡萄沟 吐鲁番",
            "lat": 42.995,
            "lon": 89.173,
            "driveHoursHint": "约 2.5-3h",
            "objective": "吐鲁番方向里体感最舒服的一个板块，适合休闲慢逛。",
            "subjective": "适合作为带老人孩子的一日终点。",
            "importance": "core",
        },
        {
            "id": "flame-mountain",
            "name": "火焰山",
            "shortLabel": "火焰山",
            "group": "turpan",
            "kind": "地貌打卡",
            "query": "火焰山 吐鲁番",
            "lat": 42.933,
            "lon": 89.502,
            "driveHoursHint": "约 3-3.5h",
            "objective": "强记忆点的短停地貌打卡。",
            "subjective": "更像顺路停 30-60 分钟，不适合作为主景点。",
            "importance": "optional",
        },
        {
            "id": "sailimu",
            "name": "赛里木湖",
            "shortLabel": "赛里木湖",
            "group": "yili",
            "kind": "高山湖泊",
            "query": "赛里木湖 博尔塔拉 博乐",
            "lat": 44.601438,
            "lon": 81.392346,
            "driveHoursHint": "同事实测约 6h / 568km",
            "objective": "伊犁环线的开场大景点，适合当天只安排一个主点。",
            "subjective": "同事实测里是从乌鲁木齐直接拉到赛里木湖开局。",
            "importance": "core",
        },
        {
            "id": "guozigou",
            "name": "果子沟大桥",
            "shortLabel": "果子沟",
            "group": "yili",
            "kind": "观景短停",
            "query": "果子沟大桥",
            "lat": 44.299,
            "lon": 81.819,
            "driveHoursHint": "赛湖后顺路",
            "objective": "伊犁方向的经典顺路观景点。",
            "subjective": "更适合短停拍照，不建议耗太久。",
            "importance": "core",
        },
        {
            "id": "yining",
            "name": "伊宁",
            "shortLabel": "伊宁",
            "group": "yili",
            "kind": "住宿补给",
            "query": "伊宁市 伊犁",
            "lat": 43.9168,
            "lon": 81.3241,
            "driveHoursHint": "赛湖后常住这里",
            "objective": "伊犁环线中的补给与住宿枢纽。",
            "subjective": "适合在这里住下，老人孩子晚上逛吃恢复体力。",
            "importance": "core",
        },
        {
            "id": "kalajun",
            "name": "喀拉峻草原",
            "shortLabel": "喀拉峻",
            "group": "yili",
            "kind": "草原主景区",
            "query": "喀拉峻草原",
            "lat": 43.142,
            "lon": 82.864,
            "driveHoursHint": "伊宁后再进草原",
            "objective": "伊犁方向最常见的草原主景区之一。",
            "subjective": "多代同行建议控制在观景为主，不追求大徒步。",
            "importance": "core",
        },
        {
            "id": "nalati",
            "name": "那拉提草原",
            "shortLabel": "那拉提",
            "group": "yili",
            "kind": "草原主景区",
            "query": "那拉提草原 空中草原",
            "lat": 43.29,
            "lon": 84.22,
            "driveHoursHint": "常与喀拉峻二选一或连排",
            "objective": "伊犁 7 天游里最容易被选中的草原代表点。",
            "subjective": "如果怕折腾，通常会在喀拉峻和那拉提中做取舍。",
            "importance": "core",
        },
        {
            "id": "duku",
            "name": "独库公路北段",
            "shortLabel": "独库",
            "group": "yili",
            "kind": "风景公路",
            "query": "独库公路 北段 独山子 那拉提",
            "lat": 44.32971,
            "lon": 84.88278,
            "driveHoursHint": "看路况决定是否走",
            "objective": "常作为伊犁返程升级项，需要看通行与天气。",
            "subjective": "带老人孩子时，只有路况好、天气稳才建议走。",
            "importance": "optional",
        },
        {
            "id": "burqin",
            "name": "布尔津",
            "shortLabel": "布尔津",
            "group": "north",
            "kind": "中转补给",
            "query": "布尔津县",
            "lat": 47.702,
            "lon": 86.863,
            "driveHoursHint": "北疆长途首晚常住点",
            "objective": "喀纳斯/禾木板块的常见中转地。",
            "subjective": "北疆深度通常第一天先赶到布尔津，不会把景点塞太满。",
            "importance": "core",
        },
        {
            "id": "wucaitan",
            "name": "五彩滩",
            "shortLabel": "五彩滩",
            "group": "north",
            "kind": "地貌观景",
            "query": "布尔津 五彩滩",
            "lat": 47.918,
            "lon": 86.721,
            "driveHoursHint": "布尔津附近短停",
            "objective": "适合当作长途日的傍晚主点。",
            "subjective": "短停回报高，很适合老人小孩。",
            "importance": "core",
        },
        {
            "id": "kanas",
            "name": "喀纳斯",
            "shortLabel": "喀纳斯",
            "group": "north",
            "kind": "湖泊森林",
            "query": "喀纳斯景区",
            "lat": 48.82139,
            "lon": 87.04722,
            "driveHoursHint": "通常要单独留一天",
            "objective": "北疆深度板块的核心景点。",
            "subjective": "7 天游如果选喀纳斯，基本就不要再硬塞伊犁和吐鲁番。",
            "importance": "core",
        },
        {
            "id": "hemu",
            "name": "禾木",
            "shortLabel": "禾木",
            "group": "north",
            "kind": "村落风光",
            "query": "禾木村",
            "lat": 48.56757,
            "lon": 87.42921,
            "driveHoursHint": "喀纳斯连排",
            "objective": "适合住一晚慢慢看，不适合匆忙打卡。",
            "subjective": "更强调氛围与停留，不是只打一张卡就走。",
            "importance": "core",
        },
        {
            "id": "ghost-city",
            "name": "乌尔禾魔鬼城",
            "shortLabel": "魔鬼城",
            "group": "north",
            "kind": "雅丹地貌",
            "query": "乌尔禾 世界魔鬼城",
            "lat": 46.089,
            "lon": 85.747,
            "driveHoursHint": "常作为回程衔接点",
            "objective": "适合做北疆回程地貌加点。",
            "subjective": "如果返程已经很累，可以直接放弃这一站。",
            "importance": "optional",
        },
        {
            "id": "s101-main",
            "name": "S101 国防公路",
            "shortLabel": "S101",
            "group": "s101",
            "kind": "风景公路",
            "query": "S101 国防公路 乌鲁木齐",
            "lat": 43.4,
            "lon": 87.26,
            "driveHoursHint": "可做 1 天游",
            "objective": "最适合用“选一段”的方式玩，重点是地貌与路上风景。",
            "subjective": "它不是单一景点，应该理解成一条玩法路线。",
            "importance": "core",
        },
        {
            "id": "liujiaowan",
            "name": "鹿角湾",
            "shortLabel": "鹿角湾",
            "group": "s101",
            "kind": "草原松林",
            "query": "鹿角湾 S101",
            "lat": 43.9799,
            "lon": 85.15805,
            "driveHoursHint": "半天-一天",
            "objective": "S101 方向里偏草原避暑的一类玩法。",
            "subjective": "更适合你们想放松时，不是必须和七彩丹霞绑死。",
            "importance": "optional",
        },
        {
            "id": "qicai",
            "name": "硫磺沟七彩山",
            "shortLabel": "七彩丹霞",
            "group": "s101",
            "kind": "丹霞地貌",
            "query": "硫磺沟 七彩山 S101",
            "lat": 43.74434,
            "lon": 87.21784,
            "driveHoursHint": "适合短停高回报",
            "objective": "S101 路线上最直观的“看地貌”选择。",
            "subjective": "适合老人孩子短停拍照，不必走很多路。",
            "importance": "core",
        },
        {
            "id": "kensiwate",
            "name": "肯斯瓦特水库",
            "shortLabel": "肯斯瓦特",
            "group": "s101",
            "kind": "湖库观景",
            "query": "肯斯瓦特水库 S101",
            "lat": 43.966667,
            "lon": 87.95,
            "driveHoursHint": "顺路观景",
            "objective": "适合和 S101 连起来看，偏观景与拍照。",
            "subjective": "风大时体感一般，适合机动处理。",
            "importance": "optional",
        },
    ]

    for spot in spots:
        spot["mapLink"] = amap_link(spot["query"])
        spot["distanceFromUrumqiKm"] = haversine_km(URUMQI["lat"], URUMQI["lon"], spot["lat"], spot["lon"])

    bounds = {
        "min_lat": min(s["lat"] for s in spots) - 0.5,
        "max_lat": max(s["lat"] for s in spots) + 0.4,
        "min_lon": min(s["lon"] for s in spots) - 0.5,
        "max_lon": max(s["lon"] for s in spots) + 0.5,
    }

    for spot in spots:
        x, y = project(spot["lon"], spot["lat"], bounds)
        spot["x"] = x
        spot["y"] = y

    routes = [
        {
            "id": "route-yili",
            "name": "线路范式 A｜伊犁经典环线",
            "summary": "同事实测常见骨架：乌鲁木齐 → 赛里木湖 → 果子沟 → 伊宁 → 喀拉峻/那拉提 → 视路况返程。",
            "color": "#2f7e79",
            "steps": [
                {"day": "D1", "title": "乌鲁木齐缓冲", "spots": ["urumqi"], "note": "博物馆或大巴扎二选一"},
                {"day": "D2", "title": "拉到赛里木湖", "spots": ["sailimu"], "note": "同事实测约 6h / 568km"},
                {"day": "D3", "title": "果子沟 + 伊宁", "spots": ["guozigou", "yining"], "note": "晚上适合住伊宁补给"},
                {"day": "D4", "title": "喀拉峻", "spots": ["kalajun"], "note": "以观景为主"},
                {"day": "D5", "title": "那拉提", "spots": ["nalati"], "note": "看体力决定是否和喀拉峻都去"},
                {"day": "D6", "title": "返程", "spots": ["duku", "urumqi"], "note": "独库北段仅在路况稳时考虑"},
            ],
        },
        {
            "id": "route-north",
            "name": "线路范式 B｜北疆深度",
            "summary": "同事实测常见骨架：乌鲁木齐 → 布尔津 → 五彩滩 → 喀纳斯 → 禾木 →（可选）魔鬼城 → 回乌鲁木齐。",
            "color": "#695a98",
            "steps": [
                {"day": "D1", "title": "乌鲁木齐缓冲", "spots": ["urumqi"], "note": "控制节奏"},
                {"day": "D2", "title": "长途到布尔津", "spots": ["burqin"], "note": "第一天通常以赶路为主"},
                {"day": "D3", "title": "五彩滩 + 喀纳斯", "spots": ["wucaitan", "kanas"], "note": "景区段需要留整块时间"},
                {"day": "D4", "title": "禾木住一晚", "spots": ["hemu"], "note": "更适合慢节奏停留"},
                {"day": "D5", "title": "魔鬼城机动", "spots": ["ghost-city"], "note": "累了可直接放弃"},
                {"day": "D6", "title": "回乌鲁木齐", "spots": ["urumqi"], "note": "返程长途日"},
            ],
        },
        {
            "id": "route-easy",
            "name": "线路范式 C｜轻松带老人小孩",
            "summary": "不追最远封面图，优先天池/南山/吐鲁番与 1 天游公路景观，减少连续赶路。",
            "color": "#c46f2d",
            "steps": [
                {"day": "D1", "title": "乌鲁木齐", "spots": ["museum", "bazaar"], "note": "市内只放 1-2 个点"},
                {"day": "D2", "title": "天山天池", "spots": ["tianchi"], "note": "近郊优先级最高"},
                {"day": "D3", "title": "南山 / 大峡谷二选一", "spots": ["nanshan", "grand-canyon"], "note": "看体力和天气"},
                {"day": "D4", "title": "吐鲁番", "spots": ["jiaohe", "karez", "grape-valley"], "note": "避开正午暴晒"},
                {"day": "D5", "title": "S101 选一段", "spots": ["s101-main", "qicai"], "note": "短停高回报"},
                {"day": "D6", "title": "机动/补给", "spots": ["salt-lake", "urumqi"], "note": "体力差就留在乌市"},
            ],
        },
    ]

    route_segments = []
    spot_index = {spot["id"]: spot for spot in spots}
    for route in routes:
        route_spot_ids = []
        for step in route["steps"]:
            for sid in step["spots"]:
                if sid not in route_spot_ids:
                    route_spot_ids.append(sid)
        route["spotIds"] = route_spot_ids
        for a, b in zip(route_spot_ids, route_spot_ids[1:]):
            sa = spot_index[a]
            sb = spot_index[b]
            route_segments.append(
                {
                    "routeId": route["id"],
                    "from": a,
                    "to": b,
                    "distanceKm": haversine_km(sa["lat"], sa["lon"], sb["lat"], sb["lon"]),
                }
            )

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>新疆周边手绘互动关系图｜乌鲁木齐做枢纽</title>
  <style>
    :root {{
      --paper: #f6f0df;
      --paper-deep: #eadfc8;
      --ink: #2e2a26;
      --muted: #6a6258;
      --blue: #355c7d;
      --green: #6c8b5d;
      --orange: #c46f2d;
      --teal: #2f7e79;
      --purple: #695a98;
      --rose: #9a4d62;
      --shadow: 0 18px 40px rgba(69, 50, 25, 0.16);
      --border: rgba(67, 54, 34, 0.18);
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; background:
      radial-gradient(circle at top left, rgba(255,255,255,.55), transparent 28%),
      repeating-linear-gradient(0deg, rgba(100,80,55,.03), rgba(100,80,55,.03) 1px, transparent 1px, transparent 24px),
      linear-gradient(180deg, var(--paper), #efe4cf 78%);
      color: var(--ink);
      font-family: "Songti SC", "Noto Serif SC", "Source Han Serif SC", serif;
    }}
    body::before {{
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background:
        radial-gradient(circle at 10% 10%, rgba(255,255,255,.32), transparent 22%),
        radial-gradient(circle at 90% 20%, rgba(255,255,255,.16), transparent 18%),
        radial-gradient(circle at 20% 85%, rgba(92,70,42,.08), transparent 20%);
      mix-blend-mode: multiply;
      opacity: .8;
    }}
    .app {{
      max-width: 1480px;
      margin: 0 auto;
      padding: 24px;
      display: grid;
      grid-template-columns: 420px minmax(0, 1fr);
      gap: 20px;
      min-height: 100vh;
    }}
    .panel {{
      background: linear-gradient(180deg, rgba(255,255,255,.48), rgba(255,255,255,.18));
      border: 2px solid var(--border);
      border-radius: 28px;
      box-shadow: var(--shadow);
      position: relative;
      overflow: hidden;
    }}
    .panel::before {{
      content: "";
      position: absolute;
      inset: 10px;
      border: 1px dashed rgba(76,57,36,.18);
      border-radius: 22px;
      pointer-events: none;
    }}
    .sidebar {{
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}
    .eyebrow {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 12px;
      border-radius: 999px;
      border: 1px solid rgba(67,54,34,.18);
      background: rgba(255,255,255,.55);
      color: var(--muted);
      font-size: 12px;
      letter-spacing: .08em;
      text-transform: uppercase;
    }}
    h1 {{
      margin: 0;
      font-size: 38px;
      line-height: 1.05;
      font-family: "Kaiti SC", "STKaiti", "KaiTi", serif;
      letter-spacing: .04em;
    }}
    .subtitle {{
      margin: 0;
      color: var(--muted);
      line-height: 1.7;
      font-size: 14px;
    }}
    .toolbar, .chip-row, .route-list, .spot-list {{ display: flex; flex-wrap: wrap; gap: 10px; }}
    .toolbar button, .chip, .route-card, .spot-card {{
      border: 1px solid rgba(67,54,34,.16);
      background: rgba(255,255,255,.55);
      color: var(--ink);
    }}
    .toolbar {{
      gap: 8px;
    }}
    .toolbar button {{
      cursor: pointer;
      border-radius: 14px;
      padding: 10px 12px;
      font-size: 13px;
      box-shadow: 0 8px 16px rgba(80,62,40,.08);
    }}
    .toolbar button:hover {{ transform: translateY(-1px) rotate(-.4deg); }}
    .copy-path {{
      font-size: 12px;
      color: var(--muted);
      line-height: 1.6;
      word-break: break-all;
    }}
    .chip {{
      appearance: none;
      border-radius: 999px;
      padding: 9px 12px;
      cursor: pointer;
      font-size: 13px;
      transform: rotate(var(--r, -1deg));
      transition: .2s ease;
      user-select: none;
    }}
    .chip.active {{
      background: #fff;
      box-shadow: 0 10px 20px rgba(80,62,40,.12);
      border-color: rgba(67,54,34,.24);
      transform: translateY(-1px) rotate(0deg);
    }}
    .section-title {{
      margin: 8px 0 0;
      font-size: 18px;
      font-family: "Kaiti SC", "STKaiti", "KaiTi", serif;
      letter-spacing: .04em;
    }}
    .route-list {{
      display: grid;
      grid-template-columns: 1fr;
    }}
    .route-card {{
      appearance: none;
      width: 100%;
      text-align: left;
      border-radius: 22px;
      padding: 16px;
      cursor: pointer;
      transition: .22s ease;
      position: relative;
    }}
    .route-card.active {{
      transform: translateX(4px) rotate(-.4deg);
      box-shadow: 0 16px 28px rgba(60,45,28,.14);
      background: rgba(255,255,255,.86);
    }}
    .route-card h3 {{
      margin: 0 0 8px;
      font-size: 18px;
      font-family: "Kaiti SC", "STKaiti", "KaiTi", serif;
    }}
    .route-card p {{
      margin: 0 0 10px;
      color: var(--muted);
      line-height: 1.65;
      font-size: 13px;
    }}
    .route-days {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      color: var(--muted);
      font-size: 12px;
    }}
    .spot-list {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 10px;
      max-height: 42vh;
      overflow: auto;
      padding-right: 4px;
    }}
    .spot-card {{
      appearance: none;
      width: 100%;
      text-align: left;
      padding: 14px 14px 12px;
      border-radius: 18px;
      cursor: pointer;
      transition: .2s ease;
      position: relative;
    }}
    .spot-card:hover {{ transform: translateX(3px); }}
    .spot-card.active {{
      background: rgba(255,255,255,.9);
      box-shadow: 0 12px 24px rgba(75,58,38,.14);
      transform: translateX(6px) rotate(-.35deg);
    }}
    .spot-card .meta {{
      display: flex;
      justify-content: space-between;
      gap: 8px;
      color: var(--muted);
      font-size: 12px;
      margin-top: 6px;
    }}
    .spot-card .kind {{
      display: inline-block;
      padding: 3px 8px;
      border-radius: 999px;
      background: rgba(63,84,110,.08);
      font-size: 11px;
      color: var(--muted);
    }}
    .spot-name {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 16px;
      font-weight: 600;
    }}
    .importance {{
      width: 8px;
      height: 8px;
      border-radius: 999px;
      background: currentColor;
      opacity: .7;
    }}
    .main {{
      padding: 20px;
      display: grid;
      grid-template-rows: auto minmax(0, 1fr) auto;
      gap: 16px;
      min-height: calc(100vh - 48px);
    }}
    .stage-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 16px;
      padding: 6px 6px 0 6px;
    }}
    .stage-title {{
      margin: 0;
      font-size: 26px;
      font-family: "Kaiti SC", "STKaiti", "KaiTi", serif;
    }}
    .stage-note {{
      max-width: 480px;
      color: var(--muted);
      line-height: 1.6;
      font-size: 13px;
    }}
    .map-shell {{
      position: relative;
      border-radius: 30px;
      overflow: hidden;
      background:
        linear-gradient(180deg, rgba(255,255,255,.56), rgba(247,239,219,.84)),
        repeating-linear-gradient(90deg, rgba(80,60,38,.035), rgba(80,60,38,.035) 1px, transparent 1px, transparent 48px),
        repeating-linear-gradient(0deg, rgba(80,60,38,.035), rgba(80,60,38,.035) 1px, transparent 1px, transparent 48px);
      min-height: 700px;
      border: 2px solid rgba(67,54,34,.14);
    }}
    svg {{
      width: 100%;
      height: 100%;
      display: block;
    }}
    .map-viewport {{
      transition: transform .7s cubic-bezier(.2,.75,.2,1);
    }}
    .bg-outline {{
      fill: rgba(216, 197, 160, .28);
      stroke: rgba(101, 76, 47, .35);
      stroke-width: 4;
      stroke-linecap: round;
      stroke-linejoin: round;
      stroke-dasharray: 12 8;
      filter: url(#paperRough);
    }}
    .zone-note {{
      font-size: 18px;
      font-family: "Kaiti SC", "STKaiti", "KaiTi", serif;
      fill: rgba(80,61,39,.66);
    }}
    .zone-sub {{
      font-size: 12px;
      fill: rgba(86,69,48,.56);
    }}
    .radial-line, .route-line {{
      fill: none;
      stroke-linecap: round;
      stroke-linejoin: round;
    }}
    .radial-line {{
      stroke: rgba(80,61,39,.18);
      stroke-width: 2.2;
      stroke-dasharray: 10 10;
    }}
    .route-line {{
      stroke-width: 4;
      opacity: .16;
      transition: opacity .25s ease, stroke-width .25s ease;
    }}
    .route-line.active {{
      opacity: .84;
      stroke-width: 6;
      filter: drop-shadow(0 4px 6px rgba(52,37,24,.14));
    }}
    .spot-node {{
      cursor: pointer;
      transition: transform .2s ease, opacity .2s ease;
    }}
    .spot-node circle {{
      stroke: rgba(62,48,30,.45);
      stroke-width: 2.5;
      filter: url(#paperRough);
    }}
    .spot-node text {{
      font-family: "Kaiti SC", "STKaiti", "KaiTi", serif;
      fill: var(--ink);
      font-size: 16px;
      font-weight: 700;
      paint-order: stroke;
      stroke: rgba(246,240,223,.9);
      stroke-width: 6px;
      stroke-linejoin: round;
    }}
    .spot-node.dimmed {{ opacity: .22; }}
    .spot-node.selected {{ transform: scale(1.04); }}
    .spot-node.selected circle {{
      stroke-width: 4;
      filter: drop-shadow(0 8px 16px rgba(53,92,125,.24));
    }}
    .distance-tag {{
      fill: rgba(255,255,255,.92);
      stroke: rgba(67,54,34,.16);
      stroke-width: 1.5;
      rx: 14;
      ry: 14;
    }}
    .distance-text {{
      font-size: 12px;
      fill: rgba(61,47,31,.75);
    }}
    .details {{
      display: grid;
      grid-template-columns: 1.1fr .9fr;
      gap: 14px;
    }}
    .note-card {{
      border-radius: 22px;
      padding: 16px 18px;
      background: rgba(255,255,255,.68);
      border: 1px solid rgba(67,54,34,.14);
      min-height: 180px;
      box-shadow: 0 10px 18px rgba(68,48,26,.08);
    }}
    .note-card h3 {{
      margin: 0 0 8px;
      font-size: 22px;
      font-family: "Kaiti SC", "STKaiti", "KaiTi", serif;
    }}
    .detail-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 12px;
    }}
    .pill {{
      padding: 5px 10px;
      border-radius: 999px;
      background: rgba(53,92,125,.08);
      color: var(--muted);
      font-size: 12px;
      border: 1px solid rgba(67,54,34,.12);
    }}
    .detail-text {{
      margin: 0;
      color: var(--muted);
      line-height: 1.7;
      font-size: 14px;
    }}
    .detail-actions {{
      margin-top: 14px;
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .detail-actions a {{
      text-decoration: none;
      color: var(--ink);
      border-radius: 14px;
      padding: 10px 12px;
      background: rgba(255,255,255,.74);
      border: 1px solid rgba(67,54,34,.16);
      font-size: 13px;
    }}
    .legend {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px 12px;
    }}
    .legend-item {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      color: var(--muted);
      font-size: 12px;
    }}
    .legend-swatch {{
      width: 16px;
      height: 16px;
      border-radius: 999px;
      border: 1px solid rgba(67,54,34,.16);
    }}
    @media (max-width: 1120px) {{
      .app {{
        grid-template-columns: 1fr;
      }}
      .main {{
        min-height: auto;
      }}
      .map-shell {{
        min-height: 580px;
      }}
      .details {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="app">
    <aside class="panel sidebar">
      <span class="eyebrow">新疆周边方向草图</span>
      <h1>乌鲁木齐做枢纽，<br/>这 7 天到底该往哪边跑？</h1>
      <p class="subtitle">这不是精确导航地图，而是帮你先建立“方向感 + 大致距离 + 常见走法”的互动手账图。左边点景点，右边会自动定位、放大，并把与乌鲁木齐及线路的关系画出来。</p>
      <div class="toolbar">
        <button id="copy-file">复制本地文件路径</button>
        <button id="copy-dir">复制输出目录</button>
        <button id="reset-view">回到总览</button>
      </div>
      <div class="copy-path" id="local-path-box"></div>

      <h2 class="section-title">先选大方向</h2>
      <div class="chip-row" id="group-chips"></div>

      <h2 class="section-title">同事实测常见走法</h2>
      <div class="route-list" id="route-list"></div>

      <h2 class="section-title">重点点位清单</h2>
      <div class="spot-list" id="spot-list"></div>
    </aside>

    <main class="panel main">
      <div class="stage-header">
        <div>
          <h2 class="stage-title">手绘互动关系图</h2>
          <div class="stage-note">默认显示总览。你可以先选“伊犁环线 / 北疆深度 / 轻松版”，再点具体景点。地图会尽量让你一眼看懂：这些点分别在哪个方向、离乌市大概多远、通常怎么串。</div>
        </div>
        <div class="legend" id="legend"></div>
      </div>

      <section class="map-shell">
        <svg viewBox="0 0 1000 760" aria-label="新疆手绘互动地图">
          <defs>
            <filter id="paperRough">
              <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="1" seed="7" result="noise"/>
              <feDisplacementMap in="SourceGraphic" in2="noise" scale="1.8" />
            </filter>
          </defs>
          <g id="mapViewport" class="map-viewport">
            <path class="bg-outline" d="M122 612 Q86 492 146 340 Q190 224 302 154 Q438 76 626 88 Q770 98 874 198 Q938 258 916 354 Q900 430 846 490 Q812 528 740 574 Q608 664 442 666 Q266 668 168 638 Q132 626 122 612Z"></path>
            <g id="zone-labels">
              <text class="zone-note" x="507" y="312">乌鲁木齐</text>
              <text class="zone-sub" x="500" y="332">枢纽 / 补给 / 到达缓冲</text>
              <text class="zone-note" x="705" y="318">吐鲁番</text>
              <text class="zone-sub" x="695" y="338">东南方向 / 高温人文线</text>
              <text class="zone-note" x="212" y="280">伊犁</text>
              <text class="zone-sub" x="180" y="300">西向草原湖泊线</text>
              <text class="zone-note" x="404" y="145">北疆</text>
              <text class="zone-sub" x="362" y="165">喀纳斯 / 禾木 / 布尔津</text>
              <text class="zone-note" x="600" y="520">近郊</text>
              <text class="zone-sub" x="570" y="540">天池 / 南山 / 达坂城</text>
              <text class="zone-note" x="388" y="486">S101</text>
              <text class="zone-sub" x="340" y="506">公路地貌 / 选一段即可</text>
            </g>
            <g id="radial-lines"></g>
            <g id="route-lines"></g>
            <g id="spot-layer"></g>
            <g id="distance-layer"></g>
          </g>
        </svg>
      </section>

      <section class="details">
        <article class="note-card">
          <h3 id="detail-title">先点一个方向或景点</h3>
          <div class="detail-meta" id="detail-meta"></div>
          <p class="detail-text" id="detail-objective">这张图默认先帮你看方向感：7 天游带老人和孩子，通常只建议选 1 个主方向。伊犁、北疆、吐鲁番和近郊，不建议全塞在一个行程里。</p>
          <p class="detail-text" id="detail-subjective" style="margin-top:10px;">左侧选中后，这里会显示该点位/线路的客观说明、主观建议，以及与乌鲁木齐的大致距离关系。</p>
          <div class="detail-actions" id="detail-actions"></div>
        </article>
        <article class="note-card">
          <h3>怎么读这张图</h3>
          <p class="detail-text">1. 先看右侧大致方向：西边是伊犁，北边是喀纳斯/禾木，东南是吐鲁番。</p>
          <p class="detail-text" style="margin-top:10px;">2. 虚线表示“从乌鲁木齐放射出去的大方向”；彩色线表示“同事攻略里常见的线路骨架”。</p>
          <p class="detail-text" style="margin-top:10px;">3. 标注的公里数是帮助你感知远近，不是精确导航；真正导航仍然点高德外跳。</p>
        </article>
      </section>
    </main>
  </div>

  <script>
    const groups = {json.dumps(groups, ensure_ascii=False)};
    const spots = {json.dumps(spots, ensure_ascii=False)};
    const routes = {json.dumps(routes, ensure_ascii=False)};
    const routeSegments = {json.dumps(route_segments, ensure_ascii=False)};
    const outputFile = {json.dumps(str(output_path), ensure_ascii=False)};
    const outputDir = {json.dumps(str(outputs_dir), ensure_ascii=False)};

    const state = {{
      groupId: "all",
      routeId: null,
      spotId: null,
    }};

    const groupMap = Object.fromEntries(groups.map(g => [g.id, g]));
    const spotMap = Object.fromEntries(spots.map(s => [s.id, s]));
    const routeMap = Object.fromEntries(routes.map(r => [r.id, r]));

    const elGroupChips = document.getElementById("group-chips");
    const elRouteList = document.getElementById("route-list");
    const elSpotList = document.getElementById("spot-list");
    const elSpotLayer = document.getElementById("spot-layer");
    const elRouteLines = document.getElementById("route-lines");
    const elRadialLines = document.getElementById("radial-lines");
    const elDistanceLayer = document.getElementById("distance-layer");
    const elMapViewport = document.getElementById("mapViewport");
    const elLegend = document.getElementById("legend");
    const elLocalPathBox = document.getElementById("local-path-box");
    const elTitle = document.getElementById("detail-title");
    const elMeta = document.getElementById("detail-meta");
    const elObjective = document.getElementById("detail-objective");
    const elSubjective = document.getElementById("detail-subjective");
    const elActions = document.getElementById("detail-actions");

    function copyText(text) {{
      navigator.clipboard.writeText(text).catch(() => window.prompt("复制下面这段：", text));
    }}

    document.getElementById("copy-file").addEventListener("click", () => copyText(outputFile));
    document.getElementById("copy-dir").addEventListener("click", () => copyText(outputDir));
    document.getElementById("reset-view").addEventListener("click", () => {{
      state.routeId = null;
      state.spotId = null;
      render();
    }});

    elLocalPathBox.innerHTML = `本地文件：<br>${{outputFile}}<br><br>输出目录：<br>${{outputDir}}`;

    function getVisibleSpots() {{
      return spots.filter(spot => state.groupId === "all" || spot.group === state.groupId);
    }}

    function getSpotColor(spot) {{
      return groupMap[spot.group]?.color || "#355c7d";
    }}

    function pathBetween(a, b) {{
      const midX = (a.x + b.x) / 2 + (b.y - a.y) * 0.05;
      const midY = (a.y + b.y) / 2 - (b.x - a.x) * 0.04;
      return `M ${{a.x}} ${{a.y}} Q ${{midX.toFixed(1)}} ${{midY.toFixed(1)}} ${{b.x}} ${{b.y}}`;
    }}

    function focusTargets(targetSpots) {{
      if (!targetSpots.length) {{
        elMapViewport.style.transform = "translate(0px, 0px) scale(1)";
        return;
      }}
      const xs = targetSpots.map(s => s.x);
      const ys = targetSpots.map(s => s.y);
      const minX = Math.min(...xs);
      const maxX = Math.max(...xs);
      const minY = Math.min(...ys);
      const maxY = Math.max(...ys);
      const boxW = Math.max(160, maxX - minX);
      const boxH = Math.max(140, maxY - minY);
      const scale = Math.max(1, Math.min(1.85, Math.min(560 / boxW, 420 / boxH)));
      const centerX = (minX + maxX) / 2;
      const centerY = (minY + maxY) / 2;
      const tx = (500 - centerX) * scale;
      const ty = (380 - centerY) * scale;
      elMapViewport.style.transform = `translate(${{tx}}px, ${{ty}}px) scale(${{scale}})`;
    }}

    function updateDetails() {{
      if (state.spotId) {{
        const spot = spotMap[state.spotId];
        elTitle.textContent = spot.name;
        elMeta.innerHTML = `
          <span class="pill">${{groupMap[spot.group].name}}</span>
          <span class="pill">${{spot.kind}}</span>
          <span class="pill">距乌市约 ${{spot.distanceFromUrumqiKm}} km</span>
          <span class="pill">${{spot.driveHoursHint}}</span>
        `;
        elObjective.textContent = spot.objective;
        elSubjective.textContent = spot.subjective;
        elActions.innerHTML = `<a href="${{spot.mapLink}}" target="_blank" rel="noopener noreferrer">去高德看这个点</a>`;
        return;
      }}
      if (state.routeId) {{
        const route = routeMap[state.routeId];
        elTitle.textContent = route.name;
        elMeta.innerHTML = `<span class="pill">线路骨架</span><span class="pill">${{route.spotIds.length}} 个核心点</span>`;
        elObjective.textContent = route.summary;
        elSubjective.textContent = route.steps.map(step => `${{step.day}} · ${{step.title}}：${{step.note}}`).join(" ｜ ");
        elActions.innerHTML = "";
        return;
      }}
      elTitle.textContent = "先点一个方向或景点";
      elMeta.innerHTML = `<span class="pill">总览模式</span><span class="pill">建议只选 1 个主方向</span>`;
      elObjective.textContent = "这张图默认先帮你看方向感：7 天游带老人和孩子，通常只建议选 1 个主方向。伊犁、北疆、吐鲁番和近郊，不建议全塞在一个行程里。";
      elSubjective.textContent = "如果你已经有倾向，先点左侧“伊犁经典环线 / 北疆深度 / 轻松版”任一线路范式，右边会自动把对应关系高亮出来。";
      elActions.innerHTML = "";
    }}

    function renderLegend() {{
      elLegend.innerHTML = groups.map(group => `
        <span class="legend-item">
          <span class="legend-swatch" style="background:${{group.color}}22;border-color:${{group.color}}66"></span>
          ${{group.name}}
        </span>
      `).join("");
    }}

    function renderChips() {{
      const allChip = {{
        id: "all",
        name: "全部方向",
        color: "#5f584d"
      }};
      elGroupChips.innerHTML = [allChip, ...groups].map((group, index) => `
        <button
          type="button"
          class="chip ${{state.groupId === group.id ? "active" : ""}}"
          data-group-id="${{group.id}}"
          style="--r:${{(index % 2 === 0 ? -1 : 1) * (index % 3)}}deg; background:${{group.id === "all" ? "rgba(255,255,255,.66)" : group.color + "14"}}"
        >${{group.name}}</button>
      `).join("");
      elGroupChips.querySelectorAll("[data-group-id]").forEach(node => {{
        node.addEventListener("click", () => {{
          state.groupId = node.dataset.groupId;
          state.routeId = null;
          state.spotId = null;
          render();
        }});
      }});
    }}

    function renderRoutes() {{
      elRouteList.innerHTML = routes.map(route => `
        <button type="button" class="route-card ${{state.routeId === route.id ? "active" : ""}}" data-route-id="${{route.id}}" style="border-left: 6px solid ${{route.color}}">
          <h3>${{route.name}}</h3>
          <p>${{route.summary}}</p>
          <div class="route-days">${{route.steps.map(step => `<span>${{step.day}} ${{step.title}}</span>`).join(" · ")}}</div>
        </button>
      `).join("");
      elRouteList.querySelectorAll("[data-route-id]").forEach(node => {{
        node.addEventListener("click", () => {{
          const routeId = node.dataset.routeId;
          state.routeId = state.routeId === routeId ? null : routeId;
          state.spotId = null;
          render();
        }});
      }});
    }}

    function renderSpotList() {{
      const visibleSpots = getVisibleSpots().filter(spot => spot.id !== "urumqi");
      elSpotList.innerHTML = visibleSpots.map(spot => `
        <button type="button" class="spot-card ${{state.spotId === spot.id ? "active" : ""}}" data-spot-id="${{spot.id}}">
          <div class="spot-name" style="color:${{getSpotColor(spot)}}">
            <span class="importance" style="opacity:${{spot.importance === "core" ? ".9" : ".42"}}"></span>
            <span>${{spot.name}}</span>
          </div>
          <div class="meta">
            <span class="kind">${{spot.kind}}</span>
            <span>距乌市约 ${{spot.distanceFromUrumqiKm}} km</span>
          </div>
        </button>
      `).join("");
      elSpotList.querySelectorAll("[data-spot-id]").forEach(node => {{
        node.addEventListener("click", () => {{
          const spotId = node.dataset.spotId;
          state.spotId = state.spotId === spotId ? null : spotId;
          if (state.spotId) state.routeId = null;
          render();
        }});
      }});
    }}

    function renderRadialLines() {{
      const visibleSpots = getVisibleSpots().filter(spot => spot.id !== "urumqi");
      const urumqi = spotMap.urumqi;
      elRadialLines.innerHTML = visibleSpots.map(spot => `
        <path class="radial-line" d="${{pathBetween(urumqi, spot)}}"></path>
      `).join("");
    }}

    function renderRouteLines() {{
      const activeRouteId = state.routeId;
      elRouteLines.innerHTML = routeSegments.map(segment => {{
        const from = spotMap[segment.from];
        const to = spotMap[segment.to];
        const route = routeMap[segment.routeId];
        const active = activeRouteId === segment.routeId;
        return `
          <g>
            <path class="route-line ${{active ? "active" : ""}}" d="${{pathBetween(from, to)}}" stroke="${{route.color}}"></path>
            ${{active ? `
              <rect class="distance-tag" x="${{((from.x + to.x)/2) - 32}}" y="${{((from.y + to.y)/2) - 15}}" width="64" height="24"></rect>
              <text class="distance-text" x="${{(from.x + to.x)/2}}" y="${{((from.y + to.y)/2) + 1}}" text-anchor="middle">${{segment.distanceKm}} km</text>
            ` : ""}}
          </g>
        `;
      }}).join("");
    }}

    function renderSpotLayer() {{
      const visibleIds = new Set(getVisibleSpots().map(spot => spot.id));
      const activeRoute = state.routeId ? routeMap[state.routeId] : null;
      elSpotLayer.innerHTML = spots.map(spot => {{
        const dimmedByGroup = !visibleIds.has(spot.id);
        const dimmedByRoute = activeRoute && !activeRoute.spotIds.includes(spot.id);
        const classes = [
          "spot-node",
          state.spotId === spot.id ? "selected" : "",
          dimmedByGroup || dimmedByRoute ? "dimmed" : ""
        ].filter(Boolean).join(" ");
        const r = spot.id === "urumqi" ? 18 : (spot.importance === "core" ? 14 : 11);
        const color = getSpotColor(spot);
        return `
          <g class="${{classes}}" data-spot-id="${{spot.id}}">
            <circle cx="${{spot.x}}" cy="${{spot.y}}" r="${{r}}" fill="${{color}}22"></circle>
            <circle cx="${{spot.x}}" cy="${{spot.y}}" r="${{r - 4}}" fill="${{color}}"></circle>
            <text x="${{spot.x}}" y="${{spot.y - r - 12}}" text-anchor="middle">${{spot.shortLabel}}</text>
          </g>
        `;
      }}).join("");
      elSpotLayer.querySelectorAll("[data-spot-id]").forEach(node => {{
        node.addEventListener("click", () => {{
          const spotId = node.dataset.spotId;
          state.spotId = spotId;
          state.routeId = null;
          render();
        }});
      }});
    }}

    function renderDistanceLayer() {{
      if (!state.spotId || state.spotId === "urumqi") {{
        elDistanceLayer.innerHTML = "";
        return;
      }}
      const from = spotMap.urumqi;
      const to = spotMap[state.spotId];
      const cx = (from.x + to.x) / 2;
      const cy = (from.y + to.y) / 2 - 22;
      elDistanceLayer.innerHTML = `
        <path class="radial-line" d="${{pathBetween(from, to)}}" style="stroke:${{getSpotColor(to)}}88;stroke-width:3.2"></path>
        <rect class="distance-tag" x="${{cx - 40}}" y="${{cy - 14}}" width="80" height="28"></rect>
        <text class="distance-text" x="${{cx}}" y="${{cy + 4}}" text-anchor="middle">约 ${{to.distanceFromUrumqiKm}} km</text>
      `;
    }}

    function renderFocus() {{
      if (state.spotId) {{
        focusTargets([spotMap[state.spotId]]);
        return;
      }}
      if (state.routeId) {{
        focusTargets(routeMap[state.routeId].spotIds.map(id => spotMap[id]));
        return;
      }}
      focusTargets([]);
    }}

    function render() {{
      renderLegend();
      renderChips();
      renderRoutes();
      renderSpotList();
      renderRadialLines();
      renderRouteLines();
      renderSpotLayer();
      renderDistanceLayer();
      updateDetails();
      renderFocus();
    }}

    render();
  </script>
</body>
</html>
"""

    output_path.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
