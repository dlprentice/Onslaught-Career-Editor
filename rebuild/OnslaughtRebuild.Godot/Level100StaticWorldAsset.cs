// SPDX-License-Identifier: GPL-3.0-or-later

using System.Security.Cryptography;
using System.Text.Json;
using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

internal sealed partial class Level100StaticWorldAsset
{
    private const string ManifestPath =
        "res://Assets/Level100/StaticWorld/level100-static-world.json";
    private const string ManifestSha256 =
        Level100ActorDefinitionManifest.ExpectedManifestSha256;
    private const string SourceArchiveSha256 =
        "ED6350C0E214D00AB1BF6A7BD137FBA3E77D0AFE19A6DC4C0607F56AC037496A";
    private const string SatTurretDefinition = "SAT Turret";
    private const string SatTurretMesh = "ft_sam";
    private const string StaticResourcePrefix = "res://Assets/Level100/StaticWorld/";
    private const string PineFarImposterShaderCode = """
        shader_type spatial;
        render_mode unshaded, cull_disabled;

        uniform sampler2D atlas : filter_nearest_mipmap, repeat_enable;
        uniform vec3 fog_color;
        uniform float fog_density;
        uniform float mesh_distance_squared;
        varying float face_alignment;
        varying float horizontal_distance_squared;
        varying float view_depth;

        vec3 retail_output(vec3 color) {
            if (OUTPUT_IS_SRGB) {
                return color;
            }
            vec3 low = color / 12.92;
            vec3 high = pow((color + vec3(0.055)) / 1.055, vec3(2.4));
            return mix(low, high, step(vec3(0.04045), color));
        }

        void vertex() {
            vec3 world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
            vec3 world_normal = normalize(mat3(MODEL_MATRIX) * NORMAL);
            face_alignment = dot(
                world_normal,
                CAMERA_POSITION_WORLD - world_position);
            vec2 horizontal_offset =
                MODEL_MATRIX[3].xz - CAMERA_POSITION_WORLD.xz;
            horizontal_distance_squared = dot(
                horizontal_offset,
                horizontal_offset);
            vec3 camera_position = (VIEW_MATRIX * vec4(world_position, 1.0)).xyz;
            view_depth = max(-camera_position.z, 0.0);
        }

        void fragment() {
            if (horizontal_distance_squared <= mesh_distance_squared ||
                face_alignment <= 0.0) {
                discard;
            }
            vec4 texel = texture(atlas, UV);
            if (texel.a < (8.0 / 255.0)) {
                discard;
            }
            float visibility = clamp(
                exp(-fog_density * view_depth),
                0.0,
                1.0);
            vec3 tree_color = min(texel.rgb * 2.0, vec3(1.0));
            ALBEDO = retail_output(mix(fog_color, tree_color, visibility));
        }
        """;
    private const string PineFastImposterShaderCode = """
        shader_type spatial;
        render_mode unshaded, cull_disabled;

        uniform sampler2D atlas : filter_nearest, repeat_enable;
        uniform float camera_facing;
        uniform vec3 fog_color;
        uniform float fog_density;
        varying float view_depth;

        vec3 retail_output(vec3 color) {
            if (OUTPUT_IS_SRGB) {
                return color;
            }
            vec3 low = color / 12.92;
            vec3 high = pow((color + vec3(0.055)) / 1.055, vec3(2.4));
            return mix(low, high, step(vec3(0.04045), color));
        }

        void vertex() {
            vec3 world_position;
            if (camera_facing > 0.5) {
                vec3 center = (MODEL_MATRIX * vec4(0.0, 0.0, 0.0, 1.0)).xyz;
                vec3 camera_right = normalize(vec3(
                    INV_VIEW_MATRIX[0].x,
                    0.0,
                    INV_VIEW_MATRIX[0].z));
                world_position = center +
                    (camera_right * VERTEX.x) +
                    vec3(0.0, VERTEX.y, 0.0);
            } else {
                world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
            }
            vec3 camera_position = (VIEW_MATRIX * vec4(world_position, 1.0)).xyz;
            POSITION = PROJECTION_MATRIX * vec4(camera_position, 1.0);
            view_depth = max(-camera_position.z, 0.0);
        }

        void fragment() {
            vec4 texel = texture(atlas, UV);
            if (texel.a < (8.0 / 255.0)) {
                discard;
            }
            float visibility = clamp(
                exp(-fog_density * view_depth),
                0.0,
                1.0);
            vec3 tree_color = min(texel.rgb * 2.0, vec3(1.0));
            ALBEDO = retail_output(mix(fog_color, tree_color, visibility));
        }
        """;

    private static Shader? _pineFarImposterShader;
    private static Shader? _pineFastImposterShader;

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

    public static Level100ActorDefinitionSet LoadActorDefinitions() =>
        Level100ActorDefinitionManifest.Decode(LoadManifestBytes());

    public static Level100StaticWorldAsset Load(Level100HeightFieldAsset terrain)
    {
        Manifest manifest = LoadManifest();
        ValidateManifest(manifest, terrain);
        float pineMeshDistance = checked((float)manifest.PineBillboards.MeshQualityDistance);

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
                    terrain,
                    key.StartsWith("pinesnow", StringComparison.Ordinal)
                        ? pineMeshDistance
                        : 0f),
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
            float verticalClearance = StringComparer.Ordinal.Equals(
                worldObject.Definition,
                SatTurretDefinition)
                    ? 0f
                    : checked((float)meshDefinition.BaseClearance);

            var objectRoot = new Node3D
            {
                Name = $"RetailWorldObject{worldObject.Ordinal:D2}",
                Position = new Vector3(
                    relativeX,
                    relativeHeight + verticalClearance,
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

        int pineCount = AddPines(root, manifest, terrain, meshes, textures);
        Level100WaterAsset water = AddWater(root, manifest, terrain, textures);
        int surfaceCount = objects.Sum(item => item.Mesh?.GetSurfaceCount() ?? 0);
        return new Level100StaticWorldAsset(root, objects, surfaceCount, pineCount, water);
    }

    private static int AddPines(
        Node3D root,
        Manifest manifest,
        Level100HeightFieldAsset terrain,
        IReadOnlyDictionary<string, ArrayMesh> meshes,
        IReadOnlyDictionary<string, Texture2D> textures)
    {
        PinePlacement[] placements = BuildPinePlacements(
            manifest.Pines,
            manifest.PineBillboards.FastStandingViewPhase,
            terrain);
        AddClosePineMeshes(root, manifest, meshes, placements);

        Texture2D atlas = textures[manifest.PineBillboards.Texture];
        AddFarPineImposters(root, manifest, terrain, atlas, placements);
        AddFastPineImposters(root, manifest, terrain, atlas, placements);
        return placements.Length;
    }

    private static PinePlacement[] BuildPinePlacements(
        IReadOnlyList<double[]> pines,
        int fastStandingViewPhase,
        Level100HeightFieldAsset terrain)
    {
        int[] fastViews = SelectFastPineViews(pines.Count, fastStandingViewPhase);
        var placements = new PinePlacement[pines.Count];
        for (int ordinal = 0; ordinal < pines.Count; ordinal++)
        {
            double[] pine = pines[ordinal];
            float retailX = checked((float)pine[0]);
            float retailY = checked((float)pine[1]);
            float relativeX = retailX - Level100HeightFieldAsset.PlayerStartX;
            float relativeZ = retailY - Level100HeightFieldAsset.PlayerStartZ;
            float height = Math.Max(
                terrain.SampleRelativeHeight(relativeX, relativeZ),
                terrain.WaterRelativeHeight);
            placements[ordinal] = new PinePlacement(
                checked((int)pine[2]),
                new Vector3(relativeX, height, -relativeZ),
                fastViews[ordinal]);
        }
        return placements;
    }

    private static int[] SelectFastPineViews(int count, int reconstructionPhase)
    {
        // Steam selects from the CTree address, but its exact allocation order
        // and two-bit phase are not established. Manifest v7 therefore pins an
        // authored reconstruction phase so the four views remain deterministic.
        if (reconstructionPhase is < 0 or > 3)
        {
            throw new InvalidDataException("Level 100 has an invalid fast-pine reconstruction phase.");
        }

        var views = new int[count];
        for (int ordinal = 0; ordinal < count; ordinal++)
        {
            views[ordinal] = (ordinal + reconstructionPhase) & 3;
        }
        if (!HasExpectedFastPineViewCoverage(views, reconstructionPhase))
        {
            throw new InvalidDataException("Level 100 fast-pine reconstruction coverage changed.");
        }
        return views;
    }

    private static bool HasExpectedFastPineViewCoverage(
        IReadOnlyList<int> views,
        int reconstructionPhase)
    {
        if (views.Count != 1481)
        {
            return false;
        }

        int[] counts = new int[4];
        for (int ordinal = 0; ordinal < views.Count; ordinal++)
        {
            int view = views[ordinal];
            if (view != ((ordinal + reconstructionPhase) & 3))
            {
                return false;
            }
            counts[view]++;
        }

        int[] expectedCounts = [370, 370, 370, 370];
        expectedCounts[reconstructionPhase]++;
        return counts.SequenceEqual(expectedCounts);
    }

    private static void AddClosePineMeshes(
        Node3D root,
        Manifest manifest,
        IReadOnlyDictionary<string, ArrayMesh> meshes,
        IReadOnlyList<PinePlacement> placements)
    {
        for (int variant = 0; variant < 4; variant++)
        {
            PinePlacement[] instances = placements
                .Where(item => item.Variant == variant)
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
                multiMesh.SetInstanceTransform(
                    index,
                    new Transform3D(
                        meshBasis,
                        instances[index].GroundOrigin + (Vector3.Up * baseClearance)));
            }
            root.AddChild(new MultiMeshInstance3D
            {
                Name = $"RetailPineSnow{variant}CloseMeshInstances",
                Multimesh = multiMesh,
            });
        }
    }

    private static void AddFarPineImposters(
        Node3D root,
        Manifest manifest,
        Level100HeightFieldAsset terrain,
        Texture2D atlas,
        IReadOnlyList<PinePlacement> placements)
    {
        ShaderMaterial material = CreatePineImposterMaterial(
            atlas,
            terrain,
            cameraFacing: false,
            meshQualityDistance: manifest.PineBillboards.MeshQualityDistance);
        for (int variant = 0; variant < 4; variant++)
        {
            PinePlacement[] instances = placements
                .Where(item => item.Variant == variant)
                .ToArray();
            ArrayMesh mesh = CreateFarPineImposterMesh(
                manifest.PineBillboards.Variants[variant],
                material);
            var multiMesh = new MultiMesh
            {
                TransformFormat = MultiMesh.TransformFormatEnum.Transform3D,
                Mesh = mesh,
                InstanceCount = instances.Length,
            };
            for (int index = 0; index < instances.Length; index++)
            {
                multiMesh.SetInstanceTransform(
                    index,
                    new Transform3D(Basis.Identity, instances[index].GroundOrigin));
            }
            root.AddChild(new MultiMeshInstance3D
            {
                Name = $"RetailPineSnow{variant}FarSixFaceInstances",
                Multimesh = multiMesh,
                CastShadow = GeometryInstance3D.ShadowCastingSetting.Off,
            });
        }
    }

    private static void AddFastPineImposters(
        Node3D root,
        Manifest manifest,
        Level100HeightFieldAsset terrain,
        Texture2D atlas,
        IReadOnlyList<PinePlacement> placements)
    {
        var fastRoot = new PineFastImposterRoot
        {
            Name = "RetailPineFastImposters",
        };
        fastRoot.Initialize(terrain);
        root.AddChild(fastRoot);

        ShaderMaterial standingMaterial = CreatePineImposterMaterial(
            atlas,
            terrain,
            cameraFacing: true,
            meshQualityDistance: null);
        ShaderMaterial elevatedMaterial = CreatePineImposterMaterial(
            atlas,
            terrain,
            cameraFacing: false,
            meshQualityDistance: null);
        for (int variant = 0; variant < 4; variant++)
        {
            PineBillboardVariant definition = manifest.PineBillboards.Variants[variant];
            Vector3 centerOffset = ToGodotVector(definition.CenterOffset);
            for (int viewIndex = 0; viewIndex < 4; viewIndex++)
            {
                PinePlacement[] instances = placements
                    .Where(item => item.Variant == variant && item.FastView == viewIndex)
                    .ToArray();
                double[] standingView = definition.Views[viewIndex];
                ArrayMesh standingMesh = CreateQuadMesh(
                    Vector3.Zero,
                    Vector3.Right * checked((float)standingView[4]),
                    Vector3.Up * checked((float)standingView[5]),
                    standingView,
                    standingMaterial);
                fastRoot.AddChild(CreatePineMultiMeshNode(
                    $"RetailPineSnow{variant}FastStandingView{viewIndex}Instances",
                    standingMesh,
                    instances,
                    centerOffset));

                float elevatedHalfSize = checked((float)(standingView[4] * 0.7));
                ArrayMesh elevatedMesh = CreateQuadMesh(
                    Vector3.Zero,
                    Vector3.Right * elevatedHalfSize,
                    Vector3.Forward * elevatedHalfSize,
                    definition.Views[4],
                    elevatedMaterial);
                fastRoot.AddElevated(CreatePineMultiMeshNode(
                    $"RetailPineSnow{variant}FastElevatedView{viewIndex}Instances",
                    elevatedMesh,
                    instances,
                    centerOffset));
            }
        }
    }

    private static MultiMeshInstance3D CreatePineMultiMeshNode(
        string name,
        ArrayMesh mesh,
        IReadOnlyList<PinePlacement> instances,
        Vector3 centerOffset)
    {
        var multiMesh = new MultiMesh
        {
            TransformFormat = MultiMesh.TransformFormatEnum.Transform3D,
            Mesh = mesh,
            InstanceCount = instances.Count,
        };
        for (int index = 0; index < instances.Count; index++)
        {
            multiMesh.SetInstanceTransform(
                index,
                new Transform3D(
                    Basis.Identity,
                    instances[index].GroundOrigin + centerOffset));
        }
        return new MultiMeshInstance3D
        {
            Name = name,
            Multimesh = multiMesh,
            CastShadow = GeometryInstance3D.ShadowCastingSetting.Off,
        };
    }

    private static ArrayMesh CreateFarPineImposterMesh(
        PineBillboardVariant definition,
        Material material)
    {
        Vector3[] rawRights =
        [
            Vector3.Right,
            new Vector3(0f, -1f, 0f),
            Vector3.Left,
            new Vector3(0f, 1f, 0f),
            Vector3.Right,
            Vector3.Right,
        ];
        Vector3[] rawUps =
        [
            Vector3.Back,
            Vector3.Back,
            Vector3.Back,
            Vector3.Back,
            new Vector3(0f, -1f, 0f),
            new Vector3(0f, 1f, 0f),
        ];
        Vector3 center = ToGodotVector(definition.CenterOffset);
        var vertices = new Vector3[24];
        var normals = new Vector3[24];
        var textureCoordinates = new Vector2[24];
        var indices = new int[36];
        for (int face = 0; face < 6; face++)
        {
            double[] view = definition.Views[face];
            Vector3 right = ToGodotVector(rawRights[face]) *
                checked((float)(view[4] * 0.99));
            Vector3 up = ToGodotVector(rawUps[face]) *
                checked((float)(view[5] * 0.99));
            Vector3 normal = ToGodotVector(rawUps[face].Cross(rawRights[face])).Normalized();
            AddQuad(
                vertices,
                normals,
                textureCoordinates,
                indices,
                face,
                center,
                right,
                up,
                normal,
                view);
        }
        return CreateArrayMesh(vertices, normals, textureCoordinates, indices, material);
    }

    private static ArrayMesh CreateQuadMesh(
        Vector3 center,
        Vector3 right,
        Vector3 up,
        double[] view,
        Material material)
    {
        var vertices = new Vector3[4];
        var normals = new Vector3[4];
        var textureCoordinates = new Vector2[4];
        var indices = new int[6];
        AddQuad(
            vertices,
            normals,
            textureCoordinates,
            indices,
            0,
            center,
            right,
            up,
            up.Cross(right).Normalized(),
            view);
        return CreateArrayMesh(vertices, normals, textureCoordinates, indices, material);
    }

    private static void AddQuad(
        Vector3[] vertices,
        Vector3[] normals,
        Vector2[] textureCoordinates,
        int[] indices,
        int quadIndex,
        Vector3 center,
        Vector3 right,
        Vector3 up,
        Vector3 normal,
        double[] view)
    {
        int vertex = quadIndex * 4;
        vertices[vertex] = center - right - up;
        vertices[vertex + 1] = center + right - up;
        vertices[vertex + 2] = center + right + up;
        vertices[vertex + 3] = center - right + up;
        for (int index = 0; index < 4; index++)
        {
            normals[vertex + index] = normal;
        }
        float u0 = checked((float)view[0]);
        float u1 = checked((float)view[1]);
        float v0 = checked((float)view[2]);
        float v1 = checked((float)view[3]);
        textureCoordinates[vertex] = new Vector2(u0, v0);
        textureCoordinates[vertex + 1] = new Vector2(u1, v0);
        textureCoordinates[vertex + 2] = new Vector2(u1, v1);
        textureCoordinates[vertex + 3] = new Vector2(u0, v1);
        int triangle = quadIndex * 6;
        indices[triangle] = vertex;
        indices[triangle + 1] = vertex + 1;
        indices[triangle + 2] = vertex + 2;
        indices[triangle + 3] = vertex + 2;
        indices[triangle + 4] = vertex + 3;
        indices[triangle + 5] = vertex;
    }

    private static ArrayMesh CreateArrayMesh(
        Vector3[] vertices,
        Vector3[] normals,
        Vector2[] textureCoordinates,
        int[] indices,
        Material material)
    {
        var arrays = new Godot.Collections.Array();
        arrays.Resize((int)Godot.Mesh.ArrayType.Max);
        arrays[(int)Godot.Mesh.ArrayType.Vertex] = vertices;
        arrays[(int)Godot.Mesh.ArrayType.Normal] = normals;
        arrays[(int)Godot.Mesh.ArrayType.TexUV] = textureCoordinates;
        arrays[(int)Godot.Mesh.ArrayType.Index] = indices;
        var mesh = new ArrayMesh();
        mesh.AddSurfaceFromArrays(Godot.Mesh.PrimitiveType.Triangles, arrays);
        mesh.SurfaceSetMaterial(0, material);
        return mesh;
    }

    private static ShaderMaterial CreatePineImposterMaterial(
        Texture2D atlas,
        Level100HeightFieldAsset terrain,
        bool cameraFacing,
        double? meshQualityDistance)
    {
        bool far = meshQualityDistance.HasValue;
        var material = new ShaderMaterial
        {
            Shader = far
                ? _pineFarImposterShader ??= new Shader { Code = PineFarImposterShaderCode }
                : _pineFastImposterShader ??= new Shader { Code = PineFastImposterShaderCode },
            RenderPriority = far ? 0 : 1,
        };
        material.SetShaderParameter("atlas", atlas);
        material.SetShaderParameter("fog_color", new Vector3(
            terrain.FogColor.R,
            terrain.FogColor.G,
            terrain.FogColor.B));
        material.SetShaderParameter("fog_density", terrain.FogDensity);
        if (far)
        {
            float distance = checked((float)meshQualityDistance!.Value);
            material.SetShaderParameter("mesh_distance_squared", distance * distance);
        }
        else
        {
            material.SetShaderParameter("camera_facing", cameraFacing ? 1f : 0f);
        }
        return material;
    }

    private static Vector3 ToGodotVector(double[] beaVector) => new(
        checked((float)beaVector[0]),
        -checked((float)beaVector[2]),
        -checked((float)beaVector[1]));

    private static Vector3 ToGodotVector(Vector3 beaVector) => new(
        beaVector.X,
        -beaVector.Z,
        -beaVector.Y);

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
        Level100HeightFieldAsset terrain,
        float maximumHorizontalDistance)
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
        return RetailFixedFunctionMaterial.Create(
            layers,
            terrain,
            maximumHorizontalDistance,
            maximumHorizontalDistance > 0f ? 8f / 255f : 0.5f);
    }

    private static Manifest LoadManifest()
    {
        byte[] source = LoadManifestBytes();
        return JsonSerializer.Deserialize<Manifest>(source, new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true,
        }) ?? throw new InvalidDataException("The Level 100 static-world manifest is empty.");
    }

    private static byte[] LoadManifestBytes()
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
        return source;
    }

    private static void ValidateManifest(Manifest manifest, Level100HeightFieldAsset terrain)
    {
        if (!StringComparer.Ordinal.Equals(manifest.Schema, "onslaught.level100-static-world.v11") ||
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
            manifest.Textures.Count != 34 ||
            Enumerable.Range(0, 4).Any(variant =>
                !manifest.Meshes.ContainsKey($"pinesnow{variant}")) ||
            !IsValidPineBillboards(manifest.PineBillboards, manifest.Textures) ||
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
            throw new InvalidDataException(
                "Level 100 static-world identity, counts, or reconstruction profile changed.");
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
        WorldObject[] satTurrets = manifest.Objects
            .Where(item => StringComparer.Ordinal.Equals(item.Definition, SatTurretDefinition))
            .ToArray();
        if (satTurrets.Length != 1 ||
            !StringComparer.Ordinal.Equals(satTurrets[0].Mesh, SatTurretMesh) ||
            manifest.Objects.Any(item =>
                StringComparer.Ordinal.Equals(item.Mesh, SatTurretMesh) &&
                !StringComparer.Ordinal.Equals(item.Definition, SatTurretDefinition)))
        {
            throw new InvalidDataException("Level 100 SAT Turret identity does not match retail.");
        }
        foreach (WorldObject worldObject in manifest.Objects)
        {
            if (string.IsNullOrWhiteSpace(worldObject.Definition) ||
                worldObject.RetailPosition.Length != 3 ||
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

    private static bool IsValidPineBillboards(
        PineBillboardDefinition definition,
        IReadOnlyDictionary<string, TextureDefinition> textures)
    {
        if (!textures.TryGetValue(definition.Texture, out TextureDefinition? texture) ||
            texture is null ||
            texture.Width != 1024 ||
            texture.Height != 256 ||
            !StringComparer.Ordinal.Equals(texture.Compression, "Dxt2") ||
            BitConverter.SingleToInt32Bits(checked((float)definition.MeshQualityDistance)) !=
                BitConverter.SingleToInt32Bits(70f) ||
            definition.FastStandingViewPhase != 0 ||
            definition.Variants.Length != 4)
        {
            return false;
        }

        int[][] expectedCenters =
        [
            [unchecked((int)0xBCCC7F20), 0x39BA4000, unchecked((int)0xBF6303AA)],
            [0x3D8FAD60, unchecked((int)0xBDA96080), unchecked((int)0xBF696408)],
            [0x3C9B2D60, unchecked((int)0xBDF5D470), unchecked((int)0xBF6A0AB4)],
            [0x3D429CA0, 0x3CD68540, unchecked((int)0xBF506532)],
        ];
        for (int variant = 0; variant < definition.Variants.Length; variant++)
        {
            PineBillboardVariant item = definition.Variants[variant];
            if (item.CenterOffset.Length != 3 || item.Views.Length != 6 ||
                !item.CenterOffset.All(double.IsFinite) ||
                item.Views.Any(view =>
                    view.Length != 6 ||
                    !view.All(double.IsFinite) ||
                    view[0] < 0.0 || view[0] >= view[1] || view[1] > 1.0 ||
                    view[2] < 0.0 || view[2] >= view[3] || view[3] > 1.0 ||
                    view[4] <= 0.0 || view[5] <= 0.0))
            {
                return false;
            }
            int[] centerBits = item.CenterOffset
                .Select(value => BitConverter.SingleToInt32Bits(checked((float)value)))
                .ToArray();
            if (!centerBits.SequenceEqual(expectedCenters[variant]))
            {
                return false;
            }
        }
        return true;
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
        public PineBillboardDefinition PineBillboards { get; init; } = new();
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

    private sealed record PineBillboardDefinition
    {
        public int FastStandingViewPhase { get; init; }
        public double MeshQualityDistance { get; init; }
        public string Texture { get; init; } = string.Empty;
        public PineBillboardVariant[] Variants { get; init; } = [];
    }

    private sealed record PineBillboardVariant
    {
        public double[] CenterOffset { get; init; } = [];
        public double[][] Views { get; init; } = [];
    }

    private readonly record struct PinePlacement(
        int Variant,
        Vector3 GroundOrigin,
        int FastView);

    private sealed partial class PineFastImposterRoot : Node3D
    {
        private readonly Node3D _elevated = new()
        {
            Name = "HeightGatedElevatedCards",
            Visible = false,
        };
        private Level100HeightFieldAsset? _terrain;

        public void Initialize(Level100HeightFieldAsset terrain)
        {
            _terrain = terrain;
            AddChild(_elevated);
        }

        public void AddElevated(MultiMeshInstance3D node) => _elevated.AddChild(node);

        public override void _Process(double delta)
        {
            Camera3D? camera = GetViewport().GetCamera3D();
            if (camera is null || _terrain is null)
            {
                _elevated.Visible = false;
                return;
            }
            Vector3 cameraPosition = camera.GlobalPosition;
            float sampledGroundHeight = _terrain.SampleRelativeHeight(
                cameraPosition.X,
                -cameraPosition.Z);
            _elevated.Visible = MathF.Abs(cameraPosition.Y - sampledGroundHeight) > 20f;
        }
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
        public string Definition { get; init; } = string.Empty;
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

        uniform sampler2D base_texture : filter_linear_mipmap_anisotropic, repeat_enable;
        uniform sampler2D dot3_texture : filter_linear_mipmap, repeat_enable;
        uniform sampler2D reflection_texture : filter_linear_mipmap_anisotropic, repeat_enable;
        uniform sampler2D overlay_texture : filter_linear_mipmap, repeat_enable;
        uniform float has_dot3;
        uniform float has_reflection;
        uniform float has_overlay;
        uniform float base_blend_texture_alpha;
        uniform float alpha_reference;
        uniform vec2 dot3_offset;
        uniform vec2 dot3_scale;
        uniform float reflection_factor_alpha;
        uniform vec2 overlay_offset;
        uniform vec2 overlay_scale;
        uniform float overlay_opacity;
        uniform vec3 ambient_color;
        uniform vec3 sun_color;
        uniform vec3 anti_sun_color;
        uniform vec3 sunlight_direction;
        uniform vec3 fog_color;
        uniform float fog_density;
        uniform float maximum_horizontal_distance_squared;
        varying vec3 vertex_light_color;
        varying vec3 model_light_direction;
        varying vec2 reflection_uv;
        varying float horizontal_distance_squared;

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
            // MultiMesh instance position is available through MODEL_MATRIX
            // here, so carry its camera distance into the fragment stage.
            vec2 horizontal_offset =
                MODEL_MATRIX[3].xz - CAMERA_POSITION_WORLD.xz;
            horizontal_distance_squared = dot(
                horizontal_offset,
                horizontal_offset);
            vec3 world_normal = normalize(mat3(MODEL_MATRIX) * NORMAL);
            float sun = max(dot(world_normal, -sunlight_direction), 0.0);
            float anti_sun = max(dot(world_normal, sunlight_direction), 0.0);
            vertex_light_color = ambient_color + (sun_color * sun) +
                (anti_sun_color * anti_sun);
            model_light_direction = normalize(
                transpose(mat3(MODEL_MATRIX)) * sunlight_direction);

            // D3DTSS_TCI_CAMERASPACEREFLECTIONVECTOR generates
            // 2(N.E)N-E per vertex. Steam then applies [.5,0;0,-.5]
            // and the (.5,.5) offset before interpolating the coordinates.
            vec3 view_position = (MODELVIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
            vec3 view_normal = normalize(MODELVIEW_NORMAL_MATRIX * NORMAL);
            vec3 eye = normalize(-view_position);
            vec3 reflection_vector =
                (2.0 * dot(view_normal, eye) * view_normal) - eye;
            reflection_uv = vec2(
                (reflection_vector.x * 0.5) + 0.5,
                (reflection_vector.y * -0.5) + 0.5);
        }

        void fragment() {
            if (maximum_horizontal_distance_squared >= 0.0 &&
                horizontal_distance_squared > maximum_horizontal_distance_squared) {
                discard;
            }
            // Steam's high static-world renderer applies a -1 mip bias to
            // hardware stage zero.
            vec4 texture_color = texture(base_texture, UV, -1.0);
            if (base_blend_texture_alpha < 0.5 && texture_color.a < alpha_reference) {
                discard;
            }
            vec3 retail_color = min(
                texture_color.rgb * vertex_light_color * 2.0,
                vec3(1.0));
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
                // Mode 2 is another stage-zero world draw. It inherits the
                // lit MODULATE2X color operation and stage-zero sampler state;
                // stage one only scales its alpha with texture factor.
                vec4 reflection_color = texture(
                    reflection_texture,
                    reflection_uv,
                    -1.0);
                vec3 reflection_stage_color = min(
                    reflection_color.rgb * vertex_light_color * 2.0,
                    vec3(1.0));
                float reflection_alpha = clamp(
                    reflection_color.a * reflection_factor_alpha,
                    0.0,
                    1.0);
                retail_color = mix(
                    retail_color,
                    reflection_stage_color,
                    reflection_alpha);
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
        Level100HeightFieldAsset terrain,
        float maximumHorizontalDistance = 0f,
        float alphaReference = 0.5f)
    {
        if (layers.Count != 6 || layers[0] is not RetailTextureLayer baseLayer)
        {
            throw new InvalidDataException("Retail material requires one base layer and six exact slots.");
        }
        if (!float.IsFinite(maximumHorizontalDistance) || maximumHorizontalDistance < 0f)
        {
            throw new ArgumentOutOfRangeException(nameof(maximumHorizontalDistance));
        }
        if (!float.IsFinite(alphaReference) || alphaReference is < 0f or > 1f)
        {
            throw new ArgumentOutOfRangeException(nameof(alphaReference));
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
        material.SetShaderParameter("alpha_reference", alphaReference);
        material.SetShaderParameter("dot3_offset", dot3Layer?.Offset ?? Vector2.Zero);
        material.SetShaderParameter("dot3_scale", dot3Layer?.Scale ?? Vector2.One);
        material.SetShaderParameter(
            "reflection_factor_alpha",
            ToTextureFactorAlpha(reflectionLayer?.Opacity ?? 0f));
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
        material.SetShaderParameter(
            "maximum_horizontal_distance_squared",
            maximumHorizontalDistance > 0f
                ? maximumHorizontalDistance * maximumHorizontalDistance
                : -1f);
        return material;
    }

    private static Vector3 ToVector(uint rgb, float divisor) => new(
        ((rgb >> 16) & 0xFF) / divisor,
        ((rgb >> 8) & 0xFF) / divisor,
        (rgb & 0xFF) / divisor);

    private static float ToTextureFactorAlpha(float strength)
    {
        int alpha = Math.Clamp(
            (int)MathF.Round(strength * byte.MaxValue, MidpointRounding.ToEven),
            byte.MinValue,
            byte.MaxValue);
        return alpha / (float)byte.MaxValue;
    }
}
