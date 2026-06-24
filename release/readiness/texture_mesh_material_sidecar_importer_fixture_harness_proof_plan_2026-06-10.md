# Texture/Mesh Material Sidecar Importer Fixture Harness Proof Plan Readiness Note

Status: complete static importer harness contract, not runtime proof
Date: 2026-06-10
Scope: `texture-mesh-material-sidecar-importer-fixture-harness-proof-plan`

Canonical display name: Texture / Mesh Material Sidecar Importer Fixture Harness Proof Plan.

Result schema: `texture-mesh-material-sidecar-importer-fixture-harness-proof-plan.v1.json`.

This slice follows the completed Texture / Mesh Material Sidecar Rebuild Fixture Matrix Proof Plan and records the public-safe importer harness contract. It does not implement an importer, launch the game, render textures, run Godot, mutate Ghidra, patch an executable, or claim rebuild parity.

Readiness tokens:

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

Harness case IDs:

- `importer-source-matrix-prerequisite`
- `importer-loose-family-fixture`
- `importer-embedded-family-fixture`
- `importer-non-additive-union-fixture`
- `importer-sidecar-match-mode-fixture`
- `importer-catalog-linkage-fixture`
- `importer-duplicate-output-surplus-fixture`
- `importer-negative-claim-guard-fixture`

Public edge IDs remain `stem-only-sidecar-match-boundary-001` and `ambiguous-catalog-ref-boundary-001`.

Boundary token: runtimeExecution=false; godotWork=false; ghidraMutation=false; executablePatching=false; productUiWired=false; importerImplementation=false; importerExecuted=false; fixtureHarnessExecuted=false; rebuildImplementation=false; runtimeTexturePixelsProven=false; materialVisualCorrectnessProven=false; materialShaderParityProven=false; rebuildParityProven=false; noNoticeableDifferenceParityProven=false; importerImplementationRows=0; actualAssetImportRows=0; privateFixtureRows=0; rawFixtureExampleRows=0; generatedAssetRows=0; outputArtifactRows=0; runtimeObservationRows=0; publicPrivateProofLeak=false.

What this proves:

- The material sidecar matrix now has a deterministic importer harness contract.
- Loose and embedded importer fixtures preserve row-family, unique-ref, sidecar match-mode, catalog linkage, and duplicate-output surplus boundaries.
- The next materialization lane can build/check public-safe harness fixtures without publishing raw texture refs, filenames, paths, hashes, or private row samples.

What remains separate proof:

- Runtime resource archive parser behavior.
- Runtime texture parser behavior and texture pixels.
- Runtime mesh loading, skinning, Direct3D/GPU upload, and material visual correctness.
- Importer implementation.
- Godot work.
- Rebuild implementation, rebuild parity, and no-noticeable-difference parity.
