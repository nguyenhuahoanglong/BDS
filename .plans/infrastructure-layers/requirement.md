# Requirement: Infrastructure Layers on BDS Map

## Overview
Add transportation infrastructure overlay layers to the existing BDS TPHCM Leaflet map, showing metro lines, expressways, and ring roads with visual status differentiation.

## Goal
Enable users to assess real estate investment potential by seeing proximity to major infrastructure — operational, under construction, and planned.

## Scope — 12 Routes

### Metro (5 tuyến)
| ID | Name | Status | Completion | Length |
|----|------|--------|-----------|--------|
| metro-1 | Tuyến 1: Bến Thành – Suối Tiên | ✅ Operational | 2024 | 19.7 km |
| metro-2 | Tuyến 2: Bến Thành – Tham Lương | 🔨 Construction | 2030 | 11.3 km |
| metro-3a | Tuyến 3A: Bến Thành – Tân Kiên | 📋 Planned | ~2031 | 19.9 km |
| metro-5 | Tuyến 5: Các quận phía Tây | 📋 Planned | TBD | 53.9 km |
| metro-6 | Tuyến 6: Tân Sơn Nhất – Phú Hữu | 📋 Planned | 2030 | 53.8 km |

### Expressways (4 tuyến)
| ID | Name | Status | Completion | Length |
|----|------|--------|-----------|--------|
| hw-ltdg | TPHCM – Long Thành – Dầu Giây | ✅ Operational (expanding) | — | 55 km |
| hw-tl | TPHCM – Trung Lương | ✅ Operational (expanding) | — | 40 km |
| hw-bllt | Bến Lức – Long Thành | 🔨 Construction | Q3/2026 | 57.8 km |
| hw-mb | TPHCM – Mộc Bài | 🔨 Construction | 2027 | 53 km |

### Ring Roads (3 tuyến)
| ID | Name | Status | Completion | Length |
|----|------|--------|-----------|--------|
| vd-2 | Vành đai 2 | 🔨 Partial (~50/64 km done) | 2027 | 64 km |
| vd-3 | Vành đai 3 | 🔨 Nearly complete | 06/2026 | 76.3 km |
| vd-4 | Vành đai 4 | 📋 Starting construction | Q2/2028 | 207 km |

## Design — Phương án A

### Line Style by Status
| Status | Style | Opacity | dashArray |
|--------|-------|---------|-----------|
| ✅ Hoàn thành | Solid, 4px | 0.9 | none |
| 🔨 Đang xây | Dashed, 4px | 0.7 | "12,8" |
| 📋 Quy hoạch | Dotted, 3px | 0.45 | "4,10" |

### Color by Type
| Type | Color Strategy |
|------|---------------|
| Metro | Each line gets a unique color |
| Expressway | All #1565C0 (dark blue) |
| Ring Road | All #7B1FA2 (purple) |

### UI Elements
- **Layer control**: 3 group toggles (Metro / Cao tốc / Vành đai)
- **Click popup**: Name, status label, completion year, length
- **Legend**: Line style samples with status labels
- **Metro stations**: Small circle markers on operational lines

## Files Changed
1. `references/tphcm-infrastructure.json` — NEW
2. `assets/map_template.html` — UPDATE
3. `scripts/generate_map.py` — UPDATE
4. `index.html` — REGENERATE

## Acceptance Criteria
- [ ] AC1: All 12 routes render as polylines with correct status styling
- [ ] AC2: Layer control toggles Metro/Highway/Ringroad groups on/off
- [ ] AC3: Click any route → popup with name, status, year, length
- [ ] AC4: Legend shows 3 line styles with Vietnamese labels
- [ ] AC5: Metro Line 1 shows station markers
- [ ] AC6: Existing project markers and district polygons unaffected
- [ ] AC7: Map loads without JS errors
