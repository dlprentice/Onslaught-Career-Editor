// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;

namespace OnslaughtToolkit.Companion.Levels;

/// <summary>
/// Arrange selected existing units in a grid as one edit. This moves positions only: it neither makes the units
/// inert nor checks model clearance. It does not create a room or a playable level.
/// </summary>
public sealed class ArrangeUnitGrid : IEditCommand
{
    private readonly int[] _rows;
    private readonly Vector2 _first, _columnStep, _rowStep;
    private readonly int _columns;
    private List<Move>? _moves;
    private bool _made;

    private sealed record Move(int Row, PlacedObject Thing, ObjectInit Init, Vector3 Before, Vector3 After);

    public ArrangeUnitGrid(IReadOnlyList<int> rows, int columns, Vector2 first, Vector2 columnStep, Vector2 rowStep)
    {
        ArgumentNullException.ThrowIfNull(rows);
        _rows = rows.ToArray();
        _columns = columns;
        _first = first;
        _columnStep = columnStep;
        _rowStep = rowStep;
    }

    public string Description => "Arrange units in a grid";

    /// <summary>Validates the whole arrangement and reports whether any stored position would change.</summary>
    public bool WouldChange(WorldBody body) => Plan(body).Any(move => !SameBits(move.Before, move.After));

    public void Do(WorldBody body)
    {
        if (_made) throw new InvalidOperationException("This arrangement is already applied.");
        List<Move> planned = Plan(body);
        if (_moves is not null)
        {
            for (int i = 0; i < planned.Count; i++)
                if (!ReferenceEquals(planned[i].Thing, _moves[i].Thing) || !ReferenceEquals(planned[i].Init, _moves[i].Init) ||
                    !SameBits(planned[i].Before, _moves[i].Before) || !SameBits(planned[i].After, _moves[i].After))
                    throw new InvalidOperationException("A unit changed after the arrangement was undone.");
        }
        else _moves = planned;
        foreach (Move move in planned) move.Init.Position = move.After;
        _made = true;
    }

    public void Undo(WorldBody body)
    {
        if (!_made || _moves is null) throw new InvalidOperationException("This arrangement is not applied.");
        Dictionary<ObjectInit, int> initCounts = CountInitializers(body);
        // Refuse before changing any row if an outside change has made the saved snapshot stale.
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
        ArgumentNullException.ThrowIfNull(body);
        if (_rows.Length == 0 || _rows.Length > body.Things.Count)
            throw new InvalidOperationException("Choose existing units to arrange.");
        if (_columns < 1 || _columns > _rows.Length)
            throw new InvalidOperationException("The number of columns must be between one and the number of selected units.");
        if (!Finite(_first) || !Finite(_columnStep) || !Finite(_rowStep))
            throw new InvalidOperationException("The first position and spacing must be finite numbers.");

        HashSet<int> selected = [];
        HashSet<Vector2> positions = [];
        Dictionary<ObjectInit, int> initCounts = CountInitializers(body);
        List<Move> planned = new(_rows.Length);
        for (int i = 0; i < _rows.Length; i++)
        {
            int row = _rows[i];
            if (row < 0 || row >= body.Things.Count || !selected.Add(row))
                throw new InvalidOperationException("Each selected row must exist and be selected only once.");
            PlacedObject thing = body.Things[row];
            if (thing is null || thing.Init is null || !DuplicateObject.CanCopy(thing))
                throw new InvalidOperationException("Only existing units can be arranged here.");
            if (initCounts[thing.Init] != 1)
                throw new InvalidOperationException("A selected unit shares its stored data with another row.");
            Vector3 before = thing.Init.Position;
            if (!MoveObject.IsFinite(before))
                throw new InvalidOperationException("A selected unit has a position that is not finite.");
            int column = i % _columns, line = i / _columns;
            float x = _first.X + _columnStep.X * column + _rowStep.X * line;
            float y = _first.Y + _columnStep.Y * column + _rowStep.Y * line;
            Vector2 position = new(x, y);
            if (!Finite(position) || x < 0 || y < 0 || x >= EditSession.TerrainSquare || y >= EditSession.TerrainSquare)
                throw new InvalidOperationException("Every arranged position must be inside the terrain.");
            if (!positions.Add(position))
                throw new InvalidOperationException("Choose spacing that gives every unit a different position.");
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

    private static bool Finite(Vector2 value) => float.IsFinite(value.X) && float.IsFinite(value.Y);

    private static bool SameBits(Vector3 a, Vector3 b) =>
        BitConverter.SingleToUInt32Bits(a.X) == BitConverter.SingleToUInt32Bits(b.X) &&
        BitConverter.SingleToUInt32Bits(a.Y) == BitConverter.SingleToUInt32Bits(b.Y) &&
        BitConverter.SingleToUInt32Bits(a.Z) == BitConverter.SingleToUInt32Bits(b.Z);
}
