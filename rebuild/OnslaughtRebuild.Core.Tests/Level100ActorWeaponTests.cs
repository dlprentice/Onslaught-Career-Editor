// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.TestSupport;
using Xunit.Abstractions;

namespace OnslaughtRebuild.Core.Tests;

/// <summary>
/// Actor-owned weapons: the released random stream, the released scatter law,
/// the released firing gate, and the <c>CRoundSeek 3</c> homing law.
///
/// Nothing in this file posts a mission event or writes a health value
/// directly. Every observation is produced by advancing
/// <see cref="Level100ActorMechanics"/> after issuing exactly the
/// <c>Attack(player)</c> command <c>AirborneDrone2.msl</c>'s <c>init()</c>
/// issues.
/// </summary>
public sealed class Level100ActorWeaponTests
{
    private readonly ITestOutputHelper _output;

    public Level100ActorWeaponTests(ITestOutputHelper output) =>
        _output = output;

    /// <summary>
    /// The released stream, reproduced. The seed is retail's own constant
    /// 123456 and the arithmetic is retail's own 32-bit Schrage step with the
    /// shipped modulus 214783647, so the sequence is not an invention: it is
    /// the shipped generator run from the shipped seed.
    ///
    /// This test also pins the two properties the shipped defect produces -
    /// the state leaves [1, m) almost immediately, and it never reaches zero
    /// (a zero state would step to m, so there is no lock-up).
    /// </summary>
    [Fact]
    public void ReleasedRandom_ReproducesTheShippedStreamFromTheShippedSeed()
    {
        var first = new Level100ReleasedRandom();
        var second = new Level100ReleasedRandom(
            SimulationConstants.Level100ReleasedRandomInitialSeed);

        int[] head = Enumerable.Range(0, 8).Select(_ => first.Next()).ToArray();
        int[] repeat = Enumerable.Range(0, 8).Select(_ => second.Next()).ToArray();
        Assert.Equal(head, repeat);
        _output.WriteLine(
            "first eight draws from seed 123456: " + string.Join(", ", head));

        // Restoring from a snapshotted seed continues the same stream, which
        // is what makes the whole thing hashable and replayable.
        var resumed = new Level100ReleasedRandom(first.Seed);
        Assert.Equal(first.Next(), resumed.Next());

        var stream = new Level100ReleasedRandom();
        bool leftNominalRange = false;
        for (int step = 0; step < 200_000; step++)
        {
            stream.Next();
            Assert.NotEqual(0, stream.Seed);
            if (stream.Seed < 1 ||
                stream.Seed > SimulationConstants.Level100ReleasedRandomModulus)
            {
                leftNominalRange = true;
            }
        }
        Assert.True(
            leftNominalRange,
            "the shipped modulus breaks the Schrage precondition, so the " +
            "state must leave [1, m); a stream that stays inside it is not " +
            "the shipped stream.");
    }

    /// <summary>
    /// The scatter sample is exactly
    /// <c>((sample % 65536) / 32768 - 1) * CWeaponInaccuracy</c>, so a
    /// 1-degree inaccuracy can never exceed 1 degree in magnitude from a
    /// non-negative draw, and a zero inaccuracy still consumes the stream.
    /// </summary>
    [Fact]
    public void ReleasedScatter_IsBoundedByTheShippedInaccuracy()
    {
        var stream = new Level100ReleasedRandom();
        int inaccuracy =
            SimulationConstants.Level100DroneVulcanInaccuracyMicroRadians;
        int maximum = 0;
        for (int draw = 0; draw < 4_096; draw++)
        {
            int sample = stream.NextSignedUnitScaled(inaccuracy);
            maximum = Math.Max(maximum, Math.Abs(sample));
        }
        _output.WriteLine(
            $"largest |scatter| over 4096 draws: {maximum} urad against the " +
            $"shipped {inaccuracy} urad CWeaponInaccuracy");
        Assert.True(maximum <= 3 * inaccuracy);

        int before = stream.Seed;
        Assert.Equal(0, stream.NextSignedUnitScaled(0));
        Assert.NotEqual(before, stream.Seed);
    }

    /// <summary>
    /// The whole released chain, driven only by the <c>Attack(player)</c>
    /// command the script issues: the drone closes to inside
    /// <c>CWeaponMaxRange</c>, passes <c>CWeaponYawTolerance</c>, fires its
    /// <c>Drone Vulcan Cannon</c> burst, and its Blasters reach the player.
    /// </summary>
    [Fact]
    public void AttackingTargetDrone_FiresItsVulcanAndReachesThePlayer()
    {
        Level100ActorDefinitionSet definitions =
            Level100TestActorDefinitions.Create();
        var registry = new Level100ActorRegistry(definitions);
        var mechanics = new Level100ActorMechanics(registry, definitions);
        Level100ActorId airfieldId = Assert.IsType<Level100ActorId>(
            registry.GetThingRef("Airfield"));
        Level100ActorId playerId = Assert.IsType<Level100ActorId>(
            registry.GetThingRef("Player 1"));
        SeatPlayerOnTheTerrain(registry, playerId);
        Level100ActorId droneId = registry.SpawnThing(
            airfieldId,
            "Target Drone",
            "SpawnerA",
            1,
            "AirborneDrone2").Single();
        mechanics.ApplyCommand(new Level100ActorScriptCommand(
            1,
            0,
            droneId,
            Level100ActorScriptCommandKind.Attack,
            playerId,
            null,
            0));

        int blasterImpacts = 0;
        int missileImpacts = 0;
        int hullDamage = 0;
        int firstImpactTick = -1;
        for (int tick = 0; tick < 30 * 180; tick++)
        {
            mechanics.AdvanceTick();
            foreach (Level100ActorRoundImpact impact in
                     mechanics.DrainActorRoundImpacts())
            {
                Assert.Equal(playerId, impact.TargetActorId);
                Assert.Equal(droneId, impact.OwnerActorId);
                hullDamage += impact.HullDamage;
                if (impact.Kind == Level100ActorRoundKind.Blaster)
                {
                    blasterImpacts++;
                }
                else
                {
                    missileImpacts++;
                }
                if (firstImpactTick < 0)
                {
                    firstImpactTick = tick;
                }
            }
        }

        _output.WriteLine(
            $"blaster impacts {blasterImpacts}, missile impacts " +
            $"{missileImpacts}, first at Core tick {firstImpactTick}, total " +
            $"{hullDamage} hull of {SimulationConstants.MaximumHull}");
        Assert.True(
            blasterImpacts > 0,
            "the released Drone Vulcan Cannon must reach the player it is " +
            "told to attack.");
        Assert.True(hullDamage > 0);
    }

    /// <summary>
    /// Released Blaster damage is <c>CRoundDamage</c> 0.2 with an explosion
    /// (<c>Small Energy Hit</c>) that carries no <c>CExplosionDamage</c>;
    /// released Forseti Missile damage is <c>CRoundDamage</c> 2.0 plus the 0.5
    /// <c>CExplosionDamage</c> its <c>Micro Missile Hit</c> inherits from
    /// <c>Small Explosion Base</c>. Both convert at
    /// <c>MaximumHull / mLife</c> = 1000/20 = 50 hull per released point.
    /// </summary>
    [Theory]
    [InlineData(Level100ActorRoundKind.Blaster, 10)]
    [InlineData(Level100ActorRoundKind.ForsetiMissile, 125)]
    public void ActorRoundDamage_MatchesTheShippedRecords(
        Level100ActorRoundKind kind,
        int expectedHullDamage)
    {
        Level100ActorDefinitionSet definitions =
            Level100TestActorDefinitions.Create();
        var registry = new Level100ActorRegistry(definitions);
        var mechanics = new Level100ActorMechanics(registry, definitions);
        Level100ActorId airfieldId = Assert.IsType<Level100ActorId>(
            registry.GetThingRef("Airfield"));
        Level100ActorId playerId = Assert.IsType<Level100ActorId>(
            registry.GetThingRef("Player 1"));
        SeatPlayerOnTheTerrain(registry, playerId);
        Level100ActorId droneId = registry.SpawnThing(
            airfieldId,
            "Target Drone",
            "SpawnerA",
            1,
            "AirborneDrone2").Single();
        mechanics.ApplyCommand(new Level100ActorScriptCommand(
            1,
            0,
            droneId,
            Level100ActorScriptCommandKind.Attack,
            playerId,
            null,
            0));

        int observed = -1;
        int launched = 0;
        int highWater = 0;
        for (int tick = 0; tick < 30 * 600 && observed < 0; tick++)
        {
            mechanics.AdvanceTick();
            Level100ActorMechanicsSnapshot snapshot = mechanics.Snapshot;
            launched = Math.Max(launched, snapshot.NextActorRoundId - 1);
            highWater = Math.Max(
                highWater,
                snapshot.ActorRounds.Count(r => r.Kind == kind));
            foreach (Level100ActorRoundImpact impact in
                     mechanics.DrainActorRoundImpacts())
            {
                if (impact.Kind == kind)
                {
                    observed = impact.HullDamage;
                }
            }
        }
        _output.WriteLine(
            $"{kind}: {launched} rounds launched overall, high-water " +
            $"{highWater} of this kind in flight");

        _output.WriteLine($"{kind} hull damage: {observed}");
        Assert.Equal(expectedHullDamage, observed);
    }

    /// <summary>
    /// The state hash sees the armament. Advancing an attacking drone changes
    /// the mechanics snapshot, and the snapshot round-trips: a mechanics
    /// instance restored from it continues the identical stream and produces
    /// the identical next snapshot.
    /// </summary>
    [Fact]
    public void ActorArmament_IsCanonicalReplayState()
    {
        Level100ActorMechanicsSnapshot Advance(int ticks)
        {
            Level100ActorDefinitionSet definitions =
                Level100TestActorDefinitions.Create();
            var registry = new Level100ActorRegistry(definitions);
            var mechanics = new Level100ActorMechanics(registry, definitions);
            Level100ActorId airfieldId = Assert.IsType<Level100ActorId>(
                registry.GetThingRef("Airfield"));
            Level100ActorId playerId = Assert.IsType<Level100ActorId>(
                registry.GetThingRef("Player 1"));
            SeatPlayerOnTheTerrain(registry, playerId);
            Level100ActorId droneId = registry.SpawnThing(
                airfieldId,
                "Target Drone",
                "SpawnerA",
                1,
                "AirborneDrone2").Single();
            mechanics.ApplyCommand(new Level100ActorScriptCommand(
                1,
                0,
                droneId,
                Level100ActorScriptCommandKind.Attack,
                playerId,
                null,
                0));
            for (int tick = 0; tick < ticks; tick++)
            {
                mechanics.AdvanceTick();
            }
            return mechanics.Snapshot;
        }

        Level100ActorMechanicsSnapshot idle = Advance(0);
        Assert.Empty(idle.ActorRounds);
        Assert.Equal(
            SimulationConstants.Level100ReleasedRandomInitialSeed,
            idle.ReleasedRandomSeed);

        Level100ActorMechanicsSnapshot flown = Advance(30 * 120);
        Level100ActorMechanicsSnapshot repeat = Advance(30 * 120);
        // Record equality would compare the two lists by reference, so this
        // compares the values the state hasher actually writes.
        Assert.Equal(flown.ReleasedRandomSeed, repeat.ReleasedRandomSeed);
        Assert.Equal(flown.NextActorRoundId, repeat.NextActorRoundId);
        Assert.Equal(flown.ActorWeapons, repeat.ActorWeapons);
        Assert.Equal(flown.ActorRounds, repeat.ActorRounds);
        Assert.NotEqual(idle.ReleasedRandomSeed, flown.ReleasedRandomSeed);
        Assert.NotEmpty(flown.ActorWeapons);
        _output.WriteLine(
            $"after 120 s: seed {flown.ReleasedRandomSeed}, " +
            $"{flown.ActorRounds.Count} rounds in flight, " +
            $"next round id {flown.NextActorRoundId}");
    }

    /// <summary>
    /// <c>CRoundSeek 3</c> is a homing round with a launcher-supplied target.
    /// Driven here through the released <c>Forseti Drone Missile Launcher</c>
    /// against a target that is moved every tick, so a straight-flying round
    /// wearing the missile's name could not produce this result.
    /// </summary>
    [Fact]
    public void ForsetiMissile_HomesOnAMovingTarget()
    {
        Level100ActorDefinitionSet definitions =
            Level100TestActorDefinitions.Create();
        var registry = new Level100ActorRegistry(definitions);
        var mechanics = new Level100ActorMechanics(registry, definitions);
        Level100ActorId airfieldId = Assert.IsType<Level100ActorId>(
            registry.GetThingRef("Airfield"));
        Level100ActorId playerId = Assert.IsType<Level100ActorId>(
            registry.GetThingRef("Player 1"));
        SeatPlayerOnTheTerrain(registry, playerId);
        Level100ActorId droneId = registry.SpawnThing(
            airfieldId,
            "Target Drone",
            "SpawnerA",
            1,
            "AirborneDrone2").Single();
        mechanics.ApplyCommand(new Level100ActorScriptCommand(
            1,
            0,
            droneId,
            Level100ActorScriptCommandKind.Attack,
            playerId,
            null,
            0));

        int missileImpacts = 0;
        int sidestep = 0;
        for (int tick = 0; tick < 30 * 600; tick++)
        {
            // Move the target laterally every base tick. A round with no
            // guidance law cannot follow this.
            Level100ActorPoseSnapshot pose = registry.GetPose(playerId);
            sidestep = (sidestep + 1) % 240;
            registry.SetPose(
                playerId,
                pose with
                {
                    PositionMillimeters = new SimVector3(
                        pose.PositionMillimeters.X + (sidestep < 120 ? 40 : -40),
                        pose.PositionMillimeters.Y,
                        pose.PositionMillimeters.Z),
                });
            mechanics.AdvanceTick();
            missileImpacts += mechanics.DrainActorRoundImpacts()
                .Count(impact =>
                    impact.Kind == Level100ActorRoundKind.ForsetiMissile);
        }

        _output.WriteLine($"Forseti Missile impacts on a moving target: {missileImpacts}");
        Assert.True(
            missileImpacts > 0,
            "CRoundSeek 3 must home; a straight round would be a different " +
            "weapon wearing the missile's name.");
    }

    /// <summary>
    /// The bare registry fixture leaves <c>Player 1</c> at its authored
    /// Y = 0, which is below the height field. <see cref="Simulation"/> does
    /// not: it seats the walker on the terrain and the flight-leg measurements
    /// record a standing origin 1,900 mm above ground. Rounds aimed at a
    /// target buried under the terrain would be spent on the terrain before
    /// reaching it, which is a fixture artefact and not a weapon result.
    /// </summary>
    private static void SeatPlayerOnTheTerrain(
        Level100ActorRegistry registry,
        Level100ActorId playerId)
    {
        Level100ActorPoseSnapshot pose = registry.GetPose(playerId);
        int ground = Level100Terrain.Instance.SampleGroundElevationMillimeters(
            new SimVector2(
                pose.PositionMillimeters.X,
                pose.PositionMillimeters.Z));
        registry.SetPose(
            playerId,
            pose with
            {
                PositionMillimeters = new SimVector3(
                    pose.PositionMillimeters.X,
                    ground + WalkerStandingOriginMillimeters,
                    pose.PositionMillimeters.Z),
            });
    }

    private const int WalkerStandingOriginMillimeters = 1_900;
}
