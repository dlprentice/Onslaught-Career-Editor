// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

public sealed partial class FirstFlightWorldView : Node3D
{
    private const float UnitsToMeters = 0.001f;
    // 2*atan(0.75), from the released binary rather than from fitting.
    // CDXEngine__SetProjectionMatrix (0x00550b10) builds proj[0][0] =
    // near/viewport_w and proj[1][1] = near/viewport_h, and the world call in
    // CDXEngine__Render (0x0053e670) passes viewport_w = near*zoom and
    // viewport_h = near*zoom*aspect. CCamera__GetAspectRatio (0x0041b070)
    // returns the constant 0.75 outside multiplayer (0x005d8bc4), and
    // CThingCamera's zoom is CBattleEngine::mZoom (thing+0x2c8), initialised to
    // 1.0 and bounded by MAX_ZOOM_OUT 1.0 / MAX_ZOOM_IN 0.4. Unzoomed play is
    // therefore tan(hfov/2)=1 and tan(vfov/2)=0.75, i.e. 90 degrees horizontal
    // and 73.739795 vertical. The 0.75 is a fixed constant, not a viewport
    // ratio. See reverse-engineering/binary-analysis/
    // player-camera-attach-and-mesh-hfov-2026-07-26.md.
    private const float RetailVerticalFovDegrees = 73.739795f;
    // The same 0.75, as the tangent the projection is actually built from.
    // Godot's frustum projection takes a near-plane extent rather than an
    // angle, and the offset below has to be expressed in those units, so the
    // tangent is the primitive and the degree figure above is its label.
    private const float RetailTanVerticalHalfFov = 0.75f;
    private const float RetailNearPlane = 0.1f;
    private const float RetailFarPlane = 700f;
    // Retail rasterises through Direct3D 9, whose pixel-centre convention puts
    // the same geometry half a pixel down and right of where a modern
    // rasteriser puts it. Measured, not assumed: high-pass registration of the
    // reconstruction's Level 100 frame against retail's peaks at
    // dy = +0.50, dx = +0.50 (correlation 0.604 against 0.295 unshifted), and
    // 14 of 15 independent 64x128 blocks return exactly (+0.50, +0.50), so it
    // is a constant frame-global translation rather than a projection or
    // field-of-view error. Control: applying the same shift to the RETAIL
    // frame instead drives the correlation to -0.036. See
    // reverse-engineering/binary-analysis/
    // terrain-spatial-dispersion-negative-2026-07-26.md section 3.
    //
    // It is corrected in the projection, not by resampling the frame and not
    // in any shader: resampling blurs exactly what it corrects, and the offset
    // moves the sky as well as the terrain.
    private const float RetailPixelCentreOffsetPixels = 0.5f;
    // The cockpit is NOT drawn in the camera's own basis. Retail's cockpit
    // render thing gets its orientation from the virtual at 0x004254f0, which
    // composes a 3x4 matrix held at CCockpit+0x2c - the cockpit's own
    // orientation-offset ("shake") matrix, seeded to identity by the
    // constructor - onto the battle engine's orientation at battleEngine+0x3c,
    // which is the same orientation CThingCamera::GetOrientation hands the
    // camera. So the drawn cockpit basis is the camera basis PRE-MULTIPLIED by
    // whatever CCockpit+0x2c holds, and until this constant existed the
    // reconstruction was implicitly asserting that it holds identity.
    //
    // It does not. Read out of a running COPY of the game
    // (local-lab/safe-copy-bea-pristine/BEA.exe, sha256 E1436EF7E0AD9CCBDDD43
    // AAACA952F6E84D4B1A282835CEAD745EFCFC32FADF4) at the Level 100 cockpit
    // draw, breakpoint window armed at 0x0053bb50 and disarmed at 0x0053ec6f,
    // dumped at 0x0053bb56 where ESI is the CCockpit, three draw windows, all
    // three identical, memory reads only:
    //
    //     CCockpit+0x2c  =  +0.99880058  +0.02999347  +0.03870098
    //                       -0.03041990  +0.99948227  +0.01047720
    //                       -0.03836670  -0.01164191  +0.99919593
    //
    // a proper rotation of 2.877224 degrees (det +0.99999998). In the same
    // read battleEngine+0x3c is an EXACT pure yaw of 29.211108 degrees with
    // zero tilt, matching the captured view matrix's forward yaw of
    // 119.211107 degrees, and battleEngine mPos is exactly the level's
    // player-start constant. So the whole cockpit-vs-camera discrepancy is
    // this one matrix and none of it is the camera's.
    //
    // Two identities close it against the independently captured
    // SetTransform(D3DTS_WORLDMATRIX(0)) values, at float32 precision:
    //     W_0 = S^T . B^T                              (max abs err 1.209e-07)
    //     C   = W_0 . R_view = S^T . P                 (max abs err 3.080e-07)
    // where P is the exact axis map x->x, y->z, z->-y that this renderer
    // realises. The basis below is that S carried into Godot camera space; it
    // reproduces retail's measured cockpit-local-to-camera basis exactly, and
    // the value derived from the composed capture instead of from S agrees
    // with it to 3.080e-07.
    //
    // HONESTY BOUND, and it is the reason this is scoped rather than global.
    // This value is MEASURED AND IDENTIFIED, not DERIVED: the shake updater at
    // 0x00424ca0 reads CCockpit+0xb0, which the same read shows holding EXACT
    // identity with every shake input zero (CCockpit+0x9c, +0xa0, the shake
    // position CCockpit+0x0c..0x14, battleEngine+0x278/+0x27c/+0x280), so
    // nothing here reproduces the value - a snapshot shows current state, not
    // write history, and whether CCockpit+0x2c is a latched previous state, a
    // write from a second updater such as 0x004250f0, or a residue from the
    // level-entry sequence is NOT established. Two things it is NOT, both
    // tested: it is not the mesh's Camera01 node (composing that
    // 0.499873-degree node out in all four orders leaves 2.61-3.20 degrees),
    // and it is not the instantaneous terrain normal (CDXLandscape's own
    // routine at 0x0047ec60, reproduced exactly from the HFLD, returns
    // 8.545 degrees at down-azimuth 87.9 at the walker's position against the
    // measured 2.298 at 44.36; no lattice cell within +/-24 units matches).
    // It is therefore correct for Level 100's single frozen pose - the only
    // pose that level presents - and must not be promoted to a general
    // cockpit mount until the generator is closed.
    //
    // See local-lab/COMPOSITION-RESIDUAL-2026-07-26.md.
    private static readonly Basis RetailNoCockpitOrientationOffset = Basis.Identity;
    private static readonly Basis RetailLevel100CockpitOrientationOffset = new(
        new Vector3(0.99880058f, 0.03836670f, 0.03041990f),
        new Vector3(-0.03870098f, 0.99919593f, 0.01047720f),
        new Vector3(-0.02999347f, -0.01164191f, 0.99948227f));

    // Import-time mesh catalog only. All live actor/projectile identity, joins,
    // interpolation and trail state belong to Scenes/World/world_entities.gd.
    private readonly Dictionary<Level100TargetVisualBinding, Mesh>
        _level100TargetAssets = [];
    private Node3D _playerRoot = null!;
    private Node3D _playerBodyPivot = null!;
    private RetailAquilaWalkerAsset _walkerAsset = null!;
    private RetailAquilaWalkerAsset _jetAsset = null!;
    private RetailAquilaWalkerAsset _cockpitAsset = null!;
    private MeshInstance3D _level100Sky = null!;
    private Level100SunAsset _level100Sun = null!;
    private Level100HeightFieldAsset _level100Terrain = null!;
    private Level100TerrainAppearanceAsset _level100TerrainAppearance = null!;
    private Level100StaticWorldAsset _level100StaticWorld = null!;
    private Texture2D _retailChrome3Texture = null!;
    private Texture2D _warehouseOverlayTexture = null!;
    private Camera3D _camera = null!;
    private Texture2D _pulseImpactAnimatedTexture = null!;
    private Texture2D _pulseImpactShockwaveTexture = null!;
    private Texture2D _vulcanImpactSparkTexture = null!;
    private Texture2D _effectFlashMediumTexture = null!;
    private Texture2D _targetTankExplosionAnimatedTexture = null!;
    private Texture2D _targetTankExplosionFireballTexture = null!;
    // Detached native clock fact used only by the remaining impact effects.
    private float _particlePresentationSeconds;
    public int TargetVisualCount => _targetVisualCount;

    public int ProjectileVisualCount => _projectileVisualCount;

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

    public int RetailLevel100TargetSurfaceCount => _targetSurfaceCount;

    public int RetailLevel100TerrainVertexCount => _level100Terrain.VertexCount;

    public int RetailLevel100TerrainTriangleCount => _level100Terrain.TriangleCount;

    public int RetailLevel100SkySurfaceCount => _level100Sky.Mesh?.GetSurfaceCount() ?? 0;

    public float Level100PlayerStartRelativeHeight => _level100Terrain.SampleRelativeHeight(0f, 0f);

    public bool ShowHud { get; private set; }

    public bool OpeningPanActive { get; private set; }

    public override void _Notification(int what)
    {
        // Reparenting/removing a live world does not reset native presentation
        // owners. Release them only when the owning node is destroyed.
        if (what == NotificationPredelete)
        {
            _level100StaticWorld?.Animation.Dispose();
            _level100TerrainAppearance?.Dispose();
            _level100Terrain?.Dispose();
        }
    }

    public void Initialize(WorldSnapshot snapshot)
    {
        BindProductionScene(snapshot);
        Render(snapshot, snapshot, 0f, 0f);
    }

    // Explicit import entry only. Runtime instantiates the resulting production
    // scene and binds its existing nodes; editor inspection executes no code.
    internal void BuildImportedScene(WorldSnapshot snapshot)
    {
        Name = "WorldView";
        BuildLevel100Terrain();
        BuildEnvironment();
        BuildLevel100StaticWorld();
        LoadSharedRetailMaterialTextures();
        BuildLevel100Targets();
        BuildPlayer();
        BuildCamera();
        CreateEntityPresentation();
        BuildPulseCannonPresentation();
        ConfigureEntityPresentation(snapshot);
        CreateWorldPresentation();
        ConfigureWorldPresentation();
        Render(snapshot, snapshot, 0f, 0f);
    }

    public void Render(WorldSnapshot previous, WorldSnapshot current,
        float interpolationAlpha, float frameDelta)
    {
        var failures = new List<System.Runtime.ExceptionServices.ExceptionDispatchInfo>();
        using Godot.Collections.Dictionary facts = WorldFrameFacts(previous, current, interpolationAlpha, frameDelta, failures);
        using Variant batch = facts;
        using Variant returned = _worldPresentation.Call("render_frame", batch);
        using Godot.Collections.Dictionary result = WorldPresentationResult(returned, failures);
    }

    public void ConsumeLevel100DestructionEvents(
        IReadOnlyList<Level100DestructionEvent> events,
        int tick)
    {
        ArgumentNullException.ThrowIfNull(events);
        foreach (Level100DestructionEvent item in events)
        {
            Vector3 position = new(
                item.Position.X * UnitsToMeters,
                -item.Position.Z * UnitsToMeters,
                -item.Position.Y * UnitsToMeters);
            switch (item.EffectKind)
            {
                case Level100DestructionEffectKind.None:
                    break;
                case Level100DestructionEffectKind.PulseImpact:
                    SpawnPulseImpact(position, item.ActorId, tick);
                    break;
                case Level100DestructionEffectKind.VulcanImpact:
                    SpawnVulcanImpact(position, item.ActorId, tick);
                    break;
                case Level100DestructionEffectKind.TargetDestroyed:
                    SpawnTargetTankDestruction(position, item.ActorId);
                    break;
                case Level100DestructionEffectKind.DroneDestroyed:
                    SpawnTargetDroneDestruction(position, item.ActorId);
                    break;
                case Level100DestructionEffectKind.FacilityDestroyed:
                    SpawnFacilityDestruction(position, item.ActorId);
                    break;
                default:
                    throw new InvalidDataException(
                        $"Core exposed unknown Level 100 destruction effect " +
                        $"{item.EffectKind}.");
            }
        }
    }

    public void ConsumeLevel100WeaponFireEvents(IReadOnlyList<Level100WeaponFireEvent> events)
    {
        ArgumentNullException.ThrowIfNull(events);
        using var weapons = new Godot.Collections.Array();
        foreach (Level100WeaponFireEvent? item in events)
            weapons.Add(item is null ? default(Variant) : (int)item.Weapon);
        using Variant batch = weapons;
        using Variant returned = _worldPresentation.Call("queue_weapon_events", batch);
        using Godot.Collections.Dictionary result = WorldPresentationResult(returned);
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

        // The sky cube paints its own soft sun disc. The flare is a separate
        // particle the released engine adds every frame on top of it -
        // references/Onslaught/DXEngine.cpp:968-1066 - so it is a separate node
        // here too, and it follows the camera rather than the world.
        _level100Sun = Level100SunAsset.Create(_level100Terrain);
        AddChild(_level100Sun.Root);
    }

    private void BuildLevel100Terrain()
    {
        _level100Terrain = Level100HeightFieldAsset.Load();
        _level100TerrainAppearance = Level100TerrainAppearanceAsset.Load(
            "res://Assets/Level100/Source/level100-root-terrain.rgb565.bin",
            "res://Assets/Level100/Source/level100-terrain-hierarchy.bin",
            "res://Assets/Level100/Textures/terrain-detail-00.texture.aya",
            "res://Assets/Level100/Textures/terrain-cloud-shadow.texture.aya",
            _level100Terrain);
        AddChild(new MeshInstance3D
        {
            Name = "RetailLevel100HeightField",
            Mesh = _level100Terrain.Mesh,
            MaterialOverride = _level100TerrainAppearance.Material,
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

        Texture2D truckTexture = CuratedAyaTextureLoader.Load(
            "res://Assets/Level100/Textures/target-truck.texture.aya",
            512,
            512);
        Material truckMaterial = CreateRetailMaterial(
            truckTexture,
            reflection: RetailLayer(_retailChrome3Texture, 0.199999988f));
        Mesh truckMesh = CuratedObjMeshLoader.Load(
            "res://Assets/Level100/level100-target-truck.obj",
            new Dictionary<string, Material>(StringComparer.Ordinal)
            {
                ["layers-00000000-ffffffff-00000001-ffffffff-ffffffff-ffffffff"] =
                    truckMaterial,
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

        // Task #114, the airborne units. `m_FA_F24_training.msh.aya` serves the
        // Air Trainer and all nine Target Drones, and its material table is the
        // Target Tank's verbatim: MEASURED from the mesh's own MSHT/TEXB
        // records, both meshes name (meshtex\f_pulsetank_training.tga,
        // meshtex\Chrome3.tga) with the Chrome3 record carrying strength
        // 0x3E4CCCCC = 0.19999998807907104, zero offset and unit scale, and
        // both emit the single material group
        // layers-00000000-ffffffff-00000001-ffffffff-ffffffff-ffffffff. So the
        // aircraft reuses `tankMaterial` rather than rebuilding an equal one.
        Mesh airTrainerMesh = CuratedObjMeshLoader.Load(
            "res://Assets/Level100/level100-air-trainer.obj",
            new Dictionary<string, Material>(StringComparer.Ordinal)
            {
                ["layers-00000000-ffffffff-00000001-ffffffff-ffffffff-ffffffff"] =
                    tankMaterial,
            });

        // The U-17 Highside Transporter is the one actor here that needs its
        // own textures. Its table is (f_lifter02, Chrome3, f_lifter01, Chrome3)
        // and its two material groups take base slot 0 and base slot 2 against
        // the same Chrome3 reflection at the same 0.19999998807907104 strength.
        // WATCH THE INVERSION: group `...-00000000-...` is f_lifter02 and group
        // `...-00000002-...` is f_lifter01.
        Texture2D transporterLifter01Texture = CuratedAyaTextureLoader.Load(
            "res://Assets/Level100/Textures/transporter-lifter01.texture.aya",
            512,
            512);
        Texture2D transporterLifter02Texture = CuratedAyaTextureLoader.Load(
            "res://Assets/Level100/Textures/transporter-lifter02.texture.aya",
            512,
            512);
        Mesh transporterMesh = CuratedObjMeshLoader.Load(
            "res://Assets/Level100/level100-transporter.obj",
            new Dictionary<string, Material>(StringComparer.Ordinal)
            {
                ["layers-00000000-ffffffff-00000001-ffffffff-ffffffff-ffffffff"] =
                    CreateRetailMaterial(
                        transporterLifter02Texture,
                        reflection: RetailLayer(
                            _retailChrome3Texture,
                            0.199999988f)),
                ["layers-00000002-ffffffff-00000001-ffffffff-ffffffff-ffffffff"] =
                    CreateRetailMaterial(
                        transporterLifter01Texture,
                        reflection: RetailLayer(
                            _retailChrome3Texture,
                            0.199999988f)),
            });

        _level100TargetAssets.Add(
            Level100TargetPresentation.TargetTankBinding,
            tankMesh);
        _level100TargetAssets.Add(
            Level100TargetPresentation.TargetTruckBinding,
            truckMesh);
        _level100TargetAssets.Add(
            Level100TargetPresentation.WarehouseBinding,
            warehouseMesh);
        _level100TargetAssets.Add(
            Level100TargetPresentation.AirTrainerBinding,
            airTrainerMesh);
        _level100TargetAssets.Add(
            Level100TargetPresentation.TargetDroneBinding,
            airTrainerMesh);
        _level100TargetAssets.Add(
            Level100TargetPresentation.TransporterBinding,
            transporterMesh);

    }

    private void BuildPlayer()
    {
        _playerRoot = new Node3D { Name = "PlayerVisual" };
        AddChild(_playerRoot);
        _playerBodyPivot = new Node3D { Name = "BodyPivot" };
        _playerRoot.AddChild(_playerBodyPivot);

        _walkerAsset = RetailAquilaWalkerAsset.CreateWalker(_level100Terrain);
        _jetAsset = RetailAquilaWalkerAsset.CreateJet(_level100Terrain);
        _playerBodyPivot.AddChild(_walkerAsset.Root);
        _playerBodyPivot.AddChild(_jetAsset.Root);
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
            Near = RetailNearPlane,
            Far = RetailFarPlane,
            Current = true,
        };
        // Frustum rather than Perspective only so the half-pixel translation
        // has somewhere to live. Godot's frustum projection with the default
        // KEEP_HEIGHT aspect takes Size as the FULL vertical extent at the
        // near plane and derives the horizontal extent as Size * aspect, so
        // Size = 2 * Near * tan(vfov/2) reproduces the perspective projection
        // this replaces exactly when FrustumOffset is zero.
        _camera.Projection = Camera3D.ProjectionType.Frustum;
        _camera.Size = 2f * _camera.Near * RetailTanVerticalHalfFov;
        AddChild(_camera);
        UpdateRetailPixelCentreOffset();

        _cockpitAsset = RetailAquilaWalkerAsset.CreateCockpit(_level100Terrain);
        _camera.AddChild(_cockpitAsset.Root);
        // Retail composes CCockpit+0x2c onto the camera's own orientation
        // before the cockpit is drawn (see the constant's provenance above).
        // The default is identity - "this build does not model the cockpit
        // orientation offset" - and only the measured Level 100 value is
        // supplied, because only Level 100's pose has been observed.
        _cockpitAsset.Root.Basis = CockpitOrientationOffset;
    }

    /// <summary>
    /// The cockpit's orientation offset relative to the camera, as retail's
    /// cockpit render thing applies it from <c>CCockpit+0x2c</c>. Identity
    /// means "not modelled". This client only ever presents Level 100, whose
    /// value was read out of the running retail copy; a client that reached
    /// another level would need its own observation rather than this one.
    /// </summary>
    internal static Basis CockpitOrientationOffset =>
        RetailLevel100CockpitOrientationOffset;

    /// <summary>
    /// Exposed so the offset cannot be silently promoted to a default: a test
    /// pins that "no offset" remains identity and is distinct from the
    /// measured Level 100 value.
    /// </summary>
    internal static Basis CockpitOrientationOffsetDefault =>
        RetailNoCockpitOrientationOffset;

    private void BuildPulseCannonPresentation()
    {
        _pulseImpactAnimatedTexture = CuratedAyaTextureLoader.Load(
            "res://Assets/Level100/Textures/pulse-impact-animated-blob.texture.aya",
            256,
            256);
        _pulseImpactShockwaveTexture = CuratedAyaTextureLoader.Load(
            "res://Assets/Level100/Textures/pulse-impact-shockwave.texture.aya",
            128,
            128,
            CuratedAyaTextureLoader.Compression.Dxt1);
        _vulcanImpactSparkTexture = CuratedAyaTextureLoader.Load(
            "res://Assets/Level100/Textures/vulcan-impact-spark.texture.aya",
            256,
            256,
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
    }

    private void SpawnPulseImpact(Vector3 position, int targetId, int tick)
    {
        Node3D root = CreateTimedEffect($"PulseImpact{targetId}-{tick}", position, 1.05d);
        // `Blue Anim Blob Large Sprite`: Radius 0.7, Final_Radius 0.75,
        // Life 20 turns = 1.0 s, End_Frame 14 (15 cells), Random_Start_Frame 1,
        // Texture_Size 2 (a 4x4 grid) - every one of which the animation below
        // already reproduces.
        MeshInstance3D animatedBlob = CreateEffectSprite(
            "BlueAnimatedBlob",
            _pulseImpactAnimatedTexture,
            0.7f,
            columns: 4,
            rows: 4);
        root.AddChild(animatedBlob);
        AnimatePulseImpactBlob(root, animatedBlob);
        AnimateScale(animatedBlob, 1f, 1.07f, 1d);

        // `Flash Medium`: Radius 1.5, Life 6 turns = 0.3 s, Texture_Size 4 (a
        // single cell), sun2.tga.
        MeshInstance3D flash = CreateEffectSprite(
            "FlashMedium",
            _effectFlashMediumTexture,
            1.5f);
        root.AddChild(flash);
        AnimateScale(flash, 1f, 0f, 0.3d);

        MeshInstance3D blastSphere = CreatePulseBlastSphere(
            _pulseImpactShockwaveTexture);
        root.AddChild(blastSphere);
        AnimatePulseBlast(
            root,
            blastSphere,
            _particlePresentationSeconds,
            0.5d);
    }

    private void SpawnVulcanImpact(Vector3 position, int targetId, int tick)
    {
        // `Mech Bullet Hit Unit Effect` schedules `Spark Anim Sprite` at Time 0.
        // The direct sprite is alparticle2.tga, additive, Radius 0.3 -> 1.0,
        // Life 5 turns, Texture_Size 2, cells 11..15, PlayOnce at 0.8
        // cells/turn. The two sibling emitter branches remain deliberately open.
        Node3D root = CreateTimedEffect(
            $"VulcanImpact{targetId}-{tick}",
            position,
            0.25d);
        MeshInstance3D spark = CreateEffectSprite(
            "VulcanImpactSpark",
            _vulcanImpactSparkTexture,
            0.3f,
            columns: 4,
            rows: 4);
        root.AddChild(spark);
        AnimateVulcanImpactSpark(root, spark);
        AnimateScale(spark, 1f, 10f / 3f, 0.25d);
    }

    private void SpawnTargetTankDestruction(Vector3 position, int targetId)
    {
        Node3D root = CreateTimedEffect($"TargetTankDestruction{targetId}", position, 1.5d);
        // `Tank Explosion Medium` dispatches the shared `Flash` sprite at Time
        // 0: sun2.tga, Radius 5, Final_Radius 0 and Life 5 turns (0.25 s).
        MeshInstance3D flash = CreateEffectSprite(
            "TargetTankFlash",
            _effectFlashMediumTexture,
            5f);
        root.AddChild(flash);
        AnimateScale(flash, 1f, 0f, 0.25d);

        // `Explosion Anim Sprite Medium`: Radius 1.5, Final_Radius 1.3,
        // Life 10 turns = 0.5 s, End_Frame 7 (8 cells), Texture_Size 2,
        // PlayOnce at 0.7 cells/turn. Tank Explosion Medium schedules it at
        // Time 5, so this direct layer remains hidden for the first 0.25 s.
        MeshInstance3D animatedExplosion = CreateEffectSprite(
            "ExplosionAnimatedSprite",
            _targetTankExplosionAnimatedTexture,
            1.5f,
            columns: 4,
            rows: 4);
        root.AddChild(animatedExplosion);
        AnimateTargetTankDelayedExplosion(root, animatedExplosion);

        // `Fire Sprite Damped 2`: Radius 1.0, Final_Radius 0.5,
        // Life 30 turns = 1.5 s, Texture_Size 2, fireball.tga. It loops only
        // cells 0..11 at 0.5 cells/turn from one authored random start; cells
        // 12..15 are deliberately blank and are not part of this sprite.
        MeshInstance3D fireball = CreateEffectSprite(
            "ExplosionFireball",
            _targetTankExplosionFireballTexture,
            1.0f,
            columns: 4,
            rows: 4);
        root.AddChild(fireball);
        AnimateTargetTankFireball(root, fireball);
        AnimateScale(fireball, 1f, 0.5f, 1.5d);
    }

    private void SpawnTargetDroneDestruction(Vector3 position, int droneId)
    {
        Node3D root = CreateTimedEffect(
            $"TargetDroneDestruction{droneId}",
            position,
            1.5d);
        // `Drone Explosion Effect` dispatches `Flash` directly at Time 0.
        // That retained sprite is sun2.tga, Radius 5, Final_Radius 0 and Life
        // 5 released 20 Hz turns. Its debris/emitter multiplicity, placement,
        // velocity and colour evolution remain open rather than being guessed.
        MeshInstance3D flash = CreateEffectSprite(
            "DroneFlash",
            _effectFlashMediumTexture,
            5f);
        root.AddChild(flash);
        AnimateScale(flash, 1f, 0f, 0.25d);

        // `Drone Explosion Emitter` is the other Time-0 branch retained by
        // `Drone Explosion Effect`. One explicitly representative
        // `Fire Sprite Damped 2` preserves its bright tail: additive
        // fireball.tga, Radius 1.0 -> 0.5, Life 30 turns = 1.5 s, and
        // random-start looping cells 0..11 at 0.5 cells/turn. The emitter's
        // decreasing multiplicity, shape, placement and velocity remain open.
        MeshInstance3D fireball = CreateEffectSprite(
            "DroneFireball",
            _targetTankExplosionFireballTexture,
            1f,
            columns: 4,
            rows: 4);
        root.AddChild(fireball);
        AnimateLoopingFireball(root, fireball, lifeTurns: 30);
        AnimateScale(fireball, 1f, 0.5f, 1.5d);
    }

    private void SpawnFacilityDestruction(Vector3 position, int facilityId)
    {
        Node3D root = CreateTimedEffect(
            $"FacilityDestruction{facilityId}",
            position,
            15d);
        // `Flash Building`: direct Time-0 entry in Muspell Building Explosion
        // Effect. Radius 3, Final_Radius 0, Life 6 released 20 Hz turns = 0.30 s,
        // Texture_Size 4 (one cell), sun2.tga.
        MeshInstance3D flash = CreateEffectSprite(
            "FacilityFlash",
            _effectFlashMediumTexture,
            3f);
        root.AddChild(flash);
        AnimateScale(flash, 1f, 0f, 0.3d);

        // `Fire Sprite Damped Long`: one explicitly representative billboard
        // from the authored Time-0 Muspell Building Explosion Emitter. Radius
        // 0.5 -> 2.0, Life 60 turns = 3.0 s, random-start looping cells 0..11
        // at 0.5 cells/turn. The emitter's unresolved decreasing multiplicity,
        // placement and velocity laws remain open rather than being invented.
        MeshInstance3D fireball = CreateEffectSprite(
            "FacilityFireball",
            _targetTankExplosionFireballTexture,
            0.5f,
            columns: 4,
            rows: 4);
        root.AddChild(fireball);
        AnimateFacilityFireball(root, fireball);
        AnimateScale(fireball, 1f, 4f, 3d);

        // `Smoke Sprite Anim Large Building`: the single Time-0 smoke emitted
        // by Building Smoke Emitter. It is an alpha-blended 4x4 alparticle4
        // billboard, radius 3 -> 2, random-start looping cells 0..14 at 0.5
        // cells/turn for 300 turns = 15 seconds. Shape placement, velocity
        // randomness and Fade_Col/Life_Pct colour behavior remain open.
        MeshInstance3D smoke = CreateEffectSprite(
            "FacilitySmoke",
            _pulseImpactAnimatedTexture,
            3f,
            columns: 4,
            rows: 4);
        ((StandardMaterial3D)smoke.MaterialOverride).BlendMode =
            BaseMaterial3D.BlendModeEnum.Mix;
        root.AddChild(smoke);
        AnimateFacilitySmoke(root, smoke);
        AnimateScale(smoke, 1f, 2f / 3f, 15d);
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

    /// <summary>
    /// Builds one billboard for a sprite descriptor.
    /// </summary>
    /// <param name="authoredRadius">
    /// The descriptor's <c>Radius</c>, exactly as its <c>MainSet.par</c> record
    /// spells it. It is a HALF extent; the quad side is derived by the one
    /// owner of that law,
    /// <see cref="ParticleEffectResolver.BillboardQuadSide(float)"/>. Pass the
    /// authored number, never a pre-doubled one - a bare literal cannot be
    /// traced back to the record it came from, which is exactly how this
    /// convention came to look inconsistent (task #151).
    /// </param>
    private static MeshInstance3D CreateEffectSprite(
        string name,
        Texture2D texture,
        float authoredRadius,
        int columns = 1,
        int rows = 1)
    {
        StandardMaterial3D material = CreateEffectMaterial(texture, billboard: true);
        material.Uv1Scale = new Vector3(1f / columns, 1f / rows, 1f);
        float side = ParticleEffectResolver.BillboardQuadSide(authoredRadius);
        return new MeshInstance3D
        {
            Name = name,
            Mesh = new QuadMesh { Size = new Vector2(side, side) },
            MaterialOverride = material,
        };
    }

    private static MeshInstance3D CreatePulseBlastSphere(Texture2D texture)
    {
        StandardMaterial3D material = CreateEffectMaterial(texture, billboard: false);
        material.Uv1Scale = new Vector3(2f, 2f, 1f);
        return new MeshInstance3D
        {
            Name = "PulseBlastSphere",
            Mesh = new SphereMesh
            {
                Radius = 0.5f,
                Height = 1f,
                RadialSegments = 10,
                Rings = 10,
            },
            MaterialOverride = material,
        };
    }

    private static void AnimatePulseBlast(
        Node root,
        MeshInstance3D sphere,
        float globalSeconds,
        double durationSeconds)
    {
        var material = (StandardMaterial3D)sphere.MaterialOverride;
        float initialV = Mathf.PosMod(-2f * globalSeconds, 1f);
        Action<float> update = normalizedAge =>
        {
            // MainSet's Shockwave Medium Growth is
            // radius = 0.6*sin(normalized age)+0.4. The mesh has radius 0.5.
            float radius = (0.6f * MathF.Sin(normalizedAge)) + 0.4f;
            sphere.Scale = Vector3.One * (radius / 0.5f);
            material.Uv1Offset = new Vector3(0f, initialV - normalizedAge, 0f);
            material.AlbedoColor = Colors.White.Lerp(Colors.Black, normalizedAge);
        };
        update(0f);
        root.CreateTween().TweenMethod(
            Callable.From<float>(update),
            0f,
            1f,
            durationSeconds);
    }

    private static void AnimatePulseImpactBlob(Node root, MeshInstance3D sprite)
    {
        var material = (StandardMaterial3D)sprite.MaterialOverride;
        int startFrame = (int)(GD.Randi() % 15u);
        Tween tween = root.CreateTween();
        const int frameAdvances = 14;
        const double frameIntervalSeconds = 1d / frameAdvances;
        for (int step = 0; step <= frameAdvances; step++)
        {
            int capturedFrame = (startFrame + step) % 15;
            tween.TweenCallback(Callable.From(() =>
            {
                material.Uv1Offset = new Vector3(
                    (capturedFrame % 4) / 4f,
                    (capturedFrame / 4) / 4f,
                    0f);
            }));
            if (step < frameAdvances)
            {
                tween.TweenInterval(frameIntervalSeconds);
            }
        }
    }

    private static void AnimateVulcanImpactSpark(
        Node root,
        MeshInstance3D spark)
    {
        const int startCell = 11;
        const int endCell = 15;
        const int columns = 4;
        const int rows = 4;
        const double cellsPerTurn = 0.8d;
        double cellIntervalSeconds =
            1d / (cellsPerTurn * SimulationConstants.TicksPerSecond);
        var material = (StandardMaterial3D)spark.MaterialOverride;
        material.Uv1Offset = new Vector3(
            (startCell % columns) / (float)columns,
            (startCell / columns) / (float)rows,
            0f);

        Tween tween = root.CreateTween();
        for (int cell = startCell + 1; cell <= endCell; cell++)
        {
            int capturedCell = cell;
            tween.TweenInterval(cellIntervalSeconds);
            tween.TweenCallback(Callable.From(() =>
            {
                material.Uv1Offset = new Vector3(
                    (capturedCell % columns) / (float)columns,
                    (capturedCell / columns) / (float)rows,
                    0f);
            }));
        }
    }

    private static void AnimateTargetTankDelayedExplosion(
        Node root,
        MeshInstance3D sprite)
    {
        const int startCell = 0;
        const int endCell = 7;
        const int columns = 4;
        const int rows = 4;
        const double cellsPerTurn = 0.7d;
        const double lifeSeconds = 0.5d;
        double startDelaySeconds = 5d / SimulationConstants.TicksPerSecond;
        double cellIntervalSeconds =
            1d / (cellsPerTurn * SimulationConstants.TicksPerSecond);
        var material = (StandardMaterial3D)sprite.MaterialOverride;
        material.Uv1Offset = new Vector3(
            (startCell % columns) / (float)columns,
            (startCell / columns) / (float)rows,
            0f);
        sprite.Visible = false;
        sprite.Scale = Vector3.One;

        Tween atlasTween = root.CreateTween();
        atlasTween.TweenInterval(startDelaySeconds);
        atlasTween.TweenCallback(Callable.From(() =>
        {
            sprite.Visible = true;
        }));
        for (int cell = startCell + 1; cell <= endCell; cell++)
        {
            int capturedCell = cell;
            atlasTween.TweenInterval(cellIntervalSeconds);
            atlasTween.TweenCallback(Callable.From(() =>
            {
                material.Uv1Offset = new Vector3(
                    (capturedCell % columns) / (float)columns,
                    (capturedCell / columns) / (float)rows,
                    0f);
            }));
        }

        Tween scaleTween = root.CreateTween();
        scaleTween.TweenInterval(startDelaySeconds);
        scaleTween.TweenProperty(
            sprite,
            new NodePath("scale"),
            Vector3.One * (1.3f / 1.5f),
            lifeSeconds);
        scaleTween.TweenCallback(Callable.From(() =>
        {
            sprite.Visible = false;
        }));
    }

    private static void AnimateTargetTankFireball(
        Node root,
        MeshInstance3D sprite) =>
        AnimateLoopingFireball(root, sprite, lifeTurns: 30);

    private static void AnimateFacilityFireball(
        Node root,
        MeshInstance3D sprite) =>
        AnimateLoopingFireball(root, sprite, lifeTurns: 60);

    private static void AnimateLoopingFireball(
        Node root,
        MeshInstance3D sprite,
        int lifeTurns)
    {
        const int startCell = 0;
        const int endCell = 11;
        const int columns = 4;
        const int rows = 4;
        const double cellsPerTurn = 0.5d;
        int cellCount = endCell - startCell + 1;
        int initialCell = startCell + (int)(GD.Randi() % (uint)cellCount);
        double cellIntervalSeconds =
            1d / (cellsPerTurn * SimulationConstants.TicksPerSecond);
        int frameAdvances = (int)(lifeTurns * cellsPerTurn);
        var material = (StandardMaterial3D)sprite.MaterialOverride;
        material.Uv1Offset = new Vector3(
            (initialCell % columns) / (float)columns,
            (initialCell / columns) / (float)rows,
            0f);

        Tween tween = root.CreateTween();
        for (int step = 1; step <= frameAdvances; step++)
        {
            int capturedCell = startCell + ((initialCell - startCell + step) % cellCount);
            tween.TweenInterval(cellIntervalSeconds);
            tween.TweenCallback(Callable.From(() =>
            {
                material.Uv1Offset = new Vector3(
                    (capturedCell % columns) / (float)columns,
                    (capturedCell / columns) / (float)rows,
                    0f);
            }));
        }
        tween.TweenCallback(Callable.From(() => sprite.Visible = false));
    }

    private static void AnimateFacilitySmoke(Node root, MeshInstance3D sprite)
    {
        const int startCell = 0;
        const int endCell = 14;
        const int columns = 4;
        const int rows = 4;
        const int lifeTurns = 300;
        const double cellsPerTurn = 0.5d;
        int cellCount = endCell - startCell + 1;
        int initialCell = startCell + (int)(GD.Randi() % (uint)cellCount);
        double cellIntervalSeconds =
            1d / (cellsPerTurn * SimulationConstants.TicksPerSecond);
        int frameAdvances = (int)(lifeTurns * cellsPerTurn);
        var material = (StandardMaterial3D)sprite.MaterialOverride;
        material.Uv1Offset = new Vector3(
            (initialCell % columns) / (float)columns,
            (initialCell / columns) / (float)rows,
            0f);

        Tween tween = root.CreateTween();
        for (int step = 1; step <= frameAdvances; step++)
        {
            int capturedCell = startCell + ((initialCell - startCell + step) % cellCount);
            tween.TweenInterval(cellIntervalSeconds);
            tween.TweenCallback(Callable.From(() =>
            {
                material.Uv1Offset = new Vector3(
                    (capturedCell % columns) / (float)columns,
                    (capturedCell / columns) / (float)rows,
                    0f);
            }));
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

    private static StandardMaterial3D CreateEffectMaterial(
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
            BillboardKeepScale = billboard,
        };
    }

    private void UpdateRetailPixelCentreOffset()
    {
        using GDScript script = GD.Load<GDScript>(WorldPresentationScriptPath);
        using Variant returned = script.Call("apply_pixel_centre_offset", this, _camera);
        using Godot.Collections.Dictionary result = WorldPresentationResult(returned);
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
