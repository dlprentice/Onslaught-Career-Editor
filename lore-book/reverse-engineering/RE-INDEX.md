# Reverse Engineering Documentation Index

> Master index for Battle Engine Aquila reverse engineering documentation
> Reorganized December 2025

## Overview

This directory contains technical documentation for the **Battle Engine Aquila** (2003) save file editor project. Documentation is organized into focused subfolders for easier navigation and maintenance.

**Key Insight**: The Steam PC release is a later retail build (console-port lineage) whose `.bes` format is a mostly-raw `CCareer` dump written/read at `file+2` after a 16-bit version word. Many values only *look* “shift-16” if you view the file at 4-byte aligned offsets.

---

## Directory Structure

```
reverse-engineering/
├── save-file/           # .BES file format (see save-file/_index.md for current counts)
├── game-mechanics/      # Runtime behavior, cheats (see game-mechanics/_index.md)
├── binary-analysis/     # Ghidra/executable analysis (see binary-analysis/_index.md for current counts)
├── game-assets/         # AYA archives, MSL scripts (see game-assets/_index.md for current counts)
├── project-meta/        # Attribution, community, audit notes (see folder index for current counts)
├── source-code/         # Stuart/AYA source analysis (see folder index for current counts)
└── RE-INDEX.md          # This file
```

---

## Subfolder Indexes

### [save-file/](save-file/) - Save File Format

Core documentation for the 10,004-byte `.bes` career save format.

| Document | Description |
|----------|-------------|
| [_index.md](save-file/_index.md) | Save-file documentation index |
| [save-format.md](save-file/save-format.md) | Complete file structure, offset map, and reserved/unmapped-region handling |
| [struct-layouts.md](save-file/struct-layouts.md) | CCareerNode, CCareerNodeLink, CGoodie definitions |
| [grade-system.md](save-file/grade-system.md) | Raw float ranking bits, S-E grade calculation |
| [goodies-system.md](save-file/goodies-system.md) | 233 displayable goodies in retail (300 slots in save) |
| [kill-tracking.md](save-file/kill-tracking.md) | Kill categories at 0x23F6 (packed meta+payload), unlock thresholds |

### [game-mechanics/](game-mechanics/) - Runtime Mechanics

Runtime behavior and cheat systems.

| Document | Description |
|----------|-------------|
| [_index.md](game-mechanics/_index.md) | Runtime mechanics overview |
| [god-mode.md](game-mechanics/god-mode.md) | God mode investigation (source/internal B4K42 path vs Steam/retail Maladim gating and runtime toggle behavior) |
| [cheat-codes.md](game-mechanics/cheat-codes.md) | Known cheats, activation flow |

### [binary-analysis/](binary-analysis/) - Executable Analysis

Ghidra disassembly and binary reverse engineering.

| Document | Description |
|----------|-------------|
| [_index.md](binary-analysis/_index.md) | Binary analysis navigation index (start here) |
| [README.md](binary-analysis/README.md) | Binary analysis overview and verified hashes |
| [GHIDRA-REFERENCE.md](binary-analysis/GHIDRA-REFERENCE.md) | Ghidra workspace and analysis reference |
| [executable-analysis.md](binary-analysis/executable-analysis.md) | PE metadata, DLL dependencies |
| [functions/_index.md](binary-analysis/functions/_index.md) | Per-source-file function mappings (see index for current counts) |
| [functions/FUNCTION_COVERAGE_STATE.md](binary-analysis/functions/FUNCTION_COVERAGE_STATE.md) | Binary-wide function-object coverage state (`% mapped`, remaining `FUN_`) |
| [windowed-mode-analysis.md](binary-analysis/windowed-mode-analysis.md) | -forcewindowed guard flag analysis |
| [widescreen-patch-analysis.md](binary-analysis/widescreen-patch-analysis.md) | ThirteenAG widescreen fix analysis |
| [widescreen-diff-regions-28.tsv](binary-analysis/widescreen-diff-regions-28.tsv) | Canonical 28-region binary diff map (`BEA.exe` vs `BEA_Widescreen.exe`) |
| [widescreen-diff-unresolved.md](binary-analysis/widescreen-diff-unresolved.md) | Canonical unresolved subset tracker for widescreen diff attribution |
| [widescreen-regions-8-11-validation.md](binary-analysis/widescreen-regions-8-11-validation.md) | Deep disassembly proof for the 8-11 widescreen hook cluster (closed unknowns) |
| [capture-menu-behavior.md](binary-analysis/capture-menu-behavior.md) | `File`/`Capture` menu command mapping and AVI-capture evidence |
| [deep-validation-status.md](binary-analysis/deep-validation-status.md) | Static RE gate tracker for ownership/type/behavior contract completion |
| [high-impact-subsystem-contracts.md](binary-analysis/high-impact-subsystem-contracts.md) | Phase-5 pass-2 contracts for AirUnit/Carrier/DiveBomber/FEPDebriefing/HeightField/Infantry/Mech/PauseMenu/ThunderHead/Unit/world/text |
| [high-impact-call-chain-appendix.md](binary-analysis/high-impact-call-chain-appendix.md) | Phase-5 call-chain depth appendix for frontend/world/text side effects and signature verification snapshot |
| [display-modernization-plan.md](binary-analysis/display-modernization-plan.md) | Post-validation display modernization decision matrix and rollout/test plan |
| [extra-graphics-feature-gate-patch.md](binary-analysis/extra-graphics-feature-gate-patch.md) | Retail extra-graphics unlock patch evidence and byte-verified apply/restore notes |
| [version-overlay-patch.md](binary-analysis/version-overlay-patch.md) | Companion patch note for the shipped `V1.00 - PATCHED` watermark behavior |

### [game-assets/](game-assets/) - Asset Formats

Game files, resource archives, and modding.

| Document | Description |
|----------|-------------|
| [_index.md](game-assets/_index.md) | Game assets documentation index |
| [game-folder-analysis.md](game-assets/game-folder-analysis.md) | Complete 680MB Steam release breakdown |
| [aya-asset-format.md](game-assets/aya-asset-format.md) | AYA archive structure, chunked format |
| [msl-scripting.md](game-assets/msl-scripting.md) | Mission Scripting Language |
| [mission-scripts-index.md](game-assets/mission-scripts-index.md) | Per-level MissionScripts inventory |
| [mission-slot-usage.md](game-assets/mission-slot-usage.md) | SetSlot/GetSlot usage from loose MSL |
| [mission-events-index.md](game-assets/mission-events-index.md) | Per-level event/objective usage from loose MSL |
| [mission-text-index.md](game-assets/mission-text-index.md) | Token → text index from loose English/Global files |
| [mission-message-usage.md](game-assets/mission-message-usage.md) | PlayCharMessage/AddHelpMessage usage from loose MSL |
| [mission-thing-usage.md](game-assets/mission-thing-usage.md) | GetThingRef/SpawnThing usage from loose MSL |
| [mission-speaker-index.md](game-assets/mission-speaker-index.md) | Speaker token → name mapping |
| [modding-reference.md](game-assets/modding-reference.md) | Launch options, widescreen, level editor |

### [project-meta/](project-meta/) - Project Resources

Attribution, community, and known issues.

| Document | Description |
|----------|-------------|
| [_index.md](project-meta/_index.md) | Project meta documentation index |
| [attribution.md](project-meta/attribution.md) | Developer attribution and legal notes |
| [community-resources.md](project-meta/community-resources.md) | Speedrun resources, public archives, similar games |
| [known-bugs.md](project-meta/known-bugs.md) | Resolved bugs, original game issues |

### [source-code/](source-code/) - Source Code Analysis

Stuart Gillam's internal PC build source code analysis.

| Subfolder | Documents |
|-----------|-----------|
| [core/](source-code/core/_index.md) | thing-system, actor-system, engine-system, platform-system |
| [gameplay/](source-code/gameplay/_index.md) | battle-system, career-system, game-system |
| [frontend/](source-code/frontend/_index.md) | fep-systems, controller-system |
| [io/](source-code/io/_index.md) | storage-system, chunker-system, event-system |
| [full-source-parse-2026-02-11.md](source-code/full-source-parse-2026-02-11.md) | Full-corpus parse refresh + metrics for both reference repos |

See [source-code/_index.md](source-code/_index.md) for complete index.

---

## Quick Reference

### File Offsets (BES format, 10,004 bytes)

| Offset | Size | Content |
|--------|------|---------|
| 0x0000 | 2 | Version word (`0x4BD1`) |
| 0x0002 | 4 | `new_goodie_count` (CCareer +0x0000) |
| 0x0006 | 6400 | CCareerNode[100] × 64 bytes |
| 0x1906 | 1600 | CCareerNodeLink[200] × 8 bytes |
| 0x1F46 | 1200 | CGoodie[300] × 4 bytes |
| 0x23F6 | 20 | Kill counters × 5 (packed `(meta<<24) | (kills&0x00FFFFFF)`) |
| 0x240A | 128 | mSlots[32] tech slots (bit arrays) |
| 0x248A | 4 | mCareerInProgress |
| 0x248E | 4 | mSoundVolume |
| 0x2492 | 4 | mMusicVolume |
| 0x2496 | 4 | `g_bGodModeEnabled` (CCareer +0x2494) |
| 0x249A | 4 | (unused/padding) |
| 0x249E | 4 | Invert Y (Flight/Jet) (P1) |
| 0x24A2 | 4 | Invert Y (Flight/Jet) (P2) |
| 0x24A6 | 4 | Invert Y (Walker) (P1) |
| 0x24AA | 4 | Invert Y (Walker) (P2) |
| 0x24AE | 4 | Controller vibration (P1) |
| 0x24B2 | 4 | Controller vibration (P2) |
| 0x24B6 | 4 | Controller config (P1) |
| 0x24BA | 4 | Controller config (P2) |
| 0x24BE | `0x20 * N` | Options entries (persisted keybind slots) |
| EOF-0x56 | 0x56 | Global tail snapshot (mouse/device/screen/audio globals) |

### Encoding Rules

- **Integers (true view)**: raw little-endian 32-bit at offsets where `file_offset % 4 == 2`
- **Floats**: raw IEEE-754 (no shift)
- **Booleans/flags**: typically raw `0`/`1` stored in 32-bit fields

### Grade Values

| Rank | Float | Bits (mRanking) |
|------|-------|-----------------|
| S | 1.0 | 0x3F800000 |
| A | 0.8 | 0x3F4CCCCD |
| B | 0.6 | 0x3F19999A |
| C | 0.35 | 0x3EB33333 |
| D | 0.15 | 0x3E19999A |
| E | 0.0 | 0x00000000 |
| NONE | -1.0 | 0xBF800000 |

---

## Related Files

- `/CURRENT_CAPABILITIES.md` - Current app surface and supported workflows
- `/lore/_index.md` - Game history, developer insights, story
- `/roadmap/ROADMAP-INDEX.md` - Project planning, features, investigations
- `/README.md` - Public GitHub readme

---

## External Resources

- **Stuart's GitHub**: https://github.com/stuart73/Onslaught
- **AYAResourceExtractor**: https://github.com/stuart73/AYAResourceExtractor
- **Lost Toys Archive**: https://web.archive.org/web/20030622111235/http://www.losttoys.com/
- **GDM Post-Mortem**: https://ia600907.us.archive.org/33/items/GDM_April_2003/GDM_April_2003.pdf

---

## Contributing

When adding new RE findings:

1. Add to the appropriate subfolder/topic file
2. Keep files under 1000 LOC (split if approaching limit)
3. Update subfolder `_index.md` if adding new documents
4. Include attribution for discoveries
5. Use hex offsets consistently (0x prefixed)
6. Note whether findings apply to console port, internal PC build, or both

---

*Last reviewed: 2026-03-04 (counts are maintained in each subfolder `_index.md`)*
