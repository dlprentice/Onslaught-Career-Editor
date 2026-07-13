# CBattleEngine__Move

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x004081c0` → `CBattleEngine__Move` (was `CMonitor__Process`). Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Address: `0x004081c0` | Prior saved Ghidra name: `CMonitor__Process`

## Status

- Current static owner/source identity: high confidence
- Saved live Ghidra correction: applied and exactly read back on 2026-07-13
- Copied-runtime behavior proof: pending

## Static Basis

The `CBattleEngine` RTTI vtable at `0x005d89c4` points to this body from slot 66
at `0x005d8acc`. Neighboring slots resolve to known BattleEngine methods. The
body uses BattleEngine state and WalkerPart/JetPart fields, dispatches both
movement parts, and reaches BattleEngine and actor movement helpers in the same
broad order as Stuart's `CBattleEngine::Move` source.

See [the 2026-07-12 movement crosswalk](../../battleengine-movement-static-crosswalk-2026-07-12.md)
for the complete evidence and non-claims.

## Boundaries

- The corrected live Ghidra name/signature/comment match this page.
- The metadata correction does not prove exact field types or retail runtime
  behavior.
- Static identity does not prove retail timing, values, camera, controls, or
  gameplay behavior.
- No executable or installed-game file was changed.
