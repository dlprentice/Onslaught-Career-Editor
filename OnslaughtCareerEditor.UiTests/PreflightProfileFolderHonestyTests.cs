using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Preparing, copying, and deleting still required an app-owned workspace,
/// output, or playable-copy root. Name the folder, not a root. Reuse the
/// same blank app-owned-folder sentence as launch/stop.
/// </summary>
public class PreflightProfileFolderHonestyTests
{
    [Test]
    public void ABlankWorkspaceFolderNamesTheFolderNotARoot()
    {
        InvalidOperationException error = Assert.Throws<InvalidOperationException>(
            () => GameProfilePreflightService.ValidateAppOwnedWorkspaceFileDestination(
                "BEA.exe",
                " ",
                "BEA.exe"));

        Assert.That(error.Message, Is.EqualTo(GameProfilePreflightService.ProfileFolderRequired));
        Assert.That(error.Message, Is.EqualTo("An app-owned profile folder is required."));
        Assert.That(error.Message, Does.Contain("profile folder"));
        Assert.That(error.Message.ToLowerInvariant(), Does.Not.Contain("root"));
        Assert.That(error.Message.ToLowerInvariant(), Does.Not.Contain("path"));
    }

    [Test]
    public void ABlankOutputFolderNamesTheFolderNotARoot()
    {
        string sourceFolder = Path.Combine(Path.GetTempPath(), $"preflight-src-{Guid.NewGuid():N}");
        Directory.CreateDirectory(sourceFolder);
        try
        {
            InvalidOperationException error = Assert.Throws<InvalidOperationException>(
                () => GameProfilePreflightService.PrepareWindowedCompatibilityProfile(
                    new GameProfilePrepareOptions(
                        SourceGameRoot: sourceFolder,
                        OutputRoot: " ",
                        ProfileName: "copy")));

            Assert.That(error.Message, Is.EqualTo(GameProfilePreflightService.ProfileFolderRequired));
            Assert.That(error.Message, Is.EqualTo("An app-owned profile folder is required."));
            Assert.That(error.Message, Does.Contain("profile folder"));
            Assert.That(error.Message.ToLowerInvariant(), Does.Not.Contain("root"));
            Assert.That(error.Message.ToLowerInvariant(), Does.Not.Contain("path"));
        }
        finally
        {
            Directory.Delete(sourceFolder, recursive: true);
        }
    }

    [Test]
    public void ABlankProfileFolderOnDeleteNamesTheFolderNotARoot()
    {
        InvalidOperationException error = Assert.Throws<InvalidOperationException>(
            () => GameProfilePreflightService.DeleteGeneratedProfile("copy", " "));

        Assert.That(error.Message, Is.EqualTo(GameProfilePreflightService.ProfileFolderRequired));
        Assert.That(error.Message, Is.EqualTo("An app-owned profile folder is required."));
        Assert.That(error.Message, Does.Contain("profile folder"));
        Assert.That(error.Message.ToLowerInvariant(), Does.Not.Contain("root"));
        Assert.That(error.Message.ToLowerInvariant(), Does.Not.Contain("path"));
    }

    [Test]
    public void ThePreflightServiceDropsTheRootRequiredSentences()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfilePreflightService.cs"));

        Assert.That(source, Does.Contain("ProfileFolderRequired"));
        Assert.That(source, Does.Not.Contain("An app-owned workspace root is required."));
        Assert.That(source, Does.Not.Contain("An app-owned output root is required."));
        Assert.That(source, Does.Not.Contain("An app-owned playable copied game folder root is required."));
    }
}
