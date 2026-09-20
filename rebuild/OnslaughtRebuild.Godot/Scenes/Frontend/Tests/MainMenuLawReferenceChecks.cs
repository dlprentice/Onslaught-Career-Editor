// SPDX-License-Identifier: GPL-3.0-or-later
using Godot;
using A = Godot.Collections.Array;
using D = Godot.Collections.Dictionary;
namespace OnslaughtRebuild.GodotClient;

/// <summary>Exact raw-word fixtures from the unchanged Main Menu expression
/// owners. No input/session clock, rendering or retail file mutation occurs.</summary>
public sealed partial class MainMenuLawReferenceChecks : Node
{
    public override void _Ready()
    {
        MainMenuReference? reference = null;
        try
        {
            string[] args = OS.GetCmdlineUserArgs();
            if (args.Length != 1 || Engine.IsEditorHint() || DisplayServer.GetName() != "headless")
                throw new InvalidOperationException("One fresh owned fixture path and headless runtime are required.");
            string path = Path.GetFullPath(args[0]);
            string owner = Path.GetFullPath(ProjectSettings.GlobalizePath("res://../../local-data")) + Path.DirectorySeparatorChar;
            if (!Path.IsPathFullyQualified(args[0]) || !string.Equals(path, args[0], StringComparison.Ordinal)
                || !path.StartsWith(owner, StringComparison.Ordinal) || args[0].Contains('\\')
                || File.Exists(path) || Directory.Exists(path) || new FileInfo(path).LinkTarget is not null)
                throw new IOException("Fixture must be fresh beneath the worktree local-data owner.");
            for (DirectoryInfo? parent = new(Path.GetDirectoryName(path)!); parent is not null; parent = parent.Parent)
                if (parent.LinkTarget is not null) throw new IOException("Fixture ancestry must not contain symlinks.");
            reference = new MainMenuReference();
            using A cases = new();
            float[] edges = [-float.MaxValue, -1f, -0f, 0f, float.Epsilon, 0.1f, 0.2f, 0.3f, 0.4f, 0.5f, 0.6f,
                0.7f, 0.75f, 0.8f, 0.9f, 1f, 2f, float.MaxValue];
            foreach (float edge in edges)
                foreach (float t in new[] { MathF.BitDecrement(edge), edge, MathF.BitIncrement(edge) }) AddCase(cases, reference, t, t);
            for (int step = 0; step <= 4096; step++) AddCase(cases, reference, step / 4096f, step / 60d);
            uint random = 0x462d40u;
            for (int index = 0; index < 1024; index++)
            {
                random = unchecked(random * 1664525 + 1013904223);
                float t = random / (float)uint.MaxValue;
                random = unchecked(random * 1664525 + 1013904223);
                AddCase(cases, reference, t, (random / (double)uint.MaxValue) * 86_400d);
            }
            foreach (double seconds in new[] { -1e100, -1e40, -1000d, -0d, 0d, double.Epsilon, 1d / 60d, 1.53d,
                10d, 20d, 1e10, 1e40, 1e100 }) AddCase(cases, reference, 1f, seconds);
            using A colors = new();
            foreach (int fade in Enumerable.Range(-1, 258).Concat([int.MinValue, int.MaxValue]))
                foreach (bool selected in new[] { false, true })
                    foreach (bool available in new[] { false, true })
                    {
                        using D row = new() { ["fade"] = fade, ["selected"] = selected, ["available"] = available,
                            ["base"] = (long)RetailMainMenuLabelColor.BaseColor(selected, available),
                            ["label"] = (long)RetailMainMenuLabelColor.SubmittedColor(selected, available, fade),
                            ["selector"] = (long)RetailMainMenuSelectorBarColor.SubmittedColor(fade) };
                        colors.Add(row);
                    }
            using D fixture = new() { ["schema"] = 1, ["cases"] = cases, ["colors"] = colors,
                ["case_count"] = cases.Count, ["color_count"] = colors.Count,
                ["completed"] = new A { "main_menu_law_reference" } };
            using (var output = Godot.FileAccess.Open(path, Godot.FileAccess.ModeFlags.Write) ?? throw new IOException("Cannot write fixture.")) output.StoreVar(fixture, false);
            reference.Free(); reference = null;
            GD.Print($"MAIN_MENU_LAW_REFERENCE: {cases.Count} expression rows, {colors.Count} packed-color rows; {path}");
            GetTree().Quit(0);
        }
        catch (Exception error) { reference?.Free(); GD.PushError(error.ToString()); GetTree().Quit(1); }
    }

    private static void AddCase(A cases, MainMenuReference reference, float transition, double seconds)
    {
        using D expected = reference.InspectLaws(transition, seconds);
        List<int> words = [];
        foreach (string key in new[] { "fade", "icon", "underlay", "scroll" }) words.Add(Bits((float)expected[key].AsDouble()));
        using A decorations = expected["decorations"].AsGodotArray();
        List<byte> draws = [];
        List<int> matrixWords = [];
        foreach (Variant value in decorations)
        {
            using D decor = value.AsGodotDictionary();
            foreach (string key in new[] { "scale", "rotation", "alpha" }) words.Add(Bits((float)decor[key].AsDouble()));
            draws.Add(decor["draw"].AsBool() ? (byte)1 : (byte)0);
            Transform2D matrix = decor["transform"].AsTransform2D();
            matrixWords.AddRange([Bits(matrix.X.X), Bits(matrix.X.Y), Bits(matrix.Y.X), Bits(matrix.Y.Y)]);
        }
        double[] shadow = expected["shadow"].AsFloat64Array();
        using D row = new() { ["transition"] = (double)transition, ["seconds"] = seconds,
            ["words"] = words.ToArray(), ["draws"] = draws.ToArray(), ["matrices"] = matrixWords.ToArray(),
            ["double_words"] = new long[] { BitConverter.DoubleToInt64Bits(expected["phase"].AsDouble()), BitConverter.DoubleToInt64Bits(shadow[0]), BitConverter.DoubleToInt64Bits(shadow[1]) } };
        cases.Add(row);
    }
    private static int Bits(float value) => BitConverter.SingleToInt32Bits(value);
}
