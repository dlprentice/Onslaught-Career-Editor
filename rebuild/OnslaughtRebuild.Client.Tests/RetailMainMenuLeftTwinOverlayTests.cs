// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.GodotClient;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// Pins the CFEPMain::Render DAT_0089D898 not/and/xor overlay at
/// <c>0x00463AD3</c>, recovered from official 74154bfa
/// <c>local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe</c>,
/// SHA-256 <c>74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750</c>
/// (2,506,752 bytes, re-hashed this cycle). Image base <c>0x400000</c>.
/// File offset = VA − <c>0x400000</c>.
///
/// <para>The keep-going leftover labeled <c>0x00463AD3</c> as the
/// not/and/xor pack on leftover left-twin DAT_0089D898, not D894 /
/// D8A0 / D8A4. Official bytes independently re-read this cycle:
/// <c>mov eax, esi</c> at <c>0x00463AD3</c> (<c>8b c6</c>),
/// <c>mov ecx, [esp+0x40]</c> at <c>0x00463AD5</c>, then
/// <c>shl 8 / sub esi / push ebp / shl 16 / mov edx, eax / push
/// 0x3F800000 / not edx / and 0x00FFFFFF / xor eax</c>. Texture
/// load at <c>0x00463AF8</c> is <c>mov eax, [0x0089D898]</c>. Dest
/// immediates <c>0x00463B05</c>=344.0 / <c>0x00463B0A</c>=219.0.
/// The leftover 0.3 push at <c>0x00463B00</c> is CDXSurf Z
/// <c>0x3E99999A</c>, not scale and not a 29% title-logo. Then
/// <c>CDXSurf__RenderSurface</c> (<c>0x005563D0</c>) at
/// <c>0x00463B0F</c>. Dest is the leftover left-twin body, not
/// DAT_0089D894 primary and not right. This is not the 0x00463E8D
/// twin-fade gate (that is D8A4). Shadow sibling 0x00463A8F is
/// already RetailMainMenuLeftTwinShadow. Settled 255 submits
/// <c>0xFEFFFFFF</c>, which is not capture BracketTint.
/// DrawMainMenu keeps BracketTint. Not a sheen (that is already
/// 0x00464343). Not SetLanguage. Not a Process increment. Do not
/// redo 0x00463873, 0x004638B7, 0x00463A8F, 0x00463D1F,
/// 0x00463D63, 0x00463F3F, or 0x00463F83. Do not redo the
/// RetailFrontendDecorShadow ellipse.</para>
/// </summary>
public sealed class RetailMainMenuLeftTwinOverlayTests
{
    [Fact]
    public void SpecimenSitesAreTheNotAndXorOverlayOnDat0089D898()
    {
        Assert.Equal(0x00463AD3u, RetailMainMenuLeftTwinOverlay.Site);
        Assert.Equal(0x00463AD5u, RetailMainMenuLeftTwinOverlay.Esp40Site);
        Assert.Equal(0x00463AD9u, RetailMainMenuLeftTwinOverlay.ShiftSite);
        Assert.Equal(8, RetailMainMenuLeftTwinOverlay.ShiftLeft);
        Assert.Equal(0x00463ADCu, RetailMainMenuLeftTwinOverlay.SubSite);
        Assert.Equal(0x00463ADEu, RetailMainMenuLeftTwinOverlay.PushEbpSite);
        Assert.Equal(0x00463ADFu, RetailMainMenuLeftTwinOverlay.Shift16Site);
        Assert.Equal(0x00463AE2u, RetailMainMenuLeftTwinOverlay.CopySite);
        Assert.Equal(0x00463AE4u, RetailMainMenuLeftTwinOverlay.ScalePushSite);
        Assert.Equal(0x3F800000u, RetailMainMenuLeftTwinOverlay.ScaleBits);
        Assert.Equal(1f, RetailMainMenuLeftTwinOverlay.Scale);
        Assert.Equal(0x00463AE9u, RetailMainMenuLeftTwinOverlay.NotSite);
        Assert.Equal(0x00463AEDu, RetailMainMenuLeftTwinOverlay.AndSite);
        Assert.Equal(0x00463AF6u, RetailMainMenuLeftTwinOverlay.XorSite);
        Assert.Equal(0x00FFFFFFu, RetailMainMenuLeftTwinOverlay.RgbMask);
        Assert.Equal(0x00463AF8u, RetailMainMenuLeftTwinOverlay.TextureLoadSite);
        Assert.Equal(0x0089D898u, RetailMainMenuLeftTwinOverlay.TextureGlobal);
        Assert.Equal(
            RetailMainMenuLeftTwinShadow.TextureGlobal,
            RetailMainMenuLeftTwinOverlay.TextureGlobal);
        Assert.NotEqual(
            RetailMainMenuLeftDecorOverlay.TextureGlobal,
            RetailMainMenuLeftTwinOverlay.TextureGlobal);
        Assert.NotEqual(
            RetailMainMenuRightDecorOverlay.TextureGlobal,
            RetailMainMenuLeftTwinOverlay.TextureGlobal);
        Assert.NotEqual(
            RetailMainMenuRightTwinOverlay.TextureGlobal,
            RetailMainMenuLeftTwinOverlay.TextureGlobal);
        Assert.NotEqual(0x0089D894u, RetailMainMenuLeftTwinOverlay.TextureGlobal);
        Assert.Equal(0x00463B00u, RetailMainMenuLeftTwinOverlay.ZPushSite);
        Assert.Equal(0x3E99999Au, RetailMainMenuLeftTwinOverlay.ZBits);
        Assert.Equal(0.3f, RetailMainMenuLeftTwinOverlay.Z);
        Assert.Equal(0x00463B05u, RetailMainMenuLeftTwinOverlay.YPushSite);
        Assert.Equal(344f, RetailMainMenuLeftTwinOverlay.DestY);
        Assert.Equal(0x00463B0Au, RetailMainMenuLeftTwinOverlay.XPushSite);
        Assert.Equal(219f, RetailMainMenuLeftTwinOverlay.DestX);
        Assert.Equal(4, RetailMainMenuLeftTwinOverlay.Mode);
        Assert.Equal(0x00463B0Fu, RetailMainMenuLeftTwinOverlay.CallSite);
        Assert.Equal(0x005563D0u, RetailMainMenuLeftTwinOverlay.RenderSurface);
        Assert.Equal(0x00463A8Fu, RetailMainMenuLeftTwinOverlay.ShadowSiblingSite);
        Assert.Equal(255, RetailMainMenuLeftTwinOverlay.ImageSettledFadeByte);
        Assert.Equal(0xFE7F7F7Fu, RetailMainMenuLeftTwinOverlay.CaptureDiffuse);
        Assert.Equal(0xFEFFFFFFu, RetailMainMenuLeftTwinOverlay.SettledSubmitted);
        Assert.False(RetailMainMenuLeftTwinOverlay.IsSetLanguage);
        Assert.False(RetailMainMenuLeftTwinOverlay.IsButtonPressed);
        Assert.False(RetailMainMenuLeftTwinOverlay.InventsSheen);
        Assert.False(RetailMainMenuLeftTwinOverlay.InventsTitleLogoScale);
        Assert.False(RetailMainMenuLeftTwinOverlay.TreatsZAsScale);
        Assert.False(RetailMainMenuLeftTwinOverlay.ReplacesBracketTint);
        Assert.False(RetailMainMenuLeftTwinOverlay.ReplacesChromeTint);
        Assert.False(RetailMainMenuLeftTwinOverlay.ReplacesShadowTint);
        Assert.False(RetailMainMenuLeftTwinOverlay.RedoesShadowSibling);
        Assert.False(RetailMainMenuLeftTwinOverlay.RedoesLeftDecorShadow);
        Assert.False(RetailMainMenuLeftTwinOverlay.RedoesLeftDecorOverlay);
        Assert.False(RetailMainMenuLeftTwinOverlay.RedoesRightDecorShadow);
        Assert.False(RetailMainMenuLeftTwinOverlay.RedoesRightDecorOverlay);
        Assert.False(RetailMainMenuLeftTwinOverlay.RedoesRightTwinShadow);
        Assert.False(RetailMainMenuLeftTwinOverlay.RedoesRightTwinOverlay);
        Assert.False(RetailMainMenuLeftTwinOverlay.RedoesDecorShadow);
        Assert.False(RetailMainMenuLeftTwinOverlay.UsesTwinFadeGate);
        Assert.NotEqual(
            RetailMainMenuLeftTwinShadow.Site,
            RetailMainMenuLeftTwinOverlay.Site);
        Assert.NotEqual(
            RetailMainMenuLeftDecorOverlay.Site,
            RetailMainMenuLeftTwinOverlay.Site);
        Assert.NotEqual(
            RetailMainMenuLeftDecorShadow.Site,
            RetailMainMenuLeftTwinOverlay.Site);
        Assert.NotEqual(
            RetailMainMenuRightDecorOverlay.Site,
            RetailMainMenuLeftTwinOverlay.Site);
        Assert.NotEqual(
            RetailMainMenuRightTwinOverlay.Site,
            RetailMainMenuLeftTwinOverlay.Site);
        Assert.Equal(
            RetailMainMenuLeftTwinShadow.BodySiblingSite,
            RetailMainMenuLeftTwinOverlay.Site);
    }

    [Fact]
    public void SettledSubmitIsWhiteAlphaNotCaptureGrey()
    {
        Assert.Equal(
            0xFEFFFFFFu,
            RetailMainMenuLeftTwinOverlay.SubmittedColor(
                RetailMainMenuLeftTwinOverlay.ImageSettledFadeByte));
        Assert.Equal(0x00FFFFFFu, RetailMainMenuLeftTwinOverlay.SubmittedColor(0));
        Assert.Equal(0xFEFFFFFFu, RetailMainMenuLeftTwinOverlay.SubmittedColor(256));
        Assert.Equal(0x00FFFFFFu, RetailMainMenuLeftTwinOverlay.SubmittedColor(-1));
        Assert.NotEqual(
            RetailMainMenuLeftTwinOverlay.CaptureDiffuse,
            RetailMainMenuLeftTwinOverlay.SubmittedColor(255));
        Assert.Equal(
            RetailClickToStartTitle.BodyColor(3.0d),
            RetailMainMenuLeftTwinOverlay.SubmittedColor(255));
        Assert.Equal(
            RetailMainMenuLanguageChevronColor.FirstPack(255),
            RetailMainMenuLeftTwinOverlay.SubmittedColor(255));
        Assert.Equal(
            RetailMainMenuLeftDecorOverlay.SubmittedColor(255),
            RetailMainMenuLeftTwinOverlay.SubmittedColor(255));
        Assert.Equal(
            RetailMainMenuRightTwinOverlay.SubmittedColor(255),
            RetailMainMenuLeftTwinOverlay.SubmittedColor(255));
        Assert.Equal(
            RetailMainMenuRightDecorOverlay.SubmittedColor(255),
            RetailMainMenuLeftTwinOverlay.SubmittedColor(255));
        Assert.NotEqual(
            RetailMainMenuLeftTwinShadow.SubmittedColor(255),
            RetailMainMenuLeftTwinOverlay.SubmittedColor(255));
        Assert.NotEqual(0x3E000000u, RetailMainMenuLeftTwinOverlay.SubmittedColor(255));
        Assert.NotEqual(0x3E7F7F7Fu, RetailMainMenuLeftTwinOverlay.SubmittedColor(255));
    }

    [Fact]
    public void PushZeroPointThreeIsZNotScaleAndDestIsLeftTwinNotPrimaryOrRight()
    {
        Assert.Equal(0x3E99999Au, RetailMainMenuLeftTwinOverlay.ZBits);
        Assert.Equal(
            0x3E99999Au,
            (uint)BitConverter.SingleToUInt32Bits(RetailMainMenuLeftTwinOverlay.Z));
        Assert.Equal(0x3F800000u, RetailMainMenuLeftTwinOverlay.ScaleBits);
        Assert.Equal(1f, RetailMainMenuLeftTwinOverlay.Scale);
        Assert.NotEqual(0.3f, RetailMainMenuLeftTwinOverlay.DestX);
        Assert.NotEqual(0.29f, RetailMainMenuLeftTwinOverlay.Z);
        Assert.NotEqual(0.35f, RetailMainMenuLeftTwinOverlay.Z);
        Assert.NotEqual(0.29f, RetailMainMenuLeftTwinOverlay.Scale);
        Assert.Equal(
            RetailMainMenuLeftDecorOverlay.ZBits,
            RetailMainMenuLeftTwinOverlay.ZBits);
        Assert.Equal(
            RetailMainMenuRightTwinOverlay.ZBits,
            RetailMainMenuLeftTwinOverlay.ZBits);
        Assert.NotEqual(
            RetailMainMenuLeftTwinShadow.ZBits,
            RetailMainMenuLeftTwinOverlay.ZBits);
        Assert.Equal(219f, RetailMainMenuLeftTwinOverlay.DestX);
        Assert.Equal(344f, RetailMainMenuLeftTwinOverlay.DestY);
        Assert.NotEqual(457f, RetailMainMenuLeftTwinOverlay.DestX);
        Assert.NotEqual(355f, RetailMainMenuLeftTwinOverlay.DestY);
        Assert.Equal(
            RetailMainMenuLeftTwinShadow.BodyDestX,
            RetailMainMenuLeftTwinOverlay.DestX);
        Assert.Equal(
            RetailMainMenuLeftTwinShadow.BodyDestY,
            RetailMainMenuLeftTwinOverlay.DestY);
        Assert.Equal(
            RetailMainMenuLeftDecorOverlay.DestX,
            RetailMainMenuLeftTwinOverlay.DestX);
        Assert.Equal(
            RetailMainMenuLeftDecorOverlay.DestY,
            RetailMainMenuLeftTwinOverlay.DestY);
        Assert.NotEqual(
            RetailMainMenuRightDecorOverlay.DestX,
            RetailMainMenuLeftTwinOverlay.DestX);
        Assert.NotEqual(
            RetailMainMenuRightDecorOverlay.DestY,
            RetailMainMenuLeftTwinOverlay.DestY);
        Assert.False(RetailMainMenuLeftTwinOverlay.TreatsZAsScale);
        Assert.False(RetailMainMenuLeftTwinOverlay.InventsSheen);
        Assert.False(RetailMainMenuLeftTwinOverlay.InventsTitleLogoScale);
        Assert.False(RetailMainMenuLeftTwinOverlay.UsesTwinFadeGate);
        Assert.False(RetailMainMenuLeftTwinOverlay.RedoesDecorShadow);
        Assert.False(RetailMainMenuLeftTwinOverlay.RedoesShadowSibling);
        Assert.False(RetailMainMenuLeftTwinOverlay.RedoesLeftDecorOverlay);
    }

    [Fact]
    public void DrawMainMenuKeepsCaptureBracketTintAndDoesNotInventASheen()
    {
        NativeMainMenuSource.HasNoPresentationSideEffects();
        NativeMainMenuSource.HasAnchor("Decoration/LeftTwin/Body", 219f, 344f);
        NativeMainMenuSource.HasAnchor("Decoration/LeftTwin/Shadow", 219f, 344f);
        NativeMainMenuSource.HasColor("Decoration/LeftTwin/Body", 0xfe7f7f7fu);
        NativeMainMenuSource.HasColor("Decoration/LeftTwin/Shadow", 0x3e000000u);
        Assert.Contains("Laws.left_twin(transition)", NativeMainMenuSource.Controller, StringComparison.Ordinal);
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
