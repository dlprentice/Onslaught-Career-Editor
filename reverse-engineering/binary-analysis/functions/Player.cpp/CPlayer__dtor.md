# CPlayer__dtor

> Address: `0x004d28c0`
>
> Source: `references/Onslaught/Player.cpp` (`CPlayer::~CPlayer()`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** Partial (source-parity likely; signature and full retail decompile audit pending)

## Purpose
Destroy a `CPlayer` instance.

## Signature
```c
// TODO: Add verified signature
CPlayer::~CPlayer(void);
```

## Key Observations
- In Stuart source the destructor body is empty (no explicit cleanup in `Player.cpp`).
- Any required cleanup likely happens via member destructors / base-class destructors in the retail build.

## Notes
- Migrated from Phase 1 xref analysis (Dec 2025); details above are source-derived.

## Related Functions
- [CPlayer__ctor](CPlayer__ctor.md) - CPlayer constructor
- [CPlayer__GotoPanView](CPlayer__GotoPanView.md) - Pan-camera transition
