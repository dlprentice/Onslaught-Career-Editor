// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Core.Tests;

/// <summary>
/// Parity tests for <see cref="RetailJetFriction"/> against
/// <c>references/Onslaught/BattleEngineJetPart.cpp:609-635</c> and the pristine
/// <c>74154bfa…</c> bytes at <c>0x00411AA0</c>.
/// </summary>
public sealed class RetailJetFrictionTests
{
    private const float StationaryComponent = 0.0f;

    // The six .rdata constants the body reads, bit for bit. 0.99f and 0.98f are
    // not representable, so a rebuild that wrote 99/100 in any other form would
    // drift; the bit pattern is the contract.
    [Fact]
    public void Constants_MatchTheReadOnlyDataTheBodyLoads()
    {
        Assert.Equal(
            0x3F7D70A4u,
            BitConverter.SingleToUInt32Bits(RetailJetFriction.NearSurfaceFriction));
        Assert.Equal(
            0x3F7AE148u,
            BitConverter.SingleToUInt32Bits(RetailJetFriction.CruiseFriction));
        Assert.Equal(
            0x3F800000u,
            BitConverter.SingleToUInt32Bits(RetailJetFriction.NearSurfaceAltitude));
        Assert.Equal(
            0x40400000u,
            BitConverter.SingleToUInt32Bits(RetailJetFriction.CruiseAltitude));
        Assert.Equal(
            0x3FC00000u,
            BitConverter.SingleToUInt32Bits(RetailJetFriction.SlowFlightSpeed));
        Assert.Equal(
            0x3C23D70Au,
            BitConverter.SingleToUInt32Bits(RetailJetFriction.AltitudeFrictionRate));
    }

    // The whole ladder against a stationary jet, driven only by altitude. The
    // altitude 1.0 row is the interesting one: the first test is strictly-less,
    // so exactly 1.0 falls through to the interpolated arm - which happens to
    // return the same 0.99f, making the ladder continuous at that seam. The
    // altitude 2.0 row reaches 0.98f bit for bit through the interpolation, not
    // through the cruise arm. 3.0 is the first altitude that is genuinely
    // cruise.
    [Theory]
    [InlineData(0.0f, 0x3F7D70A4u)]
    [InlineData(0.9999f, 0x3F7D70A4u)]
    [InlineData(1.0f, 0x3F7D70A4u)]
    [InlineData(1.25f, 0x3F7CCCCDu)]
    [InlineData(1.5f, 0x3F7C28F6u)]
    [InlineData(2.0f, 0x3F7AE148u)]
    [InlineData(2.9375f, 0x3F787AE1u)]
    [InlineData(3.0f, 0x3F7AE148u)]
    [InlineData(100.0f, 0x3F7AE148u)]
    public void GetFriction_WalksTheAltitudeLadder(float altitude, uint expectedBits) =>
        Assert.Equal(
            expectedBits,
            BitConverter.SingleToUInt32Bits(
                RetailJetFriction.GetFriction(
                    waterLevel: altitude,
                    groundLevel: altitude,
                    positionZ: 0.0f,
                    StationaryComponent,
                    StationaryComponent,
                    StationaryComponent)));

    // The slow-flight gate at 0x00411B39 is 1.5f and it is `test ah, 1` -
    // C0-only - so the interpolated arm needs a magnitude strictly below 1.5.
    // Exactly 1.5 takes the fast arm and gets the flat 0.99f, which at altitude
    // 2 is visibly different from the 0.98f the interpolation would give.
    [Theory]
    [InlineData(0.0f, 0x3F7AE148u)]
    [InlineData(1.4999f, 0x3F7AE148u)]
    [InlineData(1.5f, 0x3F7D70A4u)]
    [InlineData(9.0f, 0x3F7D70A4u)]
    public void GetFriction_GatesTheInterpolatedArmAtOnePointFive(
        float speedAlongX, uint expectedBits) =>
        Assert.Equal(
            expectedBits,
            BitConverter.SingleToUInt32Bits(
                RetailJetFriction.GetFriction(
                    waterLevel: 2.0f,
                    groundLevel: 2.0f,
                    positionZ: 0.0f,
                    speedAlongX,
                    StationaryComponent,
                    StationaryComponent)));

    // Core's existing fixed-point jet model opens the interpolated arm at a
    // speed of 1.0 in the same scale (Simulation.JetFrictionNumerator, speed <
    // 1_000 against altitudes of 1_000 and 3_000). Retail's gate is 1.5 at both
    // BattleEngineJetPart.cpp:628 and 0x00411B39, so speeds in [1.0, 1.5) below
    // the ceiling are exactly where the two models part company. Pinned here so
    // the disagreement cannot be closed by quietly moving this law.
    [Fact]
    public void GetFriction_InterpolatesAtSpeedsCoreAlreadyTreatsAsFast()
    {
        Assert.Equal(
            0x3F7AE148u,
            BitConverter.SingleToUInt32Bits(
                RetailJetFriction.GetFriction(
                    waterLevel: 2.0f,
                    groundLevel: 2.0f,
                    positionZ: 0.0f,
                    1.2f,
                    StationaryComponent,
                    StationaryComponent)));
    }

    // The reference is the numerically SMALLER of water and ground, whichever
    // of the two it happens to be, and the chassis Z is subtracted from it. The
    // first two rows are the same geometry with the roles swapped and must
    // agree; a rebuild that always took the water level, or that took the
    // larger of the pair, reads 10.5 on one of them and returns cruise
    // friction. No claim is made here about which surface that is in world
    // terms - see the remarks on RetailJetFriction.Altitude.
    [Theory]
    [InlineData(10.0f, 0.0f, -0.5f, 0x3F7D70A4u)]
    [InlineData(0.0f, 10.0f, -0.5f, 0x3F7D70A4u)]
    [InlineData(10.0f, 0.0f, -5.0f, 0x3F7AE148u)]
    public void Altitude_MeasuresFromTheLowerOfWaterAndGround(
        float waterLevel, float groundLevel, float positionZ, uint expectedBits) =>
        Assert.Equal(
            expectedBits,
            BitConverter.SingleToUInt32Bits(
                RetailJetFriction.GetFriction(
                    waterLevel,
                    groundLevel,
                    positionZ,
                    StationaryComponent,
                    StationaryComponent,
                    StationaryComponent)));

    // Every compare in this body is `fcomp / fnstsw / test ah, 1`, which reads
    // C0 alone, and an unordered compare sets C0. So a NaN water level is
    // chosen over a finite ground level, and the NaN altitude that follows
    // takes the near-surface arm. Written the natural C# way - `waterLevel <
    // groundLevel` and `altitude < 1.0f` - both would go the other way, which
    // is the mutation this test kills.
    [Fact]
    public void GetFriction_UnorderedInputsFallTheWayC0Does()
    {
        Assert.True(float.IsNaN(RetailJetFriction.Altitude(float.NaN, 5.0f, 0.0f)));

        Assert.Equal(
            0x3F7D70A4u,
            BitConverter.SingleToUInt32Bits(
                RetailJetFriction.GetFriction(
                    waterLevel: float.NaN,
                    groundLevel: 5.0f,
                    positionZ: 0.0f,
                    StationaryComponent,
                    StationaryComponent,
                    StationaryComponent)));
    }

    // The altitude is stored back to a float at 0x00411ADF before anything
    // compares it, so the value the ladder sees is float-rounded, not the
    // extended difference.
    [Fact]
    public void Altitude_IsRoundedToFloatBeforeTheLadderSeesIt()
    {
        float altitude = RetailJetFriction.Altitude(
            waterLevel: 16777216.0f, groundLevel: 16777216.0f, positionZ: -1.0f);

        Assert.Equal(0x4B800000u, BitConverter.SingleToUInt32Bits(altitude));
        Assert.Equal(16777216.0f, altitude);
    }

    // The magnitude at 0x00411B19-0x00411B31 never leaves the x87 stack, so
    // under the CRT's 53-bit precision control every partial product and sum is
    // a double. The second assertion is the same vector accumulated in floats,
    // and it lands one ulp lower - which is the mutation (widen only at the
    // end, or round each square to float) that this pins.
    [Fact]
    public void VelocityMagnitude_AccumulatesInDoubleNotFloat()
    {
        float x = BitConverter.UInt32BitsToSingle(0x401B0C75u);
        float y = BitConverter.UInt32BitsToSingle(0x3FB1D7E5u);
        float z = BitConverter.UInt32BitsToSingle(0x40340B7Eu);

        double magnitude = RetailJetFriction.VelocityMagnitude(x, y, z);

        Assert.Equal(0x400FB66050EFFAF2UL, BitConverter.DoubleToUInt64Bits(magnitude));
        Assert.Equal(0x407DB303u, BitConverter.SingleToUInt32Bits((float)magnitude));

        float allFloat = (float)System.Math.Sqrt(x * x + y * y + z * z);
        Assert.Equal(0x407DB302u, BitConverter.SingleToUInt32Bits(allFloat));

        Assert.Equal(
            0x40140000_00000000UL,
            BitConverter.DoubleToUInt64Bits(
                RetailJetFriction.VelocityMagnitude(3.0f, 4.0f, 0.0f)));
    }
}
