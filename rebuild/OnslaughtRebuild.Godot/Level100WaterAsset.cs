// SPDX-License-Identifier: GPL-3.0-or-later
using Godot;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Temporary host adapter for the native production Water scene. Geometry,
/// materials, phase updates and camera-relative placement belong to GDScript.
/// The exact pre-port comparison owner is retained only under Scenes/World/Tests.
/// </summary>
internal sealed partial class Level100WaterAsset
{
    internal const string ScenePath = "res://Scenes/World/Water.tscn";
    private const string TerrainResource =
        "OnslaughtRebuild.Core.Assets.Level100.level100-heightfield.hfld.bin";

    private Level100WaterAsset(Node3D root)
    {
        Root = root;
        using Variant result = root.Call("counts");
        using Godot.Collections.Dictionary counts = result.AsGodotDictionary();
        GridVertexCount = counts["grid_vertices"].AsInt32();
        GridTriangleCount = counts["grid_triangles"].AsInt32();
        ShorelineTriangleCount = counts["shoreline_triangles"].AsInt32();
    }

    public Node3D Root { get; }
    public int GridVertexCount { get; }
    public int GridTriangleCount { get; }
    public int ShorelineTriangleCount { get; }

    public static Level100WaterAsset Create(Level100HeightFieldAsset terrain,
        Texture2D reflection, Texture2D caustic, Texture2D waves,
        Texture2D sunBlob, Texture2D sunReflection,
        string surfaceResourcePath, string surfaceSha256)
    {
        ArgumentNullException.ThrowIfNull(terrain);
        using PackedScene scene = GD.Load<PackedScene>(ScenePath);
        Node3D root = scene.Instantiate<Node3D>();
        try
        {
            using var textures = new Godot.Collections.Dictionary {
                ["reflection_texture"] = reflection, ["caustic_texture"] = caustic,
                ["waves_texture"] = waves, ["sun_blob_texture"] = sunBlob,
                ["sun_reflection_texture"] = sunReflection };
            Configure(root, false, textures, surfaceResourcePath, surfaceSha256);
            return new Level100WaterAsset(root);
        }
        catch { root.Free(); throw; }
    }

    private static Level100WaterAsset BindNativeScene(Node3D root, Level100HeightFieldAsset terrain)
    {
        ArgumentNullException.ThrowIfNull(terrain);
        using var textures = new Godot.Collections.Dictionary();
        Configure(root, true, textures, "", "");
        return new Level100WaterAsset(root);
    }

    private static void Configure(Node3D root, bool retainSaved,
        Godot.Collections.Dictionary textures, string surfacePath, string surfaceSha256)
    {
        if (!root.HasMethod("configure"))
            throw new InvalidDataException("The imported water is stale. Rebuild the private production scene.");
        using Stream source = typeof(Level100Terrain).Assembly.GetManifestResourceStream(TerrainResource)
            ?? throw new InvalidDataException("The retained Level 100 heightfield is missing.");
        var bytes = new byte[source.Length];
        source.ReadExactly(bytes);
        using Variant result = root.Call("configure", bytes, retainSaved, textures, surfacePath, surfaceSha256);
        RequireOk(result);
    }

    public void Update(Vector3 cameraPosition, float frameDelta)
    {
        using Variant result = Root.Call("update_camera", cameraPosition, frameDelta);
        RequireOk(result);
    }

    private static void RequireOk(Variant result)
    {
        using Godot.Collections.Dictionary value = result.AsGodotDictionary();
        if (!value["ok"].AsBool()) throw new InvalidDataException(value["error"].AsString());
    }
}
