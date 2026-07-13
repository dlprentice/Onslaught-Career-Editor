# CController__GetToControl

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x0042e4d0` comment correction; `0x0046e910` comment correction. Older conflicting text below is superseded for these rows. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

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
