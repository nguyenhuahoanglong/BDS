#!/usr/bin/env python3
"""
Generate interactive Leaflet HTML map from BDS listing data.

Reads assets/map_template.html and substitutes placeholders with JSON data.
Writes bytes directly to avoid shell-escaping bugs (e.g., `<\\!DOCTYPE html>`
that bash heredoc produces).

Usage:
    python generate_map.py --data projects.json --output map.html
    python generate_map.py --data projects.json --output map.html --title "Chung Cu Q8" --subtitle "3-5 ty"

Or import and call directly:
    from generate_map import create_bds_map
    create_bds_map(projects, "out.html", title="...", subtitle="...")

Exit codes:
    0 = success
    1 = validation error, missing file, or I/O failure
"""

import argparse
import json
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TEMPLATE = SKILL_ROOT / "assets" / "map_template.html"
DEFAULT_DISTRICTS = SKILL_ROOT / "references" / "tphcm-districts.json"
DEFAULT_INFRASTRUCTURE = SKILL_ROOT / "references" / "tphcm-infrastructure.json"


def load_districts(districts_path: Path):
    """Load districts JSON and return (districts_dict, colors_dict)."""
    if not districts_path.exists():
        raise FileNotFoundError(f"Districts file not found: {districts_path}")
    with districts_path.open(encoding="utf-8") as f:
        data = json.load(f)
    districts = data.get("districts", {})
    colors = data.get("colors", {})
    if not districts:
        raise ValueError(f"No 'districts' key in {districts_path}")
    return districts, colors


def load_infrastructure(infra_path: Path):
    """Load infrastructure JSON and return list of route objects."""
    if not infra_path.exists():
        return []  # Infrastructure is optional
    with infra_path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Infrastructure data must be a JSON array: {infra_path}")
    return data


def create_bds_map(
    projects,
    output_path,
    title="BDS Listings",
    subtitle=None,
    template_path=None,
    districts_path=None,
    infrastructure_path=None,
):
    """Render map_template.html with project data -> self-contained HTML file.

    Args:
        projects: list of dicts (see references/data-format.md for schema)
        output_path: target HTML file path
        title: displayed in header and browser title
        subtitle: small text under title; defaults to "{n} du an"
        template_path: override template path (default: assets/map_template.html)
        districts_path: override districts JSON (default: references/tphcm-districts.json)
        infrastructure_path: override infrastructure JSON (default: references/tphcm-infrastructure.json); optional — missing file injects empty array

    Returns:
        str: absolute output path
    """
    template_path = Path(template_path or DEFAULT_TEMPLATE)
    districts_path = Path(districts_path or DEFAULT_DISTRICTS)
    infrastructure_path = Path(infrastructure_path or DEFAULT_INFRASTRUCTURE)
    output_path = Path(output_path)

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    # Load template + district data
    with template_path.open(encoding="utf-8") as f:
        html = f.read()

    districts, colors = load_districts(districts_path)
    infrastructure = load_infrastructure(infrastructure_path)

    # Build subtitle
    if subtitle is None:
        subtitle = f"{len(projects)} du an"

    # JSON-encode payloads (ensure_ascii=False so Vietnamese renders, but the
    # template stores them in JS string literals which handle UTF-8 fine).
    projects_json = json.dumps(projects, ensure_ascii=False)
    districts_json = json.dumps(districts, ensure_ascii=False)
    colors_json = json.dumps(colors, ensure_ascii=False)
    infrastructure_json = json.dumps(infrastructure, ensure_ascii=False)

    # Substitute placeholders. str.replace is safe here — no shell, no eval.
    replacements = {
        "{{TITLE}}": title,
        "{{SUBTITLE}}": subtitle,
        "{{PROJECTS_JSON}}": projects_json,
        "{{DISTRICTS_JSON}}": districts_json,
        "{{COLORS_JSON}}": colors_json,
        "{{INFRASTRUCTURE_JSON}}": infrastructure_json,
    }
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)

    # Sanity check: any unsubstituted placeholders left?
    leftover = [p for p in replacements if p in html]
    if leftover:
        raise RuntimeError(f"Unsubstituted placeholders: {leftover}")

    # Write bytes (UTF-8, no BOM, LF line endings) to avoid any shell escaping
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(html.encode("utf-8"))

    # Verify the first line is exactly "<!DOCTYPE html>" (not "<\!DOCTYPE html>")
    with output_path.open("rb") as f:
        first = f.readline().strip()
    if first != b"<!DOCTYPE html>":
        raise RuntimeError(
            f"DOCTYPE corrupted: first line is {first!r}, "
            f"expected b'<!DOCTYPE html>'"
        )

    size = output_path.stat().st_size
    print(f"Map saved: {output_path} ({size:,} bytes, {len(projects)} projects)")
    return str(output_path.resolve())


def main():
    parser = argparse.ArgumentParser(description="Generate BDS Leaflet HTML map")
    parser.add_argument(
        "--data",
        required=True,
        help="JSON string or path to JSON file with project data",
    )
    parser.add_argument("--output", required=True, help="Output HTML file path")
    parser.add_argument("--title", default="BDS Listings", help="Map title")
    parser.add_argument("--subtitle", default=None, help="Map subtitle")
    parser.add_argument("--template", default=None, help="Override template path")
    parser.add_argument("--districts", default=None, help="Override districts JSON path")
    parser.add_argument("--infrastructure", default=None, help="Override infrastructure JSON path")
    args = parser.parse_args()

    # Parse --data as file path first, then fall back to inline JSON
    data_arg = args.data
    try:
        maybe_path = Path(data_arg)
        if maybe_path.exists() and maybe_path.is_file():
            with maybe_path.open(encoding="utf-8") as f:
                projects = json.load(f)
        else:
            projects = json.loads(data_arg)
    except (OSError, ValueError) as e:
        print(f"ERROR: could not parse --data: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(projects, list):
        print("ERROR: --data must be a JSON array of project objects", file=sys.stderr)
        sys.exit(1)

    try:
        create_bds_map(
            projects,
            args.output,
            title=args.title,
            subtitle=args.subtitle,
            template_path=args.template,
            districts_path=args.districts,
            infrastructure_path=args.infrastructure,
        )
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
