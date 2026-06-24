# Texture/Mesh Material Sidecar Rebuild Fixture Matrix Readiness Note

Status: complete static fixture matrix, not runtime proof
Date: 2026-06-10
Scope: `texture-mesh-material-sidecar-rebuild-fixture-matrix-proof-plan`

Canonical display name: Texture / Mesh Material Sidecar Rebuild Fixture Matrix Proof Plan.
Result schema: `texture-mesh-material-sidecar-rebuild-fixture-matrix.v1.json`.

This slice records a public-safe fixture matrix for the texture/mesh material sidecar rebuild contract. It uses tracked sanitized docs/schema only for default validation.

Core result:

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
- `duplicateOutputSurplusRows=32`
- `publicEdgeCaseIdCount=2`
- `publicLeakCheck=PASS`

Representative case IDs: `loose-row-family-coverage`, `embedded-row-family-coverage`, `corpus-unique-ref-union-coverage`, `sidecar-match-mode-coverage`, `catalog-linkage-coverage`, `embedded-duplicate-output-boundary`, `public-edge-case-id-coverage`, and `negative-claim-guard`.

Public edge case IDs: `stem-only-sidecar-match-boundary-001` and `ambiguous-catalog-ref-boundary-001`.

Boundary token: runtimeExecution=false; beLaunch=false; newLaunch=false; screenshotCapture=false; privateFrameReviewPerformed=false; nativeInput=false; debuggerAttachment=false; godotWork=false; ghidraMutation=false; executablePatching=false; productUiWired=false; rebuildImplementation=false; runtimeTexturePixelsProven=false; materialVisualCorrectnessProven=false; materialShaderParityProven=false; rebuildParityProven=false; noNoticeableDifferenceParityProven=false.
