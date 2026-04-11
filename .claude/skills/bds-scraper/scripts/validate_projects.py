#!/usr/bin/env python3
"""
Validate a BDS projects JSON file against the contract in
references/data-format.md before running generate_excel.py / generate_map.py.

Checks:
  - Top-level is a JSON array
  - Each entry is an object
  - Required fields present: name, district, lat, lng
  - lat/lng are numbers in plausible TPHCM range
  - district is a canonical key (warns if not)
  - link (if present) starts with http

Outputs a structured header block and exits 0 on pass, 1 on fail.

Usage:
    python validate_projects.py --data projects.json
    python validate_projects.py --data projects.json --strict
"""

import argparse
import json
import sys
from pathlib import Path

REQUIRED_FIELDS = ("name", "district", "lat", "lng")
CANONICAL_DISTRICTS = {
    "Q.1", "Q.3", "Q.4", "Q.5", "Q.6", "Q.7", "Q.8",
    "Q.10", "Q.11", "Q.12",
    "Go Vap", "Binh Thanh", "Tan Binh", "Tan Phu", "Phu Nhuan",
    "Binh Tan", "Thu Duc", "Cu Chi", "Hoc Mon", "Binh Chanh",
    "Nha Be", "Can Gio",
}

# TPHCM bounding box (generous — covers all 22 districts)
LAT_MIN, LAT_MAX = 10.35, 11.20
LNG_MIN, LNG_MAX = 106.35, 107.05


def validate_projects(projects, strict=False):
    """Return (errors, warnings) lists."""
    errors = []
    warnings = []

    if not isinstance(projects, list):
        errors.append(f"Top-level is {type(projects).__name__}, expected list")
        return errors, warnings

    if not projects:
        warnings.append("Empty projects array — nothing to render")

    for i, p in enumerate(projects):
        prefix = f"[{i}]"
        if not isinstance(p, dict):
            errors.append(f"{prefix} is {type(p).__name__}, expected object")
            continue

        # Required fields
        for field in REQUIRED_FIELDS:
            if field not in p:
                errors.append(f"{prefix} missing required field '{field}'")

        # lat/lng type + range
        for coord, lo, hi in (("lat", LAT_MIN, LAT_MAX), ("lng", LNG_MIN, LNG_MAX)):
            val = p.get(coord)
            if val is None:
                continue  # already reported above
            if not isinstance(val, (int, float)) or isinstance(val, bool):
                errors.append(f"{prefix} {coord}={val!r} is not a number")
                continue
            if val == 0:
                errors.append(f"{prefix} {coord}=0 (likely Google Maps fallback failed)")
            elif not (lo <= val <= hi):
                warnings.append(
                    f"{prefix} {coord}={val} outside TPHCM range [{lo}, {hi}]"
                )

        # district canonical check
        district = p.get("district")
        if district and district not in CANONICAL_DISTRICTS:
            msg = (
                f"{prefix} district={district!r} is not canonical "
                f"(expected one of {sorted(CANONICAL_DISTRICTS)})"
            )
            if strict:
                errors.append(msg)
            else:
                warnings.append(msg)

        # link shape check
        link = p.get("link")
        if link and not (isinstance(link, str) and link.startswith(("http://", "https://"))):
            warnings.append(f"{prefix} link={link!r} does not start with http(s)://")

        # name non-empty
        name = p.get("name")
        if name is not None and (not isinstance(name, str) or not name.strip()):
            errors.append(f"{prefix} name is empty or not a string")

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Validate BDS projects JSON")
    parser.add_argument("--data", required=True, help="Path to projects JSON file")
    parser.add_argument(
        "--strict", action="store_true",
        help="Treat non-canonical districts as errors instead of warnings",
    )
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.exists():
        print(f"ERROR: file not found: {data_path}", file=sys.stderr)
        sys.exit(1)

    try:
        with data_path.open(encoding="utf-8") as f:
            projects = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    errors, warnings = validate_projects(projects, strict=args.strict)

    print("=== VALIDATION ===")
    print(f"file: {data_path}")
    count = len(projects) if isinstance(projects, list) else 0
    print(f"entries: {count}")
    print(f"errors: {len(errors)}")
    print(f"warnings: {len(warnings)}")
    print("=== DETAILS ===")
    for e in errors:
        print(f"FAIL {e}")
    for w in warnings:
        print(f"WARN {w}")
    print("=== RESULT ===")
    if errors:
        print("FAIL")
        sys.exit(1)
    print("PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
