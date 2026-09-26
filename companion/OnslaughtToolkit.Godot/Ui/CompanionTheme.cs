// SPDX-License-Identifier: MIT
using Godot;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>The Flight-deck palette David chose on 2026-09-25: near-black, amber actions, cyan data.</summary>
internal static class Palette
{
    internal static readonly Color Background = Color.FromHtml("0a0f14");
    internal static readonly Color Surface = Color.FromHtml("101820");
    internal static readonly Color Raised = Color.FromHtml("16222c");
    internal static readonly Color Hover = Color.FromHtml("1d2d3a");
    internal static readonly Color Field = Color.FromHtml("0c141b");
    internal static readonly Color Border = Color.FromHtml("21394a");
    internal static readonly Color Text = Color.FromHtml("dce8ef");
    internal static readonly Color Muted = Color.FromHtml("8ba3b3");
    internal static readonly Color Quote = Color.FromHtml("b9cad6");
    /// <summary>Small secondary text; at least 4.5:1 against every surface it sits on.</summary>
    internal static readonly Color Faint = Color.FromHtml("7e96a8");

    /// <summary>Text and icons of controls that cannot be used right now.</summary>
    internal static readonly Color Disabled = Color.FromHtml("5c7486");
    internal static readonly Color Accent = Color.FromHtml("f2a93b");
    internal static readonly Color AccentHover = Color.FromHtml("f7bf66");
    internal static readonly Color AccentText = Color.FromHtml("1a1204");
    internal static readonly Color Data = Color.FromHtml("56d3e6");
    internal static readonly Color Good = Color.FromHtml("6bd68f");
    internal static readonly Color Warn = Color.FromHtml("f2c14e");
    internal static readonly Color Bad = Color.FromHtml("ec6a5c");

    /// <summary>The game's own Goodie colours: gold for new, blue for viewed (Steam CFEPGoodies__Render).</summary>
    internal static readonly Color NewGold = Color.FromHtml("e8b54a");
    internal static readonly Color ViewedBlue = Color.FromHtml("5f8fe8");
}

/// <summary>
/// The one owner of the companion's type, spacing and control styles. Pages choose a type
/// variation by name (for example <c>ThemeTypeVariation = "Card"</c>) and never set colours of their own.
/// </summary>
internal static class CompanionTheme
{
    internal const int BodySize = 15;

    internal static Font HeadingFont { get; private set; } = null!;
    internal static Font StrongFont { get; private set; } = null!;
    internal static Font MonoFont { get; private set; } = null!;

    internal static Theme Build()
    {
        Font body = ThemeDB.FallbackFont;
        HeadingFont = Variation(body, embolden: 0.62f, spacing: 2);
        StrongFont = Variation(body, embolden: 0.45f, spacing: 0);
        SystemFont mono = new()
        {
            FontNames = ["JetBrains Mono", "DejaVu Sans Mono", "Liberation Mono", "Cascadia Mono", "Consolas", "Menlo", "monospace"],
            Fallbacks = [body],
        };
        MonoFont = mono;

        Theme theme = new() { DefaultFontSize = BodySize };
        Labels(theme);
        Buttons(theme);
        Toggles(theme);
        Fields(theme);
        Panels(theme);
        Lists(theme);
        Popups(theme);
        Bars(theme);
        GoodieCells(theme);
        return theme;
    }

    /// <summary>
    /// Goodie cells follow the game's own wall (CFEPGoodies__Render): new is gold, viewed is blue,
    /// locked and hint keep a dark interior, with a pale ring when the hint is shown.
    /// </summary>
    private static void GoodieCells(Theme theme)
    {
        GoodieCell(theme, "GoodieNew", Palette.NewGold, Palette.NewGold, 1, Palette.AccentText);
        // Dark numbers on the game's blue: white on it measures only 3.2:1.
        GoodieCell(theme, "GoodieViewed", Palette.ViewedBlue, Palette.ViewedBlue, 1, Palette.Background);
        GoodieCell(theme, "GoodieHint", Palette.Field, new Color(Palette.Text, 0.8f), 2, Palette.Text);
        GoodieCell(theme, "GoodieLocked", Palette.Field, Palette.Border, 1, Palette.Faint);
        GoodieCell(theme, "GoodieUnknown", Palette.Field, Palette.Bad, 2, Palette.Bad);
    }

    private static void GoodieCell(Theme theme, string name, Color fill, Color edge, int width, Color text)
    {
        theme.SetTypeVariation(name, "Button");
        StyleBoxFlat normal = Box(fill, 4, edge, width, padX: 2, padY: 2);
        StyleBoxFlat hover = Box(fill.Lightened(0.12f), 4, Palette.Text, width, padX: 2, padY: 2);
        StyleBoxFlat selected = Box(fill, 4, Palette.Accent, 3, padX: 2, padY: 2);
        theme.SetStylebox("normal", name, normal);
        theme.SetStylebox("hover", name, hover);
        theme.SetStylebox("pressed", name, selected);
        theme.SetStylebox("hover_pressed", name, selected);
        theme.SetStylebox("focus", name, Focus(4));
        theme.SetStylebox("disabled", name, normal);
        foreach (string color in new[] { "font_color", "font_hover_color", "font_pressed_color", "font_hover_pressed_color", "font_focus_color" })
            theme.SetColor(color, name, text);
        theme.SetFont("font", name, MonoFont);
        theme.SetFontSize("font_size", name, 10);
    }

    /// <summary>A flat box. Chamfered corners (corner detail 1) give the panels their cut-edge look.</summary>
    internal static StyleBoxFlat Box(Color fill, int radius = 0, Color? border = null, int borderWidth = 1,
        float padX = 0, float padY = 0, bool chamfer = true)
    {
        StyleBoxFlat box = new()
        {
            BgColor = fill, CornerDetail = chamfer ? 1 : 8, AntiAliasing = true,
            ContentMarginLeft = padX, ContentMarginRight = padX, ContentMarginTop = padY, ContentMarginBottom = padY,
        };
        box.SetCornerRadiusAll(radius);
        if (border is Color edge)
        {
            box.BorderColor = edge;
            box.SetBorderWidthAll(borderWidth);
        }
        return box;
    }

    private static FontVariation Variation(Font font, float embolden, int spacing)
    {
        FontVariation variation = new() { BaseFont = font, VariationEmbolden = embolden };
        variation.SetSpacing(TextServer.SpacingType.Glyph, spacing);
        return variation;
    }

    private static void Labels(Theme theme)
    {
        theme.SetColor("font_color", "Label", Palette.Text);
        LabelVariation(theme, "Title", 26, Palette.Text, HeadingFont);
        LabelVariation(theme, "HeroTitle", 34, Colors.White, HeadingFont);
        LabelVariation(theme, "HeroText", 16, new Color(Colors.White, 0.9f), null);
        LabelVariation(theme, "Lead", 16, Palette.Text, null);
        LabelVariation(theme, "CardTitle", 17, Palette.Text, StrongFont);
        LabelVariation(theme, "Section", 15, Palette.Text, HeadingFont);
        LabelVariation(theme, "Eyebrow", 11, Palette.Muted, Variation(ThemeDB.FallbackFont, 0.35f, 2));
        LabelVariation(theme, "StatValue", 26, Palette.Text, HeadingFont);
        LabelVariation(theme, "Strong", BodySize, Palette.Text, StrongFont);
        LabelVariation(theme, "Muted", 13, Palette.Muted, null);
        LabelVariation(theme, "Faint", 12, Palette.Faint, null);
        LabelVariation(theme, "Mono", 13, Palette.Text, MonoFont);
        LabelVariation(theme, "Accent", BodySize, Palette.Accent, StrongFont);
        LabelVariation(theme, "Data", BodySize, Palette.Data, StrongFont);
        LabelVariation(theme, "Good", 13, Palette.Good, null);
        LabelVariation(theme, "Warn", 13, Palette.Warn, null);
        LabelVariation(theme, "Bad", 13, Palette.Bad, null);
        LabelVariation(theme, "Brand", 19, Palette.Text, Variation(ThemeDB.FallbackFont, 0.7f, 3));
        LabelVariation(theme, "BrandSub", 11, Palette.Muted, Variation(ThemeDB.FallbackFont, 0.3f, 4));

        theme.SetColor("default_color", "RichTextLabel", Palette.Text);
        theme.SetColor("selection_color", "RichTextLabel", new Color(Palette.Accent, 0.35f));
        theme.SetFont("bold_font", "RichTextLabel", StrongFont);
        theme.SetFont("mono_font", "RichTextLabel", MonoFont);
        theme.SetFontSize("normal_font_size", "RichTextLabel", BodySize);
        theme.SetFontSize("bold_font_size", "RichTextLabel", BodySize);
        theme.SetFontSize("mono_font_size", "RichTextLabel", 13);
        theme.SetConstant("line_separation", "RichTextLabel", 3);
        // Slanted from the same face, so emphasis in the lore never falls back to another font.
        theme.SetFont("italics_font", "RichTextLabel", Slanted(ThemeDB.FallbackFont));
        theme.SetFont("bold_italics_font", "RichTextLabel", Slanted(StrongFont));
        theme.SetFontSize("italics_font_size", "RichTextLabel", BodySize);
        theme.SetFontSize("bold_italics_font_size", "RichTextLabel", BodySize);
        theme.SetColor("table_border", "RichTextLabel", Palette.Border);
        theme.SetColor("table_odd_row_bg", "RichTextLabel", new Color(Palette.Raised, 0.45f));
        theme.SetColor("table_even_row_bg", "RichTextLabel", new Color(0, 0, 0, 0));
    }

    private static FontVariation Slanted(Font font) =>
        new() { BaseFont = font, VariationTransform = new Transform2D(1, 0.2f, 0, 1, 0, 0) }; // Godot's documented slant: xy = 0.2.

    private static void LabelVariation(Theme theme, string name, int size, Color color, Font? font)
    {
        theme.SetTypeVariation(name, "Label");
        theme.SetFontSize("font_size", name, size);
        theme.SetColor("font_color", name, color);
        if (font is not null) theme.SetFont("font", name, font);
    }

    private static void Buttons(Theme theme)
    {
        ButtonStyles(theme, "Button", Palette.Raised, Palette.Hover, Palette.Border, Palette.Text);
        theme.SetColor("font_disabled_color", "Button", Palette.Disabled);
        theme.SetFont("font", "Button", StrongFont);
        theme.SetConstant("h_separation", "Button", 8);
        theme.SetConstant("icon_max_width", "Button", Icons.Size);
        IconColors(theme, "Button", Palette.Text, Palette.Text, Palette.Disabled);

        theme.SetTypeVariation("Primary", "Button");
        ButtonStyles(theme, "Primary", Palette.Accent, Palette.AccentHover, Palette.Accent, Palette.AccentText);
        IconColors(theme, "Primary", Palette.AccentText, Palette.AccentText, Palette.Disabled);

        // A write into the game folder: amber outline, never mistaken for an ordinary action.
        theme.SetTypeVariation("Caution", "Button");
        ButtonStyles(theme, "Caution", Palette.Surface, new Color(Palette.Warn, 0.14f), Palette.Warn, Palette.Warn);
        IconColors(theme, "Caution", Palette.Warn, Palette.Warn, Palette.Disabled);

        theme.SetTypeVariation("Nav", "Button");
        StyleBoxFlat nav = Box(new Color(0, 0, 0, 0), 6, padX: 14, padY: 8);
        StyleBoxFlat navHover = Box(Palette.Raised, 6, padX: 14, padY: 8);
        theme.SetStylebox("normal", "Nav", nav);
        theme.SetStylebox("hover", "Nav", navHover);
        theme.SetStylebox("pressed", "Nav", navHover);
        theme.SetStylebox("hover_pressed", "Nav", navHover);
        theme.SetStylebox("disabled", "Nav", nav);
        theme.SetStylebox("focus", "Nav", Focus(6));
        theme.SetColor("font_color", "Nav", Palette.Muted);
        theme.SetColor("font_hover_color", "Nav", Palette.Text);
        theme.SetColor("font_pressed_color", "Nav", Palette.Text);
        theme.SetColor("font_disabled_color", "Nav", Palette.Disabled);
        theme.SetFont("font", "Nav", ThemeDB.FallbackFont);
        theme.SetConstant("h_separation", "Nav", 12);
        IconColors(theme, "Nav", Palette.Muted, Palette.Text, Palette.Disabled);

        theme.SetTypeVariation("NavActive", "Button");
        StyleBoxFlat active = Box(Palette.Raised, 6, padX: 14, padY: 8);
        active.BorderColor = Palette.Accent;
        active.BorderWidthLeft = 3;
        foreach (string state in new[] { "normal", "hover", "pressed", "hover_pressed", "disabled" })
            theme.SetStylebox(state, "NavActive", active);
        theme.SetStylebox("focus", "NavActive", Focus(6));
        theme.SetColor("font_color", "NavActive", Palette.Text);
        theme.SetColor("font_hover_color", "NavActive", Palette.Text);
        theme.SetColor("font_pressed_color", "NavActive", Palette.Text);
        theme.SetFont("font", "NavActive", StrongFont);
        theme.SetConstant("h_separation", "NavActive", 12);
        IconColors(theme, "NavActive", Palette.Accent, Palette.Accent, Palette.Accent);

        // The fold-away group heading in the sidebar (Advanced).
        theme.SetTypeVariation("NavGroup", "Button");
        StyleBoxFlat group = Box(new Color(0, 0, 0, 0), 6, padX: 8, padY: 4);
        foreach (string state in new[] { "normal", "hover", "pressed", "hover_pressed", "disabled" })
            theme.SetStylebox(state, "NavGroup", state.StartsWith("hover") ? Box(Palette.Raised, 6, padX: 8, padY: 4) : group);
        theme.SetStylebox("focus", "NavGroup", Focus(6));
        foreach (string color in new[] { "font_color", "font_pressed_color", "font_focus_color" })
            theme.SetColor(color, "NavGroup", Palette.Faint);
        theme.SetColor("font_hover_color", "NavGroup", Palette.Muted);
        theme.SetColor("font_hover_pressed_color", "NavGroup", Palette.Muted);
        theme.SetFont("font", "NavGroup", Variation(ThemeDB.FallbackFont, 0.3f, 2));
        theme.SetFontSize("font_size", "NavGroup", 11);
        theme.SetConstant("icon_max_width", "NavGroup", 14);
        IconColors(theme, "NavGroup", Palette.Faint, Palette.Muted, Palette.Disabled);

        // A quiet text action inside cards.
        theme.SetTypeVariation("Link", "Button");
        StyleBoxEmpty none = new() { ContentMarginLeft = 2, ContentMarginRight = 2, ContentMarginTop = 2, ContentMarginBottom = 2 };
        foreach (string state in new[] { "normal", "hover", "pressed", "hover_pressed", "disabled" })
            theme.SetStylebox(state, "Link", none);
        theme.SetStylebox("focus", "Link", Focus(4));
        theme.SetColor("font_color", "Link", Palette.Data);
        theme.SetColor("font_hover_color", "Link", Palette.Text);
        theme.SetColor("font_pressed_color", "Link", Palette.Accent);
        theme.SetColor("font_disabled_color", "Link", Palette.Disabled);
    }

    private static void IconColors(Theme theme, string type, Color normal, Color hover, Color disabled)
    {
        theme.SetColor("icon_normal_color", type, normal);
        theme.SetColor("icon_focus_color", type, normal);
        theme.SetColor("icon_pressed_color", type, hover);
        theme.SetColor("icon_hover_color", type, hover);
        theme.SetColor("icon_hover_pressed_color", type, hover);
        theme.SetColor("icon_disabled_color", type, disabled);
    }

    private static void ButtonStyles(Theme theme, string type, Color fill, Color hover, Color border, Color text)
    {
        theme.SetStylebox("normal", type, Box(fill, 6, border, padX: 16, padY: 9));
        theme.SetStylebox("hover", type, Box(hover, 6, border, padX: 16, padY: 9));
        theme.SetStylebox("pressed", type, Box(hover, 6, Palette.Accent, padX: 16, padY: 9));
        theme.SetStylebox("hover_pressed", type, Box(hover, 6, Palette.Accent, padX: 16, padY: 9));
        theme.SetStylebox("disabled", type, Box(Palette.Surface, 6, Palette.Raised, padX: 16, padY: 9));
        theme.SetStylebox("focus", type, Focus(6));
        theme.SetColor("font_color", type, text);
        theme.SetColor("font_hover_color", type, text);
        theme.SetColor("font_pressed_color", type, text);
        theme.SetColor("font_hover_pressed_color", type, text);
        theme.SetColor("font_focus_color", type, text);
        theme.SetColor("font_disabled_color", type, Palette.Disabled);
    }

    private static StyleBoxFlat Focus(int radius)
    {
        StyleBoxFlat focus = Box(new Color(0, 0, 0, 0), radius, Palette.Accent, borderWidth: 2);
        focus.DrawCenter = false;
        return focus;
    }

    private static void Toggles(Theme theme)
    {
        // Identical margins in every state, so checking a box never moves its row.
        StyleBoxEmpty flat = new() { ContentMarginLeft = 4, ContentMarginRight = 8, ContentMarginTop = 4, ContentMarginBottom = 4 };
        StyleBoxFlat hover = Box(Palette.Raised, 6, padX: 4, padY: 4);
        hover.ContentMarginRight = 8;
        foreach (string type in new[] { "CheckBox", "CheckButton" })
        {
            foreach (string state in new[] { "normal", "pressed", "disabled" })
                theme.SetStylebox(state, type, flat);
            theme.SetStylebox("hover", type, hover);
            theme.SetStylebox("hover_pressed", type, hover);
            theme.SetStylebox("focus", type, Focus(6));
            theme.SetColor("font_color", type, Palette.Text);
            theme.SetColor("font_hover_color", type, Palette.Text);
            theme.SetColor("font_pressed_color", type, Palette.Text);
            theme.SetColor("font_hover_pressed_color", type, Palette.Text);
            theme.SetColor("font_disabled_color", type, Palette.Disabled);
            theme.SetConstant("h_separation", type, 8);
        }
        theme.SetIcon("unchecked", "CheckBox", CheckIcon(checkedState: false, enabled: true));
        theme.SetIcon("checked", "CheckBox", CheckIcon(checkedState: true, enabled: true));
        theme.SetIcon("unchecked_disabled", "CheckBox", CheckIcon(checkedState: false, enabled: false));
        theme.SetIcon("checked_disabled", "CheckBox", CheckIcon(checkedState: true, enabled: false));
        theme.SetIcon("radio_unchecked", "CheckBox", RadioIcon(selected: false, enabled: true));
        theme.SetIcon("radio_checked", "CheckBox", RadioIcon(selected: true, enabled: true));
        theme.SetIcon("radio_unchecked_disabled", "CheckBox", RadioIcon(selected: false, enabled: false));
        theme.SetIcon("radio_checked_disabled", "CheckBox", RadioIcon(selected: true, enabled: false));
    }

    /// <summary>An 18-pixel radio choice drawn in code: an outlined ring with an amber centre when chosen.</summary>
    private static ImageTexture RadioIcon(bool selected, bool enabled)
    {
        const int size = 18;
        Image image = Image.CreateEmpty(size, size, false, Image.Format.Rgba8);
        Color edge = enabled ? (selected ? Palette.Accent : Palette.Muted) : Palette.Border;
        Vector2 centre = new(size / 2f - 0.5f, size / 2f - 0.5f);
        for (int y = 0; y < size; y++)
        {
            for (int x = 0; x < size; x++)
            {
                float distance = new Vector2(x, y).DistanceTo(centre);
                // Soft edges: blend by distance so the ring reads as round at icon size.
                float ring = Mathf.Clamp(1.5f - Mathf.Abs(distance - 7.5f), 0f, 1f);
                float dot = selected ? Mathf.Clamp(4.5f - distance, 0f, 1f) : 0f;
                float field = Mathf.Clamp(7.5f - distance, 0f, 1f);
                Color color = new(Palette.Field, field);
                if (dot > 0) color = color.Lerp(enabled ? Palette.Accent : Palette.Border, dot) with { A = Mathf.Max(field, dot) };
                if (ring > 0) color = color.Lerp(edge, ring) with { A = Mathf.Max(color.A, ring) };
                image.SetPixel(x, y, color);
            }
        }
        return ImageTexture.CreateFromImage(image);
    }

    /// <summary>An 18-pixel check box drawn in code: an outlined square, amber-filled with a dark tick when checked.</summary>
    private static ImageTexture CheckIcon(bool checkedState, bool enabled)
    {
        const int size = 18;
        Image image = Image.CreateEmpty(size, size, false, Image.Format.Rgba8);
        Color edge = enabled ? (checkedState ? Palette.Accent : Palette.Muted) : Palette.Border;
        Color fill = checkedState ? (enabled ? Palette.Accent : Palette.Border) : Palette.Field;
        for (int y = 0; y < size; y++)
        {
            for (int x = 0; x < size; x++)
            {
                // A 1-pixel chamfer on each corner keeps the Flight-deck edge at icon size.
                bool corner = (x == 0 || x == size - 1) && (y == 0 || y == size - 1);
                bool border = x <= 1 || y <= 1 || x >= size - 2 || y >= size - 2;
                image.SetPixel(x, y, corner ? new Color(0, 0, 0, 0) : border ? edge : fill);
            }
        }
        if (checkedState)
        {
            Color tick = enabled ? Palette.AccentText : Palette.Disabled;
            (int X, int Y)[] strokes = [(4, 9), (5, 10), (6, 11), (7, 12), (8, 11), (9, 10), (10, 9), (11, 8), (12, 7), (13, 6)];
            foreach ((int x, int y) in strokes)
            {
                image.SetPixel(x, y, tick);
                image.SetPixel(x, y + 1, tick);
            }
        }
        return ImageTexture.CreateFromImage(image);
    }

    private static void Fields(Theme theme)
    {
        StyleBoxFlat field = Box(Palette.Field, 6, Palette.Border, padX: 10, padY: 7);
        StyleBoxFlat focused = Box(Palette.Field, 6, Palette.Accent, padX: 10, padY: 7);
        StyleBoxFlat readOnly = Box(Palette.Surface, 6, Palette.Raised, padX: 10, padY: 7);
        theme.SetStylebox("normal", "LineEdit", field);
        theme.SetStylebox("focus", "LineEdit", focused);
        theme.SetStylebox("read_only", "LineEdit", readOnly);
        theme.SetColor("font_color", "LineEdit", Palette.Text);
        theme.SetColor("font_uneditable_color", "LineEdit", Palette.Muted);
        theme.SetColor("font_placeholder_color", "LineEdit", Palette.Faint);
        theme.SetColor("caret_color", "LineEdit", Palette.Accent);
        theme.SetColor("selection_color", "LineEdit", new Color(Palette.Accent, 0.35f));
        theme.SetColor("font_selected_color", "LineEdit", Palette.Text);

        theme.SetTypeVariation("MonoField", "LineEdit");
        theme.SetFont("font", "MonoField", MonoFont);
        theme.SetFontSize("font_size", "MonoField", 13);

        ButtonStyles(theme, "OptionButton", Palette.Field, Palette.Raised, Palette.Border, Palette.Text);
        theme.SetConstant("arrow_margin", "OptionButton", 10);

        StyleBoxFlat slider = Box(Palette.Raised, 3, padY: 3);
        StyleBoxFlat filled = Box(Palette.Accent, 3, padY: 3);
        theme.SetStylebox("slider", "HSlider", slider);
        theme.SetStylebox("grabber_area", "HSlider", filled);
        theme.SetStylebox("grabber_area_highlight", "HSlider", Box(Palette.AccentHover, 3, padY: 3));
    }

    private static void Panels(Theme theme)
    {
        theme.SetStylebox("panel", "PanelContainer", new StyleBoxEmpty());
        PanelVariation(theme, "Card", Box(Palette.Surface, 10, Palette.Border, padX: 18, padY: 16));
        PanelVariation(theme, "Inset", Box(Palette.Raised, 8, padX: 14, padY: 12));
        PanelVariation(theme, "Sidebar", SideBorder(Palette.Surface, right: true));
        PanelVariation(theme, "StatusBar", SideBorder(Palette.Surface, top: true));
        PanelVariation(theme, "Notice", Callout(Palette.Data));
        PanelVariation(theme, "CautionNotice", Callout(Palette.Warn));
        PanelVariation(theme, "FailureNotice", Callout(Palette.Bad));
        PanelVariation(theme, "SuccessNotice", Callout(Palette.Good));
        // The banner frames the game's own art; its content is clipped to the rounded frame.
        PanelVariation(theme, "Hero", Box(Palette.Surface, 12, Palette.Border));
        // A choice in a dialog: raised, and outlined in amber when it is the chosen one.
        PanelVariation(theme, "Choice", Box(Palette.Raised, 8, Palette.Border, padX: 14, padY: 12));
        PanelVariation(theme, "ChoiceChosen", Box(Palette.Raised.Blend(new Color(Palette.Accent, 0.08f)), 8, Palette.Accent, padX: 14, padY: 12));
        // Unsaved changes under a page: raised, outlined in amber like the save it leads to.
        PanelVariation(theme, "ChangesBar", Box(Palette.Raised, 8, Palette.Accent, padX: 16, padY: 10));
        theme.SetStylebox("separator", "HSeparator", new StyleBoxLine { Color = Palette.Border, Thickness = 1 });
        theme.SetConstant("separation", "HSeparator", 12);
    }

    private static void PanelVariation(Theme theme, string name, StyleBox style)
    {
        theme.SetTypeVariation(name, "PanelContainer");
        theme.SetStylebox("panel", name, style);
    }

    private static StyleBoxFlat SideBorder(Color fill, bool right = false, bool top = false)
    {
        StyleBoxFlat box = Box(fill, 0, chamfer: false);
        box.BorderColor = Palette.Border;
        if (right) box.BorderWidthRight = 1;
        if (top) box.BorderWidthTop = 1;
        return box;
    }

    private static StyleBoxFlat Callout(Color edge)
    {
        StyleBoxFlat box = Box(Palette.Raised, 6, padX: 14, padY: 10);
        box.BorderColor = edge;
        box.BorderWidthLeft = 3;
        return box;
    }

    private static void Lists(Theme theme)
    {
        theme.SetStylebox("panel", "Tree", Box(Palette.Field, 8, Palette.Border, padX: 4, padY: 4));
        theme.SetStylebox("focus", "Tree", new StyleBoxEmpty());
        StyleBoxFlat selected = Box(Palette.Hover, 4, chamfer: false);
        selected.BorderColor = Palette.Accent;
        selected.BorderWidthLeft = 2;
        theme.SetStylebox("selected", "Tree", selected);
        theme.SetStylebox("selected_focus", "Tree", selected);
        theme.SetStylebox("cursor", "Tree", new StyleBoxEmpty());
        theme.SetStylebox("cursor_unfocused", "Tree", new StyleBoxEmpty());
        StyleBoxFlat header = Box(Palette.Raised, 0, padX: 8, padY: 6, chamfer: false);
        theme.SetStylebox("title_button_normal", "Tree", header);
        theme.SetStylebox("title_button_hover", "Tree", header);
        theme.SetStylebox("title_button_pressed", "Tree", header);
        theme.SetColor("title_button_color", "Tree", Palette.Muted);
        theme.SetFont("title_button_font", "Tree", Variation(ThemeDB.FallbackFont, 0.35f, 1));
        theme.SetFontSize("title_button_font_size", "Tree", 12);
        theme.SetColor("font_color", "Tree", Palette.Text);
        theme.SetColor("font_selected_color", "Tree", Palette.Text);
        theme.SetColor("guide_color", "Tree", new Color(Palette.Border, 0.6f));
        theme.SetColor("relationship_line_color", "Tree", Palette.Border);
        theme.SetConstant("v_separation", "Tree", 6);
        theme.SetConstant("h_separation", "Tree", 10);
        theme.SetConstant("item_margin", "Tree", 18);
        theme.SetConstant("draw_guides", "Tree", 1);
        theme.SetFontSize("font_size", "Tree", 14);
    }

    private static void Popups(Theme theme)
    {
        StyleBoxFlat menu = Box(Palette.Surface, 6, Palette.Border, padX: 6, padY: 6);
        theme.SetStylebox("panel", "PopupMenu", menu);
        theme.SetStylebox("hover", "PopupMenu", Box(Palette.Hover, 4, chamfer: false));
        theme.SetColor("font_color", "PopupMenu", Palette.Text);
        theme.SetColor("font_hover_color", "PopupMenu", Palette.Text);
        theme.SetColor("font_disabled_color", "PopupMenu", Palette.Disabled);
        theme.SetConstant("v_separation", "PopupMenu", 8);

        theme.SetStylebox("panel", "TooltipPanel", Box(Palette.Raised, 6, Palette.Border, padX: 10, padY: 7));
        theme.SetColor("font_color", "TooltipLabel", Palette.Text);
        theme.SetFontSize("font_size", "TooltipLabel", 13);

        StyleBoxFlat window = Box(Palette.Surface, 10, Palette.Border, padX: 0, padY: 0);
        window.ExpandMarginTop = 32;
        window.ExpandMarginLeft = window.ExpandMarginRight = window.ExpandMarginBottom = 6;
        theme.SetStylebox("embedded_border", "Window", window);
        theme.SetStylebox("embedded_unfocused_border", "Window", window);
        theme.SetColor("title_color", "Window", Palette.Text);
        theme.SetFont("title_font", "Window", StrongFont);
        theme.SetStylebox("panel", "AcceptDialog", Box(Palette.Surface, 0, padX: 14, padY: 12, chamfer: false));
    }

    private static void Bars(Theme theme)
    {
        foreach (string type in new[] { "VScrollBar", "HScrollBar" })
        {
            theme.SetStylebox("scroll", type, Box(new Color(0, 0, 0, 0), 4, padX: 3, padY: 3, chamfer: false));
            theme.SetStylebox("scroll_focus", type, Box(new Color(0, 0, 0, 0), 4, padX: 3, padY: 3, chamfer: false));
            theme.SetStylebox("grabber", type, Box(Palette.Border, 4, chamfer: false));
            theme.SetStylebox("grabber_highlight", type, Box(Palette.Faint, 4, chamfer: false));
            theme.SetStylebox("grabber_pressed", type, Box(Palette.Muted, 4, chamfer: false));
        }
        theme.SetStylebox("background", "ProgressBar", Box(Palette.Raised, 3, chamfer: false));
        theme.SetStylebox("fill", "ProgressBar", Box(Palette.Data, 3, chamfer: false));
        theme.SetTypeVariation("AccentBar", "ProgressBar");
        theme.SetStylebox("fill", "AccentBar", Box(Palette.Accent, 3, chamfer: false));
    }
}
