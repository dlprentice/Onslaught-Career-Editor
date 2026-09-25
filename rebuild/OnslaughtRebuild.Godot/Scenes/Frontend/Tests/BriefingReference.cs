// SPDX-License-Identifier: GPL-3.0-or-later
using Godot;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Test-only retained Mission Briefing renderer from 51477f62. Original draw,
/// wrapping and glyph arithmetic remains unchanged. The old body comment's
/// empty-means-nothing claim contradicts its executable world-100 fallback:
/// zero paragraphs select nine transcribed entries. Nonempty paragraphs do not
/// acquire an inserted blank separator. No RetailFrontendFlowWrapTests exists;
/// this harness measures the executable law, not that historical claim.
/// Missing briefing video and unresolved measured art stay outside this port.
/// </summary>
public sealed partial class BriefingReference : Control
{
    private const int GlyphColumns = 16, GlyphCellSize = 16, FirstGlyph = 32, GlyphSlotCount = 256;
    private const int Font22Columns = 16, Font22CellSize = 32;
    private static readonly Color BracketTint = RetailColor(0xfe7f7f7f);
    // MISSION BRIEFING / SELECT CONFIGURATION. Every literal in this block is
    // measured from the two pristine 640x480 captures taken 2026-07-25:
    //   local-lab/retail-reference-pristine/mission-briefing/05-mission-briefing-640x480.png
    //   local-lab/retail-reference-pristine/select-configuration/06-select-configuration-640x480.png
    // See DrawMissionBriefing and ConfigurationReference.cs for the per-element evidence.
    private const string MissionBriefingTitle = "MISSION BRIEFING";
    private const float HeaderBarCenterX = 390f;
    private const float HeaderTitleTop = 65f;
    private const float BriefingLevelNameLeft = 178.5f;
    private const float BriefingLevelNameTop = 118f;
    // The level name is the only text on either page drawn non-uniformly: the
    // free sx/sy fit peaks at sx 0.70 / sy 1.00 (score 0.808), and both a
    // uniform font22 and every Font13PS variant score below 0.48.
    private const float BriefingLevelNameScaleX = 0.70f;
    private const float BriefingLevelNameScaleY = 1.00f;
    private const float BriefingBodyLeft = 80f;
    private const float BriefingBodyTop = 163.5f;
    private const float BriefingBodyPitch = 16f;

    /// <summary>
    /// The widest briefing line retail drew: the pristine capture's longest
    /// line carries 286px of this renderer's advances (283px measured ink,
    /// within the known +2..+6 overshoot). WrapBriefingParagraphs breaks a
    /// candidate line only when it would exceed this.
    /// </summary>
    private const float BriefingBodyInkCeiling = 286f;
    // Retail's blank line does NOT advance a full 16: measured ink tops run
    // 167,183,199,215,231,247 then 273,289, so the paragraph break adds 10 on
    // top of the line the last paragraph line already advanced (247+16+10=273).
    private const float BriefingParagraphGap = 10f;
    // The rock background quad and the big ring, both fitted — see DrawBriefingStage.
    private const float BriefingBackgroundScale = 1.25f;
    private const float BriefingBackgroundLeft = -70f;
    private const float BriefingBackgroundTop = -80f;
    private const float BriefingRingSize = 990f;
    private const float BriefingRingCenterX = 267f;
    private const float BriefingRingCenterY = 221f;

    /// <summary>
    /// The briefing body, transcribed from the pristine capture. The
    /// localization backing for it WAS later found — english.dat carries the
    /// full sentences (pool slots after 0x015F8838/0x01625641) — so this
    /// literal is now only the world-100 receipt used when no session body
    /// is available, and the wrap-law test target: WrapBriefingParagraphs
    /// must reproduce these breaks from the table text.
    ///
    /// The transcription is corroborated, not assumed: summing this renderer's
    /// per-glyph advances for each line against the measured retail ink widths
    /// gives 286/283, 265/262, 285/283, 251/249, 281/279, 111/107, 271/268 and
    /// 237/231 — every line within the known +2..+6 advance overshoot and none
    /// outside it, which a mis-transcribed line would not be.
    /// </summary>
    private static readonly string[] BriefingBody =
    [
        "Tatiana will take you through the",
        "basics of piloting Battle Engine",
        "Aquila. This will cover everything",
        "from basic movement in both",
        "Walker and Jet modes as well as",
        "Weapons use.",
        "",
        "Listen to her advice and try to",
        "keep Colonel Kramer happy.",
    ];

    private static readonly Color ReleasedTitleText = RetailColor(0xff7f7f7f);
    // Briefing body ink measures (251,220,95) at its brightest; this modulate
    // renders (252,222,95).
    private static readonly Color BriefingBodyText = RetailColor(0xff7e6f30);
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
        ["LevelName"] = new(178.5f, 118, 407, 32), ["Body"] = new(80, 163.5f, 505, 122.5f),
        ["Navigation"] = new(9, 438, 623, 36),
    };
    internal sealed record Frame(string SelectedLevelName, IReadOnlyList<string> SelectedBriefingBody);
    private Frame _session = new(RetailFrontendWorldStrings.LevelName(100)!, RetailFrontendWorldStrings.Briefing(100));
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
    internal Vector2 HeaderOrigin => new(HeaderBarCenterX - MeasureFont22Text(MissionBriefingTitle, 1f) * .5f, HeaderTitleTop);
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
    internal static Color BodyTint => BriefingBodyText;
    internal static Color TextTint => ReleasedTitleText;
    internal static Color ArrowTint => BracketTint;
    internal string[] WrappedLines => Wrap(_session.SelectedBriefingBody);
    internal string[] Wrap(IReadOnlyList<string> paragraphs) => WrapBriefingParagraphs(paragraphs.Count > 0 ? paragraphs : BriefingBody).ToArray();
    internal (string Text, float Y, float Width, bool Drawn)[] Layout()
    {
        var rows = new List<(string, float, float, bool)>(); float y = BriefingBodyTop;
        foreach (string line in WrappedLines)
        {
            rows.Add((line, y, MeasureText(line, 1f), line.Length != 0));
            y += line.Length == 0 ? BriefingParagraphGap : BriefingBodyPitch;
        }
        return rows.ToArray();
    }
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
        _rockBackground = LegacyCuratedAyaTextureReference.Load("res://Assets/Frontend/Backgrounds/rock.texture.aya", 1024, 512, LegacyCuratedAyaTextureReference.Compression.Dxt1);
        _levelBracket02 = LegacyCuratedAyaTextureReference.Load("res://Assets/Frontend/level-bracket-02.texture.aya", 512, 512, LegacyCuratedAyaTextureReference.Compression.Dxt2);
        _feArrow = LegacyCuratedAyaTextureReference.Load("res://Assets/Frontend/fe-arrow.texture.aya", 64, 64, LegacyCuratedAyaTextureReference.Compression.Dxt2);
        _titleFont = LegacyCuratedAyaTextureReference.Load("res://Assets/Hud/font-13ps.texture.aya", 256, 256, LegacyCuratedAyaTextureReference.Compression.Rgba8);
        _font22 = LegacyCuratedAyaTextureReference.Load("res://Assets/Hud/font-22.texture.aya", 512, 512, LegacyCuratedAyaTextureReference.Compression.Rgba8);
        using Image body = _titleFont.GetImage(); using Image title = _font22.GetImage();
        _glyphWidths = MeasureGlyphWidths(body, GlyphCellSize, GlyphColumns);
        _font22Widths = MeasureGlyphWidths(title, Font22CellSize, Font22Columns);
        foreach (string section in Sections.Keys)
        {
            Control part = GetNode<Control>(section); part.Draw += () => DrawScenePart(part);
        }
        _initialized = true; Refresh();
    }
    internal void SetFrame(Frame frame) { _session = new(frame.SelectedLevelName, frame.SelectedBriefingBody.ToArray()); Refresh(); }
    public override void _Ready() { Initialize(); SetProcess(false); SetProcessInput(false); SetProcessUnhandledInput(false); }
    private void Refresh() { foreach (string section in Sections.Keys) GetNode<Control>(section).QueueRedraw(); }
    private void DrawScenePart(Control part)
    {
        if (!_initialized || part.Size.X <= 0f || part.Size.Y <= 0f) return;
        _paintingPart = part; _drawingSection = string.Empty;
        try { DrawSetTransform(Vector2.Zero, 0f, Vector2.One); DrawMissionBriefing(); }
        finally { _paintingPart = null; _drawingSection = string.Empty; }
    }
    private void SelectSceneSection(string section) => _drawingSection = section;
    private bool DrawsSceneSection => _paintingPart is not null && "Briefing." + _paintingPart.Name == _drawingSection;
    /// <summary>
    /// Retail MISSION BRIEFING, reached from SELECT LEVEL.
    ///
    /// The released source ships neither FEPBriefing.cpp nor its header (only
    /// the include in Frontend.h:14 and the CFEPBriefing member at
    /// Frontend.h:231), and there is no FEP_ page constant for it in any shipped
    /// header, so this page carries NO source geometry at all. Everything is
    /// measured from local-lab/retail-reference-pristine/mission-briefing/
    /// 05-mission-briefing-640x480.png.
    ///
    ///   header box       0x7f black over the scene, x191..584 y69..89 — the
    ///                    identical extent FEP_DEVSELECT and FEP_LEVEL_SELECT use
    ///   title            font22 scale 1, ink x288..490 y73..87, centred x=390
    ///   "1.00 - ..."     font22 sx 0.70 sy 1.00, ink x180..351 y126..145
    ///   body             Font13PS scale 1, ink left x=80/81, tops
    ///                    167,183,199,215,231,247 then 273,289
    ///   body colour      brightest ink (251,220,95)
    ///   chevrons         left x9..36 y438..473, right x604..631 y437..472
    ///
    /// KNOWN GAPS with their honest cause:
    ///   * The inset panel at x378..582 / y176..328 is NOT drawn and MUST NOT be
    ///     compared. Its interior is pure black in the reference only because
    ///     the capture ran with -skipfmv; that is the absence of retail's video,
    ///     not retail's drawn output. The frontend-regions file marks the region
    ///     EXCLUDED for the same reason.
    ///
    ///     MEASURED 2026-07-26, and the missing content is now identified.
    ///     Differencing the -skipfmv reference against the no-skipfmv control
    ///     (no-skipfmv-frontend/05n-mission-briefing-nofmv-b.png) shows 87.60%
    ///     of this page is pixel-identical between them; the ONLY substantial
    ///     difference is one rectangle, x380..580 y178..326, dark (mean
    ///     12,15,21) with the flag and a rendered scene (mean 119,126,145)
    ///     without it. That rectangle is 201 x 149. Every one of the 28 Bink
    ///     streams under data/video/briefings/ is 201x149, and the one named
    ///     PC_100_exact.vid — 396 frames at 25 fps — is Level 100's. So the
    ///     inset is a briefing video drawn at NATIVE 1:1 with no resampling, at
    ///     origin (380,177).
    ///
    ///     It stays undrawn: playing it needs a decode path and a clock policy
    ///     that do not exist yet, and drawing black "to match the reference"
    ///     would encode a -skipfmv artefact as product behaviour. Nothing on
    ///     this page is tinted to close the gap either.
    ///   * The metal header end-cap brackets and the top-left Forseti emblem are
    ///     the same unidentified art every other page lacks.
    /// </summary>
    private void DrawMissionBriefing()
    {
        SelectSceneSection("Briefing.Background");
        DrawBriefingStage();
        SelectSceneSection("Briefing.Header");
        DrawHeaderBarTitle(MissionBriefingTitle);

        SelectSceneSection("Briefing.LevelName");
        DrawFont22Text(
            _session.SelectedLevelName,
            new Vector2(BriefingLevelNameLeft, BriefingLevelNameTop),
            BriefingLevelNameScaleX,
            BriefingLevelNameScaleY,
            ReleasedTitleText);

        // The briefing body is the SELECTED world's own authored pair from
        // the language table (nine-slot pool law; worlds 611/612/621/622
        // carry a measured third paragraph). The static transcription below
        // stays only as the byte-identical world-100 receipt for the case
        // where no localization document is loaded; an empty session body
        // must draw NOTHING, never another world's copy.
        SelectSceneSection("Briefing.Body");
        IReadOnlyList<string> briefingBody =
            _session.SelectedBriefingBody.Count > 0
                ? _session.SelectedBriefingBody
                : BriefingBody;
        float y = BriefingBodyTop;
        foreach (string line in WrapBriefingParagraphs(briefingBody))
        {
            if (line.Length == 0)
            {
                y += BriefingParagraphGap;
                continue;
            }

            DrawText(line, new Vector2(BriefingBodyLeft, y), 1f, BriefingBodyText);
            y += BriefingBodyPitch;
        }

        SelectSceneSection("Briefing.Navigation");
        DrawPageChevrons();
    }

    /// <summary>
    /// Word-wraps the briefing paragraphs at the measured retail ink ceiling.
    ///
    /// The pristine capture's longest briefing line carries 286px of this
    /// renderer's advances (283px measured ink, within the known +2..+6
    /// overshoot), so 286 is the widest line retail drew. Greedy wrapping —
    /// keep adding words while the line fits, else break — is retained below.
    /// The old summary named a nonexistent RetailFrontendFlowWrapTests and
    /// claimed complete transcription equivalence. This oracle instead keeps
    /// the actual no-inserted-blank rule and tests it explicitly.
    /// </summary>
    private IReadOnlyList<string> WrapBriefingParagraphs(
        IReadOnlyList<string> paragraphs)
    {
        var lines = new List<string>();
        foreach (string paragraph in paragraphs)
        {
            if (paragraph.Length == 0)
            {
                lines.Add(string.Empty);
                continue;
            }

            string current = string.Empty;
            foreach (string word in paragraph.Split(' '))
            {
                string candidate = current.Length == 0
                    ? word
                    : current + " " + word;
                if (current.Length > 0 &&
                    MeasureText(candidate, 1f) > BriefingBodyInkCeiling)
                {
                    lines.Add(current);
                    current = word;
                }
                else
                {
                    current = candidate;
                }
            }

            if (current.Length > 0)
            {
                lines.Add(current);
            }
        }

        return lines;
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
    ///   * An earlier 9.4% difference was attributed to background animation.
    ///     The no-skipfmv control instead localised it to the live unit render,
    ///     with the same landscape behind both modes. That correction and the
    ///     original measurements are retained in Tests/ConfigurationReference.cs.
    ///     This shared stage retains the measured static origin and scale.
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
