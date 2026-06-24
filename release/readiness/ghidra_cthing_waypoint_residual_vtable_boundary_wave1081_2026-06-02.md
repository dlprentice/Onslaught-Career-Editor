# Ghidra CThing/Waypoint Residual Vtable Boundary Wave1081 Readiness Note

Status: complete static read-back evidence
Date: 2026-06-02
Scope: `cthing-waypoint-residual-vtable-boundary-wave1081`

Wave1081 recovered and saved seven previously unresolved CThing/CWaypoint residual true-vtable function boundaries. The pass created function objects, names, signatures, comments, and tags for the raw table targets, made no executable-byte changes, and did not launch BEA.

Recovered rows:

| Address | Saved name | Evidence |
| --- | --- | --- |
| `0x004bfa00` | `SharedVFunc__CopyGlobal829dd0Block30ToOut_004bfa00` | CThing vtable `0x005df550` slot `1` and CWaypoint vtable `0x005dd278` slot `1`; copies `0x30` bytes from global block `0x00829dd0` to caller output and returns with `RET 0x4`. |
| `0x004bfa20` | `SharedVFunc__CopyGlobal829dd0Block30ToOut_004bfa20` | CThing/CWaypoint slot `34`; same `0x00829dd0` `0x30`-byte output-copy pattern adjacent to the render-position/orientation virtual area. |
| `0x004bfa40` | `SharedVFunc__CopyGlobal829dd0Block30ToOut_004bfa40` | CThing/CWaypoint slot `61`; same `0x00829dd0` `0x30`-byte output-copy pattern before `OID__InitTargetData`. |
| `0x004f3760` | `CThing__AddShutdownEvent_004f3760` | CThing/CWaypoint slot `44`; tests and sets `this+0x2c` bit `0x1`, then calls event helper `0x0044b370` with event id `0x7d0`, matching the Stuart-source `CThing::AddShutdownEvent` shape. |
| `0x004f37a0` | `CThing__StartDieProcess_004f37a0` | CThing/CWaypoint slot `80`; tests and sets `this+0x2c` bit `0x4`, dispatches same-object vtable slot `+0x38`, returns first-transition boolean, matching the Stuart-source `CThing::StartDieProcess` shape. |
| `0x004f3d20` | `SharedVFunc__ForwardField28Slot10OrNull_004f3d20` | CThing/CWaypoint slot `21` and CInfantryAI vtable `0x005dbf14` slot `70`; forwards through `this+0x28` vtable slot `+0x10` when present, otherwise returns null. |
| `0x0043e9c0` | `SharedVFunc__CopyGlobal0066ea10Block10ToOut_0043e9c0` | CThing/CWaypoint slot `57`; copies four dwords from global block `0x0066ea10..0x0066ea1c` to caller output and stops before `CThing__GetRenderPos`. |

Read-back evidence:

- Pre-state exports showed `7` missing metadata rows, `7` missing tag rows, `7` missing decompile rows, `95` DATA xref rows, `399` around-instruction rows, and `288` vtable-slot rows. Pre vtable status was `244` `OK` and `44` `NO_FUNCTION_AT_POINTER`.
- `ApplyCThingWaypointResidualVtableBoundaryWave1081.java dry`: `updated=0 skipped=0 created=0 would_create=7 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0`.
- `ApplyCThingWaypointResidualVtableBoundaryWave1081.java apply`: `updated=7 skipped=0 created=7 would_create=0 renamed=0 would_rename=0 signature_updated=7 comment_only_updated=0 bad=0`.
- `ApplyCThingWaypointResidualVtableBoundaryWave1081.java final dry`: `updated=0 skipped=7 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0`.
- Post exports verified `7` metadata rows, `7` tag rows, `95` xref rows, `77` function-body instruction rows, `7` decompile rows, and `288` vtable-slot rows. Post vtable status is `259` `OK` and `29` `NO_FUNCTION_AT_POINTER`, resolving `15` additional slot occurrences across CThing, CWaypoint, and CInfantryAI.
- Queue after Wave1081: `6283/6283 = 100.00%`, with `0` commentless functions, `0` exact-undefined signatures, `0` `param_N` signatures, `0` weak-name rows, `0` uncertain-owner rows, `0` address-suffixed helper rows, and `0` address-suffixed wrapper rows.
- Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface advances to `1394/1560 = 89.36%`; top-500 remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260602-103048_post_wave1081_cthing_waypoint_residual_vtable_boundary_verified`, `19` files, `174787463` bytes, `DiffCount=0`.

What this proves:

- The seven target addresses now exist as saved function objects in the loaded retail Ghidra database.
- The saved names, signatures, comments, tags, decompile rows, instruction bodies, DATA xrefs, and vtable slots read back after save.
- The recovered bodies are bounded static retail evidence tied to true-vtable pointers and adjacent listing boundaries.

Probe token anchor: Wave1081; cthing-waypoint-residual-vtable-boundary-wave1081; 0x004bfa00 SharedVFunc__CopyGlobal829dd0Block30ToOut_004bfa00; 0x004f3760 CThing__AddShutdownEvent_004f3760; 0x004f37a0 CThing__StartDieProcess_004f37a0; 0x004f3d20 SharedVFunc__ForwardField28Slot10OrNull_004f3d20; 0x0043e9c0 SharedVFunc__CopyGlobal0066ea10Block10ToOut_0043e9c0; 0x005df550; 0x005dd278; 0x005dbf14; 812/1408 = 57.67%; 1394/1560 = 89.36%; 500/500 = 100.00%; 6283/6283 = 100.00%; G:\GhidraBackups\BEA_20260602-103048_post_wave1081_cthing_waypoint_residual_vtable_boundary_verified; boundary recovery.

What remains unproven:

- Exact source virtual names for every recovered shared helper.
- Concrete CThing/CWaypoint/CInfantryAI layout identity beyond observed offsets and dispatch slots.
- Runtime object, waypoint, event-delivery, death-process, orientation/output-copy, or field-forwarding behavior.
- BEA patching behavior, gameplay outcomes, and rebuild parity.
