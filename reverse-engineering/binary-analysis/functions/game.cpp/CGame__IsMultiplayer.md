# CGame__IsMultiplayer

- **Address:** `0x004725d0`
- **Saved signature:** `int __thiscall CGame__IsMultiplayer(void * this)`
- **Source context:** `references/Onslaught/game.cpp`, `CGame::IsMultiplayer`

## Summary

Returns true when the current level value is in the source-parity multiplayer range `850..899`. Retail read-back checks the `CGame+0x2a0` current-level field through the predicate `0x351 < level && level < 900`, matching Stuart source `mCurrentlyRunningLevel >849 && mCurrentlyRunningLevel < 900`.

## Notes

- Wave 406 supersedes the stale `CExplosionInitThing__CheckValueRange_852_899` label.
- Saved via serialized headless dry/apply/read-back on 2026-05-14.
- Cross-cutting xrefs pass the `CGame` singleton from sound, career, render, BattleEngine, HUD/compass/battleline, landscape, particle, monitor, and pause-menu contexts.
- Read-back evidence includes one metadata row, one tag row, `54` xref rows, `81` instruction rows, post-rename decompile text, and focused probe status `PASS`.

## Not Proven

- Exact `CGame` field layout and world-type semantics remain open.
- Runtime multiplayer behavior is not proven by this static pass.
- This does not prove BEA launch behavior, game patching, or rebuild parity.
