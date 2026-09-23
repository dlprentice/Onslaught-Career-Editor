// SPDX-License-Identifier: GPL-3.0-or-later
using Godot;
using OnslaughtRebuild.Client;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Test-only retained Select Configuration renderer from 7474445c. Its original
/// draw/font helpers and six Frontend.tscn source frames retain operation order.
/// The session is reduced to the one supplied immutable configuration record.
/// Default equivalence does not claim full retail parity: model/icons/stars,
/// the existing static-background fit stay unresolved. Other frontend pages
/// have a measured dev6 header offset; this harness does not measure retail
/// Configuration pixels. Explicit native text overrides are tested separately.
/// </summary>
public sealed partial class ConfigurationReference : Control
{
    private const int GlyphColumns = 16, GlyphCellSize = 16, FirstGlyph = 32, GlyphSlotCount = 256;
    private const int Font22Columns = 16, Font22CellSize = 32;
    private const string SelectConfigurationTitle = "SELECT CONFIGURATION";
    private const float HeaderBarCenterX = 390f, HeaderTitleTop = 65f;
    private const float ConfigurationUnitLeft = 260.5f, ConfigurationUnitTop = 99.5f;
    private const float ConfigurationRowLeft = 280f, ConfigurationRowPitch = 16f, ConfigurationWalkerTop = 210f, ConfigurationJetTop = 274f;
    private const float BriefingBackgroundScale = 1.25f, BriefingBackgroundLeft = -70f, BriefingBackgroundTop = -80f;
    private const float BriefingRingSize = 990f, BriefingRingCenterX = 267f, BriefingRingCenterY = 221f;
    private static readonly Color BracketTint = RetailColor(0xfe7f7f7f), ReleasedTitleText = RetailColor(0xff7f7f7f);
    // SELECT CONFIGURATION mode headers measure (249,217,62); this renders
    // (247,215,61). It is a different amber from the briefing body.
    private static readonly Color ConfigurationModeText = RetailColor(0xff7c6c1f);
    // The header box is the same FET3_HEADER_TEXT_BOX 0x7f000000 overlay the
    // menu pages use, but these two pages sit over a textured background rather
    // than the flat (23,23,48) fill, so the measured composite constant
    // HeaderBoxTint cannot be reused. Measured inside/outside luminance ratio
    // across the box band is 0.577 (briefing) and 0.478 (configuration) —
    // straddling the 0.5 that alpha 0x7f black predicts.
    private static readonly Color HeaderBoxOverlay = new(0f, 0f, 0f, 0.5f);
    // FE_Rock_Background is drawn through a colour modulate, not at full
    // brightness: a per-channel least-squares fit of retail against the drawn
    // texture over a clean scene band (x150..360, y350..430) gives gains
    // 0.706 / 0.710 / 0.957 with offsets under 3.3, i.e. a pure multiply. This
    // packed value renders 0.702 / 0.702 / 0.953.
    private static readonly Color BriefingBackgroundTint = RetailColor(0xff5a5a7a);
    // The big ring's modulate, fitted where its alpha is fully opaque (22,665
    // pixels): the decoded texel mean is (81,105,136) and retail's mean over
    // exactly those pixels is (101,100,105) on the briefing frame and
    // (103,102,107) on the configuration frame, i.e. per-channel gains of
    // 1.26 / 0.96 / 0.78. The mean of the two frames is used.
    //
    // The RED GAIN IS ABOVE 1, and that is itself a finding rather than a fudge:
    // no value of RetailColor can produce it, because Modulate2X saturates at
    // 1.0. Retail is evidently applying its 2x modulate to the TEXTURE stage as
    // well as to the diffuse colour, which this renderer does not model. The
    // measured gains are therefore stated directly as a Godot modulate (Godot
    // permits components above 1 and clamps at output). Every other bracket
    // draw in this file is a candidate for the same correction; none is changed
    // here because their captures are pinned baselines for this change.
    private static readonly Color BriefingRingTint = new(1.257f, 0.960f, 0.777f, 1f);

    internal static readonly IReadOnlyDictionary<string, Rect2> Sections = new Dictionary<string, Rect2>
    {
        ["Background"] = new(0, 0, 640, 480), ["Header"] = new(191, 65, 394, 32),
        ["Unit"] = new(260.5f, 99.5f, 320, 32), ["Walker"] = new(280, 210, 305, 48),
        ["Jet"] = new(280, 274, 305, 48), ["Navigation"] = new(9, 438, 623, 36),
    };
    private sealed record Frame(RetailFrontendBattleEngineConfiguration SelectedConfiguration);
    private Frame _session = new(new RetailFrontendSession().SelectedConfiguration);
    private Texture2D _rockBackground = null!, _levelBracket02 = null!, _feArrow = null!, _titleFont = null!, _font22 = null!;
    private int[] _glyphWidths = [], _font22Widths = [];
    private Control? _paintingPart;
    private string _drawingSection = string.Empty;
    private bool _initialized;
    internal Texture2D Rock => _rockBackground;
    internal Texture2D Ring => _levelBracket02;
    internal Texture2D Arrow => _feArrow;
    internal Texture2D BodyFont => _titleFont;
    internal Texture2D TitleFont => _font22;
    internal int[] BodyWidths => _glyphWidths.ToArray();
    internal int[] TitleWidths => _font22Widths.ToArray();
    internal float TextWidth(string text, bool title, float scale) => title ? MeasureFont22Text(text, scale) : MeasureText(text, scale);
    internal Vector2 HeaderOrigin => new(HeaderBarCenterX - MeasureFont22Text(SelectConfigurationTitle, 1f) * .5f, HeaderTitleTop);
    internal Rect2 RockRect => new(BriefingBackgroundLeft, BriefingBackgroundTop,
        _rockBackground.GetWidth() * BriefingBackgroundScale, _rockBackground.GetHeight() * BriefingBackgroundScale);
    internal Rect2 RingRect
    {
        get
        {
            float widthScale = BriefingRingSize / _levelBracket02.GetWidth();
            float heightScale = BriefingRingSize / _levelBracket02.GetHeight();
            float width = _levelBracket02.GetWidth() * widthScale;
            float height = _levelBracket02.GetHeight() * heightScale;
            return new(BriefingRingCenterX - width * .5f, BriefingRingCenterY - height * .5f, width, height);
        }
    }
    internal static Color RockTint => BriefingBackgroundTint;
    internal static Color RingTint => BriefingRingTint;
    internal static Color ModeTint => ConfigurationModeText;
    internal static Color TextTint => ReleasedTitleText;
    internal static Color ArrowTint => BracketTint;
    internal static int HitTest(Vector2 point) => new Rect2(0f, 430f, 48f, 48f).HasPoint(point) ? 1
        : new Rect2(595f, 430f, 45f, 48f).HasPoint(point) ? 2 : 0;
    internal static Transform2D SourceTransform(Control section)
    {
        Rect2 source = Sections[section.Name.ToString()];
        Vector2 ratio = section.Size / source.Size;
        var authored = new Transform2D(new Vector2(ratio.X, 0f), new Vector2(0f, ratio.Y), -source.Position * ratio);
        var measured = new Transform2D(0f, Vector2.One, 0f, Vector2.Zero);
        return authored * measured;
    }
    internal void Initialize()
    {
        if (_initialized) return;
        _rockBackground = CuratedAyaTextureLoader.Load("res://Assets/Frontend/Backgrounds/rock.texture.aya", 1024, 512, CuratedAyaTextureLoader.Compression.Dxt1);
        _levelBracket02 = CuratedAyaTextureLoader.Load("res://Assets/Frontend/level-bracket-02.texture.aya", 512, 512, CuratedAyaTextureLoader.Compression.Dxt2);
        _feArrow = CuratedAyaTextureLoader.Load("res://Assets/Frontend/fe-arrow.texture.aya", 64, 64, CuratedAyaTextureLoader.Compression.Dxt2);
        _titleFont = CuratedAyaTextureLoader.Load("res://Assets/Hud/font-13ps.texture.aya", 256, 256, CuratedAyaTextureLoader.Compression.Rgba8);
        _font22 = CuratedAyaTextureLoader.Load("res://Assets/Hud/font-22.texture.aya", 512, 512, CuratedAyaTextureLoader.Compression.Rgba8);
        using Image body = _titleFont.GetImage(); using Image title = _font22.GetImage();
        _glyphWidths = MeasureGlyphWidths(body, GlyphCellSize, GlyphColumns);
        _font22Widths = MeasureGlyphWidths(title, Font22CellSize, Font22Columns);
        foreach (string section in Sections.Keys)
        {
            Control part = GetNode<Control>(section); part.Draw += () => DrawScenePart(part);
        }
        _initialized = true; Refresh();
    }
    internal void SetFrame(RetailFrontendBattleEngineConfiguration configuration) { _session = new(configuration); Refresh(); }
    public override void _Ready() { Initialize(); SetProcess(false); SetProcessInput(false); SetProcessUnhandledInput(false); }
    private void Refresh() { foreach (string section in Sections.Keys) GetNode<Control>(section).QueueRedraw(); }
    private void DrawScenePart(Control part)
    {
        if (!_initialized || part.Size.X <= 0f || part.Size.Y <= 0f) return;
        _paintingPart = part; _drawingSection = string.Empty;
        try { DrawSetTransform(Vector2.Zero, 0f, Vector2.One); DrawSelectConfiguration(); }
        finally { _paintingPart = null; _drawingSection = string.Empty; }
    }
    private void SelectSceneSection(string section) => _drawingSection = section;
    private bool DrawsSceneSection => _paintingPart is not null && "Configuration." + _paintingPart.Name == _drawingSection;
    /// <summary>
    /// Retail SELECT CONFIGURATION — the page between briefing and loading that
    /// this reconstruction did not model at all until this change. Reference:
    /// local-lab/retail-reference-pristine/select-configuration/
    /// 06-select-configuration-640x480.png.
    ///
    ///   title            font22 scale 1, ink x249..526 y73..87; its advance
    ///                    width 280 from origin 249 centres on x=389
    ///   unit name        font22 scale 1, fitted origin (260.5, 99.5),
    ///                    ink x259..536 y107..127, white
    ///   mode headers     Font13PS scale 1 at x=280, ink tops 213 and 277,
    ///                    brightest ink (249,217,62)
    ///   weapon rows      Font13PS scale 1 at x=280, ink tops 229,245,293,309,
    ///                    white; row pitch 16, block gap 32
    ///
    /// KNOWN GAPS, left undrawn because no materialized asset matches them, with
    /// their measured extents so the cost is attributable:
    ///   * the circular unit render at roughly x64..256, y152..344 — it is a
    ///     live 3D view of the battle engine, not a sprite.
    ///
    ///     CORROBORATED 2026-07-26, and it corrects a recorded misreading.
    ///     Differencing the -skipfmv reference against the no-skipfmv control
    ///     (no-skipfmv-frontend/06n-select-configuration-nofmv.png) leaves this
    ///     page 90.28% pixel-identical: the painted landscape backdrop is the
    ///     SAME in both, so this page has no video background. All the
    ///     difference above threshold 64 falls in x68..270 y218..367, which is
    ///     this window, and the two frames show the unit in JET form and in
    ///     WALKER form. The earlier reading of "the two reference frames
    ///     disagree by 9.4% in a clean sky band, so the background is animated"
    ///     came from a sample band that was not clean — it contained this
    ///     render. That is the project's region-mean failure mode again, and
    ///     the countermeasure is the one used here: localise the difference by
    ///     row/column density before interpreting it.
    ///   * the three circular mode icons at x449..541, y183..209;
    ///   * the green/red star rating glyphs at x448..545 on the four weapon
    ///     rows. They are 5-pointed star sprites, not the Font13PS asterisk:
    ///     the drawn stars are 5 rows tall with a solid body, and no atlas in
    ///     the materialized set contains them.
    /// </summary>
    private void DrawSelectConfiguration()
    {
        RetailFrontendBattleEngineConfiguration configuration = _session.SelectedConfiguration;

        SelectSceneSection("Configuration.Background");
        DrawBriefingStage();
        SelectSceneSection("Configuration.Header");
        DrawHeaderBarTitle(SelectConfigurationTitle);

        SelectSceneSection("Configuration.Unit");
        DrawFont22Text(
            configuration.DisplayName,
            new Vector2(ConfigurationUnitLeft, ConfigurationUnitTop),
            1f,
            1f,
            ReleasedTitleText);

        SelectSceneSection("Configuration.Walker");
        DrawConfigurationRows(
            "Walker Mode",
            configuration.WalkerPrimary,
            configuration.WalkerSecondary,
            ConfigurationWalkerTop);
        SelectSceneSection("Configuration.Jet");
        DrawConfigurationRows(
            "Jet Mode",
            configuration.JetPrimary,
            configuration.JetSecondary,
            ConfigurationJetTop);

        SelectSceneSection("Configuration.Navigation");
        DrawPageChevrons();
    }

    private void DrawConfigurationRows(
        string modeName,
        RetailFrontendWeaponConfiguration primary,
        RetailFrontendWeaponConfiguration secondary,
        float top)
    {
        DrawText(
            modeName,
            new Vector2(ConfigurationRowLeft, top),
            1f,
            ConfigurationModeText);
        DrawText(
            primary.DisplayName,
            new Vector2(ConfigurationRowLeft, top + ConfigurationRowPitch),
            1f,
            ReleasedTitleText);
        DrawText(
            secondary.DisplayName,
            new Vector2(ConfigurationRowLeft, top + (2f * ConfigurationRowPitch)),
            1f,
            ReleasedTitleText);
    }

    /// <summary>
    /// The stage both MISSION BRIEFING and SELECT CONFIGURATION compose over:
    /// FE_Rock_Background under FE_select_level_bracket02. Neither page uses the
    /// flat (23,23,48) fill the menu pages do.
    ///
    /// BACKGROUND, measured. The underlay is FE_Rock_Background — the same
    /// texture already materialized for the click-to-start lane — drawn at 1.25
    /// (1280x640) from (-70,-80). Method: a high-pass normalised
    /// cross-correlation of a 140x100 soldier-cluster template from the briefing
    /// frame against the texture over a 1.0-4.5 scale sweep peaks at 0.82 in a
    /// 1.24-1.26 plateau, and an independent per-channel least-squares
    /// background fit over four disjoint scene bands lands on scale 1.25,
    /// origin (-70,-80) as its residual minimum. Sub-pixel origin is not
    /// resolvable from one frame: the fit's offset grid is integral.
    ///
    /// RING, measured. FE_select_level_bracket02 — decoded, it is a full metal
    /// annulus, not an arc — fitted by maximising the fraction of retail's
    /// near-neutral bright pixels (max>85, max-min<22, header/text/chevron bands
    /// excluded) that agree with the texture's alpha>96 mask, scored as
    /// INTERSECTION OVER UNION rather than coverage. Coverage alone has no
    /// penalty for a ring that is too large and it first returned 996x996 @
    /// (270,208), which put the drawn ring's inner edge 11px right of retail's
    /// at y=240. Under IoU the peak is 0.760 at 990x990 centred (267,221) on
    /// the briefing frame and 0.773 at the SAME size and centre on the
    /// configuration frame — two independent frames agreeing to the sweep step
    /// is what makes this a measurement rather than a fit artifact.
    ///
    /// The arc-scale dispute recorded in STARTUP-FLOW-FINDINGS does NOT extend
    /// to these pages: they do not draw FE_select_level_bracket01 at all, so
    /// neither 1.25 nor 1.4 is in play here.
    ///
    /// KNOWN GAPS, left undrawn rather than approximated:
    ///   * the background is ANIMATED. The two reference frames disagree by
    ///     9.4% material pixels in a clean sky band and the configuration
    ///     frame's own background best-fit lands at scale 1.275, origin
    ///     (-110,-86) rather than the briefing's 1.25/(-70,-80). This draw is
    ///     static and pinned to the briefing frame, so the configuration page
    ///     carries the full pan error as measured cost.
    ///   * the blue Forseti emblem at top-left, unidentified here as it is on
    ///     every other page.
    /// </summary>
    private void DrawBriefingStage()
    {
        DrawTextureRect(
            _rockBackground,
            new Rect2(
                BriefingBackgroundLeft,
                BriefingBackgroundTop,
                _rockBackground.GetWidth() * BriefingBackgroundScale,
                _rockBackground.GetHeight() * BriefingBackgroundScale),
            false,
            BriefingBackgroundTint);

        DrawSurfaceCentered(
            _levelBracket02,
            BriefingRingCenterX,
            BriefingRingCenterY,
            BriefingRingSize / _levelBracket02.GetWidth(),
            BriefingRingSize / _levelBracket02.GetHeight(),
            BriefingRingTint);
    }

    /// <summary>
    /// Bottom page chevrons. Measured extents on both pages are the ones
    /// FEP_LEVEL_SELECT already carries: left x9..36 y438..473, right
    /// x604..631 y437..472, and the configuration frame's right-chevron pixels
    /// are identical to the level-select frame's.
    /// </summary>
    private void DrawPageChevrons()
    {
        var arrowSource = new Rect2(16f, 12f, 30f, 40f);
        DrawTextureRectRegion(_feArrow, new Rect2(9f, 438f, -28f, 36f), arrowSource, BracketTint);
        DrawTextureRectRegion(_feArrow, new Rect2(604f, 437f, 28f, 36f), arrowSource, BracketTint);
    }

    /// <summary>Header title: font22 at scale 1, centred on HEADER_BAR_X.</summary>
    private void DrawHeaderBarTitle(string title)
    {
        DrawRect(new Rect2(191f, 69f, 394f, 21f), HeaderBoxOverlay);
        float width = MeasureFont22Text(title, 1f);
        DrawFont22Text(
            title,
            new Vector2(HeaderBarCenterX - (width * 0.5f), HeaderTitleTop),
            1f,
            1f,
            ReleasedTitleText);
    }

    private void DrawSurfaceCentered(
        Texture2D texture,
        float centerX,
        float centerY,
        float widthScale,
        float heightScale,
        Color modulate)
    {
        float width = texture.GetWidth() * widthScale;
        float height = texture.GetHeight() * heightScale;
        DrawTextureRect(
            texture,
            new Rect2(centerX - (width * 0.5f), centerY - (height * 0.5f), width, height),
            false,
            modulate);
    }

    private void DrawText(string text, Vector2 position, float scale, Color color) =>
        DrawTextCore(text, position, scale, color, dropShadow: true);

    private void DrawTextCore(string text, Vector2 position, float scale, Color color, bool dropShadow) =>
        DrawAtlasText(
            _titleFont,
            _glyphWidths,
            GlyphCellSize,
            GlyphColumns,
            text,
            position,
            scale,
            scale,
            color,
            dropShadow);

    /// <summary>
    /// Atlas-agnostic glyph run. Font13PS and font22 share the ASCII-32 origin
    /// and the 16-column grid and differ only in cell size, so one routine draws
    /// both. Separate X and Y scales exist because the briefing level name is
    /// measurably non-uniform (see <see cref="BriefingLevelNameScaleX"/>).
    /// </summary>
    private void DrawAtlasText(
        Texture2D atlas,
        int[] widths,
        int cellSize,
        int columns,
        string text,
        Vector2 position,
        float scaleX,
        float scaleY,
        Color color,
        bool dropShadow)
    {
        float x = position.X;
        foreach (char character in text)
        {
            int glyph = GlyphIndex(character);
            float glyphWidth = widths[glyph] * scaleX;
            var source = new Rect2(
                (glyph % columns) * cellSize,
                (glyph / columns) * cellSize,
                widths[glyph],
                cellSize);
            var destination = new Rect2(x, position.Y, glyphWidth, cellSize * scaleY);
            if (dropShadow)
            {
                // THE SHADOW SITS ON THE ANCHOR AND THE BODY IS DRAWN AT (-1,-1).
                // MEASURED from retail's own draw calls, 2026-07-27 d3d9 sweep
                // (local-lab/D3D9-FULL-SWEEP-2026-07-27.md; per-draw CSVs under
                // G:\bea-frontend-pages\SWEEP-2026-07-27\inventories\). Every
                // shadowed text run in the frontend is a shadow DrawPrimitive
                // followed immediately by a body DrawPrimitive whose rectangle is
                // the shadow's minus (1,1). Six pages, two font atlases, no
                // exception:
                //
                //   main-menu-settled.csv f3000 d12/d13   (175.5,296.5) / (174.5,295.5)
                //   main-menu-settled.csv f3000 d32/d33   (  0.5,464.5) / ( -0.5,463.5)
                //   options-root.csv      f2500 d11/d12   (243.5,245.5) / (242.5,244.5)
                //   options-sound.csv     f4900 d43/d44   ( 44.5,255.5) / ( 43.5,254.5)
                //   mission-briefing.csv  f3600 d18/d19   ( 80.5,164.5) / ( 79.5,163.5)
                //   select-level.csv      f2500 d71/d72   (130.5,153.5) / (129.5,152.5)
                //
                // AND THE SHADOW CARRIES THE BODY'S OWN ALPHA, not a fraction of
                // it. The packed diffuse pairs are 0xFD000000/0xFD4F4F4F and
                // 0x7D000000/0x7D1F1F1F (main menu), 0xFF000000/0xFFD6D6D6
                // (options), 0xFE000000/0xFEFFDF5F (briefing),
                // 0xFF000000/0xFF7F7F7F (select level). The alpha byte is equal on
                // every one of the 63 pairs in those five inventories; the RGB of
                // the shadow is always exactly 0x000000. The previous
                // `color.A * 0.82f` is refuted by all 63.
                //
                // WHY THIS IS AN EXACT MATCH AND NOT A HALF-PIXEL APPROXIMATION.
                // Retail's rectangles are half-integer because D3D9 samples a
                // pixel at its centre, which sits at k + 0.5 in XYZRHW space: a
                // quad spanning [k+0.5, k+0.5+n) covers pixel rows k..k+n-1, which
                // is exactly what a Godot Rect2 at integer k with height n covers.
                // Our anchors were therefore already on retail's SHADOW row; only
                // the assignment of the two quads to it was inverted. On the seven
                // main-menu rows this change takes our body from +1,+1 and our
                // shadow from +2,+2 to a zero-pixel offset on both.
                DrawTextureRectRegion(
                    atlas,
                    destination,
                    source,
                    new Color(0f, 0f, 0f, color.A));
                DrawTextureRectRegion(
                    atlas,
                    new Rect2(destination.Position - Vector2.One, destination.Size),
                    source,
                    color);
            }
            else
            {
                DrawTextureRectRegion(atlas, destination, source, color);
            }
            x += glyphWidth + scaleX;
        }
    }

    private void DrawFont22Text(string text, Vector2 position, float scaleX, float scaleY, Color color) =>
        DrawAtlasText(
            _font22,
            _font22Widths,
            Font22CellSize,
            Font22Columns,
            text,
            position,
            scaleX,
            scaleY,
            color,
            dropShadow: true);

    private float MeasureFont22Text(string text, float scaleX)
    {
        float width = 0f;
        foreach (char character in text)
        {
            width += (_font22Widths[GlyphIndex(character)] + 1) * scaleX;
        }
        return Mathf.Max(0f, width - scaleX);
    }

    private float MeasureText(string text, float scale)
    {
        float width = 0f;
        foreach (char character in text)
        {
            width += (_glyphWidths[GlyphIndex(character)] + 1) * scale;
        }
        return Mathf.Max(0f, width - scale);
    }

    private static int GlyphIndex(char character)
    {
        int code = character;
        if (code is < FirstGlyph or >= FirstGlyph + GlyphSlotCount)
        {
            code = '?';
        }

        return code - FirstGlyph;
    }

    private static int[] MeasureGlyphWidths(Image image, int cellSize, int columns)
    {
        var widths = new int[GlyphSlotCount];
        widths[0] = cellSize / 2;
        int scanMax = cellSize - 2;
        for (int glyph = 1; glyph < widths.Length; glyph++)
        {
            int cellX = (glyph % columns) * cellSize;
            int cellY = (glyph / columns) * cellSize;
            if (cellY + cellSize > image.GetHeight())
            {
                break;
            }
            int rightmost = cellX;
            for (int x = cellX + scanMax; x >= cellX; x--)
            {
                bool occupied = false;
                for (int y = cellY; y < cellY + cellSize - 1; y++)
                {
                    if (image.GetPixel(x, y).A > (16f / 255f))
                    {
                        occupied = true;
                        break;
                    }
                }
                if (occupied)
                {
                    rightmost = x;
                    break;
                }
            }
            widths[glyph] = (rightmost - cellX) + 2;
        }
        return widths;
    }

    /// <summary>
    /// Converts a packed released ARGB constant to a Godot colour.
    ///
    /// The released frontend composes its text and chrome through a 2x colour
    /// modulate, so a packed RGB channel reaches the framebuffer at
    /// <c>min(255, (c * 255) &gt;&gt; 7)</c> — very nearly double. Reproducing the packed
    /// value literally renders every frontend colour at roughly half intensity,
    /// which is why the reconstruction's menu read as dark grey-on-blue while
    /// retail reads as light grey and bright amber.
    ///
    /// Measured against <c>captures/08-main-retail.png</c> (640x480 retail frame),
    /// brightest glyph texel per row:
    ///   0x4f (normal)   -> predicted 157, measured 157
    ///   0x6f (selected) -> predicted 221, measured 220
    ///   0x3f (selected) -> predicted 125, measured 125
    /// Alpha is NOT modulated: 0x7f disabled text blends at ~0.5 as packed.
    /// </summary>
    private static Color RetailColor(uint argb) => new(
        Modulate2X((argb >> 16) & 0xff),
        Modulate2X((argb >> 8) & 0xff),
        Modulate2X(argb & 0xff),
        ((argb >> 24) & 0xff) / 255f);

    private static float Modulate2X(uint channel) =>
        Math.Min(255u, (channel * 255u) >> 7) / 255f;

    private new void DrawSetTransform(Vector2 position, float rotation = 0f, Vector2? scale = null)
    {
        if (_paintingPart is null) return;
        Vector2 ratio = _paintingPart.Size / Sections[_paintingPart.Name.ToString()].Size;
        var authored = new Transform2D(new Vector2(ratio.X, 0f), new Vector2(0f, ratio.Y),
            -Sections[_paintingPart.Name.ToString()].Position * ratio);
        var measured = new Transform2D(rotation, scale ?? Vector2.One, 0f, position);
        _paintingPart.DrawSetTransformMatrix(authored * measured);
    }
    private new void DrawRect(Rect2 rect, Color color, bool filled = true, float width = -1f, bool antialiased = false)
    {
        if (DrawsSceneSection) _paintingPart!.DrawRect(rect, color, filled, width, antialiased);
    }
    private new void DrawTextureRect(Texture2D texture, Rect2 rect, bool tile, Color? modulate = null, bool transpose = false)
    {
        if (DrawsSceneSection) _paintingPart!.DrawTextureRect(texture, rect, tile, modulate, transpose);
    }
    private new void DrawTextureRectRegion(Texture2D texture, Rect2 rect, Rect2 source, Color? modulate = null,
        bool transpose = false, bool clipUv = true)
    {
        if (DrawsSceneSection) _paintingPart!.DrawTextureRectRegion(texture, rect, source, modulate, transpose, clipUv);
    }
}
