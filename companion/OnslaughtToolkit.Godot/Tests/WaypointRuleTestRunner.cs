// SPDX-License-Identifier: GPL-3.0-only
using Godot;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Only authored, read-only waypoint checks. No mod staging or launch checks are dispatched.</summary>
public partial class WaypointRuleTestRunner : SceneTree
{
    public override void _Initialize() => _ = RunAsync();

    private async Task RunAsync()
    {
        int exitCode = 1;
        try
        {
            string output = Path.Combine(OS.GetUserDataDir(), "waypoint-rule-checks");
            Directory.CreateDirectory(output);
            Checks check = new();
            WaypointRuleAuditTests.Run(check);
            await WaypointRulePageTests.RunAsync(this, output, check);
            foreach (string failure in check.Failures) GD.PrintErr("FAIL: " + failure);
            GD.Print($"WAYPOINT_RULE_TESTS: {check.Count} checks, {check.Failures.Count} failures.");
            exitCode = check.Failures.Count == 0 ? 0 : 1;
        }
        catch (Exception error) { GD.PrintErr("WAYPOINT_RULE_TESTS stopped: " + error); }
        finally { Quit(exitCode); }
    }
}
