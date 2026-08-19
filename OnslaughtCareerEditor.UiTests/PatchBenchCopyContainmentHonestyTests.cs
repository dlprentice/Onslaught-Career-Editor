using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Launch/stop used to require a copy under the app-owned playable
/// copied game folder root. Name the folder, not a root.
/// </summary>
public class PatchBenchCopyContainmentHonestyTests
{
    [Test]
    public void ACopyOutsideTheFolderNamesTheFolderNotARoot()
    {
        string appFolder = Path.Combine(Path.GetTempPath(), $"bea-app-{Guid.NewGuid():N}");
        string copyFolder = Path.Combine(Path.GetTempPath(), $"bea-copy-{Guid.NewGuid():N}");
        Directory.CreateDirectory(appFolder);
        Directory.CreateDirectory(copyFolder);
        try
        {
            InvalidOperationException error = Assert.Throws<InvalidOperationException>(
                () => GameProfileRuntimeService.LaunchCopiedProfile(
                    new GameProfileLaunchOptions(
                        ProfileRoot: copyFolder,
                        AppOwnedProfilesRoot: appFolder)));

            Assert.That(error.Message, Is.EqualTo(GameProfileRuntimeService.CopyMustStayInside));
            Assert.That(error.Message, Is.EqualTo("Launch/stop requires a managed copy inside the app-owned profile folder."));
            Assert.That(error.Message, Does.Contain("profile folder"));
            Assert.That(error.Message.ToLowerInvariant(), Does.Not.Contain("root"));
            Assert.That(error.Message.ToLowerInvariant(), Does.Not.Contain("path"));
            Assert.That(error.Message, Does.Not.Contain("playable copied"));
            Assert.That(error.Message, Does.Not.Contain(appFolder));
            Assert.That(error.Message, Does.Not.Contain(copyFolder));
            Assert.That(error.Message, Does.Not.Contain(":\\"));
        }
        finally
        {
            Directory.Delete(appFolder, recursive: true);
            Directory.Delete(copyFolder, recursive: true);
        }
    }

    [Test]
    public void TheRuntimeServiceDropsTheRootContainmentSentence()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfileRuntimeService.cs"));

        Assert.That(source, Does.Contain("CopyMustStayInside"));
        Assert.That(source, Does.Not.Contain(
            "Launch/stop requires a managed playable copied game folder generated under the app-owned playable copied game folder root."));
    }
}
