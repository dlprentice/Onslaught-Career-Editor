# Texture/Mesh Material Sidecar Rebuild Fixture Matrix Proof Plan

Status: complete static fixture matrix, not runtime proof
Date: 2026-06-10
Scope: `texture-mesh-material-sidecar-rebuild-fixture-matrix-proof-plan`

Canonical display name: Texture / Mesh Material Sidecar Rebuild Fixture Matrix Proof Plan.

This slice follows the completed [Texture/Mesh Material Sidecar Rebuild Contract Extension Proof Plan](texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.md). It turns the stable material sidecar vocabulary into a public-safe fixture matrix for clean-room importer planning without publishing raw texture references, filenames, paths, hashes, private artifacts, or row-level samples.

Result schema: [texture-mesh-material-sidecar-rebuild-fixture-matrix.v1.json](texture-mesh-material-sidecar-rebuild-fixture-matrix.v1.json).

## Result

- `fixtureMatrixStatus=texture-mesh-material-sidecar-rebuild-fixture-matrix-complete-static-fixture-matrix-not-runtime-proof`
- `previousSlice=Texture / Mesh Material Sidecar Rebuild Contract Extension Proof Plan`
- `selectedNextSlice=Texture / Mesh Material Sidecar Importer Fixture Harness Proof Plan`
- `selectedNextScope=texture-mesh-material-sidecar-importer-fixture-harness-proof-plan`
- `matrixDimensionCount=7`
- `fixtureCaseCount=8`
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
- `publicEdgeCaseIdCount=2`
- `publicLeakCheck=PASS`

Static context remains `6411/6411 = 100.00%`, `0 / 0 / 0`, `1560/1560 = 100.00%`, `1179/1179 = 100.00%`, and `remainingActiveFocusedWork=0`.

## Fixture Matrix

| Case ID | Dimension | Public invariant |
| --- | --- | --- |
| `loose-row-family-coverage` | row family | loose rows `213`, rows with refs `213`, texture-ref instances `602`, unique refs `213`, unique output files `213`, duplicate-output groups `0`, duplicate-output surplus rows `0`. |
| `embedded-row-family-coverage` | row family | embedded rows `139`, rows with refs `139`, texture-ref instances `666`, unique refs `28`, unique output files `107`, duplicate-output groups `28`, duplicate-output surplus rows `32`. |
| `corpus-unique-ref-union-coverage` | unique refs | corpus union is `213`; loose `213` plus embedded `28` is not additive and must not become `241`. |
| `sidecar-match-mode-coverage` | sidecar match mode | `213` sidecar files cover `213` unique refs with `212` exact filename matches, `1` stem-only match, and `0` missing sidecar refs. |
| `catalog-linkage-coverage` | catalog linkage | `352/352` model rows have all texture refs catalog-mapped; catalog rows `4050`; catalog-missing refs `0`; ambiguous catalog refs `1`. |
| `embedded-duplicate-output-boundary` | output uniqueness | embedded row coverage remains `139` rows even though copied output has `107` unique output files; the `32` count is duplicate-output surplus rows, not all participating rows. |
| `public-edge-case-id-coverage` | public edge cases | `stem-only-sidecar-match-boundary-001` and `ambiguous-catalog-ref-boundary-001` represent the two singleton boundaries without raw refs, stems, filenames, paths, or hashes. |
| `negative-claim-guard` | proof boundary | runtime, render, material visual, Godot, Ghidra mutation, executable patching, rebuild implementation, rebuild parity, and no-noticeable-difference claims remain false. |

## Matrix Rules

- Row coverage and unique output-file coverage are separate dimensions.
- Unique model texture refs are a corpus union, not a sum of loose and embedded family unique-ref counts.
- Exact filename matches and stem-only matches are separate fixture outcomes.
- The single ambiguous catalog ref is a named boundary, not a failure and not an arbitrary catalog-variant selection.
- Embedded duplicate-output accounting uses `duplicateOutputSurplusRows=32` for surplus rows beyond first outputs; it does not claim all rows participating in duplicate-output groups.
- Public fixture IDs are synthetic and stable. They must not contain raw texture references, path separators, file extensions, catalog filenames, stems, hashes, or private artifact locators.

## Source Evidence

This matrix is grounded in tracked, public-safe aggregate evidence:

- [Texture/Mesh Material Sidecar Rebuild Contract Extension Proof Plan](texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.md)
- [Texture/Mesh Material Sidecar Rebuild Contract Extension schema](texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.v1.json)
- [Texture/Mesh Material Sidecar Ledger Proof](texture-mesh-material-sidecar-ledger-proof.md)
- [Texture/Mesh Asset Bridge Copied-Corpus Proof](texture-mesh-asset-bridge-copied-corpus-proof.md)
- [Mesh / Resource / Render Static Contract](../binary-analysis/mesh-resource-render-static-contract.md)
- [Texture Resource Decode Static Contract](../binary-analysis/texture-resource-decode-static-contract.md)

The matrix deliberately does not require ignored/private proof roots for default validation.

## What This Proves

- The material sidecar rebuild contract has a public-safe fixture matrix for row families, texture-ref union coverage, sidecar match modes, catalog linkage, duplicate-output boundaries, and singleton edge-case IDs.
- Clean-room importer planning can test loose and embedded row accounting without collapsing embedded row coverage into unique output-file coverage.
- The one stem-only sidecar boundary and one ambiguous catalog boundary are retained as explicit public-safe cases.

## What Remains Separate Proof

This is a static fixture matrix only. It does not prove runtime resource archive parser behavior, runtime texture parser behavior, runtime texture pixels, JPEG/inflate decode fidelity, runtime mesh loading, runtime mesh skinning, animation behavior, collision behavior, Direct3D upload, GPU behavior, native textured 3D rendering, material visual correctness, material/shader parity, asset format completeness, exact mesh/texture layouts, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.

Boundary token: runtimeExecution=false; beLaunch=false; newLaunch=false; screenshotCapture=false; privateFrameReviewPerformed=false; rowObservation=false; sourceSelectionObserved=false; sourceSelectionProven=false; nativeInput=false; debuggerAttachment=false; godotWork=false; ghidraMutation=false; executablePatching=false; productUiWired=false; rebuildImplementation=false; runtimeTextureParserBehaviorProven=false; runtimeTexturePixelsProven=false; runtimeJpegInflateDecodeFidelityProven=false; runtimeMeshLoadingProven=false; runtimeMeshSkinningProven=false; runtimeAnimationBehaviorProven=false; runtimeCollisionBehaviorProven=false; runtimeDirect3DUploadProven=false; runtimeGpuBehaviorProven=false; nativeTextured3DRenderingProven=false; materialVisualCorrectnessProven=false; materialShaderParityProven=false; visualQaComplete=false; cleanRoomRendererImplemented=false; assetFormatCompletenessProven=false; exactMeshTextureLayoutsProven=false; runtimeResourceArchiveParserProven=false; runtimeSidecarMaterialLoadProven=false; runtimeObjectIdentityProven=false; runtimeWorldLoadingProven=false; rebuildParityProven=false; noNoticeableDifferenceParityProven=false; privateAssetPublication=false; publicPrivateProofLeak=false; runtimeObservationRows=0; textureRuntimeEvidenceRows=0; meshRuntimeEvidenceRows=0; materialRuntimeEvidenceRows=0; materialVisualReviewRows=0; screenshotRows=0; privateFrameRowsObserved=0; rowObservationRows=0; sourceObservedRows=0; newLaunchRows=0; captureRows=0; ocrRows=0; rawDialogueRows=0; ghidraMutationRows=0; executablePatchRows=0; productUiRows=0; godotRows=0; rebuildImplementationRows=0; runtimeTexturePixelRows=0; runtimeMeshRenderRows=0; runtimeMaterialRows=0; runtimeCollisionRows=0; cleanRoomRendererRows=0; runtimeResourceArchiveParserRows=0; runtimeSidecarMaterialLoadRows=0; beProcessesAfterSelection=0.
