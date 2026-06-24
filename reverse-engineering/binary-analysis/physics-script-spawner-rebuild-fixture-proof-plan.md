# PhysicsScript Spawner Rebuild Fixture Proof Plan

Status: complete static spawner value-interface fixture, not runtime proof
Last updated: 2026-06-10
Scope: `physics-script-spawner-rebuild-fixture-proof-plan`

This result materializes the `spawner` fixture selected after the completed [PhysicsScript Explosion Rebuild Fixture Proof Plan](physics-script-explosion-rebuild-fixture-proof-plan.md). It turns the selected spawner value-ID interface into public-safe fixture rows for rebuild planning without publishing copied strings, raw payload bytes, numeric values, private paths, runtime observations, or spawned-unit identity claims.

Machine-checkable artifact:

- [physics-script-spawner-rebuild-fixture-proof-plan.v1.json](physics-script-spawner-rebuild-fixture-proof-plan.v1.json)

Fixture tokens:

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

This fixture proof does not change `static-reaudit-progress.json`, `static-reaudit-current-risk-ledger.json`, the Ghidra database, or the installed game. It performs no runtime launch, no Ghidra mutation, no executable patching, no Godot work, and no rebuild implementation.

## Static Closeout Context

| Track | Current |
| --- | --- |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Active current-risk focused accounting | `1179/1179 = 100.00%` |
| Remaining active focused work | `0` |
| Latest verified Ghidra backup | `latestGhidraBackupClass=verified-static-backup-redacted` |

## Fixture Surface

| Value ID | Field | Crosswalk class | Corpus status | Public-safe copied-corpus shape evidence |
| ---: | --- | --- | --- | --- |
| `1` | `unitName` | `owned_string_at_08` | observed | `owned_string_ascii_nul_shape_roundtrip=34`; `three_scalar4_roundtrip=4` |
| `2` | `delay` | `scalar4` | observed | `scalar4_roundtrip=38` |
| `3` | `amount` | `scalar4` | observed | `scalar4_roundtrip=38` |
| `4` | `seekDelay` | `scalar4` | factory-only | no copied-corpus payload row in this fixture |
| `5` | `recallEnabled` | `flag_constant_true` | factory-only | no copied-corpus payload row in this fixture |
| `6` | `minRange` | `scalar4` | observed | `scalar4_roundtrip=2` |
| `7` | `maxRange` | `scalar4` | observed | `scalar4_roundtrip=38` |
| `8` | `preSpawnDelay` | `scalar4` | observed | `scalar4_roundtrip=5` |
| `9` | `postSpawnDelay` | `scalar4` | observed | `scalar4_roundtrip=5` |
| `10` | `basedOn` | `owned_string_at_08` | factory-only | no copied-corpus payload row in this fixture |
| `11` | `squadSize` | `scalar4` | observed | `scalar4_roundtrip=37` |
| `12` | `squadDelay` | `scalar4` | observed | `scalar4_roundtrip=34` |
| `13` | `infinite` | `scalar4` | factory-only | no copied-corpus payload row in this fixture |
| `14` | `conditions` | `scalar4` | observed | `scalar4_roundtrip=9` |

The value id `1` `unitName` row is intentionally a mixed payload-shape boundary. The value-ID crosswalk names it as a string-facing `unitName` field, while copied-corpus shape classification sees `34` owned-string-shaped rows and `4` payload-size-12 rows classified by the scalar/string fixture as three-scalar roundtrip. This result preserves both shape classes and does not infer raw unit-name identity or numeric meaning.

Value ids `4`, `5`, `10`, and `13` are not hidden. They remain `factoryOnlyValueIds=4/5/10/13`: selected static factory/apply rows that are not copied-corpus-observed in the current aggregate.

## Static Anchors

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

## Requirement Rows

| Row | Status | Evidence | Boundary |
| --- | --- | --- | --- |
| `family-fixture` | `satisfied-static-with-factory-only-boundary` | `10` observed selected ids, `14` selected rows, `4` factory-only selected rows, and zero unselected observed ids. | Static family-selection proof only. |
| `loader-fixture` | `satisfied-static` | `CPhysicsScriptStatements__CreateStatementType6`, `CSpawnerStatement__LoadFromMemBuffer`, `CPhysicsSpawnerValueList__LoadFromMemBuffer`, `CSpawnerStatement__CreateSpawnerAndRecurse`, and `DAT_008553f4`. | Static loader/factory/registry bridge only. |
| `value-interface-fixture` | `satisfied-static` | Selected value ids `1,2,3,4,5,6,7,8,9,10,11,12,13,14` and all `14` rebuild-facing field names. | Selected value-ID interface only, not complete value semantics. |
| `factory-only-boundary-fixture` | `satisfied-explicit-boundary` | Value ids `4`, `5`, `10`, and `13` are factory-only selected rows in this copied-corpus aggregate. | Static factory/apply evidence only; no copied-corpus payload values are invented. |
| `payload-shape-fixture` | `satisfied-public-safe` | Nine scalar4 observed rows, one string-facing observed row, one explicit mixed payload-shape boundary for `unitName`, and four factory-only selected rows. | Public-safe payload shape only; no raw strings or numeric meanings. |
| `unit-name-fixture` | `satisfied-static` | `unitName` value id `1` is anchored to `CSpawnerUnit__ApplyToSpawnerByName` and `DAT_008553f4`. | Static unit-name field boundary only, not runtime spawned-unit identity. |
| `stop-fixture` | `enforced` | Runtime, Godot, Ghidra, patch, product, rebuild, raw-value, and private-path guards remain false with zero runtime rows. | Defer instead of broadening. |

## What This Proves

- The selected spawner value-ID interface is materialized as public-safe static fixture rows.
- Observed selected spawner value ids carry static factory/apply/registry anchors and copied-corpus payload-shape counts.
- Public-safe payload shape counts are preserved, including the value id `1` mixed-shape boundary.
- Factory-only selected rows `4`, `5`, `10`, and `13` remain explicit boundary debt.

## Not Claimed

This is not runtime PhysicsScript behavior, runtime spawner behavior, runtime spawned-unit identity, runtime spawn timing, runtime spawner AI behavior, runtime range behavior, serialized PhysicsScript completeness, exact PhysicsScript layout, exact spawner record layout, complete value-ID semantics, raw string identity, raw numeric value meaning, runtime based-on inheritance, BEA patching behavior, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.

The static child lane selected by this spawner result was `PhysicsScript Hazard Rebuild Fixture Proof Plan`.

Follow-up hazard fixture result: [PhysicsScript Hazard Rebuild Fixture Proof Plan](physics-script-hazard-rebuild-fixture-proof-plan.md), backed by [physics-script-hazard-rebuild-fixture-proof-plan.v1.json](physics-script-hazard-rebuild-fixture-proof-plan.v1.json), records fixtureStatus=physics-script-hazard-rebuild-fixture-proof-plan-complete-static-hazard-value-interface-fixture-not-runtime-proof. The child lane materialized selectedNextSlice=PhysicsScript Feature Rebuild Fixture Proof Plan while preserving selectedFixtureFamily=hazard, selectedFixturePath=hazard-selected-value-id-interface-static-fixture, selectedValueInterfaceRowCount=4, selectedObservedValueIdCount=3, selectedFactoryOnlyValueIdCount=1, selectedUnselectedObservedValueIdCount=0, selectedPayloadShapeCaseCount=4, selectedMixedPayloadShapeValueIds=2, factoryOnlyValueIds=4, runtimeExecution=false, godotWork=false, ghidraMutation=false, and rebuildImplementation=false. Follow-up feature fixture result: [PhysicsScript Feature Rebuild Fixture Proof Plan](physics-script-feature-rebuild-fixture-proof-plan.md), backed by [physics-script-feature-rebuild-fixture-proof-plan.v1.json](physics-script-feature-rebuild-fixture-proof-plan.v1.json), records fixtureStatus=physics-script-feature-rebuild-fixture-proof-plan-complete-static-feature-value-interface-fixture-not-runtime-proof and selectedNextSlice=PhysicsScript Component Rebuild Fixture Proof Plan. Active next static child lane: PhysicsScript Component Rebuild Fixture Proof Plan.
