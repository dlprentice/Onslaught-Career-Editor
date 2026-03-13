using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Xml.Linq;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

public class ThemeContrastAuditTests
{
    private static string AppXamlPath => Path.Combine(TestFixturePaths.RepoRoot, "archive", "legacy-wpf", "App.xaml");
    private static string MainWindowXamlPath => Path.Combine(TestFixturePaths.RepoRoot, "archive", "legacy-wpf", "MainWindow.xaml");

    private static void RequireLegacyWpfSurface()
    {
        if (!File.Exists(AppXamlPath) || !File.Exists(MainWindowXamlPath))
        {
            Assert.Ignore("Legacy WPF surface is not present in this tree.");
        }
    }

    [Test]
    [Category("LegacyWpf")]
    public void ThemeColors_MeetMinimumContrastThresholds()
    {
        RequireLegacyWpfSurface();
        var colors = LoadNamedBrushColors(AppXamlPath);

        AssertContrast(colors, "PrimaryTextBrush", "SurfaceBrush", minRatio: 7.0);
        AssertContrast(colors, "MutedTextBrush", "SurfaceBrush", minRatio: 4.5);
        AssertContrast(colors, "AccentDarkBrush", "SurfaceMutedBrush", minRatio: 4.5);
        AssertContrast(colors, "AccentBrush", "SurfaceBrush", minRatio: 3.0);
        AssertContrast(colors, "DangerBrush", "SurfaceBrush", minRatio: 4.5);
    }

    [Test]
    [Category("LegacyWpf")]
    public void AppXaml_UsesMaterialDesignTheme()
    {
        RequireLegacyWpfSurface();
        string xaml = File.ReadAllText(AppXamlPath);
        Assert.That(xaml, Does.Contain("materialDesign:BundledTheme"));
        Assert.That(xaml, Does.Contain("MaterialDesign3.Defaults.xaml"));
        Assert.That(xaml, Does.Contain("MaterialDesignRaisedButton"));
        Assert.That(xaml, Does.Contain("MaterialDesignFlatButton"));
        Assert.That(xaml, Does.Contain("MaterialDesignRaisedButton"));
    }

    [Test]
    [Category("LegacyWpf")]
    public void PrimaryButtonStyle_UsesMaterialDesignRaisedButton()
    {
        RequireLegacyWpfSurface();
        string xaml = File.ReadAllText(AppXamlPath);
        Assert.That(xaml, Does.Contain("x:Key=\"PrimaryButtonStyle\""));
        Assert.That(xaml, Does.Contain("MaterialDesignRaisedButton"));
    }

    [Test]
    [Category("LegacyWpf")]
    public void MainWindow_DefinesAboutTab()
    {
        RequireLegacyWpfSurface();
        string xaml = File.ReadAllText(MainWindowXamlPath);
        Assert.That(xaml, Does.Contain("Header=\"About\""));
        Assert.That(xaml, Does.Contain("<views:AboutView/>"));
    }

    [Test]
    [Category("LegacyWpf")]
    public void MainWindow_UsesMaterialDesignNamespace()
    {
        RequireLegacyWpfSurface();
        string xaml = File.ReadAllText(MainWindowXamlPath);
        Assert.That(xaml, Does.Contain("xmlns:materialDesign"));
    }

    private static Dictionary<string, string> LoadNamedBrushColors(string xamlPath)
    {
        string content = File.ReadAllText(xamlPath);
        var result = new Dictionary<string, string>(StringComparer.Ordinal);

        var brushPattern = new Regex(
            @"<SolidColorBrush\s+x:Key=""(?<key>[^""]+)""\s+Color=""(?<color>#[0-9A-Fa-f]{6,8})""",
            RegexOptions.Compiled);

        foreach (Match m in brushPattern.Matches(content))
        {
            result[m.Groups["key"].Value] = m.Groups["color"].Value;
        }

        return result;
    }

    private static void AssertContrast(IReadOnlyDictionary<string, string> colors, string leftKeyOrHex, string rightKeyOrHex, double minRatio)
    {
        var left = ResolveColor(colors, leftKeyOrHex);
        var right = ResolveColor(colors, rightKeyOrHex);
        double ratio = ContrastRatio(left, right);

        Assert.That(
            ratio,
            Is.GreaterThanOrEqualTo(minRatio),
            $"{leftKeyOrHex} vs {rightKeyOrHex} contrast ratio {ratio:F2} is below required {minRatio:F2}");
    }

    private static (double R, double G, double B) ResolveColor(IReadOnlyDictionary<string, string> colors, string keyOrHex)
    {
        if (keyOrHex.StartsWith("#", StringComparison.Ordinal))
        {
            return ParseHexColor(keyOrHex);
        }

        Assert.That(colors.ContainsKey(keyOrHex), Is.True, $"Missing brush key: {keyOrHex}");
        return ParseHexColor(colors[keyOrHex]);
    }

    private static (double R, double G, double B) ParseHexColor(string hex)
    {
        string normalized = hex.Trim();
        if (normalized.StartsWith("#", StringComparison.Ordinal))
        {
            normalized = normalized[1..];
        }

        if (normalized.Length == 8)
        {
            normalized = normalized[2..];
        }

        if (normalized.Length != 6)
        {
            throw new InvalidOperationException($"Unsupported color format: #{normalized}");
        }

        byte r = byte.Parse(normalized.Substring(0, 2), NumberStyles.HexNumber, CultureInfo.InvariantCulture);
        byte g = byte.Parse(normalized.Substring(2, 2), NumberStyles.HexNumber, CultureInfo.InvariantCulture);
        byte b = byte.Parse(normalized.Substring(4, 2), NumberStyles.HexNumber, CultureInfo.InvariantCulture);
        return (r / 255.0, g / 255.0, b / 255.0);
    }

    private static double ContrastRatio((double R, double G, double B) a, (double R, double G, double B) b)
    {
        double l1 = RelativeLuminance(a);
        double l2 = RelativeLuminance(b);
        double lighter = Math.Max(l1, l2);
        double darker = Math.Min(l1, l2);
        return (lighter + 0.05) / (darker + 0.05);
    }

    private static double RelativeLuminance((double R, double G, double B) c)
    {
        static double Transform(double channel)
            => channel <= 0.03928 ? channel / 12.92 : Math.Pow((channel + 0.055) / 1.055, 2.4);

        double r = Transform(c.R);
        double g = Transform(c.G);
        double b = Transform(c.B);
        return 0.2126 * r + 0.7152 * g + 0.0722 * b;
    }
}
