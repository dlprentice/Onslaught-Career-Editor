// SPDX-License-Identifier: GPL-3.0-only
using Godot;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Focused project and draft checks using authored inputs only.</summary>
public partial class EditorProjectTestRunner : SceneTree
{
    public override void _Initialize() => _ = RunAsync();

    private async Task RunAsync()
    {
        int exitCode = 1;
        try
        {
            string output = Path.Combine(OS.GetUserDataDir(), "editor-project-checks");
            Directory.CreateDirectory(output);
            Checks check = new();
            LevelTerrainTests.Run(output, check);
            TerrainDraftTests.Run(check);
            LevelScriptTests.Run(output, check);
            LevelScriptEditTests.Run(output, check);
            ScriptCompilerTests.Run(output, check);
            EditorProjectTests.Run(check);
            EditorProjectFilesTests.Run(output, check);
            await EditorProjectScriptsTests.RunAsync(this, output, check);
            foreach (string failure in check.Failures) GD.PrintErr("FAIL: " + failure);
            GD.Print($"EDITOR_PROJECT_TESTS: {check.Count} checks, {check.Failures.Count} failures.");
            exitCode = check.Failures.Count == 0 ? 0 : 1;
        }
        catch (Exception error) { GD.PrintErr("EDITOR_PROJECT_TESTS stopped: " + error.GetType().Name); }
        finally { Quit(exitCode); }
    }
}
