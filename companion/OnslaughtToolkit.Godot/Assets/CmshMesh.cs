// SPDX-License-Identifier: MIT
using System.Buffers.Binary;
using System.Numerics;
using System.Text;

namespace OnslaughtToolkit.Companion.Assets;

/// <summary>A 3×3 orientation as the game stores it: three rows, applied to a column vector (v' = M v).</summary>
public readonly record struct MeshBasis(Vector3 Row0, Vector3 Row1, Vector3 Row2)
{
    public static readonly MeshBasis Identity = new(Vector3.UnitX, Vector3.UnitY, Vector3.UnitZ);

    public Vector3 Apply(Vector3 v) => new(Vector3.Dot(Row0, v), Vector3.Dot(Row1, v), Vector3.Dot(Row2, v));

    public MeshBasis Times(MeshBasis m)
    {
        Vector3 c0 = new(m.Row0.X, m.Row1.X, m.Row2.X), c1 = new(m.Row0.Y, m.Row1.Y, m.Row2.Y), c2 = new(m.Row0.Z, m.Row1.Z, m.Row2.Z);
        Vector3 Row(Vector3 r) => new(Vector3.Dot(r, c0), Vector3.Dot(r, c1), Vector3.Dot(r, c2));
        return new(Row(Row0), Row(Row1), Row(Row2));
    }

    public float Determinant => Vector3.Dot(Row0, Vector3.Cross(Row1, Row2));
}

/// <summary>A part's transform: an orientation and a position.</summary>
public readonly record struct PartTransform(MeshBasis Orientation, Vector3 Position);

/// <summary>One of a mesh's textures, named as the game asks for it, with its five per-frame lanes.</summary>
public sealed record CmshTexture(string Name, float[] Blend, float[] OffsetU, float[] OffsetV, float[] ScaleU, float[] ScaleV);

/// <summary>An animation mode from the mesh's CAMD table.</summary>
public sealed record CmshAnimMode(string Name, int Id, int Start, int Last, int FrameScaler, float Rate);

/// <summary>A run of a part's vertex buffer drawn with one set of texture layers (-1 = none).</summary>
public sealed record CmshPiece(ushort[] Indices, int[] TextureSlots);

public enum PartType { Normal = 1, Null = 2, Skeletal = 3, Camera = 4, Emitter = 5, Reference = 6 }

/// <summary>A mesh part: its hierarchy links, keys, caches and geometry.</summary>
public sealed class CmshPart
{
    public required int Index { get; init; }
    public required string Name { get; init; }
    public required int Type { get; init; }
    public int? Parent { get; internal set; }
    public int[] Children { get; internal set; } = [];
    public int? ReferenceTo { get; internal set; }
    public required int VirtualFrames { get; init; }
    public byte[] FrameMap { get; internal set; } = [];
    public MeshBasis[] KeyOrientations { get; internal set; } = [];
    public Vector3[] KeyPositions { get; internal set; } = [];
    public float[] KeyFieldsOfView { get; internal set; } = [];
    public int[] Bones { get; internal set; } = [];
    public required int CachedFrameCount { get; init; }
    public Vector3[]? CachedPositions { get; internal set; }
    public MeshBasis[]? CachedOrientations { get; internal set; }
    public int VertexStride { get; internal set; }
    public Vector3[] Positions { get; internal set; } = [];
    public Vector3[] Normals { get; internal set; } = [];
    public uint[] Colors { get; internal set; } = [];
    public Vector2[] UVs { get; internal set; } = [];
    /// <summary>For 48-byte (skeletal) vertices: the three bone-palette offsets, each 3 × a BONE index.</summary>
    public Vector3[] PaletteOffsets { get; internal set; } = [];
    public CmshPiece[] Pieces { get; internal set; } = [];

    /// <summary>The key at a virtual frame: the frame is clamped, then mapped through VHFM.</summary>
    public PartTransform Key(int frame)
    {
        if (KeyOrientations.Length == 0 || FrameMap.Length == 0) return new(MeshBasis.Identity, Vector3.Zero);
        int key = FrameMap[Math.Clamp(frame, 0, FrameMap.Length - 1)];
        return new(KeyOrientations[key], KeyPositions.Length > key ? KeyPositions[key] : Vector3.Zero);
    }

    /// <summary>
    /// Triangles from each piece's stitched strip: consecutive index triples, every other one flipped, degenerate
    /// ones dropped. Returned per piece, as vertex indices.
    /// </summary>
    public IEnumerable<(CmshPiece Piece, int[] Triangles)> Triangles()
    {
        foreach (CmshPiece piece in Pieces)
        {
            List<int> triangles = [];
            ushort[] strip = piece.Indices;
            for (int i = 0; i + 2 < strip.Length; i++)
            {
                int a = strip[i], b = strip[i + 1], c = strip[i + 2];
                if (a == b || b == c || a == c) continue;
                if ((i & 1) == 0) triangles.AddRange([a, b, c]);
                else triangles.AddRange([b, a, c]);
            }
            yield return (piece, triangles.ToArray());
        }
    }
}

/// <summary>A mesh from a CMSH stream: its textures, parts and animation modes.</summary>
public sealed class CmshMesh
{
    public required string Name { get; init; }
    public required IReadOnlyList<CmshTexture> Textures { get; init; }
    public required IReadOnlyList<CmshPart> Parts { get; init; }
    public required IReadOnlyList<CmshAnimMode> Modes { get; init; }

    /// <summary>A part's model-space transform at a virtual frame: keys composed from the root (Pp + Op·p, Op·O).</summary>
    public PartTransform ModelSpace(int part, int frame)
    {
        PartTransform parent = Parts[part].Parent is int p && p >= 0 && p < Parts.Count && p != part
            ? ModelSpace(p, frame) : new(MeshBasis.Identity, Vector3.Zero);
        PartTransform key = Parts[part].Key(frame);
        return new(parent.Orientation.Times(key.Orientation), parent.Position + parent.Orientation.Apply(key.Position));
    }
}

/// <summary>Grammar counts a read produced, for checks against the walker (tools/cmsh_grammar_walk.py).</summary>
public sealed class CmshCounts
{
    public int Meshes, Parts, Pieces, Textures, AnimModes, CollisionGrids;
}

/// <summary>
/// Reads a PC CMSH stream with the loader's grammar in reverse-engineering/asset-formats/cmsh-fields.md. Every leaf
/// payload must be consumed exactly and the stream must end where the grammar ends; anything else is refused. Record
/// pointer fields are used only as presence flags, and fields the loader ignores are not read.
/// </summary>
public static class CmshReader
{
    private const int MeshRecord = 372, PartRecord = 316, VertexBufferRecord = 296;

    public static IReadOnlyList<CmshMesh> Read(byte[] stream, CmshCounts? counts = null)
    {
        Cursor c = new(stream);
        List<CmshMesh> meshes = [];
        counts ??= new CmshCounts();
        meshes.Add(ReadMesh(c, counts));
        while (c.Chained)
        {
            c.Chained = false;
            meshes.Add(ReadMesh(c, counts));
        }
        if (c.Position != stream.Length) throw new InvalidDataException($"The mesh grammar ends at byte {c.Position} of {stream.Length}.");
        return meshes;
    }

    private static CmshMesh ReadMesh(Cursor c, CmshCounts counts)
    {
        counts.Meshes++;
        c.Header();
        byte[] mesh = c.Take(MeshRecord);
        int textureCount = I32(mesh, 0x04), sequences = I32(mesh, 0x0C), modeCount = I32(mesh, 0x14), emitters = I32(mesh, 0x1C);
        int partCount = I32(mesh, 0x15C);
        bool chained = I32(mesh, 0x08) != 0;
        string name = Text(mesh, 0x24, 300);
        Require(textureCount >= 0 && partCount >= 0 && sequences >= 0 && modeCount >= 0 && emitters >= 0, "negative count in the mesh record");

        c.Header();
        byte[] records = c.Take(Checked(36, textureCount));
        List<CmshTexture> textures = [];
        for (int t = 0; t < textureCount; t++)
        {
            int frames = I32(records, 36 * t + 8);
            Require(frames >= 0, "negative texture frame count");
            c.Header();
            c.Header();
            float[][] lanes = new float[5][];
            for (int lane = 0; lane < 5; lane++) lanes[lane] = Floats(c.Take(Checked(4, frames)));
            textures.Add(new CmshTexture(Text(c.Take(128), 0, 128), lanes[0], lanes[1], lanes[2], lanes[3], lanes[4]));
            counts.Textures++;
        }

        List<CmshPart> parts = [];
        for (int p = 0; p < partCount; p++) parts.Add(ReadPart(c, p, counts));

        if (sequences > 0)
        {
            c.Header();
            byte[] table = c.Take(Checked(12, sequences));
            for (int q = 0; q < sequences; q++)
                if (I32(table, 12 * q) != 0)
                {
                    c.Header();
                    c.Take(4);
                }
        }
        List<CmshAnimMode> modes = [];
        if (modeCount > 0)
        {
            c.Header();
            byte[] table = c.Take(Checked(36, modeCount));
            for (int m = 0; m < modeCount; m++)
            {
                int o = 36 * m;
                modes.Add(new CmshAnimMode(Text(table, o, 16), I32(table, o + 16), I32(table, o + 20), I32(table, o + 24),
                    I32(table, o + 28), F32(table, o + 32)));
                counts.AnimModes++;
            }
        }
        Box(c);
        if (emitters > 0)
        {
            c.Header();
            int size = I32(c.Take(4), 0);
            Require(size >= 0x44, "emitter record too small");
            for (int e = 0; e < emitters; e++)
                if (I32(c.Take(size), 0x40) != 0) c.Take(4);
        }
        if (chained)
        {
            c.Header();
            c.Chained = true;
        }
        return new CmshMesh { Name = name, Textures = textures, Parts = parts, Modes = modes };
    }

    private static CmshPart ReadPart(Cursor c, int index, CmshCounts counts)
    {
        counts.Parts++;
        c.Header();
        c.Header();
        byte[] r = c.Take(c.Size);
        Require(r.Length >= PartRecord, "part record too small");
        int F(int offset) => I32(r, offset);
        int dvertices = F(0xA8), pvertices = F(0xAC), triangles = F(0xB0), aframes = F(0xB4), vframes = F(0xB8), hframes = F(0xBC), bones = F(0xC0);
        Require(dvertices >= 0 && pvertices >= 0 && triangles >= 0 && aframes >= 0 && vframes >= 0 && hframes >= 0 && bones >= 0 &&
            F(0x90) >= 0 && F(0x118) >= 0, "negative count in a part record");
        CmshPart part = new()
        {
            Index = index, Name = Text(r, 0xDC, 32), Type = F(0x8C), VirtualFrames = vframes, CachedFrameCount = F(0x118),
        };
        if (dvertices > 0)
        {
            c.Header();
            c.Take(Checked(I32(c.Take(4), 0), dvertices));
        }
        if (triangles > 0)
        {
            c.Header();
            c.Take(Checked(12, triangles));
        }
        if (pvertices > 0)
        {
            c.Header();
            c.Take(Checked(Checked(16, pvertices), aframes));
        }
        if (F(0x90) > 0)
        {
            c.Header();
            part.Children = Ints(c.Take(Checked(4, F(0x90))));
        }
        if (F(0x98) != 0)
        {
            c.Header();
            part.Parent = I32(c.Take(4), 0);
        }
        if (F(0x9C) != 0)
        {
            c.Header();
            c.Take(4);
        }
        Box(c);
        if (vframes > 0)
        {
            c.Header();
            part.FrameMap = c.Take(vframes);
        }
        if (hframes > 0)
        {
            if (F(0x10C) != 0)
            {
                Require(c.Header() == "HORI", "the frame-orientation slot is not HORI");
                part.KeyOrientations = Bases(c.Take(Checked(48, hframes)));
            }
            if (F(0xC8) != 0)
            {
                c.Header();
                part.KeyPositions = Vectors(c.Take(Checked(16, hframes)));
            }
            if (F(0xCC) != 0)
            {
                c.Header();
                part.KeyFieldsOfView = Floats(c.Take(Checked(4, hframes)));
            }
        }
        if (bones > 0)
        {
            c.Header();
            part.Bones = Ints(c.Take(Checked(4, bones)));
            if (F(0xD4) != 0)
            {
                c.Header();
                c.Take(Checked(Checked(4, bones), pvertices));
            }
            if (F(0xD8) != 0)
            {
                c.Header();
                c.Take(Checked(12, pvertices));
            }
        }
        if (F(0x100) != 0)
        {
            Grid(c);
            counts.CollisionGrids++;
        }
        if (F(0x104) != 0)
        {
            c.Header();
            part.CachedPositions = Vectors(c.Take(Checked(16, F(0x118))));
        }
        if (F(0x108) != 0)
        {
            Require(c.Header() == "CORI", "the cached-orientation slot is not CORI");
            part.CachedOrientations = Bases(c.Take(Checked(48, F(0x118))));
        }
        if (F(0x124) != 0)
        {
            c.Header();
            part.ReferenceTo = I32(c.Take(4), 0);
        }
        VertexBuffer(c, part, counts);
        return part;
    }

    private static void VertexBuffer(Cursor c, CmshPart part, CmshCounts counts)
    {
        c.Header();
        c.Header();
        byte[] vb = c.Take(VertexBufferRecord);
        int pieces = I32(vb, 0x108);
        Require(pieces is >= 0 and <= 64, "piece count out of range");
        if (pieces == 0) return;
        int stride = I32(vb, 0x114);
        Require(stride is 36 or 48, $"unsupported vertex size {stride}");
        part.VertexStride = stride;
        List<CmshPiece> list = [];
        for (int p = 0; p < pieces; p++)
        {
            counts.Pieces++;
            c.Header();
            int[] piece = Ints(c.Take(24));
            int indexCount = piece[2], vertexCount = piece[3];
            Require(indexCount >= 0 && vertexCount >= 0, "negative piece count");
            c.Header();
            byte[] indexBytes = c.Take(Checked(2, indexCount));
            ushort[] indices = new ushort[indexCount];
            for (int i = 0; i < indexCount; i++) indices[i] = BinaryPrimitives.ReadUInt16LittleEndian(indexBytes.AsSpan(2 * i));
            c.Header();
            if (p == 0) Vertices(part, c.Take(Checked(stride, vertexCount)), stride, vertexCount);
            else c.Skip();
            c.Header();
            list.Add(new CmshPiece(indices, Ints(c.Take(24))));
        }
        foreach (CmshPiece piece in list)
            Require(piece.Indices.All(i => i < part.Positions.Length), "an index points past the part's vertices");
        part.Pieces = list.ToArray();
    }

    private static void Vertices(CmshPart part, byte[] data, int stride, int count)
    {
        Vector3[] positions = new Vector3[count], normals = new Vector3[count], palette = stride == 48 ? new Vector3[count] : [];
        uint[] colors = new uint[count];
        Vector2[] uvs = new Vector2[count];
        int normal = stride == 48 ? 0x18 : 0x0C, color = stride == 48 ? 0x24 : 0x18, uv = stride == 48 ? 0x28 : 0x1C;
        for (int v = 0; v < count; v++)
        {
            int o = stride * v;
            positions[v] = Vec3(data, o);
            if (stride == 48) palette[v] = Vec3(data, o + 0x0C);
            normals[v] = Vec3(data, o + normal);
            colors[v] = BinaryPrimitives.ReadUInt32LittleEndian(data.AsSpan(o + color));
            uvs[v] = new Vector2(F32(data, o + uv), F32(data, o + uv + 4));
        }
        (part.Positions, part.Normals, part.Colors, part.UVs, part.PaletteOffsets) = (positions, normals, colors, uvs, palette);
    }

    private static void Grid(Cursor c)
    {
        c.Header();
        c.Header();
        byte[] grid = c.Take(c.Size);
        Require(grid.Length >= 0x70, "collision grid record too small");
        int width = I32(grid, 0x68), height = I32(grid, 0x6C);
        Require(width >= 0 && height >= 0, "negative grid size");
        c.Header();
        c.Take(8);
        for (long cell = 0; cell < (long)width * height; cell++)
        {
            c.Header();
            if (I32(c.Take(4), 0) == 1)
            {
                c.Header();
                c.Header();
                c.Take(Checked(2, I32(c.Take(4), 0)));
            }
        }
        c.Header();
        int triangles = I32(c.Take(4), 0);
        c.Header();
        for (int t = 0; t < triangles; t++)
        {
            c.Header();
            c.Take(12);
        }
        c.Header();
        int vertices = I32(c.Take(4), 0);
        for (int v = 0; v < vertices; v++)
        {
            c.Header();
            c.Take(6);
        }
    }

    private static void Box(Cursor c)
    {
        c.Header();
        c.Header();
        c.Take(40);
    }

    private sealed class Cursor(byte[] data)
    {
        public int Position { get; private set; }
        public int Size { get; private set; }
        private int _used;
        public bool Chained { get; set; }

        public string Header()
        {
            if (data.Length - Position < 8) throw new InvalidDataException("The stream ends before a chunk header.");
            string tag = Encoding.Latin1.GetString(data, Position, 4);
            uint size = BinaryPrimitives.ReadUInt32LittleEndian(data.AsSpan(Position + 4));
            Require(size <= int.MaxValue, "chunk size out of range");
            (Size, _used, Position) = ((int)size, 0, Position + 8);
            return tag;
        }

        public byte[] Take(int count)
        {
            if (count < 0 || count > Size - _used || count > data.Length - Position)
                throw new InvalidDataException($"A read of {count} bytes runs past the chunk at byte {Position}.");
            _used += count;
            byte[] result = data.AsSpan(Position, count).ToArray();
            Position += count;
            return result;
        }

        public void Skip()
        {
            int rest = Size - _used;
            if (rest > data.Length - Position) throw new InvalidDataException("A skipped chunk runs past the stream.");
            Position += rest;
            _used = Size;
        }
    }

    private static void Require(bool condition, string message)
    {
        if (!condition) throw new InvalidDataException("Not a supported mesh: " + message + ".");
    }

    private static int Checked(int unit, int count)
    {
        long bytes = (long)unit * count;
        Require(unit >= 0 && count >= 0 && bytes <= int.MaxValue, "array size out of range");
        return (int)bytes;
    }

    private static int I32(byte[] b, int o) => BinaryPrimitives.ReadInt32LittleEndian(b.AsSpan(o));
    private static float F32(byte[] b, int o) => BinaryPrimitives.ReadSingleLittleEndian(b.AsSpan(o));
    private static Vector3 Vec3(byte[] b, int o) => new(F32(b, o), F32(b, o + 4), F32(b, o + 8));

    private static string Text(byte[] b, int o, int length)
    {
        int end = Array.IndexOf(b, (byte)0, o, length);
        return Encoding.Latin1.GetString(b, o, (end < 0 ? o + length : end) - o);
    }

    private static int[] Ints(byte[] b) => Enumerable.Range(0, b.Length / 4).Select(i => I32(b, 4 * i)).ToArray();
    private static float[] Floats(byte[] b) => Enumerable.Range(0, b.Length / 4).Select(i => F32(b, 4 * i)).ToArray();
    private static Vector3[] Vectors(byte[] b) => Enumerable.Range(0, b.Length / 16).Select(i => Vec3(b, 16 * i)).ToArray();
    private static MeshBasis[] Bases(byte[] b) =>
        Enumerable.Range(0, b.Length / 48).Select(i => new MeshBasis(Vec3(b, 48 * i), Vec3(b, 48 * i + 16), Vec3(b, 48 * i + 32))).ToArray();
}
