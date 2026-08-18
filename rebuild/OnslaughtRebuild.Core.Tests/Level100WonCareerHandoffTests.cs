// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.TestSupport;

namespace OnslaughtRebuild.Core.Tests;

/// <summary>
/// Pins the mission-path wire from Level 100
/// <see cref="Level100MissionTerminalState.FrontEndHandoffReady"/> after Won
/// through the already-pinned
/// <see cref="RetailFillOutEndLevelData.ForLevel100Won"/> snapshot into
/// <see cref="RetailCareerCampaign.ApplyUpdate"/>. FillOut and ReCalcLinks
/// stay as they are; this suite only proves the mission reaches them.
/// </summary>
public sealed class Level100WonCareerHandoffTests
{
    /// <summary>
    /// The eleven named events the released side scripts post, in first-play
    /// order. Copied from
    /// <c>Level100MissionTests.ReleasedLevelScript_RunsTheCompleteFirstPlayTutorialToLevelWon</c>
    /// so this test does not invent a shorter script path.
    /// </summary>
    private static readonly string[] ReleasedFirstPlayEvents =
    [
        "Reached Target Zone 1",
        "Reached Firing Range",
        "Static Target Destroyed", "Static Target Destroyed",
        "Static Target Destroyed", "Static Target Destroyed",
        "Static Target 2 Destroyed", "Static Target 2 Destroyed",
        "Static Target 2 Destroyed",
        "Moving Target Destroyed", "Moving Target Destroyed",
        "Moving Target Destroyed", "Moving Target Destroyed",
        "Moving Target Destroyed", "Moving Target Destroyed",
        "Reached Target Zone 2",
        "Airborne Target 1 Destroyed", "Airborne Target 1 Destroyed",
        "Airborne Target 1 Destroyed",
        "Reached Target Zone 3",
        "Airborne Target 2 Destroyed", "Airborne Target 2 Destroyed",
        "Airborne Target 2 Destroyed", "Airborne Target 2 Destroyed",
        "Airborne Target 2 Destroyed", "Airborne Target 2 Destroyed",
        "Reached Target Zone 4",
    ];

    /// <summary>
    /// After the released first-play script reaches
    /// <c>FrontEndHandoffReady</c>, career must already hold the FillOut Won
    /// snapshot: world 100 complete, lower link to 110 complete, dummy higher
    /// still <c>CN_NOT_COMPLETE</c>. Mutation: reaching the handoff without
    /// calling <c>ApplyUpdate(ForLevel100Won())</c> leaves 110 locked.
    /// </summary>
    [Fact]
    public void FrontEndHandoffReadyAfterWon_AppliesFillOutAndUnlocksWorld110()
    {
        Level100Mission mission = DriveReleasedFirstPlayToTerminal();

        Assert.Equal(Level100MissionOutcome.Won, mission.Snapshot.Outcome);
        Assert.Equal(
            Level100MissionTerminalState.FrontEndHandoffReady,
            mission.Snapshot.TerminalState);

        RetailCareerCampaign career = mission.Career;
        RetailCareerNode training = career.Nodes.Find(100)!;
        RetailCareerNode next = career.Nodes.Find(110)!;
        RetailCareerNodeLink lower = career.GetLink(training.LowerLink)!;
        RetailCareerNodeLink higher = career.GetLink(training.HigherLink)!;

        Assert.Equal(1, training.Complete);
        Assert.Equal(1, career.CareerInProgress);
        Assert.Equal(0, next.Complete);
        Assert.Equal(1, lower.ToNode);
        Assert.Equal(RetailCareerNodeLink.Complete, lower.LinkType);
        Assert.Equal(-1, higher.ToNode);
        Assert.Equal(RetailCareerNodeLink.NotComplete, higher.LinkType);
        Assert.All(
            RetailFillOutEndLevelData.ForLevel100Won().SecondaryStatuses,
            status => Assert.Equal(0, status));
    }

    private static Level100Mission DriveReleasedFirstPlayToTerminal()
    {
        Level100ActorDefinitionSet definitions = Level100TestActorDefinitions.Create();
        var actors = new Level100ActorRegistry(definitions);
        Level100ActorId player = actors.GetThingRef("Player 1")!.Value;
        var mission = new Level100Mission(
            actors,
            player,
            new Level100TutorialProgress(false, false, false, false),
            initialPlayerHealth: SimulationConstants.MaximumHull);

        const int settleTicks = 100 * SimulationConstants.TicksPerSecond;
        void Settle()
        {
            for (int index = 0; index < settleTicks; index++)
            {
                mission.AdvanceTick(SimulationConstants.MaximumHull);
            }
        }

        Settle();
        foreach (string eventName in ReleasedFirstPlayEvents)
        {
            Assert.True(
                mission.QueueExternalEvent(eventName),
                $"The released LevelScript refused the event '{eventName}'.");
            Settle();
        }

        return mission;
    }
}
