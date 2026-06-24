# BattleEngine Weapon-Fire Source Path Probe - 2026-05-07

Status: public-safe source-path triage, not retail identity or runtime proof

## Objective

Clarify the source-visible weapon-fire path before using copied-profile runtime work to answer the remaining `weapon_fire_breaks_stealth` gap.

This pass asks a narrow source question:

```text
What path is visible in Stuart's source from player fire input to weapon firing, and where does the source checkout stop exposing implementation detail?
```

## Command

```powershell
npm run test:battleengine-weapon-fire-source-path
```

Equivalent direct command:

```powershell
py -3 tools\battleengine_weapon_fire_source_path_probe.py --check
```

## Result

```text
BattleEngine weapon-fire source path probe
Status: pass
Token checks: 13
WeaponFired files: 6
WeaponFired occurrences: 8
Weapon source dependency: referenced but not present in this checkout
```

## What This Proves

- The source-visible input path includes `BUTTON_MECH_FIRE_GUN_POD` calling `CBattleEngine::FireWeapon()`.
- `CBattleEngine::FireWeapon()` delegates to the walker or jet part based on current state.
- The walker and jet part fire paths call `weapon->Fire()` on the current active weapon.
- The source-visible cloak input path includes `BUTTON_MECH_CLOAK` calling `CBattleEngine::HandleCloak()`.
- The source-visible `CBattleEngine::WeaponFired(...)` wrapper still clears `mStealth` after either jet or walker part recognizes the fired weapon.
- The checked source tree still has the expected `8` `WeaponFired` symbol occurrences and no broader direct source callsite.
- `Weapon.h` is included by the visible BattleEngine source files, but `Weapon.h` / `Weapon.cpp` are not present in this checkout, so this source pass cannot inspect the `CWeapon::Fire()` callback or ownership boundary.

## What This Does Not Prove

- This does not prove exact Steam retail binary identity for `CBattleEngine::WeaponFired`.
- This does not prove whether retail calls, inlines, removes, or reorganizes the source-visible stealth reset.
- This does not prove live runtime behavior after firing while cloaked.
- This does not prove every weapon path, lock-on path, charge path, or projectile path.
- This does not mutate Ghidra, apply a rename map, patch `BEA.exe`, launch the game, or inspect private runtime evidence.
- This does not make the repository rebuildable from scratch.

## Outcome

The source-visible path supports the runtime-proof plan at `release/readiness/battleengine_weapon_stealth_runtime_proof_plan_2026-05-07.md`: the key player-visible question is now better framed as a copied-profile behavior probe, because the available source checkout reaches `weapon->Fire()` but does not expose the weapon implementation needed to prove the callback path from source alone.

Future static work should be narrower than another broad name/operand scan. Useful candidates are:

- source/reference recovery for the missing `Weapon.h` / `Weapon.cpp` implementation,
- retail xrefs around the `CWeapon::Fire()` implementation if its owner can be identified,
- or copied-profile runtime proof of whether firing while cloaked breaks stealth.

Follow-up read-back at `release/readiness/battleengine_weapon_fire_candidate_readback_2026-05-07.md` rules out the obvious currently named retail `CWeapon` candidates at `0x00505f70` / `0x00505f90` as the missing fire callback because they are shutdown/destructor-like.

## Privacy / Release Safety

This report is public-safe. It contains only source-symbol names, sanitized counts, repo-relative paths, and proof boundaries. It does not include source excerpts, binaries, private absolute paths, screenshots, frame data, copied executables, copied saves, debugger logs, Ghidra mutation logs, or raw runtime proof JSON.
