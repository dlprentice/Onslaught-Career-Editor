# Ghidra Wave900+ Through Wave1095 Recheck Note

Status: aggregate validation passed
Date: 2026-06-04
Scope: `wave900-plus-through-wave1095-recheck`

This note extends the post-Wave900 recheck chain through Wave1095. The intended local validation gate is:

```powershell
npm run test:ghidra-wave900-plus-through-wave1095-recheck
```

Wave1095 (`render-state-matrix-support-review-wave1095`) reviewed render-state, D3D state-cache, matrix, and CDXEngine support helpers, then saved tag-only normalization for `0x00513af0 D3DStateCache__SetSlotMode4or5`. The focused readiness note is [`ghidra_render_state_matrix_support_review_wave1095_2026-06-04.md`](ghidra_render_state_matrix_support_review_wave1095_2026-06-04.md).

Coverage anchors:

- Static function-quality closure remains `6410/6410 = 100.00%`.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress remains `1560/1560 = 100.00%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Representative rows include `0x00513af0 D3DStateCache__SetSlotMode4or5`, `0x00513820 D3DStateCache__SetStateCached`, `0x00513870 D3DStateCache__SetStateRaw`, `0x00513b60 D3DStateCache__ForceSlotMode4or5`, `0x00550b10 CDXEngine__SetProjectionMatrix`, `0x00550ca0 CDXEngine__SetWorldMatrixElements`, `0x00550d50 CDXEngine__ApplyPendingRenderState`, and `0x00551200 CDXEngine__ApplyCachedLight`.
- Incoming caller context for `0x00513af0` includes `CConsole__RenderLoadingScreen`, `CFrontEnd__Render`, `CHud__RenderOverlay`, `CDXLandscape__RenderTerrain`, `CMeshRenderer__RenderMeshCore`, `CRenderQueue__BeginFrame`, `CVBufTexture__DrawSpriteEx`, and `CDXTrees__Render`.
- Verified backup: `G:\GhidraBackups\BEA_20260604-171413_post_wave1095_render_state_matrix_support_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.

Boundary: this is static Ghidra/documentation/probe coverage evidence only. Runtime render-state behavior, exact Direct3D enum/state-slot schema names, exact CDXEngine/D3DStateCache/global layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, and rebuild parity remain separate proof.

Validation result:

- `npm run test:ghidra-wave900-plus-through-wave1095-recheck`: PASS.
- Focused Wave1095 probe: PASS.
- Readiness notes: `198`.
- Covered waves: `196`.
- Package probe scripts: `194`.
- Evidence bases: `194`.
- Backup references: `196`.
- Apply scripts: `72`.
- Wave982-Wave1095 direct probes: `resultCount=114`, `passCount=1`, `failCount=113`, `disallowedFailureCount=0`.
- Current queue: `6410` total, `0` commentless, `0` exact-undefined signatures, `0` `param_N`, status `PASS`.

Probe token anchor: Wave1095; render-state-matrix-support-review-wave1095; 0x00513af0 D3DStateCache__SetSlotMode4or5; 0x00513820 D3DStateCache__SetStateCached; 0x00513b60 D3DStateCache__ForceSlotMode4or5; 0x00550b10 CDXEngine__SetProjectionMatrix; 0x00550ca0 CDXEngine__SetWorldMatrixElements; 0x00550d50 CDXEngine__ApplyPendingRenderState; 0x00551200 CDXEngine__ApplyCachedLight; 1560/1560 = 100.00%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; G:\GhidraBackups\BEA_20260604-171413_post_wave1095_render_state_matrix_support_review_verified; tag-only normalization.
