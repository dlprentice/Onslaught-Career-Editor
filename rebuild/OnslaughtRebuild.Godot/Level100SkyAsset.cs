// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;

namespace OnslaughtRebuild.GodotClient;

internal static class Level100SkyAsset
{
    private const float Radius = 500f;
    private const float HalfLowerExtent = 0.5f;
    private const float MinUv = 1f / 512f;
    private const float MaxUv = 511f / 512f;
    private const float SideBottomUv = 383.5f / 512f;

    // Steam's formatter indexes the five suffix pointers in this exact order.
    private static readonly string[] FaceNames = ["cent", "up", "right", "down", "left"];

    private static readonly Vector3[][] BeaFaceVertices =
    [
        [new(-1f, -1f, -1f), new(1f, -1f, -1f), new(-1f, 1f, -1f), new(1f, 1f, -1f)],
        [new(1f, 1f, -1f), new(1f, 1f, HalfLowerExtent), new(-1f, 1f, -1f), new(-1f, 1f, HalfLowerExtent)],
        [new(1f, -1f, -1f), new(1f, -1f, HalfLowerExtent), new(1f, 1f, -1f), new(1f, 1f, HalfLowerExtent)],
        [new(-1f, -1f, -1f), new(-1f, -1f, HalfLowerExtent), new(1f, -1f, -1f), new(1f, -1f, HalfLowerExtent)],
        [new(-1f, 1f, -1f), new(-1f, 1f, HalfLowerExtent), new(-1f, -1f, -1f), new(-1f, -1f, HalfLowerExtent)],
    ];

    private static readonly Vector2[] TopFaceUvs =
    [
        new(MinUv, MinUv),
        new(MaxUv, MinUv),
        new(MinUv, MaxUv),
        new(MaxUv, MaxUv),
    ];

    private static readonly Vector2[] SideFaceUvs =
    [
        new(MaxUv, MinUv),
        new(MaxUv, SideBottomUv),
        new(MinUv, MinUv),
        new(MinUv, SideBottomUv),
    ];

    public static MeshInstance3D Create(byte skyCube)
    {
        if (skyCube != 25)
        {
            throw new InvalidDataException("Level 100 does not select the retained Kempy cube 25.");
        }

        var mesh = new ArrayMesh();
        for (int faceIndex = 0; faceIndex < FaceNames.Length; faceIndex++)
        {
            Vector3[] vertices = BeaFaceVertices[faceIndex]
                .Select(ToGodotPosition)
                .ToArray();
            Vector2[] uvs = faceIndex == 0 ? TopFaceUvs : SideFaceUvs;
            int[] indices = [0, 1, 2, 2, 1, 3];
            var arrays = new Godot.Collections.Array();
            arrays.Resize((int)Godot.Mesh.ArrayType.Max);
            arrays[(int)Godot.Mesh.ArrayType.Vertex] = vertices;
            arrays[(int)Godot.Mesh.ArrayType.TexUV] = uvs;
            arrays[(int)Godot.Mesh.ArrayType.Index] = indices;
            mesh.AddSurfaceFromArrays(Godot.Mesh.PrimitiveType.Triangles, arrays);

            Texture2D texture = CuratedAyaTextureLoader.Load(
                $"res://Assets/Level100/Sky/cube25-{FaceNames[faceIndex]}.texture.aya",
                512,
                512,
                CuratedAyaTextureLoader.Compression.Dxt1);
            mesh.SurfaceSetMaterial(faceIndex, new StandardMaterial3D
            {
                AlbedoTexture = texture,
                ShadingMode = BaseMaterial3D.ShadingModeEnum.Unshaded,
                CullMode = BaseMaterial3D.CullModeEnum.Disabled,
                DisableFog = true,
                TextureFilter = BaseMaterial3D.TextureFilterEnum.LinearWithMipmaps,
            });
        }

        return new MeshInstance3D
        {
            Name = "RetailLevel100KempyCube25",
            Mesh = mesh,
        };
    }

    private static Vector3 ToGodotPosition(Vector3 beaPosition)
    {
        return new Vector3(
            beaPosition.X,
            -beaPosition.Z,
            beaPosition.Y) * Radius;
    }
}
