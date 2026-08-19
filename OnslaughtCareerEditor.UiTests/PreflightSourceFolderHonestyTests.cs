using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Preparing a safe copy used to interpolate the missing install folder
/// (<c>Source game root does not exist: {SourceGameRoot}</c>).
/// Name the folder, not a path.
/// </summary>
public class PreflightSourceFolderHonestyTests
{
    [Test]
    public void AMissingInstallFolderNamesTheFolderNotAPath()
    {
        string missing = Path.Combine(Path.GetTempPath(), $"gone-install-{Guid.NewGuid():N}");
        DirectoryNotFoundException ex = Assert.Throws<DirectoryNotFoundException>(
            () => GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                new GameProfilePrepareOptions(
                    SourceGameRoot: missing,
                    OutputRoot: Path.Combine(Path.GetTempPath(), "profiles"),
                    ProfileName: "unused")));

        Assert.That(ex.Message, Is.EqualTo("That game folder could not be found."));
        Assert.That(ex.Message, Does.Contain("game folder"));
        Assert.That(ex.Message.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(ex.Message, Does.Not.Contain(missing));
        Assert.That(ex.Message, Does.Not.Contain(":\\"));
        Assert.That(ex.Message, Does.Not.Contain("does not exist"));
    }

    [Test]
    public void TheSourceDoesNotKeepTheOldPathSentence()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfilePreflightService.cs"));

        Assert.That(source, Does.Contain("That game folder could not be found."));
        Assert.That(source, Does.Not.Contain("Source game root does not exist:"));
        Assert.That(source, Does.Not.Contain("{options.SourceGameRoot}"));
    }
}
