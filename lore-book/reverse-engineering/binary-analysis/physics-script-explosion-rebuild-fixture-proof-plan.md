# PhysicsScript Explosion Rebuild Fixture Proof Plan

Status: complete static explosion value-interface fixture, not runtime proof
Last updated: 2026-06-10
Scope: `physics-script-explosion-rebuild-fixture-proof-plan`

This result materializes the selected `explosion` fixture chosen by the completed [PhysicsScript Rebuild Fixture Selection Proof Plan](physics-script-rebuild-fixture-selection.md). It turns the selected value-ID interface into public-safe fixture rows for rebuild planning without publishing copied strings, raw payload bytes, numeric values, private paths, or runtime observations.

Machine-checkable artifact:

- [physics-script-explosion-rebuild-fixture-proof-plan.v1.json](physics-script-explosion-rebuild-fixture-proof-plan.v1.json)

Fixture tokens:

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

| Value ID | Field | Crosswalk class | Public-safe copied-corpus shape evidence |
| ---: | --- | --- | --- |
| `1` | `basedOn` | `owned_string_at_08` | `owned_string_ascii_nul_shape_roundtrip=14` |
| `2` | `airEffect` | `owned_string_at_08` | `owned_string_ascii_nul_shape_roundtrip=111` |
| `3` | `scalar34` | `scalar4` | `scalar4_roundtrip=104` |
| `4` | `scalar38` | `scalar4` | `scalar4_roundtrip=94` |
| `5` | `groundEffect` | `owned_string_at_08` | `owned_string_ascii_nul_shape_roundtrip=107` |
| `6` | `waterEffect` | `owned_string_at_08` | `owned_string_ascii_nul_shape_roundtrip=107` |
| `7` | `unitEffect` | `owned_string_at_08` | `owned_string_ascii_nul_shape_roundtrip=107` |
| `8` | `scalar3C` | `scalar4` | `scalar4_roundtrip=17` |
| `9` | `scalar40` | `scalar4` | `scalar4_roundtrip=14` |
| `10` | `sound` | `owned_string_at_08` | `owned_string_ascii_nul_shape_roundtrip=79`; `three_scalar4_roundtrip=7` |
| `11` | `scalar44` | `scalar4` | `scalar4_roundtrip=6` |
| `12` | `scalar4C` | `scalar4` | `scalar4_roundtrip=80` |
| `13` | `scalar48` | `scalar4` | `scalar4_roundtrip=15` |
| `15` | `waterSound` | `owned_string_at_08` | `owned_string_ascii_nul_shape_roundtrip=7` |

The value id `10` `sound` row is intentionally a mixed payload-shape boundary. The value-ID crosswalk names it as a string-facing `sound` field, while copied-corpus shape classification sees `79` owned-string-shaped rows and `7` payload-size-12 rows classified by the scalar/string fixture as three-scalar roundtrip. This result preserves both shape classes and does not infer raw sound identity or numeric meaning.

Value id `14` is not hidden. It remains `deferredFactoryValueIds=14`: a factory boundary outside this selected copied-corpus-observed explosion fixture.

## Static Anchors

| Anchor | Role |
| --- | --- |
| `CPhysicsScriptStatements__CreateStatementType7` | Explosion value factory. |
| `CExplosionStatement__LoadFromMemBuffer` | Explosion statement loader. |
| `CPhysicsExplosionValueList__LoadFromMemBuffer` | Explosion value-list loader. |
| `CExplosionStatement__CreateExplosionAndRecurse` | Explosion create/recurse bridge. |
| `CExplosionBasedOn__ApplyToExplosionByName` | Static `basedOn` copy/apply anchor. |
| `CExplosionValue__ApplyToExplosionByName` | Static apply anchor for selected effect, sound, and scalar rows. |
| `DAT_008553f8` | Static explosion registry global. |

## Requirement Rows

| Row | Status | Evidence | Boundary |
| --- | --- | --- | --- |
| `family-fixture` | `satisfied-static` | `14` observed ids, `14` selected rows, zero factory-only selected rows, and zero unselected observed ids. | Static family-selection proof only. |
| `loader-fixture` | `satisfied-static` | `CPhysicsScriptStatements__CreateStatementType7`, `CExplosionStatement__LoadFromMemBuffer`, `CPhysicsExplosionValueList__LoadFromMemBuffer`, `CExplosionStatement__CreateExplosionAndRecurse`, and `DAT_008553f8`. | Static loader/factory/registry bridge only. |
| `value-interface-fixture` | `satisfied-static` | Selected value ids `1,2,3,4,5,6,7,8,9,10,11,12,13,15` and all `14` rebuild-facing field names. | Selected value-ID interface only, not complete value semantics. |
| `payload-shape-fixture` | `satisfied-public-safe` | Seven scalar4 selected fields, seven string-facing selected fields, and one explicit mixed payload-shape boundary for `sound`. | Public-safe payload shape only; no raw strings or numeric meanings. |
| `based-on-fixture` | `satisfied-static` | `basedOn` value id `1` is anchored to `CExplosionBasedOn__ApplyToExplosionByName`. | Static base-copy field boundary only, not runtime explosion inheritance behavior. |
| `stop-fixture` | `enforced` | Runtime, Godot, Ghidra, patch, product, rebuild, raw-value, and private-path guards remain false with zero runtime rows. | Defer instead of broadening. |

## What This Proves

- The selected explosion value-ID interface is materialized as public-safe static fixture rows.
- All selected explosion value ids are copied-corpus observed and carry static factory/apply/registry anchors.
- Public-safe payload shape counts are preserved, including the value id `10` mixed-shape boundary.
- Value id `14` remains explicit deferred factory boundary debt.

## Not Claimed

This is not runtime PhysicsScript behavior, runtime explosion behavior, runtime explosion damage, runtime explosion visual effects, runtime explosion audio, serialized PhysicsScript completeness, exact PhysicsScript layout, exact explosion record layout, complete value-ID semantics, raw string identity, raw numeric value meaning, runtime inheritance behavior, BEA patching behavior, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.

Follow-up spawner fixture result: [PhysicsScript Spawner Rebuild Fixture Proof Plan](physics-script-spawner-rebuild-fixture-proof-plan.md), backed by [physics-script-spawner-rebuild-fixture-proof-plan.v1.json](physics-script-spawner-rebuild-fixture-proof-plan.v1.json), records fixtureStatus=physics-script-spawner-rebuild-fixture-proof-plan-complete-static-spawner-value-interface-fixture-not-runtime-proof. The child lane materialized selectedNextSlice=PhysicsScript Hazard Rebuild Fixture Proof Plan while preserving selectedFixtureFamily=spawner, selectedFixturePath=spawner-selected-value-id-interface-static-fixture, selectedValueInterfaceRowCount=14, selectedObservedValueIdCount=10, selectedFactoryOnlyValueIdCount=4, selectedUnselectedObservedValueIdCount=0, selectedPayloadShapeCaseCount=11, selectedMixedPayloadShapeValueIds=1, factoryOnlyValueIds=4/5/10/13, runtimeExecution=false, godotWork=false, ghidraMutation=false, and rebuildImplementation=false.

The next selected static child lane is `PhysicsScript Spawner Rebuild Fixture Proof Plan`.
