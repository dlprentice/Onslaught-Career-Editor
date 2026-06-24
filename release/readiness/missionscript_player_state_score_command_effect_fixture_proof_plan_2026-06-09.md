# MissionScript Player-State / Score Command-Effect Fixture Proof Plan Readiness Note

Status: complete static player-state/score context table, not runtime proof
Date: 2026-06-09
Scope: `missionscript-player-state-score-command-effect-fixture`

This readiness note covers the public-safe static fixture plan for the MissionScript Player-State / Score command-effect family. It is documentation/schema/probe work only: no BEA launch, no Ghidra mutation, no executable patching, no copied-file mutation, no private-frame review, no Godot work, no product UI wiring, and no rebuild implementation.

Machine-checkable artifacts:

- `reverse-engineering/binary-analysis/missionscript-player-state-score-command-effect-fixture-proof-plan.md`
- `reverse-engineering/binary-analysis/missionscript-player-state-score-command-effect-fixture-proof-plan.v1.json`
- `tools/missionscript_player_state_score_command_effect_fixture_proof_plan_probe.py`

Required proof tokens:

- `missionScriptPlayerStateScoreCommandEffectFixtureProofPlanStatus=missionscript-player-state-score-command-effect-fixture-proof-plan-complete-static-player-state-score-context-table-not-runtime-proof`
- `previousSlice=MissionScript Thing Value / Engine Helper Command-Effect Fixture Proof Plan`
- `selectedNextSlice=MissionScript Command-Effect Fixture Family Completion Rollup Proof Plan`
- `selectedFixtureFamily=player-state-score`
- `selectedFixturePath=player-state-score-descriptor-alias-boundary-table`
- `descriptorIndices=84/136/137`
- `descriptorRecordCount=3`
- `descriptorContextCaseCount=3`
- `staticContextFixtureCaseCount=3`
- `deterministicFixtureCaseCount=3`
- `aliasBoundaryCaseCount=1`
- `rawLabelOnlyCaseCount=2`
- `sourceContextFamilyCount=3`
- `handlerBodyProvenCount=0`
- `deterministicRuntimeEffectCaseCount=0`
- `totalStaticCommandStepCount=3`
- `effectAssertionCount=9`
- `directNonCommentLooseMslRows=25`
- `directNonCommentLooseMslFiles=16`
- `commandWithCorpusRows=2`
- `zeroCorpusCommandCount=1`
- `addScoreCallRows=15`
- `toggleCockpitCallRows=0`
- `setStealthCallRows=10`
- `addScoreFileRows=12`
- `toggleCockpitFileRows=0`
- `setStealthFileRows=4`
- `fixtureSelectionOriginalRank=9`
- `falseGuardCount=53`
- `zeroCounterCount=39`
- `publicLeakCheck=PASS`
- `latestGhidraBackupClass=verified-static-backup-redacted`

Static anchors:

- `AddScore` descriptor row `84`, record `0x0064e350`, raw entry `IScript__Unk_00534410`.
- `ToggleCockpit` descriptor row `136`, record `0x0064f050`, raw entry `&LAB_00533950`.
- `SetStealth` descriptor row `137`, record `0x0064f090`, raw entry `&LAB_00533980`.
- `AddScore` remains an alias-boundary/context row because `0x00534410 IScript__SecondaryObjectiveComplete` is current objective/outcome evidence.
- `CGame::IncScore`, `CBattleEngine::ToggleCockpit`, `CBattleEngine__HandleCloak`, `mStealth`, and `mDesiredStealth` are context anchors only.

Guard tokens:

- `runtimeExecution=false`
- `beLaunch=false`
- `sourcePathsPublic=false`
- `rawMslRowsPublic=false`
- `liveLooseMslLoading=false`
- `packedResourceScriptSelectionProven=false`
- `ghidraMutation=false`
- `godotWork=false`
- `rebuildImplementation=false`
- `runtimeObservationRows=0`
- `missionScriptRuntimeEvidenceRows=0`
- `runtimeCommandEffectRows=0`
- `runtimePlayerStateScoreRows=0`
- `beProcessesAfterFixture=0`

Claim boundary:

This readiness note proves only a public-safe static fixture table for three descriptor context rows, aggregate command-token counts, one alias-boundary case, two raw-label/source-context cases, and a next-slice handoff to the fixture-family completion rollup. Runtime MissionScript execution, runtime command effects, runtime score/cockpit/stealth behavior, weapon-fire/stealth interaction, handler-body proof, live script loading, packed-resource selection, exact layouts, visual QA, Godot parity, Ghidra mutation, executable patching, product UI behavior, rebuild implementation, rebuild parity, and no-noticeable-difference parity remain separate proof.
