// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// The companion's root. Everything below it is built in code; <c>Main.tscn</c> only attaches this
/// script to one node. It owns the sidebar, page header, pages, dialogs and status bar, and defers
/// closing while a protected file transaction is still running.
/// </summary>
/// <summary>Where the companion looks for Steam and keeps its settings; tests and captures supply their own.</summary>
internal sealed record CompanionEnvironment(IReadOnlyList<string> SteamRoots, string SettingsPath, Func<bool>? GameRunning = null)
{
    internal static CompanionEnvironment Default() =>
        new(SteamLibraries.DefaultRoots(), ProjectSettings.GlobalizePath("user://settings.json"), GameProcess.IsRunning);
}

public partial class CompanionApp : Control
{
    private readonly IProtectedSaveFiles? _files;
    private readonly bool _managesWindow;
    private readonly CompanionEnvironment? _environment;
    private readonly Dictionary<string, Page> _pages = [];

    public CompanionApp() : this(new ProtectedSaveFiles(), managesWindow: true)
    {
    }

    /// <summary>Hosts the companion inside another tree (tests, captures) with the given file access and environment.</summary>
    internal CompanionApp(IProtectedSaveFiles? files, bool managesWindow, CompanionEnvironment? environment = null)
        => (_files, _managesWindow, _environment) = (files, managesWindow, environment);

    internal CareerWorkspace Workspace { get; private set; } = null!;
    internal GameLibrary Game { get; private set; } = null!;
    internal StatusLine Status { get; private set; } = null!;
    internal Sidebar Sidebar { get; private set; } = null!;
    internal Label PageTitle { get; private set; } = null!;
    internal Label PageSubtitle { get; private set; } = null!;
    internal Label CareerName { get; private set; } = null!;
    internal Button OpenButton { get; private set; } = null!;
    internal FileDialog OpenDialog { get; private set; } = null!;
    internal IReadOnlyDictionary<string, Page> Pages => _pages;
    internal Page Current { get; private set; } = null!;
    internal HomePage Home { get; private set; } = null!;
    internal OverviewPage Overview { get; private set; } = null!;
    internal GoodiesPage Goodies { get; private set; } = null!;
    internal InstallPage Install { get; private set; } = null!;
    internal EditCopyPage EditCopy { get; private set; } = null!;
    internal ComparePage Compare { get; private set; } = null!;
    internal StoredValuesPage StoredValues { get; private set; } = null!;
    internal MediaFilesPage MediaFiles { get; private set; } = null!;

    public override void _Ready()
    {
        Theme = CompanionTheme.Build();
        SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        Workspace = new CareerWorkspace(new SaveFileWorker(_files));
        CompanionEnvironment environment = _environment ?? CompanionEnvironment.Default();
        Game = new GameLibrary(environment.SteamRoots, new SettingsStore(environment.SettingsPath));
        Status = new StatusLine();
        this.Add(new ColorRect { Color = Palette.Background, MouseFilter = MouseFilterEnum.Ignore })
            .SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);

        Home = new HomePage(Game, Status, this, ShowOpenDialog, OpenCareerAsync);
        EditCopy = new EditCopyPage(Workspace, Game, Status, this, OpenCareerAsync);
        Overview = new OverviewPage(Workspace, Game, () => Navigate("goodies"));
        Goodies = new GoodiesPage(Workspace, Game, index =>
        {
            EditCopy.AddGoodie(index);
            Navigate("edit");
        });
        Compare = new ComparePage(Workspace, Status, this);
        StoredValues = new StoredValuesPage(Workspace);
        MediaFiles = new MediaFilesPage(Status, this);
        Install = new InstallPage(Workspace, Game, Status, this, environment.GameRunning ?? GameProcess.IsRunning);
        (string, IReadOnlyList<Page>)[] groups =
        [
            ("Start", [Home]),
            ("Career", [Overview, Goodies, EditCopy, Compare, StoredValues]),
            ("Game", [Install]),
            ("Library", [MediaFiles]),
        ];

        VBoxContainer frame = this.Add(Build.Column(0));
        frame.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        HBoxContainer body = frame.Add(Build.Row(0));
        body.SizeFlagsVertical = SizeFlags.ExpandFill;
        Sidebar = new Sidebar(groups, Navigate);
        body.Add(Sidebar.Root);
        VBoxContainer main = body.Add(Build.Column(0));
        main.SizeFlagsHorizontal = SizeFlags.ExpandFill;

        HBoxContainer header = main.Add(Build.Margin(30, 22, 30, 14)).Add(Build.Row(18));
        VBoxContainer titles = header.Add(Build.Column(2));
        titles.SizeFlagsHorizontal = SizeFlags.ExpandFill;
        PageTitle = titles.Add(Build.Heading("", "Title"));
        PageSubtitle = titles.Add(Build.Text("", "Muted", wrap: false, clip: true));
        VBoxContainer career = header.Add(Build.Column(0));
        career.SizeFlagsVertical = SizeFlags.ShrinkCenter;
        career.Add(Build.Eyebrow("Open career")).HorizontalAlignment = HorizontalAlignment.Right;
        CareerName = career.Add(Build.Text("None", "Strong", wrap: false, width: 220, clip: true));
        CareerName.HorizontalAlignment = HorizontalAlignment.Right;
        OpenButton = header.Add(Build.Button("Open career…", "Primary", "Choose a .bes career save (Ctrl+O)."));
        OpenButton.SizeFlagsVertical = SizeFlags.ShrinkCenter;

        MarginContainer hostMargin = main.Add(Build.Margin(30, 4, 30, 20));
        hostMargin.SizeFlagsVertical = SizeFlags.ExpandFill;
        VBoxContainer host = hostMargin.Add(Build.Column(0));
        foreach ((string _, IReadOnlyList<Page> pages) in groups)
        {
            foreach (Page page in pages)
            {
                _pages[page.Key] = page;
                page.Root.SizeFlagsVertical = SizeFlags.ExpandFill;
                page.Root.Visible = false;
                host.Add(page.Root);
            }
        }
        frame.Add(Status.Root);

        OpenDialog = this.Add(Build.FilePicker("Open a career save", FileDialog.FileModeEnum.OpenFile, "*.bes ; Career saves"));
        OpenButton.Pressed += ShowOpenDialog;
        OpenDialog.FileSelected += path => Status.Track(OpenCareerAsync(path));
        Workspace.Changed += RefreshActions;
        Workspace.SessionOpened += ShowSession;
        Game.Changed += ShowGameSummary;

        if (_managesWindow)
        {
            Window window = GetWindow();
            window.MinSize = new Vector2I(1024, 700);
            float scale = DisplayServer.ScreenGetScale();
            if (scale > 1.01f) window.ContentScaleFactor = scale;
            DisplayServer.SetIcon(Emblem.Icon());
            GetTree().AutoAcceptQuit = false;
            window.CloseRequested += OnCloseRequested;
        }
        if (!Workspace.IsAvailable) Status.Show(SaveFileWorker.UnavailableMessage, StatusKind.Failure);
        Navigate("home");
        RefreshActions();
        Status.Track(Game.DetectAsync());
    }

    public override void _ExitTree()
    {
        if (Workspace is null) return;
        if (_managesWindow) GetWindow().CloseRequested -= OnCloseRequested;
        MediaFiles.Cancel();
        // A close cannot abandon a write or claim it was cancelled.
        Workspace.WaitForCompletion();
    }

    public override void _UnhandledKeyInput(InputEvent @event)
    {
        if (@event is InputEventKey { Pressed: true, Echo: false, CtrlPressed: true, Keycode: Key.O } && !Workspace.Busy)
        {
            ShowOpenDialog();
            GetViewport().SetInputAsHandled();
        }
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

    /// <summary>Opens a career as the new original. A refusal keeps the previous original open.</summary>
    internal async Task<Outcome<SaveSession>> OpenCareerAsync(string path)
    {
        if (Workspace.Busy) return Outcome<SaveSession>.Refusal("A file operation is already running.");
        Status.Show("Opening and checking the career…");
        Outcome<SaveSession> opened = await Workspace.OpenAsync(path);
        if (opened.Ok)
            Status.Show("Career opened read-only; its content fingerprint and file identity are recorded.", StatusKind.Success);
        else
            Status.Show(opened.Message, StatusKind.Failure);
        return opened;
    }

    private void ShowOpenDialog()
    {
        if (!Workspace.Busy) OpenDialog.PopupCenteredRatio(0.75f);
    }

    private void ShowSession()
    {
        if (Workspace.Session is not SaveSession session) return;
        EditCopy.ShowSession(session);
        StoredValues.ShowSession(session);
        Overview.ShowSession(session);
        Goodies.ShowSession(session);
        Compare.Reset();
        CareerName.Text = System.IO.Path.GetFileName(session.Path);
        CareerName.TooltipText = session.Path;
        OpenButton.ThemeTypeVariation = "";
        if (Current == Home) Navigate("overview");
        RefreshHeader();
    }

    private void ShowGameSummary()
    {
        // Names arrive with the game's text; redraw the career pages that show them.
        if (!Game.Busy && Workspace.Session is SaveSession session)
        {
            Overview.ShowSession(session);
            Goodies.ShowSession(session);
        }
        Status.Game.Text = Game.Busy ? "Checking the game folder…" : Game.Folder is GameFolder folder
            ? (folder.Executable.State == ExecutableState.Retail ? "Game: Steam release" : "Game: BEA.exe differs from the Steam release")
            : "No game folder";
        RefreshHeader();
    }

    private void RefreshHeader()
    {
        if (Current is null) return;
        PageTitle.Text = Current.Title.ToUpperInvariant();
        PageSubtitle.Text = Current.Subtitle;
    }

    private void RefreshActions()
    {
        OpenButton.Disabled = Workspace.Busy;
        EditCopy.UpdateActions();
        Compare.Refresh();
        if (Current == Install) Install.Refresh();
        RefreshHeader();
    }

    private void OnCloseRequested()
    {
        if (Workspace.Busy)
            Status.Show("A file operation is still finishing. Wait for its result before closing.");
        else
            GetTree().Quit();
    }
}
