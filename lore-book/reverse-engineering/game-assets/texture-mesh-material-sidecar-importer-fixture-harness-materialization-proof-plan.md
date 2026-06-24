# Texture/Mesh Material Sidecar Importer Fixture Harness Materialization Proof Plan

Status: complete public-safe deterministic fixture row materialization, not runtime proof
Date: 2026-06-10
Scope: `texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan`

Canonical display name: Texture / Mesh Material Sidecar Importer Fixture Harness Materialization Proof Plan.

This slice follows the completed [Texture/Mesh Material Sidecar Importer Fixture Harness Proof Plan](texture-mesh-material-sidecar-importer-fixture-harness-proof-plan.md). It materializes the importer harness contract into eight deterministic, public-safe fixture rows. The rows carry only aggregate counts, synthetic fixture IDs, public edge-case IDs, and claim-boundary flags.

Result schema: [texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan.v1.json](texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan.v1.json).

## Result

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

Public edge IDs remain `stem-only-sidecar-match-boundary-001` and `ambiguous-catalog-ref-boundary-001`.

Static context remains `6411/6411 = 100.00%`, `0 / 0 / 0`, `1560/1560 = 100.00%`, `1179/1179 = 100.00%`, and `remainingActiveFocusedWork=0`.

Probe anchors: `213 + 139 = 352`; `602 + 666 = 1268`; `213 + 28 = 241`; `139 - 107 = 32`; `rawRefPublished=false`; `rawStemPublished=false`; `catalogVariantPublished=false`.

## Materialized Fixture Rows

| Fixture row ID | Dimension | Assertion group | Materialized claim |
| --- | --- | --- | --- |
| `importer-source-matrix-prerequisite` | prerequisite | source matrix | Requires the completed source fixture matrix status and the eight source harness case IDs before importer fixture consumption is valid. |
| `importer-loose-family-fixture` | row family | loose row family | Materializes loose aggregate counts: `213` rows, `213` rows with refs, `602` texture-ref instances, `213` unique refs, `213` unique output files, `212` exact matches, `1` stem-only match, `0` missing sidecar refs, and no duplicate-output surplus. |
| `importer-embedded-family-fixture` | row family | embedded row family | Materializes embedded aggregate counts: `139` rows, `139` rows with refs, `666` texture-ref instances, `28` unique refs, `107` unique output files, `28` duplicate-output groups, and `32` duplicate-output surplus rows. |
| `importer-non-additive-union-fixture` | unique refs | non-additive union | Materializes the non-additive texture-ref relation: corpus union `213`; loose `213` plus embedded `28` equals family sum `241`; family unique refs are not additive. |
| `importer-sidecar-match-mode-fixture` | sidecar match mode | sidecar matching | Materializes sidecar match-mode counts: `213` sidecar files, `212` exact filename matches, `1` stem-only match, `0` missing sidecar refs, and the public edge ID `stem-only-sidecar-match-boundary-001`. |
| `importer-catalog-linkage-fixture` | catalog linkage | catalog linkage | Materializes catalog linkage counts: `352/352` model rows with texture refs are catalog-mapped, `4050` catalog rows exist as aggregate context, `0` catalog-missing refs, and `1` ambiguous catalog ref with public edge ID `ambiguous-catalog-ref-boundary-001`. |
| `importer-duplicate-output-surplus-fixture` | output uniqueness | duplicate output surplus | Materializes embedded row coverage separately from output uniqueness: `139` embedded rows, `107` unique output files, `28` duplicate-output groups, `32` duplicate-output surplus rows, and dedupe-to-unique-output behavior disallowed for row coverage. |
| `importer-negative-claim-guard-fixture` | claim boundary | negative claim guard | Materializes false guards and zero counters for runtime, private evidence, Ghidra mutation, executable patching, Godot, product UI, real importer execution, rebuild implementation, rebuild parity, and no-noticeable-difference parity. |

## Derived Assertions

- `213 loose rows + 139 embedded rows = 352 model rows with texture refs`
- `602 loose texture-ref instances + 666 embedded texture-ref instances = 1268 model texture-ref instances`
- `213 loose unique refs + 28 embedded unique refs = 241 family unique-ref sum`
- `uniqueModelTextureRefUnion=213`, so family unique refs are not additive
- `139 embedded rows - 107 embedded unique output files = 32 embedded duplicate-output surplus rows`
- `352/352 model rows with texture refs` remain catalog-mapped while `catalogMissingRefs=0`

## Public-Safety Rules

- Public fixture rows use synthetic IDs only.
- Public fixture rows do not publish raw texture refs, raw stems, filenames, paths, hashes, catalog variants, source rows, output artifacts, private frames, or private asset locators.
- The stem-only sidecar match remains a count and public edge ID, not a raw sample.
- The ambiguous catalog ref remains a count and public edge ID, not a chosen catalog variant.
- Loose and embedded families remain separate; unique refs are a corpus union, not an additive family sum.
- Embedded duplicate-output rows remain row-coverage evidence and are not collapsed into unique output-file coverage.

## Source Evidence

This materialization is grounded in tracked, public-safe aggregate evidence:

- [Texture/Mesh Material Sidecar Importer Fixture Harness Proof Plan](texture-mesh-material-sidecar-importer-fixture-harness-proof-plan.md)
- [Texture/Mesh Material Sidecar Importer Fixture Harness schema](texture-mesh-material-sidecar-importer-fixture-harness-proof-plan.v1.json)
- [Texture/Mesh Material Sidecar Rebuild Fixture Matrix Proof Plan](texture-mesh-material-sidecar-rebuild-fixture-matrix-proof.md)
- [Texture/Mesh Material Sidecar Rebuild Contract Extension Proof Plan](texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.md)
- [Texture/Mesh Material Sidecar Ledger Proof](texture-mesh-material-sidecar-ledger-proof.md)
- [Texture/Mesh Asset Bridge Copied-Corpus Proof](texture-mesh-asset-bridge-copied-corpus-proof.md)
- [Mesh / Resource / Render Static Contract](../binary-analysis/mesh-resource-render-static-contract.md)
- [Texture Resource Decode Static Contract](../binary-analysis/texture-resource-decode-static-contract.md)

## What This Proves

- The importer fixture harness contract now has eight deterministic public-safe fixture rows.
- The fixture rows preserve loose and embedded row-family counts, non-additive texture-ref union accounting, sidecar match modes, catalog linkage, duplicate-output surplus rows, and public synthetic edge cases.
- A future consumer dry-run can validate importer-facing fixture consumption without using raw texture refs, filenames, paths, hashes, private row samples, private frames, or generated asset outputs.

## What Remains Separate Proof

This is public-safe fixture row materialization only. It does not prove runtime resource archive parser behavior, runtime texture parser behavior, runtime texture pixels, JPEG/inflate decode fidelity, runtime mesh loading, runtime mesh skinning, animation behavior, collision behavior, Direct3D upload, GPU behavior, native textured 3D rendering, material visual correctness, material/shader parity, asset format completeness, exact mesh/texture layouts, runtime sidecar material loading, runtime object identity, runtime world loading, Godot parity, real importer implementation, real importer execution, fixture-harness consumer execution, rebuild implementation, rebuild parity, or no-noticeable-difference parity.

Boundary token: runtimeExecution=false; beLaunch=false; newLaunch=false; screenshotCapture=false; privateFrameReviewPerformed=false; rowObservation=false; sourceSelectionObserved=false; sourceSelectionProven=false; nativeInput=false; debuggerAttachment=false; godotWork=false; ghidraMutation=false; executablePatching=false; productUiWired=false; realImporterImplementation=false; realImporterExecuted=false; importerImplementation=false; importerExecuted=false; fixtureHarnessExecuted=false; fixtureHarnessConsumerExecuted=false; rebuildImplementation=false; runtimeTextureParserBehaviorProven=false; runtimeTexturePixelsProven=false; runtimeJpegInflateDecodeFidelityProven=false; runtimeMeshLoadingProven=false; runtimeMeshSkinningProven=false; runtimeAnimationBehaviorProven=false; runtimeCollisionBehaviorProven=false; runtimeDirect3DUploadProven=false; runtimeGpuBehaviorProven=false; nativeTextured3DRenderingProven=false; materialVisualCorrectnessProven=false; materialShaderParityProven=false; visualQaComplete=false; cleanRoomRendererImplemented=false; assetFormatCompletenessProven=false; exactMeshTextureLayoutsProven=false; runtimeResourceArchiveParserProven=false; runtimeSidecarMaterialLoadProven=false; runtimeObjectIdentityProven=false; runtimeWorldLoadingProven=false; rebuildParityProven=false; noNoticeableDifferenceParityProven=false; privateAssetPublication=false; publicPrivateProofLeak=false; actualAssetImportRows=0; generatedAssetRows=0; outputArtifactRows=0; rawFixtureExampleRows=0; privateFixtureRows=0; runtimeTexturePixelRows=0; runtimeMeshRenderRows=0; runtimeMaterialRows=0; runtimeObservationRows=0; textureRuntimeEvidenceRows=0; meshRuntimeEvidenceRows=0; materialRuntimeEvidenceRows=0; materialVisualReviewRows=0; screenshotRows=0; privateFrameRowsObserved=0; rowObservationRows=0; sourceObservedRows=0; newLaunchRows=0; captureRows=0; ocrRows=0; rawDialogueRows=0; ghidraMutationRows=0; executablePatchRows=0; productUiRows=0; godotRows=0; importerImplementationRows=0; rebuildImplementationRows=0; runtimeCollisionRows=0; cleanRoomRendererRows=0; runtimeResourceArchiveParserRows=0; runtimeSidecarMaterialLoadRows=0; beProcessesAfterMaterialization=0; publicCaseRawRefLeakCount=0; privatePathLeakCount=0; rawArtifactLeakCount=0; privateAssetLeakCount=0; publicPrivateProofLeakCount=0.
