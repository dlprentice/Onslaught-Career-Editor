# CWorld__LoadWorld

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x0050b9c0` signature/comment correction. Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Address: 0x0050b9c0 | Source: World.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Current live-Ghidra signature:** corrected three-stack-argument prototype,
  applied and exactly read back on 2026-07-13
- **Revalidated ABI:** three explicit arguments
- **Verified vs Source:** Partial (behavior-level; source file is not present in current `references/Onslaught/` snapshot)
- **Latest static treatment:** 2026-07-13 runtime-critical revalidation

## Purpose

Loads serialized world state from a `CDXMemBuffer`-style input. The body is the
main retail world-load worker reached from `CWorld__LoadWorldFile`; static
evidence does not establish that its input is an `.aya` archive.

## Signature
```c
bool __thiscall CWorld__LoadWorld(
    void * this,
    void * mem_buffer,
    int is_base_world,
    int initialize_world_state);
```

Raw prologue stack accounting maps entry argument 1 to the memory-buffer read
receiver, argument 2 to the base-world gate forwarded into
`CWorld__LoadWorldHeader`, and nonzero argument 3 to initial teardown/LOD/global
world setup. The sole return is `RET 0xc`, proving three stack arguments. The
argument names are bounded semantic labels; arity, order, and callee cleanup are
direct ABI evidence.

## Historical Wave844 Static Read-Back

Wave844 saved comment/tag evidence and preserved the then-existing one-argument
signature. That preservation is historical read-back, not semantic validation;
the 2026-07-13 raw ABI review supersedes it. Wave844 made no function-boundary
or executable-byte change.

Key static anchors:

- Sole caller xref: `0x0050b720 CWorld__LoadWorldFile`.
- Prologue/tail: `0x0050b9da` calls `CRT__AllocaProbe` for a `0x38cc-byte stack frame`; `0x0050d4af` returns with `RET 0xc`.
- Setup: calls `CWorld__InitLODLists`, `CWorld__LoadWorldHeader`, `CWorld__LoadScriptEvents`, and recursive/base `CWorld__LoadWorldFile`.
- Entity and resource load path: calls `CHeightField__TraceMapLoadRequestAndCheckLoadedFlags`, `CEngine__LoadAllNamedMeshes`, `CWorldPhysicsManager__CreateSquad`, `CWorldPhysicsManager__CreateThingByType`, `CWorldPhysicsManager__CreateEffect`, `CWorldPhysicsManager__CreateTrigger`, `OID__CreateObject`, `InitThing__CreateThingByType`, and `CWorldMeshList__Add`.
- Tail: calls `CInfluenceMapManager__SkipLoad` or `CInfluenceMapManager__Load`, `CWaypointManager__LoadWaypoints`, version-gated occupancy chunk helpers, `CWorld__SpawnInitialThings`, `CInfluenceMapManager__Update`, `CInfluenceMapManager__PropagateDistances`, `CWorld__ClearOccupancyBitsUsingHeightBands`, and either `CWorld__ApplyStaticMaskToOccupancyBitplanes` or `CWorld__RebuildOccupancyGridFromDynamicSet`.

Post-Wave844 queue telemetry: `5668/6098 = 92.95%` strict clean-signature proxy. Next raw commentless row: `0x0050f680 CSpawnerThng__IsSpawnTypeAllowed`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-050626_post_wave844_cworld_load_world_verified`.

Boundary: this is static retail Ghidra evidence only. Exact world-buffer schema, concrete stack-local structure layouts, exact source-body identity, runtime load behavior, BEA patching, and rebuild parity remain deferred.

## Loading Process

1. Read and validate the observed world version range (`43..50`).
2. Load the world header and script-event data from the memory buffer.
3. Load heightfield and named-mesh state.
4. Create squads, things, effects, triggers, and related world objects.
5. Load or skip influence-map data and load waypoints.
6. For the non-base path, spawn initial things and finalize influence and
   occupancy state.

## Call-Chain Anchors (Pass 2)

- `CWorld__LoadWorldFile` delegates into this function (`functions/World.cpp/_index.md`).
- This function fans out into header/LOD/spawn setup helpers (`CWorld__LoadWorldHeader`, `CWorld__InitLODLists`, `CWorld__SpawnInitialThings`).
- Waypoint loading is called from this world-load chain (`functions/WaypointManager.cpp/_index.md`).
- The fresh targeted xref export retains one direct caller:
  `0x0050b720 CWorld__LoadWorldFile`.

## Level Naming

Levels follow a numeric naming convention:

| Range | Type | Example |
|-------|------|---------|
| 100-199 | Tutorial | Level 100 |
| 200-599 | Campaign | Level 200, 300... |
| 600-699 | Evolution | Level 600+ |

## Crash Investigation

The Evo levels (600+) were crashing until the lower-bits preservation bug was fixed. The crash occurred during world loading when the game read corrupted data from the save file.

## Memory Management

Level loading is memory-intensive. The function:
- Unloads previous level data
- Allocates memory for new level
- Streams assets as needed
- May trigger garbage collection

## Notes
- Migrated from ghidra-analysis.md (Dec 2025)
- Critical for understanding level structure
- Related to AYAResourceExtractor tool (Stuart's GitHub)
- Level crashes were caused by save file corruption, not world loading bugs
