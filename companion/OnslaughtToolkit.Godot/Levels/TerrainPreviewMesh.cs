using System;
using System.Numerics;

namespace OnslaughtToolkit.Companion.Levels;

// Converts an already decoded terrain surface to a checked, independently owned preview mesh.
internal sealed class TerrainPreviewMesh
{
    internal Vector3[] Vertices { get; }
    internal Vector3[] Normals { get; }
    internal int[] Indices { get; }
    internal Vector3 Min { get; }
    internal Vector3 Max { get; }

    private TerrainPreviewMesh(Vector3[] vertices, Vector3[] normals, int[] indices, Vector3 min, Vector3 max)
        => (Vertices, Normals, Indices, Min, Max) = (vertices, normals, indices, min, max);

    internal static TerrainPreviewMesh Build(ReadOnlySpan<Vector3> source, ReadOnlySpan<int> sourceIndices)
    {
        if (source.IsEmpty || sourceIndices.IsEmpty || sourceIndices.Length % 3 != 0)
            throw new ArgumentException("Terrain preview requires complete triangles.");
        var vertices = source.ToArray();
        var indices = sourceIndices.ToArray();
        var normals = new Vector3[vertices.Length];
        Vector3 min = vertices[0], max = vertices[0];
        foreach (var vertex in vertices)
        {
            if (!float.IsFinite(vertex.X) || !float.IsFinite(vertex.Y) || !float.IsFinite(vertex.Z))
                throw new ArgumentException("Terrain preview coordinates must be finite.");
            min = Vector3.Min(min, vertex);
            max = Vector3.Max(max, vertex);
        }
        for (int i = 0; i < indices.Length; i += 3)
        {
            int a = indices[i], b = indices[i + 1], c = indices[i + 2];
            if ((uint)a >= vertices.Length || (uint)b >= vertices.Length || (uint)c >= vertices.Length)
                throw new ArgumentException("Invalid terrain mesh index.");
            Vector3 normal = Vector3.Cross(vertices[b] - vertices[a], vertices[c] - vertices[a]);
            if (!float.IsFinite(normal.X) || !float.IsFinite(normal.Y) || !float.IsFinite(normal.Z))
                throw new ArgumentException("Terrain preview normal must be finite.");
            if (normal.Y < 0f) normal = -normal;
            normals[a] += normal;
            normals[b] += normal;
            normals[c] += normal;
        }
        for (int i = 0; i < normals.Length; i++)
        {
            float length = normals[i].LengthSquared();
            if (!float.IsFinite(length)) throw new ArgumentException("Terrain preview normal must be finite.");
            normals[i] = length > 0f ? Vector3.Normalize(normals[i]) : Vector3.UnitY;
        }
        return new TerrainPreviewMesh(vertices, normals, indices, min, max);
    }
}
