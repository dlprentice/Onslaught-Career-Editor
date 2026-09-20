// SPDX-License-Identifier: GPL-3.0-or-later
using System.Reflection;
using System.Security.Cryptography;
using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using A = Godot.Collections.Array;
using D = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

/// <summary>Exports bounded, object-free fixtures from the unchanged former
/// renderer. Only explicit fresh worktree-local output paths may be written.</summary>
public sealed partial class HeightFieldSceneChecks : Node
{
    private const BindingFlags InstanceFields = BindingFlags.Instance | BindingFlags.NonPublic;
    private const BindingFlags StaticFields = BindingFlags.Static | BindingFlags.NonPublic;
    private int _checks;

    public override async void _Ready()
    {
        LegacyLevel100HeightFieldReference? field = null;
        Camera3D? camera = null;
        MeshInstance3D? observer = null;
        try
        {
            string[] args = OS.GetCmdlineUserArgs();
            Check(args.Length == 2, "Two fresh owned output paths are required.");
            string fixturePath = Owned(args[0]);
            string reportPath = Owned(args[1]);
            Check(fixturePath != reportPath, "Fixture and report paths are distinct.");
            Check(!Engine.IsEditorHint() && DisplayServer.GetName() == "headless", "Reference is headless runtime only.");
            Input.MouseModeEnum pointer = Input.MouseMode;
            string terrainPath = Path.GetFullPath(Path.Combine(ProjectSettings.GlobalizePath("res://"),
                "..", "OnslaughtRebuild.Core", "Assets", "Level100", "level100-heightfield.hfld.bin"));
            string inputHash = Hex(File.ReadAllBytes(terrainPath));
            field = LegacyLevel100HeightFieldReference.Load();
            using D metadata = Metadata(field);
            using D initialState = State(field);
            using A heights = HeightCases(field);
            using A indices = IndexCases();
            using A cameras = new();
            using var sentinel = new StandardMaterial3D { AlbedoColor = new Color(0.17f, 0.31f, 0.59f, 1f) };
            camera = new Camera3D { Current = false };
            observer = new MeshInstance3D();
            AddChild(camera);
            AddChild(observer);

            void CameraCase(string name, Vector3 position, Vector3 forward, Vector3 up,
                bool reset = false, bool supplied = false, bool clear = false, bool rawForward = false)
            {
                if (reset)
                {
                    observer.Mesh = null;
                    field!.Mesh.Dispose();
                    ArrayMesh? provided = supplied ? SeedMesh() : null;
                    field = LegacyLevel100HeightFieldReference.Load(provided);
                    Check(!supplied || ReferenceEquals(provided, field.Mesh), "Constructor retains the supplied mesh object.");
                }
                observer.Mesh = field!.Mesh;
                Check(observer.Mesh == field.Mesh, "Another production node can share this mesh.");
                bool hadSurface = field.Mesh.GetSurfaceCount() != 0;
                if (hadSurface) field.Mesh.SurfaceSetMaterial(0, sentinel);
                if (clear) field.Mesh.ClearSurfaces();
                camera!.Position = position;
                if (rawForward)
                    camera.Basis = new Basis(Vector3.Right, Vector3.Up, -forward);
                else
                    camera.LookAt(position + forward, up);
                Vector3 actualPosition = camera.GlobalPosition;
                Vector3 actualForward = -camera.GlobalTransform.Basis.Z;
                IReadOnlyList<Level100TerrainTileSelection> selections = field.Update(camera);
                Check(selections.Count == 4096, "Every y/x tile receives a selection.");
                int[] packed = new int[4096 * 3];
                for (int index = 0; index < selections.Count; index++)
                {
                    Level100TerrainTileSelection row = selections[index];
                    Check(row.TileX == index % 64 && row.TileY == index / 64, "The selection order is y then x.");
                    packed[index * 3] = row.GeometryLevel;
                    packed[index * 3 + 1] = row.TextureLevel;
                    packed[index * 3 + 2] = row.EdgeFlags;
                }
                bool keptSentinel = field.Mesh.SurfaceGetMaterial(0) == sentinel;
                using D rowState = State(field);
                using D mesh = MeshWords(field.Mesh);
                using D rowValue = new()
                {
                    ["name"] = name, ["reset"] = reset, ["supplied_mesh"] = supplied, ["clear_before"] = clear,
                    ["position"] = Words(actualPosition), ["forward"] = Words(actualForward),
                    ["had_surface"] = hadSurface, ["kept_sentinel"] = keptSentinel,
                    ["selections"] = packed, ["state"] = rowState, ["mesh"] = mesh,
                };
                Append(cameras, rowValue);
                Check(observer.Mesh == field.Mesh, "LOD updates mutate the supplied mesh in place.");
            }

            // The current opening law is sampled against the actual initial
            // player facts, held frozen. These are renderer inputs, not a claim
            // that four sparse samples execute the opening gameplay route.
            var session = new InteractiveSession(0x48464c44, Level100StaticWorldAsset.LoadActorDefinitions());
            WorldSnapshot initial = session.CurrentSnapshot;
            var opening = new AttachedPanCameraState(SimulationConstants.Level100OpeningPanTicks, 1);
            WorldSnapshot previous = initial;
            foreach (int tick in new[] { 0, 30, 90, 119 })
            {
                WorldSnapshot current = initial with { Tick = tick,
                    Level100OpeningTicksRemaining = SimulationConstants.Level100OpeningPanTicks - tick };
                opening.Advance(previous, current);
                ClientCameraPose pose = opening.Sample(1f).Pose;
                CameraCase("opening-frozen-player-" + tick, Vector(pose.Position), Vector(pose.Forward), Vector(pose.Up));
                if (tick == 0)
                    CameraCase("opening-exact-repeat", Vector(pose.Position), Vector(pose.Forward), Vector(pose.Up));
                previous = current;
            }
            CameraCase("smoothed-move", new(40.25f, 7.5f, -60.125f), new(-0.25f, -0.125f, -1f), Vector3.Up);
            CameraCase("smoothed-repeat", new(40.25f, 7.5f, -60.125f), new(-0.25f, -0.125f, -1f), Vector3.Up);
            CameraCase("far-supplied-mesh", new(4096f, 512f, -4096f), new(-1f, -0.25f, -1f), Vector3.Up,
                reset: true, supplied: true);
            CameraCase("far-exact-repeat", new(4096f, 512f, -4096f), new(-1f, -0.25f, -1f), Vector3.Up);
            CameraCase("far-cleared-mesh", new(4096f, 512f, -4096f), new(-1f, -0.25f, -1f), Vector3.Up, clear: true);
            CameraCase("near-corner-scaled-forward", new(-288.6875f, -10f, 243.25f), new(0.25f, -0.5f, -1.25f), Vector3.Up,
                reset: true, rawForward: true);
            CameraCase("opposite-map-edge", new(223.3125f, 50f, -268.75f), new(1f, -0.25f, 1f), Vector3.Up, reset: true);
            Check(cameras.Count == 12, "Full mesh generation stays bounded to twelve updates.");
            Check(Input.MouseMode == pointer, "Heightfield fixtures never take pointer ownership.");
            Check(Hex(File.ReadAllBytes(terrainPath)) == inputHash, "The retained heightfield bytes remain unchanged.");
            using D fixture = new()
            {
                ["schema"] = 1, ["completed"] = new A { "height_field_reference" },
                ["terrain_path"] = terrainPath, ["terrain_sha256"] = inputHash,
                ["metadata"] = metadata, ["initial_state"] = initialState,
                ["height_cases"] = heights, ["index_cases"] = indices, ["camera_cases"] = cameras,
            };
            using Variant fixtureValue = fixture;
            Check(ObjectFree(fixtureValue), "Fixture contains values only, never native objects or resources.");
            using (var output = Godot.FileAccess.Open(fixturePath, Godot.FileAccess.ModeFlags.Write)
                ?? throw new IOException("Cannot create heightfield reference fixture.")) output.StoreVar(fixtureValue, false);
            using D report = new()
            {
                ["schema"] = 1, ["failure_count"] = 0, ["completed"] = new A { "height_field_reference" },
                ["counts"] = new D { ["reference"] = _checks, ["height_cases"] = heights.Count,
                    ["index_cases"] = indices.Count, ["camera_cases"] = cameras.Count },
            };
            using (var output = Godot.FileAccess.Open(reportPath, Godot.FileAccess.ModeFlags.Write)
                ?? throw new IOException("Cannot create heightfield reference report.")) output.StoreString(Json.Stringify(report));
            observer.Mesh = null;
            observer.Free(); observer = null;
            camera.Free(); camera = null;
            field.Mesh.Dispose(); field = null;
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            GD.Print($"HEIGHT_FIELD_REFERENCE_CHECKS: {_checks} passed; {heights.Count} height samples, {indices.Count} index arrays, {cameras.Count} full meshes; {fixturePath}");
            GetTree().Quit(0);
        }
        catch (Exception error)
        {
            observer?.Free();
            camera?.Free();
            field?.Mesh.Dispose();
            GD.PushError(error.ToString());
            GetTree().Quit(1);
        }
    }

    private static A HeightCases(LegacyLevel100HeightFieldReference field)
    {
        A result = new();
        void Add(float x, float z)
        {
            using D row = new() { ["x_bits"] = Word(x), ["z_bits"] = Word(z),
                ["value_bits"] = Word(field.SampleRelativeHeight(x, z)) };
            Append(result, row);
        }
        float[] edges = [float.MinValue, -513f, MathF.BitDecrement(-288.6875f), -288.6875f,
            MathF.BitIncrement(-288.6875f), -243.25f, -1f, -0f, 0f, float.Epsilon, 1f,
            MathF.BitDecrement(223.3125f), 223.3125f, MathF.BitIncrement(223.3125f), 268.75f, 512f, 513f, float.MaxValue];
        foreach (float x in edges)
            foreach (float z in edges) Add(x, z);
        foreach (uint word in new uint[] { 0x7f800000, 0xff800000, 0x7fc00000, 0xffc00001 })
        {
            float value = BitConverter.UInt32BitsToSingle(word);
            Add(value, 0f); Add(0f, value); Add(value, value);
        }
        var random = new Random(0x48464945);
        for (int index = 0; index < 128; index++)
            Add((float)(random.NextDouble() * 800.0 - 400.0), (float)(random.NextDouble() * 800.0 - 400.0));
        return result;
    }

    private static A IndexCases()
    {
        Type type = typeof(LegacyLevel100HeightFieldReference);
        int[] root = (int[])type.GetField("s_rootTileIndices", StaticFields)!.GetValue(null)!;
        int[][] patches = (int[][])type.GetField("s_patchTileIndexVariants", StaticFields)!.GetValue(null)!;
        A result = new();
        using (D row = new() { ["geometry_level"] = -1, ["edge_flags"] = 0, ["indices"] = root }) Append(result, row);
        for (int level = 0; level < 3; level++)
            for (int edges = 0; edges < 16; edges++)
            {
                using D row = new() { ["geometry_level"] = level, ["edge_flags"] = edges,
                    ["indices"] = patches[level * 16 + edges] };
                Append(result, row);
            }
        return result;
    }

    private static D Metadata(LegacyLevel100HeightFieldReference field) => new()
    {
        ["player_start_x"] = FloatWord(LegacyLevel100HeightFieldReference.PlayerStartX),
        ["player_start_z"] = FloatWord(LegacyLevel100HeightFieldReference.PlayerStartZ),
        ["player_start_elevation"] = FloatWord(LegacyLevel100HeightFieldReference.PlayerStartElevation),
        ["mixer_set"] = field.MixerSet, ["sky_cube"] = field.SkyCube, ["detail_texture"] = field.DetailTexture,
        ["water_level"] = FloatWord(field.WaterLevel), ["water_relative_height"] = FloatWord(field.WaterRelativeHeight),
        ["water_texture"] = field.WaterTexture, ["fog_color"] = Words(field.FogColor),
        ["fog_density"] = FloatWord(field.FogDensity), ["sun_color"] = Words(field.SunColor),
        ["anti_sun_color"] = Words(field.AntiSunColor), ["ambient_color"] = Words(field.AmbientColor),
        ["sun_color_rgb24"] = field.SunColorRgb24, ["anti_sun_color_rgb24"] = field.AntiSunColorRgb24,
        ["ambient_color_rgb24"] = field.AmbientColorRgb24,
        ["sun_position"] = Words(field.SunPosition), ["sunlight_direction"] = Words(field.SunlightDirection),
    };

    private static D State(LegacyLevel100HeightFieldReference field)
    {
        Type type = typeof(LegacyLevel100HeightFieldReference);
        return new D
        {
            ["smoothed_camera"] = Words((Vector3)type.GetField("_smoothedCamera", InstanceFields)!.GetValue(field)!),
            ["smoothed_forward"] = Words((Vector3)type.GetField("_smoothedForward", InstanceFields)!.GetValue(field)!),
            ["has_smoothed_camera"] = (bool)type.GetField("_hasSmoothedCamera", InstanceFields)!.GetValue(field)!,
            ["signature"] = unchecked((long)(ulong)type.GetField("_meshSignature", InstanceFields)!.GetValue(field)!),
            ["vertex_count"] = field.VertexCount, ["triangle_count"] = field.TriangleCount,
        };
    }

    private static D MeshWords(ArrayMesh mesh)
    {
        using A arrays = mesh.SurfaceGetArrays(0);
        using Variant vertices = arrays[(int)Mesh.ArrayType.Vertex];
        using Variant uv = arrays[(int)Mesh.ArrayType.TexUV];
        using Variant uv2 = arrays[(int)Mesh.ArrayType.TexUV2];
        using Variant indices = arrays[(int)Mesh.ArrayType.Index];
        return new D { ["surface_count"] = mesh.GetSurfaceCount(), ["primitive"] = (int)mesh.SurfaceGetPrimitiveType(0),
            ["vertices"] = vertices.AsVector3Array().SelectMany(Words).ToArray(),
            ["uv"] = uv.AsVector2Array().SelectMany(Words).ToArray(),
            ["uv2"] = uv2.AsVector2Array().SelectMany(Words).ToArray(), ["indices"] = indices.AsInt32Array() };
    }

    private static ArrayMesh SeedMesh()
    {
        var mesh = new ArrayMesh();
        using A arrays = new();
        arrays.Resize((int)Mesh.ArrayType.Max);
        arrays[(int)Mesh.ArrayType.Vertex] = new[] { Vector3.Zero, Vector3.Right, Vector3.Forward };
        arrays[(int)Mesh.ArrayType.Index] = new[] { 0, 1, 2 };
        mesh.AddSurfaceFromArrays(Mesh.PrimitiveType.Triangles, arrays);
        return mesh;
    }

    private static void Append(A array, D value)
    {
        using Variant item = value;
        array.Add(item);
    }
    private static D FloatWord(float value) => new() { ["float_bits"] = Word(value) };
    private static int Word(float value) => BitConverter.SingleToInt32Bits(value);
    private static int[] Words(Vector3 value) => [Word(value.X), Word(value.Y), Word(value.Z)];
    private static int[] Words(Vector2 value) => [Word(value.X), Word(value.Y)];
    private static int[] Words(Color value) => [Word(value.R), Word(value.G), Word(value.B), Word(value.A)];
    private static Vector3 Vector(Level100RenderVector3 value) => new(value.X, value.Y, value.Z);
    private static string Hex(byte[] value) => Convert.ToHexString(SHA256.HashData(value)).ToLowerInvariant();

    private static bool ObjectFree(Variant value)
    {
        if (value.VariantType == Variant.Type.Object) return false;
        if (value.VariantType == Variant.Type.Array)
        {
            using A array = value.AsGodotArray();
            for (int index = 0; index < array.Count; index++)
            {
                using Variant item = array[index];
                if (!ObjectFree(item)) return false;
            }
        }
        else if (value.VariantType == Variant.Type.Dictionary)
        {
            using D dictionary = value.AsGodotDictionary();
            ICollection<Variant> keys = dictionary.Keys;
            using IDisposable? keyCollection = keys as IDisposable;
            foreach (Variant key in keys)
            {
                using (key)
                using (Variant item = dictionary[key])
                    if (!ObjectFree(key) || !ObjectFree(item)) return false;
            }
        }
        return true;
    }

    private string Owned(string path)
    {
        string result = Path.GetFullPath(path);
        string owned = Path.GetFullPath(Path.Combine(ProjectSettings.GlobalizePath("res://"), "..", "..", "local-data"));
        Check(path == result && result.StartsWith(owned + Path.DirectorySeparatorChar, StringComparison.Ordinal) &&
            Directory.Exists(Path.GetDirectoryName(result)) && !File.Exists(result), "Output is a fresh absolute worktree-local path.");
        string part = owned;
        foreach (string segment in Path.GetRelativePath(owned, result).Split(Path.DirectorySeparatorChar))
        {
            part = Path.Combine(part, segment);
            Check(new FileInfo(part).LinkTarget is null, "Output paths never traverse links.");
        }
        return result;
    }

    private void Check(bool value, string message)
    {
        _checks++;
        if (!value) throw new InvalidOperationException(message);
    }
}
