// SPDX-License-Identifier: GPL-3.0-or-later

using System.Security.Cryptography;
using Godot;

namespace OnslaughtRebuild.GodotClient;

internal static class Level100TerrainAppearanceAsset
{
    private const int MapSize = 512;
    private const int RootTextureLength = MapSize * MapSize * sizeof(ushort);
    private const string RootTextureSha256 =
        "6EB202F450926097930BEDCA440F0163A1886572981E3C69B4EDF9289A68AE2B";

    private const string TerrainShaderCode = """
        shader_type spatial;
        render_mode unshaded;

        // D3D8's fixed-function texture stages modulated the stored texture values.
        // Sample them as encoded values, reproduce that stage arithmetic, then hand
        // Godot a linear result for its sRGB framebuffer conversion.
        uniform sampler2D macro_map : filter_linear_mipmap_anisotropic, repeat_enable;
        uniform sampler2D detail_map : filter_linear_mipmap, repeat_enable;
        uniform sampler2D cloud_shadow_map : filter_linear_mipmap, repeat_enable;
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
            vec3 macro_color = texture(macro_map, UV).rgb;
            vec2 retail_world_uv = UV * 512.0;
            vec3 detail_primary = texture(detail_map, retail_world_uv).rgb;
            vec2 detail_secondary_uv = vec2(
                (0.1350755765 * retail_world_uv.x) -
                    (0.2103677462 * retail_world_uv.y) + 0.3,
                (0.2103677462 * retail_world_uv.x) +
                    (0.1350755765 * retail_world_uv.y) + 0.3);
            vec3 detail_secondary = texture(
                detail_map,
                detail_secondary_uv).rgb;
            vec3 cloud_shadow = texture(
                cloud_shadow_map,
                (retail_world_uv / 256.0) +
                    vec2(TIME * 0.02, TIME * 0.01)).rgb;
            vec3 stage_color = macro_color;
            stage_color *= detail_primary;
            stage_color = min(stage_color * cloud_shadow * 2.0, vec3(1.0));
            vec3 retail_color = min(stage_color * detail_secondary * 2.0, vec3(1.0));
            retail_color = apply_retail_fog(retail_color, max(-VERTEX.z, 0.0));
            ALBEDO = retail_output(retail_color);
        }
        """;

    public static Material LoadMaterial(
        string rootTextureResourcePath,
        string detailTextureResourcePath,
        string cloudShadowResourcePath,
        Level100HeightFieldAsset heightField)
    {
        byte[] rootTexture = Godot.FileAccess.GetFileAsBytes(rootTextureResourcePath);
        if (rootTexture.Length != RootTextureLength ||
            !StringComparer.Ordinal.Equals(
                Convert.ToHexString(SHA256.HashData(rootTexture)),
                RootTextureSha256))
        {
            throw new InvalidDataException(
                "Level 100 root terrain texture does not match its retail-derived identity.");
        }
        if (heightField.MixerSet != 10 || heightField.DetailTexture != 0)
        {
            throw new InvalidDataException(
                "Level 100 does not select mixer set 10 and terrain detail texture 00.");
        }

        Image image = Image.CreateFromData(
            MapSize,
            MapSize,
            false,
            Image.Format.Rgb565,
            rootTexture);
        if (image.IsEmpty())
        {
            throw new InvalidDataException("Godot could not create the Level 100 landscape texture.");
        }

        Texture2D macroTexture = ImageTexture.CreateFromImage(image);
        Texture2D detailTexture = CuratedAyaTextureLoader.Load(
            detailTextureResourcePath,
            512,
            512,
            CuratedAyaTextureLoader.Compression.Dxt1);
        Texture2D cloudShadowTexture = CuratedAyaTextureLoader.Load(
            cloudShadowResourcePath,
            256,
            256,
            CuratedAyaTextureLoader.Compression.Dxt1);
        var shader = new Shader
        {
            Code = TerrainShaderCode,
        };
        var material = new ShaderMaterial
        {
            Shader = shader,
        };
        material.SetShaderParameter("macro_map", macroTexture);
        material.SetShaderParameter("detail_map", detailTexture);
        material.SetShaderParameter("cloud_shadow_map", cloudShadowTexture);
        material.SetShaderParameter("fog_color", new Vector3(
            heightField.FogColor.R,
            heightField.FogColor.G,
            heightField.FogColor.B));
        material.SetShaderParameter("fog_density", heightField.FogDensity);
        return material;
    }
}
