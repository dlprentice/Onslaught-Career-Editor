// SPDX-License-Identifier: GPL-3.0-or-later

using System.Text.Json;
using Godot;
using OnslaughtRebuild.Client;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// The bounded released-style frontend path into the Level 100 opening slice.
/// It owns its page/input/loading lifecycle and exposes load, retry, and
/// Main Menu return seams to the existing gameplay host. Mission/HUD and audio
/// presentation remain separate owners.
/// </summary>
public sealed partial class RetailFrontendFlow : Control
{
    // Steam FE virtual stage (cluster hint from CFEPMain / click render).
    private const float DesignWidth = 640f;
    private const float DesignHeight = 480f;
    private const float MenuColumnX = 219f;
    private const float MenuStartY = 304f;
    private const float MenuPitch = 20f;
    private const float MenuHitHalfWidth = 120f;
    // mustbe_Font13PS.tga — 256² atlas, 16px cells, 16 columns, ASCII-32 origin.
    //
    // This is NOT mustbe_TitleFont.tga. TitleFont is a 256² / 32px / 8-column atlas
    // containing uppercase A–Z ONLY — no lowercase, no digits, no punctuation
    // (verified by decoding the DDS and rendering it). It cannot draw "New Game",
    // and it cannot draw "V1.00". Retail draws both, so TitleFont is not the menu
    // font. The previous ToUpperInvariant() call and the lowercase-folding in
    // GlyphIndex existed only to make that wrong atlas appear to work.
    //
    // The binary names three fonts: TitleFont.tga, Font13PS.tga ("small font") and
    // font22.512.tga, at 0x23e0d4 / 0x23e10c / 0x23e178. Font13PS carries the full
    // set including lowercase and the accented glyphs the five languages need
    // (Career.h: NUM_LANGUAGES 5), at the ~13px cap height retail's menu uses.
    private const int GlyphColumns = 16;
    private const int GlyphCellSize = 16;
    private const int FirstGlyph = 32;
    private const int GlyphSlotCount = 256;

    // mustbe_font22.512.tga — the third font the binary names (0x23e178), a
    // 512² atlas with 32px cells on the same 16-column / ASCII-32 grid.
    //
    // MEASURED, and it overturns an assumption this file has carried since the
    // main menu was built: the frontend HEADER TITLES are font22, not Font13PS.
    // Fitting both atlases against the pristine MISSION BRIEFING title band
    // (x280..500, y66..94) by normalised cross-correlation over a free
    // scale/offset sweep scores font22 0.951 at scale 1.00, origin (287,65),
    // against Font13PS 0.569 at its best fit (sx 1.43, sy 1.66). The font22 fit
    // also reproduces HEADER_BAR_X exactly: its advance width for
    // "MISSION BRIEFING" is 205, so origin 287 centres it on x = 389.5.
    //
    // The FEP_DEVSELECT and FEP_LEVEL_SELECT titles above are still drawn with
    // Font13PS at 1.5. They are NOT corrected here: both pages' captures are
    // pinned no-regression baselines for this change, so re-fonting them is a
    // separate, separately-verified edit. The same fit run against those two
    // pages is the way to settle it.
    private const int Font22Columns = 16;
    private const int Font22CellSize = 32;

    private static readonly Color ReleasedNormal = RetailColor(0xff4f4f4f);
    private static readonly Color ReleasedUnavailable = RetailColor(0x7f1f1f1f);
    private static readonly Color ReleasedSelected = RetailColor(0xffff6f3f);
    private static readonly Color ReleasedBlue = RetailColor(0xff1f4f7f);
    private static readonly Color TitleLogoTint = RetailColor(0xfeafcfff);
    private static readonly Color HighlightTint = RetailColor(0x7e000000);
    private static readonly Color BracketTint = RetailColor(0xfeffffff);
    private static readonly Color ChromeTint = RetailColor(0x3ecfffff);
    // Language-selector flag tint; see DrawLanguageSelector for the measurement.
    private static readonly Color FlagTint = RetailColor(0xff3f3f3f);
    private static readonly Color ClickSlideShadow = RetailColor(0x3f000000);
    private static readonly Color ShadowTint = RetailColor(0x3e000000);
    private static readonly Color VersionTint = RetailColor(0xff102025);
    // Settled additive gray: (((255*0x7f)>>8)*0x10101) → RGB 0x7e; keep α modest for Add blend.
    private static readonly Color GlowTint = new(0x7e / 255f, 0x7e / 255f, 0x7e / 255f, 0.5f);
    // Released overlay format string is "V%1d.%02d" at VA 0x00629454 in pristine
    // BEA.exe (sha256 74154bfa…), rendering "V1.00". The prior value here was
    // "V1.00 - PATCHED", transcribed from a reference capture taken on a safe copy
    // whose version_overlay_* patches repoint the format pointer at 0x0046416f to a
    // code cave at VA 0x005AA444 holding "V%1d.%02d - PATCHED". That suffix is an
    // artifact of the patched capture, not released behavior.
    private const string VersionText = "V1.00";

    // FEP_DEVSELECT ("CHOOSE GAME NAME"). See DrawDevSelect for the measurement
    // method; every literal below is either a measured extent from the pristine
    // 640x480 capture or a constant lifted from references/Onslaught/FrontEnd.cpp.
    private const string DevSelectTitle = "CHOOSE GAME NAME";
    // Retail's title occupies x263..513 (251px wide) and y73..88 (16px tall) for
    // 16 glyphs. Font13PS at scale 1 rendered 256px wide but only 10px tall in
    // the first capture of this page, so the page is NOT tracked-out small text:
    // it is the same atlas at ~1.5x, which lands 249px wide and 15px tall.
    // The header title is drawn in font22 at scale 1 on this page as on every
    // other header page; see DrawDevSelect for the glyph-run measurement that
    // replaced the previous Font13PS-at-1.5 reading. HeaderBarCenterX /
    // HeaderTitleTop now carry the placement, so no page-local title constants
    // remain.
    // Rows and the name field are drawn larger than the 20px-pitch main menu:
    // retail's row pitch here is 24 and its glyph bodies are ~14px tall. The
    // first capture measured our "BEA 1" at 53x12 against retail's 69x17, i.e.
    // 1.30-1.42x too small at scale 1.25.
    private const float DevSelectRowScale = 1.4f;
    private const float DevSelectRowPitch = 24f;
    private const float DevSelectRowX = 132f;
    private const float DevSelectRowTop = 137f;
    private const float DevSelectNameTop = 417f;

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

    // MISSION BRIEFING / SELECT CONFIGURATION. Every literal in this block is
    // measured from the two pristine 640x480 captures taken 2026-07-25:
    //   local-lab/retail-reference-pristine/mission-briefing/05-mission-briefing-640x480.png
    //   local-lab/retail-reference-pristine/select-configuration/06-select-configuration-640x480.png
    // See DrawMissionBriefing / DrawSelectConfiguration for the method per element.
    private const string MissionBriefingTitle = "MISSION BRIEFING";
    private const string SelectConfigurationTitle = "SELECT CONFIGURATION";
    private const string ConfigurationUnitName = "BE:A Unit-00 'Prototype'";
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
    // Retail's blank line does NOT advance a full 16: measured ink tops run
    // 167,183,199,215,231,247 then 273,289, so the paragraph break adds 10 on
    // top of the line the last paragraph line already advanced (247+16+10=273).
    private const float BriefingParagraphGap = 10f;
    private const float ConfigurationUnitLeft = 260.5f;
    private const float ConfigurationUnitTop = 99.5f;
    private const float ConfigurationRowLeft = 280f;
    private const float ConfigurationRowPitch = 16f;
    private const float ConfigurationWalkerTop = 210f;
    private const float ConfigurationJetTop = 274f;
    // The rock background quad and the big ring, both fitted — see DrawBriefingStage.
    private const float BriefingBackgroundScale = 1.25f;
    private const float BriefingBackgroundLeft = -70f;
    private const float BriefingBackgroundTop = -80f;
    private const float BriefingRingSize = 990f;
    private const float BriefingRingCenterX = 267f;
    private const float BriefingRingCenterY = 221f;
    // Loading page. Bar extents and text origin measured from
    // local-lab/retail-reference-pristine/loading/07-loading-640x480.png.
    private const float LoadingTextLeft = 270f;
    private const float LoadingTextTop = 393.5f;
    private const float LoadingBarLeft = 78f;
    private const float LoadingBarTop = 423f;
    private const float LoadingBarWidth = 485f;
    private const float LoadingBarHeight = 25f;

    /// <summary>
    /// The briefing body, transcribed from the pristine capture. There is no
    /// resolved string id for it in the materialized table, so this is the one
    /// literal block on the page that is not localization-backed — the same
    /// position "Episode 1" is in on FEP_LEVEL_SELECT.
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

    /// <summary>Per-mode weapon rows: label and whether it heads a mode block.</summary>
    private static readonly (string Text, bool IsModeHeader)[] ConfigurationWalkerRows =
    [
        ("Walker Mode", true), ("Pulse Cannon", false), ("Vulcan Cannon", false),
    ];

    private static readonly (string Text, bool IsModeHeader)[] ConfigurationJetRows =
    [
        ("Jet Mode", true), ("Vulcan Cannon", false), ("Micro Missiles", false),
    ];

    private static readonly Color ReleasedTitleText = RetailColor(0xff7f7f7f);
    // Briefing body ink measures (251,220,95) at its brightest; this modulate
    // renders (252,222,95).
    private static readonly Color BriefingBodyText = RetailColor(0xff7e6f30);
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
    private static readonly Color DevSelectRowText = RetailColor(0xff404040);
    private static readonly Color DevSelectNameHighlight = RetailColor(0xff004050);
    // Panel fills and hairlines are measured framebuffer colours, not modulated
    // sprite tints, so they are stated literally.
    private static readonly Color DevSelectPanelFill = new(9f / 255f, 9f / 255f, 18f / 255f, 1f);
    private static readonly Color DevSelectPanelBorder = new(130f / 255f, 132f / 255f, 139f / 255f, 1f);
    private static readonly Color DevSelectFieldBorder = new(159f / 255f, 162f / 255f, 165f / 255f, 1f);
    private static readonly Color DevSelectScrollDivider = new(127f / 255f, 129f / 255f, 132f / 255f, 1f);
    private static readonly Color DevSelectScrollThumb = new(245f / 255f, 249f / 255f, 245f / 255f, 1f);
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
    // The guide line survives BEHIND the list panel: retail's y=180 row inside the
    // panel measures (19,19,27) rather than the (9,9,18) panel fill, which is the
    // guide colour attenuated by the panel's own alpha. Stating the measured
    // composite avoids depending on blend rounding to reproduce it.
    private static readonly Color DevSelectGuideOverPanel = new(19f / 255f, 19f / 255f, 27f / 255f, 1f);
    // FrontEnd.cpp:1128 draws FET3_HEADER_TEXT_BOX with col = 0x7f000000, and the
    // measured header interior is (12,12,24) — exactly that alpha over the
    // (23,23,48) page background. Drawn as the measured composite because an
    // alpha 0x7f fill lands on (11,11,24) after this renderer's blend rounding.
    private static readonly Color HeaderBoxTint = new(12f / 255f, 12f / 255f, 24f / 255f, 1f);
    private const float ShadowScaleBoost = 1.05f;
    // Materialized decode of data/video/FEBack128.vid (128² BIKi → rgb24).
    //
    // KNOWN DEFECT: the released file is 572 frames at 30 fps (Bink header, frames
    // at +8, fps dividend/divider at +28/+32). The materialized strip is 286 frames
    // and this declares 15 fps - exactly half of each, so every second frame is
    // dropped. Duration is preserved (19.1s) but the animation is half as smooth as
    // released. It does not currently show, because the main-menu underlay was
    // measured to be a flat fill and this is not drawn there; it will matter
    // wherever FEBack128 is actually used, which is still unresolved.
    // See local-lab/INTRO-FMV-FINDINGS-2026-07-25.md.
    private const string FeBackStripPath =
        "res://Assets/Frontend/Backgrounds/fe-back-128x128x15.rgb";
    private const int FeBackWidth = 128;
    private const int FeBackHeight = 128;
    private const int FeBackFps = 15;
    private const int FeBackFrameBytes = FeBackWidth * FeBackHeight * 3;
    // Fallback only when the strip is missing (materialize not run).
    private static readonly Color MainUnderlayFallback = new(23f / 255f, 23f / 255f, 48f / 255f, 1f);

    private readonly RetailFrontendSession _session = new();
    private readonly Dictionary<RetailFrontendMenuItemKind, string> _menuText = [];

    private Texture2D _clickBackground = null!;
    private Texture2D _clickSlide = null!;
    private Texture2D _rockBackground = null!;
    private Texture2D[] _feBackFrames = [];
    private Texture2D _forsetiWritingLarge = null!;
    private Texture2D _reflectionMap = null!;
    private Texture2D _titleLogo = null!;
    private Texture2D _titleBracket01 = null!;
    private Texture2D _titleBracket02 = null!;
    private Texture2D _titleTextBox = null!;
    private Texture2D _symbolBracket01 = null!;
    private Texture2D _symbolBracket02 = null!;
    private Texture2D _levelBracket01 = null!;
    private Texture2D _levelBracket02 = null!;
    private Texture2D _levelRing01 = null!;
    private Texture2D _levelRing02 = null!;
    private Texture2D _loadingScreen = null!;
    private Texture2D _titleFont = null!;
    private Texture2D _font22 = null!;
    private int[] _font22Widths = [];
    private Texture2D[] _languageFlags = [];
    private Texture2D _feArrow = null!;
    private Texture2D[] _menuIcons = [];
    private int[] _glyphWidths = [];
    private CanvasItemMaterial? _additiveMaterial;
    private string _selectLevelText = string.Empty;
    private string _level100Text = string.Empty;
    private string _loadingText = string.Empty;
    // Localization__GetStringById(0xe4) — English table in BEA.exe, not english.dat.
    private const string QuitConfirmPrompt = "Are you sure you want to quit the game?";
    private double _animationSeconds;
    private double _clickPulseTimer;
    private double _clickPageSeconds;
    private RetailFrontendScreen _lastDrawnScreen = RetailFrontendScreen.ClickToStart;
    private int _loadingFrames;
    private bool _initialized;
    private bool _loadRequestRaised;
    private bool _level100Ready;
    private bool _gameplayActivationRaised;

    public event Action? Level100LoadRequested;

    public event Action? GameplayActivated;

    public event Action? GameplaySuspended;

    public event Action? ReturnToMainMenuRequested;

    public event Action<RetailFrontendAudioCue>? AudioCueRequested;

    public event Action<RetailFrontendCursorMode>? CursorModeRequested;

    internal RetailFrontendScreen CurrentScreen => _session.Screen;

    public void Initialize()
    {
        if (_initialized)
        {
            throw new InvalidOperationException("The retail frontend is already initialized.");
        }

        LoadLocalization();
        LoadTextures();
        _feBackFrames = LoadFeBackFrames();
        _glyphWidths = MeasureGlyphWidths(_titleFont.GetImage(), GlyphCellSize, GlyphColumns);
        _font22Widths = MeasureGlyphWidths(_font22.GetImage(), Font22CellSize, Font22Columns);

        _initialized = true;
    }

    public void MarkLevel100Ready()
    {
        if (!_loadRequestRaised || _session.Screen != RetailFrontendScreen.Loading)
        {
            throw new InvalidOperationException(
                "Level 100 was marked ready outside the frontend loading seam.");
        }

        _level100Ready = true;
    }

    public void RestartLevel100()
    {
        RetailFrontendScreen origin = _session.Screen;
        RetailFrontendSignal signal = _session.RestartLevel100();
        ResumeFrontendForNavigation(origin);
        HandleNavigationSignal(signal);
        QueueRedraw();
    }

    public void LeaveLevel100ForMainMenu()
    {
        RetailFrontendScreen origin = _session.Screen;
        RetailFrontendSignal signal = _session.LeaveLevel100ForMainMenu();
        ResumeFrontendForNavigation(origin);
        HandleNavigationSignal(signal);
        QueueRedraw();
    }

    internal void ConfirmForSmoke()
    {
        Confirm();
    }

    /// <summary>
    /// Hides and freezes the frontend while retail's cold-start media owns the
    /// screen.
    ///
    /// This is not cosmetic. <see cref="_clickPulseTimer"/> and
    /// <see cref="_clickPageSeconds"/> accumulate in <c>_Process</c> whenever
    /// the session is on click-to-start, and the released splash pulse is
    /// <c>((cos(t*pi)+1)*0.375)+0.46875</c> — a function of that timer. Letting
    /// it run for the ~93 s the intro lasts would put the pulse at an arbitrary
    /// phase on the first frame the player actually sees, where retail's starts
    /// from zero because the page has only just been created.
    /// </summary>
    public void SuspendForStartupMedia()
    {
        Visible = false;
        SetProcess(false);
        SetProcessInput(false);
    }

    /// <summary>
    /// Hands the screen back after the cold-start media finishes or is skipped.
    /// The click-to-start timers are reset so the page begins from zero exactly
    /// as it does when the frontend is created cold.
    /// </summary>
    public void ResumeAfterStartupMedia()
    {
        _animationSeconds = 0d;
        _clickPulseTimer = 0d;
        _clickPageSeconds = 0d;
        Visible = true;
        SetProcess(true);
        SetProcessInput(true);
        QueueRedraw();
    }

    public override void _Ready()
    {
        if (!_initialized)
        {
            throw new InvalidOperationException("Initialize the retail frontend before adding it to the tree.");
        }

        AnchorRight = 1f;
        AnchorBottom = 1f;
        MouseFilter = MouseFilterEnum.Ignore;
        ZIndex = 100;
        QueueRedraw();
    }

    public override void _Process(double delta)
    {
        double step = Math.Max(0d, delta);
        _animationSeconds += step;
        if (_session.Screen == RetailFrontendScreen.ClickToStart)
        {
            if (_lastDrawnScreen != RetailFrontendScreen.ClickToStart)
            {
                _clickPulseTimer = 0d;
                _clickPageSeconds = 0d;
            }

            // Retail Process accumulates roughly 2 * frameΔ into this+0x18.
            _clickPulseTimer += 2d * step;
            _clickPageSeconds += step;
        }

        _lastDrawnScreen = _session.Screen;

        if (_session.Screen == RetailFrontendScreen.Loading)
        {
            _loadingFrames++;
            if (!_loadRequestRaised && _loadingFrames >= 2)
            {
                if (!_session.ConsumeLevel100LaunchRequest())
                {
                    throw new InvalidOperationException("The Level 100 launch edge was lost.");
                }

                _loadRequestRaised = true;
                Level100LoadRequested?.Invoke();
            }

            if (_level100Ready)
            {
                _session.CompleteLevel100Load();
            }
        }

        if (_session.Screen == RetailFrontendScreen.Gameplay && !_gameplayActivationRaised)
        {
            _gameplayActivationRaised = true;
            Visible = false;
            SetProcessInput(false);
            SetProcess(false);
            CursorModeRequested?.Invoke(RetailFrontendCursorMode.Captured);
            GameplayActivated?.Invoke();
            return;
        }

        QueueRedraw();
    }

    public override void _Input(InputEvent inputEvent)
    {
        if (_session.Screen is RetailFrontendScreen.Loading or RetailFrontendScreen.Gameplay)
        {
            return;
        }

        bool handled = inputEvent switch
        {
            InputEventMouseMotion motion => HandlePointerMotion(motion.Position),
            InputEventMouseButton button when
                button.Pressed && button.ButtonIndex == MouseButton.Left =>
                HandlePointerConfirm(button.Position),
            InputEventKey key when key.Pressed && !key.Echo => HandleKey(key),
            _ => false,
        };

        if (handled)
        {
            GetViewport().SetInputAsHandled();
        }
    }

    public override void _Draw()
    {
        // Letterbox outside the 640-class stage; no invented navy FE clear.
        DrawRect(new Rect2(Vector2.Zero, Size), Colors.Black);
        (float scale, Vector2 offset) = DesignTransform();
        DrawSetTransform(offset, 0f, new Vector2(scale, scale));

        switch (_session.Screen)
        {
            case RetailFrontendScreen.ClickToStart:
                DrawClickToStart();
                break;
            case RetailFrontendScreen.MainMenu:
                DrawMainMenu();
                break;
            case RetailFrontendScreen.QuitConfirm:
                DrawMainMenu();
                DrawQuitConfirm();
                break;
            case RetailFrontendScreen.DevSelect:
                DrawDevSelect();
                break;
            case RetailFrontendScreen.LevelSelect:
                DrawLevelSelect();
                break;
            case RetailFrontendScreen.MissionBriefing:
                DrawMissionBriefing();
                break;
            case RetailFrontendScreen.SelectConfiguration:
                DrawSelectConfiguration();
                break;
            case RetailFrontendScreen.Loading:
                DrawLoading();
                break;
        }

        DrawSetTransform(Vector2.Zero, 0f, Vector2.One);
    }

    private void DrawClickToStart()
    {
        // FUN_0051b840 splash pulse — DAT_0089d880 / fe_splash1.
        float t = Mathf.Min((float)_clickPulseTimer, 1f);
        float splashScale = ((Mathf.Cos(t * Mathf.Pi) + 1f) * 0.375f) + 0.46875f;
        // Call-site x/y are center anchors at settled scale ≈ (320, 240).
        float splashX = (558f - (splashScale * 238f)) - 126.4375f;
        float splashY = 135.9375f + (222f * splashScale);
        DrawSurfaceCentered(
            _clickBackground,
            splashX,
            splashY,
            splashScale,
            splashScale,
            Colors.White);

        // Prompt after timer > 4. Blink duty cycle is stubbed (retail FPU thunk WAIT).
        if (_clickPulseTimer > 4d && (Mathf.PosMod((float)_clickPulseTimer, 2f) < 1.6f))
        {
            // Mixed case, per the pristine 640x480 capture of the click-to-start
            // screen (local-lab/retail-reference-pristine/click-to-start-640x480.png).
            const string prompt = "Click to start"; // Localization 0x77
            const float textScale = 2f;
            float width = MeasureText(prompt, textScale);
            var origin = new Vector2(320f - (width * 0.5f), 400f);
            // Retail: four ±1 black outline passes + white body (no extra drop-shadow).
            DrawTextFlat(prompt, origin + new Vector2(-1f, 1f), textScale, Colors.Black);
            DrawTextFlat(prompt, origin + new Vector2(1f, 1f), textScale, Colors.Black);
            DrawTextFlat(prompt, origin + new Vector2(-1f, -1f), textScale, Colors.Black);
            DrawTextFlat(prompt, origin + new Vector2(1f, -1f), textScale, Colors.Black);
            DrawTextFlat(prompt, origin, textScale, Colors.White);
        }

        // DAT_0089d7bc LostToys sliding pair after prompt gate.
        if (_clickPulseTimer > 4d)
        {
            float fade = Mathf.Clamp((float)_clickPulseTimer - 4f, 0f, 1f);
            float off = (1f - fade) * (1f - fade) * 400f;
            // Call sites use mode 0 (top-left style) at these XY with sx=sy=1.
            DrawTextureRect(
                _clickSlide,
                new Rect2(124f - off, -6f, _clickSlide.GetWidth(), _clickSlide.GetHeight()),
                false,
                ClickSlideShadow);
            DrawTextureRect(
                _clickSlide,
                new Rect2(120f - off, -10f, _clickSlide.GetWidth(), _clickSlide.GetHeight()),
                false,
                Colors.White);
        }

        // Title micro-pulse near (250,290) after ~2s (simplified vs multi-pass retail).
        if (_clickPageSeconds * 1.2d > 2d)
        {
            float logoPulse = 0.55f + (0.45f * (0.5f + (0.5f * Mathf.Sin((float)_clickPageSeconds * 3f))));
            DrawSurfaceCentered(
                _titleLogo,
                250f,
                290f,
                0.35f,
                0.35f,
                new Color(TitleLogoTint.R, TitleLogoTint.G, TitleLogoTint.B, logoPulse));
        }
    }

    private void DrawMainMenu()
    {
        DrawMainUnderlay();

        // DAT_0089d7f0 Forseti writing chrome — three settled tiles (Y thunk ≈ 175).
        DrawSurfaceCentered(_forsetiWritingLarge, 458f, 175f, 1f, 1f, ChromeTint);
        DrawSurfaceCentered(_forsetiWritingLarge, 458f, 175f + 350f, 1f, 1f, ChromeTint);
        DrawSurfaceCentered(_forsetiWritingLarge, 458f, 175f + 700f, 1f, 1f, ChromeTint);

        DrawLanguageSelector();

        for (int index = 0; index < _session.Items.Count; index++)
        {
            RetailFrontendMenuItem item = _session.Items[index];
            float rowY = MenuStartY + (index * MenuPitch);
            bool selected = index == _session.SelectedMainIndex;
            // Draw the string as authored. english.json holds "Continue Game" /
            // "Load Game" in mixed case and retail renders them that way.
            // Font13PS cells are 16px, so scale 1.0 gives the retail 20px pitch.
            string label = _menuText[item.Kind];
            const float textScale = 1f;
            float textWidth = MeasureText(label, textScale);
            var textPos = new Vector2(MenuColumnX - (textWidth * 0.5f), rowY - 8f);

            if (selected)
            {
                // Highlight box width MEASURED from the pristine 640x480 capture:
                // the selected row's box spans x 166..272, w = 107. The previous
                // Mathf.Max(160f, ...) floor forced 160 and made the box 39px too
                // wide. Retail sizes it to the label plus a fixed padding.
                float boxWidth = textWidth + 22f;
                DrawTextureRect(
                    _titleTextBox,
                    new Rect2(MenuColumnX - (boxWidth * 0.5f), rowY - 10f, boxWidth, 20f),
                    false,
                    HighlightTint);
            }

            Color textColor = selected
                ? ReleasedSelected
                : item.IsAvailable ? ReleasedNormal : ReleasedUnavailable;
            DrawText(label, textPos, textScale, textColor);
        }

        // Shadows (offset bases; GetShadowOffset* ≈ 0 settled), then bodies.
        const float bracketScale = 1.25f;
        float bracketShadowScale = bracketScale * ShadowScaleBoost;
        DrawSurfaceCentered(_titleBracket01, 224f, 349f, bracketShadowScale, bracketShadowScale, ShadowTint);
        DrawSurfaceCentered(_titleBracket01, 219f, 344f, bracketScale, bracketScale, BracketTint);
        DrawSurfaceCentered(_symbolBracket01, 462f, 365f, bracketShadowScale, bracketShadowScale, ShadowTint);
        DrawSurfaceCentered(_symbolBracket01, 457f, 355f, bracketScale, bracketScale, BracketTint);

        Texture2D icon = _menuIcons[_session.SelectedMainIndex];
        Color iconTint = _session.SelectedMainItem.IsAvailable ? BracketTint : ReleasedUnavailable;
        DrawSurfaceCentered(icon, 462f, 365f, ShadowScaleBoost, ShadowScaleBoost, ShadowTint);
        DrawSurfaceCentered(icon, 457f, 355f, 1f, 1f, iconTint);

        DrawTextFlat(VersionText, new Vector2(0f, DesignHeight - 16f), 1f, VersionTint);

        // DAT_0089d7fc reflection streaks — retail additive over the stage.
        // Draw before the logo so a failed additive fallback cannot bury Title2.
        // x ≈ (256 - FpuThunk()) + 65 with thunk≈0.
        const float glowX0 = 256f + 65f;
        DrawAdditiveSurfaceCentered(_reflectionMap, glowX0, 120f, 1f, 2f, GlowTint);
        DrawAdditiveSurfaceCentered(_reflectionMap, glowX0 + 512f, 120f, 1f, 2f, GlowTint);

        DrawSurfaceCentered(_titleLogo, 325f, 140f, ShadowScaleBoost, ShadowScaleBoost, ShadowTint);
        DrawSurfaceCentered(_titleLogo, 320f, 130f, 1f, 1f, TitleLogoTint);
    }

    /// <summary>
    /// The language selector sitting directly above the menu column.
    ///
    /// Geometry MEASURED from the pristine 640x480 retail main-menu capture
    /// (local-lab/retail-reference-pristine/main-menu-640x480.png) by finding the
    /// pixels in the band above the first menu row that differ from the flat
    /// (23,23,48) background:
    ///   left chevron  x 144..165 (w 22), y 254..283 (h 30)
    ///   flag          x 177..261 (w 85), y 252..284 (h 33)
    ///   right chevron x 273..294 (w 22), y 253..282 (h 30)
    /// The content is symmetric about x = 219.0, which independently confirms
    /// MenuColumnX as a centre anchor rather than a left edge.
    /// </summary>
    private void DrawLanguageSelector()
    {
        if (_languageFlags.Length == 0)
        {
            return;
        }

        int language = (int)_session.Language;
        if (language < 0 || language >= _languageFlags.Length)
        {
            language = 0;
        }

        // Retail draws the flag dimmed, not at full brightness. Its brightest
        // rendered texel is (125,125,125) where the source texture is white, and
        // 0x3f is exactly 125 under the 2x modulate ((0x3f*255)>>7). Measured mean
        // ratio across the flag rect is 0.473/0.476/0.486 - uniform, i.e. a grey
        // tint rather than a per-channel correction.
        DrawTextureRect(
            _languageFlags[language],
            new Rect2(177f, 252f, 85f, 33f),
            false,
            FlagTint);

        // FE_Arrow points RIGHT, and its artwork occupies only (16,12)-(46,52) of
        // the 64x64 texture (measured from the decoded DDS alpha bbox). Drawing the
        // whole texture would shrink the visible chevron by the margins, so source
        // the content region explicitly. Retail's LEFT chevron is the mirrored one.
        var arrowSource = new Rect2(16f, 12f, 30f, 40f);
        DrawTextureRectRegion(_feArrow, new Rect2(166f, 254f, -22f, 30f), arrowSource, ChromeTint);
        DrawTextureRectRegion(_feArrow, new Rect2(273f, 253f, 22f, 30f), arrowSource, ChromeTint);
    }

    private void DrawMainUnderlay()
    {
        // MEASURED, not inferred: the released main menu draws a FLAT background.
        //
        // In captures/08-main-retail.png (640x480 retail), 67 of 192 40x40 tiles are
        // perfectly flat (population sd < 0.5), including large areas mid-left and
        // mid-right where no UI is drawn. Two disjoint 120x120 background regions
        // measure exactly (23,23,48) with ONE distinct colour and sd 0.0, and two
        // independently captured retail main-menu frames are bit-identical there.
        //
        // A 128² video stretched across the stage cannot produce that. Upscaling
        // yields gradients in every tile, and any non-zero modulate of a textured
        // source leaves variance behind. Zero variance across 14,400 pixels means no
        // video contribution is visible on this screen.
        //
        // Contrast the click-to-start frame, which IS textured (sd ~27-40, 60,821
        // distinct colours) with flat pillarbox bars left and right — consistent
        // with the centred 480² splash that extents.json records.
        //
        // So FEBack128 is not the visible main-menu underlay. Its actual role is
        // unresolved and the decoded strip is retained (it materializes to exactly
        // 128*128*3*286 bytes, so the decode itself is sound). See
        // local-lab/PARITY-FINDINGS-2026-07-25.md finding 5.
        //
        // ================= 2026-07-26: THE ARGUMENT ABOVE DOES NOT HOLD =========
        //
        // Every capture that argument rests on was taken with -skipfmv, and the
        // same argument applied to a page now PROVEN to carry a video underlay
        // reproduces it exactly. On FEP_LEVEL_SELECT, the -skipfmv reference's
        // underlay is flat (23,23,48) with standard deviation 0.06/0.08/0.06 over
        // 229,803 pixels — the same "zero variance, so no video" signature — while
        // the no-skipfmv control of that same page carries a swirling field at
        // mean (32.2,34.3,65.8), sd 3.18/4.36/7.45.
        //
        // And that field IS FEBack128. Admitting only the pixels the -skipfmv
        // capture proves are pure underlay (exactly (23,23,48) within 1; a
        // geometric mask, not a rectangle) and scoring every decoded strip frame
        // upscaled 128² -> 640x480 by normalised cross-correlation peaks at
        // frame 115, ncc +0.8190, with a coherent shoulder (113..117 all >= 0.747)
        // against a distribution of mean +0.4163 / sd 0.2204 running down to
        // -0.0885. A per-channel fit against that frame gives gain 0.2198/0.2209/
        // 0.2225 over offsets 24.53/24.78/49.35 — i.e. the flat fill plus ~0.22x
        // the video frame — with residual mad 1.07/1.33/2.23.
        //
        // What that does NOT establish: whether the MAIN MENU carries it. There is
        // no no-skipfmv main-menu capture in the reference set, so this page's
        // underlay is neither confirmed nor refuted, only left unproven by a
        // method that cannot decide it. One main-menu frame captured without
        // -skipfmv, run through the same mask, settles it.
        //
        // The flat fill therefore stays: it is faithful to the only reference that
        // exists, and drawing FEBack128 here on the strength of another page would
        // be speculation. _feBackFrames is loaded and deliberately not drawn.
        // See local-lab/CROSS-MODEL-STARTUP-PARITY-2026-07-26.md.
        DrawRect(new Rect2(0f, 0f, DesignWidth, DesignHeight), MainUnderlayFallback);
    }

    private void DrawQuitConfirm()
    {
        // Reconstruction messbox chrome (Steam FEMessBox layout not fully ported).
        DrawRect(new Rect2(70f, 160f, 500f, 140f), new Color(0f, 0f, 0f, 0.82f));
        DrawTextCentered(QuitConfirmPrompt, new Vector2(320f, 190f), 1.7f, Colors.White);

        DrawQuitConfirmChoice("No", 220f, _session.SelectedQuitConfirmIndex == 0);
        DrawQuitConfirmChoice("Yes", 420f, _session.SelectedQuitConfirmIndex == 1);
    }

    private void DrawQuitConfirmChoice(string label, float centerX, bool selected)
    {
        Color color = selected ? ReleasedSelected : ReleasedNormal;
        if (selected)
        {
            float width = Mathf.Max(72f, MeasureText(label, 1f) + 20f);
            DrawTextureRect(
                _titleTextBox,
                new Rect2(centerX - (width * 0.5f), 248f, width, 20f),
                false,
                HighlightTint);
        }

        DrawTextCentered(label, new Vector2(centerX, 250f), 2f, color);
    }

    /// <summary>
    /// Retail FEP_DEVSELECT — the "CHOOSE GAME NAME" page reached from New Game.
    ///
    /// Implemented visually and sequentially only; this lane carries no save or
    /// career persistence, so the career list is structurally present and empty.
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
    /// references/Onslaught/FrontEnd.cpp:1128, and the title is drawn centred on
    /// HEADER_BAR_X = 390 (FrontEnd.cpp:1101) in 0xff7f7f7f (FrontEnd.cpp:1207).
    ///
    /// KNOWN GAPS, stated rather than faked: the metal header end-cap brackets
    /// (FET3_HEADER_BRACKET1, retail x182..190 and x585..598) and the blue
    /// Forseti emblem at top-left are drawn from textures this lane has not
    /// identified or materialized, so they are not drawn at all here.
    /// </summary>
    private void DrawDevSelect()
    {
        DrawMainUnderlay();

        // Faint crosshair guides, present on this page and on the retail main
        // menu; the reconstruction has not drawn them anywhere before now.
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
        DrawRect(new Rect2(191f, 69f, 394f, 21f), HeaderBoxTint);
        float titleWidth = MeasureFont22Text(DevSelectTitle, 1f);
        DrawFont22Text(
            DevSelectTitle,
            new Vector2(HeaderBarCenterX - (titleWidth * 0.5f), HeaderTitleTop),
            1f,
            1f,
            ReleasedTitleText);

        // List panel: border, interior, scrollbar divider and thumb.
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
        DrawRect(new Rect2(128f, 408f, 403f, 44f), DevSelectFieldBorder);
        DrawRect(new Rect2(129f, 409f, 401f, 42f), DevSelectPanelFill);

        float nameWidth = MeasureText(_session.GameName, DevSelectRowScale);
        var nameOrigin = new Vector2(329.5f - (nameWidth * 0.5f), DevSelectNameTop);
        DrawRect(
            new Rect2(nameOrigin.X - 4f, 415f, nameWidth + 8f, 31f),
            DevSelectNameHighlight);
        DrawText(_session.GameName, nameOrigin, DevSelectRowScale, ReleasedTitleText);

        // Page chevrons. FE_Arrow points right and its artwork occupies only
        // (16,12)-(46,52) of the 64x64 texture, exactly as DrawLanguageSelector
        // measured; the left chevron is the mirrored draw.
        // Measured extents: right chevron x604..631 y437..472, left chevron the
        // mirrored pair six rows lower; both render in the same lit metal as the
        // arcs (~(107,117,131)), not the faint ChromeTint the language selector uses.
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
    ///                        exactly as HEADER_BAR_X (FrontEnd.cpp:1101) requires
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
        DrawMainUnderlay();

        DrawRect(new Rect2(123f, 0f, 1f, DesignHeight), DevSelectGuide);
        DrawRect(new Rect2(0f, 180f, DesignWidth, 1f), DevSelectGuide);

        DrawLevelSweepArcs();
        DrawLevelNodeGraph();

        for (int index = 0; index < LevelColumnLabels.Length; index++)
        {
            (string text, float x) = LevelColumnLabels[index];
            DrawText(
                text,
                new Vector2(x, LevelSelectColumnLabelTop),
                LevelSelectColumnLabelScale,
                ReleasedBlue);
        }

        // FrontEnd.cpp:891-892 — FET3_SELECT_BRACKET1 at SELECT_BRACKET_X/Y
        // (328,343) with SELECT_BRACKET_SCALE 1.25, plus its +5/+10 shadow at
        // scale*1.05 in 0x3F000000. FEP_LEVEL_SELECT is one of the pages
        // got_standard_SlidingTextBordersAndMask() returns TRUE for
        // (FrontEnd.cpp:783), which pins transition to 1 and therefore this
        // settled scale; the outside bracket only draws while dest == FEP_MAIN.
        //
        // MEASURED, and this page does NOT reproduce the 1.4 the FEP_DEVSELECT
        // build settled on: fitting the FE_select_level_bracket01 alpha mask over
        // 4,000 sampled retail metal pixels (header band, emblem, and chevrons
        // excluded) peaks at 96.1% overlap at scale 1.25, centre (329,343), and
        // the whole 1.10-1.74 scale sweep has its maximum there. Scale 1.4 is not
        // a local optimum on this frame. The source constants are therefore used
        // verbatim. The shadow reproduces exactly: 0x3f000000 over (23,23,48) is
        // (17,17,36), which is the third most common colour in the capture.
        const float bracketScale = 1.25f;
        const float bracketShadowScale = bracketScale * ShadowScaleBoost;
        DrawSurfaceCentered(_levelBracket01, 333f, 353f, bracketShadowScale, bracketShadowScale, ShadowTint);
        DrawSurfaceCentered(_levelBracket01, 328f, 343f, bracketScale, bracketScale, BracketTint);

        // font22 at scale 1, for the glyph-run and per-letter-IoU evidence
        // written out in DrawDevSelect. Retail's ink here is x304..471, y72..88,
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
        DrawText(
            _level100Text,
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
        DrawBriefingStage();
        DrawHeaderBarTitle(MissionBriefingTitle);

        DrawFont22Text(
            _level100Text,
            new Vector2(BriefingLevelNameLeft, BriefingLevelNameTop),
            BriefingLevelNameScaleX,
            BriefingLevelNameScaleY,
            ReleasedTitleText);

        float y = BriefingBodyTop;
        foreach (string line in BriefingBody)
        {
            if (line.Length == 0)
            {
                y += BriefingParagraphGap;
                continue;
            }

            DrawText(line, new Vector2(BriefingBodyLeft, y), 1f, BriefingBodyText);
            y += BriefingBodyPitch;
        }

        DrawPageChevrons();
    }

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
        DrawBriefingStage();
        DrawHeaderBarTitle(SelectConfigurationTitle);

        DrawFont22Text(
            ConfigurationUnitName,
            new Vector2(ConfigurationUnitLeft, ConfigurationUnitTop),
            1f,
            1f,
            ReleasedTitleText);

        DrawConfigurationRows(ConfigurationWalkerRows, ConfigurationWalkerTop);
        DrawConfigurationRows(ConfigurationJetRows, ConfigurationJetTop);

        DrawPageChevrons();
    }

    private void DrawConfigurationRows((string Text, bool IsModeHeader)[] rows, float top)
    {
        for (int index = 0; index < rows.Length; index++)
        {
            (string text, bool isModeHeader) = rows[index];
            DrawText(
                text,
                new Vector2(ConfigurationRowLeft, top + (index * ConfigurationRowPitch)),
                1f,
                isModeHeader ? ConfigurationModeText : ReleasedTitleText);
        }
    }

    /// <summary>
    /// Retail LOADING.
    ///
    /// Measured from local-lab/retail-reference-pristine/loading/
    /// 07-loading-640x480.png. The background is LoadingScreen.tga stretched to
    /// the full 640x480 stage: comparing the decoded texture resampled to
    /// 640x480 against the retail frame gives a mean absolute delta of 5.5 per
    /// channel over the whole frame BEFORE any overlay is drawn, and the only
    /// regions that disagree materially are the two overlay elements below.
    ///
    /// The previous implementation of this method drew neither of them
    /// correctly: it painted a 640x60 black band at y420 that retail does not
    /// draw at all, and put "Loading..." left-aligned at (24,436) scale 2 in
    /// Font13PS where retail centres it in font22 at scale 1 with its ink at
    /// x270..365, y401..419.
    ///
    ///   text  font22 scale 1, fitted origin (270, 393.5); its advance width 98
    ///         from x=270 centres on x=319
    ///   bar   x78..562, y423..447
    ///
    /// KNOWN GAP: the bar is drawn here as a measured opaque black rectangle,
    /// which its two ends are, but retail's is a TEXTURED bar whose alpha ramps
    /// off toward the middle — sampling row y=435 gives ref/background ratios of
    /// 0.07 at x=100 rising to ~0.77 near x=300 and back to 0.03 by x=540. That
    /// ramp is the BarL/BarC/BarR art the binary names, which is not in the
    /// materialized set, so it is not reproduced and the mid-bar residual is
    /// reported rather than tuned away. Note also that the reference frame is
    /// the earliest matching frame, so its bar is at zero fill: nothing here is
    /// evidence about how a filled bar draws.
    /// </summary>
    private void DrawLoading()
    {
        DrawRect(new Rect2(0f, 0f, DesignWidth, DesignHeight), Colors.Black);
        DrawTextureRect(
            _loadingScreen,
            new Rect2(0f, 0f, DesignWidth, DesignHeight),
            false);

        // Retail outlines this string rather than drop-shadowing it: the glyphs
        // carry a 1px black edge on all four sides, the same treatment the
        // click-to-start prompt uses. Drawing it with the standard +2/+2 shadow
        // instead left 50.6% of the text region materially different at an
        // otherwise pixel-exact ink bbox (ref x270..365 y401..420 against
        // x271..366 y401..420).
        var origin = new Vector2(LoadingTextLeft, LoadingTextTop);
        DrawFont22Outlined(_loadingText, origin + new Vector2(-1f, 1f), Colors.Black);
        DrawFont22Outlined(_loadingText, origin + new Vector2(1f, 1f), Colors.Black);
        DrawFont22Outlined(_loadingText, origin + new Vector2(-1f, -1f), Colors.Black);
        DrawFont22Outlined(_loadingText, origin + new Vector2(1f, -1f), Colors.Black);
        DrawFont22Outlined(_loadingText, origin, Colors.White);

        DrawRect(
            new Rect2(LoadingBarLeft, LoadingBarTop, LoadingBarWidth, LoadingBarHeight),
            Colors.Black);
    }

    private bool HandlePointerMotion(Vector2 position)
    {
        Vector2 design = ToDesignPosition(position);
        if (_session.Screen == RetailFrontendScreen.QuitConfirm)
        {
            int choice = QuitConfirmIndexAt(design);
            if (choice < 0 || !_session.SelectQuitConfirmIndex(choice))
            {
                return false;
            }

            RequestAudioCue(RetailFrontendAudioCue.Move);
            QueueRedraw();
            return true;
        }

        if (_session.Screen != RetailFrontendScreen.MainMenu)
        {
            return false;
        }

        int index = MainMenuIndexAt(design);
        // Retail hover requires GetActionCount ≠ 0 — ignore grayed rows.
        if (index < 0 ||
            !_session.Items[index].IsAvailable ||
            !_session.SelectMainIndex(index))
        {
            return false;
        }

        RequestAudioCue(RetailFrontendAudioCue.Move);
        QueueRedraw();
        return true;
    }

    private bool HandlePointerConfirm(Vector2 position)
    {
        Vector2 design = ToDesignPosition(position);
        switch (_session.Screen)
        {
            case RetailFrontendScreen.ClickToStart:
                Confirm();
                return true;

            case RetailFrontendScreen.MainMenu:
                int index = MainMenuIndexAt(design);
                if (index < 0 || !_session.Items[index].IsAvailable)
                {
                    return false;
                }
                if (_session.SelectMainIndex(index))
                {
                    RequestAudioCue(RetailFrontendAudioCue.Move);
                }
                Confirm();
                return true;

            case RetailFrontendScreen.QuitConfirm:
                int choice = QuitConfirmIndexAt(design);
                if (choice < 0)
                {
                    return false;
                }
                if (_session.SelectQuitConfirmIndex(choice))
                {
                    RequestAudioCue(RetailFrontendAudioCue.Move);
                }
                Confirm();
                return true;

            case RetailFrontendScreen.DevSelect:
                // Chevron hit rects match the drawn chevrons.
                if (new Rect2(0f, 430f, 46f, 48f).HasPoint(design))
                {
                    RetailFrontendSignal back = _session.Back();
                    if (back == RetailFrontendSignal.None)
                    {
                        return false;
                    }
                    RequestAudioCue(RetailFrontendAudioCue.Back);
                    HandleNavigationSignal(back);
                    QueueRedraw();
                    return true;
                }
                if (new Rect2(595f, 430f, 45f, 48f).HasPoint(design) ||
                    new Rect2(128f, 408f, 403f, 44f).HasPoint(design))
                {
                    Confirm();
                    return true;
                }
                return false;

            case RetailFrontendScreen.LevelSelect:
                // Chevron hit rects match the drawn chevrons, as on FEP_DEVSELECT.
                if (new Rect2(0f, 430f, 48f, 48f).HasPoint(design))
                {
                    RetailFrontendSignal levelBack = _session.Back();
                    if (levelBack == RetailFrontendSignal.None)
                    {
                        return false;
                    }
                    RequestAudioCue(RetailFrontendAudioCue.Back);
                    HandleNavigationSignal(levelBack);
                    QueueRedraw();
                    return true;
                }
                if (new Rect2(595f, 430f, 45f, 48f).HasPoint(design) ||
                    new Rect2(120f, 265f, 60f, 60f).HasPoint(design))
                {
                    Confirm();
                    return true;
                }
                return false;

            case RetailFrontendScreen.MissionBriefing:
            case RetailFrontendScreen.SelectConfiguration:
                // Both pages carry the same two chevrons and nothing else
                // clickable this lane models.
                if (new Rect2(0f, 430f, 48f, 48f).HasPoint(design))
                {
                    RetailFrontendSignal pageBack = _session.Back();
                    if (pageBack == RetailFrontendSignal.None)
                    {
                        return false;
                    }
                    RequestAudioCue(RetailFrontendAudioCue.Back);
                    HandleNavigationSignal(pageBack);
                    QueueRedraw();
                    return true;
                }
                if (new Rect2(595f, 430f, 45f, 48f).HasPoint(design))
                {
                    Confirm();
                    return true;
                }
                return false;

            default:
                return false;
        }
    }

    private bool HandleKey(InputEventKey key)
    {
        // The FEP_DEVSELECT name field is editable; retail pre-fills it from the
        // highlighted list entry and lets the player type over it.
        if (_session.Screen == RetailFrontendScreen.DevSelect)
        {
            if (IsKey(key, Key.Backspace))
            {
                if (_session.RemoveGameNameCharacter())
                {
                    QueueRedraw();
                }
                return true;
            }

            char typed = (char)key.Unicode;
            if (typed is >= ' ' and <= '~' && _session.AppendGameNameCharacter(typed))
            {
                QueueRedraw();
                return true;
            }
        }

        if (IsKey(key, Key.Up) || IsKey(key, Key.Left))
        {
            if (_session.MovePrevious())
            {
                RequestAudioCue(RetailFrontendAudioCue.Move);
                QueueRedraw();
            }
            return true;
        }
        if (IsKey(key, Key.Down) || IsKey(key, Key.Right))
        {
            if (_session.MoveNext())
            {
                RequestAudioCue(RetailFrontendAudioCue.Move);
                QueueRedraw();
            }
            return true;
        }
        if (IsKey(key, Key.Enter) || IsKey(key, Key.KpEnter) || IsKey(key, Key.Space))
        {
            Confirm();
            return true;
        }
        if (IsKey(key, Key.Escape))
        {
            RetailFrontendSignal signal = _session.Back();
            if (signal != RetailFrontendSignal.None)
            {
                RequestAudioCue(RetailFrontendAudioCue.Back);
                HandleNavigationSignal(signal);
                QueueRedraw();
            }
            return true;
        }

        return false;
    }

    private void Confirm()
    {
        RetailFrontendSignal signal = _session.Confirm();
        if (signal == RetailFrontendSignal.None)
        {
            return;
        }

        RequestAudioCue(RetailFrontendAudioCue.Select);
        HandleNavigationSignal(signal);
        if (signal == RetailFrontendSignal.ExitRequested)
        {
            GetTree().Quit(0);
        }
        QueueRedraw();
    }

    private void ResumeFrontendForNavigation(RetailFrontendScreen origin)
    {
        if (origin == RetailFrontendScreen.Gameplay)
        {
            GameplaySuspended?.Invoke();
        }

        Visible = true;
        SetProcessInput(true);
        SetProcess(true);
    }

    private void HandleNavigationSignal(RetailFrontendSignal signal)
    {
        if (signal == RetailFrontendSignal.Level100LaunchRequested)
        {
            _loadRequestRaised = false;
            _level100Ready = false;
            _gameplayActivationRaised = false;
            _loadingFrames = 0;
            CursorModeRequested?.Invoke(RetailFrontendCursorMode.Hidden);
        }
        else if (signal == RetailFrontendSignal.ReturnToMainMenuRequested)
        {
            CursorModeRequested?.Invoke(RetailFrontendCursorMode.Visible);
            ReturnToMainMenuRequested?.Invoke();
        }
        else if (signal == RetailFrontendSignal.PageChanged)
        {
            CursorModeRequested?.Invoke(RetailFrontendCursorMode.Visible);
        }
    }

    private int MainMenuIndexAt(Vector2 designPosition)
    {
        var menuRect = new Rect2(
            MenuColumnX - MenuHitHalfWidth,
            MenuStartY - (MenuPitch * 0.5f),
            MenuHitHalfWidth * 2f,
            MenuPitch * _session.Items.Count);
        if (!menuRect.HasPoint(designPosition))
        {
            return -1;
        }

        int index = (int)((designPosition.Y - MenuStartY + (MenuPitch * 0.5f)) / MenuPitch);
        return Math.Clamp(index, 0, _session.Items.Count - 1);
    }

    private static int QuitConfirmIndexAt(Vector2 designPosition)
    {
        if (new Rect2(160f, 240f, 120f, 36f).HasPoint(designPosition))
        {
            return 0;
        }

        if (new Rect2(360f, 240f, 120f, 36f).HasPoint(designPosition))
        {
            return 1;
        }

        return -1;
    }

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
        _level100Text = RequiredString(strings, "level100");
        _loadingText = RequiredString(strings, "loading");
    }

    private void LoadTextures()
    {
        _clickBackground = LoadTexture(
            "Backgrounds/click-to-start",
            1024,
            1024,
            CuratedAyaTextureLoader.Compression.Dxt1);
        _rockBackground = LoadTexture(
            "Backgrounds/rock",
            1024,
            512,
            CuratedAyaTextureLoader.Compression.Dxt1);
        _clickSlide = LoadTexture("click-slide", 128, 128);
        _forsetiWritingLarge = LoadTexture("forseti-writing-large", 128, 512);
        _reflectionMap = LoadTexture(
            "reflection-map",
            512,
            128,
            CuratedAyaTextureLoader.Compression.Dxt1);
        _titleLogo = LoadTexture("title-logo", 512, 256);
        _titleBracket01 = LoadTexture("title-bracket-01", 256, 256);
        _titleBracket02 = LoadTexture("title-bracket-02", 256, 256);
        _titleTextBox = LoadTexture("title-text-box", 256, 32);
        _symbolBracket01 = LoadTexture("symbol-bracket-01", 128, 128);
        _symbolBracket02 = LoadTexture("symbol-bracket-02", 128, 128);
        _levelBracket01 = LoadTexture("level-bracket-01", 512, 512);
        _levelBracket02 = LoadTexture("level-bracket-02", 512, 512);
        _levelRing01 = LoadTexture("level-ring-01", 64, 64);
        _levelRing02 = LoadTexture("level-ring-02", 64, 64);
        _loadingScreen = LoadTexture(
            "loading-screen",
            512,
            512,
            CuratedAyaTextureLoader.Compression.Dxt1);
        // data/language holds exactly five sets and the released texture set carries
        // exactly five matching flags (Career.h: NUM_LANGUAGES 5). Order matches
        // RetailFrontendLanguage.
        _languageFlags =
        [
            LoadTexture("Flags/flag-uk", 128, 128, CuratedAyaTextureLoader.Compression.Dxt1),
            LoadTexture("Flags/flag-fr", 128, 128, CuratedAyaTextureLoader.Compression.Dxt1),
            LoadTexture("Flags/flag-gr", 128, 128, CuratedAyaTextureLoader.Compression.Dxt1),
            LoadTexture("Flags/flag-it", 128, 128, CuratedAyaTextureLoader.Compression.Dxt1),
            LoadTexture("Flags/flag-sp", 128, 128, CuratedAyaTextureLoader.Compression.Dxt1),
        ];
        _feArrow = LoadTexture("fe-arrow", 64, 64);
        // Retail shares one bitmap font resource between HUD and frontend, so this
        // legitimately reaches into the Hud asset folder rather than duplicating it.
        _titleFont = LoadTexture(
            "font-13ps",
            256,
            256,
            CuratedAyaTextureLoader.Compression.Rgba8,
            folder: "Hud");
        // mustbe_font22.512.tga, shared with the HUD for the same reason.
        _font22 = LoadTexture(
            "font-22",
            512,
            512,
            CuratedAyaTextureLoader.Compression.Rgba8,
            folder: "Hud");
        // Must match RetailFrontendSession Steam-drawn row order (Update/icons).
        _menuIcons =
        [
            LoadTexture("Icons/new-game", 128, 128),
            LoadTexture("Icons/continue-game", 128, 128),
            LoadTexture("Icons/load-game", 128, 128),
            LoadTexture("Icons/multiplayer", 128, 128),
            LoadTexture("Icons/goodies", 128, 128),
            LoadTexture("Icons/options", 128, 128),
            LoadTexture("Icons/quit", 128, 128),
        ];
    }

    private static Texture2D[] LoadFeBackFrames()
    {
        string absolute = ProjectSettings.GlobalizePath(FeBackStripPath);
        if (!File.Exists(absolute))
        {
            GD.PushWarning(
                $"FEBack strip missing at {FeBackStripPath}; main underlay uses solid fallback.");
            return [];
        }

        byte[] strip = File.ReadAllBytes(absolute);
        if (strip.Length == 0 || strip.Length % FeBackFrameBytes != 0)
        {
            throw new InvalidDataException(
                $"FEBack strip length {strip.Length} is not a multiple of {FeBackFrameBytes}.");
        }

        int frameCount = strip.Length / FeBackFrameBytes;
        var frames = new Texture2D[frameCount];
        for (int index = 0; index < frameCount; index++)
        {
            byte[] frame = new byte[FeBackFrameBytes];
            Buffer.BlockCopy(strip, index * FeBackFrameBytes, frame, 0, FeBackFrameBytes);
            Image image = Image.CreateFromData(
                FeBackWidth,
                FeBackHeight,
                false,
                Image.Format.Rgb8,
                frame);
            frames[index] = ImageTexture.CreateFromImage(image);
        }

        return frames;
    }

    private static Texture2D LoadTexture(
        string name,
        int width,
        int height,
        CuratedAyaTextureLoader.Compression compression = CuratedAyaTextureLoader.Compression.Dxt2,
        string folder = "Frontend") =>
        CuratedAyaTextureLoader.Load(
            $"res://Assets/{folder}/{name}.texture.aya",
            width,
            height,
            compression);

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

    private void DrawAdditiveSurfaceCentered(
        Texture2D texture,
        float centerX,
        float centerY,
        float widthScale,
        float heightScale,
        Color modulate)
    {
        _additiveMaterial ??= new CanvasItemMaterial
        {
            BlendMode = CanvasItemMaterial.BlendModeEnum.Add,
        };
        Material = _additiveMaterial;
        DrawSurfaceCentered(texture, centerX, centerY, widthScale, heightScale, modulate);
        Material = null;
    }

    private void DrawCenteredRotated(
        Texture2D texture,
        Vector2 center,
        Vector2 size,
        float rotation,
        Color modulate)
    {
        // CONSENSUS_C: single window↔stage map. DrawSetTransform replaces (does not nest);
        // re-apply letterbox around the design-space pivot, then restore design space.
        (float scale, Vector2 offset) = DesignTransform();
        DrawSetTransform(
            offset + (center * scale),
            rotation,
            new Vector2(scale, scale));
        DrawTextureRect(texture, new Rect2(-size * 0.5f, size), false, modulate);
        DrawSetTransform(offset, 0f, new Vector2(scale, scale));
    }

    private void DrawTextCentered(string text, Vector2 center, float scale, Color color)
    {
        float width = MeasureText(text, scale);
        DrawText(text, new Vector2(center.X - (width * 0.5f), center.Y), scale, color);
    }

    private void DrawText(string text, Vector2 position, float scale, Color color) =>
        DrawTextCore(text, position, scale, color, dropShadow: true);

    private void DrawTextFlat(string text, Vector2 position, float scale, Color color) =>
        DrawTextCore(text, position, scale, color, dropShadow: false);

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
                DrawTextureRectRegion(
                    atlas,
                    new Rect2(destination.Position + new Vector2(2f, 2f), destination.Size),
                    source,
                    new Color(0f, 0f, 0f, color.A * 0.82f));
            }

            DrawTextureRectRegion(atlas, destination, source, color);
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

    private void DrawFont22Outlined(string text, Vector2 position, Color color) =>
        DrawAtlasText(
            _font22,
            _font22Widths,
            Font22CellSize,
            Font22Columns,
            text,
            position,
            1f,
            1f,
            color,
            dropShadow: false);

    private float MeasureFont22Text(string text, float scaleX)
    {
        float width = 0f;
        foreach (char character in text)
        {
            width += (_font22Widths[GlyphIndex(character)] + 1) * scaleX;
        }
        return Mathf.Max(0f, width - scaleX);
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

    private (float Scale, Vector2 Offset) DesignTransform()
    {
        float scale = Mathf.Min(Size.X / DesignWidth, Size.Y / DesignHeight);
        return (
            scale,
            new Vector2(
                (Size.X - (DesignWidth * scale)) * 0.5f,
                (Size.Y - (DesignHeight * scale)) * 0.5f));
    }

    private Vector2 ToDesignPosition(Vector2 viewportPosition)
    {
        (float scale, Vector2 offset) = DesignTransform();
        return scale <= 0f ? Vector2.Zero : (viewportPosition - offset) / scale;
    }

    private static string RequiredString(JsonElement strings, string key)
    {
        string? value = strings.GetProperty(key).GetString();
        return string.IsNullOrEmpty(value)
            ? throw new InvalidDataException($"Released frontend localization is missing '{key}'.")
            : value;
    }

    private static bool IsKey(InputEventKey input, Key key) =>
        input.PhysicalKeycode == key || input.Keycode == key;

    private void RequestAudioCue(RetailFrontendAudioCue cue) =>
        AudioCueRequested?.Invoke(cue);

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
}
