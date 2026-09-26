// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>Where the companion looks for Steam, keeps its settings and puts backups; tests and captures supply their own.</summary>
internal sealed record CompanionEnvironment(IReadOnlyList<string> SteamRoots, string SettingsPath, Func<bool>? GameRunning = null,
    Action<string>? OpenUrl = null, string? DefaultBackupFolder = null)
{
    internal const string BackupFolderName = "Battle Engine Aquila Backups";

    internal static CompanionEnvironment Default() =>
        new(SteamLibraries.DefaultRoots(), ProjectSettings.GlobalizePath("user://settings.json"), GameProcess.IsRunning);

    /// <summary>The player's Documents folder (or the app's own data folder) plus a clearly named backups folder.</summary>
    internal string BackupFolder()
    {
        if (DefaultBackupFolder is string chosen) return chosen;
        string documents = OS.GetSystemDir(OS.SystemDir.Documents);
        string root = !string.IsNullOrWhiteSpace(documents) && Directory.Exists(documents) ? documents : OS.GetUserDataDir();
        return System.IO.Path.Combine(root, BackupFolderName);
    }
}

/// <summary>
/// The companion's root. Everything below it is built in code; <c>Main.tscn</c> only attaches this
/// script to one node. It owns the sidebar, header, pages, dialogs and status bar, opens the player's
/// most recent career, keeps automatic backups when they are on, watches whether the game is running,
/// and defers closing while a file operation is still running.
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
    private bool _running, _openedFirstCareer, _autoBackupDone, _quietOpen;
    private double _sinceRunningCheck;

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
    internal ComparePage Compare { get; private set; } = null!;
    internal StoredValuesPage RawValues { get; private set; } = null!;
    internal MediaFilesPage MediaFiles { get; private set; } = null!;

    /// <summary>Whether the game was running at the last check; the header says so while it is.</summary>
    internal bool GameIsRunning => _running;

    public override void _Ready()
    {
        Theme = CompanionTheme.Build();
        SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        Workspace = new CareerWorkspace(new SaveFileWorker(_files));
        CompanionEnvironment environment = _environment ?? CompanionEnvironment.Default();
        SettingsStore settings = new(environment.SettingsPath);
        Game = new GameLibrary(environment.SteamRoots, settings);
        Status = new StatusLine();
        _gameRunning = environment.GameRunning ?? GameProcess.IsRunning;
        Action<string> openUrl = environment.OpenUrl ?? (url => OS.ShellOpen(url));
        this.Add(new ColorRect { Color = Palette.Background, MouseFilter = MouseFilterEnum.Ignore })
            .SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        Node popups = this;
        Services = new AppServices
        {
            Workspace = Workspace, Game = Game, Status = Status, Backups = new BackupLocation(settings, environment.BackupFolder()),
            GameRunning = () => _gameRunning(), OpenUrl = openUrl, Navigate = Navigate, OpenCareer = OpenCareerAsync, Popups = popups,
        };

        Home = new HomePage(Services);
        Summary = new SummaryPage(Services);
        EditCareer = new EditCareerPage(Services);
        Goodies = new GoodiesPage(Services, index =>
        {
            EditCareer.AddGoodie(index);
            Navigate("edit");
        });
        Cheats = new CheatsPage(Services);
        Settings = new SettingsPage(Services);
        Backups = new BackupsPage(Services);
        Music = new MusicPage(Game, Status);
        Lore = new LorePage(Game, Status, openUrl);
        Compare = new ComparePage(Workspace, Status, popups);
        RawValues = new StoredValuesPage(Workspace);
        MediaFiles = new MediaFilesPage(Status, popups);
        NavGroup[] groups =
        [
            new("", [Home]),
            new("Your career", [Summary, Goodies, EditCareer, Cheats]),
            new("Your game", [Settings, Backups]),
            new("Extras", [Music, Lore]),
            new("Advanced", [Compare, RawValues, MediaFiles], Folds: true),
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
        RunningBadge.TooltipText = "Battle Engine Aquila is running. The companion won't write into its folder until you close it.";
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
        MediaFiles.Cancel();
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

    public override void _UnhandledKeyInput(InputEvent @event)
    {
        if (@event is not InputEventKey { Pressed: true, Echo: false } key) return;
        if (key is { CtrlPressed: true, Keycode: Key.O } && !Workspace.Busy)
            Home.OpenDialog.PopupCenteredRatio(0.75f);
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

    /// <summary>Checks whether the game is running and updates what depends on it.</summary>
    internal void CheckRunning()
    {
        _sinceRunningCheck = 0;
        bool running = _gameRunning();
        if (running == _running) return;
        _running = running;
        RunningBadge.Visible = running;
        Home.ShowGame();
        Status.Game.Text = GameLine();
    }

    private void ShowSession()
    {
        if (Workspace.Session is not SaveSession session) return;
        EditCareer.ShowSession(session);
        RawValues.ShowSession(session);
        Summary.ShowSession(session);
        Goodies.ShowSession(session);
        Cheats.ShowSession(session);
        Compare.Reset();
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
        if (Workspace.Session is not null) return;
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
        ? (_running ? "Game running" : folder.Executable.State == ExecutableState.Retail ? "Steam version found" : "Game found (changed BEA.exe)")
        : "No game folder";

    private void ShowCareerMenu()
    {
        PopupMenu menu = CareerMenu.GetPopup();
        menu.Clear();
        _careerMenuPaths.Clear();
        string? open = Workspace.Session?.Path;
        foreach (GameFile career in Game.Folder?.Careers.Where(file => file.Supported) ?? [])
        {
            menu.AddRadioCheckItem(career.DisplayName, _careerMenuPaths.Count);
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
            Status.Track(OpenCareerAsync(_careerMenuPaths[(int)id]));
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
        Compare.Refresh();
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

    private void OnCloseRequested()
    {
        if (Workspace.Busy)
            Status.Show("A file operation is still finishing. Wait for its result before closing.");
        else
            GetTree().Quit();
    }
}
