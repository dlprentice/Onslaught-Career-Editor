# Ghidra Waypoint Wave538 Readiness Note

Date: 2026-05-18

## Scope

Wave538 saved static Ghidra name/signature/comment/tag corrections for six Waypoint/WaypointManager functions:

| Address | Saved name | Saved signature |
| --- | --- | --- |
| `0x005057b0` | `CWaypoint__InitAndLink` | `void __thiscall CWaypoint__InitAndLink(void * this, void * init)` |
| `0x00505810` | `CWaypoint__ShutdownAndUnlink` | `void __fastcall CWaypoint__ShutdownAndUnlink(void * this)` |
| `0x00505960` | `CWaypoint__Load` | `void __thiscall CWaypoint__Load(void * this, void * mem_buffer, int load_mode, void * object_table)` |
| `0x00505ab0` | `CWaypointManager__ReleasePendingObjects` | `void __cdecl CWaypointManager__ReleasePendingObjects(void)` |
| `0x00505ae0` | `CWaypointManager__LoadWaypoints` | `void __cdecl CWaypointManager__LoadWaypoints(void * mem_buffer, int load_mode, void * object_table)` |
| `0x005d5860` | `CWaypointManager__LoadWaypoints_unwind` | `void __cdecl CWaypointManager__LoadWaypoints_unwind(void)` |

The important owner correction is `0x00505960`: `CWaypointManager__LoadWaypoints` allocates a waypoint object and calls this body with that object in `ECX`, so the saved name is now `CWaypoint__Load` rather than the stale manager-owned `CWaypointManager__LoadWaypoint`.

## Evidence

- Apply script: `tools/ApplyWaypointWave538.java`.
- Probe: `tools/ghidra_waypoint_wave538_probe.py`.
- Read-back artifacts: `subagents/ghidra-static-reaudit/wave538-waypoint-005057b0/`.
- Dry run: `updated=0 skipped=6 renamed=0 would_rename=3 missing=0 bad=0`.
- Apply: `updated=6 skipped=0 renamed=3 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Verify dry: `updated=0 skipped=6 renamed=0 would_rename=0 missing=0 bad=0`.
- Post read-back verified `6` metadata rows, `6` tag rows, `6` xref rows, `678` instruction rows, `6` decompile exports, and CWaypoint vtable rows for slots 2 and 9.
- Focused probe: `py -3 tools\ghidra_waypoint_wave538_probe.py --check` PASS.
- Npm wrapper: `cmd.exe /c npm run test:ghidra-waypoint-wave538` PASS.
- Queue refresh: `cmd.exe /c npm run test:ghidra-static-reaudit-queue` PASS after the mutation.
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260518-075151_post_wave538_waypoint_verified`, `19` files, `159288199` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`.

## Queue Snapshot

Fresh queue telemetry after Wave538:

| Metric | Value |
| --- | ---: |
| Function objects | `6089` |
| Commented functions | `2628` |
| Commentless functions | `3461` |
| Exact-undefined signatures | `1535` |
| `param_N` signatures | `1313` |
| Comment-backed proxy | `2628/6089 = 43.16%` |
| Strict comment-plus-clean-signature proxy | `2574/6089 = 42.27%` |

This is telemetry only, not a completion milestone.

## Not Proven

- Runtime waypoint/pathing behavior or AI navigation semantics.
- Exact source-body identity for the behavior-derived names.
- Concrete `CWaypoint`, init-context, object-table, pending-set, or list layouts beyond observed offsets.
- Whether adjacent no-function byte ranges around `0x00505830..0x0050595e` should become named functions.
- BEA launch, executable patching, and rebuild parity.
