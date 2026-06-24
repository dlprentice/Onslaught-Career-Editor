# BattleEngine Morph Event Read-Back - 2026-05-06

## Summary

This pass adds a public-safe read-back probe for the strongest current retail bridge into the source `CBattleEngine::Morph()` transform branch.

The probe compares source Morph anchors with the current decompile of `CMonitor__UpdateFlightWalkerTransitionState` at `0x0040a580`. That retail helper contains both transform event IDs, both transition helpers, both transition animation strings, the reader-swap helper, a state gate, and an energy-gate token. This makes it a stronger candidate bridge for the source Morph branch than string xrefs alone.

This remains bounded evidence. It does not claim complete source-to-retail identity for the full `CBattleEngine::Morph()` body, final owner/name correctness for `0x0040a580`, or runtime behavior in a running mission.

## Current Status Update - 2026-05-07

This evidence now supports partial retail candidate accounting for three selected transform source anchors:

- `transform_morph_method_anchor`
- `transform_jet_to_walker_event`
- `transform_walker_to_jet_energy_gate`

`release/readiness/battleengine_transform_special_move_candidate_2026-05-07.md` later adds bounded transition-lockout candidate evidence for `transform_reject_special_moves`.

Latest source-to-binary gap baseline:

- `npm run test:battleengine-source-binary-gap`: PASS, binary families `3/3`, source anchors `17/17`.
- The current source-only pending-binary-identity count is `3`.
- The current partial retail candidate count is `14`: four damage anchors, transform special-move lockout, three Morph event/energy-gate anchors, two jet energy/stall anchors, configuration defaults, player god-mode toggles, target-lock behavior, and augmented-weapon activation/depletion.

This is transform transition-helper and transition-lockout bridge evidence only. The checked source anchors and `CMonitor__UpdateFlightWalkerTransitionState` read-back evidence are related, but complete `CBattleEngine::Morph()` source-to-retail identity and runtime transform behavior remain unresolved.

## Traceability

- Branch: `wip/sandbox`
- Implementation commit: `2269913455776d4dfbad003e3e4a7d170c0bdf5e`
- Traceability commit: `58e74ee97b8f2de2657630500393a79a599d73ac`

## Inputs

- Source anchor: `references/Onslaught/BattleEngine.cpp`
- Retail decompile input: `subagents/transition-hud-helper-ghidra-readback/current/decompile/0040a580_CMonitor__UpdateFlightWalkerTransitionState.c`
- Read-only headless export scratch: `subagents/battleengine-morph-readback/current/decompile/`
- Probe output: `subagents/battleengine-morph-event-readback/current/battleengine-morph-event-readback.json`

## Commands Run

| Command | Result | Important Output |
| --- | --- | --- |
| `powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& '<Ghidra>\support\analyzeHeadless.bat' '<Ghidra projects>' 'BEA' -process 'BEA.exe' -scriptPath '<repo>\tools' -postScript 'ExportFunctionsByPrefixDecompile.java' '<repo>\subagents\battleengine-morph-readback\current\decompile' 'CBattleEngine__' '90' -noanalysis"` | PASS | Exported 36 current `CBattleEngine__*` decompiles with 0 failures. Headless reported a project save after the read-only decompile export. |
| `py -3 tools/battleengine_morph_event_readback_probe.py --check` | PASS | Groups 2/2: source Morph branch and retail transition event bridge. |

## What This Proves

- Source `CBattleEngine::Morph()` carries the checked event, energy-gate, state, and animation-string anchors.
- Current retail read-back for `CMonitor__UpdateFlightWalkerTransitionState` carries matching event IDs, transition helpers, animation strings, reader-swap, state-gate, and energy-gate tokens.
- `0x0040a580` is now the best current public-safe candidate bridge for the source Morph transform branch.

## What This Does Not Prove

- Complete source-to-retail identity for the full `CBattleEngine::Morph()` body.
- Correct final owner/name for `0x0040a580`.
- Runtime transform behavior in a running mission.
- Ghidra rename-map mutation or read-back.
- Rebuildable gameplay parity.

## Safety

- Did not launch BEA.exe.
- Did not mutate the installed game, copied profiles, or any executable.
- Did not apply a Ghidra rename map or other intentional Ghidra mutation.
- Did not commit private assets, raw proof JSON, screenshots, frames, or local game-path contents.
