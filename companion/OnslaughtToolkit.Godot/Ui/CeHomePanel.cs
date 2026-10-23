// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>CE package selection and an explicitly requested, read-only signed release check on Home.</summary>
internal sealed class CeHomePanel
{
    private readonly AppServices _app;
    private readonly Label _launcher, _version, _userFolder, _update;
    private readonly Func<string?, CancellationToken, Task<CeUpdateState>> _check;
    private readonly CancellationTokenSource _lifetime = new();
    private bool _checking;

    internal CeHomePanel(AppServices app, Func<string?, CancellationToken, Task<CeUpdateState>>? check = null)
    {
        _app = app;
        _check = check ?? CeUpdateFeed.CheckAsync;
        (PanelContainer panel, VBoxContainer body) = Build.Card("CE launcher", 8);
        Root = panel;
        _version = body.Add(Build.Text("", "Strong"));
        _launcher = body.Add(Build.Text("", "Muted"));
        _userFolder = body.Add(Build.Text("", "Muted"));
        HBoxContainer actions = body.Add(Build.Row(12));
        ChooseLauncher = actions.Add(Build.Button("Choose CE launcher…", "", "Choose onslaught-ce on Linux, or onslaught-ce.exe on Windows."));
        CheckUpdates = actions.Add(Build.Button("Check public updates", "", "Read and verify CE's public release information; no update is installed."));
        _update = body.Add(Build.Text("Updates have not been checked. The CE launcher handles installation.", "Muted"));
        body.Add(Build.Text("Checks read latest.json and its signature from github.com/dlprentice/onslaught-ce/releases. " +
            "No saves, paths or installed version are sent.", "Faint"));
        LauncherDialog = app.Popups.Add(Build.FilePicker("Choose the Onslaught CE launcher", FileDialog.FileModeEnum.OpenFile));
        ChooseLauncher.Pressed += () => LauncherDialog.PopupCenteredRatio(0.75f);
        LauncherDialog.FileSelected += path => _app.Status.Track(ChooseAsync(path));
        CheckUpdates.Pressed += () => _app.Status.Track(CheckUpdatesAsync());
        Root.TreeExiting += () => _lifetime.Cancel();
        _app.Game.Changed += Refresh;
        _app.Workspace.Changed += Refresh;
        Refresh();
    }

    internal Control Root { get; }
    internal Button ChooseLauncher { get; }
    internal Button CheckUpdates { get; }
    internal FileDialog LauncherDialog { get; }
    internal string UpdateText => _update.Text;
    internal string VersionText => _version.Text;

    internal void Refresh()
    {
        Root.Visible = _app.Game.Target == GameTarget.OnslaughtCe;
        _version.Text = _app.Game.CeVersionMessage;
        _launcher.Text = _app.Game.Ce is CeInstallation ce ? "Launcher: " + ce.LauncherPath :
            "CE was not found automatically. Choose its launcher wherever you extracted the package.";
        _userFolder.Text = "Saves and settings: " + (_app.Game.CeUserFolder.Length > 0 ? _app.Game.CeUserFolder : "No valid CE user folder");
        ChooseLauncher.Disabled = _app.Game.Busy || _app.Workspace.Busy;
        CheckUpdates.Disabled = _checking || _app.Game.Busy;
    }

    internal async Task ChooseAsync(string path)
    {
        Outcome<CeInstallation> selected = await _app.Game.ChooseCeAsync(path);
        if (!GodotObject.IsInstanceValid(Root)) return;
        _app.Status.Show(selected.Message, selected.Ok ? StatusKind.Success : StatusKind.Failure);
        Refresh();
    }

    internal async Task CheckUpdatesAsync()
    {
        if (_checking || _app.Game.Busy) return;
        _checking = true;
        _update.Text = "Reading and verifying the public release information…";
        Refresh();
        string? installed = _app.Game.CeVersion?.Version;
        try
        {
            CeUpdateState result = await _check(installed, _lifetime.Token);
            if (!GodotObject.IsInstanceValid(Root) || _lifetime.IsCancellationRequested) return;
            // A different launcher may have been selected during the request: do not compare it to the old version.
            _update.Text = installed != _app.Game.CeVersion?.Version && result.Verified
                ? $"Signed release: CE {result.LatestVersion}. Check again to compare the selected launcher."
                : result.Message;
            _update.ThemeTypeVariation = result.Verified ? "Good" : "Bad";
        }
        finally
        {
            _checking = false;
            if (GodotObject.IsInstanceValid(Root)) Refresh();
        }
    }
}
