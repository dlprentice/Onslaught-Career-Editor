// SPDX-License-Identifier: GPL-3.0-or-later
using System.Text.Json;
using Godot;
using OnslaughtRebuild.Client;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Test-only retained Level Select renderer from 51477f62. Original draw and
/// numerical helper bodies retain operation order. Geometry calls are observed
/// at the actual Canvas API seam, not transcribed as new expected coordinates.
/// The original single CareerGraph source frame remains the comparison frame.
/// The measured graph stays static at node 0 even when selected-world text differs.
/// Missing art, unresolved arc blending and prior retail title offset stay gaps.
/// The old title-scale commentary is historical; the retained executable body
/// already uses the later Font22 scale 1 correction unchanged.
/// </summary>
public sealed partial class LevelSelectReference : Control
{
    private const float DesignWidth = 640f, DesignHeight = 480f;
    private const int GlyphColumns = 16, GlyphCellSize = 16, FirstGlyph = 32, GlyphSlotCount = 256;
    private const int Font22Columns = 16, Font22CellSize = 32;
    private const float HeaderBarCenterX = 390f, HeaderTitleTop = 65f, ShadowScaleBoost = 1.05f;
    // Main-menu row tints. The RGB triples were already exact; the ALPHA BYTE was
    // 2/255 high on all three and is corrected here from retail's own diffuse
    // values, 2026-07-27 d3d9 sweep,
    // G:\bea-frontend-pages\SWEEP-2026-07-27\inventories\main-menu-settled.csv
    // frame 3000: the six live rows and their shadows carry 0xFD (draws 12-25,
    // e.g. d17 0xFD4F4F4F, d13 0xFDFF6F3F) and the single disabled row carries
    // 0x7D (d14/d15, 0x7D000000 / 0x7D1F1F1F). Counted over that frame: 0xFD x36,
    // 0x7D x6, and no 0xFF or 0x7F anywhere in the row block.
    //
    // 0xFD IS NOT A GLOBAL FRONTEND CONSTANT and is deliberately not applied as
    // one: the same sweep measures 0xFF on the version string and on every
    // options row, and 0xFE on the mission-briefing body. Only the FEP_MAIN rows
    // are 0xFD.
    private static readonly Color ReleasedSelected = RetailColor(0xfdff6f3f);
    private static readonly Color ReleasedBlue = RetailColor(0xff1f4f7f);
    // 0xfe7f7f7f, CORRECTED 2026-07-28 from 0xfeffffff. The RGB byte was never
    // measured; it was the neutral guess, and 0xff is the one value MODULATE2X
    // cannot round-trip — (0xff*255)>>7 saturates at 255, so any authored byte
    // above 0x80 renders identically and the constant carried no information.
    // main-menu-settled.csv frame 3000 gives the exact byte on all three decor
    // bodies this tints: draw 27 (left arc, 320x320), draw 29 (right arc,
    // 160x160) and draw 31 (selected-row icon, 128x128) are each 0xFE7F7F7F.
    // A census of the settled frame of every other page in the same sweep
    // (select-level, options-root, options-video, mission-briefing,
    // choose-game-name, select-configuration) finds this class of draw at
    // 0xFE7F7F7F or 0xFF7F7F7F and NEVER at 0xFFFFFFFF, so the correction is
    // toward retail on the pages that share the constant too. The rendered
    // delta is 1/255 per channel; the point is that the byte is now measured.
    private static readonly Color BracketTint = RetailColor(0xfe7f7f7f);
    private static readonly Color ShadowTint = RetailColor(0x3e000000);

    // FEP_LEVEL_SELECT ("SELECT LEVEL"). Every literal below is measured from the
    // pristine 640x480 capture; see DrawLevelSelect for the method and the gaps.
    // FrontEndText token — english.json "selectLevel" already carries the exact
    // released string, so the title is drawn from localization (_selectLevelText).
    // "Episode 1" has no resolved string id in the materialized table; it is
    // transcribed from the pristine capture and is the one literal on this page
    // that is not localization-backed.
    private const string LevelSelectEpisodeText = "Episode 1";
    private const float LevelSelectBodyScale = 1.4f;
    private const float LevelSelectEpisodeLeft = 130f;
    private const float LevelSelectEpisodeTop = 130.2f;
    private const float LevelSelectLevelNameTop = 156.8f;
    private const float LevelSelectColumnLabelScale = 1.5f;
    private const float LevelSelectColumnLabelTop = 182.5f;
    // Node graph. Column pitch 60, three rows, all measured (DrawLevelSelect).
    private const float NodeColumnPitch = 60f;
    private const float NodeRowMiddleY = 320f;
    private const float NodeRowTopY = 290f;
    private const float NodeRowBottomY = 350f;
    private const float NodeRingSize = 61f;
    private const float NodeOuterRadius = 21f;
    private const float CurrentNodeRingSize = 80f;
    private const float CurrentNodeInnerRingSize = 62f;
    private const float CurrentNodeOuterRadius = 27f;
    private const float NodeLinkWidth = 1.6f;
    // Episode sweep arcs: circle fitted to 14 measured centre points, residuals
    // under 1.1px (see DrawLevelSelect).
    private const float SweepArcCenterX = 365.84f;
    private const float SweepArcCenterY = 320.38f;
    private const float SweepArcRadius = 249.28f;
    private const float SweepArcStartAngle = 2.5423f;
    private const float SweepArcEndAngle = 3.7253f;
    private const float SweepArcWidth = 1.6f;

    /// <summary>Node centres, in draw order. Index 0 is the current node.</summary>
    private static readonly Vector2[] LevelNodes =
    [
        new(148f, NodeRowMiddleY),
        new(208f, NodeRowMiddleY),
        new(268f, NodeRowMiddleY),
        new(328f, NodeRowTopY),
        new(328f, NodeRowBottomY),
        new(388f, NodeRowTopY),
        new(388f, NodeRowBottomY),
        new(448f, NodeRowTopY),
        new(448f, NodeRowBottomY),
        new(508f, NodeRowMiddleY),
        new(568f, NodeRowTopY),
        new(568f, NodeRowBottomY),
    ];

    /// <summary>Index pairs into <see cref="LevelNodes"/>.</summary>
    private static readonly (int From, int To)[] LevelNodeLinks =
    [
        (0, 1), (1, 2),
        (2, 3), (2, 4),
        (3, 5), (4, 6), (3, 6), (4, 5),
        (5, 7), (6, 8), (5, 8), (6, 7),
        (7, 9), (8, 9),
        (9, 10), (9, 11),
    ];

    /// <summary>Column label text and its measured left edge.</summary>
    private static readonly (string Text, float X)[] LevelColumnLabels =
    [
        ("1", 163f), ("2", 283f), ("3", 524f),
    ];

    /// <summary>Sweep-arc circle-centre X for each drawn arc.</summary>
    private static readonly float[] SweepArcCenters =
    [
        SweepArcCenterX, SweepArcCenterX + 120f, SweepArcCenterX + 360f,
    ];

    private static readonly Color DevSelectGuide = new(50f / 255f, 51f / 255f, 72f / 255f, 1f);
    // Node-graph link lines and the episode sweep arcs are measured framebuffer
    // colours at the line core, stated literally for the same reason the panel
    // fills are: they are not modulated sprite tints this lane can reproduce.
    //
    // The three sweep arcs are NOT drawn at one brightness. Sampling each arc's
    // predicted core every 20 rows from y=200 to y=460 gives a peak of 141±13 for
    // the leftmost arc and 61±4 for the other two — the current episode's divider
    // is drawn bright and the rest dim, at almost exactly one third the delta
    // over the page background.
    private static readonly Color LevelLinkLine = new(49f / 255f, 50f / 255f, 71f / 255f, 1f);
    private static readonly Color LevelSweepArcCurrent = new(142f / 255f, 142f / 255f, 167f / 255f, 1f);
    private static readonly Color LevelSweepArcOther = new(61f / 255f, 61f / 255f, 86f / 255f, 1f);
    // Unvisited node rings are FE_select_level_ring_bracket01 drawn very dim: the
    // ring peak measures (33,35,62) over the (23,23,48) page background, and the
    // texture's brightest opaque texel is (123,146,189), which is alpha 0.102 -
    // 0x1a. The blue channel is what identifies the texture: the measured ring
    // delta is (10,12,14), whose 1.4 blue/red ratio matches ring_bracket01's 1.49
    // and not ring_bracket02's 1.00.
    private static readonly Color LevelNodeRingTint = RetailColor(0x1cffffff);
    // FrontEnd.cpp:1127 sets col = 0x7f000000; line 1134 draws
    // FET3_HEADER_TEXT_BOX, and the
    // measured header interior is (12,12,24) — exactly that alpha over the
    // (23,23,48) page background. Drawn as the measured composite because an
    // alpha 0x7f fill lands on (11,11,24) after this renderer's blend rounding.
    private static readonly Color HeaderBoxTint = new(12f / 255f, 12f / 255f, 24f / 255f, 1f);
    private static readonly Color ReleasedTitleText = RetailColor(0xff7f7f7f);
    // Materialized decode of data/video/FEBack128.vid (128² BIKi → rgb24) at the
    // SHIPPED 30 fps × 572 frames. The old 15 fps / 286-frame strip dropped every
    // second frame; that was harmless while nothing drew it and is not harmless
    // now, because a half-rate strip is at the wrong phase at every instant.
    private const string FeBackStripPath =
        "res://Assets/Frontend/Backgrounds/fe-back-128x128x30.rgb";
    private const int FeBackWidth = 128;
    private const int FeBackHeight = 128;
    private const int FeBackFps = 30;
    private const int FeBackFrameBytes = FeBackWidth * FeBackHeight * 3;
    // Additive gain of the FEBack128 underlay over the flat page fill, MEASURED
    // per channel by least squares against retail captured WITHOUT -skipfmv.
    //
    // Reference: local-lab/retail-reference-pristine/nofmv-frontend-2026-07-26/run1,
    // main-menu frames mm-t001020ms .. mm-t007027ms (13 settled frames), scored on
    // the 222,683 pixels the -skipfmv main-menu capture proves are pure underlay
    // (exactly (23,23,48) within 1 — a geometric mask, not a rectangle).
    //
    // Per-frame fits are stable: R 0.2523..0.2687, G 0.2456..0.2674,
    // B 0.2290..0.2467. The competing alpha-mix model (y = (1-a)·bg + a·frame)
    // fits these pixels WORSE: residual rms 4.6..11.9 against additive's 2.4..5.7.
    //
    // Its fitted `a` also wanders 0.29..0.57 across frames where the additive gain
    // does not move. That is recorded but is NOT independent evidence, and an
    // earlier draft of this comment claimed it was. An independent adversarial
    // pass pointed out the circularity: if the truth is y = bg + g·F then forcing
    // an alpha mix gives a = g·F/(F - bg), which MUST vary with frame content.
    // The residual rms
    // is what carries this conclusion.
    //
    // What is established is narrower than "the compositor is additive": it is
    // that over a flat destination these pixels are described by bg + g·frame.
    // A D3D SRCALPHA/ONE draw of a modulated frame reduces to exactly that form,
    // and this measurement cannot separate the two.
    //
    // 0.2471 = (0x7e/255) × 0.5 — the frontend's own 0x7e7e7e modulate at alpha
    // 0.5 under D3D SRCALPHA/ONE — lands inside the measured band on all three
    // channels. That is a plausible generator and is NOT asserted here: the
    // constants below are the measurements, not the theory.
    private static readonly float[] FeBackUnderlayGain = [0.2610f, 0.2590f, 0.2420f];

    /// <summary>See <see cref="FeBackFrameIndex"/> - measured, over a full loop.</summary>
    private const int FeBackPhaseFrames = 3;
    // ---- THE PAGE FILL IS A TWO-STEP COMPOSITE, NOT A COLOUR ----
    //
    // MEASURED 2026-07-27 (local-lab/D3D9-FULL-SWEEP-2026-07-27.md section 5.3;
    // G:\bea-frontend-pages\SWEEP-2026-07-27\page-index.csv and
    // inventories\main-menu-settled.csv frame 3000 draw 0):
    //
    //   1. Clear(0x001F1F3F) = RGB(31,31,63). page-index.csv records this Clear
    //      colour on EVERY frontend page from frame ~46 onward; only the boot
    //      first page and the loading page clear to 0x00000000.
    //   2. Draw 0 of the page is a full-screen DrawPrimitiveUP TRIFAN spanning
    //      (-40,-3)-(680,483) from a 128x128 DXT2, diffuse 0x3E000000, blend
    //      SRCALPHA/INVSRCALPHA. Its stage-0 COLOROP is MODULATE(TEXTURE,
    //      DIFFUSE) with a BLACK diffuse RGB, so it contributes no colour at all
    //      whatever its texture holds, and it is the only draw on the page whose
    //      stage-0 ALPHAOP is DISABLE, so its alpha is the diffuse alpha
    //      0x3E/255 = 0.24314 flat.
    //
    // The arithmetic closes exactly: 31 x (1 - 0.24314) = 23.46 -> 23 and
    // 63 x 0.75686 = 47.68 -> 48, and the retail pixel at f000800.png(5,470)
    // reads exactly (23,23,48).
    //
    // We used to draw the (23,23,48) ANSWER as one opaque rect. That is right
    // today and wrong in principle: it bakes a result whose two inputs are
    // separately measured, so it silently stops tracking if either moves — and
    // one of them (the FEBack128 underlay this page composites next) is known to
    // be absent under -skipfmv, which is the only condition the fill has ever
    // been measured under.
    private static readonly Color FrontendClearColor = new(31f / 255f, 31f / 255f, 63f / 255f, 1f);
    private static readonly Color FrontendFillDarkener = new(0f, 0f, 0f, 0x3Eu / 255f);

    // The composed result of the two terms above. It is NOT drawn; it is the
    // base the FEBack128 strip is baked against (see BuildFeBackFrames), where a
    // single already-composited colour is what the algebra needs.
    private static readonly Color MainUnderlayFallback = new(23f / 255f, 23f / 255f, 48f / 255f, 1f);


    private sealed record Selection(string SelectedLevelName);
    internal sealed record Frame(string Title, string LevelName, double BackgroundSeconds);
    internal sealed record ArcCall(Vector2 Center, float Radius, float Start, float End, int Points, Color Ink, float Width, bool Antialiased);
    internal sealed record LineCall(Vector2 Start, Vector2 End, Color Ink, float Width, bool Antialiased);
    internal sealed record TextureCall(Texture2D Texture, Rect2 Rectangle, Color Ink);
    internal static readonly Rect2 SourceRect = new(0, 0, 640, 480);
    private Selection _session = new("1.00 - Training Level");
    private string _selectLevelText = "", _level100Text = "", _loadingText = "";
    private readonly Dictionary<RetailFrontendMenuItemKind, string> _menuText = [];
    private Texture2D _levelBracket01 = null!, _levelRing01 = null!, _levelRing02 = null!, _feArrow = null!, _titleFont = null!, _font22 = null!;
    private Texture2D[] _feBackFrames = [];
    private int[] _glyphWidths = [], _font22Widths = [];
    private double _feBackSeconds;
    private Control? _paintingPart;
    private string _drawingSection = string.Empty;
    private bool _initialized, _captureGeometry;
    private readonly List<ArcCall> _arcs = [];
    private readonly List<LineCall> _lines = [];
    private readonly List<TextureCall> _rings = [];
    internal IReadOnlyList<ArcCall> Arcs => _arcs.AsReadOnly();
    internal IReadOnlyList<LineCall> Lines => _lines.AsReadOnly();
    internal IReadOnlyList<TextureCall> Rings => _rings.AsReadOnly();
    internal string LocalizedTitle => _selectLevelText;
    internal Texture2D BodyFont => _titleFont;
    internal Texture2D TitleFont => _font22;
    internal Texture2D Bracket => _levelBracket01;
    internal Texture2D Ring01 => _levelRing01;
    internal Texture2D Ring02 => _levelRing02;
    internal Texture2D Arrow => _feArrow;
    internal int[] BodyWidths => _glyphWidths.ToArray();
    internal int[] TitleWidths => _font22Widths.ToArray();
    internal Texture2D[] BackgroundFrames => _feBackFrames.ToArray();
    internal Vector2 TitleOrigin => new(HeaderBarCenterX - MeasureFont22Text(_selectLevelText, 1f) * .5f, HeaderTitleTop);
    internal float TextWidth(string text, bool title, float scale) => title ? MeasureFont22Text(text, scale) : MeasureText(text, scale);
    internal static Color SelectedTint => ReleasedSelected;
    internal static Color BlueTint => ReleasedBlue;
    internal static Color TitleTint => ReleasedTitleText;
    internal static Color ArrowTint => BracketTint;
    internal static int HitTest(Vector2 point) => new Rect2(0, 430, 48, 48).HasPoint(point) ? 1
        : new Rect2(595, 430, 45, 48).HasPoint(point) ? 2
        : new Rect2(120, 265, 60, 60).HasPoint(point) ? 3
        : new Rect2(180, 265, 60, 60).HasPoint(point) ? 4 : 0;
    internal static Transform2D SourceTransform(Control section)
    {
        Vector2 ratio = section.Size / SourceRect.Size;
        var authored = new Transform2D(new Vector2(ratio.X, 0f), new Vector2(0f, ratio.Y), -SourceRect.Position * ratio);
        var measured = new Transform2D(0f, Vector2.One, 0f, Vector2.Zero);
        return authored * measured;
    }
    internal void Initialize()
    {
        if (_initialized) return;
        LoadLocalization();
        _levelBracket01 = LegacyCuratedAyaTextureReference.Load("res://Assets/Frontend/level-bracket-01.texture.aya", 512, 512, LegacyCuratedAyaTextureReference.Compression.Dxt2);
        _levelRing01 = LegacyCuratedAyaTextureReference.Load("res://Assets/Frontend/level-ring-01.texture.aya", 64, 64, LegacyCuratedAyaTextureReference.Compression.Dxt2);
        _levelRing02 = LegacyCuratedAyaTextureReference.Load("res://Assets/Frontend/level-ring-02.texture.aya", 64, 64, LegacyCuratedAyaTextureReference.Compression.Dxt2);
        _feArrow = LegacyCuratedAyaTextureReference.Load("res://Assets/Frontend/fe-arrow.texture.aya", 64, 64, LegacyCuratedAyaTextureReference.Compression.Dxt2);
        _titleFont = LegacyCuratedAyaTextureReference.Load("res://Assets/Hud/font-13ps.texture.aya", 256, 256, LegacyCuratedAyaTextureReference.Compression.Rgba8);
        _font22 = LegacyCuratedAyaTextureReference.Load("res://Assets/Hud/font-22.texture.aya", 512, 512, LegacyCuratedAyaTextureReference.Compression.Rgba8);
        using Image body = _titleFont.GetImage(); using Image title = _font22.GetImage();
        _glyphWidths = MeasureGlyphWidths(body, GlyphCellSize, GlyphColumns);
        _font22Widths = MeasureGlyphWidths(title, Font22CellSize, Font22Columns);
        _feBackFrames = LoadFeBackFrames();
        GetNode<Control>("CareerGraph").Draw += DrawScenePart;
        _initialized = true; GetNode<Control>("CareerGraph").QueueRedraw();
        _captureGeometry = true;
        try { DrawLevelSweepArcs(); DrawLevelNodeGraph(); }
        finally { _captureGeometry = false; }
    }
    internal void SetFrame(Frame frame)
    {
        _session = new(frame.LevelName); _selectLevelText = frame.Title; _feBackSeconds = frame.BackgroundSeconds;
        GetNode<Control>("CareerGraph").QueueRedraw();
    }
    public override void _Ready() { Initialize(); SetProcess(false); SetProcessInput(false); SetProcessUnhandledInput(false); }
    private void DrawScenePart()
    {
        Control part = GetNode<Control>("CareerGraph");
        if (!_initialized || part.Size.X <= 0f || part.Size.Y <= 0f) return;
        _paintingPart = part; _drawingSection = string.Empty;
        try { DrawSetTransform(Vector2.Zero, 0f, Vector2.One); DrawLevelSelect(); }
        finally { _paintingPart = null; _drawingSection = string.Empty; }
    }
    private void SelectSceneSection(string section) => _drawingSection = section;
    private bool DrawsSceneSection => _paintingPart is not null && _drawingSection == "LevelSelect.Content";
    private static void RequireOptionsResult(Godot.Collections.Dictionary result)
    {
        if (!result["ok"].AsBool()) throw new InvalidDataException(result["error"].AsString());
    }
    /// <summary>
    /// Retail FEP_LEVEL_SELECT — the "SELECT LEVEL" episode/level graph reached
    /// from the CHOOSE GAME NAME page.
    ///
    /// The released source in references/Onslaught/ declares CFEPLevelSelect but
    /// does not ship its implementation (there is no FEPLevelSelect.cpp), so the
    /// page body carries NO source geometry at all. Everything below is measured
    /// from the pristine 640x480 capture
    /// local-lab/retail-reference-pristine/select-level/04-select-level-640x480.png
    /// by scanning for pixels that differ from the page background.
    ///
    ///   page background      flat (23,23,48)  — same fill proven for the main menu
    ///                        (228,102 of 307,200 pixels are exactly that value)
    ///   header text box      interior (12,12,24), x191..584, y69..89 — byte-identical
    ///                        extents and colour to the FEP_DEVSELECT header
    ///   title "SELECT LEVEL" ink x304..471, y73..87; 'S' has atlas bearing (0,3), so
    ///                        origin (304, 68.5) at scale 1.5, i.e. centred on x=390
    ///                        exactly as HEADER_BAR_X (FrontEnd.cpp:1103) requires
    ///   "Episode 1"          white (254,254,254), ink x130..237 y133..148, scale 1.4
    ///   "1.00 - Training..." (254,222,126), ink x130..374 y161..176, scale 1.4
    ///   column labels 1/2/3  (62,157,253) = ReleasedBlue exactly, left edges
    ///                        x=163 / 283 / 524, ink top y=187, scale 1.5
    ///   faint guides         (50,51,72) at x=123 and y=180 — same crosshair as
    ///                        FEP_DEVSELECT and the main menu
    ///   node ring outer      diameter 41 (vertical profile y300..340 at x=208)
    ///   node columns         x = 148 + 60k, k = 0..7; rows y = 290 / 320 / 350
    ///   current node ring    blue band r20..26 at (148,320), peak (123,146,189)
    ///   link lines           core (49,50,71), one pixel wide with ±1 antialiasing
    ///   arc brackets         see below
    ///   chevrons             left x9..36 y438..473, right x604..631 y437..472
    ///
    /// Scale evidence, since two different text scales are in play: summing the
    /// measured per-glyph advances gives 158px from the title's first 'S' to its
    /// last 'L' against 160.5 predicted at 1.5 and 149.8 at 1.4, while the level
    /// name gives 243px against 261.5 at 1.5 and 244.1 at 1.4. Title 1.5, body 1.4
    /// — the same split FEP_DEVSELECT uses.
    ///
    /// KNOWN GAPS, left undrawn rather than approximated, with their measured cost:
    ///   * the blue Forseti emblem at top-left (~x48..160, y20..190) has no
    ///     materialized texture;
    ///   * the metal header end-cap brackets (retail x176..205 and x568..600) are
    ///     the same unidentified FET3_HEADER_BRACKET art FEP_DEVSELECT lacks;
    ///   * the mottled amber "current level" disc inside the highlighted node
    ///     (x138..158, y310..332) is a textured sprite, not a flat fill — its
    ///     texels run (205,161,105) to (253,243,164) — and no materialized asset
    ///     matches it, so the node is drawn as rings with an empty centre;
    ///   * the faint Forseti writing outlines around x55..135, y0..170. Fitting
    ///     FE_Forseti_Writing_large over that band scores only 0.12 correlation at
    ///     its best scale/offset, so this lane cannot claim it is that texture.
    /// </summary>
    private void DrawLevelSelect()
    {
        SelectSceneSection("LevelSelect.Content");
        // Settled; the DevSelect measurement is retained in Tests/CareerNameReference.cs.
        DrawMainUnderlay(1f);

        DrawRect(new Rect2(123f, 0f, 1f, DesignHeight), DevSelectGuide);
        DrawRect(new Rect2(0f, 180f, DesignWidth, 1f), DevSelectGuide);

        DrawLevelSweepArcs();
        // RetailLevelSelectFsub148: CFEPLevelSelect::Render leftover
        // after the sliding-borders call is fld [0x005DB53C] (148.0)
        // fsub [esi+0x3460] fstp [esp+0x14]. Official 74154bfa
        // independently re-read this cycle. The local is a window,
        // not dest. 0x00460BE4 fcomp 610.0 / 0x00460BF9 fcomp 0.0.
        // Init fstp [esi+0x3460] at 0x00460464 follows fild of the
        // zeroed [esi+0x3468]. Settled pad is 148.0 - 0. Dest stays
        // the measured node centres. Do not invent dest from 148.0.
        if (RetailLevelSelectFsub148.Applies(
                RetailLevelSelectFsub148.Pad(
                    RetailLevelSelectFsub148.SettledField)))
        {
            // RetailLevelSelectFsub10: later leftover is
            // fld [esp+0x14] / fsub [0x005D85CC] (10.0) /
            // fstp [esp] before call 0x005563D0. Official
            // 74154bfa independently re-read this cycle:
            // 0x00460C94 is d825cc855d00 fsub, not fld.
            // Settled 148.0-10.0 is 138.0. That is not dest.
            // The 322.0 push at 0x00460CE1 is later. Do not
            // invent dest from 10.0.
            _ = RetailLevelSelectFsub10.Delta(
                RetailLevelSelectFsub148.SettledPad);
            // RetailLevelSelectLater148: later leftover after the
            // 10.0 fsub is the second identical fld 148.0 /
            // fsub [esi+0x3460] / fstp [esp+0x14] triple at
            // 0x00460E24. Official 74154bfa independently
            // re-read this cycle. First consumers are
            // 0x00460E9D fcomp 0x00629390 and 0x00460EB0
            // fcomp 0x00629394. The local is a later window,
            // not dest. Do not invent dest from those
            // compares. Dest stays the measured node centres.
            if (RetailLevelSelectLater148.Applies(
                    RetailLevelSelectLater148.Pad(
                        RetailLevelSelectLater148.SettledField)))
            {
                DrawLevelNodeGraph();
                // RetailLevelSelectLaterEsp94: later leftover
                // after the later 148.0 triple is
                // fld [esp+0x94] / fsub [0x005D8BC4] (0.75) /
                // fmul [0x005D85BC] (4.0) / fcom [0x005D856C]
                // (0.0). Official 74154bfa independently
                // re-read this cycle. Different stack local,
                // not dest. First store consumer is
                // 0x00460E4D fst [esp+0x40]. Do not invent
                // dest from 0.75 or 4.0.
                _ = RetailLevelSelectLaterEsp94.Subtrahend;
                _ = RetailLevelSelectLaterEsp94.Factor;
                // RetailLevelSelectLaterOne: later leftover
                // after the later [esp+0x94] shift is
                // fcom [0x005D8568] (1.0) / fmul [0x005D8C70]
                // (255.0). Official 74154bfa independently
                // re-read this cycle. First store consumer is
                // 0x00460E7F fistp [esp+0x4C]. That is a
                // clamp-and-scale of the shifted local, not
                // dest. The later 610.0/0.0 pair at
                // 0x00460F30 is RetailLevelSelectLater610.
                // Do not invent dest from 1.0 or 255.0.
                // Do not invent a fade.
                _ = RetailLevelSelectLaterOne.CompareOne;
                _ = RetailLevelSelectLaterOne.Scale;
                // RetailLevelSelectLater610: later leftover
                // after the later 1.0 fcom is
                // fld [esp+0x14] / fcomp [0x005DB5B0]
                // (610.0) / fld [esp+0x14] /
                // fcomp [0x005D856C] (0.0). Official
                // 74154bfa independently re-read this
                // cycle. First consumer is 0x00460F5A
                // mov eax, [esi+ebx*4+0x4]. First store
                // is 0x00460F5E mov [esp+0x28], 0. That
                // is a later window on the same
                // [esp+0x14] local, not dest. The later
                // fmul 60.0 at 0x00460F73 is
                // RetailLevelSelectLater60. Do not invent
                // dest from 610.0 or 0.0.
                _ = RetailLevelSelectLater610.Applies(
                    RetailLevelSelectLater148.Pad(
                        RetailLevelSelectLater148.SettledField));
                _ = RetailLevelSelectLater610.WindowHigh;
                _ = RetailLevelSelectLater610.WindowLow;
                // RetailLevelSelectLater60: later leftover
                // after the later 610.0/0.0 pair is
                // fild [esp+0x3C] / fmul [0x005DB538]
                // (60.0) / fmul [0x005D85EC] (0.5) /
                // fadd [0x005DB3E8] (320.0) / fstp
                // [esp+0x18]. Official 74154bfa
                // independently re-read this cycle. First
                // store is 0x00460F85 fstp [esp+0x18].
                // That is a scaled local, not dest. The
                // later fld [esp+0x94] / fcomp 1.0 at
                // 0x00460FD8 is
                // RetailLevelSelectLaterEsp94One. Do not
                // invent dest from 60.0, 0.5, or 320.0.
                _ = RetailLevelSelectLater60.Factor;
                _ = RetailLevelSelectLater60.Half;
                _ = RetailLevelSelectLater60.Addend;
                // RetailLevelSelectLaterEsp94One: later leftover
                // after the later 60.0/0.5/320.0 scale is
                // fld [esp+0x94] / fcomp [0x005D8568]
                // (1.0). Official 74154bfa independently
                // re-read this cycle. First consumer of
                // the equal-1 fall-through is 0x00460FEC
                // fld [esp+0x18]. That is a compare of
                // the [esp+0x94] local, not dest. The
                // later fadd 20.0 at 0x00460FF0 is later.
                // Do not invent dest from 1.0 or 20.0.
                _ = RetailLevelSelectLaterEsp94One.Applies(
                    RetailLevelSelectLaterEsp94One.CompareOne);
                _ = RetailLevelSelectLaterEsp94One.CompareOne;
                // RetailLevelSelectLater20: later leftover after
                // the later [esp+0x94]/fcomp 1.0 compare is
                // fld [esp+0x18] / fadd [0x005D857C] (20.0) /
                // fstp [esp]. Official 74154bfa independently
                // re-read this cycle. First store is 0x00460FF7
                // fstp [esp]. That is an addend on the later-60
                // local, not dest. The later second fadd 20.0 at
                // 0x00460FFE is later. Do not invent dest from
                // 20.0 or 1.0.
                _ = RetailLevelSelectLater20.Offset(
                    RetailLevelSelectLater60.Scaled(1));
                _ = RetailLevelSelectLater20.Addend;
                // RetailLevelSelectLaterFadd20: later leftover
                // after the later first 20.0 addend is
                // fld [esp+0x18] / fadd [0x005D857C] (20.0) /
                // fstp [esp]. Official 74154bfa independently
                // re-read this cycle. First store is 0x00461005
                // fstp [esp]. That is a second addend on a later
                // [esp+0x18] local, not dest. The later fsub
                // 20.0 at 0x0046100C is later. Do not invent
                // dest from 20.0 or 1.0.
                _ = RetailLevelSelectLaterFadd20.Offset(
                    RetailLevelSelectLater20.Offset(
                        RetailLevelSelectLater60.Scaled(1)));
                _ = RetailLevelSelectLaterFadd20.Addend;
                // RetailLevelSelectLaterFsub20: later leftover
                // after the later second 20.0 addend is
                // fld [esp+0x20] / fsub [0x005D857C] (20.0) /
                // fstp [esp]. Official 74154bfa independently
                // re-read this cycle. First store is 0x00461013
                // fstp [esp]. That is a subtrahend on a later
                // [esp+0x20] local, not dest. The later second
                // fsub 20.0 at 0x0046101A is later. Do not
                // invent dest from 20.0 or 1.0.
                _ = RetailLevelSelectLaterFsub20.Offset(
                    RetailLevelSelectLater60.Scaled(1));
                _ = RetailLevelSelectLaterFsub20.Subtrahend;
            }
        }

        for (int index = 0; index < LevelColumnLabels.Length; index++)
        {
            (string text, float x) = LevelColumnLabels[index];
            DrawText(
                text,
                new Vector2(x, LevelSelectColumnLabelTop),
                LevelSelectColumnLabelScale,
                ReleasedBlue);
        }

        // RetailLevelSelectSlidingBorders: CFEPLevelSelect::Render first
        // leftover is the unique call 0x00460B61 to
        // CFrontEnd__DrawSlidingTextBordersAndMask. FrontEnd.cpp:891-892 —
        // FET3_SELECT_BRACKET1 at SELECT_BRACKET_X/Y (328,343) with
        // SELECT_BRACKET_SCALE 1.25, plus its +5/+10 shadow at scale*1.05 in
        // 0x3F000000. FEP_LEVEL_SELECT is one of the pages
        // got_standard_SlidingTextBordersAndMask() returns TRUE for
        // (FrontEnd.cpp:783), which pins transition to 1 and therefore this
        // settled scale; the outside bracket only draws while dest == FEP_MAIN.
        // The 148.0 fsub at 0x00460B66 is RetailLevelSelectFsub148
        // and is not dest.
        //
        // MEASURED, and this page does NOT reproduce the 1.4 the FEP_DEVSELECT
        // build settled on: fitting the FE_select_level_bracket01 alpha mask over
        // 4,000 sampled retail metal pixels (header band, emblem, and chevrons
        // excluded) peaks at 96.1% overlap at scale 1.25, centre (329,343), and
        // the whole 1.10-1.74 scale sweep has its maximum there. Scale 1.4 is not
        // a local optimum on this frame. The source constants are therefore used
        // verbatim. The shadow reproduces exactly: 0x3f000000 over (23,23,48) is
        // (17,17,36), which is the third most common colour in the capture.
        if (RetailLevelSelectSlidingBorders.Applies(
                standardPage: true,
                fromVirtualKeyboard: false))
        {
            const float bracketScale = RetailLevelSelectSlidingBorders.SettledInsideScale;
            const float bracketShadowScale = bracketScale * ShadowScaleBoost;
            DrawSurfaceCentered(_levelBracket01, 333f, 353f, bracketShadowScale, bracketShadowScale, ShadowTint);
            DrawSurfaceCentered(_levelBracket01, 328f, 343f, bracketScale, bracketScale, BracketTint);
        }

        // font22 at scale 1, for the glyph-run and per-letter-IoU evidence
        // retained in Tests/CareerNameReference.cs. Retail's ink here is x304..471, y72..88,
        // and its "SELECT" glyph widths are byte-identical to the SELECT
        // CONFIGURATION title that is already drawn in font22.
        //
        // BASELINE MOVED: this page's pinned capture changes in the header band.
        DrawRect(new Rect2(191f, 69f, 394f, 21f), HeaderBoxTint);
        float titleWidth = MeasureFont22Text(_selectLevelText, 1f);
        DrawFont22Text(
            _selectLevelText,
            new Vector2(HeaderBarCenterX - (titleWidth * 0.5f), HeaderTitleTop),
            1f,
            1f,
            ReleasedTitleText);

        DrawText(
            LevelSelectEpisodeText,
            new Vector2(LevelSelectEpisodeLeft, LevelSelectEpisodeTop),
            LevelSelectBodyScale,
            Colors.White);
        // The name band follows the SELECTED node: the language table carries
        // an N.NN row for every career world (english-worlds.json slot law),
        // and retail's own selector reads the loaded career — the band showing
        // the selected node's row is the only law consistent with shipped
        // data (PARITY.md 2026-08-22; FEPLevelSelect.cpp is not in the drop).
        DrawText(
            _session.SelectedLevelName,
            new Vector2(LevelSelectEpisodeLeft, LevelSelectLevelNameTop),
            LevelSelectBodyScale,
            ReleasedSelected);

        // Same FE_Arrow content region and lit-metal tint as FEP_DEVSELECT; both
        // chevrons sit at the same y on this page, unlike the dev-select frame.
        var arrowSource = new Rect2(16f, 12f, 30f, 40f);
        DrawTextureRectRegion(_feArrow, new Rect2(9f, 438f, -28f, 36f), arrowSource, BracketTint);
        DrawTextureRectRegion(_feArrow, new Rect2(604f, 437f, 28f, 36f), arrowSource, BracketTint);
    }

    /// <summary>
    /// The three episode sweep curves behind the node graph.
    ///
    /// A least-squares circle fitted to 279 intensity-weighted centre points of
    /// the middle curve — one per row from y=183 to y=461, the span over which it
    /// is unobstructed — gives centre (485.84, 320.38), radius 249.28 and apex
    /// x=236.56, with a maximum residual of 1.81px (and under 0.4px above y=440).
    /// The other two are the same circle offset by -120 and +240 in x, which the
    /// independently measured apexes confirm: 116.5 / 236.5 / 476.5 against
    /// 116.56 / 236.56 / 476.56 predicted. The drawn span is the measured one.
    ///
    /// This is a measured geometric reconstruction, not an identified sprite: the
    /// retail art that draws these curves has not been located, and the colour is
    /// the measured line core (133,133,158). Retail's own line reads as an
    /// additive composite (its delta over the background is equal in all three
    /// channels), which this alpha-blended draw does not reproduce.
    /// </summary>
    private void DrawLevelSweepArcs()
    {
        for (int index = 0; index < SweepArcCenters.Length; index++)
        {
            DrawArc(
                new Vector2(SweepArcCenters[index], SweepArcCenterY),
                SweepArcRadius,
                SweepArcStartAngle,
                SweepArcEndAngle,
                96,
                index == 0 ? LevelSweepArcCurrent : LevelSweepArcOther,
                SweepArcWidth,
                antialiased: true);
        }
    }

    /// <summary>
    /// The level-node graph: link lines first, then the rings that occlude them.
    ///
    /// Links are trimmed to the node outer radius rather than run centre-to-centre
    /// because retail's rings are open in the middle and no line shows through
    /// them — the y=320 link between the x=208 and x=268 nodes is visible only
    /// across x230..250, which is exactly edge to edge.
    ///
    /// Ring identity is measured, not assumed. Correlating the reference against
    /// each candidate alpha mask over a 47x47 box around an isolated node scores
    /// FE_select_level_ring_bracket01 at 0.63 (best drawn size 64) against
    /// ring_bracket02 at 0.56 (best size 84), and the colour ratio settles it —
    /// see <see cref="LevelNodeRingTint"/>. The current node adds ring_bracket01
    /// at full brightness, best size 79 centred (148,321), over ring_bracket02 at
    /// best size 62; both fits are peaks of an exhaustive size sweep.
    /// </summary>
    private void DrawLevelNodeGraph()
    {
        foreach ((int from, int to) in LevelNodeLinks)
        {
            Vector2 a = LevelNodes[from];
            Vector2 b = LevelNodes[to];
            Vector2 direction = (b - a).Normalized();
            float radiusA = from == 0 ? CurrentNodeOuterRadius : NodeOuterRadius;
            float radiusB = to == 0 ? CurrentNodeOuterRadius : NodeOuterRadius;
            DrawLine(
                a + (direction * radiusA),
                b - (direction * radiusB),
                LevelLinkLine,
                NodeLinkWidth,
                antialiased: true);
        }

        for (int index = 1; index < LevelNodes.Length; index++)
        {
            DrawSurfaceCentered(
                _levelRing01,
                LevelNodes[index].X,
                LevelNodes[index].Y,
                NodeRingSize / _levelRing01.GetWidth(),
                NodeRingSize / _levelRing01.GetHeight(),
                LevelNodeRingTint);
        }

        Vector2 current = LevelNodes[0];
        DrawSurfaceCentered(
            _levelRing01,
            current.X,
            current.Y,
            CurrentNodeRingSize / _levelRing01.GetWidth(),
            CurrentNodeRingSize / _levelRing01.GetHeight(),
            BracketTint);
        DrawSurfaceCentered(
            _levelRing02,
            current.X,
            current.Y,
            CurrentNodeInnerRingSize / _levelRing02.GetWidth(),
            CurrentNodeInnerRingSize / _levelRing02.GetHeight(),
            BracketTint);
    }

    /// <summary>
    /// FEP_MAIN's underlay: the flat page fill with FEBack128.vid composited
    /// additively over it.
    ///
    /// THE ARGUMENT THIS REPLACED, AND WHY IT WAS WRONG. The previous
    /// implementation drew a flat (23,23,48) fill, justified by the observation
    /// that two disjoint 120x120 regions of the retail main-menu reference hold
    /// exactly one colour at sd 0.0, which a stretched 128-square video cannot
    /// produce. That observation was correct and the conclusion did not follow:
    /// every capture it rested on was taken with `-skipfmv`, and `-skipfmv`
    /// removes the video. The same "zero variance, so no video" signature had
    /// already been shown to be reproduced on FEP_LEVEL_SELECT, a page that DOES
    /// carry the video. The comment that stood here named the experiment that
    /// would settle it — one main-menu frame captured without `-skipfmv` — and
    /// that frame has now been taken.
    ///
    /// MEASURED, from retail without `-skipfmv`
    /// (local-lab/retail-reference-pristine/nofmv-frontend-2026-07-26/, two runs,
    /// phase-anchored to the click that leaves click-to-start):
    ///
    ///   identity   the underlay IS FEBack128.vid. Scoring every decoded strip
    ///              frame upscaled 128^2 -> 640x480 by normalised cross-correlation
    ///              over the 222,683 pixels the `-skipfmv` reference proves are
    ///              pure underlay peaks at ncc +0.81..+0.92 on five sampled frames.
    ///   rate       best-match frame is 30 at t=1020 ms, 74 at 2529, 119 at 4030,
    ///              164 at 5522, 209 at 7027 — 29.80 fps, i.e. the shipped 30.
    ///   phase      that line passes through frame 0 at t = 13 ms. The clip starts
    ///              when the frontend leaves click-to-start, within one frame.
    ///   composite  flat fill PLUS gain x frame (see FeBackUnderlayGain). Alpha
    ///              mix is refuted on the same pixels.
    ///
    /// The composite is baked into the frame textures at load rather than issued as
    /// an additive draw. That is exact here and not an approximation: this is the
    /// bottom-most layer, it is drawn over a known constant fill, and
    /// fill + gain x frame peaks at 114 so nothing clamps. It also avoids depending
    /// on a canvas blend mode. The only additive helper this file had was
    /// measurably NOT additive (see the retained MainMenu reference's reflection note), and a
    /// layer this large must not inherit that defect.
    /// </summary>
    /// <param name="transition">
    /// <c>trans</c> for FEP_MAIN. The video ramps IN with the incoming page:
    /// <c>CFrontEnd::DrawStandardVideoBackground</c>, FrontEnd.cpp:1023-1045.
    ///
    /// <para><b>The law is ported; the BRANCH SELECTION is measured, and that
    /// distinction is the honest part of this method.</b> FrontEnd.cpp:1038-1041
    /// offers exactly two alphas —
    /// <c>MakeAlpha(RangeTransition(transition, 0, 0.5))</c> when the other page is
    /// FEP_MAIN and <c>MakeAlpha(RangeTransition(transition, 0.5, 1))</c>
    /// otherwise — and <c>dest</c> at FrontEnd.cpp:1299-1305 is the OTHER page, so
    /// the literal condition for FEP_MAIN's own call selects the second. The second
    /// is REFUTED: fitting retail's underlay strength as
    /// <c>pixel = fill + a * gain * FEBack[k]</c> over the pure-underlay box
    /// (0,181)-(120,300) gives a = 0.000 with zero residual at t = 14 ms (run1) and
    /// t = 29 ms (run2) — the box is bit-exactly the flat fill — and then
    /// a = 1.07 at t = 422 ms, 1.13 at 524 ms, 1.02 at 1020 ms. Full video at
    /// 422 ms cannot come from a (0.5, 1) window on a 50-frame transition. The
    /// (0, 0.5) window does produce it, so that is the branch taken here.</para>
    ///
    /// <para>Neither branch is FEP_MAIN's own: the video draw belongs to
    /// <c>CFEPMain__RenderPreCommon</c> (0x00462B70), which has no source in the
    /// drop and no decompile in this lab, and the source comment at
    /// FrontEnd.cpp:1025-1034 says the DirectX video is async-loading and "needs
    /// time before it's visible" independently of any alpha. So the exact retail
    /// mechanism for the first ~400 ms is NOT established. What is established is
    /// the pair of measurements above, and the ported law is the one of the two
    /// available that reproduces them.</para>
    /// </param>
    private void DrawMainUnderlay(float transition)
    {
        // The flat page fill is drawn FIRST and opaque, then the baked
        // fill+gain*frame composite over it at the video's own alpha. That is
        // exact rather than convenient: a * (fill + gain*frame) + (1-a) * fill
        // == fill + a * gain * frame, which is the released additive composite
        // with the alpha applied only to the video term. Modulating the baked
        // texture alone would have faded the FILL as well, and retail's page fill
        // is present at full strength on the very first frame.
        // Clear first, then the 24.31% black darkener over it — retail's own two
        // terms rather than their product. See FrontendClearColor /
        // FrontendFillDarkener for the measurement. The darkener keeps retail's
        // measured overhang (40px left and right, 3px top and bottom past the
        // client): it lands on the letterbox bars, which _Draw has already filled
        // with black, so 24% black over black leaves them black and the client
        // area is unaffected.
        DrawRect(new Rect2(0f, 0f, DesignWidth, DesignHeight), FrontendClearColor);
        DrawRect(new Rect2(-40f, -3f, DesignWidth + 80f, DesignHeight + 6f), FrontendFillDarkener);

        if (_feBackFrames.Length == 0)
        {
            // Strip missing (materialize not run). The flat fill above is what the
            // page held before the video was identified, and it is strictly better
            // than drawing nothing.
            return;
        }

        float alpha = MakeAlpha(RangeTransition(transition, 0f, 0.5f));
        if (alpha <= 0f)
        {
            return;
        }

        int frame = FeBackFrameIndex(_feBackSeconds, _feBackFrames.Length);
        DrawTextureRect(
            _feBackFrames[frame],
            new Rect2(0f, 0f, DesignWidth, DesignHeight),
            false,
            new Color(1f, 1f, 1f, alpha));
    }

    /// <summary>
    /// Which FEBack128 frame is on screen at <paramref name="seconds"/> after the
    /// frontend left click-to-start. Pure, so it is unit-testable without Godot.
    ///
    /// <para><b>The phase, and the alias that nearly took its place.</b></para>
    /// Fitting best-matching strip frames over a 7 s retail burst gave a clean
    /// 29.80 fps line through frame 0 at t = 13 ms. It also gave, on EVERY sample,
    /// a near-equal runner-up exactly +205 frames away. An independent adversarial
    /// pass flagged that as an alias risk rather than clip self-similarity, and
    /// it was right to: normalised cross-correlation cannot pick the origin of a
    /// self-similar signal from peaks that are within noise of each other, and a
    /// 7 s window is barely a third of the clip's 19.07 s period.
    ///
    /// Settled by capturing 22 s of retail main menu - more than one full loop -
    /// and scoring the WHOLE burst against each candidate offset instead of
    /// scoring each frame independently. Over 56 frames and 521 candidate offsets:
    ///
    ///   offset  -3    mean ncc 0.8546   min  0.6983   frames below 0.5:  0
    ///   offset +202   mean ncc 0.5112   min -0.2441   frames below 0.5: 23
    ///   offset -206   mean ncc 0.3791   min -0.2412   frames below 0.5: 34
    ///
    /// -3 is the global argmax. The +205 coset is refuted, and the true phase is
    /// three frames LATER than the short-window fit said - frame 0 at t = 100 ms,
    /// not 13 ms. That correction was predicted independently: before it was
    /// applied, our sweep's best match to each retail frame sat at a median
    /// -74 ms, i.e. our underlay ran about two and a half frames early.
    /// </summary>
    internal static int FeBackFrameIndex(double seconds, int frameCount)
    {
        if (frameCount <= 0)
        {
            return 0;
        }

        // Rounding, not truncation, because the offset above was fitted against
        // round(t x 30 / 1000); truncating here would silently re-introduce half a
        // frame of the very phase error the offset exists to remove.
        long index = (long)Math.Round(seconds * FeBackFps) - FeBackPhaseFrames;
        if (index <= 0)
        {
            return 0;
        }

        return (int)(index % frameCount);
    }

    /// <summary>The released clamp idiom, <c>_DAT_005d856c</c> / <c>_DAT_005d8568</c>.</summary>
    private static float Clamp01(float value) => value < 0f ? 0f : value > 1f ? 1f : value;

    /// <summary>
    /// <c>RangeTransition(t, lo, hi)</c> — the drop's normalise-and-clamp helper.
    ///
    /// Its body is NOT in the drop: Frontend.h:292 includes TransitionHelpers.h,
    /// which is one of the 200 absent headers, and no other file defines it. That
    /// it CLAMPS rather than extrapolating is settled from three independent uses
    /// that are only correct under clamping:
    /// FrontEnd.cpp:856-866 writes <c>alpha = 0</c> for transition &lt; 0.2 and
    /// then immediately overwrites it with <c>MakeAlpha(RangeTransition(t,0.2,0.5))</c>
    /// through a second non-else <c>if</c> — harmless dead code under clamping,
    /// a negative alpha without it; FrontEnd.cpp:1039 uses
    /// <c>MakeAlpha(RangeTransition(t,0,0.5))</c> as an alpha for all t up to 1;
    /// and FEPGoodies.cpp:1849 does <c>SINT(RangeTransition(t,0.75,1)*255)</c> for
    /// t from 0. The shipped main menu computes the same shape inline with an
    /// explicit clamp at every site (0x00462D40), which corroborates it.
    /// </summary>
    private static float RangeTransition(float value, float low, float high) =>
        Clamp01((value - low) / (high - low));

    /// <summary>
    /// <c>MakeAlpha(t)</c> — also absent from the drop; the shipped inline form is
    /// <c>ROUND(clamp(t) * 255.0)</c> clamped to 0..255 (<c>_DAT_005d8c70</c> =
    /// 255.0, verified in the pristine specimen), returned here as 0..1.
    /// </summary>
    private static float MakeAlpha(float value) =>
        Math.Clamp(MathF.Round(Clamp01(value) * 255f), 0f, 255f) / 255f;

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

    private void LoadLocalization()
    {
        const string resourcePath = "res://Assets/Frontend/english.json";
        string source = Godot.FileAccess.GetFileAsString(resourcePath);
        if (string.IsNullOrEmpty(source))
        {
            throw new InvalidDataException($"Released frontend localization is missing: {resourcePath}");
        }

        using JsonDocument document = JsonDocument.Parse(source);
        JsonElement root = document.RootElement;
        if (root.GetProperty("schema").GetString() != "onslaught.frontend-strings.v1" ||
            root.GetProperty("culture").GetString() != "en" ||
            root.GetProperty("sourceSha256").GetString() !=
                "789ecff619d077092769df281c540d138a25fcc74d70023466a604888e59371a")
        {
            throw new InvalidDataException("Released frontend localization has unexpected identity.");
        }

        JsonElement strings = root.GetProperty("strings");
        _menuText.Add(RetailFrontendMenuItemKind.NewGame, RequiredString(strings, "newGame"));
        _menuText.Add(RetailFrontendMenuItemKind.ContinueGame, RequiredString(strings, "continueGame"));
        _menuText.Add(RetailFrontendMenuItemKind.LoadGame, RequiredString(strings, "loadGame"));
        _menuText.Add(RetailFrontendMenuItemKind.Multiplayer, RequiredString(strings, "multiplayer"));
        _menuText.Add(RetailFrontendMenuItemKind.Goodies, RequiredString(strings, "goodies"));
        _menuText.Add(RetailFrontendMenuItemKind.Options, RequiredString(strings, "options"));
        // Index 6 menu label = FrontEndText token 8 → english.dat "Quit" (KEEP).
        // Messbox copy is Localization id 0xe4 (EXE table), not drawn on the row.
        _menuText.Add(RetailFrontendMenuItemKind.Quit, RequiredString(strings, "quit"));
        _selectLevelText = RequiredString(strings, "selectLevel");
        // The band and briefing draw the SELECTED node's row through
        // RetailFrontendWorldStrings; this load receipt stays as the proof
        // the menu table itself is present and identity-checked.
        _level100Text = RequiredString(strings, "level100");
        if (_level100Text != OnslaughtRebuild.Core.RetailFrontendWorldStrings.LevelName(100))
        {
            throw new InvalidDataException(
                "english.json level100 row diverged from the decoded world-strings table.");
        }
        _loadingText = RequiredString(strings, "loading");
    }

    private static string RequiredString(JsonElement strings, string key)
    {
        string? value = strings.GetProperty(key).GetString();
        return string.IsNullOrEmpty(value)
            ? throw new InvalidDataException($"Released frontend localization is missing '{key}'.")
            : value;
    }

    private static Texture2D[] LoadFeBackFrames(int maximumFrames = int.MaxValue)
    {
        using Resource recipe = GD.Load<Resource>("res://Scenes/Frontend/FrontendUnderlay.tres");
        using Variant returned = recipe.Call("load_frames", maximumFrames);
        using Godot.Collections.Dictionary result = returned.AsGodotDictionary();
        RequireOptionsResult(result);
        if (result["missing"].AsBool())
            GD.PushWarning($"FEBack strip missing at {FeBackStripPath}; main underlay uses solid fallback.");
        using Variant frameList = result["frames"];
        using Godot.Collections.Array frames = frameList.AsGodotArray();
        var textures = new Texture2D[frames.Count];
        for (int index = 0; index < textures.Length; index++)
        {
            using Variant frame = frames[index];
            textures[index] = frame.As<Texture2D>();
        }
        return textures;
    }

    private new void DrawSetTransform(Vector2 position, float rotation = 0f, Vector2? scale = null)
    {
        if (_paintingPart is null) return;
        Vector2 ratio = _paintingPart.Size / SourceRect.Size;
        var authored = new Transform2D(new Vector2(ratio.X, 0f), new Vector2(0f, ratio.Y), -SourceRect.Position * ratio);
        var measured = new Transform2D(rotation, scale ?? Vector2.One, 0f, position);
        _paintingPart.DrawSetTransformMatrix(authored * measured);
    }
    private new void DrawRect(Rect2 rect, Color color, bool filled = true, float width = -1f, bool antialiased = false)
    {
        if (DrawsSceneSection) _paintingPart!.DrawRect(rect, color, filled, width, antialiased);
    }
    private new void DrawTextureRect(Texture2D texture, Rect2 rect, bool tile, Color? modulate = null, bool transpose = false)
    {
        if (_captureGeometry) _rings.Add(new(texture, rect, modulate ?? Colors.White));
        if (DrawsSceneSection) _paintingPart!.DrawTextureRect(texture, rect, tile, modulate, transpose);
    }
    private new void DrawTextureRectRegion(Texture2D texture, Rect2 rect, Rect2 source, Color? modulate = null,
        bool transpose = false, bool clipUv = true)
    {
        if (DrawsSceneSection) _paintingPart!.DrawTextureRectRegion(texture, rect, source, modulate, transpose, clipUv);
    }
    private new void DrawArc(Vector2 center, float radius, float startAngle, float endAngle, int pointCount, Color color, float width = -1f, bool antialiased = false)
    {
        if (_captureGeometry) _arcs.Add(new(center, radius, startAngle, endAngle, pointCount, color, width, antialiased));
        if (DrawsSceneSection) _paintingPart!.DrawArc(center, radius, startAngle, endAngle, pointCount, color, width, antialiased);
    }
    private new void DrawLine(Vector2 from, Vector2 to, Color color, float width = -1f, bool antialiased = false)
    {
        if (_captureGeometry) _lines.Add(new(from, to, color, width, antialiased));
        if (DrawsSceneSection) _paintingPart!.DrawLine(from, to, color, width, antialiased);
    }
}
