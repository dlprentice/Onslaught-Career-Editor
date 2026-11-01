// SPDX-License-Identifier: GPL-3.0-only
using System.Reflection;
using Godot;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Ui;
using NumericVector3 = System.Numerics.Vector3;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Object dragging through the real editor page, using authored world and terrain data only.</summary>
internal static class LevelObjectDragPageTests
{
    private static async Task Frames(SceneTree tree, int count = 2)
    {
        for (int i = 0; i < count; i++) await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
    }

    private static Camera3D Camera(LevelTerrainViewport view) => view.FindChildren("*", nameof(Camera3D), true, false).OfType<Camera3D>().Single();

    private static Vector2 Marker(LevelEditorPage page, Camera3D camera, int index)
    {
        NumericVector3 p = page.Map.Rows.Single(row => row.Index == index).Position;
        return camera.UnprojectPosition(new Vector3(p.X / 100f, -p.Z / 100f, p.Y / 100f));
    }

    private static Vector2 Target(Camera3D camera, Heightfield terrain, float x, float y) =>
        camera.UnprojectPosition(new Vector3(x, -terrain.HeightAt(x, y), y));

    private static void Button(LevelTerrainViewport view, Vector2 local, bool pressed)
    {
        Vector2 p = view.GlobalPosition + local;
        view.GetViewport().PushInput(new InputEventMouseButton
        {
            Position = p, GlobalPosition = p, ButtonIndex = MouseButton.Left, Pressed = pressed,
            ButtonMask = pressed ? MouseButtonMask.Left : default,
        }, true);
    }

    private static void Motion(LevelTerrainViewport view, Vector2 from, Vector2 to, bool pressed = true)
    {
        Vector2 p = view.GlobalPosition + to;
        view.GetViewport().PushInput(new InputEventMouseMotion
        {
            Position = p, GlobalPosition = p, Relative = to - from,
            ButtonMask = pressed ? MouseButtonMask.Left : default,
        }, true);
    }

    private static bool Unchanged(EditSession session, byte[] bytes, string? undo, bool redo) =>
        session.ToBytes().SequenceEqual(bytes) && session.UndoDescription == undo && session.CanRedo == redo;

    internal static async Task RunAsync(SceneTree tree, Checks check)
    {
        check.Suite("3D object drag through editor page");
        string scratch = Path.Combine(OS.GetUserDataDir(), "object-drag-tests", Guid.NewGuid().ToString("N"));
        string gameRoot = LevelEditorTests.GameWithLevels(scratch);
        string archive = Path.Combine(gameRoot, "data", "resources", "100_res_PC.aya");
        MethodInfo terrainFixture = typeof(LevelMapPageTests).GetMethod("WithAuthoredTerrain", BindingFlags.NonPublic | BindingFlags.Static)!;
        File.WriteAllBytes(archive, (byte[])terrainFixture.Invoke(null, [File.ReadAllBytes(archive)])!);
        string[] files = LevelEditorPageTests.Snapshot(gameRoot);
        Theme theme = CompanionTheme.Build();
        SettingsStore settings = new(Path.Combine(scratch, "settings.json"));
        GameLibrary game = new([], settings, ceUserFolder: "", ceEnvironment: _ => null);
        typeof(GameLibrary).GetProperty(nameof(GameLibrary.Folder))!.SetValue(game, GameFolder.Inspect(gameRoot, "Authored object drag fixture"));
        Control popups = new();
        AppServices services = new()
        {
            Workspace = null!, Game = game, Status = new StatusLine(), Backups = null!,
            GameRunning = () => false, OpenUrl = _ => { }, Navigate = _ => { }, OpenCareer = null!, ChooseCareer = null!,
            OpenCareerFile = () => { }, AskToDiscard = (_, _, _) => { }, LevelEditsUnsaved = () => 0,
            Play = new CePlay(game, Path.Combine(scratch, "unused-play")), Popups = popups, CatchUp = () => Task.CompletedTask,
        };
        LevelEditorPage page = new(services);
        page.Root.Theme = theme;
        page.Root.Size = new Vector2(1280, 800);
        await Frames(tree, 1);
        tree.Root.AddChild(popups);
        tree.Root.AddChild(page.Root);
        try
        {
            page.Refresh();
            await Frames(tree);
            if (page.Model is not { Session: { } session, Terrain: { } terrain } model ||
                page.TerrainPreview is not { } view || page.TerrainViewSwitch is not { } viewSwitch)
            {
                check.Fail("the real page opens authored world and terrain data");
                return;
            }
            viewSwitch.ButtonPressed = true;
            await Frames(tree, 3);
            Camera3D camera = Camera(view);
            int index = session.Body.Things.FindIndex(DuplicateObject.CanCopy);
            if (index < 0 || model.MoveTo(index, MapView.ToHundredths(180), MapView.ToHundredths(180)).Result != MoveResult.Moved)
            {
                check.Fail("an authored object can be positioned inside the terrain view");
                return;
            }
            page.SelectIndex(index);
            await Frames(tree);
            tree.Root.NotifyMouseEntered();
            int moves = 0;
            view.MoveRequested += (_, _, _) => moves++;
            Vector2 start = Marker(page, camera, index), target = Target(camera, terrain, 230, 180);
            check.That(new Rect2(Vector2.Zero, view.Size).HasPoint(start) && new Rect2(Vector2.Zero, view.Size).HasPoint(target),
                "the authored object and drop point are inside the actual 3D page view");
            byte[] before = session.ToBytes();
            string? undo = session.UndoDescription;
            bool redo = session.CanRedo;
            Vector3 cameraBefore = camera.GlobalPosition;
            Motion(view, start, start, false);
            Button(view, start, true);
            Motion(view, start, start + Vector2.One);
            Button(view, start + Vector2.One, false);
            check.That(moves == 0 && Unchanged(session, before, undo, redo) && camera.GlobalPosition == cameraBefore && page.SelectedRow == index,
                "a click with small pointer jitter selects without moving or creating history");
            Button(view, start, true);
            Motion(view, start, target);
            check.That(moves == 0 && Unchanged(session, before, undo, redo) && camera.GlobalPosition == cameraBefore,
                "drag preview changes neither world history nor the camera before release");
            Button(view, target, false);
            byte[] after = session.ToBytes();
            NumericVector3 moved = session.Body.Things[index].Init.Position;
            NumericVector3 original = WorldBody.Read(before).Things[index].Init.Position;
            WorldBody expected = WorldBody.Read(before);
            expected.Things[index].Init.Position = new NumericVector3(moved.X, moved.Y, original.Z);
            check.That(moves == 1 && !after.SequenceEqual(before) && after.SequenceEqual(expected.Write()) &&
                Math.Abs(moved.X - MapView.ToHundredths(230)) <= 1 && Math.Abs(moved.Y - MapView.ToHundredths(180)) <= 1 &&
                BitConverter.SingleToInt32Bits(moved.Z) == BitConverter.SingleToInt32Bits(original.Z),
                "release makes one guarded XY move and preserves height and all other world bytes");
            ObjectRow shown = page.Map.Rows.Single(row => row.Index == index);
            check.That(shown.Position.X == moved.X && shown.Position.Y == moved.Y &&
                page.X.Text == CoordinateInput.Format(moved.X) && page.Y.Text == CoordinateInput.Format(moved.Y),
                "the same drag refreshes map coordinates and the selected-object inspector");
            if (moves == 1)
                check.That(session.Undo() && session.ToBytes().SequenceEqual(before) && session.Redo() && session.ToBytes().SequenceEqual(after),
                    "one undo restores the complete pre-drag world and one redo restores the drop");
            else check.Fail("one undo restores the complete pre-drag world and one redo restores the drop");

            foreach (string cancellation in new[] { "Escape", "outside", "terrain" })
            {
                await Frames(tree);
                start = Marker(page, camera, index); target = Target(camera, terrain, 270, 210);
                before = session.ToBytes(); undo = session.UndoDescription; redo = session.CanRedo;
                int previousMoves = moves;
                Button(view, start, true); Motion(view, start, target);
                Func<Heightfield?>? provider = view.TerrainProvider;
                if (cancellation == "Escape")
                {
                    view.GetViewport().PushInput(new InputEventKey { Keycode = Key.Escape, PhysicalKeycode = Key.Escape, Pressed = true }, true);
                    view.GetViewport().PushInput(new InputEventKey { Keycode = Key.Escape, PhysicalKeycode = Key.Escape, Pressed = false }, true);
                }
                if (cancellation == "terrain") view.TerrainProvider = () => null;
                Button(view, cancellation == "outside" ? new Vector2(-20, -20) : target, false);
                view.TerrainProvider = provider;
                check.That(moves == previousMoves && Unchanged(session, before, undo, redo),
                    $"{cancellation} cancellation leaves world bytes and undo/redo history unchanged");
            }

            await Frames(tree);
            start = Marker(page, camera, index); target = Target(camera, terrain, 270, 210);
            Button(view, start, true); Motion(view, start, target);
            int movesBeforeChange = moves;
            model.MoveTo(index, MapView.ToHundredths(210), MapView.ToHundredths(240));
            before = session.ToBytes(); undo = session.UndoDescription; redo = session.CanRedo;
            Button(view, target, false);
            check.That(moves == movesBeforeChange && Unchanged(session, before, undo, redo),
                "a changed object invalidates the pending drag before the next process frame");
            await Frames(tree);
            start = Marker(page, camera, index); target = Target(camera, terrain, 270, 210);
            Button(view, start, true); Motion(view, start, target);
            movesBeforeChange = moves;
            if (!model.Open(model.Level!.Value) || model.Session is not { } reopened)
                check.Fail("the authored level reopens for stale-session cancellation");
            else
            {
                before = reopened.ToBytes(); undo = reopened.UndoDescription; redo = reopened.CanRedo;
                Button(view, target, false);
                check.That(moves == movesBeforeChange && Unchanged(reopened, before, undo, redo),
                    "a new session invalidates the pending drag before the next process frame");
            }
            check.That(LevelEditorPageTests.Snapshot(gameRoot).SequenceEqual(files),
                "3D object drag and cancellation never change authored game files");
        }
        finally
        {
            page.Root.QueueFree(); services.Status.Root.QueueFree(); popups.QueueFree();
            await Frames(tree);
        }
    }
}
