# Wave1184 AirUnit/Plane Residual Current-Risk Review

Status: complete static current-risk read-only review with pushed artifact/state closeout
Date: 2026-06-06
Scope tag: `wave1184-airunit-plane-residual-current-risk-review`

Wave1184 accounts for `3 AirUnit/Plane support-gate residual current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh serialized Ghidra evidence. The rows were already normalized by Wave1006, so this pass made no Ghidra mutation; its value is accounting closure and current read-back proof that these Wave1006 support-gate rows are not loose current-risk work.

Codex read-only consults were used before the final judgment. Both consults converged on the exact three-row AirUnit/Plane residual slice; Codex root rejected duplicate Wave1123 slot-69 rows and deferred `0x00402ad0 CAirUnit__Init` to a separate lifecycle/init residual pass. No Cursor/Composer was used.

Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `782/1179 = 66.33%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 397; focused threshold `15`; not Wave911 reconstruction.

Fresh exports verified `3` metadata rows, `3` tag rows, `20 xref rows`, `51 instruction rows`, and `3` decompile rows. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-131434_post_wave1184_airunit_plane_residual_current_risk_review_verified`.

## Reviewed Rows

| Address | Name | Evidence |
| --- | --- | --- |
| `0x00403730` | `CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport` | Wave1006 tags/comments remain; direct call xref from `0x004d20a3 CPlane__VFunc_68_CrashIfNoAirSupport`; DATA vtable xrefs `0x005e2148`, `0x005e0e9c`, `0x005e0540`, `0x005e3634`, and `0x005e3888`; body sets a state timestamp, then triggers crash/death when flag bit 4 is set and unit-data `+0x11c` is zero. |
| `0x00403a50` | `CAirUnit__VFunc_117_HasPositionDeltaWhileFlag4Clear` | Wave1006 tags/comments remain; DATA vtable xrefs `0x005e2ff4`, `0x005e2da0`, `0x005e220c`, `0x005e1b04`, `0x005e1410`, `0x005e0f60`, `0x005e0604`, `0x005e36f8`, and `0x005e394c`; call xref `0x0044814a`; body compares position components and returns true when any differs while flag bit 4 is clear. |
| `0x004d20a0` | `CPlane__VFunc_68_CrashIfNoAirSupport` | Wave1006 tags/comments remain; DATA vtable xrefs `0x005e2f30`, `0x005e2cdc`, `0x005e1a40`, and `0x005e134c`; body calls the CAirUnit slot-68 helper, then triggers crash/death when unit-data `+0x11c` is zero. |

## Mutation Summary

No mutation occurred. The wave made no rename, no signature change, no comment change, no tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation.

## Boundary

This wave strengthens the AirUnit/Plane static support-gate contract needed for rebuild-grade static contracts and a future clean-room implementation aiming at no noticeable difference from the original game. It does not prove runtime aircraft crash behavior, runtime support-gate behavior, runtime position-delta behavior, exact source virtual names, concrete `CUnit`/`CAirUnit`/`CPlane`/support-field/position/flag layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, rebuild parity, or no-noticeable-difference parity.

Probe token anchor: Wave1184; wave1184-airunit-plane-residual-current-risk-review; 782/1179 = 66.33%; 3 AirUnit/Plane support-gate residual current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 397; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; no rename; no signature change; no comment change; no tag change; no function-boundary change; no executable-byte change; Codex read-only consults used; both consults converged on exact three-row AirUnit/Plane residual slice; root rejected duplicate Wave1123 slot-69 rows; CAirUnit__Init deferred to separate lifecycle/init residual pass; no Cursor/Composer; Wave1006 provenance; air-unit support gate; plane-family slot 68; shared slot 117 predicate; 0 / 0 / 0; 6411/6411 = 100.00%; 20 xref rows; 51 instruction rows; 3 decompile rows; 0x00403730 CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport; 0x00403a50 CAirUnit__VFunc_117_HasPositionDeltaWhileFlag4Clear; 0x004d20a0 CPlane__VFunc_68_CrashIfNoAirSupport; [maintainer-local-ghidra-backup-root]\BEA_20260606-131434_post_wave1184_airunit_plane_residual_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.
