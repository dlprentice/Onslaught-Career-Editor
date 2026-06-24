# MissionScript Message/Audio Command-Effect Fixture Proof Plan

Status: complete static message/audio/console effect table, not runtime proof
Last updated: 2026-06-09
Scope: `missionscript-message-audio-command-effect-fixture`

This proof completes the message/audio child lane selected after the [MissionScript Objective/Outcome Command-Effect Fixture Proof Plan](missionscript-objective-outcome-command-effect-fixture-proof-plan.md). It converts the completed message/audio static command-effect map into a finite fixture table for clean-room planning without launching BEA, reading private baselines, writing copied files, mutating Ghidra, starting Godot work, wiring product UI, or implementing a rebuild. The selected follow-up is the MissionScript HUD / Display Command-Effect Fixture Proof Plan.

Machine-checkable artifact:

- [missionscript-message-audio-command-effect-fixture-proof-plan.v1.json](missionscript-message-audio-command-effect-fixture-proof-plan.v1.json)

Proof tokens:

- `missionScriptMessageAudioCommandEffectFixtureProofPlanStatus=missionscript-message-audio-command-effect-fixture-proof-plan-complete-static-message-audio-console-effect-table-not-runtime-proof`
- `previousSlice=MissionScript Objective/Outcome Command-Effect Fixture Proof Plan`
- `selectedNextSlice=MissionScript HUD / Display Command-Effect Fixture Proof Plan`
- `selectedFixtureFamily=message-audio-console`
- `selectedFixturePath=message-audio-queue-console-effect-table`
- `descriptorIndices=9/15/16/27/33/34/35/89/90/111/112/117`
- `descriptorRecordCount=12`
- `descriptorContextCaseCount=12`
- `messageQueueHandlerCount=5`
- `consoleTextHandlerCount=1`
- `messageBoxContextCount=6`
- `handlerAnchorCount=6`
- `plannedMessageQueueCaseCount=5`
- `plannedConsoleTextCaseCount=1`
- `deterministicFixtureCaseCount=6`
- `textIdSeedCount=9`
- `floatSeedCount=5`
- `prioritySeedCount=2`
- `fadeEventCaseCount=2`
- `callbackContextCaseCount=1`
- `effectAssertionCount=17`
- `wave584MetadataRows=11`
- `wave1015MetadataRows=7`
- `wave1074MetadataRows=1`
- `messageCorpusLevelRows=67`
- `messageCorpusPlayCharMessage=1365`
- `messageCorpusAddHelpMessage=7`
- `messageCorpusLevelLostFamily=110`
- `messageCorpusLevelWonFamily=71`
- `messageCallsiteDetailedRows=1553`
- `messageCallsiteSpeakerCount=11`
- `messageCallsiteUniqueTokenCount=499`
- `falseGuardCount=48`
- `zeroCounterCount=38`
- `publicLeakCheck=PASS`
- `latestGhidraBackupClass=verified-static-backup-redacted`

Guard tokens:

- `runtimeExecution=false`
- `beLaunch=false`
- `sourceBaselineRead=false`
- `privateArtifactMaterialized=false`
- `copiedFileMutation=false`
- `ghidraMutation=false`
- `godotWork=false`
- `rebuildImplementation=false`
- `runtimeObservationRows=0`
- `missionScriptRuntimeEvidenceRows=0`
- `runtimeCommandEffectRows=0`
- `runtimeMessageRows=0`
- `runtimeAudioRows=0`
- `beProcessesAfterFixture=0`

## Static Authority

| Surface | Evidence |
| --- | --- |
| Descriptor context | Twelve message/audio/HUD-adjacent descriptor rows: `PlaySample`, `PrintText`, `AddMessage`, `PlayCharMessage`, `HighlightHudPart`, `UnHighlightHudPart`, `PlayCharMessageWait`, `PlayPCharMessage`, `PlayPCharMessageWait`, `SwitchMessagesOn`, `SwitchMessagesOff`, and `AddHelpMessage`. These rows preserve descriptor names, record addresses, and raw entries as context only. |
| Queue handlers | `0x00537410 IScript__PlaySound`, `0x00537500 IScript__PlaySoundWithCallback`, `0x005375f0 IScript__PlaySoundWithFade`, `0x005377e0 IScript__PlaySoundWithPriority`, and `0x005378e0 IScript__PlaySoundWithFadeAndPriority` provide static queue-construction anchors. |
| Console text handler | `0x00537c40 IScript__PrintText` provides the static `CText__GetStringById` to `CConsole__Printf` wide-string sink boundary. |
| Queue context | `DAT_008a9d84`, `CMessage__ctor_base`, `CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance`, `CMessageBox__StartVoiceOrFallbackTextReveal`, `CMessageBox__AdvanceRevealAndScheduleNextTick`, `CMessageBox__StopVoicePlaybackIfNotInCutscene`, and `CMessageBox__RenderOverlay` are retained as static queue/lifecycle context. |
| Corpus context | Public-safe message corpus accounting preserves `67` level rows, `1365` `PlayCharMessage`, `7` `AddHelpMessage`, `110` LevelLost-family rows, `71` LevelWon-family rows, `1553` detailed message rows, `11` speakers, and `499` unique message tokens. |

## Fixture Matrix

The focused probe recomputes six finite fixture cases from the static schema:

| Case | Static effect |
| --- | --- |
| `PlaySound-text-100-duration-1250ms` | One text id and one finite duration seed map to static `CMessage` construction and `CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance`. |
| `PlaySoundWithCallback-text-101-102-duration-2000ms` | Two text ids, one finite duration seed, and active-reader callback context map to the static queue handoff. |
| `PlaySoundWithFade-text-103-duration-3000ms` | One text id, one finite duration seed, and fade event `0x7d1` context map to the static queue handoff. |
| `PlaySoundWithPriority-text-104-105-duration-4000ms-priority-7` | Two text ids, one finite duration seed, and priority seed `7` map to the static queue handoff. |
| `PlaySoundWithFadeAndPriority-text-106-107-duration-5000ms-priority-8` | Two text ids, one finite duration seed, fade event `0x7d1`, and priority seed `8` map to the static queue handoff. |
| `PrintText-text-300-console-wide-string` | Text id seed `300` maps to the static `CText__GetStringById` and `CConsole__Printf("%w")` skeleton. |

The twelve descriptor rows are context cases, not runtime command cases. `HighlightHudPart`, `UnHighlightHudPart`, `SwitchMessagesOn`, `SwitchMessagesOff`, `PlayCharMessage*`, `PlayPCharMessage*`, `PlaySample`, `AddMessage`, and `AddHelpMessage` remain descriptor/corpus context here unless a later proof selects narrower handler-body evidence.

## Claim Boundary

This proves a static message/audio/console fixture table for five message queue construction cases, one console text case, and twelve descriptor context rows, tied to saved descriptor slots, saved handler anchors, MessageBox lifecycle context, and public-safe corpus counts.

It does not prove runtime MissionScript execution, runtime command effects, runtime message display, runtime voice playback, runtime audio playback, runtime HUD output, runtime queue ordering, runtime console output, runtime text lookup, runtime speaker routing, runtime subtitle timing, live loose-MSL loading, packed-resource script selection, exact command descriptor layout, exact command arity, exact argument type schema, exact `CMessage` layout, exact `CMessageBox` layout, exact text catalog layout, exact audio resource mapping, message queue capacity, message priority ordering, source-selection observation, private-frame review, visual QA, Godot parity, Ghidra mutation, executable patching, product UI behavior, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
