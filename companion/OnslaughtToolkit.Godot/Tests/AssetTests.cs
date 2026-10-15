// SPDX-License-Identifier: MIT
using System.Buffers.Binary;
using System.IO.Compression;
using Vector3 = System.Numerics.Vector3;
using System.Text;
using Godot;
using OnslaughtToolkit.Companion.Assets;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// The asset readers and exporters on small synthetic inputs built here (no game bytes): the AYA envelope, the CMSH
/// grammar and key composition, DDS decoding, glTF output Godot can read back, and exports that never replace a file
/// or land in a protected folder.
/// </summary>
internal static class AssetTests
{
    internal static void Run(string outputDirectory, Checks check)
    {
        check.Suite("assets");
        Aya(check);
        Cmsh(check);
        Dds(check);
        Exports(Path.Combine(outputDirectory, "asset-exports"), check);
        Animation(check);
        Sounds(check);
        Goodies(Path.Combine(outputDirectory, "asset-goodies"), check);
    }

    /// <summary>A Goodie archive's inflated stream: the resource prefix, then GDIE and GDAT around the content.</summary>
    internal static byte[] GoodieStream(int number, GoodieKind kind, byte[] content) =>
        [.. Chunk("LVLR", Ints(103)), .. Chunk("TARG", Ints(1)), .. Chunk("AYAD", new byte[24]),
         .. Chunk("GDIE", Chunk("GDAT", [.. Ints(number, (int)kind), .. content]))];

    /// <summary>A texture reference: the 344-byte record (name, size, one frame, A8R8G8B8, compressible) and its TFRM.</summary>
    internal static byte[] GoodieTexture(string name)
    {
        byte[] record = Record(344, new() { [172] = 4, [176] = 4, [312] = 1, [324] = 4 });
        Encoding.ASCII.GetBytes(name).CopyTo(record, 8);
        record[340] = 1;
        return Chunk("DXTX", [.. Chunk("CTEX", record), .. Chunk("TFRM", Ints(1))]);
    }

    internal static byte[] GoodieModel(int number, string backdrop, string[] textures, string mesh)
    {
        byte[] reference = new byte[309];
        Encoding.ASCII.GetBytes(mesh).CopyTo(reference, 0);
        BinaryPrimitives.WriteInt32LittleEndian(reference.AsSpan(300), 10002);
        byte[] names = [.. new[] { backdrop }.Concat(textures).SelectMany(name => Chunk("TXTR", GoodieTexture(name)))];
        return GoodieStream(number, GoodieKind.Model,
            [.. Chunk("MDAT", Ints(textures.Length + 1)), .. names, .. Chunk("MESH", Chunk("PMSH", Chunk("PMS2", reference)))]);
    }

    /// <summary>
    /// Puts a synthetic model, a texture and Goodie archives into a game folder: picture Goodies 000–007 and model
    /// Goodie 008, all naming those two files.
    /// </summary>
    internal static void WriteGoodies(string gameRoot)
    {
        string resources = Path.Combine(gameRoot, "data", "resources");
        Directory.CreateDirectory(Path.Combine(resources, "meshes"));
        Directory.CreateDirectory(Path.Combine(resources, "dxtntextures"));
        File.WriteAllBytes(Path.Combine(resources, "meshes", "m_testmodel.msh.aya"), Member(TwoPartMesh()));
        File.WriteAllBytes(Path.Combine(resources, "dxtntextures", "meshtex%test.tga(0)A8R8G8B8.aya"), Member(Dxt1Texture()));
        for (int number = 0; number < 8; number++)
            File.WriteAllBytes(Path.Combine(resources, GoodieResources.ArchiveName(number)),
                Member(GoodieStream(number, GoodieKind.Image, GoodieTexture("meshtex\\test.tga"))));
        File.WriteAllBytes(Path.Combine(resources, GoodieResources.ArchiveName(8)),
            Member(GoodieModel(8, "meshtex\\test.tga", ["meshtex\\test.tga"], "testmodel.msh")));
    }

    private static void Goodies(string root, Checks check)
    {
        check.That(GoodieResources.Parse(GoodieStream(3, GoodieKind.Image, GoodieTexture("goodies\\ca_x.tga")), 3, GoodieKind.Image)
            .SequenceEqual(["dxtntextures/goodies%ca_x.tga(0)A8R8G8B8.aya"]), "an image Goodie names its picture on the texture shelf");
        check.That(GoodieResources.Parse(GoodieModel(8, "goodies\\bg.tga", ["meshtex\\a.tga"], "f_be1.msh"), 8, GoodieKind.Model)
            .SequenceEqual(["dxtntextures/goodies%bg.tga(0)A8R8G8B8.aya", "dxtntextures/meshtex%a.tga(0)A8R8G8B8.aya", "meshes/m_f_be1.msh.aya"]),
            "a model Goodie names its backdrop, its textures and its mesh");
        string longName = "goodies\\" + new string('x', 70) + ".tga";
        string cut = GoodieResources.Parse(GoodieStream(3, GoodieKind.Image, GoodieTexture(longName)), 3, GoodieKind.Image)[0];
        check.That(cut.Length == "dxtntextures/".Length + 65 && cut.EndsWith("x.aya", StringComparison.Ordinal),
            "a long texture file name is cut to 65 characters as the game cuts it");
        check.That(Throws(() => GoodieResources.Parse(GoodieStream(4, GoodieKind.Image, GoodieTexture("x")), 3, GoodieKind.Image)) &&
            Throws(() => GoodieResources.Parse([.. GoodieStream(3, GoodieKind.Image, GoodieTexture("x")), 0], 3, GoodieKind.Image)),
            "an archive for another Goodie, or with bytes left over, is refused");
        check.That(GoodieResources.KindOf(0) == GoodieKind.Image && GoodieResources.KindOf(12) == GoodieKind.Image &&
            GoodieResources.KindOf(8) == GoodieKind.Model && GoodieResources.KindOf(76) == GoodieKind.Model &&
            GoodieResources.KindOf(66) == GoodieKind.Level && GoodieResources.KindOf(75) == GoodieKind.Video &&
            GoodieResources.KindOf(200) == GoodieKind.Image && GoodieResources.KindOf(232) == GoodieKind.Video,
            "Goodie types follow the game's number rule");
        check.That(GoodieResources.VideoOf(205) == "cutscenes/05.vid" && GoodieResources.VideoOf(232) == "cutscenes/33.vid" &&
            GoodieResources.LevelOf(66) == 901 && GoodieResources.LevelOf(70) == 905, "videos and race levels follow the Goodie number");
        WriteGoodies(root);
        GoodieContent model = GoodieResources.Read(root, 8);
        GoodieContent video = GoodieResources.Read(root, 228);
        check.That(model.Missing.Count == 0 && model.Mesh == "meshes/m_testmodel.msh.aya" && video.Missing.SequenceEqual(["video/cutscenes/28.vid"]),
            "a Goodie's files resolve in the install, and a missing video is reported");
        Directory.CreateDirectory(Path.Combine(root, "data", "video"));
        File.WriteAllBytes(Path.Combine(root, "data", "video", "gill_m_on_a_fork.vid"), [0x42]);
        check.That(GoodieResources.Read(root, 75).Missing.Count == 0 &&
            GoodieResources.Resolve(Path.Combine(root, "data"), "VIDEO/GILL_M_on_a_fork.vid") == Path.Combine(root, "data", "video", "gill_m_on_a_fork.vid"),
            "names match the install without regard to case, as the game's file system matches them");
    }

    /// <summary>A synthetic two-sample bank: one 2-sample beep (codes 4 and 0) and one silent sample.</summary>
    internal static byte[] SoundBank()
    {
        List<byte> bank = [.. Encoding.ASCII.GetBytes("PCXP"), .. BitConverter.GetBytes(2)];
        foreach ((string name, int bytes, byte[] packed) in new[] { ("Hud\\beep", 4, new byte[] { 0x40 }), ("Hud\\quiet", 8, new byte[] { 0, 0 }) })
            bank.AddRange([.. Encoding.ASCII.GetBytes("PSMP"), .. Encoding.ASCII.GetBytes(name.PadRight(64, '\0')), .. BitConverter.GetBytes(bytes), .. packed]);
        return [.. bank];
    }

    private static void Sounds(Checks check)
    {
        IReadOnlyList<XapSample> samples = XapBank.Read(SoundBank());
        check.That(samples.Count == 2 && samples[0].Name == "Hud\\beep" && samples[1].PcmBytes == 8, "A sound bank reads its samples by name.");
        check.That(XapBank.Decode(samples[0]).SequenceEqual(new short[] { 7, 8 }), "Bank samples decode as IMA ADPCM, high nibble first.");
        byte[] wav = XapBank.Wav([7, 8]);
        check.That(wav.Length == 48 && Encoding.ASCII.GetString(wav, 0, 4) == "RIFF" && BinaryPrimitives.ReadInt32LittleEndian(wav.AsSpan(24)) == 44100 &&
            BinaryPrimitives.ReadInt16LittleEndian(wav.AsSpan(44)) == 7, "A WAV copy is 16-bit mono at 44,100 Hz.");
        check.That(Throws(() => XapBank.Read([.. SoundBank(), 0])), "A bank with bytes after its last sample is refused.");
    }

    /// <summary>A part with two keys and one mode exports one animation whose samples are the keys, timed by the mode's rate.</summary>
    private static void Animation(Checks check)
    {
        CmshMesh mesh = CmshReader.Read(TwoPartMesh(animated: true))[0];
        byte[] glb = GltfExport.Write(mesh, _ => null, _ => []);
        GltfDocument document = new();
        GltfState state = new();
        bool read = document.AppendFromBuffer(glb, "", state) == Error.Ok;
        check.That(read && state.GetAnimations().Count == 1, "A mode whose keys move exports one animation Godot reads.");
        string json = Encoding.UTF8.GetString(glb, 20, BinaryPrimitives.ReadInt32LittleEndian(glb.AsSpan(12)));
        check.That(json.Contains("\"startFrame\":0") && json.Contains("\"frameScaler\":1") && json.Contains("\"name\":\"wave\""),
            "The animation keeps the mode's name and records its frames.");
        check.That(Math.Abs(GltfExport.Duration(mesh.Modes[0]) - 1f) < 1e-6f, "A mode's duration is 1 / (20 × rate) seconds.");

        // A reflected key becomes a rotation with a scale of -1 on Z, and the two rebuild the reflected axes.
        MeshBasis mirror = new(new Vector3(-1, 0, 0), Vector3.UnitY, Vector3.UnitZ);
        (Vector3 t, System.Numerics.Quaternion r, Vector3 scale) = GltfExport.Trs(new PartTransform(mirror, Vector3.Zero));
        Vector3 x = Vector3.Transform(Vector3.UnitX * scale.X, r), z = Vector3.Transform(Vector3.UnitZ * scale.Z, r);
        Vector3 wantX = GltfExport.Convert(mirror.Apply(GltfExport.Back(Vector3.UnitX))), wantZ = GltfExport.Convert(mirror.Apply(GltfExport.Back(Vector3.UnitZ)));
        check.That(scale == new Vector3(1, 1, -1) && t == Vector3.Zero && Vector3.Distance(x, wantX) < 1e-5f && Vector3.Distance(z, wantZ) < 1e-5f,
            "A reflected key exports as a rotation and a negative scale that rebuild it exactly.");
    }

    private static void Aya(Checks check)
    {
        byte[] payload = Encoding.ASCII.GetBytes("CMSH and some more bytes to compress");
        byte[] file = [.. Member(payload[..10]), .. Member(payload[10..])];
        check.That(AyaContainer.Inflate(file).AsSpan().SequenceEqual(payload), "AYA members inflate and concatenate in order.");
        byte[] truncated = file[..^3];
        check.That(Throws(() => AyaContainer.Inflate(truncated)), "A member that runs past the file is refused.");
        check.That(Throws(() => AyaContainer.Inflate(new byte[] { 0, 0, 0, 0 })), "A zero-length member is refused.");
        check.That(Throws(() => AyaContainer.Inflate(file, maxInflated: 8)), "Output past the bound is refused.");
    }

    private static void Cmsh(Checks check)
    {
        IReadOnlyList<CmshMesh> meshes = CmshReader.Read(TwoPartMesh());
        CmshMesh mesh = meshes[0];
        check.That(meshes.Count == 1 && mesh.Parts.Count == 2 && mesh.Parts[1].Parent == 0, "A synthetic two-part mesh reads with its hierarchy.");
        PartTransform child = mesh.ModelSpace(1, 0);
        check.That(Vector3.Distance(child.Position, new Vector3(-1, 0, 0)) < 1e-6f,
            "A child's model-space position is the parent's plus the parent's rotation applied to its key.");
        int[] triangles = mesh.Parts[0].Triangles().Single().Triangles;
        check.That(triangles.SequenceEqual(new[] { 0, 1, 2, 2, 1, 3 }), "Strip triangles alternate winding and keep every face.");
        byte[] stream = TwoPartMesh();
        check.That(Throws(() => CmshReader.Read([.. stream, 0, 0, 0, 0, 0, 0, 0, 0])), "Bytes after the grammar's end are refused.");
        check.That(Throws(() => CmshReader.Read(stream[..^4])), "A truncated stream is refused.");
        byte[] wrongTag = stream.ToArray();
        int hori = IndexOf(wrongTag, "HORI");
        wrongTag[hori] = (byte)'X';
        check.That(Throws(() => CmshReader.Read(wrongTag)), "An unexpected tag in the checked orientation slot is refused.");
    }

    /// <summary>One 4×4 DXT1 block: endpoints white and black, selectors 0, 1, 2, 3 repeating.</summary>
    internal static byte[] Dxt1Texture() => [.. Header(4, 4, "DXT1", 0, [0, 0, 0, 0]), 0xFF, 0xFF, 0x00, 0x00, 0xE4, 0xE4, 0xE4, 0xE4];

    private static void Dds(Checks check)
    {
        DdsImage image = DdsTexture.Decode(Dxt1Texture());
        check.That(image is { Width: 4, Height: 4, Format: "DXT1" } && image.Rgba[0] == 255 && image.Rgba[4] == 0 && image.Rgba[8] == 170 &&
            image.Rgba[12] == 85 && !image.HasTransparency, "A DXT1 block decodes to its four interpolated colours.");
        byte[] a1r5g5b5 = [.. Header(2, 1, "", 16, [0x7C00, 0x3E0, 0x1F, 0x8000]), 0x00, 0xFC, 0x1F, 0x00];
        DdsImage pixels = DdsTexture.Decode(a1r5g5b5);
        check.That(pixels.Rgba.AsSpan(0, 8).SequenceEqual(new byte[] { 255, 0, 0, 255, 0, 0, 255, 0 }),
            "A1R5G5B5 pixels decode with their one-bit alpha.");
        check.That(Throws(() => DdsTexture.Decode(Header(4, 4, "DXT5", 0, [0, 0, 0, 0]))), "An unsupported pixel format is refused.");
    }

    private static void Exports(string root, Checks check)
    {
        string game = Path.Combine(root, "game"), backups = Path.Combine(root, "backups"), chosen = Path.Combine(root, "chosen");
        foreach (string folder in new[] { game, backups, chosen }) Directory.CreateDirectory(folder);
        string[] guarded = [game, backups];
        byte[] glb = GltfExport.Write(CmshReader.Read(TwoPartMesh())[0], _ => null, _ => []);
        GltfDocument document = new();
        GltfState state = new();
        bool read = document.AppendFromBuffer(glb, "", state) == Error.Ok;
        Node? scene = read ? document.GenerateScene(state) : null;
        check.That(scene is not null && state.GetNodes().Count == 2, "The glTF export reads back in Godot with one node per part.");
        scene?.Free();

        ExportReceipt saved = ExportFiles.Write(chosen, "two.glb", glb, guarded);
        check.That(saved.Ok && File.ReadAllBytes(Path.Combine(chosen, "two.glb")).AsSpan().SequenceEqual(glb), "An export is written and read back.");
        ExportReceipt again = ExportFiles.Write(chosen, "two.glb", [1, 2, 3], guarded);
        check.That(!again.Ok && File.ReadAllBytes(Path.Combine(chosen, "two.glb")).AsSpan().SequenceEqual(glb), "An existing file is never replaced.");
        check.That(!ExportFiles.Write(game, "x.png", [1], guarded).Ok && !File.Exists(Path.Combine(game, "x.png")), "Nothing is exported into the game folder.");
        check.That(!ExportFiles.Write(backups, "x.png", [1], guarded).Ok, "Nothing is exported into the backup folder.");
        string link = Path.Combine(root, "link-to-game");
        Directory.CreateSymbolicLink(link, game);
        check.That(!ExportFiles.Write(link, "x.png", [1], guarded).Ok && !File.Exists(Path.Combine(game, "x.png")),
            "A link that leads into the game folder is refused.");
        foreach (string name in new[] { "", "../x.png", "a/b.png", ".hidden", "bad:name.png" })
            check.That(!ExportFiles.Write(chosen, name, [1], guarded).Ok, $"The export name '{name}' is refused.");
        check.That(Directory.GetFiles(chosen, ".onslaught-export-*").Length == 0, "No temporary file is left behind.");
    }

    /// <summary>A root part keyed at (1, 0, 0) with a 2-triangle strip, and a child turned 90° about Z keyed at (0, 2, 0).</summary>
    internal static byte[] TwoPartMesh(bool animated = false)
    {
        byte[] rotate = Floats(0, -1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0), identity = Floats(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0);
        byte[] Part(byte[] orientation, float[] position, int? parent, bool geometry)
        {
            int keys = animated && parent is not null ? 2 : 1;
            Dictionary<int, int> fields = new() { [0xB8] = keys, [0xBC] = keys, [0x10C] = 1, [0xC8] = 1 };
            if (parent is not null) fields[0x98] = 1;
            List<byte> body = [.. Chunk("CMSP", Record(316, fields))];
            if (parent is int p) body.AddRange(Chunk("PRNT", Ints(p)));
            body.AddRange(Box());
            body.AddRange(Chunk("VHFM", keys == 2 ? [0, 1] : [0]));
            body.AddRange(Chunk("HORI", keys == 2 ? [.. orientation, .. orientation] : orientation));
            body.AddRange(Chunk("HPOS", keys == 2 ? Floats(position[0], position[1], position[2], 0, 0, 3, 0, 0) : Floats(position[0], position[1], position[2], 0)));
            List<byte> vb = [.. Chunk("CMVB", Record(296, geometry ? new() { [0x108] = 1, [0x114] = 36 } : []))];
            if (geometry)
            {
                vb.AddRange(Chunk("MMPT", Ints(144, 8, 4, 4, 2, 1)));
                vb.AddRange(Chunk("IBUF", [0, 0, 1, 0, 2, 0, 3, 0]));
                List<byte> vertices = [];
                for (int v = 0; v < 4; v++)
                    vertices.AddRange([.. Floats(v & 1, v >> 1, 0, 0, 0, -1), .. BitConverter.GetBytes(0xFFFFFFFFu), .. Floats(0, 0)]);
                vb.AddRange(Chunk("VBUF", [.. vertices]));
                vb.AddRange(Chunk("TEXR", Ints(-1, -1, -1, -1, -1, -1)));
            }
            body.AddRange(Chunk("PMVB", [.. vb]));
            return Chunk("MESP", [.. body]);
        }
        List<byte> stream = [.. Chunk("CMSH", Record(372, new() { [0x15C] = 2, [0x14] = animated ? 1 : 0 })), .. Chunk("CMST", [])];
        stream.AddRange(Part(rotate, [1, 0, 0], null, geometry: true));
        stream.AddRange(Part(identity, [0, 2, 0], 0, geometry: false));
        if (animated)
        {
            // One mode, "wave": id 1000, frames 0..1, one frame per tick (rate 0.05 → 1 second).
            byte[] mode = new byte[36];
            Encoding.ASCII.GetBytes("wave").CopyTo(mode, 0);
            Ints(1000, 0, 1, 1).CopyTo(mode, 16);
            BitConverter.GetBytes(0.05f).CopyTo(mode, 32);
            stream.AddRange(Chunk("CAMD", mode));
        }
        stream.AddRange(Box());
        return [.. stream];
    }

    private static byte[] Box()
    {
        byte[] inner = Chunk("BBOX", new byte[40]);
        return Chunk("BBOX", inner);
    }

    private static byte[] Chunk(string tag, byte[] payload) => [.. Encoding.ASCII.GetBytes(tag), .. BitConverter.GetBytes(payload.Length), .. payload];

    private static byte[] Record(int size, Dictionary<int, int> fields)
    {
        byte[] record = new byte[size];
        foreach ((int offset, int value) in fields) BinaryPrimitives.WriteInt32LittleEndian(record.AsSpan(offset), value);
        return record;
    }

    private static byte[] Ints(params int[] values) => values.SelectMany(BitConverter.GetBytes).ToArray();
    private static byte[] Floats(params float[] values) => values.SelectMany(BitConverter.GetBytes).ToArray();

    internal static byte[] Member(byte[] data)
    {
        using MemoryStream output = new();
        using (ZLibStream zlib = new(output, CompressionLevel.Optimal, leaveOpen: true)) zlib.Write(data);
        return [.. BitConverter.GetBytes((int)output.Length), .. output.ToArray()];
    }

    private static byte[] Header(int width, int height, string fourcc, int bits, uint[] masks)
    {
        byte[] h = new byte[128];
        Encoding.ASCII.GetBytes("DDS ").CopyTo(h, 0);
        BinaryPrimitives.WriteUInt32LittleEndian(h.AsSpan(4), 124);
        BinaryPrimitives.WriteUInt32LittleEndian(h.AsSpan(12), (uint)height);
        BinaryPrimitives.WriteUInt32LittleEndian(h.AsSpan(16), (uint)width);
        BinaryPrimitives.WriteUInt32LittleEndian(h.AsSpan(80), fourcc.Length > 0 ? 4u : 0x41u);
        if (fourcc.Length > 0) Encoding.ASCII.GetBytes(fourcc).CopyTo(h, 84);
        BinaryPrimitives.WriteUInt32LittleEndian(h.AsSpan(88), (uint)bits);
        for (int m = 0; m < 4; m++) BinaryPrimitives.WriteUInt32LittleEndian(h.AsSpan(92 + 4 * m), masks[m]);
        return h;
    }

    private static int IndexOf(byte[] data, string tag)
    {
        byte[] needle = Encoding.ASCII.GetBytes(tag);
        for (int i = 0; i + 4 <= data.Length; i++)
            if (data.AsSpan(i, 4).SequenceEqual(needle)) return i;
        return -1;
    }

    private static bool Throws(Action action)
    {
        try
        {
            action();
            return false;
        }
        catch (InvalidDataException)
        {
            return true;
        }
    }
}
