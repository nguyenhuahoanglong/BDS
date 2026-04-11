# BDS Scraper — Detailed Workflow (Steps 1-5)

Full procedural guide for each workflow step. SKILL.md has the router-level overview; this file has the depth.

---

## Step 1 — Build the search URL

Use `scripts/build_search_url.py` to avoid hand-crafting URLs. It encodes the rules from `references/bds-url-guide.md`.

### Quick path

```bash
python scripts/build_search_url.py \
  --action ban \
  --type can-ho-chung-cu \
  --district quan-8 \
  --price 3000-5000
```

### Argument reference

| Flag | Values | Default |
|---|---|---|
| `--action` | `ban`, `cho-thue` | `ban` |
| `--type` | `can-ho-chung-cu`, `nha-rieng`, `biet-thu-lien-ke`, `nha-mat-pho`, `shophouse-nha-pho-thuong-mai`, `dat-nen-du-an`, `dat`, `condotel`, `kho-nha-xuong` | `can-ho-chung-cu` |
| `--district` | `quan-1`…`quan-12`, `go-vap`, `binh-thanh`, `tan-binh`, `tan-phu`, `phu-nhuan`, `binh-tan`, `thu-duc`, `cu-chi`, `hoc-mon`, `binh-chanh`, `nha-be`, `can-gio`, `tp-hcm` | `tp-hcm` |
| `--price` | `MIN-MAX` in triệu (millions VND), e.g. `3000-5000` | none |
| `--area` | `MIN-MAX` in m², e.g. `50-80` | none |
| `--page` | integer page number | `1` |

If the user gives "3-5 tỷ", convert to triệu: `3000-5000`. If "dưới 2 tỷ": `0-2000`. If "trên 10 tỷ": `10000-`.

---

## Step 2 — Scrape listings via Chrome

batdongsan.com.vn has anti-bot protection. **Always use the Chrome browser tool** (`mcp__claude-in-chrome__*`), never `curl`/`requests`/`fetch` from a script.

### Procedure

1. Load Chrome tools via `ToolSearch` (`tabs_context_mcp`, `tabs_create_mcp`, `navigate`, `read_page`, `get_page_text`).
2. Call `tabs_context_mcp` first to understand current tab state.
3. Create a new tab pointing at the URL from Step 1.
4. Use `read_page` or `get_page_text` to extract listing cards.
5. Parse each card for: title, price, area, beds/WC, address, link.
6. For pagination, append `/p2`, `/p3`, etc. to the URL path (before query string).
7. Stop when you have 15–30 unique listings or results run out.

### Card extraction hints

- Listings are in cards; the title is typically an `<a>` or `<h3>` with the listing URL.
- Price/area/beds sit in labeled badges or a spec row under the title.
- Address is usually the last text line inside a card.
- VIP/promoted posts are interleaved — prefer real listings with explicit price/area.

### Deduplication

Different posts often advertise the same project (e.g., *"Topaz Elite"* posted by 5 brokers). Gather:

- **One entry per project name**
- **price** = `"<min>-<max> ty"` across matching posts
- **area** = `"<min>-<max>m2"` across matching posts
- **note** = representative broker or investor

Normalize every entry to the schema in `references/data-format.md`.

---

## Step 3 — Resolve coordinates via Google Maps

For every unique project, obtain `lat`/`lng`:

1. `navigate` Chrome to `https://www.google.com/maps/search/{project-name}+{district}`
2. Wait for map load (short `sleep` via browser wait, not shell).
3. Read the current URL — it will contain `@<lat>,<lng>,<zoom>z`.
4. Parse lat/lng as decimals.

### Fallbacks (in order)

1. If name-based search misses, retry with the full address.
2. If still missing, load `references/tphcm-districts.json` and use `center_coords[<district>]`.
3. Never leave `lat`/`lng` as `null`/`0` — downstream map will render incorrectly.

### Optimization

Batch the lookups: open a few tabs at once, or iterate sequentially with short pauses. Aim to resolve all 15–30 projects in one pass.

---

## Step 4 — Generate Excel

```bash
python scripts/generate_excel.py \
  --data projects.json \
  --output "/path/to/Chung_Cu_Q8_3-5ty.xlsx" \
  --title "Chung Cu Q8 3-5 Ty"
```

### Output structure

- **Sheet 1 — "Danh Sach BDS"**: STT · Du An · Loai · Khoang Gia · Dien Tich · Phong Ngu · WC · Dia Chi · Quan · Ghi Chu · Link BDS
- **Sheet 2 — "Toa Do (Map)"**: Du An · Quan · Lat · Lng · Gia · Dia Chi (for Google My Maps import)

Formatting applied automatically: dark blue header (#1F4E79, white bold), frozen header row, auto-filter on all columns, district color coding, hyperlink cells, fitted column widths, thin borders.

`openpyxl` is auto-installed on first run if missing.

---

## Step 5 — Generate HTML map

```bash
python scripts/generate_map.py \
  --data projects.json \
  --output "/path/to/map.html" \
  --title "Chung Cu Q8 3-5 Ty"
```

### Why not substitute placeholders by hand

`assets/map_template.html` contains `{{PROJECTS_JSON}}`, `{{DISTRICTS_JSON}}`, `{{COLORS_JSON}}`, `{{TITLE}}`, `{{SUBTITLE}}`. Doing the substitution via `bash` heredoc corrupts `<!DOCTYPE html>` into `<\!DOCTYPE html>` because `!` is a bash history expansion. `generate_map.py` reads the template with Python and writes bytes directly — no escaping issues.

### Output features

- Leaflet 1.9.4 + OpenStreetMap tiles (only external dep — CSS/JS is inline)
- 22 TPHCM district polygons with dashed borders, 0.08 fill opacity, auto-labeled centers
- Numbered circle markers with popups (name, price, area, beds, address, source link)
- Right-side panel (320px) with stats, district filter buttons, scrollable listing
- Click listing row → zoom to marker; click filter → filter by district
- Responsive: panel moves below map on narrow screens

---

## Step 6 — Verify & deliver

1. **HTML sanity check**: `Read` the first line of the generated HTML — must be exactly `<!DOCTYPE html>` (not `<\!DOCTYPE html>`).
2. **Excel sanity check**: `Read` or `stat` the xlsx — file size must be > 5 KB.
3. **Provide links**: give the user `computer://` URLs for both files so they can open locally.
4. **Optional Chrome preview**: Chrome remote cannot open `file:///` directly — workaround is to navigate `example.com`, then inject the HTML via `document.open()` + `document.write()` using `javascript_tool`. Take a screenshot to confirm rendering.

Common failure modes and fixes are in SKILL.md's Troubleshooting section.
