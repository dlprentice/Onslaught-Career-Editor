// SPDX-License-Identifier: GPL-3.0-or-later
using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Actual Godot bridge and production world consumer, using the retained pure
/// C# owners only as test oracles. No game host, input injection or capture.
/// </summary>
public sealed partial class CameraBridgeChecks : Node
{
    private int _checks;

    public override async void _Ready()
    {
        try
        {
            Input.MouseModeEnum pointerBefore = Input.MouseMode;
            var session = new InteractiveSession(0x4f4e534c, Level100StaticWorldAsset.LoadActorDefinitions());
            WorldSnapshot basis = session.CurrentSnapshot;
            CheckPureBridge(basis);

            var viewport = new SubViewport { Size = new(640, 480), OwnWorld3D = true,
                RenderTargetUpdateMode = SubViewport.UpdateMode.Disabled };
            AddChild(viewport);
            var world = FirstFlightWorldView.InstantiateScene();
            Node presentation = world.GetNode("WorldPresentation");
            using var bridge = new GdCameraState(presentation);
            Camera3D camera = world.GetNode<Camera3D>("RetailOpeningAndFirstPersonCamera");
            Transform3D authored = camera.Transform;
            Check(!bridge.IsInitialized, "Instantiating the production scene creates no live native camera owner.");
            Expect<InvalidOperationException>(() => _ = bridge.SelectedSnapshot,
                "An uninitialized borrowed observer cannot lazily create the production camera.");
            Check(!bridge.IsInitialized, "The refused observer read leaves the world frozen.");
            viewport.AddChild(world);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            Check(!bridge.IsInitialized && camera.Transform == authored,
                "Entering the tree leaves the authored camera frozen until explicit gameplay initialization.");
            var reference = new AttachedPanCameraState(SimulationConstants.Level100OpeningPanTicks, Level100MissionTiming.ReleasedEventFrameTicks);
            var engineReference = new Level100EngineViewpointState(0.1f, 700f);
            var expectedCamera = new Camera3D { Current = false };
            viewport.AddChild(expectedCamera);
            world.Initialize(basis);
            reference.Advance(basis, basis);
            CompareConsumer(world, bridge, camera, expectedCamera, reference.Sample(0f), engineReference);
            Check(bridge.IsInitialized && !bridge.IsDisposed, "Explicit world initialization starts the native camera owner.");
            using (var temporary = new GdCameraState(presentation))
            {
                string hash = temporary.ComputeCameraHash();
                temporary.Dispose();
                Check(temporary.IsDisposed && !temporary.IsInitialized && bridge.ComputeCameraHash() == hash,
                    "Disposing one borrowed observer leaves the production camera and another observer intact.");
            }
            string originalCoreHash = StateHasher.ComputeHex(basis);

            WorldSnapshot previous = basis;
            foreach ((int tick, int remaining, int xOffset, int zoom, bool attached, VehicleMode mode) in new[]
            {
                (1, 119, 100, 1000, true, VehicleMode.Walker),
                (60, 60, 200, 900, true, VehicleMode.Walker),
                (118, 2, 300, 800, true, VehicleMode.Walker),
                (119, 1, 400, 600, true, VehicleMode.Walker),
                (120, 0, 500, 400, true, VehicleMode.Jet),
                (121, 0, 25_000, 700, true, VehicleMode.Jet),
                (122, 0, 25_100, 800, false, VehicleMode.Jet),
                (123, 0, 25_200, 900, true, VehicleMode.Walker),
                (1, 119, 0, 1000, true, VehicleMode.Walker),
            })
            {
                WorldSnapshot current = basis with { Tick = tick, Level100OpeningTicksRemaining = remaining,
                    PlayerPosition = new(basis.PlayerPosition.X + xOffset, basis.PlayerPosition.Z),
                    FacingYawMicroRad = basis.FacingYawMicroRad + 11000 * tick, FacingPitchMicroRad = tick * 230,
                    BodyRollMicroRad = tick * -170, ZoomPermille = zoom, Mode = mode, Transition = VehicleTransition.None,
                    Level100Actors = basis.Level100Actors with { Actors = basis.Level100Actors.Actors
                        .Where(actor => attached || actor.Name != "Player 1").ToArray() } };
                foreach (float alpha in new[] { 0f, 0.5f, 1f })
                {
                    string before = StateHasher.ComputeHex(current);
                    world.Render(previous, current, alpha, 0f);
                    AttachedPanCameraSnapshot expectedState = reference.Advance(previous, current);
                    Check(bridge.ComputeCameraHash() == expectedState.ComputeHash(), "The actual world consumer advances the native camera with exact frame facts.");
                    Check(bridge.CurrentSnapshot.ComputeHash() == expectedState.ComputeHash(), "Managed snapshot diagnostics preserve every native raw word.");
                    CompareConsumer(world, bridge, camera, expectedCamera, reference.Sample(alpha), engineReference);
                    Check(StateHasher.ComputeHex(current) == before, "Camera/render facts do not mutate Core snapshots.");
                }
                previous = current;
            }
            Check(StateHasher.ComputeHex(basis) == originalCoreHash, "The initial Core snapshot remains unchanged.");
            string retainedHash = bridge.ComputeCameraHash();
            viewport.RemoveChild(world);
            Check(!bridge.IsDisposed && bridge.ComputeCameraHash() == retainedHash,
                "Leaving the tree does not discard the native camera lifecycle.");
            viewport.AddChild(world);
            Check(bridge.ComputeCameraHash() == retainedHash, "Reentering the tree preserves the same camera state.");
            Check(world.GetNode<Camera3D>("RetailOpeningAndFirstPersonCamera") == camera,
                "The renderer keeps the authored production Camera3D throughout the migration.");
            world.Free();
            Check(bridge.IsDisposed && !bridge.IsInitialized, "Final node deletion releases the native camera owner.");
            Expect<ObjectDisposedException>(() => _ = bridge.SelectedSnapshot, "A deleted world cannot recreate its camera state.");
            bridge.Dispose(); // Idempotent cleanup cannot resurrect the owner.
            Check(Input.MouseMode == pointerBefore, "Camera operations never take pointer ownership.");
            viewport.QueueFree();
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            GD.Print($"CAMERA_BRIDGE_CHECKS: {_checks} passed; native/C# exact facts, words and hashes, production Camera3D, handoff, no-attachment, teleport, frozen initialization and final disposal.");
            GetTree().Quit(0);
        }
        catch (Exception error)
        {
            GD.PushError(error.ToString());
            GetTree().Quit(1);
        }
    }

    private void CheckPureBridge(WorldSnapshot basis)
    {
        uint[] words = [0, 0x80000000, 1, 0x80000001, 0x7f7fffff, 0xff7fffff,
            0x7f800000, 0xff800000, 0x7fc00000, 0xffc00001, 0x7f800001, 0xff800001];
        foreach (uint word in words)
        {
            float depth = BitConverter.UInt32BitsToSingle(word);
            using var bridge = new GdCameraState(120, 1, depth, depth);
            Check(!bridge.IsInitialized, "Bridge construction is lazy for every raw depth word.");
            var engine = new Level100EngineViewpointState(depth, depth);
            CheckViewpoint(bridge.SelectedSnapshot, engine.SelectedSnapshot);
            Check(bridge.ComputeViewpointHash() == engine.ComputeHash(), "Raw depth words survive the real managed/native boundary.");
            Expect<InvalidOperationException>(() => _ = bridge.CurrentSnapshot, "The native camera starts without an event frame.");
            Expect<ArgumentOutOfRangeException>(() => bridge.SampleAndBind(float.NaN), "Invalid alpha is rejected before no-frame state.");
            Expect<InvalidOperationException>(() => bridge.SampleAndBind(0f), "A valid sample requires an event frame.");
        }
        using var native = new GdCameraState(120, 1, 0.1f, 700f);
        var reference = new AttachedPanCameraState(120, 1);
        var engineReference = new Level100EngineViewpointState(0.1f, 700f);
        WorldSnapshot previous = basis;
        for (int index = 0; index < 16; index++)
        {
            WorldSnapshot current = basis with { Tick = index + 1, Level100OpeningTicksRemaining = 119 - index,
                FacingYawMicroRad = unchecked(int.MaxValue - index * 100000001), FacingPitchMicroRad = int.MinValue + index,
                BodyRollMicroRad = -1000000 * index, PlayerPosition = new(index == 0 ? int.MinValue : int.MaxValue - index, int.MinValue),
                PlayerElevationMillimeters = int.MaxValue - index };
            native.Advance(previous, current);
            AttachedPanCameraSnapshot snapshot = reference.Advance(previous, current);
            Check(native.ComputeCameraHash() == snapshot.ComputeHash(), "Int32 boundary facts retain exact float32 conversion and camera hashes.");
            Check(native.CurrentSnapshot.ComputeHash() == snapshot.ComputeHash(), "Returned snapshot words have not passed through native float conversion.");
            foreach (float alpha in new[] { -0f, 0.25f, 0.5f, 1f })
            {
                (AttachedPanCameraViewSnapshot camera, EngineViewpointSnapshot viewpoint) = native.SampleAndBind(alpha);
                AttachedPanCameraViewSnapshot expected = reference.Sample(alpha);
                CheckView(camera, expected);
                CheckViewpoint(viewpoint, engineReference.Bind(expected));
                Check(native.ComputeViewpointHash() == engineReference.ComputeHash(), "Sampling and slot binding share one native operation.");
            }
            previous = current;
        }
        string beforeHash = native.ComputeCameraHash();
        native.Advance(previous with { Level100Actors = null!, Level100OpeningTicksRemaining = int.MinValue }, previous);
        Check(native.ComputeCameraHash() == beforeHash, "Current-frame idempotence ignores malformed previous facts without eager bridge failure.");
        Expect<ArgumentNullException>(() => native.Advance(null!, previous), "Null previous is checked even for a repeated current frame.");
        Expect<ArgumentOutOfRangeException>(() => native.SampleAndBind(BitConverter.UInt32BitsToSingle(0x3f800001)), "Alpha above one is rejected at the native boundary.");
        Check(native.ComputeCameraHash() == beforeHash, "Refused samples and null frames preserve camera state.");

        // A name that merely begins with Player 1 must not match after an
        // embedded NUL is truncated by the Godot String marshaler.
        WorldSnapshot notPlayer = basis with { Tick = 119, Level100OpeningTicksRemaining = 1,
            Level100Actors = basis.Level100Actors with { Actors = basis.Level100Actors.Actors
                .Select(actor => actor.Name == "Player 1" ? actor with { Name = "Player 1\0ignored\ud800" } : actor).ToArray() } };
        native.Advance(previous, notPlayer);
        reference.Advance(previous, notPlayer);
        Check(native.ComputeCameraHash() == reference.CurrentSnapshot.ComputeHash(), "Raw UTF-16 name facts preserve exact attachment matching.");
        CheckView(native.SampleAndBind(1f).Camera, reference.Sample(1f));
    }

    private void CompareConsumer(FirstFlightWorldView world, GdCameraState bridge, Camera3D actual,
        Camera3D expectedNative, AttachedPanCameraViewSnapshot expected, Level100EngineViewpointState engine)
    {
        EngineViewpointSnapshot selected = engine.Bind(expected);
        CheckViewpoint(bridge.SelectedSnapshot, selected);
        Check(bridge.ComputeViewpointHash() == engine.ComputeHash(), "Live engine envelope remains identical to the retained reference.");
        Check(world.ShowHud == expected.HudVisible && world.OpeningPanActive == expected.OpeningPanActive,
            "Production HUD and opening-pan gates use the native sampled view.");
        Vector3 position = Vector(expected.Pose.Position);
        expectedNative.Position = position;
        expectedNative.LookAt(position + Vector(expected.Pose.Forward), Vector(expected.Pose.Up));
        Check(actual.Transform == expectedNative.Transform, "The existing native Camera3D receives the exact reference pose.");
        Check(Word(actual.Near) == Word(selected.NearPlane) && Word(actual.Far) == Word(selected.FarPlane),
            "The production near/far plane words remain unchanged.");
        float size = 2f * selected.NearPlane * 0.75f * expected.Zoom;
        Check(Word(actual.Size) == Word(size) && actual.Projection == Camera3D.ProjectionType.Frustum,
            "The existing frustum and zoom extent are preserved.");
        float offset = size / 480f * 0.5f;
        Check(actual.FrustumOffset == new Vector2(-offset, offset), "The existing half-pixel projection correction remains exact.");
    }

    private void CheckView(AttachedPanCameraViewSnapshot actual, AttachedPanCameraViewSnapshot expected)
    {
        Check(actual.AttachedThingId == expected.AttachedThingId && actual.HudVisible == expected.HudVisible && actual.OpeningPanActive == expected.OpeningPanActive,
            "Sampled attachment and presentation gates agree.");
        Check(Word(actual.Zoom) == Word(expected.Zoom), "Sampled zoom retains its raw word.");
        CheckVector(actual.Pose.Position, expected.Pose.Position);
        CheckVector(actual.Pose.Forward, expected.Pose.Forward);
        CheckVector(actual.Pose.Up, expected.Pose.Up);
    }

    private void CheckViewpoint(EngineViewpointSnapshot actual, EngineViewpointSnapshot expected) => Check(
        actual.SelectedSlot == expected.SelectedSlot && actual.SelectedSlotState == expected.SelectedSlotState &&
        actual.CurrentViewport == expected.CurrentViewport && Word(actual.NearPlane) == Word(expected.NearPlane) && Word(actual.FarPlane) == Word(expected.FarPlane),
        "Selected viewpoint identity, null viewport and raw depths agree.");
    private void CheckVector(Level100RenderVector3 actual, Level100RenderVector3 expected) => Check(
        Word(actual.X) == Word(expected.X) && Word(actual.Y) == Word(expected.Y) && Word(actual.Z) == Word(expected.Z),
        "Pose vector retains all three exact float words.");
    private static Vector3 Vector(Level100RenderVector3 value) => new(value.X, value.Y, value.Z);
    private static uint Word(float value) => BitConverter.SingleToUInt32Bits(value);
    private void Check(bool condition, string message)
    {
        _checks++;
        if (!condition) throw new InvalidOperationException(message);
    }
    private void Expect<T>(Action action, string message) where T : Exception
    {
        try { action(); }
        catch (T) { Check(true, message); return; }
        throw new InvalidOperationException(message);
    }
}
