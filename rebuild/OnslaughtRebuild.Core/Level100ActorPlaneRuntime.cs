// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

/// <summary>Guide-owned state, separate from the Actor's physical pose.</summary>
public sealed record Level100PlaneGuideSnapshot(
    Level100FloatVector3Bits Destination, int Mode, int ClearanceFloatBits,
    int ClearanceCellX, int ClearanceCellY, int ControllerState, int SpeedMode);

/// <summary>
/// Retained UnitAI spawning-owner reader, attachment tag, path selector and
/// absolute deadline. ScriptControlResumed belongs to the reconstruction's
/// existing approximate normal-control bridge, not a claimed retail field.
/// The controller's native +20 state remains in PlaneGuide.
/// </summary>
public sealed record Level100PlaneSpawnerExitSnapshot(
    Level100ActorId? SpawningOwnerId, Level100ActorId? CollisionIgnoredActorId, int AttachmentTag, int Selector,
    int DeadlineFloatBits, bool ScriptControlResumed);

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
        Level100ActorSnapshot actor = _actors.GetActor(actorId);
        Level100PlaneSpawnerExitSnapshot? exit = null;
        if (actor.SpawnOwnerId is { } ownerId)
        {
            // Validate admitted input before consuming RNG or filing callbacks.
            // Missing data is different from a legitimate absent selector.
            _ = _actors.GetPlaneSpawnerExitPoint(actorId, 1);
            int tag = actor.SpawnerName switch
            {
                "SpawnerA" => 15, "SpawnerB" => 16,
                _ => throw new NotSupportedException("Unadmitted aircraft exit attachment."),
            };
            exit = new(ownerId, ownerId, tag, 1, BitConverter.SingleToInt32Bits(
                (float)RetailFloat24.Add(_planeEvents?.Time ?? 0, 10.0f)), false);
        }
        _planeEvents ??= new(useFloat24Arithmetic: true);
        // Actor Init consumes this draw even though the Plane divisor is 1.
        _ = _releasedRandom.Next();
        _states.Add(actorId.Value, new ActorState
        {
            ActorId = actorId, Intent = Level100ActorCommandIntent.Stopped,
            PlaneGuide = new(physical.RetailPoses!.Current.PositionFloatBits, 0, 0, 0, 0, exit is null ? 1 : 2, 0),
            PlaneSpawnerExit = exit,
        });
        // The two cache coordinates are unwritten by native constructors.
        // Zero is the observed startup allocation in observe-plane-motion-a,
        // a declared deterministic seed here, not a universal allocator law.
        _planeEvents.AddEvent(3000, PlaneListener(actorId, 0), RetailEventScheduler.NextFrame);
        _planeEvents.AddEvent(2000, PlaneListener(actorId, 1), RetailEventScheduler.NextFrame);
        _planeEvents.AddEvent(2001, PlaneListener(actorId, 1), RetailEventScheduler.NextFrame);
        // CUnitAI__Init [004fe710,004fea24), selected profile +19c == 0:
        // no constructor Ready and no optional sweeping RNG draws.
        if (exit is not null)
            _planeEvents.AddEvent(3002, PlaneControllerListener(actorId), _planeEvents.Time);
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

    // Scheduler listeners are opaque nonzero identities. Keep established
    // Actor/Guide values; negative IDs identify the distinct UnitAI listener.
    private static int PlaneControllerListener(Level100ActorId actorId) => -actorId.Value;

    private static bool PlaneScriptControlAvailable(ActorState state) =>
        state.PlaneSpawnerExit is null || state.PlaneSpawnerExit.ScriptControlResumed;

    private void DispatchPlaneEvent(RetailEventScheduler events, RetailEventDispatch dispatch,
        Action<Level100ActorId>? dispatchReady, Action<Level100ActorId>? startPlaneDeath)
    {
        var actorId = new Level100ActorId(dispatch.Listener < 0 ? checked(-dispatch.Listener) : dispatch.Listener / 2);
        if (!_states.TryGetValue(actorId.Value, out ActorState? state) || state.PlaneGuide is null)
            throw new InvalidOperationException("Aircraft event has no guide owner.");
        Level100ActorSnapshot actor = _actors.GetActor(actorId);
        if (actor.Lifecycle == Level100ActorLifecycle.Destroyed) return;

        if (dispatch.Listener < 0)
        {
            if (state.PlaneSpawnerExit is null)
                throw new InvalidOperationException("Aircraft controller has no admitted exit owner.");
            if (dispatch.EventNum == 3002)
                AdvancePlaneSpawnerExit(events, dispatch, state, startPlaneDeath);
            else if (dispatch.EventNum == 3000)
                ResumePlaneScriptControlBridge(state);
            else throw new InvalidOperationException("Unadmitted aircraft controller callback.");
            return;
        }

        if (dispatch.Listener % 2 == 0 && dispatch.EventNum == 2003)
        {
            // A mechanics-only consumer may omit a script adapter. Simulation
            // supplies it and settles script commands inside this callback.
            dispatchReady?.Invoke(actorId);
            return;
        }

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
        if (!PlaneScriptControlAvailable(state) ||
            state.PlaneGuide is not { ControllerState: not 2 } guide || state.WaypointPath is null) return;
        Level100FloatVector4Bits point = _definitions.GetWaypointPath(state.WaypointPath)
            .ChainPoint(state.WaypointPointIndex).RetailComponentsFloatBits;
        state.PlaneGuide = guide with { Mode = 1, Destination = new(point.X, point.Y, point.Z) };
    }

    private void RefreshPlaneScriptTarget(ActorState state)
    {
        if (!PlaneScriptControlAvailable(state) || state.PlaneGuide is not { ControllerState: not 2 } guide ||
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

    private void ResumePlaneScriptControlBridge(ActorState state)
    {
        if (state.PlaneGuide!.ControllerState != 1 || state.PlaneSpawnerExit!.ScriptControlResumed)
            throw new InvalidOperationException("Aircraft normal-control handoff is out of order.");
        state.PlaneSpawnerExit = state.PlaneSpawnerExit with { ScriptControlResumed = true };
        // Explicit boundary: the recovered exit hands back to the pre-existing
        // per-Move target/waypoint and per-tick weapon approximation. This does
        // not execute native Plane common AI, hysteresis, provider preparation
        // or its recurring 3000/3001 events, and consumes no invented RNG.
        SetPlaneWaypointDestination(state);
        RefreshPlaneScriptTarget(state);
    }

    private void CompletePlaneSpawnerExit(RetailEventScheduler events, ActorState state)
    {
        // 004febe0 changes controller state and submits a FRESH normal event.
        // Ready is a different listener and another fresh event, submitted
        // after it. Native owner+38 is collision state, not this guide: do not
        // clear the guide's mode, destination or clearance at this boundary.
        state.PlaneGuide = state.PlaneGuide! with { ControllerState = 1 };
        // owner+38 is CCollisionSeekingThing; its raw +20 ignore pointer is
        // cleared at 4ffd87. The controller's monitored spawning-owner reader
        // survives. Full Plane contact response is still outside this mover.
        state.PlaneSpawnerExit = state.PlaneSpawnerExit! with { CollisionIgnoredActorId = null };
        events.AddEvent(3000, PlaneControllerListener(state.ActorId), events.Time);
        if (_actors.GetActor(state.ActorId).ScriptName is not null)
            events.AddEvent(2003, PlaneListener(state.ActorId, 0), RetailEventScheduler.NextFrame);
    }

    private void AdvancePlaneSpawnerExit(RetailEventScheduler events, RetailEventDispatch dispatch,
        ActorState state, Action<Level100ActorId>? startPlaneDeath)
    {
        Level100PlaneSpawnerExitSnapshot exit = state.PlaneSpawnerExit!;
        if (state.PlaneGuide!.ControllerState != 2 || exit.ScriptControlResumed)
            throw new InvalidOperationException("Aircraft exit callback is out of order.");
        // Selected Unit construction sets GetVulnerable (+15c) to exactly 1;
        // none of the admitted Level100 object programs calls SetVulnerable.
        // +e4 is vulnerability, not a class-kind discriminator. The reader
        // survives StartedDying and becomes null only when its owner is deleted.
        if (exit.SpawningOwnerId is not { } ownerId || _actors.GetBaseState(ownerId).IsDying)
        {
            if (startPlaneDeath is null) _actors.ReportPlaneStartedDying(state.ActorId);
            else startPlaneDeath(state.ActorId);
            return; // Native AirUnit death request bypasses Ready/normal handoff.
        }

        // The admitted Airfield's +184 capability is true. Its exact tag and
        // selector resolve constant model input; absent data was refused at Init.
        if (BitConverter.Int32BitsToSingle(exit.DeadlineFloatBits) <= events.Time)
        {
            CompletePlaneSpawnerExit(events, state);
            return;
        }
        RetailUnitAttachmentPose? point = _actors.GetPlaneSpawnerExitPoint(state.ActorId, exit.Selector);
        if (point is null || Zero(point.Value.PositionFloatBits))
        {
            CompletePlaneSpawnerExit(events, state);
            return;
        }

        Level100FloatVector3Bits destination = point.Value.PositionFloatBits;
        float floor = (float)RetailFloat24.Subtract(
            RetailWorldTerrain.SampleRetailHeight(Level100Terrain.Instance, destination), 0.1f);
        if (Read(destination.Z) > floor)
            destination = destination with { Z = BitConverter.SingleToInt32Bits(floor) };
        Level100FloatVector3Bits position = _actors.GetBaseState(state.ActorId).RetailPoses!.Current.PositionFloatBits;
        double dx = (float)RetailFloat24.Subtract(Read(destination.X), Read(position.X));
        double dy = (float)RetailFloat24.Subtract(Read(destination.Y), Read(position.Y));
        double dz = (float)RetailFloat24.Subtract(Read(destination.Z), Read(position.Z));
        double squared = RetailFloat24.Add(RetailFloat24.Add(
            RetailFloat24.Multiply(dz, dz), RetailFloat24.Multiply(dy, dy)), RetailFloat24.Multiply(dx, dx));
        // Plane's native SetThingType (50e870 -> 4fcdc0) supplies bit 0x400.
        // Its threshold is not the script-waypoint arrival radius.
        if (squared < 6.25f)
            state.PlaneSpawnerExit = exit with { Selector = checked(exit.Selector + 1) };

        // The old selector's point is still sent on the arrival update.
        // AirUnit GoTo (403a90) adds an INTEGER terrain/water/profile clamp
        // after the above arrival test. Guide 47e2d0 receives override=TRUE,
        // allowing it to write mode 1 even while controller state is 2.
        int x = checked((int)Math.Round(Read(destination.X), MidpointRounding.ToEven));
        int y = checked((int)Math.Round(Read(destination.Y), MidpointRounding.ToEven));
        double terrain = RetailFloat24.Multiply(Level100Terrain.Instance.SampleAirGuideHeightUnits(x, y),
            Level100Terrain.Instance.HeightScale);
        double minimumAltitude = RetailFloat24.Subtract(Math.Min(terrain, Level100Terrain.Instance.WaterLevel), 4.0f);
        // Profile default +15c is 4.0f; field42 is absent from selected rows
        // Air Trainer601 / Target Drone660 and their Base Air Unit570 parent.
        if (Read(destination.Z) > minimumAltitude)
            destination = destination with { Z = BitConverter.SingleToInt32Bits((float)minimumAltitude) };
        state.PlaneGuide = state.PlaneGuide with { Mode = 1, Destination = destination };

        int sample = _releasedRandom.Next() % 65536;
        double jitter = RetailFloat24.Multiply(sample, BitConverter.Int32BitsToSingle(0x35cccccd));
        float due = (float)RetailFloat24.Add(RetailFloat24.Add(jitter, events.Time), 0.1f);
        events.AddEvent(3002, dispatch.Listener, due, reuseHandle: dispatch.Handle);

        static double Read(int bits) => BitConverter.Int32BitsToSingle(bits);
        static bool Zero(Level100FloatVector3Bits value) => Read(value.X) == 0 && Read(value.Y) == 0 && Read(value.Z) == 0;
    }

    private void InvalidatePlaneReferences()
    {
        if (_planeEvents is null) return;
        var destroyed = new HashSet<int>();
        foreach (ActorState state in _states.Values)
        {
            if (state.PlaneGuide is null) continue;
            if (_actors.GetActor(state.ActorId).Lifecycle == Level100ActorLifecycle.Destroyed)
                destroyed.Add(state.ActorId.Value);
            if (state.PlaneSpawnerExit is { SpawningOwnerId: { } ownerId } exit &&
                _actors.GetActor(ownerId).Lifecycle == Level100ActorLifecycle.Destroyed)
                state.PlaneSpawnerExit = exit with { SpawningOwnerId = null };
        }
        if (destroyed.Count == 0) return;
        RetailEventSchedulerSnapshot snapshot = _planeEvents.Snapshot;
        var slots = snapshot.Slots.ToDictionary(slot => slot.Handle);
        foreach (int handle in snapshot.Lanes.SelectMany(lane => lane.Handles).Concat(snapshot.Overflow))
        {
            int listener = slots[handle].Listener;
            int actor = listener < 0 ? checked(-listener) : listener / 2;
            if (destroyed.Contains(actor)) _planeEvents.ClearListener(handle);
        }
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
            if (!slots.TryGetValue(handle, out RetailEventSlotSnapshot? slot))
                throw new ArgumentException("Aircraft queue has a missing event.", nameof(snapshot));
            // Deleted monitored listeners remain filed until normal disposal.
            if (slot.Listener == 0) continue;
            if (slot.Listener is 1 or int.MinValue)
                throw new ArgumentException("Aircraft queue has an invalid listener.", nameof(snapshot));
            int owner = slot.Listener < 0 ? -slot.Listener : slot.Listener / 2;
            if (!_states.TryGetValue(owner, out ActorState? state) || state.PlaneGuide is null)
                throw new ArgumentException("Aircraft queue has an unowned callback.", nameof(snapshot));
            bool admitted = slot.Listener < 0
                ? state.PlaneSpawnerExit is { ScriptControlResumed: false } &&
                    (slot.EventNum == 3002 && state.PlaneGuide.ControllerState == 2 ||
                     slot.EventNum == 3000 && state.PlaneGuide.ControllerState == 1)
                : slot.Listener % 2 == 1 ? slot.EventNum is 2000 or 2001
                : slot.EventNum == 3000 || slot.EventNum == 2003 && state.PlaneSpawnerExit is not null &&
                    state.PlaneGuide.ControllerState == 1;
            if (!admitted)
                throw new ArgumentException("Aircraft queue has an unowned callback.", nameof(snapshot));
        }
        foreach (ActorState state in _states.Values.Where(item => item.PlaneSpawnerExit is not null))
        {
            if (_actors.GetActor(state.ActorId).Lifecycle == Level100ActorLifecycle.Destroyed) continue;
            int[] queued = events.Lanes.SelectMany(lane => lane.Handles).Concat(events.Overflow)
                .Where(handle => slots[handle].Listener == PlaneControllerListener(state.ActorId)).ToArray();
            bool killedDuringExit = state.PlaneGuide!.ControllerState == 2 &&
                _actors.GetActor(state.ActorId).Lifecycle == Level100ActorLifecycle.StartedDying;
            if (queued.Length != (state.PlaneSpawnerExit!.ScriptControlResumed ? 0 : 1) &&
                !(killedDuringExit && queued.Length == 0))
                throw new ArgumentException("Aircraft exit has missing or duplicate controller work.", nameof(snapshot));
        }
    }

    private void ValidatePlaneGuide(Level100ActorCommandIntentSnapshot source)
    {
        bool rawPlane = _actors.GetBaseState(source.ActorId).RetailPlane is not null;
        Level100ActorSnapshot actor = _actors.GetActor(source.ActorId);
        if (rawPlane != (source.PlaneGuide is not null))
            throw new ArgumentException("Aircraft guide requires its complete raw Actor state.", nameof(source));
        if ((rawPlane && actor.SpawnOwnerId.HasValue) != (source.PlaneSpawnerExit is not null))
            throw new ArgumentException("Spawned aircraft requires retained exit ownership.", nameof(source));
        if (source.PlaneGuide is not { } guide) return;
        static bool Finite(int bits) => float.IsFinite(BitConverter.Int32BitsToSingle(bits));
        if (!Finite(guide.Destination.X) || !Finite(guide.Destination.Y) || !Finite(guide.Destination.Z) ||
            !Finite(guide.ClearanceFloatBits) || guide.Mode is < 0 or > 3 ||
            (source.PlaneSpawnerExit is null ? guide.ControllerState != 1 : guide.ControllerState is not (1 or 2)) ||
            guide.SpeedMode != 0)
            throw new ArgumentException("Unsupported aircraft guide state.", nameof(source));
        if (source.PlaneSpawnerExit is not { } exit) return;
        int tag = actor.SpawnerName == "SpawnerA" ? 15 : actor.SpawnerName == "SpawnerB" ? 16 : 0;
        if (tag == 0 || exit.AttachmentTag != tag || exit.Selector < 1 ||
            !Finite(exit.DeadlineFloatBits) || BitConverter.Int32BitsToSingle(exit.DeadlineFloatBits) < 0 ||
            (exit.SpawningOwnerId.HasValue ? exit.SpawningOwnerId != actor.SpawnOwnerId :
                _actors.GetActor(actor.SpawnOwnerId!.Value).Lifecycle != Level100ActorLifecycle.Destroyed) ||
            (guide.ControllerState == 2 ? exit.CollisionIgnoredActorId != actor.SpawnOwnerId :
                exit.CollisionIgnoredActorId is not null) ||
            exit.ScriptControlResumed && guide.ControllerState != 1)
            throw new ArgumentException("Unsupported aircraft exit state.", nameof(source));
        _ = _definitions.GetSpawnDefinition(actor.DefinitionIdentity).SpawnerExitWaypoints ??
            throw new ArgumentException("Aircraft exit inputs are missing.", nameof(source));
    }
}
