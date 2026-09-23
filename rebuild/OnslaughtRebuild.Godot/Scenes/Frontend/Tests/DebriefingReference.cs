// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Test-only retained settled Debriefing renderer from RetailFrontendFlow at
/// f86e78e0. It is a comparison oracle, never a production page or state owner.
/// The original body and its provenance/omissions are retained below. Comparing
/// this renderer establishes migration parity, not pristine retail pixel parity.
/// </summary>
public sealed partial class DebriefingReference : Control
{
    private const float DesignWidth = 640f, DesignHeight = 480f;
    private const int GlyphColumns = 16, GlyphCellSize = 16, FirstGlyph = 32, GlyphSlotCount = 256;
    private const int Font22Columns = 16, Font22CellSize = 32;
    private const float HeaderBarCenterX = 390f, HeaderTitleTop = 65f;
    private const string DebriefingTitle = "DEBRIEFING";
    private static readonly Color FrontendClearColor = new(31f / 255f, 31f / 255f, 63f / 255f, 1f);
    private static readonly Color FrontendFillDarkener = new(0f, 0f, 0f, 62f / 255f);
    private static readonly Color HeaderBoxOverlay = new(0f, 0f, 0f, 0.5f);
    private static readonly Color ReleasedTitleText = RetailColor(0xff7f7f7f);
    private static readonly Color ChromeTint = RetailColor(0x3e7f7f7f);
    private static readonly Color ShadowTint = RetailColor(0x3e000000);
    // CFEPDebriefing::Render settled positions, pristine 0x00456DD0.
    private const float DebriefingTextLeft = 130f;
    private const float DebriefingLevelTop = 149f;
    private const float DebriefingMissionStatusTop = 184f;
    private const float DebriefingPrimaryTop = 210f;
    private const float DebriefingSecondaryAfterPrimaryTop = 226f;
    private const float DebriefingValueGap = 20f;
    private const float DebriefingGradeLabelTop = 295f;
    private const float DebriefingGradeCenterX = 320f;
    private const float DebriefingGradeCenterY = 310f;
    private const float DebriefingRingCenterX = 285f;
    private const float DebriefingRingCenterY = 225f;
    private const float DebriefingRingScale = 1.6f;
    private static readonly Color DebriefingLabelText = RetailColor(0xffffaf3f);
    private static readonly Color DebriefingSuccessText = RetailColor(0xff3fff2f);
    private static readonly Color DebriefingFailureText = RetailColor(0xffff3f1f);
    private static readonly Color DebriefingAbortedText = RetailColor(0xff3f3f3f);
    private static readonly Color DebriefingGradeBodyTint = RetailColor(0xfeffffff);

    private Texture2D _titleFont = null!, _font22 = null!;
    private int[] _glyphWidths = [], _font22Widths = [];
    private Texture2D _debriefingMetalRing = null!, _forsetiWritingLarge = null!, _symbolBracket01 = null!;
    private Texture2D[] _debriefingGradeTextures = [], _feBackFrames = [];
    private RetailDebriefingProjection? _projection;
    private string _fallbackLevelName = string.Empty;
    private double _feBackSeconds;
    private readonly List<Texture2D> _ownedTextures = [];

    internal void Initialize(Texture2D[] frames)
    {
        _feBackFrames = frames;
        _titleFont = LoadTexture("font-13ps", 256, 256, CuratedAyaTextureLoader.Compression.Rgba8, "Hud");
        _font22 = LoadTexture("font-22", 512, 512, CuratedAyaTextureLoader.Compression.Rgba8, "Hud");
        using Image body = _titleFont.GetImage();
        using Image title = _font22.GetImage();
        _glyphWidths = MeasureGlyphWidths(body, GlyphCellSize, GlyphColumns);
        _font22Widths = MeasureGlyphWidths(title, Font22CellSize, Font22Columns);
        _forsetiWritingLarge = LoadTexture("forseti-writing-large", 128, 512);
        _symbolBracket01 = LoadTexture("symbol-bracket-01", 128, 128);
        LoadTextures();
        Size = new Vector2(640, 480);
        MouseFilter = MouseFilterEnum.Ignore;
        SetProcess(false);
        SetProcessInput(false);
    }

    internal IReadOnlyList<(string Name, Texture2D Texture)> Art =>
    [
        ("metal_ring", _debriefingMetalRing), ("writing", _forsetiWritingLarge),
        ("symbol_bracket", _symbolBracket01),
        .. _debriefingGradeTextures.Select((texture, index) => ($"grade_{"abcdes"[index]}", texture)),
    ];
    internal Texture2D Font(bool title) => title ? _font22 : _titleFont;
    internal int[] Widths(bool title) => (title ? _font22Widths : _glyphWidths).ToArray();
    internal float LabelColumn => DebriefingTextLeft + MathF.Max(MeasureText("Mission Status", 1f),
        MathF.Max(MeasureText("Primary Objectives", 1f), MeasureText("Secondary Objectives", 1f))) + DebriefingValueGap;

    internal void SetFrame(RetailDebriefingProjection projection, string fallbackLevelName, double seconds)
    {
        _projection = projection;
        _fallbackLevelName = fallbackLevelName;
        _feBackSeconds = seconds;
        QueueRedraw();
    }

    public override void _Draw()
    {
        if (_projection is not null) DrawDebriefing();
    }

    public override void _Notification(int what)
    {
        if (what != NotificationPredelete) return;
        foreach (Texture2D texture in _ownedTextures) texture.Dispose();
        _ownedTextures.Clear();
    }

    private void LoadTextures()
    {
        _debriefingMetalRing = LoadTexture(
            "Debriefing/metal-ring-transition",
            512,
            512,
            CuratedAyaTextureLoader.Compression.Dxt2);
        _debriefingGradeTextures =
        [
            LoadTexture("Debriefing/ranking-a", 64, 64, CuratedAyaTextureLoader.Compression.Dxt2),
            LoadTexture("Debriefing/ranking-b", 64, 64, CuratedAyaTextureLoader.Compression.Dxt2),
            LoadTexture("Debriefing/ranking-c", 64, 64, CuratedAyaTextureLoader.Compression.Dxt2),
            LoadTexture("Debriefing/ranking-d", 64, 64, CuratedAyaTextureLoader.Compression.Dxt2),
            LoadTexture("Debriefing/ranking-e", 64, 64, CuratedAyaTextureLoader.Compression.Dxt2),
            LoadTexture("Debriefing/ranking-s", 64, 64, CuratedAyaTextureLoader.Compression.Dxt2),
        ];
    }

    private Texture2D LoadTexture(string name, int width, int height,
        CuratedAyaTextureLoader.Compression compression = CuratedAyaTextureLoader.Compression.Dxt2,
        string folder = "Frontend")
    {
        Texture2D texture = CuratedAyaTextureLoader.Load($"res://Assets/{folder}/{name}.texture.aya", width, height, compression);
        _ownedTextures.Add(texture);
        return texture;
    }

    /// <summary>
    /// Settled retail <c>FEP_DEBRIEFING</c> projection. The page body is ported
    /// from pristine <c>CFEPDebriefing::Render</c>
    /// (<c>0x00456DD0..0x00457CED</c>), not inferred from the partial source
    /// drop. Its common pre-pass calls <c>CFrontEnd::RenderPreCommonFade</c>, so
    /// this uses the existing FEBack common underlay rather than the briefing
    /// page's separate rock scene.
    ///
    /// <para>The exact settled body represented here is: level at (130,149),
    /// mission status at y=184, primary at y=210 when defined, secondary at
    /// y=226 after primary or y=210 by itself, grade label at (130,295), and
    /// grade art centred at (320,310). The value column is 20 pixels after the
    /// widest of the three untranslated label extents. No kill table exists in
    /// this Render body.</para>
    ///
    /// <para>Still open rather than approximated: entry/exit interpolation,
    /// overlay and goodie particle/message effects, the delayed grade glint,
    /// retail Z-function-to-Canvas compositing equivalence for the grade
    /// foreground, and pixel validation against a pristine debriefing capture.
    /// The grade texture and submitted settled colors are exact; Level 100's
    /// current S input remains the reconstruction's unmeasured score/time
    /// shortcut.</para>
    /// </summary>
    private void DrawDebriefing()
    {
        RetailDebriefingProjection debriefing = _projection
            ?? throw new InvalidOperationException(
                "The debriefing screen has no END_LEVEL_DATA projection.");

        DrawMainUnderlay(1f);
        DrawSurfaceCentered(
            _debriefingMetalRing,
            DebriefingRingCenterX,
            DebriefingRingCenterY,
            DebriefingRingScale,
            DebriefingRingScale,
            Colors.White);
        DrawDebriefingWritingChrome();

        string levelName = RetailFrontendWorldStrings.LevelName(debriefing.WorldFinished)
            ?? _fallbackLevelName;
        DrawFont22Text(
            levelName,
            new Vector2(DebriefingTextLeft, DebriefingLevelTop),
            1f,
            1f,
            Colors.White);

        const string missionStatusLabel = "Mission Status";
        const string primaryLabel = "Primary Objectives";
        const string secondaryLabel = "Secondary Objectives";
        float valueLeft = DebriefingTextLeft
            + MathF.Max(
                MeasureText(missionStatusLabel, 1f),
                MathF.Max(
                    MeasureText(primaryLabel, 1f),
                    MeasureText(secondaryLabel, 1f)))
            + DebriefingValueGap;

        DrawText(
            missionStatusLabel + ": ",
            new Vector2(DebriefingTextLeft, DebriefingMissionStatusTop),
            1f,
            DebriefingLabelText);
        DrawText(
            DebriefingMissionStatusText(debriefing.MissionStatus),
            new Vector2(valueLeft, DebriefingMissionStatusTop),
            1f,
            DebriefingMissionStatusColor(debriefing.MissionStatus));

        if (debriefing.PrimaryObjectives != RetailDebriefingObjectiveSummary.Hidden)
        {
            DrawDebriefingObjectiveRow(
                primaryLabel,
                debriefing.PrimaryObjectives,
                DebriefingPrimaryTop,
                valueLeft);
        }

        if (debriefing.SecondaryObjectives != RetailDebriefingObjectiveSummary.Hidden)
        {
            float secondaryTop =
                debriefing.PrimaryObjectives == RetailDebriefingObjectiveSummary.Hidden
                    ? DebriefingPrimaryTop
                    : DebriefingSecondaryAfterPrimaryTop;
            DrawDebriefingObjectiveRow(
                secondaryLabel,
                debriefing.SecondaryObjectives,
                secondaryTop,
                valueLeft);
        }

        if (debriefing.GradeByte is byte gradeByte)
        {
            DrawFont22Text(
                "Grade:",
                new Vector2(DebriefingTextLeft, DebriefingGradeLabelTop),
                1f,
                1f,
                Colors.White);

            DrawSurfaceCentered(
                _symbolBracket01,
                DebriefingGradeCenterX + 5f,
                DebriefingGradeCenterY + 10f,
                1.3125f,
                1.3125f,
                ShadowTint);
            DrawSurfaceCentered(
                _symbolBracket01,
                DebriefingGradeCenterX,
                DebriefingGradeCenterY,
                1.25f,
                1.25f,
                DebriefingGradeBodyTint);

            Texture2D grade = DebriefingGradeTexture(gradeByte);
            DrawSurfaceCentered(
                grade,
                DebriefingGradeCenterX + 3f,
                DebriefingGradeCenterY + 3f,
                1f,
                1f,
                ShadowTint);
            DrawSurfaceCentered(
                grade,
                DebriefingGradeCenterX,
                DebriefingGradeCenterY,
                1f,
                1f,
                DebriefingGradeBodyTint);
        }

        DrawHeaderBarTitle(DebriefingTitle);
    }

    private void DrawDebriefingWritingChrome()
    {
        // FEPShared::RenderSelectionBrackets 0x00452FD0 is misleadingly named:
        // it draws four FE_Forseti_Writing_large surfaces at x=86, scale 0.5,
        // 180 pixels apart. Its first y is
        // 90 - fmod(frontend_counter * 0.3, 180). The current presenter has no
        // proven mapping for that counter, so it uses the exact cold-BSS phase
        // (y=90) rather than inventing a clock rate.
        for (int index = 0; index < 4; index++)
        {
            DrawSurfaceCentered(
                _forsetiWritingLarge,
                86f,
                90f + (index * 180f),
                0.5f,
                0.5f,
                ChromeTint);
        }
    }

    private void DrawDebriefingObjectiveRow(
        string label,
        RetailDebriefingObjectiveSummary summary,
        float top,
        float valueLeft)
    {
        DrawText(
            label + ": ",
            new Vector2(DebriefingTextLeft, top),
            1f,
            DebriefingLabelText);
        DrawText(
            summary == RetailDebriefingObjectiveSummary.Complete
                ? "Complete"
                : "Incomplete",
            new Vector2(valueLeft, top),
            1f,
            summary == RetailDebriefingObjectiveSummary.Complete
                ? DebriefingSuccessText
                : DebriefingFailureText);
    }

    private static string DebriefingMissionStatusText(
        RetailDebriefingMissionStatus status) => status switch
        {
            RetailDebriefingMissionStatus.Victory => "Victory",
            RetailDebriefingMissionStatus.Defeat => "Defeat",
            _ => "Aborted",
        };

    private static Color DebriefingMissionStatusColor(
        RetailDebriefingMissionStatus status) => status switch
        {
            RetailDebriefingMissionStatus.Victory => DebriefingSuccessText,
            RetailDebriefingMissionStatus.Defeat => DebriefingFailureText,
            _ => DebriefingAbortedText,
        };

    private Texture2D DebriefingGradeTexture(byte grade) => grade switch
    {
        (byte)'A' => _debriefingGradeTextures[0],
        (byte)'B' => _debriefingGradeTextures[1],
        (byte)'C' => _debriefingGradeTextures[2],
        (byte)'D' => _debriefingGradeTextures[3],
        (byte)'E' => _debriefingGradeTextures[4],
        (byte)'S' => _debriefingGradeTextures[5],
        _ => throw new InvalidDataException(
            $"Retail debriefing has no grade surface for byte 0x{grade:X2}."),
    };

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

        int frame = LevelSelectReference.FeBackFrameIndex(_feBackSeconds, _feBackFrames.Length);
        DrawTextureRect(
            _feBackFrames[frame],
            new Rect2(0f, 0f, DesignWidth, DesignHeight),
            false,
            new Color(1f, 1f, 1f, alpha));
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
    /// measurably non-uniform (see <c>BriefingLevelNameScaleX</c>).
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

    private static float Clamp01(float value) => Math.Clamp(value, 0f, 1f);
    private static float RangeTransition(float value, float low, float high) => Clamp01((value - low) / (high - low));
    private static float MakeAlpha(float value) => Math.Clamp(MathF.Round(Clamp01(value) * 255f), 0f, 255f) / 255f;
    private static Color RetailColor(uint argb) => new(
        Modulate2X((argb >> 16) & 0xff), Modulate2X((argb >> 8) & 0xff), Modulate2X(argb & 0xff),
        ((argb >> 24) & 0xff) / 255f);
    private static float Modulate2X(uint channel) => Math.Min(255u, (channel * 255u) >> 7) / 255f;
}
