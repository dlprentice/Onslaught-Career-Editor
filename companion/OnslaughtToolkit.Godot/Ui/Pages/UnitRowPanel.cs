// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using System.Globalization;
using OnslaughtToolkit.Companion.Levels;
using NumericVector2 = System.Numerics.Vector2;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>A small, independently bindable control for arranging existing units as one undoable edit.</summary>
internal sealed partial class UnitRowPanel : VBoxContainer
{
    private LevelEditorModel? _model;
    private EditSession? _shownSession;
    private bool _listening;
    private readonly List<(int Row, PlacedObject Thing)> _entries = [];
    private readonly Control _gridOptions;

    internal ItemList Units { get; }
    internal LineEdit FirstX { get; }
    internal LineEdit FirstY { get; }
    internal LineEdit StepX { get; }
    internal LineEdit StepY { get; }
    internal OptionButton Layout { get; }
    internal LineEdit Columns { get; }
    internal LineEdit RowX { get; }
    internal LineEdit RowY { get; }
    internal bool GridOptionsVisible => _gridOptions.Visible;
    internal Button SelectAll { get; }
    internal Button ClearSelection { get; }
    internal Button UseFirstPosition { get; }
    internal Button Apply { get; }
    internal Label Note { get; }

    internal event Action<MoveOutcome>? ArrangementResult;

    internal UnitRowPanel()
    {
        AddThemeConstantOverride("separation", 8);
        this.Add(Build.Heading("Arrange units"));
        this.Add(Build.Text("Choose units below. They are placed in the order shown.", "Muted"));
        HBoxContainer layout = this.Add(Build.Row(8));
        layout.Add(Build.Text("Layout", wrap: false));
        Layout = layout.Add(new OptionButton { SizeFlagsHorizontal = SizeFlags.ExpandFill, TooltipText = "Choose a single row or a grid of rows." });
        Layout.AddItem("One row");
        Layout.AddItem("Grid");
        Layout.Select(0);
        Units = this.Add(new ItemList
        {
            SelectMode = ItemList.SelectModeEnum.Toggle,
            CustomMinimumSize = new Vector2(0, 130),
            SizeFlagsHorizontal = SizeFlags.ExpandFill,
            TooltipText = "Click units to select or deselect them.",
        });
        Units.MultiSelected += (_, _) => UpdateButtons();

        HBoxContainer selection = this.Add(Build.Row(8));
        SelectAll = selection.Add(Build.Button("Select all"));
        ClearSelection = selection.Add(Build.Button("Clear"));
        SelectAll.Pressed += () => { for (int i = 0; i < _entries.Count; i++) Units.Select(i, false); UpdateButtons(); };
        ClearSelection.Pressed += () => { Units.DeselectAll(); UpdateButtons(); };

        GridContainer fields = this.Add(new GridContainer { Columns = 2, SizeFlagsHorizontal = SizeFlags.ExpandFill });
        FirstX = Field(fields, "First unit X");
        FirstY = Field(fields, "First unit Y");
        StepX = Field(fields, "X spacing per unit");
        StepY = Field(fields, "Y spacing per unit");
        StepX.Text = "10";
        StepY.Text = "0";
        VBoxContainer grid = this.Add(Build.Column(6));
        _gridOptions = grid;
        grid.Visible = false;
        grid.Add(Build.Text("The next row starts at this X/Y offset from the row before it.", "Muted"));
        GridContainer gridFields = grid.Add(new GridContainer { Columns = 2, SizeFlagsHorizontal = SizeFlags.ExpandFill });
        Columns = Field(gridFields, "Units per row");
        Columns.MaxLength = 4;
        Columns.Text = "2";
        RowX = Field(gridFields, "Next row offset X");
        RowY = Field(gridFields, "Next row offset Y");
        RowX.Text = "0";
        RowY.Text = "10";
        Layout.ItemSelected += index => _gridOptions.Visible = index == 1;
        UseFirstPosition = this.Add(Build.Button("Use first selected unit's position"));
        UseFirstPosition.Pressed += SetFirstPosition;
        this.Add(Build.Text("Only positions change. Heights stay as they are; this does not stop AI or check for overlaps.", "Muted"));
        Apply = this.Add(Build.Button("Arrange selected units"));
        Apply.Pressed += Arrange;
        Note = this.Add(Build.Text("Open a level to choose units.", "Muted"));
        UpdateButtons();
    }

    private static LineEdit Field(GridContainer parent, string label)
    {
        parent.Add(Build.Text(label, wrap: false));
        return parent.Add(new LineEdit { PlaceholderText = "Enter a number", SizeFlagsHorizontal = SizeFlags.ExpandFill });
    }

    /// <summary>Set or clear the displayed model. Rebinding always clears selections from the previous model.</summary>
    internal void Bind(LevelEditorModel? model)
    {
        StopListening();
        _model = model;
        _shownSession = null;
        Units.DeselectAll();
        FirstX.Text = "";
        FirstY.Text = "";
        if (IsInsideTree()) StartListening();
        Refresh();
    }

    public override void _EnterTree()
    {
        StartListening();
        Refresh();
    }

    public override void _ExitTree() => StopListening();

    private void StartListening()
    {
        if (_model is not null && !_listening) { _model.Changed += Refresh; _listening = true; }
    }

    private void StopListening()
    {
        if (_model is not null && _listening) _model.Changed -= Refresh;
        _listening = false;
    }

    private void Refresh()
    {
        EditSession? session = _model?.Session;
        bool sameSession = session is not null && ReferenceEquals(_shownSession, session);
        HashSet<(int Row, PlacedObject Thing)> selected = sameSession
            ? Units.GetSelectedItems().Where(index => index >= 0 && index < _entries.Count).Select(index => _entries[index]).ToHashSet()
            : [];
        if (!sameSession) { FirstX.Text = ""; FirstY.Text = ""; }
        Units.Clear();
        _entries.Clear();
        _shownSession = session;
        if (_model is not null && session is not null)
            foreach (ObjectRow row in _model.Rows())
            {
                PlacedObject thing = session.Body.Things[row.Index];
                if (thing?.Init is null || !DuplicateObject.CanCopy(thing)) continue;
                int index = _entries.Count;
                _entries.Add((row.Index, thing));
                Units.AddItem($"{row.Label} (row {row.Index})");
                if (selected.Contains((row.Index, thing))) Units.Select(index, false);
            }
        Note.Text = session is null ? "Open a level to choose units." : _entries.Count == 0 ? "This level has no units to arrange." : "";
        UpdateButtons();
    }

    private void UpdateButtons()
    {
        bool any = Units.GetSelectedItems().Length > 0;
        SelectAll.Disabled = _entries.Count == 0;
        ClearSelection.Disabled = !any;
        UseFirstPosition.Disabled = !any;
        Apply.Disabled = !any;
    }

    private bool TrySelected(out int[] rows)
    {
        rows = [];
        EditSession? session = _model?.Session;
        int[] selected = Units.GetSelectedItems().Order().ToArray();
        if (session is null || !ReferenceEquals(session, _shownSession) || selected.Length == 0 ||
            selected.Any(index => index < 0 || index >= _entries.Count || _entries[index].Row >= session.Body.Things.Count ||
                                  !ReferenceEquals(session.Body.Things[_entries[index].Row], _entries[index].Thing) ||
                                  _entries[index].Thing.Init is null || !DuplicateObject.CanCopy(_entries[index].Thing)))
        {
            Units.DeselectAll();
            Refresh();
            Note.Text = "The selection changed. Choose the units again.";
            return false;
        }
        rows = selected.Select(index => _entries[index].Row).ToArray();
        return true;
    }

    private void SetFirstPosition()
    {
        if (!TrySelected(out int[] rows)) return;
        System.Numerics.Vector3 point = _model!.Session!.Body.Things[rows[0]].Init.Position;
        if (!float.IsFinite(point.X) || !float.IsFinite(point.Y)) { Note.Text = "That unit's position is not finite."; return; }
        FirstX.Text = CoordinateInput.Format(point.X);
        FirstY.Text = CoordinateInput.Format(point.Y);
        Note.Text = "First position copied from the selected unit.";
    }

    private void Arrange()
    {
        if (!TrySelected(out int[] rows)) return;
        CoordinateParse x = CoordinateInput.Parse(FirstX.Text), y = CoordinateInput.Parse(FirstY.Text),
            dx = CoordinateInput.Parse(StepX.Text), dy = CoordinateInput.Parse(StepY.Text);
        foreach ((string name, CoordinateParse value) in new[] { ("First unit X", x), ("First unit Y", y), ("X spacing", dx), ("Y spacing", dy) })
            if (!value.Ok) { Note.Text = $"{name}: {value.Problem}"; return; }
        MoveOutcome outcome;
        bool rounded = x.Rounded || y.Rounded || dx.Rounded || dy.Rounded;
        if (Layout.Selected == 0)
            outcome = _model!.ArrangeUnitsInRow(rows, new NumericVector2(x.Value, y.Value), new NumericVector2(dx.Value, dy.Value));
        else if (Layout.Selected == 1)
        {
            if (!int.TryParse(Columns.Text.Trim(' '), NumberStyles.None, CultureInfo.InvariantCulture, out int columns) || columns < 1 || columns > rows.Length)
            {
                Note.Text = $"Units per row must be a whole number from 1 to {rows.Length}.";
                return;
            }
            CoordinateParse rowX = CoordinateInput.Parse(RowX.Text), rowY = CoordinateInput.Parse(RowY.Text);
            foreach ((string name, CoordinateParse value) in new[] { ("Next row offset X", rowX), ("Next row offset Y", rowY) })
                if (!value.Ok) { Note.Text = $"{name}: {value.Problem}"; return; }
            rounded |= rowX.Rounded || rowY.Rounded;
            outcome = _model!.ArrangeUnitsInGrid(rows, columns, new NumericVector2(x.Value, y.Value),
                new NumericVector2(dx.Value, dy.Value), new NumericVector2(rowX.Value, rowY.Value));
        }
        else { Note.Text = "Choose a layout."; return; }
        if (outcome.Result == MoveResult.Moved && rounded)
            outcome = outcome with { Message = outcome.Message + " Some values were rounded to the stored precision." };
        Note.Text = outcome.Message;
        ArrangementResult?.Invoke(outcome);
    }
}
