# World / Thing / Spawn Static-To-Rebuild Contract Crosswalk Readiness Note

Status: complete static public-safe contract, not runtime proof
Date: 2026-06-09
Scope: `world-thing-spawn-static-to-rebuild-contract-crosswalk`

This readiness note records the World / Thing / Spawn Static-To-Rebuild Contract Crosswalk Proof Plan:

- Parent slice: `Static-To-Proof Rebuild Transition Next Safe Slice Selection Proof Plan`
- `reverse-engineering/binary-analysis/world-thing-spawn-static-to-rebuild-contract-crosswalk.md`
- `reverse-engineering/binary-analysis/world-thing-spawn-static-to-rebuild-contract-crosswalk.v1.json`

Static closeout context:

| Track | Current |
| --- | --- |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Active current-risk focused accounting | `1179/1179 = 100.00%` |
| Remaining active focused work | `0` |
| Latest verified Ghidra backup | `latestGhidraBackupClass=verified-static-backup-redacted` |

Contract status tokens:

- `crosswalkStatus=world-thing-spawn-static-to-rebuild-contract-crosswalk-complete-static-contract-not-runtime-proof`
- `worldThingSpawnStaticToRebuildContractCrosswalkStatus=world-thing-spawn-static-to-rebuild-contract-crosswalk-complete-static-contract-not-runtime-proof`
- `selectedSourceProofCount=3`
- `sourceSchemaCount=3`
- `contractSectionCount=9`
- `contractFalseGuardCount=35`
- `contractZeroCounterCount=16`
- `publicLeakCheck=PASS`
- `selectedNextSlice=MissionScript Command-Effect Rebuild Interface Rollup Proof Plan`

Source proof inputs:

| Source proof | Contract input |
| --- | --- |
| World / Thing / Spawn Copied-Corpus Schema Proof | `574` raw `GetThingRef` rows, `70` raw `SpawnThing` rows, `644` total raw rows, `436` unique object-reference rows, `447` spawn-preserving rows, selected `training-target-spawn-family`, and selected `training-target-zone-getthingref-family`. |
| World / Thing / Spawn Spawner Handoff Static Proof | `8` handoff layers, `12` static field roles, `DAT_008553f4`, `0x0050f970 CWorldPhysicsManager__CreateSpawner`, `0x004e3c60 CSpawnerThng__DoSpawn`, `CUnit__VFunc08_InitAndAddToWorld`, and `0x004fc3a0 CUnit__SetSpawnCooldownState3`. |
| World / Thing / Spawn GetThingRef Object-Reference Static Proof | `9` selected raw `GetThingRef` rows, `8` selected unique object-reference rows, `1` duplicate call row, `9` empty-spawner rows, and `4` static linkage layers for `training-target-zone-getthingref-family`. |

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

What this proves:

- The selected World / Thing / Spawn static proof set has one rebuild-facing contract vocabulary for corpus rows, command descriptors, bytecode preload, world load/factory/init, spawner gates, static field roles, Unit world-add/cooldown, object-reference labels, and render/resource boundaries.
- The public-safe contract preserves source proof counts: `574`, `70`, `644`, `436`, `447`, `34`, `9`, `8`, `1`, `9`, `8`, `12`, and `4`.
- No private frame details, installed-game paths, user-profile paths, raw screenshots, executable patches, or operator-only evidence are published by this crosswalk.

What remains unproven:

- Runtime object identity.
- Runtime `SpawnThing`.
- Runtime `GetThingRef`.
- Runtime MissionScript execution.
- Runtime world loading.
- Runtime spawner behavior.
- Runtime Unit/BattleEngine spawn behavior.
- Live loose-MSL loading.
- Packed-resource script selection.
- Exact layouts.
- Source-body identity.
- BEA patching behavior.
- Visual QA.
- Godot parity.
- Rebuild implementation.
- Rebuild parity.
- No-noticeable-difference parity.

Next selected static child lane: `MissionScript Command-Effect Rebuild Interface Rollup Proof Plan`.
