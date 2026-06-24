# CGame__RunIntroFMV

- **Address:** `0x0046d890`
- **Status:** Renamed, signature set, commented in Ghidra (read-back verified)
- **Signature:** `void CGame__RunIntroFMV(void *this)`
- **Source Alignment:** High-confidence mapping to `CGame::RunIntroFMV()`.

## Behavior

1. Applies intro-FMV gating (first-time/load-state/stress/demo guards as compiled in retail).
2. Resolves intro FMV id via `lookup_FMV(level, 0)`.
3. Builds cutscene path and applies `_small` fallback when needed.
4. Unlocks associated cutscene goodie (`GS_NEW`) if not already unlocked/old.
5. Plays FMV and flushes input buffers after playback path.

## Related

- `lookup_FMV` (`0x00523120`)
- `Cutscene_FormatPath_WithSmallFallback` (`0x0046d810`)
- `CGame__RestartLoopRunLevel` (`0x0046dc30`)
