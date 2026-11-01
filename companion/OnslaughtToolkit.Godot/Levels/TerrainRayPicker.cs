// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;

namespace OnslaughtToolkit.Companion.Levels;

/// <summary>Intersects a ray with the sampled triangles actually shown by the terrain preview.</summary>
internal static class TerrainRayPicker
{
    internal static bool TryHit(TerrainSurface? surface, Vector3 origin, Vector3 direction, out Vector3 hit)
    {
        hit = default;
        if (surface is null || !Finite(origin) || !Finite(direction)) return false;

        D3 start = D3.From(origin), ray = D3.From(direction);
        double length = Math.Sqrt(D3.Dot(ray, ray));
        if (length == 0 || !double.IsFinite(length)) return false;
        ray /= length;

        var vertices = surface.Vertices.Span;
        var indices = surface.Indices.Span;
        double best = double.PositiveInfinity;
        for (int i = 0; i < indices.Length; i += 3)
        {
            D3 a = D3.From(vertices[indices[i]]), b = D3.From(vertices[indices[i + 1]]), c = D3.From(vertices[indices[i + 2]]);
            D3 edge1 = b - a, edge2 = c - a, p = D3.Cross(ray, edge2);
            double determinant = D3.Dot(edge1, p);
            double scale = Math.Sqrt(D3.Dot(edge1, edge1) * D3.Dot(edge2, edge2));
            if (!double.IsFinite(determinant) || !double.IsFinite(scale) || Math.Abs(determinant) <= scale * 1e-12) continue;

            D3 offset = start - a;
            double u = D3.Dot(offset, p) / determinant;
            if (u < -1e-9 || u > 1 + 1e-9) continue;
            D3 q = D3.Cross(offset, edge1);
            double v = D3.Dot(ray, q) / determinant;
            if (v < -1e-9 || u + v > 1 + 1e-9) continue;
            double distance = D3.Dot(edge2, q) / determinant;
            if (distance >= 0 && distance < best) best = distance;
        }
        if (!double.IsFinite(best)) return false;
        D3 point = start + ray * best;
        hit = new Vector3((float)point.X, (float)point.Y, (float)point.Z);
        return Finite(hit);
    }

    private static bool Finite(Vector3 value) => float.IsFinite(value.X) && float.IsFinite(value.Y) && float.IsFinite(value.Z);

    private readonly record struct D3(double X, double Y, double Z)
    {
        internal static D3 From(Vector3 value) => new(value.X, value.Y, value.Z);
        internal static double Dot(D3 a, D3 b) => a.X * b.X + a.Y * b.Y + a.Z * b.Z;
        internal static D3 Cross(D3 a, D3 b) => new(a.Y * b.Z - a.Z * b.Y, a.Z * b.X - a.X * b.Z, a.X * b.Y - a.Y * b.X);
        public static D3 operator +(D3 a, D3 b) => new(a.X + b.X, a.Y + b.Y, a.Z + b.Z);
        public static D3 operator -(D3 a, D3 b) => new(a.X - b.X, a.Y - b.Y, a.Z - b.Z);
        public static D3 operator *(D3 a, double b) => new(a.X * b, a.Y * b, a.Z * b);
        public static D3 operator /(D3 a, double b) => new(a.X / b, a.Y / b, a.Z / b);
    }
}
