// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Ui;

internal sealed partial class LevelEditorPage
{
    private sealed record ProjectContext(LevelEditorModel Model, EditSession Session, long Revision, EditorScriptDraftStamp Draft, EditorProjectState State, string? Root);
    private sealed record ProjectSave(string Path, byte[] Bytes, ProjectContext Context);
    private sealed record ProjectOpen(EditorProjectRead Read, ProjectContext Context, PreparedEditorProject Model, PreparedScriptProject Scripts);
    private sealed record SavedProject(LevelEditorModel Model, EditSession Session, EditorProjectState State, string DraftHash);
    private ProjectSave? _pendingProjectSave;
    private ProjectContext? _pendingModSave;
    private ProjectOpen? _pendingProjectOpen;
    private SavedProject? _savedProject;
    private bool _projectBusy, _projectCommitting;
    private Viewport? _projectSizingViewport;
    private Label _projectMessage = null!;
    internal Button SaveProject { get; private set; } = null!;
    internal Button OpenProject { get; private set; } = null!;
    internal FileDialog ProjectSaveDialog { get; private set; } = null!;
    internal FileDialog ProjectOpenDialog { get; private set; } = null!;
    internal ConfirmationDialog ProjectSaveConfirm { get; private set; } = null!;
    internal Task ProjectOperation { get; private set; } = Task.CompletedTask;
    internal string ProjectMessage => _projectMessage.Text;

    private void AddProjectControls(VBoxContainer parent)
    {
        HFlowContainer actions = parent.Add(new HFlowContainer());
        actions.AddThemeConstantOverride("h_separation", 8);
        parent.RemoveChild(TerrainEdit);
        actions.AddChild(TerrainEdit);
        SaveProject = actions.Add(Build.Button("Save project as…", tooltip: "Save drafts, world edits and sampled terrain preview to a new editor project."));
        OpenProject = actions.Add(Build.Button("Open project…", tooltip: "Select the matching base level, then reopen an editor project."));
        _projectMessage = parent.Add(Build.Text("Projects preserve editor work; export CE mods separately.", "Faint", wrap: false, clip: true));
        _projectMessage.TooltipText = _projectMessage.Text;
        Root.Resized += FitEditorMinimums;
        Root.TreeEntered += () =>
        {
            _projectSizingViewport = Root.GetViewport();
            _projectSizingViewport.SizeChanged += FitEditorMinimums;
            FitEditorMinimums();
        };
        Root.TreeExiting += () =>
        {
            if (GodotObject.IsInstanceValid(_projectSizingViewport)) _projectSizingViewport!.SizeChanged -= FitEditorMinimums;
            _projectSizingViewport = null;
        };
        string filter = "*" + EditorProjectFiles.Extension + " ; Onslaught editor projects";
        ProjectSaveDialog = _services.Popups.Add(Build.FilePicker("Save a new editor project", FileDialog.FileModeEnum.SaveFile, filter));
        ProjectOpenDialog = _services.Popups.Add(Build.FilePicker("Open a project for the selected base level", FileDialog.FileModeEnum.OpenFile, filter));
        ProjectSaveConfirm = _services.Popups.Add(Build.Confirm("Save a new editor project?", "Save project"));
        SaveProject.Pressed += () => { ProjectSaveDialog.CurrentFile = $"level-{_model?.Level:000}" + EditorProjectFiles.Extension; ProjectSaveDialog.PopupCenteredRatio(0.75f); };
        OpenProject.Pressed += () => ProjectOpenDialog.PopupCenteredRatio(0.75f);
        ProjectSaveDialog.FileSelected += path => RequestProjectSave(path);
        ProjectOpenDialog.FileSelected += path => TrackProject(OpenProjectAsync(path));
        ProjectSaveConfirm.Confirmed += () => TrackProject(SaveProjectAsync());
    }

    private void TrackProject(Task operation) { ProjectOperation = operation; _services.Status.Track(operation); }
    private void UpdateProjectControls()
    {
        if (SaveProject is null) return;
        if (_savedProject is { } saved && (!ReferenceEquals(_model, saved.Model) || !ReferenceEquals(_model?.Session, saved.Session)))
        {
            _savedProject = null;
            _projectMessage.Text = "Projects preserve editor work; export CE mods separately.";
            _projectMessage.TooltipText = _projectMessage.Text;
            _projectMessage.ThemeTypeVariation = "Faint";
        }
        bool radius = TriggerRadius is { HasDraft: true };
        bool coordinates = X is not null && CoordinatesHaveDraft;
        SaveProject.Disabled = OpenProject.Disabled = _model?.Session is null || _projectBusy || _services.Game.Busy || _services.Workspace is not { IsAvailable: true, Busy: false } || radius || coordinates;
        string? reason = radius ? "Apply or discard the unapplied trigger-radius draft before saving or opening a project."
            : coordinates ? "Apply coordinate edits first, or press Escape in a coordinate field to restore the current coordinates."
            : _model?.Session is null ? "Choose the project's base level first." : _services.Game.Busy ? "Wait for the game folder read." : _projectBusy || _services.Workspace?.Busy == true ? "Wait for the current file operation." : null;
        SaveProject.TooltipText = reason ?? "Save a new editor project at a path you choose. Existing files are kept.";
        OpenProject.TooltipText = reason ?? "Open an editor project against the selected base level, preserving its source drafts.";
    }

    private bool MatchesSavedProject()
    {
        if (_savedProject is not { } saved || !ReferenceEquals(_model, saved.Model) || !ReferenceEquals(_model.Session, saved.Session)) return false;
        try { return _scripts.DraftContentHash() == saved.DraftHash && _model.ProjectState() == saved.State; }
        catch (Exception error) when (ProjectOperationFailure(error)) { return false; }
    }

    internal Func<bool> CaptureFolderSwitchGuard()
    {
        var model = _model;
        var session = model?.Session;
        long revision = _viewRevision;
        var scripts = _scripts.CaptureDraftState();
        var coordinates = (X.Text, Y.Text, Z.Text);
        string radius = TriggerRadius.RadiusInput.Text;
        return () => ReferenceEquals(_model, model) && ReferenceEquals(_model?.Session, session) && _viewRevision == revision &&
            _scripts.MatchesDraftState(scripts) && (X.Text, Y.Text, Z.Text) == coordinates && TriggerRadius.RadiusInput.Text == radius;
    }

    private bool TryProjectContext(out ProjectContext? context)
    {
        context = null;
        if (TriggerRadius.HasDraft) { ProjectResult("Apply or discard the unapplied trigger-radius draft before saving or opening a project.", false); return false; }
        if (CoordinatesHaveDraft) { ProjectResult("Apply coordinate edits first, or press Escape in a coordinate field to restore the current coordinates.", false); return false; }
        if (_model is not { Session: { } session } model || _services.Game.Busy || _services.Workspace is not { IsAvailable: true, Busy: false } || _projectBusy)
        { ProjectResult("Choose a base level and wait for any file operation to finish.", false); return false; }
        try { EditorScriptDraftStamp draft = _scripts.CaptureDraftState(); context = new(model, session, _viewRevision, draft, model.ProjectState(), _root); return true; }
        catch (Exception error) when (ProjectOperationFailure(error)) { ProjectResult("The current edit could not be checked safely. It was kept.", false); return false; }
    }

    private bool MatchesProjectContext(ProjectContext context)
    {
        if (TriggerRadius.HasDraft || CoordinatesHaveDraft || _services.Game.Busy || !ReferenceEquals(_model, context.Model) || !ReferenceEquals(_model.Session, context.Session) ||
            _viewRevision != context.Revision || _root != context.Root || !_scripts.MatchesDraftState(context.Draft)) return false;
        try { return context.Model.ProjectState() == context.State; }
        catch (Exception error) when (ProjectOperationFailure(error)) { return false; }
    }

    internal bool RequestProjectSave(string path)
    {
        if (!TryProjectContext(out ProjectContext? context) || context is null) return false;
        try
        {
            IReadOnlyList<EditorProjectScript> scripts = _scripts.CaptureProjectScripts(context.Session, index => SourceInUse(context.Session.Body.Scripts[index].Name));
            byte[] bytes = context.Model.CaptureProject(scripts);
            if (!MatchesProjectContext(context)) { ProjectResult("The edit changed while the project was being prepared. Choose again.", false); return false; }
            _pendingProjectSave = new(path, bytes, context);
            ProjectSaveConfirm.DialogText = "Save a new editor project to:\n" + path +
                "\n\nIt contains world changes, sampled terrain preview and script source text and drafts. Source text from your installation and original-game-derived world material may be included; keep this file private." +
                "\n\nThis is an editor snapshot, not a format CE loads. Existing files are preserved. Opening a project starts a fresh undo history.";
            ProjectSaveConfirm.PopupCentered();
            return true;
        }
        catch (Exception error) when (ProjectOperationFailure(error))
        { ProjectResult(error is InvalidDataException ? error.Message : "The project could not be prepared. The current edit was kept.", false); return false; }
    }

    private async Task SaveProjectAsync()
    {
        ProjectSave? pending = _pendingProjectSave;
        _pendingProjectSave = null;
        if (pending is null || !MatchesProjectContext(pending.Context))
        { ProjectResult("The edit changed while save confirmation was open. Choose Save project as again; nothing was written.", false); return; }
        if (_services.Workspace is not { IsAvailable: true, Busy: false })
        { ProjectResult("Wait for the current file operation, then choose Save project as again. Nothing was written.", false); return; }
        _projectBusy = true;
        UpdateProjectControls();
        try
        {
            string?[] protectedFolders = [.. ProtectedFolders(), _services.Game.CeUserFolder];
            EditorProjectWrite receipt = await _services.Workspace.RunEditorFileOperationAsync(
                () => _services.EditorProjects.WriteNew(pending.Path, pending.Bytes, protectedFolders), message => new EditorProjectWrite(false, message, MayHaveOutput: true));
            if (!receipt.Ok)
            {
                ProjectResult((receipt.MayHaveOutput ? "A project file may exist without final verification. Keep it for inspection and choose a new filename. " : "") + receipt.Message, false);
                return;
            }
            if (MatchesProjectContext(pending.Context))
            {
                _savedProject = new(pending.Context.Model, pending.Context.Session, pending.Context.State, _scripts.DraftContentHash());
                ProjectResult("Saved and verified a new editor project: " + receipt.Path + ". Source drafts and sampled terrain preview are preserved; CE uses exported mods separately.", true);
            }
            else ProjectResult("Saved and verified the confirmed snapshot: " + receipt.Path + ". Newer edits remain unsaved in the editor.", true);
            UpdateDraftNote();
            HeaderChanged?.Invoke();
        }
        finally { _projectBusy = false; UpdateProjectControls(); }
    }

    internal async Task OpenProjectAsync(string path)
    {
        if (!TryProjectContext(out ProjectContext? context) || context is null) return;
        _pendingProjectOpen = null;
        ProjectOpen? automatic = null;
        _projectBusy = true;
        UpdateProjectControls();
        try
        {
            EditorProjectRead read = await ReadProjectAsync(path);
            if (!read.Ok || read.Bytes is null) { ProjectResult(read.Message, false); return; }
            if (!MatchesProjectContext(context)) { ProjectResult("The edit changed while the project was being read. The current edit was kept; choose again.", false); return; }
            if (!context.Model.TryPrepareProject(read.Bytes, out PreparedEditorProject? model, out string message) || model is null)
            { ProjectResult(message, false); return; }
            if (!_scripts.TryPrepareProjectScripts(model.Entries, model.Restored.Scripts, out PreparedScriptProject? scripts, out message) || scripts is null)
            { ProjectResult(message, false); return; }
            ProjectOpen pending = new(read, context, model, scripts);
            _pendingProjectOpen = pending;
            if (HasChanges)
                _services.AskToDiscard("Open this editor project and discard the current unsaved world changes and source drafts? The project and current level files are kept. Undo history starts again.",
                    "Discard and open project", () => TrackProject(CommitProjectOpenAsync(pending)));
            else automatic = pending;
        }
        finally { _projectBusy = false; UpdateProjectControls(); }
        if (automatic is not null) await CommitProjectOpenAsync(automatic);
    }

    private Task<EditorProjectRead> ReadProjectAsync(string path) => _services.Workspace.RunEditorFileOperationAsync(
        () => _services.EditorProjects.Open(path), message => new EditorProjectRead(false, message));

    private async Task CommitProjectOpenAsync(ProjectOpen pending)
    {
        if (!ReferenceEquals(_pendingProjectOpen, pending) || !MatchesProjectContext(pending.Context))
        { ProjectResult("The edit changed while open confirmation was pending. The current edit was kept; choose again.", false); return; }
        _pendingProjectOpen = null;
        _projectBusy = true;
        UpdateProjectControls();
        try
        {
            EditorProjectRead current = await ReadProjectAsync(pending.Read.Path);
            if (!current.Ok || current.Identity != pending.Read.Identity || current.Sha256 != pending.Read.Sha256 || current.Bytes is null ||
                !current.Bytes.AsSpan().SequenceEqual(pending.Read.Bytes))
            { ProjectResult("The selected project changed or could not be verified again. The current edit was kept; choose the project again.", false); return; }
            Dictionary<(string Name, string Text), byte[]> verified = [];
            int unverified = 0;
            foreach (EditorProjectScript script in pending.Model.Restored.Scripts)
            {
                if (script.UsedText is null) continue;
                ScriptCompileOutcome compiled = LevelEditorModel.CompileProjectScript(pending.Model.Restored.Session, script.Index, script.UsedText, _root ?? "");
                if (compiled.Script is not { } record || EditorProject.Hash(WorldBodyWriter.ScriptBytes(record)) != script.UsedRecordHash) { unverified++; continue; }
                verified[(script.Name, script.UsedText)] = WorldBodyWriter.ScriptBytes(record);
            }
            if (!MatchesProjectContext(pending.Context) || !pending.Context.Model.CanCommitProject(pending.Model) || !_scripts.IsPreparedProjectCurrent(pending.Scripts))
            { ProjectResult("The edit or prepared project changed. The current edit was kept; choose again.", false); return; }
            _projectCommitting = true;
            try
            {
                if (!pending.Context.Model.CommitProject(pending.Model, notify: false))
                { ProjectResult("The prepared project became stale. The current edit was kept.", false); return; }
                _compiledAs.Clear();
                foreach (var association in verified) _compiledAs.Add(association.Key, association.Value);
                _scriptBytes.Clear();
                _scriptChanges = pending.Model.Restored.Session.ScriptChanges();
                if (!_scripts.CommitProjectScripts(pending.Scripts, notify: false)) throw new InvalidOperationException("A prechecked script import could not be committed.");
                _shownSession = pending.Context.Model.Session;
                _shownScripts = pending.Context.Model.Scripts;
                _selected = null;
                _savedProject = new(pending.Context.Model, pending.Context.Model.Session!, pending.Context.Model.ProjectState(), _scripts.DraftContentHash());
            }
            finally { _projectCommitting = false; }
            pending.Context.Model.AnnounceProjectOpened();
            OnScriptSelected(_scripts.Current, _scripts.CurrentSource);
            ProjectResult("Opened editor project: " + current.Path + ". Source drafts and sampled terrain preview restored; undo history starts again." +
                (unverified > 0 ? " Stored source text that could not be recompiled and verified is preserved without an in-use claim." : ""), true);
            HeaderChanged?.Invoke();
        }
        finally { _projectBusy = false; UpdateProjectControls(); }
    }

    private void ProjectResult(string message, bool success)
    {
        _projectMessage.Text = message;
        _projectMessage.TooltipText = message;
        _projectMessage.ThemeTypeVariation = success ? "Muted" : "Warn";
        _services.Status.Show(message, success ? StatusKind.Success : StatusKind.Failure);
    }

    private static bool ProjectOperationFailure(Exception error) => error is IOException or UnauthorizedAccessException or ArgumentException or NotSupportedException || EditSession.IsUnstorable(error);

    private void FitEditorMinimums()
    {
        if (Table is null || Map is null || _terrainPreview3d is null) return;
        if (!Root.IsInsideTree()) return;
        float scale = Math.Max(0.1f, Root.GetGlobalTransformWithCanvas().Scale.Y);
        float height = Root.GetViewportRect().Size.Y / scale < 900 ? 96 : 150;
        if (Table.CustomMinimumSize.Y == height && _terrainPreview3d.CustomMinimumSize.Y == height && Map.CustomMinimumSize.Y == height) return;
        Table.CustomMinimumSize = new Vector2(Table.CustomMinimumSize.X, height);
        _terrainPreview3d.CustomMinimumSize = new Vector2(_terrainPreview3d.CustomMinimumSize.X, height);
        Map.CustomMinimumSize = new Vector2(Map.CustomMinimumSize.X, height);
    }
}
