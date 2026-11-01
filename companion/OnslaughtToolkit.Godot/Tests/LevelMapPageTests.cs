// SPDX-License-Identifier: GPL-3.0-only
using System.Globalization;
using System.IO.Compression;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using Godot;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// The level editor's map driven with mouse and key events pushed into the window, so they take the engine's own route to the control
/// (the control under the pointer, the focus owner for keys) and not a call into the control: click a mark, wheel-zoom, pan, drag a mark,
/// cancel a drag with Esc, and undo a drag as one step. The level is the authored one with its authored terrain; its five things start
/// on one spot and the test spreads them out first. Authored data only; nothing retail.
/// </summary>
internal static class LevelMapPageTests
{
    private static SignalAwaiter Frame(SceneTree tree) => tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);

    private static string[] Snapshot(string root) => [.. Directory.EnumerateFiles(root, "*", SearchOption.AllDirectories).Order(StringComparer.Ordinal)
        .Select(path => Path.GetRelativePath(root, path) + " " + Convert.ToHexStringLower(SHA256.HashData(File.ReadAllBytes(path))))];

    private static uint Bits(float value) => BitConverter.SingleToUInt32Bits(value);

    /// <summary>Prepends authored terrain to an authored archive, with bounded members as the reader expects.</summary>
    private static byte[] WithAuthoredTerrain(byte[] archive)
    {
        byte[] terrain = LevelTests.Unpack(LevelVectors.Terrain.Eres);
        using MemoryStream chunk = new();
        using (BinaryWriter writer = new(chunk, Encoding.ASCII, leaveOpen: true))
        {
            writer.Write(Encoding.ASCII.GetBytes("ERES"));
            writer.Write((uint)terrain.Length);
            writer.Write(terrain);
        }
        byte[] input = chunk.ToArray();
        using MemoryStream joined = new();
        using (BinaryWriter writer = new(joined, Encoding.ASCII, leaveOpen: true))
        {
            int part = Math.Min(LevelArchive.PackBufferBytes / 2, LevelArchive.MaxMemberInflatedBytes / 2);
            for (int at = 0; at < input.Length; at += part)
            {
                using MemoryStream compressed = new();
                using (ZLibStream zlib = new(compressed, CompressionLevel.Optimal, leaveOpen: true))
                    zlib.Write(input, at, Math.Min(part, input.Length - at));
                byte[] member = compressed.ToArray();
                if (member.Length > LevelArchive.PackBufferBytes) throw new InvalidDataException("The authored terrain fixture exceeds the member limit.");
                writer.Write((uint)member.Length);
                writer.Write(member);
            }
            writer.Write(archive);
        }
        return joined.ToArray();
    }

    /// <summary>A pixel of the map as a pixel of the window, which is where events are pushed.</summary>
    private static Vector2 InWindow(LevelMap map, Vector2 local) => map.GetGlobalRect().Position + local;

    private static void Push(SceneTree tree, InputEvent input) => tree.Root.PushInput(input, true);

    private static void Wheel(SceneTree tree, LevelMap map, Vector2 local, bool up)
    {
        Vector2 at = InWindow(map, local);
        Push(tree, new InputEventMouseButton { ButtonIndex = up ? MouseButton.WheelUp : MouseButton.WheelDown, Pressed = true, Factor = 1, Position = at, GlobalPosition = at });
        Push(tree, new InputEventMouseButton { ButtonIndex = up ? MouseButton.WheelUp : MouseButton.WheelDown, Pressed = false, Factor = 1, Position = at, GlobalPosition = at });
    }

    private static void Mouse(SceneTree tree, LevelMap map, Vector2 local, MouseButton button, bool pressed)
    {
        Vector2 at = InWindow(map, local);
        MouseButtonMask held = button switch { MouseButton.Left => MouseButtonMask.Left, MouseButton.Right => MouseButtonMask.Right, _ => MouseButtonMask.Middle };
        Push(tree, new InputEventMouseButton { ButtonIndex = button, Pressed = pressed, Position = at, GlobalPosition = at, ButtonMask = pressed ? held : 0 });
    }

    private static void TerrainClick(SceneTree tree, LevelTerrainViewport view, Vector2 local, MouseButton button)
    {
        Vector2 at = view.GetGlobalRect().Position + local;
        MouseButtonMask mask = button == MouseButton.Left ? MouseButtonMask.Left : MouseButtonMask.Right;
        Push(tree, new InputEventMouseButton { ButtonIndex = button, Pressed = true, Position = at, GlobalPosition = at, ButtonMask = mask });
        Push(tree, new InputEventMouseButton { ButtonIndex = button, Pressed = false, Position = at, GlobalPosition = at });
    }

    private static Camera3D? TerrainCamera(Node root)
    {
        if (root is Camera3D camera) return camera;
        foreach (Node child in root.GetChildren())
            if (TerrainCamera(child) is Camera3D found) return found;
        return null;
    }

    /// <summary>Moves the pointer in steps of at most <paramref name="stepPixels"/> from where it is to <paramref name="to"/>, holding the buttons given.</summary>
    private static void Glide(SceneTree tree, LevelMap map, ref Vector2 pointer, Vector2 to, MouseButtonMask held, float stepPixels = 9)
    {
        int steps = Math.Max(1, (int)Math.Ceiling(pointer.DistanceTo(to) / stepPixels));
        for (int step = 1; step <= steps; step++)
        {
            Vector2 next = pointer.Lerp(to, step / (float)steps);
            Vector2 at = InWindow(map, next);
            Vector2 previous = InWindow(map, pointer);
            Push(tree, new InputEventMouseMotion { Position = at, GlobalPosition = at, Relative = at - previous, ButtonMask = held });
            pointer = next;
        }
    }

    private static void PressKey(SceneTree tree, Key key) =>
        Push(tree, new InputEventKey { Keycode = key, PhysicalKeycode = key, Pressed = true });

    private static void PressKeyWith(SceneTree tree, Key key, bool shift = false, bool ctrl = false) =>
        Push(tree, new InputEventKey { Keycode = key, PhysicalKeycode = key, Pressed = true, ShiftPressed = shift, CtrlPressed = ctrl });

    /// <summary>The world position under a map pixel, worked out here from the view's centre and scale (the inverse of the drawing).</summary>
    private static (double X, double Y) World(LevelMap map, Vector2 local) =>
        (map.View.CenterX + (local.X - map.Size.X / 2.0) / map.View.Scale, map.View.CenterY - (local.Y - map.Size.Y / 2.0) / map.View.Scale);

    /// <summary>The float a pair of decimals with two places stands for, which is what typing them would store.</summary>
    private static float Hundredths(double value) =>
        float.Parse(Math.Round((decimal)value, 2, MidpointRounding.ToEven).ToString(CultureInfo.InvariantCulture), CultureInfo.InvariantCulture);

    internal static async Task RunAsync(CompanionApp app, SceneTree tree, FakeInstall install, Checks check)
    {
        check.Suite("level map");
        LevelEditorPage page = app.LevelEditor;
        // The authored level 100 again, now with its authored terrain, so the map has relief to draw.
        File.WriteAllBytes(Path.Combine(install.Game, "data", "resources", "100_res_PC.aya"),
            LevelTests.Unpack(LevelVectors.Archives.First(archive => archive.Name == "level-100-terrain").File));
        // A second authored archive has its own world and terrain, with overlapping row numbers.
        File.WriteAllBytes(Path.Combine(install.Game, "data", "resources", "200_res_PC.aya"),
            WithAuthoredTerrain(LevelTests.Unpack(LevelVectors.Archives.First(archive => archive.Name == "base-and-real").File)));
        string[] gameBefore = Snapshot(install.Game);
        // The page tests before this left the Save as mod dialog open, and an open dialog takes the window's input: close what is still showing.
        foreach (Window window in app.FindChildren("*", nameof(Window), true, false).OfType<Window>().Where(window => window.Visible)) window.Hide();
        app.Navigate("home");
        app.Navigate("levels");
        await Frame(tree);
        check.That(page.OpenLevel(100), "level 100 opens with its terrain");
        for (int frame = 0; frame < 4; frame++) await Frame(tree);
        LevelMap map = page.Map;
        LevelEditorModel model = page.Model!;
        check.That(map.IsVisibleInTree() && map.HasRelief && model.Terrain is not null && map.Size.X >= 200 && map.Size.Y >= 200 && Math.Abs(map.View.Scale - map.View.FitScale) < 1e-9,
            $"the map shows the level's relief, fitted to the whole square: {map.Size}, scale {map.View.Scale}");
        check.That(page.MapToggle.ButtonPressed && Math.Abs(map.View.CenterX - 256) < 1e-9 && Math.Abs(map.View.CenterY - 256) < 1e-9, "the map starts centred on the square");

        // Spread the five things out (typed moves, as a person would), the second with a stored -0 for Z.
        (int Row, string X, string Y, string Z)[] spread = [(0, "100", "400", "0"), (1, "300", "380", "-0"), (2, "120", "120", "0"), (3, "400", "100", "0"), (4, "256", "256", "0")];
        foreach ((int row, string x, string y, string z) in spread) check.That(model.Move(row, x, y, z).Result == MoveResult.Moved, $"row {row} is moved to {x}, {y}");
        await Frame(tree);
        await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        GD.Print("mission_terrain_page_test_reached");
        var missionTerrainSplit = tree.Root.FindChild("MissionTerrainSplit", true, false) as SplitContainer;
        var missionTerrainPanel = tree.Root.FindChild("MissionReferences", true, false) as MissionReferencePanel;
        Button? missionTerrainToggle = null;
        foreach (Node candidate in tree.Root.FindChildren("*", "Button", true, false))
            if (candidate is Button button && button.Text == "3D") { missionTerrainToggle = button; break; }
        check.That(missionTerrainSplit != null && missionTerrainPanel != null && missionTerrainToggle != null,
            "the Level page exposes the combined terrain and mission controls");
        if (missionTerrainSplit != null && missionTerrainPanel != null && missionTerrainToggle != null)
        {
            bool originalTerrainChoice = missionTerrainToggle.ButtonPressed;
            missionTerrainToggle.ButtonPressed = true;
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            var missionTerrainViewport = missionTerrainSplit.GetChild(0) as LevelTerrainViewport;
            check.That(missionTerrainSplit.Visible && missionTerrainViewport != null && missionTerrainViewport.Visible,
                "the existing 3D toggle shows the combined terrain and mission view");
            check.That(missionTerrainViewport?.TerrainProvider != null
                && missionTerrainViewport.TerrainProvider() is not null &&
                ReferenceEquals(missionTerrainViewport.TerrainProvider(), model.Terrain),
                "the combined view reads the current in-memory terrain");
            check.That(missionTerrainPanel.Snapshot != null && model.Session != null
                && missionTerrainPanel.Snapshot.Scripts.Count == model.Session.Body.Scripts.Count,
                "the mission panel reads the current in-memory session");
            missionTerrainToggle.ButtonPressed = false;
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            check.That(!missionTerrainSplit.Visible, "the existing 3D toggle hides the combined view");
            missionTerrainToggle.ButtonPressed = originalTerrainChoice;
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        }

        check.That(Bits(model.Row(1)!.Position.Z) == 0x80000000, "row 1 stores a negative zero");
        string setup = model.Session!.UndoDescription!;

        // A click on a mark selects it, in the map, the table and the fields; nothing moves.
        Vector2 pointer = map.ToScreen(256, 256);
        Mouse(tree, map, pointer, MouseButton.Left, true);
        Mouse(tree, map, pointer, MouseButton.Left, false);
        check.That(page.SelectedRow == 4 && map.Selected == 4 && page.Table.GetSelected()?.GetMetadata(0).AsInt32() == 4 && page.X.Text == "256" && page.Y.Text == "256" && map.HasFocus(),
            $"a click on a mark selects its row everywhere: row {page.SelectedRow}, map {map.Selected}, fields {page.X.Text}, {page.Y.Text}");
        check.That(model.Session.UndoDescription == setup && !map.Dragging, "and moves nothing");

        // A click within the click radius of a mark still selects it; one far from every mark does not change the selection or the view.
        pointer = map.ToScreen(120, 120) + new Vector2(7, -5);
        Mouse(tree, map, pointer, MouseButton.Left, true);
        Mouse(tree, map, pointer, MouseButton.Left, false);
        check.That(page.SelectedRow == 2 && map.Selected == 2, "a click a few pixels off a mark selects it");
        double centreX = map.View.CenterX, centreY = map.View.CenterY;
        pointer = map.ToScreen(30, 480);
        Mouse(tree, map, pointer, MouseButton.Left, true);
        Mouse(tree, map, pointer, MouseButton.Left, false);
        check.That(page.SelectedRow == 2 && map.View.CenterX == centreX && map.View.CenterY == centreY && model.Session.UndoDescription == setup, "a click on empty ground changes neither the selection nor the view");

        // The wheel zooms about the pointer: the world position under it stays under it.
        double scale = map.View.Scale;
        Vector2 about = map.ToScreen(300, 380);
        (double wx, double wy) = World(map, about);
        Wheel(tree, map, about, up: true);
        Vector2 now = map.ToScreen(wx, wy);
        check.That(Math.Abs(map.View.Scale / scale - 1.2) < 1e-9 && now.DistanceTo(about) < 0.01, $"the wheel zooms 1.2 times about the pointer: x{map.View.Scale / scale}, the point moved {now.DistanceTo(about)} pixels");
        Wheel(tree, map, about, up: false);
        check.That(Math.Abs(map.View.Scale - scale) < 1e-9 && map.ToScreen(wx, wy).DistanceTo(about) < 0.01, "the wheel the other way zooms back");
        for (int click = 0; click < 60; click++) Wheel(tree, map, about, up: true);
        check.That(map.View.Scale == MapView.MaxScale, $"zooming in stops at {MapView.MaxScale} pixels to the unit: {map.View.Scale}");
        for (int click = 0; click < 120; click++) Wheel(tree, map, about, up: false);
        check.That(Math.Abs(map.View.Scale - map.View.MinScale) < 1e-12, $"zooming out stops at half the fit: {map.View.Scale} against {map.View.MinScale}");
        PressKey(tree, Godot.Key.Home);
        check.That(Math.Abs(map.View.Scale - map.View.FitScale) < 1e-12 && map.View.CenterX == 256 && map.View.CenterY == 256, "Home shows the whole square again");
        PressKey(tree, Godot.Key.Equal);
        check.That(Math.Abs(map.View.Scale / map.View.FitScale - 1.2) < 1e-9, "the + key zooms in about the middle");
        PressKey(tree, Godot.Key.Minus);
        check.That(Math.Abs(map.View.Scale - map.View.FitScale) < 1e-12, "and the - key out");

        // Dragging the background pans: every mark moves by the pixels the pointer did.
        Vector2 markBefore = map.ToScreen(300, 380);
        pointer = map.ToScreen(200, 200);
        Vector2 start = pointer;
        Mouse(tree, map, pointer, MouseButton.Left, true);
        Vector2 target = pointer + new Vector2(40, -25);
        Glide(tree, map, ref pointer, target, MouseButtonMask.Left);
        Mouse(tree, map, pointer, MouseButton.Left, false);
        Vector2 markAfter = map.ToScreen(300, 380);
        check.That((markAfter - markBefore).DistanceTo(pointer - start) < 0.01 && !map.Dragging && page.SelectedRow == 2 && model.Session.UndoDescription == setup,
            $"dragging the background pans by the pointer's movement: marks moved {markAfter - markBefore}, pointer {pointer - start}; nothing selected or moved");
        PressKey(tree, Godot.Key.Home);

        // Dragging a mark moves it: the mark follows the pointer, nothing is changed until it is let go, then X and Y are the world position
        // under the pointer to a hundredth and Z is kept bit for bit. One drag is one undo step.
        Vector2 grab = map.ToScreen(100, 400);
        Mouse(tree, map, grab, MouseButton.Left, true);
        pointer = grab;
        Vector2 drop = map.ToScreen(150.25, 330.5) + new Vector2(0.37f, -0.21f);
        Glide(tree, map, ref pointer, drop, MouseButtonMask.Left);
        bool previewed = map.Dragging && model.Row(0)!.Position.X == 100f && model.Row(0)!.Position.Y == 400f && model.Session.UndoDescription == setup;
        // The position a drag asks for (and the label shows) is a hundredth at every pointer position, not a float with noise in its last digits.
        int untidy = 0;
        for (int step = 0; step < 60; step++)
        {
            Glide(tree, map, ref pointer, pointer + new Vector2(0.37f, -0.53f), MouseButtonMask.Left);
            if (map.DragPosition is not { } position || !Regex.IsMatch(CoordinateInput.Format(position.X), @"^-?\d+(\.\d{1,2})?$") || !Regex.IsMatch(CoordinateInput.Format(position.Y), @"^-?\d+(\.\d{1,2})?$")) untidy++;
        }
        check.That(untidy == 0, $"while a mark is dragged the position it asks for is always to a hundredth ({untidy} of 60 pointer positions were not)");
        Glide(tree, map, ref pointer, drop, MouseButtonMask.Left);
        Mouse(tree, map, pointer, MouseButton.Left, false);
        (double ex, double ey) = World(map, drop);
        System.Numerics.Vector3 moved = model.Row(0)!.Position;
        check.That(previewed && !map.Dragging, "while a mark is dragged the model keeps the stored position, and letting go ends the drag");
        check.That(moved.X == Hundredths(ex) && moved.Y == Hundredths(ey) && Bits(moved.Z) == Bits(0f),
            $"letting go moves the row to the world position under the pointer, to a hundredth, with Z kept: {moved.X}, {moved.Y}, {moved.Z} against {ex}, {ey}");
        check.That(page.X.Text == CoordinateInput.Format(moved.X) && page.Y.Text == CoordinateInput.Format(moved.Y) && page.Z.Text == "0" && page.SelectedRow == 0 &&
                   page.Table.GetSelected()?.GetText(3) == CoordinateInput.Format(moved.X) && page.Table.GetSelected()?.GetText(4) == CoordinateInput.Format(moved.Y) &&
                   page.Note.StartsWith("Tank 1 (row 0) now stands at ", StringComparison.Ordinal), $"the fields, the table and the note show the new position: \"{page.X.Text}\", \"{page.Y.Text}\", \"{page.Note}\"");
        check.That(map.ToScreen(moved.X, moved.Y).DistanceTo(drop) < 0.05, $"the mark is drawn where it was dropped: {map.ToScreen(moved.X, moved.Y)} against {drop}");
        string dragMove = model.Session.UndoDescription!;
        check.That(dragMove != setup && dragMove.Contains("Tank 1", StringComparison.Ordinal), "the drag is one entry in the undo list: " + dragMove);
        page.Undo.EmitSignal(BaseButton.SignalName.Pressed);
        check.That(model.Row(0)!.Position == new System.Numerics.Vector3(100, 400, 0) && model.Session.UndoDescription == setup && page.X.Text == "100" && page.Y.Text == "400",
            "one undo takes the whole drag back");
        page.Redo.EmitSignal(BaseButton.SignalName.Pressed);
        check.That(model.Row(0)!.Position == moved && model.Session.UndoDescription == dragMove, "and one redo makes it again");

        // Esc puts a dragged mark back: nothing is requested, and letting go afterwards does nothing.
        System.Numerics.Vector3 stood = model.Row(3)!.Position;
        grab = map.ToScreen(400, 100);
        Mouse(tree, map, grab, MouseButton.Left, true);
        pointer = grab;
        Glide(tree, map, ref pointer, grab + new Vector2(-60, 45), MouseButtonMask.Left);
        bool dragging = map.Dragging;
        PressKey(tree, Godot.Key.Escape);
        check.That(dragging && !map.Dragging, "Esc ends a drag in progress");
        Glide(tree, map, ref pointer, grab + new Vector2(-80, 20), MouseButtonMask.Left);
        Mouse(tree, map, pointer, MouseButton.Left, false);
        check.That(model.Row(3)!.Position == stood && model.Session.UndoDescription == dragMove && page.Note.Length == 0 && !map.Dragging,
            $"after Esc the row is where it was, nothing was requested (no move was announced: \"{page.Note}\"), and letting go changes nothing");

        // A press on a mark and a small wobble is a click: it selects and does not move.
        grab = map.ToScreen(400, 100);
        Mouse(tree, map, grab, MouseButton.Left, true);
        pointer = grab;
        Glide(tree, map, ref pointer, grab + new Vector2(2, -1), MouseButtonMask.Left);
        Mouse(tree, map, pointer, MouseButton.Left, false);
        check.That(page.SelectedRow == 3 && model.Row(3)!.Position == stood && model.Session.UndoDescription == dragMove && !map.Dragging, "a press and a wobble under the drag threshold selects and moves nothing");

        // A stored -0 survives a drag.
        grab = map.ToScreen(300, 380);
        Mouse(tree, map, grab, MouseButton.Left, true);
        pointer = grab;
        Glide(tree, map, ref pointer, map.ToScreen(333.33, 301.07), MouseButtonMask.Left);
        Mouse(tree, map, pointer, MouseButton.Left, false);
        System.Numerics.Vector3 ghost = model.Row(1)!.Position;
        check.That(page.SelectedRow == 1 && Bits(ghost.Z) == 0x80000000 && Math.Abs(ghost.X - 333.33f) < 0.011 && Math.Abs(ghost.Y - 301.07f) < 0.011 && page.Z.Text == "-0",
            $"dragging a row whose stored Z is -0 keeps the -0: {ghost}, \"{page.Z.Text}\"");

        // A drag that ends on another mark still moves the dragged one, and a second drag of the same row is a second undo step.
        grab = map.ToScreen(moved.X, moved.Y);
        Mouse(tree, map, grab, MouseButton.Left, true);
        pointer = grab;
        Glide(tree, map, ref pointer, map.ToScreen(256, 256), MouseButtonMask.Left);
        Mouse(tree, map, pointer, MouseButton.Left, false);
        System.Numerics.Vector3 second = model.Row(0)!.Position;
        check.That(page.SelectedRow == 0 && second.X == 256f && second.Y == 256f && Bits(second.Z) == Bits(0f) && model.Row(4)!.Position.X == 256f, $"a drag that ends on another mark still moves the dragged row: {second}");
        page.Undo.EmitSignal(BaseButton.SignalName.Pressed);
        check.That(model.Row(0)!.Position == moved && model.Row(1)!.Position.X > 333f, "and a second drag of the same row is its own step: one undo puts it back where the first drag left it, and leaves the other rows' drags");
        page.Redo.EmitSignal(BaseButton.SignalName.Pressed);
        check.That(model.Row(0)!.Position == second, "and one redo makes it again");

        // Arrow keys nudge the selected mark: 0.5 a press (+Y is up), Shift 5, Ctrl 0.05, each press one undo step; a key with nothing selected, or during a drag, moves nothing.
        page.SelectRow(0);
        map.GrabFocus();
        await Frame(tree);
        System.Numerics.Vector3 from = model.Row(0)!.Position;
        string beforeNudge = model.Session!.UndoDescription!;
        PressKey(tree, Godot.Key.Right);
        System.Numerics.Vector3 afterRight = model.Row(0)!.Position;
        PressKey(tree, Godot.Key.Up);
        System.Numerics.Vector3 afterUp = model.Row(0)!.Position;
        check.That(afterRight.X == Hundredths(from.X + 0.5) && afterRight.Y == from.Y && Bits(afterRight.Z) == Bits(from.Z) && afterUp.X == afterRight.X && afterUp.Y == Hundredths(from.Y + 0.5),
            $"the right arrow moves the selected mark 0.5 along X and the up arrow 0.5 along Y (up on the map), Z kept: {from} -> {afterRight} -> {afterUp}");
        check.That(page.X.Text == CoordinateInput.Format(afterUp.X) && page.Y.Text == CoordinateInput.Format(afterUp.Y) && page.SelectedRow == 0, $"the fields follow a nudge: \"{page.X.Text}\", \"{page.Y.Text}\" against {afterUp}");
        PressKeyWith(tree, Godot.Key.Left, shift: true);
        PressKeyWith(tree, Godot.Key.Down, ctrl: true);
        System.Numerics.Vector3 afterBig = model.Row(0)!.Position;
        check.That(afterBig.X == Hundredths(afterUp.X - 5) && afterBig.Y == Hundredths(afterUp.Y - 0.05), $"Shift nudges by 5 and Ctrl by 0.05, left is -X and down is -Y: {afterUp} -> {afterBig}");
        page.Undo.EmitSignal(BaseButton.SignalName.Pressed);
        check.That(model.Row(0)!.Position.X == afterBig.X && model.Row(0)!.Position.Y == afterUp.Y, $"each press is one undo step: one undo takes back the last nudge only: {afterBig} -> {model.Row(0)!.Position}");
        page.Undo.EmitSignal(BaseButton.SignalName.Pressed);
        page.Undo.EmitSignal(BaseButton.SignalName.Pressed);
        page.Undo.EmitSignal(BaseButton.SignalName.Pressed);
        check.That(model.Row(0)!.Position == from && model.Session.UndoDescription == beforeNudge, "and four undos take the four nudges back");
        // A nudge moves the one axis that was pressed: the other axis and Z are kept bit for bit (an off-grid number and a stored -0 included), and the pressed axis lands on the hundredth as a drop does.
        System.Numerics.Vector3 rowTwo = model.Row(2)!.Position;
        var missionPanelSnapshotBeforeMove = missionTerrainPanel?.Snapshot;
        check.That(model.Move(2, "100.123456", "55.5678", "0").Result == MoveResult.Moved, "row 2 is typed to numbers that are off the hundredth grid");
        check.That(missionTerrainPanel?.Snapshot != null && missionPanelSnapshotBeforeMove != null
            && !ReferenceEquals(missionTerrainPanel.Snapshot, missionPanelSnapshotBeforeMove),
            "mission panel recaptures the current session when the editor changes");
        page.SelectRow(2);
        map.GrabFocus();
        await Frame(tree);
        System.Numerics.Vector3 offGrid = model.Row(2)!.Position;
        check.That(Bits(Hundredths(offGrid.X)) != Bits(offGrid.X) && Bits(Hundredths(offGrid.Y)) != Bits(offGrid.Y), $"row 2 stands off the hundredth grid (the premise of the checks below): {offGrid}");
        PressKey(tree, Godot.Key.Right);
        System.Numerics.Vector3 offGridRight = model.Row(2)!.Position;
        check.That(offGridRight.X == Hundredths(offGrid.X + 0.5) && Bits(offGridRight.Y) == Bits(offGrid.Y) && Bits(offGridRight.Z) == Bits(offGrid.Z),
            $"a nudge along X puts X on the hundredth and keeps Y and Z bit for bit, Y being off the grid: {offGrid} -> {offGridRight}");
        PressKey(tree, Godot.Key.Up);
        System.Numerics.Vector3 offGridUp = model.Row(2)!.Position;
        check.That(offGridUp.Y == Hundredths(offGrid.Y + 0.5) && Bits(offGridUp.X) == Bits(offGridRight.X) && Bits(offGridUp.Z) == Bits(offGrid.Z),
            $"a nudge along Y puts Y on the hundredth and keeps X and Z bit for bit: {offGridRight} -> {offGridUp}");
        check.That(model.Move(2, CoordinateInput.Format(offGridUp.X), "-0", "0").Result == MoveResult.Moved, "row 2's Y is typed as -0");
        await Frame(tree);
        System.Numerics.Vector3 negativeY = model.Row(2)!.Position;
        PressKey(tree, Godot.Key.Right);
        System.Numerics.Vector3 negativeYRight = model.Row(2)!.Position;
        check.That(Bits(negativeY.Y) == 0x80000000 && Bits(negativeYRight.Y) == 0x80000000 && negativeYRight.X == Hundredths(negativeY.X + 0.5),
            $"a stored -0 in Y survives a nudge along X: {negativeY} -> {negativeYRight}");
        for (int undo = 0; undo < 5; undo++) page.Undo.EmitSignal(BaseButton.SignalName.Pressed);
        check.That(model.Row(2)!.Position == rowTwo && model.Session.UndoDescription == beforeNudge, "and the two typed moves and the three nudges are each one undo step: five undos put row 2 back");
        page.SelectRow(0);
        map.GrabFocus();
        await Frame(tree);
        // Mid-drag the arrows are not taken, and with no selected mark they are not either.
        grab = map.ToScreen(from.X, from.Y);
        Mouse(tree, map, grab, MouseButton.Left, true);
        pointer = grab;
        Glide(tree, map, ref pointer, grab + new Vector2(40, 30), MouseButtonMask.Left);
        bool midDrag = map.Dragging;
        PressKey(tree, Godot.Key.Right);
        bool stillMidDrag = map.Dragging;
        PressKey(tree, Godot.Key.Escape);
        Mouse(tree, map, pointer, MouseButton.Left, false);
        check.That(midDrag && stillMidDrag && model.Row(0)!.Position == from && model.Session.UndoDescription == beforeNudge, $"an arrow key during a drag moves nothing, and Esc still cancels the drag: dragging {midDrag}, {stillMidDrag}; row 0 {model.Row(0)!.Position} against {from}");
        map.Select(null);
        PressKey(tree, Godot.Key.Right);
        check.That(model.Row(0)!.Position == from && model.Session.UndoDescription == beforeNudge, $"an arrow key with no mark selected moves nothing: row 0 {model.Row(0)!.Position} against {from}");
        page.SelectRow(0);

        // The map can be hidden, and then it gets no events; showing it again brings it back.
        page.MapToggle.ButtonPressed = false;
        await Frame(tree);
        double hiddenScale = map.View.Scale;
        Wheel(tree, map, new Vector2(100, 100), up: true);
        check.That(!map.IsVisibleInTree() && map.View.Scale == hiddenScale, "a hidden map does not take events");
        page.MapToggle.ButtonPressed = true;
        await Frame(tree);
        Wheel(tree, map, new Vector2(100, 100), up: true);
        check.That(map.IsVisibleInTree() && Math.Abs(map.View.Scale / hiddenScale - 1.2) < 1e-9, "and a shown one does");

        await CheckTerrainPageWiring(page, model, tree, check);

        // The pointer leaves; the page wrote nothing into the game.
        Push(tree, new InputEventMouseMotion { Position = new Vector2(-50, -50), GlobalPosition = new Vector2(-50, -50) });
        await Frame(tree);
        check.That(Snapshot(install.Game).SequenceEqual(gameBefore), "working the map never wrote anything into the game folder");
        app.Navigate("home");
        await Frame(tree);
    }

    private static async Task CheckTerrainPageWiring(LevelEditorPage page, LevelEditorModel model, SceneTree tree, Checks check)
    {
        Vector2I previousSize = tree.Root.Size;
        try
        {
            tree.Root.Size = new Vector2I(1280, 800);
            for (int frame = 0; frame < 3; frame++) await Frame(tree);
            await CheckTerrainPageWiringWide(page, model, tree, check);
        }
        finally
        {
            tree.Root.Size = previousSize;
            await Frame(tree);
        }
    }

    private static async Task CheckTerrainPageWiringWide(LevelEditorPage page, LevelEditorModel model, SceneTree tree, Checks check)
    {
        page.TerrainViewSwitch.ButtonPressed = true;
        for (int frame = 0; frame < 4; frame++) await Frame(tree);
        LevelTerrainViewport view = page.TerrainPreview;
        Camera3D? camera = TerrainCamera(view);
        Heightfield? terrain = model.Terrain;
        EditSession? session = model.Session;
        check.That(view.IsVisibleInTree() && camera is not null && terrain is not null && session is not null,
                   "the real page shows its 3D terrain with an active editor session");
        if (camera is null || terrain is null || session is null || !view.IsVisibleInTree()) return;

        int[] units = session.Body.Things.Select((thing, row) => (thing, row))
            .Where(item => DuplicateObject.CanCopy(item.thing)).Select(item => item.row).Take(2).ToArray();
        check.That(units.Length == 2, "the authored world has two units for the page's 3D selection test");
        if (units.Length != 2) return;
        float firstX = Heightfield.Size * 0.35f, firstY = Heightfield.Size * 0.40f;
        float secondX = Heightfield.Size * 0.60f, secondY = Heightfield.Size * 0.58f;
        MoveOutcome firstSetup = model.Move(units[0], CoordinateInput.Format(firstX), CoordinateInput.Format(firstY),
                                            CoordinateInput.Format(terrain.HeightAt(firstX, firstY) + 0.125f));
        MoveOutcome secondSetup = model.Move(units[1], CoordinateInput.Format(secondX), CoordinateInput.Format(secondY),
                                             CoordinateInput.Format(terrain.HeightAt(secondX, secondY) + 0.25f));
        check.That(firstSetup.Result != MoveResult.Refused && secondSetup.Result != MoveResult.Refused,
                   "the authored units can be placed at distinct visible 3D marks");
        if (firstSetup.Result == MoveResult.Refused || secondSetup.Result == MoveResult.Refused) return;
        for (int frame = 0; frame < 2; frame++) await Frame(tree);
        System.Numerics.Vector3 first = model.Row(units[0])!.Position, second = model.Row(units[1])!.Position;
        Vector2 firstMark = camera.UnprojectPosition(new Vector3(first.X, -first.Z, -first.Y));
        Vector2 secondMark = camera.UnprojectPosition(new Vector3(second.X, -second.Z, -second.Y));
        bool marksVisible = view._GetTooltip(firstMark).Contains($"row {units[0]}", StringComparison.Ordinal) &&
                            view._GetTooltip(secondMark).Contains($"row {units[1]}", StringComparison.Ordinal);
        check.That(marksVisible, "the current page projects the two authored units as independently selectable marks");
        if (!marksVisible) return;

        page.SelectIndex(units[1]);
        int firstPickEvents = 0, guiEvents = 0;
        void FirstPicked(int row) => firstPickEvents++;
        void GotGuiInput(InputEvent input) { if (input is InputEventMouseButton) guiEvents++; }
        view.RowPicked += FirstPicked;
        view.GuiInput += GotGuiInput;
        Vector2 pointer = view.GetGlobalRect().Position + firstMark;
        Push(tree, new InputEventMouseMotion { Position = pointer, GlobalPosition = pointer });
        Control? hovered = tree.Root.GuiGetHoveredControl();
        bool hoveredView = hovered is not null && (ReferenceEquals(hovered, view) || view.IsAncestorOf(hovered));
        TerrainClick(tree, view, firstMark, MouseButton.Left);
        view.RowPicked -= FirstPicked;
        check.That(page.SelectedRow == units[0] && page.Map.Selected == units[0] &&
                   page.Table.GetSelected()?.GetMetadata(0).AsInt32() == units[0] && firstPickEvents == 1,
                   $"clicking a 3D mark selects the same row in the real page, map and table (3D hovered {hoveredView}, hovered control {hovered?.GetType().Name ?? "none"}, GUI events {guiEvents}, pick events {firstPickEvents})");

        // Project the interior of an authored preview triangle so a right-click exercises the actual camera and terrain picker.
        TerrainSurface surface = TerrainSurface.Build(terrain);
        System.Numerics.Vector3[] vertices = surface.Vertices.ToArray();
        int[] indices = surface.Indices.ToArray();
        Vector2? targetScreen = null;
        System.Numerics.Vector3 target = default;
        int inViewport = 0;
        for (int i = 0; i + 2 < indices.Length; i += 3)
        {
            var candidate = (vertices[indices[i]] + vertices[indices[i + 1]] + vertices[indices[i + 2]]) / 3;
            Vector2 screen = camera.UnprojectPosition(new Vector3(candidate.X, candidate.Y, candidate.Z));
            if (screen.X >= 0 && screen.Y >= 0 && screen.X < view.Size.X && screen.Y < view.Size.Y) inViewport++;
            if (screen.X <= 12 || screen.Y <= 12 || screen.X >= view.Size.X - 12 || screen.Y >= view.Size.Y - 12 ||
                screen.DistanceTo(firstMark) < 24 || screen.DistanceTo(secondMark) < 24 ||
                (Math.Abs(candidate.X - second.X) < 2 && Math.Abs(-candidate.Z - second.Y) < 2)) continue;
            target = candidate;
            targetScreen = screen;
            break;
        }
        check.That(targetScreen is not null, $"the authored 3D view has a visible terrain point distinct from both marks (window {tree.Root.Size}, view {view.Size}, projected triangles {inViewport})");
        if (targetScreen is not Vector2 targetAt) { view.GuiInput -= GotGuiInput; return; }

        byte[] before = session.ToBytes();
        int selectionEvents = 0, moveEvents = 0;
        void Picked(int _) => selectionEvents++;
        void Requested(int row, float x, float y) => moveEvents++;
        view.RowPicked += Picked;
        view.MoveRequested += Requested;
        TerrainClick(tree, view, secondMark, MouseButton.Left);
        bool selectedImmediately = page.SelectedRow == units[1] && page.Map.Selected == units[1];
        TerrainClick(tree, view, targetAt, MouseButton.Right); // Deliberately no frame between selection and movement.
        view.RowPicked -= Picked;
        view.MoveRequested -= Requested;
        view.GuiInput -= GotGuiInput;
        System.Numerics.Vector3 moved = model.Row(units[1])!.Position;
        check.That(selectionEvents == 1 && moveEvents == 1 && page.SelectedRow == units[1] && page.Map.Selected == units[1] &&
                   moved != second && model.Row(units[0])!.Position == first && Bits(moved.Z) == Bits(second.Z),
                   $"selecting a different 3D mark and immediately moving it updates only that page row, keeping its exact height (selected {selectedImmediately}, pick events {selectionEvents}, move events {moveEvents}, changed {moved != second}, first unchanged {model.Row(units[0])!.Position == first}, height kept {Bits(moved.Z) == Bits(second.Z)})");
        check.That(Math.Abs(moved.X - target.X) < 0.2f && Math.Abs(moved.Y + target.Z) < 0.2f &&
                   page.X.Text == CoordinateInput.Format(moved.X) && page.Y.Text == CoordinateInput.Format(moved.Y),
                   "the real page receives the terrain hit as world coordinates and updates its fields");
        byte[] after = session.ToBytes();
        page.Undo.EmitSignal(BaseButton.SignalName.Pressed);
        check.That(session.ToBytes().SequenceEqual(before), "one page Undo restores the entire 3D move");
        page.Redo.EmitSignal(BaseButton.SignalName.Pressed);
        check.That(session.ToBytes().SequenceEqual(after), "one page Redo restores the same 3D move");

        int previousLevel = model.Level!.Value;
        int? otherLevel = model.Levels.Select(level => (int?)level.Level).FirstOrDefault(level => level != previousLevel);
        check.That(otherLevel is not null && page.OpenLevel(otherLevel.Value) && model.Session is not null &&
                   !ReferenceEquals(model.Session, session), "another authored level opens as a different edit session");
        if (otherLevel is null || model.Session is not EditSession next || ReferenceEquals(next, session)) return;
        bool overlappingRow = units[1] < next.Body.Things.Count && page.SelectIndex(units[1]);
        check.That(overlappingRow && page.SelectedRow == units[1], "the next level has and selects the same row number");
        if (!overlappingRow) return;
        check.That(model.Terrain is not null && !ReferenceEquals(model.Terrain, terrain),
                   "the second authored world has a distinct terrain instance");
        byte[] nextBefore = next.ToBytes();
        System.Numerics.Vector3 nextPosition = model.Row(units[1])!.Position;
        int switchedInput = 0, switchedMove = 0;
        void SwitchedInput(InputEvent input) { if (input is InputEventMouseButton) switchedInput++; }
        void SwitchedMove(int row, float x, float y) => switchedMove++;
        view.GuiInput += SwitchedInput;
        view.MoveRequested += SwitchedMove;
        TerrainClick(tree, view, targetAt, MouseButton.Right); // The old camera still exists until the next process frame.
        check.That(switchedInput > 0 && switchedMove == 0 && next.ToBytes().SequenceEqual(nextBefore) && !next.CanUndo,
                   "the 3D view receives a right-click immediately after the level switch but cannot move the overlapping row on old terrain");
        await Frame(tree);
        await Frame(tree);
        TerrainClick(tree, view, targetAt, MouseButton.Right);
        view.GuiInput -= SwitchedInput;
        view.MoveRequested -= SwitchedMove;
        check.That(switchedMove == 1 && !next.ToBytes().SequenceEqual(nextBefore) && next.CanUndo &&
                   Bits(model.Row(units[1])!.Position.Z) == Bits(nextPosition.Z) && session.ToBytes().SequenceEqual(after),
                   "after the new terrain loads, a fresh right-click moves only the new world's row and preserves its height");
    }
}
