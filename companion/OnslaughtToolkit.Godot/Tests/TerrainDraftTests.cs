// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Authored in-memory terrain-preview edits and their shared undo boundaries.</summary>
internal static class TerrainDraftTests
{
    internal static void Run(Checks check)
    {
        check.Suite("terrain preview draft");
        EditSession session = new(LevelTests.Body("authored-v50"));
        byte[] originalWorld = session.ToBytes();
        TerrainSurface baseline = TerrainSurface.Build((_, _) => 0f, 4);
        Vector3[] originalVertices = baseline.Vertices.ToArray();
        TerrainDraft draft = new(session.Body, baseline);

        foreach ((float x, float y) in new[] { (float.NaN, 0f), (float.PositiveInfinity, 0f), (-1f, 0f), (0f, -1f), (Heightfield.Size + 1, 0f), (0f, Heightfield.Size + 1) })
            check.That(!draft.TryPrepare(x, y, true, out _, out _) && !session.CanUndo && !draft.HasChanges,
                       "invalid coordinates do not modify the draft or undo history");

        IEditCommand? first = null, stale = null;
        check.That(draft.TryPrepare(256, 256, true, out first, out _) && first is not null &&
                   draft.TryPrepare(256, 256, true, out stale, out _) && stale is not null,
                   "a finite interior point prepares a raise");
        if (first is null || stale is null) return;
        EditSession other = new(LevelTests.Body("authored-v50"));
        check.That(!other.TryApply(first, out _) && !draft.HasChanges && !other.CanUndo, "a command refuses another world without changing either session");
        check.That(session.TryApply(first, out _) && draft.ChangedCount == 1 && session.CanUndo,
                   "one raise changes one preview point and enters the shared history");
        Vector3[] raised = draft.Surface.Vertices.ToArray();
        check.That(raised[12].Y == TerrainDraft.Step && raised.Where((_, index) => index != 12).SequenceEqual(originalVertices.Where((_, index) => index != 12)) &&
                   baseline.Vertices.ToArray().SequenceEqual(originalVertices) && session.ToBytes().SequenceEqual(originalWorld),
                   "only the chosen preview vertex changes; baseline vertices and world bytes stay exact");
        check.That(!session.TryApply(stale, out _) && draft.Surface.Vertices.ToArray().SequenceEqual(raised) && draft.ChangedCount == 1,
                   "a stale command is refused without changing the current preview");

        check.That(session.TryApply(new MoveObject(0, new Vector3(90, 91, 92)), out _), "an object move can follow a terrain edit");
        byte[] movedWorld = session.ToBytes();
        check.That(session.Undo() && session.ToBytes().SequenceEqual(originalWorld) && draft.HasChanges,
                   "the first undo takes back the later object move");
        check.That(session.Undo() && !draft.HasChanges && draft.Surface.Vertices.ToArray().SequenceEqual(originalVertices),
                   "the second undo restores the preview terrain exactly");
        check.That(BitConverter.SingleToInt32Bits(draft.Surface.Vertices.Span[12].Y) == BitConverter.SingleToInt32Bits(originalVertices[12].Y),
                   "undo retains the original point's exact zero sign");
        check.That(session.Redo() && draft.Surface.Vertices.ToArray().SequenceEqual(raised) && session.Redo() && session.ToBytes().SequenceEqual(movedWorld),
                   "redo restores terrain and object in the same order");

        EditSession limits = new(LevelTests.Body("authored-v50"));
        TerrainDraft bounded = new(limits.Body, baseline);
        bool allRaised = true;
        for (int i = 0; i < (int)(TerrainDraft.MaxOffset / TerrainDraft.Step); i++)
            allRaised &= bounded.TryPrepare(0, 0, true, out IEditCommand? command, out _) && command is not null && limits.TryApply(command, out _);
        check.That(allRaised && bounded.HasChanges && bounded.Surface.Vertices.Span[0].Y == TerrainDraft.MaxOffset,
                   "an edge point can be raised to the bounded offset");
        check.That(!bounded.TryPrepare(0, 0, true, out _, out _) && bounded.Surface.Vertices.Span[0].Y == TerrainDraft.MaxOffset,
                   "a raise past the bound is refused without a change");
        bool allLowered = true;
        for (int i = 0; i < (int)(TerrainDraft.MaxOffset / TerrainDraft.Step); i++)
            allLowered &= bounded.TryPrepare(0, 0, false, out IEditCommand? command, out _) && command is not null && limits.TryApply(command, out _);
        check.That(allLowered && !bounded.HasChanges && bounded.Surface.Vertices.ToArray().SequenceEqual(originalVertices),
                   "lowering back to baseline clears the terrain's dirty state");
        check.That(bounded.TryPrepare(Heightfield.Size, Heightfield.Size, false, out IEditCommand? corner, out _) && corner is not null &&
                   limits.TryApply(corner, out _) && bounded.Surface.Vertices.Span[^1].Y == -TerrainDraft.Step && bounded.ChangedCount == 1,
                   "the opposite boundary lowers the correct corner");
        bool allBelow = true;
        for (int i = 1; i < (int)(TerrainDraft.MaxOffset / TerrainDraft.Step); i++)
            allBelow &= bounded.TryPrepare(Heightfield.Size, Heightfield.Size, false, out IEditCommand? command, out _) && command is not null && limits.TryApply(command, out _);
        check.That(allBelow && bounded.Surface.Vertices.Span[^1].Y == -TerrainDraft.MaxOffset &&
                   !bounded.TryPrepare(Heightfield.Size, Heightfield.Size, false, out _, out _),
                   "the lower offset limit is enforced without another change");
        TerrainSurface huge = TerrainSurface.Build((_, _) => float.MaxValue / 2, 1);
        TerrainDraft unrepresentable = new(session.Body, huge);
        check.That(!unrepresentable.TryPrepare(0, 0, true, out _, out _) && !unrepresentable.HasChanges,
                   "a step too small to change a stored float is refused");

        foreach (float fractional in new[] { 0.1f, -0.1f, 0.3f, -0.3f })
        {
            EditSession fractionalSession = new(LevelTests.Body("authored-v50"));
            TerrainSurface fractionalBaseline = TerrainSurface.Build((_, _) => fractional, 4);
            TerrainDraft fractionalDraft = new(fractionalSession.Body, fractionalBaseline);
            int baselineBits = BitConverter.SingleToInt32Bits(fractionalBaseline.Vertices.Span[12].Y);
            IEditCommand? raise = null, lower = null;
            bool raisedOk = fractionalDraft.TryPrepare(256, 256, true, out raise, out _) && raise is not null && fractionalSession.TryApply(raise, out _);
            int raisedBits = BitConverter.SingleToInt32Bits(fractionalDraft.Surface.Vertices.Span[12].Y);
            bool loweredOk = fractionalDraft.TryPrepare(256, 256, false, out lower, out _) && lower is not null && fractionalSession.TryApply(lower, out _);
            check.That(raisedOk && loweredOk && !fractionalDraft.HasChanges && fractionalDraft.ChangedCount == 0 &&
                       BitConverter.SingleToInt32Bits(fractionalDraft.Surface.Vertices.Span[12].Y) == baselineBits,
                       "raising then lowering a fractional point restores its exact baseline bits and clears dirty state");
            check.That(fractionalSession.Undo() && fractionalDraft.HasChanges && BitConverter.SingleToInt32Bits(fractionalDraft.Surface.Vertices.Span[12].Y) == raisedBits &&
                       fractionalSession.Redo() && !fractionalDraft.HasChanges && BitConverter.SingleToInt32Bits(fractionalDraft.Surface.Vertices.Span[12].Y) == baselineBits,
                       "undo and redo preserve the fractional raise and exact clean baseline");
            bool loweredFirst = fractionalDraft.TryPrepare(256, 256, false, out IEditCommand? lowerFirst, out _) && lowerFirst is not null && fractionalSession.TryApply(lowerFirst, out _);
            bool raisedBack = fractionalDraft.TryPrepare(256, 256, true, out IEditCommand? raiseBack, out _) && raiseBack is not null && fractionalSession.TryApply(raiseBack, out _);
            check.That(loweredFirst && raisedBack && !fractionalDraft.HasChanges &&
                       BitConverter.SingleToInt32Bits(fractionalDraft.Surface.Vertices.Span[12].Y) == baselineBits,
                       "lowering then raising a fractional point also restores exact baseline bits");
        }
    }
}
