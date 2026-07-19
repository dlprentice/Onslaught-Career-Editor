// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

public sealed partial class FirstFlightHud : CanvasLayer
{
    private RetailHudBaseLayer _baseLayer = null!;
    private RetailHudGlowLayer _glowLayer = null!;
    private RetailHudTextLayer _textLayer = null!;

    public bool IsReadyForSmoke =>
        IsInstanceValid(_baseLayer) &&
        IsInstanceValid(_glowLayer) &&
        IsInstanceValid(_textLayer) &&
        _baseLayer.IsReady &&
        _glowLayer.IsReady &&
        _textLayer.IsReady;

    public void Initialize()
    {
        Texture2D crosshair = LoadHudTexture("crosshair-outline", 64, 64);
        Texture2D circleDarkener = LoadHudTexture("circle-darkener", 128, 128);
        Texture2D radioView = LoadHudTexture("radio-view", 128, 128);
        Texture2D weaponFill = LoadHudTexture("weapon-fill", 128, 128);
        Texture2D objectiveInnerCentre = LoadHudTexture("objective-inner-centre", 64, 128);
        Texture2D objectiveInnerLeft = LoadHudTexture("objective-inner-left", 64, 128);
        Texture2D objectiveInnerRight = LoadHudTexture("objective-inner-right", 64, 128);
        Texture2D objectiveLeft = LoadHudTexture("objective-left", 128, 128);
        Texture2D objectiveRight = LoadHudTexture("objective-right", 128, 128);

        _baseLayer = new RetailHudBaseLayer(
            crosshair,
            circleDarkener,
            radioView,
            weaponFill,
            objectiveInnerCentre,
            objectiveInnerLeft,
            objectiveInnerRight,
            objectiveLeft,
            objectiveRight);
        AddFullScreenControl(_baseLayer);

        _glowLayer = new RetailHudGlowLayer(
            LoadHudTexture(
                "radar-outline",
                128,
                128,
                CuratedAyaTextureLoader.Compression.Dxt1),
            LoadHudTexture(
                "weapon-outline",
                128,
                128,
                CuratedAyaTextureLoader.Compression.Dxt1));
        AddFullScreenControl(_glowLayer);

        _textLayer = new RetailHudTextLayer(
            LoadHudTexture(
                "font-13ps",
                256,
                256,
                CuratedAyaTextureLoader.Compression.Rgba8));
        AddFullScreenControl(_textLayer);
    }

    public void UpdateFromSnapshot(WorldSnapshot snapshot)
    {
        string objective = snapshot.Level100Phase switch
        {
            Level100OpeningPhase.ReachTargetZone1 => "REACH TARGET ZONE 1",
            Level100OpeningPhase.TargetZone1DispatchPending => "TARGET ZONE 1 REACHED",
            Level100OpeningPhase.ReachFiringRange => "PROCEED TO FIRING RANGE",
            Level100OpeningPhase.FiringRangeDispatchPending => "FIRING RANGE REACHED",
            _ => "OPENING SLICE COMPLETE",
        };
        _textLayer.SetText(objective);
    }

    public void MarkInputActivity()
    {
        // The released HUD has no persistent controls legend to reveal or fade.
    }

    private static Texture2D LoadHudTexture(
        string name,
        int width,
        int height,
        CuratedAyaTextureLoader.Compression compression = CuratedAyaTextureLoader.Compression.Dxt2)
    {
        return CuratedAyaTextureLoader.Load(
            $"res://Assets/Hud/{name}.texture.aya",
            width,
            height,
            compression);
    }

    private void AddFullScreenControl(Control control)
    {
        control.AnchorRight = 1f;
        control.AnchorBottom = 1f;
        control.MouseFilter = Control.MouseFilterEnum.Ignore;
        AddChild(control);
    }

    private readonly record struct RetailHudLayout(float Scale, Vector2 Origin)
    {
        private const float ReferenceWidth = 1600f;
        private const float ReferenceHeight = 900f;

        public static RetailHudLayout For(Vector2 size)
        {
            float scale = Mathf.Min(size.X / ReferenceWidth, size.Y / ReferenceHeight);
            return new RetailHudLayout(
                scale,
                new Vector2(
                    (size.X - (ReferenceWidth * scale)) * 0.5f,
                    (size.Y - (ReferenceHeight * scale)) * 0.5f));
        }

        public Rect2 Rect(float x, float y, float width, float height)
        {
            return new Rect2(
                Origin + (new Vector2(x, y) * Scale),
                new Vector2(width, height) * Scale);
        }

        public Vector2 Point(float x, float y)
        {
            return Origin + (new Vector2(x, y) * Scale);
        }
    }

    private sealed partial class RetailHudBaseLayer(
        Texture2D crosshair,
        Texture2D circleDarkener,
        Texture2D radioView,
        Texture2D weaponFill,
        Texture2D objectiveInnerCentre,
        Texture2D objectiveInnerLeft,
        Texture2D objectiveInnerRight,
        Texture2D objectiveLeft,
        Texture2D objectiveRight) : Control
    {
        private static readonly Color ObjectiveBacking = new(0.015f, 0.025f, 0.055f, 0.86f);
        private static readonly Color RadioBlue = new(0.10f, 0.34f, 1f, 0.92f);
        private static readonly Color WeaponGreen = new(0.24f, 1f, 0.38f, 0.82f);

        public bool IsReady =>
            crosshair.GetWidth() == 64 &&
            circleDarkener.GetWidth() == 128 &&
            radioView.GetWidth() == 128 &&
            weaponFill.GetWidth() == 128 &&
            objectiveInnerCentre.GetWidth() == 64 &&
            objectiveInnerLeft.GetWidth() == 64 &&
            objectiveInnerRight.GetWidth() == 64 &&
            objectiveLeft.GetWidth() == 128 &&
            objectiveRight.GetWidth() == 128;

        public override void _Draw()
        {
            RetailHudLayout layout = RetailHudLayout.For(Size);

            Rect2 central = layout.Rect(704f, 354f, 192f, 192f);
            DrawTextureRectRegion(
                circleDarkener,
                layout.Rect(726f, 376f, 148f, 148f),
                new Rect2(0f, 0f, 98f, 98f),
                new Color(1f, 1f, 1f, 0.28f));
            DrawRotatedTexture(weaponFill, central, Mathf.Pi * 0.5f, WeaponGreen);
            DrawTextureRect(
                crosshair,
                layout.Rect(752f, 402f, 96f, 96f),
                false,
                new Color(0.94f, 0.96f, 1f, 0.88f));

            DrawTextureRectRegion(
                radioView,
                layout.Rect(1480f, 780f, 112f, 112f),
                new Rect2(0f, 0f, 98f, 98f),
                RadioBlue);

            DrawTextureRect(
                objectiveInnerLeft,
                layout.Rect(638f, 789f, 64f, 128f),
                false,
                ObjectiveBacking);
            DrawTextureRect(
                objectiveInnerCentre,
                layout.Rect(702f, 789f, 210f, 128f),
                false,
                ObjectiveBacking);
            DrawTextureRect(
                objectiveInnerRight,
                layout.Rect(912f, 789f, 64f, 128f),
                false,
                ObjectiveBacking);
            DrawTextureRect(objectiveLeft, layout.Rect(610f, 789f, 128f, 128f), false);
            DrawTextureRect(objectiveRight, layout.Rect(870f, 789f, 128f, 128f), false);
        }

        private void DrawRotatedTexture(Texture2D texture, Rect2 rect, float rotation, Color modulate)
        {
            Vector2 center = rect.GetCenter();
            DrawSetTransform(center, rotation, Vector2.One);
            DrawTextureRect(
                texture,
                new Rect2(-rect.Size * 0.5f, rect.Size),
                false,
                modulate);
            DrawSetTransform(Vector2.Zero, 0f, Vector2.One);
        }
    }

    private sealed partial class RetailHudGlowLayer(
        Texture2D radarOutline,
        Texture2D weaponOutline) : Control
    {
        public bool IsReady => radarOutline.GetWidth() == 128 && weaponOutline.GetWidth() == 128;

        public override void _Ready()
        {
            Material = new CanvasItemMaterial
            {
                BlendMode = CanvasItemMaterial.BlendModeEnum.Add,
            };
        }

        public override void _Draw()
        {
            RetailHudLayout layout = RetailHudLayout.For(Size);
            DrawTextureRect(
                radarOutline,
                layout.Rect(8f, 772f, 128f, 128f),
                false,
                new Color(0.74f, 0.70f, 0.54f, 0.86f));

            Rect2 central = layout.Rect(704f, 354f, 192f, 192f);
            Vector2 center = central.GetCenter();
            DrawSetTransform(center, Mathf.Pi * 0.5f, Vector2.One);
            DrawTextureRect(
                weaponOutline,
                new Rect2(-central.Size * 0.5f, central.Size),
                false,
                new Color(0.82f, 0.82f, 0.76f, 0.76f));
            DrawSetTransform(Vector2.Zero, 0f, Vector2.One);
        }
    }

    private sealed partial class RetailHudTextLayer(Texture2D fontAtlas) : Control
    {
        private const int FirstGlyph = 32;
        private const int GlyphColumns = 16;
        private const int GlyphCellSize = 16;
        private const int GlyphAdvance = 8;
        private string _text = string.Empty;

        public bool IsReady => fontAtlas.GetWidth() == 256 && fontAtlas.GetHeight() == 256;

        public void SetText(string text)
        {
            if (string.Equals(_text, text, StringComparison.Ordinal))
            {
                return;
            }
            _text = text;
            QueueRedraw();
        }

        public override void _Draw()
        {
            if (_text.Length == 0)
            {
                return;
            }

            RetailHudLayout layout = RetailHudLayout.For(Size);
            float glyphScale = layout.Scale;
            float glyphAdvance = GlyphAdvance * glyphScale;
            float left = (Size.X - (_text.Length * glyphAdvance)) * 0.5f;
            float top = layout.Point(0f, 831f).Y;

            for (int index = 0; index < _text.Length; index++)
            {
                int code = _text[index];
                if (code is < FirstGlyph or >= FirstGlyph + 96)
                {
                    code = '?';
                }
                int glyph = code - FirstGlyph;
                var source = new Rect2(
                    (glyph % GlyphColumns) * GlyphCellSize,
                    (glyph / GlyphColumns) * GlyphCellSize,
                    GlyphCellSize,
                    GlyphCellSize);
                var destination = new Rect2(
                    left + (index * glyphAdvance) - (4f * glyphScale),
                    top,
                    GlyphCellSize * glyphScale,
                    GlyphCellSize * glyphScale);
                DrawTextureRectRegion(
                    fontAtlas,
                    destination,
                    source,
                    new Color(0.96f, 0.97f, 1f, 0.96f));
            }
        }
    }
}
