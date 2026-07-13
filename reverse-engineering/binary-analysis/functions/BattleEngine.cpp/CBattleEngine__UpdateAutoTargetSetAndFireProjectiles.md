# CBattleEngine__HandleLocks

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x00406560` → `CBattleEngine__HandleLocks` (was `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`). Older conflicting text below is superseded for these rows. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Address: `0x00406560` | Source family: `references/Onslaught/BattleEngine.cpp`
> The legacy filename is retained so historical links do not break.

## Status

- Current live-Ghidra name: stale (`CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`)
- Revalidated static identity: `CBattleEngine__HandleLocks`
- Evidence: fresh final-snapshot metadata, xrefs, instructions, decompile, and
  direct source-shape comparison
- Runtime behavior proof: not established

## Summary

Source-aligned BattleEngine lock-maintenance and acquisition helper. It is
called from `CBattleEngine__Move` with the BattleEngine pointer in `ECX` and no
explicit stack arguments. The body selects the active JetPart or WalkerPart
weapon, prunes null, dying, or out-of-deflection entries from the lock set at
`+0x294`, enforces weapon readiness and maximum-lock gates, and handles direct,
proximity, and sequence lock modes.

## Interpretation

The old projectile interpretation came from inherited dependent helper labels.
Raw call shapes inside this body pass target, lock time, and a direct-lock flag
to the helper currently named `CBattleEngine__AddProjectile`; those arguments
and the surrounding source order identify that callee as lock-entry creation in
this context. The direct caller position and full body align with
`CBattleEngine::HandleLocks` in Stuart's source.

## Boundaries

- Static identity and ABI evidence only.
- The live Ghidra project has not been renamed under this read-only lane.
- Dependent helper names and concrete layouts remain subject to bounded review.
- No runtime target acquisition, firing, gameplay, patch behavior, or rebuild
  parity is claimed.
