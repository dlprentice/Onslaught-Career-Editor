// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>The unit-row control acts only on an authored level fixture; it does not save or stage a mod.</summary>
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
