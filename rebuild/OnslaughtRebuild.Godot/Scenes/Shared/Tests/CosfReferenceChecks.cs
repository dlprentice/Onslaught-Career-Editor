// SPDX-License-Identifier: GPL-3.0-or-later
using System.Runtime.InteropServices;
using Godot;
using A = Godot.Collections.Array;
using D = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

/// <summary>Temporary direct MathF.Cos and finite Math.FusedMultiplyAdd oracle.
/// Synthetic operands only; neither a scene lifecycle nor retail state is run.</summary>
public sealed partial class CosfReferenceChecks : Node
{
    public override void _Ready()
    {
        try
        {
            string[] args = OS.GetCmdlineUserArgs();
            if (args.Length != 2 || Engine.IsEditorHint() || DisplayServer.GetName() != "headless")
                throw new InvalidOperationException("Two fresh owned outputs and headless runtime are required.");
            string fixturePath = Owned(args[0]), reportPath = Owned(args[1]);
            if (fixturePath == reportPath) throw new IOException("Distinct outputs required.");
            var words = new SortedSet<uint>();
            void Add(uint word) => words.Add(word);
            void Value(float value) => Add(unchecked((uint)BitConverter.SingleToInt32Bits(value)));
            foreach (uint sign in new[] { 0u, 0x80000000u })
            {
                for (uint exponent = 0; exponent < 256; exponent++)
                    foreach (uint fraction in new[] { 0u, 1u, 2u, 0x3fffffu, 0x400000u, 0x7ffffeu, 0x7fffffu })
                        Add(sign | (exponent << 23) | fraction);
                foreach (uint boundary in new[] { 0x39800000u, 0x3f400000u, 0x42f00000u, 0x7f800000u })
                    for (int delta = -4; delta <= 4; delta++) Add(sign | unchecked((uint)(boundary + delta)));
                for (int step = 0; step <= 4096; step++)
                    Value((sign == 0 ? 1f : -1f) * (step / 4096f) * MathF.PI);
            }
            for (int multiple = -76; multiple <= 76; multiple++)
            {
                float value = multiple * (MathF.PI / 2f);
                for (int neighbour = -3; neighbour <= 3; neighbour++)
                {
                    float near = value;
                    for (int index = 0; index < Math.Abs(neighbour); index++)
                        near = neighbour < 0 ? MathF.BitDecrement(near) : MathF.BitIncrement(near);
                    Value(near);
                }
            }
            uint random = 0x618523u;
            for (int index = 0; index < 8192; index++)
            {
                random = unchecked(random * 1664525u + 1013904223u);
                Add(random);
            }
            int[] inputs = words.Select(word => unchecked((int)word)).ToArray();
            int[] outputs = inputs.Select(word => BitConverter.SingleToInt32Bits(MathF.Cos(BitConverter.Int32BitsToSingle(word)))).ToArray();
            using A fmas = new();
            void Fma(double a, double b, double c)
            {
                if (!double.IsFinite(a) || !double.IsFinite(b) || !double.IsFinite(c)) throw new InvalidOperationException("Finite FMA fixture only.");
                long[] values = [BitConverter.DoubleToInt64Bits(a), BitConverter.DoubleToInt64Bits(b), BitConverter.DoubleToInt64Bits(c),
                    BitConverter.DoubleToInt64Bits(Math.FusedMultiplyAdd(a, b, c))];
                using Variant value = values;
                fmas.Add(value);
            }
            double onePlus = 1.0 + Math.ScaleB(1.0, -27), oneMinus = 1.0 - Math.ScaleB(1.0, -27);
            foreach ((double a, double b, double c) in new (double, double, double)[]
            {
                (onePlus, oneMinus, -1), (-onePlus, oneMinus, 1),
                (Math.BitIncrement(1), Math.BitDecrement(1), -1),
                (double.MaxValue, 2, -double.MaxValue), (-double.MaxValue, 2, double.MaxValue),
                (double.Epsilon, 0.5, double.Epsilon), (-double.Epsilon, 0.5, -double.Epsilon),
                (double.Epsilon, 0.5, 0), (-double.Epsilon, 0.5, -0.0),
                (Math.ScaleB(1.0, -1022), Math.BitDecrement(1), -double.Epsilon),
                (0, -1, 0), (-0.0, 1, -0.0), (1, 1, -1), (-1, 1, 1),
                (1, Math.ScaleB(1, -53), 1), (1, Math.ScaleB(1, -53), Math.BitIncrement(1)),
            }) Fma(a, b, c);
            for (int index = 0; index < 2048; index++)
            {
                random = unchecked(random * 1664525u + 1013904223u);
                double x = ((random / (double)uint.MaxValue) * 2 - 1) * Math.PI;
                double square = x * x;
                Fma(square, -0.16666665941423424479, x);
                Fma(-Math.Round(x * (2 / Math.PI)), Math.PI / 2, x);
            }
            using D fixture = new()
            {
                ["schema"] = 1, ["completed"] = new A { "cosf_reference" }, ["inputs"] = inputs,
                ["outputs"] = outputs, ["fmas"] = fmas, ["runtime"] = RuntimeInformation.FrameworkDescription,
                ["architecture"] = RuntimeInformation.ProcessArchitecture.ToString(),
            };
            using Variant fixtureValue = fixture;
            using (var file = Godot.FileAccess.Open(fixturePath, Godot.FileAccess.ModeFlags.Write) ?? throw new IOException("Cannot create cosine fixture."))
                file.StoreVar(fixtureValue, false);
            using D report = new() { ["schema"] = 1, ["completed"] = new A { "cosf_reference" }, ["failure_count"] = 0,
                ["cosine_cases"] = inputs.Length, ["fma_cases"] = fmas.Count, ["runtime"] = RuntimeInformation.FrameworkDescription };
            using (var file = Godot.FileAccess.Open(reportPath, Godot.FileAccess.ModeFlags.Write) ?? throw new IOException("Cannot create cosine report."))
                file.StoreString(Json.Stringify(report));
            GD.Print($"COSF_REFERENCE: {inputs.Length} cosine words and {fmas.Count} finite FMA words; {fixturePath}");
            GetTree().Quit(0);
        }
        catch (Exception error) { GD.PushError(error.ToString()); GetTree().Quit(1); }
    }

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
