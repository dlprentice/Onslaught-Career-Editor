# PhysicsScript Rebuild Fixture Selection Readiness Note

Status: complete fixture selection, not runtime proof
Date: 2026-06-10
Scope: `physics-script-rebuild-fixture-selection`

Wave/proof context: `PhysicsScript Rebuild Fixture Selection Proof Plan` selects `explosion` as the first narrow PhysicsScript rebuild fixture family after the completed `PhysicsScript Rebuild Interface Rollup Proof Plan`.

Machine-checkable artifact: `physics-script-rebuild-fixture-selection.v1.json`.

Readiness tokens:

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

Selected static anchors:

| Anchor | Role |
| --- | --- |
| `CPhysicsScriptStatements__CreateStatementType7` | Explosion value factory. |
| `CExplosionStatement__LoadFromMemBuffer` | Explosion statement loader. |
| `CPhysicsExplosionValueList__LoadFromMemBuffer` | Explosion value-list loader. |
| `CExplosionStatement__CreateExplosionAndRecurse` | Explosion create/recurse bridge. |
| `CExplosionBasedOn__ApplyToExplosionByName` | Static `basedOn` copy/apply anchor. |
| `CExplosionValue__ApplyToExplosionByName` | Static value apply anchor for selected effect/sound/scalar rows. |
| `DAT_008553f8` | Static explosion registry global. |

This readiness note proves only that the next static child lane was selected with machine-checkable public-safe boundaries. It does not prove runtime PhysicsScript behavior, runtime explosion behavior, runtime explosion damage, runtime explosion visual effects, runtime explosion audio, serialized PhysicsScript completeness, exact layouts, complete value-ID semantics, raw string identity, raw numeric value meaning, Ghidra mutation, BEA patching behavior, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
