# CCareer__UpdateThingsKilled

> Address: 0x0041c180 | Source: `references/Onslaught/Career.cpp`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** Yes (matches `CCareer::UpdateThingsKilled()` in `references/Onslaught/Career.cpp`)

## Purpose
Accumulate per-mission kill counts into the career totals (`mKilledThings[5]`). Called after a mission ends (except training).

## Signature
```c
void CCareer::UpdateThingsKilled(void);
```

## Algorithm (Source-Accurate)
```cpp
// Source: references/Onslaught/Career.cpp (CCareer::UpdateThingsKilled())
// Note: TK_TOTAL == 5
if (END_LEVEL_DATA.mWorldFinished == 100) return; // training level

for (int i = 0; i < TK_TOTAL; i++) {
  mKilledThings[i] += END_LEVEL_DATA.mThingsKilled[i];
  LOG.AddMessage("%-15s killed this level  %d,  Total %d", nameFor(i), END_LEVEL_DATA.mThingsKilled[i], mKilledThings[i]);
}
```

## Kill Counter Layout (CCareer offset 0x23F4)
Retail/Steam nuance:
- In-memory counters are dwords at `this + 0x23F4 + i*4`.
- The **lower 24 bits** are the integer kill payload.
- The **top byte** is metadata stored with a `0x80` bias (clamped on load for the first two counters).

This function adds per-level kills to the full dword, which preserves the top byte as long as the payload does not overflow `0x00FFFFFF`.

| Index | Category | CCareer Offset | Typical Unlock Thresholds |
|-------|----------|----------------|---------------------------|
| 0 | TK_AIRCRAFT | 0x23F4 | 25/50/75/100 |
| 1 | TK_VEHICLES | 0x23F8 | 100/200/300/400 |
| 2 | TK_EMPLACEMENTS | 0x23FC | 25/50 (75 only appears in combined unlocks) |
| 3 | TK_INFANTY | 0x2400 | 40/80/160 |
| 4 | TK_MECHS | 0x2404 | 20/40/80 (40 is used by 2 goodies) |

See also:
- `CCareer__GetKillCounterTopByte_23F4/_23F8` and `CCareer__SetKillCounterTopByte_23F4/_23F8`
- `reverse-engineering/save-file/kill-tracking.md`

## File Encoding Note (Aligned vs True Dword View)
Retail `.bes` files include a 16-bit version word and CCareer is bulk-copied from `source + 2`. As a result, the **true on-disk dword boundaries** for these counters are at `fileOffset = CCareerOffset + 2` (e.g. aircraft at `0x23F6`).

The binary’s comparisons use: `kills_payload = (dword & 0x00FFFFFF)`.
See `reverse-engineering/save-file/kill-tracking.md` for the detailed reconciliation.

## Notes
- Migrated from ghidra-analysis.md (Dec 2025)
- Critical for goodie unlocks based on kill thresholds
- Kill count offset was corrected Dec 2025 (was wrongly documented at 0x23A4)

## Related Functions
- [CCareer__UpdateGoodieStates](CCareer__UpdateGoodieStates.md) - Checks kill thresholds for unlocks
- [CCareer__Update](CCareer__Update.md) - Calls this after mission
