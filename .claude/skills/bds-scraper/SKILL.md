---
name: bds-scraper
description: "Search batdongsan.com.vn, extract listings, generate Excel + Leaflet map. Use for Vietnamese real estate: 'tìm nhà', 'chung cư', 'BĐS', 'mua nhà', price ('3-5 tỷ'), districts ('Quận 8')."
---

# BDS Scraper — Vietnam Real Estate Listing Tool

Search, extract and visualize property listings from batdongsan.com.vn. Produces an Excel datasource and an interactive Leaflet HTML map with TPHCM district boundary polygons.

## When to trigger

Activate on any Vietnamese real-estate intent:

- **Intent**: "tìm nhà", "tìm chung cư", "mua nhà", "thuê nhà", "so sánh giá", "có dự án nào tốt..."
- **Domain words**: "bất động sản", "BĐS", "batdongsan", "dự án", "chung cư", "nhà phố", "biệt thự", "đất nền", "shophouse", "condotel"
- **Price cues**: "3-5 tỷ", "dưới 2 tỷ", "trên 10 tỷ"
- **District cues**: "Quận 1-12", "Thủ Đức", "Gò Vấp", "Bình Thạnh", "Tân Bình", "Phú Nhuận", "Bình Tân", "Nhà Bè", "Bình Chánh"

Casual queries like *"nhà quận mấy rẻ"* or *"có gì hay ở Q8 không"* also count — prefer to activate.

## Workflow overview

```
User criteria → Build search URL → Chrome scrape listings → Google Maps coords
    → generate_excel.py → generate_map.py → Verify & deliver
```

| # | Step | Primary tool |
|---|---|---|
| 0 | Collect criteria from user | interview (see table below) |
| 1 | Build search URL | `scripts/build_search_url.py` |
| 2 | Scrape listings via Chrome | `mcp__claude-in-chrome__*` |
| 3 | Resolve coordinates | Google Maps URL `@lat,lng` |
| 4 | Generate Excel | `scripts/generate_excel.py` |
| 5 | Generate HTML map | `scripts/generate_map.py` |
| 6 | Verify & deliver | Read tool + `computer://` links |

**Details for steps 1–5**: see `references/workflow-detailed.md`.
**JSON contract** that scripts consume: see `references/data-format.md`.

## Step 0 — Criteria collection

Ask the user only for criteria they have not already provided:

| Criterion | Example | Default |
|-----------|---------|---------|
| Property type | Chung cư / Nhà phố / Đất nền / Biệt thự | Chung cư |
| Location | District(s) in TPHCM | *(ask)* |
| Price range | 3-5 tỷ, dưới 2 tỷ, trên 10 tỷ | none |
| Area | 50-80m², trên 100m² | none |
| Bedrooms | 2PN, 3PN | none |
| Mua/Thuê | Mua / Thuê | Mua |
| Output folder | target path | `~/Downloads` |

Convert answers to canonical terms (e.g., "Quận 8" → `quan-8`, "3-5 tỷ" → `gia_tu=3000&gia_den=5000`) before building the search URL. See `references/bds-url-guide.md`.

## Scripts

| Script | Role | Entry |
|---|---|---|
| `build_search_url.py` | Context gatherer — criteria → batdongsan URL | `python build_search_url.py --type chung-cu --district quan-8 --price 3-5` |
| `generate_excel.py` | Transformer — projects JSON → formatted xlsx | `python generate_excel.py --data projects.json --output out.xlsx` |
| `generate_map.py` | Transformer — projects JSON → self-contained HTML | `python generate_map.py --data projects.json --output out.html` |
| `validate_projects.py` | Validator — checks projects JSON schema | `python validate_projects.py --data projects.json` |

**Always run `generate_map.py`** for the HTML output. Do **not** substitute `assets/map_template.html` placeholders by hand — bash heredoc escaping corrupts `<!DOCTYPE html>` into `<\!DOCTYPE html>`.

## Troubleshooting

| Problem | Fix |
|---|---|
| `<\!DOCTYPE html>` in output | Used bash heredoc — regenerate via `generate_map.py` |
| Chrome won't open `file:///` | Inject via `document.open()` + `document.write()` on `example.com` |
| batdongsan.com.vn blocks request | Use Chrome browser tool only, never curl/fetch/requests |
| Google Maps can't find project | Fallback to full address, then to district center from `tphcm-districts.json` |
| Leaflet tiles blank | Confirm HTTPS + `{s}.tile.openstreetmap.org` subdomain works |
| Duplicate listings | Gather min–max price, keep one entry per project |

## File references

- `references/workflow-detailed.md` — full procedure for steps 1–5 (scrape patterns, coord extraction, Excel/map building)
- `references/data-format.md` — JSON contract for a project object (scripts' input schema)
- `references/bds-url-guide.md` — batdongsan.com.vn URL/query structure
- `references/tphcm-districts.json` — boundary polygons + colors + centers for 22 TPHCM districts
- `scripts/build_search_url.py` — criteria → URL
- `scripts/generate_excel.py` — JSON → xlsx
- `scripts/generate_map.py` — JSON → HTML map
- `scripts/validate_projects.py` — schema validator
- `assets/map_template.html` — Leaflet template consumed by `generate_map.py`
