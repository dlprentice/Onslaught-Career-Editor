// SPDX-License-Identifier: GPL-3.0-or-later
using Godot;
using OnslaughtRebuild.Client;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Test-only retained Career Name renderer from 14f6f72b RetailFrontendFlow.cs.
/// DrawDevSelect, its font/underlay arithmetic and source-frame dispatch retain
/// their operation order. Only the session fields are supplied by this harness.
/// Original Frontend.tscn sections remain the comparison coordinate frames.
/// This establishes migration equivalence, not new retail parity: the header
/// end caps/emblem and the incoming transition remain the documented gaps.
/// </summary>
public sealed partial class CareerNameReference : Control
{
    private const float DesignWidth = 640f, DesignHeight = 480f;
    private const int GlyphColumns = 16, GlyphCellSize = 16, FirstGlyph = 32, GlyphSlotCount = 256;
    private const int Font22Columns = 16, Font22CellSize = 32;
    private const float HeaderBarCenterX = 390f, HeaderTitleTop = 65f, ShadowScaleBoost = 1.05f;
    private const string DevSelectTitle = "CHOOSE GAME NAME";
    private const float DevSelectRowScale = 1.4f, DevSelectRowPitch = 24f, DevSelectRowX = 132f, DevSelectRowTop = 137f, DevSelectNameTop = 417f;
    private const string FeBackStripPath = "res://Assets/Frontend/Backgrounds/fe-back-128x128x30.rgb";
    private const int FeBackFps = 30, FeBackPhaseFrames = 3;
    private static readonly Color BracketTint = RetailColor(0xfe7f7f7f), ShadowTint = RetailColor(0x3e000000), ReleasedTitleText = RetailColor(0xff7f7f7f);
    private static readonly Color DevSelectRowText = RetailColor(0xff404040), DevSelectNameHighlight = RetailColor(0xff004050);
    // Measured framebuffer colours, not modulated sprite tints.
    private static readonly Color DevSelectPanelFill = new(9f / 255f, 9f / 255f, 18f / 255f, 1f);
    private static readonly Color DevSelectPanelBorder = new(130f / 255f, 132f / 255f, 139f / 255f, 1f);
    private static readonly Color DevSelectFieldBorder = new(159f / 255f, 162f / 255f, 165f / 255f, 1f);
    private static readonly Color DevSelectScrollDivider = new(127f / 255f, 129f / 255f, 132f / 255f, 1f);
    private static readonly Color DevSelectScrollThumb = new(245f / 255f, 249f / 255f, 245f / 255f, 1f);
    private static readonly Color DevSelectGuide = new(50f / 255f, 51f / 255f, 72f / 255f, 1f);
    private static readonly Color DevSelectGuideOverPanel = new(19f / 255f, 19f / 255f, 27f / 255f, 1f);
    private static readonly Color HeaderBoxTint = new(12f / 255f, 12f / 255f, 24f / 255f, 1f);
    private static readonly Color FrontendClearColor = new(31f / 255f, 31f / 255f, 63f / 255f, 1f);
    private static readonly Color FrontendFillDarkener = new(0f, 0f, 0f, 0x3Eu / 255f);
    internal static readonly IReadOnlyDictionary<string, Rect2> Sections = new Dictionary<string, Rect2>
    {
        ["Background"] = new(0, 0, 640, 480), ["Decoration"] = new(0, 0, 640, 480),
        ["Header"] = new(191, 65, 394, 32), ["List"] = new(128, 130, 403, 272),
        ["Name"] = new(128, 408, 403, 44), ["Navigation"] = new(9, 437, 622, 41),
    };
    private sealed record Frame(IReadOnlyList<string> CareerNames, int SelectedCareerIndex, string GameName, bool GameNameIsFresh);
    private Frame _session = new([], -1, "BEA 1", true);
    private Texture2D _levelBracket01 = null!, _feArrow = null!, _titleFont = null!, _font22 = null!;
    private Texture2D[] _feBackFrames = [];
    private int[] _glyphWidths = [], _font22Widths = [];
    private Control? _paintingPart;
    private string _drawingSection = string.Empty;
    private bool _initialized;
    private double _feBackSeconds;
    internal Texture2D BodyFont => _titleFont;
    internal Texture2D TitleFont => _font22;
    internal Texture2D Bracket => _levelBracket01;
    internal Texture2D Arrow => _feArrow;
    internal int[] BodyWidths => _glyphWidths.ToArray();
    internal int[] TitleWidths => _font22Widths.ToArray();
    internal Texture2D[] BackgroundFrames => _feBackFrames.ToArray();
    internal int MeasureNameExtent(string text) => MeasureGameNameExtent(text);
    internal Vector2 TitleOrigin => new(HeaderBarCenterX - (MeasureFont22Text(DevSelectTitle, 1f) * 0.5f), HeaderTitleTop);
    internal float NameWidth => Math.Max(0, _session.GameName.Sum(character =>
        _glyphWidths[RetailFrontendSession.GameNameRenderGlyphIndex(character, swapInvertedPunctuation: false)] + 1) - 1) * DevSelectRowScale;
    internal Vector2 NameOrigin => new(329.5f - (NameWidth * 0.5f), DevSelectNameTop);
    internal Rect2 HighlightRect => new(NameOrigin.X - 4f, 415f, NameWidth + 8f, 31f);
    internal static int HitTest(Vector2 point) => new Rect2(0f, 430f, 46f, 48f).HasPoint(point) ? 1
        : new Rect2(595f, 430f, 45f, 48f).HasPoint(point) || new Rect2(128f, 408f, 403f, 44f).HasPoint(point) ? 2 : 0;
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
        _levelBracket01 = LegacyCuratedAyaTextureReference.Load("res://Assets/Frontend/level-bracket-01.texture.aya", 512, 512, LegacyCuratedAyaTextureReference.Compression.Dxt2);
        _feArrow = LegacyCuratedAyaTextureReference.Load("res://Assets/Frontend/fe-arrow.texture.aya", 64, 64, LegacyCuratedAyaTextureReference.Compression.Dxt2);
        _titleFont = LegacyCuratedAyaTextureReference.Load("res://Assets/Hud/font-13ps.texture.aya", 256, 256, LegacyCuratedAyaTextureReference.Compression.Rgba8);
        _font22 = LegacyCuratedAyaTextureReference.Load("res://Assets/Hud/font-22.texture.aya", 512, 512, LegacyCuratedAyaTextureReference.Compression.Rgba8);
        using Image body = _titleFont.GetImage(); using Image title = _font22.GetImage();
        _glyphWidths = MeasureGlyphWidths(body, GlyphCellSize, GlyphColumns);
        _font22Widths = MeasureGlyphWidths(title, Font22CellSize, Font22Columns);
        _feBackFrames = LoadFeBackFrames();
        foreach (string name in Sections.Keys)
        {
            Control part = GetNode<Control>(name);
            part.Draw += () => DrawScenePart(part);
        }
        _initialized = true;
        Refresh();
    }
    internal void SetFrame(IReadOnlyList<string> names, int selected, string name, bool fresh, double background)
    {
        _session = new(Array.AsReadOnly(names.ToArray()), selected, name, fresh);
        _feBackSeconds = background; Refresh();
    }
    public override void _Ready() { Initialize(); SetProcess(false); SetProcessInput(false); SetProcessUnhandledInput(false); }
    private void Refresh() { foreach (string name in Sections.Keys) GetNode<Control>(name).QueueRedraw(); }
    private void DrawScenePart(Control part)
    {
        if (!_initialized || part.Size.X <= 0f || part.Size.Y <= 0f) return;
        _paintingPart = part; _drawingSection = string.Empty;
        try { DrawSetTransform(Vector2.Zero, 0f, Vector2.One); DrawDevSelect(); }
        finally { _paintingPart = null; _drawingSection = string.Empty; }
    }
    private void SelectSceneSection(string section) => _drawingSection = section;
    private bool DrawsSceneSection => _paintingPart is not null && "Career." + _paintingPart.Name == _drawingSection;
    private static void RequireOptionsResult(Godot.Collections.Dictionary result)
    {
        if (!result["ok"].AsBool()) throw new InvalidDataException(result["error"].AsString());
    }
    /// <summary>
    /// Retail FEP_DEVSELECT — the "CHOOSE GAME NAME" page reached from New Game
    /// and Load Game.
    ///
    /// New mode renders the editable name field; Load mode renders caller-injected
    /// read-only career rows. Client owns bounded row selection, accept/back, and
    /// the selected-career handoff. This lane carries no career persistence or
    /// implicit save discovery.
    ///
    /// Geometry is MEASURED from the pristine 640x480 retail capture
    /// local-lab/retail-reference-pristine/choose-game-name/choose-game-name-640x480.png
    /// by scanning for the exact fill colours it contains:
    ///   page background      flat (23,23,48)                — same fill proven for the main menu
    ///   header text box      interior (12,12,24), x191..584, y69..89
    ///   title text           white (254,254,254), x263..513, y73..88, centred on x=390
    ///   list panel           border (130,132,139) at x128/x530/y130/y401,
    ///                        interior (9,9,18) x129..529, y131..400
    ///   scrollbar divider    (127,129,132) 1px at x=510, y131..400
    ///   scrollbar thumb      (245,249,245) outline x515..525, y135..396
    ///   name field           border (159,162,165) at x128/x530/y408/y451,
    ///                        interior (9,9,18) x129..529, y409..450
    ///   name highlight       (0,128,159) x293..366, y415..445
    ///   career row text      (128,128,128), left edge x=132, pitch 24
    ///   faint guide lines    (50,51,72) at x=123 and y=180
    ///
    /// Two of those colours corroborate the released source directly:
    /// the header box interior is exactly black at 0x7f alpha over the page
    /// background, which is the literal `col = 0x7f000000` at
    /// references/Onslaught/FrontEnd.cpp:1127, and the title is drawn centred on
    /// HEADER_BAR_X = 390 (FrontEnd.cpp:1103) in 0xff7f7f7f (FrontEnd.cpp:1215).
    ///
    /// KNOWN GAPS, stated rather than faked: the metal header end-cap brackets
    /// (FET3_HEADER_BRACKET1, retail x182..190 and x585..598) and the blue
    /// Forseti emblem at top-left are drawn from textures this lane has not
    /// identified or materialized, so they are not drawn at all here.
    /// </summary>
    private void DrawDevSelect()
    {
        // Settled: the transition length into FEP_DEVSELECT is not evidenced.
        // Passing 1 keeps its settled rendering while both New Game and Load Game
        // use the Client-owned page state.
        SelectSceneSection("Career.Background");
        DrawMainUnderlay(1f);

        // Faint crosshair guides, present on this page and on the retail main
        // menu; the reconstruction has not drawn them anywhere before now.
        SelectSceneSection("Career.Guides");
        DrawRect(new Rect2(123f, 0f, 1f, DesignHeight), DevSelectGuide);
        DrawRect(new Rect2(0f, 180f, DesignWidth, 1f), DevSelectGuide);

        // FrontEnd.cpp:891-892 — FET3_SELECT_BRACKET1 at SELECT_BRACKET_X/Y
        // (328,343) with SELECT_BRACKET_SCALE 1.25, plus its +5/+10 shadow at
        // scale*1.05 in 0x3F000000. FEP_DEVSELECT is one of the pages
        // got_standard_SlidingTextBordersAndMask() returns TRUE for
        // (FrontEnd.cpp:780), which pins transition to 1 and therefore this
        // settled scale. The outside bracket only draws while dest == FEP_MAIN.
        // MEASURED (re-fit 2026-07-26, tools/frontend_arc_bracket_fit.py): this
        // page really does use SELECT_BRACKET_SCALE2 1.4, but the centre it was
        // previously paired with was wrong. Fitting the bracket alpha mask over
        // 4,000 sampled retail arc pixels peaks at 100.0% coverage at scale 1.40,
        // centre (329,344) — i.e. SELECT_BRACKET_X/Y (328,343) within 1px, the
        // same centre DrawLevelSelect uses. Scale 1.25 reaches only 13.8% there.
        // The response surface is single-peaked: 1.38 -> 97.3, 1.39 -> 99.2,
        // 1.40 -> 100.0, 1.41 -> 95.0. Robust across alpha threshold 16..200,
        // three sample seeds, and thin-run filter 3..20.
        //
        // The earlier 83.3%/1.39/(328,336) fit was contaminated by the level-map
        // episode curves and the FET3_HEADER_BRACKET1 end-caps; a geometric
        // thin-run filter removes both (the arc band is >=25px wide on every
        // scanline it occupies). The same method, run first as a mandatory
        // control on SELECT LEVEL, reaches 99.7% at 1.25/(329,344) — reproducing
        // that page's source constants and beating its previously recorded 96.1%.
        // So both pages are one texture at one centre with two source scales.
        SelectSceneSection("Career.Decoration");
        const float bracketScale = 1.4f;
        const float bracketShadowScale = bracketScale * ShadowScaleBoost;
        DrawSurfaceCentered(_levelBracket01, 333f, 353f, bracketShadowScale, bracketShadowScale, ShadowTint);
        DrawSurfaceCentered(_levelBracket01, 328f, 343f, bracketScale, bracketScale, BracketTint);

        // Header text box then the centred title.
        //
        // MEASURED 2026-07-26 — the title is font22 at scale 1, NOT Font13PS at
        // 1.5. Atlas-free proof, from the pristine captures alone: cut the header
        // title band (y70..92, x200..580, ink threshold >120) on all four header
        // pages, segment it into per-glyph column runs, and compare glyphs of the
        // SAME LETTER between pages at 1:1 with no rescaling.
        //
        //   page                  ink rows   ink x        per-glyph run widths
        //   MISSION BRIEFING      72..88     288..490     17,2,13,13,2,15,12,...
        //   SELECT CONFIGURATION  72..88     249..526     13,11,10,11,13,14,...
        //   SELECT LEVEL          72..88     304..471     13,11,10,11,13,14,...
        //   CHOOSE GAME NAME      72..88     263..513     13,12,15,15,13,11,...
        //
        // All four have identical 17-row ink height, and SELECT LEVEL's first six
        // glyph widths are byte-identical to SELECT CONFIGURATION's ("SELECT" on
        // both). Per-letter mask IoU at 1:1 against SELECT CONFIGURATION:
        // MISSION BRIEFING 0.992 (8 letters), SELECT LEVEL 0.990 (5 letters),
        // CHOOSE GAME NAME 0.979 (7 letters). Font13PS at 1.5 would have to be a
        // rescale of a 16px cell and could not land on the same integer glyph
        // widths as a 32px cell at 1:1; it does not.
        //
        // MISSION BRIEFING and SELECT CONFIGURATION are already drawn in font22
        // at scale 1 here (NCC 0.951 fit, DrawHeaderBarTitle), so this page and
        // SELECT LEVEL are corrected to the same call.
        //
        // BASELINE MOVED: this page's pinned no-regression capture changes in the
        // header band. That is intended and is the point of the change.
        SelectSceneSection("Career.Header");
        DrawRect(new Rect2(191f, 69f, 394f, 21f), HeaderBoxTint);
        float titleWidth = MeasureFont22Text(DevSelectTitle, 1f);
        DrawFont22Text(
            DevSelectTitle,
            new Vector2(HeaderBarCenterX - (titleWidth * 0.5f), HeaderTitleTop),
            1f,
            1f,
            ReleasedTitleText);

        // List panel: border, interior, scrollbar divider and thumb.
        SelectSceneSection("Career.List");
        DrawRect(new Rect2(128f, 130f, 403f, 272f), DevSelectPanelBorder);
        DrawRect(new Rect2(129f, 131f, 401f, 270f), DevSelectPanelFill);
        DrawRect(new Rect2(129f, 180f, 401f, 1f), DevSelectGuideOverPanel);
        DrawRect(new Rect2(510f, 131f, 1f, 270f), DevSelectScrollDivider);
        DrawScrollThumbOutline(new Rect2(515f, 135f, 11f, 262f));

        for (int index = 0; index < _session.CareerNames.Count; index++)
        {
            float rowTop = DevSelectRowTop + (index * DevSelectRowPitch);
            if (rowTop + (GlyphCellSize * DevSelectRowScale) > 400f)
            {
                break;
            }

            DrawText(
                _session.CareerNames[index],
                new Vector2(DevSelectRowX, rowTop),
                DevSelectRowScale,
                index == _session.SelectedCareerIndex ? ReleasedTitleText : DevSelectRowText);
        }

        // Name field: border, interior, selection highlight, then the name.
        SelectSceneSection("Career.Name");
        DrawRect(new Rect2(128f, 408f, 403f, 44f), DevSelectFieldBorder);
        DrawRect(new Rect2(129f, 409f, 401f, 42f), DevSelectPanelFill);

        float nameWidth = Math.Max(0, _session.GameName.Sum(character =>
            _glyphWidths[RetailFrontendSession.GameNameRenderGlyphIndex(character, swapInvertedPunctuation: false)] + 1) - 1) * DevSelectRowScale;
        var nameOrigin = new Vector2(329.5f - (nameWidth * 0.5f), DevSelectNameTop);
        if (_session.GameNameIsFresh)
            DrawRect(new Rect2(nameOrigin.X - 4f, 415f, nameWidth + 8f, 31f), DevSelectNameHighlight);
        DrawAtlasText(_titleFont, _glyphWidths, GlyphCellSize, GlyphColumns,
            _session.GameName, nameOrigin, DevSelectRowScale, DevSelectRowScale, ReleasedTitleText,
            dropShadow: true, retailNameGlyphs: true);

        // Page chevrons. FE_Arrow points right and its artwork occupies only
        // (16,12)-(46,52) of the 64x64 texture, exactly as DrawLanguageSelector
        // measured; the left chevron is the mirrored draw.
        // Measured extents: right chevron x604..631 y437..472, left chevron the
        // mirrored pair six rows lower; both render in the same lit metal as the
        // arcs (~(107,117,131)), not the faint ChromeTint the language selector uses.
        SelectSceneSection("Career.Navigation");
        var arrowSource = new Rect2(16f, 12f, 30f, 40f);
        DrawTextureRectRegion(_feArrow, new Rect2(36f, 443f, -27f, 35f), arrowSource, BracketTint);
        DrawTextureRectRegion(_feArrow, new Rect2(604f, 437f, 27f, 35f), arrowSource, BracketTint);
    }

    /// <summary>1px outline for the list scrollbar thumb.</summary>
    private void DrawScrollThumbOutline(Rect2 rect)
    {
        DrawRect(new Rect2(rect.Position.X, rect.Position.Y, rect.Size.X, 1f), DevSelectScrollThumb);
        DrawRect(
            new Rect2(rect.Position.X, rect.Position.Y + rect.Size.Y - 1f, rect.Size.X, 1f),
            DevSelectScrollThumb);
        DrawRect(new Rect2(rect.Position.X, rect.Position.Y, 1f, rect.Size.Y), DevSelectScrollThumb);
        DrawRect(
            new Rect2(rect.Position.X + rect.Size.X - 1f, rect.Position.Y, 1f, rect.Size.Y),
            DevSelectScrollThumb);
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
        bool dropShadow,
        bool retailNameGlyphs = false)
    {
        float x = position.X;
        foreach (char character in text)
        {
            int glyph = retailNameGlyphs ? RetailFrontendSession.GameNameRenderGlyphIndex(character, swapInvertedPunctuation: false) : GlyphIndex(character);
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

    private int MeasureGameNameExtent(string text)
    {
        int width = 0;
        foreach (char character in text)
        {
            int glyph = RetailFrontendSession.GameNameRenderGlyphIndex(character, swapInvertedPunctuation: true);
            width += _font22Widths[glyph] + 1;
        }
        return width;
    }

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
