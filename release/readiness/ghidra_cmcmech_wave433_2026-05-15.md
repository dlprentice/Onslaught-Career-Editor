# Ghidra CMCMech Wave433 Correction

Status: public-safe static Ghidra evidence note
Date: 2026-05-15
Scope: saved retail `BEA.exe` Ghidra create/name/signature/comment/tag correction

## Summary

Wave433 corrected the adjacent `CMCMech`, mech mesh-token, and matrix-helper cluster. It recovered three missing `CMCMech` vtable-slot boundaries, corrected two stale `CMCMech` labels to `CMeshPart` predicates, hardened lifecycle/init/reset/set/get/translate signatures, and corrected nearby `MathMatrix3x3` helper signatures.

Two large bodies remain deliberately deferred: `CMCMech__UpdateBone` at `0x00499e30` and `CMCMech__UpdateBoneHierarchyRecursive` at `0x0049bd50`.

This is public-safe static evidence only. It does not launch or patch `BEA.exe`, does not mutate the installed Steam game, and does not include raw decompile text or private runtime proof.

## Saved Ghidra Changes

| Address | Saved state | Static evidence summary |
| --- | --- | --- |
| `0x00498080` | `CMeshPart__NameIsNotAnyMechCylinderBone` | Corrects stale `CMCMech` ownership; compares a mesh-part name against the 24 observed mech hydraulic-cylinder bone tokens and returns true when none match. |
| `0x00498270` | `CMeshPart__AnyChildNameIsNmidoutcyl` | Corrects stale `CMCMech` ownership; walks child mesh parts and checks child names for `Nmidoutcyl`. |
| `0x004983b0` | `CMCMech__Constructor` | `RET 0x4`; initializes the mech motion controller, owner/model fields, cached arrays, and global-list link state. |
| `0x00498510` | `CMCMech__ScalarDeletingDestructor` | Delete-flags wrapper for the destructor body. |
| `0x00498530` | `CMCMech__Destructor` | Destructor body restores the vtable, frees owned arrays, and unlinks from the global list. |
| `0x00498870` | `CMCMech__VFunc_00_OnTimedResetEvent_00498870` | Created vtable slot-0 boundary; handles event id/time `3000` (`0x0bb8`), calls `CMCMech__Reset`, requeues through `EVENT_MANAGER`, and ends with `RET 0x4`. |
| `0x004988b0` | `CMCMech__Reset` | Reset helper with two stack flags after `this`; refreshes cached pose/matrix state. |
| `0x00498bf0` | `CMCMech__SetParams` | `RET 0x1c`; stores seven motion parameters to observed offsets `+0x98`, `+0x9c`, `+0xa0`, `+0x0c`, `+0x10`, `+0xa4`, and `+0xc4`. |
| `0x00498c40` | `CMCMech__Init` | Initializes leg/bone arrays, animation channels, and shared mech-motion data from model/mesh evidence. |
| `0x00499bc0` | `CMCMech__GetFootHeight` | Samples static shadows and optional line trace context; final Ghidra signature preserves the hidden `this` nuance. |
| `0x00499d60` | `CMCMech__TranslatePositions` | Translates cached position arrays by an input vector. |
| `0x0049bbb0` | `MathMatrix3x3__DivideByScalarInPlace` | Corrects nearby matrix helper signature to scalar division in place. |
| `0x0049bc10` | `MathMatrix3x3__TransposeInPlace` | Corrects matrix transpose helper signature. |
| `0x0049bc40` | `MathMatrix3x3__Determinant` | Corrects determinant helper signature. |
| `0x0049bc80` | `MathMatrix3x3__BuildCofactorMatrix` | Corrects cofactor-matrix builder signature. |
| `0x0049be00` | `CMCMech__VFunc_04_UpdateInterpolatedBoneTransform_0049be00` | Created vtable slot-4 boundary; applies interpolated cached bone transform state, uses `DAT_008a9e44`, and ends with `RET 0x10`. |
| `0x0049c1d0` | `CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0` | Vtable slot-5 helper; writes interpolated/cached float data for a mesh part and output pointer, ending with `RET 0x8`. |
| `0x0049c240` | `CMCMech__VFunc_08_GetUpdateStateFlag_0049c240` | Created compact vtable slot-8 getter returning `this+0xc8`. |
| `0x0049c250` | `CMeshPart__NameAvoidsMechOptimizationTokens` | Corrects mech mesh-part token filter behavior around the observed tokens near `0x0062dcbc`, `0x0062df3c`, `0x0062df34`, `0x0062df30`, and `0x0062dd20`. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| `py -3 -m py_compile tools\ghidra_cmcmech_wave433_probe.py tools\ghidra_cmcmech_wave433_probe_test.py` | PASS | Focused probe modules compile. |
| `py -3 tools\ghidra_cmcmech_wave433_probe_test.py` | PASS | Focused tests passed `4/4`. |
| Expected-red `py -3 tools\ghidra_cmcmech_wave433_probe.py --check` before apply | PASS | Probe failed before mutation because expected dry/apply/read-back evidence was not present yet. |
| Headless `ApplyCmcMechWave433.java` initial dry/apply | PASS | Dry `updated=0 skipped=16 created=0 would_create=3 renamed=0 would_rename=4 missing=0 bad=0`; apply `updated=19 skipped=0 created=3 would_create=0 renamed=4 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. |
| Corrective dry/apply and verify dry | PASS | Corrective dry `updated=0 skipped=19 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`; corrective apply `updated=19 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`; verify dry repeated zero drift. |
| Post-apply metadata/tag/xref/vtable/instruction/decompile read-back | PASS | Verified `21` metadata rows, `21` tag rows, `95` xref rows, `64` vtable-slot rows, `7749` instruction rows, and `21` target decompile exports. |
| `cmd.exe /c npm run test:ghidra-cmcmech-wave433` | PASS | Focused probe returned `status: PASS` for `19` saved targets, with the two deferred large bodies excluded from semantic promotion. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS | Queue reports `6049` total functions, `1764` commented functions, `4285` commentless functions, `1811` undefined signatures, and `1775` `param_N` signatures. |
| Actual Ghidra project backup verification after Wave433 mutation | PASS | Copied the live project to `G:\GhidraBackups\BEA_20260515-210712_post_wave433_cmcmech_verified`; compared `19` files and `155814791` bytes with `MissingCount=0`, `HashDiffCount=0`, and `ExtraCount=0`. |

## Current Queue Telemetry

The refreshed static re-audit queue currently reports:

- Total function objects: `6049`
- Commented function objects: `1764`
- Commentless function objects: `4285`
- `undefined` signatures: `1811`
- Signatures still using `param_N`: `1775`

Telemetry-only proxies are comment-backed `1764/6049 = 29.16%` and strict clean-signature `1702/6049 = 28.14%`. These are not certification and are not completion gates.

## Not Proven

This wave does not prove runtime leg IK, foot-placement, bone-transform, or event-scheduling behavior; exact `CMCMech` concrete layout beyond observed offsets; exact virtual method names; exact local variable names/types; exact source-body identity; source-to-retail rebuild parity; BEA launch behavior; game patching; or runtime gameplay behavior.
