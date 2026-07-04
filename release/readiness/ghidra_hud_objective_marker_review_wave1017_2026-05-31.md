# Ghidra HUD Objective Marker Review Wave1017 Readiness Note

Status: complete read-only static review
Date: 2026-05-31
Scope: `hud-objective-marker-review-wave1017`

Wave1017 re-read three top-500 Wave911 risk-surface HUD overlay helper rows as a narrow continuity/body review. This is intentionally not a correction wave: Wave411 already corrected the owner/signature rows, Wave1004 re-read the broader HUD render-body continuum, and Wave1013 re-read the same helper band as HUD lifecycle/render-support context. Wave1017 performs fresh body-level read-back on the three selected rows and preserves the current saved Ghidra state.

Primary anchors:

| Address | Read-back evidence |
| --- | --- |
| `0x00484340 CHud__RenderTargetMarkers3D` | Called by `0x004879e0 CHud__RenderOverlayForViewpoint` at `0x00487b91`; applies HUD overlay sprite state, uses active HUD viewpoint/target fields, reads `CBattleEngine__GetInterpolatedAutoAimPos`, and draws target-marker textures. |
| `0x004858d0 CHud__RenderObjectiveProgressGaugeAndHeadingNeedle` | Called by `0x004879e0 CHud__RenderOverlayForViewpoint` at `0x00487b98`; applies overlay render state, draws objective-gauge sprites, reads `CBattleEngine__GetWeaponCharge`, and rotates heading-needle context from `CBattleEngine__GetInterpolatedEulerOrientation`. |
| `0x00486940 CHud__RenderObjectiveSlotFillPanel` | Called by `0x004879e0 CHud__RenderOverlayForViewpoint` at `0x00487ba6`; branches through energy/ammo/overheat state using `CBattleEngine__IsEnergyWeapon`, `CBattleEngine__GetWeaponAmmoPercentage`, `CBattleEngine__IsWeaponOverheated`, and `CBattleEngine__GetWeaponAmmoCount`, then draws fill sprites or ammo text. |

Read-back evidence:

- Target exports: `3` metadata rows, `3` tag rows, `3` xref rows, `1267` body-instruction rows, and `3` decompile rows.
- Context exports: `11` metadata rows, `26` xref rows, `4103` body-instruction rows, and `11` decompile rows.
- Context anchors include `0x00482590 CHud__RenderTargetIndicatorOverlay`, `0x00484c50 CHud__RenderTacticalRadarContacts`, `0x004857e0 HudOverlay__DrawSpriteQuad`, `0x00485830 CHud__SelectMarkerTextureIndexByUnitFlags`, `0x00485d50 CHud__RenderObjectiveStatusPanel`, `0x00486e00 CHud__RenderWorldTargetSprites`, `0x004879e0 CHud__RenderOverlayForViewpoint`, `0x00487bc0 CHud__RenderOverlay`, `0x00488090 CHud__RenderActiveHudComponentPass`, `0x004881e0 CHud__ResolveOverlaySlotRenderMode`, and `0x0053ecc0 CDXEngine__PostRender`.
- Queue closure remains `6238/6238 = 100.00%` with `0` commentless functions, `0` exact-undefined signatures, and `0` `param_N`.
- Wave911 focused re-audit progress remains `513/1408 = 36.43%` because these three rows are top-500 risk-ranked but not focused-correction TSV rows.
- Expanded static surface progress advances to `742/1493 = 49.70%`.
- Wave911 top-500 risk-ranked coverage advances to `442/500 = 88.40%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-201957_post_wave1017_hud_objective_marker_review_verified`, `19` files, `173968263` bytes, `DiffCount=0`, `HashDiffCount=0`.

Mutation status: read-only PASS. No Ghidra mutation, rename, signature change, comment change, tag change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation was performed.

Probe token anchor: Wave1017; hud-objective-marker-review-wave1017; 0x00484340 CHud__RenderTargetMarkers3D; 0x004858d0 CHud__RenderObjectiveProgressGaugeAndHeadingNeedle; 0x00486940 CHud__RenderObjectiveSlotFillPanel; 0x004879e0 CHud__RenderOverlayForViewpoint; 513/1408 = 36.43%; 742/1493 = 49.70%; 442/500 = 88.40%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260531-201957_post_wave1017_hud_objective_marker_review_verified; no mutation.

Boundary note: this proves static read-back coherence for selected HUD overlay helper rows only. Runtime HUD behavior, visible render ordering, exact source-body identity, concrete `CHud`/`BattleEngine`/texture/layout semantics, BEA patching, and rebuild parity remain separate proof.
