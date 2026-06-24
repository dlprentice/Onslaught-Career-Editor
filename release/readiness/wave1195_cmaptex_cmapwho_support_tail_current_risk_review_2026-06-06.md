# Wave1195 CMapTex/CMapWho Support-Tail Current-Risk Review

Status: complete static read-back evidence
Date: 2026-06-06
Tag: `wave1195-cmaptex-cmapwho-support-tail-current-risk-review`

Wave1195 accounts for `12 CMapTex/CMapWho support-tail score16 current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator. It consolidates rebuild-relevant static contracts for residual CMapTex reset/downsample/copy/deserialize helpers and CMapWho/CMapWhoEntry iterator, bounds, radius-level, debug-draw, and invalidation helpers.

The pass saved comment/tag normalization only: no rename, no signature change, no function-boundary change, and no executable-byte change.

Representative anchors:

| Address | Function | Static contract |
| --- | --- | --- |
| `0x00491180` | `CMapTex__Reset` | Writes `-1` to `+0x0c`, frees owned pointers at `+0x00/+0x08` through `OID__FreeObject`, and clears each slot. |
| `0x00491340` | `CMapTex__DownsampleTexture` | Downsamples 2x2 source texels using width at `+0x18`, with separate signed averaging for the fourth channel. |
| `0x004915d0` | `CMapTex__CopyFromOther` | Refreshes metadata, halves destination width, allocates output, and calls `CMapTex__DownsampleTexture` for each source slice. |
| `0x004916c0` | `CMapTex__Deserialize` | Reads a `0x4c-byte CMapTex header`, allocates `count << 0xc` primary data and `count << 10` secondary data, then reads payloads. |
| `0x00491900` | `CMapWhoEntry__Init` | Clears `+0x00/+0x04 next/previous` links. |
| `0x00491d80` | `CMapWho__SetIteratorFromSectorHead` | Writes sector head at `+0x04` into `this+0x00` and returns the current entry. |
| `0x00491d90` | `CMapWho__AdvanceIteratorAndGetCurrent` | Advances through the current entry next pointer and returns the current entry. |
| `0x00491da0` | `CMapWho__IsSectorCoordInBounds` | Validates level `0..4` and x/y sector bounds against `64 >> (4 - level)`. |
| `0x00491df0` | `CMapWho__SetupNextRadiusLevel` | Uses query radius at `+0x28` and level cell scale to seed radius-query bounds/current sector fields. |
| `0x00492860` | `CMapWho__DebugDrawSector` | Builds a per-level debug volume and calls `CThing__RenderDebugVolumeOverlay`. |
| `0x00492950` | `CMapWho__DebugDraw` | Traverses sectors, filters owners through `CMapWhoEntry__GetOwner`, and draws one qualifying entry per sector. |
| `0x00492c60` | `CMapWhoEntry__Invalidate` | Writes `-1` to entry level field `+0x0c`. |

Read-back evidence:

| Item | Result |
| --- | --- |
| Pre/post rows | `12` metadata rows, `12` tag rows, `37 xref rows`, `561 instruction rows`, and `12 decompile rows` |
| Dry run | `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=12 tags_added=132 missing=0 bad=0` |
| Apply | `updated=12 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=12 tags_added=132 missing=0 bad=0`; `REPORT: Save succeeded` |
| Final dry | `updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0` |
| Backup | `G:\GhidraBackups\BEA_20260606-200142_post_wave1195_cmaptex_cmapwho_support_tail_current_risk_review_verified` |

Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt. Expanded static surface remains `1560/1560 = 100.00%`. Wave1108 current focused accounting is now `877/1179 = 74.39%`; current risk candidates: 6166; current focused candidates: 1142; live regenerated current focused candidates: 1142; remaining active focused work: 302; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Fresh quality snapshot and current-risk rank were regenerated after the Ghidra write. The live rank still keeps many reviewed rows in focused candidates because expected source-identity, exact-layout, runtime/rebuild, generic-name-shape, and critical-family signals remain intentionally deferred; the continuity accounting records that these rows have received bounded static current-risk treatment.

Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference. Exact CMapTex/CMapWho/CMapWhoEntry/sector/texture/pixel layouts, exact source-body identity, runtime terrain texture behavior, runtime spatial-query behavior, runtime debug rendering behavior, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Probe token anchor: Wave1195; wave1195-cmaptex-cmapwho-support-tail-current-risk-review; 877/1179 = 74.39%; 12 CMapTex/CMapWho support-tail score16 current-risk rows; current focused candidates: 1142; live regenerated current focused candidates: 1142; remaining active focused work: 302; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=12 skipped=0; comment_only_updated=12; tags_added=132; final dry updated=0 skipped=12; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consult used; no Cursor/Composer; CMapTex__Reset; CMapTex__DownsampleTexture; CMapTex__CopyFromOther; CMapTex__Deserialize; CMapWhoEntry__Init; CMapWho__SetIteratorFromSectorHead; CMapWho__AdvanceIteratorAndGetCurrent; CMapWho__IsSectorCoordInBounds; CMapWho__SetupNextRadiusLevel; CMapWho__DebugDrawSector; CMapWho__DebugDraw; CMapWhoEntry__Invalidate; 0 / 0 / 0; 6411/6411 = 100.00%; 37 xref rows; 561 instruction rows; 12 decompile rows; G:\GhidraBackups\BEA_20260606-200142_post_wave1195_cmaptex_cmapwho_support_tail_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.
