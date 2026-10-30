// SPDX-License-Identifier: GPL-3.0-only
using Godot;

namespace OnslaughtToolkit.Companion.Development;

/// <summary>
/// The local retail conformance gate for the level data layer. Every world body of every level archive in an installed game
/// must read, write back to the same bytes, have each compiled script checked and no script name used twice, and, when the Toolkit reference's table is given, dump to the same fields the
/// reference reads (the table holds sizes and hashes only). A game with no compiled scripts does not pass. The game folder comes from BEA_GAME and is only read; nothing it
/// holds is printed or kept. Not part of the contract tests: it needs a game.
/// <code>
/// python tools/level_editor_vectors.py gate-table --game GAME --stdout &gt; TABLE.tsv
/// BEA_GAME=GAME LEVELS_TABLE=TABLE.tsv python tools/companion_godot.py test --script Development/LevelsGate.cs
/// </code>
/// </summary>
public partial class LevelsGate : SceneTree
{
    public override void _Initialize()
    {
        int exit;
        try
        {
            exit = LevelsGateCheck.Run(System.Environment.GetEnvironmentVariable("BEA_GAME") ?? "",
                System.Environment.GetEnvironmentVariable("LEVELS_TABLE") ?? "", message => GD.Print(message), message => GD.PrintErr(message));
        }
        catch (Exception error)
        {
            GD.PrintErr("LEVELS_GATE stopped unexpectedly: " + error);
            exit = 1;
        }
        Quit(exit);
    }
}
