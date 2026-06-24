Status: active quick reference
Last updated: 2026-04-29
Source: migrated from archived Codex Onslaught skills during the skill clean-slate pass.
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
static SWORD current_version_stamp() {
    return SWORD(CAREER_VERSION + (sizeof(CCareer) << 4));
}
// = 0x00004BD1
```

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
