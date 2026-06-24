# Ghidra Wave900 Through Wave1071 Recheck Readiness Note

Status: complete local validation evidence
Date: 2026-06-02
Scope: `wave900-plus-through-wave1071-recheck`

This note extends the rolling Wave900+ recheck gate through Wave1071 after the read-only `texel-unpack-head-mid-review-wave1071` pass. It keeps the prior Wave900+ notes as historical evidence and adds the current Wave1071 readiness/probe/backup anchors to the live aggregate gate.

Current anchors:

- Latest operational wave: Wave1071, `texel-unpack-head-mid-review-wave1071`.
- Latest focused probe: `tools/ghidra_texel_unpack_head_mid_review_wave1071_probe.py`.
- Latest readiness note: `release/readiness/ghidra_texel_unpack_head_mid_review_wave1071_2026-06-02.md`.
- Latest verified backup: `G:\GhidraBackups\BEA_20260602-031627_post_wave1071_texel_unpack_head_mid_review_verified`.

Current percentages:

- Static export-contract function-quality closure: `6246/6246 = 100.00%`.
- Wave911 focused re-audit progress: `812/1408 = 57.67%`.
- Expanded static surface progress: `1319/1560 = 84.55%`.
- Wave911 top-500 risk-ranked coverage: `500/500 = 100.00%`.

Representative Wave1071 anchors:

- `0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4`
- `0x00584d78 CFastVB__UnpackTexels_Bits565ToFloat4`
- `0x0058546f CMeshCollisionVolume__UnpackTexels_Bits16_16_16_16_ToFloat4`
- `0x005856b8 CDXTexture__UnpackTexels_Bits332A8ToFloat4`
- `0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor`
- `0x0058579b CTexture__UnpackTexels_Bits444ToFloat4_AlphaOne`
- `0x00585bd3 CFastVB__TexelUnpackProfile_scalar_deleting_dtor`
- `0x00585cb0 CTexture__UnpackTexels_Signed8_8_ToFloat4_RG`
- `0x00585e9f CDXTexture__UnpackTexels_Signed8_8_A8_ToFloat4_RG`
- `0x00585fa3 CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4`

Validation expectation:

- The aggregate package script is `test:ghidra-wave900-plus-through-wave1071-recheck`.
- The focused Wave1071 probe validates the primary/context exports, docs, ledgers, package scripts, queue closure, and backup summary.

Latest aggregate run:

- `test:ghidra-wave900-plus-through-wave1071-recheck`: PASS.
- Readiness notes: `174`.
- Covered waves: `172`.
- Package probe scripts: `170`.
- Evidence bases: `170`.
- Backup references: `172`.
- Apply scripts: `53`.
- Wave982-Wave1071 direct probes: result count `90`, pass count `2`, fail count `88`, disallowed failure count `0`.
- Current queue: `6246` total functions, `0` commentless, `0` exact-undefined signatures, `0` `param_N`, status `PASS`.
- Direct-probe failures remain limited to allowed stale baton/current-doc expectation classes; no disallowed metadata/signature/tag/decompile/log/backup/lock/evidence mismatch category was observed.

Boundary note: this aggregate gate proves local static evidence coverage, backup references, probe/doc wiring, and zero export-contract function-quality debt after validation. It does not prove runtime texture output behavior, runtime codec/FourCC behavior, exact profile/descriptor/layout identity, exact source identity, BEA patching, gameplay outcomes, or rebuild parity.

Probe token anchor: Wave1071; texel-unpack-head-mid-review-wave1071; 0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4; 0x0058546f CMeshCollisionVolume__UnpackTexels_Bits16_16_16_16_ToFloat4; 0x005856b8 CDXTexture__UnpackTexels_Bits332A8ToFloat4; 0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor; 0x00585fa3 CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4; 812/1408 = 57.67%; 1319/1560 = 84.55%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260602-031627_post_wave1071_texel_unpack_head_mid_review_verified; read-only review.
