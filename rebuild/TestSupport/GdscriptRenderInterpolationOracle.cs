// SPDX-License-Identifier: GPL-3.0-or-later
using System.Reflection;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;

// Synthetic, bounded value fixtures. Current Client is a temporary migration
// oracle, not new retail evidence. No scene, asset, device or native input.
internal static class GdscriptRenderInterpolationOracle
{
    private static readonly uint[] Words = [0, 0x80000000, 1, 0x80000001, 0x007fffff, 0x00800000, 0x3f800000,
        0xbf800000, 0x3f000000, 0x7f7fffff, 0xff7fffff, 0x7f800000, 0xff800000, 0x7fc00000, 0xffc00001, 0x7f800001, 0xff800001];
    private static readonly float[] Alphas = [0f, -0f, 0.25f, 0.5f, 0.75f, 1f, -1f, 2f,
        float.NaN, float.PositiveInfinity, float.NegativeInfinity];
    private static readonly MethodInfo Proper = typeof(Level100RenderInterpolation).GetMethod("IsProperRotation", BindingFlags.Static | BindingFlags.NonPublic)!;
    private static readonly FieldInfo LastRemaining = typeof(Level100ProjectileTrailHistory).GetField("_lastRemainingTicks", BindingFlags.Instance | BindingFlags.NonPublic)!;
    private static readonly Level100RenderBasis3 Identity = new(new(1, 0, 0), new(0, 1, 0), new(0, 0, 1));

    internal static object Build()
    {
        var projection = new List<object>();
        void Project(string name, TargetSnapshot? target)
        {
            object expected;
            try { expected = new { ok = true, value = Descriptor(Level100TargetPresentation.Project(target!)) }; }
            catch (Exception error) { expected = Failure(error); }
            projection.Add(new { name, target = TargetFacts(target), expected });
        }
        Project("null", null);
        foreach (Level100TargetVisualBinding binding in Level100TargetPresentation.RenderedBindings)
        {
            var target = Target(binding, new(1000, 2000, 3000), CoreIdentity());
            Project(binding.DefinitionName, target);
            Project(binding.DefinitionName + " hidden", target with { IsActive = false });
        }
        var arbitrary = Target(new("unknown\0\ud800", "mesh\0🚀"), new(int.MinValue, int.MaxValue, int.MinValue), CoreIdentity());
        Project("unknown binding remains explicit", arbitrary);
        Project("nullable binding remains distinct", arbitrary with { DefinitionName = null!, MeshBinding = null! });
        Project("null pose", arbitrary with { Pose = null! });
        foreach (uint word in Words)
        {
            int w = unchecked((int)word);
            Project("raw-basis-" + word.ToString("x8"), arbitrary with { Pose = arbitrary.Pose with {
                BasisFloatBits = new(w, w, w, w, w, w, w, w, w) } });
        }

        var vectors = new List<object>();
        void VectorCase(string name, Level100RenderVector3 p, Level100RenderVector3 c, float a, float threshold = 10f) =>
            vectors.Add(new { name, previous = Vector(p), current = Vector(c), alpha_bits = Word(a), teleport_bits = Word(threshold),
                lerp = Vector(Level100RenderInterpolation.Lerp(p, c, a)), distance_bits = Word(Level100RenderInterpolation.DistanceSquared(p, c)),
                interpolated = Vector(Level100RenderInterpolation.InterpolatePosition(p, c, a, threshold)) });
        foreach (float alpha in Alphas)
        {
            VectorCase("ordinary-" + Word(alpha), new(10, 2, -30), new(12, 3, -34), alpha);
            foreach (float distance in new[] { MathF.BitDecrement(10f), 10f, MathF.BitIncrement(10f), 20f })
                VectorCase("teleport-" + Word(distance) + "-" + Word(alpha), default, new(distance, 0, 0), alpha);
        }
        foreach (uint word in Words)
        {
            float value = Float(word);
            VectorCase("raw-position-" + word, new(value, 0, -0f), new(1, value, 0), 0.5f);
            VectorCase("raw-threshold-" + word, default, new(11, 2, 0), 0.25f, value);
        }
        var random = new Random(0x494e5445);
        for (int index = 0; index < 256; index++)
        {
            float Next() => (float)(random.NextDouble() * 2000000 - 1000000);
            VectorCase("varied-vector-" + index, new(Next(), Next(), Next()), new(Next(), Next(), Next()), (float)(random.NextDouble() * 4 - 2), float.PositiveInfinity);
        }

        var bases = new List<object>();
        void BasisCase(string name, Level100RenderBasis3 p, Level100RenderBasis3 c, float alpha) => bases.Add(new {
            name, previous = Basis(p), current = Basis(c), alpha_bits = Word(alpha),
            previous_proper = (bool)Proper.Invoke(null, [p])!, current_proper = (bool)Proper.Invoke(null, [c])!,
            expected = Basis(Level100RenderInterpolation.InterpolateBasis(p, c, alpha)) });
        var rotations = new List<Level100RenderBasis3> { Identity };
        foreach (float angle in new[] { MathF.PI / 180, MathF.PI / 2, 2 * MathF.PI / 3, MathF.PI,
            -175 * MathF.PI / 180, 175 * MathF.PI / 180, 0.01f, 0.02f, 0.03f, 0.06f, 0.064f })
            foreach (int axis in new[] { 0, 1, 2 }) rotations.Add(Rotation(axis, angle));
        for (int index = 0; index < rotations.Count; index++)
            foreach (float alpha in Alphas)
                BasisCase("rotation-" + index + "-" + Word(alpha), rotations[index], rotations[(index * 7 + 3) % rotations.Count], alpha);
        BasisCase("shortest-arc-wrap", Rotation(1, -175f * MathF.PI / 180f), Rotation(1, 175f * MathF.PI / 180f), 0.5f);
        foreach (float scale in new[] { 0f, -1f, 2f, MathF.Sqrt(1.002f), MathF.BitDecrement(MathF.Sqrt(1.002f)),
            MathF.BitIncrement(MathF.Sqrt(1.002f)), MathF.Sqrt(0.998f), MathF.BitDecrement(MathF.Sqrt(0.998f)) })
            BasisCase("unit-threshold-" + Word(scale), Identity with { XAxis = new(scale, 0, 0) }, Identity, 0.5f);
        foreach (float shear in new[] { 0.001f, MathF.BitDecrement(0.001f), MathF.BitIncrement(0.001f), -0.001f })
            BasisCase("orthogonal-threshold-" + Word(shear), Identity with { YAxis = new(shear, 1, 0) }, Identity, 0.5f);
        foreach (uint word in Words)
            BasisCase("raw-basis-" + word, Identity with { XAxis = new(Float(word), 0, 0) }, Identity, 0.5f);
        for (int index = 0; index < 256; index++)
        {
            var p = Product(Rotation(0, (float)(random.NextDouble() * 6)), Product(Rotation(1, (float)(random.NextDouble() * 6)), Rotation(2, (float)(random.NextDouble() * 6))));
            var c = Product(Rotation(0, (float)(random.NextDouble() * 6)), Product(Rotation(1, (float)(random.NextDouble() * 6)), Rotation(2, (float)(random.NextDouble() * 6))));
            BasisCase("varied-quaternion-" + index, p, c, (float)random.NextDouble());
        }

        var targets = new List<object>();
        var priorTarget = new Level100TargetVisualDescriptor(new(11), "Target Truck", "m_f_truck_training.msh.aya", true, new(10, 2, -30), Identity);
        var nextTarget = priorTarget with { Position = new(12, 3, -34), Basis = Rotation(1, MathF.PI / 2) };
        void TargetCase(string name, Level100TargetVisualDescriptor? p, Level100TargetVisualDescriptor c, float a) => targets.Add(new {
            name, previous = p is { } prior ? Descriptor(prior) : null, current = Descriptor(c), alpha_bits = Word(a),
            expected = Descriptor(Level100RenderInterpolation.Interpolate(p, c, a)) });
        foreach (float alpha in Alphas)
        {
            TargetCase("ordinary-" + Word(alpha), priorTarget, nextTarget, alpha);
            TargetCase("spawn-" + Word(alpha), null, nextTarget, alpha);
            TargetCase("identity-" + Word(alpha), priorTarget with { ActorId = new(12) }, nextTarget, alpha);
            TargetCase("definition-" + Word(alpha), priorTarget with { DefinitionName = "Target Truck\0suffix" }, nextTarget, alpha);
            TargetCase("mesh-" + Word(alpha), priorTarget with { MeshBinding = "M_f_truck_training.msh.aya" }, nextTarget, alpha);
            TargetCase("hidden-old-" + Word(alpha), priorTarget with { Visible = false }, nextTarget, alpha);
            TargetCase("hidden-new-" + Word(alpha), priorTarget, nextTarget with { Visible = false }, alpha);
            TargetCase("teleport-" + Word(alpha), priorTarget, nextTarget with { Position = new(410, 2, -30) }, alpha);
            TargetCase("nullable-names-" + Word(alpha), priorTarget with { DefinitionName = null!, MeshBinding = null! },
                nextTarget with { DefinitionName = null!, MeshBinding = null! }, alpha);
        }
        var projectiles = new List<object>();
        var spawn = new Level100ProjectileVisualState(new(1, 2, -3), new(4000, 0, 0));
        var current = new Level100ProjectileVisualState(new(5, 2, -3), new(4000, 0, 0));
        void ProjectileCase(string name, Level100ProjectileVisualState? p, Level100ProjectileVisualState s, Level100ProjectileVisualState c, float a) => projectiles.Add(new {
            name, previous = p is { } prior ? Projectile(prior) : null, spawn = Projectile(s), current = Projectile(c), alpha_bits = Word(a),
            expected = Projectile(Level100RenderInterpolation.Interpolate(p, s, c, a)) });
        foreach (float alpha in Alphas)
        {
            ProjectileCase("spawn-" + Word(alpha), null, spawn, current, alpha);
            ProjectileCase("prior-ignores-muzzle-" + Word(alpha), current, spawn, current with { Position = new(9, 2, -3) }, alpha);
            ProjectileCase("opposite-direction-" + Word(alpha), current, spawn, current with { Direction = new(-4000, 0, 0) }, alpha);
            ProjectileCase("degenerate-direction-" + Word(alpha), current with { Direction = default }, spawn, current with { Direction = default }, alpha);
        }
        foreach (uint word in Words)
            ProjectileCase("raw-direction-" + word, current with { Direction = new(Float(word), 0, 0) }, spawn, current with { Direction = new(Float(word), -0f, 1) }, 0.5f);

        var kinds = new List<object>();
        for (int kind = 0; kind <= 255; kind++)
        {
            var value = (Level100ProjectileKind)kind;
            kinds.Add(new { kind, uses = Level100ProjectileTrailHistory.UsesAuthoredTrail(value),
                points = Run(() => Level100ProjectileTrailHistory.AuthoredPointCount(value)),
                lifetime = Run(() => Level100ProjectileTrailHistory.AuthoredLifetimeTicks(value)) });
        }
        var constructors = new List<object>();
        foreach ((int capacity, int lifetime) in new[] { (1, 1), (3, 20), (5, 120), (int.MaxValue, int.MaxValue),
            (0, 0), (-1, 1), (int.MinValue, 0), (1, 0), (1, -1), (1, int.MinValue) })
        {
            object expected;
            try { _ = new Level100ProjectileTrailHistory(capacity, lifetime); expected = new { ok = true }; }
            catch (Exception error) { expected = Failure(error); }
            constructors.Add(new { capacity, lifetime, expected });
        }
        var trails = new List<object>();
        foreach ((int capacity, int lifetime) in new[] { (1, 1), (3, 20), (5, 120), (7, 11), (2, int.MaxValue) })
        {
            var state = new Level100ProjectileTrailHistory(capacity, lifetime);
            var steps = new List<object>();
            void Advance(Level100RenderVector3 point, Level100RenderVector3 velocity, int remaining)
            {
                object expected;
                try { state.Advance(point, velocity, remaining); expected = new { ok = true }; }
                catch (Exception error) { expected = Failure(error); }
                var head = new Level100RenderVector3(point.X + 0.5f, point.Y - 0.25f, point.Z);
                steps.Add(new { current = Vector(point), velocity = Vector(velocity), remaining, expected,
                    points = state.Points.Select(Vector).ToArray(), last_remaining_ticks = LastRemaining.GetValue(state),
                    head = Vector(head), with_head = state.WithRenderedHead(head).Select(Vector).ToArray() });
            }
            object[] before = state.WithRenderedHead(new(1, 2, 3)).Select(Vector).ToArray();
            Level100RenderVector3 velocity = new(1, -0.125f, 0.3f);
            Advance(new(1, 2, 3), velocity, lifetime);
            Advance(new(2, 3, 4), velocity, Math.Max(0, lifetime - 1));
            Advance(new(6, 7, 8), velocity, Math.Max(0, lifetime - 6));
            Advance(new(6.5f, 7.5f, 8.5f), new(99, 88, 77), Math.Max(0, lifetime - 6));
            Advance(new(8, 9, 10), velocity, 0); // Safe bounded append even for Int32.MaxValue lifetime.
            Advance(new(9, 8, 7), velocity, -1);
            if (lifetime < int.MaxValue) Advance(new(9, 8, 7), velocity, lifetime + 1);
            Advance(new(-10, -20, -30), velocity, lifetime);
            Advance(new(float.NaN, float.PositiveInfinity, -0f), new(0, 1, -1), Math.Max(0, lifetime - 1));
            trails.Add(new { capacity, lifetime, before, steps });
        }
        // The unbounded first-call edge itself is deliberately not run. These
        // bounded reference steps produce the same surviving capacity tail.
        var extreme = new Level100ProjectileTrailHistory(5, int.MaxValue);
        var extremePoint = new Level100RenderVector3(10, 20, 30);
        var extremeVelocity = new Level100RenderVector3(0.5f, -2f, 0.125f);
        extreme.Advance(extremePoint, extremeVelocity, int.MaxValue);
        extreme.Advance(extremePoint, extremeVelocity, 0);
        object extremeTail = new { capacity = 5, lifetime = int.MaxValue, current = Vector(extremePoint), velocity = Vector(extremeVelocity),
            points = extreme.Points.Select(Vector).ToArray(), last_remaining_ticks = 0,
            observation = "Source-derived discarded-prefix equivalence; the 2^31 original first-call loop was not executed." };

        var trig = new List<object>();
        foreach (uint word in Words.Concat(Enumerable.Range(0, 256).Select(_ => (uint)random.NextInt64(1L << 32))))
            trig.Add(new { input_bits = word, sin_bits = Word(MathF.Sin(Float(word))) });
        var acos = new List<object>();
        foreach (float value in new[] { -1f, 1f, 0f, -0f, MathF.BitDecrement(1f), MathF.BitIncrement(-1f),
            0.9995f, MathF.BitDecrement(0.9995f), MathF.BitIncrement(0.9995f) }
            .Concat(Enumerable.Range(0, 256).Select(_ => (float)(random.NextDouble() * 2 - 1))))
            acos.Add(new { input_bits = Word(value), output_bits = Word(MathF.Acos(value)) });
        return new { projection, bindings = Level100TargetPresentation.RenderedBindings.Select(Binding).ToArray(), vectors, bases, targets, projectiles,
            kinds, constructors, trails, extreme_tail = extremeTail, trig, acos, teleport_bits = Word(Level100RenderInterpolation.TeleportMeters) };
    }

    private static object Run(Func<int> operation)
    { try { return new { ok = true, value = operation() }; } catch (Exception error) { return Failure(error); } }
    private static object Failure(Exception error) => new { ok = false, error_type = error.GetType().Name,
        parameter = error is ArgumentException argument ? argument.ParamName ?? "" : "" };
    private static TargetSnapshot Target(Level100TargetVisualBinding binding, SimVector3 position, Level100FloatBasis3Bits basis) =>
        new(new(11), 0, binding.DefinitionName, binding.MeshBinding, default, 3000, true,
            new(position, basis, default, default));
    private static Level100FloatBasis3Bits CoreIdentity() => new(0x3f800000, 0, 0, 0, 0x3f800000, 0, 0, 0, 0x3f800000);
    private static Level100RenderBasis3 Rotation(int axis, float angle)
    {
        float s = MathF.Sin(angle), c = MathF.Cos(angle);
        return axis switch { 0 => new(new(1, 0, 0), new(0, c, s), new(0, -s, c)),
            1 => new(new(c, 0, -s), new(0, 1, 0), new(s, 0, c)), _ => new(new(c, s, 0), new(-s, c, 0), new(0, 0, 1)) };
    }
    private static Level100RenderBasis3 Product(Level100RenderBasis3 a, Level100RenderBasis3 b)
    {
        Level100RenderVector3 Column(Level100RenderVector3 v) => new(a.XAxis.X * v.X + a.YAxis.X * v.Y + a.ZAxis.X * v.Z,
            a.XAxis.Y * v.X + a.YAxis.Y * v.Y + a.ZAxis.Y * v.Z, a.XAxis.Z * v.X + a.YAxis.Z * v.Y + a.ZAxis.Z * v.Z);
        return new(Column(b.XAxis), Column(b.YAxis), Column(b.ZAxis));
    }
    private static object? Raw(string? value) => value?.Select(c => (int)c).ToArray();
    private static object Binding(Level100TargetVisualBinding value) => new { definition_name = Raw(value.DefinitionName), mesh_binding = Raw(value.MeshBinding) };
    private static object Vector(Level100RenderVector3 value) => new { x_bits = Word(value.X), y_bits = Word(value.Y), z_bits = Word(value.Z) };
    private static object Basis(Level100RenderBasis3 value) => new { x_axis = Vector(value.XAxis), y_axis = Vector(value.YAxis), z_axis = Vector(value.ZAxis) };
    private static object Descriptor(Level100TargetVisualDescriptor value) => new { actor_id = value.ActorId.Value, definition_name = Raw(value.DefinitionName),
        mesh_binding = Raw(value.MeshBinding), visible = value.Visible, position = Vector(value.Position), basis = Basis(value.Basis) };
    private static object Projectile(Level100ProjectileVisualState value) => new { position = Vector(value.Position), direction = Vector(value.Direction) };
    private static object? TargetFacts(TargetSnapshot? value) => value is null ? null : new { actor_id = value.ActorId.Value,
        definition_name = Raw(value.DefinitionName), mesh_binding = Raw(value.MeshBinding), is_active = value.IsActive,
        pose = value.Pose is null ? null : new { position_millimeters = new { x = value.Pose.PositionMillimeters.X, y = value.Pose.PositionMillimeters.Y, z = value.Pose.PositionMillimeters.Z },
            basis_float_bits = new { row0_x = value.Pose.BasisFloatBits.Row0X, row0_y = value.Pose.BasisFloatBits.Row0Y, row0_z = value.Pose.BasisFloatBits.Row0Z,
                row1_x = value.Pose.BasisFloatBits.Row1X, row1_y = value.Pose.BasisFloatBits.Row1Y, row1_z = value.Pose.BasisFloatBits.Row1Z,
                row2_x = value.Pose.BasisFloatBits.Row2X, row2_y = value.Pose.BasisFloatBits.Row2Y, row2_z = value.Pose.BasisFloatBits.Row2Z } } };
    private static float Float(uint bits) => BitConverter.UInt32BitsToSingle(bits);
    private static uint Word(float value) => BitConverter.SingleToUInt32Bits(value);
}
