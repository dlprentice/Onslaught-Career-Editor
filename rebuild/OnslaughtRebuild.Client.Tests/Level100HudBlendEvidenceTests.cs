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

    /// <summary>
    /// Pins the lower-right battleline instrument's composition to the bytes a
    /// device-level read of the safe copy produced, so a later "the portrait
    /// looks a bit dark, nudge it" pass has to argue with the debugger log
    /// rather than with a taste judgement. Sources:
    /// local-lab/PORTRAIT-BATTLELINE-FIELD-2026-07-26.md and
    /// local-lab/portrait-battleline-2026-07-26/.
    ///
    /// The three diffuse DWORDs (0x7fffffff darkener, 0x40ffffff portrait,
    /// 0xff6f8faf outline) and the six-fold portrait draw were read at the
    /// CVBufTexture__DrawSpriteEx call sites inside 0x00487d10
    /// CHud__RenderBattleline; the blend factors were read at the D3D device's
    /// own SetRenderState entry, not from the 0x00855540 shadow.
    /// </summary>
    [Fact]
    public void TheBattleLineCompositionMatchesTheDeviceLevelRead()
    {
        // 0x7fffffff -> alpha 127/255.
        Assert.Contains("CircleDarkenerAlpha = 127f / 255f", HudSource, StringComparison.Ordinal);
        Assert.DoesNotContain("1f, 1f, 1f, 0.76f", HudSource, StringComparison.Ordinal);

        // 0x40ffffff, issued six times under SRCALPHA/INVSRCALPHA with
        // ZWRITEENABLE=0, so every draw passes: 1 - (1 - 64/255)^6.
        Assert.Contains("PortraitDrawCount = 6", HudSource, StringComparison.Ordinal);
        Assert.Contains("PortraitDrawAlpha = 64f / 255f", HudSource, StringComparison.Ordinal);
        double composite = 1.0 - Math.Pow(1.0 - (64.0 / 255.0), 6);
        Match declared = Regex.Match(
            HudSource, @"PortraitCompositeAlpha\s*=\s*([0-9.]+)f");
        Assert.True(declared.Success, "PortraitCompositeAlpha is missing from the HUD.");
        Assert.Equal(
            composite,
            double.Parse(declared.Groups[1].Value, System.Globalization.CultureInfo.InvariantCulture),
            3);

        // The message-noise diffuse alpha byte over 66 steady-state frames of one
        // message ranged 0x3c..0x4a, mean 66.2.
        Assert.Contains("MessageNoiseAlpha = 66f / 255f", HudSource, StringComparison.Ordinal);
        Assert.InRange(66f / 255f, 0x3c / 255f, 0x4a / 255f);
    }

    /// <summary>
    /// message-noise is a DXT1 page with no coverage, so the sibling test above
    /// would normally put it on the ONE/ONE layer. Retail draws it
    /// SRCALPHA/INVSRCALPHA instead - device-confirmed - and gets away with it
    /// for two reasons this client has to reproduce exactly: the DIFFUSE alpha
    /// is ~0.26, not 1, and the quad is clipped to the instrument disc by the
    /// CircleMask depth stamp. This client has no depth stamp, so the clip is
    /// baked as CircleMask alpha in BuildMessageNoiseDiscPhases. Drop either and
    /// the page becomes the opaque rectangle the sibling test warns about.
    /// </summary>
    [Fact]
    public void MessageNoiseIsAlphaBlendedOnlyBecauseItIsDiscClippedAndFaint()
    {
        int glowLayer = HudSource.IndexOf(
            "private sealed partial class RetailHudGlowLayer", StringComparison.Ordinal);
        int glowLayerEnd = HudSource.IndexOf(
            "private sealed partial class RetailHudTextLayer", glowLayer, StringComparison.Ordinal);
        Assert.True(glowLayerEnd > glowLayer);

        // It must no longer be drawn on the additive layer, and the blue tint
        // that pass carried must be gone from the file entirely.
        Assert.DoesNotContain(
            "assets.MessageNoise,", HudSource[glowLayer..glowLayerEnd], StringComparison.Ordinal);
        Assert.DoesNotContain("0.48f, 0.66f, 1f", HudSource, StringComparison.Ordinal);

        // The disc clip is what makes the alpha-blended draw legal.
        Assert.Contains(
            "sourcePixel.A = 1f - maskImage.GetPixel(x, y).A", HudSource, StringComparison.Ordinal);
        Assert.Contains("MessageNoiseDiscPhases", HudSource, StringComparison.Ordinal);
    }
}
