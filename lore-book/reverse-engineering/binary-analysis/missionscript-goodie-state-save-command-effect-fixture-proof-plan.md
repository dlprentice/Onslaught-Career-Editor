# MissionScript Goodie State / Save Command-Effect Fixture Proof Plan

Status: complete static offset/state fixture plan, not runtime proof
Date: 2026-06-09

This slice completes `MissionScript Goodie State / Save Command-Effect Fixture Proof Plan` after `MissionScript Vector/Range Command-Effect Deterministic Helper Fixture Proof Plan`. It selects `MissionScript Goodie State / Save Copied-Baseline Byte-Diff Fixture Proof Plan` as the next child lane.

Machine-readable schema: [missionscript-goodie-state-save-command-effect-fixture-proof-plan.v1.json](missionscript-goodie-state-save-command-effect-fixture-proof-plan.v1.json).

`missionScriptGoodieStateSaveCommandEffectFixtureProofPlanStatus=missionscript-goodie-state-save-command-effect-fixture-proof-plan-complete-static-offset-state-fixture-plan-not-runtime-proof`

## Accounting

Static context remains `6411/6411 = 100.00%`, `0 / 0 / 0`, `1560/1560 = 100.00%`, and `1179/1179 = 100.00%`; `latestGhidraBackupClass=verified-static-backup-redacted`.

Plan tokens: `selectedFixtureFamily=goodie-state-save`; `selectedFixturePath=goodie-state-save-index-state-byte-preservation`; `selectedNextSlice=MissionScript Goodie State / Save Copied-Baseline Byte-Diff Fixture Proof Plan`; `sourceProofCount=6`; `fixtureFamilyCount=5`; `plannedGoodieFixtureCaseCount=43`; `descriptorBoundaryCaseCount=5`; `scriptIndexOffsetCaseCount=12`; `stateValueCaseCount=4`; `corpusBoundaryCaseCount=9`; `appCoreCopiedSaveSafetyCaseCount=13`.

Static evidence tokens: `descriptorRecordCount=3`; `uniqueDescriptorIndexCount=3`; `descriptorIndices=84/118/119`; `handlerReadbackCount=2`; `handlerAnchorCount=2`; `wave579MetadataRows=6`; `wave579TagRows=6`; `wave579XrefRows=6`; `wave579InstructionRows=1326`; `wave579DecompileRows=6`; `wave579VtableRows=24`; `goodieStorageEntryCount=300`; `displayableGoodieCount=233`; `reservedPreserveEntryCount=67`; `trueViewGoodieBase=0x1F46`; `knownScriptGoodieCallIndexCount=6`; `looseGoodieStateCallCount=32`; `zeroTargetScriptIndexCount=3`; `addScoreCorpusCallCount=15`; `copiedFileProofExpectedSize=10004`; `copiedFileProofVersionWord=0x4BD1`; `falseGuardCount=41`; `zeroCounterCount=31`; `publicLeakCheck=PASS`.

## Descriptor And Handler Boundary

The descriptor/handler fixture family records five boundary cases:

| Case | Static evidence |
| --- | --- |
| `SetGoodieState` descriptor | Descriptor index `118`, record `0x0064ebd0`, static command token `SetGoodieState`. |
| `GetGoodieState` descriptor | Descriptor index `119`, record `0x0064ec10`, static command token `GetGoodieState`. |
| `AddScore` alias boundary | Descriptor index `84`, record `0x0064e350`, preserved as descriptor/name context only because `0x00534410 IScript__SecondaryObjectiveComplete` remains an alias-boundary conflict. |
| `SetGoodieState` handler | `0x00533a70 IScript__SetGoodieState` writes `g_Career_mGoodies[index-1]`. |
| `GetGoodieState` handler | `0x00533aa0 IScript__GetGoodieState` reads `g_Career_mGoodies[index-1]` and returns an integer result object. |

The save bridge anchor is `0x00662564` for `g_Career_mGoodies`.

## Offset Fixture Matrix

The clean-room fixture plan uses `save_file_offset = 0x1F46 + (script_index - 1) * 4`.

| Script index | Boundary |
| ---: | --- |
| script index `1 -> 0x1F46` | first displayable Goodie |
| script index `51 -> 0x200E` | known script-call displayable Goodie |
| script index `53 -> 0x2016` | known script-call displayable Goodie |
| script index `68 -> 0x2052` | known race Goodie call |
| script index `71 -> 0x205E` | known race Goodie call |
| script index `233 -> 0x22E6` | last displayable Goodie |
| script index `234 -> 0x22EA` | first reserved/preserve Goodie |
| script index `300 -> 0x23F2` | last reserved/preserve Goodie |
| script index `301 -> 0x23F6` | clean-room fixture rejects; this would overlap the kill-counter base if not rejected |
| script index `0 -> 0x1F42` | clean-room fixture rejects; this underflows before the Goodie array |

State vocabulary: `GS_UNKNOWN`, `GS_INSTRUCTIONS`, `GS_NEW`, and `GS_OLD`.

Corpus boundary: existing Goodies docs record 32 loose Goodie-state calls using script indices `51`, `53`, and `68..71`, plus zero calls for `72..74`. This fixture plan uses those rows as static corpus guards only.

## Next Byte-Diff Gate

The next selected lane must use copied real baselines, not synthesized authority buffers. The byte-diff fixture must preserve file size `10004`, version `0x4BD1`, copy-before-write, source/output path separation, unchanged source baselines, unchanged reserved Goodies unless a later explicit slice arms them, and no public source paths, hashes, or raw save bytes.

AppCore safety cases for the next lane: copied `.bes` validation, copied defaultoptions validation, no-op preservation, 300-row Goodie analysis, single and multi true-view Goodie writes, displayable boundary `232`, reserved `233..299` preservation, reserved write rejection, invalid state rejection, wrong-size rejection, wrong-version rejection, and in-place write rejection.

## Guards

False guards: `runtimeExecution=false`; `runtimeGoodieStateMutationProven=false`; `runtimeSaveBehaviorProven=false`; `runtimeGoodiesWallBehaviorProven=false`; `runtimeScoreBehaviorProven=false`; `addScoreHandlerBodyProven=false`; `sourceBaselineRead=false`; `copiedFileMutation=false`; `ghidraMutation=false`; `godotWork=false`; `productUiWired=false`; `rebuildImplementation=false`.

Zero counters: `runtimeObservationRows=0`; `missionScriptRuntimeEvidenceRows=0`; `runtimeCommandEffectRows=0`; `runtimeGoodieStateRows=0`; `runtimeSaveRows=0`; `runtimeGoodiesWallRows=0`; `runtimeScoreRows=0`; `beProcessesAfterFixture=0`.

## Claim Boundary

This proves a public-safe static/codec fixture plan for Goodie command descriptors, handler anchors, one-based script-index to true-view save-offset mapping, state enum values, corpus presence/absence guards, and copied-save AppCore safety gates.

This does not prove runtime MissionScript execution, runtime command effects, runtime Goodie state mutation, runtime save/defaultoptions behavior, runtime Goodies wall behavior, runtime score behavior, `AddScore` handler semantics, hidden-Goodies reachability or unreachability, exact descriptor layout, exact command arity, exact argument type schema, exact `CCareer` layout, source-selection observation, private-frame review, visual QA, Godot parity, Ghidra mutation, executable patching, product UI behavior, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
