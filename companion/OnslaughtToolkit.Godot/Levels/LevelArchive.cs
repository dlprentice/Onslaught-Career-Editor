// SPDX-License-Identifier: GPL-3.0-only
using System.Buffers.Binary;
using System.Globalization;
using System.IO.Compression;
using System.Text;
using System.Text.RegularExpressions;

namespace OnslaughtToolkit.Companion.Levels;

/// <summary>One level archive (<c>NNN_res_PC.aya</c>) of a game folder.</summary>
public sealed record LevelArchiveFile(int Level, string Path);

/// <summary>
/// The world bodies a level archive holds (<c>WRES</c>, <c>WRLD</c>: the base world <c>BSWD</c> and the level's own
/// world <c>RLWD</c>) and the two level numbers its <c>WDAT</c> chunk names. When the archive's WDAT does not name a
/// level, <c>CWorld::Load</c> reads that level's world from <c>data\worlds\worldNNN.wrd</c> instead of the archive, which is
/// the file a mod supplies.
/// </summary>
public sealed record LevelWorlds(int BaseLevel, int RealLevel, byte[]? BaseBody, byte[]? RealBody)
{
    /// <summary>The loose file <c>CWorld::Load</c> reads a level's world from (<c>world%03d.wrd</c>).</summary>
    public static string WorldFileName(int level) => $"data/worlds/world{level:D3}.wrd";
}

/// <summary>
/// Reads a level archive the way the Toolkit's reference does (<c>tools/world_resources_encode.py</c>: <c>read_members</c>,
/// <c>inflate</c>, <c>level_worlds</c>), with its bounds: a member's compressed bytes fit the game's pack buffer, a member
/// inflates to at most 1 MiB (the buffer the game reads blocks into) and a complete archive to at most 128 MiB. Read-only.
/// </summary>
public static class LevelArchive
{
    private const int MaxFileBytes = 64 << 20, MaxInflatedBytes = 128 << 20, MaxMembers = 4096;
    private const int PackBufferBytes = 0x102927, MaxMemberInflatedBytes = 1 << 20;

    private static readonly Regex ArchiveName = new("^([0-9]{3})_res_pc\\.aya$", RegexOptions.IgnoreCase | RegexOptions.CultureInvariant);

    /// <summary>The level archives in a game folder's <c>data/resources</c>, by level number; links are ignored.</summary>
    public static IReadOnlyList<LevelArchiveFile> List(string gameRoot)
    {
        string data = System.IO.Path.Combine(gameRoot, "data");
        if (!Directory.Exists(data)) return [];
        DirectoryInfo? resources = new DirectoryInfo(data).EnumerateDirectories()
            .FirstOrDefault(folder => string.Equals(folder.Name, "resources", StringComparison.OrdinalIgnoreCase));
        if (resources is null) return [];
        List<LevelArchiveFile> files = [];
        foreach (FileInfo file in resources.EnumerateFiles("*", new EnumerationOptions { IgnoreInaccessible = true })
                     .OrderBy(file => file.Name, StringComparer.Ordinal))
        {
            Match match = ArchiveName.Match(file.Name);
            if (!match.Success || file.LinkTarget is not null) continue;
            int level = int.Parse(match.Groups[1].Value, CultureInfo.InvariantCulture);
            files.RemoveAll(existing => existing.Level == level);  // two files of one number: the later name wins, as in the reference
            files.Add(new LevelArchiveFile(level, file.FullName));
        }
        return [.. files.OrderBy(file => file.Level)];
    }

    /// <summary>Reads one archive file (not a link, at most 64 MiB).</summary>
    /// <exception cref="InvalidDataException">The file is not a level archive with a world.</exception>
    public static LevelWorlds ReadFile(string path)
    {
        if (new FileInfo(path).LinkTarget is not null) throw new InvalidDataException("a level archive may not be a link");
        using FileStream stream = new(path, FileMode.Open, FileAccess.Read, FileShare.Read);
        if (stream.Length is 0 or > MaxFileBytes) throw new InvalidDataException("the archive is empty or larger than the compressed-byte limit");
        byte[] file = new byte[stream.Length];
        stream.ReadExactly(file);
        return Read(file);
    }

    /// <summary>The world bodies and level numbers of an archive's bytes.</summary>
    /// <exception cref="InvalidDataException">The bytes are not a level archive with a world.</exception>
    public static LevelWorlds Read(ReadOnlySpan<byte> file)
    {
        byte[] stream = Inflate(file);
        foreach ((string tag, int at, int size) in Chunks(stream, 0, stream.Length))
        {
            if (tag != "WRES") continue;
            foreach ((string worldTag, int worldAt, int worldSize) in Chunks(stream, at, at + size))
            {
                if (worldTag != "WRLD") continue;
                int? baseLevel = null, realLevel = null;
                byte[]? baseBody = null, realBody = null;
                foreach ((string kind, int kindAt, int kindSize) in Chunks(stream, worldAt, worldAt + worldSize))
                {
                    switch (kind)
                    {
                        case "WDAT":
                            if (kindSize < 8) throw new InvalidDataException("WDAT is shorter than its two level numbers");
                            baseLevel = BinaryPrimitives.ReadInt32LittleEndian(stream.AsSpan(kindAt));
                            realLevel = BinaryPrimitives.ReadInt32LittleEndian(stream.AsSpan(kindAt + 4));
                            break;
                        case "BSWD":
                            baseBody = stream.AsSpan(kindAt, kindSize).ToArray();
                            break;
                        case "RLWD":
                            realBody = stream.AsSpan(kindAt, kindSize).ToArray();
                            break;
                    }
                }
                if (baseLevel is null || realLevel is null) throw new InvalidDataException("the world has no WDAT chunk naming its levels");
                return new LevelWorlds(baseLevel.Value, realLevel.Value, baseBody, realBody);
            }
        }
        throw new InvalidDataException("no WRES/WRLD chunk");
    }

    /// <summary>The packed members of a <c>.aya</c> (a u32 length, then one zlib stream), inflated and joined.</summary>
    private static byte[] Inflate(ReadOnlySpan<byte> file)
    {
        if (file.IsEmpty || file.Length > MaxFileBytes) throw new InvalidDataException("the archive is empty or larger than the compressed-byte limit");
        using MemoryStream joined = new();
        int at = 0, members = 0;
        while (at < file.Length)
        {
            if (members++ >= MaxMembers) throw new InvalidDataException("the archive exceeds the member-count limit");
            if (file.Length - at < 4) throw new InvalidDataException("truncated .aya member header");
            uint size = BinaryPrimitives.ReadUInt32LittleEndian(file[at..]);
            if (size == 0 || size > PackBufferBytes || size > file.Length - at - 4)
                throw new InvalidDataException($"implausible .aya member length {size} at {at}");
            byte[] member = file.Slice(at + 4, (int)size).ToArray();
            at += 4 + (int)size;
            int limit = (int)Math.Min(MaxMemberInflatedBytes, MaxInflatedBytes - joined.Length);
            using MemoryStream compressed = new(member);
            using ZLibStream zlib = new(compressed, CompressionMode.Decompress);
            byte[] buffer = new byte[81920];
            int inflated = 0, read;
            uint adler = 1;
            try
            {
                while ((read = zlib.Read(buffer)) > 0)
                {
                    inflated += read;
                    if (inflated > limit) throw new InvalidDataException($"inflated archive/member limit at member {members - 1}");
                    adler = Adler32(adler, buffer.AsSpan(0, read));
                    joined.Write(buffer, 0, read);
                }
            }
            catch (InvalidDataException) when (inflated <= limit)
            {
                throw new InvalidDataException($"invalid zlib data in member {members - 1}");
            }
            // The stream reader accepts a stream that ends early and bytes after its end; a member is exactly one complete
            // zlib stream, which ends with the Adler-32 of what it inflates to.
            if (member.Length < 6 || BinaryPrimitives.ReadUInt32BigEndian(member.AsSpan(member.Length - 4)) != adler)
                throw new InvalidDataException($"truncated zlib stream, or data after it, in member {members - 1}");
        }
        return joined.ToArray();
    }

    private static uint Adler32(uint adler, ReadOnlySpan<byte> data)
    {
        uint a = adler & 0xFFFF, b = adler >> 16;
        while (!data.IsEmpty)
        {
            int block = Math.Min(data.Length, 5552);  // the most bytes whose sums fit 32 bits before the modulus
            foreach (byte x in data[..block])
            {
                a += x;
                b += a;
            }
            a %= 65521;
            b %= 65521;
            data = data[block..];
        }
        return (b << 16) | a;
    }

    /// <summary>(tag, payload offset, size) for each chunk of a tag stream; read lazily, as the game's chunk reader reads.</summary>
    private static IEnumerable<(string Tag, int Offset, int Size)> Chunks(byte[] data, int start, int end)
    {
        if (start < 0 || start > end || end > data.Length) throw new InvalidDataException("invalid chunk-stream boundaries");
        int at = start;
        while (at < end)
        {
            if (end - at < 8) throw new InvalidDataException($"truncated chunk header at {at}");
            string tag = Encoding.Latin1.GetString(data, at, 4);
            uint size = BinaryPrimitives.ReadUInt32LittleEndian(data.AsSpan(at + 4));
            if (size > end - at - 8) throw new InvalidDataException($"chunk {tag} at {at} overruns its parent");
            yield return (tag, at + 8, (int)size);
            at += 8 + (int)size;
        }
    }
}
