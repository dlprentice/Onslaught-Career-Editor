// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Careers;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>Read-only stored values of the open career. Unknown and reserved values stay raw.</summary>
internal sealed class InspectorPage
{
    internal InspectorPage()
    {
        Root = Build.Column(12);
        Root.Name = "Career inspector";
        Root.Add(Build.Text("Read-only stored values from the opened career. Unknown and reserved values remain raw; " +
            "these observations do not establish in-game behavior."));
        Tree = Root.Add(Build.Table("Record", "Stored value", "Interpretation"));
        Tree.SetColumnCustomMinimumWidth(0, 150);
    }

    internal VBoxContainer Root { get; }
    internal Tree Tree { get; }

    internal void ShowSession(SaveSession session)
    {
        CareerInspection analysis = session.Analysis;
        Tree.Clear();
        TreeItem root = Tree.CreateItem();
        TreeItem missions = Build.TableRow(Tree, root, "Mission records",
            $"{analysis.MissionCensus.Used} used; {analysis.MissionCensus.Completed} completed",
            "Unused slots and unknown ranks are retained");
        foreach (MissionRecord record in analysis.Missions.Where(record => record.Used))
        {
            Build.TableRow(Tree, missions, $"Slot {record.Index} · world {record.World}",
                $"Complete {record.CompleteRaw} · attempts {record.Attempts}",
                $"{record.RankLetter ?? "no letter (outside the game's range)"} · stored 0x{record.RankBits:X8}");
        }
        LinkCensus links = analysis.LinkCensus;
        TreeItem linkRow = Build.TableRow(Tree, root, "Links",
            $"{links.Used} used · {links.Locked} locked · {links.Complete} complete · {links.AlternateRoutes} alternate routes · " +
            $"{links.Unknown} unknown · {links.Unused} unused", "Only complete links open a mission; alternate routes are the game's broken-line bookkeeping");
        linkRow.Collapsed = true;
        foreach (LinkRecord record in analysis.Links.Where(record => record.Used))
            Build.TableRow(Tree, linkRow, $"Slot {record.Index} → {record.ToNode}", $"0x{record.RawState:X8}", Label(record.State));
        TreeItem goodies = Build.TableRow(Tree, root, "Goodies", "300 stored slots", "Slots 233–299 reserved; raw state preserved");
        goodies.Collapsed = true;
        foreach (GoodieRecord record in analysis.Goodies)
            Build.TableRow(Tree, goodies, $"Slot {record.Index} · 0x{record.Offset:X4}", $"0x{record.RawState:X8}", Label(record.State));
        TreeItem tech = Build.TableRow(Tree, root, "Tech slots", "32 raw words", "No editable interpretation in this workflow");
        tech.Collapsed = true;
        for (int index = 0; index < analysis.TechSlots.Count; index++)
            Build.TableRow(Tree, tech, $"Slot {index}", $"0x{analysis.TechSlots[index]:X8}", "Read only");
        Build.TableRow(Tree, root, "Sound / music", $"{analysis.SoundVolume.Value} / {analysis.MusicVolume.Value}",
            "Stored floats; no runtime range claim");
        Build.TableRow(Tree, root, "Other bytes", "Preserved in full", "Options tail, packed bytes and unknown data are not edited");
    }

    private static string Label(Enum state) => state.ToString().ToLowerInvariant();
}
