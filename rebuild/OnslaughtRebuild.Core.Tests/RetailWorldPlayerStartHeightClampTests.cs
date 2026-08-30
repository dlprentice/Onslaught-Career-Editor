// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Core.Tests;

public sealed class RetailWorldPlayerStartHeightClampTests
{
    [Fact]
    public void Apply_ExactWorld110StartClampsToTheSecondRetailTerrainSample()
    {
        RetailWorldPlayerStartResolution resolution = ExactProjection()
            .ResolveForPlayer(1);

        RetailWorldPlayerStartHeightClampResult result =
            RetailWorldPlayerStartHeightClamp.Apply(
                resolution,
                Level100Terrain.World110);

        Assert.Same(resolution, result.Resolution);
        Assert.Equal(
            Level100Terrain.World110SourceSha256,
            result.TerrainPayloadSha256);
        Assert.Equal(15, result.ThingType);
        Assert.Equal(0x43846000, result.PositionXBits);
        Assert.Equal(0x43816800, result.PositionYBits);
        Assert.Equal(unchecked((int)0x80000000), result.SerializedPositionZBits);
        Assert.Equal(67_776, result.PositionXFixed);
        Assert.Equal(66_256, result.PositionYFixed);
        Assert.Equal(unchecked((int)0xc1199926), result.FinalPositionZBits);
        Assert.Equal(0, result.PlaneMode);
        Assert.Equal(1, result.PlayerNumber);
        Assert.True(result.HeightWasClamped);

        RetailWorldPlayerStartRecord authored = Assert.IsType<RetailWorldPlayerStartRecord>(
            result.AuthoredStart);
        Assert.Same(resolution.AuthoredStart, authored);
        Assert.Equal("wres:rlwd:0001", result.AuthoredObjectIdentity);
        Assert.Equal(unchecked((int)0xbf04fd8b), result.OrientationXBits);
        Assert.Equal(0, result.OrientationYBits);
        Assert.Equal(0, result.OrientationZBits);

        Assert.Equal(2, result.SampleCallCount);
        Assert.Collection(
            result.Samples,
            first => AssertExactWorld110Sample(first, callOrdinal: 1),
            second => AssertExactWorld110Sample(second, callOrdinal: 2));
        Assert.Equal(
            -9.599889755249023f,
            BitConverter.Int32BitsToSingle(result.FinalPositionZBits));
    }

    [Fact]
    public void Apply_EqualHeightDoesNotTakeTheStrictClampArm()
    {
        RetailWorldPlayerStartRecord equalZero = ExactStart() with
        {
            PositionXBits = BitConverter.SingleToInt32Bits(512f),
            PositionYBits = BitConverter.SingleToInt32Bits(512f),
            PositionZBits = 0,
        };
        RetailWorldPlayerStartResolution resolution =
            RetailWorldPlayerStartResolution.FromAuthored(equalZero);
        var calls = new List<(int X, int Y)>();

        int SampleEqualZero(int x, int y)
        {
            calls.Add((x, y));
            return 0;
        }

        RetailWorldPlayerStartHeightClampResult result =
            RetailWorldPlayerStartHeightClamp.Apply(
                resolution,
                Level100Terrain.World110,
                SampleEqualZero);

        Assert.False(result.HeightWasClamped);
        Assert.Equal(0, result.FinalPositionZBits);
        Assert.Equal([(131_072, 131_072)], calls);
        RetailWorldPlayerStartHeightSample sample = Assert.Single(result.Samples);
        Assert.Equal(1, sample.CallOrdinal);
        Assert.Equal(0, sample.HeightUnits);
        Assert.Equal(0, sample.HeightBits);
    }

    [Fact]
    public void Apply_ClampArmSamplesTwiceAndStoresTheSecondDistinctResult()
    {
        RetailWorldPlayerStartResolution resolution = ExactProjection()
            .ResolveForPlayer(1);
        var calls = new List<(int X, int Y)>();
        int[] returnedHeightUnits = [-10_485, -9_000];

        int SampleDistinctHeights(int x, int y)
        {
            calls.Add((x, y));
            return returnedHeightUnits[calls.Count - 1];
        }

        RetailWorldPlayerStartHeightClampResult result =
            RetailWorldPlayerStartHeightClamp.Apply(
                resolution,
                Level100Terrain.World110,
                SampleDistinctHeights);

        Assert.True(result.HeightWasClamped);
        Assert.Equal(
            [(67_776, 66_256), (67_776, 66_256)],
            calls);
        Assert.Collection(
            result.Samples,
            first =>
            {
                Assert.Equal(1, first.CallOrdinal);
                Assert.Equal(-10_485, first.HeightUnits);
            },
            second =>
            {
                Assert.Equal(2, second.CallOrdinal);
                Assert.Equal(-9_000, second.HeightUnits);
            });
        Assert.NotEqual(result.Samples[0].HeightBits, result.Samples[1].HeightBits);
        Assert.Equal(result.Samples[1].HeightBits, result.FinalPositionZBits);
    }

    [Fact]
    public void Apply_UnmatchedPlayerUsesFallbackXYWithoutInventingOrientation()
    {
        RetailWorldPlayerStartResolution fallback = ExactProjection()
            .ResolveForPlayer(2);

        RetailWorldPlayerStartHeightClampResult result =
            RetailWorldPlayerStartHeightClamp.Apply(
                fallback,
                Level100Terrain.World110);

        Assert.Same(fallback, result.Resolution);
        Assert.Equal(0x43800000, result.PositionXBits);
        Assert.Equal(0x43800000, result.PositionYBits);
        Assert.Equal(0, result.SerializedPositionZBits);
        Assert.Equal(65_536, result.PositionXFixed);
        Assert.Equal(65_536, result.PositionYFixed);
        Assert.Equal(unchecked((int)0xc1199926), result.FinalPositionZBits);
        Assert.Equal(2, result.PlayerNumber);
        Assert.Equal(0, result.PlaneMode);
        Assert.True(result.HeightWasClamped);
        Assert.Null(result.AuthoredStart);
        Assert.Null(result.AuthoredObjectIdentity);
        Assert.Null(result.OrientationXBits);
        Assert.Null(result.OrientationYBits);
        Assert.Null(result.OrientationZBits);

        Assert.Equal(2, result.SampleCallCount);
        Assert.All(result.Samples, sample =>
        {
            Assert.Equal(-10_485, sample.HeightUnits);
            Assert.Equal(0x3a7003c0, sample.HeightScaleBits);
            Assert.Equal(unchecked((int)0xc1199926), sample.HeightBits);
        });
    }

    [Fact]
    public void Apply_RejectsAHeightfieldOtherThanThePinnedWorld110Payload()
    {
        ArgumentException error = Assert.Throws<ArgumentException>(() =>
            RetailWorldPlayerStartHeightClamp.Apply(
                ExactProjection().ResolveForPlayer(1),
                Level100Terrain.Instance));

        Assert.Equal("terrain", error.ParamName);
    }

    [Fact]
    public void Apply_ProducesAnImmutableSampleTranscript()
    {
        RetailWorldPlayerStartHeightClampResult result =
            RetailWorldPlayerStartHeightClamp.Apply(
                ExactProjection().ResolveForPlayer(1),
                Level100Terrain.World110);

        Assert.Throws<NotSupportedException>(() =>
            ((IList<RetailWorldPlayerStartHeightSample>)result.Samples).Add(
                result.Samples[0]));
    }

    [Fact]
    public void Apply_RejectsNullInputs()
    {
        Assert.Throws<ArgumentNullException>(() =>
            RetailWorldPlayerStartHeightClamp.Apply(
                null!,
                Level100Terrain.World110));
        Assert.Throws<ArgumentNullException>(() =>
            RetailWorldPlayerStartHeightClamp.Apply(
                ExactProjection().ResolveForPlayer(1),
                null!));
        Assert.Throws<ArgumentNullException>(() =>
            RetailWorldPlayerStartHeightClamp.Apply(
                ExactProjection().ResolveForPlayer(1),
                Level100Terrain.World110,
                null!));
    }

    private static void AssertExactWorld110Sample(
        RetailWorldPlayerStartHeightSample sample,
        int callOrdinal)
    {
        Assert.Equal(callOrdinal, sample.CallOrdinal);
        Assert.Equal(67_776, sample.PositionXFixed);
        Assert.Equal(66_256, sample.PositionYFixed);
        Assert.Equal(-10_485, sample.HeightUnits);
        Assert.Equal(0x3a7003c0, sample.HeightScaleBits);
        Assert.Equal(unchecked((int)0xc1199926), sample.HeightBits);
    }

    private static RetailWorldPlayerStartRecord ExactStart() =>
        Assert.Single(RetailWorld110LevelActors.AuthoredPlayerStarts);

    private static RetailWorldPlayerStartProjection ExactProjection() =>
        RetailWorldPlayerStartAdmission.Admit(
            RetailWorld110LevelActors.WorldNumber,
            RetailWorld110LevelActors.ArchiveIdentity,
            RetailWorld110LevelActors.AuthoredPlayerStarts);
}
