# CMonitor__Process (Superseded Name)

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x004081c0` → `CBattleEngine__Move` (was `CMonitor__Process`). Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Address: `0x004081c0` | Current static identity: `CBattleEngine__Move`

## Status

The saved Ghidra name and this historical path are superseded. A 2026-07-12
read-only re-review identified the `CBattleEngine` RTTI vtable at `0x005d89c4`;
slot 66 at `0x005d8acc` points to this function. Constructor, field, caller,
callee, and source-order evidence independently agree with
`CBattleEngine::Move`.

Use [CBattleEngine__Move](../BattleEngine.cpp/CBattleEngine__Move.md) and the
[movement static crosswalk](../../battleengine-movement-static-crosswalk-2026-07-12.md)
as current authority.

## Historical Note

The May 2026 signature/comment waves accurately recorded the then-saved name
and selected body tokens, but their Monitor owner interpretation was wrong.
Those reports remain history rather than current semantic authority.

## Boundaries

- The live Ghidra project has not yet been renamed or retyped.
- Static identity does not prove runtime timing, values, HUD/audio outcomes,
  controls, camera behavior, or rebuild parity.
- No executable or installed-game file was changed.
