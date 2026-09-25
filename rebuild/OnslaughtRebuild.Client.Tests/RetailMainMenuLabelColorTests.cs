// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.GodotClient;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// Pins the CFEPMain::Render main-menu label colour at
/// <c>0x0046300B</c>, recovered from the pristine specimen
/// <c>local-lab/safe-copy-bea-pristine/BEA.exe.original.backup</c>,
/// SHA-256 <c>74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750</c>
/// (2,506,752 bytes, re-hashed this cycle). File offset = VA − <c>0x400000</c>.
///
/// <para>Idle <c>0xFF4F4F4F</c>, disabled <c>0x7F1F1F1F</c> when the
/// <c>[edx+0x24]</c> call returns 0, selected <c>0xFFFF6F3F</c> when
/// <c>ebx == [edi+8]</c> (selected wins). Settled ESI 255 then the
/// imul fade and draw unpack submit the capture dwords
/// <c>0xFD4F4F4F</c> / <c>0x7D1F1F1F</c> / <c>0xFDFF6F3F</c>.</para>
/// </summary>
public sealed class RetailMainMenuLabelColorTests
{
    [Fact]
    public void SpecimenImmediatesAreIdleDisabledThenSelected()
    {
        Assert.Equal(0x0046300Bu, RetailMainMenuLabelColor.IdleSite);
        Assert.Equal(0x00463017u, RetailMainMenuLabelColor.DisabledSite);
        Assert.Equal(0x00463021u, RetailMainMenuLabelColor.SelectedSite);
        Assert.Equal(0xFF4F4F4Fu, RetailMainMenuLabelColor.IdlePackedColor);
        Assert.Equal(0x7F1F1F1Fu, RetailMainMenuLabelColor.DisabledPackedColor);
        Assert.Equal(0xFFFF6F3Fu, RetailMainMenuLabelColor.SelectedPackedColor);
        Assert.Equal(0xFD4F4F4Fu, RetailMainMenuLabelColor.CaptureIdle);
        Assert.Equal(0x7D1F1F1Fu, RetailMainMenuLabelColor.CaptureDisabled);
        Assert.Equal(0xFDFF6F3Fu, RetailMainMenuLabelColor.CaptureSelected);
        Assert.Equal(255, RetailMainMenuLabelColor.ImageSettledFadeByte);
        Assert.False(RetailMainMenuLabelColor.IsSetLanguage);
        Assert.False(RetailMainMenuLabelColor.IsButtonPressed);
    }

    [Fact]
    public void SelectedWinsOverDisabled()
    {
        Assert.Equal(
            0xFFFF6F3Fu,
            RetailMainMenuLabelColor.BaseColor(selected: true, available: false));
        Assert.Equal(
            0x7F1F1F1Fu,
            RetailMainMenuLabelColor.BaseColor(selected: false, available: false));
        Assert.Equal(
            0xFF4F4F4Fu,
            RetailMainMenuLabelColor.BaseColor(selected: false, available: true));
        Assert.Equal(
            0xFFFF6F3Fu,
            RetailMainMenuLabelColor.BaseColor(selected: true, available: true));
    }

    [Fact]
    public void SettledSubmitMatchesCaptureDiffuse()
    {
        int esi = RetailMainMenuLabelColor.ImageSettledFadeByte;
        Assert.Equal(
            0xFD4F4F4Fu,
            RetailMainMenuLabelColor.SubmittedColor(selected: false, available: true, esi));
        Assert.Equal(
            0x7D1F1F1Fu,
            RetailMainMenuLabelColor.SubmittedColor(selected: false, available: false, esi));
        Assert.Equal(
            0xFDFF6F3Fu,
            RetailMainMenuLabelColor.SubmittedColor(selected: true, available: true, esi));
        Assert.Equal(
            RetailMainMenuLabelColor.CaptureSelected,
            RetailMainMenuLabelColor.SubmittedColor(selected: true, available: false, esi));
    }

    [Fact]
    public void DrawMainMenuWiresTheSettledPackAndLeavesTheHotspotsAlone()
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
        Assert.DoesNotContain("RetailMainMenuLabelColor", quit, StringComparison.Ordinal);
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
