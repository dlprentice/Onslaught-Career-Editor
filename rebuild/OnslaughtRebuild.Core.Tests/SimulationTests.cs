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
    public void WalkerLookYawRate_MatchesAcceptedTurnP02Translation()
    {
        // Dual-accept steady ≈ 0.090657 rad/s → round(ω * 1000 / 30) = 3.
        // Policy: walker-turn-yaw-retail-to-core-translation-policy.md
        Assert.Equal(3, SimulationConstants.WalkerLookYawRateMilliRadPerTick);
        const double measuredRadPerSec = 0.09065712988376617;
        int mapped = (int)Math.Round(measuredRadPerSec * 1000.0 / SimulationConstants.TicksPerSecond);
        Assert.Equal(SimulationConstants.WalkerLookYawRateMilliRadPerTick, mapped);
    }

    [Fact]
    public void LookX_IntegratesWalkerLookYawRateAndSnapsFacing()
    {
        var simulation = new Simulation(1);
        // Sector boundary ~785 milli-rad; rate is 3 mrad/tick → 262 ticks to sector 1.
        for (int tick = 0; tick < 262; tick++)
        {
            simulation.Step(new SimInput(0, 0, LookX: 1));
        }

        WorldSnapshot state = simulation.Snapshot;
        Assert.Equal(1, state.FacingX);
        Assert.Equal(1, state.FacingZ);
    }

    [Fact]
    public void MovementUsesBodyHeadingWithoutResettingLookYaw()
    {
        var simulation = new Simulation(1);
        for (int tick = 0; tick < 262; tick++)
        {
            simulation.Step(new SimInput(0, 0, LookX: 1));
        }

        WorldSnapshot state = simulation.Step(new SimInput(0, 1));
        Assert.Equal(1, state.FacingX);
        Assert.Equal(1, state.FacingZ);
        Assert.True(state.PlayerPosition.X > 0);
        Assert.True(state.PlayerPosition.Z > 0);
    }

    [Fact]
    public void LookX_OutsideUnitRange_IsRejected()
    {
        var input = new SimInput(0, 0, LookX: 2);
        Assert.Throws<ArgumentOutOfRangeException>(input.Validate);
    }

    [Fact]
    public void LookX_TakesPrecedenceOverMoveFacingSnap()
    {
        var simulation = new Simulation(1);
        // After enough Look ticks to leave sector 0, Move should not override while Look held.
        for (int tick = 0; tick < 262; tick++)
        {
            simulation.Step(new SimInput(1, 0, LookX: 1));
        }

        WorldSnapshot state = simulation.Snapshot;
        Assert.Equal(1, state.FacingX);
        Assert.Equal(1, state.FacingZ);
        // MoveX still applied velocity on X axis.
        Assert.True(state.PlayerPosition.X > 0);
    }

    [Fact]
    public void LookX_OneTick_DoesNotYetLeaveForwardFacing()
    {
        // Rate is 3 mrad/tick; sector width ~785 mrad → many ticks before snap.
        var simulation = new Simulation(1);
        WorldSnapshot state = simulation.Step(new SimInput(0, 0, LookX: 1));
        Assert.Equal(0, state.FacingX);
        Assert.Equal(1, state.FacingZ);
    }

    [Fact]
    public void LookX_Negative_SnapsFacingLeftCardinal()
    {
        var simulation = new Simulation(1);
        // 262 * (-3 mrad) ≈ −786 mrad → eight-way sector 6 → (−1, 0).
        for (int tick = 0; tick < 262; tick++)
        {
            simulation.Step(new SimInput(0, 0, LookX: -1));
        }

        WorldSnapshot state = simulation.Snapshot;
        Assert.Equal(-1, state.FacingX);
        Assert.Equal(0, state.FacingZ);
    }

    [Fact]
    public void WalkerStrafeSpeed_MatchesAcceptedStrafeP02Translation()
    {
        // Dual-accept steady ≈ 3.015 u/s → round(v * 1000 / 30) = 101.
        Assert.Equal(101, SimulationConstants.WalkerStrafeSpeedPerTick);
        const double measured = 3.015197590944186;
        int mapped = (int)Math.Round(measured * 1000.0 / SimulationConstants.TicksPerSecond);
        Assert.Equal(SimulationConstants.WalkerStrafeSpeedPerTick, mapped);
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
    public void ToggleMode_UsesEnergyAndDisablesJetShield()
    {
        var simulation = new Simulation(1);

        WorldSnapshot state = simulation.Step(new SimInput(0, 0, SimActions.ToggleMode));

        Assert.Equal(VehicleMode.Jet, state.Mode);
        Assert.Equal(0, state.Shield);
        Assert.Equal(
            SimulationConstants.MaximumEnergy -
                SimulationConstants.TransformEnergyCost -
                SimulationConstants.JetEnergyDrainPerTick,
            state.Energy);
        Assert.Equal(SimulationConstants.TransformDurationTicks, state.TransformTicksRemaining);
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
    public void Movement_ClampsPlayerToArena()
    {
        var simulation = new Simulation(1);

        for (int tick = 0; tick < 500; tick++)
        {
            simulation.Step(new SimInput(1, 1));
        }

        Assert.Equal(SimulationConstants.ArenaHalfExtent, simulation.Snapshot.PlayerPosition.X);
        Assert.Equal(SimulationConstants.ArenaHalfExtent, simulation.Snapshot.PlayerPosition.Z);
        Assert.Equal(SimVector2.Zero, simulation.Snapshot.PlayerVelocity);
    }

    [Fact]
    public void RepeatedFire_DestroysTheForwardTargetDeterministically()
    {
        var simulation = new Simulation(0xA917BEEFu);
        // Close to the forward target at z=14000 under WalkerSpeedPerTick=100
        // (retail-informed milli-unit mapping; formerly 20 ticks at 350).
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

        for (int tick = 1; tick < SimulationConstants.TransformDurationTicks; tick++)
        {
            WorldSnapshot blocked = simulation.Step(new SimInput(1, 0, SimActions.Fire));
            Assert.Equal(SimVector2.Zero, blocked.PlayerPosition);
            Assert.Empty(blocked.Projectiles);
        }

        WorldSnapshot active = simulation.Step(new SimInput(1, 0, SimActions.Fire));
        Assert.NotEqual(SimVector2.Zero, active.PlayerPosition);
        Assert.Single(active.Projectiles);
    }

    [Fact]
    public void EmptyJetEnergy_ForcesWalkerModeAndStartsTransformLock()
    {
        var simulation = new Simulation(1);
        simulation.Step(new SimInput(0, 0, SimActions.ToggleMode));

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
}
