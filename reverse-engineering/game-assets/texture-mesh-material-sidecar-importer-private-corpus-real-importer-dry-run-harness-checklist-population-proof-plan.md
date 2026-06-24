# Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Checklist Population Proof Plan

Status: complete public-safe harness checklist population, not real importer execution
Date: 2026-06-15
Scope: `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-population-proof-plan`

This proof consumes only the tracked public-safe real-importer dry-run harness-boundary proof and populates not-run/unobserved checklist rows for a later harness validation lane. It does not execute the real/private importer, read private asset content, consume raw private manifest rows, publish private paths or filenames, generate assets, launch BEA, mutate Ghidra, mutate the installed game or original executable, start Godot work, wire product UI, implement a renderer, implement a rebuild, or claim parity.

Evidence anchors:

- `privateCorpusRealImporterDryRunHarnessChecklistPopulationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-population-complete-public-safe-checklist-populated-not-real-importer-execution`
- `texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-population-proof-plan.v1.json`
- `tools/texture_mesh_material_sidecar_importer_private_corpus_real_importer_dry_run_harness_checklist_population.py`
- `previousSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Boundary Proof Plan`
- `previousScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary-proof-plan`
- `selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Checklist Validation Proof Plan`
- `selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-validation-proof-plan`
- `sourceRealImporterHarnessBoundaryStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary-defined-public-safe-boundary-only-not-real-importer-execution`
- `sourceRealImporterReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-readiness-gate-complete-public-safe-readiness-only-not-real-importer-execution`
- `sourceProofCount=23`
- `sourceHarnessBoundaryProofCount=22`

Harness checklist contract:

- `privateCorpusRealImporterDryRunHarnessChecklistPopulationOnly=true`
- `realImporterHarnessBoundaryProofConsumed=true`
- `realImporterHarnessBoundaryProofContinuityValidated=true`
- `realImporterHarnessBoundaryRowsConsumedByChecklistPopulation=true`
- `realImporterDryRunHarnessChecklistPopulated=true`
- `harnessChecklistRowsPopulated=true`
- `harnessChecklistArchiveClassRowsPopulated=true`
- `harnessChecklistInputClassRowsPopulated=true`
- `harnessChecklistRequiredArtifactRowsPopulated=true`
- `harnessChecklistStopConditionRowsPopulated=true`
- `harnessChecklistInterfaceRowsPopulated=true`
- `harnessChecklistRedactionRowsPopulated=true`
- `harnessChecklistPublicOutputRowsPopulated=true`
- `harnessChecklistRefusalGuardsValidated=true`
- `harnessChecklistArchiveClassOrderValidated=true`
- `harnessChecklistArchiveClassCountsValidated=true`
- `harnessChecklistInterfacesValidated=true`
- `harnessChecklistEmitsOnlyPublicSafeRows=true`
- `harnessChecklistValidationLaneSelected=true`
- `defaultChecklistRowStatus=not-run`
- `defaultObservationStatus=unobserved`
- `realImporterHarnessChecklistPopulationInputMode=tracked-public-safe-harness-boundary-proof-json`
- `realImporterHarnessChecklistPopulationOutputMode=public-safe-harness-checklist-not-run-unobserved-status-token-rows`
- `selectedNextLaneClass=private-corpus real importer dry-run harness checklist validation without execution`

Counts:

| Metric | Value |
| --- | ---: |
| `sourceRealImporterReadinessInterfaceCount` | 8 |
| `sourceRealImporterHarnessBoundaryInterfaceCount` | 10 |
| `realImporterDryRunHarnessChecklistPopulationInterfaceCount` | 12 |
| `realImporterHarnessBoundaryRowsConsumed` | 5 |
| `harnessChecklistGroupCount` | 7 |
| `harnessChecklistRows` | 99 |
| `harnessChecklistArchiveClassRows` | 5 |
| `harnessChecklistAllowedInputClassRows` | 5 |
| `harnessChecklistRequiredArtifactClassRows` | 6 |
| `harnessChecklistStopConditionRows` | 12 |
| `harnessChecklistBoundaryInterfaceRows` | 10 |
| `harnessChecklistRedactionFieldRows` | 28 |
| `harnessChecklistPublicAllowedOutputRows` | 33 |
| `passedChecklistRowCount` | 99 |
| `failedChecklistRowCount` | 0 |
| `notRunChecklistRowCount` | 99 |
| `unobservedChecklistRowCount` | 99 |
| `observedChecklistRowCount` | 0 |
| `rowStatusChangedCount` | 0 |
| `preflightCheckCount` | 17 |
| `passedPreflightCheckCount` | 17 |
| `failedPreflightCheckCount` | 0 |
| `consumerArchiveTotalCount` | 301 |
| `baseArchiveClassCount` | 1 |
| `frontendArchiveClassCount` | 1 |
| `loadingArchiveClassCount` | 1 |
| `numericLevelArchiveClassCount` | 66 |
| `goodieArchiveClassCount` | 232 |
| `unknownAyaArchiveClassCount` | 0 |
| `publicSafeHarnessChecklistArtifactRows` | 1 |
| `publicAllowedOutputCount` | 33 |
| `redactedFieldCount` | 28 |
| `falseGuardCount` | 94 |
| `zeroCounterCount` | 79 |

Probe count anchors: `sourceRealImporterReadinessInterfaceCount=8`; `sourceRealImporterHarnessBoundaryInterfaceCount=10`; `realImporterDryRunHarnessChecklistPopulationInterfaceCount=12`; `realImporterHarnessBoundaryRowsConsumed=5`; `harnessChecklistGroupCount=7`; `harnessChecklistRows=99`; `harnessChecklistArchiveClassRows=5`; `harnessChecklistAllowedInputClassRows=5`; `harnessChecklistRequiredArtifactClassRows=6`; `harnessChecklistStopConditionRows=12`; `harnessChecklistBoundaryInterfaceRows=10`; `harnessChecklistRedactionFieldRows=28`; `harnessChecklistPublicAllowedOutputRows=33`; `notRunChecklistRowCount=99`; `unobservedChecklistRowCount=99`; `observedChecklistRowCount=0`; `rowStatusChangedCount=0`; `preflightCheckCount=17`; `consumerArchiveTotalCount=301`; `publicSafeHarnessChecklistArtifactRows=1`; `publicAllowedOutputCount=33`; `redactedFieldCount=28`; `falseGuardCount=94`; `zeroCounterCount=79`.

Checklist groups:

- `harness-boundary-archive-class` rows: `5`, status `NOT_RUN_PUBLIC_CHECKLIST_ONLY`
- `allowed-future-input-class` rows: `5`, status `NOT_RUN_PUBLIC_CHECKLIST_ONLY`
- `required-future-artifact-class` rows: `6`, status `NOT_RUN_PUBLIC_CHECKLIST_ONLY`
- `harness-stop-condition` rows: `12`, status `NOT_RUN_PUBLIC_CHECKLIST_ONLY`
- `harness-boundary-interface` rows: `10`, status `NOT_RUN_PUBLIC_CHECKLIST_ONLY`
- `redaction-field` rows: `28`, status `NOT_RUN_PUBLIC_CHECKLIST_ONLY`
- `public-allowed-output` rows: `33`, status `NOT_RUN_PUBLIC_CHECKLIST_ONLY`

Allowed later input classes:

- `read-only-corpus-root-handle`
- `tracked-public-safe-redacted-manifest`
- `public-safe-archive-class-count-rows`
- `app-owned-private-evidence-root`
- `app-owned-importer-dry-run-output-root`

Required later artifact classes:

- `private-dry-run-command-manifest`
- `private-dry-run-input-manifest`
- `private-dry-run-output-inventory`
- `private-dry-run-log-inventory`
- `private-leak-scan-report`
- `public-safe-result-summary`

Stop conditions remain inherited from the boundary proof, including installed-title/original-executable mutation, raw private path publication, unarmed private asset reads, raw private manifest publication, output escaping app-owned roots, asset generation without inventory, BEA launch/runtime dependency, Ghidra mutation, Godot/UI/renderer/rebuild dependency, archive class/count mismatch, unknown archive class, and raw hash/byte-length/private-ref publication.

Boundary counters:

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
- `realImporterDryRunHarnessExecutedInChecklistPopulationSlice=false`
- `realImporterDryRunHarnessOutputPublished=false`
- `realImporterDryRunHarnessChecklistPopulationReadPrivateInputs=false`
- `realImporterDryRunHarnessChecklistPublishedPrivateInput=false`
- `realImporterDryRunHarnessChecklistPrivateValuesPublished=false`
- `realImporterDryRunHarnessChecklistValidationExecuted=false`
- `realImporterDryRunHarnessChecklistDryRunExecuted=false`
- `realImporterDryRunHarnessCommandMaterialized=false`
- `realImporterDryRunHarnessPrivateOutputGenerated=false`
- `actualAssetImportRows=0`
- `generatedAssetRows=0`
- `generatedDryRunOutputRows=0`
- `outputArtifactRows=0`
- `rawPathRows=0`
- `rawFilenameRows=0`
- `rawHashRows=0`
- `byteLengthRows=0`
- `rawTextureRefRows=0`
- `rawMeshRefRows=0`
- `realImporterDryRunRows=0`
- `realImporterDryRunHarnessRows=0`
- `realImporterDryRunHarnessOutputRows=0`
- `realImporterDryRunHarnessTraceRows=0`
- `harnessChecklistValidationRows=0`
- `harnessChecklistDryRunRows=0`
- `publicLeakCheck=PASS`

What this proves:

- The tracked harness-boundary proof can support public-safe not-run/unobserved checklist rows.
- The checklist preserves archive class order and aggregate count `301`.
- The checklist records allowed input classes, required artifact classes, stop conditions, interfaces, redaction fields, and public output classes.
- Private reads and real/private importer execution remain unperformed in this slice.

What remains unproven:

- Private asset content parsing.
- Raw private manifest consumption.
- Real importer implementation or execution.
- Private importer dry run or real importer dry run.
- Real importer dry-run harness execution.
- Real importer dry-run harness checklist validation.
- Actual asset import or generated asset outputs.
- Runtime resource/archive/texture/mesh behavior.
- Material visual correctness, shader parity, Godot parity, rebuild parity, or no-noticeable-difference parity.
