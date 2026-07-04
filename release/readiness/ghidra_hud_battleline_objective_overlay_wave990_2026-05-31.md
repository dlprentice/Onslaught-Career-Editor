# Ghidra HUD Battleline Objective Overlay Wave990 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-31
Scope: `hud-battleline-objective-overlay-review-wave990`

Wave990 re-audited the HUD battleline/objective overlay join after the Wave900-Wave989 recheck gate. The pass saved two bounded Ghidra comment/tag normalizations and made no rename, no signature change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary saved normalizations:

| Address | Result |
| --- | --- |
| `0x0040dda0 CUnitAI__RefreshGridCooldownFromOccupiedCells` | Updated the saved comment from stale `CSquadNormal` grid wording to current `CFearGrid__GetOccupancyAtWorldVector` evidence. The helper is called by `0x00485d50 CHud__RenderObjectiveStatusPanel` at `0x004862af`, samples `DAT_008a9d7c` and `DAT_008a9d80`, and refreshes `this+0x2e8` when either occupancy grid is active. |
| `0x00414cb0 CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices` | Added Wave990 tags and refreshed the saved comment around the `0x00487d10 CHud__RenderBattleline` caller, battle-line list `DAT_00855140`, influence/deferred list `DAT_008550a0`, predicate `0x004e6610 SharedState__IsTimer88PendingAndState7CZero`, and `0x0053b5f0 CDXBattleLine__AppendOverlayVertex`. |

Context targets re-exported without mutation:

- `0x0042da00 Input__UpdateCursorCenterWithWindowScale`
- `0x0044c720 CFearGrid__GetOccupancyAtWorldVector`
- `0x00485d50 CHud__RenderObjectiveStatusPanel`
- `0x00487d10 CHud__RenderBattleline`
- `0x004e6610 SharedState__IsTimer88PendingAndState7CZero`
- `0x0053b5f0 CDXBattleLine__AppendOverlayVertex`

Read-back evidence:

- `ApplyHudBattlelineObjectiveOverlayWave990.java` dry: `updated=0 skipped=2 comment_only_updated=2 tags_added=19 missing=0 bad=0`
- `ApplyHudBattlelineObjectiveOverlayWave990.java` apply: `updated=2 skipped=0 comment_only_updated=2 tags_added=19 missing=0 bad=0`
- `ApplyHudBattlelineObjectiveOverlayWave990.java` final dry: `updated=0 skipped=2 comment_only_updated=0 tags_added=0 missing=0 bad=0`
- Post exports: `8` metadata rows, `8` tag rows, `13` xref rows, `1429` body-instruction rows, and `8` decompile rows.
- Queue closure after refresh remains `6222/6222 = 100.00%`, with `0` commentless functions, `0` exact-undefined signatures, and `0` `param_N` signatures.
- Wave911 focused re-audit progress is `441/1408 = 31.32%`; expanded static surface progress is `517/1478 = 34.98%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-041618_post_wave990_hud_battleline_objective_overlay_verified`, 19 files, 173837191 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The saved Ghidra project now records current HUD objective-panel and battleline overlay evidence for the selected rows.
- The stale `CSquadNormal` wording on `0x0040dda0` has been replaced with current `CFearGrid__GetOccupancyAtWorldVector` call evidence.
- The selected call spine is statically coherent: `CHud__RenderObjectiveStatusPanel -> CUnitAI__RefreshGridCooldownFromOccupiedCells -> CFearGrid__GetOccupancyAtWorldVector`, and `CHud__RenderBattleline -> CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices -> SharedState__IsTimer88PendingAndState7CZero / CDXBattleLine__AppendOverlayVertex`.

What remains unproven:

- Runtime HUD behavior.
- Runtime battleline or objective-panel rendering behavior.
- Exact `CHud`, `CUnitAI`, `CFearGrid`, or `CDXBattleLine` layouts.
- Exact source-body identity.
- BEA patching behavior.
- Rebuild parity.
