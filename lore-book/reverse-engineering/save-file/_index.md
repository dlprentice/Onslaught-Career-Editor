# Save File Documentation

> .BES file format analysis for Battle Engine Aquila career saves

## Overview

This folder contains documentation for the 10,004-byte `.bes` save file format used by the retail/Steam build. In the **true dword view**, integers are stored as normal little-endian 32-bit values and floats are raw IEEE-754. The historical “shift-16” appearance comes from viewing dwords at 4-byte aligned offsets even though `BEA.exe` copies CCareer bytes from/to `file+2`.

## Documents

| Document | Description |
|----------|-------------|
| [save-format.md](save-format.md) | Complete file structure, offset map, and reserved/unmapped-region handling |
| [struct-layouts.md](struct-layouts.md) | CCareerNode, CCareerNodeLink, CGoodie struct definitions |
| [career-graph.md](career-graph.md) | Campaign graph semantics: nodes vs links, `COMPLETE_BROKEN`, safe unlock strategies |
| [career-links.md](career-links.md) | Campaign link index map: link id -> from/to world, lower vs higher unlock conditions |
| [career-unlock-recipes.md](career-unlock-recipes.md) | Per-world unlock recipes: incoming link ids, minimal manual link patch, and natural unlock conditions |
| [grade-system.md](grade-system.md) | Raw float ranking bits, S-E grade calculation |
| [goodies-system.md](goodies-system.md) | 233 retail-displayable gallery slots (0-232), conditions, character bios |
| [kill-tracking.md](kill-tracking.md) | Kill categories at 0x23F6 (packed meta+payload; first two counters are confirmed metadata-bearing, and patchers should preserve the top byte on all five counters conservatively), unlock thresholds |

## Quick Reference

**File Layout:**
```
0x0000: Version word (0x4BD1) (16-bit)
0x0002: new_goodie_count (CCareer +0x0000)
0x0006: CCareerNode[100] (6400 bytes)
0x1906: CCareerNodeLink[200] (1600 bytes)
0x1F46: CGoodie[300] (1200 bytes)
0x23F6: Kill counters (20 bytes; packed meta+payload)
0x240A: Tech slots mSlots[32] (128 bytes)
0x2496: g_bGodModeEnabled (CCareer +0x2494)
0x249A: (unused/padding)
0x249E: Invert Y (Flight/Jet) (P1)
0x24A2: Invert Y (Flight/Jet) (P2)
0x24A6: Invert Y (Walker) (P1)
0x24AA: Invert Y (Walker) (P2)
0x24AE: Vibration (P1)
0x24B2: Vibration (P2)
0x24B6: Controller Config (P1)
0x24BA: Controller Config (P2)
0x24BE: Options entries (retail/Steam observed at N=16 => 0x20 * 16 bytes; engine save-size formula is 0x2514 + 0x20*N where N is enabled-entry count)
tail:   0x56-byte OptionsTail snapshot at end of file
```

Load semantics (Steam retail):
- options entries + tail are applied on `defaultoptions.bea` load (`CCareer::Load` flag=0)
- options entries + tail are skipped on career `.bes` load (`CCareer::Load` flag=1)

**Encoding (true dword view):**
- Integers: raw little-endian 32-bit at offsets where `file_offset % 4 == 2`
- Floats: raw IEEE-754
- Booleans/flags: typically raw `0`/`1` stored in 32-bit fields

## See Also

- [../source-code/](../source-code/) - Stuart's source code analysis
- [../game-mechanics/](../game-mechanics/) - God mode, cheat codes
- [CURRENT_CAPABILITIES.md](/CURRENT_CAPABILITIES.md) - Current app surface and supported workflows

---

*Last updated: 2026-03-04*
