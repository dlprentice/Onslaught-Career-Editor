# Goodies Asset Matrix Evidence - 2026-05-07

## Scope

This pass built a public-safe matrix from the packed asset manifest generated from the user's read-only PC install. The matrix answers which Goodies rows are backed by shipped Goodie archives with texture references, mesh references, or metadata-only entries.

Raw generated JSON remains ignored/private under:

```text
subagents/goodies-asset-matrix/current/goodies-asset-matrix.json
```

## Command

```powershell
py -3 tools\goodies_asset_matrix.py --check
```

Result: PASS

Important output:

```text
PASS: wrote subagents/goodies-asset-matrix/current/goodies-asset-matrix.json
goodie archives: 232 / 233 displayable slots
unique refs resolved: textures 206/206, meshes 42/42
```

## Public-Safe Summary

Source manifest: `subagents/asset-coverage-2026-05-07/packed-asset-manifest.json`

Family counts:

| Family | Count |
| --- | ---: |
| Texture only | 149 |
| Texture + mesh | 45 |
| Metadata only | 38 |

Unique `GDIE` reference resolution:

| Ref type | Resolved | Total |
| --- | ---: | ---: |
| Textures | 206 | 206 |
| Meshes | 42 | 42 |

Source-grid/resource grouping:

| Group | Range | Archives | Resource family summary | Notes |
| --- | ---: | ---: | --- | --- |
| Character bios | 0-7 | 8 | 8 texture-only | Visible in source grid. |
| Unit/gallery resources | 8-65 | 58 | 44 texture+mesh, 14 texture-only | Visible in source grid; current best target for model-viewer work. |
| Race level unlocks | 66-70 | 5 | 5 metadata-only | Visible in source grid. |
| Goodie resources 71-73 | 71-73 | 3 | 3 texture-only | Shipped archives exist and resolve as texture-only entries, but current source `get_goodie_number` does not expose them in the visible wall rows. |
| Developer items | 74-77 | 4 | 1 texture+mesh, 1 texture-only, 2 metadata-only | Visible in source grid. |
| Concept art | 78-200 | 123 | 123 texture-only | Visible in source grid. |
| FMV cutscenes | 201-232 | 31 | 31 metadata-only | Slot 232 is displayable FMV slot 33 but has no `goodie_232_res_PC.aya` archive. |

## What This Proves

- The shipped PC Goodie archives are real install resources, not just developer source-tree fixtures.
- Forty-five Goodie archives contain mesh-bearing entries in the packed manifest.
- All unique Goodie texture and mesh references reported by the packed manifest resolved to shipped resources.
- The current source grid exposes Goodies 0-70, 74-77, 78-200, and 201-232. Shipped resource archives 71-73 are statically classified as resolved texture-only entries, but still need runtime/non-grid investigation before claiming user-visible behavior.
- Goodie 78 is concept art, not part of the developer-item row.
- Follow-up evidence in `release/readiness/goodies_71_73_export_preview_2026-05-07.md` proves Goodies 71-73 each resolve to one existing exported PNG preview in the fresh full install catalog. The remaining question is runtime reachability, not asset/export presence.

## What This Does Not Prove

- It does not perform a full fresh export of every Goodie archive in this pass.
- It does not prove final textured/animated WinUI model viewing.
- It does not prove live runtime Goodies unlock or display replay.
- It does not permit committing extracted assets, raw manifests, screenshots, or frames.

## Next Targets

- Use the unit/gallery Goodies 8-65 as the first model-viewer hardening target because they contain the largest mesh-bearing set.
- Investigate whether Goodies 71-73 are hidden, cut, platform-specific, or surfaced through a runtime/non-grid path.
- Replay a copied-profile Goodies wall selection for representative texture-only, texture+mesh, metadata-only, and FMV slots under the windowed patch.
