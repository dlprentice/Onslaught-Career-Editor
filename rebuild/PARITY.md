# Rebuild parity contract

Status: active — what "1:1 behavioral and experiential parity" means operationally
Last updated: 2026-08-19 (Level 100 UpdateGoodieStates new_goodie_count latch).
Evidence: SOURCE — authority order and the known divergences are
recorded in `PROVENANCE.md` plus the Lost-countdown row of this table; gate capabilities are MEASURED claims of the
tracked harnesses named in the table. Every row of *Carried retail contracts*
is MEASURED: its anchor re-derived from the pristine specimen and its mutation
kill observed.
Specimen: `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
(the retail addresses cited in the divergences table are from the pristine
specimen; the installed BEA.exe is deliberately patched).
Summary: the gradeable dimensions of parity, the gate each currently has (or
lacks), and the standing exceptions. This document names the gap; it does not
claim the gap is closed.

## Authority order (from PROVENANCE.md)

> **Port Stuart's shape first. Cite the file and line. Override from bytes
> only where measurement proves divergence.**

The pinned `references/Onslaught` source is the architecture and intent
authority. The pristine retail specimen (`74154bfa…`) is the behavior
authority. Where they disagree, the shipped bytes win — but only after a
measurement proves the divergence, and the divergence is recorded.

## Known divergences (measured)

| Divergence | Stuart source | Shipped bytes | Where recorded |
|---|---|---|---|
| `InJetMode` | 0.3 s | 0.5 s | PROVENANCE.md |
| `CGame::DeclareLevelLost` countdown | 5.0 s | 2.0 s | this table (`0x0046F4A8`) |
| `CGame::FillOutEndLevelData` score below D | `game.cpp:1011-1024` stores −1 then clamps to 0 then 0.001 | `0x0046d772` stores 0 and jumps to `0x0046d79b`, skipping `0x3a83126f` | this table |
| `CPanCamera` length | Stuart value | 6.0 | PROVENANCE.md (VA 0x004198D0, vtable 0x005D92A8) |
| Weapon resource path | pinned path | differing path | PROVENANCE.md |

These are exceptions to record precisely, not templates for loose porting.

## Carried retail contracts — entity, owner, implementation, test

Recorded 2026-08-17, with the Pulse Cannon increment, end-level countdown,
ReCalcLinks, FillOut, and FrontEndHandoffReady career-handoff rows added 2026-08-18. Every retail anchor below was **re-derived from the
pristine specimen** for this table (PE headers parsed directly; flat mapping
file offset = VA − 0x400000 for `.text`/`.rdata`/`.data`, whose raw ends are
0x005D8000 / 0x00622000 / 0x00661000 — `.rsrc` is **not** flat and 0x00672FD0 is
bss). Every row's mutation kill was **measured**: the named implementation was
changed to the plausible wrong value, the named test was observed to fail, the
owner was restored and verified byte-identical by SHA-256, and the test was
observed to pass. `Cases` is the number of test cases
`--filter FullyQualifiedName=<test>` selects, measured — it is the
`expectedTests` a rebuild-parity gate needs.

Owner paths are relative to the repository root; test names are relative to
`rebuild/OnslaughtRebuild.Core.Tests/` and the
`OnslaughtRebuild.Core.Tests` namespace.

> **Receipts.** The 17 mutation records behind this table — one per row plus the
> one deliberate `SURVIVED` control — live at
> `local-lab/rebuild-parity-mutation-kills-2026-08-17/`, with
> `mutation-results.json` (per row: target test, mutation meaning, every failing
> test observed, and `ownerSha256Before`/`After`), the `mutate.py` harness that
> produced them, the read-only specimen reader used to re-derive every anchor
> here, and `MANIFEST.sha256`. `local-lab/` is **ignored by git and invisible to
> a fresh clone**, so a clone sees this table's claims without its evidence;
> `local-lab/INDEX.md` carries the entry. Re-deriving a row costs one narrow
> `--filter` run, so treat a missing receipt as a reason to re-measure rather
> than to trust the table.

| Retail entity | Anchor, and what the bytes say | Owner | Implementation | Test | Cases | Mutation that was killed |
|---|---|---|---|---|---|---|
| `CBattleEngineJetPart::GetFriction` slow-flight gate | `0x00411B39` `d81dd88b5d00` = `fcomp dword ptr [0x005D8BD8]`; that dword is `00 00 c0 3f` = `1.5f`; `test ah,1` at `0x00411B41` | `rebuild/OnslaughtRebuild.Core/Simulation.cs` | `Simulation.JetFrictionNumerator` | `RetailJetFrictionTests.CoreLadder_GatesTheInterpolatedArmAtOnePointFive` | 1 | gate back to `1_000` (retail 1.0) |
| `CBattleEngineJetPart::GetFriction` ladder | `0x00411AA0`; `0x005D8CC4`=0.99f, `0x005D8B9C`=0.98f, `0x005D8568`=1.0f, `0x005D8CC0`=3.0f, `0x005D8574`=0.01f; source `BattleEngineJetPart.cpp:609-635` | `rebuild/OnslaughtRebuild.Core/RetailJetFriction.cs` | `RetailJetFriction.GetFriction` | `RetailJetFrictionTests.GetFriction_GatesTheInterpolatedArmAtOnePointFive` | 4 | `SlowFlightSpeed` written as `1.0f` |
| `CCareer::SetSlot` | `0x004214EB` `cmp eax,0x100` / `jge`, over a store indexed `sar edx,5` into `[esi+edx*4+0x2408]` — a 1024-bit array reachable only to 256 | `rebuild/OnslaughtRebuild.Core/RetailCareerProgress.cs` | `RetailCareerSlots.SetSlot` | `RetailCareerProgressTests.Slots_GuardStopsAt256WhileTheStoreHolds1024` | 1 | guard raised to the store's real 1024 |
| `CCareerNode::SetBaseThingExistTo` | `0x0041B777` `mov edx,1`; `0x0041B77E` `sar eax,5`; `0x0041B781` `and ecx,0x1f`; `0x0041B786` `shl edx,cl` — bit 0 is the low bit | `rebuild/OnslaughtRebuild.Core/RetailCareerNodes.cs` | `RetailCareerNode.SetBaseThingExistTo` | `RetailCareerNodesTests.SetBaseThingExistTo_AddressesTheWordAndBitRetailDoes` | 5 | bits numbered from the top of the word |
| `CCareer::Load` kill-counter clamp | `0x00421245`/`0x0042124B` read `[ebx+0x23f4]` and `[ebx+0x23f8]` — **two** words only; `0x0042126A` `cmp eax,-0x40`, `0x0042126F` `cmp eax,0x40`, else `xor eax,eax` | `rebuild/OnslaughtRebuild.Core/RetailCareerKillCounters.cs` | `RetailCareerKillCounters.NormaliseOnLoad` | `RetailCareerKillCountersTests.NormaliseOnLoad_LeavesTheOtherThreeCountersAlone` | 1 | normalise all five counter words |
| `CEventManager::AddEvent(CScheduledEvent*)` | `0x0044B32E` `0fbf4604` = `movsx eax, word ptr [esi+4]` — the event number is int16 | `rebuild/OnslaughtRebuild.Core/RetailEventScheduler.cs` | `RetailEventScheduler.AddEvent` | `RetailEventSchedulerTests.AddEvent_StoresTheEventNumberAsSignedSixteenBits` | 1 | store the `int` the source signature advertises |
| `CPCController::GetAnalogueLeftX` | `0x0051465E` `fild dword ptr [eax]` then `0x00514660` `fmul dword ptr [0x005DC6E4]`, that dword `6f12833a` = `0.001f`; `0x3EB851EC` (`0.36f`) occurs **zero** times in the image, so `PCController.cpp`'s dead-zone stage never shipped | `rebuild/OnslaughtRebuild.Core/RetailAnalogueControls.cs` | `RetailAnalogueControls.NormalizeLeftX` | `RetailAnalogueControlsTests.NormalizeLeftX_MultipliesByTheRoundedReciprocalNotDividesByAThousand` | 5 | implement `PCController.cpp:155`'s `/1000.0f` |
| `CBattleEngine::GetInterpolatedEulerOrientation` seam wrap | `0x0040D660`; `0x005D85E4`=+1.5707963705062866, `0x005D85C8`=−1.5707963705062866, `0x005D85E0`=6.2831854820251465; no store between the wrap and its use | `rebuild/OnslaughtRebuild.Core/RetailBattleEngineInterpolation.cs` | `RetailBattleEngineInterpolation.AdjustedOldAngle` | `RetailBattleEngineInterpolationTests.AdjustedOldAngle_StaysWideAndThatIsObservable` | 1 | round the wrapped angle back to float |
| `CBattleEngine::HandleHostileEnvironment` | `0x0040DCE0` `fld [0x00672FD0]`, `0x0040DCEF` `fsub [esi+0x510]`, `0x0040DCF5` `fcomp [0x005D85D8]` = 5.0f, `test ah,0x41` — strictly greater, on the **unrounded** difference | `rebuild/OnslaughtRebuild.Core/RetailBattleEngineAugment.cs` | `RetailHostileEnvironment.ShouldWarn` | `RetailBattleEngineAugmentTests.ShouldWarn_ComparesTheUnroundedDifference` | 1 | narrow the elapsed difference to float |
| `CBattleEngineWalkerPart::GetWeaponAmmoCount` | `0x00414470`; `0x0041449D` `df7c2404` = bare `fistp qword ptr [esp+4]` under `/QIfist`, so it **rounds to nearest even** where `BattleEngineWalkerPart.cpp:854` casts | `rebuild/OnslaughtRebuild.Core/RetailWeaponStores.cs` | `RetailWeaponStoreReadouts.AmmoCount` | `RetailWeaponStoresTests.AmmoCount_RoundsToNearestEvenWhereTheSourceTextTruncates` | 6 | implement the source's truncating `(SINT)` cast |
| `CMovieCamera::GetZoom` | `0x0041A681` `fmul dword ptr [0x005D9338]`, that dword `610b363c` = `float(1/90)` and occurs **once** in the whole image, then `0x0041A687` `fmul [0x005D85EC]` = 0.5f — two multiplies where `Camera.cpp:650` writes two divides | `rebuild/OnslaughtRebuild.Core/RetailCameraLaws.cs` | `RetailMovieCameraZoom.GetZoom` | `RetailCameraLawsTests.MovieCameraZoom_MultipliesByTheRoundedReciprocalOfNinety` | 4 | implement `(fov/90)/2` |
| `CBattleEngine::Gravity` | `0x004074D0`; jump table `0x00407520` = {`0x004074FF`,`0x004074FF`,`0x004074FF`,`0x004074E8`} and `0x00407530` = {`0x00407506`,`0x004074FF`,`0x004074FF`,`0x0040750D`}, so **index 0** takes `0x005D8BAC` = `6f12033b` = 0.002f. Index 0 is `MORPHING_INTO_WALKER` (`BattleEngine.h:32`), not the walker | `rebuild/OnslaughtRebuild.Core/RetailBattleEngineGravity.cs` | `RetailBattleEngineGravity.Gravity` | `RetailBattleEngineGravityTests.Gravity_WalksBothJumpTables` | 6 | read the header as walker-first |
| `CBattleEngineWalkerPart::CanWeaponFire` | `0x0041463C` `8b889c000000` = `mov ecx,[eax+0x9C]` then `test ecx,ecx` / `je`. The jet's body `0x00412570`–`0x0041260B` contains the displacement `9c 00 00 00` **zero** times; the walker's contains it once | `rebuild/OnslaughtRebuild.Core/RetailWeaponSelection.cs` | `RetailWeaponFireGate.CanWalkerWeaponFire` | `RetailWeaponSelectionTests.CanWalkerWeaponFire_AddsTheActiveGateTheJetDoesNotHave` | 3 | share one body across both chassis |
| `CBattleEngineWalkerPart::GoingIntoWater` arm selector | `0x00413A70`; selector at `0x00413ABF` against `0x005D8CB4` = `9a99993e` = 0.3f, on the unrounded height | `rebuild/OnslaughtRebuild.Core/RetailWalkerWaterEntry.cs` | `RetailWalkerWaterEntry.GoingIntoWater` | `RetailWalkerWaterEntryTests.GoingIntoWater_TakesTheLowArmAtExactlyTheMarginAboveWater` | 1 | make the selector inclusive; **and** hard-wire one arm |
| `CBattleEngineJetPart::AutoLevel` | `0x00412900`; `0x0041293A` `fcomp dword ptr [0x005D8C60]`, that dword `0bd7233c` = 0.010000000707805157 = `float(0.1f)²` — **not** `0.01f`, which is `0ad7233c` at `0x005D8574` | `rebuild/OnslaughtRebuild.Core/RetailJetAutoLevel.cs` | `RetailJetAutoLevel.AutoLevel` | `RetailJetAutoLevelTests.AutoLevel_GatesOnTheSquaredManoeuvreSpeedWhenGrounded` | 5 | write the threshold as plain `0.01f` |
| `CChunkReader::Read` / `::Skip` over-read | `0x00423965` `imul esi,[esp+0x10]` then `0x00423971` `add edx,esi` — the charge is **unclamped**; `0x00423998` `sub eax,esi` wraps unsigned and `0x0042399A` resets the accounting to `Size`, so `CDXMemBuffer::Skip`'s `size>0` guard drops it | `rebuild/OnslaughtRebuild.Core/RetailChunkReader.cs` | `RetailChunkReader.Skip` | `RetailChunkReaderTests.Skip_AfterOverReadingAChunkIsASilentNoOpRatherThanARewind` | 1 | clamp the over-read charge at the chunk size |
| `CWeapon__AdvanceChargeProgressIfAnySlotAssigned` | `0x005068F0`; `0x005DB358`=`00 00 c8 43`=`400.0f`; `test ah,1` / `je` then `fld [record+8]` / `fadd [weapon+0x60]`. CanCharge scan starts at `record+0x10`. Level 100 `Pulse Cannon Pod` @`0x17463` of `default physics.dat` (`e1fb3ded…ada14`) has rate `0x41200000`=`10.0f` and levels 0+1 present, so ten 20 Hz samples fill MaxCharge 100 | `rebuild/OnslaughtRebuild.Core/RetailWeaponCharge.cs` and `rebuild/OnslaughtRebuild.Core/Level100PulseCannonCharge.cs` | `RetailWeaponCharge.Charge` | `RetailWeaponChargeTests.Charge_AddsTheRecordRateWhileBelowFourHundred` | 1 | cap written as `MaxCharge` (`100.0f`); **and** Pulse Cannon rate written as `1.0f` |
| `CGame::DeclareLevelLost` / `::DeclareLevelWon` countdown | `0x0046F4A8` `c7 43 48 00 00 00 40` = `mov [ebx+0x48], 0x40000000` = `2.0f`; `0x0046F338` `c7 43 48 00 00 a0 40` = `5.0f` after `cmp eax,0x2E5` / `0x2E6` miss. Source `game.cpp:75` writes `GAME_COUNT_WHEN_LOST_OR_DRAW 5.0f` for both | `rebuild/OnslaughtRebuild.Core/RetailGameEndCountdown.cs` and `rebuild/OnslaughtRebuild.Core/Level100MissionTiming.cs` | `RetailGameEndCountdown.LostTicks` | `RetailGameEndCountdownTests.TutorialBroken_StartsTheTwoSecondLostCountdown` | 1 | Lost written as the source `5.0f` (`0x40A00000`) |
| `CCareer::ReCalcLinks` after Level 100 Won | `0x0041BDF0` calls `0x004496E0`; world 100 `level_structure[0]` is lower child node 1 / world 110 and higher `mToNode=-1`. Level 100 ships four primaries and no secondaries, so the predicate is the no-objectives FALSE; the lower link still completes (`Career.cpp:488-490`) and the dummy higher stays `CN_NOT_COMPLETE` | `rebuild/OnslaughtRebuild.Core/RetailCareerReCalcLinks.cs` | `RetailCareerCampaign.ApplyUpdate` | `RetailCareerReCalcLinksTests.Level100Won_UnlocksWorld110EvenThoughTheSecondaryPredicateIsTheNoObjectivesFalse` | 1 | require `IsAllSecondaryObjectivesComplete` for the lower child too |
| `CGame::FillOutEndLevelData` Level 100 Won snapshot | `0x0046D470`; `mWorldFinished=100`, `mFinalState=5`, ten unset secondary statuses. `game.cpp:1028` `if (GetNumSecondaryObjectives())` is false, so the 0.4/0.6 ranking clamp is skipped even though `0x004496E0` would return FALSE | `rebuild/OnslaughtRebuild.Core/RetailFillOutEndLevelData.cs` | `RetailFillOutEndLevelData.AfterSecondaryRankingClamp` | `RetailFillOutEndLevelDataTests.Level100Won_DoesNotClampRankingBecauseThereAreNoSecondaries` | 3 | apply the failed-secondary `0.6` cap when the authored count is 0 |
| `CGame::FillOutEndLevelData` Level 100 Won primary statuses | `0x0046D470` copies ten primary `GetStatus()` words: four `MOS_COMPLETE=1` then six unset — not the rebuild mission enum `Level100PrimaryObjectiveStatus.Complete=2`. Secondaries stay unset | `rebuild/OnslaughtRebuild.Core/RetailFillOutEndLevelData.cs` | `RetailFillOutEndLevelData.ForLevel100Won` | `RetailFillOutEndLevelDataTests.Level100Won_SnapshotCarriesFourMosCompletePrimariesNotTheMissionEnumTwo` | 1 | write mission-enum `Complete=2` into the primary table |
| `CGame::FillOutEndLevelData` then `CCareer::Update` from Level 100 `FrontEndHandoffReady` | After the already-pinned Won 5.0 f countdown, `RestartLoopRunLevel` calls FillOut `0x0046D470` then Update `0x0041BD00`. Mission `FrontEndHandoffReady` is that seam: `ForLevel100Won()` then `ApplyUpdate`. No new secondaries | `rebuild/OnslaughtRebuild.Core/Level100WonCareerHandoff.cs` | `Level100WonCareerHandoff.TryApply` | `Level100WonCareerHandoffTests.FrontEndHandoffReadyAfterWon_AppliesFillOutAndUnlocksWorld110` | 1 | skip `ApplyUpdate` on the handoff |
| Level 100 player-input Won to `FrontEndHandoffReady` | GOAL.md: one `Level100ChainRunFixture` reaches `Won` by `SimInput` alone. After `SuccessCountdown`, `Step(SimInput.Idle)` for `RetailGameEndCountdown.WonTicks` lands `FrontEndHandoffReady` and `ApplyUpdate` unlocks world 110. Never `QueueExternalEvent`. First-play elapsed / iceberg-kill store-0 / secondaries / ChargeWeapon stay unclaimed | `rebuild/OnslaughtRebuild.Core/Level100Mission.cs` | `Level100Mission.AdvanceTick` | `Level100PlayerInputWonHandoffTests.SimInputOnlyWon_AfterSuccessCountdown_ReachesFrontEndHandoffAndUnlocksWorld110` | 1 | stop the idle steps before the overlay elapses |
| `CCareer::Update` Lost skip at Level 100 handoff | Lost is 4; `cmp eax,5` at `0x0041BD06` skips the 32-dword copy. `TryApply` returns false even if `FrontEndHandoffReady` is claimed. Broke-Tutorial never leaves `FailureMenuReady`. No new secondaries | `rebuild/OnslaughtRebuild.Core/Level100WonCareerHandoff.cs` | `Level100WonCareerHandoff.TryApply` | `Level100WonCareerHandoffTests.LostDoesNotApplyFillOutEvenIfFrontEndHandoffReadyIsClaimed` | 1 | drop the Won check on `TryApply` |
| `CGame::FillOutEndLevelData` then `CCareer::Update` Level 100 first-play slots | First-play `SetSlotSave` writes `SLOT_TUTORIAL_1..4` (63..66). FillOut copies those 32 words; `ApplyUpdate` assigns them over career `mSlots`, so a leftover bit dies. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailFillOutEndLevelData.cs` | `RetailFillOutEndLevelData.FirstPlayTutorialSlotWords` | `Level100WonCareerHandoffTests.FrontEndHandoffReadyAfterWon_OverwritesCareerSlotsFromFillOutTutorialBits` | 1 | `ForLevel100Won` carries empty slot words |
| `CGame::FillOutEndLevelData` Level 100 Won ranking | `game.cpp:967` stores `mRanking=1.0f` before the score-time arm. Level 100's secondary count is 0, so the 0.4/0.6 clamp never rewrites it. First-play elapsed and score stay unclaimed | `rebuild/OnslaughtRebuild.Core/RetailFillOutEndLevelData.cs` | `RetailFillOutEndLevelData.ForLevel100Won` | `RetailFillOutEndLevelDataTests.Level100Won_SnapshotRankingIsThePreClampOnePointZero` | 1 | default ranking written as the failed-secondary `0.6` cap |
| `CGame::FillOutEndLevelData` Level 100 score-time arm | Last LoadWorld is outer RLWD. `0x0046d638` `fld [this+0x10c]` / `fsub [this+0x108]` / `fcomp 0.0` / `test ah,0x41` / `jne 0x0046d79b`. RLWD `+0x147ba/+0x147be` = 300.0 / 500.0 so the arm is live. Zero score vs last-wins D=70 stores 0 at `0x0046d772` (not pre-arm 1.0, not source 0.001). First-play elapsed and score stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailFillOutEndLevelData.cs` | `RetailFillOutEndLevelData.AfterScoreTimeArm` | `RetailFillOutEndLevelDataTests.Level100Won_ScoreTimeArmRewritesAZeroScoreToZeroBecauseRlwdDeltaIsPositive` | 1 | invent the skip (leave pre-arm 1.0f) |
| `CGame::FillOutEndLevelData` Level 100 score-percentage last-wins | Last LoadWorld stores RLWD `+0x147c2` = 1.0 at `CGame+0x110` (`0x0050d301` `fstp [0x008a9ba8]`). Not the `LoadLevel` leftover 0.5. Mid-band elapsed therefore does not scale a 140 score. First-play elapsed and score stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailFillOutEndLevelData.cs` | `RetailFillOutEndLevelData.Level100ScorePercentage` | `RetailFillOutEndLevelDataTests.Level100Won_ScoreTimeArmDoesNotScaleAMidScoreByElapsedBecauseScorePercentageIsOne` | 1 | adopt the `LoadLevel` leftover `0.5` |
| `CGame::FillOutEndLevelData` Level 100 exact-D score | Independently re-read specimen: `0x0046d724` `jl 0x0046d772` stores 0 only when fistp'd score is strictly below last-wins D=70. Equality interpolates to 0 then `0x0046d791` stores `0x3a83126f` (0.001). First-play elapsed and score stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailFillOutEndLevelData.cs` | `RetailFillOutEndLevelData.AfterScoreTimeArm` | `RetailFillOutEndLevelDataTests.Level100Won_ScoreTimeArmStoresPointZeroZeroOneAtExactLastWinsD` | 1 | skip the 0.001 replacement |
| `CGame::FillOutEndLevelData` Level 100 last-wins S-score | Independently re-read specimen `74154bfa…` + inflated `100_res_PC.aya` `115ede05…2df4`: `0x0050d2f7` `mov [0x008a9b90], edx` from RLWD `+0x147ae` = 210. `0x0046d6e5` / `0x0046d6f9` / `0x0046d707` `jl` so equality stores `0x3f800000` at `0x0046d709`. Not leftover BSWD 1000. First-play elapsed and score stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailFillOutEndLevelData.cs` | `RetailFillOutEndLevelData.Level100SGradeScore` | `RetailFillOutEndLevelDataTests.Level100Won_ScoreTimeArmStoresOneAtExactLastWinsS` | 1 | adopt leftover BSWD 1000 |
| `CGame::FillOutEndLevelData` Level 100 last-wins D-score | Independently re-read specimen: `0x0050d307` `mov [0x008a9b94], edx` from RLWD `+0x147b2` = 70. A fistp'd 70 against leftover BSWD 200 is strictly below D (`0x0046d724` `jl`) and stores 0 at `0x0046d772`. First-play elapsed and score stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailFillOutEndLevelData.cs` | `RetailFillOutEndLevelData.Level100DGradeScore` | `RetailFillOutEndLevelDataTests.Level100Won_ScoreTimeArmUsesLastWinsDSeventyNotLeftoverBswdTwoHundred` | 1 | adopt leftover BSWD 200 |
| `CGame::FillOutEndLevelData` Level 100 first-play base-things | `[0x0085515c]` is 35 (At() membership: 27 type-8 + 6 type-35 + 2 type-37 `CSafeSide`). Store 1 at `0x006728f8+i*4` for `i=0..34`; `35..287` stay 0. Not the materializer's 33. Iceberg player-kill store-0 stays open. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailFillOutEndLevelData.cs` | `RetailFillOutEndLevelData.FirstPlayBaseThingsLeft` | `RetailFillOutEndLevelDataTests.Level100Won_FillOutStoresOneForEachOfThirtyFiveBaseThings` | 1 | adopt the materializer's 33 visible units |
| `CGame::FillOutEndLevelData` Level 100 TF_DYING store-0 | Independently re-read specimen: `0x0046d4d1` `test byte [eax+0x2c],4` / `jne 0x0046d4df` stores 0. Null reader also stores 0. First-play still 1 at 0..34; player iceberg-kill values stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailFillOutEndLevelData.cs` | `RetailFillOutEndLevelData.BaseThingLeftWord` | `RetailFillOutEndLevelDataTests.Level100Won_FillOutStoresZeroWhenBaseThingIsDying` | 1 | store 1 on TF_DYING |
| `CCareer::UpdateBaseWorldExistsStuffForNode` after Level 100 Won | `Career.cpp:443-452` / `519-527`. `level_structure[0][3]==110` is the primary destination; `[0][4]==-1` so the secondary arm does not run. First-play zeros at `35..287` clear Blank's all-1s on world 110. World 100 stays Blank. Iceberg store-0 stays open. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerReCalcLinks.cs` | `RetailCareerCampaign.UpdateBaseWorldExistsStuffForNode` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateCopiesFillOutBaseThingsOntoWorld110` | 1 | skip the copy (leave world 110 bit 35 set) |
| `CGame::FillOutEndLevelData` then `CCareer::UpdateBaseWorldExistsStuffForNode` from Level 100 `FrontEndHandoffReady` | After the already-pinned Won countdown, first-play FillOut copies onto world 110. Mutation is skip `ApplyUpdate` on the handoff. Iceberg store-0 stays open. No new secondaries | `rebuild/OnslaughtRebuild.Core/Level100WonCareerHandoff.cs` | `Level100WonCareerHandoff.TryApply` | `Level100WonCareerHandoffTests.FrontEndHandoffReadyAfterWon_CopiesFillOutBaseThingsOntoWorld110` | 1 | skip `ApplyUpdate` on the handoff |
| `CGame::FillOutEndLevelData` Level 100 first-play kills | Copy five dwords from `player+8` (`0x0046d60f`) if player 0 is live. `CPlayer__ctor` zeros `+8..+18`. Only `0x004d30d0` increments them. A first-play Won that never takes ConfirmedKill is `0,0,0,0,0`. Career `0x0041c180` still `je` world 100. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailFillOutEndLevelData.cs` | `RetailFillOutEndLevelData.FirstPlayThingsKilled` | `RetailFillOutEndLevelDataTests.Level100Won_FirstPlayKillReadoutIsFiveZerosUnlessConfirmedKill` | 1 | write a non-zero authored L100 kill vector |
| `CGame::FillOutEndLevelData` Level 100 player-null kill zeros | Independently re-read specimen: `0x0046d5f9` `mov eax,[ebp+0x2a4]` / `0x0046d5ff` `test eax,eax` / `je 0x0046d61d` stores five zeros at `0x00672e30`. Live player copies five dwords from `player+8` (`cmp eax,0x14`). First-play still has a live player 0. Iceberg store-0 stays open. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailFillOutEndLevelData.cs` | `RetailFillOutEndLevelData.ThingsKilledReadout` | `RetailFillOutEndLevelDataTests.Level100Won_FillOutStoresFiveZeroKillsWhenPlayerPointerIsNull` | 1 | copy leftover words when the player pointer is null |
| `CGame::FillOutEndLevelData` Level 100 Won lost-reason | Independently re-read specimen: `DeclareLevelWon` `0x0046f323` stores 5 at `+0x28` and `0x0046f33a` stores 5.0f at `+0x48` — no store to `+0x114`. FillOut `0x0046d5d0` copies `[ebp+0x114]` to `0x00672e2c`. Init is 0 (`EndLevelData.h:27`). First-play elapsed and score stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailFillOutEndLevelData.cs` | `RetailFillOutEndLevelData.LostReasonWord` | `RetailFillOutEndLevelDataTests.Level100Won_FillOutLostReasonStaysInitZeroBecauseDeclareWonDoesNotWriteIt` | 1 | leftover lost-string id 123 |
| `CGame::FillOutEndLevelData` Level 100 pre-arm score/time | Independently re-read specimen: `0x0046d5af` `mov ecx,[0x00672fd0]` / `0x0046d5bf` `mov eax,[ebp+0xf4]` / `0x0046d5c5` `mov [0x00672e28],ecx` / `0x0046d5cb` `mov [0x00672e24],eax`. Those are the only FillOut stores of `mTimeTaken` / `mScore`. Arm `0x0046d6ff` rewrites `CGame+0xf4` only. First-play elapsed and score stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailFillOutEndLevelData.cs` | `RetailFillOutEndLevelData.ScoreWord` | `RetailFillOutEndLevelDataTests.Level100Won_FillOutScoreAndTimeAreThePreArmCopiesNotTheScaledRewrite` | 1 | leftover score 999 / leftover time 12.5 / post-arm scaled 105 |
| `CCareer::Update` ignores Level 100 primary statuses | FillOut copies four `MOS_COMPLETE=1` primaries, but `CCareer::Update` at `0x0041BD00` never reads that table. Writing mission-enum `Complete=2` does not change the graph | `rebuild/OnslaughtRebuild.Core/RetailCareerReCalcLinks.cs` | `RetailCareerCampaign.ApplyUpdate` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateDoesNotConsultPrimaryStatuses` | 1 | require `MOS_COMPLETE=1` before completing the node |
| `CCareer::Update` Level 100 ranking target | `Career.cpp:396-406` stores `mRanking` only on `GetNodeFromWorldNo(mWorldFinished)`. World 100 gets the already-pinned FillOut 1.0f (grade S). World 110 stays `BlankRanking` `-1.0f` (grade E) and incomplete | `rebuild/OnslaughtRebuild.Core/RetailCareerReCalcLinks.cs` | `RetailCareerCampaign.ApplyUpdate` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateWritesRankingOnlyOnTheFinishedWorld` | 1 | copy the snapshot ranking onto the unlocked child too |
| `CGame::FillOutEndLevelData` then `CCareer::Update` Level 100 ranking target | `FrontEndHandoffReady` applies the already-pinned finished-world ranking: world 100 is 1.0f / S, world 110 stays `BlankRanking` / E. No new secondaries | `rebuild/OnslaughtRebuild.Core/Level100WonCareerHandoff.cs` | `Level100WonCareerHandoff.TryApply` | `Level100WonCareerHandoffTests.FrontEndHandoffReadyAfterWon_StoresFillOutRankingOnlyOnWorld100` | 1 | stamp FillOut ranking onto the unlocked child after `TryApply` |
| `CCareer::Update` Level 100 ranking only-if-greater | `Career.cpp:405-406` stores `mRanking` only when the snapshot is strictly greater. A worse Level 100 replay leaves the already-pinned first-play 1.0f / S. Score-time stays unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerReCalcLinks.cs` | `RetailCareerCampaign.ApplyUpdate` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateDoesNotDowngradeAnExistingBetterRanking` | 1 | assign the snapshot ranking even when it is not greater |
| `CGame::FillOutEndLevelData` then `CCareer::Update` wait for the Level 100 Won countdown | `RestartLoopRunLevel` FillOut at `game.cpp:1552` after the main loop quits; that quit waits for the already-pinned 5.0 f store (`game.cpp:1997-2004`). `CFrontEnd::Init` then calls `CAREER.Update` (`FrontEnd.cpp:67`). `TryApply` returns false on `SuccessCountdown`. Score-time stays unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/Level100WonCareerHandoff.cs` | `Level100WonCareerHandoff.TryApply` | `Level100WonCareerHandoffTests.SuccessCountdownDoesNotApplyFillOutEvenIfWonIsClaimed` | 1 | accept `SuccessCountdown` on `TryApply` |
| `CCareer::UpdateGoodieStates` after Level 100 Won | `0x0041c470`. Training is not an early-out. Re-read on specimen `74154bfa…`: `0x0041c4c7` `83 3a 64` = `cmp [edx], 0x64`; `0x0041de68` `6a 43` = `push 'C'`; `0x0041ea4f` `6a 42` = `push 'B'` (one byte after the note's `0x0041ea4e`); `0x0041f70e` `6a 41` = `push 'A'`. `COMPLETE_LEVEL(100)` stores `GS_NEW=2` on 0 and 8; `GRADE(100) >= C/B/A` stores 78 / 121 / 164. FillOut 1.0f is S so all five unlock. Score-time / base-things / kill totals stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.Update` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateUnlocksTrainingGoodiesForAnS` | 1 | skip `UpdateGoodieStates` after a Won `ApplyUpdate` |
| `CCareer::UpdateGoodieStates` Level 100 grade bands | Same body. Ranking 0.25f is already pinned as C (`'D' - floor(0.25*4)`). `GRADE(100) >= C` unlocks 78; `>= B` / `>= A` stay closed so 121 and 164 stay `GS_UNKNOWN`. Score-time stays unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.Update` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateGradeCUnlocksOnlyTheCTrainingGoodies` | 1 | unlock 121 / 164 on any complete |
| `CCareer::UpdateGoodieStates` Level 100 B-grade band | Same body. Ranking 0.5f is already pinned as B. `GRADE(100) >= B` unlocks 121; `>= A` stays closed so 164 stays `GS_UNKNOWN`. Cite `0x0041ea4f` / `0x0041f70e`. Iceberg store-0 and first-play elapsed stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.Update` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateGradeBUnlocksOnlyThroughTheBTrainingGoodies` | 1 | unlock 164 on B |
| `CCareer::UpdateGoodieStates` Level 100 A-grade band | Same body. Ranking 0.75f is already pinned as A. `GRADE(100) >= A` unlocks 164. Cite `0x0041f70e`. Iceberg store-0 and first-play elapsed stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.Update` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateGradeAUnlocksTheATrainingGoodie` | 1 | skip the A arm |
| `CCareer::UpdateGoodieStates` Level 100 E-grade Won | Same body. Ranking 0.0f is already pinned as E (`0x00421499` `mov al,0x45`). A zero-score FillOut still Wins, so `COMPLETE_LEVEL(100)` writes 0 and 8; `GRADE(100) >= C` stays closed. Cite `0x00421499` / `0x0041de68`. Iceberg store-0 and first-play elapsed stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.Update` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateGradeEUnlocksOnlyTheCompleteTrainingGoodies` | 1 | unlock 78 on any complete |
| `CCareer::UpdateGoodieStates` Level 100 D-grade band | Same body. Ranking 0.001f is already pinned as the score-time exact-D replacement (`0x3a83126f`). That is D (`'D' - floor(0.001*4)`), so `GRADE(100) >= C` stays closed. Iceberg store-0 and first-play elapsed stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.Update` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateGradeDUnlocksOnlyTheCompleteTrainingGoodies` | 1 | treat any ranking above 0 as C |
| `CCareer::UpdateGoodieStates` Level 100 new-goodie latch | Same body. `CountGoodies` (`Career.cpp:670-680`) counts `mState >= GS_NEW`. First-play S raises that count by five; `new_goodie_count` at `0x00662B20` adds the delta (`Career.cpp:895-897`) and `first_goodie` at `0x00662B24` latches because goodie 0 left `GOODIE_NOT_DONE` (`Career.cpp:688 / 899-900`). `mPendingExtraGoodies` and episode instruction marks stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.CountGoodies` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateAddsFiveNewGoodiesAndLatchesFirstGoodie` | 1 | leave the globals at ctor 0 |
| `CCareer::UpdateThingsKilled` after Level 100 Won | `0x0041c180`. `cmp eax,0x64` / `je` at `0x0041c188` still refuses world 100. A non-zero FillOut kill vector does not accumulate. ConfirmedKill increment values stay unclaimed. Iceberg store-0 and first-play elapsed stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerProgress.cs` | `RetailCareerCounters.UpdateThingsKilled` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateDoesNotAccumulateThingsKilledForWorld100` | 1 | drop the equality skip |
| `CBattleEngine::ConfirmedKill` Level 100 allegiance gate | Independently re-read specimen: `0x0040a564` `cmp [eax+0x138],1` / `jne 0x0040a57d` skips `0x004d30d0`. One inbound `E8` at `0x0040a578`. First-play totals stay unclaimed — a Won that never takes this path still snapshots five zeros. Iceberg store-0 stays open. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailConfirmedKill.cs` | `RetailConfirmedKill.Apply` | `RetailConfirmedKillTests.Level100Won_ConfirmedKillDoesNotIncrementWhenThingAllegianceIsNotOne` | 1 | increment even when `+0x138` is not 1 |
| `CBattleEngine::ConfirmedKill` Level 100 incrementer remaining slots | Independently re-read specimen: `0x004d30eb` `test [eax+0x34],0x40000` / `inc [ecx+0x10]`; `0x004d30fa` `test dh,0x40` = `0x4000` / `inc [ecx+0x14]`; `0x004d3105` `test dh,8` = `0x800` / `inc [ecx+0x18]`. First-play totals stay unclaimed. Iceberg store-0 stays open. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailConfirmedKill.cs` | `RetailConfirmedKill.Apply` | `RetailConfirmedKillTests.Level100Won_ConfirmedKillIncrementsSlotTwoOnFlag40000` | 1 | write `0x40000` into slot 0 |
| `CBattleEngine::ConfirmedKill` Level 100 null player-reader skip | Independently re-read specimen: `0x0040a56d` `mov ecx,[ecx+0x574]` / `0x0040a573` `test ecx,ecx` / `je 0x0040a57d` skips `0x004d30d0`. Bytes are a null pointer, not source `ToRead()` dying-flag. First-play totals stay unclaimed. Iceberg store-0 stays open. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailConfirmedKill.cs` | `RetailConfirmedKill.Apply` | `RetailConfirmedKillTests.Level100Won_ConfirmedKillDoesNotIncrementWhenPlayerReaderIsNull` | 1 | increment even when the reader is null |
| `CGame::FillOutEndLevelData` then `CCareer::UpdateGoodieStates` from Level 100 `FrontEndHandoffReady` | After the already-pinned Won countdown, first-play FillOut 1.0f / S unlocks goodies 0, 8, 78, 121, and 164. Cite `0x0041de68` / `0x0041ea4f` / `0x0041f70e`. Score-time / base-things / kill totals stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/Level100WonCareerHandoff.cs` | `Level100WonCareerHandoff.TryApply` | `Level100WonCareerHandoffTests.FrontEndHandoffReadyAfterWon_UnlocksTrainingGoodiesForAnS` | 1 | skip `ApplyUpdate` on the handoff |

Two things this table deliberately does **not** claim. It does not claim these
contracts are graded `REBUILD_READY`: that grade is a campaign artifact and
needs the ceremony in `tools/re_campaign.py`
(`_validate_rebuild_ready_gate`), which stamps owner/test/project SHA-256s, a
`rebuildMapping`, and a re-run of the focused test. And it does not claim replay
coverage. **Sixteen of these twenty-two implementations are unreachable from the
simulation and replay path** — measured, by searching `Simulation.cs`,
`ReplayRunner.cs`, `CommandTape.cs`, `StateHasher.cs` and every `Level100*.cs`
for the owner types: `Simulation.JetFrictionNumerator` is wired,
`RetailWeaponCharge.Charge` is reached from `Simulation.TryChargeWeapon`
when the player holds `SimActions.ChargeWeapon` on the Pulse Cannon Pod,
`RetailGameEndCountdown.LostTicks` is reached from
`Level100Mission.DeclareLost` on the released Broke-Tutorial /
`LevelLostString` path, and `Level100WonCareerHandoff.TryApply` (which
calls the already-pinned `ForLevel100Won` / `ApplyUpdate`) is reached from
`Level100Mission` when `FrontEndHandoffReady` follows Won, including the
SimInput-only chain fixture that never posts a mission event. The Lost-skip
row names the same `TryApply` owner; it does not add a twenty-third
implementation. The first-play slot row names
`FirstPlayTutorialSlotWords` on the already-pinned FillOut owner.
The ranking-target row names the same `ApplyUpdate` owner as the
primary-status skip. The only-if-greater row names that same
`ApplyUpdate` owner; it does not add another implementation. The
FrontEndHandoff ranking-target row names the
same `TryApply` owner as the Won handoff. The SuccessCountdown skip
row names that same `TryApply` owner; it does not add another
implementation. The training-goodie row names
`RetailCareerUpdateGoodieStates.Update`; `ApplyUpdate` is the
already-pinned caller. The grade-band row names that same
`Update` owner; it does not add another implementation. The
B-grade row names that same `Update` owner; it does not add
another implementation. The A-grade row names that same
`Update` owner; it does not add another implementation. The
E-grade Won row names that same `Update` owner; it does not
add another implementation. The D-grade row names that same
`Update` owner; it does not add another implementation. The
new-goodie latch row names `CountGoodies` on that same owner;
`mPendingExtraGoodies` stays unclaimed. The
world-100 kill-skip row names `RetailCareerCounters.UpdateThingsKilled`;
`ApplyUpdate` is the already-pinned caller. The
FrontEndHandoff goodie row names the same `TryApply` owner as the
Won handoff. The score-time arm row names `AfterScoreTimeArm` on
the already-pinned FillOut owner; it does not rewrite
`ForLevel100Won`. The score-percentage last-wins row names
`Level100ScorePercentage` on that same FillOut owner. The
exact-D row names the same `AfterScoreTimeArm` owner; it does
not rewrite `ForLevel100Won`. The last-wins S-score row names
`Level100SGradeScore` on that same FillOut owner. The last-wins
D-score row names `Level100DGradeScore` on that same FillOut
owner. The ConfirmedKill allegiance row names
`RetailConfirmedKill.Apply`; first-play totals stay unclaimed.
The remaining incrementer-slot row names that same
`Apply` owner; it does not rewrite first-play totals.
The null player-reader row names that same `Apply`
owner; first-play still has a live player 0.
The TF_DYING store-0 row names `BaseThingLeftWord` on the
already-pinned FillOut owner. The player-null kill-zero row
names `ThingsKilledReadout` on that same FillOut owner;
first-play still has a live player 0. The pre-arm score/time
row names `ScoreWord` / `TimeTakenWord` on that same FillOut
owner; first-play elapsed and `this+0xf4` stay unclaimed.
Charge and the
career graph are not in `StateHasher` because they do not yet change fire,
movement, or any other hashed field. So no cold-start or
full-chain trace can reach the other sixteen, and the focused test is the
only falsifier they have. That is exactly
the precedent the jet-friction row set: a green replay suite there was
*vacuous* with respect to the constant it was supposed to guard, because the
jet throttle caps below the gate's band. The seventeenth through thirty-second
rows' mutation kills were measured on 2026-08-18 and 2026-08-19 in this worktree; they are
not among the 17 files
under `local-lab/rebuild-parity-mutation-kills-2026-08-17/`.

## Parity dimensions and their gates

| Dimension | What it means | Current gate | What the gate does / does not prove |
|---|---|---|---|
| **Deterministic sim state** | Identical tick-by-tick simulation given identical inputs | Core cold-start + full-chain tests, `--expect` trace hashes | Proves determinism and self-consistency. Does NOT prove retail equality — retail has no tape to replay against |
| **Visual frame** | Rendered output matches retail within tolerance | `Capture-Frontend.ps1 -Plan mainmenu` + `score_frontend_capture.py` + `frontend-regions-*.json`, `gameplay-regions-level100.json` | Proves region-level visual regression against captured retail references. The JSON thresholds are **regression ceilings, not parity claims** (rebuild README is explicit) |
| **Audio** | Playback behavior matches retail | None (no automated audio gate) | Not gradeable today |
| **Timing / feel** | Response latency, animation cadence feel equivalent | None dedicated | Not gradeable today; 20 Hz step + floor semantics are the strongest proxy |
| **Content completeness** | All retail content reachable/present | Materializer hash checks (200+ pinned inputs), level-100 slice | Proves the retail inputs consumed are byte-exact. Does NOT prove every level plays |

## The honest reading

The lane runs a scoring harness that is documented as *not* measuring the
thing the lane exists to achieve. Visual parity gates are regression
ceilings; there is no *whole-run* gate today that compares rebuild behavior to
retail behavior directly, because retail is not automatable in the same
harness. This gap is named here so it is not mistaken for closure.

What the table above adds is narrower and real: **per-contract** gates that do
compare rebuild behavior to retail behavior, because the expected value in each
is read out of the pristine specimen rather than out of the rebuild. Twenty
laws is not parity. It is the first set of rows where a wrong rebuild is
mechanically detected instead of merely plausible-looking, and the mutation kill
is what distinguishes the two.

## What "done" would require (per dimension)

- Sim: a retail-derived expected-trace source (e.g. a verified capture of
  retail's own sequence) or an accepted contract per system.
- Visual: measured tolerance windows per region against retail frames, not
  just self-regression.
- Audio: a playback contract (tracks, triggers, volume semantics).
- Timing/feel: a documented comparison protocol (the maintainer's ear is a
  legitimate instrument for feel; it is not a substitute for the others).
- Content: per-level playthrough evidence, not only input hashes.

## Standing rule

No claim of parity may be published from this file's existence. Parity is
per-dimension, measured, and gated — or it is not parity.
