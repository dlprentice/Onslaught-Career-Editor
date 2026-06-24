# MissionScript Message/Audio Command-Effect Fixture Proof Plan Readiness

Status: complete static message/audio/console effect table, not runtime proof
Date: 2026-06-09
Scope: `missionscript-message-audio-command-effect-fixture`

Artifacts:

- `reverse-engineering/binary-analysis/missionscript-message-audio-command-effect-fixture-proof-plan.md`
- `reverse-engineering/binary-analysis/missionscript-message-audio-command-effect-fixture-proof-plan.v1.json`
- `tools/missionscript_message_audio_command_effect_fixture_proof_plan_probe.py`

Key tokens:

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

Static anchors:

| Surface | Evidence |
| --- | --- |
| Queue handlers | `0x00537410 IScript__PlaySound`, `0x00537500 IScript__PlaySoundWithCallback`, `0x005375f0 IScript__PlaySoundWithFade`, `0x005377e0 IScript__PlaySoundWithPriority`, and `0x005378e0 IScript__PlaySoundWithFadeAndPriority`. |
| Console text | `0x00537c40 IScript__PrintText`, `CText__GetStringById`, and `CConsole__Printf`. |
| Queue context | `DAT_008a9d84`, `CMessage__ctor_base`, `CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance`, `CMessageBox__StartVoiceOrFallbackTextReveal`, `CMessageBox__AdvanceRevealAndScheduleNextTick`, `CMessageBox__StopVoicePlaybackIfNotInCutscene`, and `CMessageBox__RenderOverlay`. |
| Corpus | `67` message levels, `1365` PlayCharMessage rows, `7` AddHelpMessage rows, `110` LevelLost-family rows, `71` LevelWon-family rows, `1553` detailed rows, `11` speakers, and `499` unique message tokens. |

Fixture matrix:

- Five message queue construction fixture rows.
- One console text fixture row.
- Twelve descriptor context rows.

What this proves:

- Static message queue fixture planning for five saved Wave584 queue handlers.
- Static console text fixture planning for `IScript__PrintText`.
- Static descriptor and message corpus context for clean-room message/audio planning.

What remains unproven:

- Runtime MissionScript execution.
- Runtime command effects.
- Runtime message display, voice/audio playback, HUD output, queue ordering, console output, text lookup, speaker routing, or subtitle timing.
- Live loose-MSL loading, packed-resource script selection, exact descriptor/arity/type/layout details, source-selection observation, private-frame review, visual QA, Godot parity, Ghidra mutation, executable patching, product UI behavior, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
