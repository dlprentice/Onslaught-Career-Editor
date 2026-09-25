// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Client;

namespace OnslaughtRebuild.GodotClient;

// Bind the production components without constructing a second world.
internal sealed partial class RetailAquilaWalkerAsset
{
    public static RetailAquilaWalkerAsset BindWalker(Node3D root, Level100HeightFieldAsset terrain) =>
        Configure("walker", "Walker", terrain, root);

    public static RetailAquilaWalkerAsset BindJet(Node3D root, Level100HeightFieldAsset terrain) =>
        Configure("jet", "Jet", terrain, root);

    public static RetailAquilaWalkerAsset BindCockpit(Node3D root, Level100HeightFieldAsset terrain) =>
        Configure("cockpit", "Cockpit", terrain, root);
}

internal sealed partial class Level100WaterAsset
{
    public static Level100WaterAsset BindScene(Node3D root, Level100HeightFieldAsset terrain) =>
        BindNativeScene(root, terrain);
}

internal sealed partial class Level100StaticWorldAsset
{
    public static Level100StaticWorldAsset BindScene(Node3D root, Level100HeightFieldAsset terrain)
    {
        Manifest manifest = LoadManifest();
        ValidateManifest(manifest, terrain);
        Level100StaticWorldAnimationSet animation =
            Level100StaticWorldAnimationManifest.Decode(LoadAnimationManifestBytes());
        var objects = new List<MeshInstance3D>(manifest.Objects.Length);
        var bindings = new List<Level100StaticWorldAnimationBinding>();
        foreach (WorldObject item in manifest.Objects.OrderBy(item => item.Ordinal))
        {
            Node3D placement = root.GetNode<Node3D>($"RetailWorldObject{item.Ordinal:D2}");
            MeshInstance3D geometry = placement.GetChildren().OfType<MeshInstance3D>().Single();
            objects.Add(geometry);
            if (animation.Meshes.TryGetValue(item.Mesh, out Level100StaticWorldMeshAnimation? mesh) &&
                mesh.Playback == Level100StaticWorldPlayback.CyclicLoop)
            {
                foreach (Level100StaticWorldAnimatedPart part in mesh.Parts)
                {
                    MeshInstance3D node = geometry.GetNode<MeshInstance3D>(
                        $"Part{part.Part:D2}-{SanitizeNodeName(part.Name)}");
                    bindings.Add(new Level100StaticWorldAnimationBinding(mesh, part, node));
                }
            }
        }

        int pineCount = 0;
        for (int variant = 0; variant < 4; variant++)
        {
            MultiMesh close = root.GetNode<MultiMeshInstance3D>(
                $"RetailPineSnow{variant}CloseMeshInstances").Multimesh;
            MultiMesh far = root.GetNode<MultiMeshInstance3D>(
                $"RetailPineSnow{variant}FarSixFaceInstances").Multimesh;
            if (close.InstanceCount != far.InstanceCount)
            {
                throw new InvalidDataException("Imported pine representations disagree.");
            }
            pineCount += close.InstanceCount;
        }
        if (pineCount != manifest.Pines.Length || bindings.Count == 0)
        {
            throw new InvalidDataException("Imported scenery lost pine or animation bindings.");
        }
        return new Level100StaticWorldAsset(root, objects,
            objects.Sum(node => node.Mesh?.GetSurfaceCount() ?? 0) +
            bindings.Sum(binding => binding.Node.Mesh?.GetSurfaceCount() ?? 0),
            pineCount,
            Level100WaterAsset.BindScene(root.GetNode<Node3D>("RetailLevel100Water"), terrain),
            new Level100StaticWorldAnimationDriver(animation.FramesPerSecond, bindings));
    }
}
