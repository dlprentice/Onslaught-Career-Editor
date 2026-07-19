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

    public int Level100ObjectiveMarkerCount => _glowLayer.ObjectiveMarkerCount;

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
        Texture2D tatianaPortrait = LoadHudTexture("tatiana-portrait", 128, 128);
        Texture2D technicianPortrait = LoadHudTexture("technician-portrait", 128, 128);

        _baseLayer = new RetailHudBaseLayer(
            crosshair,
            circleDarkener,
            radioView,
            weaponFill,
            objectiveInnerCentre,
            objectiveInnerLeft,
            objectiveInnerRight,
            objectiveLeft,
            objectiveRight,
            tatianaPortrait,
            technicianPortrait);
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
                CuratedAyaTextureLoader.Compression.Dxt1),
            LoadHudTexture("compass-objective-marker", 16, 16));
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
        _glowLayer.SetObjectiveMarker(snapshot);
        string? message = GetTutorialMessageText(snapshot.Level100Message);
        if (message is not null)
        {
            _baseLayer.SetSpeaker(snapshot.Level100Message == Level100TutorialMessage.TechnicianStatus
                ? RetailHudSpeaker.Technician
                : RetailHudSpeaker.Tatiana);
            _textLayer.SetMessage(message);
            return;
        }

        _baseLayer.SetSpeaker(RetailHudSpeaker.None);
        string objective = snapshot.Level100Phase switch
        {
            Level100OpeningPhase.Briefing => string.Empty,
            Level100OpeningPhase.ReachTargetZone1 => "REACH TARGET ZONE 1",
            Level100OpeningPhase.TargetZone1DispatchPending => "TARGET ZONE 1 REACHED",
            Level100OpeningPhase.ReachFiringRange => "PROCEED TO FIRING RANGE",
            Level100OpeningPhase.FiringRangeDispatchPending => "FIRING RANGE REACHED",
            _ => "OPENING SLICE COMPLETE",
        };
        _textLayer.SetObjective(objective);
    }

    private static string? GetTutorialMessageText(Level100TutorialMessage message) => message switch
    {
        Level100TutorialMessage.HudIntroduction =>
            "Welcome aboard. Now don't touch anything and I'll take you through the instrumentation you see before you.",
        Level100TutorialMessage.ThreatCircle =>
            "This is the threat circle. That notch indicates North. As for its other functions, I'll demonstrate them later.",
        Level100TutorialMessage.Scanner =>
            "The circle to the left is your scanner. Enemy units show up in red, friendly units in blue.",
        Level100TutorialMessage.MessageLog =>
            "If you ever need to review these messages, check out Aquila's message log in the Pause Menu.",
        Level100TutorialMessage.TechnicianStatus => "All systems nominal.",
        Level100TutorialMessage.MovementControls =>
            "You have two primary controls.  One determines the direction of travel, and the other changes which way Aquila faces.",
        Level100TutorialMessage.ReachTargetZone1 =>
            "Okay, Hawk? I want you to manoeuvre the Battle Engine to the area marked on your HUD.",
        Level100TutorialMessage.ScannerObjective =>
            "Notice how objectives that you are given are marked as yellow dots on your scanner.",
        Level100TutorialMessage.FiringRangeInstruction =>
            "Now make your way to the firing range for target practice. I'll mark the location on your HUD again.",
        _ => null,
    };

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

    private enum RetailHudSpeaker
    {
        None,
        Tatiana,
        Technician,
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
        Texture2D objectiveRight,
        Texture2D tatianaPortrait,
        Texture2D technicianPortrait) : Control
    {
        private static readonly Color ObjectiveBacking = new(0.015f, 0.025f, 0.055f, 0.86f);
        private static readonly Color RadioBlue = new(0.10f, 0.34f, 1f, 0.92f);
        private static readonly Color WeaponGreen = new(0.24f, 1f, 0.38f, 0.82f);
        private RetailHudSpeaker _speaker;

        public bool IsReady =>
            crosshair.GetWidth() == 64 &&
            circleDarkener.GetWidth() == 128 &&
            radioView.GetWidth() == 128 &&
            weaponFill.GetWidth() == 128 &&
            objectiveInnerCentre.GetWidth() == 64 &&
            objectiveInnerLeft.GetWidth() == 64 &&
            objectiveInnerRight.GetWidth() == 64 &&
            objectiveLeft.GetWidth() == 128 &&
            objectiveRight.GetWidth() == 128 &&
            tatianaPortrait.GetWidth() == 128 &&
            technicianPortrait.GetWidth() == 128;

        public void SetSpeaker(RetailHudSpeaker speaker)
        {
            if (_speaker == speaker)
            {
                return;
            }
            _speaker = speaker;
            QueueRedraw();
        }

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

            Texture2D? portrait = _speaker switch
            {
                RetailHudSpeaker.Tatiana => tatianaPortrait,
                RetailHudSpeaker.Technician => technicianPortrait,
                _ => null,
            };
            if (portrait is not null)
            {
                DrawTextureRect(portrait, layout.Rect(1480f, 780f, 112f, 112f), false);
            }
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
        Texture2D weaponOutline,
        Texture2D objectiveMarker) : Control
    {
        private const float RadarWorldRadius = 46f;
        private bool _objectiveMarkerVisible;
        private Vector2 _objectiveMarkerOffset;

        public bool IsReady =>
            radarOutline.GetWidth() == 128 &&
            weaponOutline.GetWidth() == 128 &&
            objectiveMarker.GetWidth() == 16 &&
            objectiveMarker.GetHeight() == 16;

        public int ObjectiveMarkerCount => _objectiveMarkerVisible ? 1 : 0;

        public override void _Ready()
        {
            Material = new CanvasItemMaterial
            {
                BlendMode = CanvasItemMaterial.BlendModeEnum.Add,
            };
        }

        public void SetObjectiveMarker(WorldSnapshot snapshot)
        {
            SimVector2? objective = snapshot.Level100Phase switch
            {
                Level100OpeningPhase.ReachTargetZone1 or
                    Level100OpeningPhase.TargetZone1DispatchPending =>
                        SimulationConstants.Level100TargetZone1Position,
                Level100OpeningPhase.ReachFiringRange or
                    Level100OpeningPhase.FiringRangeDispatchPending =>
                        SimulationConstants.Level100FiringRangePosition,
                _ => null,
            };
            if (!objective.HasValue)
            {
                SetMarkerState(false, Vector2.Zero);
                return;
            }

            float deltaX = (objective.Value.X - snapshot.PlayerPosition.X) / 1_000f;
            float deltaZ = (objective.Value.Z - snapshot.PlayerPosition.Z) / 1_000f;
            float distanceSquared = (deltaX * deltaX) + (deltaZ * deltaZ);
            float yaw = snapshot.FacingYawMicroRad / 1_000_000f;
            float sin = Mathf.Sin(yaw);
            float cos = Mathf.Cos(yaw);
            var offset = new Vector2(
                (deltaX * cos) - (deltaZ * sin),
                -((deltaX * sin) + (deltaZ * cos)));
            float distance = Mathf.Sqrt(distanceSquared);
            if (distance > RadarWorldRadius)
            {
                offset *= RadarWorldRadius / distance;
            }

            SetMarkerState(true, offset);
        }

        public override void _Draw()
        {
            RetailHudLayout layout = RetailHudLayout.For(Size);
            DrawTextureRect(
                radarOutline,
                layout.Rect(8f, 772f, 128f, 128f),
                false,
                new Color(0.74f, 0.70f, 0.54f, 0.86f));
            if (_objectiveMarkerVisible)
            {
                Vector2 radarCenter = layout.Point(69f, 836f) + (_objectiveMarkerOffset * layout.Scale);
                DrawTextureRect(
                    objectiveMarker,
                    new Rect2(radarCenter - (Vector2.One * 8f * layout.Scale), Vector2.One * 16f * layout.Scale),
                    false,
                    new Color(1f, 1f, 0f, 1f));
            }

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

        private void SetMarkerState(bool visible, Vector2 offset)
        {
            if (_objectiveMarkerVisible == visible &&
                _objectiveMarkerOffset.IsEqualApprox(offset))
            {
                return;
            }

            _objectiveMarkerVisible = visible;
            _objectiveMarkerOffset = offset;
            QueueRedraw();
        }
    }

    private sealed partial class RetailHudTextLayer(Texture2D fontAtlas) : Control
    {
        private const int FirstGlyph = 32;
        private const int GlyphColumns = 16;
        private const int GlyphCellSize = 16;
        private const int GlyphAdvance = 8;
        private const int MessageCharactersPerLine = 40;
        private string[] _lines = [];
        private bool _centered;

        public bool IsReady => fontAtlas.GetWidth() == 256 && fontAtlas.GetHeight() == 256;

        public void SetObjective(string text)
        {
            SetLines([text], centered: true);
        }

        public void SetMessage(string text)
        {
            SetLines(WrapMessage(text), centered: false);
        }

        public override void _Draw()
        {
            if (_lines.Length == 0 || _lines.All(string.IsNullOrEmpty))
            {
                return;
            }

            RetailHudLayout layout = RetailHudLayout.For(Size);
            float glyphScale = layout.Scale;
            float glyphAdvance = GlyphAdvance * glyphScale;
            float top = layout.Point(0f, _centered ? 831f : 817f).Y;
            float lineAdvance = 17f * glyphScale;
            for (int lineIndex = 0; lineIndex < _lines.Length; lineIndex++)
            {
                string line = _lines[lineIndex];
                float left = _centered
                    ? (Size.X - (line.Length * glyphAdvance)) * 0.5f
                    : layout.Point(650f, 0f).X;
                for (int index = 0; index < line.Length; index++)
                {
                    int code = line[index];
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
                        top + (lineIndex * lineAdvance),
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

        private void SetLines(string[] lines, bool centered)
        {
            if (_centered == centered && _lines.SequenceEqual(lines, StringComparer.Ordinal))
            {
                return;
            }
            _lines = lines;
            _centered = centered;
            QueueRedraw();
        }

        private static string[] WrapMessage(string text)
        {
            var lines = new List<string>();
            var current = new System.Text.StringBuilder();
            foreach (string word in text.Split(' ', StringSplitOptions.RemoveEmptyEntries))
            {
                if (current.Length > 0 && current.Length + 1 + word.Length > MessageCharactersPerLine)
                {
                    lines.Add(current.ToString());
                    current.Clear();
                }
                if (current.Length > 0)
                {
                    current.Append(' ');
                }
                current.Append(word);
            }
            if (current.Length > 0)
            {
                lines.Add(current.ToString());
            }
            return lines.ToArray();
        }
    }
}
