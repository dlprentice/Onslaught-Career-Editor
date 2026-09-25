// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Client;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// Pins the <c>CMenuItemDropdown::Render</c> collapsed value dest
/// leftover at <c>0x004A40B4</c> — <c>mov edx, [esp+0x28]</c> after
/// vtable +0x44 <c>RET 4</c>, which aliases the earlier
/// <c>fstp [esp+0x18]</c> incoming dest X plus the 2.0 pad —
/// recovered from official 74154bfa
/// <c>local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe</c>,
/// SHA-256 <c>74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750</c>
/// (2,506,752 bytes, re-hashed this cycle). Image base <c>0x400000</c>.
/// File offset = VA − <c>0x400000</c>.
///
/// <para>Official bytes independently re-read this cycle:
/// <c>0x004A3D38</c> <c>fadd [0x005D8BA0]</c>,
/// <c>0x004A3D3E</c> <c>fstp [esp+0x18]</c>,
/// <c>0x005D8BA0</c> is <c>00 00 00 40</c> (2.0),
/// <c>0x004A3D78</c> <c>mov ebx, [esp+0x10C]</c> incoming dest Y,
/// <c>0x004A3DA8</c> <c>mov al, [esi+0x24]</c>,
/// <c>0x004A3DAD</c> <c>je 0x004A409B</c>,
/// <c>0x004A40A0</c> / <c>0x004A40A5</c> push identity 1.0,
/// <c>0x004A40B1</c> <c>call [eax+0x44]</c>,
/// every independently read +0x44 ends <c>RET 4</c>
/// (<c>0x004D01B2</c>, <c>0x004CF102</c>, <c>0x004A4232</c>),
/// <c>0x004A40B4</c> <c>mov edx, [esp+0x28]</c>,
/// <c>0x004A40CA</c> <c>call 0x004659A0</c>.
/// Dest X is incoming dest X plus the pad leftover. Dest is not
/// the 2.0 constant. Nearby 5.0 is leftover min dest X for the
/// label, not this dest. Dest Y keeps the row top. Scale stays
/// 1.0. DrawLabelValueRow consumes DestX. Do not invent dest Y=5,
/// dest X=5, dest Y=268, dest Y=284, dest Y=304, dest from the
/// 2.0 constant, wrap, fade, sheen, or a 2px kerning hack. Do
/// not change MeasureText. Do not redo the label dest, icon dest,
/// CMenuItem dest, colour AND, Apply pulse, dropdown cosine,
/// language pitch, or the 0x00463669 compare.</para>
/// </summary>
public sealed class RetailOptionsDropdownValueDestTests
{
    [Fact]
    public void SpecimenSitesAreCollapsedValueDestNotDestImmediates()
    {
        Assert.Equal(0x004A3C30u, RetailOptionsDropdownValueDest.RenderSite);
        Assert.Equal(0x004A3D38u, RetailOptionsDropdownValueDest.PadAddSite);
        Assert.Equal(0x004A3D3Eu, RetailOptionsDropdownValueDest.PadStoreSite);
        Assert.Equal(0x005D8BA0u, RetailOptionsDropdownValueDest.PadGlobal);
        Assert.Equal(0x40000000u, RetailOptionsDropdownValueDest.PadBits);
        Assert.Equal(0x004A3D78u, RetailOptionsDropdownValueDest.DestYLoadSite);
        Assert.Equal(0x24u, RetailOptionsDropdownValueDest.ExpandByteOffset);
        Assert.Equal(0x004A3DA8u, RetailOptionsDropdownValueDest.ExpandTestSite);
        Assert.Equal(0x004A3DADu, RetailOptionsDropdownValueDest.CollapseJumpSite);
        Assert.Equal(0x004A409Bu, RetailOptionsDropdownValueDest.CollapseTarget);
        Assert.Equal(0x44u, RetailOptionsDropdownValueDest.GetStateSlot);
        Assert.Equal(0x004A40B1u, RetailOptionsDropdownValueDest.GetStateCallSite);
        Assert.Equal(4u, RetailOptionsDropdownValueDest.GetStateRet);
        Assert.Equal(0x004A40B4u, RetailOptionsDropdownValueDest.DestLoadSite);
        Assert.Equal(0x3F800000u, RetailOptionsDropdownValueDest.ScaleBits);
        Assert.Equal(0x004A40CAu, RetailOptionsDropdownValueDest.DrawTextCallSite);
        Assert.Equal(0x004659A0u, RetailOptionsDropdownValueDest.DrawText);
        Assert.Equal(
            RetailOptionsDropdownDest.CollapsedValueDestSite,
            RetailOptionsDropdownValueDest.DestLoadSite);
        Assert.Equal(
            RetailOptionsDropdownDest.PadGlobal,
            RetailOptionsDropdownValueDest.PadGlobal);
        Assert.Equal(
            RetailOptionsDropdownDest.RenderSite,
            RetailOptionsDropdownValueDest.RenderSite);
        Assert.True(RetailOptionsDropdownValueDest.PadAddSite < RetailOptionsDropdownValueDest.PadStoreSite);
        Assert.True(RetailOptionsDropdownValueDest.PadStoreSite < RetailOptionsDropdownValueDest.DestYLoadSite);
        Assert.True(RetailOptionsDropdownValueDest.DestYLoadSite < RetailOptionsDropdownValueDest.ExpandTestSite);
        Assert.True(RetailOptionsDropdownValueDest.ExpandTestSite < RetailOptionsDropdownValueDest.CollapseJumpSite);
        Assert.True(RetailOptionsDropdownValueDest.CollapseJumpSite < RetailOptionsDropdownValueDest.CollapseTarget);
        Assert.True(RetailOptionsDropdownValueDest.CollapseTarget < RetailOptionsDropdownValueDest.GetStateCallSite);
        Assert.True(RetailOptionsDropdownValueDest.GetStateCallSite < RetailOptionsDropdownValueDest.DestLoadSite);
        Assert.True(RetailOptionsDropdownValueDest.DestLoadSite < RetailOptionsDropdownValueDest.DrawTextCallSite);
        Assert.True(RetailOptionsDropdownDest.DestStoreSite < RetailOptionsDropdownValueDest.DestLoadSite);
        Assert.True(RetailOptionsMenuItemIconDest.CxLoadSite < RetailOptionsDropdownValueDest.DestLoadSite);
        Assert.False(RetailOptionsDropdownValueDest.InventsDestY5);
        Assert.False(RetailOptionsDropdownValueDest.InventsDestX5);
        Assert.False(RetailOptionsDropdownValueDest.InventsDestY268);
        Assert.False(RetailOptionsDropdownValueDest.InventsDestY284);
        Assert.False(RetailOptionsDropdownValueDest.InventsDestY304);
        Assert.False(RetailOptionsDropdownValueDest.InventsDestFromPad);
        Assert.False(RetailOptionsDropdownValueDest.InventsDestImmediates);
        Assert.False(RetailOptionsDropdownValueDest.InventsKerningHack);
        Assert.False(RetailOptionsDropdownValueDest.InventsSheen);
        Assert.False(RetailOptionsDropdownValueDest.InventsWrapWidth);
        Assert.False(RetailOptionsDropdownValueDest.InventsFade);
        Assert.False(RetailOptionsDropdownValueDest.IsSetLanguage);
        Assert.False(RetailOptionsDropdownValueDest.IsButtonPressed);
        Assert.False(RetailOptionsDropdownValueDest.RedoesMenuItemDest);
        Assert.False(RetailOptionsDropdownValueDest.RedoesMenuItemIconDest);
        Assert.False(RetailOptionsDropdownValueDest.RedoesDropdownDest);
        Assert.False(RetailOptionsDropdownValueDest.RedoesMenuItemColor);
        Assert.False(RetailOptionsDropdownValueDest.RedoesApplyPulse);
        Assert.False(RetailOptionsDropdownValueDest.RedoesLanguagePitch);
        Assert.False(RetailOptionsDropdownValueDest.UsesTwinFadeGate);
        Assert.False(RetailOptionsDropdownValueDest.UsesLanguageCompare);
        Assert.False(RetailOptionsDropdownValueDest.ChangesMeasureText);
        Assert.False(RetailOptionsDropdownValueDest.UsesIntegerHalf);
    }

    [Fact]
    public void ValueDestIsIncomingPlusPadAndIsNotTwoOrFive()
    {
        Assert.Equal(1f, RetailOptionsDropdownValueDest.IdentityScale);
        Assert.Equal(2f, RetailOptionsDropdownValueDest.Pad);
        Assert.Equal(321f, RetailOptionsDropdownValueDest.DestX(319f));
        Assert.Equal(322f, RetailOptionsDropdownValueDest.DestX(320f));
        Assert.Equal(2f, RetailOptionsDropdownValueDest.DestX(0f));
        Assert.NotEqual(2f, RetailOptionsDropdownValueDest.DestX(319f));
        Assert.NotEqual(5f, RetailOptionsDropdownValueDest.DestX(319f));
        Assert.NotEqual(268f, RetailOptionsDropdownValueDest.DestX(319f));
        Assert.NotEqual(284f, RetailOptionsDropdownValueDest.DestX(319f));
        Assert.NotEqual(304f, RetailOptionsDropdownValueDest.DestX(319f));
        Assert.NotEqual(322f, RetailOptionsDropdownValueDest.DestX(319f));
        Assert.NotEqual(
            RetailOptionsDropdownDest.DestX(319f, 16),
            RetailOptionsDropdownValueDest.DestX(319f));
        Assert.NotEqual(
            RetailOptionsMenuItemDest.DestX(319f, 16),
            RetailOptionsDropdownValueDest.DestX(319f));
        Assert.NotEqual(
            RetailOptionsMenuItemIconDest.DestX(319f, 16),
            RetailOptionsDropdownValueDest.DestX(319f));
        Assert.NotEqual(
            RetailOptionsDropdownValueDest.Pad,
            RetailOptionsDropdownValueDest.IdentityScale);
        Assert.False(RetailOptionsDropdownValueDest.InventsDestY5);
        Assert.False(RetailOptionsDropdownValueDest.InventsDestX5);
        Assert.False(RetailOptionsDropdownValueDest.InventsDestFromPad);
        Assert.False(RetailOptionsDropdownValueDest.UsesIntegerHalf);
        Assert.False(RetailOptionsDropdownValueDest.ChangesMeasureText);
    }

    [Fact]
    public void DrawLabelValueRowConsumesDestXAndDoesNotInventDestTwo()
    {
        // Numeric/model assertions above stay pinned; this guard follows the production owner.
        string owner0 = NativeOptionsSource.Function("options_presentation.gd", "_refresh_popup");
        Assert.Contains("Laws.dropdown_value_x(319.0)", owner0, StringComparison.Ordinal);
        string owner1 = NativeOptionsSource.Function("options_row.gd", "bind");
        Assert.Contains("value.bind(row.current_state.value", owner1, StringComparison.Ordinal);
        string scene = NativeOptionsSource.Read("Options.tscn");
        Assert.Contains("offset_right = 319.0", scene, StringComparison.Ordinal);
        Assert.Contains("offset_left = 321.0", scene, StringComparison.Ordinal);
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
