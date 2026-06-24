# Ghidra CMCGroundAttack/HiveBoss Wave432 Correction

Status: public-safe static Ghidra evidence note
Date: 2026-05-15
Scope: saved retail `BEA.exe` Ghidra create/name/signature/comment/tag correction

## Summary

Wave432 corrected the adjacent `CMCGroundAttack` and `CMCHiveBoss` motion-controller cluster. It recovered three missing vtable-slot boundaries, corrected eight stale saved labels/signatures, and narrowed the nearby mesh-part token helpers to observed `turret` / `barrel` behavior.

This is public-safe static evidence only. It does not launch or patch `BEA.exe`, does not mutate the installed Steam game, and does not include raw decompile text or private runtime proof.

## Saved Ghidra Changes

| Address | Saved state | Static evidence summary |
| --- | --- | --- |
| `0x004964d0` | `CMCGroundAttack__Constructor` | `RET 0x4`; installs vtable `0x005dc330`, stores owner at `+0x08`, and seeds cached state fields. |
| `0x00496500` | `CMCGroundAttack__ScalarDeletingDestructor` | Vtable slot-1 delete-flags wrapper for `CMCGroundAttack__Destructor`. |
| `0x00496520` | `CMCGroundAttack__Destructor` | Restores the `CMCGroundAttack` vtable, clears `+0x08`, and tails into the base motion-controller destructor. |
| `0x00496540` | `CMCGroundAttack__VFunc_04_UpdateTurretTransform_00496540` | Created vtable slot-4 boundary; checks the `turret` token, performs shared transform math, refreshes cached owner values, and ends with `RET 0x10`. |
| `0x004968a0` | `CMCGroundAttack__VFunc_08_CheckCachedMotionState_004968a0` | Created vtable slot-8 boundary; compares owner motion fields against cached `this+0x0c/+0x10` state. |
| `0x004968f0` | `CMeshPart__NameIsNotTurret` | Cdecl mesh-part helper for token `0x0062dd20` (`turret`). |
| `0x00496910` | `CMeshPart__AnySubPartNameIsTurret` | Walks child mesh parts for a `turret` child name. |
| `0x00496f60` | `CMeshPart__NameAvoidsTurretAndBarrelPrefix` | Corrects older wording: rejects exact `turret`, then rejects `barrel` prefix matches. |
| `0x00497090` | `CMCHiveBoss__Constructor` | `RET 0x4`; constructs the destructable-segments motion-controller base with owner `+0x178`, clears cached cylinder slots, and installs vtable `0x005dc388`. |
| `0x00497110` | `CMCHiveBoss__ScalarDeletingDestructor` | Vtable slot-1 delete-flags wrapper through the destructable-segments destructor thunk. |
| `0x004976d0` | `CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0` | Created vtable slot-4 boundary; lazily caches named collision cylinders, applies rumble transforms, branches through cached cylinder slots, and ends with `RET 0x10`. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| `py -3 tools\ghidra_cmcgroundattack_hiveboss_wave432_probe_test.py` | PASS | Focused tests passed `4/4`. |
| Expected-red `cmd.exe /c npm run test:ghidra-cmcgroundattack-hiveboss-wave432` before apply | PASS | Probe failed on missing dry/apply/read-back evidence before mutation. |
| Headless `ApplyCmcGroundAttackHiveBossWave432.java` dry/apply | PASS | Dry `updated=0 skipped=8 created=0 would_create=3 renamed=0 would_rename=8 missing=0 bad=0`; apply `updated=11 skipped=0 created=3 would_create=0 renamed=8 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. |
| Post-apply idempotent dry run | PASS | Dry `updated=0 skipped=11 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. |
| Post-apply metadata/tag/xref/vtable/instruction/decompile read-back | PASS | Verified `11` metadata rows, `11` tag rows, `16` xref rows, `48` vtable-slot rows, `2959` instruction rows, `769` focused full HiveBoss slot-4 instruction rows, and `11` target decompile exports. |
| `cmd.exe /c npm run test:ghidra-cmcgroundattack-hiveboss-wave432` | PASS | Focused probe returned `status: PASS` with zero failures. |
| Actual Ghidra project backup verification after Wave432 mutation | PASS | Copied `BEA.gpr` and `BEA.rep` to `G:\GhidraBackups\BEA_20260515_191902_post_wave432_cmcgroundattack_hiveboss_verified`; compared `19` files and `155650951` bytes. |

## Current Queue Telemetry

The refreshed static re-audit queue currently reports:

- Total function objects: `6046`
- Commented function objects: `1745`
- Commentless function objects: `4301`
- `undefined` signatures: `1820`
- Signatures still using `param_N`: `1781`

Telemetry-only proxies are comment-backed `1745/6046 = 28.86%` and strict clean-signature `1683/6046 = 27.84%`. These are not certification and are not completion gates.

## Not Proven

This wave does not prove runtime `CMCGroundAttack` transform/state behavior, runtime `CMCHiveBoss` cylinder-transform behavior, exact concrete controller layouts beyond observed offsets, exact local variable names/types, exact source-body identity, source-to-retail rebuild parity, BEA launch behavior, game patching, or runtime gameplay behavior.
