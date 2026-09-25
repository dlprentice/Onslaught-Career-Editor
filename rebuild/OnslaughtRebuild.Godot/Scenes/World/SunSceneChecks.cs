// SPDX-License-Identifier: GPL-3.0-or-later
using System.Reflection;
using System.Security.Cryptography;
using Godot;
using OnslaughtRebuild.Client;
using D = Godot.Collections.Dictionary;
using A = Godot.Collections.Array;

namespace OnslaughtRebuild.GodotClient;

/// <summary>Object-free exact fixture from the retained pre-native Sun implementation.</summary>
public sealed partial class SunSceneChecks : Node
{
    private const BindingFlags PrivateInstance = BindingFlags.Instance | BindingFlags.NonPublic;
    private const string MainSetPath = "res://Assets/Level100/ParticleSets/MainSet.par";
    private const string TexturePath = "res://Assets/Level100/Textures/particle-sun3-additive.texture.aya";
    private int _checks;

    public override async void _Ready()
    {
        LegacyLevel100SunReference? sun = null;
        LegacyLevel100HeightFieldReference? terrain = null;
        try
        {
            string[] args = OS.GetCmdlineUserArgs();
            Check(args.Length == 2, "Two explicit fresh owned output paths are required.");
            string fixturePath = Owned(args[0]);
            string reportPath = Owned(args[1]);
            Check(fixturePath != reportPath, "Reference and report paths are distinct.");
            Check(!Engine.IsEditorHint() && DisplayServer.GetName() == "headless", "Reference runs only in a headless runtime.");
            Input.MouseModeEnum pointer = Input.MouseMode;
            string terrainPath = Path.GetFullPath(Path.Combine(ProjectSettings.GlobalizePath("res://"),
                "..", "OnslaughtRebuild.Core", "Assets", "Level100", "level100-heightfield.hfld.bin"));
            D before = InputHashes(terrainPath);
            terrain = LegacyLevel100HeightFieldReference.Load();
            sun = LegacyLevel100SunReference.Create(terrain);
            AddChild(sun.Root);
            Vector3 offset = (Vector3)typeof(LegacyLevel100SunReference).GetField("_offsetFromCamera", PrivateInstance)!.GetValue(sun)!;
            Vector3 direction = (Vector3)typeof(LegacyLevel100SunReference).GetField("_directionFromCamera", PrivateInstance)!.GetValue(sun)!;

            A heights = [];
            A cameras = [];
            void Height(float x, float z) => heights.Add(new D { ["x_bits"] = Word(x), ["z_bits"] = Word(z),
                ["value_bits"] = Word(terrain.SampleRelativeHeight(x, z)) });
            void Camera(Vector3 position)
            {
                sun.Update(position);
                cameras.Add(new D { ["camera"] = VectorWords(position), ["position"] = VectorWords(sun.Root.Position),
                    ["visible"] = sun.Visible });
            }

            float[] edges = [float.MinValue, -513f, -288.6875f, MathF.BitDecrement(-288.6875f), MathF.BitIncrement(-288.6875f),
                -243.25f, -1f, -0f, 0f, float.Epsilon, 1f, 223.3125f, MathF.BitDecrement(223.3125f),
                MathF.BitIncrement(223.3125f), 268.75f, 512f, 513f, float.MaxValue];
            foreach (float x in edges)
                foreach (float z in edges) Height(x, z);
            // SampleRelativeHeight is an existing float API: preserve its
            // NaN/infinity conversion results without assigning nonfinite node transforms.
            foreach (uint bits in new uint[] { 0x7f800000, 0xff800000, 0x7fc00000, 0xffc00001 })
            {
                float value = BitConverter.UInt32BitsToSingle(bits);
                Height(value, 0f); Height(0f, value); Height(value, value);
            }
            float[] cameraEdges = [-600f, -288.6875f, -243.25f, -1f, -0f, 0f, 1f, 223.3125f, 268.75f, 600f];
            foreach (float x in cameraEdges)
                foreach (float z in cameraEdges)
                    foreach (float elevation in new[] { -50f, 0f, 50f }) Camera(new Vector3(x, elevation, z));
            var random = new Random(0x53554e);
            for (int index = 0; index < 512; index++)
            {
                float x = (float)(random.NextDouble() * 700.0 - 350.0);
                float z = (float)(random.NextDouble() * 700.0 - 350.0);
                Height(x, z);
                Camera(new Vector3(x, (float)(random.NextDouble() * 140.0 - 40.0), z));
                // The first march point exactly touches, or lies one float word
                // to either side of, the sampled terrain. Let legacy arithmetic
                // decide the <= branch after all vector stores.
                Vector3 rayStep = direction * 2f;
                float threshold = terrain.SampleRelativeHeight(x + rayStep.X, z + rayStep.Z) - rayStep.Y;
                foreach (float y in new[] { MathF.BitDecrement(threshold), threshold, MathF.BitIncrement(threshold) })
                    Camera(new Vector3(x, y, z));
            }
            Check(cameras.Any(value => value.AsGodotDictionary()["visible"].AsBool()), "Camera fixtures exercise visible sun.");
            Check(cameras.Any(value => !value.AsGodotDictionary()["visible"].AsBool()), "Camera fixtures exercise terrain suppression.");

            var quad = (QuadMesh)sun.Root.Mesh;
            var material = (StandardMaterial3D)sun.Root.MaterialOverride;
            using Image image = material.AlbedoTexture.GetImage();
            D fixture = new() { ["schema"] = 1, ["completed"] = new A { "sun_reference" },
                ["terrain_path"] = terrainPath, ["input_hashes"] = before,
                ["offset"] = VectorWords(offset), ["direction"] = VectorWords(direction),
                ["definition"] = Layer(sun.Layer), ["height_cases"] = heights, ["camera_cases"] = cameras,
                ["constant_colours"] = Colours(sun.Layer), ["mesh"] = Properties(quad),
                ["material"] = Properties(material), ["cast_shadow"] = (int)sun.Root.CastShadow,
                ["texture"] = new D { ["size"] = image.GetSize(), ["format"] = (int)image.GetFormat(),
                    ["mipmaps"] = image.HasMipmaps(), ["sha256"] = Hex(image.GetData()) } };
            Check(Input.MouseMode == pointer, "Reference never changes pointer ownership.");
            D after = InputHashes(terrainPath);
            foreach (Variant key in before.Keys) Check(before[key].AsString() == after[key].AsString(), "Read-only Sun input remains unchanged.");
            using (var output = Godot.FileAccess.Open(fixturePath, Godot.FileAccess.ModeFlags.Write)
                ?? throw new IOException("Cannot create Sun reference fixture.")) output.StoreVar(fixture, false);
            using (var output = Godot.FileAccess.Open(reportPath, Godot.FileAccess.ModeFlags.Write)
                ?? throw new IOException("Cannot create Sun reference report."))
                output.StoreString(Json.Stringify(new D { ["schema"] = 1, ["failure_count"] = 0,
                    ["counts"] = new D { ["reference"] = _checks, ["height_cases"] = heights.Count, ["camera_cases"] = cameras.Count },
                    ["completed"] = new A { "sun_reference" } }));
            sun.Root.QueueFree(); sun = null;
            terrain.Mesh.Dispose(); terrain = null;
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            GD.Print($"SUN_REFERENCE_CHECKS: {_checks} passed; {heights.Count} height and {cameras.Count} camera cases; fresh fixture {fixturePath}");
            GetTree().Quit(0);
        }
        catch (Exception error)
        {
            sun?.Root.Free();
            terrain?.Mesh.Dispose();
            GD.PushError(error.ToString());
            GetTree().Quit(1);
        }
    }

    private static A Colours(ParticleSpriteLayer template)
    {
        A result = [];
        MethodInfo method = typeof(LegacyLevel100SunReference).GetMethod("ResolveConstantColour", BindingFlags.NonPublic | BindingFlags.Static)!;
        void Add(string name, ParticleColourRange? range)
        {
            ParticleSpriteLayer layer = template with { ColourRange = range };
            D expected;
            try { expected = new D { ["ok"] = true, ["value"] = ColourWords((Color)method.Invoke(null, [layer])!) }; }
            catch (TargetInvocationException error) { expected = new D { ["ok"] = false, ["error_type"] = error.InnerException!.GetType().Name }; }
            result.Add(new D { ["name"] = name, ["range"] = range is { } value ? Range(value) : default(Variant), ["expected"] = expected });
        }
        Add("absent", null);
        Add("actual shipped colour", template.ColourRange);
        var basic = new ParticleColourRange("test colour", (0.25f, 0.5f, 0.75f), (0.25f, 0.5f, 0.75f), (1f, 0f, 1f), true, false, 0.5f);
        Add("constant", basic);
        Add("unrecovered transition", basic with { UseTransition = true });
        Add("unrecovered end", basic with { End = (0.5f, 0.5f, 0.75f) });
        Add("unused end", basic with { End = (1f, 0f, 0f), UseEnd = false });
        Add("signed zeros equal", basic with { Start = (-0f, 0f, -0f), End = (0f, -0f, 0f) });
        foreach (uint word in new uint[] { 0, 0x80000000, 1, 0x80000001, 0x3f800000, 0xbf800000,
            0x7f7fffff, 0xff7fffff, 0x7f800000, 0xff800000, 0x7fc00000, 0xffc00001 })
        {
            float value = BitConverter.UInt32BitsToSingle(word);
            Add("equal-word-" + word, basic with { Start = (value, value, value), End = (value, value, value) });
            Add("unused-word-" + word, basic with { Start = (value, value, value), UseEnd = false });
        }
        return result;
    }

    private static D Layer(ParticleSpriteLayer layer) => new() {
        ["descriptor_name"] = Raw(layer.DescriptorName), ["path"] = Raw(layer.Path), ["texture_name"] = Raw(layer.TextureName),
        ["blend_mode"] = layer.BlendMode, ["atlas_columns"] = layer.AtlasColumns, ["atlas_rows"] = layer.AtlasRows,
        ["start_cell"] = layer.StartCell, ["end_cell"] = layer.EndCell, ["animation_mode"] = (int)layer.AnimationMode,
        ["animation_cells_per_turn_bits"] = Word(layer.AnimationCellsPerTurn), ["random_start_cell"] = layer.RandomStartCell,
        ["life_turns"] = layer.LifeTurns, ["start_radius_bits"] = Word(layer.StartRadius), ["final_radius_bits"] = Word(layer.FinalRadius),
        ["life_fraction_bits"] = Word(layer.LifeFraction), ["fade_colour"] = layer.FadeColour, ["axis_aligned"] = layer.AxisAligned,
        ["gravity"] = layer.Gravity, ["velocity_damp_bits"] = Word(layer.VelocityDamp),
        ["colour_range"] = layer.ColourRange is { } colour ? Range(colour) : default(Variant),
        ["instance_count"] = layer.InstanceCount, ["start_turns"] = new A(layer.StartTurns.Select(value => Variant.From(value))),
        ["shape"] = default(Variant), ["initial_velocity"] = new D { ["x_bits"] = Word(layer.InitialVelocity.X),
            ["y_bits"] = Word(layer.InitialVelocity.Y), ["z_bits"] = Word(layer.InitialVelocity.Z) },
        ["outward_velocity_bits"] = Word(layer.OutwardVelocity), ["velocity_randomness_bits"] = Word(layer.VelocityRandomness) };

    private static D Range(ParticleColourRange colour) => new() { ["name"] = Raw(colour.Name),
        ["start"] = Rgb(colour.Start), ["end"] = Rgb(colour.End), ["transition"] = Rgb(colour.Transition),
        ["use_end"] = colour.UseEnd, ["use_transition"] = colour.UseTransition, ["transition_point_bits"] = Word(colour.TransitionPoint) };
    private static D Rgb((float R, float G, float B) colour) => new() { ["r_bits"] = Word(colour.R), ["g_bits"] = Word(colour.G), ["b_bits"] = Word(colour.B) };

    private static D Properties(Resource resource)
    {
        D result = new();
        foreach (D property in resource.GetPropertyList())
        {
            if (((PropertyUsageFlags)property["usage"].AsInt64() & PropertyUsageFlags.Storage) == 0) continue;
            string name = property["name"].AsString();
            if (name is "resource_local_to_scene" or "resource_name" or "script") continue;
            Variant value = resource.Get(name);
            if (value.VariantType == Variant.Type.Object)
            {
                if (value.AsGodotObject() is not null && value.AsGodotObject() is not Texture2D)
                    throw new InvalidOperationException("Unexpected Sun resource property: " + name);
                result[name] = value.AsGodotObject() is Texture2D ? "Texture2D" : default(Variant);
            }
            else result[name] = EncodeProperty(value);
        }
        return result;
    }

    private static Variant EncodeProperty(Variant value) => value.VariantType switch
    {
        Variant.Type.Float => new D { ["float_bits"] = Word(value.AsSingle()) },
        Variant.Type.Color => new D { ["colour_bits"] = ColourWords(value.AsColor()) },
        Variant.Type.Vector2 => new D { ["vector_bits"] = new long[] { Word(value.AsVector2().X), Word(value.AsVector2().Y) } },
        Variant.Type.Vector3 => new D { ["vector_bits"] = VectorWords(value.AsVector3()) },
        _ => value
    };

    private static D InputHashes(string terrainPath) => new() { [MainSetPath] = Hex(Godot.FileAccess.GetFileAsBytes(MainSetPath)),
        [TexturePath] = Hex(Godot.FileAccess.GetFileAsBytes(TexturePath)), [terrainPath] = Hex(File.ReadAllBytes(terrainPath)) };
    private static string Hex(byte[] bytes) => Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
    private static long Word(float value) => BitConverter.SingleToUInt32Bits(value);
    private static long[] VectorWords(Vector3 value) => [Word(value.X), Word(value.Y), Word(value.Z)];
    private static long[] ColourWords(Color value) => [Word(value.R), Word(value.G), Word(value.B), Word(value.A)];
    private static int[] Raw(string value) => value.Select(character => (int)character).ToArray();

    private string Owned(string path)
    {
        string result = Path.GetFullPath(path);
        string root = Path.GetFullPath(Path.Combine(ProjectSettings.GlobalizePath("res://"), "..", "..", "local-data")) + Path.DirectorySeparatorChar;
        Check(result.StartsWith(root, StringComparison.Ordinal) && Directory.Exists(Path.GetDirectoryName(result)) && !File.Exists(result),
            "Output must be a fresh explicit path in this worktree's local-data.");
        return result;
    }

    private void Check(bool condition, string message)
    {
        _checks++;
        if (!condition) throw new InvalidOperationException(message);
    }
}
