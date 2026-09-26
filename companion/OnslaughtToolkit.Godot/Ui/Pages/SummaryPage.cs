// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>The open career at a glance: missions, Goodies, kills and campaign routes, read-only.</summary>
internal sealed class SummaryPage : Page
{
    private readonly CareerWorkspace _workspace;
    private readonly GameLibrary _game;
    private readonly Label _empty;
    private readonly CareerCards _choose;
    private readonly GridContainer _stats, _columns;
    private readonly Label _missionsValue, _missionsDetail, _goodiesValue, _goodiesDetail, _killsValue, _ranksValue, _ranksDetail;
    private readonly ProgressBar _missionsMeter, _goodiesMeter;
    private readonly VBoxContainer _killRows;
    private readonly PanelContainer _campaign;
    private readonly Label _routeLine;
    private readonly GridContainer _goodieStrip;
    private readonly Label _namesNote;

    internal SummaryPage(AppServices app) : base("summary", "Summary", "summary")
    {
        (_workspace, _game) = (app.Workspace, app.Game);
        (ScrollContainer scroll, VBoxContainer content) = Build.Scroller();
        Root = scroll;
        _empty = content.Add(Build.Text("Choose a career to see its missions, Goodies and kills. Opening it only reads it.", "Lead"));
        _choose = new CareerCards(app);
        content.Add(_choose.Root);

        _stats = content.Add(new GridContainer { Columns = 4 });
        _stats.AddThemeConstantOverride("h_separation", 14);
        _stats.AddThemeConstantOverride("v_separation", 14);
        (_missionsValue, _missionsDetail, _missionsMeter) = Stat("Missions");
        (_goodiesValue, _goodiesDetail, _goodiesMeter) = Stat("Goodies");
        (_killsValue, _, ProgressBar killsMeter) = Stat("Kills", "all five categories");
        killsMeter.Visible = false;
        (_ranksValue, _ranksDetail, ProgressBar ranksMeter) = Stat("Ranks");
        ranksMeter.Visible = false;
        _stats.Resized += () => _stats.Columns = _stats.Size.X >= 820 ? 4 : 2;

        (_campaign, VBoxContainer campaignBody) = Build.Card("Your path through the campaign");
        content.Add(_campaign);
        Map = campaignBody.Add(new CampaignMap());
        HBoxContainer key = campaignBody.Add(Build.Row(14));
        foreach ((string kind, string text) in new[]
        {
            ("complete", "Complete, with your rank"), ("open", "Open to play"), ("closed", "Not reached yet"),
            ("route-taken", "Route you took"), ("route-not-taken", "Route not taken"),
        })
        {
            HBoxContainer item = key.Add(Build.Row(6));
            item.Add(new CampaignSwatch(kind));
            item.Add(Build.Text(text, "Muted", wrap: false));
        }
        _routeLine = campaignBody.Add(Build.Text("", "Faint"));

        _columns = content.Add(new GridContainer { Columns = 2 });
        _columns.AddThemeConstantOverride("h_separation", 14);
        _columns.AddThemeConstantOverride("v_separation", 14);
        _columns.Resized += () => _columns.Columns = _columns.Size.X >= 1000 ? 2 : 1;

        (PanelContainer missions, VBoxContainer missionBody) = Build.Card("Missions");
        missions.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        missions.SizeFlagsStretchRatio = 1.4f;
        // No attempts column: the game only ever zeroes that field (Career.cpp:99), so it counts nothing.
        Missions = missionBody.Add(Build.Table("Level", "Mission", "Status", "Rank"));
        Missions.CustomMinimumSize = new Vector2(0, 460);
        Missions.SetColumnCustomMinimumWidth(0, 70);
        Missions.SetColumnExpand(0, false);
        Missions.SetColumnExpandRatio(1, 3);
        _namesNote = missionBody.Add(Build.Text("", "Faint"));
        _columns.Add(missions);

        VBoxContainer side = _columns.Add(Build.Column(14));
        side.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        (PanelContainer goodies, VBoxContainer goodieBody) = Build.Card("Goodies");
        _goodieStrip = goodieBody.Add(new GridContainer { Columns = 30 });
        _goodieStrip.AddThemeConstantOverride("h_separation", 3);
        _goodieStrip.AddThemeConstantOverride("v_separation", 3);
        HBoxContainer legend = goodieBody.Add(Build.Row(8));
        foreach ((Color color, string text) in new[] { (Palette.ViewedBlue, "viewed"), (Palette.NewGold, "new"), (Palette.Muted, "hint"), (Palette.Raised, "locked") })
        {
            legend.Add(new ColorRect { Color = color, CustomMinimumSize = new Vector2(10, 10), SizeFlagsVertical = Control.SizeFlags.ShrinkCenter });
            legend.Add(Build.Text(text, "Faint", wrap: false));
        }
        Button openGoodies = goodieBody.Add(Build.Button("Open the Goodies gallery", "Link"));
        openGoodies.SizeFlagsHorizontal = Control.SizeFlags.ShrinkBegin;
        openGoodies.Pressed += () => app.Navigate("goodies");
        side.Add(goodies);
        (PanelContainer kills, VBoxContainer killBody) = Build.Card("Kills");
        _killRows = killBody.Add(Build.Column(8));
        side.Add(kills);
        ShowEmpty();
    }

    internal override Control Root { get; }
    internal override string Subtitle => _workspace.Session is SaveSession session
        ? System.IO.Path.GetFileNameWithoutExtension(session.Path) + " at a glance"
        : "Your career at a glance";
    internal Tree Missions { get; }
    internal CampaignMap Map { get; }
    internal string MissionsSummary => _missionsValue.Text;

    internal void ShowSession(SaveSession session)
    {
        CareerInspection career = session.Analysis;
        GameText? text = _game.Text;
        _empty.Visible = _choose.Root.Visible = false;
        _stats.Visible = _columns.Visible = true;
        CampaignGraph graph = CampaignGraph.From(career);
        Map.Show(graph, text);
        _campaign.Visible = graph.Nodes.Count > 0;
        MissionCensus missions = career.MissionCensus;
        _missionsValue.Text = $"{missions.Completed} / {missions.Used}";
        _missionsDetail.Text = "missions complete";
        _missionsMeter.Value = missions.Used == 0 ? 0 : missions.Completed / (double)missions.Used;
        int earned = career.GoodieCensus.New + career.GoodieCensus.Old;
        _goodiesValue.Text = $"{earned} / {career.GoodieCensus.Shown}";
        _goodiesDetail.Text = $"{career.GoodieCensus.New} new · {career.GoodieCensus.Hint} hints in the gallery";
        _goodiesMeter.Value = earned / (double)career.GoodieCensus.Shown;
        _killsValue.Text = career.Kills.Sum(value => (long)value).ToString("N0");
        IEnumerable<(string Letter, int Count)> ranks = career.Missions.Where(record => record.Completed)
            .GroupBy(record => record.RankLetter ?? "?").Select(group => (group.Key, group.Count()))
            .OrderBy(pair => "SABCDE?".IndexOf(pair.Key[0]));
        _ranksValue.Text = string.Join("  ", ranks.Select(pair => $"{pair.Letter}×{pair.Count}"));
        if (_ranksValue.Text.Length == 0) _ranksValue.Text = "—";
        _ranksDetail.Text = "by the game's own rank rule";

        Missions.Clear();
        TreeItem root = Missions.CreateItem();
        foreach (MissionRecord mission in career.Missions.Where(record => record.Used))
        {
            string name = text?.LevelName(mission.World) is string display && display.IndexOf(" - ", StringComparison.Ordinal) is int dash && dash > 0
                ? display[(dash + 3)..] : "—";
            TreeItem row = Build.TableRow(Missions, root, mission.World.ToString(), name, mission.Completed ? "Complete" : "Open",
                mission.RankLetter ?? "?");
            if (name == "—") row.SetCustomColor(1, Palette.Faint);
            row.SetCustomColor(2, mission.Completed ? Palette.Good : Palette.Muted);
            row.SetCustomColor(3, Palette.Accent);
        }
        _namesNote.Text = text is null
            ? "Mission names come from your game's own text file; choose your game folder on Home to show them."
            : $"Mission names come from your game's {text.Language} text; ranks use the game's own grading.";

        _goodieStrip.Clear();
        foreach (GoodieRecord goodie in career.Goodies.Where(record => record.Shown))
        {
            _goodieStrip.Add(new ColorRect
            {
                Color = goodie.State switch
                {
                    GoodieState.Old => Palette.ViewedBlue,
                    GoodieState.New => Palette.NewGold,
                    GoodieState.Hint => Palette.Muted,
                    GoodieState.Unknown => Palette.Bad,
                    _ => Palette.Raised,
                },
                CustomMinimumSize = new Vector2(9, 9), TooltipText = $"Goodie {goodie.Index:D3}: {GoodieFacts.StateName(goodie.State)}",
            });
        }

        _killRows.Clear();
        int most = Math.Max(1, career.Kills.Max());
        for (int category = 0; category < career.Kills.Count; category++)
        {
            HBoxContainer row = _killRows.Add(Build.Row(10));
            row.Add(Build.Text(CareerSave.CategoryNames[category], "Muted", wrap: false, width: 110));
            ProgressBar bar = row.Add(Build.Meter(career.Kills[category] / (double)most, accent: true));
            bar.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
            row.Add(Build.Text(career.Kills[category].ToString("N0"), "Mono", wrap: false, width: 72)).HorizontalAlignment = HorizontalAlignment.Right;
        }

        LinkCensus links = career.LinkCensus;
        _routeLine.Text = $"Hover a mission for its name. A route not taken is the game's own record of the path you did not " +
            $"follow, not damage. {links.Complete} routes open, {links.AlternateRoutes} not taken, {links.Locked} still closed" +
            (links.Unknown > 0 ? $", {links.Unknown} with values the companion does not recognise." : ".");
    }

    private (Label Value, Label Detail, ProgressBar Meter) Stat(string name, string detail = "")
    {
        (PanelContainer card, VBoxContainer body) = Build.Panel("Card", 4);
        card.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        body.Add(Build.Eyebrow(name));
        Label value = body.Add(Build.Text("—", "StatValue", wrap: false));
        Label description = body.Add(Build.Text(detail, "Muted", wrap: false));
        ProgressBar meter = body.Add(Build.Meter(0));
        _stats.Add(card);
        return (value, description, meter);
    }

    internal override void Refresh()
    {
        if (_workspace.Session is null) ShowEmpty();
    }

    private void ShowEmpty()
    {
        _empty.Visible = _choose.Root.Visible = true;
        _choose.Show();
        _stats.Visible = _columns.Visible = _campaign.Visible = false;
    }
}
