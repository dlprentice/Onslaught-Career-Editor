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
            panel.Bind(null);
            check.That(panel.Apply.Disabled && panel.Units.ItemCount == 0, "unbinding clears the units and disables arrangement");
        }
        finally
        {
            panel.QueueFree();
            await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
        }
    }

    private static void Click(SceneTree tree, ItemList list, int item)
    {
        Vector2 point = list.GlobalPosition + list.GetItemRect(item).GetCenter();
        tree.Root.NotifyMouseEntered();
        tree.Root.PushInput(new InputEventMouseMotion { Position = point, GlobalPosition = point });
        tree.Root.PushInput(new InputEventMouseButton { Position = point, GlobalPosition = point, ButtonIndex = MouseButton.Left, Pressed = true });
        tree.Root.PushInput(new InputEventMouseButton { Position = point, GlobalPosition = point, ButtonIndex = MouseButton.Left, Pressed = false });
    }
}
