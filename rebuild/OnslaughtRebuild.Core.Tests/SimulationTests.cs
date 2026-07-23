// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.TestSupport;

namespace OnslaughtRebuild.Core.Tests;

public sealed class SimulationTests
{
    private static readonly Level100TutorialProgress CompletedTutorialSlots =
        new(Introduction: true, PulseCannon: true, VulcanCannon: true, StatusBars: true);

    [Fact]
    public void Constructor_RejectsZeroSeed()
    {
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            new Simulation(0, Level100TestActorDefinitions.Create()));
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
    public void Level100Terrain_ExposesReleasedWaterSelection()
    {
        Assert.Equal(
            unchecked((int)0xC10D70A4),
            BitConverter.SingleToInt32Bits(Level100Terrain.Instance.WaterLevel));
        Assert.Equal(0, Level100Terrain.Instance.WaterTexture);
    }

    [Theory]
    [InlineData(36, 30, 0x420C2A31)]
    [InlineData(36, 31, 0x416C43B1)]
    [InlineData(35, 30, 0x41A9B2A7)]
    [InlineData(0, 0, 0x00000000)]
    public void Level100Terrain_ReproducesReleasedPatchComplexity(
        int tileX,
        int tileY,
        int expectedFloatBits)
    {
        Assert.Equal(
            expectedFloatBits,
            BitConverter.SingleToInt32Bits(
                Level100Terrain.Instance.GetTileComplexityScore(tileX, tileY)));
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
    public void CanonicalHashRetainsResetBaselineGroundDeltaAndExactFootPhase()
    {
        Simulation simulation = CreatePlayingSimulation();
        WorldSnapshot state = simulation.Step(new SimInput(0, 1));
        for (int tick = 0;
             state.WalkerFeet.All(foot => foot.PhaseThirds == 0) && tick < 120;
             tick++)
        {
            state = simulation.Step(new SimInput(0, 1));
        }

        Assert.Contains(state.WalkerFeet, foot => foot.PhaseThirds > 0);
        Level100ActorSnapshot player = state.Level100Actors.Actors.Single(actor =>
            actor.ThingTypeMask == Level100ReleasedThingTypeMasks.BattleEngine);
        Assert.Equal(
            state.PlayerGroundDeltaMillimeters,
            player.Pose.LinearVelocityMillimetersPerTick.Y);

        string hash = StateHasher.ComputeHex(state);
        Assert.NotEqual(hash, StateHasher.ComputeHex(state with
        {
            PlayerGroundDeltaMillimeters = state.PlayerGroundDeltaMillimeters + 1,
        }));
        WalkerFootContactSnapshot changedFoot = state.WalkerFeet[0] with
        {
            PhaseThirds = state.WalkerFeet[0].PhaseThirds + 1,
        };
        Assert.NotEqual(hash, StateHasher.ComputeHex(state with
        {
            WalkerFeet = state.WalkerFeet
                .Select((foot, index) => index == 0 ? changedFoot : foot)
                .ToArray(),
        }));
        Assert.NotEqual(hash, StateHasher.ComputeHex(state with
        {
            InitialLevel100TutorialProgress = default,
        }));

        WorldSnapshot reset = simulation.Step(new SimInput(0, 0, SimActions.Reset));
        Assert.Equal(CompletedTutorialSlots, reset.InitialLevel100TutorialProgress);
    }

    [Fact]
    public void WalkerFeet_RepeatReleasedDiagonalStepsAndSettleOnTheLevel100Slope()
    {
        Simulation first = CreatePlayingSimulation();
        Simulation repeat = CreatePlayingSimulation();
        int[]? firstSwing = null;

        for (int tick = 0; tick < 360; tick++)
        {
            WorldSnapshot firstState = first.Step(new SimInput(0, 1));
            WorldSnapshot repeatState = repeat.Step(new SimInput(0, 1));
            Assert.Equal(StateHasher.ComputeHex(firstState), StateHasher.ComputeHex(repeatState));
            firstSwing ??= firstState.WalkerFeet.Any(foot => foot.StepPhase > 0)
                ? firstState.WalkerFeet
                    .Where(foot => foot.StepPhase > 0)
                    .Select(foot => foot.Id)
                    .ToArray()
                : null;
        }

        Assert.NotNull(firstSwing);
        Assert.Equal([0, 3], firstSwing!);
        for (int tick = 0; tick < 450; tick++)
        {
            WorldSnapshot firstState = first.Step(SimInput.Idle);
            WorldSnapshot repeatState = repeat.Step(SimInput.Idle);
            Assert.Equal(StateHasher.ComputeHex(firstState), StateHasher.ComputeHex(repeatState));
        }

        Assert.All(first.Snapshot.WalkerFeet, foot =>
        {
            Assert.Equal(0, foot.StepPhase);
            Assert.Equal(0, foot.LiftMillimeters);
            Assert.Equal(
                Level100Terrain.Instance.SampleGroundElevationMillimeters(foot.Position),
                foot.GroundElevationMillimeters);
        });
        Assert.True(
            first.Snapshot.WalkerFeet.Max(foot => foot.GroundElevationMillimeters) -
            first.Snapshot.WalkerFeet.Min(foot => foot.GroundElevationMillimeters) >= 500);
    }

    [Fact]
    public void Level100FirstRun_AppliesReleasedMessagesActivationAndTriggerCommands()
    {
        var simulation = new Simulation(1, Level100TestActorDefinitions.Create());
        var attemptedInput = new SimInput(
            0,
            1,
            SimActions.Fire | SimActions.ToggleMode,
            LookX: 1);

        Assert.Equal(SimulationConstants.Level100OpeningPanTicks, simulation.Snapshot.Level100OpeningTicksRemaining);
        Assert.False(simulation.Snapshot.Level100PlayerControlEnabled);
        Assert.False(simulation.Snapshot.Level100FlightEnabled);
        Assert.False(simulation.Snapshot.Level100PulseCannonEnabled);
        Assert.Empty(simulation.Snapshot.Level100Mission.PendingEvents);
        Assert.Contains(
            simulation.Snapshot.Level100MissionEvents.OfType<Level100MessageRequested>(),
            message => message.MessageId == 292562);

        var messages = simulation.Snapshot.Level100MissionEvents
            .OfType<Level100MessageRequested>()
            .Select(message => message.MessageId)
            .ToList();

        for (int tick = 1; tick <= SimulationConstants.Level100OpeningPanTicks; tick++)
        {
            WorldSnapshot state = simulation.Step(attemptedInput);
            messages.AddRange(state.Level100MissionEvents
                .OfType<Level100MessageRequested>()
                .Select(message => message.MessageId));
        }

        Assert.Equal(0, simulation.Snapshot.Level100OpeningTicksRemaining);
        Assert.False(simulation.Snapshot.Level100PlayerControlEnabled);
        Assert.Equal(SimVector2.Zero, simulation.Snapshot.PlayerPosition);
        Assert.Equal(SimulationConstants.Level100PlayerStartYawMicroRad, simulation.Snapshot.FacingYawMicroRad);
        Assert.Equal(VehicleTransition.None, simulation.Snapshot.Transition);
        Assert.Equal(SimulationConstants.MaximumEnergy, simulation.Snapshot.Energy);
        Assert.Empty(simulation.Snapshot.Projectiles);

        AdvanceUntil(
            simulation,
            state => string.Equals(
                state.Level100Mission.NavigationObjective,
                "Target Zone 1",
                StringComparison.Ordinal),
            1_000,
            state => messages.AddRange(state.Level100MissionEvents
                .OfType<Level100MessageRequested>()
                .Select(message => message.MessageId)));

        Assert.Equal(
            [292562, 293386, 296682, -1575499396, -257967449, 82987417, 4422830, 175347826],
            messages);
        Assert.Equal(1_005, simulation.Snapshot.Level100Mission.Tick);
        Assert.True(simulation.Snapshot.Level100PlayerActive);
        Assert.True(simulation.Snapshot.Level100PlayerControlEnabled);
        Level100TriggerActorSnapshot trigger = simulation.Snapshot.Level100TriggerActors
            .Single(item => item.Trigger == Level100MissionTrigger.TargetZone1);
        Assert.True(trigger.Active);
        Assert.True(trigger.IsObjective);
        Assert.False(trigger.Reached);
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
    public void WalkerVerticalLook_UsesMeasuredPitchInertiaCoastAndOpeningSlopeBounds()
    {
        Simulation simulation = CreatePlayingSimulation();

        (int Velocity, int Pitch)[] expected =
        [
            (-3_938, -3_938),
            (-7_331, -11_269),
            (-10_255, -21_524),
            (-12_775, -34_299),
            (-14_947, -49_246),
        ];
        foreach ((int velocity, int pitch) in expected)
        {
            WorldSnapshot state = simulation.Step(new SimInput(0, 0, LookY: -1));
            Assert.Equal(velocity, state.WalkerPitchVelocityMicroRadPerTick);
            Assert.Equal(pitch, state.FacingPitchMicroRad);
        }

        WorldSnapshot coast = simulation.Step(SimInput.Idle);
        Assert.Equal(-12_880, coast.WalkerPitchVelocityMicroRadPerTick);
        Assert.Equal(-62_126, coast.FacingPitchMicroRad);

        for (int tick = 0; tick < 100; tick++)
        {
            simulation.Step(new SimInput(0, 0, LookY: -1));
        }
        Assert.Equal(SimulationConstants.WalkerPitchUpLimitMicroRad, simulation.Snapshot.FacingPitchMicroRad);
        Assert.Equal(0, simulation.Snapshot.WalkerPitchVelocityMicroRadPerTick);

        for (int tick = 0; tick < 200; tick++)
        {
            simulation.Step(new SimInput(0, 0, LookY: 1));
        }
        Assert.Equal(SimulationConstants.WalkerPitchDownLimitMicroRad, simulation.Snapshot.FacingPitchMicroRad);
        Assert.Equal(0, simulation.Snapshot.WalkerPitchVelocityMicroRadPerTick);
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
    public void SnapshotPlayerOwners_AgreeAfterMovementDamageActivationDeathAndReset()
    {
        Simulation simulation = CreatePlayingSimulation();

        WorldSnapshot state = simulation.Step(
            new SimInput(1, 1, SimActions.ToggleMode, LookX: 1),
            [new Level100PlayerDamageFact(137)]);

        AssertCanonicalPlayer(state);
        Assert.Equal(VehicleTransition.None, state.Transition);

        state = simulation.Step(
            SimInput.Idle,
            [new Level100ActorActivationFact(
                state.Level100Actors.Actors.Single(actor =>
                    actor.ThingTypeMask == Level100ReleasedThingTypeMasks.BattleEngine).ActorId,
                false)]);
        AssertCanonicalPlayer(state);
        Assert.False(state.Level100PlayerActive);

        Level100ActorId playerId = state.Level100Actors.Actors.Single(actor =>
            actor.ThingTypeMask == Level100ReleasedThingTypeMasks.BattleEngine).ActorId;
        state = simulation.Step(
            SimInput.Idle,
            [new Level100ActorActivationFact(playerId, true),
             new Level100PlayerDamageFact(SimulationConstants.MaximumHull)]);
        AssertCanonicalPlayer(state);
        Assert.Equal(0, state.Hull);
        Assert.Equal(Level100ActorLifecycle.Destroyed, state.Level100Actors.Actors.Single(
            actor => actor.ActorId == playerId).Lifecycle);

        state = simulation.Step(new SimInput(0, 0, SimActions.Reset));
        AssertCanonicalPlayer(state);
        Assert.Equal(SimulationConstants.MaximumHull, state.Hull);
        Assert.Equal(Level100ActorLifecycle.Alive, state.Level100Actors.Actors.Single(
            actor => actor.ActorId == playerId).Lifecycle);
    }

    private static void AssertCanonicalPlayer(WorldSnapshot state)
    {
        Level100ActorSnapshot player = state.Level100Actors.Actors.Single(actor =>
            actor.ThingTypeMask == Level100ReleasedThingTypeMasks.BattleEngine);
        Assert.Equal(state.PlayerPosition.X, player.Pose.PositionMillimeters.X);
        Assert.Equal(state.PlayerGroundElevationMillimeters, player.Pose.PositionMillimeters.Y);
        Assert.Equal(state.PlayerPosition.Z, player.Pose.PositionMillimeters.Z);
        Assert.Equal(state.PlayerVelocity.X, player.Pose.LinearVelocityMillimetersPerTick.X);
        Assert.Equal(
            state.PlayerGroundDeltaMillimeters,
            player.Pose.LinearVelocityMillimetersPerTick.Y);
        Assert.Equal(state.PlayerVelocity.Z, player.Pose.LinearVelocityMillimetersPerTick.Z);
        Assert.Equal(state.Hull, player.Health);
        Assert.Equal(state.Level100PlayerActive, player.Active);
        Assert.Equal(state.Mode == VehicleMode.Jet, state.Level100ActorScripts.PlayerInJetMode);
    }

    [Fact]
    public void LookAxes_OutsideUnitRange_AreRejected()
    {
        Assert.Throws<ArgumentOutOfRangeException>(
            new SimInput(0, 0, LookX: 2).Validate);
        Assert.Throws<ArgumentOutOfRangeException>(
            new SimInput(0, 0, LookY: -2).Validate);
        Assert.Throws<ArgumentOutOfRangeException>(
            new SimInput(0, 0, LookXAnalogPermille: 1_001).Validate);
        Assert.Throws<ArgumentOutOfRangeException>(
            new SimInput(0, 0, LookYAnalogPermille: -1_001).Validate);
    }

    [Fact]
    public void WalkerAnalogLook_IsProportionalAndUsesTheSameRetailCoast()
    {
        Simulation half = CreatePlayingSimulation();
        Simulation full = CreatePlayingSimulation();

        WorldSnapshot halfInput = half.Step(new SimInput(0, 0, LookXAnalogPermille: 500));
        WorldSnapshot fullInput = full.Step(new SimInput(0, 0, LookXAnalogPermille: 1_000));

        Assert.Equal(5_222, halfInput.WalkerYawVelocityMicroRadPerTick);
        Assert.Equal(10_444, fullInput.WalkerYawVelocityMicroRadPerTick);
        Assert.Equal(
            halfInput.FacingYawMicroRad - SimulationConstants.Level100PlayerStartYawMicroRad,
            (fullInput.FacingYawMicroRad - SimulationConstants.Level100PlayerStartYawMicroRad) / 2);

        WorldSnapshot coast = half.Step(SimInput.Idle);
        Assert.Equal(4_500, coast.WalkerYawVelocityMicroRadPerTick);
        Assert.Equal(
            halfInput.FacingYawMicroRad + coast.WalkerYawVelocityMicroRadPerTick,
            coast.FacingYawMicroRad);
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

        Assert.Equal(SimulationConstants.Level100OpeningPanTicks + 2, reset.Tick);
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
    public void Level100ObservedFacilityContacts_PreserveSlideAndPreventEntry()
    {
        Simulation towerRun = CreatePlayingSimulation();
        AimAtTargetAndSettle(towerRun, SimulationConstants.Level100ControlTowerPosition);
        bool observedTowerSlide = false;
        for (int tick = 0; tick < 260; tick++)
        {
            WorldSnapshot state = towerRun.Step(new SimInput(0, 1));
            long offsetX = (long)state.PlayerPosition.X -
                SimulationConstants.Level100ControlTowerPosition.X;
            long offsetZ = (long)state.PlayerPosition.Z -
                SimulationConstants.Level100ControlTowerPosition.Z;
            long radius = SimulationConstants.Level100ControlTowerContactRadius;
            Assert.True((offsetX * offsetX) + (offsetZ * offsetZ) >= radius * radius);
            observedTowerSlide |=
                Math.Abs(offsetX * state.PlayerVelocity.Z - offsetZ * state.PlayerVelocity.X) >
                    40_000;
        }

        Assert.True(observedTowerSlide);

        Simulation factoryRun = CreatePlayingSimulation();
        AimAtTargetAndSettle(factoryRun, SimulationConstants.Level100TankFactoryPosition);
        bool reachedFactory = false;
        bool removedFactoryInwardMotion = false;
        for (int tick = 0; tick < 360; tick++)
        {
            WorldSnapshot state = factoryRun.Step(new SimInput(0, 1));
            long offsetX = (long)state.PlayerPosition.X -
                SimulationConstants.Level100TankFactoryPosition.X;
            long offsetZ = (long)state.PlayerPosition.Z -
                SimulationConstants.Level100TankFactoryPosition.Z;
            long radius = SimulationConstants.Level100TankFactoryContactRadius;
            long distanceSquared = (offsetX * offsetX) + (offsetZ * offsetZ);
            Assert.True(distanceSquared >= radius * radius);
            reachedFactory |= distanceSquared <= (radius + 2L) * (radius + 2L);
            if (distanceSquared <= (radius + 2L) * (radius + 2L))
            {
                long radialVelocity =
                    (offsetX * state.PlayerVelocity.X) +
                    (offsetZ * state.PlayerVelocity.Z);
                removedFactoryInwardMotion |= radialVelocity >= -(radius * 2L);
            }
        }

        Assert.True(reachedFactory);
        Assert.True(removedFactoryInwardMotion);
    }

    [Fact]
    public void Level100Triggers_UsePhysicalActorsAndReleasedSideScriptDispatch()
    {
        Simulation simulation = CreatePlayingSimulation();

        AdvanceUntilNavigation(simulation, "Target Zone 1", 500);
        Assert.True(Trigger(simulation, Level100MissionTrigger.TargetZone1).Active);
        Level100ActorScriptContinuationSnapshot targetZonePause =
            DriveUntilTriggerPause(simulation, Level100MissionTrigger.TargetZone1);
        Level100TriggerActorSnapshot targetZone = Trigger(
            simulation,
            Level100MissionTrigger.TargetZone1);
        Assert.False(targetZone.Reached);
        Assert.Equal(Level100ActorScriptWaitKind.Pause, targetZonePause.WaitKind);
        Assert.Equal(15, targetZonePause.DueTick - simulation.Snapshot.Tick);

        for (int tick = 1; tick < 15; tick++)
        {
            Assert.False(Trigger(
                simulation.Step(SimInput.Idle),
                Level100MissionTrigger.TargetZone1).Reached);
        }

        WorldSnapshot firingRangeAssignment = simulation.Step(SimInput.Idle);
        Assert.True(Trigger(firingRangeAssignment, Level100MissionTrigger.TargetZone1).Reached);
        Assert.Equal("Firing Range", firingRangeAssignment.Level100Mission.NavigationObjective);
        Assert.Contains(
            firingRangeAssignment.Level100MissionEvents.OfType<Level100MessageRequested>(),
            message => message.MessageId == 4458134);

        Level100ActorScriptContinuationSnapshot firingRangePause =
            DriveUntilTriggerPause(simulation, Level100MissionTrigger.FiringRange);
        Assert.Equal(Level100ActorScriptWaitKind.Pause, firingRangePause.WaitKind);
        Assert.Equal(15, firingRangePause.DueTick - simulation.Snapshot.Tick);
        for (int tick = 0; tick < 15; tick++)
        {
            simulation.Step(SimInput.Idle);
        }

        Assert.True(Trigger(simulation, Level100MissionTrigger.FiringRange).Reached);
        Assert.Equal(
            Level100PrimaryObjectiveStatus.Complete,
            simulation.Snapshot.Level100Mission.PrimaryObjectives[0].Status);
        Assert.True(simulation.Snapshot.Level100FiringRangeTargetsActive);
        Assert.False(simulation.Snapshot.Level100PulseCannonEnabled);
        for (int tick = 0; tick < 30; tick++)
        {
            simulation.Step(SimInput.Idle);
        }

        Assert.True(simulation.Snapshot.Level100PulseCannonEnabled);
        Assert.Single(simulation.Step(new SimInput(0, 0, SimActions.Fire)).Projectiles);
    }

    [Fact]
    public void Level100SimulationFailureTape_FirstRunRetainsLossTextAndExactTicks()
    {
        DeterministicSimulationTape first = RunLevel100FailureTape();
        DeterministicSimulationTape repeat = RunLevel100FailureTape();

        Assert.Equal(first.Hashes, repeat.Hashes);
        Assert.Equal(Level100MissionOutcome.Lost, first.Snapshot.Level100Mission.Outcome);
        Assert.Equal(Level100MissionFailureReason.TutorialBroken,
            first.Snapshot.Level100Mission.FailureReason);
        Assert.Equal(1_110_345_999, first.Snapshot.Level100Mission.FailureTextId);
        Assert.Equal(
            Level100MissionTerminalState.FailureCountdownElapsed,
            first.Snapshot.Level100Mission.TerminalState);
        Assert.Equal(0, first.Snapshot.Level100Mission.TerminalTicksRemaining);
    }

    [Fact]
    public void PitchedPulseRound_FollowsViewPitchWithoutInventingVerticalTargetHits()
    {
        Simulation simulation = CreateFiringRangeExerciseSimulation();
        TargetSnapshot target = simulation.Snapshot.Targets.Single(item => item.Id == 1);
        AimAtTarget(simulation, target.Position);
        for (int tick = 0; tick < 100; tick++)
        {
            simulation.Step(new SimInput(0, 0, LookY: -1));
        }

        WorldSnapshot fired = simulation.Step(new SimInput(0, 0, SimActions.Fire));
        ProjectileSnapshot projectile = Assert.Single(fired.Projectiles);
        Assert.Equal(SimulationConstants.WalkerPitchUpLimitMicroRad, fired.FacingPitchMicroRad);
        Assert.True(projectile.VerticalVelocityMillimetersPerTick > 0);
        long speedSquared =
            ((long)projectile.Velocity.X * projectile.Velocity.X) +
            ((long)projectile.Velocity.Z * projectile.Velocity.Z) +
            ((long)projectile.VerticalVelocityMillimetersPerTick *
                projectile.VerticalVelocityMillimetersPerTick);
        Assert.InRange(speedSquared, (long)1_166 * 1_166, (long)1_168 * 1_168);
        double yaw = fired.FacingYawMicroRad / 1_000_000d;
        double pitch = fired.FacingPitchMicroRad / 1_000_000d;
        double emitterForwardPlane =
            (SimulationConstants.PulseCannonEmitterForwardMillimeters * Math.Cos(pitch)) +
            (SimulationConstants.PulseCannonEmitterUpMillimeters * Math.Sin(pitch));
        int expectedEmitterOffsetX = (int)Math.Round(
            (SimulationConstants.PulseCannonEmitterRightMillimeters * Math.Cos(yaw)) -
            (emitterForwardPlane * Math.Sin(yaw)),
            MidpointRounding.AwayFromZero);
        int expectedEmitterOffsetZ = (int)Math.Round(
            (SimulationConstants.PulseCannonEmitterRightMillimeters * Math.Sin(yaw)) +
            (emitterForwardPlane * Math.Cos(yaw)),
            MidpointRounding.AwayFromZero);
        Assert.InRange(
            (projectile.Position.X - projectile.Velocity.X) - fired.PlayerPosition.X,
            expectedEmitterOffsetX - 1,
            expectedEmitterOffsetX + 1);
        Assert.InRange(
            (projectile.Position.Z - projectile.Velocity.Z) - fired.PlayerPosition.Z,
            expectedEmitterOffsetZ - 1,
            expectedEmitterOffsetZ + 1);
        int emitterVerticalOffset = (int)Math.Round(
            (-SimulationConstants.PulseCannonEmitterForwardMillimeters *
                Math.Sin(fired.FacingPitchMicroRad / 1_000_000d)) +
            (SimulationConstants.PulseCannonEmitterUpMillimeters *
                Math.Cos(fired.FacingPitchMicroRad / 1_000_000d)),
            MidpointRounding.AwayFromZero);
        Assert.Equal(
            fired.PlayerGroundElevationMillimeters +
                Level100Terrain.WalkerCenterOfGravityMillimeters +
                emitterVerticalOffset +
                projectile.VerticalVelocityMillimetersPerTick,
            projectile.ElevationMillimeters);

        int firstElevation = projectile.ElevationMillimeters;
        projectile = Assert.Single(simulation.Step(SimInput.Idle).Projectiles);
        Assert.Equal(
            firstElevation + projectile.VerticalVelocityMillimetersPerTick,
            projectile.ElevationMillimeters);
        for (int tick = 0; tick < SimulationConstants.ProjectileLifetimeTicks; tick++)
        {
            simulation.Step(SimInput.Idle);
        }

        Assert.Equal(
            SimulationConstants.Level100TargetTankLife,
            simulation.Snapshot.Targets.Single(item => item.Id == 1).Hull);
    }

    [Fact]
    public void Reset_RestoresDynamicStateWithoutRewindingReplayTick()
    {
        Simulation simulation = CreatePlayingSimulation(42);
        simulation.Step(new SimInput(1, 0));
        simulation.Step(new SimInput(0, 0, SimActions.ToggleMode));

        WorldSnapshot reset = simulation.Step(new SimInput(0, 0, SimActions.Reset));

        Assert.Equal(SimulationConstants.Level100OpeningPanTicks + 3, reset.Tick);
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
        Assert.False(state.Level100MissionEvents.GetType().IsArray);
        Assert.False(state.Level100TriggerActors.GetType().IsArray);

        var targets = Assert.IsAssignableFrom<IList<TargetSnapshot>>(state.Targets);
        var projectiles = Assert.IsAssignableFrom<IList<ProjectileSnapshot>>(state.Projectiles);
        Assert.True(targets.IsReadOnly);
        Assert.True(projectiles.IsReadOnly);
        Assert.Throws<NotSupportedException>(() => targets[0] = targets[0] with { Hull = 0 });
    }

    private static void DriveIntoTrigger(
        Simulation simulation,
        Level100MissionTrigger trigger)
    {
        Level100ActorScriptContinuationSnapshot pause =
            DriveUntilTriggerPause(simulation, trigger);
        int dueTick = Assert.IsType<int>(pause.DueTick);
        while (simulation.Snapshot.Tick < dueTick)
        {
            simulation.Step(SimInput.Idle);
        }

        Assert.True(Trigger(simulation, trigger).Reached);
    }

    private static Level100ActorScriptContinuationSnapshot DriveUntilTriggerPause(
        Simulation simulation,
        Level100MissionTrigger trigger)
    {
        Level100TriggerActorSnapshot releasedActor = Trigger(simulation, trigger);
        Assert.True(releasedActor.Active);
        SimVector2 destination = releasedActor.Position;
        for (int tick = 0; tick < 4_000; tick++)
        {
            WorldSnapshot state = simulation.Snapshot;
            Level100ActorSnapshot actor = state.Level100Actors.Actors.Single(
                item => item.Trigger == trigger);
            Level100ActorScriptContinuationSnapshot? pause = state.Level100ActorScripts.Instances
                .Single(item => item.ActorId == actor.ActorId)
                .Continuations
                .SingleOrDefault(item => item.WaitKind == Level100ActorScriptWaitKind.Pause);
            if (pause is not null)
            {
                return pause;
            }

            long deltaX = (long)destination.X - state.PlayerPosition.X;
            long deltaZ = (long)destination.Z - state.PlayerPosition.Z;
            double yaw = state.FacingYawMicroRad / 1_000_000d;
            double localX = (deltaX * Math.Cos(yaw)) + (deltaZ * Math.Sin(yaw));
            double localZ = (-deltaX * Math.Sin(yaw)) + (deltaZ * Math.Cos(yaw));
            sbyte moveX = (sbyte)Math.Sign(localX);
            sbyte moveZ = (sbyte)Math.Sign(localZ);
            simulation.Step(new SimInput(moveX, moveZ));
        }

        Level100ActorSnapshot stalledPlayer = simulation.Snapshot.Level100Actors.Actors.Single(
            actor => actor.Name == "Player 1");
        throw new Xunit.Sdk.XunitException(
            $"Did not start released trigger actor {trigger}; " +
            $"position={simulation.Snapshot.PlayerPosition}; " +
            $"playerActive={simulation.Snapshot.Level100PlayerActive}; " +
            $"controlEnabled={simulation.Snapshot.Level100PlayerControlEnabled}; " +
            $"navigation={simulation.Snapshot.Level100Mission.NavigationObjective}; " +
            $"playerScript={stalledPlayer.ScriptName}.");
    }

    private static Simulation CreatePlayingSimulation(uint seed = 1)
    {
        var simulation = new Simulation(
            seed,
            Level100TestActorDefinitions.Create(),
            CompletedTutorialSlots);
        for (int tick = 0; tick < SimulationConstants.Level100OpeningPanTicks; tick++)
        {
            simulation.Step(SimInput.Idle);
        }

        Assert.True(simulation.Snapshot.Level100PlayerControlEnabled);
        return simulation;
    }

    private static Simulation CreateFiringRangeExerciseSimulation()
    {
        Simulation simulation = CreatePlayingSimulation();
        AdvanceUntilNavigation(simulation, "Target Zone 1", 500);
        DriveIntoTrigger(simulation, Level100MissionTrigger.TargetZone1);
        AdvanceUntilNavigation(simulation, "Firing Range", 100);
        DriveIntoTrigger(simulation, Level100MissionTrigger.FiringRange);
        AdvanceUntil(simulation, state => state.Level100FiringRangeTargetsActive, 100);
        AdvanceUntil(simulation, state => state.Level100PulseCannonEnabled, 100);
        return simulation;
    }

    private static DeterministicSimulationTape RunLevel100FailureTape()
    {
        var simulation = new Simulation(
            0x100u,
            Level100TestActorDefinitions.Create());
        var hashes = new List<string> { StateHasher.ComputeHex(simulation.Snapshot) };
        WorldSnapshot snapshot = simulation.Step(
            SimInput.Idle,
            [new Level100MissionInputFact(Level100MissionInput.BrokeTutorial)]);
        hashes.Add(StateHasher.ComputeHex(snapshot));
        for (int tick = 0;
             tick < 500 && snapshot.Level100Mission.Outcome != Level100MissionOutcome.Lost;
             tick++)
        {
            snapshot = simulation.Step(SimInput.Idle);
            hashes.Add(StateHasher.ComputeHex(snapshot));
        }

        Assert.Equal(Level100MissionOutcome.Lost, snapshot.Level100Mission.Outcome);
        Assert.Equal(
            Level100MissionTiming.FailureCountdownTicks,
            snapshot.Level100Mission.TerminalTicksRemaining);
        for (int tick = 0; tick < Level100MissionTiming.FailureCountdownTicks; tick++)
        {
            snapshot = simulation.Step(SimInput.Idle);
            hashes.Add(StateHasher.ComputeHex(snapshot));
        }

        return new DeterministicSimulationTape(snapshot, hashes.AsReadOnly());
    }

    private static void AdvanceUntilNavigation(
        Simulation simulation,
        string thingName,
        int maximumTicks) => AdvanceUntil(
            simulation,
            state => string.Equals(
                state.Level100Mission.NavigationObjective,
                thingName,
                StringComparison.Ordinal),
            maximumTicks);

    private static void AdvanceUntil(
        Simulation simulation,
        Func<WorldSnapshot, bool> predicate,
        int maximumTicks,
        Action<WorldSnapshot>? observe = null)
    {
        for (int tick = 0; tick < maximumTicks && !predicate(simulation.Snapshot); tick++)
        {
            WorldSnapshot state = simulation.Step(SimInput.Idle);
            observe?.Invoke(state);
        }

        Assert.True(
            predicate(simulation.Snapshot),
            $"Condition was not reached by simulation tick {simulation.Snapshot.Tick}.");
    }

    private static Level100TriggerActorSnapshot Trigger(
        Simulation simulation,
        Level100MissionTrigger trigger) => Trigger(simulation.Snapshot, trigger);

    private static Level100TriggerActorSnapshot Trigger(
        WorldSnapshot snapshot,
        Level100MissionTrigger trigger) => snapshot.Level100TriggerActors
            .Single(item => item.Trigger == trigger);

    private sealed record DeterministicSimulationTape(
        WorldSnapshot Snapshot,
        IReadOnlyList<string> Hashes);

    private static void AimAtTarget(Simulation simulation, SimVector2 target)
    {
        for (int tick = 0; tick < 300; tick++)
        {
            WorldSnapshot state = simulation.Snapshot;
            double desired = Math.Atan2(
                -(target.X - state.PlayerPosition.X),
                target.Z - state.PlayerPosition.Z);
            double error = NormalizeRadians(desired - (state.FacingYawMicroRad / 1_000_000d));
            if (Math.Abs(error) < 0.04d)
            {
                return;
            }

            simulation.Step(new SimInput(0, 0, LookX: (sbyte)Math.Sign(error)));
        }

        throw new Xunit.Sdk.XunitException("Could not aim the deterministic Core at the requested target.");
    }

    private static void AimAtTargetAndSettle(Simulation simulation, SimVector2 target)
    {
        for (int tick = 0; tick < 1_200; tick++)
        {
            WorldSnapshot state = simulation.Snapshot;
            double desired = Math.Atan2(
                -(target.X - state.PlayerPosition.X),
                target.Z - state.PlayerPosition.Z);
            double error = NormalizeRadians(desired - (state.FacingYawMicroRad / 1_000_000d));
            if (Math.Abs(error) < 0.035d &&
                Math.Abs(state.WalkerYawVelocityMicroRadPerTick) < 7_000)
            {
                return;
            }

            double demand = error -
                ((state.WalkerYawVelocityMicroRadPerTick / 1_000_000d) * 5d);
            sbyte look = (sbyte)Math.Sign(demand);
            simulation.Step(new SimInput(0, 0, LookX: look));
        }

        WorldSnapshot final = simulation.Snapshot;
        double finalDesired = Math.Atan2(
            -(target.X - final.PlayerPosition.X),
            target.Z - final.PlayerPosition.Z);
        double finalError = NormalizeRadians(
            finalDesired - (final.FacingYawMicroRad / 1_000_000d));
        throw new Xunit.Sdk.XunitException(
            $"Could not settle the deterministic walker heading: error={finalError:F6}, " +
            $"velocity={final.WalkerYawVelocityMicroRadPerTick}.");
    }

    private static double NormalizeRadians(double value)
    {
        while (value > Math.PI) value -= Math.Tau;
        while (value <= -Math.PI) value += Math.Tau;
        return value;
    }

}
