using System;
using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Windowed &amp; Mods used to prompt for an existing copied data\Music
/// .ogg file. The PlaceholderText on PatchBenchMusicTargetFileName paints
/// that sentence. Name the music file.
/// </summary>
public class MusicReplacementTargetPlaceholderHonestyTests
{
    private const string PaintedSentence = "Existing copied music file";

    [Test]
    public void TheTargetFilePlaceholderPaintsTheMusicFileNotADataPath()
    {
        string placeholder = ReadTargetFilePlaceholder();

        Assert.That(placeholder, Is.EqualTo($"PlaceholderText=\"{PaintedSentence}\""));
        Assert.That(placeholder.ToLowerInvariant(), Does.Contain("music file"));
        Assert.That(placeholder, Does.Not.Contain("data\\Music"));
        Assert.That(placeholder, Does.Not.Contain("data/Music"));
        Assert.That(placeholder.ToLowerInvariant(), Does.Not.Contain("ogg"));
        Assert.That(placeholder.ToLowerInvariant(), Does.Not.Contain("sidecar"));
        Assert.That(placeholder.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(placeholder, Does.Not.Contain(@":\"));
    }

    [Test]
    public void TheTargetFilePlaceholderIsTheXamlDefault()
    {
        string xaml = ReadWindowedAndModsXaml();
        string placeholder = ReadTargetFilePlaceholder();

        Assert.That(placeholder, Is.EqualTo($"PlaceholderText=\"{PaintedSentence}\""));
        Assert.That(xaml, Does.Contain("x:Name=\"PatchBenchMusicTargetFileName\""));
        Assert.That(ReadTargetFileBox(), Does.Not.Contain("PlaceholderText=\"Existing copied data\\Music file, for example BEA_01(Master).ogg\""));
    }

    private static string ReadWindowedAndModsXaml()
    {
        return File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "BinaryPatchesPage.xaml"));
    }

    private static string ReadTargetFileBox()
    {
        string xaml = ReadWindowedAndModsXaml();
        const string boxMark = "x:Name=\"PatchBenchMusicTargetFileName\"";
        int start = xaml.IndexOf(boxMark, StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0), "PatchBenchMusicTargetFileName is missing.");

        int end = xaml.IndexOf("/>", start, StringComparison.Ordinal);
        Assert.That(end, Is.GreaterThan(start), "Target file box is unclosed.");
        return xaml[start..(end + 2)];
    }

    private static string ReadTargetFilePlaceholder()
    {
        string box = ReadTargetFileBox();
        const string mark = "PlaceholderText=\"";
        int start = box.IndexOf(mark, StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0), "PlaceholderText is missing.");

        int valueStart = start + mark.Length;
        int end = box.IndexOf('"', valueStart);
        Assert.That(end, Is.GreaterThan(valueStart), "PlaceholderText is unclosed.");
        return box[start..(end + 1)];
    }
}
