using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Launching a missing copy used to interpolate the folder.
/// Name the folder. Reuse CopyFolderMissing.
/// </summary>
public class PatchBenchSourceFolderHonestyTests
{
    [Test]
    public void AMissingLaunchCopyRootUsesTheSharedCopyFolderSentence()
    {
        DirectoryNotFoundException error = Assert.Throws<DirectoryNotFoundException>(
            () => GameProfilePreflightService.BuildLaunchPlan(
                Path.Combine(Path.GetTempPath(), "onslaught-missing-copy-folder")));

        Assert.That(error.Message, Is.EqualTo(GameProfilePreflightService.CopyFolderMissing));
        Assert.That(error.Message, Is.EqualTo("That copy folder could not be found."));
        Assert.That(error.Message, Does.Contain("copy folder"));
        Assert.That(error.Message.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(error.Message, Does.Not.Contain(":\\"));
        Assert.That(error.Message, Does.Not.Contain("/"));
    }

    [Test]
    public void TheServiceDropsTheCopyRootInterpolations()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfilePreflightService.cs"));

        Assert.That(source, Does.Contain("CopyFolderMissing"));
        Assert.That(source, Does.Not.Contain("Playable copied game folder root does not exist:"));
    }
}
