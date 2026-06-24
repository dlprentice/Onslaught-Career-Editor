# PhysicsScript Rebuild Interface Rollup Readiness Note

Status: complete static rollup, not runtime proof
Date: 2026-06-10
Scope: `physics-script-rebuild-interface-rollup`

This readiness note records a public-safe static rollup that consolidates the PhysicsScript copied-corpus parser, semantic ledger, scalar/string fixture, value-id crosswalk, and static subsystem contract into one rebuild-facing interface vocabulary. It does not run BEA, inspect private frames, mutate Ghidra, patch an executable, create a Godot project, wire product UI, or implement a rebuild.

Parent slice: `PhysicsScript Value-ID Semantic Crosswalk Proof Plan`
Public proof path: `physics-script-rebuild-interface-rollup.md`
Public schema path: `physics-script-rebuild-interface-rollup.v1.json`
Proof title: `PhysicsScript Rebuild Interface Rollup Proof Plan`

Static closeout context: `6411/6411 = 100.00%`; `0 / 0 / 0`; `1179/1179 = 100.00%`.

Representative anchors:

| Family | Anchors |
| --- | --- |
| `unit` | `CPhysicsScriptStatements__CreateStatementType2`, `CUnitStatement__LoadFromMemBuffer`, `CPhysicsUnitValueList__LoadFromMemBuffer`, `DAT_008553fc`. |
| `weapon` | `CPhysicsScriptStatements__CreateStatementType3`, `CWeaponStatement__LoadFromMemBuffer`, `CPhysicsWeaponValueList__LoadFromMemBuffer`, `DAT_008553e8`. |
| `weapon-mode` | `CPhysicsScriptStatements__CreateStatementType4`, `CWeaponModeStatement__LoadFromMemBuffer`, `CPhysicsWeaponModeValueList__LoadFromMemBuffer`, `DAT_008553ec`. |
| `round` | `CPhysicsScriptStatements__CreateStatementType5`, `CRoundStatement__LoadFromMemBuffer`, `CPhysicsRoundValueList__LoadFromMemBuffer`, `DAT_008553f0`. |
| `spawner` | `CPhysicsScriptStatements__CreateStatementType6`, `CSpawnerStatement__LoadFromMemBuffer`, `CSpawnerUnit__ApplyToSpawnerByName`, `DAT_008553f4`. |
| `explosion` | `CPhysicsScriptStatements__CreateStatementType7`, `CExplosionStatement__LoadFromMemBuffer`, `CExplosionBasedOn__ApplyToExplosionByName`, `DAT_008553f8`. |
| `component` | `CPhysicsScriptStatements__CreateStatementType10`, `CComponentStatement__LoadFromMemBuffer`, `CComponentIndexedScalar164__ApplyToComponentByName`, `DAT_00855400`. |
| `feature` | `CPhysicsScriptStatements__CreateStatementType8`, `CFeatureStatement__LoadFromMemBuffer`, `CFeatureTexture__ApplyToFeatureByName`, `DAT_00855404`. |
| `hazard` | `CPhysicsScriptStatements__CreateStatementType9`, `CHazardStatement__LoadFromMemBuffer`, `CHazardEffect__ApplyToHazardByName`, `DAT_00855408`. |

Readiness accounting:

- `rollupStatus=physics-script-rebuild-interface-rollup-complete-static-interface-vocabulary-not-runtime-proof`
- `physicsScriptRebuildInterfaceRollupStatus=physics-script-rebuild-interface-rollup-complete-static-interface-vocabulary-not-runtime-proof`
- `selectedSourceProofCount=5`
- `sourceProofCount=5`
- `sourceSchemaCount=3`
- `sourceMirrorPairCount=8`
- `topLevelFamilyCount=9`
- `semanticBucketCount=10`
- `fixtureAggregateClassCount=5`
- `fixtureClassDefinitionCount=6`
- `syntheticFixtureCaseCount=13`
- `interfaceRowCount=9`
- `valueInterfaceRowCount=87`
- `boundedCrosswalkRowCount=87`
- `observedSelectedRowCount=72`
- `factoryOnlySelectedRowCount=15`
- `unselectedObservedRowCount=113`
- `physicsScriptTopLevelStatementCount=777`
- `physicsScriptValueListNodeCount=6803`
- `physicsScriptStatementValuePairCount=185`
- `physicsScriptRawValuePayloadBytesPreserved=73796`
- `falseGuardCount=34`
- `zeroCounterCount=19`
- `publicLeakCheck=PASS`
- `latestGhidraBackupClass=verified-static-backup-redacted`
- `selectedNextSlice=PhysicsScript Rebuild Fixture Selection Proof Plan`
- `recommendedNextFixtureFamily=explosion`
- `observedValueIdCount=14`
- `selectedCrosswalkRowCount=14`
- `factoryOnlySelectedValueIdCount=0`
- `unselectedObservedValueIdCount=0`
- `runtimeExecution=false`
- `beLaunch=false`
- `newLaunch=false`
- `screenshotCapture=false`
- `godotWork=false`
- `ghidraMutation=false`
- `executablePatching=false`
- `productUiWired=false`
- `rebuildImplementation=false`
- `completeValueIdSemanticsProven=false`
- `all185PairsSemanticallyNamed=false`
- `rawStringIdentityProven=false`
- `rawNumericMeaningProven=false`

What this proves:

- The existing PhysicsScript static proof set can be referenced as one rebuild-facing interface rollup.
- Parser/corpus accounting is machine-checkable: `175603` bytes, stream header `0x12`, `777` top-level statements, `6803` value-list nodes, and `185` unique statement/value-id pairs.
- Selected value-id accounting is machine-checkable: `87` bounded selected rows, `72` observed selected rows, `15` factory-only selected rows, and `113` unselected observed rows.
- The result is public-safe and static-only.

What remains unproven:

- Runtime PhysicsScript behavior or runtime physics outcomes.
- Serialized PhysicsScript completeness.
- Exact concrete record layouts, exact registry container layout, or exact source-body identity.
- Complete value-id semantics, all `185` observed pairs semantically named, complete nested enum semantics, raw string identity, or raw numeric value meaning.
- BEA patching behavior, visual QA, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
