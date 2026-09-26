// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Client;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// The production pause scene. Its editor mode only previews this presentation:
/// it never creates a game session, handles input, or changes pointer policy.
/// </summary>
[Tool]
public sealed partial class FirstFlightPauseMenu : CanvasLayer
{
    public const string ScenePath = "res://Scenes/Pause/PauseMenu.tscn";
    private const float NativeWidth = 640f;
    private const float NativeHeight = 480f;
    private const float FadeSeconds = 0.4f;
    private const float CircleGrowSeconds = 0.2f;
    private const float ItemRowHeight = 20f;
    // Retail confirmation-prompt framing.
    //
    // CPauseMenu__Render (0x004d11d0) renders exactly one range out of the
    // pause range set -- CSPtrSet__At(this+0x14, this+0x24) -- and then
    // renders the optional prompt objects hanging off this+0x08 and
    // this+0x3c. Activating Retry (item 0x0cada9) or Quit (item 0x07a211)
    // in CPauseMenu__ButtonPressed (0x004d0810) allocates a CGameMenu into
    // this+0x08 and leaves the active range index this+0x24 at 0, so retail
    // does keep drawing the root list underneath the prompt.
    //
    // What keeps that legible is not a tint choice: the prompt range is
    // built by CMenuItemRangeVariant__Init(range, text 0x077780, 320.0,
    // 320.0, panel_flag=1, ...). CMenuItemRange__Render (0x004a4810) tests
    // that panel flag at +0x28 and, when set, calls
    // CMessageLog__RenderPanelFrame (0x004b9010) for an opaque frame behind
    // the prompt's own title and items. The root list carries panel_flag=0
    // (PauseMenu__Init 0x004cde60) and therefore never gets a frame.
    //
    // Retained scalar provenance from the previous renderer: lab BEA.exe
    // .rdata (sha256 e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4):
    //   _DAT_005dc240 = 1.1     file 0x1dc240  panel size factor
    //   _DAT_005d85ec = 0.5     file 0x1d85ec  centring halve
    //   _DAT_005dc568 = 160.0   file 0x1dc568  panel alpha scale
    //   _DAT_005db2b8 = 32.0    file 0x1db2b8  corner size
    //   _DAT_005dbb50 = 0.0625  file 0x1dbb50  edge stretch over the 16px blank
    // The alpha argument at the call site is 1.2, so the frame tint is
    // ROUND(1.2 * 160.0) = 192 over RGB 0 -- pure black, alpha 192/255,
    // the same 192 ceiling the fullscreen pause fade already uses.
    private const float PanelSizeFactor = 1.1f;
    private const float PanelTitleBand = 32f;
    private const float PanelWidthPadding = 16f;
    private const float PanelMinimumSize = 64f;
    private const float PanelCornerSize = 32f;

    private static readonly Color PanelTint = new(0f, 0f, 0f, 192f / 255f);
    private static readonly Color NormalColor = RetailColor(0xffd6d6d6);
    private static readonly Color SelectedColor = RetailColor(0xffffcc00);
    private static readonly Color DisabledColor = RetailColor(0x50505050);
    private static readonly Color TitleColor = RetailColor(0xff505050);

    private Level100PauseMenu _model = new();
    private Control _surface = null!;
    private Control _native = null!;
    private TextureRect _overlay = null!;
    private TextureRect _circle01 = null!;
    private TextureRect _circle02 = null!;
    private Control _rootRange = null!;
    private Control _confirmationRange = null!;
    private Control _frame = null!;
    private RetailBitmapLabel _rootTitle = null!;
    private RetailBitmapLabel _confirmationTitle = null!;
    private RetailBitmapLabel[] _rootRows = [];
    private RetailBitmapLabel[] _confirmationRows = [];
    private bool _bound;
    private bool _assetsLoaded;
    private string? _assetError;
    private float _openingSeconds;
    private float _closingSeconds;
    private bool _previewConfirmation;

    /// <summary>Editor-only presentation selection. Ignored during gameplay.</summary>
    [Export]
    public bool PreviewConfirmation
    {
        get => _previewConfirmation;
        set
        {
            _previewConfirmation = value;
            if (Engine.IsEditorHint() && _bound)
                ApplyEditorPreview();
        }
    }

    public bool InputReady => !Engine.IsEditorHint() && _bound &&
        _surface.Visible && !IsClosing && _openingSeconds >= FadeSeconds;
    public bool IsClosing { get; private set; }

    public static FirstFlightPauseMenu Create(Level100PauseMenu model)
    {
        var view = GD.Load<PackedScene>(ScenePath).Instantiate<FirstFlightPauseMenu>();
        view.Initialize(model);
        return view;
    }

    public void Initialize(Level100PauseMenu model)
    {
        _model = model;
        BindScene();
        if (IsInsideTree())
            Refresh();
    }

    public override void _Ready()
    {
        BindScene();
        LoadPresentationAssets();
        _surface.Resized += ApplyVisualState;
        if (Engine.IsEditorHint())
            ApplyEditorPreview();
        else
            Reset();
    }

    public override string[] _GetConfigurationWarnings() => _assetError is null
        ? []
        : ["Pause assets are unavailable. Use the supported private-asset preparation route. " + _assetError];

    private void BindScene()
    {
        if (_bound)
            return;
        _surface = GetNode<Control>("Surface");
        _native = GetNode<Control>("Surface/Native");
        _overlay = GetNode<TextureRect>("Surface/Overlay");
        _circle01 = GetNode<TextureRect>("Surface/Native/Circle01");
        _circle02 = GetNode<TextureRect>("Surface/Native/Circle02");
        _rootRange = GetNode<Control>("Surface/Native/RootRange");
        _confirmationRange = GetNode<Control>("Surface/Native/ConfirmationRange");
        _frame = _confirmationRange.GetNode<Control>("Frame");
        _rootTitle = _rootRange.GetNode<RetailBitmapLabel>("Title");
        _confirmationTitle = _confirmationRange.GetNode<RetailBitmapLabel>("Title");
        _rootRows = _rootRange.GetNode<Control>("Rows").GetChildren().Cast<RetailBitmapLabel>().ToArray();
        _confirmationRows = _confirmationRange.GetNode<Control>("Rows").GetChildren().Cast<RetailBitmapLabel>().ToArray();
        if (_rootRows.Length != _model.RootEntries.Count || _confirmationRows.Length != 2)
            throw new InvalidDataException("Pause scene rows do not match the retained menu contract.");
        _bound = true;
    }

    private void LoadPresentationAssets()
    {
        if (_assetsLoaded)
            return;
        try
        {
            Texture2D blank = CuratedAyaTextureLoader.Load(
                "res://Assets/PauseMenu/blank.texture.aya", 16, 16,
                CuratedAyaTextureLoader.Compression.Dxt1);
            _overlay.Texture = blank;
            _circle01.Texture = CuratedAyaTextureLoader.Load(
                "res://Assets/PauseMenu/circle-01.texture.aya", 256, 256);
            _circle02.Texture = CuratedAyaTextureLoader.Load(
                "res://Assets/PauseMenu/circle-02.texture.aya", 256, 256);
            Texture2D corner = CuratedAyaTextureLoader.Load(
                "res://Assets/PauseMenu/endcurve.texture.aya", 32, 32);
            foreach (TextureRect cell in _frame.GetChildren().Cast<TextureRect>())
            {
                cell.Texture = cell.Name.ToString().StartsWith("Corner", StringComparison.Ordinal) ? corner : blank;
                cell.SelfModulate = PanelTint;
            }
            var normalFont = new RetailBitmapFont(CuratedAyaTextureLoader.Load(
                "res://Assets/Hud/font-22.texture.aya", 512, 512,
                CuratedAyaTextureLoader.Compression.Rgba8), 32);
            var smallFont = new RetailBitmapFont(CuratedAyaTextureLoader.Load(
                "res://Assets/Hud/font-13ps.texture.aya", 256, 256,
                CuratedAyaTextureLoader.Compression.Rgba8), 16);
            _rootTitle.SetFont(normalFont);
            _confirmationTitle.SetFont(normalFont);
            foreach (RetailBitmapLabel row in _rootRows.Concat(_confirmationRows))
                row.SetFont(smallFont);
            _assetsLoaded = true;
            _assetError = null;
        }
        catch (Exception error) when (Engine.IsEditorHint() && error is IOException or InvalidDataException)
        {
            // Keep the authored control tree inspectable without private inputs.
            // A missing texture is not replaced by an approximate retail visual.
            _assetError = error.Message;
            UpdateConfigurationWarnings();
        }
    }

    private void ApplyEditorPreview()
    {
        _model = new Level100PauseMenu();
        _model.Open();
        if (PreviewConfirmation)
        {
            _model.Hover(6);
            _model.ActivateSelected();
        }
        _surface.Visible = true;
        IsClosing = false;
        _openingSeconds = FadeSeconds;
        _closingSeconds = 0f;
        ApplyVisualState();
    }

    public void Open()
    {
        _surface.Visible = true;
        IsClosing = false;
        _openingSeconds = 0f;
        _closingSeconds = 0f;
        ApplyVisualState();
    }

    public void Close()
    {
        if (!_surface.Visible)
            return;
        IsClosing = true;
        _closingSeconds = 0f;
        ApplyVisualState();
    }

    public void Reset()
    {
        _surface.Visible = false;
        IsClosing = false;
        _openingSeconds = 0f;
        _closingSeconds = 0f;
    }

    public void AdvanceAnimation(double delta)
    {
        if (!_surface.Visible || !double.IsFinite(delta) || delta <= 0d)
            return;
        if (IsClosing)
        {
            _closingSeconds += (float)delta;
            if (_closingSeconds >= FadeSeconds)
                Reset();
        }
        else
            _openingSeconds = Math.Min(_openingSeconds + (float)delta, FadeSeconds);
        ApplyVisualState();
    }

    public void Refresh() => ApplyVisualState();

    public bool TryHover(Vector2 viewportPosition) => TryPointAt(viewportPosition, out bool moved) && moved;

    public bool TryPointAt(Vector2 viewportPosition, out bool moved)
    {
        int index = HitTest(viewportPosition);
        if (index < 0 || !_model.Entries[index].IsEnabled)
        {
            moved = false;
            return false;
        }
        moved = _model.Hover(index);
        if (moved)
            Refresh();
        return true;
    }

    private int HitTest(Vector2 viewportPosition)
    {
        if (!InputReady || _surface.Size.Y <= 0f)
            return -1;
        float scale = _surface.Size.Y / NativeHeight;
        float horizontalOffset = (_surface.Size.X - (NativeWidth * scale)) * 0.5f;
        Vector2 native = new((viewportPosition.X - horizontalOffset) / scale, viewportPosition.Y / scale);
        if (native.X < 0f || native.X > NativeWidth)
            return -1;
        RetailBitmapLabel[] rows = _model.Page == Level100PausePage.Root ? _rootRows : _confirmationRows;
        for (int index = 0; index < rows.Length; index++)
        {
            // Authored rectangles own both presentation and hit regions. The
            // retained 20px rows and their half-open edges are checked headlessly.
            float top = rows[index].Position.Y;
            if (native.Y >= top && native.Y < top + rows[index].Size.Y)
                return index;
        }
        return -1;
    }

    private void ApplyVisualState()
    {
        if (!_bound || !_surface.Visible || _surface.Size.X <= 0f || _surface.Size.Y <= 0f)
            return;
        float scale = _surface.Size.Y / NativeHeight;
        _native.Position = new Vector2((_surface.Size.X - (NativeWidth * scale)) * 0.5f, 0f);
        _native.Scale = Vector2.One * scale;
        float transitionSeconds = IsClosing ? Math.Max(0f, FadeSeconds - _closingSeconds) : _openingSeconds;
        float overlayAlpha = Math.Clamp((float)Math.Round(transitionSeconds * 480f) / 255f, 0f, 192f / 255f);
        _overlay.SelfModulate = new Color(16f / 255f, 16f / 255f, 16f / 255f, overlayAlpha);
        float circleScale = transitionSeconds < CircleGrowSeconds ? 0.1f + (transitionSeconds * 5f * 1.1f) : 1.2f;
        float rotation = transitionSeconds < CircleGrowSeconds ? 0f :
            Math.Clamp(transitionSeconds, CircleGrowSeconds, FadeSeconds) - CircleGrowSeconds;
        _circle01.Scale = _circle02.Scale = Vector2.One * circleScale;
        _circle01.Rotation = -rotation;
        _circle02.Rotation = rotation;
        _rootRange.Visible = transitionSeconds >= FadeSeconds;
        bool confirmation = _model.Page is Level100PausePage.ConfirmRetry or Level100PausePage.ConfirmQuit;
        _confirmationRange.Visible = _rootRange.Visible && confirmation;
        ApplyMenuRange(_rootTitle, _rootRows, "PAUSED", _model.RootEntries,
            confirmation ? _model.UnderlyingRootSelection : _model.SelectedIndex);
        if (confirmation)
        {
            ApplyMenuRange(_confirmationTitle, _confirmationRows, "Are you sure?", _model.Entries,
                _model.SelectedIndex);
            ArrangePanelFrame("Are you sure?", _model.Entries, _model.Page);
        }
    }

    private static void ApplyMenuRange(RetailBitmapLabel titleControl, RetailBitmapLabel[] rows,
        string title, IReadOnlyList<Level100PauseEntry> entries, int selectedIndex)
    {
        titleControl.Text = title;
        titleControl.TextColor = TitleColor;
        titleControl.Shadow = false;
        for (int index = 0; index < entries.Count; index++)
        {
            rows[index].Text = entries[index].Label;
            rows[index].TextColor = !entries[index].IsEnabled ? DisabledColor :
                index == selectedIndex ? SelectedColor : NormalColor;
            rows[index].Shadow = true;
        }
    }

    private void ArrangePanelFrame(string title, IReadOnlyList<Level100PauseEntry> entries, Level100PausePage page)
    {
        float widest = _confirmationTitle.Measure(title);
        float itemHeights = 0f;
        foreach (Level100PauseEntry entry in entries)
        {
            widest = Math.Max(widest, _confirmationRows[0].Measure(entry.Label));
            itemHeights += ItemRowHeight;
        }
        float rawWidth = (widest + PanelWidthPadding) * PanelSizeFactor;
        float rawHeight = (PanelTitleBand + itemHeights) * PanelSizeFactor;
        float left = MathF.Round(320f - (rawWidth * 0.5f));
        float top = MathF.Round(GetRangeCenterY(page) - (rawHeight * 0.5f));
        float width = Math.Max(PanelMinimumSize, MathF.Round(rawWidth));
        float height = Math.Max(PanelMinimumSize, MathF.Round(rawHeight));
        float innerWidth = width - (PanelCornerSize * 2f);
        float innerHeight = height - (PanelCornerSize * 2f);
        float right = left + width - PanelCornerSize;
        float bottom = top + height - PanelCornerSize;
        // Native 32px lower-left-opaque quarter cells and UV mirroring are
        // unchanged from CMessageLog__RenderPanelFrame's retained mapping.
        SetPanelCell("CornerTopLeft", left, top, PanelCornerSize, PanelCornerSize);
        SetPanelCell("CornerTopRight", right, top, PanelCornerSize, PanelCornerSize);
        SetPanelCell("CornerBottomRight", right, bottom, PanelCornerSize, PanelCornerSize);
        SetPanelCell("CornerBottomLeft", left, bottom, PanelCornerSize, PanelCornerSize);
        SetPanelCell("Top", left + PanelCornerSize, top, innerWidth, PanelCornerSize);
        SetPanelCell("Bottom", left + PanelCornerSize, bottom, innerWidth, PanelCornerSize);
        SetPanelCell("Left", left, top + PanelCornerSize, PanelCornerSize, innerHeight);
        SetPanelCell("Right", right, top + PanelCornerSize, PanelCornerSize, innerHeight);
        SetPanelCell("Center", left + PanelCornerSize, top + PanelCornerSize, innerWidth, innerHeight);
    }

    private void SetPanelCell(string name, float x, float y, float width, float height)
    {
        var cell = _frame.GetNode<TextureRect>(name);
        cell.Position = new Vector2(x, y);
        cell.Size = new Vector2(Math.Max(0f, width), Math.Max(0f, height));
        cell.Visible = width > 0f && height > 0f;
    }

    private static float GetRangeCenterY(Level100PausePage page) =>
        page is Level100PausePage.ConfirmRetry or Level100PausePage.ConfirmQuit ? 320f : 240f;
    private static Color RetailColor(uint argb) => new(
        ((argb >> 16) & 0xff) / 255f, ((argb >> 8) & 0xff) / 255f,
        (argb & 0xff) / 255f, ((argb >> 24) & 0xff) / 255f);
}
