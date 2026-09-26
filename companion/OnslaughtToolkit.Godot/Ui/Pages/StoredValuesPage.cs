// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Careers;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>Every interpreted region of the open career as stored, with raw values beside the reading.</summary>
internal sealed class StoredValuesPage : Page
{
    private readonly CareerWorkspace _workspace;

    internal StoredValuesPage(CareerWorkspace workspace) : base("raw", "Raw values", "raw")
    {
        _workspace = workspace;
        VBoxContainer column = Build.Column(14);
        column.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        Root = column;
        column.Add(Build.Notice("For the curious: the open career's values exactly as stored, read-only. Unknown and reserved " +
            "values stay raw; a stored value does not by itself show how the game behaves.").Panel);
        Tree = column.Add(Build.Table("Record", "Stored value", "Reading"));
        Tree.SetColumnCustomMinimumWidth(0, 220);
    }

    internal override Control Root { get; }
    internal override string Subtitle => "The open career's raw values, read-only";
    internal Tree Tree { get; }

    internal void ShowSession(SaveSession session)
    {
        CareerInspection analysis = session.Analysis;
        Tree.Clear();
        TreeItem root = Tree.CreateItem();
        TreeItem missions = Build.TableRow(Tree, root, "Mission records",
            $"{analysis.MissionCensus.Used} used · {analysis.MissionCensus.Completed} complete",
            "Unused slots are kept as stored; the game only ever zeroes the attempts field");
        foreach (MissionRecord record in analysis.Missions.Where(record => record.Used))
        {
            Build.TableRow(Tree, missions, $"Slot {record.Index} · level {record.World}",
                $"complete {record.CompleteRaw} · attempts field {record.Attempts} · rank 0x{record.RankBits:X8}",
                record.RankLetter is string letter ? $"Rank {letter} by the game's rule" : "Rank outside the game's letters");
        }
        LinkCensus links = analysis.LinkCensus;
        TreeItem linkRow = Build.TableRow(Tree, root, "Campaign links",
            $"{links.Used} used · {links.Complete} complete · {links.AlternateRoutes} alternate · {links.Locked} locked · {links.Unknown} unknown",
            "Only complete links open a mission; alternate routes are the game's broken-line bookkeeping");
        linkRow.Collapsed = true;
        foreach (LinkRecord record in analysis.Links.Where(record => record.Used))
            Build.TableRow(Tree, linkRow, $"Link {record.Index} to node {record.ToNode}", $"0x{record.RawState:X8}", Describe(record.State));
        TreeItem goodies = Build.TableRow(Tree, root, "Goodies", "300 stored slots",
            "The gallery shows 230; 071–073 are kept but never shown; 233–299 are reserved and preserved");
        goodies.Collapsed = true;
        foreach (GoodieRecord record in analysis.Goodies)
            Build.TableRow(Tree, goodies, $"Goodie {record.Index:D3} · 0x{record.Offset:X4}", $"0x{record.RawState:X8}", Describe(record.State));
        TreeItem tech = Build.TableRow(Tree, root, "Tech slots", "32 raw words", "Read only; no interpretation is offered");
        tech.Collapsed = true;
        for (int index = 0; index < analysis.TechSlots.Count; index++)
            Build.TableRow(Tree, tech, $"Slot {index}", $"0x{analysis.TechSlots[index]:X8}", "Read only");
        Build.TableRow(Tree, root, "Pending extra Goodies", $"0x{analysis.PendingGoodiesRaw:X8}", "Cleared by the game's startup reset");
        Build.TableRow(Tree, root, "Career in progress", $"0x{analysis.CareerInProgressRaw:X8}", "Stored flag");
        Build.TableRow(Tree, root, "Sound / music volume", $"{analysis.SoundVolume.Value} / {analysis.MusicVolume.Value}",
            "Stored floats; a menu load keeps the game's current volumes");
        // CCareer::mIsGod[2]. The game's code applies a set flag whatever the career's name; Maladim only adds the menu toggle.
        for (int player = 0; player < analysis.GodFlags.Count; player++)
        {
            Build.TableRow(Tree, root, $"Player {player + 1} god flag · 0x{CareerSave.GodFlagOffsets[player]:X4}",
                $"0x{analysis.GodFlags[player]:X8}", analysis.GodFlags[player] == 0 ? "Off" :
                "On: the game's code makes this player's Battle Engine invulnerable with infinite energy (read from the code; not yet seen in play)");
        }
        Build.TableRow(Tree, root, "Everything else", "Preserved in full",
            "Options, the stored screen-position setting in the top kill bytes, and unknown data are never edited here");
    }

    private static string Describe(Enum state) => state switch
    {
        LinkState.AlternateRoute => "alternate route",
        GoodieState.Old => "viewed",
        GoodieState.Hint => "hint shown",
        _ => state.ToString().ToLowerInvariant(),
    };
}
