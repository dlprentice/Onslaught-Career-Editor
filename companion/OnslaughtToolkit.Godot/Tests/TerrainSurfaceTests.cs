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

        check.That(TerrainRayPicker.TryHit(flat, new Vector3(128, 50, -96), -Vector3.UnitY, out Vector3 flatHit) &&
            Vector3.Distance(flatHit, new Vector3(128, -7, -96)) < 0.001f,
            "A downward ray meets the visible flat terrain at the expected point");
        check.That(TerrainRayPicker.TryHit(slope, new Vector3(128, 1000, -128), -Vector3.UnitY, out Vector3 slopeHit) &&
            Vector3.Distance(slopeHit, new Vector3(128, -384, -128)) < 0.05f,
            "A ray meets a sampled slope in the view's coordinates");
        check.That(!TerrainRayPicker.TryHit(flat, new Vector3(-10, 50, -96), -Vector3.UnitY, out _) &&
            !TerrainRayPicker.TryHit(flat, new Vector3(128, 50, -96), Vector3.UnitY, out _) &&
            !TerrainRayPicker.TryHit(flat, new Vector3(128, 50, -96), Vector3.UnitX, out _),
            "A ray that misses, points away, or is parallel makes no terrain hit");
        check.That(!TerrainRayPicker.TryHit(null, Vector3.Zero, Vector3.UnitY, out _) &&
            !TerrainRayPicker.TryHit(flat, Vector3.Zero, Vector3.Zero, out _) &&
            !TerrainRayPicker.TryHit(flat, new Vector3(float.NaN, 0, 0), Vector3.UnitY, out _) &&
            !TerrainRayPicker.TryHit(flat, Vector3.Zero, new Vector3(0, float.PositiveInfinity, 0), out _),
            "Missing terrain and invalid rays never pick a point");
        check.That(TerrainRayPicker.TryHit(flat, new Vector3(128, 50, -96), new Vector3(0, -1e-35f, 0), out Vector3 shortRay) &&
            Vector3.Distance(shortRay, flatHit) < 0.001f,
            "The terrain hit does not depend on ray length");
        TerrainSurface ridge = TerrainSurface.Build((x, _) => x is > 128 and < 384 ? -10 : 0, 2);
        check.That(TerrainRayPicker.TryHit(ridge, new Vector3(-10, 5, -256), Vector3.UnitX, out Vector3 ridgeHit) &&
            Math.Abs(ridgeHit.X - 128) < 0.01,
            "When a ray crosses terrain twice the nearest intersection wins");
    }

    private static bool Throws<T>(Action action) where T : Exception
    {
        try { action(); }
        catch (T) { return true; }
        return false;
    }
}
