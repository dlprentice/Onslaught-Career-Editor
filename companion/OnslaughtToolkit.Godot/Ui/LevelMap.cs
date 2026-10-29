// SPDX-License-Identifier: GPL-3.0-only
using System.Globalization;
using Godot;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// A top-down map of a level: its terrain as hill-shaded relief with X running right and Y running up, each placed object as a mark by
/// kind (changed ones in amber, the selected one ringed), and a readout of the world position and ground height under the pointer. The
/// wheel zooms about the pointer, dragging the background pans, a click on a mark selects it, and dragging a mark moves it: the mark
/// follows the pointer, Esc puts it back, and letting go asks for the move (one drag is one move, so one undo). Every conversion between
/// pixels and the world goes through <see cref="MapView"/>. The control draws and reports; it changes nothing itself.
/// </summary>
internal sealed partial class LevelMap : Control
{
    private const double ClickRadius = 12, DragThreshold = 4, StepPerWheelClick = 1.2, Rounding = 0.01;
    private readonly MapView _view = new();
    private ImageTexture? _relief;
    private Heightfield? _terrain;
    private IReadOnlyList<ObjectRow> _rows = [];
    private int? _selected, _hover;
    private (int Row, double X, double Y)? _drag;
    private int? _pressedRow;
    private Vector2 _pressedAt;
    private bool _panning;
    private Vector2 _pointer;
    private bool _pointerInside;

    internal LevelMap()
    {
        CustomMinimumSize = new Vector2(200, 200);
        ClipContents = true;
        FocusMode = FocusModeEnum.All;
        MouseFilter = MouseFilterEnum.Stop;
        MouseDefaultCursorShape = CursorShape.Cross;
        Resized += () =>
        {
            _view.Resize(Size.X, Size.Y);
            QueueRedraw();
        };
        MouseExited += () =>
        {
            _pointerInside = false;
            _hover = null;
            QueueRedraw();
        };
    }

    /// <summary>Raised when a click lands on a mark (the row's index).</summary>
    internal event Action<int>? RowPicked;

    /// <summary>Raised when a drag of a mark is let go: the row and the position to move it to (rounded to a hundredth of a unit).</summary>
    internal event Action<int, float, float>? MoveRequested;

    internal MapView View => _view;
    internal int? Selected => _selected;
    internal bool Dragging => _drag is not null;
    internal bool HasRelief => _relief is not null;

    /// <summary>The terrain to draw (null for none) and the objects to mark. The relief is built when the terrain changes.</summary>
    internal void SetLevel(Heightfield? terrain, IReadOnlyList<ObjectRow> rows)
    {
        if (!ReferenceEquals(terrain, _terrain))
        {
            _terrain = terrain;
            _relief = null;
            if (terrain is not null)
            {
                ReliefImage image = TerrainRelief.Build(terrain);
                _relief = ImageTexture.CreateFromImage(Image.CreateFromData(image.Width, image.Height, false, Image.Format.Rgba8, image.Rgba));
            }
            _view.Fit();
        }
        SetRows(rows);
    }

    /// <summary>The objects to mark (their positions may have changed).</summary>
    internal void SetRows(IReadOnlyList<ObjectRow> rows)
    {
        _rows = rows;
        if (_selected is int selected && rows.All(row => row.Index != selected)) _selected = null;
        QueueRedraw();
    }

    internal void Select(int? row)
    {
        _selected = row;
        QueueRedraw();
    }

    /// <summary>Back to the whole square.</summary>
    internal void FitToLevel()
    {
        _view.Fit();
        QueueRedraw();
    }

    internal void ZoomBy(double factor)
    {
        _view.ZoomAbout(Size.X / 2, Size.Y / 2, factor);
        QueueRedraw();
    }

    /// <summary>The pixel (in this control) that shows a world position.</summary>
    internal Vector2 ToScreen(double x, double y)
    {
        (double sx, double sy) = _view.ToScreen(x, y);
        return new Vector2((float)sx, (float)sy);
    }

    /// <summary>The row of the mark under a pixel, if a mark is within the click radius.</summary>
    internal int? RowAt(Vector2 position) => _view.Nearest(_rows.Select(row => (row.Index, (double)row.Position.X, (double)row.Position.Y)), position.X, position.Y, ClickRadius);

    /// <summary>Where a row's mark is drawn: the pointer's world position while it is being dragged, else its stored position.</summary>
    private (double X, double Y) MarkAt(ObjectRow row) => _drag is { } drag && drag.Row == row.Index ? (drag.X, drag.Y) : (row.Position.X, row.Position.Y);

    public override string _GetTooltip(Vector2 atPosition) =>
        RowAt(atPosition) is int row && _rows.FirstOrDefault(r => r.Index == row) is { } hit ? $"{hit.Label} (row {hit.Index}, {hit.Kind})" : "";

    public override void _GuiInput(InputEvent @event)
    {
        switch (@event)
        {
            case InputEventMouseButton { ButtonIndex: MouseButton.WheelUp, Pressed: true } up:
                Zoom(up.Position, StepPerWheelClick);
                break;
            case InputEventMouseButton { ButtonIndex: MouseButton.WheelDown, Pressed: true } down:
                Zoom(down.Position, 1 / StepPerWheelClick);
                break;
            case InputEventMouseButton { ButtonIndex: MouseButton.Middle or MouseButton.Right } button:
                _panning = button.Pressed;
                _pressedAt = button.Position;
                break;
            case InputEventMouseButton { ButtonIndex: MouseButton.Left } left:
                if (left.Pressed) Press(left.Position);
                else Release(left.Position);
                break;
            case InputEventMouseMotion motion:
                Move(motion);
                break;
            case InputEventKey { Pressed: true, Keycode: Key.Escape } when _drag is not null:
                _drag = null;
                _pressedRow = null;
                QueueRedraw();
                break;
            case InputEventKey { Pressed: true, Keycode: Key.Home }:
                FitToLevel();
                break;
            case InputEventKey { Pressed: true, Keycode: Key.Equal or Key.Plus or Key.KpAdd }:
                ZoomBy(StepPerWheelClick);
                break;
            case InputEventKey { Pressed: true, Keycode: Key.Minus or Key.KpSubtract }:
                ZoomBy(1 / StepPerWheelClick);
                break;
            default:
                return;
        }
        AcceptEvent();
    }

    private void Zoom(Vector2 about, double factor)
    {
        _view.ZoomAbout(about.X, about.Y, factor);
        QueueRedraw();
    }

    private void Press(Vector2 position)
    {
        GrabFocus();
        _pressedAt = position;
        _pressedRow = RowAt(position);
        if (_pressedRow is int row)
        {
            _selected = row;
            RowPicked?.Invoke(row);
        }
        else
        {
            _panning = true;  // the background drags the map
        }
        QueueRedraw();
    }

    private void Release(Vector2 position)
    {
        if (_drag is { } drag)
        {
            _drag = null;
            double x = Math.Round(drag.X / Rounding) * Rounding, y = Math.Round(drag.Y / Rounding) * Rounding;
            MoveRequested?.Invoke(drag.Row, (float)x, (float)y);
        }
        _pressedRow = null;
        _panning = false;
        QueueRedraw();
    }

    private void Move(InputEventMouseMotion motion)
    {
        _pointer = motion.Position;
        _pointerInside = true;
        if (_drag is { } drag)
        {
            (double x, double y) = _view.ToWorld(motion.Position.X, motion.Position.Y);
            _drag = (drag.Row, x, y);
        }
        else if (_pressedRow is int row && (motion.ButtonMask & MouseButtonMask.Left) != 0 && motion.Position.DistanceTo(_pressedAt) > DragThreshold)
        {
            (double x, double y) = _view.ToWorld(motion.Position.X, motion.Position.Y);
            _drag = (row, x, y);
        }
        else if (_panning && (motion.ButtonMask & (MouseButtonMask.Left | MouseButtonMask.Middle | MouseButtonMask.Right)) != 0)
        {
            _view.Pan(motion.Relative.X, motion.Relative.Y);
        }
        else
        {
            _hover = RowAt(motion.Position);
        }
        QueueRedraw();
    }

    public override void _Draw()
    {
        DrawRect(new Rect2(Vector2.Zero, Size), Palette.Field);
        (double left, double top) = _view.ToScreen(0, MapView.WorldSize);
        (double right, double bottom) = _view.ToScreen(MapView.WorldSize, 0);
        Rect2 square = new((float)left, (float)top, (float)(right - left), (float)(bottom - top));
        if (_relief is not null) DrawTextureRect(_relief, square, false);
        else DrawRect(square, Palette.Surface);
        DrawGrid();
        DrawRect(square, Palette.Border, false, 1.5f);
        if (_relief is null) DrawString(ThemeDB.FallbackFont, new Vector2(square.Position.X + 12, square.Position.Y + 24), "No terrain to draw for this level.", HorizontalAlignment.Left, -1, 13, Palette.Muted);

        foreach (ObjectRow row in _rows.OrderBy(Layer)) DrawMark(row, row.Index == _selected, row.Index == _hover || _drag?.Row == row.Index);
        DrawReadout();
    }

    /// <summary>Faint lines every 64 world units, with their numbers along the edges once there is room.</summary>
    private void DrawGrid()
    {
        if (_view.Scale * 64 < 28) return;
        Font font = ThemeDB.FallbackFont;
        Color line = new(1, 1, 1, 0.07f), text = new(Palette.Muted, 0.8f);
        for (int unit = 0; unit <= 512; unit += 64)
        {
            Vector2 a = ToScreen(unit, 0), b = ToScreen(unit, 512), c = ToScreen(0, unit), d = ToScreen(512, unit);
            DrawLine(a, b, line, 1f);
            DrawLine(c, d, line, 1f);
            if (_view.Scale * 64 < 40) continue;
            string label = unit.ToString(CultureInfo.InvariantCulture);
            if (a.X >= 0 && a.X < Size.X - 24) DrawString(font, new Vector2(a.X + 3, Math.Min(Size.Y - 4, a.Y - 3)), label, HorizontalAlignment.Left, -1, 10, text);
            if (c.Y >= 12 && c.Y < Size.Y) DrawString(font, new Vector2(Math.Max(3, c.X + 3), c.Y - 3), label, HorizontalAlignment.Left, -1, 10, text);
        }
    }

    private static int Layer(ObjectRow row) => row.Kind switch
    {
        "level-script" or "safe-side" or "cutscene" => 0,
        "sphere-trigger" => 1,
        "waypoint" => 2,
        "start" or "spawn-point" or "wingman-start" or "escape-pod" => 4,
        "unit" or "battle-engine" or "squad" or "animal" or "spawner" => 3,
        _ => 2,
    } + (row.Changed ? 10 : 0);

    private void DrawMark(ObjectRow row, bool selected, bool hot)
    {
        (double x, double y) = MarkAt(row);
        Vector2 at = ToScreen(x, y);
        if (at.X < -30 || at.Y < -30 || at.X > Size.X + 30 || at.Y > Size.Y + 30) return;
        Color colour = row.Changed || _drag?.Row == row.Index ? Palette.Accent : MarkColour(row.Kind);
        if (row.Changed && _drag is null)
        {
            // Where the level has it, and a line to where it stands now.
            Vector2 from = ToScreen(row.Stock.X, row.Stock.Y);
            DrawLine(from, at, new Color(Palette.Accent, 0.6f), 1.5f, true);
            DrawCircle(from, 3, new Color(Palette.Accent, 0.6f), false, 1.5f, true);
        }
        switch (row.Kind)
        {
            case "sphere-trigger":
                float radius = Math.Max((float)(row.Radius * _view.Scale), 3f);
                DrawCircle(at, radius, new Color(colour, 0.10f), true, -1, true);
                DrawCircle(at, radius, new Color(colour, 0.55f), false, 1.2f, true);
                DrawCircle(at, 2.2f, colour, true, -1, true);
                break;
            case "start" or "spawn-point" or "wingman-start" or "escape-pod":
                DrawColoredPolygon([at + new Vector2(0, -8), at + new Vector2(7, 0), at + new Vector2(0, 8), at + new Vector2(-7, 0)], colour);
                DrawPolyline([at + new Vector2(0, -8), at + new Vector2(7, 0), at + new Vector2(0, 8), at + new Vector2(-7, 0), at + new Vector2(0, -8)], Palette.Background, 1.5f, true);
                break;
            case "waypoint":
                DrawColoredPolygon([at + new Vector2(0, -4.5f), at + new Vector2(4.2f, 3f), at + new Vector2(-4.2f, 3f)], colour);
                break;
            case "unit" or "battle-engine" or "squad" or "animal" or "spawner":
                DrawCircle(at, 5.5f, Palette.Background, true, -1, true);
                DrawCircle(at, 4.2f, colour, true, -1, true);
                break;
            case "level-script" or "safe-side" or "cutscene":
                DrawCircle(at, 2.5f, colour, true, -1, true);
                break;
            default:
                DrawRect(new Rect2(at - new Vector2(4, 4), new Vector2(8, 8)), Palette.Background, true);
                DrawRect(new Rect2(at - new Vector2(3, 3), new Vector2(6, 6)), colour, true);
                break;
        }
        if (selected) DrawCircle(at, 11, Colors.White, false, 2f, true);
        if (selected || hot)
        {
            string text = row.Label + (_drag?.Row == row.Index ? $"  {CoordinateInput.Format((float)Math.Round(x / Rounding) * (float)Rounding)}, {CoordinateInput.Format((float)Math.Round(y / Rounding) * (float)Rounding)}" : "");
            DrawLabel(at + new Vector2(14, -10), text);
        }
    }

    private static Color MarkColour(string kind) => kind switch
    {
        "start" or "spawn-point" or "wingman-start" or "escape-pod" => Palette.Good,
        "unit" or "battle-engine" or "squad" or "animal" or "spawner" => Palette.Data,
        "waypoint" => new Color(Palette.Quote, 0.9f),
        "sphere-trigger" => Palette.Good,
        "level-script" or "safe-side" or "cutscene" => new Color(Palette.Muted, 0.7f),
        _ => new Color(Palette.Text, 0.85f),
    };

    private void DrawLabel(Vector2 at, string text)
    {
        Font font = ThemeDB.FallbackFont;
        Vector2 size = font.GetStringSize(text, HorizontalAlignment.Left, -1, 12);
        Vector2 origin = new(Math.Min(at.X, Size.X - size.X - 10), Math.Max(at.Y, size.Y + 4));
        DrawRect(new Rect2(origin - new Vector2(5, size.Y - 1), size + new Vector2(10, 7)), new Color(Palette.Background, 0.85f), true);
        DrawString(font, origin, text, HorizontalAlignment.Left, -1, 12, Palette.Text);
    }

    /// <summary>The world position under the pointer and the ground's height there, at the bottom left.</summary>
    private void DrawReadout()
    {
        if (!_pointerInside) return;
        (double x, double y) = _view.ToWorld(_pointer.X, _pointer.Y);
        string text = $"x {x:0.0}   y {y:0.0}";
        if (_terrain is not null && x is >= 0 and < MapView.WorldSize && y is >= 0 and < MapView.WorldSize)
            text += $"   ground {_terrain.HeightAt((float)x, (float)y):0.0}";
        Font font = ThemeDB.FallbackFont;
        Vector2 size = font.GetStringSize(text, HorizontalAlignment.Left, -1, 12);
        Vector2 origin = new(10, Size.Y - 10);
        DrawRect(new Rect2(origin - new Vector2(5, size.Y - 1), size + new Vector2(10, 7)), new Color(Palette.Background, 0.8f), true);
        DrawString(font, origin, text, HorizontalAlignment.Left, -1, 12, Palette.Muted);
    }
}
