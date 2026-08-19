using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// A missing Music folder used to name data\Music. Name the folder.
/// </summary>
public class PatchBenchMusicFolderHonestyTests
{
    [Test]
    public void AMissingMusicFolderNamesTheFolderNotAPath()
    {
        string sentence = GameProfileMusicReplacementService.MusicFolderMissing;

        Assert.That(sentence, Is.EqualTo("That copy does not have a Music folder."));
        Assert.That(sentence, Does.Contain("Music folder"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(sentence, Does.Not.Contain("data"));
        Assert.That(sentence, Does.Not.Contain("\\"));
        Assert.That(sentence, Does.Not.Contain("/"));
        Assert.That(sentence, Does.Not.Contain(":\\"));
    }

    [Test]
    public void TheServiceDropsTheRelativeMusicPath()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfileMusicReplacementService.cs"));

        Assert.That(source, Does.Contain("MusicFolderMissing"));
        Assert.That(source, Does.Not.Contain("does not contain data\\\\Music."));
        Assert.That(source, Does.Not.Contain("does not contain data\\Music."));
    }
}
