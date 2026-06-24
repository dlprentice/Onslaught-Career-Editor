# MissionScript Goodie State / Save Command-Effect Fixture Proof Plan Readiness

Status: complete static offset/state fixture plan, not runtime proof
Date: 2026-06-09

This readiness note records `MissionScript Goodie State / Save Command-Effect Fixture Proof Plan`, following `MissionScript Vector/Range Command-Effect Deterministic Helper Fixture Proof Plan`, and selects `MissionScript Goodie State / Save Copied-Baseline Byte-Diff Fixture Proof Plan` as the next child lane.

Schema: `missionscript-goodie-state-save-command-effect-fixture-proof-plan.v1.json`.

`missionScriptGoodieStateSaveCommandEffectFixtureProofPlanStatus=missionscript-goodie-state-save-command-effect-fixture-proof-plan-complete-static-offset-state-fixture-plan-not-runtime-proof`

Evidence accounting: `selectedFixtureFamily=goodie-state-save`; `selectedFixturePath=goodie-state-save-index-state-byte-preservation`; `selectedNextSlice=MissionScript Goodie State / Save Copied-Baseline Byte-Diff Fixture Proof Plan`; `sourceProofCount=6`; `fixtureFamilyCount=5`; `plannedGoodieFixtureCaseCount=43`; `descriptorBoundaryCaseCount=5`; `scriptIndexOffsetCaseCount=12`; `stateValueCaseCount=4`; `corpusBoundaryCaseCount=9`; `appCoreCopiedSaveSafetyCaseCount=13`; `descriptorRecordCount=3`; `uniqueDescriptorIndexCount=3`; `descriptorIndices=84/118/119`; `handlerReadbackCount=2`; `handlerAnchorCount=2`; `wave579MetadataRows=6`; `wave579TagRows=6`; `wave579XrefRows=6`; `wave579InstructionRows=1326`; `wave579DecompileRows=6`; `wave579VtableRows=24`; `goodieStorageEntryCount=300`; `displayableGoodieCount=233`; `reservedPreserveEntryCount=67`; `trueViewGoodieBase=0x1F46`; `knownScriptGoodieCallIndexCount=6`; `looseGoodieStateCallCount=32`; `zeroTargetScriptIndexCount=3`; `addScoreCorpusCallCount=15`; `copiedFileProofExpectedSize=10004`; `copiedFileProofVersionWord=0x4BD1`; `falseGuardCount=41`; `zeroCounterCount=31`; `publicLeakCheck=PASS`; `latestGhidraBackupClass=verified-static-backup-redacted`.

Anchors: `0x00533a70 IScript__SetGoodieState`; `0x00533aa0 IScript__GetGoodieState`; `0x00662564`; `0x0064e350`; `0x0064ebd0`; `0x0064ec10`; `0x00534410 IScript__SecondaryObjectiveComplete`.

Offset fixtures: script index `1 -> 0x1F46`; script index `51 -> 0x200E`; script index `53 -> 0x2016`; script index `68 -> 0x2052`; script index `71 -> 0x205E`; script index `233 -> 0x22E6`; script index `234 -> 0x22EA`; script index `300 -> 0x23F2`; script index `301 -> 0x23F6`; script index `0 -> 0x1F42`. State vocabulary: `GS_UNKNOWN`, `GS_INSTRUCTIONS`, `GS_NEW`, `GS_OLD`.

Guard tokens: `runtimeExecution=false`; `runtimeGoodieStateMutationProven=false`; `runtimeSaveBehaviorProven=false`; `runtimeGoodiesWallBehaviorProven=false`; `runtimeScoreBehaviorProven=false`; `addScoreHandlerBodyProven=false`; `sourceBaselineRead=false`; `copiedFileMutation=false`; `ghidraMutation=false`; `godotWork=false`; `productUiWired=false`; `rebuildImplementation=false`; `runtimeObservationRows=0`; `missionScriptRuntimeEvidenceRows=0`; `runtimeCommandEffectRows=0`; `runtimeGoodieStateRows=0`; `runtimeSaveRows=0`; `runtimeGoodiesWallRows=0`; `runtimeScoreRows=0`; `beProcessesAfterFixture=0`.

This readiness note proves only the public-safe static/codec fixture plan for Goodie command descriptors, handler anchors, index-to-save-offset mapping, state values, corpus guards, and copied-save safety gates. It does not prove runtime MissionScript execution, runtime command effects, runtime Goodie state mutation, runtime save/defaultoptions behavior, runtime Goodies wall behavior, runtime score behavior, `AddScore` handler semantics, hidden-Goodies reachability or unreachability, exact descriptor layout, exact command arity, exact argument type schema, exact `CCareer` layout, private-frame review, visual QA, Godot parity, Ghidra mutation, executable patching, product UI behavior, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
