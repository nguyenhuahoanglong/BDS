#!/usr/bin/env python3
"""
Build a batdongsan.com.vn search URL from structured criteria.

Encodes the rules documented in references/bds-url-guide.md so the LLM never
has to hand-craft URLs (which has historically produced typos in path
segments and query params).

Usage:
    python build_search_url.py --type can-ho-chung-cu --district quan-8 --price 3000-5000
    python build_search_url.py --action cho-thue --type nha-rieng --district go-vap --area 50-80
    python build_search_url.py --district tp-hcm --page 2

Exit codes:
    0 = URL written to stdout
    1 = invalid argument
"""

import argparse
import sys
from urllib.parse import urlencode

BASE = "https://batdongsan.com.vn"

ACTIONS = {
    "ban": "ban",
    "cho-thue": "cho-thue",
}

PROPERTY_TYPES = {
    "can-ho-chung-cu",
    "nha-rieng",
    "biet-thu-lien-ke",
    "nha-mat-pho",
    "shophouse-nha-pho-thuong-mai",
    "dat-nen-du-an",
    "dat",
    "trang-trai-khu-nghi-duong",
    "condotel",
    "kho-nha-xuong",
}

DISTRICTS = {
    "tp-hcm",
    "quan-1", "quan-2", "quan-3", "quan-4", "quan-5", "quan-6",
    "quan-7", "quan-8", "quan-9", "quan-10", "quan-11", "quan-12",
    "go-vap", "binh-thanh", "tan-binh", "tan-phu", "phu-nhuan",
    "binh-tan", "thu-duc", "cu-chi", "hoc-mon", "binh-chanh",
    "nha-be", "can-gio",
}


def parse_range(s, flag_name):
    """Parse 'MIN-MAX' / 'MIN-' / '-MAX' into (min, max) ints.

    Empty side = None. Returns (None, None) if s is falsy.
    """
    if not s:
        return None, None
    if "-" not in s:
        raise ValueError(
            f"{flag_name} must be MIN-MAX, got {s!r} (e.g., '3000-5000' or '3000-')"
        )
    lo_str, hi_str = s.split("-", 1)
    lo = int(lo_str) if lo_str else None
    hi = int(hi_str) if hi_str else None
    if lo is not None and hi is not None and lo > hi:
        raise ValueError(f"{flag_name} min > max: {lo} > {hi}")
    return lo, hi


def build_url(action, prop_type, district, price=None, area=None, page=1):
    """Compose the batdongsan.com.vn URL from validated parts."""
    if action not in ACTIONS:
        raise ValueError(f"--action must be one of {sorted(ACTIONS)}, got {action!r}")
    if prop_type not in PROPERTY_TYPES:
        raise ValueError(
            f"--type must be one of {sorted(PROPERTY_TYPES)}, got {prop_type!r}"
        )
    if district not in DISTRICTS:
        raise ValueError(
            f"--district must be one of {sorted(DISTRICTS)}, got {district!r}"
        )

    # Path: /ban-can-ho-chung-cu-quan-8
    path = f"/{action}-{prop_type}-{district}"

    # Pagination goes in the path, before the query string: /p2
    if page and page > 1:
        path += f"/p{int(page)}"

    # Query string
    params = []
    if price:
        lo, hi = parse_range(price, "--price")
        if lo is not None:
            params.append(("gia_tu", lo))
        if hi is not None:
            params.append(("gia_den", hi))
    if area:
        lo, hi = parse_range(area, "--area")
        if lo is not None:
            params.append(("dt_tu", lo))
        if hi is not None:
            params.append(("dt_den", hi))

    url = BASE + path
    if params:
        url += "?" + urlencode(params)
    return url


def main():
    parser = argparse.ArgumentParser(
        description="Build a batdongsan.com.vn search URL",
        epilog="See references/bds-url-guide.md for full parameter reference.",
    )
    parser.add_argument(
        "--action", default="ban", choices=sorted(ACTIONS),
        help="ban (mua) or cho-thue (thue). Default: ban",
    )
    parser.add_argument(
        "--type", dest="prop_type", default="can-ho-chung-cu",
        help="Property type slug (e.g., can-ho-chung-cu, nha-rieng, dat-nen-du-an)",
    )
    parser.add_argument(
        "--district", default="tp-hcm",
        help="District slug (e.g., quan-8, go-vap, thu-duc, tp-hcm for all HCMC)",
    )
    parser.add_argument(
        "--price", default=None,
        help="Price range in trieu VND as MIN-MAX (e.g., 3000-5000 for 3-5 ty)",
    )
    parser.add_argument(
        "--area", default=None,
        help="Area range in m2 as MIN-MAX (e.g., 50-80)",
    )
    parser.add_argument(
        "--page", type=int, default=1,
        help="Page number (default: 1). Pages >1 are encoded as /p{N} in path.",
    )
    args = parser.parse_args()

    try:
        url = build_url(
            action=args.action,
            prop_type=args.prop_type,
            district=args.district,
            price=args.price,
            area=args.area,
            page=args.page,
        )
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(url)


if __name__ == "__main__":
    main()
