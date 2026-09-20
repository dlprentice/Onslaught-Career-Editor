// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.GodotClient;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// Pins the CFEPMain::Render DAT_0089D8A0 *63 alpha shadow pack at
/// <c>0x00463D1F</c>, recovered from official 74154bfa
/// <c>local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe</c>,
/// SHA-256 <c>74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750</c>
/// (2,506,752 bytes, re-hashed this cycle). Image base <c>0x400000</c>.
/// File offset = VA − <c>0x400000</c>.
///
/// <para>The keep-going leftover labeled <c>0x00463D1F</c> as the
/// *63 pack on DAT_0089D8A0, not D8A4. Official bytes:
/// <c>mov ecx, esi</c> at <c>0x00463D1F</c>, then
/// <c>shl 6 / sub esi / shl 16 / and 0xFF000000</c>. Texture load
/// at <c>0x00463D06</c> is <c>mov eax, [0x0089D8A0]</c>. The leftover
/// 0.35 push at <c>0x00463D31</c> is CDXSurf Z <c>0x3EB33333</c>,
/// not scale and not a 29% title-logo. Dest addends are
/// <c>fadd [0x005DB5C8]=365.0</c> then
/// <c>fadd [0x005DB5C4]=462.0</c> before <c>CDXSurf__RenderSurface</c>
/// (<c>0x005563D0</c>). Dest is the right-arc pair, not left.
/// This is not the 0x00463E8D twin-fade gate (that is D8A4). Body
/// sibling 0x00463D63 is the leftover not/and/xor pack at
/// (457,355) Z 0.3 — not this type. Settled 255 submits
/// <c>0x3E000000</c>, which is capture ShadowTint. DrawMainMenu
/// keeps ShadowTint. Not a sheen (that is already 0x00464343).
/// Not SetLanguage. Not a Process increment. Do not redo
/// 0x00463F3F or 0x00463F83. Do not redo the
/// RetailFrontendDecorShadow ellipse.</para>
/// </summary>
public sealed class RetailMainMenuRightDecorShadowTests
{
    [Fact]
    public void SpecimenSitesAreTheSixtyThreeAlphaShadowOnDat0089D8A0()
    {
        Assert.Equal(0x00463D1Fu, RetailMainMenuRightDecorShadow.Site);
        Assert.Equal(0x00463D21u, RetailMainMenuRightDecorShadow.ShiftSite);
        Assert.Equal(6, RetailMainMenuRightDecorShadow.ShiftLeft);
        Assert.Equal(0x00463D24u, RetailMainMenuRightDecorShadow.SubSite);
        Assert.Equal(0x00463D26u, RetailMainMenuRightDecorShadow.Shift16Site);
        Assert.Equal(0x00463D29u, RetailMainMenuRightDecorShadow.AndSite);
        Assert.Equal(0xFF000000u, RetailMainMenuRightDecorShadow.AlphaMask);
        Assert.Equal(0x00463D06u, RetailMainMenuRightDecorShadow.TextureLoadSite);
        Assert.Equal(0x0089D8A0u, RetailMainMenuRightDecorShadow.TextureGlobal);
        Assert.NotEqual(
            RetailMainMenuRightTwinShadow.TextureGlobal,
            RetailMainMenuRightDecorShadow.TextureGlobal);
        Assert.Equal(0x00463D31u, RetailMainMenuRightDecorShadow.ZPushSite);
        Assert.Equal(0x3EB33333u, RetailMainMenuRightDecorShadow.ZBits);
        Assert.Equal(0.35f, RetailMainMenuRightDecorShadow.Z);
        Assert.Equal(0x00463D36u, RetailMainMenuRightDecorShadow.SurfThisLoadSite);
        Assert.Equal(0x0089D758u, RetailMainMenuRightDecorShadow.SurfThis);
        Assert.Equal(0x00463D3Bu, RetailMainMenuRightDecorShadow.YHelperSite);
        Assert.Equal(0x00468750u, RetailMainMenuRightDecorShadow.YHelper);
        Assert.Equal(0x00463D40u, RetailMainMenuRightDecorShadow.DestYAddSite);
        Assert.Equal(0x005DB5C8u, RetailMainMenuRightDecorShadow.DestYAddGlobal);
        Assert.Equal(365f, RetailMainMenuRightDecorShadow.DestYAdd);
        Assert.Equal(0x00463D4Fu, RetailMainMenuRightDecorShadow.XHelperSite);
        Assert.Equal(0x00468730u, RetailMainMenuRightDecorShadow.XHelper);
        Assert.Equal(0x00463D54u, RetailMainMenuRightDecorShadow.DestXAddSite);
        Assert.Equal(0x005DB5C4u, RetailMainMenuRightDecorShadow.DestXAddGlobal);
        Assert.Equal(462f, RetailMainMenuRightDecorShadow.DestXAdd);
        Assert.Equal(4, RetailMainMenuRightDecorShadow.Mode);
        Assert.Equal(0x00463D5Eu, RetailMainMenuRightDecorShadow.CallSite);
        Assert.Equal(0x005563D0u, RetailMainMenuRightDecorShadow.RenderSurface);
        Assert.Equal(0x00463D63u, RetailMainMenuRightDecorShadow.BodySiblingSite);
        Assert.Equal(0x00463D95u, RetailMainMenuRightDecorShadow.BodyDestYPushSite);
        Assert.Equal(355f, RetailMainMenuRightDecorShadow.BodyDestY);
        Assert.Equal(0x00463D9Au, RetailMainMenuRightDecorShadow.BodyDestXPushSite);
        Assert.Equal(457f, RetailMainMenuRightDecorShadow.BodyDestX);
        Assert.Equal(0x3E99999Au, RetailMainMenuRightDecorShadow.BodyZBits);
        Assert.Equal(255, RetailMainMenuRightDecorShadow.ImageSettledFadeByte);
        Assert.Equal(0x3E000000u, RetailMainMenuRightDecorShadow.CaptureDiffuse);
        Assert.Equal(0x3E000000u, RetailMainMenuRightDecorShadow.SettledSubmitted);
        Assert.False(RetailMainMenuRightDecorShadow.IsSetLanguage);
        Assert.False(RetailMainMenuRightDecorShadow.IsButtonPressed);
        Assert.False(RetailMainMenuRightDecorShadow.InventsSheen);
        Assert.False(RetailMainMenuRightDecorShadow.InventsTitleLogoScale);
        Assert.False(RetailMainMenuRightDecorShadow.TreatsZAsScale);
        Assert.False(RetailMainMenuRightDecorShadow.ReplacesShadowTint);
        Assert.False(RetailMainMenuRightDecorShadow.ReplacesChromeTint);
        Assert.False(RetailMainMenuRightDecorShadow.ReplacesBracketTint);
        Assert.False(RetailMainMenuRightDecorShadow.RedoesBodyOverlay);
        Assert.False(RetailMainMenuRightDecorShadow.RedoesDecorShadow);
        Assert.False(RetailMainMenuRightDecorShadow.RedoesRightTwinShadow);
        Assert.False(RetailMainMenuRightDecorShadow.RedoesRightTwinOverlay);
        Assert.False(RetailMainMenuRightDecorShadow.UsesTwinFadeGate);
        Assert.NotEqual(
            RetailMainMenuRightTwinShadow.Site,
            RetailMainMenuRightDecorShadow.Site);
        Assert.NotEqual(
            RetailMainMenuRightTwinOverlay.Site,
            RetailMainMenuRightDecorShadow.Site);
    }

    [Fact]
    public void SettledSubmitMatchesCaptureShadowTintAndSiblingSixtyThreePacks()
    {
        Assert.Equal(
            0x3E000000u,
            RetailMainMenuRightDecorShadow.SubmittedColor(
                RetailMainMenuRightDecorShadow.ImageSettledFadeByte));
        Assert.Equal(0u, RetailMainMenuRightDecorShadow.SubmittedColor(0));
        Assert.Equal(0x3E000000u, RetailMainMenuRightDecorShadow.SubmittedColor(256));
        Assert.Equal(0u, RetailMainMenuRightDecorShadow.SubmittedColor(-1));
        Assert.Equal(
            RetailMainMenuRightDecorShadow.CaptureDiffuse,
            RetailMainMenuRightDecorShadow.SubmittedColor(255));
        Assert.Equal(
            RetailMainMenuTitleLogoShadow.SubmittedColor(255),
            RetailMainMenuRightDecorShadow.SubmittedColor(255));
        Assert.Equal(
            RetailMainMenuSelectedIconShadow.SubmittedColor(255),
            RetailMainMenuRightDecorShadow.SubmittedColor(255));
        Assert.Equal(
            RetailMainMenuRightTwinShadow.SubmittedColor(255),
            RetailMainMenuRightDecorShadow.SubmittedColor(255));
        Assert.NotEqual(
            RetailMainMenuRightTwinOverlay.SubmittedColor(255),
            RetailMainMenuRightDecorShadow.SubmittedColor(255));
        Assert.NotEqual(0xFE7F7F7Fu, RetailMainMenuRightDecorShadow.SubmittedColor(255));
        Assert.NotEqual(0x3E7F7F7Fu, RetailMainMenuRightDecorShadow.SubmittedColor(255));
    }

    [Fact]
    public void PushZeroPointThreeFiveIsZNotScaleAndDestIsRightArcNotLeft()
    {
        Assert.Equal(0x3EB33333u, RetailMainMenuRightDecorShadow.ZBits);
        Assert.Equal(
            0x3EB33333u,
            (uint)BitConverter.SingleToUInt32Bits(RetailMainMenuRightDecorShadow.Z));
        Assert.NotEqual(0.35f, RetailMainMenuRightDecorShadow.DestXAdd);
        Assert.NotEqual(0.29f, RetailMainMenuRightDecorShadow.Z);
        Assert.NotEqual(0.3f, RetailMainMenuRightDecorShadow.Z);
        Assert.Equal(
            RetailMainMenuRightTwinShadow.ZBits,
            RetailMainMenuRightDecorShadow.ZBits);
        Assert.NotEqual(
            RetailMainMenuRightTwinOverlay.ZBits,
            RetailMainMenuRightDecorShadow.ZBits);
        Assert.Equal(462f, RetailMainMenuRightDecorShadow.DestXAdd);
        Assert.Equal(365f, RetailMainMenuRightDecorShadow.DestYAdd);
        Assert.Equal(457f + 5f, RetailMainMenuRightDecorShadow.DestXAdd);
        Assert.Equal(355f + 10f, RetailMainMenuRightDecorShadow.DestYAdd);
        Assert.NotEqual(219f, RetailMainMenuRightDecorShadow.BodyDestX);
        Assert.NotEqual(344f, RetailMainMenuRightDecorShadow.BodyDestY);
        Assert.NotEqual(224f, RetailMainMenuRightDecorShadow.DestXAdd);
        Assert.NotEqual(349f, RetailMainMenuRightDecorShadow.DestYAdd);
        Assert.Equal(
            RetailMainMenuRightTwinShadow.DestXAdd,
            RetailMainMenuRightDecorShadow.DestXAdd);
        Assert.Equal(
            RetailMainMenuRightTwinShadow.DestYAdd,
            RetailMainMenuRightDecorShadow.DestYAdd);
        Assert.False(RetailMainMenuRightDecorShadow.TreatsZAsScale);
        Assert.False(RetailMainMenuRightDecorShadow.InventsSheen);
        Assert.False(RetailMainMenuRightDecorShadow.RedoesDecorShadow);
        Assert.False(RetailMainMenuRightDecorShadow.UsesTwinFadeGate);
    }

    [Fact]
    public void DrawMainMenuKeepsCaptureShadowTintAndDoesNotInventASheen()
    {
        NativeMainMenuSource.HasNoPresentationSideEffects();
        NativeMainMenuSource.HasAnchor("Decoration/Right/Body", 457f, 355f);
        NativeMainMenuSource.HasAnchor("Decoration/Right/Shadow", 457f, 355f);
        NativeMainMenuSource.HasColor("Decoration/Right/Body", 0xfe7f7f7fu);
        NativeMainMenuSource.HasColor("Decoration/Right/Shadow", 0x3e000000u);
        Assert.Contains("Laws.right_decor(transition)", NativeMainMenuSource.Controller, StringComparison.Ordinal);
        Assert.Contains("Laws.shadow_offset(facts.animation_seconds)", NativeMainMenuSource.Controller, StringComparison.Ordinal);
        Assert.Contains("var left_offset := Vector2(shadow[0], shadow[0])", NativeMainMenuSource.Controller, StringComparison.Ordinal);
        Assert.Contains("left_offset if index < 2 else offset", NativeMainMenuSource.Controller, StringComparison.Ordinal);
        Assert.Contains("state.scale * F.value(1.05)", NativeMainMenuSource.Controller, StringComparison.Ordinal);
        Assert.Contains("owner.get_node(\"Body\").set_motion(state.scale, state.rotation, state.alpha, Vector2.ZERO)", NativeMainMenuSource.Controller, StringComparison.Ordinal);
        Assert.Contains("source_anchor + offset", NativeMainMenuSource.Read("main_menu_rotated_image.gd"), StringComparison.Ordinal);
        Assert.DoesNotContain("0.29", NativeMainMenuSource.Read("main_menu_rotated_image.gd"), StringComparison.Ordinal);
        NativeMainMenuSource.HasMeasuredReflectionOnly();
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
