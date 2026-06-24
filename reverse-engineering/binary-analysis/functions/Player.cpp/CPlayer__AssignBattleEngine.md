# CPlayer__AssignBattleEngine

> Address: `0x004d3080`
>
> Source: `references/Onslaught/Player.cpp` / `references/Onslaught/Player.h`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (Wave472)
- **Verified vs Source:** Partial static source bridge; runtime player/BattleEngine behavior deferred

## Signature
```c
void __thiscall CPlayer__AssignBattleEngine(void * this, void * battle_engine);
```

## Key Observations
- The retail body reads one stack argument from `[ESP + 0x4]`, pushes that value into `CGenericActiveReader__SetReader`, and returns with `RET 0x4`.
- Four caller sites in `CGame__PostLoadProcess` and `CGame__RespawnPlayer` push one BattleEngine pointer before calling `0x004d3080`.
- The body rebinds the player active-reader cell around `this + 0x1c`, then sets the BattleEngine-side player reader around `battle_engine + 0x574` back to `this`.
- If the player god-style flag around `this + 0x20` is nonzero, the body dispatches source-compatible vulnerability and infinite-energy toggles through vtable offsets `+0xe0` and `+0x154`.
- Source header evidence ties this to `void CPlayer::AssignBattleEngine(CBattleEngine* be)`.

## Notes
- Wave472 removed the stale extra `param_2` from the saved Ghidra signature and replaced open-signature wording with stack-cleanup/caller evidence.
- Runtime god/vulnerability behavior, exact `CPlayer`/`CBattleEngine` layouts, exact virtual method identities, BEA launch, game patching, and rebuild parity remain deferred.

## Related
- [CPlayer View Helpers](CPlayer__ViewHelpers.md)
- [CPlayer Snapshot Helpers](CPlayer__SnapshotHelpers.md)
- [CPlayer__GotoPanView](CPlayer__GotoPanView.md)
