// SPDX-License-Identifier: GPL-3.0-or-later

using System.Buffers.Binary;
using System.Security.Cryptography;
using Godot;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Adapts the released Level 100 fixed-function water path. The moving grid is
/// camera-relative presentation; the serialized SURF contours remain fixed in
/// retail world space.
/// </summary>
internal sealed class Level100WaterAsset
{
    private const int GridCellsPerAxis = 24;
    private const int GridVerticesPerAxis = GridCellsPerAxis + 1;
    private const float GridStart = -768f;
    private const float GridStep = 64f;
    private const float RadialScale = 0.0013586956774815917f;
    private const int SurfaceRecordCount = 515;
    private const int SurfaceSegmentCount = 514;
    private const int SurfaceSourceLength = 18_572;
    private const float ShorelineDepthBias = 0.002f;

    private static Shader? _gridShader;
    private static Shader? _shorelinePrimaryShader;
    private static Shader? _shorelineOverlayShader;
    private static Shader? _sunReflectionShader;

    private readonly MeshInstance3D _grid;
    private readonly MeshInstance3D _sunReflection;
    private readonly float _waterHeight;
    private readonly Vector3 _sunlightDirection;

    private const string GridShaderCode = """
        shader_type spatial;
        render_mode unshaded, blend_mix, depth_draw_opaque, cull_disabled;

        uniform sampler2D caustic_texture : filter_linear_mipmap, repeat_enable;
        uniform sampler2D reflection_texture : filter_linear_mipmap, repeat_enable;
        uniform vec3 water_color;
        uniform vec2 retail_origin;
        uniform vec3 fog_color;
        uniform float fog_density;
        varying vec3 water_world_position;

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
            water_world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
        }

        void fragment() {
            // Steam advances these fixed-function texture transforms with the
            // frame delta in milliseconds: 0.003 and 0.05 per millisecond.
            float reflection_phase = mod(TIME * 3.0, 1.0);
            float caustic_phase = mod(TIME * 50.0, 6.28318530718);
            vec2 retail_xy = vec2(
                water_world_position.x + retail_origin.x,
                retail_origin.y - water_world_position.z);

            vec2 caustic_a = vec2(
                (retail_xy.x * 0.1) + (retail_xy.y * 0.03),
                (retail_xy.x * 0.03) - (retail_xy.y * 0.1));
            caustic_a += vec2(sin(caustic_phase), cos(caustic_phase)) * 0.1;

            float second_phase = caustic_phase + 3.14159265359;
            vec2 caustic_b = vec2(
                (retail_xy.x * 0.03) + (retail_xy.y * 0.1),
                (retail_xy.x * 0.1) - (retail_xy.y * 0.03));
            caustic_b += vec2(sin(second_phase), cos(second_phase)) * 0.1;

            vec2 reflection_uv = (retail_xy * 0.5) + vec2(0.0, reflection_phase);
            vec3 caustic_0 = texture(caustic_texture, caustic_a).rgb;
            vec3 caustic_1 = texture(caustic_texture, caustic_b).rgb;
            vec3 reflected = texture(reflection_texture, reflection_uv).rgb;

            // Released D3D8 stages: water diffuse × caustic × caustic,
            // followed by the reflection texture's additive stage.
            vec3 retail_color = min((water_color * caustic_0 * caustic_1) + reflected, vec3(1.0));
            retail_color = apply_retail_fog(retail_color, max(-VERTEX.z, 0.0));
            ALBEDO = retail_output(retail_color);
            ALPHA = COLOR.a;
        }
        """;

    private const string ShorelinePrimaryShaderCode = """
        shader_type spatial;
        render_mode unshaded, blend_mix, depth_draw_never, cull_disabled;

        uniform sampler2D waves_texture : filter_linear_mipmap, repeat_enable;
        uniform vec3 fog_color;
        uniform float fog_density;

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

        void fragment() {
            vec4 wave = texture(waves_texture, UV + vec2(0.0, mod(TIME * 3.0, 1.0)));

            // The released first SURF pass uses D3DTOP_MODULATEALPHA_ADDCOLOR
            // with the wave texture as Arg1 and vertex diffuse as Arg2.
            vec3 retail_color = min(wave.rgb + (wave.a * COLOR.rgb), vec3(1.0));
            retail_color = apply_retail_fog(retail_color, max(-VERTEX.z, 0.0));
            ALBEDO = retail_output(retail_color);
            ALPHA = COLOR.a;
        }
        """;

    private const string ShorelineOverlayShaderCode = """
        shader_type spatial;
        render_mode unshaded, blend_mix, depth_draw_never, cull_disabled;

        uniform sampler2D waves_texture : filter_linear_mipmap, repeat_enable;
        uniform vec3 fog_color;
        uniform float fog_density;

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

        void fragment() {
            vec4 wave = texture(waves_texture, UV + vec2(0.0, mod(TIME * 3.0, 1.0)));
            vec3 retail_color = apply_retail_fog(
                wave.rgb * COLOR.rgb,
                max(-VERTEX.z, 0.0));
            ALBEDO = retail_output(retail_color);
            ALPHA = wave.a * COLOR.a;
        }
        """;

    private const string SunReflectionShaderCode = """
        shader_type spatial;
        render_mode unshaded, blend_mix, depth_draw_never, cull_disabled;

        uniform sampler2D sun_reflection_texture : filter_linear_mipmap, repeat_enable;
        uniform sampler2D sun_blob_texture : filter_linear_mipmap, repeat_disable;
        uniform vec3 sun_reflection_color;
        uniform vec3 fog_color;
        uniform float fog_density;

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

        void fragment() {
            float reflection_phase = mod(TIME * 3.0, 1.0);
            float caustic_phase = mod(TIME * 50.0, 6.28318530718);
            vec2 reflection_a_uv = vec2(
                (UV.x * 0.1) + (UV.y * 0.03),
                (UV.x * 0.03) - (UV.y * 0.1));
            reflection_a_uv += vec2(sin(caustic_phase), cos(caustic_phase)) * 0.1;

            float second_phase = caustic_phase + 3.14159265359;
            vec2 reflection_b_uv = vec2(
                (UV.x * 0.03) + (UV.y * 0.1),
                (UV.x * 0.1) - (UV.y * 0.03));
            reflection_b_uv += vec2(sin(second_phase), cos(second_phase)) * 0.1;

            vec4 reflection_a = texture(sun_reflection_texture, reflection_a_uv);
            vec4 reflection_b = texture(sun_reflection_texture, reflection_b_uv);
            vec4 blob = texture(
                sun_blob_texture,
                (UV * 0.5) + vec2(0.0, reflection_phase));

            // The released sun pass modulates the two sun-reflection stages,
            // adds sunblob, and rejects fragments below alpha reference 0xc0.
            float retail_alpha = reflection_a.a + reflection_b.a + blob.a;
            if (retail_alpha <= (192.0 / 255.0)) {
                discard;
            }
            vec3 retail_color = min(
                (sun_reflection_color * reflection_a.rgb * reflection_b.rgb) + blob.rgb,
                vec3(1.0));
            retail_color = apply_retail_fog(retail_color, max(-VERTEX.z, 0.0));
            ALBEDO = retail_output(retail_color);
            ALPHA = 1.0;
        }
        """;

    private Level100WaterAsset(
        Node3D root,
        MeshInstance3D grid,
        MeshInstance3D sunReflection,
        float waterHeight,
        Vector3 sunlightDirection,
        int shorelineTriangleCount)
    {
        Root = root;
        _grid = grid;
        _sunReflection = sunReflection;
        _waterHeight = waterHeight;
        _sunlightDirection = sunlightDirection;
        ShorelineTriangleCount = shorelineTriangleCount;
    }

    public Node3D Root { get; }

    public int GridVertexCount => GridVerticesPerAxis * GridVerticesPerAxis;

    public int GridTriangleCount => GridCellsPerAxis * GridCellsPerAxis * 2;

    public int ShorelineTriangleCount { get; }

    public static Level100WaterAsset Create(
        Level100HeightFieldAsset terrain,
        Texture2D reflection,
        Texture2D caustic,
        Texture2D waves,
        Texture2D sunBlob,
        Texture2D sunReflection,
        string surfaceResourcePath,
        string surfaceSha256)
    {
        var root = new Node3D { Name = "RetailLevel100Water" };
        var gridMaterial = new ShaderMaterial
        {
            Shader = _gridShader ??= new Shader { Code = GridShaderCode },
        };
        gridMaterial.SetShaderParameter("reflection_texture", reflection);
        gridMaterial.SetShaderParameter("caustic_texture", caustic);
        gridMaterial.SetShaderParameter("water_color", new Vector3(
            0x21 / 255f,
            0x21 / 255f,
            0x3D / 255f));
        gridMaterial.SetShaderParameter("retail_origin", new Vector2(
            Level100HeightFieldAsset.PlayerStartX,
            Level100HeightFieldAsset.PlayerStartZ));
        SetFogParameters(gridMaterial, terrain);

        var grid = new MeshInstance3D
        {
            Name = "RetailCameraRelativeWaterGrid",
            Mesh = BuildGridMesh(),
            MaterialOverride = gridMaterial,
            CastShadow = GeometryInstance3D.ShadowCastingSetting.Off,
        };
        root.AddChild(grid);

        var shorelineOverlayMaterial = new ShaderMaterial
        {
            Shader = _shorelineOverlayShader ??= new Shader { Code = ShorelineOverlayShaderCode },
        };
        shorelineOverlayMaterial.SetShaderParameter("waves_texture", waves);
        SetFogParameters(shorelineOverlayMaterial, terrain);
        var shorelineMaterial = new ShaderMaterial
        {
            Shader = _shorelinePrimaryShader ??= new Shader { Code = ShorelinePrimaryShaderCode },
            NextPass = shorelineOverlayMaterial,
        };
        shorelineMaterial.SetShaderParameter("waves_texture", waves);
        SetFogParameters(shorelineMaterial, terrain);
        var shoreline = new MeshInstance3D
        {
            Name = "RetailAuthoredShorelineBands",
            Mesh = BuildShorelineMesh(
                surfaceResourcePath,
                surfaceSha256,
                shorelineMaterial),
            Position = Vector3.Up * ShorelineDepthBias,
            CastShadow = GeometryInstance3D.ShadowCastingSetting.Off,
        };
        root.AddChild(shoreline);

        var sunMaterial = new ShaderMaterial
        {
            Shader = _sunReflectionShader ??= new Shader { Code = SunReflectionShaderCode },
        };
        sunMaterial.SetShaderParameter("sun_reflection_texture", sunReflection);
        sunMaterial.SetShaderParameter("sun_blob_texture", sunBlob);
        sunMaterial.SetShaderParameter("sun_reflection_color", new Vector3(
            0xE8 / 255f,
            0xE8 / 255f,
            0xFF / 255f));
        SetFogParameters(sunMaterial, terrain);
        var sun = new MeshInstance3D
        {
            Name = "RetailWaterSunReflection",
            Mesh = BuildSunReflectionMesh(),
            MaterialOverride = sunMaterial,
            CastShadow = GeometryInstance3D.ShadowCastingSetting.Off,
        };
        root.AddChild(sun);

        return new Level100WaterAsset(
            root,
            grid,
            sun,
            terrain.WaterRelativeHeight,
            terrain.SunlightDirection,
            SurfaceSegmentCount * 4);
    }

    private static void SetFogParameters(
        ShaderMaterial material,
        Level100HeightFieldAsset terrain)
    {
        material.SetShaderParameter("fog_color", new Vector3(
            terrain.FogColor.R,
            terrain.FogColor.G,
            terrain.FogColor.B));
        material.SetShaderParameter("fog_density", terrain.FogDensity);
    }

    public void Update(Vector3 cameraPosition)
    {
        _grid.Position = new Vector3(cameraPosition.X, _waterHeight, cameraPosition.Z);

        Vector3 reflectedLight = _sunlightDirection.Bounce(Vector3.Up).Normalized();
        Vector3 ray = -reflectedLight;
        if (ray.Y >= -0.0001f || cameraPosition.Y <= _waterHeight)
        {
            _sunReflection.Visible = false;
            return;
        }

        float distance = (_waterHeight - cameraPosition.Y) / ray.Y;
        if (!float.IsFinite(distance) || distance <= 0f || distance > 2_000f)
        {
            _sunReflection.Visible = false;
            return;
        }

        Vector3 center = cameraPosition + (ray * distance);
        _sunReflection.Position = new Vector3(
            center.X,
            _waterHeight + (ShorelineDepthBias * 2f),
            center.Z);
        _sunReflection.Rotation = new Vector3(
            0f,
            Mathf.Atan2(ray.X, ray.Z),
            0f);
        _sunReflection.Visible = true;
    }

    private static ArrayMesh BuildGridMesh()
    {
        int vertexCount = GridVerticesPerAxis * GridVerticesPerAxis;
        var vertices = new Vector3[vertexCount];
        var colors = new Color[vertexCount];
        var indices = new int[GridCellsPerAxis * GridCellsPerAxis * 6];

        int vertex = 0;
        for (int z = 0; z < GridVerticesPerAxis; z++)
        {
            float localZ = GridStart + (z * GridStep);
            for (int x = 0; x < GridVerticesPerAxis; x++)
            {
                float localX = GridStart + (x * GridStep);
                vertices[vertex] = new Vector3(localX, 0f, localZ);
                int alpha = Math.Clamp(
                    500 - (int)MathF.Round(
                        MathF.Sqrt((localX * localX) + (localZ * localZ)) *
                        RadialScale *
                        500f),
                    0,
                    255);
                colors[vertex] = new Color(1f, 1f, 1f, alpha / 255f);
                vertex++;
            }
        }

        int index = 0;
        for (int z = 0; z < GridCellsPerAxis; z++)
        {
            for (int x = 0; x < GridCellsPerAxis; x++)
            {
                int topLeft = (z * GridVerticesPerAxis) + x;
                int bottomLeft = topLeft + GridVerticesPerAxis;
                indices[index++] = topLeft;
                indices[index++] = bottomLeft;
                indices[index++] = topLeft + 1;
                indices[index++] = topLeft + 1;
                indices[index++] = bottomLeft;
                indices[index++] = bottomLeft + 1;
            }
        }

        return BuildMeshSurface(vertices, colors, null, indices);
    }

    private static ArrayMesh BuildShorelineMesh(
        string resourcePath,
        string expectedSha256,
        Material material)
    {
        byte[] source = Godot.FileAccess.GetFileAsBytes(resourcePath);
        if (source.Length != SurfaceSourceLength ||
            !StringComparer.OrdinalIgnoreCase.Equals(
                Convert.ToHexString(SHA256.HashData(source)),
                expectedSha256))
        {
            throw new InvalidDataException(
                "The locally materialized Level 100 shoreline is missing or changed.");
        }
        RequireChunk(source, 0, "SURF"u8, SurfaceSourceLength - 8);
        RequireChunk(source, 8, "SURF"u8, SurfaceSourceLength - 16);
        if (BinaryPrimitives.ReadInt32LittleEndian(source.AsSpan(16, 4)) != 1)
        {
            throw new InvalidDataException("Level 100 has an unsupported shoreline array count.");
        }
        RequireChunk(source, 20, "OUTL"u8, SurfaceSourceLength - 28);
        if (BinaryPrimitives.ReadInt32LittleEndian(source.AsSpan(28, 4)) != SurfaceSegmentCount ||
            source.Length != 32 + (SurfaceRecordCount * 9 * sizeof(float)))
        {
            throw new InvalidDataException("Level 100 has an unsupported shoreline contour count.");
        }

        var contours = new Vector3[3, SurfaceRecordCount];
        int offset = 32;
        for (int point = 0; point < SurfaceRecordCount; point++)
        {
            for (int contour = 0; contour < 3; contour++)
            {
                float retailX = ReadSingle(source, offset);
                float retailY = ReadSingle(source, offset + 4);
                float retailZ = ReadSingle(source, offset + 8);
                offset += 12;
                if (!float.IsFinite(retailX) || !float.IsFinite(retailY) ||
                    BitConverter.SingleToInt32Bits(retailZ) != unchecked((int)0xC10D70A4))
                {
                    throw new InvalidDataException("Level 100 shoreline contains an invalid point.");
                }
                contours[contour, point] = new Vector3(
                    retailX - Level100HeightFieldAsset.PlayerStartX,
                    Level100HeightFieldAsset.PlayerStartElevation - retailZ,
                    Level100HeightFieldAsset.PlayerStartZ - retailY);
            }
        }

        var mesh = new ArrayMesh();
        AddShorelineBand(mesh, contours, 0, 1, innerBand: true);
        AddShorelineBand(mesh, contours, 1, 2, innerBand: false);
        mesh.SurfaceSetMaterial(0, material);
        mesh.SurfaceSetMaterial(1, material);
        return mesh;
    }

    private static void AddShorelineBand(
        ArrayMesh mesh,
        Vector3[,] contours,
        int firstContour,
        int secondContour,
        bool innerBand)
    {
        var vertices = new Vector3[SurfaceRecordCount * 2];
        var colors = new Color[vertices.Length];
        var uvs = new Vector2[vertices.Length];
        var indices = new int[SurfaceSegmentCount * 6];

        for (int point = 0; point < SurfaceRecordCount; point++)
        {
            float phase = point * 0.125f;
            float wave = MathF.Sin(phase * 0.5f) * 0.5f;
            int first = point * 2;
            int second = first + 1;
            vertices[first] = contours[firstContour, point];
            vertices[second] = contours[secondContour, point];

            if (innerBand)
            {
                colors[first] = new Color(1f, 1f, 1f, 0f);
                colors[second] = new Color(1f, 1f, 1f, 192f / 255f);
                uvs[first] = new Vector2(phase, wave - 0.25f - (phase * 0.25f));
                uvs[second] = new Vector2(phase, wave - (phase * 0.25f));
            }
            else
            {
                colors[first] = new Color(1f, 1f, 1f, 192f / 255f);
                colors[second] = new Color(0f, 0f, 0f, 1f);
                uvs[first] = new Vector2(phase, wave - (phase * 0.25f));
                uvs[second] = new Vector2(
                    phase + 0.0625f,
                    wave + 2f - (phase * 0.25f));
            }
        }

        int index = 0;
        for (int segment = 0; segment < SurfaceSegmentCount; segment++)
        {
            int first = segment * 2;
            int second = first + 1;
            int nextFirst = first + 2;
            int nextSecond = first + 3;
            indices[index++] = first;
            indices[index++] = second;
            indices[index++] = nextFirst;
            indices[index++] = nextFirst;
            indices[index++] = second;
            indices[index++] = nextSecond;
        }

        var arrays = new Godot.Collections.Array();
        arrays.Resize((int)Mesh.ArrayType.Max);
        arrays[(int)Mesh.ArrayType.Vertex] = vertices;
        arrays[(int)Mesh.ArrayType.Color] = colors;
        arrays[(int)Mesh.ArrayType.TexUV] = uvs;
        arrays[(int)Mesh.ArrayType.Index] = indices;
        mesh.AddSurfaceFromArrays(Mesh.PrimitiveType.Triangles, arrays);
    }

    private static ArrayMesh BuildSunReflectionMesh()
    {
        Vector3[] vertices =
        [
            new(-6f, 0f, -8f),
            new(6f, 0f, -8f),
            new(-6f, 0f, 8f),
            new(6f, 0f, 8f),
        ];
        Vector2[] uvs =
        [
            new(0f, 0f),
            new(1f, 0f),
            new(0f, 1f),
            new(1f, 1f),
        ];
        int[] indices = [0, 2, 1, 1, 2, 3];
        var arrays = new Godot.Collections.Array();
        arrays.Resize((int)Mesh.ArrayType.Max);
        arrays[(int)Mesh.ArrayType.Vertex] = vertices;
        arrays[(int)Mesh.ArrayType.TexUV] = uvs;
        arrays[(int)Mesh.ArrayType.Index] = indices;
        var mesh = new ArrayMesh();
        mesh.AddSurfaceFromArrays(Mesh.PrimitiveType.Triangles, arrays);
        return mesh;
    }

    private static ArrayMesh BuildMeshSurface(
        Vector3[] vertices,
        Color[] colors,
        Vector2[]? uvs,
        int[] indices)
    {
        var arrays = new Godot.Collections.Array();
        arrays.Resize((int)Mesh.ArrayType.Max);
        arrays[(int)Mesh.ArrayType.Vertex] = vertices;
        arrays[(int)Mesh.ArrayType.Color] = colors;
        if (uvs is not null)
        {
            arrays[(int)Mesh.ArrayType.TexUV] = uvs;
        }
        arrays[(int)Mesh.ArrayType.Index] = indices;
        var mesh = new ArrayMesh();
        mesh.AddSurfaceFromArrays(Mesh.PrimitiveType.Triangles, arrays);
        return mesh;
    }

    private static void RequireChunk(byte[] source, int offset, ReadOnlySpan<byte> tag, int size)
    {
        if (!source.AsSpan(offset, 4).SequenceEqual(tag) ||
            BinaryPrimitives.ReadInt32LittleEndian(source.AsSpan(offset + 4, 4)) != size)
        {
            throw new InvalidDataException("Level 100 shoreline has invalid chunk framing.");
        }
    }

    private static float ReadSingle(byte[] source, int offset) =>
        BitConverter.Int32BitsToSingle(
            BinaryPrimitives.ReadInt32LittleEndian(source.AsSpan(offset, sizeof(float))));
}
