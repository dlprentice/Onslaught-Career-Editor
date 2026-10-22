// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Assets;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// The open career's Goodies laid out as the game's gallery wall, row by row, in the game's own colours,
/// with each unlock rule and how far the evidence for it goes, and what each Goodie shows: its picture, model, cutscene
/// or race level, read from the player's install. Slots 071–073, which the wall never shows, are listed apart.
/// Read-only; a change is prepared on Edit a copy, and copies of pictures and models are saved from Art &amp; sound.
/// </summary>
internal sealed class GoodiesPage : Page
{
    /// <summary>What each wall row holds, as the developers' source names it (FEPGoodies.cpp:393-437).</summary>
    private static readonly string[] RowNames =
        ["Row 1 · character bios, race levels and developer extras", "Row 2 · units", "Row 3 · cutscenes", "Row 4 · concept art"];

    private static readonly (string Label, Func<GoodieState, bool> Matches)[] Filters =
    [
        ("All", _ => true),
        ("Earned", state => state is GoodieState.New or GoodieState.Old),
        ("New", state => state == GoodieState.New),
        ("Hints", state => state == GoodieState.Hint),
        ("Locked", state => state is GoodieState.Locked or GoodieState.Unknown),
    ];

    private readonly CareerWorkspace _workspace;
    private readonly GameLibrary _game;
    private readonly Action<int> _changeInCopy;
    private readonly Action<string> _openAsset;
    private readonly Label _contentText;
    private readonly TextureRect _contentImage;
    private string? _contentFile;
    private bool _revealed;
    private readonly Label _empty, _summary;
    private readonly CareerCards _choose;
    private readonly VBoxContainer _grid;
    private readonly List<(Control Section, int[] Slots)> _sections = [];
    private readonly Button[] _cells = new Button[CareerSave.GoodieTable];
    private readonly ButtonGroup _selection = new();
    private readonly Label _detailTitle, _detailName, _detailState, _detailRule, _detailEvidence;
    private readonly PanelContainer _detail;
    private readonly List<Button> _filterButtons = [];
    private int _filter;

    internal GoodiesPage(AppServices app, Action<int> changeInCopy, Action<string> openAsset) : base("goodies", "Goodies", "goodies")
    {
        (_workspace, _game, _changeInCopy, _openAsset) = (app.Workspace, app.Game, changeInCopy, openAsset);
        HBoxContainer layout = Build.Row(16);
        layout.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        Root = layout;

        (ScrollContainer scroll, VBoxContainer left) = Build.Scroller(12);
        scroll.SizeFlagsStretchRatio = 2.2f;
        layout.Add(scroll);
        _empty = left.Add(Build.Text("Choose a career to see its Goodies. Opening it only reads it.", "Lead"));
        _choose = new CareerCards(app);
        left.Add(_choose.Root);
        _summary = left.Add(Build.Text("", "Strong"));
        HBoxContainer filters = left.Add(Build.Row(8));
        for (int index = 0; index < Filters.Length; index++)
        {
            int chosen = index;
            Button filter = filters.Add(Build.Button(Filters[index].Label, index == 0 ? "Primary" : ""));
            filter.Pressed += () => ApplyFilter(chosen);
            _filterButtons.Add(filter);
        }
        _grid = left.Add(Build.Column(14));
        for (int row = 0; row < CareerSave.GalleryRows.Count; row++)
            AddSection(RowNames[row], [.. CareerSave.GalleryRows[row]]);
        AddSection("Never shown in the game · 071–073", [.. CareerSave.NeverShown]);
        _grid.Add(Build.Text("Rows follow the game's gallery wall, top to bottom.", "Faint"));

        (_detail, VBoxContainer detail) = Build.Panel("Card", 8);
        _detail.CustomMinimumSize = new Vector2(330, 0);
        _detail.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        _detail.SizeFlagsVertical = Control.SizeFlags.ShrinkBegin;
        // The detail panel scrolls on its own, so a tall picture never pushes the page past the window.
        (ScrollContainer detailScroll, VBoxContainer detailColumn) = Build.Scroller(0);
        detailScroll.CustomMinimumSize = new Vector2(344, 0);
        layout.Add(detailScroll);
        detailColumn.Add(_detail);
        _detailTitle = detail.Add(Build.Heading("Goodie"));
        _detailName = detail.Add(Build.Text("", "Strong"));
        _detailState = detail.Add(Build.Text("", "Data"));
        detail.Add(Build.Eyebrow("How the game unlocks it"));
        _detailRule = detail.Add(Build.Text(""));
        _detailEvidence = detail.Add(Build.Text("", "Muted"));
        ChangeInCopy = detail.Add(Build.Button("Change this Goodie…", tooltip: "Adds this Goodie to Edit career, where you save the change."));
        ChangeInCopy.Icon = Icons.Get("edit");
        ChangeInCopy.SizeFlagsHorizontal = Control.SizeFlags.ShrinkBegin;
        ChangeInCopy.Pressed += () => _changeInCopy(Selected);

        detail.Add(Build.Eyebrow("What it shows"));
        _contentText = detail.Add(Build.Text(""));
        _contentImage = detail.Add(new TextureRect
        {
            ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize, StretchMode = TextureRect.StretchModeEnum.KeepAspectCentered,
            CustomMinimumSize = new Vector2(0, 200), Visible = false,
        });
        HBoxContainer contentActions = detail.Add(Build.Row(8));
        ShowAnyway = contentActions.Add(Build.Button("Show it anyway", tooltip: "Shows what this Goodie holds, though this career has not earned it."));
        ShowAnyway.Pressed += () =>
        {
            _revealed = true;
            ShowContent(Selected);
        };
        OpenAsset = contentActions.Add(Build.Button("Open in Art & sound", tooltip: "Shows it in Art & sound, where you can turn it and save a copy."));
        OpenAsset.Pressed += () =>
        {
            if (_contentFile is string file) _openAsset(file);
        };
        ShowEmpty();
    }

    internal override Control Root { get; }
    internal override string Subtitle => "Unlockables in the game's own colours: gold is new, blue is viewed";
    /// <summary>One cell per slot of the game's Goodie table, indexed by slot number.</summary>
    internal IReadOnlyList<Button> Cells => _cells;
    internal int Selected { get; private set; } = -1;
    internal string DetailEvidence => _detailEvidence.Text;
    internal string DetailRule => _detailRule.Text;
    internal Button ChangeInCopy { get; }
    internal Button ShowAnyway { get; }
    internal Button OpenAsset { get; }
    internal string ContentText => _contentText.Text;
    internal Texture2D? ContentImage => _contentImage.Visible ? _contentImage.Texture : null;
    internal GoodieContent? Content { get; private set; }

    internal void ShowSession(SaveSession session)
    {
        CareerInspection career = session.Analysis;
        _empty.Visible = _choose.Root.Visible = false;
        _grid.Visible = _detail.Visible = _summary.Visible = true;
        foreach (Button filter in _filterButtons) filter.Visible = true;
        GoodieCensus census = career.GoodieCensus;
        _summary.Text = $"{census.New + census.Old} of {census.Shown} earned  ·  {census.New} new  ·  {census.Old} viewed  ·  " +
            $"{census.Hint} hints  ·  {census.Locked} locked" + (census.Unknown > 0 ? $"  ·  {census.Unknown} unknown values" : "") +
            (census.NeverShownEarned > 0 ? $"  ·  {census.NeverShownEarned} of 071–073 earned, never shown" : "");
        for (int index = 0; index < _cells.Length; index++)
        {
            GoodieState state = career.Goodies[index].State;
            _cells[index].ThemeTypeVariation = state switch
            {
                GoodieState.New => "GoodieNew",
                GoodieState.Old => "GoodieViewed",
                GoodieState.Hint => "GoodieHint",
                GoodieState.Unknown => "GoodieUnknown",
                _ => "GoodieLocked",
            };
            _cells[index].TooltipText = $"Goodie {index:D3}: {GoodieFacts.StateName(state)}" +
                (_game.Text?.GoodieTitle(index) is string title ? $"\n{title}" : "");
        }
        ApplyFilter(_filter);
        Select(Selected >= 0 ? Selected : 0);
    }

    internal void Select(int index)
    {
        if (_workspace.Session is not SaveSession session || index < 0 || index >= _cells.Length) return;
        if (index != Selected) _revealed = false;
        Selected = index;
        // Setting a toggle without a signal does not release the rest of its group, so do it here.
        for (int cell = 0; cell < _cells.Length; cell++) _cells[cell].SetPressedNoSignal(cell == index);
        GoodieRecord goodie = session.Analysis.Goodies[index];
        _detailTitle.Text = $"GOODIE {index:D3}";
        _detailName.Text = _game.Text?.GoodieTitle(index) ?? (_game.Folder is null
            ? "Titles come from your game's own text; choose your game folder on Home."
            : _game.Text is null ? "Your game's text could not be read, so titles are not shown."
            : "The game's text names no title for this Goodie.");
        _detailName.ThemeTypeVariation = _game.Text?.GoodieTitle(index) is null ? "Faint" : "Strong";
        _detailState.Text = GoodieFacts.StateName(goodie.State);
        _detailRule.Text = GoodieFacts.Rule(index);
        _detailEvidence.Text = GoodieFacts.Describe(GoodieFacts.Evidence(index));
        ChangeInCopy.Disabled = !goodie.Shown;
        ChangeInCopy.TooltipText = goodie.Shown ? "Adds this Goodie to Edit career, where you save the change."
            : "The game never shows this slot, so its state is kept.";
        ShowContent(index);
    }

    /// <summary>What the Goodie shows, from the install: hidden behind "Show it anyway" until this career has earned it.</summary>
    private void ShowContent(int index)
    {
        Content = null;
        _contentFile = null;
        _contentImage.Visible = false;
        _contentImage.Texture = null;
        ShowAnyway.Visible = OpenAsset.Visible = false;
        if (_workspace.Session is not SaveSession session) return;
        if (_game.Folder is not GameFolder folder)
        {
            _contentText.Text = "Choose your game folder on Home to see what this Goodie shows.";
            return;
        }
        bool earned = session.Analysis.Goodies[index].State is GoodieState.New or GoodieState.Old;
        if (!earned && !_revealed)
        {
            _contentText.Text = "Not earned in this career yet, so it stays hidden here too.";
            ShowAnyway.Visible = true;
            return;
        }
        GoodieContent content;
        try
        {
            content = GoodieResources.Read(folder.Root, index);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or InvalidDataException)
        {
            _contentText.Text = "This Goodie's file in your game could not be read: " + error.Message;
            return;
        }
        Content = content;
        string resources = Path.Combine(folder.Root, "data", "resources");
        string missing = content.Missing.Count == 0 ? "" : "\nYour game is missing " + string.Join(", ", content.Missing) + ".";
        switch (content.Kind)
        {
            case GoodieKind.Image:
                _contentFile = GoodieResources.Resolve(resources, content.Image!);
                _contentText.Text = "A picture: " + AssetLibrary.TextureTitle(Path.GetFileName(content.Image!)) + missing;
                if (_contentFile is not null) ShowPicture(_contentFile);
                break;
            case GoodieKind.Model:
                _contentFile = GoodieResources.Resolve(resources, content.Mesh!);
                _contentText.Text = $"A 3D model: {AssetLibrary.ModelTitle(Path.GetFileName(content.Mesh!))}, " +
                    $"with {Build.Count(content.Files.Count - 2, "texture")} and a backdrop. Open it to turn it and see its animations." + missing;
                break;
            case GoodieKind.Video:
                _contentText.Text = $"A video: data/video/{content.Video}. It is Bink video, which the companion cannot play; " +
                    "watch it in the game's gallery." + missing;
                break;
            default:
                _contentText.Text = $"A race level: the game's gallery starts race level {content.Level}.";
                break;
        }
        OpenAsset.Visible = _contentFile is not null && content.Missing.Count == 0;
    }

    private void ShowPicture(string path)
    {
        try
        {
            DdsImage image = DdsTexture.Decode(AyaContainer.Inflate(File.ReadAllBytes(path)));
            _contentImage.Texture = ImageTexture.CreateFromImage(AssetsPage.ToImage(image));
            _contentImage.Visible = true;
            _contentText.Text += $" · {image.Width} × {image.Height}";
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or InvalidDataException)
        {
            _contentText.Text += "\nThe picture could not be read: " + error.Message;
        }
    }

    private void ApplyFilter(int filter)
    {
        _filter = filter;
        for (int index = 0; index < _filterButtons.Count; index++)
            _filterButtons[index].ThemeTypeVariation = index == filter ? "Primary" : "";
        if (_workspace.Session is not SaveSession session) return;
        IReadOnlyList<GoodieRecord> goodies = session.Analysis.Goodies;
        for (int index = 0; index < _cells.Length; index++)
            _cells[index].Visible = Filters[filter].Matches(goodies[index].State);
        // A row with nothing left to show under this filter is hidden with its heading.
        foreach ((Control section, int[] slots) in _sections) section.Visible = slots.Any(slot => _cells[slot].Visible);
    }

    private void AddSection(string heading, int[] slots)
    {
        VBoxContainer section = _grid.Add(Build.Column(6));
        section.Add(Build.Eyebrow(heading));
        HFlowContainer cells = section.Add(new HFlowContainer());
        cells.AddThemeConstantOverride("h_separation", 5);
        cells.AddThemeConstantOverride("v_separation", 5);
        foreach (int slot in slots)
        {
            Button cell = cells.Add(new Button
            {
                Text = slot.ToString("D3"), ToggleMode = true, ButtonGroup = _selection, CustomMinimumSize = new Vector2(38, 30),
                ThemeTypeVariation = "GoodieLocked", FocusMode = Control.FocusModeEnum.All,
            });
            cell.Pressed += () => Select(slot);
            _cells[slot] = cell;
        }
        _sections.Add((section, slots));
    }

    internal override void Refresh()
    {
        if (_workspace.Session is null) ShowEmpty();
    }

    private void ShowEmpty()
    {
        _empty.Visible = _choose.Root.Visible = true;
        _choose.Show();
        _grid.Visible = _detail.Visible = _summary.Visible = false;
        foreach (Button filter in _filterButtons) filter.Visible = false;
    }
}
