// SPDX-License-Identifier: GPL-3.0-or-later
using System.Security.Cryptography;
using Godot;
using OnslaughtRebuild.Core;
using A = Godot.Collections.Array;
using D = Godot.Collections.Dictionary;
using Pose = OnslaughtRebuild.Core.RetailUnitAttachmentPose;
using V = OnslaughtRebuild.Core.Level100FloatVector3Bits;
using B = OnslaughtRebuild.Core.Level100FloatBasis3Bits;

namespace OnslaughtRebuild.GodotClient;

/// <summary>Temporary unchanged-C# pose oracle. Synthetic raw words only;
/// no private asset, frame selection, controller or simulation is run.</summary>
public sealed partial class MeshPartPoseReferenceChecks : Node
{
    private const int One = 0x3f800000;
    private static readonly B Identity = new(One, 0, 0, 0, One, 0, 0, 0, One);
    private static readonly B Ones = new(One, One, One, One, One, One, One, One, One);
    private static readonly Pose Origin = new(default, Identity);
    private int _checks;
    private sealed record Case(string Name, string Operation, Pose First, Pose Second = default,
        V Center = default, V Displacement = default);

    public override void _Ready()
    {
        try
        {
            string[] args = OS.GetCmdlineUserArgs();
            Check(args.Length == 2 && !Engine.IsEditorHint() && DisplayServer.GetName() == "headless", "Two fresh owned outputs and headless runtime are required.");
            string fixturePath = Owned(args[0]), reportPath = Owned(args[1]);
            Check(fixturePath != reportPath, "Distinct outputs are required.");
            Godot.Input.MouseModeEnum pointer = Godot.Input.MouseMode;
            string sourcePath = ProjectSettings.GlobalizePath("res://../OnslaughtRebuild.Core/RetailMeshPartPose.cs");
            string arithmeticPath = ProjectSettings.GlobalizePath("res://../OnslaughtRebuild.Core/RetailFloat24.cs");
            string sourceHash = Hash(sourcePath), arithmeticHash = Hash(arithmeticPath);
            BaselineAssertions();
            using A cases = new();
            using D counts = new();
            int admitted = 0, refused = 0;
            foreach (Case sample in Cases())
            {
                using D row = new() { ["name"] = sample.Name, ["operation"] = sample.Operation };
                using D input = Inputs(sample);
                Put(row, "input", input);
                object? output = null;
                ArgumentOutOfRangeException? failure = null;
                // Only the unchanged operation establishes a refusal. A
                // transport/assertion error must abort this oracle instead.
                try { output = Evaluate(sample); }
                catch (ArgumentOutOfRangeException error) { failure = error; }
                if (failure is null)
                {
                    Check(output is not null, "An admitted operation has a complete result.");
                    using D result = output is Pose pose ? Value(pose) : SphereValue(((V Position, V Displacement))output!);
                    admitted++;
                    row["ok"] = true;
                    Put(row, "value", result);
                }
                else
                {
                    refused++;
                    row["ok"] = false;
                    row["error_type"] = failure.GetType().Name;
                    row["parameter"] = failure.ParamName ?? "";
                    row["error"] = failure.Message;
                }
                using Variant rowValue = row;
                cases.Add(rowValue);
                using Variant previous = counts.TryGetValue(sample.Operation, out Variant found) ? found : Variant.From(0);
                counts[sample.Operation] = previous.AsInt32() + 1;
            }
            Check(Hash(sourcePath) == sourceHash && Hash(arithmeticPath) == arithmeticHash, "Original numerical sources remained unchanged.");
            Check(Godot.Input.MouseMode == pointer, "Oracle did not change pointer ownership.");
            using D sources = new() { ["RetailMeshPartPose.cs"] = sourceHash, ["RetailFloat24.cs"] = arithmeticHash };
            using A completed = new() { "mesh_part_pose_reference" };
            using D fixture = new() { ["schema"] = 1 };
            Put(fixture, "cases", cases); Put(fixture, "source_sha256", sources); Put(fixture, "completed", completed);
            using Variant fixtureValue = fixture;
            using (var file = Godot.FileAccess.Open(fixturePath, Godot.FileAccess.ModeFlags.Write) ?? throw new IOException("Cannot create pose fixture."))
                file.StoreVar(fixtureValue, false);
            using D report = new() { ["schema"] = 1, ["checks"] = _checks, ["failure_count"] = 0,
                ["cases"] = cases.Count, ["accepted"] = admitted, ["refused"] = refused };
            Put(report, "completed", completed); Put(report, "operations", counts); Put(report, "source_sha256", sources);
            using (var file = Godot.FileAccess.Open(reportPath, Godot.FileAccess.ModeFlags.Write) ?? throw new IOException("Cannot create pose report."))
                file.StoreString(Json.Stringify(report));
            GD.Print($"MESH_PART_POSE_REFERENCE: {_checks} assertions; {cases.Count} cases ({admitted} accepted, {refused} refused); {fixturePath}");
            GetTree().Quit(0);
        }
        catch (Exception error) { GD.PushError(error.ToString()); GetTree().Quit(1); }
    }

    private void BaselineAssertions()
    {
        var negativeZero = new Pose(new(int.MinValue, 0x3dbec640, int.MinValue), Identity with { Row0Y = int.MinValue, Row2X = int.MinValue });
        Check(RetailMeshPartPose.InterpolateSingleFrame(negativeZero) == new Pose(new(0, 0x3dbec640, 0), Identity), "Existing single-frame signed-zero expectation.");
        var query = RetailMeshPartPose.ToLocalSphereQuery(new(Vector(10, 20, 30), Identity with { Row0Y = Word(2) }), Vector(14, 25, 36), Vector(1, 2, 3));
        Check(query == (Vector(3, 9, 3), Vector(1, 4, 3)), "Existing nonorthogonal cached-transpose expectation.");
        var part = new Pose(Vector(16_777_216, 0, 0), Identity);
        query = RetailMeshPartPose.ToLocalSphereQuery(part, part.PositionFloatBits, Vector(-1, 0, 0));
        Check(query == (default(V), Vector(-1, 0, 0)), "Existing centre-minus-motion store expectation.");
        query = RetailMeshPartPose.ToLocalSphereQuery(new(default, Ones), Vector(1, -33_554_432, 33_554_432), default);
        Check(query.Position == Vector(1, 1, 1), "Existing Z/Y/X accumulation expectation.");
        int minusOne = I(0xbf800000);
        B minusOnes = new(minusOne, minusOne, minusOne, minusOne, minusOne, minusOne, minusOne, minusOne, minusOne);
        query = RetailMeshPartPose.ToLocalSphereQuery(new(default, minusOnes), default, default);
        Check(query.Displacement == new V(int.MinValue, int.MinValue, int.MinValue), "Existing stationary negative-zero displacement expectation.");
        Pose parent = new(new(minusOne, minusOne, minusOne), Ones);
        Pose local = new(new(One, Word(MathF.ScaleB(1, -24)), 0), Identity);
        Check(RetailMeshPartPose.ComposeHierarchy(parent, local).PositionFloatBits == default, "Existing hierarchy PC24 translation expectation.");
        Check(RetailMeshPartPose.ApplyOwner(parent, local).PositionFloatBits == default, "Existing owner PC24 translation expectation.");
        foreach (bool negativeMiddle in new[] { false, true })
        {
            int large = Word(MathF.ScaleB(1, 25)), negative = Word(-MathF.ScaleB(1, 25));
            int middle = negativeMiddle ? negative : One, last = negativeMiddle ? One : negative;
            local = new(default, new(large, large, large, middle, middle, middle, last, last, last));
            parent = new(default, Ones);
            B hierarchy = negativeMiddle ? new(0, 0, 0, 0, One, One, One, One, One) : new(One, 0, 0, 0, 0, 0, 0, 0, 0);
            B owner = negativeMiddle ? new(One, One, 0, One, One, 0, One, One, 0) : new(0, 0, 0, 0, 0, One, 0, 0, One);
            Check(RetailMeshPartPose.ComposeHierarchy(parent, local).BasisFloatBits == hierarchy, "Existing hierarchy matrix order expectation.");
            Check(RetailMeshPartPose.ApplyOwner(parent, local).BasisFloatBits == owner, "Existing owner matrix order expectation.");
        }
        parent = new(default, Identity with { Row0X = minusOne, Row0Y = 0x3f800001 });
        local = new(new(One, 0x3f7ffffe, 0), Identity);
        Check(RetailMeshPartPose.ApplyOwner(parent, local).PositionFloatBits.X == 0, "Existing rounded-product cancellation expectation.");
        int huge = Word(MathF.ScaleB(1, 100)), factor = Word(MathF.ScaleB(1, 40));
        parent = new(default, Identity with { Row0X = huge, Row0Y = huge ^ int.MinValue, Row0Z = One });
        local = new(new(factor, factor, One), Identity);
        Check(RetailMeshPartPose.ApplyOwner(parent, local).PositionFloatBits.X == One, "Existing retained wide-exponent cancellation expectation.");
        int tiny = Word(MathF.ScaleB(1, -100)), tinyFactor = Word(MathF.ScaleB(1, -50));
        parent = new(default, Identity with { Row0X = tiny, Row0Y = tiny, Row0Z = 0 });
        local = new(new(tinyFactor, tinyFactor, 0), Identity);
        Check(RetailMeshPartPose.ApplyOwner(parent, local).PositionFloatBits.X == 1, "Existing pre-store subnormal sum expectation.");
    }

    private static List<Case> Cases()
    {
        List<Case> cases = [];
        void Pair(string name, Pose parent, Pose local)
        {
            cases.Add(new(name + "/hierarchy", "compose_hierarchy", parent, local));
            cases.Add(new(name + "/owner", "apply_owner", parent, local));
        }
        void Sphere(string name, Pose part, V center, V displacement) => cases.Add(new(name, "to_local_sphere_query", part, default, center, displacement));
        cases.Add(new("identity", "interpolate_single_frame", Origin));
        Pair("identity", Origin, Origin);
        Pair("negative-zero", FromWords(Enumerable.Repeat(int.MinValue, 12).ToArray()), Origin);
        int[] finiteWords = [0, int.MinValue, 1, int.MinValue + 1, 2, 0x007fffff, I(0x807fffff), 0x00800000,
            I(0x80800000), 0x00800001, 0x3f000000, I(0xbf000000), 0x3f7fffff, One, 0x3f800001,
            I(0xbf800000), I(0xbf800001), 0x3dbec640, 0x3db709c2, 0x33800000, 0x33000000,
            0x4b000000, 0x4b800000, 0x4c000000, I(0xcc000000), 0x71800000, 0x0d800000, 0x7f7ffffe, 0x7f7fffff, I(0xff7fffff)];
        foreach (int word in finiteWords)
            for (int component = 0; component < 12; component++)
                cases.Add(new($"single/{component}/{unchecked((uint)word):x8}", "interpolate_single_frame", Set(Origin, component, word)));
        int halfUlp = Word(MathF.ScaleB(1, -24)), minusOne = I(0xbf800000);
        Pair("pc24-add", new(new(minusOne, minusOne, minusOne), Ones), new(new(One, halfUlp, 0), Identity));
        foreach (bool negativeMiddle in new[] { false, true })
        {
            int large = Word(MathF.ScaleB(1, 25)), negative = large ^ int.MinValue;
            int middle = negativeMiddle ? negative : One, last = negativeMiddle ? One : negative;
            Pair("matrix-orders/" + negativeMiddle, new(default, Ones), new(default, new(large, large, large, middle, middle, middle, last, last, last)));
        }
        Pair("pc24-product", new(default, Identity with { Row0X = minusOne, Row0Y = 0x3f800001 }), new(new(One, 0x3f7ffffe, 0), Identity));
        int huge = Word(MathF.ScaleB(1, 100)), factor = Word(MathF.ScaleB(1, 40));
        Pair("wide-cancellation", new(default, Identity with { Row0X = huge, Row0Y = huge ^ int.MinValue, Row0Z = One }), new(new(factor, factor, One), Identity));
        int tiny = Word(MathF.ScaleB(1, -100)), tinyFactor = Word(MathF.ScaleB(1, -50));
        Pair("subnormal-sum", new(default, Identity with { Row0X = tiny, Row0Y = tiny, Row0Z = 0 }), new(new(tinyFactor, tinyFactor, 0), Identity));
        foreach (int sign in new[] { 0, int.MinValue })
        {
            Pose maxX = new(default, Identity with { Row0X = 0x7f7fffff ^ sign });
            Pair("accepted-final-x-overflow/" + sign, maxX, new(new(0x7f7fffff, 0, 0), Identity));
            Pair("accepted-final-basis-overflow/" + sign, maxX, new(default, Identity with { Row0X = 0x7f7fffff }));
            Pair("rejected-y-intermediate-overflow/" + sign, new(default, Identity with { Row1Y = 0x7f7fffff ^ sign }), new(new(0, 0x7f7fffff, 0), Identity));
            Pair("rejected-z-intermediate-overflow/" + sign, new(default, Identity with { Row2Z = 0x7f7fffff ^ sign }), new(new(0, 0, 0x7f7fffff), Identity));
        }
        Sphere("nonorthogonal-transpose", new(Vector(10, 20, 30), Identity with { Row0Y = Word(2) }), Vector(14, 25, 36), Vector(1, 2, 3));
        Sphere("centre-first-store", new(Vector(16_777_216, 0, 0), Identity), Vector(16_777_216, 0, 0), Vector(-1, 0, 0));
        Sphere("z-y-x-order", new(default, Ones), Vector(1, -33_554_432, 33_554_432), default);
        Sphere("negative-zero-stationary", new(default, new(minusOne, minusOne, minusOne, minusOne, minusOne, minusOne, minusOne, minusOne, minusOne)), default, default);
        Sphere("centre-overflow", Origin, new(0x7f7fffff, 0, 0), new(I(0xff7fffff), 0, 0));
        Sphere("part-subtraction-overflow", new(new(I(0xff7fffff), 0, 0), Identity), new(0x7f7fffff, 0, 0), default);
        Sphere("accepted-final-query-overflow", new(default, Identity with { Row0X = 0x7f7fffff }), new(0x7f7fffff, 0, 0), default);
        Sphere("accepted-final-displacement-overflow", new(default, Identity with { Row0X = 0x7f7fffff }), new(0x7f7fffff, 0, 0), new(0x7f7fffff, 0, 0));
        int[] invalidWords = [0x7f800000, I(0xff800000), 0x7fc00000, I(0xffc00000), 0x7f800001, I(0xff800001), 0x7fffffff, -1];
        foreach (int invalid in invalidWords)
        {
            string hex = unchecked((uint)invalid).ToString("x8");
            for (int component = 0; component < 12; component++)
            {
                Pose pose = Set(Origin, component, invalid);
                cases.Add(new($"nonfinite/single/{component}/{hex}", "interpolate_single_frame", pose));
                Pair($"nonfinite/first/{component}/{hex}", pose, Origin);
                Pair($"nonfinite/second/{component}/{hex}", Origin, pose);
                Sphere($"nonfinite/part/{component}/{hex}", pose, default, default);
            }
            for (int axis = 0; axis < 3; axis++)
            {
                V vector = Set(Origin, axis, invalid).PositionFloatBits;
                Sphere($"nonfinite/center/{axis}/{hex}", Origin, vector, default);
                Sphere($"nonfinite/displacement/{axis}/{hex}", Origin, default, vector);
            }
        }
        Pose overflowingY = new(default, Identity with { Row1Y = 0x7f7fffff });
        Pose largeLocal = new(new(0, 0x7f7fffff, 0), Identity);
        Pair("bad-y-read-before-y-overflow", Set(overflowingY, 1, 0x7fc00000), largeLocal);
        Pair("y-overflow-before-bad-z-read", Set(overflowingY, 2, 0x7fc00000), largeLocal);
        Pair("basis-read-before-y-overflow", Set(overflowingY, 11, 0x7fc00000), largeLocal);
        Sphere("centre-overflow-before-bad-basis", Set(Origin, 11, 0x7fc00000), new(0x7f7fffff, 0, 0), new(I(0xff7fffff), 0, 0));
        Sphere("bad-part-read-before-centre-overflow", Set(Origin, 0, 0x7fc00000), new(0x7f7fffff, 0, 0), new(I(0xff7fffff), 0, 0));
        Sphere("all-displacement-reads-before-centre", Origin, new(0x7f7fffff, 0, 0), new(I(0xff7fffff), 0, 0x7fc00000));
        uint random = 0x502cab19;
        int Next(bool wide)
        {
            random = unchecked(random * 1664525u + 1013904223u);
            uint fraction = random & 0x007fffffu, sign = random & 0x80000000u;
            uint exponent = wide ? ((random >> 23) % 255) : 95u + ((random >> 24) % 64);
            return I(sign | (exponent << 23) | fraction);
        }
        Pose RandomPose(bool wide) => FromWords(Enumerable.Range(0, 12).Select(_ => Next(wide)).ToArray());
        foreach (bool wide in new[] { false, true })
            for (int i = 0; i < 128; i++)
            {
                Pose first = RandomPose(wide), second = RandomPose(wide);
                string name = $"varied/{wide}/{i}";
                cases.Add(new(name, "interpolate_single_frame", first));
                Pair(name, first, second);
                Sphere(name, first, second.PositionFloatBits, new(Next(wide), Next(wide), Next(wide)));
            }
        return cases;
    }

    private static object Evaluate(Case sample) => sample.Operation switch
    {
        "interpolate_single_frame" => RetailMeshPartPose.InterpolateSingleFrame(sample.First),
        "compose_hierarchy" => RetailMeshPartPose.ComposeHierarchy(sample.First, sample.Second),
        "apply_owner" => RetailMeshPartPose.ApplyOwner(sample.First, sample.Second),
        "to_local_sphere_query" => RetailMeshPartPose.ToLocalSphereQuery(sample.First, sample.Center, sample.Displacement),
        _ => throw new InvalidOperationException("Unknown pose operation.")
    };

    private static D Inputs(Case sample)
    {
        using D first = Value(sample.First), second = Value(sample.Second), center = Value(sample.Center), displacement = Value(sample.Displacement);
        D result = new();
        Put(result, "first", first); Put(result, "second", second); Put(result, "center", center); Put(result, "displacement", displacement);
        return result;
    }

    private static D Value(Pose pose)
    {
        using D position = Value(pose.PositionFloatBits), basis = Value(pose.BasisFloatBits);
        D result = new(); Put(result, "position_float_bits", position); Put(result, "basis_float_bits", basis); return result;
    }
    private static D SphereValue((V Position, V Displacement) query)
    {
        using D position = Value(query.Position), displacement = Value(query.Displacement);
        D result = new(); Put(result, "position", position); Put(result, "displacement", displacement); return result;
    }
    private static D Value(V vector) => new() { ["x"] = vector.X, ["y"] = vector.Y, ["z"] = vector.Z };
    private static D Value(B basis) => new()
    {
        ["row0_x"] = basis.Row0X, ["row0_y"] = basis.Row0Y, ["row0_z"] = basis.Row0Z,
        ["row1_x"] = basis.Row1X, ["row1_y"] = basis.Row1Y, ["row1_z"] = basis.Row1Z,
        ["row2_x"] = basis.Row2X, ["row2_y"] = basis.Row2Y, ["row2_z"] = basis.Row2Z,
    };
    private static void Put(D target, string key, D value) { using Variant carrier = value; target[key] = carrier; }
    private static void Put(D target, string key, A value) { using Variant carrier = value; target[key] = carrier; }
    private static Pose Set(Pose source, int index, int word)
    {
        V p = source.PositionFloatBits; B b = source.BasisFloatBits;
        int[] words = [p.X, p.Y, p.Z, b.Row0X, b.Row0Y, b.Row0Z, b.Row1X, b.Row1Y, b.Row1Z, b.Row2X, b.Row2Y, b.Row2Z];
        words[index] = word; return FromWords(words);
    }
    private static Pose FromWords(int[] words) => new(new(words[0], words[1], words[2]),
        new(words[3], words[4], words[5], words[6], words[7], words[8], words[9], words[10], words[11]));
    private static V Vector(float x, float y, float z) => new(Word(x), Word(y), Word(z));
    private static int Word(float value) => BitConverter.SingleToInt32Bits(value);
    private static int I(uint value) => unchecked((int)value);
    private void Check(bool condition, string message) { _checks++; if (!condition) throw new InvalidOperationException(message); }
    private static string Hash(string path) => Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path))).ToLowerInvariant();
    private static string Owned(string path)
    {
        string full = Path.GetFullPath(path), root = Path.GetFullPath(ProjectSettings.GlobalizePath("res://../../local-data"));
        if (path != full || !full.StartsWith(root + Path.DirectorySeparatorChar, StringComparison.Ordinal) || File.Exists(full) || !Directory.Exists(Path.GetDirectoryName(full)))
            throw new IOException("Fresh worktree-local output required.");
        string current = root;
        foreach (string segment in Path.GetRelativePath(root, full).Split(Path.DirectorySeparatorChar))
        {
            current = Path.Combine(current, segment);
            if (new FileInfo(current).LinkTarget is not null) throw new IOException("Output cannot traverse links.");
        }
        return full;
    }
}
