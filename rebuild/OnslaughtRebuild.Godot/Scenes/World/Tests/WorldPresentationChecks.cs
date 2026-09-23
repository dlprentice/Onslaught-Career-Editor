// SPDX-License-Identifier: GPL-3.0-or-later
using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using D = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

/// <summary>Actual production controller against the retained 1bb29345 C#
/// presentation arithmetic. The existing, separately checked Aquila components
/// consume expected contacts/frames; this is not another world renderer.</summary>
public sealed partial class WorldPresentationChecks : Node
{
    private int _checks;
    private readonly List<string> _completed = [];

    public override async void _Ready()
    {
        try
        {
            Check(!Engine.IsEditorHint() && DisplayServer.GetName() == "headless", "This bounded controller check requires headless runtime.");
            var pointer = Input.MouseMode;
            var session = new InteractiveSession(0x4f4e534c, Level100StaticWorldAsset.LoadActorDefinitions());
            WorldSnapshot basis = session.CurrentSnapshot;
            string sourceHash = StateHasher.ComputeHex(basis);
            var viewport = new SubViewport { Size = new(640, 480), OwnWorld3D = true,
                RenderTargetUpdateMode = SubViewport.UpdateMode.Disabled };
            AddChild(viewport);
            var world = FirstFlightWorldView.InstantiateScene();
            Node owner = world.GetNode("WorldPresentation");
            Node entities = world.GetNode("EntityPresentation");
            using var camera = new GdCameraState(owner);
            InitialNodePose[] authoredPoses = [InitialNodePose.Capture(world),
                InitialNodePose.Capture(world.GetNode<Node3D>("PlayerVisual")),
                InitialNodePose.Capture(world.GetNode<Node3D>("PlayerVisual/BodyPivot")),
                InitialNodePose.Capture(world.GetNode<Camera3D>("RetailOpeningAndFirstPersonCamera"))];
            Transform3D authoredPlayer = authoredPoses[1].Transform;
            Check(!camera.IsInitialized && !owner.IsProcessing() && !owner.IsProcessingInput(), "Authored world controller is passive before explicit initialization.");
            viewport.AddChild(world);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            Check(!camera.IsInitialized && world.GetNode<Node3D>("PlayerVisual").Transform == authoredPlayer,
                "Tree entry does not start a second simulation or change the authored pose.");
            world.Initialize(basis);
            using var expected = new ControllerOracle(world, viewport, authoredPoses);
            expected.Render(basis, basis, 0f, 0f, viewport.Size.Y);
            using Variant cameraOwner = owner.Get("_camera_state");
            using Variant entityOwner = owner.Get("_entities");
            Check(cameraOwner.AsGodotObject() is not null && entityOwner.AsGodotObject() == entities,
                "The authored controller borrows the existing entity component and owns one camera state.");
            Compare(world, owner, expected, camera);
            Done("authored_owner_and_initialization");

            WorldSnapshot prior = basis;
            int tick = 1;
            foreach ((VehicleMode mode, VehicleTransition transition, float delta) in new[]
            {
                (VehicleMode.Walker, VehicleTransition.None, -1f),
                (VehicleMode.Walker, VehicleTransition.WalkerToJet, 0f),
                (VehicleMode.Walker, VehicleTransition.WalkerToJet, MathF.BitDecrement(0.05f)),
                (VehicleMode.Walker, VehicleTransition.WalkerToJet, 0.05f - MathF.BitDecrement(0.05f)),
                (VehicleMode.Walker, VehicleTransition.WalkerToJet, 0.05f),
                (VehicleMode.Jet, VehicleTransition.None, 1.05f),
                (VehicleMode.Jet, VehicleTransition.None, 0.1f),
                (VehicleMode.Jet, VehicleTransition.JetToWalker, 0f),
                (VehicleMode.Jet, VehicleTransition.JetToWalker, 1.2f),
                (VehicleMode.Jet, VehicleTransition.JetToWalker, 0.05f),
                (VehicleMode.Walker, VehicleTransition.None, 0f),
                (VehicleMode.Walker, VehicleTransition.WalkerToJet, 0.05f),
                (VehicleMode.Jet, VehicleTransition.JetToWalker, 0.05f),
                (VehicleMode.Walker, VehicleTransition.None, 0f),
            })
            {
                WorldSnapshot current = basis with { Tick = tick, Level100OpeningTicksRemaining = Math.Max(0, 120 - tick),
                    Mode = mode, Transition = transition, FacingYawMicroRad = basis.FacingYawMicroRad + tick * 37000,
                    FacingPitchMicroRad = tick * -9001, BodyRollMicroRad = tick * 7003 };
                RenderPair(world, owner, expected, camera, prior, current, 0.375f, delta, viewport.Size.Y);
                prior = current;
                tick++;
            }
            // The strict ten-metre reset and reference/count gates are old
            // source decisions, not reconstructed from the native controller.
            foreach (int distance in new[] { 10_000, 10_001 })
            {
                WorldSnapshot current = Shift(basis, distance) with { Tick = tick++, Level100OpeningTicksRemaining = 0 };
                RenderPair(world, owner, expected, camera, basis, current, 0.25f, 0f, viewport.Size.Y);
                prior = current;
            }
            RenderPair(world, owner, expected, camera, prior, prior, 0.5f, 0f, viewport.Size.Y);
            RenderPair(world, owner, expected, camera, prior with { WalkerFeet = [] }, prior, 0.5f, 0f, viewport.Size.Y);
            WorldSnapshot reset = Shift(prior, 25_000) with { Tick = tick++ };
            RenderPair(world, owner, expected, camera, prior with { WalkerFeet = null! }, reset, 0.5f, 0f, viewport.Size.Y);
            WorldSnapshot boundary = basis with { Tick = tick++, Level100OpeningTicksRemaining = 0,
                PlayerPosition = new(int.MinValue, int.MaxValue), PlayerElevationMillimeters = int.MinValue,
                FacingYawMicroRad = int.MaxValue, FacingPitchMicroRad = int.MinValue, BodyRollMicroRad = int.MaxValue };
            RenderPair(world, owner, expected, camera, boundary, boundary, 0f, 0f, viewport.Size.Y);
            viewport.Size = new(801, 601);
            prior = basis with { Tick = 1, Level100OpeningTicksRemaining = 119, Mode = VehicleMode.Jet, ZoomPermille = 400 };
            RenderPair(world, owner, expected, camera, reset, prior, 1f, 0f, viewport.Size.Y);
            Check(owner.Get("_camera_state").AsGodotObject() == cameraOwner.AsGodotObject()
                && owner.Get("_entities").AsGodotObject() == entities, "Tick reset and projection resize retain the original owners.");
            Done("player_aquila_camera_and_gates");

            CheckPartialFailure(world, owner, expected, camera, prior, viewport.Size.Y);
            Done("partial_failure_and_detached_facts");
            CheckCollectionFailureBoundary(world, owner, expected, camera, prior, viewport.Size.Y);
            Done("deferred_projection_and_projectile_failure_boundary");
            CheckTransitionNonfinite(owner, expected, prior);
            Done("isolated_nonfinite_transition_math");
            CheckDisposedSceneryBoundary(world, owner, expected, camera, prior, viewport.Size.Y);
            Done("disposed_scenery_exception_and_partial_frame");
            Check(StateHasher.ComputeHex(basis) == sourceHash && Input.MouseMode == pointer,
                "Presentation leaves the deterministic source snapshot and pointer ownership unchanged.");
            world.Free();
            viewport.QueueFree();
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            GD.Print($"WORLD_PRESENTATION_CHECKS: {_checks} passed; completed={string.Join(',', _completed)}; retained C# arithmetic, production native owners, no gameplay-completion claim.");
            GetTree().Quit(0);
        }
        catch (Exception error) { GD.PushError(error.ToString()); GetTree().Quit(1); }
    }

    private void RenderPair(FirstFlightWorldView world, Node owner, ControllerOracle expected, GdCameraState camera,
        WorldSnapshot previous, WorldSnapshot current, float alpha, float delta, float height)
    {
        string before = StateHasher.ComputeHex(current);
        expected.Render(previous, current, alpha, delta, height);
        world.Render(previous, current, alpha, delta);
        Compare(world, owner, expected, camera);
        Check(StateHasher.ComputeHex(current) == before, "Rendering never writes the supplied Core snapshot.");
    }

    private void CheckPartialFailure(FirstFlightWorldView world, Node owner, ControllerOracle expected,
        GdCameraState camera, WorldSnapshot basis, float height)
    {
        world.ConsumeLevel100WeaponFireEvents([new(basis.Tick, Level100PlayerWeapon.PulseCannonPod, 1),
            new(basis.Tick, Level100PlayerWeapon.PulseCannonPod, 4)]);
        using (D pending = Snapshot(owner)) Check(pending["pending_muzzles"].AsInt32() == 2,
            "Each pulse fire event adds one native pending muzzle regardless of volley size.");
        WorldSnapshot bad = Shift(basis, 2000) with { Tick = basis.Tick + 1, WalkerFeet = basis.WalkerFeet.Take(3).ToArray() };
        string beforeCamera = camera.ComputeCameraHash();
        Expect<InvalidDataException>(() => expected.Render(basis, bad, 0.5f, 0.125f, height), "Retained foot-count failure.");
        Expect<InvalidDataException>(() => world.Render(basis, bad, 0.5f, 0.125f), "Native controller refuses at the original foot stage.");
        Compare(world, owner, expected, camera);
        using (D partial = Snapshot(owner))
        {
            Check(partial["pending_muzzles"].AsInt32() == 2 && camera.ComputeCameraHash() == beforeCamera,
                "Failed feet leave pending muzzles and camera untouched after particle/player mutation.");
            partial["pending_muzzles"] = 999;
            partial["particle_seconds_bits"] = 0;
            partial["show_hud"] = !expected.ShowHud;
        }
        using (D detached = Snapshot(owner)) Check(detached["pending_muzzles"].AsInt32() == 2
            && detached["particle_seconds_bits"].AsInt64() == Word(expected.ParticleSeconds), "Host facts are detached observations of the one native owner.");
        WorldSnapshot recovered = basis with { Tick = bad.Tick + 1 };
        RenderPair(world, owner, expected, camera, basis, recovered, 0.5f, 0f, height);
        using D after = Snapshot(owner);
        Check(after["pending_muzzles"].AsInt32() == 0, "A later successful frame can consume the preserved native muzzle queue.");
    }

    private void CheckTransitionNonfinite(Node owner, ControllerOracle expected, WorldSnapshot basis)
    {
        // Exercise the real transition stage directly, so nonfinite delta never
        // reaches terrain/water updates or a camera/player geometry setter.
        foreach ((VehicleMode mode, VehicleTransition transition, float delta) in new[]
        {
            (VehicleMode.Walker, VehicleTransition.WalkerToJet, float.NaN),
            (VehicleMode.Walker, VehicleTransition.WalkerToJet, 0f),
            (VehicleMode.Jet, VehicleTransition.JetToWalker, float.PositiveInfinity),
            (VehicleMode.Walker, VehicleTransition.None, float.NegativeInfinity),
            (VehicleMode.Walker, VehicleTransition.WalkerToJet, -0f),
            (VehicleMode.Walker, VehicleTransition.WalkerToJet, float.MaxValue),
        })
        {
            WorldSnapshot value = basis with { Mode = mode, Transition = transition };
            expected.Transition(value, delta);
            using var facts = new D { ["mode"] = (int)mode, ["transition"] = (int)transition };
            using Variant result = owner.Call("_update_aquila_transition_presentation", facts, delta);
            Require(result);
            CompareTransition(owner, expected);
        }
    }

    private void CheckCollectionFailureBoundary(FirstFlightWorldView world, Node owner, ControllerOracle expected,
        GdCameraState camera, WorldSnapshot basis, float height)
    {
        Level100ActorId target = basis.Targets.First().ActorId;
        WorldSnapshot moved = Shift(basis, 3000) with
        {
            Tick = basis.Tick + 10, FacingYawMicroRad = basis.FacingYawMicroRad + 210000,
            Mode = VehicleMode.Walker, Transition = VehicleTransition.WalkerToJet,
            WalkerFeet = Shift(basis, 3000).WalkerFeet.Select(foot => foot with
                { LiftMillimeters = foot.LiftMillimeters + 125 }).ToArray(),
        };
        WorldSnapshot invalidTarget = moved with { Level100Actors = moved.Level100Actors with
        {
            Actors = moved.Level100Actors.Actors.Select(actor => actor.ActorId == target
                ? actor with { DefinitionName = null } : actor).ToArray(),
        } };
        WorldSnapshot nullProjectile = moved with { Projectiles = new ProjectileSnapshot[] { null! } };
        WorldSnapshot invalidFootAndTarget = invalidTarget with
        {
            WalkerFeet = invalidTarget.WalkerFeet.Select((foot, index) => index == 0 ? foot with { Id = 99 } : foot).ToArray(),
        };
        world.ConsumeLevel100WeaponFireEvents([new(basis.Tick, Level100PlayerWeapon.PulseCannonPod, 1)]);
        foreach ((string name, WorldSnapshot previous, WorldSnapshot current, Type failureType, string? message) in new[]
        {
            ("current computed target projection", basis, invalidTarget, typeof(InvalidDataException), (string?)null),
            ("previous computed target projection", invalidTarget, moved, typeof(InvalidDataException), (string?)null),
            ("current null projectile row", basis, nullProjectile, typeof(NullReferenceException), (string?)null),
            ("previous null projectile row", nullProjectile, moved, typeof(NullReferenceException), (string?)null),
            ("target failure precedes previous projectile failure", nullProjectile, invalidTarget, typeof(InvalidDataException), (string?)null),
            ("pure feet failure precedes computed target failure", basis, invalidFootAndTarget, typeof(InvalidDataException), "Core exposed unknown Aquila foot 99."),
        })
        {
            string beforeCamera = camera.ComputeCameraHash();
            string beforeViewpoint = camera.ComputeViewpointHash();
            Transform3D beforePlayer = world.GetNode<Node3D>("PlayerVisual").Transform;
            Exception wanted = CaptureFailure(() => expected.Render(previous, current, 0.375f, 0.125f, height));
            Check(wanted.GetType() == failureType && (message is null || wanted.Message == message),
                name + ": retained source reaches the intended failure, rather than an unrelated invalid fixture.");
            Exception actual = CaptureFailure(() => world.Render(previous, current, 0.375f, 0.125f));
            Check(actual.GetType() == wanted.GetType(), name + ": exact exception type survives the managed/native boundary.");
            if (wanted is InvalidDataException)
                Check(actual.Message == wanted.Message, name + ": the original projection/foot failure message is retained.");
            Compare(world, owner, expected, camera);
            Check(camera.ComputeCameraHash() == beforeCamera && camera.ComputeViewpointHash() == beforeViewpoint,
                name + ": collection admission happens before camera-state and viewpoint writes.");
            using D facts = Snapshot(owner);
            Check(facts["pending_muzzles"].AsInt32() == 1,
                name + ": failed collection transport never enters the entity/Aquila callback or consumes a muzzle.");
            // The first case changes the rendered position and yaw. Subsequent
            // cases may select the same pose, but all still add their delta.
            if (name == "current computed target projection")
                Check(world.GetNode<Node3D>("PlayerVisual").Transform != beforePlayer,
                    "Deferred target failure follows the player transform writes.");
        }
        WorldSnapshot recovered = basis with { Tick = moved.Tick + 1 };
        RenderPair(world, owner, expected, camera, basis, recovered, 0.375f, 0f, height);
        using D after = Snapshot(owner);
        Check(after["pending_muzzles"].AsInt32() == 0, "A later successful frame consumes the muzzle preserved by failed collection transport.");
    }

    private void CheckDisposedSceneryBoundary(FirstFlightWorldView world, Node owner, ControllerOracle expected,
        GdCameraState camera, WorldSnapshot basis, float height)
    {
        // Use one existing production binding, rather than a duplicate scenery
        // fixture. This is the final world render because its borrowed mesh is
        // deliberately freed; the standalone static check owns broader cases.
        using Variant sceneryValue = owner.Get("_scenery");
        RefCounted scenery = sceneryValue.As<RefCounted>();
        using Variant bindingValue = scenery.Get("_bindings");
        using Godot.Collections.Array bindings = bindingValue.AsGodotArray();
        using Variant beforeValue = scenery.Call("host_snapshot");
        using D before = beforeValue.AsGodotDictionary();
        using Variant shownValue = before["shown_frames"];
        using Variant elapsedValue = before["elapsed_seconds_bits"];
        using Variant rateValue = before["frames_per_second"];
        int[] shown = shownValue.AsInt32Array();
        int fps = rateValue.AsInt32();
        long lap = 1;
        int selectedBinding = -1, selectedLoop = 0;
        MeshInstance3D? selectedNode = null;
        for (int index = 0; index < bindings.Count; index++)
        {
            using Variant rowValue = bindings[index];
            using D row = rowValue.AsGodotDictionary();
            using Variant meshValue = row["mesh"];
            using D mesh = meshValue.AsGodotDictionary();
            using Variant loopValue = mesh["loop_frame_count"];
            using Variant playback = mesh["playback"];
            int loop = loopValue.AsInt32();
            if (loop > 0)
            {
                long a = lap, b = loop;
                while (b != 0) (a, b) = (b, a % b);
                lap = lap / a * loop;
            }
            if (selectedBinding < 0 && loop > 1 && playback.AsInt32() == (int)Level100StaticWorldPlayback.CyclicLoop)
            {
                selectedBinding = index; selectedLoop = loop;
                using Variant nodeValue = row["node"];
                selectedNode = nodeValue.As<MeshInstance3D>();
            }
        }
        Check(selectedBinding >= 0 && selectedNode is not null, "The production scenery includes a borrowed looping mesh.");
        const float delta = 0.051f;
        double elapsed = BitConverter.Int64BitsToDouble(elapsedValue.AsInt64()) + delta;
        double period = lap / (double)fps;
        if (period > 0d && elapsed >= period) elapsed %= period;
        var sourceMesh = new Level100StaticWorldMeshAnimation("fixture", selectedLoop,
            Level100StaticWorldPlayback.CyclicLoop, selectedLoop, "", []);
        int selectedFrame = sourceMesh.SelectVirtualFrame(elapsed, fps);
        Check(selectedFrame != shown[selectedBinding], "The disposal probe selects a different frame, so it cannot pass by skipping the setter.");
        selectedNode!.Free();
        WorldSnapshot current = basis with { Tick = basis.Tick + 20, Mode = VehicleMode.Walker, Transition = VehicleTransition.None };
        expected.Render(basis, current, 0.25f, delta, height);
        Exception failure = CaptureFailure(() => world.Render(basis, current, 0.25f, delta));
        Check(failure.GetType() == typeof(ObjectDisposedException), "World facade retains the scenery setter's exact ObjectDisposedException type.");
        Compare(world, owner, expected, camera);
        using Variant afterValue = scenery.Call("host_snapshot");
        using D after = afterValue.AsGodotDictionary();
        using Variant afterShownValue = after["shown_frames"];
        using Variant afterElapsed = after["elapsed_seconds_bits"];
        int[] afterShown = afterShownValue.AsInt32Array();
        Check(afterElapsed.AsInt64() == BitConverter.DoubleToInt64Bits(elapsed)
            && afterShown[selectedBinding] == selectedFrame,
            "The failed scenery setter retains the double-clock and shown-frame writes from the original driver.");
        for (int index = selectedBinding + 1; index < shown.Length; index++)
            Check(afterShown[index] == shown[index], "A failed scenery setter leaves later binding frames unchanged.");
    }

    private static Exception CaptureFailure(Action action)
    {
        try { action(); }
        catch (Exception failure) { return failure; }
        throw new InvalidOperationException("The explicitly invalid world fixture unexpectedly succeeded.");
    }

    private void Compare(FirstFlightWorldView world, Node owner, ControllerOracle expected, GdCameraState camera)
    {
        Compare(world.GetNode<Node3D>("PlayerVisual").Transform, expected.Player.Transform, "player");
        Compare(world.GetNode<Node3D>("PlayerVisual/BodyPivot").Transform, expected.Body.Transform, "body");
        Compare(world.GetNode<Camera3D>("RetailOpeningAndFirstPersonCamera").Transform, expected.Camera.Transform, "camera");
        var actual = world.GetNode<Camera3D>("RetailOpeningAndFirstPersonCamera");
        Check(Word(actual.Size) == Word(expected.Camera.Size) && actual.FrustumOffset == expected.Camera.FrustumOffset
            && Word(actual.Near) == Word(expected.Camera.Near) && Word(actual.Far) == Word(expected.Camera.Far), "Projection size, raw depths and half-pixel offset retain C# operation order.");
        Compare(world.GetNode<Node3D>("RetailLevel100KempyCube25").Position, expected.Camera.Position, "sky follows camera");
        Check(camera.ComputeCameraHash() == expected.CameraHash && camera.ComputeViewpointHash() == expected.ViewpointHash,
            "Production world controller retains exact camera and engine-viewpoint hashes.");
        using D facts = Snapshot(owner);
        Check(facts["particle_seconds_bits"].AsInt64() == Word(expected.ParticleSeconds)
            && facts["show_hud"].AsBool() == expected.ShowHud && facts["opening_pan"].AsBool() == expected.OpeningPan,
            "Native clocks and display gates match the retained controller.");
        Check(world.ShowHud == expected.ShowHud && world.OpeningPanActive == expected.OpeningPan
            && world.TargetVisualCount == facts["target_count"].AsInt32() && world.ProjectileVisualCount == facts["projectile_count"].AsInt32(),
            "The managed host exposes detached current statistics rather than another presentation owner.");
        CompareTree(world.GetNode<Node3D>("PlayerVisual/BodyPivot/RetailAquilaWalker"), expected.Walker.Root);
        CompareTransition(owner, expected);
    }

    private void CompareTransition(Node owner, ControllerOracle expected)
    {
        Check(Word(owner.Get("_walker_to_jet_visual_elapsed").AsSingle()) == Word(expected.WalkerElapsed)
            && Word(owner.Get("_jet_to_walker_visual_elapsed").AsSingle()) == Word(expected.JetElapsed), "Aquila transition clocks retain exact Single words.");
        Check(owner.Get("_previous_transition").AsInt32() == (int)expected.PreviousTransition
            && owner.Get("_previous_mode").AsInt32() == (int)expected.PreviousMode, "Aquila transition edge memory matches the retained controller.");
        CompareTree(owner.Get("_jet").As<Node3D>(), expected.Jet.Root);
        CompareTree(owner.Get("_cockpit").As<Node3D>(), expected.Cockpit.Root);
    }

    private void CompareTree(Node3D actual, Node3D expected)
    {
        Compare(actual.Transform, expected.Transform, actual.Name.ToString());
        Check(actual.Visible == expected.Visible, "Aquila visibility retains the source handoff/transition gate: " + actual.Name);
        foreach (Node3D child in expected.GetChildren().OfType<Node3D>()) CompareTree(actual.GetNode<Node3D>(child.Name.ToString()), child);
    }
    private void Compare(Transform3D actual, Transform3D expected, string name)
    { Compare(actual.Origin, expected.Origin, name + " origin"); Compare(actual.Basis.X, expected.Basis.X, name + " X"); Compare(actual.Basis.Y, expected.Basis.Y, name + " Y"); Compare(actual.Basis.Z, expected.Basis.Z, name + " Z"); }
    private void Compare(Vector3 actual, Vector3 expected, string name)
    { for (int axis = 0; axis < 3; axis++) Check(Word(actual[axis]) == Word(expected[axis]), $"{name}[{axis}]: {Word(actual[axis]):x8} != {Word(expected[axis]):x8}"); }
    private static WorldSnapshot Shift(WorldSnapshot source, int x) => source with
    { PlayerPosition = new(source.PlayerPosition.X + x, source.PlayerPosition.Z),
        WalkerFeet = source.WalkerFeet.Select(foot => foot with { Position = new(foot.Position.X + x, foot.Position.Z) }).ToArray() };
    private static D Snapshot(Node owner) { using Variant value = owner.Call("host_snapshot"); return value.AsGodotDictionary(); }
    private static uint Word(float value) => BitConverter.SingleToUInt32Bits(value);
    private static void Require(Variant result)
    { using D value = result.AsGodotDictionary(); if (!value["ok"].AsBool()) throw new InvalidOperationException(value.ToString()); }
    private void Check(bool condition, string message) { _checks++; if (!condition) throw new InvalidOperationException(message); }
    private void Expect<T>(Action action, string message) where T : Exception
    { try { action(); } catch (T) { Check(true, message); return; } throw new InvalidOperationException(message); }
    private void Done(string group) { _completed.Add(group); GD.Print("WORLD_PRESENTATION_SECTION: " + group); }

    // Both controllers start from the same packed node state. A serialized
    // rotation can decompose to a scale one ULP below one; assigning Rotation
    // preserves that scale. An identity-node oracle changes the initial state
    // before exercising any of the retained C# arithmetic.
    private readonly record struct InitialNodePose(Transform3D Transform, EulerOrder RotationOrder,
        bool TopLevel, bool DisableScale)
    {
        internal static InitialNodePose Capture(Node3D node) =>
            new(node.Transform, node.RotationOrder, node.TopLevel, node.IsScaleDisabled());
        internal void Apply(Node3D node)
        {
            node.RotationOrder = RotationOrder;
            node.TopLevel = TopLevel;
            node.SetDisableScale(DisableScale);
            node.Transform = Transform;
        }
    }

    private sealed class Leaf
    {
        internal Node3D Root { get; }
        internal Leaf(Node3D original)
        {
            Root = (Node3D)original.Duplicate();
            using Variant result = Root.Call("configure_prepared", default(Variant), true, false);
            Require(result);
        }
        internal void SetVirtualFrame(float frame) { using Variant result = Root.Call("set_virtual_frame", frame); Require(result); }
        internal void SetGroundContactPose(Vector3[] contacts) { using Variant result = Root.Call("set_ground_contact_pose", contacts); Require(result); }
    }

    private sealed class ControllerOracle : IDisposable
    {
        private const float UnitsToMeters = 0.001f;
        private const float RetailWalkerCenterOfGravityHeight = Level100Terrain.WalkerCenterOfGravityMillimeters * UnitsToMeters;
        private const float RetailAquilaAnimationHz = 20f;
        private const float RetailJetWalkToFlySeconds = 25f / RetailAquilaAnimationHz;
        private const float RetailJetFlyToWalkSeconds = 25f / RetailAquilaAnimationHz;
        private const float RetailCockpitWalkToFlySeconds = 23f / RetailAquilaAnimationHz;
        private const float RetailCockpitFlyToWalkSeconds = 24f / RetailAquilaAnimationHz;
        private readonly Node3D _root = new();
        private readonly Node3D _playerRoot = new();
        private readonly Node3D _playerBodyPivot = new();
        private readonly Camera3D _camera = new() { Near = 0.1f, Far = 700f, Projection = Camera3D.ProjectionType.Frustum, Current = false };
        private readonly Leaf _walkerAsset, _jetAsset, _cockpitAsset;
        private readonly AttachedPanCameraState _cameraState = new(SimulationConstants.Level100OpeningPanTicks, Level100MissionTiming.ReleasedEventFrameTicks);
        private readonly Level100EngineViewpointState _viewpoint = new(0.1f, 700f);
        private float _particlePresentationSeconds;
        private float _walkerToJetVisualElapsed = float.PositiveInfinity;
        private float _jetToWalkerVisualElapsed = float.PositiveInfinity;
        private VehicleTransition _previousTransition;
        private VehicleMode _previousMode = VehicleMode.Walker;
        internal Node3D Player => _playerRoot;
        internal Node3D Body => _playerBodyPivot;
        internal Camera3D Camera => _camera;
        internal Leaf Walker => _walkerAsset;
        internal Leaf Jet => _jetAsset;
        internal Leaf Cockpit => _cockpitAsset;
        internal float ParticleSeconds => _particlePresentationSeconds;
        internal float WalkerElapsed => _walkerToJetVisualElapsed;
        internal float JetElapsed => _jetToWalkerVisualElapsed;
        internal VehicleTransition PreviousTransition => _previousTransition;
        internal VehicleMode PreviousMode => _previousMode;
        internal bool ShowHud { get; private set; }
        internal bool OpeningPan { get; private set; }
        internal string CameraHash => _cameraState.CurrentSnapshot.ComputeHash();
        internal string ViewpointHash => _viewpoint.ComputeHash();
        internal ControllerOracle(FirstFlightWorldView world, SubViewport viewport, InitialNodePose[] authoredPoses)
        {
            authoredPoses[0].Apply(_root);
            authoredPoses[1].Apply(_playerRoot);
            authoredPoses[2].Apply(_playerBodyPivot);
            authoredPoses[3].Apply(_camera);
            _walkerAsset = new(world.GetNode<Node3D>("PlayerVisual/BodyPivot/RetailAquilaWalker"));
            _jetAsset = new(world.GetNode<Node3D>("PlayerVisual/BodyPivot/RetailAquilaJet"));
            _cockpitAsset = new(world.GetNode<Node3D>("RetailOpeningAndFirstPersonCamera/RetailAquilaCockpit"));
            viewport.AddChild(_root); _root.AddChild(_playerRoot); _playerRoot.AddChild(_playerBodyPivot); _root.AddChild(_camera);
            _playerBodyPivot.AddChild(_walkerAsset.Root); _playerBodyPivot.AddChild(_jetAsset.Root); _camera.AddChild(_cockpitAsset.Root);
        }
        internal void Render(WorldSnapshot previous, WorldSnapshot current, float interpolationAlpha, float frameDelta, float height)
        {
            _particlePresentationSeconds += Math.Max(frameDelta, 0f);
            Vector3 previousPosition = ToPlayerWorld(previous), currentPosition = ToPlayerWorld(current);
            bool resetJump = previousPosition.DistanceSquaredTo(currentPosition) > 100f;
            _playerRoot.Position = resetJump ? currentPosition : previousPosition.Lerp(currentPosition, interpolationAlpha);
            float playerYaw = Mathf.LerpAngle(previous.FacingYawMicroRad / 1_000_000f, current.FacingYawMicroRad / 1_000_000f, interpolationAlpha);
            float playerPitch = Mathf.Lerp(previous.FacingPitchMicroRad / 1_000_000f, current.FacingPitchMicroRad / 1_000_000f, interpolationAlpha);
            float playerRoll = Mathf.LerpAngle(previous.BodyRollMicroRad / 1_000_000f, current.BodyRollMicroRad / 1_000_000f, interpolationAlpha);
            _playerRoot.Rotation = new(0f, playerYaw, 0f);
            _playerBodyPivot.Rotation = current.Mode == VehicleMode.Jet && current.Transition == VehicleTransition.None ? new(-playerPitch, 0f, -playerRoll) : Vector3.Zero;
            Vector3[] contacts = ToFootOffsets(current);
            Vector3[]? prior = null;
            if (!resetJump && !ReferenceEquals(previous, current) && previous.WalkerFeet.Count == current.WalkerFeet.Count)
            {
                prior = ToFootOffsets(previous);
            }
            AdmitOriginalCollectionTransport(previous, current);
            if (prior is not null)
            {
                for (int index = 0; index < contacts.Length; index++)
                {
                    Level100RenderVector3 value = Level100RenderInterpolation.InterpolatePosition(
                        new(prior[index].X, prior[index].Y, prior[index].Z), new(contacts[index].X, contacts[index].Y, contacts[index].Z), interpolationAlpha, 3f);
                    contacts[index] = new(value.X, value.Y, value.Z);
                }
            }
            ApplyWalkerPose(contacts, playerYaw);
            UpdateAquilaTransitionPresentation(current, frameDelta);
            _cameraState.Advance(previous, current);
            AttachedPanCameraViewSnapshot camera = _cameraState.Sample(interpolationAlpha);
            EngineViewpointSnapshot selected = _viewpoint.Bind(camera);
            ShowHud = camera.HudVisible; OpeningPan = camera.OpeningPanActive;
            UpdatePlayerShape(current, ShowHud);
            _camera.Size = 2f * selected.NearPlane * 0.75f * camera.Zoom;
            _camera.Position = new(camera.Pose.Position.X, camera.Pose.Position.Y, camera.Pose.Position.Z);
            _camera.LookAt(_camera.Position + new Vector3(camera.Pose.Forward.X, camera.Pose.Forward.Y, camera.Pose.Forward.Z), new(camera.Pose.Up.X, camera.Pose.Up.Y, camera.Pose.Up.Z));
            if (height > 0f) { float unitsPerPixel = _camera.Size / height; float offset = unitsPerPixel * 0.5f; _camera.FrustumOffset = new(-offset, offset); }
        }
        internal void Transition(WorldSnapshot snapshot, float delta) => UpdateAquilaTransitionPresentation(snapshot, delta);
        public void Dispose() { if (GodotObject.IsInstanceValid(_root)) _root.Free(); }

        private static void AdmitOriginalCollectionTransport(WorldSnapshot previous, WorldSnapshot current)
        {
            // 1bb29345 FirstFlightWorldView.Entities.cs:EntityFrameFacts built
            // both target projections, then both projectile arrays, after pure
            // foot conversion and before entering native render_frame. The
            // computed Targets getters materialize their complete projections;
            // projectile transport dereferenced Id first for every source row.
            bool same = ReferenceEquals(previous, current);
            if (!same) _ = previous.Targets;
            _ = current.Targets;
            if (!same) foreach (ProjectileSnapshot projectile in previous.Projectiles) _ = projectile.Id;
            foreach (ProjectileSnapshot projectile in current.Projectiles) _ = projectile.Id;
        }
        // The following five method bodies are retained verbatim from 1bb29345.

        private void UpdatePlayerShape(WorldSnapshot snapshot, bool attachedView)
        {
            // The released pan camera hides the HUD/cockpit and renders the
            // exterior Aquila. Its first-person handoff reverses that visibility.
            bool showingJet =
                float.IsFinite(_walkerToJetVisualElapsed) ||
                float.IsFinite(_jetToWalkerVisualElapsed) ||
                snapshot.Transition != VehicleTransition.None ||
                snapshot.Mode == VehicleMode.Jet;
            _walkerAsset.Root.Visible = !attachedView && !showingJet;
            _jetAsset.Root.Visible = !attachedView && showingJet;
            _cockpitAsset.Root.Visible = attachedView;
            _playerBodyPivot.Position = showingJet
                ? Vector3.Up * RetailWalkerCenterOfGravityHeight
                : Vector3.Zero;
        }

        private void UpdateAquilaTransitionPresentation(WorldSnapshot snapshot, float frameDelta)
        {
            bool walkerToJetStarted =
                snapshot.Transition == VehicleTransition.WalkerToJet &&
                _previousTransition != VehicleTransition.WalkerToJet;
            bool jetToWalkerStarted =
                snapshot.Transition == VehicleTransition.JetToWalker &&
                _previousTransition != VehicleTransition.JetToWalker;
            bool returnedToWalker = snapshot.Transition == VehicleTransition.None &&
                snapshot.Mode == VehicleMode.Walker &&
                (_previousTransition != VehicleTransition.None ||
                 _previousMode == VehicleMode.Jet);

            if (walkerToJetStarted)
            {
                _walkerToJetVisualElapsed = 0f;
                _jetToWalkerVisualElapsed = float.PositiveInfinity;
            }
            else if (jetToWalkerStarted)
            {
                _walkerToJetVisualElapsed = float.PositiveInfinity;
                _jetToWalkerVisualElapsed = 0f;
            }
            else if (returnedToWalker)
            {
                _walkerToJetVisualElapsed = float.PositiveInfinity;
                _jetToWalkerVisualElapsed = float.PositiveInfinity;
            }

            if (float.IsFinite(_walkerToJetVisualElapsed))
            {
                _walkerToJetVisualElapsed = Math.Min(
                    _walkerToJetVisualElapsed + Math.Max(0f, frameDelta),
                    RetailJetWalkToFlySeconds);
                int jetStep = Math.Min(
                    Mathf.FloorToInt(_walkerToJetVisualElapsed * RetailAquilaAnimationHz),
                    25);
                _jetAsset.SetVirtualFrame(25f + jetStep);

                if (_walkerToJetVisualElapsed < RetailCockpitWalkToFlySeconds)
                {
                    int cockpitStep = Math.Min(
                        Mathf.FloorToInt(_walkerToJetVisualElapsed * RetailAquilaAnimationHz),
                        22);
                    _cockpitAsset.SetVirtualFrame(27f + cockpitStep);
                }
                else
                {
                    _cockpitAsset.SetVirtualFrame(0f);
                }

                if (_walkerToJetVisualElapsed >= RetailJetWalkToFlySeconds)
                {
                    _jetAsset.SetVirtualFrame(0f);
                    _walkerToJetVisualElapsed = float.PositiveInfinity;
                }
            }
            else if (float.IsFinite(_jetToWalkerVisualElapsed))
            {
                _jetToWalkerVisualElapsed = Math.Min(
                    _jetToWalkerVisualElapsed + Math.Max(0f, frameDelta),
                    RetailJetFlyToWalkSeconds);
                int jetStep = Math.Min(
                    Mathf.FloorToInt(_jetToWalkerVisualElapsed * RetailAquilaAnimationHz),
                    25);
                _jetAsset.SetVirtualFrame(jetStep);

                int cockpitStep = Math.Min(
                    Mathf.FloorToInt(_jetToWalkerVisualElapsed * RetailAquilaAnimationHz),
                    24);
                _cockpitAsset.SetVirtualFrame(1f + cockpitStep);
                if (_jetToWalkerVisualElapsed >= RetailCockpitFlyToWalkSeconds)
                {
                    _cockpitAsset.SetVirtualFrame(25f);
                }
                if (_jetToWalkerVisualElapsed >= RetailJetFlyToWalkSeconds)
                {
                    _jetAsset.SetVirtualFrame(25f);
                    _jetToWalkerVisualElapsed = float.PositiveInfinity;
                }
            }
            else if (snapshot.Mode == VehicleMode.Jet)
            {
                _jetAsset.SetVirtualFrame(0f);
                _cockpitAsset.SetVirtualFrame(0f);
            }
            else
            {
                _jetAsset.SetVirtualFrame(25f);
                _cockpitAsset.SetVirtualFrame(25f);
            }

            _previousTransition = snapshot.Transition;
            _previousMode = snapshot.Mode;
        }

        private void ApplyWalkerPose(Vector3[] contacts, float renderedYaw)
        {
            // The legs are drawn in the player root's rendered frame, so the
            // world-to-player rotation must use the interpolated yaw the root is
            // actually carrying this frame.
            Basis worldToPlayer = new Basis(Vector3.Up, renderedYaw).Inverse();
            for (int foot = 0; foot < contacts.Length; foot++)
            {
                contacts[foot] = worldToPlayer * contacts[foot];
            }

            _walkerAsset.SetGroundContactPose(contacts);
        }

        private static Vector3[] ToFootOffsets(WorldSnapshot snapshot)
        {
            if (snapshot.WalkerFeet.Count != 4)
            {
                throw new InvalidDataException("Core did not expose four Aquila foot contacts.");
            }

            var contacts = new Vector3[4];
            foreach (WalkerFootContactSnapshot foot in snapshot.WalkerFeet)
            {
                if (foot.Id < 0 || foot.Id >= contacts.Length)
                {
                    throw new InvalidDataException($"Core exposed unknown Aquila foot {foot.Id}.");
                }
                contacts[foot.Id] = new Vector3(
                    (foot.Position.X - snapshot.PlayerPosition.X) * UnitsToMeters,
                    (foot.GroundElevationMillimeters + foot.LiftMillimeters -
                        snapshot.PlayerGroundElevationMillimeters) * UnitsToMeters,
                    -(foot.Position.Z - snapshot.PlayerPosition.Z) * UnitsToMeters);
            }

            return contacts;
        }

        private static Vector3 ToPlayerWorld(WorldSnapshot snapshot)
        {
            float x = snapshot.PlayerPosition.X * UnitsToMeters;
            float z = snapshot.PlayerPosition.Z * UnitsToMeters;
            return new Vector3(
                x,
                (snapshot.PlayerElevationMillimeters -
                    Level100Terrain.WalkerCenterOfGravityMillimeters) * UnitsToMeters,
                -z);
        }
    }
}
