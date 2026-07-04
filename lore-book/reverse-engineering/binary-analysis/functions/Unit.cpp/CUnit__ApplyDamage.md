# CUnit__ApplyDamage

> Address: 0x004f9a90 | Source owner: Unit.cpp family | Wave835 static read-back

## Status

- **Saved Ghidra name:** `CUnit__ApplyDamage`
- **Saved Ghidra signature:** `void __thiscall CUnit__ApplyDamage(void * this, float damage_amount, void * damage_source, int apply_shields, int mesh_part_index)`
- **Latest correction:** Wave835 CUnit ApplyDamage (`cunit-apply-damage-wave835`, `wave835-readback-verified`)
- **Read-back evidence:** `release/readiness/ghidra_cunit_apply_damage_wave835_2026-05-25.md`

## Purpose

`0x004f9a90 CUnit__ApplyDamage` is important shared CUnit damage/lifetime infrastructure, not throwaway tail code. Wave835 corrected the stale two-argument Ghidra signature to the four explicit stack arguments proven by `RET 0x10` at `0x004fa4a7` and direct callsite pushes at `0x004037be`, `0x00417a16`, `0x0048006d`, and `0x004898b0`.

## Static Evidence

The body is reached by `19 DATA` slot pointers: `0x005dd828`, `0x005dfa38`, `0x005dfddc`, `0x005e002c`, `0x005e027c`, `0x005e0724`, `0x005e0980`, `0x005e0bd0`, `0x005e1080`, `0x005e1530`, `0x005e1c24`, `0x005e232c`, `0x005e257c`, `0x005e2a1c`, `0x005e3114`, `0x005e3374`, `0x005e3de0`, `0x005e403c`, and `0x005e4298`.

Observed static behavior:

- Resets `CUnit__ResetDamageCooldownTimer` through `this+0x148` when source flags/owner flags match.
- Scales positive damage by profile/state fields and repairs health-like `this+0xf8` for non-positive damage.
- Applies nexus and weakpoint mesh-part gates using `s_nexus_00633af4` and `s_weakpoint_00633ae8`.
- Forwards segment damage to `CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold` when `this+0x178` exists.
- Otherwise applies shield-like `this+0x100` before life-like `this+0xf8`, then dispatches death/cleanup vfuncs when life falls below zero.
- Emits a particle effect when the profile effect pointer is present.
- Queues profile/Tara/Billy damage text through `CMessageBox` with Unit.cpp debug allocation path `0x00633b6c`, line token `0x44d`.

## Queue Context

Post-Wave835 queue telemetry: `6098` total functions, `5657` commented, `441` commentless, `0` exact-undefined signatures, `0` `param_N`, strict clean-signature proxy `5657/6098 = 92.77%`. The next raw commentless row is `0x004fa4b0 CUnit__SmoothEulerTowardTargetAndBuildMatrix`; commentless high-signal, signature, and name-confidence queues remain empty.

Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-003658_post_wave835_cunit_apply_damage_verified`.

## Boundaries

- Does not prove exact Unit.cpp source body identity.
- Does not prove concrete `CUnit`, profile, damage-source, segment, message, or effect layouts beyond observed offsets.
- Does not prove runtime damage, shield, death, particle, or message behavior.
- Does not prove exact player/god-mode behavior.
- Does not mutate `BEA.exe`, saves, private assets, or the installed game.
- Does not prove rebuild parity.

## Related Functions

- `0x004e6660 CUnit__ResetDamageCooldownTimer`
- `0x00444030 CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold`
- `0x004fe030 CUnit__TriggerEffect`
- `0x004fd140 CUnit__MarkDestroyedAndCleanupLinks`
- `0x004fa4b0 CUnit__SmoothEulerTowardTargetAndBuildMatrix`
