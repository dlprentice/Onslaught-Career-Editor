using System;
using System.IO;
using System.Linq;

namespace Onslaught___Career_Editor
{
    public static class PngHeaderReader
    {
        private static readonly byte[] PngSignature = [137, 80, 78, 71, 13, 10, 26, 10];

        public static PngHeaderInfo Read(string? path)
        {
            if (string.IsNullOrWhiteSpace(path) || !File.Exists(path))
            {
                return new PngHeaderInfo(false, null, null, 0, "PNG export is not available at the recorded local path.");
            }

            using FileStream stream = File.OpenRead(path);
            return Read(stream);
        }

        public static PngHeaderInfo Read(Stream stream)
        {
            ArgumentNullException.ThrowIfNull(stream);
            if (!stream.CanRead)
                throw new ArgumentException("PNG input stream must be readable.", nameof(stream));

            long byteSize = stream.CanSeek ? stream.Length : 0;
            if (byteSize > 0 && byteSize < 24)
            {
                return new PngHeaderInfo(false, null, null, byteSize, "PNG export is too small to inspect.");
            }

            if (stream.CanSeek)
                stream.Position = 0;

            Span<byte> header = stackalloc byte[24];
            int bytesRead = stream.Read(header);
            if (bytesRead < header.Length ||
                !header[..8].ToArray().SequenceEqual(PngSignature) ||
                !header[12..16].SequenceEqual("IHDR"u8))
            {
                return new PngHeaderInfo(false, null, null, byteSize, "Export exists, but it is not a readable PNG header.");
            }

            int width = ReadBigEndianInt32(header[16..20]);
            int height = ReadBigEndianInt32(header[20..24]);
            if (width <= 0 || height <= 0)
            {
                return new PngHeaderInfo(false, width, height, byteSize, "PNG header dimensions are invalid.");
            }

            return new PngHeaderInfo(true, width, height, byteSize, "PNG header read from the local export.");
        }

        private static int ReadBigEndianInt32(ReadOnlySpan<byte> bytes)
        {
            return (bytes[0] << 24) | (bytes[1] << 16) | (bytes[2] << 8) | bytes[3];
        }
    }

    public sealed record PngHeaderInfo(
        bool Readable,
        int? Width,
        int? Height,
        long ByteSize,
        string Status);
}
