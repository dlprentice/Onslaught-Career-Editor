# Ghidra Render-State Matrix Support Review Wave1095 Readiness Note

Status: complete static read-back evidence
Date: 2026-06-04
Scope: `render-state-matrix-support-review-wave1095`

Wave1095 reviewed twenty-one render-state, D3D state-cache, matrix, and CDXEngine support helpers. The pass saved tag-only normalization for one already named/commented/signature-clean row, `0x00513af0 D3DStateCache__SetSlotMode4or5`. It made no renames, no signature changes, no comment changes, no function-boundary changes, no executable-byte changes, no BEA launch, and no installed-game/runtime-file mutation.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00513af0 D3DStateCache__SetSlotMode4or5` | Existing signature `void __stdcall D3DStateCache__SetSlotMode4or5(int state_slot)` and comment were preserved; Wave1095 added tags only. The decompile updates per-slot state array `DAT_008557f4` to mode `4` or `5` based on `DAT_008554fc`, then notifies `DAT_00888a50` through vfunc `+0x10c` when the slot changes. |
| `0x00513820 D3DStateCache__SetStateCached` | Prior Wave849 state-cache helper retained as context; broad incoming xrefs connect it to render/frontend/device state callers. |
| `0x00513870 D3DStateCache__SetStateRaw` | Prior Wave849 raw state helper retained as context. |
| `0x00513b60 D3DStateCache__ForceSlotMode4or5` | Adjacent Wave850 forced mode helper retained as context. |
| `0x00550b10 CDXEngine__SetProjectionMatrix` | Prior Wave868 projection/depth matrix writer retained as context. |
| `0x00550ca0 CDXEngine__SetWorldMatrixElements` | Prior Wave868 world-transform writer retained as context. |
| `0x00550d50 CDXEngine__ApplyPendingRenderState` | Prior Wave829 pending render-state flush retained as context. |
| `0x00551200 CDXEngine__ApplyCachedLight` | Prior Wave869 cached-light application retained as context. |

Read-back evidence:

- `ApplyRenderStateMatrixSupportReviewWave1095.java dry`: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=13 missing=0 bad=0`.
- `ApplyRenderStateMatrixSupportReviewWave1095.java apply`: `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=13 missing=0 bad=0`, with `REPORT: Save succeeded`.
- `ApplyRenderStateMatrixSupportReviewWave1095.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Fresh pre/post exports verified `21` metadata rows, `21` tag rows, `1025` xref rows, `1388` instruction rows, and `21` decompile rows.
- The corrected target has `27` incoming xref rows, including `CConsole__RenderLoadingScreen`, `CFrontEnd__Render`, `CHud__RenderOverlay`, `CHud__RenderTacticalRadarContacts`, `CDXImposter__RenderAll`, `CDXLandscape__Render`, `CDXLandscape__RenderTerrain`, `CDXLandscape__RenderShadowMap`, `CMeshRenderer__RenderMeshCore`, `CRenderQueue__BeginFrame`, `CVBufTexture__DrawSpriteEx`, and `CDXTrees__Render`.
- Static function-quality closure remains `6410/6410 = 100.00%`, expanded static surface remains `1560/1560 = 100.00%`, Wave911 focused progress remains `812/1408 = 57.67%`, and Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260604-171413_post_wave1095_render_state_matrix_support_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.

What this proves:

- The saved Ghidra function row exists at `0x00513af0` with the expected name, signature, and comment.
- The saved tags now include `render-state-matrix-support-review-wave1095`, `wave1095-readback-verified`, `d3d-state-cache`, `render-state`, `state-cache`, `mode-toggle`, `mode-4-or-5`, and `vtable-0x10c`.
- The observed body and caller set are static retail Ghidra metadata/tag/xref/instruction/decompile evidence only.

What remains unproven:

- Runtime render-state behavior.
- Exact D3D enum or state-slot schema names beyond observed constants/callers.
- Exact CDXEngine/D3DStateCache/global layout identity.
- Exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Probe token anchor: Wave1095; render-state-matrix-support-review-wave1095; 0x00513af0 D3DStateCache__SetSlotMode4or5; 0x00513820 D3DStateCache__SetStateCached; 0x00513b60 D3DStateCache__ForceSlotMode4or5; 0x00550b10 CDXEngine__SetProjectionMatrix; 0x00550ca0 CDXEngine__SetWorldMatrixElements; 0x00550d50 CDXEngine__ApplyPendingRenderState; 0x00551200 CDXEngine__ApplyCachedLight; 1560/1560 = 100.00%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; G:\GhidraBackups\BEA_20260604-171413_post_wave1095_render_state_matrix_support_review_verified; tag-only normalization.
