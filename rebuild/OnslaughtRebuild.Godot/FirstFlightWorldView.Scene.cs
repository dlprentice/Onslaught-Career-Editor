// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

public sealed partial class FirstFlightWorldView
{
    public const string ProductionScenePath = "res://Assets/Level100/Scenes/Level100.tscn";

    public static FirstFlightWorldView InstantiateScene()
    {
        Level100SceneImport.VerifyCurrentImport();
        return ResourceLoader.Load<PackedScene>(ProductionScenePath).Instantiate<FirstFlightWorldView>();
    }

    private void BindProductionScene(WorldSnapshot snapshot)
    {
        var terrain = GetNode<MeshInstance3D>("RetailLevel100HeightField");
        _level100Terrain = Level100HeightFieldAsset.Load((ArrayMesh)terrain.Mesh);
        _level100TerrainAppearance = Level100TerrainAppearanceAsset.Load(
            "res://Assets/Level100/Source/level100-root-terrain.rgb565.bin",
            "res://Assets/Level100/Source/level100-terrain-hierarchy.bin",
            "res://Assets/Level100/Textures/terrain-detail-00.texture.aya",
            "res://Assets/Level100/Textures/terrain-cloud-shadow.texture.aya",
            _level100Terrain, (ShaderMaterial)terrain.MaterialOverride);
        _level100Sky = GetNode<MeshInstance3D>("RetailLevel100KempyCube25");
        _level100Sun = Level100SunAsset.Create(_level100Terrain,
            GetNode<MeshInstance3D>("RetailLevel100SunSprite"));
        _level100StaticWorld = Level100StaticWorldAsset.BindScene(
            GetNode<Node3D>("RetailLevel100StaticWorld"), _level100Terrain);
        _playerRoot = GetNode<Node3D>("PlayerVisual");
        _playerBodyPivot = _playerRoot.GetNode<Node3D>("BodyPivot");
        _walkerAsset = RetailAquilaWalkerAsset.BindWalker(
            _playerBodyPivot.GetNode<Node3D>("RetailAquilaWalker"), _level100Terrain);
        _jetAsset = RetailAquilaWalkerAsset.BindJet(
            _playerBodyPivot.GetNode<Node3D>("RetailAquilaJet"), _level100Terrain);
        _camera = GetNode<Camera3D>("RetailOpeningAndFirstPersonCamera");
        _cockpitAsset = RetailAquilaWalkerAsset.BindCockpit(
            _camera.GetNode<Node3D>("RetailAquilaCockpit"), _level100Terrain);
        foreach (Node child in GetNode("ActorMeshes").GetChildren())
        {
            var source = (MeshInstance3D)child;
            var binding = new Level100TargetVisualBinding(
                source.GetMeta("definition").AsString(), source.GetMeta("mesh_binding").AsString());
            _level100TargetAssets.Add(binding, source.Mesh);
        }
        _entityPresentation = GetNode("EntityPresentation");
        BuildPulseCannonPresentation();
        ConfigureEntityPresentation(snapshot);
        UpdateRetailPixelCentreOffset();
    }

    internal void AddImportedActorResources()
    {
        var meshes = new Node3D { Name = "ActorMeshes", Visible = false };
        meshes.SetMeta("purpose", "Production meshes for later script-spawned actors; not additional actors");
        AddChild(meshes);
        int ordinal = 0;
        foreach ((Level100TargetVisualBinding binding, Mesh mesh) in _level100TargetAssets)
        {
            var node = new MeshInstance3D { Name = $"Mesh{ordinal++}", Mesh = mesh };
            node.SetMeta("definition", binding.DefinitionName);
            node.SetMeta("mesh_binding", binding.MeshBinding);
            meshes.AddChild(node);
        }
    }
}
