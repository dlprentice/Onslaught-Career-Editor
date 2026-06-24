# CGame__GetPlayerLives

- **Address:** `0x004725f0`
- **Saved signature:** `int __thiscall CGame__GetPlayerLives(void * this, int player_index)`
- **Source context:** `references/Onslaught/game.cpp`, `CGame::GetPlayerLives`

## Summary

Returns the player lives counter for player index `1` or `2`, matching the source helper shape.

## Notes

- Wave 381 hardened the saved signature/comment/tags without changing the existing name.
- Read-back evidence includes player-index compares and CGame field reads around `+0x290` and `+0x294`.

## Not Proven

- Runtime lives behavior is not proven by this static pass.
- Exact CGame field names and local types remain open.
- BEA launch behavior, game patching, and rebuild parity are not proven.
