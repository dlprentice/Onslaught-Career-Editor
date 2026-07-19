// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

public sealed partial class FirstFlightWorldView : Node3D
{
    private const float UnitsToMeters = 0.001f;
    private const float RetailJetBaseClearance = 0.6706632f;
    private const float RetailWalkerCenterOfGravityHeight = 1.9f;
    private const float RetailVerticalFovDegrees = 58.7155f;

    private static readonly Color SteelDark = new(0.075f, 0.105f, 0.115f);
    private static readonly Color Amber = new(0.96f, 0.52f, 0.16f);
    private static readonly Color Green = new(0.30f, 0.70f, 0.39f);
    private static readonly Color Cyan = new(0.14f, 0.78f, 0.92f);
    private static readonly Color MutedMarker = new(0.25f, 0.34f, 0.37f);
    private static readonly Color Wreck = new(0.13f, 0.12f, 0.11f);

    private readonly Dictionary<int, TargetVisual> _targets = [];
    private readonly Dictionary<int, MeshInstance3D> _projectiles = [];
    private readonly List<MeshInstance3D> _level100Facilities = [];
    private readonly List<ObjectiveMarkerVisual> _level100ObjectiveMarkers = [];
    private Node3D _playerRoot = null!;
    private Node3D _playerBodyPivot = null!;
    private RetailAquilaWalkerAsset _walkerAsset = null!;
    private MeshInstance3D _jetMesh = null!;
    private MeshInstance3D _cockpitMesh = null!;
    private MeshInstance3D _level100Sky = null!;
    private Level100HeightFieldAsset _level100Terrain = null!;
    private Camera3D _camera = null!;
    private ObjectiveMarkerVisual _targetZone1Marker = null!;
    private ObjectiveMarkerVisual _firingRangeMarker = null!;
    private float _modeBlend;
    private float _walkCycle = -Mathf.Pi;
    private int _lastWalkPoseTick = -1;

    public int TargetVisualCount => _targets.Count;

    public int ProjectileVisualCount => _projectiles.Count;

    public bool PlayerVisualPresent => IsInstanceValid(_playerRoot);

    public bool RetailAquilaMeshesPresent =>
        IsInstanceValid(_walkerAsset.Root) &&
        IsInstanceValid(_jetMesh) &&
        _walkerAsset.SurfaceCount > 0 &&
        _jetMesh.Mesh?.GetSurfaceCount() > 0;

    public int RetailAquilaSurfaceCount =>
        _walkerAsset.SurfaceCount +
        (_jetMesh.Mesh?.GetSurfaceCount() ?? 0);

    public int RetailAquilaPartCount => _walkerAsset.PartCount;

    public int RetailAquilaAnimatedPartCount => _walkerAsset.AnimatedPartCount;

    public float RetailAquilaStandingClearance => _walkerAsset.StandingClearance;

    public int RetailCockpitSurfaceCount => _cockpitMesh.Mesh?.GetSurfaceCount() ?? 0;

    public int RetailLevel100FacilityCount => _level100Facilities.Count;

    public int RetailLevel100FacilitySurfaceCount =>
        _level100Facilities.Sum(facility => facility.Mesh?.GetSurfaceCount() ?? 0);

    public int Level100ObjectiveMarkerCount => _level100ObjectiveMarkers.Count;

    public int RetailLevel100TerrainVertexCount => _level100Terrain.VertexCount;

    public int RetailLevel100TerrainTriangleCount => _level100Terrain.TriangleCount;

    public int RetailLevel100SkySurfaceCount => _level100Sky.Mesh?.GetSurfaceCount() ?? 0;

    public float Level100PlayerStartRelativeHeight => _level100Terrain.SampleRelativeHeight(0f, 0f);

    public void Initialize(WorldSnapshot snapshot)
    {
        Name = "WorldView";
        BuildLevel100Terrain();
        BuildEnvironment();
        BuildLevel100Facilities();
        BuildLevel100ObjectiveMarkers();
        BuildPlayer();
        BuildTargets(snapshot);
        BuildCamera();
        Render(snapshot, snapshot, 0f, 0f);
    }

    public void Render(
        WorldSnapshot previous,
        WorldSnapshot current,
        float interpolationAlpha,
        float frameDelta)
    {
        Vector3 previousPosition = ToWorld(previous.PlayerPosition, 0f);
        Vector3 currentPosition = ToWorld(current.PlayerPosition, 0f);
        bool resetJump = previousPosition.DistanceSquaredTo(currentPosition) > 100f;
        Vector3 playerPosition = resetJump
            ? currentPosition
            : previousPosition.Lerp(currentPosition, interpolationAlpha);
        _playerRoot.Position = playerPosition;

        float previousYaw = previous.FacingYawMicroRad / 1_000_000f;
        float currentYaw = current.FacingYawMicroRad / 1_000_000f;
        float playerYaw = Mathf.LerpAngle(previousYaw, currentYaw, interpolationAlpha);
        _playerRoot.Rotation = new Vector3(
            0f,
            playerYaw,
            0f);

        float desiredModeBlend = current.Transition == VehicleTransition.WalkerToJet
            ? 1f - (current.TransformTicksRemaining / (float)SimulationConstants.WalkerToJetTransitionTicks)
            : current.Mode == VehicleMode.Jet ? 1f : 0f;
        _modeBlend = current.Transition == VehicleTransition.WalkerToJet
            ? desiredModeBlend
            : Mathf.MoveToward(_modeBlend, desiredModeBlend, frameDelta * 8f);
        UpdateWalkerPose(current);
        UpdatePlayerShape(current);
        UpdateLevel100ObjectiveMarkers(current);
        UpdateTargets(current);
        UpdateProjectiles(current);
        UpdateCamera(playerPosition, playerYaw);
    }

    private void BuildEnvironment()
    {
        var environment = new Godot.Environment
        {
            BackgroundMode = Godot.Environment.BGMode.Color,
            BackgroundColor = _level100Terrain.FogColor,
            AmbientLightSource = Godot.Environment.AmbientSource.Color,
            AmbientLightColor = _level100Terrain.AmbientColor,
            AmbientLightEnergy = 1f,
            TonemapMode = Godot.Environment.ToneMapper.Linear,
            FogEnabled = true,
            FogLightColor = _level100Terrain.FogColor,
            FogLightEnergy = 1f,
            FogDensity = _level100Terrain.FogDensity,
            FogSkyAffect = 0f,
        };
        AddChild(new WorldEnvironment
        {
            Name = "WorldEnvironment",
            Environment = environment,
        });

        var sun = new DirectionalLight3D
        {
            Name = "SunLight",
            LightColor = _level100Terrain.SunColor,
            LightEnergy = 1f,
            ShadowEnabled = true,
        };
        sun.LookAtFromPosition(Vector3.Zero, _level100Terrain.SunlightDirection, Vector3.Up);
        AddChild(sun);

        var antiSun = new DirectionalLight3D
        {
            Name = "AntiSunLight",
            LightColor = _level100Terrain.AntiSunColor,
            LightEnergy = 1f,
            ShadowEnabled = false,
        };
        antiSun.LookAtFromPosition(Vector3.Zero, -_level100Terrain.SunlightDirection, Vector3.Up);
        AddChild(antiSun);

        _level100Sky = Level100SkyAsset.Create(_level100Terrain.SkyCube);
        AddChild(_level100Sky);
    }

    private void BuildLevel100Terrain()
    {
        _level100Terrain = Level100HeightFieldAsset.Load(
            "res://Assets/Level100/Source/level100-heightfield.hfld.bin");
        Texture2D terrainTexture = Level100TerrainAppearanceAsset.Load(
            "res://Assets/Level100/Source/level100-mixer-set-10.mapt.bin",
            "res://Assets/Level100/Source/level100-mixer-map.mmap.bin",
            _level100Terrain);
        var terrainMaterial = new StandardMaterial3D
        {
            AlbedoTexture = terrainTexture,
            ShadingMode = BaseMaterial3D.ShadingModeEnum.Unshaded,
            Roughness = 1f,
        };
        AddChild(new MeshInstance3D
        {
            Name = "RetailLevel100HeightField",
            Mesh = _level100Terrain.Mesh,
            MaterialOverride = terrainMaterial,
        });
    }

    private void BuildLevel100Facilities()
    {
        var facilityMaterials = new Dictionary<string, Material>(StringComparer.Ordinal)
        {
            ["texture-0000"] = CreateRetailMaterial(
                CuratedAyaTextureLoader.Load("res://Assets/Level100/Textures/facility-hanger-more-bits-lit.texture.aya", 512, 512),
                0.28f,
                0.72f),
            ["texture-0002"] = CreateRetailMaterial(
                CuratedAyaTextureLoader.Load("res://Assets/Level100/Textures/facility-hanger-bits.texture.aya", 512, 512),
                0.28f,
                0.72f),
            ["texture-0004"] = CreateRetailMaterial(
                CuratedAyaTextureLoader.Load("res://Assets/Level100/Textures/facility-hanger-top-02.texture.aya", 512, 512),
                0.28f,
                0.72f),
            ["texture-0006"] = CreateRetailMaterial(
                CuratedAyaTextureLoader.Load("res://Assets/Level100/Textures/facility-hanger-top-01.texture.aya", 512, 512),
                0.28f,
                0.72f),
        };
        AddLevel100Facility(
            "RetailControlTower",
            "res://Assets/Level100/level100-control-tower.obj",
            new Vector2(-13.289886f, 5.603271f),
            0.0875791f,
            0f,
            facilityMaterials);
        AddLevel100Facility(
            "RetailTankFactory",
            "res://Assets/Level100/level100-tank-factory.obj",
            new Vector2(10.125f, 22.375f),
            0.2383346f,
            1.7894337f,
            facilityMaterials);
    }

    private void AddLevel100Facility(
        string name,
        string meshPath,
        Vector2 relativePosition,
        float meshBaseClearance,
        float retailYaw,
        IReadOnlyDictionary<string, Material> materials)
    {
        var root = new Node3D
        {
            Name = name,
            Position = new Vector3(
                relativePosition.X,
                _level100Terrain.SampleRelativeHeight(relativePosition.X, relativePosition.Y) +
                    meshBaseClearance,
                relativePosition.Y),
            Rotation = new Vector3(0f, retailYaw, 0f),
        };
        var mesh = new MeshInstance3D
        {
            Name = $"{name}Geometry",
            Mesh = CuratedObjMeshLoader.Load(meshPath, materials),
            RotationDegrees = new Vector3(-90f, 0f, 0f),
        };
        root.AddChild(mesh);
        AddChild(root);
        _level100Facilities.Add(mesh);
    }

    private void BuildLevel100ObjectiveMarkers()
    {
        _targetZone1Marker = CreateObjectiveMarker(
            "TargetZone1Marker",
            SimulationConstants.Level100TargetZone1Position);
        _firingRangeMarker = CreateObjectiveMarker(
            "FiringRangeMarker",
            SimulationConstants.Level100FiringRangePosition);
    }

    private ObjectiveMarkerVisual CreateObjectiveMarker(string name, SimVector2 position)
    {
        var material = VisualPrimitives.CreateMaterial(
            new Color(MutedMarker, 0.20f),
            0f,
            0.48f,
            MutedMarker);
        var root = new Node3D
        {
            Name = name,
            Position = ToWorld(position, 0f),
        };
        MeshInstance3D area = VisualPrimitives.CreateCylinder(
            "TriggerArea",
            SimulationConstants.Level100ObjectiveTriggerRadius * UnitsToMeters,
            0.08f,
            new Vector3(0f, 0.04f, 0f),
            material);
        MeshInstance3D beacon = VisualPrimitives.CreateCylinder(
            "ObjectiveBeacon",
            0.10f,
            14f,
            new Vector3(0f, 7f, 0f),
            material);
        root.AddChild(area);
        root.AddChild(beacon);
        AddChild(root);
        var marker = new ObjectiveMarkerVisual(root, material);
        _level100ObjectiveMarkers.Add(marker);
        return marker;
    }

    private void BuildPlayer()
    {
        _playerRoot = new Node3D { Name = "PlayerVisual" };
        AddChild(_playerRoot);
        _playerBodyPivot = new Node3D { Name = "BodyPivot" };
        _playerRoot.AddChild(_playerBodyPivot);

        StandardMaterial3D cockpit = CreateRetailMaterial(
            CuratedAyaTextureLoader.Load("res://Assets/Aquila/Textures/cockpit.texture.aya", 512, 512),
            0.45f,
            0.42f);
        StandardMaterial3D textureA = CreateRetailMaterial(
            CuratedAyaTextureLoader.Load("res://Assets/Aquila/Textures/be-tex-a.texture.aya", 512, 512),
            0.45f,
            0.42f);
        StandardMaterial3D textureB = CreateRetailMaterial(
            CuratedAyaTextureLoader.Load("res://Assets/Aquila/Textures/be-tex-b.texture.aya", 1024, 1024),
            0.45f,
            0.42f);
        _walkerAsset = RetailAquilaWalkerAsset.Load(
            "res://Assets/Aquila/Source/m_f_be1.msh.aya",
            new Dictionary<int, Material>
            {
                [0] = cockpit,
                [1] = textureB,
                [3] = textureA,
            });
        Mesh jet = CuratedObjMeshLoader.Load(
            "res://Assets/Aquila/aquila-jet.obj",
            new Dictionary<string, Material>(StringComparer.Ordinal)
            {
                ["texture-0000"] = cockpit,
                ["texture-0002"] = textureB,
                ["texture-0004"] = textureA,
            });

        // The exact walker hierarchy performs BEA's X/Y/negative-Z-up mapping
        // per part. The still-static jet retains the reviewed OBJ conversion.
        _jetMesh = new MeshInstance3D
        {
            Name = "RetailAquilaJet",
            Mesh = jet,
            Position = new Vector3(0f, RetailJetBaseClearance, 0f),
            RotationDegrees = new Vector3(-90f, 0f, 0f),
            Visible = false,
        };
        _playerBodyPivot.AddChild(_walkerAsset.Root);
        _playerBodyPivot.AddChild(_jetMesh);
    }

    private static StandardMaterial3D CreateRetailMaterial(Texture2D texture, float metallic, float roughness)
    {
        return new StandardMaterial3D
        {
            AlbedoTexture = texture,
            Metallic = metallic,
            Roughness = roughness,
        };
    }

    private void BuildTargets(WorldSnapshot snapshot)
    {
        foreach (TargetSnapshot target in snapshot.Targets)
        {
            var material = VisualPrimitives.CreateMaterial(Amber, 0.38f, 0.42f, Amber);
            var root = new Node3D
            {
                Name = $"TargetVisual{target.Id}",
                Position = ToWorld(target.Position, 0f),
            };
            var baseMesh = VisualPrimitives.CreateCylinder("Base", 1.5f, 0.26f, new Vector3(0f, 0.13f, 0f), VisualPrimitives.CreateMaterial(SteelDark, 0.3f, 0.7f));
            var body = VisualPrimitives.CreateCylinder("Body", 0.72f, 2.8f, new Vector3(0f, 1.55f, 0f), material);
            var crossbar = VisualPrimitives.CreateBox("Crossbar", new Vector3(2.4f, 0.24f, 0.35f), new Vector3(0f, 2.55f, 0f), material);
            var beacon = VisualPrimitives.CreateSphere("Beacon", 0.38f, new Vector3(0f, 3.05f, 0f), material);
            var markerMaterial = VisualPrimitives.CreateMaterial(
                new Color(1f, 0.52f, 0.12f, 0.24f),
                0f,
                0.4f,
                new Color(1f, 0.38f, 0.06f));
            var marker = VisualPrimitives.CreateCylinder("Marker", 0.07f, 8f, new Vector3(0f, 7.2f, 0f), markerMaterial);
            root.AddChild(baseMesh);
            root.AddChild(body);
            root.AddChild(crossbar);
            root.AddChild(beacon);
            root.AddChild(marker);
            AddChild(root);
            _targets.Add(target.Id, new TargetVisual(root, body, crossbar, beacon, marker, material));
        }
    }

    private void BuildCamera()
    {
        _camera = new Camera3D
        {
            Name = "RetailFirstPersonCamera",
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
        var cockpitMaterial = new StandardMaterial3D
        {
            AlbedoTexture = cockpitTexture,
            ShadingMode = BaseMaterial3D.ShadingModeEnum.Unshaded,
            CullMode = BaseMaterial3D.CullModeEnum.Disabled,
            Roughness = 1f,
        };
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
        _cockpitMesh = new MeshInstance3D
        {
            Name = "RetailWalkerCockpit",
            Mesh = CuratedObjMeshLoader.Load(
                "res://Assets/Aquila/aquila-walker-cockpit.obj",
                new Dictionary<string, Material>(StringComparer.Ordinal)
                {
                    ["texture-0000"] = gunLightMaterial,
                    ["texture-0001"] = cockpitMaterial,
                }),
            Position = new Vector3(0f, -0.01f, -0.06f),
            RotationDegrees = new Vector3(-90f, 0f, 0f),
            CastShadow = GeometryInstance3D.ShadowCastingSetting.Off,
        };
        _camera.AddChild(_cockpitMesh);
    }

    private void UpdatePlayerShape(WorldSnapshot snapshot)
    {
        // Retail first person renders the authored internal cockpit instead of
        // the player's exterior vehicle mesh.
        _walkerAsset.Root.Visible = false;
        _jetMesh.Visible = false;

        float transitionLift = snapshot.Transition == VehicleTransition.WalkerToJet
            ? Mathf.Sin(_modeBlend * Mathf.Pi) * 0.28f
            : 0f;
        _playerBodyPivot.Position = new Vector3(0f, transitionLift, 0f);
    }

    private void UpdateWalkerPose(WorldSnapshot snapshot)
    {
        if (_lastWalkPoseTick != snapshot.Tick)
        {
            float velocityX = snapshot.PlayerVelocity.X * UnitsToMeters;
            float velocityZ = snapshot.PlayerVelocity.Z * UnitsToMeters;
            float yaw = snapshot.FacingYawMicroRad / 1_000_000f;
            float forwardSpeed = (velocityX * Mathf.Sin(yaw)) + (velocityZ * Mathf.Cos(yaw));
            float strafeSpeed = (velocityX * Mathf.Cos(yaw)) - (velocityZ * Mathf.Sin(yaw));
            float cycleStep = Math.Abs(forwardSpeed) > Math.Abs(strafeSpeed)
                ? forwardSpeed * 2.5f
                : strafeSpeed * 3f;
            int elapsedTicks = _lastWalkPoseTick < 0
                ? 0
                : Math.Max(1, snapshot.Tick - _lastWalkPoseTick);
            _walkCycle = Mathf.PosMod(_walkCycle + (cycleStep * elapsedTicks) + Mathf.Pi, Mathf.Tau) -
                Mathf.Pi;
            _lastWalkPoseTick = snapshot.Tick;
        }

        float speed = Mathf.Sqrt(
            (snapshot.PlayerVelocity.X * snapshot.PlayerVelocity.X) +
            (snapshot.PlayerVelocity.Z * snapshot.PlayerVelocity.Z));
        float movementWeight = snapshot.Mode == VehicleMode.Walker &&
            snapshot.Transition == VehicleTransition.None
            ? Mathf.Clamp(speed / SimulationConstants.WalkerMaximumSpeedPerTick, 0f, 1f)
            : 0f;
        _walkerAsset.SetWalkPose(_walkCycle, movementWeight);
    }

    private void UpdateLevel100ObjectiveMarkers(WorldSnapshot snapshot)
    {
        SetObjectiveMarkerState(
            _targetZone1Marker,
            snapshot.Level100Phase is Level100OpeningPhase.ReachTargetZone1 or
                Level100OpeningPhase.TargetZone1DispatchPending,
            snapshot.Level100Phase >= Level100OpeningPhase.ReachFiringRange);
        SetObjectiveMarkerState(
            _firingRangeMarker,
            snapshot.Level100Phase is Level100OpeningPhase.ReachFiringRange or
                Level100OpeningPhase.FiringRangeDispatchPending,
            snapshot.Level100Phase == Level100OpeningPhase.FiringRangeReached);
    }

    private static void SetObjectiveMarkerState(
        ObjectiveMarkerVisual marker,
        bool active,
        bool complete)
    {
        Color color = complete ? Green : active ? Cyan : MutedMarker;
        marker.Material.AlbedoColor = new Color(color, active ? 0.32f : 0.18f);
        marker.Material.Emission = color;
        marker.Material.EmissionEnergyMultiplier = active ? 3.0f : complete ? 1.5f : 0.6f;
        marker.Root.Visible = active || complete;
    }

    private void UpdateTargets(WorldSnapshot snapshot)
    {
        foreach (TargetSnapshot target in snapshot.Targets)
        {
            TargetVisual visual = _targets[target.Id];
            visual.Root.Position = ToWorld(target.Position, 0f);
            if (target.IsActive)
            {
                float health = (float)target.Hull / SimulationConstants.TargetHull;
                visual.Root.RotationDegrees = Vector3.Zero;
                visual.Body.Scale = new Vector3(0.8f + (health * 0.2f), Mathf.Max(0.2f, health), 0.8f + (health * 0.2f));
                visual.Body.Position = new Vector3(0f, 0.25f + (1.3f * health), 0f);
                visual.Crossbar.Visible = true;
                visual.Beacon.Visible = true;
                visual.Marker.Visible = true;
                visual.Material.AlbedoColor = Amber.Lerp(Green, 1f - health);
                visual.Material.Emission = visual.Material.AlbedoColor;
                visual.Material.EmissionEnergyMultiplier = 1.5f + (health * 1.2f);
            }
            else
            {
                visual.Root.RotationDegrees = new Vector3(0f, 0f, 67f);
                visual.Body.Scale = new Vector3(1f, 0.42f, 1f);
                visual.Body.Position = new Vector3(0f, 0.58f, 0f);
                visual.Crossbar.Visible = false;
                visual.Beacon.Visible = false;
                visual.Marker.Visible = false;
                visual.Material.AlbedoColor = Wreck;
                visual.Material.Emission = Colors.Black;
                visual.Material.EmissionEnergyMultiplier = 0f;
            }
        }
    }

    private void UpdateProjectiles(WorldSnapshot snapshot)
    {
        var activeIds = new HashSet<int>();
        foreach (ProjectileSnapshot projectile in snapshot.Projectiles)
        {
            activeIds.Add(projectile.Id);
            if (!_projectiles.TryGetValue(projectile.Id, out MeshInstance3D? visual))
            {
                visual = VisualPrimitives.CreateSphere(
                    $"ProjectileVisual{projectile.Id}",
                    0.21f,
                    Vector3.Zero,
                    VisualPrimitives.CreateMaterial(new Color(1f, 0.77f, 0.20f), 0f, 0.2f, new Color(1f, 0.48f, 0.08f)));
                AddChild(visual);
                _projectiles.Add(projectile.Id, visual);
            }

            visual.Position = ToWorld(projectile.Position, 1.25f);
        }

        foreach (int id in _projectiles.Keys.Where(id => !activeIds.Contains(id)).ToArray())
        {
            _projectiles[id].QueueFree();
            _projectiles.Remove(id);
        }
    }

    private void UpdateCamera(Vector3 playerGroundPosition, float yaw)
    {
        var forward = new Vector3(Mathf.Sin(yaw), 0f, Mathf.Cos(yaw));
        Vector3 centerOfGravity = playerGroundPosition +
            (Vector3.Up * RetailWalkerCenterOfGravityHeight);

        _camera.Position = centerOfGravity;
        _camera.LookAt(centerOfGravity + forward, Vector3.Up);
        _level100Sky.Position = _camera.Position;
    }

    private Vector3 ToWorld(SimVector2 position, float heightAboveTerrain)
    {
        float x = position.X * UnitsToMeters;
        float z = position.Z * UnitsToMeters;
        return new Vector3(
            x,
            _level100Terrain.SampleRelativeHeight(x, z) + heightAboveTerrain,
            z);
    }

    private sealed record TargetVisual(
        Node3D Root,
        MeshInstance3D Body,
        MeshInstance3D Crossbar,
        MeshInstance3D Beacon,
        MeshInstance3D Marker,
        StandardMaterial3D Material);

    private sealed record ObjectiveMarkerVisual(
        Node3D Root,
        StandardMaterial3D Material);
}
