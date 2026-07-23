// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.TestSupport;

namespace OnslaughtRebuild.Client.Tests;

public sealed class InteractiveSessionTests
{
    private const int FirstRunControlTick = 790;
    private static Level100ActorDefinitionSet ActorDefinitions =>
        Level100TestActorDefinitions.Create();
    private const long OneCoreStepTicks = 333_334;
    private const uint Seed = 0x4F4E534Cu;

    [Fact]
    public void RationalAccumulator_DoesNotTruncateThirtyHertzStep()
    {
        var session = new InteractiveSession(Seed, ActorDefinitions);

        FrameAdvanceResult beforeBoundary = session.AdvanceFrameTicks(333_333);
        FrameAdvanceResult afterBoundary = session.AdvanceFrameTicks(1);

        Assert.Equal(0, beforeBoundary.StepsAdvanced);
        Assert.Equal(1, afterBoundary.StepsAdvanced);
        Assert.Equal(1, afterBoundary.CurrentSnapshot.Tick);
        Assert.Equal(20, afterBoundary.InterpolationPhase);
        Assert.Equal(InteractiveSession.PhaseUnitsPerStep, afterBoundary.InterpolationPhaseScale);
    }

    [Fact]
    public void FourQuarterSecondFrames_AdvanceExactlyThirtyTicks()
    {
        var session = new InteractiveSession(Seed, ActorDefinitions);

        FrameAdvanceResult result = default;
        for (int frame = 0; frame < 4; frame++)
        {
            result = session.AdvanceFrame(TimeSpan.FromMilliseconds(250));
            Assert.False(result.FrameTimeCapped);
        }

        Assert.Equal(30, result.CurrentSnapshot.Tick);
        Assert.Equal(30, session.Metrics.TotalSteps);
        Assert.Equal(0, session.Metrics.DroppedElapsedTicks);
    }

    [Fact]
    public void LongFrame_IsCappedAndReportedWithoutSkippingSimulationTicks()
    {
        var session = new InteractiveSession(Seed, ActorDefinitions);

        FrameAdvanceResult result = session.AdvanceFrame(TimeSpan.FromSeconds(1));

        Assert.True(result.FrameTimeCapped);
        Assert.Equal(7, result.StepsAdvanced);
        Assert.Equal(7, result.CurrentSnapshot.Tick);
        Assert.Equal(1, session.Metrics.CappedFrameCount);
        Assert.Equal(TimeSpan.FromMilliseconds(750).Ticks, session.Metrics.DroppedElapsedTicks);
    }

    [Fact]
    public void HeldToggleLevel_IsConsumedOnOneTickOnly()
    {
        InteractiveSession session = CreatePlayingSession();
        session.ObserveInput(new InteractiveInput(0, 0, false, true, false));

        FrameAdvanceResult result = session.AdvanceFrame(TimeSpan.FromMilliseconds(100));
        session.ObserveInput(new InteractiveInput(0, 0, false, true, false));
        session.AdvanceFrame(TimeSpan.FromMilliseconds(100));

        Assert.Equal(VehicleMode.Walker, result.CurrentSnapshot.Mode);
        Assert.Equal(VehicleTransition.None, result.CurrentSnapshot.Transition);
        Assert.Equal(1, session.Metrics.ToggleEdgesConsumed);

        for (int frame = 0; frame < 4; frame++)
        {
            session.AdvanceFrame(TimeSpan.FromMilliseconds(100));
        }

        Assert.Equal(VehicleMode.Walker, session.CurrentSnapshot.Mode);
        Assert.Equal(VehicleTransition.None, session.CurrentSnapshot.Transition);
        Assert.Equal(1, session.Metrics.ToggleEdgesConsumed);
    }

    [Fact]
    public void PressAndReleaseBetweenTicks_LeavesOneLatchedEdge()
    {
        InteractiveSession session = CreatePlayingSession();
        session.ObserveInput(new InteractiveInput(0, 0, false, true, false));
        session.ObserveInput(InteractiveInput.Idle);

        FrameAdvanceResult result = session.AdvanceFrameTicks(333_334);

        Assert.Equal(VehicleMode.Walker, result.CurrentSnapshot.Mode);
        Assert.Equal(VehicleTransition.None, result.CurrentSnapshot.Transition);
        Assert.Equal(1, session.Metrics.ToggleEdgesConsumed);
    }

    [Fact]
    public void DuplicateEventAndLevelEdge_AreCoalescedBeforeTheTick()
    {
        InteractiveSession session = CreatePlayingSession();
        session.QueueToggleMode();
        session.ObserveInput(new InteractiveInput(0, 0, false, true, false));

        session.AdvanceFrame(TimeSpan.FromMilliseconds(100));

        Assert.Equal(1, session.Metrics.ToggleEdgesConsumed);
    }

    [Fact]
    public void HeldFire_IsSampledOnEveryAdvancedTick()
    {
        InteractiveSession session = CreatePlayingSession();
        session.ObserveInput(new InteractiveInput(0, 0, true, false, false));

        FrameAdvanceResult result = session.AdvanceFrame(TimeSpan.FromMilliseconds(200));

        Assert.Equal(6, result.StepsAdvanced);
        Assert.Equal(6, session.Metrics.FireHeldTicksSampled);
        Assert.Equal(SimulationConstants.MaximumEnergy, result.CurrentSnapshot.Energy);
        Assert.Empty(result.CurrentSnapshot.Projectiles);
    }

    [Fact]
    public void ShortFirePulse_SurvivesUntilOneTickConsumesIt()
    {
        InteractiveSession session = CreatePlayingSession();

        session.QueueFirePulse();
        session.AdvanceFrameTicks(100_000);
        FrameAdvanceResult firingTick = session.AdvanceFrameTicks(233_334);
        FrameAdvanceResult followingTick = session.AdvanceFrameTicks(333_334);

        Assert.Empty(firingTick.CurrentSnapshot.Projectiles);
        Assert.Empty(followingTick.CurrentSnapshot.Projectiles);
        Assert.Equal(1, session.Metrics.FirePulseEdgesConsumed);
        Assert.Equal(0, session.Metrics.FireHeldTicksSampled);
    }

    [Fact]
    public void ShortMovementPulse_StartsAccelerationAndThenCoasts()
    {
        InteractiveSession session = CreatePlayingSession();

        session.QueueMovementPulse(0, 1);
        FrameAdvanceResult movementTick = session.AdvanceFrameTicks(333_334);
        FrameAdvanceResult idleTick = session.AdvanceFrameTicks(333_334);

        Assert.Equal(new SimVector2(-16, 29), movementTick.CurrentSnapshot.PlayerPosition);
        Assert.Equal(new SimVector2(-28, 51), idleTick.CurrentSnapshot.PlayerPosition);
        Assert.Equal(1, session.Metrics.MovementPulseEdgesConsumed);
    }

    [Fact]
    public void PulseAndHeldState_AreCoalescedIntoOneSimulationInput()
    {
        InteractiveSession session = CreatePlayingSession();
        session.QueueMovementPulse(0, 1);
        session.QueueFirePulse();
        session.ObserveInput(new InteractiveInput(0, 1, true, false, false));

        FrameAdvanceResult result = session.AdvanceFrameTicks(333_334);

        Assert.Equal(new SimVector2(-16, 29), result.CurrentSnapshot.PlayerPosition);
        Assert.Empty(result.CurrentSnapshot.Projectiles);
        Assert.Equal(1, session.Metrics.MovementPulseEdgesConsumed);
        Assert.Equal(1, session.Metrics.FirePulseEdgesConsumed);
        Assert.Equal(1, session.Metrics.FireHeldTicksSampled);
    }

    [Fact]
    public void ResetDominatesItsTick_AndRestartsTheOpeningInputGate()
    {
        InteractiveSession session = CreatePlayingSession();
        session.ObserveInput(new InteractiveInput(0, 0, true, false, true));

        FrameAdvanceResult resetTick = session.AdvanceFrameTicks(333_334);
        FrameAdvanceResult followingTick = session.AdvanceFrameTicks(333_334);

        Assert.Empty(resetTick.CurrentSnapshot.Projectiles);
        Assert.Empty(followingTick.CurrentSnapshot.Projectiles);
        Assert.False(followingTick.CurrentSnapshot.Level100PlayerControlEnabled);
        Assert.Equal(
            SimulationConstants.Level100OpeningPanTicks - 1,
            followingTick.CurrentSnapshot.Level100OpeningTicksRemaining);
        Assert.Equal(1, session.Metrics.ResetEdgesConsumed);
        Assert.Equal(1, session.Metrics.ResetGeneration);
        Assert.Equal(2, session.Metrics.FireHeldTicksSampled);
    }

    [Fact]
    public void SameIntegerFrameAndInputSequence_ProducesSameStateAndMetrics()
    {
        InteractiveSession first = RunInteractiveSequence();
        InteractiveSession second = RunInteractiveSequence();

        Assert.Equal(StateHasher.ComputeHex(first.CurrentSnapshot), StateHasher.ComputeHex(second.CurrentSnapshot));
        Assert.Equal(first.Metrics, second.Metrics);
        Assert.Equal(first.InterpolationPhase, second.InterpolationPhase);
    }

    [Fact]
    public void FramePartitioning_DoesNotChangeStateForTheSameHeldInput()
    {
        InteractiveSession coarse = CreatePlayingSession();
        InteractiveSession fine = CreatePlayingSession();
        var input = new InteractiveInput(1, 1, true, false, false);
        coarse.ObserveInput(input);
        fine.ObserveInput(input);

        for (int frame = 0; frame < 10; frame++)
        {
            coarse.AdvanceFrame(TimeSpan.FromMilliseconds(100));
        }

        for (int frame = 0; frame < 40; frame++)
        {
            fine.AdvanceFrame(TimeSpan.FromMilliseconds(25));
        }

        Assert.Equal(FirstRunControlTick + 30, coarse.CurrentSnapshot.Tick);
        Assert.Equal(FirstRunControlTick + 30, fine.CurrentSnapshot.Tick);
        Assert.Equal(StateHasher.ComputeHex(coarse.CurrentSnapshot), StateHasher.ComputeHex(fine.CurrentSnapshot));
    }

    [Fact]
    public void LookX_HeldRotatesFacingUsingWalkerYawInertia()
    {
        InteractiveSession session = CreatePlayingSession(1);
        // One Core step needs elapsedTicks such that elapsed * TPS >= PhaseUnitsPerStep.
        const long oneCoreStepTicks =
            (TimeSpan.TicksPerSecond / SimulationConstants.TicksPerSecond) + 1;
        session.ObserveInput(new InteractiveInput(0, 0, false, false, false, LookX: 1));
        Assert.True(session.HasHeldOrPendingInput);
        for (int i = 0; i < 20; i++)
        {
            session.AdvanceFrameTicks(oneCoreStepTicks);
        }

        Assert.Equal(1, session.CurrentSnapshot.FacingX);
        Assert.Equal(0, session.CurrentSnapshot.FacingZ);
    }

    [Fact]
    public void LookY_HeldPitchesTheBattleEngineThroughTheClientAdapter()
    {
        InteractiveSession session = CreatePlayingSession(1);
        const long oneCoreStepTicks =
            (TimeSpan.TicksPerSecond / SimulationConstants.TicksPerSecond) + 1;
        session.ObserveInput(new InteractiveInput(0, 0, false, false, false, LookY: -1));

        session.AdvanceFrameTicks(oneCoreStepTicks);

        Assert.Equal(-3_938, session.CurrentSnapshot.FacingPitchMicroRad);
        Assert.Equal(-3_938, session.CurrentSnapshot.WalkerPitchVelocityMicroRadPerTick);
    }

    [Fact]
    public void ShortLookPulse_SurvivesUntilOneTickConsumesIt()
    {
        InteractiveSession session = CreatePlayingSession(1);
        int startingYaw = session.CurrentSnapshot.FacingYawMicroRad;

        session.QueueLookPulse(1, -1);
        FrameAdvanceResult beforeTick = session.AdvanceFrameTicks(100_000);

        Assert.Equal(0, beforeTick.StepsAdvanced);
        Assert.True(session.HasHeldOrPendingInput);

        FrameAdvanceResult lookTick = session.AdvanceFrameTicks(233_334);

        Assert.Equal(1, lookTick.StepsAdvanced);
        Assert.False(session.HasHeldOrPendingInput);
        Assert.Equal(startingYaw + 10_444, lookTick.CurrentSnapshot.FacingYawMicroRad);
        Assert.Equal(10_444, lookTick.CurrentSnapshot.WalkerYawVelocityMicroRadPerTick);
        Assert.Equal(-3_938, lookTick.CurrentSnapshot.FacingPitchMicroRad);
        Assert.Equal(-3_938, lookTick.CurrentSnapshot.WalkerPitchVelocityMicroRadPerTick);
    }

    [Fact]
    public void PointerMotion_PreservesMagnitudeAndRetailRecenteringCoast()
    {
        InteractiveSession session = CreatePlayingSession(1);
        int startingYaw = session.CurrentSnapshot.FacingYawMicroRad;
        const long oneCoreStepTicks =
            (TimeSpan.TicksPerSecond / SimulationConstants.TicksPerSecond) + 1;

        session.QueuePointerMotionMilliPixels(80_000, -40_000);
        FrameAdvanceResult first = session.AdvanceFrameTicks(oneCoreStepTicks);

        Assert.Equal(3_812, first.CurrentSnapshot.WalkerYawVelocityMicroRadPerTick);
        Assert.Equal(-721, first.CurrentSnapshot.WalkerPitchVelocityMicroRadPerTick);
        Assert.Equal(startingYaw + 3_812, first.CurrentSnapshot.FacingYawMicroRad);
        Assert.True(session.HasHeldOrPendingInput);

        FrameAdvanceResult second = session.AdvanceFrameTicks(oneCoreStepTicks);

        Assert.Equal(5_959, second.CurrentSnapshot.WalkerYawVelocityMicroRadPerTick);
        Assert.Equal(-1_125, second.CurrentSnapshot.WalkerPitchVelocityMicroRadPerTick);
        Assert.Equal(
            first.CurrentSnapshot.FacingYawMicroRad + 5_959,
            second.CurrentSnapshot.FacingYawMicroRad);
    }

    [Fact]
    public void InteractiveInputSequence_MatchesDirectCoreTicks()
    {
        InteractiveSession session = CreatePlayingSession();
        var direct = new Simulation(Seed, ActorDefinitions);
        for (int tick = 0; tick < FirstRunControlTick; tick++)
        {
            direct.Step(SimInput.Idle);
        }
        var held = new InteractiveInput(0, 1, true, false, false);
        session.ObserveInput(held);
        session.AdvanceFrameTicks(1_000_000);
        for (int tick = 0; tick < 3; tick++)
        {
            direct.Step(new SimInput(0, 1, SimActions.Fire));
        }

        session.ObserveInput(new InteractiveInput(0, 1, false, true, false));
        session.AdvanceFrameTicks(333_334);
        direct.Step(new SimInput(0, 1, SimActions.ToggleMode));

        session.ObserveInput(new InteractiveInput(0, 0, true, false, true));
        session.AdvanceFrameTicks(333_334);
        direct.Step(new SimInput(0, 0, SimActions.Fire | SimActions.Reset));

        Assert.Equal(StateHasher.ComputeHex(direct.Snapshot), StateHasher.ComputeHex(session.CurrentSnapshot));
    }

    [Fact]
    public void FocusLoss_ReleasesHeldInputAndDiscardsUnconsumedEdges()
    {
        InteractiveSession session = CreatePlayingSession();
        session.ObserveInput(new InteractiveInput(1, 1, true, true, true));
        session.QueueMovementPulse(-1, -1);
        session.QueueLookPulse(-1, -1);
        session.QueuePointerMotionMilliPixels(-10_000, 10_000);
        session.QueueFirePulse();

        session.ReleaseAllInput();
        session.AdvanceFrameTicks(333_334);

        Assert.Equal(SimVector2.Zero, session.CurrentSnapshot.PlayerPosition);
        Assert.Empty(session.CurrentSnapshot.Projectiles);
        Assert.Equal(VehicleMode.Walker, session.CurrentSnapshot.Mode);
        Assert.Equal(0, session.Metrics.ToggleEdgesConsumed);
        Assert.Equal(0, session.Metrics.ResetEdgesConsumed);
        Assert.Equal(0, session.Metrics.FireHeldTicksSampled);
    }

    [Fact]
    public void FocusLoss_SuppressesHeldAndPulseInputUntilANeutralSample()
    {
        InteractiveSession session = CreatePlayingSession();
        session.ObserveInput(new InteractiveInput(1, 1, true, true, true));
        session.QueueMovementPulse(-1, -1);
        session.QueueLookPulse(-1, -1);
        session.QueuePointerMotionMilliPixels(-10_000, 10_000);
        session.QueueFirePulse();

        session.SuspendInputUntilReleased();
        session.ObserveInput(new InteractiveInput(0, 1, true, false, false));
        session.QueueMovementPulse(1, 0);
        session.QueueLookPulse(1, 0);
        session.QueuePointerMotionMilliPixels(10_000, -10_000);
        session.QueueFirePulse();
        session.QueueToggleMode();
        session.QueueReset();
        session.AdvanceFrameTicks(333_334);

        Assert.True(session.InputSuspendedUntilReleased);
        Assert.False(session.HasHeldOrPendingInput);
        Assert.Equal(SimVector2.Zero, session.CurrentSnapshot.PlayerPosition);
        Assert.Empty(session.CurrentSnapshot.Projectiles);
        Assert.Equal(VehicleMode.Walker, session.CurrentSnapshot.Mode);
        Assert.Equal(0, session.Metrics.ToggleEdgesConsumed);
        Assert.Equal(0, session.Metrics.ResetEdgesConsumed);

        session.ObserveInput(InteractiveInput.Idle);
        Assert.False(session.InputSuspendedUntilReleased);

        session.QueueMovementPulse(0, 1);
        session.QueueFirePulse();
        session.AdvanceFrameTicks(333_334);

        Assert.Equal(new SimVector2(-16, 29), session.CurrentSnapshot.PlayerPosition);
        Assert.Empty(session.CurrentSnapshot.Projectiles);
    }

    [Fact]
    public void AuthenticPauseFreezesOneSessionAndRequiresNeutralInputAfterResume()
    {
        InteractiveSession session = CreatePlayingSession();
        int startingTick = session.CurrentSnapshot.Tick;
        string startingHash = StateHasher.ComputeHex(session.CurrentSnapshot);
        InteractiveSessionMetrics startingMetrics = session.Metrics;
        long startingPhase = session.InterpolationPhase;
        session.ObserveInput(new InteractiveInput(1, 1, true, true, true));
        session.QueueMovementPulse(-1, -1);
        session.QueueLookPulse(1, -1);
        session.QueuePointerMotionMilliPixels(10_000, -10_000);
        session.QueueFirePulse();

        session.SetAuthenticMenuPaused(true);

        Assert.Equal(InteractivePauseReason.AuthenticMenu, session.PauseReasons);
        Assert.True(session.IsPaused);
        Assert.True(session.IsAuthenticMenuPaused);
        Assert.True(session.InputSuspendedUntilReleased);
        Assert.False(session.HasHeldOrPendingInput);

        session.ObserveInput(InteractiveInput.Idle);
        session.QueueMovementPulse(0, 1);
        FrameAdvanceResult pausedFrame = session.AdvanceFrame(TimeSpan.FromSeconds(1));

        Assert.Equal(0, pausedFrame.StepsAdvanced);
        Assert.False(pausedFrame.FrameTimeCapped);
        Assert.Empty(pausedFrame.Level100MissionEvents);
        Assert.Equal(startingTick, session.CurrentSnapshot.Tick);
        Assert.Equal(startingPhase, session.InterpolationPhase);
        Assert.Equal(startingHash, StateHasher.ComputeHex(session.CurrentSnapshot));
        Assert.Equal(startingMetrics, session.Metrics);

        session.SetAuthenticMenuPaused(false);

        Assert.False(session.IsPaused);
        Assert.True(session.InputSuspendedUntilReleased);
        session.ObserveInput(new InteractiveInput(0, 1, true, false, false));
        Assert.True(session.InputSuspendedUntilReleased);
        Assert.False(session.HasHeldOrPendingInput);
        session.ObserveInput(InteractiveInput.Idle);
        Assert.False(session.InputSuspendedUntilReleased);
    }

    [Fact]
    public void PauseResumePreservesTheSameCoreInputTapeTraceAndFinalHash()
    {
        InteractiveSession uninterrupted = CreatePlayingSession();
        InteractiveSession paused = CreatePlayingSession();
        InteractiveInput[] tape =
        [
            new InteractiveInput(0, 1, false, false, false),
            InteractiveInput.Idle,
            new InteractiveInput(0, 0, true, false, false),
            InteractiveInput.Idle,
            new InteractiveInput(0, 0, false, true, false),
            InteractiveInput.Idle,
            new InteractiveInput(1, 0, false, false, false),
        ];
        var uninterruptedTrace = new List<string>();
        var pausedTrace = new List<string>();

        for (int index = 0; index < tape.Length; index++)
        {
            if (index == 2)
            {
                paused.SetAuthenticMenuPaused(true);
                Assert.Equal(0, paused.AdvanceFrame(TimeSpan.FromSeconds(1)).StepsAdvanced);
                paused.ObserveInput(new InteractiveInput(1, 1, true, true, true));
                paused.QueuePointerMotionMilliPixels(100_000, -100_000);
                paused.SetAuthenticMenuPaused(false);
                paused.ObserveInput(InteractiveInput.Idle);
            }

            uninterrupted.ObserveInput(tape[index]);
            paused.ObserveInput(tape[index]);
            FrameAdvanceResult directFrame = uninterrupted.AdvanceFrameTicks(OneCoreStepTicks);
            FrameAdvanceResult resumedFrame = paused.AdvanceFrameTicks(OneCoreStepTicks);
            Assert.Equal(1, directFrame.StepsAdvanced);
            Assert.Equal(1, resumedFrame.StepsAdvanced);
            uninterruptedTrace.Add(StateHasher.ComputeHex(directFrame.CurrentSnapshot));
            pausedTrace.Add(StateHasher.ComputeHex(resumedFrame.CurrentSnapshot));
        }

        Assert.Equal(uninterruptedTrace, pausedTrace);
        Assert.Equal(
            StateHasher.ComputeHex(uninterrupted.CurrentSnapshot),
            StateHasher.ComputeHex(paused.CurrentSnapshot));
        Assert.Equal(uninterrupted.Metrics, paused.Metrics);
    }

    [Fact]
    public void SnapshotsExposePreviousAndCurrentSimulationStates()
    {
        InteractiveSession session = CreatePlayingSession();
        session.ObserveInput(new InteractiveInput(1, 0, false, false, false));

        int startingTick = session.CurrentSnapshot.Tick;

        FrameAdvanceResult result = session.AdvanceFrameTicks(333_334);

        Assert.Equal(startingTick, result.PreviousSnapshot.Tick);
        Assert.Equal(startingTick + 1, result.CurrentSnapshot.Tick);
        Assert.Equal(0, result.PreviousSnapshot.PlayerPosition.X);
        Assert.True(result.CurrentSnapshot.PlayerPosition.X > 0);
    }

    [Fact]
    public void InvalidInputAndElapsedTime_AreRejected()
    {
        var session = new InteractiveSession(Seed, ActorDefinitions);

        Assert.Throws<ArgumentOutOfRangeException>(() =>
            session.ObserveInput(new InteractiveInput(2, 0, false, false, false)));
        Assert.Throws<ArgumentOutOfRangeException>(() => session.AdvanceFrameTicks(-1));
        WorldSnapshot before = session.CurrentSnapshot;
        Assert.Throws<ArgumentException>(() => session.AdvanceFrameTicks(
            1,
            [new Level100PlayerDeathFact()]));
        Assert.Same(before, session.CurrentSnapshot);
    }

    [Fact]
    public void InitialMissionEvents_AreDeliveredOnceByFrameEnvelope()
    {
        var session = new InteractiveSession(Seed, ActorDefinitions);

        FrameAdvanceResult initial = session.AdvanceFrameTicks(0);
        FrameAdvanceResult next = session.AdvanceFrameTicks(0);

        Assert.Equal(0, initial.StepsAdvanced);
        Level100MessageRequested message = Assert.Single(
            initial.Level100MissionEvents.OfType<Level100MessageRequested>());
        Assert.Equal(292562, message.MessageId);
        Assert.Empty(next.Level100MissionEvents);
    }

    [Fact]
    public void FrameMissionEvents_AggregateEverySimulationStepInOrder()
    {
        var session = new InteractiveSession(Seed, ActorDefinitions);
        for (int tick = 0; tick < 168; tick++)
        {
            session.AdvanceFrameTicks(OneCoreStepTicks);
        }

        FrameAdvanceResult frame = session.AdvanceFrameTicks(666_667);

        Assert.Equal(2, frame.StepsAdvanced);
        Level100MessageRequested message = Assert.Single(
            frame.Level100MissionEvents.OfType<Level100MessageRequested>());
        Assert.Equal(293386, message.MessageId);
        Assert.Empty(frame.CurrentSnapshot.Level100MissionEvents);
    }

    [Fact]
    public void ClientLevel100FailureTape_FirstRunRepeatsLossTextAndHashes()
    {
        ClientMissionTape first = RunClientFailureTape();
        ClientMissionTape repeat = RunClientFailureTape();

        Assert.Equal(first.Hashes, repeat.Hashes);
        Assert.Equal(Level100MissionOutcome.Lost, first.Snapshot.Level100Mission.Outcome);
        Assert.Equal(1_110_345_999, first.Snapshot.Level100Mission.FailureTextId);
        Assert.Equal(
            Level100MissionTerminalState.FailureCountdownElapsed,
            first.Snapshot.Level100Mission.TerminalState);
    }

    [Fact]
    public void ClientAssembly_HasNoGodotOrForbiddenRuntimeDependencies()
    {
        string[] references = typeof(InteractiveSession).Assembly
            .GetReferencedAssemblies()
            .Select(reference => reference.Name ?? string.Empty)
            .ToArray();

        Assert.DoesNotContain(references, name => name.StartsWith("Godot", StringComparison.Ordinal));
        Assert.DoesNotContain(references, name => name == "System.Diagnostics.Process");
        Assert.DoesNotContain(references, name => name == "System.IO.FileSystem");
        Assert.DoesNotContain(references, name => name == "System.Net.Http");
    }

    [Fact]
    public void MaterializedLevel100ActorDefinitions_OwnCompleteWorldAndAuthoredSpawns()
    {
        Level100ActorDefinitionSet definitions = LoadMaterializedActorDefinitions();

        Assert.Equal(44, definitions.Actors.Count);
        Assert.Equal(33, definitions.Actors.Count(actor =>
            actor.DefinitionIdentity.StartsWith("wres:bswd:", StringComparison.Ordinal)));
        Assert.Equal(3, definitions.Actors.Count(actor =>
            actor.DefinitionIdentity.StartsWith("wres:rlwd:", StringComparison.Ordinal) &&
            actor.TargetGroup == Level100MissionTargetGroup.StaticTargets));
        Assert.Equal(5, definitions.Actors.Count(actor => actor.Trigger.HasValue));
        Assert.Single(definitions.Actors, actor => actor.ThingTypeMask ==
            Level100ReleasedThingTypeMasks.BattleEngine);
        Assert.Contains(definitions.Actors, actor => actor.Name == "Transporter");
        Assert.Contains(definitions.Actors, actor => actor.Name == "Air Trainer");
        Assert.Equal(10, definitions.Spawns.Count);
        Assert.Equal(
            [
                "Flyby Path",
                "Target Truck Path 3",
                "Target Truck Path 2",
                "Target Truck Path 1",
                "Transporter Path",
                "Target Tank Path 2",
                "Target Tank Path 1",
                "Drone Path 1",
            ],
            definitions.WaypointPaths.Select(path => path.Name));
        Level100WaypointPathDefinition truckPath =
            definitions.GetWaypointPath("Target Truck Path 1");
        Assert.Equal([25, 26, 27, 28], truckPath.Points.Select(point => point.NodeIndex));
        Assert.Equal(
            new SimVector2(-66_688, 16_750),
            truckPath.Points[0].HorizontalPositionMillimeters);
        Assert.Equal(
            BitConverter.SingleToInt32Bits(10.0f),
            truckPath.Points[0].RetailComponentsFloatBits.Z);
        Assert.Equal(64, definitions.IdentitySha256.Length);
        Assert.Null(definitions.Actors.Single(actor => actor.Name == "Airfield").ScriptName);
        Assert.Null(definitions.Actors.Single(actor => actor.Name == "Hangar").ScriptName);

        Level100SpawnDefinition trainer = definitions.Spawns.Single(spawn =>
            spawn.ScriptName == "AirTrainer");
        Assert.Equal("wres:bswd:0023", trainer.OwnerDefinitionIdentity);
        Assert.Equal(
            BitConverter.SingleToInt32Bits(-0.099276736f),
            trainer.AuthoredEmitterTransform.LocalPositionFloatBits.X);

        var registry = new Level100ActorRegistry(definitions);
        Level100ActorId trainerId = Assert.Single(registry.SpawnThing(
            registry.GetThingRef("Airfield")!.Value,
            "Air Trainer",
            "SpawnerB",
            1,
            "AirTrainer"));
        Assert.Equal(trainer.InitialPose, registry.GetActor(trainerId).Pose);
        Assert.DoesNotContain(registry.Snapshot.Actors, actor => actor.Pose is null);
    }

    [Fact]
    public void MaterializedLevel100ActorDefinitions_RepeatFailureHashes()
    {
        Level100ActorDefinitionSet definitions = LoadMaterializedActorDefinitions();

        ClientMissionTape failure = RunClientFailureTape(definitions);
        ClientMissionTape repeatedFailure = RunClientFailureTape(definitions);

        Assert.Equal(failure.Hashes, repeatedFailure.Hashes);
        Assert.Equal(Level100MissionOutcome.Lost, failure.Snapshot.Level100Mission.Outcome);
    }

    [Fact]
    public void FirstFlightSmokeScenario_ReachesFiringRangeAndPreservesWaypointBoundary()
    {
        InteractiveInput pan = FirstFlightSmokeScenario.GetInputForTick(0);
        InteractiveInput strafe = FirstFlightSmokeScenario.GetInputForTick(
            FirstFlightSmokeScenario.TargetZoneInputStartTick);
        InteractiveInput forward = FirstFlightSmokeScenario.GetInputForTick(
            FirstFlightSmokeScenario.TargetZoneInputStartTick + 216);
        InteractiveInput closeout = FirstFlightSmokeScenario.GetInputForTick(
            FirstFlightSmokeScenario.DurationTicks - 1);
        InteractiveInput firingRangeTurn = FirstFlightSmokeScenario.GetInputForTick(1_995);
        InteractiveInput firingRangeApproach = FirstFlightSmokeScenario.GetInputForTick(2_040);
        InteractiveInput firingRangeAim = FirstFlightSmokeScenario.GetInputForTick(3_139);
        InteractiveInput pulseCannonProof = FirstFlightSmokeScenario.GetInputForTick(3_156);

        Assert.Equal(InteractiveInput.Idle, pan);
        Assert.Equal((sbyte)-1, strafe.MoveX);
        Assert.False(strafe.FireHeld);
        Assert.Equal((sbyte)1, forward.MoveZ);
        Assert.False(forward.ToggleModeHeld);
        Assert.Equal((sbyte)-1, firingRangeTurn.MoveX);
        Assert.Equal((sbyte)1, firingRangeApproach.MoveZ);
        Assert.Equal((sbyte)-1, firingRangeAim.LookX);
        Assert.True(pulseCannonProof.FireHeld);
        Assert.Equal(InteractiveInput.Idle, closeout);
        Assert.Equal(3_228, FirstFlightSmokeScenario.DurationTicks);
        Assert.Throws<ArgumentOutOfRangeException>(() => FirstFlightSmokeScenario.GetInputForTick(-1));

        var session = new InteractiveSession(Seed, ActorDefinitions);
        while (session.CurrentSnapshot.Tick < FirstFlightSmokeScenario.DurationTicks)
        {
            session.ObserveInput(
                FirstFlightSmokeScenario.GetInputForTick(session.CurrentSnapshot.Tick));
            FrameAdvanceResult result = session.AdvanceFrameTicks(333_334);
            Assert.Equal(1, result.StepsAdvanced);
        }

        TargetSnapshot firstTarget = session.CurrentSnapshot.Targets.Single(target => target.Id == 1);
        Assert.True(firstTarget.IsActive);
        Assert.Equal(SimulationConstants.Level100TargetTankLife, firstTarget.Hull);
        Assert.Equal(0, session.CurrentSnapshot.TargetsDestroyed);
        Level100ActorScriptInstanceSnapshot targetScript =
            session.CurrentSnapshot.Level100ActorScripts.Instances.Single(item =>
                item.ActorId == firstTarget.ActorId);
        Level100ActorScriptContinuationSnapshot waypoint = Assert.Single(
            targetScript.Continuations);
        Assert.Equal(Level100ActorScriptWaitKind.FollowWaypoint, waypoint.WaitKind);
        Assert.Equal("Target Tank Path 1", waypoint.WaitArgument);
        Assert.Null(waypoint.DueTick);
        Assert.Equal(4, session.Metrics.FireHeldTicksSampled);
    }

    private static InteractiveSession RunInteractiveSequence()
    {
        InteractiveSession session = CreatePlayingSession();
        (long ElapsedTicks, InteractiveInput Input)[] frames =
        [
            (100_000, new InteractiveInput(0, 1, false, false, false)),
            (250_000, new InteractiveInput(0, 1, true, false, false)),
            (333_334, new InteractiveInput(0, 1, true, true, false)),
            (1_100_000, new InteractiveInput(1, 0, true, false, false)),
            (333_334, new InteractiveInput(0, 0, false, false, true)),
            (700_000, InteractiveInput.Idle),
        ];

        foreach ((long elapsedTicks, InteractiveInput input) in frames)
        {
            session.ObserveInput(input);
            session.AdvanceFrameTicks(elapsedTicks);
        }

        return session;
    }

    private static ClientMissionTape RunClientFailureTape(
        Level100ActorDefinitionSet? actorDefinitions = null)
    {
        var tape = new ClientMissionTape(actorDefinitions);
        tape.Step([new Level100MissionInputFact(Level100MissionInput.BrokeTutorial)]);
        tape.AdvanceUntil(
            state => state.Level100Mission.Outcome == Level100MissionOutcome.Lost,
            500);
        tape.Advance(Level100MissionTiming.FailureCountdownTicks);
        return tape;
    }

    private sealed class ClientMissionTape
    {
        private readonly InteractiveSession _session;

        internal ClientMissionTape(Level100ActorDefinitionSet? actorDefinitions = null)
        {
            _session = new InteractiveSession(
                0x100u,
                actorDefinitions ?? Level100TestActorDefinitions.Create());
            Capture(_session.AdvanceFrameTicks(0).Level100MissionEvents);
        }

        internal WorldSnapshot Snapshot => _session.CurrentSnapshot;

        internal List<Level100MissionEvent> Events { get; } = [];

        internal List<string> Hashes { get; } = [];

        internal void Step(IReadOnlyList<Level100SimulationFact>? facts = null) =>
            Step(InteractiveInput.Idle, facts);

        internal void Step(
            InteractiveInput input,
            IReadOnlyList<Level100SimulationFact>? facts = null)
        {
            _session.ObserveInput(input);
            FrameAdvanceResult result = _session.AdvanceFrameTicks(OneCoreStepTicks, facts);
            Assert.Equal(1, result.StepsAdvanced);
            Assert.Empty(result.CurrentSnapshot.Level100Mission.PendingEvents);
            Capture(result.Level100MissionEvents);
        }

        internal void Advance(int ticks)
        {
            for (int tick = 0; tick < ticks; tick++)
            {
                Step();
            }
        }

        internal void AdvanceUntil(Func<WorldSnapshot, bool> predicate, int maximumTicks)
        {
            for (int tick = 0; tick < maximumTicks && !predicate(Snapshot); tick++)
            {
                Step();
            }

            Assert.True(predicate(Snapshot),
                $"Condition was not reached by client tick {Snapshot.Tick}.");
        }

        private void Capture(IReadOnlyList<Level100MissionEvent> events)
        {
            Events.AddRange(events);
            Hashes.Add(StateHasher.ComputeHex(Snapshot));
        }
    }

    private static InteractiveSession CreatePlayingSession(uint seed = Seed)
    {
        var session = new InteractiveSession(seed, ActorDefinitions);
        for (int tick = 0; tick < FirstRunControlTick; tick++)
        {
            session.AdvanceFrameTicks(OneCoreStepTicks);
        }

        Assert.True(session.CurrentSnapshot.Level100PlayerControlEnabled);
        return session;
    }

    private static Level100ActorDefinitionSet LoadMaterializedActorDefinitions()
    {
        string path = Path.Combine(
            AppContext.BaseDirectory,
            "Assets",
            "Level100",
            "StaticWorld",
            "level100-static-world.json");
        return Level100ActorDefinitionManifest.Decode(File.ReadAllBytes(path));
    }
}
