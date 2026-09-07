// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.TestSupport;

namespace OnslaughtRebuild.Core.Tests;

public sealed class RetailWorld110InitialConstructionTests
{
    [Fact]
    public void ProductionConstruction_UsesReal110UnitsAndPreservesUnnamedActors()
    {
        var world = RetailWorld110InitialConstruction.Create();
        Assert.Equal(110, world.ActorDefinitions.WorldNumber);
        Assert.Equal(43, world.Actors.Snapshot.Actors.Count);
        Assert.Equal(33, world.ActorInputs.Count(input => input.Actor.IsStatic));
        RetailWorld110InitialActorInput[] units = world.ActorInputs
            .Where(input => !input.Actor.IsStatic).ToArray();
        Assert.Equal(new[] { 8, 12, 13, 20, 25, 34, 35, 36, 37, 38 },
            units.Select(input => int.Parse(input.Actor.DefinitionIdentity[^4..])));
        Assert.All(units, input => Assert.Equal("", input.Actor.Name));
        Assert.All(units, input =>
        {
            RetailWorldInitialObjectSeed seed = world.InitialObjectSeeds.Rows.Single(
                item => item.ObjectIdentity == input.Actor.DefinitionIdentity);
            Assert.Equal(seed.Allegiance, input.Allegiance);
            Assert.Equal(seed.Target, input.Target);
            Assert.Equal(seed.ActiveWord, input.ActiveWord);
            Assert.Equal(seed.MeshNumber, input.MeshNumber);
            Assert.Equal(seed.SpawnScript, input.SpawnScript);
            Assert.Equal(seed.AttachScriptsToUnitsWord, input.AttachScriptsToUnitsWord);
        });
        Assert.Equal(new[] { 70_000, 70_000, 70_000, 70_000, 4_000,
            3_000, 3_000, 3_000, 3_000, 3_000 },
            units.Select(input => input.Actor.InitialHealth));
        Assert.Equal(new[] { 12, 12, 12, 12, 8, 8, 8, 8, 8, 8 },
            units.Select(input => input.InternalBehaviourSelector!.Value));
        Assert.Equal("Muspell Light Landing Craft", units[0].Actor.DefinitionName);
        Assert.Equal("M_Dropship.msh", units[0].Actor.MeshBinding);
        Assert.Equal("Lander", units[0].Actor.ScriptName);
        Assert.Equal(new SimVector3(-73_688, 10_000, 178_750),
            units[0].Actor.InitialPose.PositionMillimeters);
        Assert.Null(world.Actors.GetThingRef("Player 1"));
        Assert.DoesNotContain(world.ActorDefinitions.Actors,
            actor => actor.DefinitionIdentity == "wres:rlwd:0000");
        Assert.NotEqual(Level100TestActorDefinitions.Create().IdentitySha256,
            world.ActorDefinitions.IdentitySha256);
    }

    [Fact]
    public void Construction_KeepsMissingConstructorsExplicitAndDoesNotInitializeOrSpawn()
    {
        var world = RetailWorld110InitialConstruction.Create();
        Assert.Equal(30, world.UnconstructedInitialObjects.Count);
        Assert.Equal(new[] { 21, 22 }, world.UnconstructedBaseObjectOrdinals);
        Assert.Single(world.UnconstructedInitialObjects, seed => seed.ThingType == 15);
        Assert.Equal(5, world.UnconstructedInitialObjects.Count(seed => seed.ThingType == 28));
        RetailWorldInitialObjectSeed spawner = Assert.Single(
            world.UnconstructedInitialObjects, seed => seed.ThingType == 19);
        Assert.Equal(0, spawner.ActiveWord);
        Assert.Equal(3, Assert.IsType<RetailWorldSpawnerSeedTail>(spawner.Tail).Amount);
        Assert.Empty(world.ActorDefinitions.Spawns);
        Assert.Empty(world.ActorDefinitions.WaypointPaths);
        Assert.Empty(world.ActorDefinitions.MotionDefinitions);
        Assert.Empty(world.Actors.Snapshot.PendingFacts);
        Assert.All(world.Actors.Snapshot.Actors, actor =>
        {
            Level100ActorDefinition definition = world.ActorDefinitions.Actors
                .Single(item => item.DefinitionIdentity == actor.DefinitionIdentity);
            Assert.Equal(definition.InitialPose, actor.Pose);
            Assert.Null(actor.SpawnOwnerId);
        });
    }

    [Fact]
    public void Terrain_Binds110HeightfieldInExplicitSharedCoordinateFrame()
    {
        var world = RetailWorld110InitialConstruction.Create();
        Assert.Equal(110, world.Terrain.WorldNumber);
        Assert.Equal(Level100Terrain.World110SourceSha256,
            world.Terrain.Heightfield.PayloadSha256, ignoreCase: true);
        Assert.NotEqual(Level100Terrain.Instance.PayloadSha256,
            world.Terrain.Heightfield.PayloadSha256);
        // Exact admitted World110 start XY in retail 24.8 coordinates.
        Assert.Equal(-10_485, world.Terrain.Heightfield.SampleHeightUnitsAtFixed(67_776, 66_256));
        Assert.Equal(Level100Terrain.WaterElevationMillimeters,
            RetailWorldTerrain.World100.WaterElevationMillimeters);
    }

    [Fact]
    public void Snapshot_Retains110ScriptsAndDistinctActorsOnRestore()
    {
        var world = RetailWorld110InitialConstruction.Create();
        var snapshot = world.Actors.Snapshot;
        var restored = world.RestoreActors(snapshot).Snapshot;
        Assert.Equal(snapshot.Actors, restored.Actors);
        Assert.Equal(snapshot.BaseStates, restored.BaseStates);
        Assert.Equal(snapshot.DefinitionSetIdentitySha256,
            RetailWorld110InitialConstruction.Create().Actors.Snapshot.DefinitionSetIdentitySha256);
        Level100ActorSnapshot lander = snapshot.Actors.Single(actor => actor.ScriptName == "Lander2");
        Assert.Throws<ArgumentException>(() => world.RestoreActors(snapshot with
        {
            Actors = snapshot.Actors.Select(actor => actor.ActorId == lander.ActorId
                ? actor with { ScriptName = "AirTrainer" } : actor).ToArray(),
        }));
    }

    [Fact]
    public void ScriptAssignment_UsesTheSameWorldAdmissionAsSnapshotRestore()
    {
        var world = RetailWorld110InitialConstruction.Create();
        Level100ActorId lander = world.Actors.Snapshot.Actors
            .Single(actor => actor.ScriptName == "Lander2").ActorId;
        world.Actors.SetScript(lander, "Lander");
        var beforeRefusal = world.Actors.Snapshot;
        Assert.Equal(beforeRefusal.Actors, world.RestoreActors(beforeRefusal).Snapshot.Actors);

        Assert.Throws<InvalidOperationException>(() => world.Actors.SetScript(lander, "AirTrainer"));
        Assert.Equal(beforeRefusal.Actors, world.Actors.Snapshot.Actors);
    }

    [Fact]
    public void Asset_RejectsAlteredOrSubstitutedBytes()
    {
        Assert.Throws<ArgumentException>(() =>
            RetailWorld110InitialConstruction.Decode("World 100"u8.ToArray()));
    }
}
