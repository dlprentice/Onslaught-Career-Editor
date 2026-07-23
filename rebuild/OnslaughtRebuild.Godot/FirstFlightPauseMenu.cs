// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Client;

namespace OnslaughtRebuild.GodotClient;

public sealed partial class FirstFlightPauseMenu : CanvasLayer
{
    private RetailPauseSurface _surface = null!;

    public bool InputReady => _surface.InputReady;

    public bool IsClosing => _surface.IsClosing;

    public void Initialize(Level100PauseMenu model)
    {
        Name = "Level100PauseMenu";
        Layer = 100;
        ProcessMode = ProcessModeEnum.Always;
        _surface = new RetailPauseSurface(
            model,
            CuratedAyaTextureLoader.Load(
                "res://Assets/PauseMenu/blank.texture.aya",
                16,
                16,
                CuratedAyaTextureLoader.Compression.Dxt1),
            CuratedAyaTextureLoader.Load(
                "res://Assets/PauseMenu/circle-01.texture.aya",
                256,
                256),
            CuratedAyaTextureLoader.Load(
                "res://Assets/PauseMenu/circle-02.texture.aya",
                256,
                256),
            CuratedAyaTextureLoader.Load(
                "res://Assets/Hud/font-22.texture.aya",
                512,
                512,
                CuratedAyaTextureLoader.Compression.Rgba8),
            CuratedAyaTextureLoader.Load(
                "res://Assets/Hud/font-13ps.texture.aya",
                256,
                256,
                CuratedAyaTextureLoader.Compression.Rgba8));
        _surface.AnchorRight = 1f;
        _surface.AnchorBottom = 1f;
        _surface.MouseFilter = Control.MouseFilterEnum.Ignore;
        AddChild(_surface);
    }

    public void Open() => _surface.BeginOpen();

    public void Close() => _surface.BeginClose();

    public void Reset() => _surface.Deactivate();

    public void AdvanceAnimation(double delta) => _surface.AdvanceAnimation(delta);

    public void Refresh() => _surface.QueueRedraw();

    public bool TryHover(Vector2 viewportPosition)
    {
        bool hit = TryPointAt(viewportPosition, out bool moved);
        return hit && moved;
    }

    public bool TryPointAt(Vector2 viewportPosition, out bool moved)
    {
        int index = _surface.HitTest(viewportPosition);
        if (index < 0 || !_surface.Model.Entries[index].IsEnabled)
        {
            moved = false;
            return false;
        }

        moved = _surface.Model.Hover(index);
        if (moved)
        {
            _surface.QueueRedraw();
        }
        return true;
    }

    private sealed partial class RetailPauseSurface : Control
    {
        private const float NativeWidth = 640f;
        private const float NativeHeight = 480f;
        private const float FadeSeconds = 0.4f;
        private const float CircleGrowSeconds = 0.2f;
        private const float ItemRowHeight = 20f;
        private const float TitleGap = 30f;
        private const float RangeTopOffset = 15f;

        private static readonly Color NormalColor = RetailColor(0xffd6d6d6);
        private static readonly Color SelectedColor = RetailColor(0xffffcc00);
        private static readonly Color DisabledColor = RetailColor(0x50505050);
        private static readonly Color TitleColor = RetailColor(0xff505050);

        private readonly Texture2D _blank;
        private readonly Texture2D _circle01;
        private readonly Texture2D _circle02;
        private readonly RetailBitmapFont _normalFont;
        private readonly RetailBitmapFont _smallFont;
        private float _openingSeconds;
        private float _closingSeconds;

        public RetailPauseSurface(
            Level100PauseMenu model,
            Texture2D blank,
            Texture2D circle01,
            Texture2D circle02,
            Texture2D normalFont,
            Texture2D smallFont)
        {
            Model = model;
            _blank = blank;
            _circle01 = circle01;
            _circle02 = circle02;
            _normalFont = new RetailBitmapFont(normalFont, 32);
            _smallFont = new RetailBitmapFont(smallFont, 16);
            Visible = false;
        }

        public Level100PauseMenu Model { get; }

        public bool InputReady =>
            Visible && !IsClosing && _openingSeconds >= FadeSeconds;

        public bool IsClosing { get; private set; }

        public void BeginOpen()
        {
            Visible = true;
            IsClosing = false;
            _openingSeconds = 0f;
            _closingSeconds = 0f;
            QueueRedraw();
        }

        public void BeginClose()
        {
            if (!Visible)
            {
                return;
            }

            IsClosing = true;
            _closingSeconds = 0f;
            QueueRedraw();
        }

        public void Deactivate()
        {
            Visible = false;
            IsClosing = false;
            _openingSeconds = 0f;
            _closingSeconds = 0f;
        }

        public void AdvanceAnimation(double delta)
        {
            if (!Visible || !double.IsFinite(delta) || delta <= 0d)
            {
                return;
            }

            if (IsClosing)
            {
                _closingSeconds += (float)delta;
                if (_closingSeconds >= FadeSeconds)
                {
                    Deactivate();
                }
            }
            else
            {
                _openingSeconds = Math.Min(_openingSeconds + (float)delta, FadeSeconds);
            }
            QueueRedraw();
        }

        public int HitTest(Vector2 viewportPosition)
        {
            if (!InputReady || Size.Y <= 0f)
            {
                return -1;
            }

            Vector2 native = ToNative(viewportPosition);
            if (native.X < 0f || native.X > NativeWidth)
            {
                return -1;
            }

            IReadOnlyList<Level100PauseEntry> entries = Model.Entries;
            float firstRow = GetFirstRowY(Model.Page, entries.Count);
            for (int index = 0; index < entries.Count; index++)
            {
                float top = firstRow + (index * ItemRowHeight);
                if (native.Y >= top && native.Y < top + ItemRowHeight)
                {
                    return index;
                }
            }
            return -1;
        }

        public override void _Draw()
        {
            if (!Visible || Size.X <= 0f || Size.Y <= 0f)
            {
                return;
            }

            float transitionSeconds = IsClosing
                ? Math.Max(0f, FadeSeconds - _closingSeconds)
                : _openingSeconds;
            float overlayAlpha = Math.Clamp(
                (float)Math.Round(transitionSeconds * 480f) / 255f,
                0f,
                192f / 255f);
            DrawTextureRect(
                _blank,
                new Rect2(Vector2.Zero, Size),
                false,
                new Color(16f / 255f, 16f / 255f, 16f / 255f, overlayAlpha));
            DrawPauseCircles(transitionSeconds);

            if (transitionSeconds < FadeSeconds)
            {
                return;
            }

            if (Model.Page is Level100PausePage.ConfirmRetry or Level100PausePage.ConfirmQuit)
            {
                DrawMenuRange(
                    "PAUSED",
                    Model.RootEntries,
                    Model.UnderlyingRootSelection,
                    Level100PausePage.Root);
                DrawMenuRange("Are you sure?", Model.Entries, Model.SelectedIndex, Model.Page);
                return;
            }

            DrawMenuRange("PAUSED", Model.Entries, Model.SelectedIndex, Model.Page);
        }

        private void DrawPauseCircles(float transitionSeconds)
        {
            float circleScale = transitionSeconds < CircleGrowSeconds
                ? 0.1f + (transitionSeconds * 5f * 1.1f)
                : 1.2f;
            float rotation = transitionSeconds < CircleGrowSeconds
                ? 0f
                : Math.Clamp(transitionSeconds, CircleGrowSeconds, FadeSeconds) -
                    CircleGrowSeconds;
            DrawNativeTextureRotated(_circle01, circleScale, -rotation);
            DrawNativeTextureRotated(_circle02, circleScale, rotation);
        }

        private void DrawMenuRange(
            string title,
            IReadOnlyList<Level100PauseEntry> entries,
            int selectedIndex,
            Level100PausePage page)
        {
            float firstRow = GetFirstRowY(page, entries.Count);
            _normalFont.DrawCentered(
                this,
                title,
                320f,
                firstRow - TitleGap,
                TitleColor,
                shadow: false);
            for (int index = 0; index < entries.Count; index++)
            {
                Level100PauseEntry entry = entries[index];
                Color color = !entry.IsEnabled
                    ? DisabledColor
                    : index == selectedIndex ? SelectedColor : NormalColor;
                _smallFont.DrawCentered(
                    this,
                    entry.Label,
                    320f,
                    firstRow + (index * ItemRowHeight),
                    color,
                    shadow: true);
            }
        }

        private void DrawNativeTextureRotated(Texture2D texture, float nativeScale, float rotation)
        {
            float viewportScale = ViewportScale;
            DrawSetTransform(
                ToViewport(new Vector2(320f, 240f)),
                rotation,
                Vector2.One * viewportScale * nativeScale);
            DrawTextureRect(
                texture,
                new Rect2(-128f, -128f, 256f, 256f),
                false,
                Colors.White);
            DrawSetTransform(Vector2.Zero, 0f, Vector2.One);
        }

        private Vector2 ToViewport(Vector2 native) =>
            new(HorizontalOffset + (native.X * ViewportScale), native.Y * ViewportScale);

        private Vector2 ToNative(Vector2 viewport) =>
            new(
                (viewport.X - HorizontalOffset) / ViewportScale,
                viewport.Y / ViewportScale);

        private float ViewportScale => Size.Y / NativeHeight;

        private float HorizontalOffset => (Size.X - (NativeWidth * ViewportScale)) * 0.5f;

        private static float GetFirstRowY(Level100PausePage page, int rowCount)
        {
            float centerY = page is Level100PausePage.ConfirmRetry or Level100PausePage.ConfirmQuit
                ? 320f
                : 240f;
            return centerY - (rowCount * ItemRowHeight * 0.5f) - RangeTopOffset + TitleGap;
        }

        private static Color RetailColor(uint argb) => new(
            ((argb >> 16) & 0xff) / 255f,
            ((argb >> 8) & 0xff) / 255f,
            (argb & 0xff) / 255f,
            ((argb >> 24) & 0xff) / 255f);

        private sealed class RetailBitmapFont
        {
            private const int FirstGlyph = 32;
            private const int GlyphColumns = 16;
            private const int GlyphCount = 96;

            private readonly Texture2D _atlas;
            private readonly int _cellSize;
            private readonly int[] _widths;

            public RetailBitmapFont(Texture2D atlas, int cellSize)
            {
                _atlas = atlas;
                _cellSize = cellSize;
                _widths = MeasureGlyphWidths(atlas.GetImage(), cellSize);
            }

            public float Measure(string text)
            {
                float width = 0f;
                foreach (char character in text)
                {
                    int code = character is >= (char)FirstGlyph and < (char)(FirstGlyph + GlyphCount)
                        ? character
                        : '?';
                    width += _widths[code - FirstGlyph] + 1f;
                }
                return Math.Max(0f, width - 1f);
            }

            public void DrawCentered(
                RetailPauseSurface surface,
                string text,
                float centerX,
                float y,
                Color color,
                bool shadow)
            {
                float x = centerX - (Measure(text) * 0.5f);
                foreach (char character in text)
                {
                    int code = character is >= (char)FirstGlyph and < (char)(FirstGlyph + GlyphCount)
                        ? character
                        : '?';
                    int glyph = code - FirstGlyph;
                    int width = _widths[glyph];
                    if (shadow)
                    {
                        DrawGlyph(surface, glyph, x + 1f, y + 1f, width, Colors.Black);
                    }
                    DrawGlyph(surface, glyph, x, y, width, color);
                    x += width + 1f;
                }
            }

            private void DrawGlyph(
                RetailPauseSurface surface,
                int glyph,
                float x,
                float y,
                int width,
                Color color)
            {
                var source = new Rect2(
                    (glyph % GlyphColumns) * _cellSize,
                    (glyph / GlyphColumns) * _cellSize,
                    width,
                    _cellSize);
                float scale = surface.ViewportScale;
                surface.DrawTextureRectRegion(
                    _atlas,
                    new Rect2(
                        surface.ToViewport(new Vector2(x, y)),
                        new Vector2(width, _cellSize) * scale),
                    source,
                    color);
            }

            private static int[] MeasureGlyphWidths(Image image, int cellSize)
            {
                var widths = new int[GlyphCount];
                widths[0] = cellSize / 2;
                for (int glyph = 1; glyph < widths.Length; glyph++)
                {
                    int cellX = (glyph % GlyphColumns) * cellSize;
                    int cellY = (glyph / GlyphColumns) * cellSize;
                    int rightmost = cellX;
                    for (int x = cellX + cellSize - 2; x >= cellX; x--)
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
        }
    }
}
