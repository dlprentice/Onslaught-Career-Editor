# Ghidra Explosion Path Cost Grid Wave820 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `explosion-path-cost-grid-wave820`

Wave820 explosion path cost grid saved comments, tags, and observed ABI signatures for eight adjacent `CExplosionInitThing` guidance/path cost-grid helpers from `0x004bc2e0 CExplosionInitThing__ClearCostGridBoundsAndBuildPath` through `0x004beb30 CExplosionInitThing__FindNearestVisitedGridCell`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Exact anchor set: `0x004bc2e0 CExplosionInitThing__ClearCostGridBoundsAndBuildPath`, `0x004be1d0 CExplosionInitThing__BuildGridPathWithFallbackSearch`, `0x004be420 CExplosionInitThing__SelectNextPathStepDirection`, `0x004be9b0 CExplosionInitThing__CanStepNorthFromCurrent`, `0x004bea10 CExplosionInitThing__CanStepWestFromCurrent`, `0x004bea70 CExplosionInitThing__CanStepSouthFromCurrent`, `0x004bead0 CExplosionInitThing__CanStepEastFromCurrent`, and `0x004beb30 CExplosionInitThing__FindNearestVisitedGridCell`.

Representative anchors:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x004bc2e0 CExplosionInitThing__ClearCostGridBoundsAndBuildPath` | `int __thiscall ... (void * this, float start_x, float start_y, float start_z_lane, float start_w_lane, float goal_x, float goal_y, float goal_z_lane, float goal_w_lane, int search_flags, void * path_state)` | `RET 0x28` confirms ten stack dwords after the ECX receiver; external xrefs include `0x004a0eab`, `0x0048a880`, `0x004e7696`, and orphan block `0x0047d9c1`; body clears bounded `DAT_00809dc0` cost-grid cells to `0xffff` and forwards into `0x004be1d0`. |
| `0x004be1d0 CExplosionInitThing__BuildGridPathWithFallbackSearch` | `int __cdecl ... (float start_x, float start_y, float start_z_lane, float start_w_lane, float goal_x, float goal_y, float goal_z_lane, float goal_w_lane, void * bitplane_base, int search_flags, void * path_state)` | Caller `0x004bc2e0` cleans `0x2c` stack bytes; helper rounds x/y vector lanes, stores `DAT_00809db8`, fast-tests `CExplosionInitThing__IsGridSegmentBlocked`, and falls back through nearest-bit/path selection helpers. |
| `0x004be420 CExplosionInitThing__SelectNextPathStepDirection` | `int __cdecl ... (void)` | Marks current `DAT_00829dc0`/`DAT_00809dbc` in `DAT_00809dc0`, compares to `DAT_00809db4`/`DAT_00809db0`, tests the `DAT_00809db8` bitplane directly or through the four `CanStep*` helpers, then dispatches through `PTR_LAB_004be94c`. |
| `0x004be9b0` through `0x004bead0` | four `int __cdecl CExplosionInitThing__CanStep*FromCurrent(void)` predicates | North/west/south/east helpers each check bounds, the unvisited `DAT_00809dc0` cost-grid cell value `-1`, and the packed occupancy bit under `DAT_00809db8`. |
| `0x004beb30 CExplosionInitThing__FindNearestVisitedGridCell` | `void __cdecl ... (void)` | Expanding-ring fallback over the `DAT_00809dc0` cost grid; mutates `DAT_00809db4`/`DAT_00809db0` to the first reachable non-`-1` cell after direction selection fails. |

Read-back evidence:

- Initial dry: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=8 comment_only_updated=8 missing=0 bad=0`.
- First apply intentionally remains in evidence and exposed a thiscall read-back mismatch for `0x004bc2e0`: Ghidra inserted explicit `this` ahead of the intended receiver. The script was corrected to the saved Ghidra receiver spelling.
- Corrected dry: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=1 missing=0 bad=0`.
- Corrected apply: `updated=1 skipped=7 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=1 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Final dry: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports: 8 metadata rows, 8 tag rows, 23 xref rows, 2088 target instruction rows, 729 helper instruction rows, 371 callsite instruction rows, 9 helper metadata rows, and 8 decompile rows.
- Queue after Wave820: 6098 total, 5620 commented, 478 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5620/6098 = 92.16%`, strict clean-signature proxy `5620/6098 = 92.16%`.
- Next raw commentless row: `0x004c0c70 CPDSimpleSprite__EvalExpressionNode`; commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-171120_post_wave820_explosion_path_cost_grid_verified`, 19 files, 171477895 bytes, `DiffCount=0`.

What this proves:

- The eight target function rows exist in the saved Ghidra project.
- The saved signatures/comments/tags match the Wave820 script read-back.
- The evidence ties the cluster to guide/path calls, the `DAT_00809dc0` cost grid, `DAT_00809db8` occupancy bitplane base, and already-commented Wave457/Wave819 helper context.

What remains unproven:

- Exact vector lane semantics.
- Exact `search_flags` meaning.
- Concrete `path_state` layout.
- Runtime guidance/pathing behavior.
- Exact source-body identity.
- BEA patching behavior.
- Rebuild parity.
