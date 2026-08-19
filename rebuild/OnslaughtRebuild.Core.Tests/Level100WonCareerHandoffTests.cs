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

    /// <summary>
    /// FrontEndHandoffReady applies the already-pinned FillOut 1.0f
    /// ranking only onto world 100 (grade S). World 110 stays
    /// <c>BlankRanking</c> / grade E. Mutation: stamping 1.0 onto the
    /// unlocked child after <c>TryApply</c> fails the 110 equality.
    /// Score-time, base-things, kills, and goodies stay unclaimed.
    /// No new secondaries.
    /// </summary>
    [Fact]
    public void FrontEndHandoffReadyAfterWon_StoresFillOutRankingOnlyOnWorld100()
    {
        Level100Mission mission = DriveReleasedFirstPlayToTerminal();

        Assert.Equal(Level100MissionOutcome.Won, mission.Snapshot.Outcome);
        Assert.Equal(
            Level100MissionTerminalState.FrontEndHandoffReady,
            mission.Snapshot.TerminalState);

        RetailCareerNode training = mission.Career.Nodes.Find(100)!;
        RetailCareerNode next = mission.Career.Nodes.Find(110)!;
        Assert.Equal(1.0f, training.Ranking);
        Assert.Equal(
            RetailCareerGrade.PerfectGrade,
            RetailCareerGrade.GradeByteFromRanking(training.Ranking));
        Assert.Equal(RetailCareerNode.BlankRanking, next.Ranking);
        Assert.Equal(
            RetailCareerGrade.FailedGrade,
            RetailCareerGrade.GradeByteFromRanking(next.Ranking));
        Assert.Equal(0, next.Complete);
        Assert.All(
            RetailFillOutEndLevelData.ForLevel100Won().SecondaryStatuses,
            status => Assert.Equal(0, status));
    }

    /// <summary>
    /// First-play <c>SetSlotSave</c> writes <c>SLOT_TUTORIAL_1..4</c>
    /// (63..66). FillOut copies those 32 words and <c>ApplyUpdate</c>
    /// assigns them over career <c>mSlots</c>, so a leftover bit dies.
    /// Mutation: <c>ForLevel100Won</c> carrying empty slot words leaves
    /// 63..66 unset after the handoff. No new secondaries.
    /// </summary>
    [Fact]
    public void FrontEndHandoffReadyAfterWon_OverwritesCareerSlotsFromFillOutTutorialBits()
    {
        Level100Mission mission = DriveReleasedFirstPlayToTerminal(
            career => career.Slots.SetSlot(1, 1));

        Assert.Equal(Level100MissionOutcome.Won, mission.Snapshot.Outcome);
        Assert.Equal(
            Level100MissionTerminalState.FrontEndHandoffReady,
            mission.Snapshot.TerminalState);

        RetailEndLevelSnapshot snapshot = RetailFillOutEndLevelData.ForLevel100Won();
        Assert.Equal(
            snapshot.SlotWords,
            mission.Career.Slots.Words);
        Assert.Equal(0, mission.Career.Slots.GetSlot(1));
        Assert.Equal(
            1,
            mission.Career.Slots.GetSlot(
                RetailCareerSlotHandoff.TutorialIntroductionSlot));
        Assert.Equal(
            1,
            mission.Career.Slots.GetSlot(
                RetailCareerSlotHandoff.TutorialPulseCannonSlot));
        Assert.Equal(
            1,
            mission.Career.Slots.GetSlot(
                RetailCareerSlotHandoff.TutorialVulcanCannonSlot));
        Assert.Equal(
            1,
            mission.Career.Slots.GetSlot(
                RetailCareerSlotHandoff.TutorialStatusBarsSlot));
        Assert.All(snapshot.SecondaryStatuses, status => Assert.Equal(0, status));
    }

    /// <summary>
    /// FrontEndHandoffReady after the released first-play script applies
    /// the already-pinned FillOut 1.0f / S, so <c>UpdateGoodieStates</c>
    /// writes <c>GS_NEW</c> on 0, 8, 78, 121, and 164. Mutation: skipping
    /// <c>ApplyUpdate</c> on the handoff leaves those five at
    /// <c>GS_UNKNOWN</c>. Score-time, base-things, and kill totals stay
    /// unclaimed. No new secondaries.
    /// </summary>
    [Fact]
    public void FrontEndHandoffReadyAfterWon_UnlocksTrainingGoodiesForAnS()
    {
        Level100Mission mission = DriveReleasedFirstPlayToTerminal();

        Assert.Equal(Level100MissionOutcome.Won, mission.Snapshot.Outcome);
        Assert.Equal(
            Level100MissionTerminalState.FrontEndHandoffReady,
            mission.Snapshot.TerminalState);
        Assert.Equal(
            RetailCareerGoodieState.New,
            mission.Career.Goodies.Get(RetailCareerUpdateGoodieStates.CompleteWorld100Bio));
        Assert.Equal(
            RetailCareerGoodieState.New,
            mission.Career.Goodies.Get(RetailCareerUpdateGoodieStates.CompleteWorld100Second));
        Assert.Equal(
            RetailCareerGoodieState.New,
            mission.Career.Goodies.Get(RetailCareerUpdateGoodieStates.GradeCOnWorld100));
        Assert.Equal(
            RetailCareerGoodieState.New,
            mission.Career.Goodies.Get(RetailCareerUpdateGoodieStates.GradeBOnWorld100));
        Assert.Equal(
            RetailCareerGoodieState.New,
            mission.Career.Goodies.Get(RetailCareerUpdateGoodieStates.GradeAOnWorld100));
        Assert.Equal(
            RetailCareerGrade.PerfectGrade,
            RetailCareerGrade.GradeByteFromRanking(mission.Career.Nodes.Find(100)!.Ranking));
        Assert.All(
            RetailFillOutEndLevelData.ForLevel100Won().SecondaryStatuses,
            status => Assert.Equal(0, status));
    }

    /// <summary>
    /// <c>CGame::RestartLoopRunLevel</c> calls FillOut only after the
    /// main loop quits (<c>game.cpp:1552</c>), and that quit waits for
    /// the already-pinned 5.0 f Won store (<c>game.cpp:1997-2004</c>).
    /// <c>CFrontEnd::Init</c> then calls <c>CAREER.Update</c>
    /// (<c>FrontEnd.cpp:67</c>). Mutation: letting
    /// <see cref="Level100WonCareerHandoff.TryApply"/> accept
    /// <c>SuccessCountdown</c> unlocks world 110 before the overlay
    /// elapses. Score-time, base-things, kills, and goodies stay
    /// unclaimed. No new secondaries.
    /// </summary>
    [Fact]
    public void SuccessCountdownDoesNotApplyFillOutEvenIfWonIsClaimed()
    {
        var handoff = new Level100WonCareerHandoff();

        Assert.False(handoff.TryApply(
            Level100MissionOutcome.Won,
            Level100MissionTerminalState.SuccessCountdown));

        AssertCareerStillCold(handoff.Career);
        Assert.All(
            RetailFillOutEndLevelData.ForLevel100Won().SecondaryStatuses,
            status => Assert.Equal(0, status));
    }

    /// <summary>
    /// First-play <c>LevelWon</c> starts the already-pinned 5.0 f
    /// overlay and leaves the cold career locked until those ticks
    /// elapse. Mutation: applying FillOut from <c>DeclareWon</c>
    /// unlocks 110 while <c>SuccessCountdown</c> is still running.
    /// </summary>
    [Fact]
    public void FrontEndHandoffReadyAfterWon_WaitsForTheFiveSecondCountdown()
    {
        Level100Mission mission = DriveReleasedFirstPlayUntilWon();

        Assert.Equal(Level100MissionOutcome.Won, mission.Snapshot.Outcome);
        Assert.Equal(
            Level100MissionTerminalState.SuccessCountdown,
            mission.Snapshot.TerminalState);
        Assert.Equal(
            RetailGameEndCountdown.WonTicks,
            mission.Snapshot.TerminalTicksRemaining);
        AssertCareerStillCold(mission.Career);

        for (int tick = 0; tick < RetailGameEndCountdown.WonTicks; tick++)
        {
            mission.AdvanceTick(SimulationConstants.MaximumHull);
        }

        Assert.Equal(
            Level100MissionTerminalState.FrontEndHandoffReady,
            mission.Snapshot.TerminalState);
        Assert.Equal(0, mission.Snapshot.TerminalTicksRemaining);
        RetailCareerNode training = mission.Career.Nodes.Find(100)!;
        RetailCareerNodeLink lower = mission.Career.GetLink(training.LowerLink)!;
        Assert.Equal(1, training.Complete);
        Assert.Equal(1, mission.Career.CareerInProgress);
        Assert.Equal(RetailCareerNodeLink.Complete, lower.LinkType);
        Assert.All(
            RetailFillOutEndLevelData.ForLevel100Won().SecondaryStatuses,
            status => Assert.Equal(0, status));
    }

    /// <summary>
    /// <c>CCareer::Update</c> at <c>0x0041BD06</c> is
    /// <c>cmp eax, 5</c> / <c>jne</c>. Lost is 4, so FillOut is never
    /// applied even if the handoff state is claimed. Mutation: dropping
    /// the Won check from <see cref="Level100WonCareerHandoff.TryApply"/>
    /// unlocks world 110 on Lost.
    /// </summary>
    [Fact]
    public void LostDoesNotApplyFillOutEvenIfFrontEndHandoffReadyIsClaimed()
    {
        var handoff = new Level100WonCareerHandoff();

        Assert.False(handoff.TryApply(
            Level100MissionOutcome.Lost,
            Level100MissionTerminalState.FrontEndHandoffReady));

        RetailCareerNode training = handoff.Career.Nodes.Find(100)!;
        RetailCareerNodeLink lower = handoff.Career.GetLink(training.LowerLink)!;
        Assert.Equal(0, training.Complete);
        Assert.Equal(0, handoff.Career.CareerInProgress);
        Assert.Equal(RetailCareerNodeLink.NotComplete, lower.LinkType);
    }

    /// <summary>
    /// Player-reproducible Lost: Broke-Tutorial reaches
    /// <c>FailureMenuReady</c>, never <c>FrontEndHandoffReady</c>, and
    /// the cold career stays locked. Mutation: calling
    /// <c>TryApply</c> from the Lost countdown unlocks 110.
    /// </summary>
    [Fact]
    public void BrokeTutorialLost_DoesNotApplyFillOutOrUnlockWorld110()
    {
        Level100ActorDefinitionSet definitions = Level100TestActorDefinitions.Create();
        var actors = new Level100ActorRegistry(definitions);
        var mission = new Level100Mission(
            actors,
            actors.GetThingRef("Player 1")!.Value);

        Assert.True(mission.SubmitInput(Level100MissionInput.BrokeTutorial));

        const int settleTicks = 100 * SimulationConstants.TicksPerSecond;
        for (int tick = 0; tick < settleTicks; tick++)
        {
            mission.AdvanceTick(SimulationConstants.MaximumHull);
            if (mission.Snapshot.TerminalState ==
                Level100MissionTerminalState.FailureMenuReady)
            {
                break;
            }
        }

        Assert.Equal(Level100MissionOutcome.Lost, mission.Snapshot.Outcome);
        Assert.Equal(
            Level100MissionFailureReason.TutorialBroken,
            mission.Snapshot.FailureReason);
        Assert.Equal(
            Level100MissionTerminalState.FailureMenuReady,
            mission.Snapshot.TerminalState);
        Assert.NotEqual(
            Level100MissionTerminalState.FrontEndHandoffReady,
            mission.Snapshot.TerminalState);

        RetailCareerNode training = mission.Career.Nodes.Find(100)!;
        RetailCareerNodeLink lower = mission.Career.GetLink(training.LowerLink)!;
        Assert.Equal(0, training.Complete);
        Assert.Equal(0, mission.Career.CareerInProgress);
        Assert.Equal(RetailCareerNodeLink.NotComplete, lower.LinkType);
        Assert.All(
            RetailFillOutEndLevelData.ForLevel100Won().SecondaryStatuses,
            status => Assert.Equal(0, status));
    }

    private static void AssertCareerStillCold(RetailCareerCampaign career)
    {
        RetailCareerNode training = career.Nodes.Find(100)!;
        RetailCareerNodeLink lower = career.GetLink(training.LowerLink)!;
        Assert.Equal(0, training.Complete);
        Assert.Equal(0, career.CareerInProgress);
        Assert.Equal(RetailCareerNodeLink.NotComplete, lower.LinkType);
    }

    private static Level100Mission DriveReleasedFirstPlayUntilWon()
    {
        Level100Mission mission = CreateFirstPlayMission();
        const int settleTicks = 100 * SimulationConstants.TicksPerSecond;

        Settle(mission, settleTicks);
        for (int index = 0; index < ReleasedFirstPlayEvents.Length; index++)
        {
            string eventName = ReleasedFirstPlayEvents[index];
            Assert.True(
                mission.QueueExternalEvent(eventName),
                $"The released LevelScript refused the event '{eventName}'.");
            bool lastEvent = index == ReleasedFirstPlayEvents.Length - 1;
            if (lastEvent)
            {
                for (int tick = 0; tick < settleTicks; tick++)
                {
                    mission.AdvanceTick(SimulationConstants.MaximumHull);
                    if (mission.Snapshot.Outcome == Level100MissionOutcome.Won)
                    {
                        return mission;
                    }
                }

                Assert.Fail("The released first-play script never declared Won.");
            }

            Settle(mission, settleTicks);
        }

        return mission;
    }

    private static Level100Mission CreateFirstPlayMission(
        Action<RetailCareerCampaign>? seedCareer = null)
    {
        Level100ActorDefinitionSet definitions = Level100TestActorDefinitions.Create();
        var actors = new Level100ActorRegistry(definitions);
        Level100ActorId player = actors.GetThingRef("Player 1")!.Value;
        var mission = new Level100Mission(
            actors,
            player,
            new Level100TutorialProgress(false, false, false, false),
            initialPlayerHealth: SimulationConstants.MaximumHull);
        seedCareer?.Invoke(mission.Career);
        return mission;
    }

    private static void Settle(Level100Mission mission, int settleTicks)
    {
        for (int index = 0; index < settleTicks; index++)
        {
            mission.AdvanceTick(SimulationConstants.MaximumHull);
        }
    }

    private static Level100Mission DriveReleasedFirstPlayToTerminal(
        Action<RetailCareerCampaign>? seedCareer = null)
    {
        Level100Mission mission = CreateFirstPlayMission(seedCareer);

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
