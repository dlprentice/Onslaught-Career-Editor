// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;

namespace OnslaughtToolkit.Companion.Levels;

/// <summary>
/// Arranges existing units in selection order as one undoable change. Their heights and all other fields are
/// retained. This only moves world records; it does not make units inert or guarantee clearance on the terrain.
/// </summary>
public sealed class ArrangeUnitRow : IEditCommand
{
    private readonly int[] _rows;
    private readonly Vector2 _first, _step;
    private List<Move>? _moves;
    private bool _made;

    private sealed record Move(int Row, PlacedObject Thing, ObjectInit Init, Vector3 Before, Vector3 After);

    public ArrangeUnitRow(IReadOnlyList<int> rows, Vector2 first, Vector2 step)
    {
        ArgumentNullException.ThrowIfNull(rows);
        _rows = rows.ToArray();
        _first = first;
        _step = step;
    }

    public string Description => "Arrange units in a row";

    /// <summary>Checks the complete selection without changing it, and reports whether anything would move.</summary>
    public bool WouldChange(WorldBody body) => Plan(body).Any(move => !SameBits(move.Before, move.After));

    public void Do(WorldBody body)
    {
        if (_made) throw new InvalidOperationException("This arrangement is already applied.");
        List<Move> planned = Plan(body);
        if (_moves is not null)
        {
            for (int i = 0; i < planned.Count; i++)
                if (!ReferenceEquals(planned[i].Thing, _moves[i].Thing) || !ReferenceEquals(planned[i].Init, _moves[i].Init) ||
                    !SameBits(planned[i].Before, _moves[i].Before) ||
                    !SameBits(planned[i].After, _moves[i].After))
                    throw new InvalidOperationException("A unit changed after the arrangement was undone.");
        }
        else _moves = planned;
        foreach (Move move in planned) move.Init.Position = move.After;
        _made = true;
    }

    public void Undo(WorldBody body)
    {
        if (!_made || _moves is null) throw new InvalidOperationException("This arrangement is not applied.");
        // Check all rows before changing any, so an out-of-band edit cannot make undo partially restore a row.
        Dictionary<ObjectInit, int> initCounts = CountInitializers(body);
        foreach (Move move in _moves)
            if (move.Row >= body.Things.Count || !ReferenceEquals(body.Things[move.Row], move.Thing) ||
                !ReferenceEquals(move.Thing.Init, move.Init) || !initCounts.TryGetValue(move.Init, out int count) || count != 1 ||
                !SameBits(move.Init.Position, move.After))
                throw new InvalidOperationException("A unit changed after the arrangement was made.");
        foreach (Move move in _moves) move.Init.Position = move.Before;
        _made = false;
    }

    private List<Move> Plan(WorldBody body)
    {
        if (_rows.Length == 0) throw new InvalidOperationException("Choose at least one unit to arrange.");
        if (_rows.Length > body.Things.Count) throw new InvalidOperationException("The selection contains more rows than the world.");
        if (!float.IsFinite(_first.X) || !float.IsFinite(_first.Y) || !float.IsFinite(_step.X) || !float.IsFinite(_step.Y))
            throw new InvalidOperationException("The first position and spacing must be finite numbers.");
        HashSet<int> seen = [];
        HashSet<Vector2> positions = [];
        Dictionary<ObjectInit, int> initCounts = CountInitializers(body);
        List<Move> planned = new(_rows.Length);
        for (int i = 0; i < _rows.Length; i++)
        {
            int row = _rows[i];
            if (row < 0 || row >= body.Things.Count || !seen.Add(row))
                throw new InvalidOperationException("Each selected row must exist and be selected only once.");
            PlacedObject thing = body.Things[row];
            if (thing is null || thing.Init is null || !DuplicateObject.CanCopy(thing))
                throw new InvalidOperationException("Only existing units can be arranged here.");
            if (initCounts[thing.Init] != 1) throw new InvalidOperationException("A selected unit shares its stored data with another row.");
            Vector3 before = thing.Init.Position;
            if (!MoveObject.IsFinite(before)) throw new InvalidOperationException("A selected unit has a position that is not finite.");
            float x = _first.X + _step.X * i, y = _first.Y + _step.Y * i;
            if (!float.IsFinite(x) || !float.IsFinite(y) || x < 0 || y < 0 || x >= EditSession.TerrainSquare || y >= EditSession.TerrainSquare)
                throw new InvalidOperationException("Every arranged position must be inside the terrain.");
            if (!positions.Add(new Vector2(x, y))) throw new InvalidOperationException("Choose spacing that gives every unit a different position.");
            planned.Add(new Move(row, thing, thing.Init, before, new Vector3(x, y, before.Z)));
        }
        return planned;
    }

    private static Dictionary<ObjectInit, int> CountInitializers(WorldBody body)
    {
        Dictionary<ObjectInit, int> counts = new(ReferenceEqualityComparer.Instance);
        foreach (PlacedObject? thing in body.Things)
            if (thing?.Init is { } init) counts[init] = counts.GetValueOrDefault(init) + 1;
        return counts;
    }

    private static bool SameBits(Vector3 a, Vector3 b) =>
        BitConverter.SingleToUInt32Bits(a.X) == BitConverter.SingleToUInt32Bits(b.X) &&
        BitConverter.SingleToUInt32Bits(a.Y) == BitConverter.SingleToUInt32Bits(b.Y) &&
        BitConverter.SingleToUInt32Bits(a.Z) == BitConverter.SingleToUInt32Bits(b.Z);
}
