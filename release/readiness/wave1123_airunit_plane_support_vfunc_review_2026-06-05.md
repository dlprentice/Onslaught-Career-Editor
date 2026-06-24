# Wave1123 AirUnit/Plane Support-Vfunc Review Readiness Note

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1123-airunit-plane-support-vfunc-review`

Wave1123 re-read `2 rows` from the next Wave1108 current focused candidates: 1179, as a score-23 aircraft support-mode vfunc cluster. Current focused accounting moves to `131/1179 = 11.11%`; static closure debt remains `0 / 0 / 0` for commentless / exact-undefined / `param_N`.

Representative anchors: `0x00403760 CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes` and `0x0047bf60 CPlane__VFunc_69_CrashIfNoSupportModes`.

Mutation status:

- Fresh read-only Ghidra export only.
- No mutation.
- No rename.
- No signature change.
- No function-boundary change.
- No executable-byte change.

Evidence:

- Metadata/tag/xref/instruction/decompile exports: `2` / `2` / `10` / `36` / `2`.
- Probe anchor wording: fresh read-only Ghidra export; no mutation.
- Backup: `G:\GhidraBackups\BEA_20260605-052636_post_wave1123_airunit_plane_support_vfunc_review_verified`, `19` files, `175737735` bytes, `DiffCount=0`.
- Previous latest completed Ghidra review backup: `G:\GhidraBackups\BEA_20260605-043957_post_wave1122_hlcollisiondetector_current_risk_review_verified`.
- Prior context: Wave1006 normalized the aircraft and plane-family crash/support vtable-slot evidence.

What this proves:

- The two target rows still exist in the saved Ghidra project.
- Names, signatures, comments, tags, xrefs, instruction windows, and decompile rows remain coherent with the saved static Wave1006 evidence.
- The current-risk accounting advances from `129/1179 = 10.94%` to `131/1179 = 11.11%`.

What remains separate:

- Runtime aircraft crash behavior.
- Runtime flight/support-mode behavior.
- Exact source virtual names.
- Concrete `CUnit`/`CAirUnit`/`CPlane`/support-field/position/flag layouts.
- Exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Visual QA.
- Rebuild parity.
