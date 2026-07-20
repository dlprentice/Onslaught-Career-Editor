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
    public void Level100Terrain_ExposesReleasedWaterSelection()
    {
        Assert.Equal(
            unchecked((int)0xC10D70A4),
            BitConverter.SingleToInt32Bits(Level100Terrain.Instance.WaterLevel));
        Assert.Equal(0, Level100Terrain.Instance.WaterTexture);
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
        Assert.False(simulation.Snapshot.Level100PulseCannonEnabled);
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
    public void LookAxes_OutsideUnitRange_AreRejected()
    {
        Assert.Throws<ArgumentOutOfRangeException>(
            new SimInput(0, 0, LookX: 2).Validate);
        Assert.Throws<ArgumentOutOfRangeException>(
            new SimInput(0, 0, LookY: -2).Validate);
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
            SimulationConstants.Level100TargetZone1DispatchTicks,
            simulation.Snapshot.Level100DispatchTicksRemaining);

        for (int tick = 1; tick < SimulationConstants.Level100TargetZone1DispatchTicks; tick++)
        {
            WorldSnapshot pending = simulation.Step(SimInput.Idle);
            Assert.Equal(Level100OpeningPhase.TargetZone1DispatchPending, pending.Level100Phase);
        }

        WorldSnapshot firingRangeAssignment = simulation.Step(SimInput.Idle);
        Assert.Equal(Level100OpeningPhase.ReachFiringRange, firingRangeAssignment.Level100Phase);
        Assert.Equal(
            Level100TutorialMessage.FiringRangeInstruction,
            firingRangeAssignment.Level100Message);
        Assert.Equal(
            SimulationConstants.Level100FiringRangeInstructionTicks,
            firingRangeAssignment.Level100EventMessageTicksRemaining);

        for (int tick = 1; tick < SimulationConstants.Level100FiringRangeInstructionTicks; tick++)
        {
            WorldSnapshot instruction = simulation.Step(SimInput.Idle);
            Assert.Equal(Level100TutorialMessage.FiringRangeInstruction, instruction.Level100Message);
        }

        Assert.Equal(Level100TutorialMessage.None, simulation.Step(SimInput.Idle).Level100Message);

        DriveToPhase(
            simulation,
            SimulationConstants.Level100FiringRangePosition,
            Level100OpeningPhase.FiringRangeDispatchPending);
        for (int tick = 0; tick < SimulationConstants.Level100FiringRangeDispatchTicks; tick++)
        {
            simulation.Step(SimInput.Idle);
        }

        Assert.Equal(Level100OpeningPhase.FiringRangeBriefing, simulation.Snapshot.Level100Phase);
        Assert.Equal(0, simulation.Snapshot.Level100FiringRangeSequenceTick);
        Assert.Equal(Level100TutorialMessage.WeaponSystems, simulation.Snapshot.Level100Message);
        Assert.False(simulation.Snapshot.Level100PlayerControlEnabled);
        Assert.False(simulation.Snapshot.Level100PulseCannonEnabled);
        Assert.False(simulation.Snapshot.Level100FiringRangeTargetsActive);
        Assert.Equal(
            [
                SimulationConstants.Level100TargetTank1Position,
                SimulationConstants.Level100TargetTank2Position,
                SimulationConstants.Level100TargetTank3Position,
                SimulationConstants.Level100TargetWarehousePosition,
            ],
            simulation.Snapshot.Targets.Select(target => target.Position));

        StepUntilFiringRangeSequenceTick(
            simulation,
            SimulationConstants.Level100WeaponIndicatorStartTick);
        Assert.Equal(Level100TutorialMessage.WeaponIndicator, simulation.Snapshot.Level100Message);
        Assert.True(simulation.Snapshot.Level100CurrentWeaponHighlighted);

        StepUntilFiringRangeSequenceTick(
            simulation,
            SimulationConstants.Level100PulseCannonStartTick);
        Assert.Equal(Level100TutorialMessage.PulseCannon, simulation.Snapshot.Level100Message);
        Assert.False(simulation.Snapshot.Level100CurrentWeaponHighlighted);

        StepUntilFiringRangeSequenceTick(
            simulation,
            SimulationConstants.Level100StaticTargetsActivationTick);
        Assert.Equal(Level100TutorialMessage.OpenFire, simulation.Snapshot.Level100Message);
        Assert.True(simulation.Snapshot.Level100FiringRangeTargetsActive);
        Assert.False(simulation.Snapshot.Level100PulseCannonEnabled);
        Assert.Empty(simulation.Step(new SimInput(0, 0, SimActions.Fire)).Projectiles);

        StepUntilFiringRangeSequenceTick(
            simulation,
            SimulationConstants.Level100PulseCannonActivationTick);
        Assert.Equal(Level100OpeningPhase.FiringRangeExercise, simulation.Snapshot.Level100Phase);
        Assert.True(simulation.Snapshot.Level100PlayerControlEnabled);
        Assert.True(simulation.Snapshot.Level100PulseCannonEnabled);
        Assert.Single(simulation.Step(new SimInput(0, 0, SimActions.Fire)).Projectiles);

        StepUntilFiringRangeSequenceTick(
            simulation,
            SimulationConstants.Level100FireHelpActivationTick);
        Assert.True(simulation.Snapshot.Level100FireHelpVisible);
        StepUntilFiringRangeSequenceTick(
            simulation,
            SimulationConstants.Level100PulseCannonEnergyStartTick);
        Assert.Equal(Level100TutorialMessage.PulseCannonEnergy, simulation.Snapshot.Level100Message);
    }

    [Fact]
    public void Level100FirstFiringRange_DestroysFourTargetsAndHandsOffToVulcan()
    {
        Simulation simulation = CreateFiringRangeExerciseSimulation();
        foreach (int targetId in new[] { 1, 2, 3 })
        {
            TargetSnapshot target = simulation.Snapshot.Targets.Single(item => item.Id == targetId);
            Assert.Equal(SimulationConstants.Level100TargetTankLife, target.Hull);

            foreach (int expected in new[] { 4_200, 2_400, 600, 0 })
            {
                AimAtTarget(simulation, target.Position);
                WorldSnapshot fired = simulation.Step(new SimInput(0, 0, SimActions.Fire));
                ProjectileSnapshot projectile = Assert.Single(fired.Projectiles);
                long speedSquared =
                    ((long)projectile.Velocity.X * projectile.Velocity.X) +
                    ((long)projectile.Velocity.Z * projectile.Velocity.Z);
                Assert.InRange(
                    speedSquared,
                    (long)1_166 * 1_166,
                    (long)1_168 * 1_168);

                for (int tick = 0; tick < 40; tick++)
                {
                    WorldSnapshot state = simulation.Step(SimInput.Idle);
                    target = state.Targets.Single(item => item.Id == targetId);
                    if (target.Hull == expected)
                    {
                        break;
                    }
                }

                Assert.Equal(expected, target.Hull);
            }

            Assert.False(target.IsActive);
        }

        Assert.Equal(3, simulation.Snapshot.TargetsDestroyed);
        TargetSnapshot warehouse = simulation.Snapshot.Targets.Single(item => item.Id == 4);
        Assert.True(warehouse.IsActive);
        Assert.Equal(
            SimulationConstants.Level100TargetWarehouseCenterAimDamageEnvelope,
            warehouse.Hull);

        for (int hit = 1; hit <= 12; hit++)
        {
            int expected =
                SimulationConstants.Level100TargetWarehouseCenterAimDamageEnvelope -
                (hit * SimulationConstants.Level100PulseCannonFullHitDamage);
            AimAtTarget(simulation, warehouse.Position);
            Assert.Single(simulation.Step(new SimInput(0, 0, SimActions.Fire)).Projectiles);
            for (int tick = 0; tick < SimulationConstants.ProjectileLifetimeTicks; tick++)
            {
                WorldSnapshot state = simulation.Step(SimInput.Idle);
                warehouse = state.Targets.Single(item => item.Id == 4);
                if (warehouse.Hull == expected)
                {
                    break;
                }
            }

            Assert.Equal(expected, warehouse.Hull);
        }

        Assert.False(warehouse.IsActive);
        Assert.Equal(4, simulation.Snapshot.TargetsDestroyed);
        Assert.False(simulation.Snapshot.Level100FiringRangeTargetsActive);
        Assert.Equal(
            Level100OpeningPhase.FiringRangeVulcanBriefing,
            simulation.Snapshot.Level100Phase);
        Assert.Equal(0, simulation.Snapshot.Level100FiringRangeHandoffTick);
        Assert.False(simulation.Snapshot.Level100PlayerControlEnabled);
        Assert.True(simulation.Snapshot.Level100PulseCannonEnabled);
        Assert.False(simulation.Snapshot.Level100VulcanCannonEnabled);
        Assert.Empty(simulation.Step(new SimInput(0, 0, SimActions.Fire)).Projectiles);

        StepUntilFiringRangeHandoffTick(
            simulation,
            SimulationConstants.Level100VulcanCannonStartTick);
        Assert.Equal(Level100TutorialMessage.VulcanCannon, simulation.Snapshot.Level100Message);
        Assert.False(simulation.Snapshot.Level100PlayerControlEnabled);

        StepUntilFiringRangeHandoffTick(
            simulation,
            SimulationConstants.Level100VulcanActivationTick);
        Assert.Equal(
            Level100OpeningPhase.FiringRangeVulcanExercise,
            simulation.Snapshot.Level100Phase);
        Assert.Equal(
            Level100TutorialMessage.OpenFireVulcan,
            simulation.Snapshot.Level100Message);
        Assert.True(simulation.Snapshot.Level100PlayerControlEnabled);
        Assert.False(simulation.Snapshot.Level100PulseCannonEnabled);
        Assert.True(simulation.Snapshot.Level100VulcanCannonEnabled);

        StepUntilFiringRangeHandoffTick(
            simulation,
            SimulationConstants.Level100VulcanCannonAmmoStartTick);
        Assert.Equal(
            Level100TutorialMessage.VulcanCannonAmmo,
            simulation.Snapshot.Level100Message);
        StepUntilFiringRangeHandoffTick(
            simulation,
            SimulationConstants.Level100VulcanCannonAmmoEndTick);
        Assert.Equal(Level100TutorialMessage.None, simulation.Snapshot.Level100Message);
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

    private static Simulation CreateFiringRangeExerciseSimulation()
    {
        Simulation simulation = CreatePlayingSimulation();
        DriveToPhase(
            simulation,
            SimulationConstants.Level100TargetZone1Position,
            Level100OpeningPhase.TargetZone1DispatchPending);
        for (int tick = 0; tick < SimulationConstants.Level100TargetZone1DispatchTicks; tick++)
        {
            simulation.Step(SimInput.Idle);
        }

        DriveToPhase(
            simulation,
            SimulationConstants.Level100FiringRangePosition,
            Level100OpeningPhase.FiringRangeDispatchPending);
        for (int tick = 0; tick < SimulationConstants.Level100FiringRangeDispatchTicks; tick++)
        {
            simulation.Step(SimInput.Idle);
        }
        StepUntilFiringRangeSequenceTick(
            simulation,
            SimulationConstants.Level100PulseCannonActivationTick);
        Assert.Equal(Level100OpeningPhase.FiringRangeExercise, simulation.Snapshot.Level100Phase);
        return simulation;
    }

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

    private static void StepUntilFiringRangeSequenceTick(Simulation simulation, int sequenceTick)
    {
        while (simulation.Snapshot.Level100FiringRangeSequenceTick < sequenceTick)
        {
            simulation.Step(SimInput.Idle);
        }
        Assert.Equal(sequenceTick, simulation.Snapshot.Level100FiringRangeSequenceTick);
    }

    private static void StepUntilFiringRangeHandoffTick(
        Simulation simulation,
        int handoffTick)
    {
        while (simulation.Snapshot.Level100FiringRangeHandoffTick < handoffTick)
        {
            simulation.Step(SimInput.Idle);
        }
        Assert.Equal(handoffTick, simulation.Snapshot.Level100FiringRangeHandoffTick);
    }
}
