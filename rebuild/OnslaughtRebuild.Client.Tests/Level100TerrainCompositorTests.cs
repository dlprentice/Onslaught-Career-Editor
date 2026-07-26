// SPDX-License-Identifier: GPL-3.0-or-later

using System.Security.Cryptography;
using OnslaughtRebuild.Core;
using OnslaughtRebuild.GodotClient;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// Levels 1-4 of the Level 100 macro cache are produced entirely by
/// <c>Level100TerrainCompositor.RenderTile</c>, and level 0 - the only
/// hash-pinned macro data - is selected only beyond 128 units. Everything the
/// camera sees inside 128 units therefore comes from this compositor. Running
/// it at level 0 over the whole tile grid produces the same 512x512 RGB565
/// buffer as the pinned root map, so the pinned map is a byte oracle for the
/// compositor itself.
/// </summary>
public sealed class Level100TerrainCompositorTests
{
    private const string RootTextureSha256 =
        "6EB202F450926097930BEDCA440F0163A1886572981E3C69B4EDF9289A68AE2B";

    [Fact]
    public void RenderTileAtLevelZeroReproducesThePinnedRootTerrainMap()
    {
        byte[] pinnedRoot = ReadAsset(
            "Assets/Level100/Source/level100-root-terrain.rgb565.bin");
        Assert.Equal(Level100TerrainCompositor.RootTextureLength, pinnedRoot.Length);
        Assert.Equal(
            RootTextureSha256,
            Convert.ToHexString(SHA256.HashData(pinnedRoot)));

        Level100Terrain terrain = Level100Terrain.Instance;
        Level100TerrainCompositor compositor = Level100TerrainCompositor.Create(
            ReadAsset("Assets/Level100/Source/level100-terrain-hierarchy.bin"),
            terrain.SunColorRgb24,
            terrain.AmbientColorRgb24);

        var rendered = new byte[Level100TerrainCompositor.RootTextureLength];
        for (int tileY = 0; tileY < Level100TerrainCompositor.TileCountPerAxis; tileY++)
        {
            for (int tileX = 0; tileX < Level100TerrainCompositor.TileCountPerAxis; tileX++)
            {
                compositor.RenderTile(rendered, 0, tileX, tileY, tileX, tileY);
            }
        }

        int mismatches = 0;
        int firstMismatch = -1;
        for (int index = 0; index < pinnedRoot.Length; index++)
        {
            if (rendered[index] == pinnedRoot[index])
            {
                continue;
            }
            mismatches++;
            if (firstMismatch < 0)
            {
                firstMismatch = index;
            }
        }

        Assert.True(
            mismatches == 0,
            $"Level 100 macro compositor diverged from the pinned root map in " +
            $"{mismatches} of {pinnedRoot.Length} bytes; first at byte {firstMismatch} " +
            $"(texel {firstMismatch / 2}, x {(firstMismatch / 2) % 512}, " +
            $"y {(firstMismatch / 2) / 512}).");
        Assert.Equal(
            RootTextureSha256,
            Convert.ToHexString(SHA256.HashData(rendered)));
    }

    [Fact]
    public void TerrainShaderPinsTheRetailDetailRotationAndCloudScrollConstants()
    {
        string shaderSource = ReadSourceText(
            "rebuild/OnslaughtRebuild.Godot/Level100TerrainAppearanceAsset.cs");

        // .rdata 0x005d858c = 0.25 (stage-3 scale) and 0x005d87e0 = 0.0
        // (stage-3 rotation angle). The image has no .reloc section, so both are
        // fixed for the life of the process: stage 3 is an axis-aligned quarter
        // scale with offset (0.3, 0.3), never a rotation.
        Assert.Contains(
            "vec2 detail_secondary_uv = (retail_world_uv * 0.25) + vec2(0.3);",
            shaderSource);
        Assert.DoesNotContain("0.1350755765", shaderSource);
        Assert.DoesNotContain("0.2103677462", shaderSource);

        // .rdata 0x005d8580 = 0.001 and 0x005e50e4 = 0.0005, wrapped at
        // 0x005d8568 = 1.0.
        Assert.Contains(
            "vec2 cloud_scroll = fract(vec2(TIME * 0.001, TIME * 0.0005));",
            shaderSource);
        Assert.DoesNotContain("TIME * 0.02", shaderSource);
        Assert.DoesNotContain("TIME * 0.01)", shaderSource);
    }

    private static byte[] ReadAsset(string relativePath) =>
        File.ReadAllBytes(Locate($"rebuild/OnslaughtRebuild.Godot/{relativePath}"));

    private static string ReadSourceText(string repositoryRelativePath) =>
        File.ReadAllText(Locate(repositoryRelativePath));

    private static string Locate(string repositoryRelativePath)
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            string candidate = Path.Combine(
                directory.FullName,
                repositoryRelativePath.Replace('/', Path.DirectorySeparatorChar));
            if (File.Exists(candidate))
            {
                return candidate;
            }
            directory = directory.Parent;
        }
        throw new FileNotFoundException(
            $"Could not locate '{repositoryRelativePath}'. Run 'npm run prepare:rebuild-assets'.");
    }
}
