# BattleEngine Level Launch Helper - 2026-05-07

Status: public-safe helper hardening, not runtime proof

## Objective

Make the copied-profile launch helper capable of targeting a known mission for later runtime proofs without opening the broader retail/debug command line.

The immediate need is the weapon-stealth proof setup target: `level710`.

## Change

`tools/start_game_profile.ps1` now accepts:

- `-skipfmv`
- `-forcewindowed`
- `-level <numeric mission id>`

The `-level` value must be an integer from `1` through `9999`. Non-numeric values, missing values, bare values, and unallowlisted flags such as `-devmode` are rejected.

This keeps the helper narrow enough for copied-profile runtime proof work while allowing a later operator-controlled run to start near the cloak tutorial target.

## Validation

| Command | Result | Summary |
| --- | --- | --- |
| `py -3 tools\start_game_profile_test.py` | PASS | Exercises PrintOnly allow/reject behavior against a temporary fake game root: `-skipfmv -level 710` is allowed, missing/non-numeric `-level` values are rejected, and unallowlisted debug flags remain rejected. |

The helper also now forces split launch tokens into an array so single-token arguments such as `-skipfmv` are handled as whole tokens instead of being indexed as individual characters.

## Not Claimed

- This note does not launch BEA.
- This note does not mutate the installed game, original `BEA.exe`, original saves, or Ghidra projects.
- This note does not prove that `-level 710` reaches a fully cloak-capable state in Steam retail.
- This note does not authorize broad debug or development flags.
- This note does not prove the weapon-fired stealth runtime behavior.

## Privacy / Release Safety

This note is public-safe. It contains helper behavior, validation command names, and proof boundaries only. It does not include local absolute paths, screenshots, copied executables, copied saves, raw captures, debugger logs, or raw runtime proof JSON.
