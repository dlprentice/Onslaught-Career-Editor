// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// Readability of the built theme: every label colour against every surface labels sit on, the Goodie
/// cells' numbers against their fills, and the amber buttons' text, each at least 4.5:1 (WCAG 2's
/// contrast for normal-size text). The banner's words sit on the game's art under a shade and are not
/// measured here.
/// </summary>
internal static class ThemeTests
{
    private const double Readable = 4.5;

    internal static void Run(Checks check)
    {
        check.Suite("theme");
        Theme theme = CompanionTheme.Build();
        (string Name, Color Fill)[] surfaces =
        [
            ("the page", Palette.Background), ("a card", Fill(theme, "Card")), ("an inset panel", Fill(theme, "Inset")),
            ("a notice", Fill(theme, "Notice")), ("a chosen choice", Fill(theme, "ChoiceChosen")), ("a list", Palette.Field),
        ];
        string[] labels = theme.GetTypeVariationList("Label").Where(name => !name.StartsWith("Hero", StringComparison.Ordinal)).ToArray();
        check.That(labels.Length >= 15, "the theme defines the label styles the pages use");
        foreach (string label in labels)
        {
            Color text = theme.GetColor("font_color", label);
            (string surface, double ratio) = surfaces.Select(pair => (pair.Name, Contrast(text, pair.Fill))).MinBy(pair => pair.Item2);
            check.That(text.A >= 1f && ratio >= Readable, $"{label} text is readable on {surface} ({ratio:0.00}:1)");
        }
        foreach (string cell in new[] { "GoodieNew", "GoodieViewed", "GoodieHint", "GoodieLocked", "GoodieUnknown" })
        {
            double ratio = Contrast(theme.GetColor("font_color", cell), ((StyleBoxFlat)theme.GetStylebox("normal", cell)).BgColor);
            check.That(ratio >= Readable, $"{cell} numbers are readable ({ratio:0.00}:1)");
        }
        double primary = Contrast(theme.GetColor("font_color", "Primary"), ((StyleBoxFlat)theme.GetStylebox("normal", "Primary")).BgColor);
        check.That(primary >= Readable, $"text on amber buttons is readable ({primary:0.00}:1)");
    }

    private static Color Fill(Theme theme, string panel) => ((StyleBoxFlat)theme.GetStylebox("panel", panel)).BgColor;

    private static double Contrast(Color a, Color b)
    {
        double light = Math.Max(Luminance(a), Luminance(b)), dark = Math.Min(Luminance(a), Luminance(b));
        return (light + 0.05) / (dark + 0.05);
    }

    private static double Luminance(Color color) => 0.2126 * Channel(color.R) + 0.7152 * Channel(color.G) + 0.0722 * Channel(color.B);

    private static double Channel(float value) => value <= 0.03928 ? value / 12.92 : Math.Pow((value + 0.055) / 1.055, 2.4);
}
