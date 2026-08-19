using System;
using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Windowed &amp; Mods used to name audible-proof limits a CDB decode.
/// PatchBenchMusicAudibleProofContractStatus paints that sentence.
/// Name the copied game selecting the music file.
/// </summary>
public class MusicReplacementAudibleProofHonestyTests
{
    private const string PaintedSentence =
        "A music swap modifies safe-copy files only. Audible proof still requires a bounded audio-output capture. Staging and the copied game selecting the music file are not audible playback proof.";

    [Test]
    public void TheAudibleProofStatusPaintsTheCopiedMusicFileNotACdbDecode()
    {
        string status = ReadAudibleProofStatus();

        Assert.That(status, Does.Contain($"Text=\"{PaintedSentence}\""));
        Assert.That(status.ToLowerInvariant(), Does.Contain("music file"));
        Assert.That(status.ToLowerInvariant(), Does.Contain("copied game"));
        Assert.That(status, Does.Not.Contain("CDB"));
        Assert.That(status, Does.Not.Contain("cdb"));
        Assert.That(status.ToLowerInvariant(), Does.Not.Contain("decode"));
        Assert.That(status.ToLowerInvariant(), Does.Not.Contain("ogg"));
        Assert.That(status.ToLowerInvariant(), Does.Not.Contain("sidecar"));
        Assert.That(status.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(status, Does.Not.Contain(@"data\Music"));
        Assert.That(status, Does.Not.Contain("data/Music"));
        Assert.That(status, Does.Not.Contain(@":\"));
    }

    [Test]
    public void TheAudibleProofStatusIsTheXamlDefault()
    {
        string xaml = ReadWindowedAndModsXaml();
        string status = ReadAudibleProofStatus();

        Assert.That(status, Does.Contain($"Text=\"{PaintedSentence}\""));
        Assert.That(xaml, Does.Contain($"Text=\"{PaintedSentence}\""));
        Assert.That(xaml, Does.Contain("x:Name=\"PatchBenchMusicAudibleProofContractStatus\""));
        Assert.That(xaml, Does.Not.Contain("Staging and CDB decode are not audible playback proof."));
    }

    private static string ReadWindowedAndModsXaml()
    {
        return File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "BinaryPatchesPage.xaml"));
    }

    private static string ReadAudibleProofStatus()
    {
        string xaml = ReadWindowedAndModsXaml();
        const string nameMark = "x:Name=\"PatchBenchMusicAudibleProofContractStatus\"";
        int name = xaml.IndexOf(nameMark, StringComparison.Ordinal);
        Assert.That(name, Is.GreaterThanOrEqualTo(0), "PatchBenchMusicAudibleProofContractStatus is missing.");

        const string startMark = "<TextBlock ";
        int start = xaml.LastIndexOf(startMark, name, StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0), "Audible-proof status TextBlock is missing.");

        int end = xaml.IndexOf("/>", start, StringComparison.Ordinal);
        Assert.That(end, Is.GreaterThan(start), "Audible-proof status is unclosed.");
        return xaml[start..(end + 2)];
    }
}
