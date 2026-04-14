# Implementation Plan: Infrastructure Layers

**Status**: done  
**Created**: 2026-04-13

## Wave 1 — Data Layer
### WP1: Create infrastructure data file
- **File**: `references/tphcm-infrastructure.json`
- **Description**: JSON array of 12 route objects with coordinates, metadata, styling
- **ACs**: Prerequisite for AC1-AC5
- **Status**: pending

## Wave 2 — Code Changes (parallel)
### WP2: Update map template
- **File**: `assets/map_template.html`
- **Description**: Add `{{INFRASTRUCTURE_JSON}}` placeholder, infrastructure rendering JS, layer control, legend, popups, station markers
- **ACs**: AC1, AC2, AC3, AC4, AC5, AC6, AC7
- **Status**: pending

### WP3: Update map generator script
- **File**: `scripts/generate_map.py`
- **Description**: Add `--infrastructure` parameter, load JSON, substitute placeholder
- **ACs**: Prerequisite for regeneration
- **Status**: pending

## Wave 3 — Generate & Verify
### WP4: Regenerate and test
- **Files**: `index.html` (output)
- **Description**: Run generate_map.py with infrastructure data, verify in browser
- **ACs**: AC1-AC7 (full verification)
- **Status**: pending

## AC → WP Mapping
| AC | WP |
|----|-----|
| AC1 | WP1 + WP2 |
| AC2 | WP2 |
| AC3 | WP2 |
| AC4 | WP2 |
| AC5 | WP1 + WP2 |
| AC6 | WP2 |
| AC7 | WP2 + WP3 |

## Iteration Log
- 2026-04-13: Plan created, starting Wave 1
