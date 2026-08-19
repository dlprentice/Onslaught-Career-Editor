using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Save Rescue used to require an app-owned playable copied game folder root.
/// Name the folder, not a root.
/// </summary>
public class SaveRescueProfileFolderHonestyTests
{
    [Test]
    public void ABlankAppOwnedFolderNamesTheFolderNotARoot()
    {
        InvalidOperationException error = Assert.Throws<InvalidOperationException>(
            () => SafeCopySaveRescueService.Inventory("copy", " "));

        Assert.That(error.Message, Is.EqualTo(SafeCopySaveRescueService.ProfileFolderRequired));
        Assert.That(error.Message, Is.EqualTo("A profile folder is required."));
        Assert.That(error.Message, Does.Contain("profile folder"));
        Assert.That(error.Message, Does.Not.Contain("app-owned"));
        Assert.That(error.Message.ToLowerInvariant(), Does.Not.Contain("root"));
        Assert.That(error.Message.ToLowerInvariant(), Does.Not.Contain("path"));
    }

    [Test]
    public void TheRescueServiceDropsTheRootRequiredSentence()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "SafeCopySaveRescue.cs"));

        Assert.That(source, Does.Contain("ProfileFolderRequired"));
        Assert.That(source, Does.Not.Contain("An app-owned playable copied game folder root is required."));
    }
}
