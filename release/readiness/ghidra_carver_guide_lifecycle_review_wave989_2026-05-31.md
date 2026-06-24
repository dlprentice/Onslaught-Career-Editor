# Ghidra Carver Guide Lifecycle Review Wave989 Readiness Note

Status: complete read-only static evidence review
Date: 2026-05-31
Scope: `carver-guide-lifecycle-review-wave989`

Wave989 re-reviewed the CarverGuide lifecycle trio after the Wave988 cockpit lifecycle review. It made no Ghidra mutation: no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary CarverGuide rows:

| Address | Evidence |
| --- | --- |
| `0x00422f90 CCarverGuide__ctor` | Called from `0x00422440 CCarver__Init` at `0x0042249f`; delegates to `CAirGuide__ctor(this, guideTarget)`, then installs the `CCarverGuide` vtable pointer `0x005d947c`. |
| `0x00422fb0 CCarverGuide__scalar_deleting_dtor` | DATA xref from `0x005d9480` (`CCarverGuide` vtable slot 1); calls `0x00422fd0 CCarverGuide__dtor_base`, checks delete flag bit 0, optionally frees through `CDXMemoryManager__Free`, and returns `this`. |
| `0x00422fd0 CCarverGuide__dtor_base` | Reached from the scalar-deleting destructor; removes the active-reader cell at `+0x2c` when linked, then calls `0x004bac40 CMonitor__Shutdown`. |
| `0x00423490 CCarverGuide__HandleEvent` | DATA xref from `0x005d947c` (`CCarverGuide` vtable slot 0); forwards non-`0x7d1` events to `CAirGuide__HandleEvent`, otherwise calls `0x00423510 CCarverGuide__AcquireNearestTargetReader` and reschedules with a random delay. |
| `0x00423510 CCarverGuide__AcquireNearestTargetReader` | Called from `0x00423490`; clears the active reader at `+0x2c`, scans mapwho around owner `+0x18` using the 45.0-radius path, and accepts the nearest candidate through the saved Carver-specific threshold logic. |

Context rows:

- `0x00422440 CCarver__Init`
- `0x004bac40 CMonitor__Shutdown`

Read-back evidence:

- Fresh exports: 7 metadata rows, 7 tag rows, 121 xref rows, 238 body-instruction rows, 7 decompile rows, 256 vtable-slot rows, and 2 vtable-type rows.
- Vtable type evidence resolves `0x005d947c` to `CCarverGuide`.
- Vtable slots confirm `0x005d947c[0] -> CCarverGuide__HandleEvent`, `0x005d947c[1] -> CCarverGuide__scalar_deleting_dtor`, and `0x005e0d90[8] -> CCarver__Init` for CCarver continuity.
- Queue closure remains `6222/6222 = 100.00%`.
- Wave911 focused re-audit progress is `438/1408 = 31.11%`; expanded static surface progress is `509/1478 = 34.44%`.
- Verified backup: `G:\GhidraBackups\BEA_20260531-034107_post_wave989_carver_guide_lifecycle_review_verified`, 19 files, 173837191 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The saved CarverGuide lifecycle names/signatures/comments remain internally coherent under fresh metadata/tag/xref/instruction/decompile/vtable exports.
- The destructor rows have no stale `constructor` tag in the current tag export.
- The constructor row remains tied to the CCarver init allocation path, and the destructor-base row remains tied to monitor shutdown.

What remains separate:

- Runtime CarverGuide navigation/targeting behavior.
- Exact `CCarverGuide` layout.
- Exact source method or virtual names because `Carver.cpp` source is absent from the current source snapshot.
- BEA patching behavior.
- Rebuild parity.
