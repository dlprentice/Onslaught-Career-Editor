using System;
using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Windowed &amp; Mods used to prompt for a replacement .ogg file.
/// The PlaceholderText on PatchBenchMusicReplacementPath paints that
/// sentence. Name the music file.
/// </summary>
public class MusicReplacementPlaceholderHonestyTests
{
    private const string PaintedSentence = "Replacement music file";

    [Test]
    public void TheReplacementPathPlaceholderPaintsTheMusicFileNotAnOgg()
    {
        string placeholder = ReadReplacementPathPlaceholder();

        Assert.That(placeholder, Is.EqualTo($"PlaceholderText=\"{PaintedSentence}\""));
        Assert.That(placeholder.ToLowerInvariant(), Does.Contain("music file"));
        Assert.That(placeholder.ToLowerInvariant(), Does.Not.Contain("ogg"));
        Assert.That(placeholder.ToLowerInvariant(), Does.Not.Contain("sidecar"));
        Assert.That(placeholder.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(placeholder, Does.Not.Contain(@":\"));
    }

    [Test]
    public void TheReplacementPathPlaceholderIsTheXamlDefault()
    {
        string xaml = ReadWindowedAndModsXaml();
        string placeholder = ReadReplacementPathPlaceholder();

        Assert.That(placeholder, Is.EqualTo($"PlaceholderText=\"{PaintedSentence}\""));
        Assert.That(xaml, Does.Contain("x:Name=\"PatchBenchMusicReplacementPath\""));
        Assert.That(ReadReplacementPathBox(), Does.Not.Contain("PlaceholderText=\"Replacement .ogg file\""));
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

    private static string ReadReplacementPathPlaceholder()
    {
        string box = ReadReplacementPathBox();
        const string mark = "PlaceholderText=\"";
        int start = box.IndexOf(mark, StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0), "PlaceholderText is missing.");

        int valueStart = start + mark.Length;
        int end = box.IndexOf('"', valueStart);
        Assert.That(end, Is.GreaterThan(valueStart), "PlaceholderText is unclosed.");
        return box[start..(end + 1)];
    }
}
