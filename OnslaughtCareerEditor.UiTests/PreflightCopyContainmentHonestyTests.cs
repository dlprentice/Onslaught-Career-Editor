using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Delete used to refuse a copy outside the app-owned playable copied
/// game folder root. Name the folder, not a root. Reuse the Save Rescue
/// stay-inside sentence.
/// </summary>
public class PreflightCopyContainmentHonestyTests
{
    [Test]
    public void ADeleteOutsideTheFolderNamesTheFolderNotARoot()
    {
        string appFolder = Path.Combine(Path.GetTempPath(), $"bea-del-app-{Guid.NewGuid():N}");
        string copyFolder = Path.Combine(Path.GetTempPath(), $"bea-del-copy-{Guid.NewGuid():N}");
        Directory.CreateDirectory(appFolder);
        Directory.CreateDirectory(copyFolder);
        try
        {
            InvalidOperationException error = Assert.Throws<InvalidOperationException>(
                () => GameProfilePreflightService.DeleteGeneratedProfile(copyFolder, appFolder));

            Assert.That(error.Message, Is.EqualTo(GameProfilePreflightService.CopyMustStayInside));
            Assert.That(error.Message, Is.EqualTo(SafeCopySaveRescueService.CopyMustStayInside));
            Assert.That(error.Message, Is.EqualTo("That copy must stay inside the app-owned profile folder."));
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
    public void ThePreflightServiceDropsTheRootDeleteSentence()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfilePreflightService.cs"));

        Assert.That(source, Does.Contain("CopyMustStayInside"));
        Assert.That(source, Does.Not.Contain(
            "Refusing to delete a playable copied game folder outside the app-owned playable copied game folder root."));
    }
}
