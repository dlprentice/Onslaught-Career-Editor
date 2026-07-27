// SPDX-License-Identifier: GPL-3.0-or-later

using System.Globalization;
using System.Text.Json;
using System.Text.RegularExpressions;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// A retail Level 1.00 pine has exactly two representations and no third one.
///
/// <para><b>WARNING, 2026-07-27: 70.0 IS NOT AN AUTHORED CONSTANT. It is this
/// machine's graphics setting.</b> <c>defaultoptions.bea</c> file offset 0x26CA
/// holds <c>00 00 8C 42</c> = 70.0f — but <c>proof_defaultoptions.bea</c>, in the
/// same install, holds <c>00 00 F0 41</c> = <b>30.0f</b> at the identical offset.
/// Measured directly. That file is RUN STATE, not shipped defaults: it is absent
/// from <c>INSTALL.LOG</c>'s CopyFiles list and the game rewrites it.
///
/// The field is the <b>Geometry detail</b> options row. Its setter at
/// <c>0x004dd6b0</c> has exactly three arms — <c>10 / 30 / 70</c> — and the
/// executable's own static initialisers are the MIDDLE arm, so the released
/// default is <b>30.0 (Medium)</b> and 70.0 is High.
///
/// So the swap distance below is pinned to whatever this workstation last chose,
/// and the reconstruction may be drawing full pine meshes 2.3x further out than
/// a default retail install does. THE VALUE IS DELIBERATELY LEFT AT 70.0 HERE
/// rather than changed to 30.0, because changing it alters what is rendered and
/// must be settled by measurement against a retail capture, not by swapping one
/// unverified constant for another. Tracked separately.
///
/// What these tests still prove, and it is worth keeping: every pine
/// representation the reconstruction draws is GATED on one distance, so no pass
/// can survive at all distances. That structural claim is independent of which
/// number the gate holds.</para>
///
/// Archive evidence for the representation count, unaffected by the above: the
/// level's IMPS/IMPT/VIEW chunk stores exactly six views per pine variant, each
/// a 32x32 atlas cell plus two floats, and those float pairs are the variant's
/// own mesh bounding-box half-extents scaled by exactly 1.05 on all three axes
/// (views 0/2 = X by Z, 1/3 = Y by Z, 4/5 = X by Y). That is the six faces of
/// the mesh's own bounding box, not a camera-facing card: a billboard needs one
/// view and one size pair and would never carry a top-down disc.
///
/// These tests pin the 70.0 swap and prove that every pine representation the
/// reconstruction draws is gated on it, so no pass can survive at all distances.
/// </summary>
public sealed class Level100PineRepresentationTests
{
    private static readonly string StaticWorldSource = ReadGodotSource(
        "Level100StaticWorldAsset.cs");

    /// <summary>
    /// 70.0f is exactly <c>00 00 8C 42</c> little-endian, the four bytes read
    /// from <c>defaultoptions.bea</c> at 0x26CA — which is this machine's
    /// Geometry detail setting (High), NOT a shipped default. See the class
    /// remarks: the released default is 30.0 (Medium).
    /// </summary>
    private const int MeshQualityDistanceBits = 0x428C0000;

    [Fact]
    public void ManifestPinsTheCurrentSwapDistanceBitExact()
    {
        JsonElement billboards = LoadManifest().GetProperty("pineBillboards");

        float distance = billboards.GetProperty("meshQualityDistance").GetSingle();

        Assert.Equal(MeshQualityDistanceBits, BitConverter.SingleToInt32Bits(distance));
        Assert.Equal(
            new byte[] { 0x00, 0x00, 0x8C, 0x42 },
            BitConverter.GetBytes(distance));
        Assert.Equal(70f, distance);
    }

    [Fact]
    public void EverySourceMeshQualityDistanceIsTheSameSeventyUnitValue()
    {
        // The close mesh and the far box must gate on one shared value, or a
        // band opens where both discard and the tree disappears.
        MatchCollection matches = Regex.Matches(
            StaticWorldSource,
            @"SingleToInt32Bits\(\s*(\d+(?:\.\d+)?)f\s*\)");

        Assert.Contains(
            matches.Cast<Match>(),
            match => BitConverter.SingleToInt32Bits(
                float.Parse(match.Groups[1].Value, CultureInfo.InvariantCulture)) ==
                MeshQualityDistanceBits);
    }

    [Fact]
    public void PineImposterMaterialsCannotBeCreatedWithoutADistanceGate()
    {
        // `meshQualityDistance: null` was what made the removed fast card
        // ungated: it selected an unbounded shader and RenderPriority 1, so the
        // card drew over the mesh at every distance. The parameter is no longer
        // nullable and the factory rejects a non-positive distance.
        Assert.DoesNotContain("meshQualityDistance: null", StaticWorldSource);
        Assert.DoesNotContain("double? meshQualityDistance", StaticWorldSource);
        Assert.Contains(
            "double meshQualityDistance)",
            StaticWorldSource);
        Assert.Contains(
            "mesh-quality distance.\");",
            StaticWorldSource);
        Assert.Contains(
            @"material.SetShaderParameter(""mesh_distance_squared"", distance * distance);",
            StaticWorldSource);
    }

    [Fact]
    public void OnlyTwoPineRepresentationsAreEverAddedToTheWorld()
    {
        // AddPines is the single call site that builds pine geometry.
        string body = Between(
            StaticWorldSource,
            "private static int AddPines(",
            "private static PinePlacement[] BuildPinePlacements(");

        Assert.Contains("AddClosePineMeshes(", body);
        Assert.Contains("AddFarPineImposters(", body);
        Assert.DoesNotContain("AddFastPineImposters", StaticWorldSource);
        Assert.DoesNotContain("PineFastImposterRoot", StaticWorldSource);
        Assert.DoesNotContain("PineFastImposterShaderCode", StaticWorldSource);
        Assert.DoesNotContain("camera_facing", StaticWorldSource);
    }

    [Fact]
    public void TheTwoPineShaderGatesAreComplementaryAboutTheSameDistance()
    {
        // Mesh material discards beyond the distance; the box discards at or
        // inside it. Complementary, hard, no fade — matching the byte-authored
        // hard swap with no cross-dissolve anywhere in the data or shaders.
        Assert.Contains(
            "horizontal_distance_squared > maximum_horizontal_distance_squared",
            StaticWorldSource);
        Assert.Contains(
            "horizontal_distance_squared <= mesh_distance_squared",
            StaticWorldSource);
        Assert.DoesNotContain("smoothstep", StaticWorldSource);
        Assert.DoesNotContain("RenderPriority = far", StaticWorldSource);
    }

    [Fact]
    public void NoPineGeometryIsAddedOutsideAShaderGatedMultiMesh()
    {
        // Any MultiMeshInstance3D named for pines must belong to one of the two
        // gated passes. A third batch would show up here.
        string[] names = Regex.Matches(
                StaticWorldSource,
                @"Name = \$""(RetailPine[A-Za-z0-9{}]*)""")
            .Cast<Match>()
            .Select(match => match.Groups[1].Value)
            .ToArray();

        Assert.Equal(
            [
                "RetailPineSnow{variant}CloseMeshInstances",
                "RetailPineSnow{variant}FarSixFaceInstances",
            ],
            names.Order(StringComparer.Ordinal));
    }

    [Fact]
    public void TheFarBoxSitsOnTheSameTransformAsTheCloseMesh()
    {
        // The stored VIEW half-extents are the mesh bounding box scaled 1.05 and
        // centerOffset is that bounding box centre, so the box only describes
        // the tree when it shares the mesh's origin. Both passes must therefore
        // apply the same baseClearance lift.
        Assert.Equal(
            2,
            Regex.Matches(
                StaticWorldSource,
                @"GroundOrigin \+ \(Vector3\.Up \* baseClearance\)").Count);
    }

    [Theory]
    [InlineData(0, 0.04363)]
    [InlineData(1, 0.02404)]
    [InlineData(2, 0.03370)]
    [InlineData(3, 0.03183)]
    public void GroundingTheFarBoxRemovesTheSwapStepAndLeavesOnlyAuthoredInflation(
        int variant,
        double expectedBaseClearance)
    {
        JsonElement manifest = LoadManifest();
        double baseClearance = manifest
            .GetProperty("meshes")
            .GetProperty($"pinesnow{variant}")
            .GetProperty("baseClearance")
            .GetDouble();
        JsonElement definition = manifest
            .GetProperty("pineBillboards")
            .GetProperty("variants")[variant];

        // Godot Y for the BEA centre offset is -Z.
        double centerHeight = -definition.GetProperty("centerOffset")[2].GetDouble();
        // View 0 is the X-by-Z side elevation, so element 5 is the Z half-extent.
        double halfHeight = definition.GetProperty("views")[0][5].GetDouble();

        Assert.Equal(expectedBaseClearance, baseClearance, 5);

        double bottomWithoutClearance = centerHeight - halfHeight;
        double bottomWithClearance = bottomWithoutClearance + baseClearance;

        // Before: the box hung well below the terrain and stepped at 70 units.
        Assert.True(
            bottomWithoutClearance < -0.06,
            $"variant {variant} ungrounded bottom {bottomWithoutClearance}");
        // After: the only remaining dip is the authored 5 % inflation of the
        // mesh's own bounding box, which is 0.05 * meshHalfHeight by
        // construction and is identical in retail's data.
        double meshHalfHeight = halfHeight / 1.05;
        Assert.Equal(-0.05 * meshHalfHeight, bottomWithClearance, 5);
        Assert.True(
            bottomWithClearance > -0.05,
            $"variant {variant} grounded bottom {bottomWithClearance}");
    }

    [Fact]
    public void EveryVariantStoresSixViewsMatchingItsOwnBoundingBoxAxes()
    {
        // Six views with three distinct size pairs is what rules a billboard
        // out; a camera-facing card needs one view and one pair.
        JsonElement variants = LoadManifest()
            .GetProperty("pineBillboards")
            .GetProperty("variants");

        Assert.Equal(4, variants.GetArrayLength());
        foreach (JsonElement definition in variants.EnumerateArray())
        {
            JsonElement views = definition.GetProperty("views");
            Assert.Equal(6, views.GetArrayLength());
            double x = views[0][4].GetDouble();
            double y = views[1][4].GetDouble();
            double z = views[0][5].GetDouble();

            // 0 and 2 are X by Z, 1 and 3 are Y by Z, 4 and 5 are X by Y.
            Assert.Equal(x, views[2][4].GetDouble(), 5);
            Assert.Equal(z, views[2][5].GetDouble(), 5);
            Assert.Equal(y, views[3][4].GetDouble(), 5);
            Assert.Equal(z, views[1][5].GetDouble(), 5);
            Assert.Equal(x, views[4][4].GetDouble(), 5);
            Assert.Equal(y, views[4][5].GetDouble(), 5);
            Assert.Equal(x, views[5][4].GetDouble(), 5);
            Assert.Equal(y, views[5][5].GetDouble(), 5);
        }
    }

    [Fact]
    public void TheFarBoxDrawsTheCameraFacingFacesOfAClosedSixFaceBox()
    {
        // The six views are the six faces, so all six are built; ordinary
        // culling of a closed box leaves the three facing the camera, which the
        // shader reproduces by discarding faces whose normal points away.
        Assert.Contains("for (int face = 0; face < 6; face++)", StaticWorldSource);
        Assert.Contains("new Vector3[24]", StaticWorldSource);
        Assert.Contains("new int[36]", StaticWorldSource);
        Assert.Contains("face_alignment <= 0.0", StaticWorldSource);
    }

    [Fact]
    public void ImposterSamplingAndColourTransformAreUnchanged()
    {
        // Settled by measurement: the atlas alpha histogram is binary
        // {0: 147423, 255: 114721}, the atlas carries zero mipmaps, its
        // transparent texels are mid-grey (122, 122, 123) so linear filtering
        // would drag every edge grey, and the doubled opaque mean
        // (26.1, 24.5, 31.5) * 2 matches measured retail foliage
        // (50.8, 59.7, 65.4). This test exists to stop a well-meaning "fix".
        Assert.Contains("filter_nearest", StaticWorldSource);
        Assert.DoesNotContain("atlas : filter_linear", StaticWorldSource);
        Assert.Contains("texel.rgb * 2.0", StaticWorldSource);
        Assert.Contains("texel.a < (8.0 / 255.0)", StaticWorldSource);
    }

    /// <summary>
    /// The authored statics are not pines and are seated by a different
    /// released owner. `CThing__Init` @ 0x004F34A0 stores the authored position
    /// at `this+0x1c..+0x28` (Z-down at `+0x24`) and then clamps it twice:
    /// `MOV ECX,0x006FADC8` / `CALL 0x0047EB80` (0x004F34F6, 0x004F34FB) samples
    /// the height field, `FCOM [ESI+0x24]` (0x004F3500) compares, and
    /// `FSTP [ESP+0x14]` (0x004F3529) writes the sampled height into the copy
    /// handed to `CALL [EAX+0x50]`; then `FLD [0x006FBDFC]` (0x004F3549),
    /// `FCOM [ESI+0x24]` and `FSTP [ESI+0x24]` (0x004F3559) do the same with the
    /// water level. Both stores are bare: the mesh bounding box is never read,
    /// so the pivot — not the lowest vertex — lands on the support. These tests
    /// pin that, because a `-min(vertexZ)` lift had been added on top of it and
    /// floated the docks by the exact length of their own pilings.
    /// </summary>
    [Fact]
    public void NoMeshDerivedTermIsAddedToTheReleasedStaticClamp()
    {
        string placement = Between(
            StaticWorldSource,
            "foreach (WorldObject worldObject in manifest.Objects",
            "int pineCount = AddPines(");

        Assert.Contains("relativeHeight,\n                    -relativeZ),", placement.ReplaceLineEndings("\n"));
        Assert.DoesNotContain("verticalClearance", placement);
        Assert.DoesNotContain("BaseClearance", placement);
        // The per-definition suppression only existed to cancel that lift for
        // one object; with the lift gone the general rule covers all 33.
        Assert.DoesNotContain("SatTurretDefinition", placement);
    }

    /// <summary>
    /// The docks are the object that proves the authored Z is an absolute
    /// elevation in the same space as the water plane, not an offset from the
    /// ground: BSWD ordinal 24 is authored at Z-down -8.870770454406738 and
    /// `CHFD + 0x1034` holds -8.84000015258789, so the pivot is authored
    /// 0.0308 above the water surface, while the terrain under it is the flat
    /// sea-floor plateau 10 units below. The authored term therefore wins both
    /// clamps and the pivot must land at the water line.
    /// </summary>
    [Fact]
    public void TheDocksPivotIsTheAuthoredWaterLineAndTheOldLiftWasItsOwnPilings()
    {
        JsonElement manifest = LoadManifest();
        JsonElement docks = manifest
            .GetProperty("objects")
            .EnumerateArray()
            .Single(item => item.GetProperty("ordinal").GetInt32() == 24);
        Assert.Equal("Forseti Docks", docks.GetProperty("definition").GetString());

        double authoredZ = docks.GetProperty("retailPosition")[2].GetDouble();
        double waterZ = Level100Terrain.Instance.WaterLevel;
        Assert.Equal(-8.870770454406738, authoredZ, 9);
        Assert.Equal(0.030770301818847656, waterZ - authoredZ, 9);

        (double authored, double ground, double water) = Supports(docks);
        Assert.Equal(authored, Math.Max(authored, Math.Max(ground, water)), 6);
        // The sea floor here is the flat plateau: raw 1267 * the HFLD scale.
        Assert.Equal(-1.1600439436733723 - 10.0, ground, 6);
        Assert.Equal(0.030770301818847656, authored - water, 9);

        // The lift that used to be added is exactly the piling span this mesh
        // carries below its own origin, which is why the deck hung 3.2 m up and
        // the columns ended above the water.
        double[] vertexZ = MeshVertexZ("fb-docks.obj");
        Assert.Equal(2809, vertexZ.Length);
        Assert.Equal(173, vertexZ.Count(value => value < -0.001));
        Assert.Equal(
            manifest.GetProperty("meshes").GetProperty("FB_Docks")
                .GetProperty("baseClearance").GetDouble(),
            -vertexZ.Min(),
            9);
        Assert.Equal(3.231837272644043, -vertexZ.Min(), 9);
    }

    /// <summary>
    /// The four turrets are the contrast case: they stand on land, so the
    /// ground clamp wins and the pivot must equal the sampled height exactly.
    /// Each turret mesh carries a base collar below its own origin — 56 to 69
    /// vertices reaching 0.222 to 0.228 down — that retail buries. Lifting by
    /// that span is what raised them out of the ground.
    /// </summary>
    [Theory]
    [InlineData(3, "SAT Turret", "ft_sam", "ft-sam.obj", 56, 0.22822660952806473)]
    [InlineData(10, "Blaster Turret", "ft_blaster", "ft-blaster.obj", 69, 0.22263068734901026)]
    [InlineData(11, "Blaster Turret", "ft_blaster", "ft-blaster.obj", 69, 0.22263068734901026)]
    [InlineData(12, "Pulse Turret", "ft_pulse", "ft-pulse.obj", 64, 0.22567694188910536)]
    public void EveryTurretSeatsItsPivotOnTheSampledGroundAndBuriesItsCollar(
        int ordinal,
        string definition,
        string meshKey,
        string meshFile,
        int collarVertexCount,
        double collarDepth)
    {
        JsonElement manifest = LoadManifest();
        JsonElement turret = manifest
            .GetProperty("objects")
            .EnumerateArray()
            .Single(item => item.GetProperty("ordinal").GetInt32() == ordinal);
        Assert.Equal(definition, turret.GetProperty("definition").GetString());
        Assert.Equal(meshKey, turret.GetProperty("mesh").GetString());

        (double authored, double ground, double water) = Supports(turret);
        Assert.Equal(ground, Math.Max(authored, Math.Max(ground, water)), 6);

        double[] vertexZ = MeshVertexZ(meshFile);
        Assert.Equal(collarVertexCount, vertexZ.Count(value => value < -0.001));
        Assert.Equal(collarDepth, -vertexZ.Min(), 9);
        Assert.Equal(
            collarDepth,
            manifest.GetProperty("meshes").GetProperty(meshKey)
                .GetProperty("baseClearance").GetDouble(),
            9);
    }

    /// <summary>
    /// Returns the three clamp supports for one authored object in up-positive
    /// units relative to the player-start reference elevation, exactly as
    /// <c>Level100StaticWorldAsset.Load</c> forms them.
    /// </summary>
    private static (double Authored, double Ground, double Water) Supports(
        JsonElement worldObject)
    {
        const double referenceElevation =
            Level100Terrain.PlayerStartReferenceElevationMillimeters / 1_000.0;
        JsonElement position = worldObject.GetProperty("retailPosition");
        double retailX = position[0].GetDouble();
        double retailY = position[1].GetDouble();
        Level100Terrain terrain = Level100Terrain.Instance;
        int groundUnits = terrain.SampleHeightUnitsAtFixed(
            (int)Math.Floor(retailX * Level100Terrain.FixedPointUnitsPerRetailUnit),
            (int)Math.Floor(retailY * Level100Terrain.FixedPointUnitsPerRetailUnit));
        return (
            referenceElevation - position[2].GetDouble(),
            referenceElevation - (groundUnits * (double)terrain.HeightScale),
            referenceElevation - terrain.WaterLevel);
    }

    private static double[] MeshVertexZ(string meshFile)
    {
        string path = Path.Combine(
            LocateGodotDirectory(),
            "Assets",
            "Level100",
            "StaticWorld",
            "Meshes",
            meshFile);
        Assert.True(File.Exists(path), $"The static-world mesh is missing: {path}");
        return File.ReadLines(path)
            .Where(line => line.StartsWith("v ", StringComparison.Ordinal))
            .Select(line => double.Parse(
                line.Split(' ')[3],
                CultureInfo.InvariantCulture))
            .ToArray();
    }

    private static JsonElement LoadManifest()
    {
        string path = Path.Combine(
            AppContext.BaseDirectory,
            "Assets",
            "Level100",
            "StaticWorld",
            "level100-static-world.json");
        Assert.True(File.Exists(path), $"The static-world manifest is missing: {path}");
        using var document = JsonDocument.Parse(File.ReadAllBytes(path));
        return document.RootElement.Clone();
    }

    private static string ReadGodotSource(string fileName) =>
        File.ReadAllText(Path.Combine(LocateGodotDirectory(), fileName));

    private static string LocateGodotDirectory()
    {
        DirectoryInfo? directory = new(AppContext.BaseDirectory);
        while (directory is not null)
        {
            string candidate = Path.Combine(directory.FullName, "OnslaughtRebuild.Godot");
            if (File.Exists(Path.Combine(candidate, "Level100StaticWorldAsset.cs")))
            {
                return candidate;
            }
            directory = directory.Parent;
        }
        throw new DirectoryNotFoundException(
            $"Could not locate OnslaughtRebuild.Godot above {AppContext.BaseDirectory}.");
    }

    private static string Between(string source, string start, string end)
    {
        int from = source.IndexOf(start, StringComparison.Ordinal);
        Assert.True(from >= 0, $"Source no longer contains '{start}'.");
        int to = source.IndexOf(end, from, StringComparison.Ordinal);
        Assert.True(to > from, $"Source no longer contains '{end}' after '{start}'.");
        return source[from..to];
    }
}
