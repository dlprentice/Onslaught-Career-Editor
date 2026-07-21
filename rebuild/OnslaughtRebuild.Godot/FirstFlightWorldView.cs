// SPDX-License-Identifier: GPL-3.0-or-later

using System.Buffers.Binary;
using Godot;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

public sealed partial class FirstFlightWorldView : Node3D
{
    private const float UnitsToMeters = 0.001f;
    private const float RetailWalkerCenterOfGravityHeight =
        Level100Terrain.WalkerCenterOfGravityMillimeters * UnitsToMeters;
    private const float RetailVerticalFovDegrees = 58.7155f;
    private const float RetailOpeningPanSeconds = 6f;
    private const float RetailOpeningCameraHandoffSeconds = 5.95f;
    private const float RetailAquilaAnimationHz = 20f;
    private const float RetailJetWalkToFlySeconds = 25f / RetailAquilaAnimationHz;
    // Steam enters the cockpit sequence with current=1/24 (virtual frame 27),
    // while the external jet begins at current=0 (virtual frame 25).
    private const float RetailCockpitWalkToFlySeconds = 23f / RetailAquilaAnimationHz;

    private readonly Dictionary<int, Node3D> _projectiles = [];
    private readonly Dictionary<int, Node3D> _level100Targets = [];
    private Node3D _playerRoot = null!;
    private Node3D _playerBodyPivot = null!;
    private RetailAquilaWalkerAsset _walkerAsset = null!;
    private RetailAquilaWalkerAsset _jetAsset = null!;
    private RetailAquilaWalkerAsset _cockpitAsset = null!;
    private MeshInstance3D _level100Sky = null!;
    private Level100HeightFieldAsset _level100Terrain = null!;
    private Level100StaticWorldAsset _level100StaticWorld = null!;
    private Texture2D _retailChrome3Texture = null!;
    private Texture2D _warehouseOverlayTexture = null!;
    private Camera3D _camera = null!;
    private StandardMaterial3D _pulseBoltSparkMaterial = null!;
    private StandardMaterial3D _pulseBoltTrailMaterial = null!;
    private StandardMaterial3D _pulseBoltHaloMaterial = null!;
    private StandardMaterial3D _pulseBoltEnergyTrailMaterial = null!;
    private Texture2D _pulseImpactAnimatedTexture = null!;
    private Texture2D _pulseImpactShockwaveTexture = null!;
    private Texture2D _effectFlashMediumTexture = null!;
    private Texture2D _targetTankExplosionAnimatedTexture = null!;
    private Texture2D _targetTankExplosionFireballTexture = null!;
    private AudioStream _pulseCannonFireSound = null!;
    private AudioStream _pulseImpactSmallSound = null!;
    private AudioStream _targetTankExplosionMediumSound = null!;
    private AudioStream _aquilaTakeoffSound = null!;
    private AudioStreamPlayer3D _aquilaInFlightSound = null!;
    private int _lastTargetEffectTick = -1;
    private float _walkerToJetVisualElapsed = float.PositiveInfinity;
    private VehicleTransition _previousTransition;
    private VehicleMode _previousMode = VehicleMode.Walker;

    public int TargetVisualCount => _level100Targets.Values.Count(target => target.Visible);

    public int ProjectileVisualCount => _projectiles.Count;

    public bool PlayerVisualPresent => IsInstanceValid(_playerRoot);

    public bool RetailAquilaMeshesPresent =>
        IsInstanceValid(_walkerAsset.Root) &&
        IsInstanceValid(_jetAsset.Root) &&
        _walkerAsset.SurfaceCount > 0 &&
        _jetAsset.SurfaceCount > 0;

    public int RetailAquilaSurfaceCount =>
        _walkerAsset.SurfaceCount +
        _jetAsset.SurfaceCount;

    public int RetailAquilaPartCount => _walkerAsset.PartCount;

    public int RetailAquilaAnimatedPartCount => _walkerAsset.AnimatedPartCount;

    public float RetailAquilaStandingClearance => _walkerAsset.StandingClearance;

    public int RetailCockpitSurfaceCount => _cockpitAsset.SurfaceCount;

    public int RetailLevel100StaticObjectCount => _level100StaticWorld.Objects.Count;

    public int RetailLevel100StaticObjectSurfaceCount => _level100StaticWorld.SurfaceCount;

    public int RetailLevel100PineCount => _level100StaticWorld.PineInstanceCount;

    public bool RetailLevel100WaterPresent =>
        IsInstanceValid(_level100StaticWorld.Water.Root);

    public int RetailLevel100WaterGridVertexCount =>
        _level100StaticWorld.Water.GridVertexCount;

    public int RetailLevel100WaterGridTriangleCount =>
        _level100StaticWorld.Water.GridTriangleCount;

    public int RetailLevel100ShorelineTriangleCount =>
        _level100StaticWorld.Water.ShorelineTriangleCount;

    public int RetailLevel100TargetSurfaceCount =>
        _level100Targets.Values
            .SelectMany(target => target.GetChildren().OfType<MeshInstance3D>())
            .Sum(target => target.Mesh?.GetSurfaceCount() ?? 0);

    public int RetailLevel100TerrainVertexCount => _level100Terrain.VertexCount;

    public int RetailLevel100TerrainTriangleCount => _level100Terrain.TriangleCount;

    public int RetailLevel100SkySurfaceCount => _level100Sky.Mesh?.GetSurfaceCount() ?? 0;

    public float Level100PlayerStartRelativeHeight => _level100Terrain.SampleRelativeHeight(0f, 0f);

    public bool ShowHud { get; private set; }

    public bool OpeningPanActive => !ShowHud;

    public void Initialize(WorldSnapshot snapshot)
    {
        Name = "WorldView";
        BuildLevel100Terrain();
        BuildEnvironment();
        BuildLevel100StaticWorld();
        LoadSharedRetailMaterialTextures();
        BuildLevel100Targets();
        BuildPlayer();
        BuildPulseCannonPresentation();
        BuildCamera();
        Render(snapshot, snapshot, 0f, 0f);
    }

    public void Render(
        WorldSnapshot previous,
        WorldSnapshot current,
        float interpolationAlpha,
        float frameDelta)
    {
        Vector3 previousPosition = ToPlayerWorld(previous);
        Vector3 currentPosition = ToPlayerWorld(current);
        bool resetJump = previousPosition.DistanceSquaredTo(currentPosition) > 100f;
        Vector3 playerPosition = resetJump
            ? currentPosition
            : previousPosition.Lerp(currentPosition, interpolationAlpha);
        _playerRoot.Position = playerPosition;

        float previousYaw = previous.FacingYawMicroRad / 1_000_000f;
        float currentYaw = current.FacingYawMicroRad / 1_000_000f;
        float playerYaw = Mathf.LerpAngle(previousYaw, currentYaw, interpolationAlpha);
        float previousPitch = previous.FacingPitchMicroRad / 1_000_000f;
        float currentPitch = current.FacingPitchMicroRad / 1_000_000f;
        float playerPitch = Mathf.Lerp(previousPitch, currentPitch, interpolationAlpha);
        _playerRoot.Rotation = new Vector3(
            0f,
            playerYaw,
            0f);

        UpdateWalkerPose(current);
        UpdateWalkerToJetPresentation(current, frameDelta);
        float openingElapsedTicks = GetOpeningElapsedTicks(previous, current, interpolationAlpha);
        float openingElapsedSeconds = openingElapsedTicks / SimulationConstants.TicksPerSecond;
        ShowHud = openingElapsedSeconds >= RetailOpeningCameraHandoffSeconds;
        UpdatePlayerShape(current, ShowHud);
        UpdateLevel100Targets(current);
        UpdateProjectiles(previous, current);
        UpdateCamera(playerPosition, playerYaw, playerPitch, openingElapsedSeconds, ShowHud);
        _level100StaticWorld.Water.Update(_camera.GlobalPosition, frameDelta);
    }

    private void BuildEnvironment()
    {
        var environment = new Godot.Environment
        {
            BackgroundMode = Godot.Environment.BGMode.Color,
            BackgroundColor = _level100Terrain.FogColor,
            TonemapMode = Godot.Environment.ToneMapper.Linear,
        };
        AddChild(new WorldEnvironment
        {
            Name = "WorldEnvironment",
            Environment = environment,
        });

        _level100Sky = Level100SkyAsset.Create(_level100Terrain.SkyCube);
        AddChild(_level100Sky);
    }

    private void BuildLevel100Terrain()
    {
        _level100Terrain = Level100HeightFieldAsset.Load();
        Material terrainMaterial = Level100TerrainAppearanceAsset.LoadMaterial(
            "res://Assets/Level100/Source/level100-mixer-set-10.mapt.bin",
            "res://Assets/Level100/Source/level100-mixer-map.mmap.bin",
            "res://Assets/Level100/Textures/terrain-detail-00.texture.aya",
            "res://Assets/Level100/Textures/terrain-cloud-shadow.texture.aya",
            _level100Terrain);
        AddChild(new MeshInstance3D
        {
            Name = "RetailLevel100HeightField",
            Mesh = _level100Terrain.Mesh,
            MaterialOverride = terrainMaterial,
        });
    }

    private void BuildLevel100StaticWorld()
    {
        _level100StaticWorld = Level100StaticWorldAsset.Load(_level100Terrain);
        AddChild(_level100StaticWorld.Root);
    }

    private void LoadSharedRetailMaterialTextures()
    {
        _retailChrome3Texture = CuratedAyaTextureLoader.Load(
            "res://Assets/Level100/StaticWorld/Textures/meshtex-chrome3.texture.aya",
            128,
            128);
        _warehouseOverlayTexture = CuratedAyaTextureLoader.Load(
            "res://Assets/Level100/Textures/material-overlay-a8trust5.texture.aya",
            128,
            128);
    }

    private void BuildLevel100Targets()
    {
        Texture2D tankTexture = CuratedAyaTextureLoader.Load(
            "res://Assets/Level100/Textures/target-tank.texture.aya",
            512,
            512);
        Material tankMaterial = CreateRetailMaterial(
            tankTexture,
            reflection: RetailLayer(_retailChrome3Texture, 0.199999988f));
        Mesh tankMesh = CuratedObjMeshLoader.Load(
            "res://Assets/Level100/level100-target-tank.obj",
            new Dictionary<string, Material>(StringComparer.Ordinal)
            {
                ["layers-00000000-ffffffff-00000001-ffffffff-ffffffff-ffffffff"] =
                    tankMaterial,
            });

        Texture2D warehouseM001Texture = CuratedAyaTextureLoader.Load(
            "res://Assets/Level100/Textures/target-warehouse-m001.texture.aya",
            512,
            512);
        Texture2D warehouseM002Texture = CuratedAyaTextureLoader.Load(
            "res://Assets/Level100/Textures/target-warehouse-m002.texture.aya",
            512,
            512);
        RetailTextureLayer warehouseOverlay = RetailLayer(
            _warehouseOverlayTexture,
            opacity: 1f,
            scale: new Vector2(20f, 20f));
        Material warehouseM001 = CreateRetailMaterial(warehouseM001Texture);
        Material warehouseM001Overlay = CreateRetailMaterial(
            warehouseM001Texture,
            overlay: warehouseOverlay);
        Material warehouseM002Overlay = CreateRetailMaterial(
            warehouseM002Texture,
            overlay: warehouseOverlay);
        Mesh warehouseMesh = CuratedObjMeshLoader.Load(
            "res://Assets/Level100/level100-target-warehouse.obj",
            new Dictionary<string, Material>(StringComparer.Ordinal)
            {
                ["layers-00000000-ffffffff-ffffffff-ffffffff-ffffffff-ffffffff"] =
                    warehouseM001,
                ["layers-00000001-ffffffff-ffffffff-ffffffff-00000005-ffffffff"] =
                    warehouseM001Overlay,
                ["layers-00000003-ffffffff-ffffffff-ffffffff-00000005-ffffffff"] =
                    warehouseM002Overlay,
            });

        AddLevel100Target(
            1,
            "RetailTargetTank1",
            SimulationConstants.Level100TargetTank1Position,
            -0.0523363f,
            tankMesh);
        AddLevel100Target(
            2,
            "RetailTargetTank2",
            SimulationConstants.Level100TargetTank2Position,
            -2.1535792f,
            tankMesh);
        AddLevel100Target(
            3,
            "RetailTargetTank3",
            SimulationConstants.Level100TargetTank3Position,
            2.4043305f,
            tankMesh);
        AddLevel100Target(
            4,
            "RetailTargetWarehouse",
            SimulationConstants.Level100TargetWarehousePosition,
            -1.9708606f,
            warehouseMesh);
    }

    private void AddLevel100Target(
        int id,
        string name,
        SimVector2 position,
        float retailYaw,
        Mesh mesh)
    {
        float relativeX = position.X * UnitsToMeters;
        float relativeY = position.Z * UnitsToMeters;
        var root = new Node3D
        {
            Name = name,
            Position = new Vector3(
                relativeX,
                _level100Terrain.SampleRelativeHeight(relativeX, relativeY),
                -relativeY),
            Rotation = new Vector3(0f, retailYaw, 0f),
        };
        root.AddChild(new MeshInstance3D
        {
            Name = $"{name}Geometry",
            Mesh = mesh,
            RotationDegrees = new Vector3(-90f, 0f, 0f),
        });
        AddChild(root);
        _level100Targets.Add(id, root);
    }

    private void UpdateLevel100Targets(WorldSnapshot snapshot)
    {
        foreach (TargetSnapshot target in snapshot.Targets)
        {
            if (!_level100Targets.TryGetValue(target.Id, out Node3D? visual))
            {
                throw new InvalidDataException($"Core exposed unknown Level 100 target {target.Id}.");
            }
            visual.Visible = target.IsActive;
        }
    }

    private void BuildPlayer()
    {
        _playerRoot = new Node3D { Name = "PlayerVisual" };
        AddChild(_playerRoot);
        _playerBodyPivot = new Node3D { Name = "BodyPivot" };
        _playerRoot.AddChild(_playerBodyPivot);

        Texture2D cockpitTexture = CuratedAyaTextureLoader.Load(
            "res://Assets/Aquila/Textures/cockpit.texture.aya",
            512,
            512);
        Texture2D textureA = CuratedAyaTextureLoader.Load(
            "res://Assets/Aquila/Textures/be-tex-a.texture.aya",
            512,
            512);
        Texture2D textureB = CuratedAyaTextureLoader.Load(
            "res://Assets/Aquila/Textures/be-tex-b.texture.aya",
            1024,
            1024);
        RetailTextureLayer chrome = RetailLayer(_retailChrome3Texture, 0.299999982f);
        _walkerAsset = RetailAquilaWalkerAsset.Load(
            "res://Assets/Aquila/Source/m_f_be1.msh.aya",
            new Dictionary<int, Texture2D>
            {
                [0] = cockpitTexture,
                [1] = textureB,
                [3] = textureA,
            },
            _level100Terrain);
        _jetAsset = RetailAquilaWalkerAsset.LoadJet(
            "res://Assets/Aquila/Source/m_f_be2.msh.aya",
            new Dictionary<int, Texture2D>
            {
                [0] = cockpitTexture,
                [1] = _retailChrome3Texture,
                [2] = textureB,
                [3] = _retailChrome3Texture,
                [4] = textureA,
            },
            _level100Terrain);
        _playerBodyPivot.AddChild(_walkerAsset.Root);
        _playerBodyPivot.AddChild(_jetAsset.Root);

        _aquilaTakeoffSound = LoadAudioStream(
            "res://Assets/Aquila/SoundEffects/engine-takeoff.wav");
        AudioStream inFlightStream = LoadAudioStream(
            "res://Assets/Aquila/SoundEffects/engine-inflight.wav");
        if (inFlightStream is not AudioStreamWav inFlightWave)
        {
            throw new InvalidDataException("The retained Aquila in-flight sound is not PCM WAV.");
        }
        inFlightWave.LoopMode = AudioStreamWav.LoopModeEnum.Forward;
        inFlightWave.LoopBegin = 0;
        inFlightWave.LoopEnd = inFlightWave.Data.Length / sizeof(short);
        _aquilaInFlightSound = new AudioStreamPlayer3D
        {
            Name = "RetailAquilaInFlightLoop",
            Stream = inFlightWave,
            Position = Vector3.Zero,
            MaxDistance = 80f,
            UnitSize = 8f,
        };
        _playerRoot.AddChild(_aquilaInFlightSound);
    }

    private Material CreateRetailMaterial(
        Texture2D texture,
        RetailTextureLayer? dot3 = null,
        RetailTextureLayer? reflection = null,
        RetailTextureLayer? overlay = null) =>
        RetailFixedFunctionMaterial.Create(
            [RetailLayer(texture), dot3, reflection, null, overlay, null],
            _level100Terrain);

    private static RetailTextureLayer RetailLayer(
        Texture2D texture,
        float opacity = 1f,
        Vector2? offset = null,
        Vector2? scale = null) =>
        new(texture, opacity, offset ?? Vector2.Zero, scale ?? Vector2.One);

    private void BuildCamera()
    {
        _camera = new Camera3D
        {
            Name = "RetailOpeningAndFirstPersonCamera",
            Fov = RetailVerticalFovDegrees,
            Near = 0.1f,
            Far = 700f,
            Current = true,
        };
        AddChild(_camera);

        Texture2D cockpitTexture = CuratedAyaTextureLoader.Load(
            "res://Assets/Aquila/Textures/cockpit.texture.aya",
            512,
            512);
        Texture2D gunLightTexture = CuratedAyaTextureLoader.Load(
            "res://Assets/Aquila/Textures/bluegun-light.texture.aya",
            64,
            64);
        var gunLightMaterial = new StandardMaterial3D
        {
            AlbedoTexture = gunLightTexture,
            ShadingMode = BaseMaterial3D.ShadingModeEnum.Unshaded,
            CullMode = BaseMaterial3D.CullModeEnum.Disabled,
            Transparency = BaseMaterial3D.TransparencyEnum.Alpha,
            BlendMode = BaseMaterial3D.BlendModeEnum.Add,
            EmissionEnabled = true,
            Emission = new Color(0.12f, 0.45f, 1f),
            EmissionTexture = gunLightTexture,
            EmissionEnergyMultiplier = 1.6f,
        };
        _cockpitAsset = RetailAquilaWalkerAsset.LoadCockpit(
            "res://Assets/Aquila/Source/m_cockpit2.msh.aya",
            new Dictionary<int, Texture2D>
            {
                [0] = gunLightTexture,
                [1] = cockpitTexture,
                [2] = _retailChrome3Texture,
            },
            new Dictionary<string, Material>(StringComparer.Ordinal)
            {
                ["layers-00000000-ffffffff-ffffffff-ffffffff-ffffffff-ffffffff"] =
                    gunLightMaterial,
            },
            _level100Terrain);
        _camera.AddChild(_cockpitAsset.Root);
    }

    private void UpdatePlayerShape(WorldSnapshot snapshot, bool attachedView)
    {
        // The released pan camera hides the HUD/cockpit and renders the
        // exterior Aquila. Its first-person handoff reverses that visibility.
        bool showingJet = snapshot.Transition == VehicleTransition.WalkerToJet ||
            snapshot.Mode == VehicleMode.Jet;
        _walkerAsset.Root.Visible = !attachedView && !showingJet;
        _jetAsset.Root.Visible = !attachedView && showingJet;
        _cockpitAsset.Root.Visible = attachedView;
        _playerBodyPivot.Position = Vector3.Zero;
    }

    private void UpdateWalkerToJetPresentation(WorldSnapshot snapshot, float frameDelta)
    {
        bool transitionStarted = snapshot.Transition == VehicleTransition.WalkerToJet &&
            _previousTransition != VehicleTransition.WalkerToJet;
        bool returnedToWalker = snapshot.Transition == VehicleTransition.None &&
            snapshot.Mode == VehicleMode.Walker &&
            (_previousTransition == VehicleTransition.WalkerToJet ||
             _previousMode == VehicleMode.Jet);

        if (transitionStarted)
        {
            _walkerToJetVisualElapsed = 0f;
            PlayAttachedSound("RetailAquilaTakeoff", _aquilaTakeoffSound);
            if (!_aquilaInFlightSound.Playing)
            {
                _aquilaInFlightSound.Play();
            }
        }
        else if (returnedToWalker)
        {
            _walkerToJetVisualElapsed = float.PositiveInfinity;
            _aquilaInFlightSound.Stop();
        }

        if (float.IsFinite(_walkerToJetVisualElapsed))
        {
            _walkerToJetVisualElapsed = Math.Min(
                _walkerToJetVisualElapsed + Math.Max(0f, frameDelta),
                RetailJetWalkToFlySeconds);
            int jetStep = Math.Min(
                Mathf.FloorToInt(_walkerToJetVisualElapsed * RetailAquilaAnimationHz),
                25);
            _jetAsset.SetVirtualFrame(25f + jetStep);

            if (_walkerToJetVisualElapsed < RetailCockpitWalkToFlySeconds)
            {
                int cockpitStep = Math.Min(
                    Mathf.FloorToInt(_walkerToJetVisualElapsed * RetailAquilaAnimationHz),
                    22);
                _cockpitAsset.SetVirtualFrame(27f + cockpitStep);
            }
            else
            {
                _cockpitAsset.SetVirtualFrame(0f);
            }

            if (_walkerToJetVisualElapsed >= RetailJetWalkToFlySeconds)
            {
                _jetAsset.SetVirtualFrame(0f);
                _walkerToJetVisualElapsed = float.PositiveInfinity;
            }
        }
        else if (snapshot.Mode == VehicleMode.Jet)
        {
            _jetAsset.SetVirtualFrame(0f);
            _cockpitAsset.SetVirtualFrame(0f);
        }
        else
        {
            _jetAsset.SetVirtualFrame(25f);
            _cockpitAsset.SetVirtualFrame(25f);
        }

        _previousTransition = snapshot.Transition;
        _previousMode = snapshot.Mode;
    }

    private void UpdateWalkerPose(WorldSnapshot snapshot)
    {
        if (snapshot.WalkerFeet.Count != 4)
        {
            throw new InvalidDataException("Core did not expose four Aquila foot contacts.");
        }

        float yaw = snapshot.FacingYawMicroRad / 1_000_000f;
        Basis worldToPlayer = new Basis(Vector3.Up, yaw).Inverse();
        var contacts = new Vector3[4];
        foreach (WalkerFootContactSnapshot foot in snapshot.WalkerFeet)
        {
            if (foot.Id < 0 || foot.Id >= contacts.Length)
            {
                throw new InvalidDataException($"Core exposed unknown Aquila foot {foot.Id}.");
            }
            var worldOffset = new Vector3(
                (foot.Position.X - snapshot.PlayerPosition.X) * UnitsToMeters,
                (foot.GroundElevationMillimeters + foot.LiftMillimeters -
                    snapshot.PlayerGroundElevationMillimeters) * UnitsToMeters,
                -(foot.Position.Z - snapshot.PlayerPosition.Z) * UnitsToMeters);
            contacts[foot.Id] = worldToPlayer * worldOffset;
        }
        _walkerAsset.SetGroundContactPose(contacts);
    }

    private void UpdateProjectiles(WorldSnapshot previous, WorldSnapshot current)
    {
        var activeIds = new HashSet<int>();
        foreach (ProjectileSnapshot projectile in current.Projectiles)
        {
            activeIds.Add(projectile.Id);
            if (!_projectiles.TryGetValue(projectile.Id, out Node3D? visual))
            {
                visual = CreatePulseBoltVisual(projectile.Id);
                AddChild(visual);
                _projectiles.Add(projectile.Id, visual);
                PlayPositionalSound(
                    $"PulseCannonFire{projectile.Id}",
                    _pulseCannonFireSound,
                    ToSpawnWorld(projectile));
            }

            visual.Position = ToWorld(projectile);
            var direction = new Vector3(
                projectile.Velocity.X,
                projectile.VerticalVelocityMillimetersPerTick,
                -projectile.Velocity.Z);
            if (!direction.IsZeroApprox())
            {
                visual.LookAt(visual.Position + direction.Normalized(), Vector3.Up);
            }
        }

        foreach (int id in _projectiles.Keys.Where(id => !activeIds.Contains(id)).ToArray())
        {
            _projectiles[id].QueueFree();
            _projectiles.Remove(id);
        }

        if (current.Tick == _lastTargetEffectTick || current.Tick == previous.Tick)
        {
            return;
        }

        foreach (TargetSnapshot target in current.Targets.Where(item => item.Id is >= 1 and <= 4))
        {
            TargetSnapshot previousTarget = previous.Targets.Single(item => item.Id == target.Id);
            if (target.Hull >= previousTarget.Hull)
            {
                continue;
            }

            float effectHeight = target.Id == 4 ? 2f : 0.7f;
            Vector3 effectPosition = _level100Targets[target.Id].Position +
                (Vector3.Up * effectHeight);
            if (target.Id == 4)
            {
                PlayPositionalSound(
                    $"PulseImpact{target.Id}-{current.Tick}",
                    _pulseImpactSmallSound,
                    effectPosition);
                SpawnPulseImpact(effectPosition, target.Id, current.Tick);
                continue;
            }

            if (target.IsActive)
            {
                PlayPositionalSound(
                    $"PulseImpact{target.Id}-{current.Tick}",
                    _pulseImpactSmallSound,
                    effectPosition);
                SpawnPulseImpact(effectPosition, target.Id, current.Tick);
            }
            else
            {
                PlayPositionalSound(
                    $"TargetTankExplosion{target.Id}",
                    _targetTankExplosionMediumSound,
                    effectPosition);
                SpawnTargetTankDestruction(effectPosition, target.Id);
            }
        }

        _lastTargetEffectTick = current.Tick;
    }

    private void BuildPulseCannonPresentation()
    {
        Texture2D spark = CuratedAyaTextureLoader.Load(
            "res://Assets/Level100/Textures/pulse-bolt-blue-spark.texture.aya",
            64,
            64);
        Texture2D trail = CuratedAyaTextureLoader.Load(
            "res://Assets/Level100/Textures/pulse-bolt-blue-trail.texture.aya",
            64,
            64,
            CuratedAyaTextureLoader.Compression.Dxt1);
        Texture2D halo = CuratedAyaTextureLoader.Load(
            "res://Assets/Level100/Textures/mech-pulse-medium-halo.texture.aya",
            64,
            64,
            CuratedAyaTextureLoader.Compression.Dxt1);
        Texture2D energyTrail = CuratedAyaTextureLoader.Load(
            "res://Assets/Level100/Textures/mech-pulse-medium-energy-trail.texture.aya",
            64,
            64,
            CuratedAyaTextureLoader.Compression.Dxt1);
        _pulseBoltSparkMaterial = CreatePulseParticleMaterial(spark, billboard: true);
        _pulseBoltTrailMaterial = CreatePulseParticleMaterial(trail, billboard: false);
        _pulseBoltHaloMaterial = CreatePulseParticleMaterial(halo, billboard: true);
        _pulseBoltEnergyTrailMaterial = CreatePulseParticleMaterial(
            energyTrail,
            billboard: false);

        _pulseImpactAnimatedTexture = CuratedAyaTextureLoader.Load(
            "res://Assets/Level100/Textures/pulse-impact-animated-blob.texture.aya",
            256,
            256);
        _pulseImpactShockwaveTexture = CuratedAyaTextureLoader.Load(
            "res://Assets/Level100/Textures/pulse-impact-shockwave.texture.aya",
            128,
            128,
            CuratedAyaTextureLoader.Compression.Dxt1);
        _effectFlashMediumTexture = CuratedAyaTextureLoader.Load(
            "res://Assets/Level100/Textures/effect-flash-medium.texture.aya",
            128,
            128,
            CuratedAyaTextureLoader.Compression.Dxt1);
        _targetTankExplosionAnimatedTexture = CuratedAyaTextureLoader.Load(
            "res://Assets/Level100/Textures/target-tank-explosion-animated.texture.aya",
            256,
            256,
            CuratedAyaTextureLoader.Compression.Dxt1);
        _targetTankExplosionFireballTexture = CuratedAyaTextureLoader.Load(
            "res://Assets/Level100/Textures/target-tank-explosion-fireball.texture.aya",
            256,
            256);

        _pulseCannonFireSound = LoadAudioStream(
            "res://Assets/Level100/SoundEffects/pulse-cannon-fire.wav");
        _pulseImpactSmallSound = LoadAudioStream(
            "res://Assets/Level100/SoundEffects/pulse-impact-small.wav");
        _targetTankExplosionMediumSound = LoadAudioStream(
            "res://Assets/Level100/SoundEffects/target-tank-explosion-medium.wav");
    }

    private void SpawnPulseImpact(Vector3 position, int targetId, int tick)
    {
        Node3D root = CreateTimedEffect($"PulseImpact{targetId}-{tick}", position, 1.05d);
        MeshInstance3D animatedBlob = CreateEffectSprite(
            "BlueAnimatedBlob",
            _pulseImpactAnimatedTexture,
            1.4f,
            columns: 4,
            rows: 4);
        root.AddChild(animatedBlob);
        AnimateAtlas(root, animatedBlob, frames: 15, columns: 4, rows: 4, 1d);
        AnimateScale(animatedBlob, 1f, 1.07f, 1d);

        MeshInstance3D flash = CreateEffectSprite(
            "FlashMedium",
            _effectFlashMediumTexture,
            3f);
        root.AddChild(flash);
        AnimateScale(flash, 1f, 0f, 0.3d);

        MeshInstance3D shockwave = CreateEffectSprite(
            "PulseBlastShockwave",
            _pulseImpactShockwaveTexture,
            1f);
        root.AddChild(shockwave);
        AnimateScale(shockwave, 1f, 2f, 0.5d);
    }

    private void SpawnTargetTankDestruction(Vector3 position, int targetId)
    {
        Node3D root = CreateTimedEffect($"TargetTankDestruction{targetId}", position, 1.55d);
        MeshInstance3D animatedExplosion = CreateEffectSprite(
            "ExplosionAnimatedSprite",
            _targetTankExplosionAnimatedTexture,
            3f,
            columns: 4,
            rows: 2);
        root.AddChild(animatedExplosion);
        AnimateAtlas(root, animatedExplosion, frames: 8, columns: 4, rows: 2, 0.5d);
        AnimateScale(animatedExplosion, 1f, 1.3f / 1.5f, 0.5d);

        MeshInstance3D fireball = CreateEffectSprite(
            "ExplosionFireball",
            _targetTankExplosionFireballTexture,
            2f,
            columns: 4,
            rows: 4);
        root.AddChild(fireball);
        AnimateAtlas(root, fireball, frames: 16, columns: 4, rows: 4, 1.5d);
        AnimateScale(fireball, 1f, 0.5f, 1.5d);
    }

    private Node3D CreateTimedEffect(string name, Vector3 position, double lifetimeSeconds)
    {
        var root = new Node3D
        {
            Name = name,
            Position = position,
        };
        AddChild(root);
        var lifetime = new Godot.Timer
        {
            Name = "Lifetime",
            OneShot = true,
            WaitTime = lifetimeSeconds,
        };
        lifetime.Timeout += root.QueueFree;
        root.AddChild(lifetime);
        lifetime.Start();
        return root;
    }

    private static MeshInstance3D CreateEffectSprite(
        string name,
        Texture2D texture,
        float size,
        int columns = 1,
        int rows = 1)
    {
        StandardMaterial3D material = CreatePulseParticleMaterial(
            texture,
            billboard: true);
        material.Uv1Scale = new Vector3(1f / columns, 1f / rows, 1f);
        return new MeshInstance3D
        {
            Name = name,
            Mesh = new QuadMesh { Size = new Vector2(size, size) },
            MaterialOverride = material,
        };
    }

    private static void AnimateAtlas(
        Node root,
        MeshInstance3D sprite,
        int frames,
        int columns,
        int rows,
        double durationSeconds)
    {
        var material = (StandardMaterial3D)sprite.MaterialOverride;
        Tween tween = root.CreateTween();
        double frameDuration = durationSeconds / frames;
        for (int frame = 0; frame < frames; frame++)
        {
            int capturedFrame = frame;
            tween.TweenCallback(Callable.From(() =>
            {
                material.Uv1Offset = new Vector3(
                    (capturedFrame % columns) / (float)columns,
                    (capturedFrame / columns) / (float)rows,
                    0f);
            }));
            tween.TweenInterval(frameDuration);
        }
    }

    private static void AnimateScale(Node3D node, float start, float end, double durationSeconds)
    {
        node.Scale = Vector3.One * start;
        node.CreateTween().TweenProperty(
            node,
            new NodePath("scale"),
            Vector3.One * end,
            durationSeconds);
    }

    private void PlayPositionalSound(string name, AudioStream stream, Vector3 position)
    {
        var player = new AudioStreamPlayer3D
        {
            Name = name,
            Stream = stream,
            Position = position,
            MaxDistance = 80f,
            UnitSize = 8f,
        };
        player.Finished += player.QueueFree;
        AddChild(player);
        player.Play();
    }

    private void PlayAttachedSound(string name, AudioStream stream)
    {
        var player = new AudioStreamPlayer3D
        {
            Name = name,
            Stream = stream,
            Position = Vector3.Zero,
            MaxDistance = 80f,
            UnitSize = 8f,
        };
        player.Finished += player.QueueFree;
        _playerRoot.AddChild(player);
        player.Play();
    }

    private static AudioStream LoadAudioStream(string resourcePath)
    {
        byte[] wave = Godot.FileAccess.GetFileAsBytes(resourcePath);
        if (wave.Length < 44 ||
            !wave.AsSpan(0, 4).SequenceEqual("RIFF"u8) ||
            !wave.AsSpan(8, 4).SequenceEqual("WAVE"u8) ||
            !wave.AsSpan(12, 4).SequenceEqual("fmt "u8) ||
            BinaryPrimitives.ReadUInt32LittleEndian(wave.AsSpan(16, 4)) != 16 ||
            BinaryPrimitives.ReadUInt16LittleEndian(wave.AsSpan(20, 2)) != 1 ||
            BinaryPrimitives.ReadUInt16LittleEndian(wave.AsSpan(22, 2)) != 1 ||
            BinaryPrimitives.ReadUInt32LittleEndian(wave.AsSpan(24, 4)) != 44_100 ||
            BinaryPrimitives.ReadUInt16LittleEndian(wave.AsSpan(34, 2)) != 16 ||
            !wave.AsSpan(36, 4).SequenceEqual("data"u8))
        {
            throw new InvalidDataException(
                $"Curated audio '{resourcePath}' is not 44.1 kHz mono 16-bit PCM WAV.");
        }

        uint dataLength = BinaryPrimitives.ReadUInt32LittleEndian(wave.AsSpan(40, 4));
        if (dataLength != wave.Length - 44)
        {
            throw new InvalidDataException($"Curated audio '{resourcePath}' has invalid WAV framing.");
        }

        return new AudioStreamWav
        {
            Format = AudioStreamWav.FormatEnum.Format16Bits,
            MixRate = 44_100,
            Stereo = false,
            Data = wave.AsSpan(44).ToArray(),
        };
    }

    private Node3D CreatePulseBoltVisual(int id)
    {
        var root = new Node3D { Name = $"RetailPulseBolt{id}" };
        root.AddChild(new MeshInstance3D
        {
            Name = "PulseBoltSprite",
            Mesh = new QuadMesh { Size = new Vector2(0.5f, 0.5f) },
            MaterialOverride = _pulseBoltSparkMaterial,
        });
        root.AddChild(new MeshInstance3D
        {
            Name = "PulseBoltHalo",
            Mesh = new QuadMesh { Size = new Vector2(0.6f, 0.6f) },
            MaterialOverride = _pulseBoltHaloMaterial,
        });
        root.AddChild(VisualPrimitives.CreateCylinder(
            "PulseBoltEnergyTrail",
            0.25f,
            0.2f,
            new Vector3(0f, 0f, 0.1f),
            _pulseBoltEnergyTrailMaterial,
            new Vector3(90f, 0f, 0f)));
        float trailLength = SimulationConstants.ProjectileSpeedPerTick / 1_000f;
        root.AddChild(VisualPrimitives.CreateBox(
            "PulseBoltTrail",
            new Vector3(0.08f, 0.08f, trailLength),
            new Vector3(0f, 0f, trailLength * 0.5f),
            _pulseBoltTrailMaterial));
        return root;
    }

    private static StandardMaterial3D CreatePulseParticleMaterial(
        Texture2D texture,
        bool billboard)
    {
        return new StandardMaterial3D
        {
            AlbedoTexture = texture,
            ShadingMode = BaseMaterial3D.ShadingModeEnum.Unshaded,
            CullMode = BaseMaterial3D.CullModeEnum.Disabled,
            Transparency = BaseMaterial3D.TransparencyEnum.Alpha,
            BlendMode = BaseMaterial3D.BlendModeEnum.Add,
            BillboardMode = billboard
                ? BaseMaterial3D.BillboardModeEnum.Enabled
                : BaseMaterial3D.BillboardModeEnum.Disabled,
            EmissionEnabled = true,
            Emission = Colors.White,
            EmissionTexture = texture,
            EmissionEnergyMultiplier = 1f,
        };
    }

    private static Vector3 ToWorld(ProjectileSnapshot projectile)
    {
        return new Vector3(
            projectile.Position.X * UnitsToMeters,
            projectile.ElevationMillimeters * UnitsToMeters,
            -projectile.Position.Z * UnitsToMeters);
    }

    private static Vector3 ToSpawnWorld(ProjectileSnapshot projectile)
    {
        return new Vector3(
            (projectile.Position.X - projectile.Velocity.X) * UnitsToMeters,
            (projectile.ElevationMillimeters -
                projectile.VerticalVelocityMillimetersPerTick) * UnitsToMeters,
            -(projectile.Position.Z - projectile.Velocity.Z) * UnitsToMeters);
    }

    private void UpdateCamera(
        Vector3 playerGroundPosition,
        float yaw,
        float pitch,
        float openingElapsedSeconds,
        bool attachedView)
    {
        float pitchCos = Mathf.Cos(pitch);
        var forward = new Vector3(
            -Mathf.Sin(yaw) * pitchCos,
            -Mathf.Sin(pitch),
            -Mathf.Cos(yaw) * pitchCos);
        var right = new Vector3(Mathf.Cos(yaw), 0f, -Mathf.Sin(yaw));
        Vector3 centerOfGravity = playerGroundPosition +
            (Vector3.Up * RetailWalkerCenterOfGravityHeight);

        if (attachedView)
        {
            _camera.Position = centerOfGravity;
            _camera.LookAt(centerOfGravity + forward, Vector3.Up);
        }
        else
        {
            Vector3 point0 = centerOfGravity + (forward * 10f) + (Vector3.Up * 4.3f);
            Vector3 point1 = centerOfGravity + (right * 5f) - (Vector3.Up * 1.3f);
            Vector3 point2 = centerOfGravity - (forward * 9f) + (Vector3.Up * 1.3f);
            Vector3 point3 = centerOfGravity - (forward * 2.5f);
            float fraction = Mathf.Clamp(openingElapsedSeconds / RetailOpeningPanSeconds, 0f, 0.999999f);
            _camera.Position = EvaluateRetailOpeningSpline(point0, point1, point2, point3, fraction);
            _camera.LookAt(centerOfGravity, Vector3.Up);
        }

        _level100Sky.Position = _camera.Position;
    }

    private static float GetOpeningElapsedTicks(
        WorldSnapshot previous,
        WorldSnapshot current,
        float interpolationAlpha)
    {
        float previousElapsed = SimulationConstants.Level100OpeningPanTicks -
            previous.Level100OpeningTicksRemaining;
        float currentElapsed = SimulationConstants.Level100OpeningPanTicks -
            current.Level100OpeningTicksRemaining;
        if (currentElapsed < previousElapsed)
        {
            return currentElapsed;
        }

        return Mathf.Lerp(previousElapsed, currentElapsed, interpolationAlpha);
    }

    private static Vector3 EvaluateRetailOpeningSpline(
        Vector3 point0,
        Vector3 point1,
        Vector3 point2,
        Vector3 point3,
        float fraction)
    {
        // Steam CBSpline uses order 3 with knots [0,0,0,1,2,2,2] for these
        // four points, so the released path is a clamped quadratic B-spline.
        float u = fraction * 2f;
        if (u < 1f)
        {
            float oneMinusU = 1f - u;
            return (point0 * oneMinusU * oneMinusU) +
                (point1 * (2f * u - 1.5f * u * u)) +
                (point2 * (0.5f * u * u));
        }

        float twoMinusU = 2f - u;
        float uMinusOne = u - 1f;
        return (point1 * (0.5f * twoMinusU * twoMinusU)) +
            (point2 * (2f * twoMinusU - 1.5f * twoMinusU * twoMinusU)) +
            (point3 * (uMinusOne * uMinusOne));
    }

    private static Vector3 ToPlayerWorld(WorldSnapshot snapshot)
    {
        float x = snapshot.PlayerPosition.X * UnitsToMeters;
        float z = snapshot.PlayerPosition.Z * UnitsToMeters;
        return new Vector3(
            x,
            snapshot.PlayerGroundElevationMillimeters * UnitsToMeters,
            -z);
    }

    private Vector3 ToWorld(SimVector2 position, float heightAboveTerrain)
    {
        // BEA uses X/Y horizontally and negative Z upward. Retained geometry
        // therefore shares the Godot mapping (X, -Z, -Y).
        float x = position.X * UnitsToMeters;
        float z = position.Z * UnitsToMeters;
        return new Vector3(
            x,
            _level100Terrain.SampleRelativeHeight(x, z) + heightAboveTerrain,
            -z);
    }
}
