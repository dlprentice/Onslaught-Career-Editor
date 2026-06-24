# PhysicsScript Component Rebuild Fixture Proof Plan

Status: complete static component value-interface fixture, not runtime proof
Last updated: 2026-06-10
Scope: `physics-script-component-rebuild-fixture-proof-plan`

This result materializes the `component` fixture after the completed [PhysicsScript Feature Rebuild Fixture Proof Plan](physics-script-feature-rebuild-fixture-proof-plan.md). It turns the selected component value-ID interface into public-safe fixture rows for rebuild planning without publishing copied strings, raw payload bytes, numeric values, private paths, runtime observations, component behavior claims, or rebuild parity claims.

Machine-checkable artifact:

- [physics-script-component-rebuild-fixture-proof-plan.v1.json](physics-script-component-rebuild-fixture-proof-plan.v1.json)

Follow-up weapon fixture result: [PhysicsScript Weapon Rebuild Fixture Proof Plan](physics-script-weapon-rebuild-fixture-proof-plan.md), backed by [physics-script-weapon-rebuild-fixture-proof-plan.v1.json](physics-script-weapon-rebuild-fixture-proof-plan.v1.json), records fixtureStatus=physics-script-weapon-rebuild-fixture-proof-plan-complete-static-weapon-value-interface-fixture-not-runtime-proof. The child lane materialized selectedNextSlice=PhysicsScript Round Rebuild Fixture Proof Plan and selectedNextScope=physics-script-round-rebuild-fixture-proof-plan while preserving selectedFixtureFamily=weapon, selectedFixturePath=weapon-selected-value-id-interface-static-fixture, selectedValueIds=1/4/5/14, unselectedObservedValueIds=2/3/6/7/8/9/10/11/12/13, selectedMixedPayloadShapeValueIds=1, runtimeExecution=false, godotWork=false, ghidraMutation=false, and rebuildImplementation=false. Static anchors include CWeaponStatement__LoadFromMemBuffer, CPhysicsWeaponValueList__LoadFromMemBuffer, CWeaponStatement__CreateWeaponAndRecurse, and DAT_008553e8. Active next static child lane: PhysicsScript Round Rebuild Fixture Proof Plan.

Fixture tokens:

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

Guard tokens:

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
| `1` | `scalarC0` | `scalar4` | observed | `scalar4_roundtrip=39` |
| `3` | `mesh` | `owned_string_at_08` | observed | `owned_string_ascii_nul_shape_roundtrip=39` |
| `6` | `scalar158` | `scalar4` | observed | `scalar4_roundtrip=25` |
| `7` | `scalarDC` | `scalar4` | observed | `scalar4_roundtrip=9` |
| `8` | `scalarD8` | `scalar4` | observed | `scalar4_roundtrip=6` |
| `9` | `scalarB8` | `scalar4` | observed | `scalar4_roundtrip=7` |
| `10` | `basedOn` | `owned_string_at_08` | factory-only | no copied-corpus payload row in this fixture |
| `11` | `scalarBC` | `scalar4` | observed | `scalar4_roundtrip=8` |
| `12` | `noise` | `owned_string_at_08` | observed | `owned_string_ascii_nul_shape_roundtrip=1` |
| `13` | `flag124` | `flag_from_scalar_nonzero` | observed | `scalar4_roundtrip=2` |
| `15` | `flag128` | `flag_from_scalar_nonzero` | observed | `scalar4_roundtrip=2` |
| `16` | `flag108` | `flag_from_scalar_nonzero` | factory-only | no copied-corpus payload row in this fixture |
| `17` | `scalar160` | `scalar4` | factory-only | no copied-corpus payload row in this fixture |
| `18` | `flag12C` | `flag_from_scalar_nonzero` | observed | `scalar4_roundtrip=2` |
| `20` | `indexedScalar164` | `indexed_scalar` | observed | `two_scalar4_roundtrip=1` |
| `21` | `flag198` | `flag_from_scalar_nonzero` | observed | `scalar4_roundtrip=2` |
| `22` | `flag114` | `flag_from_scalar_nonzero` | observed | `scalar4_roundtrip=10` |
| `23` | `flag19C` | `flag_from_scalar_nonzero` | observed | `scalar4_roundtrip=4` |
| `24` | `flag134` | `flag_from_scalar_nonzero` | factory-only | no copied-corpus payload row in this fixture |
| `25` | `vent` | `owned_string_at_08` | observed | `owned_string_ascii_nul_shape_roundtrip=1` |

Value ids `10`, `16`, `17`, and `24` are not hidden. They remain `factoryOnlyValueIds=10/16/17/24`: selected static factory/apply rows that are not copied-corpus-observed in the current aggregate.

Value ids `2`, `4`, `14`, and `19` are also not hidden. They remain `unselectedObservedValueIds=2/4/14/19`: copied-corpus-observed component rows outside the selected rebuild-facing crosswalk, with `unselectedObservedRawPreservedOtherPayloadCount=27` and `unselectedObservedOwnedStringShapePayloadCount=40` preserved as boundary evidence.

## Static Anchors

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

## Requirement Rows

| Row | Status | Evidence | Boundary |
| --- | --- | --- | --- |
| `family-fixture` | `satisfied-static-with-factory-only-boundary` | component has 16 observed selected ids, 20 selected rows, 4 factory-only selected rows, and 4 unselected observed ids | Static family-selection proof only. |
| `loader-fixture` | `satisfied-static` | CPhysicsScriptStatements__CreateStatementType10, CComponentStatement__LoadFromMemBuffer, CPhysicsComponentValueList__LoadFromMemBuffer, CComponentStatement__CreateComponentAndRecurse, and DAT_00855400 | Static loader/factory/registry bridge only. |
| `value-interface-fixture` | `satisfied-static` | selected value ids 1,3,6,7,8,9,10,11,12,13,15,16,17,18,20,21,22,23,24,25 and 20 rebuild-facing field names | Selected value-id interface only, not complete value semantics. |
| `factory-only-boundary-fixture` | `satisfied-explicit-boundary` | value ids 10, 16, 17, and 24 are factory-only selected rows in this copied-corpus aggregate | Static factory/apply evidence only; no copied-corpus payload values are invented. |
| `unselected-observed-boundary-fixture` | `satisfied-explicit-boundary` | value ids 2, 4, 14, and 19 are copied-corpus-observed but intentionally unselected by the current rebuild-facing crosswalk | Observed raw component payload shapes are preserved as deferred boundary rows instead of receiving invented semantics. |
| `payload-shape-fixture` | `satisfied-public-safe` | scalar4, owned-string, flag-from-scalar, and indexed two-scalar value rows with four factory-only selected rows and four unselected observed boundary rows | Public-safe payload shape only; no raw strings or numeric meanings. |
| `mesh-noise-vent-fixture` | `satisfied-static` | mesh value id 3, noise value id 12, and vent value id 25 are anchored to component apply helpers and DAT_00855400 | Static component string-field boundary only, not runtime component mesh/noise/vent dispatch. |
| `indexed-scalar-fixture` | `satisfied-public-safe` | indexedScalar164 value id 20 is observed as one two-scalar roundtrip payload shape | Static indexed-scalar payload-shape boundary only; no runtime index meaning is inferred. |
| `stop-fixture` | `enforced` | runtime/Godot/Ghidra/patch/product/rebuild guards remain false with zero runtime rows | Defer instead of broadening. |

## Claim Boundary

This proves only that the selected `component` value-ID interface is materialized as public-safe static fixture rows, with static factory/apply/registry anchors and public-safe payload-shape counts.

This does not prove runtime PhysicsScript behavior, runtime component behavior, runtime component mesh dispatch, runtime component noise dispatch, runtime component vent dispatch, runtime component flag behavior, runtime component indexed-scalar behavior, serialized PhysicsScript completeness, exact PhysicsScript layouts, exact component record layout, complete value-ID semantics, raw string identity, raw numeric value meaning, BEA patching behavior, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.

The next selected static child lane is `PhysicsScript Weapon Rebuild Fixture Proof Plan`.
