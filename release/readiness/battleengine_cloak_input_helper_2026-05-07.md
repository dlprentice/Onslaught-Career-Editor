# BattleEngine Cloak Input Helper - 2026-05-07

Status: public-safe helper hardening, not runtime proof

## Objective

Prepare the scoped input helper for a later copied-profile cloak/fire runtime proof without sending live input in this wave.

The `level710` mission text names the cloak action as `Special Function`. A later binding triage corrected the active input target: the current decoded `defaultoptions.bea` binding for `Special function` is `P1=RShift` and `P2=Tab`, not backslash. See `release/readiness/battleengine_cloak_input_binding_triage_2026-05-08.md`.

## Change

`tools/send_game_window_input.ps1` now allows:

- `tap:BACKSLASH`
- `down:BACKSLASH`
- `up:BACKSLASH`
- `tap:RSHIFT`
- `tap:LSHIFT`
- `tap:RCTRL`
- `tap:LCTRL`

The backslash mapping uses virtual key `0xDC` and scan code `0x2B`, matching the standard US keyboard backslash/OEM-5 physical key. The modifier mappings preserve left/right scan-code identity for runtime probes that need the exact active options binding.

This is deliberately a named key addition, not a generic arbitrary virtual-key escape hatch.

## Validation

| Command | Result | Summary |
| --- | --- | --- |
| `py -3 tools\send_game_window_input_test.py` | PASS | PrintOnly parsing accepts `tap:BACKSLASH,wait:250,click:320x240`, the left/right modifier aliases, and rejects an unsupported `tap:OEM_5` alias. |

## Not Claimed

- This note does not send input to BEA.
- This note does not launch BEA.
- This note does not mutate the installed game, original `BEA.exe`, original saves, or Ghidra projects.
- This note does not prove that backslash toggles cloak in Steam retail.
- This note does not prove that `RShift` or `Tab` toggles cloak in Steam retail.
- This note does not prove that firing while cloaked breaks stealth.

## Privacy / Release Safety

This note is public-safe. It contains helper behavior, validation command names, and proof boundaries only. It does not include local absolute paths, screenshots, copied executables, copied saves, raw captures, debugger logs, or raw runtime proof JSON.
