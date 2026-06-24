# Goodies Catalog Linkage Evidence - 2026-05-07

## Scope

This pass checked whether a full private Goodies catalog links Goodie rows to exported texture and model catalog rows using the same normalized matching shape as the WinUI Asset Library.

Raw generated JSON remains ignored/private under:

```text
subagents/goodies-catalog-linkage/current/goodies-catalog-linkage.json
```

## Command

```powershell
py -3 tools\goodies_catalog_linkage_check.py --check
```

Result: PASS

Important output:

```text
PASS: wrote subagents/goodies-catalog-linkage/current/goodies-catalog-linkage.json
Goodie linkage: textures 194/194, models 45/45, videos 34 (33 archive-backed, 1 catalog-only)
```

## Public-Safe Summary

Source catalog: `subagents/goodie_catalog_probe_2026-05-07/asset_catalog/catalog.json`

| Check | Matched | Total |
| --- | ---: | ---: |
| Goodies with primary texture refs | 194 | 194 |
| Goodies with primary mesh refs | 45 | 45 |
| Goodies with video ids | 34 | 34 |
| Video Goodies with source archives | 33 | 34 |
| Catalog-only video Goodies | 1 | 34 |

Catalog Goodie kind counts:

| Kind | Count |
| --- | ---: |
| Artwork | 149 |
| Level | 5 |
| Model | 45 |
| Video | 34 |

## What This Proves

- With the full private Goodies catalog loaded, every texture-bearing Goodie row can link to an exported texture catalog row.
- Every model-bearing Goodie row can link to an exported loose mesh catalog row.
- The apparent video-count mismatch is intentional: 33 video Goodies are backed by `goodie_*_res_PC.aya` source archives, while Goodie 232 is a catalog-only handoff to cutscene 33 because the checked PC install has no `goodie_232_res_PC.aya` archive.
- The current WinUI Asset Library Goodie preview path has real catalog linkage for Goodie artwork/model rows when the matching exports are present.

## What This Does Not Prove

- It does not prove final textured/animated WinUI model rendering.
- It does not prove runtime Goodies wall replay in the running game.
- It does not commit or redistribute extracted assets, raw catalog content, paths, screenshots, frames, or proof JSON.
- It does not claim the bounded fixture catalog used by some automation contains the full Goodies corpus.

## Current Product Reality

WinUI currently shows:

- PNG preview for matched exported texture Goodies,
- FBX-derived wireframe preview for matched model Goodies,
- local FBX open action for full material review,
- Media-section handoff for Bink/FMV Goodies.

`release/readiness/goodies_preview_coverage_2026-05-07.md` adds the follow-up AppCore.Host coverage run: 194/194 texture-bearing Goodies are texture-preview-ready, 45/45 model-bearing Goodies have FBX export and wireframe coverage, 34/34 video Goodies have catalog video links, and the only rows without local preview are five level-unlock metadata rows.

The next product-hardening step is a richer in-app textured model viewer or a tighter export/open workflow around representative Goodies 8-65.
