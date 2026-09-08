// SPDX-License-Identifier: GPL-3.0-or-later

using System.Text.Json;
using OnslaughtRebuild.Core;
using OnslaughtRebuild.TestSupport;

namespace OnslaughtRebuild.Core.Tests;

public sealed class Level100ActorPlaneRuntimeTests
{
    [Fact]
    public void CreationOwnsIdleMovementBeforeAnyScriptCommand()
    {
        var definitions = Level100TestActorDefinitions.LoadMaterialized();
        var actors = new Level100ActorRegistry(definitions);
        var mechanics = new Level100ActorMechanics(actors, definitions);
        Level100ActorId id = actors.GetThingRef("Air Trainer")!.Value;
        ThingActorBaseStateSnapshot initial = actors.GetBaseState(id);
        Assert.NotNull(initial.RetailPlane);
        Assert.NotNull(mechanics.Snapshot.Actors.Single(actor => actor.ActorId == id).PlaneGuide);
        Assert.Equal(3, mechanics.Snapshot.PlaneEvents!.LiveEvents);
        Assert.True(mechanics.Snapshot.PlaneEvents.Float24Arithmetic);

        mechanics.AdvanceTick();
        ThingActorBaseStateSnapshot first = actors.GetBaseState(id);
        Assert.Equal(initial.RetailPoses!.Current.PositionFloatBits, first.RetailPoses!.Current.PositionFloatBits);
        Assert.Equal(initial.RetailPoses.Current, first.RetailPoses.Old);
        Assert.NotEqual(default, first.RetailPlane!.Drive);
        Assert.Equal(0x3d4ccccd, first.RetailMotion!.LastMoveTimeFloatBits);
        // Clearance is filled AFTER this first Move, not injected before it.
        Assert.Equal(0x40c51eb8, mechanics.Snapshot.Actors.Single(actor => actor.ActorId == id)
            .PlaneGuide!.ClearanceFloatBits);
        Assert.Equal(3u, mechanics.Snapshot.PlaneEvents!.ProcessedThisUpdate);

        mechanics.AdvanceTick();
        Assert.NotEqual(first.RetailPoses.Current.PositionFloatBits,
            actors.GetBaseState(id).RetailPoses!.Current.PositionFloatBits);
        Assert.Equal(0, mechanics.Snapshot.LastConsumedCommandSequence);
    }

    [Fact]
    public void StopClearsGuideAndDriveWithoutDestroyingRetainedVelocity()
    {
        var definitions = Level100TestActorDefinitions.LoadMaterialized();
        var actors = new Level100ActorRegistry(definitions);
        var mechanics = new Level100ActorMechanics(actors, definitions);
        Level100ActorId id = actors.GetThingRef("Air Trainer")!.Value;
        mechanics.AdvanceTick(); mechanics.AdvanceTick();
        ThingActorBaseStateSnapshot before = actors.GetBaseState(id);
        mechanics.ApplyCommand(new(1, 0, id, Level100ActorScriptCommandKind.Stop, null, null, 0));
        ThingActorBaseStateSnapshot stopped = actors.GetBaseState(id);
        Assert.Equal(before.RetailPlane!.Velocity, stopped.RetailPlane!.Velocity);
        Assert.Equal(default, stopped.RetailPlane.Drive);
        Assert.Equal(before.RetailPoses, stopped.RetailPoses);
        Level100PlaneGuideSnapshot guide = mechanics.Snapshot.Actors.Single(actor => actor.ActorId == id).PlaneGuide!;
        Assert.Equal(0, guide.Mode);
        Assert.Equal(before.RetailPoses!.Current.PositionFloatBits, guide.Destination);
        mechanics.AdvanceTick();
        Assert.NotEqual(before.RetailPoses.Current.PositionFloatBits, actors.GetBaseState(id).RetailPoses!.Current.PositionFloatBits);
    }

    [Fact]
    public void RegistryAndMechanicsRestoreContinueRawFlightAndOrderedCallbacks()
    {
        var definitions = Level100TestActorDefinitions.LoadMaterialized();
        var actors = new Level100ActorRegistry(definitions);
        var mechanics = new Level100ActorMechanics(actors, definitions);
        Level100ActorId id = actors.GetThingRef("Air Trainer")!.Value;
        mechanics.ApplyCommand(new(1, 0, id, Level100ActorScriptCommandKind.FollowWaypoint,
            null, "Flyby Path", 0));
        for (int i = 0; i < 35; i++) mechanics.AdvanceTick();
        var restoredActors = new Level100ActorRegistry(definitions, actors.Snapshot);
        var restored = new Level100ActorMechanics(restoredActors, definitions, mechanics.Snapshot);
        for (int i = 0; i < 90; i++)
        {
            Assert.Equal(mechanics.AdvanceTick(), restored.AdvanceTick());
            Assert.Equal(actors.GetBaseState(id), restoredActors.GetBaseState(id));
            Assert.Equal(JsonSerializer.Serialize(mechanics.Snapshot), JsonSerializer.Serialize(restored.Snapshot));
        }
        Assert.Throws<ArgumentException>(() => new Level100ActorMechanics(restoredActors, definitions,
            restored.Snapshot with { PlaneEvents = null }));
        Assert.Throws<ArgumentException>(() => new Level100ActorMechanics(restoredActors, definitions,
            restored.Snapshot with { PlaneEvents = restored.Snapshot.PlaneEvents! with { Float24Arithmetic = false } }));
        Assert.Throws<ArgumentException>(() => new Level100ActorMechanics(restoredActors, definitions,
            restored.Snapshot with { Actors = restored.Snapshot.Actors.Select(actor => actor with { PlaneGuide = null }).ToArray() }));
    }

    [Fact]
    public void HashBindsSubprojectionMotionGuideCacheAndCallbackOrder()
    {
        var simulation = new Simulation(1, Level100TestActorDefinitions.LoadMaterialized());
        WorldSnapshot baseline = simulation.Snapshot;
        Level100ActorBaseStateSnapshot plane = baseline.Level100Actors.BaseStates.Single(item => item.State.RetailPlane is not null);
        string initial = StateHasher.ComputeHex(baseline);
        WorldSnapshot WithPhysical(ThingActorBaseStateSnapshot state) => baseline with
        {
            Level100Actors = baseline.Level100Actors with
            {
                BaseStates = baseline.Level100Actors.BaseStates.Select(item => item.ActorId == plane.ActorId ? item with { State = state } : item).ToArray(),
            },
        };
        foreach (int word in new[] { int.MinValue, 1 })
        {
            // -0 and the least positive subnormal both project to 0 mm.
            Assert.NotEqual(initial, StateHasher.ComputeHex(WithPhysical(plane.State with
            { RetailPlane = plane.State.RetailPlane! with { Velocity = new(word, 0, 0) } })));
            Assert.NotEqual(initial, StateHasher.ComputeHex(WithPhysical(plane.State with
            { RetailPlane = plane.State.RetailPlane! with { Drive = new(word, 0, 0) } })));
        }
        var shifted = plane.State.RetailPoses!.Current.PositionFloatBits with
        { Y = plane.State.RetailPoses.Current.PositionFloatBits.Y + 1 };
        var subMillimeter = plane.State with
        { RetailPoses = plane.State.RetailPoses with { Current = plane.State.RetailPoses.Current with { PositionFloatBits = shifted } } };
        Assert.Equal(plane.State.CurrentPose, new ThingActorBaseState(subMillimeter).Snapshot.CurrentPose);
        Assert.NotEqual(initial, StateHasher.ComputeHex(WithPhysical(subMillimeter)));
        Assert.NotEqual(initial, StateHasher.ComputeHex(baseline with
        {
            Level100ActorMechanics = baseline.Level100ActorMechanics with
            { Actors = baseline.Level100ActorMechanics.Actors.Select(actor => actor.PlaneGuide is null ? actor : actor with
                { PlaneGuide = actor.PlaneGuide with { ClearanceCellX = 1 } }).ToArray() },
        }));
        RetailEventSchedulerSnapshot events = baseline.Level100ActorMechanics.PlaneEvents!;
        Assert.NotEqual(initial, StateHasher.ComputeHex(baseline with
        {
            Level100ActorMechanics = baseline.Level100ActorMechanics with
            { PlaneEvents = events with { Float24Arithmetic = false } },
        }));
        Assert.NotEqual(initial, StateHasher.ComputeHex(baseline with
        {
            Level100ActorMechanics = baseline.Level100ActorMechanics with
            { PlaneEvents = events with { Lanes = events.Lanes.Select(lane => lane with { Handles = lane.Handles.Reverse().ToArray() }).ToArray() } },
        }));
        Assert.Throws<NotSupportedException>(() => StateHasher.ComputeHex(baseline with
        { Level100Mission = baseline.Level100Mission with { WorldNumber = 110 } }));
    }
}
