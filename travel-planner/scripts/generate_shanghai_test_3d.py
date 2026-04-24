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

    trip_title = "上海 3 天游测试行程（随机 20 点，仅用于 HTML 验证）"

    day1 = [
        "上海市黄浦区外滩",
        "上海市黄浦区南京路步行街",
        "上海市黄浦区人民广场",
        "上海市黄浦区上海博物馆",
        "上海市黄浦区豫园",
        "上海市黄浦区上海城隍庙",
        "上海市黄浦区新天地",
    ]

    day2 = [
        "上海市浦东新区陆家嘴金融贸易区",
        "上海市浦东新区东方明珠广播电视塔",
        "上海市浦东新区上海中心大厦",
        "上海市浦东新区上海环球金融中心",
        "上海市浦东新区金茂大厦",
        "上海市浦东新区浦东美术馆",
        "上海市浦东新区世纪公园",
    ]

    day3 = [
        "上海市浦东新区上海迪士尼乐园",
        "上海市徐汇区武康路",
        "上海市徐汇区安福路",
        "上海市静安区静安寺",
        "上海市长宁区上海动物园",
        "上海市青浦区朱家角古镇",
    ]

    initial_days = [day1, day2, day3]
    extras = [
        {
            "type": "food",
            "name": "上海生煎",
            "image": "https://upload.wikimedia.org/wikipedia/commons/0/02/Shengjianbao.jpg",
            "price": "¥8-25/份",
            "desc": "外底酥脆、内里多汁的本帮小吃，适合当早餐或加餐。",
            "where": "上海市黄浦区/静安区等常见早餐店铺",
            "tags": ["本帮", "小吃", "早餐"],
            "mapUrl": build_amap_link("上海市黄浦区 生煎"),
        },
        {
            "type": "food",
            "name": "蟹粉小笼",
            "image": "https://upload.wikimedia.org/wikipedia/commons/7/79/Xiaolongbao.JPG",
            "price": "¥30-80/笼",
            "desc": "蟹粉与肉汁融合，建议趁热、搭配姜丝与醋。",
            "where": "上海市黄浦区/静安区 老字号点心店",
            "tags": ["点心", "季节性"],
            "mapUrl": build_amap_link("上海市黄浦区 蟹粉小笼"),
        },
        {
            "type": "food",
            "name": "本帮红烧肉",
            "image": "https://upload.wikimedia.org/wikipedia/commons/8/83/Braised_pork_belly.jpg",
            "price": "¥48-128/份",
            "desc": "甜咸口、酱香浓郁，肥而不腻，配米饭很顶。",
            "where": "上海市黄浦区/徐汇区 本帮菜馆",
            "tags": ["本帮菜", "正餐"],
            "mapUrl": build_amap_link("上海市黄浦区 本帮红烧肉"),
        },
        {
            "type": "food",
            "name": "葱油拌面",
            "image": "https://upload.wikimedia.org/wikipedia/commons/3/3d/Scallion_oil_noodles.jpg",
            "price": "¥12-35/碗",
            "desc": "葱香浓郁、口味简单但耐吃，适合快速解决一餐。",
            "where": "上海市静安区/黄浦区 面馆",
            "tags": ["面食", "快手"],
            "mapUrl": build_amap_link("上海市静安区 葱油拌面"),
        },
        {
            "type": "souvenir",
            "name": "大白兔奶糖（伴手礼）",
            "image": "https://upload.wikimedia.org/wikipedia/commons/3/3a/White_Rabbit_Creamy_Candy.jpg",
            "price": "¥15-60/盒",
            "desc": "经典上海记忆，适合送同事朋友，口味也有各种限定。",
            "where": "上海市黄浦区 南京路商圈/大型商超",
            "tags": ["零食", "经典"],
            "mapUrl": build_amap_link("上海市黄浦区 大白兔 奶糖"),
        },
        {
            "type": "souvenir",
            "name": "蝴蝶酥（伴手礼）",
            "image": "https://upload.wikimedia.org/wikipedia/commons/4/4a/Palmier_pastry.jpg",
            "price": "¥30-120/盒",
            "desc": "酥香层次多，适合带回办公室分享，注意防压碎。",
            "where": "上海市黄浦区/静安区 烘焙店",
            "tags": ["烘焙", "易碎"],
            "mapUrl": build_amap_link("上海市黄浦区 蝴蝶酥"),
        },
    ]

    md_lines: list[str] = []
    md_lines.append(f"# {trip_title}")
    md_lines.append("")
    md_lines.append("说明：仅用于验证单文件 HTML（地图定位/连线/不漂移/内外链分离）。")
    md_lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    md_lines.append("")

    md_lines.append("| 日期（天） | 时间段 | 游览景点与具体安排 | 交通方式、距离与耗时 | 餐饮建议 | 住宿区域 |")
    md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")

    md_lines.append(
        "| **Day 1** | 09:30-20:30 | "
        + " → ".join([spot(n) for n in day1])
        + " | 市内步行/地铁为主（按兴趣灵活截断） | 黄浦区小吃/咖啡 | 黄浦/静安交界 |"
    )
    md_lines.append(
        "| **Day 2** | 09:30-20:30 | "
        + " → ".join([spot(n) for n in day2])
        + " | 以地铁+步行为主（陆家嘴核心圈） | 陆家嘴商圈 | 浦东陆家嘴周边 |"
    )
    md_lines.append(
        "| **Day 3** | 09:30-20:30 | "
        + " → ".join([spot(n) for n in day3])
        + " | 远近结合：市区+郊区（按时间取舍） | 迪士尼/古镇小吃随缘 | 浦东/市区皆可 |"
    )

    md_lines.append("")
    md_lines.append("## 附录：本行程点位（用于地图定位）")
    md_lines.append("")
    idx = 1
    for day in initial_days:
        for n in day:
            md_lines.append(f"{idx}. [{n}]({build_amap_link(n)})")
            idx += 1

    markdown = "\n".join(md_lines) + "\n"

    template = template_path.read_text(encoding="utf-8")
    html = (
        template.replace("MARKDOWN_CONTENT_JSON", json.dumps(markdown, ensure_ascii=False))
        .replace("INITIAL_DAYS_JSON", json.dumps(initial_days, ensure_ascii=False))
        .replace("EXTRAS_JSON", json.dumps(extras, ensure_ascii=False))
    )

    (outputs_dir / "Trip_Plan_Shanghai_Test_3D.md").write_text(markdown, encoding="utf-8")
    (outputs_dir / "Trip_Plan_Shanghai_Test_3D.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
