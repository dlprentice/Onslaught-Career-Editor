# Static-To-Proof Post-PhysicsScript Fixture Next Safe Slice Selection Refresh

Status: complete selection refresh, texture/mesh material sidecar contract extension selected
Date: 2026-06-10
Scope: `static-to-proof-post-physics-script-fixture-next-safe-slice-selection-refresh`

Proof plan name: Static-To-Proof Rebuild Transition Post-PhysicsScript Fixture Next Safe Slice Selection Refresh Proof Plan

This selection refresh follows the completed [PhysicsScript Fixture Family Completion Rollup Proof Plan](physics-script-fixture-family-completion-rollup-proof-plan.md), backed by [physics-script-fixture-family-completion-rollup-proof-plan.v1.json](physics-script-fixture-family-completion-rollup-proof-plan.v1.json). It does not reselect the completed explosion, spawner, hazard, feature, component, weapon, round, weapon-mode, `unit`, or rollup lanes.

The selected next child lane is **Texture / Mesh Material Sidecar Rebuild Contract Extension Proof Plan** with `selectedChildScope=texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan`.

Result schema: [static-to-proof-post-physics-script-fixture-next-safe-slice-selection-refresh.v1.json](static-to-proof-post-physics-script-fixture-next-safe-slice-selection-refresh.v1.json).

## Selection Result

- `selectionRefreshStatus=static-to-proof-post-physics-script-fixture-next-safe-slice-selection-refresh-complete-texture-mesh-material-sidecar-contract-extension-selected`
- `previousSlice=PhysicsScript Fixture Family Completion Rollup Proof Plan`
- `selectedChildLane=Texture / Mesh Material Sidecar Rebuild Contract Extension Proof Plan`
- `selectedChildScope=texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan`
- `consultCount=2`
- `candidateCount=4`
- `selectedCandidateRank=1`
- `selectedSourceProofCount=5`
- `completedPhysicsScriptFixtureFamilyCount=9`
- `remainingPhysicsScriptFixtureFamilyCount=0`
- `selectionFalseGuardCount=45`
- `selectionZeroCounterCount=35`
- `publicLeakCheck=PASS`
- `latestGhidraBackupClass=verified-static-backup-redacted`

## Static Context

- Static Ghidra function-quality closure remains `6411/6411 = 100.00%`.
- Static debt remains `0 / 0 / 0`.
- Expanded post-100 static surface remains `1560/1560 = 100.00%`.
- Active current-risk focused accounting remains `1179/1179 = 100.00%`.
- `remainingActiveFocusedWork=0`.

## Parent Rollup Anchors

The completed parent rollup records:

- `physicsScriptFixtureFamilyCompletionRollupStatus=physics-script-fixture-family-completion-rollup-proof-plan-complete-nine-family-static-fixture-rollup-not-runtime-proof`
- `expectedFixtureFamilyCount=9`
- `completedFixtureFamilyCount=9`
- `remainingFixtureFamilyCount=0`
- `fixturePlanDocCount=9`
- `fixturePlanSchemaCount=9`
- `fixtureProofPlanProbeCount=9`
- `sourceMirrorPairCount=18`
- `selectedValueInterfaceRowCount=87`
- `selectedObservedValueIdCount=72`
- `selectedFactoryOnlyValueIdCount=15`
- `selectedUnselectedObservedValueIdCount=113`
- `selectedTopLevelRecordCount=777`
- `selectedValueNodeCount=6803`
- `physicsScriptStatementValuePairCount=185`
- `physicsScriptRawValuePayloadBytesPreserved=73796`
- `selectedPayloadShapeCaseCount=85`
- `selectedScalar4ShapePayloadCount=1151`
- `selectedOwnedStringShapePayloadCount=1186`
- `selectedTwoScalarShapePayloadCount=13`
- `selectedThreeScalarShapePayloadCount=101`
- `selectedRawPreservedOtherShapePayloadCount=259`
- `factoryOnlyBoundaryFamilyCount=6`
- `unselectedObservedBoundaryFamilyCount=5`
- `mixedPayloadBoundaryFamilyCount=7`

## Selected Asset Anchors

The selected child is based on tracked public-safe texture/mesh/material-sidecar evidence:

- [Texture/Mesh Asset Bridge Proof Plan](../game-assets/texture-mesh-asset-bridge-proof-plan.md)
- [Texture/Mesh Asset Bridge Copied-Corpus Proof](../game-assets/texture-mesh-asset-bridge-copied-corpus-proof.md)
- [Texture/Mesh Material Sidecar Ledger Proof](../game-assets/texture-mesh-material-sidecar-ledger-proof.md)
- [Mesh / Resource / Render Static Contract](mesh-resource-render-static-contract.md)

Selected asset/material counts:

- `materialSidecarModelRowsWithRefs=352/352`
- `materialSidecarUniqueRefs=213`
- `materialSidecarFiles=213`
- `materialSidecarMissingRefs=0`
- `catalogMissingRefs=0`
- `ambiguousCatalogRefs=1`
- `embeddedDuplicateOutputBoundaryRows=32`
- Texture export lane `847/847`
- Loose mesh export lane `213/213`
- Embedded mesh export lane `139/139`
- Catalog rows `4050`

## Candidate Ranking

| Rank | Candidate | Decision | Reason |
| ---: | --- | --- | --- |
| 1 | Texture / Mesh Material Sidecar Rebuild Contract Extension Proof Plan | Selected | Static/corpus/material-sidecar evidence is already public-safe and has `352/352` mapped model rows, `213` unique refs, `213` sidecar files, `0` missing sidecar refs, and `0` catalog-missing refs. |
| 2 | World / Thing / Spawn Runtime-Proof Readiness Gate | Deferred | Useful planning lane, but closer to runtime object identity and spawn behavior than the selected static asset contract extension. |
| 3 | MissionScript Level100 Private-Frame Observation Revisit | Deferred | Requires an explicit private-frame review arm and is outside the current no-runtime/no-private-frame selection posture. |
| 4 | Godot Clean-Room Prototype Workspace Boundary Proof Plan | Deferred | Useful later, but premature before the selected texture/material static contract extension records the rebuild-facing asset vocabulary. |

## Boundaries

This refresh proves only next-slice selection after the completed PhysicsScript fixture family rollup. It does not prove runtime PhysicsScript behavior, runtime texture parser behavior, runtime texture pixels, JPEG/inflate decode fidelity, runtime mesh loading, runtime mesh skinning, animation behavior, collision behavior, Direct3D upload, GPU behavior, native textured 3D rendering, material visual correctness, material/shader parity, asset format completeness, exact mesh/texture layouts, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.

Boundary token: runtimeExecution=false; beLaunch=false; newLaunch=false; screenshotCapture=false; privateFrameReviewPerformed=false; rowObservation=false; sourceSelectionObserved=false; sourceSelectionProven=false; nativeInput=false; debuggerAttachment=false; godotWork=false; ghidraMutation=false; executablePatching=false; productUiWired=false; rebuildImplementation=false; runtimePhysicsScriptBehaviorProven=false; runtimePhysicsScriptOutcomesProven=false; serializedPhysicsScriptCompletenessProven=false; exactPhysicsScriptLayoutProven=false; completeValueIdSemanticsProven=false; all185PairsSemanticallyNamed=false; rawStringIdentityProven=false; rawNumericMeaningProven=false; runtimeTextureParserBehaviorProven=false; runtimeTexturePixelsProven=false; runtimeJpegInflateDecodeFidelityProven=false; runtimeMeshLoadingProven=false; runtimeMeshSkinningProven=false; runtimeAnimationBehaviorProven=false; runtimeCollisionBehaviorProven=false; runtimeDirect3DUploadProven=false; runtimeGpuBehaviorProven=false; nativeTextured3DRenderingProven=false; materialVisualCorrectnessProven=false; materialShaderParityProven=false; visualQaComplete=false; cleanRoomRendererImplemented=false; assetFormatCompletenessProven=false; exactMeshTextureLayoutsProven=false; runtimeObjectIdentityProven=false; runtimeWorldLoadingProven=false; rebuildParityProven=false; noNoticeableDifferenceParityProven=false; privateAssetPublication=false; publicPrivateProofLeak=false; runtimeObservationRows=0; physicsScriptRuntimeEvidenceRows=0; textureRuntimeEvidenceRows=0; meshRuntimeEvidenceRows=0; materialVisualReviewRows=0; screenshotRows=0; ghidraMutationRows=0; executablePatchRows=0; godotRows=0; rebuildImplementationRows=0; beProcessesAfterSelection=0.
