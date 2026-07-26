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
                "res://Assets/PauseMenu/endcurve.texture.aya",
                32,
                32),
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

        // Retail confirmation-prompt framing.
        //
        // CPauseMenu__Render (0x004d11d0) renders exactly one range out of the
        // pause range set -- CSPtrSet__At(this+0x14, this+0x24) -- and then
        // renders the optional prompt objects hanging off this+0x08 and
        // this+0x3c. Activating Retry (item 0x0cada9) or Quit (item 0x07a211)
        // in CPauseMenu__ButtonPressed (0x004d0810) allocates a CGameMenu into
        // this+0x08 and leaves the active range index this+0x24 at 0, so retail
        // does keep drawing the root list underneath the prompt.
        //
        // What keeps that legible is not a tint choice: the prompt range is
        // built by CMenuItemRangeVariant__Init(range, text 0x077780, 320.0,
        // 320.0, panel_flag=1, ...). CMenuItemRange__Render (0x004a4810) tests
        // that panel flag at +0x28 and, when set, calls
        // CMessageLog__RenderPanelFrame (0x004b9010) for an opaque frame behind
        // the prompt's own title and items. The root list carries panel_flag=0
        // (PauseMenu__Init 0x004cde60) and therefore never gets a frame.
        //
        // Every scalar below is read out of the pristine BEA.exe .rdata
        // (sha256 e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4):
        //   _DAT_005dc240 = 1.1     file 0x1dc240  panel size factor
        //   _DAT_005d85ec = 0.5     file 0x1d85ec  centring halve
        //   _DAT_005dc568 = 160.0   file 0x1dc568  panel alpha scale
        //   _DAT_005db2b8 = 32.0    file 0x1db2b8  corner size
        //   _DAT_005dbb50 = 0.0625  file 0x1dbb50  edge stretch over the 16px blank
        // The alpha argument at the call site is 1.2, so the frame tint is
        // ROUND(1.2 * 160.0) = 192 over RGB 0 -- pure black, alpha 192/255,
        // the same 192 ceiling the fullscreen pause fade already uses.
        private const float PanelSizeFactor = 1.1f;
        private const float PanelTitleBand = 32f;
        private const float PanelWidthPadding = 16f;
        private const float PanelMinimumSize = 64f;
        private const float PanelCornerSize = 32f;

        private static readonly Color PanelTint = new(0f, 0f, 0f, 192f / 255f);

        private static readonly Color NormalColor = RetailColor(0xffd6d6d6);
        private static readonly Color SelectedColor = RetailColor(0xffffcc00);
        private static readonly Color DisabledColor = RetailColor(0x50505050);
        private static readonly Color TitleColor = RetailColor(0xff505050);

        private readonly Texture2D _blank;
        private readonly Texture2D _circle01;
        private readonly Texture2D _circle02;
        private readonly Texture2D _endCurve;
        private readonly RetailBitmapFont _normalFont;
        private readonly RetailBitmapFont _smallFont;
        private float _openingSeconds;
        private float _closingSeconds;

        public RetailPauseSurface(
            Level100PauseMenu model,
            Texture2D blank,
            Texture2D circle01,
            Texture2D circle02,
            Texture2D endCurve,
            Texture2D normalFont,
            Texture2D smallFont)
        {
            Model = model;
            _blank = blank;
            _circle01 = circle01;
            _circle02 = circle02;
            _endCurve = endCurve;
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
                    Level100PausePage.Root,
                    panelFrame: false);
                DrawMenuRange(
                    "Are you sure?",
                    Model.Entries,
                    Model.SelectedIndex,
                    Model.Page,
                    panelFrame: true);
                return;
            }

            DrawMenuRange(
                "PAUSED",
                Model.Entries,
                Model.SelectedIndex,
                Model.Page,
                panelFrame: false);
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
            Level100PausePage page,
            bool panelFrame)
        {
            if (panelFrame)
            {
                DrawPanelFrame(title, entries, page);
            }

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

        /// <summary>
        /// Reproduces the retail panel frame that CMenuItemRange__Render draws
        /// for a panel-flagged range, sized by the same measurement pass:
        /// width comes from max(title extent, widest item) + 0x10, height from
        /// 0x20 plus the summed item heights, both scaled by 1.1, positioned by
        /// halving the unclamped size about the range origin, and only then
        /// clamped to the 0x40 floor inside CMessageLog__RenderPanelFrame.
        /// </summary>
        private void DrawPanelFrame(
            string title,
            IReadOnlyList<Level100PauseEntry> entries,
            Level100PausePage page)
        {
            float widest = _normalFont.Measure(title);
            float itemHeights = 0f;
            foreach (Level100PauseEntry entry in entries)
            {
                widest = Math.Max(widest, _smallFont.Measure(entry.Label));
                itemHeights += ItemRowHeight;
            }

            float rawWidth = (widest + PanelWidthPadding) * PanelSizeFactor;
            float rawHeight = (PanelTitleBand + itemHeights) * PanelSizeFactor;
            float left = MathF.Round(320f - (rawWidth * 0.5f));
            float top = MathF.Round(GetRangeCenterY(page) - (rawHeight * 0.5f));
            float width = Math.Max(PanelMinimumSize, MathF.Round(rawWidth));
            float height = Math.Max(PanelMinimumSize, MathF.Round(rawHeight));

            // CMessageLog__RenderPanelFrame lays the frame out as four 32x32
            // corner sprites from MessageLog%endcurve.tga, four stretched edge
            // sprites from FrontEnd%v2%FE_Blank.tga, and a stretched centre
            // fill from the same blank.
            //
            // The end-curve texture is now materialized and decoded: 32x32,
            // FourCC DXT2, one mip, 1024 bytes of block data = exactly 64 4x4
            // blocks for a single 32x32 level. So PanelCornerSize 32 is the
            // texture's NATIVE size -- no sub-rect and no atlas -- which
            // independently agrees with _DAT_005DB2B8 = 32.0. The corner
            // sprites also pass scale (1.0, 1.0) where the edge and centre
            // blanks pass pixels * 0.0625 over a 16x16 blank, confirming the
            // corners are drawn unstretched.
            //
            // Its alpha is a filled quarter disc: 753 texels opaque, 208 clear,
            // 63 intermediate across the whole 4-bit ramp (a one-texel
            // antialiased edge), opaque toward the LOWER-LEFT. RGB is
            // effectively white (every opaque texel 246..255), so it acts as a
            // pure alpha mask under PanelTint. Straight alpha, not
            // premultiplied -- 31 of the 63 semi-transparent texels carry RGB
            // above their own alpha, which premultiplied data cannot.
            //
            // Per-corner mirroring is taken from CVBufTexture__DrawSpriteEx's
            // last four UV arguments in 0x004b9010. With the decoded
            // orientation all four then land opaque-toward-the-panel-interior,
            // and that self-consistency is the check that the flip table is
            // right.
            float innerWidth = width - (PanelCornerSize * 2f);
            float innerHeight = height - (PanelCornerSize * 2f);
            float right = left + width - PanelCornerSize;
            float bottom = top + height - PanelCornerSize;

            DrawPanelCorner(left, top, flipX: true, flipY: false);
            DrawPanelCorner(right, top, flipX: false, flipY: false);
            DrawPanelCorner(right, bottom, flipX: false, flipY: true);
            DrawPanelCorner(left, bottom, flipX: true, flipY: true);

            if (innerWidth > 0f)
            {
                DrawNativeRect(left + PanelCornerSize, top, innerWidth, PanelCornerSize);
                DrawNativeRect(left + PanelCornerSize, bottom, innerWidth, PanelCornerSize);
            }

            if (innerHeight > 0f)
            {
                DrawNativeRect(left, top + PanelCornerSize, PanelCornerSize, innerHeight);
                DrawNativeRect(right, top + PanelCornerSize, PanelCornerSize, innerHeight);
            }

            if (innerWidth > 0f && innerHeight > 0f)
            {
                DrawNativeRect(
                    left + PanelCornerSize,
                    top + PanelCornerSize,
                    innerWidth,
                    innerHeight);
            }
        }

        /// <summary>
        /// Draws one 32x32 end-curve corner cell, mirrored so its opaque
        /// quarter faces the panel interior. Mirroring is expressed as a
        /// negative <see cref="Rect2"/> extent, which is how the retail sprite
        /// call's swapped UV pair reads once the texture's native orientation
        /// (opaque lower-left) is accounted for.
        /// </summary>
        private void DrawPanelCorner(float x, float y, bool flipX, bool flipY)
        {
            float scale = ViewportScale;
            Vector2 origin = ToViewport(new Vector2(
                flipX ? x + PanelCornerSize : x,
                flipY ? y + PanelCornerSize : y));
            var extent = new Vector2(
                flipX ? -PanelCornerSize : PanelCornerSize,
                flipY ? -PanelCornerSize : PanelCornerSize) * scale;
            DrawTextureRect(_endCurve, new Rect2(origin, extent), false, PanelTint);
        }

        private void DrawNativeRect(float x, float y, float width, float height)
        {
            float scale = ViewportScale;
            DrawTextureRect(
                _blank,
                new Rect2(ToViewport(new Vector2(x, y)), new Vector2(width, height) * scale),
                false,
                PanelTint);
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

        // PauseMenu__Init builds the root range at (320, 240) for the in-game
        // mode flag; CPauseMenu__ButtonPressed builds the Retry/Quit prompt
        // range at (320, 320). Both origins are literal floats in those bodies.
        private static float GetRangeCenterY(Level100PausePage page) =>
            page is Level100PausePage.ConfirmRetry or Level100PausePage.ConfirmQuit
                ? 320f
                : 240f;

        private static float GetFirstRowY(Level100PausePage page, int rowCount) =>
            GetRangeCenterY(page) - (rowCount * ItemRowHeight * 0.5f) - RangeTopOffset + TitleGap;

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
