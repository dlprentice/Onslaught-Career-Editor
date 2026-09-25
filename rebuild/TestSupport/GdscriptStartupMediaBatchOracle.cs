// SPDX-License-Identifier: GPL-3.0-or-later
using System.Buffers.Binary;
using System.IO.Compression;
using System.Security.Cryptography;
using System.Text;
using OnslaughtRebuild.GodotClient;

namespace OnslaughtRebuild.TestSupport;

/// <summary>
/// Path observations plus tiny synthetic PNGs in a fresh child of an explicitly
/// supplied owned output directory. No cache, retail asset or research input is read.
/// </summary>
public static class GdscriptStartupMediaBatchOracle
{
    public static object Create(string outputRoot)
    {
        var paths = new List<object>();
        void Add(string? path)
        {
            object result;
            try { result = new { ok = true, value_units = Units(Path.GetFullPath(path!)) }; }
            catch (Exception error) { result = new { ok = false, error_type = error.GetType().Name }; }
            paths.Add(new { name = "path_" + paths.Count, path_units = path is null ? null : Units(path), result });
        }
        foreach (string? path in new string?[]
        {
            null, "", "\0", "a\0suffix", " ", "\t", ".", "..", "./", "../", "/", "//", "///",
            "/a//b/", "a/./b", "a/b/..", "a/b/../", "a/../b/.", "../../../../file", "/../../file",
            "literal\\name", "a\\..\\b", "//server/share", "C:foo", "C:\\foo\\..\\bar",
            "\\\\?\\C:\\foo\\..\\bar", "res://child", "user://child", "\uFEFFlead", "a/\uFEFFleaf",
            "\u2003", "..x/.foo", "a/.../b", "a/ .. /b", "\ud800", "\udfff", "a/\ud800/../b", "a/🚀/../é",
        }) Add(path);
        var random = new Random(0xBEA48);
        string[] pieces = ["a", "b", ".", "..", "", "literal\\part", " ", "é", "🚀"];
        for (int row = 0; row < 256; row++)
        {
            var segments = new List<string>();
            for (int index = 0, count = random.Next(1, 8); index < count; index++)
                segments.Add(pieces[random.Next(pieces.Length)]);
            Add((random.Next(3) == 0 ? "/" : "") + string.Join('/', segments) + (random.Next(3) == 0 ? "/" : ""));
        }
        var missing = RetailStartupMediaIndex.Load(null!, File.Exists);
        return new
        {
            schema = 1, platform = OperatingSystem.IsWindows() ? "Windows" : "Unix",
            current_directory_units = Units(Environment.CurrentDirectory), paths,
            playback = CreatePlaybackFixtures(outputRoot),
            empty_batch = new
            {
                schema = "onslaught-startup-verified-batch.v1", clips = new Dictionary<string, object>(),
                frame_paths = new Dictionary<string, object>(), audio = new Dictionary<string, object>(),
                splash_path = string.Empty, unavailable = missing.Unavailable,
            },
        };
    }

    private static object CreatePlaybackFixtures(string outputRoot)
    {
        if (!Path.IsPathFullyQualified(outputRoot) || !Directory.Exists(outputRoot))
            throw new ArgumentException("An existing fully qualified owned output directory is required.", nameof(outputRoot));
        if (!OperatingSystem.IsLinux())
            throw new PlatformNotSupportedException("The literal-backslash playback fixture requires the Linux host.");
        string owned = Path.Combine(outputRoot, "startup-playback-fixtures-" + Guid.NewGuid().ToString("n"));
        if (Directory.Exists(owned) || File.Exists(owned))
            throw new IOException("Refusing to reuse a startup playback fixture path.");
        Directory.CreateDirectory(owned);
        var files = new List<object>();
        void Write(string name, string relative, byte r, byte g, byte b)
        {
            string path = Path.Combine(owned, relative);
            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            byte[] bytes = Png(r, g, b);
            using (var output = new FileStream(path, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                output.Write(bytes);
            files.Add(new
            {
                name, path, bytes_hex = Convert.ToHexString(bytes),
                sha256 = Convert.ToHexString(SHA256.HashData(bytes)), rgba = new[] { (int)r, g, b, 255 },
            });
        }
        Write("literal_backslash_red", "literal\\pixel.png", 255, 0, 0);
        Write("normalized_alias_blue", "literal/pixel.png", 0, 0, 255);
        Write("regular_green", "regular.png", 0, 255, 0);
        return new { root = owned, files };
    }

    private static byte[] Png(byte r, byte g, byte b)
    {
        using var image = new MemoryStream();
        image.Write([137, 80, 78, 71, 13, 10, 26, 10]);
        void Chunk(string name, byte[] payload)
        {
            byte[] kind = Encoding.ASCII.GetBytes(name);
            Span<byte> word = stackalloc byte[4];
            BinaryPrimitives.WriteUInt32BigEndian(word, (uint)payload.Length);
            image.Write(word); image.Write(kind); image.Write(payload);
            uint crc = uint.MaxValue;
            foreach (byte value in kind.Concat(payload))
            {
                crc ^= value;
                for (int bit = 0; bit < 8; bit++)
                    crc = (crc >> 1) ^ ((crc & 1) != 0 ? 0xEDB88320u : 0u);
            }
            BinaryPrimitives.WriteUInt32BigEndian(word, ~crc);
            image.Write(word);
        }
        byte[] header = new byte[13];
        BinaryPrimitives.WriteUInt32BigEndian(header, 1);
        BinaryPrimitives.WriteUInt32BigEndian(header.AsSpan(4), 1);
        header[8] = 8; header[9] = 2; // 8-bit RGB, no interlace.
        Chunk("IHDR", header);
        using var compressed = new MemoryStream();
        using (var zlib = new ZLibStream(compressed, CompressionLevel.SmallestSize, leaveOpen: true))
            zlib.Write([0, r, g, b]); // One unfiltered row.
        Chunk("IDAT", compressed.ToArray());
        Chunk("IEND", []);
        return image.ToArray();
    }

    private static int[] Units(string text) => text.Select(unit => (int)unit).ToArray();
}
