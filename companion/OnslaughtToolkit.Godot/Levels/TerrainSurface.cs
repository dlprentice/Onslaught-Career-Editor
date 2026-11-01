// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;
using System.Runtime.CompilerServices;

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
    // Managed data only; weak heightfield keys and one grid plan per key bound retention without engine resources.
    private static readonly ConditionalWeakTable<Heightfield, PreviewCache> PreviewCaches = new();
    private sealed class PreviewCache { internal PreviewPlan? Current; }
    private sealed record PreviewPlan(TerrainSurface Baseline, TerrainSurface Refined);

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

    /// <summary>Samples an existing read-only terrain. A malformed non-finite height is refused.</summary>
    public static TerrainSurface Build(Heightfield field, int divisions = DefaultDivisions)
    {
        ArgumentNullException.ThrowIfNull(field);
        return Build(field.HeightAt, divisions);
    }

    /// <summary>
    /// A bounded render/pick refinement of the editable grid. The original grid vertices and indices used by
    /// terrain drafts stay with that grid; this derived mesh is never a terrain draft or a game-ground oracle.
    /// Heightfield.HeightAt owns the height function. Flat triangles still approximate that function.
    /// </summary>
    internal static TerrainSurface BuildPreview(Heightfield field, TerrainSurface editable)
    {
        ArgumentNullException.ThrowIfNull(field);
        ArgumentNullException.ThrowIfNull(editable);
        PreviewCache cache = PreviewCaches.GetValue(field, _ => new());
        PreviewPlan plan;
        lock (cache)
        {
            if (cache.Current is not { } current || current.Baseline.Divisions != editable.Divisions)
            {
                TerrainSurface baseline = Build(field, editable.Divisions);
                cache.Current = new PreviewPlan(baseline, BuildPreview(field.HeightAt, baseline, Math.Abs((double)field.Scale) * 2));
            }
            plan = cache.Current!;
        }
        if (editable._vertices.Length != plan.Baseline._vertices.Length)
            throw new ArgumentException("Preview refinement requires the regular editable grid.", nameof(editable));
        double[]? offsets = null;
        for (int i = 0; i < editable._vertices.Length; i++)
        {
            Vector3 point = editable._vertices[i], original = plan.Baseline._vertices[i];
            if (point.X != original.X || point.Z != original.Z)
                throw new ArgumentException("The editable grid coordinates changed.", nameof(editable));
            if (BitConverter.SingleToInt32Bits(point.Y) == BitConverter.SingleToInt32Bits(original.Y)) continue;
            offsets ??= new double[editable._vertices.Length];
            offsets[i] = (double)point.Y - original.Y;
        }
        if (offsets is null) return plan.Refined;
        Vector3[] vertices = plan.Refined._vertices.ToArray();
        Array.Copy(editable._vertices, vertices, editable._vertices.Length);
        for (int i = editable._vertices.Length; i < vertices.Length; i++)
        {
            Vector3 point = vertices[i];
            double x = (double)point.X * editable.Divisions / Heightfield.Size, y = -(double)point.Z * editable.Divisions / Heightfield.Size;
            int column = Math.Min(editable.Divisions - 1, (int)Math.Floor(x)), row = Math.Min(editable.Divisions - 1, (int)Math.Floor(y));
            double offset = PreviewRefinement.Linear(offsets, editable.Divisions, column, row, x - column, y - row);
            point.Y = (float)((double)point.Y + offset);
            if (!float.IsFinite(point.Y)) throw new InvalidDataException("Terrain preview offsets cannot be represented.");
            vertices[i] = point;
        }
        return new TerrainSurface(editable.Divisions, vertices, plan.Refined._indices);
    }

    internal static TerrainSurface BuildPreview(Func<float, float, float> heightAt, TerrainSurface editable, double roundingEnvelope = 0)
    {
        ArgumentNullException.ThrowIfNull(heightAt);
        ArgumentNullException.ThrowIfNull(editable);
        if (!double.IsFinite(roundingEnvelope) || roundingEnvelope < 0) throw new ArgumentOutOfRangeException(nameof(roundingEnvelope));
        if (editable._vertices.Length != checked((editable.Divisions + 1) * (editable.Divisions + 1)))
            throw new ArgumentException("Preview refinement requires the regular editable grid.", nameof(editable));
        return new PreviewRefinement(heightAt, editable, roundingEnvelope).Build();
    }

    private sealed class PreviewRefinement
    {
        // These are preview work budgets, not statements about the game's collision or rendering grid.
        private const int FinestDivisions = 512, StableBorderCells = 2, CellsPerRefinement = 64;
        private readonly Func<float, float, float> _heightAt;
        private readonly TerrainSurface _editable;
        private readonly double _roundingEnvelope;
        private readonly int _divisions, _factor, _fineDivisions;
        private readonly double[] _offsets;
        private readonly bool _hasOffsets;
        private readonly float[] _sampleValues;
        private readonly bool[] _sampled;
        private readonly Dictionary<long, int> _vertexAt = [];
        private readonly List<Vector3> _vertices;

        internal PreviewRefinement(Func<float, float, float> heightAt, TerrainSurface editable, double roundingEnvelope)
        {
            _heightAt = heightAt; _editable = editable; _roundingEnvelope = roundingEnvelope;
            _divisions = editable.Divisions;
            _factor = _divisions * 4 <= FinestDivisions ? 4 : 2;
            _fineDivisions = _divisions * _factor;
            int probes = checked((_fineDivisions + 1) * (_fineDivisions + 1));
            _sampleValues = new float[probes];
            _sampled = new bool[probes];
            _vertices = [.. editable._vertices];
            _offsets = new double[_vertices.Count];
            for (int row = 0; row <= _divisions; row++)
                for (int column = 0; column <= _divisions; column++)
                {
                    int index = row * (_divisions + 1) + column;
                    Vector3 point = _vertices[index];
                    float baseline = SampleHeight(point.X, -point.Z);
                    _offsets[index] = (double)point.Y - baseline;
                    _hasOffsets |= _offsets[index] != 0;
                    _vertexAt.Add(Key(column * _factor, row * _factor), index);
                }
        }

        internal TerrainSurface Build()
        {
            int budget = _divisions * _divisions / CellsPerRefinement;
            if (budget == 0) return _editable;
            PriorityQueue<int, (double Error, int Cell)> candidates = new();
            for (int row = StableBorderCells; row < _divisions - StableBorderCells; row++)
                for (int column = StableBorderCells; column < _divisions - StableBorderCells; column++)
                {
                    double error = Error(column, row);
                    int cell = row * _divisions + column;
                    if (error > 0) candidates.Enqueue(cell, (-error, cell));
                }
            HashSet<int> refined = [];
            while (refined.Count < budget && candidates.TryDequeue(out int cell, out _)) refined.Add(cell);
            if (refined.Count == 0) return _editable;

            // Register all fine patch vertices first, so adjacent coarse cells can stitch to their exact shared edges.
            foreach (int cell in refined.Order())
            {
                int x = cell % _divisions * _factor, y = cell / _divisions * _factor;
                for (int row = 0; row <= _factor; row++)
                    for (int column = 0; column <= _factor; column++) AddSample(x + column, y + row);
            }
            List<int> indices = [];
            for (int row = 0; row < _divisions; row++)
                for (int column = 0; column < _divisions; column++)
                {
                    int x = column * _factor, y = row * _factor;
                    if (refined.Contains(row * _divisions + column))
                    {
                        for (int v = 0; v < _factor; v++)
                            for (int u = 0; u < _factor; u++) Quad(indices, x + u, y + v, 1);
                        continue;
                    }
                    List<int> boundary = [_vertexAt[Key(x, y)]];
                    Edge(boundary, x, y, 0, 1, includeEnd: true);
                    Edge(boundary, x, y + _factor, 1, 0, includeEnd: true);
                    Edge(boundary, x + _factor, y + _factor, 0, -1, includeEnd: true);
                    Edge(boundary, x + _factor, y, -1, 0, includeEnd: false);
                    if (boundary.Count == 4) { Quad(indices, x, y, _factor); continue; }
                    int cx = x + _factor / 2, cy = y + _factor / 2;
                    // A transition cell retains its old centre, rather than inventing extra terrain detail there.
                    float centreHeight = (float)Linear(_editable._vertices, column, row, 0.5, 0.5);
                    int centre = AddVertex(cx, cy, centreHeight);
                    for (int i = 0; i < boundary.Count; i++)
                    { indices.Add(centre); indices.Add(boundary[i]); indices.Add(boundary[(i + 1) % boundary.Count]); }
                }
            return new TerrainSurface(_divisions, [.. _vertices], [.. indices]);
        }

        private double Error(int column, int row)
        {
            double maximum = 0, magnitude = 0;
            int x = column * _factor, y = row * _factor;
            for (int v = 0; v <= _factor; v++)
                for (int u = 0; u <= _factor; u++)
                {
                    float actual = At(x + u, y + v);
                    double coarse = Linear(_editable._vertices, column, row, (double)u / _factor, (double)v / _factor);
                    maximum = Math.Max(maximum, Math.Abs(actual - coarse));
                    magnitude = Math.Max(magnitude, Math.Abs(actual));
                }
            return maximum - Math.Max(0.0001, _roundingEnvelope + magnitude * 0.000001);
        }

        private static long Key(int x, int y) => ((long)y << 32) | (uint)x;
        private float Coordinate(int at) => Heightfield.Size * at / _fineDivisions;
        private float SampleHeight(float x, float y)
        {
            float value = -_heightAt(Math.Clamp(x, EdgeInset, Heightfield.Size - EdgeInset), Math.Clamp(y, EdgeInset, Heightfield.Size - EdgeInset));
            if (!float.IsFinite(value)) throw new InvalidDataException("Terrain contains a non-finite height.");
            return value;
        }

        private float At(int x, int y)
        {
            if (x % _factor == 0 && y % _factor == 0)
                return _editable._vertices[y / _factor * (_divisions + 1) + x / _factor].Y;
            int probe = y * (_fineDivisions + 1) + x;
            if (_sampled[probe]) return _sampleValues[probe];
            int column = Math.Min(_divisions - 1, x / _factor), row = Math.Min(_divisions - 1, y / _factor);
            double u = (double)x / _factor - column, v = (double)y / _factor - row;
            float value = (float)(SampleHeight(Coordinate(x), Coordinate(y)) + (_hasOffsets ? Linear(_offsets, column, row, u, v) : 0));
            if (!float.IsFinite(value)) throw new InvalidDataException("Terrain preview offsets cannot be represented.");
            _sampleValues[probe] = value;
            _sampled[probe] = true;
            return value;
        }

        private double Linear(IReadOnlyList<Vector3> values, int column, int row, double u, double v) =>
            Linear(values[row * (_divisions + 1) + column].Y, values[row * (_divisions + 1) + column + 1].Y,
                values[(row + 1) * (_divisions + 1) + column].Y, values[(row + 1) * (_divisions + 1) + column + 1].Y, u, v);
        private double Linear(IReadOnlyList<double> values, int column, int row, double u, double v) =>
            Linear(values, _divisions, column, row, u, v);
        internal static double Linear(IReadOnlyList<double> values, int divisions, int column, int row, double u, double v) =>
            Linear(values[row * (divisions + 1) + column], values[row * (divisions + 1) + column + 1],
                values[(row + 1) * (divisions + 1) + column], values[(row + 1) * (divisions + 1) + column + 1], u, v);
        private static double Linear(double a, double b, double c, double d, double u, double v) => u + v <= 1
            ? a + u * (b - a) + v * (c - a) : d + (1 - v) * (b - d) + (1 - u) * (c - d);
        private int AddSample(int x, int y) => AddVertex(x, y, At(x, y));
        private int AddVertex(int x, int y, float height)
        {
            long key = Key(x, y);
            if (_vertexAt.TryGetValue(key, out int index)) return index;
            index = _vertices.Count;
            _vertices.Add(new Vector3(Coordinate(x), height, -Coordinate(y)));
            _vertexAt.Add(key, index);
            return index;
        }
        private void Edge(List<int> boundary, int x, int y, int dx, int dy, bool includeEnd)
        {
            int end = includeEnd ? _factor : _factor - 1;
            for (int i = 1; i <= end; i++)
                if (_vertexAt.TryGetValue(Key(x + i * dx, y + i * dy), out int index)) boundary.Add(index);
        }
        private void Quad(List<int> indices, int x, int y, int size)
        {
            int a = _vertexAt[Key(x, y)], b = _vertexAt[Key(x + size, y)], c = _vertexAt[Key(x, y + size)], d = _vertexAt[Key(x + size, y + size)];
            indices.Add(a); indices.Add(c); indices.Add(b); indices.Add(b); indices.Add(c); indices.Add(d);
        }
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
