// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtCareerEditor.AppCore;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// The game's own cheats: it switches one on when a career's name contains its code (retail
/// CCareer::IsCheatActive, a case-sensitive substring test). A cheat copy is byte-identical to the
/// open career; only its name changes. Only codes seen working in the Steam game are offered.
/// </summary>
internal sealed class CheatsPage : Page
{
    private readonly CareerWorkspace _workspace;
    private readonly GameLibrary _game;
    private readonly StatusLine _status;
    private readonly Func<bool> _gameRunning;
    private readonly List<(CheatCode Cheat, CheckBox Box)> _choices = [];
    private readonly Label _empty, _preview, _switches, _resultText;
    private readonly PanelContainer _result;
    private readonly List<Control> _needsCareer = [];

    internal CheatsPage(CareerWorkspace workspace, GameLibrary game, StatusLine status, Node popups, Func<bool> gameRunning)
        : base("cheats", "Cheat names")
    {
        (_workspace, _game, _status, _gameRunning) = (workspace, game, status, gameRunning);
        (ScrollContainer scroll, VBoxContainer content) = Build.Scroller();
        Root = scroll;
        content.Add(Build.Notice("The game switches a cheat on when a career's name contains its code, and the case matters. " +
            "A cheat copy is byte-identical to your career; only the file name changes. Loading any career from the game's menu " +
            "also copies it over defaultoptions.bea.").Panel);
        _empty = content.Add(Build.Text("Open a career to make a cheat copy of it.", "Muted"));

        (PanelContainer cheats, VBoxContainer cheatBody) = Build.Card("Cheats seen working in the Steam game");
        foreach (CheatCode cheat in CheatCodeCatalog.All.Where(cheat => cheat.Evidence == CheatEvidenceLevel.SeenWorkingInGame))
        {
            VBoxContainer item = cheatBody.Add(Build.Column(2));
            CheckBox box = item.Add(new CheckBox { Text = $"{cheat.DisplayName}  —  {cheat.Code}" });
            box.Toggled += _ => ShowName();
            item.Add(Build.Text(cheat.WhatItDoes, "Muted")).CustomMinimumSize = new Vector2(0, 0);
            item.Add(Build.Text(cheat.WhatWeKnow, "Good"));
            _choices.Add((cheat, box));
        }
        _needsCareer.Add(content.Add(cheats));

        (PanelContainer naming, VBoxContainer nameBody) = Build.Card("Name");
        HBoxContainer nameRow = nameBody.Add(Build.Row(10));
        nameRow.Add(Build.Text("Career name", "Muted", wrap: false, width: 120));
        BaseName = nameRow.Add(new LineEdit { SizeFlagsHorizontal = Control.SizeFlags.ExpandFill, PlaceholderText = "Optional" });
        BaseName.TextChanged += _ => ShowName();
        _preview = nameBody.Add(Build.Text("", "Mono"));
        _switches = nameBody.Add(Build.Text("", "Muted"));
        _needsCareer.Add(content.Add(naming));

        (PanelContainer make, VBoxContainer makeBody) = Build.Card("Make the copy");
        HBoxContainer actions = makeBody.Add(Build.Row(10));
        WriteCopy = actions.Add(Build.Button("Write a verified copy to a folder…", "Primary", disabled: true));
        AddToGame = actions.Add(Build.Button("Add to the game's savegames…", "Caution", disabled: true));
        (_result, _resultText) = Build.Notice("");
        makeBody.Add(_result).Visible = false;
        _needsCareer.Add(content.Add(make));

        FolderDialog = popups.Add(Build.FilePicker("Choose a folder for the cheat copy", FileDialog.FileModeEnum.OpenDir));
        Confirm = popups.Add(new ConfirmationDialog { Title = "Add a cheat career to the game?", OkButtonText = "Back up, then add" });
        Confirm.GetLabel().AutowrapMode = TextServer.AutowrapMode.WordSmart;
        Confirm.MinSize = new Vector2I(560, 0);
        WriteCopy.Pressed += () => FolderDialog.PopupCenteredRatio(0.75f);
        FolderDialog.DirSelected += folder => _status.Track(WriteCopyAsync(folder));
        AddToGame.Pressed += AskToAdd;
        Confirm.Confirmed += () => _status.Track(ConfirmAddAsync());
        foreach (Control section in _needsCareer) section.Visible = false;
    }

    internal override Control Root { get; }
    internal override string Subtitle => "A byte-identical copy whose name switches on the game's own cheats";
    internal LineEdit BaseName { get; }
    internal Button WriteCopy { get; }
    internal Button AddToGame { get; }
    internal FileDialog FolderDialog { get; }
    internal ConfirmationDialog Confirm { get; }
    internal IReadOnlyList<CheckBox> Choices => _choices.Select(choice => choice.Box).ToArray();
    internal string Result => _resultText.Text;
    internal CheatSaveName Composed => CheatSaveNameComposer.Compose(BaseName.Text,
        _choices.Where(choice => choice.Box.ButtonPressed).Select(choice => choice.Cheat.Id));

    internal void ShowSession(SaveSession session)
    {
        _empty.Visible = false;
        foreach (Control section in _needsCareer) section.Visible = true;
        BaseName.Text = System.IO.Path.GetFileNameWithoutExtension(session.Path);
        foreach ((CheatCode _, CheckBox box) in _choices) box.SetPressedNoSignal(false);
        _result.Visible = false;
        ShowName();
    }

    internal override void Refresh() => ShowName();

    internal async Task<PublicationReceipt> WriteCopyAsync(string folder)
    {
        if (_workspace.Session is not SaveSession session || Problem() is string problem)
            return new PublicationReceipt(false, Problem() ?? "Open a career first.");
        string destination = System.IO.Path.Combine(folder, Composed.FileName);
        _status.Show("Writing and verifying the cheat copy…");
        PublicationReceipt receipt = await _workspace.PublishAsync(destination, session.CopyBytes());
        ShowResult(receipt.Ok ? $"Written and verified: {receipt.Output}" : receipt.Message +
            (receipt.MayHaveOutput ? $"\nA copy may exist at: {receipt.Output ?? destination}" : ""), receipt.Ok);
        _status.Show(receipt.Ok ? "Cheat copy written and verified." : receipt.Message, receipt.Ok ? StatusKind.Success : StatusKind.Failure);
        return receipt;
    }

    internal void AskToAdd()
    {
        if (_workspace.Session is not SaveSession session || _game.Folder is null || Problem() is not null) return;
        string backups = _game.Settings.Load().BackupFolder ?? "";
        Confirm.DialogText = $"Add {Composed.FileName} to your game's savegames folder, as a byte-identical copy of\n{session.Path}?\n\n" +
            $"First, every career and the options file are copied and verified into a new set in\n{backups}\n\n" +
            "Close Battle Engine Aquila before continuing; nothing is written while it runs.";
        Confirm.PopupCentered();
    }

    internal async Task<InstallReceipt> ConfirmAddAsync()
    {
        Confirm.Hide();
        if (_workspace.Session is not SaveSession session || _game.Folder is not GameFolder game)
            return new InstallReceipt(false, "Open a career and choose your game folder first.", "");
        string backups = _game.Settings.Load().BackupFolder ?? "";
        _status.Show("Backing up, then adding the cheat career…");
        InstallReceipt receipt = await _workspace.InstallAsync(game, session.Path, Composed.FileName, backups, _gameRunning);
        ShowResult(receipt.Message + (receipt.BackupFolder is string backup ? $"\nBackup: {backup}" : ""), receipt.Ok);
        _status.Show(receipt.Message, receipt.Ok ? StatusKind.Success : StatusKind.Failure);
        await _game.RescanAsync();
        return receipt;
    }

    private string? Problem()
    {
        CheatSaveName composed = Composed;
        if (composed.Problem is string problem) return problem;
        if (composed.ActiveCheatIds.Count == 0) return "Choose at least one cheat.";
        return GameInstaller.PortableNameProblem(composed.Name);
    }

    private void ShowName()
    {
        CheatSaveName composed = Composed;
        string? problem = Problem();
        _preview.Text = composed.FileName;
        _switches.Text = problem ?? "The game will switch on: " + string.Join(", ",
            CheatSaveNameComposer.ActiveCheatsIn(composed.Name).Select(cheat => cheat.DisplayName));
        _switches.ThemeTypeVariation = problem is null ? "Muted" : "Bad";
        bool ready = problem is null && _workspace.Session is not null && !_workspace.Busy;
        WriteCopy.Disabled = !ready;
        AddToGame.Disabled = !ready || _game.Folder is null || string.IsNullOrEmpty(_game.Settings.Load().BackupFolder);
        AddToGame.TooltipText = string.IsNullOrEmpty(_game.Settings.Load().BackupFolder)
            ? "Choose a backup folder on Install & backups first." : "";
    }

    private void ShowResult(string text, bool ok)
    {
        _result.Visible = true;
        _result.ThemeTypeVariation = ok ? "SuccessNotice" : "FailureNotice";
        _resultText.Text = text;
    }
}
