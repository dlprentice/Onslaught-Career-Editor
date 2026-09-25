// SPDX-License-Identifier: GPL-3.0-or-later
using System.Text.Json;
using Godot;
using OnslaughtRebuild.Client;
namespace OnslaughtRebuild.GodotClient;

/// <summary>Unchanged Main Menu drawing, authored-subtree routing and native
/// TextureRect update laws retained from e31519b8's predecessor renderer.
/// Only the host/session harness and type names are reduced to this one page.
/// This is a comparison owner, never called by production presentation.</summary>
public sealed partial class MainMenuReference : Control
{
    private const float DesignWidth = 640f;
    private const float DesignHeight = 480f;
    private const float MenuColumnX = 219f;
    private static float MenuStartY => RetailMainMenuRowY.NonzeroSlotY;
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
    private static readonly Color ReleasedNormal = RetailColor(0xfd4f4f4f);
    private static readonly Color ReleasedUnavailable = RetailColor(0x7d1f1f1f);
    private static readonly Color ReleasedSelected = RetailColor(0xfdff6f3f);
    private static readonly Color ReleasedBlue = RetailColor(0xff1f4f7f);
    // 0xfeafcfff is an immediate in the image: `and edx,0xffafcfff` /
    // `or edx,0xafcfff` at 0x004642e4 / 0x004642f1 inside CFEPMain__Render.
    //
    // Whether it goes through RetailColor()'s MODULATE2X was tested on 2026-07-26
    // and plain MODULATE was REFUTED — full-frame material rose 18.54 -> 18.73 %
    // and meanD 6.19 -> 7.07 on all 13 paired frames.
    //
    // THAT TEST IS WITHDRAWN, because it was run against a build that was missing
    // the additive sheen (TitleLogoReflectionLayer). Two errors were cancelling:
    // the sheen adds a mean +42/+39/+26 inside the logo footprint, and a
    // 2x-clamped white tint was covering for it. With the sheen restored and
    // subtracted, retail's logo body against ours regresses to
    //   slope 0.589 / 0.704 / 0.850, intercept +9.5 / +10.7 / +14.9
    // over 420k unsaturated footprint pixels on the 12 settled frames. The SLOPE
    // RATIOS 0.692 / 0.828 / 1.000 are the packed tint's own ratios
    // 0xaf/0xff = 0.686, 0xcf/0xff = 0.812, 1.000 — so the hue is real and the 2x
    // that erased it is wrong here. The default render-state block sets stage 0
    // COLOROP = D3DTOP_MODULATE, not MODULATE2X
    // (reverse-engineering/binary-analysis/d3d-default-render-state-block-2026-07-27.md
    // section 7), which is the mechanism, not a fit.
    //
    // STILL UNEXPLAINED, and deliberately NOT tuned away: a uniform residual gain
    // of ~0.86 and an intercept of ~+12 remain after the tint ratios are taken
    // out. Candidates are the 0x3e000000 logo shadow showing through partial
    // alpha, and the DXT2 premultiplied-alpha path. Neither is measured.
    private static readonly Color TitleLogoTint = new(
        0xafu / 255f,
        0xcfu / 255f,
        0xffu / 255f,
        0xfeu / 255f);
    private static readonly Color HighlightTint = RetailColor(0x7e000000);
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
    // 0x3e7f7f7f, CORRECTED 2026-07-28 from 0x3ecfffff. Same class of error and
    // worse: 0xcf was a *hue* that MODULATE2X clamps straight back to 255, so
    // the constant claimed a warm tint that could never reach a pixel. Retail's
    // byte is 0x3E7F7F7F, shared bit-for-bit by both element groups this tints:
    // the three Forseti chrome strips (frame 3000 draws 3, 4 and 5, 128x512
    // DXT2) and the two language chevrons (draws 7 and 9, 64x64 DXT2).
    // Alpha 0x3E was already exact.
    private static readonly Color ChromeTint = RetailColor(0x3e7f7f7f);
    // Language-selector flag tint; see DrawLanguageSelector for the measurement.
    // Alpha 0xfd, CORRECTED 2026-07-28 from 0xff: frame 3000 draw 6 is
    // 0xFD3F3F3F. Same alpha-byte class as the row-label correction at :75-77.
    private static readonly Color FlagTint = RetailColor(0xfd3f3f3f);
    private static readonly Color ShadowTint = RetailColor(0x3e000000);
    private static readonly Color VersionTint = RetailColor(0xff102025);
    // Released overlay format is CFEPMain::Render 0x0046416E:
    // push 0x00629454 "V%1d.%02d". Image-initial major 0x00629410 is 1;
    // minor 0x00679980 is BSS 0. RetailMainMenuVersionOverlay owns the
    // sprintf. The prior value here was "V1.00 - PATCHED", transcribed
    // from a reference capture taken on a safe copy whose
    // version_overlay_* patches repoint the format pointer at 0x0046416f
    // to a code cave at VA 0x005AA444 holding "V%1d.%02d - PATCHED".
    // That suffix is an artifact of the patched capture, not released
    // behavior. Colour at 0x004641B1/B4 is fade<<24 | 0x00102025 =
    // 0xFF102025 settled, which is this VersionTint, so the draw keeps
    // VersionTint and does not call SubmittedColor.

    private const float ShadowScaleBoost = 1.05f;
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

    // ================= THE RELEASED PAGE-TRANSITION MACHINE =================
    //
    // Ported from the pinned GPL drop:
    //
    //   references/Onslaught/FrontEnd.cpp:563-592  CFrontEnd::SetPage(page, time)
    //       time == 0 goes straight there; time > 0 sets mTransitionCount = 0,
    //       mTransitionTime = time and parks mActivePage at FEP_TRANSITION.
    //   references/Onslaught/FrontEnd.cpp:665-675  CFrontEnd::Process()
    //       mTransitionCount++ ONCE per Process, and the destination page becomes
    //       active on the Process where mTransitionCount == mTransitionTime.
    //   references/Onslaught/FrontEnd.cpp:1291     CFrontEnd::Render()
    //       trans = float(mTransitionCount) / float(mTransitionTime).
    //   references/Onslaught/FrontEnd.cpp:1431-1438 CFrontEnd::Run()
    //       exactly one Process per rendered frame;
    //   references/Onslaught/FrontEnd.cpp:1261     Render() refuses to draw until
    //       1/60 s has passed, so a transition length is a FRAME COUNT and one
    //       frame is AT LEAST 1/60 s. Lengths are never stored as milliseconds:
    //       a wall-clock length would make the reveal host-dependent.
    //
    // Frontend.h:97 `#define MAINTIME 70` is NOT this length. It has exactly one
    // caller in the drop — FEPGoodies.cpp:1461, the Goodies BACK edge — and
    // FEPIntro.cpp is absent. The cold-start length came from the shipped bytes
    // instead; see MainMenuEntryTransitionFrames.
    //
    // NOT IMPLEMENTED, and why. FrontEnd.cpp:1291-1334 renders BOTH pages during
    // a transition (higher page ordinal first), the outgoing one at 1 - trans.
    // On this edge the outgoing page is the click page, and retail's own first
    // main-menu frame REFUTES a visible outgoing draw: at t = 14 ms
    // (run1/mm-t000014ms.png) the frame is the flat fill plus the title logo plus
    // the crosshair guides and NOTHING else, while 1 - trans = 0.98 there. The
    // ordinals are known for this edge anyway — SetPage is called with page 0 and
    // CFEPMain__Render tests dest == 0x0c, so to = 0 and from = 12, meaning
    // FrontEnd.cpp:1304 draws the click page FIRST and the main menu over it —
    // so a second draw would have to be visible under the (video-less) main menu
    // and is not. Drawing one would ADD a defect, so this lane keeps the single
    // atomic page swap it already had and records the divergence here.
    //
    /// <summary>
    /// Length of the cold-start click-to-start -> FEP_MAIN transition, in
    /// frontend frames.
    ///
    /// RECOVERED FROM THE SHIPPED BYTES, not from the drop. Read out of
    /// <c>local-lab/safe-copy-bea-pristine/BEA.exe.original.backup</c>
    /// (sha256 74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750;
    /// the installed Steam BEA.exe is deliberately patched and is not a valid
    /// specimen). At VA 0x0051B660 / file 0x11B660, the click page's action
    /// handler:
    /// <code>
    ///   0051b660  83 7c 24 04 2c    cmp   dword [esp+4], 0x2C   ; the click action
    ///   0051b686  6a 32             push  0x32                  ; time  = 50
    ///   0051b690  6a 00             push  0                     ; page  = 0 = FEP_MAIN
    ///   0051b698  b9 58 d7 89 00    mov   ecx, 0x0089d758       ; &amp;FRONTEND
    ///   0051b69d  e8 3e b4 f4 ff    call  0x00466ae0            ; CFrontEnd::SetPage
    /// </code>
    /// So the released cold-start reveal is 50 frames, and FEP_MAIN's ordinal is 0.
    ///
    /// <para><b>The rate is the unresolved part, and it is not papered over.</b>
    /// 50 frames at the source's own 1/60 s gate settles at 817 ms. Retail's burst
    /// is settled at t = 1020 ms and NOT settled at t = 812 ms (menu-column peak
    /// channel 155 against 253 settled), so retail's realised reveal is somewhat
    /// slower than 50/60 s. FrontEnd.cpp:1261 is a floor, not a target — a frame
    /// whose work or whose <c>PLATFORM.Flip()</c> exceeds 1/60 s simply takes
    /// longer, and FrontEnd.cpp:1437 <c>while(!Render());</c> also burns whole
    /// frames without ticking the count whenever RenderStart fails, which is
    /// exactly what an async-loading video does at page entry. The frame count is
    /// evidenced; the realised frontend frame rate is NOT, and no rate constant is
    /// fitted here to close the ~15 % gap.</para>
    /// </summary>
    private const int MainMenuEntryTransitionFrames = 50;

    private float _transition = 1f;
    private float MainMenuTransition => _transition;
    private double _animationSeconds, _feBackSeconds;
    private readonly ReferenceSession _session = new();
    private readonly Dictionary<RetailFrontendMenuItemKind, string> _menuText = [];
    private Texture2D[] _feBackFrames = [];
    private Texture2D _forsetiWritingLarge = null!, _titleLogo = null!, _reflectionMap = null!;
    private Texture2D _titleBracket01 = null!, _titleBracket02 = null!, _titleTextBox = null!;
    private Texture2D _symbolBracket01 = null!, _symbolBracket02 = null!, _feArrow = null!, _titleFont = null!;
    private Texture2D[] _languageFlags = [], _menuIcons = [];
    private int[] _glyphWidths = [];
    private TitleLogoReflectionLayer? _titleLogoReflection;
    private readonly Dictionary<string, MainMenuReferencePart> _sceneParts = new(StringComparer.Ordinal);
    private readonly Dictionary<string, RetailTextureRect> _nativeTextures = new(StringComparer.Ordinal);
    private readonly Dictionary<string, Color> _nativeTints = new(StringComparer.Ordinal);
    private Control _stage = null!;
    private MainMenuReferencePart? _paintingPart;
    private string _drawingSection = string.Empty;
    private bool _initialized;
    private static readonly Color DevSelectGuide = new(50f / 255f, 51f / 255f, 72f / 255f, 1f);
    private sealed class ReferenceSession
    {
        internal List<RetailFrontendMenuItem> Items { get; } = Enum.GetValues<RetailFrontendMenuItemKind>().Select(kind => new RetailFrontendMenuItem(kind, kind != RetailFrontendMenuItemKind.ContinueGame)).ToList();
        internal int SelectedMainIndex { get; set; }
        internal RetailFrontendMenuItem SelectedMainItem => Items[SelectedMainIndex];
        internal RetailFrontendLanguage Language { get; set; }
        internal RetailFrontendScreen Screen { get; set; } = RetailFrontendScreen.MainMenu;
    }
    internal void Initialize()
    {
        if (_initialized) return;
        _stage = GetNode<Control>("Stage");
        foreach (Node node in _stage.FindChildren("*", nameof(Control), true, false))
            if (node is MainMenuReferencePart part) _sceneParts.Add(part.Section, part);
        foreach (Node node in _stage.FindChildren("*", "TextureRect", true, false))
            if (node is RetailTextureRect image)
            {
                string path = _stage.GetPathTo(image).ToString();
                _nativeTextures.Add(path, image); _nativeTints.Add(path, image.SelfModulate);
            }
        using JsonDocument strings = JsonDocument.Parse(Godot.FileAccess.GetFileAsString("res://Assets/Frontend/english.json"));
        JsonElement rows = strings.RootElement.GetProperty("strings");
        string[] keys = ["newGame", "continueGame", "loadGame", "multiplayer", "goodies", "options", "quit"];
        for (int index = 0; index < keys.Length; index++) _menuText.Add((RetailFrontendMenuItemKind)index, rows.GetProperty(keys[index]).GetString()!);
        _titleFont = LoadTexture("font-13ps", 256, 256, LegacyCuratedAyaTextureReference.Compression.Rgba8, "Hud");
        using (Image atlas = _titleFont.GetImage()) _glyphWidths = MeasureGlyphWidths(atlas, 16, 16);
        _forsetiWritingLarge = LoadTexture("forseti-writing-large", 128, 512);
        _titleLogo = LoadTexture("title-logo", 512, 256);
        _reflectionMap = LoadTexture("reflection-map", 512, 128, LegacyCuratedAyaTextureReference.Compression.Dxt1);
        _titleBracket01 = LoadTexture("title-bracket-01", 256, 256);
        _titleBracket02 = LoadTexture("title-bracket-02", 256, 256);
        _titleTextBox = LoadTexture("title-text-box", 256, 32);
        _symbolBracket01 = LoadTexture("symbol-bracket-01", 128, 128);
        _symbolBracket02 = LoadTexture("symbol-bracket-02", 128, 128);
        _feArrow = LoadTexture("fe-arrow", 64, 64);
        _languageFlags = new[] { "uk", "fr", "gr", "it", "sp" }.Select(name => LoadTexture("Flags/flag-" + name, 128, 128, LegacyCuratedAyaTextureReference.Compression.Dxt1)).ToArray();
        _menuIcons = new[] { "new-game", "continue-game", "load-game", "multiplayer", "goodies", "options", "quit" }.Select(name => LoadTexture("Icons/" + name, 128, 128)).ToArray();
        using Resource recipe = GD.Load<Resource>("res://Scenes/Frontend/FrontendUnderlay.tres");
        using Godot.Collections.Dictionary loaded = recipe.Call("load_frames").AsGodotDictionary();
        if (!loaded["ok"].AsBool()) throw new InvalidDataException(loaded["error"].AsString());
        using Godot.Collections.Array frames = loaded["frames"].AsGodotArray();
        _feBackFrames = frames.Select(value => value.As<Texture2D>()).ToArray();
        _titleLogoReflection = new TitleLogoReflectionLayer { Name = "TitleLogoReflection" };
        AddChild(_titleLogoReflection);
        _titleLogoReflection.Configure(_titleLogo, _reflectionMap);
        Resized += FitStage;
        _initialized = true;
        SetProcess(false); SetProcessInput(false); SetProcessUnhandledInput(false);
    }
    public override void _Ready() { Initialize(); FitStage(); Refresh(); }
    public override void _Draw() => base.DrawRect(new Rect2(Vector2.Zero, Size), Colors.Black);
    internal void SetFrame(float transition, double animationSeconds, double backgroundSeconds, int selection, int language, bool[] available, string[] labels, bool reflection)
    {
        _transition = transition; _animationSeconds = animationSeconds; _feBackSeconds = backgroundSeconds;
        _session.SelectedMainIndex = selection; _session.Language = (RetailFrontendLanguage)language;
        _session.Screen = reflection ? RetailFrontendScreen.MainMenu : RetailFrontendScreen.QuitConfirm;
        for (int index = 0; index < 7; index++)
        {
            _session.Items[index] = new RetailFrontendMenuItem((RetailFrontendMenuItemKind)index, available[index]);
            _menuText[(RetailFrontendMenuItemKind)index] = labels[index];
        }
        Refresh();
    }
    private void Refresh()
    {
        if (!_initialized || !IsInsideTree()) return;
        UpdateNativeTextures(); UpdateTitleLogoReflection();
        foreach (MainMenuReferencePart part in _sceneParts.Values) part.QueueRedraw();
    }
    private void FitStage()
    {
        (float scale, Vector2 offset) = DesignTransform();
        _stage.Position = offset; _stage.Scale = new Vector2(scale, scale);
        Refresh();
    }
    internal int RowAt(Vector2 design) => MainMenuIndexAt(design);
    internal Texture2D Font => _titleFont;
    internal int[] Widths => _glyphWidths.ToArray();
    internal string[] Labels => Enum.GetValues<RetailFrontendMenuItemKind>().Select(kind => _menuText[kind]).ToArray();
    internal Texture2D[] Flags => _languageFlags;
    internal Texture2D[] Icons => _menuIcons;
    internal Texture2D[] Frames => _feBackFrames;
    internal IReadOnlyDictionary<string, MainMenuReferencePart> Parts => _sceneParts;
    internal Dictionary<string, Texture2D> Art => new()
    {
        ["forseti-writing-large"] = _forsetiWritingLarge, ["title-logo"] = _titleLogo,
        ["reflection-map"] = _reflectionMap, ["title-bracket-01"] = _titleBracket01,
        ["title-bracket-02"] = _titleBracket02, ["title-text-box"] = _titleTextBox,
        ["symbol-bracket-01"] = _symbolBracket01, ["symbol-bracket-02"] = _symbolBracket02, ["fe-arrow"] = _feArrow,
    };
    internal float Measure(string text) => MeasureText(text, 1f);
    internal Godot.Collections.Dictionary InspectLaws(float transition, double seconds)
    {
        var offsets = RetailFrontendDecorShadow.OffsetAtPhase(RetailFrontendDecorShadow.PhaseAtSeconds(seconds));
        MainMenuDecor[] decorations = [MainMenuLeftDecor(transition), MainMenuLeftDecorTwin(transition), MainMenuRightDecor(transition), MainMenuRightDecorTwin(transition)];
        var result = new Godot.Collections.Dictionary
        {
            ["fade"] = (double)Clamp01((transition - 0.75f) * 4f),
            ["icon"] = (double)Clamp01((transition - 0.8f) * 5f),
            ["underlay"] = (double)MakeAlpha(RangeTransition(transition, 0f, 0.5f)),
            ["phase"] = RetailFrontendDecorShadow.PhaseAtSeconds(seconds),
            ["shadow"] = new double[] { offsets.X, offsets.Y },
            ["scroll"] = (double)Mathf.PosMod(((float)seconds * 29.95f) + 86.68f, 512f),
        };
        using var rows = new Godot.Collections.Array();
        foreach (MainMenuDecor item in decorations)
        {
            using var row = new Godot.Collections.Dictionary { ["scale"] = (double)item.Scale, ["rotation"] = (double)item.Rotation, ["alpha"] = (double)item.Alpha, ["draw"] = item.Draw,
                ["transform"] = new Transform2D(item.Rotation, Vector2.One, 0f, Vector2.Zero) };
            rows.Add(row);
        }
        result["decorations"] = rows;
        return result;
    }
    private Texture2D LoadTexture(string name, int width, int height, LegacyCuratedAyaTextureReference.Compression compression = LegacyCuratedAyaTextureReference.Compression.Dxt2, string folder = "Frontend") =>
        LegacyCuratedAyaTextureReference.Load($"res://Assets/{folder}/{name}.texture.aya", width, height, compression);
    internal void DrawScenePart(MainMenuReferencePart part)
    {
        if (!_initialized || part.SourceRect.Size.X <= 0f || part.SourceRect.Size.Y <= 0f) return;
        _paintingPart = part; _drawingSection = string.Empty;
        try { DrawSetTransform(Vector2.Zero, 0f, Vector2.One); DrawMainMenu(); }
        finally { _paintingPart = null; _drawingSection = string.Empty; }
    }
    private void SelectSceneSection(string section) => _drawingSection = section;
    private bool DrawsSceneSection => _paintingPart is not null && _paintingPart.Section == _drawingSection;
    private string SceneText(string importedText) => DrawsSceneSection && _paintingPart!.OverrideText ? _paintingPart.Text : importedText;
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

    /// <summary>Scale, rotation and alpha of one animated main-menu decoration.</summary>
    private readonly record struct MainMenuDecor(float Scale, float Rotation, float Alpha, bool Draw);

    /// <summary>
    /// Left decoration <c>DAT_0089d894</c> (title-bracket-01) at (219, 344).
    ///
    /// PORTED FROM THE SHIPPED BYTES, dest == 0x0c branch of CFEPMain__Render
    /// (0x00462D40, pristine BEA.exe.original.backup sha256 74154bfa…). The drop
    /// has no FEPMain.cpp, so this law is not available from source; what the drop
    /// does carry is the same law's SHAPE in CFrontEnd's shared helpers —
    /// FrontEnd.cpp:854-876 for a bordered page whose other side is FEP_MAIN, and
    /// the generic FrontEnd.cpp:881-887 — and the breakpoint/scale idioms match.
    /// The thresholds below are the shipped ones and the float pool addresses are
    /// verified: 0.2 @0x005d8604, 0.4 @0x005d8c40, 0.6 @0x005d8bb8, 5.0 @0x005db564,
    /// 0.25 @0x005d858c, 0.3 @0x005d8cb4.
    ///
    /// <para><b>Why dest == 0x0c and not the generic branch.</b> The generic branch
    /// fades the TITLE LOGO with the page (its alpha is the same clamp as the menu
    /// rows); the 0x0c branch forces the logo to 0xff (0x0046423D). Retail's first
    /// main-menu frame has the logo at ~96 % of its settled value while the menu
    /// column, the language selector and both bracket pairs are still exactly the
    /// flat fill. Only the 0x0c branch can produce that frame.</para>
    /// </summary>
    private static MainMenuDecor MainMenuLeftDecor(float transition)
    {
        float scale = 1.25f;
        float rotation = 0f;
        float alpha = 1f;
        if (transition < 1f)
        {
            if (transition < 0.2f)
            {
                float t = Clamp01(transition * 5f);
                alpha = MakeAlpha(t);
                rotation = -((1f - t) * 0.3f);
                scale = t;
            }
            else if (transition < 0.4f)
            {
                scale = 1f;
            }
            else if (transition < 0.6f)
            {
                scale = (Clamp01((transition - 0.4f) * 5f) * 0.25f) + 1f;
            }
        }

        return new MainMenuDecor(scale, rotation, alpha, Draw: true);
    }

    /// <summary>
    /// Left transition twin <c>DAT_0089d898</c> (title-bracket-02), same anchor.
    /// Drawn ONLY while transition &lt; 1 and only on the dest == 0x0c side, and
    /// gone from 0.8 onward — the settled main menu has never drawn it, which is
    /// why it is absent from this lane's settled frame today.
    ///
    /// Note the rotation sign flips between the two moving windows in the shipped
    /// code (positive below 0.2, negative in 0.6..0.8). That is reproduced rather
    /// than tidied.
    /// </summary>
    private static MainMenuDecor MainMenuLeftDecorTwin(float transition)
    {
        if (transition >= 1f)
        {
            return default;
        }

        if (transition < 0.2f)
        {
            float t = Clamp01(transition * 5f);
            return new MainMenuDecor(t, (1f - t) * 0.3f, MakeAlpha(t), Draw: true);
        }

        if (transition < 0.6f)
        {
            return new MainMenuDecor(1f, 0f, 1f, Draw: true);
        }

        if (transition < 0.8f)
        {
            float t = 1f - Clamp01((transition - 0.6f) * 5f);
            return new MainMenuDecor(t, -((1f - t) * 0.3f), MakeAlpha(t), Draw: true);
        }

        return default;
    }

    /// <summary>
    /// Right decoration <c>DAT_0089d8a0</c> (symbol-bracket-01) at (457, 355).
    /// Same dest == 0x0c branch, one breakpoint set earlier than the left pair:
    /// 0.1 @0x005d85c0, 0.3 @0x005d8cb4, 0.5 @0x005d85ec, 0.7 @0x005d8bec.
    /// Below 0.1 the shipped code leaves the scale at 1.25 and zeroes the alpha,
    /// so it is invisible rather than small — reproduced as written.
    /// </summary>
    private static MainMenuDecor MainMenuRightDecor(float transition)
    {
        float scale = 1.25f;
        float rotation = 0f;
        float alpha = 1f;
        if (transition < 1f)
        {
            if (transition < 0.1f)
            {
                alpha = 0f;
            }
            else if (transition < 0.3f)
            {
                float t = Clamp01((transition - 0.1f) * 5f);
                alpha = MakeAlpha(t);
                rotation = -(t * 0.3f);
                scale = t;
            }
            else if (transition < 0.5f)
            {
                scale = 1f;
            }
            else if (transition < 0.7f)
            {
                scale = (Clamp01((transition - 0.5f) * 5f) * 0.25f) + 1f;
            }
        }

        return new MainMenuDecor(scale, rotation, alpha, Draw: alpha > 0f);
    }

    /// <summary>
    /// Right transition twin <c>DAT_0089d8a4</c> (symbol-bracket-02), same anchor,
    /// drawn only while 0.1 &lt;= transition &lt; 0.9 on the dest == 0x0c side.
    /// </summary>
    private static MainMenuDecor MainMenuRightDecorTwin(float transition)
    {
        if (transition >= 1f || transition < 0.1f)
        {
            return default;
        }

        if (transition < 0.3f)
        {
            float t = Clamp01((transition - 0.1f) * 5f);
            return new MainMenuDecor(t, -(t * 0.3f), MakeAlpha(t), Draw: true);
        }

        if (transition < 0.7f)
        {
            return new MainMenuDecor(1f, 0f, 1f, Draw: true);
        }

        if (transition < 0.9f)
        {
            float t = 1f - Clamp01((transition - 0.7f) * 5f);
            return new MainMenuDecor(t, -(t * 0.3f), MakeAlpha(t), Draw: true);
        }

        return default;
    }

    private void DrawMainMenuDecor(Texture2D texture, Vector2 body, Vector2 shadow, MainMenuDecor decor)
    {
        if (!decor.Draw || decor.Alpha <= 0f)
        {
            return;
        }

        var size = new Vector2(texture.GetWidth(), texture.GetHeight());
        // Shadow first, at scale * 1.05 (_DAT_005db4ac) and the same rotation. Its
        // packed colour is (alpha * 0x3f & 0xff00) << 0x10, i.e. ShadowTint scaled
        // by the decoration's own alpha.
        DrawCenteredRotated(
            texture,
            shadow,
            size * (decor.Scale * ShadowScaleBoost),
            decor.Rotation,
            new Color(ShadowTint.R, ShadowTint.G, ShadowTint.B, ShadowTint.A * decor.Alpha));
        DrawCenteredRotated(
            texture,
            body,
            size * decor.Scale,
            decor.Rotation,
            new Color(BracketTint.R, BracketTint.G, BracketTint.B, BracketTint.A * decor.Alpha));
    }

    private void DrawMainMenu()
    {
        float transition = MainMenuTransition;

        // CFEPMain__Render's page fade, computed once at 0x00462D5x as
        // local_68 = (transition - 0.75) * 4.0 and then clamped at every use:
        // 0.75 @_DAT_005d8bc4, 4.0 @_DAT_005d85bc, both verified in the pristine
        // specimen. It drives the right chrome strips, the language row, every
        // menu label and the version string.
        float fade = Clamp01((transition - 0.75f) * 4f);

        // The selection icon (and, on the literal reading of the same block, the
        // selected row's highlight box) fade on their own later window,
        // clamp((transition - 0.8) * 5): 0.8 @_DAT_005d85f8, 5.0 @_DAT_005db4b8.
        //
        // INFERRED OPERAND, marked because it matters: the highlight box's driver
        // decompiles as an uninitialised stack float rather than as `transition`
        // itself. `(x - 0.8) * 5` is the same expression the icon block uses a few
        // hundred bytes later, so `transition` is the reading taken here, but the
        // operand identity is not proven and both candidates differ only inside
        // 0.75..0.8.
        float iconFade = Clamp01((transition - 0.8f) * 5f);

        SelectSceneSection("Main.Background");
        DrawMainUnderlay(transition);

        // The faint crosshair guides. FEP_DEVSELECT and FEP_LEVEL_SELECT have drawn
        // these since the font22 work; FEP_MAIN never did, and retail draws them on
        // all three. Counting exact (50,51,72) on the pristine -skipfmv main-menu
        // capture: 618 px, of which 370 are the column x=123 and 248 are the row
        // y=180. Ours held 1.
        //
        // KNOWN RESIDUAL, recorded rather than fudged: retail's guide is NOT an
        // opaque fill, it is a constant ADDITION. At (123,300) the -skipfmv capture
        // reads (50,51,72) over a (23,23,48) fill — delta (+27,+28,+24) — and the
        // no-skipfmv capture reads (64,68,100) over a (39,43,80) underlay at the
        // same pixel — delta (+25,+25,+20). An opaque (50,51,72) is exact on the
        // first and 14 levels low on the second. All three pages draw it opaquely
        // today, so this residual is shared and is not introduced here; closing it
        // needs a per-pixel composite of the guide against the live underlay, which
        // this canvas cannot express as a blend mode. See DrawMainUnderlay.
        //
        // UNGATED, and that is measured rather than assumed: the guides are drawn
        // by the COMMON page (FrontEnd.cpp:1314 renders it with the raw trans and
        // FEP_NONE), not by CFEPMain, and retail's t = 14 ms frame already carries
        // the full-height x = 123 column and the full-width y = 180 row while
        // every CFEPMain element is still absent.
        SelectSceneSection("Main.Guides");
        DrawRect(new Rect2(123f, 0f, 1f, DesignHeight), DevSelectGuide);
        DrawRect(new Rect2(0f, 180f, DesignWidth, 1f), DevSelectGuide);

        // DAT_0089D7F0 Forseti writing chrome. Y is CFEPMain::Render 0x00462D46:
        // 175 - fmod(mCounter * 0.3, 350), then +350 / +700. Cold BSS counter
        // is 0, which is the three settled tiles. Colour at 0x00462DE4 is
        // RetailMainMenuWritingColor: settled (255*63)<<16 | 0x00FFFFFF is
        // 0x3EFFFFFF, which is not capture ChromeTint 0x3E7F7F7F, so this
        // draw keeps ChromeTint and does not call SubmittedColor. Z/X at
        // 0x00462DFF is RetailMainMenuWritingZ: three tiles push
        // 0x3F666666 then dest 458. That leftover is Z, not scale, so the
        // draw keeps scale 1.0 and TileX and does not treat the dword as
        // a 29% title-logo. Not a sheen. ChromeTint stays put.
        SelectSceneSection("Main.Writing");
        var chromeTint = new Color(ChromeTint.R, ChromeTint.G, ChromeTint.B, ChromeTint.A * fade);
        float writingCounter = RetailMainMenuWritingScroll.ImageInitialCounter;
        DrawSurfaceCentered(
            _forsetiWritingLarge,
            RetailMainMenuWritingScroll.TileX,
            RetailMainMenuWritingScroll.TileY(writingCounter, 0),
            1f,
            1f,
            chromeTint);
        DrawSurfaceCentered(
            _forsetiWritingLarge,
            RetailMainMenuWritingScroll.TileX,
            RetailMainMenuWritingScroll.TileY(writingCounter, 1),
            1f,
            1f,
            chromeTint);
        DrawSurfaceCentered(
            _forsetiWritingLarge,
            RetailMainMenuWritingScroll.TileX,
            RetailMainMenuWritingScroll.TileY(writingCounter, 2),
            1f,
            1f,
            chromeTint);

        SelectSceneSection("Main.Language");
        DrawLanguageSelector(fade);

        // The selector bar is drawn BEFORE every row, not interleaved into the
        // row loop. Retail's order is not ambiguous: the bar is frame 3000
        // draw 11 and the fourteen row draws are 12..25, so the bar is under all
        // of them. Interleaved, it was emitted after rows 0..k-1 for a selection
        // at index k, and because the bar is 32 tall on a 20 pitch it reaches
        // 4px into the row above (rowY-16..rowY-12 against that row's glyph box
        // ending at rowY-12). That washed the bottom 4px of the previous label
        // with the bar's 49%-alpha black on every selection except row 0 — which
        // is exactly why nothing caught it: the settled capture selects row 0.
        SelectSceneSection("Main.Selector");
        DrawMainMenuSelectorBar(iconFade);

        for (int index = 0; index < _session.Items.Count; index++)
        {
            SelectSceneSection($"Main.Row{index}");
            RetailFrontendMenuItem item = _session.Items[index];
            // RetailMainMenuRowY: [esp+0x10] seeds 268 / index
            // -1. Nonzero [0x0083D990] overwrites 304 / index 0.
            // Dest Y keeps rowY - 8. Do not invent dest Y.
            // RetailMainMenuLanguagePitch: language fall-through
            // fld / fadd 36.0 at 0x00463647, then the shared
            // tail. Reached from 0x004634EE and after 0x0046363B.
            // Next slot is NonzeroSlotY. Dest Y keeps rowY - 8.
            // Do not invent dest from 36.0 or the nearby 284 push.
            float rowY = RetailMainMenuRowY.NonzeroSlotY + (index * MenuPitch);
            bool selected = index == _session.SelectedMainIndex;
            // Draw the string as authored. english.json holds "Continue Game" /
            // "Load Game" in mixed case and retail renders them that way.
            // Font13PS cells are 16px, so scale 1.0 gives the retail 20px pitch.
            string label = SceneText(_menuText[item.Kind]);
            const float textScale = 1f;
            float textWidth = MeasureText(label, textScale);
            // RetailMainMenuLabelDest: dest X is the measure
            // sibling (219 minus half cx), not a dest immediate.
            // Dest Y keeps rowY - 8. Do not invent dest or a
            // 2px kerning hack.
            var textPos = new Vector2(
                RetailMainMenuLabelDest.DestX(textWidth),
                rowY - 8f);

            if (fade <= 0f)
            {
                continue;
            }

            // RetailMainMenuLabelText: the other CFEPMain::Render
            // DrawTextDynamic at 0x0046316F. Dest is ebx / [esp+0x24],
            // not immediates. 0x0046315A leftover is Z, not writing
            // chrome and not the selector bar. Leftover stack args
            // 10 / 9 / 8 stay unused. Font slot push 1. Scales stay
            // 1.0. Colour stays LabelColor. Dest stays MeasureText.
            // Cite-fix: cmp ebx, 0x3E8 is 0x00465771; 0x00465777 is
            // mov word [eax], 0. Do not invent dest, wrap, fade,
            // sheen, or a 2px kerning hack.
            Color textColor = RetailColor(RetailMainMenuLabelColor.SubmittedColor(
                selected,
                item.IsAvailable,
                RetailMainMenuLabelColor.ImageSettledFadeByte));
            DrawText(label, textPos, textScale, new Color(textColor, textColor.A * fade));
        }

        // Shadows (offset bases; GetShadowOffset* ≈ 0 settled), then bodies. Order
        // is the shipped order: left decoration, its transition twin, right
        // decoration, its transition twin, then the selection icon. At transition
        // >= 1 every state below collapses to the previous constants — scale 1.25,
        // rotation 0, alpha 1, twins not drawn — so the settled frame is unchanged
        // by this whole block.
        // THE SHADOW OFFSETS ARE ANIMATED. Recovered 2026-07-27 from retail's own
        // draw calls over 3,756 settled frames of the A2 main-menu log and
        // re-verified in the main loop on seven frames, two of them outside the
        // reported range. The law, its evidence, its dt-driven clock and its one
        // soft term are all in RetailFrontendDecorShadow; only the wiring is here.
        //
        // The literals this replaces — (224,349) and (462,365), i.e. offsets
        // (+5,+5) and (+5,+10) — are EXACTLY the centre of the measured ellipse,
        // so they were retail's law evaluated at its time-mean. Nothing about
        // them was wrong-signed; the oscillation around them was simply absent.
        // The BODY anchors (219,344) and (457,355) are measured-exact and are
        // untouched.
        var leftShadow = RetailFrontendDecorShadow.LeftArcOffsetAtPhase(
            RetailFrontendDecorShadow.PhaseAtSeconds(_animationSeconds));
        SelectSceneSection("Main.Decoration");
        var sharedShadow = RetailFrontendDecorShadow.OffsetAtPhase(
            RetailFrontendDecorShadow.PhaseAtSeconds(_animationSeconds));
        var leftArcBody = new Vector2(219f, 344f);
        var rightArcBody = new Vector2(457f, 355f);
        Vector2 leftArcShadow = leftArcBody + new Vector2((float)leftShadow.X, (float)leftShadow.Y);
        Vector2 rightArcShadow = rightArcBody + new Vector2((float)sharedShadow.X, (float)sharedShadow.Y);

        DrawMainMenuDecor(
            _titleBracket01,
            leftArcBody,
            leftArcShadow,
            MainMenuLeftDecor(transition));
        // Colour at 0x00463873 is RetailMainMenuLeftDecorShadow: DAT_0089D894
        // *63 alpha pack, dest fadd 224/349, z push 0x3EB33333 (0.35) not
        // scale. Settled 255 submits 0x3E000000, which is this ShadowTint,
        // so the draw keeps ShadowTint and does not call SubmittedColor.
        // Dest is the left-arc pair (219+5, 344+5), not right 462/365.
        // Both dest helpers land on 0x00468730. The 224/349 addends are
        // the already-shipped ellipse centre — do not redo
        // RetailFrontendDecorShadow. Colour at 0x004638B7 is
        // RetailMainMenuLeftDecorOverlay: DAT_0089D894 not/and/xor pack,
        // dest immediates 219/344, z push 0x3E99999A (0.3) not scale.
        // Settled 255 submits 0xFEFFFFFF, which is not this BracketTint
        // 0xFE7F7F7F, so the draw keeps BracketTint and does not call
        // SubmittedColor. Dest is the left-arc body, not right. Not the
        // 0x00463E8D twin gate (that is D8A4). Not a sheen (that is
        // 0x00464343 / TitleLogoReflectionLayer). Not a 29% title-logo
        // scale. ChromeTint and ShadowTint stay put. Do not redo
        // 0x00463873, 0x00463D1F, 0x00463D63, 0x00463F3F, or 0x00463F83.
        DrawMainMenuDecor(
            _titleBracket02,
            leftArcBody,
            leftArcShadow,
            MainMenuLeftDecorTwin(transition));
        // Colour at 0x00463A8F is RetailMainMenuLeftTwinShadow: DAT_0089D898
        // *63 alpha pack, dest fadd 224/349, z push 0x3EB33333 (0.35) not
        // scale. Settled 255 submits 0x3E000000, which is this ShadowTint,
        // so the draw keeps ShadowTint and does not call SubmittedColor.
        // Dest is the leftover left-twin pair (219+5, 344+5), not
        // DAT_0089D894 primary and not right 462/365. Both dest helpers
        // land on 0x00468730. The 224/349 addends are the already-shipped
        // ellipse centre — do not redo RetailFrontendDecorShadow. Colour
        // at 0x00463AD3 is RetailMainMenuLeftTwinOverlay: DAT_0089D898
        // not/and/xor pack, dest immediates 219/344, z push 0x3E99999A
        // (0.3) not scale. Settled 255 submits 0xFEFFFFFF, which is not
        // this BracketTint 0xFE7F7F7F, so the draw keeps BracketTint and
        // does not call SubmittedColor. Dest is the leftover left-twin
        // body, not DAT_0089D894 primary and not right. Not a sheen.
        // Not a 29% title-logo scale. ChromeTint and ShadowTint stay
        // put. Do not redo 0x00463873, 0x004638B7, 0x00463A8F,
        // 0x00463D1F, 0x00463D63, 0x00463F3F, or 0x00463F83.
        DrawMainMenuDecor(
            _symbolBracket01,
            rightArcBody,
            rightArcShadow,
            MainMenuRightDecor(transition));
        DrawMainMenuDecor(
            _symbolBracket02,
            rightArcBody,
            rightArcShadow,
            MainMenuRightDecorTwin(transition));
        // Colour at 0x00463D1F is RetailMainMenuRightDecorShadow: DAT_0089D8A0
        // *63 alpha pack, dest fadd 462/365, z push 0x3EB33333 (0.35) not
        // scale. Settled 255 submits 0x3E000000, which is this ShadowTint,
        // so the draw keeps ShadowTint and does not call SubmittedColor.
        // Dest is the right-arc pair, not left. Not the 0x00463E8D twin
        // gate (that is D8A4). The 462/365 addends are the already-shipped
        // ellipse centre — do not redo RetailFrontendDecorShadow. Not a
        // sheen (that is 0x00464343 / TitleLogoReflectionLayer). Not a
        // 29% title-logo scale. ChromeTint and BracketTint stay put. Do
        // not redo 0x00463F3F or 0x00463F83.
        // Colour at 0x00463D63 is RetailMainMenuRightDecorOverlay:
        // DAT_0089D8A0 not/and/xor pack, dest immediates 457/355, z push
        // 0x3E99999A (0.3) not scale. Settled 255 submits 0xFEFFFFFF,
        // which is not this BracketTint 0xFE7F7F7F, so the draw keeps
        // BracketTint and does not call SubmittedColor. Dest is the
        // right-arc body, not left. Not the 0x00463E8D twin gate (that
        // is D8A4). Not a sheen. Not a 29% title-logo scale. ChromeTint
        // and ShadowTint stay put. Do not redo 0x00463D1F.
        // Colour at 0x00463F3F is RetailMainMenuRightTwinShadow: DAT_0089D8A4
        // *63 alpha pack, dest fadd 462/365, z push 0x3EB33333 (0.35) not
        // scale. Settled 255 submits 0x3E000000, which is this ShadowTint,
        // so the draw keeps ShadowTint and does not call SubmittedColor.
        // Same 0x00463E8D gate as the body overlay; settled frames skip.
        // The 462/365 addends are the already-shipped ellipse centre —
        // do not redo RetailFrontendDecorShadow. Not a sheen (that is
        // 0x00464343 / TitleLogoReflectionLayer). Not a 29% title-logo
        // scale. ChromeTint and BracketTint stay put.
        // Colour at 0x00463F83 is RetailMainMenuRightTwinOverlay: DAT_0089D8A4
        // mode-4 at (457,355), z push 0x3E99999A (0.3) not scale. Settled 255
        // submits 0xFEFFFFFF, which is not this BracketTint 0xFE7F7F7F, so
        // the draw keeps BracketTint and does not call SubmittedColor. Gate
        // 0x00463E8D skips the call once transition >= 0.9; settled frames
        // never issue it. Not a sheen (that is 0x00464343 /
        // TitleLogoReflectionLayer). Not a 29% title-logo scale. ChromeTint
        // and ShadowTint stay put.

        SelectSceneSection("Main.SelectedIcon");
        if (iconFade > 0f)
        {
            Texture2D icon = _menuIcons[_session.SelectedMainIndex];
            Color iconTint = _session.SelectedMainItem.IsAvailable ? BracketTint : ReleasedUnavailable;
            // Pair C of the four the shadow law was recovered from: the
            // selected-row icon takes the SHARED (u,v) offset, the same vector as
            // the right arc, off the same body anchor (457,355).
            // Colour at 0x0046407C is RetailMainMenuSelectedIconShadow: settled
            // ((255<<6)-255)<<16 & 0xFF000000 is 0x3E000000, which is this
            // ShadowTint, so the draw keeps ShadowTint and does not call
            // SubmittedColor. Shadow scale stays ShadowScaleBoost (1.05).
            DrawSurfaceCentered(
                icon,
                rightArcShadow.X,
                rightArcShadow.Y,
                ShadowScaleBoost,
                ShadowScaleBoost,
                new Color(ShadowTint, ShadowTint.A * iconFade));
            // Colour at 0x004640DC is RetailMainMenuSelectedIconColor: settled
            // ((255<<8)-255)<<16 | 0x00FFFFFF is 0xFEFFFFFF, which is not
            // this BracketTint 0xFE7F7F7F (frame 3000 draw 31), so the draw
            // keeps BracketTint and does not call SubmittedColor. Body scale
            // stays 1.0; this is not a 29% scale. ChromeTint and ShadowTint
            // stay put.
            DrawSurfaceCentered(icon, 457f, 355f, 1f, 1f, new Color(iconTint, iconTint.A * iconFade));
        }

        SelectSceneSection("Main.Version");
        if (fade > 0f)
        {
            // SHADOWED, corrected 2026-07-28 from a single flat run. The version
            // string is a shadow/body PAIR like every other text run on the page:
            // frame 3000 draw 32/33 is the already-owned DrawText pair — shadow
            // on the anchor, body at anchor-(1,1), shadow RGB black carrying the
            // body's own alpha. Dest leftover at 0x004641C9 is
            // RetailMainMenuVersionOverlayZ: PLATFORM__GetWindowHeight then
            // sub 0x10, dest X push 0. That leftover is not a dest immediate.
            // 0x004641C4 push 0x3C23D70A is Z, not scale, so this draw keeps
            // VersionTint, Format, DestX, DestY(DesignHeight), and scale 1.0.
            // Font leftover is RetailMainMenuVersionOverlayFont: push 1 selects
            // FONT_SMALL / Font13PS at this+0x20, not this+0x1C. No measure
            // call on the sprintf buffer. Pre-draw leftover is
            // RetailMainMenuVersionOverlayEnable: after sprintf / add esp,10 /
            // lea edx,[esp+0x3C], 0x00464180 stores [0x00679B40]=0. The
            // 0x00465F00 reader is mov al,[0x00679B40]; ret. Widen leftover
            // is RetailMainMenuVersionOverlayWiden: after the enable-byte
            // store, push edx of that sprintf buffer and call
            // Text__AsciiToWideScratch. add esp,4 shows cdecl one-arg.
            // EAX is the wide scratch pointer. Tail leftover is
            // RetailMainMenuVersionOverlayTail: after add esp,4 the
            // three leftover pushes remain as DrawTextDynamic's last
            // three stack slots. The leftover float is past the
            // below-zero / below-quarter / below-half arms, and the
            // second leftover dword is zero so that colour arm is
            // skipped. Do not invent dest, wrap, fade, or sheen from
            // those slots. Post-draw leftover is
            // RetailMainMenuVersionOverlayFlags:
            // after DrawTextDynamic, 0x004641FC/203/20A store
            // [0x00679B40]=1, [0x009C68AC]=0, [0x009C690D]=1 between
            // fcom [0.0] and fnstsw. That fcom is the already-owned
            // title-logo shadow clamp, not a version fade. The MeasureText
            // residual stays open; do not invent a fade or a kerning hack.
            DrawText(
                RetailMainMenuVersionOverlayWiden.Widen(
                    RetailMainMenuVersionOverlay.Format(
                        RetailMainMenuVersionOverlay.ImageInitialMajor,
                        RetailMainMenuVersionOverlay.ImageInitialMinor)),
                new Vector2(
                    RetailMainMenuVersionOverlayZ.DestX,
                    RetailMainMenuVersionOverlayZ.DestY((int)DesignHeight)),
                1f,
                new Color(VersionTint, VersionTint.A * fade));
        }

        // DAT_0089d7fc reflection sheen — RESTORED 2026-07-27 from the shipped
        // bytes, as a separate additive CanvasItem clipped to the logo's own
        // alpha-tested footprint. It is NOT drawn here; see
        // TitleLogoReflectionLayer for the disassembly, the ONE/ONE blend, the
        // 0xff7e7e7e tint, the depth-stamp mask and the two measured constants.
        //
        // The 2026-07-26 deletion rationale is kept below because reason (1) was
        // right and is the defect this fixes.
        //
        // Two 512x128 quads were drawn at scale (1,2) centred on (321,120) and
        // (833,120), covering x65..640, y-8..248 of the stage. Two independent
        // measurements say retail does not put that there:
        //
        // 1. It was not additive. The helper set CanvasItem.Material for the
        //    duration of one call, but a CanvasItem's material
        //    applies to the whole item, not to a bracketed span of _Draw commands,
        //    and the trailing `Material = null` leaves the item non-additive at
        //    submit time. The proof is in the pixels, not in that reading: our
        //    captured main menu held (26,24,33) at (320,0) where the page fill is
        //    (23,23,48). Additive blending cannot LOWER a channel by 15.
        // 2. Retail shows no excess there: fitting fill + gain x FEBack128 over
        //    the proven-underlay mask and splitting the residual by this footprint
        //    gives mean -0.43..+0.84 (|mean| 1.5..3.4) over 84,912 pixels INSIDE
        //    it against +0.27..+1.45 (|mean| 1.8..3.1) over 137,771 outside, on 13
        //    frames.
        //
        //    THE STRENGTH OF (2) IS BOUNDED, and an earlier draft of this comment
        //    overstated it as "retail has no such layer". An independent
        //    adversarial pass is right that a mean residual mostly constrains
        //    the DC component: a reflection texture that is near zero-mean
        //    over the footprint can
        //    carry a real gain while moving the mean by nothing, and if it
        //    correlates with FEBack128 the FEBack fit absorbs part of it. What (2)
        //    supports is a DC bound of order one level, not absence. The
        //    projection of the residual onto the reflection texture orthogonalised
        //    to FEBack128 was NOT computed and would settle it.
        //
        //    The deletion does not rest on (2). It rests on (1): what was drawn
        //    here was provably not the blend it claimed to be.
        //
        // WITHDRAWN 2026-07-27: (2)'s footprint was the whole 512x256 rectangle,
        // but the bytes put the layer inside the logo's alpha>=8 texels only. Run
        // the same regression on that footprint and the gain is 0.488/0.489/0.487
        // against 0.025/0.030/0.038 outside it. A rectangle-wide mean could not
        // have seen that, which is exactly the bound the comment already conceded.
        // Pair D of the four the shadow law was recovered from. Retail's title
        // body is (64,2)-(576,258), centre (320,130) — this anchor exactly — and
        // its shadow takes the SHARED (u,v) offset off it, at the same 1.05 scale.
        // The (325,140) that stood here is that offset's time-mean.
        // Colour at 0x0046424F is RetailMainMenuTitleLogoShadow: settled
        // (255*63)<<16 & 0xFF000000 is 0x3E000000, which is this ShadowTint,
        // so the draw keeps ShadowTint and does not call SubmittedColor.
        // dest==0x0c at 0x0046423D forces ESI=255. Body scale stays 1.0;
        // this is not a 29% scale. Body pack stays TitleLogoTint.
        // DAT_0089D88C leftover at 0x00464251 is
        // RetailMainMenuTitleLogoShadowZ: same Title2, then push
        // 0x3DCCCCCD. That leftover is Z, not scale. Dest is
        // GetShadowOffsetY + [0x005D8C20] and GetShadowOffsetX +
        // [0x005DB4A8], not RenderSurface immediates, so this draw
        // keeps ShadowTint, ShadowScaleBoost, DestX, DestY, and
        // sharedShadow. Nearby 0x3F866666 is already
        // ShadowScaleBoost. Not a sheen.
        // DAT_0089D88C at 0x004642CE is RetailMainMenuTitleLogoZ:
        // FrontEnd\v3\FE_BEA_Title2.tga via ebp+0x12C, then push
        // 0x3F7FBE77, dest Y 130, dest X 320. That leftover is Z, not
        // scale, so this draw keeps TitleLogoTint, scale 1.0, DestX,
        // and DestY and does not treat the dword as a 29% title-logo.
        // Nearby 0x3F866666 is already ShadowScaleBoost. Not a sheen.
        SelectSceneSection("Main.TitleLogo");
        DrawSurfaceCentered(
            _titleLogo,
            RetailMainMenuTitleLogoZ.DestX + (float)sharedShadow.X,
            RetailMainMenuTitleLogoZ.DestY + (float)sharedShadow.Y,
            ShadowScaleBoost,
            ShadowScaleBoost,
            ShadowTint);
        DrawSurfaceCentered(
            _titleLogo,
            RetailMainMenuTitleLogoZ.DestX,
            RetailMainMenuTitleLogoZ.DestY,
            1f,
            1f,
            TitleLogoTint);
    }

    /// <summary>
    /// The selected row's highlight bar — retail's frame 3000 draw 11, emitted
    /// before all fourteen row draws (12..25) rather than between them.
    ///
    /// <para>WIDTH: the label's own ink width plus exactly 31. MEASURED on two
    /// selected rows by scanning every 256x32 selector-bar draw in the A3 run
    /// (<c>G:\bea-frontend-pages\A3-options-20260727-205107\d3d9-draws.log</c>,
    /// frames 1..2600, 1,165 draws), which returns exactly TWO distinct
    /// rectangles because the run hovers Options on its way into that page:</para>
    ///
    /// <code>
    ///   New Game selected  (160.5,288)-(277.5,320)  117 x 32  frames  754..1830
    ///   Options  selected  (173.0,388)-(265.0,420)   92 x 32  frames 1831..1918
    /// </code>
    ///
    /// <para>Both are centred on x = 219 and on their own row centre, both are 32
    /// tall, and both are ink + 31: 86+31 = 117 and 61+31 = 92. Two rows whose
    /// labels differ by 25px give the same constant, so the width tracks the
    /// label and 31 is the padding.</para>
    ///
    /// <para>HEIGHT 32, MEASURED, not 20: draw 11 is a 256x32 DXT2 at u,v 0..1,
    /// diffuse 0x7E000000, identical on frames 3500 and 4000 of the same run.
    /// <c>rowY - 16</c> lands the quad at y 288 for row 0; a D3D9 quad spanning
    /// [288,320) covers pixel rows 288..319, which is what a Godot Rect2 at
    /// y = 288, h = 32 covers.</para>
    ///
    /// <para>DAT_0089D89C at 0x00462FED is RetailMainMenuSelectorBarZ:
    /// FrontEnd\v3\FE_BEA_title_text_box.tga via ebp+0x13C, then push
    /// 0x3EA8F5C3 and dest 219. That leftover is Z, not scale, so this
    /// draw keeps _titleTextBox, the measured ink+31 width, and DestX
    /// and does not treat the dword as a 29% title-logo. Colour at
    /// 0x00462FB9 stays RetailMainMenuSelectorBarColor. Not a sheen.</para>
    /// </summary>
    private void DrawMainMenuSelectorBar(float iconFade)
    {
        if (iconFade <= 0f)
        {
            return;
        }

        int index = _session.SelectedMainIndex;
        if (index < 0 || index >= _session.Items.Count)
        {
            return;
        }

        float rowY = MenuStartY + (index * MenuPitch);
        float boxWidth = MeasureText(_menuText[_session.Items[index].Kind], 1f) + 31f;

        // DAT_0089D89C at 0x00462FED is RetailMainMenuSelectorBarZ.
        // 0x3EA8F5C3 leftover is Z, not scale. Dest X is this DestX.
        DrawTextureRect(
            _titleTextBox,
            new Rect2(
                RetailMainMenuSelectorBarZ.DestX - (boxWidth * 0.5f),
                rowY - 16f,
                boxWidth,
                32f),
            false,
            new Color(
                RetailColor(RetailMainMenuSelectorBarColor.SubmittedColor(
                    RetailMainMenuSelectorBarColor.ImageSettledFadeByte)),
                HighlightTint.A * iconFade));
    }

    /// <summary>
    /// The language selector sitting directly above the menu column.
    ///
    /// GEOMETRY REPLACED 2026-07-28 by retail's own quads. The values below were
    /// previously read off a 640x480 PNG by hunting pixels that differ from the
    /// flat (23,23,48) background — left chevron x 144..165 y 254..283, flag
    /// x 177..261 y 252..284, right chevron x 273..294 y 253..282. That is ink
    /// measurement, and it was close, but it could not recover the quads and it
    /// disagreed with itself: it put the two chevrons on different rows (254 and
    /// 253) and gave them different heights from the flag, which no released
    /// layout does.
    ///
    /// Retail's quads, main-menu-settled.csv frame 3000, confirmed identical on
    /// frame 4000 and on all 250 frames of main-menu-reveal-frames-613-900.csv:
    ///
    ///   draw  6  flag           (177.4,252.0)-(260.6,284.0)   83.2 x 32.0
    ///   draw  7  left chevron   (128.4,242.4)-(179.6,293.6)   51.2 x 51.2
    ///   draw  9  right chevron  (258.4,242.4)-(309.6,293.6)   51.2 x 51.2
    ///
    /// QUAD IS NOT INK, AND THAT DISTINCTION IS THE WHOLE FINDING HERE. Read as
    /// appearance, those rectangles say the left chevron's right edge (179.6)
    /// runs 2.2px PAST the flag's left edge (177.4) — that the chevron overlaps
    /// the flag. It does not. The d3d9 proxy does not wrap textures, so the
    /// inventory carries quad, format and dimensions and never ink extent; the
    /// two prior write-ups both stopped at "blocked on texture contents".
    ///
    /// It is not blocked. The texture is on this machine. FE_Arrow.tga decodes
    /// (Assets/Frontend/fe-arrow.texture.aya, a 64x64 DXT2 DDS, which matches the
    /// inventory's tex0 exactly) to a right-pointing chevron whose alpha is a
    /// hard 0-or-255 with ink bounded by texels (16,12)-(46,52) — 30 x 40 inside
    /// 64 x 64, i.e. u 0.25..0.71875, v 0.1875..0.8125. The draws sample u,v
    /// 0..1, so composing sprite with quad gives the ink:
    ///
    ///   left chevron ink   (142.8,252.0)-(166.8,284.0)   24.0 x 32.0
    ///   flag               (177.4,252.0)-(260.6,284.0)   83.2 x 32.0
    ///   right chevron ink  (271.2,252.0)-(295.2,284.0)   24.0 x 32.0
    ///
    /// So retail leaves a 10.6px CLEAR GAP on each side, and all three elements
    /// are exactly 32 tall on exactly the same rows, y 252..284. The overlap was
    /// entirely in the sprite's transparent margin.
    ///
    /// The left chevron is the MIRRORED draw, and the composition proves it
    /// rather than assuming it: the ink box is off-centre in its texture (16 left
    /// margin against 18 right), so mirroring shifts it. Mirrored, the row is
    /// symmetric about x = 219.0 to 0.0 — 219-142.8 = 76.2 = 295.2-219 and
    /// 219-166.8 = 52.2 = 271.2-219. Unmirrored it would miss by 1.6px. That
    /// symmetry also independently re-confirms MenuColumnX as a centre anchor.
    ///
    /// Draws 8 and 10 are a SECOND COPY of each chevron at exactly twice the
    /// size, concentric on the same centres (154,268) and (284,268). They are not
    /// drawn here because they cannot produce a pixel: their diffuse is
    /// 0x007F7F7F in 500 of 500 sampled rows, stage-0 ALPHAOP is
    /// MODULATE(TEXTURE, DIFFUSE) so the result alpha is zero, and ALPHATEST is
    /// enabled at GREATEREQUAL ref 8, which rejects every texel before blending.
    /// They are real draw calls and they are no-ops; see the diff note for why
    /// that matters to any "39 of 39" claim.
    ///
    /// <paramref name="fade"/> is CFEPMain__Render's page fade. The language row is
    /// drawn inside the same loop as the menu labels and every one of its packed
    /// colours is multiplied by the same alpha byte, so it reveals with them. The
    /// selected-row sine at 0x0046319E is pinned by RetailMainMenuLanguageSine;
    /// session cannot hold this+0x08=-1, so this draw does not light that pack.
    /// Chevron visibility is RetailMainMenuLanguageBlink: fistp(mCounter) signed
    /// remainder 64, draw while below 50. Cold BSS 0 draws. The 2x copies stay
    /// no-ops. Chevron colour at 0x0046336B / 0x004634F4 is
    /// RetailMainMenuLanguageChevronColor: settled unselected submits
    /// 0x3EFFFFFF, which is not capture ChromeTint 0x3E7F7F7F, so this
    /// draw keeps ChromeTint and does not call SubmittedColor.
    /// </summary>
    private void DrawLanguageSelector(float fade)
    {
        if (_languageFlags.Length == 0 || fade <= 0f)
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
            LanguageRowRect(RetailFrontendLanguageRow.Flag),
            false,
            new Color(FlagTint, FlagTint.A * fade));

        // Draw the WHOLE 64x64 texture into retail's whole 51.2x51.2 quad, the
        // way retail does, rather than sourcing the ink sub-rect into an ink-sized
        // destination. Both put the ink in the same place; this one keeps our
        // constants equal to the inventory's, so the next reader diffs numbers
        // against the CSV instead of re-deriving the margin. It also samples the
        // sprite's transparent border the way retail's sampler does, which is
        // where the two differ by a texel of edge feathering.
        var arrowTint = new Color(ChromeTint, ChromeTint.A * fade);
        if (RetailMainMenuLanguageBlink.ShouldDraw(
                RetailMainMenuLanguageBlink.ImageInitialCounter,
                RetailMainMenuLanguageBlink.ImageInitialTimer))
        {
            DrawTextureRect(
                _feArrow,
                LanguageRowRect(RetailFrontendLanguageRow.LeftChevron),
                false,
                arrowTint);
            DrawTextureRect(
                _feArrow,
                LanguageRowRect(RetailFrontendLanguageRow.RightChevron),
                false,
                arrowTint);
        }
    }

    /// <summary>
    /// Retail's language-row quad as a Godot rect.
    ///
    /// <para><b>A negative width flips IN PLACE. It does not move the rect.</b>
    /// Godot turns a negative <c>Rect2</c> size into a flip flag and the absolute
    /// size, leaving <c>position</c> as the LEFT edge either way — so the
    /// position passed here is always <c>quad.X</c>, never <c>quad.Right</c>.
    /// This is not a style note. The code this replaces read
    /// <c>Rect2(166, 254, -22, 30)</c> intending x 144..166, and it rendered at
    /// x 166..188 — 22px right of where it was meant to be, which put the left
    /// chevron ON TOP of the flag. Measured on our own captured frame
    /// (local-lab/godot-captures/gaterepair-head-mainmenu/mainmenu-t008000ms.png,
    /// columns above threshold in the row band): retail shows three separated
    /// runs 144..165 / 178..260 / 273..294, ours showed two, 167..261 and
    /// 274..293, with nothing at all where retail's left chevron lives.</para>
    /// </summary>
    private static Rect2 LanguageRowRect(RetailFrontendLanguageRow.Quad quad) =>
        new(
            (float)quad.X,
            (float)quad.Y,
            quad.Mirrored ? (float)-quad.Width : (float)quad.Width,
            (float)quad.Height);

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
    /// measurably NOT additive (see DrawMainMenu's reflection-streak note), and a
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
        if (_paintingPart is not null) return (1f, Vector2.Zero);
        float scale = Mathf.Min(Size.X / DesignWidth, Size.Y / DesignHeight);
        return (
            scale,
            new Vector2(
                (Size.X - (DesignWidth * scale)) * 0.5f,
                (Size.Y - (DesignHeight * scale)) * 0.5f));
    }

    private void UpdateTitleLogoReflection()
    {
        if (_titleLogoReflection is not TitleLogoReflectionLayer layer)
        {
            return;
        }

        bool visible = _session.Screen == RetailFrontendScreen.MainMenu;
        layer.Visible = visible;
        if (!visible)
        {
            return;
        }

        if (!_nativeTextures.TryGetValue("MainMenu/TitleLogo/Body", out RetailTextureRect? logo)) return;
        Vector2 ratio = logo.Size / new Vector2(TitleLogoReflectionLayer.LogoWidth, TitleLogoReflectionLayer.LogoHeight);
        var sourceToLogo = new Transform2D(
            new Vector2(ratio.X, 0f), new Vector2(0f, ratio.Y),
            -new Vector2(TitleLogoReflectionLayer.LogoLeft, TitleLogoReflectionLayer.LogoTop) * ratio);
        layer.Transform = GetGlobalTransformWithCanvas().AffineInverse() * logo.GetGlobalTransformWithCanvas() * sourceToLogo;
        layer.SetScroll(_feBackSeconds);
    }

    private int MainMenuIndexAt(Vector2 designPosition)
    {
        if (_stage is null) return -1;
        Vector2 canvasPoint = _stage.GetGlobalTransformWithCanvas() * designPosition;
        for (int index = 0; index < _session.Items.Count; index++)
        {
            MainMenuReferencePart row = _sceneParts[$"Main.Row{index}"];
            Vector2 local = row.GetGlobalTransformWithCanvas().AffineInverse() * canvasPoint;
            if (new Rect2(Vector2.Zero, row.Size).HasPoint(local)) return index;
        }
        return -1;
    }

    private void UpdateNativeTextures()
    {
        float fade = Clamp01((MainMenuTransition - 0.75f) * 4f);
        float iconFade = Clamp01((MainMenuTransition - 0.8f) * 5f);
        for (int index = 0; index < 3; index++)
            BindNativeTexture($"MainMenu/Writing/Tile{index}", _forsetiWritingLarge, fade);
        int language = Math.Clamp((int)_session.Language, 0, _languageFlags.Length - 1);
        BindNativeTexture("MainMenu/Language/Flag", _languageFlags[language], fade);
        bool arrows = RetailMainMenuLanguageBlink.ShouldDraw(
            RetailMainMenuLanguageBlink.ImageInitialCounter, RetailMainMenuLanguageBlink.ImageInitialTimer);
        BindNativeTexture("MainMenu/Language/LeftChevron", _feArrow, arrows ? fade : 0f);
        BindNativeTexture("MainMenu/Language/RightChevron", _feArrow, arrows ? fade : 0f);
        Texture2D icon = _menuIcons[_session.SelectedMainIndex];
        BindNativeTexture("MainMenu/SelectedIcon/ShadowMotion/Shadow", icon, iconFade);
        BindNativeTexture("MainMenu/SelectedIcon/Body", icon, iconFade);
        if (!_session.SelectedMainItem.IsAvailable)
            _nativeTextures["MainMenu/SelectedIcon/Body"].SelfModulate =
                new Color(ReleasedUnavailable, ReleasedUnavailable.A * iconFade);
        BindNativeTexture("MainMenu/TitleLogo/ShadowMotion/Shadow", _titleLogo, 1f);
        BindNativeTexture("MainMenu/TitleLogo/Body", _titleLogo, 1f);
        var shadow = RetailFrontendDecorShadow.OffsetAtPhase(
            RetailFrontendDecorShadow.PhaseAtSeconds(_animationSeconds));
        Vector2 offset = new((float)shadow.X, (float)shadow.Y);
        // Animation owns only the motion wrapper. The texture's authored
        // Position/Size remain editable, and saving/reopening cannot accumulate
        // the current phase offset into the next run's baseline.
        _stage!.GetNode<Control>("MainMenu/SelectedIcon/ShadowMotion").Position = offset;
        _stage.GetNode<Control>("MainMenu/TitleLogo/ShadowMotion").Position = offset;
    }

    private void BindNativeTexture(string key, Texture2D texture, float fade)
    {
        RetailTextureRect control = _nativeTextures[key];
        control.Texture = texture;
        Color tint = _nativeTints[key];
        control.SelfModulate = new Color(tint, tint.A * fade);
    }

    private new void DrawSetTransform(Vector2 position, float rotation = 0f, Vector2? scale = null)
    {
        if (_paintingPart is null) return;
        Vector2 ratio = _paintingPart.Size / _paintingPart.SourceRect.Size;
        var authored = new Transform2D(new Vector2(ratio.X, 0f), new Vector2(0f, ratio.Y),
            -_paintingPart.SourceRect.Position * ratio);
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

    private new void DrawLine(Vector2 from, Vector2 to, Color color, float width = -1f, bool antialiased = false)
    {
        if (DrawsSceneSection) _paintingPart!.DrawLine(from, to, color, width, antialiased);
    }

    private new void DrawArc(Vector2 center, float radius, float startAngle, float endAngle, int pointCount,
        Color color, float width = -1f, bool antialiased = false)
    {
        if (DrawsSceneSection) _paintingPart!.DrawArc(center, radius, startAngle, endAngle, pointCount, color, width, antialiased);
    }

    private new void DrawPolyline(Vector2[] points, Color color, float width = -1f, bool antialiased = false)
    {
        if (DrawsSceneSection) _paintingPart!.DrawPolyline(points, color, width, antialiased);
    }    private static Color RetailColor(uint argb) => new(
        Modulate2X((argb >> 16) & 0xff),
        Modulate2X((argb >> 8) & 0xff),
        Modulate2X(argb & 0xff),
        ((argb >> 24) & 0xff) / 255f);

    private static float Modulate2X(uint channel) =>
        Math.Min(255u, (channel * 255u) >> 7) / 255f;

    /// <summary>
    /// The scrolling additive sheen CFEPMain__Render lays over the title logo —
    /// RECOVERED FROM THE SHIPPED BYTES, not fitted.
    ///
    /// <para><b>Why this exists.</b></para>
    /// The settled main menu's two worst regions, <c>title-logo</c> (41.21 % gap)
    /// and <c>bg-emblem-topright</c> (35.57 %), are largely the same 512x256 quad,
    /// and our renderer was already exonerated for it: fitted against the decoded
    /// texel our pixels give slope 1.002, intercept -0.30, rms 0.39. Retail simply
    /// puts something else there — an animated layer whose temporal std inside the
    /// opaque logo interior is ~15 while its mean is constant to +-0.6.
    ///
    /// A version of this layer was drawn until 2026-07-26 and was deleted for two
    /// stated reasons. The first was correct and is fixed here: it set
    /// <c>CanvasItem.Material</c> around a bracketed span of <c>_Draw</c> commands,
    /// but a CanvasItem's blend mode applies to the whole item, so the "additive"
    /// draw was never additive. That is why this is a SEPARATE CanvasItem. The
    /// second reason — a DC residual bound — was already withdrawn in that comment
    /// as bounding only the mean, and it does not survive: the layer is confined to
    /// the logo's own alpha footprint, where a footprint-wide mean is the wrong
    /// instrument.
    ///
    /// <para><b>What the bytes say.</b></para>
    /// Specimen <c>local-lab/safe-copy-bea-pristine/BEA.exe.original.backup</c>,
    /// sha256 <c>74154bfa…</c> (the PATCHED sibling <c>BEA.exe</c> was not read).
    /// <c>CFEPMain__Render</c> is <c>[0x00462d40, 0x0046449e)</c>; every address
    /// below is inside it. Its tail, in order:
    /// <code>
    /// 0x00464251  logo shadow: DAT_0089d88c at (325 + sin, 140 + cos), z 0.1,
    ///             scale 1.05, tint 0x3e000000
    /// 0x004642b5  SetRenderState(0x17 D3DRS_ZFUNC, 8 D3DCMP_ALWAYS)   [0x00513bc0]
    /// 0x004642ce  logo body:   DAT_0089d88c at (320, 130), z 0.99899 (0x3f7fbe77),
    ///             scale 1, tint 0xfeafcfff  (and 0xafcfff is literally
    ///             `and edx,0xffafcfff` / `or edx,0xafcfff` at 0x004642e4/f1)
    /// 0x0046431a  SetRenderState(0x17 D3DRS_ZFUNC, 4 D3DCMP_LESSEQUAL)
    /// 0x0046435d  CFrontEnd__EnableAdditiveAlpha (0x004681c0) — and this is the
    ///             whole of it: SetRenderState(0x13 SRCBLEND, 2 D3DBLEND_ONE) and
    ///             SetRenderState(0x14 DESTBLEND, 2 D3DBLEND_ONE). ONE/ONE.
    /// 0x004643aa  DAT_0089d7fc at (321 - m, 120), z 0.99799, scale (1, 2)
    /// 0x004643e7  DAT_0089d7fc at (321 - m + 512, 120), same
    /// 0x004643f4  CFrontEnd__EnableModulateAlpha (0x004681e0) — SRCBLEND 5
    ///             SRCALPHA / DESTBLEND 6 INVSRCALPHA
    /// </code>
    ///
    /// <b>The texture.</b> <c>DAT_0089d7fc</c> is loaded at <c>0x00468aa9</c> from
    /// <c>"FrontEnd\v2\FE_Reflection_map.tga"</c> (string at <c>0x0062a83c</c>) and
    /// stored to <c>[ebp+0x9c]</c> at <c>0x00468ac0</c>; the same routine stores
    /// <c>FE_BEA_Title2.tga</c> to <c>[ebp+0x12c]</c> at <c>0x00468e60</c>, and
    /// <c>0x0089d88c - 0x12c = 0x0089d760 = ebp</c>, so <c>ebp + 0x9c</c> is exactly
    /// <c>0x0089d7fc</c>. That arithmetic is the identification; the map note that
    /// carried this global as "path unknown / low confidence" is superseded.
    ///
    /// <b>The tint.</b> <c>0x00464362</c>-<c>0x00464387</c> computes
    /// <c>((a*127)&gt;&gt;8) * 0x010101 - 0x01000000</c>, i.e. <c>0xff7e7e7e</c> at
    /// alpha 255. Under ONE/ONE with stage 0 <c>MODULATE(TEXTURE, DIFFUSE)</c> the
    /// framebuffer gains <c>tex.rgb * 126/255</c>. NOTE: <see cref="RetailColor"/>'s
    /// 2x modulate does NOT apply on this path — measurement below says 0.488, not
    /// 0.988 — so the raw ratio is used.
    ///
    /// <b>The scroll.</b> <c>0x00464331</c>-<c>0x00464359</c>:
    /// <c>m = fmod(FRONTEND.mCounter * 0.6, 512)</c> and <c>x = 256 - m + 65</c>,
    /// with the second copy at <c>+512</c> under <c>D3DTADDRESS_WRAP</c>. The
    /// counter is <c>0x008a9570</c>, the float form of <c>CFrontEnd::mCounter</c>
    /// (<c>FrontEnd.cpp:597</c>): <c>GetShadowOffsetX</c> at <c>0x00468730</c> is
    /// <c>sin(counter * 0.01) * 6</c>, exactly <c>FrontEnd.cpp:1561</c>'s
    /// <c>sinf(counter / SHADOW_PERIOD) * SHADOW_RADIUS_X</c> with
    /// <c>SHADOW_PERIOD 100</c>, <c>SHADOW_RADIUS_X 6</c>.
    ///
    /// <b>The mask, which is the whole trick.</b> The logo body is drawn under
    /// <c>D3DCMP_ALWAYS</c> at z 0.99899 with <c>ZWRITEENABLE</c> and the default
    /// block's <c>ALPHATESTENABLE</c> / <c>ALPHAFUNC GREATEREQUAL</c> /
    /// <c>ALPHAREF 8</c> (d3d-default-render-state-block-2026-07-27.md §5). So it
    /// stamps depth 0.99899 over exactly its alpha&gt;=8 texels and nowhere else.
    /// ZFUNC then goes back to <c>LESSEQUAL</c> and the sheen is submitted at
    /// 0.99799 — which passes inside that stamp and fails against the page behind
    /// it. The sheen is a logo-shaped clip, not a rectangle. That is why the
    /// pedestal has equal core and 1-2 px ring intercepts, and why a spatial
    /// control outside the ink found nothing.
    ///
    /// <para><b>What is measured rather than recovered, stated plainly.</b></para>
    /// A static disassembly cannot say how fast <c>mCounter</c> advances, and
    /// nothing pins its phase at main-menu entry. Both were measured from retail
    /// pixels, on the 12 settled <c>run1</c> frames of
    /// <c>local-lab/retail-reference-pristine/nofmv-frontend-2026-07-26</c>, by
    /// regressing frame-to-frame differences onto the decoded reflection texel
    /// under the recovered model (differences, so the static page cancels and no
    /// baseline is assumed):
    /// <code>
    ///   rate  29.95 design px/s   (= 0.6 px/tick x 49.9 ticks/s)
    ///   phase 133 px at t = 1530 ms after main-menu entry
    /// </code>
    /// The gain was NOT fitted — it is <c>126/255 = 0.4941</c> from the bytes — but
    /// it was checked: least squares inside the alpha&gt;=8 footprint, on
    /// unsaturated pixels, gives R 0.4883, G 0.4887, B 0.4870. Residual rms inside
    /// the footprint drops 28.4 -> 4.3 (R), 26.6 -> 4.6 (G), 20.0 -> 7.8 (B).
    /// OUTSIDE the footprint the same regression gives gain 0.025/0.030/0.038 and
    /// moves rms by nothing (7.35 -> 7.26), which is the depth clip showing up in
    /// the pixels.
    ///
    /// The phase constant is the same class of measured anchor as
    /// <see cref="FeBackPhaseFrames"/> and carries the same caveat: retail's
    /// counter is never reset on a page change, so its value at main-menu entry
    /// depends on how long click-to-start was held.
    /// </summary>
    [Tool]
    private sealed partial class TitleLogoReflectionLayer : Node2D
    {
        // Recovered: 126/255 from the 0xff7e7e7e vertex tint under ONE/ONE.
        internal const float Gain = 126f / 255f;

        // Recovered: fmod(counter * 0.6, 512), two copies 512 apart.
        internal const float ScrollPeriodPx = 512f;

        // MEASURED (see the class remarks) — 0.6 px/tick against a counter that
        // advanced 49.9 times a second in the reference capture.
        internal const float ScrollPxPerSecond = 29.95f;

        // MEASURED — chosen so scroll(1.530 s after main-menu entry) = 133 px.
        // 133 - 29.95 * (1.530 + 1/60) = 86.68.
        internal const float ScrollPhasePx = 86.68f;

        // The logo quad: DAT_0089d88c is 512x256 drawn centred on (320, 130).
        internal const float LogoLeft = 64f;
        internal const float LogoTop = 2f;
        internal const float LogoWidth = 512f;
        internal const float LogoHeight = 256f;

        // The sheen quad: 512x128 at scale (1, 2) centred on (321 - m, 120), so it
        // spans y -8..248 and, with its +512 twin under WRAP, always covers
        // x 65..577. Screen pixel x samples texel (x - 65 + m) mod 512; screen y
        // samples texel (y + 8) / 2.
        internal const float SheenLeftAtZeroScroll = 65f;
        internal const float SheenTop = -8f;
        internal const float SheenHeight = 256f;

        private static Shader? _shader;
        private readonly ShaderMaterial _material = new();
        private Texture2D _logo = null!;

        public override void _Ready() => Material = _material;

        public void Configure(Texture2D logo, Texture2D reflection)
        {
            _logo = logo;
            _material.Shader = _shader ??= new Shader { Code = ShaderCode };
            _material.SetShaderParameter("reflection", reflection);
            _material.SetShaderParameter("gain", Gain);
        }

        /// <summary>
        /// <paramref name="frontendSeconds"/> is the same clock
        /// <see cref="FeBackFrameIndex"/> consumes: seconds since the frontend left
        /// click-to-start.
        /// </summary>
        public void SetScroll(double frontendSeconds)
        {
            float scroll = Mathf.PosMod(
                ((float)frontendSeconds * ScrollPxPerSecond) + ScrollPhasePx,
                ScrollPeriodPx);
            _material.SetShaderParameter("scroll", scroll);
            QueueRedraw();
        }

        public override void _Draw()
        {
            if (_logo is null)
            {
                return;
            }

            // One quad over the logo footprint. The shader clips it to the logo's
            // own alpha>=8 texels, which is what retail's depth stamp does.
            DrawTextureRect(
                _logo,
                new Rect2(LogoLeft, LogoTop, LogoWidth, LogoHeight),
                false,
                Colors.White);
        }

        // The literals here are the const fields above; the shader cannot consume
        // C# consts directly, so they are repeated once and only once:
        //   64/2/512/256  logo quad          (LogoLeft/Top/Width/Height)
        //   65/-8/256     sheen quad         (SheenLeftAtZeroScroll/Top/Height)
        //   512           wrap period        (ScrollPeriodPx)
        private const string ShaderCode = """
            shader_type canvas_item;
            render_mode blend_add, unshaded;

            uniform sampler2D reflection : filter_linear, repeat_enable;
            uniform float scroll;
            uniform float gain;

            void fragment() {
                // Fragment centres, so x is the pixel's integer column + 0.5.
                float x = 64.0 + (UV.x * 512.0);
                float y = 2.0 + (UV.y * 256.0);

                // D3DCMP_ALWAYS z-stamp of the alpha-tested logo body (ALPHAREF 8).
                float mask = step(8.0 / 255.0, texture(TEXTURE, UV).a);
                // The sheen quad's own edges: its left edge is 65 - scroll and its
                // bottom is y = 248. Everything between is covered by it or by its
                // +512 twin, which is what the mod() below expresses.
                mask *= step(65.0 - scroll, x);
                mask *= step(y, 248.0);

                float u = mod(x - 65.0 + scroll, 512.0) / 512.0;
                float v = (y + 8.0) / 256.0;
                COLOR = vec4(texture(reflection, vec2(u, v)).rgb * gain, mask);
            }
            """;
    }
}
