# PhysicsScript Rebuild Fixture Selection Proof Plan

Status: complete fixture selection, not runtime proof
Last updated: 2026-06-10
Scope: `physics-script-rebuild-fixture-selection`

This result selects the first narrow PhysicsScript rebuild fixture path after the completed [PhysicsScript Rebuild Interface Rollup Proof Plan](physics-script-rebuild-interface-rollup.md).

Machine-checkable artifact:

- [physics-script-rebuild-fixture-selection.v1.json](physics-script-rebuild-fixture-selection.v1.json)

Follow-up Weapon-Mode fixture result: [PhysicsScript Weapon-Mode Rebuild Fixture Proof Plan](physics-script-weapon-mode-rebuild-fixture-proof-plan.md), backed by [physics-script-weapon-mode-rebuild-fixture-proof-plan.v1.json](physics-script-weapon-mode-rebuild-fixture-proof-plan.v1.json), records fixtureStatus=physics-script-weapon-mode-rebuild-fixture-proof-plan-complete-static-weapon-mode-value-interface-fixture-not-runtime-proof. The child lane materialized selectedNextSlice=PhysicsScript Unit Rebuild Fixture Proof Plan and selectedNextScope=physics-script-unit-rebuild-fixture-proof-plan while preserving selectedFixtureFamily=weapon-mode, selectedFixturePath=weapon-mode-selected-value-id-interface-static-fixture, selectedValueIds=2/6/15/18/24/28/31/34/36, factoryOnlyValueIds=15/36, unselectedObservedValueIds=1/3/4/5/8/9/10/11/12/13/14/16/17/19/20/21/22/23/26/27/29/30/32/33/35, selectedMixedPayloadShapeValueIds=2/24, runtimeExecution=false, godotWork=false, ghidraMutation=false, and rebuildImplementation=false. Static anchors include CWeaponModeStatement__LoadFromMemBuffer, CPhysicsWeaponModeValueList__LoadFromMemBuffer, CWeaponModeStatement__CreateWeaponModeAndRecurse, and DAT_008553ec. Active next static child lane: PhysicsScript Unit Rebuild Fixture Proof Plan.

Follow-up Round fixture result: [PhysicsScript Round Rebuild Fixture Proof Plan](physics-script-round-rebuild-fixture-proof-plan.md), backed by [physics-script-round-rebuild-fixture-proof-plan.v1.json](physics-script-round-rebuild-fixture-proof-plan.v1.json), records fixtureStatus=physics-script-round-rebuild-fixture-proof-plan-complete-static-round-value-interface-fixture-not-runtime-proof. The child lane materialized selectedNextSlice=PhysicsScript Weapon-Mode Rebuild Fixture Proof Plan and selectedNextScope=physics-script-weapon-mode-rebuild-fixture-proof-plan while preserving selectedFixtureFamily=round, selectedFixturePath=round-selected-value-id-interface-static-fixture, selectedValueIds=4/8/9/24/33/35/36, unselectedObservedValueIds=1/2/3/5/6/10/11/12/13/14/15/16/17/18/19/22/23/26/27/28/29/30/31/32/37/38, selectedMixedPayloadShapeValueIds=8/9, runtimeExecution=false, godotWork=false, ghidraMutation=false, and rebuildImplementation=false. Static anchors include CRoundStatement__LoadFromMemBuffer, CPhysicsRoundValueList__LoadFromMemBuffer, CRoundStatement__CreateRoundAndRecurse, and DAT_008553f0. Active next static child lane: PhysicsScript Weapon-Mode Rebuild Fixture Proof Plan.

Follow-up weapon fixture result: [PhysicsScript Weapon Rebuild Fixture Proof Plan](physics-script-weapon-rebuild-fixture-proof-plan.md), backed by [physics-script-weapon-rebuild-fixture-proof-plan.v1.json](physics-script-weapon-rebuild-fixture-proof-plan.v1.json), records fixtureStatus=physics-script-weapon-rebuild-fixture-proof-plan-complete-static-weapon-value-interface-fixture-not-runtime-proof. The child lane materialized selectedNextSlice=PhysicsScript Round Rebuild Fixture Proof Plan and selectedNextScope=physics-script-round-rebuild-fixture-proof-plan while preserving selectedFixtureFamily=weapon, selectedFixturePath=weapon-selected-value-id-interface-static-fixture, selectedValueIds=1/4/5/14, unselectedObservedValueIds=2/3/6/7/8/9/10/11/12/13, selectedMixedPayloadShapeValueIds=1, runtimeExecution=false, godotWork=false, ghidraMutation=false, and rebuildImplementation=false. Static anchors include CWeaponStatement__LoadFromMemBuffer, CPhysicsWeaponValueList__LoadFromMemBuffer, CWeaponStatement__CreateWeaponAndRecurse, and DAT_008553e8. Active next static child lane: PhysicsScript Round Rebuild Fixture Proof Plan.

Follow-up explosion fixture result: [PhysicsScript Explosion Rebuild Fixture Proof Plan](physics-script-explosion-rebuild-fixture-proof-plan.md), backed by [physics-script-explosion-rebuild-fixture-proof-plan.v1.json](physics-script-explosion-rebuild-fixture-proof-plan.v1.json), records fixtureStatus=physics-script-explosion-rebuild-fixture-proof-plan-complete-static-explosion-value-interface-fixture-not-runtime-proof. The child lane materialized selectedNextSlice=PhysicsScript Spawner Rebuild Fixture Proof Plan while preserving selectedFixtureFamily=explosion, selectedFixturePath=explosion-selected-value-id-interface-static-fixture, selectedValueInterfaceRowCount=14, selectedValueIds=1/2/3/4/5/6/7/8/9/10/11/12/13/15, selectedObservedValueIdCount=14, selectedFactoryOnlyValueIdCount=0, selectedUnselectedObservedValueIdCount=0, selectedPayloadShapeCaseCount=15, selectedMixedPayloadShapeValueIds=10, soundObservedOwnedStringShapeCount=79, soundObservedThreeScalarShapeCount=7, deferredFactoryValueIds=14, falseGuardCount=40, zeroCounterCount=26, publicLeakCheck=PASS, runtimeExecution=false, godotWork=false, ghidraMutation=false, executablePatching=false, productUiWired=false, and rebuildImplementation=false. The active next static child lane is PhysicsScript Spawner Rebuild Fixture Proof Plan.

Follow-up spawner fixture result: [PhysicsScript Spawner Rebuild Fixture Proof Plan](physics-script-spawner-rebuild-fixture-proof-plan.md), backed by [physics-script-spawner-rebuild-fixture-proof-plan.v1.json](physics-script-spawner-rebuild-fixture-proof-plan.v1.json), records fixtureStatus=physics-script-spawner-rebuild-fixture-proof-plan-complete-static-spawner-value-interface-fixture-not-runtime-proof. The child lane materialized selectedNextSlice=PhysicsScript Hazard Rebuild Fixture Proof Plan while preserving selectedFixtureFamily=spawner, selectedFixturePath=spawner-selected-value-id-interface-static-fixture, selectedValueInterfaceRowCount=14, selectedObservedValueIdCount=10, selectedFactoryOnlyValueIdCount=4, selectedUnselectedObservedValueIdCount=0, selectedPayloadShapeCaseCount=11, selectedMixedPayloadShapeValueIds=1, factoryOnlyValueIds=4/5/10/13, runtimeExecution=false, godotWork=false, ghidraMutation=false, and rebuildImplementation=false. The active next static child lane is PhysicsScript Hazard Rebuild Fixture Proof Plan.

Follow-up hazard fixture result: [PhysicsScript Hazard Rebuild Fixture Proof Plan](physics-script-hazard-rebuild-fixture-proof-plan.md), backed by [physics-script-hazard-rebuild-fixture-proof-plan.v1.json](physics-script-hazard-rebuild-fixture-proof-plan.v1.json), records fixtureStatus=physics-script-hazard-rebuild-fixture-proof-plan-complete-static-hazard-value-interface-fixture-not-runtime-proof. The child lane materialized selectedNextSlice=PhysicsScript Feature Rebuild Fixture Proof Plan while preserving selectedFixtureFamily=hazard, selectedFixturePath=hazard-selected-value-id-interface-static-fixture, selectedValueInterfaceRowCount=4, selectedObservedValueIdCount=3, selectedFactoryOnlyValueIdCount=1, selectedUnselectedObservedValueIdCount=0, selectedPayloadShapeCaseCount=4, selectedMixedPayloadShapeValueIds=2, factoryOnlyValueIds=4, runtimeExecution=false, godotWork=false, ghidraMutation=false, and rebuildImplementation=false. The active next static child lane is PhysicsScript Feature Rebuild Fixture Proof Plan.

Follow-up feature fixture result: [PhysicsScript Feature Rebuild Fixture Proof Plan](physics-script-feature-rebuild-fixture-proof-plan.md), backed by [physics-script-feature-rebuild-fixture-proof-plan.v1.json](physics-script-feature-rebuild-fixture-proof-plan.v1.json), records fixtureStatus=physics-script-feature-rebuild-fixture-proof-plan-complete-static-feature-value-interface-fixture-not-runtime-proof. The child lane materialized selectedNextSlice=PhysicsScript Component Rebuild Fixture Proof Plan while preserving selectedFixtureFamily=feature, selectedFixturePath=feature-selected-value-id-interface-static-fixture, selectedValueInterfaceRowCount=7, selectedObservedValueIdCount=5, selectedFactoryOnlyValueIdCount=2, selectedUnselectedObservedValueIdCount=0, selectedPayloadShapeCaseCount=6, selectedMixedPayloadShapeValueIds=2, factoryOnlyValueIds=5/7, runtimeExecution=false, godotWork=false, ghidraMutation=false, and rebuildImplementation=false. The active next static child lane is PhysicsScript Component Rebuild Fixture Proof Plan.

Selection tokens:

- `fixtureSelectionStatus=physics-script-rebuild-fixture-selection-complete-explosion-selected`
- `selectedFixtureFamily=explosion`
- `selectedFixturePath=explosion-selected-value-id-interface-static-fixture`
- `selectedChildLane=PhysicsScript Explosion Rebuild Fixture Proof Plan`
- `selectedCandidateRank=1`
- `candidateFamilyCount=9`
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
- `selectedValueIds=1/2/3/4/5/6/7/8/9/10/11/12/13/15`
- `ownedStringFieldCorpusCount=539`
- `scalarFieldCorpusCount=330`
- `sourceProofCount=5`
- `sourceSchemaCount=3`
- `sourceMirrorPairCount=8`
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
- `falseGuardCount=37`
- `zeroCounterCount=23`
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
- `completeValueIdSemanticsProven=false`
- `all185PairsSemanticallyNamed=false`
- `rawStringIdentityProven=false`
- `rawNumericMeaningProven=false`
- `runtimeExplosionBehaviorProven=false`
- `runtimeExplosionDamageProven=false`
- `runtimeExplosionVisualEffectProven=false`
- `runtimeExplosionAudioProven=false`
- `runtimeObservationRows=0`
- `physicsScriptRuntimeEvidenceRows=0`
- `runtimePhysicsScriptRows=0`
- `runtimeExplosionRows=0`
- `runtimeExplosionDamageRows=0`
- `runtimeExplosionVisualRows=0`
- `runtimeExplosionAudioRows=0`
- `beProcessesAfterSelection=0`

This is not runtime PhysicsScript behavior proof, runtime physics outcome proof, runtime explosion behavior proof, runtime explosion damage proof, runtime explosion visual effect proof, runtime explosion audio proof, serialized PhysicsScript completeness, exact concrete layout proof, complete value-id semantics, all-observed-pair semantic naming, raw string identity proof, raw numeric value meaning proof, BEA launch, screenshot capture, private-frame review, source-selection proof, native-input run, debugger attachment, Godot work, Ghidra mutation, executable patching, product UI wiring, rebuild implementation, rebuild parity, or no-noticeable-difference parity.

## Static Closeout Context

| Track | Current |
| --- | --- |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Active current-risk focused accounting | `1179/1179 = 100.00%` |
| Remaining active focused work | `0` |
| Latest verified Ghidra backup | `latestGhidraBackupClass=verified-static-backup-redacted` |

This fixture selection does not change `static-reaudit-progress.json`, `static-reaudit-current-risk-ledger.json`, the current percentages, the Ghidra database, or the installed game.

## Selected Fixture Path

The selected first fixture family is `explosion`, specifically `explosion-selected-value-id-interface-static-fixture`.

| Surface | Selected static evidence |
| --- | --- |
| Factory and loaders | `CPhysicsScriptStatements__CreateStatementType7`, `CExplosionStatement__LoadFromMemBuffer`, and `CPhysicsExplosionValueList__LoadFromMemBuffer`. |
| Create and registry bridge | `CExplosionStatement__CreateExplosionAndRecurse` and `DAT_008553f8`. |
| Apply anchors | `CExplosionBasedOn__ApplyToExplosionByName` for `basedOn`; `CExplosionValue__ApplyToExplosionByName` for named effect/sound fields and offset-named scalar fields. |
| Selected value IDs | `selectedValueIds=1/2/3/4/5/6/7/8/9/10/11/12/13/15`; value id `14` is not selected by this proof. |
| Owned-string-shaped fields | `basedOn`, `airEffect`, `groundEffect`, `waterEffect`, `unitEffect`, `sound`, and `waterSound`; `ownedStringFieldCorpusCount=539`. |
| Scalar fields | `scalar34`, `scalar38`, `scalar3C`, `scalar40`, `scalar44`, `scalar4C`, and `scalar48`; `scalarFieldCorpusCount=330`. |

The future fixture proof should begin with the selected value-ID interface and public-safe scalar/string payload-shape model. It should not start with runtime explosion damage, audio, visuals, or object outcome claims.

## Candidate Ranking

| Rank | Candidate fixture family | Decision | Rationale |
| ---: | --- | --- | --- |
| `1` | `explosion` | selected | Fully observed selected value-ID surface: `14` observed ids, `14` selected crosswalk rows, zero factory-only selected rows, and zero unselected observed ids. |
| `2` | `spawner` | deferred | No unselected observed ids, but four factory-only selected rows make it less clean as the first deterministic fixture. |
| `3` | `hazard` | deferred | Small surface, but one factory-only selected row makes the evidence boundary less clean than explosion. |
| `4` | `feature` | deferred | No unselected observed ids, but two factory-only selected rows remain explicit boundary debt. |
| `5` | `component` | deferred | High-value selected surface, but four unselected observed ids and four factory-only selected rows remain. |
| `6` | `weapon` | deferred | Weapon registry rows are valuable, but ten unselected observed ids remain and runtime firing behavior is easy to overclaim. |
| `7` | `round` | deferred | Projectile/round rows are important, but twenty-six unselected observed ids and runtime projectile outcomes are out of scope. |
| `8` | `weapon-mode` | deferred | Mode rows tempt firing cadence and launch-angle behavior claims while twenty-five unselected observed ids remain. |
| `9` | `unit` | deferred | Broad AI/unit surface with forty-eight unselected observed ids; it should follow narrower deterministic fixture work. |

## Future Evidence Requirements

The selected child lane, `PhysicsScript Explosion Rebuild Fixture Proof Plan`, should require these rows before any runtime or rebuild implementation claim:

| Row | Requirement | Boundary |
| --- | --- | --- |
| `family-fixture` | Reconfirm explosion family coverage from the rollup: `14` observed ids, `14` selected rows, zero factory-only selected rows, and zero unselected observed ids. | Static family-selection proof only. |
| `loader-fixture` | Preserve `CPhysicsScriptStatements__CreateStatementType7`, `CExplosionStatement__LoadFromMemBuffer`, `CPhysicsExplosionValueList__LoadFromMemBuffer`, `CExplosionStatement__CreateExplosionAndRecurse`, and `DAT_008553f8`. | Static loader/factory/registry bridge only. |
| `value-interface-fixture` | Preserve exact selected value ids `1,2,3,4,5,6,7,8,9,10,11,12,13,15` and all `14` rebuild-facing field names. | Selected value-ID interface only, not complete value semantics. |
| `payload-shape-fixture` | Model seven owned-string-shaped fields and seven scalar4 fields using the scalar/string fixture classes without publishing copied strings or raw numeric meanings. | Public-safe payload shape only. |
| `based-on-fixture` | Treat `basedOn` as a static copy/apply anchor through `CExplosionBasedOn__ApplyToExplosionByName`. | Static base-copy field boundary only, not runtime explosion inheritance behavior. |
| `stop-fixture` | Stop if the proof needs runtime effects, audio, damage, visual behavior, BE launch, Godot, Ghidra mutation, executable patching, product UI wiring, rebuild implementation, raw values, or private paths. | Defer instead of broadening. |

## What This Proves

- The first PhysicsScript rebuild fixture path has been selected from the completed static interface rollup.
- `explosion` is the safest first PhysicsScript fixture family because it has a fully selected observed value-ID interface and no factory-only or unselected observed value-ID debt.
- The future child lane has explicit evidence requirements and stop conditions before runtime, Godot, patching, or rebuild implementation begins.

## Not Claimed

This does not prove runtime PhysicsScript behavior, runtime physics outcomes, runtime explosion behavior, runtime explosion damage, runtime explosion visual effects, runtime explosion audio, serialized PhysicsScript completeness, exact PhysicsScript layouts, exact explosion record layout, complete value-ID semantics, all-observed-pair semantic naming, raw string identity, raw numeric value meaning, exact source-body identity, BEA patching behavior, visual QA, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.

Follow-up component fixture result: [PhysicsScript Component Rebuild Fixture Proof Plan](physics-script-component-rebuild-fixture-proof-plan.md), backed by [physics-script-component-rebuild-fixture-proof-plan.v1.json](physics-script-component-rebuild-fixture-proof-plan.v1.json), records fixtureStatus=physics-script-component-rebuild-fixture-proof-plan-complete-static-component-value-interface-fixture-not-runtime-proof and selectedNextSlice=PhysicsScript Weapon Rebuild Fixture Proof Plan. The child lane materialized selectedFixtureFamily=component, selectedFixturePath=component-selected-value-id-interface-static-fixture, selectedValueInterfaceRowCount=20, selectedObservedValueIdCount=16, selectedFactoryOnlyValueIdCount=4, selectedUnselectedObservedValueIdCount=4, selectedPayloadShapeCaseCount=16, factoryOnlyValueIds=10/16/17/24, unselectedObservedValueIds=2/4/14/19, runtimeExecution=false, godotWork=false, ghidraMutation=false, and rebuildImplementation=false. Active next static child lane: PhysicsScript Weapon Rebuild Fixture Proof Plan.
