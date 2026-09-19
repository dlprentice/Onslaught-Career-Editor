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
            WorldSnapshot basis = session.CurrentSnapshot with { Targets = [], Projectiles = [] };
            string initialHash = StateHasher.ComputeHex(session.CurrentSnapshot);
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
            var assets = new Array();
            foreach (Level100TargetVisualBinding binding in Level100TargetPresentation.RenderedBindings)
                assets.Add(new Dictionary { ["definition_name"] = binding.DefinitionName,
                    ["mesh_binding"] = binding.MeshBinding, ["mesh"] = new BoxMesh() });
            Result(owner.Call("configure", world, camera, assets, new Array()));

            WorldSnapshot previous = basis;
            for (int step = 0; step < 32; step++)
            {
                TargetSnapshot[] targets = Enumerable.Range(0, 6)
                    .Select(index => Target(index, step)).Reverse().ToArray();
                // An absent actor intentionally retains its previous visual;
                // an inactive actor remains registered and explicitly hidden.
                if (step % 7 == 4) targets = targets.Where(value => value.ActorId.Value != 3).ToArray();
                ProjectileSnapshot[] projectiles = step % 8 == 7 ? [] :
                [
                    new(100 + step / 8, Level100ProjectileKind.MechPulseBoltMedium,
                        new(3000 + step * 170, 7000 - step * 230), new(170, -230), 1500 + step * 19, 19, 120 - step % 8),
                    new(200 + step / 8, step % 2 == 0 ? Level100ProjectileKind.MechBullet : Level100ProjectileKind.MechAirBullet,
                        new(-2000 + step * 77, 3000 + step * 150), new(77, 150), 2100 - step * 8, -8, 20 - step % 8),
                ];
                WorldSnapshot current = basis with { Tick = step + 1, Targets = targets, Projectiles = projectiles,
                    WalkerFeet = basis.WalkerFeet.Select(foot => foot with { Position = new(foot.Position.X + step * 15,
                        foot.Position.Z - step * 11), LiftMillimeters = foot.LiftMillimeters + step * 4 }).ToArray() };
                // A duplicate previous identity must select its last pose,
                // rather than a sorted/ordinal or first-match substitute.
                if (step == 9 && previous.Targets.Count > 0)
                    previous = previous with { Targets = previous.Targets.Concat([previous.Targets[0] with {
                        Pose = previous.Targets[0].Pose with { PositionMillimeters = new SimVector3(previous.Targets[0].Pose.PositionMillimeters.X + 19, previous.Targets[0].Pose.PositionMillimeters.Y + 23, previous.Targets[0].Pose.PositionMillimeters.Z + 29) } }]).ToArray() };
                if (step == 16)
                {
                    world.Transform = new Transform3D(new Basis(Vector3.Up, 0.3f), new(3, 0, 4));
                    referenceWorld.Transform = world.Transform;
                }
                foreach (float alpha in new[] { 0f, 0.25f, 0.5f, 1f })
                {
                    int callbacks = 0;
                    using Dictionary facts = FirstFlightWorldView.EntityFrameFacts(previous, current, alpha,
                        resetJump: step == 12, pendingMuzzles: 0);
                    Callable stage = Callable.From<Array, Dictionary>(feet =>
                    {
                        callbacks++;
                        CompareFeet(previous, current, alpha, step == 12, feet);
                        return new Dictionary { ["ok"] = true };
                    });
                    Dictionary result = Result(owner.Call("render_frame", facts, stage));
                    Check(callbacks == 1, "Exactly one Aquila stage callback per native render batch.");
                    CompareTargets(owner, world, previous, current, alpha);
                    CompareProjectiles(owner, world, referenceWorld, camera, previous, current, alpha);
                    Check(result["projectile_count"].AsInt32() == current.Projectiles.Count, "Projectile diagnostics reflect the native owner.");
                    Check(result["target_count"].AsInt32() == _referenceTargets.Values.Count(value => value.Visible), "Visible actor diagnostics reflect retained/inactive actors.");
                }
                previous = current;
            }
            // Reference-equal snapshots deliberately suppress previous joins.
            using (Dictionary same = FirstFlightWorldView.EntityFrameFacts(previous, previous, 0.5f, false, 0))
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
        Dictionary snapshot = owner.Call("diagnostic_snapshot").AsGodotDictionary();
        Dictionary trails = snapshot["trails"].AsGodotDictionary();
        Check(trails.Count == _referenceTrails.Count, "Native trail histories retire alongside projectiles.");
        foreach ((int id, Level100ProjectileTrailHistory expected) in _referenceTrails)
        {
            Array points = trails[id].AsGodotDictionary()["points"].AsGodotArray();
            Check(points.Count == expected.Points.Count, "Native trail capacity matches its authored kind.");
            for (int index = 0; index < points.Count; index++)
                Compare(RawVector(points[index].AsGodotDictionary()), Vector(expected.Points[index]), "history point");
        }
    }

    private void CompareTrail(MeshInstance3D actual, IReadOnlyList<Level100RenderVector3> points,
        Node3D world, Vector3 camera, Transform3D worldToProjectile, float width)
    {
        Array arrays = actual.Mesh.SurfaceGetArrays(0);
        Vector3[] vertices = arrays[(int)Mesh.ArrayType.Vertex].AsVector3Array();
        Vector2[] uv = arrays[(int)Mesh.ArrayType.TexUV].AsVector2Array();
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
        for (int index = 0; index < 4; index++) Compare(RawVector(actual[index].AsGodotDictionary()), expected[index], "foot interpolation");
    }

    private static Vector3[] FootOffsets(WorldSnapshot snapshot)
    {
        var result = new Vector3[4];
        foreach (WalkerFootContactSnapshot foot in snapshot.WalkerFeet)
            result[foot.Id] = new((foot.Position.X - snapshot.PlayerPosition.X) * 0.001f,
                (foot.GroundElevationMillimeters + foot.LiftMillimeters - snapshot.PlayerGroundElevationMillimeters) * 0.001f,
                -(foot.Position.Z - snapshot.PlayerPosition.Z) * 0.001f);
        return result;
    }
    private static TargetSnapshot Target(int index, int step)
    {
        Level100TargetVisualBinding binding = Level100TargetPresentation.RenderedBindings[index];
        float yaw = (step * 0.03f) + index * 0.13f;
        int s = BitConverter.SingleToInt32Bits(MathF.Sin(yaw)), c = BitConverter.SingleToInt32Bits(MathF.Cos(yaw));
        return new(new(index + 1), index, binding.DefinitionName, binding.MeshBinding, default, 3000,
            (step + index) % 9 != 0, new(new(index * 5000 + step * (step == 10 ? 2000 : 30), 1700 + index * 101, -3000 + step * 45),
                new(c, 0, s, 0, 0x3f800000, 0, s ^ int.MinValue, 0, c), default, default));
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
        if (!result.TryGetValue("ok", out Variant ok) || ok.VariantType != Variant.Type.Bool || !ok.AsBool())
            throw new InvalidOperationException("Native scene refused: " + result);
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
