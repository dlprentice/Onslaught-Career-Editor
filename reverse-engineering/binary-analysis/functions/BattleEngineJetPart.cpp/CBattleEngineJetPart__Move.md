# CBattleEngineJetPart__Move

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x00410c50` → `CBattleEngineJetPart__Move` (was `CMonitor__UpdateMovementTransitionAndEffects`). Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Address: `0x00410c50` | Prior saved Ghidra name: `CMonitor__UpdateMovementTransitionAndEffects`

## Status

- Current static owner/source identity: high confidence
- Saved live Ghidra correction: applied and exactly read back on 2026-07-13
- Copied-runtime behavior proof: pending

## Static Basis

`CBattleEngine__Move` calls this body through the JetPart stored at BattleEngine
`+0x57c`; initialization and constructor evidence independently establish that
object relationship and the JetPart main-part backpointer at `+0x18`. The body
sequence matches Stuart's JetPart movement method across energy use, engine
state, stall/morph, ground effect, flight motion, auto-return, shield clearing,
particle effects, and skimming.

See [the 2026-07-12 movement crosswalk](../../battleengine-movement-static-crosswalk-2026-07-12.md)
for the complete child-helper map and non-claims.

## Boundaries

- The corrected live Ghidra owner, rendered signature parameter, and comment
  match this page.
- Source constants remain hypotheses until copied-runtime measurement.
- This does not establish authentic handling, timing, camera, animation,
  presentation, or rebuild parity.
- No executable or installed-game file was changed.
