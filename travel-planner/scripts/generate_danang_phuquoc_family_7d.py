import json
from pathlib import Path
from datetime import datetime
from typing import Optional


def build_gmaps_link(query: str) -> str:
    q = query.replace(" ", "+")
    return f"https://www.google.com/maps/search/?api=1&query={q}"


def spot(name: str, query: Optional[str] = None) -> str:
    q = query or name
    link = build_gmaps_link(q)
    return f"[{name}]({link}) [🗺️]({link})"


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    template_path = base_dir / "template_intl.html"
    outputs_dir = base_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    trip_title = "岘港 + 富国岛 7 日亲子度假行程（两大两小：8 岁 / 6 岁）"

    user_profile = {
        "目的地": "越南｜岘港（含会安） + 富国岛",
        "天数": "7 天游玩",
        "同行人员": "2 大 2 小（8 岁、6 岁）",
        "节奏": "度假为主：每天 1-2 个主点 + 午休/泳池时间",
        "交通": "岘港/会安：打车或包车；富国岛：打车为主（亲子省心）",
        "住宿": "建议岘港 4 晚（市区/美溪海滩一带）+ 富国岛 3 晚（长滩/中区或北部 Vin 区）",
        "备注": "旺季与节假日请提前预订：巴拿山/主题乐园门票与酒店",
    }

    day1_points = [
        "My Khe Beach, Da Nang",
        "Dragon Bridge, Da Nang",
        "Han Market, Da Nang",
    ]
    day2_points = [
        "Marble Mountains, Da Nang",
        "Linh Ung Pagoda (Lady Buddha), Da Nang",
        "My Khe Beach, Da Nang",
    ]
    day3_points = [
        "Ba Na Hills, Da Nang",
        "Golden Bridge, Ba Na Hills",
    ]
    day4_points = [
        "Hoi An Ancient Town, Hoi An",
        "Hoi An Night Market, Hoi An",
        "An Bang Beach, Hoi An",
    ]
    day5_points = [
        "Phu Quoc Night Market, Phu Quoc",
        "Dinh Cau Temple, Phu Quoc",
        "Long Beach (Bai Truong), Phu Quoc",
    ]
    day6_points = [
        "VinWonders Phu Quoc",
        "Vinpearl Safari Phu Quoc",
    ]
    day7_points = [
        "Sao Beach, Phu Quoc",
        "Sunset Town, An Thoi, Phu Quoc",
        "Hon Thom Cable Car, Phu Quoc",
    ]

    initial_days = [
        day1_points,
        day2_points,
        day3_points,
        day4_points,
        day5_points,
        day6_points,
        day7_points,
    ]

    extras = [
        {
            "type": "food",
            "name": "越南河粉 Pho（岘港/富国岛都适合）",
            "image": "https://upload.wikimedia.org/wikipedia/commons/5/5f/Pho-Bo-Hanoi.jpg",
            "price": "₫35,000-80,000/碗",
            "desc": "清爽汤底、接受度高，孩子也容易吃。可以当早餐或正餐。",
            "where": "岘港市区/会安古城周边；富国岛夜市附近",
            "tags": ["亲子友好", "主食"],
            "mapUrl": build_gmaps_link("Pho restaurant Da Nang"),
        },
        {
            "type": "food",
            "name": "越南法棍 Bánh mì（加餐首选）",
            "image": "https://upload.wikimedia.org/wikipedia/commons/8/8d/Banh_mi_thit.jpg",
            "price": "₫20,000-45,000/个",
            "desc": "携带方便、适合孩子补能量；注意酱料可让店家少放。",
            "where": "岘港市区；会安古城；富国岛夜市周边",
            "tags": ["加餐", "便携"],
            "mapUrl": build_gmaps_link("Banh mi Da Nang"),
        },
        {
            "type": "food",
            "name": "岘港海鲜（清蒸/烤虾更适合带娃）",
            "image": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Grilled_shrimp.jpg",
            "price": "₫250,000-600,000/餐（视人数）",
            "desc": "选清蒸/烤制更稳；让店家少辣少油，孩子更容易接受。",
            "where": "岘港海边餐厅（美溪海滩一带）",
            "tags": ["晚餐", "家庭"],
            "mapUrl": build_gmaps_link("Seafood My Khe Beach Da Nang"),
        },
        {
            "type": "food",
            "name": "会安鸡饭 Cơm gà Hội An",
            "image": "https://upload.wikimedia.org/wikipedia/commons/1/10/Hainanese_chicken_rice.jpg",
            "price": "₫45,000-90,000/份",
            "desc": "口味温和、配菜丰富，适合亲子；不吃辣可提前说明。",
            "where": "会安古城内",
            "tags": ["亲子友好", "主食"],
            "mapUrl": build_gmaps_link("Com ga Hoi An"),
        },
        {
            "type": "food",
            "name": "越南滴漏咖啡（大人能量补给）",
            "image": "https://upload.wikimedia.org/wikipedia/commons/0/0c/Vietnamese_iced_coffee.jpg",
            "price": "₫25,000-60,000/杯",
            "desc": "香浓偏甜，冰咖适合热天；孩子可选椰子/果汁替代。",
            "where": "岘港/会安咖啡馆；富国岛长滩周边",
            "tags": ["咖啡", "大人友好"],
            "mapUrl": build_gmaps_link("Vietnamese coffee Da Nang"),
        },
        {
            "type": "souvenir",
            "name": "腰果/咖啡豆（越南常见伴手礼）",
            "image": "https://upload.wikimedia.org/wikipedia/commons/8/8a/Cashew_nuts.jpg",
            "price": "₫80,000-250,000/袋",
            "desc": "更适合带回分发；注意选择密封包装与生产日期新鲜的。",
            "where": "岘港韩市场；富国岛夜市与超市",
            "tags": ["伴手礼", "零食"],
            "mapUrl": build_gmaps_link("Han Market cashew Da Nang"),
        },
        {
            "type": "souvenir",
            "name": "会安灯笼（装饰类纪念品）",
            "image": "https://upload.wikimedia.org/wikipedia/commons/2/2b/Hoi_An_lanterns.jpg",
            "price": "₫50,000-200,000/个",
            "desc": "会安标志性手作，适合当装饰纪念；带回注意压扁与防潮。",
            "where": "会安古城与夜市",
            "tags": ["手作", "装饰"],
            "mapUrl": build_gmaps_link("Hoi An lantern shop"),
        },
        {
            "type": "souvenir",
            "name": "富国岛胡椒（Phu Quoc Pepper）",
            "image": "https://upload.wikimedia.org/wikipedia/commons/1/1c/Black_pepper.jpg",
            "price": "₫80,000-220,000/袋",
            "desc": "富国岛特产之一，香气更足；适合带回做菜或送亲友。",
            "where": "富国岛胡椒农场/超市",
            "tags": ["特产", "调味"],
            "mapUrl": build_gmaps_link("Pepper farm Phu Quoc"),
        },
        {
            "type": "souvenir",
            "name": "鱼露（挑小瓶密封装更好带）",
            "image": "https://upload.wikimedia.org/wikipedia/commons/2/2a/Fish_sauce.jpg",
            "price": "₫60,000-180,000/瓶",
            "desc": "越南料理灵魂调味；建议选小瓶/礼盒装并做好托运行李防漏。",
            "where": "富国岛夜市/超市",
            "tags": ["特产", "托运"],
            "mapUrl": build_gmaps_link("Fish sauce Phu Quoc"),
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

    md.append("## 第二步：20+ 景点备选清单（按区域聚合，便于你后续微调）")
    md.append("")
    md.append("| 序号 | 所属区域 | 景点名称与地图导航 | 客观内容介绍 | 主观评价建议 | 推荐度 | 游览耗时 | 门票花费 | 类型 |")
    md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    pool = [
        (
            "岘港-海滩",
            "My Khe Beach, Da Nang",
            "岘港最有名的城市海滩之一，沙滩很长、配套成熟，适合玩沙、踏浪、堆沙堡与海边散步；傍晚的风更舒服。",
            "把它当作“每天固定放电点”最稳：建议早晚去，中午太阳强就回酒店泳池；给孩子备防晒、沙滩鞋与替换衣物。",
            "★★★★★",
            "2-4h",
            "免费",
            "海滩",
        ),
        (
            "岘港-地标",
            "Dragon Bridge, Da Nang",
            "跨越汉江的龙形大桥，是岘港夜景地标；周边河畔步道适合散步拍照，夜间氛围热闹。",
            "更适合“饭后顺路短打卡”，不建议带娃久站；周末喷火喷水通常更拥挤，提前占位并注意车流安全。",
            "★★★★☆",
            "0.5-1.5h",
            "免费",
            "城市地标",
        ),
        (
            "岘港-购物",
            "Han Market, Da Nang",
            "本地综合市场，常见咖啡、干果、零食、海产干货与纪念品；室内摊位密集，烟火气很足。",
            "适合“集中买伴手礼+补给”，但人多容易走散；建议白天去、目标清单化采购，带娃就控制在 1 小时内。",
            "★★★☆☆",
            "1-2h",
            "免费",
            "市场/购物",
        ),
        (
            "岘港-自然",
            "Son Tra Peninsula, Da Nang",
            "山茶半岛是岘港的山海观景区，沿途有海湾视角与观景点，风景好但路弯较多、车程相对更长。",
            "如果孩子容易晕车，建议只选 1-2 个观景点短线；更推荐清晨或傍晚出发，避开中午暴晒与拥堵。",
            "★★★★☆",
            "2-4h",
            "免费",
            "自然/观景",
        ),
        (
            "岘港-寺庙",
            "Linh Ung Pagoda (Lady Buddha), Da Nang",
            "灵应寺与“观音像”所在的观景点，步行距离不长，视野开阔，可以俯瞰海岸线与城市轮廓。",
            "亲子友好、强度低，适合当半岛行程的核心停留点；注意着装与防晒，尽量避开正午高温时段。",
            "★★★★☆",
            "1-2h",
            "免费",
            "寺庙/观景",
        ),
        (
            "岘港-洞穴",
            "Marble Mountains, Da Nang",
            "五行山由石灰岩山体与洞穴寺庙构成，能体验“探洞+观景+小爬坡”；部分路段台阶多、洞内湿滑。",
            "6 岁也能玩但要控强度：挑主洞穴+观景台即可；穿防滑鞋、带驱蚊，雨后更滑时优先走安全路线。",
            "★★★★☆",
            "2-3h",
            "付费",
            "洞穴/寺庙",
        ),
        (
            "岘港-亲子",
            "Sun World Asia Park, Da Nang",
            "城市里的游乐园与摩天轮综合体，项目覆盖亲子游乐与拍照点，适合小学年龄段放松玩半天。",
            "建议傍晚入园更凉快、体验更好；如果当天已经走了不少路，就把它作为“轻松补充”而不是主线。",
            "★★★★☆",
            "3-5h",
            "付费",
            "游乐园",
        ),
        (
            "岘港-日游",
            "Ba Na Hills, Da Nang",
            "巴拿山需要缆车上山，集金桥、法式小镇、花园与娱乐项目于一体，景观与体验都更“主题化”。",
            "这是亲子高光日：务必早出发、预留排队时间；给孩子带薄外套（山上温差）与零食水，避免太晚回城。",
            "★★★★★",
            "6-9h",
            "较贵",
            "缆车/主题景区",
        ),
        (
            "岘港-日游",
            "Golden Bridge, Ba Na Hills",
            "金桥是巴拿山的标志性景观步道，视野与照片效果很好；通常与巴拿山同日游览，不单独成行。",
            "早到能避开人潮、拍照更轻松；带娃建议先打卡金桥再去其他区域，避免孩子后面体力下滑导致情绪崩。",
            "★★★★★",
            "0.5-1.5h",
            "含在门票",
            "景观/打卡",
        ),
        (
            "会安-古城",
            "Hoi An Ancient Town, Hoi An",
            "会安古城以黄墙老街、河畔与灯笼夜景出名，适合慢逛拍照、吃小吃、体验手作；夜晚氛围最强。",
            "强烈建议傍晚到夜间安排：白天太热就先午休；带娃注意人流密度，提前约定集合点并尽量早些回酒店。",
            "★★★★★",
            "3-5h",
            "通票",
            "古城/夜景",
        ),
        (
            "会安-夜市",
            "Hoi An Night Market, Hoi An",
            "古城附近的夜市与灯笼摊集中，适合买小纪念品、逛吃与拍灯笼街景，整体步行体验很好。",
            "建议把“逛夜市”当作会安行程的收尾：先吃正餐再逛更不容易踩坑；带娃别买太多零散易丢物品。",
            "★★★★☆",
            "1-2h",
            "免费",
            "夜市",
        ),
        (
            "会安-海滩",
            "An Bang Beach, Hoi An",
            "会安附近更休闲的海滩，氛围比城市海滩安静，适合玩沙、海边咖啡馆歇脚、随时撤退。",
            "适合作为“会安半日+放电”组合点；如果当天夜里逛古城很晚，次日就把这里当作轻松恢复日。",
            "★★★★☆",
            "2-4h",
            "免费",
            "海滩",
        ),
        (
            "会安-体验",
            "Cam Thanh Coconut Village, Hoi An",
            "椰林水道的簸箕船体验，互动性强、孩子参与感高，通常包含短航程与简单表演/体验环节。",
            "商业化比较重，建议提前选口碑团、明确包含项目与价格；娃如果怕晃或怕水，就选更平稳的船程版本。",
            "★★★★☆",
            "1.5-2.5h",
            "付费",
            "亲子体验",
        ),
        (
            "富国岛-海滩",
            "Long Beach (Bai Truong), Phu Quoc",
            "富国岛最成熟的酒店海滩带，餐饮与便利店选择多，适合“住着玩”：海边散步、泳池、日落都方便。",
            "如果你们更看重省心与机动性，优先把酒店定在这一区域；每天保留午休/泳池时间，体验会明显更像度假。",
            "★★★★★",
            "2-4h",
            "免费",
            "海滩/度假",
        ),
        (
            "富国岛-海滩",
            "Sao Beach, Phu Quoc",
            "星沙海滩以更白的沙与更“海岛感”的颜色出名，适合拍照、玩沙和浅水区戏水，通常要打车前往。",
            "建议上午去：光线更好、人也相对少；如果当天计划再去日落小镇，就别把上午玩得太狠，留体力给下午。",
            "★★★★★",
            "3-5h",
            "免费/消费",
            "海滩",
        ),
        (
            "富国岛-主题",
            "VinWonders Phu Quoc",
            "大型主题乐园，项目丰富，适合 6-12 岁玩一整天；园区很大，走路与排队强度都不低。",
            "旺季建议早入园并先攻最想玩的项目；如果你们不想太累，可以把它拆成“半天+回酒店午休”再决定是否二刷。",
            "★★★★★",
            "6-9h",
            "较贵",
            "主题乐园",
        ),
        (
            "富国岛-动物",
            "Vinpearl Safari Phu Quoc",
            "亲子向动物园，包含步行区与观光车区，孩子能近距离看动物，整体体验偏“轻松科普”。",
            "更适合安排在上午，避开高温；带好防晒、驱蚊与水。若只能二选一，怕累就优先 Safari（更轻松）。",
            "★★★★★",
            "4-7h",
            "较贵",
            "动物园",
        ),
        (
            "富国岛-日落",
            "Sunset Town, An Thoi, Phu Quoc",
            "安泰一带的日落小镇，建筑风格出片，适合傍晚散步、看日落与吃晚饭；整体偏商业街区体验。",
            "非常适合作为“最后一天轻松收尾”：不赶时间、随时可撤；如果孩子当天已经玩累，就只保留日落+晚餐即可。",
            "★★★★☆",
            "2-4h",
            "免费/消费",
            "日落街区",
        ),
        (
            "富国岛-缆车",
            "Hon Thom Cable Car, Phu Quoc",
            "跨海缆车是富国岛特色体验，视野开阔、孩子通常会兴奋；但受天气与风浪影响，可能临时调整。",
            "建议把它安排在“天气更稳定的一天”，并给出替代方案（星沙海滩/酒店躺平）；恐高的小朋友要提前沟通。",
            "★★★★☆",
            "4-7h",
            "付费",
            "缆车/海岛",
        ),
        (
            "富国岛-夜市",
            "Phu Quoc Night Market, Phu Quoc",
            "夜市集合海鲜烧烤、小吃与小纪念品，适合晚饭后散步觅食；人流密集，热闹但也更嘈杂。",
            "亲子建议早点去：18:00-19:30 更友好；点海鲜时优先选熟食与清淡口味，避免太辣或生冷导致肠胃不适。",
            "★★★★☆",
            "1-2h",
            "免费",
            "夜市/小吃",
        ),
        (
            "富国岛-地标",
            "Dinh Cau Temple, Phu Quoc",
            "海边小庙与礁石观景点，常被当作日落顺路打卡；步行距离短，适合拍照与短暂停留。",
            "不必专程去，更适合作为夜市前后的“顺路补点”；带娃注意礁石边缘防滑与海风较大。",
            "★★★☆☆",
            "0.5-1h",
            "免费",
            "小寺庙/观景",
        ),
    ]

    for i, (area, name, objective, subjective, stars, dur, fee, kind) in enumerate(pool, 1):
        md.append(f"| {i} | {area} | {spot(name)} | {objective} | {subjective} | {stars} | {dur} | {fee} | {kind} |")

    md.append("")
    md.append("我将按你的授权直接做主安排行程（亲子度假节奏：每天 1-2 个主点 + 午休/泳池）。")
    md.append("")

    md.append("## 第四步：行程编排原则（本次采用）")
    md.append("")
    md.append("- 每天 1 个主景点 + 1 个轻松点；中午安排午休/回酒店")
    md.append("- 大景区（日票）分散到不同天，避免孩子过度疲劳")
    md.append("- 海滩/泳池时间作为“固定内容”，并预留弹性应对天气")
    md.append("- 城市间移动日尽量轻松，晚上以夜市/散步为主")
    md.append("")

    md.append("## 第五步：7 日行程表（可直接执行）")
    md.append("")
    md.append("| 日期（天） | 时间段 | 游览景点与具体安排 | 交通方式、距离与耗时 | 餐饮建议 | 住宿区域 |")
    md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")

    md.append(f"| **Day 1（岘港）** | 下午-傍晚 | {spot('My Khe Beach（美溪海滩）', 'My Khe Beach Da Nang')} 沙滩放电 + 日落散步 | 机场/酒店打车：约15-30分钟（视酒店） | 海边简餐/水果 | 岘港：美溪海滩一带 |")
    md.append(f"| **Day 1（岘港）** | 晚上 | {spot('Dragon Bridge（龙桥）', 'Dragon Bridge Da Nang')} 夜景打卡（周末可看喷火喷水） | 打车：约10-20分钟 | 亲子友好餐厅（不辣为主） | 岘港：美溪海滩一带 |")

    md.append(f"| **Day 2（岘港）** | 上午 | {spot('Marble Mountains（五行山）', 'Marble Mountains Da Nang')} 洞穴+寺庙轻探险（控强度） | 打车：约20-35分钟 | - | 岘港：美溪海滩一带 |")
    md.append(f"| **Day 2（岘港）** | 午间 | 回酒店午休/泳池时间 | 打车回程：约20-35分钟 | 酒店简餐/外卖 | 岘港：美溪海滩一带 |")
    md.append(f"| **Day 2（岘港）** | 傍晚 | {spot('Linh Ung Pagoda（灵应寺/观音像）', 'Linh Ung Pagoda Lady Buddha Da Nang')} 观景 + 轻松散步 | 打车：约25-45分钟 | 早些吃晚饭避免太晚 | 岘港：美溪海滩一带 |")

    md.append(f"| **Day 3（岘港）** | 全天 | {spot('Ba Na Hills（巴拿山）', 'Ba Na Hills')} + {spot('Golden Bridge（金桥）', 'Golden Bridge Ba Na Hills')}（亲子高光日） | 包车/打车：单程约45-70分钟 | 景区简餐 + 随身零食/水 | 岘港：美溪海滩一带 |")

    md.append(f"| **Day 4（会安往返）** | 下午-夜间 | {spot('Hoi An Ancient Town（会安古城）', 'Hoi An Ancient Town')} + {spot('Hoi An Night Market（会安夜市）', 'Hoi An Night Market')}（灯笼夜景） | 包车/打车：单程约45-70分钟 | 会安小吃/鸡饭（不辣） | 岘港：美溪海滩一带 |")
    md.append(f"| **Day 4（会安往返）** | 傍晚前 | 视体力加点：{spot('An Bang Beach（安邦海滩）', 'An Bang Beach Hoi An')} 沙滩放电 | 打车：约10-20分钟 | - | 岘港：美溪海滩一带 |")

    md.append(f"| **Day 5（移动到富国岛）** | 下午-夜间 | 抵达后轻松：{spot('Long Beach（长滩）', 'Long Beach Phu Quoc')} 日落散步 + {spot('Phu Quoc Night Market（富国岛夜市）', 'Phu Quoc Night Market')} | 机场到酒店：约15-40分钟 | 夜市小吃/海鲜（少辣） | 富国岛：长滩一带（或北部 Vin 区） |")
    md.append(f"| **Day 5（富国岛）** | 晚上 | 顺路：{spot('Dinh Cau Temple（丁考庙）', 'Dinh Cau Temple Phu Quoc')} 小打卡 | 打车：约5-15分钟 | - | 富国岛：长滩一带（或北部 Vin 区） |")

    md.append(f"| **Day 6（富国岛）** | 全天 | 二选一或都去（看体力）：{spot('VinWonders（主题乐园）', 'VinWonders Phu Quoc')} + {spot('Vinpearl Safari（动物园）', 'Vinpearl Safari Phu Quoc')} | 打车/接驳：单程约30-60分钟（视酒店） | 园区简餐 + 随身零食/水 | 富国岛：长滩一带（或北部 Vin 区） |")

    md.append(f"| **Day 7（富国岛）** | 上午 | {spot('Sao Beach（星沙海滩）', 'Sao Beach Phu Quoc')} 纯海滩放松（亲子玩沙） | 打车：约25-50分钟 | 海边简餐/椰子水 | 富国岛：长滩一带（或北部 Vin 区） |")
    md.append(f"| **Day 7（富国岛）** | 下午-傍晚 | {spot('Hon Thom Cable Car（跨海缆车）', 'Hon Thom Cable Car Phu Quoc')} + {spot('Sunset Town（日落小镇）', 'Sunset Town An Thoi Phu Quoc')}（轻松收尾） | 打车：约25-60分钟 | 日落小镇晚餐 | 富国岛：长滩一带（或北部 Vin 区） |")

    md.append("")
    md.append("## 第五点五步：美食与伴手礼（带图片卡片展示）")
    md.append("")
    for item in extras:
        md.append(f"- {item['name']}（{item['price']}）：{item['desc']}｜推荐：{item['where']}｜[🗺️]({item['mapUrl']})")

    md.append("")
    md.append("## 附录：本行程点位（用于地图定位）")
    md.append("")
    idx = 1
    for day in initial_days:
        for n in day:
            md.append(f"{idx}. [{n}]({build_gmaps_link(n)})")
            idx += 1

    markdown = "\n".join(md) + "\n"

    template = template_path.read_text(encoding="utf-8")
    html = (
        template.replace("MARKDOWN_CONTENT_JSON", json.dumps(markdown, ensure_ascii=False))
        .replace("INITIAL_DAYS_JSON", json.dumps(initial_days, ensure_ascii=False))
        .replace("EXTRAS_JSON", json.dumps(extras, ensure_ascii=False))
    )

    (outputs_dir / "Trip_Plan_DaNang_PhuQuoc_Family_7D.md").write_text(markdown, encoding="utf-8")
    (outputs_dir / "Trip_Plan_DaNang_PhuQuoc_Family_7D.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
