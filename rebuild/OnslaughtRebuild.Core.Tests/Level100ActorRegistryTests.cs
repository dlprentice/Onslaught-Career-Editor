// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.TestSupport;

namespace OnslaughtRebuild.Core.Tests;

public sealed class Level100ActorRegistryTests
{
    [Fact]
    public void ReleasedRegistry_ResolvesStableActorsAndRoundTripsAllMutableState()
    {
        Level100ActorDefinitionSet definitions = Level100TestActorDefinitions.Create();
        var registry = new Level100ActorRegistry(definitions);
        Level100ActorId tankFactory = Assert.IsType<Level100ActorId>(
            registry.GetThingRef("Tank Factory"));
        Level100ActorId airfield = Assert.IsType<Level100ActorId>(
            registry.GetThingRef("Airfield"));
        Level100ActorId targetZone1 = Assert.IsType<Level100ActorId>(
            registry.GetThingRef("Target Zone 1"));

        Assert.Equal(2, tankFactory.Value);
        Assert.Equal(10, airfield.Value);
        Assert.Equal(12, targetZone1.Value);
        Assert.Null(registry.GetThingRef("Not In Level 100"));

        Level100ActorId trainer = Assert.Single(registry.SpawnThing(
            airfield,
            "Air Trainer",
            "SpawnerB",
            1,
            "AirTrainer"));
        var pose = new Level100ActorPoseSnapshot(
            new SimVector3(1, 2, 3),
            new Level100FloatBasis3Bits(
                BitConverter.SingleToInt32Bits(1f), 0, 0,
                0, BitConverter.SingleToInt32Bits(1f), 0,
                0, 0, BitConverter.SingleToInt32Bits(1f)),
            new SimVector3(7, 8, 9),
            new SimVector3(10, 11, 12));
        registry.SetPose(trainer, pose);
        registry.SetHealth(trainer, 321);
        registry.Deactivate(trainer);
        registry.SetObjective(trainer, true);
        registry.ReportHit(trainer, tankFactory);
        Assert.True(registry.ReportStartedDying(trainer));
        Assert.True(registry.ReportDied(trainer));
        Assert.False(registry.ReportDied(trainer));

        Level100ActorRegistrySnapshot snapshot = registry.Snapshot;
        Level100ActorSnapshot actor = snapshot.Actors.Single(item => item.ActorId == trainer);
        Assert.Equal(definitions.IdentitySha256, snapshot.DefinitionSetIdentitySha256);
        Assert.Equal(definitions.Actors.Count + 1, trainer.Value);
        Assert.Equal("Air Trainer", actor.DefinitionName);
        Assert.Equal("AirTrainer", actor.ScriptName);
        Assert.Equal(airfield, actor.SpawnOwnerId);
        Assert.Equal("SpawnerB", actor.SpawnerName);
        Assert.Equal(pose, actor.Pose);
        Assert.Equal(321, actor.Health);
        Assert.Equal(Level100ActorLifecycle.Destroyed, actor.Lifecycle);
        Assert.False(actor.Active);
        Assert.False(actor.IsObjective);
        Assert.Throws<InvalidOperationException>(() => registry.Activate(trainer));
        Assert.Throws<InvalidOperationException>(() => registry.SetObjective(trainer, true));
        Assert.Equal(
            [
                Level100ActorFactKind.Hit,
                Level100ActorFactKind.StartedDying,
                Level100ActorFactKind.Died,
            ],
            snapshot.PendingFacts.Select(item => item.Kind).ToArray());

        var restored = new Level100ActorRegistry(definitions, snapshot);
        Level100ActorRegistrySnapshot restoredSnapshot = restored.Snapshot;
        Assert.Equal(snapshot.NextActorId, restoredSnapshot.NextActorId);
        Assert.Equal(snapshot.NextFactSequence, restoredSnapshot.NextFactSequence);
        Assert.Equal(snapshot.Actors, restoredSnapshot.Actors);
        Assert.Equal(snapshot.PendingFacts, restoredSnapshot.PendingFacts);

        Level100ActorRegistrySnapshot impossibleLifecycle = snapshot with
        {
            Actors = snapshot.Actors
                .Select(item => item.ActorId == trainer
                    ? item with { Active = true, IsObjective = true }
                    : item)
                .ToArray(),
        };
        Assert.Throws<ArgumentException>(() =>
            new Level100ActorRegistry(definitions, impossibleLifecycle));

        WorldSnapshot world = new Simulation(0x100u, definitions).Snapshot;
        Assert.Equal(
            StateHasher.ComputeHex(world with { Level100Actors = snapshot }),
            StateHasher.ComputeHex(world with { Level100Actors = restoredSnapshot }));
    }

    [Fact]
    public void InvalidSpawn_DoesNotConsumeIdentityOrMutateRegistry()
    {
        var registry = new Level100ActorRegistry(Level100TestActorDefinitions.Create());
        Level100ActorId airfield = registry.GetThingRef("Airfield")!.Value;
        Level100ActorRegistrySnapshot before = registry.Snapshot;

        Assert.Throws<InvalidOperationException>(() => registry.SpawnThing(
            airfield,
            "Air Trainer",
            "SpawnerB",
            2,
            "AirTrainer"));

        Level100ActorRegistrySnapshot after = registry.Snapshot;
        Assert.Equal(before.NextActorId, after.NextActorId);
        Assert.Equal(before.NextFactSequence, after.NextFactSequence);
        Assert.Equal(before.Actors, after.Actors);
        Assert.Equal(before.PendingFacts, after.PendingFacts);
    }

    /// <summary>
    /// Two definition sets with identical node coordinates but different
    /// TRAVERSAL ORDERS are different definition sets.
    /// </summary>
    /// <remarks>
    /// <para>
    /// The chain decides which node a follower steers at, so a set that walks
    /// <c>Flyby Path</c> as <c>[41, 42, 43]</c> and one that walks it as
    /// <c>[43, 42, 41]</c> produce different simulations from the same
    /// geometry. If <c>ComputeIdentity</c> ignored the chain, those two would
    /// share a digest, a snapshot taken under one would restore cleanly under
    /// the other, and a replay would silently diverge.
    /// </para>
    /// <para>
    /// This is the exact hole that let the previous waypoint defect live: the
    /// aliased coordinate table and the corrected one were distinguishable only
    /// because positions happened to be hashed. Order was not, until #146.
    /// </para>
    /// </remarks>
    [Fact]
    public void DefinitionIdentity_SeparatesRoutesThatDifferOnlyInTraversalOrder()
    {
        Level100ActorDefinitionSet original = Level100TestActorDefinitions.Create();
        var reordered = new Level100ActorDefinitionSet(
            original.Actors,
            original.Spawns,
            original.WaypointPaths
                .Select(path => new Level100WaypointPathDefinition(
                    path.Name,
                    path.Points,
                    path.Points.Select(point => point.NodeIndex).ToArray(),
                    path.IsClosed))
                .ToArray(),
            original.MotionDefinitions);

        // Same geometry, node for node, on every path.
        foreach (Level100WaypointPathDefinition path in original.WaypointPaths)
        {
            Assert.Equal(
                path.Points,
                reordered.GetWaypointPath(path.Name).Points);
        }

        Assert.NotEqual(original.IdentitySha256, reordered.IdentitySha256);

        // And the closure flag is hashed too, on its own.
        var unlooped = new Level100ActorDefinitionSet(
            original.Actors,
            original.Spawns,
            original.WaypointPaths
                .Select(path => new Level100WaypointPathDefinition(
                    path.Name,
                    path.Points,
                    path.TargetChainNodeIndices,
                    IsClosed: false))
                .ToArray(),
            original.MotionDefinitions);
        Assert.Contains(original.WaypointPaths, path => path.IsClosed);
        Assert.NotEqual(original.IdentitySha256, unlooped.IdentitySha256);
    }

    [Fact]
    public void DefinitionIdentity_OwnsAuthoredDataAndRejectsCrossSetRestore()
    {
        Level100ActorDefinitionSet original = Level100TestActorDefinitions.Create();
        Level100ActorDefinition first = original.Actors[0];
        Level100ActorPoseSnapshot changedPose = first.InitialPose with
        {
            PositionMillimeters = first.InitialPose.PositionMillimeters with
            {
                X = first.InitialPose.PositionMillimeters.X + 1,
            },
        };
        Level100ActorDefinition[] changedActors = original.Actors.ToArray();
        changedActors[0] = first with { InitialPose = changedPose };
        var changed = new Level100ActorDefinitionSet(
            changedActors,
            original.Spawns,
            original.WaypointPaths,
            original.MotionDefinitions);
        var withPath = new Level100ActorDefinitionSet(
            original.Actors,
            original.Spawns,
            [
                new Level100WaypointPathDefinition(
                    "Path",
                    [
                        new Level100WaypointPointDefinition(
                            1,
                            new SimVector3(10, 30, 20),
                            new Level100FloatVector4Bits(1, 2, 3, 4)),
                    ],
                    [1],
                    false),
            ],
            original.MotionDefinitions);

        Assert.NotEqual(original.IdentitySha256, changed.IdentitySha256);
        Assert.NotEqual(original.IdentitySha256, withPath.IdentitySha256);
        Level100ActorRegistrySnapshot snapshot = new Level100ActorRegistry(original).Snapshot;
        Assert.Throws<ArgumentException>(() => new Level100ActorRegistry(changed, snapshot));

        WorldSnapshot originalWorld = new Simulation(0x100u, original).Snapshot;
        WorldSnapshot changedWorld = new Simulation(0x100u, changed).Snapshot;
        Assert.NotEqual(
            StateHasher.ComputeHex(originalWorld),
            StateHasher.ComputeHex(changedWorld));

        Level100ActorRegistrySnapshot incomplete = snapshot with
        {
            Actors = snapshot.Actors.Skip(1).ToArray(),
        };
        Assert.Throws<ArgumentException>(() =>
            new Level100ActorRegistry(original, incomplete));

        Level100ActorRegistry registry = new(original);
        Level100ActorId airfield = registry.GetThingRef("Airfield")!.Value;
        Level100ActorId drone = Assert.Single(registry.SpawnThing(
            airfield,
            "Target Drone",
            "SpawnerB",
            1,
            "AirborneDrone1"));
        Level100ActorRegistrySnapshot spawnedSnapshot = registry.Snapshot;
        Level100ActorSnapshot changedSpawn = registry.GetActor(drone) with { Name = "changed" };
        Level100ActorRegistrySnapshot changedSpawnSnapshot = spawnedSnapshot with
        {
            Actors = spawnedSnapshot.Actors
                .Select(actor => actor.ActorId == drone ? changedSpawn : actor)
                .ToArray(),
        };
        Assert.Throws<ArgumentException>(() =>
            new Level100ActorRegistry(original, changedSpawnSnapshot));
    }

    [Fact]
    public void Restore_AllowsReleasedSetupScriptMutationAndRejectsUnknownScript()
    {
        Level100ActorDefinitionSet definitions = Level100TestActorDefinitions.Create();
        var registry = new Level100ActorRegistry(definitions);
        Level100ActorId tankFactory = registry.GetThingRef("Tank Factory")!.Value;
        registry.SetScript(tankFactory, "TankFactory");

        Level100ActorRegistrySnapshot setupSnapshot = registry.Snapshot;
        var restored = new Level100ActorRegistry(definitions, setupSnapshot);
        Assert.Equal("TankFactory", restored.GetActor(tankFactory).ScriptName);

        Level100ActorRegistrySnapshot unknownScript = setupSnapshot with
        {
            Actors = setupSnapshot.Actors
                .Select(actor => actor.ActorId == tankFactory
                    ? actor with { ScriptName = "NotAReleasedProgram" }
                    : actor)
                .ToArray(),
        };
        Assert.Throws<ArgumentException>(() =>
            new Level100ActorRegistry(definitions, unknownScript));
    }

    [Fact]
    public void SpawnThing_UsesAuthoredPoseAndKeepsDuplicateNamesOnDistinctIds()
    {
        Level100ActorDefinitionSet definitions = Level100TestActorDefinitions.Create();
        var registry = new Level100ActorRegistry(definitions);
        Level100ActorId airfield = registry.GetThingRef("Airfield")!.Value;
        Level100SpawnDefinition authored = definitions.Spawns.Single(item =>
            item.ScriptName == "AirborneDrone1");

        Level100ActorId[] actors = Enumerable.Range(0, 3)
            .Select(_ => Assert.Single(registry.SpawnThing(
                airfield,
                "Target Drone",
                "SpawnerB",
                1,
                "AirborneDrone1")))
            .ToArray();

        Assert.Equal(3, actors.Distinct().Count());
        Assert.Null(registry.GetThingRef("AirborneDrone1"));

        // Re-derived 2026-08-01, when SeatOnGround stopped being ground-vehicle
        // only and became the general CThing::Init support clamp. The authored
        // spawn vertical is -6133; the terrain sample at the emitter's own
        // (46216, 14450) is 0, which is above both it and the water plane at
        // -1160, so Init seats it at 0. EVERYTHING ELSE about the pose is still
        // the authored pose verbatim, and that is asserted separately rather
        // than folded into one comparison, so a basis or velocity that moved
        // could not hide behind the vertical.
        Level100ActorPoseSnapshot seated = authored.InitialPose with
        {
            PositionMillimeters = authored.InitialPose.PositionMillimeters with
            {
                Y = 0,
            },
        };
        Assert.Equal(-6_133, authored.InitialPose.PositionMillimeters.Y);
        Assert.All(actors, actorId =>
            Assert.Equal(seated, registry.GetActor(actorId).Pose));
        Assert.DoesNotContain(registry.Snapshot.Actors, actor => actor.Pose is null);
    }

    [Fact]
    public void SetPose_RejectsNonFiniteBasisWithoutMutatingActor()
    {
        var registry = new Level100ActorRegistry(Level100TestActorDefinitions.Create());
        Level100ActorId player = registry.GetThingRef("Player 1")!.Value;
        Level100ActorPoseSnapshot before = registry.GetActor(player).Pose;
        Level100ActorPoseSnapshot invalid = before with
        {
            BasisFloatBits = before.BasisFloatBits with
            {
                Row0X = BitConverter.SingleToInt32Bits(float.NaN),
            },
        };

        Assert.Throws<ArgumentException>(() => registry.SetPose(player, invalid));
        Assert.Equal(before, registry.GetActor(player).Pose);
    }

    [Fact]
    public void SimulationRoutesExactFacilityEventSpellingsFromRegistryActors()
    {
        var tankFactorySimulation = new Simulation(
            0x100u,
            Level100TestActorDefinitions.Create());
        Level100ActorId tankFactory = tankFactorySimulation.Snapshot.Level100Actors.Actors
            .Single(actor => actor.Name == "Tank Factory")
            .ActorId;
        WorldSnapshot matching = tankFactorySimulation.Step(
            SimInput.Idle,
            [new Level100ActorDiedFact(tankFactory)]);
        Assert.Contains(
            matching.Level100Mission.Continuations,
            item => item.Execution.EventName == "Friendly Building Destroyed");

        var facilitiesSimulation = new Simulation(
            0x100u,
            Level100TestActorDefinitions.Create());
        Level100ActorId controlTower = facilitiesSimulation.Snapshot.Level100Actors.Actors
            .Single(actor => actor.Name == "Control Tower")
            .ActorId;
        WorldSnapshot mismatched = facilitiesSimulation.Step(
            SimInput.Idle,
            [new Level100ActorDiedFact(controlTower)]);
        Assert.DoesNotContain(
            mismatched.Level100Mission.Continuations,
            item => item.Execution.EventName is
                "Friendly Building Destroyed" or "Destroyed Friendly Building");
    }
}
