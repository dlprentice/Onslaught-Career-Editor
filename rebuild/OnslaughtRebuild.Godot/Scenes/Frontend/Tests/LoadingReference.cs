// SPDX-License-Identifier: GPL-3.0-or-later

using System.Text.Json;
using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Exact DrawLoading numerical law retained from RetailFrontendFlow at
/// b86b7b9b. This comparison oracle is never a production page or lifecycle.
/// The old scene's Control proxy transform is measured separately by the
/// actual-flow harness; it is not folded into these original source anchors.
/// Pixel equality here proves migration parity, not pristine retail parity.
/// </summary>
public sealed partial class LoadingReference : Control
{
    private const float DesignWidth = 640f, DesignHeight = 480f;
    private const float LoadingTextLeft = 270f, LoadingTextTop = 393.5f;
    private const float LoadingBarLeft = 78f, LoadingBarTop = 423f, LoadingBarWidth = 485f, LoadingBarHeight = 25f;
    private const int FirstGlyph = 32, GlyphSlotCount = 256, Font22CellSize = 32, Font22Columns = 16;
    private Texture2D _loadingScreen = null!, _font22 = null!;
    private int[] _font22Widths = [];
    private string _loadingText = "Loading...";

    internal void Initialize()
    {
        _loadingScreen = LegacyCuratedAyaTextureReference.Load("res://Assets/Frontend/loading-screen.texture.aya", 512, 512,
            LegacyCuratedAyaTextureReference.Compression.Dxt1);
        _font22 = LegacyCuratedAyaTextureReference.Load("res://Assets/Hud/font-22.texture.aya", 512, 512,
            LegacyCuratedAyaTextureReference.Compression.Rgba8);
        using Image image = _font22.GetImage();
        _font22Widths = MeasureGlyphWidths(image, Font22CellSize, Font22Columns);
        Size = new Vector2(640, 480);
        MouseFilter = MouseFilterEnum.Ignore;
        SetProcess(false);
        SetProcessInput(false);
    }

    internal Texture2D Font => _font22;
    internal Texture2D Background => _loadingScreen;
    internal int[] Widths => _font22Widths.ToArray();
    internal void SetCaption(string text) { _loadingText = text; QueueRedraw(); }
    public override void _Draw() => DrawLoading();
    public override void _Notification(int what)
    {
        if (what != NotificationPredelete) return;
        _loadingScreen?.Dispose();
        _font22?.Dispose();
    }
    private static void SelectSceneSection(string section) { }

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
    /// KNOWN GAP: the bar is the measured opaque black rectangle over that
    /// bbox. The capture is a continuous dark overlay on y435 (x78=(40,41,43),
    /// x100=(7,6,6), x200=(33,28,29), x300=(66,78,88), x400=(32,31,31),
    /// x540=(2,1,1), x562=(39,39,39); outside, x70/x570 stay mid-grey). A
    /// full-width rect is too solid in the middle but at least spans the bbox.
    ///
    /// FrontEnd\BarL/BarC/BarR.tga stay hash-pinned in FRONTEND_ASSETS. They
    /// are CFrontEnd::DrawBar (FrontEnd.cpp:1073) header-bar white masks
    /// (64x64 DXT2), not this page's sprite. CConsole__RenderLoadingScreen
    /// (0x0042C810) does not call DrawBar; its static callee list has one
    /// CVBufTexture__DrawSpriteEx and one CDXSurf__RenderSurface. Do not
    /// invent a DrawBar tile dest here. Draw the recovered sprite (texture,
    /// dest, tint, blend) only when that RenderLoadingScreen call is cited.
    /// Falsifier: local-lab/retail-reference-pristine/loading/07-loading-640x480.png.
    /// </summary>
    private void DrawLoading()
    {
        SelectSceneSection("Loading.Background");
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
        SelectSceneSection("Loading.Caption");
        var origin = new Vector2(LoadingTextLeft, LoadingTextTop);
        DrawFont22Outlined(_loadingText, origin + new Vector2(-1f, 1f), Colors.Black);
        DrawFont22Outlined(_loadingText, origin + new Vector2(1f, 1f), Colors.Black);
        DrawFont22Outlined(_loadingText, origin + new Vector2(-1f, -1f), Colors.Black);
        DrawFont22Outlined(_loadingText, origin + new Vector2(1f, -1f), Colors.Black);
        DrawFont22Outlined(_loadingText, origin, Colors.White);

        SelectSceneSection("Loading.Bar");
        DrawRect(
            new Rect2(LoadingBarLeft, LoadingBarTop, LoadingBarWidth, LoadingBarHeight),
            Colors.Black);
    }

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

    private void DrawFont22Outlined(string text, Vector2 position, Color color) =>
        DrawAtlasText(_font22, _font22Widths, Font22CellSize, Font22Columns, text,
            position, 1f, 1f, color, dropShadow: false);

    // Mirrors existing LoadLocalization admission and ordering. The production
    // host still uses its verified loader; standalone native editing uses the
    // same receipt rules, compared against this retained reference below.
    internal static string AdmitCaption(string source, string path = "res://Assets/Frontend/english.json")
    {
        if (string.IsNullOrEmpty(source)) throw new InvalidDataException($"Released frontend localization is missing: {path}");
        using JsonDocument document = JsonDocument.Parse(source);
        JsonElement root = document.RootElement;
        if (root.GetProperty("schema").GetString() != "onslaught.frontend-strings.v1" ||
            root.GetProperty("culture").GetString() != "en" ||
            root.GetProperty("sourceSha256").GetString() !=
                "789ecff619d077092769df281c540d138a25fcc74d70023466a604888e59371a")
            throw new InvalidDataException("Released frontend localization has unexpected identity.");
        JsonElement strings = root.GetProperty("strings");
        foreach (string key in new[] { "newGame", "continueGame", "loadGame", "multiplayer", "goodies", "options", "quit", "selectLevel" })
            RequiredString(strings, key);
        string level = RequiredString(strings, "level100");
        if (level != RetailFrontendWorldStrings.LevelName(100))
            throw new InvalidDataException("english.json level100 row diverged from the decoded world-strings table.");
        return RequiredString(strings, "loading");
    }
    private static string RequiredString(JsonElement strings, string key)
    {
        string? value = strings.GetProperty(key).GetString();
        return string.IsNullOrEmpty(value)
            ? throw new InvalidDataException($"Released frontend localization is missing '{key}'.") : value;
    }
}
