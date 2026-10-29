// SPDX-License-Identifier: GPL-3.0-only
using Godot;

namespace OnslaughtToolkit.Companion.Development;

/// <summary>
/// The local retail gate for the C# mission script compiler. Every compiled script of every world body of an installed game is compared
/// with what the compiler makes of the source the game folder holds for it (the compile session's counters taken from the shipped script),
/// the way <c>tools/msl_gate.py</c> does it for the Python reference: exact, exact once an include the install lacks is bound from the
/// shipped constants, or one of the pinned stale sources; anything else fails. When the reference's per-script table is given
/// (<c>msl_gate.py --table</c>) every script must also have the status the reference gave it. The game folder comes from BEA_GAME and is
/// only read; only counts and names are printed. Not part of the contract tests: it needs a game.
/// <code>
/// python tools/msl_gate.py --game GAME --table &gt; TABLE.tsv
/// BEA_GAME=GAME SCRIPTS_TABLE=TABLE.tsv python tools/companion_godot.py test --script Development/ScriptsGate.cs
/// </code>
/// </summary>
public partial class ScriptsGate : SceneTree
{
    public override void _Initialize()
    {
        int exit;
        try
        {
            exit = ScriptsGateCheck.Run(System.Environment.GetEnvironmentVariable("BEA_GAME") ?? "",
                System.Environment.GetEnvironmentVariable("SCRIPTS_TABLE") ?? "", message => GD.Print(message), message => GD.PrintErr(message));
        }
        catch (Exception error)
        {
            GD.PrintErr("SCRIPTS_GATE stopped unexpectedly: " + error);
            exit = 1;
        }
        Quit(exit);
    }
}
