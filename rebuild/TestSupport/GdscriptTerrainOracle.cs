// SPDX-License-Identifier: GPL-3.0-or-later
// Transitional comparison against the existing deterministic terrain owner.
// Vectors contain only identities, coordinates and results, never HFLD bytes.
using System.Buffers.Binary;
using System.Reflection;
using System.Security.Cryptography;
using OnslaughtRebuild.Core;

internal static class GdscriptTerrainOracle
{
    private const BindingFlags PrivateInstance = BindingFlags.Instance | BindingFlags.NonPublic;
    private const BindingFlags PrivateStatic = BindingFlags.Static | BindingFlags.NonPublic;
    private static readonly MethodInfo Coordinates = typeof(Level100Terrain).GetMethod(
        "GetRetailFixedCoordinates", PrivateInstance)!;
    private static readonly MethodInfo GroundAtFixed = typeof(Level100Terrain).GetMethod(
        "SampleGroundElevationMillimetersAtFixed", PrivateInstance)!;
    private static readonly MethodInfo DecodeScale = typeof(Level100Terrain).GetMethod(
        "DecodePositiveFloatScale", PrivateStatic)!;
    private static readonly MethodInfo FloorDivide = typeof(Level100Terrain).GetMethod(
        "FloorDivide", PrivateStatic)!;
    private static readonly MethodInfo RoundDivide = typeof(Level100Terrain).GetMethod(
        "RoundDivideAwayFromZero", PrivateStatic)!;
    private static readonly MethodInfo LoadEmbedded = typeof(Level100Terrain).GetMethod(
        "LoadEmbedded", PrivateStatic, null, [typeof(string), typeof(string)], null)!;

    internal static object Build(string repositoryRoot)
    {
        var worlds = new List<object>();
        foreach ((int id, Level100Terrain terrain) in new[] {
            (100, Level100Terrain.Instance), (110, Level100Terrain.World110),
            (200, Level100Terrain.World200), (300, Level100Terrain.World300) })
        {
            string path = Path.GetFullPath(Path.Combine(repositoryRoot, "rebuild", "OnslaughtRebuild.Core",
                "Assets", $"Level{id}", $"level{id}-heightfield.hfld.bin"));
            byte[] source = File.ReadAllBytes(path);
            string resource = $"OnslaughtRebuild.Core.Assets.Level{id}.level{id}-heightfield.hfld.bin";
            using Stream embedded = typeof(Level100Terrain).Assembly.GetManifestResourceStream(resource)!;
            var embeddedBytes = new byte[embedded.Length];
            embedded.ReadExactly(embeddedBytes);
            if (!source.AsSpan().SequenceEqual(embeddedBytes) || Hex(source) != terrain.PayloadSha256)
                throw new InvalidDataException("Prepared terrain input differs from the admitted C# resource: " + id);

            var calls = new List<object>();
            void Add(string operation, int x, int y)
            {
                object result = Capture(() => operation switch
                {
                    "fixed" => terrain.SampleHeightUnitsAtFixed(x, y),
                    "grid" => terrain.SampleGridHeightUnits(x, y),
                    "air_guide" => terrain.SampleAirGuideHeightUnits(x, y),
                    "complexity" => BitConverter.SingleToUInt32Bits(terrain.GetTileComplexityScore(x, y)),
                    "coordinates" => CoordinateResult(terrain, x, y),
                    "ground" => terrain.SampleGroundElevationMillimeters(new SimVector2(x, y)),
                    "ground_fixed" => GroundAtFixed.Invoke(terrain, [x, y])!,
                    "gradient" => GradientResult(terrain, x, y),
                    _ => throw new ArgumentException("Unknown terrain oracle operation.")
                });
                calls.Add(new { operation, x, y, result });
            }

            // Existing SimulationTests retail ground and LOD fixtures remain
            // explicit, alongside the asymmetric RetailPlaneMotionTests arms.
            foreach ((int x, int y) in new[] { (73904, 62272), (73895, 62287), (73647, 62729) })
                Add("fixed", x, y);
            foreach ((int x, int y) in new[] { (36, 30), (36, 31), (35, 30), (0, 0) })
                Add("complexity", x, y);
            foreach ((int x, int y) in new[] { (512, 100), (513, 100), (511, 512), (512, 512),
                (768, 768), (4194305, 4194306), (-1, 10), (10, -1), (1024, 10) })
                Add("air_guide", x, y);

            int[] fixedEdges = [int.MinValue, -1, 0, 1, 255, 256, 2047, 2048, 131070, 131071, 131072, int.MaxValue];
            foreach (int x in fixedEdges)
                foreach (int y in fixedEdges)
                {
                    Add("fixed", x, y);
                    Add("ground_fixed", x, y);
                }
            int[] latticeEdges = [int.MinValue, -1, 0, 1, 7, 8, 63, 64, 255, 256, 511, 512, 513, int.MaxValue];
            foreach (int x in latticeEdges)
                foreach (int y in latticeEdges)
                {
                    Add("grid", x, y);
                    Add("complexity", x, y);
                }
            int[] maskEdges = [int.MinValue, -4194304, -4194303, -1, 0, 1, 7, 8, 255, 256, 511, 512,
                513, 767, 768, 1023, 1024, 16383, 4194303, 4194304, 4194305, int.MaxValue];
            foreach (int x in maskEdges)
                foreach (int y in maskEdges)
                    Add("air_guide", x, y);
            int[] relativeX = [int.MinValue, -288689, -288688, -288687, -1001, -1000, -999, -4, -1,
                0, 1, 3, 4, 999, 1000, 1001, 223312, 223313, 223314, int.MaxValue];
            int[] relativeZ = [int.MinValue, -243251, -243250, -243249, -1001, -1000, -999, -4, -1,
                0, 1, 3, 4, 999, 1000, 1001, 268749, 268750, 268751, int.MaxValue];
            foreach (int x in relativeX)
                foreach (int z in relativeZ)
                    foreach (string operation in new[] { "coordinates", "ground", "gradient" }) Add(operation, x, z);
            var random = new Random(0x48464c44 + id);
            for (int index = 0; index < 256; index++)
            {
                int x = random.Next(131072), y = random.Next(131072);
                Add("fixed", x, y);
                Add("ground_fixed", x, y);
                Add("grid", random.Next(513), random.Next(513));
                Add("complexity", random.Next(64), random.Next(64));
                Add("air_guide", unchecked((int)random.NextInt64(1L << 32)), unchecked((int)random.NextInt64(1L << 32)));
                int rx = random.Next(-289000, 224000), rz = random.Next(-244000, 269000);
                Add("coordinates", rx, rz);
                Add("ground", rx, rz);
                Add("gradient", rx, rz);
            }

            var admission = new List<object>();
            // These two front-door checks are before any binary reads in the
            // existing private loader. Its fixed resource stream cannot accept
            // a synthetic array, so only that byte boundary is reproduced here;
            // metadata and samples below always come from the actual C# owner.
            foreach (int size in new[] { 0, 1, 7, 8, 15, 16, 5107, 5108, 668659, 668661 })
                admission.Add(new { kind = "resize", size, result = ByteAdmission(new byte[size], terrain.PayloadSha256) });
            foreach (int offset in new[] { 0, 4, 8, 12, 16, 16 + 0x102c, 16 + 0x1034,
                16 + 0x1098, 16 + 0x10a4, 5100, 5104, 5108, 668659 })
            {
                byte[] changed = (byte[])source.Clone();
                changed[offset] ^= 1;
                admission.Add(new { kind = "flip", offset, result = ByteAdmission(changed, terrain.PayloadSha256) });
            }
            // The hash-refusal type/message also comes from the actual private
            // loader with a deliberately nonmatching expected hash in the oracle.
            object hashRefusal = Capture(() => LoadEmbedded.Invoke(null, [resource, new string('0', 64)])!);
            int otherWorld = id == 100 ? 110 : 100;
            admission.Add(new { kind = "other_world", world_id = otherWorld, result = hashRefusal });

            worlds.Add(new { id, path, metadata = Metadata(id, terrain), calls, admission,
                full_grid_sha256 = HashGrid(513, (x, y) => terrain.SampleGridHeightUnits(x, y)),
                fixed_grid_sha256 = HashGrid(512, (x, y) => terrain.SampleHeightUnitsAtFixed(x * 256 + 137, y * 256 + 199)),
                lod_sha256 = HashGrid(64, (x, y) => unchecked((int)BitConverter.SingleToUInt32Bits(terrain.GetTileComplexityScore(x, y)))) });
        }

        var scales = new List<object>();
        for (int exponent = 0; exponent <= 255; exponent++)
            foreach (uint fraction in new uint[] { 0, 1, 0x3fffff, 0x7fffff })
                foreach (uint sign in new uint[] { 0, 0x80000000 })
                {
                    uint bits = sign | ((uint)exponent << 23) | fraction;
                    object result = Capture(() =>
                    {
                        var decoded = ((int Significand, long Denominator))DecodeScale.Invoke(null, [unchecked((int)bits)])!;
                        return new { significand = decoded.Significand, denominator = decoded.Denominator.ToString(System.Globalization.CultureInfo.InvariantCulture) };
                    });
                    scales.Add(new { bits, result });
                }

        var divisions = new List<object>();
        foreach (long denominator in new long[] { 1, 2, 3, 1000, 1001, 1L << 33, 1L << 34, 1L << 62 })
        {
            long[] values = [long.MinValue, long.MinValue + 1, -1_000_000_001, -1001, -1000, -999, -2, -1,
                0, 1, 2, 999, 1000, 1001, 1_000_000_001, long.MaxValue - 1, long.MaxValue,
                -denominator, -denominator / 2 - 1, -denominator / 2, -denominator / 2 + 1,
                denominator / 2 - 1, denominator / 2, denominator / 2 + 1, denominator];
            foreach (long value in values.Distinct())
                divisions.Add(new { value = value.ToString(System.Globalization.CultureInfo.InvariantCulture),
                    denominator = denominator.ToString(System.Globalization.CultureInfo.InvariantCulture),
                    floor = ((long)FloorDivide.Invoke(null, [value, denominator])!).ToString(System.Globalization.CultureInfo.InvariantCulture),
                    away = ((long)RoundDivide.Invoke(null, [value, denominator])!).ToString(System.Globalization.CultureInfo.InvariantCulture) });
        }
        return new { worlds, scales, divisions, constants = new Dictionary<string, object> {
            ["SOURCE_SHA256"] = Level100Terrain.SourceSha256,
            ["WORLD110_SOURCE_SHA256"] = Level100Terrain.World110SourceSha256,
            ["WORLD200_SOURCE_SHA256"] = Level100Terrain.World200SourceSha256,
            ["WORLD300_SOURCE_SHA256"] = Level100Terrain.World300SourceSha256,
            ["FIXED_POINT_UNITS_PER_RETAIL_UNIT"] = Level100Terrain.FixedPointUnitsPerRetailUnit,
            ["MAP_EXTENT_RETAIL_UNITS"] = Level100Terrain.MapExtentRetailUnits,
            ["PLAYER_START_RETAIL_X_FIXED"] = Level100Terrain.PlayerStartRetailXFixed,
            ["PLAYER_START_RETAIL_Y_FIXED"] = Level100Terrain.PlayerStartRetailYFixed,
            ["PLAYER_START_REFERENCE_ELEVATION_MILLIMETERS"] = Level100Terrain.PlayerStartReferenceElevationMillimeters,
            ["WALKER_CENTER_OF_GRAVITY_MILLIMETERS"] = Level100Terrain.WalkerCenterOfGravityMillimeters,
            ["WATER_ELEVATION_MILLIMETERS"] = Level100Terrain.WaterElevationMillimeters,
            ["MINIMUM_RELATIVE_X_MILLIMETERS"] = Level100Terrain.MinimumRelativeXMillimeters,
            ["MAXIMUM_RELATIVE_X_MILLIMETERS"] = Level100Terrain.MaximumRelativeXMillimeters,
            ["MINIMUM_RELATIVE_Z_MILLIMETERS"] = Level100Terrain.MinimumRelativeZMillimeters,
            ["MAXIMUM_RELATIVE_Z_MILLIMETERS"] = Level100Terrain.MaximumRelativeZMillimeters } };
    }

    private static object CoordinateResult(Level100Terrain terrain, int x, int z)
    {
        var result = ((int X, int Y))Coordinates.Invoke(terrain, [new SimVector2(x, z)])!;
        return new { x = result.X, y = result.Y };
    }

    private static object GradientResult(Level100Terrain terrain, int x, int z)
    {
        SimVector2 result = terrain.SampleGroundGradientPermille(new SimVector2(x, z));
        return new { x = result.X, z = result.Z };
    }

    private static object Metadata(int id, Level100Terrain terrain) => new {
        world_id = id, payload_sha256 = terrain.PayloadSha256,
        height_scale_bits = BitConverter.SingleToUInt32Bits(terrain.HeightScale), mixer_set = terrain.MixerSet,
        sky_cube = terrain.SkyCube, detail_texture = terrain.DetailTexture,
        water_level_bits = BitConverter.SingleToUInt32Bits(terrain.WaterLevel), water_texture = terrain.WaterTexture,
        fog_color_rgb24 = terrain.FogColorRgb24, fog_density_bits = BitConverter.SingleToUInt32Bits(terrain.FogDensity),
        sun_color_rgb24 = terrain.SunColorRgb24, anti_sun_color_rgb24 = terrain.AntiSunColorRgb24,
        ambient_color_rgb24 = terrain.AmbientColorRgb24,
        sun_position_x_bits = BitConverter.SingleToUInt32Bits(terrain.SunPositionX),
        sun_position_y_bits = BitConverter.SingleToUInt32Bits(terrain.SunPositionY),
        sun_position_z_bits = BitConverter.SingleToUInt32Bits(terrain.SunPositionZ) };

    private static object ByteAdmission(byte[] source, string pin) => Capture(() =>
    {
        if (source.Length != 668660)
            throw new InvalidDataException("The retained heightfield has an unexpected length.");
        if (Hex(source) != pin)
            throw new InvalidDataException("The retained heightfield hash does not match its provenance.");
        throw new InvalidOperationException("Corruption fixture unexpectedly passed byte admission.");
    });

    private static object Capture(Func<object> operation)
    {
        try { return new { ok = true, value = operation() }; }
        catch (Exception error)
        {
            while (error is TargetInvocationException { InnerException: not null } invocation) error = invocation.InnerException;
            var result = new Dictionary<string, object> { ["ok"] = false, ["error_type"] = error.GetType().Name,
                ["parameter"] = error is ArgumentException argument ? argument.ParamName ?? "" : "" };
            if (error is InvalidDataException) result["error"] = error.Message;
            return result;
        }
    }

    private static string HashGrid(int axis, Func<int, int, int> sampler)
    {
        using IncrementalHash hash = IncrementalHash.CreateHash(HashAlgorithmName.SHA256);
        byte[] row = new byte[axis * sizeof(int)];
        for (int x = 0; x < axis; x++)
        {
            for (int y = 0; y < axis; y++) BinaryPrimitives.WriteInt32LittleEndian(row.AsSpan(y * sizeof(int)), sampler(x, y));
            hash.AppendData(row);
        }
        return Convert.ToHexString(hash.GetHashAndReset());
    }

    private static string Hex(byte[] source) => Convert.ToHexString(SHA256.HashData(source));
}
