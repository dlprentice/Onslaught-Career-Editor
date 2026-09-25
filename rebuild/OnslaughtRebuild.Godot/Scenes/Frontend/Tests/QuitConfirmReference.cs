// SPDX-License-Identifier: GPL-3.0-or-later
using Godot;
using OnslaughtRebuild.Client;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Test-only retained Quit dialog from 5390cb11 RetailFrontendFlow.cs and its
/// original authored Frontend.tscn Dialog (110,170; 420x160; same SourceRect).
/// Drawing, glyph measurement, color conversion and half-open hit laws remain
/// unchanged; only the session selection and section dispatch are reduced to
/// this single dialog. RetailFeMessBox retains the provenance: height 140 is
/// reconstruction, FEMessBox.cpp is absent, and no retail quit capture exists.
/// This is an old-renderer comparison, not new retail visual-parity evidence.
/// </summary>
public sealed partial class QuitConfirmReference : Control
{
    internal const string Prompt = "Are you sure you want to quit the game?";
    private const string QuitConfirmPrompt = Prompt;
    private const int GlyphColumns = 16, GlyphCellSize = 16, FirstGlyph = 32, GlyphSlotCount = 256;
    private const int Font22Columns = 16, Font22CellSize = 32;
    private Texture2D _feBlank = null!, _titleFont = null!, _font22 = null!;
    private int[] _glyphWidths = [], _font22Widths = [];
    private int _selectedIndex;
    private bool _initialized;
    private Rect2 _sourceRect = new(110, 170, 420, 160);
    [Export] public Rect2 SourceRect { get => _sourceRect; set { _sourceRect = value; QueueRedraw(); } }
    internal Texture2D Blank => _feBlank;
    internal Texture2D BodyFont => _titleFont;
    internal Texture2D ChoiceFont => _font22;
    internal int[] BodyWidths => _glyphWidths.ToArray();
    internal int[] ChoiceWidths => _font22Widths.ToArray();
    internal Vector2 PromptOrigin => new(RetailFeMessBox.QuitCenterX - (MeasureText(QuitConfirmPrompt, 1f) * 0.5f), RetailFeMessBox.PromptTop);
    internal Vector2 ChoiceOrigin(int index) => new(RetailFeMessBox.QuitCenterX - (MeasureFont22Text(index == 1 ? RetailFeMessBox.YesLabel : RetailFeMessBox.NoLabel, 1f) * 0.5f), index == 1 ? RetailFeMessBox.YesChoiceTop : RetailFeMessBox.NoChoiceTop);
    internal Rect2 HighlightRect(int index)
    {
        string label = index == 1 ? RetailFeMessBox.YesLabel : RetailFeMessBox.NoLabel;
        float width = MeasureFont22Text(label, 1f);
        float left = RetailFeMessBox.QuitCenterX - (width * 0.5f);
        float top = index == 1 ? RetailFeMessBox.YesChoiceTop : RetailFeMessBox.NoChoiceTop;
        return new Rect2(left - RetailFeMessBox.HighlightPadX, top,
            width + (RetailFeMessBox.HighlightPadX * 2f), RetailFeMessBox.ChoiceRowHeight);
    }
    internal Transform2D SourceTransform()
    {
        // Exact original DrawSetTransform composition, including the identity
        // measured transform passed by DrawScenePart before selecting Quit.
        Vector2 ratio = Size / SourceRect.Size;
        var authored = new Transform2D(new Vector2(ratio.X, 0f), new Vector2(0f, ratio.Y),
            -SourceRect.Position * ratio);
        var measured = new Transform2D(0f, Vector2.One, 0f, Vector2.Zero);
        return authored * measured;
    }
    internal void Initialize()
    {
        if (_initialized) throw new InvalidOperationException("The retained dialog is already initialized.");
        _feBlank = LegacyCuratedAyaTextureReference.Load("res://Assets/PauseMenu/blank.texture.aya", 16, 16, LegacyCuratedAyaTextureReference.Compression.Dxt1);
        _titleFont = LegacyCuratedAyaTextureReference.Load("res://Assets/Hud/font-13ps.texture.aya", 256, 256, LegacyCuratedAyaTextureReference.Compression.Rgba8);
        _font22 = LegacyCuratedAyaTextureReference.Load("res://Assets/Hud/font-22.texture.aya", 512, 512, LegacyCuratedAyaTextureReference.Compression.Rgba8);
        using Image body = _titleFont.GetImage(); using Image choice = _font22.GetImage();
        _glyphWidths = MeasureGlyphWidths(body, GlyphCellSize, GlyphColumns);
        _font22Widths = MeasureGlyphWidths(choice, Font22CellSize, Font22Columns);
        _initialized = true;
    }
    internal void SetFrame(int selectedIndex)
    {
        if (selectedIndex is < 0 or > 1) throw new ArgumentOutOfRangeException(nameof(selectedIndex));
        _selectedIndex = selectedIndex; QueueRedraw();
    }
    public override void _Ready()
    {
        if (!_initialized) Initialize();
        SetProcess(false); SetProcessInput(false); SetProcessUnhandledInput(false);
    }
    public override void _Draw()
    {
        if (!_initialized || SourceRect.Size.X <= 0f || SourceRect.Size.Y <= 0f) return;
        DrawSetTransformMatrix(SourceTransform());
        DrawQuitConfirm();
    }
    public override void _Notification(int what)
    {
        if (what == NotificationResized) QueueRedraw();
    }

    private void DrawQuitConfirm()
    {
        // Create() width/centre are pinned on RetailFeMessBox. Height is still
        // reconstruction (the 4th stack immediate is 0.1f). Chrome below is
        // FrontEnd.cpp DrawPanel/DrawBox plus the option_mode-2 YESNO stack,
        // not FEMessBox.cpp tiles — that file is absent and there is no
        // quit-confirm capture.
        var box = new Rect2(
            RetailFeMessBox.QuitLeft,
            RetailFeMessBox.BoxTop,
            RetailFeMessBox.QuitWidth,
            RetailFeMessBox.ReconstructionHeight);
        DrawTextureRect(_feBlank, box, false, RetailColor(RetailFeMessBox.PanelColor));
        DrawFeMessBoxEdges(box, RetailColor(RetailFeMessBox.BorderColor));

        Color text = RetailColor(RetailFeMessBox.TextColor);
        float promptWidth = MeasureText(QuitConfirmPrompt, 1f);
        DrawText(
            QuitConfirmPrompt,
            new Vector2(RetailFeMessBox.QuitCenterX - (promptWidth * 0.5f), RetailFeMessBox.PromptTop),
            1f,
            text);

        DrawQuitConfirmChoice(
            RetailFeMessBox.YesLabel,
            RetailFeMessBox.YesChoiceTop,
            _selectedIndex == 1);
        DrawQuitConfirmChoice(
            RetailFeMessBox.NoLabel,
            RetailFeMessBox.NoChoiceTop,
            _selectedIndex == 0);
    }

    private void DrawQuitConfirmChoice(string label, float top, bool selected)
    {
        float width = MeasureFont22Text(label, 1f);
        float left = RetailFeMessBox.QuitCenterX - (width * 0.5f);
        if (selected)
        {
            DrawTextureRect(
                _feBlank,
                new Rect2(
                    left - RetailFeMessBox.HighlightPadX,
                    top,
                    width + (RetailFeMessBox.HighlightPadX * 2f),
                    RetailFeMessBox.ChoiceRowHeight),
                false,
                RetailColor(RetailFeMessBox.HighlightColor));
        }

        DrawFont22Text(label, new Vector2(left, top), 1f, 1f, RetailColor(RetailFeMessBox.TextColor));
    }

    private void DrawFeMessBoxEdges(Rect2 box, Color color)
    {
        float w = RetailFeMessBox.BoxLineWidth;
        DrawRect(new Rect2(box.Position.X, box.Position.Y, box.Size.X, w), color);
        DrawRect(new Rect2(box.Position.X, box.End.Y - w, box.Size.X, w), color);
        DrawRect(new Rect2(box.Position.X, box.Position.Y, w, box.Size.Y), color);
        DrawRect(new Rect2(box.End.X - w, box.Position.Y, w, box.Size.Y), color);
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
    /// measurably non-uniform (see the original briefing level-name scales).
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

    internal static int HitTest(Vector2 designPosition)
    {
        var noRow = new Rect2(
            RetailFeMessBox.QuitLeft,
            RetailFeMessBox.NoChoiceTop,
            RetailFeMessBox.QuitWidth,
            RetailFeMessBox.ChoiceRowHeight);
        if (noRow.HasPoint(designPosition))
        {
            return 0;
        }

        var yesRow = new Rect2(
            RetailFeMessBox.QuitLeft,
            RetailFeMessBox.YesChoiceTop,
            RetailFeMessBox.QuitWidth,
            RetailFeMessBox.ChoiceRowHeight);
        if (yesRow.HasPoint(designPosition))
        {
            return 1;
        }

        return -1;
    }

    private static Color RetailColor(uint argb) => new(
        Modulate2X((argb >> 16) & 0xff),
        Modulate2X((argb >> 8) & 0xff),
        Modulate2X(argb & 0xff),
        ((argb >> 24) & 0xff) / 255f);

    private static float Modulate2X(uint channel) =>
        Math.Min(255u, (channel * 255u) >> 7) / 255f;

}
