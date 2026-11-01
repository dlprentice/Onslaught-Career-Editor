// SPDX-License-Identifier: GPL-3.0-only
using System.IO.Compression;
using System.Numerics;
using System.Runtime.InteropServices;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Authored preview-mesh checks only; these do not establish the game's terrain or unit contact.</summary>
internal static class TerrainAnchorProjectionTests
{
    private static byte[] Unpack(string packed)
    {
        using MemoryStream input = new(Convert.FromBase64String(string.Concat(packed.Where(c => !char.IsWhiteSpace(c)))));
        using ZLibStream inflater = new(input, CompressionMode.Decompress);
        using MemoryStream output = new();
        inflater.CopyTo(output);
        return output.ToArray();
    }

    private static bool Close(float a, float b) => MathF.Abs(a - b) <= 0.001f * MathF.Max(1f, MathF.Abs(b));

    internal static void Run(Checks check)
    {
        check.Suite("terrain preview origin alignment");
        Heightfield field = Heightfield.Read(Unpack(LevelVectors.Terrain.Eres));
        TerrainSurface baseline = TerrainSurface.Build(field, 4);
        byte[] authored = Unpack(LevelVectors.Valid.Single(vector => vector.Name == "authored-v50").Body);
        EditSession session = new(authored);
        TerrainDraft draft = new(session.Body, baseline);
        Vector3 centre = baseline.Vertices.Span[baseline.Vertices.Length / 2];
        if (!draft.TryPrepare(centre.X, -centre.Z, true, out IEditCommand? command, out _) || command is null ||
            !session.TryApply(command, out _)) { check.Fail("the authored preview edit must apply"); return; }
        TerrainSurface surface = draft.Surface;
        Vector3[] vertices = surface.Vertices.ToArray();
        int[] indices = surface.Indices.ToArray();
        int chosen = -1;
        for (int i = 0; i < indices.Length; i += 3)
        {
            Vector3 a = vertices[indices[i]], b = vertices[indices[i + 1]], c = vertices[indices[i + 2]];
            float cross = (b.X - a.X) * (c.Z - a.Z) - (b.Z - a.Z) * (c.X - a.X);
            if (MathF.Abs(cross) > 0.001f && (a.Y != b.Y || b.Y != c.Y)) { chosen = i; break; }
        }
        if (chosen < 0 || !TerrainAnchorProjection.TryCapture(surface, out TerrainAnchorProjection? projection) || projection is null)
        { check.Fail("the authored sloping preview must be capturable"); return; }
        byte[] before = session.ToBytes();
        Vector3 first = vertices[indices[chosen]], second = vertices[indices[chosen + 1]], third = vertices[indices[chosen + 2]];
        Vector3 centroid = (first + second + third) / 3f;
        Vector3 original = new(centroid.X, -centroid.Z, 73f);
        check.That(projection.IsCurrent(surface) && projection.TryProject(surface, original, out Vector3 aligned) &&
                   aligned.X == original.X && aligned.Y == original.Y && Close(aligned.Z, -centroid.Y),
                   "a sloping preview triangle interpolates the origin without changing horizontal placement");
        Vector3 edge = (first + second) / 2f;
        check.That(projection.TryProject(surface, new Vector3(edge.X, -edge.Z, 17f), out Vector3 edgeAligned) &&
                   Close(edgeAligned.Z, -edge.Y), "a preview triangle edge has the interpolated height");
        check.That(projection.TryProject(surface, new Vector3(first.X, -first.Z, 17f), out Vector3 vertexAligned) &&
                   Close(vertexAligned.Z, -first.Y), "a preview vertex can be projected");
        float outside = vertices.Max(v => v.X) + 100f;
        check.That(!projection.TryProject(surface, new Vector3(outside, original.Y, original.Z), out _) &&
                   !projection.TryProject(surface, new Vector3(float.NaN, original.Y, original.Z), out _) &&
                   !projection.TryProject(surface, new Vector3(original.X, float.PositiveInfinity, original.Z), out _) &&
                   !projection.TryProject(surface, new Vector3(original.X, original.Y, float.NaN), out _) &&
                   !projection.TryProject(surface, new Vector3(float.MaxValue, original.Y, original.Z), out _),
                   "outside and nonfinite positions are refused");
        TerrainSurface separate = TerrainSurface.Build(field, 4);
        check.That(!projection.IsCurrent(separate) && !projection.TryProject(separate, original, out _),
                   "a replaced preview is refused even when it belongs to the same terrain input");
        bool exposed = MemoryMarshal.TryGetArray(surface.Vertices, out ArraySegment<Vector3> segment) && segment.Array is not null;
        if (!exposed) { check.Fail("the authored mutation control must expose its private fixture array"); return; }
        Vector3[] array = segment.Array!;
        int changed = segment.Offset + indices[chosen];
        Vector3 saved = array[changed];
        array[changed] = new Vector3(saved.X, saved.Y + 1f, saved.Z);
        bool refusedChanged = !projection.IsCurrent(surface) && !projection.TryProject(surface, original, out _);
        array[changed] = new Vector3(saved.X, float.NaN, saved.Z);
        bool refusedInvalid = !TerrainAnchorProjection.TryCapture(surface, out _);
        array[changed] = new Vector3(saved.X, float.PositiveInfinity, saved.Z);
        bool refusedInfinity = !TerrainAnchorProjection.TryCapture(surface, out _);
        array[changed] = saved;
        check.That(refusedChanged && refusedInvalid && refusedInfinity && projection.IsCurrent(surface),
                   "in-place preview changes invalidate the capture and nonfinite surfaces are refused");
        bool exposedIndices = MemoryMarshal.TryGetArray(surface.Indices, out ArraySegment<int> segmentIndices) && segmentIndices.Array is not null;
        if (!exposedIndices) { check.Fail("the authored topology control must expose its private fixture array"); return; }
        int[] indexArray = segmentIndices.Array!;
        int indexSlot = segmentIndices.Offset + chosen;
        int savedIndex = indexArray[indexSlot];
        indexArray[indexSlot] = indices[chosen + 1];
        bool refusedTopology = !projection.IsCurrent(surface) && !projection.TryProject(surface, original, out _);
        indexArray[indexSlot] = vertices.Length;
        bool refusedOutOfRangeIndex = !TerrainAnchorProjection.TryCapture(surface, out _);
        indexArray[indexSlot] = savedIndex;
        check.That(refusedTopology && refusedOutOfRangeIndex && projection.IsCurrent(surface),
                   "changed or invalid triangle indices are refused and a restored preview matches again");
        check.That(session.ToBytes().AsSpan().SequenceEqual(before), "projection never changes the authored world bytes");
        if (!draft.TryPrepare(centre.X, -centre.Z, true, out IEditCommand? next, out _) || next is null || !session.TryApply(next, out _))
        { check.Fail("the second authored preview edit must apply"); return; }
        check.That(!projection.IsCurrent(draft.Surface) && !projection.TryProject(draft.Surface, original, out _),
                   "a changed preview rejects a projection captured before that edit");
        check.That(session.Undo() && session.ToBytes().AsSpan().SequenceEqual(before),
                   "the projection calculations left the authored object bytes untouched");
    }
}
