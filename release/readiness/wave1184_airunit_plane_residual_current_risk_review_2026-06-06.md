# Wave1184 AirUnit/Plane Residual Current-Risk Readiness Note

Status: complete static current-risk read-only review with pushed artifact/state closeout
Date: 2026-06-06
Scope: `wave1184-airunit-plane-residual-current-risk-review`

Wave1184 reviewed `3 AirUnit/Plane support-gate residual current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh serialized Ghidra exports. It is a read-only review of the Wave1006-normalized air-unit support/crash helpers and shared position-delta predicate:

- `0x00403730 CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport`
- `0x00403a50 CAirUnit__VFunc_117_HasPositionDeltaWhileFlag4Clear`
- `0x004d20a0 CPlane__VFunc_68_CrashIfNoAirSupport`

Evidence:

- Fresh exports: `3` metadata rows, `3` tag rows, `20 xref rows`, `51 instruction rows`, and `3` decompile rows.
- Logs: metadata `targets=3 found=3 missing=0`, tags `rows=3 missing=0`, xrefs `Wrote 20 rows`, instructions `Wrote 51 function-body instruction rows`, and decompile `targets=3 dumped=3 missing=0 failed=0`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-131434_post_wave1184_airunit_plane_residual_current_risk_review_verified`, `19` files, `176098183` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Accounting: `782/1179 = 66.33%`, current focused candidates: 1178, live regenerated current focused candidates: 1178, remaining active focused work: 397, current risk candidates: 6166.

Codex read-only consults were used. Both consults converged on the exact three-row AirUnit/Plane residual slice; Codex root rejected duplicate Wave1123 slot-69 rows and deferred `0x00402ad0 CAirUnit__Init` to a separate lifecycle/init residual pass. No Cursor/Composer was used.

Mutation boundary:

- No mutation.
- No rename.
- No signature change.
- No comment change.
- No tag change.
- No function-boundary change.
- No executable-byte change.
- No BEA launch, installed-game mutation, save mutation, or runtime-file mutation.

Static clean-room target: rebuild-grade static contracts for a future clean-room implementation aiming at no noticeable difference.

Not proven here: runtime aircraft crash behavior, runtime support-gate behavior, runtime position-delta behavior, exact source virtual names, concrete `CUnit`/`CAirUnit`/`CPlane`/support-field/position/flag layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, rebuild parity, or no-noticeable-difference parity.

Probe token anchor: Wave1184; wave1184-airunit-plane-residual-current-risk-review; 782/1179 = 66.33%; 3 AirUnit/Plane support-gate residual current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 397; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; no rename; no signature change; no comment change; no tag change; no function-boundary change; no executable-byte change; Codex read-only consults used; both consults converged on exact three-row AirUnit/Plane residual slice; root rejected duplicate Wave1123 slot-69 rows; CAirUnit__Init deferred to separate lifecycle/init residual pass; no Cursor/Composer; Wave1006 provenance; air-unit support gate; plane-family slot 68; shared slot 117 predicate; 0 / 0 / 0; 6411/6411 = 100.00%; 20 xref rows; 51 instruction rows; 3 decompile rows; 0x00403730 CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport; 0x00403a50 CAirUnit__VFunc_117_HasPositionDeltaWhileFlag4Clear; 0x004d20a0 CPlane__VFunc_68_CrashIfNoAirSupport; [maintainer-local-ghidra-backup-root]\BEA_20260606-131434_post_wave1184_airunit_plane_residual_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.
