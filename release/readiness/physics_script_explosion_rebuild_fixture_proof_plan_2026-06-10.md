# PhysicsScript Explosion Rebuild Fixture Proof Plan Readiness Note

Status: complete static explosion value-interface fixture, not runtime proof
Date: 2026-06-10
Scope: `physics-script-explosion-rebuild-fixture-proof-plan`

This readiness note records the public-safe fixture result for `PhysicsScript Explosion Rebuild Fixture Proof Plan`, backed by `physics-script-explosion-rebuild-fixture-proof-plan.v1.json`.

Readiness tokens:

- `explosionFixtureStatus=physics-script-explosion-rebuild-fixture-proof-plan-complete-static-explosion-value-interface-fixture-not-runtime-proof`
- `fixtureStatus=physics-script-explosion-rebuild-fixture-proof-plan-complete-static-explosion-value-interface-fixture-not-runtime-proof`
- `previousSlice=PhysicsScript Rebuild Fixture Selection Proof Plan`
- `selectedNextSlice=PhysicsScript Spawner Rebuild Fixture Proof Plan`
- `selectedNextScope=physics-script-spawner-rebuild-fixture-proof-plan`
- `selectedFixtureFamily=explosion`
- `selectedFixturePath=explosion-selected-value-id-interface-static-fixture`
- `selectedCandidateRank=1`
- `selectedSourceProofCount=4`
- `selectedValueInterfaceRowCount=14`
- `selectedValueIdCount=14`
- `selectedObservedValueIdCount=14`
- `selectedFactoryOnlyValueIdCount=0`
- `selectedUnselectedObservedValueIdCount=0`
- `selectedTopLevelRecordCount=118`
- `selectedValueNodeCount=869`
- `selectedRawValuePayloadBytesPreserved=14616`
- `selectedDeclaredPayloadBytes=27335`
- `selectedOwnedStringFieldCount=7`
- `selectedScalarFieldCount=7`
- `selectedFixtureRowCount=14`
- `selectedPayloadShapeCaseCount=15`
- `selectedObservedPayloadShapeClassCount=3`
- `selectedScalar4ShapePayloadCount=330`
- `selectedOwnedStringShapePayloadCount=532`
- `selectedThreeScalarShapePayloadCount=7`
- `selectedMixedPayloadShapeValueIdCount=1`
- `selectedMixedPayloadShapeValueIds=10`
- `selectedCrosswalkOwnedStringCorpusCount=539`
- `selectedCrosswalkScalarCorpusCount=330`
- `soundObservedOwnedStringShapeCount=79`
- `soundObservedThreeScalarShapeCount=7`
- `deferredFactoryValueIdCount=1`
- `deferredFactoryValueIds=14`
- `selectedValueIds=1/2/3/4/5/6/7/8/9/10/11/12/13/15`
- `ownedStringFields=basedOn/airEffect/groundEffect/waterEffect/unitEffect/sound/waterSound`
- `scalarFields=scalar34/scalar38/scalar3C/scalar40/scalar44/scalar4C/scalar48`
- `sourceProofCount=5`
- `sourceSchemaCount=4`
- `sourceMirrorPairCount=10`
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
- `zeroCounterCount=26`
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
- `runtimeExplosionBehaviorProven=false`
- `runtimeExplosionDamageProven=false`
- `runtimeExplosionVisualEffectProven=false`
- `runtimeExplosionAudioProven=false`
- `serializedPhysicsScriptCompletenessProven=false`
- `exactPhysicsScriptLayoutProven=false`
- `exactExplosionRecordLayoutProven=false`
- `completeValueIdSemanticsProven=false`
- `all185PairsSemanticallyNamed=false`
- `rawStringIdentityProven=false`
- `rawNumericMeaningProven=false`
- `runtimeObservationRows=0`
- `runtimeCommandEffectRows=0`
- `physicsScriptRuntimeEvidenceRows=0`
- `runtimePhysicsScriptRows=0`
- `runtimeExplosionRows=0`
- `runtimeExplosionDamageRows=0`
- `runtimeExplosionVisualRows=0`
- `runtimeExplosionAudioRows=0`

Selected static anchors:

| Anchor | Role |
| --- | --- |
| `CPhysicsScriptStatements__CreateStatementType7` | Explosion value factory. |
| `CExplosionStatement__LoadFromMemBuffer` | Explosion statement loader. |
| `CPhysicsExplosionValueList__LoadFromMemBuffer` | Explosion value-list loader. |
| `CExplosionStatement__CreateExplosionAndRecurse` | Explosion create/recurse bridge. |
| `CExplosionBasedOn__ApplyToExplosionByName` | Static `basedOn` copy/apply anchor. |
| `CExplosionValue__ApplyToExplosionByName` | Static apply anchor for selected effect, sound, and scalar rows. |
| `DAT_008553f8` | Static explosion registry global. |

Fixture requirement rows: `family-fixture`, `loader-fixture`, `value-interface-fixture`, `payload-shape-fixture`, `based-on-fixture`, and `stop-fixture`.

The value id `10` `sound` row records a public-safe mixed payload-shape boundary: `soundObservedOwnedStringShapeCount=79` and `soundObservedThreeScalarShapeCount=7`. Value id `14` remains `deferredFactoryValueIds=14`.

This readiness note proves only static selected explosion value-ID fixture materialization. It does not prove runtime PhysicsScript behavior, runtime explosion behavior, runtime explosion damage, runtime explosion visual effects, runtime explosion audio, serialized PhysicsScript completeness, exact layouts, complete value-ID semantics, raw string identity, raw numeric value meaning, Ghidra mutation, BEA patching behavior, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
