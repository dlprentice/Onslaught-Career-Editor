// SPDX-License-Identifier: GPL-3.0-or-later

using System.Buffers.Binary;
using System.IO.Compression;
using System.Text.RegularExpressions;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// Pins the reason the in-level HUD's DXT1 pages are drawn additively, so that a
/// later "convert the HUD to alpha blending" pass cannot quietly turn them into
/// opaque black rectangles.
///
/// The reason is in the DDS bytes, not in a convention. A DXT1 block encodes
/// 1-bit alpha by storing colour0 &lt;= colour1, which turns index 3 into a
/// transparent texel. Those 3-colour blocks are PRESENT in every one of the
/// HUD's DXT1 pages - so the format was available to the artists - and index 3
/// is used exactly zero times in all of them. The pages therefore decode to
/// alpha 255 everywhere and carry no coverage at all.
///
/// Retail has nowhere else to get coverage from: every
/// D3DXCreateTextureFromFileEx call site in the released binary passes
/// ColorKey=0, and its luminance code is all L8/A8L8/A4L4/L16 surface-format
/// packing that never writes luminance into alpha. And retail only ever selects
/// three blends - SRCALPHA/INVSRCALPHA, ONE/ONE and ZERO/ONE. A page with no
/// coverage drawn SRCALPHA/INVSRCALPHA is an opaque rectangle, which no retail
/// frame shows, so these pages are its ONE/ONE passes.
///
/// This test reads the page list out of FirstFlightHud.cs itself, so adding a
/// DXT1 page or changing a page's declared compression re-checks the bytes.
/// </summary>
public sealed class Level100HudBlendEvidenceTests
{
    private static readonly string HudSource = File.ReadAllText(
        Path.Combine(AppContext.BaseDirectory, "godot-hud-layout-source", "FirstFlightHud.cs"));

    private static string HudAssetDirectory
    {
        get
        {
            DirectoryInfo? probe = new(AppContext.BaseDirectory);
            while (probe is not null)
            {
                string candidate = Path.Combine(
                    probe.FullName, "OnslaughtRebuild.Godot", "Assets", "Hud");
                if (Directory.Exists(candidate))
                {
                    return candidate;
                }
                probe = probe.Parent;
            }

            throw new DirectoryNotFoundException(
                "Materialized HUD assets were not found; run prepare:rebuild-assets.");
        }
    }

    /// <summary>Page names FirstFlightHud.cs declares as DXT1.</summary>
    private static IEnumerable<string> DeclaredDxt1Pages()
    {
        foreach (Match match in Regex.Matches(
            HudSource,
            @"LoadHudTexture\(\s*""(?<name>[a-z0-9\-]+)""\s*,\s*\d+\s*,\s*\d+\s*,\s*" +
            @"CuratedAyaTextureLoader\.Compression\.Dxt1\s*\)",
            RegexOptions.Singleline))
        {
            yield return match.Groups["name"].Value;
        }
    }

    private static byte[] InflateAya(byte[] source)
    {
        using var output = new MemoryStream();
        int position = 0;
        while (position < source.Length)
        {
            uint length = BinaryPrimitives.ReadUInt32LittleEndian(
                source.AsSpan(position, sizeof(uint)));
            position += sizeof(uint);
            using var compressed = new MemoryStream(source, position, checked((int)length));
            using var inflater = new ZLibStream(compressed, CompressionMode.Decompress);
            inflater.CopyTo(output);
            position += checked((int)length);
        }

        return output.ToArray();
    }

    private static (string FourCc, int Width, int Height, byte[] Body) ReadPage(string name)
    {
        byte[] dds = InflateAya(
            File.ReadAllBytes(Path.Combine(HudAssetDirectory, $"{name}.texture.aya")));
        Assert.True(dds.Length >= 128, $"{name} is not a DDS image.");
        Assert.Equal("DDS ", System.Text.Encoding.ASCII.GetString(dds, 0, 4));
        return (
            System.Text.Encoding.ASCII.GetString(dds, 84, 4),
            (int)BinaryPrimitives.ReadUInt32LittleEndian(dds.AsSpan(16, 4)),
            (int)BinaryPrimitives.ReadUInt32LittleEndian(dds.AsSpan(12, 4)),
            dds[128..]);
    }

    [Fact]
    public void TheHudDeclaresTheTwelveDxt1PagesTheReleasedArchiveContains()
    {
        Assert.Equal(
            [
                "bar-line", "battleline-outline", "damage-flash", "guns-front",
                "guns-outline", "guns-side", "guns-top", "message-noise",
                "radar-outline", "screen-marker", "threat-flash", "weapon-outline",
            ],
            DeclaredDxt1Pages().Order(StringComparer.Ordinal).ToArray());
    }

    [Fact]
    public void NoDxt1HudPageCarriesASingleTransparentTexel()
    {
        foreach (string name in DeclaredDxt1Pages())
        {
            (string fourCc, int width, int height, byte[] body) = ReadPage(name);
            Assert.Equal("DXT1", fourCc);

            int blocks = (width / 4) * (height / 4);
            int threeColourBlocks = 0;
            int transparentTexels = 0;
            for (int block = 0; block < blocks; block++)
            {
                int offset = block * 8;
                ushort colour0 = BinaryPrimitives.ReadUInt16LittleEndian(body.AsSpan(offset, 2));
                ushort colour1 = BinaryPrimitives.ReadUInt16LittleEndian(body.AsSpan(offset + 2, 2));
                if (colour0 > colour1)
                {
                    continue;
                }

                threeColourBlocks++;
                uint indices = BinaryPrimitives.ReadUInt32LittleEndian(body.AsSpan(offset + 4, 4));
                for (int texel = 0; texel < 16; texel++)
                {
                    if (((indices >> (2 * texel)) & 3u) == 3u)
                    {
                        transparentTexels++;
                    }
                }
            }

            // The punch-through encoding was available in this very page...
            Assert.True(
                threeColourBlocks > 0,
                $"{name} has no 3-colour DXT1 blocks, so this test proves nothing about it.");
            // ...and the artists never used it, so the page has no coverage and
            // cannot be alpha-blended without becoming an opaque rectangle.
            Assert.Equal(0, transparentTexels);
        }
    }

    [Fact]
    public void CompassObjectiveMarkerCarriesRealAlphaAndIsNotOnTheAdditiveLayer()
    {
        // It is the compass marker that retail alpha-blends: CDXCompass__Render
        // restores SRCALPHA/INVSRCALPHA for its final pass. Unlike the DXT1
        // pages it has the coverage that needs, so it must not drift back onto
        // the additive layer.
        Assert.Equal("DXT2", ReadPage("compass-objective-marker").FourCc);

        int glowLayer = HudSource.IndexOf(
            "private sealed partial class RetailHudGlowLayer", StringComparison.Ordinal);
        Assert.True(glowLayer > 0, "RetailHudGlowLayer is missing from the HUD.");
        int glowLayerEnd = HudSource.IndexOf(
            "private sealed partial class RetailHudTextLayer", glowLayer, StringComparison.Ordinal);
        Assert.True(glowLayerEnd > glowLayer, "RetailHudTextLayer is missing from the HUD.");

        Assert.DoesNotContain(
            "CompassObjectiveMarker",
            HudSource[glowLayer..glowLayerEnd],
            StringComparison.Ordinal);
    }

    [Fact]
    public void TheAdditiveLayerIsTheOnlyLayerThatDeclaresAnAddBlendMode()
    {
        Assert.Single(
            Regex.Matches(HudSource, @"BlendMode\s*=\s*CanvasItemMaterial\.BlendModeEnum\.Add"));
    }
}
