// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;

namespace OnslaughtToolkit.Companion.Levels;

/// <summary>A change to a world body that can be made and taken back. One instance is one change: it is made, taken back and made again in turn.</summary>
public interface IEditCommand
{
    /// <summary>What the change does, in words, once it has been made (for an undo list).</summary>
    string Description { get; }

    /// <summary>Makes the change. Throws <see cref="InvalidOperationException"/>, changing nothing, when it cannot be made (or has been made already).</summary>
    void Do(WorldBody body);

    /// <summary>Takes the change back; only called after <see cref="Do"/> succeeded and has not been undone since.</summary>
    void Undo(WorldBody body);
}

/// <summary>
/// Moves one stored thing record to a new position. Nothing else about the record changes, so the row counts and order, and
/// with them every waypoint path and every career's index into a base world, stay as they are. One instance is one move: it
/// remembers the position it replaced, so it cannot be made twice without being taken back between (a second move to the same
/// place is a second <see cref="MoveObject"/>).
/// </summary>
public sealed class MoveObject(int thingIndex, Vector3 position) : IEditCommand
{
    private Vector3 _previous;
    private bool _made;
    private string _description = $"Move row {thingIndex}";

    public int ThingIndex => thingIndex;
    public Vector3 Position => position;
    public string Description => _description;

    public void Do(WorldBody body)
    {
        if (_made) throw new InvalidOperationException("This move has already been made. Take it back first, or make a new move.");
        if (thingIndex < 0 || thingIndex >= body.Things.Count)
            throw new InvalidOperationException($"There is no row {thingIndex}: this world has {body.Things.Count}.");
        if (!IsFinite(position)) throw new InvalidOperationException("A position must be three finite numbers.");
        PlacedObject thing = body.Things[thingIndex];
        if (!IsFinite(thing.Init.Position)) throw new InvalidOperationException($"Row {thingIndex} stores a position that is not three finite numbers, so it cannot be moved.");
        _previous = thing.Init.Position;
        thing.Init.Position = position;
        _made = true;
        _description = $"Move {thing.Label} (row {thingIndex})";
    }

    public void Undo(WorldBody body)
    {
        if (!_made) throw new InvalidOperationException("This move has not been made, so there is nothing to take back.");
        body.Things[thingIndex].Init.Position = _previous;
        _made = false;
    }

    internal static bool IsFinite(Vector3 value) => float.IsFinite(value.X) && float.IsFinite(value.Y) && float.IsFinite(value.Z);
}

/// <summary>One thing record whose stored position differs from the baseline's.</summary>
public sealed record ObjectChange(int Index, string Kind, string Name, Vector3 From, Vector3 To)
{
    /// <summary>How far it moved, in world units (X and Y and Z together).</summary>
    public float Distance => Vector3.Distance(From, To);
}

/// <summary>A reason an edit should not be saved (an error) or should be saved with care (a warning).</summary>
public sealed record Finding(string Code, string Message, int? Index = null);

/// <summary>What <see cref="EditSession.Validate"/> found. An edit with errors is not saved; warnings are shown.</summary>
public sealed record ValidationReport(IReadOnlyList<Finding> Errors, IReadOnlyList<Finding> Warnings)
{
    public bool CanSave => Errors.Count == 0;
}

/// <summary>
/// An edit of one world body: the baseline as it was loaded, the working body, the commands made on it (to undo and redo)
/// and what differs from the baseline. The baseline must read and write back to the same bytes, so that what is saved
/// differs from it only where an edit changed it. Nothing here touches a file.
/// </summary>
public sealed class EditSession
{
    /// <summary>The terrain lookup answers for X and Y from 0 up to this; outside that square it gives no height.</summary>
    public const float TerrainSquare = 512f;

    private readonly Stack<IEditCommand> _undo = new(), _redo = new();
    private readonly WorldBody _baseline;

    /// <param name="baseline">The body as the game has it (an archive's body, or a mod's world file).</param>
    /// <param name="isBaseWorld">True for a level's base world: careers remember which of its buildings still stand.</param>
    /// <exception cref="InvalidDataException">The bytes are not a world body, or do not write back to the same bytes.</exception>
    public EditSession(byte[] baseline, bool isBaseWorld = false)
    {
        Baseline = baseline.ToArray();
        _baseline = WorldBody.Read(Baseline);
        if (!_baseline.Write().AsSpan().SequenceEqual(Baseline)) throw new InvalidDataException("This world body does not write back to the same bytes, so it cannot be edited safely.");
        Body = WorldBody.Read(Baseline);
        IsBaseWorld = isBaseWorld;
    }

    /// <summary>The bytes the session started from.</summary>
    public byte[] Baseline { get; }

    /// <summary>The working body. Edit it through <see cref="Apply"/> so that the change can be undone.</summary>
    public WorldBody Body { get; }

    public bool IsBaseWorld { get; }
    public bool CanUndo => _undo.Count > 0;
    public bool CanRedo => _redo.Count > 0;
    public string? UndoDescription => _undo.Count > 0 ? _undo.Peek().Description : null;
    public string? RedoDescription => _redo.Count > 0 ? _redo.Peek().Description : null;

    /// <summary>Raised after every change to the working body (an edit, an undo, a redo).</summary>
    public event Action? Changed;

    /// <summary>Makes a change and clears what could be redone.</summary>
    /// <exception cref="InvalidOperationException">The change cannot be made; the body is as it was.</exception>
    public void Apply(IEditCommand command)
    {
        command.Do(Body);
        _undo.Push(command);
        _redo.Clear();
        Changed?.Invoke();
    }

    /// <summary>Takes back the last change. If the command cannot be taken back it stays where it was, and the exception comes out.</summary>
    public bool Undo()
    {
        if (_undo.Count == 0) return false;
        IEditCommand command = _undo.Peek();
        command.Undo(Body);
        _undo.Pop();
        _redo.Push(command);
        Changed?.Invoke();
        return true;
    }

    /// <summary>Makes the last change again. If the command cannot be made it stays where it was, and the exception comes out.</summary>
    public bool Redo()
    {
        if (_redo.Count == 0) return false;
        IEditCommand command = _redo.Peek();
        command.Do(Body);
        _redo.Pop();
        _undo.Push(command);
        Changed?.Invoke();
        return true;
    }

    /// <summary>Back to the baseline: every change is undone (and can be redone, one by one).</summary>
    public void UndoAll()
    {
        while (Undo())
        {
        }
    }

    /// <summary>The bytes of the working body.</summary>
    /// <exception cref="InvalidDataException">The body holds something the format cannot store.</exception>
    public byte[] ToBytes() => Body.Write();

    /// <summary>The records whose stored position differs from the baseline's, in row order (compared bit for bit).</summary>
    public IReadOnlyList<ObjectChange> Changes()
    {
        List<ObjectChange> changes = [];
        for (int i = 0; i < Math.Min(_baseline.Things.Count, Body.Things.Count); i++)
        {
            Vector3 from = _baseline.Things[i].Init.Position, to = Body.Things[i].Init.Position;
            if (!SameBits(from, to)) changes.Add(new ObjectChange(i, _baseline.Things[i].Kind, _baseline.Things[i].Label, from, to));
        }
        return changes;
    }

    /// <summary>
    /// Errors that stop a save: nothing changed, the body cannot be written, the row list changed, or something other than a
    /// position differs from the baseline. Warnings: a position outside the square the terrain lookup covers, and any change
    /// to a base world.
    /// </summary>
    public ValidationReport Validate()
    {
        List<Finding> errors = [], warnings = [];
        byte[] bytes;
        try
        {
            bytes = Body.Write();
        }
        catch (InvalidDataException error)
        {
            errors.Add(new Finding("cannot-write", $"This world cannot be saved: {error.Message}"));
            return new ValidationReport(errors, warnings);
        }
        if (bytes.AsSpan().SequenceEqual(Baseline))
        {
            errors.Add(new Finding("no-change", "Nothing has changed, so there is nothing to save."));
            return new ValidationReport(errors, warnings);
        }
        if (!Body.Things.Select(t => t.ObjectId).SequenceEqual(_baseline.Things.Select(t => t.ObjectId)))
            errors.Add(new Finding("rows-changed", "The number or order of the world's rows changed; this editor only moves things."));
        else
        {
            // Everything but the positions must be what the baseline has: put the baseline's positions back and compare.
            WorldBody check = WorldBody.Read(bytes);
            for (int i = 0; i < check.Things.Count; i++) check.Things[i].Init.Position = _baseline.Things[i].Init.Position;
            if (!check.Write().AsSpan().SequenceEqual(Baseline))
                errors.Add(new Finding("other-change", "Something other than a position differs from the world as it was loaded."));
        }
        foreach (ObjectChange change in Changes())
        {
            if (!MoveObject.IsFinite(change.To))
                errors.Add(new Finding("not-finite", $"{change.Name} (row {change.Index}) has a position that is not three finite numbers.", change.Index));
            else if (change.To.X < 0 || change.To.X >= TerrainSquare || change.To.Y < 0 || change.To.Y >= TerrainSquare)
                warnings.Add(new Finding("outside-terrain",
                    $"{change.Name} (row {change.Index}) is outside the 0 to {TerrainSquare:0} square the terrain covers; the game finds no ground height there.", change.Index));
        }
        if (IsBaseWorld && Changes().Count > 0)
            warnings.Add(new Finding("base-world", "This is a level's base world. Careers remember which of its buildings still stand, so a career may not agree with a base world whose things were moved."));
        return new ValidationReport(errors, warnings);
    }

    private static bool SameBits(Vector3 a, Vector3 b) =>
        BitConverter.SingleToUInt32Bits(a.X) == BitConverter.SingleToUInt32Bits(b.X) &&
        BitConverter.SingleToUInt32Bits(a.Y) == BitConverter.SingleToUInt32Bits(b.Y) &&
        BitConverter.SingleToUInt32Bits(a.Z) == BitConverter.SingleToUInt32Bits(b.Z);

}
