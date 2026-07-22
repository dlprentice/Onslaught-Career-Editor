// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

internal sealed class Level100HeightFieldAsset
{
    public const float PlayerStartX =
        Level100Terrain.PlayerStartRetailXFixed /
        (float)Level100Terrain.FixedPointUnitsPerRetailUnit;
    public const float PlayerStartZ =
        Level100Terrain.PlayerStartRetailYFixed /
        (float)Level100Terrain.FixedPointUnitsPerRetailUnit;
    public const float PlayerStartElevation =
        Level100Terrain.PlayerStartReferenceElevationMillimeters / 1_000f;

    private const int TileCountPerAxis = 64;
    private const int TileWidth = 8;
    private const int MapExtent = TileCountPerAxis * TileWidth;
    private const int HighDetailVertexCountPerAxis = MapExtent + 1;

    private readonly Level100Terrain _terrain;

    private Level100HeightFieldAsset(Level100Terrain terrain)
    {
        _terrain = terrain;
        MixerSet = terrain.MixerSet;
        SkyCube = terrain.SkyCube;
        DetailTexture = terrain.DetailTexture;
        WaterLevel = terrain.WaterLevel;
        WaterTexture = terrain.WaterTexture;
        FogColor = ToColor(terrain.FogColorRgb24);
        FogDensity = terrain.FogDensity;
        SunColor = ToColor(terrain.SunColorRgb24);
        AntiSunColor = ToColor(terrain.AntiSunColorRgb24);
        AmbientColor = ToColor(terrain.AmbientColorRgb24);
        SunColorRgb24 = terrain.SunColorRgb24;
        AntiSunColorRgb24 = terrain.AntiSunColorRgb24;
        AmbientColorRgb24 = terrain.AmbientColorRgb24;

        var beaSunPosition = new Vector3(
            terrain.SunPositionX,
            terrain.SunPositionY,
            terrain.SunPositionZ);
        Vector3 beaLightDirection = -beaSunPosition.Normalized();
        SunlightDirection = new Vector3(
            beaLightDirection.X,
            -beaLightDirection.Z,
            -beaLightDirection.Y);
        Mesh = BuildHighDetailMesh();
    }

    public ArrayMesh Mesh { get; }

    public int VertexCount => HighDetailVertexCountPerAxis * HighDetailVertexCountPerAxis;

    public int TriangleCount => MapExtent * MapExtent * 2;

    public byte MixerSet { get; }

    public byte SkyCube { get; }

    public byte DetailTexture { get; }

    public float WaterLevel { get; }

    public float WaterRelativeHeight => PlayerStartElevation - WaterLevel;

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

    public static Level100HeightFieldAsset Load() => new(Level100Terrain.Instance);

    public float SampleRelativeHeight(float relativeX, float relativeZ) =>
        PlayerStartElevation - SampleRetailHeight(relativeX + PlayerStartX, relativeZ + PlayerStartZ);

    private ArrayMesh BuildHighDetailMesh()
    {
        var vertices = new Vector3[VertexCount];
        var normals = new Vector3[VertexCount];
        var textureCoordinates = new Vector2[VertexCount];
        var indices = new int[TriangleCount * 3];

        int vertexIndex = 0;
        for (int z = 0; z <= MapExtent; z++)
        {
            for (int x = 0; x <= MapExtent; x++)
            {
                float height = PlayerStartElevation - SampleGridRetailHeight(x, z);
                vertices[vertexIndex] = new Vector3(x - PlayerStartX, height, PlayerStartZ - z);

                int leftX = Math.Max(0, x - 1);
                int rightX = Math.Min(MapExtent, x + 1);
                int backZ = Math.Max(0, z - 1);
                int forwardZ = Math.Min(MapExtent, z + 1);
                float left = SampleGridRetailHeight(leftX, z);
                float right = SampleGridRetailHeight(rightX, z);
                float back = SampleGridRetailHeight(x, backZ);
                float forward = SampleGridRetailHeight(x, forwardZ);
                normals[vertexIndex] = new Vector3(
                    (right - left) / (rightX - leftX),
                    1f,
                    (back - forward) / (forwardZ - backZ)).Normalized();
                textureCoordinates[vertexIndex] = new Vector2(
                    x / (float)MapExtent,
                    z / (float)MapExtent);
                vertexIndex++;
            }
        }

        int index = 0;
        for (int z = 0; z < MapExtent; z++)
        {
            for (int x = 0; x < MapExtent; x++)
            {
                int topLeft = (z * HighDetailVertexCountPerAxis) + x;
                int bottomLeft = topLeft + HighDetailVertexCountPerAxis;
                indices[index++] = topLeft;
                indices[index++] = bottomLeft;
                indices[index++] = topLeft + 1;
                indices[index++] = topLeft + 1;
                indices[index++] = bottomLeft;
                indices[index++] = bottomLeft + 1;
            }
        }

        var arrays = new Godot.Collections.Array();
        arrays.Resize((int)Godot.Mesh.ArrayType.Max);
        arrays[(int)Godot.Mesh.ArrayType.Vertex] = vertices;
        arrays[(int)Godot.Mesh.ArrayType.Normal] = normals;
        arrays[(int)Godot.Mesh.ArrayType.TexUV] = textureCoordinates;
        arrays[(int)Godot.Mesh.ArrayType.Index] = indices;

        var mesh = new ArrayMesh();
        mesh.AddSurfaceFromArrays(Godot.Mesh.PrimitiveType.Triangles, arrays);
        return mesh;
    }

    private float SampleRetailHeight(float x, float z)
    {
        int fixedX = ToFixedCoordinate(x);
        int fixedZ = ToFixedCoordinate(z);
        return _terrain.SampleHeightUnitsAtFixed(fixedX, fixedZ) * _terrain.HeightScale;
    }

    private float SampleGridRetailHeight(int x, int z) =>
        _terrain.SampleGridHeightUnits(x, z) * _terrain.HeightScale;

    private static int ToFixedCoordinate(float coordinate)
    {
        float clamped = Math.Clamp(coordinate, 0f, MathF.BitDecrement(MapExtent));
        return (int)MathF.Floor(clamped * Level100Terrain.FixedPointUnitsPerRetailUnit);
    }

    private static Color ToColor(uint rgb) => new(
        ((rgb >> 16) & 0xFF) / 255f,
        ((rgb >> 8) & 0xFF) / 255f,
        (rgb & 0xFF) / 255f);
}
