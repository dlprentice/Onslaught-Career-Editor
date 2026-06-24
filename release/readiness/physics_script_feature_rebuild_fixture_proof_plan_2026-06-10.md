# PhysicsScript Feature Rebuild Fixture Proof Plan Readiness Note

Status: complete static feature value-interface fixture, not runtime proof
Date: 2026-06-10
Scope: `physics-script-feature-rebuild-fixture-proof-plan`

This readiness note records the public-safe completion of the Feature child fixture after the Hazard fixture.

Artifacts:

- Proof: `reverse-engineering/binary-analysis/physics-script-feature-rebuild-fixture-proof-plan.md`
- Schema: `reverse-engineering/binary-analysis/physics-script-feature-rebuild-fixture-proof-plan.v1.json`
- Generator: `tools/physics_script_feature_rebuild_fixture_proof_plan.py`
- Probe: `tools/physics_script_feature_rebuild_fixture_proof_plan_probe.py`

Readiness tokens:

- `featureFixtureStatus=physics-script-feature-rebuild-fixture-proof-plan-complete-static-feature-value-interface-fixture-not-runtime-proof`
- `fixtureStatus=physics-script-feature-rebuild-fixture-proof-plan-complete-static-feature-value-interface-fixture-not-runtime-proof`
- `previousSlice=PhysicsScript Hazard Rebuild Fixture Proof Plan`
- `selectedNextSlice=PhysicsScript Component Rebuild Fixture Proof Plan`
- `selectedNextScope=physics-script-component-rebuild-fixture-proof-plan`
- `selectedFixtureFamily=feature`
- `selectedFixturePath=feature-selected-value-id-interface-static-fixture`
- `selectedCandidateRank=4`
- `selectedSourceProofCount=5`
- `selectedValueInterfaceRowCount=7`
- `selectedValueIdCount=7`
- `selectedValueIds=1/2/3/4/5/6/7`
- `observedValueIds=1/2/3/4/6`
- `selectedObservedValueIdCount=5`
- `selectedFactoryOnlyValueIdCount=2`
- `selectedUnselectedObservedValueIdCount=0`
- `selectedTopLevelRecordCount=43`
- `selectedValueNodeCount=113`
- `selectedRawValuePayloadBytesPreserved=1375`
- `selectedDeclaredPayloadBytes=3319`
- `selectedOwnedStringFieldCount=3`
- `selectedScalarFieldCount=2`
- `selectedFlagConstantTrueFieldCount=0`
- `selectedFlagFromScalarNonzeroFieldCount=2`
- `selectedFixtureRowCount=7`
- `selectedObservedFixtureRowCount=5`
- `selectedFactoryOnlyFixtureRowCount=2`
- `selectedPayloadShapeCaseCount=6`
- `selectedObservedPayloadShapeClassCount=3`
- `selectedScalar4ShapePayloadCount=45`
- `selectedOwnedStringShapePayloadCount=66`
- `selectedThreeScalarShapePayloadCount=2`
- `selectedMixedPayloadShapeValueIdCount=1`
- `selectedMixedPayloadShapeValueIds=2`
- `selectedCrosswalkOwnedStringCorpusCount=68`
- `selectedCrosswalkScalarCorpusCount=25`
- `selectedCrosswalkFlagConstantTrueCorpusCount=0`
- `selectedCrosswalkFlagFromScalarNonzeroCorpusCount=20`
- `meshObservedOwnedStringShapeCount=40`
- `meshObservedThreeScalarShapeCount=2`
- `factoryOnlyValueIdCount=2`
- `factoryOnlyValueIds=5/7`
- `ownedStringFields=mesh/texture/noise`
- `scalarFields=scalar18/scalar1C`
- `flagConstantTrueFields=`
- `flagFromScalarNonzeroFields=flag10/flag14`
- `sourceProofCount=6`
- `sourceSchemaCount=5`
- `sourceMirrorPairCount=9`
- `topLevelFamilyCount=9`
- `valueInterfaceRowCount=87`
- `observedSelectedRowCount=72`
- `factoryOnlySelectedRowCount=15`
- `unselectedObservedRowCount=113`
- `physicsScriptCorpusByteCount=175603`
- `physicsScriptStreamHeader=0x12`
- `physicsScriptTopLevelStatementCount=777`
- `physicsScriptValueListNodeCount=6803`
- `physicsScriptStatementValuePairCount=185`
- `physicsScriptRawValuePayloadBytesPreserved=73796`
- `falseGuardCount=44`
- `zeroCounterCount=29`
- `publicLeakCheck=PASS`
- `latestGhidraBackupClass=verified-static-backup-redacted`

Static anchors:

- `CPhysicsScriptStatements__CreateStatementType8`
- `CFeatureStatement__LoadFromMemBuffer`
- `CPhysicsFeatureValueList__LoadFromMemBuffer`
- `CFeatureStatement__CreateFeatureAndRecurse`
- `CFeatureMesh__ApplyToFeatureByName`
- `CFeatureTexture__ApplyToFeatureByName`
- `CFeatureNoise__ApplyToFeatureByName`
- `CFeatureFlag10__ApplyToFeatureByName`
- `CFeatureFlag14__ApplyToFeatureByName`
- `DAT_00855404`

Boundary tokens:

- `runtimeExecution=false`
- `beLaunch=false`
- `newLaunch=false`
- `screenshotCapture=false`
- `privateFrameReviewPerformed=false`
- `rowObservation=false`
- `sourceSelectionObserved=false`
- `sourceSelectionProven=false`
- `nativeInput=false`
- `debuggerAttachment=false`
- `godotWork=false`
- `ghidraMutation=false`
- `executablePatching=false`
- `productUiWired=false`
- `rebuildImplementation=false`
- `runtimePhysicsScriptBehaviorProven=false`
- `runtimeFeatureBehaviorProven=false`
- `runtimeFeatureMeshProven=false`
- `runtimeFeatureTextureProven=false`
- `runtimeFeatureNoiseProven=false`
- `runtimeFeatureFlagBehaviorProven=false`
- `serializedPhysicsScriptCompletenessProven=false`
- `exactPhysicsScriptLayoutProven=false`
- `completeValueIdSemanticsProven=false`
- `rawStringIdentityProven=false`
- `rawNumericMeaningProven=false`
- `runtimeObservationRows=0`
- `physicsScriptRuntimeEvidenceRows=0`
- `runtimePhysicsScriptRows=0`
- `runtimeFeatureRows=0`
- `runtimeFeatureMeshRows=0`
- `runtimeFeatureTextureRows=0`
- `runtimeFeatureNoiseRows=0`
- `runtimeFeatureFlagRows=0`

Requirement-row tokens:

- `factory-only-boundary-fixture`
- `mesh-texture-noise-fixture`
- `stop-fixture`

What this proves:

- The selected `feature` value-ID interface has been materialized as public-safe static fixture rows.
- The public-safe schema records seven selected rows, five copied-corpus-observed selected IDs, two factory-only selected IDs, and zero unselected observed IDs.
- The mixed-shape `mesh` row and factory-only `noise` / `scalar1C` rows are explicit boundaries.

What remains unproven:

- Runtime PhysicsScript behavior.
- Runtime feature mesh, texture, noise, terrain/material, or flag behavior.
- Serialized PhysicsScript completeness.
- Exact PhysicsScript or feature record layout.
- Raw string identity or raw numeric meaning.
- Ghidra mutation, executable patching, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
