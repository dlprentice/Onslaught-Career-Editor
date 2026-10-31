using System;
using Godot;

namespace OnslaughtToolkit.Companion.Ui;

// A terrain preview: editing and object selection stay in the existing map.
public partial class LevelTerrainViewport : SubViewportContainer
{
    internal Func<OnslaughtToolkit.Companion.Levels.Heightfield?>? TerrainProvider { get; set; }

    private readonly MeshInstance3D _mesh;
    private readonly Camera3D _camera;
    private readonly Label _help;
    private OnslaughtToolkit.Companion.Levels.Heightfield? _loaded;
    private Vector3 _target;
    private float _extent = 1f;
    private float _distance = 4f;
    private float _yaw = 0.8f;
    private float _pitch = 0.8f;
    private bool _dragging;

    public LevelTerrainViewport()
    {
        Stretch = true;
        MouseFilter = MouseFilterEnum.Stop;
        FocusMode = FocusModeEnum.All;
        var viewport = new SubViewport
        {
            OwnWorld3D = true,
            RenderTargetUpdateMode = SubViewport.UpdateMode.WhenVisible,
        };
        AddChild(viewport);
        var world = new Node3D();
        viewport.AddChild(world);
        _mesh = new MeshInstance3D();
        world.AddChild(_mesh);
        _camera = new Camera3D { Current = true, Fov = 50f };
        world.AddChild(_camera);
        world.AddChild(new DirectionalLight3D
        {
            RotationDegrees = new Vector3(-55f, -35f, 0f),
            LightEnergy = 1.2f,
        });
        _help = new Label
        {
            Text = "Load a level to preview its terrain.",
            MouseFilter = MouseFilterEnum.Ignore,
        };
        AddChild(_help);
    }

    public override void _Process(double delta)
    {
        if (!IsVisibleInTree()) return;
        var current = TerrainProvider?.Invoke();
        if (ReferenceEquals(current, _loaded)) return;
        _loaded = current;
        Rebuild(current);
    }

    public override void _GuiInput(InputEvent input)
    {
        if (input is InputEventMouseButton button)
        {
            if (button.ButtonIndex == MouseButton.Left)
            {
                _dragging = button.Pressed;
                if (button.Pressed) GrabFocus();
                AcceptEvent();
            }
            else if (button.Pressed && button.ButtonIndex == MouseButton.WheelUp)
            {
                Zoom(0.9f);
                AcceptEvent();
            }
            else if (button.Pressed && button.ButtonIndex == MouseButton.WheelDown)
            {
                Zoom(1.1f);
                AcceptEvent();
            }
        }
        else if (input is InputEventMouseMotion motion && _dragging)
        {
            Orbit(-motion.Relative.X * 0.008f, -motion.Relative.Y * 0.008f);
            AcceptEvent();
        }
        else if (input is InputEventKey key && key.Pressed && !key.Echo)
        {
            switch (key.Keycode)
            {
                case Key.Left: Orbit(0.1f, 0f); break;
                case Key.Right: Orbit(-0.1f, 0f); break;
                case Key.Up: Orbit(0f, 0.1f); break;
                case Key.Down: Orbit(0f, -0.1f); break;
                case Key.Pageup: Zoom(0.9f); break;
                case Key.Pagedown: Zoom(1.1f); break;
                default: return;
            }
            AcceptEvent();
        }
    }

    public override void _Notification(int what)
    {
        if (what == NotificationFocusExit || what == NotificationVisibilityChanged)
            _dragging = false;
    }

    private void Orbit(float yaw, float pitch)
    {
        _yaw += yaw;
        _pitch = Mathf.Clamp(_pitch + pitch, 0.12f, 1.45f);
        PositionCamera();
    }

    private void Zoom(float scale)
    {
        _distance = Mathf.Clamp(_distance * scale, Math.Max(_extent * 0.05f, 0.1f), Math.Max(_extent * 8f, 1f));
        PositionCamera();
    }

    private void PositionCamera()
    {
        float horizontal = Mathf.Cos(_pitch);
        var direction = new Vector3(horizontal * Mathf.Cos(_yaw), Mathf.Sin(_pitch), horizontal * Mathf.Sin(_yaw));
        _camera.Position = _target + direction * _distance;
        _camera.LookAt(_target, Vector3.Up);
    }

    private void Rebuild(OnslaughtToolkit.Companion.Levels.Heightfield? terrain)
    {
        _mesh.Mesh = null;
        if (terrain == null)
        {
            _help.Text = "Load a level to preview its terrain.";
            return;
        }
        try
        {
            var surface = OnslaughtToolkit.Companion.Levels.TerrainSurface.Build(terrain);
            var preview = OnslaughtToolkit.Companion.Levels.TerrainPreviewMesh.Build(surface.Vertices.Span, surface.Indices.Span);
            var vertices = new Vector3[preview.Vertices.Length];
            var normals = new Vector3[preview.Normals.Length];
            for (int i = 0; i < vertices.Length; i++)
            {
                var vertex = preview.Vertices[i];
                var normal = preview.Normals[i];
                vertices[i] = new Vector3(vertex.X, vertex.Y, vertex.Z);
                normals[i] = new Vector3(normal.X, normal.Y, normal.Z);
            }
            var arrays = new Godot.Collections.Array();
            arrays.Resize((int)Mesh.ArrayType.Max);
            arrays[(int)Mesh.ArrayType.Vertex] = vertices;
            arrays[(int)Mesh.ArrayType.Normal] = normals;
            arrays[(int)Mesh.ArrayType.Index] = preview.Indices;
            var mesh = new ArrayMesh();
            mesh.AddSurfaceFromArrays(Mesh.PrimitiveType.Triangles, arrays);
            _mesh.Mesh = mesh;
            _mesh.MaterialOverride = new StandardMaterial3D
            {
                AlbedoColor = new Color(0.38f, 0.46f, 0.31f),
                Roughness = 0.9f,
                CullMode = BaseMaterial3D.CullModeEnum.Disabled,
            };
            var min = preview.Min;
            var max = preview.Max;
            _target = new Vector3((min.X + max.X) * 0.5f, (min.Y + max.Y) * 0.5f, (min.Z + max.Z) * 0.5f);
            _extent = Math.Max(1f, Math.Max(max.X - min.X, Math.Max(max.Y - min.Y, max.Z - min.Z)));
            _distance = _extent * 1.5f;
            _camera.Near = Math.Max(0.05f, _extent / 10000f);
            _camera.Far = Math.Max(100f, _extent * 20f);
            PositionCamera();
            _help.Text = "Terrain preview: drag to orbit, wheel to zoom. Arrow and Page keys also work.";
        }
        catch (Exception error) when (error is ArgumentException or System.IO.InvalidDataException or OverflowException)
        {
            _help.Text = "The terrain could not be previewed.";
        }
    }
}
