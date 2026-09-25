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
        AssertRectangle("Dialog/Panel", "rectangle", RetailFeMessBox.QuitLeft,
            RetailFeMessBox.BoxTop, RetailFeMessBox.QuitWidth, RetailFeMessBox.ReconstructionHeight);
        Assert.Equal(new[] { RetailFeMessBox.QuitCenterX, RetailFeMessBox.PromptTop },
            NativeMainMenuSource.Vector(NativeQuitSource.Node("Dialog/Prompt"), "source_anchor", "Vector2"));
        Assert.Contains("Stage/QuitConfirm", NativeFrontendSource.PageFunction("_configure_quit"));
        Assert.DoesNotContain("new Rect2(70f, 160f, 500f, 140f)", NativeQuitSource.Presentation);
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
        float x = RetailFeMessBox.QuitLeft, y = RetailFeMessBox.BoxTop;
        float width = RetailFeMessBox.QuitWidth, height = RetailFeMessBox.ReconstructionHeight;
        float line = RetailFeMessBox.BoxLineWidth;
        AssertRectangle("Dialog/BorderTop", "rectangle", x, y, width, line);
        AssertRectangle("Dialog/BorderBottom", "rectangle", x, y + height - line, width, line);
        AssertRectangle("Dialog/BorderLeft", "rectangle", x, y, line, height);
        AssertRectangle("Dialog/BorderRight", "rectangle", x + width - line, y, line, height);
        AssertColor("Dialog/Panel", RetailFeMessBox.PanelColor);
        foreach (string edge in new[] { "Top", "Bottom", "Left", "Right" })
            AssertColor("Dialog/Border" + edge, RetailFeMessBox.BorderColor);
        foreach (string row in new[] { "Yes", "No" })
            AssertColor("Dialog/" + row + "/Highlight", RetailFeMessBox.HighlightColor);
        Assert.Contains("text = \"" + RetailFeMessBox.YesLabel + "\"", NativeQuitSource.Node("Dialog/Yes/Label"));
        Assert.Contains("text = \"" + RetailFeMessBox.NoLabel + "\"", NativeQuitSource.Node("Dialog/No/Label"));
        Assert.Contains("res://Assets/PauseMenu/blank.texture.aya", NativeQuitSource.Scene);
        Assert.Contains("dimensions = Vector2i(16, 16)", NativeQuitSource.Scene);
        Assert.Contains("compression = 0", NativeQuitSource.Scene);
        Assert.Contains("ink_color: Color = Color.WHITE", NativeQuitSource.Read("quit_confirm_label.gd"));
        Assert.DoesNotContain("new Color(0f, 0f, 0f, 0.82f)", NativeQuitSource.Presentation);
    }

    [Fact]
    public void QuitConfirmHitRowsAreTheFullWidthYesNoStack()
    {
        AssertRectangle("Dialog/No", "hit_rect", RetailFeMessBox.QuitLeft,
            RetailFeMessBox.NoChoiceTop, RetailFeMessBox.QuitWidth, RetailFeMessBox.ChoiceRowHeight);
        AssertRectangle("Dialog/Yes", "hit_rect", RetailFeMessBox.QuitLeft,
            RetailFeMessBox.YesChoiceTop, RetailFeMessBox.QuitWidth, RetailFeMessBox.ChoiceRowHeight);
        Assert.Contains("get_node(\"Stage/QuitConfirm\").hit_test(design)", NativeFrontendSource.RootFunction("quit_confirm_index_at"));
        Assert.Contains("hit_rect.has_point(", NativeQuitSource.Read("quit_confirm_row.gd"));
        Assert.Contains("\"selected_index\": session.get_selected_quit_confirm_index()", NativeQuitSource.Bridge);
        Assert.DoesNotContain(".confirm(", NativeQuitSource.Bridge);
        Assert.DoesNotContain("get_tree().quit", NativeQuitSource.Presentation);
    }

    [Fact]
    public void QuitConfirmUpSelectsYesAndDownSelectsNo()
    {
        // CFrontEnd__HandleModalPanelButton 0x0044dd60 option_mode 2:
        // BUTTON_FRONTEND_MENU_UP 0x2a writes this+0x1fa0 = 1 (Yes, upper);
        // DOWN 0x2b writes 0 (No, lower). PCController maps KEYCODE_UP/DOWN
        // onto those buttons. Session law stays 0=No / 1=Yes; Left/Right keep
        // MovePrevious / MoveNext.
        Assert.Equal(1, RetailFeMessBox.YesChoiceIndex);
        Assert.Equal(0, RetailFeMessBox.DefaultChoiceIndex);

        string handleKey = NativeFrontendSource.RootFunction("handle_key");
        int quit = handleKey.IndexOf("if _session.get_screen() == Frontend.Screen.QUIT_CONFIRM:", StringComparison.Ordinal);
        Assert.True(quit >= 0, "handle_key must special-case QuitConfirm.");
        string quitArm = handleKey[quit..];
        int sharedUpLeft = quitArm.IndexOf("if is_key(key, KEY_UP) or is_key(key, KEY_LEFT):", StringComparison.Ordinal);
        Assert.True(sharedUpLeft > 0, "The shared Up/Left arm must follow the QuitConfirm split.");
        string beforeShared = quitArm[..sharedUpLeft];
        Assert.Contains("if is_key(key, KEY_UP): return _handled(_move_selection(_session.select_quit_confirm_index(1)))", beforeShared);
        Assert.Contains("if is_key(key, KEY_DOWN): return _handled(_move_selection(_session.select_quit_confirm_index(0)))", beforeShared);
        Assert.DoesNotContain("is_key(key, KEY_LEFT)", beforeShared);
        Assert.DoesNotContain("is_key(key, KEY_RIGHT)", beforeShared);
        Assert.Contains("is_key(key, KEY_LEFT)", handleKey);
        Assert.Contains("_session.move_previous()", handleKey);
        Assert.Contains("is_key(key, KEY_RIGHT)", handleKey);
        Assert.Contains("_session.move_next()", handleKey);
    }

    private static void AssertRectangle(string node, string property, params float[] values) =>
        Assert.Equal(values, NativeMainMenuSource.Vector(NativeQuitSource.Node(node), property, "Rect2"));

    private static void AssertColor(string node, uint argb) => NativeQuitSource.HasColor(node, argb);

}
