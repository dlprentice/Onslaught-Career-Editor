# CBattleEngineJetPart__Move

> Address: `0x00410c50` | Prior saved Ghidra name: `CMonitor__UpdateMovementTransitionAndEffects`

## Status

- Current static owner/source identity: high confidence
- Saved live Ghidra correction: pending separate mutation baton
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

- The saved Ghidra owner, signature parameter, and comment are still stale.
- Source constants remain hypotheses until copied-runtime measurement.
- This does not establish authentic handling, timing, camera, animation,
  presentation, or rebuild parity.
- No executable or installed-game file was changed.
