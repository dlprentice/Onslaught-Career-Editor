# BattleEngine God-Mode Source Bridge - 2026-05-07

## Summary

This pass adds a public-safe verifier for the current god-mode mechanism bridge.

The source `CPlayer::SetIsGod` path toggles BattleEngine vulnerability and infinite-energy state. Existing Steam-build docs and binary function notes show a cheat-gated `Maladim` pause-menu toggle, a visible `God OFF` / `God ON` state, combat-damage behavior evidence, and the Unit damage-handler vulnerability bridge.

This is partial mechanism evidence only. It does not prove a single direct Steam-build `CPlayer::SetIsGod` call path, exact source-to-retail identity for `CPlayer::SetIsGod`, the runtime vfunc notification boundary, environmental hazard behavior, or rebuild parity.

## Current Status Update

This evidence supports partial retail candidate accounting for one selected source anchor:

- `player_god_mode_toggles`

Latest source-to-binary gap baseline:

- `npm run test:battleengine-source-binary-gap`: PASS, binary families `3/3`, source anchors `17/17`.
- The current source-only pending-binary-identity count is `6`.
- The current partial retail candidate count is `11`: four damage anchors, three Morph event/energy-gate anchors, player god-mode toggles, configuration defaults, target-lock behavior, and augmented-weapon activation/depletion.

## Commands Run

| Command | Result | Important Output |
| --- | --- | --- |
| `cmd.exe /c npm run test:battleengine-god-mode-source-bridge` before token correction | FAIL / expected red | Groups `2/4`; caught mismatched source signature and Unit boundary token. |
| `py -3 -m py_compile tools\battleengine_god_mode_source_bridge_probe.py tools\battleengine_source_binary_gap_probe.py` | PASS | No compiler output. |
| `cmd.exe /c npm run test:battleengine-god-mode-source-bridge` | PASS | Groups `4/4`: source player toggle, Steam runtime mechanism note, pause-menu binary note, and Unit damage binary note. |

## What This Proves

- Source `Player.cpp` contains the checked `SetIsGod` vulnerability and infinite-energy toggles.
- Steam-build god-mode docs record the `Maladim` menu/effect evidence and the non-exact-mechanism boundary.
- Binary function notes record the pause-menu gating/toggle state and the Unit damage-handler vulnerability bridge.
- The source-to-binary gap probe can treat `player_god_mode_toggles` as partial mechanism evidence instead of pure source-only evidence.

## What Is Not Proven

- Exact source-to-retail identity for `CPlayer::SetIsGod`.
- A single direct Steam-build `SetIsGod` call path.
- The exact runtime vfunc notification boundary for the toggle.
- Environmental hazard behavior while god mode is enabled.
- Ghidra mutation, runtime replay, or rebuildable gameplay parity.

## Private Evidence Policy

This report does not include source excerpts, binaries, private absolute paths, runtime captures, screenshots, frame data, Ghidra project files, or mutation logs.
