# Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Dry-Run Consumer Validation Proof Plan

Status: complete public-safe command arm-checklist command dry-run consumer validation, not command arming or execution

Date: 2026-06-15

## Scope

This proof consumes the tracked public-safe command arm-checklist command dry-run proof at texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-dry-run-proof-plan.v1.json and validates that its 99 embedded command dry-run rows remain non-armed, non-dispatched, and not executed. It does not read private asset bytes, consume raw private manifests, publish private paths or filenames, publish raw command arguments or traces, arm a command, dispatch a command to a shell, execute a command, execute a real/private importer, generate assets, launch BEA, mutate Ghidra, mutate the installed game or original executable, wire product UI, do Godot work, implement a renderer/rebuild, or claim runtime/rebuild/no-noticeable-difference parity.

## Continuity

| Field | Value |
| --- | --- |
| Schema | texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-dry-run-consumer-validation-proof-plan.v1 |
| Status token | privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandDryRunConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-dry-run-consumer-validation-complete-public-safe-non-dispatched-command-arm-checklist-command-dry-run-consumed-not-real-importer-execution |
| Previous slice | Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Dry-Run Proof Plan |
| Previous scope | texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-dry-run-proof-plan |
| Selected next slice | Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Readiness Gate Proof Plan |
| Selected next scope | texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-readiness-gate-proof-plan |
| Source status | sourceCommandArmChecklistCommandDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-dry-run-complete-public-safe-readiness-row-consumption-not-real-importer-execution |
| Generator | tools/texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_command_arm_checklist_command_dry_run_consumer_validation.py |
| Tracked proof JSON | texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-dry-run-consumer-validation-proof-plan.v1.json |

## Positive Evidence

| Metric | Value |
| --- | ---: |
| sourceProofCount | 40 |
| sourceCommandArmChecklistCommandDryRunProofCount | 39 |
| sourceCommandArmChecklistCommandDryRunInterfaceCount | 10 |
| commandArmChecklistCommandDryRunConsumerValidationInterfaceCount | 10 |
| commandArmChecklistCommandDryRunRowsConsumed | 99 |
| commandArmChecklistCommandDryRunConsumerValidationRows | 99 |
| validatedNonDispatchedCommandArmChecklistCommandDryRunRowCount | 99 |
| armedCommandRowCount | 0 |
| executedCommandRowCount | 0 |
| shellDispatchedCommandRowCount | 0 |
| readyForLaterCommandArmChecklistCommandArmReadinessGateRowCount | 99 |
| readyForLaterHarnessArmRowCount | 99 |
| observedChecklistRowCount | 0 |
| rowStatusChangedCount | 0 |
| consumerArchiveTotalCount | 301 |
| unknownAyaArchiveClassCount | 0 |
| publicSafeCommandArmChecklistCommandDryRunConsumerValidationArtifactRows | 1 |
| publicAllowedOutputCount | 49 |
| redactedFieldCount | 29 |
| falseGuardCount | 184 |
| zeroCounterCount | 150 |
| publicLeakCheck | PASS |

Exact probe tokens: sourceProofCount=40; sourceCommandArmChecklistCommandDryRunProofCount=39; sourceCommandArmChecklistCommandDryRunInterfaceCount=10; commandArmChecklistCommandDryRunConsumerValidationInterfaceCount=10; commandArmChecklistCommandDryRunRowsConsumed=99; commandArmChecklistCommandDryRunConsumerValidationRows=99; validatedNonDispatchedCommandArmChecklistCommandDryRunRowCount=99; armedCommandRowCount=0; executedCommandRowCount=0; shellDispatchedCommandRowCount=0; readyForLaterCommandArmChecklistCommandArmReadinessGateRowCount=99; readyForLaterHarnessArmRowCount=99; observedChecklistRowCount=0; rowStatusChangedCount=0; consumerArchiveTotalCount=301; unknownAyaArchiveClassCount=0; publicSafeCommandArmChecklistCommandDryRunConsumerValidationArtifactRows=1; publicAllowedOutputCount=49; redactedFieldCount=29; falseGuardCount=184; zeroCounterCount=150; publicLeakCheck=PASS.

Category count tokens: allowed-future-input-class=5; harness-boundary-archive-class=5; harness-boundary-interface=10; harness-stop-condition=12; public-allowed-output=33; redaction-field=28; required-future-artifact-class=6.

## Required True Guards

- privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandDryRunConsumerValidationOnly=true
- commandArmChecklistCommandDryRunProofConsumed=true
- commandArmChecklistCommandDryRunProofContinuityValidated=true
- commandArmChecklistCommandDryRunProofRowsConsumed=true
- commandArmChecklistCommandDryRunConsumerValidationExecuted=true
- commandArmChecklistCommandDryRunConsumerValidationInputAccepted=true
- commandArmChecklistCommandDryRunArtifactSchemaValidated=true
- commandArmChecklistCommandDryRunRowOrdinalsValidated=true
- commandArmChecklistCommandDryRunNonDispatchedStatusesValidated=true
- commandArmChecklistCommandDryRunAggregateCountsValidated=true
- commandArmChecklistCommandDryRunConsumerValidationInterfacesValidated=true
- commandArmChecklistCommandDryRunConsumerValidationEmitsOnlyPublicSafeRows=true
- harnessCommandArmChecklistCommandArmReadinessGateLaneSelected=true
- privateEvidenceStoredOutsidePublicReleaseScope=true
- publicPrivateSeparationRequired=true

## Required False Guards

- privateAssetContentRead=false
- privateArchiveBytesRead=false
- rawPrivateManifestConsumed=false
- rawPrivateManifestRowsConsumed=false
- realImporterImplementation=false
- realImporterExecuted=false
- privateImporterDryRunExecuted=false
- realImporterDryRunExecuted=false
- realImporterDryRunHarnessExecuted=false
- realImporterDryRunHarnessArmed=false
- realImporterDryRunHarnessCommandArmed=false
- realImporterDryRunHarnessCommandExecuted=false
- realImporterDryRunHarnessCommandSentToShell=false
- realImporterDryRunHarnessCommandPrivateOutputGenerated=false
- realImporterDryRunHarnessRunnableCommandMaterialized=false
- realImporterDryRunHarnessCommandArmChecklistCommandDryRunExecuted=false
- realImporterDryRunHarnessCommandArmChecklistCommandDryRunSentToShell=false
- realImporterDryRunHarnessCommandArmChecklistCommandDryRunPrivateOutputGenerated=false
- realImporterDryRunHarnessCommandArmChecklistCommandDryRunConsumerValidationReadPrivateInputs=false
- realImporterDryRunHarnessCommandArmChecklistCommandDryRunConsumerValidationPublishedPrivateInput=false
- realImporterDryRunHarnessCommandArmChecklistCommandDryRunConsumerValidationExecutedShellCommand=false
- privateCommandArmChecklistCommandDryRunConsumerValidationArtifactPublished=false
- realImporterDryRunHarnessCommandArmChecklistCommandArmReadinessGateExecuted=false
- actualAssetImportExecuted=false
- generatedAssetOutputExecuted=false
- installedGameMutationAllowed=false
- originalExecutableMutationAllowed=false

## Required Zero Counters

- rawPathRows=0
- rawFilenameRows=0
- rawStemRows=0
- rawHashRows=0
- byteLengthRows=0
- rawTextureRefRows=0
- rawMeshRefRows=0
- rawCommandArgumentRows=0
- publishedCommandArgumentRows=0
- rawCommandArmChecklistCommandDryRunTraceRows=0
- commandExecutionRows=0
- commandShellDispatchRows=0
- commandArmChecklistCommandDryRunOutputArtifactRows=0
- privateCommandArmChecklistCommandDryRunConsumerValidationArtifactRows=0
- actualAssetImportRows=0
- generatedAssetRows=0
- outputArtifactRows=0
- privateArtifactRows=0
- privateDryRunRows=0
- realImporterDryRunRows=0
- realImporterDryRunHarnessCommandArmChecklistCommandDryRunConsumerValidationRows=0
- realImporterDryRunHarnessCommandArmChecklistCommandDryRunRows=0
- realImporterImplementationRows=0
- rebuildImplementationRows=0

## Boundary

This proof only proves public-safe consumer validation of the tracked command arm-checklist command dry-run proof and selection of the next command arm-checklist command arm-readiness gate. It does not prove private asset parsing, private raw manifest consumption, runnable command materialization, command arming, command execution, shell dispatch, real importer implementation, real importer execution, private importer dry run, real importer dry run, generated asset output, runtime parser behavior, texture pixels, mesh loading/skinning, Direct3D/GPU behavior, material visual correctness, material/shader parity, asset format completeness, product UI behavior, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.