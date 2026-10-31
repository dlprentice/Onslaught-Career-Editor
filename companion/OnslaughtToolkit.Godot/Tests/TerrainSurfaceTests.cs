// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Tests;

internal static class TerrainSurfaceTests
{
    internal static void Run(Checks check, Heightfield field)
    {
        TerrainSurface flat = TerrainSurface.Build((_, _) => 7, 2);
        ReadOnlySpan<Vector3> vertices = flat.Vertices.Span;
        ReadOnlySpan<int> indices = flat.Indices.Span;
        check.That(flat.Divisions == 2 && vertices.Length == 9 && indices.Length == 24,
            "3D terrain has the expected bounded grid and triangle count");
        check.That(vertices[0] == new Vector3(0, -7, 0) &&
            vertices[^1] == new Vector3(Heightfield.Size, -7, -Heightfield.Size),
            "3D terrain maps horizontal axes and down-positive heights");

        bool valid = true, facingUp = true;
        for (int at = 0; at < indices.Length; at += 3)
        {
            int a = indices[at], b = indices[at + 1], c = indices[at + 2];
            if (a < 0 || b < 0 || c < 0 || a >= vertices.Length || b >= vertices.Length || c >= vertices.Length)
            {
                valid = false;
                break;
            }
            Vector3 up = Vector3.Cross(vertices[c] - vertices[a], vertices[b] - vertices[a]);
            facingUp &= up.Y > 0;
        }
        check.That(valid && facingUp, "3D terrain triangles use valid indices and face upward in Godot");

        bool inside = true;
        TerrainSurface slope = TerrainSurface.Build((x, y) =>
        {
            inside &= x > 0 && x < Heightfield.Size && y > 0 && y < Heightfield.Size;
            return x + 2 * y;
        }, 2);
        Vector3 middle = slope.Vertices.Span[4];
        float centre = Heightfield.Size / 2;
        check.That(inside, "3D terrain never asks the height lookup outside its defined square");
        check.That(middle == new Vector3(centre, -3 * centre, -centre),
            "3D terrain samples the right world point for an interior slope");

        TerrainSurface actual = TerrainSurface.Build(field, 2);
        check.That(actual.Vertices.Span[4].Y == -field.HeightAt(centre, centre),
            "3D terrain uses the existing authored heightfield lookup");
        check.That(TerrainSurface.Build((_, _) => 0, TerrainSurface.MaxDivisions).Indices.Length ==
            TerrainSurface.MaxDivisions * TerrainSurface.MaxDivisions * 6,
            "3D terrain supports its documented maximum resolution");
        check.That(Throws<ArgumentOutOfRangeException>(() => TerrainSurface.Build((_, _) => 0, 0)) &&
            Throws<ArgumentOutOfRangeException>(() => TerrainSurface.Build((_, _) => 0, TerrainSurface.MaxDivisions + 1)),
            "3D terrain refuses resolutions outside its bounds");
        check.That(Throws<ArgumentNullException>(() => TerrainSurface.Build((Heightfield)null!)) &&
            Throws<ArgumentNullException>(() => TerrainSurface.Build((Func<float, float, float>)null!, 1)),
            "3D terrain refuses a missing field or sampler");
        check.That(Throws<InvalidDataException>(() => TerrainSurface.Build((_, _) => float.NaN, 1)) &&
            Throws<InvalidDataException>(() => TerrainSurface.Build((_, _) => float.PositiveInfinity, 1)),
            "3D terrain refuses non-finite heights");
    }

    private static bool Throws<T>(Action action) where T : Exception
    {
        try { action(); }
        catch (T) { return true; }
        return false;
    }
}
