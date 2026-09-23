// SPDX-License-Identifier: GPL-3.0-or-later
using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using Array = Godot.Collections.Array;
using Dictionary = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

/// <summary>Actual native scene/managed facts boundary. Retained Client laws are
/// test oracles only; the production host owns no competing entity state.</summary>
public sealed partial class EntityBridgeChecks : Node
{
    private int _checks;
    private readonly System.Collections.Generic.Dictionary<int, Node3D> _referenceProjectiles = [];
    private readonly System.Collections.Generic.Dictionary<int, Level100ProjectileTrailHistory> _referenceTrails = [];
    private readonly System.Collections.Generic.Dictionary<Level100ActorId, Level100TargetVisualDescriptor> _referenceTargets = [];

    public override async void _Ready()
    {
        try
        {
            var pointer = Input.MouseMode;
            var session = new InteractiveSession(0x4f4e534c, Level100StaticWorldAsset.LoadActorDefinitions());
            WorldSnapshot basis = session.CurrentSnapshot with
            {
                Level100Actors = session.CurrentSnapshot.Level100Actors with { Actors = [] },
                Projectiles = [],
            };
            string initialHash = StateHasher.ComputeHex(session.CurrentSnapshot);
            CompareProductionTexturePages();
            CompareMuzzleAnimation();
            var viewport = new SubViewport { Size = new(320, 240), OwnWorld3D = true,
                RenderTargetUpdateMode = SubViewport.UpdateMode.Disabled };
            AddChild(viewport);
            var world = new Node3D();
            var referenceWorld = new Node3D();
            viewport.AddChild(world);
            viewport.AddChild(referenceWorld);
            var camera = new Camera3D { Position = new(4, 2, 8), Current = false };
            world.AddChild(camera);
            using PackedScene scene = GD.Load<PackedScene>(FirstFlightWorldView.EntityScenePath);
            Node owner = scene.Instantiate();
            world.AddChild(owner);
            using var assets = new Array();
            foreach (Level100TargetVisualBinding binding in Level100TargetPresentation.RenderedBindings)
            {
                using var mesh = new BoxMesh();
                using Variant meshValue = mesh;
                using var entry = new Dictionary { ["definition_name"] = binding.DefinitionName,
                    ["mesh_binding"] = binding.MeshBinding, ["mesh"] = meshValue };
                using Variant entryValue = entry;
                assets.Add(entryValue);
            }
            using var initialTargets = new Array();
            using Variant assetValues = assets;
            using Variant targetValues = initialTargets;
            using Variant configuredValue = owner.Call("configure", world, camera, assetValues, targetValues);
            using Dictionary configured = Result(configuredValue);

            WorldSnapshot previous = basis;
            for (int step = 0; step < 32; step++)
            {
                Level100ActorSnapshot[] actors = Enumerable.Range(0, 6)
                    .Select(index => Actor(index, step)).Reverse().ToArray();
                // An absent actor intentionally retains its previous visual;
                // an inactive actor remains registered and explicitly hidden.
                if (step % 7 == 4) actors = actors.Where(value => value.ActorId.Value != 3).ToArray();
                ProjectileSnapshot[] projectiles = step % 8 == 7 ? [] :
                [
                    new(100 + step / 8, Level100ProjectileKind.MechPulseBoltMedium,
                        new(3000 + step * 170, 7000 - step * 230), new(170, -230), 1500 + step * 19, 19, 120 - step % 8),
                    new(200 + step / 8, step % 2 == 0 ? Level100ProjectileKind.MechBullet : Level100ProjectileKind.MechAirBullet,
                        new(-2000 + step * 77, 3000 + step * 150), new(77, 150), 2100 - step * 8, -8, 20 - step % 8),
                ];
                WorldSnapshot current = basis with { Tick = step + 1,
                    Level100Actors = basis.Level100Actors with { Actors = actors }, Projectiles = projectiles,
                    WalkerFeet = basis.WalkerFeet.Select(foot => foot with { Position = new(foot.Position.X + step * 15,
                        foot.Position.Z - step * 11), LiftMillimeters = foot.LiftMillimeters + step * 4 }).ToArray() };
                // A duplicate previous identity must select its last pose,
                // rather than a sorted/ordinal or first-match substitute.
                if (step == 9 && previous.Level100Actors.Actors.Count > 0)
                {
                    Level100ActorSnapshot duplicate = previous.Level100Actors.Actors[0];
                    duplicate = duplicate with { Pose = duplicate.Pose with { PositionMillimeters = new(
                        duplicate.Pose.PositionMillimeters.X + 19, duplicate.Pose.PositionMillimeters.Y + 23,
                        duplicate.Pose.PositionMillimeters.Z + 29) } };
                    previous = previous with { Level100Actors = previous.Level100Actors with {
                        Actors = previous.Level100Actors.Actors.Concat([duplicate]).ToArray() } };
                }
                if (step == 16)
                {
                    world.Transform = new Transform3D(new Basis(Vector3.Up, 0.3f), new(3, 0, 4));
                    referenceWorld.Transform = world.Transform;
                }
                foreach (float alpha in new[] { 0f, 0.25f, 0.5f, 1f })
                {
                    int callbacks = 0;
                    using Dictionary facts = EntityFrameFacts(previous, current, alpha,
                        resetJump: step == 12, pendingMuzzles: 0);
                    Callable stage = Callable.From<Array, Dictionary>(feet =>
                    {
                        callbacks++;
                        CompareFeet(previous, current, alpha, step == 12, feet);
                        return new Dictionary { ["ok"] = true };
                    });
                    using Variant factValues = facts;
                    using Variant frameResult = owner.Call("render_frame", factValues, stage);
                    using Dictionary result = Result(frameResult);
                    Check(callbacks == 1, "Exactly one Aquila stage callback per native render batch.");
                    CompareTargets(owner, world, previous, current, alpha);
                    CompareProjectiles(owner, world, referenceWorld, camera, previous, current, alpha);
                    Check(result["projectile_count"].AsInt32() == current.Projectiles.Count, "Projectile diagnostics reflect the native owner.");
                    Check(result["target_count"].AsInt32() == _referenceTargets.Values.Count(value => value.Visible), "Visible actor diagnostics reflect retained/inactive actors.");
                }
                previous = current;
            }
            // Reference-equal snapshots deliberately suppress previous joins.
            using (Dictionary same = EntityFrameFacts(previous, previous, 0.5f, false, 0))
            {
                Check(same["same_snapshot"].AsBool() && same["previous_targets"].AsGodotArray().Count == 0 &&
                    same["previous_projectiles"].AsGodotArray().Count == 0 && same["previous_feet"].VariantType == Variant.Type.Nil,
                    "The actual host facts preserve the reference-equal snapshot gate.");
            }
            Check(StateHasher.ComputeHex(session.CurrentSnapshot) == initialHash, "Presentation leaves source Core state unchanged.");
            Check(Input.MouseMode == pointer, "The actual entity boundary never takes pointer ownership.");
            world.Free();
            referenceWorld.Free();
            viewport.QueueFree();
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            GD.Print($"ENTITY_BRIDGE_CHECKS: {_checks} passed; exact actor matrices, foot words, projectile poses, trail vertices/UVs, identity and retained lifecycle.");
            GetTree().Quit(0);
        }
        catch (Exception error)
        {
            GD.PushError(error.ToString());
            GetTree().Quit(1);
        }
    }

    private void CompareProductionTexturePages()
    {
        using PackedScene scene = GD.Load<PackedScene>(FirstFlightWorldView.EntityScenePath);
        Node owner = scene.Instantiate();
        try
        {
            foreach ((string part, string file, int size, CuratedAyaTextureLoader.Compression compression) in new[]
            {
                ("PulseBolt/PulseBoltSprite", "pulse-bolt-blue-spark", 64, CuratedAyaTextureLoader.Compression.Dxt2),
                ("PulseBolt/PulseBoltHalo", "mech-pulse-medium-halo", 64, CuratedAyaTextureLoader.Compression.Dxt1),
                ("PulseBolt/PulseBoltEnergyTrail", "mech-pulse-medium-energy-trail", 64, CuratedAyaTextureLoader.Compression.Dxt1),
                ("PulseBolt/ProjectileTrail", "pulse-bolt-blue-trail", 64, CuratedAyaTextureLoader.Compression.Dxt1),
                ("VulcanBullet/ProjectileTrail", "vulcan-bullet-trail", 64, CuratedAyaTextureLoader.Compression.Dxt1),
                ("MuzzleFlash/PulseCannonMuzzleFlash", "particle-alparticle5-additive", 128, CuratedAyaTextureLoader.Compression.Dxt1),
            })
            {
                var visual = owner.GetNode<MeshInstance3D>("Definitions/" + part);
                var material = (StandardMaterial3D)visual.MaterialOverride;
                Texture2D actual = material.AlbedoTexture;
                Check(actual is not null && actual.HasMethod("ensure_loaded"), "Each production material owns its native private-page recipe.");
                using Variant loadedValue = actual!.Call("ensure_loaded");
                using Dictionary loaded = Result(loadedValue);
                using Texture2D expected = CuratedAyaTextureLoader.Load(
                    "res://Assets/Level100/Textures/" + file + ".texture.aya", size, size, compression);
                using Image referenceImage = expected.GetImage();
                using Image actualImage = actual.GetImage();
                Check(actualImage.GetWidth() == referenceImage.GetWidth() && actualImage.GetHeight() == referenceImage.GetHeight(),
                    "Native texture dimensions equal the former managed loader: " + file);
                Check(actualImage.GetFormat() == referenceImage.GetFormat() && actualImage.HasMipmaps() == referenceImage.HasMipmaps(),
                    "Native texture format and mipmap admission equal the former loader: " + file);
                Check(actualImage.GetData().AsSpan().SequenceEqual(referenceImage.GetData()),
                    "Native decoded texture bytes equal the former loader: " + file);
                if (part != "MuzzleFlash/PulseCannonMuzzleFlash")
                    // Godot 4.8 dev6 excludes emission fields from Storage on
                    // unshaded materials. Local-to-scene copies drop those
                    // inactive fields; the native scene checks separately
                    // inspect identical page references in the authored state.
                    Check(material.ShadingMode == BaseMaterial3D.ShadingModeEnum.Unshaded &&
                        !material.EmissionEnabled && material.EmissionTexture is null,
                        "Native local-to-scene duplication omits inactive unshaded emission fields.");
            }
        }
        finally { owner.Free(); }
    }

    private void CompareMuzzleAnimation()
    {
        // Advance both production tweens explicitly, without wall-clock sleeps
        // or rendering. This retains the exact former C# schedule as the
        // temporary oracle for the native scene's UV and scale animation.
        var before = GetTree().GetProcessedTweens().Select(value => value.GetInstanceId()).ToHashSet();
        using PackedScene scene = GD.Load<PackedScene>("res://Scenes/World/PulseMuzzleFlash.tscn");
        var native = scene.Instantiate<Node3D>();
        AddChild(native);
        using Variant startValue = native.Call("start");
        using Dictionary started = Result(startValue);
        Tween[] nativeTweens = GetTree().GetProcessedTweens()
            .Where(value => !before.Contains(value.GetInstanceId())).ToArray();
        Check(nativeTweens.Length == 2, "A muzzle starts exactly one atlas and one scale tween.");
        Check(!native.GetNode<Godot.Timer>("Lifetime").IsStopped() &&
            native.GetNode<Godot.Timer>("Lifetime").WaitTime == 0.5d,
            "The native muzzle retains its explicit half-second lifetime timer.");
        var reference = new Node3D();
        AddChild(reference);
        var material = new StandardMaterial3D { AlbedoColor = new(0.5f, 1f, 1f, 1f),
            Uv1Scale = new(0.25f, 0.25f, 1f), Uv1Offset = new(0.25f, 0f, 0f) };
        var flash = new MeshInstance3D { Mesh = new QuadMesh { Size = new(0.6f, 0.6f) }, MaterialOverride = material };
        reference.AddChild(flash);
        Tween atlas = reference.CreateTween();
        const double interval = 1d / (1.4d * SimulationConstants.TicksPerSecond);
        for (int cell = 2; cell <= 15; cell++)
        {
            int captured = cell;
            atlas.TweenInterval(interval);
            atlas.TweenCallback(Callable.From(() => material.Uv1Offset = new(
                (captured % 4) / 4f, (captured / 4) / 4f, 0f)));
        }
        flash.Scale = Vector3.One;
        Tween scale = flash.CreateTween();
        scale.TweenProperty(flash, new NodePath("scale"), Vector3.One * 5f, 0.5d);
        Tween[] referenceTweens = [atlas, scale];
        bool[] nativeActive = [true, true], referenceActive = [true, true];
        foreach (Tween tween in nativeTweens.Concat(referenceTweens)) tween.Pause();
        var actual = native.GetNode<MeshInstance3D>("PulseCannonMuzzleFlash");
        foreach (double delta in new[] { 0d, Math.BitDecrement(interval), interval - Math.BitDecrement(interval),
            interval, 0.01d, 0.023d, interval, 0.1d, interval, 0.15d, 0.2d })
        {
            for (int index = 0; index < 2; index++)
            {
                if (nativeActive[index]) nativeActive[index] = nativeTweens[index].CustomStep(delta);
                if (referenceActive[index]) referenceActive[index] = referenceTweens[index].CustomStep(delta);
                Check(nativeActive[index] == referenceActive[index], "Native muzzle tween completion follows the original schedule.");
            }
            Compare(((StandardMaterial3D)actual.MaterialOverride).Uv1Offset, material.Uv1Offset, "muzzle atlas UV");
            Compare(actual.Scale, flash.Scale, "muzzle radius animation");
        }
        Check(((StandardMaterial3D)actual.MaterialOverride).Uv1Offset == new Vector3(0.75f, 0.75f, 0f),
            "The production muzzle reaches final atlas cell fifteen.");
        Compare(actual.Scale, Vector3.One * 5f, "muzzle final radius ratio");
        foreach (Tween tween in nativeTweens.Concat(referenceTweens)) tween.Kill();
        native.Free();
        reference.Free();
    }

    private void CompareTargets(Node owner, Node3D world, WorldSnapshot previous, WorldSnapshot current, float alpha)
    {
        var prior = new System.Collections.Generic.Dictionary<Level100ActorId, Level100TargetVisualDescriptor>();
        foreach (TargetSnapshot item in previous.Targets) prior[item.ActorId] = Level100TargetPresentation.Project(item);
        foreach (TargetSnapshot item in current.Targets)
        {
            Level100TargetVisualDescriptor descriptor = Level100TargetPresentation.Project(item);
            Level100TargetVisualDescriptor expected = Level100RenderInterpolation.Interpolate(
                prior.TryGetValue(item.ActorId, out var found) ? found : null, descriptor, alpha);
            _referenceTargets[item.ActorId] = expected;
        }
        foreach ((Level100ActorId id, Level100TargetVisualDescriptor expected) in _referenceTargets)
        {
            var actual = world.GetNode<Node3D>($"RetailLevel100TargetActor{id.Value}");
            Compare(actual.Transform, new(new Basis(Vector(expected.Basis.XAxis), Vector(expected.Basis.YAxis), Vector(expected.Basis.ZAxis)), Vector(expected.Position)), $"actor {id.Value}");
            Check(actual.Visible == expected.Visible, "Actor visibility follows the current explicit flag.");
            Check(actual.GetMeta("actor_id").AsInt32() == id.Value, "Actor identity remains authored metadata.");
        }
    }

    private void CompareProjectiles(Node owner, Node3D world, Node3D referenceWorld, Camera3D camera,
        WorldSnapshot previous, WorldSnapshot current, float alpha)
    {
        var prior = new System.Collections.Generic.Dictionary<int, ProjectileSnapshot>();
        foreach (ProjectileSnapshot item in previous.Projectiles) prior[item.Id] = item;
        var active = new HashSet<int>();
        foreach (ProjectileSnapshot item in current.Projectiles)
        {
            active.Add(item.Id);
            if (!_referenceProjectiles.TryGetValue(item.Id, out Node3D? reference))
            {
                reference = new Node3D();
                referenceWorld.AddChild(reference);
                _referenceProjectiles.Add(item.Id, reference);
                _referenceTrails.Add(item.Id, new(Level100ProjectileTrailHistory.AuthoredPointCount(item.Kind), Level100ProjectileTrailHistory.AuthoredLifetimeTicks(item.Kind)));
            }
            Level100ProjectileVisualState expected = Level100RenderInterpolation.Interpolate(
                prior.TryGetValue(item.Id, out ProjectileSnapshot? previousItem) ? State(previousItem, Position(previousItem)) : null,
                State(item, Spawn(item)), State(item, Position(item)), alpha);
            reference.Position = Vector(expected.Position);
            Vector3 direction = Vector(expected.Direction);
            if (!direction.IsZeroApprox()) reference.LookAt(reference.Position + direction.Normalized(), Vector3.Up);
            string prefix = item.Id < 200 ? "RetailPulseBolt" : "RetailVulcanBullet";
            Node3D actual = world.GetNode<Node3D>(prefix + item.Id);
            Compare(actual.Transform, reference.Transform, "projectile " + item.Id);
            Level100ProjectileTrailHistory trail = _referenceTrails[item.Id];
            trail.Advance(Position(item), new(item.Velocity.X * 0.001f, item.VerticalVelocityMillimetersPerTick * 0.001f, -item.Velocity.Z * 0.001f), item.RemainingTicks);
            IReadOnlyList<Level100RenderVector3> points = trail.WithRenderedHead(expected.Position);
            MeshInstance3D mesh = actual.GetNode<MeshInstance3D>("ProjectileTrail");
            Check(mesh.Visible == (points.Count >= 2), "Trail visibility retains the one-point gate.");
            if (points.Count >= 2)
                CompareTrail(mesh, points, referenceWorld, camera.GlobalPosition, reference.GlobalTransform.AffineInverse(), item.Kind == Level100ProjectileKind.MechPulseBoltMedium ? 0.08f : 0.02f);
        }
        foreach (int id in _referenceProjectiles.Keys.Where(id => !active.Contains(id)).ToArray())
        {
            _referenceProjectiles[id].Free();
            _referenceProjectiles.Remove(id);
            _referenceTrails.Remove(id);
        }
        using Variant snapshotValue = owner.Call("diagnostic_snapshot");
        using Dictionary snapshot = snapshotValue.AsGodotDictionary();
        using Variant trailValues = snapshot["trails"];
        using Dictionary trails = trailValues.AsGodotDictionary();
        Check(trails.Count == _referenceTrails.Count, "Native trail histories retire alongside projectiles.");
        foreach ((int id, Level100ProjectileTrailHistory expected) in _referenceTrails)
        {
            using Variant trailValue = trails[id];
            using Dictionary trail = trailValue.AsGodotDictionary();
            using Variant pointValues = trail["points"];
            using Array points = pointValues.AsGodotArray();
            Check(points.Count == expected.Points.Count, "Native trail capacity matches its authored kind.");
            for (int index = 0; index < points.Count; index++)
            {
                using Variant pointValue = points[index];
                using Dictionary point = pointValue.AsGodotDictionary();
                Compare(RawVector(point), Vector(expected.Points[index]), "history point");
            }
        }
    }

    private void CompareTrail(MeshInstance3D actual, IReadOnlyList<Level100RenderVector3> points,
        Node3D world, Vector3 camera, Transform3D worldToProjectile, float width)
    {
        using Array arrays = actual.Mesh.SurfaceGetArrays(0);
        using Variant vertexValues = arrays[(int)Mesh.ArrayType.Vertex];
        using Variant uvValues = arrays[(int)Mesh.ArrayType.TexUV];
        Vector3[] vertices = vertexValues.AsVector3Array();
        Vector2[] uv = uvValues.AsVector2Array();
        Check(vertices.Length == points.Count * 2 && uv.Length == vertices.Length, "Trail emits one ordered strip pair per retained point.");
        float halfWidth = width * 0.5f;
        for (int index = 0; index < points.Count; index++)
        {
            Vector3 point = world.ToGlobal(Vector(points[index]));
            Vector3 neighbour = world.ToGlobal(Vector(points[index + 1 < points.Count ? index + 1 : index - 1]));
            Vector3 direction = index + 1 < points.Count ? neighbour - point : point - neighbour;
            if (direction.IsZeroApprox()) direction = Vector3.Forward;
            Vector3 side = direction.Cross(camera - point);
            if (side.IsZeroApprox()) side = direction.Cross(Vector3.Up);
            if (side.IsZeroApprox()) side = Vector3.Right;
            side = side.Normalized() * halfWidth;
            Compare(vertices[index * 2], worldToProjectile * (point - side), "trail left vertex");
            Compare(vertices[index * 2 + 1], worldToProjectile * (point + side), "trail right vertex");
            float u = index / (float)(points.Count - 1);
            Check(uv[index * 2] == new Vector2(u, 0) && uv[index * 2 + 1] == new Vector2(u, 1), "Trail UV order and float32 fraction match.");
        }
    }

    private void CompareFeet(WorldSnapshot previous, WorldSnapshot current, float alpha, bool reset, Array actual)
    {
        Vector3[] expected = FootOffsets(current);
        if (!reset)
        {
            Vector3[] prior = FootOffsets(previous);
            for (int index = 0; index < 4; index++) expected[index] = Vector(Level100RenderInterpolation.InterpolatePosition(Render(prior[index]), Render(expected[index]), alpha, 3f));
        }
        Check(actual.Count == 4, "The Aquila stage receives exactly four contacts.");
        for (int index = 0; index < 4; index++)
        {
            using Variant pointValue = actual[index];
            using Dictionary point = pointValue.AsGodotDictionary();
            Compare(RawVector(point), expected[index], "foot interpolation");
        }
    }

    // Retained pre-controller host fixture from FirstFlightWorldView.Entities
    // at 1bb29345. Production now submits raw snapshot facts to its native
    // world owner; this conversion remains only as an independent leaf oracle.
    private static Dictionary EntityFrameFacts(WorldSnapshot previous, WorldSnapshot current,
        float alpha, bool resetJump, int pendingMuzzles)
    {
        Array currentFeet = EntityVectors(FootOffsets(current));
        Variant previousFeet = default;
        bool same = ReferenceEquals(previous, current);
        if (!resetJump && !same && previous.WalkerFeet.Count == current.WalkerFeet.Count)
            previousFeet = EntityVectors(FootOffsets(previous));
        return new Dictionary
        {
            ["alpha_bits"] = (long)BitConverter.SingleToUInt32Bits(alpha),
            ["same_snapshot"] = same, ["current_feet"] = currentFeet,
            ["previous_feet"] = previousFeet,
            ["previous_targets"] = same ? new Array() : FirstFlightWorldView.EntityTargetFacts(previous.Targets),
            ["current_targets"] = FirstFlightWorldView.EntityTargetFacts(current.Targets),
            ["previous_projectiles"] = same ? new Array() : FirstFlightWorldView.EntityProjectileFacts(previous.Projectiles),
            ["current_projectiles"] = FirstFlightWorldView.EntityProjectileFacts(current.Projectiles),
            ["pending_muzzles"] = pendingMuzzles,
        };
    }

    private static Array EntityVectors(IEnumerable<Vector3> values)
    {
        var result = new Array();
        foreach (Vector3 value in values)
            result.Add(new Dictionary { ["x_bits"] = (long)BitConverter.SingleToUInt32Bits(value.X),
                ["y_bits"] = (long)BitConverter.SingleToUInt32Bits(value.Y), ["z_bits"] = (long)BitConverter.SingleToUInt32Bits(value.Z) });
        return result;
    }

    private static Vector3[] FootOffsets(WorldSnapshot snapshot)
    {
        if (snapshot.WalkerFeet.Count != 4)
            throw new InvalidDataException("Core did not expose four Aquila foot contacts.");
        var result = new Vector3[4];
        foreach (WalkerFootContactSnapshot foot in snapshot.WalkerFeet)
        {
            if (foot.Id < 0 || foot.Id >= result.Length)
                throw new InvalidDataException($"Core exposed unknown Aquila foot {foot.Id}.");
            result[foot.Id] = new((foot.Position.X - snapshot.PlayerPosition.X) * 0.001f,
                (foot.GroundElevationMillimeters + foot.LiftMillimeters - snapshot.PlayerGroundElevationMillimeters) * 0.001f,
                -(foot.Position.Z - snapshot.PlayerPosition.Z) * 0.001f);
        }
        return result;
    }
    private static Level100ActorSnapshot Actor(int index, int step)
    {
        Level100TargetVisualBinding binding = Level100TargetPresentation.RenderedBindings[index];
        float yaw = (step * 0.03f) + index * 0.13f;
        int s = BitConverter.SingleToInt32Bits(MathF.Sin(yaw)), c = BitConverter.SingleToInt32Bits(MathF.Cos(yaw));
        return new(new(index + 1), "synthetic-entity-" + index, "Entity " + index,
            binding.DefinitionName, null, binding.MeshBinding, 0, null, null, false,
            (step + index) % 9 != 0, false, Level100ActorLifecycle.Alive, 3000,
            new(new(index * 5000 + step * (step == 10 ? 2000 : 30), 1700 + index * 101, -3000 + step * 45),
                new(c, 0, s, 0, 0x3f800000, 0, s ^ int.MinValue, 0, c), default, default),
            Level100MissionTargetGroup.None, 0, null, false, null, false);
    }
    private static Level100RenderVector3 Position(ProjectileSnapshot item) => new(item.Position.X * 0.001f, item.ElevationMillimeters * 0.001f, -item.Position.Z * 0.001f);
    private static Level100RenderVector3 Spawn(ProjectileSnapshot item) => new((item.Position.X - item.Velocity.X) * 0.001f,
        (item.ElevationMillimeters - item.VerticalVelocityMillimetersPerTick) * 0.001f, -(item.Position.Z - item.Velocity.Z) * 0.001f);
    private static Level100ProjectileVisualState State(ProjectileSnapshot item, Level100RenderVector3 position) => new(position, new(item.Velocity.X, item.VerticalVelocityMillimetersPerTick, -item.Velocity.Z));
    private static Vector3 Vector(Level100RenderVector3 value) => new(value.X, value.Y, value.Z);
    private static Level100RenderVector3 Render(Vector3 value) => new(value.X, value.Y, value.Z);
    private static Vector3 RawVector(Dictionary value) => new(BitConverter.UInt32BitsToSingle((uint)value["x_bits"].AsInt64()),
        BitConverter.UInt32BitsToSingle((uint)value["y_bits"].AsInt64()), BitConverter.UInt32BitsToSingle((uint)value["z_bits"].AsInt64()));
    private static Dictionary Result(Variant value)
    {
        if (value.VariantType != Variant.Type.Dictionary) throw new InvalidOperationException("Native scene aborted without a completion record.");
        Dictionary result = value.AsGodotDictionary();
        bool hasFlag = result.TryGetValue("ok", out Variant ok);
        using (ok)
            if (!hasFlag || ok.VariantType != Variant.Type.Bool || !ok.AsBool())
            {
                string error = "Native scene refused: " + result;
                result.Dispose();
                throw new InvalidOperationException(error);
            }
        return result;
    }
    private void Compare(Transform3D actual, Transform3D expected, string name)
    { Compare(actual.Origin, expected.Origin, name + " origin"); Compare(actual.Basis.X, expected.Basis.X, name + " X"); Compare(actual.Basis.Y, expected.Basis.Y, name + " Y"); Compare(actual.Basis.Z, expected.Basis.Z, name + " Z"); }
    private void Compare(Vector3 actual, Vector3 expected, string name)
    {
        for (int axis = 0; axis < 3; axis++)
            Check(BitConverter.SingleToUInt32Bits(actual[axis]) == BitConverter.SingleToUInt32Bits(expected[axis]),
                $"{name}[{axis}]: actual {BitConverter.SingleToUInt32Bits(actual[axis]):x8}, expected {BitConverter.SingleToUInt32Bits(expected[axis]):x8}.");
    }
    private void Check(bool condition, string message)
    { _checks++; if (!condition) throw new InvalidOperationException(message); }
}
