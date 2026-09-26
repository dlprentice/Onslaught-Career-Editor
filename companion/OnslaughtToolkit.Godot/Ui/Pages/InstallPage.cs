// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// The one page that writes into the game folder. Backups are verified copies in a folder the player
/// chooses; installing or restoring asks first, refuses while the game runs, and always backs up
/// every career and the options file before touching anything.
/// </summary>
internal sealed class InstallPage : Page
{
    private const string NewCareer = "A new career…";

    private readonly CareerWorkspace _workspace;
    private readonly GameLibrary _game;
    private readonly StatusLine _status;
    private readonly Func<bool> _gameRunning;
    private readonly VBoxContainer _sets;
    private readonly PanelContainer _backupResult, _installResult;
    private readonly Label _backupResultText, _installResultText, _noGame;
    private readonly HBoxContainer _newNameRow;
    private string _pendingSource = "", _pendingTarget = "";

    internal InstallPage(CareerWorkspace workspace, GameLibrary game, StatusLine status, Node popups, Func<bool> gameRunning)
        : base("install", "Install & backups")
    {
        (_workspace, _game, _status, _gameRunning) = (workspace, game, status, gameRunning);
        (ScrollContainer scroll, VBoxContainer content) = Build.Scroller();
        Root = scroll;
        content.Add(Build.Notice("This page writes into your game folder. Nothing is written until you confirm, never while " +
            "the game is running, and never before a verified backup of every career and the options file.", "CautionNotice").Panel);
        _noGame = content.Add(Build.Text("Choose your game folder on Home first.", "Muted"));

        (PanelContainer backups, VBoxContainer backupBody) = Build.Card("Backups");
        HBoxContainer folderRow = backupBody.Add(Build.Row(10));
        folderRow.Add(Build.Text("Backup folder", "Muted", wrap: false, width: 120));
        BackupFolder = folderRow.Add(new LineEdit
        {
            Editable = false, ThemeTypeVariation = "MonoField", SizeFlagsHorizontal = Control.SizeFlags.ExpandFill,
            PlaceholderText = "Choose a folder outside the game",
        });
        ChooseBackupFolder = folderRow.Add(Build.Button("Choose…"));
        BackUpNow = backupBody.Add(Build.Button("Back up all careers and options", "Primary", disabled: true));
        BackUpNow.SizeFlagsHorizontal = Control.SizeFlags.ShrinkBegin;
        (_backupResult, _backupResultText) = Build.Notice("");
        backupBody.Add(_backupResult).Visible = false;
        backupBody.Add(Build.Eyebrow("Backup sets in this folder"));
        _sets = backupBody.Add(Build.Column(8));
        content.Add(backups);

        (PanelContainer installCard, VBoxContainer installBody) = Build.Card("Install a copy into the game");
        installBody.Add(Build.Text("Put a verified copy into the game: a .bes career into savegames, or a .bea options file as " +
            "defaultoptions.bea. The file being replaced is compared with its fresh backup immediately before an atomic swap.", "Muted"));
        HBoxContainer sourceRow = installBody.Add(Build.Row(10));
        sourceRow.Add(Build.Text("File to install", "Muted", wrap: false, width: 120));
        Source = sourceRow.Add(new LineEdit
        {
            Editable = false, ThemeTypeVariation = "MonoField", SizeFlagsHorizontal = Control.SizeFlags.ExpandFill,
            PlaceholderText = "A verified copy (.bes or .bea)",
        });
        UseLastCopy = sourceRow.Add(Build.Button("Use last verified copy", disabled: true));
        ChooseSource = sourceRow.Add(Build.Button("Choose…"));
        HBoxContainer targetRow = installBody.Add(Build.Row(10));
        targetRow.Add(Build.Text("Goes to", "Muted", wrap: false, width: 120));
        Target = targetRow.Add(new OptionButton { CustomMinimumSize = new Vector2(280, 0) });
        _newNameRow = installBody.Add(Build.Row(10));
        _newNameRow.Add(Build.Text("New name", "Muted", wrap: false, width: 120));
        NewName = _newNameRow.Add(new LineEdit { PlaceholderText = "Career name", CustomMinimumSize = new Vector2(280, 0) });
        _newNameRow.Add(Build.Text(".bes", "MonoMuted", wrap: false));
        Install = installBody.Add(Build.Button("Install into the game…", "Caution", disabled: true));
        Install.SizeFlagsHorizontal = Control.SizeFlags.ShrinkBegin;
        (_installResult, _installResultText) = Build.Notice("");
        installBody.Add(_installResult).Visible = false;
        content.Add(installCard);

        FolderDialog = popups.Add(Build.FilePicker("Choose a backup folder", FileDialog.FileModeEnum.OpenDir));
        SourceDialog = popups.Add(Build.FilePicker("Choose a verified copy to install", FileDialog.FileModeEnum.OpenFile,
            "*.bes ; Career saves", "*.bea ; Options files"));
        Confirm = popups.Add(new ConfirmationDialog { Title = "Write into the game folder?", OkButtonText = "Back up, then write" });
        Confirm.GetLabel().AutowrapMode = TextServer.AutowrapMode.WordSmart;
        Confirm.MinSize = new Vector2I(560, 0);

        ChooseBackupFolder.Pressed += () => FolderDialog.PopupCenteredRatio(0.75f);
        FolderDialog.DirSelected += SetBackupFolder;
        BackUpNow.Pressed += () => _status.Track(BackUpAsync());
        UseLastCopy.Pressed += () => SetSource(_workspace.LastVerifiedOutput);
        ChooseSource.Pressed += () => SourceDialog.PopupCenteredRatio(0.75f);
        SourceDialog.FileSelected += SetSource;
        Target.ItemSelected += _ => UpdateActions();
        NewName.TextChanged += _ => UpdateActions();
        Install.Pressed += AskToInstall;
        Confirm.Confirmed += () => _status.Track(ConfirmAsync());
        _game.Changed += Refresh;
    }

    internal override Control Root { get; }
    internal override string Subtitle => "Verified backups, and writes into the game folder that you confirm";
    internal LineEdit BackupFolder { get; }
    internal Button ChooseBackupFolder { get; }
    internal Button BackUpNow { get; }
    internal LineEdit Source { get; }
    internal Button UseLastCopy { get; }
    internal Button ChooseSource { get; }
    internal OptionButton Target { get; }
    internal LineEdit NewName { get; }
    internal Button Install { get; }
    internal FileDialog FolderDialog { get; }
    internal FileDialog SourceDialog { get; }
    internal ConfirmationDialog Confirm { get; }
    internal string BackupResult => _backupResultText.Text;
    internal string InstallResult => _installResultText.Text;
    internal IReadOnlyList<Button> RestoreButtons => _sets.FindChildren("*", nameof(Button), true, false).OfType<Button>().ToArray();

    internal override void Refresh()
    {
        string? saved = _game.Settings.Load().BackupFolder;
        if (BackupFolder.Text.Length == 0 && saved is not null) BackupFolder.Text = saved;
        _noGame.Visible = _game.Folder is null;
        ShowTargets();
        ShowSets();
        UpdateActions();
    }

    internal void SetBackupFolder(string path)
    {
        BackupFolder.Text = path;
        CompanionSettings settings = _game.Settings.Load();
        settings.BackupFolder = path;
        _game.Settings.Save(settings);
        ShowSets();
        UpdateActions();
    }

    internal void SetSource(string path)
    {
        Source.Text = path;
        ShowTargets();
        UpdateActions();
    }

    internal async Task<BackupReceipt> BackUpAsync()
    {
        if (_game.Folder is not GameFolder game) return new BackupReceipt(false, "Choose your game folder on Home first.");
        _status.Show("Backing up every career and the options file…");
        BackupReceipt receipt = await _workspace.BackUpAsync(game, BackupFolder.Text);
        ShowResult(_backupResult, _backupResultText, receipt.Ok ? $"{receipt.Message}\n{receipt.Set?.Folder}" :
            receipt.Message + (receipt.PartialFolder is string partial ? $"\nPartial backup folder, kept for inspection: {partial}" : ""), receipt.Ok);
        _status.Show(receipt.Message, receipt.Ok ? StatusKind.Success : StatusKind.Failure);
        ShowSets();
        return receipt;
    }

    /// <summary>Opens the confirmation for the chosen install; nothing is written until it is confirmed.</summary>
    internal void AskToInstall()
    {
        if (ChosenTarget() is not string target || _game.Folder is not GameFolder game) return;
        PrepareConfirmation(Source.Text, target, game);
    }

    /// <summary>Opens the confirmation for restoring one backed-up file.</summary>
    internal void AskToRestore(BackupSet set, BackupFile file)
    {
        if (_game.Folder is not GameFolder game) return;
        PrepareConfirmation(Path.Combine(set.Folder, file.Name), file.Name, game);
    }

    internal async Task<InstallReceipt> ConfirmAsync()
    {
        if (_game.Folder is not GameFolder game || _pendingSource.Length == 0)
            return new InstallReceipt(false, "Nothing was chosen to write.", "");
        (string source, string target) = (_pendingSource, _pendingTarget);
        (_pendingSource, _pendingTarget) = ("", "");
        _status.Show("Backing up, checking and writing…");
        InstallReceipt receipt = await _workspace.InstallAsync(game, source, target, BackupFolder.Text, _gameRunning);
        ShowResult(_installResult, _installResultText, receipt.Message +
            (receipt.BackupFolder is string backup ? $"\nBackup: {backup}" : "") +
            (receipt.Sha256 is string sha ? $"\nSHA-256 {sha}" : "") +
            (receipt.MayHaveChanged ? "\nInspect the game folder before playing." : ""), receipt.Ok);
        _status.Show(receipt.Message, receipt.Ok ? StatusKind.Success : StatusKind.Failure);
        await _game.RescanAsync();
        ShowSets();
        return receipt;
    }

    private void PrepareConfirmation(string source, string target, GameFolder game)
    {
        (_pendingSource, _pendingTarget) = (source, target);
        string where = GameInstaller.Target(game, target) ?? target;
        bool replaces = File.Exists(where);
        Confirm.DialogText = $"{(replaces ? "Replace" : "Add")} {target} in your game folder with\n{source}?\n\n" +
            $"First, every career and the options file are copied and verified into a new set in\n{BackupFolder.Text}\n\n" +
            (replaces ? "The current file is compared with that backup immediately before an atomic swap. " : "") +
            "Close Battle Engine Aquila before continuing; nothing is written while it runs.";
        Confirm.PopupCentered();
    }

    private string? ChosenTarget()
    {
        if (Target.Selected < 0 || Target.ItemCount == 0) return null;
        string item = Target.GetItemText(Target.Selected);
        if (item != NewCareer) return item;
        string name = NewName.Text.Trim();
        return name.Length == 0 ? null : name + ".bes";
    }

    private void ShowTargets()
    {
        string previous = Target.Selected >= 0 && Target.ItemCount > 0 ? Target.GetItemText(Target.Selected) : "";
        Target.Clear();
        if (_game.Folder is GameFolder game && Source.Text.Length > 0)
        {
            if (Source.Text.EndsWith(".bea", StringComparison.OrdinalIgnoreCase))
            {
                Target.AddItem(GameInstaller.OptionsName);
            }
            else
            {
                foreach (GameFile career in game.Careers.Where(file => file.Supported)) Target.AddItem(career.Name);
                Target.AddItem(NewCareer);
            }
        }
        for (int index = 0; index < Target.ItemCount; index++)
        {
            if (Target.GetItemText(index) == previous) Target.Selected = index;
        }
        if (Target.Selected < 0 && Target.ItemCount > 0) Target.Selected = 0;
    }

    private void ShowSets()
    {
        _sets.Clear();
        if (BackupFolder.Text.Length == 0)
        {
            _sets.Add(Build.Text("Choose a backup folder to see its sets.", "Faint"));
            return;
        }
        IReadOnlyList<BackupSet> sets = Backups.List(BackupFolder.Text);
        if (sets.Count == 0) _sets.Add(Build.Text("No backup sets yet.", "Faint"));
        foreach (BackupSet set in sets.Take(20))
        {
            (PanelContainer panel, VBoxContainer body) = Build.Panel("Inset", 4);
            HBoxContainer head = body.Add(Build.Row(12));
            head.Add(Build.Text(set.Created.ToString("yyyy-MM-dd HH:mm:ss"), "Strong", wrap: false));
            head.Add(Build.Text($"{set.Files.Count} files", "Muted", wrap: false));
            Label folder = head.Add(Build.Text(Path.GetFileName(set.Folder), "MonoMuted", wrap: false, clip: true));
            folder.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
            folder.TooltipText = set.Folder;
            foreach (BackupFile file in set.Files)
            {
                HBoxContainer row = body.Add(Build.Row(12));
                Label name = row.Add(Build.Text(file.Name, "", wrap: false, clip: true));
                name.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
                row.Add(Build.Text(file.Sha256[..12] + "…", "MonoMuted", wrap: false));
                Button restore = row.Add(Build.Button("Restore…", "Caution", disabled: _game.Folder is null || _workspace.Busy));
                restore.Pressed += () => AskToRestore(set, file);
            }
            _sets.Add(panel);
        }
    }

    private void UpdateActions()
    {
        bool ready = _game.Folder is not null && !_workspace.Busy && !_game.Busy;
        BackUpNow.Disabled = !ready || BackupFolder.Text.Length == 0;
        UseLastCopy.Disabled = _workspace.LastVerifiedOutput.Length == 0;
        _newNameRow.Visible = Target.ItemCount > 0 && Target.GetItemText(Math.Max(0, Target.Selected)) == NewCareer;
        Install.Disabled = !ready || BackupFolder.Text.Length == 0 || Source.Text.Length == 0 || ChosenTarget() is null;
    }

    private static void ShowResult(PanelContainer panel, Label label, string text, bool ok)
    {
        panel.Visible = true;
        panel.ThemeTypeVariation = ok ? "SuccessNotice" : "FailureNotice";
        label.Text = text;
    }
}
