# Wave1185 AirUnit Init Current-Risk Review

Status: complete static current-risk comment/tag normalization; artifact commit `902934b6864f02c12546d58a8984f64f4ae425c1`
Date: 2026-06-06
Scope tag: `wave1185-airunit-init-current-risk-review`

Wave1185 accounts for `1 AirUnit init lifecycle current-risk row` from the `wave1108-current-risk-rank` current-risk denominator with fresh serialized Ghidra evidence:

- `0x00402ad0 CAirUnit__Init`

The saved Ghidra signature was already `void __thiscall CAirUnit__Init(void * this, void * init)`. This wave normalized the saved comment and tags only, so the row carries the current static contract and explicit no-runtime/no-rebuild boundary.

One Codex read-only consult was used and recommended the exact one-row slice. No Cursor/Composer was used.

Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `783/1179 = 66.41%`; current risk candidates: 6166; current focused candidates: 1177; live regenerated current focused candidates: 1177; remaining active focused work: 396; focused threshold `15`; not Wave911 reconstruction.

Fresh exports verified `1` metadata row, `1` tag row, `8 xref rows`, `165 instruction rows`, and `1` decompile row. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-134914_post_wave1185_airunit_init_current_risk_review_verified`.

## Reviewed Row

| Address | Name | Evidence |
| --- | --- | --- |
| `0x00402ad0` | `CAirUnit__Init` | Signature `void __thiscall CAirUnit__Init(void * this, void * init)`; call xrefs from `CCarrier__Init`, `CDropship__Init`, `CPlane__Init`, `CGroundAttackAircraft__Init`, and two no-function call sites; DATA vtable refs `0x005e3548` and `0x005e379c`; body delegates to `CUnit__Init`, reads init/profile config at `+0x3bc`, seeds speed/accel-like fields, builds `Trail` / `Engine` particle-node lists via strings `0x00622d14` / `0x00622cec` and `CSPtrSet` add paths, and links into the air-unit set. |

## Mutation Summary

The wave saved comment/tag normalization only: dry/apply/final-dry reported `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 tags_added=13 missing=0 bad=0`, then `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 tags_added=13 missing=0 bad=0`, then `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.

No rename, signature change, function-boundary change, executable-byte change, BEA launch, installed-game mutation, save mutation, or runtime-file mutation occurred.

## Boundary

This wave strengthens the AirUnit init static contract needed for rebuild-grade static contracts and a future clean-room implementation aiming at no noticeable difference from the original game. It does not prove concrete `CUnit`/`CAirUnit`/init/profile/particle-node layouts, exact source-body identity, runtime flight/effect behavior, BEA patching behavior, gameplay/visual outcomes, rebuild parity, or no-noticeable-difference parity.

Probe token anchor: Wave1185; wave1185-airunit-init-current-risk-review; 783/1179 = 66.41%; 1 AirUnit init lifecycle current-risk row; current focused candidates: 1177; live regenerated current focused candidates: 1177; remaining active focused work: 396; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=1 skipped=0; comment_only_updated=1; tags_added=13; final dry updated=0 skipped=1; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consult used; no Cursor/Composer; CAirUnit__Init; CUnit__Init; CCarrier__Init; CDropship__Init; CPlane__Init; CGroundAttackAircraft__Init; aircraft vtable DATA refs 0x005e3548/0x005e379c; Trail; Engine; 0x00622d14; 0x00622cec; 0 / 0 / 0; 6411/6411 = 100.00%; 8 xref rows; 165 instruction rows; 1 decompile row; [maintainer-local-ghidra-backup-root]\BEA_20260606-134914_post_wave1185_airunit_init_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.
