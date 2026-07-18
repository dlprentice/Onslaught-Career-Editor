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

## Retail level-intro skip paths

This function owns a level's intro FMV, not the startup front-end sequence. The
Steam build has two distinct skip mechanisms for this playback path:

- `CLIParams__ParseCommandLine` (`0x00423BC0`) recognizes `-skipfmv` and sets
  the gate read by this function at `0x00663050`, so the level-intro playback
  call is never entered. It does not bypass the startup logo, startup movie, or
  click-to-start page.
- During playback, the receiver at `0x004656E0` sets the FMV quit flag for
  virtual `BUTTON_SKIP_CUTSCENE` (`7`). The retail default single-player table
  at `0x00514210` binds that action to Space (`DIK 0x39`), Enter (`0x1C`),
  Escape (`0x01`), and numpad Enter (`0x9C`). The playback loop at `0x0053F190`
  also exits on the left-, middle-, or right-mouse transient latches populated
  by both the window-message and DirectInput paths.

Stuart's `CLIParams.cpp` and `game.cpp` corroborate the `-skipfmv` gate, while
his controller table shows only the source-build Space mapping. The broader key
set and mouse exits above come directly from the Steam executable. A single
keypress missed during focus acquisition or transient-input reset does not
establish that the cinematic is unskippable.

The separate, controlled startup sequence is documented in
[`fep-systems.md`](../../../source-code/frontend/fep-systems.md#steam-startup-skip-sequence).

## Related

- `lookup_FMV` (`0x00523120`)
- `Cutscene_FormatPath_WithSmallFallback` (`0x0046d810`)
- `CGame__RestartLoopRunLevel` (`0x0046dc30`)
