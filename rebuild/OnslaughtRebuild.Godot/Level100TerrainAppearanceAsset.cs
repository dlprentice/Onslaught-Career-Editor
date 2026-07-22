// SPDX-License-Identifier: GPL-3.0-or-later

using System.Security.Cryptography;
using Godot;

namespace OnslaughtRebuild.GodotClient;

internal sealed class Level100TerrainAppearanceAsset
{
    private const int MapSize = 512;
    private const int TileCountPerAxis = 64;
    private const int TileCount = TileCountPerAxis * TileCountPerAxis;
    private const int TileWidth = 8;
    private const int MaterialCount = 6;
    private const int PaletteEntriesPerMaterial = 256;
    private const int WeightCountPerLayer = 9 * 9;
    private const int ShadowBytesPerTile = 64 * 64 / 8;
    private const int RootTextureLength = MapSize * MapSize * sizeof(ushort);
    private const string RootTextureSha256 =
        "6EB202F450926097930BEDCA440F0163A1886572981E3C69B4EDF9289A68AE2B";
    private const string HierarchySourceSha256 =
        "541EACD0AA75FAE8BEFB8A3E1505EA52AE6B1F6C1367C15C65D7DD23B7CFE977";

    private static readonly int[] s_pineLevelOffsets = [0, 1, 5, 21, 85, 341, 1_365];

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

        vec3 sample_macro_map(int level) {
            if (level == 4) {
                return texture(macro_map_4, UV / 32.0).rgb;
            }
            if (level == 3) {
                return texture(macro_map_3, UV / 64.0).rgb;
            }
            if (level == 2) {
                return texture(macro_map_2, UV / 128.0).rgb;
            }
            if (level == 1) {
                return texture(macro_map_1, UV / 256.0).rgb;
            }
            return texture(macro_map_0, UV / 512.0).rgb;
        }

        void fragment() {
            int macro_level = int(clamp(floor(UV2.x + 0.5), 0.0, 4.0));
            vec3 macro_color = sample_macro_map(macro_level);
            vec2 retail_world_uv = UV;
            vec3 detail_primary = texture(detail_map, retail_world_uv).rgb;
            vec2 detail_secondary_uv = vec2(
                (0.1350755765 * retail_world_uv.x) -
                    (0.2103677462 * retail_world_uv.y) + 0.3,
                (0.2103677462 * retail_world_uv.x) +
                    (0.1350755765 * retail_world_uv.y) + 0.3);
            vec3 detail_secondary = texture(detail_map, detail_secondary_uv).rgb;
            vec3 cloud_shadow = texture(
                cloud_shadow_map,
                (retail_world_uv / 256.0) + vec2(TIME * 0.02, TIME * 0.01)).rgb;
            vec3 stage_color = macro_color;
            stage_color *= detail_primary;
            stage_color = min(stage_color * cloud_shadow * 2.0, vec3(1.0));
            vec3 retail_color = min(stage_color * detail_secondary * 2.0, vec3(1.0));
            retail_color = apply_retail_fog(retail_color, max(-VERTEX.z, 0.0));
            ALBEDO = retail_output(retail_color);
        }
        """;

    private readonly TerrainHierarchy _hierarchy;
    private readonly LightingCoefficient[] _lighting;
    private readonly ImageTexture[] _macroTextures = new ImageTexture[5];
    private readonly byte[][] _cacheBytes = new byte[5][];
    private readonly int[][] _slotOwners = new int[5][];
    private readonly int[][] _occupiedSlots = new int[5][];
    private readonly ShaderMaterial _material;

    private Level100TerrainAppearanceAsset(
        TerrainHierarchy hierarchy,
        byte[] rootTexture,
        Texture2D detailTexture,
        Texture2D cloudShadowTexture,
        Level100HeightFieldAsset heightField)
    {
        _hierarchy = hierarchy;
        _lighting = BuildLightingGradient(
            heightField.SunColorRgb24,
            heightField.AmbientColorRgb24);
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
            Code = TerrainShaderCode,
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
    }

    public Material Material => _material;

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

        TerrainHierarchy hierarchy = TerrainHierarchy.Load(hierarchyResourcePath);
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
            hierarchy,
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

            RenderTile(level, selection.TileX, selection.TileY, slotX, slotY);
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

    private void RenderTile(int level, int tileX, int tileY, int slotX, int slotY)
    {
        int scale = 1 << level;
        int blockSize = TileWidth * scale;
        var block = new ushort[blockSize * blockSize];
        MapTexture map = _hierarchy.Maps[level];
        TerrainCell cell = _hierarchy.Cells[(tileY * TileCountPerAxis) + tileX];
        byte[]? shadow = _hierarchy.Shadows[(tileY * TileCountPerAxis) + tileX];

        for (int controlY = 0; controlY < TileWidth; controlY++)
        {
            int shadeY = (tileY * TileWidth) + controlY;
            for (int controlX = 0; controlX < TileWidth; controlX++)
            {
                int shadeX = (tileX * TileWidth) + controlX;
                int shadeTopLeft = Shade(shadeX, shadeY);
                int shadeTopRight = Shade(Math.Min(shadeX + 1, MapSize - 1), shadeY);
                int shadeBottomLeft = Shade(shadeX, Math.Min(shadeY + 1, MapSize - 1));
                int shadeBottomRight = Shade(
                    Math.Min(shadeX + 1, MapSize - 1),
                    Math.Min(shadeY + 1, MapSize - 1));
                int shadeHorizontal = ((shadeTopRight - shadeTopLeft) << 8) >> level;
                int shadeVertical = ((shadeBottomLeft - shadeTopLeft) << 8) >> level;
                int shadeCross = unchecked(
                    (((shadeBottomRight - shadeBottomLeft) -
                      (shadeTopRight - shadeTopLeft)) << 8) >> (level * 2));

                for (int subY = 0; subY < scale; subY++)
                {
                    int pixelY = (controlY * scale) + subY;
                    // The released lighting loop advances both row slopes
                    // before its first texel; material weights do not.
                    int shadeRow = (shadeTopLeft << 8) + ((subY + 1) * shadeVertical);
                    int shadeStep = shadeHorizontal + ((subY + 1) * shadeCross);
                    for (int subX = 0; subX < scale; subX++)
                    {
                        int pixelX = (controlX * scale) + subX;
                        int sourceX = ((tileX & 1) * blockSize) + pixelX;
                        int sourceY = ((tileY & 1) * blockSize) + pixelY;
                        int sourceTexel = (sourceY * map.Width) + sourceX;
                        uint color = LookupColor(map, 0, sourceTexel);

                        for (int layer = 0; layer < cell.MaterialIds.Length; layer++)
                        {
                            int weightOffset = (layer * WeightCountPerLayer) +
                                (controlY * 9) + controlX;
                            int weightTopLeft = (sbyte)cell.Weights[weightOffset];
                            int weightTopRight = (sbyte)cell.Weights[weightOffset + 1];
                            int weightBottomLeft = (sbyte)cell.Weights[weightOffset + 9];
                            int weightBottomRight = (sbyte)cell.Weights[weightOffset + 10];
                            int weightHorizontal = unchecked(
                                ((weightTopRight - weightTopLeft) << 24) >> level);
                            int weightVertical = unchecked(
                                ((weightBottomLeft - weightTopLeft) << 24) >> level);
                            int weightCross = unchecked(
                                (((weightBottomRight - weightBottomLeft) -
                                  (weightTopRight - weightTopLeft)) << 24) >> (level * 2));
                            int weight = unchecked(
                                (weightTopLeft << 24) +
                                (subY * weightVertical) +
                                (subX * (weightHorizontal + (subY * weightCross))));
                            uint candidate = unchecked(
                                LookupColor(map, cell.MaterialIds[layer], sourceTexel) +
                                (uint)(weight & unchecked((int)0xFF000000)));
                            color = BlendMaterial(color, candidate);
                        }

                        int shadeValue = Math.Clamp(
                            (shadeRow + ((subX + 1) * shadeStep)) >> 8,
                            0,
                            63);
                        if (shadow is not null)
                        {
                            int shadowX = (pixelX * 8) / scale;
                            int shadowY = (pixelY * 8) / scale;
                            int shadowBit = (shadowY * 64) + shadowX;
                            if ((shadow[shadowBit >> 3] & (1 << (shadowBit & 7))) != 0)
                            {
                                shadeValue >>= 1;
                            }
                        }

                        LightingCoefficient light = _lighting[shadeValue];
                        uint red = color & 0xFF;
                        uint green = (color >> 8) & 0xFF;
                        uint blue = (color >> 16) & 0xFF;
                        block[(pixelY * blockSize) + pixelX] = (ushort)(
                            ((green * light.Green & 0x07E00000) +
                             (blue * light.Blue & 0x001F0000) +
                             (red * light.Red & 0xF8000000)) >> 16);
                    }
                }
            }
        }

        ApplyPineShadows(block, blockSize, level, tileX, tileY);
        int destinationX = slotX * blockSize;
        int destinationY = slotY * blockSize;
        byte[] cache = _cacheBytes[level];
        for (int pixelY = 0; pixelY < blockSize; pixelY++)
        {
            int destination = (((destinationY + pixelY) * MapSize) + destinationX) * sizeof(ushort);
            for (int pixelX = 0; pixelX < blockSize; pixelX++)
            {
                ushort value = block[(pixelY * blockSize) + pixelX];
                cache[destination++] = (byte)value;
                cache[destination++] = (byte)(value >> 8);
            }
        }
    }

    private int Shade(int x, int y) => _hierarchy.Shade[(y * MapSize) + x];

    private void ApplyPineShadows(
        ushort[] block,
        int blockSize,
        int logicalLevel,
        int tileX,
        int tileY)
    {
        int scale = 1 << logicalLevel;
        int blockOriginX = tileX * TileWidth * scale;
        int blockOriginY = tileY * TileWidth * scale;
        for (int descriptorIndex = _hierarchy.Pines.Length - 1;
             descriptorIndex >= 0;
             descriptorIndex--)
        {
            PineShadow pine = _hierarchy.Pines[descriptorIndex];
            int alphaLevel = pine.RootLevel + logicalLevel;
            int dimension = 1 << alphaLevel;
            int localTopX = (pine.TopX * scale) - blockOriginX;
            int localTopY = (pine.TopY * scale) - blockOriginY;
            if (localTopX >= blockSize || localTopY >= blockSize ||
                localTopX + dimension <= 0 || localTopY + dimension <= 0)
            {
                continue;
            }

            int alphaOffset = s_pineLevelOffsets[alphaLevel];
            for (int sourceY = 0; sourceY < dimension; sourceY++)
            {
                int targetY = localTopY + sourceY;
                if ((uint)targetY >= blockSize)
                {
                    continue;
                }
                for (int sourceX = 0; sourceX < dimension; sourceX++)
                {
                    int targetX = localTopX + sourceX;
                    if ((uint)targetX >= blockSize)
                    {
                        continue;
                    }
                    int amount = _hierarchy.PineAlpha[
                        alphaOffset + (sourceY * dimension) + sourceX];
                    if (amount >= 32)
                    {
                        continue;
                    }
                    int target = (targetY * blockSize) + targetX;
                    uint destination = block[target];
                    uint pair = ((destination << 16) | destination) & 0x07E0F81F;
                    uint scaled = ((pair * (uint)amount) >> 5) & 0x07E0F81F;
                    block[target] = (ushort)((scaled >> 16) + scaled);
                }
            }
        }
    }

    private static uint LookupColor(MapTexture map, int material, int texel)
    {
        int paletteIndex = map.Indices[(material * map.Width * map.Width) + texel];
        return map.Palette[(material * PaletteEntriesPerMaterial) + paletteIndex];
    }

    private static uint BlendMaterial(uint color, uint candidate)
    {
        int difference = unchecked((int)(candidate - color));
        if (difference > 0x1FFFFFFF)
        {
            return candidate;
        }
        if (difference < 0)
        {
            return color;
        }

        uint blend = (uint)difference >> 26;
        return unchecked(
            ((((color & 0x00F8F8FF) * (7 - blend)) +
               ((candidate & 0x00F8F8FF) * blend)) >> 3) +
            (candidate & 0xFF000000));
    }

    private static ImageTexture CreateRgb565Texture(byte[] bytes)
    {
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

    private static LightingCoefficient[] BuildLightingGradient(uint sunColor, uint ambientColor)
    {
        int redBase = (int)((((ambientColor >> 16) & 0xFF) << 8) /
            (((sunColor >> 16) & 0xFE) + 1));
        int greenBase = (int)((ambientColor & 0xFF00) /
            (((sunColor >> 8) & 0xFE) + 1));
        int blueBase = (int)(((ambientColor & 0xFF) << 8) /
            ((sunColor & 0xFE) + 1));
        int red = redBase << 8;
        int green = greenBase << 8;
        int blue = blueBase << 8;
        var result = new LightingCoefficient[64];
        for (int index = 0; index < result.Length; index++)
        {
            uint redValue = (uint)Math.Min(((red >> 8) << 16) * 2, 0x00F80000) & 0x00F80000;
            uint greenValue = (uint)Math.Min(((green >> 8) << 11) * 2, 0x0007E000) & 0x0007E000;
            uint blueValue = (uint)Math.Min(((blue >> 3) & unchecked((int)0xFFFFFFE0)) * 2, 0x00001F00) & 0x00001F00;
            result[index] = new LightingCoefficient(redValue, greenValue, blueValue);
            red += (255 - redBase) * 4;
            green += (255 - greenBase) * 4;
            blue += (255 - blueBase) * 4;
        }
        return result;
    }

    private readonly record struct LightingCoefficient(uint Red, uint Green, uint Blue);

    private sealed record MapTexture(int Width, byte[] Indices, uint[] Palette);

    private sealed record TerrainCell(byte[] MaterialIds, byte[] Weights);

    private readonly record struct PineShadow(short TopX, short TopY, byte RootLevel);

    private sealed record TerrainHierarchy(
        MapTexture[] Maps,
        TerrainCell[] Cells,
        byte[] Shade,
        byte[]?[] Shadows,
        byte[] PineAlpha,
        PineShadow[] Pines)
    {
        public static TerrainHierarchy Load(string resourcePath)
        {
            byte[] source = Godot.FileAccess.GetFileAsBytes(resourcePath);
            if (!StringComparer.Ordinal.Equals(
                    Convert.ToHexString(SHA256.HashData(source)),
                    HierarchySourceSha256))
            {
                throw new InvalidDataException(
                    "Level 100 terrain hierarchy does not match its retail-derived identity.");
            }

            using var stream = new MemoryStream(source, writable: false);
            using var reader = new BinaryReader(stream);
            if (!reader.ReadBytes(4).SequenceEqual("LTH1"u8.ToArray()) ||
                reader.ReadUInt32() != 1 ||
                reader.ReadUInt32() != 5)
            {
                throw new InvalidDataException("Level 100 terrain hierarchy has an invalid header.");
            }

            var maps = new MapTexture[5];
            for (int level = 0; level < maps.Length; level++)
            {
                int width = reader.ReadInt32();
                int expectedWidth = 16 << level;
                int dataLength = reader.ReadInt32();
                if (width != expectedWidth || dataLength != MaterialCount * width * width)
                {
                    throw new InvalidDataException(
                        $"Level 100 MAPT level {level} has invalid dimensions.");
                }
                byte[] indices = ReadExactly(reader, dataLength);
                int paletteLength = reader.ReadInt32();
                if (paletteLength != MaterialCount * PaletteEntriesPerMaterial)
                {
                    throw new InvalidDataException(
                        $"Level 100 MAPT level {level} has an invalid palette.");
                }
                var palette = new uint[paletteLength];
                for (int index = 0; index < palette.Length; index++)
                {
                    palette[index] = reader.ReadUInt32();
                }
                maps[level] = new MapTexture(width, indices, palette);
            }

            if (reader.ReadInt32() != TileCount)
            {
                throw new InvalidDataException("Level 100 terrain hierarchy has an invalid cell count.");
            }
            var cells = new TerrainCell[TileCount];
            for (int index = 0; index < cells.Length; index++)
            {
                int layerCount = reader.ReadByte();
                if (layerCount is < 1 or > 5)
                {
                    throw new InvalidDataException(
                        $"Level 100 terrain cell {index} has an invalid layer count.");
                }
                byte[] materialIds = ReadExactly(reader, layerCount);
                if (materialIds.Any(material => material >= MaterialCount))
                {
                    throw new InvalidDataException(
                        $"Level 100 terrain cell {index} has an invalid material.");
                }
                cells[index] = new TerrainCell(
                    materialIds,
                    ReadExactly(reader, layerCount * WeightCountPerLayer));
            }

            int shadeLength = reader.ReadInt32();
            if (shadeLength != MapSize * MapSize)
            {
                throw new InvalidDataException("Level 100 terrain hierarchy has an invalid shade map.");
            }
            byte[] shade = ReadExactly(reader, shadeLength);
            if (shade.Any(value => value > 63))
            {
                throw new InvalidDataException("Level 100 terrain hierarchy has an invalid shade value.");
            }

            int shadowCount = reader.ReadInt32();
            if (shadowCount != 211)
            {
                throw new InvalidDataException("Level 100 terrain hierarchy has an invalid shadow count.");
            }
            var shadows = new byte[]?[TileCount];
            for (int index = 0; index < shadowCount; index++)
            {
                int tileIndex = reader.ReadUInt16();
                if ((uint)tileIndex >= TileCount || shadows[tileIndex] is not null)
                {
                    throw new InvalidDataException("Level 100 terrain hierarchy has an invalid shadow tile.");
                }
                shadows[tileIndex] = ReadExactly(reader, ShadowBytesPerTile);
            }

            int pineAlphaLength = reader.ReadInt32();
            if (pineAlphaLength != 5_461)
            {
                throw new InvalidDataException("Level 100 terrain hierarchy has invalid pine alpha.");
            }
            byte[] pineAlpha = ReadExactly(reader, pineAlphaLength);
            int pineCount = reader.ReadInt32();
            if (pineCount != 1_481)
            {
                throw new InvalidDataException("Level 100 terrain hierarchy has an invalid pine count.");
            }
            var pines = new PineShadow[pineCount];
            for (int index = 0; index < pines.Length; index++)
            {
                short topX = reader.ReadInt16();
                short topY = reader.ReadInt16();
                byte rootLevel = reader.ReadByte();
                if (rootLevel is < 1 or > 2)
                {
                    throw new InvalidDataException(
                        $"Level 100 pine shadow {index} has an invalid level.");
                }
                pines[index] = new PineShadow(topX, topY, rootLevel);
            }
            if (stream.Position != stream.Length)
            {
                throw new InvalidDataException("Level 100 terrain hierarchy has trailing data.");
            }
            return new TerrainHierarchy(maps, cells, shade, shadows, pineAlpha, pines);
        }

        private static byte[] ReadExactly(BinaryReader reader, int count)
        {
            byte[] result = reader.ReadBytes(count);
            if (result.Length != count)
            {
                throw new InvalidDataException("Level 100 terrain hierarchy is truncated.");
            }
            return result;
        }
    }
}
