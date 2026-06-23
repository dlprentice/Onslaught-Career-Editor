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
    private static string WinUiAppXamlPath => Path.Combine(TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "App.xaml");
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
    public void WinUiApp_DefaultsToLightThemeForPrimaryProductLaunch()
    {
        XDocument document = XDocument.Load(WinUiAppXamlPath);
        string? requestedTheme = document.Root?.Attribute("RequestedTheme")?.Value;

        Assert.That(
            requestedTheme,
            Is.EqualTo("Light"),
            "The primary WinUI product should launch in the calmer light theme by default; dark resources may remain available, but forced dark launch chrome made broad visual QA read heavier than intended.");
    }

    [Test]
    public void WinUiShellThemeColors_MeetMinimumContrastThresholds()
    {
        var themes = LoadWinUiThemeBrushColors(WinUiAppXamlPath);

        foreach (string themeName in new[] { "Default", "Dark", "Light" })
        {
            Assert.That(themes.ContainsKey(themeName), Is.True, $"Missing WinUI theme dictionary: {themeName}");
            IReadOnlyDictionary<string, string> colors = themes[themeName];

            AssertContrast(colors, "ShellTextBrush", "ShellSurfaceBrush", minRatio: 7.0);
            AssertContrast(colors, "ShellTextBrush", "ShellPageBrush", minRatio: 7.0);
            AssertContrast(colors, "ShellTextBrush", "ShellMetricSurfaceBrush", minRatio: 7.0);
            AssertContrast(colors, "ShellMutedTextBrush", "ShellSurfaceBrush", minRatio: 4.5);
            AssertContrast(colors, "ShellMutedTextBrush", "ShellMutedSurfaceBrush", minRatio: 4.5);
            AssertContrast(colors, "ShellHeroTextBrush", "ShellHeroBrush", minRatio: 4.5);
            AssertContrast(colors, "ShellHeroTextBrush", "ShellAccentBrush", minRatio: 4.5);
            AssertContrast(colors, "ShellAccentBrush", "ShellSurfaceBrush", minRatio: 3.0);
            AssertContrast(colors, "ShellAccentBrush", "ShellPageBrush", minRatio: 3.0);
        }
    }

    [Test]
    public void WinUiPages_UseNamedThemeResourcesInsteadOfRawHexColors()
    {
        string pagesRoot = Path.Combine(TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages");
        var rawColorPattern = new Regex(@"=""#[0-9A-Fa-f]{6,8}""", RegexOptions.Compiled);
        List<string> offenders = [];

        foreach (string xamlPath in Directory.GetFiles(pagesRoot, "*.xaml", SearchOption.AllDirectories))
        {
            string relativePath = Path.GetRelativePath(TestFixturePaths.RepoRoot, xamlPath);
            string[] lines = File.ReadAllLines(xamlPath);
            for (int i = 0; i < lines.Length; i++)
            {
                if (rawColorPattern.IsMatch(lines[i]))
                {
                    offenders.Add($"{relativePath}:{i + 1}: {lines[i].Trim()}");
                }
            }
        }

        Assert.That(
            offenders,
            Is.Empty,
            "Active WinUI pages should use named theme resources for colors so contrast and visual QA stay centralized.");
    }

    [Test]
    public void WinUiPages_DoNotUseHeroButtonStyleInsideCardSurfaces()
    {
        string pagesRoot = Path.Combine(TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages");
        List<string> offenders = [];

        foreach (string xamlPath in Directory.GetFiles(pagesRoot, "*.xaml", SearchOption.AllDirectories))
        {
            string relativePath = Path.GetRelativePath(TestFixturePaths.RepoRoot, xamlPath);
            string[] lines = File.ReadAllLines(xamlPath);
            for (int i = 0; i < lines.Length; i++)
            {
                if (lines[i].Contains("HeroActionButtonStyle", StringComparison.Ordinal))
                {
                    offenders.Add($"{relativePath}:{i + 1}: {lines[i].Trim()}");
                }
            }
        }

        Assert.That(
            offenders,
            Is.Empty,
            "HeroActionButtonStyle is tuned for the blue product header. Page/card primary actions should use card-safe button styling so they remain visible in the light shell.");
    }

    [Test]
    public void WinUiSemanticStatusBrushes_AreCentralized()
    {
        string brushHelper = Path.Combine(TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Helpers", "ThemeBrushes.cs");
        Assert.That(File.Exists(brushHelper), Is.True, "Expected centralized WinUI semantic brush helper.");

        string settingsPage = File.ReadAllText(Path.Combine(TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "SettingsPage.xaml.cs"));
        string patchItemModel = File.ReadAllText(Path.Combine(TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Models", "BinaryPatchItemModel.cs"));

        Assert.That(settingsPage, Does.Not.Contain("Colors.Orange"));
        Assert.That(settingsPage, Does.Not.Contain("Colors.OrangeRed"));
        Assert.That(settingsPage, Does.Not.Contain("Colors.LightGreen"));
        Assert.That(patchItemModel, Does.Not.Contain("ColorHelper.FromArgb"));
    }

    [Test]
    [Category("LegacyWpf")]
    [Explicit("Legacy WPF reference audit; not part of the default WinUI/AppCore gate.")]
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
    [Explicit("Legacy WPF reference audit; not part of the default WinUI/AppCore gate.")]
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
    [Explicit("Legacy WPF reference audit; not part of the default WinUI/AppCore gate.")]
    public void PrimaryButtonStyle_UsesMaterialDesignRaisedButton()
    {
        RequireLegacyWpfSurface();
        string xaml = File.ReadAllText(AppXamlPath);
        Assert.That(xaml, Does.Contain("x:Key=\"PrimaryButtonStyle\""));
        Assert.That(xaml, Does.Contain("MaterialDesignRaisedButton"));
    }

    [Test]
    [Category("LegacyWpf")]
    [Explicit("Legacy WPF reference audit; not part of the default WinUI/AppCore gate.")]
    public void MainWindow_DefinesAboutTab()
    {
        RequireLegacyWpfSurface();
        string xaml = File.ReadAllText(MainWindowXamlPath);
        Assert.That(xaml, Does.Contain("Header=\"About\""));
        Assert.That(xaml, Does.Contain("<views:AboutView/>"));
    }

    [Test]
    [Category("LegacyWpf")]
    [Explicit("Legacy WPF reference audit; not part of the default WinUI/AppCore gate.")]
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

    private static Dictionary<string, Dictionary<string, string>> LoadWinUiThemeBrushColors(string xamlPath)
    {
        Assert.That(File.Exists(xamlPath), Is.True, $"Missing WinUI App.xaml: {xamlPath}");

        XNamespace xNamespace = "http://schemas.microsoft.com/winfx/2006/xaml";
        XDocument document = XDocument.Load(xamlPath);
        var result = new Dictionary<string, Dictionary<string, string>>(StringComparer.Ordinal);

        foreach (XElement dictionary in document.Descendants().Where(e => e.Name.LocalName == "ResourceDictionary"))
        {
            string? dictionaryKey = dictionary.Attribute(xNamespace + "Key")?.Value;
            if (string.IsNullOrWhiteSpace(dictionaryKey) || dictionaryKey is not ("Default" or "Dark" or "Light"))
            {
                continue;
            }

            var colors = new Dictionary<string, string>(StringComparer.Ordinal);
            foreach (XElement brush in dictionary.Elements().Where(e => e.Name.LocalName == "SolidColorBrush"))
            {
                string? key = brush.Attribute(xNamespace + "Key")?.Value;
                string? color = brush.Attribute("Color")?.Value;
                if (!string.IsNullOrWhiteSpace(key) && !string.IsNullOrWhiteSpace(color))
                {
                    colors[key] = color;
                }
            }

            result[dictionaryKey] = colors;
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
