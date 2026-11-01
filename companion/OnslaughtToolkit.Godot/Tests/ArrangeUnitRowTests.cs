// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Unit-row placement against an authored level fixture; no game installation or staging is used.</summary>
internal static class ArrangeUnitRowTests
{
    internal static void Run(string outputDirectory, Checks check)
    {
        check.Suite("arrange units in a row");
        string game = LevelEditorTests.GameWithLevels(Path.Combine(outputDirectory, "arrange-unit-row"));
        LevelEditorModel model = LevelEditorModel.ForGame(game);
        if (model.Levels.Count == 0 || !model.Open(model.Levels[0].Level) || model.Session is null)
        {
            check.Fail("the authored test level opens");
            return;
        }
        EditSession session = model.Session;
        int[] units = session.Body.Things.Select((thing, row) => (thing, row))
            .Where(item => DuplicateObject.CanCopy(item.thing)).Select(item => item.row).Take(2).Reverse().ToArray();
        int other = session.Body.Things.FindIndex(thing => !DuplicateObject.CanCopy(thing));
        if (units.Length < 2 || other < 0)
        {
            check.Fail("the authored test level has two units and another object");
            return;
        }

        Vector3[] original = session.Body.Things.Select(thing => thing.Init.Position).ToArray();
        byte[] baseline = session.ToBytes();
        int notifications = 0;
        model.Changed += () => notifications++;
        Vector2 first = new(40, 60), step = new(12, 3);
        MoveOutcome placed = model.ArrangeUnitsInRow(units, first, step);
        Vector3 a = session.Body.Things[units[0]].Init.Position, b = session.Body.Things[units[1]].Init.Position;
        check.That(placed.Result == MoveResult.Moved && notifications == 1 && session.CanUndo &&
                   a.X == first.X && a.Y == first.Y && b.X == first.X + step.X && b.Y == first.Y + step.Y &&
                   SameBits(a.Z, original[units[0]].Z) && SameBits(b.Z, original[units[1]].Z) &&
                   session.Body.Things.Select((thing, row) => (thing, row))
                       .Where(item => !units.Contains(item.row)).All(item => item.thing.Init.Position == original[item.row]),
                   "selected units move in order as one edit; their heights and all unselected objects stay put");
        byte[] arranged = session.ToBytes();
        MoveOutcome same = model.ArrangeUnitsInRow(units, first, step);
        check.That(same.Result == MoveResult.Unchanged && notifications == 1 && session.ToBytes().SequenceEqual(arranged),
                   "placing an already arranged row does not add a change");

        MoveOutcome[] refusals =
        [
            model.ArrangeUnitsInRow(null, first, step),
            model.ArrangeUnitsInRow([], first, step),
            model.ArrangeUnitsInRow([units[0], units[0]], first, step),
            model.ArrangeUnitsInRow([units[0], session.Body.Things.Count], first, step),
            model.ArrangeUnitsInRow([units[0], other], first, step),
            model.ArrangeUnitsInRow(units, new Vector2(float.NaN, first.Y), step),
            model.ArrangeUnitsInRow(units, first, new Vector2(float.PositiveInfinity, 0)),
            model.ArrangeUnitsInRow(units, new Vector2(-1, first.Y), step),
            model.ArrangeUnitsInRow(units, first, Vector2.Zero),
            model.ArrangeUnitsInRow(units, first, new Vector2(float.Epsilon, 0)),
            model.ArrangeUnitsInRow(units, first, new Vector2(float.MaxValue, 0)),
        ];
        check.That(refusals.All(result => result.Result == MoveResult.Refused && result.Message.Length > 0) &&
                   notifications == 1 && session.ToBytes().SequenceEqual(arranged) && session.CanUndo,
                   "invalid selections, positions and spacing refuse the whole change without disturbing history");
        ObjectInit originalOther = session.Body.Things[other].Init;
        session.Body.Things[other].Init = session.Body.Things[units[0]].Init;
        MoveOutcome alias = model.ArrangeUnitsInRow(units, first + Vector2.One, step);
        session.Body.Things[other].Init = originalOther;
        check.That(alias.Result == MoveResult.Refused && notifications == 1 && session.ToBytes().SequenceEqual(arranged),
                   "a selection sharing data with another row is refused without moving either row");

        check.That(session.Undo() && notifications == 2 && session.ToBytes().SequenceEqual(baseline) && !session.CanUndo && session.CanRedo,
                   "one undo restores the whole row and leaves the previous world bytes intact");
        MoveOutcome refusedAfterUndo = model.ArrangeUnitsInRow([units[0], units[0]], first, step);
        check.That(refusedAfterUndo.Result == MoveResult.Refused && session.CanRedo && notifications == 2 && session.ToBytes().SequenceEqual(baseline),
                   "a refused arrangement after undo preserves the redo option");
        check.That(session.Redo() && notifications == 3 && session.ToBytes().SequenceEqual(arranged),
                   "one redo restores the whole arrangement");

        // If a selected row is altered outside the session, do not restore just the other selected rows.
        session.Body.Things[units[1]].Init.Position = b with { X = b.X + 1 };
        byte[] conflicting = session.ToBytes();
        bool refused = false;
        try { session.Undo(); }
        catch (InvalidOperationException) { refused = true; }
        check.That(refused && session.CanUndo && notifications == 3 && session.ToBytes().SequenceEqual(conflicting) &&
                   session.Body.Things[units[0]].Init.Position == a,
                   "undo refuses an externally changed selected unit before restoring any of the others");
        session.Body.Things[units[1]].Init.Position = b;

        session.Body.Things[other].Init = session.Body.Things[units[0]].Init;
        refused = false;
        try { session.Undo(); }
        catch (InvalidOperationException) { refused = true; }
        check.That(refused && session.CanUndo && session.Body.Things[units[0]].Init.Position == a,
                   "undo refuses a selected unit that now shares data with an unselected row");
        session.Body.Things[other].Init = originalOther;
        check.That(session.Undo() && session.ToBytes().SequenceEqual(baseline), "after the conflicts are resolved, the row can still be undone");

        session.Body.Things[units[1]].Init.Position = original[units[1]] with { X = original[units[1]].X + 1 };
        conflicting = session.ToBytes();
        refused = false;
        try { session.Redo(); }
        catch (InvalidOperationException) { refused = true; }
        check.That(refused && session.CanRedo && session.ToBytes().SequenceEqual(conflicting) &&
                   session.Body.Things[units[0]].Init.Position == original[units[0]],
                   "redo refuses a conflicting edit before moving any selected unit");
        session.Body.Things[units[1]].Init.Position = original[units[1]];
        check.That(session.Redo() && session.ToBytes().SequenceEqual(arranged), "redo remains available after resolving the conflict");

        WorldBody authored = WorldBody.Read(LevelTests.Body("authored-v50"));
        float negativeZero = BitConverter.Int32BitsToSingle(int.MinValue);
        authored.Things[units[0]].Init.Position = authored.Things[units[0]].Init.Position with { Z = negativeZero };
        ArrangeUnitRow signedHeight = new(units, first, step);
        signedHeight.Do(authored);
        bool preserved = SameBits(authored.Things[units[0]].Init.Position.Z, negativeZero);
        signedHeight.Undo(authored);
        check.That(preserved && SameBits(authored.Things[units[0]].Init.Position.Z, negativeZero),
                   "a stored signed-zero height survives placement and undo exactly");
    }

    private static bool SameBits(float a, float b) => BitConverter.SingleToUInt32Bits(a) == BitConverter.SingleToUInt32Bits(b);
}
