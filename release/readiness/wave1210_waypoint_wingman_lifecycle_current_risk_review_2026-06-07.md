# Wave1210 Waypoint/Wingman Lifecycle Current-Risk Review

Status: complete static read-back evidence; later validation passed by current-risk closeout gates
Date: 2026-06-07
Scope: `wave1210-waypoint-wingman-lifecycle-current-risk-review`

Wave1210 saved comment/tag normalization for `6 Waypoint/Wingman lifecycle current-risk rows`: `CWaypoint__scalar_deleting_dtor`, `CWingmanStart__scalar_deleting_dtor`, `CWaypoint__dtor_base`, `CWingmanStart__dtor_base`, `CWaypoint__Load`, and `CWaypointPath__scalar_deleting_dtor`.

The correction is intentionally narrow. Fresh instruction/decompile evidence shows `CWaypoint__dtor_base` delegates to `CThing__dtor_base`, correcting stale `CThing__ctor_like_004f3640` wording, and the scalar-deleting wrappers call the matching destructor bodies before optional `CDXMemoryManager__Free(&DAT_009c3df0, this)`. No rename, no signature change, no function-boundary change, and no executable-byte change occurred. Codex read-only consult used; no Cursor/Composer.

Read-back evidence:

- Pre/post target exports: `6` metadata rows, `6` tag rows, `6 xref rows`, `630 instruction rows`, and `6 decompile rows`.
- Context exports: `8` metadata rows, `8` tag rows, `11` xref rows, `968` instruction rows, and `8` decompile rows.
- Pre/post metadata confirms six changed target comments; the final script apply only removed the accidental `destructor` tag from `CWaypoint__Load`.
- Apply/final proof: `tags_removed=1`; `final dry updated=0 skipped=6`.
- Verified backup: `G:\GhidraBackups\BEA_20260607-053028_post_wave1210_waypoint_wingman_lifecycle_current_risk_review_verified`, `19` files, `176425863` bytes, `DiffCount=0`, `HashDiffCount=0`.

Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt. Active current-risk accounting is unique-address accounting at `1102/1179 = 93.47%`; current focused candidates: 1127; live regenerated current focused candidates: 1127; remaining active focused work: 77; current risk candidates: 6166; legacy additive counter is deprecated (`1133/1179`); 26 duplicate-address overcount; Wave1145 arithmetic overcount: 5; Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction. Active completion target: `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`. Measurement paths: `static-reaudit-current-risk-ledger.json`, `static-reaudit-measurement-register.md`, and `wave1108-current-risk-rank`.

What this proves:

- The six target rows exist in the saved Ghidra project with expected names/signatures.
- The saved comments/tags align the wrapper/body/list-cleanup contracts with observed xrefs, instructions, and decompile output.
- `CWaypoint__Load` is not classified as a destructor after the final tag cleanup.

What remains separate:

- Runtime waypoint behavior.
- Runtime wingman-start behavior.
- Exact CWaypoint/CWingmanStart/CWaypointPath layouts.
- Exact source identity.
- BEA patching behavior.
- Rebuild parity and no-noticeable-difference parity.

Probe token anchor: Wave1210; wave1210-waypoint-wingman-lifecycle-current-risk-review; 1102/1179 = 93.47%; 6 Waypoint/Wingman lifecycle current-risk rows; CWaypoint__scalar_deleting_dtor; CWingmanStart__scalar_deleting_dtor; CWaypoint__dtor_base; CWingmanStart__dtor_base; CWaypoint__Load; CWaypointPath__scalar_deleting_dtor; 6411/6411 = 100.00%; 0 / 0 / 0; 6 xref rows; 630 instruction rows; 6 decompile rows; current focused candidates: 1127; live regenerated current focused candidates: 1127; remaining active focused work: 77; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; CThing__dtor_base; stale CThing__ctor_like_004f3640; tags_removed=1; final dry updated=0 skipped=6; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consult used; no Cursor/Composer; CDXMemoryManager__Free(&DAT_009c3df0, this); CSPtrSet__Remove; legacy additive counter is deprecated (`1133/1179`); 26 duplicate-address overcount; Wave1145 arithmetic overcount: 5; Wave911 is historical-retired/non-reconstructable at 812/1408 = 57.67%; 1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence; static-reaudit-current-risk-ledger.json; static-reaudit-measurement-register.md; continuity denominator; G:\GhidraBackups\BEA_20260607-053028_post_wave1210_waypoint_wingman_lifecycle_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.
