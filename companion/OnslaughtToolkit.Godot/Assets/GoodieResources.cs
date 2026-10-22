// SPDX-License-Identifier: GPL-3.0-only
using System.Buffers.Binary;
using System.Text;

namespace OnslaughtToolkit.Companion.Assets;

public enum GoodieKind { Image, Model, Video, Level }

/// <summary>
/// What a Goodie shows. <see cref="Files"/> are paths under <c>data/resources</c>. A model lists its backdrop texture
/// first, then its own textures, then its mesh. A video names the <c>data/video</c> file it plays; a level names
/// the race level it starts. <see cref="Missing"/> lists named files the install lacks.
/// </summary>
public sealed record GoodieContent(int Number, GoodieKind Kind, IReadOnlyList<string> Files, string? Video, int? Level,
    IReadOnlyList<string> Missing)
{
    public string? Image => Kind == GoodieKind.Image ? Files.FirstOrDefault() : null;
    public string? Mesh => Kind == GoodieKind.Model ? Files.LastOrDefault() : null;
}

/// <summary>
/// The Goodie archives (<c>data/resources/goodie_NN_res_PC.aya</c>), read as
/// reverse-engineering/asset-formats/goodie-resources.md describes them. Image and model Goodies name textures and a
/// mesh on the game's existing shelves; video and level Goodies are mapped from their number, as the game does.
/// Read-only.
/// </summary>
public static class GoodieResources
{
    private const int TextureRecord = 344, MeshReference = 309;

    private static readonly string[] Formats =
        ["UNKNOWN", "A1R5G5B5", "A4R4G4B4", "X8R8G8B8", "A8R8G8B8", "R5G6B5", "DXT1", "DXT2", "DXT4", "V8U8", "Q8W8V8U8"];

    /// <summary>The type the game gives a Goodie number.</summary>
    public static GoodieKind KindOf(int number) => number switch
    {
        <= 7 or 12 or 13 or 24 or 33 or 34 or 35 => GoodieKind.Image,
        <= 57 => GoodieKind.Model,
        <= 65 => GoodieKind.Image,
        <= 70 => GoodieKind.Level,
        <= 74 => GoodieKind.Image,
        75 or 77 or > 200 => GoodieKind.Video,
        76 => GoodieKind.Model,
        _ => GoodieKind.Image,
    };

    /// <summary>The video a video Goodie plays, under <c>data/video</c> with its <c>.vid</c> extension.</summary>
    public static string? VideoOf(int number) => number switch
    {
        >= 201 and <= 231 => $"cutscenes/{number - 200:D2}.vid",
        232 => "cutscenes/33.vid",
        75 => "GILL_M_on_a_fork.vid",
        77 => "UsTheMovie.vid",
        _ => null,
    };

    public static int? LevelOf(int number) => number is >= 66 and <= 70 ? 835 + number : null;

    public static string ArchiveName(int number) => $"goodie_{number:D2}_res_PC.aya";

    /// <summary>Reads what Goodie <paramref name="number"/> shows from the install at <paramref name="gameRoot"/>.</summary>
    public static GoodieContent Read(string gameRoot, int number)
    {
        GoodieKind kind = KindOf(number);
        string resources = Path.Combine(gameRoot, "data", "resources");
        if (kind == GoodieKind.Video)
        {
            string video = VideoOf(number)!;
            bool present = Resolve(Path.Combine(gameRoot, "data", "video"), video) is not null;
            return new GoodieContent(number, kind, [], video, null, present ? [] : ["video/" + video]);
        }
        if (kind == GoodieKind.Level) return new GoodieContent(number, kind, [], null, LevelOf(number), []);
        byte[] stream = AyaContainer.Inflate(File.ReadAllBytes(Path.Combine(resources, ArchiveName(number))));
        IReadOnlyList<string> files = Parse(stream, number, kind);
        return new GoodieContent(number, kind, files, null, null, files.Where(file => Resolve(resources, file) is null).ToList());
    }

    /// <summary>
    /// The file at <paramref name="relative"/> under <paramref name="folder"/>, matching each part of the path without regard to
    /// case as the game's own file system does (the game asks for <c>GILL_M_on_a_fork</c>; the install has
    /// <c>gill_m_on_a_fork.vid</c>). An exact match wins; null when there is none, or more than one that differ only in case.
    /// </summary>
    public static string? Resolve(string folder, string relative)
    {
        string current = folder;
        string[] parts = relative.Split('/', '\\');
        for (int i = 0; i < parts.Length; i++)
        {
            bool last = i == parts.Length - 1;
            string exact = Path.Combine(current, parts[i]);
            if (last ? File.Exists(exact) : Directory.Exists(exact))
            {
                current = exact;
                continue;
            }
            if (!Directory.Exists(current)) return null;
            string[] matches = (last ? Directory.GetFiles(current) : Directory.GetDirectories(current))
                .Where(entry => string.Equals(Path.GetFileName(entry), parts[i], StringComparison.OrdinalIgnoreCase)).ToArray();
            if (matches.Length != 1) return null;
            current = matches[0];
        }
        return current;
    }

    /// <summary>The files an image or model Goodie's inflated archive names, in order. Throws if the layout differs.</summary>
    public static IReadOnlyList<string> Parse(byte[] stream, int number, GoodieKind kind)
    {
        Chunks top = new(stream, 0, stream.Length);
        foreach (string tag in new[] { "LVLR", "TARG", "AYAD" }) top.Take(tag);
        Chunks gdie = top.Take("GDIE");
        top.Closed("the archive");
        Chunks gdat = gdie.Take("GDAT");
        gdie.Closed("GDIE");
        int stored = gdat.Int32(), type = gdat.Int32();
        if (stored != number || type != (int)kind)
            throw new InvalidDataException($"the archive is Goodie {stored} of type {type}, not Goodie {number} of type {(int)kind}");
        List<string> files = [];
        if (kind == GoodieKind.Image)
            files.Add(Texture(gdat));
        else
        {
            Chunks mdat = gdat.Take("MDAT");
            int count = mdat.Int32();
            mdat.Closed("MDAT");
            if (count is < 0 or > 64) throw new InvalidDataException($"the model names {count} textures");
            for (int i = 0; i < count; i++)
            {
                Chunks txtr = gdat.Take("TXTR");
                files.Add(Texture(txtr));
                txtr.Closed("TXTR");
            }
            Chunks mesh = gdat.Take("MESH");
            Chunks pmsh = mesh.Take("PMSH");
            mesh.Closed("MESH");
            Chunks pms2 = pmsh.Take("PMS2");
            pmsh.Closed("PMSH");
            byte[] reference = pms2.Bytes(MeshReference);
            pms2.Closed("PMS2");
            files.Add($"meshes/m_{Text(reference, 0, 300)}.aya");
        }
        gdat.Closed("GDAT");
        return files;
    }

    /// <summary>The shelf file for frame 0 of a texture reference, by the game's path rule.</summary>
    private static string Texture(Chunks parent)
    {
        Chunks dxtx = parent.Take("DXTX");
        Chunks record = dxtx.Take("CTEX");
        byte[] raw = record.Bytes(TextureRecord);
        record.Closed("CTEX");
        int frames = BinaryPrimitives.ReadInt32LittleEndian(raw.AsSpan(312));
        int format = BinaryPrimitives.ReadInt32LittleEndian(raw.AsSpan(324));
        if (frames is < 1 or > 16 || format < 0 || format >= Formats.Length)
            throw new InvalidDataException($"a texture has {frames} frames and format {format}");
        for (int frame = 0; frame < frames; frame++)
        {
            Chunks tfrm = dxtx.Take("TFRM");
            tfrm.Int32();
            tfrm.Closed("TFRM");
        }
        dxtx.Closed("DXTX");
        bool compressible = raw[340] != 0;
        string stem = $"{Text(raw, 8, 128).Replace('\\', '%')}(0){Formats[format]}";
        return compressible ? "dxtntextures/" + Cut(stem) : "textures/" + Cut("mustbe_" + stem);
    }

    /// <summary>The part after the folder is at most 65 characters; a longer one keeps 61 and ends in ".aya".</summary>
    private static string Cut(string stem) => stem.Length + 4 > 65 ? stem[..61] + ".aya" : stem + ".aya";

    private static string Text(byte[] bytes, int offset, int length)
    {
        int end = Array.IndexOf(bytes, (byte)0, offset, length);
        return Encoding.Latin1.GetString(bytes, offset, (end < 0 ? offset + length : end) - offset);
    }

    /// <summary>Nested chunks (tag, u32 size, payload), each checked to close exactly.</summary>
    private sealed class Chunks(byte[] data, int position, int end)
    {
        private int _position = position;

        public Chunks Take(string tag)
        {
            if (_position + 8 > end) throw new InvalidDataException($"{tag} is missing");
            string found = Encoding.ASCII.GetString(data, _position, 4);
            uint size = BinaryPrimitives.ReadUInt32LittleEndian(data.AsSpan(_position + 4));
            if (found != tag) throw new InvalidDataException($"expected {tag}, found {found}");
            int start = _position + 8;
            if (size > (uint)(end - start)) throw new InvalidDataException($"{tag} runs past its parent");
            _position = start + (int)size;
            return new Chunks(data, start, start + (int)size);
        }

        public byte[] Bytes(int count)
        {
            if (_position + count > end) throw new InvalidDataException("a record runs past its chunk");
            byte[] value = data.AsSpan(_position, count).ToArray();
            _position += count;
            return value;
        }

        public int Int32() => BinaryPrimitives.ReadInt32LittleEndian(Bytes(4));

        public void Closed(string what)
        {
            if (_position != end) throw new InvalidDataException($"{what} has {end - _position} unread bytes");
        }
    }
}
