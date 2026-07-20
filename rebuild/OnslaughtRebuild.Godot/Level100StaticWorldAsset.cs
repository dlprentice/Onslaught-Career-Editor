// SPDX-License-Identifier: GPL-3.0-or-later

using System.Security.Cryptography;
using System.Text.Json;
using Godot;

namespace OnslaughtRebuild.GodotClient;

internal sealed class Level100StaticWorldAsset
{
    private const string ManifestPath =
        "res://Assets/Level100/StaticWorld/level100-static-world.json";
    private const string ManifestSha256 =
        "6DBD271DF598F2A6940416C849E42BFC655CC368DCA9959EB713D93486F920FB";
    private const string SourceArchiveSha256 =
        "ED6350C0E214D00AB1BF6A7BD137FBA3E77D0AFE19A6DC4C0607F56AC037496A";
    private const string StaticResourcePrefix = "res://Assets/Level100/StaticWorld/";

    private Level100StaticWorldAsset(
        Node3D root,
        IReadOnlyList<MeshInstance3D> objects,
        int surfaceCount,
        int pineInstanceCount,
        MeshInstance3D water)
    {
        Root = root;
        Objects = objects;
        SurfaceCount = surfaceCount;
        PineInstanceCount = pineInstanceCount;
        Water = water;
    }

    public Node3D Root { get; }

    public IReadOnlyList<MeshInstance3D> Objects { get; }

    public int SurfaceCount { get; }

    public int PineInstanceCount { get; }

    public MeshInstance3D Water { get; }

    public static Level100StaticWorldAsset Load(Level100HeightFieldAsset terrain)
    {
        Manifest manifest = LoadManifest();
        ValidateManifest(manifest, terrain);

        var root = new Node3D { Name = "RetailLevel100StaticWorld" };
        var textures = new Dictionary<string, Texture2D>(StringComparer.Ordinal);
        foreach ((string key, TextureDefinition definition) in manifest.Textures)
        {
            textures.Add(key, LoadTexture(definition));
        }

        var materials = textures.ToDictionary(
            pair => pair.Key,
            pair => (Material)RetailFixedFunctionMaterial.Create(pair.Value, terrain),
            StringComparer.Ordinal);
        var meshes = new Dictionary<string, ArrayMesh>(StringComparer.Ordinal);
        foreach ((string key, MeshDefinition definition) in manifest.Meshes)
        {
            var surfaceMaterials = definition.Materials.ToDictionary(
                pair => pair.Key,
                pair => materials[pair.Value],
                StringComparer.Ordinal);
            ArrayMesh mesh = CuratedObjMeshLoader.Load(definition.ResourcePath, surfaceMaterials);
            meshes.Add(key, mesh);
        }

        var objects = new List<MeshInstance3D>(manifest.Objects.Length);
        foreach (WorldObject worldObject in manifest.Objects.OrderBy(item => item.Ordinal))
        {
            MeshDefinition meshDefinition = manifest.Meshes[worldObject.Mesh];
            float retailX = checked((float)worldObject.RetailPosition[0]);
            float retailY = checked((float)worldObject.RetailPosition[1]);
            float retailZ = checked((float)worldObject.RetailPosition[2]);
            float relativeX = retailX - Level100HeightFieldAsset.PlayerStartX;
            float relativeZ = retailY - Level100HeightFieldAsset.PlayerStartZ;
            float relativeHeight = Math.Max(
                Level100HeightFieldAsset.PlayerStartElevation - retailZ,
                Math.Max(
                    terrain.SampleRelativeHeight(relativeX, relativeZ),
                    terrain.WaterRelativeHeight));

            var objectRoot = new Node3D
            {
                Name = $"RetailWorldObject{worldObject.Ordinal:D2}",
                Position = new Vector3(
                    relativeX,
                    relativeHeight + checked((float)meshDefinition.BaseClearance),
                    -relativeZ),
                Rotation = new Vector3(0f, checked((float)worldObject.Yaw), 0f),
            };
            var geometry = new MeshInstance3D
            {
                Name = $"{worldObject.Name}Geometry",
                Mesh = meshes[worldObject.Mesh],
                RotationDegrees = new Vector3(-90f, 0f, 0f),
            };
            objectRoot.AddChild(geometry);
            root.AddChild(objectRoot);
            objects.Add(geometry);
        }

        int pineCount = AddPines(root, manifest, terrain, meshes);
        MeshInstance3D water = AddWater(root, manifest, terrain, textures);
        int surfaceCount = objects.Sum(item => item.Mesh?.GetSurfaceCount() ?? 0);
        return new Level100StaticWorldAsset(root, objects, surfaceCount, pineCount, water);
    }

    private static int AddPines(
        Node3D root,
        Manifest manifest,
        Level100HeightFieldAsset terrain,
        IReadOnlyDictionary<string, ArrayMesh> meshes)
    {
        int total = 0;
        for (int variant = 0; variant < 4; variant++)
        {
            double[][] instances = manifest.Pines
                .Where(item => checked((int)item[2]) == variant)
                .ToArray();
            string meshKey = $"pinesnow{variant}";
            float baseClearance = checked((float)manifest.Meshes[meshKey].BaseClearance);
            var multiMesh = new MultiMesh
            {
                TransformFormat = MultiMesh.TransformFormatEnum.Transform3D,
                Mesh = meshes[meshKey],
                InstanceCount = instances.Length,
            };
            var meshBasis = new Basis(Vector3.Right, -Mathf.Pi / 2f);
            for (int index = 0; index < instances.Length; index++)
            {
                float retailX = checked((float)instances[index][0]);
                float retailY = checked((float)instances[index][1]);
                float relativeX = retailX - Level100HeightFieldAsset.PlayerStartX;
                float relativeZ = retailY - Level100HeightFieldAsset.PlayerStartZ;
                float height = Math.Max(
                    terrain.SampleRelativeHeight(relativeX, relativeZ),
                    terrain.WaterRelativeHeight);
                multiMesh.SetInstanceTransform(
                    index,
                    new Transform3D(
                        meshBasis,
                        new Vector3(relativeX, height + baseClearance, -relativeZ)));
            }
            root.AddChild(new MultiMeshInstance3D
            {
                Name = $"RetailPineSnow{variant}Instances",
                Multimesh = multiMesh,
            });
            total += instances.Length;
        }
        return total;
    }

    private static MeshInstance3D AddWater(
        Node3D root,
        Manifest manifest,
        Level100HeightFieldAsset terrain,
        IReadOnlyDictionary<string, Texture2D> textures)
    {
        var water = new MeshInstance3D
        {
            Name = "RetailLevel100Water",
            Mesh = new PlaneMesh { Size = new Vector2(512f, 512f) },
            MaterialOverride = RetailFixedFunctionMaterial.CreateWater(
                textures[manifest.Water.Texture]),
            Position = new Vector3(
                256f - Level100HeightFieldAsset.PlayerStartX,
                terrain.WaterRelativeHeight,
                Level100HeightFieldAsset.PlayerStartZ - 256f),
            CastShadow = GeometryInstance3D.ShadowCastingSetting.Off,
        };
        root.AddChild(water);
        return water;
    }

    private static Texture2D LoadTexture(TextureDefinition definition)
    {
        if (!Enum.TryParse(
                definition.Compression,
                ignoreCase: false,
                out CuratedAyaTextureLoader.Compression compression))
        {
            throw new InvalidDataException(
                $"Static-world texture has unsupported compression '{definition.Compression}'.");
        }
        return CuratedAyaTextureLoader.Load(
            definition.ResourcePath,
            definition.Width,
            definition.Height,
            compression);
    }

    private static Manifest LoadManifest()
    {
        byte[] source = Godot.FileAccess.GetFileAsBytes(ManifestPath);
        if (source.Length is < 1 or > 512_000 ||
            !StringComparer.Ordinal.Equals(
                Convert.ToHexString(SHA256.HashData(source)),
                ManifestSha256))
        {
            throw new InvalidDataException(
                "The locally materialized Level 100 static-world manifest is missing or changed.");
        }
        return JsonSerializer.Deserialize<Manifest>(source, new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true,
        }) ?? throw new InvalidDataException("The Level 100 static-world manifest is empty.");
    }

    private static void ValidateManifest(Manifest manifest, Level100HeightFieldAsset terrain)
    {
        if (!StringComparer.Ordinal.Equals(manifest.Schema, "onslaught.level100-static-world.v1") ||
            !StringComparer.OrdinalIgnoreCase.Equals(
                manifest.SourceArchiveSha256,
                SourceArchiveSha256) ||
            manifest.UnitRecordCount != 35 ||
            manifest.VisibleObjectCount != 33 ||
            manifest.SuppressedFernCount != 753 ||
            manifest.PineInstanceCount != 1481 ||
            manifest.Objects.Length != 33 ||
            manifest.Pines.Length != 1481 ||
            manifest.Meshes.Count != 28 ||
            manifest.Textures.Count != 26 ||
            manifest.Water.TextureIndex != terrain.WaterTexture ||
            BitConverter.SingleToInt32Bits(checked((float)manifest.Water.Level)) !=
                BitConverter.SingleToInt32Bits(terrain.WaterLevel) ||
            !manifest.Textures.ContainsKey(manifest.Water.Texture))
        {
            throw new InvalidDataException("Level 100 static-world identity or counts do not match retail.");
        }

        int[] variants = new int[4];
        foreach (double[] pine in manifest.Pines)
        {
            if (pine.Length != 3 || !pine.All(double.IsFinite))
            {
                throw new InvalidDataException("Level 100 has an invalid pine instance.");
            }
            int variant = checked((int)pine[2]);
            if (variant is < 0 or > 3 || pine[2] != variant)
            {
                throw new InvalidDataException("Level 100 has an invalid pine variant.");
            }
            variants[variant]++;
        }
        if (!variants.SequenceEqual([383, 355, 318, 425]))
        {
            throw new InvalidDataException("Level 100 pine variant counts do not match retail.");
        }

        if (manifest.Objects.Select(item => item.Ordinal).Distinct().Count() != 33)
        {
            throw new InvalidDataException("Level 100 static-world ordinals are not unique.");
        }
        foreach (WorldObject worldObject in manifest.Objects)
        {
            if (worldObject.RetailPosition.Length != 3 ||
                !worldObject.RetailPosition.All(double.IsFinite) ||
                !double.IsFinite(worldObject.Yaw) ||
                !manifest.Meshes.ContainsKey(worldObject.Mesh))
            {
                throw new InvalidDataException("Level 100 has an invalid static-world object.");
            }
        }
        foreach (MeshDefinition mesh in manifest.Meshes.Values)
        {
            RequireOwnedResource(mesh.ResourcePath);
            if (!double.IsFinite(mesh.BaseClearance) || mesh.Materials.Count == 0 ||
                mesh.Materials.Values.Any(key => !manifest.Textures.ContainsKey(key)))
            {
                throw new InvalidDataException("Level 100 has an invalid static-world mesh.");
            }
        }
        foreach (TextureDefinition texture in manifest.Textures.Values)
        {
            RequireOwnedResource(texture.ResourcePath);
            if (texture.Width is < 1 or > 1024 || texture.Height is < 1 or > 1024)
            {
                throw new InvalidDataException("Level 100 has invalid static-world texture dimensions.");
            }
        }
    }

    private static void RequireOwnedResource(string resourcePath)
    {
        if (!resourcePath.StartsWith(StaticResourcePrefix, StringComparison.Ordinal) ||
            resourcePath.Contains("..", StringComparison.Ordinal))
        {
            throw new InvalidDataException("Level 100 static-world resource escaped its local owner.");
        }
    }

    private sealed record Manifest
    {
        public string Schema { get; init; } = string.Empty;
        public string SourceArchiveSha256 { get; init; } = string.Empty;
        public int UnitRecordCount { get; init; }
        public int VisibleObjectCount { get; init; }
        public int SuppressedFernCount { get; init; }
        public int PineInstanceCount { get; init; }
        public Dictionary<string, MeshDefinition> Meshes { get; init; } = [];
        public Dictionary<string, TextureDefinition> Textures { get; init; } = [];
        public WorldObject[] Objects { get; init; } = [];
        public double[][] Pines { get; init; } = [];
        public WaterDefinition Water { get; init; } = new();
    }

    private sealed record MeshDefinition
    {
        public double BaseClearance { get; init; }
        public Dictionary<string, string> Materials { get; init; } = [];
        public string ResourcePath { get; init; } = string.Empty;
    }

    private sealed record TextureDefinition
    {
        public string Compression { get; init; } = string.Empty;
        public int Height { get; init; }
        public string ResourcePath { get; init; } = string.Empty;
        public int Width { get; init; }
    }

    private sealed record WorldObject
    {
        public string Mesh { get; init; } = string.Empty;
        public string Name { get; init; } = string.Empty;
        public int Ordinal { get; init; }
        public double[] RetailPosition { get; init; } = [];
        public double Yaw { get; init; }
    }

    private sealed record WaterDefinition
    {
        public double Level { get; init; }
        public string Texture { get; init; } = string.Empty;
        public int TextureIndex { get; init; }
    }
}

internal static class RetailFixedFunctionMaterial
{
    private static Shader? _objectShader;
    private static Shader? _waterShader;

    private const string ShaderCode = """
        shader_type spatial;
        render_mode unshaded, cull_back;

        uniform sampler2D albedo_texture : filter_linear_mipmap, repeat_enable;
        uniform vec3 ambient_color;
        uniform vec3 sun_color;
        uniform vec3 anti_sun_color;
        uniform vec3 sunlight_direction;
        varying vec3 world_normal;

        vec3 srgb_to_linear(vec3 color) {
            vec3 low = color / 12.92;
            vec3 high = pow((color + vec3(0.055)) / 1.055, vec3(2.4));
            return mix(low, high, step(vec3(0.04045), color));
        }

        void vertex() {
            world_normal = normalize(mat3(MODEL_MATRIX) * NORMAL);
        }

        void fragment() {
            vec4 texture_color = texture(albedo_texture, UV);
            if (texture_color.a < 0.5) {
                discard;
            }
            vec3 normal = normalize(world_normal);
            float sun = max(dot(normal, -sunlight_direction), 0.0);
            float anti_sun = max(dot(normal, sunlight_direction), 0.0);
            vec3 light_color = ambient_color + (sun_color * sun) +
                (anti_sun_color * anti_sun);
            vec3 retail_color = min(texture_color.rgb * light_color * 2.0, vec3(1.0));
            ALBEDO = srgb_to_linear(retail_color);
        }
        """;

    private const string WaterShaderCode = """
        shader_type spatial;
        render_mode unshaded, cull_disabled;

        uniform sampler2D water_texture : filter_linear_mipmap, repeat_disable;

        vec3 srgb_to_linear(vec3 color) {
            vec3 low = color / 12.92;
            vec3 high = pow((color + vec3(0.055)) / 1.055, vec3(2.4));
            return mix(low, high, step(vec3(0.04045), color));
        }

        void fragment() {
            ALBEDO = srgb_to_linear(texture(water_texture, UV).rgb);
        }
        """;

    public static ShaderMaterial Create(Texture2D texture, Level100HeightFieldAsset terrain)
    {
        var material = new ShaderMaterial
        {
            Shader = _objectShader ??= new Shader { Code = ShaderCode },
        };
        material.SetShaderParameter("albedo_texture", texture);
        material.SetShaderParameter("ambient_color", ToVector(terrain.AmbientColorRgb24, 255f));
        material.SetShaderParameter("sun_color", ToVector(terrain.SunColorRgb24, 256f));
        material.SetShaderParameter("anti_sun_color", ToVector(terrain.AntiSunColorRgb24, 256f));
        material.SetShaderParameter("sunlight_direction", terrain.SunlightDirection);
        return material;
    }

    public static ShaderMaterial CreateWater(Texture2D texture)
    {
        var material = new ShaderMaterial
        {
            Shader = _waterShader ??= new Shader { Code = WaterShaderCode },
        };
        material.SetShaderParameter("water_texture", texture);
        return material;
    }

    private static Vector3 ToVector(uint rgb, float divisor) => new(
        ((rgb >> 16) & 0xFF) / divisor,
        ((rgb >> 8) & 0xFF) / divisor,
        (rgb & 0xFF) / divisor);
}
