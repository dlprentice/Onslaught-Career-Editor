# CBattleEngine__Move

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x004081c0` → `CBattleEngine__Move` (was `CMonitor__Process`). Older conflicting text below is superseded for these rows. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Address: `0x004081c0` | Prior saved Ghidra name: `CMonitor__Process`

## Status

- Current static owner/source identity: high confidence
- Saved live Ghidra correction: pending separate mutation baton
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

- The saved Ghidra name/signature/comment are still stale.
- Exact field types and final ABI labels are not yet applied.
- Static identity does not prove retail timing, values, camera, controls, or
  gameplay behavior.
- No executable or installed-game file was changed.
