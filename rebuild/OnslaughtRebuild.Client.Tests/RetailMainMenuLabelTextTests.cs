// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.GodotClient;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// Pins the other CFEPMain::Render DrawTextDynamic at
/// <c>0x0046316F</c> — dest ebx/ecx, leftover 0 / 0 /
/// <c>0x447A0000</c>, Z <c>0x3EA3D70A</c> — recovered from
/// official 74154bfa
/// <c>local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe</c>,
/// SHA-256 <c>74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750</c>
/// (2,506,752 bytes, re-hashed this cycle). Image base <c>0x400000</c>.
/// File offset = VA − <c>0x400000</c>.
///
/// <para>Official bytes independently re-read this cycle:
/// <c>0x0046313D</c> / <c>0x00463141</c> load <c>[esp+0x28]</c> /
/// <c>[esp+0x24]</c>, then <c>0x00463145</c> / <c>0x00463147</c> /
/// <c>0x00463149</c> push 0 / 0 / <c>0x447A0000</c>,
/// <c>push eax</c> / <c>push ebp</c> / 1.0 / 1.0 /
/// <c>0x3EA3D70A</c> / <c>push ecx</c> / <c>push ebx</c> /
/// <c>push 1</c>, <c>mov ecx, 0x0088A0A8</c>,
/// <c>call 0x00515A70</c> at <c>0x00463168</c>,
/// <c>call 0x00465710</c> at <c>0x0046316F</c>
/// (<c>RET 0x28</c>). Dest is ebx/ecx, not immediates.
/// <c>0x3EA3D70A</c> is Z, not writing-chrome 0.9 and not
/// selector-bar 0.33. Cite-fix: <c>cmp ebx, 0x3E8</c> is at
/// <c>0x00465771</c>; <c>0x00465777</c> is
/// <c>mov word [eax], 0</c>. Do not invent wrap from either.
/// The 2px MeasureText residual stays open. DrawMainMenu keeps
/// LabelColor, MeasureText dest, and scale 1.0. Do not invent
/// dest, wrap, fade, or sheen. Do not redo version
/// DrawTextDynamic tail, writing Z/X, selector-bar Z/X,
/// 0x00463873, 0x004638B7, 0x00463A8F, 0x00463AD3,
/// 0x00463D1F, 0x00463D63, 0x00463F3F, or 0x00463F83.</para>
/// </summary>
public sealed class RetailMainMenuLabelTextTests
{
    [Fact]
    public void SpecimenSitesAreLabelDrawTextDynamicNotADestImmediate()
    {
        Assert.Equal(0x0046313Du, RetailMainMenuLabelText.TextLoadSite);
        Assert.Equal(0x00463141u, RetailMainMenuLabelText.DestYLoadSite);
        Assert.Equal(0x00463145u, RetailMainMenuLabelText.FirstLeftoverPushSite);
        Assert.Equal(0x00463147u, RetailMainMenuLabelText.SecondLeftoverPushSite);
        Assert.Equal(0x00463149u, RetailMainMenuLabelText.FloatLeftoverPushSite);
        Assert.Equal(0x447A0000u, RetailMainMenuLabelText.FloatSlotBits);
        Assert.Equal(0x0046314Eu, RetailMainMenuLabelText.TextPushSite);
        Assert.Equal(0x0046314Fu, RetailMainMenuLabelText.ColorPushSite);
        Assert.Equal(0x00463150u, RetailMainMenuLabelText.ScaleYPushSite);
        Assert.Equal(0x00463155u, RetailMainMenuLabelText.ScaleXPushSite);
        Assert.Equal(0x0046315Au, RetailMainMenuLabelText.ZPushSite);
        Assert.Equal(0x3EA3D70Au, RetailMainMenuLabelText.ZBits);
        Assert.Equal(0x0046315Fu, RetailMainMenuLabelText.DestYPushSite);
        Assert.Equal(0x00463160u, RetailMainMenuLabelText.DestXPushSite);
        Assert.Equal(0x00463161u, RetailMainMenuLabelText.FontSlotPushSite);
        Assert.Equal(1, RetailMainMenuLabelText.FontSlot);
        Assert.Equal(0x0088A0A8u, RetailMainMenuLabelText.FontThis);
        Assert.Equal(0x00463168u, RetailMainMenuLabelText.FontCallSite);
        Assert.Equal(0x00515A70u, RetailMainMenuLabelText.FontHelper);
        Assert.Equal(0x0046316Fu, RetailMainMenuLabelText.CallSite);
        Assert.Equal(0x00465710u, RetailMainMenuLabelText.DrawTextDynamic);
        Assert.Equal(0x00465997u, RetailMainMenuLabelText.BodyRetSite);
        Assert.Equal(0x28, RetailMainMenuLabelText.BodyRetImmediate);
        Assert.Equal(10, RetailMainMenuLabelText.StackArgCount);
        Assert.Equal(0x00462F29u, RetailMainMenuLabelText.TextSaveSite);
        Assert.Equal(0x00462F3Du, RetailMainMenuLabelText.GetTextExtentSite);
        Assert.Equal(0x00540680u, RetailMainMenuLabelText.GetTextExtent);
        Assert.Equal(0x00462F17u, RetailMainMenuLabelText.LanguageRowGateSite);
        Assert.Equal(0x00463191u, RetailMainMenuLabelText.LanguageRowTarget);
        Assert.Equal(0x0046318Cu, RetailMainMenuLabelText.PostCallJmpSite);
        Assert.Equal(0x0046364Du, RetailMainMenuLabelText.PostCallJmpTarget);
        Assert.Equal(0x00465771u, RetailMainMenuLabelText.LengthClampSite);
        Assert.Equal(0x00465777u, RetailMainMenuLabelText.LengthClampStoreSite);
        Assert.Equal(0x3E8, RetailMainMenuLabelText.LengthClampImmediate);
        Assert.Equal(0x005DB5E0u, RetailMainMenuLabelText.DestXGlobal);
        Assert.Equal(0x435B0000u, RetailMainMenuLabelText.DestXGlobalBits);
        Assert.Equal(
            RetailMainMenuVersionOverlayTail.DrawTextDynamic,
            RetailMainMenuLabelText.DrawTextDynamic);
        Assert.Equal(
            RetailMainMenuVersionOverlayFont.FontHelper,
            RetailMainMenuLabelText.FontHelper);
        Assert.Equal(
            RetailMainMenuVersionOverlayFont.FontSlot,
            RetailMainMenuLabelText.FontSlot);
        Assert.Equal(
            RetailMainMenuVersionOverlayTail.FloatSlotBits,
            RetailMainMenuLabelText.FloatSlotBits);
        Assert.NotEqual(
            RetailMainMenuVersionOverlayTail.CallSite,
            RetailMainMenuLabelText.CallSite);
        Assert.NotEqual(
            RetailMainMenuWritingZ.Tile0ZBits,
            RetailMainMenuLabelText.ZBits);
        Assert.NotEqual(
            RetailMainMenuSelectorBarZ.ZBits,
            RetailMainMenuLabelText.ZBits);
        Assert.NotEqual(
            RetailMainMenuVersionOverlayZ.ZBits,
            RetailMainMenuLabelText.ZBits);
        Assert.False(RetailMainMenuLabelText.InventsDestImmediates);
        Assert.False(RetailMainMenuLabelText.InventsFade);
        Assert.False(RetailMainMenuLabelText.InventsKerningHack);
        Assert.False(RetailMainMenuLabelText.InventsWrapWidth);
        Assert.False(RetailMainMenuLabelText.InventsSheen);
        Assert.False(RetailMainMenuLabelText.InventsLengthClampAsWrap);
        Assert.False(RetailMainMenuLabelText.IsSetLanguage);
        Assert.False(RetailMainMenuLabelText.IsButtonPressed);
        Assert.False(RetailMainMenuLabelText.RedoesVersionOverlayTail);
        Assert.False(RetailMainMenuLabelText.RedoesVersionOverlayZ);
        Assert.False(RetailMainMenuLabelText.RedoesWritingZ);
        Assert.False(RetailMainMenuLabelText.RedoesSelectorBarZ);
        Assert.False(RetailMainMenuLabelText.UsesTwinFadeGate);
        Assert.False(RetailMainMenuLabelText.OwnsLanguageSine);
    }

    [Fact]
    public void LeftoverZIsPointThreeTwoAndTailSkipsBelowZeroQuarterAndHalfArms()
    {
        Assert.Equal(0.32f, RetailMainMenuLabelText.Z);
        Assert.Equal(1000f, RetailMainMenuLabelText.FloatSlot);
        Assert.Equal(1f, RetailMainMenuLabelText.ScaleX);
        Assert.Equal(1f, RetailMainMenuLabelText.ScaleY);
        Assert.Equal(219f, RetailMainMenuLabelText.DestXAnchor);
        Assert.Equal(0, RetailMainMenuLabelText.SecondSlot);
        Assert.Equal(0, RetailMainMenuLabelText.FirstSlot);
        Assert.Equal(
            RetailMainMenuVersionOverlayTail.BodyRetImmediate,
            RetailMainMenuLabelText.StackArgCount * 4);
        Assert.False(
            RetailMainMenuVersionOverlayTail.TakesBelowZeroArm(
                RetailMainMenuLabelText.FloatSlot));
        Assert.False(
            RetailMainMenuVersionOverlayTail.TakesBelowQuarterArm(
                RetailMainMenuLabelText.FloatSlot));
        Assert.False(
            RetailMainMenuVersionOverlayTail.TakesBelowHalfArm(
                RetailMainMenuLabelText.FloatSlot));
        Assert.True(
            RetailMainMenuVersionOverlayTail.SkipsArg9Arm(
                RetailMainMenuLabelText.SecondSlot));
        Assert.NotEqual(
            RetailMainMenuLabelText.LengthClampImmediate,
            unchecked((int)RetailMainMenuLabelText.FloatSlotBits));
        Assert.NotEqual(
            RetailMainMenuLabelText.LengthClampSite,
            RetailMainMenuLabelText.LengthClampStoreSite);
        Assert.True(RetailMainMenuLabelText.ZPushSite < RetailMainMenuLabelText.CallSite);
        Assert.True(RetailMainMenuLabelText.CallSite < RetailMainMenuLabelText.PostCallJmpSite);
        Assert.True(
            RetailMainMenuLabelText.LanguageRowGateSite <
            RetailMainMenuLabelText.CallSite);
        Assert.NotEqual(
            RetailMainMenuLabelText.PostCallJmpTarget,
            RetailMainMenuLabelText.LanguageRowTarget);
        Assert.False(RetailMainMenuLabelText.InventsWrapWidth);
        Assert.False(RetailMainMenuLabelText.InventsDestImmediates);
        Assert.False(RetailMainMenuLabelText.InventsFade);
        Assert.False(RetailMainMenuLabelText.InventsLengthClampAsWrap);
        Assert.False(RetailMainMenuLabelText.InventsKerningHack);
    }

    [Fact]
    public void DrawMainMenuKeepsLabelColorMeasureTextAndDoesNotInventDestOrWrap()
    {
        NativeMainMenuSource.HasNoPresentationSideEffects();
        Assert.Contains("label.bind(rows[index].text, font)", NativeMainMenuSource.Controller, StringComparison.Ordinal);
        Assert.Contains("Laws.label_color(index == selected, rows[index].available)", NativeMainMenuSource.Controller, StringComparison.Ordinal);
        Assert.Contains("active_font.measure(displayed_units())", NativeMainMenuSource.Label, StringComparison.Ordinal);
        Assert.Contains("source_anchor.x - F.value(width * 0.5)", NativeMainMenuSource.Label, StringComparison.Ordinal);
        Assert.Contains("active_font.draw_run(self, displayed_units(), drawing_origin()", NativeMainMenuSource.Label, StringComparison.Ordinal);
        Assert.DoesNotContain("wrap", NativeMainMenuSource.Label, StringComparison.Ordinal);
        Assert.DoesNotContain("42.0", NativeMainMenuSource.Label, StringComparison.Ordinal);
        Assert.DoesNotContain("1000.0", NativeMainMenuSource.Label, StringComparison.Ordinal);
        Assert.DoesNotContain("0.32", NativeMainMenuSource.Label, StringComparison.Ordinal);
        Assert.DoesNotContain(" - 2", NativeMainMenuSource.Label, StringComparison.Ordinal);
        string[] names = ["NewGame", "ContinueGame", "LoadGame", "Multiplayer", "Goodies", "Options", "Quit"];
        for (int index = 0; index < names.Length; index++)
        {
            NativeMainMenuSource.HasAnchor(names[index], 219f, 304f + index * 20f - 8f);
            NativeMainMenuSource.HasBounds(names[index], 99f, 294f + index * 20f, 339f, 314f + index * 20f);
        }
        Assert.Contains("const ROW_FIRST_Y: float = 304.0", NativeMainMenuSource.Laws, StringComparison.Ordinal);
        Assert.Contains("const ROW_PITCH: float = 20.0", NativeMainMenuSource.Laws, StringComparison.Ordinal);

        string flow = File.ReadAllText(Path.Combine(AppContext.BaseDirectory, "godot-pause-source", "RetailFrontendFlow.cs"));
        string quit = NativeQuitSource.Presentation;
        Assert.DoesNotContain("RetailMainMenuLabelText", quit, StringComparison.Ordinal);
        string choice = NativeQuitSource.Presentation;
        Assert.DoesNotContain("RetailMainMenuLabelText", choice, StringComparison.Ordinal);
        string loading = NativeLoadingSource.Presentation;
        Assert.DoesNotContain("RetailMainMenuLabelText", loading, StringComparison.Ordinal);
        string bar = NativeMainMenuSource.Selector;
        Assert.DoesNotContain("RetailMainMenuLabelText", bar, StringComparison.Ordinal);
        string language = NativeMainMenuSource.Controller;
        Assert.DoesNotContain("RetailMainMenuLabelText", language, StringComparison.Ordinal);
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
