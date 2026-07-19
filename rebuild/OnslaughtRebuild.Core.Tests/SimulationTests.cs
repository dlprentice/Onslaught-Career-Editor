// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Core.Tests;

public sealed class SimulationTests
{
    [Fact]
    public void Constructor_RejectsZeroSeed()
    {
        Assert.Throws<ArgumentOutOfRangeException>(() => new Simulation(0));
    }

    [Theory]
    [InlineData(73_904, 62_272, -11_153)]
    [InlineData(73_895, 62_287, -11_161)]
    [InlineData(73_647, 62_729, -11_469)]
    public void Level100Terrain_MatchesCopiedRetailGroundSamples(
        int retailXFixed,
        int retailYFixed,
        int expectedHeightUnits)
    {
        Assert.Equal(
            expectedHeightUnits,
            Level100Terrain.Instance.SampleHeightUnitsAtFixed(retailXFixed, retailYFixed));
    }

    [Fact]
    public void WalkerGroundElevation_IsDeterministicCoreState()
    {
        Simulation first = CreatePlayingSimulation();
        Simulation repeat = CreatePlayingSimulation();

        Assert.Equal(211, first.Snapshot.PlayerGroundElevationMillimeters);
        for (int tick = 0; tick < 40; tick++)
        {
            WorldSnapshot firstState = first.Step(new SimInput(-1, 1));
            WorldSnapshot repeatState = repeat.Step(new SimInput(-1, 1));
            Assert.Equal(
                firstState.PlayerGroundElevationMillimeters,
                repeatState.PlayerGroundElevationMillimeters);
            Assert.Equal(StateHasher.ComputeHex(firstState), StateHasher.ComputeHex(repeatState));
        }

        Assert.Equal(new SimVector2(-3_705, 1_007), first.Snapshot.PlayerPosition);
        Assert.Equal(5, first.Snapshot.PlayerGroundElevationMillimeters);
    }

    [Fact]
    public void Level100Briefing_ReproducesRetailMessagesPowerAndObjectiveGates()
    {
        var simulation = new Simulation(1);
        var attemptedInput = new SimInput(
            0,
            1,
            SimActions.Fire | SimActions.ToggleMode,
            LookX: 1);

        Assert.Equal(SimulationConstants.Level100OpeningPanTicks, simulation.Snapshot.Level100OpeningTicksRemaining);
        Assert.False(simulation.Snapshot.Level100PlayerControlEnabled);
        Assert.False(simulation.Snapshot.Level100FlightEnabled);
        Assert.False(simulation.Snapshot.Level100WeaponsEnabled);
        Assert.Equal(Level100OpeningPhase.Briefing, simulation.Snapshot.Level100Phase);

        for (int tick = 1; tick <= SimulationConstants.Level100OpeningPanTicks; tick++)
        {
            simulation.Step(attemptedInput);
        }

        Assert.Equal(0, simulation.Snapshot.Level100OpeningTicksRemaining);
        Assert.False(simulation.Snapshot.Level100PlayerControlEnabled);
        Assert.Equal(SimVector2.Zero, simulation.Snapshot.PlayerPosition);
        Assert.Equal(SimulationConstants.Level100PlayerStartYawMicroRad, simulation.Snapshot.FacingYawMicroRad);
        Assert.Equal(VehicleTransition.None, simulation.Snapshot.Transition);
        Assert.Equal(SimulationConstants.MaximumEnergy, simulation.Snapshot.Energy);
        Assert.Empty(simulation.Snapshot.Projectiles);

        (int Start, int End, Level100TutorialMessage Message)[] messages =
        [
            (SimulationConstants.Level100Hud01StartTick, SimulationConstants.Level100Hud01EndTick, Level100TutorialMessage.HudIntroduction),
            (SimulationConstants.Level100Hud02StartTick, SimulationConstants.Level100Hud02EndTick, Level100TutorialMessage.ThreatCircle),
            (SimulationConstants.Level100Hud06StartTick, SimulationConstants.Level100Hud06EndTick, Level100TutorialMessage.Scanner),
            (SimulationConstants.Level100MessageLogStartTick, SimulationConstants.Level100MessageLogEndTick, Level100TutorialMessage.MessageLog),
            (SimulationConstants.Level100TechnicianStartTick, SimulationConstants.Level100TechnicianEndTick, Level100TutorialMessage.TechnicianStatus),
            (SimulationConstants.Level100MovementInstructionStartTick, SimulationConstants.Level100MovementInstructionEndTick, Level100TutorialMessage.MovementControls),
            (SimulationConstants.Level100TargetZone1InstructionStartTick, SimulationConstants.Level100TargetZone1InstructionEndTick, Level100TutorialMessage.ReachTargetZone1),
            (SimulationConstants.Level100ScannerInstructionStartTick, SimulationConstants.Level100ScannerInstructionEndTick, Level100TutorialMessage.ScannerObjective),
        ];
        foreach ((int start, int end, Level100TutorialMessage message) in messages)
        {
            StepUntilLevel100Tick(simulation, start);
            Assert.Equal(message, simulation.Snapshot.Level100Message);
            StepUntilLevel100Tick(simulation, end);
            Assert.Equal(Level100TutorialMessage.None, simulation.Snapshot.Level100Message);
        }

        var second = new Simulation(1);
        StepUntilLevel100Tick(second, SimulationConstants.Level100PowerActivationTick - 1, attemptedInput);
        Assert.False(second.Snapshot.Level100PlayerControlEnabled);
        Assert.Equal(SimVector2.Zero, second.Snapshot.PlayerPosition);

        WorldSnapshot handoff = second.Step(attemptedInput);
        Assert.True(handoff.Level100PlayerControlEnabled);
        Assert.Equal(SimVector2.Zero, handoff.PlayerPosition);

        WorldSnapshot playing = second.Step(new SimInput(0, 1, SimActions.Fire | SimActions.ToggleMode, LookX: 1));
        Assert.NotEqual(SimVector2.Zero, playing.PlayerPosition);
        Assert.NotEqual(SimulationConstants.Level100PlayerStartYawMicroRad, playing.FacingYawMicroRad);
        Assert.Equal(VehicleTransition.None, playing.Transition);
        Assert.Empty(playing.Projectiles);

        StepUntilLevel100Tick(second, SimulationConstants.Level100TargetZone1ActivationTick - 1);
        Assert.Equal(Level100OpeningPhase.Briefing, second.Snapshot.Level100Phase);
        Assert.Equal(
            Level100OpeningPhase.ReachTargetZone1,
            second.Step(SimInput.Idle).Level100Phase);
    }

    [Fact]
    public void WalkerForward_AcceleratesToMeasuredCapAndCoastsAfterRelease()
    {
        Simulation simulation = CreatePlayingSimulation();

        foreach (SimVector2 expected in new[]
                 {
                     new SimVector2(-16, 29),
                     new SimVector2(-28, 51),
                     new SimVector2(-38, 69),
                     new SimVector2(-45, 83),
                     new SimVector2(-47, 87),
                 })
        {
            WorldSnapshot state = simulation.Step(new SimInput(0, 1));
            Assert.Equal(expected, state.PlayerVelocity);
        }

        foreach (SimVector2 expected in new[]
                 {
                     new SimVector2(-37, 68),
                     new SimVector2(-29, 53),
                     new SimVector2(-22, 41),
                     new SimVector2(-17, 32),
                     new SimVector2(-13, 25),
                 })
        {
            WorldSnapshot state = simulation.Step(SimInput.Idle);
            Assert.Equal(expected, state.PlayerVelocity);
        }
    }

    [Fact]
    public void WalkerStrafe_UsesTheSameMeasuredResponseAsForward()
    {
        Simulation simulation = CreatePlayingSimulation();

        foreach (SimVector2 expected in new[]
                 {
                     new SimVector2(29, 16),
                     new SimVector2(51, 28),
                     new SimVector2(69, 38),
                     new SimVector2(83, 45),
                     new SimVector2(87, 47),
                 })
        {
            WorldSnapshot state = simulation.Step(new SimInput(1, 0));
            Assert.Equal(expected, state.PlayerVelocity);
        }
    }

    [Fact]
    public void WalkerLook_AcceleratesBodyYawAndCoastsAfterRelease()
    {
        Simulation simulation = CreatePlayingSimulation();

        foreach (int expected in new[] { 10_444, 19_444, 27_200, 33_884, 39_644 })
        {
            WorldSnapshot state = simulation.Step(new SimInput(0, 0, LookX: 1));
            Assert.Equal(expected, state.WalkerYawVelocityMicroRadPerTick);
        }

        WorldSnapshot coast = simulation.Step(SimInput.Idle);
        Assert.Equal(34_164, coast.WalkerYawVelocityMicroRadPerTick);
        Assert.Equal(674_610, coast.FacingYawMicroRad);
    }

    [Fact]
    public void WalkerMovementUsesContinuousBodyYawWithoutResettingLookYaw()
    {
        Simulation simulation = CreatePlayingSimulation();
        for (int tick = 0; tick < 20; tick++)
        {
            simulation.Step(new SimInput(0, 0, LookX: 1));
        }

        WorldSnapshot state = simulation.Step(new SimInput(0, 1));
        Assert.Equal(1, state.FacingX);
        Assert.Equal(0, state.FacingZ);
        Assert.Equal(1_635_706, state.FacingYawMicroRad);
        Assert.Equal(new SimVector2(-33, -2), state.PlayerVelocity);
    }

    [Fact]
    public void LookX_OutsideUnitRange_IsRejected()
    {
        var input = new SimInput(0, 0, LookX: 2);
        Assert.Throws<ArgumentOutOfRangeException>(input.Validate);
    }

    [Fact]
    public void LookX_OneTick_DoesNotYetLeaveForwardFacing()
    {
        Simulation simulation = CreatePlayingSimulation();
        WorldSnapshot state = simulation.Step(new SimInput(0, 0, LookX: 1));
        Assert.Equal(0, state.FacingX);
        Assert.Equal(1, state.FacingZ);
        Assert.Equal(520_274, state.FacingYawMicroRad);
    }

    [Fact]
    public void LookX_Negative_TurnsLeftFromTheAuthoredStartYaw()
    {
        Simulation simulation = CreatePlayingSimulation();
        for (int tick = 0; tick < 20; tick++)
        {
            simulation.Step(new SimInput(0, 0, LookX: -1));
        }

        WorldSnapshot state = simulation.Snapshot;
        Assert.Equal(-1, state.FacingX);
        Assert.Equal(1, state.FacingZ);
    }

    [Fact]
    public void JetEnergyDrain_MatchesAcceptedEnergyP02Translation()
    {
        // Dual-accept mid |rate| ≈ 0.5169 energy units/s → round(|r|*1000/30)=17.
        // Policy: jet-energy-drain-retail-to-core-translation-policy.md
        Assert.Equal(17, SimulationConstants.JetEnergyDrainPerTick);
        const double midAbsRate = 0.5169068149241056;
        int mapped = (int)Math.Round(midAbsRate * 1000.0 / SimulationConstants.TicksPerSecond);
        Assert.Equal(SimulationConstants.JetEnergyDrainPerTick, mapped);
    }

    [Fact]
    public void Reset_DominatesOtherActionsInTheSameInputSlot()
    {
        Simulation simulation = CreatePlayingSimulation();
        simulation.Step(new SimInput(1, 0, SimActions.Fire));

        WorldSnapshot reset = simulation.Step(new SimInput(
            1,
            1,
            SimActions.Reset | SimActions.Fire | SimActions.ToggleMode));

        Assert.Equal(SimulationConstants.Level100TargetZone1ActivationTick + 2, reset.Tick);
        Assert.Equal(VehicleMode.Walker, reset.Mode);
        Assert.Equal(SimVector2.Zero, reset.PlayerPosition);
        Assert.Equal(SimulationConstants.MaximumEnergy, reset.Energy);
        Assert.Equal(SimulationConstants.MaximumShield, reset.Shield);
        Assert.Empty(reset.Projectiles);
    }

    [Fact]
    public void Movement_IsNotClampedByTheRetiredSyntheticArena()
    {
        Simulation simulation = CreatePlayingSimulation();

        for (int tick = 0; tick < 500; tick++)
        {
            simulation.Step(new SimInput(1, 1));
        }

        long distanceSquared =
            ((long)simulation.Snapshot.PlayerPosition.X * simulation.Snapshot.PlayerPosition.X) +
            ((long)simulation.Snapshot.PlayerPosition.Z * simulation.Snapshot.PlayerPosition.Z);
        Assert.True(distanceSquared > 30_000L * 30_000L);
        Assert.NotEqual(SimVector2.Zero, simulation.Snapshot.PlayerVelocity);
    }

    [Fact]
    public void Level100Opening_AdvancesThroughAuthoredTriggersAfterScriptDelay()
    {
        Simulation simulation = CreatePlayingSimulation();

        Assert.Equal(Level100OpeningPhase.ReachTargetZone1, simulation.Snapshot.Level100Phase);
        Assert.Equal(
            SimulationConstants.Level100PlayerStartYawMicroRad,
            simulation.Snapshot.FacingYawMicroRad);

        DriveToPhase(
            simulation,
            SimulationConstants.Level100TargetZone1Position,
            Level100OpeningPhase.TargetZone1DispatchPending);
        Assert.Equal(
            SimulationConstants.Level100ObjectiveDispatchTicks,
            simulation.Snapshot.Level100DispatchTicksRemaining);

        for (int tick = 1; tick < SimulationConstants.Level100ObjectiveDispatchTicks; tick++)
        {
            WorldSnapshot pending = simulation.Step(SimInput.Idle);
            Assert.Equal(Level100OpeningPhase.TargetZone1DispatchPending, pending.Level100Phase);
        }

        Assert.Equal(
            Level100OpeningPhase.ReachFiringRange,
            simulation.Step(SimInput.Idle).Level100Phase);

        DriveToPhase(
            simulation,
            SimulationConstants.Level100FiringRangePosition,
            Level100OpeningPhase.FiringRangeDispatchPending);
        for (int tick = 0; tick < SimulationConstants.Level100ObjectiveDispatchTicks; tick++)
        {
            simulation.Step(SimInput.Idle);
        }

        Assert.Equal(Level100OpeningPhase.FiringRangeReached, simulation.Snapshot.Level100Phase);
    }

    [Fact]
    public void Reset_RestoresDynamicStateWithoutRewindingReplayTick()
    {
        Simulation simulation = CreatePlayingSimulation(42);
        simulation.Step(new SimInput(1, 0));
        simulation.Step(new SimInput(0, 0, SimActions.ToggleMode));

        WorldSnapshot reset = simulation.Step(new SimInput(0, 0, SimActions.Reset));

        Assert.Equal(SimulationConstants.Level100TargetZone1ActivationTick + 3, reset.Tick);
        Assert.Equal(VehicleMode.Walker, reset.Mode);
        Assert.Equal(SimVector2.Zero, reset.PlayerPosition);
        Assert.Equal(SimulationConstants.MaximumEnergy, reset.Energy);
        Assert.Equal(SimulationConstants.MaximumShield, reset.Shield);
        Assert.Equal(0, reset.TargetsDestroyed);
        Assert.Empty(reset.Projectiles);
    }

    [Fact]
    public void SnapshotCollections_DoNotExposeMutableArrays()
    {
        Simulation simulation = CreatePlayingSimulation();
        WorldSnapshot state = simulation.Step(new SimInput(0, 0, SimActions.Fire));

        Assert.False(state.Targets.GetType().IsArray);
        Assert.False(state.Projectiles.GetType().IsArray);

        var targets = Assert.IsAssignableFrom<IList<TargetSnapshot>>(state.Targets);
        var projectiles = Assert.IsAssignableFrom<IList<ProjectileSnapshot>>(state.Projectiles);
        Assert.True(targets.IsReadOnly);
        Assert.True(projectiles.IsReadOnly);
        Assert.Throws<NotSupportedException>(() => targets[0] = targets[0] with { Hull = 0 });
    }

    private static void DriveToPhase(
        Simulation simulation,
        SimVector2 destination,
        Level100OpeningPhase expectedPhase)
    {
        for (int tick = 0; tick < 2_000 && simulation.Snapshot.Level100Phase != expectedPhase; tick++)
        {
            SimVector2 position = simulation.Snapshot.PlayerPosition;
            sbyte moveX = (sbyte)Math.Sign(destination.X - position.X);
            sbyte moveZ = (sbyte)Math.Sign(destination.Z - position.Z);
            simulation.Step(new SimInput(moveX, moveZ));
        }

        Assert.Equal(expectedPhase, simulation.Snapshot.Level100Phase);
    }

    private static Simulation CreatePlayingSimulation(uint seed = 1)
    {
        var simulation = new Simulation(seed);
        for (int tick = 0; tick < SimulationConstants.Level100TargetZone1ActivationTick; tick++)
        {
            simulation.Step(SimInput.Idle);
        }

        Assert.True(simulation.Snapshot.Level100PlayerControlEnabled);
        return simulation;
    }

    private static void StepUntilLevel100Tick(
        Simulation simulation,
        int timelineTick,
        SimInput? input = null)
    {
        while (simulation.Snapshot.Level100TimelineTick < timelineTick)
        {
            simulation.Step(input ?? SimInput.Idle);
        }
        Assert.Equal(timelineTick, simulation.Snapshot.Level100TimelineTick);
    }
}
