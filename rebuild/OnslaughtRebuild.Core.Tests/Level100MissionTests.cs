// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.TestSupport;
using Xunit.Abstractions;

namespace OnslaughtRebuild.Core.Tests;

public sealed class Level100MissionTests
{
    private readonly ITestOutputHelper _output;

    public Level100MissionTests(ITestOutputHelper output) => _output = output;

    private static readonly Level100TutorialProgress CompletedTutorialSlots =
        new(Introduction: true, PulseCannon: true, VulcanCannon: true, StatusBars: true);

    [Fact]
    public void MissionNativeSetPos_CopiesGetPosPositionAndPreservesOtherPoseState()
    {
        Level100ActorDefinitionSet definitions = Level100TestActorDefinitions.Create();
        var actors = new Level100ActorRegistry(definitions);
        Level100ActorId player = actors.GetThingRef("Player 1")!.Value;
        Level100ActorId source = actors.GetThingRef("Turret 01")!.Value;
        Level100ActorId target = actors.GetThingRef("Turret 02")!.Value;
        var runtime = new Level100ActorScriptRuntime(actors, player);

        Level100ActorPoseSnapshot sourcePose = actors.GetPose(source);
        Level100ActorPoseSnapshot targetBefore = actors.GetPose(target);
        Level100ScriptValue position = runtime.InvokePositionNative(
            49,
            source,
            Array.Empty<Level100ScriptValue>());

        _ = runtime.InvokePositionNative(135, target, [position]);

        Level100ActorPoseSnapshot targetAfter = actors.GetPose(target);
        Level100ScriptValue readback = runtime.InvokePositionNative(
            49,
            target,
            Array.Empty<Level100ScriptValue>());
        Assert.Equal(sourcePose.PositionMillimeters, targetAfter.PositionMillimeters);
        Assert.Equal(position.Snapshot, readback.Snapshot);
        Assert.Equal(targetBefore.BasisFloatBits, targetAfter.BasisFloatBits);
        Assert.Equal(
            targetBefore.LinearVelocityMillimetersPerTick,
            targetAfter.LinearVelocityMillimetersPerTick);
        Assert.Equal(
            targetBefore.AngularVelocityMicroRadiansPerTick,
            targetAfter.AngularVelocityMicroRadiansPerTick);

        Assert.Throws<InvalidOperationException>(() =>
            runtime.InvokePositionNative(
                135,
                target,
                [Level100ScriptValue.Integer(1)]));
        Assert.Equal(targetAfter, actors.GetPose(target));
    }

    [Fact]
    public void MissionNativeUnsetObjective_ClearsOnlyTheObjectiveFlagAndIsIdempotent()
    {
        Level100ActorDefinitionSet definitions = Level100TestActorDefinitions.Create();
        var actors = new Level100ActorRegistry(definitions);
        Level100ActorId player = actors.GetThingRef("Player 1")!.Value;
        Level100ActorId target = actors.GetThingRef("Turret 02")!.Value;
        var runtime = new Level100ActorScriptRuntime(actors, player);
        Level100ActorSnapshot initial = actors.GetActor(target);

        runtime.InvokeObjectiveNative(23, target, Array.Empty<Level100ScriptValue>());
        Level100ActorSnapshot marked = actors.GetActor(target);
        Assert.Equal(initial with { IsObjective = true }, marked);

        runtime.InvokeObjectiveNative(30, target, Array.Empty<Level100ScriptValue>());
        Assert.Equal(initial, actors.GetActor(target));
        runtime.InvokeObjectiveNative(30, target, Array.Empty<Level100ScriptValue>());
        Assert.Equal(initial, actors.GetActor(target));

        Assert.Throws<InvalidOperationException>(() =>
            runtime.InvokeObjectiveNative(
                30,
                target,
                [Level100ScriptValue.Integer(1)]));
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            runtime.InvokeObjectiveNative(
                31,
                target,
                Array.Empty<Level100ScriptValue>()));
        Assert.Equal(initial, actors.GetActor(target));
    }

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
    /// The recovered delivery LAW for the released message box, asserted
    /// against the eight retail opening boundaries.
    /// </summary>
    /// <remarks>
    /// <para>
    /// The law has three parts and none of it is fitted to a picture:
    /// </para>
    /// <list type="number">
    /// <item>nothing plays before
    /// <see cref="Level100MissionTiming.MessageBoxAllowedTick"/>, because
    /// <c>CGame::StartPlayingState</c> (<c>game.cpp:3026-3031</c>) only then
    /// posts <c>ALLOWED_TO_PLAY_MESSAGES</c> to the message box;</item>
    /// <item>a message is on screen for its full
    /// <c>Level100MissionTiming.MessagePlaybackTicks</c> entry — retail
    /// activates it before the voice and retains it through the completion
    /// hold, so the 18-tick offset in that table is NOT a post-roll to
    /// subtract;</item>
    /// <item>the next queued message becomes active exactly
    /// <see cref="Level100MissionTiming.MessageAdvanceDelayTicks"/> after the
    /// previous one clears (<c>CMessageBox__TryAdvanceQueuedMessage</c>
    /// <c>0x004b7b80</c>, 0.2 s on the released 0.05 s event clock).</item>
    /// </list>
    /// <para>
    /// The retail column is the measurement recorded in
    /// <c>rebuild/PROVENANCE.md</c>: one clean control and two fresh
    /// uninterrupted app-owned Steam Level 100 runs repeated these eight
    /// boundaries within one 50 ms retail sample, with Core tick zero aligned
    /// to Steam's game-time-3.0 pan start. The gap is asserted EXACTLY because
    /// every one of the seven measured gaps is exactly six 30 Hz ticks, i.e.
    /// 0.2 s.
    /// </para>
    /// <para>
    /// <b>THE RETAIL COLUMN IS RECORDED IN 30 Hz CORE TICKS AND IS NOT
    /// CONVERTED HERE.</b> That is deliberate: it is somebody's measurement,
    /// and rewriting a measurement into the unit of the day is how a
    /// measurement quietly acquires the assumptions of the code it is checking.
    /// Both columns are instead compared in MILLISECONDS, which is the unit the
    /// 50 ms sampler actually worked in and the only one that survives a Core
    /// tick-rate change.
    /// </para>
    /// <para>
    /// <b>This is the migration's headline acceptance signal.</b> Retail floors
    /// every scheduled delay onto a whole 20 Hz boundary
    /// (<c>references/Onslaught/eventmanager.cpp:210-212</c>), so a 30 Hz Core
    /// could not land those boundaries even in principle. A correct 20 Hz Core
    /// should land them BETTER - and the summed-residual assertion below is
    /// there so that a failure to improve is a red test rather than a shrug.
    /// The 30 Hz tree's summed absolute residual over these sixteen boundaries
    /// was 766.7 ms; anything at or above that means the migration did not do
    /// the thing it was for.
    /// </para>
    /// </remarks>
    [Fact]
    public void ReleasedMessageBox_ReproducesTheRetailOpeningDeliverySchedule()
    {
        // (message id, retail measured start, retail measured end), both in
        // the 30 Hz Core ticks the measurement was recorded in.
        (int Id, int Start, int End)[] retail =
        [
            (292562, 182, 351),          // HUD_01, the greeting
            (293386, 357, 567),          // HUD_02, threat circle
            (296682, 573, 756),          // HUD_06, scanner
            (-1575499396, 762, 926),     // TUTORIAL_MESSAGE_LOG
            (-257967449, 932, 998),      // TUTORIAL_TECHNICIAN_01
            (82987417, 1004, 1220),      // TUTORIAL_13_MOD
            (4422830, 1226, 1387),       // TUTORIAL_01
            (175347826, 1393, 1530),     // TUTORIAL_SCANNER
        ];

        // The rate the retail column above is expressed in. It is a property of
        // that recorded measurement, NOT of Core, and must not be replaced with
        // SimulationConstants.TicksPerSecond.
        const double RetailColumnTicksPerSecond = 30d;
        static double RetailMs(int tick) =>
            tick * 1_000d / RetailColumnTicksPerSecond;
        static double CoreMs(int tick) =>
            tick * 1_000d / SimulationConstants.TicksPerSecond;

        // Three 50 ms retail samples. Stated in milliseconds so it cannot
        // silently loosen when the Core rate moves: the old form was "4 Core
        // ticks", which was 133 ms at 30 Hz and would have become 200 ms here.
        const double ToleranceMs = 150d;
        // The 30 Hz tree's own total over the same sixteen boundaries.
        const double ThirtyHertzResidualMs = 766.7d;

        Level100ActorDefinitionSet definitions = Level100TestActorDefinitions.Create();
        var actors = new Level100ActorRegistry(definitions);
        Level100ActorId player = actors.GetThingRef("Player 1")!.Value;
        var mission = new Level100Mission(
            actors,
            player,
            new Level100TutorialProgress(false, false, false, false),
            initialPlayerHealth: 735);

        var delivered = new List<Level100MessageRequested>();
        void Drain()
        {
            delivered.AddRange(mission.DrainEvents().OfType<Level100MessageRequested>());
        }

        Drain();
        // The whole opening runs on script waits alone: no player input, no
        // trigger and no destruction event is involved.
        Assert.Empty(delivered);
        for (int tick = 1; tick <= 1_600 && delivered.Count < retail.Length; tick++)
        {
            mission.AdvanceTick(735);
            Drain();
        }

        Assert.Equal(retail.Length, delivered.Count);

        // 1. The greeting exists, and it is delivered after the opening pan
        //    rather than behind it. CPanCamera::GetShowHUD is false for the
        //    whole pan, so a delivery before tick 180 is invisible.
        Assert.Equal(292562, delivered[0].MessageId);
        Assert.Equal(Level100MissionTiming.MessageBoxAllowedTick, delivered[0].Tick);
        Assert.True(
            delivered[0].Tick >= SimulationConstants.Level100OpeningPanTicks,
            "the greeting must not be delivered behind the opening pan");

        int previousEnd = int.MinValue;
        double totalResidualMs = 0;
        for (int index = 0; index < retail.Length; index++)
        {
            Level100MessageRequested actual = delivered[index];
            (int id, int start, int end) = retail[index];

            Assert.Equal(id, actual.MessageId);

            // 2. Display duration is the full shipped table entry.
            Assert.Equal(
                Level100MissionTiming.MessagePlaybackTicks(id),
                actual.ExpectedPlaybackTicks);

            // 3. The advance gap is exact.
            if (previousEnd != int.MinValue)
            {
                Assert.Equal(
                    Level100MissionTiming.MessageAdvanceDelayTicks,
                    actual.Tick - previousEnd);
            }

            int actualEnd = actual.Tick + actual.ExpectedPlaybackTicks;
            double startResidualMs = CoreMs(actual.Tick) - RetailMs(start);
            double endResidualMs = CoreMs(actualEnd) - RetailMs(end);
            _output.WriteLine(
                $"{id,12}  start core={actual.Tick,5} " +
                $"({CoreMs(actual.Tick),9:F1} ms) retail={start,5} " +
                $"({RetailMs(start),9:F1} ms) residual={startResidualMs,7:F1} ms" +
                $"   end core={actualEnd,5} retail={end,5} " +
                $"residual={endResidualMs,7:F1} ms");
            totalResidualMs +=
                Math.Abs(startResidualMs) + Math.Abs(endResidualMs);

            Assert.InRange(startResidualMs, -ToleranceMs, ToleranceMs);
            Assert.InRange(endResidualMs, -ToleranceMs, ToleranceMs);
            previousEnd = actualEnd;
        }

        // THE NEGATIVE ACCEPTANCE CRITERION. A 20 Hz Core that merely lands
        // these boundaries DIFFERENTLY has not done the thing the migration was
        // for; it has to land them BETTER, because retail's own scheduler
        // floors to 20 Hz boundaries. Failing to improve is the signal that
        // something in the conversion is wrong, and it would otherwise read as
        // a pass.
        _output.WriteLine(
            $"total absolute residual = {totalResidualMs:F1} ms " +
            $"(30 Hz tree: {ThirtyHertzResidualMs:F1} ms)");
        Assert.True(
            totalResidualMs < ThirtyHertzResidualMs,
            $"the summed residual against the eight measured retail " +
            $"boundaries is {totalResidualMs:F1} ms, which is no better than " +
            $"the {ThirtyHertzResidualMs:F1} ms the 30 Hz Core achieved. " +
            "Retail floors every event onto a 20 Hz boundary, so a correct " +
            "20 Hz Core lands these closer, not merely elsewhere.");
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
        const int SettleTicks = 100 * SimulationConstants.TicksPerSecond;
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
