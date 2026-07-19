// SPDX-License-Identifier: GPL-3.0-or-later

using System.Buffers.Binary;
using Godot;

namespace OnslaughtRebuild.GodotClient;

internal sealed class Level100HeightFieldAsset
{
    public const float PlayerStartX = 288.6875f;
    public const float PlayerStartZ = 243.25f;
    public const float PlayerStartElevation = -10f;

    private const int HfldPayloadSize = 668_652;
    private const int ChfdPayloadSize = 5_084;
    private const int HfdtPayloadSize = 663_552;
    private const int HeightScaleOffset = 0x102C;
    private const int MixerSetOffset = 0x1030;
    private const int FogColorOffset = 0x1078;
    private const int SunColorOffset = 0x107C;
    private const int AntiSunColorOffset = 0x1080;
    private const int AmbientColorOffset = 0x108C;
    private const int SkyCubeOffset = 0x1090;
    private const int DetailTextureOffset = 0x1094;
    private const int FogDensityOffset = 0x1098;
    private const int SunPositionOffset = 0x10A4;
    private const int TileCountPerAxis = 64;
    private const int TileWidth = 8;
    private const int SamplesPerTileAxis = 9;
    private const int SamplesPerTile = SamplesPerTileAxis * SamplesPerTileAxis;
    private const int MapExtent = TileCountPerAxis * TileWidth;
    private const int CoarseVertexCountPerAxis = TileCountPerAxis + 1;

    private static readonly uint HfldTag = Tag("HFLD");
    private static readonly uint ChfdTag = Tag("CHFD");
    private static readonly uint HfdtTag = Tag("HFDT");

    private readonly short[] _heightSamples;
    private readonly float _heightScale;

    private Level100HeightFieldAsset(
        short[] heightSamples,
        float heightScale,
        byte mixerSet,
        byte skyCube,
        byte detailTexture,
        uint fogColor,
        float fogDensity,
        uint sunColor,
        uint antiSunColor,
        uint ambientColor,
        Vector3 sunlightDirection)
    {
        _heightSamples = heightSamples;
        _heightScale = heightScale;
        MixerSet = mixerSet;
        SkyCube = skyCube;
        DetailTexture = detailTexture;
        FogColor = ToColor(fogColor);
        FogDensity = fogDensity;
        SunColor = ToColor(sunColor);
        AntiSunColor = ToColor(antiSunColor);
        AmbientColor = ToColor(ambientColor);
        SunColorRgb24 = sunColor;
        AmbientColorRgb24 = ambientColor;
        SunlightDirection = sunlightDirection;
        Mesh = BuildCoarseMesh();
    }

    public ArrayMesh Mesh { get; }

    public int VertexCount => CoarseVertexCountPerAxis * CoarseVertexCountPerAxis;

    public int TriangleCount => TileCountPerAxis * TileCountPerAxis * 2;

    public byte MixerSet { get; }

    public byte SkyCube { get; }

    public byte DetailTexture { get; }

    public Color FogColor { get; }

    public float FogDensity { get; }

    public Color SunColor { get; }

    public Color AntiSunColor { get; }

    public Color AmbientColor { get; }

    public uint SunColorRgb24 { get; }

    public uint AmbientColorRgb24 { get; }

    public Vector3 SunlightDirection { get; }

    public static Level100HeightFieldAsset Load(string resourcePath)
    {
        byte[] source = Godot.FileAccess.GetFileAsBytes(resourcePath);
        if (source.Length != HfldPayloadSize + 8 ||
            ReadUInt32(source, 0) != HfldTag ||
            ReadUInt32(source, 4) != HfldPayloadSize)
        {
            throw new InvalidDataException("Level 100 HFLD has an unexpected envelope.");
        }

        const int chfdHeaderOffset = 8;
        const int chfdPayloadOffset = chfdHeaderOffset + 8;
        if (ReadUInt32(source, chfdHeaderOffset) != ChfdTag ||
            ReadUInt32(source, chfdHeaderOffset + 4) != ChfdPayloadSize)
        {
            throw new InvalidDataException("Level 100 HFLD is missing its CHFD metadata.");
        }

        int hfdtHeaderOffset = chfdPayloadOffset + ChfdPayloadSize;
        int hfdtPayloadOffset = hfdtHeaderOffset + 8;
        if (ReadUInt32(source, hfdtHeaderOffset) != HfdtTag ||
            ReadUInt32(source, hfdtHeaderOffset + 4) != HfdtPayloadSize ||
            hfdtPayloadOffset + HfdtPayloadSize != source.Length)
        {
            throw new InvalidDataException("Level 100 HFLD is missing its exact HFDT sample block.");
        }

        int heightScaleBits = BinaryPrimitives.ReadInt32LittleEndian(
            source.AsSpan(chfdPayloadOffset + HeightScaleOffset, sizeof(int)));
        float heightScale = BitConverter.Int32BitsToSingle(heightScaleBits);
        if (!float.IsFinite(heightScale) || heightScale <= 0f)
        {
            throw new InvalidDataException("Level 100 HFLD has an invalid height scale.");
        }

        byte mixerSet = source[chfdPayloadOffset + MixerSetOffset];
        byte skyCube = source[chfdPayloadOffset + SkyCubeOffset];
        byte detailTexture = source[chfdPayloadOffset + DetailTextureOffset];
        float fogDensity = ReadSingle(source, chfdPayloadOffset + FogDensityOffset);
        if (!float.IsFinite(fogDensity) || fogDensity < 0f)
        {
            throw new InvalidDataException("Level 100 HFLD has an invalid fog density.");
        }

        Vector3 beaSunPosition = new(
            ReadSingle(source, chfdPayloadOffset + SunPositionOffset),
            ReadSingle(source, chfdPayloadOffset + SunPositionOffset + sizeof(float)),
            ReadSingle(source, chfdPayloadOffset + SunPositionOffset + (sizeof(float) * 2)));
        if (!beaSunPosition.IsFinite() || beaSunPosition.IsZeroApprox())
        {
            throw new InvalidDataException("Level 100 HFLD has an invalid sun direction.");
        }
        Vector3 beaLightDirection = -beaSunPosition.Normalized();
        Vector3 sunlightDirection = new(
            beaLightDirection.X,
            -beaLightDirection.Z,
            -beaLightDirection.Y);

        var samples = new short[HfdtPayloadSize / sizeof(short)];
        for (int index = 0; index < samples.Length; index++)
        {
            samples[index] = BinaryPrimitives.ReadInt16LittleEndian(
                source.AsSpan(hfdtPayloadOffset + (index * sizeof(short)), sizeof(short)));
        }

        return new Level100HeightFieldAsset(
            samples,
            heightScale,
            mixerSet,
            skyCube,
            detailTexture,
            ReadUInt32(source, chfdPayloadOffset + FogColorOffset),
            fogDensity,
            ReadUInt32(source, chfdPayloadOffset + SunColorOffset),
            ReadUInt32(source, chfdPayloadOffset + AntiSunColorOffset),
            ReadUInt32(source, chfdPayloadOffset + AmbientColorOffset),
            sunlightDirection);
    }

    public float SampleRelativeHeight(float relativeX, float relativeZ)
    {
        return PlayerStartElevation -
            SampleRetailHeight(relativeX + PlayerStartX, relativeZ + PlayerStartZ);
    }

    private ArrayMesh BuildCoarseMesh()
    {
        var vertices = new Vector3[VertexCount];
        var normals = new Vector3[VertexCount];
        var textureCoordinates = new Vector2[VertexCount];
        var indices = new int[TriangleCount * 3];

        int vertexIndex = 0;
        for (int z = 0; z <= MapExtent; z += TileWidth)
        {
            for (int x = 0; x <= MapExtent; x += TileWidth)
            {
                float height = PlayerStartElevation - SampleRetailHeight(x, z);
                vertices[vertexIndex] = new Vector3(x - PlayerStartX, height, PlayerStartZ - z);

                float left = SampleRetailHeight(Math.Max(0, x - TileWidth), z);
                float right = SampleRetailHeight(Math.Min(MapExtent, x + TileWidth), z);
                float back = SampleRetailHeight(x, Math.Max(0, z - TileWidth));
                float forward = SampleRetailHeight(x, Math.Min(MapExtent, z + TileWidth));
                normals[vertexIndex] = new Vector3(
                    right - left,
                    TileWidth * 2f,
                    back - forward).Normalized();
                textureCoordinates[vertexIndex] = new Vector2(
                    x / (float)MapExtent,
                    z / (float)MapExtent);
                vertexIndex++;
            }
        }

        int index = 0;
        for (int z = 0; z < TileCountPerAxis; z++)
        {
            for (int x = 0; x < TileCountPerAxis; x++)
            {
                int topLeft = (z * CoarseVertexCountPerAxis) + x;
                int bottomLeft = topLeft + CoarseVertexCountPerAxis;
                indices[index++] = topLeft;
                indices[index++] = bottomLeft;
                indices[index++] = topLeft + 1;
                indices[index++] = topLeft + 1;
                indices[index++] = bottomLeft;
                indices[index++] = bottomLeft + 1;
            }
        }

        var arrays = new Godot.Collections.Array();
        arrays.Resize((int)Godot.Mesh.ArrayType.Max);
        arrays[(int)Godot.Mesh.ArrayType.Vertex] = vertices;
        arrays[(int)Godot.Mesh.ArrayType.Normal] = normals;
        arrays[(int)Godot.Mesh.ArrayType.TexUV] = textureCoordinates;
        arrays[(int)Godot.Mesh.ArrayType.Index] = indices;

        var mesh = new ArrayMesh();
        mesh.AddSurfaceFromArrays(Godot.Mesh.PrimitiveType.Triangles, arrays);
        return mesh;
    }

    private float SampleRetailHeight(float x, float z)
    {
        float clampedX = Math.Clamp(x, 0f, MapExtent);
        float clampedZ = Math.Clamp(z, 0f, MapExtent);
        int x0 = (int)MathF.Floor(clampedX);
        int z0 = (int)MathF.Floor(clampedZ);
        int x1 = Math.Min(x0 + 1, MapExtent);
        int z1 = Math.Min(z0 + 1, MapExtent);
        float fractionX = clampedX - x0;
        float fractionZ = clampedZ - z0;

        float near = Mathf.Lerp(SampleIntegerHeight(x0, z0), SampleIntegerHeight(x1, z0), fractionX);
        float far = Mathf.Lerp(SampleIntegerHeight(x0, z1), SampleIntegerHeight(x1, z1), fractionX);
        return Mathf.Lerp(near, far, fractionZ);
    }

    private float SampleIntegerHeight(int x, int z)
    {
        int tileX = Math.Min(x / TileWidth, TileCountPerAxis - 1);
        int tileZ = Math.Min(z / TileWidth, TileCountPerAxis - 1);
        int localX = x == MapExtent ? TileWidth : x % TileWidth;
        int localZ = z == MapExtent ? TileWidth : z % TileWidth;
        int sampleIndex =
            (((tileX * TileCountPerAxis) + tileZ) * SamplesPerTile) +
            (localZ * SamplesPerTileAxis) +
            localX;
        return _heightSamples[sampleIndex] * _heightScale;
    }

    private static uint ReadUInt32(byte[] source, int offset)
    {
        if (offset < 0 || offset + sizeof(uint) > source.Length)
        {
            throw new InvalidDataException("Level 100 HFLD ended unexpectedly.");
        }

        return BinaryPrimitives.ReadUInt32LittleEndian(source.AsSpan(offset, sizeof(uint)));
    }

    private static float ReadSingle(byte[] source, int offset)
    {
        return BitConverter.Int32BitsToSingle(
            BinaryPrimitives.ReadInt32LittleEndian(source.AsSpan(offset, sizeof(float))));
    }

    private static Color ToColor(uint rgb)
    {
        return new Color(
            ((rgb >> 16) & 0xFF) / 255f,
            ((rgb >> 8) & 0xFF) / 255f,
            (rgb & 0xFF) / 255f);
    }

    private static uint Tag(string value)
    {
        return (uint)value[0] |
            ((uint)value[1] << 8) |
            ((uint)value[2] << 16) |
            ((uint)value[3] << 24);
    }
}
