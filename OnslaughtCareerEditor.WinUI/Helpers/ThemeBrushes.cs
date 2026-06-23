using Microsoft.UI;
using Microsoft.UI.Xaml.Media;

namespace OnslaughtCareerEditor.WinUI.Helpers;

internal static class ThemeBrushes
{
    public static SolidColorBrush Success()
        => Create(0x71, 0xD2, 0x8F);

    public static SolidColorBrush Warning()
        => Create(0xE0, 0xB8, 0x4B);

    public static SolidColorBrush Danger()
        => Create(0xE4, 0x6B, 0x6B);

    private static SolidColorBrush Create(byte red, byte green, byte blue)
        => new(ColorHelper.FromArgb(0xFF, red, green, blue));
}
