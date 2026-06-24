# Texture/Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Dry-Run Proof Plan

Status: complete redacted read-only manifest-shape dry run
Date: 2026-06-10
Scope: `texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-dry-run-proof-plan`

Canonical display name: Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Dry-Run Proof Plan.

This slice follows the completed [Texture/Mesh Material Sidecar Importer Private Corpus Read-Only Inventory Preflight Proof Plan](texture-mesh-material-sidecar-importer-private-corpus-read-only-inventory-preflight-proof-plan.md). It performs a bounded read-only manifest-shape dry run using redacted class/count/status-token inventory evidence only. It does not publish raw private paths, raw filenames, raw stems, raw texture references, raw mesh references, hashes, byte lengths, directory listings, or importer output. It does not read asset content bytes, materialize a private manifest, observe private manifest rows, implement or execute a real importer, emit imported assets, launch BEA, mutate the installed game, mutate the original executable, mutate Ghidra, patch executables, use Godot, wire product UI, implement a renderer, implement a rebuild, or claim rebuild/no-noticeable-difference parity.

Dry-run module: `tools/texture_mesh_material_sidecar_importer_private_corpus_readonly_manifest_dry_run.py`.

Machine-checkable schema: [texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-dry-run-proof-plan.v1.json](texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-dry-run-proof-plan.v1.json).

## Result

- `privateCorpusReadOnlyManifestDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-dry-run-complete-redacted-class-manifest-shape-no-content-read`
- `previousSlice=Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Inventory Preflight Proof Plan`
- `previousScope=texture-mesh-material-sidecar-importer-private-corpus-read-only-inventory-preflight-proof-plan`
- `selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Materialization Proof Plan`
- `selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-materialization-proof-plan`
- `sourcePreflightStatus=texture-mesh-material-sidecar-importer-private-corpus-read-only-inventory-preflight-complete-redacted-class-count-summary-no-content-read`
- `sourceProofCount=11`
- `readOnlyManifestDryRunOnly=true`
- `privateCorpusReadOnlyManifestDryRunExecuted=true`
- `privateCorpusRootClassEvidenceConsumed=true`
- `archiveClassSummaryConsumed=true`
- `redactedManifestShapeGenerated=true`
- `manifestClassRowsGenerated=true`
- `privateEvidenceStoredOutsidePublicReleaseScope=true`
- `privateAssetContentRead=false`
- `privateArchiveBytesRead=false`
- `privateManifestMaterialized=false`
- `privateManifestRowsObserved=false`
- `privateManifestRowsPublished=false`
- `realImporterImplementation=false`
- `realImporterExecuted=false`
- `installedGameMutationAllowed=false`
- `originalExecutableMutationAllowed=false`
- `publicPrivateSeparationRequired=true`
- `sourceRootClass=user-owned-installed-or-copied-game-resource-root`
- `resourceRootExists=true`
- `resourceDirectoryExists=true`
- `requiredArchiveClassCount=5`
- `observedRequiredArchiveClassCount=5`
- `allRequiredArchiveClassesObserved=true`
- `ayaArchiveTotalCount=301`
- `baseArchiveClassCount=1`
- `frontendArchiveClassCount=1`
- `loadingArchiveClassCount=1`
- `numericLevelArchiveClassCount=66`
- `goodieArchiveClassCount=232`
- `unknownAyaArchiveClassCount=0`
- `manifestDryRunClassRowCount=5`
- `manifestDryRunArchiveTotalCount=301`
- `manifestDryRunSummaryRows=1`
- `publicAllowedOutputCount=8`
- `redactedFieldCount=14`
- `falseGuardCount=39`
- `zeroCounterCount=34`
- `publicLeakCheck=PASS`

Static context remains `6411/6411 = 100.00%`, `0 / 0 / 0`, `1560/1560 = 100.00%`, `1179/1179 = 100.00%`, and `remainingActiveFocusedWork=0`.

## Redacted Manifest Shape

The dry run publishes only synthetic archive-class manifest rows:

| Archive class | Count | Row mode |
| --- | ---: | --- |
| `base-resource-archive` | `1` | `class-count-status-token-only` |
| `frontend-resource-archive` | `1` | `class-count-status-token-only` |
| `loading-resource-archive` | `1` | `class-count-status-token-only` |
| `numeric-level-resource-archive` | `66` | `class-count-status-token-only` |
| `goodie-resource-archive` | `232` | `class-count-status-token-only` |

Each row records `privateAssetContentRead=false`, `privateArchiveBytesRead=false`, `rawPathRows=0`, `rawFilenameRows=0`, `rawTextureRefRows=0`, `rawMeshRefRows=0`, and `byteLengthRows=0`.

## Redaction Policy

Allowed public outputs are `resource-root-existence-status`, `resource-directory-existence-status`, `archive-class-counts`, `required-class-coverage-status`, `redacted-manifest-class-rows`, `manifest-dry-run-row-counts`, `redaction-field-counts`, and `claim-boundary`.

Redacted fields are private corpus roots, concrete archive paths, concrete resource directory paths, raw resource filenames, raw resource stems, raw texture references, raw mesh references, private digests, private byte lengths, operator profile identifiers, raw directory listings, raw importer stdout/stderr, raw private manifest rows, and private manifest output paths.

## Boundary Token

readOnlyManifestDryRunOnly=true; privateCorpusReadOnlyManifestDryRunExecuted=true; privateCorpusRootClassEvidenceConsumed=true; archiveClassSummaryConsumed=true; redactedManifestShapeGenerated=true; manifestClassRowsGenerated=true; privateEvidenceStoredOutsidePublicReleaseScope=true; privateAssetContentRead=false; privateArchiveBytesRead=false; privateManifestMaterialized=false; privateManifestRowsObserved=false; privateManifestRowsPublished=false; realImporterImplementation=false; realImporterExecuted=false; privateImporterDryRunExecuted=false; installedGameMutationAllowed=false; originalExecutableMutationAllowed=false; importerImplementation=false; importerExecuted=false; actualAssetImport=false; generatedAssetOutputs=false; privateAssetPublication=false; runtimeExecution=false; beLaunch=false; newLaunch=false; screenshotCapture=false; nativeInput=false; debuggerAttachment=false; godotWork=false; ghidraMutation=false; executablePatching=false; productUiWired=false; rendererImplementation=false; rebuildImplementation=false; runtimeResourceArchiveParserProven=false; runtimeTextureParserBehaviorProven=false; runtimeTexturePixelsProven=false; runtimeMeshLoadingProven=false; runtimeMeshSkinningProven=false; runtimeDirect3DUploadProven=false; runtimeGpuBehaviorProven=false; nativeTextured3DRenderingProven=false; materialVisualCorrectnessProven=false; materialShaderParityProven=false; visualQaComplete=false; assetFormatCompletenessProven=false; exactMeshTextureLayoutsProven=false; rebuildParityProven=false; noNoticeableDifferenceParityProven=false; publicPrivateProofLeak=false; rawPathRows=0; rawFilenameRows=0; rawStemRows=0; rawHashRows=0; privateHashRows=0; byteLengthRows=0; rawTextureRefRows=0; rawMeshRefRows=0; privateManifestRows=0; privateManifestOutputRows=0; privateManifestPublishedRows=0; actualAssetImportRows=0; generatedAssetRows=0; outputArtifactRows=0; privateArtifactRows=0; publishedPrivatePathRows=0; publishedRawRefRows=0; privatePathLeakCount=0; rawArtifactLeakCount=0; privateAssetLeakCount=0; publicPrivateProofLeakCount=0; runtimeObservationRows=0; runtimeTexturePixelRows=0; runtimeMeshRenderRows=0; runtimeMaterialRows=0; screenshotRows=0; captureRows=0; ghidraMutationRows=0; executablePatchRows=0; productUiRows=0; godotRows=0; realImporterImplementationRows=0; rebuildImplementationRows=0; mutationRows=0.

## What This Proves

- The selected read-only manifest dry run can consume redacted archive class/count/status evidence.
- The dry run generated five synthetic manifest class rows without publishing raw private paths, filenames, hashes, byte lengths, texture references, mesh references, or directory listings.
- The dry run preserved the prior required archive class coverage counts.
- Private manifest materialization, real importer implementation, and real importer execution remain unperformed.

## What Remains Separate Proof

This is a redacted read-only manifest-shape dry run only. It does not prove private asset content parsing, private corpus manifest materialization, private manifest row observation, real importer implementation, real importer execution, runtime resource archive parser behavior, runtime texture parser behavior, runtime texture pixels, JPEG/inflate decode fidelity, runtime mesh loading or skinning, Direct3D upload or GPU behavior, native textured 3D rendering, material visual correctness, material/shader parity, asset format completeness, exact mesh or texture layouts, product UI behavior, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
