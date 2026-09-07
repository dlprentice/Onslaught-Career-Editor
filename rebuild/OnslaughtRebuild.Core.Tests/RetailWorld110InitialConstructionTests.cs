// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.TestSupport;
using System.Buffers.Binary;
using System.Security.Cryptography;

namespace OnslaughtRebuild.Core.Tests;

public sealed class RetailWorld110InitialConstructionTests
{
    [Fact]
    public void TreeInputs_RetainBothTablesButOnlyBasePinesCallInit()
    {
        var world = RetailWorld110InitialConstruction.Create();
        Assert.Equal(new[] { "BSWD", "RLWD" }, world.TreeTables.Select(table => table.SourceChunk));
        Assert.Equal(new[] { 2709, 18327 }, world.TreeTables.Select(table => table.HeaderOffset));
        Assert.Equal(new[] { 29549, 45167 }, world.TreeTables.Select(table => table.EndOffset));
        Assert.Equal(new[] { false, true, false, false },
            world.TreeTables.SelectMany(table => table.Groups).Select(group => group.CallsTreeInit));
        string[] digests = [
            "c6b83ebfacf563f04294decfd1d5879726895bbd33fb23f2164b01c391117372",
            "c4308e46dad3b687051eb9c6e4650f923133d713f92401f3db997a6fa28bae59"];
        foreach (RetailWorld110TreeTableInput table in world.TreeTables)
        {
            Assert.Equal(new[] { "fernsnow", "pinesnow" }, table.Groups.Select(group => group.Name));
            Assert.Equal(new[] { 753, 1481 }, table.Groups.Select(group => group.Placements.Count));
            for (int groupIndex = 0; groupIndex < table.Groups.Count; groupIndex++)
            {
                RetailWorld110TreeGroupInput group = table.Groups[groupIndex];
                byte[] records = new byte[group.Placements.Count * 12];
                for (int index = 0; index < group.Placements.Count; index++)
                {
                    RetailWorld110TreePlacement placement = group.Placements[index];
                    BinaryPrimitives.WriteInt32LittleEndian(records.AsSpan(index * 12), placement.PositionXFloatBits);
                    BinaryPrimitives.WriteInt32LittleEndian(records.AsSpan(index * 12 + 4), placement.PositionYFloatBits);
                    BinaryPrimitives.WriteInt32LittleEndian(records.AsSpan(index * 12 + 8), placement.Variant);
                }
                Assert.Equal(digests[groupIndex], group.RecordsSha256);
                Assert.Equal(digests[groupIndex], Convert.ToHexString(SHA256.HashData(records)), ignoreCase: true);
                Assert.Throws<NotSupportedException>(() =>
                    ((IList<RetailWorld110TreePlacement>)group.Placements)[0] = default);
            }
        }
        // The two serialized tables are retained; neither is silently merged
        // or treated as a second instantiated grove. No tree Init runs here.
        Assert.Equal(1481, world.UnconstructedTreeCount);
        Assert.Equal(43, world.Actors.Snapshot.Actors.Count);
        Assert.Empty(world.Actors.Snapshot.PendingFacts);
    }

    [Fact]
    public void ComponentInitInputs_UseFourRealOwnersAndNativeArithmeticResults()
    {
        var world = RetailWorld110InitialConstruction.Create();
        Assert.Equal(new[] { "wres:rlwd:0008", "wres:rlwd:0012", "wres:rlwd:0013", "wres:rlwd:0020" },
            world.ComponentInitInputs.Select(input => input.OwnerDefinitionIdentity));
        // Independent arithmetic probe: original x87 instructions under
        // explicit027f, not a captured game run or this C# implementation.
        uint[][] positions = [
            [0x4356f370, 0x43cddb4a, 0xc1bc8228],
            [0x4353fe1d, 0x439fbbae, 0xc1e48228],
            [0x436d8c90, 0x43af24b6, 0xc2064114],
            [0x4329f370, 0x43f75b4a, 0xc1e48228]];
        uint[] yaw = [0xc0490fda, 0xc019f91f, 0xb1466810, 0xc0490fda];
        uint[][] bases = [
            [0xbf800000, 0x33b3c5a5, 0xb34ff226, 0xb3c07e26, 0xbf7d8235, 0x3e0e8363, 0xb31be221, 0x3e0e8363, 0x3f7d8235],
            [0xbf3dc719, 0x3f2a249a, 0xbdbf4bda, 0xbf2bd0a8, 0xbf3bee4a, 0x3dd34ba9, 0xb31be221, 0x3e0e8363, 0x3f7d8235],
            [0x3f800000, 0x314479c2, 0x331bb081, 0x31181ef8, 0x3f7d8235, 0xbe0e8363, 0xb31be221, 0x3e0e8363, 0x3f7d8235]];
        for (int index = 0; index < world.ComponentInitInputs.Count; index++)
        {
            RetailWorld110ComponentInitInput input = world.ComponentInitInputs[index];
            Assert.Equal(new Level100FloatVector3Bits(unchecked((int)positions[index][0]),
                unchecked((int)positions[index][1]), unchecked((int)positions[index][2])),
                input.AttachmentPose.PositionFloatBits);
            Assert.Equal(new Level100FloatVector3Bits(unchecked((int)yaw[index]), 0x3e0efa33, 0x331d6a4f),
                input.RetailEulerFloatBits);
            uint[] basis = bases[index == 3 ? 0 : index];
            Assert.Equal(new Level100FloatBasis3Bits(
                unchecked((int)basis[0]), unchecked((int)basis[1]), unchecked((int)basis[2]),
                unchecked((int)basis[3]), unchecked((int)basis[4]), unchecked((int)basis[5]),
                unchecked((int)basis[6]), unchecked((int)basis[7]), unchecked((int)basis[8])),
                input.AttachmentPose.BasisFloatBits);
            Assert.Equal("Dropship Gun Turret", input.ComponentDefinitionName);
            Assert.Equal(1, input.AttachmentIndex);
            Assert.Equal(0, input.OrientationTypeWord);
            Assert.Equal(1, input.Allegiance);
            Assert.Equal(1, input.ActiveWord);
            Assert.Empty(input.Name);
            Assert.Empty(input.Script);
            Assert.Empty(input.SpawnScript);
            Level100ActorSnapshot owner = world.Actors.Snapshot.Actors.Single(
                actor => actor.ActorId == input.OwnerActorId);
            Assert.Equal(input.OwnerDefinitionIdentity, owner.DefinitionIdentity);
        }
        // Preparing incoming arguments does not allocate/publish children.
        Assert.Equal(43, world.Actors.Snapshot.Actors.Count);
        Assert.Empty(world.Actors.Snapshot.PendingFacts);
    }

    [Fact]
    public void LandingCraftOrigins_AlreadyClearTheActualGroundAndWaterClamps()
    {
        var world = RetailWorld110InitialConstruction.Create();
        foreach (RetailWorld110ComponentInitInput component in world.ComponentInitInputs)
        {
            var position = world.ActorInputs.Single(
                input => input.Actor.DefinitionIdentity == component.OwnerDefinitionIdentity)
                .Actor.AuthoredTransform.RetailPositionFloatBits;
            float x = BitConverter.Int32BitsToSingle(position.X);
            float y = BitConverter.Int32BitsToSingle(position.Y);
            float z = BitConverter.Int32BitsToSingle(position.Z);
            Level100Terrain terrain = world.Terrain.Heightfield;
            float ground = terrain.SampleHeightUnitsAtFixed(
                (int)(x * Level100Terrain.FixedPointUnitsPerRetailUnit),
                (int)(y * Level100Terrain.FixedPointUnitsPerRetailUnit)) * terrain.HeightScale;
            // Down-positive retail Z. This proves the actual origin clamp
            // decisions, not clearance for the entire collision volume.
            Assert.True(z < ground);
            Assert.True(z < terrain.WaterLevel);
        }
    }

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
