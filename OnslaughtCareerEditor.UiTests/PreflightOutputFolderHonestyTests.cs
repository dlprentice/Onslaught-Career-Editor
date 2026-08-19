using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Preparing a copy used to refuse an output root. Name the folder, not a root.
/// </summary>
public class PreflightOutputFolderHonestyTests
{
    [Test]
    public void PrepareRefusalsNameTheFolderNotARoot()
    {
        Assert.That(GameProfilePreflightService.ProfileFolderInsideGame,
            Is.EqualTo("The app-owned profile folder must not sit inside the game folder."));
        Assert.That(GameProfilePreflightService.GameFolderInsideProfile,
            Is.EqualTo("The game folder must not sit inside the app-owned profile folder."));
        Assert.That(GameProfilePreflightService.ProfileFolderUnderProtectedInstall,
            Is.EqualTo("The app-owned profile folder must not sit under Program Files or another protected install folder."));
        Assert.That(GameProfilePreflightService.ProfileFolderUnderSteamInstall,
            Is.EqualTo("The app-owned profile folder must not sit under a steamapps/common/Battle Engine Aquila install folder."));

        foreach (string sentence in new[]
        {
            GameProfilePreflightService.ProfileFolderInsideGame,
            GameProfilePreflightService.GameFolderInsideProfile,
            GameProfilePreflightService.ProfileFolderUnderProtectedInstall,
            GameProfilePreflightService.ProfileFolderUnderSteamInstall,
        })
        {
            Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("root"));
            Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("path"));
            Assert.That(sentence, Does.Not.Contain(":\\"));
        }
    }

    [Test]
    public void ThePreflightServiceDropsTheOutputRootSentences()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfilePreflightService.cs"));

        Assert.That(source, Does.Contain("ProfileFolderInsideGame"));
        Assert.That(source, Does.Contain("GameFolderInsideProfile"));
        Assert.That(source, Does.Contain("ProfileFolderUnderProtectedInstall"));
        Assert.That(source, Does.Contain("ProfileFolderUnderSteamInstall"));
        Assert.That(source, Does.Not.Contain("The app-owned output root must not be inside the source game root."));
        Assert.That(source, Does.Not.Contain("The source game root must not be inside the app-owned output root."));
        Assert.That(source, Does.Not.Contain("The app-owned output root must not be under Program Files or another protected install root."));
        Assert.That(source, Does.Not.Contain("The app-owned output root must not be under a steamapps/common/Battle Engine Aquila install root."));
    }
}
