# Ghidra Wave900 Through Wave1060 Recheck

Status: complete local static evidence gate
Date: 2026-06-01
Scope: `wave900-plus-through-wave1060-recheck`

This note extends the Wave900-plus static recheck boundary through Wave1060. Wave900 remains the loaded-Ghidra export-contract function-quality closure point; Wave1060 adds comment/tag normalization for the DXCompass lifecycle/render-support surface.

Wave1060 (`dxcompass-lifecycle-review-wave1060`) re-read seven primary DXCompass lifecycle/render rows and two adjacent context rows, then saved function tags plus one stale caller-comment correction: `0x00406040 CDXCompass__GetTrackedPositionX`, `0x0040c630 CDXCompass__GetTrackedPositionY`, `0x004270e0 CDXCompass__InitMarkerArrays`, `0x00427110 CDXCompass__LoadTextures`, `0x00427190 CDXCompass__DestroyTextures`, `0x00427200 CDXCompass__Reset`, `0x00427210 CDXCompass__Render`, `0x0053be40 CDXCompass__Init`, and `0x0053c1d0 CDXCompass__BuildRingGeometry`.

Fresh evidence:

- Primary pre exports: `7` metadata rows, `7` tag rows, `12` xref rows, `731` function-body instruction rows, and `7` decompile rows.
- Context pre exports: `13` metadata rows, `13` tag rows, `14` xref rows, `2339` function-body instruction rows, and `13` decompile rows.
- Post tagged exports: `9` metadata rows, `9` tag rows, `15` xref rows, `1081` function-body instruction rows, and `9` decompile rows.
- Dry/apply/final-dry sequence: dry `updated=0 skipped=0 tags_added=110 missing=0 bad=0`; apply `updated=9 skipped=0 tags_added=110 missing=0 bad=0`; final dry `updated=0 skipped=9 tags_added=0 missing=0 bad=0`.
- Comment-correction sequence: dry `updated=0 skipped=8 tags_added=0 comment_updated=1 missing=0 bad=0`; apply `updated=1 skipped=8 tags_added=0 comment_updated=1 missing=0 bad=0`; final dry `updated=0 skipped=9 tags_added=0 comment_updated=0 missing=0 bad=0`.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1148/1509 = 76.08%`.
- Wave911 top-500 coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260601-205027_post_wave1060_dxcompass_lifecycle_review_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`.

Validation command:

```powershell
npm run test:ghidra-wave900-plus-through-wave1060-recheck
```

Boundary note: this aggregate gate is static documentation/evidence hygiene. Runtime compass/HUD rendering behavior, exact `CHud`/`CDXCompass`/battle-engine context layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1060; dxcompass-lifecycle-review-wave1060; 0x00406040 CDXCompass__GetTrackedPositionX; 0x0040c630 CDXCompass__GetTrackedPositionY; 0x004270e0 CDXCompass__InitMarkerArrays; 0x00427110 CDXCompass__LoadTextures; 0x00427190 CDXCompass__DestroyTextures; 0x00427200 CDXCompass__Reset; 0x00427210 CDXCompass__Render; 0x0053be40 CDXCompass__Init; 0x0053c1d0 CDXCompass__BuildRingGeometry; 812/1408 = 57.67%; 1148/1509 = 76.08%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260601-205027_post_wave1060_dxcompass_lifecycle_review_verified; tag normalization.
