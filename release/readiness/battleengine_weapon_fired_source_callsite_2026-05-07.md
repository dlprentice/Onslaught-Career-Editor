# BattleEngine WeaponFired Source Callsite Probe - 2026-05-07

Status: public-safe source-tree triage, not retail identity proof

## Objective

Clarify the source-side shape of the remaining `weapon_fire_breaks_stealth` anchor before spending more static retail-binary effort on exact identity.

The source method is small and clear, but exact retail identity has stayed elusive. This pass checks whether Stuart's source tree contains a direct callsite for `WeaponFired` outside the definitions/declarations themselves.

## Commands

```powershell
py -3 -m py_compile tools\battleengine_weapon_fired_source_callsite_probe.py
npm run test:battleengine-weapon-fired-source-callsite
```

## Result

```text
BattleEngine WeaponFired source callsite probe
Status: pass
Occurrences: 8
Unexpected occurrences: 0
```

The checked source occurrences are:

- `BattleEngine.cpp`: `CBattleEngine::WeaponFired` definition
- `BattleEngine.cpp`: jet-part delegation inside `CBattleEngine::WeaponFired`
- `BattleEngine.cpp`: walker-part delegation inside `CBattleEngine::WeaponFired`
- `BattleEngine.h`: `CBattleEngine::WeaponFired` declaration
- `BattleEngineJetPart.cpp` / `.h`: jet-part helper definition/declaration
- `BattleEngineWalkerPart.cpp` / `.h`: walker-part helper definition/declaration

## What This Proves

- Stuart's source defines the weapon-fired stealth-reset behavior.
- The current checked source tree has no direct `WeaponFired` callsite outside the expected declarations/definitions and the two part-delegation calls inside `CBattleEngine::WeaponFired` itself.
- The lack of a direct source callsite explains why a one-to-one Steam retail method identity may not appear in current function-name, operand, or helper scans.

## What This Does Not Prove

- This does not prove Steam retail lacks weapon-fired stealth reset behavior.
- This does not prove exact Steam retail function body identity for `CBattleEngine::WeaponFired`.
- This does not prove whether retail removed, inlined, reorganized, or changed the source behavior.
- This does not prove runtime stealth behavior after firing a weapon.
- This does not mutate Ghidra, apply a rename map, patch `BEA.exe`, or run the game.
- This does not make the repository rebuildable from scratch.

## Outcome

`weapon_fire_breaks_stealth` remains source-only in aggregate source-to-binary gap accounting. Static work has now established three useful boundaries:

- no strict current Ghidra function-name match,
- no suspected stealth-field weapon/fire/projectile operand candidate,
- no direct source callsite outside the definitions/declarations.

The next high-value step is probably not more broad static name/operand scanning. It is either a narrower call-chain hypothesis from weapon object callbacks, or a copied-profile runtime probe that observes whether firing while cloaked clears stealth in the Steam retail build.

## Privacy / Release Safety

This report stores repo-relative source filenames, line-number summaries, command results, and proof boundaries only. It does not include binaries, private absolute paths, raw source excerpts beyond symbolic names, runtime captures, screenshots, copied executables, or mutation logs.
