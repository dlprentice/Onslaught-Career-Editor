# Hazard.cpp Function Mappings

> Source family: `CHazard` cleanup helpers | Binary: `BEA.exe` (Steam build)

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

This folder tracks bounded saved-Ghidra evidence for Hazard-family helpers. Wave396 corrected the address-suffixed virtual-slot label at `0x0047e6e0` after metadata, decompile, xref, tag, and instruction read-back.

## Functions

| Address | Name | Purpose | Evidence |
| --- | --- | --- | --- |
| `0x0047e6e0` | `CHazard__VFunc02_CleanupWorldSoundAndLinkedState` | Vtable slot-2 cleanup path that releases sound samples, clears linked state, removes world occupancy, and dispatches base cleanup. | `ghidra_terrain_tail_wave396_2026-05-14.md` |

## Boundaries

- This is static saved-Ghidra evidence only.
- Exact source-body identity, concrete `CHazard` layout, local variable names, local types, runtime hazard behavior, BEA launch behavior, game patching, and rebuild parity remain unproven.
