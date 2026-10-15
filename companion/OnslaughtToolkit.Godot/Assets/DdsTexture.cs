// SPDX-License-Identifier: MIT
using System.Buffers.Binary;
using System.Text;

namespace OnslaughtToolkit.Companion.Assets;

/// <summary>
/// The top mip level of one of the game's textures, decoded to 8-bit RGBA rows (top row first). The installed textures
/// use four DDS pixel formats (reverse-engineering/asset-formats/dds-texture.md): DXT1, DXT2 (explicit 4-bit alpha,
/// colours left as stored), 16-bit A1R5G5B5 and 32-bit A8R8G8B8. Anything else is refused rather than guessed.
/// </summary>
public sealed record DdsImage(int Width, int Height, string Format, int MipLevels, byte[] Rgba)
{
    public bool HasTransparency
    {
        get
        {
            for (int i = 3; i < Rgba.Length; i += 4)
                if (Rgba[i] != 255) return true;
            return false;
        }
    }
}

public static class DdsTexture
{
    private const int HeaderSize = 128;

    public static DdsImage Decode(byte[] dds)
    {
        Require(dds.Length >= HeaderSize && Encoding.ASCII.GetString(dds, 0, 4) == "DDS " && U32(dds, 4) == 124, "not a DDS file");
        int height = (int)U32(dds, 12), width = (int)U32(dds, 16), mips = (int)Math.Max(1, U32(dds, 28));
        Require(width is > 0 and <= 8192 && height is > 0 and <= 8192, "image size out of range");
        uint flags = U32(dds, 80), bits = U32(dds, 88);
        string fourcc = Encoding.ASCII.GetString(dds, 84, 4);
        ReadOnlySpan<byte> data = dds.AsSpan(HeaderSize);
        byte[] rgba = new byte[width * height * 4];
        string format;
        if ((flags & 4) != 0 && fourcc is "DXT1")
        {
            format = "DXT1";
            Blocks(data, width, height, 8, rgba, (block, pixels) => Colors(block, pixels, dxt1: true));
        }
        else if ((flags & 4) != 0 && fourcc is "DXT2" or "DXT3")
        {
            format = fourcc;
            Blocks(data, width, height, 16, rgba, (block, pixels) =>
            {
                Colors(block[8..], pixels, dxt1: false);
                for (int p = 0; p < 16; p++)
                {
                    int nibble = (block[p / 2] >> (4 * (p & 1))) & 0xF;
                    pixels[4 * p + 3] = (byte)(nibble * 17);
                }
            });
        }
        else if ((flags & 0x40) != 0 && bits == 16 && Masks(dds) == (0x7C00, 0x3E0, 0x1F, 0x8000))
        {
            format = "A1R5G5B5";
            Require(data.Length >= width * height * 2, "the pixel data is shorter than the image");
            for (int i = 0; i < width * height; i++)
            {
                int v = BinaryPrimitives.ReadUInt16LittleEndian(data[(2 * i)..]);
                rgba[4 * i] = Expand5(v >> 10);
                rgba[4 * i + 1] = Expand5(v >> 5);
                rgba[4 * i + 2] = Expand5(v);
                rgba[4 * i + 3] = (v & 0x8000) != 0 ? (byte)255 : (byte)0;
            }
        }
        else if ((flags & 0x40) != 0 && bits == 32 && Masks(dds) == (0xFF0000, 0xFF00, 0xFF, 0xFF000000))
        {
            format = "A8R8G8B8";
            Require(data.Length >= width * height * 4, "the pixel data is shorter than the image");
            for (int i = 0; i < width * height; i++)
            {
                rgba[4 * i] = data[4 * i + 2];
                rgba[4 * i + 1] = data[4 * i + 1];
                rgba[4 * i + 2] = data[4 * i];
                rgba[4 * i + 3] = data[4 * i + 3];
            }
        }
        else
        {
            throw new InvalidDataException($"Not a supported texture: pixel format {(((flags & 4) != 0) ? fourcc : $"{bits}-bit RGB")}.");
        }
        return new DdsImage(width, height, format, mips, rgba);
    }

    private static void Blocks(ReadOnlySpan<byte> data, int width, int height, int blockBytes, byte[] rgba,
        BlockDecoder decode)
    {
        int across = (width + 3) / 4, down = (height + 3) / 4;
        Require(data.Length >= (long)across * down * blockBytes, "the block data is shorter than the image");
        byte[] pixels = new byte[64];
        for (int by = 0; by < down; by++)
            for (int bx = 0; bx < across; bx++)
            {
                Array.Clear(pixels);
                decode(data.Slice((by * across + bx) * blockBytes, blockBytes), pixels);
                for (int py = 0; py < 4; py++)
                    for (int px = 0; px < 4; px++)
                    {
                        int x = 4 * bx + px, y = 4 * by + py;
                        if (x < width && y < height) Array.Copy(pixels, 4 * (4 * py + px), rgba, 4 * (y * width + x), 4);
                    }
            }
    }

    private delegate void BlockDecoder(ReadOnlySpan<byte> block, byte[] pixels);

    /// <summary>A DXT colour block: two RGB565 endpoints, then sixteen 2-bit selectors.</summary>
    private static void Colors(ReadOnlySpan<byte> block, byte[] pixels, bool dxt1)
    {
        int c0 = BinaryPrimitives.ReadUInt16LittleEndian(block), c1 = BinaryPrimitives.ReadUInt16LittleEndian(block[2..]);
        Span<int> r = stackalloc int[4], g = stackalloc int[4], b = stackalloc int[4], a = stackalloc int[4];
        (r[0], g[0], b[0]) = Rgb565(c0);
        (r[1], g[1], b[1]) = Rgb565(c1);
        a[0] = a[1] = a[2] = a[3] = 255;
        if (!dxt1 || c0 > c1)
        {
            r[2] = (2 * r[0] + r[1]) / 3; g[2] = (2 * g[0] + g[1]) / 3; b[2] = (2 * b[0] + b[1]) / 3;
            r[3] = (r[0] + 2 * r[1]) / 3; g[3] = (g[0] + 2 * g[1]) / 3; b[3] = (b[0] + 2 * b[1]) / 3;
        }
        else
        {
            r[2] = (r[0] + r[1]) / 2; g[2] = (g[0] + g[1]) / 2; b[2] = (b[0] + b[1]) / 2;
            r[3] = g[3] = b[3] = 0;
            a[3] = 0;
        }
        uint selectors = BinaryPrimitives.ReadUInt32LittleEndian(block[4..]);
        for (int p = 0; p < 16; p++)
        {
            int s = (int)((selectors >> (2 * p)) & 3);
            pixels[4 * p] = (byte)r[s];
            pixels[4 * p + 1] = (byte)g[s];
            pixels[4 * p + 2] = (byte)b[s];
            pixels[4 * p + 3] = (byte)a[s];
        }
    }

    private static (int R, int G, int B) Rgb565(int c) =>
        (((c >> 11) & 31) * 255 / 31, ((c >> 5) & 63) * 255 / 63, (c & 31) * 255 / 31);

    private static byte Expand5(int v) => (byte)((v & 31) * 255 / 31);

    private static (uint, uint, uint, uint) Masks(byte[] d) => (U32(d, 92), U32(d, 96), U32(d, 100), U32(d, 104));

    private static uint U32(byte[] b, int o) => BinaryPrimitives.ReadUInt32LittleEndian(b.AsSpan(o));

    private static void Require(bool condition, string message)
    {
        if (!condition) throw new InvalidDataException("Not a supported texture: " + message + ".");
    }
}
