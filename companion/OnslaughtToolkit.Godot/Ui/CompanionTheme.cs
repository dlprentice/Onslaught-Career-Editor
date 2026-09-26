// SPDX-License-Identifier: MIT
using Godot;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>The one owner of the companion's colors, type sizes and control styles.</summary>
internal static class CompanionTheme
{
    internal static readonly Color Background = new(0.043f, 0.063f, 0.09f);
    internal static readonly Color Accent = new(0.59f, 0.97f, 0.84f);
    internal static readonly Color Text = new(0.9f, 0.94f, 0.97f);
    internal static readonly Color Failure = new(1.0f, 0.72f, 0.65f);

    internal const int TitleSize = 32, SectionSize = 21, PageHeadingSize = 23, NoteSize = 14;

    internal static Theme Build()
    {
        StyleBoxFlat panel = Box(new Color(0.063f, 0.09f, 0.13f), 20, 16, 8);
        StyleBoxFlat button = Box(new Color(0.12f, 0.19f, 0.26f), 18, 11, 5);
        StyleBoxFlat hover = Box(new Color(0.19f, 0.31f, 0.39f), 18, 11, 5);
        StyleBoxFlat disabled = Box(new Color(0.1f, 0.13f, 0.17f), 18, 11, 5);
        StyleBoxFlat tab = Box(new Color(0.12f, 0.24f, 0.28f), 22, 12, 0);
        StyleBoxFlat field = Box(new Color(0.035f, 0.052f, 0.074f), 10, 8, 0);
        StyleBoxFlat focus = new() { BgColor = new Color(0, 0, 0, 0), BorderColor = new Color(0.45f, 0.89f, 0.79f) };
        focus.SetBorderWidthAll(2);
        focus.SetCornerRadiusAll(5);

        Theme theme = new() { DefaultFontSize = 17 };
        theme.SetColor("font_color", "Label", Text);
        theme.SetColor("font_color", "Button", new Color(0.94f, 0.97f, 0.99f));
        theme.SetColor("font_disabled_color", "Button", new Color(0.54f, 0.61f, 0.68f));
        theme.SetStylebox("normal", "Button", button);
        theme.SetStylebox("hover", "Button", hover);
        theme.SetStylebox("pressed", "Button", tab);
        theme.SetStylebox("focus", "Button", focus);
        theme.SetStylebox("disabled", "Button", disabled);
        theme.SetStylebox("panel", "PanelContainer", panel);
        theme.SetStylebox("panel", "TabContainer", panel);
        theme.SetStylebox("tab_selected", "TabContainer", tab);
        theme.SetStylebox("tab_unselected", "TabContainer", button);
        theme.SetColor("font_selected_color", "TabContainer", Accent);
        theme.SetColor("font_unselected_color", "TabContainer", new Color(0.86f, 0.9f, 0.94f));
        theme.SetStylebox("normal", "LineEdit", field);
        theme.SetStylebox("focus", "LineEdit", focus);
        theme.SetColor("default_color", "RichTextLabel", new Color(0.85f, 0.9f, 0.95f));
        theme.SetStylebox("panel", "Tree", field);
        theme.SetColor("font_color", "Tree", new Color(0.88f, 0.93f, 0.97f));
        theme.SetColor("font_selected_color", "Tree", Colors.White);
        return theme;
    }

    private static StyleBoxFlat Box(Color color, float horizontal, float vertical, int radius)
    {
        StyleBoxFlat box = new()
        {
            BgColor = color,
            ContentMarginLeft = horizontal, ContentMarginRight = horizontal,
            ContentMarginTop = vertical, ContentMarginBottom = vertical,
        };
        box.SetCornerRadiusAll(radius);
        return box;
    }
}
