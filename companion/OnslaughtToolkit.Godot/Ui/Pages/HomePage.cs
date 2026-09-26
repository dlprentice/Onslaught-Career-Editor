// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>The landing page: the game folder, the careers it holds and how the companion keeps files safe.</summary>
internal sealed class HomePage : Page
{
    private readonly GameLibrary _game;
    private readonly StatusLine _status;
    private readonly Func<string, Task> _openCareer;
    private readonly VBoxContainer _careerList;
    private readonly Label _folderPath, _folderSource, _identity, _inventory, _optionsLine;
    private readonly PanelContainer _careersCard, _optionsCard;

    internal HomePage(GameLibrary game, StatusLine status, Node popups, Action showOpenDialog, Func<string, Task> openCareer)
        : base("home", "Home")
    {
        (_game, _status, _openCareer) = (game, status, openCareer);
        (ScrollContainer scroll, VBoxContainer content) = Build.Scroller();
        Root = scroll;

        (PanelContainer folderCard, VBoxContainer folder) = Build.Card("Game folder", 6);
        _folderPath = folder.Add(Build.Text("Looking for the game…", "Mono"));
        _folderSource = folder.Add(Build.Text("", "Muted"));
        _identity = folder.Add(Build.Text("", "Muted"));
        _inventory = folder.Add(Build.Text("", "Faint"));
        HBoxContainer folderActions = folder.Add(Build.Row(10));
        ChooseFolder = folderActions.Add(Build.Button("Choose game folder…", tooltip: "The folder that contains BEA.exe and data."));
        Rescan = folderActions.Add(Build.Button("Rescan"));
        OpenOther = folderActions.Add(Build.Button("Open a career from elsewhere…", "Link"));
        content.Add(folderCard);

        (_careersCard, VBoxContainer careers) = Build.Card("Careers in this game");
        careers.Add(Build.Text("The game keeps careers in its savegames folder. Opening one is read-only.", "Muted"));
        _careerList = careers.Add(Build.Column(6));
        content.Add(_careersCard);

        (_optionsCard, VBoxContainer options) = Build.Card("Options file");
        _optionsLine = options.Add(Build.Text("", "Muted"));
        options.Add(Build.Text("The game reads defaultoptions.bea at startup. Loading a career from the game's menu also " +
            "copies that career over this file (seen in the game and in its original code).", "Faint"));
        content.Add(_optionsCard);

        (PanelContainer safety, VBoxContainer rules) = Build.Card("How your files stay safe", 6);
        foreach (string rule in new[]
        {
            "Careers open read-only; the original is never modified.",
            "Changes go to a new file that is reopened and compared with the preview before it is offered.",
            "An edit never replaces a file. Only Install & backups writes into the game folder: after you confirm, never " +
                "while the game runs, and only after a verified backup of every career and the options file.",
            "Each value says how we know what it means: seen in the game, read from the game's code, or unproven.",
        })
        {
            rules.Add(Build.Text("—  " + rule, "Muted"));
        }
        content.Add(safety);

        FolderDialog = popups.Add(Build.FilePicker("Choose the game folder", FileDialog.FileModeEnum.OpenDir));
        ChooseFolder.Pressed += () => FolderDialog.PopupCenteredRatio(0.75f);
        FolderDialog.DirSelected += path => _status.Track(ChooseAsync(path));
        Rescan.Pressed += () => _status.Track(_game.RescanAsync());
        OpenOther.Pressed += showOpenDialog;
        _game.Changed += ShowGame;
        ShowGame();
    }

    internal override Control Root { get; }
    internal override string Subtitle => _game.Folder is GameFolder folder
        ? $"{folder.Careers.Count} career{(folder.Careers.Count == 1 ? "" : "s")} in your game folder"
        : "Careers, verified copies and the game's own media";

    internal Button ChooseFolder { get; }
    internal Button Rescan { get; }
    internal Button OpenOther { get; }
    internal FileDialog FolderDialog { get; }
    internal IReadOnlyList<Button> OpenButtons => _careerList.GetChildren().OfType<HBoxContainer>()
        .SelectMany(row => row.GetChildren().OfType<Button>()).ToArray();

    internal async Task ChooseAsync(string path)
    {
        var chosen = await _game.ChooseAsync(path);
        _status.Show(chosen.Message, chosen.Ok ? StatusKind.Success : StatusKind.Failure);
    }

    internal void ShowGame()
    {
        ChooseFolder.Disabled = Rescan.Disabled = _game.Busy;
        _careerList.Clear();
        if (_game.Folder is not GameFolder folder)
        {
            _folderPath.Text = _game.Busy ? "Looking for the game…" : "No game folder found.";
            _folderSource.Text = _game.Busy ? "" : "Choose the folder that contains BEA.exe and data. Career tools still work " +
                "on any career you open.";
            _identity.Text = _inventory.Text = "";
            _careersCard.Visible = _optionsCard.Visible = false;
            return;
        }
        _folderPath.Text = folder.Root;
        _folderSource.Text = folder.Source;
        (_identity.Text, _identity.ThemeTypeVariation) = folder.Executable.State switch
        {
            ExecutableState.Retail => ("●  BEA.exe is the Steam release, byte for byte (SHA-256 checked).", "Good"),
            ExecutableState.Different => ("●  BEA.exe differs from the Steam release: patched or another version. Career tools " +
                "work the same; nothing is assumed about how it behaves.", "Warn"),
            ExecutableState.Missing => ("●  No BEA.exe was found.", "Bad"),
            _ => ("●  BEA.exe could not be read.", "Bad"),
        };
        List<string> inventory = [$"{folder.Careers.Count} career{(folder.Careers.Count == 1 ? "" : "s")}"];
        if (folder.Options is not null) inventory.Add("options file");
        if (folder.Languages.Count > 0) inventory.Add("text: " + string.Join(", ", folder.Languages));
        if (folder.MusicTracks > 0) inventory.Add($"{folder.MusicTracks} music track{(folder.MusicTracks == 1 ? "" : "s")}");
        if (folder.VoiceLines > 0) inventory.Add($"{folder.VoiceLines:N0} voice lines");
        if (folder.Cutscenes > 0) inventory.Add($"{folder.Cutscenes} cutscenes");
        _inventory.Text = string.Join("  ·  ", inventory);

        _careersCard.Visible = _optionsCard.Visible = true;
        if (folder.Careers.Count == 0)
            _careerList.Add(Build.Text("No careers yet. The game writes one when you save a career in it.", "Faint"));
        foreach (GameFile career in folder.Careers)
        {
            HBoxContainer row = _careerList.Add(Build.Row(14));
            Label name = row.Add(Build.Text(System.IO.Path.GetFileNameWithoutExtension(career.Name), "Strong", wrap: false, clip: true));
            name.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
            name.TooltipText = career.Path;
            row.Add(Build.Text(career.Modified == default ? "" : career.Modified.ToString("yyyy-MM-dd HH:mm"), "MonoMuted", wrap: false));
            row.Add(Build.Text(career.Problem ?? "supported", career.Supported ? "Faint" : "Warn", wrap: false));
            Button open = row.Add(Build.Button("Open", career.Supported ? "Primary" : "", disabled: !career.Supported));
            string path = career.Path;
            open.Pressed += () => _status.Track(_openCareer(path));
        }
        _optionsLine.Text = folder.Options is GameFile options
            ? $"{options.Name}  ·  {(options.Supported ? "supported" : options.Problem)}  ·  " +
              (options.Modified == default ? "" : options.Modified.ToString("yyyy-MM-dd HH:mm"))
            : "No defaultoptions.bea yet; the game writes it when it saves settings.";
    }
}
