// SPDX-License-Identifier: GPL-3.0-only
using System.Buffers.Binary;
using System.IO.Compression;

namespace OnslaughtToolkit.Companion.Assets;

/// <summary>
/// The game's <c>.aya</c> envelope (reverse-engineering/asset-formats/aya-container.md): one or more members, each a
/// little-endian u32 length followed by that many bytes of one zlib stream; the inflated members concatenate. Anything
/// else (a zero or overrunning length, a broken stream, output past the bound) is refused.
/// </summary>
public static class AyaContainer
{
    /// <summary>The largest inflated payload accepted; the biggest installed file inflates to about 8 MiB.</summary>
    public const int MaxInflated = 256 * 1024 * 1024;

    public static byte[] Inflate(ReadOnlySpan<byte> file, int maxInflated = MaxInflated)
    {
        using MemoryStream output = new();
        int position = 0;
        byte[] buffer = new byte[81920];
        while (position < file.Length)
        {
            if (file.Length - position < 4) throw new InvalidDataException("The file ends inside a member length.");
            uint length = BinaryPrimitives.ReadUInt32LittleEndian(file[position..]);
            position += 4;
            if (length == 0 || length > file.Length - position) throw new InvalidDataException("A member length runs past the file.");
            byte[] member = file.Slice(position, (int)length).ToArray();
            position += (int)length;
            using ZLibStream zlib = new(new MemoryStream(member), CompressionMode.Decompress);
            int read;
            while ((read = zlib.Read(buffer, 0, buffer.Length)) > 0)
            {
                if (output.Length + read > maxInflated) throw new InvalidDataException("The file inflates past the allowed size.");
                output.Write(buffer, 0, read);
            }
        }
        if (output.Length == 0) throw new InvalidDataException("The file holds no data.");
        return output.ToArray();
    }
}
