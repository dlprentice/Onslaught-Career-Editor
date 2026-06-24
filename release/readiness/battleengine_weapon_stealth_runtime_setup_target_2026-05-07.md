# BattleEngine Weapon-Stealth Runtime Setup Target - 2026-05-07

Status: public-safe setup-target evidence, not runtime proof

## Objective

Identify a practical copied-profile runtime setup target for the remaining `weapon_fire_breaks_stealth` source-only anchor.

The runtime question is still:

```text
In the Steam retail build, when the player is cloaked and fires a weapon, does the live runtime clear or visibly break stealth?
```

This note does not launch the game, patch an executable, mutate a save, or prove the behavior. It narrows the later runtime proof to mission states that already carry cloak-specific script/text evidence.

## Preferred Setup Target

Use `level710` as the first copied-profile runtime candidate.

Tracked mission evidence shows `Level710script.msl` uses cloak-specific player-facing text:

- `AddHelpMessage` with `_710_J_CLOAK`.
- `PlayCharMessage` from `P_TATIANA` with `_710_CLOAK`.

Tracked language evidence maps `_710_CLOAK` to Tatiana telling the player that Aquila has been fitted with a cloaking device and that the Special Function button activates it. The generated full-install language catalog also contains `_710_J_CLOAK` help text for toggling cloak.

This makes `level710` the strongest current setup candidate because the mission itself teaches cloak activation instead of merely referencing enemy cloak or stealth events.

## Fallback Clue Levels

If `level710` cannot be reached or controlled reliably in a copied-profile proof, the next static clues are:

- `level611` / `level612`: mission event index contains `Cloaked`, and language rows include `_612_CARVER_CLOAKED`.
- `level621` / `level622`: mission event index contains `Stealth`.

These are weaker fallback candidates. They may refer to enemy behavior or mission scripting rather than player cloak availability, so they should not be used for a player-fire stealth claim unless runtime capture proves the player can cloak and fire in that state.

## Runtime Proof Implication

The next runtime wave should treat setup as a gated step:

1. Prepare a copied profile from read-only installed game material.
2. Apply `force_windowed` only to the copied `BEA.exe` if needed for capture/input.
3. Launch the managed copied profile.
4. Reach `level710` or another documented cloak-capable state.
5. Capture cloak-active baseline.
6. Send one bounded weapon-fire input to the managed BEA window.
7. Capture the after-fire state.
8. Stop the managed process and prove no `BEA.exe` remains.

The public result can only claim the observed behavior class if the private captures show the player was actually cloaked before firing.

## Not Claimed

- This note is not runtime proof.
- This note does not launch BEA.
- This note does not mutate the installed game, original `BEA.exe`, original saves, or Ghidra projects.
- This note does not prove that `level710` is the fastest setup path.
- This note does not prove the exact retail function identity for `CBattleEngine::WeaponFired`.
- This note does not prove that firing breaks stealth across every mission, weapon, or player state.

## Privacy / Release Safety

This note is public-safe. It contains tracked mission/text keys, sanitized setup reasoning, and proof boundaries only. It does not include private screenshots, copied saves, copied executables, raw captures, local absolute paths, media cache paths, debugger logs, or raw runtime proof JSON.
