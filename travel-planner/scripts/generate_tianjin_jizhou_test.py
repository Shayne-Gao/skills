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

    trip_title = "天津蓟州测试行程（用于 HTML 稳定性验证）"

    day1_points = [
        "天津市蓟州区独乐寺",
        "天津市蓟州区白塔寺",
        "天津市蓟州区渔阳古镇",
        "天津市蓟州区盘山风景名胜区",
        "天津市蓟州区府君山",
        "天津市蓟州区玉龙滑雪场",
        "天津市蓟州区黄崖关长城",
        "天津市蓟州区九山顶",
        "天津市蓟州区八仙山",
        "天津市蓟州区于桥水库",
    ]

    initial_days = [day1_points]

    md_lines: list[str] = []
    md_lines.append(f"# {trip_title}")
    md_lines.append("")
    md_lines.append("说明：这是一个仅用于验证单文件 HTML（地图定位/连线/不漂移/内外链分离）的测试行程。")
    md_lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    md_lines.append("")
    md_lines.append("| 日期（天） | 时间段 | 游览景点与具体安排 | 交通方式、距离与耗时 | 餐饮建议 | 住宿区域 |")
    md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")

    md_lines.append(
        "| **Day 1** | 09:00-10:00 | "
        + spot("天津市蓟州区独乐寺")
        + "（古建+佛寺） | 蓟州城区内短途打车/步行 | 城区早餐 | 蓟州城区 |"
    )
    md_lines.append(
        "| **Day 1** | 10:00-10:30 | "
        + spot("天津市蓟州区白塔寺")
        + "（寺塔一带快览） | 城区内短途 | - | 蓟州城区 |"
    )
    md_lines.append(
        "| **Day 1** | 10:40-11:30 | "
        + spot("天津市蓟州区渔阳古镇")
        + "（古镇街区） | 城区内短途 | 小吃随缘 | 蓟州城区 |"
    )
    md_lines.append(
        "| **Day 1** | 12:30-15:30 | "
        + spot("天津市蓟州区盘山风景名胜区")
        + "（主景区游览） | 打车/自驾：城区 → 盘山 | 景区附近简餐 | 蓟州城区 |"
    )
    md_lines.append(
        "| **Day 1** | 15:50-16:30 | "
        + spot("天津市蓟州区府君山")
        + "（山景观景点） | 短途车程 | - | 蓟州城区 |"
    )
    md_lines.append(
        "| **Day 1** | 16:40-17:20 | "
        + spot("天津市蓟州区玉龙滑雪场")
        + "（夏季也可作为地标点位测试） | 短途车程 | - | 蓟州城区 |"
    )
    md_lines.append(
        "| **Day 1** | 18:00-19:00 | "
        + spot("天津市蓟州区黄崖关长城")
        + "（长城段落/观景） | 自驾/打车：山区路段注意时间 | 山区简餐 | 蓟州城区 |"
    )
    md_lines.append(
        "| **Day 1** | 19:10-19:40 | "
        + spot("天津市蓟州区九山顶")
        + "（山峰地标） | 山区短途 | - | 蓟州城区 |"
    )
    md_lines.append(
        "| **Day 1** | 19:50-20:20 | "
        + spot("天津市蓟州区八仙山")
        + "（山峰地标） | 山区短途 | - | 蓟州城区 |"
    )
    md_lines.append(
        "| **Day 1** | 20:40-21:20 | "
        + spot("天津市蓟州区于桥水库")
        + "（水库夜景/收尾） | 返回途中顺路 | 晚餐返城解决 | - |"
    )

    md_lines.append("")
    md_lines.append("## 附录：本行程点位（用于地图定位）")
    md_lines.append("")
    for i, n in enumerate(day1_points, 1):
        md_lines.append(f"{i}. [{n}]({build_amap_link(n)})")

    markdown = "\n".join(md_lines) + "\n"

    template = template_path.read_text(encoding="utf-8")
    html = (
        template.replace("MARKDOWN_CONTENT_JSON", json.dumps(markdown, ensure_ascii=False))
        .replace("INITIAL_DAYS_JSON", json.dumps(initial_days, ensure_ascii=False))
    )

    (outputs_dir / "Trip_Plan_Tianjin_Jizhou_Test.md").write_text(markdown, encoding="utf-8")
    (outputs_dir / "Trip_Plan_Tianjin_Jizhou_Test.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()

