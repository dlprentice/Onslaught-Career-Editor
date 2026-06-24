# PhysicsScript Component Rebuild Fixture Proof Plan Readiness Note

Status: complete static component value-interface fixture, not runtime proof
Date: 2026-06-10
Scope: `physics-script-component-rebuild-fixture-proof-plan`

This readiness note records the public-safe completion of the Component child fixture after the Feature fixture.

Artifacts:

- Proof: `reverse-engineering/binary-analysis/physics-script-component-rebuild-fixture-proof-plan.md`
- Schema: `reverse-engineering/binary-analysis/physics-script-component-rebuild-fixture-proof-plan.v1.json`
- Generator: `tools/physics_script_component_rebuild_fixture_proof_plan.py`
- Probe: `tools/physics_script_component_rebuild_fixture_proof_plan_probe.py`

Readiness tokens:

- `componentFixtureStatus=physics-script-component-rebuild-fixture-proof-plan-complete-static-component-value-interface-fixture-not-runtime-proof`
- `fixtureStatus=physics-script-component-rebuild-fixture-proof-plan-complete-static-component-value-interface-fixture-not-runtime-proof`
- `previousSlice=PhysicsScript Feature Rebuild Fixture Proof Plan`
- `selectedNextSlice=PhysicsScript Weapon Rebuild Fixture Proof Plan`
- `selectedNextScope=physics-script-weapon-rebuild-fixture-proof-plan`
- `selectedFixtureFamily=component`
- `selectedFixturePath=component-selected-value-id-interface-static-fixture`
- `selectedCandidateRank=5`
- `selectedSourceProofCount=5`
- `selectedValueInterfaceRowCount=20`
- `selectedValueIdCount=20`
- `selectedObservedValueIdCount=16`
- `selectedFactoryOnlyValueIdCount=4`
- `selectedUnselectedObservedValueIdCount=4`
- `selectedTopLevelRecordCount=39`
- `selectedValueNodeCount=225`
- `selectedRawValuePayloadBytesPreserved=2921`
- `selectedDeclaredPayloadBytes=6337`
- `selectedOwnedStringFieldCount=4`
- `selectedScalarFieldCount=7`
- `selectedFlagConstantTrueFieldCount=0`
- `selectedFlagFromScalarNonzeroFieldCount=8`
- `selectedIndexedScalarFieldCount=1`
- `selectedFixtureRowCount=20`
- `selectedObservedFixtureRowCount=16`
- `selectedFactoryOnlyFixtureRowCount=4`
- `selectedPayloadShapeCaseCount=16`
- `selectedObservedPayloadShapeClassCount=3`
- `selectedScalar4ShapePayloadCount=116`
- `selectedOwnedStringShapePayloadCount=41`
- `selectedTwoScalarShapePayloadCount=1`
- `selectedThreeScalarShapePayloadCount=0`
- `selectedMixedPayloadShapeValueIdCount=0`
- `selectedMixedPayloadShapeValueIds=`
- `selectedCrosswalkOwnedStringCorpusCount=41`
- `selectedCrosswalkScalarCorpusCount=94`
- `selectedCrosswalkFlagConstantTrueCorpusCount=0`
- `selectedCrosswalkFlagFromScalarNonzeroCorpusCount=22`
- `selectedCrosswalkIndexedScalarCorpusCount=1`
- `meshObservedOwnedStringShapeCount=39`
- `noiseObservedOwnedStringShapeCount=1`
- `ventObservedOwnedStringShapeCount=1`
- `indexedScalar164ObservedTwoScalarShapeCount=1`
- `factoryOnlyValueIdCount=4`
- `factoryOnlyValueIds=10/16/17/24`
- `observedValueIds=1/3/6/7/8/9/11/12/13/15/18/20/21/22/23/25`
- `unselectedObservedValueIds=2/4/14/19`
- `unselectedObservedValueIdCount=4`
- `unselectedObservedRawPreservedOtherPayloadCount=27`
- `unselectedObservedOwnedStringShapePayloadCount=40`
- `selectedValueIds=1/3/6/7/8/9/10/11/12/13/15/16/17/18/20/21/22/23/24/25`
- `ownedStringFields=mesh/basedOn/noise/vent`
- `scalarFields=scalarC0/scalar158/scalarDC/scalarD8/scalarB8/scalarBC/scalar160`
- `flagConstantTrueFields=`
- `flagFromScalarNonzeroFields=flag124/flag128/flag108/flag12C/flag198/flag114/flag19C/flag134`
- `indexedScalarFields=indexedScalar164`
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
- `falseGuardCount=46`
- `zeroCounterCount=31`
- `publicLeakCheck=PASS`
- `latestGhidraBackupClass=verified-static-backup-redacted`

Static anchors:

- `CPhysicsScriptStatements__CreateStatementType10`
- `CComponentStatement__LoadFromMemBuffer`
- `CPhysicsComponentValueList__LoadFromMemBuffer`
- `CComponentStatement__CreateComponentAndRecurse`
- `CComponentMesh__ApplyToComponentByName`
- `CComponentNoise__ApplyToComponentByName`
- `CComponentBasedOn__ApplyToComponentByName`
- `CComponentVent__ApplyToComponentByName`
- `CComponentIndexedScalar164__ApplyToComponentByName`
- `DAT_00855400`

Boundary tokens:

- `programFilesInputUsed=false`
- `installedGameMutation=false`
- `livePhysicsScriptRuntimeLoading=false`
- `runtimeExecution=false`
- `runtimeMissionScriptExecutionProven=false`
- `runtimeCommandEffectsProven=false`
- `runtimePhysicsScriptBehaviorProven=false`
- `runtimePhysicsScriptOutcomesProven=false`
- `runtimeComponentBehaviorProven=false`
- `runtimeComponentMeshProven=false`
- `runtimeComponentNoiseProven=false`
- `runtimeComponentVentProven=false`
- `runtimeComponentFlagBehaviorProven=false`
- `runtimeComponentIndexedScalarBehaviorProven=false`
- `serializedPhysicsScriptCompletenessProven=false`
- `exactPhysicsScriptLayoutProven=false`
- `exactComponentRecordLayoutProven=false`
- `completeValueIdSemanticsProven=false`
- `all185PairsSemanticallyNamed=false`
- `rawStringIdentityProven=false`
- `rawNumericMeaningProven=false`
- `rawCopiedStringsEmitted=false`
- `rawPayloadBytesPublished=false`
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
- `rebuildParityProven=false`
- `noNoticeableDifferenceParityProven=false`
- `exactSourceBodyIdentityProven=false`
- `exactRegistryContainerLayoutProven=false`
- `runtimeMeshDispatchProven=false`
- `runtimeNoiseDispatchProven=false`
- `runtimeVentDispatchProven=false`
- `runtimeComponentFlagDispatchProven=false`
- `runtimeComponentIndexedScalarDispatchProven=false`
- `runtimeObservationRows=0`
- `runtimeCommandEffectRows=0`
- `physicsScriptRuntimeEvidenceRows=0`
- `runtimePhysicsScriptRows=0`
- `runtimeComponentRows=0`
- `runtimeComponentMeshRows=0`
- `runtimeComponentNoiseRows=0`
- `runtimeComponentVentRows=0`
- `runtimeComponentFlagRows=0`
- `runtimeComponentIndexedScalarRows=0`
- `runtimeMeshRows=0`
- `runtimeNoiseRows=0`
- `runtimeVentRows=0`
- `runtimeComponentFlagDispatchRows=0`
- `runtimeComponentIndexedScalarDispatchRows=0`

Requirement-row tokens:

- `factory-only-boundary-fixture`
- `unselected-observed-boundary-fixture`
- `mesh-noise-vent-fixture`
- `indexed-scalar-fixture`
- `stop-fixture`

What this proves:

- The selected `component` value-ID interface has been materialized as public-safe static fixture rows.
- The public-safe schema records twenty selected rows, sixteen copied-corpus-observed selected IDs, four factory-only selected IDs, and four unselected observed IDs.
- The indexed-scalar row and factory-only / unselected-observed rows are explicit boundaries.

What remains unproven:

- Runtime PhysicsScript behavior.
- Runtime component mesh, noise, vent, flag, or indexed-scalar behavior.
- Serialized PhysicsScript completeness.
- Exact PhysicsScript or component record layout.
- Raw string identity or raw numeric meaning.
- Ghidra mutation, executable patching, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
