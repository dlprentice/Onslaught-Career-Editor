# CPlayer__ctor

> Address: `0x004d2780`
>
> Source: `references/Onslaught/Player.cpp` (`CPlayer::CPlayer(int number)`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (Wave470)
- **Verified vs Source:** Partial static source bridge; runtime layout/rebuild proof deferred

## Purpose
Initialize a `CPlayer` instance with its player-slot number and default gameplay state (view mode, kill counters, god-mode flag).

## Signature
```c
void * __thiscall CPlayer__ctor(void * this, int player_number);
```

## Key Observations
- Retail address is `0x004d2780`; older notes incorrectly attached this doc to a view helper address.
- Sets the `CPlayer` vtable pointer to `0x005de770`.
- Source constructor initializes `mNumber` from `number`.
- Clears `mBattleEngine` ActiveReader storage.
- Calls `WipeStats()` (stats reset).
- Sets view defaults (`mCurrentViewMode = PLAYER_FP_VIEW`, `mPreferedControlView = PLAYER_FP_VIEW`).
- Clears kill counters (`mThingsKilled.SetAll(0)`).
- Reads a CAREER-adjacent per-player flag matching source `mIsGod = CAREER.GetIsGod(mNumber-1)`.

## Notes
- Wave470 saved the Ghidra name/signature/comment/tag after fresh metadata, decompile, xref, instruction, and source review.
- Source has a separate `CPlayer::Init()` for runtime initialization (calls `GotoFPView()` and stamps timeout time).
- Exact `CPlayer` field layout, runtime camera behavior, BEA launch, game patching, and rebuild parity remain deferred.

## Related Functions
- [CPlayer__dtor](CPlayer__dtor.md) - CPlayer destructor
- [CPlayer__GotoPanView](CPlayer__GotoPanView.md) - Pan-camera transition
