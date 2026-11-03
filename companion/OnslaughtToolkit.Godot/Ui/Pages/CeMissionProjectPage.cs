// SPDX-License-Identifier: GPL-3.0-only
using System.Globalization;
using Godot;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Missions;
using Position = System.Numerics.Vector3;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>Authored objects and mission source in a standalone project, using the shared 3D placement viewport.</summary>
internal sealed class CeMissionProjectPage : Page
{
    private readonly StatusLine _status;
    private readonly ICeMissionProjectFiles _files;
    private readonly Func<string, CeMissionProject, CeLinkedSceneSnapshot> _loadScene;
    private readonly Func<IReadOnlyList<string?>> _protectedFolders;
    private readonly Action<string, string, Action> _ask;
    private readonly Label _notice, _selection, _drafts, _mapStatus, _mapObjectLabel, _previewNotice;
    private readonly Dictionary<string, (string X, string Y, string Z)> _positionDrafts = new(StringComparer.Ordinal);
    private readonly Dictionary<string, string> _sourceDrafts = new(StringComparer.Ordinal);
    private IReadOnlyList<ObjectRow> _rows = [];
    private TerrainSurface _workspace = TerrainSurface.Flat(0, 0, 128, 128);
    private string? _selectedObject, _selectedSource, _nameDraft;
    private bool _updating, _busy;
    private long _draftGeneration, _sceneGeneration;
    private CeLinkedSceneSnapshot? _linkedScene;
    private CeMissionMapLink? _linkedMap;
    private string? _linkedRoot;

    internal CeMissionProjectEditor Editor { get; } = new(CeMissionProject.Empty("mission_" + Guid.NewGuid().ToString("N"), "New mission"));
    internal override Control Root { get; }
    internal override string Subtitle => Editor.Current.Name + (HasUnsavedChanges ? " · not saved" : "");
    internal bool HasUnsavedChanges => Editor.HasUnsavedChanges || HasDrafts;
    internal bool Busy => _busy;
    private bool HasDrafts => _nameDraft is not null || _positionDrafts.Count > 0 || _sourceDrafts.Count > 0;
    internal LevelTerrainViewport View { get; }
    internal ItemList Objects { get; }
    internal OptionButton Sources { get; }
    internal CodeEdit Source { get; }
    internal LineEdit ProjectName { get; }
    internal LineEdit ObjectName { get; }
    internal LineEdit Definition { get; }
    internal LineEdit SourceName { get; }
    internal LineEdit MapLevel { get; }
    internal LineEdit MapObject { get; }
    internal Button LinkMapObject { get; }
    internal Button ClearMap { get; }
    internal string MapStatus => _mapStatus.Text;
    internal LineEdit X { get; }
    internal LineEdit Y { get; }
    internal LineEdit Z { get; }
    internal Button AddObject { get; }
    internal Button AddSource { get; }
    internal Button Apply { get; }
    internal Button Bind { get; }
    internal Button Unbind { get; }
    internal Button Undo { get; }
    internal Button Redo { get; }
    internal Button NewProject { get; }
    internal Button OpenProject { get; }
    internal Button SaveProject { get; }
    internal Button LoadLinkedMap { get; }
    internal Button ReloadLinkedMap { get; }
    internal Button ClearLinkedMap { get; }
    internal FileDialog LinkedMapDialog { get; }
    internal CeLinkedSceneSnapshot? LinkedScene => _linkedScene;
    internal string PreviewNotice => _previewNotice.Text;
    internal CheckButton EntrySource { get; }
    internal FileDialog OpenDialog { get; }
    internal FileDialog SaveDialog { get; }
    internal string Notice => _notice.Text;

    internal CeMissionProjectPage(StatusLine status, Node popups, Action<string, string, Action> ask,
        Func<IReadOnlyList<string?>>? protectedFolders = null, ICeMissionProjectFiles? files = null,
        Func<string, CeMissionProject, CeLinkedSceneSnapshot>? sceneLoader = null)
        : base("mission-project", "Mission project", "models")
    {
        _status = status;
        _ask = ask;
        _files = files ?? new CeMissionProjectFiles();
        _loadScene = sceneLoader ?? CeLinkedSceneLoader.Load;
        _protectedFolders = protectedFolders ?? (() => []);
        VBoxContainer page = Build.Column(10);
        Root = page;
        page.Add(Build.Text("CE linked-map placement · requires CE project support. Source text is preserved, not compiled.", "Muted"));
        HFlowContainer toolbar = page.Add(new HFlowContainer());
        NewProject = toolbar.Add(Build.Button("New", tooltip: "Start a new mission project."));
        OpenProject = toolbar.Add(Build.Button("Open…", tooltip: "Open a mission project."));
        SaveProject = toolbar.Add(Build.Button("Save as…", tooltip: "Save a new mission-project file; existing files are never replaced."));
        Undo = toolbar.Add(Build.Button("Undo"));
        Redo = toolbar.Add(Build.Button("Redo"));
        Button frame = toolbar.Add(Build.Button("Frame all", tooltip: "Frame every authored object in the 3D preview."));
        Apply = toolbar.Add(Build.Button("Apply drafts"));
        LoadLinkedMap = toolbar.Add(Build.Button("Load linked map…", tooltip: "Choose an installed-game folder to read its linked terrain and supported object models."));
        ReloadLinkedMap = toolbar.Add(Build.Button("Reload map", tooltip: "Read the selected game folder again for this project's current map bindings."));
        ClearLinkedMap = toolbar.Add(Build.Button("Close map preview", tooltip: "Release the local scene preview; keep the project's map links and placements."));
        HBoxContainer name = page.Add(Build.Row(10));
        name.Add(Build.Text("Project name", wrap: false));
        ProjectName = name.Add(new LineEdit { SizeFlagsHorizontal = Control.SizeFlags.ExpandFill });
        _drafts = page.Add(Build.Text("", "Warn"));
        _notice = page.Add(Build.Text("Add an object, place it in the 3D view, then attach mission source.", "Muted"));

        HSplitContainer body = page.Add(new HSplitContainer { SizeFlagsVertical = Control.SizeFlags.ExpandFill });
        VBoxContainer left = body.Add(Build.Column(8));
        left.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        View = left.Add(new LevelTerrainViewport
        {
            UseAuthoredSurface = true, CustomMinimumSize = new Vector2(320, 200), SizeFlagsVertical = Control.SizeFlags.ExpandFill,
            PreviewSurfaceProvider = () => _linkedScene?.Terrain ?? _workspace, RowsProvider = () => _rows,
            LinkedSceneProvider = () => _linkedScene, LinkedProjectProvider = () => Editor.Current,
            FramingPointsProvider = () => Editor.Current.Placements.Select(item => new Position(item.Position.X, -item.Position.Z, -item.Position.Y)),
            SelectedRowProvider = () => _selectedObject is null ? null : _rows.FirstOrDefault(row => Editor.Current.Placements[row.Index].Id == _selectedObject)?.Index,
        });
        _previewNotice = left.Add(Build.Text("Placement plane only · Z is the stored coordinate, positive down.", "Muted"));
        Objects = left.Add(new ItemList { CustomMinimumSize = new Vector2(320, 90), SizeFlagsVertical = Control.SizeFlags.Fill });
        VBoxContainer right = body.Add(Build.Column(8));
        right.CustomMinimumSize = new Vector2(330, 0);
        _selection = right.Add(Build.Text("Choose an object to place it or attach source.", "Muted"));
        HBoxContainer coordinates = right.Add(Build.Row(6));
        X = Coordinate(coordinates, "X"); Y = Coordinate(coordinates, "Y"); Z = Coordinate(coordinates, "Z (down)");
        ScrollContainer scroll = right.Add(new ScrollContainer { FollowFocus = true, SizeFlagsVertical = Control.SizeFlags.ExpandFill });
        VBoxContainer inspector = scroll.Add(Build.Column(8));
        inspector.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        inspector.Add(Build.Heading("New object draft", "Section"));
        ObjectName = Field(inspector, "Name for new object", "Object");
        Definition = Field(inspector, "Definition for new object", "authored.unit");
        AddObject = inspector.Add(Build.Button("Add draft as new object"));
        inspector.Add(Build.Heading("Installed-map link", "Section"));
        inspector.Add(Build.Text("Reposition one existing named map object per definition. Terrain and assets come from that map.", "Muted"));
        MapLevel = Field(inspector, "Installed map number", "");
        _mapObjectLabel = inspector.Add(Build.Text("Existing map object", "Muted"));
        MapObject = inspector.Add(new LineEdit { SizeFlagsHorizontal = Control.SizeFlags.ExpandFill,
            TooltipText = "Exact named object supplied by the linked map. Press Link selected definition to apply these fields." });
        LinkMapObject = inspector.Add(Build.Button("Link selected definition"));
        ClearMap = inspector.Add(Build.Button("Remove installed-map link"));
        _mapStatus = inspector.Add(Build.Text("", "Muted"));
        inspector.Add(Build.Heading("Mission source", "Section"));
        SourceName = Field(inspector, "Name for new source", "Mission source");
        AddSource = inspector.Add(Build.Button("Add source"));
        Sources = inspector.Add(new OptionButton { SizeFlagsHorizontal = Control.SizeFlags.ExpandFill, FitToLongestItem = false });
        EntrySource = inspector.Add(new CheckButton { Text = "Mission entry source" });
        Bind = inspector.Add(Build.Button("Attach source to selected object"));
        Unbind = inspector.Add(Build.Button("Remove object's source link"));
        Source = inspector.Add(new CodeEdit
        {
            GuttersDrawLineNumbers = true, CaretBlink = false, ScrollSmooth = false, AutoBraceCompletionEnabled = false,
            CustomMinimumSize = new Vector2(300, 190), SizeFlagsHorizontal = Control.SizeFlags.ExpandFill,
            TooltipText = "Preserved MSL source. This editor document does not compile or run it.",
        });
        Source.AddThemeFontOverride("font", CompanionTheme.MonoFont);
        Source.AddThemeFontSizeOverride("font_size", 13);
        OpenDialog = ProjectDialog(FileDialog.FileModeEnum.OpenFile, "Open mission project");
        SaveDialog = ProjectDialog(FileDialog.FileModeEnum.SaveFile, "Save a new mission project");
        LinkedMapDialog = Build.FilePicker("Choose the installed-game folder for this linked map", FileDialog.FileModeEnum.OpenDir);
        popups.AddChild(OpenDialog); popups.AddChild(SaveDialog); popups.AddChild(LinkedMapDialog);
        Connect(frame);
        Editor.Changed += RefreshDocument;
        RefreshDocument();
    }

    private void Connect(Button frame)
    {
        NewProject.Pressed += () => AskBeforeDiscard("Start a new mission project?", "Discard and start", () => OpenDocument(
            CeMissionProject.Empty("mission_" + Guid.NewGuid().ToString("N"), "New mission")));
        OpenProject.Pressed += ShowOpen;
        SaveProject.Pressed += ShowSave;
        LoadLinkedMap.Pressed += () =>
        {
            if (!_busy && !HasDrafts && Editor.Current.Map is not null) LinkedMapDialog.PopupCenteredRatio(0.8f);
        };
        LinkedMapDialog.DirSelected += path => _status.Track(LoadLinkedSceneAsync(path));
        ReloadLinkedMap.Pressed += () =>
        {
            if (!_busy && _linkedRoot is not null) _status.Track(LoadLinkedSceneAsync(_linkedRoot));
        };
        ClearLinkedMap.Pressed += CloseLinkedScene;
        OpenDialog.FileSelected += path => AskBeforeDiscard("Open another project and discard your unsaved project changes?",
            "Discard and open", () => _status.Track(OpenFileAsync(path, discardConfirmed: true)));
        SaveDialog.FileSelected += path => _status.Track(SaveFileAsync(path));
        Undo.Pressed += () => { if (!_busy && !HasDrafts) Editor.Undo(); };
        Redo.Pressed += () => { if (!_busy && !HasDrafts) Editor.Redo(); };
        frame.Pressed += FrameObjects;
        Apply.Pressed += () => ApplyDrafts();
        AddObject.Pressed += () =>
        {
            if (_busy || HasDrafts) return;
            string id = "object_" + Guid.NewGuid().ToString("N");
            Position position = new(32 + Editor.Current.Placements.Count * 12, 64, 0);
            if (Editor.TryAddPlacement(new(id, ObjectName.Text, Definition.Text, position), Editor.Revision, out string message))
            {
                _selectedObject = id;
                RefreshDocument();
                FrameObjects();
            }
            Report(message);
        };
        LinkMapObject.Pressed += () =>
        {
            if (_busy || HasDrafts || _selectedObject is null) return;
            if (!int.TryParse(MapLevel.Text, NumberStyles.None, CultureInfo.InvariantCulture, out int level))
            { Report("Enter an installed map number, then link the selected definition. No game files are read here."); return; }
            CeMissionProject project = Editor.Current;
            string definition = project.Placement(_selectedObject).Definition;
            try
            {
                CeMissionMapLink map = new(level, (project.Map?.Bindings.AsEnumerable() ?? [])
                    .Where(row => row.Definition != definition).Append(new(definition, MapObject.Text)));
                Editor.TrySetMapLink(map, Editor.Revision, out string message);
                Report(message + " Save as keeps this map link with the placements.");
            }
            catch (ArgumentException error) { Report(error.Message); }
        };
        ClearMap.Pressed += () =>
        {
            if (_busy || HasDrafts) return;
            Editor.TrySetMapLink(null, Editor.Revision, out string message);
            Report(message);
        };
        AddSource.Pressed += () =>
        {
            if (_busy || HasDrafts) return;
            string id = "source_" + Guid.NewGuid().ToString("N");
            if (Editor.TryAddScript(new(id, SourceName.Text, "// New mission source\n"), Editor.Revision, out string message))
            {
                _selectedSource = id;
                RefreshDocument();
                Source.GrabFocus();
            }
            Report(message);
        };
        ProjectName.TextChanged += text =>
        {
            if (_updating) return;
            _nameDraft = text == Editor.Current.Name ? null : text;
            _draftGeneration++;
            RefreshControls();
        };
        foreach (LineEdit field in new[] { X, Y, Z }) field.TextChanged += _ => StorePositionDraft();
        Source.TextChanged += () =>
        {
            if (_updating || _selectedSource is null) return;
            if (Source.Text == Editor.Current.Script(_selectedSource).Text) _sourceDrafts.Remove(_selectedSource);
            else _sourceDrafts[_selectedSource] = Source.Text;
            _draftGeneration++;
            RefreshControls();
        };
        Objects.ItemSelected += index => SelectObject((int)index);
        Sources.ItemSelected += index =>
        {
            if (_updating) return;
            _selectedSource = index < 0 || index >= Editor.Current.Scripts.Count ? null : Editor.Current.Scripts[(int)index].Id;
            RefreshDocument();
        };
        Bind.Pressed += () =>
        {
            if (_busy || HasDrafts || _selectedObject is null || _selectedSource is null) return;
            Editor.TryBindScript(_selectedObject, _selectedSource, Editor.Revision, out string message);
            Report(message);
        };
        Unbind.Pressed += () =>
        {
            if (_busy || HasDrafts || _selectedObject is null) return;
            Editor.TryBindScript(_selectedObject, null, Editor.Revision, out string message);
            Report(message);
        };
        EntrySource.Toggled += on =>
        {
            if (_updating || _busy || HasDrafts || _selectedSource is null) return;
            Editor.TrySetEntry(on ? _selectedSource : null, Editor.Revision, out string message);
            Report(message);
        };
        View.RowPicked += SelectObject;
        View.MoveRequested += (index, x, y) =>
        {
            if (_busy || HasDrafts) { Report("Apply your pending fields before placing an object in 3D."); return; }
            if (index < 0 || index >= Editor.Current.Placements.Count) return;
            CeMissionPlacement placement = Editor.Current.Placements[index];
            Editor.TryMovePlacement(placement.Id, new(x, y, placement.Position.Z), Editor.Revision, out string message);
            Report(message);
        };
    }

    private void SelectObject(int index)
    {
        if (_updating || _busy || index < 0 || index >= Editor.Current.Placements.Count) return;
        CeMissionPlacement placement = Editor.Current.Placements[index];
        _selectedObject = placement.Id;
        if (placement.ScriptId is not null) _selectedSource = placement.ScriptId;
        RefreshDocument();
    }

    private void StorePositionDraft()
    {
        if (_updating || _selectedObject is null) return;
        Position position = Editor.Current.Placement(_selectedObject).Position;
        var text = (X.Text, Y.Text, Z.Text);
        if (text == (Number(position.X), Number(position.Y), Number(position.Z))) _positionDrafts.Remove(_selectedObject);
        else _positionDrafts[_selectedObject] = text;
        _draftGeneration++;
        RefreshControls();
    }

    internal bool ApplyDrafts()
    {
        if (_busy) return false;
        Dictionary<string, Position> positions = new(StringComparer.Ordinal);
        foreach (var (id, text) in _positionDrafts)
        {
            if (!CoordinateValue(text.X, out float x) || !CoordinateValue(text.Y, out float y) || !CoordinateValue(text.Z, out float z))
            {
                Report("Each coordinate must be a finite number. Your drafts have been kept.");
                return false;
            }
            positions[id] = new(x, y, z);
        }
        if (!Editor.TryApplyDrafts(_nameDraft, positions, _sourceDrafts, Editor.Revision, out string message))
        { Report(message); return false; }
        ClearDrafts();
        RefreshDocument();
        Report(message);
        return true;
    }

    private void RefreshDocument()
    {
        _updating = true;
        try
        {
            CeMissionProject project = Editor.Current;
            if (_linkedScene is not null && !ReferenceEquals(project.Map, _linkedMap))
            {
                _linkedScene = null; _linkedMap = null; _sceneGeneration++;
                View.Refit();
            }
            _previewNotice.Text = _linkedScene is null
                ? "Placement plane only · Z is the stored coordinate, positive down."
                : "Sampled linked terrain · static, untextured object models · source files stay read-only." +
                  (_linkedScene.Notes.Count == 0 ? "" : " " + _linkedScene.Notes.Count + " model reference note(s); hover for details.");
            _previewNotice.TooltipText = _linkedScene is null ? _linkedRoot ?? "" :
                string.Join("\n", new[] { _linkedRoot ?? "", "Only explicit map mesh references are shown; code-created models and animation are outside this preview." }
                    .Concat(_linkedScene.Notes.Take(8).Select(PreviewNote)));
            if (!project.Placements.Any(item => item.Id == _selectedObject)) _selectedObject = project.Placements.FirstOrDefault()?.Id;
            if (!project.Scripts.Any(item => item.Id == _selectedSource)) _selectedSource = project.Scripts.FirstOrDefault()?.Id;
            _rows = project.Placements.Select((item, index) => new ObjectRow(index, "Authored", item.Name, item.Definition,
                item.Position, item.Position)).ToArray();
            ProjectName.Text = _nameDraft ?? project.Name;
            Objects.Clear();
            for (int index = 0; index < project.Placements.Count; index++)
            {
                CeMissionPlacement item = project.Placements[index];
                Objects.AddItem(item.Name + " · " + item.Definition);
                Objects.SetItemTooltip(index, item.Id);
                if (item.Id == _selectedObject) Objects.Select(index);
            }
            CeMissionPlacement? selected = project.Placements.FirstOrDefault(item => item.Id == _selectedObject);
            _selection.Text = selected is null ? "Choose an object to place it or attach source." :
                "Selected: " + selected.Name + (selected.ScriptId is null ? " · no source attached" : " · source: " + project.Script(selected.ScriptId).Name);
            var position = selected is not null && _positionDrafts.TryGetValue(selected.Id, out var draft) ? draft :
                selected is not null ? (Number(selected.Position.X), Number(selected.Position.Y), Number(selected.Position.Z)) : ("0", "0", "0");
            (X.Text, Y.Text, Z.Text) = position;
            MapLevel.Text = project.Map?.Level.ToString(CultureInfo.InvariantCulture) ?? "";
            _mapObjectLabel.Text = selected is null ? "Select a placement to bind its definition" : "Existing map object for " + selected.Definition;
            MapObject.Text = selected is null ? "" : project.Map?.Bindings.FirstOrDefault(row => row.Definition == selected.Definition)?.SourceObject ?? "";
            _mapStatus.Text = project.RuntimeLinkStatus();
            Sources.Clear();
            for (int index = 0; index < project.Scripts.Count; index++)
            {
                Sources.AddItem(project.Scripts[index].Name);
                if (project.Scripts[index].Id == _selectedSource) Sources.Select(index);
            }
            Source.Text = _selectedSource is null ? "" : _sourceDrafts.GetValueOrDefault(_selectedSource, project.Script(_selectedSource).Text);
            EntrySource.ButtonPressed = _selectedSource is not null && project.EntryScriptId == _selectedSource;
        }
        finally { _updating = false; }
        RefreshControls();
    }

    private void RefreshControls()
    {
        bool change = !_busy && !HasDrafts;
        NewProject.Disabled = OpenProject.Disabled = SaveProject.Disabled = _busy;
        LoadLinkedMap.Disabled = !change || Editor.Current.Map is null;
        ReloadLinkedMap.Disabled = !change || Editor.Current.Map is null || _linkedRoot is null;
        ClearLinkedMap.Disabled = _busy || (_linkedScene is null && _linkedRoot is null);
        AddObject.Disabled = AddSource.Disabled = !change;
        LinkMapObject.Disabled = !change || _selectedObject is null;
        ClearMap.Disabled = !change || Editor.Current.Map is null;
        MapLevel.Editable = MapObject.Editable = !_busy;
        Apply.Disabled = _busy || !HasDrafts;
        Undo.Disabled = !change || !Editor.CanUndo;
        Redo.Disabled = !change || !Editor.CanRedo;
        Bind.Disabled = !change || _selectedObject is null || _selectedSource is null;
        Unbind.Disabled = !change || _selectedObject is null || Editor.Current.Placement(_selectedObject).ScriptId is null;
        EntrySource.Disabled = !change || _selectedSource is null;
        ProjectName.Editable = ObjectName.Editable = Definition.Editable = SourceName.Editable = !_busy;
        X.Editable = Y.Editable = Z.Editable = !_busy && _selectedObject is not null;
        Source.Editable = !_busy && _selectedSource is not null;
        Sources.Disabled = _busy || Editor.Current.Scripts.Count == 0;
        _drafts.Visible = HasDrafts;
        _drafts.Text = "Draft fields are kept as you switch selection. Apply drafts or Save as before Undo.";
        HeaderChanged?.Invoke();
    }

    internal void OpenDocument(CeMissionProject document)
    {
        ClearDrafts();
        _selectedObject = _selectedSource = null;
        Editor.Open(document);
        FrameObjects();
        Report("Project opened. Placements, map bindings and source are kept together; Undo starts a new history.");
    }

    private void FrameObjects()
    {
        try
        {
            double minX = 0, minY = 0, maxX = 128, maxY = 128;
            foreach (CeMissionPlacement placement in Editor.Current.Placements)
            {
                minX = Math.Min(minX, placement.Position.X); maxX = Math.Max(maxX, placement.Position.X);
                minY = Math.Min(minY, placement.Position.Y); maxY = Math.Max(maxY, placement.Position.Y);
            }
            double margin = Math.Max(maxX - minX, maxY - minY) * 0.1;
            _workspace = TerrainSurface.Flat((float)(minX - margin), (float)(minY - margin), (float)(maxX + margin), (float)(maxY + margin));
            View.Refit();
        }
        catch (ArgumentException) { Report("These coordinates are kept in the project, but their range is too large for this preview."); }
    }

    internal async Task<bool> LoadLinkedSceneAsync(string gameRoot)
    {
        if (_busy || HasDrafts) { Report("Apply pending fields before reading a linked map."); return false; }
        CeMissionProject project = Editor.Current;
        if (project.Map is null) { Report("Link an installed map and named object first. No game folder was read."); return false; }
        if (!Path.IsPathFullyQualified(gameRoot)) { Report("Choose an explicit installed-game folder for the read-only preview."); return false; }
        long revision = Editor.Revision, generation = _sceneGeneration, drafts = _draftGeneration;
        _busy = true;
        Report("Reading linked terrain and models from the selected folder… Source files are opened read-only.");
        RefreshControls();
        try
        {
            CeLinkedSceneSnapshot scene = await Task.Run(() => _loadScene(gameRoot, project));
            if (Editor.Revision != revision || _draftGeneration != drafts || _sceneGeneration != generation)
            { Report("The project changed while that map was read. The newer document was kept; load its map again."); return false; }
            if (scene.Level != project.Map.Level)
            { Report("That scene does not match the project's installed-map link. The current preview was kept."); return false; }
            _linkedScene = scene;
            _linkedMap = project.Map;
            _linkedRoot = Path.GetFullPath(gameRoot);
            RefreshDocument();
            FrameObjects();
            Report("Linked map preview loaded read-only. Position edits update the project; Save as keeps them in its own file." +
                (scene.Notes.Count == 0 ? "" : " " + string.Join(" ", scene.Notes.Take(2).Select(PreviewNote))));
            return true;
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or InvalidDataException or ArgumentException)
        {
            Report("The linked map preview could not be loaded. " + error.Message + " The project was kept.");
            return false;
        }
        finally { _busy = false; RefreshControls(); }
    }

    internal void CloseLinkedScene()
    {
        if (_busy) return;
        _linkedScene = null; _linkedMap = null; _linkedRoot = null; _sceneGeneration++;
        RefreshDocument();
        FrameObjects();
        Report("The local map preview was closed. Project placements, map links and source were kept.");
    }

    internal void ShowOpen()
    {
        if (!_busy) OpenDialog.PopupCenteredRatio(0.8f);
    }

    internal void ShowSave()
    {
        if (_busy || !ApplyDrafts()) return;
        SaveDialog.CurrentFile = "mission-project" + CeMissionProjectFiles.Extension;
        SaveDialog.PopupCenteredRatio(0.8f);
    }

    internal async Task<bool> OpenFileAsync(string path, bool discardConfirmed = false)
    {
        if (_busy) return false;
        if (HasUnsavedChanges && !discardConfirmed) { Report("Confirm discarding unsaved changes before opening another project."); return false; }
        long revision = Editor.Revision, draftGeneration = _draftGeneration;
        _busy = true;
        RefreshControls();
        try
        {
            CeProjectRead read = await Task.Run(() => _files.Open(path));
            if (!read.Ok || read.Bytes is null) { Report(read.Message); return false; }
            CeMissionProject document;
            try { document = CeMissionProjectJson.Read(read.Bytes); }
            catch (InvalidDataException error) { Report(error.Message + " Your current project was kept."); return false; }
            if (Editor.Revision != revision || _draftGeneration != draftGeneration)
            { Report("Your project changed while that file was read. The current project and drafts were kept."); return false; }
            OpenDocument(document);
            return true;
        }
        finally { _busy = false; RefreshControls(); }
    }

    internal async Task<bool> SaveFileAsync(string path)
    {
        if (_busy || !ApplyDrafts()) return false;
        byte[] bytes;
        try { bytes = CeMissionProjectJson.Write(Editor.Current); }
        catch (InvalidDataException error) { Report(error.Message); return false; }
        long revision = Editor.Revision;
        string?[] protectedFolders = _protectedFolders().ToArray();
        _busy = true;
        RefreshControls();
        try
        {
            CeProjectWrite write = await Task.Run(() => _files.WriteNew(path, bytes, protectedFolders));
            if (!write.Ok) { Report(write.Message); return false; }
            bool current = Editor.MarkSaved(revision) && !HasDrafts;
            Report(write.Message + (current ? " " + Path.GetFileName(write.Path) : " A saved snapshot exists; newer changes are still unsaved."));
            _notice.TooltipText = write.Path ?? "";
            return true;
        }
        finally { _busy = false; RefreshControls(); }
    }

    private void AskBeforeDiscard(string question, string action, Action then)
    {
        if (_busy) return;
        if (HasUnsavedChanges) _ask(question, action, then);
        else then();
    }

    private static FileDialog ProjectDialog(FileDialog.FileModeEnum mode, string title) =>
        Build.FilePicker(title, mode, "*.ceproject ; CE mission projects");

    private void ClearDrafts() { _nameDraft = null; _positionDrafts.Clear(); _sourceDrafts.Clear(); _draftGeneration++; }
    private void Report(string message) { _notice.Text = message; }
    private static string PreviewNote(string value)
    {
        if (value.Length <= 180) return value;
        int end = char.IsHighSurrogate(value[176]) ? 176 : 177;
        return value[..end] + "…";
    }

    private static string Number(float value) => value.ToString("R", CultureInfo.InvariantCulture);
    private static bool CoordinateValue(string text, out float value) => float.TryParse(text, NumberStyles.Float,
        CultureInfo.InvariantCulture, out value) && float.IsFinite(value);

    private static LineEdit Field(VBoxContainer parent, string label, string value)
    {
        parent.Add(Build.Text(label, "Muted", wrap: false));
        return parent.Add(new LineEdit { Text = value, SizeFlagsHorizontal = Control.SizeFlags.ExpandFill, TooltipText = label });
    }

    private static LineEdit Coordinate(HBoxContainer parent, string label)
    {
        VBoxContainer field = parent.Add(Build.Column(3));
        field.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        field.Add(Build.Text(label, "Muted", wrap: false));
        return field.Add(new LineEdit { Text = "0", CustomMinimumSize = new Vector2(70, 0), SizeFlagsHorizontal = Control.SizeFlags.ExpandFill });
    }
}
