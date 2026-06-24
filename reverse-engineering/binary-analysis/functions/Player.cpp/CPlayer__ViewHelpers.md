# CPlayer View Helpers

> Addresses: `0x004d28a0`, `0x004d28c0`, `0x004d29c0`, `0x004d2a50`
>
> Source: `references/Onslaught/Player.cpp` / `references/Onslaught/Player.h`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (Wave470)
- **Verified vs Source:** Partial static source bridge; runtime camera behavior deferred

## Signatures
```c
void __fastcall CPlayer__Init(void * this);
void __fastcall CPlayer__GotoFPView(void * this);
void __fastcall CPlayer__Goto3rdPersonView(void * this);
void __fastcall CPlayer__GotoControlView(void * this);
```

## Key Observations
- `CPlayer__Init` calls `CPlayer__GotoFPView`, then stores `PLATFORM__GetSysTimeFloat()` around `this + 0x4c`, matching source `mTimeoutTime`.
- `CPlayer__GotoFPView` exits if the active BattleEngine reader around `this + 0x1c` is null, sets current view mode around `this + 0x24` to `PLAYER_FP_VIEW` (`1`), allocates an 8-byte `CThingCamera`-style object, and calls the current-camera setter with `player_number - 1`.
- `CPlayer__Goto3rdPersonView` uses the same BattleEngine guard, sets view mode to `PLAYER_3RD_PERSON_VIEW` (`2`), allocates a 0xc-byte third-person camera object, calls `CThing3rdPersonCamera__ctor`, and sets it as current camera.
- `CPlayer__GotoControlView` reads preferred control view mode around `this + 0x28`, dispatching to first-person for mode `1` and third-person for mode `2`.
- Source header evidence ties the enum to `PLAYER_PAN_VIEW`, `PLAYER_FP_VIEW`, `PLAYER_3RD_PERSON_VIEW`, and event `GOTO_CONTROL_VIEW = 4000`.

## Notes
- Wave470 saved names/signatures/comments/tags for this view tranche after fresh metadata, decompile, xref, instruction, and source review.
- This pass corrected stale public docs that still associated `0x004d28c0` and `0x004d29c0` with constructor/destructor notes.
- Runtime camera behavior, exact `CPlayer` layout, BEA launch, game patching, and rebuild parity remain deferred.

## Related
- [CPlayer__ctor](CPlayer__ctor.md)
- [CPlayer__dtor](CPlayer__dtor.md)
- [CPlayer__GotoPanView](CPlayer__GotoPanView.md)
