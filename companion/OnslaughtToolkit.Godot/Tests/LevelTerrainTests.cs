// SPDX-License-Identifier: GPL-3.0-only
using System.Buffers.Binary;
using System.Security.Cryptography;
using System.Text;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// The terrain and the map's arithmetic against the Toolkit's Python reference and on authored data (no game bytes): the ERES
/// chunk reads to the samples the reference reads, the lookup answers the bits the reference's port answers at every probe
/// (the square's edges, tile and sample boundaries, negative, fractional and far-out positions), a damaged chunk is refused,
/// an archive carries its terrain to the model, the relief shows water and land where the lookup says, and the map's pixel and
/// world conversions, zoom, pan and hit test do what the control draws by. Nothing here touches Godot.
/// </summary>
internal static class LevelTerrainTests
{
    internal static void Run(string outputDirectory, Checks check)
    {
        check.Suite("level terrain");
        Stage(check, "the terrain vector", () => Vector(check));
        Stage(check, "the test's terrain builder", () => Builder(check));
        Stage(check, "a damaged terrain", () => Damaged(check));
        Stage(check, "the archive's terrain", () => Archive(Path.Combine(outputDirectory, "level-terrain"), check));
        Stage(check, "the relief", () => Relief(check));
        Stage(check, "the relief's lighting and colours", () => Lighting(check));
        Stage(check, "the map view", () => View(check));
    }

    private static void Stage(Checks check, string name, Action stage)
    {
        try
        {
            stage();
        }
        catch (Exception error)
        {
            check.Fail($"{name} stopped with {error.GetType().Name}: {error.Message}");
        }
    }

    private static uint Bits(float value) => BitConverter.SingleToUInt32Bits(value);

    private static byte[] Eres() => LevelTests.Unpack(LevelVectors.Terrain.Eres);

    /// <summary>
    /// An authored ERES payload in the layout CEngine::Deserialize reads, as tools/heightfield_lookup_tests.py builds one: the given samples,
    /// scale and water level, and (when asked) the optional mixer data (the second mip's two textures and extra blocks, the sixth slot's three
    /// entries) that the loader reads when their pointers are not 0.
    /// </summary>
    internal static byte[] BuildEres(ReadOnlySpan<short> samples, float scale, float water, bool mixerData = false)
    {
        using MemoryStream stream = new();
        void Header(string tag) => stream.Write([.. Encoding.ASCII.GetBytes(tag), 0, 0, 0, 0]);
        void Int(int value) => stream.Write(BitConverter.GetBytes(value));
        Header("ENGN");
        Int(7);
        for (int mip = 0; mip < 7; mip++)
        {
            bool carries = mixerData && mip == 1;
            Header("MTEX");
            Header("DATA");
            byte[] map = new byte[0x4C];
            if (carries)
            {
                BinaryPrimitives.WriteUInt32LittleEndian(map, 1);
                BinaryPrimitives.WriteUInt32LittleEndian(map.AsSpan(8), 1);
                BinaryPrimitives.WriteInt32LittleEndian(map.AsSpan(16), 6);
                BinaryPrimitives.WriteInt32LittleEndian(map.AsSpan(20), 2);
            }
            BinaryPrimitives.WriteInt16LittleEndian(map.AsSpan(12), 3);
            stream.Write(map);
            if (carries)
            {
                Header("TXDT");
                stream.Write(new byte[2 * 6]);
                Header("TXEX");
                stream.Write(new byte[2 * 1024]);
            }
        }
        Header("MAP ");
        Int(7);
        Header("HFLD");
        Header("DATA");
        byte[] record = new byte[0x13DC];
        BinaryPrimitives.WriteSingleLittleEndian(record.AsSpan(0x102C), scale);
        BinaryPrimitives.WriteSingleLittleEndian(record.AsSpan(0x1034), water);
        record[0x1030] = 3;
        (record[0x1078 + 0x18], record[0x1078 + 0x1C], record[0x1078 + 0x1D]) = (2, 1, 4);
        stream.Write(record);
        Header("HGTS");
        byte[] raw = new byte[samples.Length * 2];
        for (int i = 0; i < samples.Length; i++) BinaryPrimitives.WriteInt16LittleEndian(raw.AsSpan(i * 2), samples[i]);
        stream.Write(raw);
        Header("MIXR");
        for (int slot = 0; slot < 0x1000; slot++)
        {
            bool carries = mixerData && slot == 5;
            Header("SLOT");
            Header("DATA");
            byte[] entry = new byte[0x14];
            if (carries)
            {
                BinaryPrimitives.WriteInt32LittleEndian(entry, 3);
                BinaryPrimitives.WriteUInt32LittleEndian(entry.AsSpan(4), 1);
            }
            stream.Write(entry);
            if (carries)
            {
                Header("SDAT");
                stream.Write(new byte[3 * 81]);
            }
        }
        Header("MMAP");
        stream.Write(new byte[0x40000]);
        return stream.ToArray();
    }

    /// <summary>A terrain whose height at the world position (x, y) is <paramref name="height"/> in sample units, for the whole 0 to 512 square.</summary>
    private static Heightfield Custom(Func<int, int, int> height, float scale, float water)
    {
        short[] samples = new short[Heightfield.SampleCount];
        for (int tileX = 0; tileX < 64; tileX++)
            for (int tileY = 0; tileY < 64; tileY++)
                for (int row = 0; row < 9; row++)
                    for (int column = 0; column < 9; column++) samples[((tileX * 64 + tileY) * 9 + row) * 9 + column] = (short)height(tileX * 8 + column, tileY * 8 + row);
        return Heightfield.Read(BuildEres(samples, scale, water));
    }

    private static void Builder(Checks check)
    {
        Heightfield field = Heightfield.Read(Eres());
        check.That(BuildEres(field.Samples, field.Scale, field.Water, mixerData: true).AsSpan().SequenceEqual(Eres()),
            "the test's terrain builder writes the bytes the Python builder wrote for the vector's terrain, optional mixer data included");
        Heightfield plain = Heightfield.Read(BuildEres(field.Samples, field.Scale, field.Water));
        check.That(plain.SamplesSha256() == field.SamplesSha256() && Bits(plain.Scale) == Bits(field.Scale) && Bits(plain.Water) == Bits(field.Water), "without that data it is the same terrain");
    }

    private static void Vector(Checks check)
    {
        LevelVectors.TerrainVector vector = LevelVectors.Terrain;
        Heightfield field = Heightfield.Read(Eres());
        check.That(field.SamplesSha256() == vector.SamplesSha256 && Bits(field.Scale) == vector.ScaleBits && Bits(field.Water) == vector.WaterBits && field.Samples.Length == Heightfield.SampleCount,
            "the terrain chunk reads to the samples, scale and water the reference reads");
        byte[] probes = LevelTests.Unpack(vector.Probes);
        check.That(vector.Count >= 2000 && probes.Length == vector.Count * 12, $"the vector holds its probes ({vector.Count})");
        int different = 0;
        for (int i = 0; i < vector.Count; i++)
        {
            ReadOnlySpan<byte> record = probes.AsSpan(i * 12, 12);
            float x = BitConverter.UInt32BitsToSingle(BinaryPrimitives.ReadUInt32LittleEndian(record)), y = BitConverter.UInt32BitsToSingle(BinaryPrimitives.ReadUInt32LittleEndian(record[4..]));
            uint expected = BinaryPrimitives.ReadUInt32LittleEndian(record[8..]), actual = Bits(field.HeightAt(x, y));
            if (actual == expected) continue;
            if (++different <= 5) check.Fail($"the height at ({x:R}, {y:R}) is {actual:x8}, the reference's is {expected:x8}");
        }
        check.That(different == 0, $"the lookup answers the reference's bits at all {vector.Count} probes ({different} differ)");
        check.That(Bits(Heightfield.Bias) == 0x3AFFFEB0, "the bias is the game's constant");
        check.That(field.HeightAt(float.NaN, 5f) == 0f && field.HeightAt(5f, float.PositiveInfinity) == 0f && field.HeightAt(512f, 5f) == 0f && field.HeightAt(5f, -0.01f) == 0f, "outside the square, and for a position that is not finite, the lookup answers 0");
        check.That(Bits(field.HeightAt(-0f, 4f)) == Bits(field.HeightAt(0f, 4f)), "a negative zero is a zero to the lookup");
    }

    private static void Damaged(Checks check)
    {
        byte[] eres = Eres();
        // The second mip carries textures (its map record starts at 120): a count below zero, a size that no longer matches the bytes after it, and a count far past the payload.
        byte[] Patched(int at, int value) => [.. eres[..at], .. BitConverter.GetBytes(value), .. eres[(at + 4)..]];
        foreach ((string what, byte[] bytes) in new (string, byte[])[]
                 {
                     ("a mixer mip with a negative texture count", Patched(120 + 20, -5)), ("a mixer mip whose texture size does not match its bytes", Patched(120 + 16, 7)),
                     ("a mixer mip with a texture count far past the payload", Patched(120 + 20, 1_000_000)),
                     ("a payload one byte short", eres[..^1]), ("a payload with a byte too many", [.. eres, 0]), ("a payload that does not start with ENGN", [.. "XXXX"u8.ToArray(), .. eres[4..]]),
                     ("a payload with six mixer mips", [.. eres[..8], 6, 0, 0, 0, .. eres[12..]]), ("a payload cut inside its samples", eres[..400_000]), ("no bytes", []),
                 })
        {
            try
            {
                Heightfield.Read(bytes);
                check.Fail($"{what}: accepted");
            }
            catch (InvalidDataException)
            {
                check.That(true, what);
            }
            catch (Exception error)
            {
                check.Fail($"{what}: refused with {error.GetType().Name} instead of InvalidDataException: {error.Message}");
            }
        }
    }

    private static void Archive(string folder, Checks check)
    {
        byte[] archive = LevelTests.Unpack(LevelVectors.Archives.First(a => a.Name == "level-100-terrain").File);
        LevelWorlds worlds = LevelArchive.Read(archive);
        check.That(worlds.Terrain is not null && SHA256.HashData(worlds.Terrain).AsSpan().SequenceEqual(SHA256.HashData(Eres())) && worlds.RealLevel == 100, "an archive carries its ERES chunk");

        string game = Path.Combine(folder, "game");
        string resources = Path.Combine(game, "data", "resources");
        Directory.CreateDirectory(resources);
        File.WriteAllBytes(Path.Combine(resources, "100_res_PC.aya"), archive);
        File.WriteAllBytes(Path.Combine(resources, "200_res_PC.aya"), LevelTests.Unpack(LevelVectors.Archives.First(a => a.Name == "base-and-real").File));
        LevelEditorModel model = LevelEditorModel.ForGame(game);
        check.That(model.Open(100) && model.Terrain is not null && model.TerrainProblem is null && model.Terrain.SamplesSha256() == LevelVectors.Terrain.SamplesSha256, "the model opens a level with its terrain");
        check.That(model.Open(200) && model.Session is not null && model.Terrain is null && model.TerrainProblem!.Contains("could not be read", StringComparison.Ordinal),
            "a level whose ERES chunk is not a terrain still opens for editing, without a terrain and with the reason: " + model.TerrainProblem);
        check.That(model.Open(100) && model.Terrain is not null, "and a level with a terrain opens again");
        LevelWorlds twice = LevelArchive.Read(LevelTests.Unpack(LevelVectors.Archives.First(a => a.Name == "level-100-two-terrains").File));
        check.That(twice.Terrain is not null && SHA256.HashData(twice.Terrain).AsSpan().SequenceEqual(SHA256.HashData(Eres())) && twice.RealLevel == 100, "an archive with two ERES chunks keeps the first");

        // A drag on the map moves a row's X and Y and keeps its Z bit for bit; a refused move changes nothing.
        byte[] baseline = LevelTests.Body("authored-v50");
        ObjectRow row = model.Row(0)!;
        MoveOutcome moved = model.MoveTo(0, 12.5f, 7.25f);
        check.That(moved.Result == MoveResult.Moved && model.Row(0)!.Position == new System.Numerics.Vector3(12.5f, 7.25f, row.Position.Z) && moved.Message == "Tank 1 (row 0) now stands at 12.5, 7.25, 0.", $"a drag moves X and Y: {moved.Message}");
        check.That(model.MoveTo(0, 12.5f, 7.25f).Result == MoveResult.Unchanged && model.MoveTo(0, float.NaN, 1f).Result == MoveResult.Refused && model.MoveTo(99, 1f, 1f).Result == MoveResult.Refused &&
                   model.Session!.Undo() && model.Session.ToBytes().AsSpan().SequenceEqual(baseline), "a move to where it stands, a move to a position that is not finite and a move of a missing row change nothing; one undo undoes the drag");
        check.That(new[] { model.MoveTo(0, float.NaN, 1f), model.MoveTo(0, 1f, float.NaN), model.MoveTo(0, float.PositiveInfinity, 1f), model.MoveTo(0, 1f, float.NegativeInfinity) }
                       .All(outcome => outcome.Result == MoveResult.Refused && outcome.Message == "A position must be finite numbers.") &&
                   model.MoveTo(-1, 1f, 1f).Result == MoveResult.Refused && model.MoveTo(model.Session!.Body.Things.Count, 1f, 1f).Result == MoveResult.Refused &&
                   model.MoveTo(model.Session.Body.Things.Count - 1, 5f, 5f).Result == MoveResult.Moved, "a move of one coordinate that is not finite, or of the row before the first or the row after the last, is refused; the last row moves");
        model.Session!.Undo();
        model.Move(0, "0", "20", "0");
        MoveOutcome signed = model.MoveTo(0, -0f, 20f);
        check.That(signed.Result == MoveResult.Moved && Bits(model.Row(0)!.Position.X) == 0x80000000, "dragging to -0 where a 0 stands is a move: the bits differ");
        model.Session.Undo();
        model.Session.Undo();
        EditSession zeroed = new(baseline);
        zeroed.Apply(new MoveObject(0, new System.Numerics.Vector3(10f, 20f, -0f)));
        LevelEditorModel negative = LevelEditorModel.ForGame(game);
        negative.Open(100);
        negative.Move(0, "10", "20", "-0");
        negative.MoveTo(0, 30f, 40f);
        check.That(Bits(negative.Row(0)!.Position.Z) == 0x80000000 && negative.Row(0)!.Position.X == 30f, "a drag keeps a stored -0 as it was");
    }

    private static void Relief(Checks check)
    {
        Heightfield field = Heightfield.Read(Eres());
        ReliefImage image = TerrainRelief.Build(field);
        check.That(image.Width == 512 && image.Height == 512 && image.Rgba.Length == 512 * 512 * 4 && image.PixelsPerUnit == 1, "the relief is one pixel to the world unit over the 512 square");
        check.That(image.PixelOf(0f, 0f) == (0, 511) && image.PixelOf(100.5f, 411.5f) == (100, 100) && image.PixelOf(511.99f, 511.99f) == (511, 0) && image.PixelOf(512f, 5f) is null && image.PixelOf(-0.1f, 5f) is null &&
                   image.PixelOf(5f, 512f) is null && image.PixelOf(5f, -0.1f) is null,
            "X runs right and Y runs up: the pixel of (0, 0) is bottom left, of (100.5, 411.5) is column 100, row 100");
        // Water is ground whose height is greater than the water's (Z is down); the pixel shows it blue-dominant, land green-dominant.
        int checkedPixels = 0, wrong = 0;
        for (float y = 3.5f; y < 512; y += 17f)
        {
            for (float x = 2.5f; x < 512; x += 19f)
            {
                float height = field.HeightAt(x, y);
                if (Math.Abs(height - field.Water) < 0.05f) continue;
                (int column, int row) = image.PixelOf(x, y)!.Value;
                (byte r, byte g, byte b) = image.Color(column, row);
                bool shownAsWater = b > g;
                if (shownAsWater != (height > field.Water)) wrong++;
                checkedPixels++;
            }
        }
        check.That(checkedPixels > 500 && wrong == 0, $"water and land are tinted where the lookup says ({checkedPixels} pixels, {wrong} wrong)");
        check.That(TerrainRelief.Build(field).Rgba.AsSpan().SequenceEqual(image.Rgba), "the relief is the same every time");
        ReliefImage fine = TerrainRelief.Build(field, 2);
        check.That(fine.Width == 1024 && fine.PixelOf(100.5f, 411.5f) == (201, 1024 - 1 - 823), "at two pixels to the unit the image is 1024 wide and the mapping follows");
        // Slopes shade: a pixel on the slope facing the light is lighter than one facing away.
        (int, int) bright = (0, 0), dim = (0, 0);
        float brightest = -1, dimmest = 2;
        for (int row = 1; row < 511; row++)
        {
            for (int column = 1; column < 511; column++)
            {
                (byte r, byte g, byte b) = image.Color(column, row);
                if (b > g) continue;  // land only
                float lum = (r + g + b) / 765f;
                if (lum > brightest) (brightest, bright) = (lum, (column, row));
                if (lum < dimmest) (dimmest, dim) = (lum, (column, row));
            }
        }
        check.That(brightest > dimmest + 0.1f, $"land is shaded by its slope (lightest {brightest:0.00}, darkest {dimmest:0.00})");
        foreach (int refused in new[] { 0, 5, -1 })
        {
            try
            {
                TerrainRelief.Build(field, refused);
                check.Fail($"a relief of {refused} pixels to the unit was made");
            }
            catch (ArgumentOutOfRangeException)
            {
                check.That(true, $"a relief of {refused} pixels to the unit is refused");
            }
        }
        check.That(TerrainRelief.Build(field, 4).Width == 2048, "four pixels to the unit is the most");
    }

    private static float Lum(ReliefImage image, float x, float y)
    {
        (int column, int row) = image.PixelOf(x, y)!.Value;
        (byte r, byte g, byte b) = image.Color(column, row);
        return (r + g + b) / 765f;
    }

    private static bool Water(ReliefImage image, float x, float y)
    {
        (int column, int row) = image.PixelOf(x, y)!.Value;
        (_, byte g, byte b) = image.Color(column, row);
        return b > g;
    }

    /// <summary>The relief's lighting and palette on authored terrains whose answers are known: which side of a hill is lit, how water darkens, what a flat pixel's colours are.</summary>
    private static void Lighting(Checks check)
    {
        // A tent along X (a ridge at x = 256 whose sides rise a quarter of a unit of height to the unit of distance) and one along Y: at equal heights on the
        // two sides, the side facing the north-west is the lighter.
        Heightfield tentX = Custom((x, y) => -(1000 - Math.Abs(x - 256)), 0.25f, 100f), tentY = Custom((x, y) => -(1000 - Math.Abs(y - 256)), 0.25f, 100f);
        ReliefImage reliefX = TerrainRelief.Build(tentX), reliefY = TerrainRelief.Build(tentY);
        float westFacing = Lum(reliefX, 156.5f, 256.5f), eastFacing = Lum(reliefX, 355.5f, 256.5f);
        check.That(westFacing > eastFacing + 0.1f, $"a slope facing west is lighter than one facing east at the same height ({westFacing:0.000} against {eastFacing:0.000})");
        float northFacing = Lum(reliefY, 256.5f, 355.5f), southFacing = Lum(reliefY, 256.5f, 156.5f);
        check.That(northFacing > southFacing + 0.1f, $"a slope facing north is lighter than one facing south at the same height ({northFacing:0.000} against {southFacing:0.000})");

        // Water darkens with depth: a shallow and a deep flat, both under a water level of -5 (height above it is under water).
        ReliefImage water = TerrainRelief.Build(Custom((x, y) => x < 256 ? -4 : 3, 1f, -5f));
        check.That(Water(water, 100.5f, 256.5f) && Water(water, 400.5f, 256.5f) && Lum(water, 400.5f, 256.5f) < Lum(water, 100.5f, 256.5f) - 0.03f, $"deep water is darker than shallow ({Lum(water, 400.5f, 256.5f):0.000} against {Lum(water, 100.5f, 256.5f):0.000})");

        // Ground exactly at the water's height is land; its flat colours are the palette's (a pixel of ground at the low end of the range, lit square on).
        ReliefImage edge = TerrainRelief.Build(Custom((x, y) => -4, 0.5f, -2f));
        (int column, int row) = edge.PixelOf(256.5f, 256.5f)!.Value;
        check.That(!Water(edge, 256.5f, 256.5f) && edge.Color(column, row) == (56, 76, 56), $"ground at the water's height is land, in the palette's flat colours: {edge.Color(column, row)}");
        // Land is coloured by its height between the lowest and the highest of the picture: a step of two units, far from the water.
        ReliefImage steps = TerrainRelief.Build(Custom((x, y) => x < 256 ? -4 : -12, 0.25f, 100f));
        (int lowColumn, int lowRow) = steps.PixelOf(100.5f, 256.5f)!.Value;
        (int highColumn, int highRow) = steps.PixelOf(400.5f, 256.5f)!.Value;
        check.That(steps.Color(lowColumn, lowRow) == (56, 76, 56) && steps.Color(highColumn, highRow) == (178, 168, 133),
            $"the lowest ground has the palette's low colours and the highest its high ones: {steps.Color(lowColumn, lowRow)}, {steps.Color(highColumn, highRow)}");

        // A pixel shows the terrain at its centre, not its corner: stripes of one-unit width give water at every whole position and land halfway between.
        ReliefImage stripesX = TerrainRelief.Build(Custom((x, y) => x % 2 == 0 ? -4 : 2, 1f, 0f)), stripesY = TerrainRelief.Build(Custom((x, y) => y % 2 == 0 ? -4 : 2, 1f, 0f));
        int waterPixels = 0;
        for (int i = 0; i < 20; i++)
        {
            if (Water(stripesX, 100.5f + i, 256.5f)) waterPixels++;
            if (Water(stripesY, 256.5f, 100.5f + i)) waterPixels++;
        }
        check.That(waterPixels == 0, $"a pixel shows the terrain at its centre, where the stripes read as land ({waterPixels} water pixels of 40)");
    }

    private static void View(Checks check)
    {
        MapView view = new();
        view.Resize(800, 600);
        check.That(Math.Abs(view.Scale - 600 / (512 * 1.04)) < 1e-9 && view.CenterX == 256 && view.CenterY == 256, "the first size fits the whole square");
        (double sx, double sy) = view.ToScreen(256, 256);
        check.That(Math.Abs(sx - 400) < 1e-9 && Math.Abs(sy - 300) < 1e-9, "the middle of the square is the middle of the view");
        (double lx, double ly) = view.ToScreen(0, 0);
        (double rx, double ry) = view.ToScreen(512, 512);
        check.That(lx < rx && ry < ly && lx >= 0 && rx <= 800 && ry >= 0 && ly <= 600, "X runs right and Y runs up: (0, 0) is bottom left and (512, 512) top right, both inside the view");
        bool roundTrips = true;
        foreach ((double x, double y) in new[] { (0.0, 0.0), (100.25, 411.5), (511.99, 3.0), (-20.0, 700.0) })
        {
            (double px, double py) = view.ToScreen(x, y);
            (double wx, double wy) = view.ToWorld(px, py);
            roundTrips &= Math.Abs(wx - x) < 1e-9 && Math.Abs(wy - y) < 1e-9;
        }
        check.That(roundTrips, "a position goes to a pixel and back");

        // Zooming about a pixel keeps the world position under it.
        (double beforeX, double beforeY) = view.ToWorld(650, 120);
        view.ZoomAbout(650, 120, 3);
        (double afterX, double afterY) = view.ToWorld(650, 120);
        check.That(Math.Abs(beforeX - afterX) < 1e-9 && Math.Abs(beforeY - afterY) < 1e-9 && Math.Abs(view.Scale - 3 * 600 / (512 * 1.04)) < 1e-9, "a zoom about a pixel keeps what is under it there");
        view.ZoomAbout(10, 10, 1e9);
        check.That(view.Scale == MapView.MaxScale, "the zoom stops at its largest scale");
        view.ZoomAbout(10, 10, 1e-9);
        check.That(Math.Abs(view.Scale - view.FitScale / 2) < 1e-12, "and at half the scale that fits the square");
        view.Fit();
        (double panX, double panY) = view.ToScreen(100, 100);
        view.Pan(30, -20);
        (double movedX, double movedY) = view.ToScreen(100, 100);
        check.That(Math.Abs(movedX - panX - 30) < 1e-9 && Math.Abs(movedY - panY + 20) < 1e-9, "a pan moves the content by the pixels dragged");
        view.Pan(1e9, 1e9);
        check.That(view.CenterX == 0 && view.CenterY == 512, "a pan cannot take the centre out of the square");
        view.Fit();
        view.Resize(1000, 400);
        check.That(view.CenterX == 256 && Math.Abs(view.Scale - view.FitScale) > 0 && view.Scale >= view.MinScale, "a new size keeps the centre and a scale inside the limits");
        check.That(MapView.MaxScale == 32 && MapView.WorldSize == 512, "the largest zoom is 32 pixels to the unit, and the world is the 512 square");

        // Zooming out about the right-hand edge with the centre at the square's left edge would put the centre outside it: it stays at the edge.
        MapView edge = new();
        edge.Resize(400, 300);
        edge.ZoomAbout(200, 150, 8);
        edge.Pan(1e9, 0);
        double edgeScale = edge.Scale;
        edge.ZoomAbout(400, 150, 0.5);
        check.That(edge.Scale < edgeScale && edge.CenterX == 0, $"zooming out at the edge keeps the centre inside the square: {edge.CenterX}");
        // A window that grows brings a scale that was fine for the small one up to half of what fits the big one.
        MapView growing = new();
        growing.Resize(100, 100);
        growing.Resize(1000, 1000);
        check.That(Math.Abs(growing.Scale - growing.MinScale) < 1e-12 && growing.Scale > 0.9, $"a window that grows lifts the scale to the new smallest: {growing.Scale} (smallest {growing.MinScale})");
        MapView empty = new();
        empty.Resize(0, 0);
        (double ex, double ey) = empty.ToScreen(256, 256);
        check.That(empty.Width == 1 && empty.Height == 1 && empty.FitScale > 0 && double.IsFinite(ex) && double.IsFinite(ey), "a window of no size is treated as one pixel");

        // Hit test: the nearest within the radius wins; the first listed wins a tie; nothing is found beyond the radius.
        view.Fit();
        (double ax, double ay) = view.ToScreen(100, 100);
        (int, double, double)[] marks = [(7, 100, 100), (3, 100.1, 100), (9, 300, 300), (4, 100, 100)];
        // Marks 7 and 4 stand on one spot and mark 3 a tenth of a unit (about a tenth of a pixel) to its right.
        check.That(view.Nearest(marks, ax, ay, 12) == 7 && view.Nearest(marks, ax + 0.2, ay, 12) == 3, "the nearest mark within the radius is hit, and the first listed wins a tie");
        check.That(view.Nearest(marks, ax + 50, ay + 50, 12) is null && view.Nearest([], ax, ay, 12) is null, "a pixel far from every mark hits none");
        (double bx, double by) = view.ToScreen(300, 300);
        check.That(view.Nearest(marks, bx + 5, by - 5, 12) == 9 && view.Nearest(marks, bx + 9, by + 9, 12) is null, "the radius is in pixels");
    }
}
