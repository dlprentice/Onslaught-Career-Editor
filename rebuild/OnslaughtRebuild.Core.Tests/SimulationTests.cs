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

    [Fact]
    public void WalkerForward_AcceleratesToMeasuredCapAndCoastsAfterRelease()
    {
        var simulation = new Simulation(1);

        foreach (int expected in new[] { 33, 59, 79, 95, 100 })
        {
            WorldSnapshot state = simulation.Step(new SimInput(0, 1));
            Assert.Equal(new SimVector2(0, expected), state.PlayerVelocity);
        }

        foreach (int expected in new[] { 78, 61, 48, 37, 29 })
        {
            WorldSnapshot state = simulation.Step(SimInput.Idle);
            Assert.Equal(new SimVector2(0, expected), state.PlayerVelocity);
        }
    }

    [Fact]
    public void WalkerStrafe_UsesTheSameMeasuredResponseAsForward()
    {
        var simulation = new Simulation(1);

        foreach (int expected in new[] { 33, 59, 79, 95, 100 })
        {
            WorldSnapshot state = simulation.Step(new SimInput(1, 0));
            Assert.Equal(new SimVector2(expected, 0), state.PlayerVelocity);
        }
    }

    [Fact]
    public void WalkerLook_AcceleratesBodyYawAndCoastsAfterRelease()
    {
        var simulation = new Simulation(1);

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
    public void MovementUsesBodyHeadingWithoutResettingLookYaw()
    {
        var simulation = new Simulation(1);
        for (int tick = 0; tick < 20; tick++)
        {
            simulation.Step(new SimInput(0, 0, LookX: 1));
        }

        WorldSnapshot state = simulation.Step(new SimInput(0, 1));
        Assert.Equal(1, state.FacingX);
        Assert.Equal(0, state.FacingZ);
        Assert.True(state.PlayerPosition.X > 0);
        Assert.Equal(0, state.PlayerPosition.Z);
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
        var simulation = new Simulation(1);
        WorldSnapshot state = simulation.Step(new SimInput(0, 0, LookX: 1));
        Assert.Equal(0, state.FacingX);
        Assert.Equal(1, state.FacingZ);
        Assert.Equal(520_274, state.FacingYawMicroRad);
    }

    [Fact]
    public void LookX_Negative_TurnsLeftFromTheAuthoredStartYaw()
    {
        var simulation = new Simulation(1);
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
    public void ToggleMode_EntersMeasuredWalkerToJetTransitionBeforeCommittingJetMode()
    {
        var simulation = new Simulation(1);

        WorldSnapshot state = simulation.Step(new SimInput(0, 0, SimActions.ToggleMode));

        Assert.Equal(VehicleMode.Walker, state.Mode);
        Assert.Equal(VehicleTransition.WalkerToJet, state.Transition);
        Assert.Equal(0, state.Shield);
        Assert.Equal(
            SimulationConstants.MaximumEnergy -
                SimulationConstants.TransformEnergyCost -
                SimulationConstants.JetEnergyDrainPerTick,
            state.Energy);
        Assert.Equal(SimulationConstants.WalkerToJetTransitionTicks, state.TransformTicksRemaining);

        for (int interval = 1; interval < SimulationConstants.WalkerToJetTransitionTicks; interval++)
        {
            state = simulation.Step(new SimInput(
                0,
                0,
                interval == 1 ? SimActions.ToggleMode : SimActions.None));
            Assert.Equal(VehicleMode.Walker, state.Mode);
            Assert.Equal(VehicleTransition.WalkerToJet, state.Transition);
            Assert.Equal(SimulationConstants.WalkerToJetTransitionTicks - interval, state.TransformTicksRemaining);
        }

        state = simulation.Step(SimInput.Idle);
        Assert.Equal(VehicleMode.Jet, state.Mode);
        Assert.Equal(VehicleTransition.None, state.Transition);
        Assert.Equal(0, state.TransformTicksRemaining);
    }

    [Fact]
    public void FirstTickFire_ConsumesResourcesAndAdvancesTheSpawnedProjectile()
    {
        var simulation = new Simulation(1);

        WorldSnapshot state = simulation.Step(new SimInput(0, 0, SimActions.Fire));

        ProjectileSnapshot projectile = Assert.Single(state.Projectiles);
        Assert.Equal(new SimVector2(0, SimulationConstants.ProjectileSpeedPerTick), projectile.Position);
        Assert.Equal(SimulationConstants.ProjectileLifetimeTicks - 1, projectile.RemainingTicks);
        Assert.Equal(SimulationConstants.MaximumEnergy - SimulationConstants.FireEnergyCost, state.Energy);
        Assert.Equal(SimulationConstants.FireCooldownTicks, state.FireCooldownTicksRemaining);
    }

    [Fact]
    public void Reset_DominatesOtherActionsInTheSameInputSlot()
    {
        var simulation = new Simulation(1);
        simulation.Step(new SimInput(1, 0, SimActions.Fire));

        WorldSnapshot reset = simulation.Step(new SimInput(
            1,
            1,
            SimActions.Reset | SimActions.Fire | SimActions.ToggleMode));

        Assert.Equal(2, reset.Tick);
        Assert.Equal(VehicleMode.Walker, reset.Mode);
        Assert.Equal(SimVector2.Zero, reset.PlayerPosition);
        Assert.Equal(SimulationConstants.MaximumEnergy, reset.Energy);
        Assert.Equal(SimulationConstants.MaximumShield, reset.Shield);
        Assert.Empty(reset.Projectiles);
    }

    [Fact]
    public void Movement_IsNotClampedByTheRetiredSyntheticArena()
    {
        var simulation = new Simulation(1);

        for (int tick = 0; tick < 500; tick++)
        {
            simulation.Step(new SimInput(1, 1));
        }

        Assert.True(simulation.Snapshot.PlayerPosition.X > 30_000);
        Assert.True(simulation.Snapshot.PlayerPosition.Z > 30_000);
        Assert.NotEqual(SimVector2.Zero, simulation.Snapshot.PlayerVelocity);
    }

    [Fact]
    public void Level100Opening_AdvancesThroughAuthoredTriggersAfterScriptDelay()
    {
        var simulation = new Simulation(1);

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
    public void RepeatedFire_DestroysTheForwardTargetDeterministically()
    {
        var simulation = new Simulation(0xA917BEEFu);
        // Move toward the synthetic forward target under the measured walker cap.
        for (int tick = 0; tick < 70; tick++)
        {
            simulation.Step(new SimInput(0, 1));
        }

        for (int tick = 0; tick < 40; tick++)
        {
            simulation.Step(new SimInput(0, 0, SimActions.Fire));
        }

        Assert.Equal(1, simulation.Snapshot.TargetsDestroyed);
        Assert.False(simulation.Snapshot.Targets.Single(target => target.Id == 1).IsActive);
    }

    [Fact]
    public void Reset_RestoresDynamicStateWithoutRewindingReplayTick()
    {
        var simulation = new Simulation(42);
        simulation.Step(new SimInput(1, 0));
        simulation.Step(new SimInput(0, 0, SimActions.ToggleMode));

        WorldSnapshot reset = simulation.Step(new SimInput(0, 0, SimActions.Reset));

        Assert.Equal(3, reset.Tick);
        Assert.Equal(VehicleMode.Walker, reset.Mode);
        Assert.Equal(SimVector2.Zero, reset.PlayerPosition);
        Assert.Equal(SimulationConstants.MaximumEnergy, reset.Energy);
        Assert.Equal(SimulationConstants.MaximumShield, reset.Shield);
        Assert.Equal(0, reset.TargetsDestroyed);
        Assert.Empty(reset.Projectiles);
    }

    [Fact]
    public void StateHash_IncludesNextProjectileIdentityWhenNoProjectileIsActive()
    {
        var fired = new Simulation(1);
        var didNotFire = new Simulation(1);

        fired.Step(new SimInput(1, 0, SimActions.Fire));
        didNotFire.Step(new SimInput(1, 0));
        for (int tick = 1; tick < SimulationConstants.ProjectileLifetimeTicks; tick++)
        {
            fired.Step(SimInput.Idle);
            didNotFire.Step(SimInput.Idle);
        }

        Assert.Empty(fired.Snapshot.Projectiles);
        Assert.Empty(didNotFire.Snapshot.Projectiles);
        Assert.NotEqual(
            StateHasher.ComputeHex(fired.Snapshot),
            StateHasher.ComputeHex(didNotFire.Snapshot));

        WorldSnapshot firedAgain = fired.Step(new SimInput(0, 0, SimActions.Fire));
        WorldSnapshot firstFire = didNotFire.Step(new SimInput(0, 0, SimActions.Fire));
        Assert.NotEqual(firedAgain.Projectiles.Single().Id, firstFire.Projectiles.Single().Id);
    }

    [Fact]
    public void SnapshotCollections_DoNotExposeMutableArrays()
    {
        var simulation = new Simulation(1);
        WorldSnapshot state = simulation.Step(new SimInput(0, 0, SimActions.Fire));

        Assert.False(state.Targets.GetType().IsArray);
        Assert.False(state.Projectiles.GetType().IsArray);

        var targets = Assert.IsAssignableFrom<IList<TargetSnapshot>>(state.Targets);
        var projectiles = Assert.IsAssignableFrom<IList<ProjectileSnapshot>>(state.Projectiles);
        Assert.True(targets.IsReadOnly);
        Assert.True(projectiles.IsReadOnly);
        Assert.Throws<NotSupportedException>(() => targets[0] = targets[0] with { Hull = 0 });
        Assert.Throws<NotSupportedException>(() => projectiles[0] = projectiles[0] with { RemainingTicks = 0 });
    }

    [Fact]
    public void TransformPeriod_BlocksMovementAndFireUntilItCompletes()
    {
        var simulation = new Simulation(1);
        simulation.Step(new SimInput(0, 0, SimActions.ToggleMode));

        for (int tick = 1; tick < SimulationConstants.WalkerToJetTransitionTicks; tick++)
        {
            WorldSnapshot blocked = simulation.Step(new SimInput(1, 0, SimActions.Fire, LookX: 1));
            Assert.Equal(SimVector2.Zero, blocked.PlayerPosition);
            Assert.Equal(SimulationConstants.Level100PlayerStartYawMicroRad, blocked.FacingYawMicroRad);
            Assert.Equal(0, blocked.WalkerYawVelocityMicroRadPerTick);
            Assert.Empty(blocked.Projectiles);
        }

        WorldSnapshot active = simulation.Step(new SimInput(1, 0, SimActions.Fire, LookX: 1));
        Assert.NotEqual(SimVector2.Zero, active.PlayerPosition);
        Assert.NotEqual(0, active.FacingYawMicroRad);
        Assert.Single(active.Projectiles);
    }

    [Fact]
    public void EmptyJetEnergy_ForcesWalkerModeAndStartsTransformLock()
    {
        var simulation = new Simulation(1);
        simulation.Step(new SimInput(0, 0, SimActions.ToggleMode));

        for (int tick = 0; tick < SimulationConstants.WalkerToJetTransitionTicks; tick++)
        {
            simulation.Step(SimInput.Idle);
        }

        for (int tick = 0; tick < 1_000 && simulation.Snapshot.Mode == VehicleMode.Jet; tick++)
        {
            simulation.Step(SimInput.Idle);
        }

        Assert.Equal(VehicleMode.Walker, simulation.Snapshot.Mode);
        Assert.Equal(0, simulation.Snapshot.Energy);
        Assert.Equal(SimulationConstants.TransformDurationTicks, simulation.Snapshot.TransformTicksRemaining);
    }

    [Fact]
    public void FireCooldown_PreventsProjectileSpamWhileFireIsHeld()
    {
        var simulation = new Simulation(1);
        simulation.Step(new SimInput(1, 0, SimActions.Fire));

        for (int tick = 1; tick < SimulationConstants.FireCooldownTicks; tick++)
        {
            simulation.Step(new SimInput(0, 0, SimActions.Fire));
            Assert.Single(simulation.Snapshot.Projectiles);
        }

        simulation.Step(new SimInput(0, 0, SimActions.Fire));
        Assert.Equal(2, simulation.Snapshot.Projectiles.Count);
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
}
