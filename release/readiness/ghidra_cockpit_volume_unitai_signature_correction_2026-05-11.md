# Ghidra Cockpit / Volume / UnitAI Signature Correction - 2026-05-11

Status: public-safe static RE evidence
Scope: saved Ghidra name/signature/comment correction only
Privacy: no raw decompile excerpts, screenshots, runtime logs, copied executables, private game payloads, or private absolute paths are included.

## Summary

Wave 321 revisited the next static re-audit queue slice after the CLIParams/FlexArray correction. Fresh Ghidra metadata, decompile, xref, instruction, and callsite read-back covered one cockpit constructor-like body, one GeneralVolume randomized-offset helper, two GeneralVolume transform-transition helpers, four CUnitAI deploy tracking/animation helpers, and one generic matrix helper.

The serialized headless correction saved `9` signatures/comments and made `2` renames:

- `0x004244b0`: `CCockpit__ctor`, replacing the stale `CCockpit__ctor_like_004244b0` label and removing a phantom extra parameter.
- `0x004247a0`: `CGeneralVolume__InitRandomizedVelocityOffsets`, removing a stale extra float parameter after callsite read-back.
- `0x00424920` and `0x00424990`: `CGeneralVolume__BeginFlyToWalkTransition` and `CGeneralVolume__BeginWalkToFlyTransition`, both corrected to ECX-only object dispatch signatures.
- `0x00424a20`, `0x00424be0`, `0x00424ca0`, and `0x004250f0`: CUnitAI deploy aim, phase, target-tracking, and neutral-decay helpers with named `this` parameters.
- `0x00425760`: `Mat34__OrthonormalizeAxes`, replacing the stale CUnitAI-specific owner label with an owner-neutral matrix helper name.

## Validation

Headless dry/apply results:

- `ApplyCockpitVolumeUnitAiSignatureCorrection.java dry`: `updated=0 skipped=9 renamed=0 missing=0 bad=0`
- `ApplyCockpitVolumeUnitAiSignatureCorrection.java apply`: `updated=9 skipped=0 renamed=2 missing=0 bad=0`
- Ghidra reported `REPORT: Save succeeded` for the apply run.

Read-back and focused checks:

- Metadata read-back: `9/9` targets
- Decompile read-back: `9/9` targets
- Xref read-back: `18` rows
- Instruction read-back: `2205` rows
- Focused probe: `PASS`, classification `ghidra-cockpit-volume-unitai-signature-correction.v1`
- Queue snapshot after correction: `5876` functions, `724` with comments, `5152` commentless, `2013` undefined signatures, and `2310` `param_N` signatures

Raw machine-readable evidence remains under ignored repo-relative paths such as `subagents/ghidra-static-reaudit/cockpit-volume-unitai-wave321/current/`.

## Proven

- The saved Ghidra project now has corrected names/signatures/comments for the cockpit constructor-like body, the selected GeneralVolume random/transition helpers, the selected UnitAI deploy helpers, and a generic Mat34 orthonormalization helper.
- Callsite read-back narrows stale phantom parameters for the cockpit constructor, transition helpers, and randomized-offset helper.
- `0x00425760` is no longer recorded as CUnitAI-specific because current xrefs support an owner-neutral matrix helper classification.
- The generic static re-audit queue no longer lists this slice as commentless or `param_N` signature debt.

## Not Proven

- This does not prove runtime cockpit, morph, deploy, target-tracking, or matrix behavior.
- This does not prove exact source-to-retail identity for source bodies absent from the current Stuart source snapshot.
- This does not prove concrete class/struct layouts, local variable names, tags, structure types, or rebuild parity.
- This does not launch, patch, or mutate `BEA.exe`.
