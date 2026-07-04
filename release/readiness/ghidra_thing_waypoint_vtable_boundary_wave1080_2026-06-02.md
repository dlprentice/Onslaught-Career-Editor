# Ghidra Thing/Waypoint Vtable Boundary Wave1080 Readiness Note

Status: complete static mutation/read-back evidence
Date: 2026-06-02
Scope: `thing-waypoint-vtable-boundary-wave1080`

Wave1080 recovered and saved fourteen previously unresolved CThing-family/CWaypoint vtable-boundary functions in the loaded Steam retail Ghidra database. The pass focused on true vtable starts for CThing `0x005df550`, CWaypoint `0x005dd278`, and CInfantryAI `0x005dbf14` after Wave1079 showed that adjacent CTGALoader/CImageLoader/TerrainGuide rows had table-boundary artifacts.

Recovered targets:

| Address | Saved name | Evidence summary |
| --- | --- | --- |
| `0x004013f0` | `SharedVFunc__ReturnColorFF000080_004013f0` | Shared CThing-family/CInfantryAI constant-return body; returns `0xff000080`. |
| `0x00401400` | `SharedVFunc__ForwardField28Slot18OrFallbackFloat_00401400` | Loads `this+0x28`, forwards through pointee vtable slot `+0x18` when non-null, otherwise returns fallback float `0x005d8568`. |
| `0x004014d0` | `SharedVFunc__ReturnField64Offset10OrMinusOne_004014d0` | Returns `*(this+0x64+0x10)` when present, else `-1`. |
| `0x004014f0` | `SharedVFunc__ReturnField68_004014f0` | Returns pointer/value at `this+0x68`. |
| `0x00401500` | `SharedVFunc__ReturnField64Offset14OrZero_00401500` | Returns `*(this+0x64+0x14)` when present, else `0`. |
| `0x004040a0` | `SharedVFunc__CopyVector14ToOut_004040a0` | Copies four dwords from `this+0x14` into caller output buffer and returns with `RET 0x4`. |
| `0x004040d0` | `SharedVFunc__CopyBlock34ToOut_004040d0` | Copies `0x30` bytes from `this+0x34` into caller output buffer and returns with `RET 0x4`. |
| `0x00405910` | `SharedVFunc__ReturnMinusOne_00405910` | Shared constant-return stub returning `-1`. |
| `0x00405920` | `SharedVFunc__ReturnOneRet4_00405920` | Shared constant-return stub returning `1` and consuming one stack argument. |
| `0x004bfb50` | `CWaypoint__GetClassNameString_004bfb50` | CWaypoint vtable `0x005dd278` slot `37` constant-string getter; string read-back at `0x00630c58` is `CWaypoint`. |
| `0x004bfb60` | `CWaypoint__SetThingTypeMask1001_004bfb60` | CWaypoint vtable `0x005dd278` slot `68` type-mask setter; ORs stack argument with `0x1001`, stores `this+0x34`, and returns with `RET 0x4`. |
| `0x004f3460` | `CThing__GetClassNameString_004f3460` | CThing vtable `0x005df550` slot `37` constant-string getter; string read-back at `0x00633174` is `CThing`. |
| `0x004f3470` | `CThing__SetThingTypeMaskOr1_004f3470` | CThing vtable `0x005df550` slot `68` type-mask setter; ORs the low byte of the stack argument with `1`, stores `this+0x34`, and returns with `RET 0x4`. |
| `0x0052db60` | `CWaypoint__GetTypeId12_0052db60` | CWaypoint vtable `0x005dd278` slot `38` type-id getter; returns `0x12` and stops before adjacent `0x0052db70`. |

Read-back evidence:

- Pre exports verified `60` adjacent vtable-slot rows, `3` metadata rows, `3` tag rows, `178` xref rows, `3` instruction rows, and `3` decompile index rows for the initial false-boundary targets.
- True-vtable/context exports verified `240` true vtable-slot rows, `31` missing code-candidate metadata rows, `979` code-candidate xref rows, `3379` around-instruction rows, and `2232` vtable/type-candidate rows.
- String evidence verified `0x00633174 = CThing`, `0x00630c58 = CWaypoint`, and `0x00622c60 = CActor`.
- `ApplyThingWaypointVtableBoundaryWave1080.java` dry/apply/final dry reported `updated=0 skipped=0 created=0 would_create=14 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`, then `updated=14 skipped=0 created=14 would_create=0 renamed=0 would_rename=0 signature_updated=14 comment_only_updated=0 missing=0 bad=0`, then `updated=0 skipped=14 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post exports verified `14` metadata rows, `14` tag rows, `584` xref rows, `67` function-body instruction rows, `14` decompile rows, and `240` post true-vtable-slot rows.
- Post true-vtable export shows `32` slot occurrences across the recovered targets now resolve with `OK`; `40` unresolved/non-function slots remain deliberately deferred, including larger CInfantryAI-style bodies, CThing-family residuals, and obvious float/data payload slots.
- Queue closure after Wave1080 is `6276/6276 = 100.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; expanded static re-audit surface advances to `1387/1560 = 88.91%`; top-500 coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-095224_post_wave1080_thing_waypoint_vtable_boundary_verified`, 19 files, 174787463 bytes, `DiffCount=0`.

What this proves:

- The fourteen target function rows exist in the saved Ghidra project.
- The saved signatures, names, comments, and tags read back from the loaded retail database.
- The true CThing/CWaypoint/CInfantryAI vtable rows now resolve the recovered small helper slots instead of reporting `NO_FUNCTION_AT_POINTER`.
- The observed bodies are static retail Ghidra evidence tied to vtable slots, DATA xrefs, listing state, instruction exports, decompile exports, and string read-back.

What remains separate proof:

- Exact source virtual names.
- Concrete CThing/CWaypoint/CInfantryAI layout semantics.
- Meaning of the type-mask bits and type-id enum beyond observed constants.
- Runtime object/class-name/type-mask/vector-copy behavior.
- The deferred `40` unresolved/non-function true-vtable slots.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Probe token anchor: Wave1080; thing-waypoint-vtable-boundary-wave1080; 0x004013f0 SharedVFunc__ReturnColorFF000080_004013f0; 0x00401400 SharedVFunc__ForwardField28Slot18OrFallbackFloat_00401400; 0x004040a0 SharedVFunc__CopyVector14ToOut_004040a0; 0x004bfb50 CWaypoint__GetClassNameString_004bfb50; 0x004f3460 CThing__GetClassNameString_004f3460; 0x0052db60 CWaypoint__GetTypeId12_0052db60; 0x005df550; 0x005dd278; 0x005dbf14; 812/1408 = 57.67%; 1387/1560 = 88.91%; 500/500 = 100.00%; 6276/6276 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260602-095224_post_wave1080_thing_waypoint_vtable_boundary_verified; boundary recovery.
