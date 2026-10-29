// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>Where the companion looks for Steam, keeps its settings and puts backups; tests and captures supply their own.</summary>
internal sealed record CompanionEnvironment(IReadOnlyList<string> SteamRoots, string SettingsPath, Func<bool>? GameRunning = null,
    Action<string>? OpenUrl = null, string? DefaultBackupFolder = null, Action? Quit = null, string? OldCopiesFolder = null,
    string? CeUserFolder = null, Func<string, bool>? CeInstallSupported = null)
{
    internal const string BackupFolderName = "Battle Engine Aquila Backups";

    internal static CompanionEnvironment Default() =>
        new(SteamLibraries.DefaultRoots(), ProjectSettings.GlobalizePath("user://settings.json"), GameProcess.IsRunning);

    /// <summary>
    /// A clearly named backups folder in the player's Documents folder, or on Windows in the unsynced local application
    /// data folder (<see cref="WindowsFolders.DefaultBackupRoot"/>), or else in the app's own data folder.
    /// </summary>
    internal string BackupFolder()
    {
        if (DefaultBackupFolder is string chosen) return chosen;
        string root = WindowsFolders.DefaultBackupRoot(OperatingSystem.IsWindows(), OS.GetSystemDir(OS.SystemDir.Documents),
            System.Environment.GetFolderPath(System.Environment.SpecialFolder.LocalApplicationData), OS.GetUserDataDir());
        return System.IO.Path.Combine(root, BackupFolderName);
    }
}

/// <summary>
/// The companion's root. Everything below it is built in code; <c>Main.tscn</c> only attaches this
/// script to one node. It owns the sidebar, header, pages, dialogs and status bar, opens the player's
/// most recent career, keeps automatic backups when they are on, watches whether the game is running,
/// catches up with what the game saved when it closes or the player comes back to the companion, and
/// defers closing while a file operation is still running.
/// </summary>
public partial class CompanionApp : Control
{
    private const float RunningCheckSeconds = 2f;

    private readonly IProtectedSaveFiles? _files;
    private readonly bool _managesWindow;
    private readonly CompanionEnvironment? _environment;
    private readonly Dictionary<string, Page> _pages = [];
    private readonly List<string> _careerMenuPaths = [];
    private Func<bool> _gameRunning = () => false;
    private Action _quit = () => { };
    private Action? _onDiscard;
    private bool _running, _openedFirstCareer, _autoBackupDone, _quietOpen;
    private double _sinceRunningCheck;
    private Task _catchUp = Task.CompletedTask;

    public CompanionApp() : this(new ProtectedSaveFiles(), managesWindow: true)
    {
    }

    /// <summary>Hosts the companion inside another tree (tests, captures) with the given file access and environment.</summary>
    internal CompanionApp(IProtectedSaveFiles? files, bool managesWindow, CompanionEnvironment? environment = null)
        => (_files, _managesWindow, _environment) = (files, managesWindow, environment);

    internal CareerWorkspace Workspace { get; private set; } = null!;
    internal GameLibrary Game { get; private set; } = null!;
    internal StatusLine Status { get; private set; } = null!;
    internal AppServices Services { get; private set; } = null!;
    internal Sidebar Sidebar { get; private set; } = null!;
    internal Label PageTitle { get; private set; } = null!;
    internal Label PageSubtitle { get; private set; } = null!;
    internal MenuButton CareerMenu { get; private set; } = null!;
    internal Label RunningBadge { get; private set; } = null!;
    internal IReadOnlyDictionary<string, Page> Pages => _pages;
    internal Page Current { get; private set; } = null!;
    internal HomePage Home { get; private set; } = null!;
    internal SummaryPage Summary { get; private set; } = null!;
    internal GoodiesPage Goodies { get; private set; } = null!;
    internal EditCareerPage EditCareer { get; private set; } = null!;
    internal CheatsPage Cheats { get; private set; } = null!;
    internal SettingsPage Settings { get; private set; } = null!;
    internal BackupsPage Backups { get; private set; } = null!;
    internal MusicPage Music { get; private set; } = null!;
    internal LorePage Lore { get; private set; } = null!;
    internal CareerBytesPage Bytes { get; private set; } = null!;
    internal AssetsPage Assets { get; private set; } = null!;
    internal LevelEditorPage LevelEditor { get; private set; } = null!;

    /// <summary>Asks before unsaved changes on Edit career or Game settings would be lost (switching careers, closing).</summary>
    internal ConfirmationDialog DiscardDialog { get; private set; } = null!;

    /// <summary>Whether the game was running at the last check; the header says so while it is.</summary>
    internal bool GameIsRunning => _running;

    /// <summary>The latest catch-up with the game folder (see <see cref="CatchUpAsync"/>), for tests to await.</summary>
    internal Task PendingCatchUp => _catchUp;

    public override void _Ready()
    {
        Theme = CompanionTheme.Build();
        SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        Workspace = new CareerWorkspace(new SaveFileWorker(_files));
        CompanionEnvironment environment = _environment ?? CompanionEnvironment.Default();
        SettingsStore settings = new(environment.SettingsPath);
        Game = new GameLibrary(environment.SteamRoots, settings,
            environment.CeUserFolder ?? (_managesWindow ? null : System.IO.Path.Combine(System.IO.Path.GetDirectoryName(environment.SettingsPath)!, "ce-user")),
            _managesWindow ? null : _ => null, environment.CeInstallSupported);
        Status = new StatusLine();
        _gameRunning = environment.GameRunning ?? GameProcess.IsRunning;
        _quit = environment.Quit ?? (() => GetTree().Quit());
        Action<string> openUrl = environment.OpenUrl ?? (url => OS.ShellOpen(url));
        this.Add(new ColorRect { Color = Palette.Background, MouseFilter = MouseFilterEnum.Ignore })
            .SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        Node popups = this;
        Services = new AppServices
        {
            Workspace = Workspace, Game = Game, Status = Status, Backups = new BackupLocation(settings, environment.BackupFolder()),
            GameRunning = () => _gameRunning(), OpenUrl = openUrl, Navigate = Navigate, OpenCareer = OpenCareerAsync,
            ChooseCareer = ChooseCareerAsync, Popups = popups, SelectTarget = SelectTargetAsync,
            CatchUp = () => CatchUpAsync(force: true, backUp: false),
            OpenCareerFile = () => Home.OpenDialog.PopupCenteredRatio(0.75f),
            OldCopiesFolder = environment.OldCopiesFolder ?? OldSafeCopies.DefaultRoot(),
        };

        DiscardDialog = this.Add(Build.Confirm("Discard unsaved changes?", "Discard"));
        DiscardDialog.Confirmed += () =>
        {
            Action? then = _onDiscard;
            _onDiscard = null;
            then?.Invoke();
        };
        DiscardDialog.Canceled += () => _onDiscard = null;

        Home = new HomePage(Services);
        Summary = new SummaryPage(Services);
        EditCareer = new EditCareerPage(Services);
        Goodies = new GoodiesPage(Services, index =>
        {
            Navigate("edit");
            EditCareer.AddGoodie(index);
        }, path =>
        {
            Navigate("assets");
            Assets.Reveal(path);
        });
        Cheats = new CheatsPage(Services);
        Settings = new SettingsPage(Services);
        Backups = new BackupsPage(Services);
        Music = new MusicPage(Game, Status);
        Lore = new LorePage(Game, Status, openUrl);
        Bytes = new CareerBytesPage(Workspace, Status, popups);
        Assets = new AssetsPage(Services);
        LevelEditor = new LevelEditorPage(Services);
        NavGroup[] groups =
        [
            new("", [Home]),
            new("Your career", [Summary, Goodies, EditCareer, Cheats]),
            new("Your game", [Settings, Backups]),
            new("Extras", [Music, Lore, Assets, LevelEditor]),
            new("Advanced", [Bytes], Folds: true),
        ];

        VBoxContainer frame = this.Add(Build.Column(0));
        frame.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        HBoxContainer body = frame.Add(Build.Row(0));
        body.SizeFlagsVertical = SizeFlags.ExpandFill;
        Sidebar = new Sidebar(groups, Navigate);
        body.Add(Sidebar.Root);
        VBoxContainer main = body.Add(Build.Column(0));
        main.SizeFlagsHorizontal = SizeFlags.ExpandFill;

        HBoxContainer header = main.Add(Build.Margin(30, 22, 30, 14)).Add(Build.Row(14));
        VBoxContainer titles = header.Add(Build.Column(2));
        titles.SizeFlagsHorizontal = SizeFlags.ExpandFill;
        PageTitle = titles.Add(Build.Heading("", "Title"));
        PageSubtitle = titles.Add(Build.Text("", "Muted", wrap: false, clip: true));
        RunningBadge = header.Add(Build.Text("Game running", "Warn", wrap: false));
        RunningBadge.TooltipText = "The original game or Onslaught CE is detected. Close both games before saving and wait for the save to finish before starting either.";
        RunningBadge.SizeFlagsVertical = SizeFlags.ShrinkCenter;
        RunningBadge.Visible = false;
        VBoxContainer career = header.Add(Build.Column(2));
        career.SizeFlagsVertical = SizeFlags.ShrinkCenter;
        career.Add(Build.Eyebrow("Career")).HorizontalAlignment = HorizontalAlignment.Right;
        CareerMenu = career.Add(new MenuButton { Text = "Choose a career", Flat = false, Alignment = HorizontalAlignment.Right,
            CustomMinimumSize = new Vector2(220, 0), TooltipText = "Switch careers, or open a career file (Ctrl+O)." });
        CareerMenu.Icon = Icons.Get("down");
        CareerMenu.IconAlignment = HorizontalAlignment.Right;
        CareerMenu.GetPopup().IdPressed += ChooseFromMenu;

        MarginContainer hostMargin = main.Add(Build.Margin(30, 4, 30, 20));
        hostMargin.SizeFlagsVertical = SizeFlags.ExpandFill;
        VBoxContainer host = hostMargin.Add(Build.Column(0));
        foreach (NavGroup group in groups)
        {
            foreach (Page page in group.Pages)
            {
                _pages[page.Key] = page;
                page.HeaderChanged = RefreshHeader;
                page.Root.SizeFlagsVertical = SizeFlags.ExpandFill;
                page.Root.Visible = false;
                host.Add(page.Root);
            }
        }
        frame.Add(Status.Root);

        Workspace.Changed += RefreshActions;
        Workspace.SessionOpened += ShowSession;
        Game.Changed += ShowGameSummary;

        if (_managesWindow)
        {
            Window window = GetWindow();
            window.MinSize = new Vector2I(1024, 700);
            FitToScreen(window);
            DisplayServer.SetIcon(Emblem.Icon());
            GetTree().AutoAcceptQuit = false;
            window.CloseRequested += OnCloseRequested;
        }
        if (!Workspace.IsAvailable) Status.Show(SaveFileWorker.UnavailableMessage, StatusKind.Failure);
        Navigate("home");
        RefreshActions();
        CheckRunning();
        Status.Track(Game.DetectAsync());
    }

    public override void _ExitTree()
    {
        if (Workspace is null) return;
        if (_managesWindow) GetWindow().CloseRequested -= OnCloseRequested;
        // A close cannot abandon a write or claim it was cancelled.
        Workspace.WaitForCompletion();
        Icons.Clear();
        GameArt.Clear();
    }

    public override void _Process(double delta)
    {
        if (Current == Music) Music.Tick();
        _sinceRunningCheck += delta;
        if (_sinceRunningCheck >= RunningCheckSeconds) CheckRunning();
    }

    public override void _Notification(int what)
    {
        // Coming back to the companion, perhaps after playing: pick up anything the game saved.
        if (what == NotificationApplicationFocusIn && Workspace is not null) CheckRunning(catchUp: true);
    }

    public override void _UnhandledKeyInput(InputEvent @event)
    {
        if (@event is not InputEventKey { Pressed: true, Echo: false } key) return;
        if (key is { CtrlPressed: true, Keycode: Key.O } && !Workspace.Busy)
            Home.OpenDialog.PopupCenteredRatio(0.75f);
        else if (key is { CtrlPressed: true, Keycode: Key.S } && Current == EditCareer && !EditCareer.Save.Disabled)
            EditCareer.AskToSave();
        else if (key is { CtrlPressed: true, Keycode: Key.S } && Current == Settings && !Settings.Save.Disabled)
            Settings.AskToSave();
        else if (Current == Lore && key is { CtrlPressed: true, Keycode: Key.F })
            Lore.Search.GrabFocus();
        else if (Current == Lore && key is { AltPressed: true, Keycode: Key.Left })
            Lore.Back();
        else if (Current == Lore && key is { AltPressed: true, Keycode: Key.Right })
            Lore.Forward();
        else
            return;
        GetViewport().SetInputAsHandled();
    }

    /// <summary>Shows one page and refreshes its header.</summary>
    internal void Navigate(string key)
    {
        if (!_pages.TryGetValue(key, out Page? page)) return;
        if (Current is not null && Current != page) Status.Clear();
        if (Current is not null) Current.Root.Visible = false;
        Current = page;
        page.Root.Visible = true;
        Sidebar.Select(key);
        page.Refresh();
        RefreshHeader();
    }

    /// <summary>Opens a career read-only as the one the career pages show. A refusal keeps the previous career open.</summary>
    internal async Task<Outcome<SaveSession>> OpenCareerAsync(string path)
    {
        if (Workspace.Busy) return Outcome<SaveSession>.Refusal("A file operation is already running.");
        Status.Show("Opening the career…");
        Outcome<SaveSession> opened = await Workspace.OpenAsync(path);
        if (opened.Ok)
            Status.Show($"{System.IO.Path.GetFileNameWithoutExtension(path)} is open. Opening only reads it.", StatusKind.Success);
        else
            Status.Show(opened.Message, StatusKind.Failure);
        return opened;
    }

    /// <summary>
    /// Opens a career the player chose (the Career menu, Home, or a file picked with Ctrl+O). Opening another career
    /// starts Edit career again from it, so unsaved changes there are only dropped after the player says so; until then
    /// the open career stays and this returns a refusal.
    /// </summary>
    internal Task<Outcome<SaveSession>> ChooseCareerAsync(string path)
    {
        if (!EditCareer.HasChanges) return OpenCareerAsync(path);
        AskToDiscard($"{Build.Count(EditCareer.ChangeCount, "change")} on Edit career {(EditCareer.ChangeCount == 1 ? "is" : "are")} " +
            $"not saved. Open {System.IO.Path.GetFileNameWithoutExtension(path)} and discard {(EditCareer.ChangeCount == 1 ? "it" : "them")}?",
            "Discard and open", () => Status.Track(OpenCareerAsync(path)));
        return Task.FromResult(Outcome<SaveSession>.Refusal("Your unsaved changes are kept until you choose."));
    }

    /// <summary>
    /// Closes the companion, unless a file operation is still running (a close never abandons a write) or Edit career
    /// or Game settings holds unsaved changes, which are only dropped after the player says so. Returns whether it quit.
    /// </summary>
    internal bool RequestClose()
    {
        if (CloseWouldAbandonWrite()) return false;
        List<string> unsaved = [];
        if (EditCareer.HasChanges) unsaved.Add($"{Build.Count(EditCareer.ChangeCount, "change")} on Edit career");
        if (Settings.HasChanges) unsaved.Add($"{Build.Count(Settings.ChangeCount, "change")} on Game settings");
        if (unsaved.Count == 0)
        {
            _quit();
            return true;
        }
        AskToDiscard($"Not saved yet: {string.Join(" and ", unsaved)}. Close the companion and discard them?", "Discard and close", () =>
        {
            // The dialog stays open across frames, and an automatic backup can start meanwhile (the game closed).
            if (!CloseWouldAbandonWrite()) _quit();
        });
        return false;
    }

    internal async Task SelectTargetAsync(GameTarget target)
    {
        if (Game.Busy || Workspace.Busy || target == Game.Target) return;
        if (EditCareer.HasChanges || Settings.HasChanges)
        {
            Status.Show("Save or undo your career and settings changes before switching games.", StatusKind.Failure);
            Home.ShowGame();
            return;
        }
        Workspace.CloseSession();
        Settings.ResetTarget();
        _openedFirstCareer = false;
        _autoBackupDone = false;
        await Game.SelectTargetAsync(target);
        Navigate("home");
    }

    private bool CloseWouldAbandonWrite()
    {
        if (!Workspace.Busy) return false;
        Status.Show("A file operation is still finishing. Wait for its result before closing.");
        return true;
    }

    private void AskToDiscard(string text, string action, Action then)
    {
        _onDiscard = then;
        DiscardDialog.DialogText = text;
        DiscardDialog.OkButtonText = action;
        DiscardDialog.PopupCentered();
    }

    /// <summary>
    /// Checks whether the game is running and updates what depends on it. When the game has just closed,
    /// the companion catches up with what it saved and, if automatic backups are on, backs that up.
    /// </summary>
    internal void CheckRunning(bool catchUp = false)
    {
        _sinceRunningCheck = 0;
        bool running = _gameRunning();
        bool closed = _running && !running;
        if (running != _running)
        {
            _running = running;
            RunningBadge.Visible = running;
            Home.ShowGame();
            Settings.Refresh();
            Status.Game.Text = GameLine();
        }
        if ((closed || catchUp) && !running && _catchUp.IsCompleted)
        {
            _catchUp = CatchUpAsync(force: false, backUp: closed);
            Status.Track(_catchUp);
        }
    }

    /// <summary>
    /// Brings the companion up to date after the game (or anything else) changed its careers or settings:
    /// reads the folder again, makes an automatic backup when asked and they are on, and reopens the open
    /// career and settings if they changed and hold no unsaved changes. Without <paramref name="force"/> it
    /// does nothing unless the files' names, sizes or times changed. It never writes into the game.
    /// </summary>
    internal async Task CatchUpAsync(bool force, bool backUp)
    {
        if (Game.Busy || Workspace.Busy || Game.Folder is null) return;
        if (Game.Target == GameTarget.OnslaughtCe) await Settings.CatchUpAsync();
        if (!force && !Game.FilesChanged()) return;
        await Game.RescanAsync();
        if (Game.Folder is not GameFolder folder) return;
        if (backUp && Game.Settings.Load().AutoBackup == true) await AutoBackUpAsync(folder);
        if (Workspace.Session is SaveSession session && !Workspace.Busy &&
            folder.Careers.FirstOrDefault(file => string.Equals(file.Path, session.Path, StringComparison.Ordinal) ||
                folder.Target == GameTarget.OnslaughtCe && file.Name.Equals(System.IO.Path.GetFileName(session.Path), StringComparison.OrdinalIgnoreCase)) is { Sha256: string now } career &&
            (now != session.Sha256 || career.Path != session.Path))
        {
            if (EditCareer.HasChanges)
            {
                Status.Show($"{career.DisplayName} has changed in your game since you opened it. Undo your changes on Edit career to see " +
                    "the latest; saving in its place is refused until then.");
            }
            else
            {
                _quietOpen = true;
                try
                {
                    await OpenCareerAsync(career.Path);
                }
                finally
                {
                    _quietOpen = false;
                }
                Status.Show($"{career.DisplayName} changed in your game; the companion shows the latest.", StatusKind.Success);
            }
        }
        await Settings.CatchUpAsync();
    }

    private void ShowSession()
    {
        if (Workspace.Session is not SaveSession session) return;
        EditCareer.ShowSession(session);
        Bytes.ShowSession(session);
        Summary.ShowSession(session);
        Goodies.ShowSession(session);
        Cheats.ShowSession(session);
        // A career the player opens from Home takes them to it; the one opened at startup does not move them.
        if (Current == Home && !_quietOpen) Navigate("summary");
        ShowCareerMenu();
        RefreshHeader();
    }

    private void ShowGameSummary()
    {
        // Names arrive with the game's text; redraw the career pages that show them.
        if (!Game.Busy && Workspace.Session is SaveSession session)
        {
            Summary.ShowSession(session);
            Goodies.ShowSession(session);
        }
        Status.Game.Text = GameLine();
        ShowCareerMenu();
        RefreshHeader();
        if (Game.Busy || Game.Folder is not GameFolder folder) return;
        if (!_autoBackupDone)
        {
            _autoBackupDone = true;
            if (Game.Settings.Load().AutoBackup == true) Status.Track(AutoBackUpAsync(folder));
        }
        if (!_openedFirstCareer && Workspace.Session is null && !Workspace.Busy)
        {
            // The career played most recently opens by itself, read-only, so its pages are ready.
            _openedFirstCareer = true;
            if (folder.Careers.Where(file => file.Supported).OrderByDescending(file => file.Modified).FirstOrDefault() is GameFile recent)
                Status.Track(OpenFirstAsync(recent.Path));
        }
    }

    private async Task OpenFirstAsync(string path)
    {
        // An automatic backup may be running; wait for it rather than refusing.
        for (int frame = 0; frame < 600 && Workspace.Busy; frame++) await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        if (Workspace.Session is not null || Game.Folder?.Careers.Any(file => file.Path == path) != true) return;
        _quietOpen = true;
        try
        {
            await OpenCareerAsync(path);
        }
        finally
        {
            _quietOpen = false;
        }
    }

    private async Task AutoBackUpAsync(GameFolder folder)
    {
        if (Services.BackupFolderOrReport() is not string backups) return;
        BackupReceipt receipt = await Workspace.AutoBackUpAsync(folder, backups);
        if (receipt.Set is not null) Status.Show("Your careers and settings were backed up automatically.", StatusKind.Success);
        else if (!receipt.Ok) Status.Show("The automatic backup did not finish: " + receipt.Message, StatusKind.Failure);
        Home.ShowGame();
    }

    private string GameLine() => Game.Busy ? "Checking the game folder…" : Game.Folder is GameFolder folder
        ? (_running ? "Game running" : folder.Target == GameTarget.OnslaughtCe ? "Onslaught CE" : folder.Executable.State == ExecutableState.Retail ? "Original game (Steam, unmodified)"
            : "Original game (BEA.exe differs from the Steam release)")
        : "No game folder";

    private void ShowCareerMenu()
    {
        PopupMenu menu = CareerMenu.GetPopup();
        menu.Clear();
        _careerMenuPaths.Clear();
        string? open = Workspace.Session?.Path;
        foreach (GameFile career in Game.Folder?.Careers.Where(file => file.Supported) ?? [])
        {
            menu.AddRadioCheckItem(career.DisplayName + (career.FromOriginalInstall ? " (original game, read-only)" : ""), _careerMenuPaths.Count);
            menu.SetItemChecked(menu.ItemCount - 1, string.Equals(career.Path, open, StringComparison.Ordinal));
            _careerMenuPaths.Add(career.Path);
        }
        if (menu.ItemCount > 0) menu.AddSeparator();
        menu.AddItem("Open a career file…", 1000);
        CareerMenu.Text = open is null ? "Choose a career" : System.IO.Path.GetFileNameWithoutExtension(open);
    }

    private void ChooseFromMenu(long id)
    {
        if (id == 1000)
            Home.OpenDialog.PopupCenteredRatio(0.75f);
        else if (id >= 0 && id < _careerMenuPaths.Count)
            Status.Track(ChooseCareerAsync(_careerMenuPaths[(int)id]));
    }

    private void RefreshHeader()
    {
        if (Current is null) return;
        PageTitle.Text = Current.Title.ToUpperInvariant();
        PageSubtitle.Text = Current.Subtitle;
    }

    private void RefreshActions()
    {
        CareerMenu.Disabled = Workspace.Busy;
        EditCareer.UpdateActions();
        Bytes.Refresh();
        if (Current == Backups) Backups.Refresh();
        if (Current == Cheats) Cheats.Refresh();
        RefreshHeader();
    }

    /// <summary>
    /// Scales the interface for high-density screens. Windows reports density through DPI rather than a
    /// scale, so the window is also enlarged to keep the same layout, within the screen's usable area.
    /// </summary>
    private static void FitToScreen(Window window)
    {
        float scale = OperatingSystem.IsWindows() ? DisplayServer.ScreenGetDpi() / 96f : DisplayServer.ScreenGetScale();
        if (scale <= 1.01f) return;
        window.ContentScaleFactor = scale;
        if (!OperatingSystem.IsWindows()) return;
        Vector2I usable = DisplayServer.ScreenGetUsableRect().Size;
        window.MinSize = new Vector2I((int)(1024 * scale), (int)(700 * scale)).Min(usable);
        window.Size = new Vector2I((int)(1280 * scale), (int)(800 * scale)).Min(usable - new Vector2I(40, 40));
        window.MoveToCenter();
    }

    private void OnCloseRequested() => RequestClose();
}
