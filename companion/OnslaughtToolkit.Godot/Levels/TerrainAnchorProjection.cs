// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;
using System.Runtime.InteropServices;
using System.Security.Cryptography;

namespace OnslaughtToolkit.Companion.Levels;

/// <summary>Aligns an object origin to the current editor preview mesh. This does not establish contact between
/// a unit's visible geometry and the ground, or establish the game's real terrain height.</summary>
/// <remarks>This calculation does not edit a level. A caller must check the projection and the object's current
/// state again immediately before an undoable edit, on the editor's serialized thread.</remarks>
internal sealed class TerrainAnchorProjection
{
    private readonly TerrainSurface _surface;
    private readonly byte[] _digest;
    private readonly float _rayTop;

    private TerrainAnchorProjection(TerrainSurface surface, byte[] digest, float rayTop)
    {
        _surface = surface;
        _digest = digest;
        _rayTop = rayTop;
    }

    /// <summary>Captures a validated preview mesh; this never opens a file or changes a world.</summary>
    internal static bool TryCapture(TerrainSurface? surface, out TerrainAnchorProjection? projection)
    {
        projection = null;
        if (surface is null) return false;
        ReadOnlySpan<Vector3> vertices = surface.Vertices.Span;
        ReadOnlySpan<int> indices = surface.Indices.Span;
        if (vertices.IsEmpty || indices.IsEmpty || indices.Length % 3 != 0) return false;
        float top = float.NegativeInfinity;
        foreach (Vector3 vertex in vertices)
        {
            if (!Finite(vertex)) return false;
            top = MathF.Max(top, vertex.Y);
        }
        foreach (int index in indices) if ((uint)index >= (uint)vertices.Length) return false;
        float rayTop = top + MathF.Max(1f, MathF.Abs(top) * 0.0001f);
        if (!float.IsFinite(rayTop) || rayTop <= top) return false;
        projection = new TerrainAnchorProjection(surface, Digest(surface), rayTop);
        return true;
    }

    /// <summary>Rejects replacement or in-place mutation of either mesh array since capture.</summary>
    internal bool IsCurrent(TerrainSurface? surface) => ReferenceEquals(surface, _surface) &&
        CryptographicOperations.FixedTimeEquals(_digest, Digest(_surface));

    /// <summary>Returns a position in authored coordinates on the preview triangle beneath its horizontal origin.</summary>
    internal bool TryProject(TerrainSurface? current, Vector3 original, out Vector3 projected)
    {
        projected = default;
        if (!Finite(original) || !IsCurrent(current)) return false;
        Vector3 ray = new(original.X, _rayTop, -original.Y);
        if (!Finite(ray) || !TerrainRayPicker.TryHit(_surface, ray, -Vector3.UnitY, out Vector3 hit) ||
            !Finite(hit) || !IsCurrent(current)) return false;
        projected = new Vector3(original.X, original.Y, -hit.Y);
        return Finite(projected);
    }

    private static bool Finite(Vector3 vector) => float.IsFinite(vector.X) && float.IsFinite(vector.Y) && float.IsFinite(vector.Z);

    private static byte[] Digest(TerrainSurface surface)
    {
        using IncrementalHash hash = IncrementalHash.CreateHash(HashAlgorithmName.SHA256);
        hash.AppendData(MemoryMarshal.AsBytes(surface.Vertices.Span));
        hash.AppendData(MemoryMarshal.AsBytes(surface.Indices.Span));
        return hash.GetHashAndReset();
    }
}
