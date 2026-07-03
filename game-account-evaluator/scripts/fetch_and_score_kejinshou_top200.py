import argparse
import hashlib
import json
import math
import re
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from post_refresh_hooks import run_scripts


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
)

DEFAULT_PRICE_START = "50"
DEFAULT_PRICE_END = "200"
DEFAULT_LATEST_ORIGIN_ORDER = "polish_at_desc"
ORIGIN_ORDER_ALIASES = {
    "latest": DEFAULT_LATEST_ORIGIN_ORDER,
    "strength": "zhs_property_desc",
}


@dataclass(frozen=True)
class Weights:
    char5: float
    weapon5: float
    pull: float


@dataclass(frozen=True)
class DetailScore:
    product_id: str
    price: float
    area_name: str
    title: str
    sub_title: str
    upper_at: str
    polish_time_desc: str
    total_yellow: int
    char5: int
    weapon5: int
    star_voice: int
    fj_waves: int
    zc_waves: int
    hs_waves: int
    wave_pulls: int
    pulls_total: float
    equiv_pulls_total: float
    equiv_pulls_per_rmb: float
    level: int
    role_resonance: str
    weapon_resonance: str


def _now_tag() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _today_tag() -> str:
    return datetime.now().strftime("%Y%m%d")


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _to_int(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return 0
        return int(round(value))
    text = str(value).strip()
    if not text:
        return 0
    m = re.findall(r"(\d+(?:\.\d+)?)", text.replace(",", ""))
    if not m:
        return 0
    num = float(m[0])
    if "万" in text or re.search(r"(?i)\d+w", text):
        num *= 10000.0
    return int(round(num))


def _csv_escape(s: str) -> str:
    t = str(s or "")
    if any(x in t for x in [",", "\"", "\n", "\r"]):
        return "\"" + t.replace("\"", "\"\"") + "\""
    return t


def _write_csv(path: Path, header: List[str], rows: List[List[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [",".join(_csv_escape(x) for x in header)]
    for row in rows:
        lines.append(",".join(_csv_escape(x) for x in row))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _format_table(rows: List[List[str]]) -> str:
    if not rows:
        return ""
    widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    out = []
    for row in rows:
        out.append("  ".join(row[i].ljust(widths[i]) for i in range(len(row))).rstrip())
    return "\n".join(out)


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_product_id(value: Any) -> str:
    text = str(value or "").strip()
    return text


def _resolve_origin_order(sort_key: str, explicit_origin_order: str) -> str:
    if explicit_origin_order:
        return explicit_origin_order
    return ORIGIN_ORDER_ALIASES[sort_key]


def _extract_list_items(page_obj: Dict[str, Any]) -> List[Dict[str, Any]]:
    return list(page_obj.get("data", {}).get("data", {}).get("list", []))


def _list_item_snapshot(item: Dict[str, Any], rank: int, is_new: Optional[bool] = None) -> Dict[str, Any]:
    snapshot = {
        "rank": rank,
        "id": _normalize_product_id(item.get("id")),
        "price": _to_int(item.get("price")),
        "polishAt": str(item.get("polishAt") or ""),
        "polishTimeDesc": str(item.get("polishTimeDesc") or ""),
        "title": str(item.get("title") or ""),
        "subTitle": str(item.get("subTitle") or ""),
    }
    if is_new is not None:
        snapshot["isNew"] = bool(is_new)
    return snapshot


def _load_seen_ids(path: Path) -> Set[str]:
    if not path.exists():
        return set()
    obj = _read_json(path)
    if isinstance(obj, dict):
        raw_ids = obj.get("ids", [])
    elif isinstance(obj, list):
        raw_ids = obj
    else:
        raw_ids = []
    return {_normalize_product_id(x) for x in raw_ids if _normalize_product_id(x)}


class KejinshouClient:
    def __init__(self, mw_token: str, mw_enc_token: str, mw_sid: str, mw_k5: str) -> None:
        self.mw_token = mw_token
        self.mw_enc_token = mw_enc_token
        self.mw_sid = mw_sid
        self.mw_k5 = mw_k5

    def _build_mw_headers(self, data_obj: Dict[str, Any], mw_k5: str) -> Dict[str, str]:
        return {
            "mw-appkey": "100222",
            "mw-pv": "H5",
            "mw-k7": "h5",
            "mw-k3": "h5-nature-pc",
            "mw-id": "h-batch-top200-1",
            "mw-k9": "h5",
            "mw-k5": mw_k5,
            "mw-device": "Macintosh/1470/956",
            "mw-os": "macOS/10.15.7",
            "mw-ver": "h5-nuxt/3.41.0",
            "mw-runon": "Chrome/148.0.0.0",
            "data": json.dumps(data_obj, ensure_ascii=False, separators=(",", ":")),
            "mw-t": str(int(time.time() * 1000)),
            "mw-h5-token": self.mw_token,
            "mw-h5-token-enc": self.mw_enc_token,
        }

    def _calc_sign(self, api: str, version: str, headers: Dict[str, str]) -> str:
        omit_sign = {"mw-pv", "mw-sign", "mw-did", "mw-sid"}
        sorted_keys = sorted(headers.keys())
        values = [headers[k] for k in sorted_keys if k.startswith("mw-") and k not in omit_sign]
        values.append(api)
        values.append(version)
        values.append(_md5(headers["data"]))
        if self.mw_token:
            values.append(self.mw_token)
        return _md5("&".join(values))

    def _request(self, api: str, data_obj: Dict[str, Any], mw_k5: str, with_auth: bool) -> Dict[str, Any]:
        version = "1.0"
        mw_headers = self._build_mw_headers(data_obj=data_obj, mw_k5=mw_k5)
        if with_auth and self.mw_sid:
            mw_headers["mw-sid"] = self.mw_sid
        sign = self._calc_sign(api=api, version=version, headers=mw_headers)
        query = urllib.parse.urlencode(mw_headers)
        url = f"https://api.kejinshou.com/h5/{api}/{version}?{query}&mw-sign={sign}"

        headers = {
            "Accept": "*/*",
            "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7,zh;q=0.6,ko;q=0.5",
            "Connection": "keep-alive",
            "Origin": "https://m.kejinshou.com",
            "Referer": "https://m.kejinshou.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": USER_AGENT,
            "content-type": "application/x-www-form-urlencoded",
            "sec-ch-ua": "\"Chromium\";v=\"148\", \"Google Chrome\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"macOS\"",
        }
        if with_auth and self.mw_sid:
            headers["authorization"] = f"Bearer {self.mw_sid}"

        req = urllib.request.Request(url, headers=headers)
        text = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
        obj = json.loads(text)
        if obj.get("ret") != "SUCCESS" or obj.get("data", {}).get("status") != 0:
            raise RuntimeError(f"API failed: {api} ret={obj.get('ret')} status={obj.get('data', {}).get('status')}")
        return obj

    def search_products(
        self,
        page: int,
        size: int,
        price_start: str,
        price_end: str,
        origin_order: str,
    ) -> Dict[str, Any]:
        data_obj = {
            "gameId": "7265",
            "cateId": 7996,
            "type": "goods",
            "priceStart": price_start,
            "priceEnd": price_end,
            "originOrder": origin_order,
            "size": size,
            "page": page,
        }
        return self._request(
            api="mwp.kjs_search.product.search",
            data_obj=data_obj,
            mw_k5="0",
            with_auth=False,
        )

    def get_product_detail(self, product_id: int) -> Dict[str, Any]:
        return self._request(
            api="mwp.kjs_product.product.detail",
            data_obj={"id": product_id},
            mw_k5=self.mw_k5,
            with_auth=True,
        )


def _get_fp(properties_info: Dict[str, Any], title: str) -> Dict[str, Any]:
    for fp in properties_info.get("fps", []):
        if fp.get("title") == title:
            return fp
    return {}


def _get_sp(fp: Dict[str, Any], title: str) -> Dict[str, Any]:
    for sp in fp.get("sps", []):
        if sp.get("title") == title:
            return sp
    return {}


def _pvs_map(sp: Dict[str, Any]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for pv in sp.get("pvs", []):
        name = str(pv.get("title") or "").strip()
        out[name] = _to_int(pv.get("hasNum"))
    return out


def _resonance_to_text(d: Dict[str, int]) -> str:
    parts = []
    for key in ["6鸣", "5鸣", "4鸣", "3鸣", "2鸣", "1鸣", "0鸣"]:
        if d.get(key):
            parts.append(f"{key}x{d[key]}")
    return " ".join(parts)


def _parse_detail(detail_obj: Dict[str, Any], weights: Weights) -> DetailScore:
    data = detail_obj["data"]["data"]
    prop = data.get("propertyDetail", {})
    base = prop.get("baseInfos", {})
    properties_info = prop.get("propertiesInfo", {})

    resonator_fp = _get_fp(properties_info, "共鸣者")
    weapon_fp = _get_fp(properties_info, "武器")

    char5 = _pvs_map(_get_sp(resonator_fp, "星级")).get("五星", 0)
    weapon5 = _pvs_map(_get_sp(weapon_fp, "星级")).get("五星", 0)
    role_resonance_map = _pvs_map(_get_sp(resonator_fp, "角色共鸣"))
    weapon_resonance_map = _pvs_map(_get_sp(weapon_fp, "武器共鸣"))

    star_voice = _to_int(base.get("星声数量"))
    fj = _to_int(base.get("浮金波纹数量"))
    zc = _to_int(base.get("铸潮波纹数量"))
    hs = _to_int(base.get("唤声涡纹数量"))
    wave_pulls = fj + zc + hs
    pulls_total = star_voice / 160.0 + float(wave_pulls)
    equiv_pulls_total = char5 * weights.char5 + weapon5 * weights.weapon5 + pulls_total * weights.pull
    price = float(_to_int(data.get("price") or data.get("payPrice")))
    equiv_pulls_per_rmb = equiv_pulls_total / max(price, 1e-9)

    return DetailScore(
        product_id=str(data.get("id") or ""),
        price=price,
        area_name=str(data.get("areaName") or ""),
        title=str(data.get("title") or data.get("areaName") or ""),
        sub_title=str(data.get("subTitle") or ""),
        upper_at=str(data.get("upperAt") or ""),
        polish_time_desc=str(data.get("polishTimeDesc") or ""),
        total_yellow=_to_int(base.get("总黄数")),
        char5=char5,
        weapon5=weapon5,
        star_voice=star_voice,
        fj_waves=fj,
        zc_waves=zc,
        hs_waves=hs,
        wave_pulls=wave_pulls,
        pulls_total=pulls_total,
        equiv_pulls_total=equiv_pulls_total,
        equiv_pulls_per_rmb=equiv_pulls_per_rmb,
        level=_to_int(base.get("联觉等级")),
        role_resonance=_resonance_to_text(role_resonance_map),
        weapon_resonance=_resonance_to_text(weapon_resonance_map),
    )


def _flatten_list_pages(page_objs: Iterable[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for obj in page_objs:
        items.extend(_extract_list_items(obj))
    return items[:limit]


def _fetch_detail_scores(
    client: KejinshouClient,
    items: List[Dict[str, Any]],
    detail_dir: Path,
    weights: Weights,
    sleep_ms: int,
) -> Tuple[List[Path], List[DetailScore]]:
    detail_dir.mkdir(parents=True, exist_ok=True)
    detail_paths: List[Path] = []
    detail_scores: List[DetailScore] = []
    for idx, item in enumerate(items, start=1):
        product_id = _to_int(item.get("id"))
        obj = client.get_product_detail(product_id=product_id)
        path = detail_dir / f"{product_id}.json"
        _write_json(path, obj)
        detail_paths.append(path)
        detail_scores.append(_parse_detail(detail_obj=obj, weights=weights))
        if idx < len(items):
            time.sleep(max(sleep_ms, 0) / 1000.0)
    detail_scores.sort(key=lambda x: (x.equiv_pulls_per_rmb, x.equiv_pulls_total), reverse=True)
    return detail_paths, detail_scores


def _build_scored_rows(detail_scores: List[DetailScore]) -> Tuple[List[str], List[List[str]], List[List[str]]]:
    csv_header = [
        "rank",
        "product_id",
        "price",
        "upper_at",
        "polish_time_desc",
        "area_name",
        "level",
        "total_yellow",
        "char5",
        "weapon5",
        "star_voice",
        "fj_waves",
        "zc_waves",
        "hs_waves",
        "wave_pulls",
        "pulls_total",
        "equiv_pulls_total",
        "equiv_pulls_per_rmb",
        "role_resonance",
        "weapon_resonance",
        "sub_title",
    ]
    csv_rows: List[List[str]] = []
    table_rows: List[List[str]] = [csv_header[:16]]

    for rank, score in enumerate(detail_scores, start=1):
        row = [
            str(rank),
            score.product_id,
            f"{score.price:.0f}",
            score.upper_at,
            score.polish_time_desc,
            score.area_name,
            str(score.level),
            str(score.total_yellow),
            str(score.char5),
            str(score.weapon5),
            str(score.star_voice),
            str(score.fj_waves),
            str(score.zc_waves),
            str(score.hs_waves),
            str(score.wave_pulls),
            f"{score.pulls_total:.2f}",
            f"{score.equiv_pulls_total:.2f}",
            f"{score.equiv_pulls_per_rmb:.3f}",
            score.role_resonance,
            score.weapon_resonance,
            score.sub_title,
        ]
        csv_rows.append(row)
        table_rows.append(row[:16])
    return csv_header, csv_rows, table_rows


def _write_scored_outputs(
    csv_path: Path,
    json_path: Path,
    detail_scores: List[DetailScore],
    weights: Weights,
    extra_meta: Dict[str, Any],
) -> Tuple[List[List[str]], int]:
    csv_header, csv_rows, table_rows = _build_scored_rows(detail_scores)
    _write_csv(csv_path, header=csv_header, rows=csv_rows)
    _write_json(
        json_path,
        {
            "meta": {
                "generatedAt": _now_tag(),
                "count": len(detail_scores),
                "weights": {
                    "char5": weights.char5,
                    "weapon5": weights.weapon5,
                    "pull": weights.pull,
                },
                **extra_meta,
            },
            "items": [dict(zip(csv_header, row)) for row in csv_rows],
        },
    )
    return table_rows, len(csv_rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, default="full", choices=["full", "incremental"])
    parser.add_argument("--sort", type=str, default="latest", choices=sorted(ORIGIN_ORDER_ALIASES.keys()))
    parser.add_argument("--origin-order", type=str, default="")
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--incremental-count", type=int, default=20)
    parser.add_argument("--page-size", type=int, default=60)
    parser.add_argument("--price-start", type=str, default=DEFAULT_PRICE_START)
    parser.add_argument("--price-end", type=str, default=DEFAULT_PRICE_END)
    parser.add_argument("--seen-file", type=str, default="")
    parser.add_argument("--sleep-ms", type=int, default=150)
    parser.add_argument("--mw-token", type=str, required=True)
    parser.add_argument("--mw-enc-token", type=str, required=True)
    parser.add_argument("--mw-sid", type=str, required=True)
    parser.add_argument("--mw-k5", type=str, default="9411078")
    parser.add_argument("--char5-weight", type=float, default=80.0)
    parser.add_argument("--weapon5-weight", type=float, default=65.0)
    parser.add_argument("--pull-weight", type=float, default=1.0)
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parents[1]
    raw_dir = base_dir / "data" / "raw"
    output_dir = base_dir / "outputs"
    raw_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    client = KejinshouClient(
        mw_token=args.mw_token,
        mw_enc_token=args.mw_enc_token,
        mw_sid=args.mw_sid,
        mw_k5=args.mw_k5,
    )
    weights = Weights(char5=args.char5_weight, weapon5=args.weapon5_weight, pull=args.pull_weight)
    origin_order = _resolve_origin_order(sort_key=args.sort, explicit_origin_order=args.origin_order)

    list_pages_dir: Path
    combined_list_path: Path
    detail_dir: Path
    csv_path: Path
    json_path: Path
    list_target_items: List[Dict[str, Any]]
    extra_meta: Dict[str, Any]

    if args.mode == "full":
        list_pages_dir = raw_dir / "kejinshou_top200_pages"
        detail_dir = base_dir / "data" / "detail" / "kejinshou_top200"
        list_pages_dir.mkdir(parents=True, exist_ok=True)
        detail_dir.mkdir(parents=True, exist_ok=True)

        page_count = int(math.ceil(args.limit / max(args.page_size, 1)))
        page_objs: List[Dict[str, Any]] = []
        for page in range(1, page_count + 1):
            obj = client.search_products(
                page=page,
                size=args.page_size,
                price_start=args.price_start,
                price_end=args.price_end,
                origin_order=origin_order,
            )
            page_objs.append(obj)
            _write_json(list_pages_dir / f"page_{page}.json", obj)
            time.sleep(max(args.sleep_ms, 0) / 1000.0)

        list_target_items = _flatten_list_pages(page_objs=page_objs, limit=args.limit)
        combined_list_path = list_pages_dir / "top200_combined.json"
        _write_json(
            combined_list_path,
            {
                "meta": {
                    "mode": args.mode,
                    "limit": args.limit,
                    "sort": args.sort,
                    "originOrder": origin_order,
                    "priceStart": args.price_start,
                    "priceEnd": args.price_end,
                },
                "list": list_target_items,
            },
        )
        csv_path = output_dir / "kejinshou_top200_scored.csv"
        json_path = output_dir / "kejinshou_top200_scored.json"
        extra_meta = {
            "mode": args.mode,
            "sort": args.sort,
            "originOrder": origin_order,
            "priceStart": args.price_start,
            "priceEnd": args.price_end,
            "combinedListPath": str(combined_list_path),
            "detailDir": str(detail_dir),
        }
    else:
        batch_tag = _now_tag()
        list_pages_dir = raw_dir
        raw_page_path = raw_dir / f"kejinshou_incremental_page1_response_{batch_tag}.json"
        combined_list_path = raw_dir / f"kejinshou_incremental_page1_{_today_tag()}.json"
        seen_file = (
            Path(args.seen_file).expanduser()
            if args.seen_file
            else raw_dir / "kejinshou_incremental_seen_ids.json"
        )
        detail_dir = base_dir / "data" / "detail" / "kejinshou_incremental" / batch_tag
        csv_path = output_dir / f"kejinshou_incremental_scored_{batch_tag}.csv"
        json_path = output_dir / f"kejinshou_incremental_scored_{batch_tag}.json"

        page_obj = client.search_products(
            page=1,
            size=args.page_size,
            price_start=args.price_start,
            price_end=args.price_end,
            origin_order=origin_order,
        )
        _write_json(raw_page_path, page_obj)
        page_items = _extract_list_items(page_obj)
        batch_count = min(max(args.incremental_count, 1), len(page_items))
        batch_items = page_items[:batch_count]

        seen_ids = _load_seen_ids(seen_file)
        batch_snapshots: List[Dict[str, Any]] = []
        batch_ids: Set[str] = set()
        new_ids: List[str] = []
        list_target_items = []
        for rank, item in enumerate(batch_items, start=1):
            product_id = _normalize_product_id(item.get("id"))
            if product_id:
                batch_ids.add(product_id)
            is_new = bool(product_id) and product_id not in seen_ids
            batch_snapshots.append(_list_item_snapshot(item=item, rank=rank, is_new=is_new))
            if is_new:
                new_ids.append(product_id)
                list_target_items.append(item)

        _write_json(
            seen_file,
            {
                "updatedAt": _now_iso(),
                "count": len(seen_ids | batch_ids),
                "ids": sorted(seen_ids | batch_ids),
            },
        )
        _write_json(
            combined_list_path,
            {
                "source": "kejinshou",
                "capturedAt": _now_iso(),
                "strategy": {
                    "mode": args.mode,
                    "page": 1,
                    "incrementalCount": max(args.incremental_count, 1),
                    "pageSize": args.page_size,
                    "sort": args.sort,
                    "originOrder": origin_order,
                    "priceStart": args.price_start,
                    "priceEnd": args.price_end,
                    "seenFile": str(seen_file),
                },
                "items": batch_snapshots,
                "summary": {
                    "batchCount": len(batch_snapshots),
                    "newCount": len(new_ids),
                    "existingCount": len(batch_snapshots) - len(new_ids),
                },
            },
        )
        extra_meta = {
            "mode": args.mode,
            "sort": args.sort,
            "originOrder": origin_order,
            "priceStart": args.price_start,
            "priceEnd": args.price_end,
            "combinedListPath": str(combined_list_path),
            "rawPagePath": str(raw_page_path),
            "detailDir": str(detail_dir),
            "seenFile": str(seen_file),
            "detailScope": "new_only",
            "batchCount": len(batch_snapshots),
            "newCount": len(new_ids),
            "existingCount": len(batch_snapshots) - len(new_ids),
        }

    detail_paths, detail_scores = _fetch_detail_scores(
        client=client,
        items=list_target_items,
        detail_dir=detail_dir,
        weights=weights,
        sleep_ms=args.sleep_ms,
    )
    table_rows, scored_count = _write_scored_outputs(
        csv_path=csv_path,
        json_path=json_path,
        detail_scores=detail_scores,
        weights=weights,
        extra_meta=extra_meta,
    )

    print(f"mode: {args.mode}")
    print(f"list_pages_dir: {list_pages_dir}")
    print(f"combined_list: {combined_list_path}")
    print(f"detail_dir: {detail_dir}")
    print(f"detail_count: {len(detail_paths)}")
    print(f"sort: {args.sort} origin_order={origin_order}")
    print(f"price_range: {args.price_start}-{args.price_end}")
    if args.mode == "incremental":
        print(f"incremental_count: {max(args.incremental_count, 1)}")
        print(f"new_scored_count: {scored_count}")
    print(f"weights: char5={weights.char5} weapon5={weights.weapon5} pull={weights.pull}")
    print()
    print(_format_table(table_rows[:21]))
    print()
    print(f"csv: {csv_path}")
    print(f"json: {json_path}")

    if args.mode == "incremental":
        run_scripts(
            base_dir=base_dir,
            script_names=["generate_unified_wuwa_review.py"],
            reason="kejinshou incremental fetch",
        )
    else:
        run_scripts(
            base_dir=base_dir,
            script_names=["normalize_and_score_wuwa_role_tiers.py"],
            reason="kejinshou full fetch",
        )


if __name__ == "__main__":
    main()
