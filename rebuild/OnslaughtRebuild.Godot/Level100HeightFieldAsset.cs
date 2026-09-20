// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Core;
using Dictionary = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

internal readonly record struct Level100TerrainTileSelection(
    int TileX, int TileY, int GeometryLevel, int TextureLevel, int EdgeFlags);

/// <summary>
/// Temporary adapter for the native terrain renderer. It transfers pinned
/// HFLD bytes once and one camera/selection batch per update. The native owner
/// controls sampling, smoothing, LOD, stitching, mesh identity and geometry;
/// the native appearance owner receives its packed selections directly. The
/// remaining managed static-world consumers only read immutable scalar facts.
/// Original numerical/provenance comments remain with the unchanged reference
/// in Scenes/World/Tests/LegacyLevel100HeightFieldReference.cs.
/// </summary>
internal sealed class Level100HeightFieldAsset : IDisposable
{
    private const string ScriptPath = "res://Scenes/World/height_field.gd";
    private const string TerrainResource = "OnslaughtRebuild.Core.Assets.Level100.level100-heightfield.hfld.bin";
    public const float PlayerStartX = Level100Terrain.PlayerStartRetailXFixed / (float)Level100Terrain.FixedPointUnitsPerRetailUnit;
    public const float PlayerStartZ = Level100Terrain.PlayerStartRetailYFixed / (float)Level100Terrain.FixedPointUnitsPerRetailUnit;
    public const float PlayerStartElevation = Level100Terrain.PlayerStartReferenceElevationMillimeters / 1_000f;
    private readonly RefCounted _native;

    private Level100HeightFieldAsset(RefCounted native)
    {
        _native = native;
        using Variant mesh = native.Call("get_mesh");
        Mesh = mesh.As<ArrayMesh>();
        using Variant metadata = native.Call("metadata");
        using Dictionary values = metadata.AsGodotDictionary();
        // Cache immutable scalar facts once; their property reads never cross
        // languages or recompute a second presentation owner.
        MixerSet = Read<byte>(values, "mixer_set");
        SkyCube = Read<byte>(values, "sky_cube");
        DetailTexture = Read<byte>(values, "detail_texture");
        WaterTexture = Read<byte>(values, "water_texture");
        WaterLevel = Read<float>(values, "water_level");
        WaterRelativeHeight = Read<float>(values, "water_relative_height");
        FogColor = Read<Color>(values, "fog_color");
        FogDensity = Read<float>(values, "fog_density");
        SunColor = Read<Color>(values, "sun_color");
        AntiSunColor = Read<Color>(values, "anti_sun_color");
        AmbientColor = Read<Color>(values, "ambient_color");
        SunColorRgb24 = Read<uint>(values, "sun_color_rgb24");
        AntiSunColorRgb24 = Read<uint>(values, "anti_sun_color_rgb24");
        AmbientColorRgb24 = Read<uint>(values, "ambient_color_rgb24");
        SunlightDirection = Read<Vector3>(values, "sunlight_direction");
        SunPosition = Read<Vector3>(values, "sun_position");
    }

    public ArrayMesh Mesh { get; }
    public int VertexCount { get; private set; }
    public int TriangleCount { get; private set; }
    public byte MixerSet { get; }
    public byte SkyCube { get; }
    public byte DetailTexture { get; }
    public float WaterLevel { get; }
    public float WaterRelativeHeight { get; }
    public byte WaterTexture { get; }
    public Color FogColor { get; }
    public float FogDensity { get; }
    public Color SunColor { get; }
    public Color AntiSunColor { get; }
    public Color AmbientColor { get; }
    public uint SunColorRgb24 { get; }
    public uint AntiSunColorRgb24 { get; }
    public uint AmbientColorRgb24 { get; }
    public Vector3 SunlightDirection { get; }
    public Vector3 SunPosition { get; }

    public static Level100HeightFieldAsset Load(ArrayMesh? sceneMesh = null)
    {
        using Stream source = typeof(Level100Terrain).Assembly.GetManifestResourceStream(TerrainResource)
            ?? throw new InvalidDataException("The retained Level 100 heightfield is missing.");
        byte[] bytes = new byte[source.Length];
        source.ReadExactly(bytes);
        using GDScript script = GD.Load<GDScript>(ScriptPath);
        using Variant input = bytes;
        using Variant mesh = sceneMesh is null ? default : Variant.From(sceneMesh);
        using Variant loaded = script.Call("from_bytes", input, mesh);
        using Dictionary result = Result(loaded);
        using Variant value = result["value"];
        RefCounted native = value.As<RefCounted>();
        try { return new Level100HeightFieldAsset(native); }
        catch { native.Dispose(); throw; }
    }

    public float SampleRelativeHeight(float relativeX, float relativeZ)
    {
        using Variant result = _native.Call("sample_relative_height", relativeX, relativeZ);
        return result.AsSingle();
    }

    public void Update(Camera3D camera, Level100TerrainAppearanceAsset appearance, double frameDelta)
    {
        using Variant returned = _native.Call("update", camera.GlobalPosition, -camera.GlobalTransform.Basis.Z);
        using Dictionary result = Result(returned);
        // Geometry has already changed if the following appearance update
        // fails. Preserve those observable counts before forwarding its batch.
        VertexCount = Read<int>(result, "vertex_count");
        TriangleCount = Read<int>(result, "triangle_count");
        using Variant selection = result["selections"];
        appearance.UpdateHeightfield(selection, frameDelta);
    }

    public void Dispose() => _native.Dispose();

    private static T Read<[MustBeVariant] T>(Dictionary source, string key)
    {
        using Variant value = source[key];
        return value.As<T>();
    }

    private static Dictionary Result(Variant value)
    {
        if (value.VariantType != Variant.Type.Dictionary)
            throw new InvalidOperationException("Native terrain aborted without a completion result.");
        Dictionary result = value.AsGodotDictionary();
        using Variant ok = result["ok"];
        if (ok.VariantType == Variant.Type.Bool && ok.AsBool()) return result;
        using Variant error = result["error"];
        string message = error.AsString();
        result.Dispose();
        throw new InvalidDataException(message);
    }
}
