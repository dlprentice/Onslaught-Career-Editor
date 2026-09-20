// SPDX-License-Identifier: GPL-3.0-or-later
using Godot;
using Dictionary = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Temporary host adapter for the native terrain appearance owner. The native
/// owner admits the assets once, retains the scene material and owns cloud
/// phases, cache composition and upload ordering. No per-tile managed work is
/// performed. The unchanged previous implementation remains a test oracle in
/// Scenes/World/Tests/LegacyLevel100TerrainAppearanceReference.cs.
/// </summary>
internal sealed class Level100TerrainAppearanceAsset : IDisposable
{
    private const string ScriptPath = "res://Scenes/World/terrain_appearance.gd";
    private readonly RefCounted _native;

    private Level100TerrainAppearanceAsset(RefCounted native)
    {
        _native = native;
        using Variant material = native.Call("get_material");
        Material = material.As<ShaderMaterial>();
    }

    public Material Material { get; }

    public static Level100TerrainAppearanceAsset Load(
        string rootTextureResourcePath,
        string hierarchyResourcePath,
        string detailTextureResourcePath,
        string cloudShadowResourcePath,
        Level100HeightFieldAsset heightField,
        ShaderMaterial? sceneMaterial = null)
    {
        using GDScript script = GD.Load<GDScript>(ScriptPath);
        using Dictionary facts = new();
        if (heightField is not null)
        {
            facts["mixer_set"] = heightField.MixerSet;
            facts["detail_texture"] = heightField.DetailTexture;
            facts["sun_color_rgb24"] = heightField.SunColorRgb24;
            facts["anti_sun_color_rgb24"] = heightField.AntiSunColorRgb24;
            facts["ambient_color_rgb24"] = heightField.AmbientColorRgb24;
            facts["fog_color"] = heightField.FogColor;
            facts["fog_density"] = heightField.FogDensity;
        }
        using Variant metadata = heightField is null ? default : Variant.From(facts);
        using Variant material = sceneMaterial is null ? default : Variant.From(sceneMaterial);
        using Variant returned = script.Call("load_paths", rootTextureResourcePath,
            hierarchyResourcePath, detailTextureResourcePath, cloudShadowResourcePath, metadata, material);
        using Dictionary result = Result(returned);
        using Variant value = result["value"];
        RefCounted native = value.As<RefCounted>();
        try { return new Level100TerrainAppearanceAsset(native); }
        catch { native.Dispose(); throw; }
    }

    internal void UpdateHeightfield(Variant selections, double frameDelta)
    {
        using Variant returned = _native.Call("update_heightfield", selections, frameDelta);
        using Dictionary result = Result(returned);
    }

    internal void UpdateTiles(Variant selections, double frameDelta)
    {
        using Variant returned = _native.Call("update_tiles", selections, frameDelta);
        using Dictionary result = Result(returned);
    }

    public void Dispose() => _native.Dispose();

    private static Dictionary Result(Variant value)
    {
        if (value.VariantType != Variant.Type.Dictionary)
            throw new InvalidOperationException("Native terrain appearance aborted without a completion result.");
        Dictionary result = value.AsGodotDictionary();
        using Variant ok = result["ok"];
        if (ok.VariantType == Variant.Type.Bool && ok.AsBool()) return result;
        using Variant error = result["error"];
        using Variant type = result["error_type"];
        string message = error.AsString();
        string errorType = type.AsString();
        result.Dispose();
        throw errorType switch
        {
            "IndexOutOfRangeException" => new IndexOutOfRangeException(message),
            "NullReferenceException" => new NullReferenceException(message),
            "ArgumentException" => new ArgumentException(message),
            "InvalidOperationException" => new InvalidOperationException(message),
            _ => new InvalidDataException(message)
        };
    }
}
