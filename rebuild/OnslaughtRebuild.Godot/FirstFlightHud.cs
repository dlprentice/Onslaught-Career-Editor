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

    public int Level100ObjectiveMarkerCount => _baseLayer.ObjectiveMarkerCount;

    public void Initialize()
    {
        _baseLayer = new RetailHudBaseLayer(
            LoadHudTexture("circle-darkener", 128, 128),
            LoadHudTexture("circle-mask", 128, 128),
            LoadHudTexture("radio-view", 128, 128),
            LoadHudTexture("weapon-fill", 128, 128),
            LoadHudTexture("radio-north", 32, 32),
            LoadHudTexture("scanner-blob-small", 16, 16),
            LoadHudTexture("crosshair-primary", 64, 64),
            LoadHudTexture("crosshair-secondary", 128, 128),
            LoadHudTexture("crosshair-dot", 64, 64),
            LoadHudTexture("objective-inner-centre", 64, 128),
            LoadHudTexture("objective-inner-left", 64, 128),
            LoadHudTexture("objective-inner-right", 64, 128),
            LoadHudTexture("objective-left", 128, 128),
            LoadHudTexture("objective-right", 128, 128),
            [
                LoadHudTexture("tatiana-portrait-oo", 128, 128),
                LoadHudTexture("tatiana-portrait-ee", 128, 128),
                LoadHudTexture("tatiana-portrait-mm", 128, 128),
                LoadHudTexture("tatiana-portrait", 128, 128),
            ],
            [
                LoadHudTexture("technician-portrait-oo", 128, 128),
                LoadHudTexture("technician-portrait-ee", 128, 128),
                LoadHudTexture("technician-portrait-mm", 128, 128),
                LoadHudTexture("technician-portrait", 128, 128),
            ]);
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
            LoadHudTexture(
                "battleline-outline",
                128,
                128,
                CuratedAyaTextureLoader.Compression.Dxt1),
            LoadHudTexture(
                "message-noise",
                128,
                128,
                CuratedAyaTextureLoader.Compression.Dxt1),
            LoadHudTexture(
                "bar-line",
                16,
                64,
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
        Vector2[] markerOffsets = GetMarkedPositions(snapshot)
            .Select(position => ProjectRadarOffset(snapshot, position))
            .ToArray();
        string? message = GetTutorialMessageText(snapshot.Level100Message);
        RetailHudSpeaker speaker = message is null
            ? RetailHudSpeaker.None
            : snapshot.Level100Message == Level100TutorialMessage.TechnicianStatus
                ? RetailHudSpeaker.Technician
                : RetailHudSpeaker.Tatiana;

        _baseLayer.SetState(snapshot, speaker, markerOffsets);
        _glowLayer.SetState(snapshot, message is not null, markerOffsets);
        if (message is null)
        {
            _textLayer.Clear();
        }
        else
        {
            _textLayer.SetMessage(message);
        }
    }

    private static SimVector2[] GetMarkedPositions(WorldSnapshot snapshot) => snapshot.Level100Phase switch
    {
        Level100OpeningPhase.ReachTargetZone1 or
            Level100OpeningPhase.TargetZone1DispatchPending =>
                [SimulationConstants.Level100TargetZone1Position],
        Level100OpeningPhase.ReachFiringRange or
            Level100OpeningPhase.FiringRangeDispatchPending =>
                [SimulationConstants.Level100FiringRangePosition],
        _ when snapshot.Level100FiringRangeTargetsActive =>
            snapshot.Targets
                .Where(target => target.IsActive)
                .OrderBy(target => target.Id)
                .Select(target => target.Position)
                .ToArray(),
        _ => [],
    };

    private static Vector2 ProjectRadarOffset(WorldSnapshot snapshot, SimVector2 objective)
    {
        const float radarRadius = 46f;
        float deltaX = (objective.X - snapshot.PlayerPosition.X) / 1_000f;
        float deltaZ = (objective.Z - snapshot.PlayerPosition.Z) / 1_000f;
        float yaw = snapshot.FacingYawMicroRad / 1_000_000f;
        float sin = Mathf.Sin(yaw);
        float cos = Mathf.Cos(yaw);
        var offset = new Vector2(
            (deltaX * cos) - (deltaZ * sin),
            -((deltaX * sin) + (deltaZ * cos)));
        float distance = offset.Length();
        if (distance > radarRadius)
        {
            offset *= radarRadius / distance;
        }

        return offset;
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
        Level100TutorialMessage.WeaponSystems =>
            "In a moment we're going to activate your weapon systems.",
        Level100TutorialMessage.WeaponIndicator =>
            "Here is your weapon indicator. This shows you what weapon is currently selected. It also allows you to keep track of its temperature or remaining ammo level.",
        Level100TutorialMessage.PulseCannon =>
            "The IS-5 Pulse Cannon is your primary weapon. It can be fired rapidly or charged up to release a larger round.",
        Level100TutorialMessage.OpenFire =>
            "Now destroy the three tanks and that building marked on your HUD.",
        Level100TutorialMessage.PulseCannonEnergy =>
            "As an energy weapon it never runs out of ammo but it can overheat. It is most effective against enemy vehicles or buildings.",
        Level100TutorialMessage.VulcanCannon =>
            "Aquila is also equipped with a rapid-fire Vulcan Cannon. It has limited target tracking facilities, so it's really easy to use.",
        Level100TutorialMessage.OpenFireVulcan =>
            "There are 3 trucks nearby. Try the Vulcan Cannon on them.",
        Level100TutorialMessage.VulcanCannonAmmo =>
            "You have limited ammo with this one and it's only really effective against infantry or lightly armoured units.",
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

    private static Color RetailColor(uint argb) => new(
        ((argb >> 16) & 0xff) / 255f,
        ((argb >> 8) & 0xff) / 255f,
        (argb & 0xff) / 255f,
        ((argb >> 24) & 0xff) / 255f);

    private void AddFullScreenControl(Control control)
    {
        control.AnchorRight = 1f;
        control.AnchorBottom = 1f;
        control.MouseFilter = Control.MouseFilterEnum.Ignore;
        AddChild(control);
    }

    private enum RetailHudSpeaker
    {
        None,
        Tatiana,
        Technician,
    }

    private sealed partial class RetailHudBaseLayer(
        Texture2D circleDarkener,
        Texture2D circleMask,
        Texture2D radioView,
        Texture2D weaponFill,
        Texture2D radioNorth,
        Texture2D scannerBlobSmall,
        Texture2D crosshairPrimary,
        Texture2D crosshairSecondary,
        Texture2D crosshairDot,
        Texture2D objectiveInnerCentre,
        Texture2D objectiveInnerLeft,
        Texture2D objectiveInnerRight,
        Texture2D objectiveLeft,
        Texture2D objectiveRight,
        Texture2D[] tatianaPortraits,
        Texture2D[] technicianPortraits) : Control
    {
        private RetailHudSpeaker _speaker;
        private Vector2[] _objectiveMarkerOffsets = [];
        private float _facingYaw;
        private int _portraitPoseIndex = 3;
        private bool _weaponHighlighted;

        public bool IsReady =>
            circleDarkener.GetSize() == new Vector2I(128, 128) &&
            circleMask.GetSize() == new Vector2I(128, 128) &&
            radioView.GetSize() == new Vector2I(128, 128) &&
            weaponFill.GetSize() == new Vector2I(128, 128) &&
            radioNorth.GetSize() == new Vector2I(32, 32) &&
            scannerBlobSmall.GetSize() == new Vector2I(16, 16) &&
            crosshairPrimary.GetSize() == new Vector2I(64, 64) &&
            crosshairSecondary.GetSize() == new Vector2I(128, 128) &&
            crosshairDot.GetSize() == new Vector2I(64, 64) &&
            objectiveInnerCentre.GetSize() == new Vector2I(64, 128) &&
            objectiveInnerLeft.GetSize() == new Vector2I(64, 128) &&
            objectiveInnerRight.GetSize() == new Vector2I(64, 128) &&
            objectiveLeft.GetSize() == new Vector2I(128, 128) &&
            objectiveRight.GetSize() == new Vector2I(128, 128) &&
            PortraitSetIsReady(tatianaPortraits) &&
            PortraitSetIsReady(technicianPortraits);

        public int ObjectiveMarkerCount => _objectiveMarkerOffsets.Length;

        public void SetState(
            WorldSnapshot snapshot,
            RetailHudSpeaker speaker,
            Vector2[] objectiveMarkerOffsets)
        {
            float facingYaw = snapshot.FacingYawMicroRad / 1_000_000f;
            int portraitPoseIndex = speaker == RetailHudSpeaker.None
                ? 3
                : SelectPortraitPose(snapshot.Tick);
            bool weaponHighlighted = snapshot.Level100CurrentWeaponHighlighted;
            if (_speaker == speaker &&
                Mathf.IsEqualApprox(_facingYaw, facingYaw) &&
                _portraitPoseIndex == portraitPoseIndex &&
                _weaponHighlighted == weaponHighlighted &&
                _objectiveMarkerOffsets.SequenceEqual(objectiveMarkerOffsets))
            {
                return;
            }

            _speaker = speaker;
            _facingYaw = facingYaw;
            _portraitPoseIndex = portraitPoseIndex;
            _weaponHighlighted = weaponHighlighted;
            _objectiveMarkerOffsets = objectiveMarkerOffsets;
            QueueRedraw();
        }

        public override void _Draw()
        {
            DrawLowerLeftInstrument();
            DrawBattleline();
            if (_speaker != RetailHudSpeaker.None)
            {
                DrawMessageFrame();
            }
            DrawCrosshair();
        }

        private void DrawLowerLeftInstrument()
        {
            DrawTextureRect(
                radioView,
                new Rect2(17f, Size.Y - 112f, 128f, 128f),
                false,
                RetailColor(0x6fffffff));
            DrawTextureRect(
                weaponFill,
                new Rect2(9f, Size.Y - 141f, 128f, 128f),
                false,
                _weaponHighlighted
                    ? RetailColor(0x7f7fff3f)
                    : RetailColor(0x3f000000));

            Vector2 radarCenter = new(69f, Size.Y - 64f);
            foreach (Vector2 markerOffset in _objectiveMarkerOffsets)
            {
                DrawTextureRect(
                    scannerBlobSmall,
                    new Rect2(radarCenter + markerOffset - new Vector2(8f, 8f), new Vector2(16f, 16f)),
                    false,
                    new Color(1f, 0.92f, 0.08f, 1f));
            }

            Vector2 northCenter = new(65f, Size.Y - 64f);
            Vector2 northPosition = northCenter + new Vector2(
                Mathf.Sin(_facingYaw) * 45f,
                -Mathf.Cos(_facingYaw) * 45f);
            DrawCenteredRotated(
                radioNorth,
                northPosition,
                new Vector2(32f, 32f),
                _facingYaw,
                RetailColor(0xff5f7fff));
        }

        private void DrawBattleline()
        {
            DrawTextureRect(
                circleDarkener,
                new Rect2(Size.X - 121f, Size.Y - 112f, 128f, 128f),
                false,
                new Color(1f, 1f, 1f, 0.76f));

            if (_speaker == RetailHudSpeaker.None)
            {
                return;
            }

            Texture2D portrait = (_speaker == RetailHudSpeaker.Technician
                ? technicianPortraits
                : tatianaPortraits)[_portraitPoseIndex];
            DrawTextureRect(
                portrait,
                new Rect2(Size.X - 121f, Size.Y - 112f, 96f, 96f),
                false,
                Colors.White);
            DrawTextureRect(
                circleMask,
                new Rect2(Size.X - 137f, Size.Y - 128f, 128f, 128f),
                false);
        }

        private void DrawMessageFrame()
        {
            const float frameWidth = 252f;
            const float pieceHeight = 120f;
            const float innerWidth = 60f;
            Color innerTint = RetailColor(0x90000000);
            float centerX = (Size.X * 0.5f) + 22f;
            float centerY = Size.Y - 41f;
            float leftCenter = centerX - (frameWidth * 0.5f);
            float rightCenter = centerX + (frameWidth * 0.5f);
            float top = centerY - (pieceHeight * 0.5f);

            DrawTextureRect(
                objectiveLeft,
                new Rect2(leftCenter - (pieceHeight * 0.5f), top, pieceHeight, pieceHeight),
                false);
            DrawTextureRect(
                objectiveInnerLeft,
                new Rect2(leftCenter - innerWidth, top, innerWidth, pieceHeight),
                false,
                innerTint);
            DrawTextureRect(
                objectiveRight,
                new Rect2(rightCenter - (pieceHeight * 0.5f), top, pieceHeight, pieceHeight),
                false);
            DrawTextureRect(
                objectiveInnerRight,
                new Rect2(rightCenter, top, innerWidth, pieceHeight),
                false,
                innerTint);

            float remaining = frameWidth;
            float x = leftCenter;
            while (remaining > 0f)
            {
                float width = Mathf.Min(innerWidth, remaining);
                DrawTextureRectRegion(
                    objectiveInnerCentre,
                    new Rect2(x, top, width, pieceHeight),
                    new Rect2(0f, 0f, 64f * (width / innerWidth), 128f),
                    innerTint);
                x += width;
                remaining -= width;
            }
        }

        private static bool PortraitSetIsReady(Texture2D[] portraits) =>
            portraits.Length == 4 &&
            portraits.All(portrait => portrait.GetSize() == new Vector2I(128, 128));

        private static int SelectPortraitPose(int simulationTick)
        {
            // Retail changes among oo/ee/mm/aa at a 50 ms cadence with weighted
            // random selection. Core advances at 30 Hz, so every third tick is
            // one stable 100 ms presentation interval rather than frame-rate state.
            uint value = unchecked((uint)((simulationTick / 3) + 123456));
            value = unchecked((value * 214013u) + 2531011u);
            int sample = (int)((value >> 16) & 0xff) * 100 / 256;
            return sample switch
            {
                < 8 => 0,
                < 20 => 1,
                < 60 => 2,
                _ => 3,
            };
        }

        private void DrawCrosshair()
        {
            Vector2 center = Size * 0.5f;
            DrawTextureRect(
                crosshairSecondary,
                new Rect2(center - new Vector2(64f, 64f), new Vector2(128f, 128f)),
                false);
            DrawTextureRect(
                crosshairPrimary,
                new Rect2(center - new Vector2(32f, 32f), new Vector2(64f, 64f)),
                false);
            DrawTextureRect(
                crosshairDot,
                new Rect2(center - new Vector2(32f, 32f), new Vector2(64f, 64f)),
                false);
        }

        private void DrawCenteredRotated(
            Texture2D texture,
            Vector2 center,
            Vector2 size,
            float rotation,
            Color modulate)
        {
            DrawSetTransform(center, rotation, Vector2.One);
            DrawTextureRect(texture, new Rect2(-size * 0.5f, size), false, modulate);
            DrawSetTransform(Vector2.Zero, 0f, Vector2.One);
        }
    }

    private sealed partial class RetailHudGlowLayer(
        Texture2D radarOutline,
        Texture2D weaponOutline,
        Texture2D battlelineOutline,
        Texture2D messageNoise,
        Texture2D barLine,
        Texture2D objectiveMarker) : Control
    {
        private Vector2[] _objectiveMarkerOffsets = [];
        private float _facingYaw;
        private bool _messageActive;
        private bool _weaponHighlighted;

        public bool IsReady =>
            radarOutline.GetSize() == new Vector2I(128, 128) &&
            weaponOutline.GetSize() == new Vector2I(128, 128) &&
            battlelineOutline.GetSize() == new Vector2I(128, 128) &&
            messageNoise.GetSize() == new Vector2I(128, 128) &&
            barLine.GetSize() == new Vector2I(16, 64) &&
            objectiveMarker.GetSize() == new Vector2I(16, 16);

        public override void _Ready()
        {
            Material = new CanvasItemMaterial
            {
                BlendMode = CanvasItemMaterial.BlendModeEnum.Add,
            };
        }

        public void SetState(
            WorldSnapshot snapshot,
            bool messageActive,
            Vector2[] objectiveMarkerOffsets)
        {
            float facingYaw = snapshot.FacingYawMicroRad / 1_000_000f;
            bool weaponHighlighted = snapshot.Level100CurrentWeaponHighlighted;
            if (Mathf.IsEqualApprox(_facingYaw, facingYaw) &&
                _messageActive == messageActive &&
                _weaponHighlighted == weaponHighlighted &&
                _objectiveMarkerOffsets.SequenceEqual(objectiveMarkerOffsets))
            {
                return;
            }

            _facingYaw = facingYaw;
            _messageActive = messageActive;
            _weaponHighlighted = weaponHighlighted;
            _objectiveMarkerOffsets = objectiveMarkerOffsets;
            QueueRedraw();
        }

        public override void _Draw()
        {
            DrawLowerLeftOutlines();
            DrawThreatCircle();
            DrawBattlelineOutline();
        }

        private void DrawLowerLeftOutlines()
        {
            DrawTextureRect(
                radarOutline,
                new Rect2(17f, Size.Y - 112f, 128f, 128f),
                false,
                RetailColor(0xff6f8faf));
            DrawTextureRect(
                weaponOutline,
                new Rect2(9f, Size.Y - 141f, 128f, 128f),
                false,
                _weaponHighlighted
                    ? RetailColor(0xff7fff3f)
                    : RetailColor(0xff7f7f7f));
        }

        private void DrawThreatCircle()
        {
            Vector2 center = Size * 0.5f;
            DrawArc(
                center,
                98f,
                0f,
                Mathf.Tau,
                128,
                new Color(0.76f, 0.82f, 1f, 0.20f),
                2f,
                true);

            Vector2 northPosition = center + new Vector2(
                Mathf.Sin(_facingYaw) * 110f,
                -Mathf.Cos(_facingYaw) * 110f);
            DrawCenteredRotated(
                barLine,
                northPosition,
                new Vector2(16f, 64f),
                _facingYaw,
                new Color(0.90f, 0.82f, 0.24f, 0.86f));

            foreach (Vector2 markerOffset in _objectiveMarkerOffsets)
            {
                if (markerOffset.IsZeroApprox())
                {
                    continue;
                }
                Vector2 markerCenter = center + (markerOffset.Normalized() * 111.5f);
                DrawTextureRect(
                    objectiveMarker,
                    new Rect2(markerCenter - new Vector2(8f, 8f), new Vector2(16f, 16f)),
                    false,
                    new Color(1f, 0.91f, 0.08f, 1f));
            }
        }

        private void DrawBattlelineOutline()
        {
            if (_messageActive)
            {
                DrawTextureRect(
                    messageNoise,
                    new Rect2(Size.X - 137f, Size.Y - 128f, 128f, 128f),
                    false,
                    new Color(0.48f, 0.66f, 1f, 0.16f));
            }
            DrawTextureRect(
                battlelineOutline,
                new Rect2(Size.X - 121f, Size.Y - 112f, 128f, 128f),
                false,
                RetailColor(0xff6f8faf));
        }

        private void DrawCenteredRotated(
            Texture2D texture,
            Vector2 center,
            Vector2 size,
            float rotation,
            Color modulate)
        {
            DrawSetTransform(center, rotation, Vector2.One);
            DrawTextureRect(texture, new Rect2(-size * 0.5f, size), false, modulate);
            DrawSetTransform(Vector2.Zero, 0f, Vector2.One);
        }
    }

    private sealed partial class RetailHudTextLayer : Control
    {
        private const int FirstGlyph = 32;
        private const int GlyphColumns = 16;
        private const int GlyphCellSize = 16;
        private const int MessageCharactersPerLine = 26;
        private const int MaximumLines = 5;
        private readonly Texture2D _fontAtlas;
        private readonly int[] _glyphWidths;
        private string[] _lines = [];

        public RetailHudTextLayer(Texture2D fontAtlas)
        {
            _fontAtlas = fontAtlas;
            _glyphWidths = MeasureGlyphWidths(fontAtlas.GetImage());
        }

        public bool IsReady =>
            _fontAtlas.GetSize() == new Vector2I(256, 256) &&
            _glyphWidths.Length == 96;

        public void Clear()
        {
            SetLines([]);
        }

        public void SetMessage(string text)
        {
            SetLines(WrapMessage(text));
        }

        public override void _Draw()
        {
            if (_lines.Length == 0)
            {
                return;
            }

            float left = (Size.X * 0.5f) - 116f;
            float top = Size.Y - 68f;
            for (int lineIndex = 0; lineIndex < _lines.Length; lineIndex++)
            {
                string line = _lines[lineIndex];
                float x = left;
                for (int index = 0; index < line.Length; index++)
                {
                    x += DrawGlyph(line[index], x, top + (lineIndex * 15f));
                }
            }
        }

        private int DrawGlyph(char character, float x, float y)
        {
            int code = character;
            if (code is < FirstGlyph or >= FirstGlyph + 96)
            {
                code = '?';
            }
            int glyph = code - FirstGlyph;
            int glyphWidth = _glyphWidths[glyph];
            var source = new Rect2(
                (glyph % GlyphColumns) * GlyphCellSize,
                (glyph / GlyphColumns) * GlyphCellSize,
                glyphWidth,
                GlyphCellSize);
            DrawTextureRectRegion(
                _fontAtlas,
                new Rect2(x, y, glyphWidth, GlyphCellSize),
                source,
                Colors.Black);
            DrawTextureRectRegion(
                _fontAtlas,
                new Rect2(x - 1f, y - 1f, glyphWidth, GlyphCellSize),
                source,
                Colors.White);
            return glyphWidth + 1;
        }

        private static int[] MeasureGlyphWidths(Image image)
        {
            var widths = new int[96];
            widths[0] = 8;
            for (int glyph = 1; glyph < widths.Length; glyph++)
            {
                int cellX = (glyph % GlyphColumns) * GlyphCellSize;
                int cellY = (glyph / GlyphColumns) * GlyphCellSize;
                int rightmost = cellX;
                for (int x = cellX + 14; x >= cellX; x--)
                {
                    bool occupied = false;
                    for (int y = cellY; y < cellY + 15; y++)
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

        private void SetLines(string[] lines)
        {
            if (_lines.SequenceEqual(lines, StringComparer.Ordinal))
            {
                return;
            }
            _lines = lines;
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
                    if (lines.Count == MaximumLines)
                    {
                        break;
                    }
                    current.Clear();
                }
                if (current.Length > 0)
                {
                    current.Append(' ');
                }
                current.Append(word);
            }
            if (lines.Count < MaximumLines && current.Length > 0)
            {
                lines.Add(current.ToString());
            }
            return lines.ToArray();
        }
    }
}
