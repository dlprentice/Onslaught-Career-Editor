# PhysicsScript Hazard Rebuild Fixture Proof Plan Readiness Note

Status: complete static hazard value-interface fixture, not runtime proof
Date: 2026-06-10
Scope: `physics-script-hazard-rebuild-fixture-proof-plan`

This readiness note covers the public-safe static fixture artifact for the PhysicsScript `hazard` family. It materializes the selected Hazard value-ID interface after the completed PhysicsScript Spawner Rebuild Fixture Proof Plan, while preserving runtime, raw-value, Ghidra, patching, Godot, product UI, and rebuild boundaries.

Tracked artifacts:

- `reverse-engineering/binary-analysis/physics-script-hazard-rebuild-fixture-proof-plan.md`
- `reverse-engineering/binary-analysis/physics-script-hazard-rebuild-fixture-proof-plan.v1.json`
- `tools/physics_script_hazard_rebuild_fixture_proof_plan.py`
- `tools/physics_script_hazard_rebuild_fixture_proof_plan_probe.py`

Fixture tokens:

- `hazardFixtureStatus=physics-script-hazard-rebuild-fixture-proof-plan-complete-static-hazard-value-interface-fixture-not-runtime-proof`
- `fixtureStatus=physics-script-hazard-rebuild-fixture-proof-plan-complete-static-hazard-value-interface-fixture-not-runtime-proof`
- `previousSlice=PhysicsScript Spawner Rebuild Fixture Proof Plan`
- `selectedNextSlice=PhysicsScript Feature Rebuild Fixture Proof Plan`
- `selectedNextScope=physics-script-feature-rebuild-fixture-proof-plan`
- `selectedFixtureFamily=hazard`
- `selectedFixturePath=hazard-selected-value-id-interface-static-fixture`
- `selectedCandidateRank=3`
- `selectedSourceProofCount=5`
- `selectedValueInterfaceRowCount=4`
- `selectedValueIdCount=4`
- `selectedObservedValueIdCount=3`
- `selectedFactoryOnlyValueIdCount=1`
- `selectedUnselectedObservedValueIdCount=0`
- `selectedTopLevelRecordCount=4`
- `selectedValueNodeCount=12`
- `selectedRawValuePayloadBytesPreserved=83`
- `selectedDeclaredPayloadBytes=273`
- `selectedOwnedStringFieldCount=2`
- `selectedScalarFieldCount=2`
- `selectedFlagConstantTrueFieldCount=0`
- `selectedFixtureRowCount=4`
- `selectedObservedFixtureRowCount=3`
- `selectedFactoryOnlyFixtureRowCount=1`
- `selectedPayloadShapeCaseCount=4`
- `selectedObservedPayloadShapeClassCount=3`
- `selectedScalar4ShapePayloadCount=8`
- `selectedOwnedStringShapePayloadCount=3`
- `selectedThreeScalarShapePayloadCount=1`
- `selectedMixedPayloadShapeValueIdCount=1`
- `selectedMixedPayloadShapeValueIds=2`
- `selectedCrosswalkOwnedStringCorpusCount=4`
- `selectedCrosswalkScalarCorpusCount=8`
- `selectedCrosswalkFlagConstantTrueCorpusCount=0`
- `effectObservedOwnedStringShapeCount=3`
- `effectObservedThreeScalarShapeCount=1`
- `factoryOnlyValueIdCount=1`
- `factoryOnlyValueIds=4`
- `observedValueIds=1/2/3`
- `selectedValueIds=1/2/3/4`
- `ownedStringFields=effect/noise`
- `scalarFields=scalar14/scalar18`
- `flagConstantTrueFields=`
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
- `falseGuardCount=40`
- `zeroCounterCount=25`
- `publicLeakCheck=PASS`
- `latestGhidraBackupClass=verified-static-backup-redacted`

Static anchors:

- `CPhysicsScriptStatements__CreateStatementType9`
- `CHazardStatement__LoadFromMemBuffer`
- `CPhysicsHazardValueList__LoadFromMemBuffer`
- `CHazardStatement__CreateHazardAndRecurse`
- `CHazardStatement__CreateAndRegisterByName`
- `CHazardEffect__ApplyToHazardByName`
- `CHazardNoise__ApplyToHazardByName`
- `DAT_00855408`

Requirement rows:

- `family-fixture`: static Hazard family surface with `3` observed selected ids, `4` selected rows, `1` factory-only selected row, and zero unselected observed ids.
- `loader-fixture`: static loader/factory/registry bridge through the Hazard statement factory, loader, value-list loader, create/recurse bridge, and registry global.
- `value-interface-fixture`: selected value ids `1,2,3,4` and all `4` rebuild-facing field names.
- `factory-only-boundary-fixture`: value id `4` remains factory-only selected boundary debt.
- `payload-shape-fixture`: two scalar4 observed rows, one string-facing observed row, one mixed `effect` row, and one factory-only row.
- `effect-fixture`: static `effect` apply anchor through `CHazardEffect__ApplyToHazardByName`.
- `stop-fixture`: runtime/Godot/Ghidra/patch/product/rebuild guards remain false with zero runtime rows.

Guard tokens:

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
- `runtimePhysicsScriptOutcomesProven=false`
- `runtimeHazardBehaviorProven=false`
- `runtimeHazardEffectProven=false`
- `runtimeHazardNoiseProven=false`
- `serializedPhysicsScriptCompletenessProven=false`
- `exactPhysicsScriptLayoutProven=false`
- `exactHazardRecordLayoutProven=false`
- `completeValueIdSemanticsProven=false`
- `all185PairsSemanticallyNamed=false`
- `rawStringIdentityProven=false`
- `rawNumericMeaningProven=false`
- `runtimeObservationRows=0`
- `physicsScriptRuntimeEvidenceRows=0`
- `runtimePhysicsScriptRows=0`
- `runtimeHazardRows=0`
- `runtimeHazardEffectRows=0`
- `runtimeHazardNoiseRows=0`

What this proves:

- The selected Hazard value-ID interface is materialized as public-safe static fixture rows.
- Observed selected Hazard value ids carry static factory/apply/registry anchors and copied-corpus payload-shape counts.
- The value id `2` `effect` mixed-shape boundary and value id `4` factory-only `noise` boundary are explicit.

What remains unproven:

- Runtime PhysicsScript behavior.
- Runtime hazard behavior, effect dispatch, or noise dispatch.
- Serialized PhysicsScript completeness.
- Exact PhysicsScript or hazard record layouts.
- Complete value-ID semantics, raw string identity, or raw numeric value meaning.
- Ghidra mutation, BEA patching behavior, Godot parity, product UI wiring, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
