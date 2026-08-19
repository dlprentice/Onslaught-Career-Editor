using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Launch/stop used to require an app-owned playable copied game folder root.
/// Name the folder, not a root.
/// </summary>
public class PatchBenchProfileFolderHonestyTests
{
    [Test]
    public void ABlankAppOwnedFolderNamesTheFolderNotARoot()
    {
        InvalidOperationException error = Assert.Throws<InvalidOperationException>(
            () => GameProfileRuntimeService.LaunchCopiedProfile(
                new GameProfileLaunchOptions(
                    ProfileRoot: "copy",
                    AppOwnedProfilesRoot: " ")));

        Assert.That(error.Message, Is.EqualTo(GameProfileRuntimeService.ProfileFolderRequired));
        Assert.That(error.Message, Is.EqualTo("An app-owned profile folder is required."));
        Assert.That(error.Message, Does.Contain("profile folder"));
        Assert.That(error.Message.ToLowerInvariant(), Does.Not.Contain("root"));
        Assert.That(error.Message.ToLowerInvariant(), Does.Not.Contain("path"));
    }

    [Test]
    public void TheRuntimeServiceDropsTheRootRequiredSentence()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfileRuntimeService.cs"));

        Assert.That(source, Does.Contain("ProfileFolderRequired"));
        Assert.That(source, Does.Not.Contain("An app-owned playable copied game folder root is required."));
    }
}
