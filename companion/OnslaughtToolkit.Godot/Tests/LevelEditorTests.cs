// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;
using System.Text;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// What the Level editor page stands on, without the page: the coordinate reader against the Toolkit's move tool on the texts
/// tools/level_editor_vectors.py ran it on (<c>LevelVectors.Coordinates</c>), and the model that turns a game folder's level archives,
/// typed coordinates and a mod's words into an edit and a saved mod. Authored data only; nothing here touches Godot.
/// </summary>
internal static class LevelEditorTests
{
    internal static void Run(string outputDirectory, Checks check)
    {
        check.Suite("level editor");
        Stage(check, "the coordinate vectors", () => CoordinateVectors(check));
        Stage(check, "the coordinate rules", () => CoordinateRules(check));
        Stage(check, "the model's levels", () => Levels(Path.Combine(outputDirectory, "level-editor-levels"), check));
        Stage(check, "the model's moves", () => Moves(Path.Combine(outputDirectory, "level-editor-moves"), check));
        Stage(check, "the model's saves", () => Saves(Path.Combine(outputDirectory, "level-editor-saves"), check));
        Stage(check, "a mod's id and name", () => Words(check));
        Stage(check, "paths shown shortened", () => Paths(check));
    }

    private static void Stage(Checks check, string name, Action stage)
    {
        try
        {
            stage();
        }
        catch (Exception error)
        {
            check.Fail($"{name} stopped with {error.GetType().Name}: {error.Message}");
        }
    }

    private static uint Bits(float value) => BitConverter.SingleToUInt32Bits(value);

    private static byte[] Archive(string name) => LevelTests.Unpack(LevelVectors.Archives.First(archive => archive.Name == name).File);

    // ---- the coordinate reader against the move tool ---------------------------------------------------------------------------
    private static void CoordinateVectors(Checks check)
    {
        check.That(LevelVectors.Coordinates.Length >= 110, "the vector file holds the coordinate texts");
        int accepted = 0, narrower = 0;
        foreach (LevelVectors.CoordinateVector v in LevelVectors.Coordinates)
        {
            string shown = v.Text.Length > 40 ? v.Text[..40] + "..." : v.Text;
            shown = string.Concat(shown.Select(c => c is < ' ' or > '~' ? $"\\u{(int)c:x4}" : c.ToString()));
            CoordinateParse parse = CoordinateInput.Parse(v.Text);
            if (!v.Grammar)
            {
                narrower++;
                check.That(!parse.Ok && parse.Problem is { Length: > 0 }, $"\"{shown}\" is outside the form the page reads, so it is refused (the tool {(v.Ok ? "reads it" : "refuses it too")})");
            }
            else if (!v.Ok)
            {
                check.That(!parse.Ok && parse.Problem is { Length: > 0 }, $"\"{shown}\" is refused, as the tool refuses it");
            }
            else
            {
                accepted++;
                uint expected = BitConverter.ToUInt32(Convert.FromHexString(v.Hex));  // the tool writes the four bytes little-endian; so does this host
                check.That(parse.Ok && Bits(parse.Value) == expected && parse.Rounded == v.Rounded,
                    $"\"{shown}\" is stored as {v.Hex} (rounded: {v.Rounded}); the page reads {(parse.Ok ? Convert.ToHexStringLower(BitConverter.GetBytes(parse.Value)) : parse.Problem)} (rounded: {parse.Rounded})");
                check.That(CoordinateInput.Exact(BitConverter.UInt32BitsToSingle(expected)) == v.Exact, $"\"{shown}\": its stored value is exactly {v.Exact}");
            }
        }
        check.That(accepted >= 70 && narrower >= 20, $"the vectors cover the accepted and the refused texts ({accepted} read, {narrower} outside the page's form)");
    }

    private static void CoordinateRules(Checks check)
    {
        CoordinateParse negativeZero = CoordinateInput.Parse("-0");
        check.That(negativeZero.Ok && Bits(negativeZero.Value) == 0x80000000 && !negativeZero.Rounded, "a negative zero stays a negative zero and is not called rounded");
        check.That(Bits(CoordinateInput.Parse("-0.0e5").Value) == 0x80000000 && Bits(CoordinateInput.Parse("+0").Value) == 0, "signed zeros keep their sign whatever spelling they have");
        check.That(Bits(CoordinateInput.Parse("-1e-50").Value) == 0x80000000 && CoordinateInput.Parse("-1e-50").Rounded, "a number too small to hold becomes a signed zero and is called rounded");
        check.That(CoordinateInput.Parse("512").Rounded == false && CoordinateInput.Parse("0.5").Rounded == false && CoordinateInput.Parse("0.1").Rounded, "a number the format holds exactly is not called rounded");
        check.That(CoordinateInput.Parse("276.49").Value == 276.49f && CoordinateInput.Parse("  -12.1 ").Value == -12.1f, "ordinary numbers read, with ASCII spaces around them ignored");
        check.That(CoordinateInput.Format(276.49f) == "276.49" && CoordinateInput.Format(-0f) == "-0" && CoordinateInput.Format(0f) == "0" && CoordinateInput.Format(-12.1f) == "-12.1",
            "a stored coordinate is shown as the shortest text that reads back as it");
        check.That(CoordinateInput.Exact(276.49f) == "276.489990234375" && CoordinateInput.Exact(-0f) == "-0" && CoordinateInput.Exact(0.5f) == "0.5" &&
                   CoordinateInput.Exact(-12.1f) == "-12.1000003814697265625" && CoordinateInput.Exact(float.MaxValue) == "340282346638528859811704183484516925440",
            "the exact value of a stored coordinate is written out in full");
        check.That(CoordinateInput.Parse("").Problem == "Type a number." && CoordinateInput.Parse("abc").Problem!.Contains("is not a number", StringComparison.Ordinal) &&
                   CoordinateInput.Parse("1e39").Problem!.Contains("too large", StringComparison.Ordinal) && CoordinateInput.Parse(new string('1', 129)).Problem!.Contains("too long", StringComparison.Ordinal) &&
                   CoordinateInput.Parse("1e1000000000000000000").Problem!.Contains("exponent", StringComparison.Ordinal), "each refusal says what is wrong in words");

        // Every stored value reads back from what is shown for it, and from its exact value: bits that survive a round trip.
        Random random = new(20261029);
        int checkedValues = 0;
        for (int i = 0; i < 4000; i++)
        {
            float value = BitConverter.UInt32BitsToSingle((uint)random.NextInt64(0, 1L << 32));
            if (!float.IsFinite(value)) continue;
            CoordinateParse shortest = CoordinateInput.Parse(CoordinateInput.Format(value));
            check.That(shortest.Ok && Bits(shortest.Value) == Bits(value), $"{CoordinateInput.Format(value)} reads back as the float it was shown for ({Bits(value):x8})");
            string exact = CoordinateInput.Exact(value);
            if (exact.Length > CoordinateInput.MaxLength) continue;
            CoordinateParse whole = CoordinateInput.Parse(exact);
            check.That(whole.Ok && Bits(whole.Value) == Bits(value) && !whole.Rounded, $"{exact} reads back as exactly the float it is the value of ({Bits(value):x8})");
            checkedValues++;
        }
        check.That(checkedValues > 1000, $"a thousand stored values were read back from their exact text ({checkedValues})");
    }

    // ---- the model --------------------------------------------------------------------------------------------------------------
    internal static string GameWithLevels(string folder)
    {
        string game = Path.Combine(folder, "game");
        string resources = Path.Combine(game, "data", "resources");
        Directory.CreateDirectory(resources);
        File.WriteAllBytes(Path.Combine(resources, "100_res_PC.aya"), Archive("level-100"));
        File.WriteAllBytes(Path.Combine(resources, "200_res_PC.aya"), Archive("base-and-real"));
        File.WriteAllBytes(Path.Combine(resources, "300_res_PC.aya"), Archive("real-only"));  // its WDAT names level 200
        File.WriteAllBytes(Path.Combine(resources, "400_res_PC.aya"), [1, 2, 3]);
        return game;
    }

    private static void Levels(string folder, Checks check)
    {
        LevelEditorModel model = LevelEditorModel.ForGame(GameWithLevels(folder));
        int changes = 0;
        model.Changed += () => changes++;
        check.That(model.Levels.Select(level => level.Level).SequenceEqual([100, 200, 300, 400]) && model.Session is null && model.Rows().Count == 0 && model.ChangeSummary() is null,
            "a model lists the game's levels and holds nothing until one is opened");

        check.That(model.Open(100) && model.Level == 100 && model.Problem is null && model.Session is not null && model.BaseLevel is null && model.Worlds?.RealLevel == 100 && changes == 1,
            "a level whose archive names itself opens its own world for editing");
        WorldBody body = WorldBody.Read(LevelTests.Body("authored-v50"));
        IReadOnlyList<ObjectRow> rows = model.Rows();
        check.That(rows.Count == body.Things.Count && rows.Select(row => row.Index).SequenceEqual(Enumerable.Range(0, body.Things.Count)), "the table has a row for each stored thing, in row order");
        check.That(rows[0].Name == "Tank 1" && rows[0].Kind == "unit" && rows[0].Label == "Tank 1" && rows[0].Position == new Vector3(10f, 20f, 0f) && rows[0].Stock == rows[0].Position && !rows[0].Changed,
            "a row says what it is and where it stands");
        check.That(rows[1].Name.Length == 0 && rows[1].Definition == "Ghost" && rows[1].Label == "Ghost" && rows[1].Kind == "unit", "a thing with no name is called by the definition it names");
        check.That(rows[2].Name.Length == 0 && rows[2].Definition.Length == 0 && rows[2].Label == rows[2].Kind, "a thing with no name and no definition is called by its kind");
        check.That(model.Rows("tank").Any(row => row.Index == 0) && model.Rows("TANK").Any(row => row.Index == 0) && model.Rows("2").Any(row => row.Index == 2) &&
                   model.Rows("waypoint").Any(row => row.Index == 2) && model.Rows("ghost").Single().Index == 1 && model.Rows("tank 1").Single().Index == 0 && model.Rows("no such thing").Count == 0 && model.Rows("  ").Count == rows.Count,
            "a search keeps rows by number, name, definition or kind, whatever the case");
        check.That(body.Things.Select((thing, index) => (thing, index)).Where(pair => pair.thing.Init.Script.Length > 0).All(pair => model.Rows(pair.thing.Init.Script).Any(row => row.Index == pair.index)),
            "a search finds a row by its script");
        check.That(model.Row(0)?.Index == 0 && model.Row(99) is null && model.Row(-1) is null, "a row is found by its number");

        check.That(!model.Open(999) && model.Problem!.Contains("no archive for level 999", StringComparison.Ordinal) && model.Session is null && model.Rows().Count == 0 && model.Worlds is null,
            "a level the game has no archive for says so and leaves nothing open");
        check.That(!model.Open(300) && model.Problem!.Contains("names level 200", StringComparison.Ordinal) && model.Session is null,
            "an archive that names another level as its world's level is not edited under this one");
        check.That(!model.Open(400) && model.Problem!.Contains("could not be read", StringComparison.Ordinal) && model.Session is null, "an archive that is not one says it could not be read");
        check.That(model.Open(200) && model.BaseLevel == 100 && model.Worlds?.BaseBody is not null && model.Session is not null && !model.Session.IsBaseWorld,
            "a level that also carries a base world edits its own world and says which level the base world is");
        check.That(model.Open(100) && model.Problem is null, "a level opens again after a refusal");

        // The game's levels can be listed again without losing the open level.
        string game = Path.Combine(folder, "game");
        check.That(!model.Rescan(game) && model.Level == 100 && model.Session is not null, "listing the levels again with nothing new changes nothing");
        File.WriteAllBytes(Path.Combine(game, "data", "resources", "500_res_PC.aya"), Archive("level-100"));
        check.That(model.Rescan(game) && model.Levels.Select(level => level.Level).SequenceEqual([100, 200, 300, 400, 500]) && model.Level == 100 && model.Session is not null && !model.Open(500),
            "a level that appeared is listed, and the open level stays open (level 500's archive names level 100)");

        LevelEditorModel none = LevelEditorModel.ForGame(Path.Combine(folder, "missing"));
        check.That(none.Levels.Count == 0 && !none.Open(100) && none.Problem is not null, "a game with no level archives opens nothing");
        check.That(none.Move(0, "1", "2", "3").Result == MoveResult.Refused && none.Reset(0).Result == MoveResult.Refused && !none.SaveAsMod(folder, new ModInfo("ok", "Ok"), []).Ok, "with nothing open there is nothing to move, reset or save");
    }

    private static void Moves(string folder, Checks check)
    {
        LevelEditorModel model = LevelEditorModel.ForGame(GameWithLevels(folder));
        int changes = 0;
        model.Open(100);
        model.Changed += () => changes++;
        byte[] baseline = LevelTests.Body("authored-v50");
        check.That(LevelEditorModel.Shown(new Vector3(10f, 20f, 0f)) == ("10", "20", "0") && LevelEditorModel.Shown(new Vector3(276.49f, -12.1f, -0f)) == ("276.49", "-12.1", "-0"),
            "the fields show each coordinate as the shortest text that reads back as it, and a negative zero as -0");

        // Typed coordinates move a row to the bytes the reference writes for the same move.
        LevelVectors.EditVector edit = LevelVectors.Edits.First(e => e.Name == "move-v50");
        MoveOutcome moved = model.Move(0, "12.5", "-40", "3");
        check.That(moved.Result == MoveResult.Moved && moved.Message == "Tank 1 (row 0) now stands at 12.5, -40, 3." && model.Session!.ToBytes().AsSpan().SequenceEqual(LevelTests.Unpack(edit.Body)) && changes == 1,
            $"typing coordinates writes the bytes the reference writes for that move: {moved.Message}");
        ObjectRow row = model.Row(0)!;
        check.That(row.Changed && row.Position == new Vector3(12.5f, -40f, 3f) && row.Stock == new Vector3(10f, 20f, 0f), "the row says it changed and where the level has it");
        check.That(model.Rows("", changedOnly: true).Select(r => r.Index).SequenceEqual([0]) && model.Rows("tank", changedOnly: true).Select(r => r.Index).SequenceEqual([0]) && model.Rows("ghost", changedOnly: true).Count == 0 &&
                   model.Rows("", changedOnly: false).Count > 1, "the changed-only list holds the moved rows, and a search narrows it further");
        check.That(model.ChangeSummary() is { } summary && summary.StartsWith("1 object moved: Tank 1 (row 0), 60.1 units", StringComparison.Ordinal) && summary.EndsWith('.'), "the changes are summarised: " + model.ChangeSummary());

        MoveOutcome same = model.Move(0, "12.5", "-40", "3");
        check.That(same.Result == MoveResult.Unchanged && same.Message.Contains("already stands", StringComparison.Ordinal) && changes == 1, "typing where a row already stands changes nothing and raises nothing");
        MoveOutcome sameValue = model.Move(0, " 12.50 ", "-40.0", "+3");
        check.That(sameValue.Result == MoveResult.Unchanged && changes == 1, "another spelling of the same coordinates changes nothing");

        // A refused field refuses the whole move, naming the field.
        MoveOutcome refusedX = model.Move(0, "abc", "-40", "3");
        MoveOutcome refusedZ = model.Move(0, "99", "99", "1e39");
        check.That(refusedX.Result == MoveResult.Refused && refusedX.Message.StartsWith("X: ", StringComparison.Ordinal) && refusedZ.Result == MoveResult.Refused && refusedZ.Message.StartsWith("Z: ", StringComparison.Ordinal) &&
                   model.Row(0)!.Position == new Vector3(12.5f, -40f, 3f) && changes == 1, $"a coordinate that is not accepted refuses the whole move and says which: {refusedX.Message} / {refusedZ.Message}");
        check.That(model.Move(99, "1", "2", "3").Result == MoveResult.Refused && model.Move(-1, "1", "2", "3").Result == MoveResult.Refused && changes == 1, "there is no row 99 or -1 to move");

        // A coordinate that is not exact says what is stored.
        MoveOutcome rounded = model.Move(0, "276.49", "265.07", "-12.1");
        check.That(rounded.Result == MoveResult.Moved && rounded.Message == "Tank 1 (row 0) now stands at 276.49, 265.07, -12.1. Stored as X 276.489990234375, Y 265.07000732421875, Z -12.1000003814697265625 (the nearest values the game can hold).",
            "coordinates the format cannot hold exactly are stored rounded, and the page says so: " + rounded.Message);
        check.That(Bits(model.Row(0)!.Position.X) == Bits(276.49f) && Bits(model.Row(0)!.Position.Y) == Bits(265.07f) && Bits(model.Row(0)!.Position.Z) == Bits(-12.1f), "the float32 nearest each number is what is stored");
        MoveOutcome roundedAgain = model.Move(0, "276.49", "265.07", "-12.1");
        check.That(roundedAgain.Result == MoveResult.Unchanged, "the text shown for a rounded value is not read again, so it changes nothing");
        MoveOutcome one = model.Move(0, "0.1", "265.07", "-12.1");
        check.That(one.Result == MoveResult.Moved && one.Message == "Tank 1 (row 0) now stands at 0.1, 265.07, -12.1. Stored as X 0.100000001490116119384765625 (the nearest value the game can hold).", "one rounded coordinate is said in the singular: " + one.Message);
        check.That(model.Move(0, "0.5", "265.07", "-12.1").Message == "Tank 1 (row 0) now stands at 0.5, 265.07, -12.1.", "a coordinate that is stored exactly adds nothing");
        MoveOutcome ghost = model.Move(1, "5", "6", "7");
        check.That(ghost.Result == MoveResult.Moved && ghost.Message == "Ghost (row 1) now stands at 5, 6, 7." && model.ChangeSummary()!.Contains("Ghost (row 1)", StringComparison.Ordinal), "a thing with no name is named by its definition: " + ghost.Message);
        model.Open(100);

        // A stored negative zero is shown as -0 and kept as it is unless it is typed over.
        EditSession zeroes = new(baseline);
        zeroes.Apply(new MoveObject(0, new Vector3(10f, 20f, -0f)));
        check.That(zeroes.Changes().Count == 1, "a zero that became a negative zero is a change");
        model.Open(100);
        changes = 0;
        check.That(model.Move(0, "10", "20", "-0").Result == MoveResult.Moved && Bits(model.Row(0)!.Position.Z) == 0x80000000 && changes == 1, "typing -0 stores a negative zero");
        check.That(LevelEditorModel.Shown(model.Row(0)!.Position).Z == "-0" && model.Move(0, "10", "20", "-0").Result == MoveResult.Unchanged, "a stored -0 is shown as -0, and showing it back changes nothing");
        check.That(model.Move(0, "11", "20", "-0").Result == MoveResult.Moved && Bits(model.Row(0)!.Position.Z) == 0x80000000 && model.Row(0)!.Position.X == 11f, "moving only X keeps a stored -0 as it was");
        check.That(model.Move(0, "11", "20", "0").Result == MoveResult.Moved && Bits(model.Row(0)!.Position.Z) == 0, "typing 0 over -0 stores a plain zero, which is a change");

        // Reset puts a row back, as an edit that can be undone.
        model.Open(100);
        model.Move(0, "5", "5", "5");
        model.Move(2, "6", "6", "6");
        changes = 0;
        MoveOutcome reset = model.Reset(0);
        check.That(reset.Result == MoveResult.Moved && reset.Message.Contains("back where the level has it, at 10, 20, 0", StringComparison.Ordinal) && !model.Row(0)!.Changed && model.Row(2)!.Changed && changes == 1,
            "reset puts one object back where the level has it and leaves the others: " + reset.Message);
        check.That(model.Reset(0).Result == MoveResult.Unchanged && model.Reset(99).Result == MoveResult.Refused && changes == 1, "an object that has not moved has nothing to reset");
        check.That(model.Session!.Undo() && model.Row(0)!.Changed && model.Row(0)!.Position == new Vector3(5f, 5f, 5f), "a reset can be undone");
        check.That(model.ChangeSummary() is { } two && two.StartsWith("2 objects moved: ", StringComparison.Ordinal), "two moved objects are summarised together: " + model.ChangeSummary());
        for (int i = 0; i < model.Rows().Count; i++) model.Move(i, $"{i + 1}", $"{i + 1}", $"{i + 1}");
        int allRows = model.Rows().Count;
        check.That(allRows >= 4 && model.ChangeSummary() is { } many && many.StartsWith($"{allRows} objects moved: ", StringComparison.Ordinal) && many.EndsWith($" and {allRows - 3} more.", StringComparison.Ordinal) && many.Split("(row ").Length - 1 == 3,
            "a long list of changes is shortened: " + model.ChangeSummary());

        // Undo and redo go through the session and raise Changed.
        model.Open(100);
        changes = 0;
        model.Move(0, "1", "2", "3");
        check.That(model.Session!.Undo() && model.Session.ToBytes().AsSpan().SequenceEqual(baseline) && model.Session.Redo() && model.Row(0)!.Position == new Vector3(1f, 2f, 3f) && changes == 3, "undo and redo each raise Changed");
    }

    private static void Saves(string folder, Checks check)
    {
        string game = GameWithLevels(folder);
        string mods = Path.Combine(folder, "user", "mods");
        LevelVectors.StageVector vector = LevelVectors.Stages.First(v => v.Name == "editor-save");
        ModInfo info = new(vector.Id, vector.ModName, vector.Version, vector.Author, vector.Description, vector.CeMin, vector.CeMax);
        LevelEditorModel model = LevelEditorModel.ForGame(game);
        model.Open(100);
        check.That(!model.HasUnsavedChanges && model.UnsavedChangeCount == 0, "a level just opened holds nothing unsaved");

        SaveOutcome nothing = model.SaveAsMod(mods, info, [game]);
        check.That(!nothing.Ok && nothing.Message.Contains("Nothing has changed", StringComparison.Ordinal) && !Directory.Exists(mods), "an unchanged level is not saved: " + nothing.Message);

        model.Move(0, "12.5", "-40", "3");
        check.That(model.HasUnsavedChanges && model.UnsavedChangeCount == 1, "a move is unsaved until a Save as mod has written it");
        SaveOutcome inGame = model.SaveAsMod(Path.Combine(game, "mods"), info, [game]);
        check.That(!inGame.Ok && inGame.Message.Contains("never saved into your game folder", StringComparison.Ordinal) && !Directory.Exists(Path.Combine(game, "mods")), "a mod is not saved into a protected folder: " + inGame.Message);
        check.That(model.UnsavedChangeCount == 1, "a save that was refused leaves the move unsaved");

        // A protected folder that does not exist yet (the backups folder before the first backup) still guards its place, and the refusal does not make it.
        string absent = Path.Combine(folder, "backups-not-made-yet");
        foreach (string destination in new[] { absent, Path.Combine(absent, "mods"), Path.Combine(absent, "a", "b") })
        {
            SaveOutcome intoAbsent = model.SaveAsMod(destination, info, [game, absent]);
            check.That(!intoAbsent.Ok && intoAbsent.Message.Contains("never saved into your game folder or the companion's backups", StringComparison.Ordinal) && !Directory.Exists(absent),
                $"a mod is not saved into a protected folder that does not exist yet ({Path.GetRelativePath(folder, destination)}), and it is not made: {intoAbsent.Message}");
        }
        check.That(model.UnsavedChangeCount == 1, "and those refusals leave the move unsaved");

        SaveOutcome saved = model.SaveAsMod(mods, info, [game, absent]);
        check.That(saved.Ok && saved.Message == $"Saved the mod to {Path.Combine(mods, vector.Id)}." && saved.Staged!.ManifestSha256 == vector.ManifestSha256 &&
                   saved.Staged.Files.Select(f => (f.Path, f.Size, f.Sha256)).SequenceEqual(vector.Files.Select(f => (f.Path, f.Size, f.Sha256))),
            "the edit is saved as the mod the reference stager writes for that edit: " + saved.Message);
        check.That(File.ReadAllBytes(Path.Combine(saved.Staged!.Root, "mod.json")).AsSpan().SequenceEqual(LevelTests.Unpack(vector.Manifest)) &&
                   File.ReadAllBytes(Path.Combine(saved.Staged.Root, "data", "worlds", "world100.wrd")).AsSpan().SequenceEqual(LevelTests.Unpack(LevelVectors.Edits.First(e => e.Name == "move-v50").Body)),
            "its mod.json and world file are the reference's, byte for byte");
        check.That(!model.HasUnsavedChanges && model.UnsavedChangeCount == 0, "once saved, the move is not unsaved");
        model.Move(0, "13", "-40", "3");
        check.That(model.UnsavedChangeCount == 1, "the saved object moved again, to another place, is unsaved though the same objects are moved");
        model.Move(0, "13", "-40", "4");
        model.Move(0, "12.5", "-40", "4");
        check.That(model.UnsavedChangeCount == 1, "a change in height alone is unsaved");
        check.That(model.Session!.Undo() && model.Session.Undo() && model.Session.Undo() && model.UnsavedChangeCount == 0, "undone back to what was saved, nothing is unsaved");
        model.Move(1, "5", "6", "7");
        check.That(model.UnsavedChangeCount == 2, "a move made after the save is unsaved, and the saved one counts with it: " + model.UnsavedChangeCount);
        check.That(model.Session!.Undo() && model.UnsavedChangeCount == 0, "undone back to what was saved, nothing is unsaved");
        check.That(model.Session.Undo() && model.UnsavedChangeCount == 0 && model.Session.Changes().Count == 0, "undone to the level's own, there is nothing to lose");
        check.That(model.Session.Redo() && model.UnsavedChangeCount == 0 && model.Session.Redo() && model.UnsavedChangeCount == 2, "and redone past the save, the later move is unsaved again");
        model.Session.Undo();
        model.Open(100);
        check.That(model.UnsavedChangeCount == 0 && !model.HasUnsavedChanges, "opening a level again starts without anything unsaved");
        model.Move(0, "12.5", "-40", "3");
        check.That(model.UnsavedChangeCount == 1, "a move made on a level opened again is unsaved even if it is the one saved before: a new session has no save");
        SaveOutcome again = model.SaveAsMod(mods, info, [game]);
        check.That(!again.Ok && again.Message.Contains("already holds", StringComparison.Ordinal), "saving again into the same folder is refused: " + again.Message);
        check.That(model.UnsavedChangeCount == 1, "and that refusal leaves the move unsaved");

        // A zero and a negative zero are different bytes in the file, so changing one into the other after a save is unsaved.
        model.Open(100);
        model.Move(0, "12.5", "-40", "-0");
        check.That(model.SaveAsMod(Path.Combine(folder, "user", "mods-zero"), info, [game]).Ok && model.UnsavedChangeCount == 0, "a move to a height of -0 is saved");
        model.Move(0, "12.5", "-40", "0");
        check.That(model.UnsavedChangeCount == 1, "typing 0 over the saved -0 is unsaved: the file would differ in one bit");
        model.Move(0, "12.5", "-40", "-0");
        check.That(model.UnsavedChangeCount == 0, "and -0 again is what was saved");
        check.That(!model.SaveAsMod(mods, new ModInfo("Bad Id", "Name"), [game]).Ok && !model.SaveAsMod("relative/folder", info, [game]).Ok, "words CE would not accept and a folder that is not a full path are refused");

        // A level whose archive names another level is never saved under this one: it cannot be opened, so nothing is staged.
        model.Open(300);
        check.That(!model.SaveAsMod(Path.Combine(folder, "user", "other"), info, [game]).Ok && !Directory.Exists(Path.Combine(folder, "user", "other")), "nothing is saved for a level that is not open");
    }

    private static void Paths(Checks check)
    {
        check.That(PathText.Elide("/a/b", 52) == "/a/b" && PathText.Elide(new string('x', 52), 52) == new string('x', 52), "a path that fits is shown as it is, the longest one that fits included");
        string path = "/home/someone/projects/onslaught/mods/a-folder-with-a-rather-long-name/level-100-edit";
        string cut = PathText.Elide(path, 52);
        check.That(cut.Length <= 52 && cut.Contains('…') && cut.StartsWith(path[..12], StringComparison.Ordinal) && cut.EndsWith("level-100-edit", StringComparison.Ordinal),
            $"a longer path is cut in the middle: {cut.Length} characters, {cut}");
        check.That(cut == "/home/someone/pro…-a-rather-long-name/level-100-edit", "the cut keeps a third of the room for where the path starts and two thirds for where it ends: " + cut);
        check.That(PathText.Elide(new string('p', 53), 52).Length == 52 && PathText.Elide(new string('p', 5000), 52).Length == 52, "one character over is cut to the limit, and so is a path of thousands");
        check.That(PathText.Elide("/abcdefgh", 5) == "/a…gh" || PathText.Elide("/abcdefgh", 5).Length == 5, "the shortest limit still cuts: " + PathText.Elide("/abcdefgh", 5));
        // A cut never splits a surrogate pair, wherever it falls.
        UTF8Encoding strict = new(false, true);
        for (int offset = 0; offset < 6; offset++)
        {
            string emoji = new string('a', offset) + string.Concat(Enumerable.Repeat("😀", 40));
            for (int max = 5; max < 30; max++)
            {
                string cutEmoji = PathText.Elide(emoji, max);
                try
                {
                    strict.GetBytes(cutEmoji);
                    check.That(cutEmoji.Length <= max, $"the elided text of {max} characters fits ({offset} before the emoji)");
                }
                catch (EncoderFallbackException)
                {
                    check.Fail($"the path was cut inside a surrogate pair at {max} characters, {offset} before the emoji");
                }
            }
        }
        Refuses(check, "a limit too short to cut", () => PathText.Elide("/long/path/here", 4));
    }

    private static void Refuses(Checks check, string what, Action action)
    {
        try
        {
            action();
            check.Fail(what + ": nothing was thrown");
        }
        catch (ArgumentOutOfRangeException)
        {
            check.That(true, what);
        }
    }

    private static void Words(Checks check)
    {
        check.That(LevelEditorModel.DefaultModName(100) == "Level 100 edit" && LevelEditorModel.ModIdFromName("Level 100 edit") == "level-100-edit", "a mod is called after its level, and its id after its name");
        foreach ((string name, string id) in new[]
                 {
                     ("  My  Mod!! ", "my-mod"), ("a--b", "a-b"), ("-lead", "lead"), ("trail-", "trail"), ("_x_", "_x_"), ("Ünï", "n"), ("ÄÖ", "level-edit"), ("", "level-edit"), ("!!!", "level-edit"),
                     (new string('x', 60), new string('x', 48)), (new string('a', 47) + " b", new string('a', 47)), ("Tank 12, 276.49", "tank-12-276-49"),
                 })
        {
            string made = LevelEditorModel.ModIdFromName(name);
            check.That(made == id && ModStager.Problem(new ModInfo(made, "Name")) is null, $"\"{name}\" gives the id \"{made}\" (expected \"{id}\"), which CE accepts");
        }
        StringBuilder every = new();
        for (int c = 0; c < 0x250; c++) every.Append((char)c);
        check.That(ModStager.Problem(new ModInfo(LevelEditorModel.ModIdFromName(every.ToString()), "Name")) is null, "whatever the name holds, the id made from it is one CE accepts");
    }
}
