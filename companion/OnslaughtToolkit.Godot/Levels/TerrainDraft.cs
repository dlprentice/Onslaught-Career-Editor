// SPDX-License-Identifier: GPL-3.0-only
namespace OnslaughtToolkit.Companion.Levels;

/// <summary>A nonzero number of preview steps at one sampled vertex.</summary>
internal readonly record struct TerrainOffset(int Index, int Steps);

/// <summary>A bounded, in-memory edit of the sampled 3D preview, separate from the level's original heightfield.</summary>
internal sealed class TerrainDraft
{
    internal const float Step = 2f, MaxOffset = 64f;
    private readonly TerrainSurface _baseline;
    private readonly WorldBody _owner;
    private readonly Dictionary<int, int> _steps = [];

    internal TerrainDraft(WorldBody owner, TerrainSurface baseline)
    {
        _owner = owner;
        _baseline = baseline;
        Surface = baseline;
    }

    internal TerrainSurface Surface { get; private set; }
    internal TerrainSurface Baseline => _baseline;
    internal int ChangedCount => _steps.Count;
    internal bool HasChanges => ChangedCount > 0;
    internal static bool IsTerrainCommand(IEditCommand? command) => command is VertexChange;
    internal bool BelongsTo(WorldBody owner) => ReferenceEquals(_owner, owner);

    /// <summary>Snapshots the current offsets in deterministic vertex order.</summary>
    internal IReadOnlyList<TerrainOffset> Offsets() => [.. _steps.OrderBy(entry => entry.Key).Select(entry => new TerrainOffset(entry.Key, entry.Value))];

    /// <summary>Restores bounded offsets without manufacturing undo history.</summary>
    internal static TerrainDraft Restore(WorldBody owner, TerrainSurface baseline, IReadOnlyList<TerrainOffset> offsets)
    {
        ArgumentNullException.ThrowIfNull(owner);
        ArgumentNullException.ThrowIfNull(baseline);
        ArgumentNullException.ThrowIfNull(offsets);
        TerrainDraft draft = new(owner, baseline);
        Dictionary<int, float> heights = [];
        int previous = -1, maxSteps = (int)(MaxOffset / Step);
        foreach (TerrainOffset offset in offsets)
        {
            if (offset.Index <= previous || offset.Index >= baseline.Vertices.Length ||
                offset.Steps == 0 || offset.Steps < -maxSteps || offset.Steps > maxSteps)
                throw new InvalidDataException("A saved terrain preview point is invalid or repeated.");
            float original = baseline.Vertices.Span[offset.Index].Y;
            float after = (float)((double)original + (double)offset.Steps * Step);
            if (!float.IsFinite(original) || !float.IsFinite(after) || Math.Abs((double)after - original) > MaxOffset || Bits(after) == Bits(original))
                throw new InvalidDataException("A saved terrain preview height is outside its safe bounds.");
            heights.Add(offset.Index, after);
            draft._steps.Add(offset.Index, offset.Steps);
            previous = offset.Index;
        }
        draft.Surface = baseline.WithVertexHeights(heights);
        return draft;
    }

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
        int beforeSteps = _steps.GetValueOrDefault(index);
        int afterSteps = beforeSteps + (raise ? 1 : -1);
        if (Math.Abs(afterSteps) > (int)(MaxOffset / Step))
        {
            message = "This point is at the preview's height limit.";
            return false;
        }
        // Each height comes from the original and an integer offset: returning to zero copies every original bit exactly.
        float after = afterSteps == 0 ? original : (float)((double)original + (double)afterSteps * Step);
        if (!float.IsFinite(after) || Math.Abs((double)after - original) > MaxOffset)
        {
            message = "This point is at the preview's height limit.";
            return false;
        }
        if (Bits(after) == Bits(before))
        {
            message = "This point cannot be changed by the preview's step.";
            return false;
        }
        command = new VertexChange(this, _owner, index, beforeSteps, afterSteps, before, after);
        message = raise ? "Raised one point in the 3D terrain preview." : "Lowered one point in the 3D terrain preview.";
        return true;
    }

    private static int Bits(float value) => BitConverter.SingleToInt32Bits(value);

    private void Replace(int index, int expectedSteps, int nextSteps, float expected, float next)
    {
        if (_steps.GetValueOrDefault(index) != expectedSteps || Bits(Surface.Vertices.Span[index].Y) != Bits(expected))
            throw new InvalidOperationException("The terrain preview changed since this edit was prepared.");
        TerrainSurface replacement = Surface.WithVertexHeight(index, next);
        if (nextSteps == 0) _steps.Remove(index);
        else _steps[index] = nextSteps;
        Surface = replacement;
    }

    private sealed class VertexChange(TerrainDraft draft, WorldBody owner, int index, int beforeSteps, int afterSteps, float before, float after) : IEditCommand
    {
        private bool _made;
        public string Description => "Change a 3D terrain preview point";

        public void Do(WorldBody body)
        {
            if (!ReferenceEquals(body, owner) || _made) throw new InvalidOperationException("This terrain edit does not belong to the current world.");
            draft.Replace(index, beforeSteps, afterSteps, before, after);
            _made = true;
        }

        public void Undo(WorldBody body)
        {
            if (!ReferenceEquals(body, owner) || !_made) throw new InvalidOperationException("This terrain edit cannot be undone here.");
            draft.Replace(index, afterSteps, beforeSteps, after, before);
            _made = false;
        }
    }
}
