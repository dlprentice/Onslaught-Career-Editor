// SPDX-License-Identifier: GPL-3.0-or-later
using System.Security.Cryptography;
using Godot;
using A = Godot.Collections.Array;
using D = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

/// <summary>Temporary oracle for the unchanged CFEPIntro expression owners.
/// This is CPU/headless only; no production lifecycle is advanced.</summary>
public sealed partial class ClickLawReferenceChecks : Node
{
    public override void _Ready()
    {
        try
        {
            string[] args = OS.GetCmdlineUserArgs();
            if (args.Length != 1 || Engine.IsEditorHint() || DisplayServer.GetName() != "headless")
                throw new InvalidOperationException("One fresh owned fixture path and headless runtime are required.");
            string path = Path.GetFullPath(args[0]);
            string owner = Path.GetFullPath(ProjectSettings.GlobalizePath("res://../../local-data")) + Path.DirectorySeparatorChar;
            if (!Path.IsPathFullyQualified(args[0]) || !path.StartsWith(owner, StringComparison.Ordinal) || File.Exists(path))
                throw new IOException("Fixture must be fresh beneath the worktree local-data owner.");
            using A cases = new();
            double[] edges = [-1e40, -100, -1, -0.0, 0, double.Epsilon, 1e-5, 0.25, 0.5, 0.75,
                1, 1.0 / 1.2, 2.0 / 1.2, 2, 2.25, 3, 4, 5, 6, 8, 30, 31, 1e40];
            foreach (double edge in edges)
                foreach (double time in new[] { Math.BitDecrement(edge), edge, Math.BitIncrement(edge) }) AddCase(cases, time);
            for (int step = 0; step <= 4096; step++) AddCase(cases, step / 4096d);
            for (int step = 0; step <= 512; step++) AddCase(cases, step / 64d);
            uint random = 0x78250u;
            for (int index = 0; index < 1024; index++)
            {
                random = unchecked(random * 1664525 + 1013904223);
                AddCase(cases, (random / (double)uint.MaxValue) * 8);
            }
            using A advances = new();
            foreach (double timer in new[] { 0d, -0d, RetailClickToStartPrompt.SeedValue, 0.5, 4, -4 })
                foreach (double page in new[] { 0d, 1, Math.BitIncrement(1d), 2, 30, Math.BitIncrement(30d) })
                    foreach (double delta in new[] { -0.25, 0d, 1d / 60, 0.5 })
                    {
                        using D row = new() { ["timer"] = timer, ["page"] = page, ["delta"] = delta,
                            ["bits"] = BitConverter.DoubleToInt64Bits(RetailClickToStartPrompt.Advance(timer, page, delta)) };
                        advances.Add(row);
                    }
            using A glyphs = new();
            foreach (int width in new[] { int.MinValue, -1, 0, 1, 2, 77, 98, 101, 16_777_217, int.MaxValue })
                for (int index = 0; index < 5; index++)
                {
                    using D row = new() { ["width"] = width, ["pass"] = index,
                        ["bits"] = Bits(RetailClickToStartGlyphs.X(RetailClickToStartGlyphs.Passes[index], width)) };
                    glyphs.Add(row);
                }
            using D fixture = new() { ["schema"] = 1, ["cases"] = cases, ["advances"] = advances, ["glyphs"] = glyphs };
            using Variant value = fixture;
            using (var output = Godot.FileAccess.Open(path, Godot.FileAccess.ModeFlags.Write) ?? throw new IOException("Cannot write fixture.")) output.StoreVar(value, false);
            GD.Print($"CLICK_LAW_REFERENCE: {cases.Count} expression rows, {advances.Count} clock rows, {glyphs.Count} glyph rows; {path}");
            GetTree().Quit(0);
        }
        catch (Exception error) { GD.PushError(error.ToString()); GetTree().Quit(1); }
    }

    private static void AddCase(A cases, double time)
    {
        int[] words = [Bits(RetailClickToStartPrompt.SplashArgument(time)), Bits(RetailClickToStartSplash.Scale(time)),
            Bits(RetailClickToStartSplash.X(time)), Bits(RetailClickToStartSplash.Y(time)),
            Bits(RetailClickToStartSlide.Fade(time)), Bits(RetailClickToStartSlide.Offset(time)),
            Bits(RetailClickToStartSlide.X(RetailClickToStartSlide.Passes[0], time)),
            Bits(RetailClickToStartSlide.X(RetailClickToStartSlide.Passes[1], time)),
            Bits(RetailClickToStartTitle.Scale(time)), Bits(RetailClickToStartTitle.SixthScale(time))];
        long[] colors = [RetailClickToStartTitle.OutlineColor(time), RetailClickToStartTitle.BodyColor(time), RetailClickToStartTitle.SixthColor(time)];
        using D row = new() { ["time"] = time, ["words"] = words, ["colors"] = colors,
            ["prompt"] = RetailClickToStartGlyphs.ShouldDraw(time), ["title"] = RetailClickToStartTitle.ShouldDraw(time),
            ["sixth"] = RetailClickToStartTitle.ShouldDrawSixth(time), ["idle"] = RetailClickToStartPrompt.ShouldWriteIdleResult(time) };
        cases.Add(row);
    }
    private static int Bits(float value) => BitConverter.SingleToInt32Bits(value);
}
