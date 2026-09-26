// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// The front page: the game with its own art and a Play button, the player's careers, the safety net
/// (automatic backups and the promises the companion keeps) and ways into the rest of the app.
/// </summary>
internal sealed class HomePage : Page
{
    private readonly AppServices _app;
    private readonly TextureRect _art;
    private readonly Emblem _emblem;
    private readonly Label _heroStatus, _folderLine, _backupLine;
    private readonly PanelContainer _askBackups, _backupsOn;
    private readonly GridContainer _columns;
    private readonly SaveChoice _addChoice;
    private string _addSource = "";

    internal HomePage(AppServices app) : base("home", "Home", "home")
    {
        _app = app;
        (ScrollContainer scroll, VBoxContainer content) = Build.Scroller(18);
        Root = scroll;

        // The banner: the Battle Engine render from the game's manual, shaded so the words stay readable.
        PanelContainer hero = content.Add(new PanelContainer { ThemeTypeVariation = "Hero", ClipContents = true,
            CustomMinimumSize = new Vector2(0, 250) });
        Control stage = hero.Add(new Control { MouseFilter = Control.MouseFilterEnum.Ignore });
        _art = stage.Add(new TextureRect
        {
            ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize, StretchMode = TextureRect.StretchModeEnum.KeepAspectCovered,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        });
        _art.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        _emblem = stage.Add(new Emblem { CustomMinimumSize = new Vector2(150, 150), Modulate = new Color(1, 1, 1, 0.5f) });
        _emblem.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.CenterRight, Control.LayoutPresetMode.KeepSize, 48);
        TextureRect shade = stage.Add(new TextureRect
        {
            Texture = Shade(), ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize, StretchMode = TextureRect.StretchModeEnum.Scale,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        });
        shade.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        MarginContainer words = stage.Add(Build.Margin(34, 30, 34, 28));
        words.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        VBoxContainer heroColumn = words.Add(Build.Column(6));
        heroColumn.Add(Build.Eyebrow("Your game"));
        heroColumn.Add(Build.Text("Battle Engine Aquila", "HeroTitle", wrap: false));
        _heroStatus = heroColumn.Add(Build.Text("Looking for your game…", "HeroText"));
        _heroStatus.CustomMinimumSize = new Vector2(360, 0);
        _heroStatus.SizeFlagsHorizontal = Control.SizeFlags.ShrinkBegin;
        heroColumn.Add(Build.Spacer(0, expand: true));
        HBoxContainer heroActions = heroColumn.Add(Build.Row(10));
        Play = heroActions.Add(Build.Button("Play", "Primary", "Starts Battle Engine Aquila through Steam."));
        Play.Icon = Icons.Get("play");
        ChooseFolder = heroActions.Add(Build.Button("Choose game folder…", "", "The folder that contains BEA.exe and the data folder."));
        ChooseFolder.Icon = Icons.Get("folder");

        _columns = content.Add(new GridContainer { Columns = 2 });
        _columns.AddThemeConstantOverride("h_separation", 18);
        _columns.AddThemeConstantOverride("v_separation", 18);
        _columns.Resized += () => _columns.Columns = _columns.Size.X >= 900 ? 2 : 1;

        (PanelContainer careersCard, VBoxContainer careers) = Build.Card("Your careers", 12);
        careersCard.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        careersCard.SizeFlagsStretchRatio = 1.4f;
        careers.Add(Build.Text("Open a career to see its missions and Goodies, change it, or add cheats. Opening only reads it.", "Muted"));
        Careers = new CareerCards(app);
        careers.Add(Careers.Root);
        HBoxContainer careerLinks = careers.Add(Build.Row(16));
        AddCareer = careerLinks.Add(Build.Button("Add a career file to your game…", "Link",
            "Put a career you have as a file (from a friend, or a backup of your own) into the game's career list."));
        OpenFile = careerLinks.Add(Build.Button("Open a career file…", "Link", "Look at a career file anywhere on your computer, read-only."));
        _columns.Add(careersCard);

        VBoxContainer side = _columns.Add(Build.Column(18));
        side.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        (PanelContainer safety, VBoxContainer safetyBody) = Build.Card("Your safety net", 10);
        (_askBackups, VBoxContainer ask) = Build.Panel("CautionNotice", 8);
        ask.Add(Build.Text("Keep automatic backups?", "Strong"));
        ask.Add(Build.Text("Each time the companion opens, it copies your careers and settings to a backup folder if anything " +
            "changed. Nothing is ever deleted.", "Muted"));
        HBoxContainer askActions = ask.Add(Build.Row(10));
        TurnOnBackups = askActions.Add(Build.Button("Turn on automatic backups", "Primary"));
        NotNow = askActions.Add(Build.Button("Not now"));
        safetyBody.Add(_askBackups);
        (_backupsOn, VBoxContainer on) = Build.Panel("Inset", 8);
        _backupLine = on.Add(Build.Text("", "Muted"));
        HBoxContainer backupActions = on.Add(Build.Row(10));
        BackUpNow = backupActions.Add(Build.Button("Back up now"));
        BackUpNow.Icon = Icons.Get("backups");
        Button seeBackups = backupActions.Add(Build.Button("See backups", "Link"));
        seeBackups.Pressed += () => _app.Navigate("backups");
        safetyBody.Add(_backupsOn);
        foreach (string promise in new[]
        {
            "Nothing in your game changes without a backup first.",
            "Nothing is written while the game is running.",
            "Any earlier version can be put back from Backups.",
        })
        {
            HBoxContainer line = safetyBody.Add(Build.Row(10));
            line.Add(new TextureRect
            {
                Texture = Icons.Get("check"), ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
                StretchMode = TextureRect.StretchModeEnum.KeepAspectCentered, CustomMinimumSize = new Vector2(18, 18),
                Modulate = Palette.Good, SizeFlagsVertical = Control.SizeFlags.ShrinkCenter,
            });
            line.Add(Build.Text(promise));
        }
        side.Add(safety);

        (PanelContainer explore, VBoxContainer exploreBody) = Build.Card("Explore", 10);
        GridContainer tiles = exploreBody.Add(new GridContainer { Columns = 2 });
        tiles.AddThemeConstantOverride("h_separation", 10);
        tiles.AddThemeConstantOverride("v_separation", 10);
        foreach ((string key, string label, string icon) in new[]
        {
            ("goodies", "Goodies", "goodies"), ("lore", "Lore", "lore"), ("music", "Music & voices", "music"),
        })
        {
            Button tile = tiles.Add(Build.Button(label));
            tile.Icon = Icons.Get(icon);
            tile.Alignment = HorizontalAlignment.Left;
            tile.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
            tile.Pressed += () => _app.Navigate(key);
        }
        Manual = tiles.Add(Build.Button("The game's manual", "", "Opens the manual that came with your game, in your browser."));
        Manual.Icon = Icons.Get("book");
        Manual.Alignment = HorizontalAlignment.Left;
        Manual.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        side.Add(explore);

        _folderLine = content.Add(Build.Text("", "Faint"));

        FolderDialog = app.Popups.Add(Build.FilePicker("Choose the game folder", FileDialog.FileModeEnum.OpenDir));
        OpenDialog = app.Popups.Add(Build.FilePicker("Open a career file", FileDialog.FileModeEnum.OpenFile, "*.bes ; Career files"));
        AddDialog = app.Popups.Add(Build.FilePicker("Choose a career file to add", FileDialog.FileModeEnum.OpenFile, "*.bes ; Career files"));
        _addChoice = new SaveChoice(app);
        _addChoice.Chosen += (_, name) => _app.Status.Track(AddCareerAsync(name));

        Play.Pressed += () =>
        {
            _app.OpenUrl($"steam://rungameid/{SteamLibraries.AppId}");
            _app.Status.Show("Asking Steam to start Battle Engine Aquila…");
        };
        ChooseFolder.Pressed += () => FolderDialog.PopupCenteredRatio(0.75f);
        FolderDialog.DirSelected += path => _app.Status.Track(ChooseAsync(path));
        OpenFile.Pressed += () => OpenDialog.PopupCenteredRatio(0.75f);
        OpenDialog.FileSelected += path => _app.Status.Track(_app.OpenCareer(path));
        AddCareer.Pressed += () => AddDialog.PopupCenteredRatio(0.75f);
        AddDialog.FileSelected += AskToAdd;
        Manual.Pressed += () =>
        {
            if (GameArt.Manual(_app.Game.Folder?.Root) is string manual) _app.OpenUrl(manual);
        };
        TurnOnBackups.Pressed += () => _app.Status.Track(TurnOnAutomaticBackupsAsync());
        NotNow.Pressed += () =>
        {
            CompanionSettings settings = _app.Game.Settings.Load();
            settings.AutoBackup = false;
            _app.Game.Settings.Save(settings);
            ShowGame();
        };
        BackUpNow.Pressed += () => _app.Status.Track(BackUpNowAsync());
        _app.Game.Changed += ShowGame;
        _app.Workspace.Changed += ShowGame;
        ShowGame();
    }

    internal override Control Root { get; }
    internal override string Subtitle => "Your game, your careers and your safety net";

    internal Button Play { get; }
    internal Button ChooseFolder { get; }
    internal Button AddCareer { get; }
    internal Button OpenFile { get; }
    internal Button Manual { get; }
    internal Button TurnOnBackups { get; }
    internal Button NotNow { get; }
    internal Button BackUpNow { get; }
    internal CareerCards Careers { get; }
    internal FileDialog FolderDialog { get; }
    internal FileDialog OpenDialog { get; }
    internal FileDialog AddDialog { get; }
    internal SaveChoice AddChoice => _addChoice;
    internal IReadOnlyList<Button> OpenButtons => Careers.OpenButtons;
    internal string HeroStatus => _heroStatus.Text;

    /// <summary>Whether the banner shows the game's own art (read from the install) rather than the emblem.</summary>
    internal bool ShowsGameArt => _art.Texture is not null;
    internal bool AskingAboutBackups => _askBackups.Visible;

    internal override void Refresh() => ShowGame();

    internal async Task ChooseAsync(string path)
    {
        var chosen = await _app.Game.ChooseAsync(path);
        _app.Status.Show(chosen.Message, chosen.Ok ? StatusKind.Success : StatusKind.Failure);
    }

    internal void AskToAdd(string source)
    {
        _addSource = source;
        _addChoice.Open("Add a career to your game", NewName(System.IO.Path.GetFileNameWithoutExtension(source)), null, "",
            CareerNameProblem, elsewhere: false);
    }

    /// <summary>Copies a career file into the game's savegames folder under a new name, after a verified backup.</summary>
    internal async Task<InstallReceipt> AddCareerAsync(string name)
    {
        if (_app.Game.Folder is not GameFolder game) return new InstallReceipt(false, "Choose your game folder first.", name);
        if (_app.BackupFolderOrReport() is not string backups) return new InstallReceipt(false, "No backup folder.", name);
        _app.Status.Show("Backing up, then adding the career…");
        InstallReceipt receipt = await _app.Workspace.InstallAsync(game, _addSource, name + ".bes", backups, _app.GameRunning,
            $"Before adding {name}");
        _app.Status.Show(receipt.Ok ? $"{name} is now in your game. Your earlier careers are in the backup." : receipt.Message,
            receipt.Ok ? StatusKind.Success : StatusKind.Failure);
        await _app.Game.RescanAsync();
        return receipt;
    }

    internal async Task<BackupReceipt> TurnOnAutomaticBackupsAsync()
    {
        CompanionSettings settings = _app.Game.Settings.Load();
        settings.AutoBackup = true;
        _app.Game.Settings.Save(settings);
        BackupReceipt receipt = await BackUpNowAsync();
        ShowGame();
        return receipt;
    }

    internal async Task<BackupReceipt> BackUpNowAsync()
    {
        if (_app.Game.Folder is not GameFolder game) return new BackupReceipt(false, "Choose your game folder first.");
        if (_app.BackupFolderOrReport() is not string backups) return new BackupReceipt(false, "No backup folder.");
        _app.Status.Show("Backing up your careers and settings…");
        BackupReceipt receipt = await _app.Workspace.BackUpAsync(game, backups);
        _app.Status.Show(receipt.Ok ? $"Backed up to {backups}." : receipt.Message, receipt.Ok ? StatusKind.Success : StatusKind.Failure);
        ShowGame();
        return receipt;
    }

    /// <summary>Why a new career name cannot be used in this game, or null.</summary>
    internal string? CareerNameProblem(string name) =>
        GameInstaller.PortableNameProblem(name) ?? (_app.Game.Folder?.Careers.Any(career =>
            string.Equals(career.DisplayName, name, StringComparison.OrdinalIgnoreCase)) == true
            ? "Your game already has a career with that name." : null);

    /// <summary>A name not yet used by a career in the game: "Pilot", then "Pilot (2)" and so on.</summary>
    internal string NewName(string wanted)
    {
        string name = wanted.Trim();
        for (int number = 2; CareerNameProblem(name) is not null && number < 100; number++) name = $"{wanted.Trim()} ({number})";
        return name;
    }

    internal void ShowGame()
    {
        GameFolder? folder = _app.Game.Folder;
        Texture2D? art = GameArt.Load(folder?.Root, GameArt.Banner);
        _art.Texture = art;
        _emblem.Visible = art is null;
        ChooseFolder.Disabled = _app.Game.Busy;
        ChooseFolder.ThemeTypeVariation = folder is null && !_app.Game.Busy ? "Primary" : "";
        ChooseFolder.Text = folder is null ? "Choose game folder…" : "Change folder…";
        Play.Visible = folder is not null && folder.Root.Replace('\\', '/').Contains("/steamapps/", StringComparison.OrdinalIgnoreCase);
        Manual.Visible = GameArt.Manual(folder?.Root) is not null;
        AddCareer.Disabled = folder is null;
        Careers.Show();

        IReadOnlyList<BackupSet> sets = Backups.List(_app.Backups.Folder);
        if (_app.Game.Busy)
        {
            _heroStatus.Text = "Looking for your game…";
        }
        else if (folder is null)
        {
            _heroStatus.Text = "Your game was not found. Choose the folder Battle Engine Aquila is installed in; everything else " +
                "works on any career file you open.";
        }
        else
        {
            string version = folder.Executable.State switch
            {
                ExecutableState.Retail => "Steam version",
                ExecutableState.Different => "Your game (its BEA.exe has been changed or is another version)",
                _ => "Your game (BEA.exe is missing or unreadable)",
            };
            string backups = sets.Count == 0 ? "not backed up yet" : $"last backed up {Build.When(sets[0].Created)}";
            _heroStatus.Text = $"{version}  ·  {Build.Count(folder.Careers.Count, "career")}  ·  {backups}" +
                (_app.GameRunning() ? "\nThe game is running. The companion won't write into it until you close it." : "");
        }

        bool? auto = _app.Game.Settings.Load().AutoBackup;
        _askBackups.Visible = folder is not null && auto is null;
        _backupsOn.Visible = folder is not null && auto is not null;
        _backupLine.Text = (auto == true ? "Automatic backups are on." : "Automatic backups are off; turn them on from Backups.") +
            (sets.Count == 0 ? " No backups yet." : $" {Build.Count(sets.Count, "backup")}, the latest {Build.When(sets[0].Created)}.") +
            $"\nFolder: {_app.Backups.Folder}";
        BackUpNow.Disabled = folder is null || _app.Workspace.Busy;
        _folderLine.Text = folder is null ? "" : $"Game folder: {folder.Root}  ({(folder.Source.StartsWith("Found through Steam", StringComparison.Ordinal) ? "found through Steam" : "chosen by you")})";
    }

    /// <summary>A left-to-right shade over the banner art so its words stay readable.</summary>
    private static GradientTexture2D Shade()
    {
        Gradient gradient = new()
        {
            Colors = [new Color(Palette.Background, 0.95f), new Color(Palette.Background, 0.7f), new Color(Palette.Background, 0.05f)],
            Offsets = [0f, 0.42f, 1f],
        };
        return new GradientTexture2D { Gradient = gradient, Width = 256, Height = 4, FillFrom = Vector2.Zero, FillTo = new Vector2(1, 0) };
    }
}
