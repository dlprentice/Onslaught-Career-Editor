using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Staging music used to interpolate the missing copy folder. Name the folder.
/// </summary>
public class PatchBenchMusicCopyFolderHonestyTests
{
    [Test]
    public void AMissingCopyFolderNamesTheFolderNotAPath()
    {
        string sentence = GameProfileMusicReplacementService.CopyFolderMissing;

        Assert.That(sentence, Is.EqualTo("That copy folder could not be found."));
        Assert.That(sentence, Does.Contain("copy folder"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(sentence, Does.Not.Contain(":\\"));
        Assert.That(sentence, Does.Not.Contain("/"));
    }

    [Test]
    public void AMissingProfileFolderNamesTheFolderNotARoot()
    {
        string sentence = GameProfileMusicReplacementService.ProfileFolderMissing;

        Assert.That(sentence, Is.EqualTo("That app-owned profile folder could not be found."));
        Assert.That(sentence, Does.Contain("profile folder"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("root"));
        Assert.That(sentence, Does.Not.Contain(":\\"));
        Assert.That(sentence, Does.Not.Contain("/"));
    }

    [Test]
    public void TheServiceDropsTheSafeGameRootInterpolation()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfileMusicReplacementService.cs"));

        Assert.That(source, Does.Contain("CopyFolderMissing"));
        Assert.That(source, Does.Contain("ProfileFolderMissing"));
        Assert.That(source, Does.Not.Contain("Playable copied game folder root does not exist:"));
        Assert.That(source, Does.Not.Contain("App-owned profiles root does not exist:"));
    }
}
