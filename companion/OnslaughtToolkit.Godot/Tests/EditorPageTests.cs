// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;
using Vector3 = System.Numerics.Vector3;
using System.Security.Cryptography;
using Godot;
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
    private static string[] Snapshot(string root) => [.. Directory.EnumerateFiles(root, "*", SearchOption.AllDirectories).Order(StringComparer.Ordinal)
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
        check.That(page.Model?.Level == 100 && page.Problem.Length == 0 && page.Table.GetRoot()?.GetChildCount() == body.Things.Count && app.PageSubtitle.Text == $"Level 100 · {Build.Count(body.Things.Count, "object")}",
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
        check.That(page.SavedText.StartsWith($"Saved the mod to {root}.", StringComparison.Ordinal) && page.SavedText.Contains($"mods={vector.Id}", StringComparison.Ordinal) && page.CopyVisible &&
                   app.Status.Label.Text.EndsWith("Saved the mod Level 100 edit.", StringComparison.Ordinal) && app.Status.Label.Text.StartsWith("✓", StringComparison.Ordinal), $"saving says where the mod is and what to add to ce.ini: \"{page.SavedText}\"");
        check.That(File.ReadAllBytes(Path.Combine(root, "mod.json")).AsSpan().SequenceEqual(LevelTests.Unpack(vector.Manifest)) &&
                   File.ReadAllBytes(Path.Combine(root, "data", "worlds", "world100.wrd")).AsSpan().SequenceEqual(LevelTests.Unpack(LevelVectors.Edits.First(e => e.Name == "move-v50").Body)) &&
                   Directory.GetFiles(root, "*", SearchOption.AllDirectories).Length == 2, "the saved mod.json and world file are the reference stager's, byte for byte");
        dialog.EmitSignal(AcceptDialog.SignalName.Confirmed);
        check.That(page.SavedText.Contains("already holds", StringComparison.Ordinal) && !page.CopyVisible, "saving again into the same folder is refused, and says so: " + page.SavedText);

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
