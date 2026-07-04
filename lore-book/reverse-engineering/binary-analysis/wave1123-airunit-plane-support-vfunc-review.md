# Wave1123 AirUnit/Plane Support-Vfunc Review

Status: validated static read-only evidence
Date: 2026-06-05
Tag: `wave1123-airunit-plane-support-vfunc-review`

Wave1123 accounts for `2 rows` from the Wave1108 current focused denominator as a score-23 aircraft support-mode vfunc cluster, moving current focused accounting to `131/1179 = 11.11%` of current focused candidates: 1179. Static closure debt remains `0 / 0 / 0` for commentless / exact-undefined / `param_N`.

This is a fresh read-only Ghidra export of the Wave1006 aircraft crash/support virtual helper evidence; no mutation was needed: no rename, no signature change, no function-boundary change, and no executable-byte change.

Reviewed anchors:

| Address | Static read-back evidence |
| --- | --- |
| `0x00403760 CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes` | CAirUnit-family vtable slot 69 helper. The body calls `CUnit__ResetFieldD0ToGlobalThreshold`, checks flag bit 4, then checks unit-data `+0x11c/+0x124` before the drop/spawn plus vfunc `+0x38` crash/death path. It has a direct call xref from `0x0047bf60 CPlane__VFunc_69_CrashIfNoSupportModes` at `0x0047bf63` plus DATA vtable xrefs. |
| `0x0047bf60 CPlane__VFunc_69_CrashIfNoSupportModes` | Plane-family vtable slot 69 override. The body calls `CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes`, then checks unit-data `+0x11c/+0x124` before the same drop/spawn plus vfunc `+0x38` crash/death path. DATA vtable xrefs include `0x005e2f34`, `0x005e2ce0`, `0x005e1a44`, and `0x005e1350`. |

Evidence:

- Fresh metadata/tag/xref/instruction/decompile exports: `2` / `2` / `10` / `36` / `2`.
- Existing tags remain anchored to `air-unit-crash-support-vfunc-review-wave1006`, `support-gate`, `vtable-slot-69`, and `static-reaudit`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-052636_post_wave1123_airunit_plane_support_vfunc_review_verified`, `19` files, `175737735` bytes, `DiffCount=0`.
- Previous latest completed Ghidra review backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-043957_post_wave1122_hlcollisiondetector_current_risk_review_verified`.
- Prior context: Wave1006 normalized the saved comments/tags for the air-unit crash/support virtual helpers and plane-family overrides.

Boundary:

This is static Ghidra/source-reference evidence. It does not prove runtime aircraft crash behavior, runtime flight/support-mode behavior, exact source virtual names, concrete `CUnit`/`CAirUnit`/`CPlane`/support-field/position/flag layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, or rebuild parity.
