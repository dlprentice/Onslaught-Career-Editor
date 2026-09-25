// SPDX-License-Identifier: GPL-3.0-or-later
using System.Reflection;
using System.Security.Cryptography;
using Godot;
using A = Godot.Collections.Array;
using D = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

/// <summary>Object-free fixtures from the retained appearance, compositor and
/// heightfield implementations. No private asset is copied into the fixture.</summary>
public sealed partial class TerrainAppearanceSceneChecks : Node
{
    private const BindingFlags Fields = BindingFlags.Instance | BindingFlags.NonPublic;
    private const string RootPath = "res://Assets/Level100/Source/level100-root-terrain.rgb565.bin";
    private const string HierarchyPath = "res://Assets/Level100/Source/level100-terrain-hierarchy.bin";
    private const string DetailPath = "res://Assets/Level100/Textures/terrain-detail-00.texture.aya";
    private const string CloudPath = "res://Assets/Level100/Textures/terrain-cloud-shadow.texture.aya";
    private int _checks;

    public override async void _Ready()
    {
        LegacyLevel100HeightFieldReference? field = null;
        LegacyLevel100TerrainAppearanceReference? appearance = null;
        string previousProbe = OS.GetEnvironment("ONSLAUGHT_TERRAIN_PROBE");
        bool hadProbe = OS.HasEnvironment("ONSLAUGHT_TERRAIN_PROBE");
        try
        {
            string[] args = OS.GetCmdlineUserArgs();
            Check(args.Length == 2, "Two fresh owned output paths are required.");
            string fixturePath = Owned(args[0]), reportPath = Owned(args[1]);
            Check(fixturePath != reportPath, "Fixture and report paths differ.");
            Check(!Engine.IsEditorHint() && DisplayServer.GetName() == "headless", "Reference is headless runtime only.");
            Input.MouseModeEnum pointer = Input.MouseMode;
            OS.UnsetEnvironment("ONSLAUGHT_TERRAIN_PROBE");
            string terrainPath = Path.GetFullPath(Path.Combine(ProjectSettings.GlobalizePath("res://"), "..",
                "OnslaughtRebuild.Core", "Assets", "Level100", "level100-heightfield.hfld.bin"));
            D paths = new() { ["root"] = RootPath, ["hierarchy"] = HierarchyPath, ["detail"] = DetailPath,
                ["cloud"] = CloudPath, ["terrain"] = terrainPath };
            D hashes = Hashes(paths);
            field = LegacyLevel100HeightFieldReference.Load();
            D facts = Facts(field);
            A scenarios = [];
            void Scenario(string name, Action<Action<int[]?, double>> build)
            {
                appearance = Load(field);
                A steps = [];
                D initial = Snapshot(appearance);
                void Update(int[]? triples, double delta)
                {
                    D result;
                    try
                    {
                        var selections = triples is null ? null : Enumerable.Range(0, triples.Length / 3)
                            .Select(i => new Level100TerrainTileSelection(triples[i * 3], triples[i * 3 + 1],
                                0, triples[i * 3 + 2], 0)).ToArray();
                        appearance.Update(selections!, delta);
                        result = new D { ["ok"] = true };
                    }
                    catch (Exception error) { result = Failure(error); }
                    steps.Add(new D { ["tiles"] = triples is null ? default(Variant) : Variant.From(triples),
                        ["delta"] = BitConverter.GetBytes(delta), ["result"] = result, ["state"] = Snapshot(appearance) });
                }
                build(Update);
                scenarios.Add(new D { ["name"] = name, ["initial"] = initial, ["steps"] = steps });
                DisposeOwner(appearance); appearance = null;
            }
            Scenario("ordered_updates", update => {
                update([], 0d);
                update([37, 9, 1, 51, 48, 2, 3, 57, 3, 62, 31, 4], 1d / 60d);
                update([37, 9, 1, 51, 48, 2, 3, 57, 3, 62, 31, 4], -0d);
                update([2, 4, 1, 7, 8, 2, 4, 2, 3, 2, 1, 4], -0.125d);
                update([int.MinValue, int.MaxValue, 0], 50.00000000000001d);
            });
            Scenario("alias_partial_cpu_then_retry", update => {
                update([0, 0, 1, 32, 0, 1], 0.25d);
                update([0, 0, 1], 0.25d);
                update([1, 0, 1], 0.25d);
                update([0, 0, 2, 16, 0, 2], 0.25d);
                update([0, 0, 2], 0.25d);
                update([1, 0, 2], 0.25d);
            });
            Scenario("bounds_and_flat_aliases", update => {
                update(null, -0.5d);
                update([0, 0, -1], 0.125d);
                update([0, 0, 5], 0.125d);
                update([0, 0, int.MaxValue], 0.125d);
                update([-1, 0, 1], 0.125d); // -1 owner sentinel skips composition.
                update([-1, 1, 1, 64, 0, 2], 0.125d); // Accepted flat source aliases.
                update([1, 2, 3, 0, 64, 1], 0.125d); // Prior CPU write survives later failure.
                update([int.MinValue, int.MaxValue, 1], 0.125d);
                update([0, -1, 4], 0.125d);
            });
            Scenario("binary64_phase", update => {
                foreach (ulong bits in new ulong[] { 0, 0x8000000000000000, 1, 0x8000000000000001,
                    0x3ff0000000000000, 0xbff0000000000000, 0x4048ffffffffffff, 0x4049000000000000,
                    0x4049000000000001, 0x7fefffffffffffff, 0xffefffffffffffff })
                    update([], BitConverter.UInt64BitsToDouble(bits));
            });
            foreach (ulong bits in new ulong[] { 0x7ff0000000000000, 0xfff0000000000000,
                0x7ff8000000000000, 0xfff8000000000041 })
                Scenario("phase_nonfinite_" + bits.ToString("x16"), update => {
                    update([], BitConverter.UInt64BitsToDouble(bits)); update([], 0.25d);
                });
            A probeCases = [];
            MethodInfo probeMethod = typeof(LegacyLevel100TerrainAppearanceReference).GetMethod("ProbeShaderCode", BindingFlags.Static | BindingFlags.NonPublic)!;
            string shaderCode = (string)typeof(LegacyLevel100TerrainAppearanceReference)
                .GetField("TerrainShaderCode", BindingFlags.Static | BindingFlags.NonPublic)!.GetRawConstantValue()!;
            string whitespace = "\t\n\v\f\r \u0085\u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000";
            foreach (string probe in new[] { "", whitespace, "macro", "mask", "chain", "uv", "uvfine",
                whitespace + "macro" + whitespace, "MACRO", "macro uv", "\u180emacro", "macro\u200b", "\ufeffmacro", "\u0085wrong\u00a0" })
            {
                OS.SetEnvironment("ONSLAUGHT_TERRAIN_PROBE", probe);
                try { probeCases.Add(new D { ["input"] = probe, ["result"] = new D { ["ok"] = true, ["code"] = (string)probeMethod.Invoke(null, null)! } }); }
                catch (TargetInvocationException error) { probeCases.Add(new D { ["input"] = probe, ["result"] = Failure(error.InnerException!) }); }
            }
            OS.UnsetEnvironment("ONSLAUGHT_TERRAIN_PROBE");
            A supplied = [];
            foreach (string probe in new[] { "", whitespace, "macro", "invalid" })
            {
                using var shader = new Shader { Code = shaderCode + "\n// supplied shader identity" };
                using var material = new ShaderMaterial { Shader = shader };
                material.SetShaderParameter("terrain_cloud_scroll", new Vector2(0.25f, 0.75f));
                material.SetShaderParameter("fog_density", 0.125f);
                OS.SetEnvironment("ONSLAUGHT_TERRAIN_PROBE", probe);
                D result;
                try { appearance = Load(field, material); result = new D { ["ok"] = true }; }
                catch (Exception error) { result = Failure(error); }
                supplied.Add(new D { ["probe"] = probe, ["result"] = result,
                    ["same_material"] = appearance is null || ReferenceEquals(appearance.Material, material),
                    ["same_shader"] = ReferenceEquals(material.Shader, shader), ["shader"] = material.Shader.Code,
                    ["uniforms"] = Uniforms(material) });
                if (appearance is not null) { DisposeOwner(appearance, false); appearance = null; }
                if (!ReferenceEquals(material.Shader, shader)) material.Shader.Dispose();
            }
            OS.UnsetEnvironment("ONSLAUGHT_TERRAIN_PROBE");
            // A y-major complete batch whose geometry and edge words deliberately
            // differ from texture levels. Four asymmetric coordinates falsify a
            // transposition, wrong stride and geometry-for-texture substitution.
            int[] packed = new int[4096 * 3], explicitTiles = new int[4096 * 3];
            for (int i = 0; i < 4096; i++) {
                packed[i * 3] = (i % 5) + 9; packed[i * 3 + 2] = i ^ 0x35;
                explicitTiles[i * 3] = i & 63; explicitTiles[i * 3 + 1] = i >> 6;
            }
            foreach ((int x, int y, int level) in new[] { (37, 9, 1), (51, 48, 2), (3, 57, 3), (62, 31, 4) }) {
                packed[(y * 64 + x) * 3 + 1] = level; explicitTiles[(y * 64 + x) * 3 + 2] = level;
            }
            appearance = Load(field);
            appearance.Update(Enumerable.Range(0,4096).Select(i => new Level100TerrainTileSelection(
                i & 63, i >> 6, packed[i * 3], packed[i * 3 + 1], packed[i * 3 + 2])).ToArray(), 0.375d);
            D fast = new() { ["packed"] = packed, ["explicit"] = explicitTiles, ["delta"] = BitConverter.GetBytes(0.375d), ["state"] = Snapshot(appearance) };
            DisposeOwner(appearance); appearance = null;
            // Synthetic corrupt inputs contain no copied retail payload.
            string emptyPath = Owned(Path.Combine(Path.GetDirectoryName(fixturePath)!, "empty.bin"));
            string wrongRoot = Owned(Path.Combine(Path.GetDirectoryName(fixturePath)!, "wrong-root.bin"));
            File.WriteAllBytes(emptyPath, []); File.WriteAllBytes(wrongRoot, new byte[524288]);
            hashes[emptyPath] = Hex(File.ReadAllBytes(emptyPath)); hashes[wrongRoot] = Hex(File.ReadAllBytes(wrongRoot));
            A admission = [];
            void Reject(string name, string root, string hierarchy, bool nullField, byte mixer, byte detail) {
                typeof(LegacyLevel100HeightFieldReference).GetField("<MixerSet>k__BackingField", Fields)!.SetValue(field, mixer);
                typeof(LegacyLevel100HeightFieldReference).GetField("<DetailTexture>k__BackingField", Fields)!.SetValue(field, detail);
                D result;
                try { appearance = LegacyLevel100TerrainAppearanceReference.Load(root, hierarchy, DetailPath, CloudPath, nullField ? null! : field); result = new D { ["ok"] = true }; }
                catch (Exception error) { result = Failure(error); }
                admission.Add(new D { ["name"] = name, ["root"] = root, ["hierarchy"] = hierarchy,
                    ["null_field"] = nullField, ["mixer"] = mixer, ["detail"] = detail, ["result"] = result });
                if (appearance is not null) { DisposeOwner(appearance); appearance = null; }
            }
            Reject("empty_root_before_null", emptyPath, emptyPath, true, 0, 1);
            Reject("wrong_root_before_selectors", wrongRoot, emptyPath, false, 0, 1);
            Reject("null_after_root", RootPath, emptyPath, true, 10, 0);
            Reject("mixer_before_hierarchy", RootPath, emptyPath, false, 9, 0);
            Reject("detail_before_hierarchy", RootPath, emptyPath, false, 10, 1);
            Reject("hierarchy_before_textures", RootPath, emptyPath, false, 10, 0);
            Check(Input.MouseMode == pointer, "No pointer ownership change.");
            D after = Hashes(paths);
            foreach (Variant key in after.Keys) Check(after[key].AsString() == hashes[key].AsString(), "Input unchanged.");
            D fixture = new() { ["schema"] = 1, ["completed"] = new A { "terrain_appearance_reference" },
                ["paths"] = paths, ["input_hashes"] = hashes, ["facts"] = facts, ["shader"] = shaderCode,
                ["scenarios"] = scenarios, ["probes"] = probeCases, ["supplied"] = supplied, ["fast"] = fast, ["admission"] = admission };
            using (var output = Godot.FileAccess.Open(fixturePath, Godot.FileAccess.ModeFlags.Write) ?? throw new IOException("Cannot write fixture.")) output.StoreVar(fixture, false);
            using (var output = Godot.FileAccess.Open(reportPath, Godot.FileAccess.ModeFlags.Write) ?? throw new IOException("Cannot write report."))
                output.StoreString(Json.Stringify(new D { ["schema"] = 1, ["failure_count"] = 0,
                    ["counts"] = new D { ["reference"] = _checks, ["scenarios"] = scenarios.Count }, ["completed"] = new A { "terrain_appearance_reference" } }));
            field.Mesh.Dispose(); field = null;
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            GD.Print($"TERRAIN_APPEARANCE_REFERENCE: {_checks} checks, {scenarios.Count} scenarios; {fixturePath}");
            GetTree().Quit(0);
        }
        catch (Exception error) { if (appearance is not null) DisposeOwner(appearance); field?.Mesh.Dispose(); GD.PushError(error.ToString()); GetTree().Quit(1); }
        finally { if (hadProbe) OS.SetEnvironment("ONSLAUGHT_TERRAIN_PROBE", previousProbe); else OS.UnsetEnvironment("ONSLAUGHT_TERRAIN_PROBE"); }
    }

    private static LegacyLevel100TerrainAppearanceReference Load(LegacyLevel100HeightFieldReference field, ShaderMaterial? material = null) =>
        LegacyLevel100TerrainAppearanceReference.Load(RootPath, HierarchyPath, DetailPath, CloudPath, field, material);
    private static T Field<T>(LegacyLevel100TerrainAppearanceReference owner, string name) =>
        (T)typeof(LegacyLevel100TerrainAppearanceReference).GetField(name, Fields)!.GetValue(owner)!;
    private static D Facts(LegacyLevel100HeightFieldReference field) => new() { ["mixer_set"] = field.MixerSet,
        ["detail_texture"] = field.DetailTexture, ["sun_color_rgb24"] = field.SunColorRgb24,
        ["anti_sun_color_rgb24"] = field.AntiSunColorRgb24, ["ambient_color_rgb24"] = field.AmbientColorRgb24,
        ["fog_color"] = field.FogColor, ["fog_density"] = field.FogDensity };
    private static D Snapshot(LegacyLevel100TerrainAppearanceReference owner)
    {
        A levels = [];
        byte[][] cpu = Field<byte[][]>(owner, "_cacheBytes");
        int[][] owners = Field<int[][]>(owner, "_slotOwners"), occupied = Field<int[][]>(owner, "_occupiedSlots");
        ImageTexture[] textures = Field<ImageTexture[]>(owner, "_macroTextures");
        for (int i = 0; i < 5; i++) {
            using Image image = textures[i].GetImage();
            levels.Add(new D { ["cpu"] = Hex(cpu[i]), ["gpu"] = ImageFacts(image), ["owners"] = owners[i], ["occupied"] = occupied[i] });
        }
        return new D { ["u"] = BitConverter.GetBytes(Field<double>(owner, "_cloudScrollU")),
            ["v"] = BitConverter.GetBytes(Field<double>(owner, "_cloudScrollV")), ["levels"] = levels,
            ["uniforms"] = Uniforms((ShaderMaterial)owner.Material) };
    }
    private static D Uniforms(ShaderMaterial material)
    {
        D result = new();
        foreach (string name in new[] { "fog_color", "fog_density", "terrain_vertex_diffuse", "terrain_cloud_scroll" }) {
            using Variant value = material.GetShaderParameter(name);
            result[name] = GD.VarToBytes(value);
        }
        foreach (string name in new[] { "detail_map", "cloud_shadow_map" }) {
            using Variant value = material.GetShaderParameter(name);
            if (value.VariantType == Variant.Type.Object && value.AsGodotObject() is Texture2D texture) {
                using Image image = texture.GetImage(); result[name] = ImageFacts(image);
            }
        }
        return result;
    }
    private static D ImageFacts(Image image) => new() { ["width"] = image.GetWidth(), ["height"] = image.GetHeight(),
        ["format"] = (int)image.GetFormat(), ["mips"] = image.HasMipmaps(), ["sha256"] = Hex(image.GetData()) };
    private static D Failure(Exception error) => new() { ["ok"] = false, ["error_type"] = error.GetType().Name, ["error"] = error.Message };
    private static D Hashes(D paths) { D result = new(); foreach (Variant key in paths.Keys) { string path = paths[key].AsString(); result[path] = Hex(Godot.FileAccess.GetFileAsBytes(path)); } return result; }
    private static string Hex(byte[] bytes) => Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
    private static void DisposeOwner(LegacyLevel100TerrainAppearanceReference owner, bool disposeMaterial = true)
    {
        foreach (ImageTexture texture in Field<ImageTexture[]>(owner, "_macroTextures")) texture.Dispose();
        var material = (ShaderMaterial)owner.Material;
        foreach (string name in new[] { "detail_map", "cloud_shadow_map" }) {
            using Variant value = material.GetShaderParameter(name); value.AsGodotObject()?.Dispose();
        }
        if (disposeMaterial) { material.Shader.Dispose(); material.Dispose(); }
    }
    private string Owned(string path) {
        string full = Path.GetFullPath(path), root = Path.GetFullPath(Path.Combine(ProjectSettings.GlobalizePath("res://"), "..", "..", "local-data")) + Path.DirectorySeparatorChar;
        Check(full.StartsWith(root, StringComparison.Ordinal) && Directory.Exists(Path.GetDirectoryName(full)) && !File.Exists(full), "Output must be fresh worktree-local data."); return full;
    }
    private void Check(bool condition, string message) { _checks++; if (!condition) throw new InvalidOperationException(message); }
}
