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
}
