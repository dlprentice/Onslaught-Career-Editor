# Ghidra DXCompass HUD Head Wave591 Readiness Note

Date: 2026-05-19
Status: static saved-Ghidra evidence only

Wave591 hardened six HUD/render rows at the static re-audit queue head: one `CDXEngine` optional render-effect helper and five `CDXCompass` field-block helpers reached through `CHud`.

Saved rows:

| Address | Function |
| --- | --- |
| `0x0053bb50` | `CDXEngine__RenderOptionalFullscreenEffectPass` |
| `0x0053bd60` | `CDXCompass__InitFields` |
| `0x0053bda0` | `CDXCompass__ReleaseDynamicResources` |
| `0x0053c2e0` | `CDXCompass__BuildByteSpriteOverlayTexture` |
| `0x0053c510` | `CDXCompass__UpdateDynamicOverlayTexture` |
| `0x0053cd30` | `CDXCompass__RenderWorldSpaceOverlay` |

What is proven:

- Ghidra now records clean signatures, comments, and `dxcompass-hud-head-wave591` tags for all six rows.
- `CDXEngine__RenderOptionalFullscreenEffectPass` is an ECX-only render tail called from `CDXEngine__Render`; the body gates optional fullscreen/effect rendering, enables render state `0x8f`, writes `DAT_0063012c` during the pass, and resets it to `0xff`.
- `CHud__Init` allocates the compass field block, calls `CDXCompass__InitFields`, stores the result at `CHud+0x60`, and then calls `CDXCompass__InitMarkerArrays`.
- `CHud__ShutDown` calls `CDXCompass__DestroyTextures`, then `CDXCompass__ReleaseDynamicResources`, then frees the `CHud+0x60` field block.
- `CHud__RenderTargetMarkers3D` calls `CDXCompass__RenderWorldSpaceOverlay` with the `CHud+0x60` compass field block in `ECX` and `CHud+0x50` as the sole stack argument.
- `CDXCompass__RenderWorldSpaceOverlay` calls `CDXCompass__BuildByteSpriteOverlayTexture` and `CDXCompass__UpdateDynamicOverlayTexture` with the same `ECX` field block and one `battleEngineContext` stack argument.
- `RET 0x4` read-back on `CDXCompass__BuildByteSpriteOverlayTexture`, `CDXCompass__UpdateDynamicOverlayTexture`, and `CDXCompass__RenderWorldSpaceOverlay` disproves the older extra-parameter signatures.
- Post-save read-back verified 6 metadata rows, 6 tag rows, 6 xref rows, 2046 instruction rows, 6 target decompile rows, 4 caller decompile rows, 246 callsite instruction rows, 726 proof instruction rows, and 1101 `0x0053c510` return-check instruction rows.
- The queue refresh reports `6093` total functions, `3027` commented, `3066` commentless, `1347` exact-undefined signatures, and `1106` `param_N` signatures.
- Comment-backed proxy is `3027/6093 = 49.68%`; strict clean-signature proxy is `2981/6093 = 48.92%`.
- The next high-signal queue head is `0x0053d3a0 CLTShell__ReleaseHudRefAndTargetHandle`.
- The live Ghidra project backup verified at `G:\GhidraBackups\BEA_20260519-130808_post_wave591_dxcompass_hud_head_verified` with 19 files, 160959367 bytes, `DiffCount=0`, and manifest hash `5713ad6ccec91519996a5c085677773276fc00bed3385be1e4f67fdf89bacb14`.

What is not proven:

- Runtime HUD/effect behavior remains unproven.
- Exact source identity remains unproven because no matching tracked Stuart source implementation body was found for this wave.
- Exact `CDXCompass`, `CDXEngine`, `CHud`, `CBattleEngine`, texture, byte-sprite, and render-state layouts remain unproven beyond the observed fields documented in the read-back notes.
- BEA patching, gameplay behavior, and rebuild parity remain unproven.
