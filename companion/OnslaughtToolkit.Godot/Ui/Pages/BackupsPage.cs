// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// The safety net: where backups go, automatic backups, and every backup set with a way to put any file
/// back. Putting a file back is itself a write into the game, so it backs up the current files first.
/// </summary>
internal sealed class BackupsPage : Page
{
    private const int SetsShown = 30;

    private readonly AppServices _app;
    private readonly VBoxContainer _sets;
    private readonly Label _folder, _empty;
    private (BackupSet Set, BackupFile File)? _pending;

    internal BackupsPage(AppServices app) : base("backups", "Backups", "backups")
    {
        _app = app;
        (ScrollContainer scroll, VBoxContainer content) = Build.Scroller();
        Root = scroll;
        content.Add(Build.Text("Every change the companion makes to your game is backed up first. You can put any earlier version back.", "Lead"));

        (PanelContainer settings, VBoxContainer body) = Build.Card("Your backups", 10);
        Automatic = body.Add(new CheckBox { Text = "Back up automatically when the companion opens and after you play (only when something changed)" });
        Automatic.Toggled += on =>
        {
            CompanionSettings saved = _app.Game.Settings.Load();
            saved.AutoBackup = on;
            _app.Game.Settings.Save(saved);
            _app.Status.Show(on ? "Automatic backups are on." : "Automatic backups are off. Changes you make still back up first.");
        };
        _folder = body.Add(Build.Text("", "Muted"));
        HBoxContainer actions = body.Add(Build.Row(10));
        BackUpNow = actions.Add(Build.Button("Back up now", "Primary"));
        BackUpNow.Icon = Icons.Get("backups");
        OpenFolder = actions.Add(Build.Button("Open the folder"));
        OpenFolder.Icon = Icons.Get("open");
        ChooseFolder = actions.Add(Build.Button("Use another folder…", "Link"));
        content.Add(settings);

        (PanelContainer list, VBoxContainer listBody) = Build.Card("Backups, newest first", 10);
        _empty = listBody.Add(Build.Text("", "Muted"));
        _sets = listBody.Add(Build.Column(10));
        content.Add(list);

        FolderDialog = app.Popups.Add(Build.FilePicker("Choose a folder for backups", FileDialog.FileModeEnum.OpenDir));
        Confirm = app.Popups.Add(new ConfirmationDialog { Title = "Put a file back?", OkButtonText = "Back up and put back" });
        Confirm.GetLabel().AutowrapMode = TextServer.AutowrapMode.WordSmart;
        Confirm.MinSize = new Vector2I(560, 0);
        BackUpNow.Pressed += () => _app.Status.Track(BackUpAsync());
        OpenFolder.Pressed += () =>
        {
            if (_app.BackupFolderOrReport() is string folder) _app.OpenUrl(folder);
        };
        ChooseFolder.Pressed += () => FolderDialog.PopupCenteredRatio(0.75f);
        FolderDialog.DirSelected += SetBackupFolder;
        Confirm.Confirmed += () => _app.Status.Track(ConfirmAsync());
        _app.Game.Changed += Refresh;
    }

    internal override Control Root { get; }
    internal override string Subtitle => "Your safety net: every earlier version, ready to put back";
    internal CheckBox Automatic { get; }
    internal Button BackUpNow { get; }
    internal Button OpenFolder { get; }
    internal Button ChooseFolder { get; }
    internal FileDialog FolderDialog { get; }
    internal ConfirmationDialog Confirm { get; }
    internal IReadOnlyList<Button> RestoreButtons => _sets.FindChildren("*", nameof(Button), true, false).OfType<Button>().ToArray();

    internal override void Refresh()
    {
        Automatic.SetPressedNoSignal(_app.Game.Settings.Load().AutoBackup == true);
        _folder.Text = $"Kept in {_app.Backups.Folder}" + (_app.Backups.IsDefault ? " (the default folder)." : ".");
        BackUpNow.Disabled = _app.Game.Folder is null || _app.Workspace.Busy;
        ShowSets();
    }

    internal void SetBackupFolder(string path)
    {
        bool saved = _app.Backups.Choose(path);
        _app.Status.Show(saved ? $"Backups will go to {path}." : "That folder could not be remembered.", saved ? StatusKind.Success : StatusKind.Failure);
        Refresh();
    }

    internal async Task<BackupReceipt> BackUpAsync()
    {
        if (_app.Game.Folder is not GameFolder game) return new BackupReceipt(false, "Choose your game folder first.");
        if (_app.BackupFolderOrReport() is not string folder) return new BackupReceipt(false, "No backup folder.");
        _app.Status.Show("Backing up your careers and settings…");
        BackupReceipt receipt = await _app.Workspace.BackUpAsync(game, folder);
        _app.Status.Show(receipt.Ok ? $"Backed up {receipt.Set?.Files.Count ?? 0} files and checked every one." : receipt.Message,
            receipt.Ok ? StatusKind.Success : StatusKind.Failure);
        Refresh();
        return receipt;
    }

    /// <summary>Asks before putting a backed-up file back into the game.</summary>
    internal void AskToRestore(BackupSet set, BackupFile file)
    {
        if (_app.Game.Folder is null) return;
        _pending = (set, file);
        string what = Describe(file.Name);
        Confirm.DialogText = $"Put {what} back as it was {Build.When(set.Created)}?\n\nThe {what} in your game now is backed up first, " +
            "together with every other career and your settings, so you can undo this too. Nothing is written while the game is running.";
        Confirm.PopupCentered();
    }

    internal async Task<InstallReceipt> ConfirmAsync()
    {
        Confirm.Hide();
        if (_pending is not (BackupSet set, BackupFile file) || _app.Game.Folder is not GameFolder game)
            return new InstallReceipt(false, "Nothing was chosen to put back.", "");
        _pending = null;
        if (_app.BackupFolderOrReport() is not string folder) return new InstallReceipt(false, "No backup folder.", file.Name);
        _app.Status.Show("Backing up, then putting the file back…");
        InstallReceipt receipt = await _app.Workspace.InstallAsync(game, System.IO.Path.Combine(set.Folder, file.Name), file.Name, folder,
            _app.GameRunning, $"Before putting back {Describe(file.Name)} from {set.Created:d MMM HH:mm}");
        await _app.CatchUp();
        _app.Status.Show(receipt.Ok ? $"{Capitalised(Describe(file.Name))} is back as it was {Build.When(set.Created)}." : receipt.Message,
            receipt.Ok ? StatusKind.Success : StatusKind.Failure);
        Refresh();
        return receipt;
    }

    private void ShowSets()
    {
        _sets.Clear();
        IReadOnlyList<BackupSet> sets = Backups.List(_app.Backups.Folder);
        _empty.Text = sets.Count == 0 ? "No backups yet. Back up now, or turn on automatic backups; every change you save into your " +
            "game also backs up first." : "";
        _empty.Visible = sets.Count == 0;
        foreach (BackupSet set in sets.Take(SetsShown))
        {
            (PanelContainer panel, VBoxContainer body) = Build.Panel("Inset", 6);
            HBoxContainer head = body.Add(Build.Row(12));
            head.Add(Build.Text(Capitalised(Build.When(set.Created)), "Strong", wrap: false));
            Label reason = head.Add(Build.Text(set.Reason ?? "Backup", "Muted", wrap: false, clip: true));
            reason.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
            head.Add(Build.Text(Build.Count(set.Files.Count, "file"), "Faint", wrap: false));
            foreach (BackupFile file in set.Files)
            {
                HBoxContainer row = body.Add(Build.Row(12));
                Label name = row.Add(Build.Text(Capitalised(Describe(file.Name)), "", wrap: false, clip: true));
                name.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
                name.TooltipText = System.IO.Path.Combine(set.Folder, file.Name);
                Button restore = row.Add(Build.Button("Put back", "Caution", disabled: _app.Game.Folder is null || _app.Workspace.Busy));
                restore.Icon = Icons.Get("restore");
                restore.Pressed += () => AskToRestore(set, file);
            }
            panel.TooltipText = set.Folder;
            _sets.Add(panel);
        }
        if (sets.Count > SetsShown)
            _sets.Add(Build.Text($"{sets.Count - SetsShown} older backups are in the folder too.", "Faint"));
    }

    private static string Describe(string file) =>
        string.Equals(file, GameInstaller.OptionsName, StringComparison.OrdinalIgnoreCase) ? "the game's default settings"
            : System.IO.Path.GetFileNameWithoutExtension(file);

    private static string Capitalised(string text) => text.Length == 0 ? text : char.ToUpperInvariant(text[0]) + text[1..];
}
