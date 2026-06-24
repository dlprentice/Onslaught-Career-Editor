# CGame__RunOutroFMV

- **Address:** `0x0046d9f0`
- **Status:** Renamed, signature set, commented in Ghidra (read-back verified)
- **Signature:** `void CGame__RunOutroFMV(void *this)`
- **Source Alignment:** High-confidence mapping to `CGame::RunOutroFMV()`.

## Behavior

1. Runs only on qualifying quit/final-state conditions.
2. Resolves primary/alternate outro FMV ids via `lookup_FMV(level, 1/2)`.
3. Applies level-specific branch conditions (notably level `500` and `720` paths).
4. Uses cutscene path fallback and unlocks corresponding goodie state.
5. Plays selected outro and triggers `CGame__RollCredits` for final-level routes.

## Related

- `lookup_FMV` (`0x00523120`)
- `Cutscene_FormatPath_WithSmallFallback` (`0x0046d810`)
- `CGame__RollCredits` (`0x004726b0`)
- `CGame__RunLevel` (`0x0046e240`)
