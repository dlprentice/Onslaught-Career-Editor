using System;
using Godot;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Ui;

// A sampled terrain view. Its host owns selection and applies move requests through the shared edit session.
public partial class LevelTerrainViewport : SubViewportContainer
{
    internal Func<Heightfield?>? TerrainProvider { get; set; }
    internal Func<IReadOnlyList<ObjectRow>>? RowsProvider { get; set; }
    internal Func<int?>? SelectedRowProvider { get; set; }
    internal event Action<int>? RowPicked;
    internal event Action<int, float, float>? MoveRequested;

    private readonly MeshInstance3D _mesh;
    private readonly Camera3D _camera;
    private readonly Label _help;
    private readonly MarkerOverlay _marks;
    private Heightfield? _loaded;
    private TerrainSurface? _surface;
    private IReadOnlyList<ObjectRow> _rows = Array.Empty<ObjectRow>();
    private int? _selected;
    private Vector3 _target;
    private float _extent = 1f;
    private float _radius;
    private float _fitDistance;
    private float _distance = 4f;
    private float _yaw = 0.8f;
    private float _pitch = 0.8f;
    private bool _dragging;
    private bool _leftPressed;
    private Vector2 _pressedAt;

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
        _marks = new MarkerOverlay(this) { MouseFilter = MouseFilterEnum.Ignore };
        AddChild(_marks);
        _marks.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        _help = new Label
        {
            Text = "Load a level to preview its terrain.",
            MouseFilter = MouseFilterEnum.Ignore,
            AutowrapMode = TextServer.AutowrapMode.WordSmart,
        };
        AddChild(_help);
        _help.SetAnchorsAndOffsetsPreset(LayoutPreset.TopWide);
        _help.OffsetLeft = 8;
        _help.OffsetTop = 8;
        _help.OffsetRight = -8;
        _help.OffsetBottom = 64;
    }

    public override void _Process(double delta)
    {
        if (!IsVisibleInTree()) return;
        var current = TerrainProvider?.Invoke();
        if (!ReferenceEquals(current, _loaded))
        {
            _loaded = current;
            Rebuild(current);
        }
        RefreshRows();
    }

    private void RefreshRows()
    {
        var rows = RowsProvider?.Invoke() ?? Array.Empty<ObjectRow>();
        int? selected = SelectedRowProvider?.Invoke();
        if (!ReferenceEquals(rows, _rows) || selected != _selected)
        {
            _rows = rows;
            _selected = selected;
            _marks.QueueRedraw();
        }
    }

    public override void _GuiInput(InputEvent input)
    {
        if (input is InputEventMouseButton button)
        {
            // A selection can change between input events, before the next frame is drawn.
            RefreshRows();
            if (button.ButtonIndex == MouseButton.Left)
            {
                if (button.Pressed)
                {
                    _leftPressed = true;
                    _dragging = false;
                    _pressedAt = button.Position;
                    GrabFocus();
                }
                else
                {
                    if (_leftPressed && !_dragging && RowAt(button.Position) is { } row)
                        RowPicked?.Invoke(row.Index);
                    _leftPressed = _dragging = false;
                }
                AcceptEvent();
            }
            else if (button.Pressed && button.ButtonIndex == MouseButton.Right)
            {
                RequestMove(button.Position);
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
        else if (input is InputEventMouseMotion motion && _leftPressed)
        {
            if (_dragging || motion.Position.DistanceTo(_pressedAt) > 4f)
            {
                _dragging = true;
                Orbit(-motion.Relative.X * 0.008f, -motion.Relative.Y * 0.008f);
            }
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
        if (what == NotificationResized)
        {
            ReframeOnResize();
            _marks?.QueueRedraw();
        }
        if (what == NotificationFocusExit || what == NotificationVisibilityChanged)
            _leftPressed = _dragging = false;
    }

    private void Orbit(float yaw, float pitch)
    {
        _yaw += yaw;
        _pitch = Mathf.Clamp(_pitch + pitch, 0.12f, 1.45f);
        PositionCamera();
    }


    private float FitDistance()
    {
        double width = System.Math.Max(1.0, Size.X);
        double height = System.Math.Max(1.0, Size.Y);
        double verticalHalf = _camera.Fov * System.Math.PI / 360.0;
        double horizontalHalf = System.Math.Atan(System.Math.Tan(verticalHalf) * width / height);
        double halfAngle = System.Math.Max(0.000001, System.Math.Min(verticalHalf, horizontalHalf));
        double distance = 1.1 * _radius / System.Math.Sin(halfAngle);
        return (float)System.Math.Min(distance, float.MaxValue / 8.0);
    }

    private void ReframeOnResize()
    {
        if (_radius <= 0f || _fitDistance <= 0f)
            return;
        float zoomRatio = _distance / _fitDistance;
        _fitDistance = FitDistance();
        _distance = _fitDistance * zoomRatio;
        PositionCamera();
    }

    private void UpdateClipPlanes()
    {
        float near = Mathf.Max(0.0001f, _radius * 0.001f);
        if (_distance > _radius)
            near = Mathf.Min(near, (_distance - _radius) * 0.5f);
        _camera.Near = Mathf.Max(0.0001f, near);
        _camera.Far = Mathf.Max(_camera.Near + 1f, _distance + _radius * 1.1f + 1f);
    }

    private void Zoom(float scale)
    {
        _distance = Mathf.Clamp(_distance * scale, Math.Max(_extent * 0.05f, 0.1f), Mathf.Max(Math.Max(_extent * 8f, 1f), _fitDistance * 4f));
        PositionCamera();
    }

    private void PositionCamera()
    {
        if (_radius > 0f)
            UpdateClipPlanes();
        float horizontal = Mathf.Cos(_pitch);
        var direction = new Vector3(horizontal * Mathf.Cos(_yaw), Mathf.Sin(_pitch), horizontal * Mathf.Sin(_yaw));
        _camera.Position = _target + direction * _distance;
        _camera.LookAt(_target, Vector3.Up);
        _marks.QueueRedraw();
    }

    private void Rebuild(Heightfield? terrain)
    {
        _mesh.Mesh = null;
        _surface = null;
        _marks.QueueRedraw();
        if (terrain == null)
        {
            _help.Text = "Load a level to preview its terrain.";
            return;
        }
        try
        {
            var surface = TerrainSurface.Build(terrain);
            var preview = TerrainPreviewMesh.Build(surface.Vertices.Span, surface.Indices.Span);
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
            _radius = (preview.Max - preview.Min).Length() * 0.5f;
            if (!float.IsFinite(_radius))
                throw new System.IO.InvalidDataException("Terrain bounds cannot be framed.");
            _radius = Mathf.Max(_radius, 0.0001f);
            _fitDistance = FitDistance();
            _distance = _fitDistance;
            PositionCamera();
            _surface = surface;
            _help.Text = "Click to select · right-click to move (height unchanged) · drag to orbit · wheel to zoom";
        }
        catch (Exception error) when (error is ArgumentException or System.IO.InvalidDataException or OverflowException)
        {
            _mesh.Mesh = null;
            _help.Text = "The terrain could not be previewed.";
        }
    }

    private void RequestMove(Vector2 at)
    {
        if (_selected is not int selected || _surface is null || MoveRequested is null ||
            !_rows.Any(row => row.Index == selected)) return;
        Vector3 origin = _camera.ProjectRayOrigin(at), direction = _camera.ProjectRayNormal(at);
        var start = new System.Numerics.Vector3(origin.X, origin.Y, origin.Z);
        var ray = new System.Numerics.Vector3(direction.X, direction.Y, direction.Z);
        if (TerrainRayPicker.TryHit(_surface, start, ray, out var hit))
        {
            // Rounding a hit at the last edge to 512 would put it outside the ground lookup.
            double x = Math.Clamp((double)hit.X, 0, Heightfield.Size - 0.01);
            double y = Math.Clamp(-(double)hit.Z, 0, Heightfield.Size - 0.01);
            MoveRequested.Invoke(selected, MapView.ToHundredths(x), MapView.ToHundredths(y));
        }
    }

    public override string _GetTooltip(Vector2 atPosition)
    {
        RefreshRows();
        return RowAt(atPosition) is { } row ? $"{row.Label} (row {row.Index}, {row.Kind})" : "";
    }

    private ObjectRow? RowAt(Vector2 at)
    {
        ObjectRow? nearest = null;
        float bestDistance = 12f * 12f, bestDepth = float.PositiveInfinity;
        foreach (var row in _rows)
        {
            if (!TryProject(row, out Vector2 screen, out float depth)) continue;
            float distance = at.DistanceSquaredTo(screen);
            if (distance < bestDistance || (distance == bestDistance && depth < bestDepth))
            {
                nearest = row;
                bestDistance = distance;
                bestDepth = depth;
            }
        }
        return nearest;
    }

    private bool TryProject(ObjectRow row, out Vector2 screen, out float depth)
    {
        screen = default;
        depth = 0;
        if (_surface is null || !IsInsideTree()) return false;
        // Screen-space editor marks intentionally remain visible through the terrain.
        var p = row.Position;
        if (!float.IsFinite(p.X) || !float.IsFinite(p.Y) || !float.IsFinite(p.Z)) return false;
        var point = new Vector3(p.X, -p.Z, -p.Y);
        depth = -(_camera.GlobalTransform.AffineInverse() * point).Z;
        if (!float.IsFinite(depth) || depth < _camera.Near || depth > _camera.Far || _camera.IsPositionBehind(point)) return false;
        screen = _camera.UnprojectPosition(point);
        return float.IsFinite(screen.X) && float.IsFinite(screen.Y) && screen.X >= 0 && screen.Y >= 0 && screen.X < Size.X && screen.Y < Size.Y;
    }

    private sealed partial class MarkerOverlay(LevelTerrainViewport owner) : Control
    {
        public override void _Draw()
        {
            foreach (var row in owner._rows)
            {
                if (!owner.TryProject(row, out Vector2 at, out _)) continue;
                bool selected = row.Index == owner._selected;
                DrawCircle(at, 6f, new Color(0.04f, 0.06f, 0.08f, 0.9f), true, -1, true);
                DrawCircle(at, 4f, selected ? new Color(1f, 0.8f, 0.3f) : new Color(0.36f, 0.8f, 0.95f), true, -1, true);
            }
            var selectedRow = owner._rows.FirstOrDefault(row => row.Index == owner._selected);
            if (selectedRow is not null && owner.TryProject(selectedRow, out Vector2 selectedAt, out _))
                DrawCircle(selectedAt, 10f, Colors.White, false, 2f, true);
        }
    }
}
