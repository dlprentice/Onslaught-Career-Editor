// SPDX-License-Identifier: GPL-3.0-or-later

using System.Buffers.Binary;
using System.IO.Compression;
using Godot;

namespace OnslaughtRebuild.GodotClient;

internal static class CuratedAyaTextureLoader
{
    internal enum Compression
    {
        Dxt1,
        Dxt2,
    }

    private const int MaximumSourceBytes = 2 * 1024 * 1024;
    private const int MaximumDdsBytes = 8 * 1024 * 1024;

    public static Texture2D Load(
        string resourcePath,
        int expectedWidth,
        int expectedHeight,
        Compression expectedCompression = Compression.Dxt2)
    {
        byte[] source = Godot.FileAccess.GetFileAsBytes(resourcePath);
        if (source.Length is 0 or > MaximumSourceBytes)
        {
            throw new InvalidDataException($"Curated texture '{resourcePath}' is missing or exceeds the source limit.");
        }

        byte[] dds = InflateAya(source);
        ReadOnlySpan<byte> expectedFourCc = expectedCompression == Compression.Dxt1
            ? "DXT1"u8
            : "DXT2"u8;
        if (dds.Length < 128 ||
            !dds.AsSpan(0, 4).SequenceEqual("DDS "u8) ||
            !dds.AsSpan(84, 4).SequenceEqual(expectedFourCc))
        {
            throw new InvalidDataException(
                $"Curated texture is not an AYA-wrapped {expectedCompression} DDS image.");
        }

        var image = new Image();
        Error result = image.LoadDdsFromBuffer(dds);
        if (result != Error.Ok || image.IsEmpty())
        {
            throw new InvalidDataException($"Godot could not decode curated texture '{resourcePath}' ({result}).");
        }
        if (image.GetWidth() != expectedWidth || image.GetHeight() != expectedHeight)
        {
            throw new InvalidDataException(
                $"Curated texture '{resourcePath}' decoded as {image.GetWidth()}x{image.GetHeight()}, " +
                $"expected {expectedWidth}x{expectedHeight}.");
        }

        return ImageTexture.CreateFromImage(image);
    }

    private static byte[] InflateAya(byte[] source)
    {
        using var output = new MemoryStream();
        int position = 0;
        int records = 0;
        byte[] buffer = new byte[16 * 1024];

        while (position < source.Length)
        {
            if (source.Length - position < sizeof(uint))
            {
                throw new InvalidDataException("Curated texture has a truncated AYA record header.");
            }

            uint declaredLength = BinaryPrimitives.ReadUInt32LittleEndian(source.AsSpan(position, sizeof(uint)));
            position += sizeof(uint);
            if (declaredLength is 0 or > int.MaxValue || declaredLength > source.Length - position)
            {
                throw new InvalidDataException("Curated texture has invalid AYA record framing.");
            }

            int compressedLength = checked((int)declaredLength);
            using var compressed = new MemoryStream(
                source,
                position,
                compressedLength,
                writable: false,
                publiclyVisible: false);
            using (var inflater = new ZLibStream(compressed, CompressionMode.Decompress, leaveOpen: true))
            {
                int read;
                while ((read = inflater.Read(buffer, 0, buffer.Length)) > 0)
                {
                    if (output.Length + read > MaximumDdsBytes)
                    {
                        throw new InvalidDataException("Curated texture exceeds the decoded DDS limit.");
                    }
                    output.Write(buffer, 0, read);
                }
            }

            if (compressed.Position != compressed.Length)
            {
                throw new InvalidDataException("Curated texture AYA record contains trailing compressed data.");
            }

            position += compressedLength;
            records++;
        }

        if (records == 0)
        {
            throw new InvalidDataException("Curated texture contains no AYA records.");
        }

        return output.ToArray();
    }
}
