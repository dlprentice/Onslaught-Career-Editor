# Wave1209 PhysicsScript Round-Value Destructor Current-Risk Review

Status: complete static read-back evidence
Date: 2026-06-07
Scope: `wave1209-physics-roundvalue-destructor-current-risk-review`

Wave1209 saved comment/tag normalization for `4 PhysicsScript round-value destructor current-risk rows`: `CRoundSeek__scalar_deleting_dtor`, `CRoundSeek__dtor_base`, `CRoundTreeCollision__scalar_deleting_dtor`, and `CRoundTreeCollision__dtor_base`.

The correction is intentionally narrow. Fresh instruction/decompile evidence shows the scalar-deleting wrappers free through `CDXMemoryManager__Free(&DAT_009c3df0, this)` via call `0x00549220`, not OID__FreeObject. No rename, no signature change, no function-boundary change, and no executable-byte change occurred.

Read-back evidence:

- Pre/post target exports: `4` metadata rows, `4` tag rows, `4 xref rows`, `68 instruction rows`, and `4 decompile rows`.
- Context exports: `6` metadata rows, `6` tag rows, `43 xref rows`, `177 instruction rows`, and `6 decompile rows`.
- Dry run: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=34 missing=0 bad=0`.
- Apply: `updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=34 missing=0 bad=0`; `REPORT: Save succeeded`.
- Final dry: `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-044807_post_wave1209_physics_roundvalue_destructor_current_risk_review_verified`, `19` files, `176425863` bytes, `DiffCount=0`, `HashDiffCount=0`.

Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt. Active current-risk accounting is unique-address accounting at `1096/1179 = 92.96%`; current focused candidates: 1141; live regenerated current focused candidates: 1141; remaining active focused work: 83; current risk candidates: 6166; legacy additive counter is deprecated (`1127/1179`); 26 duplicate-address overcount; Wave1145 arithmetic overcount: 5; Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction. Active completion target: `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`.

What this proves:

- The four target rows exist in the saved Ghidra project with the expected names/signatures.
- The scalar-deleting wrapper comments now match the observed memory-manager free path.
- The rows carry `wave1209-physics-roundvalue-destructor-current-risk-review`, `wave1209-readback-verified`, `current-risk-review`, and lifecycle-specific tags.

What remains separate:

- Exact PhysicsScript round-value layouts.
- Exact source destructor identity.
- Runtime physics-script loading/application/lifetime behavior.
- Runtime projectile collision behavior.
- BEA patching behavior.
- Rebuild parity and no-noticeable-difference parity.

Probe token anchor: Wave1209; wave1209-physics-roundvalue-destructor-current-risk-review; 1096/1179 = 92.96%; 4 PhysicsScript round-value destructor current-risk rows; current focused candidates: 1141; live regenerated current focused candidates: 1141; remaining active focused work: 83; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=4 skipped=0; comment_only_updated=4; tags_added=34; final dry updated=0 skipped=4; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consults used; no Cursor/Composer; CDXMemoryManager__Free(&DAT_009c3df0, this); not OID__FreeObject; CRoundSeek__scalar_deleting_dtor; CRoundSeek__dtor_base; CRoundTreeCollision__scalar_deleting_dtor; CRoundTreeCollision__dtor_base; 0 / 0 / 0; 6411/6411 = 100.00%; 4 xref rows; 68 instruction rows; 4 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260607-044807_post_wave1209_physics_roundvalue_destructor_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification; static-reaudit-current-risk-ledger.json; static-reaudit-measurement-register.md.
