// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.Client;

namespace OnslaughtRebuild.Client.Tests;

public sealed class InteractiveSessionTests
{
    private const uint Seed = 0x4F4E534Cu;

    [Fact]
    public void RationalAccumulator_DoesNotTruncateThirtyHertzStep()
    {
        var session = new InteractiveSession(Seed);

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
        var session = new InteractiveSession(Seed);

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
        var session = new InteractiveSession(Seed);

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

        Assert.Equal(SimulationConstants.Level100TargetZone1ActivationTick + 30, coarse.CurrentSnapshot.Tick);
        Assert.Equal(SimulationConstants.Level100TargetZone1ActivationTick + 30, fine.CurrentSnapshot.Tick);
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
    public void InteractiveInputSequence_MatchesDirectCoreTicks()
    {
        InteractiveSession session = CreatePlayingSession();
        var direct = new Simulation(Seed);
        for (int tick = 0; tick < SimulationConstants.Level100TargetZone1ActivationTick; tick++)
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
        session.QueueFirePulse();

        session.SuspendInputUntilReleased();
        session.ObserveInput(new InteractiveInput(0, 1, true, false, false));
        session.QueueMovementPulse(1, 0);
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
        var session = new InteractiveSession(Seed);

        Assert.Throws<ArgumentOutOfRangeException>(() =>
            session.ObserveInput(new InteractiveInput(2, 0, false, false, false)));
        Assert.Throws<ArgumentOutOfRangeException>(() => session.AdvanceFrameTicks(-1));
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
    public void FirstFlightSmokeScenario_ReachesTheFiringRangeAssignment()
    {
        InteractiveInput pan = FirstFlightSmokeScenario.GetInputForTick(0);
        InteractiveInput strafe = FirstFlightSmokeScenario.GetInputForTick(
            SimulationConstants.Level100TargetZone1ActivationTick + 57);
        InteractiveInput forward = FirstFlightSmokeScenario.GetInputForTick(
            SimulationConstants.Level100TargetZone1ActivationTick + 57 + 216);
        InteractiveInput closeout = FirstFlightSmokeScenario.GetInputForTick(
            FirstFlightSmokeScenario.DurationTicks - 1);

        Assert.Equal(InteractiveInput.Idle, pan);
        Assert.Equal((sbyte)-1, strafe.MoveX);
        Assert.False(strafe.FireHeld);
        Assert.Equal((sbyte)1, forward.MoveZ);
        Assert.False(forward.ToggleModeHeld);
        Assert.Equal(InteractiveInput.Idle, closeout);
        Assert.Equal(1_995, FirstFlightSmokeScenario.DurationTicks);
        Assert.Throws<ArgumentOutOfRangeException>(() => FirstFlightSmokeScenario.GetInputForTick(-1));
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

    private static InteractiveSession CreatePlayingSession(uint seed = Seed)
    {
        var session = new InteractiveSession(seed);
        const long oneCoreStepTicks =
            (TimeSpan.TicksPerSecond / SimulationConstants.TicksPerSecond) + 1;
        for (int tick = 0; tick < SimulationConstants.Level100TargetZone1ActivationTick; tick++)
        {
            session.AdvanceFrameTicks(oneCoreStepTicks);
        }

        Assert.True(session.CurrentSnapshot.Level100PlayerControlEnabled);
        return session;
    }
}
