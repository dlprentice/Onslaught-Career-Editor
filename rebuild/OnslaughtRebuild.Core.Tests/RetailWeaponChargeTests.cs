// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Core.Tests;

/// <summary>
/// Parity tests for <see cref="RetailWeaponCharge"/> against the pristine
/// <c>74154bfa…</c> bytes at <c>0x00412370</c>, <c>0x00412000</c> and
/// <c>0x00413CF0</c>. The pinned drop has no <c>CWeapon</c>, so every claim
/// here is measured from the image; the source only says "delegate".
/// </summary>
public sealed class RetailWeaponChargeTests
{
    private static RetailWeaponChargeTable Weapon(float charge, params int[] levels)
    {
        RetailWeaponChargeTable weapon = new() { Charge = charge };
        for (int index = 0; index < levels.Length; index++)
        {
            weapon.Levels[index] = levels[index];
        }

        return weapon;
    }

    // Five levels at a hundred each, absent marked with -1. The loop bounds
    // are `cmp eax, 0x1F4` against `add eax, 0x64` and `cmp eax, 5`.
    [Fact]
    public void TableShape_MatchesTheLoopBounds()
    {
        Assert.Equal(5, RetailWeaponChargeTable.LevelCount);
        Assert.Equal(100, RetailWeaponChargeTable.ValuePerLevel);
        Assert.Equal(-1, RetailWeaponChargeTable.AbsentLevel);
        Assert.Equal(
            0x1F4,
            RetailWeaponChargeTable.LevelCount * RetailWeaponChargeTable.ValuePerLevel);
    }

    // The scan has no early exit, so the answer is the LAST present index times
    // a hundred - not the first, not a count, and not the number of entries. A
    // rebuild that broke on the first hit reads 100 for the fourth row.
    [Theory]
    [InlineData(0, -1, -1, -1, -1, -1)]
    [InlineData(0, 7, -1, -1, -1, -1)]
    [InlineData(100, -1, 7, -1, -1, -1)]
    [InlineData(300, -1, 7, -1, 9, -1)]
    [InlineData(400, 1, 2, 3, 4, 5)]
    [InlineData(400, -1, -1, -1, -1, 5)]
    [InlineData(100, 7, 7, -1, -1, -1)]
    public void MaxCharge_TakesTheLastPresentLevel(
        int expected, int l0, int l1, int l2, int l3, int l4) =>
        Assert.Equal(expected, RetailWeaponCharge.MaxCharge(Weapon(0.0f, l0, l1, l2, l3, l4)));

    // `test esi, esi / je` at 0x004123DC returns 0.0f for an empty table AND
    // for a table whose only present level is index 0, because index 0 scales
    // to zero. A rebuild that divided anyway would produce an infinity for the
    // second case.
    [Theory]
    [InlineData(50.0f, -1, -1, -1, -1, -1)]
    [InlineData(50.0f, 7, -1, -1, -1, -1)]
    public void GetCharge_ReportsZeroWhenTheScaleIsZero(
        float charge, int l0, int l1, int l2, int l3, int l4)
    {
        float result = RetailWeaponCharge.GetCharge(Weapon(charge, l0, l1, l2, l3, l4));

        Assert.Equal(0x00000000u, BitConverter.SingleToUInt32Bits(result));
        Assert.False(float.IsInfinity(result));
    }

    // fild max / fdivr mCharge, so the quotient is charge over the scale. Exact
    // bits, because 1/300 is not representable and a rebuild that scaled by
    // anything but the last present index lands somewhere else entirely.
    [Theory]
    [InlineData(150.0f, 0x3F000000u)]
    [InlineData(1.0f, 0x3B5A740Eu)]
    [InlineData(300.0f, 0x3F800000u)]
    [InlineData(600.0f, 0x40000000u)]
    [InlineData(0.0f, 0x00000000u)]
    public void GetCharge_DividesByTheLastPresentLevel(float charge, uint expectedBits) =>
        Assert.Equal(
            expectedBits,
            BitConverter.SingleToUInt32Bits(
                RetailWeaponCharge.GetCharge(Weapon(charge, -1, 7, -1, 9, -1))));

    // CanCharge starts at record + 0x10 with its counter at 1, so level 0 is
    // invisible to it. That is the same population GetCharge reports as zero.
    [Theory]
    [InlineData(false, -1, -1, -1, -1, -1)]
    [InlineData(false, 7, -1, -1, -1, -1)]
    [InlineData(true, -1, 7, -1, -1, -1)]
    [InlineData(true, -1, -1, -1, -1, 7)]
    [InlineData(true, 7, 7, 7, 7, 7)]
    public void CanCharge_IgnoresTheFirstLevel(
        bool expected, int l0, int l1, int l2, int l3, int l4) =>
        Assert.Equal(expected, RetailWeaponCharge.CanCharge(Weapon(0.0f, l0, l1, l2, l3, l4)));

    // Not fully charged iff the scale is ordered and strictly greater than the
    // charge. Exactly at the scale counts as full (C3), and above it counts as
    // full (C0 on the other side).
    [Theory]
    [InlineData(0.0f, false)]
    [InlineData(299.0f, false)]
    [InlineData(300.0f, true)]
    [InlineData(301.0f, true)]
    [InlineData(-5.0f, false)]
    public void FullyCharged_ComparesTheScaleAgainstTheCharge(float charge, bool expected) =>
        Assert.Equal(
            expected,
            RetailWeaponCharge.FullyCharged(Weapon(charge, -1, 7, -1, 9, -1)));

    // test ah, 0x41 with jne to the bail-out label: an unordered compare sets
    // both bits, so a NaN charge reads as fully charged. Written the natural
    // way - `charge >= max` - C# would say false.
    [Fact]
    public void FullyCharged_TreatsAnUnorderedChargeAsFull()
    {
        Assert.True(RetailWeaponCharge.FullyCharged(Weapon(float.NaN, -1, 7, -1, 9, -1)));
        Assert.False(float.NaN >= 300.0f);
    }

    // The dead half of the inlined body, kept because a caller other than
    // ChargeWeapon could reach it: a weapon that cannot charge at all is
    // reported as fully charged.
    [Fact]
    public void FullyCharged_ReportsFullWhenNothingCanCharge() =>
        Assert.True(RetailWeaponCharge.FullyCharged(Weapon(0.0f, 7, -1, -1, -1, -1)));

    // `mov dword ptr [weapon + 0x60], 0` is an integer store of the all-zero
    // word, so the charge lands on +0.0f. A rebuild that wrote -0.0f, or that
    // subtracted to zero, would leave a different bit pattern for the divide to
    // read.
    [Fact]
    public void LoseCharge_StoresThePositiveZeroWord()
    {
        RetailWeaponChargeTable weapon = Weapon(-123.5f, -1, 7, -1, 9, -1);

        RetailWeaponCharge.LoseCharge(weapon);

        Assert.Equal(0x00000000u, BitConverter.SingleToUInt32Bits(weapon.Charge));
        Assert.Equal(
            0x00000000u,
            BitConverter.SingleToUInt32Bits(RetailWeaponCharge.GetCharge(weapon)));
    }
}
