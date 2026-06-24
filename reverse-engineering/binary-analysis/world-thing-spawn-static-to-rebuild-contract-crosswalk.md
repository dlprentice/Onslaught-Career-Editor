# World / Thing / Spawn Static-To-Rebuild Contract Crosswalk Proof Plan

Status: static-to-rebuild contract crosswalk complete, not runtime proof
Last updated: 2026-06-09
Scope: `world-thing-spawn-static-to-rebuild-contract-crosswalk`

This result turns the selected World / Thing / Spawn source proofs into one implementation-facing static contract for rebuild planning:

- Parent slice: `Static-To-Proof Rebuild Transition Next Safe Slice Selection Proof Plan`
- Public proof path: `world-thing-spawn-static-to-rebuild-contract-crosswalk.md`
- [world-thing-spawn-static-to-rebuild-contract-crosswalk.v1.json](world-thing-spawn-static-to-rebuild-contract-crosswalk.v1.json)

This is not a runtime proof wave, private-frame review, row observation, BEA launch, screenshot or frame capture, OCR pass, raw dialogue publication, source-selection proof, native-input run, debugger attachment, Godot project, Ghidra mutation, executable patch, rebuild implementation, rebuild parity proof, or no-noticeable-difference parity proof.

## Static Closeout Context

| Track | Current |
| --- | --- |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Active current-risk focused accounting | `1179/1179 = 100.00%` |
| Remaining active focused work | `0` |
| Latest verified Ghidra backup | `latestGhidraBackupClass=verified-static-backup-redacted` |

This crosswalk does not change `static-reaudit-progress.json`, `static-reaudit-current-risk-ledger.json`, or the current percentages.

## Source Proofs

| Source proof | Contract input |
| --- | --- |
| [World / Thing / Spawn Copied-Corpus Schema Proof](world-thing-spawn-copied-corpus-schema-proof.md) | `574` raw `GetThingRef` rows, `70` raw `SpawnThing` rows, `644` total raw rows, `436` unique object-reference rows, `447` spawn-preserving rows, selected `training-target-spawn-family`, and selected `training-target-zone-getthingref-family`. |
| [World / Thing / Spawn Spawner Handoff Static Proof](world-thing-spawn-spawner-handoff-static-proof.md) | `8` handoff layers, `12` static field roles, selected `training-target-spawn-family`, `DAT_008553f4`, `0x0050f970 CWorldPhysicsManager__CreateSpawner`, `0x004e3c60 CSpawnerThng__DoSpawn`, `CUnit__VFunc08_InitAndAddToWorld`, and `0x004fc3a0 CUnit__SetSpawnCooldownState3`. |
| [World / Thing / Spawn GetThingRef Object-Reference Static Proof](world-thing-spawn-getthingref-object-reference-static-proof.md) | Selected `training-target-zone-getthingref-family`, `9` raw selected `GetThingRef` rows, `8` unique object-reference rows, `1` duplicate call row, `9` empty-spawner rows, and `4` static linkage layers. |

Contract accounting:

- `crosswalkStatus=world-thing-spawn-static-to-rebuild-contract-crosswalk-complete-static-contract-not-runtime-proof`
- `worldThingSpawnStaticToRebuildContractCrosswalkStatus=world-thing-spawn-static-to-rebuild-contract-crosswalk-complete-static-contract-not-runtime-proof`
- `selectedSourceProofCount=3`
- `sourceSchemaCount=3`
- `contractSectionCount=9`
- `contractFalseGuardCount=35`
- `contractZeroCounterCount=16`
- `publicLeakCheck=PASS`
- `selectedNextSlice=MissionScript Command-Effect Rebuild Interface Rollup Proof Plan`

Guard tokens:

- `crosswalkOnly=true`
- `staticPublicSafeOnly=true`
- `copiedAppOwnedInputOnly=true`
- `trackedLooseMslCorpusOnly=true`
- `fieldRolesStaticOnly=true`
- `programFilesInputUsed=false`
- `liveLooseMslLoading=false`
- `packedResourceScriptSelectionProven=false`
- `runtimeExecution=false`
- `beLaunch=false`
- `newLaunch=false`
- `screenshotCapture=false`
- `privateFrameReviewPerformed=false`
- `rowObservation=false`
- `exactTextOcrPerformed=false`
- `rawDialoguePublished=false`
- `visibleTextExcerptPublished=false`
- `sourceSelectionObserved=false`
- `sourceSelectionProven=false`
- `nativeInput=false`
- `debuggerAttachment=false`
- `godotWork=false`
- `ghidraMutation=false`
- `executablePatching=false`
- `rebuildImplementation=false`
- `runtimeObjectIdentityProven=false`
- `runtimeObjectLookupByNameProven=false`
- `runtimeSpawnThingBehaviorProven=false`
- `runtimeGetThingRefBehaviorProven=false`
- `runtimeWorldLoadingProven=false`
- `runtimeSpawnerBehaviorProven=false`
- `runtimeUnitBattleEngineSpawnBehaviorProven=false`
- `runtimeMissionScriptExecutionProven=false`
- `runtimeCommandEffectsProven=false`
- `exactDescriptorLayoutProven=false`
- `exactHandlerAddressProven=false`
- `exactVmObjectCodeWorldThingSpawnerUnitLayoutsProven=false`
- `exactSourceBodyIdentityProven=false`
- `rebuildParityProven=false`
- `noNoticeableDifferenceParityProven=false`
- `runtimeObservationRows=0`
- `missionScriptRuntimeEvidenceRows=0`
- `privateFrameRowsObserved=0`
- `sourceObservedRows=0`
- `sourceRuntimeObservationRows=0`
- `sourceRowStatusChangedCount=0`
- `ghidraMutationRows=0`
- `rebuildImplementationRows=0`
- `beProcessesAfterCrosswalk=0`
- `publicAbsolutePathLeakCount=0`
- `publicSha256ValueLeakCount=0`
- `publicWindowIdentifierLeakCount=0`
- `publicProcessIdentifierLeakCount=0`
- `privatePathLeakCount=0`
- `rawArtifactLeakCount=0`
- `rawDialogueLeakCount=0`

## Implementation Contract Rows

| Contract row | Static anchors | Rebuild-facing obligation |
| --- | --- | --- |
| Corpus row identity | `mission-thing-usage.md`, `world-thing-spawn-copied-corpus-schema.v1.json`, `training-target-spawn-family`, `training-target-zone-getthingref-family`, `level022`, `level100` | Preserve level, directory, file, call, thing label, spawner cell, casing, raw duplicate-call counts, unique object-reference counts, and spawner-preserving counts as distinct metrics from tracked loose-MSL corpus rows only. |
| MissionScript descriptor/datatype | `IScript__SpawnThing`, `IScript__GetThingRef`, `CThingPtrDataType`, `ScriptCommandRegistry__InitBuiltins`, `0x0064ce50`, `0x0064f210`, `0x0052ff30` | Treat `SpawnThing` and `GetThingRef` as thing-pointer command families with static descriptor/datatype anchors, without claiming runtime dispatch or exact handler layout. |
| Bytecode preload and dependency scan | `0x005392a0 CScriptObjectCode__CollectSpawnThings`, opcode `0x18`, `CWorldMeshList__Add` | Model the static `SpawnThing` pre-scan that collects spawn dependencies before runtime MissionScript execution proof. |
| World load and mesh dependency | `0x0050b9c0 CWorld__LoadWorld`, `0x0050ac70 CWorld__LoadScriptEvents`, `0x0050d9e0 CWorldMeshList__Add`, `DAT_00855358`, `DAT_008553fc +0xb0` | Keep world load, script-event load, and mesh-list dependency boundaries explicit before any object or spawn runtime proof. |
| World factory and init | `0x0050dcb0 CWorld__SpawnInitialThings`, `0x0050df80 CWorldPhysicsManager__CreateThingByType`, `0x0048c650 InitThing__CreateThingByType`, `0x0040e280 CInitThing__LoadFromMemBuffer`, `CThing__InitRenderThingFromInitMeshName` | Represent static thing-definition to init-object factory flow without claiming exact object layout or runtime creation. |
| Spawner gate and wave shell | `0x004e3010 CSpawnerThng__Init`, `0x004e36c0 CSpawnerThng__FindSpawnerByName`, `0x004e3c60 CSpawnerThng__DoSpawn`, `0x004e3f90 CSpawnerThng__ProcessSpawnWave`, `0x0050f680 CSpawnerThng__IsSpawnTypeAllowed`, `0x00511440 CWorldPhysicsManager__IsSpawnerThingTypeAllowedByName`, `0x005115b0 CWorldPhysicsManager__MapGunOrSpawnerTagToIndex`, `0x00511ad0 CWorldPhysicsManager__AddSpawnerByName`, `DAT_008553f4` | Preserve spawner name/tag/type-gate and wave-processing shell as static contract rows only. |
| Static field roles | `CSpawnerThng+0x0468`, `CSpawnerThng+0x007c`, `CSpawnerThng+0x0080`, `CSpawnerThng+0x0090`, `CSpawnerThng+0x0094`, `CSpawnerThng+0x0098`, `CSpawnerThng+0x009c`, `CSpawnerThng+0x00a0`, `CSpawnerThng+0x00a4`, `CSpawnerThng+0x00b0`, `CUnit+0x0168`, `CUnit+0x016c` | Preserve the twelve static role labels as implementation hints, not final C++ layouts. |
| Unit world-add and cooldown | `CUnit__VFunc08_InitAndAddToWorld`, `CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk`, `0x004fc3a0 CUnit__SetSpawnCooldownState3` | Carry Unit/BattleEngine world-add and spawn-cooldown anchors into rebuild planning without claiming runtime activation. |
| Object-reference and render/resource boundary | `Target Zone 1`, `Target Zone 2`, `Target Zone 3`, `Target Zone 4`, `world-thing-spawn-getthingref-object-reference-static.v1.json`, `CThing__InitRenderThingFromInitMeshName`, `mesh-resource-render-static-contract.md`, `texture-resource-decode-static-contract.md` | Keep `GetThingRef` object labels and render/resource dependencies tied to the world/thing boundary while preserving runtime lookup and visual parity as separate proof. |

## What This Proves

- The selected World / Thing / Spawn static proof set has a single rebuild-facing contract vocabulary for corpus rows, command descriptors, bytecode preload, world load/factory/init, spawner gates, static field roles, Unit world-add/cooldown, object-reference labels, and render/resource boundaries.
- The crosswalk preserves the source proof counts: `574`, `70`, `644`, `436`, `447`, `34`, `9`, `8`, `1`, `9`, `8`, `12`, and `4`.
- The selected contract is public-safe and static-only; it publishes no private frame details, installed-game paths, user-profile paths, raw screenshots, executable patches, or operator-only evidence.

## Not Claimed

This does not prove runtime object identity, runtime `SpawnThing`, runtime `GetThingRef`, runtime MissionScript execution, runtime world loading, runtime spawner behavior, runtime Unit/BattleEngine spawn behavior, runtime object lookup by name, runtime AI activation, runtime collision, runtime damage, runtime HUD/message/audio output, live loose-MSL loading, packed-resource script selection, exact descriptor layout, exact handler address, exact VM/object-code/world/thing/spawner/Unit layouts, exact source-body identity, BEA patching behavior, visual QA, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.

## Next Useful Static-To-Proof Step

The next selected static child lane is `MissionScript Command-Effect Rebuild Interface Rollup Proof Plan`. It should consolidate completed static command-effect families into an implementation-facing interface rollup without claiming runtime MissionScript execution, runtime command effects, private-frame review, Godot, executable patching, rebuild parity, or no-noticeable-difference parity.
