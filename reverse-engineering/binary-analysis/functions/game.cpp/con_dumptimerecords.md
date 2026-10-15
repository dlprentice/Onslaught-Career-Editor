# con_dumptimerecords

> Address: 0x0046bed0 | Source: `references/Onslaught/game.cpp`

## Status
- **Named in Ghidra:** Yes (free function)
- **Signature Set:** Yes
- **Verified vs Source:** Yes (`references/Onslaught/game.cpp:117`)

## Purpose

Console command: `dumptimerecords` dumps the game's time record telemetry (when compiled in).

## Notes (Binary Evidence)

- This build has `DEBUG_TIMERECORDS` disabled. The handler only prints:
  - `Time record support not compiled in!\n` (string at `0x0062bb5c`)

## Related

- Registered during level load (matches `references/Onslaught/game.cpp:1386`):
  - Pushes name `dumptimerecords` (`0x0062c104`)
  - Pushes desc `Dump the game time records` (`0x0062c114`)
  - Registers handler `0x0046bed0` via `CONSOLE.RegisterCommand(...)` call at `0x0046dec4`
