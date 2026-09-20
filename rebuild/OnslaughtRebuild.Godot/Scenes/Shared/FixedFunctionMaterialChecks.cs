// SPDX-License-Identifier: GPL-3.0-or-later
using System.Reflection;
using System.Security.Cryptography;
using Godot;
using A = Godot.Collections.Array;
using D = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

/// <summary>Actual old Godot-hosted material fixtures. Pixels are synthetic;
/// the existing HFLD is read only for its original light/fog metadata.</summary>
public sealed partial class FixedFunctionMaterialChecks : Node
{
    private const BindingFlags HiddenStatic = BindingFlags.Static | BindingFlags.NonPublic;
    private static readonly string[] TextureNames = ["base_texture", "dot3_texture", "reflection_texture", "overlay_texture"];
    private static readonly string[] ValueNames = ["has_dot3", "has_reflection", "has_overlay", "base_blend_texture_alpha",
        "alpha_reference", "stage_zero_gain", "dot3_offset", "dot3_scale", "reflection_factor_alpha", "overlay_offset",
        "overlay_scale", "overlay_opacity", "ambient_color", "sun_color", "anti_sun_color", "sunlight_direction",
        "fog_color", "fog_density", "maximum_horizontal_distance_squared"];
    private int _checks;

    public override async void _Ready()
    {
        LegacyLevel100HeightFieldReference? terrain = null;
        Texture2D[] textures = [];
        Node3D? scene = null;
        try
        {
            string[] args = OS.GetCmdlineUserArgs();
            Check(args.Length == 2, "Two fresh owned output paths are required.");
            string fixturePath = Owned(args[0]), reportPath = Owned(args[1]);
            Check(fixturePath != reportPath && !Engine.IsEditorHint() && DisplayServer.GetName() == "headless", "Reference is distinct outputs and headless runtime only.");
            Input.MouseModeEnum pointer = Input.MouseMode;
            terrain = LegacyLevel100HeightFieldReference.Load();
            string terrainPath = Path.GetFullPath(Path.Combine(ProjectSettings.GlobalizePath("res://"), "..", "OnslaughtRebuild.Core", "Assets", "Level100", "level100-heightfield.hfld.bin"));
            string inputHash = Hex(File.ReadAllBytes(terrainPath));
            A images = [];
            textures = Enumerable.Range(0, 4).Select(index => {
                byte[] pixels = Enumerable.Range(0, 64).Select(value => unchecked((byte)(value * (index * 2 + 3) + index * 47))).ToArray();
                using Image image = Image.CreateFromData(4, 4, false, Image.Format.Rgba8, pixels);
                images.Add(new D { ["width"] = 4, ["height"] = 4, ["format"] = (int)Image.Format.Rgba8,
                    ["mips"] = false, ["bytes"] = pixels, ["sha256"] = Hex(pixels) });
                return (Texture2D)ImageTexture.CreateFromImage(image);
            }).ToArray();
            A cases = [];
            Shader? sharedShader = null;
            void Case(string name, LegacyRetailTextureLayer?[]? layers, float distance = 0f,
                float alpha = 0.5f, int operation = 5, LegacyRetailMeshLightRig? rig = null, bool nullTerrain = false)
            {
                D row = new() { ["name"] = name, ["layers"] = LayerInputs(layers, textures), ["facts"] = nullTerrain ? default(Variant) : Variant.From(Facts(terrain)),
                    ["distance"] = Word(distance), ["alpha"] = Word(alpha), ["operation"] = operation,
                    ["rig"] = rig is null ? default(Variant) : Variant.From(Rig(rig.Value)) };
                ShaderMaterial? material = null;
                try {
                    material = LegacyRetailFixedFunctionMaterial.Create(layers!, nullTerrain ? null! : terrain,
                        distance, alpha, (LegacyRetailStageZeroColorOperation)operation, rig);
                    row["result"] = new D { ["ok"] = true };
                }
                catch (Exception error) { row["result"] = Failure(error); }
                if (material is not null)
                {
                    try
                    {
                        row["material"] = MaterialFacts(material, textures);
                        sharedShader ??= material.Shader;
                        Check(ReferenceEquals(sharedShader, material.Shader), "All returned materials share the original one shader.");
                    }
                    finally { material.Dispose(); }
                }
                cases.Add(row);
            }
            LegacyRetailTextureLayer Layer(int texture, float opacity = 1f, bool blend = false) => new(
                texture < 0 ? null! : textures[texture], opacity, new Vector2(0.125f, -0.25f), new Vector2(2f, -0.5f), blend);
            foreach (int operation in new[] { 4, 5 })
                foreach (bool blend in new[] { false, true })
                    for (int mask = 0; mask < 8; mask++) {
                        var layers = new LegacyRetailTextureLayer?[] { Layer(0, float.NaN, blend),
                            (mask & 1) != 0 ? Layer(1, float.PositiveInfinity) : null,
                            (mask & 2) != 0 ? Layer(2, 0.299999982f) : null,
                            Layer(3, float.NaN), (mask & 4) != 0 ? Layer(3, 0.625f) : null, Layer(1, float.NegativeInfinity) };
                        Case($"layers-{operation}-{blend}-{mask}", layers, rig: mask % 2 == 0 ? null : LegacyRetailMeshLightRig.ClosePine(terrain));
                    }
            var full = new LegacyRetailTextureLayer?[] { Layer(0), Layer(1), Layer(2), null, Layer(3), null };
            foreach (float distance in new[] { -0f, float.Epsilon, 1f, 47.25f, MathF.BitDecrement(MathF.Sqrt(float.MaxValue)), float.MaxValue,
                -float.Epsilon, -1f, float.NaN, float.PositiveInfinity, float.NegativeInfinity })
                Case("distance-" + Word(distance), full, distance, operation: 4);
            foreach (float alpha in new[] { -0f, float.Epsilon, 8f / 255f, 0.5f, 1f, MathF.BitIncrement(1f), -float.Epsilon, float.NaN, float.PositiveInfinity })
                Case("alpha-" + Word(alpha), full, alpha: alpha);
            foreach (int operation in new[] { int.MinValue, -1, 0, 3, 6, int.MaxValue }) Case("operation-" + operation, full, operation: operation);
            Case("null-layers-first", null, float.NaN, float.NaN, -1, nullTerrain: true);
            Case("empty-layers-first", [], float.NaN, float.NaN, -1, nullTerrain: true);
            Case("missing-base-first", new LegacyRetailTextureLayer?[6], float.NaN, float.NaN, -1, nullTerrain: true);
            Case("distance-before-alpha-operation-terrain", full, -1f, float.NaN, -1, nullTerrain: true);
            Case("alpha-before-operation-terrain", full, 1f, float.NaN, -1, nullTerrain: true);
            Case("operation-before-terrain", full, 1f, 0.5f, -1, nullTerrain: true);
            Case("null-terrain-default-rig", full, nullTerrain: true);
            Case("null-terrain-explicit-rig", full, rig: LegacyRetailMeshLightRig.ClosePine(terrain), nullTerrain: true);
            Case("null-textures-presence-flags", [Layer(-1), Layer(-1), Layer(-1), null, Layer(-1), null]);
            Case("null-secondary-textures-use-base", [Layer(0), Layer(-1), Layer(-1), null, Layer(-1), null]);
            var nonfiniteRig = new LegacyRetailMeshLightRig(new Vector3(float.NaN, -0f, float.PositiveInfinity),
                new Vector3(-1f, float.NegativeInfinity, float.Epsilon), Vector3.One, new Vector3(-0f, 2f, -3f));
            Case("unbounded-supplied-rig", full, rig: nonfiniteRig);
            foreach (uint word in new uint[] { 0, 0x80000000, 1, 0x3effffff, 0x3f000000, 0x3f000001, 0x3f800000,
                0xbf800000, 0x4b000000, 0x7f7fffff, 0x7f800000, 0xff800000, 0x7fc00000, 0xffc00041 }) {
                var opacityLayers = full.ToArray();
                opacityLayers[2] = Layer(2, Single(word)); opacityLayers[4] = Layer(3, Single(word));
                Case("opacity-" + word.ToString("x8"), opacityLayers);
            }
            // Preserve arbitrary fog values; this factory never imposes a new
            // finite/range admission on supplied HFLD or explicit light data.
            foreach (uint fogWord in new uint[] { 0, 0x80000000, 0xbf800000, 0x7f800000, 0xffc00041 }) {
                typeof(LegacyLevel100HeightFieldReference).GetField("<FogDensity>k__BackingField", BindingFlags.Instance | BindingFlags.NonPublic)!.SetValue(terrain, Single(fogWord));
                Case("fog-" + fogWord.ToString("x8"), full);
            }
            terrain.Mesh.Dispose(); terrain = LegacyLevel100HeightFieldReference.Load();
            A alphaWords = [];
            MethodInfo alphaMethod = typeof(LegacyRetailFixedFunctionMaterial).GetMethod("ToTextureFactorAlpha", HiddenStatic)!;
            var words = new SortedSet<uint> { 0, 0x80000000, 1, 0x80000001, 0x7f7fffff, 0xff7fffff,
                0x7f800000, 0xff800000, 0x7fc00000, 0xffc00041, 0x4b000000, 0x4b010102, 0xcb010102 };
            for (int value = -1; value <= 256; value++) {
                float middle = (value + 0.5f) / 255f;
                words.Add(BitConverter.SingleToUInt32Bits(MathF.BitDecrement(middle)));
                words.Add(BitConverter.SingleToUInt32Bits(middle));
                words.Add(BitConverter.SingleToUInt32Bits(MathF.BitIncrement(middle)));
                words.Add(BitConverter.SingleToUInt32Bits(value / 255f));
            }
            foreach (uint word in words) alphaWords.Add(new D { ["input"] = (long)word,
                ["output"] = Word((float)alphaMethod.Invoke(null, [Single(word)])!) });
            using ShaderMaterial privateMaterial = LegacyRetailFixedFunctionMaterial.Create(full, terrain);
            scene = BuildScene(privateMaterial);
            AddChild(scene);
            D sceneFacts = SceneFacts(scene, textures);
            string scenePath = Owned(Path.Combine(Path.GetDirectoryName(fixturePath)!, "legacy-material-scene.tscn"));
            using (var packed = new PackedScene()) { Check(packed.Pack(scene) == Error.Ok, "Pack original material scene."); Check(ResourceSaver.Save(packed, scenePath) == Error.Ok, "Save original material scene."); }
            D fixture = new() { ["schema"] = 1, ["completed"] = new A { "fixed_function_material_reference" }, ["textures"] = images,
                ["terrain_path"] = terrainPath, ["input_sha256"] = inputHash, ["cases"] = cases, ["alpha_words"] = alphaWords,
                ["shader"] = (string)typeof(LegacyRetailFixedFunctionMaterial).GetField("ShaderCode", HiddenStatic)!.GetRawConstantValue()!,
                ["scene_path"] = scenePath, ["scene_sha256"] = Hex(File.ReadAllBytes(scenePath)), ["scene_facts"] = sceneFacts,
                ["scene_input"] = new D { ["layers"] = LayerInputs(full, textures), ["facts"] = Facts(terrain), ["distance"] = 0L, ["alpha"] = Word(0.5f), ["operation"] = 5 } };
            Check(Input.MouseMode == pointer, "Reference preserves pointer ownership.");
            Check(Hex(File.ReadAllBytes(terrainPath)) == inputHash, "HFLD input is unchanged.");
            using (var file = Godot.FileAccess.Open(fixturePath, Godot.FileAccess.ModeFlags.Write) ?? throw new IOException("Cannot write fixture.")) file.StoreVar(fixture, false);
            using (var file = Godot.FileAccess.Open(reportPath, Godot.FileAccess.ModeFlags.Write) ?? throw new IOException("Cannot write report."))
                file.StoreString(Json.Stringify(new D { ["schema"] = 1, ["failure_count"] = 0,
                    ["completed"] = new A { "fixed_function_material_reference" }, ["counts"] = new D { ["checks"] = _checks, ["cases"] = cases.Count, ["alpha"] = alphaWords.Count } }));
            scene.Free(); scene = null; terrain.Mesh.Dispose(); terrain = null;
            foreach (Texture2D texture in textures) texture.Dispose(); textures = [];
            GC.Collect(); GC.WaitForPendingFinalizers();
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            GD.Print($"FIXED_FUNCTION_MATERIAL_REFERENCE: {_checks} checks, {cases.Count} materials, {alphaWords.Count} alpha words; {fixturePath}");
            GetTree().Quit(0);
        }
        catch (Exception error) { scene?.Free(); terrain?.Mesh.Dispose(); foreach (Texture2D texture in textures) texture.Dispose(); GD.PushError(error.ToString()); GetTree().Quit(1); }
    }

    private static D Facts(LegacyLevel100HeightFieldReference terrain) => new() { ["ambient_color_rgb24"] = terrain.AmbientColorRgb24,
        ["sun_color_rgb24"] = terrain.SunColorRgb24, ["anti_sun_color_rgb24"] = terrain.AntiSunColorRgb24,
        ["sunlight_direction"] = terrain.SunlightDirection, ["fog_color"] = terrain.FogColor, ["fog_density"] = terrain.FogDensity };
    private static D Rig(LegacyRetailMeshLightRig rig) => new() { ["ambient_color"] = rig.AmbientColor,
        ["key_light_color"] = rig.KeyLightColor, ["fill_light_color"] = rig.FillLightColor, ["key_light_direction"] = rig.KeyLightDirection };
    private static Variant LayerInputs(LegacyRetailTextureLayer?[]? layers, Texture2D[] textures) {
        if (layers is null) return default;
        A result = [];
        foreach (LegacyRetailTextureLayer? layer in layers) result.Add(layer is null ? default(Variant) : Variant.From(new D {
            ["texture"] = Array.FindIndex(textures, texture => ReferenceEquals(texture, layer.Texture)), ["opacity"] = Word(layer.Opacity),
            ["offset"] = layer.Offset, ["scale"] = layer.Scale, ["blend_texture_alpha"] = layer.BlendTextureAlpha }));
        return result;
    }
    private static D MaterialFacts(ShaderMaterial material, Texture2D[] textures) {
        D values = new(), selected = new(), pixels = new();
        foreach (string name in ValueNames) { using Variant value = material.GetShaderParameter(name); values[name] = GD.VarToBytes(value); }
        foreach (string name in TextureNames) { using Variant value = material.GetShaderParameter(name);
            Texture2D? texture = value.VariantType == Variant.Type.Object ? value.AsGodotObject() as Texture2D : null;
            selected[name] = Array.FindIndex(textures, candidate => ReferenceEquals(candidate, texture));
            if (texture is not null) { using Image image = texture.GetImage(); pixels[name] = Hex(image.GetData()); }
        }
        return new D { ["values"] = values, ["textures"] = selected, ["pixels"] = pixels, ["priority"] = material.RenderPriority,
            ["next_pass"] = material.NextPass is null, ["local_to_scene"] = material.ResourceLocalToScene };
    }
    private static Node3D BuildScene(ShaderMaterial material) {
        var root = new Node3D { Name = "MaterialComparison" };
        var mesh = new ArrayMesh(); var arrays = new A(); arrays.Resize((int)Mesh.ArrayType.Max);
        arrays[(int)Mesh.ArrayType.Vertex] = new Vector3[] { new(-1,-1,0), new(1,-1,0), new(0,1,0) };
        arrays[(int)Mesh.ArrayType.Normal] = new Vector3[] { Vector3.Back, Vector3.Back, Vector3.Back };
        arrays[(int)Mesh.ArrayType.TexUV] = new Vector2[] { Vector2.Zero, Vector2.Right, Vector2.Down };
        arrays[(int)Mesh.ArrayType.Color] = new Color[] { Colors.White, new(0.5f,0.5f,0.5f,1f), Colors.White };
        mesh.AddSurfaceFromArrays(Mesh.PrimitiveType.Triangles, arrays);
        foreach (bool mirrored in new[] { false, true }) {
            var node = new MeshInstance3D { Name = mirrored ? "Mirrored" : "Ordinary", Mesh = mesh, MaterialOverride = material,
                Transform = new Transform3D(Basis.FromScale(new Vector3(mirrored ? -1f : 1f, 1f, 1f)), new Vector3(mirrored ? 3f : 0f, 0f, 0f)) };
            root.AddChild(node); node.Owner = root;
        }
        return root;
    }
    private static D SceneFacts(Node3D scene, Texture2D[] textures) {
        D result = new(); foreach (MeshInstance3D node in scene.GetChildren()) {
            using var arrays = ((ArrayMesh)node.Mesh).SurfaceGetArrays(0);
            result[node.Name.ToString()] = new D { ["transform"] = GD.VarToBytes(node.Transform), ["mesh"] = Hex(GD.VarToBytes(arrays)),
                ["shadow"] = (int)node.CastShadow, ["layers"] = node.Layers, ["material"] = MaterialFacts((ShaderMaterial)node.MaterialOverride, textures) };
        } return result;
    }
    private static D Failure(Exception error) => new() { ["ok"] = false, ["error_type"] = error.GetType().Name,
        ["error"] = error.Message, ["parameter"] = error is ArgumentException argument ? argument.ParamName ?? "" : "" };
    private static long Word(float value) => BitConverter.SingleToUInt32Bits(value);
    private static float Single(uint value) => BitConverter.UInt32BitsToSingle(value);
    private static string Hex(byte[] bytes) => Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
    private string Owned(string path) { string full = Path.GetFullPath(path), root = Path.GetFullPath(Path.Combine(ProjectSettings.GlobalizePath("res://"), "..", "..", "local-data")) + Path.DirectorySeparatorChar;
        Check(full.StartsWith(root, StringComparison.Ordinal) && Directory.Exists(Path.GetDirectoryName(full)) && !File.Exists(full), "Output is fresh worktree-local data."); return full; }
    private void Check(bool condition, string message) { _checks++; if (!condition) throw new InvalidOperationException(message); }
}
