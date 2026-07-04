# Ghidra BattleEngine Zoom Auto-Aim Review Wave1010 Readiness Note

Status: complete saved static read-back evidence
Date: 2026-05-31
Scope: `battleengine-weapon-autoaim-review-wave1010`

Wave1010 re-reviewed the BattleEngine zoom/change/rearm/crosshair/auto-aim spine and recovered one missing source-backed event-dispatch function boundary at `0x0040c180 CBattleEngine__HandleEvent`. The pass created one function object, saved its name/signature/comment/tags, refreshed the function-quality queue to `6234/6234 = 100.00%`, and made no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary reviewed anchors:

| Address | Evidence |
| --- | --- |
| `0x00409e80 CBattleEngine__AutoZoomOut` | Carried-forward source-parity zoom helper; xrefs from JetPart and WalkerPart weapon-change helpers. |
| `0x00409e90 CBattleEngine__ZoomOut` | Source-parity zoom-out helper reached from `CPlayer__ReceiveButtonAction`. |
| `0x00409ec0 CBattleEngine__ZoomIn` | Source-parity zoom-in helper reached from `CPlayer__ReceiveButtonAction`. |
| `0x00409f70 CBattleEngine__ChangeWeapon` | Source bridge for weapon cycling, timestamp, and HUD sample flow. |
| `0x0040ac50 CBattleEngine__Rearm` | Source bridge for six-store recharge/clamp flow; remaining raw caller at `0x004d8d07` stays deferred. |
| `0x0040acc0 CBattleEngine__CalcUnitOverCrossHair` | Source bridge for view-ray trace/reader update; xrefs from `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles` and recovered `CBattleEngine__HandleEvent`. |
| `0x0040b120 CBattleEngine__UpdateAutoAim` | Source bridge for predictive/direct target yaw-pitch computation and smoothing. |
| `0x0040b6d0 CBattleEngine__HandleAutoAim` | Source bridge for MapWho candidate scan, range/angle/trace filters, and event `0x1773` reschedule. |

Recovered boundary anchor:

| Address | Evidence |
| --- | --- |
| `0x0040c180 CBattleEngine__HandleEvent` | Pre-mutation metadata was missing, while DATA/vtable ref `0x005d89c4` pointed at `0x0040c180`. The prior saved function `CBattleEngine__StartDieProcess` ends at `0x0040c17b RET`; the next saved function `CBattleEngine__CanSpawnBurstForResolvedEntry` starts at `0x0040c2e0`. The recovered body reads `event+0x04`, handles event ids including `0x1770`, `0x1771`, `0x1772`, and `0x1773`, calls `CBattleEngine__HandleAutoAim` at `0x0040c2ad`, calls `CBattleEngine__CalcUnitOverCrossHair` at `0x0040c2c3`, updates an active reader through `CGenericActiveReader__SetReader`, and matches `references/Onslaught/BattleEngine.cpp:CBattleEngine::HandleEvent` at the static source-parity level. |

Read-back evidence:

- Pre-review exports: 8 metadata rows, 8 tag rows, 11 xref rows, 1951 body-instruction rows, and 8 decompile rows.
- Raw caller/boundary evidence: 196 raw caller instruction rows, 546 raw HandleEvent instruction rows, pre-boundary metadata missing at `0x0040c180`, and one DATA xref row from `0x005d89c4` to `0x0040c180`.
- Vtable/context evidence: 192 vtable-slot rows and 4 vtable-type rows around the candidate pointer ranges.
- Boundary apply dry/apply/final dry: dry reported `updated=1 skipped=0 created=0 would_create=1 renamed=0 would_rename=0 signature_updated=1 comment_updated=1 tag_updated=1 missing=0 bad=0`; apply reported `updated=1 skipped=0 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_updated=1 tag_updated=1 missing=0 bad=0`; final dry reported `updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_updated=0 tag_updated=0 missing=0 bad=0`.
- Final exports: 9 metadata rows, 9 tag rows, 12 xref rows, 2044 body-instruction rows, and 9 decompile rows.
- Queue closure after refresh: `6234/6234 = 100.00%`, with 0 commentless functions, 0 exact-undefined signatures, and 0 `param_N` signatures.
- Re-audit progress after Wave1010: Wave911 focused `505/1408 = 35.87%`; expanded static surface `701/1489 = 47.08%`; Wave911 top-500 risk-ranked `409/500 = 81.80%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-163000_post_wave1010_battleengine_zoom_autoaim_review_verified`, 19 files, 173935495 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The recovered `CBattleEngine__HandleEvent` row now exists as a saved function object in the loaded Ghidra database.
- The recovered row has saved bounded name, signature, comment, and `battleengine-weapon-autoaim-review-wave1010` / `wave1010-readback-verified` tags.
- Static xref, instruction, decompile, vtable/DATA, queue-refresh, source-parity, and backup evidence support the saved boundary recovery and BattleEngine event-dispatch classification.

What remains unproven:

- Runtime zoom, weapon switching, rearm, crosshair, auto-aim, or event-dispatch behavior.
- Concrete `CBattleEngine`, `CEvent`, weapon, target-reader, or active-reader layouts beyond observed offsets.
- Exact source-body identity beyond the bounded static source-parity match.
- BEA patching behavior.
- Rebuild parity.
