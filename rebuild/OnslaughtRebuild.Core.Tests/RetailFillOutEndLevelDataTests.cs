// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Core.Tests;

/// <summary>
/// Parity tests for the Level 100 Won snapshot
/// <c>CGame::FillOutEndLevelData</c> hands to career. Source
/// <c>game.cpp:910-1043</c>; retail identity <c>0x0046D470</c>.
/// The secondary predicate is already pinned; this suite pins that
/// FillOut does not consult it when the authored secondary count is 0.
/// </summary>
public sealed class RetailFillOutEndLevelDataTests
{
    [Fact]
    public void Level100Won_SnapshotIsWorld100StateWonWithNoSecondaries()
    {
        RetailEndLevelSnapshot snapshot = RetailFillOutEndLevelData.ForLevel100Won();

        Assert.Equal(100, snapshot.WorldFinished);
        Assert.Equal(RetailCareerReCalcLinks.GameStateLevelWon, snapshot.FinalState);
        Assert.Equal(
            RetailEndLevelObjectives.SecondaryObjectiveCount,
            snapshot.SecondaryStatuses.Count);
        Assert.All(snapshot.SecondaryStatuses, status => Assert.Equal(0, status));
        Assert.Equal(0, RetailFillOutEndLevelData.Level100SecondaryCount);
        Assert.Equal(4, RetailFillOutEndLevelData.Level100PrimaryCount);

        RetailSecondaryObjectiveVerdict verdict =
            RetailEndLevelObjectives.IsAllSecondaryObjectivesComplete(
                snapshot.SecondaryStatuses);
        Assert.False(verdict.Result);
        Assert.False(verdict.AnyObjectiveSet);
    }

    /// <summary>
    /// FillOut copies the ten primary <c>GetStatus()</c> words. After a
    /// Level 100 win those are four <c>MOS_COMPLETE</c> (1) and six
    /// unset slots — already pinned on
    /// <see cref="RetailGameObjectiveCount.Level100WonPrimaryStatuses"/>.
    /// That is not the rebuild mission enum's
    /// <c>Level100PrimaryObjectiveStatus.Complete = 2</c>. Mutation:
    /// writing 2 for complete fails the snapshot equality. Secondaries
    /// stay unset; do not invent them.
    /// </summary>
    [Fact]
    public void Level100Won_SnapshotCarriesFourMosCompletePrimariesNotTheMissionEnumTwo()
    {
        RetailEndLevelSnapshot snapshot = RetailFillOutEndLevelData.ForLevel100Won();

        Assert.Equal(
            RetailGameObjectiveCount.Level100WonPrimaryStatuses(),
            snapshot.PrimaryStatuses);
        Assert.Equal(new[] { 1, 1, 1, 1, 0, 0, 0, 0, 0, 0 }, snapshot.PrimaryStatuses);
        Assert.DoesNotContain(
            (int)Level100PrimaryObjectiveStatus.Complete,
            snapshot.PrimaryStatuses);
        Assert.All(snapshot.SecondaryStatuses, status => Assert.Equal(0, status));
    }

    /// <summary>
    /// <c>game.cpp:1028</c> is <c>if (GetNumSecondaryObjectives())</c>.
    /// Level 100's count is 0, so neither the 0.4 floor nor the 0.6 cap
    /// runs. Mutation: applying the failed-secondary 0.6 cap because the
    /// predicate is FALSE would turn a 1.0 ranking into 0.6; applying the
    /// completed-secondary 0.4 floor would turn a 0.0 ranking into 0.4.
    /// </summary>
    [Theory]
    [InlineData(1.0f)]
    [InlineData(0.0f)]
    [InlineData(0.75f)]
    public void Level100Won_DoesNotClampRankingBecauseThereAreNoSecondaries(float ranking)
    {
        float after = RetailFillOutEndLevelData.AfterSecondaryRankingClamp(
            ranking,
            RetailFillOutEndLevelData.Level100SecondaryCount,
            RetailFillOutEndLevelData.UnsetSecondaryStatuses());

        Assert.Equal(ranking, after);
        Assert.NotEqual(0.6f, after);
        Assert.NotEqual(0.4f, after == ranking ? -1.0f : after);
    }

    [Fact]
    public void Level100Won_FillOutSnapshotDrivesTheAlreadyPinnedCareerUpdate()
    {
        RetailCareerCampaign career = RetailCareerReCalcLinks.CreateColdTrainingSlice();
        RetailEndLevelSnapshot snapshot = RetailFillOutEndLevelData.ForLevel100Won();

        career.ApplyUpdate(snapshot);

        RetailCareerNode training = career.Nodes.Find(100)!;
        RetailCareerNodeLink lower = career.GetLink(training.LowerLink)!;
        RetailCareerNodeLink higher = career.GetLink(training.HigherLink)!;

        Assert.Equal(1, training.Complete);
        Assert.Equal(RetailCareerNodeLink.Complete, lower.LinkType);
        Assert.Equal(RetailCareerNodeLink.NotComplete, higher.LinkType);
    }
}
