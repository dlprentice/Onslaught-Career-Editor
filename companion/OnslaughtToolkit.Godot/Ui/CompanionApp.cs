// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// The companion's root. Everything below it is built in code; <c>Main.tscn</c> only attaches this
/// script to one node. It owns the shared header, pages, dialogs and footer, and defers closing
/// while a protected file transaction is still running.
/// </summary>
public partial class CompanionApp : Control
{
    private readonly IProtectedSaveFiles? _files;
    private readonly bool _managesWindow;

    public CompanionApp() : this(new ProtectedSaveFiles(), managesWindow: true)
    {
    }

    /// <summary>Hosts the companion inside another tree (tests, captures) with the given file access.</summary>
    internal CompanionApp(IProtectedSaveFiles? files, bool managesWindow)
        => (_files, _managesWindow) = (files, managesWindow);

    internal CareerWorkspace Workspace { get; private set; } = null!;
    internal StatusLine Status { get; private set; } = null!;
    internal Button OpenButton { get; private set; } = null!;
    internal FileDialog OpenDialog { get; private set; } = null!;
    internal TabContainer Tabs { get; private set; } = null!;
    internal SaveLabPage SaveLab { get; private set; } = null!;
    internal InspectorPage Inspector { get; private set; } = null!;
    internal ComparePage Compare { get; private set; } = null!;
    internal MediaPage Media { get; private set; } = null!;

    public override void _Ready()
    {
        Theme = CompanionTheme.Build();
        SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        Workspace = new CareerWorkspace(new SaveFileWorker(_files));
        Status = new StatusLine();

        MarginContainer margin = this.Add(new MarginContainer());
        margin.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        foreach ((string side, int size) in new[] { ("left", 28), ("right", 28), ("top", 20), ("bottom", 20) })
            margin.AddThemeConstantOverride("margin_" + side, size);
        VBoxContainer layout = margin.Add(Build.Column(16));

        HBoxContainer header = layout.Add(new HBoxContainer());
        VBoxContainer brand = header.Add(new VBoxContainer { SizeFlagsHorizontal = SizeFlags.ExpandFill });
        brand.Add(Build.Text("Onslaught Toolkit", CompanionTheme.TitleSize, CompanionTheme.Accent));
        brand.Add(Build.Text("Careers, verified copies & preservation"));
        OpenButton = header.Add(Build.Button("Open career…", "Choose a real .bes career save. Ctrl+O"));
        OpenButton.SizeFlagsVertical = SizeFlags.ShrinkCenter;

        Tabs = layout.Add(new TabContainer { SizeFlagsVertical = SizeFlags.ExpandFill });
        SaveLab = new SaveLabPage(Workspace, Status, this, OpenCareerAsync);
        Inspector = new InspectorPage();
        Compare = new ComparePage(Workspace, Status, this);
        Media = new MediaPage(Status, this);
        Tabs.Add(SaveLab.Root);
        Tabs.Add(Inspector.Root);
        Tabs.Add(Compare.Root);
        Tabs.Add(Media.Root);
        layout.Add(Status.Root);

        OpenDialog = this.Add(Build.FilePicker("Open a career save", FileDialog.FileModeEnum.OpenFile, "*.bes ; Career saves"));
        OpenButton.Pressed += ShowOpenDialog;
        OpenDialog.FileSelected += path => Status.Track(OpenCareerAsync(path));
        Workspace.Changed += RefreshActions;
        Workspace.SessionOpened += ShowSession;

        if (_managesWindow)
        {
            GetWindow().MinSize = new Vector2I(920, 700);
            GetTree().AutoAcceptQuit = false;
            GetWindow().CloseRequested += OnCloseRequested;
        }
        if (!Workspace.IsAvailable) Status.Show(SaveFileWorker.UnavailableMessage, failed: true);
        RefreshActions();
    }

    public override void _ExitTree()
    {
        if (Workspace is null) return;
        if (_managesWindow) GetWindow().CloseRequested -= OnCloseRequested;
        Media.Cancel();
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

    /// <summary>Opens a career as the new original. A refusal keeps the previous original open.</summary>
    internal async Task<Outcome<SaveSession>> OpenCareerAsync(string path)
    {
        if (Workspace.Busy) return Outcome<SaveSession>.Refusal("A file operation is already running.");
        Status.Show("Opening and checking the career…");
        Outcome<SaveSession> opened = await Workspace.OpenAsync(path);
        Status.Show(opened.Ok
            ? "Career opened and protected snapshot verified. Select edits or make an unchanged recovery copy."
            : opened.Message, failed: !opened.Ok);
        return opened;
    }

    private void ShowOpenDialog()
    {
        if (!Workspace.Busy) OpenDialog.PopupCenteredRatio(0.75f);
    }

    private void ShowSession()
    {
        if (Workspace.Session is not SaveSession session) return;
        SaveLab.ShowSession(session);
        Inspector.ShowSession(session);
        Compare.Reset();
    }

    private void RefreshActions()
    {
        OpenButton.Disabled = Workspace.Busy;
        SaveLab.UpdateActions();
        Compare.UpdateActions();
    }

    private void OnCloseRequested()
    {
        if (Workspace.Busy)
            Status.Show("A file operation is still finishing. Wait for its result before closing.");
        else
            GetTree().Quit();
    }
}
