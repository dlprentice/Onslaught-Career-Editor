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

    private static Shader? _pineFarImposterShader;

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
            float retailX = checked((float)worldObject.RetailPosition[0]);
            float retailY = checked((float)worldObject.RetailPosition[1]);
            float retailZ = checked((float)worldObject.RetailPosition[2]);
            float relativeX = retailX - Level100HeightFieldAsset.PlayerStartX;
            float relativeZ = retailY - Level100HeightFieldAsset.PlayerStartZ;
            // `CThing__Init` @ 0x004F34A0 is the whole vertical placement the
            // released game applies to an authored static. It copies the
            // authored position into `this+0x1c..+0x28` (Z-down at `+0x24`),
            // then runs two clamps and nothing else:
            //
            //   0x004F34F6  b9 c8 ad 6f 00  MOV ECX, 0x006FADC8   height field
            //   0x004F34FB  e8 80 b6 f8 ff  CALL 0x0047EB80       bilinear sample
            //   0x004F3500  d8 56 24        FCOM  [ESI + 0x24]    sample vs authored
            //   0x004F3529  d9 5c 24 14     FSTP  [ESP + 0x14]    sample becomes Z
            //   0x004F3534  ff 50 50        CALL  [EAX + 0x50]    SetPosition
            //   0x004F3549  d9 05 fc bd 6f 00 FLD [0x006FBDFC]    water level
            //   0x004F354F  d8 56 24        FCOM  [ESI + 0x24]
            //   0x004F3559  d9 5e 24        FSTP  [ESI + 0x24]    water becomes Z
            //
            // Both `FSTP`s write the support height straight into the pivot.
            // Z is down-positive, so the pair is `min(authored, support)` there
            // and the `Math.Max` below in up-positive units. No mesh extent is
            // read anywhere on that path: retail seats the *pivot*, never the
            // bounding box. A `-min(vertexZ)` clearance term therefore has no
            // retail counterpart and is not applied. It measured +3.2318 on
            // `FB_Docks` — exactly that mesh's own 173-vertex piling span below
            // its origin, which is why the docks hung in the air with their
            // legs ending above the water — and +0.2226/+0.2257/+0.2282 on the
            // three turret meshes, each exactly the buried base collar those
            // meshes carry below z = 0.
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
                    relativeHeight,
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
        // A retail Level 1.00 pine has exactly two representations: the
        // pinesnow mesh at or inside the authored 70.0 mesh-quality distance,
        // and the six-face box imposter outside it. `defaultoptions.bea`
        // offset 0x26CA is `00 00 8C 42` = 70.0f, and the archive's
        // IMPS/IMPT/VIEW chunk carries exactly six views per variant whose
        // (width, height) pairs are that variant's own mesh bounding-box
        // half-extents inflated by 1.05 on all three axes. The two shader
        // gates below are complementary about the same 70.0 value, so every
        // pine is covered at every distance and neither pass is ungated.
        PinePlacement[] placements = BuildPinePlacements(manifest.Pines, terrain);
        AddClosePineMeshes(root, manifest, meshes, placements);

        Texture2D atlas = textures[manifest.PineBillboards.Texture];
        AddFarPineImposters(root, manifest, terrain, atlas, placements);
        return placements.Length;
    }

    private static PinePlacement[] BuildPinePlacements(
        IReadOnlyList<double[]> pines,
        Level100HeightFieldAsset terrain)
    {
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
                new Vector3(relativeX, height, -relativeZ));
        }
        return placements;
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
            meshQualityDistance: manifest.PineBillboards.MeshQualityDistance);
        for (int variant = 0; variant < 4; variant++)
        {
            PinePlacement[] instances = placements
                .Where(item => item.Variant == variant)
                .ToArray();
            ArrayMesh mesh = CreateFarPineImposterMesh(
                manifest.PineBillboards.Variants[variant],
                material);
            // The stored VIEW half-extents are this variant's own mesh
            // bounding box scaled by 1.05, and `centerOffset` is that mesh
            // bounding box centre. The box therefore only describes the tree
            // when it sits on the same transform the mesh does, which
            // AddClosePineMeshes places at GroundOrigin + Up * baseClearance.
            // Omitting the clearance here put the box bottom 0.0804 below
            // ground for pinesnow0 and stepped the tree vertically at the
            // 70.0 swap.
            float baseClearance = checked(
                (float)manifest.Meshes[$"pinesnow{variant}"].BaseClearance);
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
                    new Transform3D(
                        Basis.Identity,
                        instances[index].GroundOrigin + (Vector3.Up * baseClearance)));
            }
            root.AddChild(new MultiMeshInstance3D
            {
                Name = $"RetailPineSnow{variant}FarSixFaceInstances",
                Multimesh = multiMesh,
                CastShadow = GeometryInstance3D.ShadowCastingSetting.Off,
            });
        }
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
        double meshQualityDistance)
    {
        // Every imposter material is distance-gated. There is no ungated
        // overload: the box may only appear where the mesh has been discarded.
        float distance = checked((float)meshQualityDistance);
        if (!float.IsFinite(distance) || distance <= 0f)
        {
            throw new InvalidDataException(
                "Level 100 pine imposters require a positive mesh-quality distance.");
        }
        var material = new ShaderMaterial
        {
            Shader = _pineFarImposterShader ??= new Shader { Code = PineFarImposterShaderCode },
            RenderPriority = 0,
        };
        material.SetShaderParameter("atlas", atlas);
        material.SetShaderParameter("fog_color", new Vector3(
            terrain.FogColor.R,
            terrain.FogColor.G,
            terrain.FogColor.B));
        material.SetShaderParameter("fog_density", terrain.FogDensity);
        material.SetShaderParameter("mesh_distance_squared", distance * distance);
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
        // MODULATE2X, stated rather than inherited. Stage-zero
        // D3DTSS_COLOROP was read at the entry to every mesh render of one
        // whole Level 100 frame and is 5 = D3DTOP_MODULATE2X on all 134 mode-0
        // static-world draws and all 442 CRTTree mesh draws.
        //
        // OPEN, and deliberately not applied here: 19 further draws inside
        // CRTMesh::BuildRenderOutputs in that same frame run at mode 4 with
        // stage-zero COLOROP 4 = D3DTOP_MODULATE. They are a separate pass
        // issued after the cockpit, from four CRTMesh objects whose count
        // varies frame to frame (two in one observed frame, four in three
        // others), so they are not the 28 authored static-world meshes this
        // manifest builds and nothing here has been mapped to them. Giving any
        // mesh built from this manifest MODULATE would therefore be a guess,
        // not a measurement.
        return RetailFixedFunctionMaterial.Create(
            layers,
            terrain,
            maximumHorizontalDistance,
            maximumHorizontalDistance > 0f ? 8f / 255f : 0.5f,
            RetailStageZeroColorOperation.Modulate2X);
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
        if (!StringComparer.Ordinal.Equals(manifest.Schema, "onslaught.level100-static-world.v13") ||
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
            // Manifest identity only. Retail's fast tree batch has no
            // established enable condition and is not drawn here, so nothing
            // consumes this phase; it stays pinned so a manifest change is
            // still caught.
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
        Vector3 GroundOrigin);

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

/// <summary>
/// The stage-zero <c>D3DTSS_COLOROP</c> a draw through
/// <see cref="RetailFixedFunctionMaterial"/> runs under. The members carry the
/// Direct3D <c>D3DTOP</c> enumerant values so the source reads the same way the
/// runtime dump does.
/// </summary>
/// <remarks>
/// This is a per-draw property in the released game, not a constant. Every
/// stage-zero <c>D3DTSS_COLOROP</c> value below was read out of the running
/// safe copy's texture-stage-state shadow at <c>0x008557f4</c> — the caching
/// setter at <c>0x00513820</c> computes its index as
/// <c>(type + stage*0n30)*4 + 0x008557f0</c> at <c>0x0051382a</c>–<c>0x00513833</c>,
/// and the invalidator at <c>0x00513600</c> clears 0n240 = 8 stages x 0n30
/// dwords there — sampled at the entry to <c>CMeshRenderer::RenderMeshCore</c>
/// (<c>0x00549570</c>, the image's only mesh-render call site) for one whole
/// Level 100 frame:
/// <list type="bullet">
/// <item><description>134 mode-0 static-world draws: <c>5</c>
/// = <c>D3DTOP_MODULATE2X</c>.</description></item>
/// <item><description>442 <c>CRTTree</c> close-mesh draws: <c>5</c>
/// = <c>D3DTOP_MODULATE2X</c>.</description></item>
/// <item><description>All seven cockpit batches: <c>4</c>
/// = <c>D3DTOP_MODULATE</c>, read 16 times inside the cockpit window with zero
/// stage-zero <c>COLOROP</c> transitions while inside it.</description></item>
/// <item><description>19 mode-4 static-world draws in that same frame: <c>4</c>
/// = <c>D3DTOP_MODULATE</c>.</description></item>
/// </list>
/// <c>COLORARG1</c> is <c>2</c> = <c>D3DTA_TEXTURE</c>, <c>COLORARG2</c> is
/// <c>0</c> = <c>D3DTA_DIFFUSE</c> and stage-one <c>COLOROP</c> is <c>1</c> =
/// <c>D3DTOP_DISABLE</c> at every one of those draws.
/// </remarks>
internal enum RetailStageZeroColorOperation
{
    /// <summary>D3DTOP_MODULATE. Texture x diffuse, no doubling.</summary>
    Modulate = 4,

    /// <summary>D3DTOP_MODULATE2X. Texture x diffuse x 2.</summary>
    Modulate2X = 5,
}

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
        // Stage-zero D3DTSS_COLOROP as a multiplier: 1.0 for D3DTOP_MODULATE
        // (4), 2.0 for D3DTOP_MODULATE2X (5). Per draw, never a constant --
        // see RetailStageZeroColorOperation for the runtime reads that fix it.
        uniform float stage_zero_gain;
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
            // Retail leaves D3DRS_LIGHTING on for the FVF 0x152 mesh draw and
            // sets D3DRS_DIFFUSEMATERIALSOURCE and D3DRS_AMBIENTMATERIALSOURCE
            // to D3DMCS_COLOR1 (D3DStateCache__UseDefaultRenderState,
            // 0x004EB1E0), leaving D3DRS_COLORVERTEX at its TRUE default. The
            // per-vertex DIFFUSE dword is therefore the diffuse and ambient
            // material reflectance for every term of the lighting equation, and
            // the lit result is stage-zero COLORARG2 = D3DTA_DIFFUSE.
            vertex_light_color *= COLOR.rgb;
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
            // Stage zero is COLORARG1 = D3DTA_TEXTURE, COLORARG2 =
            // D3DTA_DIFFUSE, and COLOROP is whichever of MODULATE /
            // MODULATE2X the draw is under. Read out of the running safe copy
            // from the texture-stage-state shadow at 0x008557f4 (the setter at
            // 0x00513820 indexes it as (type + stage*0n30)*4 + 0x008557f0):
            // 5 = MODULATE2X on the 134 mode-0 static-world draws and the 442
            // CRTTree mesh draws of one frame, 4 = MODULATE on all seven
            // cockpit batches (16 reads inside the cockpit window, zero
            // transitions while inside it) and on the 19 mode-4 static-world
            // draws of that same frame. So the gain is per draw.
            vec3 retail_color = min(
                texture_color.rgb * vertex_light_color * stage_zero_gain,
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
                // The reflection layer is another stage-zero world draw, and
                // it is a MODE-0 one: [0x00704e48], the RenderMeshCore mode
                // global, was read at every one of 4,393 mesh renders across
                // three launches and is 0 on 4,314 and 4 on 79 -- never 2,
                // never 6, never 8, and the mode-2/mode-6 draw calls at
                // 0x0054a423 / 0x0054a466 never fired at all. D3DRS_LIGHTING
                // ([0x00855764], the render-state shadow at 0x00855540 indexed
                // state*4) is 1 across all 576 world and tree draws, so the
                // layer is lit, which is what this branch already assumed. It
                // inherits stage zero's colour operation and sampler state;
                // stage one only scales its alpha with texture factor.
                vec4 reflection_color = texture(
                    reflection_texture,
                    reflection_uv,
                    -1.0);
                vec3 reflection_stage_color = min(
                    reflection_color.rgb * vertex_light_color * stage_zero_gain,
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

    public static ShaderMaterial Create(
        Texture2D texture,
        Level100HeightFieldAsset terrain,
        RetailStageZeroColorOperation stageZeroColorOperation)
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
            terrain,
            stageZeroColorOperation: stageZeroColorOperation);
    }

    /// <param name="stageZeroColorOperation">
    /// The stage-zero <c>D3DTSS_COLOROP</c> this draw runs under. Retail's
    /// value varies by draw, so every call site states the one it measured;
    /// the default is the <c>MODULATE2X</c> read at the 134 mode-0
    /// static-world and 442 tree draws, which are the majority of the draws
    /// through this shader. See <see cref="RetailStageZeroColorOperation"/>.
    /// </param>
    public static ShaderMaterial Create(
        IReadOnlyList<RetailTextureLayer?> layers,
        Level100HeightFieldAsset terrain,
        float maximumHorizontalDistance = 0f,
        float alphaReference = 0.5f,
        RetailStageZeroColorOperation stageZeroColorOperation =
            RetailStageZeroColorOperation.Modulate2X)
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
        float stageZeroGain = StageZeroGain(stageZeroColorOperation);
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
        material.SetShaderParameter("stage_zero_gain", stageZeroGain);
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

    /// <summary>
    /// The stage-zero colour operation as the multiplier the shader applies.
    /// <c>D3DTOP_MODULATE</c> is texture x diffuse and <c>D3DTOP_MODULATE2X</c>
    /// is that doubled, so these are exactly 1 and 2. Any other enumerant is
    /// refused rather than silently collapsed onto one of them: nothing has
    /// observed retail using one at these draws.
    /// </summary>
    private static float StageZeroGain(RetailStageZeroColorOperation operation) =>
        operation switch
        {
            RetailStageZeroColorOperation.Modulate => 1f,
            RetailStageZeroColorOperation.Modulate2X => 2f,
            _ => throw new ArgumentOutOfRangeException(nameof(operation)),
        };

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
