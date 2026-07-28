Status: active quick reference
Last updated: 2026-04-29
Source: migrated from archived Onslaught skills during the skill clean-slate pass.
Summary: Key source function signature lookup.
# Key Function Signatures

## Grade Calculation (Career.cpp:1178)

```cpp
char GetGradeFromRanking(float f) {
    if (f == 1.f) return 'S';
    if (f <= 0.f) return 'E';
    return 'D' - floor(f * 4);  // A=0.8, B=0.6, C=0.4, D=0.2
}
```

## Tech Slot Access (NO shift-16!)

```cpp
bool GetSlot(int slot) {
    return (mSlots[slot >> 5] & (1 << (slot & 31))) != 0;
}
void SetSlot(int slot) {
    mSlots[slot >> 5] |= (1 << (slot & 31));
}
```

## Cheat Detection (FEPSaveGame.cpp)

```cpp
bool IsCheatActive(int index) {
    // strstr = substring match ANYWHERE in name
    return strstr(saveName, cheat_codes[index]) != NULL;
}
```

## Kill Tracking (Player.cpp)

```cpp
void ThingKilledBy(CThing* thing) {
    if (thing->IsA(THING_TYPE_AIR_UNIT))
        mThingsKilled[TK_AIRCRAFT]++;
    if (thing->IsA(THING_TYPE_VEHICLE))
        mThingsKilled[TK_VEHICLES]++;
    // ... etc
}
```

## Version Stamp

```cpp
// references/Onslaught/Career.cpp:1086-1089
static SWORD current_version_stamp() {
    return SWORD(CAREER_VERSION + (sizeof(CCareer) << 4));
}
```

**CORRECTED 2026-07-28 — the derivation was wrong; the value it named is right.**

This snippet previously carried the trailing line `// = 0x00004BD1` inside the
code block, attributing the retail stamp to the formula exactly as pinned. That
attribution is false. The old line is quoted here rather than deleted so a reader
who remembers it can tell it was corrected, not lost.

- **MEASURED** — the retail stamp is `0x4BD1`: bytes 0-1 of
  `tests_shared/fixtures/gold_career_save.bin` (10,004 bytes) are `d1 4b`.
- **SOURCE** — `references/Onslaught/Career.cpp:22` declares
  `int CAREER_VERSION = 9 ;`, and nothing in the pinned corpus reassigns it. The
  only other occurrences are reads or comments: `Career.cpp:1049`, `:1075`,
  `:1085` (comment), `:1088`, and `Career.h:19` (`extern`).
- The formula **cannot** produce `0x4BD1` with that constant, for any integer
  `sizeof(CCareer)`. `0x4BD1 - 9 = 19400` and `19400 % 16 = 8`, while
  `(sizeof << 4)` is always a multiple of 16 — and stays one under the `SWORD`
  truncation, because 65536 is itself a multiple of 16.
- With the retail career block size `0x24BC` (9,404 bytes) the pinned constant
  yields `SWORD(9 + 150464) = 19401 = 0x4BC9`, eight short of the shipped stamp.

**INFERRED** — `0x4BD1` falls out of the same formula with `BASE_VERSION = 17`,
which is the derivation
[`../save-file/struct-layouts.md`](../save-file/struct-layouts.md) already records
under "Version Stamp Calculation": "The console port uses BASE_VERSION=17. The
internal PC build used 9." That inference holds only if `sizeof(CCareer)` is
`0x24BC` in the shipping build; it has not been measured against a retail binary
here, and this document does not assert it as measured.

So the snippet above is the **internal build's** version stamp, not retail's.
`../save-file/struct-layouts.md` is the authority for the shipped stamp, which is
the field the WinUI editor validates before touching a save.

## CSArray Template

```cpp
template <class T, int size>
class CSArray {
    T mItems[size];  // Raw array, no metadata
};
```

Implication: Save files are flat binary dumps.

## CActiveReader Smart Pointer

```cpp
CActiveReader<CUnit> mTarget;
// When target destroyed:
// 1. CMonitor::ToReadDied() called
// 2. mToRead = NULL
// 3. Read() returns NULL safely
```
