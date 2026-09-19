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
/// packing that never writes luminance into alpha. And retail selects four
/// blends - SRCALPHA/INVSRCALPHA, ONE/ONE, ZERO/ONE and, on the two threat-
/// compass rings only, the premultiplied ONE/INVSRCALPHA measured at the device
/// on 2026-07-27. A page with no coverage drawn SRCALPHA/INVSRCALPHA is an
/// opaque rectangle, which no retail frame shows, so these pages are its
/// ONE/ONE passes.
///
/// This test reads the page list out of hud_assets.gd itself, so adding a
/// DXT1 page or changing a page's declared compression re-checks the bytes.
/// </summary>
public sealed class Level100HudBlendEvidenceTests
{
    private static string Read(string name) => File.ReadAllText(
        Path.Combine(AppContext.BaseDirectory, "godot-hud-layout-source", name));
    private static readonly string GlowSource = Read("hud_glow_draw.gd");
    private static readonly string BaseSource = Read("hud_base_draw.gd");
    private static readonly string SceneSource = Read("FirstFlightHud.tscn");
    private static readonly string HudSource = string.Join("\n", Read("hud_draw.gd"),
        Read("hud_assets.gd"), BaseSource, GlowSource, Read("hud_text_draw.gd"), SceneSource);

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
                // Owned --artifacts-path builds are below local-data rather
                // than rebuild/. Stop at this checkout's Git entrance: an
                // absent worktree asset link must not borrow another tree.
                string gitEntrance = Path.Combine(probe.FullName, ".git");
                if (File.Exists(gitEntrance) || Directory.Exists(gitEntrance))
                {
                    candidate = Path.Combine(probe.FullName, "rebuild", "OnslaughtRebuild.Godot", "Assets", "Hud");
                    if (Directory.Exists(candidate)) return candidate;
                    break;
                }
                probe = probe.Parent;
            }

            throw new DirectoryNotFoundException(
                "Materialized HUD assets were not found; run prepare:rebuild-assets.");
        }
    }

    /// <summary>Page names the production GDScript recipes declare as DXT1 (compression 0).</summary>
    private static IEnumerable<string> DeclaredDxt1Pages()
    {
        foreach (Match match in Regex.Matches(
            HudSource,
            @"""(?<name>[a-z0-9\-]+)"": \[\d+, \d+, 0\]",
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
        Assert.Equal("DXT2", ReadPage("compass-objective-marker").FourCc);
        Assert.Contains("texture(\"compass-objective-marker\"", BaseSource, StringComparison.Ordinal);
        Assert.DoesNotContain("compass-objective-marker", GlowSource, StringComparison.Ordinal);
    }

    [Fact]
    public void EveryHudLayerAppliesTheRetailPostModulateAlphaTestAndOnlyGlowAdds()
    {
        (string fourCc, int width, int height, byte[] body) =
            ReadPage("crosshair-secondary");
        Assert.Equal("DXT2", fourCc);

        int alphaNibbleOneTexels = 0;
        int topMipBlocks = (width / 4) * (height / 4);
        for (int block = 0; block < topMipBlocks; block++)
        {
            ulong alphaNibbles = BinaryPrimitives.ReadUInt64LittleEndian(
                body.AsSpan(block * 16, 8));
            for (int texel = 0; texel < 16; texel++)
            {
                if (((alphaNibbles >> (texel * 4)) & 0xfu) == 1u)
                {
                    alphaNibbleOneTexels++;
                }
            }
        }

        // At RetailCrosshairFaint alpha 0.3412 these become 5.8/255 after
        // modulation: below ALPHAREF 8, despite the source texel being 17/255.
        Assert.Equal(20, alphaNibbleOneTexels);
        Assert.Contains("COLOR.a < (8.0 / 255.0)", HudSource, StringComparison.Ordinal);
        Assert.DoesNotContain("COLOR.a <=", HudSource, StringComparison.Ordinal);
        foreach (string group in new[] { "Base", "Glow", "Text" })
        {
            Assert.Matches($@"(?s)\[node name=""{group}""[^\]]*\][^\[]*material = SubResource\(""Material_{group.ToLowerInvariant()}""\)", SceneSource);
        }
        Assert.Matches(@"(?s)\[sub_resource type=""ShaderMaterial"" id=""Material_base""\]\s*shader = SubResource\(""Shader_mix""\)", SceneSource);
        Assert.Matches(@"(?s)\[sub_resource type=""ShaderMaterial"" id=""Material_text""\]\s*shader = SubResource\(""Shader_mix""\)", SceneSource);
        Assert.Matches(@"(?s)\[sub_resource type=""ShaderMaterial"" id=""Material_glow""\]\s*shader = SubResource\(""Shader_add""\)", SceneSource);
        Assert.Single(Regex.Matches(SceneSource, @"render_mode\s+blend_mix,\s*unshaded"));
        Assert.Single(Regex.Matches(SceneSource, @"render_mode\s+blend_add,\s*unshaded"));
    }

    [Fact]
    public void DamageFlashUsesTheReleasedAdditiveRgbFadeAndCompassGeometry()
    {
        int start = GlowSource.IndexOf("for flash: Dictionary in hud.damage_flashes:", StringComparison.Ordinal);
        int end = GlowSource.IndexOf("\n\tgauge_needle(", start, StringComparison.Ordinal);
        Assert.True(start >= 0 && end > start);
        string method = GlowSource[start..end];
        Assert.Contains("state.damage_flash_lifetime_ticks", method, StringComparison.Ordinal);
        Assert.Contains("* 96.0", method, StringComparison.Ordinal);
        Assert.Contains("Vector2(128, 32)", method, StringComparison.Ordinal);
        Assert.Contains("Color(fade, fade, fade, 1)", method, StringComparison.Ordinal);
        Assert.DoesNotContain("Color(1, 1, 1, alpha)", method, StringComparison.Ordinal);
        Assert.Contains("SimulationConstants.Level100DamageFlashLifetimeTicks", Read("FirstFlightHud.cs"), StringComparison.Ordinal);
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
        Assert.Contains("CIRCLE_DARKENER_ALPHA: float = 127.0 / 255.0", HudSource, StringComparison.Ordinal);
        Assert.DoesNotContain("1f, 1f, 1f, 0.76f", HudSource, StringComparison.Ordinal);

        // 0x40ffffff, issued six times under SRCALPHA/INVSRCALPHA with
        // ZWRITEENABLE=0, so every draw passes: 1 - (1 - 64/255)^6.
        Assert.Contains("PORTRAIT_DRAW_COUNT: int = 6", HudSource, StringComparison.Ordinal);
        Assert.Contains("PORTRAIT_DRAW_ALPHA: float = 64.0 / 255.0", HudSource, StringComparison.Ordinal);
        double composite = 1.0 - Math.Pow(1.0 - (64.0 / 255.0), 6);
        Match declared = Regex.Match(
            HudSource, @"PORTRAIT_COMPOSITE_ALPHA:\s*float\s*=\s*([0-9.]+)");
        Assert.True(declared.Success, "PortraitCompositeAlpha is missing from the HUD.");
        Assert.Equal(
            composite,
            double.Parse(declared.Groups[1].Value, System.Globalization.CultureInfo.InvariantCulture),
            3);

        // The message-noise diffuse alpha byte over 66 steady-state frames of one
        // message ranged 0x3c..0x4a, mean 66.2.
        Assert.Contains("MESSAGE_NOISE_ALPHA: float = 66.0 / 255.0", HudSource, StringComparison.Ordinal);
        Assert.InRange(66f / 255f, 0x3c / 255f, 0x4a / 255f);
    }

    /// <summary>
    /// Pins the compass base ring to the texel that was read out of the running
    /// game, so a later "the ring looks a bit flat, warm it up" pass has to argue
    /// with a locked texture surface rather than with a taste judgement.
    ///
    /// Ring 1 - 50 segments, radius percent 31 - is textured by
    /// CDXCompass__BuildByteSpriteOverlayTexture (0x0053c2e0) into a 512x32
    /// A4R4G4B4 surface. All 32 rows were dumped whole at two positions of the
    /// Level 100 TTD trace (G:\bea-ttd\play-level100\q-texels\cdb.log), read at
    /// the UnlockRect instruction through LockRect's own pBits. The entire ink
    /// is ONE value, 0x2444, on five rows, identical at both positions; and the
    /// pristine specimen writes the whole four-entry palette as immediates at
    /// 0x0053c312..0x0053c327 - 0x0000, 0x2222, 0x2444, 0x2666 - every one of
    /// them achromatic. Two independent routes, one value.
    ///
    /// Nothing can tint it: FVF 0x102 has no D3DFVF_DIFFUSE so diffuse is opaque
    /// white, and at the ring-1 DrawPrimitive the stage is
    /// MODULATE(TEXTURE, DIFFUSE) under ONE/INVSRCALPHA. So the law is
    /// out = texel.rgb + (1 - texel.a) * bg, and this test recomputes both sides
    /// of it from the raw nibbles.
    ///
    /// Full recovery, including the six-row offset that is still open and is why
    /// the 95/101 radii were NOT touched:
    /// local-lab/HUD-LANE-RECOVERED-2026-07-29.md.
    /// </summary>
    [Fact]
    public void TheCompassBaseRingIsTheAchromaticTapeTexelDrawnAsOneStrip()
    {
        // 0x2444 decoded from its nibbles, not from a transcribed decimal.
        const int Texel = 0x2444;
        double alpha = ((Texel >> 12) & 0xf) / 15.0;
        double red = ((Texel >> 8) & 0xf) / 15.0;
        double green = ((Texel >> 4) & 0xf) / 15.0;
        double blue = (Texel & 0xf) / 15.0;

        // The whole point: retail's base ring has no hue at all.
        Assert.Equal(red, green);
        Assert.Equal(green, blue);

        // The file must carry the texel itself, so the two halves of the one
        // premultiplied draw are derived rather than fitted.
        Assert.Contains(
            "COMPASS_BASE_RING_TEXEL_ALPHA: float = 2.0 / 15.0", HudSource, StringComparison.Ordinal);
        Assert.Contains(
            "COMPASS_BASE_RING_TEXEL_PREMULTIPLIED_RGB: float = 4.0 / 15.0",
            HudSource,
            StringComparison.Ordinal);
        Assert.Equal(2.0 / 15.0, alpha, 6);
        Assert.Equal(4.0 / 15.0, red, 6);

        // Godot blends per CanvasItem, so the single premultiplied draw is an
        // alpha-blended half plus an additive half: (1-a)bg + aK + K, which
        // equals (1-a)bg + P exactly when K = P/(1+a). Same identity the gauge
        // arcs already use.
        Assert.Contains(
            "f(COMPASS_BASE_RING_TEXEL_PREMULTIPLIED_RGB) / f(1.0 + f(COMPASS_BASE_RING_TEXEL_ALPHA))",
            HudSource,
            StringComparison.Ordinal);
        double paint = red / (1.0 + alpha);
        Assert.Equal((1.0 - alpha) + ((1.0 + alpha) * paint), (1.0 - alpha) + red, 6);

        // The blue the ring used to carry must be gone from the file entirely -
        // both from CompassBaseColor and from the additive half that duplicated
        // its literal.
        Assert.DoesNotContain(
            "0.42f + compassHighlight, 0.58f, 0.90f", HudSource, StringComparison.Ordinal);
        Assert.Single(Regex.Matches(HudSource, @"func compass_color\(\)"));
        Assert.Equal(
            2,
            Regex.Matches(HudSource, @"(?<!func )compass_color\(\)").Count);

        // And the ring stays one primitive: retail issues 102 vertices as a
        // single D3DPT_TRIANGLESTRIP, so the helper must not go back to emitting
        // one antialiased DrawLine per segment.
        Assert.Contains("draw_polyline(points, color, width, true)", HudSource, StringComparison.Ordinal);
        Assert.DoesNotContain("DrawLine(firstPoint, secondPoint", HudSource, StringComparison.Ordinal);
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
        Assert.DoesNotContain("noise_phases", GlowSource, StringComparison.Ordinal);
        Assert.Contains("assets.noise_phases", BaseSource, StringComparison.Ordinal);
        Assert.DoesNotContain("Color(0.48, 0.66, 1", HudSource, StringComparison.Ordinal);
        Assert.Contains("pixel.a = F32.value(1.0 - mask.get_pixel(x, y).a)", HudSource, StringComparison.Ordinal);
        Assert.Contains("MESSAGE_NOISE_ALPHA", BaseSource, StringComparison.Ordinal);
    }
}
