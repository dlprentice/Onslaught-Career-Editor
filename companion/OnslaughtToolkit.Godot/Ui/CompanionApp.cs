// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// The companion's root. Everything below it is built in code; <c>Main.tscn</c> only attaches this
/// script to one node. It owns the sidebar, page header, pages, dialogs and status bar, and defers
/// closing while a protected file transaction is still running.
/// </summary>
public partial class CompanionApp : Control
{
    private readonly IProtectedSaveFiles? _files;
    private readonly bool _managesWindow;
    private readonly Dictionary<string, Page> _pages = [];

    public CompanionApp() : this(new ProtectedSaveFiles(), managesWindow: true)
    {
    }

    /// <summary>Hosts the companion inside another tree (tests, captures) with the given file access.</summary>
    internal CompanionApp(IProtectedSaveFiles? files, bool managesWindow)
        => (_files, _managesWindow) = (files, managesWindow);

    internal CareerWorkspace Workspace { get; private set; } = null!;
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
    internal EditCopyPage EditCopy { get; private set; } = null!;
    internal ComparePage Compare { get; private set; } = null!;
    internal StoredValuesPage StoredValues { get; private set; } = null!;
    internal MediaFilesPage MediaFiles { get; private set; } = null!;

    public override void _Ready()
    {
        Theme = CompanionTheme.Build();
        SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        Workspace = new CareerWorkspace(new SaveFileWorker(_files));
        Status = new StatusLine();
        this.Add(new ColorRect { Color = Palette.Background, MouseFilter = MouseFilterEnum.Ignore })
            .SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);

        Home = new HomePage(ShowOpenDialog);
        EditCopy = new EditCopyPage(Workspace, Status, this, OpenCareerAsync);
        Compare = new ComparePage(Workspace, Status, this);
        StoredValues = new StoredValuesPage(Workspace);
        MediaFiles = new MediaFilesPage(Status, this);
        (string, IReadOnlyList<Page>)[] groups =
        [
            ("Start", [Home]),
            ("Career", [EditCopy, Compare, StoredValues]),
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
        PageSubtitle = titles.Add(Build.Text("", "Muted", wrap: false));
        VBoxContainer career = header.Add(Build.Column(0));
        career.SizeFlagsVertical = SizeFlags.ShrinkCenter;
        career.Add(Build.Eyebrow("Open career")).HorizontalAlignment = HorizontalAlignment.Right;
        CareerName = career.Add(Build.Text("None", "Strong", wrap: false));
        CareerName.HorizontalAlignment = HorizontalAlignment.Right;
        CareerName.CustomMinimumSize = new Vector2(160, 0);
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
        Compare.Reset();
        CareerName.Text = System.IO.Path.GetFileName(session.Path);
        CareerName.TooltipText = session.Path;
        OpenButton.ThemeTypeVariation = "";
        if (Current == Home) Navigate("edit");
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
        Home.OpenCareer.Disabled = Workspace.Busy;
        EditCopy.UpdateActions();
        Compare.Refresh();
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
