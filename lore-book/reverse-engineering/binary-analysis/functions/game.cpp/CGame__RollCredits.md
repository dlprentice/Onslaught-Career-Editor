# CGame__RollCredits

- **Address:** `0x004726b0`
- **Status:** Renamed + signature set in Ghidra (direct-HTTP read-back verified)
- **Signature:** `void CGame__RollCredits(void)`
- **Source Alignment:** High-confidence mapping to `CGame::RollCredits()` (`references/Onslaught/game.cpp:4107`).

## Behavior

1. Captures start time via `PLATFORM__GetSysTimeFloat`.
2. Builds a temporary local control handler object with a quit flag (matches source `CGameCreditControlHandler` pattern).
3. Allocates/initializes temporary controllers and flushes input each frame.
4. If music is enabled, starts credits track selection.
5. Main loop:
   - Pumps platform events.
   - Flushes controller input.
   - Begins scene, clears screen, applies render state.
   - Calls `CCredits__RenderCredits(elapsed, alpha)`; exits when it returns false.
   - Updates music, ends scene, flips.
   - Also exits if skip/quit input flag is set.
6. Shuts down local monitor/control object, frees temporary controllers, stops music.

## Related

- `CGame__RunOutroFMV` (`0x0046d9f0`) calls this for final-level routes.
- `CCredits__RenderCredits` (`0x0051a030`) is the per-frame credits renderer.
