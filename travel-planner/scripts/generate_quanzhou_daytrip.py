import json
from pathlib import Path
from datetime import datetime


def build_amap_link(query: str) -> str:
    q = query.replace(" ", "+")
    return f"https://ditu.amap.com/search?query={q}"


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    template_path = base_dir / "template.html"
    outputs_dir = base_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    trip_title = "泉州一日游（五店市 → 鲤城古城）"

    day1_points = [
        "泉州市晋江市五店市传统街区",
        "泉州市鲤城区西街历史文化街区",
        "泉州市鲤城区开元寺",
        "泉州市鲤城区钟楼",
        "泉州市鲤城区清净寺",
        "泉州市鲤城区泉州府文庙",
        "泉州市鲤城区通淮关岳庙",
        "泉州市鲤城区泉郡天后宫",
        "泉州市鲤城区中山中路",
    ]

    initial_days = [day1_points]

    md_lines = []
    md_lines.append(f"# {trip_title}")
    md_lines.append("")
    md_lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    md_lines.append("")
    md_lines.append("| 日期（天） | 时间段 | 游览景点与具体安排 | 交通方式、距离与耗时 | 餐饮建议 | 住宿区域 |")
    md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")

    def spot(name: str) -> str:
        link = build_amap_link(name)
        return f"[{name}]({link}) [🗺️]({link})"

    md_lines.append(
        "| **Day 1** | 09:30-11:30 | "
        + spot("泉州市晋江市五店市传统街区")
        + "（慢逛古厝街巷、拍照） | 打车/公交：市区 → 晋江；到达后步行 | 五店市周边小吃（面线糊/海蛎煎） | 鲤城/丰泽交界（方便夜逛） |"
    )
    md_lines.append(
        "| **Day 1** | 12:30-14:30 | "
        + spot("泉州市鲤城区西街历史文化街区")
        + "（西街主街+巷弄） | 打车：五店市 → 鲤城古城（约30-45分钟，视路况） | 西街小吃（姜母鸭/土笋冻） | 鲤城古城 |"
    )
    md_lines.append(
        "| **Day 1** | 14:30-15:30 | "
        + spot("泉州市鲤城区开元寺")
        + "（寺内漫步、双塔远观） | 步行：西街附近（约10-15分钟） | 轻食/咖啡歇脚 | 鲤城古城 |"
    )
    md_lines.append(
        "| **Day 1** | 15:30-16:10 | "
        + spot("泉州市鲤城区钟楼")
        + "（古城地标、拍照） | 步行：开元寺 → 钟楼（约10-15分钟） | - | 鲤城古城 |"
    )
    md_lines.append(
        "| **Day 1** | 16:10-16:40 | "
        + spot("泉州市鲤城区清净寺")
        + "（外观/庭院） | 步行：钟楼 → 清净寺（约10-12分钟） | - | 鲤城古城 |"
    )
    md_lines.append(
        "| **Day 1** | 16:40-17:20 | "
        + spot("泉州市鲤城区泉州府文庙")
        + "（牌坊/棂星门一带） | 步行：清净寺 → 文庙（约8-12分钟） | - | 鲤城古城 |"
    )
    md_lines.append(
        "| **Day 1** | 17:20-18:00 | "
        + spot("泉州市鲤城区通淮关岳庙")
        + "（香火旺、注意秩序） | 步行：文庙 → 关岳庙（约10-15分钟） | - | 鲤城古城 |"
    )
    md_lines.append(
        "| **Day 1** | 18:00-19:00 | "
        + spot("泉州市鲤城区泉郡天后宫")
        + "（傍晚更舒服） | 步行/短打车：关岳庙 → 天后宫（约10-15分钟） | 附近海鲜/闽南小馆 | 鲤城/丰泽交界 |"
    )
    md_lines.append(
        "| **Day 1** | 19:30-21:00 | "
        + spot("泉州市鲤城区中山中路")
        + "（夜逛街区、买伴手礼） | 步行：天后宫附近（约10-20分钟） | 小吃自由发挥 | 返程/住宿 |"
    )

    md_lines.append("")
    md_lines.append("## 附录：本行程点位（用于地图定位）")
    md_lines.append("")
    for i, n in enumerate(day1_points, 1):
        link = build_amap_link(n)
        md_lines.append(f"{i}. [{n}]({link})")

    markdown = "\n".join(md_lines) + "\n"

    template = template_path.read_text(encoding="utf-8")
    html = (
        template.replace("MARKDOWN_CONTENT_JSON", json.dumps(markdown, ensure_ascii=False))
        .replace("INITIAL_DAYS_JSON", json.dumps(initial_days, ensure_ascii=False))
    )

    (outputs_dir / "Trip_Plan_Quanzhou.md").write_text(markdown, encoding="utf-8")
    (outputs_dir / "Trip_Plan_Quanzhou.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()

