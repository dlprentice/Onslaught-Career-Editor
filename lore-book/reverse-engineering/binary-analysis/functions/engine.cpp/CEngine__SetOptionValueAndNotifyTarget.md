# CEngine Option Value Notify Helper

> Source File: engine.cpp | Binary: BEA.exe
> Wave: 486 | Evidence: saved Ghidra metadata, decompile, xrefs, instruction rows, raw-caller rows, tags, and focused probe

## Function

| Address | Name | Saved signature |
| --- | --- | --- |
| `0x004d3020` | `CEngine__SetOptionValueAndNotifyTarget` | `void __thiscall CEngine__SetOptionValueAndNotifyTarget(void * this, int option_value)` |

## Evidence

- Wave486 corrected the stale two-stack-argument signature; instruction read-back shows one stack argument and `RET 0x4`.
- The helper stores `option_value` at `this+0x20`.
- It mirrors the value through a `this+0x2c` indexed global dword array at `0x00662ab0`.
- When target pointer `this+0x1c` is present, it dispatches target vfunc `+0xe0` with the inverse of `option_value == 1`.
- It then dispatches target vfunc `+0x154` with `option_value == 1`.
- It increments `this+0x3c` when `option_value` is nonzero.
- Xrefs include `CGame__RestartLoopRunLevel`, `CGameInterface__HandleMenuSelection`, `CPauseMenu__ButtonPressed`, `CGame__ReceiveButtonAction`, and raw no-function callers `0x004d113a` / `0x004d114a`.
- The raw no-function callers pass `0` or `1` through the same runtime options/god-toggle-adjacent path documented in `reverse-engineering/game-mechanics/god-mode.md`.

## Boundary

Static retail-binary evidence only. Exact owner/source identity, target vfunc identities, concrete layout, runtime god/options behavior, BEA launch behavior, game patching, and rebuild parity remain unproven.
