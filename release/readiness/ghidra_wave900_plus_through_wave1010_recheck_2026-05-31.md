# Ghidra Wave900+ Through Wave1010 Recheck Note

Status: PASS
Date: 2026-05-31
Scope: `ghidra-wave900-plus-through-wave1010-recheck`

Wave900-Wave1010 aggregate recheck extends the Wave900+ structural evidence gate after Wave1010 BattleEngine zoom/auto-aim review and `CBattleEngine__HandleEvent` boundary recovery. This is structural static evidence validation for the loaded Ghidra project and repo evidence surfaces, not runtime proof, exact source-layout proof, BEA patching proof, or rebuild parity.

Wave1010 anchor: `battleengine-weapon-autoaim-review-wave1010`; `0x00409e80 CBattleEngine__AutoZoomOut`; `0x00409e90 CBattleEngine__ZoomOut`; `0x00409ec0 CBattleEngine__ZoomIn`; `0x00409f70 CBattleEngine__ChangeWeapon`; `0x0040ac50 CBattleEngine__Rearm`; `0x0040acc0 CBattleEngine__CalcUnitOverCrossHair`; `0x0040b120 CBattleEngine__UpdateAutoAim`; `0x0040b6d0 CBattleEngine__HandleAutoAim`; `0x0040c180 CBattleEngine__HandleEvent`.

Verified recheck result:

- Readiness notes: `113`
- Covered waves: `111`
- Package probe scripts: `109`
- Evidence bases: `109`
- Backup references: `111`
- Apply scripts: `35`
- Wave982-Wave1010 direct probes: `29` total, `1` current pass, `28` classified stale-current failures, `0` disallowed evidence or unclassified failures
- Current queue closure: `6234/6234 = 100.00%`
- Wave911 focused re-audit progress: `505/1408 = 35.87%`
- Expanded static surface progress: `701/1489 = 47.08%`
- Wave911 top-500 risk-ranked coverage: `409/500 = 81.80%`
- Verified Wave1010 backup: `G:\GhidraBackups\BEA_20260531-163000_post_wave1010_battleengine_zoom_autoaim_review_verified`

The direct-probe stale-current classifications are expected when older focused probes still assert historical baton/current-doc totals that have intentionally rolled forward. The aggregate gate treats those as stale-current only when the line-level classifier finds no metadata, signature, tag, decompile, log, backup, lock, or unclassified evidence mismatch.

Boundary note: Wave1010 confirms saved static boundary/name/signature/comment/tag coherence for `0x0040c180 CBattleEngine__HandleEvent` plus read-back coherence for the surrounding BattleEngine zoom/change/rearm/crosshair/auto-aim anchors. Runtime zoom, weapon switching, rearm, crosshair, auto-aim, or event-dispatch behavior; exact source-body identity; concrete layouts; BEA patching; and rebuild parity remain separate proof.
