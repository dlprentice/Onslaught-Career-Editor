# Texture/Mesh Material Sidecar Importer Private Corpus Safety Boundary Proof Plan

Status: complete public-safe private-corpus safety boundary, no private corpus read
Date: 2026-06-10
Scope: `texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-proof-plan`

Canonical display name: Texture / Mesh Material Sidecar Importer Private Corpus Safety Boundary Proof Plan.

This slice follows the completed [Texture/Mesh Material Sidecar Importer Public Contract Skeleton Implementation Proof Plan](texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-proof-plan.md). It defines the safety packet required before any later private-corpus manifest/checklist work. It does not read private assets, enumerate private roots, check private-root existence, execute a real importer, emit imported assets, launch BEA, mutate Ghidra, patch executables, use Godot, wire product UI, implement a renderer, or claim rebuild/no-noticeable-difference parity.

Boundary module: `tools/texture_mesh_material_sidecar_importer_private_corpus_safety_boundary.py`.

Machine-checkable schema: [texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-proof-plan.v1.json](texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-proof-plan.v1.json).

## Result

- `privateCorpusSafetyBoundaryStatus=texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-defined-no-private-corpus-read`
- `previousSlice=Texture / Mesh Material Sidecar Importer Public Contract Skeleton Implementation Proof Plan`
- `previousScope=texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-proof-plan`
- `selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Safety Packet Checklist Population Proof Plan`
- `selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-safety-packet-checklist-population-proof-plan`
- `sourcePublicContractSkeletonStatus=texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-complete-public-contract-only-not-real-importer-proof`
- `sourceProofCount=8`
- `publicContractSkeletonImplemented=true`
- `contractSkeletonValidationExecuted=true`
- `contractInterfaceCount=6`
- `implementedContractInterfaceCount=6`
- `contractFunctionCount=2`
- `publicContractSkeletonImplementationRows=1`
- `validationSummaryRows=1`
- `skeletonContractCheckCount=46`
- `failedSkeletonContractChecks=0`
- `sourceConsumedFixtureRowCount=8`
- `publicEdgeCaseIdCount=2`
- `uniqueModelTextureRefUnion=213`
- `familyUniqueRefsAreNotAdditive=true`
- `embeddedDuplicateOutputSurplusRows=32`
- `safetyBoundaryOnly=true`
- `privateCorpusSafetyBoundaryDefined=true`
- `privateCorpusReadAuthorizationPresent=false`
- `explicitImporterImplementationArmPresent=false`
- `operatorPrivateOutputReviewAvailable=false`
- `privateAssetRead=false`
- `privateCorpusReadPerformed=false`
- `privateCorpusEnumeration=false`
- `privateRootExistenceChecked=false`
- `privateAssetReadPerformed=false`
- `privateManifestMaterialized=false`
- `privateManifestRowsObserved=false`
- `realImporterImplementation=false`
- `realImporterExecuted=false`
- `futurePrivateCorpusReadRequiresExplicitArm=true`
- `requiresCopiedOrAppOwnedCorpusRoot=true`
- `requiresAppOwnedArtifactRoot=true`
- `installedGameMutationAllowed=false`
- `originalExecutableMutationAllowed=false`
- `publicPrivateSeparationRequired=true`
- `safetyPacketItemCount=10`
- `authorizationGateCount=8`
- `privateCorpusClassCount=5`
- `redactedFieldCount=12`
- `publicAllowedOutputClassCount=6`
- `stopConditionCount=12`
- `falseGuardCount=45`
- `zeroCounterCount=36`
- `publicLeakCheck=PASS`

Static context remains `6411/6411 = 100.00%`, `0 / 0 / 0`, `1560/1560 = 100.00%`, `1179/1179 = 100.00%`, and `remainingActiveFocusedWork=0`.

## Safety Packet

The private-corpus safety packet has these public class tokens only:

- `copied-or-app-owned-private-corpus-root-required`
- `installed-game-remains-read-only`
- `original-executable-remains-read-only`
- `app-owned-output-root-required`
- `public-private-separation-manifest-required`
- `no-public-raw-texture-ref-publication`
- `no-public-private-path-publication`
- `dry-run-before-importer-execution`
- `leak-check-before-public-docs`
- `stop-on-missing-explicit-private-corpus-arm`

Authorization gates:

- `explicit-private-corpus-read-arm-required`
- `operator-private-output-review-required`
- `copied-or-app-owned-corpus-root-required`
- `app-owned-artifact-root-required`
- `installed-game-mutation-forbidden`
- `original-executable-mutation-forbidden`
- `public-redaction-policy-required`
- `dry-run-before-output-materialization`

Future private-corpus classes are public labels only:

- `loose-texture-sidecar-private-corpus`
- `loose-mesh-sidecar-private-corpus`
- `embedded-mesh-output-private-corpus`
- `asset-catalog-linkage-private-corpus`
- `importer-generated-output-private-corpus`

Allowed public outputs remain `class-counts`, `status-tokens`, `claim-boundary`, `redaction-field-counts`, `no-private-paths`, and `no-raw-texture-refs`.

## Redaction Policy

`redactionPolicy=public-safe-class-count-status-token-only`. Public docs may not include concrete private corpus roots, concrete resource archive paths, concrete sidecar paths, concrete output paths, raw texture references, raw filenames/stems, private digests, private byte lengths, operator profile identifiers, process/window identifiers, raw importer stdout/stderr, screenshots, or frame locators.

This slice records `redactedFieldCount=12` and `publicLeakCheck=PASS`.

## Stop Conditions

Stop and record a bounded deferred result if a later pass requires:

- a private corpus path written to public docs
- raw texture references, stems, filenames, digests, or byte counts published
- private asset reads before an explicit private-corpus arm
- real importer execution before a dry-run safety-packet checklist exists
- generated/imported assets outside an app-owned artifact root
- installed game files or original executable mutation
- runtime parser, pixel, mesh-loading, Direct3D, GPU, or material visual behavior inferred from this boundary
- Godot, product UI, renderer, rebuild, or no-noticeable-difference parity inferred from this boundary
- public and private proof artifacts that cannot be separated
- operator private-output review unavailable when private outputs would be produced
- a leak check that cannot distinguish class/count summaries from raw private evidence
- a public skeleton source that no longer selects this private-corpus boundary

## Boundary Token

privateCorpusReadAuthorizationPresent=false; explicitImporterImplementationArmPresent=false; operatorPrivateOutputReviewAvailable=false; privateAssetRead=false; privateCorpusReadPerformed=false; privateCorpusEnumeration=false; privateRootExistenceChecked=false; privateAssetReadPerformed=false; privateManifestMaterialized=false; privateManifestRowsObserved=false; realImporterImplementation=false; realImporterExecuted=false; importerImplementation=false; importerExecuted=false; actualAssetImport=false; generatedAssetOutputs=false; privateAssetPublication=false; runtimeExecution=false; beLaunch=false; newLaunch=false; screenshotCapture=false; nativeInput=false; debuggerAttachment=false; godotWork=false; ghidraMutation=false; executablePatching=false; productUiWired=false; rendererImplementation=false; rebuildImplementation=false; runtimeResourceArchiveParserProven=false; runtimeTextureParserBehaviorProven=false; runtimeTexturePixelsProven=false; runtimeMeshLoadingProven=false; runtimeMeshSkinningProven=false; runtimeDirect3DUploadProven=false; runtimeGpuBehaviorProven=false; nativeTextured3DRenderingProven=false; materialVisualCorrectnessProven=false; materialShaderParityProven=false; visualQaComplete=false; assetFormatCompletenessProven=false; exactMeshTextureLayoutsProven=false; rebuildParityProven=false; noNoticeableDifferenceParityProven=false; publicPrivateProofLeak=false; privateCorpusReadRows=0; privateAssetReadRows=0; privateManifestRows=0; actualAssetImportRows=0; generatedAssetRows=0; outputArtifactRows=0; dryRunOutputArtifactRows=0; rawFixtureExampleRows=0; privateFixtureRows=0; privateArtifactRows=0; privatePathRows=0; rawPathRows=0; rawFilenameRows=0; rawHashRows=0; privateHashRows=0; rawTextureRefRows=0; publishedPrivatePathRows=0; publishedRawRefRows=0; publicCaseRawRefLeakCount=0; privatePathLeakCount=0; rawArtifactLeakCount=0; privateAssetLeakCount=0; publicPrivateProofLeakCount=0; runtimeObservationRows=0; runtimeTexturePixelRows=0; runtimeMeshRenderRows=0; runtimeMaterialRows=0; screenshotRows=0; captureRows=0; ghidraMutationRows=0; executablePatchRows=0; productUiRows=0; godotRows=0; realImporterImplementationRows=0; rebuildImplementationRows=0; beProcessesAfterPrivateCorpusBoundary=0.

## What This Proves

- The completed public contract skeleton has an explicit private-corpus safety boundary.
- Future private-corpus work must use copied or app-owned roots and app-owned artifact outputs.
- Future public results are limited to class/count/status-token summaries and redacted field counts.
- Private corpus reads and real importer execution remain unperformed in this slice.

## What Remains Separate Proof

This is a boundary proof only. It does not prove private asset import, private corpus manifest materialization, real importer implementation, real importer execution, runtime resource archive parser behavior, runtime texture parser behavior, runtime texture pixels, JPEG/inflate decode fidelity, runtime mesh loading or skinning, Direct3D upload or GPU behavior, native textured 3D rendering, material visual correctness, material/shader parity, asset format completeness, exact mesh or texture layouts, product UI behavior, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
