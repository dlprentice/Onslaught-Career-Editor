// SPDX-License-Identifier: GPL-3.0-only
using System.Globalization;
using Godot;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// The Level editor: pick one of the game's levels, see the things its world places and the scripts it runs (read only), move a thing by
/// typing coordinates, and save the result as an Onslaught CE mod. The game is only read; the only thing this page writes is a new mod
/// folder, and only when the player confirms. Everything it decides (what a coordinate means, what an edit changed, what a mod holds) is in
/// <see cref="LevelEditorModel"/>; this page lays it out and passes the player's words to it.
/// </summary>
internal sealed class LevelEditorPage : Page
{
    private const int PlaceholderId = 99999;

    /// <summary>The most characters of the saved mod's folder the notice shows (its middle is left out); the full path is on the Copy button and the tooltip.</summary>
    private const int SavedPathLength = 52;

    /// <summary>The width of the left column from which the table and the map sit side by side; narrower, the map is below the table.</summary>
    private const float SideBySideFrom = 880;

    // Short, since the line shares its row with two switches in the narrowest window; the tooltips say the rest.
    private const string ObjectSearchHint = "Name, kind, script, row", ScriptSearchHint = "Script, event, function";
    private readonly AppServices _services;
    private readonly Label _empty, _worldNote, _objectTitle, _objectDetail, _stock, _note, _hint, _summary, _draftNote, _warnings, _problemText, _savedText, _playNote, _filterNote;
    private readonly PanelContainer _problemPanel, _savedPanel;
    private readonly SplitContainer _split;
    private readonly ScrollContainer _side;
    private readonly Button _copy, _copyFolder;
    private readonly Control _body;
    private readonly Control _mapPanel;
    private readonly ScriptsPanel _scripts;
    private readonly PanelContainer _scriptCard;
    private readonly Label _scriptTitle, _scriptWhere, _scriptHandles, _scriptCalls, _scriptRuns, _scriptSource, _scriptNamesTitle, _pathText;
    private readonly HFlowContainer _scriptUses, _objectScripts, _scriptNames, _objectPaths;
    private IReadOnlyList<ScriptEntry>? _shownScripts;
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
        // The search shares its line with the Map switch: the toolbar above has no width to spare in the smallest window.
        HBoxContainer searchRow = left.Add(Build.Row(10));
        Search = searchRow.Add(new LineEdit
        {
            PlaceholderText = ObjectSearchHint, ClearButtonEnabled = true, SizeFlagsHorizontal = Control.SizeFlags.ExpandFill,
            TooltipText = "Shows the objects whose row number, name, kind or script holds this text.",
        });
        MapToggle = searchRow.Add(new CheckButton { Text = "Map", ButtonPressed = true, TooltipText = "Show or hide the map next to the table." });
        MapToggle.Toggled += on => _mapPanel!.Visible = on;
        ScriptsToggle = searchRow.Add(new CheckButton { Text = "Scripts", TooltipText = "Show the level's compiled scripts and their source, read only, instead of the objects." });
        ScriptsToggle.Toggled += ShowScripts;
        Search.TextChanged += _ =>
        {
            if (_scripts!.Visible) _scripts.Filter(Search.Text);
            else RebuildTable();
        };
        _worldNote = left.Add(Build.Text("", "Faint"));
        _filterNote = left.Add(Build.Text("", "Faint"));
        _filterNote.Visible = false;
        // The table and the map share the column: side by side when it is wide, the map under the table (which keeps its columns) when it is not.
        _split = left.Add(new SplitContainer { SizeFlagsVertical = Control.SizeFlags.ExpandFill, Vertical = true });
        _split.Resized += () =>
        {
            _split.Vertical = _split.Size.X < SideBySideFrom;
            _mapPanel!.SizeFlagsStretchRatio = _split.Vertical ? 1.6f : 1.25f;  // the map is what the room is for
        };
        Table = _split.Add(Build.Table("Row", "Kind", "Name", "X", "Y", "Z"));
        Table.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        Table.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        Table.SizeFlagsStretchRatio = 1f;
        Table.CustomMinimumSize = new Vector2(280, 150);
        VBoxContainer mapColumn = _split.Add(Build.Column(6));
        mapColumn.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        mapColumn.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        mapColumn.SizeFlagsStretchRatio = 1.6f;
        _mapPanel = mapColumn;
        Map = mapColumn.Add(new LevelMap { SizeFlagsVertical = Control.SizeFlags.ExpandFill, SizeFlagsHorizontal = Control.SizeFlags.ExpandFill });
        mapColumn.Add(Build.Text("Wheel zooms · drag the background to pan · click or drag a mark to select or move it (Esc cancels) · Home fits the level", "Faint"));
        HBoxContainer pathBar = mapColumn.Add(Build.Row(8));
        PathsToggle = pathBar.Add(new CheckButton { Text = "Paths", TooltipText = "Draw every waypoint path of the level, faintly, through the objects it names." });
        PathsToggle.Toggled += on => Map.ShowAllPaths = on;
        _pathText = pathBar.Add(Build.Text("", "Muted", wrap: false, clip: true));
        _pathText.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        _pathText.MouseFilter = Control.MouseFilterEnum.Pass;  // so that the tooltip, which has the whole text when it is cut short, shows
        HidePath = pathBar.Add(Build.Button("Hide path", tooltip: "Stop highlighting the path."));
        HidePath.Disabled = true;  // always in the row, so that the map above it keeps its height when a path is shown
        HidePath.Pressed += () => HighlightPath(null);
        Map.RowPicked += row => SelectIndex(row);
        Map.MoveRequested += (row, x, y) => Dragged(row, x, y);
        foreach (int column in new[] { 0, 1, 3, 4, 5 }) Table.SetColumnExpand(column, false);
        Table.SetColumnCustomMinimumWidth(0, 46);
        Table.SetColumnCustomMinimumWidth(1, 108);
        Table.SetColumnExpandRatio(2, 1);
        foreach (int column in new[] { 3, 4, 5 }) Table.SetColumnCustomMinimumWidth(column, 86);
        // Titles line up with their cells: numbers on the right, words on the left.
        foreach (int column in new[] { 0, 3, 4, 5 }) Table.SetColumnTitleAlignment(column, HorizontalAlignment.Right);
        foreach (int column in new[] { 1, 2 }) Table.SetColumnTitleAlignment(column, HorizontalAlignment.Left);
        Table.ItemSelected += () => Select(Table.GetSelected());

        // The scripts take the table's and the map's place when the Scripts switch is on.
        _scripts = left.Add(new ScriptsPanel { Visible = false });
        _scripts.Selected += OnScriptSelected;

        // Right: the selected object, and what the edit has changed so far.
        ScrollContainer side = _side = layout.Add(new ScrollContainer
        {
            HorizontalScrollMode = ScrollContainer.ScrollMode.Disabled, CustomMinimumSize = new Vector2(370, 0), SizeFlagsVertical = Control.SizeFlags.ExpandFill,
        });
        MarginContainer gutter = side.Add(Build.Margin(0, 0, 12, 0));
        gutter.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        VBoxContainer right = gutter.Add(Build.Column(12));
        right.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        (PanelContainer scriptCard, VBoxContainer scriptInside) = Build.Panel("Card", 8);
        _scriptCard = right.Add(scriptCard);
        _scriptCard.Visible = false;
        scriptInside.Add(Build.Eyebrow("Selected script"));
        _scriptTitle = scriptInside.Add(Build.Text("Nothing selected", "Section", wrap: false, clip: true));
        _scriptWhere = scriptInside.Add(Build.Text("", "Muted"));
        _scriptHandles = scriptInside.Add(Build.Text("", ""));
        _scriptCalls = scriptInside.Add(Build.Text("", "Muted"));
        _scriptRuns = scriptInside.Add(Build.Text("", "Strong"));
        _scriptUses = scriptInside.Add(new HFlowContainer());
        _scriptUses.AddThemeConstantOverride("h_separation", 6);
        _scriptUses.AddThemeConstantOverride("v_separation", 6);
        _scriptSource = scriptInside.Add(Build.Text("", "Faint"));
        _scriptEditActions = scriptInside.Add(new HFlowContainer());
        _scriptEditActions.AddThemeConstantOverride("h_separation", 8);
        _scriptEditActions.AddThemeConstantOverride("v_separation", 6);
        _scriptEditActions.Visible = false;
        EditSource = _scriptEditActions.Add(Build.Button("Edit source", tooltip: "Type in the script's source. Nothing in the level changes until you compile and use it."));
        EditSource.ToggleMode = true;
        CompileScriptButton = _scriptEditActions.Add(Build.Button("Compile and use", "Primary", "Compile the source and, if it compiles, make the level use the new script. Undo takes it back.", disabled: true));
        ShippedScriptButton = _scriptEditActions.Add(Build.Button("Put the shipped script back", tooltip: "Make the level use the script it came with.", disabled: true));
        _scriptEditNote = scriptInside.Add(Build.Text("", "Muted"));
        _scriptEditWarnings = scriptInside.Add(Build.Text("", "Warn"));
        _scriptEditWarnings.Visible = false;
        _scriptNamesTitle = scriptInside.Add(Build.Text("", "Strong"));
        _scriptNamesTitle.Visible = false;
        _scriptNames = scriptInside.Add(new HFlowContainer());
        _scriptNames.AddThemeConstantOverride("h_separation", 6);
        _scriptNames.AddThemeConstantOverride("v_separation", 6);
        _scripts.NameUnderCaret += OnNameUnderCaret;
        _scripts.IsReplaced = name => OwnScriptPlace(name) is int place && _scriptChanges.Any(change => change.Index == place);
        _scripts.IsInUse = UsesText;
        _scripts.TextEdited += OnScriptTextEdited;
        EditSource.Toggled += on =>
        {
            _scripts.SetEditing(on);
            UpdateScriptEdit();
        };
        CompileScriptButton.Pressed += CompileCurrentScript;
        ShippedScriptButton.Pressed += PutShippedScriptBack;

        (PanelContainer inspector, VBoxContainer inside) = Build.Panel("Card", 8);
        right.Add(inspector);
        inside.Add(Build.Eyebrow("Selected object"));
        _objectTitle = inside.Add(Build.Text("Nothing selected", "Section", wrap: false, clip: true));
        _objectDetail = inside.Add(Build.Text("", "Muted"));
        _objectScripts = inside.Add(new HFlowContainer());
        _objectScripts.AddThemeConstantOverride("h_separation", 6);
        _objectScripts.AddThemeConstantOverride("v_separation", 6);
        _objectPaths = inside.Add(new HFlowContainer());
        _objectPaths.AddThemeConstantOverride("h_separation", 6);
        _objectPaths.AddThemeConstantOverride("v_separation", 6);
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
        ChangedOnly = changesBody.Add(new CheckButton { Text = "List only the moved objects", Disabled = true,
            TooltipText = "Show only the objects you have moved in the table, so a long session can be looked over." });
        ChangedOnly.Toggled += _ => RebuildTable();
        _draftNote = changesBody.Add(Build.Text("", "Warn"));  // the typed text that is not in use: what the prompts count as a change beside the level's own
        _draftNote.Visible = false;
        _warnings = changesBody.Add(Build.Text("", "Warn"));
        Save = changesBody.Add(Build.Button("Save as mod…", "Primary", "Save the changes as an Onslaught CE mod: a new folder. Nothing in your game changes.", disabled: true));
        Play = changesBody.Add(Build.Button("Play this level with the changes", tooltip: PlayTip, disabled: true));
        _playNote = changesBody.Add(Build.Text("", "Muted"));
        _playNote.Visible = false;
        (_savedPanel, VBoxContainer savedInside) = Build.Panel("SuccessNotice", 6);
        changesBody.Add(_savedPanel);
        _savedPanel.Visible = false;
        _savedText = savedInside.Add(Build.Text("", ""));
        _savedText.MouseFilter = Control.MouseFilterEnum.Pass;  // so that the tooltip, which has the full path, shows
        // What saving did shows under the button, in the column that scrolls, so it never takes room from the table and the map (or moves them when
        // it appears); the page scrolls it into view. It never grows with its path: the text shows the path's ends, and the buttons wrap in a narrow column.
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
        changesBody.Add(Build.Text("A saved mod is a new folder; the game's own files are never touched. Onslaught CE loads a level's world from a mod " +
            "only on Linux for now, and only if its README's Mods section lists world files as something a mod may add.", "Faint"));
        SaveDialog = new SaveAsModDialog(services.Popups);
        services.Popups.AddChild(SaveDialog);
        Save.Pressed += BeginSave;
        SaveDialog.Confirmed += () => SaveNow();
        Play.Pressed += () => _services.Status.Track(PlayAsync());
        services.Play.Changed += UpdateChanges;

        services.Game.Changed += Refresh;
        Refresh();
    }

    internal override Control Root { get; }

    internal override string Subtitle => _model?.Level is int level && _model.Session is { } session
        ? $"Level {level} · {Build.Count(session.Body.Things.Count, "object")} · {Build.Count(_model.Scripts.Count(entry => !entry.FromBaseWorld), "script")}"
        : "Move things in the game's levels, and save the result as an Onslaught CE mod";

    internal OptionButton Level { get; }
    internal LineEdit Search { get; }
    internal Tree Table { get; }
    internal LevelMap Map { get; }
    internal CheckButton MapToggle { get; }
    internal CheckButton ScriptsToggle { get; }
    internal CheckButton PathsToggle { get; }
    internal Button HidePath { get; }
    internal string HighlightedPathText => _pathText.Text;
    internal ScriptsPanel Scripts => _scripts;
    internal string NamesTitle => _scriptNamesTitle.Visible ? _scriptNamesTitle.Text : "";
    internal IReadOnlyList<Button> NameButtons => [.. _scriptNames.GetChildren().OfType<Button>()];
    internal IReadOnlyList<Label> NameLabels => [.. _scriptNames.GetChildren().OfType<Label>()];
    internal Label PathLabel => _pathText;
    internal IReadOnlyList<Button> ObjectPathButtons => [.. _objectPaths.GetChildren().OfType<Button>()];
    internal string ScriptCardTitle => _scriptCard.Visible ? _scriptTitle.Text : "";
    internal string ScriptCardText => _scriptCard.Visible ? string.Join("\n", new[] { _scriptWhere.Text, _scriptHandles.Text, _scriptCalls.Text, _scriptRuns.Text, _scriptSource.Text }.Where(text => text.Length > 0)) : "";
    internal IReadOnlyList<Button> ScriptUseButtons => [.. _scriptUses.GetChildren().OfType<Button>()];
    internal IReadOnlyList<Button> ObjectScriptButtons => [.. _objectScripts.GetChildren().OfType<Button>()];
    internal string ObjectScriptsText => string.Join("\n", _objectScripts.GetChildren().Select(child => child is Button button ? button.Text : child is Label label ? label.Text : ""));
    internal LineEdit X { get; }
    internal LineEdit Y { get; }
    internal LineEdit Z { get; }
    internal Button Undo { get; }
    internal Button Redo { get; }
    internal Button Apply { get; }
    internal Button Reset { get; }
    internal Button Save { get; }

    /// <summary>Whether the table lists only the objects that have been moved.</summary>
    internal CheckButton ChangedOnly { get; }

    /// <summary>What the page says under the world note when the filters leave the table empty (empty when it says nothing).</summary>
    internal string FilterNote => _filterNote.Visible ? _filterNote.Text : "";
    internal Button Play { get; }

    /// <summary>What the page says under the Play button: that CE is starting, or how the test play went (empty when it says nothing).</summary>
    internal string PlayNote => _playNote.Visible ? _playNote.Text : "";

    private const string PlayTip = "Start this level in Onslaught CE with your changes, without saving anything. CE runs in a temporary folder of its own: " +
        "your careers and CE settings are not touched, and nothing CE saves during the play is kept. Close CE to come back here.";
    internal SaveAsModDialog SaveDialog { get; }

    private readonly Label _scriptEditNote, _scriptEditWarnings;
    private readonly HFlowContainer _scriptEditActions;
    private EditSession? _shownSession;
    private IReadOnlyList<ScriptChange> _scriptChanges = [];  // the scripts the open level uses in place of the shipped ones, as of the last model change: the text events must not diff every script of the level
    private bool _editNoteRefused;  // the note is a refusal of the text as it was typed: it goes when the text changes
    private readonly Dictionary<(string Name, string Text), byte[]> _compiledAs = [];  // what each text that was compiled and used made, as the script is stored
    private readonly Dictionary<int, byte[]?> _scriptBytes = [];  // the open level's own scripts as stored, by place, as of the last model change

    /// <summary>The switch that makes the selected script's source editable.</summary>
    internal Button EditSource { get; }

    /// <summary>Compiles the source and makes the level use the new script.</summary>
    internal Button CompileScriptButton { get; }

    /// <summary>Makes the level use the script it came with.</summary>
    internal Button ShippedScriptButton { get; }

    /// <summary>The note in the changes card about typed text that is not in use (empty when there is none).</summary>
    internal string DraftNote => _draftNote.Visible ? _draftNote.Text : "";

    /// <summary>What compiling or putting the shipped script back said, in the script card, and the warnings about the script the level uses under it.</summary>
    internal string ScriptEditNote => string.Join("\n", new[] { _scriptEditNote.Text, _scriptEditWarnings.Visible ? _scriptEditWarnings.Text : "" }.Where(text => text.Length > 0));
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

    /// <summary>Whether the saved notice, which sits in the column that scrolls, is wholly inside what that column shows.</summary>
    internal bool SavedNoticeInView => _savedPanel.Visible && _side.GetGlobalRect().Encloses(_savedPanel.GetGlobalRect());
    internal bool EmptyVisible => _empty.Visible;
    internal string? SelectedName => _selected is int row ? _model?.Row(row)?.Label : null;
    internal int? SelectedRow => _selected;

    /// <summary>Whether the map sits beside the table (a wide column) rather than below it.</summary>
    internal bool MapBesideTable => !_split.Vertical;

    /// <summary>
    /// Whether the open level holds changes that no Save as mod has written, or source text typed and not yet compiled and used: what leaving the level, the game
    /// or the companion would drop.
    /// </summary>
    internal bool HasChanges => (_model?.HasUnsavedChanges ?? false) || _scripts.UnusedDraftCount > 0;

    /// <summary>How many changed level records and uncompiled source drafts belong to the unsaved state.</summary>
    internal int ChangeCount => (_model?.UnsavedChangeCount ?? 0) + _scripts.UnusedDraftCount;

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
            Map.SetLevel(null, []);
            _scripts.SetScripts(root, []);
            _shownScripts = [];
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
    /// changes that are not saved; the picker keeps showing the open level while the question is up, and the chosen one when the player agrees.
    /// </summary>
    internal void PickLevel(int level)
    {
        int changed = ChangeCount;
        if (_model?.Level is int open && changed > 0)
        {
            ShowInPicker(open);
            _services.AskToDiscard($"{Build.Count(changed, "change")} on level {open} {(changed == 1 ? "is" : "are")} not saved. Open level {level} and discard {(changed == 1 ? "it" : "them")}?",
                "Discard and open", () => OpenLevel(level));
            return;
        }
        OpenLevel(level);
    }

    /// <summary>Opens a level's own world, dropping what was open (the picker asks first when it holds unsaved changes). Returns false, with the reason shown, if it cannot be edited.</summary>
    internal bool OpenLevel(int level)
    {
        if (_model is null) return false;
        _selected = null;
        _savedPanel.Visible = false;
        ShowNote("", refusal: false);
        ChangedOnly.SetPressedNoSignal(false);
        bool opened = _model.Open(level);
        ShowInPicker(level);
        RebuildTable();
        Map.SetLevel(_model.Terrain, _model.Rows());
        Map.FitToLevel();
        Map.Select(null);
        HighlightPath(null);
        UpdateInspector(clearNote: true);
        UpdateChanges();
        UpdateEmpty();
        HeaderChanged?.Invoke();
        return opened;
    }

    /// <summary>The source view goes to its top while the page is shown: it is hidden with the page, and a hidden view keeps its first visible line (see ScriptsPanel.ScrollToTop).</summary>
    internal override void Leave() => _scripts.ScrollToTop();

    private void OnModelChanged()
    {
        _scriptChanges = _model?.Session?.ScriptChanges() ?? [];
        _scriptBytes.Clear();
        _problemPanel.Visible = _model?.Problem is not null;
        _problemText.Text = _model?.Problem ?? "";
        _worldNote.Text = _model?.BaseLevel is int baseLevel ? $"This level also loads the base world of level {baseLevel}. This editor does not change it." : "";
        if (!ReferenceEquals(_shownScripts, _model?.Scripts))  // the scripts change when a level is opened and when a script is replaced or taken back, not with each move
        {
            IReadOnlyList<ScriptEntry> scripts = _model?.Scripts ?? [];
            bool sameEdit = _model?.Session is not null && ReferenceEquals(_shownSession, _model.Session);
            _shownScripts = scripts;
            _shownSession = _model?.Session;
            if (!sameEdit) _compiledAs.Clear();  // another level: its scripts are not made by the texts typed for this one
            if (sameEdit) _scripts.Refresh(scripts);
            else _scripts.SetScripts(_root, scripts);
        }
        RebuildTable();
        Map.SetLevel(_model?.Terrain, _model?.Rows() ?? []);
        Map.SetPaths(_model?.Session?.Body.WaypointPaths ?? []);
        ShowPathState();
        Map.Select(_selected);
        UpdateInspector(clearNote: false);
        UpdateChanges();
    }

    private void RebuildTable()
    {
        Table.Clear();
        TreeItem root = Table.CreateItem();
        IReadOnlyList<ObjectRow> rows = _model?.Rows(Search.Text, ChangedOnly.ButtonPressed) ?? [];
        _filterNote.Text = rows.Count > 0 || _model?.Session is null ? "" : ChangedOnly.ButtonPressed
            ? Search.Text.Trim().Length > 0 ? "No moved object matches the search." : "No object is moved yet. Move one and it is listed here." : "";
        _filterNote.Visible = _filterNote.Text.Length > 0;
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
        Map.Select(row.Index);
        UpdateInspector(clearNote: true);
        return true;
    }

    /// <summary>Selects a row by its index wherever the click came from (the map): in the table too, when the search leaves it there.</summary>
    internal bool SelectIndex(int index)
    {
        if (_model?.Row(index) is null) return false;
        if (SelectRow(index)) return true;  // the table shows it
        _selected = index;
        Map.Select(index);
        UpdateInspector(clearNote: true);
        return true;
    }

    /// <summary>A mark was dragged and let go: move the row there. The move is one undo step; Z stays as it was.</summary>
    internal MoveOutcome? Dragged(int row, float x, float y)
    {
        if (_model is null) return null;
        MoveOutcome outcome = _model.MoveTo(row, x, y);
        if (_selected != row) SelectIndex(row);
        ShowNote(outcome.Message, outcome.Result == MoveResult.Refused);
        return outcome;
    }

    private void UpdateInspector(bool clearNote)
    {
        ObjectRow? row = _selected is int index ? _model?.Row(index) : null;
        if (clearNote) ShowNote("", refusal: false);
        foreach (LineEdit field in new[] { X, Y, Z }) field.Editable = row is not null;
        Apply.Disabled = row is null;
        Reset.Disabled = row is not { Changed: true };
        ShowObjectScripts(row);
        ShowObjectPaths(row);
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
        _hint.Text = "Type a number such as 276.49 or -12.1 and press Enter, or click the map and press the arrow keys (0.5 a press, Shift 5, Ctrl 0.05)." +
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
            ChangedOnly.Disabled = true;
            Play.Disabled = true;
            Play.TooltipText = "Choose a level first.";
            return;
        }
        string? summary = _model!.ChangeSummary();
        _summary.Text = summary ?? "No changes yet. Choose an object and type new coordinates.";
        ChangedOnly.Disabled = false;
        ValidationReport report = session.Validate();
        List<string> lines = [];
        if (summary is not null) lines.AddRange(report.Errors.Select(finding => "Cannot save: " + finding.Message));
        lines.AddRange(report.Warnings.Select(finding => "Take care: " + finding.Message));
        _warnings.Text = string.Join("\n", lines);
        _warnings.Visible = lines.Count > 0;
        Save.Disabled = !report.CanSave;
        Save.TooltipText = report.CanSave ? "Save the changes as an Onslaught CE mod: a new folder. Nothing in your game changes."
            : report.Errors[0].Message;
        string? playBlock = summary is null ? "Make a change first: there is nothing to try yet." : !report.CanSave ? report.Errors[0].Message : _services.Play.Unavailable();
        Play.Disabled = playBlock is not null;
        Play.TooltipText = playBlock ?? PlayTip;
    }

    private void ShowPlayNote(string text, bool failed)
    {
        _playNote.Text = text;
        _playNote.ThemeTypeVariation = failed ? "Warn" : "Muted";
        _playNote.Visible = text.Length > 0;
        if (text.Length > 0) BringIntoView(_playNote);
    }

    /// <summary>
    /// Starts Onslaught CE at the open level with the changes as they are now (nothing is saved, and the player's own CE folder and ce.ini are not
    /// written: <see cref="CePlay"/> uses a temporary folder), and says what came of it when CE closes.
    /// </summary>
    internal async Task PlayAsync()
    {
        if (_model is not { Level: int level } model || Play.Disabled) return;
        ShowPlayNote($"Onslaught CE is starting at level {level} with your changes. Close it to come back here.", failed: false);
        CePlayReport report = await _services.Play.PlayAsync(level, (parent, info) => model.StageForPlay(parent, info, ProtectedFolders()));
        bool good = report.Started && report.ModServed && report.Left.Count == 0;
        ShowPlayNote(report.Message + (report.ModLines.Count > 0 && !report.ModServed ? "\n" + string.Join("\n", report.ModLines) : ""), failed: !good);
        _services.Status.Show(!report.Started ? report.Message : report.ModServed ? $"Onslaught CE closed after level {level} with your changes." :
            "Onslaught CE closed, but its log does not say it loaded the mod.", good ? StatusKind.Success : StatusKind.Failure);
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

    /// <summary>Scrolls the right-hand column to the saved notice, once the notice has its place and size (a frame or two after it is shown).</summary>
    private void BringNoticeIntoView() => BringIntoView(_savedPanel);

    /// <summary>Scrolls the right-hand column to <paramref name="target"/> (the saved notice, the test play's note), a frame or two after it is shown, if it still is.</summary>
    private async void BringIntoView(Control target)
    {
        SceneTree? tree = _side.GetTree();
        if (tree is null) return;
        await _side.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        await _side.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        if (GodotObject.IsInstanceValid(_side) && _side.IsInsideTree() && GodotObject.IsInstanceValid(target) && target.Visible) _side.EnsureControlVisible(target);
    }

    // ---- scripts -----------------------------------------------------------------------------------------------------------------
    /// <summary>The Scripts switch: the level's compiled scripts and their source in place of the table and the map.</summary>
    private void ShowScripts(bool on)
    {
        if (!on) _scripts.ScrollToTop();  // while it is still shown: a hidden view keeps its first visible line (see ScriptsPanel.ScrollToTop)
        _split.Visible = !on;
        _scripts.Visible = on;
        MapToggle.Visible = !on;
        _scriptCard.Visible = on;
        Search.PlaceholderText = on ? ScriptSearchHint : ObjectSearchHint;
        Search.TooltipText = on ? "Shows the scripts whose name, events or functions hold this text."
            : "Shows the objects whose row number, name, kind or script holds this text.";
        if (on) _scripts.Filter(Search.Text);
        else RebuildTable();
    }

    /// <summary>Shows a script of the open level (the Scripts view, with the search cleared so that nothing hides it). Returns false if there is none of that name.</summary>
    internal bool ShowScript(string name, bool fromBase = false)
    {
        if (_model?.Scripts.Any(entry => entry.FromBaseWorld == fromBase && entry.Summary.Name == name) != true) return false;
        Search.Text = "";
        if (!ScriptsToggle.ButtonPressed) ScriptsToggle.ButtonPressed = true;
        return _scripts.Select(name, fromBase);
    }

    /// <summary>Shows an object: back to the table and the map, with the row selected.</summary>
    internal bool ShowObject(int row)
    {
        Search.Text = "";
        if (ScriptsToggle.ButtonPressed) ScriptsToggle.ButtonPressed = false;
        RebuildTable();
        return SelectIndex(row);
    }

    private void OnScriptSelected(ScriptEntry? entry, ScriptSourceResult? source)
    {
        foreach (Node child in _scriptUses.GetChildren())
        {
            _scriptUses.RemoveChild(child);
            child.QueueFree();
        }
        if (entry is null)
        {
            _scriptTitle.Text = "Nothing selected";
            _scriptWhere.Text = _scriptHandles.Text = _scriptCalls.Text = _scriptRuns.Text = _scriptSource.Text = "";
            _scriptEditNote.Text = "";
            _scriptEditWarnings.Visible = false;
            _editNoteRefused = false;
            return;
        }
        ScriptSummary summary = entry.Summary;
        _scriptTitle.Text = summary.Name;
        _scriptWhere.Text = entry.FromBaseWorld
            ? $"Compiled in the base world of level {entry.SourceLevel}, which this level loads too. This editor does not list that world's objects."
            : $"Compiled in this level's world · {Build.Count(summary.Instructions, "instruction")}";
        int shown = 12;
        _scriptHandles.Text = summary.Events.Count == 0 ? "Handles no event: nothing starts it by itself." :
            "Handles: " + string.Join(", ", summary.Events.Take(shown)) + (summary.Events.Count > shown ? $" and {summary.Events.Count - shown} more" : "");
        string calls = string.Join(", ", summary.Calls.OrderByDescending(call => call.Count).ThenBy(call => call.Name, StringComparer.Ordinal).Take(shown)
            .Select(call => call.Count > 1 ? $"{call.Name} ×{call.Count}" : call.Name));
        _scriptCalls.Text = summary.Calls.Count == 0 ? "Calls no game function." : $"Calls: {calls}" + (summary.Calls.Count > shown ? $" and {summary.Calls.Count - shown} more" : "");
        if (entry.FromBaseWorld)
        {
            _scriptRuns.Text = "";
        }
        else if (summary.Uses.Count == 0)
        {
            _scriptRuns.Text = "No object in this level names it.";
        }
        else
        {
            _scriptRuns.Text = "Named by:";
            foreach (ScriptUse use in summary.Uses.Take(16))
            {
                ObjectRow? row = _model?.Row(use.Row);
                string label = row is null ? $"row {use.Row}" : $"{use.Row} · {row.Label}";
                Button button = _scriptUses.Add(Build.Button(label, tooltip: $"{(row?.Kind ?? "object")} row {use.Row} uses it as its {use.Role}. Shows it on the map."));
                int target = use.Row;
                button.Pressed += () => ShowObject(target);
            }
            if (summary.Uses.Count > 16) _scriptUses.Add(Build.Text($"and {summary.Uses.Count - 16} more", "Faint", wrap: false));
        }
        _scriptSource.Text = source?.Source is { } found
            ? $"Source: {Path.GetFileName(found.Path)}, {(_scripts.Editing ? "being edited" : "read only")}. The game runs the compiled script, which a source in your game folder may differ from."
            : source?.Problem ?? "";
        // The note says what the last compile or reset did to the script on view. This event comes when another script is chosen and when the level's scripts changed (an Undo, a
        // Redo, another edit): either makes the note stale. A refused compile changes neither, so its note stays until the text does.
        _scriptEditNote.Text = "";
        _editNoteRefused = false;
        ShowScriptWarnings(entry);
        UpdateScriptEdit();
    }

    /// <summary>The edit controls of the script card for the selected script: what can be done with it now, and why not when it cannot.</summary>
    private void UpdateScriptEdit()
    {
        ScriptEntry? entry = _scripts.Current;
        int? index = entry is null || _model is null ? null : _model.OwnScriptIndex(entry);
        bool editable = _scripts.CanEditCurrent && index is not null && _root is not null;
        _scriptEditActions.Visible = entry is not null;
        EditSource.SetPressedNoSignal(editable && _scripts.WantsEditing);  // a script that cannot be edited shows the switch off; it comes back on with the next one that can
        EditSource.Disabled = !editable;
        EditSource.TooltipText = editable ? "Type in the script's source. Nothing in the level changes until you compile and use it."
            : entry is null ? "Choose a script."
            : entry.FromBaseWorld ? "This script belongs to the base world, which this editor shows and does not change."
            : _root is null ? "Choose your game folder on Home to edit a script."
            : "There is no source file in your game folder to start from.";
        CompileScriptButton.Disabled = !(editable && _scripts.Editing);
        // Put the shipped script back has something to do when the level uses a replaced script, and when text was typed that is to be dropped.
        ShippedScriptButton.Disabled = !(index is int place && (_scriptChanges.Any(change => change.Index == place) || _scripts.HasDraft(entry!.Summary.Name)));
        UpdateDraftNote();
    }

    /// <summary>Says which scripts have text that was typed and is not in use, so that the unsaved-work prompts' count has something to point at.</summary>
    private void UpdateDraftNote()
    {
        string text = DraftNoteText(_scripts.UnusedDraftNames);
        _draftNote.Visible = text.Length > 0;
        _draftNote.Text = text;
    }

    /// <summary>What the changes card says about typed text that is not in use, for the scripts it was typed for (empty when there are none).</summary>
    internal static string DraftNoteText(IReadOnlyList<string> names) => names.Count == 0 ? ""
        : $"Text typed for {(names.Count <= 2 ? string.Join(" and ", names) : $"{names[0]}, {names[1]} and {names.Count - 2} more")} is not in use yet and is not saved anywhere.";

    /// <summary>Compiles the source in the view and, if it compiles, makes the level use it as the script (one edit that Undo takes back).</summary>
    private void CompileCurrentScript()
    {
        if (_model is null || _root is null || _scripts.Current is not { } entry || _model.OwnScriptIndex(entry) is not int index || !_scripts.Editing) return;
        string text = _scripts.SourceText;
        ScriptEditOutcome outcome = _model.ReplaceScriptFromSource(index, text, _root);
        // The text is in use when the level's script is exactly what it compiled to: a replacement that was made, or a script that already was that.
        if ((outcome.Result is ScriptEditResult.Replaced or ScriptEditResult.Unchanged) && ScriptBytesAt(index) is { } made) _compiledAs[(entry.Summary.Name, text)] = made;
        ShowScriptEdit(outcome);
        _scripts.RefreshInfo();
        if (outcome.Line is int line) _scripts.GoToLine(line);
        UpdateScriptEdit();
    }

    /// <summary>
    /// Makes the level use the script it came with, and shows the source file's text again. When the level already uses the shipped script it drops the text that was
    /// typed instead (the one way to let go of a draft that the unsaved-work prompts count).
    /// </summary>
    private void PutShippedScriptBack()
    {
        if (_model is null || _scripts.Current is not { } entry || _model.OwnScriptIndex(entry) is not int index) return;
        if (!_scriptChanges.Any(change => change.Index == index))
        {
            if (!_scripts.HasDraft(entry.Summary.Name)) return;
            _scripts.DiscardEdit(entry.Summary.Name);
            ShowScriptEdit(new ScriptEditOutcome(ScriptEditResult.Unchanged, $"The text you typed was dropped; {entry.Summary.Name} is as the level has it.", null, []));
            UpdateScriptEdit();
            return;
        }
        ScriptEditOutcome outcome = _model.ResetScript(index);
        if (outcome.Result == ScriptEditResult.Replaced) _scripts.DiscardEdit(entry.Summary.Name);
        ShowScriptEdit(outcome);
        UpdateScriptEdit();
    }

    private void ShowScriptEdit(ScriptEditOutcome outcome)
    {
        List<string> lines = [outcome.Message];
        lines.AddRange(outcome.Notes.Select(note => $"Line {note.Line + 1}: {note.Text}"));
        if (outcome.Result == ScriptEditResult.Replaced) lines.Add("Undo takes it back.");
        _scriptEditNote.Text = string.Join("\n", lines);
        _scriptEditNote.ThemeTypeVariation = outcome.Result == ScriptEditResult.Refused ? "Warn" : "Muted";
        _editNoteRefused = outcome.Result == ScriptEditResult.Refused;
    }

    /// <summary>The note about a refusal is about the text as it was: it goes with that text. The note about a replacement stays, as the replacement does.</summary>
    private void OnScriptTextEdited()
    {
        if (_editNoteRefused)
        {
            _scriptEditNote.Text = "";
            _editNoteRefused = false;
        }
        UpdateScriptEdit();
    }

    /// <summary>The place in the open level's own world of the script with this name, or null.</summary>
    private int? OwnScriptPlace(string name)
    {
        if (_model is null) return null;
        for (int i = 0; i < _model.Scripts.Count; i++)
            if (!_model.Scripts[i].FromBaseWorld && _model.Scripts[i].Summary.Name == name) return i;
        return null;
    }

    /// <summary>The script at this place as the open level stores it (null when it cannot be stored), kept until the model next changes.</summary>
    private byte[]? ScriptBytesAt(int place)
    {
        if (_scriptBytes.TryGetValue(place, out byte[]? known)) return known;
        byte[]? bytes = null;
        if (_model?.Session is { } session && place >= 0 && place < session.Body.Scripts.Count && session.Body.Scripts[place] is { } script)
        {
            try { bytes = WorldBodyWriter.ScriptBytes(script); }
            catch (Exception error) when (EditSession.IsUnstorable(error)) { }
        }
        _scriptBytes[place] = bytes;
        return bytes;
    }

    /// <summary>Whether the open level's script of this name is exactly what this text made when it was compiled and used.</summary>
    private bool UsesText(string name, string text) =>
        OwnScriptPlace(name) is int place && _compiledAs.TryGetValue((name, text), out byte[]? made) && ScriptBytesAt(place) is { } current && current.AsSpan().SequenceEqual(made);

    /// <summary>The text the open level's script of this name was compiled from, when it was compiled and used on this page; null for the shipped script and for one made some other way.</summary>
    internal string? SourceInUse(string name)
    {
        if (OwnScriptPlace(name) is not int place || ScriptBytesAt(place) is not { } current) return null;
        foreach (KeyValuePair<(string Name, string Text), byte[]> made in _compiledAs)
            if (made.Key.Name == name && current.AsSpan().SequenceEqual(made.Value)) return made.Key.Text;
        return null;
    }

    /// <summary>Shows what to take care of in the script the level uses for this entry. Only a replaced script can have a warning, so the others cost no parse of the baseline.</summary>
    private void ShowScriptWarnings(ScriptEntry entry)
    {
        IReadOnlyList<string> warnings = _model?.OwnScriptIndex(entry) is int place && _scriptChanges.Any(change => change.Index == place) ? _model.ScriptWarnings(place) : [];
        _scriptEditWarnings.Text = string.Join("\n", warnings);
        _scriptEditWarnings.Visible = warnings.Count > 0;
    }

    /// <summary>Highlights a waypoint path of the open level on the map and brings the map to the objects it passes through. Returns false if there is no such path.</summary>
    internal bool ShowPath(int index)
    {
        if (_model?.Session?.Body.WaypointPaths is not { } paths || index < 0 || index >= paths.Count) return false;
        Search.Text = "";
        if (ScriptsToggle.ButtonPressed) ScriptsToggle.ButtonPressed = false;
        if (!MapToggle.ButtonPressed) MapToggle.ButtonPressed = true;
        RebuildTable();
        HighlightPath(index, fit: true);
        return Map.HighlightedPath == index;
    }

    private void HighlightPath(int? index, bool fit = false)
    {
        Map.HighlightPath(index, fit);
        ShowPathState();
    }

    private void ShowPathState()
    {
        WaypointPath? path = Map.HighlightedPath is int index && _model?.Session?.Body.WaypointPaths is { } paths && index < paths.Count ? paths[index] : null;
        _pathText.Text = path is null ? "" : $"Path {path.Name} · {Build.Count(WaypointCatalog.Rows(_model!.Session!.Body, path).Count, "point")}, numbered along it";
        _pathText.TooltipText = _pathText.Text;
        HidePath.Disabled = path is null;
    }

    /// <summary>Under the caret of a source there is a quoted text: say what in this level has that name, each a button that goes to it.</summary>
    private void OnNameUnderCaret(SourceToken? token)
    {
        _scriptNames.Clear();
        _scriptNamesTitle.Visible = false;
        if (token is not { Quoted: true } quoted || _model?.Session is not { } session) return;
        IReadOnlyList<NameMatch> matches = ScriptNames.Resolve(quoted.Text, session.Body, _model.Scripts, _model.BaseWorld, quoted.PathArgument);
        _scriptNamesTitle.Visible = true;
        _scriptNamesTitle.Text = matches.Count == 0 ? $"“{quoted.Text}” names nothing in this level." : $"“{quoted.Text}” names:";
        foreach (NameMatch match in matches.Take(10))
        {
            string text = match.Label + (match.ExactCase ? "" : " (other letter case)");
            if (match.Kind is NameKind.BaseObject or NameKind.BasePath)
            {
                // This page does not list the base world's objects or draw its paths, so there is nothing to go to: it is said, not offered.
                bool isPath = match.Kind == NameKind.BasePath;
                Label note = _scriptNames.Add(Build.Text($"{text} · base world", "Muted", wrap: false));
                note.MouseFilter = Control.MouseFilterEnum.Pass;  // so that the tooltip shows
                note.TooltipText = isPath
                    ? $"A path of the base world (level {_model.BaseLevel}), which the game loads before the level's own paths. The first path of that name is searched; if it has no usable waypoints, none is found. This page does not draw that world's paths."
                    : $"An object of the base world (level {_model.BaseLevel}), which the game loads with this level. This page does not list that world's objects.";
                continue;
            }
            Button button = _scriptNames.Add(Build.Button(text, tooltip: match.Kind switch
            {
                NameKind.Object => "Shows the object on the table and the map.",
                NameKind.Path => "Shows the path on the map.",
                _ => "Shows the script and its source.",
            }));
            NameMatch followed = match;
            button.Pressed += () => Follow(followed);
        }
        if (matches.Count > 10) _scriptNames.Add(Build.Text($"and {matches.Count - 10} more", "Faint", wrap: false));
        ScrollNamesIntoView();
    }

    /// <summary>The names card is the last thing in the script card, below the fold of a short window: scroll the column so that what a click just found is in view.</summary>
    private async void ScrollNamesIntoView()
    {
        SceneTree? tree = _side.GetTree();
        if (tree is null) return;
        await _side.ToSignal(tree, SceneTree.SignalName.ProcessFrame);  // the flow of buttons has its height once the column has been laid out
        await _side.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        if (GodotObject.IsInstanceValid(_side) && _side.IsInsideTree() && _scriptNamesTitle.IsVisibleInTree())
            _side.EnsureControlVisible(_scriptNames.GetChildCount() > 0 ? _scriptNames : _scriptNamesTitle);
    }

    private void Follow(NameMatch match)
    {
        switch (match.Kind)
        {
            case NameKind.Object:
                ShowObject(match.Index);
                break;
            case NameKind.Path:
                ShowPath(match.Index);
                break;
            default:
                if (_model?.Scripts.ElementAtOrDefault(match.Index) is { } entry) ShowScript(entry.Summary.Name, entry.FromBaseWorld);
                break;
        }
    }

    /// <summary>The waypoint paths the selected object is a point of, as buttons that show them on the map.</summary>
    private void ShowObjectPaths(ObjectRow? row)
    {
        _objectPaths.Clear();
        if (row is null || _model?.Session is not { } session) return;
        foreach (PathStop stop in WaypointCatalog.Through(session.Body, row.Index))
        {
            Button button = _objectPaths.Add(Build.Button($"Path {stop.Name} · point {stop.Position} of {stop.Count}", tooltip: "Shows the path on the map, numbered along it."));
            int path = stop.PathIndex;
            button.Pressed += () =>
            {
                if (ShowPath(path) && _selected is int keep) Map.Select(keep);
            };
        }
    }

    /// <summary>The scripts the selected object names, as buttons that show them (a name this level has no script of is only said).</summary>
    private void ShowObjectScripts(ObjectRow? row)
    {
        foreach (Node child in _objectScripts.GetChildren())
        {
            _objectScripts.RemoveChild(child);
            child.QueueFree();
        }
        if (row is null || _model?.Session is not { } session) return;
        foreach (ScriptReference reference in ScriptCatalog.ReferencesOf(session.Body, row.Index))
        {
            string role = char.ToUpperInvariant(reference.Role[0]) + reference.Role[1..];
            if (reference.Resolved)
            {
                Button button = _objectScripts.Add(Build.Button($"{role}: {reference.Name}", tooltip: "Shows the script's source and what it handles."));
                string name = reference.Name;
                button.Pressed += () => ShowScript(name);
            }
            else
            {
                _objectScripts.Add(Build.Text($"{role}: {reference.Name} (this level has no script of that name)", "Faint"));
            }
        }
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
        BringNoticeIntoView();
        return outcome;
    }
}
