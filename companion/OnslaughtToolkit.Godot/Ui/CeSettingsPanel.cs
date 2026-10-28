// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Options;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>Only the two documented launcher switches; career-embedded options and all other ce.ini keys stay separate.</summary>
internal sealed class CeSettingsPanel
{
    private readonly AppServices _app;
    private readonly Label _path, _source, _result;
    private CeSettings? _snapshot;
    private string? _loadedFolder;
    private bool _loading, _saving;

    internal CeSettingsPanel(AppServices app)
    {
        _app = app;
        (ScrollContainer scroll, VBoxContainer content) = Build.Scroller();
        Root = scroll;
        (PanelContainer card, VBoxContainer body) = Build.Card("CE launcher settings");
        content.Add(card);
        _path = body.Add(Build.Text("", "Faint"));
        body.Add(Build.Text("These choices apply the next time you start CE. Other settings in ce.ini are kept as they are.", "Muted"));
        UpdateCheck = body.Add(new CheckBox { Text = "Check for updates when CE starts (update_check; read by CE 0.1.8 and later)" });
        body.Add(Build.Text("Turning update checks off does not make CE 0.1.0–0.1.6 safe to start: their startup cleanup " +
            "can delete neighbouring folders either way.", "Faint"));
        RecordSessions = body.Add(new CheckBox { Text = "Offer to record a session when CE starts" });
        _source = body.Add(Build.Text("", "Muted"));
        body.Add(Build.Text("Change controls, sound and gameplay options in CE itself. The original game's default settings are separate.", "Muted"));
        HBoxContainer actions = body.Add(Build.Row(12));
        Save = actions.Add(Build.Button("Back up and save…", "Primary"));
        Undo = actions.Add(Build.Button("Undo changes"));
        _result = body.Add(Build.Text("", "Muted"));
        Confirm = app.Popups.Add(Build.Confirm("Save CE launcher settings?", "Back up and save"));
        Confirm.Confirmed += () => _app.Status.Track(SaveAsync());
        Confirm.Canceled += RefreshControls;
        UpdateCheck.Toggled += _ => RefreshControls();
        RecordSessions.Toggled += _ => RefreshControls();
        Save.Pressed += AskToSave;
        Undo.Pressed += () => _app.Status.Track(LoadAsync());
        _app.Game.Changed += Refresh;
        _app.Workspace.Changed += RefreshControls;
        RefreshControls();
    }

    internal Control Root { get; }
    internal CheckBox UpdateCheck { get; }
    internal CheckBox RecordSessions { get; }
    internal Button Save { get; }
    internal Button Undo { get; }
    internal ConfirmationDialog Confirm { get; }
    internal string ResultText => _result.Text;
    internal string SettingsPath => _snapshot?.Path ?? "";
    internal bool HasChanges => _snapshot is CeSettings saved &&
        (UpdateCheck.ButtonPressed != saved.UpdateCheck || RecordSessions.ButtonPressed != saved.RecordSessions);
    internal int ChangeCount => _snapshot is CeSettings saved
        ? (UpdateCheck.ButtonPressed != saved.UpdateCheck ? 1 : 0) + (RecordSessions.ButtonPressed != saved.RecordSessions ? 1 : 0) : 0;

    internal void ResetTarget()
    {
        _snapshot = null;
        _loadedFolder = null;
        Confirm.Hide();
        RefreshControls();
    }

    internal void Refresh()
    {
        Root.Visible = _app.Game.Target == GameTarget.OnslaughtCe;
        if (Root.Visible && !_app.Game.Busy && !_loading && !_saving &&
            _loadedFolder != _app.Game.CeUserFolder)
            _app.Status.Track(LoadAsync());
        RefreshControls();
    }

    internal async Task LoadAsync()
    {
        if (_loading || _saving || _app.Workspace.Busy || _app.Game.Target != GameTarget.OnslaughtCe) return;
        _loading = true;
        string folder = _app.Game.CeUserFolder;
        RefreshControls();
        try
        {
            Outcome<CeSettings> read = await Task.Run(() => CeSettings.Read(folder));
            if (!GodotObject.IsInstanceValid(Root) || _app.Game.Target != GameTarget.OnslaughtCe || folder != _app.Game.CeUserFolder) return;
            _loadedFolder = folder;
            _snapshot = read.Value;
            _path.Text = _snapshot?.Path ?? folder;
            _result.Text = read.Message;
            _result.ThemeTypeVariation = read.Ok ? "Muted" : "Bad";
            UpdateCheck.SetPressedNoSignal(_snapshot?.UpdateCheck ?? true);
            RecordSessions.SetPressedNoSignal(_snapshot?.RecordSessions ?? false);
            _source.Text = _snapshot?.GameDirectory is { Length: > 0 } data ? "Original game data recorded by CE: " + data :
                "CE chooses its original game data when it starts. No folder is recorded in ce.ini.";
        }
        finally
        {
            _loading = false;
            if (GodotObject.IsInstanceValid(Root)) RefreshControls();
        }
    }

    internal void AskToSave()
    {
        if (Save.Disabled || _snapshot is null) return;
        Confirm.DialogText = $"Save {ChangeCount} launcher setting{(ChangeCount == 1 ? "" : "s")} to:\n{_snapshot.Path}\n\n" +
            $"The current ce.ini is backed up and verified in {_app.Backups.Folder} before it is replaced. " +
            "If it does not exist yet, a recovery note records that. Other keys are kept. " +
            AppServices.GameWriteGuidance + " " + AppServices.GameWriteChecks;
        Confirm.PopupCentered();
    }

    internal async Task<InstallReceipt> SaveAsync()
    {
        if (_snapshot is not CeSettings snapshot || !HasChanges || _loading || _saving || _app.Workspace.Busy ||
            _app.Game.Target != GameTarget.OnslaughtCe)
            return new InstallReceipt(false, "There are no CE settings ready to save.", _snapshot?.Path ?? "");
        if (_app.BackupFolderOrReport() is not string backup)
            return new InstallReceipt(false, "Choose a writable backup folder first.", snapshot.Path);
        _saving = true;
        RefreshControls();
        InstallReceipt result;
        try
        {
            result = await _app.Workspace.SaveCeSettingsAsync(snapshot, UpdateCheck.ButtonPressed, RecordSessions.ButtonPressed,
                backup, _app.GameRunning, _app.Game.CePackageRoot, _app.Game.CeOriginalRoot);
        }
        finally
        {
            _saving = false;
        }
        if (!GodotObject.IsInstanceValid(Root)) return result;
        if (result.Ok) await LoadAsync();
        _result.Text = result.Message + (result.BackupFolder is null ? "" : "\nBackup: " + result.BackupFolder);
        _result.ThemeTypeVariation = result.Ok ? "Good" : "Bad";
        _app.Status.Show(result.Message, result.Ok ? StatusKind.Success : StatusKind.Failure);
        RefreshControls();
        return result;
    }

    private void RefreshControls()
    {
        bool busy = _loading || _saving || _app.Workspace.Busy || _app.Game.Busy;
        bool available = _snapshot is not null && !busy && _app.Game.Target == GameTarget.OnslaughtCe;
        UpdateCheck.Disabled = !available;
        RecordSessions.Disabled = !available;
        Save.Disabled = !available || !HasChanges || _app.GameRunning();
        Undo.Text = HasChanges ? "Undo changes" : "Reload settings";
        Undo.Disabled = busy || _app.Game.Target != GameTarget.OnslaughtCe;
    }
}
