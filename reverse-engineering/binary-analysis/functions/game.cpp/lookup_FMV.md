# lookup_FMV

- **Address:** `0x00523120`
- **Status:** Renamed, signature set, commented in Ghidra (read-back verified)
- **Signature:** `int lookup_FMV(int level_id, int index_type)`
- **Source Alignment:** High-confidence parity with `lookup_FMV(...)` used by `CGame::GetIntroFMV` / `RunOutroFMV` in `references/Onslaught/game.cpp`.

## Behavior

1. Walks an internal FMV mapping table keyed by level id.
2. On match, returns one of three FMV slots by `index_type`:
   - `0`: intro FMV
   - `1`: primary outro FMV
   - `2`: alternate outro FMV
3. Returns `-1` when no mapping exists.

## Related

- `CGame__RunIntroFMV` (`0x0046d890`)
- `CGame__RunOutroFMV` (`0x0046d9f0`)
- `CGame__RestartLoopRunLevel` (`0x0046dc30`)
