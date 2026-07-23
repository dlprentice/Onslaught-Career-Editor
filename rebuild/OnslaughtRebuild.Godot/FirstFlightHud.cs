// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

public sealed partial class FirstFlightHud : CanvasLayer
{
    private const float RadarRadius = 46f;
    private const float ScannerNorthRadius = 45f;
    private const float CompassThreatRadius = 111.5f;
    private const float CompassDamageRadius = 96f;
    private const float CompassGaugeNeedleRadius = 110f;
    private const float CompassObjectiveRadius = 98f;

    private HudAssets _assets = null!;
    private Level100HudAssetCatalog _catalog = null!;
    private readonly Level100HudPresentationState _presentation = new();
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
    public int Level100DeliveredMessageCount => _textLayer.DeliveredMessageCount;
    public int Level100DeliveredHelpCount => _textLayer.DeliveredHelpCount;
    public int Level100Energy => _glowLayer.Energy;
    public int Level100Shield => _glowLayer.Shield;
    public int Level100Health => _glowLayer.Health;
    public bool Level100BattleLineInfluenceAvailable =>
        _baseLayer.BattleLineInfluenceAvailable;
    public bool Level100MessagePlaybackAvailable { get; private set; }
    public bool Level100MessagePlaying { get; private set; }
    public double Level100MessagePlaybackPositionSeconds { get; private set; }
    public double Level100MessagePlaybackLengthSeconds { get; private set; }

    public void Initialize(Level100HudAssetCatalog catalog)
    {
        ArgumentNullException.ThrowIfNull(catalog);
        _catalog = catalog;
        _assets = LoadAssets();
        _baseLayer = new RetailHudBaseLayer(_assets);
        AddFullScreenControl(_baseLayer);

        _glowLayer = new RetailHudGlowLayer(_assets);
        AddFullScreenControl(_glowLayer);

        _textLayer = new RetailHudTextLayer(_assets.Font13Ps, _assets.Font22, catalog);
        AddFullScreenControl(_textLayer);
    }

    public void ConsumeMissionEvents(IReadOnlyList<Level100MissionEvent> events) =>
        _presentation.Consume(events);

    public void UpdateFromSnapshot(
        WorldSnapshot snapshot,
        Level100MessagePlaybackState playback)
    {
        Level100HudSnapshot hud = _presentation.Project(snapshot, playback);
        Level100HudMessageDeliverySnapshot? activeDelivery =
            hud.ActiveMessage?.Delivery;
        Level100HudMessageDefinition? message =
            activeDelivery is null ? null : _catalog.GetRequired(activeDelivery.MessageId);
        Level100MessagePlaybackSnapshot activePlayback =
            playback.ActiveMessageId.HasValue &&
            message is not null &&
            playback.ActiveMessageId.Value == message.MessageId
                ? new Level100MessagePlaybackSnapshot(
                    IsAvailable: true,
                    playback.ActiveMessageId,
                    playback.Playing,
                    playback.PositionSeconds,
                    playback.LengthSeconds,
                    PortraitPoseIndex(playback),
                    MessagePageIndex: null)
                : Level100MessagePlaybackSnapshot.Unavailable;
        if (activePlayback.PortraitPoseIndex is < 0 or > 3 ||
            activePlayback.MessagePageIndex is < 0)
        {
            throw new InvalidDataException("Level 100 audio presentation state is out of range.");
        }
        Level100MessagePlaybackAvailable = activePlayback.IsAvailable;
        Level100MessagePlaying = activePlayback.Playing;
        Level100MessagePlaybackPositionSeconds = activePlayback.PositionSeconds;
        Level100MessagePlaybackLengthSeconds = activePlayback.LengthSeconds;

        _baseLayer.SetState(
            snapshot,
            hud,
            message,
            activeDelivery?.Speaker,
            activePlayback.PortraitPoseIndex);
        _glowLayer.SetState(snapshot, hud, message is not null);
        _textLayer.SetState(hud, message, activePlayback);
    }

    private static int PortraitPoseIndex(Level100MessagePlaybackState playback)
    {
        if (!playback.Playing || !playback.ActiveMessageId.HasValue)
        {
            return 3;
        }

        int frame = Math.Max(0, (int)Math.Floor(playback.PositionSeconds / 0.05d));
        uint value = unchecked(
            ((uint)playback.ActiveMessageId.Value * 0x9E3779B9u) ^
            ((uint)frame * 0x85EBCA6Bu));
        value ^= value >> 16;
        int weighted = (int)(value % 100u);
        return weighted switch
        {
            < 8 => 0,
            < 20 => 1,
            < 60 => 2,
            _ => 3,
        };
    }

    public void MarkInputActivity()
    {
        // The released HUD has no persistent controls legend to reveal or fade.
    }

    private static HudAssets LoadAssets()
    {
        Texture2D circleMask = LoadHudTexture("circle-mask", 128, 128);
        Texture2D[][] sourcePortraits =
        [
            LoadPortraitSet("tatiana"),
            LoadPortraitSet("technician"),
            LoadPortraitSet("kramer"),
        ];

        return new HudAssets
        {
            BarLine = LoadHudTexture(
                "bar-line",
                16,
                64,
                CuratedAyaTextureLoader.Compression.Dxt1),
            BattleLineMarker = LoadHudTexture("battleline-marker", 16, 16),
            BattleLineOutline = LoadHudTexture(
                "battleline-outline",
                128,
                128,
                CuratedAyaTextureLoader.Compression.Dxt1),
            CircleDarkener = LoadHudTexture("circle-darkener", 128, 128),
            CircleMask = circleMask,
            CompassObjectiveMarker = LoadHudTexture("compass-objective-marker", 16, 16),
            CrosshairDot = LoadHudTexture("crosshair-dot", 64, 64),
            CrosshairEnemy = LoadHudTexture("crosshair-enemy", 64, 64),
            CrosshairFriend = LoadHudTexture("crosshair-friend", 64, 64),
            CrosshairOutline = LoadHudTexture("crosshair-outline", 64, 64),
            CrosshairPredictor = LoadHudTexture("crosshair-predictor", 64, 64),
            CrosshairPrimary = LoadHudTexture("crosshair-primary", 64, 64),
            CrosshairSecondary = LoadHudTexture("crosshair-secondary", 128, 128),
            DamageFlash = LoadHudTexture(
                "damage-flash",
                128,
                32,
                CuratedAyaTextureLoader.Compression.Dxt1),
            Dial = LoadHudBytes("dial.raw", 8_192),
            Font13Ps = LoadHudTexture(
                "font-13ps",
                256,
                256,
                CuratedAyaTextureLoader.Compression.Rgba8),
            Font22 = LoadHudTexture(
                "font-22",
                512,
                512,
                CuratedAyaTextureLoader.Compression.Rgba8),
            GunsDarken = LoadHudTexture("guns-darken", 128, 128),
            GunsFront = LoadHudTexture(
                "guns-front",
                128,
                128,
                CuratedAyaTextureLoader.Compression.Dxt1),
            GunsOutline = LoadHudTexture(
                "guns-outline",
                128,
                128,
                CuratedAyaTextureLoader.Compression.Dxt1),
            GunsSide = LoadHudTexture(
                "guns-side",
                128,
                128,
                CuratedAyaTextureLoader.Compression.Dxt1),
            GunsTop = LoadHudTexture(
                "guns-top",
                128,
                128,
                CuratedAyaTextureLoader.Compression.Dxt1),
            MessageNoise = LoadHudTexture(
                "message-noise",
                128,
                128,
                CuratedAyaTextureLoader.Compression.Dxt1),
            ObjectiveInnerCentre = LoadHudTexture("objective-inner-centre", 64, 128),
            ObjectiveInnerLeft = LoadHudTexture("objective-inner-left", 64, 128),
            ObjectiveInnerRight = LoadHudTexture("objective-inner-right", 64, 128),
            ObjectiveLeft = LoadHudTexture("objective-left", 128, 128),
            ObjectiveRight = LoadHudTexture("objective-right", 128, 128),
            OffscreenArrow = LoadHudTexture("offscreen-arrow", 32, 32),
            RadarOutline = LoadHudTexture(
                "radar-outline",
                128,
                128,
                CuratedAyaTextureLoader.Compression.Dxt1),
            RadioNorth = LoadHudTexture("radio-north", 32, 32),
            RadioView = LoadHudTexture("radio-view", 128, 128),
            ScannerBlobs =
            [
                LoadHudTexture("scanner-blob-small", 16, 16),
                LoadHudTexture("scanner-blob-medium", 16, 16),
                LoadHudTexture("scanner-blob-large", 16, 16),
                LoadHudTexture("scanner-blob-repair-pad", 16, 16),
            ],
            ScreenMarker = LoadHudTexture(
                "screen-marker",
                64,
                64,
                CuratedAyaTextureLoader.Compression.Dxt1),
            TargetSighted = LoadHudTexture("target-sighted", 64, 64),
            ThreatFlash = LoadHudTexture(
                "threat-flash",
                32,
                32,
                CuratedAyaTextureLoader.Compression.Dxt1),
            WeaponFill = LoadHudTexture("weapon-fill", 128, 128),
            WeaponOutline = LoadHudTexture(
                "weapon-outline",
                128,
                128,
                CuratedAyaTextureLoader.Compression.Dxt1),
            WeaponIcons =
            [
                LoadHudTexture("weapon-plasma-cannon", 64, 64),
                LoadHudTexture("weapon-vulcan-cannon", 64, 64),
            ],
            Portraits = sourcePortraits
                .Select(set => ApplyReleasedPortraitMask(set, circleMask))
                .ToArray(),
        };
    }

    private static Texture2D[] LoadPortraitSet(string speaker) =>
    [
        LoadHudTexture($"{speaker}-portrait-oo", 128, 128),
        LoadHudTexture($"{speaker}-portrait-ee", 128, 128),
        LoadHudTexture($"{speaker}-portrait-mm", 128, 128),
        LoadHudTexture($"{speaker}-portrait", 128, 128),
    ];

    private static Texture2D[] ApplyReleasedPortraitMask(Texture2D[] source, Texture2D circleMask)
    {
        Image maskImage = circleMask.GetImage();
        MakeCpuReadable(maskImage);
        return source.Select(portrait => ApplyReleasedPortraitMask(portrait, maskImage)).ToArray();
    }

    private static Texture2D ApplyReleasedPortraitMask(Texture2D source, Image maskImage)
    {
        const int sourceSize = 128;
        const int portraitSize = 96;
        const int portraitInset = (sourceSize - portraitSize) / 2;
        Image sourceImage = source.GetImage();
        MakeCpuReadable(sourceImage);
        sourceImage.Resize(portraitSize, portraitSize, Image.Interpolation.Bilinear);
        Image masked = Image.CreateEmpty(sourceSize, sourceSize, false, Image.Format.Rgba8);
        for (int y = 0; y < sourceSize; y++)
        {
            for (int x = 0; x < sourceSize; x++)
            {
                Color sourcePixel = x is >= portraitInset and < portraitInset + portraitSize &&
                    y is >= portraitInset and < portraitInset + portraitSize
                        ? sourceImage.GetPixel(x - portraitInset, y - portraitInset)
                        : Colors.Transparent;
                Color maskPixel = maskImage.GetPixel(x, y);
                sourcePixel.A *= 1f - maskPixel.A;
                masked.SetPixel(x, y, sourcePixel);
            }
        }
        return ImageTexture.CreateFromImage(masked);
    }

    private static void MakeCpuReadable(Image image)
    {
        if (image.IsCompressed() && image.Decompress() != Error.Ok)
        {
            throw new InvalidDataException("Released HUD texture could not be decompressed for portrait masking.");
        }

        if (image.GetFormat() != Image.Format.Rgba8)
        {
            image.Convert(Image.Format.Rgba8);
        }
    }

    private static Texture2D LoadHudTexture(
        string name,
        int width,
        int height,
        CuratedAyaTextureLoader.Compression compression = CuratedAyaTextureLoader.Compression.Dxt2) =>
        CuratedAyaTextureLoader.Load(
            $"res://Assets/Hud/{name}.texture.aya",
            width,
            height,
            compression);

    private static byte[] LoadHudBytes(string name, int expectedLength)
    {
        string path = $"res://Assets/Hud/{name}";
        byte[] source = Godot.FileAccess.GetFileAsBytes(path);
        if (source.Length != expectedLength)
        {
            throw new InvalidDataException(
                $"Released HUD asset has the wrong length: {path} ({source.Length}, expected {expectedLength})");
        }
        return source;
    }

    private static Color RetailColor(uint argb) => new(
        ((argb >> 16) & 0xff) / 255f,
        ((argb >> 8) & 0xff) / 255f,
        (argb & 0xff) / 255f,
        ((argb >> 24) & 0xff) / 255f);

    private static Color ContactColor(Level100HudContactSnapshot contact)
    {
        if (contact.IsObjective)
        {
            return new Color(1f, 0.92f, 0.08f, 1f);
        }

        return contact.Allegiance switch
        {
            Level100HudAllegiance.Friendly => new Color(0.25f, 0.48f, 1f, 1f),
            Level100HudAllegiance.Enemy => new Color(1f, 0.10f, 0.10f, 1f),
            _ => new Color(0.75f, 0.75f, 0.75f, 1f),
        };
    }

    private static Vector2 ProjectRadarOffset(WorldSnapshot snapshot, SimVector2 position)
    {
        float deltaX = (position.X - snapshot.PlayerPosition.X) / 1_000f;
        float deltaZ = (position.Z - snapshot.PlayerPosition.Z) / 1_000f;
        float yaw = snapshot.FacingYawMicroRad / 1_000_000f;
        float sin = Mathf.Sin(yaw);
        float cos = Mathf.Cos(yaw);
        var offset = new Vector2(
            (deltaX * cos) + (deltaZ * sin),
            (deltaX * sin) - (deltaZ * cos));
        float distance = offset.Length();
        if (distance > RadarRadius)
        {
            offset *= RadarRadius / distance;
        }
        return offset;
    }

    private static float RelativeYaw(WorldSnapshot snapshot, SimVector2 position)
    {
        float dx = position.X - snapshot.PlayerPosition.X;
        float dz = position.Z - snapshot.PlayerPosition.Z;
        float desiredYaw = Mathf.Atan2(-dx, dz);
        return NormalizeAngle((snapshot.FacingYawMicroRad / 1_000_000f) - desiredYaw);
    }

    private static float NormalizeAngle(float angle)
    {
        while (angle > Mathf.Pi)
        {
            angle -= Mathf.Tau;
        }
        while (angle <= -Mathf.Pi)
        {
            angle += Mathf.Tau;
        }
        return angle;
    }

    private void AddFullScreenControl(Control control)
    {
        control.AnchorRight = 1f;
        control.AnchorBottom = 1f;
        control.MouseFilter = Control.MouseFilterEnum.Ignore;
        AddChild(control);
    }

    private sealed class HudAssets
    {
        public required Texture2D BarLine { get; init; }
        public required Texture2D BattleLineMarker { get; init; }
        public required Texture2D BattleLineOutline { get; init; }
        public required Texture2D CircleDarkener { get; init; }
        public required Texture2D CircleMask { get; init; }
        public required Texture2D CompassObjectiveMarker { get; init; }
        public required Texture2D CrosshairDot { get; init; }
        public required Texture2D CrosshairEnemy { get; init; }
        public required Texture2D CrosshairFriend { get; init; }
        public required Texture2D CrosshairOutline { get; init; }
        public required Texture2D CrosshairPredictor { get; init; }
        public required Texture2D CrosshairPrimary { get; init; }
        public required Texture2D CrosshairSecondary { get; init; }
        public required Texture2D DamageFlash { get; init; }
        public required byte[] Dial { get; init; }
        public required Texture2D Font13Ps { get; init; }
        public required Texture2D Font22 { get; init; }
        public required Texture2D GunsDarken { get; init; }
        public required Texture2D GunsFront { get; init; }
        public required Texture2D GunsOutline { get; init; }
        public required Texture2D GunsSide { get; init; }
        public required Texture2D GunsTop { get; init; }
        public required Texture2D MessageNoise { get; init; }
        public required Texture2D ObjectiveInnerCentre { get; init; }
        public required Texture2D ObjectiveInnerLeft { get; init; }
        public required Texture2D ObjectiveInnerRight { get; init; }
        public required Texture2D ObjectiveLeft { get; init; }
        public required Texture2D ObjectiveRight { get; init; }
        public required Texture2D OffscreenArrow { get; init; }
        public required Texture2D RadarOutline { get; init; }
        public required Texture2D RadioNorth { get; init; }
        public required Texture2D RadioView { get; init; }
        public required Texture2D[] ScannerBlobs { get; init; }
        public required Texture2D ScreenMarker { get; init; }
        public required Texture2D TargetSighted { get; init; }
        public required Texture2D ThreatFlash { get; init; }
        public required Texture2D WeaponFill { get; init; }
        public required Texture2D[] WeaponIcons { get; init; }
        public required Texture2D WeaponOutline { get; init; }
        public required Texture2D[][] Portraits { get; init; }
    }

    private sealed partial class RetailHudBaseLayer(HudAssets assets) : Control
    {
        private WorldSnapshot? _snapshot;
        private Level100HudSnapshot? _hud;
        private Level100HudMessageDefinition? _message;
        private Level100HudSpeaker? _speaker;
        private int? _portraitPoseIndex;

        public bool IsReady =>
            assets.CircleDarkener.GetSize() == new Vector2I(128, 128) &&
            assets.CircleMask.GetSize() == new Vector2I(128, 128) &&
            assets.RadioView.GetSize() == new Vector2I(128, 128) &&
            assets.WeaponFill.GetSize() == new Vector2I(128, 128) &&
            assets.RadioNorth.GetSize() == new Vector2I(32, 32) &&
            assets.ScannerBlobs.Length == 4 &&
            assets.ScannerBlobs.All(texture => texture.GetSize() == new Vector2I(16, 16)) &&
            assets.Portraits.Length == 3 &&
            assets.Portraits.All(PortraitSetIsReady);

        public int ObjectiveMarkerCount =>
            _hud?.Objectives.Count(
                objective => objective.State == Level100HudObjectiveState.Active &&
                    objective.Position.HasValue) ?? 0;

        public bool BattleLineInfluenceAvailable =>
            _hud?.BattleLine is Level100HudBattleLineSnapshot battleLine &&
            battleLine.HasInfluenceValues &&
            battleLine.InfluencePermille.Count == Level100HudInfluenceMap.Nodes.Count;

        public void SetState(
            WorldSnapshot snapshot,
            Level100HudSnapshot hud,
            Level100HudMessageDefinition? message,
            Level100HudSpeaker? speaker,
            int? portraitPoseIndex)
        {
            _snapshot = snapshot;
            _hud = hud;
            _message = message;
            _speaker = speaker;
            _portraitPoseIndex = portraitPoseIndex;
            QueueRedraw();
        }

        public override void _Draw()
        {
            if (_snapshot is not WorldSnapshot snapshot ||
                _hud is not Level100HudSnapshot hud)
            {
                return;
            }

            DrawLowerLeftInstrument(snapshot, hud);
            DrawWeaponSelection(hud);
            DrawBattleLine();
            if (_message is not null)
            {
                DrawMessageFrame();
            }
            DrawWorldMarkers(snapshot, hud);
            DrawCrosshair(snapshot, hud);
        }

        private void DrawLowerLeftInstrument(
            WorldSnapshot snapshot,
            Level100HudSnapshot hud)
        {
            Rect2 radarRect = new(17f, Size.Y - 112f, 128f, 128f);
            Rect2 weaponRect = new(9f, Size.Y - 141f, 128f, 128f);
            DrawTextureRect(assets.RadioView, radarRect, false, RetailColor(0x6fffffff));
            DrawTextureRect(assets.WeaponFill, weaponRect, false, RetailColor(0x3f000000));

            DrawWeaponResource(snapshot, hud, weaponRect);
            DrawWeaponIcon(hud.Weapon, weaponRect);

            Vector2 radarCenter = new(69f, Size.Y - 64f);
            foreach (Level100HudContactSnapshot contact in hud.Contacts
                         .Where(contact => contact.OnScanner))
            {
                Vector2 offset = ProjectRadarOffset(snapshot, contact.Position);
                int textureIndex = Math.Clamp((int)contact.Size, 0, assets.ScannerBlobs.Length - 1);
                DrawTextureRect(
                    assets.ScannerBlobs[textureIndex],
                    new Rect2(radarCenter + offset - new Vector2(8f, 8f), new Vector2(16f, 16f)),
                    false,
                    ContactColor(contact));
            }

            float yaw = snapshot.FacingYawMicroRad / 1_000_000f;
            Vector2 northCenter = new(65f, Size.Y - 64f);
            Vector2 northPosition = northCenter + new Vector2(
                Mathf.Sin(yaw) * ScannerNorthRadius,
                -Mathf.Cos(yaw) * ScannerNorthRadius);
            DrawCenteredRotated(
                assets.RadioNorth,
                northPosition,
                new Vector2(32f, 32f),
                yaw,
                RetailColor(0xff5f7fff));
        }

        private void DrawWeaponResource(
            WorldSnapshot snapshot,
            Level100HudSnapshot hud,
            Rect2 rect)
        {
            Level100HudWeaponSnapshot weapon = hud.Weapon;
            int? resource = weapon.SelectedWeapon switch
            {
                Level100HudWeapon.PulseCannon => weapon.PulseHeatPermille is int heat
                    ? 1_000 - heat
                    : null,
                _ => null,
            };
            if (resource is not int resourcePermille)
            {
                return;
            }

            float fraction = Math.Clamp(resourcePermille / 1_000f, 0f, 1f);
            float height = rect.Size.Y * fraction;
            var destination = new Rect2(
                rect.Position.X,
                rect.End.Y - height,
                rect.Size.X,
                height);
            var source = new Rect2(0f, 128f - (128f * fraction), 128f, 128f * fraction);
            Color tint = weapon.PulseCannonOverheated == true && (snapshot.Tick / 3) % 2 == 0
                ? new Color(1f, 0.15f, 0.05f, 0.82f)
                : new Color(0.28f, 0.92f, 0.38f, 0.64f);
            DrawTextureRectRegion(assets.WeaponFill, destination, source, tint);
        }

        private void DrawWeaponIcon(Level100HudWeaponSnapshot weapon, Rect2 panel)
        {
            Texture2D? icon = weapon.SelectedWeapon switch
            {
                Level100HudWeapon.PulseCannon when weapon.PulseCannonEnabled => assets.WeaponIcons[0],
                Level100HudWeapon.VulcanCannon when weapon.VulcanCannonEnabled => assets.WeaponIcons[1],
                _ => null,
            };
            if (icon is null)
            {
                return;
            }

            DrawTextureRect(
                icon,
                new Rect2(panel.Position + new Vector2(32f, 30f), new Vector2(64f, 64f)),
                false,
                Colors.White);
        }

        private void DrawWeaponSelection(Level100HudSnapshot hud)
        {
            Level100HudWeaponSnapshot weapon = hud.Weapon;
            if (weapon.SelectionPanelVisible != true ||
                weapon.SelectionSlot is not Level100HudWeaponSelectionSlot selectionSlot ||
                selectionSlot == Level100HudWeaponSelectionSlot.None)
            {
                return;
            }

            Rect2 rect = new(Size.X - 137f, Size.Y - 240f, 128f, 128f);
            DrawTextureRect(assets.GunsDarken, rect, false, RetailColor(0x78000000));
            Texture2D? selectedSlotTexture = selectionSlot switch
            {
                Level100HudWeaponSelectionSlot.Side => assets.GunsSide,
                Level100HudWeaponSelectionSlot.Front => assets.GunsFront,
                Level100HudWeaponSelectionSlot.Top => assets.GunsTop,
                _ => null,
            };
            if (selectedSlotTexture is not null)
            {
                DrawTextureRect(
                    selectedSlotTexture,
                    rect,
                    false,
                    new Color(0.50f, 0.75f, 0.88f, 0.80f));
            }
        }

        private void DrawBattleLine()
        {
            Rect2 rect = BattleLineRect();
            DrawTextureRect(assets.CircleDarkener, rect, false, new Color(1f, 1f, 1f, 0.76f));

            if (_message is not null &&
                _speaker is Level100HudSpeaker speaker &&
                _portraitPoseIndex is int pose)
            {
                int speakerIndex = speaker switch
                {
                    Level100HudSpeaker.Tatiana => 0,
                    Level100HudSpeaker.Technician => 1,
                    Level100HudSpeaker.Kramer => 2,
                    _ => -1,
                };
                if (speakerIndex >= 0)
                {
                    DrawTextureRect(assets.Portraits[speakerIndex][pose], rect, false, Colors.White);
                }
                return;
            }
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
                assets.ObjectiveLeft,
                new Rect2(leftCenter - (pieceHeight * 0.5f), top, pieceHeight, pieceHeight),
                false);
            DrawTextureRect(
                assets.ObjectiveInnerLeft,
                new Rect2(leftCenter - innerWidth, top, innerWidth, pieceHeight),
                false,
                innerTint);
            DrawTextureRect(
                assets.ObjectiveRight,
                new Rect2(rightCenter - (pieceHeight * 0.5f), top, pieceHeight, pieceHeight),
                false);
            DrawTextureRect(
                assets.ObjectiveInnerRight,
                new Rect2(rightCenter, top, innerWidth, pieceHeight),
                false,
                innerTint);

            float remaining = frameWidth;
            float x = leftCenter;
            while (remaining > 0f)
            {
                float width = Mathf.Min(innerWidth, remaining);
                DrawTextureRectRegion(
                    assets.ObjectiveInnerCentre,
                    new Rect2(x, top, width, pieceHeight),
                    new Rect2(0f, 0f, 64f * (width / innerWidth), 128f),
                    innerTint);
                x += width;
                remaining -= width;
            }
        }

        private void DrawWorldMarkers(
            WorldSnapshot snapshot,
            Level100HudSnapshot hud)
        {
            foreach (Level100HudObjectiveSnapshot objective in hud.Objectives
                         .Where(objective => objective.State == Level100HudObjectiveState.Active &&
                             objective.Position.HasValue))
            {
                DrawWorldMarker(
                    snapshot,
                    objective.Position!.Value,
                    new Color(1f, 0.92f, 0.08f, 1f));
            }
        }

        private void DrawWorldMarker(WorldSnapshot snapshot, SimVector2 position, Color tint)
        {
            float relativeYaw = RelativeYaw(snapshot, position);
            const float horizontalLimit = 1.05f;
            Vector2 center = Size * 0.5f;
            if (Math.Abs(relativeYaw) <= horizontalLimit)
            {
                float x = center.X + ((relativeYaw / horizontalLimit) * (Size.X * 0.42f));
                DrawTextureRect(
                    assets.ScreenMarker,
                    new Rect2(new Vector2(x, center.Y) - new Vector2(32f, 32f), new Vector2(64f, 64f)),
                    false,
                    tint);
                return;
            }

            float side = Math.Sign(relativeYaw);
            Vector2 arrowCenter = new(
                side < 0f ? 28f : Size.X - 28f,
                center.Y);
            DrawCenteredRotated(
                assets.OffscreenArrow,
                arrowCenter,
                new Vector2(32f, 32f),
                side < 0f ? -Mathf.Pi * 0.5f : Mathf.Pi * 0.5f,
                tint);
        }

        private void DrawCrosshair(
            WorldSnapshot snapshot,
            Level100HudSnapshot hud)
        {
            Vector2 center = Size * 0.5f;
            DrawTextureRect(
                assets.CrosshairSecondary,
                new Rect2(center - new Vector2(64f, 64f), new Vector2(128f, 128f)),
                false);
            DrawTextureRect(
                assets.CrosshairPrimary,
                new Rect2(center - new Vector2(32f, 32f), new Vector2(64f, 64f)),
                false);
            DrawTextureRect(
                assets.CrosshairDot,
                new Rect2(center - new Vector2(32f, 32f), new Vector2(64f, 64f)),
                false);

            if (hud.Target is not Level100HudTargetSnapshot target)
            {
                DrawTextureRect(
                    assets.CrosshairOutline,
                    new Rect2(center - new Vector2(32f, 32f), new Vector2(64f, 64f)),
                    false);
                return;
            }

            Level100HudContactSnapshot? contact = hud.Contacts.FirstOrDefault(
                candidate => candidate.Id == target.ContactId);
            Texture2D classification = contact?.Allegiance == Level100HudAllegiance.Friendly
                ? assets.CrosshairFriend
                : assets.CrosshairEnemy;
            Color classificationTint = contact is null ? Colors.White : ContactColor(contact);
            DrawTextureRect(
                classification,
                new Rect2(center - new Vector2(32f, 32f), new Vector2(64f, 64f)),
                false,
                classificationTint);
            DrawTextureRect(
                assets.TargetSighted,
                new Rect2(center - new Vector2(32f, 32f), new Vector2(64f, 64f)),
                false,
                new Color(1f, 1f, 1f, Math.Clamp(target.LockPermille / 1_000f, 0f, 1f)));

            float predictedYaw = RelativeYaw(snapshot, target.PredictedPosition);
            float predictorX = center.X + ((predictedYaw / 1.05f) * (Size.X * 0.42f));
            predictorX = Math.Clamp(predictorX, 32f, Size.X - 32f);
            DrawTextureRect(
                assets.CrosshairPredictor,
                new Rect2(new Vector2(predictorX, center.Y) - new Vector2(32f, 32f), new Vector2(64f, 64f)),
                false,
                classificationTint);

        }

        private Rect2 BattleLineRect() => new(Size.X - 137f, Size.Y - 128f, 128f, 128f);

        private static bool PortraitSetIsReady(Texture2D[] portraits) =>
            portraits.Length == 4 &&
            portraits.All(portrait => portrait.GetSize() == new Vector2I(128, 128));

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

    private sealed partial class RetailHudGlowLayer(HudAssets assets) : Control
    {
        private WorldSnapshot? _snapshot;
        private Level100HudSnapshot? _hud;
        private bool _messageActive;

        public bool IsReady =>
            assets.RadarOutline.GetSize() == new Vector2I(128, 128) &&
            assets.WeaponOutline.GetSize() == new Vector2I(128, 128) &&
            assets.BattleLineOutline.GetSize() == new Vector2I(128, 128) &&
            assets.MessageNoise.GetSize() == new Vector2I(128, 128) &&
            assets.Dial.Length == 8_192 &&
            assets.BarLine.GetSize() == new Vector2I(16, 64) &&
            assets.CompassObjectiveMarker.GetSize() == new Vector2I(16, 16) &&
            assets.ThreatFlash.GetSize() == new Vector2I(32, 32) &&
            assets.DamageFlash.GetSize() == new Vector2I(128, 32);

        public int Energy { get; private set; }
        public int Shield { get; private set; }
        public int Health { get; private set; }

        public override void _Ready()
        {
            Material = new CanvasItemMaterial
            {
                BlendMode = CanvasItemMaterial.BlendModeEnum.Add,
            };
        }

        public void SetState(
            WorldSnapshot snapshot,
            Level100HudSnapshot hud,
            bool messageActive)
        {
            _snapshot = snapshot;
            _hud = hud;
            _messageActive = messageActive;
            Energy = snapshot.Energy;
            Shield = snapshot.Shield;
            Health = snapshot.Hull;
            QueueRedraw();
        }

        public override void _Draw()
        {
            if (_snapshot is not WorldSnapshot snapshot ||
                _hud is not Level100HudSnapshot hud)
            {
                return;
            }

            DrawInstrumentOutlines(snapshot, hud);
            DrawDynamicCompass(snapshot, hud);
            DrawBattleLineOutline(snapshot, hud);
        }

        private void DrawInstrumentOutlines(
            WorldSnapshot snapshot,
            Level100HudSnapshot hud)
        {
            float radarHighlight = HighlightAlpha(snapshot, hud, Level100HudPart.Radar);
            float weaponHighlight = HighlightAlpha(
                snapshot,
                hud,
                Level100HudPart.CurrentWeapon);
            DrawTextureRect(
                assets.RadarOutline,
                new Rect2(17f, Size.Y - 112f, 128f, 128f),
                false,
                new Color(0.44f + radarHighlight, 0.56f + (radarHighlight * 0.35f), 0.69f, 1f));
            DrawTextureRect(
                assets.WeaponOutline,
                new Rect2(9f, Size.Y - 141f, 128f, 128f),
                false,
                weaponHighlight > 0f
                    ? new Color(0.50f, 1f, 0.25f, 1f)
                    : RetailColor(0xff7f7f7f));

            Rect2 gunsRect = new(Size.X - 137f, Size.Y - 240f, 128f, 128f);
            Level100HudWeaponSnapshot weapon = hud.Weapon;
            if (weapon.SelectionPanelVisible == true &&
                weapon.SelectionSlot is Level100HudWeaponSelectionSlot selectionSlot &&
                selectionSlot != Level100HudWeaponSelectionSlot.None)
            {
                DrawTextureRect(assets.GunsOutline, gunsRect, false, RetailColor(0xff6f8faf));
            }
        }

        private void DrawDynamicCompass(
            WorldSnapshot snapshot,
            Level100HudSnapshot hud)
        {
            Vector2 center = Size * 0.5f;
            float compassHighlight = HighlightAlpha(snapshot, hud, Level100HudPart.Compass);
            Color baseColor = new(0.42f + compassHighlight, 0.58f, 0.90f, 0.25f + (compassHighlight * 0.4f));

            // CDXCompass builds the outer band from a 512x32 texture at 31%
            // thickness and the inner band from a 256x8 texture at 27%.
            // Normalize its largest generated radius to 100 HUD units. The
            // shipped Dial.raw north frame rotates with heading on that band;
            // threat, damage, gauge-needle, and objective sprites have their
            // separate released 111.5/96/110/98-unit radii.
            const float outerTextureAspect = (32f * Mathf.Pi) / 512f;
            const float outerGeneratedInner = (1f - outerTextureAspect) * 0.31f;
            const float outerGeneratedOuter = (1f + outerTextureAspect) * 0.31f;
            const float innerTextureAspect = (8f * Mathf.Pi) / 256f;
            const float innerGeneratedInner = (1f - innerTextureAspect) * 0.27f;
            const float innerGeneratedOuter = (1f + innerTextureAspect) * 0.27f;
            const float generatedToHud = 100f / outerGeneratedOuter;
            const float outerInnerRadius = outerGeneratedInner * generatedToHud;
            const float outerOuterRadius = outerGeneratedOuter * generatedToHud;
            const float innerInnerRadius = innerGeneratedInner * generatedToHud;
            const float innerOuterRadius = innerGeneratedOuter * generatedToHud;
            float outerRadius = (outerInnerRadius + outerOuterRadius) * 0.5f;
            float outerWidth = outerOuterRadius - outerInnerRadius;
            float innerRadius = (innerInnerRadius + innerOuterRadius) * 0.5f;
            float innerWidth = innerOuterRadius - innerInnerRadius;

            DrawSegmentedRing(center, outerRadius, 50, outerWidth, 0f, 1f, baseColor);
            DrawSegmentedRing(center, innerRadius, 40, innerWidth, 0f, 1f, new Color(0.32f, 0.54f, 0.96f, 0.20f));

            float health = Math.Clamp(
                Health / (float)SimulationConstants.MaximumHull,
                0f,
                1f);
            float energy = Math.Clamp(
                Energy / (float)SimulationConstants.MaximumEnergy,
                0f,
                1f);
            Color healthColor = new Color(1f - health, health, 0.08f, 0.88f);
            Color energyColor = new Color(0.18f, 0.62f, 1f, 0.88f);
            float healthHighlight = HighlightAlpha(snapshot, hud, Level100HudPart.Health);
            float energyHighlight = HighlightAlpha(snapshot, hud, Level100HudPart.Energy);
            healthColor.A = Math.Clamp(healthColor.A + healthHighlight, 0f, 1f);
            energyColor.A = Math.Clamp(energyColor.A + energyHighlight, 0f, 1f);
            DrawSegmentedRing(
                center,
                outerRadius,
                50,
                outerWidth,
                (150f - (health * 90f)) / 360f,
                health * (90f / 360f),
                healthColor);
            DrawSegmentedRing(center, innerRadius, 40, innerWidth, 225f / 360f, energy * (135f / 360f), energyColor);
            DrawDialNorthOverlay(snapshot, center, outerInnerRadius, outerOuterRadius, baseColor);

            DrawThreats(hud, center);
            DrawDamageFlashes(hud, center);
            DrawGaugeNeedlesAndObjectives(snapshot, hud, center, health, energy);
        }

        private void DrawThreats(Level100HudSnapshot hud, Vector2 center)
        {
            foreach (Level100HudThreatSnapshot threat in hud.Threats)
            {
                float angle = threat.RelativeYawMicroRad / 1_000_000f;
                float alpha = Math.Clamp(threat.TicksRemaining / 600f, 0f, 1f);
                Vector2 position = center +
                    new Vector2(Mathf.Sin(angle), -Mathf.Cos(angle)) * CompassThreatRadius;
                DrawCenteredRotated(
                    assets.ThreatFlash,
                    position,
                    new Vector2(32f, 32f),
                    angle,
                    new Color(1f, 1f, 1f, alpha));
            }
        }

        private void DrawDamageFlashes(Level100HudSnapshot hud, Vector2 center)
        {
            foreach (Level100HudDamageFlashSnapshot flash in hud.DamageFlashes)
            {
                float angle = flash.RelativeYawMicroRad / 1_000_000f;
                float alpha = Math.Clamp(flash.TicksRemaining / 60f, 0f, 1f);
                Vector2 position = center +
                    new Vector2(Mathf.Sin(angle), -Mathf.Cos(angle)) * CompassDamageRadius;
                DrawCenteredRotated(
                    assets.DamageFlash,
                    position,
                    new Vector2(128f, 32f),
                    angle,
                    new Color(1f, 1f, 1f, alpha));
            }
        }

        private void DrawGaugeNeedlesAndObjectives(
            WorldSnapshot snapshot,
            Level100HudSnapshot hud,
            Vector2 center,
            float health,
            float energy)
        {
            DrawGaugeNeedle(center, Mathf.DegToRad(150f - (health * 90f)));
            DrawGaugeNeedle(center, Mathf.DegToRad(150f));
            DrawGaugeNeedle(center, Mathf.DegToRad(225f + (energy * 135f)));
            DrawGaugeNeedle(center, Mathf.DegToRad(225f));

            foreach (Level100HudObjectiveSnapshot objective in hud.Objectives
                         .Where(objective => objective.State == Level100HudObjectiveState.Active &&
                             objective.Position.HasValue))
            {
                float relativeYaw = RelativeYaw(snapshot, objective.Position!.Value);
                Vector2 position = center + new Vector2(
                    Mathf.Sin(relativeYaw) * CompassObjectiveRadius,
                    -Mathf.Cos(relativeYaw) * CompassObjectiveRadius);
                DrawTextureRect(
                    assets.CompassObjectiveMarker,
                    new Rect2(position - new Vector2(8f, 8f), new Vector2(16f, 16f)),
                    false,
                    new Color(1f, 0.91f, 0.08f, 1f));
            }
        }

        private void DrawGaugeNeedle(Vector2 center, float angle)
        {
            Vector2 position = center +
                new Vector2(Mathf.Sin(angle), -Mathf.Cos(angle)) * CompassGaugeNeedleRadius;
            DrawCenteredRotated(
                assets.BarLine,
                position,
                new Vector2(16f, 64f),
                angle,
                RetailColor(0xff1f1f1f));
        }

        private void DrawDialNorthOverlay(
            WorldSnapshot snapshot,
            Vector2 center,
            float innerRadius,
            float outerRadius,
            Color color)
        {
            const int frameSize = 16;
            const int dialTextureWidth = 512;
            const int dialTextureHeight = 32;
            const int frameTop = 15;
            float heading = snapshot.FacingYawMicroRad / 1_000_000f;
            float angularStep = Mathf.Tau / dialTextureWidth;
            float radialWidth = (outerRadius - innerRadius) / dialTextureHeight;
            for (int y = 0; y < frameSize; y++)
            {
                float sourceV = frameTop + y + 0.5f;
                float radius = Mathf.Lerp(outerRadius, innerRadius, sourceV / dialTextureHeight);
                for (int x = 0; x < frameSize; x++)
                {
                    byte paletteIndex = assets.Dial[(y * frameSize) + x];
                    if (paletteIndex == 0)
                    {
                        continue;
                    }

                    float firstAngle = heading + ((x - (frameSize * 0.5f)) * angularStep);
                    float secondAngle = firstAngle + angularStep;
                    Color tint = color;
                    tint.A *= paletteIndex / 15f;
                    DrawLine(
                        center + new Vector2(Mathf.Sin(firstAngle), -Mathf.Cos(firstAngle)) * radius,
                        center + new Vector2(Mathf.Sin(secondAngle), -Mathf.Cos(secondAngle)) * radius,
                        tint,
                        radialWidth,
                        true);
                }
            }
        }

        private void DrawBattleLineOutline(
            WorldSnapshot snapshot,
            Level100HudSnapshot hud)
        {
            Rect2 rect = new(Size.X - 137f, Size.Y - 128f, 128f, 128f);
            if (_messageActive)
            {
                DrawTextureRect(
                    assets.MessageNoise,
                    rect,
                    false,
                    new Color(0.48f, 0.66f, 1f, 0.16f));
            }
            float highlight = HighlightAlpha(snapshot, hud, Level100HudPart.BattleLine);
            DrawTextureRect(
                assets.BattleLineOutline,
                rect,
                false,
                new Color(0.44f + highlight, 0.56f + (highlight * 0.35f), 0.69f, 1f));
        }

        private static float HighlightAlpha(
            WorldSnapshot snapshot,
            Level100HudSnapshot hud,
            Level100HudPart part)
        {
            if (!hud.EmphasizedParts.Contains(part))
            {
                return 0f;
            }
            return 0.22f + (0.18f * (Mathf.Sin(snapshot.Tick * 0.45f) + 1f));
        }

        private void DrawSegmentedRing(
            Vector2 center,
            float radius,
            int segmentCount,
            float width,
            float startTurn,
            float turnLength,
            Color color)
        {
            int segmentStart = Math.Clamp((int)Math.Floor(startTurn * segmentCount), 0, segmentCount);
            int segmentEnd = Math.Clamp(
                (int)Math.Ceiling((startTurn + turnLength) * segmentCount),
                segmentStart,
                segmentCount);
            for (int segment = segmentStart; segment < segmentEnd; segment++)
            {
                float first = (segment / (float)segmentCount) * Mathf.Tau;
                float second = ((segment + 1) / (float)segmentCount) * Mathf.Tau;
                Vector2 firstPoint = center + new Vector2(Mathf.Sin(first), -Mathf.Cos(first)) * radius;
                Vector2 secondPoint = center + new Vector2(Mathf.Sin(second), -Mathf.Cos(second)) * radius;
                DrawLine(firstPoint, secondPoint, color, width, true);
            }
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
        private const int SmallGlyphCellSize = 16;
        private const int LargeGlyphCellSize = 32;
        private const int MaximumMessageLines = 5;
        private const float MessageLineHeight = 15f;
        private const float MessageTextWidth = 232f;
        private const float MessageTextHeight = 76f;

        private readonly Texture2D _fontAtlas;
        private readonly int[] _glyphWidths;
        private readonly Texture2D _largeFontAtlas;
        private readonly int[] _largeGlyphWidths;
        private readonly Level100HudAssetCatalog _catalog;
        private string[][] _messagePages = [];
        private Level100HudHelpDefinition[] _activeHelp = [];
        private Level100HudWeaponSnapshot _weapon = Level100HudWeaponSnapshot.Unavailable;
        private int _messagePageIndex;

        public RetailHudTextLayer(
            Texture2D fontAtlas,
            Texture2D largeFontAtlas,
            Level100HudAssetCatalog catalog)
        {
            _fontAtlas = fontAtlas;
            _glyphWidths = MeasureGlyphWidths(fontAtlas.GetImage(), SmallGlyphCellSize);
            _largeFontAtlas = largeFontAtlas;
            _largeGlyphWidths = MeasureGlyphWidths(largeFontAtlas.GetImage(), LargeGlyphCellSize);
            _catalog = catalog;
        }

        public bool IsReady =>
            _fontAtlas.GetSize() == new Vector2I(256, 256) &&
            _glyphWidths.Length == 96 &&
            _largeFontAtlas.GetSize() == new Vector2I(512, 512) &&
            _largeGlyphWidths.Length == 96;

        public int DeliveredMessageCount { get; private set; }
        public int DeliveredHelpCount { get; private set; }

        public void SetState(
            Level100HudSnapshot hud,
            Level100HudMessageDefinition? message,
            Level100MessagePlaybackSnapshot playback)
        {
            _messagePages = message is null
                ? []
                : Paginate(message.Text, MessageTextWidth, MaximumMessageLines);
            _messagePageIndex =
                playback.IsAvailable &&
                playback.LengthSeconds > 0d &&
                _messagePages.Length > 1
                    ? Math.Min(
                        _messagePages.Length - 1,
                        (int)Math.Floor(
                            (playback.PositionSeconds / playback.LengthSeconds) *
                            _messagePages.Length))
                    : 0;
            if (_messagePages.Length > 0 && _messagePageIndex >= _messagePages.Length)
            {
                throw new InvalidDataException(
                    "Level 100 native message page is outside the released text pagination.");
            }
            _activeHelp = hud.ActiveHelp
                .Select(_catalog.GetRequired)
                .ToArray();
            DeliveredMessageCount = hud.DeliveredMessages.Count;
            DeliveredHelpCount = hud.DeliveredHelp.Count;
            _weapon = hud.Weapon;
            QueueRedraw();
        }

        public override void _Draw()
        {
            DrawMessagePage();
            DrawHelpPrompts();
            DrawWeaponAmmo();
        }

        private void DrawMessagePage()
        {
            if (_messagePages.Length == 0)
            {
                return;
            }

            string[] lines = _messagePages[_messagePageIndex];
            var textRect = new Rect2(
                (Size.X * 0.5f) - 94f,
                Size.Y - 93f,
                MessageTextWidth,
                MessageTextHeight);
            for (int lineIndex = 0; lineIndex < lines.Length; lineIndex++)
            {
                DrawTextLine(
                    lines[lineIndex],
                    textRect.Position.X,
                    textRect.Position.Y + (lineIndex * MessageLineHeight),
                    textRect);
            }
        }

        private void DrawHelpPrompts()
        {
            float y = 28f;
            foreach (Level100HudHelpDefinition prompt in _activeHelp)
            {
                string[] lines = WrapIntoLines(prompt.Text, 360f).Take(2).ToArray();
                foreach (string line in lines)
                {
                    float width = MeasureText(line);
                    DrawTextLine(line, (Size.X - width) * 0.5f, y);
                    y += MessageLineHeight;
                }
                y += 4f;
            }
        }

        private void DrawWeaponAmmo()
        {
            if (_weapon.SelectedWeapon != Level100HudWeapon.VulcanCannon ||
                !_weapon.VulcanCannonEnabled ||
                _weapon.VulcanAmmo is not int ammo)
            {
                return;
            }

            string text = ammo.ToString(System.Globalization.CultureInfo.InvariantCulture);
            var bounds = new Rect2(9f, Size.Y - 141f, 128f, LargeGlyphCellSize);
            float left = bounds.End.X - MeasureText(text, _largeGlyphWidths) - 8f;
            DrawTextLine(
                text,
                left,
                bounds.Position.Y,
                _largeFontAtlas,
                _largeGlyphWidths,
                LargeGlyphCellSize,
                drawShadow: false,
                clip: bounds);
        }

        private void DrawTextLine(string line, float left, float top, Rect2? clip = null)
        {
            DrawTextLine(
                line,
                left,
                top,
                _fontAtlas,
                _glyphWidths,
                SmallGlyphCellSize,
                drawShadow: true,
                clip: clip);
        }

        private void DrawTextLine(
            string line,
            float left,
            float top,
            Texture2D atlas,
            int[] glyphWidths,
            int cellSize,
            bool drawShadow,
            Rect2? clip)
        {
            float x = left;
            foreach (char character in line)
            {
                x += DrawGlyph(
                    character,
                    x,
                    top,
                    atlas,
                    glyphWidths,
                    cellSize,
                    drawShadow,
                    clip);
            }
        }

        private void DrawTextureRectRegionClipped(
            Texture2D atlas,
            Rect2 destination,
            Rect2 source,
            Color modulate,
            Rect2? clip)
        {
            if (clip is not Rect2 clipRect)
            {
                DrawTextureRectRegion(atlas, destination, source, modulate);
                return;
            }

            float left = Math.Max(destination.Position.X, clipRect.Position.X);
            float top = Math.Max(destination.Position.Y, clipRect.Position.Y);
            float right = Math.Min(destination.End.X, clipRect.End.X);
            float bottom = Math.Min(destination.End.Y, clipRect.End.Y);
            if (right <= left || bottom <= top)
            {
                return;
            }

            var clippedDestination = new Rect2(left, top, right - left, bottom - top);
            var clippedSource = new Rect2(
                source.Position + clippedDestination.Position - destination.Position,
                clippedDestination.Size);
            DrawTextureRectRegion(atlas, clippedDestination, clippedSource, modulate);
        }

        private int DrawGlyph(
            char character,
            float x,
            float y,
            Texture2D atlas,
            int[] glyphWidths,
            int cellSize,
            bool drawShadow,
            Rect2? clip)
        {
            int code = NormalizeGlyph(character);
            int glyph = code - FirstGlyph;
            int glyphWidth = glyphWidths[glyph];
            var source = new Rect2(
                (glyph % GlyphColumns) * cellSize,
                (glyph / GlyphColumns) * cellSize,
                glyphWidth,
                cellSize);
            if (drawShadow)
            {
                DrawTextureRectRegionClipped(
                    atlas,
                    new Rect2(x, y, glyphWidth, cellSize),
                    source,
                    Colors.Black,
                    clip);
            }
            DrawTextureRectRegionClipped(
                atlas,
                new Rect2(
                    drawShadow ? x - 1f : x,
                    drawShadow ? y - 1f : y,
                    glyphWidth,
                    cellSize),
                source,
                Colors.White,
                clip);
            return glyphWidth + 1;
        }

        private float MeasureText(string text)
        {
            return MeasureText(text, _glyphWidths);
        }

        private static float MeasureText(string text, int[] glyphWidths)
        {
            float width = 0f;
            foreach (char character in text)
            {
                width += glyphWidths[NormalizeGlyph(character) - FirstGlyph] + 1;
            }
            return width;
        }

        private static int NormalizeGlyph(char character) =>
            character is >= (char)FirstGlyph and < (char)(FirstGlyph + 96)
                ? character
                : '?';

        private static int[] MeasureGlyphWidths(Image image, int cellSize)
        {
            var widths = new int[96];
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

        private string[][] Paginate(string text, float width, int linesPerPage)
        {
            string[] lines = WrapIntoLines(text, width);
            return lines
                .Select((line, index) => (line, index))
                .GroupBy(item => item.index / linesPerPage)
                .Select(group => group.Select(item => item.line).ToArray())
                .ToArray();
        }

        private string[] WrapIntoLines(string text, float maximumWidth)
        {
            var lines = new List<string>();
            string normalized = text.Replace("\r\n", "\n", StringComparison.Ordinal)
                .Replace('\r', '\n');
            foreach (string paragraph in normalized.Split('\n'))
            {
                string current = string.Empty;
                int position = 0;
                while (position < paragraph.Length)
                {
                    int separatorStart = position;
                    while (position < paragraph.Length && char.IsWhiteSpace(paragraph[position]))
                    {
                        position++;
                    }
                    string separator = paragraph[separatorStart..position];

                    int wordStart = position;
                    while (position < paragraph.Length && !char.IsWhiteSpace(paragraph[position]))
                    {
                        position++;
                    }
                    if (wordStart == position)
                    {
                        break;
                    }

                    string word = paragraph[wordStart..position];
                    string candidate = current.Length == 0
                        ? word
                        : current + separator + word;
                    if (MeasureText(candidate) <= maximumWidth)
                    {
                        current = candidate;
                        continue;
                    }

                    if (current.Length > 0)
                    {
                        lines.Add(current);
                        current = string.Empty;
                    }

                    string remaining = word;
                    while (remaining.Length > 0 && MeasureText(remaining) > maximumWidth)
                    {
                        int split = 1;
                        while (split < remaining.Length &&
                               MeasureText(remaining[..(split + 1)]) <= maximumWidth)
                        {
                            split++;
                        }
                        lines.Add(remaining[..split]);
                        remaining = remaining[split..];
                    }
                    current = remaining;
                }

                if (current.Length > 0)
                {
                    lines.Add(current);
                }
                else if (paragraph.Length == 0)
                {
                    lines.Add(string.Empty);
                }
            }
            return lines.ToArray();
        }

    }
}
