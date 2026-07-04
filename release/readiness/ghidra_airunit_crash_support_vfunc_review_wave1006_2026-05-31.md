# Ghidra Air-Unit Crash/Support Vfunc Review Wave1006 Readiness Note

Status: complete static read-back evidence with metadata-only normalization
Date: 2026-05-31
Scope: `air-unit-crash-support-vfunc-review-wave1006`

Wave1006 re-read the prior air-unit / plane-family virtual-function owner correction around crash/support gates and the shared slot-117 position-delta predicate. Fresh vtable evidence confirmed the saved owner names still match the current Ghidra database. The wave saved comment/tag normalization only: no rename, no signature change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00402fa0 CUnit__UpdateMotionAndTrailEffects` | CBigAirUnit vtable slot 66 at `0x005e362c` and CAirUnit slot 66 at `0x005e3880` point here; body remains a unit motion/effects pass with attachment/trail and low-altitude crash context. |
| `0x00403730 CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport` | CFenrir, CCarver, CCarrier, CBigAirUnit, and CAirUnit vtable slot 68 rows point here; body sets a timestamp and reaches crash/death flow when flag bit 4 is set and unit-data `+0x11c` is zero. |
| `0x00403760 CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes` | Same air-unit family slot 69 rows point here; body resets the D0 threshold helper and reaches crash/death flow when unit-data `+0x11c/+0x124` are both zero. |
| `0x00403a50 CAirUnit__VFunc_117_HasPositionDeltaWhileFlag4Clear` | CFenrir, CCarver, CDiveBomber, CPlane, CCarrier, CGroundAttackAircraft, CBomber, CBigAirUnit, and CAirUnit slot 117 rows point here; body returns true when position components differ while flag bit 4 is clear. |
| `0x0047bf60 CPlane__VFunc_69_CrashIfNoSupportModes` | CDiveBomber, CPlane, CGroundAttackAircraft, and CBomber vtable slot 69 rows point here; body calls the CAirUnit slot-69 helper then performs the plane-family zero-support-mode crash/death check. |
| `0x004d20a0 CPlane__VFunc_68_CrashIfNoAirSupport` | Same plane-family vtables slot 68 rows point here; body calls the CAirUnit slot-68 helper then performs the plane-family no-air-support crash/death check. |

Read-back evidence:

- `ApplyAirUnitCrashSupportVfuncReviewWave1006.java dry`: `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 missing=0 bad=0`
- `ApplyAirUnitCrashSupportVfuncReviewWave1006.java apply`: `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=6 missing=0 bad=0`
- `ApplyAirUnitCrashSupportVfuncReviewWave1006.java final dry`: `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Pre/post target exports: 6 metadata rows, 6 tag rows, 39 xref rows, 570 body-instruction rows, and 6 decompile rows.
- Context exports: 5 metadata rows, 5 decompile rows, and 200 body-instruction rows.
- Vtable evidence: 1152 slot rows and 9 RTTI type rows covering CFenrir, CCarver, CDiveBomber, CPlane, CCarrier, CGroundAttackAircraft, CBomber, CBigAirUnit, and CAirUnit.
- Queue closure remains `6223/6223 = 100.00%` with 0 commentless functions, 0 exact-undefined signatures, and 0 `param_N` signatures.
- Wave911 focused re-audit progress remains `485/1408 = 34.45%`.
- Expanded static surface progress advances to `662/1478 = 44.79%`.
- Wave911 top-500 risk-ranked coverage remains `384/500 = 76.80%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-135619_post_wave1006_airunit_crash_support_vfunc_review_verified`, 19 files, 173869959 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The saved Ghidra project still places the selected crash/support virtual helpers in the air-unit and plane-family vtables named above.
- The old owner-correction boundaries still hold: the slot-68/69 rows are not `CExplosionInitThing` or generic `CUnitAI` methods, and slot 117 is not a `CFrontEndPage` method.
- The six selected rows now carry `air-unit-crash-support-vfunc-review-wave1006` and `wave1006-readback-verified` tags with bounded comments.

What remains unproven:

- Runtime aircraft crash behavior.
- Runtime flight/support-mode behavior.
- Exact source virtual names.
- Concrete `CUnit`, `CAirUnit`, `CPlane`, support-field, position, or flag layouts.
- Exact source-body identity.
- BEA patching behavior.
- Rebuild parity.
