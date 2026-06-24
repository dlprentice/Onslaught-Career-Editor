# God Mode Mechanism Follow-up (Wave 4)

Date: 2026-03-29
Mode: offline repo analysis only (saved decomp + source snapshot; no live debugger)

## Confirmed Path

The Steam-build pause toggle path is concretely visible in saved decomp:

- `CPauseMenu__ButtonPressed` at `0x004d0810`
- cheat-gated item IDs:
  - `0x148fe9`
  - `0x226f16`
- toggle handler:
  - `0x148fe9 -> 0x226f16`, then `CEngine__SetOptionValueAndNotifyTarget(DAT_008a9d3c, 0, ...)`
  - `0x226f16 -> 0x148fe9`, then `CEngine__SetOptionValueAndNotifyTarget(DAT_008a9d3c, 1, ...)`

Saved decomp anchor:
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-27/pass2_semantic_wave126_prep/decomp_caller_probe_b/004d0810_CPauseMenu__ButtonPressed.c`

The target helper decomp at `0x004d3020` shows:

- it stores the new option value,
- writes it into a career-backed option slot,
- and then notifies a target object through **two** vtable calls with complementary booleans.

Saved decomp anchor:
- `reverse-engineering/binary-analysis/scratch/deep_semantic_tail_2026-02-27/pass2_semantic_wave146/verify_decomp/004d3020_CEngine__SetOptionValueAndNotifyTarget.c`

## Strong Mechanism Interpretation

This looks like a Steam-build split replacement for the internal/source `CPlayer::SetIsGod()` path rather than a direct one-call wrapper.

Internal/source behavior:

- `CPlayer::SetIsGod(TRUE)` calls:
  - `mBattleEngine->SetVulnerable(FALSE)`
  - `mBattleEngine->SetInfinateEnergy(TRUE)`
- `CPlayer::SetIsGod(FALSE)` calls the inverse pair.

Source anchors:
- `references/Onslaught/Player.cpp`
- `references/Onslaught/BattleEngine.cpp`
- `references/Onslaught/BattleEngine.h`

## Why This Fits The Observed Steam Behavior

Observed live behavior:

- normal combat damage is blocked when `God ON`
- toggling back on refills shields
- already-lost hull is not repaired

The source-side damage logic explains most of this cleanly:

- `CBattleEngine::Damage()` snapshots life/shields/energy at entry
- if `mVulnerable == FALSE`, it restores those pre-hit values at the end
- therefore future hits do not stick
- but already-lost hull is not automatically healed just because invulnerability was turned back on later

That matches the user's hull observation very well.

## Why Shield Refill Is Probably Not A Simple Full-Heal Call

Source-side `SetInfinateEnergy(TRUE)` only forces energy to max directly.
It does **not** directly set hull.

However, walker-part shield recharge logic includes:

- `mShieldsRecharging = TRUE`
- `mMainPart->mShields = mMainPart->mEnergy`

That means a Steam-build path that reenables invulnerability and maxes/maintains energy can plausibly produce rapid or immediate shield refill without implying a full life/hull heal.

This is a strong fit for the live result:

- shield refill yes
- pre-existing hull repair no

## Current Confidence

High confidence:

- `Maladim` works
- pause-menu toggle path is real
- the toggle changes combat damage behavior
- pre-existing hull loss is not repaired by merely turning god mode back on

Moderate confidence / inference:

- the Steam build is still using a split runtime path closely analogous to source `SetVulnerable` + `SetInfinateEnergy`
- the observed shield refill is likely mediated by energy/shield recharge interaction rather than a direct full-heal call

Still open:

- exact identity of the two target vfuncs reached from `0x004d3020`
- whether water/environmental death still bypasses the effect in the current Steam-build pass
