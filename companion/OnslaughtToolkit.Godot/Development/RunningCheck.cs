// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Files;

namespace OnslaughtToolkit.Companion.Development;

/// <summary>
/// Prints what the companion's running-game check sees right now: every process it counts as Battle Engine
/// Aquila, then <c>GAME_RUNNING true|false</c>. Reads the process list only. Development builds only:
/// <c>python tools/companion_godot.py test --script Development/RunningCheck.cs</c>.
/// </summary>
public partial class RunningCheck : SceneTree
{
    public override void _Initialize()
    {
        IReadOnlyList<string> running = GameProcess.Running();
        foreach (string process in running) GD.Print("GAME_PROCESS " + process);
        GD.Print($"GAME_RUNNING {(running.Count > 0 ? "true" : "false")}");
        Quit(0);
    }
}
