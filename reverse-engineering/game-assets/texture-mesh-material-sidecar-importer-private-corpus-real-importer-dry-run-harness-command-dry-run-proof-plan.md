# Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Dry-Run Proof Plan

Status: complete public-safe non-dispatched command dry-run, not command execution

Date: 2026-06-15

## Scope

This proof consumes the tracked public-safe command-readiness gate proof at `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-readiness-gate-proof-plan.v1.json` and validates that its 99 non-armed command rows can pass a public-safe command dry-run. It does not arm a command, dispatch a command to a shell, execute a command, execute a real/private importer, read private asset bytes, consume raw private manifests, generate assets, launch BEA, mutate Ghidra, mutate the installed game or original executable, wire product UI, do Godot work, implement a renderer/rebuild, or claim runtime/rebuild/no-noticeable-difference parity.

## Continuity

| Field | Value |
| --- | --- |
| Schema | `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-dry-run-proof-plan.v1` |
| Status token | `privateCorpusRealImporterDryRunHarnessCommandDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-dry-run-complete-public-safe-readiness-row-consumption-not-real-importer-execution` |
| Previous slice | Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Readiness Gate Proof Plan |
| Previous scope | `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-readiness-gate-proof-plan` |
| Selected next slice | Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Dry-Run Consumer Validation Proof Plan |
| Selected next scope | `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-dry-run-consumer-validation-proof-plan` |
| Source status | `sourceCommandReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-readiness-gate-complete-public-safe-readiness-only-not-command-execution` |
| Generator | `tools/texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_dry_run.py` |
| Tracked proof JSON | `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-dry-run-proof-plan.v1.json` |

## Positive Evidence

| Metric | Value |
| --- | ---: |
| `sourceProofCount` | `29` |
| `sourceCommandReadinessGateProofCount` | `28` |
| `sourceCommandReadinessGateInterfaceCount` | `10` |
| `commandDryRunInterfaceCount` | `10` |
| `commandReadinessGateRowsConsumed` | `99` |
| `commandDryRunRows` | `99` |
| `passedCommandDryRunRowCount` | `99` |
| `failedCommandDryRunRowCount` | `0` |
| `armedCommandRowCount` | `0` |
| `executedCommandRowCount` | `0` |
| `shellDispatchedCommandRowCount` | `0` |
| `readyForLaterCommandDryRunConsumerValidationRowCount` | `99` |
| `readyForLaterHarnessArmRowCount` | `99` |
| `consumerArchiveTotalCount` | `301` |
| `publicSafeCommandDryRunArtifactRows` | `1` |
| `publicAllowedOutputCount` | `16` |
| `redactedFieldCount` | `17` |
| `falseGuardCount` | `122` |
| `zeroCounterCount` | `100` |
| `publicLeakCheck` | `PASS` |

Exact probe tokens: `sourceProofCount=29`; `sourceCommandReadinessGateProofCount=28`; `sourceCommandReadinessGateInterfaceCount=10`; `commandDryRunInterfaceCount=10`; `commandReadinessGateRowsConsumed=99`; `commandDryRunRows=99`; `passedCommandDryRunRowCount=99`; `failedCommandDryRunRowCount=0`; `armedCommandRowCount=0`; `executedCommandRowCount=0`; `shellDispatchedCommandRowCount=0`; `readyForLaterCommandDryRunConsumerValidationRowCount=99`; `readyForLaterHarnessArmRowCount=99`; `consumerArchiveTotalCount=301`; `publicSafeCommandDryRunArtifactRows=1`; `publicAllowedOutputCount=16`; `redactedFieldCount=17`; `falseGuardCount=122`; `zeroCounterCount=100`; `publicLeakCheck=PASS`.

## Required True Guards

- `privateCorpusRealImporterDryRunHarnessCommandDryRunOnly=true`
- `commandReadinessGateProofConsumed=true`
- `commandReadinessGateProofContinuityValidated=true`
- `commandReadinessGateProofRowsConsumed=true`
- `harnessCommandDryRunExecuted=true`
- `harnessCommandDryRunInputAccepted=true`
- `harnessCommandDryRunRowsGenerated=true`
- `harnessCommandDryRunRowsValidated=true`
- `harnessCommandDryRunAggregateCountsValidated=true`
- `harnessCommandDryRunInterfacesValidated=true`
- `harnessCommandDryRunEmitsOnlyPublicSafeRows=true`
- `harnessCommandDryRunRedactionPolicyValidated=true`
- `harnessCommandDryRunConsumerValidationLaneSelected=true`
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
- `harnessCommandDryRunReadPrivateInputs=false`
- `harnessCommandDryRunPublishedPrivateInput=false`
- `privateCommandDryRunArtifactPublished=false`
- `rawCommandDryRunTracePublished=false`
- `commandDryRunSentToShell=false`
- `commandDryRunGeneratedPrivateOutput=false`
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
- `privateCommandDryRunArtifactRows=0`
- `actualAssetImportRows=0`
- `generatedAssetRows=0`
- `outputArtifactRows=0`
- `privateArtifactRows=0`
- `privateDryRunRows=0`
- `realImporterDryRunRows=0`
- `realImporterDryRunHarnessCommandDryRunRows=0`
- `realImporterImplementationRows=0`
- `rebuildImplementationRows=0`

## Boundary

This proof only proves public-safe non-dispatched command dry-run validation of tracked command-readiness rows and selection of the next command dry-run consumer-validation lane. It does not prove private asset parsing, runnable command materialization, command arming, command execution, shell dispatch, runtime parser behavior, texture pixels, mesh loading/skinning, Direct3D/GPU behavior, material visual correctness, material/shader parity, asset format completeness, product UI behavior, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
