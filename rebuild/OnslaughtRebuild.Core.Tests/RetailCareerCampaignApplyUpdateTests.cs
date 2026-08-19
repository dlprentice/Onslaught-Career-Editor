// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Core.Tests;

/// <summary>
/// Pins the Level 100 Won consumer that carries FillOut's
/// <c>END_LEVEL_DATA.mSlots</c> into <c>CCareer::Update</c> via
/// <see cref="RetailCareerCampaign.ApplyUpdate"/>. The 32-dword
/// assignment itself is already pinned; this suite only proves
/// <see cref="RetailFillOutEndLevelData.ForLevel100Won"/> includes
/// the four first-play <c>SetSlotSave</c> bits and that ApplyUpdate
/// replaces career <c>mSlots</c> with them.
/// </summary>
public sealed class RetailCareerCampaignApplyUpdateTests
{
    /// <summary>
    /// After a cold-career first-play win, FillOut's snapshot holds
    /// <c>SLOT_TUTORIAL_1..4</c> (63..66) and nothing else addressable.
    /// <c>ApplyUpdate</c> assigns those 32 words over career
    /// <c>mSlots</c>, so a leftover bit dies. Mutation: OR-ing the
    /// words leaves slot 1 set; skipping the overwrite leaves 63..66
    /// unset; inventing a secondary would mark a status word 1 or 2.
    /// </summary>
    [Fact]
    public void Level100Won_ApplyUpdateOverwritesCareerSlotsFromTheFillOutSnapshot()
    {
        RetailCareerCampaign career = RetailCareerReCalcLinks.CreateColdTrainingSlice();
        career.Slots.SetSlot(1, 1);

        RetailEndLevelSnapshot snapshot = RetailFillOutEndLevelData.ForLevel100Won();
        var snapshotSlots = new RetailCareerSlots();
        snapshotSlots.CopyWords(snapshot.SlotWords);

        Assert.Equal(1, snapshotSlots.GetSlot(RetailCareerSlotHandoff.TutorialIntroductionSlot));
        Assert.Equal(1, snapshotSlots.GetSlot(RetailCareerSlotHandoff.TutorialPulseCannonSlot));
        Assert.Equal(1, snapshotSlots.GetSlot(RetailCareerSlotHandoff.TutorialVulcanCannonSlot));
        Assert.Equal(1, snapshotSlots.GetSlot(RetailCareerSlotHandoff.TutorialStatusBarsSlot));
        Assert.Equal(0, snapshotSlots.GetSlot(1));
        Assert.Equal(0, snapshotSlots.GetSlot(62));
        Assert.Equal(0, snapshotSlots.GetSlot(67));
        Assert.All(snapshot.SecondaryStatuses, status => Assert.Equal(0, status));

        career.ApplyUpdate(snapshot);

        Assert.Equal(0, career.Slots.GetSlot(1));
        Assert.Equal(1, career.Slots.GetSlot(RetailCareerSlotHandoff.TutorialIntroductionSlot));
        Assert.Equal(1, career.Slots.GetSlot(RetailCareerSlotHandoff.TutorialPulseCannonSlot));
        Assert.Equal(1, career.Slots.GetSlot(RetailCareerSlotHandoff.TutorialVulcanCannonSlot));
        Assert.Equal(1, career.Slots.GetSlot(RetailCareerSlotHandoff.TutorialStatusBarsSlot));
        Assert.Equal(snapshot.SlotWords, career.Slots.Words);
        Assert.Equal(1, career.Nodes.Find(100)!.Complete);
        Assert.Equal(
            RetailCareerNodeLink.Complete,
            career.GetLink(career.Nodes.Find(100)!.LowerLink)!.LinkType);
    }

    /// <summary>
    /// <c>CCareer::Update</c> never reads the primary table FillOut
    /// copied. Writing the rebuild mission enum <c>Complete=2</c> into
    /// that table must not change the graph. Mutation: requiring
    /// <c>MOS_COMPLETE=1</c> before completing the node leaves 110
    /// locked on the mission-enum snapshot. No new secondaries.
    /// </summary>
    [Fact]
    public void Level100Won_ApplyUpdateDoesNotConsultPrimaryStatuses()
    {
        RetailCareerCampaign mosComplete = RetailCareerReCalcLinks.CreateColdTrainingSlice();
        RetailCareerCampaign missionEnum = RetailCareerReCalcLinks.CreateColdTrainingSlice();
        RetailEndLevelSnapshot won = RetailFillOutEndLevelData.ForLevel100Won();
        RetailEndLevelSnapshot completeTwo = won with
        {
            PrimaryStatuses = new[] { 2, 2, 2, 2, 0, 0, 0, 0, 0, 0 },
        };

        mosComplete.ApplyUpdate(won);
        missionEnum.ApplyUpdate(completeTwo);

        RetailCareerNodeLink mosLower =
            mosComplete.GetLink(mosComplete.Nodes.Find(100)!.LowerLink)!;
        RetailCareerNodeLink enumLower =
            missionEnum.GetLink(missionEnum.Nodes.Find(100)!.LowerLink)!;
        Assert.Equal(1, mosComplete.Nodes.Find(100)!.Complete);
        Assert.Equal(1, missionEnum.Nodes.Find(100)!.Complete);
        Assert.Equal(RetailCareerNodeLink.Complete, mosLower.LinkType);
        Assert.Equal(RetailCareerNodeLink.Complete, enumLower.LinkType);
        Assert.All(won.SecondaryStatuses, status => Assert.Equal(0, status));
        Assert.All(completeTwo.SecondaryStatuses, status => Assert.Equal(0, status));
    }

    /// <summary>
    /// <c>CCareer::Update</c> writes <c>mRanking</c> only onto
    /// <c>GetNodeFromWorldNo(mWorldFinished)</c> (<c>Career.cpp:396-406</c>).
    /// The already-pinned FillOut 1.0f therefore lands on world 100
    /// (grade S) and world 110 stays <c>BlankRanking</c> / grade E.
    /// Mutation: copying the snapshot ranking onto the unlocked child
    /// makes 110 read 1.0 / S. Score-time, base-things, kills, and
    /// goodies stay unclaimed. No new secondaries.
    /// </summary>
    [Fact]
    public void Level100Won_ApplyUpdateWritesRankingOnlyOnTheFinishedWorld()
    {
        RetailCareerCampaign career = RetailCareerReCalcLinks.CreateColdTrainingSlice();
        RetailEndLevelSnapshot snapshot = RetailFillOutEndLevelData.ForLevel100Won();

        career.ApplyUpdate(snapshot);

        RetailCareerNode training = career.Nodes.Find(100)!;
        RetailCareerNode next = career.Nodes.Find(110)!;
        Assert.Equal(1.0f, snapshot.Ranking);
        Assert.Equal(1.0f, training.Ranking);
        Assert.Equal(
            RetailCareerGrade.PerfectGrade,
            RetailCareerGrade.GradeByteFromRanking(training.Ranking));
        Assert.Equal(RetailCareerNode.BlankRanking, next.Ranking);
        Assert.Equal(
            RetailCareerGrade.FailedGrade,
            RetailCareerGrade.GradeByteFromRanking(next.Ranking));
        Assert.Equal(0, next.Complete);
        Assert.All(snapshot.SecondaryStatuses, status => Assert.Equal(0, status));
    }

    /// <summary>
    /// <c>Career.cpp:405-406</c> stores <c>mRanking</c> only when the
    /// snapshot is strictly greater. A worse Level 100 replay therefore
    /// leaves the already-pinned first-play 1.0f / S in place. Mutation:
    /// assigning the snapshot even when it is not greater makes world 100
    /// read 0.5. Score-time stays unclaimed. No new secondaries.
    /// </summary>
    [Fact]
    public void Level100Won_ApplyUpdateDoesNotDowngradeAnExistingBetterRanking()
    {
        RetailCareerCampaign career = RetailCareerReCalcLinks.CreateColdTrainingSlice();
        career.ApplyUpdate(RetailFillOutEndLevelData.ForLevel100Won());
        career.ApplyUpdate(RetailFillOutEndLevelData.ForLevel100Won(ranking: 0.5f));

        RetailCareerNode training = career.Nodes.Find(100)!;
        RetailCareerNode next = career.Nodes.Find(110)!;
        Assert.Equal(1.0f, training.Ranking);
        Assert.Equal(
            RetailCareerGrade.PerfectGrade,
            RetailCareerGrade.GradeByteFromRanking(training.Ranking));
        Assert.Equal(RetailCareerNode.BlankRanking, next.Ranking);
        Assert.Equal(
            RetailCareerGrade.FailedGrade,
            RetailCareerGrade.GradeByteFromRanking(next.Ranking));
        Assert.Equal(1, training.Complete);
        Assert.Equal(0, next.Complete);
        Assert.All(
            RetailFillOutEndLevelData.ForLevel100Won().SecondaryStatuses,
            status => Assert.Equal(0, status));
    }

    /// <summary>
    /// Training is not exempt from <c>UpdateGoodieStates</c>
    /// (<c>0x0041c470</c>; <c>Career.cpp:690 / 698 / 769 / 813 / 857</c>).
    /// A first-play FillOut 1.0f is grade S, so complete-100 unlocks 0 and
    /// 8 and <c>GRADE(100) &gt;= C/B/A</c> unlocks 78, 121, and 164.
    /// Mutation: skipping the recompute after ApplyUpdate leaves those
    /// five at <c>GS_UNKNOWN</c>. Score-time, base-things, and kill
    /// totals stay unclaimed. No new secondaries.
    /// </summary>
    [Fact]
    public void Level100Won_ApplyUpdateUnlocksTrainingGoodiesForAnS()
    {
        RetailCareerCampaign career = RetailCareerReCalcLinks.CreateColdTrainingSlice();
        RetailEndLevelSnapshot snapshot = RetailFillOutEndLevelData.ForLevel100Won();

        career.ApplyUpdate(snapshot);

        Assert.Equal(1.0f, snapshot.Ranking);
        Assert.Equal(
            RetailCareerGrade.PerfectGrade,
            RetailCareerGrade.GradeByteFromRanking(career.Nodes.Find(100)!.Ranking));
        Assert.Equal(
            RetailCareerGoodieState.New,
            career.Goodies.Get(RetailCareerUpdateGoodieStates.CompleteWorld100Bio));
        Assert.Equal(
            RetailCareerGoodieState.New,
            career.Goodies.Get(RetailCareerUpdateGoodieStates.CompleteWorld100Second));
        Assert.Equal(
            RetailCareerGoodieState.New,
            career.Goodies.Get(RetailCareerUpdateGoodieStates.GradeCOnWorld100));
        Assert.Equal(
            RetailCareerGoodieState.New,
            career.Goodies.Get(RetailCareerUpdateGoodieStates.GradeBOnWorld100));
        Assert.Equal(
            RetailCareerGoodieState.New,
            career.Goodies.Get(RetailCareerUpdateGoodieStates.GradeAOnWorld100));
        Assert.Equal(0, career.Nodes.Find(110)!.Complete);
        Assert.All(snapshot.SecondaryStatuses, status => Assert.Equal(0, status));
    }

    /// <summary>
    /// Lost still calls <c>UpdateGoodieStates</c> (<c>Career.cpp:382-385</c>)
    /// but world 100 is not complete, so <c>GRADE(100)</c> is the incomplete
    /// <c>'E'</c> and none of 0 / 8 / 78 / 121 / 164 become
    /// <c>GS_NEW</c>. Mutation: unlocking those five without the complete
    /// / grade predicates would fail the zeros.
    /// </summary>
    [Fact]
    public void Level100Lost_ApplyUpdateDoesNotUnlockTrainingGoodies()
    {
        RetailCareerCampaign career = RetailCareerReCalcLinks.CreateColdTrainingSlice();
        RetailEndLevelSnapshot won = RetailFillOutEndLevelData.ForLevel100Won();
        RetailEndLevelSnapshot lost = won with
        {
            FinalState = RetailCareerReCalcLinks.GameStateLevelLost,
        };

        career.ApplyUpdate(lost);

        Assert.Equal(0, career.Nodes.Find(100)!.Complete);
        Assert.Equal(
            RetailCareerGoodieState.Unknown,
            career.Goodies.Get(RetailCareerUpdateGoodieStates.CompleteWorld100Bio));
        Assert.Equal(
            RetailCareerGoodieState.Unknown,
            career.Goodies.Get(RetailCareerUpdateGoodieStates.CompleteWorld100Second));
        Assert.Equal(
            RetailCareerGoodieState.Unknown,
            career.Goodies.Get(RetailCareerUpdateGoodieStates.GradeCOnWorld100));
        Assert.Equal(
            RetailCareerGoodieState.Unknown,
            career.Goodies.Get(RetailCareerUpdateGoodieStates.GradeBOnWorld100));
        Assert.Equal(
            RetailCareerGoodieState.Unknown,
            career.Goodies.Get(RetailCareerUpdateGoodieStates.GradeAOnWorld100));
        Assert.All(lost.SecondaryStatuses, status => Assert.Equal(0, status));
    }
}
