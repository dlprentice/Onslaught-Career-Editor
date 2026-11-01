// SPDX-License-Identifier: GPL-3.0-only
namespace OnslaughtToolkit.Companion.Levels;

/// <summary>A bounded, in-memory edit of the sampled 3D preview, separate from the level's original heightfield.</summary>
internal sealed class TerrainDraft
{
    internal const float Step = 2f, MaxOffset = 64f;
    private readonly TerrainSurface _baseline;
    private readonly WorldBody _owner;
    private readonly HashSet<int> _changed = [];

    internal TerrainDraft(WorldBody owner, TerrainSurface baseline)
    {
        _owner = owner;
        _baseline = baseline;
        Surface = baseline;
    }

    internal TerrainSurface Surface { get; private set; }
    internal int ChangedCount => _changed.Count;
    internal bool HasChanges => ChangedCount > 0;
    internal static bool IsTerrainCommand(IEditCommand? command) => command is VertexChange;

    /// <summary>Prepares one vertex adjustment without mutating the draft or its owner.</summary>
    internal bool TryPrepare(float x, float y, bool raise, out IEditCommand? command, out string message)
    {
        command = null;
        if (!float.IsFinite(x) || !float.IsFinite(y) || x < 0 || y < 0 || x > Heightfield.Size || y > Heightfield.Size)
        {
            message = "Choose a point inside the preview terrain.";
            return false;
        }
        int divisions = Surface.Divisions;
        int column = (int)Math.Round((double)x * divisions / Heightfield.Size, MidpointRounding.AwayFromZero);
        int row = (int)Math.Round((double)y * divisions / Heightfield.Size, MidpointRounding.AwayFromZero);
        int index = row * (divisions + 1) + column;
        float before = Surface.Vertices.Span[index].Y;
        float original = _baseline.Vertices.Span[index].Y;
        float after = before + (raise ? Step : -Step);
        if (!float.IsFinite(after) || Math.Abs((double)after - original) > MaxOffset)
        {
            message = "This point is at the preview's height limit.";
            return false;
        }
        // Returning to a zero baseline restores its exact sign as well.
        if (after == original) after = original;
        if (Bits(after) == Bits(before))
        {
            message = "This point cannot be changed by the preview's step.";
            return false;
        }
        command = new VertexChange(this, _owner, index, before, after);
        message = raise ? "Raised one point in the 3D terrain preview." : "Lowered one point in the 3D terrain preview.";
        return true;
    }

    private static int Bits(float value) => BitConverter.SingleToInt32Bits(value);

    private void Replace(int index, float expected, float next)
    {
        if (Bits(Surface.Vertices.Span[index].Y) != Bits(expected))
            throw new InvalidOperationException("The terrain preview changed since this edit was prepared.");
        TerrainSurface replacement = Surface.WithVertexHeight(index, next);
        if (Bits(_baseline.Vertices.Span[index].Y) == Bits(next)) _changed.Remove(index);
        else _changed.Add(index);
        Surface = replacement;
    }

    private sealed class VertexChange(TerrainDraft draft, WorldBody owner, int index, float before, float after) : IEditCommand
    {
        private bool _made;
        public string Description => "Change a 3D terrain preview point";

        public void Do(WorldBody body)
        {
            if (!ReferenceEquals(body, owner) || _made) throw new InvalidOperationException("This terrain edit does not belong to the current world.");
            draft.Replace(index, before, after);
            _made = true;
        }

        public void Undo(WorldBody body)
        {
            if (!ReferenceEquals(body, owner) || !_made) throw new InvalidOperationException("This terrain edit cannot be undone here.");
            draft.Replace(index, after, before);
            _made = false;
        }
    }
}
