// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Careers;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// For the curious, under Advanced: the open career's values exactly as stored, and a byte-for-byte comparison with
/// another career. Both views are read-only; neither file changes.
/// </summary>
internal sealed class CareerBytesPage : Page
{
    private readonly CareerWorkspace _workspace;
    private readonly StatusLine _status;
    private readonly PanelContainer _comparePanel;

    internal CareerBytesPage(CareerWorkspace workspace, StatusLine status, Node popups) : base("bytes", "Career bytes", "raw")
    {
        (_workspace, _status) = (workspace, status);
        VBoxContainer column = Build.Column(14);
        column.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        Root = column;
        column.Add(Build.Notice("For the curious: the open career's values exactly as stored, or every byte that differs from " +
            "another career, including bytes whose meaning is unknown. Read-only; no file is changed.").Panel);
        HBoxContainer actions = column.Add(Build.Row(12));
        View = actions.Add(new OptionButton { TooltipText = "What to show" });
        View.AddItem("Stored values", 0);
        View.AddItem("Compare with another career", 1);
        View.ItemSelected += _ => ShowView();
        CompareButton = actions.Add(Build.Button("Choose a career to compare…", "Primary", disabled: true));

        (_comparePanel, VBoxContainer summaryBody) = Build.Panel("Inset", 4);
        Summary = summaryBody.Add(Build.Detail("Open a career first, then choose the career to compare with it.", bbcode: true));
        column.Add(_comparePanel);
        Values = column.Add(Build.Table("Record", "Stored value", "Reading"));
        Values.SetColumnCustomMinimumWidth(0, 220);
        Differences = column.Add(Build.Table("Offset", "Region", "Original", "Other"));
        Differences.SetColumnCustomMinimumWidth(0, 110);
        Differences.SetColumnCustomMinimumWidth(1, 220);

        Dialog = popups.Add(Build.FilePicker("Compare another career", FileDialog.FileModeEnum.OpenFile, "*.bes ; Career saves"));
        CompareButton.Pressed += () => Dialog.PopupCenteredRatio(0.75f);
        Dialog.FileSelected += path => _status.Track(CompareAsync(path));
        ShowView();
    }

    internal override Control Root { get; }
    internal override string Subtitle => View.Selected == 1 ? "Every byte that differs between two careers, read-only"
        : "The open career's raw values, read-only";
    internal OptionButton View { get; }
    internal Button CompareButton { get; }
    internal RichTextLabel Summary { get; }
    internal Tree Values { get; }
    internal Tree Differences { get; }
    internal FileDialog Dialog { get; }

    internal override void Refresh() => CompareButton.Disabled = _workspace.Session is null || _workspace.Busy;

    /// <summary>Shows the stored values, or the comparison.</summary>
    internal void ShowView(int? view = null)
    {
        if (view is int chosen) View.Select(chosen);
        bool compare = View.Selected == 1;
        Values.Visible = !compare;
        Differences.Visible = _comparePanel.Visible = CompareButton.Visible = compare;
        HeaderChanged?.Invoke();
    }

    internal void ShowSession(SaveSession session)
    {
        Differences.Clear();
        Summary.Text = "Choose another career to compare with the open one.";
        CareerInspection analysis = session.Analysis;
        Values.Clear();
        TreeItem root = Values.CreateItem();
        TreeItem missions = Build.TableRow(Values, root, "Mission records",
            $"{analysis.MissionCensus.Used} used · {analysis.MissionCensus.Completed} complete",
            "Unused slots are kept as stored; the game only ever zeroes the attempts field");
        foreach (MissionRecord record in analysis.Missions.Where(record => record.Used))
        {
            Build.TableRow(Values, missions, $"Slot {record.Index} · level {record.World}",
                $"complete {record.CompleteRaw} · attempts field {record.Attempts} · rank 0x{record.RankBits:X8}",
                record.RankLetter is string letter ? $"Rank {letter} by the game's rule" : "Rank outside the game's letters");
        }
        LinkCensus links = analysis.LinkCensus;
        TreeItem linkRow = Build.TableRow(Values, root, "Campaign links",
            $"{links.Used} used · {links.Complete} complete · {links.AlternateRoutes} alternate · {links.Locked} locked · {links.Unknown} unknown",
            "Only complete links open a mission; alternate routes are the game's broken-line bookkeeping");
        linkRow.Collapsed = true;
        foreach (LinkRecord record in analysis.Links.Where(record => record.Used))
            Build.TableRow(Values, linkRow, $"Link {record.Index} to node {record.ToNode}", $"0x{record.RawState:X8}", Describe(record.State));
        TreeItem goodies = Build.TableRow(Values, root, "Goodies", "300 stored slots",
            "The gallery shows 230; 071–073 are kept but never shown; 233–299 are reserved and preserved");
        goodies.Collapsed = true;
        foreach (GoodieRecord record in analysis.Goodies)
            Build.TableRow(Values, goodies, $"Goodie {record.Index:D3} · 0x{record.Offset:X4}", $"0x{record.RawState:X8}", Describe(record.State));
        TreeItem tech = Build.TableRow(Values, root, "Tech slots", "32 raw words", "Read only; no interpretation is offered");
        tech.Collapsed = true;
        for (int index = 0; index < analysis.TechSlots.Count; index++)
            Build.TableRow(Values, tech, $"Slot {index}", $"0x{analysis.TechSlots[index]:X8}", "Read only");
        Build.TableRow(Values, root, "Pending extra Goodies", $"0x{analysis.PendingGoodiesRaw:X8}", "Cleared by the game's startup reset");
        Build.TableRow(Values, root, "Career in progress", $"0x{analysis.CareerInProgressRaw:X8}", "Stored flag");
        Build.TableRow(Values, root, "Sound / music volume", $"{analysis.SoundVolume.Value} / {analysis.MusicVolume.Value}",
            "Stored floats; a menu load keeps the game's current volumes");
        // CCareer::mIsGod[2]. The game's code applies a set flag whatever the career's name; Maladim only adds the menu toggle.
        for (int player = 0; player < analysis.GodFlags.Count; player++)
        {
            Build.TableRow(Values, root, $"Player {player + 1} god flag · 0x{CareerSave.GodFlagOffsets[player]:X4}",
                $"0x{analysis.GodFlags[player]:X8}", analysis.GodFlags[player] == 0 ? "Off" :
                "On: the game's code makes this player's Battle Engine invulnerable with infinite energy (read from the code; not yet seen in play)");
        }
        Build.TableRow(Values, root, "Everything else", "Preserved in full",
            "Options, the stored screen-position setting in the top kill bytes, and unknown data are never edited here");
    }

    internal async Task<Outcome<CareerComparison>> CompareAsync(string path)
    {
        if (_workspace.Busy || _workspace.Session is not SaveSession original)
            return Outcome<CareerComparison>.Refusal("Open an original first.");
        _status.Show("Opening the comparison career…");
        Outcome<CareerComparison> result = await _workspace.CompareAsync(path);
        if (result.Value is not CareerComparison comparison)
        {
            _status.Show(result.Message, StatusKind.Failure);
            return result;
        }
        ByteComparison bytes = comparison.Bytes;
        string verdict = bytes.Equal ? "[color=#" + Palette.Good.ToHtml(false) + "]Byte-for-byte identical.[/color]"
            : $"[color=#{Palette.Data.ToHtml(false)}]{bytes.ChangedBytes:N0} differing bytes[/color] in " +
              string.Join(", ", bytes.Regions.Select(region => $"{region.Key} ({region.Value})")) + ".";
        Summary.Text = $"[b]{comparison.Other.Path.Replace("[", "[lb]")}[/b]\n{verdict}\n" +
            $"[code]other    {comparison.Other.Sha256}\noriginal {original.Sha256}[/code]";
        Differences.Clear();
        TreeItem root = Differences.CreateItem();
        foreach (ByteChange change in bytes.Changes)
            Build.TableRow(Differences, root, $"0x{change.Offset:X4}", CareerSave.RegionOf(change.Offset), Hex(change.Before), Hex(change.After));
        ShowView(1);
        _status.Show(result.Message, StatusKind.Success);
        return result;
    }

    private static string Hex(int value) => value == ByteComparison.MissingByte ? "absent" : $"{value:X2}";

    private static string Describe(Enum state) => state switch
    {
        LinkState.AlternateRoute => "alternate route",
        GoodieState.Old => "viewed",
        GoodieState.Hint => "hint shown",
        _ => state.ToString().ToLowerInvariant(),
    };
}
