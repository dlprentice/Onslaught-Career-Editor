# CCareer__SetSlot

> Address: `0x004214e0`
>
> Source: `references/Onslaught/Career.cpp` (`CCareer::SetSlot(int, BOOL)`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Yes

## Purpose
Set/clear a tech-slot bit in `mSlots` (CCareer offset `0x2408`). Uses standard bit manipulation (NOT shift-16).

Source range check is `0 <= num < MAX_CAREER_SLOTS * 8` (32 * 8 = 256).

## Signature
```c
// Source: val TRUE => set, FALSE => clear
void CCareer::SetSlot(int num, int val);

// BEA.exe (Ghidra):
void CCareer__SetSlot(void * this, int slot_num, int val);
```

## Algorithm
```cpp
int i = num >> 5;
int b = num & 31;
int m = 1 << b;

if (val) {
  mSlots[i] |= m;
} else {
  mSlots[i] &= ~m;
}
```

## Known Slots
Slot IDs are defined by retail mission scripts (`game/data/MissionScripts/onsldef.msl`) and are used as persistent script-exposed flags.

Observed in real saves so far (true dword view):

| Slot | Script Macro | Notes |
|------|-------------|-------|
| 11 | `SLOT_F_731_MAINGUN_11` | Fenrir (world 731) component |
| 40 | `SLOT_F_732_TURRET_10` | Fenrir (world 732) component |
| 61 | `SLOT_500_ROCKET` | World 500 branch gating |
| 62 | `SLOT_500_SUB` | World 500 branch gating |
| 63..66 | `SLOT_TUTORIAL_1..4` | Tutorial completion flags |

Full slot list (1..66) is documented in `reverse-engineering/save-file/struct-layouts.md`.

## Notes
- Migrated from ghidra-analysis.md (Dec 2025)
- Tech slots use standard bit manipulation, NOT shift-16
- The save reserves 32 dwords (1024 bits), but the source range check only allows 256 slot IDs (0-255), so only `mSlots[0..7]` are used.
- On-disk dword boundary for `mSlots[0]` is at file offset `0x240A` (CCareer offset `0x2408` + 2 bytes).

## Related Functions
- [CCareer__Blank](CCareer__Blank.md) - Zeros all slots
