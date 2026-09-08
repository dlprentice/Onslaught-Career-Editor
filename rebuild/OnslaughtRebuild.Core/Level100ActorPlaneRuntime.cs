// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

/// <summary>Guide-owned state, separate from the Actor's physical pose.</summary>
public sealed record Level100PlaneGuideSnapshot(
    Level100FloatVector3Bits Destination, int Mode, int ClearanceFloatBits,
    int ClearanceCellX, int ClearanceCellY, int ControllerState, int SpeedMode);

public sealed partial class Level100ActorMechanics
{
    private RetailEventScheduler? _planeEvents;

    private void InitializePlanes()
    {
        foreach (Level100ActorSnapshot actor in _actors.Snapshot.Actors)
            RegisterSpawnedActor(actor.ActorId);
    }

    /// <summary>
    /// Called after allocation and before its script initializer. Move is
    /// queued before the two guide callbacks, including for an idle Plane.
    /// The isolated aircraft queue does not claim the complete world event,
    /// effect or random-consumer order.
    /// </summary>
    internal void RegisterSpawnedActor(Level100ActorId actorId)
    {
        ThingActorBaseStateSnapshot physical = _actors.GetBaseState(actorId);
        if (physical.RetailPlane is null) return;
        if (_states.ContainsKey(actorId.Value))
            throw new InvalidOperationException("Aircraft mechanics was already registered.");
        _planeEvents ??= new(useFloat24Arithmetic: true);
        // Actor Init consumes this draw even though the Plane divisor is 1.
        _ = _releasedRandom.Next();
        _states.Add(actorId.Value, new ActorState
        {
            ActorId = actorId, Intent = Level100ActorCommandIntent.Stopped,
            PlaneGuide = new(physical.RetailPoses!.Current.PositionFloatBits, 0, 0, 0, 0, 1, 0),
        });
        // The two cache coordinates are unwritten by native constructors.
        // Zero is the observed startup allocation in observe-plane-motion-a,
        // a declared deterministic seed here, not a universal allocator law.
        _planeEvents.AddEvent(3000, PlaneListener(actorId, 0), RetailEventScheduler.NextFrame);
        _planeEvents.AddEvent(2000, PlaneListener(actorId, 1), RetailEventScheduler.NextFrame);
        _planeEvents.AddEvent(2001, PlaneListener(actorId, 1), RetailEventScheduler.NextFrame);
    }

    internal void AdvanceEventClock(uint eventFrameCount)
    {
        if (_planeEvents is null) return;
        if (eventFrameCount != unchecked(_planeEvents.FrameCount + 1))
            throw new InvalidOperationException("Aircraft event clock cannot skip or repeat a frame.");
        _planeEvents.AdvanceTime();
    }

    private static int PlaneListener(Level100ActorId actorId, int owner) =>
        checked(actorId.Value * 2 + owner);

    private void DispatchPlaneEvent(RetailEventScheduler events, RetailEventDispatch dispatch)
    {
        var actorId = new Level100ActorId(dispatch.Listener / 2);
        if (!_states.TryGetValue(actorId.Value, out ActorState? state) || state.PlaneGuide is null)
            throw new InvalidOperationException("Aircraft event has no guide owner.");
        Level100ActorSnapshot actor = _actors.GetActor(actorId);
        if (actor.Lifecycle == Level100ActorLifecycle.Destroyed) return;

        if (dispatch.Listener % 2 == 0 && dispatch.EventNum == 3000)
        {
            if (actor.Active && actor.Lifecycle == Level100ActorLifecycle.Alive)
            {
                // The existing script/weapon target bridge is still partial:
                // common UnitAI support/fire callbacks and Plane's controller
                // approach/retreat cadence are not implemented by this Move.
                RefreshPlaneScriptTarget(state);
                Level100PlaneGuideSnapshot guide = state.PlaneGuide;
                RetailPlaneMotion.AdvanceFreeFlight(_actors.GetPlaneState(actorId),
                    new(guide.Destination, guide.Mode, guide.ClearanceFloatBits,
                        guide.ControllerState, guide.SpeedMode, null),
                    actor.DefinitionName == "Air Trainer" ? 0x41133333 : 0x40b00000,
                    BitConverter.SingleToInt32Bits(events.Time));
            }
            // Native AddMoveEvent stops recurrence once shutdown is declared.
            if (!_actors.GetBaseState(actorId).IsShuttingDown)
                events.AddEvent(3000, dispatch.Listener, RetailEventScheduler.NextFrame,
                    reuseHandle: dispatch.Handle);
            return;
        }

        if (dispatch.Listener % 2 != 1 || dispatch.EventNum is not (2000 or 2001))
            throw new InvalidOperationException("Unadmitted aircraft callback.");
        if (dispatch.EventNum == 2000)
        {
            Level100FloatVector3Bits position = _actors.GetBaseState(actorId).RetailPoses!.Current.PositionFloatBits;
            int x = checked((int)Math.Round(BitConverter.Int32BitsToSingle(position.X), MidpointRounding.ToEven));
            int y = checked((int)Math.Round(BitConverter.Int32BitsToSingle(position.Y), MidpointRounding.ToEven));
            if (x != state.PlaneGuide.ClearanceCellX || y != state.PlaneGuide.ClearanceCellY)
                state.PlaneGuide = state.PlaneGuide with
                {
                    ClearanceFloatBits = RetailPlaneMotion.ComputeClearance(Level100Terrain.Instance, position),
                    ClearanceCellX = x, ClearanceCellY = y,
                };
        }
        // 2001's actual ordered MapWho candidate/reader owner is still absent
        // from Level100. Its cadence is retained, but avoidance remains null;
        // actor-ID scans or collision spheres would fabricate its input.
        // Both callbacks draw and reschedule even on a clearance-cache hit.
        double jitter = RetailFloat24.Multiply(_releasedRandom.Next() % 65536, 1.0 / 131072);
        float due = (float)RetailFloat24.Add(RetailFloat24.Add(jitter, events.Time), .5f);
        events.AddEvent(dispatch.EventNum, dispatch.Listener, due, reuseHandle: dispatch.Handle);
    }

    private void SetPlaneWaypointDestination(ActorState state)
    {
        if (state.PlaneGuide is not { ControllerState: not 2 } guide || state.WaypointPath is null) return;
        Level100FloatVector4Bits point = _definitions.GetWaypointPath(state.WaypointPath)
            .ChainPoint(state.WaypointPointIndex).RetailComponentsFloatBits;
        state.PlaneGuide = guide with { Mode = 1, Destination = new(point.X, point.Y, point.Z) };
    }

    private void RefreshPlaneScriptTarget(ActorState state)
    {
        if (state.PlaneGuide is not { ControllerState: not 2 } guide ||
            state.Intent != Level100ActorCommandIntent.Attacking || !state.TargetActorId.HasValue) return;
        Level100ActorSnapshot target = _actors.GetActor(state.TargetActorId.Value);
        if (target.Lifecycle == Level100ActorLifecycle.Destroyed)
        {
            SetStoppedIntent(state);
            return;
        }
        ThingActorBaseStateSnapshot physical = _actors.GetBaseState(target.ActorId);
        Level100FloatVector3Bits position = physical.RetailPoses?.Current.PositionFloatBits ??
            RetailPositionFromProjection(target.Pose.PositionMillimeters);
        // Player motion still owns a quantized position. This conversion is a
        // bridge, not recovered raw target state or native virtual aim point.
        state.PlaneGuide = guide with { Mode = 1, Destination = position };
    }

    internal static Level100FloatVector3Bits RetailPositionFromProjection(SimVector3 position) => new(
        BitConverter.SingleToInt32Bits((float)(position.X / 1000.0 + 288.6875)),
        BitConverter.SingleToInt32Bits((float)(position.Z / 1000.0 + 243.25)),
        BitConverter.SingleToInt32Bits((float)(-10.0 - position.Y / 1000.0)));

    private void RestorePlaneEvents(Level100ActorMechanicsSnapshot snapshot)
    {
        if (snapshot.PlaneEvents is { Float24Arithmetic: false })
            throw new ArgumentException("Aircraft callbacks require the observed PC24 arithmetic mode.", nameof(snapshot));
        _planeEvents = snapshot.PlaneEvents is null ? null : new(snapshot.PlaneEvents);
        Level100ActorId[] rawActors = _actors.Snapshot.BaseStates
            .Where(item => item.State.RetailPlane is not null).Select(item => item.ActorId).ToArray();
        if (rawActors.Any(id => !_states.TryGetValue(id.Value, out ActorState? state) || state.PlaneGuide is null) ||
            ((_planeEvents is null) != (rawActors.Length == 0)))
            throw new ArgumentException("Aircraft physical/guide/event ownership is incomplete.", nameof(snapshot));
        if (snapshot.PlaneEvents is not { } events) return;
        var slots = events.Slots.ToDictionary(slot => slot.Handle);
        foreach (int handle in events.Lanes.SelectMany(lane => lane.Handles).Concat(events.Overflow))
        {
            if (!slots.TryGetValue(handle, out RetailEventSlotSnapshot? slot) ||
                slot.Listener <= 1 || !_states.TryGetValue(slot.Listener / 2, out ActorState? state) ||
                state.PlaneGuide is null || (slot.Listener % 2 == 0 ? slot.EventNum != 3000 : slot.EventNum is not (2000 or 2001)))
                throw new ArgumentException("Aircraft queue has an unowned callback.", nameof(snapshot));
        }
    }

    private void ValidatePlaneGuide(Level100ActorCommandIntentSnapshot source)
    {
        bool rawPlane = _actors.GetBaseState(source.ActorId).RetailPlane is not null;
        if (rawPlane != (source.PlaneGuide is not null))
            throw new ArgumentException("Aircraft guide requires its complete raw Actor state.", nameof(source));
        if (source.PlaneGuide is not { } guide) return;
        static bool Finite(int bits) => float.IsFinite(BitConverter.Int32BitsToSingle(bits));
        if (!Finite(guide.Destination.X) || !Finite(guide.Destination.Y) || !Finite(guide.Destination.Z) ||
            !Finite(guide.ClearanceFloatBits) || guide.Mode is < 0 or > 3 ||
            guide.ControllerState != 1 || guide.SpeedMode != 0)
            throw new ArgumentException("Unsupported aircraft guide state.", nameof(source));
    }
}
