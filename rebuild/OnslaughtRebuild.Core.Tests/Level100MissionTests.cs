// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.TestSupport;

namespace OnslaughtRebuild.Core.Tests;

public sealed class Level100MissionTests
{
    private static readonly Level100TutorialProgress CompletedTutorialSlots =
        new(Introduction: true, PulseCannon: true, VulcanCannon: true, StatusBars: true);

    [Fact]
    public void ReleasedPrograms_InitializeAgainstOneCanonicalActorRegistry()
    {
        Level100ActorDefinitionSet definitions = Level100TestActorDefinitions.Create();
        var actors = new Level100ActorRegistry(definitions);
        Level100ActorId player = actors.GetThingRef("Player 1")!.Value;
        var actorScripts = new Level100ActorScriptRuntime(actors, player);
        actorScripts.InitializeReleasedScripts();
        var mission = new Level100Mission(
            actors,
            player,
            CompletedTutorialSlots,
            initialPlayerHealth: 735);

        Level100MissionSnapshot missionState = mission.Snapshot;
        Level100ActorScriptRuntimeSnapshot actorState = actorScripts.Snapshot;
        Assert.Equal(
            "73eb349b9c4b5c5d7294b2183cd4d4aebe024c5d3c8cda9be685bd1463ed6fb1",
            missionState.ProgramSha256);
        Assert.Equal(334, missionState.Locals.Count);
        Assert.False(missionState.FlightModeEnabled);
        Assert.Equal(735, missionState.InitialPlayerHealth);
        Assert.Contains(actorState.Instances, instance =>
            instance.ActorId is null && instance.ProgramName == "Setup");
        Assert.Contains(actorState.Instances, instance =>
            instance.ActorId == actors.GetThingRef("Player 1"));
        Assert.All(actorState.Instances, instance => Assert.True(instance.Initialized));
    }

    [Fact]
    public void ActorRuntimeSnapshot_RoundTripsAndChangesCanonicalWorldHash()
    {
        Level100ActorDefinitionSet definitions = Level100TestActorDefinitions.Create();
        var actors = new Level100ActorRegistry(definitions);
        Level100ActorId player = actors.GetThingRef("Player 1")!.Value;
        var runtime = new Level100ActorScriptRuntime(actors, player);
        runtime.InitializeReleasedScripts();
        Level100ActorScriptRuntimeSnapshot snapshot = runtime.Snapshot;

        var restored = new Level100ActorScriptRuntime(actors, player, snapshot);
        WorldSnapshot envelope = new Simulation(0x100u, definitions).Snapshot;
        string originalHash = StateHasher.ComputeHex(envelope with
        {
            Level100Actors = actors.Snapshot,
            Level100ActorScripts = snapshot,
        });
        string restoredHash = StateHasher.ComputeHex(envelope with
        {
            Level100Actors = actors.Snapshot,
            Level100ActorScripts = restored.Snapshot,
        });
        Assert.Equal(originalHash, restoredHash);

        int changedInstanceIndex = snapshot.Instances
            .Select((instance, index) => (instance, index))
            .First(item => item.instance.Locals.Count > 0)
            .index;
        Level100ActorScriptInstanceSnapshot source = snapshot.Instances[changedInstanceIndex];
        Level100ScriptLocalSnapshot local = source.Locals[0];
        Level100ScriptValueSnapshot changedValue = local.Value with
        {
            Scalar = unchecked(local.Value.Scalar + 1),
        };
        Level100ActorScriptInstanceSnapshot changedInstance = source with
        {
            Locals = source.Locals
                .Select((item, index) => index == 0 ? item with { Value = changedValue } : item)
                .ToArray(),
        };
        Level100ActorScriptRuntimeSnapshot changed = snapshot with
        {
            Instances = snapshot.Instances
                .Select((item, index) => index == changedInstanceIndex ? changedInstance : item)
                .ToArray(),
        };
        Assert.NotEqual(originalHash, StateHasher.ComputeHex(envelope with
        {
            Level100Actors = actors.Snapshot,
            Level100ActorScripts = changed,
        }));

        Level100ActorScriptRuntimeSnapshot wrongProgram = snapshot with
        {
            Instances = snapshot.Instances
                .Select((item, index) => index == 0
                    ? item with { ProgramSha256 = new string('0', 64) }
                    : item)
                .ToArray(),
        };
        Assert.Throws<ArgumentException>(() =>
            new Level100ActorScriptRuntime(actors, player, wrongProgram));

        Level100ActorScriptInstanceSnapshot waiting = snapshot.Instances.First(instance =>
            instance.Continuations.Count > 0);
        Level100ActorScriptRuntimeSnapshot activeExecution = snapshot with
        {
            Instances = snapshot.Instances
                .Select(instance => ReferenceEquals(instance, waiting)
                    ? instance with
                    {
                        ActiveExecution = instance.Continuations[0].Execution,
                    }
                    : instance)
                .ToArray(),
        };
        Assert.Throws<ArgumentException>(() =>
            new Level100ActorScriptRuntime(actors, player, activeExecution));
    }

    [Fact]
    public void TargetTank1_StopsAtTheReleasedWaypointMechanicsBoundary()
    {
        Level100ActorDefinitionSet definitions = Level100TestActorDefinitions.Create();
        var actors = new Level100ActorRegistry(definitions);
        Level100ActorId player = actors.GetThingRef("Player 1")!.Value;
        var runtime = new Level100ActorScriptRuntime(actors, player);
        runtime.InitializeReleasedScripts();
        Level100ActorSnapshot target = actors.Snapshot.Actors.Single(actor =>
            actor.TargetGroup == Level100MissionTargetGroup.StaticTargets &&
            actor.TargetOrdinal == 1);

        Assert.Equal("test:spawn:test:tank-factory:Target Tank:SpawnerA:TargetTank1",
            target.DefinitionIdentity);
        Assert.Equal("Target Tank", target.DefinitionName);
        Assert.Equal("TargetTank1", target.ScriptName);
        Assert.Equal("SpawnerA", target.SpawnerName);
        Assert.Equal(actors.GetThingRef("Tank Factory"), target.SpawnOwnerId);
        // Authored spawn elevation is -126. Released CThing::Init ground-clamps
        // it, and the registry now seats Target Tank/Target Truck actors at
        // ground + CoreGroundOriginOffsetMillimeters (200 + 100 here), the same
        // expression Level100ActorMechanics applies once the actor moves.
        Assert.Equal(new SimVector3(3_439, 300, 21_051), target.Pose!.PositionMillimeters);
        Assert.Equal(
            new Level100FloatBasis3Bits(
                -1_101_128_975, 0, -1_082_529_832,
                0, 1_065_353_216, 0,
                1_064_953_816, 0, -1_101_128_975),
            target.Pose.BasisFloatBits);

        Level100ActorScriptCommand command = Assert.Single(runtime.DrainCommands(), item =>
            item.ActorId == target.ActorId &&
            item.Kind == Level100ActorScriptCommandKind.FollowWaypointWait);
        Assert.Equal(target.ActorId, command.ActorId);
        Assert.Equal(Level100ActorScriptCommandKind.FollowWaypointWait, command.Kind);
        Assert.Equal("Target Tank Path 1", command.Argument);
        Level100ActorScriptInstanceSnapshot instance = runtime.Snapshot.Instances.Single(
            item => item.ActorId == target.ActorId);
        Level100ActorScriptContinuationSnapshot continuation = Assert.Single(
            instance.Continuations);
        Assert.Equal(Level100ActorScriptWaitKind.FollowWaypoint, continuation.WaitKind);
        Assert.Equal("Target Tank Path 1", continuation.WaitArgument);
        Assert.Null(continuation.DueTick);
    }

    /// <summary>
    /// The complete released Level 100 tutorial, driven by exactly the eleven
    /// named events its own side scripts post (LevelScript.msl SHA-256
    /// d51f8864564b5bde872092ec822df5af49daac16563f500719135f1a8c6c04a4:
    /// TargetZone1..4 post the "Reached ..." events, StaticTarget/StaticTarget2/
    /// TargetTank2 post the destruction events). This pins the whole first-play
    /// script path -- every character message in order, all four primary
    /// objectives, the four saved tutorial slots and the terminal handoff -- so
    /// that the mission-program layer cannot silently regress to a prefix while
    /// mechanics, AI and presentation catch up.
    /// </summary>
    [Fact]
    public void ReleasedLevelScript_RunsTheCompleteFirstPlayTutorialToLevelWon()
    {
        Level100ActorDefinitionSet definitions = Level100TestActorDefinitions.Create();
        var actors = new Level100ActorRegistry(definitions);
        Level100ActorId player = actors.GetThingRef("Player 1")!.Value;
        // Default progress == every SLOT_TUTORIAL_n FALSE, i.e. a first play,
        // which is the longest released path through the script.
        var mission = new Level100Mission(
            actors,
            player,
            new Level100TutorialProgress(false, false, false, false),
            initialPlayerHealth: 735);

        var messageIds = new List<int>();
        var postedEvents = new List<string>();
        var completedObjectives = new List<int>();
        var savedSlots = new List<int>();

        void Drain()
        {
            foreach (Level100MissionEvent item in mission.DrainEvents())
            {
                switch (item)
                {
                    case Level100MessageRequested message:
                        messageIds.Add(message.MessageId);
                        break;
                    case Level100MissionEventPosted posted:
                        postedEvents.Add(posted.EventName);
                        break;
                    case Level100TutorialSlotSaved slot:
                        savedSlots.Add(slot.Slot);
                        break;
                    case Level100PrimaryObjectiveChanged objective
                        when objective.Status == Level100PrimaryObjectiveStatus.Complete:
                        completedObjectives.Add(objective.Objective);
                        break;
                }
            }
        }

        // The longest released wait in one step is Pause(30) plus its adjacent
        // message waits, so 3000 ticks (100 s at 30 Hz) settles every step.
        const int SettleTicks = 3_000;
        void Settle()
        {
            for (int index = 0; index < SettleTicks; index++)
            {
                mission.AdvanceTick(735);
                Drain();
            }
        }

        Drain();
        Settle();

        string[] releasedEventSequence =
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

        foreach (string eventName in releasedEventSequence)
        {
            Assert.True(
                mission.QueueExternalEvent(eventName),
                $"The released LevelScript refused the event '{eventName}'.");
            Drain();
            Settle();
        }

        // Every PlayCharMessage/PlayCharMessageWait the released first-play
        // path requests, in order. HUD_01, HUD_02, HUD_06, TUTORIAL_MESSAGE_LOG,
        // TUTORIAL_TECHNICIAN_01, TUTORIAL_13_MOD, TUTORIAL_01,
        // TUTORIAL_SCANNER (init), TUTORIAL_02 (zone 1), TUTORIAL_03, HUD_05,
        // TUTORIAL_PULSE_CANNON, TUTORIAL_OPEN_FIRE, TUTORIAL_PULSE_CANNON_2
        // (firing range), then the Vulcan, zoom, dodge, transform, throttle,
        // strafe and landing beats through TUTORIAL_11.
        Assert.Equal(
            [
                292562, 293386, 296682, -1575499396, -257967449, 82987417,
                4422830, 175347826, 4458134, 4493438, 295858, 1339691000,
                669198996, -1715818922, -1616775312, -1860407443, 864965454,
                4564046, 22775962, 294210, 295034, 667656903, 150647733,
                151778876, 1326027769, 4528742, 165861931, 4599350, 1062059777,
                4475837, 4705262, 4634654, 80260569, 4669958, 4440532,
            ],
            messageIds);

        // The events LevelScript posts back to its own side scripts. It has no
        // listener for any of them, so each is an outbound fact only.
        Assert.Equal(
            [
                "Activate Static Targets",
                "Activate Static Targets 2",
                "Activate Moving Targets",
                "Trainer Attack",
                "Cease Trainer Attack",
                "Activate Airborne Targets 1",
                "Activate Airborne Targets 2",
            ],
            postedEvents);

        // Objective 2 is completed on each of the three "Static Target 2
        // Destroyed" events, exactly as the released script does.
        Assert.Equal([1, 2, 2, 2, 3, 4], completedObjectives);
        Assert.Equal([63, 64, 65, 66], savedSlots);

        Level100MissionSnapshot final = mission.Snapshot;
        Assert.Equal(Level100MissionOutcome.Won, final.Outcome);
        Assert.Equal(Level100MissionTerminalState.FrontEndHandoffReady, final.TerminalState);
        Assert.Equal(
            new Level100TutorialProgress(true, true, true, true),
            final.TutorialProgress);
        Assert.All(
            final.PrimaryObjectives,
            objective => Assert.Equal(
                Level100PrimaryObjectiveStatus.Complete,
                objective.Status));
        // The clean dodge exercise never posts "Evade Failed", so the released
        // TUTORIAL_DODGE_GOOD branch awards its +50 and nothing deducts.
        Assert.Equal(50, final.ScoreDelta);
        Assert.True(final.FlightModeEnabled);
    }

    [Fact]
    public void ExternalTerminalFacts_StopTheReleasedLevelScriptOnce()
    {
        Level100ActorDefinitionSet definitions = Level100TestActorDefinitions.Create();
        var deathActors = new Level100ActorRegistry(definitions);
        var death = new Level100Mission(
            deathActors,
            deathActors.GetThingRef("Player 1")!.Value,
            CompletedTutorialSlots);
        Assert.True(death.ReportPlayerDeath());
        Assert.False(death.ReportWaterLoss());
        Assert.Equal(Level100MissionFailureReason.PlayerDeath, death.Snapshot.FailureReason);

        var waterActors = new Level100ActorRegistry(definitions);
        var water = new Level100Mission(
            waterActors,
            waterActors.GetThingRef("Player 1")!.Value,
            CompletedTutorialSlots);
        Assert.True(water.ReportWaterLoss());
        Assert.False(water.SubmitInput(Level100MissionInput.BrokeTutorial));
        Assert.Equal(Level100MissionFailureReason.WaterLoss, water.Snapshot.FailureReason);
    }
}
