# CController__GetToControl

> Address: `0x0042e4b0` | Source: `references/Onslaught/Controller.cpp:437`

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes (`void * CController__GetToControl(void *this)`)
- **Verified vs Source:** Yes (high-confidence structural match to `CController::GetToControl()`)

## Purpose
Returns the current top-of-stack control target (`IController*`) for this controller.

## Behavior Summary
- Reads `mToControlStack.First()` from controller storage.
- Caches the stack-head pointer in a temporary/iterator slot.
- Returns `First()->ToRead()` when present, else returns null.

## Typical Call Sites
- `CGame__Update` (`0x0046e910`) pause/unpause/control-handoff checks.
- `CController__SendButtonAction` (`0x0042e4d0`) dispatch target resolution path.
