# Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Readiness Gate Proof Plan

Status: complete public-safe command arm-readiness gate, not command arming or execution

Date: 2026-06-15

## Scope

This proof consumes the tracked public-safe command dry-run consumer-validation proof at `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-dry-run-consumer-validation-proof-plan.v1.json` and validates that its 99 embedded command rows remain non-armed, non-dispatched, and not executed before selecting a later command arm-boundary lane. It does not read private asset bytes, consume raw private manifests, publish private paths or filenames, arm a command, dispatch a command to a shell, execute a command, execute a real/private importer, generate assets, launch BEA, mutate Ghidra, mutate the installed game or original executable, wire product UI, do Godot work, implement a renderer/rebuild, or claim runtime/rebuild/no-noticeable-difference parity.

## Continuity

| Field | Value |
| --- | --- |
| Schema | `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-readiness-gate-proof-plan.v1` |
| Status token | `privateCorpusRealImporterDryRunHarnessCommandArmReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-readiness-gate-complete-public-safe-readiness-only-not-command-arming` |
| Previous slice | Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Dry-Run Consumer Validation Proof Plan |
| Previous scope | `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-dry-run-consumer-validation-proof-plan` |
| Selected next slice | Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Boundary Proof Plan |
| Selected next scope | `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-boundary-proof-plan` |
| Source status | `sourceCommandDryRunConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-dry-run-consumer-validation-complete-public-safe-non-dispatched-command-dry-run-consumed-not-real-importer-execution` |
| Generator | `tools/texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_readiness_gate.py` |
| Tracked proof JSON | `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-readiness-gate-proof-plan.v1.json` |

## Positive Evidence

| Metric | Value |
| --- | ---: |
| `sourceProofCount` | `31` |
| `sourceCommandDryRunConsumerValidationProofCount` | `30` |
| `sourceCommandDryRunConsumerValidationInterfaceCount` | `10` |
| `commandArmReadinessGateInterfaceCount` | `10` |
| `commandDryRunConsumerValidationRowsConsumed` | `99` |
| `commandArmReadinessGateRows` | `99` |
| `passedCommandArmReadinessGateRowCount` | `99` |
| `failedCommandArmReadinessGateRowCount` | `0` |
| `armedCommandRowCount` | `0` |
| `executedCommandRowCount` | `0` |
| `shellDispatchedCommandRowCount` | `0` |
| `readyForLaterCommandArmBoundaryRowCount` | `99` |
| `readyForLaterHarnessArmRowCount` | `99` |
| `observedChecklistRowCount` | `0` |
| `rowStatusChangedCount` | `0` |
| `consumerArchiveTotalCount` | `301` |
| `unknownAyaArchiveClassCount` | `0` |
| `publicSafeCommandArmReadinessGateArtifactRows` | `1` |
| `publicAllowedOutputCount` | `22` |
| `redactedFieldCount` | `19` |
| `falseGuardCount` | `132` |
| `zeroCounterCount` | `110` |
| `publicLeakCheck` | `PASS` |

Exact probe tokens: `sourceProofCount=31`; `sourceCommandDryRunConsumerValidationProofCount=30`; `sourceCommandDryRunConsumerValidationInterfaceCount=10`; `commandArmReadinessGateInterfaceCount=10`; `commandDryRunConsumerValidationRowsConsumed=99`; `commandArmReadinessGateRows=99`; `passedCommandArmReadinessGateRowCount=99`; `failedCommandArmReadinessGateRowCount=0`; `armedCommandRowCount=0`; `executedCommandRowCount=0`; `shellDispatchedCommandRowCount=0`; `readyForLaterCommandArmBoundaryRowCount=99`; `readyForLaterHarnessArmRowCount=99`; `observedChecklistRowCount=0`; `rowStatusChangedCount=0`; `consumerArchiveTotalCount=301`; `unknownAyaArchiveClassCount=0`; `publicSafeCommandArmReadinessGateArtifactRows=1`; `publicAllowedOutputCount=22`; `redactedFieldCount=19`; `falseGuardCount=132`; `zeroCounterCount=110`; `publicLeakCheck=PASS`.

Category count tokens: `allowed-future-input-class=5`; `harness-boundary-archive-class=5`; `harness-boundary-interface=10`; `harness-stop-condition=12`; `public-allowed-output=33`; `redaction-field=28`; `required-future-artifact-class=6`.

## Required True Guards

- `privateCorpusRealImporterDryRunHarnessCommandArmReadinessGateOnly=true`
- `commandDryRunConsumerValidationProofConsumed=true`
- `commandDryRunConsumerValidationProofContinuityValidated=true`
- `commandDryRunConsumerValidationProofRowsConsumed=true`
- `commandArmReadinessGateExecuted=true`
- `commandArmReadinessGateInputAccepted=true`
- `commandArmReadinessGatePreconditionsValidated=true`
- `commandArmReadinessGateRowStatusesValidated=true`
- `commandArmReadinessGateRowOrdinalsValidated=true`
- `commandArmReadinessGateCategoryCountsValidated=true`
- `commandArmReadinessGateInterfacesValidated=true`
- `commandArmReadinessGateEmitsOnlyPublicSafeRows=true`
- `commandArmReadinessGateRedactionPolicyValidated=true`
- `harnessCommandArmBoundaryLaneSelected=true`
- `privateEvidenceStoredOutsidePublicReleaseScope=true`
- `publicPrivateSeparationRequired=true`

## Required False Guards

- `privateAssetContentRead=false`
- `privateArchiveBytesRead=false`
- `rawPrivateManifestConsumed=false`
- `rawPrivateManifestRowsConsumed=false`
- `realImporterImplementation=false`
- `realImporterExecuted=false`
- `privateImporterDryRunExecuted=false`
- `realImporterDryRunExecuted=false`
- `realImporterDryRunHarnessExecuted=false`
- `realImporterDryRunHarnessArmed=false`
- `realImporterDryRunHarnessCommandArmed=false`
- `realImporterDryRunHarnessCommandExecuted=false`
- `realImporterDryRunHarnessCommandSentToShell=false`
- `realImporterDryRunHarnessCommandPrivateOutputGenerated=false`
- `realImporterDryRunHarnessRunnableCommandMaterialized=false`
- `realImporterDryRunHarnessCommandDryRunExecuted=false`
- `realImporterDryRunHarnessCommandDryRunSentToShell=false`
- `realImporterDryRunHarnessCommandDryRunPrivateOutputGenerated=false`
- `realImporterDryRunHarnessCommandArmReadinessGateReadPrivateInputs=false`
- `realImporterDryRunHarnessCommandArmReadinessGatePublishedPrivateInput=false`
- `privateCommandArmReadinessGateArtifactPublished=false`
- `realImporterDryRunHarnessCommandArmBoundaryExecuted=false`
- `realImporterDryRunHarnessCommandArmBoundarySentToShell=false`
- `realImporterDryRunHarnessCommandArmBoundaryPrivateOutputGenerated=false`
- `actualAssetImportExecuted=false`
- `generatedAssetOutputExecuted=false`
- `installedGameMutationAllowed=false`
- `originalExecutableMutationAllowed=false`

## Required Zero Counters

- `rawPathRows=0`
- `rawFilenameRows=0`
- `rawStemRows=0`
- `rawHashRows=0`
- `byteLengthRows=0`
- `rawTextureRefRows=0`
- `rawMeshRefRows=0`
- `rawCommandArgumentRows=0`
- `publishedCommandArgumentRows=0`
- `rawCommandDryRunTraceRows=0`
- `commandExecutionRows=0`
- `commandShellDispatchRows=0`
- `commandDryRunOutputArtifactRows=0`
- `commandArmBoundaryOutputArtifactRows=0`
- `privateCommandArmReadinessGateArtifactRows=0`
- `realImporterDryRunHarnessCommandArmReadinessGateRows=0`
- `realImporterDryRunHarnessCommandArmBoundaryRows=0`
- `actualAssetImportRows=0`
- `generatedAssetRows=0`
- `outputArtifactRows=0`
- `privateArtifactRows=0`

## Claim Boundary

This proves only that the tracked command dry-run consumer-validation proof can be consumed as public-safe command arm-readiness input, that the 99 command rows remain non-armed/non-dispatched/not-executed, and that a later command arm-boundary lane can be selected without arming or executing a command here.

It does not prove private asset content parsing, raw private manifest consumption, runnable real-importer harness command materialization, command arming, shell dispatch, real importer implementation/execution, actual asset import, generated asset outputs, runtime parser behavior, texture pixels, mesh loading/skinning, Direct3D/GPU behavior, material visual correctness, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
