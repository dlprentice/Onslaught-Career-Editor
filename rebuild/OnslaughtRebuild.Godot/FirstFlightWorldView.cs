// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

public sealed partial class FirstFlightWorldView : Node3D
{
    private const float UnitsToMeters = 0.001f;

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
    private MeshInstance3D _walkerMesh = null!;
    private MeshInstance3D _jetMesh = null!;
    private Level100HeightFieldAsset _level100Terrain = null!;
    private Camera3D _camera = null!;
    private ObjectiveMarkerVisual _targetZone1Marker = null!;
    private ObjectiveMarkerVisual _firingRangeMarker = null!;
    private bool _cameraInitialized;
    private float _modeBlend;

    public int TargetVisualCount => _targets.Count;

    public int ProjectileVisualCount => _projectiles.Count;

    public bool PlayerVisualPresent => IsInstanceValid(_playerRoot);

    public bool RetailAquilaMeshesPresent =>
        IsInstanceValid(_walkerMesh) &&
        IsInstanceValid(_jetMesh) &&
        _walkerMesh.Mesh?.GetSurfaceCount() > 0 &&
        _jetMesh.Mesh?.GetSurfaceCount() > 0;

    public int RetailAquilaSurfaceCount =>
        (_walkerMesh.Mesh?.GetSurfaceCount() ?? 0) +
        (_jetMesh.Mesh?.GetSurfaceCount() ?? 0);

    public int RetailLevel100FacilityCount => _level100Facilities.Count;

    public int Level100ObjectiveMarkerCount => _level100ObjectiveMarkers.Count;

    public int RetailLevel100TerrainVertexCount => _level100Terrain.VertexCount;

    public int RetailLevel100TerrainTriangleCount => _level100Terrain.TriangleCount;

    public void Initialize(WorldSnapshot snapshot)
    {
        Name = "WorldView";
        BuildEnvironment();
        BuildLevel100Terrain();
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
        Vector3 previousPosition = ToWorld(previous.PlayerPosition, 0.95f);
        Vector3 currentPosition = ToWorld(current.PlayerPosition, 0.95f);
        bool resetJump = previousPosition.DistanceSquaredTo(currentPosition) > 100f;
        Vector3 playerPosition = resetJump
            ? currentPosition
            : previousPosition.Lerp(currentPosition, interpolationAlpha);
        _playerRoot.Position = playerPosition;

        float previousYaw = previous.FacingYawMicroRad / 1_000_000f;
        float currentYaw = current.FacingYawMicroRad / 1_000_000f;
        _playerRoot.Rotation = new Vector3(
            0f,
            Mathf.LerpAngle(previousYaw, currentYaw, interpolationAlpha),
            0f);

        float desiredModeBlend = current.Transition == VehicleTransition.WalkerToJet
            ? 1f - (current.TransformTicksRemaining / (float)SimulationConstants.WalkerToJetTransitionTicks)
            : current.Mode == VehicleMode.Jet ? 1f : 0f;
        _modeBlend = current.Transition == VehicleTransition.WalkerToJet
            ? desiredModeBlend
            : Mathf.MoveToward(_modeBlend, desiredModeBlend, frameDelta * 8f);
        UpdatePlayerShape(current);
        UpdateLevel100ObjectiveMarkers(current);
        UpdateTargets(current);
        UpdateProjectiles(current);
        UpdateCamera(current, playerPosition, frameDelta);
    }

    private void BuildEnvironment()
    {
        var skyMaterial = new ProceduralSkyMaterial
        {
            SkyTopColor = new Color(0.025f, 0.055f, 0.075f),
            SkyHorizonColor = new Color(0.24f, 0.32f, 0.34f),
            GroundBottomColor = new Color(0.015f, 0.018f, 0.02f),
            GroundHorizonColor = new Color(0.18f, 0.20f, 0.18f),
        };
        var sky = new Sky { SkyMaterial = skyMaterial };
        var environment = new Godot.Environment
        {
            BackgroundMode = Godot.Environment.BGMode.Sky,
            Sky = sky,
            AmbientLightSource = Godot.Environment.AmbientSource.Color,
            AmbientLightColor = new Color(0.42f, 0.50f, 0.53f),
            AmbientLightEnergy = 0.65f,
            ReflectedLightSource = Godot.Environment.ReflectionSource.Sky,
            TonemapMode = Godot.Environment.ToneMapper.Filmic,
        };
        AddChild(new WorldEnvironment
        {
            Name = "WorldEnvironment",
            Environment = environment,
        });

        AddChild(new DirectionalLight3D
        {
            Name = "SunLight",
            RotationDegrees = new Vector3(-52f, -28f, 0f),
            LightColor = new Color(1f, 0.92f, 0.78f),
            LightEnergy = 1.15f,
            ShadowEnabled = true,
        });
    }

    private void BuildLevel100Terrain()
    {
        _level100Terrain = Level100HeightFieldAsset.Load(
            "res://Assets/Level100/Source/level100-heightfield.hfld.bin");
        var terrainMaterial = VisualPrimitives.CreateMaterial(
            new Color(0.16f, 0.22f, 0.20f),
            0.02f,
            0.96f);
        AddChild(new MeshInstance3D
        {
            Name = "RetailLevel100HeightField",
            Mesh = _level100Terrain.Mesh,
            MaterialOverride = terrainMaterial,
        });
    }

    private void BuildLevel100Facilities()
    {
        AddLevel100Facility(
            "RetailControlTower",
            "res://Assets/Level100/level100-control-tower.obj",
            new Vector2(-13.289886f, 5.603271f),
            0.0875791f,
            0f,
            new Color(0.42f, 0.53f, 0.56f));
        AddLevel100Facility(
            "RetailTankFactory",
            "res://Assets/Level100/level100-tank-factory.obj",
            new Vector2(10.125f, 22.375f),
            0.2383346f,
            1.7894337f,
            new Color(0.49f, 0.55f, 0.48f));
    }

    private void AddLevel100Facility(
        string name,
        string meshPath,
        Vector2 relativePosition,
        float meshBaseClearance,
        float retailYaw,
        Color color)
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
            Mesh = CuratedObjMeshLoader.Load(meshPath),
            RotationDegrees = new Vector3(-90f, 0f, 0f),
            MaterialOverride = VisualPrimitives.CreateMaterial(color, 0.28f, 0.72f),
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

        Mesh walker = CuratedObjMeshLoader.Load("res://Assets/Aquila/aquila-walker.obj");
        Mesh jet = CuratedObjMeshLoader.Load("res://Assets/Aquila/aquila-jet.obj");
        var material = VisualPrimitives.CreateMaterial(new Color(0.47f, 0.64f, 0.74f), 0.45f, 0.42f);

        _walkerMesh = new MeshInstance3D
        {
            Name = "RetailAquilaWalker",
            Mesh = walker,
            MaterialOverride = material,
            Position = new Vector3(0f, 1.99f, 0f),
            Scale = Vector3.One * 1.8f,
        };
        _jetMesh = new MeshInstance3D
        {
            Name = "RetailAquilaJet",
            Mesh = jet,
            MaterialOverride = material,
            Position = new Vector3(0f, 0.53f, 0f),
            RotationDegrees = new Vector3(-90f, 0f, 0f),
            Scale = Vector3.One * 2.2f,
            Visible = false,
        };
        _playerBodyPivot.AddChild(_walkerMesh);
        _playerBodyPivot.AddChild(_jetMesh);
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
            Name = "FollowCamera",
            Fov = 63f,
            Near = 0.1f,
            Far = 300f,
            Current = true,
        };
        AddChild(_camera);
    }

    private void UpdatePlayerShape(WorldSnapshot snapshot)
    {
        bool showJet = _modeBlend >= 0.5f;
        _walkerMesh.Visible = !showJet;
        _jetMesh.Visible = showJet;

        float transitionLift = snapshot.Transition == VehicleTransition.WalkerToJet
            ? Mathf.Sin(_modeBlend * Mathf.Pi) * 0.28f
            : 0f;
        _playerBodyPivot.Position = new Vector3(0f, transitionLift, 0f);
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

    private void UpdateCamera(WorldSnapshot snapshot, Vector3 playerPosition, float frameDelta)
    {
        float yaw = snapshot.FacingYawMicroRad / 1_000_000f;
        var forward = new Vector3(Mathf.Sin(yaw), 0f, Mathf.Cos(yaw));

        Vector3 focus = playerPosition + (forward * 5.5f) + new Vector3(0f, 1.2f, 0f);
        Vector3 desired = playerPosition - (forward * 14.5f) + new Vector3(0f, 7.0f, 0f);
        if (!_cameraInitialized)
        {
            _camera.Position = desired;
            _cameraInitialized = true;
        }
        else
        {
            float weight = 1f - Mathf.Exp(-frameDelta * 4.5f);
            _camera.Position = _camera.Position.Lerp(desired, weight);
        }

        _camera.LookAt(focus, Vector3.Up);
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
