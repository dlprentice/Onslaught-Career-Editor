# Wave1210 Waypoint/Wingman Lifecycle Current-Risk Review

Status: complete static read-back evidence; later validation passed by current-risk closeout gates
Date: 2026-06-07
Tag: `wave1210-waypoint-wingman-lifecycle-current-risk-review`

Wave1210 accounts for `6 Waypoint/Wingman lifecycle current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator. It re-read the CWaypoint/CWingmanStart scalar-deleting destructor wrappers, destructor bodies, `CWaypoint__Load`, and the CWaypointPath scalar-deleting destructor wrapper with fresh Ghidra metadata, tag, xref, instruction, and decompile exports.

The pass saved comment/tag normalization only. The pre/post metadata diff proves six comment changes. The follow-up apply corrected one accidental loader tag, so the durable final logs show `tags_removed=1` and `final dry updated=0 skipped=6`. No rename, no signature change, no function-boundary change, and no executable-byte change occurred. Codex read-only consult used; no Cursor/Composer.

Representative anchors:

| Address | Function | Static contract |
| --- | --- | --- |
| `0x004bfd60` | `CWaypoint__scalar_deleting_dtor` | DATA vtable ref `0x005dd2f4`; calls `CWaypoint__dtor_base`, tests `flags & 1`, optionally frees through `CDXMemoryManager__Free(&DAT_009c3df0, this)`, returns `this`, and ends with `RET 0x4`. |
| `0x004bfdc0` | `CWingmanStart__scalar_deleting_dtor` | DATA vtable ref `0x005dcb5c`; calls `CWingmanStart__dtor_base`, tests `flags & 1`, optionally frees through `CDXMemoryManager__Free(&DAT_009c3df0, this)`, returns `this`, and ends with `RET 0x4`. |
| `0x004bfe70` | `CWaypoint__dtor_base` | Called from `0x004bfd63`; removes populated `this+0x3c` owner/list link through `CSPtrSet__Remove`, then delegates to `CThing__dtor_base`. This corrects stale `CThing__ctor_like_004f3640` wording. |
| `0x004bffa0` | `CWingmanStart__dtor_base` | Called from `0x004bfdc3`; removes populated `this+0x7c` owner/list link through `CSPtrSet__Remove`, then delegates to `CComplexThing__dtor_base`. |
| `0x00505960` | `CWaypoint__Load` | Called by `CWaypointManager__LoadWaypoints` at `0x00505b64`; `RET 0x0c` confirms `mem_buffer`, `load_mode`, and `object_table` stack arguments; reads WaypointManager.cpp line `0x1a` name/list evidence. |
| `0x00505bb0` | `CWaypointPath__scalar_deleting_dtor` | DATA table ref `0x005dfc8c`; calls `CWaypointPath__dtor_base`, checks `flags & 1`, frees through `CDXMemoryManager__Free(&DAT_009c3df0, this)` when requested, returns `this`, and ends with `RET 0x4`. |

Read-back evidence:

| Item | Result |
| --- | --- |
| Target pre/post exports | `6` metadata rows, `6` tag rows, `6 xref rows`, `630 instruction rows`, and `6 decompile rows` |
| Context exports | `8` metadata rows, `8` tag rows, `11` xref rows, `968` instruction rows, and `8` decompile rows |
| Dry/apply/final proof | Final script dry/apply/final-dry reported `tags_removed=1`, then `final dry updated=0 skipped=6`; pre/post metadata confirms all six target comments changed and final tags keep `CWaypoint__Load` out of the `destructor` bucket |
| Backup | `G:\GhidraBackups\BEA_20260607-053028_post_wave1210_waypoint_wingman_lifecycle_current_risk_review_verified`, `19` files, `176425863` bytes, `DiffCount=0`, `HashDiffCount=0` |

Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` commentless/exact-undefined/`param_N` debt. Active current-risk accounting is `1102/1179 = 93.47%`; current focused candidates: 1127; live regenerated current focused candidates: 1127; remaining active focused work: 77; current risk candidates: 6166; legacy additive counter is deprecated (`1133/1179`); 26 duplicate-address overcount; Wave1145 arithmetic overcount: 5; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`. Active measurement files: `static-reaudit-current-risk-ledger.json`, `static-reaudit-measurement-register.md`, and `wave1108-current-risk-rank`.

Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference. Runtime waypoint behavior, runtime wingman-start behavior, runtime waypoint-path teardown behavior, exact CWaypoint/CWingmanStart/CWaypointPath layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Probe token anchor: Wave1210; wave1210-waypoint-wingman-lifecycle-current-risk-review; 1102/1179 = 93.47%; 6 Waypoint/Wingman lifecycle current-risk rows; CWaypoint__scalar_deleting_dtor; CWingmanStart__scalar_deleting_dtor; CWaypoint__dtor_base; CWingmanStart__dtor_base; CWaypoint__Load; CWaypointPath__scalar_deleting_dtor; 6411/6411 = 100.00%; 0 / 0 / 0; 6 xref rows; 630 instruction rows; 6 decompile rows; current focused candidates: 1127; live regenerated current focused candidates: 1127; remaining active focused work: 77; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; CThing__dtor_base; stale CThing__ctor_like_004f3640; tags_removed=1; final dry updated=0 skipped=6; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consult used; no Cursor/Composer; CDXMemoryManager__Free(&DAT_009c3df0, this); CSPtrSet__Remove; legacy additive counter is deprecated (`1133/1179`); 26 duplicate-address overcount; Wave1145 arithmetic overcount: 5; Wave911 is historical-retired/non-reconstructable at 812/1408 = 57.67%; 1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence; static-reaudit-current-risk-ledger.json; static-reaudit-measurement-register.md; continuity denominator; G:\GhidraBackups\BEA_20260607-053028_post_wave1210_waypoint_wingman_lifecycle_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.
