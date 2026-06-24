# Ghidra Wave900 Through Wave1070 Recheck Readiness Note

Status: complete local validation evidence
Date: 2026-06-02
Scope: `wave900-plus-through-wave1070-recheck`

This note extends the rolling Wave900+ recheck gate through Wave1070 after the read-only `texel-unpack-tail-review-wave1070` pass. It keeps the prior Wave900+ notes as historical evidence and adds the current Wave1070 readiness/probe/backup anchors to the live aggregate gate.

Current anchors:

- Latest operational wave: Wave1070, `texel-unpack-tail-review-wave1070`.
- Latest focused probe: `tools/ghidra_texel_unpack_tail_review_wave1070_probe.py`.
- Latest readiness note: `release/readiness/ghidra_texel_unpack_tail_review_wave1070_2026-06-02.md`.
- Latest verified backup: `G:\GhidraBackups\BEA_20260602-022701_post_wave1070_texel_unpack_tail_review_verified`.

Current percentages:

- Static export-contract function-quality closure: `6246/6246 = 100.00%`.
- Wave911 focused re-audit progress: `812/1408 = 57.67%`.
- Expanded static surface progress: `1278/1560 = 81.92%`.
- Wave911 top-500 risk-ranked coverage: `500/500 = 100.00%`.

Representative Wave1070 anchors:

- `0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor`
- `0x005860ba CTexture__UnpackTexels_Signed16_16_ToFloat4_RG`
- `0x005861b4 CDXTexture__UnpackTexels_Signed2_10_10_10_ToFloat4`
- `0x00586305 CDXTexture__UnpackTexels_Signed16_16_16_16_ToFloat4`
- `0x00586438 CTexture__UnpackTexels_NormalXY_Signed8_8_ReconstructZ`
- `0x00586609 CDXTexture__UnpackTexels_CallbackPerTexel_Stride2_SetRGBAOne`
- `0x005866d2 CFastVB__UnpackTexels_CallbackPerTexel_Stride4_SetZAOne`
- `0x0058677b CDXTexture__UnpackTexels_CallbackSingleTexel`
- `0x0058686f CTexture__UnpackTexels_CopyRaw128`
- `0x005868d1 CFastVB__UnpackTexels_L16A16_ToFloat4`
- `0x00586bb7 CFastVB__FlushPendingConvertedRows16`
- `0x00586f37 CFastVB__DecodeRowWindowToScratchPairs`

Validation expectation:

- The aggregate package script is `test:ghidra-wave900-plus-through-wave1070-recheck`.
- The focused Wave1070 probe validates the primary/context exports, docs, ledgers, package scripts, queue closure, and backup summary.

Latest aggregate run:

- `test:ghidra-wave900-plus-through-wave1070-recheck`: PASS.
- Readiness notes: `173`.
- Covered waves: `171`.
- Package probe scripts: `169`.
- Evidence bases: `169`.
- Backup references: `171`.
- Apply scripts: `53`.
- Wave982-Wave1070 direct probe TSV: `resultCount=89`, `passCount=1`, `failCount=88`, `disallowedFailureCount=0`.
- Current queue: `6246` total, `0` commentless, `0` exact-undefined signatures, `0` `param_N`, status PASS.

Boundary note: this aggregate gate proves local static evidence coverage, backup references, probe/doc wiring, and zero export-contract function-quality debt. It does not prove runtime texture output behavior, runtime codec/FourCC behavior, exact profile/descriptor/row-window layouts, exact source identity, BEA patching, gameplay outcomes, or rebuild parity.

Probe token anchor: Wave1070; texel-unpack-tail-review-wave1070; 0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor; 0x005860ba CTexture__UnpackTexels_Signed16_16_ToFloat4_RG; 0x005861b4 CDXTexture__UnpackTexels_Signed2_10_10_10_ToFloat4; 0x00586305 CDXTexture__UnpackTexels_Signed16_16_16_16_ToFloat4; 0x00586438 CTexture__UnpackTexels_NormalXY_Signed8_8_ReconstructZ; 0x00586609 CDXTexture__UnpackTexels_CallbackPerTexel_Stride2_SetRGBAOne; 0x005866d2 CFastVB__UnpackTexels_CallbackPerTexel_Stride4_SetZAOne; 0x0058677b CDXTexture__UnpackTexels_CallbackSingleTexel; 0x0058686f CTexture__UnpackTexels_CopyRaw128; 0x005868d1 CFastVB__UnpackTexels_L16A16_ToFloat4; 0x00586bb7 CFastVB__FlushPendingConvertedRows16; 0x00586f37 CFastVB__DecodeRowWindowToScratchPairs; 812/1408 = 57.67%; 1278/1560 = 81.92%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260602-022701_post_wave1070_texel_unpack_tail_review_verified; read-only review.
