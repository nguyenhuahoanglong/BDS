#!/usr/bin/env python3
"""
Enrich BDS listings with trust_score, price_per_m2, and price_confidence.

Reads a projects JSON file (output of Step 2 scrape + dedupe), computes
scoring fields, and writes back. See references/data-format.md for the
schema and formulas.

Usage:
    python score_listings.py --data output/projects_raw.json --output output/projects.json
    python score_listings.py --data projects.json   # in-place (no --output)

Exit codes:
    0 = success (even if some entries unscored — they keep nulls)
    1 = bad input (file missing, not a list)
"""

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

VIP_POINTS = {"diamond": 50, "gold": 40, "silver": 30, "normal": 0}
SELLER_POINTS = {"broker_pro": 30, "agency": 25, "individual": 10, "unknown": 5}

OUTLIER_THRESHOLD = 0.25  # ±25% of group median
GROUP_MIN_SIZE = 5        # below this, skip outlier comparison


def parse_price_billion(price_str):
    """Parse price string -> midpoint in billion VND. None if unparseable.

    Examples: "3.2-4.8 ty" -> 4.0, "5 ty" -> 5.0, "Thoa thuan" -> None.
    """
    if not isinstance(price_str, str):
        return None
    s = price_str.lower().replace(",", ".")
    nums = re.findall(r"\d+(?:\.\d+)?", s)
    if not nums:
        return None
    vals = [float(n) for n in nums]
    # Sanity: assume "ty" (billions) unit. Values < 0.05 likely garbage.
    vals = [v for v in vals if v >= 0.05]
    if not vals:
        return None
    return sum(vals) / len(vals)


def parse_area_m2(area_str):
    """Parse area string -> midpoint in m². None if unparseable."""
    if not isinstance(area_str, str):
        return None
    s = area_str.lower().replace(",", ".")
    nums = re.findall(r"\d+(?:\.\d+)?", s)
    if not nums:
        return None
    vals = [float(n) for n in nums if float(n) >= 5]
    if not vals:
        return None
    return sum(vals) / len(vals)


def compute_trust_score(entry):
    vip_tier = (entry.get("vip_tier") or "normal").lower()
    seller_type = (entry.get("seller_type") or "unknown").lower()
    posted_days = entry.get("posted_days") or 0
    try:
        posted_days = int(posted_days)
    except (TypeError, ValueError):
        posted_days = 999

    vip_pts = VIP_POINTS.get(vip_tier, 0)
    seller_pts = SELLER_POINTS.get(seller_type, 5)
    if posted_days <= 7:
        freshness_pts = 20
    elif posted_days <= 30:
        freshness_pts = 10
    else:
        freshness_pts = 0

    return min(100, vip_pts + seller_pts + freshness_pts)


def compute_price_per_m2(entry):
    """price_per_m2 in triệu VND/m² (1 tỷ = 1000 triệu)."""
    price_b = parse_price_billion(entry.get("price"))
    area_m2 = parse_area_m2(entry.get("area"))
    if price_b is None or area_m2 is None or area_m2 == 0:
        return None
    return round((price_b * 1000) / area_m2, 2)


def classify_confidence(entry, group_median, group_size):
    trust = entry.get("trust_score") or 0
    ppm2 = entry.get("price_per_m2")

    if ppm2 is None or group_median is None:
        return "medium" if trust >= 50 else "low"

    if group_size < GROUP_MIN_SIZE:
        return "medium" if trust >= 50 else "low"

    deviation = abs(ppm2 - group_median) / group_median
    if deviation > OUTLIER_THRESHOLD:
        return "low"
    if trust >= 60:
        return "high"
    return "medium"


def score_projects(projects):
    """Mutate projects in place. Returns the list."""
    # Pass 1: trust_score + price_per_m2
    for p in projects:
        if not isinstance(p, dict):
            continue
        # Defaults so downstream renderers always have these keys
        p.setdefault("vip_tier", "normal")
        p.setdefault("is_vip", p["vip_tier"] != "normal")
        p.setdefault("seller_type", "unknown")
        p.setdefault("posted_days", 0)

        p["trust_score"] = compute_trust_score(p)
        p["price_per_m2"] = compute_price_per_m2(p)

    # Pass 2: group medians by (district, type)
    groups = {}
    for p in projects:
        if not isinstance(p, dict):
            continue
        if p.get("price_per_m2") is None:
            continue
        key = (p.get("district") or "", (p.get("type") or "Chung cu").lower())
        groups.setdefault(key, []).append(p["price_per_m2"])

    medians = {k: statistics.median(v) for k, v in groups.items()}
    sizes = {k: len(v) for k, v in groups.items()}

    # Pass 3: classify confidence
    for p in projects:
        if not isinstance(p, dict):
            continue
        key = (p.get("district") or "", (p.get("type") or "Chung cu").lower())
        median = medians.get(key)
        size = sizes.get(key, 0)
        p["price_confidence"] = classify_confidence(p, median, size)

    return projects


def print_summary(projects):
    total = len(projects)
    by_conf = {"high": 0, "medium": 0, "low": 0}
    for p in projects:
        c = p.get("price_confidence", "low")
        if c in by_conf:
            by_conf[c] += 1
    print(f"=== SCORING SUMMARY ===")
    print(f"total entries: {total}")
    print(f"  high  : {by_conf['high']}")
    print(f"  medium: {by_conf['medium']}")
    print(f"  low   : {by_conf['low']} (outliers / sparse-group / unscored)")


def main():
    parser = argparse.ArgumentParser(description="Score BDS listings (trust + price confidence)")
    parser.add_argument("--data", required=True, help="Input projects JSON path")
    parser.add_argument("--output", default=None, help="Output path (default: overwrite --data)")
    args = parser.parse_args()

    src = Path(args.data)
    if not src.exists():
        print(f"ERROR: file not found: {src}", file=sys.stderr)
        sys.exit(1)

    with src.open(encoding="utf-8") as f:
        projects = json.load(f)

    if not isinstance(projects, list):
        print("ERROR: top-level must be a JSON array", file=sys.stderr)
        sys.exit(1)

    score_projects(projects)

    dst = Path(args.output) if args.output else src
    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("w", encoding="utf-8") as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)

    print(f"Scored: {dst} ({len(projects)} entries)")
    print_summary(projects)


if __name__ == "__main__":
    main()
