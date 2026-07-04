# Ghidra HUD Overlay Helpers Correction - 2026-05-14

Status: public-safe static Ghidra evidence note

Wave411 corrected saved Ghidra metadata for nine HUD overlay helper functions adjacent to the Wave410 overlay root. This is serialized static Ghidra name/signature/comment/tag read-back only.

| Address | Prior saved state | Saved state | Static evidence summary |
| --- | --- | --- | --- |
| `0x00483530` | `CExplosionInitThing__RenderControllerSlotStatusPanel` | `void __thiscall CHud__RenderControllerSlotStatusPanel(void * this)` | Called by `CHud__RenderOverlayForViewpoint`; animates controller-slot status fields, calls `CHud__RenderSegmentedMeterBar`, formats timer/status text, and draws with the HUD font path. |
| `0x00484340` | `CExplosionInitThing__RenderTargetMarkers3D` | `void __thiscall CHud__RenderTargetMarkers3D(void * this)` | Called by `CHud__RenderOverlayForViewpoint`; uses CHud marker fields, applies overlay sprite state, reads `CBattleEngine__GetInterpolatedAutoAimPos`, and draws target-marker sprites. |
| `0x00484c50` | `CExplosionInitThing__RenderTacticalRadarContacts` | `void __thiscall CHud__RenderTacticalRadarContacts(void * this)` | Called by `CHud__RenderOverlayForViewpoint`; partitions visible units into temporary pointer sets, projects contacts using BattleEngine orientation, selects marker textures, draws radar markers, and clears temporary sets. |
| `0x004857e0` | `CExplosionInitThing__DrawHudSpriteQuad` | `void __cdecl HudOverlay__DrawSpriteQuad(float x, float y, void * texture, float argb_tint_bits)` | Owner-neutral HUD overlay sprite wrapper called repeatedly by the tactical radar helper; forwards sprite arguments to `CVBufTexture__DrawSpriteEx` with fixed depth `0.011`. |
| `0x00485830` | `CExplosionInitThing__SelectMarkerTextureIndexByUnitFlags` | `int __thiscall CHud__SelectMarkerTextureIndexByUnitFlags(void * this, void * unit)` | Corrects the old extra-argument shape; instruction read-back returns with `RET 0x4`, reads unit flags at `+0x34`, and returns CHud texture slots `+0x1a0/+0x1a4/+0x1a8`. |
| `0x004858d0` | `CExplosionInitThing__RenderObjectiveProgressGaugeAndHeadingNeedle` | `void __thiscall CHud__RenderObjectiveProgressGaugeAndHeadingNeedle(void * this)` | Called by `CHud__RenderOverlayForViewpoint`; draws objective gauge sprites, reads `CBattleEngine__GetWeaponCharge`, and rotates heading needle context through `CBattleEngine__GetInterpolatedEulerOrientation`. |
| `0x00485d50` | `CExplosionInitThing__RenderObjectiveStatusPanel` | `void __thiscall CHud__RenderObjectiveStatusPanel(void * this)` | Called by `CHud__RenderOverlayForViewpoint`; uses selection counts, weapon icon/name helpers, multiplayer lives context, and objective text drawing paths. |
| `0x00486940` | `CExplosionInitThing__RenderObjectiveSlotFillPanel` | `void __thiscall CHud__RenderObjectiveSlotFillPanel(void * this)` | Called by `CHud__RenderOverlayForViewpoint`; branches on energy-weapon status, ammo percentage, overheat state, ammo count, and fill-sprite/text drawing paths. |
| `0x00486e00` | `CExplosionInitThing__RenderWorldTargetSprites` | `void __thiscall CHud__RenderWorldTargetSprites(void * this)` | Called by `CHud__RenderOverlayForViewpoint`; uses CHud target fields, overlay state, target/lock projection, `CLockInfo__GetLockPercentage`, and `CUnitAI__GetWorldPositionForTargeting`. |

## Correction Boundary

The Wave410 caller chain now directly supports CHud ownership for these neighboring overlay helpers, because `CHud__RenderOverlayForViewpoint` dispatches seven of them with the same receiver. The sprite-quad wrapper at `0x004857e0` remains owner-neutral because the body is a thin cdecl draw wrapper, not a CHud method. Stuart's source snapshot still does not provide matching HUD implementation bodies, so exact source-body identity, concrete CHud/unit/radar layouts, local-variable names, and structure recovery remain queued for later review.

## Validation

- Headless dry run: `updated=0 skipped=9 created=0 would_create=0 renamed=0 would_rename=9 missing=0 bad=0`; `REPORT: Save succeeded`.
- Headless apply: `updated=9 skipped=0 created=0 would_create=0 renamed=9 would_rename=0 missing=0 bad=0`; `REPORT: Save succeeded`.
- Read-back verified `9` metadata rows, `9` tag rows, `18` xref rows, `9` target decompile exports, and `1` caller decompile export.
- Focused unit tests passed `2/2`, Python compile passed, and the direct/package-script probes passed.
- Refreshed queue telemetry reports `6028` functions, `1574` commented functions, `4454` commentless functions, `1909` undefined signatures, and `1843` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1574/6028 = 26.11%`; strict clean-signature `1511/6028 = 25.07%`.
- The live Ghidra project backup was verified on `[maintainer-local-backup-volume]` at `[maintainer-local-ghidra-backup-root]\BEA_20260514_094034_post_wave411_hud_overlay_helpers_verified` with `19` files, `154831751` bytes, and `HashDiffCount=0`.

## Claim Boundary

This note does not prove runtime HUD behavior, does not prove concrete CHud/unit/radar layouts, does not prove exact source-body identity, does not prove local-variable or structure recovery, does not prove rebuild parity, and does not involve launching or patching `BEA.exe`.
