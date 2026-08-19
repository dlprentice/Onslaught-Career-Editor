using System;
using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Windowed &amp; Mods used to name the replacement help a data\Music
/// folder. The TextBlock immediately after PatchBenchMusicReplacementPath
/// paints that sentence. Name the Music folder.
/// </summary>
public class MusicReplacementFolderHelpHonestyTests
{
    private const string PaintedSentence =
        "Target must be an existing file in the safe copy's Music folder. Stop the safe copy before staging or restoring.";

    [Test]
    public void TheReplacementHelpPaintsTheMusicFolderNotADataPath()
    {
        string help = ReadReplacementFolderHelp();

        Assert.That(help, Does.Contain($"Text=\"{PaintedSentence}\""));
        Assert.That(help, Does.Contain("Music folder"));
        Assert.That(help, Does.Not.Contain("data\\Music"));
        Assert.That(help, Does.Not.Contain("data/Music"));
        Assert.That(help, Does.Not.Contain("data"));
        Assert.That(help.ToLowerInvariant(), Does.Not.Contain("ogg"));
        Assert.That(help.ToLowerInvariant(), Does.Not.Contain("sidecar"));
        Assert.That(help.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(help, Does.Not.Contain(@":\"));
    }

    [Test]
    public void TheReplacementHelpIsTheXamlDefault()
    {
        string xaml = ReadWindowedAndModsXaml();
        string help = ReadReplacementFolderHelp();

        Assert.That(help, Does.Contain($"Text=\"{PaintedSentence}\""));
        Assert.That(xaml, Does.Contain($"Text=\"{PaintedSentence}\""));
        Assert.That(xaml, Does.Not.Contain("safe copy's data\\Music folder"));
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

    private static string ReadReplacementFolderHelp()
    {
        string xaml = ReadWindowedAndModsXaml();
        const string boxMark = "x:Name=\"PatchBenchMusicReplacementPath\"";
        int box = xaml.IndexOf(boxMark, StringComparison.Ordinal);
        Assert.That(box, Is.GreaterThanOrEqualTo(0), "PatchBenchMusicReplacementPath is missing.");

        int boxEnd = xaml.IndexOf("/>", box, StringComparison.Ordinal);
        Assert.That(boxEnd, Is.GreaterThan(box), "Replacement path box is unclosed.");

        const string startMark = "<TextBlock Text=\"";
        int start = xaml.IndexOf(startMark, boxEnd, StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThan(boxEnd), "Replacement folder help is missing.");

        int end = xaml.IndexOf("/>", start, StringComparison.Ordinal);
        Assert.That(end, Is.GreaterThan(start), "Replacement folder help is unclosed.");
        return xaml[start..(end + 2)];
    }
}
