// SPDX-License-Identifier: GPL-3.0-only
using Godot;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Authored project checks only; no career, game, mission compiler, stager or catalogue operation runs.</summary>
public partial class CeMissionProjectTestRunner : SceneTree
{
    public override void _Initialize()
    {
        int exit = 1;
        try
        {
            Checks check = new();
            CeMissionProjectTests.Run(check);
            foreach (string failure in check.Failures) GD.PrintErr("FAIL: " + failure);
            GD.Print($"CE_PROJECT_TESTS: {check.Count} checks, {check.Failures.Count} failures.");
            exit = check.Failures.Count == 0 ? 0 : 1;
        }
        catch (Exception error) { GD.PrintErr("CE_PROJECT_TESTS stopped: " + error); }
        Quit(exit);
    }
}
