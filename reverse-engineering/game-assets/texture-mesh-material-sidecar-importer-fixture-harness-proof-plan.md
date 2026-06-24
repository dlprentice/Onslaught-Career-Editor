# Texture/Mesh Material Sidecar Importer Fixture Harness Proof Plan

Status: complete static importer harness contract, not runtime proof
Date: 2026-06-10
Scope: `texture-mesh-material-sidecar-importer-fixture-harness-proof-plan`

Canonical display name: Texture / Mesh Material Sidecar Importer Fixture Harness Proof Plan.

This slice follows the completed [Texture/Mesh Material Sidecar Rebuild Fixture Matrix Proof Plan](texture-mesh-material-sidecar-rebuild-fixture-matrix-proof.md). It converts the public-safe matrix into a deterministic importer harness contract: what fixture groups must exist, which aggregate counts must be asserted, which edge cases must stay synthetic, and which claims remain outside this lane.

Result schema: [texture-mesh-material-sidecar-importer-fixture-harness-proof-plan.v1.json](texture-mesh-material-sidecar-importer-fixture-harness-proof-plan.v1.json).

## Result

- `importerFixtureHarnessStatus=texture-mesh-material-sidecar-importer-fixture-harness-proof-plan-complete-static-importer-harness-contract-not-runtime-proof`
- `previousSlice=Texture / Mesh Material Sidecar Rebuild Fixture Matrix Proof Plan`
- `selectedNextSlice=Texture / Mesh Material Sidecar Importer Fixture Harness Materialization Proof Plan`
- `selectedNextScope=texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan`
- `sourceFixtureMatrixStatus=texture-mesh-material-sidecar-rebuild-fixture-matrix-complete-static-fixture-matrix-not-runtime-proof`
- `harnessDimensionCount=7`
- `harnessCaseCount=8`
- `importerAssertionGroupCount=8`
- `publicSyntheticFixtureCount=8`
- `publicEdgeCaseIdCount=2`
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

## Harness Contract

| Case ID | Harness dimension | Required importer-harness assertion |
| --- | --- | --- |
| `importer-source-matrix-prerequisite` | prerequisite | The harness materialization must require the completed fixture matrix status and the eight matrix case IDs before any importer case is considered valid. |
| `importer-loose-family-fixture` | row family | Loose fixtures must preserve `213` rows, `213` rows with refs, `602` texture-ref instances, `213` unique refs, `213` unique output files, `212` exact matches, `1` stem-only match, `0` missing sidecar refs, and no duplicate-output surplus. |
| `importer-embedded-family-fixture` | row family | Embedded fixtures must preserve `139` rows, `139` rows with refs, `666` texture-ref instances, `28` unique refs, `107` unique output files, `28` duplicate-output groups, and `32` duplicate-output surplus rows. |
| `importer-non-additive-union-fixture` | unique refs | Importer tests must assert the corpus union is `213`; loose `213` plus embedded `28` must remain a non-additive family sum of `241`. |
| `importer-sidecar-match-mode-fixture` | sidecar match mode | Importer tests must distinguish `212` exact filename matches, `1` stem-only match, and `0` missing sidecar refs without publishing raw refs or filenames. |
| `importer-catalog-linkage-fixture` | catalog linkage | Importer tests must assert `352/352` model rows remain catalog-mapped, `4050` catalog rows are available as aggregate context, catalog-missing refs remain `0`, and the single ambiguous catalog ref remains an explicit boundary. |
| `importer-duplicate-output-surplus-fixture` | output uniqueness | Importer tests must preserve embedded row coverage separately from `107` unique output files; `32` is duplicate-output surplus rows and dedupe-to-unique-output behavior is not allowed for row coverage. |
| `importer-negative-claim-guard-fixture` | claim boundary | Runtime parser, texture pixels, mesh loading, Direct3D/GPU, material visual correctness, Godot, Ghidra mutation, executable patching, product UI, rebuild implementation, rebuild parity, and no-noticeable-difference claims remain false. |

## Harness Rules

- The importer fixture harness must be deterministic from public aggregate schema rows only.
- Public synthetic fixture IDs must not contain raw texture refs, paths, filenames, stems, hashes, or private artifact locators.
- Loose row fixtures and embedded row fixtures are separate families.
- Unique model texture refs are a corpus union, not an additive sum of family unique refs.
- Stem-only matching is an explicit boundary case, not a failed sidecar lookup.
- The ambiguous catalog ref is an explicit boundary case, not an arbitrary variant choice.
- Embedded duplicate-output accounting uses surplus rows and must not collapse row coverage to unique output-file coverage.
- The next materialization lane must stay public-safe unless it explicitly uses ignored/private evidence roots and publishes only sanitized counts.

## Source Evidence

This contract is grounded in tracked, public-safe aggregate evidence:

- [Texture/Mesh Material Sidecar Rebuild Fixture Matrix Proof Plan](texture-mesh-material-sidecar-rebuild-fixture-matrix-proof.md)
- [Texture/Mesh Material Sidecar Rebuild Fixture Matrix schema](texture-mesh-material-sidecar-rebuild-fixture-matrix.v1.json)
- [Texture/Mesh Material Sidecar Rebuild Contract Extension Proof Plan](texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.md)
- [Texture/Mesh Material Sidecar Ledger Proof](texture-mesh-material-sidecar-ledger-proof.md)
- [Texture/Mesh Asset Bridge Copied-Corpus Proof](texture-mesh-asset-bridge-copied-corpus-proof.md)
- [Mesh / Resource / Render Static Contract](../binary-analysis/mesh-resource-render-static-contract.md)
- [Texture Resource Decode Static Contract](../binary-analysis/texture-resource-decode-static-contract.md)

## What This Proves

- The material sidecar matrix now has a deterministic importer harness contract.
- The future importer harness has stable aggregate fixtures for loose rows, embedded rows, non-additive texture-ref union accounting, sidecar match modes, catalog linkage, duplicate-output surplus rows, and synthetic edge cases.
- The next implementation-facing lane can materialize/check public-safe harness fixtures without needing raw texture refs, filenames, paths, hashes, or private row samples.

## What Remains Separate Proof

This is a static importer harness contract only. It does not prove runtime resource archive parser behavior, runtime texture parser behavior, runtime texture pixels, JPEG/inflate decode fidelity, runtime mesh loading, runtime mesh skinning, animation behavior, collision behavior, Direct3D upload, GPU behavior, native textured 3D rendering, material visual correctness, material/shader parity, asset format completeness, exact mesh/texture layouts, Godot parity, importer implementation, rebuild implementation, rebuild parity, or no-noticeable-difference parity.

Boundary token: runtimeExecution=false; beLaunch=false; newLaunch=false; screenshotCapture=false; privateFrameReviewPerformed=false; rowObservation=false; sourceSelectionObserved=false; sourceSelectionProven=false; nativeInput=false; debuggerAttachment=false; godotWork=false; ghidraMutation=false; executablePatching=false; productUiWired=false; importerImplementation=false; importerExecuted=false; fixtureHarnessExecuted=false; rebuildImplementation=false; runtimeTextureParserBehaviorProven=false; runtimeTexturePixelsProven=false; runtimeJpegInflateDecodeFidelityProven=false; runtimeMeshLoadingProven=false; runtimeMeshSkinningProven=false; runtimeAnimationBehaviorProven=false; runtimeCollisionBehaviorProven=false; runtimeDirect3DUploadProven=false; runtimeGpuBehaviorProven=false; nativeTextured3DRenderingProven=false; materialVisualCorrectnessProven=false; materialShaderParityProven=false; visualQaComplete=false; cleanRoomRendererImplemented=false; assetFormatCompletenessProven=false; exactMeshTextureLayoutsProven=false; runtimeResourceArchiveParserProven=false; runtimeSidecarMaterialLoadProven=false; runtimeObjectIdentityProven=false; runtimeWorldLoadingProven=false; rebuildParityProven=false; noNoticeableDifferenceParityProven=false; privateAssetPublication=false; publicPrivateProofLeak=false; runtimeObservationRows=0; textureRuntimeEvidenceRows=0; meshRuntimeEvidenceRows=0; materialRuntimeEvidenceRows=0; materialVisualReviewRows=0; screenshotRows=0; privateFrameRowsObserved=0; rowObservationRows=0; sourceObservedRows=0; newLaunchRows=0; captureRows=0; ocrRows=0; rawDialogueRows=0; ghidraMutationRows=0; executablePatchRows=0; productUiRows=0; godotRows=0; importerImplementationRows=0; actualAssetImportRows=0; privateFixtureRows=0; rawFixtureExampleRows=0; generatedAssetRows=0; outputArtifactRows=0; rebuildImplementationRows=0; runtimeTexturePixelRows=0; runtimeMeshRenderRows=0; runtimeMaterialRows=0; runtimeCollisionRows=0; cleanRoomRendererRows=0; runtimeResourceArchiveParserRows=0; runtimeSidecarMaterialLoadRows=0; beProcessesAfterSelection=0.
