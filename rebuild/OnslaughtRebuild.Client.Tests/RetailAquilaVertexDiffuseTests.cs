// SPDX-License-Identifier: GPL-3.0-or-later

using System.Buffers.Binary;
using System.IO.Compression;
using System.Text;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// The three retained Aquila specimens carry the same per-vertex D3DCOLOR
/// DIFFUSE dword the static world does, and the released renderer consumes it.
///
/// The render-state evidence is stated once, in
/// <see cref="Level100VertexDiffuseTests"/>: read read-only out of the
/// maintainer Ghidra database, <c>D3DStateCache__UseDefaultRenderState</c> at
/// <c>0x004EB1E0</c> sets <c>D3DRS_LIGHTING</c> TRUE,
/// <c>D3DRS_DIFFUSEMATERIALSOURCE</c> and <c>D3DRS_AMBIENTMATERIALSOURCE</c>
/// both <c>D3DMCS_COLOR1</c>, and stage zero
/// <c>COLORARG1 = D3DTA_TEXTURE</c> / <c>COLORARG2 = D3DTA_DIFFUSE</c>;
/// <c>D3DRS_COLORVERTEX</c> is written at none of the 547 render-state call
/// sites and so keeps its <c>TRUE</c> Direct3D 8 default; and
/// <c>CMeshRenderer__RenderMeshCore</c> clears lighting only around modes 2
/// and 6, restoring it immediately, so the base mesh pass runs lit.
///
/// These tests measure the bytes of the retained specimens themselves rather
/// than restating that. The walker loader is a Godot-project type this test
/// assembly cannot reference, so the vertex stream is re-walked here from the
/// materialized <c>.aya</c> files with an independent reader.
/// </summary>
public sealed class RetailAquilaVertexDiffuseTests
{
    private const string SourceDirectory = "Assets/Aquila/Source";

    /// <summary>
    /// Owned vertices per specimen. A part carrying <c>REFR</c> shares an
    /// earlier part's vertex stream and owns no bytes of its own, so these are
    /// the distinct stride-36 records actually present in the file.
    /// </summary>
    public static TheoryData<string, int, int, int> Specimens => new()
    {
        { "m_f_be1.msh.aya", 5_520, 203, 153 },
        { "m_f_be2.msh.aya", 6_588, 203, 153 },
        { "m_cockpit2.msh.aya", 745, 48, 16 },
    };

    [Theory]
    [MemberData(nameof(Specimens))]
    public void EachSpecimenCarriesTheMeasuredVertexDiffuseDistribution(
        string fileName,
        int expectedVertices,
        int expectedNonWhite,
        int expectedDark)
    {
        uint[] diffuse = ReadOwnedVertexDiffuse(fileName);

        Assert.Equal(expectedVertices, diffuse.Length);
        Assert.Equal(expectedNonWhite, diffuse.Count(color => (color & 0x00FFFFFFu) != 0x00FFFFFFu));
        Assert.Equal(
            expectedDark,
            diffuse.Count(color =>
                (color & 0x00FFFFFFu) != 0x00FFFFFFu &&
                Math.Max(Math.Max((color >> 16) & 0xFF, (color >> 8) & 0xFF), color & 0xFF) < 200));
    }

    /// <summary>
    /// Stage zero also runs <c>D3DTSS_ALPHAOP = MODULATE</c> against
    /// <c>D3DTA_DIFFUSE</c>, so a non-opaque dword would be a real alpha term.
    /// Every vertex of all three specimens is alpha 255, matching the
    /// 278,173-vertex retail corpus, and the loader refuses anything else
    /// rather than silently dropping it.
    /// </summary>
    [Theory]
    [MemberData(nameof(Specimens))]
    public void EveryVertexDiffuseAlphaIsOpaque(
        string fileName,
        int expectedVertices,
        int expectedNonWhite,
        int expectedDark)
    {
        _ = expectedVertices;
        _ = expectedNonWhite;
        _ = expectedDark;

        Assert.All(ReadOwnedVertexDiffuse(fileName), color => Assert.Equal(0xFFu, color >> 24));
    }

    /// <summary>
    /// The walker's 203 coloured vertices are six exact authored D3DCOLOR
    /// values, all neutral greys. Any drift here would mean the reader is
    /// taking the wrong bytes of the stride-36 record.
    /// </summary>
    [Fact]
    public void TheWalkerColouredVerticesAreTheExactAuthoredD3DColors()
    {
        Dictionary<uint, int> counts = ReadOwnedVertexDiffuse("m_f_be1.msh.aya")
            .Where(color => (color & 0x00FFFFFFu) != 0x00FFFFFFu)
            .GroupBy(color => color)
            .ToDictionary(group => group.Key, group => group.Count());

        Assert.Equal(
            new Dictionary<uint, int>
            {
                [0xFF6A6F75] = 66,
                [0xFFEDEDED] = 50,
                [0xFF363636] = 27,
                [0xFF888888] = 26,
                [0xFF0A0A0A] = 18,
                [0xFF050505] = 16,
            },
            counts);
    }

    [Fact]
    public void TheWalkerLoaderReadsTheDiffuseDwordAndBindsTheColorArray()
    {
        string loader = ReadGodotSource("RetailAquilaWalkerAsset.cs");

        Assert.Contains("colors[index] = ReadDiffuse(data, offset + 24);", loader);
        Assert.Contains("arrays[(int)Mesh.ArrayType.Color] = geometry.Colors;", loader);
        Assert.Contains(
            "throw new InvalidDataException(\"The retained Aquila walker has a non-opaque vertex diffuse alpha.\");",
            loader);

        // The walker, jet and cockpit all draw through the shared fixed-function
        // material, whose lit vertex colour is already modulated by COLOR.rgb.
        Assert.Contains("RetailFixedFunctionMaterial.Create(layers, terrain)", loader);
        Assert.Contains("vertex_light_color *= COLOR.rgb;", ReadGodotSource("Level100StaticWorldAsset.cs"));
    }

    /// <summary>
    /// Walks the inflated CMSH stream for group-zero <c>MMPT</c>/<c>IBUF</c>/
    /// <c>VBUF</c> triples and returns the DIFFUSE dword at offset 24 of every
    /// owned stride-36 record. The declared vertex bytes, index bytes,
    /// primitive count and active flag all have to agree before a run is
    /// accepted, and secondary groups declare a zero-length <c>VBUF</c> because
    /// they reuse the owner's stream.
    /// </summary>
    private static uint[] ReadOwnedVertexDiffuse(string fileName)
    {
        byte[] data = Inflate(File.ReadAllBytes(
            Path.Combine(LocateGodotDirectory(), SourceDirectory, fileName)));
        var diffuse = new List<uint>();
        int position = 0;
        while (position + 8 <= data.Length)
        {
            if (!Tag(data, position, "MMPT") ||
                BinaryPrimitives.ReadInt32LittleEndian(data.AsSpan(position + 4, 4)) != 24 ||
                position + 32 > data.Length)
            {
                position++;
                continue;
            }

            uint vertexBytes = BinaryPrimitives.ReadUInt32LittleEndian(data.AsSpan(position + 8, 4));
            uint indexBytes = BinaryPrimitives.ReadUInt32LittleEndian(data.AsSpan(position + 12, 4));
            uint indexCount = BinaryPrimitives.ReadUInt32LittleEndian(data.AsSpan(position + 16, 4));
            uint vertexCount = BinaryPrimitives.ReadUInt32LittleEndian(data.AsSpan(position + 20, 4));
            uint primitiveCount = BinaryPrimitives.ReadUInt32LittleEndian(data.AsSpan(position + 24, 4));
            uint active = BinaryPrimitives.ReadUInt32LittleEndian(data.AsSpan(position + 28, 4));
            int index = position + 32;
            if (active != 1 || indexCount < 3 || primitiveCount != indexCount - 2 ||
                indexBytes != indexCount * 2 || vertexBytes != vertexCount * 36 ||
                !Tag(data, index, "IBUF") ||
                BinaryPrimitives.ReadUInt32LittleEndian(data.AsSpan(index + 4, 4)) != indexBytes)
            {
                position++;
                continue;
            }

            int vertex = index + 8 + (int)indexBytes;
            if (vertex + 8 > data.Length || !Tag(data, vertex, "VBUF"))
            {
                position++;
                continue;
            }

            uint declared = BinaryPrimitives.ReadUInt32LittleEndian(data.AsSpan(vertex + 4, 4));
            int payload = vertex + 8;
            if (declared == vertexBytes && vertexBytes > 0 && payload + vertexBytes <= data.Length)
            {
                for (int record = 0; record < vertexCount; record++)
                {
                    diffuse.Add(BinaryPrimitives.ReadUInt32LittleEndian(
                        data.AsSpan(payload + (record * 36) + 24, 4)));
                }
            }
            position = payload + (int)declared;
        }
        return diffuse.ToArray();
    }

    private static bool Tag(byte[] data, int offset, string expected) =>
        offset >= 0 && offset + 4 <= data.Length &&
        Encoding.ASCII.GetString(data, offset, 4) == expected;

    private static byte[] Inflate(byte[] source)
    {
        using var output = new MemoryStream();
        int position = 0;
        while (position < source.Length)
        {
            int length = BinaryPrimitives.ReadInt32LittleEndian(source.AsSpan(position, 4));
            position += 4;
            using var compressed = new MemoryStream(source, position, length, writable: false);
            using (var inflater = new ZLibStream(compressed, CompressionMode.Decompress, leaveOpen: true))
            {
                inflater.CopyTo(output);
            }
            position += length;
        }
        return output.ToArray();
    }

    private static string ReadGodotSource(string fileName) =>
        File.ReadAllText(Path.Combine(LocateGodotDirectory(), fileName));

    private static string LocateGodotDirectory()
    {
        DirectoryInfo? directory = new(AppContext.BaseDirectory);
        while (directory is not null)
        {
            string candidate = Path.Combine(directory.FullName, "OnslaughtRebuild.Godot");
            if (Directory.Exists(Path.Combine(candidate, SourceDirectory)))
            {
                return candidate;
            }
            directory = directory.Parent;
        }
        throw new DirectoryNotFoundException(
            $"Could not locate OnslaughtRebuild.Godot/{SourceDirectory} above {AppContext.BaseDirectory}.");
    }
}
