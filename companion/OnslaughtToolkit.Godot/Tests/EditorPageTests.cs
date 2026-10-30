// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;
using Vector3 = System.Numerics.Vector3;
using System.Security.Cryptography;
using Godot;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// The Level editor page driven in the code-built interface on a fake install holding authored level archives: choose a level, select
/// an object, type coordinates, undo, redo, reset, and save the edit as a mod through the dialog; and the page never writing into the
/// game. Authored data only (the archives are tools/level_editor_vectors.py's); nothing retail.
/// </summary>
internal static class LevelEditorPageTests
{
    private static SignalAwaiter Frame(SceneTree tree) => tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);

    private static byte[] Archive(string name) => LevelTests.Unpack(LevelVectors.Archives.First(archive => archive.Name == name).File);

    private static uint Bits(float value) => BitConverter.SingleToUInt32Bits(value);

    /// <summary>Every file under a folder with its SHA-256, to see that nothing changed.</summary>
    internal static string[] Snapshot(string root) => [.. Directory.EnumerateFiles(root, "*", SearchOption.AllDirectories).Order(StringComparer.Ordinal)
        .Select(path => Path.GetRelativePath(root, path) + " " + Convert.ToHexStringLower(SHA256.HashData(File.ReadAllBytes(path))))];

    private static TreeItem? Row(LevelEditorPage page, int index)
    {
        for (TreeItem? item = page.Table.GetRoot()?.GetFirstChild(); item is not null; item = item.GetNext())
            if (item.GetMetadata(0).AsInt32() == index) return item;
        return null;
    }

    private static void Set(LineEdit field, string text) => field.Text = text;

    private static LevelEditorModel M(LevelEditorPage page) => page.Model!;

    private static void Submit(LineEdit field) => field.EmitSignal(LineEdit.SignalName.TextSubmitted, field.Text);

    private static void Edited(LineEdit field) => field.EmitSignal(LineEdit.SignalName.TextChanged, field.Text);

    private static void Press(BaseButton button) => button.EmitSignal(BaseButton.SignalName.Pressed);

    private static void Choose(LevelEditorPage page, int level)
    {
        for (int i = 0; i < page.Level.ItemCount; i++)
        {
            if (page.Level.GetItemId(i) != level) continue;
            page.Level.Select(i);
            page.Level.EmitSignal(OptionButton.SignalName.ItemSelected, (long)i);
            return;
        }
    }

    /// <summary>
    /// What happens to a move no Save as mod has written when the player closes the companion, picks another level, switches games or
    /// chooses another game folder: the page asks first, a cancelled question keeps the move, and a saved move is not asked about.
    /// </summary>
    internal static async Task UnsavedAsync(CompanionApp app, SceneTree tree, FakeInstall install, string outputDirectory, CompanionUiTests.Flag quit, Checks check)
    {
        check.Suite("level editor unsaved changes");
        LevelEditorPage page = app.LevelEditor;
        foreach (Window window in app.FindChildren("*", nameof(Window), true, false).OfType<Window>().Where(window => window.Visible)) window.Hide();
        app.Navigate("levels");
        await Frame(tree);
        check.That(page.OpenLevel(100) && !page.HasChanges && page.ChangeCount == 0, "a level just opened holds nothing unsaved");
        quit.On = false;
        check.That(app.RequestClose() && quit.On && !app.DiscardDialog.Visible, "with nothing moved on the Level editor, closing does not ask");
        quit.On = false;

        // Closing asks, and a cancelled question keeps the move.
        page.SelectRow(1);
        Set(page.X, "7");
        Set(page.Y, "8");
        Set(page.Z, "9");
        Submit(page.X);
        check.That(page.HasChanges && page.ChangeCount == 1 && !page.Undo.Disabled, "a typed move is unsaved");
        check.That(!app.RequestClose() && app.DiscardDialog.Visible && app.DiscardDialog.DialogText.StartsWith("Not saved yet: 1 change on Level editor.", StringComparison.Ordinal) && !quit.On,
            $"closing with an unsaved move asks first and does not close: \"{app.DiscardDialog.DialogText}\"");
        app.DiscardDialog.EmitSignal(AcceptDialog.SignalName.Canceled);
        app.DiscardDialog.Hide();
        check.That(page.HasChanges && !quit.On && M(page).Session!.Changes().Count == 1, "a cancelled question keeps the move and the companion open");
        check.That(!app.RequestClose() && app.DiscardDialog.Visible, "closing asks again");
        app.DiscardDialog.EmitSignal(AcceptDialog.SignalName.Confirmed);
        check.That(quit.On, "agreeing to discard closes the companion");
        quit.On = false;
        app.DiscardDialog.Hide();

        // Together with the other pages' changes, and from another page (leaving and coming back kept the move already).
        app.Navigate("home");
        check.That(!app.RequestClose() && app.DiscardDialog.Visible && app.DiscardDialog.DialogText.Contains("1 change on Level editor", StringComparison.Ordinal), "closing asks about the Level editor from any page");
        app.DiscardDialog.EmitSignal(AcceptDialog.SignalName.Canceled);
        app.DiscardDialog.Hide();
        app.Navigate("levels");
        await Frame(tree);

        // The picker asks before it drops the move; the question leaves the picker on the open level, and agreeing opens the other.
        Choose(page, 200);
        check.That(app.DiscardDialog.Visible && app.DiscardDialog.DialogText.StartsWith("1 change on level 100 is not saved. Open level 200 and discard it?", StringComparison.Ordinal) && page.Model?.Level == 100 &&
                   page.Level.GetItemId(page.Level.Selected) == 100 && page.HasChanges, $"choosing another level asks first, and the picker keeps showing the open one: \"{app.DiscardDialog.DialogText}\"");
        app.DiscardDialog.EmitSignal(AcceptDialog.SignalName.Canceled);
        app.DiscardDialog.Hide();
        check.That(page.Model?.Level == 100 && page.HasChanges && page.Level.GetItemId(page.Level.Selected) == 100 && M(page).Row(1)!.Position == new System.Numerics.Vector3(7f, 8f, 9f), "a cancelled question keeps the level and the move");
        Choose(page, 100);
        check.That(app.DiscardDialog.Visible && page.HasChanges, "choosing the open level again asks too, since it would be read afresh");
        app.DiscardDialog.EmitSignal(AcceptDialog.SignalName.Canceled);
        app.DiscardDialog.Hide();
        Choose(page, 200);
        app.DiscardDialog.EmitSignal(AcceptDialog.SignalName.Confirmed);
        await Frame(tree);
        check.That(page.Model?.Level == 200 && !page.HasChanges && page.Level.GetItemId(page.Level.Selected) == 200 && M(page).Session!.Changes().Count == 0, "after the player agrees, the other level opens and the move is dropped");
        app.DiscardDialog.Hide();

        // Switching games asks too (it is refused until the move is saved or undone, as with a career), and the move stays.
        Choose(page, 100);
        await Frame(tree);
        page.SelectRow(1);
        Set(page.X, "7");
        Submit(page.X);
        check.That(page.HasChanges, "a move on a level opened again is unsaved");
        await app.SelectTargetAsync(GameTarget.OnslaughtCe);
        check.That(app.Status.Label.Text.Contains("Save or undo your career, settings and level changes", StringComparison.Ordinal) && app.Game.Target == GameTarget.Original && page.HasChanges && page.Model?.Level == 100,
            $"switching games is refused while a level move is unsaved, and the move stays: \"{app.Status.Label.Text}\"");

        // Choosing another game folder starts the page over, so it asks first.
        await app.Home.ChooseAsync(install.Game);
        check.That(app.DiscardDialog.Visible && app.DiscardDialog.DialogText.StartsWith("1 change on the Level editor is not saved. Use ", StringComparison.Ordinal) && app.DiscardDialog.DialogText.EndsWith("as the game folder and discard it?", StringComparison.Ordinal) && page.HasChanges,
            $"choosing a game folder asks first: \"{app.DiscardDialog.DialogText}\"");
        app.DiscardDialog.EmitSignal(AcceptDialog.SignalName.Canceled);
        app.DiscardDialog.Hide();
        check.That(page.HasChanges && page.Model?.Level == 100, "a cancelled question keeps the move");

        // A move that Save as mod has written is not asked about: not on close, not on a level switch; and a move made after the save is.
        string saveFolder = Path.Combine(outputDirectory, "ui-level-unsaved-mods");
        app.Navigate("levels");
        await Frame(tree);
        page.SaveDialog.Begin(100, saveFolder);
        check.That(page.SaveNow().Ok && !page.HasChanges && page.ChangeCount == 0 && M(page).Session!.Changes().Count == 1, "saving the move as a mod leaves nothing unsaved, and the page still holds the edit");
        check.That(app.RequestClose() && quit.On && !app.DiscardDialog.Visible, "a saved move is not asked about on close");
        quit.On = false;
        page.SelectRow(2);
        Set(page.X, "11");
        Set(page.Y, "12");
        Set(page.Z, "13");
        Submit(page.X);
        check.That(page.HasChanges && page.ChangeCount == 2 && !app.RequestClose() && app.DiscardDialog.DialogText.Contains("2 changes on Level editor", StringComparison.Ordinal), $"a move made after the save is unsaved, counted with the saved one: \"{app.DiscardDialog.DialogText}\"");
        app.DiscardDialog.EmitSignal(AcceptDialog.SignalName.Canceled);
        app.DiscardDialog.Hide();
        Press(page.Undo);
        check.That(!page.HasChanges && app.RequestClose() && quit.On, "undone back to what was saved, nothing is unsaved");
        quit.On = false;
        Choose(page, 200);
        check.That(!app.DiscardDialog.Visible && page.Model?.Level == 200, "and then another level opens without a question");

        // The same three exit routes must protect an unstorable script edit, without treating it as a moved object.
        Choose(page, 100);
        await Frame(tree);
        EditSession scriptSession = M(page).Session!;
        MissionScript unstorable = scriptSession.ShippedScript(0);
        unstorable.Trailer = new byte[9];
        scriptSession.Apply(new ReplaceScript(0, unstorable));
        await Frame(tree);
        check.That(page.HasChanges && page.ChangeCount == 1 && page.Save.Disabled && page.Summary.Contains("cannot be saved:", StringComparison.Ordinal),
            "an unstorable script is shown as an unsaved change and cannot be saved");
        check.That(!app.RequestClose() && app.DiscardDialog.DialogText.Contains("1 change on Level editor", StringComparison.Ordinal),
            "closing asks before dropping an unstorable script edit");
        app.DiscardDialog.EmitSignal(AcceptDialog.SignalName.Canceled);
        app.DiscardDialog.Hide();
        Choose(page, 200);
        check.That(app.DiscardDialog.Visible && app.DiscardDialog.DialogText.Contains("1 change on level 100", StringComparison.Ordinal) && page.Model?.Level == 100,
            "the level picker asks before dropping an unstorable script edit");
        app.DiscardDialog.EmitSignal(AcceptDialog.SignalName.Canceled);
        app.DiscardDialog.Hide();
        await app.Home.ChooseAsync(install.Game);
        check.That(app.DiscardDialog.Visible && app.DiscardDialog.DialogText.Contains("1 change on the Level editor", StringComparison.Ordinal) && page.HasChanges,
            "changing the game folder asks before dropping an unstorable script edit");
        app.DiscardDialog.EmitSignal(AcceptDialog.SignalName.Canceled);
        app.DiscardDialog.Hide();
        check.That(scriptSession.Undo() && !page.HasChanges, "undoing the unstorable script leaves nothing to discard");

        // A caller can mutate the public working body into a state the editor refuses to save. Every exit must still protect it.
        MissionScript replacement = scriptSession.ShippedScript(0);
        replacement.Trailer[0]++;
        scriptSession.Apply(new ReplaceScript(0, replacement));
        scriptSession.Body.Scripts[0].Name = "renamed";
        check.That(page.HasChanges && !app.RequestClose() && app.DiscardDialog.Visible, "closing asks before dropping a renamed script list");
        app.DiscardDialog.EmitSignal(AcceptDialog.SignalName.Canceled);
        app.DiscardDialog.Hide();
        Choose(page, 200);
        check.That(app.DiscardDialog.Visible && page.Model?.Level == 100, "the level picker asks before dropping a renamed script list");
        app.DiscardDialog.EmitSignal(AcceptDialog.SignalName.Canceled);
        app.DiscardDialog.Hide();
        await app.Home.ChooseAsync(install.Game);
        check.That(app.DiscardDialog.Visible && page.HasChanges, "changing the game folder asks before dropping a renamed script list");
        app.DiscardDialog.EmitSignal(AcceptDialog.SignalName.Canceled);
        app.DiscardDialog.Hide();
        check.That(scriptSession.Undo() && !page.HasChanges, "undo restores the baseline after a refused script-list change");
        app.Navigate("home");
        await Frame(tree);
    }

    /// <summary>Copying a unit on the page: the button's states, the copy selected at once and listed, moved like any row, undone, redone and asked about before it is dropped.</summary>
    internal static async Task CopyAsync(CompanionApp app, SceneTree tree, CompanionUiTests.Flag quit, Checks check)
    {
        check.Suite("level editor copying units");
        LevelEditorPage page = app.LevelEditor;
        foreach (Window window in app.FindChildren("*", nameof(Window), true, false).OfType<Window>().Where(window => window.Visible)) window.Hide();
        app.Navigate("levels");
        await Frame(tree);
        check.That(page.OpenLevel(100) && !page.HasChanges, "level 100 is open with nothing changed");
        int count = page.Table.GetRoot()!.GetChildCount();
        check.That(page.Duplicate.Disabled && page.Duplicate.TooltipText == "Choose an object first.", "with nothing selected the copy button is off and says why");
        page.SelectRow(2);
        check.That(page.Duplicate.Disabled && page.Duplicate.TooltipText.StartsWith("Only units can be copied for now", StringComparison.Ordinal), $"a path point cannot be copied, and the button says so: \"{page.Duplicate.TooltipText}\"");
        check.That(page.DuplicateSelected() is { Row: null } refused && !refused.Message.StartsWith("Open", StringComparison.Ordinal) && !page.HasChanges && page.Table.GetRoot()!.GetChildCount() == count && page.Note.StartsWith("Only units can be copied", StringComparison.Ordinal),
            "pressing it anyway adds nothing and says why");

        page.SelectRow(0);
        check.That(!page.Duplicate.Disabled && page.Reset.Disabled && page.Duplicate.TooltipText.StartsWith("Add a copy of this unit", StringComparison.Ordinal), "a unit can be copied");
        Press(page.Duplicate);
        await Frame(tree);
        check.That(page.Table.GetRoot()!.GetChildCount() == count + 1 && page.SelectedRow == count && page.SelectedName == "Tank 1 copy" && page.Map.Selected == count &&
                   page.X.Text == "20" && page.Y.Text == "20" && page.Z.Text == "0" && page.Reset.Disabled && !page.Duplicate.Disabled && page.Note.StartsWith("Tank 1 (row 0) copied as row ", StringComparison.Ordinal),
            $"the copy is a new row at the end, selected at once, 10 units to the right of the original: \"{page.Note}\"");
        check.That(Row(page, count) is { } added && added.GetText(1) == "unit" && added.GetText(2) == "Tank 1 copy" && added.GetText(3) == "20" && page.HasChanges && page.ChangeCount == 1 && !page.Save.Disabled && !page.Undo.Disabled &&
                   page.Summary.StartsWith("1 unit copied: Tank 1 copy", StringComparison.Ordinal),
            $"the copy is listed, counts as one unsaved change, can be saved and undone, and the changes box says so: \"{page.Summary}\"");

        // The copy moves like any row, and that is still one change.
        Set(page.X, "33");
        Submit(page.X);
        check.That(M(page).Row(count)!.Position.X == 33f && page.ChangeCount == 1 && page.Summary.StartsWith("1 unit copied", StringComparison.Ordinal) && page.Reset.Disabled, "moving the copy does not add a change, and a copy cannot be reset");
        page.ChangedOnly.ButtonPressed = true;
        check.That(page.Table.GetRoot()!.GetChildCount() == 1 && Row(page, count) is not null && page.SelectedRow == count, "the list of changed rows holds the copy");
        page.ChangedOnly.ButtonPressed = false;

        // Closing asks about it.
        quit.On = false;
        check.That(!app.RequestClose() && app.DiscardDialog.Visible && app.DiscardDialog.DialogText.StartsWith("Not saved yet: 1 change on Level editor.", StringComparison.Ordinal) && !quit.On,
            $"closing with a copy not saved asks first: \"{app.DiscardDialog.DialogText}\"");
        app.DiscardDialog.EmitSignal(AcceptDialog.SignalName.Canceled);
        app.DiscardDialog.Hide();

        // Undo takes the move and then the copy back; the selection that pointed at the copy goes with it.
        Press(page.Undo);
        check.That(M(page).Row(count)!.Position.X == 20f && page.Table.GetRoot()!.GetChildCount() == count + 1, "undo takes the move of the copy back first");
        Press(page.Undo);
        await Frame(tree);
        check.That(page.Table.GetRoot()!.GetChildCount() == count && page.SelectedRow is null && page.Map.Selected is null && page.Duplicate.Disabled && page.X.Editable == false && !page.HasChanges && page.Save.Disabled,
            "undo then takes the copy away: the row is gone, nothing is selected, nothing is unsaved");
        Press(page.Redo);
        Press(page.Redo);
        await Frame(tree);
        check.That(page.Table.GetRoot()!.GetChildCount() == count + 1 && M(page).Row(count)!.Position.X == 33f && page.ChangeCount == 1 && page.Summary.StartsWith("1 unit copied", StringComparison.Ordinal), "redo makes the copy and its move again");

        // Starting over (Reset all, if the page has it) or opening another level asks, and agreeing drops the copy.
        Choose(page, 200);
        check.That(app.DiscardDialog.Visible && app.DiscardDialog.DialogText.Contains("1 change on level 100", StringComparison.Ordinal) && page.Model?.Level == 100, "the level picker asks before dropping a copy");
        app.DiscardDialog.EmitSignal(AcceptDialog.SignalName.Confirmed);
        app.DiscardDialog.Hide();
        await Frame(tree);
        check.That(page.Model?.Level == 200 && !page.HasChanges && page.SelectedRow is null, "agreeing opens the other level with nothing left over");
        app.Navigate("home");
        await Frame(tree);
    }

    internal static async Task RunAsync(CompanionApp app, SceneTree tree, FakeInstall install, string outputDirectory, Checks check)
    {
        LevelEditorPage page = app.LevelEditor;
        app.Navigate("levels");
        await Frame(tree);
        check.That(app.Current == page && page.Root.Visible && app.PageTitle.Text == "LEVEL EDITOR" && page.Level.ItemCount == 1 && page.Save.Disabled && page.Undo.Disabled && page.Redo.Disabled &&
                   page.Table.GetRoot()?.GetChildCount() == 0 && !page.X.Editable && page.EmptyVisible, "a game with no level archives offers no level and nothing to edit, and says so");

        // Level archives appear in the game: the page lists them when it is shown again.
        string resources = Path.Combine(install.Game, "data", "resources");
        Directory.CreateDirectory(resources);
        File.WriteAllBytes(Path.Combine(resources, "100_res_PC.aya"), Archive("level-100"));
        File.WriteAllBytes(Path.Combine(resources, "200_res_PC.aya"), Archive("base-and-real"));
        File.WriteAllBytes(Path.Combine(resources, "300_res_PC.aya"), Archive("real-only"));  // its WDAT names level 200
        string[] gameBefore = Snapshot(install.Game);
        WorldBody body = WorldBody.Read(LevelTests.Body("authored-v50"));
        app.Navigate("home");
        app.Navigate("levels");
        await Frame(tree);
        check.That(page.Level.ItemCount == 4 && page.Level.GetItemId(1) == 100 && page.Level.GetItemText(1) == "100" && page.Level.IsItemDisabled(0) && !page.EmptyVisible &&
                   page.Level.Selected == 1 && page.Model?.Level == 100 && page.Table.GetRoot()?.GetChildCount() == body.Things.Count,
            "the game's level archives are listed, and the training level, 100, is open at once rather than an empty table");

        // Choose level 100 again: its own world's objects are the rows.
        Choose(page, 100);
        await Frame(tree);
        check.That(page.Model?.Level == 100 && page.Problem.Length == 0 && page.Table.GetRoot()?.GetChildCount() == body.Things.Count && app.PageSubtitle.Text == $"Level 100 · {Build.Count(body.Things.Count, "object")} · {Build.Count(body.Scripts.Count, "script")}",
            $"choosing a level lists its objects: {page.Table.GetRoot()?.GetChildCount()} rows, \"{app.PageSubtitle.Text}\"");
        check.That(Row(page, 0) is { } first && first.GetText(0) == "0" && first.GetText(1) == "unit" && first.GetText(2) == "Tank 1" && first.GetText(3) == "10" && first.GetText(4) == "20" && first.GetText(5) == "0" &&
                   Row(page, 1) is { } ghost && ghost.GetText(2) == "Ghost" && Row(page, 2) is { } waypoint && waypoint.GetText(2) == "—",
            "a row shows its number, kind, name and position; an unnamed thing shows its definition, or a dash when it has none");
        check.That(page.Summary.StartsWith("No changes yet", StringComparison.Ordinal) && page.Save.Disabled && page.Undo.Disabled && !page.X.Editable && page.Apply.Disabled, "nothing is selected and nothing is changed yet");

        // Search keeps rows by name, kind, script or number.
        page.Search.Text = "tank";
        Edited(page.Search);
        check.That(Row(page, 0) is not null && Row(page, 2) is null && page.Table.GetRoot()!.GetChildCount() >= 1, "a search keeps the rows that match");
        page.Search.Text = "";
        Edited(page.Search);
        check.That(page.Table.GetRoot()!.GetChildCount() == body.Things.Count, "clearing the search brings every row back");

        // Select an object.
        check.That(page.SelectRow(0) && page.X.Editable && page.X.Text == "10" && page.Y.Text == "20" && page.Z.Text == "0" && page.SelectedName == "Tank 1" && !page.Apply.Disabled && page.Reset.Disabled,
            "selecting a row fills the coordinate fields with what is stored");

        // Type coordinates: the move is made, shown in the table, and can be undone.
        Set(page.X, "12.5");
        Set(page.Y, "-40");
        Set(page.Z, "3");
        Submit(page.X);
        check.That(page.Note == "Tank 1 (row 0) now stands at 12.5, -40, 3." && Row(page, 0)!.GetText(3) == "12.5" && Row(page, 0)!.GetText(4) == "-40" && page.X.Text == "12.5" && page.Y.Text == "-40" &&
                   page.Z.Text == "3" && !page.Undo.Disabled && page.Redo.Disabled && !page.Save.Disabled && !page.Reset.Disabled,
            $"typing coordinates and pressing Enter moves the object: \"{page.Note}\"");
        check.That(page.Summary.StartsWith("1 object moved: Tank 1 (row 0), 60.1 units", StringComparison.Ordinal) && page.Warnings.Contains("outside the 0 to 512 square", StringComparison.Ordinal) && !page.Save.Disabled,
            $"the changes are summarised, and a position outside the terrain's square is a warning that does not stop saving: \"{page.Summary}\" / \"{page.Warnings}\"");

        // "List only the moved objects": the table holds just the moved rows, a search narrows it, an empty list says so, and the filter goes away when another level opens.
        check.That(!page.ChangedOnly.Disabled && !page.ChangedOnly.ButtonPressed && page.FilterNote.Length == 0, "with a level open the switch is there, off, and says nothing");
        page.ChangedOnly.ButtonPressed = true;
        check.That(page.Table.GetRoot()!.GetChildCount() == 1 && Row(page, 0) is not null && Row(page, 1) is null && page.FilterNote.Length == 0 && page.SelectedRow == 0 && page.Table.GetSelected() is not null,
            "switched on, the table lists the one moved row, and the selection stays on it");
        page.Search.Text = "ghost";
        Edited(page.Search);
        check.That(page.Table.GetRoot()!.GetChildCount() == 0 && page.FilterNote == "No moved object matches the search.", $"a search that matches no moved row says so: \"{page.FilterNote}\"");
        page.Search.Text = "";
        Edited(page.Search);
        page.Reset.EmitSignal(BaseButton.SignalName.Pressed);
        check.That(page.Table.GetRoot()!.GetChildCount() == 0 && page.FilterNote == "No object is moved yet. Move one and it is listed here.", $"with nothing moved the list says so: \"{page.FilterNote}\"");
        page.Undo.EmitSignal(BaseButton.SignalName.Pressed);
        check.That(page.Table.GetRoot()!.GetChildCount() == 1 && page.FilterNote.Length == 0, "moving the object again (undoing the reset) lists it again");
        page.ChangedOnly.ButtonPressed = false;
        check.That(page.Table.GetRoot()!.GetChildCount() == body.Things.Count && page.FilterNote.Length == 0, "switched off, every row is back");
        page.ChangedOnly.ButtonPressed = true;
        Choose(page, 200);
        app.DiscardDialog.EmitSignal(AcceptDialog.SignalName.Confirmed);
        app.DiscardDialog.Hide();
        await Frame(tree);
        check.That(!page.ChangedOnly.ButtonPressed && page.Model?.Level == 200, "opening another level lists every row again");
        Choose(page, 100);
        await Frame(tree);
        page.SelectRow(0);
        Set(page.X, "12.5");
        Set(page.Y, "-40");
        Set(page.Z, "3");
        Submit(page.X);
        check.That(page.Model?.Level == 100 && page.Note == "Tank 1 (row 0) now stands at 12.5, -40, 3.", "the same move again, on the level opened afresh, so the checks below go on as before");

        // A coordinate that is not a number is refused in words and nothing moves; putting the field right clears it.
        Set(page.X, "abc");
        Submit(page.X);
        check.That(page.Note.StartsWith("X: ", StringComparison.Ordinal) && page.Note.Contains("is not a number", StringComparison.Ordinal) && page.X.Text == "abc" && M(page).Row(0)!.Position == new Vector3(12.5f, -40f, 3f),
            $"a coordinate that is not a number is refused and the object stays: \"{page.Note}\"");
        Set(page.X, "12.5");
        page.X.EmitSignal(Control.SignalName.FocusExited);
        check.That(page.Note.Length == 0, "putting the field back the way it was clears the refusal");

        // Leaving a field commits what was typed in it.
        Set(page.Y, "30");
        page.Y.EmitSignal(Control.SignalName.FocusExited);
        check.That(M(page).Row(0)!.Position == new Vector3(12.5f, 30f, 3f) && Row(page, 0)!.GetText(4) == "30" && page.Note == "Tank 1 (row 0) now stands at 12.5, 30, 3.", "leaving a field moves the object to what was typed");

        // Pressing Move after the field's own commit (a click takes the focus first) leaves the note of the move that was made.
        Press(page.Apply);
        check.That(page.Note == "Tank 1 (row 0) now stands at 12.5, 30, 3." && M(page).Row(0)!.Position == new Vector3(12.5f, 30f, 3f), "pressing Move with nothing new to apply keeps the note of the move just made");

        // Undo and redo.
        Press(page.Undo);
        check.That(M(page).Row(0)!.Position == new Vector3(12.5f, -40f, 3f) && page.Y.Text == "-40" && page.Note.StartsWith("Took back: Move Tank 1 (row 0)", StringComparison.Ordinal) && !page.Redo.Disabled,
            $"undo takes the last move back and says what it was: \"{page.Note}\"");
        Press(page.Redo);
        check.That(M(page).Row(0)!.Position == new Vector3(12.5f, 30f, 3f) && page.Note.StartsWith("Made again: ", StringComparison.Ordinal) && page.Redo.Disabled, "redo makes it again");

        // Reset puts the object back where the level has it, and the page has nothing left to save.
        Press(page.Reset);
        check.That(M(page).Row(0)!.Position == new Vector3(10f, 20f, 0f) && page.Note.Contains("back where the level has it, at 10, 20, 0", StringComparison.Ordinal) && page.Reset.Disabled && page.Save.Disabled &&
                   page.Summary.StartsWith("No changes yet", StringComparison.Ordinal), $"reset puts the object back: \"{page.Note}\"");

        // Rounding is said; a negative zero is shown as -0 and kept unless it is typed over.
        Set(page.X, "276.49");
        Set(page.Y, "265.07");
        Set(page.Z, "-0");
        Submit(page.Z);
        check.That(page.Note.Contains("Stored as X 276.489990234375, Y 265.07000732421875 (the nearest values the game can hold).", StringComparison.Ordinal) && page.Z.Text == "-0" &&
                   Bits(M(page).Row(0)!.Position.Z) == 0x80000000 && page.Hint.Contains("A stored -0 is shown as -0", StringComparison.Ordinal),
            $"a number that cannot be stored exactly says what is stored, and -0 stays -0 with a line that says so: \"{page.Note}\" / \"{page.Hint}\"");
        Set(page.X, "300");
        Submit(page.X);
        check.That(Bits(M(page).Row(0)!.Position.Z) == 0x80000000 && page.Z.Text == "-0" && M(page).Row(0)!.Position.X == 300f, "moving only X keeps a stored -0 as it was");
        Set(page.Z, "0");
        Submit(page.Z);
        check.That(Bits(M(page).Row(0)!.Position.Z) == 0 && page.Z.Text == "0", "typing 0 over -0 stores a plain zero");

        // The edit of the acceptance test's shape: the move the reference writes for row 0, saved as a mod.
        LevelVectors.StageVector vector = LevelVectors.Stages.First(v => v.Name == "editor-save");
        Set(page.X, "12.5");
        Set(page.Y, "-40");
        Set(page.Z, "3");
        Submit(page.X);
        check.That(M(page).Session!.ToBytes().AsSpan().SequenceEqual(LevelTests.Unpack(LevelVectors.Edits.First(e => e.Name == "move-v50").Body)), "the typed move gives the bytes the reference writes for it");
        Press(page.Save);
        await Frame(tree);
        SaveAsModDialog dialog = page.SaveDialog;
        check.That(dialog.Visible && dialog.ModName.Text == "Level 100 edit" && dialog.Id.Text == "level-100-edit" && dialog.Version.Text == "1" && dialog.Author.Text == "" &&
                   dialog.Destination.Text == Path.Combine(app.Game.CeUserFolder, "mods") && dialog.Problem.Length == 0 && !dialog.GetOkButton().Disabled,
            $"Save as mod opens with a name, an id, a version and CE's mods folder filled in: \"{dialog.ModName.Text}\", \"{dialog.Id.Text}\", \"{dialog.Destination.Text}\", \"{dialog.Problem}\"");

        // What the dialog will not take.
        Set(dialog.ModName, "");
        Edited(dialog.ModName);
        check.That(dialog.Problem.Contains("name", StringComparison.Ordinal) && dialog.GetOkButton().Disabled, "an empty name is refused: " + dialog.Problem);
        Set(dialog.ModName, "My Mod");
        Edited(dialog.ModName);
        check.That(dialog.Id.Text == "my-mod" && dialog.Problem.Length == 0, "the id follows the name until it is edited: " + dialog.Id.Text);
        Set(dialog.Id, "Custom");
        Edited(dialog.Id);
        check.That(dialog.Problem.Contains("lowercase", StringComparison.Ordinal) && dialog.GetOkButton().Disabled, "an id with a capital is refused: " + dialog.Problem);
        Set(dialog.Id, "custom");
        Edited(dialog.Id);
        Set(dialog.ModName, "Other");
        Edited(dialog.ModName);
        check.That(dialog.Id.Text == "custom" && dialog.Problem.Length == 0, "an edited id is no longer made from the name");
        Set(dialog.Destination, "relative/folder");
        Edited(dialog.Destination);
        check.That(dialog.Problem.Contains("full folder path", StringComparison.Ordinal) && dialog.GetOkButton().Disabled, "a folder that is not a full path is refused: " + dialog.Problem);
        Set(dialog.Destination, "");
        Edited(dialog.Destination);
        check.That(dialog.Problem.Contains("Choose the folder", StringComparison.Ordinal) && dialog.GetOkButton().Disabled, "no folder is refused: " + dialog.Problem);
        string chosen = Path.Combine(outputDirectory, "ui-level-mods");
        dialog.FolderDialog.EmitSignal(FileDialog.SignalName.DirSelected, chosen);
        check.That(dialog.Destination.Text == chosen && dialog.Problem.Length == 0 && !dialog.GetOkButton().Disabled, "a folder chosen in the picker is filled in");

        // Into the game folder: refused, with the reason on the page and nothing made.
        Set(dialog.Destination, Path.Combine(install.Game, "mods"));
        Edited(dialog.Destination);
        dialog.EmitSignal(AcceptDialog.SignalName.Confirmed);
        check.That(page.SavedText.Contains("game folder", StringComparison.Ordinal) && !page.CopyVisible && !Directory.Exists(Path.Combine(install.Game, "mods")) &&
                   app.Status.Label.Text.StartsWith("✕", StringComparison.Ordinal) && app.Status.Label.Text.Contains("game folder", StringComparison.Ordinal), $"a mod is not saved into the game folder: \"{page.SavedText}\"");

        // The words of the reference's stager for this edit, into a folder of the test's own.
        dialog.Begin(100, chosen);
        Set(dialog.Author, vector.Author);
        Edited(dialog.Author);
        Set(dialog.Description, vector.Description);
        Edited(dialog.Description);
        check.That(dialog.Info == new ModInfo(vector.Id, vector.ModName, vector.Version, vector.Author, vector.Description), "the dialog holds the words the reference stager was given");
        dialog.EmitSignal(AcceptDialog.SignalName.Confirmed);
        string root = Path.Combine(chosen, vector.Id);
        check.That(page.SavedText.StartsWith($"Saved the mod to {PathText.Elide(root, 52)}.", StringComparison.Ordinal) && page.SavedFolder == root && page.SavedTooltip.StartsWith(root + "\n", StringComparison.Ordinal) &&
                   page.SavedText.Contains($"mods={vector.Id}", StringComparison.Ordinal) && page.CopyVisible &&
                   app.Status.Label.Text.EndsWith("Saved the mod Level 100 edit.", StringComparison.Ordinal) && app.Status.Label.Text.StartsWith("✓", StringComparison.Ordinal), $"saving says where the mod is and what to add to ce.ini: \"{page.SavedText}\"");
        for (int frame = 0; frame < 5; frame++) await Frame(tree);
        check.That(page.SavedNoticeInView, "the notice, which sits under the Save button in the column that scrolls, is brought into view when it appears");
        check.That(File.ReadAllBytes(Path.Combine(root, "mod.json")).AsSpan().SequenceEqual(LevelTests.Unpack(vector.Manifest)) &&
                   File.ReadAllBytes(Path.Combine(root, "data", "worlds", "world100.wrd")).AsSpan().SequenceEqual(LevelTests.Unpack(LevelVectors.Edits.First(e => e.Name == "move-v50").Body)) &&
                   Directory.GetFiles(root, "*", SearchOption.AllDirectories).Length == 2, "the saved mod.json and world file are the reference stager's, byte for byte");
        dialog.EmitSignal(AcceptDialog.SignalName.Confirmed);
        check.That(page.SavedText.Contains("already holds", StringComparison.Ordinal) && !page.CopyVisible, "saving again into the same folder is refused, and says so: " + page.SavedText);

        // A very long folder does not make the notice long: it shows the path's two ends, keeps the full path for Copy and the tooltip, and the page still fits the smallest window.
        string deep = Path.Combine(chosen, new string('d', 120), new string('e', 120));
        dialog.Begin(100, deep);
        dialog.EmitSignal(AcceptDialog.SignalName.Confirmed);
        await Frame(tree);
        string deepRoot = Path.Combine(deep, dialog.Id.Text);
        check.That(page.SavedFolder == deepRoot && page.SavedText.Split('\n').Length == 2 && page.SavedText.Split('\n')[0].Length <= "Saved the mod to .".Length + 52 && page.SavedText.Contains("…", StringComparison.Ordinal) &&
                   page.SavedTooltip.StartsWith(deepRoot + "\n", StringComparison.Ordinal) && page.CopyVisible, $"a very long folder is shown by its ends only, and the full path is kept: \"{page.SavedText}\"");
        for (int frame = 0; frame < 3; frame++) await Frame(tree);
        check.That(app.GetCombinedMinimumSize().Y <= 700 && app.GetCombinedMinimumSize().X <= 1024, $"with the saved notice up the page still fits the smallest window: {app.GetCombinedMinimumSize()}");

        // The backups folder before its first use does not exist; a mod is still not saved inside it.
        string backups = app.Services.Backups.Folder;
        string held = backups + ".held-by-the-test";
        bool existed = Directory.Exists(backups);
        if (existed) Directory.Move(backups, held);
        try
        {
            dialog.Begin(100, Path.Combine(backups, "mods"));
            dialog.EmitSignal(AcceptDialog.SignalName.Confirmed);
            check.That(page.SavedText.Contains("never saved into your game folder or the companion's backups", StringComparison.Ordinal) && !page.CopyVisible && !Directory.Exists(backups),
                $"a mod is not saved into the backups folder before it exists, and the folder is not made: \"{page.SavedText}\"");
        }
        finally
        {
            if (existed) Directory.Move(held, backups);
        }

        // A level that also carries a base world, and one whose archive names another level.
        Choose(page, 200);
        await Frame(tree);
        check.That(page.Model?.Level == 200 && page.WorldNote.Contains("base world of level 100", StringComparison.Ordinal) && page.Problem.Length == 0 && page.Table.GetRoot()!.GetChildCount() == body.Things.Count &&
                   page.Save.Disabled && page.SavedText.Length == 0, "a level that carries a base world says so and edits its own world; a new level starts without a saved-mod message");
        Choose(page, 300);
        await Frame(tree);
        check.That(page.Problem.Contains("names level 200", StringComparison.Ordinal) && page.Table.GetRoot()!.GetChildCount() == 0 && page.Save.Disabled && !page.X.Editable, "an archive that names another level is not edited, and says why: " + page.Problem);
        Choose(page, 100);
        await Frame(tree);
        check.That(page.Problem.Length == 0 && page.Model?.Session is not null && page.Table.GetRoot()!.GetChildCount() == body.Things.Count, "a level opens again after a refusal");

        // Going somewhere else and coming back keeps the open level and its edit.
        page.SelectRow(1);
        Set(page.X, "7");
        Set(page.Y, "8");
        Set(page.Z, "9");
        Submit(page.X);
        app.Navigate("home");
        app.Navigate("levels");
        await Frame(tree);
        check.That(page.Model?.Level == 100 && M(page).Session!.Changes().Count == 1 && page.Level.GetItemId(page.Level.Selected) == 100 && !page.Save.Disabled, "leaving the page and coming back keeps the open level and its edit");

        check.That(Snapshot(install.Game).SequenceEqual(gameBefore), "the page never wrote anything into the game folder");
        FileDialog[] pickers = app.FindChildren("*", nameof(FileDialog), true, false).OfType<FileDialog>().ToArray();
        check.That(pickers.Contains(dialog.FolderDialog) && pickers.All(picker => !picker.DeletingEnabled && !picker.FolderCreationEnabled && picker.Access == FileDialog.AccessEnum.Filesystem), "the folder picker cannot delete files or create folders");
        app.Navigate("home");
        await Frame(tree);
    }
}
