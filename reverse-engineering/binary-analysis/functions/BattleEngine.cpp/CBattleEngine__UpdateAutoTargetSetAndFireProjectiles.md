# CBattleEngine__HandleLocks

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x00406560` → `CBattleEngine__HandleLocks` (was `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`). Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Address: `0x00406560` | Source family: `references/Onslaught/BattleEngine.cpp`
> The legacy filename is retained so historical links do not break.

## Status

- Current live-Ghidra name: `CBattleEngine__HandleLocks` (applied and exactly
  read back on 2026-07-13)
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
- The confirmed live Ghidra name/comment correction was applied under the
  bounded 2026-07-13 mutation lease.
- Dependent helper names and concrete layouts remain subject to bounded review.
- No runtime target acquisition, firing, gameplay, patch behavior, or rebuild
  parity is claimed.
