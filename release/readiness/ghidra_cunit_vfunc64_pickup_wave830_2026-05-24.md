# Ghidra CUnit VFunc64 Pickup Wave830 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `cunit-vfunc64-pickup-wave830`

Probe anchor: Wave830 CUnit vfunc64 pickup.

Wave830 corrected the former raw commentless queue head `0x004ef100 CUnit__RunTransitionStepThreeTimes` to `0x004ef100 CUnit__VFunc64_SpawnConfiguredPickupThreeTimes`. The pass saved the signature `void __fastcall CUnit__VFunc64_SpawnConfiguredPickupThreeTimes(void * this)`, comments, and tags after serialized headless dry/apply/read-back. It made no function-boundary changes and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x004ef100 CUnit__VFunc64_SpawnConfiguredPickupThreeTimes` | DATA xref from vtable slot address `0x005e1610` in the CUnit-family vtable at `0x005e1510`; slot index `64`. |
| `0x004ef100` body | Preserves the ECX receiver in EDI, initializes ESI to `3`, then loops with `ECX=this` to call `CUnit__SpawnConfiguredPickupIfAboveWater` three times before returning. |
| `0x004f9490 CUnit__SpawnConfiguredPickupIfAboveWater` | Existing Wave526 helper evidence builds a local CInitThing-style record, resolves position from the unit, copies side/team field `this+0x138`, and creates the profile-configured pickup from profile field `+0xec` when height is above `DAT_006fbdfc`. |
| Context rows | Adjacent transition-state helpers `0x004ef000`, `0x004ef050`, and `0x004ef0f0` remain the saved Wave512 transition helpers; Wave830 does not claim the exact source virtual name or the reason for three pickup-spawn passes. |

Read-back evidence:

- `ApplyCUnitVFunc64PickupWave830.java dry`: `updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyCUnitVFunc64PickupWave830.java apply`: `READBACK_OK`, then `updated=1 skipped=0 renamed=1 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyCUnitVFunc64PickupWave830.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 1 xref row, 37 instruction rows, 1 decompile row, 5 context metadata rows, 5 context decompile rows, and 80 CUnit-family vtable rows.
- Queue after Wave830: `6098` total functions, `5651` commented, `447` commentless, `0` exact-undefined signatures, `0` `param_N` signatures, comment-backed proxy `5651/6098 = 92.67%`, strict clean-signature proxy `5651/6098 = 92.67%`.
- Next raw commentless row: `0x004f2660 CText__CopyFrom`.
- Verified backup: `G:\GhidraBackups\BEA_20260524-220229_post_wave830_cunit_vfunc64_pickup_verified`, 19 files, 171641735 bytes, `DiffCount=0`.

What this proves:

- The target function row exists in the saved Ghidra project.
- The saved name, signature, comment, and tags are present after read-back.
- The CUnit-family vtable at `0x005e1510` references the target at slot index 64 through DATA slot address `0x005e1610`.
- The body is a small but important connective virtual helper: its static role is a repeated bridge from CUnit-family vtable dispatch into the configured pickup-spawn helper.

What remains unproven:

- Exact source virtual name.
- Why this virtual performs exactly three pickup-spawn passes.
- Concrete CUnit/profile/init/vtable layouts.
- Runtime pickup or transition behavior.
- BEA patching behavior.
- Rebuild parity.
