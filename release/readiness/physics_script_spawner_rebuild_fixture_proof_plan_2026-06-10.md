# PhysicsScript Spawner Rebuild Fixture Proof Plan Readiness Note

Status: complete static spawner value-interface fixture, not runtime proof
Date: 2026-06-10
Scope: `physics-script-spawner-rebuild-fixture-proof-plan`

This readiness note records the public-safe fixture result for `PhysicsScript Spawner Rebuild Fixture Proof Plan`, backed by `physics-script-spawner-rebuild-fixture-proof-plan.v1.json`.

Readiness tokens:

- `spawnerFixtureStatus=physics-script-spawner-rebuild-fixture-proof-plan-complete-static-spawner-value-interface-fixture-not-runtime-proof`
- `fixtureStatus=physics-script-spawner-rebuild-fixture-proof-plan-complete-static-spawner-value-interface-fixture-not-runtime-proof`
- `previousSlice=PhysicsScript Explosion Rebuild Fixture Proof Plan`
- `selectedNextSlice=PhysicsScript Hazard Rebuild Fixture Proof Plan`
- `selectedNextScope=physics-script-hazard-rebuild-fixture-proof-plan`
- `selectedFixtureFamily=spawner`
- `selectedFixturePath=spawner-selected-value-id-interface-static-fixture`
- `selectedCandidateRank=2`
- `selectedSourceProofCount=5`
- `selectedValueInterfaceRowCount=14`
- `selectedValueIdCount=14`
- `selectedObservedValueIdCount=10`
- `selectedFactoryOnlyValueIdCount=4`
- `selectedUnselectedObservedValueIdCount=0`
- `selectedTopLevelRecordCount=38`
- `selectedValueNodeCount=244`
- `selectedRawValuePayloadBytesPreserved=1441`
- `selectedDeclaredPayloadBytes=5279`
- `selectedOwnedStringFieldCount=2`
- `selectedScalarFieldCount=11`
- `selectedFlagConstantTrueFieldCount=1`
- `selectedFixtureRowCount=14`
- `selectedObservedFixtureRowCount=10`
- `selectedFactoryOnlyFixtureRowCount=4`
- `selectedPayloadShapeCaseCount=11`
- `selectedObservedPayloadShapeClassCount=3`
- `selectedScalar4ShapePayloadCount=206`
- `selectedOwnedStringShapePayloadCount=34`
- `selectedThreeScalarShapePayloadCount=4`
- `selectedMixedPayloadShapeValueIdCount=1`
- `selectedMixedPayloadShapeValueIds=1`
- `selectedCrosswalkOwnedStringCorpusCount=38`
- `selectedCrosswalkScalarCorpusCount=206`
- `selectedCrosswalkFlagConstantTrueCorpusCount=0`
- `unitNameObservedOwnedStringShapeCount=34`
- `unitNameObservedThreeScalarShapeCount=4`
- `factoryOnlyValueIdCount=4`
- `factoryOnlyValueIds=4/5/10/13`
- `observedValueIds=1/2/3/6/7/8/9/11/12/14`
- `selectedValueIds=1/2/3/4/5/6/7/8/9/10/11/12/13/14`
- `ownedStringFields=unitName/basedOn`
- `scalarFields=delay/amount/seekDelay/minRange/maxRange/preSpawnDelay/postSpawnDelay/squadSize/squadDelay/infinite/conditions`
- `flagConstantTrueFields=recallEnabled`
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
- `falseGuardCount=41`
- `zeroCounterCount=27`
- `publicLeakCheck=PASS`
- `latestGhidraBackupClass=verified-static-backup-redacted`

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
- `runtimeSpawnerBehaviorProven=false`
- `runtimeSpawnerUnitSpawnProven=false`
- `runtimeSpawnerTimingProven=false`
- `runtimeSpawnerAiBehaviorProven=false`
- `runtimeSpawnerRangeBehaviorProven=false`
- `serializedPhysicsScriptCompletenessProven=false`
- `exactPhysicsScriptLayoutProven=false`
- `exactSpawnerRecordLayoutProven=false`
- `completeValueIdSemanticsProven=false`
- `all185PairsSemanticallyNamed=false`
- `rawStringIdentityProven=false`
- `rawNumericMeaningProven=false`
- `runtimeObservationRows=0`
- `runtimeCommandEffectRows=0`
- `physicsScriptRuntimeEvidenceRows=0`
- `runtimePhysicsScriptRows=0`
- `runtimeSpawnerRows=0`
- `runtimeSpawnerUnitSpawnRows=0`
- `runtimeSpawnerTimingRows=0`
- `runtimeSpawnerAiRows=0`
- `runtimeSpawnerRangeRows=0`

Selected static anchors:

| Anchor | Role |
| --- | --- |
| `CPhysicsScriptStatements__CreateStatementType6` | Spawner value factory. |
| `CSpawnerStatement__LoadFromMemBuffer` | Spawner statement loader. |
| `CPhysicsSpawnerValueList__LoadFromMemBuffer` | Spawner value-list loader. |
| `CSpawnerStatement__CreateSpawnerAndRecurse` | Spawner create/recurse bridge. |
| `CSpawnerData__CreateAndRegisterByName` | Static spawner registry creation anchor. |
| `CSpawnerBasedOn__ApplyToSpawnerByName` | Static `basedOn` copy/apply anchor. |
| `CSpawnerUnit__ApplyToSpawnerByName` | Static `unitName` apply anchor. |
| `DAT_008553f4` | Static spawner registry global. |

Fixture requirement rows: `family-fixture`, `loader-fixture`, `value-interface-fixture`, `factory-only-boundary-fixture`, `payload-shape-fixture`, `unit-name-fixture`, and `stop-fixture`.

The value id `1` `unitName` row records a public-safe mixed payload-shape boundary: `unitNameObservedOwnedStringShapeCount=34` and `unitNameObservedThreeScalarShapeCount=4`. Value ids `4`, `5`, `10`, and `13` remain `factoryOnlyValueIds=4/5/10/13`.

This readiness note proves only static selected spawner value-ID fixture materialization. It does not prove runtime PhysicsScript behavior, runtime spawner behavior, runtime spawned-unit identity, runtime spawn timing, runtime spawner AI behavior, runtime range behavior, serialized PhysicsScript completeness, exact layouts, complete value-ID semantics, raw string identity, raw numeric value meaning, Ghidra mutation, BEA patching behavior, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
