// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.TestSupport;

namespace OnslaughtRebuild.Core.Tests;

public sealed class RetailWorld110CannonFeatureConstructionTests
{
    [Fact]
    public void AuthoredPrefix_UsesSharedWorldOwnersAndDistinctPublicationLists()
    {
        var world = RetailWorld110InitialConstruction.CreateThroughInitialIcebergs(123456);
        var actors = world.InitializedActors;
        Assert.Equal(10, actors.Count);
        Assert.Equal(Enumerable.Range(0, 10).Select(index => $"wres:bswd:{index:0000}"),
            actors.Select(actor => actor.Input.Actor.DefinitionIdentity));
        Assert.Equal(3, world.Buildings.Count);
        Assert.IsType<RetailWorld110Cannon>(actors[3]);
        Assert.All(actors.Skip(4), actor => Assert.IsType<RetailWorld110Feature>(actor));
        Assert.Equal(43, world.Actors.Snapshot.Actors.Count);
        Assert.Equal(1481, world.Trees.Count);
        Assert.Equal(1491, world.SpatialEntryCount);
        Assert.Equal(actors.Reverse(), world.InitializedThingsNewestFirst.Take(10));
        Assert.Equal(world.Trees.Reverse(), world.InitializedThingsNewestFirst.Skip(10));
        Assert.Equal(actors.Take(4).Reverse(), world.NamedActorsNewestFirst);
        Assert.Equal(actors.Take(4).Reverse(), world.UnitsNewestFirst);
        Assert.Equal(actors.Take(4), world.FactionUnits(0));
        Assert.Empty(world.FactionUnits(1));
        Assert.Equal(3, world.UnitCount(0, 7));
        Assert.Equal(1, world.UnitCount(0, 4));
        Assert.Equal(actors.Reverse(), world.OccupancyCandidatesNewestFirst);
        Assert.Equal(new[] { 1,4,5,6,8 }.Select(index => actors[index]), world.BigThingsOldestFirst);
        Assert.Equal(64, world.SegmentsNewestFirst.Count());
        Assert.Equal(0, world.WorldMeshCatalogCount);
        Assert.All(actors, actor =>
        {
            Assert.Equal(world.ActorWorldIdentities[actor.ActorId], actor.Identity);
            Assert.Same(actor, actor.MapEntry.Owner);
            Assert.True(actor.MapEntry.IsRegistered);
            Assert.Same(actor.ActorState.RetailPoses, world.Actors.GetBaseState(actor.ActorId).RetailPoses);
        });
        Assert.False(world.OccupancyActive);
        Assert.All(world.OccupancyBitplanes, plane => Assert.All(plane, value => Assert.Equal(255, value)));
    }

    [Fact]
    public void InactiveSat_KeepsSharedWeaponOwnersAndLooksUpAnimationByMode()
    {
        var world = RetailWorld110InitialConstruction.CreateThroughInitialIcebergs(123456);
        var cannon = Assert.IsType<RetailWorld110Cannon>(world.InitializedActors[3]);
        Assert.Equal("Turret 03", cannon.Input.Actor.Name);
        Assert.Equal(0, cannon.ActiveWord);
        Assert.False(world.Actors.GetActor(cannon.ActorId).Active);
        Assert.Equal(0xc0840233u, cannon.ThingTypeMask);
        Assert.Equal(new RetailMapWhoSector(31,32,4), cannon.MapEntry.Sector);
        Assert.Equal(1, cannon.InitialRejectedPeerCount);
        Assert.Equal(0, cannon.InitialRejectedByPeerMaskCount);
        Assert.Equal(unchecked((int)0xc1199926), cannon.PositionFloatBits.Z);
        Assert.Equal(cannon.ActorState.RetailPoses!.Current, cannon.ActorState.RetailPoses.Old);
        Assert.Equal(0, cannon.FireControlEnabledWord);
        Assert.Equal(RetailUnitAiKind.Warspite, cannon.Ai.Kind);
        Assert.Equal(0, cannon.RepairAiFlagWord);
        Assert.Equal(1, cannon.State260);
        Assert.Equal(0, cannon.State264);
        Assert.Equal(0, cannon.WaterFlagWord);
        Assert.Equal(0, cannon.Field100FloatBits);
        Assert.Equal(0, cannon.Field104FloatBits);
        Assert.Equal(0, cannon.Field108FloatBits);
        Assert.Equal(0, cannon.FieldF4FloatBits);
        Assert.Equal(default, cannon.Fields12CTo134);
        Assert.Same(cannon, cannon.TerrainGuide.Owner);
        Assert.Equal(cannon.PositionFloatBits, cannon.TerrainGuide.PositionFloatBits);
        Assert.Same(cannon, cannon.MotionController.Owner);
        Assert.True(cannon.MotionController.UsesOwnerRenderInterface);
        Assert.Equal(cannon.MotionControllerIdentity, cannon.MotionController.Identity);
        Assert.Equal(unchecked((int)0xc479c000), cannon.MotionController.Field0CFloatBits);
        Assert.Equal(unchecked((int)0xc479c000), cannon.MotionController.Field10FloatBits);
        Assert.Empty(world.Readers.ReadersNewestFirst(cannon.Identity)); // Direct owner references.
        Assert.All(new[] { cannon.Ai.ReaderCell0C, cannon.Ai.TargetReaderCell24, cannon.Ai.SpawnedByReaderCell28 },
            reader => { Assert.True(world.Readers.ContainsReaderCell(reader)); Assert.Null(world.Readers.TargetOf(reader)); });

        Assert.Equal(21, cannon.Mesh.FrameCount);
        Assert.Equal(16, cannon.Mesh.Parts.Count);
        Assert.Equal(4, cannon.Mesh.Animations.Count);
        Assert.Equal("Inactive", cannon.Animation.Definition!.Name);
        Assert.Equal(1003, cannon.AnimationMode); // CAMD mode ID is not physical index 3.
        Assert.Equal(3, cannon.Animation.RealIndex);
        Assert.Same(cannon.Mesh.Animations[3], cannon.Animation.Definition);
        Assert.Equal(0, cannon.AnimationFrame);
        Assert.True(cannon.AnimationForceLoop);
        Assert.Equal(1, cannon.AnimationIncrement); // Authored rate 0 is clamped by SetAnim.
        Assert.Equal(0, cannon.Animation.Definition.IncrementFloatBits);

        var weapon = Assert.Single(cannon.Weapons);
        Assert.Same(cannon, weapon.Owner);
        Assert.Equal("SAT Launcher", weapon.Definition.DefinitionName);
        Assert.Equal(88, weapon.Definition.TypeOrdinal);
        Assert.Equal(50, weapon.CurrentMode.TypeOrdinal);
        Assert.Same(weapon.Definition.SelectedMode, weapon.CurrentMode);
        Assert.Equal(new[] {50,-1,-1,-1,-1}, weapon.ChargeState.Levels);
        Assert.Equal(2, weapon.ChargeState.ChargeRate);
        Assert.Equal(1, weapon.Definition.AdjustAimWord);
        Assert.Equal(0x400u, weapon.Use.RawCreationFlags);
        Assert.Equal(1, weapon.TagIndex);
        Assert.Equal(1, weapon.UnitTagIndex);
        Assert.Equal(1, weapon.ActiveWord); // Inactive Unit does not deactivate its new weapon.
        Assert.Equal(0, weapon.Charge);
        Assert.Equal(-200, weapon.ReadyAtTime);
        Assert.False(weapon.HasTurretPart);
        Assert.False(weapon.HasBarrelPart); // Profile disables inspection despite GunA mesh emitters.
        Assert.Empty(cannon.Spawners);
        Assert.Same(cannon.PrimaryEffect, world.EffectHead);
        Assert.Same(weapon.Effect1C, cannon.PrimaryEffect.Next);
        Assert.Same(weapon.Effect14, weapon.Effect1C.Next);
        Assert.Same(world.Buildings[2].PrimaryEffect, weapon.Effect14.Next);
        int effects = 0;
        for (var link = world.EffectHead; link is not null; link = link.Next)
        { Assert.False(link.HasEffect); effects++; }
        Assert.Equal(8, effects);
    }

    [Fact]
    public void Icebergs_WaterClampPreservesAuthoredOldPoseAndRealSpatialOrder()
    {
        var world = RetailWorld110InitialConstruction.CreateThroughInitialIcebergs(123456);
        var features = world.InitializedActors.Skip(4).Cast<RetailWorld110Feature>().ToArray();
        Assert.Equal(new[] { "Iceberg 1", "Iceberg 2", "Iceberg 3", "Iceberg 4", "Iceberg 2", "Iceberg 4" },
            features.Select(feature => feature.Definition.DefinitionName));
        Assert.Equal(new[] { new RetailMapWhoSector(7,4,2), new(11,5,2), new(10,5,2),
            new(23,10,3), new(3,9,2), new(9,22,3) }, features.Select(feature => feature.MapEntry.Sector));
        Assert.Equal(new[] { 94,0,1,2,0,0 }, features.Select(feature => feature.InitialRejectedPeerCount));
        Assert.Equal(new[] { int.MinValue,int.MinValue,0,0,int.MinValue,int.MinValue },
            features.Select(feature => feature.ActorState.RetailPoses!.Old.PositionFloatBits.Z));
        foreach (var feature in features)
        {
            var authored = feature.Input.Actor.AuthoredTransform.RetailPositionFloatBits;
            var poses = feature.ActorState.RetailPoses!;
            Assert.Equal(0x3f947c52, BitConverter.SingleToInt32Bits(
                RetailWorldTerrain.SampleRetailHeight(world.Terrain.Heightfield, authored)));
            Assert.Equal(authored, poses.Old.PositionFloatBits);
            Assert.Equal(authored with { Z = unchecked((int)0xc10d70a4) }, poses.Current.PositionFloatBits);
            Assert.Equal(poses.Current.BasisFloatBits, poses.Old.BasisFloatBits);
            Assert.Equal(int.MinValue, poses.Current.BasisFloatBits.Row0Y);
            Assert.Equal(int.MinValue, poses.Current.BasisFloatBits.Row2X);
            Assert.Equal(0x80d00023u, feature.ThingTypeMask);
            Assert.Equal(0, feature.InitialRejectedByPeerMaskCount);
            Assert.Equal(2, feature.Allegiance);
            Assert.Equal(0, feature.WaterFlagWord); // Equal water is not below water.
            Assert.Equal(0, feature.FieldE0);
            Assert.Equal(0, feature.FieldF0);
            Assert.Equal(1, feature.Definition.InvincibleWord);
            Assert.Empty(feature.Input.Actor.Name);
            Assert.Equal(new[] { 2,4 }, feature.Definition.Fields.Select(field => field.FieldId));
            Assert.Equal(101, feature.Mesh.FrameCount);
            var part = Assert.Single(feature.Mesh.Parts);
            Assert.Equal(4, part.CachedPositionWords.Count);
            Assert.Equal(12, part.CachedOrientationWords.Count);
            Assert.Empty(feature.Mesh.Animations);
        }
    }

    [Fact]
    public void CollisionVolumes_UseTypeDependentCentresAndSeparateFloatStores()
    {
        var world = RetailWorld110InitialConstruction.CreateThroughInitialIcebergs(123456);
        // Independently calculated from pinned BBOX/HFLD inputs and pristine
        // GetCentrePos/426150 stores, before Building's later grounding copy.
        Level100FloatVector3Bits[] buildingCentres = [
            Words(0x4389adc3,0x4378a8eb,0xc1869d02), Words(0x43952e43,0x4384db91,0xc155cd15),
            Words(0x436648de,0x437dc484,0xc11b7067)];
        Level100FloatVector3Bits[] buildingOffsets = [
            Words(0xbd244000,0xbe461400,0xc0e741bc), Words(0xbee6f400,0x3db91000,0xc04e4c30),
            Words(0x3d0de000,0x3c908000,0xbea119a0)];
        Assert.Equal(buildingCentres, world.Buildings.Select(building => building.Collision.WorldCentreFloatBits));
        Assert.Equal(buildingOffsets, world.Buildings.Select(building => building.Collision.OwnerRelativeCentreFloatBits));
        var cannon = world.InitializedActors[3];
        Assert.Equal(0x2a1, cannon.CollisionFlags);
        Assert.True(cannon.Collision.ForceObb);
        Assert.False(cannon.Collision.FixedMeshTransforms);
        Assert.Equal(0x3fe61f94, cannon.Collision.RadiusFloatBits);
        Assert.Equal(0x404edcc2, cannon.Collision.RadiusSquaredFloatBits);
        var features = world.InitializedActors.Skip(4).ToArray();
        Assert.Equal(new[] { 0x4113ab60,0x4107bd9f,0x410773ff,0x40e05d73,0x4107bd9f,0x40e05d73 },
            features.Select(feature => feature.Collision.RadiusFloatBits));
        Assert.Equal(new[] { 0x42aa5c86,0x428ff314,0x428f5717,0x4244a3ab,0x428ff314,0x4244a3ab },
            features.Select(feature => feature.Collision.RadiusSquaredFloatBits));
        Assert.Equal(new uint[] { 0xc13a0cba,0xc1367be7,0xc13c35da,0xc1392ace,0xc1367be7,0xc1392ace },
            features.Select(feature => unchecked((uint)feature.Collision.WorldCentreFloatBits.Z)));
        Assert.Equal(new uint[] { 0xc0327058,0xc0242d0c,0xc03b14d8,0xc02ee8a8,0xc0242d0c,0xc02ee8a8 },
            features.Select(feature => unchecked((uint)feature.Collision.OwnerRelativeCentreFloatBits.Z)));
        foreach (var feature in features)
        {
            Assert.Equal(0xa9, feature.CollisionFlags);
            Assert.Equal(0x20u, feature.CollisionExclusionMask);
            Assert.False(feature.Collision.ForceObb);
            Assert.False(feature.Collision.FixedMeshTransforms);
            Assert.Equal(feature.PositionFloatBits.X, feature.Collision.WorldCentreFloatBits.X);
            Assert.Equal(feature.PositionFloatBits.Y, feature.Collision.WorldCentreFloatBits.Y);
            Assert.Equal(0, feature.Collision.OwnerRelativeCentreFloatBits.X);
            Assert.Equal(0, feature.Collision.OwnerRelativeCentreFloatBits.Y);
        }
        Assert.All(world.Buildings, building => Assert.True(building.Collision.FixedMeshTransforms));
        Assert.All(world.InitializedActors, actor =>
        {
            Assert.Same(actor, actor.Collision.Owner);
            Assert.Same(actor.Mesh, actor.Collision.Mesh);
            Assert.Equal(default, actor.Collision.MeshVolumeOffsetFloatBits);
            Assert.False(actor.Collision.IgnoreAnimationCollision);
            Assert.Equal(0, actor.CollisionFlags & 0x400); // Initial readiness remains undelivered.
        });
        Assert.Equal(40, world.InitializedActors.SelectMany(actor => new[] { actor.Identity,
            actor.Collision.Identity, actor.Collision.PrimarySphereIdentity, actor.Collision.MeshVolumeIdentity }).Distinct().Count());
    }

    [Fact]
    public void Prefix_ConsumesOneSharedDrawPerActorAndQueuesEventsInRetailOrder()
    {
        var world = RetailWorld110InitialConstruction.CreateThroughInitialIcebergs(123456);
        var random = new Level100ReleasedRandom(123456);
        for (int index = 0; index < 1491; index++) random.Next();
        Assert.Equal(random.Seed, world.ReleasedRandomSeed);
        Assert.Equal(1481, world.PendingTreeEvents);
        Assert.Equal(1513, world.PendingEvents);
        var cannon = Assert.IsType<RetailWorld110Cannon>(world.InitializedActors[3]);
        var admissions = world.Buildings.SelectMany(building => new[] { building.Collision.InitialEvent,
            building.MoveEvent, building.UnitEvent, building.Ai.InitialEvent, building.Animation.InitialEvent })
            .Concat(new[] { cannon.Collision.InitialEvent, cannon.MoveEvent, cannon.UnitEvent,
                cannon.Animation.InitialEvent, cannon.Ai.InitialEvent })
            .Concat(world.InitializedActors.Skip(4).SelectMany(feature => new[] { feature.Collision.InitialEvent, feature.MoveEvent }))
            .ToArray();
        Assert.Equal(Enumerable.Range(1481, 32), admissions.Select(admission => admission.Handle));
        Assert.All(admissions, admission => Assert.Equal(RetailEventPlacement.ImmediateBucket, admission.Placement));
        Assert.Equal(new[] { cannon.Collision.Identity,cannon.Identity,cannon.Identity,cannon.Animation.Identity,cannon.Ai.Identity },
            admissions.Skip(15).Take(5).Select(admission => world.Events!.ListenerOf(admission.Handle)));
        Assert.Equal(new short[] { 3000,3000,4003,3000,3000 },
            admissions.Skip(15).Take(5).Select(admission => world.Events!.EventNumOf(admission.Handle)));
        Assert.Equal(0u, cannon.Ai.InitialEvent.DueTimeBits);
        Assert.All(world.InitializedActors.Skip(4), feature =>
        {
            Assert.Equal(feature.Collision.Identity, world.Events!.ListenerOf(feature.Collision.InitialEvent.Handle));
            Assert.Equal(feature.Identity, world.Events.ListenerOf(feature.MoveEvent.Handle));
            Assert.Equal(BitConverter.SingleToUInt32Bits(0.0001f), feature.Collision.InitialEvent.DueTimeBits);
            Assert.Equal(BitConverter.SingleToUInt32Bits(0.0001f), feature.MoveEvent.DueTimeBits);
        });
        Assert.All(world.InitializedActors, actor =>
        { Assert.Equal(0, actor.MovePhase); Assert.Equal(new RetailActorMotionSnapshot(0, 1), actor.ActorState.RetailMotion); });
    }

    [Fact]
    public void IncompletePrefix_RejectsFrameRestoreHashAndLegacyDamageWithoutMutation()
    {
        var world = RetailWorld110InitialConstruction.CreateThroughInitialIcebergs(123456);
        var snapshot = world.Actors.Snapshot;
        int? seed = world.ReleasedRandomSeed;
        Assert.Throws<NotSupportedException>(() => world.AdvanceTreeReadinessEvents());
        Assert.Throws<NotSupportedException>(() => world.RestoreActors(snapshot));
        foreach (var actor in world.InitializedActors.Skip(3))
        {
            var before = world.Actors.GetActor(actor.ActorId);
            Assert.Throws<NotSupportedException>(() => world.Actors.SetHealth(actor.ActorId, 0));
            Assert.Throws<NotSupportedException>(() => world.Actors.ReportDied(actor.ActorId));
            Assert.Throws<NotSupportedException>(() => world.Actors.Deactivate(actor.ActorId));
            Assert.Equal(before, world.Actors.GetActor(actor.ActorId));
        }
        var envelope = new Simulation(1, Level100TestActorDefinitions.Create()).Snapshot;
        Assert.Throws<NotSupportedException>(() => StateHasher.ComputeHex(envelope with { Level100Actors = snapshot }));
        Assert.Equal(0, world.EventTime);
        Assert.Equal(1513, world.PendingEvents);
        Assert.Equal(seed, world.ReleasedRandomSeed);
        Assert.Equal(1491, world.SpatialEntryCount);
        Assert.All(world.Trees, tree => Assert.False(tree.CollisionReady));
    }

    private static Level100FloatVector3Bits Words(uint x, uint y, uint z) =>
        new(unchecked((int)x), unchecked((int)y), unchecked((int)z));
}
