# GameControllers__RelinquishControlForTarget

> Address: `0x004cdd70`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void __fastcall GameControllers__RelinquishControlForTarget(void * controlled_target)`)
- **Verified vs Source:** No exact Stuart source method identified; source confirms the underlying controller stack helpers.

## Purpose
Releases any player controller whose current top control target matches the supplied `controlled_target`.

## Behavior Summary
- Treats `ECX` as the target `IController`/control receiver pointer.
- Iterates controller slots `0` and `1` through the global `CGame` singleton.
- For each non-null controller, calls `CController__GetToControl`.
- If the current top control target equals `controlled_target`, calls `CController__RelinquishControl` on that controller.

## Evidence
- `0x004cdd72` moves `ECX` into `EDI`; no stack parameters are read.
- Calls `CGame__GetController(&DAT_008a9a98, number)` at `0x004cdd7c`, `0x004cdd8b`, and `0x004cdda1`.
- Calls `CController__GetToControl` at `0x004cdd92`, compares the result with `EDI`, then calls `CController__RelinquishControl` at `0x004cdda8`.
- Confirmed callers include `CMessageLog__HandleInputCommand` and a raw close/back handler at `0x0048ffcc`.

## Limits
Static retail-binary evidence only. Exact source identity, concrete target type, runtime input/menu behavior, and rebuild parity remain unproven.
