# CPlayer__ctor

> Address: `0x004d29c0`
>
> Source: `references/Onslaught/Player.cpp` (`CPlayer::CPlayer(int number)`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** No
- **Verified vs Source:** Partial (source-parity likely; signature and full retail decompile audit pending)

## Purpose
Initialize a `CPlayer` instance with its player-slot number and default gameplay state (view mode, kill counters, god-mode flag).

## Signature
```c
// TODO: Add verified signature
CPlayer::CPlayer(int number);
```

## Key Observations
- Source constructor initializes `mNumber` from `number`.
- Clears `mBattleEngine` ActiveReader (`SetReader(NULL)` in source).
- Calls `WipeStats()` (stats reset).
- Sets view defaults (`mCurrentViewMode = PLAYER_FP_VIEW`, `mPreferedControlView = PLAYER_FP_VIEW`).
- Clears kill counters (`mThingsKilled.SetAll(0)`).
- Reads persisted god-mode toggle (`mIsGod = CAREER.GetIsGod(mNumber-1)` in source).

## Notes
- Migrated from Phase 1 xref analysis (Dec 2025); details above are source-derived.
- Source has a separate `CPlayer::Init()` for runtime initialization (calls `GotoFPView()` and stamps timeout time).

## Related Functions
- [CPlayer__dtor](CPlayer__dtor.md) - CPlayer destructor
- [CPlayer__GotoPanView](CPlayer__GotoPanView.md) - Pan-camera transition
