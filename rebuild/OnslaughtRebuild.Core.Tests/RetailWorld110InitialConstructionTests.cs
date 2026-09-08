// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.TestSupport;
using System.Buffers.Binary;
using System.Security.Cryptography;

namespace OnslaughtRebuild.Core.Tests;

public sealed class RetailWorld110InitialConstructionTests
{
    [Fact]
    public void ControlTower_UsesExistingActorAndRealPrecedingSpatialOwners()
    {
        var world = RetailWorld110InitialConstruction.CreateWithControlTower(123456);
        var tower = Assert.IsType<RetailWorld110Building>(world.ControlTower);
        Assert.Equal(1481, world.Trees.Count);
        Assert.Equal(1482, world.SpatialEntryCount);
        Assert.Equal(43, world.Actors.Snapshot.Actors.Count);
        Assert.Equal(world.ActorWorldIdentities[tower.ActorId], tower.Identity);
        Assert.Same(tower, tower.MapEntry.Owner);
        Assert.True(tower.MapEntry.IsRegistered);
        Assert.Equal(new RetailMapWhoSector(17, 15, 3), tower.MapEntry.Sector);
        Assert.Equal(15, tower.InitialRejectedPeerCount);
        Assert.Equal(0xc0900133u, tower.ThingTypeMask);
        Assert.Equal(ThingActorFlags.InMapWho, tower.ActorState.Flags);
        Assert.Equal(0x0a9, tower.CollisionFlags);
        Assert.Equal(0x08000020u, tower.CollisionExclusionMask);
        Assert.Equal(2, tower.CollisionMinimumKind);
        Assert.Equal(2, tower.CollisionMaximumKind);
        Assert.Equal(unchecked((int)0xc1199926), tower.PositionFloatBits.Z);
        Assert.Same(tower.ActorState.RetailPoses, world.Actors.GetBaseState(tower.ActorId).RetailPoses);
        Assert.Equal(tower.ActorState.CurrentPose.PositionMillimeters,
            world.Actors.GetActor(tower.ActorId).Pose.PositionMillimeters);
        Assert.Equal(tower.ActorState.RetailPoses!.Current, tower.ActorState.RetailPoses.Old);
        Assert.Equal(int.MinValue, tower.ActorState.RetailPoses.Current.BasisFloatBits.Row2X);
        Assert.Same(tower, world.InitializedThingsNewestFirst.First());
        Assert.Equal(world.Trees.Reverse(), world.InitializedThingsNewestFirst.Skip(1));
        Assert.Same(tower, Assert.Single(world.NamedBuildingsNewestFirst));
        Assert.Same(tower, Assert.Single(world.UnitsNewestFirst));
        Assert.Same(tower, Assert.Single(world.FactionUnits(0)));
        Assert.Empty(world.FactionUnits(1));
        Assert.Equal(1, world.UnitCount(0, 7));
        Assert.Equal(0, world.UnitCount(1, 7));
        Assert.Equal(0, world.WorldMeshCatalogCount);
        Assert.False(world.IsUnitDefinitionUsed("Control Tower"));
        Assert.Same(tower, Assert.Single(world.OccupancyCandidatesNewestFirst));
        Assert.False(world.OccupancyActive);
        Assert.Equal(3, world.OccupancyBitplanes.Count);
        Assert.All(world.OccupancyBitplanes, plane =>
        { Assert.Equal(8192, plane.Count); Assert.All(plane, value => Assert.Equal(255, value)); });
        Assert.Same(tower.PrimaryEffect, world.PrimaryEffectHead);
        Assert.Same(tower, tower.PrimaryEffect.Owner);
        Assert.Null(tower.PrimaryEffect.Next);
        Assert.False(tower.PrimaryEffect.HasEffect);
        // A tree-only diagnostic must tolerate the new mixed spatial owner.
        Assert.All(world.GetTreeCollisionNeighbors(0), tree => Assert.Same(world.Trees[tree.Ordinal], tree));
    }

    [Fact]
    public void ControlTower_SegmentsRetainGraphFloatStoresAndSharedReferences()
    {
        var world = RetailWorld110InitialConstruction.CreateWithControlTower(123456);
        var segments = world.ControlTower!.Segments;
        int[] order = [0,1,2,3,4,5,6,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,30,31,32,33];
        int[] scale = [0,0x419690b2,0x418a9ec1,0x41841869,0x41698d57,0x41300788,0x41300788,
            0x4194c620,0x4006efbf,0x401a2f94,0x403f5b11,0x4049f2cd,0x4049f2cd,0x40c214bb,
            0x4093973f,0x40a0e5f7,0x40a0807c,0x4047959d,0x4091719f,0x401f800c,0x409171a1,
            0x4016ca59,0x4091719f,0x404d12db,0x409171a1,0x40204a27,0x406fb0d9,0x40988e20,0x40615098];
        Assert.Equal(order, segments.Allocated.Select(segment => segment.PartOrdinal));
        Assert.Equal(8, segments.CoreCount);
        Assert.Equal(40, segments.ByPart.Count);
        Assert.Equal(Enumerable.Range(1, 8), segments.Allocated.Where(segment => segment.CoreOrdinal.HasValue)
            .Select(segment => segment.CoreOrdinal!.Value));
        Assert.Equal(0x425e25dc, BitConverter.SingleToInt32Bits(segments.TotalWeight));
        Assert.Equal(0x433a4938, BitConverter.SingleToInt32Bits(segments.InitialTotalHealth));
        Assert.Equal(scale, segments.Allocated.Select(segment => BitConverter.SingleToInt32Bits(segment.Health)));
        Assert.Equal(segments.Allocated.Reverse(), world.SegmentsNewestFirst);
        Assert.Equal(segments.Allocated.Count, segments.Allocated.Select(segment => segment.Identity).Distinct().Count());
        foreach (var segment in segments.Allocated)
        {
            Assert.Same(segment, segments.ByPart[segment.PartOrdinal]);
            Assert.Equal(segment.Health, segment.InitialHealth);
            Assert.All(segment.ChildrenNewestFirst, child => Assert.Same(segment, child.Parent));
        }
        Assert.Same(segments.ByPart[0], segments.Root);
        Assert.Null(segments.Root.Parent);
        Assert.Equal(new[] {33,32,31,30,2}, segments.ByPart[1]!.ChildrenNewestFirst.Select(segment => segment.PartOrdinal));
        Assert.Equal(new[] {24,22,20,18,5}, segments.ByPart[4]!.ChildrenNewestFirst.Select(segment => segment.PartOrdinal));
        Assert.Equal(new[] {17,16,15,14,9}, segments.ByPart[8]!.ChildrenNewestFirst.Select(segment => segment.PartOrdinal));
        Assert.Equal(new[] {13,12}, segments.ByPart[11]!.ChildrenNewestFirst.Select(segment => segment.PartOrdinal));
        Assert.Equal(new[] {7,26,27,28,29,34,35,36,37,38,39},
            Enumerable.Range(0, 40).Where(index => segments.ByPart[index] is null));
    }

    [Fact]
    public void ControlTower_ConsumesOneAdditionalDrawAndOwnsFiveUndeliveredEvents()
    {
        var world = RetailWorld110InitialConstruction.CreateWithControlTower(123456);
        var tower = world.ControlTower!;
        var random = new Level100ReleasedRandom(123456);
        for (int index = 0; index < 1482; index++) random.Next();
        Assert.Equal(random.Seed, world.ReleasedRandomSeed);
        Assert.Equal(0, tower.MovePhase);
        Assert.Equal(new RetailActorMotionSnapshot(0, 1), tower.ActorState.RetailMotion);
        Assert.Equal(1481, world.PendingTreeEvents);
        Assert.Equal(1486, world.PendingEvents);
        var admissions = new[] {tower.Collision.InitialEvent, tower.MoveEvent, tower.UnitEvent,
            tower.Ai.InitialEvent, tower.Animation.InitialEvent};
        Assert.Equal(Enumerable.Range(1481, 5), admissions.Select(admission => admission.Handle));
        Assert.Equal(new short[] {3000, 3000, 4003, 3000, 3000},
            admissions.Select(admission => world.Events!.EventNumOf(admission.Handle)));
        Assert.Equal(new[] {tower.Collision.Identity, tower.Identity, tower.Identity, tower.Ai.Identity, tower.Animation.Identity},
            admissions.Select(admission => world.Events!.ListenerOf(admission.Handle)));
        Assert.All(admissions, admission => Assert.Equal(RetailEventPlacement.ImmediateBucket, admission.Placement));
        Assert.Equal(0u, tower.Ai.InitialEvent.DueTimeBits);
        Assert.All(new[] {admissions[0], admissions[1], admissions[2], admissions[4]},
            admission => Assert.Equal(BitConverter.SingleToUInt32Bits(0.0001f), admission.DueTimeBits));
        Assert.Equal(4, new[] {tower.Identity, tower.Collision.Identity, tower.Ai.Identity, tower.Animation.Identity}.Distinct().Count());
        Assert.Same(tower, tower.Collision.Owner);
        Assert.Same(tower, tower.Ai.Owner);
        Assert.Same(tower, tower.Animation.Owner);
        Assert.Equal(1, tower.Ai.State);
        Assert.Null(tower.Ai.TargetIdentity);
        Assert.Null(tower.Ai.SpawnedByIdentity);
        Assert.All(new[] {tower.Ai.ReaderCell0C, tower.Ai.TargetReaderCell24, tower.Ai.SpawnedByReaderCell28}, reader =>
        { Assert.True(world.Readers.ContainsReaderCell(reader)); Assert.Null(world.Readers.TargetOf(reader)); });
        Assert.Empty(world.Readers.ReadersNewestFirst(tower.Identity)); // Owner+8 is a direct reference.
        Assert.Equal(-1, tower.AnimationMode);
        Assert.True(tower.AnimationForceLoop);
        Assert.Equal(1, tower.AnimationIncrement);
        Assert.False(tower.HasNotShutAnimation);
        Assert.Throws<NotSupportedException>(() => world.AdvanceTreeReadinessEvents());
        Assert.Equal(0, world.EventTime);
        Assert.Equal(1486, world.PendingEvents);
        Assert.All(world.Trees, tree => Assert.False(tree.CollisionReady));
    }

    [Fact]
    public void ControlTower_RejectsIncompleteRestoreHashAndLegacyLifecycle()
    {
        var world = RetailWorld110InitialConstruction.CreateWithControlTower(123456);
        var tower = world.ControlTower!;
        var before = world.Actors.GetActor(tower.ActorId);
        var state = world.Actors.GetBaseState(tower.ActorId);
        Assert.Throws<NotSupportedException>(() => world.Actors.ReportDied(tower.ActorId));
        Assert.Throws<NotSupportedException>(() => world.Actors.ReportStartedDying(tower.ActorId));
        Assert.Throws<NotSupportedException>(() => world.Actors.SetHealth(tower.ActorId, 0));
        Assert.Throws<NotSupportedException>(() => world.Actors.Deactivate(tower.ActorId));
        Assert.Equal(before, world.Actors.GetActor(tower.ActorId));
        Assert.Equal(state, world.Actors.GetBaseState(tower.ActorId));
        Assert.Empty(world.Actors.Snapshot.PendingFacts);
        Assert.Equal(1486, world.PendingEvents);
        Assert.Equal(1482, world.SpatialEntryCount);
        Assert.Throws<NotSupportedException>(() => world.RestoreActors(world.Actors.Snapshot));
        var envelope = new Simulation(1, Level100TestActorDefinitions.Create()).Snapshot;
        Assert.Throws<NotSupportedException>(() => StateHasher.ComputeHex(envelope with
        { Level100Actors = world.Actors.Snapshot }));
    }

    [Fact]
    public void BaseTrees_ConstructRealOwnedCThingsAndPublishOnceInLoadOrder()
    {
        var world = RetailWorld110InitialConstruction.CreateWithBaseTrees(123456);
        Assert.Equal(1481, world.Trees.Count);
        Assert.Equal(1481, world.SpatialEntryCount);
        Assert.Equal(0, world.UnconstructedTreeCount);
        Assert.Equal(43, world.Actors.Snapshot.Actors.Count);
        Assert.Equal(world.Trees.Reverse(), world.InitializedTreesNewestFirst);
        Assert.False(world.InitializedTreesNewestFirst is ICollection<RetailWorld110Tree>);
        var placements = world.TreeTables[0].Groups[1].Placements;
        foreach (RetailWorld110Tree tree in world.Trees)
        {
            Assert.Equal(placements[tree.Ordinal].PositionXFloatBits, tree.PositionFloatBits.X);
            Assert.Equal(placements[tree.Ordinal].PositionYFloatBits, tree.PositionFloatBits.Y);
            Assert.Equal(placements[tree.Ordinal].Variant, tree.Mesh.Variant);
            Assert.Same(tree, tree.MapEntry.Owner);
            Assert.True(tree.MapEntry.IsRegistered);
            Assert.Equal(4, tree.MapEntry.Sector.Layer);
            Assert.Equal(ThingActorFlags.InMapWho, tree.Flags);
            Assert.Equal(0x02800021u, tree.ThingTypeMask);
            Assert.Equal(0u, tree.ThingTypeMask & (ThingActorTypeMasks.Actor | ThingActorTypeMasks.ComplexThing));
            Assert.False(tree.MatrixCacheValid);
            Assert.False(tree.HasFallingTreeData);
        }
        // Constructor scans inspect real earlier pines, not an empty provider.
        Assert.True(world.Trees.Sum(tree => tree.InitialRejectedPeerCount) > 1000);
        var neighbors = world.GetTreeCollisionNeighbors(0);
        Assert.Contains(world.Trees[0], neighbors);
        Assert.True(neighbors.Count > 1);
        Assert.All(neighbors, tree => Assert.Same(world.Trees[tree.Ordinal], tree));
        Assert.Throws<NotSupportedException>(() => ((IList<RetailWorld110Tree>)world.Trees).Clear());
    }

    [Fact]
    public void BaseTrees_UseActualTerrainFloatWordsAndDistinctMeshBounds()
    {
        var world = RetailWorld110InitialConstruction.CreateWithBaseTrees(123456);
        int[] radii = [0x4005575c, 0x4007f5c1, 0x400cea52, 0x40054422];
        Assert.Equal(radii, world.TreeMeshes.Select(mesh => mesh.MeshRadiusFloatBits));
        foreach (RetailWorld110Tree tree in world.Trees)
        {
            float x = BitConverter.Int32BitsToSingle(tree.PositionFloatBits.X);
            float y = BitConverter.Int32BitsToSingle(tree.PositionFloatBits.Y);
            // Independent fixed-coordinate formulation, equivalent only for
            // these admitted inputs under the stated nearest-store assumption.
            float sampled = world.Terrain.Heightfield.SampleHeightUnitsAtFixed(
                (int)Math.Floor(x * 256.0), (int)Math.Floor(y * 256.0)) * world.Terrain.Heightfield.HeightScale;
            float expected = Math.Min(sampled, world.Terrain.Heightfield.WaterLevel);
            Assert.Equal(BitConverter.SingleToInt32Bits(expected), tree.PositionFloatBits.Z);
            Assert.Equal(0x3e4ccccd, tree.CollisionRadiusFloatBits);
            Assert.Equal(0x3d23d70b, tree.CollisionRadiusSquaredFloatBits);
            Assert.Equal(BitConverter.SingleToInt32Bits(
                BitConverter.Int32BitsToSingle(radii[tree.Mesh.Variant]) / 2), tree.CollisionHalfHeightFloatBits);
            Assert.Equal(0x20u, tree.CollisionMask);
            Assert.Equal(1, tree.CollisionMaximumKind);
        }
        Assert.Equal(new RetailMapWhoSector(41, 31, 4), world.Trees[0].MapEntry.Sector);
        Assert.All(world.TreeMeshes, mesh => Assert.Throws<NotSupportedException>(() =>
            ((IList<int>)mesh.GlobalBoundingBoxWords).Clear()));
    }

    [Fact]
    public void BaseTrees_ConsumeOneSharedDrawEachAndDispatchActualReadinessListeners()
    {
        var world = RetailWorld110InitialConstruction.CreateWithBaseTrees(123456);
        var random = new Level100ReleasedRandom(123456);
        foreach (RetailWorld110Tree tree in world.Trees)
        {
            int expected = (int)Math.Round((random.Next() % 65536) / 2048.0, MidpointRounding.ToEven);
            Assert.Equal(expected, tree.InitialRotationSelector);
            Assert.False(tree.CollisionReady);
            Assert.Equal(RetailEventPlacement.ImmediateBucket, tree.ReadinessEvent.Placement);
        }
        Assert.Contains(world.Trees, tree => tree.InitialRotationSelector == 32);
        Assert.Equal(random.Seed, world.ReleasedRandomSeed);
        Assert.Equal(1481, world.PendingTreeEvents);
        var dispatched = world.AdvanceTreeReadinessEvents();
        Assert.Equal(world.Trees.Select(tree => tree.CollisionIdentity), dispatched.Select(item => item.Listener));
        Assert.All(dispatched, item =>
        {
            Assert.Equal(3000, item.EventNum);
            Assert.Equal(RetailEventPriority.StartOfFrame, item.Priority);
        });
        Assert.All(world.Trees, tree => Assert.True(tree.CollisionReady));
        Assert.Equal(0, world.PendingTreeEvents);
        Assert.Equal(random.Seed, world.ReleasedRandomSeed); // No callback draw.
        Assert.Empty(world.AdvanceTreeReadinessEvents()); // No reschedule.
    }

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
