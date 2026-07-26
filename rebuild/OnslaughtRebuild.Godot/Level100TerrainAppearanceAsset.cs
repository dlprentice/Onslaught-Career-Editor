// SPDX-License-Identifier: GPL-3.0-or-later

using System.Security.Cryptography;
using Godot;

namespace OnslaughtRebuild.GodotClient;

internal sealed class Level100TerrainAppearanceAsset
{
    private const int MapSize = Level100TerrainCompositor.MapSize;
    private const int TileCountPerAxis = Level100TerrainCompositor.TileCountPerAxis;
    private const int RootTextureLength = Level100TerrainCompositor.RootTextureLength;
    private const string RootTextureSha256 =
        "6EB202F450926097930BEDCA440F0163A1886572981E3C69B4EDF9289A68AE2B";

    // Retail creates the landscape cache texture through
    // CLandscapeTexture__Init -> CUMTexture__ConfigureByMode(this, size, 1, 1)
    // -> CUMTexture__RecreateTextureResource -> CEngine__CreateTextureUnchecked,
    // whose device vtable slot 0x5c is ltshell.h
    // D3D_CreateTexture(Width, Height, Levels, Usage, Format, Pool, ppTexture, pData).
    // ConfigureByMode stores the third argument (1) at this+0x18, and
    // RecreateTextureResource passes this+0x18 as Levels. Retail's macro cache is
    // therefore a ONE-LEVEL texture with no D3D mip chain, which is why these
    // images are built useMipmaps: false. Retail still asks for anisotropic
    // minification of that single level on stage 0 only
    // (CDXLandscape__RenderTerrain 0x00545590: SetSamplerState(0, MINFILTER,
    // D3DTEXF_ANISOTROPIC) and SetSamplerState(0, MAXANISOTROPY, 4)), which is what
    // filter_linear_mipmap_anisotropic reproduces here: with a single stored level
    // the mip term is inert and only the anisotropic taps of level 0 remain, and
    // Godot's default anisotropy is retail's own 4.
    private const string TerrainShaderCode = """
        shader_type spatial;
        render_mode unshaded;

        // Steam owns macro UVs as repeated absolute landscape X/Y in each
        // 20-byte vertex. Each logical level is an independent one-level
        // 512x512 cache with a progressively smaller virtual world span.
        uniform sampler2D macro_map_0 : filter_linear_mipmap_anisotropic, repeat_enable;
        uniform sampler2D macro_map_1 : filter_linear_mipmap_anisotropic, repeat_enable;
        uniform sampler2D macro_map_2 : filter_linear_mipmap_anisotropic, repeat_enable;
        uniform sampler2D macro_map_3 : filter_linear_mipmap_anisotropic, repeat_enable;
        uniform sampler2D macro_map_4 : filter_linear_mipmap_anisotropic, repeat_enable;
        uniform sampler2D detail_map : filter_linear_mipmap, repeat_enable;
        uniform sampler2D cloud_shadow_map : filter_linear_mipmap, repeat_enable;
        uniform vec3 fog_color;
        uniform float fog_density;
        // The constant lit vertex colour of retail's terrain draw:
        // 0.8 x (CHFD+0x107C + CHFD+0x1080) / 256, computed at load from the
        // shipped HFLD by Level100TerrainCompositor.TerrainVertexDiffuse. The
        // terrain vertex carries no normal, so this is one colour for the whole
        // surface with no positional term.
        uniform vec3 terrain_vertex_diffuse;

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

        vec3 sample_macro_map(int level, vec2 retail_world_uv) {
            if (level == 4) {
                return texture(macro_map_4, retail_world_uv / 32.0).rgb;
            }
            if (level == 3) {
                return texture(macro_map_3, retail_world_uv / 64.0).rgb;
            }
            if (level == 2) {
                return texture(macro_map_2, retail_world_uv / 128.0).rgb;
            }
            if (level == 1) {
                return texture(macro_map_1, retail_world_uv / 256.0).rgb;
            }
            return texture(macro_map_0, retail_world_uv / 512.0).rgb;
        }

        void fragment() {
            vec2 retail_world_uv = UV;
            int macro_level = int(clamp(floor(UV2.x + 0.5), 0.0, 4.0));
            vec3 macro_color = sample_macro_map(macro_level, retail_world_uv);
            vec3 detail_primary = texture(detail_map, retail_world_uv).rgb;
            // Retail's stage-3 texture matrix is
            // [k*cos(t), k*sin(t); -k*sin(t), k*cos(t)] with offset (0.3, 0.3),
            // k = *(float *)0x005d858c = 0.25 and t = *(float *)0x005d87e0 = 0.0.
            // Both live in .rdata (0x005d8000..0x00622000) in a .reloc-free image,
            // so the angle is fixed at zero for the life of the process and the
            // matrix is a pure uniform quarter-scale aligned with stage 1.
            vec2 detail_secondary_uv = (retail_world_uv * 0.25) + vec2(0.3);
            vec3 detail_secondary = texture(detail_map, detail_secondary_uv).rgb;
            // Retail accumulates the stage-2 translation as
            // u += dt * *(float *)0x005d8580 (0.001) and
            // v += dt * *(float *)0x005e50e4 (0.0005), wrapping at
            // *(float *)0x005d8568 (1.0).
            vec2 cloud_scroll = fract(vec2(TIME * 0.001, TIME * 0.0005));
            vec3 cloud_shadow = texture(
                cloud_shadow_map,
                (retail_world_uv / 256.0) + cloud_scroll).rgb;
            // Stage 0 is COLORARG1 = D3DTA_TEXTURE, COLORARG2 = D3DTA_DIFFUSE
            // (0x00545699, 0x005456a8) with COLOROP = D3DTOP_MODULATE2X
            // (0x005454ae; the MODULATE alternative at 0x0054568a is taken only
            // when LANDSCAPE_LIGHTING is zero, and its default is 1). So the
            // macro texel is multiplied by the lit vertex colour and doubled.
            // The 2.0 is the stage op and terrain_vertex_diffuse is the lighting
            // term; neither is meaningful without the other, and applying the
            // doubling alone overshoots.
            // Fixed-function stages saturate, hence the min() - the same clamp
            // the two later 2x stages below already carry.
            vec3 stage_color = min(
                macro_color * terrain_vertex_diffuse * 2.0,
                vec3(1.0));
            stage_color *= detail_primary;
            stage_color = min(stage_color * cloud_shadow * 2.0, vec3(1.0));
            vec3 retail_color = min(stage_color * detail_secondary * 2.0, vec3(1.0));
            retail_color = apply_retail_fog(retail_color, max(-VERTEX.z, 0.0));
            ALBEDO = retail_output(retail_color);
            // PROBE_HOOK
        }
        """;

    // Analysis-only fragment tails. Each replaces ALBEDO with one measured term
    // of the terrain chain so an offline probe can invert
    //   retail_pixel = macro x detail x cloud x detail x fog
    // against retail's own frame. Selected by the ONSLAUGHT_TERRAIN_PROBE
    // environment variable; unset (the shipping path) leaves the shader byte
    // for byte as above. Captures taken with it set are stamped 'probe' by
    // Capture-Frontend.ps1 because the working tree is dirty, which is the
    // intended and correct outcome - none of these frames describe the build.
    private static readonly Dictionary<string, string> s_probeTails = new(StringComparer.Ordinal)
    {
        // Our macro cache as sampled on screen.
        ["macro"] = "ALBEDO = retail_output(macro_color);",
        // Terrain coverage mask (R==255, B==0) carrying fog visibility in G.
        ["mask"] =
            "ALBEDO = retail_output(vec3(1.0, " +
            "clamp(exp(-fog_density * max(-VERTEX.z, 0.0)), 0.0, 1.0), 0.0));",
        // The whole post-macro chain with the macro term forced to one and the
        // two saturating min() stages removed. Scaled by 0.25 so the unclamped
        // product (max 0.859 * 2 * 1.0 * 0.859 * 2 = 2.95) stays inside [0,1];
        // the offline probe multiplies by 4 to recover it.
        ["chain"] =
            "ALBEDO = retail_output(0.25 * detail_primary * cloud_shadow * 2.0 " +
            "* detail_secondary * 2.0);",
        // World identity of the shaded texel. UV is retail's absolute landscape
        // X/Y and the island spans 512 units, so this is the root-map texel
        // coordinate at 2-unit resolution, plus the selected macro level.
        ["uv"] =
            "ALBEDO = retail_output(vec3(fract(retail_world_uv / 512.0), " +
            "float(macro_level) / 8.0));",
        // Sub-unit refinement of the same identity: a 2-unit period at 1/128
        // unit resolution, which combines with 'uv' to an exact world position.
        ["uvfine"] =
            "ALBEDO = retail_output(vec3(fract(retail_world_uv / 2.0), 0.0));",
    };

    private readonly Level100TerrainCompositor _compositor;
    private readonly ImageTexture[] _macroTextures = new ImageTexture[5];
    private readonly byte[][] _cacheBytes = new byte[5][];
    private readonly int[][] _slotOwners = new int[5][];
    private readonly int[][] _occupiedSlots = new int[5][];
    private readonly ShaderMaterial _material;

    private Level100TerrainAppearanceAsset(
        Level100TerrainCompositor compositor,
        byte[] rootTexture,
        Texture2D detailTexture,
        Texture2D cloudShadowTexture,
        Level100HeightFieldAsset heightField)
    {
        _compositor = compositor;
        _macroTextures[0] = CreateRgb565Texture(rootTexture);
        _cacheBytes[0] = rootTexture;
        _slotOwners[0] = [];
        _occupiedSlots[0] = [];

        for (int level = 1; level <= 4; level++)
        {
            _cacheBytes[level] = new byte[RootTextureLength];
            _macroTextures[level] = CreateRgb565Texture(_cacheBytes[level]);
            int tilesPerAxis = TileCountPerAxis >> level;
            int slotCount = tilesPerAxis * tilesPerAxis;
            _slotOwners[level] = new int[slotCount];
            Array.Fill(_slotOwners[level], -1);
            _occupiedSlots[level] = new int[slotCount];
        }

        var shader = new Shader
        {
            Code = ProbeShaderCode(),
        };
        _material = new ShaderMaterial
        {
            Shader = shader,
        };
        for (int level = 0; level <= 4; level++)
        {
            _material.SetShaderParameter($"macro_map_{level}", _macroTextures[level]);
        }
        _material.SetShaderParameter("detail_map", detailTexture);
        _material.SetShaderParameter("cloud_shadow_map", cloudShadowTexture);
        _material.SetShaderParameter("fog_color", new Vector3(
            heightField.FogColor.R,
            heightField.FogColor.G,
            heightField.FogColor.B));
        _material.SetShaderParameter("fog_density", heightField.FogDensity);
        // CEngine::SetupLights enables cached lights 0 and 1 only, filling them
        // from CHFD+0x107C and CHFD+0x1080 - which the Core height field parses
        // as SunColorRgb24 and AntiSunColorRgb24. Read from the shipped HFLD, not
        // written down: another level's lights are other bytes.
        (float red, float green, float blue) = Level100TerrainCompositor.TerrainVertexDiffuse(
            heightField.SunColorRgb24,
            heightField.AntiSunColorRgb24);
        _material.SetShaderParameter(
            "terrain_vertex_diffuse",
            new Vector3(red, green, blue));
    }

    public Material Material => _material;

    private static string ProbeShaderCode()
    {
        string probe = OS.GetEnvironment("ONSLAUGHT_TERRAIN_PROBE");
        if (string.IsNullOrWhiteSpace(probe))
        {
            return TerrainShaderCode;
        }
        if (!s_probeTails.TryGetValue(probe.Trim(), out string? tail))
        {
            throw new InvalidDataException(
                $"ONSLAUGHT_TERRAIN_PROBE='{probe}' is not a known terrain probe mode.");
        }
        GD.Print($"[terrain-probe] fragment tail overridden: {probe.Trim()}");
        return TerrainShaderCode.Replace("// PROBE_HOOK", tail, StringComparison.Ordinal);
    }

    public static Level100TerrainAppearanceAsset Load(
        string rootTextureResourcePath,
        string hierarchyResourcePath,
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

        Level100TerrainCompositor compositor = Level100TerrainCompositor.Create(
            Godot.FileAccess.GetFileAsBytes(hierarchyResourcePath),
            heightField.SunColorRgb24,
            heightField.AmbientColorRgb24);
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
        return new Level100TerrainAppearanceAsset(
            compositor,
            rootTexture,
            detailTexture,
            cloudShadowTexture,
            heightField);
    }

    public void Update(IReadOnlyList<Level100TerrainTileSelection> selections)
    {
        for (int level = 1; level <= 4; level++)
        {
            Array.Fill(_occupiedSlots[level], -1);
        }
        Span<bool> changed = stackalloc bool[5];
        changed.Clear();

        foreach (Level100TerrainTileSelection selection in selections)
        {
            int level = selection.TextureLevel;
            if (level == 0)
            {
                continue;
            }

            int tilesPerAxis = TileCountPerAxis >> level;
            int slotX = selection.TileX & (tilesPerAxis - 1);
            int slotY = selection.TileY & (tilesPerAxis - 1);
            int slot = (slotY * tilesPerAxis) + slotX;
            int tileIndex = (selection.TileY * TileCountPerAxis) + selection.TileX;
            if (_occupiedSlots[level][slot] >= 0 &&
                _occupiedSlots[level][slot] != tileIndex)
            {
                throw new InvalidDataException(
                    $"Level 100 landscape cache {level} selected aliased active tiles.");
            }
            _occupiedSlots[level][slot] = tileIndex;

            if (_slotOwners[level][slot] == tileIndex)
            {
                continue;
            }

            _compositor.RenderTile(
                _cacheBytes[level],
                level,
                selection.TileX,
                selection.TileY,
                slotX,
                slotY);
            _slotOwners[level][slot] = tileIndex;
            changed[level] = true;
        }

        for (int level = 1; level <= 4; level++)
        {
            if (!changed[level])
            {
                continue;
            }
            Image image = Image.CreateFromData(
                MapSize,
                MapSize,
                false,
                Image.Format.Rgb565,
                _cacheBytes[level]);
            if (image.IsEmpty())
            {
                throw new InvalidDataException(
                    $"Godot could not update Level 100 landscape cache {level}.");
            }
            _macroTextures[level].Update(image);
        }
    }

    private static ImageTexture CreateRgb565Texture(byte[] bytes)
    {
        // useMipmaps: false is retail's own contract - see the D3D_CreateTexture
        // Levels == 1 derivation above the shader source.
        Image image = Image.CreateFromData(
            MapSize,
            MapSize,
            false,
            Image.Format.Rgb565,
            bytes);
        if (image.IsEmpty())
        {
            throw new InvalidDataException("Godot could not create a Level 100 landscape texture.");
        }
        return ImageTexture.CreateFromImage(image);
    }
}
