// SPDX-License-Identifier: GPL-3.0-only
using System.IO.Compression;
using System.Numerics;
using System.Runtime.InteropServices;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>In-memory authored checks for preview-only origin alignment; no CE ground-contact claim.</summary>
internal static class AlignOriginToPreviewTests
{
    private static byte[] Unpack(string packed)
    {
        using MemoryStream input = new(Convert.FromBase64String(string.Concat(packed.Where(c => !char.IsWhiteSpace(c)))));
        using ZLibStream inflater = new(input, CompressionMode.Decompress);
        using MemoryStream output = new(); inflater.CopyTo(output); return output.ToArray();
    }

    private sealed class Fixture
    {
        internal readonly EditSession Session;
        internal readonly TerrainDraft Draft;
        internal TerrainDraft? Active;
        internal readonly Vector3 Target;
        internal Func<TerrainDraft?> Provider => () => Active;

        internal Fixture()
        {
            byte[] world = Unpack(LevelVectors.Valid.Single(v => v.Name == "authored-v50").Body);
            Session = new EditSession(world);
            Heightfield field = Heightfield.Read(Unpack(LevelVectors.Terrain.Eres));
            TerrainSurface surface = TerrainSurface.Build(field, 4);
            Draft = new TerrainDraft(Session.Body, surface);
            Active = Draft;
            int[] indices = surface.Indices.ToArray();
            Vector3[] vertices = surface.Vertices.ToArray();
            Vector3 centre = (vertices[indices[0]] + vertices[indices[1]] + vertices[indices[2]]) / 3f;
            Target = new Vector3(centre.X, -centre.Z, -centre.Y);
            Session.Body.Things[0].Init.Position = new Vector3(Target.X, Target.Y, Target.Z + 17f);
        }

        internal bool Prepare(out AlignOriginToPreview? command) =>
            AlignOriginToPreview.TryPrepare(Session, Draft, Provider, 0, out command);
    }

    private static bool Close(float a, float b) => MathF.Abs(a - b) <= 0.001f * MathF.Max(1f, MathF.Abs(b));
    private static bool ThrowsInvalidOperation(Action action)
    {
        try { action(); return false; }
        catch (InvalidOperationException) { return true; }
    }

    internal static void Run(Checks check)
    {
        check.Suite("undoable preview origin alignment");
        Fixture f = new();
        byte[] before = f.Session.ToBytes();
        Vector3 original = f.Session.Body.Things[0].Init.Position;
        if (!f.Prepare(out AlignOriginToPreview? command) || command is null) { check.Fail("the authored move must prepare"); return; }
        check.That(f.Session.ToBytes().AsSpan().SequenceEqual(before) && !f.Session.CanUndo,
                   "preparation leaves the authored world and history unchanged");
        bool applied = f.Session.TryApply(command, out _);
        Vector3 moved = f.Session.Body.Things[0].Init.Position;
        byte[] after = f.Session.ToBytes();
        check.That(applied && f.Session.CanUndo && !after.AsSpan().SequenceEqual(before) &&
                   moved.X == original.X && moved.Y == original.Y && Close(moved.Z, f.Target.Z),
                   "apply moves only the origin to the sampled preview surface");
        check.That(f.Session.Undo() && f.Session.ToBytes().AsSpan().SequenceEqual(before) && f.Session.CanRedo,
                   "undo restores every authored world byte");
        check.That(f.Session.Redo() && f.Session.ToBytes().AsSpan().SequenceEqual(after) && f.Session.CanUndo,
                   "redo restores the exact applied authored world");

        Fixture stale = new();
        if (!stale.Prepare(out AlignOriginToPreview? staleMove) || staleMove is null) { check.Fail("the stale control must prepare"); return; }
        Vector3 changed = stale.Session.Body.Things[0].Init.Position + new Vector3(1, 0, 0);
        stale.Session.Body.Things[0].Init.Position = changed;
        byte[] changedBytes = stale.Session.ToBytes();
        check.That(!stale.Session.TryApply(staleMove, out _) && stale.Session.ToBytes().AsSpan().SequenceEqual(changedBytes) &&
                   !stale.Session.CanUndo, "a stale object position is refused without changing it or history");

        Fixture changedWorld = new();
        if (!changedWorld.Prepare(out AlignOriginToPreview? changedWorldMove) || changedWorldMove is null) { check.Fail("the world control must prepare"); return; }
        Vector3 extraPosition = changedWorld.Session.Body.Things[0].Init.Position + new Vector3(1, 1, 0);
        bool extraAdded = changedWorld.Session.TryApply(new DuplicateObject(0, extraPosition, "authored extra"), out _);
        byte[] worldAfterOtherEdit = changedWorld.Session.ToBytes();
        check.That(extraAdded && !changedWorld.Session.TryApply(changedWorldMove, out _) && changedWorld.Session.CanUndo &&
                   changedWorld.Session.ToBytes().AsSpan().SequenceEqual(worldAfterOtherEdit),
                   "an intervening change elsewhere in the world is refused without removing its history");

        Fixture reentrant = new();
        int draftReads = 0;
        Vector3 reentrantPosition = reentrant.Session.Body.Things[0].Init.Position + new Vector3(1, 0, 0);
        TerrainDraft? SideEffectingAccessor()
        {
            if (++draftReads == 3) reentrant.Session.Body.Things[0].Init.Position = reentrantPosition;
            return reentrant.Draft;
        }
        if (!AlignOriginToPreview.TryPrepare(reentrant.Session, reentrant.Draft, SideEffectingAccessor, 0,
                out AlignOriginToPreview? reentrantMove) || reentrantMove is null) { check.Fail("the reentrant control must prepare"); return; }
        bool acceptedReentrant = reentrant.Session.TryApply(reentrantMove, out _);
        check.That(!acceptedReentrant && reentrant.Session.Body.Things[0].Init.Position == reentrantPosition && !reentrant.Session.CanUndo,
                   "an accessor that changes the object before apply is refused without overwriting it");

        Fixture reentrantIdentity = new();
        int identityReads = 0;
        TerrainDraft? ReplacingAccessor()
        {
            if (++identityReads == 3)
            {
                WorldBody copy = WorldBody.Read(reentrantIdentity.Session.ToBytes());
                reentrantIdentity.Session.Body.Things[0] = copy.Things[0];
            }
            return reentrantIdentity.Draft;
        }
        byte[] identityBefore = reentrantIdentity.Session.ToBytes();
        if (!AlignOriginToPreview.TryPrepare(reentrantIdentity.Session, reentrantIdentity.Draft, ReplacingAccessor, 0,
                out AlignOriginToPreview? replacedDuringCheck) || replacedDuringCheck is null) { check.Fail("the reentrant identity control must prepare"); return; }
        check.That(!reentrantIdentity.Session.TryApply(replacedDuringCheck, out _) &&
                   reentrantIdentity.Session.ToBytes().AsSpan().SequenceEqual(identityBefore) && !reentrantIdentity.Session.CanUndo,
                   "an accessor that replaces the object with identical bytes is refused by identity");

        Fixture identity = new();
        if (!identity.Prepare(out AlignOriginToPreview? identityMove) || identityMove is null) { check.Fail("the identity control must prepare"); return; }
        byte[] identical = identity.Session.ToBytes();
        WorldBody clone = WorldBody.Read(identical);
        identity.Session.Body.Things[0] = clone.Things[0];
        check.That(identity.Session.ToBytes().AsSpan().SequenceEqual(identical) && !identity.Session.TryApply(identityMove, out _) &&
                   identity.Session.ToBytes().AsSpan().SequenceEqual(identical),
                   "a byte-identical replacement object is refused by identity");

        Fixture replaced = new();
        if (!replaced.Prepare(out AlignOriginToPreview? replacedMove) || replacedMove is null) { check.Fail("the draft control must prepare"); return; }
        byte[] replacedBytes = replaced.Session.ToBytes();
        replaced.Active = new TerrainDraft(replaced.Session.Body, replaced.Draft.Surface);
        check.That(!replaced.Session.TryApply(replacedMove, out _) && replaced.Session.ToBytes().AsSpan().SequenceEqual(replacedBytes) &&
                   !replaced.Session.CanUndo, "replacement of the active draft refuses a stale move");

        Fixture changedPreview = new();
        if (!changedPreview.Prepare(out AlignOriginToPreview? previewMove) || previewMove is null) { check.Fail("the preview control must prepare"); return; }
        Vector3 sample = changedPreview.Draft.Surface.Vertices.Span[changedPreview.Draft.Surface.Vertices.Length / 2];
        if (!changedPreview.Draft.TryPrepare(sample.X, -sample.Z, true, out IEditCommand? terrainEdit, out _) || terrainEdit is null ||
            !changedPreview.Session.TryApply(terrainEdit, out _)) { check.Fail("the authored preview edit must apply"); return; }
        byte[] previewBytes = changedPreview.Session.ToBytes();
        check.That(!changedPreview.Session.TryApply(previewMove, out _) && changedPreview.Session.ToBytes().AsSpan().SequenceEqual(previewBytes),
                   "changing the preview refuses a command prepared against its earlier surface");

        Fixture redo = new();
        if (!redo.Prepare(out AlignOriginToPreview? redoMove) || redoMove is null || !redo.Session.TryApply(redoMove, out _))
        { check.Fail("the redo control must apply"); return; }
        byte[] redoAfter = redo.Session.ToBytes();
        if (!redo.Session.Undo()) { check.Fail("the redo control must undo"); return; }
        byte[] redoBefore = redo.Session.ToBytes();
        redo.Active = null;
        bool refusedRedo = ThrowsInvalidOperation(() => redo.Session.Redo());
        check.That(refusedRedo && redo.Session.CanRedo && redo.Session.ToBytes().AsSpan().SequenceEqual(redoBefore),
                   "redo refuses a stale active preview without losing redo history");
        redo.Active = redo.Draft;
        if (!MemoryMarshal.TryGetArray(redo.Draft.Surface.Vertices, out ArraySegment<Vector3> redoSegment) || redoSegment.Array is null)
        { check.Fail("the redo surface control must be available"); return; }
        Vector3 redoVertex = redoSegment.Array[redoSegment.Offset];
        redoSegment.Array[redoSegment.Offset] = new Vector3(redoVertex.X, redoVertex.Y + 1, redoVertex.Z);
        bool refusedChangedSurface = ThrowsInvalidOperation(() => redo.Session.Redo());
        bool keptRedo = redo.Session.CanRedo && redo.Session.ToBytes().AsSpan().SequenceEqual(redoBefore);
        redoSegment.Array[redoSegment.Offset] = redoVertex;
        check.That(refusedChangedSurface && keptRedo, "redo refuses an in-place preview change without losing history");
        check.That(redo.Session.Redo() && redo.Session.ToBytes().AsSpan().SequenceEqual(redoAfter),
                   "redo succeeds when the original preview is active again");

        Fixture undo = new();
        if (!undo.Prepare(out AlignOriginToPreview? undoMove) || undoMove is null) { check.Fail("the undo control must prepare"); return; }
        byte[] undoBefore = undo.Session.ToBytes();
        if (!undo.Session.TryApply(undoMove, out _)) { check.Fail("the undo control must apply"); return; }
        byte[] undoAfter = undo.Session.ToBytes();
        Vector3 movedPosition = undo.Session.Body.Things[0].Init.Position;
        undo.Session.Body.Things[0].Init.Position = movedPosition + new Vector3(1, 0, 0);
        byte[] externallyChanged = undo.Session.ToBytes();
        bool refusedUndo = ThrowsInvalidOperation(() => undo.Session.Undo());
        check.That(refusedUndo && undo.Session.CanUndo && undo.Session.ToBytes().AsSpan().SequenceEqual(externallyChanged),
                   "undo refuses a stale world without losing its undo history");
        undo.Session.Body.Things[0].Init.Position = movedPosition;
        check.That(undo.Session.ToBytes().AsSpan().SequenceEqual(undoAfter), "the authored stale-world control restores its input");
        if (!MemoryMarshal.TryGetArray(undo.Draft.Surface.Vertices, out ArraySegment<Vector3> segment) || segment.Array is null)
        { check.Fail("the authored preview mutation control must be available"); return; }
        Vector3 saved = segment.Array[segment.Offset];
        segment.Array[segment.Offset] = new Vector3(saved.X, saved.Y + 1, saved.Z);
        bool undone = undo.Session.Undo();
        segment.Array[segment.Offset] = saved;
        check.That(undone && undo.Session.ToBytes().AsSpan().SequenceEqual(undoBefore),
                   "undo restores the object even if the preview has subsequently changed");

        Fixture invalid = new();
        TerrainDraft unrelated = new(new EditSession(invalid.Session.ToBytes()).Body, invalid.Draft.Surface);
        byte[] invalidBefore = invalid.Session.ToBytes();
        bool rejected = !AlignOriginToPreview.TryPrepare(null, invalid.Draft, invalid.Provider, 0, out _) &&
                        !AlignOriginToPreview.TryPrepare(invalid.Session, null, invalid.Provider, 0, out _) &&
                        !AlignOriginToPreview.TryPrepare(invalid.Session, invalid.Draft, null, 0, out _) &&
                        !AlignOriginToPreview.TryPrepare(invalid.Session, invalid.Draft, invalid.Provider, -1, out _) &&
                        !AlignOriginToPreview.TryPrepare(invalid.Session, invalid.Draft, invalid.Provider, invalid.Session.Body.Things.Count, out _) &&
                        !AlignOriginToPreview.TryPrepare(invalid.Session, unrelated, () => unrelated, 0, out _);
        check.That(rejected && invalid.Session.ToBytes().AsSpan().SequenceEqual(invalidBefore) && !invalid.Session.CanUndo,
                   "invalid sessions, rows, providers and foreign previews are refused without edits");
        check.That(!AlignOriginToPreview.TryPrepare(invalid.Session, invalid.Draft,
                       () => throw new InvalidOperationException(), 0, out _) &&
                   invalid.Session.ToBytes().AsSpan().SequenceEqual(invalidBefore),
                   "an unavailable active-draft accessor is refused without changes");
        int accesses = 0;
        TerrainDraft? FailsOnApply() => ++accesses <= 2 ? invalid.Draft : throw new InvalidOperationException();
        if (!AlignOriginToPreview.TryPrepare(invalid.Session, invalid.Draft, FailsOnApply, 0, out AlignOriginToPreview? unavailable) || unavailable is null)
        { check.Fail("the unavailable-accessor control must prepare"); return; }
        check.That(!invalid.Session.TryApply(unavailable, out _) && invalid.Session.ToBytes().AsSpan().SequenceEqual(invalidBefore) &&
                   !invalid.Session.CanUndo, "an accessor that becomes unavailable before apply refuses without changes");
        invalid.Session.Body.Things[0].Init.Position = invalid.Target;
        check.That(!invalid.Prepare(out _) && !invalid.Session.CanUndo, "an already aligned origin does not create a history entry");
        invalid.Session.Body.Things[0].Init.Position = new Vector3(float.NaN, invalid.Target.Y, invalid.Target.Z);
        check.That(!invalid.Prepare(out _) && !invalid.Session.CanUndo, "nonfinite authored positions are refused");
        invalid.Session.Body.Things[0].Init.Position = new Vector3(float.MaxValue, invalid.Target.Y, invalid.Target.Z);
        check.That(!invalid.Prepare(out _) && !invalid.Session.CanUndo, "origins outside the preview are refused");
    }
}
