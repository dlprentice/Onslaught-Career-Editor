// SPDX-License-Identifier: GPL-3.0-only
using System.Diagnostics;
using Godot;
using OnslaughtToolkit.Companion.Levels;
using NumericVector3 = System.Numerics.Vector3;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Authored surface, topology and small-feature checks; no retail input, stager, saved career or external action.</summary>
public partial class TerrainSurfaceFidelityTests : SceneTree
{
    public override void _Initialize() => _ = RunFocusedAsync();
    private async Task RunFocusedAsync()
    {
        int code = 1;
        try
        {
            await ToSignal(this, SignalName.ProcessFrame);
            Checks check = new(); Run(check);
            foreach (string failure in check.Failures) GD.PrintErr("FAIL: " + failure);
            GD.Print($"TERRAIN_SURFACE_FIDELITY: {check.Count} checks, {check.Failures.Count} failures; authored fixtures only.");
            code = check.Failures.Count == 0 ? 0 : 1;
        }
        catch (Exception error) { GD.PrintErr("TERRAIN_SURFACE_FIDELITY stopped: " + error); }
        finally { Quit(code); }
    }

    internal static float Cell => Heightfield.Size / TerrainSurface.DefaultDivisions;
    internal static float PeakX => Heightfield.Size * 0.5f + Cell * 0.25f;
    internal static float PeakY => PeakX;
    internal static float Hill(float x, float y) => -32 * MathF.Max(0, 1 - MathF.Abs(x - PeakX) / (Cell * 0.25f)) *
        MathF.Max(0, 1 - MathF.Abs(y - PeakY) / (Cell * 0.25f));
    internal static long MeshPayload(TerrainSurface surface) => surface.Vertices.Length * 24L + surface.Indices.Length * 4L;

    internal static void Run(Checks check)
    {
        check.Suite("bounded preview surface fidelity");
        TerrainSurface flat = TerrainSurface.Build((_, _) => 7, TerrainSurface.DefaultDivisions);
        check.That(ReferenceEquals(TerrainSurface.BuildPreview((_, _) => 7, flat), flat), "a flat sampled field keeps the original mesh");
        TerrainSurface coarse = TerrainSurface.Build(Hill, TerrainSurface.DefaultDivisions);
        NumericVector3[] before = coarse.Vertices.ToArray(); int[] oldIndices = coarse.Indices.ToArray();
        long allocationBefore = GC.GetAllocatedBytesForCurrentThread(); Stopwatch watch = Stopwatch.StartNew();
        TerrainSurface refined = TerrainSurface.BuildPreview(Hill, coarse);
        watch.Stop(); long allocated = GC.GetAllocatedBytesForCurrentThread() - allocationBefore;
        check.That(coarse.Vertices.Span.ToArray().All(point => point.Y == 0), "the authored small feature lies between every editable grid sample");
        check.That(Hit(coarse, PeakX, PeakY, out var oldHit) && oldHit.Y == 0 &&
                   Hit(refined, PeakX, PeakY, out var newHit) && Math.Abs(newHit.Y - 32) < 0.0001,
                   "actual ray picking recovers the authored feature missed by the editable grid");
        check.That(refined.Divisions == coarse.Divisions && PrefixMatches(refined, before), "refinement retains every editable vertex and its index exactly");
        check.That(coarse.Vertices.Span.SequenceEqual(before) && coarse.Indices.Span.SequenceEqual(oldIndices), "refinement never mutates its editable source");
        check.That(refined.Vertices.Length < coarse.Vertices.Length * 2 && refined.Indices.Length < coarse.Indices.Length * 2,
                   "the small-feature refinement stays below twice the original vertex and triangle budgets");
        check.That(Watertight(refined), "fine patches and coarse neighbours form a conforming surface without internal open edges");
        TerrainSurface repeated = TerrainSurface.BuildPreview(Hill, coarse);
        check.That(refined.Vertices.Span.SequenceEqual(repeated.Vertices.Span) && refined.Indices.Span.SequenceEqual(repeated.Indices.Span),
                   "identical sampled inputs produce identical vertices and triangle order");
        check.That(OuterCellsUnchanged(coarse, refined), "the original outermost cell triangles and both-sided inset behaviour remain unchanged");

        int baseIndex = TerrainSurface.DefaultDivisions / 2 * (TerrainSurface.DefaultDivisions + 1) + TerrainSurface.DefaultDivisions / 2;
        TerrainSurface edited = coarse.WithVertexHeight(baseIndex, coarse.Vertices.Span[baseIndex].Y + 2);
        TerrainSurface editedPreview = TerrainSurface.BuildPreview(Hill, edited);
        check.That(PrefixMatches(editedPreview, edited.Vertices.ToArray()) && Hit(editedPreview, PeakX, PeakY, out var editedHit) && Math.Abs(editedHit.Y - 33) < 0.0001,
                   "a coarse preview edit keeps its stored index and its existing linear offset while retaining the sampled feature");
        check.That(Hit(refined, PeakX, PeakY, out var unchangedHit) && Math.Abs(unchangedHit.Y - 32) < 0.0001,
                   "building a later preview leaves the earlier render/pick surface unchanged");

        float tinyX = Heightfield.Size * 0.5f + Cell * 0.125f, tinyY = tinyX;
        float Tiny(float x, float y) => -32 * MathF.Max(0, 1 - MathF.Abs(x - tinyX) / (Cell * 0.04f)) *
            MathF.Max(0, 1 - MathF.Abs(y - tinyY) / (Cell * 0.04f));
        TerrainSurface tinyBase = TerrainSurface.Build(Tiny, TerrainSurface.DefaultDivisions);
        TerrainSurface tinyPreview = TerrainSurface.BuildPreview(Tiny, tinyBase);
        check.That(Tiny(tinyX, tinyY) == -32 && Hit(tinyPreview, tinyX, tinyY, out var tinyHit) && tinyHit.Y == 0,
                   "a feature below the bounded sampling cadence is an explicit missed-feature counterexample");
        float Saddle(float x, float y) => -1000 * (x / Heightfield.Size) * (y / Heightfield.Size);
        TerrainSurface saddle = TerrainSurface.BuildPreview(Saddle, TerrainSurface.Build(Saddle, TerrainSurface.DefaultDivisions));
        float sx = Heightfield.Size * 0.5f + Cell * 0.31f, sy = Heightfield.Size * 0.5f + Cell * 0.23f;
        check.That(Hit(saddle, sx, sy, out var saddleHit) && Math.Abs(saddleHit.Y + Saddle(sx, sy)) > 0.00001,
                   "even a bilinear field can retain triangle error, so this preview establishes no game-ground agreement");
        Heightfield field = Heightfield.Read(LevelTests.Unpack(LevelVectors.Terrain.Eres));
        TerrainSurface grid = TerrainSurface.Build(field);
        TerrainSurface cached = TerrainSurface.BuildPreview(field, grid);
        long warmBefore = GC.GetAllocatedBytesForCurrentThread(); Stopwatch warm = Stopwatch.StartNew();
        TerrainSurface reused = TerrainSurface.BuildPreview(field, grid);
        warm.Stop(); long warmAllocated = GC.GetAllocatedBytesForCurrentThread() - warmBefore;
        check.That(ReferenceEquals(cached, reused) && warmAllocated < MeshPayload(grid),
                   "the immutable field reuses its bounded plan rather than rebuilding the sampled mesh on refresh");
        TerrainSurface alteredGrid = grid.WithVertexHeight(baseIndex, grid.Vertices.Span[baseIndex].Y + 2);
        TerrainSurface alteredPreview = TerrainSurface.BuildPreview(field, alteredGrid);
        check.That(PrefixMatches(alteredPreview, alteredGrid.Vertices.ToArray()) && TerrainSurface.BuildPreview(field, grid).Vertices.Span.SequenceEqual(cached.Vertices.Span),
                   "cached plans apply current draft offsets without changing their baseline or earlier previews");
        GD.Print($"AUTHORED_PREVIEW_COST: base {coarse.Vertices.Length} vertices/{coarse.Indices.Length / 3} triangles/{MeshPayload(coarse)} mesh-payload bytes; " +
            $"adaptive {refined.Vertices.Length} vertices/{refined.Indices.Length / 3} triangles/{MeshPayload(refined)} bytes; " +
            $"build {watch.Elapsed.TotalMilliseconds:0.###} ms, managed allocation {allocated} bytes (single authored run; no performance acceptance).");
        GD.Print($"AUTHORED_PREVIEW_WARM_COST: {warm.Elapsed.TotalMilliseconds:0.###} ms, {warmAllocated} managed bytes; authored immutable field reuse only.");
    }

    private static bool Hit(TerrainSurface surface, float x, float y, out NumericVector3 hit) =>
        TerrainRayPicker.TryHit(surface, new NumericVector3(x, 10000, -y), -NumericVector3.UnitY, out hit);
    private static bool PrefixMatches(TerrainSurface surface, NumericVector3[] expected)
    {
        for (int i = 0; i < expected.Length; i++)
        {
            var a = surface.Vertices.Span[i]; var b = expected[i];
            if (BitConverter.SingleToInt32Bits(a.X) != BitConverter.SingleToInt32Bits(b.X) ||
                BitConverter.SingleToInt32Bits(a.Y) != BitConverter.SingleToInt32Bits(b.Y) ||
                BitConverter.SingleToInt32Bits(a.Z) != BitConverter.SingleToInt32Bits(b.Z)) return false;
        }
        return true;
    }
    private static bool Watertight(TerrainSurface surface)
    {
        Dictionary<(int, int), int> uses = [];
        var indices = surface.Indices.Span;
        for (int i = 0; i < indices.Length; i += 3)
            for (int j = 0; j < 3; j++)
            {
                int a = indices[i + j], b = indices[i + (j + 1) % 3];
                var key = a < b ? (a, b) : (b, a); uses[key] = uses.GetValueOrDefault(key) + 1;
            }
        foreach (var pair in uses)
        {
            if (pair.Value == 2) continue;
            if (pair.Value != 1) return false;
            var a = surface.Vertices.Span[pair.Key.Item1]; var b = surface.Vertices.Span[pair.Key.Item2];
            if (!((a.X == 0 && b.X == 0) || (a.X == Heightfield.Size && b.X == Heightfield.Size) ||
                  (a.Z == 0 && b.Z == 0) || (a.Z == -Heightfield.Size && b.Z == -Heightfield.Size))) return false;
        }
        return true;
    }
    private static bool OuterCellsUnchanged(TerrainSurface before, TerrainSurface after)
    {
        HashSet<(int, int, int)> triangles = [];
        var next = after.Indices.Span;
        for (int i = 0; i < next.Length; i += 3) triangles.Add((next[i], next[i + 1], next[i + 2]));
        int d = before.Divisions;
        for (int row = 0; row < d; row++)
            for (int column = 0; column < d; column++)
                if (row == 0 || column == 0 || row == d - 1 || column == d - 1)
                {
                    int at = (row * d + column) * 6;
                    var indices = before.Indices.Span;
                    if (!triangles.Contains((indices[at], indices[at + 1], indices[at + 2])) ||
                        !triangles.Contains((indices[at + 3], indices[at + 4], indices[at + 5]))) return false;
                }
        return true;
    }
}
