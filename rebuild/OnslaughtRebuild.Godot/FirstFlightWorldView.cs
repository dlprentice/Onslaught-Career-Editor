// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

public sealed partial class FirstFlightWorldView : Node3D
{
    private const float UnitsToMeters = 0.001f;

    private static readonly Color Steel = new(0.20f, 0.27f, 0.30f);
    private static readonly Color SteelDark = new(0.075f, 0.105f, 0.115f);
    private static readonly Color Cyan = new(0.10f, 0.74f, 0.82f);
    private static readonly Color Amber = new(0.96f, 0.52f, 0.16f);
    private static readonly Color Green = new(0.30f, 0.70f, 0.39f);
    private static readonly Color Wreck = new(0.13f, 0.12f, 0.11f);

    private readonly Dictionary<int, TargetVisual> _targets = [];
    private readonly Dictionary<int, MeshInstance3D> _projectiles = [];
    private Node3D _playerRoot = null!;
    private Node3D _playerBodyPivot = null!;
    private MeshInstance3D? _leftLeg;
    private MeshInstance3D? _rightLeg;
    private MeshInstance3D? _leftWing;
    private MeshInstance3D? _rightWing;
    private MeshInstance3D? _leftEngine;
    private MeshInstance3D? _rightEngine;
    private StandardMaterial3D? _playerAccentMaterial;
    private Camera3D _camera = null!;
    private bool _cameraInitialized;
    private float _modeBlend;
    private bool _localPlayerVisual;
    private bool _localTerrainVisual;
    private LocalPresentationConfig? _localPresentation;

    public int TargetVisualCount => _targets.Count;

    public int ProjectileVisualCount => _projectiles.Count;

    public bool PlayerVisualPresent => IsInstanceValid(_playerRoot);

    public LocalPresentationLoadStatus LocalPresentationStatus => new(_localPlayerVisual, _localTerrainVisual);

    public void Initialize(WorldSnapshot snapshot, LocalPresentationConfig? localPresentation = null)
    {
        Name = "WorldView";
        _localPresentation = localPresentation;
        BuildEnvironment();
        BuildArena();
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

        float targetYaw = Mathf.Atan2(current.FacingX, current.FacingZ);
        _playerRoot.Rotation = new Vector3(
            0f,
            Mathf.LerpAngle(_playerRoot.Rotation.Y, targetYaw, Mathf.Clamp(frameDelta * 12f, 0f, 1f)),
            0f);

        float desiredModeBlend = current.Mode == VehicleMode.Jet ? 1f : 0f;
        float blendRate = current.TransformTicksRemaining > 0 ? 3.5f : 8f;
        _modeBlend = Mathf.MoveToward(_modeBlend, desiredModeBlend, frameDelta * blendRate);
        UpdatePlayerShape(current, frameDelta);
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

    private void BuildArena()
    {
        if (_localPresentation?.HasTerrainMesh == true &&
            _localPresentation.Terrain is not null &&
            _localPresentation.TerrainMeshPath is not null)
        {
            Node3D? terrain = LocalAssetMeshLoader.TryLoadMeshNode(
                _localPresentation.TerrainMeshPath,
                _localPresentation.Terrain,
                "LocalTerrain");
            if (terrain is not null)
            {
                AddChild(terrain);
                _localTerrainVisual = true;
                BuildArenaBoundariesOnly();
                return;
            }
        }

        BuildArenaSynthetic();
    }

    private void BuildArenaSynthetic()
    {
        var groundMaterial = VisualPrimitives.CreateMaterial(new Color(0.075f, 0.105f, 0.095f), 0.05f, 0.92f);
        AddChild(new MeshInstance3D
        {
            Name = "ArenaGround",
            Mesh = new PlaneMesh { Size = new Vector2(68f, 68f) },
            MaterialOverride = groundMaterial,
        });

        var gridMaterial = VisualPrimitives.CreateMaterial(new Color(0.20f, 0.29f, 0.27f, 0.58f), 0f, 1f);
        for (int coordinate = -30; coordinate <= 30; coordinate += 5)
        {
            AddChild(VisualPrimitives.CreateBox(
                $"GridX{coordinate}",
                new Vector3(0.035f, 0.025f, 60f),
                new Vector3(coordinate, 0.018f, 0f),
                gridMaterial));
            AddChild(VisualPrimitives.CreateBox(
                $"GridZ{coordinate}",
                new Vector3(60f, 0.025f, 0.035f),
                new Vector3(0f, 0.018f, coordinate),
                gridMaterial));
        }

        BuildArenaBoundariesOnly();

        var structureMaterial = VisualPrimitives.CreateMaterial(SteelDark, 0.25f, 0.78f);
        AddChild(VisualPrimitives.CreateBox("WestRelay", new Vector3(3.5f, 5f, 3.5f), new Vector3(-26f, 2.5f, 20f), structureMaterial));
        AddChild(VisualPrimitives.CreateBox("EastRelay", new Vector3(4f, 7f, 3f), new Vector3(25f, 3.5f, 16f), structureMaterial));
        AddChild(VisualPrimitives.CreateBox("SouthBlock", new Vector3(8f, 2.8f, 3f), new Vector3(19f, 1.4f, -25f), structureMaterial));
        AddChild(VisualPrimitives.CreateBox("NorthBlock", new Vector3(6f, 2.2f, 4f), new Vector3(-17f, 1.1f, 26f), structureMaterial));
    }

    private void BuildArenaBoundariesOnly()
    {
        var boundaryMaterial = VisualPrimitives.CreateMaterial(
            new Color(0.78f, 0.30f, 0.08f),
            0.15f,
            0.5f,
            new Color(0.80f, 0.21f, 0.04f));
        AddChild(VisualPrimitives.CreateBox("NorthBoundary", new Vector3(62f, 0.16f, 0.18f), new Vector3(0f, 0.08f, 30.6f), boundaryMaterial));
        AddChild(VisualPrimitives.CreateBox("SouthBoundary", new Vector3(62f, 0.16f, 0.18f), new Vector3(0f, 0.08f, -30.6f), boundaryMaterial));
        AddChild(VisualPrimitives.CreateBox("EastBoundary", new Vector3(0.18f, 0.16f, 62f), new Vector3(30.6f, 0.08f, 0f), boundaryMaterial));
        AddChild(VisualPrimitives.CreateBox("WestBoundary", new Vector3(0.18f, 0.16f, 62f), new Vector3(-30.6f, 0.08f, 0f), boundaryMaterial));
    }

    private void BuildPlayer()
    {
        _playerRoot = new Node3D { Name = "PlayerVisual" };
        AddChild(_playerRoot);
        _playerBodyPivot = new Node3D { Name = "BodyPivot" };
        _playerRoot.AddChild(_playerBodyPivot);

        if (_localPresentation?.HasPlayerMesh == true &&
            _localPresentation.Player is not null)
        {
            Node3D? localPlayer = LocalAssetMeshLoader.TryLoadMeshNode(
                _localPresentation.PlayerMeshPath,
                _localPresentation.Player,
                "LocalAquila");
            if (localPlayer is not null)
            {
                _playerBodyPivot.AddChild(localPlayer);
                _localPlayerVisual = true;
                return;
            }
        }

        BuildPlayerSynthetic();
    }

    private void BuildPlayerSynthetic()
    {
        var bodyMaterial = VisualPrimitives.CreateMaterial(Steel, 0.55f, 0.36f);
        var darkMaterial = VisualPrimitives.CreateMaterial(SteelDark, 0.35f, 0.55f);
        _playerAccentMaterial = VisualPrimitives.CreateMaterial(Cyan, 0.35f, 0.32f, Cyan);

        _playerBodyPivot.AddChild(VisualPrimitives.CreateBox("MainHull", new Vector3(2.3f, 0.85f, 3.1f), new Vector3(0f, 1.55f, 0f), bodyMaterial));
        _playerBodyPivot.AddChild(VisualPrimitives.CreateBox("Nose", new Vector3(1.35f, 0.5f, 1.2f), new Vector3(0f, 1.62f, 1.85f), _playerAccentMaterial));
        _playerBodyPivot.AddChild(VisualPrimitives.CreateSphere("Cockpit", 0.58f, new Vector3(0f, 2.12f, 0.35f), darkMaterial));

        _leftWing = VisualPrimitives.CreateBox("LeftWing", new Vector3(2.7f, 0.16f, 1.55f), new Vector3(-2.05f, 1.62f, -0.25f), bodyMaterial, new Vector3(0f, 0f, -8f));
        _rightWing = VisualPrimitives.CreateBox("RightWing", new Vector3(2.7f, 0.16f, 1.55f), new Vector3(2.05f, 1.62f, -0.25f), bodyMaterial, new Vector3(0f, 0f, 8f));
        _playerBodyPivot.AddChild(_leftWing);
        _playerBodyPivot.AddChild(_rightWing);

        _leftLeg = VisualPrimitives.CreateBox("LeftLeg", new Vector3(0.55f, 1.7f, 0.72f), new Vector3(-0.72f, 0.45f, -0.25f), darkMaterial);
        _rightLeg = VisualPrimitives.CreateBox("RightLeg", new Vector3(0.55f, 1.7f, 0.72f), new Vector3(0.72f, 0.45f, -0.25f), darkMaterial);
        _playerRoot.AddChild(_leftLeg);
        _playerRoot.AddChild(_rightLeg);

        _leftEngine = VisualPrimitives.CreateCylinder("LeftEngine", 0.26f, 0.85f, new Vector3(-0.78f, 1.55f, -1.85f), _playerAccentMaterial, new Vector3(90f, 0f, 0f));
        _rightEngine = VisualPrimitives.CreateCylinder("RightEngine", 0.26f, 0.85f, new Vector3(0.78f, 1.55f, -1.85f), _playerAccentMaterial, new Vector3(90f, 0f, 0f));
        _playerBodyPivot.AddChild(_leftEngine);
        _playerBodyPivot.AddChild(_rightEngine);
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
            Far = 180f,
            Current = true,
        };
        AddChild(_camera);
    }

    private void UpdatePlayerShape(WorldSnapshot snapshot, float frameDelta)
    {
        if (_localPlayerVisual ||
            _leftLeg is null ||
            _rightLeg is null ||
            _leftWing is null ||
            _rightWing is null ||
            _leftEngine is null ||
            _rightEngine is null ||
            _playerAccentMaterial is null)
        {
            return;
        }

        _leftLeg.Position = new Vector3(-0.72f - (_modeBlend * 0.35f), 0.45f + (_modeBlend * 0.72f), -0.25f - (_modeBlend * 0.78f));
        _rightLeg.Position = new Vector3(0.72f + (_modeBlend * 0.35f), 0.45f + (_modeBlend * 0.72f), -0.25f - (_modeBlend * 0.78f));
        _leftLeg.RotationDegrees = new Vector3(_modeBlend * 72f, 0f, _modeBlend * -18f);
        _rightLeg.RotationDegrees = new Vector3(_modeBlend * 72f, 0f, _modeBlend * 18f);
        _leftWing.Position = new Vector3(-2.05f - (_modeBlend * 0.5f), 1.62f, -0.25f);
        _rightWing.Position = new Vector3(2.05f + (_modeBlend * 0.5f), 1.62f, -0.25f);
        _playerBodyPivot.RotationDegrees = new Vector3(_modeBlend * -10f, 0f, 0f);

        float speed = snapshot.PlayerVelocity.X != 0 || snapshot.PlayerVelocity.Z != 0 ? 1f : 0f;
        float engineScale = 0.75f + (_modeBlend * 0.7f) + (speed * 0.28f);
        _leftEngine.Scale = new Vector3(engineScale, engineScale, engineScale);
        _rightEngine.Scale = _leftEngine.Scale;
        float pulse = snapshot.TransformTicksRemaining > 0
            ? 2.4f + (Mathf.Sin(snapshot.Tick * 0.9f) * 0.8f)
            : 1.8f + (_modeBlend * 1.4f);
        _playerAccentMaterial.EmissionEnergyMultiplier = Mathf.MoveToward(
            _playerAccentMaterial.EmissionEnergyMultiplier,
            pulse,
            frameDelta * 8f);
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
        TargetSnapshot? nearestTarget = snapshot.Targets
            .Where(target => target.IsActive)
            .OrderBy(target =>
            {
                Vector3 position = ToWorld(target.Position, 0f);
                return position.DistanceSquaredTo(playerPosition);
            })
            .FirstOrDefault();
        Vector3 focus = nearestTarget is null
            ? playerPosition
            : playerPosition.Lerp(ToWorld(nearestTarget.Position, 0.9f), 0.36f);
        Vector3 desired = focus + new Vector3(0f, 31f, -25f);
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

        _camera.LookAt(focus + new Vector3(0f, 0.9f, 1.5f), Vector3.Up);
    }

    private static Vector3 ToWorld(SimVector2 position, float height)
    {
        return new Vector3(position.X * UnitsToMeters, height, position.Z * UnitsToMeters);
    }

    private sealed record TargetVisual(
        Node3D Root,
        MeshInstance3D Body,
        MeshInstance3D Crossbar,
        MeshInstance3D Beacon,
        MeshInstance3D Marker,
        StandardMaterial3D Material);
}

public readonly record struct LocalPresentationLoadStatus(bool PlayerLoaded, bool TerrainLoaded)
{
    public bool AnyLoaded => PlayerLoaded || TerrainLoaded;
}
