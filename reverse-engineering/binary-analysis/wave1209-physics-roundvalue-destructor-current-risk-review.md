# Wave1209 PhysicsScript Round-Value Destructor Current-Risk Review

Status: complete static read-back evidence
Date: 2026-06-07
Tag: `wave1209-physics-roundvalue-destructor-current-risk-review`

Wave1209 accounts for `4 PhysicsScript round-value destructor current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator. It re-read the CRoundSeek and CRoundTreeCollision scalar-deleting destructor wrappers and destructor bodies with fresh Ghidra metadata, tag, xref, instruction, and decompile exports.

The pass saved comment/tag normalization only. It corrected the two scalar-deleting wrapper comments from stale `OID__FreeObject` wording to the observed `CDXMemoryManager__Free(&DAT_009c3df0, this)` path through call `0x00549220`. No rename, no signature change, no function-boundary change, and no executable-byte change occurred.

Representative anchors:

| Address | Function | Static contract |
| --- | --- | --- |
| `0x004395b0` | `CRoundSeek__scalar_deleting_dtor` | Calls `CRoundSeek__dtor_base`, tests the scalar-delete flag, and frees through `CDXMemoryManager__Free(&DAT_009c3df0, this)` via `0x00549220` when bit 0 is set. DATA vtable ref `0x005da534`. |
| `0x004395d0` | `CRoundSeek__dtor_base` | Installs CRoundSeek vtable `0x005da534`, destroys owned child value at `this+0x8` through child vtable slot 0 with flag 1 when non-null, restores CPhysicsRoundValue base vtable `0x005da584`, and unwinds the SEH frame. |
| `0x00439ad0` | `CRoundTreeCollision__scalar_deleting_dtor` | Calls `CRoundTreeCollision__dtor_base`, tests the scalar-delete flag, and frees through `CDXMemoryManager__Free(&DAT_009c3df0, this)` via `0x00549220` when bit 0 is set. DATA vtable ref `0x005da2dc`. |
| `0x00439af0` | `CRoundTreeCollision__dtor_base` | Installs CRoundTreeCollision vtable `0x005da2dc`, destroys owned child value at `this+0x8` through child vtable slot 0 with flag 1 when non-null, restores CPhysicsRoundValue base vtable `0x005da584`, and unwinds the SEH frame. |

Read-back evidence:

| Item | Result |
| --- | --- |
| Target pre/post exports | `4` metadata rows, `4` tag rows, `4 xref rows`, `68 instruction rows`, and `4 decompile rows` |
| Context exports | `6` metadata rows, `6` tag rows, `43 xref rows`, `177 instruction rows`, and `6 decompile rows` for base round-value lifecycle and apply/load siblings |
| Dry run | `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=34 missing=0 bad=0` |
| Apply | `updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=34 missing=0 bad=0`; `REPORT: Save succeeded` |
| Final dry | `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0` |
| Backup | `G:\GhidraBackups\BEA_20260607-044807_post_wave1209_physics_roundvalue_destructor_current_risk_review_verified` |

Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` commentless/exact-undefined/`param_N` debt. Active current-risk accounting is `1096/1179 = 92.96%`; current focused candidates: 1141; live regenerated current focused candidates: 1141; remaining active focused work: 83; current risk candidates: 6166; legacy additive counter is deprecated (`1127/1179`); 26 duplicate-address overcount; Wave1145 arithmetic overcount: 5; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction.

Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference. Exact PhysicsScript round-value layouts, exact source destructor identity, runtime physics-script loading/application/lifetime behavior, runtime projectile collision behavior, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Probe token anchor: Wave1209; wave1209-physics-roundvalue-destructor-current-risk-review; 1096/1179 = 92.96%; 4 PhysicsScript round-value destructor current-risk rows; current focused candidates: 1141; live regenerated current focused candidates: 1141; remaining active focused work: 83; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=4 skipped=0; comment_only_updated=4; tags_added=34; final dry updated=0 skipped=4; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consults used; no Cursor/Composer; CDXMemoryManager__Free(&DAT_009c3df0, this); not OID__FreeObject; CRoundSeek__scalar_deleting_dtor; CRoundSeek__dtor_base; CRoundTreeCollision__scalar_deleting_dtor; CRoundTreeCollision__dtor_base; 0 / 0 / 0; 6411/6411 = 100.00%; 4 xref rows; 68 instruction rows; 4 decompile rows; G:\GhidraBackups\BEA_20260607-044807_post_wave1209_physics_roundvalue_destructor_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification; static-reaudit-current-risk-ledger.json; static-reaudit-measurement-register.md.
