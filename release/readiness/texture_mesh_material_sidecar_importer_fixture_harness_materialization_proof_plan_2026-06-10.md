# Texture/Mesh Material Sidecar Importer Fixture Harness Materialization Proof Plan Readiness Note

Status: complete public-safe deterministic fixture row materialization, not runtime proof
Date: 2026-06-10
Scope: `texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan`

This readiness note covers the Texture / Mesh Material Sidecar Importer Fixture Harness Materialization Proof Plan. The slice follows the completed Texture / Mesh Material Sidecar Importer Fixture Harness Proof Plan and materializes eight deterministic public-safe fixture rows from aggregate evidence only.

Canonical artifact:

- `reverse-engineering/game-assets/texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan.md`
- `reverse-engineering/game-assets/texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan.v1.json`

Result:

- `materializationStatus=texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan-complete-public-safe-deterministic-fixture-row-materialization-not-runtime-proof`
- `previousSlice=Texture / Mesh Material Sidecar Importer Fixture Harness Proof Plan`
- `selectedNextSlice=Texture / Mesh Material Sidecar Importer Fixture Harness Consumer Dry-Run Proof Plan`
- `selectedNextScope=texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan`
- `sourceHarnessStatus=texture-mesh-material-sidecar-importer-fixture-harness-proof-plan-complete-static-importer-harness-contract-not-runtime-proof`
- `harnessDimensionCount=7`
- `sourceHarnessCaseCount=8`
- `materializedFixtureRowCount=8`
- `importerAssertionGroupCount=8`
- `publicSyntheticFixtureCount=8`
- `publicEdgeCaseIdCount=2`
- `derivedAssertionCount=6`
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

Materialized fixture rows:

| Fixture row ID | Dimension | Assertion group |
| --- | --- | --- |
| `importer-source-matrix-prerequisite` | prerequisite | source-matrix-prerequisite |
| `importer-loose-family-fixture` | row-family | loose-row-family |
| `importer-embedded-family-fixture` | row-family | embedded-row-family |
| `importer-non-additive-union-fixture` | unique-ref-union | non-additive-union |
| `importer-sidecar-match-mode-fixture` | sidecar-match-mode | sidecar-match-mode |
| `importer-catalog-linkage-fixture` | catalog-linkage | catalog-linkage |
| `importer-duplicate-output-surplus-fixture` | output-uniqueness | duplicate-output-surplus |
| `importer-negative-claim-guard-fixture` | claim-boundary | negative-claim-guard |

Derived assertions:

- `213 + 139 = 352`
- `602 + 666 = 1268`
- `213 + 28 = 241`
- `uniqueModelTextureRefUnion=213`
- `139 - 107 = 32`
- `352/352` model rows with texture refs remain catalog-mapped while `catalogMissingRefs=0`

Public edge IDs remain `stem-only-sidecar-match-boundary-001` and `ambiguous-catalog-ref-boundary-001`. For both, `rawRefPublished=false`, `rawStemPublished=false`, `catalogVariantPublished=false`, `filenamePublished=false`, `pathPublished=false`, and `hashPublished=false`.

Static context remains `6411/6411 = 100.00%`, `0 / 0 / 0`, `1560/1560 = 100.00%`, `1179/1179 = 100.00%`, and `remainingActiveFocusedWork=0`.

What this proves:

- The importer fixture harness contract now has eight deterministic public-safe fixture rows.
- Loose and embedded row-family aggregates, non-additive texture-ref union accounting, sidecar match modes, catalog linkage, duplicate-output surplus rows, and synthetic edge cases are materialized for a future consumer dry-run.
- The next consumer-dry-run lane can validate fixture consumption without raw texture refs, filenames, paths, hashes, private samples, private frames, generated asset outputs, runtime launch, or real importer execution.

What remains separate proof:

- Runtime resource archive parser behavior.
- Runtime texture parser behavior and texture pixels.
- Runtime mesh loading, skinning, animation, collision, Direct3D/GPU behavior, and native textured 3D rendering.
- Material visual correctness and material/shader parity.
- Asset format completeness and exact mesh/texture layouts.
- Real importer implementation or execution.
- Fixture-harness consumer execution.
- Godot parity.
- Rebuild implementation, rebuild parity, and no-noticeable-difference parity.

Boundary token: runtimeExecution=false; beLaunch=false; newLaunch=false; screenshotCapture=false; privateFrameReviewPerformed=false; rowObservation=false; sourceSelectionObserved=false; sourceSelectionProven=false; nativeInput=false; debuggerAttachment=false; godotWork=false; ghidraMutation=false; executablePatching=false; productUiWired=false; realImporterImplementation=false; realImporterExecuted=false; importerImplementation=false; importerExecuted=false; fixtureHarnessExecuted=false; fixtureHarnessConsumerExecuted=false; rebuildImplementation=false; runtimeTextureParserBehaviorProven=false; runtimeTexturePixelsProven=false; runtimeJpegInflateDecodeFidelityProven=false; runtimeMeshLoadingProven=false; runtimeMeshSkinningProven=false; runtimeAnimationBehaviorProven=false; runtimeCollisionBehaviorProven=false; runtimeDirect3DUploadProven=false; runtimeGpuBehaviorProven=false; nativeTextured3DRenderingProven=false; materialVisualCorrectnessProven=false; materialShaderParityProven=false; visualQaComplete=false; cleanRoomRendererImplemented=false; assetFormatCompletenessProven=false; exactMeshTextureLayoutsProven=false; runtimeResourceArchiveParserProven=false; runtimeSidecarMaterialLoadProven=false; runtimeObjectIdentityProven=false; runtimeWorldLoadingProven=false; rebuildParityProven=false; noNoticeableDifferenceParityProven=false; privateAssetPublication=false; publicPrivateProofLeak=false; actualAssetImportRows=0; generatedAssetRows=0; outputArtifactRows=0; rawFixtureExampleRows=0; privateFixtureRows=0; runtimeTexturePixelRows=0; runtimeMeshRenderRows=0; runtimeMaterialRows=0; runtimeObservationRows=0; textureRuntimeEvidenceRows=0; meshRuntimeEvidenceRows=0; materialRuntimeEvidenceRows=0; materialVisualReviewRows=0; screenshotRows=0; privateFrameRowsObserved=0; rowObservationRows=0; sourceObservedRows=0; newLaunchRows=0; captureRows=0; ocrRows=0; rawDialogueRows=0; ghidraMutationRows=0; executablePatchRows=0; productUiRows=0; godotRows=0; importerImplementationRows=0; rebuildImplementationRows=0; runtimeCollisionRows=0; cleanRoomRendererRows=0; runtimeResourceArchiveParserRows=0; runtimeSidecarMaterialLoadRows=0; beProcessesAfterMaterialization=0; publicCaseRawRefLeakCount=0; privatePathLeakCount=0; rawArtifactLeakCount=0; privateAssetLeakCount=0; publicPrivateProofLeakCount=0.
