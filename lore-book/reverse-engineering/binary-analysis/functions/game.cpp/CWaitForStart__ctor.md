# CWaitForStart__ctor

> Address: `0x0046dbd0` | Source context: `references/Onslaught/game.cpp` restart-loop local wait object setup

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void CWaitForStart__ctor(void *this)`)
- **Verified vs Source:** Yes (high-confidence structural parity for local wait-sink initialization)

## Purpose
Initializes a temporary wait-sink helper object used inside the restart-loop flow:
- writes vtable pointer at `this+0x00`
- zeros state field at `this+0x04`

## Notes
- This is a small local-object constructor helper, not the top-level level driver.
- Observed in the same restart-loop cluster as:
  - `CGame__RestartLoopRunLevel` (`0x0046dc30`)
  - `CGame__RunLevel` (`0x0046e240`)

