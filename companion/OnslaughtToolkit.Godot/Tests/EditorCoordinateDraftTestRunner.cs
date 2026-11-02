// SPDX-License-Identifier: GPL-3.0-only
using Godot;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Focused authored coordinate checks; no full-suite, export, capture or game launch is dispatched.</summary>
public partial class EditorCoordinateDraftTestRunner : SceneTree
{
    public override void _Initialize() => _ = RunAsync();

    private async Task RunAsync()
    {
        int code = 1;
        try
        {
            string output = Path.Combine(OS.GetUserDataDir(), "coordinate-draft-checks");
            Directory.CreateDirectory(output);
            Checks check = new();
            await EditorCoordinateDraftTests.RunAsync(this, output, check);
            foreach (string failure in check.Failures) GD.PrintErr("FAIL: " + failure);
            GD.Print($"COORDINATE_DRAFT_TESTS: {check.Count} checks, {check.Failures.Count} failures.");
            code = check.Failures.Count == 0 ? 0 : 1;
        }
        catch (Exception error) { GD.PrintErr("COORDINATE_DRAFT_TESTS stopped: " + error); }
        finally { Quit(code); }
    }
}
