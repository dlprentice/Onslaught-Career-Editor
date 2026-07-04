# Ghidra CEngine View Resource Light Review Wave932 Readiness Note

Status: complete read-only static review
Date: 2026-05-28
Scope: `cengine-view-resource-light-review-wave932`

Wave932 re-reviewed eight Wave911 focused CEngine view/resource/light bridge candidates, plus nine context helpers that bracket viewpoint setup, render handoff, heightfield resource loading, Kempy cube, water reload, landscape reset, and render-queue lighting context. Wave932 no mutation status: the review made no Ghidra mutation, no rename, no signature change, no function-boundary change, and no executable-byte change.

Primary targets:

| Address | Saved state | Fresh evidence |
| --- | --- | --- |
| `0x00449ef0 CEngine__GetViewMatrixFromCamera` | `void __thiscall CEngine__GetViewMatrixFromCamera(void * this, void * camera, void * outViewMatrix)` | Xrefs from `CDXEngine__Render`, `CFrontEnd__RenderStart`, and `CFrontEnd__UpdateCamera`; decompile uses `RET 0x8`, the 1.570796-style pitch basis, camera orientation vfunc, transpose/multiply work, and copies twelve dwords to `outViewMatrix`. |
| `0x0044a0d0 CEngine__SelectViewpoint` | `void __thiscall CEngine__SelectViewpoint(void * this, int viewpoint)` | Xrefs from `CDXEngine__Render` and `CHud__RenderOverlayForViewpoint`; writes current viewpoint at `+0x4ac`, copies the selected viewport block, and calls `D3DDevice__SetViewport`. |
| `0x0044a110 CEngine__ResetPos` | `void __thiscall CEngine__ResetPos(void * this, int x, int y)` | Xref from `CCutscene__Stop`; forwards engine landscape pointer `this+0x10` and x/y stack values to `CDXLandscape__ResetWrapper`. |
| `0x0044a130 CEngine__InitDamageSystem` | `void __fastcall CEngine__InitDamageSystem(void * engine)` | Xref from `CGame__RestartLoopRunLevel`; resets landscape damage tables, iterates tree entries, applies tree-shadow damage stamps, and completes the LockCurrentDamage-style tracking step. |
| `0x0044a1f0 CEngine__LoadMixers` | `void __thiscall CEngine__LoadMixers(void * this, int set)` | Xref from `CHeightField__DeserializeMapAndInitResources`; loads the map-texture array at `+0x49c`, calls `CMapTex__LoadMixerTextureSet(set, 6, 0x100)`, and copies mixer levels through offsets `0x4c` through `0x1c8`. |
| `0x0044a2a0 CEngine__SetKempyCube` | `void __thiscall CEngine__SetKempyCube(void * this, int number)` | Xref from `CHeightField__DeserializeMapAndInitResources`; loads engine field `+0x498` and forwards the cube number to `CDXEngine__InitKempyCubeResources`. |
| `0x0044a2c0 CEngine__SetWater` | `void __thiscall CEngine__SetWater(void * this, int number)` | Xref from `CHeightField__DeserializeMapAndInitResources`; loads water/render field `+0x14` and calls `CWaterRenderSystem__ReloadTextures`; the current decompile does not consume the stack `number` directly. |
| `0x0044a2d0 CEngine__SetupLights` | `void CEngine__SetupLights(void)` | Xref from `CDXEngine__Render`; normalizes the MAP sun vector, calls atmospherics light-direction context, and calls `CRenderQueue__UpdateViewVectorAndMatrix(&DAT_009c7550, ...)`. |

Context helpers:

| Address | Role |
| --- | --- |
| `0x0044a020 CEngine__SetViewpoint` | CGame render path installs per-view camera/viewport/player wrappers before CDXEngine render. |
| `0x0044a1c0 CEngine__UpdatePos` | Main-loop landscape tile bridge for render-landscape flag `+0x4a8` and current viewpoint `+0x4ac`. |
| `0x00491060 CHeightField__DeserializeMapAndInitResources` | MAP deserialize context that calls `CEngine__LoadMixers`, `CEngine__SetKempyCube`, and `CEngine__SetWater`. |
| `0x0044a6e0 CEngine__Deserialize` | Upstream ENGN/map-texture deserialize context from Wave931. |
| `0x0053e2e0 CDXEngine__Render` | Render context for `CEngine__SelectViewpoint`, `CEngine__GetViewMatrixFromCamera`, `CEngine__SetupLights`, Kempy cube render, and water render passes. |
| `0x005441a0 CDXEngine__InitKempyCubeResources` | Wrapper reached from `CEngine__SetKempyCube`. |
| `0x00544fb0 CDXLandscape__ResetWrapper` | Landscape reset wrapper reached from `CEngine__ResetPos`. |
| `0x0055b330 CWaterRenderSystem__ReloadTextures` | Water texture reload helper reached from `CEngine__SetWater`. |
| `0x005524a0 CRenderQueue__UpdateViewVectorAndMatrix` | Render-queue view-vector/matrix helper reached from `CEngine__SetupLights`. |

Evidence:

- Primary exports: 8 metadata rows, 8 tag rows, 11 xref rows, 403 instruction rows, and 8 decompile rows.
- Context exports: 9 metadata rows, 9 tag rows, 19 xref rows, 963 instruction rows, and 9 decompile rows.
- Composer 2.5 adversarial consult agreed this is a coherent one-wave read-only cluster and that mutation should be unlikely unless live Ghidra diverged from the prior Wave360-Wave362/Wave600/Wave872 evidence. The live exports did not diverge.
- Wave911 focused re-audit progress after Wave932: `130/1408 = 9.23%`.
- Static export-contract closure remains `6113/6113 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-001551_post_wave932_cengine_view_resource_light_review_verified`, 19 files, 173247367 bytes, `DiffCount=0`.

What this proves:

- The saved names, signatures, tags, xrefs, instruction bodies, and decompiles for the eight primary CEngine view/resource/light rows remain internally consistent with prior bounded claims.
- The resource selection and render-light helpers are source-compatible with the adjacent `engine.cpp` API block while the loaded Steam Ghidra database remains authoritative.
- `CEngine__SetupLights` remains a CEngine-labeled global/static setup helper that hands view-vector/matrix context to the documented global render queue; Wave932 does not turn this into a runtime lighting proof.

What remains unproven:

- Runtime camera, viewport, mixer, water, Kempy cube, landscape reset, damage-stamp, lighting, or render behavior.
- Exact `CEngine`, `CDXEngine`, `CDXLandscape`, `CWaterRenderSystem`, `CMapTex`, or `CRenderQueue` layouts beyond observed address-qualified offsets.
- Exact source-body identity or clean-room rebuild equivalence.
- BEA patch behavior, gameplay outcomes, and rebuild parity.
