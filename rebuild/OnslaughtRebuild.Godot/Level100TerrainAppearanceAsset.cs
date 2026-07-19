// SPDX-License-Identifier: GPL-3.0-or-later

using System.Buffers.Binary;
using Godot;

namespace OnslaughtRebuild.GodotClient;

internal static class Level100TerrainAppearanceAsset
{
    private const int MapSize = 512;
    private const int TileCountPerAxis = 64;
    private const int TileSize = 8;
    private const int MixerTextureWidth = 256;
    private const int MixerTextureCount = 6;
    private const int MixerTextureArea = MixerTextureWidth * MixerTextureWidth;
    private const int MixerPaletteStride = 256 * sizeof(uint);
    private const int MixerWeightCountPerLayer = 9 * 9;
    private const int MapTextureSourceLength = 399_468;
    private const int MixerMapSourceLength = 877_597;

    private static readonly uint MaptTag = Tag("MAPT");
    private static readonly uint CmtxTag = Tag("CMTX");
    private static readonly uint DataTag = Tag("DATA");
    private static readonly uint PaletteTag = Tag("PALT");
    private static readonly uint MixerMapTag = Tag("MMAP");
    private static readonly uint MixerCellTag = Tag("MCEL");
    private static readonly uint MixerCellRecordTag = Tag("CMCL");
    private static readonly uint MixerWeightsTag = Tag("MXRS");
    private static readonly uint MixerShadeTag = Tag("MSHD");

    public static Texture2D Load(
        string mapTextureResourcePath,
        string mixerMapResourcePath,
        Level100HeightFieldAsset heightField)
    {
        byte[] mapTexture = Godot.FileAccess.GetFileAsBytes(mapTextureResourcePath);
        byte[] mixerMap = Godot.FileAccess.GetFileAsBytes(mixerMapResourcePath);
        if (mapTexture.Length != MapTextureSourceLength ||
            mixerMap.Length != MixerMapSourceLength)
        {
            throw new InvalidDataException("Level 100 terrain appearance inputs have unexpected lengths.");
        }
        if (heightField.MixerSet != 10)
        {
            throw new InvalidDataException("Level 100 does not select the retained mixer set 10.");
        }

        MapTextureSlices textures = ParseMapTexture(mapTexture);
        MixerMapSlices mixer = ParseMixerMap(mixerMap);
        byte[] rgb = RenderLandscapeTexture(
            textures,
            mixer,
            heightField.SunColorRgb24,
            heightField.AmbientColorRgb24);

        Image image = Image.CreateFromData(MapSize, MapSize, false, Image.Format.Rgb8, rgb);
        if (image.IsEmpty())
        {
            throw new InvalidDataException("Godot could not create the Level 100 landscape texture.");
        }
        return ImageTexture.CreateFromImage(image);
    }

    private static MapTextureSlices ParseMapTexture(byte[] source)
    {
        RequireChunk(source, 0, MaptTag, MapTextureSourceLength - 8);
        const int cmtxHeaderOffset = 8;
        const int cmtxPayloadSize = 76;
        RequireChunk(source, cmtxHeaderOffset, CmtxTag, cmtxPayloadSize);

        const int cmtxPayloadOffset = cmtxHeaderOffset + 8;
        if (ReadUInt32(source, cmtxPayloadOffset) != 0xDEAD ||
            ReadUInt32(source, cmtxPayloadOffset + 8) != 0xDEAD ||
            ReadInt32(source, cmtxPayloadOffset + 0x10) != MixerTextureArea ||
            ReadInt32(source, cmtxPayloadOffset + 0x14) != MixerTextureCount ||
            ReadInt32(source, cmtxPayloadOffset + 0x18) != MixerTextureWidth)
        {
            throw new InvalidDataException("Level 100 MAPT metadata does not match mixer set 10.");
        }

        int dataHeaderOffset = cmtxPayloadOffset + cmtxPayloadSize;
        int dataSize = MixerTextureArea * MixerTextureCount;
        RequireChunk(source, dataHeaderOffset, DataTag, dataSize);
        int dataOffset = dataHeaderOffset + 8;

        int paletteHeaderOffset = dataOffset + dataSize;
        int paletteSize = MixerPaletteStride * MixerTextureCount;
        RequireChunk(source, paletteHeaderOffset, PaletteTag, paletteSize);
        int paletteOffset = paletteHeaderOffset + 8;
        if (paletteOffset + paletteSize != source.Length)
        {
            throw new InvalidDataException("Level 100 MAPT has trailing data.");
        }

        return new MapTextureSlices(source, dataOffset, paletteOffset);
    }

    private static MixerMapSlices ParseMixerMap(byte[] source)
    {
        RequireChunk(source, 0, MixerMapTag, MixerMapSourceLength - 8);
        var cells = new MixerCell[TileCountPerAxis * TileCountPerAxis];
        int position = 8;

        for (int cellIndex = 0; cellIndex < cells.Length; cellIndex++)
        {
            if (ReadUInt32(source, position) != MixerCellTag)
            {
                throw new InvalidDataException($"Level 100 MMAP is missing cell {cellIndex}.");
            }
            int cellPayloadSize = ReadInt32(source, position + 4);
            int cellPayloadOffset = position + 8;
            RequireChunk(source, cellPayloadOffset, MixerCellRecordTag, 20);
            int recordOffset = cellPayloadOffset + 8;
            int layerCount = ReadInt32(source, recordOffset);
            if (layerCount is < 1 or > 5 || ReadUInt32(source, recordOffset + 4) != 0xDEAD)
            {
                throw new InvalidDataException($"Level 100 MMAP cell {cellIndex} has invalid metadata.");
            }

            var materialIds = new byte[layerCount];
            for (int layer = 0; layer < layerCount; layer++)
            {
                ushort materialId = BinaryPrimitives.ReadUInt16LittleEndian(
                    source.AsSpan(recordOffset + 8 + (layer * sizeof(ushort)), sizeof(ushort)));
                if (materialId >= MixerTextureCount)
                {
                    throw new InvalidDataException(
                        $"Level 100 MMAP cell {cellIndex} selects unsupported material {materialId}.");
                }
                materialIds[layer] = checked((byte)materialId);
            }

            int weightsHeaderOffset = recordOffset + 20;
            int weightsSize = layerCount * MixerWeightCountPerLayer;
            RequireChunk(source, weightsHeaderOffset, MixerWeightsTag, weightsSize);
            int weightsOffset = weightsHeaderOffset + 8;
            if (cellPayloadSize != 36 + weightsSize)
            {
                throw new InvalidDataException($"Level 100 MMAP cell {cellIndex} has an invalid envelope.");
            }

            cells[cellIndex] = new MixerCell(materialIds, source.AsSpan(weightsOffset, weightsSize).ToArray());
            position += 8 + cellPayloadSize;
        }

        RequireChunk(source, position, MixerShadeTag, MapSize * MapSize);
        int shadeOffset = position + 8;
        if (shadeOffset + (MapSize * MapSize) != source.Length)
        {
            throw new InvalidDataException("Level 100 MMAP has trailing data.");
        }
        for (int index = shadeOffset; index < source.Length; index++)
        {
            if (source[index] > 63)
            {
                throw new InvalidDataException("Level 100 MMAP contains an invalid shade index.");
            }
        }

        return new MixerMapSlices(cells, source, shadeOffset);
    }

    private static byte[] RenderLandscapeTexture(
        MapTextureSlices textures,
        MixerMapSlices mixer,
        uint sunColor,
        uint ambientColor)
    {
        GradientEntry[] gradient = BuildLightingGradient(sunColor, ambientColor);
        var output = new byte[MapSize * MapSize * 3];

        for (int z = 0; z < MapSize; z++)
        {
            for (int x = 0; x < MapSize; x++)
            {
                int tileX = x / TileSize;
                int tileZ = z / TileSize;
                int localX = x % TileSize;
                int localZ = z % TileSize;
                int cellIndex = (tileX * TileCountPerAxis) + tileZ;
                MixerCell cell = mixer.Cells[cellIndex];

                int sourceX = localX + ((cellIndex & 1) != 0 ? TileSize : 0);
                int sourceZ = localZ + ((cellIndex & 0x40) != 0 ? TileSize : 0);
                int sourceTexel = (sourceX * MixerTextureWidth) + sourceZ;
                uint color = ReadPaletteColor(textures, 0, sourceTexel);

                for (int layer = 0; layer < cell.MaterialIds.Length; layer++)
                {
                    byte materialId = cell.MaterialIds[layer];
                    uint candidate = ReadPaletteColor(textures, materialId, sourceTexel);
                    int weight = unchecked((sbyte)cell.Weights[
                        (layer * MixerWeightCountPerLayer) + (localX * 9) + localZ]);
                    candidate = unchecked(candidate + (uint)(weight << 24));
                    int difference = unchecked((int)(candidate - color));
                    if (difference > 0x1FFFFFFF)
                    {
                        color = candidate;
                    }
                    else if (difference >= 0)
                    {
                        int blend = difference >> 26;
                        color = unchecked(
                            ((((color & 0x00F8F8FF) * (uint)(7 - blend)) +
                               ((candidate & 0x00F8F8FF) * (uint)blend)) >> 3) +
                            (candidate & 0xFF000000));
                    }
                }

                byte red = (byte)color;
                byte green = (byte)(color >> 8);
                byte blue = (byte)(color >> 16);
                byte shadeIndex = mixer.Source[mixer.ShadeOffset + (x * MapSize) + z];
                GradientEntry light = gradient[shadeIndex];
                uint rgb565 = (((uint)green * light.Green & 0x07E00000) +
                    ((uint)blue * light.Blue & 0x001F0000) +
                    ((uint)red * light.Red & 0xF8000000)) >> 16;

                int outputOffset = ((z * MapSize) + x) * 3;
                output[outputOffset] = (byte)((((rgb565 >> 11) & 0x1F) * 255) / 31);
                output[outputOffset + 1] = (byte)((((rgb565 >> 5) & 0x3F) * 255) / 63);
                output[outputOffset + 2] = (byte)(((rgb565 & 0x1F) * 255) / 31);
            }
        }

        return output;
    }

    private static GradientEntry[] BuildLightingGradient(uint sunColor, uint ambientColor)
    {
        int redBase = (int)(((ambientColor >> 16) & 0xFF) << 8) /
            ((int)((sunColor >> 16) & 0xFE) + 1);
        int greenBase = (int)(ambientColor & 0xFF00) /
            ((int)((sunColor >> 8) & 0xFE) + 1);
        int blueBase = (int)((ambientColor & 0xFF) << 8) /
            ((int)(sunColor & 0xFE) + 1);
        int redAccumulator = redBase << 8;
        int greenAccumulator = greenBase << 8;
        int blueAccumulator = blueBase << 8;
        var gradient = new GradientEntry[64];

        for (int index = 0; index < gradient.Length; index++)
        {
            uint red = (uint)((redAccumulator >> 8) << 16);
            uint green = (uint)((greenAccumulator >> 8) << 11);
            uint blue = (uint)(blueAccumulator >> 3) & 0xFFFFFFE0;
            red = Math.Min(red * 2, 0x00F80000) & 0x00F80000;
            green = Math.Min(green * 2, 0x0007E000) & 0x0007E000;
            blue = Math.Min(blue * 2, 0x00001F00) & 0x00001F00;
            gradient[index] = new GradientEntry(red, green, blue);

            redAccumulator += (255 - redBase) * 4;
            greenAccumulator += (255 - greenBase) * 4;
            blueAccumulator += (255 - blueBase) * 4;
        }

        return gradient;
    }

    private static uint ReadPaletteColor(MapTextureSlices textures, int materialId, int texel)
    {
        byte paletteIndex = textures.Source[
            textures.DataOffset + (materialId * MixerTextureArea) + texel];
        return ReadUInt32(
            textures.Source,
            textures.PaletteOffset + (materialId * MixerPaletteStride) + (paletteIndex * sizeof(uint)));
    }

    private static void RequireChunk(byte[] source, int offset, uint tag, int payloadSize)
    {
        if (offset < 0 ||
            offset + 8 > source.Length ||
            ReadUInt32(source, offset) != tag ||
            ReadInt32(source, offset + 4) != payloadSize ||
            payloadSize < 0 ||
            offset + 8 + payloadSize > source.Length)
        {
            throw new InvalidDataException("Level 100 terrain appearance has invalid chunk framing.");
        }
    }

    private static int ReadInt32(byte[] source, int offset)
    {
        return BinaryPrimitives.ReadInt32LittleEndian(source.AsSpan(offset, sizeof(int)));
    }

    private static uint ReadUInt32(byte[] source, int offset)
    {
        return BinaryPrimitives.ReadUInt32LittleEndian(source.AsSpan(offset, sizeof(uint)));
    }

    private static uint Tag(string value)
    {
        return (uint)value[0] |
            ((uint)value[1] << 8) |
            ((uint)value[2] << 16) |
            ((uint)value[3] << 24);
    }

    private readonly record struct MapTextureSlices(byte[] Source, int DataOffset, int PaletteOffset);

    private readonly record struct MixerMapSlices(MixerCell[] Cells, byte[] Source, int ShadeOffset);

    private readonly record struct MixerCell(byte[] MaterialIds, byte[] Weights);

    private readonly record struct GradientEntry(uint Red, uint Green, uint Blue);
}
