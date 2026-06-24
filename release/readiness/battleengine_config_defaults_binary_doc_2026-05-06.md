# BattleEngine Config Defaults Binary-Doc Probe

Status: public-safe reverse-engineering evidence
Date: 2026-05-06
Branch: `wip/sandbox`
Source head before pass: `17762fef`
Evidence-report commit: 17bd53e987da2bc53ab336436e70f6974b90743f

## Purpose

This pass adds a narrow read-only bridge from the BattleEngine source defaults anchor to existing binary documentation for the function now saved as `CBattleEngineData__Initialise`. It checks that selected source default tokens and corresponding binary-doc float/hex tokens are both present.

No game runtime, Ghidra mutation, executable patching, installed-game access, source excerpt export, or binary read occurred in this pass.

## Current Status Update - 2026-05-07

This evidence now supports partial retail candidate accounting for the `config_defaults` source anchor.

Latest source-to-binary gap baseline:

- `npm run test:battleengine-source-binary-gap`: PASS, binary families `3/3`, source anchors `17/17`.
- The current source-only pending-binary-identity count is `14`.
- The current partial retail candidate count is `3`: configuration defaults, target-lock behavior, and augmented-weapon activation/depletion.

This is value-level bridge evidence only. The checked source and binary-doc value tokens align for selected defaults, but exact Steam retail function body identity for each source default field still requires a later direct retail-binary/decompile/read-back pass.

## Command

```powershell
npm run test:battleengine-config-defaults-binary-doc
```

Equivalent direct command:

```powershell
py -3 tools\battleengine_config_defaults_binary_doc_probe.py --check
```

Working directory:

```text
repo root
```

Result: PASS.

Important output summary:

```text
BattleEngine config defaults binary-doc probe
Status: pass
Anchors: 4/4
- PASS: energy_default
- PASS: max_air_energy_cost_default
- PASS: min_transform_energy_default
- PASS: shield_efficiency_default
```

## What This Proves

- The source reference and existing binary docs both contain matching value tokens for selected BattleEngine configuration defaults.
- The checked values are energy default, max air-energy cost default, minimum transform energy default, and shield-efficiency default.
- The aggregate gap probe can treat this anchor as partial retail candidate evidence instead of pure source-only evidence.
- The generated JSON report is ignored/private under `subagents/` and contains repo-relative filenames, token names, line numbers, and pass/fail state only.

## What This Does Not Prove

- Exact Steam retail function body identity for each source default field.
- Fresh Ghidra decompile/read-back for these constants.
- Runtime gameplay-state interpretation.
- Rebuildable implementation parity.

## Privacy / Release Safety

The committed evidence is public-safe. It does not include source excerpts, binaries, private absolute paths, runtime captures, screenshots, private assets, or Ghidra mutation logs.

The raw JSON report remains ignored local evidence under `subagents/battleengine-config-defaults-binary-doc/`.

## Recommended Next Step

Use this as one value-level support point when planning a later read-only Ghidra identity pass. Promote only one mechanics anchor at a time after direct retail-binary/decompile/read-back proof.
