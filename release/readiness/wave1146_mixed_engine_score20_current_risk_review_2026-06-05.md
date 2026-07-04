# Wave1146 Mixed Engine Score20 Current-Risk Readiness Note

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1146-mixed-engine-score20-current-risk-review`

Wave1146 re-read eight mixed CDamage/CConsole/CDebugMarkers/CEngine score20 current-risk rows with fresh Ghidra exports and made no mutation: no rename, signature change, comment/tag change, function-boundary change, executable-byte change, BEA launch, installed-game mutation, save mutation, or runtime-file mutation.

Probe token anchor: Wave1146; wave1146-mixed-engine-score20-current-risk-review; 306/1179 = 25.95%; 8 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 873; current risk candidates: 6166; mixed CDamage/CConsole/CDebugMarkers/CEngine score20 current-risk review; fresh Ghidra export; damage sentinel; console status-history; debug-marker shutdown; engine resource/view/light helpers; read-only review; no mutation; no Codex subagent; 0 / 0 / 0; 6411/6411 = 100.00%; CDamage__ctor_clear_head_and_init_flag; CConsole__ResetStatusHistoryBuffer; CDebugMarkers__Shutdown; CEngine__InitResources; CEngine__LoadAllNamedMeshes; CEngine__GetViewMatrixFromCamera; CEngine__ResetPos; CEngine__SetupLights; [maintainer-local-ghidra-backup-root]\BEA_20260605-174520_post_wave1146_mixed_engine_score20_current_risk_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260605-171711_post_wave1145_component_flag_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Fresh evidence:

- `pre-metadata.tsv`: `8` rows, `targets=8 found=8 missing=0`.
- `pre-tags.tsv`: `8` rows, `missing=0`.
- `pre-xrefs.tsv`: `12` rows.
- `pre-instructions.tsv`: `466` instruction rows, `targets=8 missing=0`.
- `pre-decompile/index.tsv`: `8` rows, `targets=8 dumped=8 missing=0 failed=0`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-174520_post_wave1146_mixed_engine_score20_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-171711_post_wave1145_component_flag_current_risk_review_verified`.
- Codex subagent usage: none for this slice; Codex root selected and audited the mixed tranche locally.

Reviewed rows:

| Address | Static read-back |
| --- | --- |
| `0x00440b70 CDamage__ctor_clear_head_and_init_flag` | Damage head/sentinel clear; `+0x1588c` initialization field used by `CDamage__Init`. |
| `0x004416e0 CConsole__ResetStatusHistoryBuffer` | Console status-history buffer reset; 30 slots, `+0x9e4/+0x9e8`, and `DAT_00662dd0` gate. |
| `0x00441e50 CDebugMarkers__Shutdown` | Debug-marker shutdown; unlinks `DAT_0066ffb0` and frees via `CDXMemoryManager__Free` at `0x00549220`. |
| `0x00449d50 CEngine__InitResources` | Engine resource loader for zoom, shadow, highlight, hit-effect, cloak, and cloud-shadow textures. |
| `0x00449dc0 CEngine__LoadAllNamedMeshes` | Named mesh table reset/load/reuse path with `CMesh__FindOrCreate`. |
| `0x00449ef0 CEngine__GetViewMatrixFromCamera` | Camera/view matrix helper with two stack arguments and 12-dword output copy. |
| `0x0044a110 CEngine__ResetPos` | Landscape reset-position forwarding helper using `this+0x10`. |
| `0x0044a2d0 CEngine__SetupLights` | MAP sun-vector normalization, Atmospherics notifier call, and render-light matrix setup. |

Accounting after Wave1146:

- Static closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Wave911 focused: `812/1408 = 57.67%`.
- Wave911 top-500: `500/500 = 100.00%`.
- Wave1108 current focused accounting: `306/1179 = 25.95%`.
- Current risk candidates: 6166.
- Current focused candidates: 1178.
- Live regenerated current focused candidates: 1178.
- Remaining active focused work: 873.

This is static Ghidra evidence only. Runtime damage behavior, runtime console behavior, runtime debug-marker behavior, runtime engine/render behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof. Artifact commit traceability is recorded in `reverse-engineering/binary-analysis/static-reaudit-progress.json` and repo state closeout after commit.
