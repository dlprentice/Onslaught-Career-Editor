# Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Boundary Proof Plan

Status: complete public-safe command arm boundary, not command arming or execution

Date: 2026-06-15

## Scope

This proof consumes the tracked public-safe command arm-checklist command arm-readiness proof at `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-readiness-gate-proof-plan.v1.json` and defines the public-safe boundary for a later explicit command-arm checklist-population lane. It does not read private asset bytes, consume raw private manifests, publish private paths or filenames, arm a command, dispatch a command to a shell, execute a command, execute a real/private importer, generate assets, launch BEA, mutate Ghidra, mutate the installed game or original executable, wire product UI, do Godot work, implement a renderer/rebuild, or claim runtime/rebuild/no-noticeable-difference parity.

## Continuity

| Field | Value |
| --- | --- |
| Schema | `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-boundary-proof-plan.v1` |
| Status token | `privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmBoundaryStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-boundary-defined-public-safe-no-command-arming` |
| Previous slice | Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Readiness Gate Proof Plan |
| Previous scope | `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-readiness-gate-proof-plan` |
| Selected next slice | Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Population Proof Plan |
| Selected next scope | `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-population-proof-plan` |
| Source status | `sourceCommandArmChecklistCommandArmReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-readiness-gate-complete-public-safe-readiness-only-not-command-arming` |
| Generator | `tools/texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_command_arm_boundary.py` |
| Tracked proof JSON | `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-boundary-proof-plan.v1.json` |

## Positive Evidence

| Metric | Value |
| --- | ---: |
| `sourceProofCount` | `42` |
| `sourceCommandArmChecklistCommandArmReadinessGateProofCount` | `41` |
| `sourceCommandArmChecklistCommandArmReadinessGateInterfaceCount` | `10` |
| `commandArmChecklistCommandArmBoundaryInterfaceCount` | `10` |
| `commandArmChecklistCommandArmReadinessGateRowsConsumed` | `99` |
| `commandArmChecklistCommandArmBoundaryRows` | `99` |
| `definedCommandArmChecklistCommandArmBoundaryRowCount` | `99` |
| `failedCommandArmChecklistCommandArmBoundaryRowCount` | `0` |
| `armedCommandRowCount` | `0` |
| `executedCommandRowCount` | `0` |
| `shellDispatchedCommandRowCount` | `0` |
| `readyForLaterCommandArmChecklistCommandArmChecklistPopulationRowCount` | `99` |
| `readyForLaterHarnessArmRowCount` | `99` |
| `observedChecklistRowCount` | `0` |
| `rowStatusChangedCount` | `0` |
| `consumerArchiveTotalCount` | `301` |
| `unknownAyaArchiveClassCount` | `0` |
| `publicSafeCommandArmChecklistCommandArmBoundaryArtifactRows` | `1` |
| `publicAllowedOutputCount` | `55` |
| `redactedFieldCount` | `31` |
| `stopConditionCount` | `12` |
| `falseGuardCount` | `193` |
| `zeroCounterCount` | `161` |
| `publicLeakCheck` | `PASS` |

Exact probe tokens: `sourceProofCount=42`; `sourceCommandArmChecklistCommandArmReadinessGateProofCount=41`; `sourceCommandArmChecklistCommandArmReadinessGateInterfaceCount=10`; `commandArmChecklistCommandArmBoundaryInterfaceCount=10`; `commandArmChecklistCommandArmReadinessGateRowsConsumed=99`; `commandArmChecklistCommandArmBoundaryRows=99`; `definedCommandArmChecklistCommandArmBoundaryRowCount=99`; `passedCommandArmChecklistCommandArmBoundaryRowCount=99`; `failedCommandArmChecklistCommandArmBoundaryRowCount=0`; `armedCommandRowCount=0`; `executedCommandRowCount=0`; `shellDispatchedCommandRowCount=0`; `readyForLaterCommandArmChecklistCommandArmChecklistPopulationRowCount=99`; `readyForLaterHarnessArmRowCount=99`; `observedChecklistRowCount=0`; `rowStatusChangedCount=0`; `consumerArchiveTotalCount=301`; `unknownAyaArchiveClassCount=0`; `publicSafeCommandArmChecklistCommandArmBoundaryArtifactRows=1`; `publicAllowedOutputCount=55`; `redactedFieldCount=31`; `stopConditionCount=12`; `falseGuardCount=193`; `zeroCounterCount=161`; `publicLeakCheck=PASS`.

Category count tokens: `allowed-future-input-class=5`; `harness-boundary-archive-class=5`; `harness-boundary-interface=10`; `harness-stop-condition=12`; `public-allowed-output=33`; `redaction-field=28`; `required-future-artifact-class=6`.

## Required True Guards

- `privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmBoundaryOnly=true`
- `commandArmChecklistCommandArmReadinessGateProofConsumed=true`
- `commandArmChecklistCommandArmReadinessGateProofContinuityValidated=true`
- `commandArmChecklistCommandArmReadinessGateProofRowsConsumed=true`
- `commandArmChecklistCommandArmBoundaryDefined=true`
- `commandArmChecklistCommandArmBoundaryInputAccepted=true`
- `commandArmChecklistCommandArmBoundaryRowStatusesValidated=true`
- `commandArmChecklistCommandArmBoundaryRowOrdinalsValidated=true`
- `commandArmChecklistCommandArmBoundaryCategoryCountsValidated=true`
- `commandArmChecklistCommandArmBoundaryInterfacesValidated=true`
- `commandArmChecklistCommandArmBoundaryStopConditionsValidated=true`
- `commandArmChecklistCommandArmBoundaryEmitsOnlyPublicSafeRows=true`
- `commandArmChecklistCommandArmBoundaryRedactionPolicyValidated=true`
- `harnessCommandArmChecklistCommandArmChecklistPopulationLaneSelected=true`
- `futureCommandArmRequiresExplicitOperatorArm=true`
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
- `realImporterDryRunHarnessCommandArmChecklistCommandDryRunExecuted=false`
- `realImporterDryRunHarnessCommandArmChecklistCommandDryRunSentToShell=false`
- `realImporterDryRunHarnessCommandArmChecklistCommandDryRunPrivateOutputGenerated=false`
- `realImporterDryRunHarnessCommandArmReadinessGateReadPrivateInputs=false`
- `realImporterDryRunHarnessCommandArmReadinessGatePublishedPrivateInput=false`
- `privateCommandArmChecklistCommandArmReadinessGateArtifactPublished=false`
- `realImporterDryRunHarnessCommandArmChecklistCommandArmBoundaryExecuted=false`
- `realImporterDryRunHarnessCommandArmChecklistCommandArmBoundarySentToShell=false`
- `realImporterDryRunHarnessCommandArmChecklistCommandArmBoundaryPrivateOutputGenerated=false`
- `privateCommandArmChecklistCommandArmBoundaryArtifactPublished=false`
- `realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistPopulationExecuted=false`
- `realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistPopulationSentToShell=false`
- `realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistPopulationPrivateOutputGenerated=false`
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
- `privateCommandArmBoundaryArtifactRows=0`
- `realImporterDryRunHarnessCommandArmBoundaryRows=0`
- `realImporterDryRunHarnessCommandArmChecklistCommandArmChecklistPopulationRows=0`
- `actualAssetImportRows=0`
- `generatedAssetRows=0`
- `outputArtifactRows=0`
- `privateArtifactRows=0`

## Arm Boundary

The later command-arm checklist-population proof may only populate public-safe checklist rows and may move nothing into an armed, dispatched, executed, or private-output state unless a later lane is explicitly selected and armed. This boundary records `futureCommandArmRequiresExplicitOperatorArm=true`, `harnessCommandArmChecklistCommandArmChecklistPopulationLaneSelected=true`, and `readyForLaterCommandArmChecklistCommandArmChecklistPopulationRowCount=99`.

Stop conditions are encoded as `stopConditionCount=12` and include command arming, shell dispatch, real importer dry-run execution, private asset/raw manifest exposure, generated asset output inference, runtime parser or material-visual claims, installed/original executable mutation, Ghidra mutation, BEA launch, Godot, product UI, renderer, rebuild, and no-noticeable-difference claims.

## Claim Boundary

This proves only that the tracked command arm-checklist command arm-readiness proof can be consumed as public-safe command arm-checklist command arm-boundary input, that the 99 command rows remain non-armed/non-dispatched/not-executed, and that a later command arm-checklist-population lane can be selected without arming or executing a command here.

It does not prove private asset content parsing, raw private manifest consumption, runnable real-importer harness command materialization, command arming, shell dispatch, real importer implementation/execution, actual asset import, generated asset outputs, runtime parser behavior, texture pixels, mesh loading/skinning, Direct3D/GPU behavior, material visual correctness, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
