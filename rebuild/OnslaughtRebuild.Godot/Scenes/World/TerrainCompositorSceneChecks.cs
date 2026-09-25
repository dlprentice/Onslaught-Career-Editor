// SPDX-License-Identifier: GPL-3.0-or-later
using System.Reflection;
using System.Security.Cryptography;
using Godot;
using OnslaughtRebuild.Core;
using A = Godot.Collections.Array;
using D = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

/// <summary>Bounded private value fixtures from the unchanged C# compositor.
/// This exports no resources and writes only explicit fresh local-data paths.</summary>
public sealed partial class TerrainCompositorSceneChecks : Node
{
    private const BindingFlags InstanceFields = BindingFlags.Instance | BindingFlags.NonPublic;
    private const BindingFlags StaticMethods = BindingFlags.Static | BindingFlags.NonPublic;
    private const string HierarchySha = "541eacd0aa75fae8befb8a3e1505ea52ae6b1f6c1367c15c65d7dd23b7cfe977";
    private const string RootSha = "6eb202f450926097930bedca440f0163a1886572981e3c69b4edf9289a68ae2b";
    private int _checks;

    public override async void _Ready()
    {
        try
        {
            string[] args = OS.GetCmdlineUserArgs();
            Check(args.Length == 2, "Two fresh owned output paths are required.");
            string fixturePath = Owned(args[0]);
            string reportPath = Owned(args[1]);
            Check(fixturePath != reportPath, "Fixture and report paths are distinct.");
            Check(!Engine.IsEditorHint() && DisplayServer.GetName() == "headless", "Reference is headless runtime only.");
            Input.MouseModeEnum pointer = Input.MouseMode;
            string hierarchyPath = ProjectSettings.GlobalizePath("res://Assets/Level100/Source/level100-terrain-hierarchy.bin");
            string rootPath = ProjectSettings.GlobalizePath("res://Assets/Level100/Source/level100-root-terrain.rgb565.bin");
            byte[] source = File.ReadAllBytes(hierarchyPath);
            byte[] root = File.ReadAllBytes(rootPath);
            Check(Hex(source) == HierarchySha, "Hierarchy input retains its existing exact identity.");
            Check(root.Length == Level100TerrainCompositor.RootTextureLength && Hex(root) == RootSha,
                "Root texture retains its existing length and exact identity.");
            Level100Terrain terrain = Level100Terrain.Instance;
            var compositor = Level100TerrainCompositor.Create(source, terrain.SunColorRgb24, terrain.AmbientColorRgb24);
            byte[] rendered = new byte[root.Length];
            for (int y = 0; y < 64; y++)
                for (int x = 0; x < 64; x++) compositor.RenderTile(rendered, 0, x, y, x, y);
            Check(rendered.AsSpan().SequenceEqual(root) && Hex(rendered) == RootSha,
                "All 4096 level-zero tiles reproduce the fixed root bytes, not a changed expected hash.");
            object hierarchy = typeof(Level100TerrainCompositor).GetField("_hierarchy", InstanceFields)!.GetValue(compositor)!;
            using A tiles = TileCases(compositor, hierarchy);
            using A pines = PineCases(compositor, hierarchy);
            using A blends = BlendCases();
            using A lighting = LightingCases(terrain);
            using A refusals = AdmissionCases(source, terrain);
            using A boundaries = BoundaryCases(compositor);
            using D fixture = new()
            {
                ["schema"] = 1, ["completed"] = new A { "terrain_compositor_reference" },
                ["hierarchy_path"] = hierarchyPath, ["hierarchy_sha256"] = HierarchySha,
                ["root_path"] = rootPath, ["root_sha256"] = RootSha, ["root_bytes"] = rendered,
                ["sun"] = terrain.SunColorRgb24, ["ambient"] = terrain.AmbientColorRgb24,
                ["tiles"] = tiles, ["pines"] = pines, ["blends"] = blends, ["lighting"] = lighting,
                ["admission"] = refusals, ["boundaries"] = boundaries,
            };
            using Variant fixtureValue = fixture;
            Check(ObjectFree(fixtureValue), "Fixture contains values only, never objects or resources.");
            Check(Hex(File.ReadAllBytes(hierarchyPath)) == HierarchySha && Hex(File.ReadAllBytes(rootPath)) == RootSha,
                "Retained input files remain unchanged.");
            Check(Input.MouseMode == pointer, "Compositor fixture never takes pointer ownership.");
            using (var output = Godot.FileAccess.Open(fixturePath, Godot.FileAccess.ModeFlags.Write)
                ?? throw new IOException("Cannot create compositor fixture.")) output.StoreVar(fixtureValue, false);
            using D report = new()
            {
                ["schema"] = 1, ["failure_count"] = 0, ["completed"] = new A { "terrain_compositor_reference" },
                ["counts"] = new D { ["reference"] = _checks, ["root_bytes"] = rendered.Length,
                    ["tiles"] = tiles.Count, ["pines"] = pines.Count, ["blends"] = blends.Count,
                    ["lighting"] = lighting.Count, ["admission"] = refusals.Count, ["boundaries"] = boundaries.Count },
            };
            using (var output = Godot.FileAccess.Open(reportPath, Godot.FileAccess.ModeFlags.Write)
                ?? throw new IOException("Cannot create compositor report.")) output.StoreString(Json.Stringify(report));
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            GD.Print($"TERRAIN_COMPOSITOR_REFERENCE_CHECKS: {_checks} passed; fixed {rendered.Length} root bytes, {tiles.Count} higher-level blocks; {fixturePath}");
            GetTree().Quit(0);
        }
        catch (Exception error)
        {
            GD.PushError(error.ToString());
            GetTree().Quit(1);
        }
    }

    private A TileCases(Level100TerrainCompositor compositor, object hierarchy)
    {
        var cells = (System.Array)Property(hierarchy, "Cells");
        var shadows = (byte[]?[])Property(hierarchy, "Shadows");
        var pines = (System.Array)Property(hierarchy, "Pines");
        int Layers(int tile) => ((byte[])Property(cells.GetValue(tile)!, "MaterialIds")).Length;
        int PineCount(int tile)
        {
            int x = tile % 64 * 8, y = tile / 64 * 8;
            return pines.Cast<object>().Count(pine =>
            {
                int px = (short)Property(pine, "TopX"), py = (short)Property(pine, "TopY");
                int size = 1 << (byte)Property(pine, "RootLevel");
                return px < x + 8 && py < y + 8 && px + size > x && py + size > y;
            });
        }
        int shadowTile = Enumerable.Range(0, 4096).First(i => shadows[i]?.Any(value => value != 0) == true);
        int layeredTile = Enumerable.Range(0, 4096).OrderByDescending(Layers).First();
        int pineTile = Enumerable.Range(0, 4096).OrderByDescending(PineCount).First();
        (string Name, int Tile)[] selected = [("top-left", 0), ("top-right", 63), ("bottom-left", 4032),
            ("bottom-right", 4095), ("maximum-layers", layeredTile), ("static-shadow", shadowTile),
            ("maximum-pine-overlap", pineTile), ("middle-parity", 32 * 64 + 31)];
        Check(PineCount(pineTile) > 1, "Higher-level fixtures cover overlapping ordered pine shadows.");
        Check(Layers(layeredTile) > 1, "Higher-level fixtures cover material blending.");
        A result = new();
        for (int level = 1; level <= 4; level++)
            for (int index = 0; index < selected.Length; index++)
            {
                int tile = selected[index].Tile, size = 8 << level, slots = 512 / size;
                int sx = index * 3 % slots, sy = (index * 5 + 1) % slots;
                byte[] cache = Enumerable.Repeat((byte)0xa5, Level100TerrainCompositor.RootTextureLength).ToArray();
                compositor.RenderTile(cache, level, tile % 64, tile / 64, sx, sy);
                byte[] block = new byte[size * size * 2];
                for (int y = 0; y < size; y++)
                    cache.AsSpan(((sy * size + y) * 512 + sx * size) * 2, size * 2).CopyTo(block.AsSpan(y * size * 2));
                using D row = new()
                {
                    ["name"] = selected[index].Name + "-level-" + level, ["level"] = level,
                    ["tile_x"] = tile % 64, ["tile_y"] = tile / 64, ["slot_x"] = sx, ["slot_y"] = sy,
                    ["layers"] = Layers(tile), ["has_shadow"] = shadows[tile] is not null,
                    ["pine_count"] = PineCount(tile), ["bytes"] = block, ["cache_sha256"] = Hex(cache),
                };
                Append(result, row);
            }
        Check(result.Count == 32, "Higher-level work is bounded to 32 complete tiles.");
        return result;
    }

    private A PineCases(Level100TerrainCompositor compositor, object hierarchy)
    {
        Type type = typeof(Level100TerrainCompositor);
        Type pineType = type.GetNestedType("PineShadow", BindingFlags.NonPublic)!;
        MethodInfo apply = type.GetMethod("ApplyPineShadows", InstanceFields)!;
        int[] descriptors = [-1, -1, 2, 0, 1, 1, 1, 1, 2, 7, 7, 2, 8, -2, 2, -4, 6, 2, 5, 0, 1];
        byte[] alpha = Enumerable.Range(0, 5461).Select(i => (byte)((i * 17 + i / 13) % 40)).ToArray();
        System.Array records = System.Array.CreateInstance(pineType, descriptors.Length / 3);
        for (int index = 0; index < records.Length; index++)
            records.SetValue(Activator.CreateInstance(pineType, (short)descriptors[index * 3],
                (short)descriptors[index * 3 + 1], (byte)descriptors[index * 3 + 2]), index);
        object syntheticHierarchy = hierarchy.GetType().GetConstructors().Single(c => c.GetParameters().Length == 6)
            .Invoke([Property(hierarchy, "Maps"), Property(hierarchy, "Cells"), Property(hierarchy, "Shade"),
                Property(hierarchy, "Shadows"), alpha, records]);
        var synthetic = (Level100TerrainCompositor)type.GetConstructors(InstanceFields).Single().Invoke(
            [syntheticHierarchy, type.GetField("_lighting", InstanceFields)!.GetValue(compositor)!]);
        A result = new();
        for (int level = 0; level <= 4; level++)
        {
            int size = 8 << level;
            ushort[] before = Enumerable.Range(0, size * size).Select(i => unchecked((ushort)(i * 521 + 0x35a7))).ToArray();
            ushort[] after = (ushort[])before.Clone();
            apply.Invoke(synthetic, [after, size, level, 0, 0]);
            Check(!before.AsSpan().SequenceEqual(after), "Each pine fixture exercises actual shadow writes.");
            using D row = new() { ["level"] = level, ["descriptors"] = descriptors, ["alpha"] = alpha,
                ["before"] = before.Select(value => (int)value).ToArray(), ["after"] = after.Select(value => (int)value).ToArray() };
            Append(result, row);
        }
        return result;
    }

    private static A BlendCases()
    {
        MethodInfo blend = typeof(Level100TerrainCompositor).GetMethod("BlendMaterial", StaticMethods)!;
        uint[] words = [0, 1, 0xff, 0xffffff, 0x1000000, 0x3ffffff, 0x4000000, 0x1fffffff,
            0x20000000, 0x7fffffff, 0x80000000, 0xff000000, 0xfff8f8ff, 0xfffffffe, 0xffffffff];
        A result = new();
        void Add(uint color, uint candidate)
        {
            using D row = new() { ["color"] = color, ["candidate"] = candidate,
                ["value"] = (uint)blend.Invoke(null, [color, candidate])! };
            Append(result, row);
        }
        foreach (uint color in words)
        {
            foreach (uint candidate in words) Add(color, candidate);
            foreach (uint delta in new uint[] { 0, 1, 0x3ffffff, 0x4000000, 0x1ffffffe, 0x1fffffff,
                0x20000000, 0x20000001, 0x7fffffff, 0x80000000, 0xffffffff }) Add(color, unchecked(color + delta));
        }
        var random = new Random(0x434f4d50);
        for (int index = 0; index < 512; index++) Add((uint)random.NextInt64(0x100000000), (uint)random.NextInt64(0x100000000));
        return result;
    }

    private static A LightingCases(Level100Terrain terrain)
    {
        MethodInfo gradient = typeof(Level100TerrainCompositor).GetMethod("BuildLightingGradient", StaticMethods)!;
        A result = new();
        void Add(uint sun, uint ambient)
        {
            var coefficients = (System.Array)gradient.Invoke(null, [sun, ambient])!;
            long[] words = coefficients.Cast<object>().SelectMany(coefficient => new[] { (long)(uint)Property(coefficient, "Red"),
                (long)(uint)Property(coefficient, "Green"), (long)(uint)Property(coefficient, "Blue") }).ToArray();
            (float red, float green, float blue) = Level100TerrainCompositor.TerrainVertexDiffuse(sun, ambient);
            using D row = new() { ["sun"] = sun, ["ambient"] = ambient, ["gradient"] = words,
                ["diffuse"] = new[] { BitConverter.SingleToInt32Bits(red), BitConverter.SingleToInt32Bits(green), BitConverter.SingleToInt32Bits(blue) } };
            Append(result, row);
        }
        Add(terrain.SunColorRgb24, terrain.AmbientColorRgb24);
        Add(terrain.SunColorRgb24, terrain.AntiSunColorRgb24);
        foreach (uint sun in new uint[] { 0, 1, 0x010101, 0x020202, 0x7f7f7f, 0xfefefe, 0xffffff, 0xffffffff })
            foreach (uint ambient in new uint[] { 0, 1, 0xffffff, 0xffffffff }) Add(sun, ambient);
        var random = new Random(0x4c494748);
        for (int index = 0; index < 128; index++) Add((uint)random.NextInt64(0x100000000), (uint)random.NextInt64(0x100000000));
        return result;
    }

    private A AdmissionCases(byte[] source, Level100Terrain terrain)
    {
        A result = new();
        void Add(string kind, int argument)
        {
            byte[]? changed = kind switch
            {
                "null" => null, "truncate" => source[..argument], "append" => [.. source, (byte)argument],
                "flip" => (byte[])source.Clone(), _ => throw new InvalidOperationException(kind),
            };
            if (kind == "flip") changed![argument] ^= 1;
            string? error = null;
            try { Level100TerrainCompositor.Create(changed!, terrain.SunColorRgb24, terrain.AmbientColorRgb24); }
            catch (Exception caught) { error = caught.GetType().Name; }
            Check(error is not null, "Mutated source must not produce a compositor.");
            using D row = new() { ["kind"] = kind, ["argument"] = argument, ["error_type"] = error! };
            Append(result, row);
        }
        Add("null", 0);
        foreach (int length in new[] { 0, 1, 3, 4, 8, 12, 1024, source.Length - 1 }) Add("truncate", length);
        foreach (int offset in new[] { 0, 4, 8, 12, 16, source.Length / 2, source.Length - 1 }) Add("flip", offset);
        Add("append", 0); Add("append", 255);
        return result;
    }

    private static A BoundaryCases(Level100TerrainCompositor compositor)
    {
        A result = new();
        void Add(string name, int length, int level, int tx, int ty, int sx, int sy)
        {
            byte[]? bytes = length < 0 ? null : Enumerable.Repeat((byte)0xa5, length).ToArray();
            string error = "";
            try { compositor.RenderTile(bytes!, level, tx, ty, sx, sy); }
            catch (Exception caught) { error = caught.GetType().Name; }
            using D row = new() { ["name"] = name, ["length"] = length, ["level"] = level,
                ["tile_x"] = tx, ["tile_y"] = ty, ["slot_x"] = sx, ["slot_y"] = sy,
                ["error_type"] = error, ["bytes"] = bytes ?? [] };
            Append(result, row);
        }
        Add("null-destination", -1, 0, 0, 0, 0, 0);
        foreach (int length in new[] { 0, 1, 2, 15, 16, 17, 1024, 1025, 1040, 7183, 7184 })
            Add("partial-" + length, length, 0, 0, 0, 0, 0);
        Add("negative-tile-x", 8192, 0, -1, 0, 0, 0);
        Add("negative-tile-y", 8192, 0, 0, -1, 0, 0);
        Add("negative-tile-x-flat-alias", 8192, 0, -1, 1, 0, 0);
        Add("tile-x64-flat-alias", 8192, 0, 64, 0, 0, 0);
        Add("tile-y64-outside", 8192, 0, 0, 64, 0, 0);
        Add("tile-int-overflow", 8192, 0, int.MinValue, int.MinValue, 0, 0);
        Add("slot-x64-flat-alias", 9216, 0, 0, 0, 64, 0);
        Add("slot-x-negative-flat-alias", 16384, 0, 0, 0, -1, 1);
        Add("slot-x-negative-outside", 8192, 0, 0, 0, -1, 0);
        Add("slot-y-negative-outside", 8192, 0, 0, 0, 0, -1);
        Add("slot-intmax-wrap-alias", 16384, 0, 0, 0, int.MaxValue, 1);
        Add("slot-intmin-wrap-alias", 8192, 0, 0, 0, int.MinValue, 0);
        // These invalid levels allocate at most 64 KiB before the C# map-array
        // refusal. Do not invoke extreme shifts which can monopolize the host.
        Add("negative-level-safe-shift", 16, -32, 0, 0, 0, 0);
        Add("high-level-safe-shift", 16, 32, 0, 0, 0, 0);
        return result;
    }

    private static object Property(object owner, string name) => owner.GetType().GetProperty(name)!.GetValue(owner)!;
    private static string Hex(byte[] bytes) => Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
    private static void Append(A array, D row) { using Variant value = row; array.Add(value); }

    private static bool ObjectFree(Variant value)
    {
        if (value.VariantType == Variant.Type.Object) return false;
        if (value.VariantType == Variant.Type.Array)
        {
            using A array = value.AsGodotArray();
            for (int index = 0; index < array.Count; index++)
            { using Variant item = array[index]; if (!ObjectFree(item)) return false; }
        }
        else if (value.VariantType == Variant.Type.Dictionary)
        {
            using D dictionary = value.AsGodotDictionary();
            ICollection<Variant> keys = dictionary.Keys;
            using IDisposable? disposableKeys = keys as IDisposable;
            foreach (Variant key in keys)
                using (key)
                using (Variant item = dictionary[key])
                    if (!ObjectFree(key) || !ObjectFree(item)) return false;
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
        { part = Path.Combine(part, segment); Check(new FileInfo(part).LinkTarget is null, "Output never traverses links."); }
        return result;
    }

    private void Check(bool value, string message)
    { _checks++; if (!value) throw new InvalidOperationException(message); }
}
