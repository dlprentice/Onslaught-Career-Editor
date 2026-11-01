// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Headless geometry checks on the authored terrain fixture; no retail data or rendered-image assertion.</summary>
internal static class TerrainViewportProjectionTests
{
    internal static async Task RunAsync(SceneTree tree, Checks check)
    {
        check.Suite("3D terrain preview framing");
        Heightfield terrain = Heightfield.Read(LevelTests.Unpack(LevelVectors.Terrain.Eres));
        TerrainSurface surface = TerrainSurface.Build(terrain);
        var vertices = surface.Vertices.ToArray();
        var view = new LevelTerrainViewport { TerrainProvider = () => terrain, Size = new Vector2(580, 480) };
        // The root may still be adding the test runner; wait before attaching a sibling.
        await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        tree.Root.AddChild(view);
        try
        {
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            Camera3D? camera = FindCamera(view);
            Viewport? cameraViewport = camera?.GetViewport();
            check.That(cameraViewport is not null && cameraViewport.GetCamera3D() == camera,
                "The authored terrain preview has an active camera.");
            if (camera is null || cameraViewport is null) return;
            check.That(camera.GetViewport().GetVisibleRect().Size.X == 580, "3D terrain starts at the requested width");
            check.That(AllInside(camera, vertices), "The initial camera frames every authored terrain vertex.");
            var mouse = view.GlobalPosition + new Vector2(60, 60);
            var beforeOrbit = camera.GlobalPosition;
            view.GetViewport().PushInput(new InputEventMouseButton { Position = mouse, GlobalPosition = mouse, ButtonIndex = MouseButton.Left, Pressed = true });
            var movedMouse = mouse + new Vector2(36, 18);
            view.GetViewport().PushInput(new InputEventMouseMotion { Position = movedMouse, GlobalPosition = movedMouse, Relative = new Vector2(36, 18), ButtonMask = MouseButtonMask.Left });
            view.GetViewport().PushInput(new InputEventMouseButton { Position = movedMouse, GlobalPosition = movedMouse, ButtonIndex = MouseButton.Left, Pressed = false });
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            check.That(camera.GlobalPosition.DistanceTo(beforeOrbit) > 0.001f, "3D terrain drag orbits the camera");
            check.That(AllInside(camera, vertices), "3D terrain stays framed after orbit");

            // Connect a synthetic edit session just as the page will: a view requests a move; the host owns the edit and undo.
            var edit = new EditSession(LevelTests.Body("authored-v50"));
            var anchor = new System.Numerics.Vector3(256, 256, terrain.HeightAt(256, 256));
            check.That(edit.TryApply(new MoveObject(0, anchor), out _), "The synthetic 3D move starts with a movable object");
            ObjectRow marker = new(0, "unit", "Test object", "", anchor, anchor);
            IReadOnlyList<ObjectRow> rows = [marker];
            int? selected = null;
            int moveRequests = 0;
            view.RowsProvider = () => rows;
            view.SelectedRowProvider = () => selected;
            view.RowPicked += row => selected = row;
            view.MoveRequested += (row, x, y) =>
            {
                moveRequests++;
                var before = edit.Body.Things[row].Init.Position;
                if (edit.TryApply(new MoveObject(row, new System.Numerics.Vector3(x, y, before.Z)), out _))
                    rows = [marker with { Position = edit.Body.Things[row].Init.Position }];
            };
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            Vector2 targetScreen = camera.UnprojectPosition(new Vector3(320, -terrain.HeightAt(320, 200), -200));
            Click(view, targetScreen, MouseButton.Right);
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            check.That(moveRequests == 0 && edit.Body.Things[0].Init.Position == anchor,
                "Right-clicking terrain without a selected object changes nothing");
            Vector2 markAt = camera.UnprojectPosition(new Vector3(anchor.X, -anchor.Z, -anchor.Y));
            check.That(view._GetTooltip(markAt).Contains("Test object"), "Hovering a 3D mark identifies its object");
            Click(view, markAt, MouseButton.Left);
            Click(view, targetScreen, MouseButton.Right);
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            check.That(selected == 0, "Clicking a visible 3D mark selects its object");
            var moved = edit.Body.Things[0].Init.Position;
            check.That(moveRequests == 1 && moved != anchor &&
                BitConverter.SingleToInt32Bits(moved.Z) == BitConverter.SingleToInt32Bits(anchor.Z),
                "Immediately right-clicking terrain requests one move for the newly selected object and preserves its height");
            check.That(Math.Abs(moved.X - 320) < 2 && Math.Abs(moved.Y - 200) < 2,
                $"3D placement maps the visible point back to world X/Y (got {moved.X}, {moved.Y})");
            check.That(edit.Undo() && edit.Body.Things[0].Init.Position == anchor &&
                edit.Redo() && edit.Body.Things[0].Init.Position == moved,
                "The requested 3D move can be undone and redone through the shared edit session");
            selected = 999;
            Click(view, targetScreen, MouseButton.Right);
            check.That(moveRequests == 1, "A selection that no longer names an object cannot move a stale row");

            view.Size = new Vector2(240, 480);
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            check.That(AllInside(camera, vertices), "The camera still frames the authored terrain after a narrow resize.");
            check.That(camera.GetViewport().GetVisibleRect().Size.X == 240, "3D terrain uses the narrow width");
            var min = vertices[0];
            var max = vertices[0];
            foreach (var vertex in vertices)
            {
                min = System.Numerics.Vector3.Min(min, vertex);
                max = System.Numerics.Vector3.Max(max, vertex);
            }
            var target = new Godot.Vector3((min.X + max.X) * 0.5f, (min.Y + max.Y) * 0.5f, (min.Z + max.Z) * 0.5f);
            var narrowFit = camera.GlobalPosition.DistanceTo(target);
            view.Size = new Vector2(580, 480);
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            var wideFit = camera.GlobalPosition.DistanceTo(target);
            view.GetViewport().PushInput(new InputEventMouseButton { Position = mouse, GlobalPosition = mouse, ButtonIndex = MouseButton.WheelDown, Pressed = true });
            view.GetViewport().PushInput(new InputEventMouseButton { Position = mouse, GlobalPosition = mouse, ButtonIndex = MouseButton.WheelDown, Pressed = false });
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            var wideZoom = camera.GlobalPosition.DistanceTo(target);
            check.That(wideZoom > wideFit, "3D terrain wheel zoom moves the camera outward");
            view.Size = new Vector2(240, 480);
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            var narrowZoom = camera.GlobalPosition.DistanceTo(target);
            check.That(wideFit > 0 && narrowFit > 0 && Mathf.Abs(wideZoom / wideFit - narrowZoom / narrowFit) < 0.005f, "3D terrain resize preserves the zoom ratio");
            check.That(AllInside(camera, vertices), "3D terrain stays framed after zoom and resize");
            view.Size = new Vector2(80, 480);
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            check.That(camera.GetViewport().GetVisibleRect().Size.X == 80, "3D terrain uses the very narrow width");
            check.That(AllInside(camera, vertices), "3D terrain stays framed in a very narrow view");
        }
        finally
        {
            view.QueueFree();
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        }
    }

    private static void Click(LevelTerrainViewport view, Vector2 at, MouseButton button)
    {
        Vector2 point = view.GlobalPosition + at;
        view.GetViewport().PushInput(new InputEventMouseButton { Position = point, GlobalPosition = point, ButtonIndex = button, Pressed = true });
        view.GetViewport().PushInput(new InputEventMouseButton { Position = point, GlobalPosition = point, ButtonIndex = button, Pressed = false });
    }

    private static Camera3D? FindCamera(Node node)
    {
        if (node is Camera3D camera) return camera;
        foreach (Node child in node.GetChildren())
            if (FindCamera(child) is Camera3D found) return found;
        return null;
    }

    private static bool AllInside(Camera3D camera, System.Numerics.Vector3[] vertices)
    {
        Vector2 size = camera.GetViewport().GetVisibleRect().Size;
        if (size.X <= 0 || size.Y <= 0 || vertices.Length == 0) return false;
        foreach (System.Numerics.Vector3 vertex in vertices)
        {
            Vector3 point = new(vertex.X, vertex.Y, vertex.Z);
            Vector2 screen = camera.UnprojectPosition(point);
            float depth = -(camera.GlobalTransform.AffineInverse() * point).Z;
            if (!float.IsFinite(screen.X) || !float.IsFinite(screen.Y) || !float.IsFinite(depth) ||
                camera.IsPositionBehind(point) || depth < camera.Near || depth > camera.Far ||
                screen.X < 0 || screen.Y < 0 || screen.X > size.X || screen.Y > size.Y) return false;
        }
        return true;
    }
}
