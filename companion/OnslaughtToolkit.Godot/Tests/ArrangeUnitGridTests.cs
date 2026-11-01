// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Grid placement on an authored world; it neither loads game data nor stages a mod.</summary>
internal static class ArrangeUnitGridTests
{
    internal static void Run(Checks check)
    {
        check.Suite("arrange units in a grid");
        WorldBody authored = WorldBody.Read(LevelTests.Body("authored-v50"));
        PlacedObject? example = authored.Things.FirstOrDefault(DuplicateObject.CanCopy);
        if (example is null) { check.Fail("the authored world contains a unit"); return; }
        while (authored.Things.Count(DuplicateObject.CanCopy) < 5) authored.Things.Add(example.Clone());
        int[] rows = authored.Things.Select((thing, index) => (thing, index)).Where(pair => DuplicateObject.CanCopy(pair.thing))
            .Select(pair => pair.index).Take(5).Reverse().ToArray();
        int other = authored.Things.FindIndex(thing => !DuplicateObject.CanCopy(thing));
        if (other < 0) { check.Fail("the authored world contains another object"); return; }
        float negativeZero = BitConverter.Int32BitsToSingle(int.MinValue);
        authored.Things[rows[0]].Init.Position = authored.Things[rows[0]].Init.Position with { Z = negativeZero };
        EditSession session = new(authored.Write());
        byte[] baseline = session.ToBytes();
        int notifications = 0;
        session.Changed += () => notifications++;
        Vector2 first = new(40, 60), across = new(12, 3), down = new(-4, 18);
        List<int> callerSelection = [.. rows];
        ArrangeUnitGrid grid = new(callerSelection, 2, first, across, down);
        callerSelection.Clear();
        check.That(grid.WouldChange(session.Body), "the complete placement is validated before it is made");
        session.Apply(grid);

        WorldBody expected = WorldBody.Read(baseline);
        for (int i = 0; i < rows.Length; i++)
        {
            Vector3 before = expected.Things[rows[i]].Init.Position;
            int column = i % 2, line = i / 2;
            expected.Things[rows[i]].Init.Position = new(first.X + across.X * column + down.X * line,
                first.Y + across.Y * column + down.Y * line, before.Z);
        }
        byte[] placed = session.ToBytes();
        check.That(placed.SequenceEqual(expected.Write()) && session.CanUndo && notifications == 1 &&
                   SameBits(session.Body.Things[rows[0]].Init.Position.Z, negativeZero),
                   "two-column placement preserves order, all unselected data and exact height bits as one edit");
        check.That(!new ArrangeUnitGrid(rows, 2, first, across, down).WouldChange(session.Body),
                   "the same placement is detected as unchanged");

        ArrangeUnitGrid[] invalid =
        [
            new([], 1, first, across, down),
            new(rows, 0, first, across, down),
            new(rows, rows.Length + 1, first, across, down),
            new([rows[0], rows[0]], 2, first, across, down),
            new([rows[0], session.Body.Things.Count], 2, first, across, down),
            new([rows[0], other], 2, first, across, down),
            new(rows, 2, new(float.NaN, 0), across, down),
            new(rows, 2, first, new(float.PositiveInfinity, 0), down),
            new(rows, 2, first, across, new(0, float.NaN)),
            new(rows, 2, new(-1, 0), across, down),
            new(rows, 2, first, new(float.MaxValue, 0), down),
            new(rows, 2, first, Vector2.Zero, down),
            new(rows, 2, first, across, across),
            new(rows, 2, first, new(float.Epsilon, 0), down),
        ];
        bool rejected = true;
        foreach (ArrangeUnitGrid bad in invalid)
        {
            bool accepted = session.TryApply(bad, out string? reason);
            rejected &= !accepted && !string.IsNullOrWhiteSpace(reason) && session.ToBytes().SequenceEqual(placed);
        }
        check.That(rejected && notifications == 1 && session.CanUndo,
                   "invalid selections, dimensions, boundaries and duplicate positions refuse without partial edits");

        ObjectInit otherInit = session.Body.Things[other].Init;
        session.Body.Things[other].Init = session.Body.Things[rows[0]].Init;
        bool aliasAccepted = session.TryApply(new ArrangeUnitGrid(rows, 2, first, across, down), out _);
        session.Body.Things[other].Init = otherInit;
        check.That(!aliasAccepted && session.ToBytes().SequenceEqual(placed) && notifications == 1,
                   "a unit sharing its initializer with an unselected row is rejected without a change");

        check.That(session.Undo() && session.ToBytes().SequenceEqual(baseline) && notifications == 2 && session.CanRedo,
                   "one undo restores the exact original world");
        bool refusedAfterUndo = session.TryApply(new ArrangeUnitGrid([rows[0], rows[0]], 2, first, across, down), out _);
        check.That(!refusedAfterUndo && session.CanRedo && session.ToBytes().SequenceEqual(baseline) && notifications == 2,
                   "a refused edit after undo preserves redo");
        check.That(session.Redo() && session.ToBytes().SequenceEqual(placed) && notifications == 3,
                   "one redo restores the complete grid");

        Vector3 expectedLast = session.Body.Things[rows[^1]].Init.Position;
        session.Body.Things[rows[^1]].Init.Position = expectedLast with { X = expectedLast.X + 1 };
        byte[] conflict = session.ToBytes();
        bool undoRefused = false;
        try { session.Undo(); } catch (InvalidOperationException) { undoRefused = true; }
        check.That(undoRefused && session.CanUndo && session.ToBytes().SequenceEqual(conflict) && notifications == 3,
                   "undo detects an outside edit before restoring any selected unit");
        session.Body.Things[rows[^1]].Init.Position = expectedLast;
        check.That(session.Undo() && session.ToBytes().SequenceEqual(baseline), "undo remains available when the conflict is resolved");

        Vector3 oldLast = session.Body.Things[rows[^1]].Init.Position;
        session.Body.Things[rows[^1]].Init.Position = oldLast with { Y = oldLast.Y + 1 };
        conflict = session.ToBytes();
        bool redoRefused = false;
        try { session.Redo(); } catch (InvalidOperationException) { redoRefused = true; }
        check.That(redoRefused && session.CanRedo && session.ToBytes().SequenceEqual(conflict),
                   "redo detects an outside edit before moving any selected unit");
        session.Body.Things[rows[^1]].Init.Position = oldLast;
        check.That(session.Redo() && session.ToBytes().SequenceEqual(placed), "redo remains available when the conflict is resolved");
    }

    private static bool SameBits(float a, float b) => BitConverter.SingleToUInt32Bits(a) == BitConverter.SingleToUInt32Bits(b);
}
