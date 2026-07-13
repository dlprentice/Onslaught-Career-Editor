# Ghidra CollisionSeekingRound Boundary / Signature Correction - 2026-05-11

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x00425a10` → `CCollisionSeekingInfantryBloke__CheckCollisionFlagsWithDeadSideBranch` (was `CCollisionSeekingInfantryBloke__CheckSideCompatibleOrCollisionFlags`). The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: public-safe static RE evidence
Scope: saved Ghidra boundary/name/signature/comment correction only
Privacy: no raw decompile excerpts, screenshots, runtime logs, copied executables, private game payloads, or private absolute paths are included.

## Summary

Wave 322 revisited the `CCollisionSeekingRound` collision-seeking projectile cluster after the cockpit/volume/UnitAI correction. Fresh Ghidra metadata, decompile, xref, instruction, vtable-target, and create-function review covered the vtable slots around `0x00425b50` through `0x00426a40`, plus related `CLine`, `CMeshCollisionVolume`, and infantry-bloke collision-filter helpers.

The serialized headless correction recovered `8` missing function boundaries and saved `19` names/signatures/comments:

- `0x00425b50`, `0x00425c60`, `0x00425e30`, `0x00426370`, `0x004264a0`, `0x00426920`, `0x00426a00`, and `0x00426a20`: recovered `CCollisionSeekingRound` vtable/callback boundaries.
- `0x00426360`: corrected from the stale CollisionSeekingRound-specific label to owner-neutral `CLine__SetBaseVtable_00426360`.
- `0x00426300` and `0x00426340`: saved scalar-deleting destructor wrappers for the mesh collision-volume helper and CLine-style helper.
- `0x00426150`, `0x004263f0`, `0x00426460`, `0x00426480`, `0x00426900`, `0x004269b0`, and `0x00426a40`: hardened existing `CCollisionSeekingRound` init/destructor/mask/check/effect signatures and comments.
- `0x00425a10`: hardened the related infantry-bloke collision-filter helper.

## Validation

Headless create and correction results:

- `CreateFunctionsFromAddressList.java dry`: `would_create=8 failed=0`
- `CreateFunctionsFromAddressList.java apply`: `created=8 renamed=8 failed=0`
- `ApplyCollisionSeekingRoundBoundarySignatureCorrection.java dry`: `updated=0 skipped=19 renamed=0 missing=0 bad=0`
- `ApplyCollisionSeekingRoundBoundarySignatureCorrection.java apply`: `updated=19 skipped=0 renamed=12 missing=0 bad=0`
- Final comment-token apply after tightening two comments: `updated=19 skipped=0 renamed=0 missing=0 bad=0`
- Ghidra reported `REPORT: Save succeeded` for the apply runs.

Read-back and focused checks:

- Metadata read-back: `19/19` targets
- Decompile read-back: `19/19` targets
- Xref read-back: `94` rows
- Instruction read-back: `1691` rows
- Created boundary read-back: `8/8`
- Focused probe: `PASS`, classification `ghidra-collision-seeking-round-boundary-signature-correction.v1`
- Queue snapshot after correction: `5884` functions, `743` with comments, `5141` commentless, `2004` undefined signatures, and `2307` `param_N` signatures
- Baseline probe after correction: `5884` functions, `0` weak names, `0` uncertain owners/helpers/wrappers, and no missing seed function objects.
- Actual Ghidra project backup: copied `BEA.gpr` and `BEA.rep` to `[maintainer-local-backup-volume]` after the final saved write; verification matched `19` files, `151456647` bytes, and `0` manifest diffs.

Raw machine-readable evidence remains under ignored repo-relative paths such as `subagents/ghidra-static-reaudit/collision-seeking-wave322/current/`.

## Proven

- The saved Ghidra project now contains function objects for the eight previously missing `CCollisionSeekingRound` boundary targets in this cluster.
- The final saved names, signatures, and comments read back for all `19` checked targets.
- `0x00426360` is no longer recorded as CollisionSeekingRound-specific because broader CLine-helper xref evidence makes an owner-neutral name safer.
- The full static re-audit quality snapshot now reflects `5884` function objects after the recovered boundaries.

## Not Proven

- This does not prove runtime projectile, collision-response, or sound/event behavior.
- This does not prove exact source virtual method names for the recovered retail vtable slots.
- This does not prove concrete class/struct layouts, local variable names, tags, structure types, or rebuild parity.
- This does not launch, patch, or mutate `BEA.exe`.
