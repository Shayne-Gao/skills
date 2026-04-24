import json
from pathlib import Path
from datetime import datetime


def build_amap_link(query: str) -> str:
    q = query.replace(" ", "+")
    return f"https://ditu.amap.com/search?query={q}"


def spot(name: str) -> str:
    link = build_amap_link(name)
    return f"[{name}]({link}) [🗺️]({link})"


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    template_path = base_dir / "template.html"
    outputs_dir = base_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    destination = "天津市蓟州区"
    trip_title = "天津蓟州 2 日亲子+长辈友好行程（五一假期）"

    user_profile = {
        "目的地": "天津蓟州",
        "天数": "2 天",
        "人群": "2 位老人 + 2 个孩子（亲子 + 长辈友好）",
        "节奏": "休闲（强制降级：每天留出休息与弹性时间）",
        "时间": "五一假期（人多，建议提前预约/错峰）",
        "假设": "默认自驾或打车；若公共交通出行，按实际站点再微调",
    }

    day1_points = [
        f"{destination}独乐寺",
        f"{destination}白塔寺",
        f"{destination}渔阳古镇",
        f"{destination}府君山",
        f"{destination}于桥水库",
    ]

    day2_points = [
        f"{destination}盘山风景名胜区",
        f"{destination}郭家沟",
        f"{destination}黄崖关长城",
        f"{destination}九山顶",
    ]

    initial_days = [day1_points, day2_points]

    attraction_pool = [
        f"{destination}独乐寺",
        f"{destination}白塔寺",
        f"{destination}渔阳古镇",
        f"{destination}于桥水库",
        f"{destination}盘山风景名胜区",
        f"{destination}黄崖关长城",
        f"{destination}九山顶",
        f"{destination}八仙山",
        f"{destination}车神架",
        f"{destination}梨木台",
        f"{destination}郭家沟",
        f"{destination}天津蓟州国家地质公园",
        f"{destination}吉祥寺",
        f"{destination}万佛寺",
        f"{destination}玉龙滑雪场",
        f"{destination}翠屏湖",
        f"{destination}蓟州文庙",
        f"{destination}鼓楼",
        f"{destination}渔阳鼓楼",
        f"{destination}翠屏山",
        f"{destination}盘山烈士陵园",
    ]

    extras = [
        {
            "type": "food",
            "name": "蓟州板栗（现炒/礼盒）",
            "image": "https://upload.wikimedia.org/wikipedia/commons/5/57/Roasted_chestnuts.jpg",
            "price": "¥15-40/袋；¥60-180/礼盒",
            "desc": "蓟州山区特产，香甜粉糯，现炒适合边走边吃，礼盒适合带回。",
            "where": f"{destination}渔阳古镇/城区商超",
            "tags": ["特产", "亲子友好"],
            "mapUrl": build_amap_link(f"{destination} 板栗"),
        },
        {
            "type": "food",
            "name": "山楂制品（山楂糕/山楂条）",
            "image": "https://upload.wikimedia.org/wikipedia/commons/5/52/Hawthorn_fruit.jpg",
            "price": "¥10-35/袋",
            "desc": "酸甜开胃，适合小朋友；建议选配料表干净的品牌。",
            "where": f"{destination}渔阳古镇/特产店",
            "tags": ["零食", "开胃"],
            "mapUrl": build_amap_link(f"{destination} 山楂糕"),
        },
        {
            "type": "food",
            "name": "农家炖柴鸡/炖鱼（山里一桌菜）",
            "image": "https://upload.wikimedia.org/wikipedia/commons/3/35/Chicken_stew.jpg",
            "price": "¥80-180/份（视人数）",
            "desc": "适合家庭聚餐，口味偏家常；五一建议提前订位，尽量避开高峰。",
            "where": f"{destination}盘山/黄崖关周边农家院",
            "tags": ["正餐", "家庭"],
            "mapUrl": build_amap_link(f"{destination} 农家院"),
        },
        {
            "type": "souvenir",
            "name": "柿饼/果干（季节性）",
            "image": "https://upload.wikimedia.org/wikipedia/commons/0/0e/Hoshigaki.jpg",
            "price": "¥30-120/盒",
            "desc": "甜口伴手礼，适合送长辈；注意是否添加糖分与防腐剂。",
            "where": f"{destination}渔阳古镇/城区特产店",
            "tags": ["伴手礼", "季节性"],
            "mapUrl": build_amap_link(f"{destination} 柿饼"),
        },
        {
            "type": "souvenir",
            "name": "文创冰箱贴/纪念章（景区纪念）",
            "image": "https://upload.wikimedia.org/wikipedia/commons/0/0d/Fridge_magnets.jpg",
            "price": "¥15-60/个",
            "desc": "轻便好带，适合孩子收集；建议在景区官方文创店购买。",
            "where": f"{destination}盘山风景名胜区/黄崖关长城",
            "tags": ["文创", "轻便"],
            "mapUrl": build_amap_link(f"{destination} 文创店"),
        },
        {
            "type": "souvenir",
            "name": "手作糖葫芦/小食（现做）",
            "image": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Tanghulu.jpg",
            "price": "¥8-25/串",
            "desc": "小朋友很喜欢，注意牙口与糖分；建议饭后少量。",
            "where": f"{destination}渔阳古镇",
            "tags": ["亲子", "现做"],
            "mapUrl": build_amap_link(f"{destination} 糖葫芦"),
        },
    ]

    md: list[str] = []
    md.append(f"# {trip_title}")
    md.append("")
    md.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    md.append("")

    md.append("## 第一步：关键信息（已收集）")
    md.append("")
    for k, v in user_profile.items():
        md.append(f"- {k}：{v}")
    md.append("")

    md.append("## 第二步：蓟州 20+ 景点备选清单（按区域聚合）")
    md.append("")
    md.append("| 序号 | 所属区域 | 景点名称与地图导航 | 推荐度 | 游览耗时 | 门票花费 | 类型 | 备注 |")
    md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    def area_of(name: str) -> str:
        if "盘山" in name:
            return "盘山片区"
        if "黄崖关" in name or "长城" in name:
            return "黄崖关片区"
        if "溶洞" in name:
            return "北部山景/溶洞"
        if "于桥" in name or "翠屏" in name:
            return "水库湖景"
        if "渔阳" in name or "鼓楼" in name or "文庙" in name:
            return "城区/古镇"
        if "八仙山" in name or "九山顶" in name or "梨木台" in name or "车神架" in name:
            return "北部山景"
        return "蓟州其他"

    def stars(name: str) -> str:
        if any(k in name for k in ["盘山风景名胜区", "黄崖关长城", "独乐寺"]):
            return "★★★★★"
        if any(k in name for k in ["于桥水库", "渔阳古镇", "蓟州溶洞"]):
            return "★★★★☆"
        return "★★★☆☆"

    def duration(name: str) -> str:
        if "盘山" in name or "黄崖关" in name:
            return "3-5 小时"
        if "溶洞" in name:
            return "1.5-2.5 小时"
        if "于桥水库" in name or "翠屏" in name:
            return "1-2 小时"
        return "1-2 小时"

    def ticket(name: str) -> str:
        if any(k in name for k in ["盘山风景名胜区", "黄崖关长城", "蓟州溶洞", "九山顶", "八仙山", "梨木台", "车神架"]):
            return "多为收费（以现场/官方为准）"
        return "可能免费或低门槛（以现场为准）"

    def kind(name: str) -> str:
        if any(k in name for k in ["寺", "文庙"]):
            return "人文/古建"
        if any(k in name for k in ["古镇", "鼓楼"]):
            return "人文/街区"
        if any(k in name for k in ["水库", "湖"]):
            return "自然/湖景"
        if any(k in name for k in ["溶洞"]):
            return "自然/溶洞"
        if any(k in name for k in ["长城"]):
            return "人文/户外"
        return "自然/山景"

    for i, name in enumerate(attraction_pool, 1):
        area = area_of(name)
        md.append(
            f"| {i} | {area} | {spot(name)} | {stars(name)} | {duration(name)} | {ticket(name)} | {kind(name)} | 五一人多建议早到/预约 |"
        )

    md.append("")
    md.append("我将按你的授权直接做主安排行程（亲子 + 长辈友好，五一假期偏休闲、可随时截断）。")
    md.append("")

    md.append("## 第四步：行程编排原则（本次采用）")
    md.append("")
    md.append("- 每天主线不超过 4-5 个点，午间安排休息/缓冲")
    md.append("- 山景优先选择“缆车/观光车可替代爬坡”的景区，降低老人强度")
    md.append("- 五一尽量错峰：热门景区尽量早到，避开 11:00-15:00 高峰")
    md.append("")

    md.append("## 第五步：2 日行程表（可直接执行）")
    md.append("")
    md.append("| 日期（天） | 时间段 | 游览景点与具体安排 | 交通方式、距离与耗时 | 餐饮建议 | 住宿区域 |")
    md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")

    md.append(
        f"| **Day 1** | 09:30-11:00 | {spot(day1_points[0])}（古建+寺庙，轻松逛） | 打车/自驾：城区内短途（约10-20分钟） | 简单早餐后出发 | 蓟州城区 |"
    )
    md.append(
        f"| **Day 1** | 11:10-11:40 | {spot(day1_points[1])}（近距离快览） | 短途：约2-5公里/10-15分钟 | - | 蓟州城区 |"
    )
    md.append(
        f"| **Day 1** | 12:00-14:00 | {spot(day1_points[2])}（古镇街区+午餐+休息） | 短途：约10-20分钟 | 古镇内小吃/家常菜 | 蓟州城区 |"
    )
    md.append(
        f"| **Day 1** | 14:30-16:00 | {spot(day1_points[3])}（轻量登高可选，体力不足可只在山脚拍照） | 打车：约10-20分钟 | 下午茶/补水 | 蓟州城区 |"
    )
    md.append(
        f"| **Day 1** | 16:30-18:00 | {spot(day1_points[4])}（湖景散步，孩子放电） | 自驾/打车：约20-35分钟 | 晚餐回城解决 | 蓟州城区（方便次日出发） |"
    )

    md.append(
        f"| **Day 2** | 08:30-13:00 | {spot(day2_points[0])}（建议选缆车/观光车路线，减少爬坡） | 自驾/打车：约30-60分钟（视酒店位置） | 景区简餐/自带零食 | - |"
    )
    md.append(
        f"| **Day 2** | 13:40-15:30 | {spot(day2_points[1])}（山村漫步+拍照打卡，老人小孩都能走） | 车程：约20-40分钟 | - | - |"
    )
    md.append(
        f"| **Day 2** | 16:10-18:10 | {spot(day2_points[2])}（长城段落轻走，老人可只看观景台） | 车程：约30-60分钟 | 提前吃点垫肚子 | - |"
    )
    md.append(
        f"| **Day 2** | 18:30-19:30 | {spot(day2_points[3])}（日落视情况可选，体力不足可跳过） | 车程：约20-40分钟 | 返程前简餐 | 返程/结束 |"
    )

    md.append("")
    md.append("## 第五点五步：美食与伴手礼")
    md.append("")
    for item in extras:
        md.append(f"- {item['name']}（{item['price']}）：{item['desc']}｜推荐：{item['where']}｜[🗺️]({item['mapUrl']})")

    md.append("")
    md.append("## 附录：本行程点位（用于地图定位）")
    md.append("")
    idx = 1
    for day in initial_days:
        for n in day:
            md.append(f"{idx}. [{n}]({build_amap_link(n)})")
            idx += 1

    markdown = "\n".join(md) + "\n"

    template = template_path.read_text(encoding="utf-8")
    html = (
        template.replace("MARKDOWN_CONTENT_JSON", json.dumps(markdown, ensure_ascii=False))
        .replace("INITIAL_DAYS_JSON", json.dumps(initial_days, ensure_ascii=False))
        .replace("EXTRAS_JSON", json.dumps(extras, ensure_ascii=False))
    )

    (outputs_dir / "Trip_Plan_Tianjin_Jizhou_Family_2D.md").write_text(markdown, encoding="utf-8")
    (outputs_dir / "Trip_Plan_Tianjin_Jizhou_Family_2D.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
