# Level 100 mission-completion test truthfulness audit

Status: historical audit of base `04cdd9c3`. Its completion-causality grades
and test census remain a record of that base; the 2026-08-27 debriefing landing
supersedes its N1 mechanics and direct-LevelSelect/current-capability claims.
Date: 2026-08-24 (rev E, current-main census 16/46)

2026-08-27 outcome: Client now applies the Career update, consumes the two
Goodie latches, projects the measured mission-status/objective/grade fields,
and lands on a settled Godot `FEP_DEBRIEFING` page before acknowledgement
returns to Level Select. This closes the direct-LevelSelect substitution only.
Outro FMV, a live score/time snapshot join, entry/exit interpolation,
Goodie particle/message effects, grade glint, native host-hop automation, and
retail-frame pixel validation remain open.

Verdict: the completion chain's field-law core (countdowns, FillOut snapshot,
career handoff, loss paths, negative controls) is TRUTHFUL against pristine
anchors, while every scripted-Won completion-causality test is PARTIAL
(QueueExternalEvent injection or an omniscient stand-in driver), the full
chain's trajectory pins are SYNTHETIC_ONLY self-pins, and the post-Won human
experience (debriefing page, outro FMV) plus the Godot host handoff hop remain
untested — three material corrections (N1/N2/N3) nominated in §5.
Evidence: SOURCE — every retail claim in §1 is quoted from retained tracked
authorities (pinned GPL `game.cpp`/`Career.cpp`/`EndLevelData`, pristine
function notes and contracts with VAs and body SHAs listed in §1.1); §2's
inventory counts were recomputed 2026-08-24 (rev E) by an anchored static
census over the fetched current-main (`04cdd9c3`) test sources; no new
measurement was taken (§6).
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes,
SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
all byte-level retail claims in this report are read from that specimen or
from tracked pristine contract/function notes pinned to it.
Question: do the current Level 100 / mission-completion tests assert what a
human player would call "finished the level," or only narrower synthetic
invariants?
Scope boundary: this report changes no behavior, launches no binary, executes
no ROM, and writes nothing outside this worktree. Worktree base is fetched
current main `04cdd9c31c03f581c55e67a45fa1f3a283f3f3c6` (`git merge-tree`
clean against then-current `origin/main` is required again at publication).

Execution boundary: every Won-bearing test inventoried here runs a managed
Core/Client/headless simulation, either with `QueueExternalEvent` facts or an
omniscient input driver. Those are synthetic or machine-path completion
checks, not a native Godot human-play completion. This report neither ran nor
claims a native human playthrough, and it never upgrades a synthetic Won into
one.

Current-source boundary: fetched origin/main is
`04cdd9c31c03f581c55e67a45fa1f3a283f3f3c6` (tree
`f750ce4f15dab659ea16006e95da9eac4f83d603`). Main still includes reviewed
reticle-to-emitter merge `608d93bd759620d53ca22fe603d025cd623aa2b2` (candidate
`10f21fb3a9411a654c0f2a9c21f761ec2cfb5394`), which changed the managed
full-chain self-pins to tick 6992 / hull 10900 and added two anchored
`SimulationTests` declarations (then-current file total 44). Later reviewed
current-main additions bring the live census to `Level100MissionTests` **16**
`[Fact]` methods and `SimulationTests` **46** public methods (42 Facts + 4
Theories):
`SecondaryObjectiveComplete_WritesOnlyTheIndexedRetailSlotAndRejectsSwappedOrOutOfRangeArguments`,
`SecondaryObjectiveFailed_WritesTheIndexedRetailSlotAndRejectsSwappedOrOutOfRangeArguments`,
`World110Session_CrossesNative88AndStepsDeterministically`, and
`CanonicalHash_PreservesWorld100SchemaAndBindsWorld110SecondaryState`.
Managed/Core/headless GREEN is not a native Godot human playthrough, and this
report does not claim native-88 `SecondaryObjectiveFailed` capability.

---

## 1. Retail Level 100 completion law (source-first)

### 1.1 Authorities consumed

| Authority | Owner | What it fixes |
| --- | --- | --- |
| Pinned GPL `references/Onslaught/game.cpp` | `CGame::DeclareLevelWon` 2384–2412, `MainLoop` countdown 1997–2035, `FillOutEndLevelData` 910–1043, `DeclareLevelLost` 2466–2501, `DeclarePlayerDead` 2503–2555, outro-FMV Won gate/lookup/selection 1166–1190 and playback arm 1191–1214 (`FMV.PlayFullscreen` line 1213) | architecture and intent |
| Pinned GPL `references/Onslaught/EndLevelData.h/.cpp` | `CEndLevelData` layout, `IsAllSecondaryObjectivesComplete` | the handoff structure |
| Pinned GPL `references/Onslaught/Career.cpp` | `CCareer::Update` 379–418, `ReCalcLinks` 423–515, `UpdateThingsKilled` 539–541, `UpdateGoodieStates` | career consumption |
| Pristine static contract | `reverse-engineering/contracts/engine-world/CGame__DeclareLevelWon__0046f2f0.md` | body `[0x0046f2f0,0x0046f35b]`, raw-body SHA `2bf6c8ff…a46f6`; sole caller `IScript__LevelWon 0x005381e0` |
| Pristine function note | `reverse-engineering/binary-analysis/functions/game.cpp/CGame__FillOutEndLevelData.md` | `0x0046d470`, 920-byte body SHA `2cd8ee26…8fd2`, every destination global |
| Pristine function note | `…/functions/game.cpp/CGame__RestartLoopRunLevel.md` (2026-08-22 re-read) | exit tail order: KillAllSamples → **FillOutEndLevelData** → teardown; in-loop timeout law |
| Pristine function note | `…/functions/Career.cpp/CCareer__Update.md` | "mission finished" entry point, wave1049 re-audit |
| Pristine function note | `…/functions/EndLevelData.cpp/CEndLevelData__IsAllSecondaryObjectivesComplete.md` | predicate `0x004496e0`, callers |
| Function notes | `…/functions/game.cpp/CGame__DeclareLevelLost.md`, `con_win.md`, `CGame__RollCredits.md` | loss path, console win, credits |
| Lifecycle receipt | `…/cgame-level-lifecycle-semantics-2026-08-11.md` + `.tsv` | six-function lifecycle, `Shutdown` fills END_LEVEL_DATA before teardown |
| Mission-script registry | `…/mission-script-command-registry-2026-08-12.tsv` | native command identities |
| Native corpus census | `…/mission-native-corpus-coverage-2026-08-15.tsv` | which handlers retained traces ever executed |
| Compiled payload pin | `rebuild/OnslaughtRebuild.Core/Level100MissionProgram.cs` | LevelScript object 20,586 B, SHA-256 `73eb349b…6fb1` |
| Bridge documents | `…/career-progression-static-bridge-contract.md`, `reverse-engineering/save-file/career-unlock-recipes.md` | graph vocabulary, unlock recipes |
| Parity contract | `rebuild/PARITY.md` carried-contract rows (2026-08-17/18/21/22 waves; mutation kills measured) | per-row retail anchors behind the seam tests |
| Goal framing | `GOAL.md` lines 70–96, 1789–1841 | acceptance-test demotion; "proxy, not the goal" |
| Integration/sibling findings | reviewed merge `608d93bd` / Kanban `t_be6f5191` (reticle/adjust-aim correction, managed full-chain semantic receipts), `t_356b980e` (historical native-88 `SecondaryObjectiveFailed` boundary on world 110), later current-main World110 admission `27496779` | current managed full-chain behavior and the world-110 secondary inventory below; not native-play evidence and not a native-88 capability claim |

Known source limits: the pinned drop has **no** `MissionObjective.h`,
`MissionScript` VM, `FEPDebriefing.cpp`, or `FEPLevelSelect.cpp`
(`references/Onslaught/` holds 108 files; `game.h` includes the missing
`MissionObjective.h`). Objective-status vocabulary therefore comes from the
measured plate (`IScript::PrimaryObjectiveFailed` `0x0053445e` writes state 2;
FillOut Won snapshot carries four `MOS_COMPLETE = 1`) and from decompile-level
notes, not from a header in the drop.

### 1.2 The law, stated

For shipped Level 100 (world 100, the training/tutorial level), retail
"finishing the level" is this exact chain:

1. **Script decision.** The hash-pinned compiled `LevelScript` object decides
   the outcome. Its only win exit is native command 9 `LevelWon`
   (`IScript__LevelWon 0x005381E0`); its loss exits are command 8 `LevelLost`
   and command 106 `LevelLostString(id)` (→ `CGame::DeclareLevelLost`). Along
   the first-play path the script issues `PrimaryObjectiveComplete(1..3)`
   repeatedly and `PrimaryObjectiveComplete(4)` when its own `numTargets`
   countdown reaches zero, saves `SLOT_TUTORIAL_1..4` mid-mission through
   command 133 `SetSlotSave`, and awards `AddScore(+50/-50)`.
2. **Engine transition.** `CGame::DeclareLevelWon` (`0x0046f2f0`) guards
   `mGameState <= PLAYING`, writes state 5 (`GAME_STATE_LEVEL_WON`) at
   `this+0x28`, writes the 5.0 f end timer at `this+0x48` (`0x0046f338`;
   worlds 741/742 write 0 instead), clears rumble, pauses. Source
   `game.cpp:1997–2004` then consumes the timer and quits to frontend.
   (`RestartLoopRunLevel`'s measured body also contains an in-loop
   global-time force-win/force-lose arm — see §7 open questions.)
3. **Snapshot.** `CGame::FillOutEndLevelData` (`0x0046d470`) runs during
   attempt shutdown, before any frontend code: `mWorldFinished = mCurrentLevel`
   (=100), `mFinalState = mGameState` (=5), ten stride-8 primary words (four
   `MOS_COMPLETE = 1`, six unset — **not** any rebuild enum), ten unset
   secondary words, `mRanking` pre-arm 1.0 f then the live score-time arm
   (RLWD 300.0/500.0/1.0, S=210, D=70), `mTimeTaken`, `mLevelLostReason` (init
   0 — DeclareLevelWon never writes `+0x114`), 32 slot dwords (first play:
   the four tutorial bits already persisted by `SetSlotSave`), 35 base-thing
   words (TF_DYING store-0 law), five kill dwords from `player+8`.
4. **Outro presentation.** On a Won quit, `game.cpp:1166–1190` gates the Won
   route and looks up/selects the level's outro FMV
   (`lookup_FMV(mCurrentLevel, …)`); `game.cpp:1191–1214` arms and plays it
   (`FMV.PlayFullscreen` at line 1213);
   `CGame::RunOutroFMV` consults `IsAllSecondaryObjectivesComplete` on some
   routes. The PC frontend then initializes and `CFrontEnd::Init` calls
   `CAREER.Update` (`FrontEnd.cpp:67`); the PC init lands on
   `FEP_DEBRIEFING` (`FrontEnd.cpp:233–269`). `Initialize` only allocates and
   resets transient effect storage; `TransitionNotification` consumes the two
   Goodie latches; and `Render` displays the level name, mission status,
   objective-group summaries, and a win-only grade from `END_LEVEL_DATA`.
   The Render body reads no kill table and draws no per-Goodie list.
5. **Career progression.** `CCareer::Update` (`0x0041bd00`) returns after
   `UpdateGoodieStates()` alone unless `mFinalState == GAME_STATE_LEVEL_WON`.
   On Won it: overwrites `mSlots` from the snapshot; adds kill deltas
   (**world 100 is skipped** — `cmp [world], 0x64 / je`); finds the node by
   `mWorldFinished`; stores ranking only if strictly better; sets
   `node->mComplete = TRUE`; sets `mCareerInProgress = TRUE`; runs
   `ReCalcLinks` (`0x0041bdf0`), whose lower-link completion for world 100 →
   world 110 fires **even though** `IsAllSecondaryObjectivesComplete`
   (`0x004496e0`) is the no-objectives FALSE (Level 100 ships four primaries
   and zero secondaries), while the dummy higher link stays
   `CN_NOT_COMPLETE`; propagates base-things onto world 110 via
   `level_structure[0][3]`; and recomputes goodies (S-band unlocks 78/121/164,
   `COMPLETE_LEVEL(100)` opens goodie 0, `GRADE(110)`/`COMPLETE_LEVEL(110)`
   rules stay closed on a first-play S).

**What retail therefore requires for "completed":** the script-issued WON
state, the 5.0 s countdown, the FillOut snapshot, and the career update.
Primary-objective completeness is *displayed* (debriefing) and *produced by*
the script, but `CCareer::Update` never reads the primary table; secondary
objectives do not exist on this level. A human's "finished the level"
additionally includes the outro FMV and the debriefing screen — both outside
what the rebuild currently composes.

**Loss law (the falsifying half):** `DeclareLevelLost(message, player_died)`
(`0x0046f430`) writes the reason, state `LEVEL_LOST`, and a **2.0 f** countdown
(`0x0046f4a8`) — a measured divergence from the source's 5.0 f. Level 100 loss
reasons: `TutorialBroken` (script `LevelLostString`, e.g. after a
`Broke Tutorial` posted by a destroyed-before-activation target's `died()`),
`GAME_OVER_DEATH` (player death), `GAME_OVER_WATER` (water). A dead thing's
mission script is deleted inside `died()` (`thing.cpp:711–724`), so a destroyed
actor can post exactly one terminal fact.

---

## 2. Inventory: completion-related test owners and the exact terminal conditions they assert

Lane-by-lane. Every Level 100 / EndLevel / career-handoff test owner in the
four tracked lanes is inventoried below; owners whose assertions carry no
terminal, snapshot, or handoff content are accounted for explicitly in the
exclusion tables with their asserted condition and the reason they are out of
scope. Counts are anchored C# test-method declarations
(`^\s*public void`), not source strings or theory cases.

### 2.1 rebuild/OnslaughtRebuild.Core.Tests

| Test owner | Test(s) | Exact terminal condition asserted |
| --- | --- | --- |
| `Level100MissionTests.cs` (16) | `SecondaryObjectiveComplete_WritesOnlyTheIndexedRetailSlotAndRejectsSwappedOrOutOfRangeArguments` | managed `RetailSecondaryObjectiveState.SetComplete` writes `MOS_COMPLETE=1` only at the indexed slot (native-84 `0x00534410` store law); a neighboring failed slot is unchanged; swapped or out-of-range arguments throw and leave prior slots untouched. Not a Level 100 terminal (this level ships zero secondaries) and not a native-88 execution claim |
| | `SecondaryObjectiveFailed_WritesTheIndexedRetailSlotAndRejectsSwappedOrOutOfRangeArguments` | managed `SetFailed` writes `MOS_FAILED=2` only at the indexed slot, citing the native-88 body at `0x00534470`; swapped or out-of-range arguments throw. This is a Core store-state adverse control, **not** a native-88 `SecondaryObjectiveFailed` capability |
| | `ReleasedLevelScript_RunsTheCompleteFirstPlayTutorialToLevelWon` | Outcome **Won**; TerminalState **FrontEndHandoffReady**; all four objectives `Complete`; slots saved [63,64,65,66]; 35 ordered message ids; 7 posted events; ScoreDelta 50; FlightModeEnabled — produced by the real embedded `73eb349b…` payload driven through `QueueExternalEvent` (`Level100MissionTests.cs:909`) |
| | `Init_PrimaryObjectiveFailedWritesRetailMosFailedTwo`, `Init_PrimaryObjectiveFailedWritesRetailObjectiveTextDword` | objective-word mapping: retail MOS failed = 2, complete = 1 (via `RetailGameObjectiveCount`), text dwords `_100_OBJECTIVE_1..4`; ten-word table shape |
| | `Init_UnHighlightHudPartWritesOneAfterHighlightTwo` | HUD-part highlight/unhighlight word sequence (two then one) at init |
| | `Init_PlayCharMessageWaitWritesOneAtCvmSingletonPlus220` | PlayCharMessage posts the wait flag: literal 1 stored at CvmSingleton+0x220, not incremented |
| | `MissionNativeSetPos_CopiesGetPosPositionAndPreservesOtherPoseState` | native SetPos copies GetPos position and leaves other pose state intact |
| | `MissionNativeUnsetObjective_ClearsOnlyTheObjectiveFlagAndIsIdempotent` | UnsetObjective clears only the objective flag; idempotent |
| | `MissionNativeDamage_ForwardsTheAuthoredFloat32AmountUnchanged` | native Damage forwards the authored float32 amount unchanged |
| | `MissionNativeDamage_IsIssuedByNoShippedLevel100Program` | negative corpus claim: no shipped Level 100 program issues Damage |
| | `ReleasedPrograms_InitializeAgainstOneCanonicalActorRegistry` | all released programs initialize against the canonical actor registry |
| | `ActorRuntimeSnapshot_RoundTripsAndChangesCanonicalWorldHash` | actor runtime snapshot round-trips and moves the canonical world hash |
| | `TargetTank1_StopsAtTheReleasedWaypointMechanicsBoundary` | Target Tank 1 halts at the released waypoint-mechanics boundary (route-data-derived) |
| | `ReleasedMessageBox_ReproducesTheRetailOpeningDeliverySchedule` | opening MessageBox delivery schedule reproduces the retail schedule |
| | `ExternalTerminalFacts_StopTheReleasedLevelScriptOnce` | `ReportPlayerDeath` → Outcome **Lost**, reason **PlayerDeath**, `DeathPauseDelayTicks` remaining; water likewise; second terminal fact refused |
| `Level100WonCareerHandoffTests.cs` (25) | `FrontEndHandoffReadyAfterWon_AppliesFillOutAndUnlocksWorld110` | after Won + FrontEndHandoffReady: node 100 `Complete=1`, `CareerInProgress=1`, lower link →110 `CN_COMPLETE`, world 110 still incomplete |
| | `…_StoresFillOutRankingOnlyOnWorld100` | ranking 1.0 f stamped only on node 100 (grade S), 110 stays Blank/E |
| | `…_OverwritesCareerSlotsFromFillOutTutorialBits` | 32 slot words overwritten; leftover bits die |
| | `…_UnlocksTrainingGoodiesForAnS`, `…_AddsFiveNewGoodiesAndLatchesFirstGoodie`, plus 4 leftover-goodie, 3 closed-goodie, `…_DoesNotIncrementLeftoverNumAttempts`, `…_DoesNotOverwriteAlreadyOldTrainingGoodies`, `…_StoresNewOverInstructionTrainingGoodies` | `UpdateGoodieStates` band/latch laws through the seam |
| | `…_CopiesFillOutBaseThingsOntoWorld110` | 35 base-thing words land on world 110's node |
| | `SuccessCountdownDoesNotApplyFillOutEvenIfWonIsClaimed`, `…_WaitsForTheFiveSecondCountdown` | career stays cold during `SuccessCountdown`; `WonTicks` (5.0 f) must elapse before `FrontEndHandoffReady` |
| | `LostDoesNotApplyFillOutEvenIfFrontEndHandoffReadyIsClaimed`, `BrokeTutorialLost_DoesNotApplyFillOutOrUnlockWorld110` | Lost/BrokeTutorial never applies FillOut nor unlocks |
| | `SetSlotSave_PersistsTutorialBitsBeforeApplyUpdate` | bits 63..66 set mid-mission, before FillOut overwrite |
| | `AddScore_FirstPlayWonWritesCGamePlusF4`, `EnableFlightMode_FirstPlayWonWritesCBattleEnginePlus58C`, `UnHighlightHudPart_FirstPlayWonWritesOneAtCompass`, `EnableWeapon_FirstPlayWonWritesOneAtTwinVulcanPlus9C`, `SetObjective_FirstPlayWonOrsBit20AtTargetZone4Plus2C` | per-store retail immediates on the script-driven first-play run |
| `Level100PlayerInputWonHandoffTests.cs` (1) | `SimInputOnlyWon_AfterSuccessCountdown_ReachesFrontEndHandoffAndUnlocksWorld110` | SimInput-only chain reaches **Won** with **zero posted mission events**, `SuccessCountdown` with `WonTicks` left, then idle ticks land **FrontEndHandoffReady** and `ApplyUpdate` unlocks world 110; career cold-check before countdown |
| `Level100FullChainTests.cs` (5) | `ChainAutopilot_ReachesWonByInputAlone` | Won; 4 named ground actors + 3 trucks + 6 moving + 3 wave-1 destroyed; all five trigger volumes dispatched; wave-2 kills=6/spawnsDamaged=6/damage=6000; `Aborted=false`; objective 4 Complete; plus current trajectory self-pins tick 6992 / hull 10900 (classified separately in §3) |
| | `NaiveWalkerAutopilot_ClearsTheFiringRangeAndStillNeverFinishes` | honest negative: firing without looking does **not** reach Won; tank dies; route-end arrival asserted from route data |
| | `BlasterMissLaw_…`, `AbortAirborneDrones_…`, `PlayerWeaponFire_…` (adjacent/instrument) | miss separatrix; abort silencing; fire-per-release |
| `Level100ColdStartTests.cs` (4) | `ColdStart_PlaysLevel100ThroughThePlayerInputSurface` | client-routed (pointer-quantised) cold-career run reaches **Won**, FailureReason None, Zone 4 dispatched; unquantised control also Won; zero unreachable look commands |
| | `ColdStart_VisitsEveryReleasedStageInOrder` | stage ordering to Won |
| | `ClientRoute_…`, `ClientPointerPath_…` | quantisation equivalence; retail whole-pixel lattice |
| `Level100TutorialProgressionTests.cs` (9) | `TargetTruckKilledBeforeActivation_LosesTheLevelAndRetiresItsScript` | destroying the unarmed truck pre-activation ⇒ its script runs `died()` and is deleted, then Outcome **Lost**, reason **TutorialBroken** — through live simulation, no injected facts |
| | `AuthoredGroundVehicles_AreSeatedOnTheTerrain` (adjacent) | authored ground vehicles seat onto the terrain sampler at authored poses |
| | `PulseCannonRun_DestroysEveryAuthoredStaticTarget`, drone/tank/vulcan damage-model tests (adjacent) | destruction prerequisites of the progression events |
| `RetailFillOutEndLevelDataTests.cs` (16) | `Level100Won_SnapshotIsWorld100StateWonWithNoSecondaries`, `…_SnapshotCarriesFourMosCompletePrimariesNotTheMissionEnumTwo`, `…_SnapshotRankingIsThePreClampOnePointZero`, `…_DoesNotClampRankingBecauseThereAreNoSecondaries`, `…_FillOutStoresOneForEachOfThirtyFiveBaseThings`, `…_FillOutStoresZeroWhenBaseThingIsDying`, `…_FirstPlayKillReadoutIsFiveZerosUnlessConfirmedKill`, `…_FillOutStoresFiveZeroKillsWhenPlayerPointerIsNull`, `…_FillOutLostReasonStaysInitZero…`, `…_FillOutScoreAndTimeAreThePreArmCopies…`, five score-time-arm tests, `…_FillOutSnapshotDrivesTheAlreadyPinnedCareerUpdate` | the entire §1.2 step-3 snapshot field law against pristine-specimen anchors (PARITY rows; mutation kills measured 2026-08-17/18) |
| `RetailEndLevelObjectivesTests.cs` (10) | `Constants_MatchTheInstructionImmediates`, `Layout_ClosesAgainstTheTwoMeasuredGlobals`, eight `IsAllSecondaryObjectivesComplete` behavior tests | predicate `0x004496e0` law (complete/failed/unset semantics, tenth entry, ten-slot arity) |
| `RetailGameObjectiveCountTests.cs` (3) | `Constants_MatchTheTenSlotTablesAndTheZeroSentinel`, `GetNumPrimaryObjectives_CountsEveryNonZeroStatus`, `Level100Won_PrimaryTableIsFourCompleteOnesNotTheMissionEnumTwo` | count law; MOS vocabulary; Won-table contents |
| `RetailCareerCampaignApplyUpdateTests.cs` (33) | `Level100Won_ApplyUpdate*` (slots, primary-ignore, ranking target/no-downgrade/no-attempts, S/A/B/C/D/E grade bands, leftover-goodies, base-things, kill skip), `Level100Lost_ApplyUpdate*` (no goodies, latches, slots, base-things), `CountGoodies*` family | §1.2 step-5 career laws through `ApplyUpdate` |
| `RetailCareerReCalcLinksTests.cs` (4) | `Constants_MatchTheShippedTrainingSliceAndGameStateWon`, `Level100Won_SecondaryPredicateIsTheNoObjectivesFalse`, `Level100Won_UnlocksWorld110EvenThoughTheSecondaryPredicateIsTheNoObjectivesFalse`, `Level100Lost_DoesNotTouchTheTrainingGraph` | the subtlest law in the chain: lower link completes despite the FALSE predicate; Lost touches nothing |
| `RetailCareerSlotHandoffTests.cs` (4) | `Constants_MatchTheShippedTutorialSlotsAndTheThirtyTwoWordCopy` (theory), `OnlyGameStateLevelWon_CopiesTheSlotWords`, `Level100Won_OverwritesCareerSlotsWithTheFourTutorialBits`, `Overwrite_CopiesAllThirtyTwoWordsIncludingTheUnreachableTail` | 32-word copy gated on FinalState == 5 |
| `RetailConfirmedKillTests.cs` (7) | allegiance gate, five per-flag increments, null-player skip | thingsKilled increment law (career still skips world 100) |
| `RetailAddScoreTests.cs` (1) | `Add_AddsTheDeltaOntoCGamePlusF4NotReplace` | `add [0x008a9b8c]` not replace |
| `RetailGameEndCountdownTests.cs` (4) | `LostCountdown_IsTheImmediateTwoNotTheSourceFive`, `WonCountdown_IsFiveForEveryWorldThatIsNotTheTwoSpecialCases`, `Level100MissionTiming_CarriesTheSameImmediates`, `TutorialBroken_StartsTheTwoSecondLostCountdown` | 5.0 f Won / 2.0 f Lost byte immediates; 741/742 special case |
| `RetailWorldCatalogTests.cs` (7) | `NodeCount_MatchesCareerHeader`, `Root_IsLevel100_…`, `LevelStructure_SpotRowsMatchPinnedSource`, `ChildWorlds_ResolveThroughNodeIndexes`, `IsWorldLater_MatchesSubtreeSemantics` (structure), `IsWorldSelectable_ColdCareerOffersOnlyTheRoot`, `IsWorldSelectable_WonRootUnlocksWorld110ButNotDistantNodes` | offer law before/after the Won update; catalog structure pins |
| `RetailSetObjectiveTests.cs` (1) | `MarkAndUnmark_OrBit20ThenClearItNotBoolReplace` | `CThing+0x2c` bit-20 objective flag law |
| `RetailEnableFlightModeTests.cs` (1) | `Enable_StoresLiteralOneAtCBattleEnginePlus58CNotIncrement` | flight-mode store law: literal 1 at CBattleEngine+0x58C, not increment — the store the Won chain's beat-6 relies on |
| `RetailEnableWeaponTests.cs` (1) | `Enable_StoresLiteralOneAtWeaponPlus9CNotIncrement` | weapon-enable store law: literal 1 at Weapon+0x9C, not increment |
| `RetailHighlightHudPartTests.cs` (1) | `HighlightAndUnhighlight_StoreTwoThenOneNotBoolMask` | HUD-part highlight=2 / unhighlight=1 store law, not a bool mask |
| `RetailIScriptInJetModeTests.cs` (2) | `Evaluate_IsFalseUnlessBattleEngineBit8AndNotARecentlyGroundedWalker`, `Native_AirborneWalkerBattleEngineIsTrueAndNonBattleEngineIsFalse` | the InJetMode predicate law (bit 8 + recent-grounding recency) that gates Target Zone hits and jet-leg progression |
| `RetailIScriptWaitStopTests.cs` (1) | `Stop_StoresLiteralOneAtCvmSingletonPlus220NotIncrement` | wait-stop store law: literal 1 at CvmSingleton+0x220 |
| `Level100EnableFlightModeTests.cs` (1) | `GrantFlightLeg_StoresCBattleEnginePlus58CSoToggleModeCanTakeOff` | granted flight leg writes +0x58C so ToggleMode can take off |
| `Level100DestructionContactTests.cs` (18) | catalog retention, swept-sphere narrowphase, terrain sweep, warehouse extent/terminal rules (30 % core-child law both arms), target-tank typed impact/terminal effects, pulse direct→explosion damage order, drone explosion-stage gating, strictly-negative-life terminal law, overkill trace bits, registry pose/lifecycle facts, occlusion without damage, terrain contact without mutation, destruction snapshot restore/hash, hot-path allocation | the damage/contact/destruction laws that produce the progression events' causal facts (actor deaths); no terminal/completion assertion of its own |
| `Level100FlightLegTests.cs` (2) | `ThreeFlightLegs_AreFlownAndLandedByInputAlone` | all three released flight legs are flown and landed by SimInput alone |
| | `InJetMode_IsFalseOnlyForARecentlyGroundedWalker` | the InJetMode recency clause evaluated in live simulation |
| `Level100FerryLandingTests.cs` (6) | `OnePermilleSweep_NeverDrownsOnTheFerryHome`, `FixedSweep_NeverMorphsAboveTheHandoffClearance` | 20-point ferry-home perturbation sweeps use **Won** as the survival metric |
| | `AdverseControl_CommitsTheFallTheClearanceTermRefuses` | adverse control proves the clearance term prevents the fall |
| | `WaterRule_IsPinnedAtTheReleasedTwoHundredMillimetres`, `WaterRule_AgreesWithTheCommittedElevationInEveryRealRun` | 200 mm retail water-loss threshold and agreement with committed elevations in every real run |
| | `ClearanceTerms_ChangeNothingBeforeTheFerryHome` | added clearance terms do not change the prefix trajectory |
| `Level100TargetZoneHitTests.cs` (2) | `TargetZone2_Hit_PostsReachedOnlyForARecentlyGroundedBattleEngineAndStoresWaitStop` | Target Zone 2 `hit()` posts `Reached Target Zone 2` only for the recently grounded Battle Engine, stores WaitStop, and honors the InJetMode recency gate |
| | `TargetZone2_FallInAndLand_PostsReachedFromHitNotFromTriggerEntered` | fall-in/landing path proves the event originates from `hit()`, not `triggerEntered()` |
| `Level100SkipPanningTests.cs` (14) | `SkipDuringPanning_EndsThePanAndStartsPlayingState`, `NoInputDoesAnythingDuringThePan_OnAReturningCareerWherePlayerIsActive`, `TheSkipTickIsStillAPanningTick_OnAReturningCareer`, `NoInputDoesAnythingWhilePanning_IncludingOnTheSkipTickItself`, `SkipAfterPlayingStateHasStarted_DoesNothingAtAll` | skip/no-input state-gate laws across Panning → Playing; the skip tick remains a panning tick and post-playing skip is inert |
| | `SkippingThePan_MovesTheWholeTutorialMessageSchedule`, `SkippingThePan_MovesPlayerActivationEarlierByTheSameAmount` | schedule and activation both shift earlier by the skipped duration |
| | `SkipStillWorksAfterAReset_BecauseTheGateIsMissionRelative`, `SkipIsAnEdgeAndReplaysDeterministically`, `SkipPanningIsAnEdgeActionInTheTape` | mission-relative reset gate, edge semantics, deterministic replay, tape representation |
| | `ATapeWrittenUnderTheOldSchemaIsRejectedRatherThanMisparsed`, `DeclaredButUnimplementedActionsAreRejectedRatherThanIgnored`, `ActionSetFitsTheChosenWidthWithRoomToSpare`, `TheUnprovenSkipKeyRoutingStaysRecordedOnTheAction` | tape schema/width/rejection laws and explicit recording of the unproven key-routing boundary |
| `SimulationTests.cs` (file total **46** public methods: 42 Facts + 4 Theories; adjacent) | `World110Session_CrossesNative88AndStepsDeterministically`; `CanonicalHash_PreservesWorld100SchemaAndBindsWorld110SecondaryState`; `Level100FirstRun_AppliesReleasedMessagesActivationAndTriggerCommands`; `PulseCannonEmitter_ConvergesOnTheCameraReticleContact`; `PulseCannonEmitter_DoesNotSnapMissesOutsideTheContactVolume` | world-110 Core admission constructs, records secondary[1] Failed, and idle-steps two sims to one hash; the hash test keeps world-100 schema 42 on the 40-step control hash and binds schema-43 world-110 secondary slots so a changed text dword moves the hash. First-run init applies released messages, activation, and trigger commands; the two reticle additions assert that the source-backed adjustable cockpit emitter converges on a camera-reticle contact and does not snap two misses outside the contact volume. These are admission/schema/beat/aim instruments beneath or beside the Level 100 progression chain, not terminal assertions, not authored-110 content, not native-88 capability, and not native-play assertions |

Excluded Core.Tests owners (checked; asserted condition + reason):

| Excluded owner (count) | What it asserts | Why excluded |
| --- | --- | --- |
| `Level100ActorMechanicsTests.cs` (6) | base-pose advance/full-stop divergence, ground-vehicle cadence/velocity, command-intent ordering, transporter arrival radius, hash retention | movement-domain laws; no terminal, snapshot, or career-handoff assertion |
| `Level100ActorRegistryTests.cs` (10) | registry spawn/pose/restore identity, facility-event spellings, invalid-spawn rejection | actor-infrastructure laws; participates in no terminal condition |
| `Level100ActorWeaponTests.cs` (6) | shipped random stream, scatter bound, drone fire-and-close, round impact aggregate, armament replay, missile homing | weapon-domain laws upstream of destruction but carrying no completion assertion |
| `Level100AirTrainerFlybyTests.cs` (5) | flyby path visit order, ground clearance, chain wrap/completion | ambient-aircraft domain |
| `Level100JetGroundEffectTests.cs` (2) | ground-effect engagement height and lead distance | flight-feel domain; no handoff content |
| `Level100PlayerDamageTests.cs` (18) | shield/life routing, augment, death strictly-below-zero, regeneration, flash lists | player-death *mechanics* only; the mission-terminal PlayerDeath outcome is owned by `Level100MissionTests.ExternalTerminalFacts_StopTheReleasedLevelScriptOnce` |
| `Level100PlayerWeaponRuntimeTests.cs` (8) | weapon selection/cycle/wrap runtime | weapon-UI domain |
| `Level100PulseCannonChargeTests.cs` (3) | pod levels, charge increments, charged-bolt selection | weapon domain |
| `Level100WaypointFixtureTests.cs` (5) | fixture manifests match serialized paths/nodes | test infrastructure |
| Remaining `Retail*` lane files (analogue controls, camera laws, battle-engine configuration/cloak/gravity/interpolation/augment, chunk reader, event scheduler, frontend harness/world strings, jet auto-level/friction/thrust, walker water entry, weapon charge/selection/stores, career grades/nodes/progress/save-codec/kill-counters, world 110/200/300 admission) | their own retail law lanes (controls, physics, weapons, frontend chrome, save codecs, other worlds' admission) | none of them asserts a Level 100 terminal condition, the FillOut snapshot, or the world-100 career handoff; the career-graph pieces they own that bear on the handoff are already inventoried above via the ApplyUpdate / ReCalcLinks / SlotHandoff / ConfirmedKill / WorldCatalog / Grades-consuming owners |

### 2.2 rebuild/OnslaughtRebuild.Client.Tests

Fresh-current-main census: exactly **22** files match
`rebuild/OnslaughtRebuild.Client.Tests/*Level100*Tests.cs`. All 22 are named
below: `Level100HudPresentationTests` and `Level100AudioCatalogTests` in the
completion-related table, plus the other 20 in the explicit exclusion table.
`RetailCampaignFlowTests` and `InteractiveSessionTests` do not match that file
glob but remain inventoried because they own the frontend handoff and client
loss path respectively. Counts below use anchored C# method declarations
(`^\s*public void`), so source-code strings containing those words do not
inflate the result.

| Test owner | Test(s) | Exact terminal condition asserted |
| --- | --- | --- |
| `RetailCampaignFlowTests.cs` (5) | `WonHandoff_ReturnsToLevelSelect_AndUnlocksWorld110` | `TryAcceptWonHandoff(Won, FrontEndHandoffReady)` applies the FillOut update, lands **LevelSelect** with world 110 selectable, launch-world bookkeeping; `SelectWorld(110)` launches 110 and reports it unconstructible today |
| | `WonHandoff_IsRejectedUnlessGameplayWonIsReady` | rejection off Gameplay / non-Won / non-ready states |
| | `ColdCareer_SelectorOffersOnlyWorld100_AndLaunchCarriesIt`, `WonRoot_UnlocksWorld110_AndLaunchCarriesIt` | selector offer law and launch-world carry |
| | `SelectWorld_IsRejectedOutsideLevelSelect` | navigation guard: world launch refused off LevelSelect |
| `InteractiveSessionTests.cs` (3 relevant/adjacent of **44**) | `ClientLevel100FailureTape_FirstRunRepeatsLossTextAndHashes`, `MaterializedLevel100ActorDefinitions_RepeatFailureHashes` | `BrokeTutorial` input through the client session ⇒ Outcome **Lost**, `FailureTextId` 1110345999, `FailureCountdownElapsed`; byte-hash repeatable |
| | `FirstFlightSmokeScenario_ReachesFiringRangeAndCompletesWaypoint` (adjacent) | scripted inputs reach the Firing Range beat |
| | remaining **41** methods (input edges, frame partitioning, pause/resume, focus loss, pointer curves, event envelopes, materialization) | session/input/presentation laws with no terminal, snapshot, or career-handoff assertion — explicitly excluded from completion classification |
| `Level100HudPresentationTests.cs` (1 relevant of **18**) | `ProjectionExposesRetailTerminalOverlayOnlyWhileCountdownRemains` (8-case theory) | terminal overlay visibility/ticks across Won/Lost × SuccessCountdown/FrontEndHandoffReady/FailureCountdown/FailureMenuReady/FailureCountdownElapsed |
| | remaining **17** methods | delivery-log/message/objective projection, influence/damage/weapon HUD state, repeated-help/playback independence, captured wrapping/type-on timing/centering; no terminal outcome, EndLevel snapshot, or career handoff — explicitly excluded |
| `Level100AudioCatalogTests.cs` (1 relevant of **30**) | `DeathTerminalFeedsTheRecoveredMixBeforeTheNominalPause` | static source-order gate over `FirstFlightGame.ConsumeFrameEvents` and `ResumeFromAuthenticPause`; the exact asserted token sequences and negative/count assertions are enumerated immediately below |
| | remaining **29** methods | message/voice queues, warning and movement cues, water-skimming quiet gap, cue/music/options/fade/spatial/pitch laws; audio-domain assertions with no terminal outcome, EndLevel snapshot, or career handoff — explicitly excluded |

`DeathTerminalFeedsTheRecoveredMixBeforeTheNominalPause` is a source-reader,
not an executed Godot-host test. Its exact static assertions are:

- in `ConsumeFrameEvents`, this order:
  `_audio.SetGameplayMix(Level100MissionTiming.GameplayMix(` →
  `mission.Outcome,` → `mission.FailureReason,` →
  `mission.TerminalTicksRemaining));` →
  `_audio.SetGameplayPaused(Level100MissionTiming.GameplayPaused(` →
  `mission.Outcome,` → `mission.FailureReason,` →
  `mission.TerminalTicksRemaining));`;
- exactly one occurrence each of `_audio.SetGameplayMix(` and
  `_audio.SetGameplayPaused(` in that method, and no
  `OpenAuthenticPauseMenu` token;
- in `ResumeFromAuthenticPause`, this order:
  `_session.SetAuthenticMenuPaused(false);` →
  `Level100MissionSnapshot mission = _session.CurrentSnapshot.Level100Mission;`
  → `_audio.SetGameplayPaused(Level100MissionTiming.GameplayPaused(` →
  `mission.Outcome,` → `mission.FailureReason,` →
  `mission.TerminalTicksRemaining));`; and
- no `_audio.SetGameplayPaused(false)` token in that resume method.

The other 20 current-main Client Level100 owners are present but outside this
completion audit. Each is explicitly accounted rather than silently omitted:

| Excluded Client Level100 owner | Asserted condition | Why excluded from completion classification |
| --- | --- | --- |
| `RetailLevel100CutsceneTests.cs` | measured pre-level cutscene quad/UV/brightness/decoder, one-clip schedule, skip/retry/re-entry/loading order, and Bink voice-track coverage | this is the **intro** between loading and gameplay, not the Won outro, debriefing, terminal snapshot, or career handoff |
| `Level100WaterEnvelopeTests.cs` | captured water geometry remains inside the retail envelope and shoreline shader operands retain their order | rendering envelope only; it does not assert the hostile-water Lost outcome or reason |
| `Level100VoiceProgressTests.cs` | started voice messages are an ordered prefix, speaker identity/order survives, requested smoke messages resolve, and clearing leaves no stale message | queue/playback progress only; no terminal outcome, snapshot, or handoff |
| `Level100VertexDiffuseTests.cs` | per-vertex diffuse payloads, authored non-white meshes/bytes, shader binding/modulation, normal-space and static/tree lighting rigs | world-rendering law only |
| `Level100TerrainCompositorTests.cs` | level-zero terrain tile reproduces the pinned root map; detail rotation and cloud-scroll constants are pinned | terrain composition only |
| `Level100TerrainAmbientLightTests.cs` | terrain diffuse is 0.5 × summed HFLD lights, coefficients/clamp match shipped bytes/D3D, and the shader applies the stage-zero lighting term | terrain-lighting law only |
| `Level100SunTests.cs` | shipped sun sprite/colour/radius and decoded descriptor values | sun rendering only |
| `Level100StaticWorldAnimationTests.cs` | authored active classification, released lap lengths, frame-zero rest, cyclic return, and disjoint animated vertex ranges | static-world animation only |
| `Level100SkipPanningClientTests.cs` | queued skip ends the pan on the next step, skip is one edge, paused/suspended skips drop, and three of four scan codes are statically bound with reachability unproven | pre-playing client-input gate only; no terminal outcome or handoff (the Core 14-test skip family is separately inventoried as a PARTIAL prerequisite) |
| `Level100ScannerProjectionTests.cs` | decoded scanner constants, facing/bearing/scale/rim/alpha laws, measured blobs, allegiance, objective retention and tint | scanner projection only |
| `Level100RenderInterpolationTests.cs` | continuous target position/orientation, shortest-arc spherical weights, interpolation suppression, projectile first-frame muzzle state, and non-rotation fallback | renderer interpolation only |
| `Level100PineRepresentationTests.cs` | authored LOD distance, complementary shader gates, seating/bounds/six-view imposters, static clamp, docks pivot and turret seating | vegetation/static representation only |
| `Level100PauseMenuTests.cs` | retained menu order/navigation/cancel, safe confirmations, Godot input/audio/cursor integration, panel geometry/tint and no invented legibility treatment | pause-menu behavior only; retry/quit presentation does not assert a resulting Won/Lost snapshot or career update |
| `Level100MessageScheduleTests.cs` | delivery/clear windows, elapsed-time conversion, greeting timing, captured text gates, product-path tick ownership and MessageBox gap behavior | tutorial message timing only |
| `Level100MacroCacheResolutionTests.cs` | every downsampled macro-cache level resolves to the root terrain map | terrain-cache resolution only |
| `Level100HudLowerRightSocketTests.cs` | portrait/influence/Forseti selection and explicit unknown/unavailable handling | lower-right HUD socket state only |
| `Level100HudDesignSpaceTests.cs` | 640×480 stage, viewport-independent layout, measured circles/baselines/panel metrics, nearest blit, centred whole-stage transform | HUD geometry only |
| `Level100HudBlendEvidenceTests.cs` | DXT1 opacity, compass alpha, post-modulate/additive rules, damage flash, battle-line/compass composition and message-noise blending | HUD blend evidence only |
| `Level100EngineViewpointStateTests.cs` | initial camera, attached-thing identity across the six-second camera handoff, missing-identity clearing, canonical hash, dependency boundary and selected snapshot consumption | camera/viewpoint handoff, not the end-level frontend/career handoff |
| `Level100AmbientAircraftTests.cs` | two ambient aircraft project to the renderer without becoming targets, authored motion/freeze behavior, visual bindings, and player exclusion | ambient actor presentation only |

### 2.3 rebuild/OnslaughtRebuild.Godot (host)

No test project exists for `OnslaughtRebuild.Godot` (absent from
`OnslaughtRebuild.slnx`). Owners involved: `FirstFlightGame.cs`
`TryAcceptWonFrontendHandoff` (lines 829–838 — polls `TerminalState ==
FrontEndHandoffReady` and calls `AcceptWonHandoff` at line 837; line 823
`SetProcess(false);` is the load-failure arm, not the handoff predicate),
`RetailFrontendFlow.AcceptWonHandoff` (line 689),
`RetailFrontendScenePath.TryAcceptWonHandoff` (line 236, the documented
FEP_DEBRIEFING substitution), `FirstFlightHud.DrawTerminalOverlay`
(lines ~2686–2700, renders `Victory`/`Defeat` from the catalog),
`Level100HudAssetCatalog` (validates terminal-string identity and non-empty
text when the manifest is materialized). **None of these hops has an
automated gate.**

### 2.4 OnslaughtCareerEditor.AppCore / WinUI / Cli

| Test owner | Test(s) | Relation to completion |
| --- | --- | --- |
| `SaveAnalyzerServiceTests.cs` | `BuildAnalysisDocument_ForCareerSave_ProducesExpectedMetricsAndSummary` | reads `.bes` nodes/links/goodies (CompletedNodes etc.) — save analysis, not mission completion; document is constructed, not derived from a played level |
| `AssetCatalogServiceTests.cs` | `GoodieUnlockRequirementService_MapsSourceBackedRules` (theory) | text mapping of the goodie law incl. "Complete level 100." / grade bands, evidence-labelled `CCareer__UpdateGoodieStates 0x0041c470` |
| `MissionScriptGoodieStateSaveCodecTests.cs` (15) | `GetVectorFromScriptIndex_MatchesStaticGoodieOffsetProof`, `GetStateLabel_MatchesAppCoreGoodieVocabulary`, `SetDisplayableStatesByScriptIndex_MatchesCopiedBaselineChangedOffsets`, `DisplayableSet_IsIdempotentAndUnknownRoundtrips`, `Codec_RejectsInvalidIndicesStatesAndContainers`, `SetDisplayableStatesByScriptIndex_InvalidMixedBatchLeavesBufferUnchanged`, per-index matrices (`…TouchesOnlyExpectedDwordStartAndRoundtrips`, `…MatchesTrueViewOffsetAndRange`, reserved-index rejection, boundary state matrix), raw-state range rejection, `TryGetDisplayableStateBySaveIndex_*`, `TryReadDisplayableCensus_*` | goodie-state codec law against copied-baseline offsets (the `.bes` twin of `UpdateGoodieStates` persistence); orthogonal to the Won chain — no terminal assertion |
| `MissionScriptSlotBitsetSaveCodecTests.cs` (7 + theories) | slot-bit codec vs copied-file proofs (slots 61/62, per-slot roundtrip) | the `.bes` twin of `SetSlotSave` persistence |
| `BesFilePatcher.cs` (comment, line 438) | grade computed at runtime from EndLevelData; RankingScore patches removed | acknowledged law, **no test owns it** |
| `SaveLabGoodieUnlockHonestyTests.cs` (5, UiTests) | UI honesty of unlock descriptions | presentation only |
| Cli.Tests | verb routing/exit codes only | **no** completion/career-handoff owner exists in the CLI lane |
| WinUI | none | **no** completion-path test owner |

Excluded AppCore/Ui/Cli owners (checked; reason): the remaining AppCore files
(options contract, patch catalogs, cheat catalog, game-text catalog, media
catalog, safe-copy profiles/rescue, career-save location) assert tool-lane
contracts with no Level 100 completion, EndLevel, or handoff content.

---

## 3. Classification

Classes — the only three labels used in this report:

- **TRUTHFUL** — the assertion's falsifiable content is the retail terminal
  condition (Won/Lost through the released mechanism, including honest
  negatives) or a retail field/seam law of the completion chain (a store,
  copy, predicate, or countdown pinned to a pristine VA/immediate/global).
  When the content is such a law, the drive that triggers it being injected
  does not weaken the law.
- **PARTIAL** — genuinely retail-shaped but with a bounded gap: the
  completion *causality* is exercised through a synthetic hop (facts injected
  via `QueueExternalEvent`), an omniscient driver stands in for the human, a
  known divergence is codified, or the test plays an instrument/prerequisite
  role for the chain.
- **SYNTHETIC_ONLY** — the assertion's content is rebuild-local or
  self-referential with no retail anchor in the asserted expression (constant
  compared to itself, trajectory values pinned to this tree's own run).

Per-assertion splits are called out in the caveats wherever one test mixes
classes.

| Area / test | Class | Evidence & bounded caveats |
| --- | --- | --- |
| `ReleasedLevelScript_RunsTheCompleteFirstPlayTutorialToLevelWon` | **PARTIAL** | real hash-pinned payload and opcodes; the asserted *outcome* (Won, objectives, slots, messages, score, flight) is genuine script law, but all 27 progression facts are injected via `QueueExternalEvent` (`Level100MissionTests.cs:909`), so this test alone does not prove gameplay *produces* them (the full-chain and cold-start tests close that hop) |
| `SecondaryObjectiveComplete_WritesOnlyTheIndexedRetailSlotAndRejectsSwappedOrOutOfRangeArguments` | **TRUTHFUL** | indexed-slot `MOS_COMPLETE=1` store/reject law pinned to native-84 `0x00534410`; Level 100 ships zero secondaries, so this is isolated store-state rather than completion causality, and it is not a native-88 execution claim |
| `SecondaryObjectiveFailed_WritesTheIndexedRetailSlotAndRejectsSwappedOrOutOfRangeArguments` | **TRUTHFUL** | indexed-slot `MOS_FAILED=2` store/reject law citing native-88 `0x00534470`. Managed Core store-state only: this report does **not** claim native-88 `SecondaryObjectiveFailed` capability |
| `Init_PrimaryObjectiveFailedWritesRetailMosFailedTwo` / `…ObjectiveTextDword` | **TRUTHFUL** | MOS-vocabulary and text-dword immediates pinned to the measured plate |
| `Init_UnHighlight…`, `Init_PlayCharMessageWait…` (Level100MissionTests) | **TRUTHFUL** | store laws with pristine immediates (+0x220 law shared with `RetailIScriptWaitStopTests`) |
| `MissionNativeSetPos_/UnsetObjective_/Damage_*`, `ReleasedPrograms_*`, `ActorRuntimeSnapshot_*`, `TargetTank1_*`, `ReleasedMessageBox_*` | **PARTIAL** | real native-command and route laws of the released payload, but isolated from the completion chain — prerequisite/instrument role |
| `ExternalTerminalFacts_StopTheReleasedLevelScriptOnce` | **TRUTHFUL** | terminal refusal/dedup law of the released script itself; loss reasons pinned |
| `Level100WonCareerHandoffTests` consumer family (25) | **PARTIAL** | the FillOut/career seam mutations they assert are real, but the shared drivers inject the progression facts at `Level100WonCareerHandoffTests.cs:1182-1210,1238-1259` via `QueueExternalEvent`, so completion causality is synthetic per the definition above; the load-bearing snapshot/career pins are independently owned TRUTHFULLY by the `RetailFillOutEndLevelDataTests` / `RetailCareer*` families |
| `Assert.All(RetailFillOutEndLevelData.ForLevel100Won().SecondaryStatuses, …)` sprinkles inside that family | **SYNTHETIC_ONLY** | constant compared to itself; cannot fail independently; zero falsification power (see §4 G5) |
| `SuccessCountdownDoesNotApplyFillOutEvenIfWonIsClaimed`, `…_WaitsForTheFiveSecondCountdown`, `LostDoesNotApplyFillOut…`, `BrokeTutorialLost_DoesNotApplyFillOut…` | **TRUTHFUL** | countdown/state-gate field laws (5.0 f / WonTicks, FinalState==5 gate) with pristine anchors |
| `SetSlotSave_PersistsTutorialBitsBeforeApplyUpdate` | **TRUTHFUL** | command-133 persistence law with pristine anchor; caveat: drive is event-injected (irrelevant to the store law) |
| `AddScore_FirstPlayWonWritesCGamePlusF4`, `EnableFlightMode_…Plus58C`, `UnHighlightHudPart_…Compass`, `EnableWeapon_…Plus9C`, `SetObjective_…Bit20` | **TRUTHFUL** | per-store immediacies pinned to pristine addresses; the drive being event-injected does not change what the store asserts |
| `SimInputOnlyWon_AfterSuccessCountdown_ReachesFrontEndHandoffAndUnlocksWorld110` | **PARTIAL** | zero-posted-event input causality is genuine and the script issues Won itself; bounded by GOAL.md's own demotion — the autopilot *reads* omnisciently (exact health, full poses), so this proves the machine path, not that a human finished; the career-node assertions it embeds restate TRUTHFUL `ApplyUpdate` field laws |
| `ChainAutopilot_ReachesWonByInputAlone` — terminal/path assertions (Won, actor/volume/wave/objective facts) | **PARTIAL** | same omniscient-driver bound; machine-path proof |
| `ChainAutopilot_ReachesWonByInputAlone` — current trajectory pins tick 6992 / hull 10900 (`Level100FullChainTests.cs:414-415`) | **SYNTHETIC_ONLY** | self-pins of this tree's own managed run; no retail anchor in the asserted expression (reviewed merge `608d93bd` moved the prior 6572/18244 pins through the released adjust-aim law — evidence the values track the rebuild, not retail or a native human playthrough) |
| `NaiveWalkerAutopilot_…NeverFinishes` | **TRUTHFUL** | honest `NotEqual(Won)` negative control through live simulation with route-data-derived arrival assertions |
| `TargetTruckKilledBeforeActivation_LosesTheLevelAndRetiresItsScript` | **TRUTHFUL** | end-to-end released loss through live sim: `died()` → script retirement → `Broke Tutorial` → `LevelLostString` → Lost/TutorialBroken |
| `ColdStart_PlaysLevel100ThroughThePlayerInputSurface`, `ColdStart_VisitsEveryReleasedStageInOrder` | **PARTIAL** | client-routed input causality to Won is genuine; same omniscient-driver bound |
| `ClientRoute_…`, `ClientPointerPath_…` | **PARTIAL** | quantisation-equivalence instruments around the input surface |
| FillOut / EndLevelObjectives / ObjectiveCount / SlotHandoff / ConfirmedKill / AddScore / GameEndCountdown / SetObjective families | **TRUTHFUL** | every row traces to a pristine VA and most carry measured mutation kills (`rebuild/PARITY.md` receipts); they pin the snapshot, not the Won moment |
| Career `ApplyUpdate` / `ReCalcLinks` / WorldCatalog offer-law tests | **TRUTHFUL** | incl. the no-secondaries-FALSE subtlety and the Lost early-return |
| `RetailWorldCatalogTests` structure rows (`NodeCount_…`, `Root_…`, `SpotRows…`, `ChildWorlds…`, `IsWorldLater…`) | **TRUTHFUL** | catalog structure pinned to source rows |
| `RetailEnableFlightModeTests`, `RetailEnableWeaponTests`, `RetailHighlightHudPartTests` | **TRUTHFUL** | store-immediate laws (literal-1 stores, two/one mask) used by the handoff family |
| `RetailIScriptInJetModeTests`, `RetailIScriptWaitStopTests` | **TRUTHFUL** | predicate/store contract laws behind Target Zone gating and PlayChar waits |
| `Level100EnableFlightModeTests.GrantFlightLeg_…` | **TRUTHFUL** | +0x58C store law through the granted-flight path |
| `Level100DestructionContactTests` (18) | **PARTIAL** | retail-shaped damage/contact/destruction laws that produce the progression events' causal facts; none asserts a terminal condition — prerequisite role |
| `Level100FlightLegTests.ThreeFlightLegs_AreFlownAndLandedByInputAlone` | **PARTIAL** | input-flown path proof through released mechanics; no pinned retail value |
| `Level100FlightLegTests.InJetMode_IsFalseOnlyForARecentlyGroundedWalker` | **TRUTHFUL** | restates the measured predicate law inside live simulation |
| `SimulationTests.Level100FirstRun_AppliesReleasedMessagesActivationAndTriggerCommands` | **PARTIAL** | beat-level init law beneath the events; isolated from the terminal chain |
| `SimulationTests.World110Session_CrossesNative88AndStepsDeterministically` | **PARTIAL** | managed Core admission: a world-110 session constructs, records secondary[1] Failed, and idle-steps deterministically. Not authored-110 content, not a native-88 `SecondaryObjectiveFailed` capability, not Level 100 completion, and not a native human playthrough |
| `SimulationTests.CanonicalHash_PreservesWorld100SchemaAndBindsWorld110SecondaryState` — schema 42/43 secondary bind | **PARTIAL** | rebuild canonical-schema instrument: world 100 stays schema 42; world 110 binds the ten secondary slots so a changed text dword moves the hash. Isolated from the Level 100 completion chain and not a native-88 capability claim |
| `SimulationTests.CanonicalHash_PreservesWorld100SchemaAndBindsWorld110SecondaryState` — 40-step control hash `b8a1c8bc…1216` | **SYNTHETIC_ONLY** | self-pin of this tree's own managed run; no retail anchor in the asserted expression |
| `SimulationTests.PulseCannonEmitter_ConvergesOnTheCameraReticleContact` / `…DoesNotSnapMissesOutsideTheContactVolume` | **PARTIAL** | source-backed adjustable-emitter contact/miss instruments added by reviewed merge `608d93bd`; they explain the current managed trajectory change but do not measure retail, assert completion, or prove native human play |
| Ferry/water: `WaterRule_IsPinnedAtTheReleasedTwoHundredMillimetres`, `WaterRule_AgreesWithTheCommittedElevationInEveryRealRun` | **TRUTHFUL** | the 200 mm rule is byte-pinned both sides (`BattleEngine.cpp:1249–1266`) |
| Ferry/water sweeps: `OnePermilleSweep_…`, `FixedSweep_…`, `AdverseControl_…`, `ClearanceTerms_ChangeNothingBeforeTheFerryHome` | **PARTIAL** | perturbation envelopes counting Won as the survival metric — instrument role, they do not measure retail |
| TargetZone hit tests (`Level100TargetZoneHitTests`) | **PARTIAL** | event-production law, retail-anchored via the InJetMode contract, but isolated from the mission |
| Core skip-panning family (`Level100SkipPanningTests`, 14) | **PARTIAL** | pre-playing-state window law only; the separate Client skip owner is explicitly excluded in §2.2 because it has no terminal assertion |
| `WonHandoff_ReturnsToLevelSelect_AndUnlocksWorld110` | **PARTIAL** | known divergence: the frontend *terminal* experience intentionally substitutes SELECT LEVEL for retail's `FEP_DEBRIEFING` + outro FMV (`RetailFrontendSession.cs:656–668` records the substitution); what it asserts is real but is not retail's post-Won screen sequence |
| `WonHandoff_IsRejectedUnlessGameplayWonIsReady` | **PARTIAL** | rebuild session-guard law in the substitution context; no direct retail counterpart is testable while FEP_DEBRIEFING is substituted |
| `ColdCareer_SelectorOffersOnlyWorld100…`, `WonRoot_UnlocksWorld110…` | **TRUTHFUL** | selector offer law restating the pinned career-graph law through the session |
| `SelectWorld_IsRejectedOutsideLevelSelect` | **SYNTHETIC_ONLY** | with respect to completion, this is a navigation guard with no retail anchor in the asserted expression |
| `ClientLevel100FailureTape_…`, `MaterializedLevel100ActorDefinitions_RepeatFailureHashes` | **TRUTHFUL** | loss path: released input → script → Lost, hash-stable; `FailureTextId` is a hashed id with no `text.stf` resolution owner |
| Smoke-scenario test | **PARTIAL** | progression prefix only |
| `ProjectionExposesRetailTerminalOverlayOnlyWhileCountdownRemains` | **PARTIAL** | countdown arithmetic is byte-anchored; the overlay's own look/text has no retail anchor |
| `Level100AudioCatalogTests.DeathTerminalFeedsTheRecoveredMixBeforeTheNominalPause` | **PARTIAL** | exact static source-order assertion proves the host feeds terminal outcome/reason/ticks into the recovered mix before deriving the nominal pause, and re-derives that pause after menu resume; it does not compile or execute the Godot host, exercise audio, prove a Won handoff, or represent a native human playthrough |
| `BuildAnalysisDocument_ForCareerSave_…` | **SYNTHETIC_ONLY** | with respect to completion, this is a constructed document for UI metrics; no claim about played outcomes |
| `GoodieUnlockRequirementService_MapsSourceBackedRules` | **PARTIAL** | faithful text mapping of measured goodie rules; string-level only |
| `MissionScriptGoodieStateSaveCodecTests` (15), `MissionScriptSlotBitsetSaveCodecTests` (7+) | **TRUTHFUL** | codec laws: copied-baseline offset proofs; orthogonal to the Won chain — they pin `.bes` persistence twins of SetSlotSave/goodie state, not completion |
| `SaveLabGoodieUnlockHonestyTests` | **SYNTHETIC_ONLY** | with respect to completion, this asserts UI wording honesty only |

**Verdict.** The completion chain's *field law core* is truthful: the
countdowns, the FillOut snapshot, the career handoff, the loss paths, and the
negative controls are asserted against pristine-specimen anchors through the
released mechanisms. The *completion causality* side is honestly weaker than
rev A claimed: every test that ends a scripted first play in Won reaches it
through `QueueExternalEvent` injection (PARTIAL), the input-only chains prove
the machine path but stand in for no human (PARTIAL), and the full chain's
trajectory pins are self-referential (SYNTHETIC_ONLY). Three bounded gaps keep
the suite from asserting the full human experience: (a) the post-Won
presentation (debriefing page, outro FMV) is substituted, not tested against
retail; (b) the Godot host hop from Core Won to frontend return is untested;
(c) the last EndLevelData joins (live score/time/kills from a simulated run
feeding the score-time arm) are proven on parameterized snapshots and
script-driven missions rather than on the input-only chain.

---

## 4. Gap table

| # | Test / area | What it proves | What retail requires that it does NOT check | Cheapest falsifier / correction owner |
| --- | --- | --- | --- | --- |
| G1 | Whole suite | Won state + FrontEndHandoffReady + career apply | Outro FMV on Won (`game.cpp:1166–1190` gate/lookup/selection; `game.cpp:1191–1214` playback arm through `FMV.PlayFullscreen` line 1213, `RunOutroFMV 0x0046d9f0`) — nothing plays or is asserted | Extend `RetailCampaignFlowTests` once an outro seam exists; blocked on video-infrastructure decision (recorded future question, no owner this cycle) |
| G2 | `RetailCampaignFlowTests` (session level) | handoff acceptance + selector unlock | The Godot tick seam that actually delivers it: `FirstFlightGame.TryAcceptWonFrontendHandoff` → `RetailFrontendFlow.AcceptWonHandoff` has **no** test owner (Godot not in slnx) | Card **N2** |
| G3 | `Level100PlayerInputWonHandoffTests` | SimInput-only Won → handoff → world 110 | The run's own live score/flight stores through `AddScore`/`+0xf4` and `EnableFlightMode`/`+0x58c` are only proven on the script-event-driven mission (`Level100WonCareerHandoffTests.AddScore_FirstPlayWonWritesCGamePlusF4` et al.), never joined to the input-only chain's end-state | One joined assertion set on the shared fixture — card **N3** |
| G4 | `WonHandoff_…` | return to LevelSelect | At the audited base, the settled mission-status, primary/secondary summary, and win-only grade page was composed nowhere; transient Goodie effects/message and transition animation were also open | Card **N1** (projection owner; see the dependency note there) |
| G5 | Consumer handoff tests | various seam mutations | Nothing (behaviorally) — but the repeated `Assert.All(ForLevel100Won().SecondaryStatuses…)` self-comparison has zero falsification power and inflates apparent coverage | Hygiene only; the load-bearing pins already live in `RetailFillOutEndLevelDataTests.Level100Won_SnapshotIsWorld100StateWonWithNoSecondaries`. Listed, no card (filler rule) |
| G6 | `ClientLevel100FailureTape_…` | Lost + hashed text id | `TEXT_DB.GetString(message)` resolution — the player-visible loss sentence is never resolved/asserted | Owner would be a text.stf reader; low player impact on L100 (defeat string dominates); recorded, no card |
| G7 | Terminal overlay (HUD/Godot) | visibility/tick law | "Victory"/"Defeat" render strings: `Level100HudAssetCatalog` pins each string's *identity* (textId + symbol, e.g. `FETX_VICTORY` 8959659) and rejects empty text, but the tracked tree carries no materialized manifest (`res://Assets/Level100/MissionData/level100-hud-events.json` is user-materialized local content), so the displayed pair has no tracked retail-text anchor and no captured end-of-level frame pins it | Recorded standalone future gap: capture one retail end-of-level frame and pin the rendered pair (requires the materialized install + capture policy); no owner this cycle, folded into no card |
| G8 | Suite-wide | — | `BesFilePatcher`'s "grade computed at runtime from EndLevelData" law (comment `BesFilePatcher.cs:438`) has no owning test anywhere | Candidate follow-up for the AppCore lane; recorded, no card under the materiality bar this cycle |

---

## 5. Correction nominations (material, non-overlapping)

These are nominations only. Per the card contract, the minimal cards are to be
created **after** this report is committed, pushed, and independently
reviewed.

- **N1 — First-play tutorial debriefing projection (synthetic snapshot).**
  Renamed/narrowed from rev A's "post-Won debriefing parity slice": because
  the only snapshot available today is the canned pre-arm one, this card is
  explicitly a **projection** correction, not parity, and must not be
  presented as parity.
  Ownership (one exact triple): production
  `rebuild/OnslaughtRebuild.Client/RetailDebriefingProjection.cs` (new static
  projection type beside `RetailFrontendSession`; page composition stays out
  of Godot); tests
  `rebuild/OnslaughtRebuild.Client.Tests/RetailDebriefingProjectionTests.cs`;
  composition wired through
  `rebuild/OnslaughtRebuild.Client/RetailFrontendSession.cs::TryAcceptWonHandoff`
  (existing method, lines 667–683).
  Predecessor evidence: `CFEPDebriefing__Render.md` (`0x00456DD0`),
  `CFEPDebriefing__TransitionNotification` (`0x00457CF0`),
  `FrontEnd.cpp:67` / `:233–269`, and the already-pinned FillOut snapshot plus
  `RetailCareerGrades` law.
  Scope: project mission status, primary/secondary objective summaries, and
  win-only rank letter from a `RetailEndLevelSnapshot`, plus the two consumed
  Goodie-latch values needed by later transient effects. It explicitly excludes
  a kill readout and visible Goodie list because retail Render contains neither.
  Dependency (resolves rev A finding 4): the input consumed today is
  `RetailFillOutEndLevelData.ForLevel100Won()` — the canned pre-arm 1.0 f
  rank/goodie snapshot (`RetailFillOutEndLevelData.cs:22-25,267-286` records
  that score/time are unclaimed on a first play) that
  `RetailFrontendSession.cs:678` already applies. That is a synthetic
  projection, not parity. **N3 is the predecessor for any parity upgrade:**
  once N3 joins the input-only chain to its own live stores, the joined live
  EndLevelData snapshot replaces the canned one as N1's input, upgrading the
  slice toward parity without changing the projection owner. Until then N1
  ships labelled synthetic.
  Explicitly excludes FMV playback and any new video infrastructure (that
  dependency is recorded in §4 G1 as its own future question) and excludes the
  G7 overlay-text capture (standalone recorded gap, owned by no card).
  Non-overlap: does not touch Core mission/career owners (N3's file) or the
  Godot delivery wire (N2's).

- **N2 — Godot host Won-handoff wiring gate.**
  Single architecture (removes rev A's "extract … or stand up …" alternative):
  **extract the tick-seam predicate into a Client-owned, testable type.**
  Ownership (one exact triple): production
  `rebuild/OnslaughtRebuild.Client/RetailWonHandoffGate.cs` (new type
  exposing the predicate that today lives inline in
  `rebuild/OnslaughtRebuild.Godot/FirstFlightGame.cs::TryAcceptWonFrontendHandoff`,
  lines 829–838, with the `AcceptWonHandoff` call at line 837, and with
  `FirstFlightGame` delegating to it — the delegation edit is part of this card
  and changes no behavior); tests
  `rebuild/OnslaughtRebuild.Client.Tests/RetailWonHandoffGateTests.cs`.
  Predecessor evidence: session-level coverage ends at
  `RetailFrontendSession.TryAcceptWonHandoff` (`RetailCampaignFlowTests`);
  `OnslaughtRebuild.slnx` omits the Godot project.
  Scope: one gate proving a `FrontEndHandoffReady` snapshot produces exactly
  one accepted `AcceptWonHandoff` delivery and no premature deliveries on
  `SuccessCountdown`. Non-overlap: N1 composes the destination page; N2 only
  proves the delivery wire; N3 stays inside one Core test file.

- **N3 — Join the input-only chain to its own EndLevelData stores.**
  Ownership (one exact triple):
  `rebuild/OnslaughtRebuild.Core.Tests/Level100PlayerInputWonHandoffTests.cs`
  (fixture already shared via `Level100ChainRunFixture` in
  `Level100FullChainTests.cs`); production owners observed are the existing
  `IScript::AddScore` / flight-store paths in
  `rebuild/OnslaughtRebuild.Core` (PARITY rows `IScript::AddScore` incrementer
  `0x005343cb`, `IScript::EnableFlightMode` `+0x58c` store — already pinned,
  no production change expected); test additions land only in the one named
  test file.
  Predecessor evidence: PARITY rows above;
  `Level100WonCareerHandoffTests.AddScore_FirstPlayWonWritesCGamePlusF4` /
  `EnableFlightMode_FirstPlayWonWritesCBattleEnginePlus58C` prove the stores on
  the script-driven mission only. Scope: assert the same two live stores (and
  the resulting score-time-arm band) from the SimInput-only fixture's
  end-state, closing the last synthetic-input hop in the completion chain.
  Downstream role: **N3 feeds N1's parity upgrade** (joined live snapshot
  replaces the canned pre-arm input). Non-overlap: N1/N2 touch Client/Godot
  presentation and wiring; N3 touches one Core test file.

Deliberately not nominated (recorded in §4): the self-comparison hygiene item
(G5), loss-sentence text resolution (G6), the overlay-text anchor (G7 —
standalone recorded gap, owned by no card), the AppCore runtime-grade law test
(G8), and the RestartLoopRunLevel timeout question below (open question, not
settled law).

---

## 6. Reuse accounting

- **REUSED: 16 evidence owners** (§1.1 table), plus reviewed integration
  `608d93bd`, two sibling-card result sets (`t_be6f5191`, `t_356b980e`), and
  the PARITY mutation-kill receipts.
  Every retail claim in §1 is quoted from retained tracked evidence; no
  address in this report was newly derived. Rev D additionally recomputed the
  §2 inventory against fetched current main: 22 Client `*Level100*Tests.cs`
  owners, `InteractiveSessionTests` 44/41,
  `Level100HudPresentationTests` 18/17, `Level100AudioCatalogTests` 30/29,
  `SimulationTests` 46 total (42 Facts + 4 Theories), `Level100MissionTests` 16,
  `Level100SkipPanningTests` 14, and
  `MissionScriptGoodieStateSaveCodecTests` 15. The AudioCatalog declaration
  census is anchored and excludes 11 source-string `public void` tokens from
  its 41 raw token lines. This is static source inspection, not a retail or
  behavioral measurement; the reviewed reticle GREEN remains managed/headless,
  not a native human playthrough.
- **EXTENDED: 0** — no retained receipt needed reinterpretation.
- **NEW_MEASUREMENT: 0** — no product/rebuild test or binary was run and no
  capture was taken; the required `npm run test:docs` publication gate is
  documentation validation, not retail-behavior evidence. Every open
  falsifier that retained evidence could not answer is listed in §4/§5/§7
  rather than measured.

---

## 7. Open questions and boundaries

- **RestartLoopRunLevel in-loop timeout arm.** The 2026-08-22 pristine re-read
  records three global-time comparisons with a force-win when state == 4.
  Whether shipped builds can reach it outside demo/stress conditions is not
  settled by retained evidence; cheapest falsifier is a controlled
  copied-runtime probe held at `GAME_STATE_PLAYING` past the smallest
  threshold. No rebuild owner exists; not nominated this cycle.
- **World-110 secondary objectives.** Level 100 ships four primaries and zero
  secondaries; that law is unchanged. Current-main managed Core now includes
  `SimulationTests.World110Session_CrossesNative88AndStepsDeterministically`
  (a world-110 session constructs, records secondary[1] Failed, and idle-steps
  deterministically) plus the two `Level100MissionTests` indexed-slot store
  tests. Those are managed/headless Core admission and store-state laws. They
  do **not** claim a native-88 `SecondaryObjectiveFailed` capability, a native
  Godot playthrough, or authored world-110 content. Historical sibling
  `t_356b980e` recorded a then-current world-110 init throw; that receipt is
  not restated here as live current-main behavior.
- **Iceberg store-0 / first-play elapsed and score** remain unclaimed exactly
  as recorded on `RetailFillOutEndLevelData`; inherited, unchanged.
- **Boundaries honored:** read-only analysis; one tracked report; worktree
  only; no pristine/install/save/G:/H:/D: write; no Ghidra/browser mutation;
  no hard delete; no model/provider pin; no code behavior change.
