using System;
using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Windowed &amp; Mods used to label the replacement music picker as an
/// OGG track. The TextBlock above PatchBenchMusicReplacementPath paints
/// that sentence. Name the music file.
/// </summary>
public class MusicReplacementTrackLabelHonestyTests
{
    private const string PaintedSentence = "Replacement music file";

    [Test]
    public void TheReplacementTrackLabelPaintsTheMusicFileNotAnOgg()
    {
        string label = ReadReplacementTrackLabel();

        Assert.That(label, Does.Contain($"Text=\"{PaintedSentence}\""));
        Assert.That(label.ToLowerInvariant(), Does.Contain("music file"));
        Assert.That(label.ToLowerInvariant(), Does.Not.Contain("ogg"));
        Assert.That(label.ToLowerInvariant(), Does.Not.Contain("sidecar"));
        Assert.That(label.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(label, Does.Not.Contain(@":\"));
    }

    [Test]
    public void TheReplacementTrackLabelIsTheXamlDefault()
    {
        string xaml = ReadWindowedAndModsXaml();
        string label = ReadReplacementTrackLabel();

        Assert.That(xaml, Does.Contain($"Text=\"{PaintedSentence}\""));
        Assert.That(label, Does.Contain($"Text=\"{PaintedSentence}\""));
        Assert.That(xaml, Does.Not.Contain("Text=\"Replacement track (.ogg)\""));
        Assert.That(xaml, Does.Contain("x:Name=\"PatchBenchMusicReplacementPath\""));
    }

    private static string ReadWindowedAndModsXaml()
    {
        return File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "BinaryPatchesPage.xaml"));
    }

    private static string ReadReplacementTrackLabel()
    {
        string xaml = ReadWindowedAndModsXaml();
        const string boxMark = "x:Name=\"PatchBenchMusicReplacementPath\"";
        int box = xaml.IndexOf(boxMark, StringComparison.Ordinal);
        Assert.That(box, Is.GreaterThanOrEqualTo(0), "PatchBenchMusicReplacementPath is missing.");

        const string startMark = "<TextBlock Text=\"";
        int start = xaml.LastIndexOf(startMark, box, StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0), "Replacement track label is missing.");

        int end = xaml.IndexOf("/>", start, StringComparison.Ordinal);
        Assert.That(end, Is.GreaterThan(start), "Replacement track label is unclosed.");
        Assert.That(end, Is.LessThan(box), "Replacement track label is not the TextBlock above the picker.");
        return xaml[start..(end + 2)];
    }
}
