# Project Object — JSON Data Contract

This is the shared input schema consumed by `generate_excel.py`, `generate_map.py`, and `validate_projects.py`. Every listing collected during scraping (Step 2) must be normalized into this shape before running any downstream script.

## Schema

Each entry is a JSON object with the following fields. Only `name`, `district`, `lat`, `lng` are strictly required for the map; Excel tolerates missing fields.

| Field | Type | Required | Example | Notes |
|---|---|---|---|---|
| `name` | string | yes | `"Topaz Elite"` | Dự án / listing title. Dedupe by name when multiple posts share one project. |
| `type` | string | no | `"Chung cu"` | Property type. Defaults to `"Chung cu"` if missing. |
| `price` | string | recommended | `"3.2-4.8 ty"` | Free-text price range. Use `"Thoa thuan"` if unknown. Keep min-max form when multiple posts exist. |
| `area` | string | recommended | `"60-92m2"` | Free-text area range. |
| `beds` | string | no | `"2-3"` | Bedroom count range. |
| `wc` | string | no | `"2"` | Bathroom count. |
| `addr` | string | recommended | `"Cao Lo, P.4, Q.8"` | Street + ward + district. |
| `district` | string | yes | `"Q.8"` | Canonical district label. Must match a key in `tphcm-districts.json` for polygon/color lookup. See canonical keys below. |
| `note` | string | no | `"Van Thai Land, 3 block"` | Investor, block count, broker — anything noteworthy. |
| `link` | string | recommended | `"https://batdongsan.com.vn/..."` | Source listing URL. Becomes hyperlink in Excel. |
| `lat` | number | yes (map) | `10.7392189` | Decimal latitude from Google Maps `@lat,lng,zoom` URL. |
| `lng` | number | yes (map) | `106.6797322` | Decimal longitude. |

## Canonical district keys

Use these exact strings in the `district` field so both Excel color mapping and map polygon lookup resolve correctly:

```
Q.1, Q.3, Q.4, Q.5, Q.6, Q.7, Q.8, Q.10, Q.11, Q.12,
Go Vap, Binh Thanh, Tan Binh, Tan Phu, Phu Nhuan, Binh Tan,
Thu Duc, Cu Chi, Hoc Mon, Binh Chanh, Nha Be, Can Gio
```

No Vietnamese diacritics (ASCII only) to keep filename-safe and Excel/HTML compatible.

**Note on polygon lookup**: `tphcm-districts.json` uses the long-form keys (`"Quan 8"`, `"Q.Go Vap"`, `"TP.Thu Duc"`) for polygon coordinates, while the `district` field in project records uses the short form above (`"Q.8"`, `"Go Vap"`, `"Thu Duc"`). Both `generate_excel.py` and `generate_map.py` handle this mapping internally via fuzzy matching — callers don't need to care.

## Example

```json
[
  {
    "name": "Topaz Elite",
    "type": "Chung cu",
    "price": "3.2-4.8 ty",
    "area": "60-92m2",
    "beds": "2-3",
    "wc": "2",
    "addr": "Cao Lo, P.4, Q.8",
    "district": "Q.8",
    "note": "Van Thai Land, 3 block",
    "link": "https://batdongsan.com.vn/ban-can-ho-chung-cu-du-an-topaz-elite",
    "lat": 10.7392189,
    "lng": 106.6797322
  }
]
```

## Collection rules

1. **Dedupe by project** — multiple listings for the same project = one entry with combined `price`/`area` ranges.
2. **Preserve source link** — use the first (or most representative) listing URL.
3. **District fallback** — if Google Maps coordinate lookup fails, use the district center from `tphcm-districts.json → center_coords[district]`.
4. **Target 15–30 entries** per search — enough to be useful without overwhelming the map.
