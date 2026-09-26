// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtCareerEditor.AppCore;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// The game's own cheats: it switches one on when a career's name contains its code (retail
/// CCareer::IsCheatActive, a case-sensitive substring test). The companion adds a byte-identical copy of
/// the open career under a name carrying the chosen codes; the career itself never changes. Only codes
/// seen working in the Steam game are offered.
/// </summary>
internal sealed class CheatsPage : Page
{
    private readonly AppServices _app;
    private readonly List<(CheatCode Cheat, CheckBox Box)> _choices = [];
    private readonly Label _intro, _preview, _switches, _resultText;
    private readonly PanelContainer _result;
    private readonly CareerCards _choose;
    private readonly List<Control> _needsCareer = [];

    internal CheatsPage(AppServices app) : base("cheats", "Cheats", "cheats")
    {
        _app = app;
        (ScrollContainer scroll, VBoxContainer content) = Build.Scroller();
        Root = scroll;
        _intro = content.Add(Build.Text("", "Lead"));
        _choose = new CareerCards(app);
        content.Add(_choose.Root);

        (PanelContainer cheats, VBoxContainer cheatBody) = Build.Card("Cheats that work in the Steam game");
        cheatBody.Add(Build.Text("The game switches a cheat on when a career's name contains its code, capital letters included.", "Muted"));
        foreach (CheatCode cheat in CheatCodeCatalog.All.Where(cheat => cheat.Evidence == CheatEvidenceLevel.SeenWorkingInGame))
        {
            (PanelContainer panel, VBoxContainer item) = Build.Panel("Inset", 4);
            CheckBox box = item.Add(new CheckBox { Text = $"{cheat.DisplayName}   ({cheat.Code})" });
            box.Toggled += _ => ShowName();
            item.Add(Build.Text(cheat.WhatItDoes));
            item.Add(Build.Text(cheat.WhatWeKnow, "Faint"));
            cheatBody.Add(panel);
            _choices.Add((cheat, box));
        }
        _needsCareer.Add(content.Add(cheats));

        (PanelContainer naming, VBoxContainer nameBody) = Build.Card("The new career");
        HBoxContainer nameRow = nameBody.Add(Build.Row(10));
        nameRow.Add(Build.Text("Name", "Muted", wrap: false, width: 80));
        BaseName = nameRow.Add(new LineEdit { SizeFlagsHorizontal = Control.SizeFlags.ExpandFill, PlaceholderText = "Optional", MaxLength = 80 });
        BaseName.TextChanged += _ => ShowName();
        _preview = nameBody.Add(Build.Text("", "CardTitle"));
        _switches = nameBody.Add(Build.Text("", "Muted"));
        HBoxContainer actions = nameBody.Add(Build.Row(10));
        AddToGame = actions.Add(Build.Button("Add to your game", "Primary", disabled: true));
        AddToGame.Icon = Icons.Get("save");
        WriteCopy = actions.Add(Build.Button("Save a copy somewhere else…", "Link", disabled: true));
        (_result, _resultText) = Build.Notice("");
        nameBody.Add(_result).Visible = false;
        _needsCareer.Add(content.Add(naming));

        FolderDialog = app.Popups.Add(Build.FilePicker("Choose a folder for the cheat copy", FileDialog.FileModeEnum.OpenDir));
        Confirm = app.Popups.Add(Build.Confirm("Add a cheat career to your game?", "Back up and add"));
        WriteCopy.Pressed += () => FolderDialog.PopupCenteredRatio(0.75f);
        FolderDialog.DirSelected += folder => _app.Status.Track(WriteCopyAsync(folder));
        AddToGame.Pressed += AskToAdd;
        Confirm.Confirmed += () => _app.Status.Track(ConfirmAddAsync());
        ShowEmpty();
    }

    internal override Control Root { get; }
    internal override string Subtitle => "A copy of your career whose name switches cheats on";
    internal LineEdit BaseName { get; }
    internal Button WriteCopy { get; }
    internal Button AddToGame { get; }
    internal FileDialog FolderDialog { get; }
    internal ConfirmationDialog Confirm { get; }
    internal IReadOnlyList<CheckBox> Choices => _choices.Select(choice => choice.Box).ToArray();
    internal string Result => _resultText.Text;
    internal string Switches => _switches.Text;
    internal CheatSaveName Composed => CheatSaveNameComposer.Compose(BaseName.Text,
        _choices.Where(choice => choice.Box.ButtonPressed).Select(choice => choice.Cheat.Id));

    internal void ShowSession(SaveSession session)
    {
        foreach (Control section in _needsCareer) section.Visible = true;
        _choose.Root.Visible = false;
        string name = System.IO.Path.GetFileNameWithoutExtension(session.Path);
        _intro.Text = $"Pick cheats and the companion adds a copy of {name} whose name switches them on. {name} itself doesn't change.";
        BaseName.Text = name;
        foreach ((CheatCode _, CheckBox box) in _choices) box.SetPressedNoSignal(false);
        _result.Visible = false;
        ShowName();
    }

    internal override void Refresh()
    {
        if (_app.Workspace.Session is null) ShowEmpty();
        else ShowName();
    }

    /// <summary>Publishes a byte-identical copy under the composed name in a folder outside the game.</summary>
    internal async Task<PublicationReceipt> WriteCopyAsync(string folder)
    {
        if (_app.Workspace.Session is not SaveSession session || Problem(checkGame: false) is string problem)
            return new PublicationReceipt(false, Problem(checkGame: false) ?? "Open a career first.");
        string destination = System.IO.Path.Combine(folder, Composed.FileName);
        _app.Status.Show("Saving the cheat copy…");
        PublicationReceipt receipt = await _app.Workspace.PublishAsync(destination, session.CopyBytes());
        ShowResult(receipt.Ok ? $"Saved {Composed.Name} to {receipt.Output}. It was read back and matches your career byte for byte."
            : receipt.Message + (receipt.MayHaveOutput ? $"\nA copy may exist at: {receipt.Output ?? destination}" : ""), receipt.Ok);
        _app.Status.Show(receipt.Ok ? "Cheat copy saved and checked." : receipt.Message, receipt.Ok ? StatusKind.Success : StatusKind.Failure);
        return receipt;
    }

    internal void AskToAdd()
    {
        if (_app.Workspace.Session is not SaveSession session || _app.Game.Folder is null || Problem(checkGame: true) is not null) return;
        string switches = string.Join(", ", CheatSaveNameComposer.ActiveCheatsIn(Composed.Name).Select(cheat => cheat.DisplayName));
        Confirm.DialogText = $"Add {Composed.Name} to your game?\n\nIt is a copy of {System.IO.Path.GetFileNameWithoutExtension(session.Path)} " +
            $"whose name switches on: {switches}.\n\nFirst, every career and your settings are backed up to {_app.Backups.Folder}. " +
            "Nothing is written while the game is running.";
        Confirm.PopupCentered();
    }

    internal async Task<InstallReceipt> ConfirmAddAsync()
    {
        Confirm.Hide();
        if (_app.Workspace.Session is not SaveSession session || _app.Game.Folder is not GameFolder game)
            return new InstallReceipt(false, "Open a career and choose your game folder first.", "");
        if (_app.BackupFolderOrReport() is not string backups) return new InstallReceipt(false, "No backup folder.", Composed.FileName);
        string name = Composed.Name;
        _app.Status.Show("Backing up, then adding the cheat career…");
        InstallReceipt receipt = await _app.Workspace.InstallBytesAsync(game, Composed.FileName, session.CopyBytes(), backups,
            _app.GameRunning, null, $"Before adding {name}");
        ShowResult(receipt.Ok ? $"{name} is now in your game's career list. Load it in the game to play with the cheats on." : receipt.Message,
            receipt.Ok);
        _app.Status.Show(receipt.Ok ? $"{name} added to your game." : receipt.Message, receipt.Ok ? StatusKind.Success : StatusKind.Failure);
        await _app.Game.RescanAsync();
        ShowName();
        return receipt;
    }

    private string? Problem(bool checkGame)
    {
        CheatSaveName composed = Composed;
        if (composed.Problem is string problem) return problem;
        if (composed.ActiveCheatIds.Count == 0) return "Choose at least one cheat.";
        if (GameInstaller.PortableNameProblem(composed.Name) is string nameProblem) return nameProblem;
        return checkGame ? _app.CareerNameProblem(composed.Name) : null;
    }

    private void ShowName()
    {
        CheatSaveName composed = Composed;
        string? problem = Problem(checkGame: true);
        _preview.Text = composed.Name.Length > 0 ? composed.Name : "—";
        _switches.Text = problem ?? "The game will switch on: " + string.Join(", ",
            CheatSaveNameComposer.ActiveCheatsIn(composed.Name).Select(cheat => cheat.DisplayName));
        _switches.ThemeTypeVariation = problem is null ? "Good" : "Muted";
        bool ready = _app.Workspace.Session is not null && !_app.Workspace.Busy;
        WriteCopy.Disabled = !ready || Problem(checkGame: false) is not null;
        AddToGame.Disabled = !ready || problem is not null || _app.Game.Folder is null;
        AddToGame.TooltipText = _app.Game.Folder is null ? "Choose your game folder on Home first." : "";
    }

    private void ShowEmpty()
    {
        foreach (Control section in _needsCareer) section.Visible = false;
        _intro.Text = "Choose the career to copy with cheats. Opening it only reads it.";
        _choose.Root.Visible = true;
        _choose.Show();
    }

    private void ShowResult(string text, bool ok)
    {
        _result.Visible = true;
        _result.ThemeTypeVariation = ok ? "SuccessNotice" : "FailureNotice";
        _resultText.Text = text;
    }
}
