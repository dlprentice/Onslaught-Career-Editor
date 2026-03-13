# Game Assets Documentation

> AYA archives, MSL scripting, game files, and modding

## Overview

This folder documents Battle Engine Aquila's asset formats and file structure. The game uses proprietary `.aya` files for **multiple** asset families (mesh/texture packages and resource archives) and `.msl` scripts for mission logic.

**Important scope note:** `aya-asset-format.md` describes the **mesh/texture** flavor of `.aya` (what AYAResourceExtractor can parse). Other `.aya` resource archives (e.g., `goodie_###_res_PC.aya`) use different tag sets and are **not** currently parsed by the extractor.

**Note:** Asset formats are separate from save files (`.bes`). See [../save-file/](../save-file/) for career save documentation.

## Documents

| Document | Description |
|----------|-------------|
| [game-folder-analysis.md](game-folder-analysis.md) | Complete 680MB Steam release breakdown |
| [aya-asset-format.md](aya-asset-format.md) | AYA archive structure, chunked format |
| [msl-scripting.md](msl-scripting.md) | Mission Scripting Language - syntax, events, functions |
| [mission-scripts-index.md](mission-scripts-index.md) | Per-level script inventory from loose MissionScripts |
| [mission-slot-usage.md](mission-slot-usage.md) | SetSlot/GetSlot usage extracted from loose MSL |
| [mission-events-index.md](mission-events-index.md) | Per-level event/objective usage from loose MSL |
| [mission-text-index.md](mission-text-index.md) | Token → text index from loose English/Global files |
| [mission-message-usage.md](mission-message-usage.md) | PlayCharMessage/AddHelpMessage usage from loose MSL |
| [mission-thing-usage.md](mission-thing-usage.md) | GetThingRef/SpawnThing usage from loose MSL |
| [mission-speaker-index.md](mission-speaker-index.md) | Speaker token → name mapping (global text) |
| [modding-reference.md](modding-reference.md) | Launch options, widescreen patch, level editor |

## File Format Quick Reference

| Extension | Purpose | Tool |
|-----------|---------|------|
| `.aya` | Mesh/texture packages and resource archives | AYAResourceExtractor (mesh/texture only) |
| `.msl` | Mission scripts | Text editor |
| `.bes` | Career saves | This project |
| `.vid` | Bink video | ffmpeg |
| `.ogg` | Audio | Standard players |

## AYA Chunk Tags

The tags below refer to **resource-archive** `.aya` notes from earlier research and are **not** the mesh/texture tag set documented in `aya-asset-format.md`. Treat as **non-exhaustive** and verify before use.

| Tag | Purpose |
|-----|---------|
| `LVLR` | Level resources |
| `GDIE` | Goodie data |
| `TEXT` | Textures |
| `MESH` | 3D meshes |
| `NEKO` | Xbox memory card magic |

## See Also

- [../source-code/io/_index.md](../source-code/io/_index.md) - Chunker system source analysis
- [Stuart's AYAResourceExtractor](https://github.com/stuart73/AYAResourceExtractor)
- [CURRENT_CAPABILITIES.md](/CURRENT_CAPABILITIES.md) - Current app surface and supported workflows

---

*Last updated: February 2026*
