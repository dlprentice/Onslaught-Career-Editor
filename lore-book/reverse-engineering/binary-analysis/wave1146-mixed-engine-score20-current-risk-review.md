# Wave1146 Mixed Engine Score20 Current-Risk Review

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1146-mixed-engine-score20-current-risk-review`

Wave1146 re-read eight current-risk rows from the Wave1108 current focused denominator. The slice covers mixed CDamage/CConsole/CDebugMarkers/CEngine score20 current-risk evidence with fresh Ghidra metadata, tag, xref, instruction, and decompile exports. No Ghidra mutation was warranted.

## Coverage

The reviewed rows are already named, commented, and signature-clean in saved Ghidra. Wave1146 verifies the damage sentinel clear, console status-history reset, debug-marker shutdown allocator path, and engine resource/view/light helpers without changing names, signatures, comments, tags, function boundaries, executable bytes, BEA runtime state, installed game files, saves, or private assets.

| Address | Static read-back |
| --- | --- |
| `0x00440b70 CDamage__ctor_clear_head_and_init_flag` | Clears the damage-object head pointer and `+0x1588c` initialization/sentinel field used by `CDamage__Init`; supersedes stale UnitAI-owner history. |
| `0x004416e0 CConsole__ResetStatusHistoryBuffer` | Clears 30 `0x50`-byte status-history text slots and timestamp slots, resets `+0x9e4/+0x9e8`, and gates `+0x9ec` through `DAT_00662dd0`. |
| `0x00441e50 CDebugMarkers__Shutdown` | Walks the marker head passed by reference, unlinks entries from `DAT_0066ffb0`, and frees through `CDXMemoryManager__Free` at `0x00549220` with context `0x009c3df0`. |
| `0x00449d50 CEngine__InitResources` | Loads zoom textures, blob shadows, `hilight.tga`, `hiteffect.tga`, `cloak.tga`, and the landscape cloud-shadow texture. |
| `0x00449dc0 CEngine__LoadAllNamedMeshes` | Resets the global named-mesh count, reports `Loading named meshes`, reads names from the buffer, reuses existing entries by case-insensitive compare, and calls `CMesh__FindOrCreate` for new entries. |
| `0x00449ef0 CEngine__GetViewMatrixFromCamera` | Uses two stack arguments, builds camera/view basis context, calls the camera orientation vfunc, multiplies bases, and copies twelve dwords to `outViewMatrix`. |
| `0x0044a110 CEngine__ResetPos` | Uses two stack arguments, loads `mLandscape` from `this+0x10`, and forwards reset coordinates to the landscape reset-position helper. |
| `0x0044a2d0 CEngine__SetupLights` | Normalizes the MAP sun vector, calls the current Atmospherics notifier, updates view-vector/matrix context, and fills global render-light matrices. |

## Evidence Counts

- Primary exports: `8` metadata rows, `8` tag rows, `12` xref rows, `466` instruction rows, and `8` decompile rows.
- Backup: `G:\GhidraBackups\BEA_20260605-174520_post_wave1146_mixed_engine_score20_current_risk_review_verified`; `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed backup: `G:\GhidraBackups\BEA_20260605-171711_post_wave1145_component_flag_current_risk_review_verified`.
- Codex subagent usage: none for this slice; Codex root selected and audited the mixed tranche locally against fresh exports.

## Progress

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless / exact-undefined / `param_N`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Wave911 focused historical residual: `812/1408 = 57.67%`.
- Wave911 top-500: `500/500 = 100.00%`.
- Wave1108 current focused accounting: `306/1179 = 25.95%`.
- Current risk candidates: 6166.
- Current focused candidates: 1178.
- Live regenerated current focused candidates: 1178.
- Remaining active focused work: 873.

## Boundary

Wave1146 is static Ghidra evidence only. It does not prove runtime damage behavior, runtime console behavior, runtime debug-marker behavior, runtime engine/render behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, or rebuild parity.

Probe token anchor: Wave1146; wave1146-mixed-engine-score20-current-risk-review; 306/1179 = 25.95%; 8 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 873; current risk candidates: 6166; mixed CDamage/CConsole/CDebugMarkers/CEngine score20 current-risk review; fresh Ghidra export; damage sentinel; console status-history; debug-marker shutdown; engine resource/view/light helpers; read-only review; no mutation; no Codex subagent; 0 / 0 / 0; 6411/6411 = 100.00%; CDamage__ctor_clear_head_and_init_flag; CConsole__ResetStatusHistoryBuffer; CDebugMarkers__Shutdown; CEngine__InitResources; CEngine__LoadAllNamedMeshes; CEngine__GetViewMatrixFromCamera; CEngine__ResetPos; CEngine__SetupLights; G:\GhidraBackups\BEA_20260605-174520_post_wave1146_mixed_engine_score20_current_risk_review_verified; G:\GhidraBackups\BEA_20260605-171711_post_wave1145_component_flag_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
