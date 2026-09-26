// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// Every displayable Goodie of the open career in the game's own colours, with its unlock rule and
/// how far the evidence for that rule goes. Read-only; a change is prepared on Edit a copy.
/// </summary>
internal sealed class GoodiesPage : Page
{
    private static readonly (string Label, Func<GoodieState, bool> Matches)[] Filters =
    [
        ("All", _ => true),
        ("Earned", state => state is GoodieState.New or GoodieState.Old),
        ("New", state => state == GoodieState.New),
        ("Hints", state => state == GoodieState.Hint),
        ("Locked", state => state is GoodieState.Locked or GoodieState.Unknown),
    ];

    private readonly CareerWorkspace _workspace;
    private readonly GameLibrary _game;
    private readonly Action<int> _changeInCopy;
    private readonly Label _empty, _summary;
    private readonly HFlowContainer _grid;
    private readonly List<Button> _cells = [];
    private readonly ButtonGroup _selection = new();
    private readonly Label _detailTitle, _detailName, _detailState, _detailRule, _detailEvidence, _detailRaw;
    private readonly PanelContainer _detail;
    private readonly List<Button> _filterButtons = [];
    private int _filter;

    internal GoodiesPage(CareerWorkspace workspace, GameLibrary game, Action<int> changeInCopy) : base("goodies", "Goodies")
    {
        (_workspace, _game, _changeInCopy) = (workspace, game, changeInCopy);
        HBoxContainer layout = Build.Row(16);
        layout.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        Root = layout;

        (ScrollContainer scroll, VBoxContainer left) = Build.Scroller(12);
        scroll.SizeFlagsStretchRatio = 2.2f;
        layout.Add(scroll);
        _empty = left.Add(Build.Text("Open a career to see its Goodies.", "Muted"));
        _summary = left.Add(Build.Text("", "Strong"));
        HBoxContainer filters = left.Add(Build.Row(8));
        for (int index = 0; index < Filters.Length; index++)
        {
            int chosen = index;
            Button filter = filters.Add(Build.Button(Filters[index].Label, index == 0 ? "Primary" : ""));
            filter.Pressed += () => ApplyFilter(chosen);
            _filterButtons.Add(filter);
        }
        _grid = left.Add(new HFlowContainer());
        _grid.AddThemeConstantOverride("h_separation", 5);
        _grid.AddThemeConstantOverride("v_separation", 5);
        for (int index = 0; index < CareerSave.DisplayableGoodies; index++)
        {
            int goodie = index;
            Button cell = _grid.Add(new Button
            {
                Text = index.ToString("D3"), ToggleMode = true, ButtonGroup = _selection, CustomMinimumSize = new Vector2(38, 30),
                ThemeTypeVariation = "GoodieLocked", FocusMode = Control.FocusModeEnum.All,
            });
            cell.Pressed += () => Select(goodie);
            _cells.Add(cell);
        }

        (_detail, VBoxContainer detail) = Build.Panel("Card", 8);
        _detail.CustomMinimumSize = new Vector2(330, 0);
        _detail.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        _detail.SizeFlagsVertical = Control.SizeFlags.ShrinkBegin;
        layout.Add(_detail);
        _detailTitle = detail.Add(Build.Heading("Goodie"));
        _detailName = detail.Add(Build.Text("", "Strong"));
        _detailState = detail.Add(Build.Text("", "Data"));
        detail.Add(Build.Eyebrow("How the game unlocks it"));
        _detailRule = detail.Add(Build.Text(""));
        _detailEvidence = detail.Add(Build.Text("", "Muted"));
        _detailRaw = detail.Add(Build.Text("", "MonoMuted"));
        ChangeInCopy = detail.Add(Build.Button("Change its state in a copy…", tooltip: "Adds this Goodie to Edit a copy."));
        ChangeInCopy.SizeFlagsHorizontal = Control.SizeFlags.ShrinkBegin;
        ChangeInCopy.Pressed += () => _changeInCopy(Selected);
        ShowEmpty();
    }

    internal override Control Root { get; }
    internal override string Subtitle => "Unlockables in the game's own colours: gold is new, blue is viewed";
    internal IReadOnlyList<Button> Cells => _cells;
    internal int Selected { get; private set; } = -1;
    internal string DetailEvidence => _detailEvidence.Text;
    internal string DetailRule => _detailRule.Text;
    internal Button ChangeInCopy { get; }

    internal void ShowSession(SaveSession session)
    {
        CareerInspection career = session.Analysis;
        _empty.Visible = false;
        _grid.Visible = _detail.Visible = _summary.Visible = true;
        foreach (Button filter in _filterButtons) filter.Visible = true;
        GoodieCensus census = career.GoodieCensus;
        _summary.Text = $"{census.New + census.Old} of {census.Displayable} earned  ·  {census.New} new  ·  {census.Old} viewed  ·  " +
            $"{census.Hint} hints  ·  {census.Locked} locked" + (census.Unknown > 0 ? $"  ·  {census.Unknown} unknown values" : "");
        for (int index = 0; index < _cells.Count; index++)
        {
            GoodieState state = career.Goodies[index].State;
            _cells[index].ThemeTypeVariation = state switch
            {
                GoodieState.New => "GoodieNew",
                GoodieState.Old => "GoodieViewed",
                GoodieState.Hint => "GoodieHint",
                GoodieState.Unknown => "GoodieUnknown",
                _ => "GoodieLocked",
            };
            _cells[index].TooltipText = $"Goodie {index:D3}: {GoodieFacts.StateName(state)}" +
                (_game.Text?.GoodieTitle(index) is string title ? $"\n{title}" : "");
        }
        ApplyFilter(_filter);
        Select(Selected >= 0 ? Selected : 0);
    }

    internal void Select(int index)
    {
        if (_workspace.Session is not SaveSession session || index < 0 || index >= _cells.Count) return;
        Selected = index;
        // Setting a toggle without a signal does not release the rest of its group, so do it here.
        for (int cell = 0; cell < _cells.Count; cell++) _cells[cell].SetPressedNoSignal(cell == index);
        GoodieRecord goodie = session.Analysis.Goodies[index];
        _detailTitle.Text = $"GOODIE {index:D3}";
        _detailName.Text = _game.Text?.GoodieTitle(index) ?? (_game.Text is null
            ? "Titles come from your game's own text; choose your game folder on Home."
            : "The game's text names no title for this Goodie.");
        _detailName.ThemeTypeVariation = _game.Text?.GoodieTitle(index) is null ? "Faint" : "Strong";
        _detailState.Text = GoodieFacts.StateName(goodie.State);
        _detailRule.Text = GoodieFacts.Rule(index);
        _detailEvidence.Text = GoodieFacts.Describe(GoodieFacts.Evidence(index));
        _detailRaw.Text = $"stored 0x{goodie.RawState:X8} at 0x{goodie.Offset:X4}";
    }

    private void ApplyFilter(int filter)
    {
        _filter = filter;
        for (int index = 0; index < _filterButtons.Count; index++)
            _filterButtons[index].ThemeTypeVariation = index == filter ? "Primary" : "";
        if (_workspace.Session is not SaveSession session) return;
        IReadOnlyList<GoodieRecord> goodies = session.Analysis.Goodies;
        for (int index = 0; index < _cells.Count; index++)
            _cells[index].Visible = Filters[filter].Matches(goodies[index].State);
    }

    private void ShowEmpty()
    {
        _empty.Visible = true;
        _grid.Visible = _detail.Visible = _summary.Visible = false;
        foreach (Button filter in _filterButtons) filter.Visible = false;
    }
}
