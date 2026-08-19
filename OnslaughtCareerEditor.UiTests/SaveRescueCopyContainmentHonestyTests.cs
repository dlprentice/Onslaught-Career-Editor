using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Save Rescue used to refuse a copy outside the app-owned playable
/// copied game folder root. Name the folder, not a root.
/// </summary>
public class SaveRescueCopyContainmentHonestyTests
{
    [Test]
    public void ACopyOutsideTheFolderNamesTheFolderNotARoot()
    {
        string appFolder = Path.Combine(Path.GetTempPath(), $"bea-rescue-app-{Guid.NewGuid():N}");
        string copyFolder = Path.Combine(Path.GetTempPath(), $"bea-rescue-copy-{Guid.NewGuid():N}");
        Directory.CreateDirectory(appFolder);
        Directory.CreateDirectory(copyFolder);
        try
        {
            InvalidOperationException error = Assert.Throws<InvalidOperationException>(
                () => SafeCopySaveRescueService.Inventory(copyFolder, appFolder));

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
    public void TheRescueServiceDropsTheRootContainmentSentence()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "SafeCopySaveRescue.cs"));

        Assert.That(source, Does.Contain("CopyMustStayInside"));
        Assert.That(source, Does.Not.Contain(
            "Refusing to read a playable copied game folder outside the app-owned playable copied game folder root."));
    }
}
