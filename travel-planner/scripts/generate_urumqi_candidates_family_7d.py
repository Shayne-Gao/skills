import json
import math
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Optional
from urllib.parse import quote

URUMQI_BASE = {"lat": 43.8256, "lon": 87.6168}


def build_map_link(query: str) -> str:
    q = query.replace(" ", "+")
    return f"https://ditu.amap.com/search?query={q}"


def build_images_link(query: str) -> str:
    return f"https://www.bing.com/images/search?q={quote(query)}"


def spot(name: str, query: Optional[str] = None) -> str:
    q = query or name
    link = build_map_link(q)
    return f"[{name}]({link}) [🗺️]({link})"


def stars_score(stars: str) -> float:
    s = str(stars or "")
    score = float(s.count("★"))
    if "½" in s:
        score += 0.5
    return score


def spot_html(name: str, query: str) -> str:
    link = build_map_link(query)
    return (
        f'<a class="candidate-name" href="#" data-query="{escape(query, quote=True)}" data-name="{escape(name, quote=True)}">{escape(name)}</a> '
        f'<a href="{link}" target="_blank" rel="noopener noreferrer">🗺️</a>'
    )


def marker_label(name: str) -> str:
    s = str(name or "").strip()
    if "天山天池" in s:
        return "天山天池"
    if "天山大峡谷" in s:
        return "天山大峡谷"
    if "S101" in s or "国防公路" in s:
        return "S101"
    if "独库" in s:
        return "独库"
    if "天池" in s and ("栈道" in s or "步道" in s):
        return "天池栈道"
    if "（" in s and "）" in s:
        inner = s.split("（", 1)[1].rsplit("）", 1)[0].strip()
        if inner and len(inner) <= 8 and not any(
            k in inner
            for k in [
                "按",
                "折返",
                "选",
                "可选",
                "备选",
                "顺路",
                "外观",
                "轻量",
                "路过",
            ]
        ):
            return inner
    base = s.split("（", 1)[0].strip() if "（" in s else s
    base = base.replace("乌鲁木齐", "").strip()
    if len(base) > 10:
        return base[:10]
    return base


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
    r = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return int(round(2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))))


def direction_from_urumqi(lat: float, lon: float) -> str:
    dlon = lon - URUMQI_BASE["lon"]
    dlat = lat - URUMQI_BASE["lat"]
    if abs(dlon) < 0.08 and abs(dlat) < 0.08:
        return "乌市附近"
    angle = (math.degrees(math.atan2(dlon, dlat)) + 360) % 360
    dirs = ["北", "东北", "东", "东南", "南", "西南", "西", "西北"]
    idx = int((angle + 22.5) // 45) % 8
    return f"乌市{dirs[idx]}方向"


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    template_path = base_dir / "template_intl.html"
    outputs_dir = base_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    trip_title = "乌鲁木齐及周边 7 日自驾｜四位老人 + 两位大人 + 两位小孩｜第二步：景点备选清单（用于选择）"

    user_profile = {
        "目的地": "中国｜新疆｜乌鲁木齐及周边（自驾）",
        "出行时间": "8 月初（夏季，市区偏热、山区早晚偏凉）",
        "天数": "约 7 天",
        "同行人员": "4 位老人 + 2 位大人 + 2 位小孩（多代同游）",
        "节奏": "偏舒缓：每天 1 个主点 + 1 个轻量备选；午后尽量安排休息/室内",
        "交通": "乌鲁木齐自驾出发；尽量避免连续多天长距离赶路",
        "备注": "多代同行优先考虑：步行强度、台阶/坡度、如厕与补给便利、避开正午暴晒；如出现高反/心肺不适，优先减少海拔爬升与步行。",
    }

    pool = [
        {
            "area": "乌鲁木齐市区｜文化轻松",
            "name": "新疆维吾尔自治区博物馆（博物馆）",
            "query": "新疆维吾尔自治区博物馆 乌鲁木齐",
            "objective": "综合性博物馆类点位，内容以历史、民族文化与文物展陈为主；室内为主，适合避暑与长辈慢节奏参观。",
            "subjective": "非常适合作为“老人友好”的核心点位。建议控制参观重点（选 1-2 个主题即可），中途安排坐着休息与补水；带娃可以用“找展品/打卡点”提升参与度。",
            "stars": "★★★★★",
            "dur": "2-4h",
            "fee": "通常免费/需预约",
            "kind": "博物馆/室内",
        },
        {
            "area": "乌鲁木齐市区｜文化轻松",
            "name": "新疆国际大巴扎（大巴扎）",
            "query": "新疆国际大巴扎 乌鲁木齐",
            "objective": "商业街区/建筑地标与餐饮购物集合区，体验以氛围、夜景、餐饮与伴手礼采购为主。",
            "subjective": "更推荐放在傍晚/晚上，作为“吃+逛”的组合。人流密集时要把孩子和老人照顾放第一；不必长时间久逛，定好目标（吃什么/买什么）更省体力。",
            "stars": "★★★★☆",
            "dur": "1.5-3h",
            "fee": "免费/消费",
            "kind": "夜市/购物",
        },
        {
            "area": "乌鲁木齐市区｜城市烟火（轻松）",
            "name": "领馆巷美食街（领馆巷）",
            "query": "领馆巷 美食街 乌鲁木齐",
            "objective": "餐饮与夜间烟火气点位，适合体验当地小吃与轻松逛吃。",
            "subjective": "更适合傍晚/晚上去，选 2-3 家目标店即可。多代同行建议优先选“好停车/排队可控”的店，避免老人久站。",
            "stars": "★★★★☆",
            "dur": "1-2h",
            "fee": "消费",
            "kind": "美食/夜间",
        },
        {
            "area": "天山天池方向｜经典必去",
            "name": "天山天池（天池）",
            "query": "天山天池 阜康 新疆",
            "lat": 43.886028,
            "lon": 88.132389,
            "objective": "高山湖泊+天山景观的代表性目的地，通常可通过景区交通抵达核心观景区域，步行强度可按需控制。",
            "subjective": "如果只能选一个周边“自然代表点”，它通常是首选。多代同行建议把“核心观景+短走”作为目标，不追求走远；注意山区早晚温差与老人对海拔变化的适应。",
            "stars": "★★★★★",
            "dur": "5-8h",
            "fee": "付费",
            "kind": "高山湖/自然",
        },
        {
            "area": "天山天池方向｜舒缓加分",
            "name": "五江温泉城（温泉）",
            "query": "五江温泉城 阜康 天山天池",
            "lat": 43.909,
            "lon": 88.168,
            "objective": "温泉度假类点位，适合舒缓放松与给老人“回血”；通常以室内外泡池为主。",
            "subjective": "很适合放在天池同一天的傍晚，或作为“中间休息日”。注意老人泡温泉时长与补水，带娃注意防滑与保暖。",
            "stars": "★★★★☆",
            "dur": "2-4h",
            "fee": "付费",
            "kind": "温泉/休闲",
        },
        {
            "area": "天山天池方向｜轻徒步备选",
            "name": "天池周边栈道/轻量步道（按体力折返）",
            "query": "天山天池 栈道",
            "lat": 43.886028,
            "lon": 88.132389,
            "objective": "围绕核心景观的短步道/栈道型体验，可选择轻量线路，适合以观景为主的慢节奏玩法。",
            "subjective": "更适合作为“同一日的加分项”，而不是单独成行。老人腿脚不便时，建议以观景台与平缓路段为主，避免长台阶与湿滑路段。",
            "stars": "★★★★☆",
            "dur": "0.5-2h",
            "fee": "包含在景区内",
            "kind": "步道/观景",
        },
        {
            "area": "南山方向｜草原清凉",
            "name": "乌鲁木齐南山风景区（南山）",
            "query": "乌鲁木齐 南山 风景区",
            "lat": 43.474,
            "lon": 87.185,
            "objective": "市区周边较常见的避暑方向，主要体验是草原/林地景观、清凉空气与轻量散步；具体点位可按当天路况与人流灵活选择。",
            "subjective": "多代同行很友好：把它当作“开车看风景+短走+野餐/休息”就很舒服。建议安排在天气热的那几天，用来降温与缓冲节奏。",
            "stars": "★★★★★",
            "dur": "半天-一天",
            "fee": "部分点位付费",
            "kind": "草原/避暑",
        },
        {
            "area": "南山方向｜草原清凉",
            "name": "南山菊花台（菊花台）",
            "query": "南山 菊花台 乌鲁木齐",
            "lat": 43.333,
            "lon": 87.156,
            "objective": "南山方向常见的草原观景与摄影点，夏季草甸与远山景色更突出；具体体验与季节、人流关系较大。",
            "subjective": "如果老人能接受少量步行，它是“南山里更有代表性”的加分点；若当天很晒或老人腿脚一般，就只停在视野开阔处短拍照即可。",
            "stars": "★★★★☆",
            "dur": "2-5h",
            "fee": "可能付费",
            "kind": "草原/观景",
        },
        {
            "area": "南山方向｜度假休闲",
            "name": "丝绸之路国际度假区（丝路度假区）",
            "query": "丝绸之路国际度假区 乌鲁木齐",
            "lat": 43.439167,
            "lon": 87.410278,
            "objective": "度假区类点位，冬季滑雪为主，夏季通常也有山地度假/观景等项目；整体配套相对完善。",
            "subjective": "如果你们更偏“省心+设施齐”，它比纯野景更稳。适合安排半天到一天，按体力选项目。",
            "stars": "★★★☆☆",
            "dur": "半天-一天",
            "fee": "付费",
            "kind": "度假区/休闲",
        },
        {
            "area": "南山方向｜轻松自然",
            "name": "白杨沟（白杨沟）",
            "query": "白杨沟 乌鲁木齐",
            "lat": 43.406,
            "lon": 87.068,
            "objective": "山谷/林地型自然景观点，通常以乘凉、溪谷氛围与短走为主；强度因具体路线而异。",
            "subjective": "适合“老人需要清凉+孩子想玩水边/林间”的组合，但雨后湿滑要更谨慎。建议把它定位为轻松半日点。",
            "stars": "★★★★☆",
            "dur": "3-6h",
            "fee": "可能付费",
            "kind": "山谷/自然",
        },
        {
            "area": "南山方向｜观景体验",
            "name": "乌鲁木齐天山大峡谷（大峡谷）",
            "query": "乌鲁木齐 天山大峡谷",
            "lat": 43.431128,
            "lon": 87.3737683,
            "objective": "峡谷地貌与观景点结合的景区类型，常见需要步行与台阶上下，视觉冲击感更强。",
            "subjective": "景观上很值得，但对老人腿脚更有挑战。建议仅在全员状态好时安排，并把路线控制在“核心观景区”，不追求走深走远。",
            "stars": "★★★★☆",
            "dur": "4-7h",
            "fee": "付费",
            "kind": "峡谷/地貌",
        },
        {
            "area": "达坂城方向｜盐湖+风电（轻量）",
            "name": "新疆盐湖景区（盐湖）",
            "query": "新疆盐湖景区 达坂城",
            "lat": 43.39111,
            "lon": 88.10750,
            "objective": "盐湖观景与拍照型景点，体验以短停观景、拍照、走少量栈道为主。",
            "subjective": "多代同行可以把它当作“轻量出片点”。风大、日晒强时不宜久留，控制在 1-2 小时更舒服。",
            "stars": "★★★★☆",
            "dur": "1-2.5h",
            "fee": "付费",
            "kind": "盐湖/拍照",
        },
        {
            "area": "达坂城方向｜盐湖+风电（轻量）",
            "name": "达坂城古镇（达坂城）",
            "query": "达坂城古镇 乌鲁木齐",
            "lat": 43.3605,
            "lon": 88.3063,
            "objective": "带有西域风情的文化体验点位，常见是短停参观与拍照，强度通常可控。",
            "subjective": "更适合作为盐湖同方向的“顺路加点”。如果当天风太大或老人不适，就可以直接跳过。",
            "stars": "★★★☆☆",
            "dur": "1-2h",
            "fee": "可能付费",
            "kind": "文化/打卡",
        },
        {
            "area": "昌吉方向｜亲子+园区",
            "name": "新疆古生态园汗血马基地（古生态园）",
            "query": "新疆古生态园 汗血马基地 乌鲁木齐",
            "lat": 43.9026,
            "lon": 87.5388,
            "objective": "园区式景点，常见特点是内容集中、动线清晰、适合带娃与老人按节奏参观。",
            "subjective": "很适合作为“轻松不累的一天”。如果你们希望降低户外暴晒比例，这类园区往往比纯自然景点更省心。",
            "stars": "★★★☆☆",
            "dur": "2-4h",
            "fee": "付费",
            "kind": "园区/亲子",
        },
        {
            "area": "伊犁方向｜5 日经典环线（乌鲁木齐出发）",
            "name": "赛里木湖（赛湖）",
            "query": "赛里木湖 博尔塔拉 博乐",
            "lat": 44.601438,
            "lon": 81.392346,
            "objective": "新疆最经典的高山湖泊之一，常见玩法是环湖自驾+观景台短走+拍照；也可选择景区内住宿，第二天清晨/傍晚光线更好。",
            "subjective": "来自同事实测攻略（端午 5 日伊犁环线）：乌鲁木齐→赛里木湖约 6h/568km。对多代同行来说，建议把它安排成“当天只做 1 个主点”，避免赶路叠加走路。",
            "stars": "★★★★★",
            "dur": "4-8h",
            "fee": "付费",
            "kind": "湖泊/自然",
        },
        {
            "area": "伊犁方向｜5 日经典环线（乌鲁木齐出发）",
            "name": "果子沟大桥（果子沟）",
            "query": "果子沟大桥",
            "lat": 44.3022,
            "lon": 81.7886,
            "objective": "伊犁方向经典地标与观景点位，多为观景台短停拍照；通常与赛里木湖同方向顺路安排。",
            "subjective": "来自同事实测攻略（端午 5 日伊犁环线）：赛里木湖→伊宁途中可顺路安排。多代同行建议“短停 20-40 分钟”即可，风大时注意老人孩子保暖与安全。",
            "stars": "★★★★☆",
            "dur": "0.5-1.5h",
            "fee": "免费",
            "kind": "地标/观景",
        },
        {
            "area": "伊犁方向｜5 日经典环线（乌鲁木齐出发）",
            "name": "伊宁市（伊宁）",
            "query": "伊宁市 伊犁",
            "lat": 43.9168,
            "lon": 81.3241,
            "objective": "伊犁州核心城市，适合作为环线的“补给与夜晚休整”落脚点；可搭配老城街区、美食与轻松散步。",
            "subjective": "来自同事实测攻略（端午 5 日伊犁环线）：赛里木湖→伊宁约 200km。建议把伊宁当作“住宿+逛吃”的缓冲日，给老人孩子回血。",
            "stars": "★★★★☆",
            "dur": "半天-一天",
            "fee": "消费",
            "kind": "城市/补给",
        },
        {
            "area": "伊犁方向｜5 日经典环线（乌鲁木齐出发）",
            "name": "伊宁六星街（六星街）",
            "query": "伊宁 六星街",
            "lat": 43.9114,
            "lon": 81.3068,
            "objective": "街区型点位，氛围感与拍照属性强，适合傍晚散步与轻松打卡。",
            "subjective": "更适合作为“住在伊宁当晚”的轻松收尾，老人孩子都能接受；控制在 1-2 小时，不必深夜久逛。",
            "stars": "★★★★☆",
            "dur": "1-2h",
            "fee": "免费/消费",
            "kind": "街区/夜间",
        },
        {
            "area": "伊犁方向｜5 日经典环线（乌鲁木齐出发）",
            "name": "喀拉峻草原（喀拉峻）",
            "query": "喀拉峻草原",
            "lat": 43.145,
            "lon": 82.817,
            "objective": "伊犁草原代表性景区之一，典型体验是草原观景、轻徒步与观景台；通常需要一定车程与景区交通。",
            "subjective": "来自同事实测攻略（端午 5 日伊犁环线）：伊宁→昭苏→巩留一带可串联喀拉峻。多代同行建议提前确认区间车/步行强度，尽量选观景为主的轻线路。",
            "stars": "★★★★★",
            "dur": "5-9h",
            "fee": "付费",
            "kind": "草原/自然",
        },
        {
            "area": "伊犁方向｜5 日经典环线（乌鲁木齐出发）",
            "name": "那拉提草原（那拉提）",
            "query": "那拉提草原 空中草原",
            "lat": 43.29,
            "lon": 84.22,
            "objective": "北疆/伊犁方向最经典的草原景区之一，常见玩法是空中草原观景、轻徒步、拍照；旺季人流较大。",
            "subjective": "来自同事实测攻略（端午 5 日伊犁环线）：那拉提与唐布拉百里画廊常被作为二选一；多代同行更推荐“那拉提空中草原（观景为主）”，减少路上折腾与步行消耗。",
            "stars": "★★★★★",
            "dur": "5-9h",
            "fee": "付费",
            "kind": "草原/自然",
        },
        {
            "area": "伊犁方向｜5 日经典环线（乌鲁木齐出发）",
            "name": "巴音布鲁克草原（巴音布鲁克）",
            "query": "巴音布鲁克草原 天鹅湖 九曲十八弯",
            "lat": 42.882,
            "lon": 84.147,
            "objective": "草原湿地与“九曲十八弯”日落为代表的景区型点位，游玩通常需要一整天体力与车程。",
            "subjective": "更适合老人状态好时安排，或作为“伊犁方向深度升级点”。多代同行建议把它当成“当天唯一主点”，并准备外套与保暖。",
            "stars": "★★★★☆",
            "dur": "6-10h",
            "fee": "付费",
            "kind": "草原/湿地",
        },
        {
            "area": "伊犁方向｜5 日经典环线（乌鲁木齐出发）",
            "name": "独库公路北段（独库）",
            "query": "独库公路 北段 独山子 那拉提",
            "lat": 44.32971,
            "lon": 84.88278,
            "objective": "公路景观线类型，体验核心是“在路上看风景”；路况与通行受季节与管制影响，需要出发前再确认。",
            "subjective": "来自同事实测攻略（端午 5 日伊犁环线）：巴音镇→乌鲁木齐一段会走独库北段（文中也提到 S101 备选）。多代同行建议以安全为先，别夜间赶山路。",
            "stars": "★★★★★",
            "dur": "半天-一天",
            "fee": "免费",
            "kind": "自驾/风景线",
        },
        {
            "area": "北疆深度｜喀纳斯 + 禾木（乌鲁木齐出发）",
            "name": "布尔津（布尔津）",
            "query": "布尔津县",
            "lat": 47.7019,
            "lon": 86.8631,
            "objective": "北疆深度线路常见的中转与补给点，便于串联五彩滩、喀纳斯、禾木等。",
            "subjective": "来自同事实测攻略（北疆自驾 2023）：乌鲁木齐出发通常需要较长车程抵达布尔津/附近。更适合把北疆深度当作“4-6 天游”的独立板块安排。",
            "stars": "★★★☆☆",
            "dur": "半天",
            "fee": "消费",
            "kind": "城镇/补给",
        },
        {
            "area": "北疆深度｜喀纳斯 + 禾木（乌鲁木齐出发）",
            "name": "五彩滩（五彩滩）",
            "query": "布尔津 五彩滩",
            "lat": 47.9133,
            "lon": 86.6999,
            "objective": "典型玩法是傍晚/日落时段观景拍照，停留时间相对可控。",
            "subjective": "来自同事实测攻略（北疆自驾 2023）：常被安排在“长途赶路后的傍晚”作为轻量主点。老人孩子更适合这种“短停高回报”的点位。",
            "stars": "★★★★☆",
            "dur": "1-2h",
            "fee": "付费",
            "kind": "观景/地貌",
        },
        {
            "area": "北疆深度｜喀纳斯 + 禾木（乌鲁木齐出发）",
            "name": "喀纳斯景区（喀纳斯）",
            "query": "喀纳斯景区",
            "lat": 48.82139,
            "lon": 87.04722,
            "objective": "北疆王牌景区，湖泊、森林与观景点组合，通常需景区交通+步行，建议至少安排 1 天游玩。",
            "subjective": "来自同事实测攻略（北疆自驾 2023）：喀纳斯往往不止一天（同事文档有“喀纳斯 v2”）。多代同行建议把动线压缩到核心观景点，减少长距离徒步。",
            "stars": "★★★★★",
            "dur": "1-2 天",
            "fee": "付费",
            "kind": "湖泊/森林",
        },
        {
            "area": "北疆深度｜喀纳斯 + 禾木（乌鲁木齐出发）",
            "name": "禾木村（禾木）",
            "query": "禾木村",
            "lat": 48.56757,
            "lon": 87.42921,
            "objective": "图瓦村落与木屋风光结合的经典点位，适合慢节奏拍照与轻松散步；夜晚温差较大。",
            "subjective": "来自同事实测攻略（北疆自驾 2023）：禾木通常与喀纳斯成套安排。适合老人孩子“住一晚慢慢走”，但要准备保暖与防蚊。",
            "stars": "★★★★★",
            "dur": "半天-1 天",
            "fee": "付费",
            "kind": "村落/风光",
        },
        {
            "area": "北疆深度｜喀纳斯 + 禾木（乌鲁木齐出发）",
            "name": "白哈巴（白哈巴）",
            "query": "白哈巴村",
            "lat": 48.7352,
            "lon": 86.5495,
            "objective": "边境村落与风景点位，常作为喀纳斯方向的加分项，路程与通行要求需提前确认。",
            "subjective": "来自同事实测攻略（北疆自驾 2023）：同事将其与“禾木、喀纳斯”同一天组合。多代同行可视状态决定是否加点，别为了打卡硬赶路。",
            "stars": "★★★★☆",
            "dur": "3-7h",
            "fee": "付费",
            "kind": "村落/风光",
        },
        {
            "area": "北疆深度｜喀纳斯 + 禾木（乌鲁木齐出发）",
            "name": "乌尔禾世界魔鬼城（魔鬼城）",
            "query": "乌尔禾 世界魔鬼城",
            "lat": 46.0895,
            "lon": 85.7478,
            "objective": "雅丹地貌景区，常见体验是乘区间车+观景台短停，出片但日晒与风沙明显。",
            "subjective": "来自同事实测攻略（北疆自驾 2023）：布尔津→魔鬼城是一段常见衔接。多代同行建议避开正午暴晒，并准备防风沙措施。",
            "stars": "★★★★☆",
            "dur": "2-4h",
            "fee": "付费",
            "kind": "地貌/观景",
        },
        {
            "area": "阿勒泰远线｜可可托海方向",
            "name": "可可托海（可可托海）",
            "query": "可可托海景区 富蕴",
            "lat": 47.222081,
            "lon": 89.884211,
            "objective": "阿勒泰方向的代表性景区，以额尔齐斯大峡谷、花岗岩峰林、河谷森林和矿山/地质景观见长，整体风格和伊犁草原、吐鲁番古城都不一样。",
            "subjective": "它不是“乌鲁木齐周边顺手加一个”的点，而是更接近北疆远线里的独立板块。如果你们对阿勒泰方向有兴趣，它值得单独占掉 2-3 天，否则不要和伊犁、喀纳斯、吐鲁番硬塞在同一周里。",
            "stars": "★★★★★",
            "dur": "2-3 天",
            "fee": "付费",
            "kind": "峡谷/森林/地质",
        },
        {
            "area": "S101 国防公路｜分段玩法（自驾为主）",
            "name": "S101 国防公路（选一段即可）",
            "query": "S101 国防公路 乌鲁木齐",
            "lat": 43.40,
            "lon": 87.26,
            "objective": "自驾风景线类型，体验核心是“在路上看风景”，可灵活选择路段与停靠点；对步行要求较低但对驾驶时间有要求。",
            "subjective": "非常适合多代同行：把“看景”交给车程，把“走路”控制在短暂停靠。建议提前规划补给与卫生间点位，避免一路找不到停靠带来的焦虑。",
            "stars": "★★★★★",
            "dur": "半天-一天",
            "fee": "免费",
            "kind": "自驾/风景线",
        },
        {
            "area": "S101 国防公路｜分段玩法（自驾为主）",
            "name": "亚洲大陆地理中心（亚心）",
            "query": "亚洲大陆地理中心 乌鲁木齐",
            "lat": 43.5042,
            "lon": 87.3079,
            "objective": "地标打卡点位，适合短暂停靠拍照，作为 S101 的开场仪式感更强。",
            "subjective": "适合老人孩子“下车活动 15 分钟”的那种点：别久晒、别久站就很好。",
            "stars": "★★★☆☆",
            "dur": "0.5-1h",
            "fee": "可能付费",
            "kind": "地标/打卡",
        },
        {
            "area": "S101 国防公路｜分段玩法（自驾为主）",
            "name": "硫磺沟七彩山/百里丹霞（七彩丹霞）",
            "query": "硫磺沟 七彩山 S101",
            "lat": 43.74434,
            "lon": 87.21784,
            "objective": "丹霞地貌观景段，适合公路沿途多点短停观景与拍照。",
            "subjective": "如果你们想看“地貌很震撼但不想走太多路”，这段非常合适。注意防晒、补水与停车安全。",
            "stars": "★★★★☆",
            "dur": "1-3h",
            "fee": "免费",
            "kind": "丹霞/观景",
        },
        {
            "area": "S101 国防公路｜分段玩法（自驾为主）",
            "name": "肯斯瓦特水库（肯斯瓦特）",
            "query": "肯斯瓦特水库 S101",
            "lat": 43.966667,
            "lon": 87.95,
            "objective": "湖水与丹霞撞色的经典观景点位，适合停留拍照与短走观景台。",
            "subjective": "很出片，但停车与风大时的安全要注意。老人腿脚一般就只走到观景台，不要在碎石边缘逗留。",
            "stars": "★★★★★",
            "dur": "1-2.5h",
            "fee": "免费/可能付费项目",
            "kind": "水库/观景",
        },
        {
            "area": "S101 国防公路｜分段玩法（自驾为主）",
            "name": "康家石门子岩画（岩画）",
            "query": "康家石门子岩画 S101",
            "lat": 43.85032,
            "lon": 86.31821,
            "objective": "人文遗存类点位，可作为 S101 的文化补充，通常停留时间不长。",
            "subjective": "如果老人对历史文化感兴趣可以加；如果当天赶路或太晒，可以跳过，不影响整体体验。",
            "stars": "★★★☆☆",
            "dur": "0.5-1.5h",
            "fee": "可能付费",
            "kind": "人文/遗址",
        },
        {
            "area": "S101 国防公路｜分段玩法（自驾为主）",
            "name": "鹿角湾（鹿角湾）",
            "query": "鹿角湾 S101",
            "lat": 43.9799,
            "lon": 85.15805,
            "objective": "高山草原与松林景观点位，适合避暑、草原氛围与轻量散步。",
            "subjective": "更适合用半天慢慢玩：看草原、坐毡房、让孩子放电。注意早晚温差，给老人备外套。",
            "stars": "★★★★☆",
            "dur": "2-5h",
            "fee": "可能付费",
            "kind": "草原/避暑",
        },
        {
            "area": "S101 国防公路｜分段玩法（自驾为主）",
            "name": "安集海大峡谷（安集海）",
            "query": "安集海大峡谷",
            "lat": 44.0629,
            "lon": 85.7875,
            "objective": "峡谷地貌观景点位，视觉冲击强，常见为观景台短停与拍照。",
            "subjective": "对老人来说核心是“安全第一”：别靠近边缘、别逆光盲走，风大时减少停留。适合当作“路过加分点”。",
            "stars": "★★★★☆",
            "dur": "0.5-2h",
            "fee": "免费/可能付费服务",
            "kind": "峡谷/观景",
        },
        {
            "area": "吐鲁番方向｜文化历史",
            "name": "交河故城（交河）",
            "query": "交河故城 吐鲁番",
            "lat": 42.95460079,
            "lon": 89.06543255,
            "objective": "古城遗址类景点，体验以遗址形态与历史氛围为主；户外步行与遮阴条件会影响体感。",
            "subjective": "很有文化含量，但 8 月吐鲁番可能非常热。更建议清晨或傍晚参观，并严格控制停留时长；老人和孩子更需要补水与遮阳。",
            "stars": "★★★★☆",
            "dur": "2-4h",
            "fee": "付费",
            "kind": "遗址/历史",
        },
        {
            "area": "吐鲁番方向｜文化历史",
            "name": "高昌故城（高昌）",
            "query": "高昌故城 吐鲁番",
            "lat": 42.8585,
            "lon": 89.5323,
            "objective": "古城遗址类点位，内容更偏历史与遗址氛围；夏季多为户外高温体感。",
            "subjective": "如果你们对古城遗址特别感兴趣可以加；否则更建议二选一（交河/高昌），避免老人孩子在高温里走太久。",
            "stars": "★★★☆☆",
            "dur": "2-4h",
            "fee": "付费",
            "kind": "遗址/历史",
        },
        {
            "area": "吐鲁番方向｜文化历史",
            "name": "苏公塔（苏公塔）",
            "query": "苏公塔 吐鲁番",
            "lat": 42.93444,
            "lon": 89.20306,
            "objective": "历史建筑类点位，通常以短停参观与拍照为主，耗时较短。",
            "subjective": "很适合作为吐鲁番一日里“轻量文化点”。避开正午最晒时段更舒服。",
            "stars": "★★★☆☆",
            "dur": "0.5-1.5h",
            "fee": "可能付费",
            "kind": "历史建筑/打卡",
        },
        {
            "area": "吐鲁番方向｜文化历史",
            "name": "坎儿井民俗园/坎儿井（坎儿井）",
            "query": "吐鲁番 坎儿井",
            "lat": 42.9472,
            "lon": 89.1273,
            "objective": "传统水利与民俗展示相关点位，内容相对集中，参观强度通常较低，适合作为吐鲁番一日中的轻量点。",
            "subjective": "比纯遗址更适合多代同行，尤其在高温天。可以作为“了解一段历史+室内/半室内缓冲”的组合点。",
            "stars": "★★★☆☆",
            "dur": "1-2h",
            "fee": "付费",
            "kind": "民俗/文化",
        },
        {
            "area": "吐鲁番方向｜文化历史",
            "name": "吐峪沟（吐峪沟）",
            "query": "吐峪沟 吐鲁番",
            "lat": 42.8763,
            "lon": 89.7512,
            "objective": "峡谷风光与古村落/历史文化结合的点位，体验兼具自然与人文。",
            "subjective": "如果你们更喜欢“有故事的风景”，它会比纯打卡更有记忆点。但路程与体力要评估，建议当作吐鲁番方向的升级备选。",
            "stars": "★★★☆☆",
            "dur": "2-5h",
            "fee": "可能付费",
            "kind": "村落/人文自然",
        },
        {
            "area": "吐鲁番方向｜亲子休闲",
            "name": "葡萄沟（葡萄沟）",
            "query": "葡萄沟 吐鲁番",
            "lat": 42.9941,
            "lon": 89.1756,
            "objective": "绿荫葡萄园与休闲观光结合的区域型景点，体验以漫步、休息、品尝与轻量观光为主。",
            "subjective": "多代同行友好，因为节奏可以很慢。更建议把它放在午后热的时候作为“乘凉+休息”的点，而不是正午暴晒下长时间走动。",
            "stars": "★★★☆☆",
            "dur": "2-4h",
            "fee": "可能付费",
            "kind": "休闲/亲子",
        },
        {
            "area": "吐鲁番方向｜远观打卡",
            "name": "火焰山（火焰山）",
            "query": "火焰山 吐鲁番",
            "lat": 42.9124,
            "lon": 89.5145,
            "objective": "地貌/打卡型点位，典型体验是短停拍照与感受地貌氛围；夏季体感通常更热。",
            "subjective": "建议把它当作“顺路短停”，不作为长时间游览点；对老人和孩子来说，短停+快速回到车里更舒适。",
            "stars": "★★★☆☆",
            "dur": "0.5-1.5h",
            "fee": "可能付费",
            "kind": "地貌/打卡",
        },
        {
            "area": "东天山方向｜奇台 1-2 天游",
            "name": "江布拉克（江布拉克）",
            "query": "江布拉克景区 奇台",
            "lat": 43.562175,
            "lon": 89.754700,
            "objective": "东天山方向很适合家庭游的草原/麦田/山地景区，典型体验是天山麦海、空中草原、怪坡、轻量步道与观景平台。",
            "subjective": "如果你们想要一个比天池更开阔、比吐鲁番更凉快、又不想一下子跑到伊犁/喀纳斯那么远的方向，它其实非常值得进候选。更像“1 天游升级版”或“2 天游轻度外拓”。",
            "stars": "★★★★★",
            "dur": "1 天-2 天",
            "fee": "付费",
            "kind": "草原/麦田/避暑",
        },
        {
            "area": "乌鲁木齐周边｜历史小众（可选）",
            "name": "乌拉泊古城（乌拉泊）",
            "query": "乌拉泊古城 乌鲁木齐",
            "lat": 43.6604,
            "lon": 87.8387,
            "objective": "丝路相关古城遗址类点位，偏小众，适合对历史感兴趣的家庭短停参观。",
            "subjective": "作为“人少+有故事”的备选不错，但不建议在烈日下长时间逗留。若老人怕晒或孩子不耐走，可跳过。",
            "stars": "★★★☆☆",
            "dur": "1-2.5h",
            "fee": "可能免费/可能付费",
            "kind": "遗址/小众",
        },
        {
            "area": "乌鲁木齐周边｜风电+湖景备选",
            "name": "达坂城风力发电站（风车）",
            "query": "达坂城 风力发电站",
            "lat": 43.525713,
            "lon": 88.148117,
            "objective": "公路沿线的观景/路过型点位，主要看点是成片风机与戈壁景观的组合，适合短暂停靠拍照。",
            "subjective": "适合做“开车途中加一段记忆点”。风大时注意老人小孩保暖与安全，控制停留时长即可。",
            "stars": "★★★☆☆",
            "dur": "0.5-1h",
            "fee": "免费",
            "kind": "路过/观景",
        },
        {
            "area": "乌鲁木齐周边｜风电+湖景备选",
            "name": "柴窝堡湖（柴窝堡）",
            "query": "柴窝堡湖 乌鲁木齐",
            "lat": 43.5295,
            "lon": 88.1787,
            "objective": "城市周边湖泊/湿地类点位，适合短暂停留与观景；体验依赖当日天气与可到达的观景点位。",
            "subjective": "更适合作为“顺路就去”的轻量点，不建议专程投入太多时间。若风大或日晒强，优先保证舒适与安全。",
            "stars": "★★★☆☆",
            "dur": "1-2h",
            "fee": "免费/可能付费",
            "kind": "湖景/观景",
        },
    ]

    md: list[str] = []
    md.append(f"# {trip_title}")
    md.append("")
    md.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    md.append("")

    md.append("## 第一步：关键信息（按多代同行默认假设）")
    md.append("")
    for k, v in user_profile.items():
        md.append(f"- {k}：{v}")
    md.append("")

    md.append("## 你关心的：乌鲁木齐做枢纽怎么走（先给方向感）")
    md.append("")
    md.append("你说得对：乌市本身通常只需要 1-2 天（博物馆/大巴扎/轻松逛吃），真正的看点在“乌鲁木齐向外辐射”。这里先把方向感捋清：")
    md.append("")
    md.append("- **近郊 1 天游（轻松）**：天池 / 南山 / 盐湖（达坂城）/ 温泉。适合带老人孩子做“避暑+缓冲日”。")
    md.append("- **吐鲁番方向 1-2 天游（东疆，高温）**：交河/高昌/坎儿井/葡萄沟/火焰山。建议清晨或傍晚，正午尽量室内或休息。")
    md.append("- **伊犁方向 4-6 天游（草原+湖泊）**：赛里木湖 → 果子沟 → 伊宁（补给） → 喀拉峻/特克斯一带 → 那拉提 →（可选）巴音布鲁克 → 返程走独库北段或其他路线。")
    md.append("- **北疆深度 4-7 天游（喀纳斯+禾木）**：布尔津（补给） → 五彩滩 → 喀纳斯 → 禾木 →（可选）白哈巴/魔鬼城。更适合作为“单独板块”，不要和吐鲁番挤在同一周里硬塞。")
    md.append("")
    md.append("来自同事实测攻略补充：在「端午 5 日伊犁环线」里，同事写到“乌鲁木齐→赛里木湖约 6h/568km”，以及返程会考虑“独库北段 / S101 备选”。这类信息我会继续用外部检索做时效校验（路况/开放/预约）。")
    md.append("")
    md.append("### 同事线路怎么走（用来帮你选方向，不是最终行程）")
    md.append("")
    md.append("**线路范式 A｜伊犁经典环线（更推荐作为 7 天游主方向）**")
    md.append("- D1 乌鲁木齐：到达/缓冲（博物馆/逛吃二选一）")
    md.append("- D2 乌鲁木齐 → 赛里木湖（同事写约 6h/568km）：当天只做赛湖 1 个主点")
    md.append("- D3 赛里木湖 → 果子沟 → 伊宁：傍晚六星街/逛吃，住伊宁（补给日）")
    md.append("- D4 伊宁 →（二选一）喀拉峻/特克斯一带：以观景为主，减少长徒步")
    md.append("- D5 特克斯/巩留一带 → 那拉提：空中草原观景为主")
    md.append("- D6 返程：按路况二选一（独库北段 / 常规高速返乌鲁木齐）")
    md.append("- D7 乌鲁木齐：缓冲 + 返程（或天池半日）")
    md.append("")
    md.append("**线路范式 B｜北疆深度（喀纳斯+禾木）**")
    md.append("- D1 乌鲁木齐：到达/缓冲")
    md.append("- D2 长途到布尔津（补给）")
    md.append("- D3 五彩滩 → 喀纳斯：住景区/贾登峪附近")
    md.append("- D4 禾木：住一晚慢慢走（温差大，注意保暖）")
    md.append("- D5（可选）白哈巴 / 或回程衔接魔鬼城")
    md.append("- D6 回乌鲁木齐（长途日）")
    md.append("- D7 乌鲁木齐：缓冲/返程")
    md.append("")
    md.append("**线路范式 C｜轻松带娃带老人（不追求喀纳斯/伊犁深度）**")
    md.append("- 乌鲁木齐 1-2 天游：博物馆 + 大巴扎/逛吃")
    md.append("- 周边 1 天游：天池（必去）或南山（避暑缓冲）")
    md.append("- 吐鲁番 1 天游：交河/坎儿井/葡萄沟（避开正午暴晒）")
    md.append("- S101 1 天游：选一段看地貌（短停为主）")
    md.append("")

    md.append("## 第二步：景点备选清单（更适合挑选的文档式展示）")
    md.append("")
    md.append(
        '<div id="candidate-toolbar" class="candidate-toolbar">'
        '<div class="hint">'
        '点击景点名称：在右侧地图定位｜点击 🗺️：外跳高德地图｜点击 📷：图片搜索（仅作参考）｜必去 '
        '<b id="candidate-must-count">0</b> ｜不想去 '
        '<b id="candidate-avoid-count">0</b> ｜未选：随缘安排（顺路就去，否则就不去）'
        "</div>"
        '<div class="actions">'
        '<button id="candidate-copy" class="candidate-btn primary" type="button" disabled>复制选择结果</button>'
        '<button id="candidate-clear" class="candidate-btn" type="button" disabled>清空必去/不想去</button>'
        "</div>"
        "</div>"
    )
    md.append("")

    groups: dict[str, list[dict]] = {}
    for item in pool:
        groups.setdefault(str(item.get("area") or "其他"), []).append(item)

    for items in groups.values():
        items.sort(
            key=lambda x: (stars_score(str(x.get("stars") or "")), str(x.get("name") or "")),
            reverse=True,
        )

    idx = 0
    ordered_points: list[dict] = []
    for area, items in groups.items():
        md.append('<section class="candidate-area">')
        md.append(
            f'<div class="candidate-area-title">'
            f'<h3 class="name">{escape(area)}</h3>'
            f'<div class="meta">{len(items)} 个</div>'
            f"</div>"
        )
        md.append('<div class="candidate-list">')
        for it in items:
            idx += 1
            name = str(it.get("name") or "").strip()
            query = str(it.get("query") or name).strip()
            p: dict = {"idx": idx, "query": query, "label": marker_label(name)}
            lat = it.get("lat")
            lon = it.get("lon")
            if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                p["lat"] = float(lat)
                p["lon"] = float(lon)
                p["km"] = haversine_km(URUMQI_BASE["lat"], URUMQI_BASE["lon"], float(lat), float(lon))
                p["dir"] = direction_from_urumqi(float(lat), float(lon))
            p["area"] = area
            p["kind"] = str(it.get("kind") or "").strip()
            p["title"] = name
            p["objective"] = str(it.get("objective") or "").strip()
            p["subjective"] = str(it.get("subjective") or "").strip()
            ordered_points.append(p)
            stars = str(it.get("stars") or "").strip()
            dur = str(it.get("dur") or "").strip()
            fee = str(it.get("fee") or "").strip()
            kind = str(it.get("kind") or "").strip()
            objective = str(it.get("objective") or "").strip()
            subjective = str(it.get("subjective") or "").strip()
            distance_pill = ""
            direction_pill = ""
            if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
                distance_pill = f"距乌市约 {haversine_km(URUMQI_BASE['lat'], URUMQI_BASE['lon'], float(lat), float(lon))} km"
                direction_pill = direction_from_urumqi(float(lat), float(lon))

            md.append(f'<article class="candidate-card" data-idx="{idx}">')
            md.append('<div class="candidate-top">')
            md.append('<div class="candidate-title">')
            md.append(f'<span class="candidate-index">{idx}</span>')
            md.append(spot_html(name, query))
            md.append(
                f' <a href="{build_images_link(query)}" target="_blank" rel="noopener noreferrer">📷</a>'
            )
            md.append('<span class="candidate-actions">')
            md.append('<button class="candidate-pillbtn must" type="button">必去</button>')
            md.append('<button class="candidate-pillbtn avoid" type="button">不想去</button>')
            md.append('<button class="candidate-pillbtn neutral" type="button">随缘</button>')
            md.append("</span>")
            md.append("</div>")
            md.append(f'<div class="candidate-rating">{escape(stars)}</div>')
            md.append("</div>")

            md.append('<div class="candidate-pills">')
            if kind:
                md.append(f'<span class="candidate-pill">{escape(kind)}</span>')
            if dur:
                md.append(f'<span class="candidate-pill">耗时 {escape(dur)}</span>')
            if fee:
                md.append(f'<span class="candidate-pill">门票 {escape(fee)}</span>')
            if distance_pill:
                md.append(f'<span class="candidate-pill">{escape(distance_pill)}</span>')
            if direction_pill:
                md.append(f'<span class="candidate-pill">{escape(direction_pill)}</span>')
            md.append("</div>")

            md.append('<div class="candidate-desc">')
            if objective:
                md.append("<div>")
                md.append('<div class="candidate-desc-title">客观内容介绍</div>')
                md.append(f'<div class="candidate-desc-body">{escape(objective)}</div>')
                md.append("</div>")
            if subjective:
                md.append("<div>")
                md.append('<div class="candidate-desc-title">主观评价建议</div>')
                md.append(f'<div class="candidate-desc-body">{escape(subjective)}</div>')
                md.append("</div>")
            md.append("</div>")
            md.append("</article>")

        md.append("</div>")
        md.append("</section>")
        md.append("")

    md.append("## 请选择必去 / 不想去（这一步我会暂停等你选）")
    md.append("")
    md.append("- 两个选择：**必去**（泛绿） / **不想去**（泛红）。")
    md.append("- **未选择** 的景点：我会按“顺路就去，否则就不去”的策略随缘安排。")
    md.append("- 你也可以直接说：**“你直接决定，不用我选”**，我会按多代同行节奏给出 7 日可执行自驾行程。")
    md.append("")

    markdown = "\n".join(md) + "\n"
    initial_days = [[p] for p in ordered_points]
    extras: list[dict] = []

    template = template_path.read_text(encoding="utf-8")
    html_out = (
        template.replace("MARKDOWN_CONTENT_JSON", json.dumps(markdown, ensure_ascii=False))
        .replace("INITIAL_DAYS_JSON", json.dumps(initial_days, ensure_ascii=False))
        .replace("EXTRAS_JSON", json.dumps(extras, ensure_ascii=False))
    )

    (outputs_dir / "Trip_Candidates_Urumqi_Family_7D.md").write_text(markdown, encoding="utf-8")
    (outputs_dir / "Trip_Candidates_Urumqi_Family_7D.html").write_text(html_out, encoding="utf-8")


if __name__ == "__main__":
    main()
