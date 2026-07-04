# Ghidra HUD Overlay Correction - 2026-05-14

Status: public-safe static Ghidra evidence note

Wave410 corrected saved Ghidra metadata for three HUD overlay functions. This is serialized static Ghidra name/signature/comment/tag read-back only.

| Address | Prior saved state | Saved state | Static evidence summary |
| --- | --- | --- | --- |
| `0x00487bc0` | `CDXEngine__CollectOverlayMarkersAndSetupRenderState` | `void __thiscall CHud__RenderOverlay(void * this)` | Called from `CDXEngine__PostRender` with HUD singleton `&DAT_008aa4e8`, matching the Stuart-source `HUD.RenderOverlay();` callsite in `DXEngine.cpp`. The body loops active viewpoints, dispatches the per-viewpoint overlay renderer, and restores overlay render state. |
| `0x004879e0` | `CExplosionInitThing__AccumulateOverlayMarkerFromViewpoint` | `void __thiscall CHud__RenderOverlayForViewpoint(void * this, void * viewpoint, int viewpoint_index, float param_3)` | Called by `CHud__RenderOverlay`; validates target/camera context, selects the viewpoint, clips overlay marker coordinates, stores overlay state fields, applies HUD overlay sprite state, and dispatches world-target, target-indicator, controller-slot, 3D marker, objective, slot-fill, and radar helper paths. |
| `0x00482590` | `CExplosionInitThing__RenderTargetIndicatorOverlay` | `void __thiscall CHud__RenderTargetIndicatorOverlay(void * this)` | Called by `CHud__RenderOverlayForViewpoint`; chooses active/last target reader context, handles split-screen Y placement, draws from CHud texture refs, covers the Thunderhead miniature path and generic viewport/projection sphere path, and draws target health bars. |

## Correction Boundary

The caller chain and source callsite supersede the older `CDXEngine` / `CExplosionInitThing` owner labels for this three-function overlay root. Stuart's source snapshot does not include the matching HUD implementation body, so the exact source bodies, concrete CHud layout, local-variable names, and neighboring overlay helper ownership remain queued for later review.

## Validation

- Headless dry run: `updated=0 skipped=3 created=0 would_create=0 renamed=0 would_rename=3 missing=0 bad=0`; `REPORT: Save succeeded`.
- Headless apply: `updated=3 skipped=0 created=0 would_create=0 renamed=3 would_rename=0 missing=0 bad=0`; `REPORT: Save succeeded`.
- Read-back verified `3` metadata rows, `3` tag rows, `3` xref rows, `3` target decompile exports, and `1` outer-caller decompile export.
- Focused unit tests passed `2/2`, Python compile passed, and the direct/package-script probes passed.
- Refreshed queue telemetry reports `6028` functions, `1565` commented functions, `4463` commentless functions, `1909` undefined signatures, and `1852` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1565/6028 = 25.96%`; strict clean-signature `1502/6028 = 24.92%`.
- The live Ghidra project backup was verified on `[maintainer-local-backup-volume]` at `[maintainer-local-ghidra-backup-root]\BEA_20260514_090320_post_wave410_hud_overlay_verified` with `19` files, `154798983` bytes, and `HashDiffCount=0`.

## Claim Boundary

This note does not prove runtime HUD behavior, does not prove concrete CHud layout, does not certify neighboring overlay helpers, does not prove local-variable or structure recovery, does not prove rebuild parity, and does not involve launching or patching `BEA.exe`.
