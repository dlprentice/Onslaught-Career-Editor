# BattleEngine Cloak Input Binding Triage - 2026-05-08

Status: public-safe input binding correction, not runtime proof

## Objective

Correct the next copied-profile cloak probe setup before sending more runtime input.

The previous helper note added a named `BACKSLASH` token, and the first runtime observer wave sent `tap:TAB`. This triage checks the current `defaultoptions.bea` binding evidence instead of relying on a tutorial-text assumption.

## Evidence

The repo options decoder was run against:

- the ignored copied-profile `defaultoptions.bea` used by the prior runtime probe,
- the operator's current installed `defaultoptions.bea`, read only.

Both decoded the same active binding for entry `0x3B` / `Others: Special function`:

| Slot | Binding |
| --- | --- |
| P1 | `RShift` |
| P2 | `Tab` |

The static control-binding map already identifies UI action `0x4C` as `entry_id 0x3B`, binding type `8`, and AppCore exposes the same row as `Special function`.

## Change

`tools/send_game_window_input.ps1` now exposes exact left/right modifier tokens:

- `LSHIFT`
- `RSHIFT`
- `LCTRL`
- `RCTRL`

This keeps scoped input bounded to named keys while allowing the next copied-profile proof to send the exact `RShift` scan code stored in the active options file. The older `BACKSLASH` helper token remains available as a named physical key, but it is not the current decoded default cloak binding for this profile.

## Proof Boundary

This pass does not prove that cloak activates, that `Tab` is sufficient, that `RShift` is sufficient, or that firing while cloaked breaks stealth. It only proves the next runtime wave should not treat backslash as the current default binding and should test the decoded `Special function` bindings before any weapon-fire input.

## Validation

| Command | Result | Summary |
| --- | --- | --- |
| `py -3 tools\send_game_window_input_test.py` | PASS | PrintOnly parsing accepts `RSHIFT`, `LSHIFT`, `RCTRL`, and `LCTRL` with expected scan-code metadata. |

## Privacy / Release Safety

This report is public-safe. It records binding labels, repo-relative tool names, and proof boundaries only. It does not include full local paths, copied executables, copied saves/options files, screenshots, raw debugger logs, captures, or private proof JSON.
