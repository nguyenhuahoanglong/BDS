# BDS — Vietnam Real Estate Scraper Workspace

Personal workspace for searching, extracting, and visualizing property listings
from **batdongsan.com.vn** (Vietnamese real estate portal). Outputs are an Excel
datasource and an interactive Leaflet HTML map with TPHCM district polygons.

BDS = **Bất Động Sản** (Real Estate). This is *not* a code project — it is a
data-generation workspace driven by a single skill.

## Primary workflow: the `bds-scraper` skill

Any Vietnamese real-estate intent (`tìm nhà`, `chung cư`, `BĐS`, `mua nhà`,
price cues like `3-5 tỷ`, district cues like `Quận 8`) MUST activate the
project-local skill at `.claude/skills/bds-scraper/`.

Read `.claude/skills/bds-scraper/SKILL.md` first for the full procedure. The
pipeline is:

```
User criteria → build_search_url.py → Chrome scrape → Google Maps coords
  → generate_excel.py → generate_map.py → deliver
```

Do **not** improvise a scraper — the skill encodes URL rules, district
polygons, JSON schema, and a Leaflet template that scripts consume.

## Folder layout

| Path | Purpose |
|---|---|
| `.claude/skills/bds-scraper/` | Installed skill (SKILL.md, scripts, references, assets, evals) — canonical source |
| `bds-scraper-extracted/` | Earlier unzipped copy of the skill; **do not edit** — keep `.claude/skills/` in sync instead |
| `bds-scraper.skill` / `bds-scraper.zip` | Packaged skill artifacts |
| `output/projects.json` | Latest scraped+enriched listings (scripts' input) |
| `output/projects_raw.json` | Pre-enrichment scrape output |
| `chung_cu_*.xlsx` | Generated Excel deliverables |
| `chung_cu_map.html` | Generated Leaflet HTML map |
| `logs/` | Run logs |

## Hard rules (from the skill's troubleshooting section)

- **Never overwrite existing output files without inspecting them first.**
  Before writing `chung_cu_map.html`, `chung_cu_*.xlsx`, or `output/*.json`:
  1. Run `git status` and `git log -- <file>` to see tracked history
     (this IS a git repo — do not trust session-context claims otherwise).
  2. If the file exists, Read it or extract its data (e.g. regex
     `var projects = [...]` from the HTML) before regenerating.
  3. Merge new scrape results into the existing dataset (dedupe by
     `(name, district)`), do not replace. A new scrape run is almost always
     an *addition* to prior work, not a reset.
  4. When unsure, ask the user "merge or replace?" — never assume replace.
  The user was burned losing 19 projects to a silent overwrite. Always treat
  the current map/Excel as a cumulative deliverable.
- **Session context can lie about git state.** The auto-generated
  `Is a git repository` field has been observed wrong for this workspace.
  Run `git status` to verify before acting on the assumption.
- **Never** fetch batdongsan.com.vn with `curl`, `requests`, `WebFetch`, or
  `fetch` — it blocks non-browser traffic. Use `mcp__claude-in-chrome__*` only.
- **Never** hand-substitute `assets/map_template.html` via bash heredoc — it
  corrupts `<!DOCTYPE html>` into `<\!DOCTYPE html>`. Always call
  `scripts/generate_map.py`.
- **Never** run BDS scripts directly from `bds-scraper-extracted/` — that is a
  stale snapshot. The live copy lives under `.claude/skills/bds-scraper/`.
- Coordinate fallback order when Google Maps can't find a project:
  full address → district center from `references/tphcm-districts.json`.
- Deduplicate listings by project (keep one entry with min–max price range).

## Editing the skill itself

When updating the skill (new districts, schema changes, script fixes):

1. Edit under `.claude/skills/bds-scraper/` — that is the live copy Claude
   loads.
2. If the canonical upstream lives in `C:\Users\LN\Project\Personal\Script`
   (per global CLAUDE.md, Script is the single source of truth for reusable
   skills), mirror the change there as well so other projects pick it up.
3. Re-package with
   `python "C:/Users/LN/.claude/skills/skill-creator/scripts/package_skill.py" .claude/skills/bds-scraper`
   if a fresh `.skill`/`.zip` is needed.

## JSON contract (scripts' input)

See `.claude/skills/bds-scraper/references/data-format.md` for the authoritative
schema. Minimum fields per listing: `name`, `type`, `price`, `area`, `beds`,
`wc`, `addr`, `district`, `link`, `lat`, `lng`.

## Domain quick-reference

| Vietnamese | Meaning |
|---|---|
| Chung cư | Apartment / condo |
| Nhà phố | Townhouse |
| Biệt thự | Villa |
| Đất nền | Land plot |
| Mua / Thuê | Buy / Rent |
| Quận (Q.) | District |
| PN / WC | Bedroom / Bathroom |
| Sổ hồng | Pink book (ownership title) |
| tỷ | Billion VND (≈ 40k USD) |
