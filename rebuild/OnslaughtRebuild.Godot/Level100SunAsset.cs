// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Temporary host adapter for the production GDScript Sun scene. The native
/// scene owns authored material, descriptor admission, placement and the
/// existing terrain-only occlusion law. The retained comparison implementation
/// in Scenes/World/Tests/LegacyLevel100SunReference.cs records the unchanged
/// source provenance and its unresolved VisibleSun/world-object omissions.
/// </summary>
internal sealed class Level100SunAsset
{
    internal const string ScenePath = "res://Scenes/World/SunSprite.tscn";
    private const string TerrainResource =
        "OnslaughtRebuild.Core.Assets.Level100.level100-heightfield.hfld.bin";

    private Level100SunAsset(MeshInstance3D root) => Root = root;

    public MeshInstance3D Root { get; }
    public bool Visible => Root.Visible;

    public static Level100SunAsset Create(Level100HeightFieldAsset terrain, MeshInstance3D? sceneRoot = null)
    {
        ArgumentNullException.ThrowIfNull(terrain);
        MeshInstance3D root;
        if (sceneRoot is null)
        {
            using PackedScene scene = GD.Load<PackedScene>(ScenePath);
            root = scene.Instantiate<MeshInstance3D>();
        }
        else root = sceneRoot;

        try
        {
            if (!root.HasMethod("configure"))
                throw new InvalidDataException("The imported sun is stale. Rebuild the private production scene.");
            // The current host already embeds this exact, pinned input. Transfer
            // it once; native terrain owns every subsequent sample and ray step.
            using Stream source = typeof(Level100Terrain).Assembly.GetManifestResourceStream(TerrainResource)
                ?? throw new InvalidDataException("The retained Level 100 heightfield is missing.");
            var bytes = new byte[source.Length];
            source.ReadExactly(bytes);
            using Variant result = root.Call("configure", bytes, sceneRoot is not null);
            RequireOk(result);
            return new Level100SunAsset(root);
        }
        catch
        {
            if (sceneRoot is null) root.Free();
            throw;
        }
    }

    public void Update(Vector3 cameraPosition)
    {
        using Variant result = Root.Call("update_camera", cameraPosition);
        RequireOk(result);
    }

    private static void RequireOk(Variant result)
    {
        using Godot.Collections.Dictionary value = result.AsGodotDictionary();
        using Variant ok = value["ok"];
        if (!ok.AsBool())
        {
            using Variant error = value["error"];
            throw new InvalidDataException(error.AsString());
        }
    }
}
