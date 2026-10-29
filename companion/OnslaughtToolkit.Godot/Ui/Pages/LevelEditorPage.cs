// SPDX-License-Identifier: GPL-3.0-only
using System.Globalization;
using Godot;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// The Level editor: pick one of the game's levels, see the things its world places, move one by typing coordinates, and save the
/// result as an Onslaught CE mod. The game is only read; the only thing this page writes is a new mod folder, and only when the
/// player confirms. Everything it decides (what a coordinate means, what an edit changed, what a mod holds) is in
/// <see cref="LevelEditorModel"/>; this page lays it out and passes the player's words to it.
/// </summary>
internal sealed class LevelEditorPage : Page
{
    private const int PlaceholderId = 99999;

    /// <summary>The most characters of the saved mod's folder the notice shows (its middle is left out); the full path is on the Copy button and the tooltip.</summary>
    private const int SavedPathLength = 52;
    private readonly AppServices _services;
    private readonly Label _empty, _worldNote, _objectTitle, _objectDetail, _stock, _note, _hint, _summary, _warnings, _problemText, _savedText;
    private readonly PanelContainer _problemPanel, _savedPanel;
    private readonly Button _copy, _copyFolder;
    private readonly Control _body;
    private LevelEditorModel? _model;
    private string? _root;
    private int? _selected;
    private (string X, string Y, string Z) _shown = ("", "", "");
    private string _savedId = "", _savedFolder = "";
    private bool _noteIsRefusal;

    internal LevelEditorPage(AppServices services) : base("levels", "Level editor", "models")
    {
        _services = services;
        VBoxContainer page = Build.Column(10);
        page.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        Root = page;

        _empty = page.Add(Build.Text("Choose your game folder on Home to see its levels.", "Muted"));
        (_problemPanel, _problemText) = Build.Notice("", "FailureNotice");
        page.Add(_problemPanel);
        _problemPanel.Visible = false;

        HBoxContainer layout = Build.Row(16);
        layout.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        _body = page.Add(layout);

        // Left: the level, a search, what was saved, and the things the level's world places.
        VBoxContainer left = layout.Add(Build.Column(10));
        left.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        HBoxContainer toolbar = left.Add(Build.Row(10));
        Level = toolbar.Add(new OptionButton
        {
            TooltipText = "The game's levels. Opening one shows the things its world places.", CustomMinimumSize = new Vector2(150, 0),
            SizeFlagsHorizontal = Control.SizeFlags.ExpandFill, FitToLongestItem = false, TextOverrunBehavior = TextServer.OverrunBehavior.TrimEllipsis, ClipText = true,
        });
        Level.ItemSelected += index => PickLevel((int)Level.GetItemId((int)index));
        Undo = toolbar.Add(Build.Button("Undo", tooltip: "Take back the last move.", disabled: true));
        Redo = toolbar.Add(Build.Button("Redo", tooltip: "Make the move you took back.", disabled: true));
        Undo.Pressed += () => Step(undo: true);
        Redo.Pressed += () => Step(undo: false);
        Search = left.Add(new LineEdit
        {
            PlaceholderText = "Search by name, kind, script or row", ClearButtonEnabled = true, SizeFlagsHorizontal = Control.SizeFlags.ExpandFill,
            TooltipText = "Shows the objects whose row number, name, kind or script holds this text.",
        });
        Search.TextChanged += _ => RebuildTable();
        _worldNote = left.Add(Build.Text("", "Faint"));
        (_savedPanel, VBoxContainer savedInside) = Build.Panel("SuccessNotice", 6);
        left.Add(_savedPanel);
        _savedPanel.Visible = false;
        _savedText = savedInside.Add(Build.Text("", ""));
        _savedText.MouseFilter = Control.MouseFilterEnum.Pass;  // so that the tooltip, which has the full path, shows
        // The notice never grows with its path: the text shows the path's ends, and the buttons wrap in a narrow column.
        HFlowContainer savedActions = savedInside.Add(new HFlowContainer());
        savedActions.AddThemeConstantOverride("h_separation", 8);
        savedActions.AddThemeConstantOverride("v_separation", 6);
        _copy = savedActions.Add(Build.Button("Copy mods= line", tooltip: "Copies the line to put in ce.ini."));
        _copyFolder = savedActions.Add(Build.Button("Copy folder path", tooltip: "Copies the mod folder's full path."));
        _copy.Pressed += () =>
        {
            DisplayServer.ClipboardSet($"mods={_savedId}");
            _services.Status.Show($"Copied mods={_savedId}.", StatusKind.Info);
        };
        _copyFolder.Pressed += () =>
        {
            DisplayServer.ClipboardSet(_savedFolder);
            _services.Status.Show("Copied the mod folder's path.", StatusKind.Info);
        };
        Table = left.Add(Build.Table("Row", "Kind", "Name", "X", "Y", "Z"));
        Table.CustomMinimumSize = new Vector2(0, 150);
        foreach (int column in new[] { 0, 1, 3, 4, 5 }) Table.SetColumnExpand(column, false);
        Table.SetColumnCustomMinimumWidth(0, 46);
        Table.SetColumnCustomMinimumWidth(1, 108);
        Table.SetColumnExpandRatio(2, 1);
        foreach (int column in new[] { 3, 4, 5 }) Table.SetColumnCustomMinimumWidth(column, 86);
        // Titles line up with their cells: numbers on the right, words on the left.
        foreach (int column in new[] { 0, 3, 4, 5 }) Table.SetColumnTitleAlignment(column, HorizontalAlignment.Right);
        foreach (int column in new[] { 1, 2 }) Table.SetColumnTitleAlignment(column, HorizontalAlignment.Left);
        Table.ItemSelected += () => Select(Table.GetSelected());

        // Right: the selected object, and what the edit has changed so far.
        ScrollContainer side = layout.Add(new ScrollContainer
        {
            HorizontalScrollMode = ScrollContainer.ScrollMode.Disabled, CustomMinimumSize = new Vector2(370, 0), SizeFlagsVertical = Control.SizeFlags.ExpandFill,
        });
        MarginContainer gutter = side.Add(Build.Margin(0, 0, 12, 0));
        gutter.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        VBoxContainer right = gutter.Add(Build.Column(12));
        right.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        (PanelContainer inspector, VBoxContainer inside) = Build.Panel("Card", 8);
        right.Add(inspector);
        inside.Add(Build.Eyebrow("Selected object"));
        _objectTitle = inside.Add(Build.Text("Nothing selected", "Section", wrap: false, clip: true));
        _objectDetail = inside.Add(Build.Text("", "Muted"));
        GridContainer fields = inside.Add(new GridContainer { Columns = 2 });
        fields.AddThemeConstantOverride("h_separation", 10);
        fields.AddThemeConstantOverride("v_separation", 6);
        X = Axis(fields, "X");
        Y = Axis(fields, "Y");
        Z = Axis(fields, "Z");
        _stock = inside.Add(Build.Text("", "Faint"));
        HBoxContainer actions = inside.Add(Build.Row(10));
        Apply = actions.Add(Build.Button("Move", tooltip: "Move the object to these coordinates (Enter does the same).", disabled: true));
        Reset = actions.Add(Build.Button("Reset this object", tooltip: "Put the object back where the level has it.", disabled: true));
        Apply.Pressed += () => ApplyFields(explicitly: true);
        Reset.Pressed += ResetSelected;
        _note = inside.Add(Build.Text("", "Muted"));
        _hint = inside.Add(Build.Text("", "Faint"));

        (PanelContainer changes, VBoxContainer changesBody) = Build.Panel("Card", 8);
        right.Add(changes);
        changesBody.Add(Build.Eyebrow("Your changes"));
        _summary = changesBody.Add(Build.Text("", "Strong"));
        _warnings = changesBody.Add(Build.Text("", "Warn"));
        Save = changesBody.Add(Build.Button("Save as mod…", "Primary", "Save the changes as an Onslaught CE mod: a new folder. Nothing in your game changes.", disabled: true));
        changesBody.Add(Build.Text("A saved mod is a new folder; the game's own files are never touched. Onslaught CE loads a level's world from a mod " +
            "only on Linux for now, and only if its README's Mods section lists world files as something a mod may add.", "Faint"));
        SaveDialog = new SaveAsModDialog(services.Popups);
        services.Popups.AddChild(SaveDialog);
        Save.Pressed += BeginSave;
        SaveDialog.Confirmed += () => SaveNow();

        services.Game.Changed += Refresh;
        Refresh();
    }

    internal override Control Root { get; }

    internal override string Subtitle => _model?.Level is int level && _model.Session is { } session
        ? $"Level {level} · {Build.Count(session.Body.Things.Count, "object")}"
        : "Move things in the game's levels, and save the result as an Onslaught CE mod";

    internal OptionButton Level { get; }
    internal LineEdit Search { get; }
    internal Tree Table { get; }
    internal LineEdit X { get; }
    internal LineEdit Y { get; }
    internal LineEdit Z { get; }
    internal Button Undo { get; }
    internal Button Redo { get; }
    internal Button Apply { get; }
    internal Button Reset { get; }
    internal Button Save { get; }
    internal SaveAsModDialog SaveDialog { get; }
    internal LevelEditorModel? Model => _model;
    internal string Note => _note.Text;
    internal string Hint => _hint.Text;
    internal string Summary => _summary.Text;
    internal string Warnings => _warnings.Text;
    internal string Problem => _problemPanel.Visible ? _problemText.Text : "";
    internal string WorldNote => _worldNote.Text;
    internal string SavedText => _savedPanel.Visible ? _savedText.Text : "";
    internal bool CopyVisible => _savedPanel.Visible && _copy.Visible && _copyFolder.Visible;

    /// <summary>The full path of the mod folder the last save made (what Copy folder path puts on the clipboard), or empty.</summary>
    internal string SavedFolder => _savedPanel.Visible && _copyFolder.Visible ? _savedFolder : "";

    /// <summary>What the notice says when the pointer rests on it: the full path and what the mod holds.</summary>
    internal string SavedTooltip => _savedText.TooltipText;
    internal bool EmptyVisible => _empty.Visible;
    internal string? SelectedName => _selected is int row ? _model?.Row(row)?.Label : null;

    /// <summary>Whether the open level holds moves that no Save as mod has written: what leaving the level, the game or the companion would drop.</summary>
    internal bool HasChanges => _model?.HasUnsavedChanges ?? false;

    /// <summary>How many objects those moves cover.</summary>
    internal int ChangeCount => _model?.UnsavedChangeCount ?? 0;

    private LineEdit Axis(GridContainer grid, string label)
    {
        grid.Add(Build.Text(label, "Strong", wrap: false));
        LineEdit field = grid.Add(new LineEdit
        {
            ThemeTypeVariation = "MonoField", SizeFlagsHorizontal = Control.SizeFlags.ExpandFill, Editable = false, SelectAllOnFocus = true,
            TooltipText = $"The object's {label} coordinate. Press Enter to move it.",
        });
        field.TextSubmitted += _ => ApplyFields(explicitly: true);
        field.FocusExited += () => ApplyFields(explicitly: false);
        return field;
    }

    internal override void Refresh()
    {
        if (_services.Game.Busy) return;
        string? root = _services.Game.Folder?.AssetRoot;
        // The same game: keep the edit in hand, and list its levels again (a quick listing of one folder). Another game (or none): start over.
        if (_model is null || !string.Equals(root, _root, StringComparison.Ordinal))
        {
            _root = root;
            _selected = null;
            _model = root is null ? null : LevelEditorModel.ForGame(root);
            if (_model is not null) _model.Changed += OnModelChanged;
            _savedPanel.Visible = _problemPanel.Visible = false;
            _worldNote.Text = "";
            FillLevels();
            RebuildTable();
        }
        else if (root is not null && _model.Rescan(root))
        {
            FillLevels();
        }
        // A game with levels opens one at once, its training level if it has one, rather than showing an empty table.
        if (_model is { Level: null, Levels.Count: > 0 } fresh) OpenLevel(fresh.Levels.Any(file => file.Level == 100) ? 100 : fresh.Levels[0].Level);
        UpdateEmpty();
        UpdateInspector(clearNote: false);
        UpdateChanges();
        HeaderChanged?.Invoke();
    }

    private void UpdateEmpty()
    {
        string? root = _services.Game.Folder?.AssetRoot;
        _empty.Text = root is null ? "Choose your game folder on Home to see its levels." : "No level archives were found in your game's data folder.";
        _empty.Visible = root is null || _model is null || _model.Levels.Count == 0;
        _body.Visible = !_empty.Visible;
    }

    private void FillLevels()
    {
        Level.Clear();
        Level.AddItem("Choose a level…", PlaceholderId);
        Level.SetItemDisabled(0, true);
        GameText? text = _services.Game.Text;
        foreach (LevelArchiveFile file in _model?.Levels ?? [])
        {
            string? name = text?.LevelName((uint)file.Level);
            Level.AddItem(name is null ? $"{file.Level:000}" : $"{file.Level:000} · {name}", file.Level);
        }
        Level.Select(0);
        for (int i = 0; i < Level.ItemCount; i++)
            if (_model?.Level is int open && _model.Session is not null && Level.GetItemId(i) == open) Level.Select(i);
    }

    private void ShowInPicker(int level)
    {
        for (int i = 0; i < Level.ItemCount; i++)
            if (Level.GetItemId(i) == level) Level.Select(i);
    }

    /// <summary>
    /// The player chose a level in the picker, the open one again included (it is read afresh). It asks first when the open level holds
    /// moves that are not saved; the picker keeps showing the open level while the question is up, and the chosen one when the player agrees.
    /// </summary>
    internal void PickLevel(int level)
    {
        if (_model?.Level is int open && HasChanges)
        {
            int moved = ChangeCount;
            ShowInPicker(open);
            _services.AskToDiscard($"{Build.Count(moved, "object")} moved on level {open} {(moved == 1 ? "is" : "are")} not saved. Open level {level} and discard {(moved == 1 ? "it" : "them")}?",
                "Discard and open", () => OpenLevel(level));
            return;
        }
        OpenLevel(level);
    }

    /// <summary>Opens a level's own world, dropping what was open (the picker asks first when that holds unsaved moves). Returns false, with the reason shown, if it cannot be edited.</summary>
    internal bool OpenLevel(int level)
    {
        if (_model is null) return false;
        _selected = null;
        _savedPanel.Visible = false;
        ShowNote("", refusal: false);
        bool opened = _model.Open(level);
        ShowInPicker(level);
        RebuildTable();
        UpdateInspector(clearNote: true);
        UpdateChanges();
        UpdateEmpty();
        HeaderChanged?.Invoke();
        return opened;
    }

    private void OnModelChanged()
    {
        _problemPanel.Visible = _model?.Problem is not null;
        _problemText.Text = _model?.Problem ?? "";
        _worldNote.Text = _model?.BaseLevel is int baseLevel ? $"This level also loads the base world of level {baseLevel}. This editor does not change it." : "";
        RebuildTable();
        UpdateInspector(clearNote: false);
        UpdateChanges();
    }

    private void RebuildTable()
    {
        Table.Clear();
        TreeItem root = Table.CreateItem();
        IReadOnlyList<ObjectRow> rows = _model?.Rows(Search.Text) ?? [];
        TreeItem? selected = null;
        foreach (ObjectRow row in rows)
        {
            bool named = row.Name.Length > 0 || row.Definition.Length > 0;
            TreeItem item = Build.TableRow(Table, root, row.Index.ToString(CultureInfo.InvariantCulture), row.Kind, named ? row.Label : "—",
                CoordinateInput.Format(row.Position.X), CoordinateInput.Format(row.Position.Y), CoordinateInput.Format(row.Position.Z));
            item.SetMetadata(0, row.Index);
            foreach (int column in new[] { 0, 3, 4, 5 }) item.SetTextAlignment(column, HorizontalAlignment.Right);
            if (!named) item.SetCustomColor(2, Palette.Faint);
            if (row.Changed)
                for (int column = 0; column < 6; column++) item.SetCustomColor(column, Palette.Accent);
            if (row.Index == _selected) selected = item;
        }
        selected?.Select(0);
        if (selected is not null) Table.ScrollToItem(selected);
    }

    /// <summary>Selects the table row <paramref name="index"/>, if the table shows it. Returns false if it does not.</summary>
    internal bool SelectRow(int index)
    {
        for (TreeItem? item = Table.GetRoot()?.GetFirstChild(); item is not null; item = item.GetNext())
        {
            if (item.GetMetadata(0).AsInt32() != index) continue;
            item.Select(0);
            Table.ScrollToItem(item);
            return Select(item);
        }
        return false;
    }

    internal bool Select(TreeItem? item)
    {
        if (item is null || _model?.Row(item.GetMetadata(0).AsInt32()) is not { } row) return false;
        if (_selected == row.Index) return true;
        _selected = row.Index;
        UpdateInspector(clearNote: true);
        return true;
    }

    private void UpdateInspector(bool clearNote)
    {
        ObjectRow? row = _selected is int index ? _model?.Row(index) : null;
        if (clearNote) ShowNote("", refusal: false);
        foreach (LineEdit field in new[] { X, Y, Z }) field.Editable = row is not null;
        Apply.Disabled = row is null;
        Reset.Disabled = row is not { Changed: true };
        if (row is null)
        {
            _objectTitle.Text = "Nothing selected";
            _objectDetail.Text = _model?.Session is null ? "Choose a level, then an object in the table." : "Choose an object in the table.";
            _shown = ("", "", "");
            X.Text = Y.Text = Z.Text = "";
            _stock.Text = "";
            _hint.Text = "";
            _hint.Visible = false;
            return;
        }
        _objectTitle.Text = row.Label;
        _objectDetail.Text = $"{row.Kind} · row {row.Index}" + (row.Name.Length > 0 && row.Definition.Length > 0 ? $" · {row.Definition}" : "");
        _shown = LevelEditorModel.Shown(row.Position);
        (X.Text, Y.Text, Z.Text) = _shown;
        (string sx, string sy, string sz) = LevelEditorModel.Shown(row.Stock);
        _stock.Text = row.Changed ? $"In the level: {sx}, {sy}, {sz}" : "Where the level has it.";
        bool negativeZero = new[] { _shown.X, _shown.Y, _shown.Z }.Contains("-0");
        _hint.Text = "Type a number such as 276.49 or -12.1 and press Enter." +
            (negativeZero ? " A stored -0 is shown as -0 and kept as it is unless you type another value." : "");
        _hint.Visible = true;
    }

    private void UpdateChanges()
    {
        EditSession? session = _model?.Session;
        Undo.Disabled = session is not { CanUndo: true };
        Redo.Disabled = session is not { CanRedo: true };
        Undo.TooltipText = session?.UndoDescription is { } undo ? $"Take back: {undo}." : "Take back the last move.";
        Redo.TooltipText = session?.RedoDescription is { } redo ? $"Make again: {redo}." : "Make the move you took back.";
        if (session is null)
        {
            _summary.Text = "";
            _warnings.Text = "";
            _warnings.Visible = false;
            Save.Disabled = true;
            Save.TooltipText = "Choose a level first.";
            return;
        }
        string? summary = _model!.ChangeSummary();
        _summary.Text = summary ?? "No changes yet. Choose an object and type new coordinates.";
        ValidationReport report = session.Validate();
        List<string> lines = [];
        if (summary is not null) lines.AddRange(report.Errors.Select(finding => "Cannot save: " + finding.Message));
        lines.AddRange(report.Warnings.Select(finding => "Take care: " + finding.Message));
        _warnings.Text = string.Join("\n", lines);
        _warnings.Visible = lines.Count > 0;
        Save.Disabled = !report.CanSave;
        Save.TooltipText = report.CanSave ? "Save the changes as an Onslaught CE mod: a new folder. Nothing in your game changes."
            : report.Errors[0].Message;
    }

    /// <summary>Moves the selected object to the coordinates in the fields. Returns what happened, or null if nothing is selected.</summary>
    internal MoveOutcome? ApplyFields(bool explicitly)
    {
        if (_model is null || _selected is not int row) return null;
        // A field left as it is (still the text shown for the stored value) is not read again, so leaving the fields moves nothing.
        if (!explicitly && (X.Text, Y.Text, Z.Text) == _shown)
        {
            if (_noteIsRefusal) ShowNote("", refusal: false);  // the fields were put right: the refusal no longer applies
            return null;
        }
        MoveOutcome outcome = _model.Move(row, X.Text, Y.Text, Z.Text);
        // Pressing Move first takes the focus from the field (which applies what was typed) and then presses the button: the second, which
        // finds nothing to change, must not wipe out the first one's note.
        if (outcome.Result != MoveResult.Unchanged || (explicitly && _note.Text.Length == 0)) ShowNote(outcome.Message, outcome.Result == MoveResult.Refused);
        if (outcome.Result == MoveResult.Unchanged) UpdateInspector(clearNote: false);
        return outcome;
    }

    private void ResetSelected()
    {
        if (_model is null || _selected is not int row) return;
        MoveOutcome outcome = _model.Reset(row);
        ShowNote(outcome.Message, outcome.Result == MoveResult.Refused);
    }

    private void ShowNote(string message, bool refusal)
    {
        _note.Text = message;
        _note.Visible = message.Length > 0;
        _note.ThemeTypeVariation = refusal ? "Bad" : "Muted";
        _noteIsRefusal = refusal && message.Length > 0;
    }

    private void Step(bool undo)
    {
        EditSession? session = _model?.Session;
        if (session is null) return;
        string? what = undo ? session.UndoDescription : session.RedoDescription;
        bool done = undo ? session.Undo() : session.Redo();
        ShowNote(done ? (undo ? $"Took back: {what}." : $"Made again: {what}.") : "", refusal: false);
    }

    // ---- saving ------------------------------------------------------------------------------------------------------------------
    private string DefaultDestination() => _services.Game.CeUserFolder.Length > 0 ? Path.Combine(_services.Game.CeUserFolder, "mods") : "";

    private void BeginSave()
    {
        if (_model?.Level is not int level || _model.Session is null) return;
        SaveDialog.Begin(level, DefaultDestination());
        SaveDialog.PopupCentered();
    }

    /// <summary>The folders a mod is never saved in: the game, its original install, CE's package and the companion's backups.</summary>
    private IEnumerable<string?> ProtectedFolders() =>
    [
        _services.Game.Original?.Root, _services.Game.Folder?.AssetRoot, _services.Game.CePackageRoot, _services.Game.CeOriginalRoot, _services.Backups.Folder,
    ];

    /// <summary>Saves the edit with the words in the dialog. Returns what happened, with the reason shown if it did not save.</summary>
    internal SaveOutcome SaveNow()
    {
        if (_model is null) return new SaveOutcome(null, "Choose a level first.");
        ModInfo info = SaveDialog.Info;
        SaveOutcome outcome = _model.SaveAsMod(SaveDialog.Destination.Text.Trim(), info, ProtectedFolders());
        _savedPanel.Visible = true;
        _savedPanel.ThemeTypeVariation = outcome.Ok ? "SuccessNotice" : "FailureNotice";
        _copy.Visible = _copyFolder.Visible = outcome.Ok;
        if (outcome.Ok)
        {
            _savedId = info.Id;
            _savedFolder = outcome.Staged!.Root;
            _savedText.Text = $"Saved the mod to {PathText.Elide(_savedFolder, SavedPathLength)}.\n" +
                $"To play it, close Onslaught CE and add this line to ce.ini:  mods={info.Id}";
            _savedText.TooltipText = $"{_savedFolder}\nIt holds {Build.Count(outcome.Staged.Files.Count + 1, "file")}: mod.json and {string.Join(", ", outcome.Staged.Files.Select(file => file.Path))}.";
        }
        else
        {
            _savedFolder = "";
            _savedText.Text = outcome.Message;
            _savedText.TooltipText = outcome.Message;
        }
        _services.Status.Show(outcome.Ok ? $"Saved the mod {info.Name}." : outcome.Message, outcome.Ok ? StatusKind.Success : StatusKind.Failure);
        return outcome;
    }
}
