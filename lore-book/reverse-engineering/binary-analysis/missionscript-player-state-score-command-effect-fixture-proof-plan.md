# MissionScript Player-State / Score Command-Effect Fixture Proof Plan

Status: complete static player-state/score context table, not runtime proof
Last updated: 2026-06-09
Scope: `missionscript-player-state-score-command-effect-fixture`

This proof completes the Player-State / Score child lane selected after the [MissionScript Thing Value / Engine Helper Command-Effect Fixture Proof Plan](missionscript-thing-value-engine-helper-command-effect-fixture-proof-plan.md). It converts the completed Player-State / Score static command-effect map into a finite static context fixture table for clean-room planning without launching BEA, publishing private loose-MSL rows, reading private baselines, writing copied files, mutating Ghidra, starting Godot work, wiring product UI, or implementing a rebuild. The selected follow-up is the MissionScript Command-Effect Fixture Family Completion Rollup Proof Plan.

Machine-checkable artifact:

- [missionscript-player-state-score-command-effect-fixture-proof-plan.v1.json](missionscript-player-state-score-command-effect-fixture-proof-plan.v1.json)

Proof tokens:

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

## Static Authority

| Surface | Evidence |
| --- | --- |
| Descriptor context | Three descriptor rows: `84 AddScore` at `0x0064e350`, `136 ToggleCockpit` at `0x0064f050`, and `137 SetStealth` at `0x0064f090`. |
| Raw entries | `AddScore` raw entry remains `IScript__Unk_00534410`; `ToggleCockpit` raw entry remains `&LAB_00533950`; `SetStealth` raw entry remains `&LAB_00533980`. |
| Alias boundary | `AddScore` is explicitly preserved as an alias-boundary/context case because `0x00534410 IScript__SecondaryObjectiveComplete` is current objective/outcome evidence. This proof does not bind `AddScore` to score mutation or `CGame::IncScore`. |
| Source context | `CGame::IncScore`, `CBattleEngine::ToggleCockpit`, `CBattleEngine__HandleCloak`, `mStealth`, and `mDesiredStealth` are retained only as source/static planning context. |
| Loose corpus context | Aggregate static command-token counts are `15` `AddScore`, `0` `ToggleCockpit`, and `10` `SetStealth`, across aggregate file counts `12 / 0 / 4`. Raw source rows are not published in this fixture. |
| Original fixture ranking | The historical first-fixture selection ranked `player-state-score` at `9` with decision `deferred`; this fixture preserves that as original selection context, not as current deferral. |

## Fixture Matrix

The focused probe recomputes three finite static context cases from the static schema:

| Command | Descriptor | Static fixture model | Boundary |
| --- | ---: | --- | --- |
| `AddScore` | `84` | Descriptor/name/corpus alias-boundary case tied to `IScript__Unk_00534410`, aggregate `15` command-token rows, `12` aggregate files, and the `0x00534410 IScript__SecondaryObjectiveComplete` conflict. | Static context only; no handler-body proof and no runtime score behavior. |
| `ToggleCockpit` | `136` | Raw descriptor/source-context case tied to `&LAB_00533950`, `0` aggregate command-token rows, and `CBattleEngine::ToggleCockpit` source context. | Static context only; no handler-body proof and no runtime cockpit behavior. |
| `SetStealth` | `137` | Raw descriptor/corpus/source-context case tied to `&LAB_00533980`, aggregate `10` command-token rows, `4` aggregate files, `CBattleEngine__HandleCloak`, `mStealth`, and `mDesiredStealth`. | Static context only; no handler-body proof, runtime stealth behavior, or weapon-fire/stealth interaction. |

The fixture intentionally models descriptor/corpus/source-context coverage rather than handler dispatch. `deterministicFixtureCaseCount=3` means the static context rows are finite and machine-checkable; it does not mean any runtime effect is deterministic or proven.

## Claim Boundary

This proves a static Player-State / Score fixture table for three descriptor context cases, one `AddScore` alias-boundary case, two raw-label/source-context cases, aggregate command-token counts, and the preserved first-fixture rank/deferral context.

It does not prove runtime MissionScript execution, runtime command effects, runtime score behavior, runtime cockpit behavior, runtime stealth behavior, weapon-fire/stealth interaction, runtime ranking/career/save behavior, `AddScore` handler-body proof, `ToggleCockpit` handler-body proof, `SetStealth` handler-body proof, live loose-MSL loading, packed-resource script selection, exact command descriptor layout, exact command arity, exact argument type schema, exact datatype layout, exact player-state layout, source-selection observation, private-frame review, visual QA, Godot parity, Ghidra mutation, executable patching, product UI behavior, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
