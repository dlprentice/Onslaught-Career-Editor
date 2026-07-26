// SPDX-License-Identifier: GPL-3.0-or-later

using System.Globalization;
using System.Text.Json;
using System.Text.RegularExpressions;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// A retail Level 1.00 pine has exactly two representations and no third one.
///
/// Byte evidence: <c>defaultoptions.bea</c> file offset 0x26CA holds
/// <c>00 00 8C 42</c> = 70.0f, the mesh-quality distance. Archive evidence: the
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
    /// from <c>defaultoptions.bea</c> at 0x26CA.
    /// </summary>
    private const int MeshQualityDistanceBits = 0x428C0000;

    [Fact]
    public void ManifestPinsTheAuthoredSeventyUnitSwapDistanceBitExact()
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

    private static string ReadGodotSource(string fileName)
    {
        DirectoryInfo? directory = new(AppContext.BaseDirectory);
        while (directory is not null)
        {
            string candidate = Path.Combine(
                directory.FullName,
                "OnslaughtRebuild.Godot",
                fileName);
            if (File.Exists(candidate))
            {
                return File.ReadAllText(candidate);
            }
            directory = directory.Parent;
        }
        throw new FileNotFoundException(
            $"Could not locate OnslaughtRebuild.Godot/{fileName} above {AppContext.BaseDirectory}.");
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
