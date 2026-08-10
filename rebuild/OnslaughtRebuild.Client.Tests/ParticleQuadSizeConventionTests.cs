// SPDX-License-Identifier: GPL-3.0-or-later

using System.Text.RegularExpressions;
using OnslaughtRebuild.Client;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// <b>How an authored <c>Radius</c> becomes a billboard quad, settled once for
/// every effect (task #151).</b>
///
/// <para>The particle system is absent from the GPL drop - no
/// <c>Particle.cpp</c>, no <c>ParticleManager.h</c>, no sprite-renderer
/// implementation, only call sites - so the conversion cannot be ported and had
/// to be measured. It was, and the measurement is unusually direct: retail's own
/// draw-call vertex positions, which need no camera parameters and no pixel
/// fitting.</para>
///
/// <para>#151 was filed on the belief that the sun used <c>2 * Radius</c> while
/// every older effect used <c>Radius</c>, so one of them had to be wrong. That
/// belief was itself wrong, and these tests exist so it cannot be re-formed:
/// the older sites were already drawing <c>2 * Radius</c>, they simply spelled
/// it as a pre-doubled literal (<c>3f</c> for a <c>Radius 1.5</c> record) with
/// nothing tying it back to the shipped file. There is now one owner,
/// <see cref="ParticleEffectResolver.BillboardQuadSide(float)"/>, and every call
/// site passes the authored number.</para>
/// </summary>
public sealed class ParticleQuadSizeConventionTests
{
    private const string MainSetRelativePath =
        "rebuild/OnslaughtRebuild.Godot/Assets/Level100/ParticleSets/MainSet.par";

    /// <summary>
    /// <b>MEASURED 2026-07-31</b> from the d3d9 proxy's recorded vertex
    /// positions for the retail sun billboard - the only single-quad
    /// <c>fvf=0x142</c> draw in the frame, additive <c>ONE/ONE</c>, 128x128
    /// DXT1, vertex diffuse <c>0x00808080</c>.
    ///
    /// <para>The four edges read 0.20009, 0.19998, 0.20003 and 0.20004 world
    /// units, and the figure is bit-identical across nine logged frames from
    /// three independent launches:
    /// <c>G:\bea-d3d9-capture\B1-level100-f1400-20260727-205715</c> draw 1130,
    /// <c>B2-level100-f1860-20260727-205923</c> draw 1123 and
    /// <c>B3-level100-f2600-20260727-210011</c> draw 1123. The bounds below are
    /// the extreme edge readings, so they carry the instrument's own spread
    /// rather than a tolerance chosen to make the test pass.</para>
    /// </summary>
    private const double MeasuredRetailSunQuadSideLow = 0.19998;

    private const double MeasuredRetailSunQuadSideHigh = 0.20009;

    /// <summary>
    /// The half-extent reading predicts the measured retail quad exactly, and
    /// the full-extent reading is out by a factor of two.
    ///
    /// <para>This is the load-bearing assertion of the whole convention. It
    /// compares two world-space lengths, so unlike task #148's frame fit it
    /// depends on no camera parameter, no field of view and no pixel
    /// registration.</para>
    /// </summary>
    [Fact]
    public void TheAuthoredRadiusIsHalfTheQuadSideRetailDraws()
    {
        ParticleSpriteLayer sun = ResolveSingleLayer("Sun Sprite");
        Assert.Equal(0.1f, sun.StartRadius);

        double asHalfExtent = ParticleEffectResolver.BillboardQuadSide(sun.StartRadius);
        Assert.InRange(
            asHalfExtent,
            MeasuredRetailSunQuadSideLow,
            MeasuredRetailSunQuadSideHigh);

        // The competing reading: Radius as the full quad side. Retail's own
        // geometry refutes it - it predicts 0.1 against a measured 0.2.
        Assert.False(
            sun.StartRadius >= MeasuredRetailSunQuadSideLow &&
            sun.StartRadius <= MeasuredRetailSunQuadSideHigh,
            $"Radius-as-full-extent predicts a {sun.StartRadius:F5} quad side, which the " +
            "measured retail draw call was supposed to refute.");
    }

    /// <summary>
    /// The two instruments agree. Task #148 fitted the flare's on-screen half
    /// extent at 65-69 px off a retail frame; the draw-call geometry measured
    /// here says the world quad is 0.2 units at a known depth. Projecting the
    /// second must land inside the first, and it does.
    ///
    /// <para>Neither measurement was derived from the other - one is a pixel
    /// residual over a captured frame, the other is a vertex buffer - so their
    /// agreement is a genuine cross-check rather than a restatement. It is also
    /// far closer than it had to be: the draw-call geometry projects to
    /// 68.97-69.00 px against a fitted band whose upper bound is 69.</para>
    ///
    /// <para>#148's band endpoints are whole pixels, so the comparison is made
    /// to half-pixel tolerance. Nothing near that tolerance is load-bearing -
    /// the refuted full-extent reading projects to 34.5 px, which misses by
    /// 30 px.</para>
    /// </summary>
    [Fact]
    public void TheDrawCallGeometryAgreesWithTheFrameMeasurement()
    {
        // Placement law, references/Onslaught/DXEngine.cpp:1043-1064, over a
        // Level 100 SunPos of unit length. #148's measured off-axis fraction.
        const double distanceFromEye = 0.6;
        const double depth = distanceFromEye * 0.77329;
        const double focalPixels = (480 / 2) / 0.75;
        const double fitQuantization = 0.5;

        double halfExtentPixelsLow = (MeasuredRetailSunQuadSideLow / 2) / depth * focalPixels;
        double halfExtentPixelsHigh = (MeasuredRetailSunQuadSideHigh / 2) / depth * focalPixels;

        // #148's fitted band, established independently on pixels.
        Assert.InRange(halfExtentPixelsLow, 65 - fitQuantization, 69 + fitQuantization);
        Assert.InRange(halfExtentPixelsHigh, 65 - fitQuantization, 69 + fitQuantization);

        // And the full-extent reading is nowhere near it, by 30 px.
        double refutedHalfExtentPixels = (MeasuredRetailSunQuadSideHigh / 4) / depth * focalPixels;
        Assert.True(
            refutedHalfExtentPixels < 65 - fitQuantization,
            $"Radius-as-full-extent projects to {refutedHalfExtentPixels:F1} px, which #148's " +
            "frame fit was supposed to refute.");
    }

    /// <summary>
    /// Every billboard the world view builds takes an authored radius through
    /// the one owner, and each of those radii is the <c>Radius</c> the named
    /// shipped record actually carries.
    ///
    /// <para>This is what makes the convention uniform rather than a claim about
    /// one sprite. It fails if a literal is pre-doubled again, if a size is
    /// invented, or if a new sprite is added whose number is not in the file.
    /// </para>
    /// </summary>
    [Fact]
    public void EveryEffectSpriteSizeIsAnAuthoredRadiusFromTheShippedSet()
    {
        // The shipped record each construction site draws, established by
        // matching Radius, Final_Radius, Life, End_Frame, Random_Start_Frame and
        // Texture_Size against the animation each site already reproduces.
        var expected = new Dictionary<string, string>(StringComparer.Ordinal)
        {
            ["BlueAnimatedBlob"] = "Blue Anim Blob Large Sprite",
            ["FlashMedium"] = "Flash Medium",
            ["ExplosionAnimatedSprite"] = "Explosion Anim Sprite Medium",
            ["ExplosionFireball"] = "Fire Sprite Damped 2",
            ["FacilityFlash"] = "Flash Building",
            ["PulseCannonMuzzleFlash"] = "Pulse Cannon Muzzle Flash",
        };

        string source = ReadGodotSource("FirstFlightWorldView.cs");
        Assert.Matches(
            @"case\s+Level100DestructionEffectKind\.FacilityDestroyed:\s*" +
            @"SpawnFacilityDestruction\(position,\s*item\.ActorId\);\s*break;",
            source);
        Assert.Matches(
            @"(?s)private void SpawnFacilityDestruction\(Vector3 position, int facilityId\).*?" +
            @"CreateTimedEffect\(\s*\$""FacilityDestruction\{facilityId\}"",\s*position,\s*0\.3d\).*?" +
            @"CreateEffectSprite\(\s*""FacilityFlash"",\s*_effectFlashMediumTexture,\s*3f\).*?" +
            @"AnimateScale\(flash,\s*1f,\s*0f,\s*0\.3d\);",
            source);

        // The owner is used, and the raw multiplication is not re-inlined.
        Assert.Contains(
            "ParticleEffectResolver.BillboardQuadSide(authoredRadius)",
            source,
            StringComparison.Ordinal);

        ParticleSetFile set = ParticleSetFile.Parse(File.ReadAllBytes(Locate(MainSetRelativePath)));

        MatchCollection sites = Regex.Matches(
            source,
            @"CreateEffectSprite\(\s*""(?<name>[A-Za-z0-9]+)"",\s*\S+,\s*(?<radius>[0-9]*\.?[0-9]+)f",
            RegexOptions.None,
            TimeSpan.FromSeconds(5));

        Assert.Equal(expected.Count, sites.Count);

        foreach (Match site in sites)
        {
            string name = site.Groups["name"].Value;
            float coded = float.Parse(
                site.Groups["radius"].Value,
                System.Globalization.CultureInfo.InvariantCulture);

            Assert.True(
                expected.TryGetValue(name, out string? descriptorName),
                $"Effect sprite '{name}' has no recorded shipped descriptor. Identify the " +
                "record it draws before giving it a size.");

            (float authored, _) = set.Require(descriptorName!).FloatWithModifier("Radius");
            Assert.Equal(authored, coded);
        }
    }

    /// <summary>
    /// The owner is a doubling and nothing else. Guards the case where the
    /// constant is left at 2 but the method stops using it.
    /// </summary>
    [Fact]
    public void TheOwnerAppliesTheMeasuredFactor()
    {
        Assert.Equal(2f, ParticleEffectResolver.AuthoredRadiusIsHalfTheQuadSide);
        Assert.Equal(3f, ParticleEffectResolver.BillboardQuadSide(1.5f));
        Assert.Equal(0f, ParticleEffectResolver.BillboardQuadSide(0f));
    }

    private static ParticleSpriteLayer ResolveSingleLayer(string effectName)
    {
        ParticleSetFile set = ParticleSetFile.Parse(File.ReadAllBytes(Locate(MainSetRelativePath)));
        return Assert.Single(ParticleEffectResolver.Resolve(set, effectName).Layers);
    }

    private static string ReadGodotSource(string fileName)
    {
        string path = Path.Combine(AppContext.BaseDirectory, "godot-effects-source", fileName);
        Assert.True(File.Exists(path), $"Source was not copied to the test output: {path}");
        return File.ReadAllText(path);
    }

    private static string Locate(string repositoryRelativePath)
    {
        DirectoryInfo? directory = new(AppContext.BaseDirectory);
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
