// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// Copying a unit to the end of a level's thing list (M5's first step, append-only): the deep copy of a record and the member-by-member comparison that finds a copy, the command and
/// its refusals, the session (what is saved, the added rows, undo), what the validator accepts and what it refuses, and the model's copy (the place, the name, the summary, the counts and
/// what Save as mod writes). Authored data only; no game is involved.
/// </summary>
internal static class LevelCopyTests
{
    internal static void Run(string output, Checks check)
    {
        check.Suite("copying units");
        byte[] baseline = LevelTests.Body("authored-v50");
        Cloning(baseline, check);
        Command(baseline, check);
        Session(baseline, check);
        Validation(baseline, check);
        Model(Path.Combine(output, "level-copy"), check);
    }

    private static int FirstOf(WorldBody body, Func<PlacedObject, bool> match) => body.Things.FindIndex(thing => match(thing));

    private static void Throws(Checks check, string what, Action action, string contains)
    {
        try
        {
            action();
            check.Fail($"{what}: nothing was refused");
        }
        catch (InvalidOperationException error)
        {
            check.That(error.Message.Contains(contains, StringComparison.Ordinal), $"{what}: \"{error.Message}\"");
        }
    }

    // ---- the copy of a record -----------------------------------------------------------------------------------------------------
    private static void Cloning(byte[] baseline, Checks check)
    {
        WorldBody body = WorldBody.Read(baseline);
        int kinds = 0, shared = 0;
        foreach (PlacedObject thing in body.Things)
        {
            PlacedObject clone = thing.Clone();
            kinds++;
            bool same = !ReferenceEquals(clone, thing) && !ReferenceEquals(clone.Init, thing.Init) && clone.SameExceptPlace(thing) && clone.Init.Name == thing.Init.Name && clone.Init.Position == thing.Init.Position;
            foreach (object? block in new object?[] { thing.Init.Spawner, thing.Init.Squad, thing.Init.Cutscene, thing.Init.Start, thing.Init.Tree, thing.Init.SphereTrigger })
                if (block is not null && new object?[] { clone.Init.Spawner, clone.Init.Squad, clone.Init.Cutscene, clone.Init.Start, clone.Init.Tree, clone.Init.SphereTrigger }.Any(other => ReferenceEquals(other, block))) shared++;
            if (!same) check.Fail($"the copy of row {kinds - 1} ({thing.Kind}) is not an equal, separate record");
        }
        check.That(kinds == body.Things.Count && shared == 0, "every record of the authored level copies to an equal record that shares nothing with it, kind-specific blocks included");

        // The comparison ignores the place and nothing else: each member changed alone makes a record not a copy.
        PlacedObject unit = body.Things[FirstOf(body, thing => thing.ObjectId == ObjectKinds.Unit)];
        PlacedObject moved = unit.Clone();
        moved.Init.Position = new Vector3(1f, 2f, 3f);
        moved.Init.Name = "elsewhere";
        check.That(moved.SameExceptPlace(unit) && unit.SameExceptPlace(moved), "a record at another place under another name is still a copy of the record");
        List<(string Member, Action<PlacedObject> Change)> changes =
        [
            ("object id", thing => thing.ObjectId += 1), ("definition", thing => thing.Definition = "Something else"), ("dies on", thing => thing.DiesOn += 1),
            ("orientation", thing => thing.Init.Orientation += new Vector3(0.5f, 0, 0)), ("mesh", thing => thing.Init.MeshNumber += 1), ("allegiance", thing => thing.Init.Allegiance += 1),
            ("target", thing => thing.Init.Target += 1), ("script", thing => thing.Init.Script += "x"), ("spawn script", thing => thing.Init.SpawnScript += "x"), ("active", thing => thing.Init.Active += 1),
            ("attach scripts", thing => thing.Init.AttachScriptsToUnits = (thing.Init.AttachScriptsToUnits ?? 0) + 1),
        ];
        foreach ((string member, Action<PlacedObject> change) in changes)
        {
            PlacedObject other = unit.Clone();
            change(other);
            check.That(!other.SameExceptPlace(unit) && !unit.SameExceptPlace(other), $"a record whose {member} differs is not a copy");
        }
        // The kind-specific blocks are copied apart and compared too.
        int spawner = FirstOf(body, thing => thing.Init.Spawner is not null), trigger = FirstOf(body, thing => thing.Init.SphereTrigger is not null);
        if (spawner >= 0)
        {
            PlacedObject s = body.Things[spawner].Clone();
            s.Init.Spawner!.Amount += 1;
            check.That(!s.SameExceptPlace(body.Things[spawner]) && s.Init.Spawner.Amount != body.Things[spawner].Init.Spawner!.Amount, "a spawner's block is copied apart and compared");
        }
        if (trigger >= 0)
        {
            PlacedObject s = body.Things[trigger].Clone();
            s.Init.SphereTrigger!.Radius += 1f;
            check.That(!s.SameExceptPlace(body.Things[trigger]) && s.Init.SphereTrigger.Radius != body.Things[trigger].Init.SphereTrigger!.Radius, "a sphere trigger's block is copied apart and compared");
        }
    }

    // ---- the command --------------------------------------------------------------------------------------------------------------
    private static void Command(byte[] baseline, Checks check)
    {
        WorldBody body = WorldBody.Read(baseline);
        int unit = FirstOf(body, thing => thing.ObjectId == ObjectKinds.Unit), waypoint = FirstOf(body, thing => thing.ObjectId == 18), count = body.Things.Count;
        check.That(unit >= 0 && waypoint >= 0 && DuplicateObject.CanCopy(body.Things[unit]) && !DuplicateObject.CanCopy(body.Things[waypoint]), "units can be copied and path points cannot");
        DuplicateObject copy = new(unit, new Vector3(50f, 60f, 0f), "Tank 1 copy");
        copy.Do(body);
        PlacedObject added = body.Things[^1];
        check.That(body.Things.Count == count + 1 && copy.AddedIndex == count && added.SameExceptPlace(body.Things[unit]) && added.Init.Name == "Tank 1 copy" && added.Init.Position == new Vector3(50f, 60f, 0f) &&
                   !ReferenceEquals(added, body.Things[unit]) && body.Things[unit].Init.Name == "Tank 1" && copy.Description == $"Copy Tank 1 (row {unit}) as row {count}",
            $"a copy is appended after every row, a separate record with the new place and name: \"{copy.Description}\"");
        check.That(WorldBody.Read(body.Write()).Things[count].SameExceptPlace(body.Things[unit]) && body.Write().Length > baseline.Length, "the body with the copy writes and reads back, the copy included");
        Throws(check, "a copy made twice", () => copy.Do(body), "already been made");
        copy.Undo(body);
        check.That(body.Things.Count == count && copy.AddedIndex is null && body.Write().AsSpan().SequenceEqual(baseline), "taking the copy back leaves the body as the baseline has it, byte for byte");
        Throws(check, "taking back a copy that was not made", () => copy.Undo(body), "not been made");
        copy.Do(body);
        check.That(body.Things.Count == count + 1 && copy.AddedIndex == count, "a copy taken back can be made again");

        // Only the last row can be taken back: a copy with something after it stays.
        body.Things.Add(body.Things[unit].Clone());
        Throws(check, "taking back a copy that is not the last row", () => copy.Undo(body), "not the last row");
        body.Things.RemoveAt(body.Things.Count - 1);
        copy.Undo(body);

        Throws(check, "copying a path point", () => new DuplicateObject(waypoint, Vector3.Zero, "x").Do(body), "Only units can be copied");
        Throws(check, "copying row -1", () => new DuplicateObject(-1, Vector3.Zero, "x").Do(body), "no row -1");
        Throws(check, "copying a row that is not there", () => new DuplicateObject(count + 5, Vector3.Zero, "x").Do(body), "no row");
        Throws(check, "a copy at a position that is not a number", () => new DuplicateObject(unit, new Vector3(float.NaN, 0, 0), "x").Do(body), "finite");
        check.That(body.Things.Count == count, "a refused copy changes nothing");
        while (body.Things.Count < WorldBody.MaxThings) body.Things.Add(body.Things[unit].Clone());
        Throws(check, "a copy past the game's limit of things", () => new DuplicateObject(unit, Vector3.Zero, "x").Do(body), $"at most {WorldBody.MaxThings}");
    }

    // ---- the session ---------------------------------------------------------------------------------------------------------------
    private static void Session(byte[] baseline, Checks check)
    {
        EditSession session = new(baseline);
        int unit = FirstOf(session.Body, thing => thing.ObjectId == ObjectKinds.Unit), count = session.Body.Things.Count;
        check.That(session.BaselineThingCount == count && session.Additions().Count == 0, "a session starts with no added rows");
        session.Apply(new DuplicateObject(unit, new Vector3(70f, 80f, 0f), "Tank 1 copy"));
        check.That(session.Additions().Count == 1 && session.Additions()[0] == (count, "unit", "Tank 1 copy") && session.Changes().Count == 0 && session.Validate().CanSave, "a copy is an added row, no move, and can be saved");
        byte[] saved = session.ToBytes();
        WorldBody read = WorldBody.Read(saved);
        check.That(read.Things.Count == count + 1 && read.Write().AsSpan().SequenceEqual(saved) && read.Things[count].SameExceptPlace(read.Things[unit]) && read.Things[count].Init.Position == new Vector3(70f, 80f, 0f) && !session.IsBaseline(saved), "what is saved reads back strictly and writes back the same bytes, with the copy at its place");

        // The copy can be moved like any row, and that is still not a change of a row the level has.
        session.Apply(new MoveObject(count, new Vector3(90f, 91f, 0f)));
        check.That(session.Changes().Count == 0 && session.Additions().Count == 1 && session.Validate().CanSave && session.Body.Things[count].Init.Position == new Vector3(90f, 91f, 0f), "moving the copy is not a move of a row the level has");
        // A copy of a copy is a copy.
        session.Apply(new DuplicateObject(count, new Vector3(95f, 91f, 0f), "Tank 1 copy 2"));
        check.That(session.Additions().Count == 2 && session.Validate().CanSave && session.Body.Things[count + 1].SameExceptPlace(session.Body.Things[unit]), "a copy of a copy is saved too");
        // Undo takes them back in order, the copy last of all, to the baseline.
        session.Undo();
        session.Undo();
        check.That(session.Additions().Count == 1 && session.Body.Things[count].Init.Position == new Vector3(70f, 80f, 0f), "undo takes the second copy and then the move back");
        session.Undo();
        check.That(session.Additions().Count == 0 && session.IsBaseline(session.ToBytes()) && !session.Validate().CanSave, "and the first copy: the session is the baseline again, and there is nothing to save");
        session.Redo();
        session.Redo();
        session.Redo();
        check.That(session.Additions().Count == 2 && session.Validate().CanSave, "redo makes all three again");

        // A copy next to a moved row of the level: both are kept apart.
        EditSession both = new(baseline);
        both.Apply(new MoveObject(unit, new Vector3(5f, 5f, 0f)));
        both.Apply(new DuplicateObject(unit, new Vector3(15f, 5f, 0f), "Tank 1 copy"));
        check.That(both.Changes().Count == 1 && both.Additions().Count == 1 && both.Body.Things[count].SameExceptPlace(both.Body.Things[unit]) && both.Validate().CanSave, "a moved row and a copy are both there, and both are listed apart");
    }

    // ---- the validator ------------------------------------------------------------------------------------------------------------
    private static void Validation(byte[] baseline, Checks check)
    {
        static bool Has(EditSession session, string code) => session.Validate().Errors.Any(error => error.Code == code);
        int unit = FirstOf(WorldBody.Read(baseline), thing => thing.ObjectId == ObjectKinds.Unit), waypoint = FirstOf(WorldBody.Read(baseline), thing => thing.ObjectId == 18);

        EditSession fromWaypoint = new(baseline);
        fromWaypoint.Body.Things.Add(fromWaypoint.Body.Things[waypoint].Clone());
        check.That(Has(fromWaypoint, "added-row") && !fromWaypoint.Validate().CanSave, "an added row that is not a unit is refused");

        EditSession notACopy = new(baseline);
        PlacedObject odd = notACopy.Body.Things[unit].Clone();
        odd.DiesOn += 1;
        notACopy.Body.Things.Add(odd);
        check.That(Has(notACopy, "added-row"), "an added unit that is not a copy of an earlier row is refused");

        EditSession changedOriginal = new(baseline);
        changedOriginal.Apply(new DuplicateObject(unit, new Vector3(1f, 1f, 0f), "c"));
        changedOriginal.Body.Things[unit].Init.Allegiance += 1;
        check.That(Has(changedOriginal, "other-change") && !changedOriginal.Validate().CanSave, "a field of a row the level has that changed, beside a copy, is still refused");

        EditSession taken = new(baseline);
        taken.Body.Things.RemoveAt(taken.Body.Things.Count - 1);
        check.That(Has(taken, "rows-changed"), "a row taken away is refused");

        EditSession reordered = new(baseline);
        (reordered.Body.Things[unit], reordered.Body.Things[waypoint]) = (reordered.Body.Things[waypoint], reordered.Body.Things[unit]);
        check.That(Has(reordered, "rows-changed"), "rows of different kinds in another order are refused");

        EditSession baseWorld = new(baseline, isBaseWorld: true);
        baseWorld.Apply(new DuplicateObject(unit, new Vector3(1f, 1f, 0f), "c"));
        check.That(Has(baseWorld, "base-world-rows") && !baseWorld.Validate().CanSave, "a base world is never given more things");

        EditSession full = new(baseline);
        while (full.Body.Things.Count <= WorldBody.MaxThings) full.Body.Things.Add(full.Body.Things[unit].Clone());
        check.That(!full.Validate().CanSave && full.Validate().Errors.Any(error => error.Code == "cannot-write"), "more things than the game's world holds cannot be written, so cannot be saved");

        EditSession nan = new(baseline);
        nan.Apply(new DuplicateObject(unit, new Vector3(1f, 1f, 0f), "c"));
        nan.Body.Things[^1].Init.Position = new Vector3(float.NaN, 0, 0);
        check.That(Has(nan, "added-row"), "a copy whose position is not a number is refused");
    }

    // ---- the model ------------------------------------------------------------------------------------------------------------------
    private static void Model(string folder, Checks check)
    {
        LevelEditorModel model = LevelEditorModel.ForGame(LevelEditorTests.GameWithLevels(folder));
        check.That(model.Duplicate(0).Row is null && !model.CanDuplicate(0), "with no level open there is nothing to copy");
        model.Open(100);
        int count = model.Rows().Count;
        check.That(model.CanDuplicate(0) && model.CanDuplicate(1) && !model.CanDuplicate(2) && !model.CanDuplicate(99) && !model.CanDuplicate(-1), "units can be copied; a path point, and a row that is not there, cannot");

        DuplicateOutcome first = model.Duplicate(0);
        ObjectRow added = model.Row(first.Row ?? -1)!;
        check.That(first.Ok && first.Row == count && added.Added && added.Changed && added.Name == "Tank 1 copy" && added.Kind == "unit" && added.Definition == model.Row(0)!.Definition &&
                   added.Position == new Vector3(20f, 20f, 0f) && added.Stock == added.Position && model.Rows().Count == count + 1,
            $"a copy is a new row at the end, 10 units to the right of the original, under a new name: {first.Message}");
        check.That(first.Message.StartsWith("Tank 1 (row 0) copied as row ", StringComparison.Ordinal) && first.Message.Contains("to its right", StringComparison.Ordinal) && first.Message.EndsWith("Move it where you want it.", StringComparison.Ordinal),
            $"the page is told where it stands: \"{first.Message}\"");
        check.That(model.Rows("", changedOnly: true).Select(row => row.Index).SequenceEqual([count]) && !model.Row(0)!.Added && !model.Row(0)!.Changed, "the list of changed rows holds the copy, and the original is not changed");
        check.That(model.ChangeSummary() == $"1 unit copied: Tank 1 copy (row {count})." && model.UnsavedChangeCount == 1 && model.HasUnsavedChanges, $"the changes are summarised and counted: \"{model.ChangeSummary()}\"");

        DuplicateOutcome second = model.Duplicate(0);
        DuplicateOutcome ghost = model.Duplicate(1);
        check.That(second.Ok && model.Row(second.Row!.Value)!.Name == "Tank 1 copy 2" && ghost.Ok && model.Row(ghost.Row!.Value)!.Name.Length == 0 && model.Row(ghost.Row!.Value)!.Label == "Ghost",
            "a second copy of the same unit is numbered, and a unit with no name has a copy with none");
        check.That(model.ChangeSummary() == $"3 units copied: Tank 1 copy (row {count}); Tank 1 copy 2 (row {count + 1}); Ghost (row {count + 2}).", $"the summary lists them: \"{model.ChangeSummary()}\"");
        DuplicateOutcome copyOfCopy = model.Duplicate(count);
        check.That(copyOfCopy.Ok && model.Row(copyOfCopy.Row!.Value)!.Name == "Tank 1 copy copy" && model.Row(copyOfCopy.Row!.Value)!.Position == new Vector3(30f, 20f, 0f), "a copy of a copy is allowed, named after it and shifted from it");

        DuplicateOutcome refused = model.Duplicate(2);
        check.That(!refused.Ok && refused.Message.StartsWith("Only units can be copied for now, and ", StringComparison.Ordinal) && !model.Duplicate(99).Ok && !model.Duplicate(-1).Ok && model.Rows().Count == count + 4,
            $"a path point and a row that is not there are refused in words, and nothing is added: \"{refused.Message}\"");

        // A unit near the edge of the terrain's square is copied to its left, so the copy stays inside.
        model.Move(0, "505", "20", "0");
        DuplicateOutcome edge = model.Duplicate(0);
        check.That(edge.Ok && model.Row(edge.Row!.Value)!.Position == new Vector3(495f, 20f, 0f) && edge.Message.Contains("to its left", StringComparison.Ordinal), $"a copy that would leave the square goes to the left instead: {edge.Message}");

        // What is saved holds the copies, strictly; after the save nothing is unsaved, and undoing a copy is an unsaved change again.
        check.That(model.Session!.Validate().CanSave && model.Session.Additions().Count == 5, "the edit with its copies can be saved");
        string mods = Path.Combine(folder, "mods");
        SaveOutcome saved = model.SaveAsMod(mods, new ModInfo("copy-test", "Copy test"), []);
        byte[] world = saved.Staged is null ? [] : File.ReadAllBytes(Path.Combine(saved.Staged.Root, "data", "worlds", "world100.wrd"));
        WorldBody written = WorldBody.Read(world);
        check.That(saved.Ok && world.AsSpan().SequenceEqual(model.Session.ToBytes()) && written.Things.Count == count + 5 && written.Write().AsSpan().SequenceEqual(world) && model.UnsavedChangeCount == 0,
            $"Save as mod writes the level with its copies, which reads back strictly, and the edit counts as saved: {saved.Message}");
        model.Session.Undo();
        check.That(model.Rows().Count == count + 4 && model.UnsavedChangeCount > 0, "taking the last copy back (or the move before it) leaves something unsaved again");
    }
}
