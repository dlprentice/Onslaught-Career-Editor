# CWorld__LoadWorld

> Address: 0x0050b9c0 | Source: World.cpp (source file not present in `references/Onslaught/` snapshot)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (headless postscript + read-back verified, 2026-03-01)
- **Verified vs Source:** Partial (behavior-level; source file is not present in current `references/Onslaught/` snapshot)

## Purpose

Loads a game world/level from an .aya asset archive file. This is the main entry point for level loading.

## Signature
```c
bool __thiscall CWorld__LoadWorld(void * this, void * levelName);
```

Read-back verified in `scratch/program_2026-03-01/phase5_signature_readback/index.tsv` (`status=OK`).

## Loading Process

1. **Parse AYA Header** - Read archive structure
2. **Extract Terrain** - Load heightmap and terrain textures
3. **Load Entities** - Spawn buildings, vehicles, units
4. **Initialize Scripts** - Load and compile MSL scripts
5. **Setup Audio** - Load level-specific sounds
6. **Finalize** - Post-processing and optimization

## Call-Chain Anchors (Pass 2)

- `CWorld__LoadWorldFile` delegates into this function (`functions/World.cpp/_index.md`).
- This function fans out into header/LOD/spawn setup helpers (`CWorld__LoadWorldHeader`, `CWorld__InitLODLists`, `CWorld__SpawnInitialThings`).
- Waypoint loading is called from this world-load chain (`functions/WaypointManager.cpp/_index.md`).
- Additional caller anchor captured in xref export:
  - `scratch/deep_semantic_tail_2026-02-27/pass2_semantic_wave145_prep/xrefs.tsv` line 21 (`CDXEngine__Unk_005475d0` call at `0x0050d11e`).

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
