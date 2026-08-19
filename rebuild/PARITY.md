# Rebuild parity contract

Status: active — what "1:1 behavioral and experiential parity" means operationally
Last updated: 2026-08-19 (Level 100 IScript Wait stop-flag stores 1 at 0x0089c800).
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
| `CCareer::Update` Level 100 mNumAttempts skip | `Career.cpp:379-418` never writes `CCareerNode+0x38`. `CCareerNode::Blank` at `Career.cpp:99` / `0x0041B740` is the only store. Leftover 7 on world 100 and 11 on world 110 survive first-play S even though Complete / Ranking / CareerInProgress change. Isolated Blank ctor 0 does not go through ApplyUpdate. Existing ranking / Complete tests do not name `+0x38`. FrontEndHandoff leftover now names the same 7 / 11 through `TryApply`. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerReCalcLinks.cs` | `RetailCareerCampaign.ApplyUpdate` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateDoesNotIncrementNumAttempts` | 1 | increment the finished node's `mNumAttempts` |
| `CGame::FillOutEndLevelData` then `CCareer::Update` wait for the Level 100 Won countdown | `RestartLoopRunLevel` FillOut at `game.cpp:1552` after the main loop quits; that quit waits for the already-pinned 5.0 f store (`game.cpp:1997-2004`). `CFrontEnd::Init` then calls `CAREER.Update` (`FrontEnd.cpp:67`). `TryApply` returns false on `SuccessCountdown`. Score-time stays unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/Level100WonCareerHandoff.cs` | `Level100WonCareerHandoff.TryApply` | `Level100WonCareerHandoffTests.SuccessCountdownDoesNotApplyFillOutEvenIfWonIsClaimed` | 1 | accept `SuccessCountdown` on `TryApply` |
| `CCareer::UpdateGoodieStates` after Level 100 Won | `0x0041c470`. Training is not an early-out. Re-read on specimen `74154bfa…`: `0x0041c4c7` `83 3a 64` = `cmp [edx], 0x64`; `0x0041de68` `6a 43` = `push 'C'`; `0x0041ea4f` `6a 42` = `push 'B'` (one byte after the note's `0x0041ea4e`); `0x0041f70e` `6a 41` = `push 'A'`. `COMPLETE_LEVEL(100)` stores `GS_NEW=2` on 0 and 8; `GRADE(100) >= C/B/A` stores 78 / 121 / 164. FillOut 1.0f is S so all five unlock. Score-time / base-things / kill totals stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.Update` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateUnlocksTrainingGoodiesForAnS` | 1 | skip `UpdateGoodieStates` after a Won `ApplyUpdate` |
| `CCareer::UpdateGoodieStates` Level 100 grade bands | Same body. Ranking 0.25f is already pinned as C (`'D' - floor(0.25*4)`). `GRADE(100) >= C` unlocks 78; `>= B` / `>= A` stay closed so 121 and 164 stay `GS_UNKNOWN`. Score-time stays unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.Update` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateGradeCUnlocksOnlyTheCTrainingGoodies` | 1 | unlock 121 / 164 on any complete |
| `CCareer::UpdateGoodieStates` Level 100 B-grade band | Same body. Ranking 0.5f is already pinned as B. `GRADE(100) >= B` unlocks 121; `>= A` stays closed so 164 stays `GS_UNKNOWN`. Cite `0x0041ea4f` / `0x0041f70e`. Iceberg store-0 and first-play elapsed stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.Update` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateGradeBUnlocksOnlyThroughTheBTrainingGoodies` | 1 | unlock 164 on B |
| `CCareer::UpdateGoodieStates` Level 100 A-grade band | Same body. Ranking 0.75f is already pinned as A. `GRADE(100) >= A` unlocks 164. Cite `0x0041f70e`. Iceberg store-0 and first-play elapsed stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.Update` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateGradeAUnlocksTheATrainingGoodie` | 1 | skip the A arm |
| `CCareer::UpdateGoodieStates` Level 100 E-grade Won | Same body. Ranking 0.0f is already pinned as E (`0x00421499` `mov al,0x45`). A zero-score FillOut still Wins, so `COMPLETE_LEVEL(100)` writes 0 and 8; `GRADE(100) >= C` stays closed. Cite `0x00421499` / `0x0041de68`. Iceberg store-0 and first-play elapsed stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.Update` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateGradeEUnlocksOnlyTheCompleteTrainingGoodies` | 1 | unlock 78 on any complete |
| `CCareer::UpdateGoodieStates` Level 100 D-grade band | Same body. Ranking 0.001f is already pinned as the score-time exact-D replacement (`0x3a83126f`). That is D (`'D' - floor(0.001*4)`), so `GRADE(100) >= C` stays closed. Iceberg store-0 and first-play elapsed stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.Update` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateGradeDUnlocksOnlyTheCompleteTrainingGoodies` | 1 | treat any ranking above 0 as C |
| `CCareer::UpdateGoodieStates` Level 100 GRADE(110) C-goodie | Same body. `Career.cpp:691` is `if (GRADE(110) >= GRADE_C) SET_GOODIE_NEW(1)`. After a C-grade Level 100 Won, world 110 is still incomplete / BlankRanking so `GRADE` is the already-pinned incomplete `'E'` (`0x0041C3FE`) and goodie 1 stays `GS_UNKNOWN`. Existing C-band tests unlock 78 and do not name goodie 1 or `NewGoodieCount`. Isolated closed concept-art now names 79. A `GRADE(100)` mutation on the S path is not unique versus the latch count of 5. Do not invent the rest of the table. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.Update` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateGradeCLeavesTheWorld110CGoodieUnknown` | 1 | store `GS_NEW` on goodie 1 after the CountGoodies add |
| `CCareer::UpdateGoodieStates` Level 100 GRADE(110) C concept-art goodie closed | Same body. `Career.cpp:770` is `if (GRADE(110) >= GRADE_C) SET_GOODIE_NEW(79)`. After a C-grade Level 100 Won, world 110 is still incomplete / BlankRanking so `GRADE` is the already-pinned incomplete `'E'` (`0x0041C3FE`) and goodie 79 stays `GS_UNKNOWN`. Isolated closed GRADE(110) names 1, not 79. Isolated leftover C 79 names the open store. FrontEndHandoff leftover 79 names TryApply. Existing C-band tests unlock 78 and do not name 79. Skipping `SET_GOODIE_NEW(79)` is not unique versus leftover C concept-art. Do not invent `GRADE(110) >= B` / `A` or a world-110 FillOut. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.Update` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateGradeCLeavesTheWorld110CConceptArtGoodieUnknown` | 1 | store `GS_NEW` on goodie 79 after ApplyUpdate when world 110 is incomplete |
| `CCareer::UpdateGoodieStates` Level 100 leftover GRADE(110) C-goodie | Same body. Leftover world-110 complete + ranking 0.25f (already pinned as C) opens `Career.cpp:691`. Isolated `GradeByteForWorld` already returns C for complete+0.25 and does not go through ApplyUpdate. The closed first-play pin does not name the store. Cold-slice latch tests stay at 5 because they do not seed leftover complete-110. Do not invent a world-110 FillOut. The leftover `COMPLETE_LEVEL(110)` store is not named here. Isolated leftover C concept-art now names 79. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.Update` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateLeftoverWorld110CompleteCUnlocksTheWorld110CGoodie` | 1 | skip `SET_GOODIE_NEW(1)` when `GRADE(110) >= C` |
| `CCareer::UpdateGoodieStates` Level 100 leftover GRADE(110) C concept-art goodie | Same body. `Career.cpp:770` is `if (GRADE(110) >= GRADE_C) SET_GOODIE_NEW(79)`. Leftover world-110 complete + ranking 0.25f opens that store. Isolated leftover C names 1, not 79. Isolated leftover C CountGoodies is now 6 because 79 is also New; skip `SET_GOODIE_NEW(79)` is not unique versus that count. Isolated leftover 14 CountGoodies uses ranking 0.0f so `GRADE(110) >= C` stays closed. Isolated first-play closed GRADE(110) names 1; isolated first-play closed concept-art names 79 at `GS_UNKNOWN`. World 110 is in the cold slice. FrontEndHandoff leftover of this seed now names 79 through `TryApply`. Do not invent `GRADE(110) >= B` / `A` or a world-110 FillOut. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.Update` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateLeftoverWorld110CompleteCUnlocksTheWorld110CConceptArtGoodie` | 1 | skip `SET_GOODIE_NEW(79)` when `GRADE(110) >= C` |
| `CCareer::UpdateGoodieStates` Level 100 COMPLETE_LEVEL(110) goodie | Same body. `Career.cpp:704` is `if (COMPLETE_LEVEL(110) ) SET_GOODIE_NEW(14)`. After a C-grade Level 100 Won, world 110 is unlocked but still incomplete, so goodie 14 stays `GS_UNKNOWN`. Existing GRADE(110) tests name goodie 1 and do not name goodie 14. Leftover complete-110 plus ranking 0.0f now names the open store. Do not invent the rest of the table. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.Update` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateLeavesTheWorld110CompleteGoodieUnknown` | 1 | store `GS_NEW` on goodie 14 after the CountGoodies add |
| `CCareer::UpdateGoodieStates` Level 100 leftover COMPLETE_LEVEL(110) goodie | Same body. Leftover world-110 complete + ranking 0.0f (already pinned as E) opens `Career.cpp:704`. Isolated `CompleteFlagOf` / the closed first-play pin do not go through leftover ApplyUpdate: deleting the `COMPLETE_LEVEL(110)` arm still leaves goodie 14 at `GS_UNKNOWN` on first-play. The leftover GRADE(110) C test already seeds leftover complete-110 + 0.25f and now also opens 14 in `Update()` but does not name goodie 14. Ranking 0.0f keeps `GRADE(110) >= C` / goodie 1 closed. Cold-slice latch tests stay at 5 because they do not seed leftover complete-110. Lost leftover of the same seed now names the Lost return. Do not invent a world-110 FillOut or the rest of the table. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.Update` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateLeftoverWorld110CompleteEUnlocksTheWorld110CompleteGoodie` | 1 | skip `SET_GOODIE_NEW(14)` when `COMPLETE_LEVEL(110)` |
| `CCareer::UpdateGoodieStates` Level 100 Lost leftover COMPLETE_LEVEL(110) goodie | Same body, via the Lost early return (`Career.cpp:382-385`). Leftover world-110 complete + ranking 0.0f still opens `SET_GOODIE_NEW(14)` because Lost still calls `UpdateGoodieStates` then returns. Isolated Won leftover 14 does not go through Lost ApplyUpdate. Existing Lost zeros name 0/8/78/121/164 and do not seed leftover complete-110 or name goodie 14. Lost latch does not name 14. Ranking 0.0f keeps `GRADE(110) >= C` / goodie 1 closed. World 100 stays incomplete so the five first-play S slots stay `GS_UNKNOWN`. Do not invent a world-110 FillOut or the rest of the table. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerReCalcLinks.cs` | `RetailCareerCampaign.ApplyUpdate` | `RetailCareerCampaignApplyUpdateTests.Level100Lost_ApplyUpdateLeftoverWorld110CompleteEUnlocksTheWorld110CompleteGoodie` | 1 | skip `UpdateGoodieStates` on the Lost return |
| `CCareer::UpdateGoodieStates` Level 100 new-goodie latch | Same body. `CountGoodies` (`Career.cpp:670-680`) counts `mState >= GS_NEW`. First-play S raises that count by five; `new_goodie_count` at `0x00662B20` adds the delta (`Career.cpp:895-897`) and `first_goodie` at `0x00662B24` latches because goodie 0 left `GOODIE_NOT_DONE` (`Career.cpp:688 / 899-900`). `mPendingExtraGoodies` and episode instruction marks stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.CountGoodies` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateAddsFiveNewGoodiesAndLatchesFirstGoodie` | 1 | leave the globals at ctor 0 |
| `CCareer::UpdateGoodieStates` Level 100 replay CountGoodies delta | Same body. A second `ApplyUpdate` of the already-pinned first-play S does not raise `CountGoodies`: `SET_GOODIE_NEW` stores only when `GOODIE_NOT_DONE` (`Career.cpp:564-566`). `new_goodie_count` therefore adds 0 (`Career.cpp:895-897`) and `first_goodie` stays latched. `mPendingExtraGoodies` and episode instruction marks stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.Update` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateReplayDoesNotAddTheSameFirstPlayGoodiesAgain` | 1 | add `CountGoodies` without subtracting the previous total |
| `CCareer::UpdateGoodieStates` Level 100 SET_GOODIE_NEW GS_OLD overwrite | Same body. Seeding the five first-play S slots as `GS_OLD` leaves them at 3: `SET_GOODIE_NEW` stores only when `GOODIE_NOT_DONE` (`Career.cpp:564-566`). Replay of already-`GS_NEW` does not uniquely prove this. `new_goodie_count` / `first_goodie` stay ctor 0 because CountGoodies does not rise and goodie 0 was already done. Isolated leftover Old count now names that `CountGoodies` read of 5. FrontEndHandoff leftover now names the same five slots through `TryApply`. Isolated leftover `GS_INSTRUCTIONS` now names the store-when-not-done side of the same `<=`. `mPendingExtraGoodies` and episode instruction marks stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerGoodies.SetNewIfNotDone` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateDoesNotOverwriteAlreadyOldTrainingGoodies` | 1 | store `GS_NEW` even when `mState > GS_INSTRUCTIONS` |
| `CCareer::CountGoodies` Level 100 leftover GS_OLD count | Same owner. `Career.cpp:670-680` counts `mState >= GS_NEW`. Seeding the five first-play S slots as `GS_OLD` therefore reads 5 before ApplyUpdate. Isolated leftover `GS_OLD` `NewGoodieCount=0` does not uniquely prove this: the delta is 0 whether `previouslyNew` is 0 or 5. The latch names first-play Unknown-to-New. Replay names already-`GS_NEW`. Isolated leftover `GS_INSTRUCTIONS` store names the write to 2. Isolated leftover Instructions count names the skip of state 1. `mPendingExtraGoodies` and episode instruction marks stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.CountGoodies` | `RetailCareerCampaignApplyUpdateTests.Level100Won_CountGoodiesCountsLeftoverOldTrainingGoodies` | 1 | count only `== GS_NEW` |
| `CCareer::CountGoodies` Level 100 leftover GS_INSTRUCTIONS count | Same owner. `Career.cpp:670-680` counts `mState >= GS_NEW`. Seeding the five first-play S slots as `GS_INSTRUCTIONS` therefore reads 0 before ApplyUpdate. Isolated leftover `GS_INSTRUCTIONS` store names the write to 2, not the pre-count. Isolated leftover Old count expects 5. FrontEndHandoff leftover Instructions names the store through `TryApply`. Counting only `== GS_NEW` still reads 0 on this seed. Do not invent `SET_GOODIE_INSTRUCTION` or episode instruction marks. `mPendingExtraGoodies` stays unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.CountGoodies` | `RetailCareerCampaignApplyUpdateTests.Level100Won_CountGoodiesDoesNotCountLeftoverInstructionTrainingGoodies` | 1 | count `mState >= GS_INSTRUCTIONS` |
| `CCareer::CountGoodies` Level 100 leftover COMPLETE_LEVEL(110) goodie | Same owner. `Career.cpp:670-680` iterates every slot. Leftover world-110 complete + E writes `GS_NEW` on goodie 14 while a C-grade Level 100 Won writes 0 / 8 / 78, so the count is 4. Isolated leftover 14 names the write of 14, not the count. Isolated leftover Old / Instructions counts seed only the five first-play S slots. Isolated C-grade does not name `NewGoodieCount` (would be 3). Isolated S latch is 5 without leftover 14. Skipping `SET_GOODIE_NEW(14)` is not unique versus leftover 14. Do not invent a world-110 FillOut. `mPendingExtraGoodies` stays unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.CountGoodies` | `RetailCareerCampaignApplyUpdateTests.Level100Won_CountGoodiesCountsLeftoverWorld110CompleteGoodie` | 1 | count only the five first-play S slots |
| `CCareer::CountGoodies` Level 100 leftover GRADE(110) C-goodie | Same owner. `Career.cpp:670-680` iterates every slot. Leftover world-110 complete + C writes `GS_NEW` on goodie 1, leftover 14, and leftover 79 while a C-grade Level 100 Won writes 0 / 8 / 78, so the count is 6. Isolated leftover C names the write of 1, not the count. Isolated leftover C concept-art names the write of 79, not the count. Isolated leftover 14 CountGoodies uses ranking 0.0f so the count is 4. Isolated leftover Old / Instructions counts seed only the five first-play S slots. Isolated C-grade does not name `NewGoodieCount` (would be 3). Isolated S latch is 5 without leftover 1 / 14 / 79. Skipping `SET_GOODIE_NEW(1)` is not unique versus leftover C. Skipping `SET_GOODIE_NEW(14)` is not unique versus leftover 14. Skipping `SET_GOODIE_NEW(79)` is not unique versus leftover C concept-art. Counting only the five first-play S slots is not unique versus leftover 14 CountGoodies. Do not invent a world-110 FillOut. `mPendingExtraGoodies` stays unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.CountGoodies` | `RetailCareerCampaignApplyUpdateTests.Level100Won_CountGoodiesCountsLeftoverWorld110GradeCGoodie` | 1 | skip counting goodie 1 |
| `CCareer::UpdateGoodieStates` Level 100 SET_GOODIE_NEW GS_INSTRUCTIONS store | Same body. Seeding the five first-play S slots as `GS_INSTRUCTIONS` writes 2: `SET_GOODIE_NEW` stores when `mState <= GS_INSTRUCTIONS` (`Career.cpp:564-566`). Isolated leftover `GS_OLD` and FrontEndHandoff leftover `GS_OLD` name the skip for state 3. FrontEndHandoff leftover of the same seed now names the store through `TryApply`. FrontEndHandoff S starts at `GS_UNKNOWN`. Replay names already-`GS_NEW`. Do not invent `SET_GOODIE_INSTRUCTION` or episode instruction marks — leftover seed only. `mPendingExtraGoodies` stays unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerGoodies.SetNewIfNotDone` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateStoresNewOverInstructionTrainingGoodies` | 1 | skip `SET_GOODIE_NEW` when `mState == GS_INSTRUCTIONS` |
| `CCareer::UpdateGoodieStates` Level 100 GetAndReset replay latch | Same body. `GetAndResetGoodieNewCount` / `GetAndResetFirstGoodie` (`Career.cpp:1411-1424`) consume the first-play latch. A second `ApplyUpdate` then leaves both globals at 0: CountGoodies delta is 0 and `first_goodie` is transition-only (`Career.cpp:688 / 899-900`). Replay without reset leaves the latch at 1 either way. Isolated GetAndReset is already pinned. `mPendingExtraGoodies` and episode instruction marks stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.Update` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateReplayAfterGetAndResetLeavesGoodieLatchesClear` | 1 | re-arm `first_goodie` whenever goodie 0 is currently `GS_NEW` |
| `CCareer::UpdateGoodieStates` Level 100 Lost latch | Same body, via the Lost early return (`Career.cpp:382-385`). World 100 stays incomplete, so CountGoodies delta is 0 (`Career.cpp:895-897`) and `first_goodie` stays ctor 0: goodie 0 was `GOODIE_NOT_DONE` and still is (`Career.cpp:688 / 899-900`). Existing Lost goodie-state zeros do not name these two globals. `mPendingExtraGoodies` and episode instruction marks stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerUpdateGoodieStates.cs` | `RetailCareerUpdateGoodieStates.Update` | `RetailCareerCampaignApplyUpdateTests.Level100Lost_ApplyUpdateLeavesGoodieLatchesAtCtorZero` | 1 | arm `first_goodie` whenever goodie 0 was `GOODIE_NOT_DONE` at entry |
| `CCareer::Update` Level 100 Lost skips mSlots | Lost returns before `mSlots = END_LEVEL_DATA.mSlots` (`Career.cpp:382-385` / `392`). FillOut still carries first-play `SLOT_TUTORIAL_1..4` (63..66); ApplyUpdate does not assign them, so leftover career bits stay. Isolated `ShouldOverwriteFromEndLevel` does not go through ApplyUpdate. Existing Lost goodie/latch tests do not name slots. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerReCalcLinks.cs` | `RetailCareerCampaign.ApplyUpdate` | `RetailCareerCampaignApplyUpdateTests.Level100Lost_ApplyUpdateDoesNotOverwriteCareerSlotsFromTheFillOutSnapshot` | 1 | overwrite `mSlots` on the Lost return |
| `CCareer::Update` Level 100 Lost skips ReCalcLinks base things | Lost returns before `ReCalcLinks` / `UpdateBaseWorldExistsStuffForNode` (`Career.cpp:382-385` / `416` / `443-452` / `519-527`). FillOut still carries first-play 1 at 0..34 and 0 at 35..287; ApplyUpdate does not copy them, so leftover Blank all-1s on world 110 stay set. Isolated `UpdateBaseWorldExistsStuffForNode` and `Level100Lost_DoesNotTouchTheTrainingGraph` do not name leftover bits (graph test passes no `mBaseThingsLeft`). Existing Lost goodie/latch/mSlots tests do not name them. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerReCalcLinks.cs` | `RetailCareerCampaign.ApplyUpdate` | `RetailCareerCampaignApplyUpdateTests.Level100Lost_ApplyUpdateDoesNotCopyFillOutBaseThingsOntoWorld110` | 1 | copy FillOut `mBaseThingsLeft` onto world 110 on the Lost return |
| `CCareer::UpdateThingsKilled` after Level 100 Won | `0x0041c180`. `cmp eax,0x64` / `je` at `0x0041c188` still refuses world 100. A non-zero FillOut kill vector does not accumulate. ConfirmedKill increment values stay unclaimed. Iceberg store-0 and first-play elapsed stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailCareerProgress.cs` | `RetailCareerCounters.UpdateThingsKilled` | `RetailCareerCampaignApplyUpdateTests.Level100Won_ApplyUpdateDoesNotAccumulateThingsKilledForWorld100` | 1 | drop the equality skip |
| `CBattleEngine::ConfirmedKill` Level 100 allegiance gate | Independently re-read specimen: `0x0040a564` `cmp [eax+0x138],1` / `jne 0x0040a57d` skips `0x004d30d0`. One inbound `E8` at `0x0040a578`. First-play totals stay unclaimed — a Won that never takes this path still snapshots five zeros. Iceberg store-0 stays open. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailConfirmedKill.cs` | `RetailConfirmedKill.Apply` | `RetailConfirmedKillTests.Level100Won_ConfirmedKillDoesNotIncrementWhenThingAllegianceIsNotOne` | 1 | increment even when `+0x138` is not 1 |
| `CBattleEngine::ConfirmedKill` Level 100 incrementer remaining slots | Independently re-read specimen: `0x004d30eb` `test [eax+0x34],0x40000` / `inc [ecx+0x10]`; `0x004d30fa` `test dh,0x40` = `0x4000` / `inc [ecx+0x14]`; `0x004d3105` `test dh,8` = `0x800` / `inc [ecx+0x18]`. First-play totals stay unclaimed. Iceberg store-0 stays open. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailConfirmedKill.cs` | `RetailConfirmedKill.Apply` | `RetailConfirmedKillTests.Level100Won_ConfirmedKillIncrementsSlotTwoOnFlag40000` | 1 | write `0x40000` into slot 0 |
| `CBattleEngine::ConfirmedKill` Level 100 null player-reader skip | Independently re-read specimen: `0x0040a56d` `mov ecx,[ecx+0x574]` / `0x0040a573` `test ecx,ecx` / `je 0x0040a57d` skips `0x004d30d0`. Bytes are a null pointer, not source `ToRead()` dying-flag. First-play totals stay unclaimed. Iceberg store-0 stays open. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailConfirmedKill.cs` | `RetailConfirmedKill.Apply` | `RetailConfirmedKillTests.Level100Won_ConfirmedKillDoesNotIncrementWhenPlayerReaderIsNull` | 1 | increment even when the reader is null |
| `CGame::FillOutEndLevelData` then `CCareer::UpdateGoodieStates` from Level 100 `FrontEndHandoffReady` | After the already-pinned Won countdown, first-play FillOut 1.0f / S unlocks goodies 0, 8, 78, 121, and 164. Cite `0x0041de68` / `0x0041ea4f` / `0x0041f70e`. Score-time / base-things / kill totals stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/Level100WonCareerHandoff.cs` | `Level100WonCareerHandoff.TryApply` | `Level100WonCareerHandoffTests.FrontEndHandoffReadyAfterWon_UnlocksTrainingGoodiesForAnS` | 1 | skip `ApplyUpdate` on the handoff |
| `CGame::FillOutEndLevelData` then `CCareer::UpdateGoodieStates` Level 100 FrontEndHandoff latch | Same seam. First-play S raises `CountGoodies` by five; `new_goodie_count` at `0x00662B20` adds the delta (`Career.cpp:895-897`) and `first_goodie` at `0x00662B24` latches because goodie 0 left `GOODIE_NOT_DONE` (`Career.cpp:688 / 899-900`). Isolated ApplyUpdate latch does not go through `TryApply`. Existing FrontEndHandoff goodie-state test does not name these two globals. `mPendingExtraGoodies` and episode instruction marks stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/Level100WonCareerHandoff.cs` | `Level100WonCareerHandoff.TryApply` | `Level100WonCareerHandoffTests.FrontEndHandoffReadyAfterWon_AddsFiveNewGoodiesAndLatchesFirstGoodie` | 1 | clear both globals after `TryApply` |
| `CGame::FillOutEndLevelData` then `CCareer::UpdateGoodieStates` Level 100 FrontEndHandoff leftover COMPLETE_LEVEL(110) goodie | Same seam. Leftover world-110 complete + ranking 0.0f (already pinned as E) opens `Career.cpp:704` through `TryApply`. Isolated leftover 14 names ApplyUpdate and does not go through `TryApply`. Lost leftover 14 names ApplyUpdate's Lost return, not `TryApply`. Existing FrontEndHandoff S goodies name 0/8/78/121/164, not 14. Ranking 0.0f keeps `GRADE(110) >= C` / goodie 1 closed. Do not invent a world-110 FillOut or the rest of the table. No new secondaries | `rebuild/OnslaughtRebuild.Core/Level100WonCareerHandoff.cs` | `Level100WonCareerHandoff.TryApply` | `Level100WonCareerHandoffTests.FrontEndHandoffReadyAfterWon_LeftoverWorld110CompleteEUnlocksTheWorld110CompleteGoodie` | 1 | clear goodie 14 after `TryApply` |
| `CGame::FillOutEndLevelData` then `CCareer::UpdateGoodieStates` Level 100 FrontEndHandoff leftover GRADE(110) C-goodie | Same seam. Leftover world-110 complete + ranking 0.25f (already pinned as C) opens `Career.cpp:691` through `TryApply`. Isolated leftover C names ApplyUpdate and does not go through `TryApply`. FrontEndHandoff leftover 14 names 14, not 1. Existing FrontEndHandoff S goodies name 0/8/78/121/164, not 1. Do not invent a world-110 FillOut or the rest of the table. The leftover `COMPLETE_LEVEL(110)` store is not named here. Isolated leftover C concept-art names 79 through ApplyUpdate and is not named here. No new secondaries | `rebuild/OnslaughtRebuild.Core/Level100WonCareerHandoff.cs` | `Level100WonCareerHandoff.TryApply` | `Level100WonCareerHandoffTests.FrontEndHandoffReadyAfterWon_LeftoverWorld110CompleteCUnlocksTheWorld110CGoodie` | 1 | clear goodie 1 after `TryApply` |
| `CGame::FillOutEndLevelData` then `CCareer::UpdateGoodieStates` Level 100 FrontEndHandoff leftover GRADE(110) C concept-art goodie | Same seam. Leftover world-110 complete + ranking 0.25f (already pinned as C) opens `Career.cpp:770` through `TryApply`. Isolated leftover C 79 names ApplyUpdate and does not go through `TryApply`. FrontEndHandoff leftover C names 1, not 79. Existing FrontEndHandoff S goodies name 0/8/78/121/164, not 79. Do not invent `GRADE(110) >= B` / `A` or a world-110 FillOut. No new secondaries | `rebuild/OnslaughtRebuild.Core/Level100WonCareerHandoff.cs` | `Level100WonCareerHandoff.TryApply` | `Level100WonCareerHandoffTests.FrontEndHandoffReadyAfterWon_LeftoverWorld110CompleteCUnlocksTheWorld110CConceptArtGoodie` | 1 | clear goodie 79 after `TryApply` |
| `CGame::FillOutEndLevelData` then `CCareer::UpdateGoodieStates` Level 100 FrontEndHandoff GRADE(110) C-goodie closed | Same seam. First-play S through `TryApply` leaves world 110 incomplete so `GRADE` is the already-pinned incomplete `'E'` (`0x0041C3FE`) and goodie 1 stays `GS_UNKNOWN`. Isolated closed GRADE(110) names ApplyUpdate and does not go through `TryApply`. Leftover C FrontEndHandoff names 1 as New. Existing FrontEndHandoff S goodies name 0/8/78/121/164, not 1. Isolated closed concept-art now names 79 on ApplyUpdate. Do not invent a world-110 FillOut or the rest of the table. No new secondaries | `rebuild/OnslaughtRebuild.Core/Level100WonCareerHandoff.cs` | `Level100WonCareerHandoff.TryApply` | `Level100WonCareerHandoffTests.FrontEndHandoffReadyAfterWon_LeavesTheWorld110CGoodieUnknown` | 1 | store `GS_NEW` on goodie 1 after `TryApply` when world 110 is incomplete |
| `CGame::FillOutEndLevelData` then `CCareer::UpdateGoodieStates` Level 100 FrontEndHandoff GRADE(110) C concept-art goodie closed | Same seam. First-play S through `TryApply` leaves world 110 incomplete so `GRADE` is the already-pinned incomplete `'E'` (`0x0041C3FE`) and goodie 79 stays `GS_UNKNOWN`. Isolated closed concept-art names ApplyUpdate and does not go through `TryApply`. FrontEndHandoff closed GRADE(110) names 1, not 79. Leftover C FrontEndHandoff names 79 as New. Existing FrontEndHandoff S goodies name 0/8/78/121/164, not 79. Skipping `SET_GOODIE_NEW(79)` is not unique versus leftover C concept-art. Skipping `ApplyUpdate` on the handoff is not unique versus existing FrontEndHandoff tests. Do not invent `GRADE(110) >= B` / `A` or a world-110 FillOut. No new secondaries | `rebuild/OnslaughtRebuild.Core/Level100WonCareerHandoff.cs` | `Level100WonCareerHandoff.TryApply` | `Level100WonCareerHandoffTests.FrontEndHandoffReadyAfterWon_LeavesTheWorld110CConceptArtGoodieUnknown` | 1 | store `GS_NEW` on goodie 79 after `TryApply` when world 110 is incomplete |
| `CGame::FillOutEndLevelData` then `CCareer::UpdateGoodieStates` Level 100 FrontEndHandoff COMPLETE_LEVEL(110) goodie closed | Same seam. First-play S through `TryApply` leaves world 110 unlocked but incomplete so goodie 14 stays `GS_UNKNOWN`. Isolated closed COMPLETE_LEVEL(110) names ApplyUpdate and does not go through `TryApply`. Leftover 14 FrontEndHandoff names 14 as New. Existing FrontEndHandoff S goodies name 0/8/78/121/164, not 14. Do not invent a world-110 FillOut or the rest of the table. No new secondaries | `rebuild/OnslaughtRebuild.Core/Level100WonCareerHandoff.cs` | `Level100WonCareerHandoff.TryApply` | `Level100WonCareerHandoffTests.FrontEndHandoffReadyAfterWon_LeavesTheWorld110CompleteGoodieUnknown` | 1 | store `GS_NEW` on goodie 14 after `TryApply` |
| `CGame::FillOutEndLevelData` then `CCareer::Update` Level 100 FrontEndHandoff leftover mNumAttempts skip | Same seam. Leftover 7 on world 100 and 11 on world 110 survive first-play S through `TryApply` because `Career.cpp:379-418` never writes `+0x38`. Isolated leftover 7 / 11 names ApplyUpdate and does not go through `TryApply`. Isolated Blank ctor 0 does not go through `TryApply`. Existing FrontEndHandoff ranking / Complete / CareerInProgress / goodie tests do not name `+0x38`. Incrementing inside ApplyUpdate is not unique versus the isolated pin. Skipping `ApplyUpdate` on the handoff is not unique versus existing FrontEndHandoff tests. No new secondaries | `rebuild/OnslaughtRebuild.Core/Level100WonCareerHandoff.cs` | `Level100WonCareerHandoff.TryApply` | `Level100WonCareerHandoffTests.FrontEndHandoffReadyAfterWon_DoesNotIncrementLeftoverNumAttempts` | 1 | increment the finished node after `TryApply` |
| `CGame::FillOutEndLevelData` then `CCareer::UpdateGoodieStates` Level 100 FrontEndHandoff leftover SET_GOODIE_NEW GS_OLD overwrite | Same seam. Seeding the five first-play S slots as `GS_OLD` leaves them at 3 through `TryApply`: `SET_GOODIE_NEW` stores only when `GOODIE_NOT_DONE` (`Career.cpp:564-566`). Isolated leftover `GS_OLD` names ApplyUpdate and does not go through `TryApply`. Existing FrontEndHandoff S goodies start `GS_UNKNOWN` and name them as New. Replay CountGoodies names already-`GS_NEW`. `new_goodie_count` / `first_goodie` stay ctor 0. Storing `GS_NEW` even when `mState > GS_INSTRUCTIONS` is not unique versus the isolated pin. Skipping `ApplyUpdate` on the handoff is not unique versus existing FrontEndHandoff tests. `mPendingExtraGoodies` and episode instruction marks stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/Level100WonCareerHandoff.cs` | `Level100WonCareerHandoff.TryApply` | `Level100WonCareerHandoffTests.FrontEndHandoffReadyAfterWon_DoesNotOverwriteAlreadyOldTrainingGoodies` | 1 | store `GS_NEW` on the five slots after `TryApply` when they were `GS_OLD` |
| `CGame::FillOutEndLevelData` then `CCareer::UpdateGoodieStates` Level 100 FrontEndHandoff leftover SET_GOODIE_NEW GS_INSTRUCTIONS store | Same seam. Seeding the five first-play S slots as `GS_INSTRUCTIONS` writes 2 through `TryApply`: `SET_GOODIE_NEW` stores when `mState <= GS_INSTRUCTIONS` (`Career.cpp:564-566`). Isolated leftover `GS_INSTRUCTIONS` names ApplyUpdate and does not go through `TryApply`. Isolated leftover `GS_OLD` and FrontEndHandoff leftover `GS_OLD` name the skip for state 3. FrontEndHandoff S starts `GS_UNKNOWN`. Replay names already-`GS_NEW`. Skipping `SET_GOODIE_NEW` when `mState == GS_INSTRUCTIONS` is not unique versus the isolated pin. Skipping `ApplyUpdate` on the handoff is not unique versus existing FrontEndHandoff tests. Do not invent `SET_GOODIE_INSTRUCTION` or episode instruction marks. `mPendingExtraGoodies` stays unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/Level100WonCareerHandoff.cs` | `Level100WonCareerHandoff.TryApply` | `Level100WonCareerHandoffTests.FrontEndHandoffReadyAfterWon_StoresNewOverInstructionTrainingGoodies` | 1 | restore the five slots to `GS_INSTRUCTIONS` after `TryApply` when they were `GS_INSTRUCTIONS` |
| `IScript::SetSlotSave` Level 100 tutorial persist | `0x00533900` calls `CGame::SetSlot` `0x0046d3a0` then `CCareer::SetSlot` `0x004214e0`. First-play `SetSlotSave(SLOT_TUTORIAL_1..4, TRUE)` writes career bits 63..66 during the tutorial, before `DeclareLevelWon` and before FillOut / `ApplyUpdate`. Isolated FrontEndHandoff overwrite names the 32-dword assignment after `TryApply`; empty FillOut slot words still leave 63..66 set here. World 100 stays incomplete. Live `GAME.mSlots` stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailSetSlotSave.cs` | `RetailSetSlotSave.PersistCareerSlot` | `Level100WonCareerHandoffTests.SetSlotSave_PersistsTutorialBitsBeforeApplyUpdate` | 1 | skip `PersistCareerSlot` so 63..66 stay 0 on `SuccessCountdown` |
| `IScript::PrimaryObjectiveFailed` Level 100 init MOS | `0x00534440` writes state 2 (Wave580 plate). Level 100 `init()` calls it for objectives 1..4 before the first `PlayCharMessageWait`. Rebuild `Level100PrimaryObjectiveStatus.Failed` is 1, so an identity cast is not `MOS_FAILED`. Isolated FillOut Won names four `MOS_COMPLETE` (1) and does not go through init. `GetNumPrimaryObjectives` counting non-zero is not unique versus mapping Failed to 1. Live `GAME.mSlots` stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailGameObjectiveCount.cs` | `RetailGameObjectiveCount.FromLevel100MissionStatus` | `Level100MissionTests.Init_PrimaryObjectiveFailedWritesRetailMosFailedTwo` | 1 | identity-cast the mission enum so Failed stores 1 |
| `IScript::PrimaryObjectiveFailed` Level 100 init text dword | `0x0053445e` `89 78 04` = `mov [eax+4], edi` on specimen `74154bfa…`. Twin Complete at `0x005343fe`. Table base `lea eax, [eax*8+0x8a9adc]`. Level 100 `init()` stores `_100_OBJECTIVE_1..4` = 110325434 / 111145813 / 111966192 / 112786571 (first cited in `msl-scripting.md`; 2..4 from hash-pinned LevelScript). Isolated MOS-failed names state 2, not `+4`. Isolated FillOut Won names four `GetStatus()` words and does not copy the text dword. Live `GAME.mSlots` stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailGameObjectiveCount.cs` | `RetailGameObjectiveCount.FromLevel100MissionPrimaryTextIds` | `Level100MissionTests.Init_PrimaryObjectiveFailedWritesRetailObjectiveTextDword` | 1 | leave the ten text words at 0 |
| `IScript::AddScore` Level 100 incrementer | `0x005343c0` body `8b442404 8b08 8b11 ff5230 01058c9b8a00 c20c00` on specimen `74154bfa…`. `0x005343cb` is `01 05 8c 9b 8a 00` = `add [0x008a9b8c], eax` = `CGame+0xf4`. Source `game.h:210` is `mScore+=inScore`. LoadLevel writes 0. Isolated `ScoreDelta` = 50 names the rebuild accumulator; one live `AddScore(50)` is not unique versus replace. Isolated FillOut `ScoreWord` copies a parameterized dword. First-play elapsed and FillOut score stay unclaimed. Live `GAME.mSlots` stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailAddScore.cs` | `RetailAddScore.Add` | `RetailAddScoreTests.Add_AddsTheDeltaOntoCGamePlusF4NotReplace` | 1 | replace so a second +50 stays 50 |
| `IScript::EnableFlightMode` Level 100 flight flag | `0x00535070` body `8b4910f64134087405e8328cedffc20c00` on specimen `74154bfa…`. `0x00535079` is `e8 32 8c ed ff` = `call 0x0040dcb0` (W001 inbound). Callee `0x0040dcb0` is `c7 81 8c 05 00 00 01 00 00 00 c3` = `mov [ecx+0x58c], 1`. Isolated `FlightModeEnabled` = true names the rebuild bool; skip store Expected 1 Actual 0. One live store of 1 is not unique versus increment from 0. Wrapper gate `test [ecx+0x34], 8` and Disable clear / morph stay unclaimed. ChargeWeapon stays unclaimed. Live `GAME.mSlots` stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailEnableFlightMode.cs` | `RetailEnableFlightMode.Enable` | `RetailEnableFlightModeTests.Enable_StoresLiteralOneAtCBattleEnginePlus58CNotIncrement` | 1 | increment so Enable(1) becomes 2 |
| `IScript::HighlightHudPart` / `UnHighlightHudPart` Level 100 HUD words | `0x00535e60` body `8b4424048b088b11ff5230c704851ca58a0002000000c20c00` on specimen `74154bfa…` (25 B SHA-256 `d2a93e3b…e479fc39`). `0x00535e6c` is `c7 04 85 1c a5 8a 00 02 00 00 00` = `mov dword [eax*4+0x008aa51c], 2`. Twin `0x00535e80` SHA-256 `d273f5d1…c3c5a581` stores immediate 1, not 0. Isolated `Emphasized` true/false names the rebuild bitmask; skip UnHighlight after Highlight leaves 2. Array extent and state-1/2 HUD meaning stay unclaimed. ChargeWeapon stays unclaimed. Live `GAME.mSlots` stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailHighlightHudPart.cs` | `RetailHighlightHudPart.Unhighlight` | `RetailHighlightHudPartTests.HighlightAndUnhighlight_StoreTwoThenOneNotBoolMask` | 1 | Unhighlight writes 0 so Unhighlight(2) becomes 0 |
| `IScript::EnableWeapon` Level 100 walker active flag | `0x00534fb0` body SHA-256 `b71e37ce…92766eb4` on specimen `74154bfa…`. `0x00534fce` is `ff 97 98 01 00 00` = `call [edi+0x198]`. Player override `0x0040dc30` (37 B SHA-256 `fa72dd3f…eb92f839`) forwards to walker `0x00414970`. `0x004149c7` is `c7 87 9c 00 00 00 01 00 00 00` = `mov [edi+0x9c], 1`. Isolated `Enabled` = true names the rebuild bool; skip store Expected 1 Actual 0. One live store of 1 is not unique versus increment from 0. Wrapper gate `test [eax+0x34], 0x10` and Disable store-0 / ChangeWeapon stay unclaimed. ChargeWeapon stays unclaimed. Live `GAME.mSlots` stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailEnableWeapon.cs` | `RetailEnableWeapon.Enable` | `RetailEnableWeaponTests.Enable_StoresLiteralOneAtWeaponPlus9CNotIncrement` | 1 | increment so Enable(1) becomes 2 |
| `IScript::SetObjective` / `UnsetObjective` Level 100 thing flag | `0x00535ed0` body `8b49106a01e896dafbffc20c00` on specimen `74154bfa…` (13 B SHA-256 `e1e368b8…a48f666b`). Twin Unset `0x00535ee0` pushes 0. Callee `0x004f3970` 61 B SHA-256 `da733fdd…353980b0`. `0x004f398e` is `80 4e 2c 20` = `or [esi+0x2c], 0x20`. Unset `0x004f39a5` is `80 66 2c df` = `and [esi+0x2c], 0xdf`. Isolated `IsObjective` / navigation name stay the rebuild bool / string; skip store Expected 0x20 Actual 0. One live store of 0x20 from 0 is not unique versus replace. Isolated Mark(0x04)=0x24. Noticeboard Add/Remove stay unclaimed. ChargeWeapon stays unclaimed. Live `GAME.mSlots` stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailSetObjective.cs` | `RetailSetObjective.Mark` | `RetailSetObjectiveTests.MarkAndUnmark_OrBit20ThenClearItNotBoolReplace` | 1 | replace so Mark(0x04) becomes 0x20 |
| `IScript::Pause` / `PlayCharMessageWait` Level 100 wait stop flag | `0x00537c70` through `ret 0xc` at `0x00537d66` (249 B SHA-256 `2bdf08ea…829f`) and `0x005375f0` through `ret 0xc` at `0x005377d5` (488 B SHA-256 `7d65b4bc…55e3`) on specimen `74154bfa…`. `0x00537d55` / `0x005376f9` are `c7 05 00 c8 89 00 01 00 00 00` = `mov [0x0089c800], 1` (singleton `+0x220`). Isolated `PauseTicks` / `MessagePlaybackTicks` name the rebuild sleep; skip store Expected 1 Actual 0. One live store of 1 is not unique versus increment from 0. First-play init issues six `PlayCharMessageWait`s; increment would be 6. CVM snapshot / 0.05f / FollowWaypointWait / PlayAnimationWait / Run-yield stay unclaimed. ChargeWeapon stays unclaimed. Live `GAME.mSlots` stay unclaimed. No new secondaries | `rebuild/OnslaughtRebuild.Core/RetailIScriptWaitStop.cs` | `RetailIScriptWaitStop.Stop` | `RetailIScriptWaitStopTests.Stop_StoresLiteralOneAtCvmSingletonPlus220NotIncrement` | 1 | increment so Stop(1) becomes 2 |

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
GRADE(110) C-goodie row names that same `Update` owner; it
does not invent the rest of the table. The GRADE(110) C
concept-art closed row names that same `Update` owner and
`Career.cpp:770`; isolated closed GRADE(110) names 1, not 79.
The leftover
GRADE(110) C-goodie row names that same `Update` owner and
the leftover complete-110 + C store; it does not invent a
world-110 FillOut. The leftover GRADE(110) C concept-art
row names that same `Update` owner and `Career.cpp:770`
`SET_GOODIE_NEW(79)`; isolated leftover C names 1, not 79.
Isolated first-play closed concept-art names 79 at
`GS_UNKNOWN`.
The COMPLETE_LEVEL(110) goodie row names
that same `Update` owner; first-play leaves world 110
incomplete so goodie 14 stays `GS_UNKNOWN`. The leftover
COMPLETE_LEVEL(110) goodie row names that same `Update`
owner and the leftover complete-110 + E store; it does not
invent a world-110 FillOut. The Lost leftover
COMPLETE_LEVEL(110) goodie row names `ApplyUpdate`; isolated
Won leftover 14 does not uniquely prove the Lost return still
runs `UpdateGoodieStates`. The
new-goodie latch row names `CountGoodies` on that same owner;
`mPendingExtraGoodies` stays unclaimed. The
replay CountGoodies-delta row names that same `Update` owner;
it does not add another implementation. The
SET_GOODIE_NEW GS_OLD overwrite row names `SetNewIfNotDone` on
that same owner; it does not add another implementation.
FrontEndHandoff leftover of that same seed now names
`TryApply`. The leftover `GS_OLD` CountGoodies row names
`CountGoodies` on that same owner; isolated leftover
`GS_OLD` `NewGoodieCount=0` does not uniquely prove the
count of leftover Old. The leftover `GS_INSTRUCTIONS`
CountGoodies row names that same `CountGoodies` owner;
isolated leftover `GS_INSTRUCTIONS` store names the write
to 2, not the pre-count of 0. The leftover COMPLETE_LEVEL(110)
CountGoodies row names that same `CountGoodies` owner;
isolated leftover 14 names the write of 14, not the count of
4. The leftover GRADE(110) C CountGoodies row names that
same `CountGoodies` owner; isolated leftover C names the
write of 1, not the count of 6. Isolated leftover C
concept-art names the write of 79, not that count. Isolated leftover 14
CountGoodies uses ranking 0.0f so the count is 4. The
SET_GOODIE_NEW GS_INSTRUCTIONS store row names that same
`SetNewIfNotDone` owner; isolated leftover `GS_OLD` names
the skip for state 3 and does not uniquely prove the store
when `mState == GS_INSTRUCTIONS`. The
GetAndReset replay-latch row names that same `Update` owner;
it does not add another implementation. Isolated GetAndReset
is already pinned on `RetailCareerCounters`. The
Lost-latch row names that same `Update` owner via the Lost
early return. The Lost mSlots-skip row names `ApplyUpdate`;
isolated `ShouldOverwriteFromEndLevel` does not uniquely
prove the early return. The Lost ReCalcLinks / base-things
skip row names that same `ApplyUpdate` owner; isolated
`UpdateBaseWorldExistsStuffForNode` and
`Level100Lost_DoesNotTouchTheTrainingGraph` do not uniquely
prove leftover Blank all-1s. The
world-100 kill-skip row names `RetailCareerCounters.UpdateThingsKilled`;
`ApplyUpdate` is the already-pinned caller. The
FrontEndHandoff goodie row names the same `TryApply` owner as the
Won handoff. The FrontEndHandoff latch row names that same
`TryApply` owner; isolated ApplyUpdate latch and the
FrontEndHandoff goodie-state test do not name the two globals.
The FrontEndHandoff leftover COMPLETE_LEVEL(110) goodie row
names that same `TryApply` owner; isolated leftover 14 and
Lost leftover 14 do not go through `TryApply`.
The FrontEndHandoff leftover GRADE(110) C-goodie row names
that same `TryApply` owner; isolated leftover C names
ApplyUpdate and FrontEndHandoff leftover 14 names 14, not 1.
The leftover C concept-art store is not named there.
The FrontEndHandoff leftover GRADE(110) C concept-art
row names that same `TryApply` owner; isolated leftover C
79 names ApplyUpdate and FrontEndHandoff leftover C names
1, not 79.
The FrontEndHandoff GRADE(110) C-goodie closed row names
that same `TryApply` owner; isolated closed GRADE(110) names
ApplyUpdate and leftover C FrontEndHandoff names 1 as New.
The FrontEndHandoff GRADE(110) C concept-art closed row
names that same `TryApply` owner; isolated closed concept-art
names ApplyUpdate and leftover C FrontEndHandoff names 79
as New.
The FrontEndHandoff COMPLETE_LEVEL(110) goodie closed row
names that same `TryApply` owner; isolated closed
COMPLETE_LEVEL(110) names ApplyUpdate and leftover 14
FrontEndHandoff names 14 as New.
The FrontEndHandoff leftover mNumAttempts row names
that same `TryApply` owner; isolated leftover 7 / 11
names ApplyUpdate and existing FrontEndHandoff ranking /
Complete / CareerInProgress / goodie tests do not name
`+0x38`.
The FrontEndHandoff leftover SET_GOODIE_NEW GS_OLD
overwrite row names that same `TryApply` owner; isolated
leftover `GS_OLD` names ApplyUpdate and existing
FrontEndHandoff S goodies start `GS_UNKNOWN`. Replay
CountGoodies names already-`GS_NEW`.
The FrontEndHandoff leftover SET_GOODIE_NEW GS_INSTRUCTIONS
store row names that same `TryApply` owner; isolated leftover
`GS_INSTRUCTIONS` names ApplyUpdate and does not uniquely
prove the store through `TryApply`.
The SetSlotSave persist row names `PersistCareerSlot` on
`RetailSetSlotSave`; isolated FrontEndHandoff overwrite
names the 32-dword assignment after `TryApply` and does
not uniquely prove the mid-mission `CCareer::SetSlot`.
Live `GAME.mSlots` stay unclaimed.
The init MOS-failed row names `FromLevel100MissionStatus` on
`RetailGameObjectiveCount`; isolated FillOut Won names four
`MOS_COMPLETE` (1) and does not uniquely prove init's
`MOS_FAILED` (2).
The init text-dword row names `FromLevel100MissionPrimaryTextIds`
on that same owner; isolated MOS-failed names state 2 and
does not uniquely prove `[eax+4]`. Isolated FillOut Won
names four `GetStatus()` words and does not copy the text
dword. Live `GAME.mSlots` stay unclaimed.
The AddScore incrementer row names `RetailAddScore.Add`; isolated
`ScoreDelta` = 50 names the rebuild accumulator and does
not uniquely prove `add [0x008a9b8c], eax`. One live
`AddScore(50)` is not unique versus replace. Isolated
FillOut `ScoreWord` copies a parameterized dword. First-play
elapsed and FillOut score stay unclaimed.
The EnableFlightMode flight-flag row names
`RetailEnableFlightMode.Enable`; isolated
`FlightModeEnabled` = true names the rebuild bool and
does not uniquely prove `mov [ecx+0x58c], 1`. One live
store of 1 is not unique versus increment from 0.
Wrapper gate `test [ecx+0x34], 8` and Disable clear /
morph stay unclaimed. ChargeWeapon stays unclaimed.
The HighlightHudPart / UnHighlightHudPart HUD-word row
names `RetailHighlightHudPart.Unhighlight`; isolated
`Emphasized` = false names the rebuild bool and does
not uniquely prove `mov [eax*4+0x008aa51c], 1`. Skip
UnHighlight after Highlight leaves 2. Array extent and
state-1/2 HUD meaning stay unclaimed. ChargeWeapon
stays unclaimed.
The EnableWeapon walker-active-flag row names
`RetailEnableWeapon.Enable`; isolated `Enabled` = true
names the rebuild bool and does not uniquely prove
`mov [edi+0x9c], 1`. One live store of 1 is not unique
versus increment from 0. Wrapper gate
`test [eax+0x34], 0x10` and Disable store-0 /
ChangeWeapon stay unclaimed. ChargeWeapon stays
unclaimed.
The SetObjective / UnsetObjective thing-flag row names
`RetailSetObjective.Mark`; isolated `IsObjective` /
navigation name do not uniquely prove
`or [esi+0x2c], 0x20`. One live store of 0x20 from 0
is not unique versus replace. Isolated Mark(0x04)=0x24.
Noticeboard Add/Remove stay unclaimed. ChargeWeapon
stays unclaimed.
The Pause / PlayCharMessageWait stop-flag row names
`RetailIScriptWaitStop.Stop`; isolated `PauseTicks` /
`MessagePlaybackTicks` name the rebuild sleep and do
not uniquely prove `mov [0x0089c800], 1`. One live
store of 1 is not unique versus increment from 0.
CVM snapshot / 0.05f / FollowWaypointWait /
PlayAnimationWait / Run-yield stay unclaimed.
ChargeWeapon stays unclaimed.
The score-time arm row names `AfterScoreTimeArm` on
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
jet throttle caps below the gate's band. The seventeenth through thirty-seventh
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
