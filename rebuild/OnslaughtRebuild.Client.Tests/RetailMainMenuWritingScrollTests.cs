// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.GodotClient;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// Pins the CFEPMain::Render prologue writing-chrome Y at
/// <c>0x00462D46</c>, recovered from the pristine specimen
/// <c>local-lab/safe-copy-bea-pristine/BEA.exe.original.backup</c>,
/// SHA-256 <c>74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750</c>
/// (2,506,752 bytes, re-hashed this cycle). File offset = VA − <c>0x400000</c>.
///
/// <para>The measured pool is 0.3 / 350.0 / 175 / +350 / +700.
/// Cold <c>mCounter</c> is BSS 0. This is not the 0x00463E8D twin
/// fade, not SetLanguage, and not a Process increment.</para>
/// </summary>
public sealed class RetailMainMenuWritingScrollTests
{
    [Fact]
    public void SpecimenPoolIsPointThreeTimesThreeHundredFiftyMinusFromOneHundredSeventyFive()
    {
        Assert.Equal(0x008A9570u, RetailMainMenuWritingScroll.CounterGlobal);
        Assert.Equal(0u, RetailMainMenuWritingScroll.ImageInitialCounterBits);
        Assert.Equal(0f, RetailMainMenuWritingScroll.ImageInitialCounter);
        Assert.Equal(0x005D8CB4u, RetailMainMenuWritingScroll.RateGlobal);
        Assert.Equal(0x3E99999Au, RetailMainMenuWritingScroll.RateBits);
        Assert.Equal(0.3f, RetailMainMenuWritingScroll.Rate);
        Assert.Equal(0x005DB5F0u, RetailMainMenuWritingScroll.PeriodGlobal);
        Assert.Equal(0x4075E00000000000UL, RetailMainMenuWritingScroll.PeriodBits);
        Assert.Equal(350.0, RetailMainMenuWritingScroll.Period);
        Assert.Equal(0x005DB5E8u, RetailMainMenuWritingScroll.OriginYGlobal);
        Assert.Equal(0x432F0000u, RetailMainMenuWritingScroll.OriginYBits);
        Assert.Equal(175f, RetailMainMenuWritingScroll.OriginY);
        Assert.Equal(0x005DB5E4u, RetailMainMenuWritingScroll.Tile1AddGlobal);
        Assert.Equal(0x43AF0000u, RetailMainMenuWritingScroll.Tile1AddBits);
        Assert.Equal(350f, RetailMainMenuWritingScroll.Tile1Add);
        Assert.Equal(0x005DB3B0u, RetailMainMenuWritingScroll.Tile2AddGlobal);
        Assert.Equal(0x442F0000u, RetailMainMenuWritingScroll.Tile2AddBits);
        Assert.Equal(700f, RetailMainMenuWritingScroll.Tile2Add);
        Assert.Equal(0x0055E3EAu, RetailMainMenuWritingScroll.FmodSite);
        Assert.Equal(3, RetailMainMenuWritingScroll.TileCount);
        Assert.Equal(458f, RetailMainMenuWritingScroll.TileX);
        Assert.Equal(268f, RetailMainMenuWritingScroll.LanguageSlotOverwriteY);
    }

    [Fact]
    public void ColdCounterRestoresTheThreeSettledTileYs()
    {
        float cold = RetailMainMenuWritingScroll.ImageInitialCounter;
        Assert.Equal(175f, RetailMainMenuWritingScroll.OffsetY(cold));
        Assert.Equal(175f, RetailMainMenuWritingScroll.TileY(cold, 0));
        Assert.Equal(525f, RetailMainMenuWritingScroll.TileY(cold, 1));
        Assert.Equal(875f, RetailMainMenuWritingScroll.TileY(cold, 2));
    }

    [Fact]
    public void OneTickDropsYByTheMeasuredRateAndWrapsAtThePeriod()
    {
        Assert.Equal(174.7f, RetailMainMenuWritingScroll.OffsetY(1f), 5);
        Assert.Equal(
            175f - 0.3f,
            RetailMainMenuWritingScroll.OffsetY(1f),
            5);
        // fmod(350, 350) == 0, so a full period returns to the origin.
        float fullPeriod = (float)(RetailMainMenuWritingScroll.Period / RetailMainMenuWritingScroll.Rate);
        Assert.Equal(175f, RetailMainMenuWritingScroll.OffsetY(fullPeriod));
        Assert.Equal(
            525f - 0.3f,
            RetailMainMenuWritingScroll.TileY(1f, 1),
            5);
        Assert.Equal(
            875f - 0.3f,
            RetailMainMenuWritingScroll.TileY(1f, 2),
            5);
    }

    [Fact]
    public void DrawMainMenuWiresThePrologueYAndLeavesTheHotspotsAlone()
    {
        NativeMainMenuSource.HasNoPresentationSideEffects();
        for (int tile = 0; tile < RetailMainMenuWritingScroll.TileCount; tile++)
        {
            float y = RetailMainMenuWritingScroll.TileY(RetailMainMenuWritingScroll.ImageInitialCounter, tile);
            NativeMainMenuSource.HasBounds("Writing/Tile" + tile, RetailMainMenuWritingScroll.TileX - 64f, y - 256f, RetailMainMenuWritingScroll.TileX + 64f, y + 256f);
            NativeMainMenuSource.HasColor("Writing/Tile" + tile, 0x3e7f7f7fu);
        }
        Assert.Contains("for index: int in range(3): get_node(\"Writing/Tile%d\" % index).set_fade(fade)", NativeMainMenuSource.Controller, StringComparison.Ordinal);
        Assert.Contains("forseti-writing-large.texture.aya", NativeMainMenuSource.Scene, StringComparison.Ordinal);
        Assert.DoesNotContain("Writing/Tile%d\" % index).position", NativeMainMenuSource.Controller, StringComparison.Ordinal);
        Assert.DoesNotContain("Writing/Tile%d\" % index).scale", NativeMainMenuSource.Controller, StringComparison.Ordinal);
    }

    [Fact]
    public void FourthTileIsNotRetail()
    {
        Assert.Throws<ArgumentOutOfRangeException>(
            () => RetailMainMenuWritingScroll.TileY(0f, 3));
        Assert.Throws<ArgumentOutOfRangeException>(
            () => RetailMainMenuWritingScroll.TileY(0f, -1));
    }

    private static string Slice(string source, string signature)
    {
        int start = source.IndexOf(signature, StringComparison.Ordinal);
        Assert.True(start >= 0, signature);
        string rest = source[start..];
        int next = rest.IndexOf("\n    private ", signature.Length, StringComparison.Ordinal);
        return next >= 0 ? rest[..next] : rest;
    }
}
