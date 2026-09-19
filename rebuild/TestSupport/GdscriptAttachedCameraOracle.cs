// SPDX-License-Identifier: GPL-3.0-or-later
using System.Reflection;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using OnslaughtRebuild.Core.Tests;

// Temporary differential oracle for the currently committed Client camera seam.
// Synthetic facts supplement bounded existing simulation facts. No camera draft,
// device, scene, clock, viewport or new retail measurement is involved.
internal static class GdscriptAttachedCameraOracle
{
    private static readonly uint[] Alphas = [0, 0x80000000, 1, 0x3e800000, 0x3f000000, 0x3f400000, 0x3f800000];
    private static readonly uint[] EdgeWords = [0, 0x80000000, 1, 0x80000001, 0x007fffff, 0x00800000,
        0x3f800000, 0xbf800000, 0x7f7fffff, 0xff7fffff, 0x7f800000, 0xff800000,
        0x7fc00000, 0xffc00001, 0x7f800001, 0xff800001];

    internal static object Build()
    {
        var constructors = new List<object>();
        foreach ((int duration, int lead) in new (int, int)[] { (120, 1), (1, 0), (60, 59), (int.MaxValue, 0),
            (int.MaxValue, int.MaxValue - 1), (0, 0), (-1, 0), (int.MinValue, int.MinValue),
            (120, -1), (120, 120), (1, 1), (1, int.MaxValue) })
        {
            object expected;
            try { _ = new AttachedPanCameraState(duration, lead); expected = new { ok = true }; }
            catch (Exception error) { expected = Failure(error); }
            constructors.Add(new { duration, lead, expected });
        }

        var scenarios = new List<object>();
        void Scenario(string name, int duration, int lead, Action<Trace> actions)
        {
            var trace = new Trace(duration, lead);
            actions(trace);
            scenarios.Add(new { name, duration, lead, steps = trace.Steps });
        }
        Scenario("uninitialized-and-alpha-admission-order", 120, 1, t =>
        {
            t.Current();
            foreach (uint alpha in Alphas.Concat(new uint[] { 0xbf800000, 0x3f800001, 0x7f800000, 0xff800000, 0x7fc00001 })) t.Sample(alpha);
            t.Frame(Frame(0, 0));
            foreach (uint alpha in new uint[] { 0xbf800000, 0x3f800001, 0x7f800000, 0xff800000, 0xffc00001 }) t.Sample(alpha);
        });
        Scenario("shadow-repeat-conflict-reset-missing-handoff", 120, 1, t =>
        {
            t.Frame(Frame(0, 0)); t.SampleAll();
            t.Frame(Frame(1, 1, 1)); t.Frame(Frame(1, 1, 1)); t.Frame(Frame(1, 1, 2)); t.SampleAll();
            t.Frame(Frame(2, 2, 4)); t.Frame(Frame(3, 3, attached: false)); t.SampleAll();
            t.Frame(Frame(50, 50, 5)); t.Frame(Frame(51, 0, 100)); t.SampleAll();
            t.Frame(Frame(20, 60, 2)); t.Frame(Frame(118, 118, 2)); t.Frame(Frame(119, 119, 3, 800)); t.SampleAll();
            t.Frame(Frame(120, 120, 100)); t.SampleAll();
            t.Frame(Frame(121, 121, attached: false)); t.SampleAll();
            t.Frame(Frame(122, 122, 2, id: -1)); t.SampleAll();
            t.Frame(Frame(123, 123, 3, id: int.MinValue)); t.SampleAll();
        });
        foreach ((int duration, int lead) in new (int, int)[] { (1, 0), (2, 0), (2, 1), (3, 1), (60, 1), (120, 0), (int.MaxValue, int.MaxValue - 1) })
            Scenario($"duration-{duration}-lead-{lead}", duration, lead, t =>
            {
                t.Frame(Frame(0, 0)); t.SampleAll();
                t.Frame(Frame(1, Math.Max(0, duration - lead - 1), 1)); t.SampleAll();
                t.Frame(Frame(2, duration - lead, 2, int.MaxValue)); t.SampleAll();
                t.Frame(Frame(3, duration, 3, 1)); t.SampleAll();
                t.Frame(Frame(4, int.MaxValue, attached: false)); t.SampleAll();
            });
        Scenario("every-opening-tick", 120, 1, t =>
        {
            for (int tick = 0; tick <= 121; tick++)
            {
                t.Frame(Frame(tick, tick, tick * 0.125f, 1000 - tick));
                t.Sample(0x3f000000);
            }
        });
        foreach (float distance in new[] { MathF.BitDecrement(10f), 10f, MathF.BitIncrement(10f), 20f })
            Scenario("teleport-threshold-" + Word(distance), 120, 1, t =>
            {
                t.Frame(Frame(119, 119));
                t.Frame(Frame(120, 120, distance)); t.SampleAll();
            });
        Scenario("zero-directions-normalization-fallback", 120, 1, t =>
        {
            var first = new ClientCameraPose(new(1, 2, 3), new(1, 0, 0), new(0, 1, 0));
            var opposite = new ClientCameraPose(new(2, 3, 4), new(-1, 0, 0), new(0, -1, 0));
            t.Frame(Frame(119, 119, pose: first)); t.Frame(Frame(120, 120, pose: opposite)); t.SampleAll();
            t.Frame(Frame(121, 121, pose: new(new(3, 4, 5), default, default))); t.SampleAll();
        });
        Scenario("invalid-frames-preserve-existing-state", 120, 1, t =>
        {
            t.Frame(Frame(1, 1));
            foreach (var frame in new[] { Frame(-1, 2), Frame(2, -1), Frame(2, 2, zoom: 0),
                Frame(int.MinValue, int.MinValue, zoom: int.MinValue), Frame(2, 2, zoom: -1) }) t.Frame(frame);
            t.Current(); t.SampleAll(); t.Frame(Frame(2, 2));
        });
        Scenario("checked-reset-generation-retains-prior-state", 120, 1, t =>
        {
            t.Frame(Frame(10, 10)); t.SeedGeneration(int.MaxValue);
            t.Frame(Frame(11, 0)); t.Frame(Frame(0, 11)); t.Frame(Frame(11, 11)); t.SampleAll();
        });
        foreach (uint word in EdgeWords)
            Scenario("raw-vector-word-" + word.ToString("x8"), 120, 1, t =>
            {
                float value = Float(word);
                var pose = new ClientCameraPose(new(value, -0f, 1f), new(0f, value, -1f), new(value, 1f, 0f));
                t.Frame(Frame(119, 119, pose: pose, right: new(value, 0, 0)));
                t.SampleAll(); t.Frame(Frame(120, 120, pose: pose)); t.SampleAll();
            });
        Scenario("record-equality-uses-Single-Equals-not-raw-word-equality", 120, 1, t =>
        {
            var nan = new ClientCameraPose(new(Float(0x7fc00001), 0, 0), ClientCameraPose.Identity.Forward, ClientCameraPose.Identity.Up);
            t.Frame(Frame(1, 1, pose: nan));
            t.Frame(Frame(1, 1, pose: nan with { Position = new(Float(0xffc00023), -0f, 0) }));
            t.Current();
            t.Frame(Frame(2, 2, 0));
            t.Frame(Frame(2, 2, -0f)); t.Current();
        });

        Type fixtures = typeof(SimulationTests).Assembly.GetType("OnslaughtRebuild.TestSupport.Level100TestActorDefinitions")!;
        var definitions = (Level100ActorDefinitionSet)fixtures.GetMethod("Create", BindingFlags.NonPublic | BindingFlags.Static)!.Invoke(null, null)!;
        var simulation = new Simulation(0x4f4e534c, definitions, new(true, true, true, true));
        WorldSnapshot world = simulation.Snapshot;
        WorldSnapshot At(int tick, int remaining, int zoom = 1000) => world with
            { Tick = tick, Level100OpeningTicksRemaining = remaining, ZoomPermille = zoom };
        Scenario("world-adapter-read-order-and-partial-mutation", 120, 1, t =>
        {
            WorldSnapshot first = At(0, 120);
            WorldSnapshot next = At(1, 119);
            t.World(null, next); t.World(first, null);
            t.World(first, next); t.World(first, next);
            // The current frame matches; an impossible previous duration must not be read.
            t.World(At(-1, int.MinValue), next);
            t.World(null, next);
            t.World(next, At(2, 121)); t.World(next, At(2, int.MinValue));
            t.World(At(2, 118), At(3, 117, 0)); // Previous frame is committed before invalid current zoom.
            t.Current();
            t.World(At(-1, 120, 0), At(4, 116)); // Older previous is not advanced/validated.
            WorldSnapshot duplicate = At(5, 115) with { Level100Actors = world.Level100Actors with {
                Actors = world.Level100Actors.Actors.Concat([world.Level100Actors.Actors.Single(a => a.Name == "Player 1")]).ToArray() } };
            t.World(At(4, 116), duplicate);
            WorldSnapshot missing = At(119, 1) with { Level100Actors = world.Level100Actors with {
                Actors = world.Level100Actors.Actors.Where(a => a.Name != "Player 1").ToArray() } };
            t.World(At(118, 2), missing); t.SampleAll();
            t.World(missing, At(120, 0)); t.SampleAll();
            t.World(At(0, 120), At(1, 119)); t.SampleAll();
        });
        Scenario("bounded-live-simulation-world-pairs", 120, 1, t =>
        {
            WorldSnapshot previous = simulation.Snapshot;
            for (int tick = 0; tick < 8; tick++)
            {
                simulation.Step(new SimInput(0, 1));
                WorldSnapshot current = simulation.Snapshot;
                t.World(previous, current); t.SampleAll();
                previous = current;
            }
        });
        Scenario("varied-world-pose-float32-boundaries", 120, 1, t =>
        {
            uint random = 0x50414e43;
            int Next() { random = unchecked(random * 1664525u + 1013904223u); return unchecked((int)random); }
            WorldSnapshot previous = At(0, 120);
            for (int index = 1; index <= 96; index++)
            {
                WorldSnapshot current = At(index, 120 - index) with { FacingYawMicroRad = Next(), FacingPitchMicroRad = Next(),
                    BodyRollMicroRad = Next(), PlayerPosition = new(Next(), index == 1 ? int.MinValue : Next()), PlayerElevationMillimeters = Next() };
                t.World(previous, current); t.Sample(0x3e800000); t.Sample(0x3f400000);
                previous = current;
            }
        });

        var hashRows = new List<object>();
        void Hash(string name, AttachedPanCameraSnapshot? snapshot)
        {
            object expected;
            try { expected = new { ok = true, hex = AttachedPanCameraState.ComputeHash(snapshot!) }; }
            catch (Exception error) { expected = Failure(error); }
            hashRows.Add(new { name, snapshot = snapshot is null ? null : Snapshot(snapshot), expected });
        }
        Hash("null", null);
        var hashState = new AttachedPanCameraState(120, 1);
        AttachedPanCameraSnapshot original = hashState.AdvanceAtEndOfEventFrame(Frame(0, 0));
        Hash("original", original);
        Hash("hash-does-not-impose-advance-admission", original with { PanDurationTicks = -1, ControlViewHandoffTick = int.MaxValue,
            ResetGeneration = int.MinValue, UpdatePhase = (AttachedPanCameraUpdatePhase)(-1),
            PreviousFrame = Frame(-1, -1, zoom: 0), PanUpdateScheduled = false });
        foreach (uint word in EdgeWords)
            Hash("raw-hash-word-" + word.ToString("x8"), original with {
                CurrentPanPose = original.CurrentPanPose with { Position = new(Float(word), Float(word), Float(word)) } });

        var engines = new List<object>();
        foreach (uint depth in EdgeWords.Prepend(0x442f0000u))
        {
            uint near = depth == 0x442f0000 ? 0x3dcccccdu : depth;
            var engine = new Level100EngineViewpointState(Float(near), Float(depth));
            object initial = Selected(engine.SelectedSnapshot);
            string initialHash = engine.ComputeHash();
            var rows = new List<object>();
            foreach (int? id in new int?[] { null, 7, 7, 19, null, 0, -1, int.MinValue, int.MaxValue, null })
            {
                var view = new AttachedPanCameraViewSnapshot(id is int present ? new Level100ActorId(present) : null,
                    ClientCameraPose.Identity, Float(0xffc00001), HudVisible: false, OpeningPanActive: true);
                EngineViewpointSnapshot selected = engine.Bind(view);
                rows.Add(new { camera = View(view), selected = Selected(selected), hash = engine.ComputeHash() });
            }
            engines.Add(new { near_plane_bits = near, far_plane_bits = depth, slot_count = engine.SlotCount, initial, initial_hash = initialHash, rows });
        }
        return new { constructors, scenarios, hashes = hashRows, engines, identity_pose = Pose(ClientCameraPose.Identity) };
    }

    private sealed class Trace(int duration, int lead)
    {
        private readonly AttachedPanCameraState _state = new(duration, lead);
        internal List<object> Steps { get; } = [];
        internal void Frame(AttachedPanCameraFrame frame) => Add("frame", () => Snapshot(_state.AdvanceAtEndOfEventFrame(frame)), frame: frame);
        internal void Sample(uint alpha) => Add("sample", () => View(_state.Sample(Float(alpha))), alpha: alpha);
        internal void SampleAll() { foreach (uint alpha in Alphas) Sample(alpha); }
        internal void Current() => Add("current", () => Snapshot(_state.CurrentSnapshot));
        internal void World(WorldSnapshot? previous, WorldSnapshot? current) =>
            Add("world", () => Snapshot(_state.Advance(previous!, current!)), previous: previous, current: current);
        internal void SeedGeneration(int generation) => Add("seed_generation", () =>
        {
            typeof(AttachedPanCameraState).GetField("_snapshot", BindingFlags.NonPublic | BindingFlags.Instance)!
                .SetValue(_state, _state.CurrentSnapshot with { ResetGeneration = generation });
            return Snapshot(_state.CurrentSnapshot);
        }, generation: generation);
        private void Add(string operation, Func<object> action, AttachedPanCameraFrame? frame = null, uint alpha = 0,
            WorldSnapshot? previous = null, WorldSnapshot? current = null, int generation = 0)
        {
            object expected;
            try { expected = new { ok = true, value = action() }; }
            catch (Exception error) { expected = Failure(error); }
            AttachedPanCameraSnapshot? snapshot = null;
            try { snapshot = _state.CurrentSnapshot; } catch (InvalidOperationException) { }
            Steps.Add(new { operation, frame = frame is { } f ? GdscriptAttachedCameraOracle.FrameFacts(f) : null,
                alpha_bits = alpha, previous = Facts(previous), current = Facts(current), generation, expected,
                snapshot = snapshot is null ? null : Snapshot(snapshot), hash = snapshot?.ComputeHash() });
        }
    }

    private static AttachedPanCameraFrame Frame(int tick, int elapsed, float x = 0, int zoom = 1000,
        bool attached = true, int id = 7, ClientCameraPose? pose = null, Level100RenderVector3? right = null) =>
        new(tick, elapsed, zoom, attached ? new AttachedCameraThingSnapshot(new(id),
            pose ?? new(new(x, 0, 0), new(0, 0, -1), new(0, 1, 0)), right ?? new(1, 0, 0)) : null);
    private static object Failure(Exception error) => new { ok = false, error_type = error.GetType().Name,
        parameter = error is ArgumentException argument ? argument.ParamName ?? "" : "" };
    private static object Vector(Level100RenderVector3 vector) => new { x_bits = Word(vector.X), y_bits = Word(vector.Y), z_bits = Word(vector.Z) };
    private static object Pose(ClientCameraPose pose) => new { position = Vector(pose.Position), forward = Vector(pose.Forward), up = Vector(pose.Up) };
    private static object FrameFacts(AttachedPanCameraFrame frame) => new { event_frame = frame.EventFrame,
        pan_elapsed_ticks = frame.PanElapsedTicks, zoom_permille = frame.ZoomPermille,
        attached_thing = frame.AttachedThing is { } attached ? new { thing_id = attached.ThingId.Value, pose = Pose(attached.Pose), pan_right = Vector(attached.PanRight) } : null };
    private static object Snapshot(AttachedPanCameraSnapshot snapshot) => new { pan_duration_ticks = snapshot.PanDurationTicks,
        control_view_handoff_tick = snapshot.ControlViewHandoffTick, reset_generation = snapshot.ResetGeneration, update_phase = (int)snapshot.UpdatePhase,
        previous_frame = FrameFacts(snapshot.PreviousFrame), current_frame = FrameFacts(snapshot.CurrentFrame),
        previous_pan_pose = Pose(snapshot.PreviousPanPose), current_pan_pose = Pose(snapshot.CurrentPanPose), pan_update_scheduled = snapshot.PanUpdateScheduled };
    private static object View(AttachedPanCameraViewSnapshot view) => new { attached_thing_id = view.AttachedThingId?.Value,
        pose = Pose(view.Pose), zoom_bits = Word(view.Zoom), hud_visible = view.HudVisible, opening_pan_active = view.OpeningPanActive };
    private static object? Facts(WorldSnapshot? world) => world is null ? null : new { tick = world.Tick,
        opening_ticks_remaining = world.Level100OpeningTicksRemaining, zoom_permille = world.ZoomPermille,
        facing_yaw_micro_rad = world.FacingYawMicroRad, facing_pitch_micro_rad = world.FacingPitchMicroRad, body_roll_micro_rad = world.BodyRollMicroRad,
        player_position = new { x = world.PlayerPosition.X, z = world.PlayerPosition.Z }, player_elevation_millimeters = world.PlayerElevationMillimeters,
        actors = world.Level100Actors.Actors.Select(actor => new { name = actor.Name?.Select(c => (int)c).ToArray(), actor_id = actor.ActorId.Value }) };
    private static object Selected(EngineViewpointSnapshot selected) => new { selected_slot = selected.SelectedSlot,
        selected_slot_state = new { camera_identity = selected.SelectedSlotState.CameraIdentity?.Select(c => (int)c).ToArray(),
            player_thing_identity = selected.SelectedSlotState.PlayerThingIdentity, viewport = (object?)null },
        current_viewport = (object?)null, near_plane_bits = Word(selected.NearPlane), far_plane_bits = Word(selected.FarPlane) };
    private static float Float(uint bits) => BitConverter.UInt32BitsToSingle(bits);
    private static uint Word(float value) => BitConverter.SingleToUInt32Bits(value);
}
