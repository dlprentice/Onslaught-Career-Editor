# PhysicsScript Feature Rebuild Fixture Proof Plan

Status: complete static feature value-interface fixture, not runtime proof
Last updated: 2026-06-10
Scope: `physics-script-feature-rebuild-fixture-proof-plan`

This result materializes the `feature` fixture selected after the completed [PhysicsScript Hazard Rebuild Fixture Proof Plan](physics-script-hazard-rebuild-fixture-proof-plan.md). It turns the selected feature value-ID interface into public-safe fixture rows for rebuild planning without publishing copied strings, raw payload bytes, numeric values, private paths, runtime observations, terrain/material behavior claims, or rebuild parity claims.

Machine-checkable artifact:

- [physics-script-feature-rebuild-fixture-proof-plan.v1.json](physics-script-feature-rebuild-fixture-proof-plan.v1.json)

Fixture tokens:

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
- `observedValueIds=1/2/3/4/6`
- `selectedValueIds=1/2/3/4/5/6/7`
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
| `1` | `scalar18` | `scalar4` | observed | `scalar4_roundtrip=25` |
| `2` | `mesh` | `owned_string_at_08` | observed | `owned_string_ascii_nul_shape_roundtrip=40`; `three_scalar4_roundtrip=2` |
| `3` | `texture` | `owned_string_at_08` | observed | `owned_string_ascii_nul_shape_roundtrip=26` |
| `4` | `flag10` | `flag_from_scalar_nonzero` | observed | `scalar4_roundtrip=18` |
| `5` | `noise` | `owned_string_at_08` | factory-only | no copied-corpus payload row in this fixture |
| `6` | `flag14` | `flag_from_scalar_nonzero` | observed | `scalar4_roundtrip=2` |
| `7` | `scalar1C` | `scalar4` | factory-only | no copied-corpus payload row in this fixture |

The value id `2` `mesh` row is intentionally a mixed payload-shape boundary. The value-ID crosswalk names it as a string-facing `mesh` field, while copied-corpus shape classification sees `40` owned-string-shaped rows and `2` payload-size-12 rows classified by the scalar/string fixture as three-scalar roundtrip. This result preserves both shape classes and does not infer raw mesh identity or numeric meaning.

Value ids `5` and `7` are not hidden. They remain `factoryOnlyValueIds=5/7`: selected static factory/apply rows that are not copied-corpus-observed in the current aggregate.

## Static Anchors

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

## Requirement Rows

| Row | Status | Evidence | Boundary |
| --- | --- | --- | --- |
| `family-fixture` | `satisfied-static-with-factory-only-boundary` | `feature` has `5` observed selected ids, `7` selected rows, `2` factory-only selected rows, and zero unselected observed ids. | Static family-selection proof only. |
| `loader-fixture` | `satisfied-static` | Type8 factory, feature statement loader, feature value-list loader, feature create/recurse anchor, and registry global. | Static loader/factory/registry bridge only. |
| `value-interface-fixture` | `satisfied-static` | Selected value ids `1` through `7` and `7` rebuild-facing field names. | Selected value-ID interface only, not complete value semantics. |
| `factory-only-boundary-fixture` | `satisfied-explicit-boundary` | Value ids `5` and `7` are factory-only selected rows in this copied-corpus aggregate. | Static factory/apply evidence only; no copied-corpus payload values are invented. |
| `payload-shape-fixture` | `satisfied-public-safe` | Scalar4, owned-string, and flag-from-scalar value rows with one explicit mixed payload-shape boundary for `mesh`. | Public-safe payload shape only; no raw strings or numeric meanings. |
| `mesh-texture-noise-fixture` | `satisfied-static` | `mesh`, `texture`, and factory-only `noise` rows are anchored to feature apply helpers and `DAT_00855404`. | Static feature string-field boundary only, not runtime feature mesh/texture/noise dispatch. |
| `stop-fixture` | `enforced` | Runtime/Godot/Ghidra/patch/product/rebuild guards remain false with zero runtime rows. | Defer instead of broadening. |

## Claim Boundary

This proves only that the selected `feature` value-ID interface is materialized as public-safe static fixture rows, with static factory/apply/registry anchors and public-safe payload-shape counts.

This does not prove runtime PhysicsScript behavior, runtime feature behavior, runtime feature mesh dispatch, runtime feature texture dispatch, runtime feature noise dispatch, runtime feature flag behavior, serialized PhysicsScript completeness, exact PhysicsScript layouts, exact feature record layout, complete value-ID semantics, raw string identity, raw numeric value meaning, BEA patching behavior, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.

The next selected static child lane is `PhysicsScript Component Rebuild Fixture Proof Plan`.

Follow-up component fixture result: [PhysicsScript Component Rebuild Fixture Proof Plan](physics-script-component-rebuild-fixture-proof-plan.md), backed by [physics-script-component-rebuild-fixture-proof-plan.v1.json](physics-script-component-rebuild-fixture-proof-plan.v1.json), records fixtureStatus=physics-script-component-rebuild-fixture-proof-plan-complete-static-component-value-interface-fixture-not-runtime-proof and selectedNextSlice=PhysicsScript Weapon Rebuild Fixture Proof Plan. The child lane materialized selectedFixtureFamily=component, selectedFixturePath=component-selected-value-id-interface-static-fixture, selectedValueInterfaceRowCount=20, selectedObservedValueIdCount=16, selectedFactoryOnlyValueIdCount=4, selectedUnselectedObservedValueIdCount=4, selectedPayloadShapeCaseCount=16, factoryOnlyValueIds=10/16/17/24, unselectedObservedValueIds=2/4/14/19, runtimeExecution=false, godotWork=false, ghidraMutation=false, and rebuildImplementation=false. Active next static child lane: PhysicsScript Weapon Rebuild Fixture Proof Plan.
