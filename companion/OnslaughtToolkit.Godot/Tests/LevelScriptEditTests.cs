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
        Session(check);
        Validation(check);
    }

    private static WorldBody Authored() => LevelScriptTests.Body(LevelScriptTests.Script("alpha", [0, 3], ["go"], ("PostEvent", 1)), LevelScriptTests.Script("beta", [], []));

    private static void Command(Checks check)
    {
        WorldBody body = Authored();
        MissionScript original = body.Scripts[0], replacement = LevelScriptTests.Script("alpha", [0], ["stop"], ("PostEvent", 1));
        ReplaceScript replace = new(0, replacement);
        replace.Do(body);
        check.That(ReferenceEquals(body.Scripts[0], replacement) && replace.Description == "Replace script alpha" && replace.ScriptIndex == 0 && ReferenceEquals(replace.Script, replacement),
            "a replacement puts the new script in the old one's place and says so in words");
        replace.Undo(body);
        check.That(ReferenceEquals(body.Scripts[0], original), "taking it back puts the script that was there back");
        replace.Do(body);
        check.That(ReferenceEquals(body.Scripts[0], replacement), "and it can be made again");
        check.That(Throws(() => replace.Do(body)), "a replacement already made is not made twice");
        replace.Undo(body);
        check.That(Throws(() => replace.Undo(body)) && ReferenceEquals(body.Scripts[0], original), "and one taken back is not taken back twice");
        check.That(Throws(() => new ReplaceScript(-1, replacement).Do(body)) && Throws(() => new ReplaceScript(2, replacement).Do(body)) && Throws(() => new ReplaceScript(int.MaxValue, replacement).Do(body)),
            "a script number outside the world's list is refused");
        MissionScript other = LevelScriptTests.Script("Alpha", [], []);
        check.That(Throws(() => new ReplaceScript(0, other).Do(body)) && ReferenceEquals(body.Scripts[0], original) && Throws(() => new ReplaceScript(1, replacement).Do(body)) && body.Scripts[1].Name == "beta",
            "a script keeps its name (in its exact spelling), and a refused replacement changes nothing");
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
        ValidationReport report = session.Validate();
        check.That(report.CanSave && report.Warnings.Count == 0, $"a replaced script is a change that can be saved: {string.Join(", ", report.Errors.Select(finding => finding.Code))}");

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
        baseWorld.Apply(new ReplaceScript(0, edited));
        report = baseWorld.Validate();
        EditSession moved = new(bytes, isBaseWorld: true);
        moved.Apply(new MoveObject(0, moved.Body.Things[0].Init.Position + new Vector3(1, 0, 0)));
        check.That(moved.Validate().Warnings.Select(finding => finding.Code).SequenceEqual(["base-world"]), "a base world with a thing moved and no script replaced has no word about scripts");
        check.That(report.CanSave && report.Warnings.Select(finding => finding.Code).SequenceEqual(["base-world-scripts"]),
            $"a base world's replaced script is saved with a warning that every level loading it runs the new one: {string.Join(", ", report.Warnings.Select(finding => finding.Code))}");
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
        both.Apply(new ReplaceScript(0, LevelScriptTests.Script("alpha", [0, 3], ["go2"], ("PostEvent", 1))));
        check.That(both.Validate().CanSave && both.Changes().Count == 1 && both.ScriptChanges().Count == 1, "a moved object and a replaced script are both edits this editor makes");

        EditSession other = new(bytes);
        other.Apply(new ReplaceScript(0, LevelScriptTests.Script("alpha", [0, 3], ["go2"], ("PostEvent", 1))));
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
