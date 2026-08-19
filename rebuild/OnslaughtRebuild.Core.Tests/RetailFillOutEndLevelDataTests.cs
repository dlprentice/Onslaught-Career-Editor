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
    /// Last LoadWorld on Level 100 is outer RLWD. <c>CGame+0x108/+0x10c</c>
    /// are RLWD <c>+0x147ba/+0x147be</c> = 300.0 / 500.0, so
    /// <c>test ah,0x41 / jne 0x0046d79b</c> does not skip. A zero score
    /// against last-wins D=70 stores 0 at <c>0x0046d772</c> and jumps
    /// past the 0.001 replacement. Mutation: inventing a skip leaves the
    /// pre-arm 1.0f. First-play elapsed and score stay unclaimed — this
    /// does not rewrite <see cref="RetailFillOutEndLevelData.ForLevel100Won"/>.
    /// Do not invent secondaries.
    /// </summary>
    [Fact]
    public void Level100Won_ScoreTimeArmRewritesAZeroScoreToZeroBecauseRlwdDeltaIsPositive()
    {
        Assert.False(
            RetailFillOutEndLevelData.ScoreTimeArmSkips(
                RetailFillOutEndLevelData.Level100FullScoreTime,
                RetailFillOutEndLevelData.Level100PercentageScoreTime));

        float early = RetailFillOutEndLevelData.AfterScoreTimeArm(
            preArmRanking: 1.0f,
            elapsedTime: 0.0f,
            RetailFillOutEndLevelData.Level100FullScoreTime,
            RetailFillOutEndLevelData.Level100PercentageScoreTime,
            RetailFillOutEndLevelData.Level100ScorePercentage,
            score: 0,
            RetailFillOutEndLevelData.Level100SGradeScore,
            RetailFillOutEndLevelData.Level100DGradeScore);
        float late = RetailFillOutEndLevelData.AfterScoreTimeArm(
            preArmRanking: 1.0f,
            elapsedTime: 600.0f,
            RetailFillOutEndLevelData.Level100FullScoreTime,
            RetailFillOutEndLevelData.Level100PercentageScoreTime,
            RetailFillOutEndLevelData.Level100ScorePercentage,
            score: 0,
            RetailFillOutEndLevelData.Level100SGradeScore,
            RetailFillOutEndLevelData.Level100DGradeScore);

        Assert.Equal(0.0f, early);
        Assert.Equal(0.0f, late);
        Assert.NotEqual(1.0f, early);
        Assert.NotEqual(0.001f, early);
        Assert.Equal(1.0f, RetailFillOutEndLevelData.ForLevel100Won().Ranking);
        Assert.All(
            RetailFillOutEndLevelData.ForLevel100Won().SecondaryStatuses,
            status => Assert.Equal(0, status));
    }

    /// <summary>
    /// <c>game.cpp:967</c> stores <c>mRanking = 1.0f</c> before the
    /// score-time arm. Level 100's secondary count is 0, so the 0.4 / 0.6
    /// clamp never runs. Mutation: defaulting the snapshot ranking to the
    /// failed-secondary 0.6 cap fails this equality. First-play elapsed
    /// and score stay unclaimed. Do not invent secondaries.
    /// </summary>
    [Fact]
    public void Level100Won_SnapshotRankingIsThePreClampOnePointZero()
    {
        RetailEndLevelSnapshot snapshot = RetailFillOutEndLevelData.ForLevel100Won();

        Assert.Equal(1.0f, snapshot.Ranking);
        Assert.NotEqual(0.6f, snapshot.Ranking);
        Assert.NotEqual(0.4f, snapshot.Ranking);
        Assert.All(snapshot.SecondaryStatuses, status => Assert.Equal(0, status));
    }

    /// <summary>
    /// FillOut walks Size=35 and stores 1 at 0..34 (including two
    /// type-37 <c>CSafeSide</c>). Slots 35..287 stay 0. Mutation:
    /// adopting the materializer's 33 visible units leaves index 33
    /// and 34 unset. Iceberg player-kill store-0 stays open. Do not
    /// invent secondaries.
    /// </summary>
    [Fact]
    public void Level100Won_FillOutStoresOneForEachOfThirtyFiveBaseThings()
    {
        RetailEndLevelSnapshot snapshot = RetailFillOutEndLevelData.ForLevel100Won();

        Assert.Equal(RetailCareerNode.BaseThingsExistsSize, snapshot.BaseThingsLeft.Count);
        Assert.Equal(35, RetailFillOutEndLevelData.Level100BaseWorldThingCount);
        Assert.NotEqual(33, RetailFillOutEndLevelData.Level100BaseWorldThingCount);
        Assert.Equal(1, snapshot.BaseThingsLeft[33]);
        Assert.Equal(1, snapshot.BaseThingsLeft[34]);
        Assert.Equal(0, snapshot.BaseThingsLeft[35]);
        Assert.Equal(35, snapshot.BaseThingsLeft.Count(value => value == 1));
        Assert.All(
            snapshot.BaseThingsLeft.Take(35),
            value => Assert.Equal(1, value));
        Assert.All(
            snapshot.BaseThingsLeft.Skip(35),
            value => Assert.Equal(0, value));
        Assert.All(snapshot.SecondaryStatuses, status => Assert.Equal(0, status));
    }

    /// <summary>
    /// Kill readout is ctor-zero plus <c>0x004d30d0</c> ConfirmedKill
    /// increments, not an authored L100 constant. A first-play Won that
    /// never takes that increment snapshots five zeros. Career still
    /// skips world 100. Mutation: writing a non-zero authored vector
    /// fails the zeros. Do not invent secondaries.
    /// </summary>
    [Fact]
    public void Level100Won_FirstPlayKillReadoutIsFiveZerosUnlessConfirmedKill()
    {
        RetailEndLevelSnapshot snapshot = RetailFillOutEndLevelData.ForLevel100Won();

        Assert.Equal(
            new[] { 0, 0, 0, 0, 0 },
            snapshot.ThingsKilled);
        Assert.Equal(
            RetailCareerCounters.KilledTypeCount,
            snapshot.ThingsKilled.Count);
        Assert.Equal(
            RetailFillOutEndLevelData.FirstPlayThingsKilled(),
            snapshot.ThingsKilled);
        Assert.All(snapshot.SecondaryStatuses, status => Assert.Equal(0, status));
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
