# FEPDebriefing.cpp - Function Index

> Source File: FEPDebriefing.cpp | Category: Frontend/Mission Debriefing

## Overview

Frontend mission debriefing screen implementation. Displays mission results after completion, including rank achieved, kills by category, and unlocked content.

## Functions

| Address | Function | Status | Description |
|---------|----------|--------|-------------|
| 0x00456780 | [CFEPDebriefing__Initialize](./CFEPDebriefing__Initialize.md) | Named | Initialize mission debriefing screen |

Live signature (normalized, 2026-02-24):
- `int CFEPDebriefing__Initialize(void * this)`

Caller-anchor update (2026-03-01):
- Dedicated xref export for `0x00456780` produced `from_addr=0x005db9c0`, `ref_type=DATA`, indicating indirect vtable/dispatch-table invocation (`scratch/program_2026-03-01/phase5_fepdebriefing_xrefs/xrefs.tsv`).

## Debriefing Screen Contents

After completing a mission, the debriefing screen displays:

1. **Mission Rank** (S, A, B, C, D, E)
   - Calculated from performance metrics
   - Uses `GetGradeFromRanking()` to convert float to letter grade

2. **Kill Statistics**
   - Aircraft destroyed
   - Vehicles destroyed
   - Emplacements destroyed
   - Infantry eliminated
   - Mechs destroyed

3. **Unlocked Content**
   - New goodies unlocked by this mission
   - Based on kill thresholds and grade achieved

4. **Mission Time**
   - Time taken to complete the mission

## Grade Calculation

From Career.cpp source:
```cpp
if (f == 1.f) c = 'S';
else if (f <= 0.f) c = 'E';
else c = 'D' - floor(f * 4);
```

| Float Range | Grade |
|-------------|-------|
| 1.0 | S |
| 0.75-0.99 | A |
| 0.50-0.74 | B |
| 0.25-0.49 | C |
| 0.01-0.24 | D |
| <= 0.0 | E |

## Kill Thresholds for Goodies

| Kill Type | Thresholds | Goodies Unlocked |
|-----------|------------|------------------|
| Aircraft | 25, 50, 75, 100 | 4 goodies |
| Vehicles | 100, 200, 300, 400 | 4 goodies |
| Emplacements | 25, 50 (75 only in combined unlocks) | 2 standalone (+ combined unlocks) |
| Infantry | 40, 80, 160 | 3 goodies |
| Mechs | 20, 40, 80 | 4 goodies (40 unlocks 2 goodies) |

## Cross-References

- Related: [Career.cpp](../Career.cpp/_index.md) - grade calculation and kill tracking
- Related: [FEPGoodies.cpp](../FEPGoodies.cpp/_index.md) - goodie unlock display

## Migration Notes

- Migrated from ghidra-analysis.md (Dec 2025)
