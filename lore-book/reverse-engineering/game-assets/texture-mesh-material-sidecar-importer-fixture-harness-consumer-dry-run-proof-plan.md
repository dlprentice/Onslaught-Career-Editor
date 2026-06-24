# Texture/Mesh Material Sidecar Importer Fixture Harness Consumer Dry-Run Proof Plan

Status: complete public-safe consumer dry-run, not importer execution proof
Date: 2026-06-10
Scope: `texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan`

Canonical display name: Texture / Mesh Material Sidecar Importer Fixture Harness Consumer Dry-Run Proof Plan.

This slice follows the completed [Texture/Mesh Material Sidecar Importer Fixture Harness Materialization Proof Plan](texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan.md). It validates that the eight tracked public-safe materialized fixture rows can be consumed by a dry-run importer-facing contract without running a real importer, reading private assets, launching BEA, mutating Ghidra, doing Godot work, wiring product UI, or producing rebuild/output artifacts.

Result schema: [texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan.v1.json](texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan.v1.json).

## Result

- `consumerDryRunStatus=texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan-complete-public-safe-consumer-dry-run-not-importer-execution-proof`
- `previousSlice=Texture / Mesh Material Sidecar Importer Fixture Harness Materialization Proof Plan`
- `selectedNextSlice=Texture / Mesh Material Sidecar Importer Implementation Readiness Gate Proof Plan`
- `selectedNextScope=texture-mesh-material-sidecar-importer-implementation-readiness-gate-proof-plan`
- `sourceMaterializationStatus=texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan-complete-public-safe-deterministic-fixture-row-materialization-not-runtime-proof`
- `sourceMaterializedFixtureRowCount=8`
- `consumedFixtureRowCount=8`
- `consumerDryRunStepCount=10`
- `consumerAssertionGroupCount=8`
- `consumerAssertionCheckCount=19`
- `failedConsumerAssertions=0`
- `unexpectedFixtureRows=0`
- `publicSyntheticFixtureCount=8`
- `publicEdgeCaseIdCount=2`
- `derivedAssertionCount=6`
- `dryRunOnly=true`
- `dryRunValidationOnly=true`
- `consumerInputMode=tracked-public-sanitized-materialization-schema`
- `consumerOutputMode=dry-run-summary-only`
- `consumerDryRunExecuted=true`
- `realImporterImplementation=false`
- `realImporterExecuted=false`
- `consumerOutputArtifactRows=0`
- `modelRowsWithTextureRefs=352/352`
- `modelTextureReferenceInstances=1268`
- `uniqueModelTextureRefUnion=213`
- `familyUniqueRefSum=241`
- `familyUniqueRefsAreNotAdditive=true`
- `sidecarFiles=213`
- `exactFilenameMatches=212`
- `stemOnlyMatches=1`
- `missingSidecarRefs=0`
- `catalogRows=4050`
- `catalogMissingRefs=0`
- `ambiguousCatalogRefs=1`
- `embeddedDuplicateOutputGroups=28`
- `embeddedDuplicateOutputSurplusRows=32`
- `publicLeakCheck=PASS`

Static context remains `6411/6411 = 100.00%`, `0 / 0 / 0`, `1560/1560 = 100.00%`, `1179/1179 = 100.00%`, and `remainingActiveFocusedWork=0`.

Probe anchors: `213 + 139 = 352`; `602 + 666 = 1268`; `213 + 28 = 241`; `212 + 1 = 213`; `139 - 107 = 32`; `consumerDryRunExecuted=true`; `dryRunOnly=true`; `dryRunValidationOnly=true`; `realImporterExecuted=false`; `consumerOutputArtifactRows=0`; `failedConsumerAssertions=0`; `unexpectedFixtureRows=0`; `beProcessesAfterConsumerDryRun=0`.

## Consumed Fixture Rows

The consumer dry-run consumes exactly the eight materialized row IDs from the previous slice:

- `importer-source-matrix-prerequisite`
- `importer-loose-family-fixture`
- `importer-embedded-family-fixture`
- `importer-non-additive-union-fixture`
- `importer-sidecar-match-mode-fixture`
- `importer-catalog-linkage-fixture`
- `importer-duplicate-output-surplus-fixture`
- `importer-negative-claim-guard-fixture`

## Dry-Run Transcript

| Step ID | Result | Claim |
| --- | --- | --- |
| `load-public-materialization-schema` | `PASS` | Loads only the tracked public materialization schema. |
| `validate-source-materialization-status` | `PASS` | Confirms source status and static context before consumption. |
| `consume-source-prerequisite-row` | `PASS` | Confirms the eight-row source harness prerequisite. |
| `consume-loose-family-row` | `PASS` | Accepts the loose row-family aggregate without raw texture refs or filenames. |
| `consume-embedded-family-row` | `PASS` | Accepts the embedded row-family aggregate while preserving duplicate-output surplus. |
| `consume-non-additive-union-row` | `PASS` | Accepts the texture-ref union as non-additive across families. |
| `consume-sidecar-match-and-catalog-edge-rows` | `PASS` | Accepts the public stem-only and ambiguous-catalog edge IDs without resolving private variants. |
| `consume-duplicate-output-surplus-row` | `PASS` | Keeps row coverage separate from unique output-file coverage. |
| `consume-negative-claim-guard-row` | `PASS` | Keeps runtime/importer/Godot/Ghidra/product/rebuild/parity guards false. |
| `emit-dry-run-summary-no-artifacts` | `PASS` | Emits no importer outputs, generated assets, screenshots, frames, or private artifacts. |

## Consumer Checks

- Source materialization status and source row count match the prior slice.
- All eight materialized fixture row IDs are consumed exactly once.
- Loose family aggregates remain `213` rows, `602` texture-ref instances, `213` unique refs, `213` unique output files, `212` exact matches, `1` stem-only match, and `0` duplicate-output surplus rows.
- Embedded family aggregates remain `139` rows, `666` texture-ref instances, `28` unique refs, `107` unique output files, `28` duplicate-output groups, and `32` duplicate-output surplus rows.
- `213 + 139 = 352`, `602 + 666 = 1268`, `213 + 28 = 241`, `212 + 1 = 213`, and `139 - 107 = 32`.
- `uniqueModelTextureRefUnion=213`, so family unique refs remain non-additive.
- `stem-only-sidecar-match-boundary-001` and `ambiguous-catalog-ref-boundary-001` remain public edge IDs, not raw samples or chosen variants.
- `rawRefPublished=false`, `rawStemPublished=false`, `catalogVariantPublished=false`, `filenamePublished=false`, `pathPublished=false`, and `hashPublished=false` remain true for public edge cases.
- `runtimeExecution=false`, `godotWork=false`, `ghidraMutation=false`, `realImporterImplementation=false`, `realImporterExecuted=false`, `fixtureHarnessConsumerRuntimeExecuted=false`, `rebuildImplementation=false`, `rebuildParityProven=false`, and `noNoticeableDifferenceParityProven=false`.
- `actualAssetImportRows=0`, `generatedAssetRows=0`, `outputArtifactRows=0`, `dryRunOutputArtifactRows=0`, `importerImplementationRows=0`, `rebuildImplementationRows=0`, and `beProcessesAfterConsumerDryRun=0`.

## Public-Safety Rules

- The consumer dry-run reads only tracked public materialization JSON.
- The dry-run uses synthetic fixture row IDs and aggregate counts only.
- No raw texture refs, raw stems, filenames, paths, hashes, catalog variants, source rows, output artifacts, private frames, or private asset locators are published.
- The stem-only sidecar match remains a count and public edge ID.
- The ambiguous catalog ref remains a count and public edge ID.
- Embedded duplicate-output rows remain row-coverage evidence and are not collapsed into unique output-file coverage.

## Source Evidence

This consumer dry-run is grounded in tracked, public-safe aggregate evidence:

- [Texture/Mesh Material Sidecar Importer Fixture Harness Materialization Proof Plan](texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan.md)
- [Texture/Mesh Material Sidecar Importer Fixture Harness Materialization schema](texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan.v1.json)
- [Texture/Mesh Material Sidecar Importer Fixture Harness Proof Plan](texture-mesh-material-sidecar-importer-fixture-harness-proof-plan.md)
- [Texture/Mesh Material Sidecar Rebuild Fixture Matrix Proof Plan](texture-mesh-material-sidecar-rebuild-fixture-matrix-proof.md)
- [Texture/Mesh Material Sidecar Rebuild Contract Extension Proof Plan](texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.md)

## What This Proves

- The eight public-safe materialized fixture rows can be consumed by a dry-run importer-facing contract.
- The dry-run preserves loose and embedded row-family separation, non-additive texture-ref union accounting, sidecar match modes, catalog linkage, duplicate-output surplus rows, and synthetic edge-case IDs.
- The dry-run emits no importer outputs, generated assets, screenshots, frames, raw samples, or private artifacts.

## What Remains Separate Proof

This is public-safe consumer dry-run proof only. It does not prove real importer implementation, real importer execution, runtime resource archive parser behavior, runtime texture parser behavior, runtime texture pixels, JPEG/inflate decode fidelity, runtime mesh loading, runtime mesh skinning, animation behavior, collision behavior, Direct3D upload, GPU behavior, native textured 3D rendering, material visual correctness, material/shader parity, asset format completeness, exact mesh/texture layouts, runtime sidecar material loading, runtime object identity, runtime world loading, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.

Boundary token: runtimeExecution=false; beLaunch=false; newLaunch=false; screenshotCapture=false; privateFrameReviewPerformed=false; rowObservation=false; sourceSelectionObserved=false; sourceSelectionProven=false; nativeInput=false; debuggerAttachment=false; godotWork=false; ghidraMutation=false; executablePatching=false; productUiWired=false; realImporterImplementation=false; realImporterExecuted=false; importerImplementation=false; importerExecuted=false; fixtureHarnessRuntimeExecuted=false; fixtureHarnessConsumerRuntimeExecuted=false; rebuildImplementation=false; runtimeTextureParserBehaviorProven=false; runtimeTexturePixelsProven=false; runtimeJpegInflateDecodeFidelityProven=false; runtimeMeshLoadingProven=false; runtimeMeshSkinningProven=false; runtimeAnimationBehaviorProven=false; runtimeCollisionBehaviorProven=false; runtimeDirect3DUploadProven=false; runtimeGpuBehaviorProven=false; nativeTextured3DRenderingProven=false; materialVisualCorrectnessProven=false; materialShaderParityProven=false; visualQaComplete=false; cleanRoomRendererImplemented=false; assetFormatCompletenessProven=false; exactMeshTextureLayoutsProven=false; runtimeResourceArchiveParserProven=false; runtimeSidecarMaterialLoadProven=false; runtimeObjectIdentityProven=false; runtimeWorldLoadingProven=false; rebuildParityProven=false; noNoticeableDifferenceParityProven=false; privateAssetPublication=false; publicPrivateProofLeak=false; actualAssetImportRows=0; generatedAssetRows=0; outputArtifactRows=0; dryRunOutputArtifactRows=0; rawFixtureExampleRows=0; privateFixtureRows=0; runtimeTexturePixelRows=0; runtimeMeshRenderRows=0; runtimeMaterialRows=0; runtimeObservationRows=0; textureRuntimeEvidenceRows=0; meshRuntimeEvidenceRows=0; materialRuntimeEvidenceRows=0; materialVisualReviewRows=0; screenshotRows=0; privateFrameRowsObserved=0; rowObservationRows=0; sourceObservedRows=0; newLaunchRows=0; captureRows=0; ocrRows=0; rawDialogueRows=0; ghidraMutationRows=0; executablePatchRows=0; productUiRows=0; godotRows=0; importerImplementationRows=0; rebuildImplementationRows=0; runtimeCollisionRows=0; cleanRoomRendererRows=0; runtimeResourceArchiveParserRows=0; runtimeSidecarMaterialLoadRows=0; beProcessesAfterConsumerDryRun=0; publicCaseRawRefLeakCount=0; privatePathLeakCount=0; rawArtifactLeakCount=0; privateAssetLeakCount=0; publicPrivateProofLeakCount=0.
