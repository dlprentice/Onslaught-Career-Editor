# Ghidra CFrontEnd Render Wave467 Evidence

Date: 2026-05-16

## Scope

Wave467 saved Ghidra name/signature/comment/tag corrections for `15` CFrontEnd render, camera, loop, and source-bridge targets:

`0x004662a0`, `0x00466990`, `0x00466de0`, `0x00466e70`, `0x00467010`, `0x004670b0`, `0x004679e0`, `0x00467ae0`, `0x004681c0`, `0x004681e0`, `0x004684d0`, `0x004685a0`, `0x004685f0`, `0x00468730`, and `0x00468750`.

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave467-frontend-render-current/`
- Apply script: `tools/ApplyCFrontEndRenderWave467.java`
- Probe: `tools/ghidra_cfrontend_render_wave467_probe.py`
- Test alias: `npm run test:ghidra-cfrontend-render-wave467`
- Dry summary: `updated=0 skipped=15 created=0 would_create=0 renamed=0 would_rename=2 missing=0 bad=0`
- Apply summary: `updated=15 skipped=0 created=0 would_create=0 renamed=2 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=15 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports verified `15` metadata rows, `15` tag rows, `72` xref rows, `15` decompile exports plus `index.tsv`, and `4095` focused instruction rows.
- Corrected `CFrontEnd__SetRenderViewAndProjection` to `CFrontEnd__UpdateCamera` and `CFrontEnd__VFunc_06_004685f0` to `CFrontEnd__RenderStart`.
- Hardened source-backed signatures/comments for `CFrontEnd__DrawLine`, `CFrontEnd__DrawBox`, `CFrontEnd__DrawPanel`, `CFrontEnd__DrawBarGraph`, `CFrontEnd__DrawBar`, alpha-state helpers, shadow-offset helpers, `CFrontEnd__Init`, `CFrontEnd__Run`, and the retail fixed-return `CFrontEnd__NumControllersPresent` helper.
- Queue after refresh: `6057` functions, `2129` commented, `3928` commentless, `1705` undefined signatures, `1582` `param_N` signatures.
- Current telemetry proxies: comment-backed `2129/6057 = 35.15%`; strict comment-plus-clean-signature `2065/6057 = 34.09%`.
- Verified backup: `G:\GhidraBackups\BEA_20260516-203319_post_wave467_cfrontend_render_verified` (`19` files, `157125511` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`).

## Boundary

This is static retail-binary/source-bridge evidence only. Runtime frontend rendering/controller/camera behavior, exact CFrontEnd/page/render-state layouts, exact platform-specific source identities, BEA launch behavior, game patching, and rebuild parity remain unproven.
