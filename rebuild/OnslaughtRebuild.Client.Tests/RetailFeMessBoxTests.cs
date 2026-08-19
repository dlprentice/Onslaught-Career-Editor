// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.GodotClient;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// Pins the quit FEMessBox Create() arguments recovered from
/// <c>CFEPMain__DoAction</c> <c>0x004623E0</c> in pristine
/// <c>BEA.exe.original.backup</c> SHA-256
/// <c>74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750</c>.
///
/// Height is not claimed: the 4th stack immediate is <c>0x3DCCCCCD</c> (0.1f),
/// not a pixel extent.
/// </summary>
public sealed class RetailFeMessBoxTests
{
    [Fact]
    public void QuitCreateIsFourHundredWideCentredOnTheStage()
    {
        // 0x004625E6 push 400.0f; 0x004625EB push 240.0f; 0x004625F0 push 320.0f
        // immediately before the Create call. Localization 0xe4 is pushed at
        // 0x004625D1.
        Assert.Equal(320f, RetailFeMessBox.QuitCenterX);
        Assert.Equal(240f, RetailFeMessBox.QuitCenterY);
        Assert.Equal(400f, RetailFeMessBox.QuitWidth);
        Assert.Equal(120f, RetailFeMessBox.QuitLeft);
        Assert.Equal(0xE4, RetailFeMessBox.QuitLocalizationId);
    }

    [Fact]
    public void DrawQuitConfirmUsesTheRecoveredWidthAndCentre()
    {
        string flow = File.ReadAllText(
            Path.Combine(AppContext.BaseDirectory, "godot-pause-source", "RetailFrontendFlow.cs"));

        Assert.Contains("RetailFeMessBox.QuitLeft", flow);
        Assert.Contains("RetailFeMessBox.QuitWidth", flow);
        Assert.DoesNotContain("new Rect2(70f, 160f, 500f, 140f)", flow);
    }
}
