// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;

namespace OnslaughtToolkit.Companion.Levels;

/// <summary>
/// A bounded, sampled terrain surface for a future 3D level view. The surface is a preview: it does not change the
/// level, replace its height lookup or claim to reproduce the original terrain renderer.
/// </summary>
public sealed class TerrainSurface
{
    public const int DefaultDivisions = 128;
    public const int MaxDivisions = 256;

    // The existing relief preview also samples just inside the world edge, where the height lookup is defined.
    private const float EdgeInset = 0.01f;

    private readonly Vector3[] _vertices;
    private readonly int[] _indices;

    private TerrainSurface(int divisions, Vector3[] vertices, int[] indices)
    {
        Divisions = divisions;
        _vertices = vertices;
        _indices = indices;
    }

    /// <summary>Number of cells along each side of the square surface.</summary>
    public int Divisions { get; }

    /// <summary>
    /// Vertices in Godot coordinates: world X is X, world Y is negative Z, and world height (Z down) is negative Y.
    /// The coordinates retain the full world boundary, while boundary heights are sampled just inside it.
    /// </summary>
    public ReadOnlyMemory<Vector3> Vertices => _vertices;

    /// <summary>Triangle indices in Godot's clockwise front-face order, with the front of a flat surface facing up.</summary>
    public ReadOnlyMemory<int> Indices => _indices;

    /// <summary>Returns a new preview surface with one changed vertical coordinate, keeping its topology.</summary>
    internal TerrainSurface WithVertexHeight(int index, float height)
    {
        if (index < 0 || index >= _vertices.Length) throw new ArgumentOutOfRangeException(nameof(index));
        if (!float.IsFinite(height)) throw new ArgumentOutOfRangeException(nameof(height));
        Vector3[] vertices = _vertices.ToArray();
        vertices[index].Y = height;
        return new TerrainSurface(Divisions, vertices, _indices);
    }

    /// <summary>Returns a preview with a bounded set of height replacements, copying the surface once.</summary>
    internal TerrainSurface WithVertexHeights(IReadOnlyDictionary<int, float> heights)
    {
        ArgumentNullException.ThrowIfNull(heights);
        Vector3[] vertices = _vertices.ToArray();
        foreach ((int index, float height) in heights)
        {
            if (index < 0 || index >= vertices.Length || !float.IsFinite(height))
                throw new InvalidDataException("A saved terrain preview point is invalid.");
            vertices[index].Y = height;
        }
        return new TerrainSurface(Divisions, vertices, _indices);
    }

    /// <summary>Samples an existing read-only terrain. A malformed non-finite height is refused.</summary>
    public static TerrainSurface Build(Heightfield field, int divisions = DefaultDivisions)
    {
        ArgumentNullException.ThrowIfNull(field);
        return Build(field.HeightAt, divisions);
    }

    // An injected height function makes the coordinate and topology checks independent of game data.
    internal static TerrainSurface Build(Func<float, float, float> heightAt, int divisions)
    {
        ArgumentNullException.ThrowIfNull(heightAt);
        if (divisions is < 1 or > MaxDivisions) throw new ArgumentOutOfRangeException(nameof(divisions));

        int stride = divisions + 1;
        Vector3[] vertices = new Vector3[stride * stride];
        for (int row = 0; row <= divisions; row++)
        {
            float worldY = Heightfield.Size * row / divisions;
            float sampleY = Math.Clamp(worldY, EdgeInset, Heightfield.Size - EdgeInset);
            for (int column = 0; column <= divisions; column++)
            {
                float worldX = Heightfield.Size * column / divisions;
                float sampleX = Math.Clamp(worldX, EdgeInset, Heightfield.Size - EdgeInset);
                float height = heightAt(sampleX, sampleY);
                if (!float.IsFinite(height)) throw new InvalidDataException("Terrain contains a non-finite height.");
                vertices[row * stride + column] = new Vector3(worldX, -height, -worldY);
            }
        }

        int[] indices = new int[divisions * divisions * 6];
        int at = 0;
        for (int row = 0; row < divisions; row++)
        {
            for (int column = 0; column < divisions; column++)
            {
                int nearLeft = row * stride + column;
                int farLeft = nearLeft + stride;
                // Godot treats clockwise triangles as front-facing.
                indices[at++] = nearLeft;
                indices[at++] = farLeft;
                indices[at++] = nearLeft + 1;
                indices[at++] = nearLeft + 1;
                indices[at++] = farLeft;
                indices[at++] = farLeft + 1;
            }
        }
        return new TerrainSurface(divisions, vertices, indices);
    }
}
