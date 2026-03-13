# CGame__PlayMusicForCurrentLevel

- **Address:** `0x0046dc00`
- **Status:** Renamed, signature set, commented in Ghidra (read-back verified)
- **Signature:** `void CGame__PlayMusicForCurrentLevel(void *this)`
- **Source Alignment:** High-confidence parity with the level-music branch in `references/Onslaught/game.cpp` (tutorial track for level `100`, otherwise normal in-game track).

## Behavior

1. Checks global music-enabled flag.
2. Reads current level id from the game object (`this+0x30` in retail layout).
3. If level is `100`, calls music track type `2` (tutorial).
4. Otherwise calls music track type `4` (in-game selection).

## Why It Matters

- This helper cleanly explains the simple level-based music branch otherwise duplicated across game-flow code.
- It improves readability in callers that toggle music context (pause/unpause/front-end transitions).

## Related

- `CGame__RunLevel` (`0x0046e240`)
- `CGame__RestartLoopRunLevel` (`0x0046dc30`)
- `CMusic__PlayTrackByType`
