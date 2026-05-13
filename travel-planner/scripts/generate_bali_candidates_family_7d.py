import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from html import escape
from urllib.parse import quote


def build_gmaps_link(query: str) -> str:
    q = query.replace(" ", "+")
    return f"https://www.google.com/maps/search/?api=1&query={q}"

def build_gimages_link(query: str) -> str:
    return f"https://www.google.com/search?tbm=isch&q={quote(query)}"


def spot(name: str, query: Optional[str] = None) -> str:
    q = query or name
    link = build_gmaps_link(q)
    return f"[{name}]({link}) [🗺️]({link})"

def stars_score(stars: str) -> float:
    s = str(stars or "")
    score = float(s.count("★"))
    if "½" in s:
        score += 0.5
    return score


def spot_html(name: str, query: str) -> str:
    link = build_gmaps_link(query)
    return f'<a class="candidate-name" href="{link}">{escape(name)}</a> <a href="{link}">🗺️</a>'

def marker_label(name: str) -> str:
    s = str(name or "").strip()
    if "（" in s and "）" in s:
        inner = s.split("（", 1)[1].rsplit("）", 1)[0].strip()
        if inner:
            return inner
    return s


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    template_path = base_dir / "template_intl.html"
    outputs_dir = base_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    trip_title = "巴厘岛 7 日亲子度假（两大两小：8 岁 / 6 岁）｜第二步：景点备选清单（用于选择）"

    user_profile = {
        "目的地": "印尼｜巴厘岛（Bali）",
        "天数": "7 天游玩",
        "同行人员": "2 大 2 小（8 岁、6 岁）",
        "节奏": "度假为主：每天 1-2 个主点 + 午休/泳池时间",
        "交通": "包车/打车（Grab/Blue Bird）为主；远距离日游建议包车更省心",
        "住宿": "建议 2+2+3：乌布 2 晚（稻田/文化）+ 金巴兰/乌鲁瓦图 2 晚（海景/日落）+ 努沙杜瓦/水明漾 3 晚（亲子海滩/配套）",
        "备注": "带娃优先避开中午暴晒与走路强度过大的点；动物园/水上乐园要预留充足补水与防晒",
    }

    pool = [
        {
            "area": "乌布-亲子",
            "name": "Bali Safari & Marine Park（巴厘野生动物园）",
            "query": "Bali Safari and Marine Park",
            "objective": "大型亲子动物园类景区，通常包含观光车/分区游览/互动体验等，整体动线较成熟，适合孩子“看动物+放电”。因为是户外为主，体感受天气影响明显。",
            "subjective": "亲子很推荐作为“主打一天”的高光点。为了避免暴晒与排队，通常更适合早到并把最想看的部分放在前半天；带好防晒、补水与替换衣物，孩子更舒服。",
            "stars": "★★★★★",
            "dur": "4-7h",
            "fee": "付费",
            "kind": "动物园/亲子",
        },
        {
            "area": "乌布-亲子",
            "name": "Bali Zoo（巴厘动物园）",
            "query": "Bali Zoo",
            "objective": "相对“轻量级”的动物园/亲子景点，通常以步行参观为主，路线更容易控强度；适合安排半天看动物、简单互动与拍照。",
            "subjective": "当你们更偏好“省心不累”时，它通常比大型动物园更合适。建议避开正午最热的时段，做好防蚊与补水；孩子兴奋过头时也更容易随时撤退。",
            "stars": "★★★★☆",
            "dur": "3-5h",
            "fee": "付费",
            "kind": "动物园/亲子",
        },
        {
            "area": "乌布-自然",
            "name": "Tegalalang Rice Terrace（德格拉朗梯田）",
            "query": "Tegalalang Rice Terrace",
            "objective": "乌布周边的梯田观景点，主要体验是梯田层次与田野景观；通常有观景台与若干步道选择，可以按体力决定走多少。",
            "subjective": "带娃更推荐把它当作“观景+短走”的轻松点：挑视野好的观景位即可，不追求走到最深。为了更舒适和更好拍照，一般清晨/傍晚比中午更合适。",
            "stars": "★★★★☆",
            "dur": "1.5-3h",
            "fee": "小费/付费",
            "kind": "自然/观景",
        },
        {
            "area": "乌布-自然",
            "name": "Campuhan Ridge Walk（坎普汉山脊步道）",
            "query": "Campuhan Ridge Walk",
            "objective": "乌布附近的轻徒步/散步路线，通常以开阔视野与绿色景观为卖点，路线强度相对温和，可以按需折返。",
            "subjective": "作为亲子“轻运动”很合适，但中午会更晒更热。带娃建议设置一个“最远点”，走到就回头，避免孩子后段体力掉线影响情绪。",
            "stars": "★★★★☆",
            "dur": "1-2.5h",
            "fee": "免费",
            "kind": "步道/轻徒步",
        },
        {
            "area": "乌布-宗教",
            "name": "Tirta Empul（圣泉寺）",
            "query": "Tirta Empul Temple",
            "objective": "寺庙/文化体验类景点，常见看点包括寺庙建筑、泉池与仪式氛围，整体偏“文化参观”而非游乐项目。",
            "subjective": "适合作为“文化半日”点缀行程。带娃更建议以参观为主、节奏放慢；若想参与净身类体验，通常需要排队与着装规范，需评估孩子耐心与当日体力。",
            "stars": "★★★★☆",
            "dur": "1.5-3h",
            "fee": "付费",
            "kind": "寺庙/文化",
        },
        {
            "area": "乌布-自然",
            "name": "Tegenungan Waterfall（特格农甘瀑布）",
            "query": "Tegenungan Waterfall",
            "objective": "瀑布氛围体验点，常见玩法是到观景点拍照、感受水声与热带植被；通常需要走台阶上下，湿滑风险与天气相关。",
            "subjective": "亲子可去但要控强度：建议只到主要观景点即可，不一定要走到最底。雨后更滑时优先安全；穿防滑鞋、带换洗衣物会更从容。",
            "stars": "★★★★☆",
            "dur": "1.5-3h",
            "fee": "付费",
            "kind": "瀑布/自然",
        },
        {
            "area": "乌布-文化",
            "name": "Ubud Palace（乌布王宫）",
            "query": "Ubud Palace",
            "objective": "市区内的传统建筑/文化参观点，参观距离通常不长，适合了解一点当地建筑风格与做城市漫步的停靠点。",
            "subjective": "更推荐当作“顺路短停”，不必专程安排很久。和市场、咖啡馆组合体验会更完整；带娃时可随时调整停留时长。",
            "stars": "★★★☆☆",
            "dur": "0.5-1.5h",
            "fee": "免费",
            "kind": "文化/建筑",
        },
        {
            "area": "乌布-文化",
            "name": "Ubud Art Market（乌布艺术市场）",
            "query": "Ubud Art Market",
            "objective": "手工艺品与纪念品为主的市场，常见小摆件、衣物与编织品等，适合集中浏览与采购伴手礼。",
            "subjective": "对带娃来说容易“逛到累”：更建议先定好想买的类型，再集中下手并控制时长。价格通常可适度议价；孩子如果对人多嘈杂敏感，就把它当可选项。",
            "stars": "★★★☆☆",
            "dur": "1-2h",
            "fee": "免费",
            "kind": "市场/购物",
        },
        {
            "area": "乌布-动物",
            "name": "Sacred Monkey Forest Sanctuary（乌布猴林）",
            "query": "Sacred Monkey Forest Sanctuary",
            "objective": "森林步道+猴群栖息地类型景点，主要体验是林荫步行、看猴群活动与拍照；整体更像“自然漫步”。",
            "subjective": "带娃可去但一定要把安全规则讲清楚：避免手上拿食物/塑料袋，帽子眼镜要固定，不主动挑逗动物。如果孩子怕动物或对突然接近不适应，这个点可以直接跳过。",
            "stars": "★★★★☆",
            "dur": "1.5-3h",
            "fee": "付费",
            "kind": "动物/森林",
        },
        {
            "area": "北巴厘-寺庙",
            "name": "Ulun Danu Beratan Temple（水神庙）",
            "query": "Ulun Danu Beratan Temple",
            "objective": "湖边寺庙与湖景观结合的景点，典型看点是“水边建筑+山湖背景”的画面感，步行强度通常可控。",
            "subjective": "更适合包车日游安排，因为车程往往较长。亲子建议只搭配 1-2 个附近点，避免把一天塞得太满导致孩子在车上时间过长。",
            "stars": "★★★★☆",
            "dur": "2-4h",
            "fee": "付费",
            "kind": "寺庙/湖景",
        },
        {
            "area": "北巴厘-自然",
            "name": "Jatiluwih Rice Terraces（贾提卢维梯田）",
            "query": "Jatiluwih Rice Terraces",
            "objective": "更大尺度的梯田景观区，体验以“开阔田野+层次感”为主；通常也可以选择不同长度的步道线路。",
            "subjective": "适合偏好自然与慢节奏的家庭。亲子建议选短线或仅观景点停留，避开正午暴晒；如果当天还要跑别的点，就别安排长步道。",
            "stars": "★★★★☆",
            "dur": "2-4h",
            "fee": "付费",
            "kind": "梯田/自然",
        },
        {
            "area": "金巴兰-海滩",
            "name": "Jimbaran Beach（日落海滩+海鲜晚餐）",
            "query": "Jimbaran Beach",
            "objective": "傍晚海滩+晚餐组合型目的地，通常以日落氛围、沙滩玩耍与海边就餐体验为主，步行强度低。",
            "subjective": "非常适合亲子作为“晚间主线”安排：孩子玩沙，大人放松。餐厅选择上建议优先口碑稳定的店，并提前确认点餐与计价方式，减少沟通成本。",
            "stars": "★★★★★",
            "dur": "2-4h",
            "fee": "免费/消费",
            "kind": "海滩/美食",
        },
        {
            "area": "乌鲁瓦图-寺庙",
            "name": "Uluwatu Temple（乌鲁瓦图断崖寺）",
            "query": "Uluwatu Temple",
            "objective": "断崖海景+寺庙建筑的组合型景点，主要体验是海景视野、崖边步道与日落氛围，拍照点丰富。",
            "subjective": "带娃要把安全放第一：崖边行走看紧孩子，同时注意猴子出没的情况。若计划连看 Kecak 火舞，建议把交通与散场拥挤的预期考虑进去，避免回程太晚影响第二天。",
            "stars": "★★★★★",
            "dur": "2-4h",
            "fee": "付费",
            "kind": "寺庙/海景",
        },
        {
            "area": "乌鲁瓦图-演出",
            "name": "Kecak Fire Dance（凯卡火舞｜乌鲁瓦图）",
            "query": "Kecak Fire Dance Uluwatu",
            "objective": "传统表演类体验，常作为日落后的夜间活动，亮点在于仪式感与现场氛围；对体力消耗相对小但需要坐着观看。",
            "subjective": "亲子可去，但要预估孩子耐心：建议选更靠边的位置，方便中途进出与照顾。若孩子开始犯困，提前离场比硬撑更划算。",
            "stars": "★★★★☆",
            "dur": "1-1.5h",
            "fee": "付费",
            "kind": "演出/文化",
        },
        {
            "area": "努沙杜瓦-亲子",
            "name": "Nusa Dua Beach（努沙杜瓦海滩）",
            "query": "Nusa Dua Beach",
            "objective": "亲子度假区代表性海滩带，典型优势是配套成熟、活动选择多，适合玩沙、游泳、酒店躺平与日常补给。",
            "subjective": "如果你们追求“省心+稳定体验”，把它作为主基地通常最舒服。建议每天都留固定的海滩/泳池时间，行程会更像度假而不是赶路。",
            "stars": "★★★★★",
            "dur": "2-4h",
            "fee": "免费/消费",
            "kind": "海滩/度假",
        },
        {
            "area": "努沙杜瓦-文化",
            "name": "Garuda Wisnu Kencana（GWK 文化公园）",
            "query": "Garuda Wisnu Kencana Cultural Park",
            "objective": "地标雕像+园区式文化景点，体验以“看地标、拍照、园区漫步”为主，步行强度取决于你逛多大范围。",
            "subjective": "亲子建议把它当作“短逛点缀”：优先地标区域与核心点即可。因为遮阴未必充足，通常傍晚体感更好，把体力留给更适合孩子的海滩/泳池更值。",
            "stars": "★★★★☆",
            "dur": "2-4h",
            "fee": "付费",
            "kind": "地标/文化",
        },
        {
            "area": "库塔-亲子",
            "name": "Waterbom Bali（水上乐园）",
            "query": "Waterbom Bali",
            "objective": "水上乐园类亲子目的地，通常包含滑道、戏水区与休息区，适合孩子集中放电；全天活动会比较耗体力与防晒资源。",
            "subjective": "很适合做成“亲子高光日”。建议提前了解身高/年龄限制并规划休息节奏；带好防晒、水鞋、毛巾与补水零食，能明显提升体验。",
            "stars": "★★★★★",
            "dur": "5-8h",
            "fee": "付费",
            "kind": "水上乐园/亲子",
        },
        {
            "area": "水明漾-沙滩",
            "name": "Seminyak Beach（水明漾海滩）",
            "query": "Seminyak Beach",
            "objective": "海滩+餐饮配套密集的休闲区域，典型玩法是傍晚看日落、海边散步玩沙、顺路解决一餐，机动性强。",
            "subjective": "适合做“缓冲日/随缘日”的主场景。带娃不建议追求密集打卡，把它当作散步+玩沙+吃饭的组合会更舒服。",
            "stars": "★★★★☆",
            "dur": "2-4h",
            "fee": "免费/消费",
            "kind": "海滩/休闲",
        },
        {
            "area": "苍古-亲子",
            "name": "Finns Recreation Club（亲子娱乐中心）",
            "query": "Finns Recreation Club Bali",
            "objective": "亲子娱乐综合体类型，常见是室内外混合项目（运动/游乐等），更像“换个场景放电”的选择。",
            "subjective": "非常适合雨天、想避暑或不想跑远的日子。建议按孩子兴趣选 1-2 个项目即可，保留弹性，避免过度兴奋后疲劳崩盘。",
            "stars": "★★★★☆",
            "dur": "2-5h",
            "fee": "付费",
            "kind": "亲子娱乐",
        },
        {
            "area": "海神庙-日落",
            "name": "Tanah Lot Temple（海神庙）",
            "query": "Tanah Lot Temple",
            "objective": "经典日落观景+寺庙地标类型景点，看点主要在海边视野与氛围；周边通常有观景步道与商业配套。",
            "subjective": "更推荐在傍晚安排，但人流往往更密集。带娃建议选择更宽松的观景点位，不必挤到最前排；把“安全+舒适”放在“抢最佳角度”之前。",
            "stars": "★★★★★",
            "dur": "2-4h",
            "fee": "付费",
            "kind": "寺庙/日落",
        },
        {
            "area": "东巴厘-经典",
            "name": "Lempuyang Temple（天空之门）",
            "query": "Lempuyang Temple Gate of Heaven",
            "objective": "以“打卡拍照”为主的热门点位，体验高度依赖当天能见度与人流；通常需要排队才能完成经典机位拍摄。",
            "subjective": "两大两小一般不优先推荐：车程和排队会消耗孩子耐心。如果你们非常想去，更适合清晨出发并准备备选方案，把它当作“可成可不成”的加分项。",
            "stars": "★★★☆☆",
            "dur": "4-7h",
            "fee": "付费",
            "kind": "打卡/寺庙",
        },
        {
            "area": "努沙佩尼达-日游",
            "name": "Nusa Penida Day Trip（佩尼达岛一日游）",
            "query": "Nusa Penida",
            "objective": "离岛日游类型，通常以海岛氛围与观景点为卖点，但会涉及船程与岛上交通，整体强度和不确定性更高。",
            "subjective": "亲子不是不能去，但更累、更看天气与路况。更建议当作加分项：如果你们当天状态很好、天气稳定再上；否则把时间留给本岛更省心的海滩/亲子点。",
            "stars": "★★★☆☆",
            "dur": "8-11h",
            "fee": "付费",
            "kind": "离岛/日游",
        },
        {
            "area": "乌布-文化",
            "name": "Goa Gajah（象窟）",
            "query": "Goa Gajah",
            "objective": "遗迹/洞窟元素结合的文化参观点，游览距离通常可控，带一点“探索感”，对孩子会更友好一些。",
            "subjective": "如果孩子喜欢探洞或对遗迹好奇，它会比纯参观寺庙更有趣。雨后湿滑时注意脚下与台阶；安排成 1-2 小时的短停最合适。",
            "stars": "★★★★☆",
            "dur": "1-2h",
            "fee": "付费",
            "kind": "遗迹/文化",
        },
        {
            "area": "乌布-自然",
            "name": "Bali Swing（秋千体验｜乌布）",
            "query": "Bali Swing Ubud",
            "objective": "偏拍照体验的项目点，通常以秋千/观景平台为主，内容相对集中，体验高度取决于排队与当日人流。",
            "subjective": "更适合大人拍照打卡；带娃时如果孩子胆小、对高度敏感或限制条件不合适，就建议直接跳过。时间有限时，把它让位给梯田/动物园往往更有性价比。",
            "stars": "★★★☆☆",
            "dur": "1-2h",
            "fee": "付费",
            "kind": "拍照/体验",
        },
        {
            "area": "金巴兰-海滩",
            "name": "Kedonganan Beach（更安静的海边散步）",
            "query": "Kedonganan Beach",
            "objective": "相对更安静、偏本地氛围的海滩散步点，玩法以傍晚散步、看海与轻松放空为主，强度低。",
            "subjective": "很适合作为“备选轻松点”：当你们不想去拥挤景点时就安排它。带娃注意潮水、碎贝壳与脚下安全；把它当作顺路散步点会更合适。",
            "stars": "★★★★☆",
            "dur": "1.5-3h",
            "fee": "免费/消费",
            "kind": "海滩/休闲",
        },
    ]

    md: list[str] = []
    md.append(f"# {trip_title}")
    md.append("")
    md.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    md.append("")

    md.append("## 第一步：关键信息（已收集/按亲子度假默认假设）")
    md.append("")
    for k, v in user_profile.items():
        md.append(f"- {k}：{v}")
    md.append("")

    md.append("## 第二步：景点备选清单（更适合挑选的文档式展示）")
    md.append("")
    md.append(
        '<div id="candidate-toolbar" class="candidate-toolbar">'
        '<div class="hint">'
        '点击景点名称：在右侧地图定位｜点击 🗺️：外跳 Google Maps｜点击 📷：图片搜索（仅作参考）｜必去 '
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
        items.sort(key=lambda x: (stars_score(str(x.get("stars") or "")), str(x.get("name") or "")), reverse=True)

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
            ordered_points.append({"idx": idx, "query": query, "label": marker_label(name)})
            stars = str(it.get("stars") or "").strip()
            dur = str(it.get("dur") or "").strip()
            fee = str(it.get("fee") or "").strip()
            kind = str(it.get("kind") or "").strip()
            objective = str(it.get("objective") or "").strip()
            subjective = str(it.get("subjective") or "").strip()

            md.append(f'<article class="candidate-card" data-idx="{idx}">')
            md.append('<div class="candidate-top">')
            md.append('<div class="candidate-title">')
            md.append(f'<span class="candidate-index">{idx}</span>')
            md.append(spot_html(name, query))
            md.append(f' <a href="{build_gimages_link(query)}" target="_blank" rel="noopener noreferrer">📷</a>')
            md.append('<span class="candidate-actions">')
            md.append('<button class="candidate-pillbtn must" type="button">必去</button>')
            md.append('<button class="candidate-pillbtn avoid" type="button">不想去</button>')
            md.append('</span>')
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
            md.append("</div>")

            md.append('<div class="candidate-desc">')
            if objective:
                md.append('<div>')
                md.append('<div class="candidate-desc-title">客观内容介绍</div>')
                md.append(f'<div class="candidate-desc-body">{escape(objective)}</div>')
                md.append("</div>")
            if subjective:
                md.append('<div>')
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
    md.append("- 你也可以直接说：**“你直接决定，不用我选”**，我会按亲子度假节奏给出 7 日可执行行程。")
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

    (outputs_dir / "Trip_Candidates_Bali_Family_7D.md").write_text(markdown, encoding="utf-8")
    (outputs_dir / "Trip_Candidates_Bali_Family_7D.html").write_text(html_out, encoding="utf-8")


if __name__ == "__main__":
    main()
