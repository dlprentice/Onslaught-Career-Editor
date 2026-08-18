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
/// not a pixel extent. The extra chrome assertions pin FrontEnd.cpp
/// DrawPanel/DrawBox, Init colours, and the option_mode-2 Yes/No stack — not
/// FEMessBox.cpp tiles.
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
        string flow = FlowSource();

        Assert.Contains("RetailFeMessBox.QuitLeft", flow);
        Assert.Contains("RetailFeMessBox.QuitWidth", flow);
        Assert.DoesNotContain("new Rect2(70f, 160f, 500f, 140f)", flow);
    }

    [Fact]
    public void YesNoChromeIsTheCitedVerticalOptionModeTwoStack()
    {
        // CFrontEnd__RenderAndProcessModalPanel option_mode==2 draws FrontEndText
        // 0x1b then 0x1c. ASCII fallbacks at VA 0x0062b7d4 / 0x0062b7d0 are
        // "Yes" / "No". Selected 0 highlights the lower (No) row.
        Assert.Equal(2, RetailFeMessBox.OptionYesNo);
        Assert.Equal(0x1B, RetailFeMessBox.YesToken);
        Assert.Equal(0x1C, RetailFeMessBox.NoToken);
        Assert.Equal("Yes", RetailFeMessBox.YesLabel);
        Assert.Equal("No", RetailFeMessBox.NoLabel);
        Assert.Equal(0, RetailFeMessBox.DefaultChoiceIndex);
        Assert.Equal(140f, RetailFeMessBox.ReconstructionHeight);
        Assert.True(RetailFeMessBox.YesChoiceTop < RetailFeMessBox.NoChoiceTop);
    }

    [Fact]
    public void PanelAndBoxChromeAreTheCitedFrontEndDrawHelpers()
    {
        // FrontEnd.cpp:747-755 DrawPanel stretches FET2_BLANK over the rect.
        // FrontEnd.cpp:737-742 DrawBox issues four edges at width 2.0.
        // Init colours from CFrontEnd__InitPageStateDefaults 0x0044d320.
        Assert.Equal(16f, RetailFeMessBox.BlankPanelSize);
        Assert.Equal(2f, RetailFeMessBox.BoxLineWidth);
        Assert.Equal(0xAF000000u, RetailFeMessBox.PanelColor);
        Assert.Equal(0xFFFFFFFFu, RetailFeMessBox.TextColor);
        Assert.Equal(0xAF40FF40u, RetailFeMessBox.HighlightColor);
        Assert.Equal(0xFF7F7F7Fu, RetailFeMessBox.BorderColor);
        Assert.Equal(8f, RetailFeMessBox.TextPadY);
        Assert.Equal(4f, RetailFeMessBox.HighlightPadX);
    }

    [Fact]
    public void DrawQuitConfirmUsesBlankPanelBoxAndVerticalYesNo()
    {
        string flow = FlowSource();

        Assert.Contains("RetailFeMessBox.PanelColor", flow);
        Assert.Contains("RetailFeMessBox.BorderColor", flow);
        Assert.Contains("RetailFeMessBox.BoxLineWidth", flow);
        Assert.Contains("RetailFeMessBox.YesLabel", flow);
        Assert.Contains("RetailFeMessBox.NoLabel", flow);
        Assert.Contains("_feBlank", flow);
        Assert.DoesNotContain("DrawQuitConfirmChoice(\"No\", 220f", flow);
        Assert.DoesNotContain("DrawQuitConfirmChoice(\"Yes\", 420f", flow);
        Assert.DoesNotContain("new Color(0f, 0f, 0f, 0.82f)", flow);
    }

    [Fact]
    public void QuitConfirmHitRowsAreTheFullWidthYesNoStack()
    {
        string flow = FlowSource();

        Assert.DoesNotContain("new Rect2(160f, 240f, 120f, 36f)", flow);
        Assert.DoesNotContain("new Rect2(360f, 240f, 120f, 36f)", flow);
        Assert.Contains("RetailFeMessBox.QuitLeft", MethodBody(flow, "QuitConfirmIndexAt"));
        Assert.Contains("RetailFeMessBox.NoChoiceTop", MethodBody(flow, "QuitConfirmIndexAt"));
        Assert.Contains("RetailFeMessBox.YesChoiceTop", MethodBody(flow, "QuitConfirmIndexAt"));
    }

    private static string FlowSource() =>
        File.ReadAllText(
            Path.Combine(AppContext.BaseDirectory, "godot-pause-source", "RetailFrontendFlow.cs"));

    private static string MethodBody(string source, string methodName)
    {
        int signature = source.IndexOf("int " + methodName + "(", StringComparison.Ordinal);
        Assert.True(signature >= 0, methodName + " was not found.");
        int open = source.IndexOf('{', signature);
        int depth = 0;
        for (int index = open; index < source.Length; index++)
        {
            if (source[index] == '{')
            {
                depth++;
            }
            else if (source[index] == '}')
            {
                depth--;
                if (depth == 0)
                {
                    return source[open..(index + 1)];
                }
            }
        }

        throw new InvalidOperationException(methodName + " has an unbalanced body.");
    }
}
