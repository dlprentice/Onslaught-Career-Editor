// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// Replacing a compiled script of a world body as an undoable edit: the command, what the session says changed, and what validation lets through. Nothing
/// here touches Godot or a file; every script is authored here.
/// </summary>
internal static class LevelScriptEditTests
{
    internal static void Run(string output, Checks check)
    {
        check.Suite("level script edits");
        Command(check);
        Snapshots(check);
        Session(check);
        StoredFields(check);
        Unstorable(check);
        Validation(check);
        BrokenScripts(check);
        Model(output, check);
    }

    /// <summary>The replacement the checks that save use: the shape of the authored alpha, as a program the checker accepts (the authored one is a stand-in that is never run).</summary>
    private static MissionScript Saveable() => LevelScriptCheckerTests.WellFormed("alpha", [0, 3], ["go2"], ("PostEvent", 1));

    private static WorldBody Authored() => LevelScriptTests.Body(LevelScriptTests.Script("alpha", [0, 3], ["go"], ("PostEvent", 1)), LevelScriptTests.Script("beta", [], []));

    private static void Command(Checks check)
    {
        WorldBody body = Authored();
        MissionScript original = body.Scripts[0], replacement = LevelScriptTests.Script("alpha", [0], ["stop"], ("PostEvent", 1));
        byte[] originalBytes = WorldBodyWriter.ScriptBytes(original), replacementBytes = WorldBodyWriter.ScriptBytes(replacement);
        ReplaceScript replace = new(0, replacement);
        replace.Do(body);
        check.That(!ReferenceEquals(body.Scripts[0], replacement) && WorldBodyWriter.ScriptBytes(body.Scripts[0]).AsSpan().SequenceEqual(replacementBytes) &&
                   replace.Description == "Replace script alpha" && replace.ScriptIndex == 0 && !ReferenceEquals(replace.Script, replacement) &&
                   WorldBodyWriter.ScriptBytes(replace.Script).AsSpan().SequenceEqual(replacementBytes),
            "a replacement puts a copy of the new script in the old one's place and says so in words");
        replace.Undo(body);
        check.That(WorldBodyWriter.ScriptBytes(body.Scripts[0]).AsSpan().SequenceEqual(originalBytes), "taking it back puts the script that was there back");
        replace.Do(body);
        check.That(WorldBodyWriter.ScriptBytes(body.Scripts[0]).AsSpan().SequenceEqual(replacementBytes), "and it can be made again");
        check.That(Throws(() => replace.Do(body)), "a replacement already made is not made twice");
        replace.Undo(body);
        check.That(Throws(() => replace.Undo(body)) && WorldBodyWriter.ScriptBytes(body.Scripts[0]).AsSpan().SequenceEqual(originalBytes), "and one taken back is not taken back twice");
        check.That(Throws(() => new ReplaceScript(-1, replacement).Do(body)) && Throws(() => new ReplaceScript(2, replacement).Do(body)) && Throws(() => new ReplaceScript(int.MaxValue, replacement).Do(body)),
            "a script number outside the world's list is refused");
        MissionScript other = LevelScriptTests.Script("Alpha", [], []);
        check.That(Throws(() => new ReplaceScript(0, other).Do(body)) && WorldBodyWriter.ScriptBytes(body.Scripts[0]).AsSpan().SequenceEqual(originalBytes) && Throws(() => new ReplaceScript(1, replacement).Do(body)) && body.Scripts[1].Name == "beta",
            "a script keeps its name (in its exact spelling), and a refused replacement changes nothing");
    }

    private static void Snapshots(Checks check)
    {
        byte[] baseline = Authored().Write();
        EditSession session = new(baseline);
        MissionScript priorReference = session.Body.Scripts[0], caller = Saveable();
        byte[] expected = WorldBodyWriter.ScriptBytes(caller);
        ReplaceScript command = new(0, caller);
        caller.Code.Symbols[0].Value = new ScriptInt(17);
        caller.Code.EventPcs[0] = 99;
        caller.Code.Instructions.Clear();
        caller.Code.EventFunctions[0].Parameters.Clear();
        caller.Trailer[0] = 42;
        session.Apply(command);
        int events = 0;
        session.Changed += () => events++;
        caller.Name = "changed after Apply";
        caller.Code.Tail1 = 123;
        caller.Trailer[2] = 8;
        MissionScript exposed = command.Script;
        exposed.Code.Symbols[0].Name = "changed through getter";
        exposed.Trailer[1] = 7;
        priorReference.Code.Symbols[0].Value = new ScriptText("changed while set aside");
        check.That(events == 0 && WorldBodyWriter.ScriptBytes(session.Body.Scripts[0]).AsSpan().SequenceEqual(expected) &&
                   WorldBodyWriter.ScriptBytes(command.Script).AsSpan().SequenceEqual(expected),
            "caller changes before and after Apply and changes to the getter copy do not silently change the working edit");
        session.Body.Scripts[0].Code.EventPcs[0] = 55;
        check.That(session.Undo() && session.ToBytes().AsSpan().SequenceEqual(baseline) && session.Redo() &&
                   WorldBodyWriter.ScriptBytes(session.Body.Scripts[0]).AsSpan().SequenceEqual(expected) && events == 2,
            "undo restores the captured prior record and redo restores the captured replacement even if both exposed objects were mutated");
    }

    private static void Session(Checks check)
    {
        byte[] bytes = Authored().Write();
        EditSession session = new(bytes);
        check.That(session.ScriptChanges().Count == 0 && session.Changes().Count == 0, "a session starts with no script changed");
        MissionScript edited = LevelScriptTests.Script("alpha", [0, 3], ["go2"], ("PostEvent", 1));
        session.Apply(new ReplaceScript(0, edited));
        IReadOnlyList<ScriptChange> changes = session.ScriptChanges();
        check.That(changes.Count == 1 && changes[0] is { Index: 0, Name: "alpha", InstructionsFrom: 2, InstructionsTo: 2, SymbolsFrom: 1, SymbolsTo: 1, CodeDiffers: false } &&
                   changes[0].Symbols.Count == 1 && changes[0].Symbols[0].Index == 0 && changes[0].Symbols[0].From.EndsWith("\"go\"", StringComparison.Ordinal) && changes[0].Symbols[0].To.EndsWith("\"go2\"", StringComparison.Ordinal),
            $"the session says which script changed and which constant: {(changes.Count > 0 ? string.Join("; ", changes[0].Symbols.Select(symbol => $"{symbol.Index}: {symbol.From} -> {symbol.To}")) : "none")}");
        check.That(session.Changes().Count == 0 && session.UndoDescription == "Replace script alpha", "no object moved, and the undo list names the script");
        session.Apply(new ReplaceScript(0, Saveable()));
        ValidationReport report = session.Validate();
        check.That(report.CanSave && report.Warnings.Count == 0, $"a replaced script is a change that can be saved: {string.Join(", ", report.Errors.Select(finding => finding.Code))}");
        session.Undo();

        session.Apply(new ReplaceScript(0, LevelScriptTests.Script("alpha", [0, 3], ["go2"], ("PostEvent", 2), ("Pause", 1))));
        ScriptChange longer = session.ScriptChanges().Single();
        check.That(longer.CodeDiffers && longer.InstructionsFrom == 2 && longer.InstructionsTo == 4, $"a script with more calls says its instruction count and that its code differs: {longer.InstructionsFrom} to {longer.InstructionsTo}");

        session.Apply(new ReplaceScript(0, LevelScriptTests.Script("alpha", [0, 3], ["go", "more"], ("PostEvent", 1))));
        ScriptChange extra = session.ScriptChanges().Single();
        check.That(extra.SymbolsFrom == 1 && extra.SymbolsTo == 2 && extra.Symbols.Count == 1 && extra.Symbols[0].Index == 1 && extra.Symbols[0].From == "(none)" && extra.Symbols[0].To.EndsWith("\"more\"", StringComparison.Ordinal),
            $"a symbol the baseline lacks is said to be new: {string.Join("; ", extra.Symbols.Select(symbol => $"{symbol.Index}: {symbol.From} -> {symbol.To}"))}");
        MissionScript marked = LevelScriptTests.Script("alpha", [0, 3], ["go"], ("PostEvent", 1));
        marked.Trailer[9] = 1;
        session.Apply(new ReplaceScript(0, marked));
        ScriptChange trailer = session.ScriptChanges().Single();
        check.That(trailer.Symbols.Count == 0 && !trailer.CodeDiffers && trailer.InstructionsFrom == trailer.InstructionsTo, "a record that differs in its trailer alone is still a change");

        session.UndoAll();
        check.That(session.ScriptChanges().Count == 0 && session.Validate().Errors.Select(finding => finding.Code).SequenceEqual(["no-change"]), "taking every change back leaves nothing to save");
        session.Apply(new ReplaceScript(0, edited));
        session.Apply(new ReplaceScript(0, session.ShippedScript(0)));
        check.That(session.ScriptChanges().Count == 0 && session.Validate().Errors.Select(finding => finding.Code).SequenceEqual(["no-change"]),
            "putting the shipped script back is a change that can itself be taken back, and leaves the world as it was loaded");
        check.That(session.UndoDescription == "Replace script alpha" && session.Undo() && session.ScriptChanges().Count == 1, "and taking that back brings the edit back");
        check.That(!ReferenceEquals(session.ShippedScript(0), session.ShippedScript(0)), "every call to ask for the shipped script gives a copy of its own");
        MissionScript shipped = session.ShippedScript(1);
        check.That(WorldBodyWriter.ScriptBytes(shipped).AsSpan().SequenceEqual(WorldBodyWriter.ScriptBytes(session.Body.Scripts[1])) && !ReferenceEquals(shipped, session.Body.Scripts[1]) &&
                   ThrowsArgument(() => session.ShippedScript(-1)) && ThrowsArgument(() => session.ShippedScript(2)),
            "the shipped script is a fresh copy of the baseline's, and a script number the world lacks is refused");

        EditSession baseWorld = new(bytes, isBaseWorld: true);
        baseWorld.Apply(new ReplaceScript(0, Saveable()));
        report = baseWorld.Validate();
        EditSession moved = new(bytes, isBaseWorld: true);
        moved.Apply(new MoveObject(0, moved.Body.Things[0].Init.Position + new Vector3(1, 0, 0)));
        check.That(moved.Validate().Warnings.Select(finding => finding.Code).SequenceEqual(["base-world"]), "a base world with a thing moved and no script replaced has no word about scripts");
        check.That(report.CanSave && report.Warnings.Select(finding => finding.Code).SequenceEqual(["base-world-scripts"]),
            $"a base world's replaced script is saved with a warning that every level loading it runs the new one: {string.Join(", ", report.Warnings.Select(finding => finding.Code))}");
    }

    private static void StoredFields(Checks check)
    {
        byte[] baseline = LevelScriptTests.Body(Saveable()).Write();
        (string What, Action<MissionScript> Edit, string? Field)[] cases =
        [
            ("instruction opcode", s => s.Code.Instructions[0] = s.Code.Instructions[0] with { Opcode = 7 }, "instruction 0"),
            ("instruction operand", s => s.Code.Instructions[0] = s.Code.Instructions[0] with { Attribute = 8 }, "instruction 0"),
            ("fixed event entry", s => s.Code.EventPcs[0]++, "event 0 entry"),
            ("symbol name", s => s.Code.Symbols[0].Name += "x", null),
            ("symbol data type", s => s.Code.Symbols[0].DataType = 4, null),
            ("symbol value", s => s.Code.Symbols[0].Value = new ScriptInt(3), null),
            ("symbol type/line", s => s.Code.Symbols[0].SymbolType++, null),
            ("symbol index", s => s.Code.Symbols[0].Index++, null),
            ("symbol flag", s => s.Code.Symbols[0].Flag++, null),
            ("next symbol index", s => s.Code.NextSymbolIndex++, "next symbol index"),
            ("handler entry", s => s.Code.EventFunctions[0].EntryPc++, "handler 0"),
            ("handler parameter", s => s.Code.EventFunctions[0].Parameters[0]++, "handler 0"),
            ("first trailing word", s => s.Code.Tail1++, "first trailing word"),
            ("second trailing word", s => s.Code.Tail2++, "second trailing word"),
            ("trailer byte", s => s.Trailer[9]++, "trailer"),
        ];
        foreach ((string what, Action<MissionScript> edit, string? field) in cases)
        {
            EditSession session = new(baseline);
            MissionScript changed = session.ShippedScript(0);
            edit(changed);
            session.Apply(new ReplaceScript(0, changed));
            ScriptChange change = session.ScriptChanges().Single();
            bool explained = field is null
                ? change.Symbols.Count == 1 && change.Symbols[0].From != change.Symbols[0].To
                : change.Fields.Any(entry => entry.Field == field && entry.From != entry.To);
            string summary = change.Describe();
            bool summarized = field is null ? summary.Contains("symbol", StringComparison.Ordinal)
                : field.StartsWith("instruction ", StringComparison.Ordinal) ? summary.Contains("code differs", StringComparison.Ordinal)
                : summary.Contains(field, StringComparison.Ordinal);
            check.That(explained && summarized, $"a {what}-only record change identifies the field, gives different values and summarizes it: {summary}");
        }

        EditSession additions = new(baseline);
        MissionScript larger = additions.ShippedScript(0);
        larger.Code.Instructions.Add(new ScriptInstruction(23, -1));
        larger.Code.EventFunctions.Add(new EventFunction { EntryPc = 2 });
        larger.Code.Symbols.Add(new ScriptSymbol { Name = "added", DataType = 1, Value = new ScriptInt(1), Index = 2 });
        additions.Apply(new ReplaceScript(0, larger));
        ScriptChange added = additions.ScriptChanges().Single();
        check.That(added.Fields.Any(field => field.Field == "handler 1" && field.From == "(none)") &&
                   added.Fields.Any(field => field.Field.StartsWith("instruction ", StringComparison.Ordinal) && field.From == "(none)") &&
                   added.Symbols.Single().From == "(none)", "added instructions, handlers and symbols are listed from none");

        EditSession many = new(baseline);
        MissionScript manyEntries = many.ShippedScript(0);
        for (int i = 0; i < 5; i++) manyEntries.Code.EventPcs[i]++;
        many.Apply(new ReplaceScript(0, manyEntries));
        ScriptChange several = many.ScriptChanges().Single();
        check.That(several.Fields.Count == 5 && several.Describe().Contains("2 more fields differ", StringComparison.Ordinal),
            "a long summary names its first three changed fields and says how many more, while retaining every detail");

        float nan1 = BitConverter.UInt32BitsToSingle(0x7fc00001), nan2 = BitConverter.UInt32BitsToSingle(0x7fc00002);
        WorldBody vectors = LevelScriptTests.Body(LevelScriptTests.Script("alpha", [], []));
        vectors.Scripts[0].Code.Symbols.Add(new ScriptSymbol { Name = "v", DataType = 6, Value = new ScriptVector(new Vector3(0f, nan1, 0f)), Index = 0 });
        vectors.Scripts[0].Code.NextSymbolIndex = 1;
        EditSession bitChange = new(vectors.Write());
        MissionScript signed = bitChange.ShippedScript(0);
        signed.Code.Symbols[0].Value = new ScriptVector(new Vector3(-0f, nan2, 0f));
        bitChange.Apply(new ReplaceScript(0, signed));
        SymbolChange vector = bitChange.ScriptChanges().Single().Symbols.Single();
        check.That(vector.From.Contains("0x00000000", StringComparison.Ordinal) && vector.From.Contains("0x7fc00001", StringComparison.Ordinal) &&
                   vector.To.Contains("0x80000000", StringComparison.Ordinal) && vector.To.Contains("0x7fc00002", StringComparison.Ordinal),
            "vector components show their exact float bits, including signed zero and distinct NaN payloads");
    }

    private static void Unstorable(Checks check)
    {
        byte[] baseline = LevelScriptTests.Body(Saveable()).Write();
        (string What, Action<MissionScript> Break)[] cases =
        [
            ("wrong value type", s => s.Code.Symbols[0].Value = new ScriptText("not an integer")),
            ("unknown data type", s => s.Code.Symbols[0].DataType = 99),
            ("non-Latin-1 symbol", s => s.Code.Symbols[0].Name = "\u0100"),
            ("wrong trailer length", s => s.Trailer = new byte[9]),
            ("missing trailer", s => s.Trailer = null!),
            ("wrong entry count", s => s.Code.EventPcs = new int[12]),
            ("missing entries", s => s.Code.EventPcs = null!),
            ("missing code", s => s.Code = null!),
            ("missing symbol", s => s.Code.Symbols[0] = null!),
            ("missing symbol name", s => s.Code.Symbols[0].Name = null!),
            ("missing text value", s => s.Code.Symbols[1].Value = new ScriptText(null!)),
            ("missing handler", s => s.Code.EventFunctions[0] = null!),
        ];
        foreach ((string what, Action<MissionScript> breakScript) in cases)
        {
            EditSession session = new(baseline);
            MissionScript script = session.ShippedScript(0);
            breakScript(script);
            session.Apply(new ReplaceScript(0, script));
            ScriptChange change = session.ScriptChanges().Single();
            ValidationReport report = session.Validate();
            check.That(change.StorageError is { Length: > 0 } && change.Describe().StartsWith("cannot be saved: ", StringComparison.Ordinal) &&
                       !report.CanSave && report.Errors.Single() is { Code: "script-unstorable", Index: 0 } &&
                       report.Errors[0].Message.Contains(change.StorageError, StringComparison.Ordinal),
                $"{what} is reported by ScriptChanges and refused by Validate without throwing");
            check.That(session.Undo() && session.ToBytes().AsSpan().SequenceEqual(baseline), $"an edit with {what} can still be undone");
        }

        EditSession both = new(LevelScriptTests.Body(Saveable(), LevelScriptCheckerTests.WellFormed("beta", [0], [], ("PostEvent", 1))).Write());
        MissionScript first = both.ShippedScript(0), second = both.ShippedScript(1);
        first.Trailer = new byte[9];
        second.Code.EventPcs = new int[12];
        both.Apply(new ReplaceScript(0, first));
        both.Apply(new ReplaceScript(1, second));
        check.That(both.ScriptChanges().Count(change => change.StorageError is not null) == 2 &&
                   both.Validate().Errors.Select(error => (error.Code, error.Index)).SequenceEqual([("script-unstorable", 0), ("script-unstorable", 1)]),
            "each of two unstorable scripts is reported with its own index");

        EditSession tooLong = new(baseline);
        tooLong.Body.Scripts[0].Code.Instructions.AddRange(Enumerable.Repeat(new ScriptInstruction(0, 0), ByteReader.CountLimit + 1));
        ScriptChange excessive = tooLong.ScriptChanges().Single();
        check.That(excessive.StorageError?.Contains("reader's", StringComparison.Ordinal) == true &&
                   tooLong.Validate().Errors.Single() is { Code: "script-unstorable", Index: 0 },
            "an instruction count the strict reader refuses is reported before a large diff is assembled or an unreadable world is accepted");

        EditSession missing = new(baseline);
        missing.Body.Scripts[0] = null!;
        check.That(missing.ScriptChanges().Count == 0 && missing.Validate().Errors.Single().Code == "cannot-write",
            "a missing script record is refused as an unwritable world, without throwing while listing changes");
    }

    /// <summary>The real level-editor model on an authored archive: summary, refusal, save and undo/redo across script changes.</summary>
    private static void Model(string output, Checks check)
    {
        string folder = Path.Combine(output, "script-edit-summary"), game = Path.Combine(folder, "game");
        string resources = Path.Combine(game, "data", "resources");
        Directory.CreateDirectory(resources);
        File.WriteAllBytes(Path.Combine(resources, "100_res_PC.aya"), LevelTests.Unpack(LevelVectors.Archives.First(archive => archive.Name == "level-100").File));
        LevelEditorModel model = LevelEditorModel.ForGame(game);
        bool opened = model.Open(100) && model.Session is not null;
        check.That(opened, "the authored level opens for script-change summary checks");
        if (!opened) return;
        EditSession session = model.Session!;

        MissionScript trailer = session.ShippedScript(0);
        trailer.Trailer[0]++;
        session.Apply(new ReplaceScript(0, trailer));
        check.That(model.HasUnsavedChanges && model.UnsavedChangeCount == 1 &&
                   model.ChangeSummary() is { } summary && summary.Contains("1 script replaced: main", StringComparison.Ordinal) && summary.Contains("trailer:", StringComparison.Ordinal),
            "a trailer-only script change is unsaved and its named field appears in the model summary");
        check.That(session.Undo() && !model.HasUnsavedChanges && model.ChangeSummary() is null && session.Redo() && model.HasUnsavedChanges,
            "undo and redo update the model's script-only unsaved state");

        MissionScript invalid = session.ShippedScript(0);
        invalid.Trailer = new byte[9];
        session.Apply(new ReplaceScript(0, invalid));
        string refusedFolder = Path.Combine(folder, "refused-mods");
        SaveOutcome refused = model.SaveAsMod(refusedFolder, new ModInfo("bad-script", "Bad script"), [game]);
        check.That(model.HasUnsavedChanges && model.UnsavedChangeCount == 1 && model.ChangeSummary()!.Contains("cannot be saved:", StringComparison.Ordinal) &&
                   !refused.Ok && refused.Message.Contains("cannot be saved", StringComparison.Ordinal) && !Directory.Exists(refusedFolder),
            "an unstorable script remains unsaved, explains why, and cannot create a mod folder");

        check.That(model.Open(100) && model.Session is not null, "reopening the authored level resets the session");
        session = model.Session!;
        MissionScript valid = LevelScriptCheckerTests.WellFormed("main", [0], [], ("Pause", 1));
        session.Apply(new ReplaceScript(0, valid));
        check.That(session.Validate().CanSave && model.HasUnsavedChanges, "a valid authored replacement can be saved and starts unsaved");
        string mods = Path.Combine(folder, "mods");
        SaveOutcome saved = model.SaveAsMod(mods, new ModInfo("script-edit", "Script edit"), [game]);
        check.That(saved.Ok && !model.HasUnsavedChanges && model.UnsavedChangeCount == 0, $"saving the script's exact state clears the unsaved flag: {saved.Message}");
        MissionScript later = ScriptCopy.Of(session.Body.Scripts[0]);
        int originalTail = session.ShippedScript(0).Code.Tail1;
        int changedTail = originalTail ^ 1;
        later.Code.Tail1 = changedTail == later.Code.Tail1 ? originalTail ^ 2 : changedTail;
        session.Apply(new ReplaceScript(0, later));
        check.That(model.HasUnsavedChanges && model.UnsavedChangeCount == 1 &&
                   session.ScriptChanges().Single().Fields.Any(field => field.Field == "first trailing word") &&
                   model.ChangeSummary()!.Contains("more field", StringComparison.Ordinal),
            $"a later same-size script edit is unsaved even though the number of changed scripts is the same: {model.HasUnsavedChanges}, {model.UnsavedChangeCount}, {model.ChangeSummary()}");
        check.That(session.Undo() && !model.HasUnsavedChanges && session.Redo() && model.HasUnsavedChanges,
            "undoing to the saved script clears the flag and redoing the later edit sets it again");

        check.That(session.Undo() && !model.HasUnsavedChanges, "the saved script state is restored before structural changes");
        session.Body.Scripts[0].Name = "renamed";
        check.That(model.HasUnsavedChanges && model.UnsavedChangeCount >= 1 && session.Validate().Errors.Any(error => error.Code == "scripts-changed"),
            "renaming a saved script remains unsaved even when the script list no longer matches");
        session.Body.Scripts[0].Name = "main";
        check.That(!model.HasUnsavedChanges, "restoring the saved script name restores the saved state");

        foreach ((string what, Action<EditSession> change, string errorCode) in new (string, Action<EditSession>, string)[]
        {
            ("renamed", edit => edit.Body.Scripts[0].Name = "renamed", "scripts-changed"),
            ("removed", edit => edit.Body.Scripts.RemoveAt(0), "scripts-changed"),
            ("added", edit => edit.Body.Scripts.Add(edit.ShippedScript(0)), "scripts-changed"),
            ("missing", edit => edit.Body.Scripts[0] = null!, "cannot-write"),
        })
        {
            check.That(model.Open(100) && model.Session is not null, $"a fresh authored level opens before the {what} script test");
            session = model.Session!;
            MissionScript replacement = session.ShippedScript(0);
            replacement.Trailer[0]++;
            session.Apply(new ReplaceScript(0, replacement));
            change(session);
            SaveOutcome blocked = model.SaveAsMod(Path.Combine(folder, "unsupported-" + what), new ModInfo("invalid", "Invalid"), [game]);
            check.That(model.HasUnsavedChanges && model.UnsavedChangeCount >= 1 && session.Validate().Errors.Any(error => error.Code == errorCode) &&
                       model.ChangeSummary() is { Length: > 0 } && !blocked.Ok && !Directory.Exists(Path.Combine(folder, "unsupported-" + what)),
                $"a {what} script list retains unsaved state and cannot be published, even with a previous replacement");
        }

        check.That(model.Open(100) && model.Session is not null, "a fresh authored level opens before an unsupported field change");
        session = model.Session!;
        session.Body.MapNumber++;
        check.That(model.HasUnsavedChanges && model.UnsavedChangeCount == 1 && model.ChangeSummary() is { Length: > 0 } &&
                   session.Validate().Errors.Any(error => error.Code == "other-change"), "an unsupported non-list field change is unsaved and cannot be written as a mod");
    }

    private static void Validation(Checks check)
    {
        byte[] bytes = Authored().Write();
        EditSession dropped = new(bytes);
        dropped.Body.Scripts.RemoveAt(1);
        check.That(dropped.Validate().Errors.Select(finding => finding.Code).SequenceEqual(["scripts-changed"]) && dropped.ScriptChanges().Count == 0, "a script dropped is not a replacement: the save is refused");
        EditSession added = new(bytes);
        added.Body.Scripts.Add(LevelScriptTests.Script("gamma", [], []));
        check.That(added.Validate().Errors.Select(finding => finding.Code).SequenceEqual(["scripts-changed"]) && added.ScriptChanges().Count == 0, "nor is one added");
        EditSession renamed = new(bytes);
        renamed.Body.Scripts[1].Name = "gamma";
        check.That(renamed.Validate().Errors.Select(finding => finding.Code).SequenceEqual(["scripts-changed"]) && renamed.ScriptChanges().Count == 0, "and neither is a script renamed");
        EditSession reordered = new(bytes);
        (reordered.Body.Scripts[0], reordered.Body.Scripts[1]) = (reordered.Body.Scripts[1], reordered.Body.Scripts[0]);
        check.That(reordered.Validate().Errors.Select(finding => finding.Code).SequenceEqual(["scripts-changed"]) && reordered.ScriptChanges().Count == 0, "or two swapped");

        EditSession both = new(bytes);
        both.Apply(new MoveObject(0, both.Body.Things[0].Init.Position + new Vector3(1, 0, 0)));
        both.Apply(new ReplaceScript(0, Saveable()));
        check.That(both.Validate().CanSave && both.Changes().Count == 1 && both.ScriptChanges().Count == 1, "a moved object and a replaced script are both edits this editor makes");

        EditSession other = new(bytes);
        other.Apply(new ReplaceScript(0, Saveable()));
        other.Body.MapNumber += 1;
        check.That(other.Validate().Errors.Select(finding => finding.Code).SequenceEqual(["other-change"]), "anything else that differs still stops the save");

        EditSession floats = new(WithFloat(0f).Write());
        MissionScript signed = LevelScriptTests.Script("alpha", [], []);
        signed.Code.Symbols.Add(new ScriptSymbol { Name = "const data0", DataType = 2, Value = new ScriptFloat(-0f), Index = 0, Flag = 1 });
        signed.Code.NextSymbolIndex = 1;
        floats.Apply(new ReplaceScript(0, signed));
        ScriptChange change = floats.ScriptChanges().Single();
        check.That(change.Symbols.Count == 1 && change.Symbols[0].From.Contains("0x00000000", StringComparison.Ordinal) && change.Symbols[0].To.Contains("0x80000000", StringComparison.Ordinal),
            $"a float's sign bit is a change, and is shown in bits: {string.Join("; ", change.Symbols.Select(symbol => $"{symbol.From} -> {symbol.To}"))}");
    }

    /// <summary>
    /// A replaced script that breaks one of the game's rules is not saved. These are the ten structurally broken scripts an independent review made, each
    /// of which could be saved before <see cref="EditSession.Validate"/> called the checker.
    /// </summary>
    private static void BrokenScripts(Checks check)
    {
        byte[] bytes = LevelScriptTests.Body(LevelScriptCheckerTests.WellFormed("alpha", [0, 3], ["go"], ("PostEvent", 1)), LevelScriptCheckerTests.WellFormed("beta", [], [])).Write();
        (string What, string Rule, Action<MissionScript> Break)[] cases =
        [
            ("PUSH of symbol 999 (the table has 2)", "symbol-operand", s => s.Code.Instructions.Insert(0, new ScriptInstruction(5, 999))),
            ("JMP to instruction 12345", "jump-target", s => s.Code.Instructions.Insert(0, new ScriptInstruction(20, 12345))),
            ("opcode 99 (the VM has 27)", "opcode", s => s.Code.Instructions.Insert(0, new ScriptInstruction(99, 0))),
            ("CALL of function 250 (the table has fewer)", "call-function", s => s.Code.Instructions.Insert(0, new ScriptInstruction(24, 250 | (1 << 16)))),
            ("init's entry point at 777", "entry-point", s => s.Code.EventPcs[0] = 777),
            ("nextSymbolIndex 50 for a table of 2", "next-symbol-index", s => s.Code.NextSymbolIndex = 50),
            ("a symbol whose number is not its place", "symbol-index", s => s.Code.Symbols[0].Index = 7),
            ("a handler whose event symbol is 42", "handler-parameter", s => s.Code.EventFunctions[0].Parameters[0] = 42),
            ("a handler whose entry point is -5", "handler-entry", s => s.Code.EventFunctions[0].EntryPc = -5),
            ("no instructions at all, entry points kept", "empty-code", s => s.Code.Instructions.Clear()),
        ];
        foreach ((string what, string rule, Action<MissionScript> doBreak) in cases)
        {
            EditSession session = new(bytes);
            MissionScript script = session.ShippedScript(0);
            doBreak(script);
            session.Apply(new ReplaceScript(0, script));
            ValidationReport report = session.Validate();
            check.That(!report.CanSave && report.Errors.Count > 0 && report.Errors.All(error => error.Code == "script-broken" && error.Index == 0 && error.Message.StartsWith("Script alpha: ", StringComparison.Ordinal)) &&
                       report.Errors.Any(error => ScriptChecker.Check(script).Any(problem => problem.Rule == rule && problem.Message == error.Message)),
                $"{what} is not saved: {string.Join(" | ", report.Errors.Select(error => $"{error.Code} {error.Message}"))}");
        }

        // One finding for each problem, and a good script beside a broken one is not blamed.
        EditSession many = new(bytes);
        MissionScript twice = many.ShippedScript(0);
        twice.Code.Instructions.Insert(0, new ScriptInstruction(5, 999));
        twice.Code.Instructions.Insert(0, new ScriptInstruction(99, 0));
        many.Apply(new ReplaceScript(0, twice));
        many.Apply(new ReplaceScript(1, LevelScriptCheckerTests.WellFormed("beta", [0], [], ("Pause", 1))));
        IReadOnlyList<ScriptProblem> problems = ScriptChecker.Check(twice);
        List<Finding> errors = [.. many.Validate().Errors];
        check.That(problems.Count >= 2 && errors.Count == problems.Count && errors.Select(error => error.Message).SequenceEqual(problems.Select(problem => problem.Message)) && errors.All(error => error.Index == 0),
            $"each problem of a broken script is a finding of its own, and only the broken script is blamed: {errors.Count} findings for {problems.Count} problems");

        // A script that is broken in the baseline and left alone is the game's own business; one replaced is judged.
        WorldBody shipped = WorldBody.Read(bytes);
        shipped.Scripts[0].Code.Instructions.Insert(0, new ScriptInstruction(5, 999));
        EditSession kept = new(shipped.Write());
        kept.Apply(new ReplaceScript(1, LevelScriptCheckerTests.WellFormed("beta", [0], [], ("Pause", 1))));
        check.That(kept.Validate().CanSave && ScriptChecker.Check(kept.Body.Scripts[0]).Count > 0, "a broken script the world shipped with, left alone, does not stop a save of another script");
        MissionScript again = kept.ShippedScript(0);
        again.Code.Instructions.Add(new ScriptInstruction(23, -1));
        kept.Apply(new ReplaceScript(0, again));
        check.That(!kept.Validate().CanSave && kept.Validate().Errors.All(error => error.Code == "script-broken" && error.Index == 0), "but when it is replaced (here by another that is broken the same way), it is judged");
        kept.Undo();
        kept.Apply(new ReplaceScript(0, kept.ShippedScript(0)));
        check.That(kept.Validate().CanSave && kept.ScriptChanges().Count == 1, "and when it is put back as it shipped, it is no change at all");

        // A base world's replaced script is judged as well, and the warning about the levels that load it stays.
        EditSession baseWorld = new(bytes, isBaseWorld: true);
        MissionScript broken = baseWorld.ShippedScript(0);
        broken.Code.EventPcs[1] = 99;
        baseWorld.Apply(new ReplaceScript(0, broken));
        ValidationReport baseReport = baseWorld.Validate();
        check.That(!baseReport.CanSave && baseReport.Errors.Select(error => error.Code).SequenceEqual(["script-broken"]) && baseReport.Warnings.Select(warning => warning.Code).SequenceEqual(["base-world-scripts"]),
            $"a base world's broken script is refused and the warning about its other levels stays: {string.Join(",", baseReport.Errors.Select(error => error.Code))} / {string.Join(",", baseReport.Warnings.Select(warning => warning.Code))}");
    }

    private static WorldBody WithFloat(float value)
    {
        WorldBody body = LevelScriptTests.Body(LevelScriptTests.Script("alpha", [], []));
        body.Scripts[0].Code.Symbols.Add(new ScriptSymbol { Name = "const data0", DataType = 2, Value = new ScriptFloat(value), Index = 0, Flag = 1 });
        body.Scripts[0].Code.NextSymbolIndex = 1;
        return body;
    }

    private static bool Throws(Action action)
    {
        try
        {
            action();
            return false;
        }
        catch (InvalidOperationException)
        {
            return true;
        }
    }

    private static bool ThrowsArgument(Action action)
    {
        try
        {
            action();
            return false;
        }
        catch (ArgumentOutOfRangeException)
        {
            return true;
        }
    }
}
