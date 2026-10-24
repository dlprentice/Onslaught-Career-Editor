// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// The front page: the game with its own art and a Play button, the player's careers, the safety net
/// (automatic backups and the promises the companion keeps) and ways into the rest of the app. On Windows it also
/// lists careers left in the retired toolkit's copied installs, so each can be saved as a copy elsewhere.
/// </summary>
internal sealed class HomePage : Page
{
    private readonly AppServices _app;
    private readonly TextureRect _art;
    private readonly Emblem _emblem;
    private readonly Label _heroStatus, _folderLine, _backupLine, _heroTitle;
    private readonly CeHomePanel _ce;
    private readonly PanelContainer _askBackups, _backupsOn, _oldCopies;
    private readonly Label _oldCopiesNote, _virtualStoreNote;
    private readonly PanelContainer _virtualStore;
    private readonly VBoxContainer _oldCopyRows;
    private readonly List<Button> _oldCopyButtons = [];
    private string _oldCopySource = "";
    private readonly GridContainer _columns;
    private readonly SaveChoice _addChoice;
    private readonly List<Label> _promises = [];
    private string _addSource = "";

    internal HomePage(AppServices app) : base("home", "Home", "home")
    {
        _app = app;
        (ScrollContainer scroll, VBoxContainer content) = Build.Scroller(18);
        Root = scroll;

        HBoxContainer targetRow = content.Add(Build.Row(12));
        targetRow.Add(Build.Text("Game", "Strong", wrap: false));
        Target = targetRow.Add(new OptionButton { CustomMinimumSize = new Vector2(240, 0) });
        Target.AddItem("Original Battle Engine Aquila", (int)GameTarget.Original);
        Target.AddItem("Onslaught CE", (int)GameTarget.OnslaughtCe);
        Target.ItemSelected += index =>
        {
            if (_app.SelectTarget is not null) _app.Status.Track(_app.SelectTarget((GameTarget)index));
        };

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
        // Sized before it is anchored, so it sits inside the banner rather than growing past its right edge.
        _emblem = stage.Add(new Emblem
        {
            CustomMinimumSize = new Vector2(150, 150), Size = new Vector2(150, 150), Modulate = new Color(1, 1, 1, 0.5f),
            GrowHorizontal = Control.GrowDirection.Begin, GrowVertical = Control.GrowDirection.Both,
        });
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
        _heroTitle = heroColumn.Add(Build.Text("Battle Engine Aquila", "HeroTitle", wrap: false));
        _heroStatus = heroColumn.Add(Build.Text("Looking for your game…", "HeroText"));
        _heroStatus.CustomMinimumSize = new Vector2(520, 0);
        _heroStatus.SizeFlagsHorizontal = Control.SizeFlags.ShrinkBegin;
        heroColumn.Add(Build.Spacer(0, expand: true));
        HBoxContainer heroActions = heroColumn.Add(Build.Row(10));
        Play = heroActions.Add(Build.Button("Play", "Primary", "Starts the original Battle Engine Aquila through Steam."));
        Play.Icon = Icons.Get("play");
        ChooseFolder = heroActions.Add(Build.Button("Choose game folder…", "", "The folder that contains BEA.exe and the data folder."));
        ChooseFolder.Icon = Icons.Get("folder");

        _ce = new CeHomePanel(app);
        content.Add(_ce.Root);

        _columns = content.Add(new GridContainer { Columns = 2 });
        _columns.AddThemeConstantOverride("h_separation", 18);
        _columns.AddThemeConstantOverride("v_separation", 18);
        _columns.Resized += () => _columns.Columns = _columns.Size.X >= 900 ? 2 : 1;

        (PanelContainer careersCard, VBoxContainer careers) = Build.Card("Your careers", 12);
        careersCard.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        careersCard.SizeFlagsStretchRatio = 1.4f;
        careers.Add(Build.Text("Open a career to see its missions and Goodies, change it, or add cheats. Opening only reads it.", "Muted"));
        Careers = new CareerCards(app, onHome: true);
        careers.Add(Careers.Root);
        HBoxContainer careerLinks = careers.Add(Build.Row(16));
        AddCareer = careerLinks.Add(Build.Button("Add a career file to your game…", "Link",
            "Put a career you have as a file (from a friend, or a backup of your own) into the game's career list."));
        OpenFile = careerLinks.Add(Build.Button("Open a career file…", "Link", "Look at a career file anywhere on your computer, read-only."));
        (_oldCopies, VBoxContainer old) = Build.Panel("Inset", 8);
        old.Add(Build.Text("Careers from the old Windows toolkit", "Strong"));
        _oldCopiesNote = old.Add(Build.Text("", "Muted"));
        _oldCopyRows = old.Add(Build.Column(6));
        _oldCopies.Visible = false;
        careers.Add(_oldCopies);
        (_virtualStore, VBoxContainer store) = Build.Panel("CautionNotice", 8);
        store.Add(Build.Text("Careers Windows kept elsewhere", "Strong"));
        _virtualStoreNote = store.Add(Build.Text("", "Muted"));
        _virtualStore.Visible = false;
        careers.Add(_virtualStore);
        _columns.Add(careersCard);

        VBoxContainer side = _columns.Add(Build.Column(18));
        side.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        (PanelContainer safety, VBoxContainer safetyBody) = Build.Card("Your safety net", 10);
        (_askBackups, VBoxContainer ask) = Build.Panel("CautionNotice", 8);
        ask.Add(Build.Text("Keep automatic backups?", "Strong"));
        ask.Add(Build.Text("When the companion opens, and when you close the game while it is open, it copies the selected game's " +
            "careers to a backup folder if anything changed. Original-game backups also include default settings. Nothing is ever deleted.", "Muted"));
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
            "Career changes are backed up before they replace a file.",
            "Nothing is written to game files while Battle Engine Aquila or Onslaught CE is running.",
            "Verified career backups can be put back from Backups.",
        })
        {
            HBoxContainer line = safetyBody.Add(Build.Row(10));
            line.Add(new TextureRect
            {
                Texture = Icons.Get("check"), ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
                StretchMode = TextureRect.StretchModeEnum.KeepAspectCentered, CustomMinimumSize = new Vector2(18, 18),
                Modulate = Palette.Good, SizeFlagsVertical = Control.SizeFlags.ShrinkCenter,
            });
            // A wrapping label in a row needs the row's width, or it wraps after every letter.
            Label said = line.Add(Build.Text(promise));
            said.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
            _promises.Add(said);
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
        OldCopyDialog = app.Popups.Add(Build.FilePicker("Save a copy of the career", FileDialog.FileModeEnum.SaveFile, "*.bes ; Career files"));
        OldCopyDialog.FileSelected += path => _app.Status.Track(SaveOldCopyAsync(_oldCopySource, path));
        _addChoice = new SaveChoice(app);
        _addChoice.Chosen += (_, name) => _app.Status.Track(AddCareerAsync(name));

        Play.Pressed += () =>
        {
            if (_app.Game.Target == GameTarget.OnslaughtCe)
            {
                if (_app.Game.Ce is CeInstallation ce)
                {
                    Outcome<string> launched = ce.Launch();
                    _app.Status.Show(launched.Message, launched.Ok ? StatusKind.Success : StatusKind.Failure);
                }
                return;
            }
            _app.OpenUrl($"steam://rungameid/{SteamLibraries.AppId}");
            _app.Status.Show("Asking Steam to start Battle Engine Aquila…");
        };
        ChooseFolder.Pressed += () => FolderDialog.PopupCenteredRatio(0.75f);
        FolderDialog.DirSelected += path => _app.Status.Track(ChooseAsync(path));
        OpenFile.Pressed += () => OpenDialog.PopupCenteredRatio(0.75f);
        OpenDialog.FileSelected += path => _app.Status.Track(_app.ChooseCareer(path));
        AddCareer.Pressed += () => AddDialog.PopupCenteredRatio(0.75f);
        AddDialog.FileSelected += AskToAdd;
        Manual.Pressed += () =>
        {
            if (GameArt.Manual(_app.Game.Folder?.AssetRoot) is string manual) _app.OpenUrl(manual);
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

    internal OptionButton Target { get; }
    internal CeHomePanel CePanel => _ce;
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
    internal FileDialog OldCopyDialog { get; }

    /// <summary>The careers found in the retired Windows toolkit's copies, as Home lists them.</summary>
    internal IReadOnlyList<OldCopyCareer> OldCopies { get; private set; } = [];
    internal IReadOnlyList<Button> OldCopyButtons => _oldCopyButtons;
    internal bool ShowsOldCopies => _oldCopies.Visible;
    internal SaveChoice AddChoice => _addChoice;
    internal IReadOnlyList<Button> OpenButtons => Careers.OpenButtons;
    internal string HeroStatus => _heroStatus.Text;
    internal IReadOnlyList<Label> Promises => _promises;

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
        _addChoice.Open("Add a career to your game", _app.NewCareerName(System.IO.Path.GetFileNameWithoutExtension(source)), null, "",
            _app.CareerNameProblem, elsewhere: false);
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

    /// <summary>
    /// Saves a career from one of the old toolkit's copies as a new file elsewhere, through the same protected
    /// route as every copy: the source is read as a verified snapshot, the copy is published without replacing
    /// anything and read back. The old copy is never changed.
    /// </summary>
    internal async Task<PublicationReceipt> SaveOldCopyAsync(string source, string destination)
    {
        _app.Status.Show("Saving a checked copy…");
        Outcome<SaveSession> read = await _app.Workspace.ReadSnapshotAsync(source);
        PublicationReceipt receipt = read.Value is SaveSession snapshot
            ? await _app.Workspace.PublishFromAsync(snapshot, destination, snapshot.CopyBytes())
            : new PublicationReceipt(false, read.Message);
        _app.Status.Show(receipt.Ok ? $"Saved a checked copy to {receipt.Output}. The old toolkit's copy is unchanged."
            : receipt.Message + (receipt.MayHaveOutput ? "\nA copy may exist at: " + (receipt.Output ?? destination) : ""),
            receipt.Ok ? StatusKind.Success : StatusKind.Failure);
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

    internal void ShowGame()
    {
        GameFolder? folder = _app.Game.Folder;
        bool ce = _app.Game.Target == GameTarget.OnslaughtCe;
        Target.Select((int)_app.Game.Target);
        Target.Disabled = _app.Game.Busy || _app.Workspace.Busy;
        _heroTitle.Text = ce ? "Onslaught CE" : "Battle Engine Aquila";
        _ce.Refresh();
        Texture2D? art = GameArt.Load(folder?.AssetRoot, GameArt.Banner);
        _art.Texture = art;
        _emblem.Visible = art is null;
        ChooseFolder.Disabled = _app.Game.Busy || _app.Workspace.Busy;
        ChooseFolder.ThemeTypeVariation = folder is null && !_app.Game.Busy ? "Primary" : "";
        ChooseFolder.Text = ce ? "Choose original game folder…" : folder is null ? "Choose game folder…" : "Change folder…";
        ChooseFolder.TooltipText = ce ? "Choose the original game's pictures and music. Original careers come from the data folder recorded or discovered by CE."
            : "The folder that contains BEA.exe and the data folder.";
        Play.Visible = ce ? _app.Game.Ce is not null : folder is not null && folder.Root.Replace('\\', '/').Contains("/steamapps/", StringComparison.OrdinalIgnoreCase);
        Play.Disabled = _app.Game.Busy || _app.Workspace.Busy || _app.GameRunning();
        Play.TooltipText = ce ? "Starts the selected CE launcher; it handles updates." : "Starts the original game through Steam.";
        Manual.Visible = GameArt.Manual(folder?.AssetRoot) is not null;
        AddCareer.Disabled = folder is null;
        Careers.Show();

        // Only this game folder's backups count as its backups.
        IReadOnlyList<BackupSet> sets = folder is null ? [] : Backups.List(_app.Backups.Folder, folder);
        if (_app.Game.Busy && folder is null)
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
            string version = ce ? _app.Game.CeVersionMessage : folder.Executable.State switch
            {
                ExecutableState.Retail => "Original game (Steam, unmodified)",
                ExecutableState.Different => "Original game (its BEA.exe differs from the Steam release; on Steam, Verify integrity of " +
                    "game files restores it)",
                _ => "Original game (BEA.exe is missing or unreadable)",
            };
            string backups = sets.Count == 0 ? "not backed up yet" : $"last backed up {Build.When(sets[0].Created)}";
            _heroStatus.Text = $"{version}  ·  {Build.Count(folder.Careers.Count, "career")}  ·  {backups}" +
                (_app.GameRunning() ? "\nThe game or Onslaught CE is running. The companion won't write into the game folder until it closes." : "");
        }

        bool? auto = _app.Game.Settings.Load().AutoBackup;
        _askBackups.Visible = folder is not null && auto is null;
        _backupsOn.Visible = folder is not null && auto is not null;
        _backupLine.Text = (auto == true ? "Automatic backups are on." : "Automatic backups are off; turn them on from Backups.") +
            (sets.Count == 0 ? " No backups yet." : $" {Build.Count(sets.Count, "backup")}, the latest {Build.When(sets[0].Created)}.") +
            $"\nFolder: {_app.Backups.Folder}";
        BackUpNow.Disabled = folder is null || _app.Workspace.Busy;
        ShowOldCopies();
        ShowVirtualStore(ce ? null : folder?.Root);
        _folderLine.Text = folder is null ? "" : ce ? $"CE user folder: {folder.Root}" :
            $"Game folder: {folder.Root}  ({(folder.Source.StartsWith("Found through Steam", StringComparison.Ordinal) ? "found through Steam" : "chosen by you")})";
    }

    /// <summary>Lists the old toolkit's careers again when they changed; the panel shows only when there are some.</summary>
    private void ShowOldCopies()
    {
        IReadOnlyList<OldCopyCareer> found = OldSafeCopies.Find(_app.OldCopiesFolder);
        if (found.SequenceEqual(OldCopies)) return;
        OldCopies = found;
        foreach (Node child in _oldCopyRows.GetChildren())
        {
            _oldCopyRows.RemoveChild(child);
            child.QueueFree();
        }
        _oldCopyButtons.Clear();
        foreach (OldCopyCareer career in found)
        {
            HBoxContainer row = _oldCopyRows.Add(Build.Row(10));
            Label name = row.Add(Build.Text($"{career.Name}  ·  in the copy \"{career.Where}\"" +
                (career.CanCopy ? "" : $"\nNot career-sized ({career.Length:N0} bytes; a career is {CareerSave.Size:N0}), so it cannot be copied. It is left where it is: {career.Path}")));
            name.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
            Button save = row.Add(Build.Button("Save a copy somewhere else…", "Link", career.CanCopy
                ? "Saves a checked copy of this career outside the game. The old copy is left as it is."
                : "This file is not the size of a career, so the companion cannot check it or copy it."));
            save.Disabled = !career.CanCopy;
            save.Pressed += () => ChooseOldCopyDestination(career);
            _oldCopyButtons.Add(save);
        }
        _oldCopiesNote.Text = $"The retired Windows toolkit (v1.0.11) could play a copy of the game kept in {_app.OldCopiesFolder}, " +
            "and careers played there were saved in that copy, where the game does not look. Save any you want to keep as a " +
            "copy somewhere else; \"Add a career file to your game…\" can then put it in your game. The companion only reads " +
            "these copies and never changes or deletes them.";
        _oldCopies.Visible = found.Count > 0;
    }

    /// <summary>
    /// Says when Windows kept careers for a game in Program Files in its VirtualStore folder, which the companion does
    /// not read, back up or write; the panel shows only when that folder holds some.
    /// </summary>
    private void ShowVirtualStore(string? root)
    {
        string? saves = root is null ? null : WindowsFolders.VirtualStoreSavesHere(root);
        IReadOnlyList<string> found = WindowsFolders.Careers(saves);
        _virtualStore.Visible = found.Count > 0;
        if (found.Count == 0) return;
        _virtualStoreNote.Text = $"Your game is in a Program Files folder, and Windows kept {Build.Count(found.Count, "career")} " +
            $"it saved in {saves} instead of in the game folder ({string.Join(", ", found.Select(System.IO.Path.GetFileNameWithoutExtension))}). " +
            "The game may be playing those copies. The companion does not read, back up or change that folder yet; this has not " +
            "been tried on Windows.";
    }

    private void ChooseOldCopyDestination(OldCopyCareer career)
    {
        _oldCopySource = career.Path;
        OldCopyDialog.CurrentDir = System.Environment.GetFolderPath(System.Environment.SpecialFolder.MyDocuments) is { Length: > 0 } documents
            ? documents : "";
        OldCopyDialog.CurrentFile = career.Name + ".bes";
        OldCopyDialog.PopupCenteredRatio(0.75f);
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
