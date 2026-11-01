// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>The arrangement control and editor page act only on an authored level fixture; they do not save or stage a mod.</summary>
internal static class UnitRowPanelTests
{
    internal static async Task RunAsync(SceneTree tree, string outputDirectory, Checks check)
    {
        check.Suite("unit-row panel");
        UnitRowPanel panel = new();
        panel.Size = new Vector2(460, 700);
        await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        tree.Root.AddChild(panel);
        await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        try
        {
            check.That(panel.Apply.Disabled && panel.SelectAll.Disabled && panel.Note.Text.Contains("Open a level", StringComparison.Ordinal),
                       "with no level there is nothing to arrange");
            LevelEditorModel model = LevelEditorModel.ForGame(LevelEditorTests.GameWithLevels(Path.Combine(outputDirectory, "unit-row-panel")));
            if (model.Levels.Count == 0 || !model.Open(model.Levels[0].Level) || model.Session is null)
            {
                check.Fail("the authored level opens");
                return;
            }
            panel.Bind(model);
            EditSession session = model.Session;
            int[] rows = session.Body.Things.Select((thing, row) => (thing, row)).Where(item => DuplicateObject.CanCopy(item.thing))
                .Select(item => item.row).Take(2).ToArray();
            if (rows.Length < 2 || panel.Units.ItemCount < 2)
            {
                check.Fail("the authored level shows two units");
                return;
            }
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            tree.Root.NotifyMouseEntered();
            Click(tree, panel.Units, 0);
            Click(tree, panel.Units, 1);
            check.That(panel.Units.GetSelectedItems().SequenceEqual([0, 1]) && !panel.Apply.Disabled,
                       "normal clicks toggle multiple units and enable arrangement");
            Click(tree, panel.Units, 0);
            Click(tree, panel.Units, 1);
            check.That(panel.Units.GetSelectedItems().Length == 0 && panel.Apply.Disabled,
                       "clicking selected units again clears them and disables arrangement");
            panel.Units.Select(0, false);
            panel.Units.Select(1, false);
            panel.Units.EmitSignal(ItemList.SignalName.MultiSelected, 1, true);
            check.That(!panel.Apply.Disabled && !panel.UseFirstPosition.Disabled && panel.Units.GetSelectedItems().Length == 2,
                       "the list accepts more than one unit and enables arrangement");
            panel.UseFirstPosition.EmitSignal(BaseButton.SignalName.Pressed);
            check.That(panel.FirstX.Text == CoordinateInput.Format(session.Body.Things[rows[0]].Init.Position.X) &&
                       panel.FirstY.Text == CoordinateInput.Format(session.Body.Things[rows[0]].Init.Position.Y),
                       "the first selected unit can provide the starting position");

            byte[] before = session.ToBytes();
            panel.FirstX.Text = "40"; panel.FirstY.Text = "60"; panel.StepX.Text = "not a number"; panel.StepY.Text = "3";
            panel.Apply.EmitSignal(BaseButton.SignalName.Pressed);
            check.That(panel.Note.Text.StartsWith("X spacing:", StringComparison.Ordinal) && session.ToBytes().SequenceEqual(before) && !session.CanUndo,
                       "an invalid field explains the problem and changes nothing");
            panel.StepX.Text = "12";
            int outcomes = 0;
            panel.ArrangementResult += _ => outcomes++;
            panel.Apply.EmitSignal(BaseButton.SignalName.Pressed);
            byte[] moved = session.ToBytes();
            check.That(session.CanUndo && outcomes == 1 && !moved.SequenceEqual(before) && panel.Units.GetSelectedItems().Length == 2 &&
                       panel.Note.Text.Contains("heights", StringComparison.OrdinalIgnoreCase),
                       "applying arranges the selection as one change and keeps its selection");
            check.That(session.Undo() && session.ToBytes().SequenceEqual(before) && panel.Units.GetSelectedItems().Length == 2,
                       "undo restores the original world and retains the selection in the same session");
            check.That(session.Redo() && session.ToBytes().SequenceEqual(moved) && panel.Units.GetSelectedItems().Length == 2,
                       "redo restores the arrangement in the same session");

            int level = model.Level!.Value;
            check.That(model.Open(level) && panel.Units.GetSelectedItems().Length == 0 && panel.Apply.Disabled &&
                       panel.FirstX.Text.Length == 0 && panel.FirstY.Text.Length == 0,
                       "opening even the same level creates a new session and clears its old selection and first position");
            session = model.Session!;
            rows = session.Body.Things.Select((thing, row) => (thing, row)).Where(item => DuplicateObject.CanCopy(item.thing))
                .Select(item => item.row).Take(2).ToArray();
            panel.Units.Select(0, false); panel.Units.Select(1, false);
            panel.Units.EmitSignal(ItemList.SignalName.MultiSelected, 1, true);
            panel.FirstX.Text = "40"; panel.FirstY.Text = "60"; panel.StepX.Text = "12"; panel.StepY.Text = "3";
            // A model can be modified by another editor control between selection and Apply. A replacement at the same index is not the old unit.
            session.Body.Things[rows[0]] = session.Body.Things[rows[0]].Clone();
            before = session.ToBytes();
            panel.Apply.EmitSignal(BaseButton.SignalName.Pressed);
            check.That(panel.Note.Text.Contains("selection changed", StringComparison.OrdinalIgnoreCase) && panel.Apply.Disabled &&
                       panel.Units.GetSelectedItems().Length == 0 && session.ToBytes().SequenceEqual(before) && !session.CanUndo,
                       "a replaced selected object is rejected and every old selection is cleared");
            await Grid(tree, model, panel, level, check);
            panel.Bind(null);
            check.That(panel.Apply.Disabled && panel.Units.ItemCount == 0, "unbinding clears the units and disables arrangement");
        }
        finally
        {
            panel.QueueFree();
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        }
        await GridOnPage(tree, outputDirectory, check);
    }

    private static async Task Grid(SceneTree tree, LevelEditorModel model, UnitRowPanel panel, int level, Checks check)
    {
        if (!model.Open(level) || model.Session is null) { check.Fail("the authored level reopens for grid placement"); return; }
        EditSession session = model.Session;
        int source = session.Body.Things.FindIndex(DuplicateObject.CanCopy);
        if (source < 0 || model.Duplicate(source).Row is null || model.Duplicate(source).Row is null)
        {
            check.Fail("the authored level provides four units for the grid");
            return;
        }
        int[] rows = session.Body.Things.Select((thing, index) => (thing, index))
            .Where(pair => DuplicateObject.CanCopy(pair.thing)).Select(pair => pair.index).Take(4).ToArray();
        if (rows.Length != 4 || panel.Units.ItemCount < 4) { check.Fail("four authored units are listed"); return; }
        check.That(panel.Layout.Selected == 0 && !panel.GridOptionsVisible,
                   "the existing single-row layout remains the default");
        bool choseGrid = await ChooseLayout(tree, panel.Layout, "ui_down");
        check.That(choseGrid && panel.Layout.Selected == 1 && panel.GridOptionsVisible &&
                   panel.Columns.Text == "2" && panel.RowX.Text == "0" && panel.RowY.Text == "10",
                   "a real layout selection exposes clear two-column and row-offset defaults");
        if (!choseGrid || panel.Layout.Selected != 1) return;
        bool choseRow = await ChooseLayout(tree, panel.Layout, "ui_up");
        check.That(choseRow && panel.Layout.Selected == 0 && !panel.GridOptionsVisible,
                   "switching back to a row hides the grid-only fields");
        if (!choseRow || panel.Layout.Selected != 0) return;
        choseGrid = await ChooseLayout(tree, panel.Layout, "ui_down");
        if (!choseGrid || panel.Layout.Selected != 1) { check.Fail("the grid layout can be selected again"); return; }
        for (int i = 0; i < 4; i++) Click(tree, panel.Units, i);
        check.That(panel.Units.GetSelectedItems().SequenceEqual([0, 1, 2, 3]) && !panel.Apply.Disabled,
                   "normal clicks select the four units for a grid");
        panel.FirstX.Text = "40"; panel.FirstY.Text = "60";
        panel.StepX.Text = "12"; panel.StepY.Text = "3";
        panel.RowX.Text = "-4"; panel.RowY.Text = "18";
        byte[] before = session.ToBytes();
        string? history = session.UndoDescription;
        foreach (string invalid in new[] { "", "0", "5", "2.5", "-1", "no" })
        {
            panel.Columns.Text = invalid;
            panel.Apply.EmitSignal(BaseButton.SignalName.Pressed);
            if (!session.ToBytes().SequenceEqual(before) || session.UndoDescription != history || !panel.Note.Text.Contains("whole number", StringComparison.Ordinal))
            {
                check.Fail("invalid grid columns are refused without changing the world or undo history");
                return;
            }
        }
        check.That(true, "invalid grid columns are refused without changing the world or undo history");
        panel.Columns.Text = "2";
        panel.RowY.Text = "not a number";
        panel.Apply.EmitSignal(BaseButton.SignalName.Pressed);
        check.That(panel.Note.Text.StartsWith("Next row offset Y:", StringComparison.Ordinal) && session.ToBytes().SequenceEqual(before) && session.UndoDescription == history,
                   "invalid row offsets explain the problem and change nothing");
        panel.RowY.Text = "18";
        panel.FirstX.Text = "510";
        panel.Apply.EmitSignal(BaseButton.SignalName.Pressed);
        check.That(panel.Note.Text.Contains("inside the terrain", StringComparison.Ordinal) && session.ToBytes().SequenceEqual(before) && session.UndoDescription == history,
                   "a grid outside the terrain is refused atomically");
        panel.FirstX.Text = "40";
        panel.RowX.Text = "12"; panel.RowY.Text = "3";
        panel.Apply.EmitSignal(BaseButton.SignalName.Pressed);
        check.That(panel.Note.Text.Contains("different position", StringComparison.Ordinal) && session.ToBytes().SequenceEqual(before) && session.UndoDescription == history,
                   "overlapping grid positions are refused atomically");
        panel.RowX.Text = "-4"; panel.RowY.Text = "18";
        WorldBody expected = WorldBody.Read(before);
        for (int i = 0; i < rows.Length; i++)
        {
            System.Numerics.Vector3 original = expected.Things[rows[i]].Init.Position;
            expected.Things[rows[i]].Init.Position = new(40 + 12 * (i % 2) - 4 * (i / 2),
                60 + 3 * (i % 2) + 18 * (i / 2), original.Z);
        }
        await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        ClickButton(tree, panel.Apply);
        byte[] moved = session.ToBytes();
        check.That(moved.SequenceEqual(expected.Write()) && session.UndoDescription == "Arrange units in a grid" &&
                   panel.Note.Text.Contains("heights", StringComparison.OrdinalIgnoreCase) && panel.Units.GetSelectedItems().Length == 4,
                   "a real mouse click arranges four selected units in two rows as one edit");
        check.That(session.Undo() && session.ToBytes().SequenceEqual(before) && panel.Units.GetSelectedItems().Length == 4,
                   "one undo restores the whole grid while preserving the selection");
        check.That(session.Redo() && session.ToBytes().SequenceEqual(moved) && panel.Units.GetSelectedItems().Length == 4,
                   "one redo restores the whole grid while preserving the selection");
        panel.Apply.EmitSignal(BaseButton.SignalName.Pressed);
        check.That(panel.Note.Text.Contains("already", StringComparison.OrdinalIgnoreCase) && session.Undo() && session.ToBytes().SequenceEqual(before),
                   "an unchanged grid adds no extra undo step");
        check.That(session.CanRedo, "the grid can be redone after the unchanged request");
        session.Body.Things[rows[0]] = session.Body.Things[rows[0]].Clone();
        byte[] stale = session.ToBytes();
        panel.Apply.EmitSignal(BaseButton.SignalName.Pressed);
        check.That(panel.Note.Text.Contains("selection changed", StringComparison.OrdinalIgnoreCase) && session.ToBytes().SequenceEqual(stale) && session.CanRedo,
                   "a replaced unit invalidates the grid selection without losing redo");
    }

    private static async Task GridOnPage(SceneTree tree, string outputDirectory, Checks check)
    {
        string scratch = Path.Combine(outputDirectory, "grid-page-authored");
        string gameRoot = LevelEditorTests.GameWithLevels(scratch);
        string[] files = Directory.GetFiles(gameRoot, "*", SearchOption.AllDirectories).Order().ToArray();
        byte[][] originals = files.Select(File.ReadAllBytes).ToArray();
        SettingsStore settings = new(Path.Combine(scratch, "settings.json"));
        GameLibrary game = new([], settings, ceUserFolder: "", ceEnvironment: _ => null);
        GameFolder folder = GameFolder.Inspect(gameRoot, "Authored test fixture");
        typeof(GameLibrary).GetProperty(nameof(GameLibrary.Folder))!.SetValue(game, folder);
        Control popups = new();
        tree.Root.AddChild(popups);
        AppServices services = new()
        {
            Workspace = null!, Game = game, Status = new StatusLine(), Backups = null!,
            GameRunning = () => false, OpenUrl = _ => { }, Navigate = _ => { }, OpenCareer = null!, ChooseCareer = null!,
            OpenCareerFile = () => { }, AskToDiscard = (_, _, _) => { }, LevelEditsUnsaved = () => 0,
            Play = new CePlay(game, Path.Combine(scratch, "unused-play")), Popups = popups, CatchUp = () => Task.CompletedTask,
        };
        // The application initializes its shared fonts before constructing pages.
        Theme theme = CompanionTheme.Build();
        LevelEditorPage page = new(services);
        page.Root.Theme = theme;
        page.Root.Size = new Vector2(1024, 768);
        tree.Root.AddChild(page.Root);
        try
        {
            page.Refresh();
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            if (page.Model?.Session is not EditSession session || page.UnitRowsToggle.Disabled)
            {
                check.Fail("the real editor page opens an authored level and offers unit arrangement");
                return;
            }
            int source = session.Body.Things.FindIndex(DuplicateObject.CanCopy);
            if (source < 0 || page.Model.Duplicate(source).Row is null || page.Model.Duplicate(source).Row is null)
            {
                check.Fail("the real page fixture provides four authored units");
                return;
            }
            int[] rows = session.Body.Things.Select((thing, index) => (thing, index))
                .Where(pair => DuplicateObject.CanCopy(pair.thing)).Select(pair => pair.index).Take(4).ToArray();
            ScrollContainer? side = page.UnitRowsToggle.GetParent() as ScrollContainer;
            Node? parent = page.UnitRowsToggle.GetParent();
            while (side is null && parent is not null) { parent = parent.GetParent(); side = parent as ScrollContainer; }
            if (rows.Length != 4 || side is null) { check.Fail("the page exposes its arrangement panel inside a scrollable column"); return; }
            side.EnsureControlVisible(page.UnitRowsToggle);
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            ClickButton(tree, page.UnitRowsToggle);
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            check.That(page.UnitRowsToggle.ButtonPressed && page.UnitRows.Visible,
                       "a real click opens arrangement from the editor page");
            if (!page.UnitRows.Visible) return;
            side.EnsureControlVisible(page.UnitRows.Layout);
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            bool choseGrid = await ChooseLayout(tree, page.UnitRows.Layout, "ui_down");
            check.That(choseGrid && page.UnitRows.Layout.Selected == 1 && page.UnitRows.GridOptionsVisible,
                       "the real page exposes grid fields through normal layout input");
            if (!choseGrid || page.UnitRows.Layout.Selected != 1) return;
            side.EnsureControlVisible(page.UnitRows.Units);
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            for (int i = 0; i < 4; i++) Click(tree, page.UnitRows.Units, i);
            if (page.UnitRows.Units.GetSelectedItems().Length != 4) { check.Fail("the real page selects four authored units"); return; }
            page.UnitRows.FirstX.Text = "40"; page.UnitRows.FirstY.Text = "60";
            page.UnitRows.StepX.Text = "12"; page.UnitRows.StepY.Text = "3";
            page.UnitRows.Columns.Text = "2"; page.UnitRows.RowX.Text = "-4"; page.UnitRows.RowY.Text = "18";
            byte[] before = session.ToBytes();
            WorldBody expected = WorldBody.Read(before);
            for (int i = 0; i < rows.Length; i++)
            {
                System.Numerics.Vector3 old = expected.Things[rows[i]].Init.Position;
                expected.Things[rows[i]].Init.Position = new(40 + 12 * (i % 2) - 4 * (i / 2),
                    60 + 3 * (i % 2) + 18 * (i / 2), old.Z);
            }
            side.EnsureControlVisible(page.UnitRows.Apply);
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
            ClickButton(tree, page.UnitRows.Apply);
            byte[] after = session.ToBytes();
            check.That(after.SequenceEqual(expected.Write()) && page.Map.Rows.Count == session.Body.Things.Count &&
                       session.UndoDescription == "Arrange units in a grid",
                       "the real page applies the grid as one edit and refreshes its map");
            check.That(session.Undo() && session.ToBytes().SequenceEqual(before) && session.Redo() && session.ToBytes().SequenceEqual(after),
                       "the real page's grid edit can be undone and redone");
            check.That(files.SequenceEqual(Directory.GetFiles(gameRoot, "*", SearchOption.AllDirectories).Order()) &&
                       files.Select((path, index) => File.ReadAllBytes(path).SequenceEqual(originals[index])).All(same => same),
                       "the authored game-data fixture stays unchanged throughout the page interaction");
        }
        finally
        {
            page.Root.QueueFree();
            services.Status.Root.QueueFree();
            popups.QueueFree();
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        }
    }

    private static async Task<bool> ChooseLayout(SceneTree tree, OptionButton layout, string direction)
    {
        ClickButton(tree, layout);
        await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        PopupMenu popup = layout.GetPopup();
        if (!popup.Visible) return false;
        Key key = direction == "ui_down" ? Key.Down : Key.Up;
        for (int i = 0; i < 2; i++)
        {
            tree.Root.PushInput(new InputEventKey { Keycode = key, PhysicalKeycode = key, Pressed = true });
            tree.Root.PushInput(new InputEventKey { Keycode = key, PhysicalKeycode = key, Pressed = false });
        }
        tree.Root.PushInput(new InputEventKey { Keycode = Key.Enter, PhysicalKeycode = Key.Enter, Pressed = true });
        tree.Root.PushInput(new InputEventKey { Keycode = Key.Enter, PhysicalKeycode = Key.Enter, Pressed = false });
        await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        return !popup.Visible;
    }

    private static void ClickButton(SceneTree tree, Button button)
    {
        Vector2 point = button.GlobalPosition + button.Size / 2;
        tree.Root.PushInput(new InputEventMouseMotion { Position = point, GlobalPosition = point });
        tree.Root.PushInput(new InputEventMouseButton { Position = point, GlobalPosition = point, ButtonIndex = MouseButton.Left, Pressed = true });
        tree.Root.PushInput(new InputEventMouseButton { Position = point, GlobalPosition = point, ButtonIndex = MouseButton.Left, Pressed = false });
    }

    private static void Click(SceneTree tree, ItemList list, int item)
    {
        Vector2 point = list.GlobalPosition + list.GetItemRect(item).GetCenter();
        tree.Root.PushInput(new InputEventMouseMotion { Position = point, GlobalPosition = point });
        tree.Root.PushInput(new InputEventMouseButton { Position = point, GlobalPosition = point, ButtonIndex = MouseButton.Left, Pressed = true });
        tree.Root.PushInput(new InputEventMouseButton { Position = point, GlobalPosition = point, ButtonIndex = MouseButton.Left, Pressed = false });
    }
}
