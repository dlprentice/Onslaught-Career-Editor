# PhysicsScript Hazard Rebuild Fixture Proof Plan

Status: complete static hazard value-interface fixture, not runtime proof
Last updated: 2026-06-10
Scope: `physics-script-hazard-rebuild-fixture-proof-plan`

This result materializes the `hazard` fixture selected after the completed [PhysicsScript Spawner Rebuild Fixture Proof Plan](physics-script-spawner-rebuild-fixture-proof-plan.md). It turns the selected hazard value-ID interface into public-safe fixture rows for rebuild planning without publishing copied strings, raw payload bytes, numeric values, private paths, runtime observations, hazard effect identity claims, or hazard noise identity claims.

Machine-checkable artifact:

- [physics-script-hazard-rebuild-fixture-proof-plan.v1.json](physics-script-hazard-rebuild-fixture-proof-plan.v1.json)

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
| `1` | `scalar14` | `scalar4` | observed | `scalar4_roundtrip=4` |
| `2` | `effect` | `owned_string_at_08` | observed | `owned_string_ascii_nul_shape_roundtrip=3`; `three_scalar4_roundtrip=1` |
| `3` | `scalar18` | `scalar4` | observed | `scalar4_roundtrip=4` |
| `4` | `noise` | `owned_string_at_08` | factory-only | no copied-corpus payload row in this fixture |

The value id `2` `effect` row is intentionally a mixed payload-shape boundary. The value-ID crosswalk names it as a string-facing `effect` field, while copied-corpus shape classification sees `3` owned-string-shaped rows and `1` payload-size-12 row classified by the scalar/string fixture as three-scalar roundtrip. This result preserves both shape classes and does not infer raw effect identity or numeric meaning.

Value id `4` is not hidden. It remains `factoryOnlyValueIds=4`: a selected static factory/apply row that is not copied-corpus-observed in the current aggregate.

## Static Anchors

| Anchor | Role |
| --- | --- |
| `CPhysicsScriptStatements__CreateStatementType9` | Hazard value factory. |
| `CHazardStatement__LoadFromMemBuffer` | Hazard statement loader. |
| `CPhysicsHazardValueList__LoadFromMemBuffer` | Hazard value-list loader. |
| `CHazardStatement__CreateHazardAndRecurse` | Hazard create/recurse bridge. |
| `CHazardStatement__CreateAndRegisterByName` | Static hazard registry creation anchor. |
| `CHazardEffect__ApplyToHazardByName` | Static `effect` apply anchor. |
| `CHazardNoise__ApplyToHazardByName` | Static `noise` apply anchor. |
| `DAT_00855408` | Static hazard registry global. |

## Requirement Rows

| Row | Status | Evidence | Boundary |
| --- | --- | --- | --- |
| `family-fixture` | `satisfied-static-with-factory-only-boundary` | `3` observed selected ids, `4` selected rows, `1` factory-only selected row, and zero unselected observed ids. | Static family-selection proof only. |
| `loader-fixture` | `satisfied-static` | `CPhysicsScriptStatements__CreateStatementType9`, `CHazardStatement__LoadFromMemBuffer`, `CPhysicsHazardValueList__LoadFromMemBuffer`, `CHazardStatement__CreateHazardAndRecurse`, and `DAT_00855408`. | Static loader/factory/registry bridge only. |
| `value-interface-fixture` | `satisfied-static` | Selected value ids `1,2,3,4` and all `4` rebuild-facing field names. | Selected value-ID interface only, not complete value semantics. |
| `factory-only-boundary-fixture` | `satisfied-explicit-boundary` | Value id `4` is a factory-only selected row in this copied-corpus aggregate. | Static factory/apply evidence only; no copied-corpus payload values are invented. |
| `payload-shape-fixture` | `satisfied-public-safe` | Two scalar4 observed rows, one string-facing observed row, one explicit mixed payload-shape boundary for `effect`, and one factory-only selected row. | Public-safe payload shape only; no raw strings or numeric meanings. |
| `effect-fixture` | `satisfied-static` | `effect` value id `2` is anchored to `CHazardEffect__ApplyToHazardByName` and `DAT_00855408`. | Static effect field boundary only, not runtime hazard effect dispatch. |
| `stop-fixture` | `enforced` | Runtime, Godot, Ghidra, patch, product, rebuild, raw-value, and private-path guards remain false with zero runtime rows. | Defer instead of broadening. |

## What This Proves

- The selected hazard value-ID interface is materialized as public-safe static fixture rows.
- Observed selected hazard value ids carry static factory/apply/registry anchors and copied-corpus payload-shape counts.
- Public-safe payload shape counts are preserved, including the value id `2` mixed-shape boundary.
- Factory-only selected row `4` remains explicit boundary debt.

## Not Claimed

This is not runtime PhysicsScript behavior, runtime hazard behavior, runtime hazard effect dispatch, runtime hazard noise dispatch, serialized PhysicsScript completeness, exact PhysicsScript layout, exact hazard record layout, complete value-ID semantics, raw string identity, raw numeric value meaning, runtime effect behavior, BEA patching behavior, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.

The static child lane selected by this hazard result was `PhysicsScript Feature Rebuild Fixture Proof Plan`.

Follow-up feature fixture result: [PhysicsScript Feature Rebuild Fixture Proof Plan](physics-script-feature-rebuild-fixture-proof-plan.md), backed by [physics-script-feature-rebuild-fixture-proof-plan.v1.json](physics-script-feature-rebuild-fixture-proof-plan.v1.json), records fixtureStatus=physics-script-feature-rebuild-fixture-proof-plan-complete-static-feature-value-interface-fixture-not-runtime-proof. The child lane materialized selectedNextSlice=PhysicsScript Component Rebuild Fixture Proof Plan while preserving selectedFixtureFamily=feature, selectedFixturePath=feature-selected-value-id-interface-static-fixture, selectedValueInterfaceRowCount=7, selectedObservedValueIdCount=5, selectedFactoryOnlyValueIdCount=2, selectedUnselectedObservedValueIdCount=0, selectedPayloadShapeCaseCount=6, selectedMixedPayloadShapeValueIds=2, factoryOnlyValueIds=5/7, runtimeExecution=false, godotWork=false, ghidraMutation=false, and rebuildImplementation=false. Active next static child lane: PhysicsScript Component Rebuild Fixture Proof Plan.
