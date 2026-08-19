using System;
using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Windowed &amp; Mods used to name the replacement music picker an
/// OGG file for assistive technology. The AutomationProperties.Name on
/// PatchBenchMusicReplacementPath paints that sentence. Name the music
/// file.
/// </summary>
public class MusicReplacementAccessibilityNameHonestyTests
{
    private const string PaintedSentence = "Replacement music file";

    [Test]
    public void TheReplacementPathAccessibilityNamePaintsTheMusicFileNotAnOgg()
    {
        string name = ReadReplacementPathAccessibilityName();

        Assert.That(name, Is.EqualTo($"AutomationProperties.Name=\"{PaintedSentence}\""));
        Assert.That(name.ToLowerInvariant(), Does.Contain("music file"));
        Assert.That(name.ToLowerInvariant(), Does.Not.Contain("ogg"));
        Assert.That(name.ToLowerInvariant(), Does.Not.Contain("sidecar"));
        Assert.That(name.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(name, Does.Not.Contain(@":\"));
    }

    [Test]
    public void TheReplacementPathAccessibilityNameIsTheXamlDefault()
    {
        string xaml = ReadWindowedAndModsXaml();
        string name = ReadReplacementPathAccessibilityName();

        Assert.That(name, Is.EqualTo($"AutomationProperties.Name=\"{PaintedSentence}\""));
        Assert.That(xaml, Does.Contain("x:Name=\"PatchBenchMusicReplacementPath\""));
        Assert.That(ReadReplacementPathBox(), Does.Not.Contain("AutomationProperties.Name=\"Replacement track OGG file\""));
    }

    private static string ReadWindowedAndModsXaml()
    {
        return File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "BinaryPatchesPage.xaml"));
    }

    private static string ReadReplacementPathBox()
    {
        string xaml = ReadWindowedAndModsXaml();
        const string boxMark = "x:Name=\"PatchBenchMusicReplacementPath\"";
        int start = xaml.IndexOf(boxMark, StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0), "PatchBenchMusicReplacementPath is missing.");

        int end = xaml.IndexOf("/>", start, StringComparison.Ordinal);
        Assert.That(end, Is.GreaterThan(start), "Replacement path box is unclosed.");
        return xaml[start..(end + 2)];
    }

    private static string ReadReplacementPathAccessibilityName()
    {
        string box = ReadReplacementPathBox();
        const string mark = "AutomationProperties.Name=\"";
        int start = box.IndexOf(mark, StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0), "AutomationProperties.Name is missing.");

        int valueStart = start + mark.Length;
        int end = box.IndexOf('"', valueStart);
        Assert.That(end, Is.GreaterThan(valueStart), "AutomationProperties.Name is unclosed.");
        return box[start..(end + 1)];
    }
}
