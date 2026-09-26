# CPlayer__SetIsGod

Status: renamed function note; the pre-audit notes below are leads
Last updated: 2026-09-26 (renamed from `CEngine__SetOptionValueAndNotifyTarget` by the RE record audit)
Summary: `0x004d3020` is `CPlayer::SetIsGod(value)` (`Player.cpp:221-243`): it stores the god flag in the player and
the career, updates the Battle Engine through its vtable and counts a cheat. The current contract is
[god mode](../../../game-mechanics/god-mode.md); the rename is in [the second label cohort](../../../ghidra/README.md#re-audit-label-corrections-second-cohort--september-26). The notes below were written under the
former label.

> Source File: `references/Onslaught/Player.cpp:221-243` (the pre-audit note said engine.cpp) | Binary: BEA.exe
> Wave: 486 | Evidence: saved Ghidra metadata, decompile, xrefs, instruction rows, raw-caller rows, tags, and focused probe

## Function

| Address | Name | Saved signature |
| --- | --- | --- |
| `0x004d3020` | `CPlayer__SetIsGod` | `void __thiscall CPlayer__SetIsGod(void * this, int option_value)` |

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
