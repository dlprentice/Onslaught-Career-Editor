// SPDX-License-Identifier: GPL-3.0-or-later

using System.Text.Json;
using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// The bounded released-style frontend path into the Level 100 opening slice.
/// It owns its page/input/loading lifecycle and exposes load, retry, and
/// Main Menu return seams to the existing gameplay host. Mission/HUD and audio
/// presentation remain separate owners.
/// </summary>
[Tool]
public sealed partial class RetailFrontendFlow : Control
{
    // Steam FE virtual stage (cluster hint from CFEPMain / click render).
    private const float DesignWidth = 640f;
    private const float DesignHeight = 480f;
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

    // MISSION BRIEFING / SELECT CONFIGURATION. Every literal in this block is
    // measured from the two pristine 640x480 captures taken 2026-07-25:
    //   local-lab/retail-reference-pristine/mission-briefing/05-mission-briefing-640x480.png
    //   local-lab/retail-reference-pristine/select-configuration/06-select-configuration-640x480.png
    // See DrawMissionBriefing and Tests/ConfigurationReference.cs for the per-element evidence.
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

    // WHICH BRANCH THE MAIN MENU TAKES ON THIS EDGE, and why there is no `dest`
    // variable for it. `dest` is the OTHER page of the transition, as passed at
    // FrontEnd.cpp:1299-1305 — the parameter is named for the destination but each
    // page receives its counterpart. CFEPMain__Render (0x00462D40) branches on
    // `dest == 0x0c` at five sites verified in the pristine specimen — 0x004636B2,
    // 0x00463920, 0x00463B44, 0x00463DCC and 0x0046423D, all `83 fb 0c cmp ebx,0Ch`
    // — and the page we arrive from is the click page, ordinal 12. This lane can
    // therefore only ever be on the 0x0c side, so the constant is folded into the
    // ported laws rather than carried as state. See native main_menu_laws.gd for how that
    // was settled against pixels instead of assumed.

    private int _mainTransitionCount;
    private int _mainTransitionTime;

    private GdFrontendSession _session = null!;
    private readonly Dictionary<RetailFrontendMenuItemKind, string> _menuText = [];

    private Texture2D _rockBackground = null!;
    private Texture2D[] _feBackFrames = [];
    private Texture2D _titleTextBox = null!;
    private Texture2D _symbolBracket01 = null!;
    private Texture2D _levelBracket01 = null!;
    private Texture2D _levelBracket02 = null!;
    private Texture2D _levelRing01 = null!;
    private Texture2D _levelRing02 = null!;
    private Texture2D _titleFont = null!;
    private Texture2D _font22 = null!;
    private int[] _font22Widths = [];
    private Texture2D _feArrow = null!;
    private int[] _glyphWidths = [];
    private string _selectLevelText = string.Empty;
    // The level-select name band and the briefing page draw the SELECTED
    // node's row through _session.SelectedLevelName; this field stays as the
    // localization-table load receipt (english.json "level100") and feeds
    // nothing on its own.
    private string _level100Text = string.Empty;
    private string _loadingText = string.Empty;
    private double _animationSeconds;
    private double _clickPulseTimer;
    private double _clickPageSeconds;
    // Seconds since the frontend left click-to-start, which is MEASURED to be
    // FEBack128's phase origin. See FeBackFrameIndex for the phase itself and for
    // the alias that nearly got this wrong.
    private double _feBackSeconds;
    private RetailFrontendScreen _lastDrawnScreen = RetailFrontendScreen.ClickToStart;
    private int _loadingFrames;
    private bool _initialized;
    private bool _loadRequestRaised;
    private bool _level100Ready;
    private bool _gameplayActivationRaised;

    public event Action? Level100LoadRequested;

    public event Action? Level100LoadingStarted;

    public event Action? GameplayActivated;

    public event Action? GameplaySuspended;

    public event Action? ReturnToMainMenuRequested;

    public event Action? ExitRequested;

    internal AudioPlaybackRetirement PlaybackRetirement { get; set; } = null!;

    public event Action<RetailCareerDescriptor>? CareerSelected;

    public event Action<RetailFrontendAudioCue>? AudioCueRequested;

    public event Action<RetailFrontendCursorMode>? CursorModeRequested;

    internal RetailFrontendScreen CurrentScreen => _session.Screen;

    public void Initialize(IReadOnlyList<RetailCareerDescriptor> careerDescriptors)
    {
        if (_initialized)
        {
            throw new InvalidOperationException("The retail frontend is already initialized.");
        }

        ArgumentNullException.ThrowIfNull(careerDescriptors);
        _session?.Dispose();
        _session = new GdFrontendSession(careerDescriptors);
        LoadLocalization();
        LoadTextures();
        _feBackFrames = LoadFeBackFrames(Engine.IsEditorHint() ? 1 : int.MaxValue);
        InitializeOptions();
        InitializeClick();
        InitializeMainMenu();
        InitializeQuitConfirm();
        InitializeCareerName();
        InitializeConfiguration();
        InitializeLoading();
        InitializeDebriefing();

        _initialized = true;
    }

    public override void _Notification(int what)
    {
        if (what == NotificationPredelete)
        {
            _session?.Dispose();
            _debriefingFrame?.Dispose();
        }
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

    /// <summary>
    /// Post-Won re-entry: apply the FillOut update and show FEP_DEBRIEFING.
    /// The host tears the Level 100 world down through the existing
    /// <see cref="ReturnToMainMenuRequested"/> seam; SELECT LEVEL follows only
    /// after the player acknowledges the debriefing page.
    /// </summary>
    public void AcceptWonHandoff(
        Level100MissionOutcome outcome,
        Level100MissionTerminalState terminalState)
    {
        RetailFrontendScreen origin = _session.Screen;
        if (!_session.TryAcceptWonHandoff(outcome, terminalState))
        {
            return;
        }

        ResumeFrontendForNavigation(origin);
        HandleNavigationSignal(RetailFrontendSignal.PageChanged);
        ReturnToMainMenuRequested?.Invoke();
        QueueRedraw();
    }

    internal int LaunchWorldNumber => _session.ConsumeLaunchWorldNumber;

    internal bool SelectedWorldIsConstructible => _session.SelectedWorldIsConstructible;

    /// <summary>
    /// Loading admitted a world this reconstruction cannot build. Return to
    /// SELECT LEVEL without constructing Level 100 in its place.
    /// </summary>
    public void ReturnUnconstructibleLaunchToLevelSelect()
    {
        if (!_session.ReturnUnconstructibleLaunchToLevelSelect())
        {
            throw new InvalidOperationException(
                "An unconstructible launch can return only after its request was consumed.");
        }

        _loadRequestRaised = false;
        _level100Ready = false;
        _loadingFrames = 0;
        QueueRedraw();
    }

    internal void ConfirmForSmoke()
    {
        Confirm();
    }

    internal void SelectMainIndexForCapture(int index)
    {
        _session.SelectMainIndex(index);
        QueueRedraw();
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
        _mouseCursorLayer?.QueueRedraw();
    }

    public override void _Ready()
    {
        if (Engine.IsEditorHint() && !_initialized)
        {
            try
            {
                Initialize([]);
                SetEditorPage();
            }
            catch (Exception exception)
            {
                GD.PushWarning($"Frontend assets unavailable: {exception.Message}");
                SetProcess(false);
                SetProcessInput(false);
                return;
            }
        }
        if (!_initialized)
            Initialize([]); // Running the frontend scene alone has no injected careers.
        BindSceneParts();

        if (!Engine.IsEditorHint())
            SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        MouseFilter = MouseFilterEnum.Ignore;
        ZIndex = 100;

        if (!Engine.IsEditorHint())
        {
            _mouseCursorLayer = new RetailMouseCursorLayer
            {
                Name = "RetailMouseCursor",
                ZIndex = 2,
            };
            _mouseCursorLayer.Configure(this);
            AddChild(_mouseCursorLayer);
        }
        SetProcess(!Engine.IsEditorHint());
        SetProcessInput(!Engine.IsEditorHint());
        QueueRedraw();
    }

    public override void _Process(double delta)
    {
        if (Engine.IsEditorHint()) return;
        double step = Math.Max(0d, delta);
        _animationSeconds += step;

        // CFrontEnd::SetPage, FrontEnd.cpp:583-591 — arm the transition on the
        // edge, exactly the edge the click page's 0x2C handler takes. Every OTHER
        // way into FEP_MAIN stays instant: FrontEnd.cpp:228-232 re-enters the
        // frontend with SetPage(FEP_MAIN, 0) on FEE_TITLE_SCREEN, and no other
        // released entry length is evidenced, so none is invented.
        if (_session.Screen == RetailFrontendScreen.MainMenu &&
            _lastDrawnScreen == RetailFrontendScreen.ClickToStart)
        {
            _mainTransitionCount = 0;
            _mainTransitionTime = MainMenuEntryTransitionFrames;
        }

        // CFrontEnd::Process, FrontEnd.cpp:665-675 — one increment per Process,
        // and the page goes active on the frame where count == time. Godot's
        // _Process is this lane's Process, and it stages the frame that _Draw
        // then rasterizes, so the first drawn frame carries count == 1 exactly as
        // FrontEnd.cpp:1433-1437 does.
        if (_mainTransitionTime > 0)
        {
            _mainTransitionCount++;
            if (_mainTransitionCount >= _mainTransitionTime)
            {
                _mainTransitionTime = 0;
            }
        }

        if (_session.Screen == RetailFrontendScreen.ClickToStart)
        {
            if (_lastDrawnScreen != RetailFrontendScreen.ClickToStart)
            {
                _clickPulseTimer = 0d;
                _clickPageSeconds = 0d;
            }

            // CFEPIntro::Process 0x0051B6B0: hold this+0x18 at 0 until
            // GetTime()-[this+4] > 1.0, seed 0x3727C5AC, then add 2*dt.
            // See RetailClickToStartPrompt. The 30 s idle write of -3 to
            // 0x008A956C is deliberately not driven here.
            _clickPageSeconds += step;
            _clickPulseTimer = RetailClickToStartPrompt.Advance(
                _clickPulseTimer,
                _clickPageSeconds,
                step);
        }
        else if (_session.Screen != RetailFrontendScreen.IntroCutscene)
        {
            // Free-runs from the moment click-to-start is left, and is NOT reset on
            // later page changes. Retail's underlay is measured to be page-anchored
            // on the main menu and NOT page-anchored on FEP_DEVSELECT or
            // FEP_LEVEL_SELECT (matched-offset cross-run material 7-44 % and
            // 5.8-63 % there against 0.4-1.5 % on the main menu), which is what a
            // single clock started once at frontend entry produces.
            //
            // IntroCutscene is excluded because retail's frontend page machine is
            // not running at all during RunIntroFMV — that call sits inside
            // CGame::RestartLoopRunLevel, not inside the frontend. Letting this
            // clock run would inject 123.8 s of phase into a MEASURED underlay
            // scroll, which is a lab artefact and not a released behaviour.
            _feBackSeconds += step;
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
                // Retail runs the level's intro FMV HERE — after the load, with
                // the loading screen driven to 100 % and dismissed, before the
                // first gameplay frame (references/Onslaught/game.cpp:1336-1345).
                // See RetailFrontendFlow.Cutscene.cs. When there is no cutscene
                // to play this falls through to the pre-existing handoff.
                if (!TryBeginLevel100IntroCutscene())
                {
                    if (!_session.TryCompleteLoading(
                            startupMediaActive: false,
                            launchConsumed: _loadRequestRaised))
                    {
                        throw new InvalidOperationException(
                            "Level 100 can complete only after its pending launch request is consumed.");
                    }
                }
            }
        }

        if (TryRaiseGameplayActivation())
        {
            return;
        }

        QueueRedraw();
        _mouseCursorLayer?.QueueRedraw();
    }

    /// <summary>
    /// Hands the screen to gameplay on the frame the session first reaches it.
    ///
    /// Extracted from <c>_Process</c> so the intro-cutscene completion can raise
    /// the SAME edge in the SAME frame. The cutscene finishes inside its own
    /// child node's <c>_Process</c>, which Godot runs after this node's, so
    /// leaving the edge to the next frame put the session on Gameplay for one
    /// frame while nothing had been activated — a window the smoke harness
    /// observed and threw on. It is the ordering artefact, not the state, that
    /// this removes.
    /// </summary>
    private bool TryRaiseGameplayActivation()
    {
        if (_session.Screen != RetailFrontendScreen.Gameplay || _gameplayActivationRaised)
        {
            return false;
        }

        _gameplayActivationRaised = true;
        Visible = false;
        SetProcessInput(false);
        SetProcess(false);
        CursorModeRequested?.Invoke(RetailFrontendCursorMode.Captured);
        GameplayActivated?.Invoke();
        return true;
    }

    /// <summary>
    /// <c>trans</c> as FrontEnd.cpp:1291 computes it, and 1.0 once the page is
    /// active (FrontEnd.cpp:1310 renders a settled page with a literal 1.f).
    /// </summary>
    private float MainMenuTransition =>
        _mainTransitionTime <= 0
            ? 1f
            : Math.Min(1f, (float)_mainTransitionCount / _mainTransitionTime);

    public override void _Input(InputEvent inputEvent)
    {
        if (Engine.IsEditorHint()) return;
        // IntroCutscene is included because the movie owns the screen and the
        // RetailStartupSequence child owns the abort. A frontend page reacting to
        // the keypress that skips the movie would navigate an invisible page.
        if (_session.Screen is RetailFrontendScreen.Loading or
            RetailFrontendScreen.IntroCutscene or
            RetailFrontendScreen.Gameplay)
        {
            return;
        }

        // FrontEnd.cpp:551-552 — while mActivePage == FEP_TRANSITION the
        // button action is never forwarded to a page. CFEPMain::Render
        // hover is not ButtonPressed: 0x004630AC / 0x004631EF run when
        // transition > 0.9 (fcomp [0x005D8BB0]; test ah,0x41 / jne skip).
        // Motion is therefore allowed through; HandlePointerMotion applies
        // the 0.9 gate. Confirm and HandleKey stay swallowed here.
        if (RetailMainMenuHitTest.SwallowsFrontendInput(
                _mainTransitionTime > 0,
                inputEvent is InputEventMouseMotion))
        {
            return;
        }

        bool handled = inputEvent switch
        {
            InputEventMouseMotion motion => HandlePointerMotion(motion.Position),
            InputEventMouseButton button when
                button.Pressed && button.ButtonIndex == MouseButton.Left =>
                HandlePointerConfirm(button.Position),
            InputEventMouseButton button when
                button.Pressed && button.ButtonIndex == MouseButton.Right =>
                HandlePointerCancel(),
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
        // Actual production page components own their drawing in the authored
        // scene. Only the outside-stage letterbox belongs to this controller.
        base.DrawRect(new Rect2(Vector2.Zero, Size), Colors.Black);
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
    /// keep adding words while the line fits, else break — reproduces world
    /// 100's transcribed breaks exactly under that ceiling (asserted by
    /// <c>RetailFrontendFlowWrapTests</c>); other worlds get the same law
    /// rather than invented breaks.
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

    private bool HandlePointerMotion(Vector2 position)
    {
        Vector2 design = ToDesignPosition(position);
        if (_session.Screen == RetailFrontendScreen.Options)
        {
            if (!HandleOptionsPointerMotion(design))
            {
                return false;
            }
            QueueRedraw();
            return true;
        }

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

        // 0x004630AC / 0x004631EF: hover only when transition > 0.9.
        // Language hover writes this+0x08 = -1; that is not a language
        // swap and not a button confirm. Session cannot hold -1.
        if (!RetailMainMenuHitTest.AcceptsHitTest(MainMenuTransition))
        {
            return false;
        }

        if (RetailMainMenuHitTest.LanguageHoverContains(design.X, design.Y))
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
                // CFEPIntro::Process 0x0051B801 submits (0,0,width,width,0x2C)
                // — full window, not a glyph box. See RetailFrontendScenePath.
                if (!_session.AcceptsClickToStartMouse(
                        design.X,
                        design.Y))
                {
                    return false;
                }

                Confirm();
                return true;

            case RetailFrontendScreen.Options:
                return HandleOptionsPointerConfirm(design);

            case RetailFrontendScreen.MainMenu:
                int index = MainMenuIndexAt(design);
                if (!_session.CanAcceptMainMenuRow(index))
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
                int careerTarget = CareerNameTargetAt(design);
                if (careerTarget == 1)
                {
                    if (!_session.TryBackPage(
                            startupMediaActive: false,
                            out RetailFrontendSignal back))
                    {
                        return false;
                    }
                    RequestAudioCue(RetailFrontendAudioCue.Back);
                    HandleNavigationSignal(back);
                    QueueRedraw();
                    return true;
                }
                if (careerTarget == 2)
                {
                    Confirm();
                    return true;
                }
                return false;

            case RetailFrontendScreen.LevelSelect:
                // Chevron hit rects match the drawn chevrons, as on FEP_DEVSELECT.
                if (new Rect2(0f, 430f, 48f, 48f).HasPoint(design))
                {
                    if (!_session.TryBackPage(
                            startupMediaActive: false,
                            out RetailFrontendSignal levelBack))
                    {
                        return false;
                    }
                    RequestAudioCue(RetailFrontendAudioCue.Back);
                    HandleNavigationSignal(levelBack);
                    QueueRedraw();
                    return true;
                }
                if (new Rect2(595f, 430f, 45f, 48f).HasPoint(design))
                {
                    Confirm();
                    return true;
                }

                // LevelNodes[0] at (148,320) — the root, world 100. The
                // measured 60x60 hit box is unchanged.
                if (new Rect2(120f, 265f, 60f, 60f).HasPoint(design))
                {
                    _ = _session.SelectWorld(RetailWorldCatalog.RootWorldNumber);
                    Confirm();
                    return true;
                }

                // LevelNodes[1] is one column pitch (60) to the right of the
                // root — the first child in the measured Episode 1 graph,
                // which the career table says is world 110. Locked until a
                // Won update unlocks it; do not Confirm the root instead.
                if (new Rect2(180f, 265f, 60f, 60f).HasPoint(design))
                {
                    if (!_session.SelectWorld(110))
                    {
                        return false;
                    }

                    Confirm();
                    return true;
                }

                return false;

            case RetailFrontendScreen.Debriefing:
                // Settled CFEPDebriefing::Render dispatches button 0x2C over
                // the entire 640x480 rectangle when mouse input is ready.
                if (!new Rect2(0f, 0f, DesignWidth, DesignHeight).HasPoint(design))
                {
                    return false;
                }

                Confirm();
                return true;

            case RetailFrontendScreen.MissionBriefing:
            case RetailFrontendScreen.SelectConfiguration:
                // Both pages carry the same two chevrons and nothing else
                // clickable this lane models.
                int pageTarget = _session.Screen == RetailFrontendScreen.SelectConfiguration
                    ? ConfigurationTargetAt(design)
                    : new Rect2(0f, 430f, 48f, 48f).HasPoint(design) ? 1
                    : new Rect2(595f, 430f, 45f, 48f).HasPoint(design) ? 2 : 0;
                if (pageTarget == 1)
                {
                    if (!_session.TryBackPage(
                            startupMediaActive: false,
                            out RetailFrontendSignal pageBack))
                    {
                        return false;
                    }
                    RequestAudioCue(RetailFrontendAudioCue.Back);
                    HandleNavigationSignal(pageBack);
                    QueueRedraw();
                    return true;
                }
                if (pageTarget == 2)
                {
                    Confirm();
                    return true;
                }
                return false;

            default:
                return false;
        }
    }

    private bool HandlePointerCancel()
    {
        if (_session.Screen != RetailFrontendScreen.Options)
        {
            return false;
        }

        return HandleOptionsPointerCancel(rightDown: true);
    }

    private bool HandleKey(InputEventKey key)
    {
        // FEP_OPTIONS owns its own selection, left/right value stepping, dropdown
        // expansion and back stack, so it takes the whole key path.
        if (_session.Screen == RetailFrontendScreen.Options)
        {
            return HandleOptionsKey(key);
        }

        // New-career FEP_DEVSELECT is editable; Load mode mirrors the selected
        // injected save name and RetailFrontendSession rejects edits.
        if (_session.Screen == RetailFrontendScreen.DevSelect &&
            _session.CareerPageMode == RetailFrontendCareerPageMode.New)
        {
            if (IsKey(key, Key.Backspace))
            {
                if (_session.RemoveGameNameCharacter())
                {
                    QueueRedraw();
                }
                return true;
            }

            if (IsKey(key, Key.Left) || IsKey(key, Key.Up) || IsKey(key, Key.Right) || IsKey(key, Key.Down))
            {
                _session.MoveGameNameCursor(IsKey(key, Key.Right) || IsKey(key, Key.Down));
                QueueRedraw();
                return true;
            }
            if (IsKey(key, Key.Home) || IsKey(key, Key.End) || IsKey(key, Key.Delete)) return true;
            if (key.Unicode >= 32)
            {
                if (key.Unicode <= char.MaxValue &&
                    _session.AppendGameNameCharacter((char)key.Unicode, MeasureGameNameExtent(_session.GameName)))
                    QueueRedraw();
                return true;
            }
        }

        // QuitConfirm is a vertical YESNO stack. Retail
        // CFrontEnd__HandleModalPanelButton 0x0044dd60 option_mode 2:
        // BUTTON_FRONTEND_MENU_UP (0x2a) writes this+0x1fa0 = 1 (Yes, upper);
        // DOWN (0x2b) writes 0 (No, lower). PCController.cpp maps KEYCODE_UP /
        // KEYCODE_DOWN onto those buttons. Left/Right keep the session
        // 0=No / 1=Yes MovePrevious / MoveNext law.
        if (_session.Screen == RetailFrontendScreen.QuitConfirm)
        {
            if (IsKey(key, Key.Up))
            {
                if (_session.SelectQuitConfirmIndex(RetailFeMessBox.YesChoiceIndex))
                {
                    RequestAudioCue(RetailFrontendAudioCue.Move);
                    QueueRedraw();
                }

                return true;
            }

            if (IsKey(key, Key.Down))
            {
                if (_session.SelectQuitConfirmIndex(RetailFeMessBox.DefaultChoiceIndex))
                {
                    RequestAudioCue(RetailFrontendAudioCue.Move);
                    QueueRedraw();
                }

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
            if (_session.Screen == RetailFrontendScreen.ClickToStart
                && !_session.AcceptsClickToStartKey(
                    ScanCodeFor(key)))
            {
                return true;
            }

            Confirm();
            return true;
        }
        if (IsKey(key, Key.Escape))
        {
            if (_session.TryBackPage(
                    startupMediaActive: false,
                    out RetailFrontendSignal signal))
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
        if (!_session.TryConfirmPage(
                startupMediaActive: false,
                out RetailFrontendSignal signal))
        {
            return;
        }

        // CFEPOptions::TransitionNotification reuses one persistent frontend
        // pause-menu context/tree but starts a fresh root session on each entry.
        if (_session.Screen == RetailFrontendScreen.Options)
        {
            ResetOptions();
        }

        RequestAudioCue(RetailFrontendAudioCue.Select);
        HandleNavigationSignal(signal);
        if (signal == RetailFrontendSignal.ExitRequested)
        {
            ExitRequested?.Invoke();
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
        QueueRedraw();
        _mouseCursorLayer?.QueueRedraw();
    }

    private void HandleNavigationSignal(RetailFrontendSignal signal)
    {
        if (signal == RetailFrontendSignal.LevelLaunchRequested)
        {
            _loadRequestRaised = false;
            _level100Ready = false;
            _gameplayActivationRaised = false;
            _loadingFrames = 0;
            Level100LoadingStarted?.Invoke();
            CursorModeRequested?.Invoke(RetailFrontendCursorMode.Hidden);
        }
        else if (signal == RetailFrontendSignal.ReturnToMainMenuRequested)
        {
            CursorModeRequested?.Invoke(RetailFrontendCursorMode.Custom);
            ReturnToMainMenuRequested?.Invoke();
        }
        else if (signal == RetailFrontendSignal.CareerLoadRequested)
        {
            RetailCareerDescriptor selectedCareer =
                _session.ConsumeSelectedCareerLoadRequest()
                ?? throw new InvalidOperationException(
                    "CareerLoadRequested did not carry a selected career descriptor.");
            CareerSelected?.Invoke(selectedCareer);
            CursorModeRequested?.Invoke(RetailFrontendCursorMode.Custom);
        }
        else if (signal == RetailFrontendSignal.PageChanged)
        {
            CursorModeRequested?.Invoke(RetailFrontendCursorMode.Custom);
        }
    }

    private int MainMenuIndexAt(Vector2 designPosition)
    {
        if (_stage is null) return -1;
        Vector2 canvasPoint = _stage.GetGlobalTransformWithCanvas() * designPosition;
        return _mainMenuView.Call("hit_test", canvasPoint).AsInt32();
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

    private void LoadTextures()
    {
        _rockBackground = LoadTexture(
            "Backgrounds/rock",
            1024,
            512,
            CuratedAyaTextureLoader.Compression.Dxt1);
        _titleTextBox = LoadTexture("title-text-box", 256, 32);
        _symbolBracket01 = LoadTexture("symbol-bracket-01", 128, 128);
        _levelBracket01 = LoadTexture("level-bracket-01", 512, 512);
        _levelBracket02 = LoadTexture("level-bracket-02", 512, 512);
        _levelRing01 = LoadTexture("level-ring-01", 64, 64);
        _levelRing02 = LoadTexture("level-ring-02", 64, 64);
        _feArrow = LoadTexture("fe-arrow", 64, 64);
        // Frontend font pages and widths are supplied once by native Options
        // from their shared public recipes; no per-glyph language calls.
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

    private Texture2D LoadTexture(
        string name,
        int width,
        int height,
        CuratedAyaTextureLoader.Compression compression = CuratedAyaTextureLoader.Compression.Dxt2,
        string folder = "Frontend") =>
        CuratedAyaTextureLoader.Load(
            AssetPaths.TexturePath(folder, name),
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
        if (_paintingPart is not null) return (1f, Vector2.Zero);
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

    private static int ScanCodeFor(InputEventKey key)
    {
        Key code = key.PhysicalKeycode != Key.None ? key.PhysicalKeycode : key.Keycode;
        return code switch
        {
            Key.Space => 0x39,
            Key.Enter => 0x1C,
            Key.Escape => 0x01,
            Key.KpEnter => 0x9C,
            _ => 0,
        };
    }

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
