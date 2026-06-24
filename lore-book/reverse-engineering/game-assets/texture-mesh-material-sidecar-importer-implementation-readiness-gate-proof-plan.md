# Texture/Mesh Material Sidecar Importer Implementation Readiness Gate Proof Plan

Status: complete public-safe readiness gate, public contract skeleton ready, not real importer proof
Date: 2026-06-10
Scope: `texture-mesh-material-sidecar-importer-implementation-readiness-gate-proof-plan`

Canonical display name: Texture / Mesh Material Sidecar Importer Implementation Readiness Gate Proof Plan.

This slice follows the completed [Texture/Mesh Material Sidecar Importer Fixture Harness Consumer Dry-Run Proof Plan](texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan.md). It decides whether the texture/mesh material-sidecar lane is ready for real importer implementation or only a narrower public contract skeleton. The answer is deliberately narrow: the prior public dry-run evidence is strong enough to build a non-runtime public contract skeleton next, but not enough to implement or execute a real importer, read private assets, launch BEA, mutate Ghidra, do Godot work, wire product UI, build a renderer, or claim rebuild/no-noticeable-difference parity.

Result schema: [texture-mesh-material-sidecar-importer-implementation-readiness-gate-proof-plan.v1.json](texture-mesh-material-sidecar-importer-implementation-readiness-gate-proof-plan.v1.json).

## Result

- `implementationReadinessStatus=texture-mesh-material-sidecar-importer-implementation-readiness-gate-complete-public-contract-skeleton-ready-not-real-importer-proof`
- `previousSlice=Texture / Mesh Material Sidecar Importer Fixture Harness Consumer Dry-Run Proof Plan`
- `selectedNextSlice=Texture / Mesh Material Sidecar Importer Public Contract Skeleton Implementation Proof Plan`
- `selectedNextScope=texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-proof-plan`
- `sourceConsumerDryRunStatus=texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan-complete-public-safe-consumer-dry-run-not-importer-execution-proof`
- `sourceConsumedFixtureRowCount=8`
- `sourceConsumerDryRunStepCount=10`
- `sourceConsumerAssertionGroupCount=8`
- `sourceConsumerAssertionCheckCount=19`
- `sourceFailedConsumerAssertions=0`
- `sourceUnexpectedFixtureRows=0`
- `sourceConsumerOutputArtifactRows=0`
- `readinessGateCount=8`
- `readinessCheckCount=16`
- `failedReadinessGateCount=0`
- `blockedReadinessGateCount=0`
- `readinessValidationOnly=true`
- `readinessConsumesPublicDryRunOnly=true`
- `publicContractSkeletonReadyNow=true`
- `realImporterImplementationReadyNow=false`
- `realImporterExecutionReadyNow=false`
- `implementationDeferred=true`
- `explicitImporterImplementationArmPresent=false`
- `privateAssetReadAuthorizationPresent=false`
- `operatorPrivateOutputReviewAvailable=false`
- `selectedNextImplementationSliceCount=1`
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

Static context remains `6411/6411 = 100.00%`, `0 / 0 / 0`, `1560/1560 = 100.00%`, `1179/1179 = 100.00%`, and `remainingActiveFocusedWork=0`.

Probe anchors: `implementationReadinessGateComplete=true`; `publicContractSkeletonReadyNow=true`; `realImporterImplementationReadyNow=false`; `realImporterExecutionReadyNow=false`; `implementationDeferred=true`; `readinessGateCount=8`; `readinessCheckCount=16`; `failedReadinessGateCount=0`; `blockedReadinessGateCount=0`; `readinessValidationOnly=true`; `readinessConsumesPublicDryRunOnly=true`; `213 + 139 = 352`; `602 + 666 = 1268`; `213 + 28 = 241`; `212 + 1 = 213`; `139 - 107 = 32`; `beProcessesAfterReadinessGate=0`.

## Readiness Gates

| Gate ID | Result | Claim |
| --- | --- | --- |
| `source-consumer-dry-run-status` | `PASS` | Source consumer dry-run is complete and explicitly not importer execution proof. |
| `fixture-row-identity` | `PASS` | The next contract skeleton may consume exactly the eight public-safe row IDs. |
| `aggregate-arithmetic` | `PASS` | Row, reference, union, sidecar, and duplicate-output arithmetic are stable. |
| `public-edge-boundaries` | `PASS` | The stem-only and ambiguous catalog cases remain synthetic public IDs. |
| `private-data-refusal` | `PASS` | The next contract skeleton must refuse private paths, raw refs, raw stems, filenames, hashes, and raw artifacts. |
| `runtime-boundary` | `PASS` | Runtime launch, capture, debugger, Ghidra, Godot, renderer, UI, patch, and rebuild work remain out of scope. |
| `output-boundary` | `PASS` | The next slice may emit only a public validation summary, not imported assets or runtime outputs. |
| `next-slice-selection` | `PASS` | The next selected slice is a public contract skeleton implementation proof, not real importer execution proof. |

## Required Public Contract Interfaces

- `load-public-consumer-dry-run-schema`
- `enumerate-consumed-fixture-row-ids`
- `validate-aggregate-counts`
- `validate-public-edge-case-boundaries`
- `refuse-private-or-runtime-inputs`
- `emit-public-validation-summary`

## Consumed Fixture Rows

- `importer-source-matrix-prerequisite`
- `importer-loose-family-fixture`
- `importer-embedded-family-fixture`
- `importer-non-additive-union-fixture`
- `importer-sidecar-match-mode-fixture`
- `importer-catalog-linkage-fixture`
- `importer-duplicate-output-surplus-fixture`
- `importer-negative-claim-guard-fixture`

## Public Edge Cases

- `stem-only-sidecar-match-boundary-001`
- `ambiguous-catalog-ref-boundary-001`

Both edge cases keep `rawRefPublished=false`, `rawStemPublished=false`, `catalogVariantPublished=false`, `filenamePublished=false`, `pathPublished=false`, and `hashPublished=false`.

## Implementation Boundary

The selected next slice is `Texture / Mesh Material Sidecar Importer Public Contract Skeleton Implementation Proof Plan`. That future slice may create a public contract skeleton over the tracked sanitized schema, but it must not implement or execute a real importer. It must not read private assets, resolve raw texture refs, produce imported assets, launch BEA, mutate Ghidra, patch executables, use Godot, wire product UI, implement a renderer, or claim rebuild/no-noticeable-difference parity.

Boundary token: runtimeExecution=false; beLaunch=false; newLaunch=false; screenshotCapture=false; privateFrameReviewPerformed=false; rowObservation=false; sourceSelectionObserved=false; sourceSelectionProven=false; nativeInput=false; debuggerAttachment=false; godotWork=false; ghidraMutation=false; executablePatching=false; productUiWired=false; realImporterImplementation=false; realImporterExecuted=false; realImporterImplementationReadyNow=false; realImporterExecutionReadyNow=false; explicitImporterImplementationArmPresent=false; privateAssetReadAuthorizationPresent=false; operatorPrivateOutputReviewAvailable=false; importerImplementation=false; importerExecuted=false; fixtureHarnessRuntimeExecuted=false; fixtureHarnessConsumerRuntimeExecuted=false; rebuildImplementation=false; runtimeTextureParserBehaviorProven=false; runtimeTexturePixelsProven=false; runtimeJpegInflateDecodeFidelityProven=false; runtimeMeshLoadingProven=false; runtimeMeshSkinningProven=false; runtimeAnimationBehaviorProven=false; runtimeCollisionBehaviorProven=false; runtimeDirect3DUploadProven=false; runtimeGpuBehaviorProven=false; nativeTextured3DRenderingProven=false; materialVisualCorrectnessProven=false; materialShaderParityProven=false; visualQaComplete=false; cleanRoomRendererImplemented=false; assetFormatCompletenessProven=false; exactMeshTextureLayoutsProven=false; runtimeResourceArchiveParserProven=false; runtimeSidecarMaterialLoadProven=false; runtimeObjectIdentityProven=false; runtimeWorldLoadingProven=false; rebuildParityProven=false; noNoticeableDifferenceParityProven=false; privateAssetPublication=false; publicPrivateProofLeak=false; implementationReadinessFalseGuardCount=45; implementationReadinessZeroCounterCount=38; actualAssetImportRows=0; generatedAssetRows=0; outputArtifactRows=0; dryRunOutputArtifactRows=0; rawFixtureExampleRows=0; privateFixtureRows=0; runtimeTexturePixelRows=0; runtimeMeshRenderRows=0; runtimeMaterialRows=0; runtimeObservationRows=0; textureRuntimeEvidenceRows=0; meshRuntimeEvidenceRows=0; materialRuntimeEvidenceRows=0; materialVisualReviewRows=0; screenshotRows=0; privateFrameRowsObserved=0; rowObservationRows=0; sourceObservedRows=0; newLaunchRows=0; captureRows=0; ocrRows=0; rawDialogueRows=0; ghidraMutationRows=0; executablePatchRows=0; productUiRows=0; godotRows=0; realImporterImplementationRows=0; rebuildImplementationRows=0; runtimeCollisionRows=0; runtimeResourceArchiveParserRows=0; runtimeSidecarMaterialLoadRows=0; publicContractSkeletonImplementationRows=0; beProcessesAfterReadinessGate=0; publicCaseRawRefLeakCount=0; privatePathLeakCount=0; rawArtifactLeakCount=0; privateAssetLeakCount=0; publicPrivateProofLeakCount=0.

## What This Proves

- The importer implementation path has a public-safe readiness gate.
- The consumer dry-run proof stack is sufficient to build a non-runtime public contract skeleton next.
- The next selected slice is a public contract skeleton implementation proof only.
- Real importer implementation and execution remain deferred until a separate explicit authorization and private-safety packet exist.

## What Remains Separate Proof

This is readiness-gate proof only. It does not prove real importer implementation, real importer execution, private asset import, runtime resource archive parser behavior, runtime texture parser behavior, runtime texture pixels, JPEG/inflate decode fidelity, runtime mesh loading or skinning, Direct3D upload or GPU behavior, native textured 3D rendering, material visual correctness, material/shader parity, asset format completeness, exact mesh or texture layouts, product UI behavior, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
