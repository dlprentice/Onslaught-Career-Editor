# Ghidra Waypoint Random Offset / CWaypointPath Wave549 Readiness Note

Date: 2026-05-18

## Scope

Wave549 hardened three static Ghidra functions:

| Address | Saved symbol |
| --- | --- |
| `0x004ffe00` | `void __fastcall CWaypoint__RandomizeOffsetVectors(void * this)` |
| `0x00505bb0` | `void * __thiscall CWaypointPath__scalar_deleting_dtor(void * this, byte flags)` |
| `0x00505bd0` | `void __fastcall CWaypointPath__dtor_base(void * this)` |

## Evidence

- `CWaypoint__RandomizeOffsetVectors` uses ECX as the waypoint object, samples `Random__NextLCGAbs(DAT_008a9d9c)` four times, scales two random draws into offsets `+0x48/+0x54`, conditionally mirrors signs into `+0x50/+0x5c`, and duplicates positive offsets at `+0x4c/+0x58`.
- `CWaypointPath__scalar_deleting_dtor` is a table-backed scalar-deleting destructor wrapper: it calls `CWaypointPath__dtor_base`, checks `flags & 1`, frees `this` when requested, returns `this`, and ends with `RET 0x4`.
- `CWaypointPath__dtor_base` restores table pointer `0x005dfc8c`, frees optional pointer `+0x04`, clears the embedded `CSPtrSet` at `+0x08`, restores the exception list, and returns.
- Xrefs are bounded to four raw/no-function callsites for the random-offset helper, table data xref `0x005dfc8c` for the wrapper, and the wrapper call into the destructor body.

## Read-Back

- Dry: `updated=0 skipped=3 renamed=0 would_rename=2 missing=0 bad=0`.
- Apply: `updated=3 skipped=0 renamed=2 would_rename=0 missing=0 bad=0`.
- Verify dry: `updated=0 skipped=3 renamed=0 would_rename=0 missing=0 bad=0`.
- Ghidra save reported `REPORT: Save succeeded`.
- Post exports verified `3` metadata rows, `3` tag rows, `6` xref rows, `1287` instruction rows, and `3` decompile exports.
- Focused probe: `py -3 tools\ghidra_waypoint_path_wave549_probe.py --check` PASS.
- npm wrapper: `cmd.exe /c npm run test:ghidra-waypoint-path-wave549` PASS.
- Queue refresh: PASS with `6089` total functions, `2659` commented, `3430` commentless, `1535` exact-undefined signatures, and `1283` `param_N` signatures.
- Backup: `G:\GhidraBackups\BEA_20260518-123044_post_wave549_waypoint_path_verified`, `19` files, `159320967` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`.

## Not Proven

- Runtime waypoint/pathing behavior or AI navigation semantics.
- Exact source identity for these names.
- Concrete CWaypoint or CWaypointPath layout and field names/types.
- Complete ownership and slot semantics for table `0x005dfc8c`.
- BEA patching or rebuild parity.
