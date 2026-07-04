# DXCompass.cpp - DirectX Compass HUD

**Source File:** `[maintainer-local-source-export-root]\DXCompass.cpp`
**Debug String Address:** `0x00650454`
**Functions Found:** 14
**Analysis Date:** December 2025; tracked-position getter signatures refreshed 2026-05-09; DXCompass render/resource signatures/comments refreshed 2026-05-12; HUD-head field-block signatures/comments refreshed 2026-05-19; Wave1060 comment/tag normalization/read-back 2026-06-01

> **Queue status (2026-06-01):** Ghidra export-contract closure **6246/6246** (Wave1060: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

CDXCompass is the DirectX-based compass HUD element that displays:
- Threat direction indicators (enemy positions)
- Damage flash indicators (incoming damage direction)
- Bar line markers
- Objective markers (mission waypoints)

The compass is a circular ring rendered at the top of the screen, with markers positioned using trigonometric calculations (sin/cos) around the circumference.

## 2026-06-01 Wave1060 DXCompass Lifecycle / Render-Support Review

Wave1060 (`dxcompass-lifecycle-review-wave1060`) re-read the DXCompass lifecycle/render-support surface and saved function tags plus one stale caller-comment correction for nine already named/commented rows. It made no renames, no signature changes, no function-boundary changes, and no executable-byte changes.

Fresh primary pre exports verified `7` metadata rows, `7` tag rows, `12` xref rows, `731` function-body instruction rows, and `7` decompile rows; context pre exports verified `13` metadata rows, `13` tag rows, `14` xref rows, `2339` instruction rows, and `13` decompile rows; post tagged exports verified `9` metadata rows, `9` tag rows, `15` xref rows, `1081` instruction rows, and `9` decompile rows. Dry/apply/final-dry reported `updated=0 skipped=0 tags_added=110 missing=0 bad=0`, then `updated=9 skipped=0 tags_added=110 missing=0 bad=0`, then `updated=0 skipped=9 tags_added=0 missing=0 bad=0`; comment-correction dry/apply/final-dry reported `updated=0 skipped=8 tags_added=0 comment_updated=1 missing=0 bad=0`, then `updated=1 skipped=8 tags_added=0 comment_updated=1 missing=0 bad=0`, then `updated=0 skipped=9 tags_added=0 comment_updated=0 missing=0 bad=0`. Queue closure remains `6246/6246 = 100.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface progress advances to `1148/1509 = 76.08%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-205027_post_wave1060_dxcompass_lifecycle_review_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`.

| Address | Wave1060 read-back role |
| --- | --- |
| `0x00406040 CDXCompass__GetTrackedPositionX` | FPU-return getter for tracked context `+0x1c`; called by `CDXCompass__Render` and dynamic overlay update. |
| `0x0040c630 CDXCompass__GetTrackedPositionY` | FPU-return getter for tracked context `+0x20`; called by `CDXCompass__Render` and dynamic overlay update. |
| `0x004270e0 CDXCompass__InitMarkerArrays` | `CHud__Init`-reached marker-array zeroer for the two 30-slot arrays at `this+0x3c24`, then calls `CDXCompass__Init`. |
| `0x00427110 CDXCompass__LoadTextures` | `CHud__LoadTextures`-reached load of `ThreatFlash`, `DamageFlash`, `BarLine`, and `CompassObjectiveMarker` refs. |
| `0x00427190 CDXCompass__DestroyTextures` | `CHud__ShutDown`-reached release/zero of the same four texture refs through the texture ref-count helper. |
| `0x00427200 CDXCompass__Reset` | Clears compass render/state flag `this+0x3c10` in the reset/init-fields path. |
| `0x00427210 CDXCompass__Render` | Main compass sprite render path called by `CDXCompass__RenderWorldSpaceOverlay`; draws threat/damage/bar/objective sprites and flushes `CFastVB`. |
| `0x0053be40 CDXCompass__Init` | Initializes byte-sprite, ring texture pairs, CVBuffers, ring geometry, and byte-sprite target setup. |
| `0x0053c1d0 CDXCompass__BuildRingGeometry` | Plain helper that fills locked ring vertices from texture dimensions, segment count, thickness percent, and UV scale. |

Runtime compass/HUD rendering behavior, exact `CHud`/`CDXCompass`/battle-engine context layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1060; dxcompass-lifecycle-review-wave1060; 0x00406040 CDXCompass__GetTrackedPositionX; 0x0040c630 CDXCompass__GetTrackedPositionY; 0x004270e0 CDXCompass__InitMarkerArrays; 0x00427110 CDXCompass__LoadTextures; 0x00427190 CDXCompass__DestroyTextures; 0x00427200 CDXCompass__Reset; 0x00427210 CDXCompass__Render; 0x0053be40 CDXCompass__Init; 0x0053c1d0 CDXCompass__BuildRingGeometry; 812/1408 = 57.67%; 1148/1509 = 76.08%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-205027_post_wave1060_dxcompass_lifecycle_review_verified; tag normalization.

## 2026-05-31 Wave1013 HUD Lifecycle / Compass Context

Wave1013 (`hud-lifecycle-render-support-review-wave1013`) re-read `0x004821e0 CDXCompass__ApplyRenderStateAdditive` in HUD lifecycle/render-support context with no mutation. The helper remains called by `0x00427210 CDXCompass__Render`; adjacent context re-read `0x0053bd60 CDXCompass__InitFields` and `0x00427210 CDXCompass__Render` while HUD lifecycle anchors included `0x00481450 CHud__Init`, `0x004815c0 CHud__Reset`, `0x00481650 CHud__LoadTextures`, `0x00481af0 CHud__PostLoadProcess`, and `0x00481f40 CHud__SetHudComponent`. Queue closure remains `6238/6238 = 100.00%`; Wave911 focused re-audit progress remains `505/1408 = 35.87%`; expanded static surface progress is `718/1493 = 48.09%`; Wave911 top-500 risk-ranked coverage is `420/500 = 84.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-182125_post_wave1013_hud_lifecycle_render_support_review_verified`. Runtime compass/HUD behavior, exact source-body identity, concrete layouts, BEA patching, and rebuild parity remain separate proof. Probe token anchor: Wave1013; hud-lifecycle-render-support-review-wave1013; 0x00481450 CHud__Init; 0x004815c0 CHud__Reset; 0x00481650 CHud__LoadTextures; 0x00481af0 CHud__PostLoadProcess; 0x00481f40 CHud__SetHudComponent; 0x004821e0 CDXCompass__ApplyRenderStateAdditive; 0x00488330 CIBuffer__CreateConfigured; 0x004885e0 CIBuffer__LockDirect; 0x0048f540 CLevelBriefingLog__ctor; 0x0048f5a0 CLevelBriefingLog__scalar_deleting_dtor; 0x0048f5c0 CLevelBriefingLog__dtor; 505/1408 = 35.87%; 718/1493 = 48.09%; 420/500 = 84.00%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260531-182125_post_wave1013_hud_lifecycle_render_support_review_verified; no mutation.

## 2026-05-12 Correction Scope

Wave 323 saved signatures/comments for eight DXCompass-adjacent targets after fresh Ghidra metadata, decompile, xref, instruction, and callsite review. `CDXCompass__Render` is now modeled as a `__thiscall` body with the compass object in `ECX` and a battle-engine/render-context stack argument. `CDXCompass__BuildRingGeometry` is modeled as a plain `__cdecl` helper taking locked vertices and ring parameters, not as a class method. `0x00426fd0` remains a broad allocator wrapper and is not DXCompass-specific ownership proof.

This is saved Ghidra refinement only. The available Stuart source snapshot does not contain the `DXCompass.cpp` body, so runtime HUD behavior, exact source-body identity, concrete layouts, tags, locals, structure types, and rebuild parity remain unproven.

## 2026-05-19 Wave591 HUD-Head Correction Scope

Wave591 saved five additional `CDXCompass` field-block rows after fresh xref, caller, instruction, return-shape, and decompile review. `CHud__Init` stores this field block at `CHud+0x60`; `CHud__RenderTargetMarkers3D` later passes that same block in `ECX` to `CDXCompass__RenderWorldSpaceOverlay` with `CHud+0x50` as the single stack argument. `CDXCompass__BuildByteSpriteOverlayTexture`, `CDXCompass__UpdateDynamicOverlayTexture`, and `CDXCompass__RenderWorldSpaceOverlay` all prove `RET 0x4`, so the older extra-parameter signatures were removed.

This is static saved-Ghidra evidence only. Runtime HUD behavior, exact `CHud`/`CDXCompass`/`CBattleEngine` layouts, exact source-body identity, BEA patching, and rebuild parity remain unproven.

Queue after Wave591: `6093` total, `3027` commented, `3066` commentless, `1347` exact-undefined signatures, `1106` `param_N`, and next head `0x0053d3a0 CLTShell__ReleaseHudRefAndTargetHandle`.

## Functions

| Address | Name | Size | Description |
|---------|------|------|-------------|
| `0x0053bd60` | `CDXCompass__InitFields` | ~0x40 | Initializes and clears the compass field block later stored at `CHud+0x60` |
| `0x0053bda0` | `CDXCompass__ReleaseDynamicResources` | ~0xa0 | Releases ring texture pairs, byte sprite, and dynamic compass resources |
| `0x0053be40` | `CDXCompass__Init` | ~0x390 | Main initialization - allocates textures, vertex buffers, builds ring geometry |
| `0x0053c1d0` | `CDXCompass__BuildRingGeometry` | ~0x130 | Generates circular ring vertices using sin/cos |
| `0x0053c2e0` | `CDXCompass__BuildByteSpriteOverlayTexture` | ~0x230 | Builds the byte-sprite staging overlay texture from compass field-block resources |
| `0x0053c510` | `CDXCompass__UpdateDynamicOverlayTexture` | ~0x810 | Updates dynamic compass overlay texture bands from battle-engine context data |
| `0x0053cd30` | `CDXCompass__RenderWorldSpaceOverlay` | ~0xae0 | World-space compass overlay render bridge called from `CHud__RenderTargetMarkers3D` |
| `0x004270e0` | `CDXCompass__InitMarkerArrays` | ~0x30 | Zeroes marker tracking arrays (30 markers x 2 players) |
| `0x00427110` | `CDXCompass__LoadTextures` | ~0x80 | Loads HUD textures via CTexture::FindTexture |
| `0x00427190` | `CDXCompass__DestroyTextures` | ~0x70 | Releases texture references |
| `0x00427200` | `CDXCompass__Reset` | ~0x10 | Resets compass state flag at offset 0x3c10 |
| `0x00427210` | `CDXCompass__Render` | ~0xB70 | Main render function saved as `void __thiscall CDXCompass__Render(void * this, void * battleEngineContext)` |
| `0x00406040` | `CDXCompass__GetTrackedPositionX` | ~0x10 | Reads a tracked pointer from `context +0x4b0` and returns the `+0x1c` value through the FPU |
| `0x0040c630` | `CDXCompass__GetTrackedPositionY` | ~0x10 | Reads a tracked pointer from `context +0x4b0` and returns the `+0x20` value through the FPU |

## Saved Signatures

| Address | Current saved signature | Boundary |
|--------|--------------------------|----------|
| `0x00426fd0` | `void * __cdecl OID__AllocObject_DefaultTag_00662b2c(int sizeBytes)` | Broad allocation wrapper forwarding `sizeBytes`, default type/tag `0`, debug tag `DAT_00662b2c`, and allocator context `0x009c3df0` to `OID__AllocObject`; xrefs are broader than DXCompass. |
| `0x004270e0` | `void __fastcall CDXCompass__InitMarkerArrays(void * this)` | Zeroes two 30-slot compass marker arrays starting at `this+0x3c24` with `0x18` stride, then calls `CDXCompass__Init`. |
| `0x00427110` | `void __fastcall CDXCompass__LoadTextures(void * this)` | Loads ThreatFlash, DamageFlash, BarLine, and CompassObjectiveMarker texture refs into `this+0x3ef4` through `this+0x3f00`. |
| `0x00427190` | `void __fastcall CDXCompass__DestroyTextures(void * this)` | Releases the four compass texture refs by calling the ref-count helper on `texture+8`, then zeroes each slot. |
| `0x00427200` | `void __fastcall CDXCompass__Reset(void * this)` | Clears the compass render/state flag at `this+0x3c10`; the observed HUD reset helper then clears ring texture, vertex-buffer, and byte-sprite slots. |
| `0x00427210` | `void __thiscall CDXCompass__Render(void * this, void * battleEngineContext)` | Main render path called from `CDXCompass__RenderWorldSpaceOverlay` with compass object in `ECX` and a context stack argument. |
| `0x0053bd60` | `void * __fastcall CDXCompass__InitFields(void * this)` | `CHud__Init` calls this ECX-only return-this initializer, stores the result at `CHud+0x60`, then calls `CDXCompass__InitMarkerArrays`; the body clears ring texture and dynamic resource slots. |
| `0x0053bda0` | `void __fastcall CDXCompass__ReleaseDynamicResources(void * this)` | `CHud__ShutDown` calls this after `CDXCompass__DestroyTextures`; releases ring texture pairs, dynamic resource objects, and the byte sprite before the field block is freed. |
| `0x0053be40` | `void __fastcall CDXCompass__Init(void * this)` | Allocates/loads the byte sprite, clamps ring texture dimensions against GPU caps, allocates ring texture pairs and CVBuffers, builds ring geometry, and assigns the byte-sprite target. |
| `0x0053c1d0` | `void __cdecl CDXCompass__BuildRingGeometry(void * vertices, int textureWidth, int textureHeight, int segmentCount, int thicknessPercent, float uvScale)` | Fills a compass ring vertex strip from locked vertices and ring parameters using sin/cos, then copies the first pair of vertices to close the ring. |
| `0x0053c2e0` | `void __thiscall CDXCompass__BuildByteSpriteOverlayTexture(void * this, void * battleEngineContext)` | Called by `CDXCompass__RenderWorldSpaceOverlay`; `RET 0x4` proves one stack argument after the `ECX` compass field block. |
| `0x0053c510` | `void __thiscall CDXCompass__UpdateDynamicOverlayTexture(void * this, void * battleEngineContext)` | Called by `CDXCompass__RenderWorldSpaceOverlay`; `RET 0x4` proves one stack argument after the `ECX` compass field block. |
| `0x0053cd30` | `void __thiscall CDXCompass__RenderWorldSpaceOverlay(void * this, void * battleEngineContext)` | Called by `CHud__RenderTargetMarkers3D` with `CHud+0x60` in `ECX` and `CHud+0x50` as the stack argument; calls the two texture builders and `CDXCompass__Render`. |

## Class Layout (Partial)

The CDXCompass data is embedded in a field block owned by `CHud`. Wave591 proves `CHud__Init` stores that block at `CHud+0x60`; offsets below are from the compass field-block `this` pointer:

| Offset | Type | Name | Description |
|--------|------|------|-------------|
| `0x3c08` | CByteSprite* | mCompassSprite | Sprite for compass ring |
| `0x3c10` | int | mState | Compass state flag |
| `0x3c24` | MarkerData[30][2] | mMarkers | Marker tracking (30 slots x 2 players) |
| `0x3ef4` | CTexture* | mThreatFlashTex | "hud\\v2\\ThreatFlash.tga" |
| `0x3ef8` | CTexture* | mDamageFlashTex | "hud\\v2\\DamageFlash.tga" |
| `0x3efc` | CTexture* | mBarLineTex | "hud\\v2\\BarLine.tga" |
| `0x3f00` | CTexture* | mObjectiveMarkerTex | "hud\\v2\\CompassObjectiveMarker.tga" |
| `0x3f04` | CTexture*[2] | mRingTextures | Ring textures (2 per player) |
| `0x3f0c` | CVBuffer* | mOuterRingVB | Vertex buffer for outer ring |
| `0x3f10` | CVBuffer* | mInnerRingVB | Vertex buffer for inner ring |

## Function Details

### CDXCompass__Init (0x0053be40)

Main initialization function called from `CHud::Init`.

**Key Operations:**
1. Allocates CByteSprite for compass rendering (0x20 bytes, type 0x4d)
2. Loads compass sprite data (16x16, 20 frames, 4 columns)
3. Adjusts texture dimensions based on GPU capabilities (DAT_00888a90 flags)
4. Creates 2 CTexture objects per player (4 total) for ring rendering
5. Allocates CVBuffer objects for outer ring (0x66 vertices) and inner ring (0x52 vertices)
6. Calls `CDXCompass__BuildRingGeometry` to populate vertex buffers
7. Sets target rendering parameters (512x512, 30 fps)

**Global Data References:**
- `DAT_00888a90` - GPU capability flags (bit 5 = texture size limit)
- `DAT_0089c924` - Additional GPU flag
- `DAT_00888aac` - Max texture width
- `DAT_00888ab0` - Max texture height
- `DAT_00650424/28/2c/30` - Texture dimensions for compass rings

### CDXCompass__BuildRingGeometry (0x0053c1d0)

Generates vertex data for the circular compass ring.

**Parameters:**
- `vertices` (void*) - Locked output vertex buffer
- `textureWidth` (int) - Texture width
- `textureHeight` (int) - Texture height
- `segmentCount` (int) - Number of segments
- `thicknessPercent` (int) - Ring thickness percentage
- `uvScale` (float) - UV scale factor

**Algorithm:**
- Uses `2*PI` (6.2831855) for full circle
- Inner radius = `(1 - scale) * thickness * 0.01`
- Outer radius = `(1 + scale) * thickness * 0.01`
- Generates triangle strip with 10 floats per vertex pair (position, UV, etc.)

### CDXCompass__Render (0x00427210)

Main rendering function - the largest and most complex function.

Saved signature: `void __thiscall CDXCompass__Render(void * this, void * battleEngineContext)`.

The caller context is `CDXCompass__RenderWorldSpaceOverlay`; instruction read-back shows the compass object in `ECX` and the battle-engine/render context supplied as a stack argument. Exact context layout and stack-local provenance remain open.

**Rendering Passes:**
1. **Threat indicators** - Red markers showing enemy directions (uses mThreatFlashTex)
2. **Damage indicators** - Flash markers showing incoming damage (uses mDamageFlashTex)
3. **Bar line markers** - 4 directional markers for N/S/E/W (uses mBarLineTex)
4. **Objective markers** - Yellow markers for mission objectives (uses mObjectiveMarkerTex)

**Key Constants:**
- `6.2831855` - 2*PI for angle calculations
- `111.5` / `95.0` - Outer ring radius (normal/split-screen)
- `96.0` / `80.0` - Middle ring radius
- `110.0` / `100.0` - Inner ring radius
- `0x1e` (30) - Maximum markers per player

**Split-Screen Support:**
- Checks multiplayer/current-level state via `CGame__IsMultiplayer()`
- Adjusts vertical center (0.5x or 1.5x) based on which player
- Uses different marker array slot based on player

## Texture Assets

| File | Usage |
|------|-------|
| `hud\v2\ThreatFlash.tga` | Enemy threat direction indicator |
| `hud\v2\DamageFlash.tga` | Incoming damage direction flash |
| `hud\v2\BarLine.tga` | Compass cardinal direction markers |
| `hud\v2\CompassObjectiveMarker.tga` | Mission objective waypoint marker |

## Call Hierarchy

```
CHud__Init (0x00481450)
  -> CDXCompass__InitFields (0x0053bd60)
       -> CDXCompass__Reset (0x00427200)
  -> CDXCompass__InitMarkerArrays (0x004270e0)
       -> CDXCompass__Init (0x0053be40)
            -> CByteSprite::Init
            -> CByteSprite::Load
            -> CTexture::ctor (x4)
            -> CVBuffer::Create (x2)
            -> CDXCompass__BuildRingGeometry (x2)

CHud__LoadTextures
  -> CDXCompass__LoadTextures (0x00427110)
       -> CTexture::FindTexture (x4)

CHud__ShutDown
  -> CDXCompass__DestroyTextures (0x00427190)
  -> CDXCompass__ReleaseDynamicResources (0x0053bda0)

CHud__RenderTargetMarkers3D (0x00484340)
  -> CDXCompass__RenderWorldSpaceOverlay (0x0053cd30)
       -> CDXCompass__BuildByteSpriteOverlayTexture (0x0053c2e0)
       -> CDXCompass__UpdateDynamicOverlayTexture (0x0053c510)
       -> CDXCompass__Render (0x00427210)
       -> CFastVB::Render (multiple times)
       -> CVBufTexture__DrawSpriteEx (sprite rendering context)
```

## Technical Notes

1. **Memory Allocation**: Uses `OID__AllocObject` with type IDs:
   - `0x4d` - CByteSprite
   - `0x02` - CTexture
   - `0x2c` - CVBuffer

2. **Angle Normalization**: All angles are normalized to [0, 2*PI] range using loops

3. **Alpha Blending**: Marker alpha calculated from distance/time, encoded as ARGB color

4. **Aspect Ratio**: Uses `DAT_00888a40` for Y-axis scaling to maintain circular appearance

5. **Exception Handling**: Uses structured exception handling (SEH) with unwind handlers at 0x005d77xx

6. **Tracked-position getters**: `CDXCompass__GetTrackedPositionX` and `CDXCompass__GetTrackedPositionY` were signature-hardened on 2026-05-09 from fresh Ghidra read-back. Their current evidence covers the `context +0x4b0` tracked pointer plus `+0x1c` / `+0x20` field reads and xrefs from compass render / dynamic overlay update paths. Exact context layout, return precision, tags, local names, structure types, runtime compass behavior, and rebuild parity remain unproven.

7. **Wave591 field-block proof**: The current saved head proves `CHud+0x60` as the compass field-block pointer for init, teardown, and world-space overlay rendering. The three overlay helpers use `RET 0x4`, so the saved signatures carry only one explicit stack argument, `battleEngineContext`.
