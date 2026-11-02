// SPDX-License-Identifier: GPL-3.0-only
using Godot;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Authored linked-scene geometry and existing viewport interactions, without installed assets.</summary>
public partial class CeLinkedSceneTestRunner : SceneTree
{
    public override void _Initialize() => _ = RunAsync();
    private async Task RunAsync()
    {
        int exit = 1;
        try
        {
            string output = OS.GetCmdlineUserArgs().FirstOrDefault(a => a.StartsWith("--output-dir=", StringComparison.Ordinal))?[13..]
                ?? throw new InvalidOperationException("An owned --output-dir is required.");
            Checks check = new();
            await CeLinkedSceneTests.RunAsync(this, output, check);
            await TerrainViewportProjectionTests.RunAsync(this, check);
            foreach (string failure in check.Failures) GD.PrintErr("FAIL: " + failure);
            GD.Print($"CE_LINKED_SCENE_TESTS: {check.Count} checks, {check.Failures.Count} failures.");
            exit = check.Failures.Count == 0 ? 0 : 1;
        }
        catch (Exception error) { GD.PrintErr("CE_LINKED_SCENE_TESTS stopped: " + error); }
        finally { Quit(exit); }
    }
}
