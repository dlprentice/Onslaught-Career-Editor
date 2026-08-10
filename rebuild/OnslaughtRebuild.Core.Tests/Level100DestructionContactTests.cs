// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.TestSupport;

namespace OnslaughtRebuild.Core.Tests;

public sealed class Level100DestructionContactTests
{
    [Fact]
    public void CatalogRetainsExactLevel100DefinitionsWithoutCreatingActors()
    {
        Level100ContactCatalog catalog = Level100ContactCatalog.Instance;

        Assert.Equal(28, catalog.Definitions.Count);
        Assert.Equal(70, catalog.PulseRound.RadiusMillimeters);
        Assert.Equal("Mech Pulse Hit Medium", catalog.PulseRound.ImpactPhysicsDefinition);
        Assert.Equal(
            "Mech Pulse Bolt Explosion Medium",
            catalog.PulseRound.ImpactParticleDescriptor);
        Assert.Equal("Explosion Small", catalog.PulseRound.ImpactSoundDescriptor);

        Level100ContactDefinition tank = catalog.GetDefinition("Target Tank");
        Assert.Equal(Level100DefinitionKind.TargetTank, tank.Kind);
        Assert.Equal(0x40C00000u, tank.MaximumLifeBits);
        Assert.Equal(7, tank.PartCount);
        Assert.Equal("Tank Explosion Medium", tank.DestructionPhysicsDefinition);
        Assert.Equal("Tank Explosion Medium", tank.DestructionParticleDescriptor);
        Assert.Equal("Explosion Medium", tank.DestructionSoundDescriptor);

        // Target Truck decodes from the shipped `m_f_truck_training.msh.aya`
        // (sha256 3bd92ce9...96c5): one collidable CMSH part `Mesh01` with
        // 306 vertices and 432 triangles, half-extents (525, 1510, 287) mm
        // about centre (-4, -50, -475). Life 3.0 (0x40400000) and the
        // destruction record are read from `Unit / Target Truck` at 0x24d9e in
        // `default physics.dat`. No part of this volume is authored here.
        Level100ContactDefinition truck = catalog.GetDefinition("Target Truck");
        Assert.Equal(Level100DefinitionKind.TargetTank, truck.Kind);
        Assert.Equal(0x40400000u, truck.MaximumLifeBits);
        Assert.Equal("m_f_truck_training.msh.aya", truck.Mesh);
        Assert.Equal(1, truck.PartCount);
        Assert.Equal("Mesh01", truck.Parts[0].Name);
        Assert.True(truck.Parts[0].Collidable);
        Assert.Equal(306 * 3, truck.Parts[0].VerticesMillimeters.Length);
        Assert.Equal(432 * 3, truck.Parts[0].Triangles.Length);
        Assert.Equal(
            new Level100Vector3(525, 1_510, 287),
            truck.Parts[0].HalfExtents);
        Assert.Equal(new Level100Vector3(-4, -50, -475), truck.Parts[0].Center);
        Assert.Equal("Tank Explosion Medium", truck.DestructionPhysicsDefinition);
        Assert.Equal("Tank Explosion Medium", truck.DestructionParticleDescriptor);
        Assert.Equal("Explosion Medium", truck.DestructionSoundDescriptor);

        // Target Drone decodes from the shipped `m_FA_F24_training.msh.aya`
        // (sha256 48876552...6ec5): 12 CMSH parts of which exactly one,
        // `Object03`, is collidable, with half-extents (519, 1416, 185) mm
        // about centre (-5, 323, -26). Life 1.0 (0x3F800000) and the
        // destruction record `Drone Explosion` (@0x5df9) come from
        // `Unit / Target Drone` at record 0x24e76 in `default physics.dat`.
        // The mesh names three of its non-collidable parts `GUNA`, `GUNA` and
        // `GUNB`, which is the mesh's own corroboration of the record's two
        // `CUnitUse` weapon slots. Nothing here is authored.
        Level100ContactDefinition drone = catalog.GetDefinition("Target Drone");
        Assert.Equal(Level100DefinitionKind.TargetDrone, drone.Kind);
        Assert.Equal(0x3F800000u, drone.MaximumLifeBits);
        Assert.Equal("m_FA_F24_training.msh.aya", drone.Mesh);
        Assert.Equal(12, drone.PartCount);
        Assert.Equal("Object03", drone.Parts[0].Name);
        Assert.True(drone.Parts[0].Collidable);
        Assert.Single(drone.Parts, part => part.Collidable);
        Assert.Equal(
            new Level100Vector3(519, 1_416, 185),
            drone.Parts[0].HalfExtents);
        Assert.Equal(new Level100Vector3(-5, 323, -26), drone.Parts[0].Center);
        Assert.Equal("Drone Explosion", drone.DestructionPhysicsDefinition);
        Assert.Equal(
            "Drone Explosion Effect",
            drone.DestructionParticleDescriptor);
        // The divergence that used to make this definition unrepresentable:
        // `Drone Explosion` field 6 (CExplosionWaterEffect) is a different
        // descriptor from fields 2/5/7. The schema now carries it.
        Assert.Equal(
            "Water Explosion Small",
            drone.DestructionWaterParticleDescriptor);
        Assert.Equal("Explosion Small", drone.DestructionSoundDescriptor);
        Assert.Equal(
            "Tank Explosion Medium",
            truck.DestructionWaterParticleDescriptor);

        Level100ContactDefinition warehouse = catalog.GetDefinition("Warehouse");
        Assert.Equal(Level100DefinitionKind.Warehouse, warehouse.Kind);
        Assert.Equal(0x42480000u, warehouse.MaximumLifeBits);
        Assert.Equal(28, warehouse.PartCount);
        Assert.Equal(-1, warehouse.Parts[0].Parent);
    }

    [Fact]
    public void SweptSphereUsesMeshNarrowphaseAfterBboxBroadphase()
    {
        Level100ContactDefinition tank =
            Level100ContactCatalog.Instance.GetDefinition("Target Tank");
        var actors = new[]
        {
            new Level100ContactActor(
                41,
                active: true,
                Level100Transform3.Identity,
                Level100Vector3.Zero,
                tank),
        };

        Assert.True(Level100ContactMechanics.TrySweepPulse(
            new Level100Vector3(0, 0, -2_000),
            new Level100Vector3(0, 0, 1_000),
            actors,
            out Level100ContactHit hit));
        Assert.Equal(41, hit.ActorId);
        Assert.Equal(Level100ContactSurfaceKind.Mesh, hit.SurfaceKind);
        Assert.InRange(hit.PartIndex, 0, 2);
        Assert.InRange(hit.TimePartsPerMillion, 1, 999_999);

        var destruction = new Level100DestructionState(41, tank);
        var destructionEvents = new Level100DestructionEvent[
            Level100DestructionState.MaximumEventsPerHit];
        destruction.ApplyPulseHit(
            hit,
            destructionEvents);
        Assert.Equal(0x40866666u, destruction.CurrentLifeBits);

        var disabled = new byte[tank.PartCount];
        actors[0] = new Level100ContactActor(
            41,
            active: true,
            Level100Transform3.Identity,
            Level100Vector3.Zero,
            tank,
            partActivity: disabled);
        Assert.False(Level100ContactMechanics.TrySweepPulse(
            new Level100Vector3(0, 0, -2_000),
            new Level100Vector3(0, 0, 1_000),
            actors,
            out _));

        actors[0] = new Level100ContactActor(
            41,
            active: true,
            Level100Transform3.Identity,
            Level100Vector3.Zero,
            tank);

        // This ray traverses the tank-body BBOX corner but no retained
        // triangle. A broadphase-only implementation reports a false hit.
        Assert.False(Level100ContactMechanics.TrySweepPulse(
            new Level100Vector3(800, 730, -2_000),
            new Level100Vector3(800, 730, 1_000),
            actors,
            out _));
    }

    [Fact]
    public void DownwardPulseUsesRetainedTerrainSamplerWithoutMarching()
    {
        Assert.True(Level100ContactMechanics.TrySweepPulseAgainstTerrain(
            new Level100Vector3(0, 0, -2_000),
            new Level100Vector3(0, 0, 2_000),
            out Level100ContactHit hit));

        Assert.Equal(Level100ContactSurfaceKind.Terrain, hit.SurfaceKind);
        Assert.Equal(-211, hit.SurfacePoint.Z);
        Assert.Equal(-281, hit.ImpactCenter.Z);
        Assert.Equal(429_625, hit.TimePartsPerMillion);
        Assert.True(hit.NormalPartsPerMillion.Z < 0);
    }

    [Fact]
    public void TerrainSweepFindsSamplerRidgeBetweenClearEndpoints()
    {
        var start = new Level100Vector3(16_000, 94_000, -7_140);
        var end = new Level100Vector3(17_000, 94_000, -7_140);

        Assert.False(Level100ContactMechanics.TrySweepPulseAgainstTerrain(
            start,
            start,
            out _));
        Assert.False(Level100ContactMechanics.TrySweepPulseAgainstTerrain(
            end,
            end,
            out _));
        Assert.True(Level100ContactMechanics.TrySweepPulseAgainstTerrain(
            start,
            end,
            out Level100ContactHit hit));
        Assert.Equal(Level100ContactSurfaceKind.Terrain, hit.SurfaceKind);
        Assert.InRange(hit.TimePartsPerMillion, 1, 999_999);
    }

    [Fact]
    public void ExternalActorContractRejectsInvalidIdentityBasisAndPart()
    {
        Level100ContactDefinition tank =
            Level100ContactCatalog.Instance.GetDefinition("Target Tank");

        Assert.Throws<ArgumentOutOfRangeException>(() =>
            new Level100ContactActor(
                0,
                active: true,
                Level100Transform3.Identity,
                Level100Vector3.Zero,
                tank));
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            new Level100ContactActor(
                1,
                active: true,
                default,
                Level100Vector3.Zero,
                tank));

        var state = new Level100DestructionState(1, tank);
        var events = new Level100DestructionEvent[
            Level100DestructionState.MaximumEventsPerHit];
        Assert.Throws<ArgumentOutOfRangeException>(() => state.ApplyPulseHit(
            Hit(1, tank.PartCount),
            events));
    }

    [Fact]
    public void WarehouseUsesExtentWeightsAndDetachesOnlyTheHitSegment()
    {
        Level100ContactDefinition warehouse =
            Level100ContactCatalog.Instance.GetDefinition("Warehouse");
        var state = new Level100DestructionState(101, warehouse);
        var events = new Level100DestructionEvent[
            Level100DestructionState.MaximumEventsPerHit];

        Assert.Equal(0u, state.GetInitialSegmentHealthBits(0));
        Assert.Equal(0x4196959Eu, state.GetInitialSegmentHealthBits(1));
        Assert.Equal(0x3ED1CE4Fu, state.GetInitialSegmentHealthBits(19));

        Level100ContactHit chimneyHit = Hit(101, 19);
        int count = state.ApplyPulseHit(
            chimneyHit,
            events);

        Assert.Equal(3, count);
        Assert.Equal(
            new[]
            {
                Level100DestructionEventKind.PulseImpact,
                Level100DestructionEventKind.SegmentDamaged,
                Level100DestructionEventKind.SegmentDetached,
            },
            events.AsSpan(0, count).ToArray().Select(item => item.Kind));
        Assert.Equal(0, state.ContactPartActivity.Span[19]);
        Assert.Equal(1, state.ContactPartActivity.Span[20]);
        Assert.False(state.Terminal);
    }

    [Fact]
    public void WarehouseTerminalIsCoreChildOrThirtyPercentNotSyntheticHull()
    {
        Level100ContactDefinition warehouse =
            Level100ContactCatalog.Instance.GetDefinition("Warehouse");
        var state = new Level100DestructionState(102, warehouse);
        var events = new Level100DestructionEvent[
            Level100DestructionState.MaximumEventsPerHit];
        Level100ContactHit coreHit = Hit(102, 1);

        for (int hitIndex = 0; hitIndex < 10; hitIndex++)
        {
            state.ApplyPulseHit(
                coreHit,
                events);
            Assert.False(state.Terminal);
            Assert.Equal(1, state.ContactPartActivity.Span[1]);
        }

        int terminalCount = state.ApplyPulseHit(
            coreHit,
            events);

        Assert.True(state.Terminal);
        Assert.Equal(0, state.ContactPartActivity.Span[1]);
        Assert.Equal(1, state.ContactPartActivity.Span[2]);
        Assert.Contains(
            events.AsSpan(0, terminalCount).ToArray(),
            item => item.Kind == Level100DestructionEventKind.Terminal &&
                item.EffectKind ==
                    Level100DestructionEffectKind.FacilityDestroyed);
    }

    [Fact]
    public void WarehouseAlsoTerminatesBelowThirtyPercentWithCoreIntact()
    {
        Level100ContactDefinition warehouse =
            Level100ContactCatalog.Instance.GetDefinition("Warehouse");
        var state = new Level100DestructionState(103, warehouse);
        var events = new Level100DestructionEvent[
            Level100DestructionState.MaximumEventsPerHit];

        for (int partIndex = 2; partIndex < warehouse.PartCount && !state.Terminal; partIndex++)
        {
            Level100ContactHit hit = Hit(103, partIndex);
            while (state.ContactPartActivity.Span[partIndex] != 0 && !state.Terminal)
            {
                state.ApplyPulseHit(
                    hit,
                    events);
            }
        }

        Assert.True(state.Terminal);
        Assert.Equal(1, state.ContactPartActivity.Span[1]);
        Assert.NotEqual(0u, state.GetCurrentSegmentHealthBits(1));
    }

    [Fact]
    public void TargetTankEmitsTypedImpactAndTerminalEffects()
    {
        Level100ContactDefinition tank =
            Level100ContactCatalog.Instance.GetDefinition("Target Tank");
        var state = new Level100DestructionState(201, tank);
        var events = new Level100DestructionEvent[
            Level100DestructionState.MaximumEventsPerHit];
        Level100ContactHit hit = Hit(201, 0);

        for (int hitIndex = 0; hitIndex < 3; hitIndex++)
        {
            state.ApplyPulseHit(hit, events);
            Assert.False(state.Terminal);
        }
        int count = state.ApplyPulseHit(hit, events);

        Assert.True(state.Terminal);
        Assert.Equal(0xBF99999Au, state.CurrentLifeBits);
        Assert.Contains(
            events.AsSpan(0, count).ToArray(),
            item => item.Kind == Level100DestructionEventKind.PulseImpact &&
                item.EffectKind == Level100DestructionEffectKind.PulseImpact);
        Assert.Contains(
            events.AsSpan(0, count).ToArray(),
            item => item.Kind == Level100DestructionEventKind.Terminal &&
                item.EffectKind ==
                    Level100DestructionEffectKind.TargetDestroyed);
    }

    [Fact]
    public void WholeBodyLifeRequiresStrictlyNegativeRemainingLifeToBecomeTerminal()
    {
        Level100ContactDefinition tank =
            Level100ContactCatalog.Instance.GetDefinition("Target Tank");
        var state = new Level100DestructionState(202, tank);
        var events = new Level100DestructionEvent[
            Level100DestructionState.MaximumEventsPerHit];
        Level100ContactHit hit = Hit(202, 0);
        Assert.Equal(0x40C00000u, tank.MaximumLifeBits);

        int zeroCount = state.ApplyRoundHit(
            hit,
            tank.MaximumLifeBits,
            Level100DestructionEffectKind.PulseImpact,
            events);

        Assert.Equal(0x00000000u, state.CurrentLifeBits);
        Assert.False(state.Terminal);
        Assert.DoesNotContain(
            events.AsSpan(0, zeroCount).ToArray(),
            item => item.Kind == Level100DestructionEventKind.Terminal);

        int negativeCount = state.ApplyRoundHit(
            hit,
            0x3F800000u,
            Level100DestructionEffectKind.PulseImpact,
            events);

        Assert.Equal(0xBF800000u, state.CurrentLifeBits);
        Assert.True(state.Terminal);
        Assert.Contains(
            events.AsSpan(0, negativeCount).ToArray(),
            item => item.Kind == Level100DestructionEventKind.Terminal);
    }

    [Fact]
    public void ApplyDamageTraceVectorPreservesExactOverkillBits()
    {
        // Existing-trace reproof a0bd86d8... observes CUnit__ApplyDamage at
        // 0x004F9A90 store life 0x3BA3D70B -> 0xC479FFAE for amount
        // 0x447A0000 (1000.0f). The actor's shield was already zero, so this
        // pins the whole-body life arithmetic and terminal edge only; it does
        // not claim positive-shield absorption.
        Level100ContactDefinition tank =
            Level100ContactCatalog.Instance.GetDefinition("Target Tank");
        var state = new Level100DestructionState(203, tank);
        Level100DestructionSnapshot baseline = state.CaptureSnapshot();
        state.Restore(new Level100DestructionSnapshot(
            baseline.ActorId,
            baseline.DefinitionName,
            currentLifeBits: 0x3BA3D70Bu,
            terminal: false,
            belowHalfReported: false,
            baseline.InitialHealthBits.ToArray(),
            baseline.CurrentHealthBits.ToArray(),
            baseline.PartActivity.ToArray()));
        var events = new Level100DestructionEvent[
            Level100DestructionState.MaximumEventsPerHit];

        int count = state.ApplyRoundHit(
            Hit(203, 0),
            damageBits: 0x447A0000u,
            Level100DestructionEffectKind.PulseImpact,
            events);

        Assert.Equal(0xC479FFAEu, state.CurrentLifeBits);
        Assert.True(state.Terminal);
        Assert.Contains(
            events.AsSpan(0, count).ToArray(),
            item => item.Kind == Level100DestructionEventKind.SegmentDamaged &&
                item.RemainingHealthBits == 0xC479FFAEu);
        Assert.Contains(
            events.AsSpan(0, count).ToArray(),
            item => item.Kind == Level100DestructionEventKind.Terminal);
    }

    [Fact]
    public void RuntimeConsumesRegistryPoseAndReportsReleasedLifecycleFacts()
    {
        Level100ActorDefinitionSet definitions = Level100TestActorDefinitions.Create();
        var registry = new Level100ActorRegistry(definitions);
        var runtime = new Level100DestructionRuntime(registry);
        Level100ActorId actorId = Assert.IsType<Level100ActorId>(
            registry.GetThingRef("Target Tank 2"));
        Level100ActorSnapshot authored = registry.GetActor(actorId);
        var pose = new Level100ActorPoseSnapshot(
            new SimVector3(1_000, 3_000, 2_000),
            IdentityFloatBasis(),
            new SimVector3(100, 0, 0),
            new SimVector3(0, 25_000, 0));
        registry.SetPose(actorId, pose);

        // Contact-local sweep is (0,0,-2000)->(0,0,1000). Core's vertical
        // axis is up, so the target remains above terrain while the released
        // contact path receives its native Z-down coordinates.
        var start = new SimVector3(1_000, 5_000, 2_000);
        var end = new SimVector3(1_000, 2_000, 2_000);
        for (int hitIndex = 0; hitIndex < 4; hitIndex++)
        {
            Assert.True(runtime.TryApplyPulseSweep(start, end, out Level100ContactHit hit));
            Assert.Equal(actorId.Value, hit.ActorId);
            Assert.Equal(Level100ContactSurfaceKind.Mesh, hit.SurfaceKind);
        }

        Level100ActorSnapshot destroyed = registry.GetActor(actorId);
        Assert.Equal(authored.DefinitionIdentity, destroyed.DefinitionIdentity);
        Assert.Equal(authored.MeshBinding, destroyed.MeshBinding);
        Assert.Equal(pose, destroyed.Pose);
        Assert.Equal(0, destroyed.Health);
        Assert.False(destroyed.Active);
        Assert.Equal(Level100ActorLifecycle.Destroyed, destroyed.Lifecycle);
        Assert.Equal(
            new[]
            {
                Level100ActorFactKind.Hit,
                Level100ActorFactKind.Hit,
                Level100ActorFactKind.Hit,
                Level100ActorFactKind.Hit,
                Level100ActorFactKind.StartedDying,
                Level100ActorFactKind.Died,
            },
            registry.Snapshot.PendingFacts.Select(fact => fact.Kind));

        Level100DestructionSnapshot component = runtime.Snapshot.Actors.Single(
            item => item.ActorId == actorId.Value);
        Assert.True(component.Terminal);
        Assert.Contains(
            runtime.Events,
            item => item.ActorId == actorId.Value &&
                item.Kind == Level100DestructionEventKind.Terminal);

        WorldSnapshot envelope = new Simulation(0x100u, definitions).Snapshot;
        Assert.NotEqual(
            StateHasher.ComputeHex(envelope),
            StateHasher.ComputeHex(envelope with
            {
                Level100Destruction = runtime.Snapshot,
                Level100DestructionEvents = runtime.Events,
            }));
    }

    [Fact]
    public void NearerStaticGeometryOccludesDestructibleActorWithoutDamage()
    {
        Level100ActorDefinitionSet definitions = Level100TestActorDefinitions.Create();
        var registry = new Level100ActorRegistry(definitions);
        var runtime = new Level100DestructionRuntime(registry);
        Level100ActorId facilityId = Assert.IsType<Level100ActorId>(
            registry.GetThingRef("Control Tower"));
        Level100ActorId targetId = Assert.IsType<Level100ActorId>(
            registry.GetThingRef("Target Tank 2"));

        registry.SetPose(
            facilityId,
            new Level100ActorPoseSnapshot(
                new SimVector3(0, 4_000, 0),
                IdentityFloatBasis(),
                SimVector3.Zero,
                SimVector3.Zero));
        registry.SetPose(
            targetId,
            new Level100ActorPoseSnapshot(
                new SimVector3(0, 2_000, 0),
                IdentityFloatBasis(),
                SimVector3.Zero,
                SimVector3.Zero));
        Level100ActorSnapshot facilityBefore = registry.GetActor(facilityId);
        Level100ActorSnapshot targetBefore = registry.GetActor(targetId);

        Assert.True(runtime.TryApplyPulseSweep(
            new SimVector3(0, 6_000, 0),
            new SimVector3(0, 1_000, 0),
            out Level100ContactHit hit));

        Assert.Equal(facilityId.Value, hit.ActorId);
        Assert.Equal(Level100ContactSurfaceKind.Mesh, hit.SurfaceKind);
        Assert.Equal(facilityBefore, registry.GetActor(facilityId));
        Assert.Equal(targetBefore, registry.GetActor(targetId));
        // The occluding static takes no damage, but it does now observe the
        // released THING_TYPE_AMMUNITION contact: `CThing::Hit` dispatches to
        // the attached script whether or not the thing is destructible, and
        // Facilities.msl / TankFactory.msl / Turret.msl all define
        // `hit(otherThing)`. Without this fact `Hit Friendly Building` and
        // `Broke Tutorial` can never be posted. This assertion was
        // `Assert.Empty` while that route was missing.
        Level100ActorFactSnapshot hitFact =
            Assert.Single(registry.Snapshot.PendingFacts);
        Assert.Equal(Level100ActorFactKind.Hit, hitFact.Kind);
        Assert.Equal(facilityId, hitFact.ActorId);
        Assert.Equal(
            Level100ReleasedThingTypeMasks.Ammunition,
            hitFact.OtherThingTypeMask);
        Level100DestructionEvent impact = Assert.Single(runtime.Events);
        Assert.Equal(Level100DestructionEventKind.PulseImpact, impact.Kind);
        Assert.Equal(Level100DestructionEffectKind.PulseImpact, impact.EffectKind);
        Assert.Equal(facilityId.Value, impact.ActorId);
    }

    [Fact]
    public void TerrainContactEmitsImpactWithoutRegistryMutation()
    {
        Level100ActorDefinitionSet definitions = Level100TestActorDefinitions.Create();
        var registry = new Level100ActorRegistry(definitions);
        var runtime = new Level100DestructionRuntime(registry);
        Level100ActorRegistrySnapshot before = registry.Snapshot;

        Assert.True(runtime.TryApplyPulseSweep(
            new SimVector3(0, 2_000, 0),
            new SimVector3(0, -2_000, 0),
            out Level100ContactHit hit));

        Assert.Equal(0, hit.ActorId);
        Assert.Equal(Level100ContactSurfaceKind.Terrain, hit.SurfaceKind);
        Level100DestructionEvent impact = Assert.Single(runtime.Events);
        Assert.Equal(Level100DestructionEventKind.PulseImpact, impact.Kind);
        Assert.Equal(Level100DestructionEffectKind.PulseImpact, impact.EffectKind);
        Assert.Equal(0, impact.ActorId);
        Assert.Equal(-1, impact.PartIndex);
        Assert.Equal(hit.SurfacePoint, impact.Position);

        Level100ActorRegistrySnapshot after = registry.Snapshot;
        Assert.Equal(before.NextActorId, after.NextActorId);
        Assert.Equal(before.NextFactSequence, after.NextFactSequence);
        Assert.Equal(before.Actors.ToArray(), after.Actors.ToArray());
        Assert.Equal(before.PendingFacts.ToArray(), after.PendingFacts.ToArray());

        var vulcanRuntime = new Level100DestructionRuntime(
            new Level100ActorRegistry(definitions));
        Assert.True(vulcanRuntime.TryApplyRoundSweep(
            new SimVector3(0, 2_000, 0),
            new SimVector3(0, -2_000, 0),
            Level100ContactMechanics.PulseRadiusMillimeters,
            Level100DestructionState.MechBulletDamageBits,
            Level100DestructionEffectKind.VulcanImpact,
            out _));
        Level100DestructionEvent vulcanImpact =
            Assert.Single(vulcanRuntime.Events);
        Assert.Equal(
            Level100DestructionEventKind.VulcanImpact,
            vulcanImpact.Kind);
        Assert.Equal(
            Level100DestructionEffectKind.VulcanImpact,
            vulcanImpact.EffectKind);
    }

    [Fact]
    public void DamagedAndTerminalRegistryDestructionSnapshotsRestoreAndHash()
    {
        AssertRegistryDestructionRoundTrip(hitCount: 1, expectedHealth: 4_200);
        AssertRegistryDestructionRoundTrip(hitCount: 4, expectedHealth: 0);
    }

    [Fact]
    public void MeshContactHotPathDoesNotAllocatePerQuery()
    {
        Level100ContactDefinition tank =
            Level100ContactCatalog.Instance.GetDefinition("Target Tank");
        var actors = new[]
        {
            new Level100ContactActor(
                401,
                active: true,
                Level100Transform3.Identity,
                Level100Vector3.Zero,
                tank),
        };
        Level100Vector3 start = new(0, 0, -2_000);
        Level100Vector3 end = new(0, 0, 1_000);
        Assert.True(Level100ContactMechanics.TrySweepPulse(
            start,
            end,
            actors,
            out _));

        long before = GC.GetAllocatedBytesForCurrentThread();
        for (int index = 0; index < 100; index++)
        {
            Assert.True(Level100ContactMechanics.TrySweepPulse(
                start,
                end,
                actors,
                out _));
        }
        long allocated = GC.GetAllocatedBytesForCurrentThread() - before;

        Assert.Equal(0, allocated);
    }

    private static Level100ContactHit Hit(int actorId, int partIndex) =>
        new(
            actorId,
            partIndex,
            Level100ContactSurfaceKind.Mesh,
            500_000,
            new Level100Vector3(0, 0, 0),
            new Level100Vector3(0, 0, 70),
            new Level100Vector3(0, 0, -1_000_000));

    private static void AssertRegistryDestructionRoundTrip(
        int hitCount,
        int expectedHealth)
    {
        Level100ActorDefinitionSet definitions =
            Level100TestActorDefinitions.Create();
        var registry = new Level100ActorRegistry(definitions);
        var runtime = new Level100DestructionRuntime(registry);
        Level100ActorId actorId = Assert.IsType<Level100ActorId>(
            registry.GetThingRef("Target Tank 2"));
        registry.SetPose(
            actorId,
            new Level100ActorPoseSnapshot(
                new SimVector3(1_000, 3_000, 2_000),
                IdentityFloatBasis(),
                SimVector3.Zero,
                SimVector3.Zero));

        for (int hitIndex = 0; hitIndex < hitCount; hitIndex++)
        {
            Assert.True(runtime.TryApplyPulseSweep(
                new SimVector3(1_000, 5_000, 2_000),
                new SimVector3(1_000, 2_000, 2_000),
                out _));
        }

        Level100ActorSnapshot actor = registry.GetActor(actorId);
        Assert.Equal(expectedHealth, actor.Health);
        Assert.Equal(
            hitCount == 4
                ? Level100ActorLifecycle.Destroyed
                : Level100ActorLifecycle.Alive,
            actor.Lifecycle);
        Assert.Equal(hitCount != 4, actor.Active);

        Level100ActorRegistrySnapshot registrySnapshot = registry.Snapshot;
        Level100DestructionRuntimeSnapshot destructionSnapshot = runtime.Snapshot;
        IReadOnlyList<Level100DestructionEvent> events = runtime.Events;
        var restoredRegistry = new Level100ActorRegistry(
            definitions,
            registrySnapshot);
        var restoredRuntime = new Level100DestructionRuntime(
            restoredRegistry,
            destructionSnapshot);
        Assert.Equal(expectedHealth, restoredRegistry.GetActor(actorId).Health);
        Assert.Equal(
            destructionSnapshot.Actors.Single(item =>
                item.ActorId == actorId.Value).Terminal,
            restoredRuntime.Snapshot.Actors.Single(item =>
                item.ActorId == actorId.Value).Terminal);

        WorldSnapshot envelope = new Simulation(0x100u, definitions).Snapshot;
        WorldSnapshot original = envelope with
        {
            Level100Actors = registrySnapshot,
            Level100Destruction = destructionSnapshot,
            Level100DestructionEvents = events,
        };
        WorldSnapshot restored = original with
        {
            Level100Actors = restoredRegistry.Snapshot,
            Level100Destruction = restoredRuntime.Snapshot,
        };
        Assert.Equal(
            StateHasher.ComputeHex(original),
            StateHasher.ComputeHex(restored));

        Level100ActorRegistrySnapshot mismatchedSnapshot =
            registrySnapshot with
            {
                Actors = registrySnapshot.Actors
                    .Select(item => item.ActorId == actorId
                        ? item with { Health = item.Health + 1 }
                        : item)
                    .ToArray(),
            };
        var mismatchedRegistry = new Level100ActorRegistry(
            definitions,
            mismatchedSnapshot);
        Assert.Throws<InvalidDataException>(() =>
            new Level100DestructionRuntime(
                mismatchedRegistry,
                destructionSnapshot));
    }

    private static Level100FloatBasis3Bits IdentityFloatBasis() => new(
        BitConverter.SingleToInt32Bits(1f), 0, 0,
        0, BitConverter.SingleToInt32Bits(1f), 0,
        0, 0, BitConverter.SingleToInt32Bits(1f));
}
