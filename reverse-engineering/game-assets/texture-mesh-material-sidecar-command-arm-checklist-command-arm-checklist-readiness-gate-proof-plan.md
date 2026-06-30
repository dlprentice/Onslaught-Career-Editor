# Texture Mesh Material Sidecar Command Arm Checklist Readiness Gate Proof Plan

Status: materialized public-safe readiness-gate proof plan slot; planning and
continuity guard only, not readiness-gate execution and not command arming

Date: 2026-06-30

Alias: `tmm-arm4-readiness-gate`

Full slice: `Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Checklist Readiness Gate Proof Plan`

Scope: `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-checklist-readiness-gate-proof-plan`

Source evidence: completed `tmm-arm4-validation`, backed by
`texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-validation-proof.v1.json`.

This proof plan materializes the public-safe ARM4 readiness-gate slot selected
by the rebuild front-door chain map. It consumes only the tracked public-safe
validation proof summary and defines the checks a later explicit readiness-gate
proof must satisfy before any separate command-arm boundary lane can be chosen.

Machine proof JSON, a readiness-gate generator, command arming, shell dispatch,
real importer execution, generated payload output, runtime proof, and rebuild
parity remain separate later gates. This plan is not a completed
readiness-gate proof; specifically, it is not a completed readiness-gate proof.

## Source Continuity

The completed validation proof records these source-bound counters for this
plan:

| Field | Expected value |
| --- | --- |
| `privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationStatus` | `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-complete-public-safe-not-run-checklist-rows-validated-no-command-arming` |
| `selectedNextScope` | `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-checklist-readiness-gate-proof-plan` |
| `commandArmChecklistRowsConsumed` | `99` |
| `commandArmChecklistValidationRows` | `99` |
| `passedCommandArmChecklistValidationRowCount` | `99` |
| `failedCommandArmChecklistValidationRowCount` | `0` |
| `validatedNotRunCommandArmChecklistRowCount` | `99` |
| `validatedUnobservedCommandArmChecklistRowCount` | `99` |
| `validatedNotArmedCommandArmChecklistRowCount` | `99` |
| `validatedNotExecutedCommandArmChecklistRowCount` | `99` |
| `armedCommandRowCount` | `0` |
| `executedCommandRowCount` | `0` |
| `shellDispatchedCommandRowCount` | `0` |
| `consumerArchiveTotalCount` | `301` |
| `unknownAyaArchiveClassCount` | `0` |
| `publicLeakCheck` | `PASS` |
| `realImporterExecuted` | `false` |
| `actualAssetImportRows` | `0` |
| `generatedAssetRows` | `0` |
| `rawPathRows` | `0` |
| `rawFilenameRows` | `0` |
| `rawHashRows` | `0` |
| `byteLengthRows` | `0` |

The readiness-gate proof plan may only describe those counters and the next
fail-closed checks. It must not introduce raw private rows, payload locations,
hashes, byte lengths, command arguments, shell traces, or generated asset output.

## Required Later Readiness-Gate Checks

A later completed readiness-gate proof must, at minimum:

- load the public-safe ARM4 validation proof listed above;
- verify the validation proof status is `PASS`;
- verify the validation proof selected this exact readiness-gate scope;
- preserve all `99` not-run, unobserved, not-armed, and not-executed rows;
- preserve `armedCommandRowCount=0`, `executedCommandRowCount=0`, and
  `shellDispatchedCommandRowCount=0`;
- preserve `realImporterExecuted=false`, `actualAssetImportRows=0`,
  `generatedAssetRows=0`, `rawPathRows=0`, `rawFilenameRows=0`,
  `rawHashRows=0`, and `byteLengthRows=0`;
- verify `publicLeakCheck=PASS`;
- reject any private asset content read, raw private manifest consumption,
  command arming, shell dispatch, importer execution, generated payload output,
  BEA launch, CDB attach, Ghidra mutation or read-back, product UI work,
  renderer/rebuild implementation, runtime proof, visual parity, gameplay
  proof, rebuild parity, runtime parity, or no no-noticeable-difference parity
  claim;
- select only a later explicit command-arm boundary lane after those checks pass.

## Explicit Non-Claims

This artifact makes only a public-safe planning and continuity claim. It is:

- no private asset reads;
- no private asset bytes;
- no raw private manifest reads;
- no raw private manifest consumption in public scope;
- no command arming;
- no shell dispatch;
- no command execution;
- no importer execution;
- no generated payloads;
- no generated asset output;
- no BEA launch;
- no CDB;
- no Ghidra mutation or read-back;
- no product code change;
- no patch catalog change;
- no state baton edit;
- no runtime proof;
- no runtime parity;
- no visual parity;
- no gameplay proof;
- no rebuild parity;
- no no-noticeable-difference parity.

Static closure remains a static measurement result only. It does not prove
runtime behavior, gameplay behavior, importer behavior, generated asset
correctness, renderer behavior, rebuild parity, runtime parity, visual parity,
or no-noticeable-difference parity.

## Fail-Closed Conditions

The plan and checker fail closed if any of the following is observed:

- source validation proof is missing, malformed, or not `PASS`;
- source validation proof does not select this readiness-gate scope;
- any expected source counter differs from the table above;
- any command row is armed, executed, or shell-dispatched;
- any importer execution, asset import, generated payload, raw path, raw
  filename, raw hash, or byte-length counter is nonzero;
- `publicLeakCheck` is not `PASS`;
- the plan text contains private paths, generated payload names, raw hashes,
  command arguments, shell traces, or positive runtime/rebuild/parity claims;
- the plan is described as a completed readiness-gate proof instead of a
  public-safe proof-plan slot.

## Checker

Run the plan checker from the repo root:

```powershell
py -3 tools\rebuild_tmm_arm4_readiness_gate_proof_plan_probe.py --check
```

The checker reads only tracked public-safe files: this Markdown file, the
tracked validation proof JSON, and the front-door index/map docs that link this
slot. It does not discover local game folders, inspect private asset manifests,
resolve private paths, stat payload files, run BEA, attach CDB, launch Ghidra,
or write generated assets.
