// SPDX-License-Identifier: GPL-3.0-only
using Godot;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Focused editor checks on authored fixtures; no career, installed game or external action is needed.</summary>
public partial class EditorPreviewTestRunner : SceneTree
{
    public override void _Initialize() => _ = RunAsync();

    private async Task RunAsync()
    {
        int exitCode = 1;
        try
        {
            string output = Path.Combine(OS.GetUserDataDir(), "editor-preview-checks");
            Directory.CreateDirectory(output);
            Checks check = new();
            LevelTerrainTests.Run(output, check);
            TerrainDraftTests.Run(check);
            LevelTriggerEditTests.Run(check);
            await TerrainViewportProjectionTests.RunAsync(this, check);
            await TerrainPreviewPageTests.RunAsync(this, output, check);
            foreach (string failure in check.Failures) GD.PrintErr("FAIL: " + failure);
            GD.Print($"EDITOR_PREVIEW_TESTS: {check.Count} checks, {check.Failures.Count} failures.");
            exitCode = check.Failures.Count == 0 ? 0 : 1;
        }
        catch (Exception error) { GD.PrintErr("EDITOR_PREVIEW_TESTS stopped: " + error); }
        finally { Quit(exitCode); }
    }
}
