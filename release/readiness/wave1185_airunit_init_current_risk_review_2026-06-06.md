# Wave1185 AirUnit Init Current-Risk Readiness Note

Status: complete static current-risk comment/tag normalization; artifact commit `902934b6864f02c12546d58a8984f64f4ae425c1`
Date: 2026-06-06
Scope: `wave1185-airunit-init-current-risk-review`

Wave1185 accounts for `1 AirUnit init lifecycle current-risk row` from the `wave1108-current-risk-rank` current-risk denominator:

- `0x00402ad0 CAirUnit__Init`

The saved Ghidra signature was already `void __thiscall CAirUnit__Init(void * this, void * init)`. The pass normalized the saved comment and tags only; it made no rename, no signature change, no function-boundary change, and no executable-byte change.

Evidence:

- Ghidra dry/apply/final-dry: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 tags_added=13 missing=0 bad=0`, then `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 tags_added=13 missing=0 bad=0`, then `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Fresh exports after apply: `1` metadata row, `1` tag row, `8 xref rows`, `165 instruction rows`, and `1` decompile row.
- Queue refresh after apply: `6411` total functions, `6411` commented, `0` commentless, `0` exact-undefined signatures, `0` `param_N` signatures.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-134914_post_wave1185_airunit_init_current_risk_review_verified`, `19` files, `176098183` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Accounting: `783/1179 = 66.41%`, current focused candidates: 1177, live regenerated current focused candidates: 1177, remaining active focused work: 396, current risk candidates: 6166.

Static contract:

`CAirUnit__Init` is reached from `CCarrier__Init`, `CDropship__Init`, `CPlane__Init`, `CGroundAttackAircraft__Init`, and aircraft vtable DATA refs `0x005e3548` / `0x005e379c`. It delegates to `CUnit__Init`, reads init/profile config at `+0x3bc`, seeds speed/accel-like fields, builds `Trail` / `Engine` particle-node lists via strings `0x00622d14` / `0x00622cec` and `CSPtrSet` add paths, and links into the air-unit set.

One Codex read-only consult was used and recommended the exact one-row slice. No Cursor/Composer was used.

Mutation boundary:

- Comment/tag normalization only.
- No rename.
- No signature change.
- No function-boundary change.
- No executable-byte change.
- No BEA launch, installed-game mutation, save mutation, or runtime-file mutation.

Static clean-room target: rebuild-grade static contracts for a future clean-room implementation aiming at no noticeable difference.

Not proven here: concrete `CUnit`/`CAirUnit`/init/profile/particle-node layouts, exact source-body identity, runtime flight/effect behavior, BEA patching behavior, gameplay/visual outcomes, rebuild parity, or no-noticeable-difference parity.

Probe token anchor: Wave1185; wave1185-airunit-init-current-risk-review; 783/1179 = 66.41%; 1 AirUnit init lifecycle current-risk row; current focused candidates: 1177; live regenerated current focused candidates: 1177; remaining active focused work: 396; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=1 skipped=0; comment_only_updated=1; tags_added=13; final dry updated=0 skipped=1; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consult used; no Cursor/Composer; CAirUnit__Init; CUnit__Init; CCarrier__Init; CDropship__Init; CPlane__Init; CGroundAttackAircraft__Init; aircraft vtable DATA refs 0x005e3548/0x005e379c; Trail; Engine; 0x00622d14; 0x00622cec; 0 / 0 / 0; 6411/6411 = 100.00%; 8 xref rows; 165 instruction rows; 1 decompile row; [maintainer-local-ghidra-backup-root]\BEA_20260606-134914_post_wave1185_airunit_init_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.
