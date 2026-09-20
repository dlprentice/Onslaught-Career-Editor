// SPDX-License-Identifier: GPL-3.0-or-later
using System.Reflection;
using System.Security.Cryptography;
using Godot;
using D = Godot.Collections.Dictionary;
using A = Godot.Collections.Array;

namespace OnslaughtRebuild.GodotClient;

/// <summary>Object-free fixtures from the exact pre-native water and heightfield owners.</summary>
public sealed partial class WaterSceneChecks : Node
{
    private const BindingFlags PrivateInstance = BindingFlags.Instance | BindingFlags.NonPublic;
    private const string SurfacePath = "res://Assets/Level100/StaticWorld/Source/level100-water-surface.surf.bin";
    private const string SurfaceHash = "C3177354FED3EB5A94DC72DEBF2465C32AB1D931DE79E5E88AC431043D3E917D";
    private static readonly string[] Children = ["RetailCameraRelativeWaterGrid", "RetailAuthoredShorelineBands", "RetailCameraRelativeWaterSunGlint"];
    private static readonly (string Uniform, string File, int Width, int Height, CuratedAyaTextureLoader.Compression Compression)[] Textures = [
        ("reflection_texture", "water-reflection-00.texture.aya", 512, 512, CuratedAyaTextureLoader.Compression.Dxt1),
        ("caustic_texture", "water-caustic-00.texture.aya", 64, 64, CuratedAyaTextureLoader.Compression.Dxt1),
        ("waves_texture", "water-waves.texture.aya", 128, 128, CuratedAyaTextureLoader.Compression.Dxt1),
        ("sun_blob_texture", "water-sun-blob.texture.aya", 128, 128, CuratedAyaTextureLoader.Compression.Rgba8),
        ("sun_reflection_texture", "water-sun-reflection.texture.aya", 64, 64, CuratedAyaTextureLoader.Compression.Rgba8) ];
    private int _checks;

    public override async void _Ready()
    {
        LegacyLevel100WaterReference? water = null;
        LegacyLevel100HeightFieldReference? terrain = null;
        try
        {
            string[] args = OS.GetCmdlineUserArgs();
            Check(args.Length == 2, "Two fresh explicit owned output paths are required.");
            string fixturePath = Owned(args[0]);
            string reportPath = Owned(args[1]);
            Check(fixturePath != reportPath, "Reference and report paths are distinct.");
            Check(!Engine.IsEditorHint() && DisplayServer.GetName() == "headless", "Reference runs only in a headless runtime.");
            Input.MouseModeEnum pointer = Input.MouseMode;
            string terrainPath = Path.GetFullPath(Path.Combine(ProjectSettings.GlobalizePath("res://"), "..",
                "OnslaughtRebuild.Core", "Assets", "Level100", "level100-heightfield.hfld.bin"));
            D hashes = InputHashes(terrainPath);
            terrain = LegacyLevel100HeightFieldReference.Load();
            var textures = Textures.Select(spec => CuratedAyaTextureLoader.Load(TexturePath(spec.File), spec.Width, spec.Height, spec.Compression)).ToArray();
            water = LegacyLevel100WaterReference.Create(terrain, textures[0], textures[1], textures[2], textures[3], textures[4], SurfacePath, SurfaceHash);
            AddChild(water.Root);
            D visual = Visual(water.Root);
            D initial = Snapshot(water);
            A steps = [];
            void Update(Vector3 camera, float delta)
            {
                water.Update(camera, delta);
                steps.Add(new D { ["kind"] = "update", ["camera"] = VectorWords(camera), ["delta_bits"] = Word(delta), ["expected"] = Snapshot(water) });
            }
            void Bind()
            {
                water = LegacyLevel100WaterReference.BindScene(water.Root, terrain);
                steps.Add(new D { ["kind"] = "bind", ["expected"] = Snapshot(water) });
            }
            float[] heights = [-50f, MathF.BitDecrement(terrain.WaterRelativeHeight), terrain.WaterRelativeHeight,
                MathF.BitIncrement(terrain.WaterRelativeHeight), -0f, 0f, 1f, 5f, 90f];
            foreach (float height in heights)
                foreach (uint bits in new uint[] { 0, 0x80000000, 1, 0x80000001, 0x3d75c28f, 0x3c888889,
                    0x3f800000, 0xbf800000, 0x40c90fda, 0x40c90fdb, 0x40c90fdc, 0x7f7fffff,
                    0x7f800000, 0xff800000, 0x7fc00000, 0xffc00001 })
                    Update(new Vector3(25f, height, -100f), BitConverter.UInt32BitsToSingle(bits));
            Bind();
            Update(new Vector3(-0f, -5f, -0f), -0f);
            var random = new Random(0x57415445);
            for (int index = 0; index < 1024; index++)
            {
                if (index % 257 == 256) Bind();
                Update(new Vector3((float)(random.NextDouble() * 1000 - 500),
                    (float)(random.NextDouble() * 160 - 50), (float)(random.NextDouble() * 1000 - 500)),
                    (float)(random.NextDouble() * 0.16));
            }
            // Probe the exact private C# geometry admission without modifying or
            // copying any input. Synthetic files are fresh and task-owned.
            A admission = [];
            MethodInfo build = typeof(LegacyLevel100WaterReference).GetMethod("BuildShorelineMesh", BindingFlags.NonPublic | BindingFlags.Static)!;
            foreach (int length in new[] { 0, 1, 18571, 18572, 18573 })
            {
                string path = Owned(Path.Combine(Path.GetDirectoryName(fixturePath)!, $"synthetic-shoreline-{length}.bin"));
                File.WriteAllBytes(path, new byte[length]);
                try
                {
                    using var unexpected = (ArrayMesh)build.Invoke(null, [path, SurfaceHash])!;
                    throw new InvalidOperationException("Synthetic shoreline unexpectedly admitted.");
                }
                catch (TargetInvocationException error)
                {
                    admission.Add(new D { ["length"] = length, ["path"] = path, ["sha256"] = Hex(File.ReadAllBytes(path)),
                        ["error_type"] = error.InnerException!.GetType().Name, ["error"] = error.InnerException.Message });
                }
            }
            D textureFacts = new();
            for (int index = 0; index < textures.Length; index++)
            {
                using Image image = textures[index].GetImage();
                textureFacts[Textures[index].Uniform] = ImageFacts(image);
            }
            D fixture = new() { ["schema"] = 1, ["completed"] = new A { "water_reference" },
                ["terrain_path"] = terrainPath, ["input_hashes"] = hashes, ["visual"] = visual,
                ["initial"] = initial, ["steps"] = steps, ["admission"] = admission,
                ["textures"] = textureFacts, ["counts"] = new D { ["grid_vertices"] = water.GridVertexCount,
                    ["grid_triangles"] = water.GridTriangleCount, ["shoreline_triangles"] = water.ShorelineTriangleCount } };
            Check(Input.MouseMode == pointer, "Reference does not change pointer ownership.");
            D after = InputHashes(terrainPath);
            foreach (Variant key in hashes.Keys) Check(hashes[key].AsString() == after[key].AsString(), "Read-only water input is unchanged.");
            using (var output = Godot.FileAccess.Open(fixturePath, Godot.FileAccess.ModeFlags.Write)
                ?? throw new IOException("Cannot write water reference.")) output.StoreVar(fixture, false);
            using (var output = Godot.FileAccess.Open(reportPath, Godot.FileAccess.ModeFlags.Write)
                ?? throw new IOException("Cannot write water reference report."))
                output.StoreString(Json.Stringify(new D { ["schema"] = 1, ["failure_count"] = 0,
                    ["counts"] = new D { ["reference"] = _checks, ["steps"] = steps.Count }, ["completed"] = new A { "water_reference" } }));
            water.Root.QueueFree(); water = null;
            terrain.Mesh.Dispose(); terrain = null;
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            GD.Print($"WATER_REFERENCE_CHECKS: {_checks} passed; {steps.Count} ordered operations; {fixturePath}");
            GetTree().Quit(0);
        }
        catch (Exception error)
        {
            water?.Root.Free(); terrain?.Mesh.Dispose();
            GD.PushError(error.ToString()); GetTree().Quit(1);
        }
    }

    private static D Snapshot(LegacyLevel100WaterReference water)
    {
        T Field<T>(string name) => (T)typeof(LegacyLevel100WaterReference).GetField(name, PrivateInstance)!.GetValue(water)!;
        D children = new();
        foreach (string name in Children)
        {
            MeshInstance3D node = water.Root.GetNode<MeshInstance3D>(name);
            var material = (ShaderMaterial)node.MaterialOverride;
            D phases = new();
            foreach (D parameter in material.Shader.GetShaderUniformList())
            {
                string key = parameter["name"].AsString();
                if (key is "caustic_phase" or "main_wave_scroll" or "glint_phase")
                    phases[key] = Word(material.GetShaderParameter(key).AsSingle());
            }
            children[name] = new D { ["position"] = VectorWords(node.Position), ["rotation"] = VectorWords(node.Rotation),
                ["scale"] = VectorWords(node.Scale), ["phases"] = phases };
        }
        return new D { ["caustic_phase"] = Word(Field<float>("_causticPhase")), ["main_wave_scroll"] = Word(Field<float>("_mainWaveScroll")),
            ["water_height"] = Word(Field<float>("_waterHeight")), ["direction"] = VectorWords(Field<Vector3>("_sunGlintOffsetDirection")), ["children"] = children };
    }

    private static D Visual(Node3D root)
    {
        D children = new();
        foreach (string name in Children)
        {
            MeshInstance3D node = root.GetNode<MeshInstance3D>(name);
            var material = (ShaderMaterial)node.MaterialOverride;
            A surfaces = [];
            for (int index = 0; index < node.Mesh.GetSurfaceCount(); index++)
            {
                using A arrays = node.Mesh.SurfaceGetArrays(index);
                surfaces.Add(new D { ["arrays"] = arrays, ["sha256"] = Hex(GD.VarToBytes(arrays)),
                    ["primitive"] = (int)((ArrayMesh)node.Mesh).SurfaceGetPrimitiveType(index), ["format"] = node.Mesh.Call("surface_get_format", index).AsInt64() });
            }
            D parameters = new();
            foreach (D parameter in material.Shader.GetShaderUniformList())
            {
                string key = parameter["name"].AsString();
                Variant value = material.GetShaderParameter(key);
                parameters[key] = value.VariantType switch {
                    Variant.Type.Float => new D { ["float_bits"] = Word(value.AsSingle()) },
                    Variant.Type.Vector2 => new D { ["vector_bits"] = new long[] { Word(value.AsVector2().X), Word(value.AsVector2().Y) } },
                    Variant.Type.Vector3 => new D { ["vector_bits"] = VectorWords(value.AsVector3()) },
                    Variant.Type.Object => "Texture2D", _ => value };
            }
            children[name] = new D { ["surfaces"] = surfaces, ["priority"] = material.RenderPriority,
                ["cast_shadow"] = (int)node.CastShadow, ["parameters"] = parameters, ["shader"] = material.Shader.Code };
        }
        return children;
    }

    private static D ImageFacts(Image image) => new() { ["size"] = image.GetSize(), ["format"] = (int)image.GetFormat(), ["mipmaps"] = image.HasMipmaps(), ["sha256"] = Hex(image.GetData()) };
    private static D InputHashes(string terrainPath)
    {
        D result = new() { [SurfacePath] = Hex(Godot.FileAccess.GetFileAsBytes(SurfacePath)), [terrainPath] = Hex(File.ReadAllBytes(terrainPath)) };
        foreach (var texture in Textures) result[TexturePath(texture.File)] = Hex(Godot.FileAccess.GetFileAsBytes(TexturePath(texture.File)));
        return result;
    }
    private static string TexturePath(string file) => "res://Assets/Level100/StaticWorld/Textures/" + file;
    private static string Hex(byte[] source) => Convert.ToHexString(SHA256.HashData(source)).ToLowerInvariant();
    private static long Word(float value) => BitConverter.SingleToUInt32Bits(value);
    private static long[] VectorWords(Vector3 value) => [Word(value.X), Word(value.Y), Word(value.Z)];
    private string Owned(string path)
    {
        string result = Path.GetFullPath(path);
        string root = Path.GetFullPath(Path.Combine(ProjectSettings.GlobalizePath("res://"), "..", "..", "local-data")) + Path.DirectorySeparatorChar;
        Check(result.StartsWith(root, StringComparison.Ordinal) && Directory.Exists(Path.GetDirectoryName(result)) && !File.Exists(result), "Output must be fresh and under this worktree's local-data.");
        return result;
    }
    private void Check(bool condition, string message) { _checks++; if (!condition) throw new InvalidOperationException(message); }
}
