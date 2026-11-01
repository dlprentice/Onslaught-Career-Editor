// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;
using System.Security.Cryptography;

namespace OnslaughtToolkit.Companion.Levels;

/// <summary>One undoable object-origin move to a sampled editor preview. This is not CE ground contact,
/// model-foot clearance, a saved level, or evidence about real level behavior.</summary>
/// <remarks>The caller must supply an accessor to the actually active draft and serialize preparation,
/// application, undo and redo on the editor thread. A refusal from undo or redo can throw and must be reported.
/// This command cannot enforce preview-only mode: a future caller must block save, staging and play while its
/// preview-origin moves are present until those paths have a separately reviewed design.</remarks>
internal sealed class AlignOriginToPreview : IEditCommand
{
    private readonly EditSession _session;
    private readonly TerrainDraft _draft;
    private readonly Func<TerrainDraft?> _currentDraft;
    private readonly TerrainAnchorProjection _projection;
    private readonly int _index;
    private readonly object _thing;
    private readonly byte[] _before;
    private readonly byte[] _after;
    private readonly MoveObject _move;

    private AlignOriginToPreview(EditSession session, TerrainDraft draft, Func<TerrainDraft?> currentDraft,
        TerrainAnchorProjection projection, int index, object thing, byte[] before, byte[] after, Vector3 target)
    {
        _session = session;
        _draft = draft;
        _currentDraft = currentDraft;
        _projection = projection;
        _index = index;
        _thing = thing;
        _before = before;
        _after = after;
        _move = new MoveObject(index, target);
    }

    /// <summary>Prepares a command without changing the session or its preview.</summary>
    internal static bool TryPrepare(EditSession? session, TerrainDraft? draft, Func<TerrainDraft?>? currentDraft,
        int index, out AlignOriginToPreview? command)
    {
        command = null;
        if (session is null || draft is null || currentDraft is null || !draft.BelongsTo(session.Body) ||
            !IsActive(currentDraft, draft) || (uint)index >= (uint)session.Body.Things.Count) return false;
        try
        {
            object thing = session.Body.Things[index];
            Vector3 original = session.Body.Things[index].Init.Position;
            TerrainSurface surface = draft.Surface;
            if (!TerrainAnchorProjection.TryCapture(surface, out TerrainAnchorProjection? projection) || projection is null ||
                !projection.TryProject(surface, original, out Vector3 target) || Same(original, target)) return false;
            byte[] bytes = session.ToBytes();
            EditSession scratch = EditSession.Restore(session.Baseline, bytes, session.IsBaseWorld);
            new MoveObject(index, target).Do(scratch.Body);
            byte[] result = scratch.ToBytes();
            if (!IsActive(currentDraft, draft) || !projection.IsCurrent(draft.Surface) ||
                !ReferenceEquals(thing, session.Body.Things[index]) || !session.ToBytes().AsSpan().SequenceEqual(bytes)) return false;
            command = new AlignOriginToPreview(session, draft, currentDraft, projection, index, thing,
                SHA256.HashData(bytes), SHA256.HashData(result), target);
            return true;
        }
        catch (Exception error) when (EditSession.IsUnstorable(error) || error is InvalidOperationException) { return false; }
    }

    /// <summary>A label for the editor's undo history.</summary>
    public string Description => "Align origin to preview terrain";

    /// <summary>Applies or redoes the move only while the captured world, object and active preview still match.</summary>
    public void Do(WorldBody world)
    {
        if (!Matches(world, _before) || !IsActive(_currentDraft, _draft) || !_draft.BelongsTo(world) ||
            !_projection.IsCurrent(_draft.Surface)) throw new InvalidOperationException("The object or terrain preview changed; prepare the move again.");
        _move.Do(world);
    }

    /// <summary>Restores the original object position even if the preview later changes, provided the world still matches.</summary>
    public void Undo(WorldBody world)
    {
        if (!Matches(world, _after)) throw new InvalidOperationException("The world changed; the move cannot be undone safely.");
        _move.Undo(world);
    }

    private static bool IsActive(Func<TerrainDraft?> currentDraft, TerrainDraft expected)
    {
        try { return ReferenceEquals(currentDraft(), expected); }
        catch (Exception error) when (error is InvalidOperationException or ArgumentException) { return false; }
    }

    private bool Matches(WorldBody world, byte[] expected)
    {
        if (!ReferenceEquals(world, _session.Body) || (uint)_index >= (uint)world.Things.Count ||
            !ReferenceEquals(world.Things[_index], _thing)) return false;
        try { return CryptographicOperations.FixedTimeEquals(SHA256.HashData(_session.ToBytes()), expected); }
        catch (Exception error) when (EditSession.IsUnstorable(error)) { return false; }
    }

    private static bool Same(Vector3 a, Vector3 b) => BitConverter.SingleToUInt32Bits(a.X) == BitConverter.SingleToUInt32Bits(b.X) &&
        BitConverter.SingleToUInt32Bits(a.Y) == BitConverter.SingleToUInt32Bits(b.Y) &&
        BitConverter.SingleToUInt32Bits(a.Z) == BitConverter.SingleToUInt32Bits(b.Z);
}
