using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Creating a copy that already exists used to interpolate the full
/// targetRoot. Name the folder.
/// </summary>
public class PatchBenchCopyExistsHonestyTests
{
    [Test]
    public void AnExistingCopyNamesTheFolderNotAPath()
    {
        string sentence = GameProfilePreflightService.TargetCopyExists;

        Assert.That(sentence, Is.EqualTo("That copy folder already exists."));
        Assert.That(sentence, Does.Contain("copy folder"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(sentence, Does.Not.Contain(":\\"));
        Assert.That(sentence, Does.Not.Contain("/"));
    }

    [Test]
    public void ThePrepareServiceDropsTheTargetRootInterpolation()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfilePreflightService.cs"));

        Assert.That(source, Does.Contain("TargetCopyExists"));
        Assert.That(source, Does.Not.Contain("Target playable copied game folder already exists:"));
        Assert.That(source, Does.Not.Contain("{targetRoot}"));
    }
}
