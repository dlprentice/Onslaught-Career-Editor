using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Deleting a missing copy used to interpolate the folder. Name the folder.
/// </summary>
public class PatchBenchDeleteCopyFolderHonestyTests
{
    [Test]
    public void AMissingCopyFolderNamesTheFolderNotAPath()
    {
        string sentence = GameProfilePreflightService.CopyFolderMissing;

        Assert.That(sentence, Is.EqualTo("That copy folder could not be found."));
        Assert.That(sentence, Does.Contain("copy folder"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(sentence, Does.Not.Contain(":\\"));
        Assert.That(sentence, Does.Not.Contain("/"));
    }

    [Test]
    public void TheDeleteServiceDropsTheProfileRootInterpolation()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfilePreflightService.cs"));

        Assert.That(source, Does.Contain("CopyFolderMissing"));
        Assert.That(source, Does.Not.Contain("Playable copied game folder does not exist:"));
    }
}
