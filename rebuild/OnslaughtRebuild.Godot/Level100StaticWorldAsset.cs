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
        "ACB4FFA4532340AF9584614E66EC43AF9993570CFC0A34DEB00F58D1D41B3B71";
    private const string SourceArchiveSha256 =
        "ED6350C0E214D00AB1BF6A7BD137FBA3E77D0AFE19A6DC4C0607F56AC037496A";
    private const string StaticResourcePrefix = "res://Assets/Level100/StaticWorld/";

    private Level100StaticWorldAsset(
        Node3D root,
        IReadOnlyList<MeshInstance3D> objects,
        int surfaceCount,
        int pineInstanceCount,
        Level100WaterAsset water)
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

    public Level100WaterAsset Water { get; }

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

        var meshes = new Dictionary<string, ArrayMesh>(StringComparer.Ordinal);
        foreach ((string key, MeshDefinition definition) in manifest.Meshes)
        {
            var surfaceMaterials = definition.Materials.ToDictionary(
                pair => pair.Key,
                pair => (Material)CreateMaterial(
                    pair.Value,
                    textures,
                    manifest.Textures,
                    terrain),
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
        Level100WaterAsset water = AddWater(root, manifest, terrain, textures);
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

    private static Level100WaterAsset AddWater(
        Node3D root,
        Manifest manifest,
        Level100HeightFieldAsset terrain,
        IReadOnlyDictionary<string, Texture2D> textures)
    {
        Level100WaterAsset water = Level100WaterAsset.Create(
            terrain,
            textures[manifest.Water.ReflectionTexture],
            textures[manifest.Water.CausticTexture],
            textures[manifest.Water.WavesTexture],
            textures[manifest.Water.SunBlobTexture],
            textures[manifest.Water.SunReflectionTexture],
            manifest.Water.SurfaceResourcePath,
            manifest.Water.SurfaceSha256);
        root.AddChild(water.Root);
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

    private static ShaderMaterial CreateMaterial(
        MaterialDefinition definition,
        IReadOnlyDictionary<string, Texture2D> textures,
        IReadOnlyDictionary<string, TextureDefinition> textureDefinitions,
        Level100HeightFieldAsset terrain)
    {
        RetailTextureLayer?[] layers = definition.Layers
            .Select(layer => layer is null
                ? null
                : new RetailTextureLayer(
                    textures[layer.Texture],
                    checked((float)layer.Opacity),
                    new Vector2(
                        checked((float)layer.Offset[0]),
                        checked((float)layer.Offset[1])),
                    new Vector2(
                        checked((float)layer.Scale[0]),
                        checked((float)layer.Scale[1])),
                    textureDefinitions[layer.Texture].BlendTextureAlpha))
            .ToArray();
        return RetailFixedFunctionMaterial.Create(layers, terrain);
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
        if (!StringComparer.Ordinal.Equals(manifest.Schema, "onslaught.level100-static-world.v4") ||
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
            manifest.Textures.Count != 33 ||
            !manifest.Textures.TryGetValue(
                "meshtex-a8-fb-hangermorebits-lit",
                out TextureDefinition? blendTexture) ||
            blendTexture is null ||
            !blendTexture.BlendTextureAlpha ||
            manifest.Textures.Values.Count(texture => texture.BlendTextureAlpha) != 1 ||
            manifest.Water.TextureIndex != terrain.WaterTexture ||
            BitConverter.SingleToInt32Bits(checked((float)manifest.Water.Level)) !=
                BitConverter.SingleToInt32Bits(terrain.WaterLevel) ||
            !manifest.Textures.ContainsKey(manifest.Water.ReflectionTexture) ||
            !manifest.Textures.ContainsKey(manifest.Water.CausticTexture) ||
            !manifest.Textures.ContainsKey(manifest.Water.WavesTexture) ||
            !manifest.Textures.ContainsKey(manifest.Water.SunBlobTexture) ||
            !manifest.Textures.ContainsKey(manifest.Water.SunReflectionTexture) ||
            string.IsNullOrWhiteSpace(manifest.Water.SurfaceSha256))
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
                mesh.Materials.Values.Any(material =>
                    !IsValidMaterial(material, manifest.Textures)))
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
        RequireOwnedResource(manifest.Water.SurfaceResourcePath);
    }

    private static bool IsValidMaterial(
        MaterialDefinition material,
        IReadOnlyDictionary<string, TextureDefinition> textures)
    {
        if (material.Layers.Length != 6 || material.Layers[0] is null)
        {
            return false;
        }
        for (int index = 0; index < material.Layers.Length; index++)
        {
            MaterialLayerDefinition? layer = material.Layers[index];
            if (layer is null)
            {
                continue;
            }
            if (!textures.ContainsKey(layer.Texture) ||
                !double.IsFinite(layer.Opacity) ||
                layer.Opacity is < 0.0 or > 1.0 ||
                layer.Offset.Length != 2 ||
                layer.Scale.Length != 2 ||
                !layer.Offset.All(double.IsFinite) ||
                !layer.Scale.All(double.IsFinite) ||
                layer.Scale.Any(value => value is < 0.0 or > 100.0) ||
                (index == 4 && layer.Scale.Any(value => value <= 0.0)))
            {
                return false;
            }
        }
        return true;
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
        public Dictionary<string, MaterialDefinition> Materials { get; init; } = [];
        public string ResourcePath { get; init; } = string.Empty;
    }

    private sealed record MaterialDefinition
    {
        public MaterialLayerDefinition?[] Layers { get; init; } = [];
    }

    private sealed record MaterialLayerDefinition
    {
        public double[] Offset { get; init; } = [];
        public double Opacity { get; init; }
        public double[] Scale { get; init; } = [];
        public string Texture { get; init; } = string.Empty;
    }

    private sealed record TextureDefinition
    {
        public bool BlendTextureAlpha { get; init; }
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
        public string CausticTexture { get; init; } = string.Empty;
        public double Level { get; init; }
        public string ReflectionTexture { get; init; } = string.Empty;
        public string SunBlobTexture { get; init; } = string.Empty;
        public string SunReflectionTexture { get; init; } = string.Empty;
        public string SurfaceResourcePath { get; init; } = string.Empty;
        public string SurfaceSha256 { get; init; } = string.Empty;
        public int TextureIndex { get; init; }
        public string WavesTexture { get; init; } = string.Empty;
    }
}

internal sealed record RetailTextureLayer(
    Texture2D Texture,
    float Opacity,
    Vector2 Offset,
    Vector2 Scale,
    bool BlendTextureAlpha = false);

internal static class RetailFixedFunctionMaterial
{
    private static Shader? _objectShader;

    private const string ShaderCode = """
        shader_type spatial;
        render_mode unshaded, cull_back;

        uniform sampler2D base_texture : filter_linear_mipmap, repeat_enable;
        uniform sampler2D dot3_texture : filter_linear_mipmap, repeat_enable;
        uniform sampler2D reflection_texture : filter_linear_mipmap, repeat_disable;
        uniform sampler2D overlay_texture : filter_linear_mipmap, repeat_enable;
        uniform float has_dot3;
        uniform float has_reflection;
        uniform float has_overlay;
        uniform float base_blend_texture_alpha;
        uniform vec2 dot3_offset;
        uniform vec2 dot3_scale;
        uniform float reflection_opacity;
        uniform vec2 overlay_offset;
        uniform vec2 overlay_scale;
        uniform float overlay_opacity;
        uniform vec3 ambient_color;
        uniform vec3 sun_color;
        uniform vec3 anti_sun_color;
        uniform vec3 sunlight_direction;
        uniform vec3 fog_color;
        uniform float fog_density;
        varying vec3 world_normal;
        varying vec3 view_normal;
        varying vec3 model_light_direction;

        vec3 retail_output(vec3 color) {
            if (OUTPUT_IS_SRGB) {
                return color;
            }
            vec3 low = color / 12.92;
            vec3 high = pow((color + vec3(0.055)) / 1.055, vec3(2.4));
            return mix(low, high, step(vec3(0.04045), color));
        }

        vec3 apply_retail_fog(vec3 color, float view_depth) {
            float visibility = clamp(exp(-fog_density * view_depth), 0.0, 1.0);
            return mix(fog_color, color, visibility);
        }

        void vertex() {
            world_normal = normalize(mat3(MODEL_MATRIX) * NORMAL);
            view_normal = normalize(mat3(VIEW_MATRIX) * world_normal);
            model_light_direction = normalize(
                transpose(mat3(MODEL_MATRIX)) * sunlight_direction);
        }

        void fragment() {
            vec4 texture_color = texture(base_texture, UV);
            if (base_blend_texture_alpha < 0.5 && texture_color.a < 0.5) {
                discard;
            }
            vec3 normal = normalize(world_normal);
            float sun = max(dot(normal, -sunlight_direction), 0.0);
            float anti_sun = max(dot(normal, sunlight_direction), 0.0);
            vec3 light_color = ambient_color + (sun_color * sun) +
                (anti_sun_color * anti_sun);
            vec3 retail_color = min(texture_color.rgb * light_color * 2.0, vec3(1.0));
            if (base_blend_texture_alpha > 0.5) {
                retail_color = mix(retail_color, texture_color.rgb, texture_color.a);
            }

            if (has_dot3 > 0.5) {
                vec3 dot3_sample = texture(
                    dot3_texture,
                    (UV * dot3_scale) + dot3_offset).rgb;
                vec3 encoded_light = round(clamp(
                    (model_light_direction * 127.0) + vec3(128.0),
                    vec3(0.0),
                    vec3(255.0))) / 255.0;
                float dot3_value = clamp(
                    4.0 * dot(dot3_sample - vec3(0.5), encoded_light - vec3(0.5)),
                    0.0,
                    1.0);
                retail_color = vec3(dot3_value);
            }

            if (has_reflection > 0.5) {
                vec3 reflection_vector = reflect(
                    normalize(VERTEX),
                    normalize(view_normal));
                vec2 reflection_uv = clamp(
                    vec2(
                        (reflection_vector.x * 0.5) + 0.5,
                        (reflection_vector.y * -0.5) + 0.5),
                    vec2(0.0),
                    vec2(1.0));
                vec4 reflection_color = texture(reflection_texture, reflection_uv);
                float reflection_alpha = clamp(
                    reflection_color.a * reflection_opacity,
                    0.0,
                    1.0);
                retail_color = mix(retail_color, reflection_color.rgb, reflection_alpha);
            }

            if (has_overlay > 0.5) {
                vec4 overlay_color = texture(
                    overlay_texture,
                    (UV * overlay_scale) + overlay_offset);
                float overlay_alpha = clamp(
                    overlay_color.a * overlay_opacity,
                    0.0,
                    1.0);
                retail_color = mix(retail_color, overlay_color.rgb, overlay_alpha);
            }

            retail_color = apply_retail_fog(retail_color, max(-VERTEX.z, 0.0));
            ALBEDO = retail_output(retail_color);
        }
        """;

    public static ShaderMaterial Create(Texture2D texture, Level100HeightFieldAsset terrain)
    {
        return Create(
            [
                new RetailTextureLayer(texture, 1f, Vector2.Zero, Vector2.One),
                null,
                null,
                null,
                null,
                null,
            ],
            terrain);
    }

    public static ShaderMaterial Create(
        IReadOnlyList<RetailTextureLayer?> layers,
        Level100HeightFieldAsset terrain)
    {
        if (layers.Count != 6 || layers[0] is not RetailTextureLayer baseLayer)
        {
            throw new InvalidDataException("Retail material requires one base layer and six exact slots.");
        }
        RetailTextureLayer? dot3Layer = layers[1];
        RetailTextureLayer? reflectionLayer = layers[2];
        RetailTextureLayer? overlayLayer = layers[4];
        var material = new ShaderMaterial
        {
            Shader = _objectShader ??= new Shader { Code = ShaderCode },
        };
        material.SetShaderParameter("base_texture", baseLayer.Texture);
        material.SetShaderParameter("dot3_texture", dot3Layer?.Texture ?? baseLayer.Texture);
        material.SetShaderParameter("reflection_texture", reflectionLayer?.Texture ?? baseLayer.Texture);
        material.SetShaderParameter("overlay_texture", overlayLayer?.Texture ?? baseLayer.Texture);
        material.SetShaderParameter("has_dot3", dot3Layer is null ? 0f : 1f);
        material.SetShaderParameter("has_reflection", reflectionLayer is null ? 0f : 1f);
        material.SetShaderParameter("has_overlay", overlayLayer is null ? 0f : 1f);
        material.SetShaderParameter(
            "base_blend_texture_alpha",
            baseLayer.BlendTextureAlpha ? 1f : 0f);
        material.SetShaderParameter("dot3_offset", dot3Layer?.Offset ?? Vector2.Zero);
        material.SetShaderParameter("dot3_scale", dot3Layer?.Scale ?? Vector2.One);
        material.SetShaderParameter("reflection_opacity", reflectionLayer?.Opacity ?? 0f);
        material.SetShaderParameter("overlay_offset", overlayLayer?.Offset ?? Vector2.Zero);
        material.SetShaderParameter("overlay_scale", overlayLayer?.Scale ?? Vector2.One);
        material.SetShaderParameter("overlay_opacity", overlayLayer?.Opacity ?? 0f);
        material.SetShaderParameter("ambient_color", ToVector(terrain.AmbientColorRgb24, 255f));
        material.SetShaderParameter("sun_color", ToVector(terrain.SunColorRgb24, 256f));
        material.SetShaderParameter("anti_sun_color", ToVector(terrain.AntiSunColorRgb24, 256f));
        material.SetShaderParameter("sunlight_direction", terrain.SunlightDirection);
        material.SetShaderParameter("fog_color", new Vector3(
            terrain.FogColor.R,
            terrain.FogColor.G,
            terrain.FogColor.B));
        material.SetShaderParameter("fog_density", terrain.FogDensity);
        return material;
    }

    private static Vector3 ToVector(uint rgb, float divisor) => new(
        ((rgb >> 16) & 0xFF) / divisor,
        ((rgb >> 8) & 0xFF) / divisor,
        (rgb & 0xFF) / divisor);
}
