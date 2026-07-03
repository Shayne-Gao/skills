import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class Weights:
    char5: float
    weapon5: float
    pull: float


@dataclass(frozen=True)
class AccountResources:
    char5: int
    weapon5: int
    star_voice: int
    wave_pulls: int

    @property
    def total_pulls(self) -> float:
        return self.star_voice / 160.0 + float(self.wave_pulls)


@dataclass(frozen=True)
class Candidate:
    product_id: str
    title: str
    price: float
    resources: AccountResources

    @property
    def total_yellow(self) -> int:
        return int(self.resources.char5) + int(self.resources.weapon5)


def _now_tag() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _read_stdin_text() -> str:
    try:
        data = sys.stdin.read()
    except KeyboardInterrupt:
        raise SystemExit(130)
    return data.strip()


def _parse_range_number(s: str, range_mode: str) -> Optional[float]:
    text = str(s or "").strip()
    if not text:
        return None

    text = text.replace(",", "").replace(" ", "")
    text = re.sub(r"[＋+]", "+", text)

    m = re.findall(r"(\d+(?:\.\d+)?)", text)
    if not m:
        return None

    nums = [float(x) for x in m]
    if len(nums) == 1:
        val = nums[0]
    else:
        lo, hi = min(nums), max(nums)
        if range_mode == "max":
            val = hi
        elif range_mode == "avg":
            val = (lo + hi) / 2.0
        else:
            val = lo

    if "万" in text or re.search(r"(?i)\bw\b", text) or re.search(r"(?i)\d+w", text):
        val *= 10000.0
    return val


def _to_int(x: Optional[float]) -> int:
    if x is None or math.isnan(x):
        return 0
    return int(round(x))


def _candidate_list_from_response(obj: Any) -> List[Dict[str, Any]]:
    if isinstance(obj, dict):
        for path in [
            ("data", "list"),
            ("data", "items"),
            ("data", "result", "list"),
            ("data", "result", "items"),
            ("data", "data", "list"),
            ("data", "data", "items"),
            ("result", "list"),
            ("result", "items"),
        ]:
            cur: Any = obj
            ok = True
            for k in path:
                if not isinstance(cur, dict) or k not in cur:
                    ok = False
                    break
                cur = cur[k]
            if ok and isinstance(cur, list) and all(isinstance(x, dict) for x in cur):
                return cur

    if isinstance(obj, list) and all(isinstance(x, dict) for x in obj):
        return obj

    return []


def _get_first_str(d: Dict[str, Any], keys: Iterable[str]) -> str:
    for k in keys:
        v = d.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
        if v is not None and not isinstance(v, (dict, list)):
            s = str(v).strip()
            if s:
                return s
    return ""


def _get_first_number(d: Dict[str, Any], keys: Iterable[str], range_mode: str) -> Optional[float]:
    for k in keys:
        if k not in d:
            continue
        v = d.get(k)
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            n = _parse_range_number(v, range_mode=range_mode)
            if n is not None:
                return n
    return None


def _extract_attr_pairs(item: Dict[str, Any]) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    for k in ["attrs", "attrList", "properties", "propertyList", "zhsPropertyList", "zhs_property_list"]:
        v = item.get(k)
        if not isinstance(v, list):
            continue
        for x in v:
            if not isinstance(x, dict):
                continue
            name = _get_first_str(x, ["name", "title", "key", "label", "propName"])
            val = _get_first_str(x, ["value", "val", "content", "propValue"])
            if name and val:
                out.append((name, val))
    return out


def _parse_resources_from_text(text: str, range_mode: str) -> AccountResources:
    s = str(text or "")

    char5 = _to_int(
        _parse_range_number(
            _first_group(
                s,
                r"(?:五星角色数|5星角色数|五星角色数量|5星角色数量)\s*[:：]?\s*(\d+(?:\.\d+)?)",
            ),
            range_mode,
        )
    )
    if char5 == 0:
        char5 = _to_int(
            _parse_range_number(
                _first_group(s, r"(\d+(?:\.\d+)?)\s*(?:个)?\s*(?:五星角色|5星角色)"),
                range_mode,
            )
        )
    if char5 == 0:
        char5 = _to_int(
            _parse_range_number(
                _first_group(s, r"(\d+(?:\.\d+)?)\s*(?:角黄|角|角色黄|角色黄数)"),
                range_mode,
            )
        )

    weapon5 = _to_int(
        _parse_range_number(
            _first_group(
                s,
                r"(?:五星武器数|5星武器数|五星武器数量|5星武器数量)\s*[:：]?\s*(\d+(?:\.\d+)?)",
            ),
            range_mode,
        )
    )
    if weapon5 == 0:
        weapon5 = _to_int(
            _parse_range_number(
                _first_group(s, r"(\d+(?:\.\d+)?)\s*(?:个)?\s*(?:五星武器|5星武器)"),
                range_mode,
            )
        )
    if weapon5 == 0:
        weapon5 = _to_int(
            _parse_range_number(
                _first_group(s, r"(\d+(?:\.\d+)?)\s*(?:武黄|武器黄|武器黄数)"),
                range_mode,
            )
        )

    star_voice = _to_int(
        _parse_range_number(
            _first_group(s, r"(?:星声数量|星聲數量)\s*[:：]?\s*(\d+(?:\.\d+)?(?:万|w)?)"),
            range_mode,
        )
    )
    if star_voice == 0:
        star_voice = _to_int(
            _parse_range_number(
                _first_group(s, r"(\d+(?:\.\d+)?(?:万|w)?)\s*(?:星声|星聲)"),
                range_mode,
            )
        )

    wave = 0
    for pat in [
        r"(?:浮金波纹数量|浮金波紋數量|浮金波纹|浮金波紋)\s*[:：]?\s*(\d+(?:\.\d+)?(?:万|w)?)",
        r"(?:铸潮波纹数量|鑄潮波紋數量|铸潮波纹|鑄潮波紋)\s*[:：]?\s*(\d+(?:\.\d+)?(?:万|w)?)",
        r"(?:唤声涡纹数量|喚聲渦紋數量|唤声涡纹|喚聲渦紋)\s*[:：]?\s*(\d+(?:\.\d+)?(?:万|w)?)",
        r"(?:金波纹|金波紋|金波)\s*[:：]?\s*(\d+(?:\.\d+)?(?:万|w)?)",
        r"(?:蓝波纹|藍波紋|蓝波)\s*[:：]?\s*(\d+(?:\.\d+)?(?:万|w)?)",
        r"(?:波纹数量|波紋數量)\s*[:：]?\s*(\d+(?:\.\d+)?(?:万|w)?)",
    ]:
        wave += _to_int(_parse_range_number(_first_group(s, pat), range_mode))

    return AccountResources(char5=char5, weapon5=weapon5, star_voice=star_voice, wave_pulls=wave)


def _first_group(text: str, pattern: str) -> str:
    m = re.search(pattern, text, flags=re.IGNORECASE)
    if not m:
        return ""
    if m.groups():
        return m.group(1) or ""
    return m.group(0) or ""


def extract_resources(item: Dict[str, Any], range_mode: str) -> AccountResources:
    pairs = _extract_attr_pairs(item)

    char5 = 0
    weapon5 = 0
    star_voice = 0
    wave = 0

    for name, val in pairs:
        key = str(name or "").strip()
        v = str(val or "").strip()
        if not key or not v:
            continue

        if "角色" in key and "黄" in key:
            char5 = max(char5, _to_int(_parse_range_number(v, range_mode)))
            continue
        if "武器" in key and "黄" in key:
            weapon5 = max(weapon5, _to_int(_parse_range_number(v, range_mode)))
            continue
        if "星声" in key or "星聲" in key:
            star_voice = max(star_voice, _to_int(_parse_range_number(v, range_mode)))
            continue
        if "波纹" in key or "波紋" in key:
            wave += _to_int(_parse_range_number(v, range_mode))

    title = _get_first_str(item, ["title", "name", "subject", "productTitle", "product_name"])
    sub_title = _get_first_str(item, ["subTitle", "subtitle", "sub_title"])
    highlight = _get_first_str(item, ["highlight", "desc", "description", "detail", "content"])
    merged = "\n".join(x for x in [title, sub_title, highlight] if x)
    fallback = _parse_resources_from_text(merged, range_mode=range_mode)

    if char5 == 0:
        char5 = fallback.char5
    if weapon5 == 0:
        weapon5 = fallback.weapon5
    if star_voice == 0:
        star_voice = fallback.star_voice
    if wave == 0:
        wave = fallback.wave_pulls

    return AccountResources(char5=char5, weapon5=weapon5, star_voice=star_voice, wave_pulls=wave)


def score_candidate(c: Candidate, w: Weights) -> Dict[str, float]:
    pulls = c.resources.total_pulls
    total_equiv_pulls = c.resources.char5 * w.char5 + c.resources.weapon5 * w.weapon5 + pulls * w.pull
    value_per_rmb = total_equiv_pulls / max(c.price, 1e-9)
    return {
        "pulls": pulls,
        "total_equiv_pulls": total_equiv_pulls,
        "value_per_rmb": value_per_rmb,
    }


def _format_table(rows: List[List[str]]) -> str:
    if not rows:
        return ""
    widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    lines = []
    for r in rows:
        parts = [r[i].ljust(widths[i]) for i in range(len(r))]
        lines.append("  ".join(parts).rstrip())
    return "\n".join(lines)


def _csv_escape(s: str) -> str:
    t = str(s or "")
    if any(x in t for x in [",", "\"", "\n", "\r"]):
        return "\"" + t.replace("\"", "\"\"") + "\""
    return t


def _write_csv(path: Path, header: List[str], rows: List[List[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append(",".join(_csv_escape(x) for x in header))
    for r in rows:
        lines.append(",".join(_csv_escape(x) for x in r))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _parse_weights(weights_json: str) -> Weights:
    try:
        obj = json.loads(weights_json)
    except json.JSONDecodeError:
        raise SystemExit("--weights 必须是合法 JSON，例如 {\"char5\":80,\"weapon5\":65,\"pull\":1}")
    if not isinstance(obj, dict):
        raise SystemExit("--weights 必须是 JSON object")
    char5 = float(obj.get("char5", 80))
    weapon5 = float(obj.get("weapon5", 65))
    pull = float(obj.get("pull", 1))
    return Weights(char5=char5, weapon5=weapon5, pull=pull)


def _load_json_from_path(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def _load_input_json(args: argparse.Namespace, data_dir: Path) -> Tuple[Any, Optional[Path]]:
    if args.input:
        p = Path(args.input).expanduser()
        return _load_json_from_path(p), p

    text = _read_stdin_text()
    if not text:
        raise SystemExit("缺少输入：用 --input 指定 JSON 文件，或把 curl 响应通过 stdin 传入")

    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        raise SystemExit("stdin 不是合法 JSON，请确认 curl 输出为 JSON")

    if args.raw_out:
        p = Path(args.raw_out).expanduser()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text + "\n", encoding="utf-8")
        return obj, p

    if args.save_raw:
        raw_dir = data_dir / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        p = raw_dir / f"kejinshou_{_now_tag()}.json"
        p.write_text(text + "\n", encoding="utf-8")
        return obj, p

    return obj, None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="")
    parser.add_argument("--save-raw", action="store_true", default=False)
    parser.add_argument("--raw-out", type=str, default="")
    parser.add_argument("--weights", type=str, default="")
    parser.add_argument("--range", type=str, default="min", choices=["min", "avg", "max"])
    parser.add_argument("--limit", type=int, default=60)
    parser.add_argument("--dump-fields", action="store_true", default=False)
    parser.add_argument("--csv-out", type=str, default="")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parents[1]
    data_dir = base_dir / "data"
    outputs_dir = base_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    weights = _parse_weights(args.weights) if args.weights else Weights(char5=80, weapon5=65, pull=1)

    obj, raw_path = _load_input_json(args, data_dir=data_dir)
    items = _candidate_list_from_response(obj)
    if not items:
        raise SystemExit("未能在 JSON 中找到候选列表，请用 --dump-fields 看结构并补充解析规则")

    if args.dump_fields:
        first = items[0]
        keys = sorted(list(first.keys()))
        pairs = _extract_attr_pairs(first)
        print("top_keys:", keys)
        print("attr_pairs:", pairs[:50])
        return

    candidates: List[Candidate] = []
    for it in items[: max(args.limit, 1)]:
        title = _get_first_str(it, ["title", "name", "subject", "productTitle", "product_name"])
        product_id = _get_first_str(it, ["id", "productId", "product_id", "goodsId", "spuId", "skuId", "itemId"])

        price = _get_first_number(it, ["price", "showPrice", "priceYuan", "salePrice", "minPrice"], range_mode=args.range)
        if price is None:
            price = _parse_range_number(title, range_mode=args.range)
        if price is None:
            continue

        if price > 1000 and float(int(price)) == float(price):
            price = price / 100.0

        resources = extract_resources(it, range_mode=args.range)
        candidates.append(Candidate(product_id=product_id or "-", title=title or "-", price=float(price), resources=resources))

    scored = []
    for c in candidates:
        s = score_candidate(c, weights)
        scored.append((c, s))

    scored.sort(key=lambda x: (x[1]["value_per_rmb"], x[1]["total_equiv_pulls"]), reverse=True)

    header = [
        "rank",
        "price",
        "char5",
        "weapon5",
        "yellow_total",
        "star_voice",
        "wave_pulls",
        "pulls_total",
        "equiv_pulls_total",
        "equiv_pulls_per_rmb",
        "product_id",
        "title",
    ]

    out_rows: List[List[str]] = []
    table_rows: List[List[str]] = []
    table_rows.append(header[:10] + ["product_id"])

    for i, (c, s) in enumerate(scored, start=1):
        row = [
            str(i),
            f"{c.price:.2f}".rstrip("0").rstrip("."),
            str(c.resources.char5),
            str(c.resources.weapon5),
            str(c.total_yellow),
            str(c.resources.star_voice),
            str(c.resources.wave_pulls),
            f"{s['pulls']:.1f}",
            f"{s['total_equiv_pulls']:.1f}",
            f"{s['value_per_rmb']:.3f}",
            c.product_id,
            c.title,
        ]
        out_rows.append(row)
        table_rows.append(row[:10] + [row[10]])

    print(
        f"weights: char5={weights.char5} weapon5={weights.weapon5} pull={weights.pull} (单位：等价抽数)\n"
        f"range_mode: {args.range}\n"
        f"items: {len(items)} parsed: {len(out_rows)}\n"
        f"raw_saved: {raw_path if raw_path else '-'}\n"
    )
    print(_format_table(table_rows))

    csv_path = Path(args.csv_out).expanduser() if args.csv_out else (outputs_dir / f"ranking_{_now_tag()}.csv")
    _write_csv(csv_path, header=header, rows=out_rows)
    print(f"\ncsv: {csv_path}")


if __name__ == "__main__":
    main()
